"""`harness-inspect` admin CLI — read-only state-ledger summary (U-RT-47).

Per `Spec_Harness_Runtime_v1.md` v1.1 §13 C-RT-13:

> `harness-inspect` (read-only). Opens state ledger (`.harness/state.jsonl`)
> and collector sqlite (path resolved via PATH_CLASS_REGISTRY per C-IS-01
> §1) in read-only mode. No writes. Dumps a summary: ledger head hash +
> last N entries (N from CLI flag, default 10); last N spans from collector
> (default 10); current cost-attribution rollup if available. Runs against
> a stopped harness; does not modify any state. Exits 0 on success;
> nonzero on file-not-found or read-error.

**AC mapping per session-3 atomic decomposition** (U-RT-47 acceptance:
"runs against a stopped harness; returns ledger head and last N spans"):

- runs against stopped harness — LAND (filesystem read, no process)
- returns ledger head — LAND (last entry `response_hash.hex()`)
- returns last N spans — **STRUCK**; extends
  `[[fork-trace-storage-pathclass-gap]]` (collector sqlite is in-memory-only
  per U-RT-30 PARTIAL-LAND); output names the gap explicitly

**Read-only invariant** (C-RT-13 invariant #1): this module MUST NOT
write to any file. The read path uses `Path.read_text()` + direct
`JsonlLedgerHandle` construction (no bootstrap-time side effects from
`initialize_jsonl_event_ledger`). Tested via chmod-readonly fixture.

**Framework discipline** (spec §13 deferred-to-discretion): argparse
stdlib only. No click / typer per workspace-root CLAUDE.md §3.2
framework-pull discipline.

**Cost-attribution rollup** (spec §13): "if available" — at HEAD the cost
chain is stateless-by-design per U-RT-31 (
`.harness/class_3_drift_u_rt_45_cost_chain_stateless.md`). Reported as
N/A in the summary.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from harness_core import DeploymentSurface, PersonaTier
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import StateLedgerEntry
from harness_is.state_ledger_write import read_ledger
from harness_od.observability_matrix import CellID
from harness_od.operator_burden_eval_primitives import OperatorBurdenEvalPrimitive

__all__ = ["build_parser", "main"]


# ---------------------------------------------------------------------------
# Defaults.
# ---------------------------------------------------------------------------


_DEFAULT_LEDGER_PATH = Path(".harness/state.jsonl")
_DEFAULT_LAST_N = 10
_EXIT_OK = 0
_EXIT_INSPECT_PATH = 2  # RT-FAIL-INSPECT-PATH per C-RT-13


_SPANS_UNAVAILABLE_REASON = (
    "in-memory collector storage at HEAD; on-disk sqlite path resolution "
    "STRUCK per [[fork-trace-storage-pathclass-gap]] (U-RT-30 PARTIAL-LAND)"
)

_COST_UNAVAILABLE_REASON = (
    "cost-attribution chain is stateless-by-design per U-RT-31; spec §10 "
    "step 2 over-specification documented at "
    "class_3_drift_u_rt_45_cost_chain_stateless.md"
)


# ---------------------------------------------------------------------------
# argparse.
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser. Factored for unit-testability."""
    parser = argparse.ArgumentParser(
        prog="harness-inspect",
        description=(
            "Read-only state-ledger inspector (Track A admin stub per "
            "Spec_Harness_Runtime_v1.md §13 C-RT-13)."
        ),
    )
    parser.add_argument(
        "--ledger-path",
        type=Path,
        default=_DEFAULT_LEDGER_PATH,
        help=f"Path to the state ledger JSONL (default: {_DEFAULT_LEDGER_PATH}).",
    )
    parser.add_argument(
        "--collector-path",
        type=Path,
        default=None,
        help=(
            "Path to the collector sqlite span store (C-OD-19 §19.2). Required "
            "with --browse. Unused otherwise — the ledger summary's span rollup "
            "remains N/A regardless (production span ingestion into this store "
            "is a separate, pre-existing deferral; see "
            "b-od19-slice-c-otelcol-manifest-reconciliation.md)."
        ),
    )
    parser.add_argument(
        "--browse",
        action="store_true",
        help=(
            "Launch the TUI trace browser (C-OD-19 §19.3) over --collector-path "
            "instead of the ledger summary."
        ),
    )
    parser.add_argument(
        "--last-n",
        type=int,
        default=_DEFAULT_LAST_N,
        help=f"Number of recent entries to dump (default: {_DEFAULT_LAST_N}).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output. Default is human-readable.",
    )
    _add_holdout_arguments(parser)
    return parser


# ---------------------------------------------------------------------------
# Holdout-loop tooling (B-OD17-EVAL-LOOP-TOOLING; C-OD-17 §17.3).
# ---------------------------------------------------------------------------


_DEFAULT_CELL_ID = "solo-developer:local-development"
_DEFAULT_STUB_DIR = Path("holdout_stubs")


def _add_holdout_arguments(parser: argparse.ArgumentParser) -> None:
    """Register the three holdout-loop actions (mutually exclusive with each
    other and with `--browse`/the ledger-summary default; `main` dispatches
    on whichever fires first)."""
    parser.add_argument(
        "--holdout-sample",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Draw a deterministic sample of N traces from --collector-path "
            "into a new holdout file at --holdout-path (C-OD-17 §17.3 "
            "holdout-set construction). Requires --primitive; --seed and "
            f"--cell-id have defaults ({_DEFAULT_CELL_ID})."
        ),
    )
    parser.add_argument(
        "--holdout-review",
        action="store_true",
        help=(
            "Interactively review the holdout set at --holdout-path against "
            "--review-ledger-path: for each not-yet-reviewed trace, print its "
            "id and span count and prompt for an operator-typed category. "
            "Makes NO model calls and computes no judge ratio."
        ),
    )
    parser.add_argument(
        "--holdout-scaffold",
        action="store_true",
        help=(
            "Scaffold an operator-authored assertion stub (one .py file per "
            "reviewed trace lacking one) under --stub-dir from "
            "--review-ledger-path. Never overwrites an existing stub."
        ),
    )
    parser.add_argument(
        "--holdout-path",
        type=Path,
        default=None,
        help=(
            "Path to the holdout-set JSON file "
            "(write target for --holdout-sample, read source for --holdout-review)."
        ),
    )
    parser.add_argument(
        "--review-ledger-path",
        type=Path,
        default=None,
        help=(
            "Path to the append-only review ledger JSONL "
            "(used by --holdout-review and --holdout-scaffold)."
        ),
    )
    parser.add_argument(
        "--stub-dir",
        type=Path,
        default=_DEFAULT_STUB_DIR,
        help=f"Directory for scaffolded assertion stubs (default: {_DEFAULT_STUB_DIR}).",
    )
    parser.add_argument(
        "--primitive",
        choices=[
            OperatorBurdenEvalPrimitive.SANDBOX_TIER_ROUTING_ACCURACY.value,
            OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT.value,
        ],
        default=None,
        help=(
            "The holdout-evaluable primitive (C-OD-17 §17.1) "
            "--holdout-sample draws a holdout set for."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Deterministic sampling seed for --holdout-sample (default: 0).",
    )
    parser.add_argument(
        "--cell-id",
        default=_DEFAULT_CELL_ID,
        help=(
            f"'persona-tier:deployment-surface' (default: {_DEFAULT_CELL_ID}). "
            "Values per harness_core.PersonaTier / DeploymentSurface, hyphenated lowercase."
        ),
    )


def _parse_cell_id(raw: str) -> CellID:
    """Parse `'solo-developer:local-development'` into a `CellID`.

    Enum values are the StrEnum's own hyphenated-lowercase form (e.g.
    `PersonaTier.SOLO_DEVELOPER.value == "solo-developer"`) — the CLI
    surface accepts exactly that form, not the Python member name.
    """
    persona_raw, _, surface_raw = raw.partition(":")
    return CellID(
        persona_tier=PersonaTier(persona_raw),
        deployment_surface=DeploymentSurface(surface_raw),
    )


# ---------------------------------------------------------------------------
# Read path.
# ---------------------------------------------------------------------------


def _read_entries(ledger_path: Path) -> list[StateLedgerEntry]:
    """Read every entry from `ledger_path` via the IS reader.

    Constructs a `JsonlLedgerHandle` directly — no
    `initialize_jsonl_event_ledger` (which would create the file if absent
    and `path.parent.mkdir(parents=True, exist_ok=True)`, violating the
    read-only invariant). At HEAD `read_ledger` only reads
    `canonical_path.read_text()`.
    """
    text = ledger_path.read_text()
    entry_count = sum(1 for line in text.splitlines() if line.strip())
    handle = JsonlLedgerHandle(
        canonical_path=ledger_path,
        exists=True,
        entry_count=entry_count,
    )
    return read_ledger(handle)


def _entry_head_hash(entry: StateLedgerEntry) -> str:
    """Lowercase hex of `entry.response_hash` (the C-IS-06 chain head)."""
    return entry.response_hash.hex()


def _entry_summary(entry: StateLedgerEntry) -> dict[str, Any]:
    """One-entry summary dict — JSON-serializable + human-readable source.

    `Timestamp` is `datetime` per C-IS-05 §5; serialized as ISO-8601 string.
    """
    return {
        "action_id": str(entry.action_id),
        "idempotency_key": str(entry.idempotency_key),
        "actor_class": entry.actor.actor_class.value,
        "actor_id": entry.actor.actor_id,
        "timestamp": entry.timestamp.isoformat(),
        "response_hash": entry.response_hash.hex(),
        "prior_event_hash": entry.prior_event_hash.hex(),
    }


# ---------------------------------------------------------------------------
# Output formatters.
# ---------------------------------------------------------------------------


def _format_human(
    *,
    ledger_path: Path,
    entries: list[StateLedgerEntry],
    last_n: int,
) -> str:
    lines: list[str] = []
    lines.append("harness-inspect — read-only summary")
    lines.append(f"  ledger:        {ledger_path}")
    lines.append(f"  total_entries: {len(entries)}")

    if not entries:
        lines.append("  head_hash:     (genesis — no entries)")
    else:
        lines.append(f"  head_hash:     {_entry_head_hash(entries[-1])}")

    lines.append("")
    lines.append(f"Last {min(last_n, len(entries)) if last_n > 0 else 0} entries:")
    for entry in entries[-last_n:] if last_n > 0 else []:
        s = _entry_summary(entry)
        lines.append(
            f"  - action_id={s['action_id']!s} "
            f"actor={s['actor_class']}/{s['actor_id']} "
            f"ts={s['timestamp']} "
            f"response_hash={s['response_hash'][:16]}…"
        )

    lines.append("")
    lines.append(f"Spans: N/A — {_SPANS_UNAVAILABLE_REASON}")
    lines.append(f"Cost rollup: N/A — {_COST_UNAVAILABLE_REASON}")
    return "\n".join(lines) + "\n"


def _format_json(
    *,
    ledger_path: Path,
    entries: list[StateLedgerEntry],
    last_n: int,
) -> str:
    head = _entry_head_hash(entries[-1]) if entries else None
    payload: dict[str, Any] = {
        "ledger_path": str(ledger_path),
        "total_entries": len(entries),
        "head_hash": head,
        "entries": [_entry_summary(e) for e in (entries[-last_n:] if last_n > 0 else [])],
        "spans": None,
        "spans_unavailable_reason": _SPANS_UNAVAILABLE_REASON,
        "cost_rollup": None,
        "cost_rollup_unavailable_reason": _COST_UNAVAILABLE_REASON,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


# ---------------------------------------------------------------------------
# --browse (C-OD-19 §19.3 TUI trace browser).
# ---------------------------------------------------------------------------


def _run_browse(collector_path: Path | None) -> int:
    """Launch the TUI trace browser over `collector_path`. Returns the exit code."""
    if collector_path is None:
        print(
            "harness-inspect: RT-FAIL-INSPECT-PATH — --browse requires --collector-path",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH

    import curses

    from harness_runtime.admin.trace_browser import (
        compute_operator_burden_rollups,
        open_readonly_span_store,
        run_trace_browser_tui,
    )

    try:
        conn = open_readonly_span_store(collector_path)
    except sqlite3.DatabaseError as exc:
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — collector sqlite not found "
            f"or unreadable at {collector_path}: {exc}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    try:
        # Run the real rollup query before entering curses — a wrong/old
        # collector-db schema (missing table, missing column) or a file that
        # isn't a sqlite database at all (`sqlite3.DatabaseError`, which
        # `OperationalError` subclasses — SQLite defers "file is not a
        # database" until the first read) then surfaces here as a clean
        # RT-FAIL-INSPECT-PATH exit rather than a raw traceback mid-render
        # inside `curses.wrapper`.
        rollups = compute_operator_burden_rollups(conn)
    except sqlite3.DatabaseError as exc:
        conn.close()
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — {collector_path} is not an "
            f"initialized span store: {exc}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    try:
        curses.wrapper(run_trace_browser_tui, rollups)
    finally:
        conn.close()
    return _EXIT_OK


# ---------------------------------------------------------------------------
# Holdout-loop actions (B-OD17-EVAL-LOOP-TOOLING; C-OD-17 §17.3).
#
# Each function makes NO model calls and computes no judge/alignment ratio —
# per the standing model-judge-as-governance-gate refusal, this tooling only
# samples, persists operator input, and scaffolds files for a human to fill
# in by hand.
# ---------------------------------------------------------------------------


def _run_holdout_sample(args: argparse.Namespace) -> int:
    from harness_od.holdout_set import sample_holdout_traces as sample
    from harness_od.holdout_set import write_holdout_set

    if args.collector_path is None or args.holdout_path is None or args.primitive is None:
        print(
            "harness-inspect: RT-FAIL-INSPECT-PATH — --holdout-sample requires "
            "--collector-path, --holdout-path, and --primitive",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    try:
        conn = open_readonly_span_store_for_holdout(args.collector_path)
    except sqlite3.DatabaseError as exc:
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — collector sqlite not found "
            f"or unreadable at {args.collector_path}: {exc}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    try:
        holdout = sample(
            conn,
            cell_id=_parse_cell_id(args.cell_id),
            primitive=OperatorBurdenEvalPrimitive(args.primitive),
            n=args.holdout_sample,
            seed=args.seed,
            sampled_at=datetime.now(UTC).isoformat(),
        )
    except sqlite3.DatabaseError as exc:
        # sqlite defers "not a database" / wrong-schema errors to first query —
        # `open_readonly_span_store_for_holdout` only calls `sqlite3.connect`,
        # so a wrong-schema file surfaces here, not at connect time.
        conn.close()
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — {args.collector_path} is "
            f"not an initialized span store: {exc}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    conn.close()
    write_holdout_set(holdout, args.holdout_path)
    print(
        f"harness-inspect: wrote {len(holdout.traces)} trace(s) to {args.holdout_path} "
        f"(seed={args.seed}, primitive={args.primitive})"
    )
    return _EXIT_OK


def _run_holdout_review(args: argparse.Namespace, *, input_fn: Any = None) -> int:
    # `input_fn` defaults to `None` rather than binding the `input` builtin
    # directly: a default-argument expression is evaluated once at function-
    # definition time, so `input_fn: Any = input` would freeze the reference
    # before a test's `monkeypatch.setattr("builtins.input", ...)` ever runs.
    # A bare `input(...)` call below is a dynamic builtins lookup at CALL
    # time, which the monkeypatch does reach.
    if input_fn is None:
        input_fn = input
    from harness_od.holdout_review_ledger import (
        ReviewEntry,
        append_review_entry,
        reviewed_trace_ids,
    )
    from harness_od.holdout_set import read_holdout_set

    if args.holdout_path is None or args.review_ledger_path is None:
        print(
            "harness-inspect: RT-FAIL-INSPECT-PATH — --holdout-review requires "
            "--holdout-path and --review-ledger-path",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    try:
        holdout = read_holdout_set(args.holdout_path)
    except (OSError, ValueError) as exc:
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — cannot read holdout set at "
            f"{args.holdout_path}: {exc}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH

    already = reviewed_trace_ids(args.review_ledger_path)
    pending = [t for t in holdout.traces if t.trace_id not in already]
    if not pending:
        print("harness-inspect: nothing to review — every trace is already categorized.")
        return _EXIT_OK

    for trace in pending:
        print(
            f"\ntrace_id={trace.trace_id}  spans={trace.span_count}  "
            f"primitive={holdout.primitive.value}"
        )
        category = input_fn("category> ").strip()
        if not category:
            print("harness-inspect: empty category — skipping this trace.")
            continue
        notes_raw = input_fn("notes (optional)> ").strip()
        append_review_entry(
            args.review_ledger_path,
            ReviewEntry(
                cell_id=holdout.cell_id,
                primitive=holdout.primitive,
                trace_id=trace.trace_id,
                category=category,
                notes=notes_raw or None,
                reviewed_at=datetime.now(UTC).isoformat(),
            ),
        )
    print(f"\nharness-inspect: review ledger at {args.review_ledger_path}")
    return _EXIT_OK


def _run_holdout_scaffold(args: argparse.Namespace) -> int:
    from harness_od.holdout_assertion_scaffold import scaffold_pending_stubs

    if args.review_ledger_path is None:
        print(
            "harness-inspect: RT-FAIL-INSPECT-PATH — --holdout-scaffold requires "
            "--review-ledger-path",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    written = scaffold_pending_stubs(args.review_ledger_path, args.stub_dir)
    if written:
        print(f"harness-inspect: scaffolded {len(written)} stub(s) in {args.stub_dir}:")
        for path in written:
            print(f"  - {path}")
    else:
        print(f"harness-inspect: no new stubs — {args.stub_dir} is already up to date.")
    return _EXIT_OK


def open_readonly_span_store_for_holdout(collector_path: Path) -> sqlite3.Connection:
    """Read-only open shared with `--browse` (same read-only invariant, C-RT-13)."""
    from harness_runtime.admin.trace_browser import open_readonly_span_store

    return open_readonly_span_store(collector_path)


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """`harness-inspect` entry point.

    Returns the process exit code (0 success; 2 RT-FAIL-INSPECT-PATH).
    Wired by `[project.scripts]` in `harness-runtime/pyproject.toml`.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.browse:
        return _run_browse(args.collector_path)
    if args.holdout_sample is not None:
        return _run_holdout_sample(args)
    if args.holdout_review:
        return _run_holdout_review(args)
    if args.holdout_scaffold:
        return _run_holdout_scaffold(args)

    ledger_path: Path = args.ledger_path
    last_n: int = args.last_n

    try:
        entries = _read_entries(ledger_path)
    except FileNotFoundError:
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — ledger not found: {ledger_path}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH
    except OSError as exc:
        print(
            f"harness-inspect: RT-FAIL-INSPECT-PATH — read error on {ledger_path}: {exc}",
            file=sys.stderr,
        )
        return _EXIT_INSPECT_PATH

    if args.json:
        output = _format_json(ledger_path=ledger_path, entries=entries, last_n=last_n)
    else:
        output = _format_human(ledger_path=ledger_path, entries=entries, last_n=last_n)

    sys.stdout.write(output)
    return _EXIT_OK


if __name__ == "__main__":  # pragma: no cover — invoked via console_script
    raise SystemExit(main())

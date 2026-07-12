"""TUI trace browser — C-OD-19 §19.3 (B-OD19-LOCAL-INSPECTION slice a).

Terminal-native scoped-query browser over the sqlite ring-buffer span store.
Per §19.3 ("Deferred to implementation discretion: specific TUI trace browser
implementation — terminal toolkit binding; query language"), this binds
stdlib `curses` (bounded framework-pull adoption per workspace CLAUDE.md
§3.2 — operator dev machine is Intel x86 macOS, `curses` ships in the
stdlib, no dependency added).

Split for headless testability: `compute_operator_burden_rollups` +
`render_operator_burden_screen` are pure (state → data / data → screen
lines); `run_trace_browser_tui` is the thin curses driver that threads
keypresses back into the pure render function. The acceptance bar ("scripted
TUI test or headless render harness") is met by testing the pure functions
directly — no live terminal required.

Reuses `harness_od.sqlite_span_store_reader.read_spans_by_name` (the
extension point that reader module's own docstring anticipated: "consumers
(TUI per §19.3...) cannot drift to string concatenation") and
`harness_od.operator_burden_eval_primitives.EVAL_PRIMITIVE_DECLARATIONS`
(the canonical 5-primitive set per C-OD-17 §17.1) — extends `harness-inspect`
internals rather than forking a separate reader.

**Scope boundary** (see `.harness/b-od19-slice-c-otelcol-manifest-reconciliation.md`):
this module renders whatever the sqlite span store contains. At HEAD nothing
in production writes real spans there (the in-process collector daemon's
`ingest_span_row` has no production caller — a pre-existing, already-
documented deferral, not introduced here). Tested against seeded data.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from harness_od.operator_burden_eval_primitives import (
    EVAL_PRIMITIVE_DECLARATIONS,
    EvalPrimitiveDeclaration,
)
from harness_od.sqlite_span_store import SpanInsertRow
from harness_od.sqlite_span_store_reader import read_spans_by_name

__all__ = [
    "OperatorBurdenRollup",
    "compute_operator_burden_rollups",
    "open_readonly_span_store",
    "render_operator_burden_screen",
    "run_trace_browser_tui",
]


@dataclass(frozen=True, slots=True)
class OperatorBurdenRollup:
    """One row of the TUI's operator-burden eval primitive view (§19.3).

    `value` is populated only when the primitive's C-OD-17 §17.1 declaration
    names a `computation_formula` (`cache_hit_rate_alignment_floor` is the
    only one at HEAD); the two holdout-evaluable primitives
    (`sandbox_tier_routing_accuracy`, `routing_accuracy_holdout`) surface
    `matching_span_count` only — computing their meta-judge ratio requires
    the B-OD17 holdout-set tooling (a separate registered arc) and is not
    fabricated here.
    """

    declaration: EvalPrimitiveDeclaration
    matching_span_count: int
    value: float | None


def _cache_hit_ratio(rows: list[SpanInsertRow]) -> float | None:
    """§17.1 primitive-4 formula: cache_read / (cache_read + cache_creation).

    Reads the two `anthropic.cache_*` token attributes out of each matching
    span's `attributes_json`; malformed/missing attributes contribute zero.
    Returns `None` when no matching span carries either attribute (nothing
    to divide by), which the render layer treats as "no data yet" rather
    than a fabricated 0.0.
    """
    read_total = 0
    creation_total = 0
    for row in rows:
        try:
            parsed = json.loads(row.attributes_json)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        attrs = cast("dict[str, Any]", parsed)
        read_total += _coerce_int(attrs.get("anthropic.cache_read_input_tokens"))
        creation_total += _coerce_int(attrs.get("anthropic.cache_creation_input_tokens"))
    denom = read_total + creation_total
    if denom == 0:
        return None
    return read_total / denom


def _coerce_int(value: object) -> int:
    """Best-effort int coercion for a span attribute value.

    Non-numeric / missing / `None` values contribute zero rather than raising
    — an eval rollup over operator-facing span data must not crash on a
    malformed attribute."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def compute_operator_burden_rollups(
    conn: sqlite3.Connection,
) -> tuple[OperatorBurdenRollup, ...]:
    """Scoped-query rollup over the 5 operator-burden eval primitives (§19.3).

    One `OperatorBurdenRollup` per `EVAL_PRIMITIVE_DECLARATIONS` entry
    (canonical order), querying the sqlite span store for spans whose `name`
    equals the primitive's `source_span_class`. §17.1 declares the same
    `source_span_class` (`"meta-eval"`) for two primitives
    (`sandbox_tier_routing_accuracy`, `routing_accuracy_holdout`) — both
    surface the same matching-span count per the spec's own
    primitive-to-span-class mapping; this is spec fidelity, not an
    under-differentiated query.
    """
    rollups: list[OperatorBurdenRollup] = []
    for declaration in EVAL_PRIMITIVE_DECLARATIONS:
        rows = read_spans_by_name(conn, declaration.source_span_class)
        value = _cache_hit_ratio(rows) if declaration.computation_formula else None
        rollups.append(
            OperatorBurdenRollup(
                declaration=declaration,
                matching_span_count=len(rows),
                value=value,
            )
        )
    return tuple(rollups)


def render_operator_burden_screen(
    rollups: Sequence[OperatorBurdenRollup],
    *,
    selected_index: int,
    width: int = 100,
) -> list[str]:
    """Pure state → screen-buffer render (headlessly testable; no curses call).

    Returns a list of text lines. `selected_index` drives the `>` cursor
    marker on one row — the only view state the curses driver threads back
    into this pure function on each keypress.
    """
    lines = [
        "harness-inspect --browse — operator-burden eval primitives (C-OD-19 §19.3)",
        "",
    ]
    for i, rollup in enumerate(rollups):
        marker = ">" if i == selected_index else " "
        name = rollup.declaration.primitive.value
        if rollup.value is not None:
            metric = f"ratio={rollup.value:.3f} ({rollup.matching_span_count} spans)"
        elif rollup.declaration.holdout_evaluable:
            metric = (
                f"count={rollup.matching_span_count} "
                "(holdout-evaluable; ratio needs B-OD17 holdout tooling)"
            )
        else:
            metric = f"count={rollup.matching_span_count}"
        lines.append(f"{marker} {name:<45} {metric}")
    lines.append("")
    if 0 <= selected_index < len(rollups):
        detail = rollups[selected_index].declaration
        lines.append(
            f"source_span_class={detail.source_span_class}  source_adr={detail.source_adr}"
        )
    lines.append("")
    lines.append("[up/down navigate]  [q quit]")
    return [line[:width] for line in lines]


def open_readonly_span_store(db_path: Path) -> sqlite3.Connection:
    """Open the sqlite span store read-only (C-RT-13 read-only invariant: no
    writes from an inspection tool). Raises `sqlite3.OperationalError` when
    `db_path` does not exist — the caller maps this to `RT-FAIL-INSPECT-PATH`,
    mirroring `harness-inspect`'s existing ledger-read failure mode.

    Builds the `file:` URI via `Path.as_uri()` (percent-encodes the path)
    before appending `?mode=ro` — a raw `f"file:{db_path}?mode=ro"` would let
    a `?` or `#` in an operator-supplied path be parsed as URI syntax,
    truncating the path and silently dropping the read-only mode.
    """
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def run_trace_browser_tui(stdscr: object, rollups: tuple[OperatorBurdenRollup, ...]) -> None:
    """Thin curses driver. All rendering logic lives in the pure functions
    above; this loop only handles terminal I/O + keypress dispatch.

    Takes precomputed `rollups` (not a live connection) — the caller runs
    `compute_operator_burden_rollups(conn)` *before* entering
    `curses.wrapper`, so a malformed/wrong-schema span-store sqlite file
    raises `sqlite3.OperationalError` where the caller can map it to a clean
    `RT-FAIL-INSPECT-PATH` exit rather than crashing mid-render inside curses.

    `stdscr` is the `curses` window object passed by `curses.wrapper(...)`
    (typed `object` here to keep this module importable/testable on
    platforms without a live terminal — `curses` itself is imported lazily,
    only when this function actually runs).
    """
    import curses

    win = cast("curses.window", stdscr)
    selected = 0
    curses.curs_set(0)
    while True:
        lines = render_operator_burden_screen(
            rollups, selected_index=selected, width=curses.COLS - 1
        )
        win.erase()
        for row, line in enumerate(lines[: curses.LINES]):
            win.addstr(row, 0, line)
        win.refresh()
        key = win.getch()
        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(rollups) - 1:
            selected += 1
        elif key in (ord("q"), 27):
            return

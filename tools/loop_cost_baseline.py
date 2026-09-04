#!/usr/bin/env python3
"""Loop cost baseline: one JSON object from .harness/merge-gate-log.jsonl (plan Task 0).

Read-only. Feeds the §0 table of .harness/plan/loop-optimization-plan-2026-09-03.md and is
re-run after each of the plan's merges so every saving is measured against the same rows.

Rules the numbers follow (each one a reviewer finding on the registration PR or this arc):
  * a round is a distinct (channel, head_sha, pass) per arc, named by ANY record kind, over
    the REVIEW producers only: `codex_review_wrapper` and `gemini_review_wrapper` (each its
    own paid round, scoped per producer — `just gemini-review` runs standalone) and the merge
    gate (three `merge-gate-*` lenses). A gemini row is ALWAYS its own producer round here:
    the C-HE-17 D-C failover child is forced to the primary's round number
    (review_wrapper_common.round_n_for) but the log carries no failover marker, so a
    reducer cannot tell a failover child from a standalone `just gemini-review` that
    happened to share the key. Inferring lineage from key coincidence was tried and
    reversed (b-230-task-0 r6/r7); instead `failover_ambiguous_rounds` reports how many
    (arc, head, round_n) keys carry both a codex `reviewer_unavailable` row and a gemini
    row — the exact upper bound on the overcount — and the marker is forward work
    on the wrapper (register B-231). Head-bound, because round_n is reused across an
    arc's review heads (branch-he-lanes-s1 has codex round 0 on six heads). A gate lens
    mints its round_n INDEPENDENTLY (PR 1414 recorded one three-lens pass as concurrency r3
    beside spec/witness r2), so a gate pass at a head is the per-lens RANK of the lens's
    round_n at that head: the k-th distinct round of each lens at one head is pass k, and
    lenses at the same rank are one pass. Codex r1 and gate pass 1 are two rounds (u-he-35:
    10 + 3 = 13). A clean `no_finding` round and a clean-only arc count; probe producers
    (`reviewer_concurrency_probe`, whose round_n is an iteration index) and door producers
    (round_n null) are not rounds;
  * `gate_rounds_with_findings` / `single_lens_rounds` group lens VERDICT finding rows by that
    pass identity; single = exactly one lens producer raised findings in the pass. Two row
    shapes under a lens producer are NOT lens work and count nowhere here: the row the gate
    emitter writes about ITSELF (the markdown-sibling write failure, `finding_type:
    transient-retry`, `lineage_claim: wrapper`, merge_gate_log.py:300-316) and the typed
    detector-skip row the plan's Task 6 defines (`no_finding` with `finding_type:
    lens_skipped`) — a skipped reviewer is the cost reduction this baseline measures, never
    work performed;
  * a `unique_catch` flag counts only when the finding's LAST `finding_adjudication` row is
    `accepted` — last in APPEND order, the reducer authority C-HE-24 §5 names ("readers
    reduce by finding_id → last row"), never by ts; rejected / suppressed and
    never-adjudicated flags are reported in their own counters and never folded in;
  * catches are counted per DISTINCT finding_id (C-HE-24 §5 N6 shape): a same-core retry
    re-emits a finding row under the same id before adjudication and is one finding, and the
    LAST finding row of the lineage (append order) carries the flag that counts —
    `unique_catch` is outside finding_record._CORE_IMMUTABLE, so a retry may lower it;
  * `arcs` counts every distinct arc_id in the log (door-only arcs included — the two lease
    events live on `u-he-32-refresh2`, which never had a review round); `reviewed_arcs` is
    the rounds-per-arc denominator (arcs with at least one review round);
  * `codex_rows` / `lens_rows` are the rows the out-of-family wrapper / the gate lenses
    WROTE — `finding`, `no_finding`, `reviewer_unavailable` — never `finding_adjudication`
    rows, which keep the producer but are written by the absorber (`disposition_actor`);
  * `lease_acquire_events` are the door's own rows only — `record_kind: finding` with
    `finding_type: HITL-recoverable` from producer `merge-door-lease-acquire`; a later
    adjudication row of such an event is not a second event;
  * `--loop-status` counts the NOTIFY rows whose cause is exactly
    `merge-door-lease-acquire:lease_held_yield` (Task 8's out-of-repo contention row);
    without the flag that field is null — an honest could-not-look, never a zero.
    `lease_held_yields_30d_max` is the B-232 trigger as a ROLLING window — the most
    such rows whose `ts` fall in any half-open 30-day span [t, t + 30 d) — because a
    lifetime count would read "triggered" forever after six events spread over years;
    two rows exactly 30 days apart are in different windows.

Usage:
    uv run python tools/loop_cost_baseline.py [--log PATH] [--loop-status PATH]
Exit 0 with the JSON object on stdout; exit 2 when the log has no rows (a measurement
over nothing is a defect in the invocation, not a baseline of zeros).
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path

YIELD_CAUSE = "merge-door-lease-acquire:lease_held_yield"
TRIGGER_WINDOW = timedelta(days=30)  # B-232: > TRIGGER_THRESHOLD yield rows in any window
TRIGGER_THRESHOLD = 5  # B-232 trigger: lease_held_yields_30d_max > 5 opens the spec leg
#: The structured column EXACTLY as `loop_log_structured` writes it: `lane=<x>;cause=<y>`,
#: both keys, in that order, with `;` and whitespace stripped from the values
#: (`_loop_structured_col`, tools/hooks/loop_lib.sh:151-166). Matching any `key=value`
#: run instead misreads a LEGACY free-text detail that happens to be one token — a
#: three-column row ending `status=done` — as a truncated structured row, and since the
#: pilot report refuses on those, ONE such historical row would make every future report
#: permanently unanswerable (codex r4 P2, on the r3 fix).
_STRUCTURED_COL = re.compile(r"lane=[^;\s]*;cause=[^;\s]*")
LEASE_PRODUCER = "merge-door-lease-acquire"
CODEX_PRODUCER = "codex_review_wrapper"
GEMINI_PRODUCER = "gemini_review_wrapper"
OUT_OF_FAMILY = frozenset({CODEX_PRODUCER, GEMINI_PRODUCER})
WRAPPER_WRITTEN_KINDS = frozenset({"finding", "no_finding", "reviewer_unavailable"})
LENS_SKIPPED = "lens_skipped"  # plan Task 6's typed detector-skip row; not lens work


def _is_lens(producer: object) -> bool:
    return isinstance(producer, str) and producer.startswith("merge-gate")


def _is_lens_verdict_row(r: dict) -> bool:
    """A row a lens's verdict produced. The lens's `no_finding` / `reviewer_unavailable` marker
    rows carry `lineage_claim: wrapper` and ARE its verdict. Excluded: a `finding` the emitter
    wrote about itself under the lens's producer (the markdown-sibling write failure,
    merge_gate_log.py:300-316 — a finding row with `lineage_claim: wrapper`), and the typed
    detector-skip row (`no_finding` with `finding_type: lens_skipped`, plan Task 6)."""
    if not (_is_lens(r.get("producer")) and r.get("record_kind") in WRAPPER_WRITTEN_KINDS):
        return False
    if r.get("record_kind") == "finding" and r.get("lineage_claim") == "wrapper":
        return False
    return r.get("finding_type") != LENS_SKIPPED


def _channel(producer: object) -> str | None:
    """The round namespace a producer's round_n lives in; None for non-review producers."""
    if producer in OUT_OF_FAMILY:
        return str(producer)
    if _is_lens(producer):
        return "gate"
    return None


def _failover_ambiguous_rounds(rows: list[dict]) -> int:
    """Keys (arc_id, head_sha, round_n) carrying both a codex `reviewer_unavailable` row and a
    gemini row: each MAY be a D-C failover child counted as an extra round. The log has no
    marker to settle it, so the count is reported as the overcount's upper bound."""
    unavailable = {
        (r.get("arc_id"), r.get("head_sha"), r.get("round_n"))
        for r in rows
        if r.get("producer") == CODEX_PRODUCER and r.get("record_kind") == "reviewer_unavailable"
    }
    gemini = {
        (r.get("arc_id"), r.get("head_sha"), r.get("round_n"))
        for r in rows
        if r.get("producer") == GEMINI_PRODUCER and r.get("round_n") is not None
    }
    return len(unavailable & gemini)


def _last_dispositions(rows: list[dict]) -> dict[str, str]:
    """finding_id -> disposition of its LAST adjudication row in APPEND order (C-HE-24 §5)."""
    latest: dict[str, str] = {}
    for r in rows:
        if r.get("record_kind") == "finding_adjudication":
            latest[str(r.get("finding_id"))] = str(r.get("disposition"))
    return latest


def _gate_pass_ranks(rows: list[dict]) -> dict[tuple, int]:
    """(arc_id, head_sha, lens, round_n) -> pass rank at that head (1 = the lens's first round)."""
    seen: dict[tuple, set] = collections.defaultdict(set)
    for r in rows:
        if _is_lens(r.get("producer")) and r.get("round_n") is not None:
            seen[(r.get("arc_id"), r.get("head_sha"), r.get("producer"))].add(r.get("round_n"))
    ranks: dict[tuple, int] = {}
    for (arc, head, lens), rounds in seen.items():
        for k, n in enumerate(sorted(rounds), start=1):
            ranks[(arc, head, lens, n)] = k
    return ranks


def summarize(rows: list[dict], loop_status_rows: list[str] | None = None) -> dict:
    per_arc: dict[str, set] = collections.defaultdict(set)
    by_round: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    ranks = _gate_pass_ranks(rows)
    for r in rows:
        channel = _channel(r.get("producer"))
        if r.get("round_n") is None or channel is None:
            continue
        if channel == "gate" and not _is_lens_verdict_row(r):
            continue  # a typed skip row is not a gate pass
        arc, head, n = r.get("arc_id"), r.get("head_sha"), r.get("round_n")
        if channel == "gate":
            n = ranks[(arc, head, r.get("producer"), n)]
        per_arc[str(arc)].add((channel, head, n))
        if r.get("record_kind") == "finding" and channel == "gate" and _is_lens_verdict_row(r):
            by_round[(arc, head, n)][r.get("producer")] += 1

    gate_rounds = [k for k, c in by_round.items() if any(_is_lens(p) for p in c)]
    single = [k for k in gate_rounds if sum(1 for p in by_round[k] if _is_lens(p)) == 1]

    last = _last_dispositions(rows)
    # one entry per DISTINCT finding_id; the LAST finding row of the lineage (append order)
    # decides the flag, since a same-core retry may re-emit the id with a different value
    lineage_last: dict[str, dict] = {}
    for r in rows:
        if r.get("record_kind") == "finding":
            lineage_last[str(r.get("finding_id"))] = r
    flagged = {
        fid: r.get("producer") for fid, r in lineage_last.items() if r.get("unique_catch") is True
    }
    accepted = collections.Counter(
        producer for fid, producer in flagged.items() if last.get(fid) == "accepted"
    )
    rejected_or_suppressed = sum(
        1 for fid in flagged if last.get(fid) in ("rejected", "suppressed")
    )
    unadjudicated = sum(1 for fid in flagged if fid not in last)
    lease_events = sum(
        1
        for r in rows
        if r.get("record_kind") == "finding"
        and r.get("finding_type") == "HITL-recoverable"
        and r.get("producer") == LEASE_PRODUCER
    )
    codex_rows = sum(
        1
        for r in rows
        if r.get("producer") == CODEX_PRODUCER and r.get("record_kind") in WRAPPER_WRITTEN_KINDS
    )
    lens_rows = sum(1 for r in rows if _is_lens_verdict_row(r))
    all_arcs = {str(r.get("arc_id")) for r in rows}

    yields: int | None = None
    yields_30d_max: int | None = None
    if loop_status_rows is not None:
        stamps = yield_stamps(loop_status_rows)
        yields = len(stamps)
        yields_30d_max = rolling_window_max(stamps, TRIGGER_WINDOW)

    return {
        "rows": len(rows),
        "arcs": len(all_arcs),
        "reviewed_arcs": len(per_arc),
        "rounds_per_arc_median": statistics.median(len(v) for v in per_arc.values())
        if per_arc
        else 0,
        "rounds_per_arc_max": max((len(v) for v in per_arc.values()), default=0),
        "failover_ambiguous_rounds": _failover_ambiguous_rounds(rows),
        "codex_rows": codex_rows,
        "lens_rows": lens_rows,
        "gate_rounds_with_findings": len(gate_rounds),
        "single_lens_rounds": len(single),
        "unique_catch_raw": len(flagged),
        "unique_catch_by_producer": dict(accepted),
        "unique_catch_rejected_or_suppressed": rejected_or_suppressed,
        "unique_catch_unadjudicated": unadjudicated,
        "lease_acquire_events": lease_events,
        "lease_held_yields": yields,
        "lease_held_yields_30d_max": yields_30d_max,
    }


def _row_ts(line: str) -> datetime:
    """The `ts` cell of a loop_status.md row, ISO-8601 with a `Z` suffix (loop_now). A
    malformed stamp raises — a row the trigger cannot place in time is a defect in the
    ledger, never a row to drop ([LAW:no-silent-failure])."""
    return datetime.fromisoformat(line.split("|")[1].strip().replace("Z", "+00:00"))


def rolling_window_max(stamps: list[datetime], window: timedelta) -> int:
    """The most stamps inside any half-open window [t, t + window) — two-pointer over
    the sorted stamps; pure ([LAW:effects-at-boundaries]). Empty input → 0."""
    ordered = sorted(stamps)
    best = lo = 0
    for hi, t in enumerate(ordered):
        while t - ordered[lo] >= window:
            lo += 1
        best = max(best, hi - lo + 1)
    return best


def parse_loop_row(line: str) -> dict[str, str] | None:
    """One shared-ledger row as `{ts, kind, lane, cause, detail}`, or None for a line that
    is not a data row (the header, the `|---|` rule, prose).

    THE parser for the ledger's row grammar ([LAW:one-source-of-truth]): `_is_yield_row`
    below and `tools/lanes_pilot.py`'s C-HE-13 §3 report both reduce through it, so the
    grammar has one reader rather than a regex per consumer.

    Two row shapes are live and are told apart by cell count, not by guessing: the
    structured 4-column row `loop_log_structured` writes (`ts | kind | lane=…;cause=… |
    detail`) and the older 3-column `ts | kind | detail`, whose lane and cause are empty
    strings — absent, never invented."""
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 5 or not cells[1] or cells[1] == "ts" or set(cells[2]) <= {"-"}:
        return None
    # Structured vs legacy is decided by the third cell's SHAPE, not by cell count. Counting
    # alone reads a TRUNCATED structured row (`| ts | DEFERRED-HIL | lane=L;cause=x |`, five
    # cells) as a legacy three-column row, silently yielding an empty cause and the metadata
    # as the detail — so a truncated coordination escalation would parse "successfully" and
    # slip past a consumer's malformed-row refusal (codex r3 P2). The structured cell is
    # entirely `key=value` pairs joined by `;` with no spaces; a legacy detail that merely
    # contains an `=` (`holder=u-9 backoff=0`) has a space and is not mistaken for one.
    structured_col = bool(_STRUCTURED_COL.fullmatch(cells[3]))
    if structured_col and len(cells) < 6:
        return None  # truncated structured row: unreadable, never silently legacy
    structured = structured_col and len(cells) >= 6
    fields = dict(p.split("=", 1) for p in (cells[3] if structured else "").split(";") if "=" in p)
    return {
        "ts": cells[1],
        "kind": cells[2],
        "lane": fields.get("lane", ""),
        "cause": fields.get("cause", ""),
        "detail": cells[4] if structured else cells[3],
    }


def _is_yield_row(line: str) -> bool:
    """A loop_status.md table row `| ts | NOTIFY | lane=…;cause=<YIELD_CAUSE> | detail |`."""
    row = parse_loop_row(line)
    return bool(row) and row["kind"] == "NOTIFY" and row["cause"] == YIELD_CAUSE


def yield_stamps(lines: list[str]) -> list[datetime]:
    """The `ts` of every lease_held_yield NOTIFY row — the one seam both the baseline
    and tools/lease_yield_trigger.py (the session-start carrier) read through."""
    return [_row_ts(line) for line in lines if _is_yield_row(line)]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--log", default=".harness/merge-gate-log.jsonl")
    ap.add_argument(
        "--loop-status", default=None, help="loop_status.md; counts lease_held_yield NOTIFY rows"
    )
    a = ap.parse_args()
    rows = [json.loads(line) for line in Path(a.log).read_text().splitlines() if line.strip()]
    if not rows:
        print(f"loop_cost_baseline: no rows in {a.log}", file=sys.stderr)
        return 2
    status_rows = Path(a.loop_status).read_text().splitlines() if a.loop_status else None
    json.dump(summarize(rows, status_rows), sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

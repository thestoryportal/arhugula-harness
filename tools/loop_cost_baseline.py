#!/usr/bin/env python3
"""Loop cost baseline: one JSON object from .harness/merge-gate-log.jsonl (plan Task 0).

Read-only. Feeds the §0 table of .harness/plan/loop-optimization-plan-2026-09-03.md and is
re-run after each of the plan's merges so every saving is measured against the same rows.

Rules the numbers follow (each one a reviewer finding on the registration PR or this arc):
  * a round is a distinct (channel, head_sha, pass) per arc, named by ANY record kind, over
    the two REVIEW channels only: out-of-family (`codex_review_wrapper`, with
    `gemini_review_wrapper` the failover of the SAME round, so pass = round_n) and the merge
    gate (three `merge-gate-*` lenses). Head-bound, because round_n is reused across an
    arc's review heads (branch-he-lanes-s1 has codex round 0 on six heads). A gate lens
    mints its round_n INDEPENDENTLY (PR 1414 recorded one three-lens pass as concurrency r3
    beside spec/witness r2), so a gate pass at a head is the per-lens RANK of the lens's
    round_n at that head: the k-th distinct round of each lens at one head is pass k, and
    lenses at the same rank are one pass. Codex r1 and gate pass 1 are two rounds (u-he-35:
    10 + 3 = 13). A clean `no_finding` round and a clean-only arc count; probe producers
    (`reviewer_concurrency_probe`, whose round_n is an iteration index) and door producers
    (round_n null) are not rounds;
  * `gate_rounds_with_findings` / `single_lens_rounds` group lens finding rows by that pass
    identity; single = exactly one lens producer raised findings in the pass;
  * a `unique_catch` flag counts only when the finding's LAST `finding_adjudication` row is
    `accepted` — last in APPEND order, the reducer authority C-HE-24 §5 names ("readers
    reduce by finding_id → last row"), never by ts; rejected / suppressed and
    never-adjudicated flags are reported in their own counters and never folded in;
  * catches are counted per DISTINCT finding_id (C-HE-24 §5 N6 shape): a same-core retry
    re-emits a finding row under the same id before adjudication and is one finding;
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

Usage:
    uv run python tools/loop_cost_baseline.py [--log PATH] [--loop-status PATH]
Exit 0 with the JSON object on stdout; exit 2 when the log has no rows (a measurement
over nothing is a defect in the invocation, not a baseline of zeros).
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

YIELD_CAUSE = "merge-door-lease-acquire:lease_held_yield"
LEASE_PRODUCER = "merge-door-lease-acquire"
CODEX_PRODUCER = "codex_review_wrapper"
OUT_OF_FAMILY = frozenset({CODEX_PRODUCER, "gemini_review_wrapper"})
WRAPPER_WRITTEN_KINDS = frozenset({"finding", "no_finding", "reviewer_unavailable"})


def _is_lens(producer: object) -> bool:
    return isinstance(producer, str) and producer.startswith("merge-gate")


def _channel(producer: object) -> str | None:
    """The review channel a producer's round_n is scoped to; None for non-review producers."""
    if producer in OUT_OF_FAMILY:
        return "out-of-family"
    if _is_lens(producer):
        return "gate"
    return None


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
        arc, head, n = r.get("arc_id"), r.get("head_sha"), r.get("round_n")
        if channel == "gate":
            n = ranks[(arc, head, r.get("producer"), n)]
        per_arc[str(arc)].add((channel, head, n))
        if r.get("record_kind") == "finding" and channel == "gate":
            by_round[(arc, head, n)][r.get("producer")] += 1

    gate_rounds = [k for k, c in by_round.items() if any(_is_lens(p) for p in c)]
    single = [k for k in gate_rounds if sum(1 for p in by_round[k] if _is_lens(p)) == 1]

    last = _last_dispositions(rows)
    # one entry per DISTINCT flagged finding_id (a same-core retry repeats the id)
    flagged: dict[str, object] = {}
    for r in rows:
        if r.get("record_kind") == "finding" and r.get("unique_catch") is True:
            flagged.setdefault(str(r.get("finding_id")), r.get("producer"))
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
    lens_rows = sum(
        1
        for r in rows
        if _is_lens(r.get("producer")) and r.get("record_kind") in WRAPPER_WRITTEN_KINDS
    )
    all_arcs = {str(r.get("arc_id")) for r in rows}

    yields: int | None = None
    if loop_status_rows is not None:
        yields = sum(1 for line in loop_status_rows if _is_yield_row(line))

    return {
        "rows": len(rows),
        "arcs": len(all_arcs),
        "reviewed_arcs": len(per_arc),
        "rounds_per_arc_median": statistics.median(len(v) for v in per_arc.values())
        if per_arc
        else 0,
        "rounds_per_arc_max": max((len(v) for v in per_arc.values()), default=0),
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
    }


def _is_yield_row(line: str) -> bool:
    """A loop_status.md table row `| ts | NOTIFY | lane=…;cause=<YIELD_CAUSE> | detail |`."""
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 5 or cells[2] != "NOTIFY":
        return False
    return any(part == f"cause={YIELD_CAUSE}" for part in cells[3].split(";"))


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

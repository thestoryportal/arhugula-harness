#!/usr/bin/env python3
"""Loop cost baseline: one JSON object from .harness/merge-gate-log.jsonl (plan Task 0).

Read-only. Feeds the §0 table of .harness/plan/loop-optimization-plan-2026-09-03.md and is
re-run after each of the plan's merges so every saving is measured against the same rows.

Rules the numbers follow (each one a reviewer finding on the registration PR):
  * a round is any (arc_id, round_n) named by ANY record kind — a clean `no_finding`
    round and a clean-only arc count; door rows carry round_n null and are not rounds;
  * a `unique_catch` flag counts only when the finding's LAST `finding_adjudication`
    (by ts) is `accepted` (C-HE-29); rejected / suppressed and never-adjudicated flags
    are reported in their own counters and never folded into the catch;
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


def _is_lens(producer: object) -> bool:
    return isinstance(producer, str) and producer.startswith("merge-gate")


def _last_dispositions(rows: list[dict]) -> dict[str, str]:
    """finding_id -> disposition of its LAST adjudication row by ts (file order breaks ties)."""
    latest: dict[str, tuple[str, int, str]] = {}
    for i, r in enumerate(rows):
        if r.get("record_kind") != "finding_adjudication":
            continue
        fid = str(r.get("finding_id"))
        key = (str(r.get("ts") or ""), i, str(r.get("disposition")))
        if fid not in latest or key[:2] > latest[fid][:2]:
            latest[fid] = key
    return {fid: v[2] for fid, v in latest.items()}


def summarize(rows: list[dict], loop_status_rows: list[str] | None = None) -> dict:
    per_arc: dict[str, set] = collections.defaultdict(set)
    by_round: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        if r.get("round_n") is None:
            continue
        per_arc[str(r.get("arc_id"))].add(r.get("round_n"))
        if r.get("record_kind") == "finding":
            by_round[(r.get("arc_id"), r.get("round_n"))][r.get("producer")] += 1

    gate_rounds = [k for k, c in by_round.items() if any(_is_lens(p) for p in c)]
    single = [k for k in gate_rounds if sum(1 for p in by_round[k] if _is_lens(p)) == 1]

    last = _last_dispositions(rows)
    flagged = [
        r for r in rows if r.get("record_kind") == "finding" and r.get("unique_catch") is True
    ]
    accepted = collections.Counter(
        r.get("producer") for r in flagged if last.get(str(r.get("finding_id"))) == "accepted"
    )
    rejected_or_suppressed = sum(
        1 for r in flagged if last.get(str(r.get("finding_id"))) in ("rejected", "suppressed")
    )
    unadjudicated = sum(1 for r in flagged if str(r.get("finding_id")) not in last)

    yields: int | None = None
    if loop_status_rows is not None:
        yields = sum(1 for line in loop_status_rows if _is_yield_row(line))

    return {
        "rows": len(rows),
        "arcs": len(per_arc),
        "rounds_per_arc_median": statistics.median(len(v) for v in per_arc.values())
        if per_arc
        else 0,
        "gate_rounds_with_findings": len(gate_rounds),
        "single_lens_rounds": len(single),
        "unique_catch_raw": len(flagged),
        "unique_catch_by_producer": dict(accepted),
        "unique_catch_rejected_or_suppressed": rejected_or_suppressed,
        "unique_catch_unadjudicated": unadjudicated,
        "lease_acquire_events": sum(1 for r in rows if r.get("producer") == LEASE_PRODUCER),
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

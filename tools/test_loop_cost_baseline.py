"""Witness for tools/loop_cost_baseline.py (loop optimization plan, Task 0).

The fixture is the contract: a round is any (arc_id, round_n) named by ANY record kind,
door rows (round_n null) are not rounds, and a unique_catch flag counts only when the
finding's LAST adjudication is `accepted` (C-HE-29) — rejected, suppressed and unadjudicated
flags are each reported in their own counter, never folded into the catch.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from loop_cost_baseline import summarize

SCRIPT = Path(__file__).resolve().parent / "loop_cost_baseline.py"
YIELD = "merge-door-lease-acquire:lease_held_yield"


def _rows() -> list[dict]:
    return [
        {
            "record_kind": "finding",
            "arc_id": "a",
            "round_n": 1,
            "producer": "codex_review_wrapper",
            "finding_id": "c1",
            "unique_catch": False,
        },
        {
            "record_kind": "finding",
            "arc_id": "a",
            "round_n": 2,
            "producer": "merge-gate-witness-adequacy",
            "finding_id": "w1",
            "unique_catch": True,
        },
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": 2,
            "finding_id": "w1",
            "disposition": "accepted",
            "ts": "2026-09-03T10:00:00Z",
        },
        {
            "record_kind": "finding",
            "arc_id": "a",
            "round_n": 2,
            "producer": "merge-gate-spec-conformance",
            "finding_id": "s1",
            "unique_catch": True,
        },
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": 2,
            "finding_id": "s1",
            "disposition": "accepted",
            "ts": "2026-09-03T10:00:00Z",
        },
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": 2,
            "finding_id": "s1",
            "disposition": "rejected",
            "ts": "2026-09-03T10:00:01Z",
        },
        {
            "record_kind": "finding",
            "arc_id": "a",
            "round_n": 2,
            "producer": "merge-gate-concurrency",
            "finding_id": "k1",
            "unique_catch": True,
        },
        {
            "record_kind": "no_finding",
            "arc_id": "a",
            "round_n": 3,
            "producer": "merge-gate-concurrency",
        },
        {
            "record_kind": "finding",
            "finding_type": "HITL-recoverable",
            "arc_id": "a",
            "round_n": None,
            "producer": "merge-door-lease-acquire",
        },
    ]


def _run(log: Path, *extra: str) -> dict:
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--log", str(log), *extra],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out)


def test_baseline_reports_expected_keys(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    log.write_text("\n".join(json.dumps(r) for r in _rows()) + "\n")
    data = _run(log)
    assert data["rows"] == 9
    assert data["arcs"] == 1
    assert (
        data["rounds_per_arc_median"] == 3
    )  # the clean round 3 counts; the door row (round_n null) does not
    assert data["gate_rounds_with_findings"] == 1
    assert data["single_lens_rounds"] == 0  # round 2 had three lenses
    assert data["unique_catch_raw"] == 3
    assert data["unique_catch_by_producer"] == {
        "merge-gate-witness-adequacy": 1
    }  # s1's LAST disposition is rejected; k1 is unadjudicated
    assert data["unique_catch_rejected_or_suppressed"] == 1
    assert data["unique_catch_unadjudicated"] == 1
    assert data["lease_acquire_events"] == 1
    assert data["rounds_per_arc_max"] == 3
    assert data["codex_rows"] == 1
    assert (
        data["lease_held_yields"] is None
    )  # no --loop-status given: an honest could-not-look, never a zero


def test_last_appended_row_wins_not_the_latest_ts() -> None:
    # C-HE-24 §5: readers reduce by finding_id -> LAST ROW (append order). A row appended
    # later with an OLDER ts is still the reducer's answer; ts must not reorder it.
    rows = _rows()
    rows.append(
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": 2,
            "finding_id": "s1",
            "disposition": "accepted",
            "ts": "2026-09-03T09:00:00Z",
        }
    )
    data = summarize(rows)
    assert data["unique_catch_by_producer"] == {
        "merge-gate-witness-adequacy": 1,
        "merge-gate-spec-conformance": 1,
    }
    assert data["unique_catch_rejected_or_suppressed"] == 0


def test_same_core_retry_is_one_finding() -> None:
    rows = _rows()
    # w1 re-emitted under the same finding_id (a same-core retry before adjudication)
    rows.insert(2, dict(rows[1]))
    data = summarize(rows)
    assert data["rows"] == 10
    assert data["unique_catch_raw"] == 3
    assert data["unique_catch_by_producer"] == {"merge-gate-witness-adequacy": 1}


def test_lease_event_is_the_door_row_not_its_adjudication() -> None:
    rows = _rows()
    rows.append(
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": None,
            "finding_id": "door-1",
            "producer": "merge-door-lease-acquire",
            "disposition": "accepted",
            "ts": "2026-09-03T11:00:00Z",
        }
    )
    rows.append(
        {
            "record_kind": "finding",
            "finding_type": "terminal-block",
            "arc_id": "a",
            "round_n": 1,
            "producer": "merge-door-lease-acquire",
        }
    )
    assert summarize(rows)["lease_acquire_events"] == 1


def test_suppressed_is_not_a_catch() -> None:
    rows = _rows()
    rows.append(
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": 2,
            "finding_id": "w1",
            "disposition": "suppressed",
            "ts": "2026-09-03T10:00:05Z",
        }
    )
    data = summarize(rows)
    assert data["unique_catch_by_producer"] == {}
    assert data["unique_catch_rejected_or_suppressed"] == 2


def test_rounds_are_scoped_per_channel_and_probes_are_not_rounds() -> None:
    rows = [
        # codex r1 and gate pass 1 are TWO rounds; the three lenses share pass 1
        {
            "record_kind": "finding",
            "arc_id": "d",
            "round_n": 1,
            "producer": "codex_review_wrapper",
            "finding_id": "c9",
        },
        {
            "record_kind": "finding",
            "arc_id": "d",
            "round_n": 2,
            "producer": "codex_review_wrapper",
            "finding_id": "c10",
        },
        {
            "record_kind": "reviewer_unavailable",
            "arc_id": "d",
            "round_n": 3,
            "producer": "gemini_review_wrapper",
        },
        {
            "record_kind": "no_finding",
            "arc_id": "d",
            "round_n": 1,
            "producer": "merge-gate-concurrency",
        },
        {
            "record_kind": "no_finding",
            "arc_id": "d",
            "round_n": 1,
            "producer": "merge-gate-spec-conformance",
        },
        {
            "record_kind": "finding",
            "arc_id": "d",
            "round_n": 1,
            "producer": "merge-gate-witness-adequacy",
            "finding_id": "w9",
        },
        # a probe iteration index and a door row are not review rounds
        {
            "record_kind": "finding",
            "arc_id": "d",
            "round_n": 0,
            "producer": "reviewer_concurrency_probe",
            "finding_id": "p1",
        },
        {
            "record_kind": "finding",
            "arc_id": "d",
            "round_n": 4,
            "producer": "reviewer_concurrency_probe",
            "finding_id": "p2",
        },
        {
            "record_kind": "finding",
            "finding_type": "HITL-recoverable",
            "arc_id": "d",
            "round_n": None,
            "producer": "merge-door-post-merge-ci",
        },
    ]
    data = summarize(rows)
    assert data["rounds_per_arc_median"] == 4  # codex 1, 2, 3 (gemini failover of r3) + gate pass 1
    assert data["rounds_per_arc_max"] == 4
    assert data["codex_rows"] == 2


def test_codex_rows_exclude_adjudications_the_absorber_wrote() -> None:
    rows = _rows()
    rows.append(
        {
            "record_kind": "finding_adjudication",
            "arc_id": "a",
            "round_n": 1,
            "finding_id": "c1",
            "producer": "codex_review_wrapper",
            "disposition": "accepted",
            "disposition_actor": "claude_absorber",
            "ts": "2026-09-03T12:00:00Z",
        }
    )
    assert summarize(rows)["codex_rows"] == 1


def test_single_lens_round_and_clean_only_arc() -> None:
    rows = [
        {
            "record_kind": "finding",
            "arc_id": "b",
            "round_n": 1,
            "producer": "merge-gate-witness-adequacy",
            "finding_id": "w2",
            "unique_catch": False,
        },
        {
            "record_kind": "finding",
            "arc_id": "b",
            "round_n": 1,
            "producer": "codex_review_wrapper",
            "finding_id": "c2",
            "unique_catch": False,
        },
        {
            "record_kind": "no_finding",
            "arc_id": "c",
            "round_n": 1,
            "producer": "merge-gate-concurrency",
        },
        {
            "record_kind": "reviewer_unavailable",
            "arc_id": "c",
            "round_n": 2,
            "producer": "codex_review_wrapper",
        },
    ]
    data = summarize(rows)
    assert data["arcs"] == 2  # the clean-only arc c counts
    assert data["rounds_per_arc_median"] == 2  # b: codex r1 + gate pass 1; c: gate pass 1 + codex r2
    assert data["gate_rounds_with_findings"] == 1
    assert data["single_lens_rounds"] == 1  # codex rows do not make a round multi-lens


def test_loop_status_counts_only_the_yield_cause(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    log.write_text(json.dumps(_rows()[0]) + "\n")
    status = tmp_path / "loop_status.md"
    status.write_text(
        "| ts | kind | lane;cause | detail |\n|---|---|---|---|\n"
        f"| 2026-09-03T01:00:00Z | NOTIFY | lane=L;cause={YIELD} | holder=u-x backoff=0 |\n"
        "| 2026-09-03T02:00:00Z | NOTIFY | lane=L;cause=- | a .codex-worktrees/ lane is present |\n"
        f"| 2026-09-03T03:00:00Z | DEFERRED-HIL | lane=L;cause={YIELD} | not a NOTIFY row |\n"
        f"| 2026-09-03T04:00:00Z | NOTIFY | lane=L;cause={YIELD} | holder=u-y backoff=0 |\n"
    )
    data = _run(log, "--loop-status", str(status))
    assert data["lease_held_yields"] == 2


def test_empty_log_is_an_error(tmp_path: Path) -> None:
    log = tmp_path / "empty.jsonl"
    log.write_text("")
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--log", str(log)], capture_output=True, text=True
    )
    assert p.returncode == 2
    assert "no rows" in p.stderr

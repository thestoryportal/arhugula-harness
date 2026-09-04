"""Witness for tools/lanes_pilot.py — the C-HE-13 §1 pilot gate and §3 pilot report.

The fixture is the contract: a skip is not a pass (§1); the §3 iff-clause is a conjunction
of independently-witnessed clauses; and each clause's failure shape is pinned so a mutation
that makes one vacuous turns this file red.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lanes_pilot as lp
import lanes_verify as lv
import pytest

SCRIPT = Path(__file__).resolve().parent / "lanes_pilot.py"


def _row(contract: str = "C-HE-06", artifact: str = "pytest:x") -> lv.Row:
    return lv.Row(contract, artifact, "phase0", "local", True)


def _arc(arc_id: str, **over) -> dict:
    """A landed pilot arc. `lane_id` defaults to a per-arc lane, because C-HE-13 §3 pilots
    run at 3–4 DISTINCT lanes and a shared-lane fixture would hide that clause."""
    arc = {
        "arc_id": arc_id,
        "state": "merged",
        "lane_id": f"L-{arc_id}",
        "merge_sha": "a" * 40,
        "reserved_at": "2026-09-04T01:00:00Z",
        "transitioned_at": "2026-09-04T02:00:00Z",
    }
    arc.update(over)
    return arc


def _pilot_arcs(n: int = 3) -> list[dict]:
    return [_arc(f"u-{i}") for i in range(1, n + 1)]


def _stores(arcs: list[dict], **over) -> lp.Stores:
    base = {
        "arcs": arcs,
        "gate_rows": [],
        "loop_rows": [],
        "merged_ledger_arc_ids": [a["arc_id"] for a in arcs],
        "queued_arc_ids": set(),
    }
    base.update(over)
    return lp.Stores(**base)


def _loop_row(
    kind: str, cause: str, detail: str, *, lane: str = "L-u-1", ts: str = "2026-09-04T01:30:00Z"
) -> dict:
    return {"ts": ts, "kind": kind, "lane": lane, "cause": cause, "detail": detail}


# ── C-HE-13 §1: the gate ──────────────────────────────────────────────────────


GREEN = ("GREEN", "probe result recorded")


def test_pilot_runner_refuses_on_any_phase0_red() -> None:
    rc, msg = lp.gate([lv.Result(_row("C-HE-06", "pytest:x"), "fail", "boom")], probe=GREEN)
    assert rc != 0 and "C-HE-06" in msg and "pytest:x" in msg and "boom" in msg


def test_a_skip_is_not_a_pass() -> None:
    """C-HE-13 §1 names this explicitly: skip-marked rows count as NOT passed."""
    rc, msg = lp.gate(
        [lv.Result(_row(), "pass"), lv.Result(_row("C-HE-09", "shell:y"), "skip", "no docker")],
        probe=GREEN,
    )
    assert rc != 0 and "C-HE-09" in msg and "skip" in msg


def test_a_live_row_is_not_a_pass_either() -> None:
    rc, _ = lp.gate(
        [lv.Result(_row("C-HE-13", "just:lanes-pilot-report <run-id>"), "live", "")], probe=GREEN
    )
    assert rc != 0


def test_all_pass_is_green() -> None:
    rc, msg = lp.gate(
        [lv.Result(_row(), "pass"), lv.Result(_row("C-HE-09", "shell:y"), "pass")], probe=GREEN
    )
    assert rc == 0 and "GREEN" in msg and "2 rows" in msg


def test_a_red_reviewer_concurrency_probe_refuses_the_pilot() -> None:
    """C-HE-13 §2 orders the reviewer-concurrency probe BEFORE pilots, and
    `just pilot-gate-check` is its mechanical form. Running only the phase0 half would
    admit a pilot behind an absent or RED probe result."""
    rc, msg = lp.gate([lv.Result(_row(), "pass")], probe=("RED", "no result row"))
    assert rc != 0 and "C-HE-22" in msg and "RED" in msg


def test_a_green_gate_names_both_halves() -> None:
    rc, msg = lp.gate([lv.Result(_row(), "pass")], probe=GREEN)
    assert rc == 0 and "phase0 GREEN" in msg and "probe-result GREEN" in msg


def test_gate_reduces_through_phase0_verdict(monkeypatch) -> None:
    """The gate owns no pass/fail rule of its own: it is `lanes_verify.phase0_verdict`."""
    monkeypatch.setattr(lv, "phase0_verdict", lambda results: 0)
    rc, _ = lp.gate([lv.Result(_row(), "fail", "boom")], probe=GREEN)
    assert rc == 0


# ── §3 clause (a): landed THROUGH THE DOOR, first-parent clean ────────────────


def test_iff_clause_passes_on_a_clean_pilot() -> None:
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs()))
    assert rep["pass"] is True
    assert rep["friction"] == [] and rep["arcs"] == ["u-1", "u-2", "u-3"]


def test_an_unmerged_arc_fails() -> None:
    arcs = _pilot_arcs()
    arcs[1]["state"] = "open"
    rep = lp.evaluate("pilot-1", _stores(arcs))
    assert rep["pass"] is False
    assert any("is open, not merged" in v for v in rep["door_landing_violations"])


def test_merged_without_a_merge_sha_is_not_a_door_landing() -> None:
    """`reservations.reconcile()` flips an externally-merged PR to `merged` from `gh`
    ground truth WITHOUT setting `merge_sha` (C-HE-03 §5). §3 clause (a) requires the arc
    to land through the merge door, so state alone cannot satisfy it."""
    arcs = _pilot_arcs()
    arcs[0].pop("merge_sha")
    rep = lp.evaluate("pilot-1", _stores(arcs))
    assert rep["pass"] is False
    assert any("no door-recorded merge_sha" in v for v in rep["door_landing_violations"])


def test_toctou_from_the_doors_own_arc_id_shape_fails() -> None:
    """The merge door writes the arc's OWN id on its BASE_TOCTOU row. A report matching
    only the CI re-check's `merge-<sha12>` shape would read this as clean."""
    rows = [{"producer": "BASE_TOCTOU", "arc_id": "u-1"}]
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), gate_rows=rows))
    assert rep["pass"] is False and rep["base_toctou"] == 1


def test_toctou_from_the_ci_recheck_shape_also_fails() -> None:
    """`codex_context_guard.check_base_toctou` writes `merge-<sha12>` instead."""
    rows = [{"producer": "BASE_TOCTOU", "arc_id": "merge-" + "a" * 12}]
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), gate_rows=rows))
    assert rep["pass"] is False and rep["base_toctou"] == 1


def test_a_toctou_for_another_arc_never_counts() -> None:
    rows = [{"producer": "BASE_TOCTOU", "arc_id": "someone-else"}]
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), gate_rows=rows))
    assert rep["pass"] is True and rep["base_toctou"] == 0


# ── §3: a pilot is a run at 3–4 lanes ─────────────────────────────────────────


def test_a_two_lane_run_is_not_a_pilot() -> None:
    """C-HE-13 §3 defines pilots as runs at 3–4 lanes. A shared-lane or short run must not
    count toward the >= 3 pilots that gate follow-on orchestration."""
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(2)))
    assert rep["pass"] is False
    assert any("2 distinct lane(s)" in v for v in rep["lane_violations"])


def test_two_arcs_on_one_lane_is_one_lane() -> None:
    arcs = [_arc("u-1", lane_id="L1"), _arc("u-2", lane_id="L1"), _arc("u-3", lane_id="L1")]
    rep = lp.evaluate("pilot-1", _stores(arcs))
    assert rep["pass"] is False and rep["lanes"] == ["L1"]


def test_four_lanes_is_still_a_pilot() -> None:
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(4)))
    assert rep["pass"] is True and rep["lane_violations"] == []


def test_five_lanes_is_outside_the_defined_range() -> None:
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(5)))
    assert rep["pass"] is False and rep["lane_violations"]


# ── §3 clause (b): the union-ledger invariants ────────────────────────────────


def test_duplicate_merged_ledger_rows_fail_c_he_03() -> None:
    arcs = _pilot_arcs()
    ids = [a["arc_id"] for a in arcs] + ["u-1"]
    rep = lp.evaluate("pilot-1", _stores(arcs, merged_ledger_arc_ids=ids))
    assert rep["pass"] is False
    assert any(
        "C-HE-03" in v and "2 union-ledger rows" in v for v in rep["ledger_invariant_violations"]
    )


def test_a_duplicate_non_pilot_arc_id_also_violates_c_he_03() -> None:
    """The duplicate rule is a property of the UNION LEDGER, not of the pilot's own rows.
    Scoping the scan to pilot arcs would let the report claim the union ledger is sound
    while holding proof that it is not."""
    arcs = _pilot_arcs()
    ids = [a["arc_id"] for a in arcs] + ["old-arc", "old-arc"]
    rep = lp.evaluate("pilot-1", _stores(arcs, merged_ledger_arc_ids=ids))
    assert rep["pass"] is False
    assert any("old-arc has 2 union-ledger rows" in v for v in rep["ledger_invariant_violations"])


def test_queued_and_committed_at_once_fails_c_he_04() -> None:
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), queued_arc_ids={"u-1"}))
    assert rep["pass"] is False
    assert any("C-HE-04" in v and "BOTH" in v for v in rep["ledger_invariant_violations"])


def test_neither_queued_nor_committed_fails_c_he_04() -> None:
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), merged_ledger_arc_ids=[]))
    assert rep["pass"] is False
    assert any("neither" in v for v in rep["ledger_invariant_violations"])


def test_a_held_drain_is_the_invariants_first_branch_not_a_violation() -> None:
    """An arc still queued whose row is not yet on merged history is legal (C-HE-04's
    branch (a)). The workspace drain has held since u-he-34, so treating this as a
    violation would fail every pilot for a pre-existing reason."""
    arcs = _pilot_arcs()
    rep = lp.evaluate(
        "pilot-1",
        _stores(arcs, queued_arc_ids={"u-1"}, merged_ledger_arc_ids=["u-2", "u-3"]),
    )
    assert rep["ledger_invariant_violations"] == []
    assert rep["rows_not_yet_folded"] == ["u-1"] and rep["pass"] is True


# ── §3 clause (c): coordination HIL ───────────────────────────────────────────


def test_a_coordination_hil_fails_even_after_it_is_resolved() -> None:
    """C-HE-13 §3 is "no HITL escalation CARRIES a `merge-door-`/`reservation-`
    signature", not "none remains outstanding". A pilot that needed operator recovery
    still hit coordination pain, which is the signal §3 collects."""
    deferred = _loop_row(
        "DEFERRED-HIL", "merge-door-lease-acquire:HITL-recoverable:x", "u-1 — door blocked"
    )
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[deferred]))
    assert rep["pass"] is False and len(rep["coordination_hil"]) == 1
    assert rep["coordination_hil_still_outstanding"] == 1

    resolved = _loop_row(
        "RESOLVED-HIL", "merge-door-lease-acquire:HITL-recoverable:x", "u-1 — cleared"
    )
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[deferred, resolved]))
    assert rep["pass"] is False, "a resolved coordination escalation still occurred"
    assert len(rep["coordination_hil"]) == 1
    assert rep["coordination_hil_still_outstanding"] == 0


def test_a_hil_raised_after_the_merged_flip_still_counts() -> None:
    """The door holds its lease past the `merged` flip, so its post-merge escalations are
    stamped AFTER `transitioned_at`. Scoping by a [reserved_at, transitioned_at] window
    would drop exactly the coordination failures §3 exists to catch."""
    late = _loop_row(
        "DEFERRED-HIL",
        "merge-door-post-merge:HITL-recoverable:base_toctou",
        "u-1 — merge landed on another base",
        ts="2026-09-04T09:00:00Z",
    )
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[late]))
    assert rep["pass"] is False and len(rep["coordination_hil"]) == 1


def test_a_non_coordination_hil_never_fails_the_pilot() -> None:
    """An environmental cause must not be recorded under the coordination prefixes, so a
    branch-hygiene deferral leaves the pilot green while still showing as friction."""
    row = _loop_row("DEFERRED-HIL", "branch-hygiene", "u-1 — branch hygiene close-out pending")
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[row]))
    assert rep["pass"] is True and rep["friction"] == ["branch-hygiene"]


def test_another_arcs_hil_never_counts() -> None:
    row = _loop_row(
        "DEFERRED-HIL", "merge-door-lease-acquire:x", "other-arc — not this pilot", lane="L9"
    )
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[row]))
    assert rep["pass"] is True and rep["coordination_hil"] == []


def test_friction_keeps_an_arcless_post_merge_row_inside_the_pilots_own_span() -> None:
    """The door's post-merge escalations ARE arc-attributed, so they extend the window's
    close; an arcless row alongside them (the lease-yield NOTIFY carries no arc id) is
    therefore captured. Bounding at `transitioned_at` would drop both, undercounting the
    organic-pain bar."""
    attributed = _loop_row(
        "DEFERRED-HIL",
        "merge-door-post-merge:HITL-recoverable:ci",
        "u-1 — post-merge run red",
        ts="2026-09-04T23:30:00Z",
    )
    arcless = _loop_row(
        "NOTIFY",
        "merge-door-lease-acquire:lease_held_yield",
        "holder=u-9 backoff=0",
        ts="2026-09-04T23:00:00Z",
    )
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[arcless, attributed]))
    assert "merge-door-lease-acquire:lease_held_yield" in rep["friction"]
    assert "merge-door-post-merge:HITL-recoverable:ci" in rep["friction"]


def test_friction_excludes_a_later_arcs_causes_on_the_same_lane() -> None:
    """Unbounded above, a persistent lane's LATER arcs would add their causes to this
    pilot's deduplicated set, which can falsely satisfy the recurring bar that authorises
    follow-on orchestration. The window closes at the pilot's own last arc-attributed
    activity, so a later unrelated arc does not extend it."""
    later = _loop_row(
        "NOTIFY", "some-later-arc-cause", "holder=x backoff=0", ts="2027-01-01T00:00:00Z"
    )
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[later]))
    assert rep["friction"] == []


def test_friction_ignores_a_row_predating_the_pilot() -> None:
    row = _loop_row("NOTIFY", "old-cause", "holder=x backoff=0", ts="2020-01-01T00:00:00Z")
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[row]))
    assert rep["friction"] == []


# ── §3 recurring definition ───────────────────────────────────────────────────


def test_recurring_definition() -> None:
    assert lp.recurring({"p1": {"a:x:y"}, "p2": {"a:x:y"}, "p3": set()}, severe=set()) == {"a:x:y"}
    assert lp.recurring({"p1": {"b:x:y"}, "p2": set(), "p3": set()}, severe={"b:x:y"}) == {"b:x:y"}
    assert lp.recurring({"p1": {"c"}, "p2": set(), "p3": set()}, severe=set()) == set()


# ── CLI contract: 0 PASS, 1 measured FAIL, 2 unanswerable ─────────────────────


def test_report_refuses_when_no_arc_carries_the_run_id(monkeypatch) -> None:
    """An unknown run id is unanswerable, not a FAIL: a FAIL here would be an
    answer-shaped void the operator could not tell from a real pilot failure."""
    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: [])
    with pytest.raises(lp.PilotError, match="no reservation carries"):
        lp.report("ghost")


def test_the_merged_ledger_read_preserves_byte_identical_duplicates(monkeypatch) -> None:
    """The C-HE-03 invariant forbids a second row for one arc_id, so the reader must not
    deduplicate: `arc_metrics._committed_ledger_lines()` returns a SET and would collapse a
    byte-identical duplicate, making the violation undetectable through the real path."""
    import arc_metrics as am

    row = '{"arc_id": "u-1"}'
    monkeypatch.setattr(am, "run", lambda *a, **k: f"{row}\n{row}\n")
    assert lp._merged_ledger_arc_ids() == ["u-1", "u-1"]


def test_the_merged_ledger_read_refuses_when_unreadable(monkeypatch) -> None:
    import arc_metrics as am

    def boom(*a, **k):
        raise am.AbortError("no such ref")

    monkeypatch.setattr(am, "run", boom)
    with pytest.raises(lp.PilotError, match="unreadable"):
        lp._merged_ledger_arc_ids()


def test_report_refuses_when_merged_history_is_unreadable(monkeypatch) -> None:
    """`arc_metrics.committed_arc_ids()` collapses "unreadable" into an empty set because
    holding a capture is the safe default for the DRAIN. Here the same empty set would
    make every arc look like the legal queued-and-not-folded branch and print PASS, so the
    tri-state reader's None must refuse."""
    import merge_door as md

    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: _pilot_arcs())
    monkeypatch.setattr(lp, "_loop_rows", lambda: [])
    monkeypatch.setattr(md, "read_lease", lambda: None)
    monkeypatch.setattr(lp, "_merged_ledger_arc_ids", _raise_unreadable)
    with pytest.raises(lp.PilotError, match="unreadable"):
        lp.report("pilot-1")


def _raise_unreadable() -> list[str]:
    raise lp.PilotError("merged history is unreadable")


def test_report_refuses_while_the_door_still_holds_a_lease(monkeypatch) -> None:
    """The reservation flips to `merged` with its `merge_sha` at door step (vi); the door
    THEN runs first-parent detection, post-merge CI and the refresh while holding the
    lease. A report inside that window could print PASS moments before a BASE_TOCTOU or CI
    escalation is written, so it is unanswerable rather than a verdict."""
    import merge_door as md

    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: _pilot_arcs())
    monkeypatch.setattr(md, "read_lease", lambda: {"reservation_id": "u-2"})
    with pytest.raises(lp.PilotError, match="still holds a lease"):
        lp.report("pilot-1")


def test_report_refuses_when_the_gate_log_is_absent(monkeypatch, tmp_path) -> None:
    """Class-sibling of the tri-state read: `finding_record.read_rows()` returns [] for an
    absent gate log, which would make the BASE_TOCTOU half of clause (a) read clean when
    the detections could not be looked at at all."""
    import finding_record as fr
    import merge_door as md

    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: _pilot_arcs())
    monkeypatch.setattr(lp, "_loop_rows", lambda: [])
    monkeypatch.setattr(md, "read_lease", lambda: None)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "absent.jsonl")
    with pytest.raises(lp.PilotError, match="gate log"):
        lp.report("pilot-1")


def test_cli_maps_an_unreadable_store_to_exit_2_not_the_fail_code(monkeypatch) -> None:
    """Exit 1 is the documented measured-FAIL code, so an unreadable store must not
    arrive as one — a traceback would exit 1 and read as a failed pilot."""

    def boom(run_id):
        raise OSError("store gone")

    monkeypatch.setattr(lp, "_pilot_arcs", boom)
    assert lp.main(["report", "pilot-1"]) == 2


def test_cli_report_exits_2_on_an_unanswerable_run(monkeypatch) -> None:
    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: [])
    assert lp.main(["report", "ghost"]) == 2


def test_cli_needs_a_run_id() -> None:
    assert lp.main(["report"]) == 2
    assert lp.main(["start"]) == 2


def test_cli_start_prints_the_recipe(capsys) -> None:
    assert lp.main(["start", "pilot-7"]) == 0
    out = capsys.readouterr().out
    assert "pilot_run_id=pilot-7" in out and "lanes-pilot-report pilot-7" in out


def test_script_runs_as_a_module() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "start", "pilot-1"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0 and "Phase 0 GREEN" in proc.stdout

"""Witness for tools/lanes_pilot.py — the C-HE-13 §1 pilot gate and §3 pilot report.

The fixture is the contract: a skip is not a pass (§1); the §3 iff-clause is a conjunction
of four independently-witnessed clauses; and each clause's failure shape is pinned so a
mutation that makes one vacuous turns this file red.
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
    arc = {
        "arc_id": arc_id,
        "state": "merged",
        "lane_id": "L1",
        "merge_sha": "a" * 40,
        "reserved_at": "2026-09-04T01:00:00Z",
        "transitioned_at": "2026-09-04T02:00:00Z",
    }
    arc.update(over)
    return arc


def _stores(arcs: list[dict], **over) -> lp.Stores:
    base = {
        "arcs": arcs,
        "gate_rows": [],
        "loop_rows": [],
        "ledger_arc_ids": [a["arc_id"] for a in arcs],
        "committed_arc_ids": {a["arc_id"] for a in arcs},
        "queued_arc_ids": set(),
    }
    base.update(over)
    return lp.Stores(**base)


def _loop_row(
    kind: str, cause: str, detail: str, *, lane: str = "L1", ts: str = "2026-09-04T01:30:00Z"
) -> dict:
    return {"ts": ts, "kind": kind, "lane": lane, "cause": cause, "detail": detail}


# ── C-HE-13 §1: the gate ──────────────────────────────────────────────────────


def test_pilot_runner_refuses_on_any_phase0_red() -> None:
    rc, msg = lp.gate([lv.Result(_row("C-HE-06", "pytest:x"), "fail", "boom")])
    assert rc != 0 and "C-HE-06" in msg and "pytest:x" in msg and "boom" in msg


def test_a_skip_is_not_a_pass() -> None:
    """C-HE-13 §1 names this explicitly: skip-marked rows count as NOT passed."""
    rc, msg = lp.gate(
        [lv.Result(_row(), "pass"), lv.Result(_row("C-HE-09", "shell:y"), "skip", "no docker")]
    )
    assert rc != 0 and "C-HE-09" in msg and "skip" in msg


def test_a_live_row_is_not_a_pass_either() -> None:
    """`run_row` returns `live` for a placeholder artifact; only `pass` passes."""
    rc, _ = lp.gate([lv.Result(_row("C-HE-13", "just:lanes-pilot-report <run-id>"), "live", "")])
    assert rc != 0


def test_all_pass_is_green() -> None:
    rc, msg = lp.gate([lv.Result(_row(), "pass"), lv.Result(_row("C-HE-09", "shell:y"), "pass")])
    assert rc == 0 and "GREEN" in msg and "2 rows" in msg


def test_gate_reduces_through_phase0_verdict(monkeypatch) -> None:
    """The gate owns no pass/fail rule of its own: it is `lanes_verify.phase0_verdict`.
    Redefining that reduction must change the gate's verdict, or there are two
    authorities on what "phase0 green" means."""
    monkeypatch.setattr(lv, "phase0_verdict", lambda results: 0)
    rc, _ = lp.gate([lv.Result(_row(), "fail", "boom")])
    assert rc == 0


# ── C-HE-13 §3 clause (a): merged + first-parent clean ────────────────────────


def test_iff_clause_passes_on_a_clean_pilot() -> None:
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1"), _arc("u-2")]))
    assert rep["pass"] is True
    assert rep["friction"] == [] and rep["arcs"] == ["u-1", "u-2"]


def test_an_unmerged_arc_fails() -> None:
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1"), _arc("u-2", state="open")]))
    assert rep["pass"] is False and rep["all_merged"] is False


def test_toctou_from_the_doors_own_arc_id_shape_fails() -> None:
    """The merge door writes the arc's OWN id on its BASE_TOCTOU row
    (`merge_door._emit_gate(gate="BASE_TOCTOU", arc_id=arc_id)`). A report that only
    matched the CI re-check's `merge-<sha12>` shape would read this as clean."""
    rows = [{"producer": "BASE_TOCTOU", "arc_id": "u-1"}]
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], gate_rows=rows))
    assert rep["pass"] is False and rep["base_toctou"] == 1


def test_toctou_from_the_ci_recheck_shape_also_fails() -> None:
    """`codex_context_guard.check_base_toctou` writes `merge-<sha12>` instead."""
    rows = [{"producer": "BASE_TOCTOU", "arc_id": "merge-" + "a" * 12}]
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], gate_rows=rows))
    assert rep["pass"] is False and rep["base_toctou"] == 1


def test_a_toctou_for_another_arc_never_counts() -> None:
    rows = [{"producer": "BASE_TOCTOU", "arc_id": "someone-else"}]
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], gate_rows=rows))
    assert rep["pass"] is True and rep["base_toctou"] == 0


# ── C-HE-13 §3 clause (b): the union-ledger invariants ────────────────────────


def test_duplicate_union_ledger_rows_fail_c_he_03() -> None:
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], ledger_arc_ids=["u-1", "u-1"]))
    assert rep["pass"] is False
    assert any(
        "C-HE-03" in v and "2 union-ledger rows" in v for v in rep["ledger_invariant_violations"]
    )


def test_queued_and_committed_at_once_fails_c_he_04() -> None:
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], queued_arc_ids={"u-1"}))
    assert rep["pass"] is False
    assert any("C-HE-04" in v and "BOTH" in v for v in rep["ledger_invariant_violations"])


def test_neither_queued_nor_committed_fails_c_he_04() -> None:
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], committed_arc_ids=set(), ledger_arc_ids=[]))
    assert rep["pass"] is False
    assert any("neither" in v for v in rep["ledger_invariant_violations"])


def test_a_held_drain_is_the_invariants_first_branch_not_a_violation() -> None:
    """An arc still queued whose row is not yet committed is legal (C-HE-04's branch (a)).
    The drain has been held workspace-wide since u-he-34, so treating this as a violation
    would fail every pilot for a pre-existing reason."""
    rep = lp.evaluate(
        "pilot-1",
        _stores([_arc("u-1")], queued_arc_ids={"u-1"}, committed_arc_ids=set(), ledger_arc_ids=[]),
    )
    assert rep["ledger_invariant_violations"] == []
    assert rep["rows_not_yet_folded"] == ["u-1"] and rep["pass"] is True


# ── C-HE-13 §3 clause (c): coordination HIL ───────────────────────────────────


def test_a_coordination_hil_fails_and_a_resolve_clears_it() -> None:
    deferred = _loop_row(
        "DEFERRED-HIL", "merge-door-lease-acquire:HITL-recoverable:x", "u-1 — door blocked"
    )
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], loop_rows=[deferred]))
    assert rep["pass"] is False and len(rep["coordination_hil"]) == 1

    resolved = _loop_row(
        "RESOLVED-HIL", "merge-door-lease-acquire:HITL-recoverable:x", "u-1 — cleared"
    )
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], loop_rows=[deferred, resolved]))
    assert rep["pass"] is True and rep["coordination_hil"] == []


def test_a_hil_raised_after_the_merged_flip_still_counts() -> None:
    """The door holds its lease past the `merged` flip, so its post-merge escalations are
    stamped AFTER `transitioned_at`. Scoping by a [reserved_at, transitioned_at] window
    would drop exactly the coordination failures §3 exists to catch."""
    late = _loop_row(
        "DEFERRED-HIL",
        "merge-door-post-merge:HITL-recoverable:base_toctou",
        "u-1 — merge landed on another base",
        ts="2026-09-04T09:00:00Z",  # well after the arc's transitioned_at
    )
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], loop_rows=[late]))
    assert rep["pass"] is False and len(rep["coordination_hil"]) == 1


def test_a_non_coordination_hil_never_fails_the_pilot() -> None:
    """An environmental cause must not be recorded under the coordination prefixes, so a
    branch-hygiene deferral leaves the pilot green while still showing as friction."""
    row = _loop_row("DEFERRED-HIL", "branch-hygiene", "u-1 — branch hygiene close-out pending")
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], loop_rows=[row]))
    assert rep["pass"] is True and rep["friction"] == ["branch-hygiene"]


def test_another_lanes_hil_never_counts() -> None:
    row = _loop_row(
        "DEFERRED-HIL", "merge-door-lease-acquire:x", "other-arc — not this pilot", lane="L9"
    )
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], loop_rows=[row]))
    assert rep["pass"] is True and rep["coordination_hil"] == []


def test_friction_includes_an_arcless_row_from_a_pilot_lane_in_window() -> None:
    """The lease-yield NOTIFY carries no arc id in its detail; arc attribution alone would
    drop it. Friction is a reporting field, so the wider scope never moves the verdict."""
    row = _loop_row("NOTIFY", "merge-door-lease-acquire:lease_held_yield", "holder=u-9 backoff=0")
    rep = lp.evaluate("pilot-1", _stores([_arc("u-1")], loop_rows=[row]))
    assert rep["friction"] == ["merge-door-lease-acquire:lease_held_yield"]
    assert rep["pass"] is True  # a NOTIFY is not an escalation


# ── §3 recurring definition ───────────────────────────────────────────────────


def test_recurring_definition() -> None:
    assert lp.recurring({"p1": {"a:x:y"}, "p2": {"a:x:y"}, "p3": set()}, severe=set()) == {"a:x:y"}
    assert lp.recurring({"p1": {"b:x:y"}, "p2": set(), "p3": set()}, severe={"b:x:y"}) == {"b:x:y"}
    assert lp.recurring({"p1": {"c"}, "p2": set(), "p3": set()}, severe=set()) == set()


# ── CLI contract ──────────────────────────────────────────────────────────────


def test_report_refuses_when_no_arc_carries_the_run_id(monkeypatch) -> None:
    """An unknown run id is unanswerable, not a FAIL: a FAIL verdict here would be an
    answer-shaped void the operator could not tell from a real pilot failure."""
    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: [])
    with pytest.raises(lp.PilotError, match="no reservation carries"):
        lp.report("ghost")


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

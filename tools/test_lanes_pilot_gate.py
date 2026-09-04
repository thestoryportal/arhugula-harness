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


class _Proc:
    """A `subprocess.run` result standing in for the ledger-path resolution."""

    def __init__(self, stdout: str, returncode: int = 0, stderr: str = "") -> None:
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


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


def test_queued_and_committed_is_the_sweep_window_not_a_violation() -> None:
    """`arc_metrics._drain_one` unlinks a queue entry only once the row is ALREADY in
    committed history, on a LATER drain pass — so "queued and committed" is the normal
    self-healing window, not a C-HE-04 breach. C-HE-04's exclusive-or is stated *after a
    drain invocation*, not as a globally-true property, and with the workspace drain held
    this window is the steady state. Failing on it would cry wolf on every pilot."""
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), queued_arc_ids={"u-1"}))
    assert rep["ledger_invariant_violations"] == []
    assert rep["rows_awaiting_queue_sweep"] == ["u-1"]
    assert rep["pass"] is True


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


def test_friction_ignores_bookkeeping_row_kinds() -> None:
    """A RESOLVED-HIL carries the cause_signature of the item it SETTLES, so counting it
    would let the delivery of a pre-pilot deferral read as new pilot friction."""
    row = _loop_row("RESOLVED-HIL", "merge-door-lease-acquire:x", "u-1 — cleared")
    rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[row]))
    assert rep["friction"] == []


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


def test_the_recurring_bar_needs_at_least_three_pilots() -> None:
    """§3 defines the bar over >= 3 pilots; two is not a smaller sample of it, and
    returning a signature from two would authorise follow-on orchestration on evidence
    the contract does not accept."""
    with pytest.raises(ValueError, match=">= 3 pilots"):
        lp.recurring({"p1": {"a"}, "p2": {"a"}}, severe=set())


def test_a_severe_signature_must_actually_have_occurred() -> None:
    """`severe` rates an OCCURRENCE severe, so a signature that appeared in no pilot
    cannot be one; passing it through would invent friction evidence."""
    with pytest.raises(ValueError, match="never occurred"):
        lp.recurring({"p1": set(), "p2": set(), "p3": set()}, severe={"never-seen"})


def test_the_pilot_recipe_runs_the_gate_before_start() -> None:
    """The recipe body is the production wiring: `gate()` unit tests stay green even if
    `just lanes-pilot` is reduced to `lanes_pilot.py start`, which would admit a pilot
    with no gate at all (codex r4 P2). Pin the chain itself."""
    body = (Path(__file__).resolve().parent.parent / "justfile").read_text()
    recipe = body.split("\nlanes-pilot run_id:", 1)[1].split("\n\n", 1)[0]
    assert "lanes_pilot.py gate" in recipe
    assert "lanes_pilot.py start {{run_id}}" in recipe
    assert recipe.index("gate") < recipe.index("start"), "the gate must precede start"
    assert "&&" in recipe, "start must be conditional on the gate's exit code"


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


def test_cli_gate_dispatch_runs_the_real_phase0_seam(monkeypatch, capsys) -> None:
    """`just lanes-pilot` invokes `lanes_pilot.py gate` FIRST, and that CLI branch is the
    wiring that makes the recipe refuse. Every other gate test calls `gate()` directly with
    a hand-built result list, so hardcoding this branch to `return 0` — or dropping the
    `phase0_results()` call — would leave them all green (merge-gate witness lens)."""
    called = {"n": 0}

    def fake_phase0():
        called["n"] += 1
        return [lv.Result(_row("C-HE-06", "pytest:x"), "fail", "boom")]

    monkeypatch.setattr(lp, "phase0_results", fake_phase0)
    monkeypatch.setattr(lv, "probe_result_verdict", lambda: GREEN)
    rc = lp.main(["gate"])
    assert rc != 0, "a RED phase0 row must make the CLI exit non-zero"
    assert called["n"] == 1, "the CLI must consult the real phase0 seam"
    assert "phase0 RED" in capsys.readouterr().out


def test_cli_gate_dispatch_consults_the_real_probe_seam(monkeypatch, capsys) -> None:
    """The §2 half of the same wiring: `gate()`'s `probe is not None else
    lv.probe_result_verdict()` else-branch is the ONLY path the CLI takes, and every direct
    `gate()` test passes `probe=` explicitly. Without a counter here, hardcoding that branch
    to a literal `("GREEN", "stub")` — the same bug shape witnessed for `phase0_results` —
    would leave the whole suite green (merge-gate witness lens, second pass)."""
    seen = {"n": 0}

    def fake_probe():
        seen["n"] += 1
        return GREEN

    monkeypatch.setattr(lp, "phase0_results", lambda: [lv.Result(_row(), "pass")])
    monkeypatch.setattr(lv, "probe_result_verdict", fake_probe)
    assert lp.main(["gate"]) == 0
    assert seen["n"] == 1, "the CLI must consult the real probe-result seam"
    assert "GREEN" in capsys.readouterr().out


def test_cli_gate_dispatch_refuses_on_a_red_probe(monkeypatch, capsys) -> None:
    """Phase 0 green and the C-HE-22 probe RED must still refuse, through the CLI path."""
    monkeypatch.setattr(lp, "phase0_results", lambda: [lv.Result(_row(), "pass")])
    monkeypatch.setattr(lv, "probe_result_verdict", lambda: ("RED", "no result row"))
    assert lp.main(["gate"]) != 0
    assert "C-HE-22" in capsys.readouterr().out


def test_loop_rows_raises_on_a_malformed_data_row(monkeypatch, tmp_path) -> None:
    """`_loop_rows`'s malformed-pipe-row branch is the [LAW:no-silent-failure] arm: a
    truncated DEFERRED-HIL still carries its coordination cause, so dropping it would report
    "no escalation occurred". Exercised directly, not through a monkeypatched stand-in."""
    ledger = tmp_path / "loop_status.md"
    ledger.write_text(
        "| ts | kind | lane;cause | detail |\n|---|---|---|---|\n"
        "| 2026-09-04T01:00:00Z | DEFERRED-HIL | lane=L1;cause=merge-door-x |\n"
    )
    monkeypatch.setattr(lp.subprocess, "run", lambda *a, **k: _Proc(str(ledger)))
    with pytest.raises(lp.PilotError, match="unreadable ledger row"):
        lp._loop_rows()


def test_loop_rows_reads_well_formed_rows(monkeypatch, tmp_path) -> None:
    ledger = tmp_path / "loop_status.md"
    ledger.write_text(
        "| ts | kind | lane;cause | detail |\n|---|---|---|---|\n"
        "| 2026-09-04T01:00:00Z | NOTIFY | lane=L1;cause=c | u-1 — detail |\n"
    )
    monkeypatch.setattr(lp.subprocess, "run", lambda *a, **k: _Proc(str(ledger)))
    rows = lp._loop_rows()
    assert len(rows) == 1 and rows[0]["cause"] == "c" and rows[0]["lane"] == "L1"


def test_loop_rows_refuses_when_the_ledger_path_cannot_be_resolved(monkeypatch) -> None:
    monkeypatch.setattr(
        lp.subprocess, "run", lambda *a, **k: _Proc("", returncode=1, stderr="no venue")
    )
    with pytest.raises(lp.PilotError, match="could not resolve"):
        lp._loop_rows()


def test_pilot_arcs_refuses_a_store_path_that_is_not_a_directory(monkeypatch, tmp_path) -> None:
    """A containment breach must never read as an empty store."""
    import reservations as rs

    planted = tmp_path / "reservations"
    planted.write_text("not a directory")
    monkeypatch.setattr(rs, "reservations_root", lambda: planted)
    with pytest.raises(lp.PilotError, match="not a directory"):
        lp._pilot_arcs("pilot-1")


def test_pilot_arcs_selects_only_reservations_carrying_this_run_id(monkeypatch, tmp_path) -> None:
    """The SELECTION LOOP itself, not just its guard clauses: a real reservations root is
    walked, dotfiles and plain files are skipped, and only records whose `pilot_run_id`
    matches are returned. Dropping the run-id filter — an unconditional append — would
    otherwise leave every report's arcs, lanes and verdict silently wrong while the suite
    stayed green (merge-gate witness lens, third pass)."""
    import reservations as rs

    root = tmp_path / "reservations"
    for name in ("u-1", "u-2", ".hidden"):
        (root / name).mkdir(parents=True)
    (root / "stray.json").write_text("{}")
    payloads = {
        "u-1": _arc("u-1", pilot_run_id="pilot-1"),
        "u-2": _arc("u-2", pilot_run_id="another-pilot"),
        ".hidden": _arc("hidden", pilot_run_id="pilot-1"),
    }
    monkeypatch.setattr(rs, "reservations_root", lambda: root)
    monkeypatch.setattr(rs, "current", lambda arc_id: (1, payloads[arc_id]))

    got = lp._pilot_arcs("pilot-1")
    assert [a["arc_id"] for a in got] == ["u-1"], "only this run id's reservations"


def test_pilot_arcs_skips_a_reservation_with_no_run_id(monkeypatch, tmp_path) -> None:
    import reservations as rs

    root = tmp_path / "reservations"
    (root / "u-9").mkdir(parents=True)
    monkeypatch.setattr(rs, "reservations_root", lambda: root)
    monkeypatch.setattr(rs, "current", lambda arc_id: (1, _arc("u-9")))
    assert lp._pilot_arcs("pilot-1") == []


def test_merged_ledger_read_refuses_an_unparseable_row(monkeypatch) -> None:
    """A malformed merged-history row is unreadable evidence; silently skipping it would
    under-count the C-HE-03 duplicate check."""
    import arc_metrics as am

    monkeypatch.setattr(am, "run", lambda *a, **k: '{"arc_id": "u-1"}\nnot json\n')
    with pytest.raises(lp.PilotError, match="unparseable row"):
        lp._merged_ledger_arc_ids()


def test_pilot_arcs_returns_empty_for_an_absent_store(monkeypatch, tmp_path) -> None:
    import reservations as rs

    monkeypatch.setattr(rs, "reservations_root", lambda: tmp_path / "absent")
    assert lp._pilot_arcs("pilot-1") == []


def _wire_report(monkeypatch, tmp_path, arcs, *, merged, queued_names, gate_rows=(), loop_rows=()):
    """Wire report()'s four store seams to real on-disk content, leaving the queued-arc
    loop, the Stores assembly and evaluate() to run for real."""
    import arc_metrics as am
    import finding_record as fr
    import merge_door as md

    queue = tmp_path / "queue"
    queue.mkdir()
    for name in queued_names:
        (queue / name).write_text("{}")
    gate_log = tmp_path / "gate-log.jsonl"
    gate_log.write_text("")
    monkeypatch.setattr(lp, "_pilot_arcs", lambda run_id: arcs)
    # NON-EMPTY on purpose: stubbing these to `[]` returns exactly what a mutation
    # hardcoding `Stores(gate_rows=[], loop_rows=[])` produces, so the seams would be
    # indistinguishable and clause (a)'s BASE_TOCTOU check and clause (c)'s
    # coordination-HIL check could go permanently vacuous with the suite green.
    monkeypatch.setattr(lp, "_loop_rows", lambda: list(loop_rows))
    monkeypatch.setattr(lp, "_merged_ledger_arc_ids", lambda: list(merged))
    monkeypatch.setattr(md, "read_lease", lambda: None)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", gate_log)
    monkeypatch.setattr(fr, "read_rows", lambda: list(gate_rows))
    monkeypatch.setattr(am, "QUEUE_DIR", queue)


def test_report_success_path_returns_a_real_pass(monkeypatch, tmp_path) -> None:
    """report()'s SUCCESS path — every other report test raises before reaching
    `Stores(...)`/`evaluate(...)`, so the queued-arc-id loop, the Stores assembly and the
    verdict were all unwitnessed. Both queue-entry filename shapes are exercised here:
    `<arc>.json` (free) and `<arc>.taken` (claimed mid-drain)."""
    arcs = _pilot_arcs()
    _wire_report(
        monkeypatch,
        tmp_path,
        arcs,
        merged=["u-3"],
        queued_names=["u-1.json", "u-2.taken"],
        gate_rows=[{"producer": "BASE_TOCTOU", "arc_id": "someone-else"}],
        loop_rows=[_loop_row("NOTIFY", "env-cause", "unattributed", lane="L-u-1")],
    )
    rep = lp.report("pilot-1")
    assert rep["friction"] == ["env-cause"], "the loop ledger must reach the report"
    assert rep["pass"] is True
    assert rep["arcs"] == ["u-1", "u-2", "u-3"]
    assert rep["rows_not_yet_folded"] == ["u-1", "u-2"], "both queue shapes recognised"
    assert rep["ledger_invariant_violations"] == []


def test_report_reads_the_gate_log_for_base_toctou(monkeypatch, tmp_path) -> None:
    """A BASE_TOCTOU row naming a PILOT arc must fail through the real `report()` path —
    the witness that `gate_rows=fr.read_rows()` is genuinely consulted, not hardcoded."""
    _wire_report(
        monkeypatch,
        tmp_path,
        _pilot_arcs(),
        merged=["u-1", "u-2", "u-3"],
        queued_names=[],
        gate_rows=[{"producer": "BASE_TOCTOU", "arc_id": "u-2"}],
    )
    rep = lp.report("pilot-1")
    assert rep["base_toctou"] == 1 and rep["pass"] is False


def test_report_reads_the_loop_ledger_for_coordination_hil(monkeypatch, tmp_path) -> None:
    """Clause (c) through the real `report()` path, for the same reason."""
    _wire_report(
        monkeypatch,
        tmp_path,
        _pilot_arcs(),
        merged=["u-1", "u-2", "u-3"],
        queued_names=[],
        loop_rows=[_loop_row("DEFERRED-HIL", "merge-door-lease-acquire:x", "u-1 — blocked")],
    )
    rep = lp.report("pilot-1")
    assert len(rep["coordination_hil"]) == 1 and rep["pass"] is False


def test_cli_report_exits_0_on_pass_and_1_on_fail(monkeypatch, tmp_path, capsys) -> None:
    """main()'s PASS/FAIL exit mapping: inverting the ternary must not stay green."""
    arcs = _pilot_arcs()
    _wire_report(
        monkeypatch, tmp_path, arcs, merged=["u-3"], queued_names=["u-1.json", "u-2.taken"]
    )
    assert lp.main(["report", "pilot-1"]) == 0
    assert "PILOT PASS" in capsys.readouterr().out

    arcs[0]["state"] = "open"  # a lane that never landed
    assert lp.main(["report", "pilot-1"]) == 1
    assert "PILOT FAIL" in capsys.readouterr().out


def test_phase0_results_runs_the_real_manifest_rows(monkeypatch) -> None:
    """Its body is otherwise never executed: collapsing it to `return []` would make the
    real CLI gate vacuously GREEN, since phase0_verdict([]) is 0."""
    row = _row("C-HE-06", "pytest:x")
    seen = []

    def fake_run_row(r):
        seen.append(r.artifact)
        return lv.Result(r, "fail", "ran for real")

    monkeypatch.setattr(lv, "phase0_rows", lambda: [row])
    monkeypatch.setattr(lv, "run_row", fake_run_row)
    got = lp.phase0_results()
    # The stub records the call and returns a status a bypass would not invent, so a
    # mutation skipping run_row and hardcoding a passing Result is distinguishable.
    assert seen == ["pytest:x"], "each manifest row must be run for real"
    assert [(r.row.contract, r.status, r.reason) for r in got] == [
        ("C-HE-06", "fail", "ran for real")
    ]


def test_loop_rows_refuses_an_empty_ledger_path(monkeypatch) -> None:
    """The `or not path` disjunct: a zero exit with empty stdout is still unresolvable."""
    monkeypatch.setattr(lp.subprocess, "run", lambda *a, **k: _Proc("", returncode=0))
    with pytest.raises(lp.PilotError, match="could not resolve"):
        lp._loop_rows()


def test_loop_rows_refuses_a_ledger_path_that_does_not_exist(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(lp.subprocess, "run", lambda *a, **k: _Proc(str(tmp_path / "gone.md")))
    with pytest.raises(lp.PilotError, match="does not exist"):
        lp._loop_rows()


def test_merged_ledger_read_is_empty_for_a_ledger_outside_the_repo(monkeypatch, tmp_path) -> None:
    """A ledger outside the repo has no committed history at all — a KNOWN empty, which is
    why it returns [] rather than refusing like the unreadable case."""
    import arc_metrics as am

    monkeypatch.setattr(am, "LEDGER", tmp_path / "elsewhere.jsonl")
    assert lp._merged_ledger_arc_ids() == []


def test_friction_ignores_a_row_with_no_cause() -> None:
    for empty in ("-", ""):
        row = _loop_row("NOTIFY", empty, "u-1 — placeholder cause")
        rep = lp.evaluate("pilot-1", _stores(_pilot_arcs(), loop_rows=[row]))
        assert rep["friction"] == [], f"cause={empty!r} must not register as friction"


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

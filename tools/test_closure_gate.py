from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import closure_gate


def _green_delegates(monkeypatch) -> None:
    monkeypatch.setattr(
        closure_gate,
        "_arc_snapshot",
        lambda: {
            "standalone_registered": 0,
            "standalone_gated": 0,
            "frozen_done": 11,
            "frozen_total": 11,
        },
    )
    monkeypatch.setattr(
        closure_gate,
        "_overlay_orphans",
        lambda: {
            "contract_without_code": [{"id": "C-IS-11"}],
            "unit_without_code": [{"id": "U-RT-00"}],
            "cxa_seam_missing_endpoint": [],
        },
    )
    monkeypatch.setattr(closure_gate, "_run", lambda *args: (0, "ok"))
    monkeypatch.setattr(closure_gate, "_roadmap_status", lambda rid: "BLOCKED")


def test_tier1_manual_signoff_records_gates_as_passed(tmp_path, monkeypatch) -> None:
    _green_delegates(monkeypatch)
    signoff = tmp_path / "r-fs-1-tier1-manual-signoff.json"
    signoff.write_text(
        json.dumps(
            {
                "gates": {
                    "G1.4": {"status": "signed", "evidence": "unit advisory reviewed"},
                    "G1.7": {"status": "signed", "evidence": "fork scan reviewed"},
                    "G1.8": {"status": "signed", "evidence": "residual scan reviewed"},
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(closure_gate, "TIER1_MANUAL_SIGNOFF", signoff)

    preds = {pred.pid: pred for pred in closure_gate.evaluate()}

    assert preds["G1.4"].state is True
    assert preds["G1.4"].detail == "unit advisory reviewed"
    assert preds["G1.7"].state is True
    assert preds["G1.8"].state is True


def test_tier1_manual_signoff_missing_gate_stays_open(tmp_path, monkeypatch) -> None:
    _green_delegates(monkeypatch)
    signoff = tmp_path / "r-fs-1-tier1-manual-signoff.json"
    signoff.write_text(
        json.dumps(
            {
                "gates": {
                    "G1.4": {"status": "signed", "evidence": "unit advisory reviewed"},
                    "G1.7": {"status": "signed", "evidence": "fork scan reviewed"},
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(closure_gate, "TIER1_MANUAL_SIGNOFF", signoff)

    preds = {pred.pid: pred for pred in closure_gate.evaluate()}

    assert preds["G1.4"].state is True
    assert preds["G1.7"].state is True
    assert preds["G1.8"].state is None
    assert "sign-off missing" in preds["G1.8"].detail


def test_tier1_manual_signoff_non_object_json_stays_open(tmp_path, monkeypatch) -> None:
    _green_delegates(monkeypatch)
    signoff = tmp_path / "r-fs-1-tier1-manual-signoff.json"
    signoff.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(closure_gate, "TIER1_MANUAL_SIGNOFF", signoff)

    preds = {pred.pid: pred for pred in closure_gate.evaluate()}

    assert preds["G1.4"].state is None
    assert "root object missing" in preds["G1.4"].detail


def test_automatable_and_tier2_predicates_evaluate_from_mocked_delegates(
    tmp_path, monkeypatch
) -> None:
    """B-28 finding #19 (test-quality preflight 2026-07-12) — `_green_delegates`
    mocks `_run`/`_roadmap_status`/`_arc_snapshot`/`_overlay_orphans` for
    every test in this file, but every existing test asserts only the
    manual-signoff predicates (G1.4/G1.7/G1.8); the 5 automatable Tier-1
    predicates and all 6 Tier-2 predicates were never asserted on."""
    _green_delegates(monkeypatch)
    signoff = tmp_path / "r-fs-1-tier1-manual-signoff.json"
    signoff.write_text(json.dumps({"gates": {}}), encoding="utf-8")
    monkeypatch.setattr(closure_gate, "TIER1_MANUAL_SIGNOFF", signoff)

    preds = {pred.pid: pred for pred in closure_gate.evaluate()}

    # Tier 1 automatable — all green per _green_delegates' mocked values:
    # standalone_registered=0/standalone_gated=0 (G1.1), _run always (0, "ok")
    # (G1.2/G1.6), contract_without_code=[C-IS-11] which is a DOCUMENTED_NON_CONTRACT
    # so 0 real orphans remain (G1.3), cxa_seam_missing_endpoint=[] (G1.5).
    assert preds["G1.1"].state is True
    assert preds["G1.2"].state is True
    assert preds["G1.3"].state is True
    assert preds["G1.5"].state is True
    assert preds["G1.6"].state is True

    # Tier 2 — _roadmap_status is mocked to always return "BLOCKED", so every
    # G2.N predicate (state = status == "RESOLVED") must be False.
    for pid in ("G2.1", "G2.2", "G2.3", "G2.4", "G2.5", "G2.6"):
        assert preds[pid].state is False

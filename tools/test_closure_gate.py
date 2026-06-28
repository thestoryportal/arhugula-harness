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

"""U-HE-35 hermetic suite: the C-HE-22 pass rule on synthetic samples, the arc-id-stripped
child env, exit-code -> validity mapping, and `run`'s row emission — no live reviewer, no
tracked gate log ([LAW:behavior-not-structure] every test asserts the probe's contract:
verdict, reason class, rows written)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import reviewer_concurrency_probe as rcp


@pytest.fixture(autouse=True)
def _hermetic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Nothing here may reach a real reviewer or the tracked gate log."""
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate-log.jsonl")
    monkeypatch.setenv("HARNESS_GATE_LOG", str(tmp_path / "gate-log.jsonl"))
    monkeypatch.setattr(
        rcp.subprocess,
        "run",
        lambda *a, **k: pytest.fail(f"real reviewer subprocess: {a[0][:4]}"),
    )


def _series(count: int, wall: float, ok: bool = True) -> list[tuple[float, bool]]:
    return [(wall, ok)] * count


# ── decide: the C-HE-22 pass rule (plan S6 step 1) ───────────────────────────


def test_decide_green():
    ok, why = rcp.decide({1: _series(5, 60), 2: _series(5, 100), 4: _series(5, 110)})
    assert ok
    assert "no throttling signal" in why


# mutation-probe: commenting out decide()'s wall-clock rule (base median -> bound) reds this
def test_decide_red_wallclock():
    # 130 > 2 x 60: the N=4 median breaches the doubling bound
    ok, why = rcp.decide({1: _series(5, 60), 2: _series(5, 100), 4: _series(5, 130)})
    assert not ok
    assert "wall-clock" in why


def test_decide_red_validity():
    samples = {1: _series(5, 60), 2: [*_series(4, 100), (100.0, False)], 4: _series(5, 110)}
    ok, why = rcp.decide(samples)
    assert not ok
    assert "validity" in why


def test_decide_red_insufficient():
    ok, why = rcp.decide({1: _series(5, 60), 2: _series(4, 100), 4: _series(5, 110)})
    assert not ok
    assert "insufficient" in why


def test_decide_red_no_baseline():
    # Wall-clock GREEN is RELATIVE to the N=1 median; without it there is no rule to apply
    ok, why = rcp.decide({2: _series(5, 100), 4: _series(5, 110)})
    assert not ok
    assert "insufficient" in why


def test_decide_validity_outranks_wallclock():
    # Both violations present -> the validity reason (zero-failures is the harder rule)
    ok, why = rcp.decide({1: _series(5, 60, ok=False), 4: _series(5, 130)})
    assert not ok
    assert "validity" in why


# ── probe_env: the B-215 posture is set in ONE place ─────────────────────────


def test_probe_env_strips_arc_and_lane_ids(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HARNESS_ARC_ID", "u-he-35")
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-x")
    monkeypatch.setenv("HARNESS_GATE_LOG", "/tmp/keep-me")
    env = rcp.probe_env()
    assert "HARNESS_ARC_ID" not in env
    assert "HARNESS_LANE_ID" not in env
    # only the two reservation-joining ids are stripped; the rest of the env passes through
    assert env["HARNESS_GATE_LOG"] == "/tmp/keep-me"


# ── _one: exit code -> validity mapping (C-HE-15: 0/1 = parsed verdict) ──────


@pytest.mark.parametrize(("rc", "valid"), [(0, True), (1, True), (2, False), (3, False)])
def test_one_exit_code_validity(monkeypatch: pytest.MonkeyPatch, rc: int, valid: bool):
    monkeypatch.setattr(
        rcp.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], rc, "", ""),
    )
    wall, ok = rcp._one("codex", "main", {})
    assert ok is valid
    assert wall >= 0


def test_one_timeout_is_invalid_sample(monkeypatch: pytest.MonkeyPatch):
    def _boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd=a[0], timeout=k["timeout"])

    monkeypatch.setattr(rcp.subprocess, "run", _boom)
    _wall, ok = rcp._one("codex", "main", {})
    assert ok is False  # a hung reviewer is a validity-failure SAMPLE, not a probe crash


# ── run: emission + verdict wiring ───────────────────────────────────────────


@pytest.fixture()
def _fixed_binding(monkeypatch: pytest.MonkeyPatch):
    head = "a" * 40
    monkeypatch.setattr(
        rcp.rw,
        "code_binding",
        lambda repo, base: {"head_sha": head, "base_sha": "b" * 40, "diff_digest": "c" * 64},
    )
    monkeypatch.setenv("HARNESS_ARC_ID", "u-he-35")
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-x")
    return head


def test_run_green_emits_one_row_per_call(tmp_path: Path, _fixed_binding: str, capsys):
    calls: list[dict[str, str]] = []

    def fake_one(channel: str, base: str, env: dict[str, str]) -> tuple[float, bool]:
        calls.append(env)
        return 60.0, True

    rc = rcp.run("main", channel="codex", reps=5, ns=(1, 2), one=fake_one)
    assert rc == 0
    out = capsys.readouterr().out
    assert "GREEN" in out and "N=1" in out and "N=2" in out
    # one C-HE-24 row per call: 5x1 + 5x2
    rows = fr.read_rows()
    assert len(calls) == len(rows) == 15
    assert {r["producer"] for r in rows} == {rcp.PRODUCER}
    assert {r["finding_type"] for r in rows} == {"probe-sample"}
    assert {r["arc_id"] for r in rows} == {"u-he-35"}
    assert {r["head_sha"] for r in rows} == {_fixed_binding}
    evidence = json.loads(rows[0]["observed_evidence"])
    assert evidence == {"wall_s": 60.0, "valid": True, "n": 1, "rep": 0}
    # the child env never carries the reservation-joining ids (B-215 stays Inactive)
    assert all("HARNESS_ARC_ID" not in env for env in calls)


def test_run_red_exit_and_rows_still_recorded(tmp_path: Path, _fixed_binding: str, capsys):
    rc = rcp.run("main", channel="codex", reps=5, ns=(1,), one=lambda c, b, e: (60.0, False))
    assert rc == 1
    assert "RED" in capsys.readouterr().out
    # invalid samples are still evidence: every call has its row
    assert len(fr.read_rows()) == 5

"""U-HE-35 hermetic suite: the C-HE-22 pass rule on synthetic samples, the arc-id-stripped
child env, per-channel machine-seam validity, and `run`'s row emission — no live reviewer,
no tracked gate log ([LAW:behavior-not-structure] every test asserts the probe's contract:
verdict, reason class, rows written)."""

from __future__ import annotations

import json
import subprocess
import sys
import threading
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
        "Popen",
        lambda *a, **k: pytest.fail(f"real reviewer subprocess: {a[0][:4]}"),
    )


class FakePopen:
    """A completed reviewer child: `communicate` returns the canned streams."""

    def __init__(self, argv, stderr_text: str = "", on_spawn=None, **kwargs):
        self.pid = 4242
        self.argv = argv
        self.kwargs = kwargs
        self._stderr = stderr_text
        if on_spawn is not None:
            on_spawn(argv)

    def communicate(self, timeout=None):
        return "", self._stderr


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
    ok, why = rcp.decide({1: _series(5, 60, ok=False), 2: _series(5, 100), 4: _series(5, 130)})
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


# ── _one: validity comes from the channel's machine seam, never the exit code ─


@pytest.mark.parametrize(
    ("stderr", "valid"),
    [
        ("codex-review: APPROVE\n", True),
        ("- [P1] tools/x.py:1: msg\ncodex-review: BLOCK\n", True),
        ("codex-review: BLOCK [source: log]\n", True),
        ("codex-review: REVIEWER_UNAVAILABLE (transient: rate limit)\n", False),
        ("codex-review: GATE_REFUSED (NO_PREFLIGHT)\n", False),
        ("Traceback (most recent call last):\n  boom\n", False),
        ("", False),
    ],
)
def test_one_codex_validity_is_the_terminal_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stderr: str, valid: bool
):
    # no exit code is consulted at all: an uncaught wrapper exception also exits 1,
    # so only the stderr completion line is the verdict (codex r1 P1)
    spawned: list[FakePopen] = []

    def fake_popen(argv, **k):
        p = FakePopen(argv, stderr_text=stderr, **k)
        spawned.append(p)
        return p

    monkeypatch.setattr(rcp.subprocess, "Popen", fake_popen)
    wall, ok = rcp._one("codex", "main", {}, tmp_path)
    assert ok is valid
    assert wall >= 0
    # own process group, so a timeout can kill the whole reviewer tree (codex r4 P2)
    assert spawned[0].kwargs["start_new_session"] is True


def test_one_gemini_validity_is_the_outcome_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    def write_envelope(terminal: str):
        def on_spawn(argv):
            sink = Path(argv[argv.index("--outcome-json") + 1])
            sink.write_text(json.dumps({"terminal": terminal}))

        return lambda argv, **k: FakePopen(argv, on_spawn=on_spawn, **k)

    monkeypatch.setattr(rcp.subprocess, "Popen", write_envelope("APPROVE"))
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path)
    assert ok is True
    # no envelope written (wrapper crashed / refused the sink) -> invalid
    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: FakePopen(argv, **k))
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path)
    assert ok is False
    # an envelope whose terminal is not a verdict -> invalid
    monkeypatch.setattr(rcp.subprocess, "Popen", write_envelope("REVIEWER_UNAVAILABLE"))
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path)
    assert ok is False


def test_one_timeout_kills_process_group_and_is_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """A timed-out reviewer must not keep running into later concurrency levels
    (codex r4 P2): the whole process group is killed, and the call reads invalid."""
    killed: list[tuple[int, int]] = []

    class TimeoutPopen(FakePopen):
        def communicate(self, timeout=None):
            if timeout is not None:
                raise subprocess.TimeoutExpired(cmd="codex-review", timeout=timeout)
            return "", ""  # the post-kill reap

    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: TimeoutPopen(argv, **k))
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    _wall, ok = rcp._one("codex", "main", {}, tmp_path)
    assert ok is False  # a hung reviewer is a validity-failure SAMPLE, not a probe crash
    assert killed == [(4242, rcp.signal.SIGKILL)]  # the TREE died, not just the launcher


def test_reps_cli_boundary_refuses_nonpositive():
    with pytest.raises(SystemExit):  # argparse rejects at the checkpoint, pre-run
        rcp.main(["--reps", "0"])
    with pytest.raises(SystemExit):
        rcp.main(["--reps", "-3"])


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

    def fake_one(channel: str, base: str, env: dict[str, str], scratch: Path) -> tuple[float, bool]:
        calls.append(env)
        return 60.0, True

    rc = rcp.run("main", channel="codex", reps=5, ns=(1, 2, 4), one=fake_one)
    assert rc == 0
    out = capsys.readouterr().out
    assert "GREEN" in out and "N=1" in out and "N=2" in out and "N=4" in out
    # one C-HE-24 row per call (5x1 + 5x2 + 5x4) plus ONE durable terminal result row
    rows = fr.read_rows()
    sample_rows = [r for r in rows if r["finding_type"] == "probe-sample"]
    result_rows = [r for r in rows if r["finding_type"] == "probe-result"]
    assert len(calls) == len(sample_rows) == 35
    assert {r["producer"] for r in rows} == {rcp.PRODUCER}
    assert {r["arc_id"] for r in rows} == {"u-he-35"}
    assert {r["head_sha"] for r in rows} == {_fixed_binding}
    evidence = json.loads(sample_rows[0]["observed_evidence"])
    assert evidence == {"wall_s": 60.0, "valid": True, "n": 1, "rep": 0}
    # the terminal record is what "result row required before pilots" can enforce
    # (codex r4 P2): exactly one, carrying the verdict
    assert len(result_rows) == 1
    result = json.loads(result_rows[0]["observed_evidence"])
    assert result["verdict"] == "GREEN"
    assert result["counts"] == {"1": 5, "2": 10, "4": 20}
    # the child env never carries the reservation-joining ids (B-215 stays Inactive)
    assert all("HARNESS_ARC_ID" not in env for env in calls)


def test_run_red_exit_and_rows_still_recorded(tmp_path: Path, _fixed_binding: str, capsys):
    # the FULL required series, so this RED depends on the invalid samples alone
    # (codex r5 P3: with ns=(1,) the missing-series rule fired first and the validity
    # propagation had no witness)
    rc = rcp.run(
        "main", channel="codex", reps=5, ns=(1, 2, 4), one=lambda c, b, e, s: (60.0, False)
    )
    assert rc == 1
    out = capsys.readouterr().out
    assert "RED" in out and "validity" in out
    # invalid samples are still evidence: every call has its row, plus the RED result row
    rows = fr.read_rows()
    assert len([r for r in rows if r["finding_type"] == "probe-sample"]) == 35
    [result] = [r for r in rows if r["finding_type"] == "probe-result"]
    assert json.loads(result["observed_evidence"])["verdict"] == "RED"


@pytest.mark.parametrize(
    ("start", "end"),
    [
        # a moved HEAD
        (("a" * 40, "c" * 40, "d" * 64), ("b" * 40, "c" * 40, "d" * 64)),
        # a moved base ref under an UNMOVED HEAD (codex r2 P2): different merge-base,
        # different reviewed bytes — head_sha alone would miss it
        (("a" * 40, "c" * 40, "d" * 64), ("a" * 40, "e" * 40, "f" * 64)),
    ],
)
def test_run_red_when_binding_drifts_mid_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
    start: tuple[str, str, str],
    end: tuple[str, str, str],
):
    """Any changed binding component voids the one-fixed-diff premise: GREEN arithmetic
    must not survive it, and the drifted batch's rows must never be recorded (codex r3
    P2: a later RED cannot repair a durable false measurement record)."""

    def make(t: tuple[str, str, str]) -> dict[str, str]:
        return {"head_sha": t[0], "base_sha": t[1], "diff_digest": t[2]}

    # initial capture -> batch-1 gate (drifted) -> the report's end re-read
    bindings = iter([make(start), make(end), make(end)])
    # (the result-row append reads no binding: it reuses the initial capture)
    monkeypatch.setattr(rcp.rw, "code_binding", lambda repo, base: next(bindings))
    monkeypatch.setenv("HARNESS_ARC_ID", "u-he-35")
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-x")
    calls: list[int] = []

    def fake_one(c, b, e, s):
        calls.append(1)
        return 60.0, True

    rc = rcp.run("main", channel="codex", reps=5, ns=(1, 2), one=fake_one)
    assert rc == 1
    assert "fixed-diff violated" in capsys.readouterr().out
    rows = fr.read_rows()
    # the drifted batch persisted NO sample row; the RED terminal record still lands
    assert [r["finding_type"] for r in rows] == ["probe-result"]
    assert json.loads(rows[0]["observed_evidence"])["verdict"] == "RED"
    assert len(calls) == 1  # sampling aborted at the first drifted batch — no further spend


def test_one_spawn_oserror_is_invalid_sample(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def _spawn_fail(*a, **k):
        raise OSError("Resource temporarily unavailable")

    monkeypatch.setattr(rcp.subprocess, "Popen", _spawn_fail)
    _wall, ok = rcp._one("codex", "main", {}, tmp_path)
    assert ok is False  # a failed spawn under load is a validity-failure SAMPLE


def test_run_batch_calls_actually_overlap(tmp_path: Path, _fixed_binding: str, capsys):
    """The probe's whole point is N OVERLAPPING calls: a serialized executor would
    deadlock this barrier (BrokenBarrierError after the timeout), so a green run is a
    witness that both calls in every N=2 batch were in flight simultaneously."""
    barrier = threading.Barrier(2)

    def overlapping_one(c, b, e, s):
        barrier.wait(timeout=10)
        return 60.0, True

    rc = rcp.run("main", channel="codex", reps=5, ns=(2,), one=overlapping_one)
    assert rc == 1  # N=2 alone misses required series -> RED insufficient; overlap still proven
    assert "insufficient" in capsys.readouterr().out
    assert len([r for r in fr.read_rows() if r["finding_type"] == "probe-sample"]) == 10


# ── LIVE_GROUPS: no orphaned reviewer trees on termination (codex r5 P2) ─────


def test_live_groups_kill_all_kills_registered_pgids(monkeypatch: pytest.MonkeyPatch):
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    groups = rcp._LiveGroups()
    groups.add(111)
    groups.add(222)
    groups.discard(222)  # a completed call deregisters — only live groups die
    groups.kill_all()
    assert killed == [(111, rcp.signal.SIGKILL)]
    groups.kill_all()  # idempotent: the set was drained
    assert killed == [(111, rcp.signal.SIGKILL)]


def test_one_registers_and_deregisters_its_group(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    seen: list[set[int]] = []

    class SnoopPopen(FakePopen):
        def communicate(self, timeout=None):
            seen.append(set(rcp.LIVE_GROUPS._pgids))  # live DURING the call
            return "", "codex-review: APPROVE\n"

    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: SnoopPopen(argv, **k))
    _wall, ok = rcp._one("codex", "main", {}, tmp_path)
    assert ok is True
    assert seen == [{4242}]  # registered while running...
    assert 4242 not in rcp.LIVE_GROUPS._pgids  # ...deregistered after


def test_run_restores_signal_handlers(tmp_path: Path, _fixed_binding: str, capsys):
    import signal as _signal

    before = (_signal.getsignal(_signal.SIGTERM), _signal.getsignal(_signal.SIGINT))
    rcp.run("main", channel="codex", reps=5, ns=(1, 2, 4), one=lambda c, b, e, s: (60.0, True))
    after = (_signal.getsignal(_signal.SIGTERM), _signal.getsignal(_signal.SIGINT))
    assert after == before  # the probe's handlers never outlive the run


def test_add_refused_once_terminating(monkeypatch: pytest.MonkeyPatch):
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    groups = rcp._LiveGroups()
    groups.add(111)
    groups.begin_termination()
    assert killed == [(111, rcp.signal.SIGKILL)]  # the snapshot died
    assert groups.add(333) is False  # ...and no later registration is accepted
    groups.reset()
    assert groups.add(444) is True  # re-armed for the next run


def test_one_skips_spawn_once_terminating(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # the autouse fixture makes any real spawn a failure, so reaching the return
    # WITHOUT tripping it proves no reviewer was spawned after termination began
    monkeypatch.setattr(rcp, "LIVE_GROUPS", rcp._LiveGroups())
    rcp.LIVE_GROUPS.begin_termination()
    wall, ok = rcp._one("codex", "main", {}, tmp_path)
    assert (wall, ok) == (0.0, False)


def test_one_kills_own_group_when_registration_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """The Popen->add window (codex r6 P2): termination beginning mid-spawn means the
    handler's snapshot cannot see this group — the worker must kill it itself."""
    monkeypatch.setattr(rcp, "LIVE_GROUPS", rcp._LiveGroups())
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))

    def spawn_then_terminate(argv, **k):
        p = FakePopen(argv, stderr_text="codex-review: APPROVE\n", **k)
        rcp.LIVE_GROUPS.begin_termination()  # the signal lands between Popen and add
        return p

    monkeypatch.setattr(rcp.subprocess, "Popen", spawn_then_terminate)
    _wall, ok = rcp._one("codex", "main", {}, tmp_path)
    assert ok is False  # a call whose group was killed at registration is not a verdict
    assert killed == [(4242, rcp.signal.SIGKILL)]  # the just-spawned group died

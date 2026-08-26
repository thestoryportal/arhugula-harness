"""U-HE-35 hermetic suite: the C-HE-22 pass rule on synthetic samples, the arc-id-stripped
child env, per-channel machine-seam validity, and `run`'s row emission — no live reviewer,
no tracked gate log ([LAW:behavior-not-structure] every test asserts the probe's contract:
verdict, reason class, rows written)."""

from __future__ import annotations

import contextlib
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
    monkeypatch.setattr(
        rcp.subprocess,
        "run",
        lambda *a, **k: pytest.fail(f"real subprocess.run: {a[0][:4]}"),
    )


class FakePopen:
    """A reviewer child: alive (`poll()` None) until `communicate` reaps it."""

    def __init__(self, argv, stderr_text: str = "", on_spawn=None, **kwargs):
        self.pid = 4242
        self.argv = argv
        self.kwargs = kwargs
        self._stderr = stderr_text
        self._returncode = None
        if on_spawn is not None:
            on_spawn(argv)

    def poll(self):
        return self._returncode

    def communicate(self, timeout=None):
        self._returncode = 0
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


# mutation-probe: commenting out decide()'s required-series loop must red this (N=1 alone
def test_decide_red_n1_alone_never_certifies():
    """merge-gate witness P2: five valid N=1 samples ALONE must read RED (the codex r4
    P3 regression shape — a check narrowed back to `if 1 not in samples` passes only
    if no test supplies N=1 present with N=2/N=4 absent; this test is that shape)."""
    ok, why = rcp.decide({1: _series(5, 60)})
    assert not ok
    assert "insufficient" in why and "N=2" in why


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
    wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
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
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path, tmp_path)
    assert ok is True
    # no envelope written (wrapper crashed / refused the sink) -> invalid
    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: FakePopen(argv, **k))
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path, tmp_path)
    assert ok is False
    # an envelope whose terminal is not a verdict -> invalid
    monkeypatch.setattr(rcp.subprocess, "Popen", write_envelope("REVIEWER_UNAVAILABLE"))
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path, tmp_path)
    assert ok is False

    # a syntactically valid but wrong-SHAPED body (codex r7 P3): `null` has no
    # ["terminal"] to subscript — invalid sample, never an escaping TypeError
    def write_null(argv, **k):
        def on_spawn(a):
            Path(a[a.index("--outcome-json") + 1]).write_text("null")

        return FakePopen(argv, on_spawn=on_spawn, **k)

    monkeypatch.setattr(rcp.subprocess, "Popen", write_null)
    _wall, ok = rcp._one("gemini", "main", {}, tmp_path, tmp_path)
    assert ok is False


def test_one_timeout_cooperative_term_is_invalid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A timed-out reviewer is TERMed first (codex r8 P2: the wrapper's own termination
    path is the only holder of the nested vendor group id) and the call reads invalid."""
    killed: list[tuple[int, int]] = []

    class TimeoutPopen(FakePopen):
        def communicate(self, timeout=None):
            if timeout == rcp.CALL_TIMEOUT_S:  # the bounded wait expires...
                raise subprocess.TimeoutExpired(cmd="codex-review", timeout=timeout)
            self._returncode = -15  # ...and the wrapper obeys the TERM within the grace
            return "", ""

    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: TimeoutPopen(argv, **k))
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    _wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
    assert ok is False  # a hung reviewer is a validity-failure SAMPLE, not a probe crash
    assert killed == [(4242, rcp.signal.SIGTERM)]  # cooperative — no blind SIGKILL


def test_one_timeout_escalates_to_kill_on_hung_wrapper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """A wrapper too hung to honor the TERM is SIGKILLed after the grace (codex r4/r8)."""
    killed: list[tuple[int, int]] = []

    class HungPopen(FakePopen):
        def communicate(self, timeout=None):
            if timeout is not None:  # BOTH the bounded wait and the TERM grace expire
                raise subprocess.TimeoutExpired(cmd="codex-review", timeout=timeout)
            self._returncode = -9  # the post-kill reap
            return "", ""

    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: HungPopen(argv, **k))
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    monkeypatch.setattr(rcp, "TERM_GRACE_S", 0.01)
    _wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
    assert ok is False
    assert killed == [(4242, rcp.signal.SIGTERM), (4242, rcp.signal.SIGKILL)]


def test_main_threads_argv_to_run(monkeypatch: pytest.MonkeyPatch):
    recorded = {}

    def fake_run(base, *, channel, reps, ns=(1, 2, 4), one=None):
        recorded.update(base=base, channel=channel, reps=reps)
        return 7

    monkeypatch.setattr(rcp, "run", fake_run)
    assert rcp.main(["--base", "dev", "--channel", "gemini", "--reps", "6"]) == 7
    assert recorded == {"base": "dev", "channel": "gemini", "reps": 6}


def test_reps_cli_boundary_refuses_nonpositive():
    with pytest.raises(SystemExit):  # argparse rejects at the checkpoint, pre-run
        rcp.main(["--reps", "0"])
    with pytest.raises(SystemExit):
        rcp.main(["--reps", "-3"])


# ── run: emission + verdict wiring ───────────────────────────────────────────


@pytest.fixture()
def _fixed_binding(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    head = "a" * 40
    monkeypatch.setattr(
        rcp.rw,
        "code_binding",
        lambda repo, base: {"head_sha": head, "base_sha": "b" * 40, "diff_digest": "c" * 64},
    )

    @contextlib.contextmanager
    def fake_pin(head_sha):
        workdir = tmp_path / "pinned"
        workdir.mkdir(exist_ok=True)
        yield workdir

    monkeypatch.setattr(rcp, "_pinned_worktree", fake_pin)
    monkeypatch.setenv("HARNESS_ARC_ID", "u-he-35")
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-x")
    return head


def test_run_green_emits_one_row_per_call(tmp_path: Path, _fixed_binding: str, capsys):
    calls: list[dict[str, str]] = []

    def fake_one(channel, base, env, scratch, workdir) -> tuple[float, bool]:
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
        "main", channel="codex", reps=5, ns=(1, 2, 4), one=lambda c, b, e, s, w: (60.0, False)
    )
    assert rc == 1
    out = capsys.readouterr().out
    assert "RED" in out and "validity" in out
    # invalid samples are still evidence: every call has its row, plus the RED result row
    rows = fr.read_rows()
    assert len([r for r in rows if r["finding_type"] == "probe-sample"]) == 35
    [result] = [r for r in rows if r["finding_type"] == "probe-result"]
    assert json.loads(result["observed_evidence"])["verdict"] == "RED"


def test_run_freezes_base_and_pins_workdir(tmp_path: Path, _fixed_binding: str, capsys):
    """The one-fixed-diff premise is structural (codex r7 P2): every child call gets the
    FROZEN base sha (never the mutable ref) and runs inside the pinned worktree, so no
    ref move — including an A->B->A wiggle — can change what any child reviews."""
    seen: list[tuple[str, Path]] = []

    def fake_one(channel, base, env, scratch, workdir):
        seen.append((base, workdir))
        return 60.0, True

    rc = rcp.run("main", channel="codex", reps=5, ns=(1, 2, 4), one=fake_one)
    assert rc == 0
    assert {b for b, _ in seen} == {"b" * 40}  # the captured base_sha, not "main"
    assert {w.name for _, w in seen} == {"pinned"}  # every call inside the pinned tree


def test_pinned_worktree_add_prewarm_remove(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """The pin's lifecycle: detached add at the exact sha, venv pre-warm OUTSIDE any
    measured call, forced remove on exit — remove failure warns loudly, never silently."""
    ran: list[list[str]] = []

    def fake_run(argv, **k):
        ran.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(rcp.subprocess, "run", fake_run)
    names = []
    with rcp._pinned_worktree("f" * 40) as workdir:
        names.append(workdir.name)
    with rcp._pinned_worktree("f" * 40) as workdir:
        names.append(workdir.name)
    # merge-gate concurrency P2: the basename rides the tempdir's unique suffix — a
    # fixed literal would race git's .git/worktrees/<id> collision-avoidance across
    # CONCURRENT probe processes in the shared repo
    assert names[0] != names[1] and all(n.startswith("pin-") for n in names)
    add, prewarm, remove = ran[:3]
    assert add[:5] == ["git", "-C", str(rcp.REPO), "worktree", "add"]
    assert "--detach" in add and add[-1] == "f" * 40
    assert prewarm[:2] == ["uv", "run"]
    assert remove[3:5] == ["worktree", "remove"] and "--force" in remove


def test_pin_failure_records_red_result_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    """merge-gate concurrency P2: a failed worktree add must not crash recordless —
    the run records a durable RED probe-result row (pilot-gate stays fail-closed)."""
    monkeypatch.setattr(
        rcp.rw,
        "code_binding",
        lambda repo, base: {"head_sha": "a" * 40, "base_sha": "b" * 40, "diff_digest": "c" * 64},
    )
    monkeypatch.setenv("HARNESS_ARC_ID", "u-he-35")
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-x")

    @contextlib.contextmanager
    def failing_pin(head_sha):
        raise rcp.PinError("git worktree add failed: fatal: collision")
        yield  # pragma: no cover

    monkeypatch.setattr(rcp, "_pinned_worktree", failing_pin)
    rc = rcp.run(
        "main", channel="codex", reps=5, ns=(1, 2, 4), one=lambda c, b, e, s, w: (60.0, True)
    )
    assert rc == 1
    assert "pinned worktree unavailable" in capsys.readouterr().out
    rows = fr.read_rows()
    assert [r["finding_type"] for r in rows] == ["probe-result"]  # no samples, ONE terminal row
    result = json.loads(rows[0]["observed_evidence"])
    assert result["verdict"] == "RED" and "worktree" in result["why"]


def test_pin_add_failure_raises_typed_after_prune(monkeypatch: pytest.MonkeyPatch):
    ran = []

    def fake_run(argv, **k):
        ran.append(list(argv))
        if "add" in argv:
            raise subprocess.CalledProcessError(128, argv, stderr="fatal: collision")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(rcp.subprocess, "run", fake_run)
    with pytest.raises(rcp.PinError, match="collision"):
        with rcp._pinned_worktree("f" * 40):
            pass  # pragma: no cover
    assert ran[-1][3:] == ["worktree", "prune"]  # partial admin state pruned best-effort


def test_pinned_worktree_remove_failure_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    def fake_run(argv, **k):
        rc = 1 if "remove" in argv else 0
        return subprocess.CompletedProcess(argv, rc, "", "locked")

    monkeypatch.setattr(rcp.subprocess, "run", fake_run)
    with rcp._pinned_worktree("f" * 40):
        pass
    assert "pinned worktree not removed" in capsys.readouterr().err


def test_one_spawn_oserror_is_invalid_sample(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def _spawn_fail(*a, **k):
        raise OSError("Resource temporarily unavailable")

    monkeypatch.setattr(rcp.subprocess, "Popen", _spawn_fail)
    _wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
    assert ok is False  # a failed spawn under load is a validity-failure SAMPLE


def test_run_batch_calls_actually_overlap(tmp_path: Path, _fixed_binding: str, capsys):
    """The probe's whole point is N OVERLAPPING calls: a serialized executor would
    deadlock this barrier (BrokenBarrierError after the timeout), so a green run is a
    witness that both calls in every N=2 batch were in flight simultaneously."""
    barrier = threading.Barrier(2)

    def overlapping_one(c, b, e, s, w):
        barrier.wait(timeout=10)
        return 60.0, True

    rc = rcp.run("main", channel="codex", reps=5, ns=(2,), one=overlapping_one)
    assert rc == 1  # N=2 alone misses required series -> RED insufficient; overlap still proven
    assert "insufficient" in capsys.readouterr().out
    assert len([r for r in fr.read_rows() if r["finding_type"] == "probe-sample"]) == 10


# ── LIVE_GROUPS: no orphaned reviewer trees on termination (codex r5 P2) ─────


def test_live_groups_kill_all_terms_cooperatively(monkeypatch: pytest.MonkeyPatch):
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    monkeypatch.setattr(rcp, "_group_alive", lambda pgid: False)  # wrapper obeyed the TERM
    groups = rcp._LiveGroups()
    groups.add(111)
    groups.add(222)
    groups.discard(222)  # a completed call deregisters — only live groups die
    groups.kill_all()
    # cooperative: TERM lets the wrapper tear down its NESTED vendor group (codex r8 P2)
    assert killed == [(111, rcp.signal.SIGTERM)]
    groups.kill_all()  # idempotent: the set was drained
    assert killed == [(111, rcp.signal.SIGTERM)]


def test_live_groups_kill_all_escalates_on_hung_wrapper(monkeypatch: pytest.MonkeyPatch):
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    monkeypatch.setattr(rcp, "_group_alive", lambda pgid: True)  # wrapper ignored the TERM
    monkeypatch.setattr(rcp, "TERM_GRACE_S", 0.01)
    groups = rcp._LiveGroups()
    groups.add(111)
    groups.kill_all()
    assert killed == [(111, rcp.signal.SIGTERM), (111, rcp.signal.SIGKILL)]


def test_one_registers_and_deregisters_its_group(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    seen: list[set[int]] = []

    class SnoopPopen(FakePopen):
        def communicate(self, timeout=None):
            seen.append(set(rcp.LIVE_GROUPS._pgids))  # live DURING the call
            self._returncode = 0
            return "", "codex-review: APPROVE\n"

    monkeypatch.setattr(rcp.subprocess, "Popen", lambda argv, **k: SnoopPopen(argv, **k))
    _wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
    assert ok is True
    assert seen == [{4242}]  # registered while running...
    assert 4242 not in rcp.LIVE_GROUPS._pgids  # ...deregistered after


def test_run_installs_armed_handlers_and_restores(
    tmp_path: Path, _fixed_binding: str, monkeypatch: pytest.MonkeyPatch, capsys
):
    """merge-gate witness P2: before/after symmetry alone passes a capture-without-
    install mutation — so capture the handler DURING the run and prove it is ARMED
    (invoking it terminates the registry and raises SystemExit 128+signum)."""
    import signal as _signal

    monkeypatch.setattr(rcp, "LIVE_GROUPS", rcp._LiveGroups())
    before = (_signal.getsignal(_signal.SIGTERM), _signal.getsignal(_signal.SIGINT))
    seen = {}

    def capture_one(c, b, e, s, w):
        seen["term"] = _signal.getsignal(_signal.SIGTERM)
        seen["int"] = _signal.getsignal(_signal.SIGINT)
        return 60.0, True

    rcp.run("main", channel="codex", reps=5, ns=(1, 2, 4), one=capture_one)
    after = (_signal.getsignal(_signal.SIGTERM), _signal.getsignal(_signal.SIGINT))
    assert after == before  # the probe's handlers never outlive the run
    assert seen["term"] is seen["int"] and seen["term"] not in before  # INSTALLED mid-run
    with pytest.raises(SystemExit) as exc:  # and ARMED: the real termination behavior
        seen["term"](_signal.SIGTERM, None)
    assert exc.value.code == 128 + _signal.SIGTERM
    assert rcp.LIVE_GROUPS.terminating  # the handler drove the registry
    rcp.LIVE_GROUPS.reset()


def test_add_refused_once_terminating(monkeypatch: pytest.MonkeyPatch):
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(rcp.os, "killpg", lambda pgid, sig: killed.append((pgid, sig)))
    monkeypatch.setattr(rcp, "_group_alive", lambda pgid: False)
    groups = rcp._LiveGroups()
    groups.add(111)
    groups.begin_termination()
    assert killed == [(111, rcp.signal.SIGTERM)]  # the snapshot was stopped
    assert groups.add(333) is False  # ...and no later registration is accepted
    groups.reset()
    assert groups.add(444) is True  # re-armed for the next run


def test_one_skips_spawn_once_terminating(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # the autouse fixture makes any real spawn a failure, so reaching the return
    # WITHOUT tripping it proves no reviewer was spawned after termination began
    monkeypatch.setattr(rcp, "LIVE_GROUPS", rcp._LiveGroups())
    rcp.LIVE_GROUPS.begin_termination()
    wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
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
    _wall, ok = rcp._one("codex", "main", {}, tmp_path, tmp_path)
    assert ok is False  # a call whose group was stopped at registration is not a verdict
    assert killed == [(4242, rcp.signal.SIGTERM)]  # the just-spawned group was stopped


def test_run_records_completed_samples_before_a_worker_crash(
    tmp_path: Path, _fixed_binding: str, capsys
):
    """codex r9 P2: a worker that raises must not discard the batch's already-completed
    paid samples — they are recorded as they finish, THEN the bug surfaces loudly."""
    calls = iter([lambda: (60.0, True), lambda: (_ for _ in ()).throw(RuntimeError("boom"))])

    def one_then_boom(c, b, e, s, w):
        return next(calls)()

    with pytest.raises(RuntimeError, match="boom"):
        rcp.run("main", channel="codex", reps=1, ns=(2,), one=one_then_boom)
    rows = fr.read_rows()
    # the completed call's sample is durable; the crash prevented the terminal result
    # row, so the run reads as not-run (absence), never as a clean verdict
    assert [r["finding_type"] for r in rows] == ["probe-sample"]


def test_begin_termination_reentrant_under_held_lock():
    """codex r10 P2: the signal handler runs ON the main thread and can interrupt a
    locked section — begin_termination must re-enter the SAME thread's held lock (RLock)
    instead of self-deadlocking. A plain-Lock regression manifests as this test hanging."""
    groups = rcp._LiveGroups()
    # fast discriminator FIRST (merge-gate witness P3): same-thread double-acquire
    # succeeds only on an RLock — a plain-Lock regression fails HERE in milliseconds
    # instead of hanging the reentry call below until an external job-timeout
    assert groups._lock.acquire(blocking=False)
    assert groups._lock.acquire(blocking=False), "lock is not reentrant (RLock regressed)"
    groups._lock.release()
    groups._lock.release()
    with groups._lock:  # simulate SIGTERM landing while main holds the lock
        groups.begin_termination()
    assert groups.add(1) is False  # the flag committed despite the held lock

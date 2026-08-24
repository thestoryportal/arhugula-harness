"""B-208 — the shared loop ledger must be unreachable from a test process.

`loop_status_path()` (tools/hooks/loop_lib.sh) resolves the venue from the ambient
environment, falling back to the operator's real ledger when `HARNESS_LOOP_STATUS_PATH`
is unset. Every pytest process starts with it unset, so any test reaching a real emit
path appended real `DEFERRED-HIL` rows to the venue the SessionStart hook reads.
`tools/conftest.py` now redirects it once per `tools/` session -- at the joint where
every loop-row producer lives, rather than at the root, where the redirect would also
leak a `HARNESS_*` name into axis suites that assert none is set. These witness that.

Case 2 is the load-bearing one and is deliberately hermetic: it moves the COMPUTED
FALLBACK to a temp dir, so removing the conftest redirect sends the write into a file
this test owns rather than into the operator's ledger. A mutation probe of the fix must
not reproduce the very damage the fix prevents.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reservations as rs

_VENUE_ENV = "HARNESS_LOOP_STATUS_PATH"


def test_session_venue_is_redirected_away_from_the_default():
    """(1) The redirect happened at all, and named a real absolute path."""
    venue = os.environ.get("HARNESS_LOOP_STATUS_PATH")
    assert venue, "tools/conftest.py must redirect HARNESS_LOOP_STATUS_PATH"
    assert venue.startswith("/"), f"loop_status_path rejects a relative venue, got {venue!r}"
    assert "harness-loop-status-" in venue, f"not the session's throwaway venue: {venue!r}"
    assert ".gstack" not in venue, f"venue still resolves inside the operator's store: {venue!r}"


def test_a_real_emit_lands_in_the_redirect_and_not_in_the_computed_fallback(monkeypatch, tmp_path):
    """(2) The redirect governs the ACTUAL writer, not just the variable.

    `emit_loop_row` shells out to `loop_log_structured`, which is also the path the
    door's subprocess-driven tests take — monkeypatching the Python seam cannot reach
    those, so the environment is the only lever and this asserts on it end to end.
    """
    # Relocate the fallback the shell would compute if the redirect were gone. With the
    # redirect in place HARNESS_LOOP_STATUS_PATH wins and this file must never appear;
    # revert the conftest and the emit lands here instead — discriminating, and harmless.
    queue = tmp_path / "arc-metrics-queue"
    queue.mkdir()
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR", str(queue))
    fallback = tmp_path / "loop_status.md"

    # Read the venue WITHOUT subscripting: with the redirect reverted the variable is
    # absent, and dying here would leave the assertion below — the one that actually
    # observes the pollution — unexercised, so the probe would prove only that the test
    # reads an env var. The emit must run either way for the witness to see the mechanism.
    redirect = os.environ.get("HARNESS_LOOP_STATUS_PATH")
    venue = Path(redirect) if redirect else None
    before = venue.read_text() if venue and venue.exists() else ""

    rs.emit_loop_row(
        "NOTIFY", "b-208-witness", "b-208:isolation:probe", "row from the B-208 witness"
    )

    assert not fallback.exists(), (
        "a real emit reached the COMPUTED fallback venue — under a production environment "
        f"that path is the operator's shared append-only ledger ({fallback})"
    )
    assert venue is not None, "tools/conftest.py must redirect HARNESS_LOOP_STATUS_PATH"
    assert venue.exists(), "the emit did not reach the redirected venue"
    appended = venue.read_text()[len(before) :]
    assert "b-208:isolation:probe" in appended, f"row missing from the redirect: {appended!r}"


def test_the_redirect_does_not_outlive_a_tools_test(tmp_path):
    """(3) The isolation is a property, not an accident of how the suites are invoked.

    `HARNESS_LOOP_STATUS_PATH` lives in process-global state that outlives whichever
    suite set it, and `RuntimeConfig`'s env loader consumes the whole `HARNESS_*`
    namespace — so `harness-runtime`'s `test_env_defaults_to_os_environ_when_none`
    asserts that none of them is set. A session-scoped setter in `tools/conftest.py`
    satisfies every tools test and still breaks that one whenever the two run in the
    same process. That was the first shape of the fixture, and it failed exactly this
    way (out-of-family review, round 2, confirmed by running it).

    Asserting it in-process is not possible — this test cannot observe its own teardown
    — so the witness is the mixed invocation itself, in a subprocess.

    The two orders catch DIFFERENT regressions, and only the first catches that one.
    `[mine, axis]` is the discriminating order for a session-scoped setter: revert the
    fixture to `scope="session"` and it reds, while `[axis, mine]` stays green, because
    nothing has set the variable yet when the axis test runs first (verified by mutation,
    merge-gate witness lens). `[axis, mine]` is kept because it catches the shape the
    first order cannot — a redirect established at import or collection time rather than
    per test, which is set before ANY test runs and so leaks in both directions.
    """
    axis = "harness-runtime/tests/test_config_loader.py::test_env_defaults_to_os_environ_when_none"
    mine = (
        "tools/test_loop_status_isolation.py"
        "::test_session_venue_is_redirected_away_from_the_default"
    )
    root = Path(__file__).resolve().parent.parent
    # The child must model a FRESH invocation. Without this it inherits the redirect
    # THIS test is running under (the autouse fixture set it for us too), so the axis
    # test fails on the parent's variable and the witness reports a leak that the fix
    # did not cause. Stripping the namespace leaves the child's own tools/conftest.py
    # as the only thing that can set it — which is exactly the mechanism under test.
    env = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_")}

    for order in ([mine, axis], [axis, mine]):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:randomly",
                *order,
                "--basetemp",
                str(tmp_path / "bt"),
            ],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert proc.returncode == 0, (
            f"the tools redirect leaked across suites in order {order}:\n"
            f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
        )


def test_a_mid_test_monkeypatch_undo_does_not_lift_the_redirect(monkeypatch, tmp_path):
    """(4) The redirect survives the `monkeypatch.undo()` several tools tests perform.

    `monkeypatch` is ONE function-scoped instance shared between a test body and every
    fixture that requests it, and `undo()` empties the whole stack — not just the
    caller's own entries. Tools tests use it to drop a `run` stub before exercising the
    real subprocess runner (`test_arc_exit_report.py:942`, `:958`, `:598`,
    `test_lanes_verify.py:258`, `test_merge_gate_log.py:504`, `:527`,
    `test_finding_record.py:635`, `test_mutation_probe.py:1785`, `:1825`). If the venue
    redirect rode on that stack it would be lifted right before the emit that most needs
    it, and the row would land in the operator's ledger.

    `test_arc_exit_report.py::shared_ledger` documents this same trap and avoids it the
    same way; the fixture in `tools/conftest.py` briefly did not, and this pins it.
    """
    queue = tmp_path / "arc-metrics-queue"
    queue.mkdir()
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR", str(queue))
    fallback = tmp_path / "loop_status.md"

    monkeypatch.undo()  # exactly what those tests do mid-test

    venue = os.environ.get(_VENUE_ENV)
    assert venue, (
        "the undo() lifted the redirect — a real emit would now resolve the operator's ledger"
    )

    rs.emit_loop_row("NOTIFY", "b-208-witness", "b-208:undo:probe", "row after a mid-test undo")

    assert not fallback.exists(), "a post-undo emit reached the computed fallback venue"
    assert "b-208:undo:probe" in Path(venue).read_text()

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

import pytest
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

    One order, deliberately. `[mine, axis]` is the order that discriminates: revert the
    fixture to `scope="session"` and it reds, while the reverse stays green, because
    nothing has set the variable yet when the axis test runs first. An earlier version
    ran both and justified the reverse as catching an import/collection-time redirect
    this order could not — that justification was false, and mutation-probing settled it:
    a collection-time redirect reds BOTH orders equally (1 failed, 1 passed each),
    because pytest imports every conftest before running any test. No regression shape
    was found that the reverse order alone catches, so it is gone rather than kept as
    ceremony whose stated reason does not hold.

    `-p no:randomly` is not decoration: the ordering IS the mechanism here, and a
    shuffling plugin would silently reorder the two node ids.
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

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:randomly",
            mine,
            axis,
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
        "the tools redirect outlived its test and reached the axis suite:\n"
        f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
    )


def test_a_mid_test_monkeypatch_undo_does_not_lift_the_redirect(monkeypatch, tmp_path):
    """(4) The redirect survives the `monkeypatch.undo()` several tools tests perform.

    `monkeypatch` is ONE function-scoped instance shared between a test body and every
    fixture that requests it, and `undo()` empties the whole stack — not just the
    caller's own entries. Tools tests use it to drop a `run` stub before exercising the
    real subprocess runner. `rg 'monkeypatch.undo' tools/` finds them.

    No count, no file list, and no line numbers -- deliberately. This paragraph named
    line numbers first, and this PR's own docstring edit shifted every one of them by two
    the same day; it then named a count and a file list, and that was wrong on arrival and
    missed a file entirely. Both were maps somebody has to remember to redraw, and neither
    fact the mechanism actually depends on: what matters is THAT tools tests undo()
    mid-test, not how many or where. The grep stays true by construction. If the venue
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


def test_the_session_temp_root_is_removed_when_the_session_ends(tmp_path):
    """(5) The venue directory does not accrue one tree per pytest run.

    `mkdtemp` with nobody to clean up after it is the shape B-207 was filed under, and
    this arc reintroduced it before giving the root a fixture teardown. That teardown
    then sat unwitnessed for three rounds: deleting it left this file and
    `test_arc_exit_report.py` entirely green (merge-gate witness lens, round 3), so a
    future edit dropping it would restore the leak with no signal at all.

    Session teardown cannot be observed from inside the session, so the witness is a
    child pytest run with `TMPDIR` pointed at a directory this test owns — `mkdtemp`
    honours it — and the assertion is that nothing matching the venue prefix survives the
    child's exit.

    The child runs TWO items, not one, and that is the load-bearing detail. With a single
    item, "one root cached for the session" and "a fresh root minted per item" are
    indistinguishable: both leave exactly one directory, and `pytest_unconfigure` removes
    the one in the stash either way. Removing the cache guard in `_venue_root` therefore
    kept all six witnesses green while stranding five directories per run — the same
    B-207-shaped accrual this teardown exists to close (merge-gate witness lens, round 5).
    With two items, the uncached shape mints two and cleans one, so the survivor shows up.

    Not vacuous: the child runs the redirect witness, which asserts the venue path
    contains `harness-loop-status-`. Its passing therefore proves a directory WAS created
    under the child's `TMPDIR`, so an empty survivor list means removed, not never-made.

    The two chosen items must not themselves spawn a child — this test does, and naming
    the whole module here would recurse.
    """
    tmproot = tmp_path / "tmproot"
    tmproot.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_")}
    env["TMPDIR"] = str(tmproot)

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:randomly",
            "tools/test_loop_status_isolation.py"
            "::test_session_venue_is_redirected_away_from_the_default",
            "tools/test_loop_status_isolation.py"
            "::test_a_mid_test_monkeypatch_undo_does_not_lift_the_redirect",
            "--basetemp",
            str(tmp_path / "bt"),
        ],
        cwd=Path(__file__).resolve().parent.parent,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, (
        "the child could not establish a venue, so this test proves nothing:\n"
        f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
    )

    survivors = sorted(p.name for p in tmproot.glob("harness-loop-status-*"))
    assert survivors == [], (
        f"the session temp root outlived its pytest run: {survivors} — one tree accrues "
        "per run, which is the B-207-shaped leak this fixture's teardown exists to close"
    )


_MODULE_PHASE: dict[str, object] = {}


@pytest.fixture(scope="module", autouse=True)
def _emit_during_module_setup():
    """Emit from a MODULE-scoped fixture, i.e. outside any test body.

    Higher-scoped fixtures are set up before the function-scoped ones and torn down after
    them, so this runs in the phase a per-test redirect cannot reach. It is a fixture
    rather than a test on purpose: the phase IS the thing under test.
    """
    _MODULE_PHASE["venue"] = os.environ.get(_VENUE_ENV)
    try:
        rs.emit_loop_row(
            "NOTIFY", "b-208-witness", "b-208:module-phase:probe", "row from module setup"
        )
        _MODULE_PHASE["emitted"] = True
    except Exception as exc:
        _MODULE_PHASE["emitted"] = exc
    yield


def test_the_redirect_covers_fixture_phases_not_just_test_bodies():
    """(6) The boundary holds for the whole item lifecycle, not only the test body.

    A function-scoped autouse fixture — this conftest's shape for four rounds — starts
    after higher-scoped fixtures are set up and ends before they tear down, so anything
    emitting from a session- or module-scoped fixture still resolved the operator's
    ledger. No witness up to round 6 ran outside a test body, so none could see it
    (out-of-family review, round 7).

    Revert the conftest to a function-scoped autouse fixture and this reds: the module
    fixture above observes no venue at all.
    """
    venue = _MODULE_PHASE.get("venue")
    assert venue, (
        "a module-scoped fixture saw no redirect — an emit from any fixture phase would "
        "resolve the operator's ledger"
    )
    assert "harness-loop-status-" in str(venue), f"not the session venue: {venue!r}"
    assert _MODULE_PHASE.get("emitted") is True, (
        f"the module-phase emit did not succeed: {_MODULE_PHASE.get('emitted')!r}"
    )
    assert "b-208:module-phase:probe" in Path(str(venue)).read_text()

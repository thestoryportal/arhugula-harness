"""B-208 — keep the SHARED loop ledger unreachable from a `tools/` test process.

`loop_status_path()` (tools/hooks/loop_lib.sh) resolves the ledger from the ambient
environment and falls back to the operator's real
`~/.gstack/projects/<project>/loop_status.md` whenever `HARNESS_LOOP_STATUS_PATH` is
unset -- the default state of every pytest process. Any test reaching a real emit path
therefore appended real `DEFERRED-HIL` rows to the venue the SessionStart hook reads,
where a synthetic `pr-1` gate nags forever and only a hand-written `RESOLVED-HIL`
clears it. It is append-only by contract (C-HE-09 §2), so the debris is not removable
after the fact: by the time this landed, 6288 of the ledger's 6589 rows (1.07 MB) were
`lane=A` fixtures against 82 real-lane rows.

Isolating per test FILE is what the workspace tried and what drifted -- two files
remember (`test_arc_exit_report.py`, `test_review_wrapper.py`), `test_merge_door.py`
does not, and a file written tomorrow will not either. `emit_loop_row` also shells out
to bash and several door tests drive `merge_door.py` as a real SUBPROCESS, so
monkeypatching the Python seam cannot reach them; only the inherited environment can.
Hence one enforcement point for the whole directory: no `tools/` test can reach the
production ledger by omission.

This lives HERE and not in the root conftest deliberately. Every producer of loop rows
is under `tools/` (`reservations.emit_loop_row`, its `merge_door` callers, the hook
suites -- which already isolate themselves); no `harness-*` package writes the ledger.
A root-level redirect additionally leaks a `HARNESS_*` name into every axis suite, and
`harness-runtime/tests/test_config_loader.py::test_env_defaults_to_os_environ_when_none`
asserts that NO `HARNESS_*` variable is set, because RuntimeConfig's env loader consumes
that namespace. Enforcing at the joint where the concern actually lives keeps both
invariants true instead of trading one for the other.
"""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

_VENUE_ENV = "HARNESS_LOOP_STATUS_PATH"


@pytest.fixture(scope="session")
def _loop_status_root() -> Iterator[Path]:
    """One throwaway directory per session, removed when the session ends.

    Session-scoped so a run does not create a tree per test, and OWNED so it does not
    accrue a tree per run either: `mkdtemp` with nobody to clean it up is the shape
    B-207's sibling leak was filed under, and a fixture already has the teardown.
    """
    root = Path(tempfile.mkdtemp(prefix="harness-loop-status-"))
    try:
        yield root
    finally:
        # Swallowing here is deliberate and bounded: the tree is ours, lives under
        # TMPDIR, and nothing downstream reads it. Raising would turn a cleanup hiccup
        # into a red session, the wrong trade for a directory the OS reaps anyway --
        # the leak this closes is about accrual, not correctness.
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture(autouse=True)
def _isolated_loop_status_venue(_loop_status_root: Path) -> Iterator[Path]:
    """Redirect the ledger around EACH `tools/` test, restoring it by hand.

    Per-TEST rather than session-scoped, because the variable lives in process-global
    state that outlives whichever suite set it. A session-scoped setter leaves
    `HARNESS_LOOP_STATUS_PATH` in place for everything that runs afterwards in the same
    process, so a mixed `pytest tools/... harness-runtime/...` invocation would fail the
    axis suite's no-`HARNESS_*` invariant. That was this fixture's second shape and it
    failed exactly that way when run; `test_the_redirect_does_not_outlive_a_tools_test`
    is the witness.

    Deliberately NOT the `monkeypatch` FIXTURE -- the same reason
    `test_arc_exit_report.py::shared_ledger` gives, and the same trap: that fixture is ONE
    function-scoped instance shared with the test body, and nine tools tests call
    `monkeypatch.undo()` mid-test to drop a `run` stub before exercising the real
    subprocess runner. An `undo()` empties the whole stack, so a redirect riding on it is
    silently lifted mid-test and the very next real emit resolves the operator's ledger.
    That was this fixture's third shape; out-of-family review and CI caught it
    independently, the latter by rolling `test_arc_exit_report.py`'s own pin back
    underneath it. `test_a_mid_test_monkeypatch_undo_does_not_lift_the_redirect` is the
    witness.

    An INDEPENDENT `MonkeyPatch` is immune to that -- `undo()` only empties the instance
    it is called on. It is preferred over a hand-rolled `try/finally` because restoring an
    environment variable has two modes (it was set; it was not), only one of which is
    reachable from a pytest process that nobody pre-configured. The hand-rolled version
    therefore shipped a restore branch no witness could reach, confirmed dead by mutation
    (merge-gate witness lens). Delegating to `MonkeyPatch` deletes the branch rather than
    testing it: one implementation owns both modes, and it is already covered by pytest's
    own suite.

    Set unconditionally rather than only-if-unset: no test here legitimately writes the
    real venue, so an ambient value pointing at it is a misconfiguration, not an intent
    worth honouring. A test that pins its own venue later (`shared_ledger`) still wins,
    and this restores whatever it found underneath.
    """
    venue = _loop_status_root / "loop_status.md"
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv(_VENUE_ENV, str(venue))
        yield venue

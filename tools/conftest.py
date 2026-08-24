"""B-208 — keep the SHARED loop ledger unreachable from a `tools/` test process.

`loop_status_path()` (tools/hooks/loop_lib.sh) resolves the ledger from the ambient
environment and falls back to the operator's real
`~/.gstack/projects/<project>/loop_status.md` whenever `HARNESS_LOOP_STATUS_PATH` is
unset -- the default state of every pytest process. Any test reaching a real emit path
therefore appended real `DEFERRED-HIL` rows to the venue the SessionStart hook reads,
where a synthetic `pr-1` gate nags forever and only a hand-written `RESOLVED-HIL`
clears it. It is append-only by contract (C-HE-09 §2), so the debris is not removable
after the fact: by the time this landed, 6288 of the ledger's 6589 lines (1.07 MB) were
synthetic `lane=A` fixture rows and only 82 came from real lanes — the rest are `lane=-`
infra rows and the file's own header, so those two figures are not a partition of the whole.

Isolating per test FILE is what the workspace tried and what drifted -- two files
remember (`test_arc_exit_report.py`, `test_review_wrapper.py`), `test_merge_door.py`
does not, and a file written tomorrow will not either. `emit_loop_row` also shells out
to bash and several door tests drive `merge_door.py` as a real SUBPROCESS, so
monkeypatching the Python seam cannot reach them; only the inherited environment can.
Hence one enforcement point for the whole directory: no `tools/` test can reach the
production ledger by omission. The bracket is per-ITEM, so two phases run outside it —
collection, and session-scope fixture teardown after a non-tools FINAL item in a mixed
run (module scope is bracketed: pytest tears down to the next item's level inside the
current item's teardown phase — measured). Covering them would hold the variable alive
outside tools items, the exact session-wide leak rejected below; there the boundary is
instead the witnessed emptiness claim that nothing under `tools/` emits in those phases
(`test_loop_status_isolation.py` cases 7–8, the owned-fallback canaries).

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

import pathlib
import shutil
import tempfile
from pathlib import Path

import pytest

_VENUE_ENV = "HARNESS_LOOP_STATUS_PATH"
_DIR = Path(__file__).resolve().parent
_ROOT_KEY: pytest.StashKey[Path] = pytest.StashKey()


def _venue_root(config: pytest.Config) -> Path:
    """One throwaway directory per session, made on first use and owned by this module."""
    if _ROOT_KEY not in config.stash:
        config.stash[_ROOT_KEY] = Path(tempfile.mkdtemp(prefix="harness-loop-status-"))
    return config.stash[_ROOT_KEY]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):
    """Redirect the ledger around each `tools/` item's WHOLE lifecycle.

    A function-scoped autouse fixture -- this file's previous shape -- only covers the
    test BODY. Higher-scoped fixtures are set up before it and torn down after it, so a
    session- or module-scoped fixture that emitted would still resolve the operator's
    ledger, which contradicts the boundary this module claims (out-of-family review,
    round 7). Wrapping the run protocol brackets setup, call and teardown together.

    Per-ITEM rather than per-session, because the variable lives in process-global state
    that outlives whichever suite set it: `RuntimeConfig`'s env loader consumes the whole
    `HARNESS_*` namespace, and `harness-runtime`'s
    `test_env_defaults_to_os_environ_when_none` asserts none of them is set. A session-wide
    redirect fails that test in a mixed invocation (round 2, confirmed by running it);
    `test_the_redirect_does_not_outlive_a_tools_test` is the witness.

    The path guard is NOT decoration. A subdirectory conftest's `pytest_runtest_protocol`
    fires for items ANYWHERE in the run, not only those beneath it -- measured, and
    without the guard the axis test above sees the variable and fails. Only items under
    this directory get the redirect.

    An INDEPENDENT `MonkeyPatch` restores it: `undo()` empties only the instance it is
    called on, so the mid-test `monkeypatch.undo()` several tools tests perform cannot
    lift this (round 3; `rg 'monkeypatch.undo' tools/`). Delegating also avoids a
    hand-rolled two-armed restore whose was-set arm nothing could reach (round 4).
    """
    if _DIR not in pathlib.Path(str(item.path)).resolve().parents:
        yield
        return
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv(_VENUE_ENV, str(_venue_root(item.config) / "loop_status.md"))
        yield


def pytest_unconfigure(config: pytest.Config) -> None:
    """Take the venue directory with us, so a run does not accrue one tree.

    `mkdtemp` with nobody to clean up after it is the shape B-207 was filed under.
    Swallowing a removal failure is deliberate and bounded: the tree is ours, lives under
    TMPDIR, and nothing downstream reads it -- the leak this closes is about accrual, not
    correctness. `test_the_session_temp_root_is_removed_when_the_session_ends` is the
    witness.
    """
    root = config.stash.get(_ROOT_KEY, None)
    if root is not None:
        shutil.rmtree(root, ignore_errors=True)

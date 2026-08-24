"""Workspace root conftest — B-117 duplicate-test-module-path session gate.

Fails the session at collection start (loud, earliest venue) when two
``harness-*/tests`` files resolve to the same importable module path — the
shape that silently drops witnesses (see ``tools/module_path_guard.py`` for
the mechanism and the #1241 incident). A hard ``UsageError`` here is the
deliberate failure venue: the alternative (a CI-only step) would leave local
runs green while witnesses are dropped, which is the defect's own signature.

The guard library is loaded by file path (not ``import tools.…``): ``tools``
is not a package, and under ``--import-mode=importlib`` the repo root is not
guaranteed on ``sys.path`` for this conftest.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent

# Published so a witness can read back the venue this session redirected to.
_LOOP_VENUE: pytest.StashKey[Path] = pytest.StashKey()


def _load_guard():  # -> module
    spec = importlib.util.spec_from_file_location(
        "module_path_guard", _ROOT / "tools" / "module_path_guard.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pytest_sessionstart(session: pytest.Session) -> None:
    guard = _load_guard()
    duplicates = guard.find_duplicate_test_module_paths(_ROOT)
    if duplicates:
        raise pytest.UsageError(guard.render_report(duplicates))


def pytest_configure(config: pytest.Config) -> None:
    """Point the SHARED loop ledger at a throwaway venue for the whole test session.

    `loop_status_path()` (tools/hooks/loop_lib.sh) falls back to the operator's real
    `~/.gstack/projects/<project>/loop_status.md` whenever `HARNESS_LOOP_STATUS_PATH`
    is unset -- and unset is the default state of every pytest process. Any test that
    reaches a real emit path therefore appends real `DEFERRED-HIL` rows to the venue
    the SessionStart hook reads, where a synthetic `pr-1` gate nags forever and only a
    hand-written `RESOLVED-HIL` clears it. It is append-only by contract (C-HE-09 §2),
    so the debris is not removable after the fact: by the time this landed, 6288 of the
    ledger's 6589 rows (1.07 MB) were `lane=A` fixtures against 82 real-lane rows.

    Isolating per test FILE is what the workspace tried and what drifted -- two files
    remember (`test_arc_exit_report.py`, `test_review_wrapper.py`), `test_merge_door.py`
    does not, and a file written tomorrow will not either. `emit_loop_row` also shells
    out to bash and several door tests drive `merge_door.py` as a real SUBPROCESS, so
    monkeypatching the Python seam cannot reach them; only the inherited environment
    can. Hence one enforcement point, at the outermost venue, before collection: no
    test in this workspace can reach the production ledger by omission.

    Set unconditionally rather than only-if-unset. No test here legitimately writes the
    real venue, so an ambient value pointing at it is a misconfiguration, not an intent
    worth honouring. Per-test `monkeypatch.setenv` still wins -- it runs later.
    """
    venue = Path(tempfile.mkdtemp(prefix="harness-loop-status-")) / "loop_status.md"
    os.environ["HARNESS_LOOP_STATUS_PATH"] = str(venue)
    config.stash[_LOOP_VENUE] = venue

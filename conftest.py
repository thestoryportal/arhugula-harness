"""Workspace root conftest — B-117 duplicate-test-module-path session gate.

Fails the session at collection start (loud, earliest venue) when two files
under the configured ``testpaths`` resolve to the same importable module path — the
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
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent


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
    # [LAW:one-source-of-truth] the scanned roots are pytest's own parsed `testpaths`
    configured = session.config.getini("testpaths")
    if not configured:
        raise pytest.UsageError(
            "B-117: no configured `testpaths`, so the duplicate-module guard has no roots to prove"
        )
    rootpath = session.config.rootpath
    try:
        duplicates = guard.find_duplicate_test_module_paths(
            rootpath, [rootpath / path for path in configured]
        )
    except FileNotFoundError as exc:
        # [LAW:no-silent-failure] a configured root that is gone is a usage error, not a crash
        raise pytest.UsageError(str(exc)) from exc
    if duplicates:
        raise pytest.UsageError(guard.render_report(duplicates))

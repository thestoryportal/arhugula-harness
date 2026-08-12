"""B-117 duplicate-test-module-path guard witnesses.

The positive-control collision probe the register close-out prescribes: a
synthetic package-anchored duplicate must be REPORTED (deleting the guard's
collision logic fails these), the real tree must pass clean, and the
collision unit must be the pytest-faithful PACKAGE-ANCHORED module path —
non-package nested files and cross-depth same-basenames are legal and must
NOT be flagged (both verified against live pytest behavior at the #1315
build probes).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_guard():
    """Load the sibling library by file path — cwd-independent, so the file
    runs identically from the repo root (`uv run pytest tools/...`) and from
    the CI step's `working-directory: tools` (codex r7)."""
    path = Path(__file__).resolve().parent / "module_path_guard.py"
    spec = importlib.util.spec_from_file_location("module_path_guard", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mpg = _load_guard()


def _mk(root: Path, rel: str, *, packages: bool = True) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def test_placeholder() -> None: ...\n")
    if packages:
        member = root / Path(rel).parts[0]
        d = p.parent
        while d != member:
            (d / "__init__.py").touch()
            d = d.parent


def test_synthetic_duplicate_is_reported(tmp_path: Path) -> None:
    """Two members claiming tests/test_x.py collide — the #1241 shape."""
    _mk(tmp_path, "harness-aa/tests/test_x.py")
    _mk(tmp_path, "harness-bb/tests/test_x.py")
    duplicates = mpg.find_duplicate_test_module_paths(tmp_path)
    assert duplicates == {
        "tests.test_x": [
            "harness-aa/tests/test_x.py",
            "harness-bb/tests/test_x.py",
        ]
    }


def test_suffix_pattern_duplicate_is_reported(tmp_path: Path) -> None:
    """pytest also discovers *_test.py — the probe showed the same silent
    drop for tests/collision_test.py; the guard must scan both patterns."""
    _mk(tmp_path, "harness-aa/tests/collision_test.py")
    _mk(tmp_path, "harness-bb/tests/collision_test.py")
    assert "tests.collision_test" in mpg.find_duplicate_test_module_paths(tmp_path)


def test_package_subdir_duplicate_is_reported(tmp_path: Path) -> None:
    """Same path inside a tests SUBPACKAGE (with __init__.py chain) collides."""
    _mk(tmp_path, "harness-aa/tests/integration/test_y.py")
    _mk(tmp_path, "harness-bb/tests/integration/test_y.py")
    assert "tests.integration.test_y" in mpg.find_duplicate_test_module_paths(tmp_path)


def test_broken_chain_still_collides_at_inner_package(tmp_path: Path) -> None:
    """tests/ WITHOUT __init__.py but tests/integration/ WITH it anchors the
    module at the inner package — two members' integration/test_w.py resolve
    to the SAME `integration.test_w` and pytest drops one (round-2 probe:
    2 of 3 functions collected). The guard must anchor at the outermost
    CONTIGUOUS package, not require the chain to reach tests/."""
    _mk(tmp_path, "harness-aa/tests/integration/test_w.py", packages=False)
    _mk(tmp_path, "harness-bb/tests/integration/test_w.py", packages=False)
    (tmp_path / "harness-aa/tests/integration/__init__.py").touch()
    (tmp_path / "harness-bb/tests/integration/__init__.py").touch()
    assert "integration.test_w" in mpg.find_duplicate_test_module_paths(tmp_path)


def test_non_package_subdir_is_legal(tmp_path: Path) -> None:
    """Same relpath under NON-package subdirs (no __init__.py) collects fine
    under importlib mode (live probe: both b117probe/test_p1.py PASSED) —
    flagging it would be a false positive."""
    _mk(tmp_path, "harness-aa/tests/unit/test_y.py", packages=False)
    _mk(tmp_path, "harness-bb/tests/unit/test_y.py", packages=False)
    (tmp_path / "harness-aa/tests/__init__.py").touch()
    (tmp_path / "harness-bb/tests/__init__.py").touch()
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_same_basename_different_depth_is_legal(tmp_path: Path) -> None:
    """tests/test_z.py vs tests/integration/test_z.py are DISTINCT modules."""
    _mk(tmp_path, "harness-aa/tests/test_z.py")
    _mk(tmp_path, "harness-bb/tests/integration/test_z.py")
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_unique_tree_is_clean(tmp_path: Path) -> None:
    _mk(tmp_path, "harness-aa/tests/test_a.py")
    _mk(tmp_path, "harness-bb/tests/test_b.py")
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_non_harness_dirs_out_of_scope(tmp_path: Path) -> None:
    """Only harness-*/tests trees participate (tools/ is single-directory
    top-level modules — the collision cannot arise there by construction)."""
    _mk(tmp_path, "tools/test_t.py", packages=False)
    _mk(tmp_path, "harness-aa/tests/test_t.py")
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_double_pattern_match_counts_once(tmp_path: Path) -> None:
    """A file matching BOTH patterns (test_foo_test.py) must not self-collide."""
    _mk(tmp_path, "harness-aa/tests/test_foo_test.py")
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_live_tree_is_clean() -> None:
    """Positive control at HEAD: the real workspace carries no collision (the
    B-117 re-measure) — and this very session imported the guard through the
    root conftest, so a regression fails BOTH this assert and collection."""
    root = Path(__file__).resolve().parent.parent
    assert mpg.find_duplicate_test_module_paths(root) == {}


def test_report_names_every_file() -> None:
    report = mpg.render_report(
        {"tests.test_x": ["harness-aa/tests/test_x.py", "harness-bb/tests/test_x.py"]}
    )
    assert "tests.test_x" in report
    assert "harness-aa/tests/test_x.py" in report
    assert "harness-bb/tests/test_x.py" in report
    assert "SILENTLY DROP" in report


def test_conftest_gate_aborts_real_session(tmp_path: Path) -> None:
    """REAL-ENTRY-POINT witness for the conftest half: a synthetic workspace
    with two colliding members, the real conftest.py and the real guard
    library — an actual pytest subprocess must ABORT with the guard report
    (deleting the sessionstart hook or mis-rooting the scan fails this;
    the library-level witnesses alone cannot see either mutation)."""
    import shutil
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parent.parent
    (tmp_path / "tools").mkdir()
    shutil.copy(repo_root / "conftest.py", tmp_path / "conftest.py")
    shutil.copy(
        repo_root / "tools" / "module_path_guard.py",
        tmp_path / "tools" / "module_path_guard.py",
    )
    _mk(tmp_path, "harness-aa/tests/test_x.py")
    _mk(tmp_path, "harness-bb/tests/test_x.py")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q", "-p", "no:cacheprovider"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "B-117 duplicate test module path(s) detected" in combined
    assert "harness-aa/tests/test_x.py" in combined


def test_norecursedirs_are_excluded(tmp_path: Path) -> None:
    """A COLLIDING pair buried under a norecursedirs dir (fully
    package-chained, so only the exclusion saves it) must NOT block the
    session — recursive discovery never collects those files (codex r4:
    false-positive-only, but a blocked suite). Deleting
    `_pytest_would_recurse` flags `tests.venv.test_v` and fails this
    (merge-gate lens-3 catch: the prior fixture had no pair the exclusion
    ever adjudicated)."""
    _mk(tmp_path, "harness-aa/tests/venv/test_v.py")
    _mk(tmp_path, "harness-bb/tests/venv/test_v.py")
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_invalid_identifier_dir_anchors_below_it(tmp_path: Path) -> None:
    """A package chain broken by a non-identifier dir name (group-aa) anchors
    the module BELOW it — two members' group-*/integration/test_same.py still
    collide as integration.test_same (codex r6 probe, pytest 9.0.3)."""
    _mk(tmp_path, "harness-aa/tests/group-aa/integration/test_same.py")
    _mk(tmp_path, "harness-bb/tests/group-bb/integration/test_same.py")
    assert "integration.test_same" in mpg.find_duplicate_test_module_paths(tmp_path)

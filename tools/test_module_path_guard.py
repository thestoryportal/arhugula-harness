"""B-117 duplicate-test-module-path guard witnesses.

The positive-control collision probe the register close-out prescribes: a
synthetic duplicate must be REPORTED (deleting the guard's collision logic
fails these), the real tree must pass clean, and the collision unit must be
the relative module path — not the bare basename (same basename at different
depths is legal and must NOT be flagged).
"""

from __future__ import annotations

from pathlib import Path

import module_path_guard as mpg


def _mk(root: Path, rel: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def test_placeholder() -> None: ...\n")


def test_synthetic_duplicate_is_reported(tmp_path: Path) -> None:
    """Two members claiming tests/test_x.py collide — the #1241 shape."""
    _mk(tmp_path, "harness-aa/tests/test_x.py")
    _mk(tmp_path, "harness-bb/tests/test_x.py")
    duplicates = mpg.find_duplicate_test_module_paths(tmp_path)
    assert duplicates == {
        "tests/test_x.py": [
            "harness-aa/tests/test_x.py",
            "harness-bb/tests/test_x.py",
        ]
    }


def test_subdir_duplicate_is_reported(tmp_path: Path) -> None:
    """Same relative path inside a tests SUBPACKAGE collides too."""
    _mk(tmp_path, "harness-aa/tests/integration/test_y.py")
    _mk(tmp_path, "harness-bb/tests/integration/test_y.py")
    assert "tests/integration/test_y.py" in mpg.find_duplicate_test_module_paths(tmp_path)


def test_same_basename_different_depth_is_legal(tmp_path: Path) -> None:
    """tests/test_z.py vs tests/integration/test_z.py are DISTINCT modules —
    flagging them would be a false positive the relpath unit avoids."""
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
    _mk(tmp_path, "tools/test_t.py")
    _mk(tmp_path, "harness-aa/tests/test_t.py")
    assert mpg.find_duplicate_test_module_paths(tmp_path) == {}


def test_live_tree_is_clean() -> None:
    """Positive control at HEAD: the real workspace carries no collision (the
    B-117 re-measure) — and this very session imported the guard through the
    root conftest, so a regression fails BOTH this assert and collection."""
    root = Path(__file__).resolve().parent.parent
    assert mpg.find_duplicate_test_module_paths(root) == {}


def test_report_names_every_file() -> None:
    report = mpg.render_report(
        {"tests/test_x.py": ["harness-aa/tests/test_x.py", "harness-bb/tests/test_x.py"]}
    )
    assert "tests/test_x.py" in report
    assert "harness-aa/tests/test_x.py" in report
    assert "harness-bb/tests/test_x.py" in report
    assert "SILENTLY DROP" in report

"""B-104 Task 5a F3: the store checks a parent's carriers through CP's PUBLIC hash verifier.

The store must not import CP's private hash function nor keep its own copy of CP's hash field
list: `verify_pause_snapshot_hash` is the one place that decides whether a snapshot's stored
hash covers its own content. A parent whose journaled carrier no longer matches its stored hash
must refuse before any child claim exists.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import harness_runtime
import pytest

from .test_b104_resume_claim_started import (
    Family,
    _parent_carried_refusal,  # pyright: ignore[reportPrivateUsage]
    _started_parent,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def test_a_journaled_parent_carrier_altered_under_an_unchanged_hash_admits_no_child(
    placed: Any,
) -> None:
    family = Family(placed.journal_dir)
    honest = family.parent_with(family.child_refs)  # carrying, and hash-covered
    assert honest.fan_out_resume is not None
    # A carrier field the stored hash covers, changed WITHOUT re-hashing: same `snapshot_hash`.
    altered = honest.fan_out_resume.model_copy(update={"worker_count": 3})
    tampered = honest.model_copy(update={"fan_out_resume": altered})
    assert tampered.snapshot_hash == honest.snapshot_hash
    family.parent_ref = family.journal.capture(tampered, depth=0)

    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent, child=0)


def _top_package(module: str | None) -> str:
    return (module or "").split(".")[0]


def _private_harness_cp_imports(source_root: Path) -> list[tuple[str, int, str]]:
    """Every `from harness_cp... import _x` (or `import harness_cp._x`) in Runtime source."""
    found: list[tuple[str, int, str]] = []
    for path in sorted(source_root.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and _top_package(node.module) == "harness_cp":
                found += [
                    (str(path.relative_to(source_root)), node.lineno, alias.name)
                    for alias in node.names
                    if alias.name.startswith("_")
                ]
            elif isinstance(node, ast.Import):
                found += [
                    (str(path.relative_to(source_root)), node.lineno, alias.name)
                    for alias in node.names
                    if alias.name.split(".")[0] == "harness_cp"
                    and any(part.startswith("_") for part in alias.name.split("."))
                ]
    return found


def test_runtime_source_imports_nothing_private_from_harness_cp() -> None:
    source_root = Path(harness_runtime.__file__).resolve().parent

    assert _private_harness_cp_imports(source_root) == []


def test_the_private_import_scan_would_see_a_violation(tmp_path: Path) -> None:
    (tmp_path / "offender.py").write_text("from harness_cp.pause_resume_protocol import _x\n")

    assert _private_harness_cp_imports(tmp_path) == [("offender.py", 1, "_x")]

"""B-117 — duplicate-test-module-path guard (library half).

Every ``harness-*/tests/`` directory is a package literally named ``tests``
(each carries an ``__init__.py``), so two test files sharing the same path
RELATIVE to their package's ``tests`` root resolve to the SAME importable
module path (``tests.test_x`` / ``tests.integration.test_x``) — pytest
imports ONE module for BOTH files and SILENTLY DROPS the loser's tests, with
every signal (exit code, collected count) staying green. Not hypothetical:
at the B-93 build leg (#1241) ``test_b93_cross_process_lock_deadline.py``
existed in both ``harness-is/tests/`` and ``harness-runtime/tests/`` and 12
written witnesses never ran. ``--import-mode=importlib`` (already set) does
NOT prevent the drop while the ``tests`` packages share a name — the module
path is derived from the package path, which is identical across members.

The collision unit is the RELATIVE module path, not the bare basename:
``tests/test_x.py`` and ``tests/integration/test_x.py`` are distinct modules
and legitimately coexist. The guard therefore reports exactly the shape that
drops witnesses, with zero false positives by construction.

Consumed by the root ``conftest.py`` at every pytest session start (local
runs and the CI "pytest (all axis packages)" job alike — the earliest-stage
venue per the gate-enforcement-site discipline). ``tools/`` test files are
top-level modules in one directory and cannot express this collision; they
are out of scope by construction (noted, not silently skipped).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path


def find_duplicate_test_module_paths(root: Path) -> dict[str, list[str]]:
    """Map each colliding relative module path to the files claiming it.

    Scans ``<root>/harness-*/tests/**/test_*.py``; the key is the path
    relative to the workspace-member directory (``tests/...``), the value the
    repo-relative file paths (sorted) — an entry appears only when two or
    more DISTINCT members claim the same relative path. Empty dict == clean.
    """
    claims: dict[str, list[str]] = defaultdict(list)
    for member in sorted(root.glob("harness-*")):
        tests_dir = member / "tests"
        if not tests_dir.is_dir():
            continue
        for test_file in sorted(tests_dir.rglob("test_*.py")):
            rel_module = test_file.relative_to(member).as_posix()
            claims[rel_module].append(test_file.relative_to(root).as_posix())
    return {rel: files for rel, files in claims.items() if len(files) > 1}


def render_report(duplicates: dict[str, list[str]]) -> str:
    """Human-readable failure report, one colliding module path per block."""
    lines = [
        "B-117 duplicate test module path(s) detected — pytest would import ONE",
        "module for each group below and SILENTLY DROP the other file's tests:",
    ]
    for rel, files in sorted(duplicates.items()):
        lines.append(f"  {rel}:")
        lines.extend(f"    - {f}" for f in files)
    lines.append("Rename one file in each group (module paths under the shared")
    lines.append("`tests` package name must be workspace-unique).")
    return "\n".join(lines)

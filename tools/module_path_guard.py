"""B-117 — duplicate-test-module-path guard (library half).

Every ``harness-*/tests/`` directory is a package literally named ``tests``
(each carries an ``__init__.py``), so two test files resolving to the same
PACKAGE-ANCHORED module path (``tests.test_x`` / ``tests.integration.test_x``)
are imported as ONE module — pytest SILENTLY runs one file's tests under both
paths and DROPS the loser's, with every signal (exit code, collected count)
staying green. Not hypothetical: at the B-93 build leg (#1241)
``test_b93_cross_process_lock_deadline.py`` existed in both
``harness-is/tests/`` and ``harness-runtime/tests/`` and 12 written witnesses
never ran. ``--import-mode=importlib`` (already set) does NOT prevent the
drop while the ``tests`` packages share a name — the module path is derived
from the ``__init__.py`` package chain, which is identical across members.

Collision unit — verified by live probes at the #1315 build (out-of-family
rounds absorbed):

- The module path is PACKAGE-ANCHORED: it exists only where every directory
  from the member's ``tests`` root down to the file's parent carries an
  ``__init__.py``. A file under a NON-package subdirectory (no
  ``__init__.py``) gets a pytest-disambiguated unique module name and both
  same-named files collect fine — flagging those would be a false positive
  (probe: two ``tests/b117probe/test_p1.py`` files, no ``__init__.py``, both
  PASSED).
- BOTH default discovery patterns collide: ``test_*.py`` and ``*_test.py``
  (probe: two ``tests/collision_test.py`` files — the second path re-ran the
  FIRST file's function; the loser's tests silently vanished).

Consumed by the root ``conftest.py`` at every pytest session start (local
runs and the CI axis jobs alike — the earliest-stage venue per the
gate-enforcement-site discipline). ``tools/`` test files are top-level
modules in one directory and cannot express this collision; they are out of
scope by construction (noted, not silently skipped).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

_TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")


def _package_anchored_module(member: Path, test_file: Path) -> str | None:
    """The dotted module path pytest derives for ``test_file``, or ``None``
    when the file is not package-anchored at the member's ``tests`` root.

    Walks the directory chain from ``tests`` down to the file's parent; every
    directory must carry an ``__init__.py`` for the shared-package collision
    to exist. A break anywhere means pytest assigns a path-derived unique
    module name instead (no collision possible — verified by probe).
    """
    rel = test_file.relative_to(member)
    chain = [member / rel.parts[0]]
    for part in rel.parts[1:-1]:
        chain.append(chain[-1] / part)
    if any(not (d / "__init__.py").is_file() for d in chain):
        return None
    return ".".join((*rel.parts[:-1], test_file.stem))


def find_duplicate_test_module_paths(root: Path) -> dict[str, list[str]]:
    """Map each colliding package-anchored module path to the files claiming it.

    Scans both pytest default discovery patterns under
    ``<root>/harness-*/tests/``; the key is the dotted module path
    (``tests[.subpkg…].stem``), the value the repo-relative file paths
    (sorted) — an entry appears only when two or more DISTINCT members claim
    the same module path. Empty dict == clean.
    """
    claims: dict[str, list[str]] = defaultdict(list)
    for member in sorted(root.glob("harness-*")):
        tests_dir = member / "tests"
        if not tests_dir.is_dir():
            continue
        seen: set[Path] = set()
        for pattern in _TEST_FILE_PATTERNS:
            for test_file in sorted(tests_dir.rglob(pattern)):
                if test_file in seen:
                    continue
                seen.add(test_file)
                module = _package_anchored_module(member, test_file)
                if module is None:
                    continue
                claims[module].append(test_file.relative_to(root).as_posix())
    return {mod: sorted(files) for mod, files in claims.items() if len(files) > 1}


def render_report(duplicates: dict[str, list[str]]) -> str:
    """Human-readable failure report, one colliding module path per block."""
    lines = [
        "B-117 duplicate test module path(s) detected — pytest would import ONE",
        "module for each group below and SILENTLY DROP the other file's tests:",
    ]
    for mod, files in sorted(duplicates.items()):
        lines.append(f"  {mod}:")
        lines.extend(f"    - {f}" for f in files)
    lines.append("Rename one file in each group (module paths under the shared")
    lines.append("`tests` package name must be workspace-unique).")
    return "\n".join(lines)

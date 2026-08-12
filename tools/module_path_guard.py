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
from fnmatch import fnmatch
from pathlib import Path

_TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")

#: pytest's default ``norecursedirs`` (no override in pyproject.toml at HEAD):
#: files below these are never collected by RECURSIVE discovery, so they must
#: not trip the gate (r4 — a venv/build dir inside tests/ would otherwise
#: block every run). A collision below them IS still reachable by passing the
#: files as EXPLICIT pytest args (r8) — deliberately out of the guarded set:
#: the guard protects recursive suite runs (CI + just check), the r4
#: false-positive direction is the realistic hazard, and the two directions
#: are mutually exclusive at a session gate that cannot see invocation args.
#: Recorded, not silently dropped.
_NORECURSE_PATTERNS = (
    "*.egg",
    ".*",
    "_darcs",
    "build",
    "CVS",
    "dist",
    "node_modules",
    "venv",
    "{arch}",
    "__pycache__",
)


def _iter_test_files(tests_dir: Path):
    """Yield test files under ``tests_dir``, PRUNING norecursedirs during
    traversal exactly as pytest does (codex r9: post-filtering after a full
    ``rglob`` still walks a generated venv/build subtree on every session
    start; pruning skips the descent entirely)."""
    import os

    for dirpath, dirnames, filenames in os.walk(tests_dir):
        dirnames[:] = sorted(
            d for d in dirnames if not any(fnmatch(d, pat) for pat in _NORECURSE_PATTERNS)
        )
        for name in sorted(filenames):
            if any(fnmatch(name, pat) for pat in _TEST_FILE_PATTERNS):
                yield Path(dirpath) / name


def _package_anchored_module(member: Path, test_file: Path) -> str | None:
    """The dotted module path pytest derives for ``test_file``, or ``None``
    when the file's own directory is not a package.

    pytest anchors the module name at the OUTERMOST CONTIGUOUS package: walk
    UP from the file's parent while ``__init__.py`` exists (stopping at the
    member root, which is never a package in this src-layout workspace). A
    ``tests/`` root without ``__init__.py`` whose ``tests/integration/`` IS a
    package still collides across members as ``integration.test_x``
    (out-of-family round-2 probe: 2 of 3 functions collected). A file whose
    own parent is not a package gets a pytest-disambiguated unique module
    name — no collision possible (round-1 probe). The walk also stops at a
    directory whose name is not a valid Python identifier — pytest cannot
    treat it as a package segment, so the module anchors BELOW it and two
    members' ``tests/group-*/integration/test_x.py`` still collide as
    ``integration.test_x`` (out-of-family round-6 probe on pytest 9.0.3).
    """
    d = test_file.parent
    parts = [test_file.stem]
    while d != member and (d / "__init__.py").is_file() and d.name.isidentifier():
        parts.append(d.name)
        d = d.parent
    if len(parts) == 1:
        return None
    return ".".join(reversed(parts))


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
        for test_file in _iter_test_files(tests_dir):
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

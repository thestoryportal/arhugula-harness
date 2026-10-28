#!/usr/bin/env python3
"""WO-U06 / WP-04 — proportionate trial commits and changed-subject reuse (spec WS-07,
WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

Git's own pre-commit hook is the trial commit gate (`pre-commit --root`, run first by
`.githooks/pre-commit`), so a `git commit` reaches it however the command that makes it
is spelled, and the gate reads the index Git hands the hook rather than any shell text.
Git's own bypasses (`--no-verify`, another `core.hooksPath`) skip it; required CI still
runs. A worktree selects `trial` only where Git runs that hook. Legacy work exits 0 and
the existing hooks continue unchanged; a held selection holds. A trial commit must leave
staging explicit (`recorded_index`): Git records the repository's own index only when no
`-a`, `-i`, `--only`, pathspec or interactive mode built another, so only then is the
inspected index exactly what Git records.

`parse_staged` turns Git's listings into a `StagedScope`, and a staged path whose
worktree bytes differ from the index holds (`binding_stale`). `commit_obligations` names
the proportionate local set (WS-07): Ruff lint and format for each changed Python
subject, the behavior tests the commit still records of each changed or deleted Python
or shell subject (`tests_for`), the named risk expansion for hook and guard paths, the CI
record producers for any record path, and a parser for JSON records. A staged subject
with no behavior test is a `Gap` and holds. There is no whole-project Pyright, suite or
closeout. Stop runs the Ruff subset over the working tree.

Commit checks run in a private Git checkout of exactly the staged tree
(`index_snapshot`), so unstaged or untracked work neither reaches nor blocks them while a
check that asks Git still sees the commit's tree, and the index is observed again once
they finish: a change while they ran holds. Every check and checker probe receives only
`checker_environment`, the pinned variables its manifest records. Every check is keyed by
its WP-03 input manifest, which includes the observed checker identity (`Toolchain`, for
`uv run` checks the interpreter and every installed distribution) and that environment.
A stored passed receipt is reused only when `reuse_result` accepts it for the current
manifest, so an unchanged commit or turn runs nothing, while any material change runs
the check again; a concurrent identical check accepts the receipt that published first
on the same terms. Failed, unavailable or unreadable results are never reused as a pass.
Each checker runs under a subreaper that ends every descendant with it, including one that
left its process group or session, so no descendant outlives the result.

`worktree_profile` routes a worktree: only a unit bound through its Codex loop arc can
select `trial` (WP-02 `select_profile`). Until the coherent activation (WP-17) every unit
selects `legacy`, so this path is inactive.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Generator, Iterable, Mapping, Sequence
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

if __package__ in (None, ""):  # run as a script by the Stop hook
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.workflow_boundaries import ReasonCode, Result, observe_policy
from tools.workflow_evidence import (
    Checker,
    CheckRequest,
    EvidenceError,
    Index,
    InputManifest,
    WorkingTree,
    build_manifest,
    check_receipt,
    load_receipt,
    parse_classification,
    reuse_result,
)
from tools.workflow_policy import (
    CANONICAL_ROOT,
    SelectionFacts,
    WorkflowPolicy,
    read_activation,
    select_profile,
)

CHECK_ROOT = CANONICAL_ROOT / ".local" / "buford-loop" / "workflow-checks"
LOOP_STATE = Path(".harness/codex_loop_state.json")
RUFF_CONFIG = "pyproject.toml"
# The environment every `uv run` check resolves; hashed so a lock or interpreter change
# runs the check again. A missing file is recorded as deleted, not refused.
LOCKED_INPUTS = ("pyproject.toml", "uv.lock", ".python-version", "conftest.py")
# One commit's checks share this bound; a commit needing longer holds (`check_pending`)
# rather than keeping the agent's Bash command waiting without limit.
COMMIT_BUDGET_SECONDS = 110.0
# [LAW:single-enforcer] the directory whose pre-commit hook gates trial commits.
GATE_HOOKS = ".githooks"
# [LAW:one-source-of-truth] the only caller variables a check or probe receives, each
# pinned in the check's manifest, so a receipt describes the environment its checker ran
# in. BASH_ENV, interpreter, uv, pytest and Git variables never reach a check.
CHECK_VARIABLES = ("HOME", "LANG", "LC_ALL", "LC_CTYPE", "PATH", "TMPDIR")
_GITHUB_REMOTE = re.compile(r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?")

Scope = WorkingTree | Index


# --- routing -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Trial:
    unit: str
    repository: str
    policy: WorkflowPolicy


@dataclass(frozen=True)
class Legacy:
    """The existing hooks govern, unchanged."""


@dataclass(frozen=True)
class Held:
    reasons: tuple[str, ...]


Profile = Trial | Legacy | Held


def observe_repository(root: Path) -> str:
    """[LAW:effects-at-boundaries] the origin's owner/name, or the raw URL when it is not
    GitHub, so an unknown remote fails selection's repository match instead of passing."""
    url = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    match = _GITHUB_REMOTE.fullmatch(url)
    return match.group(1) if match else url


def loop_arc(raw: bytes | None) -> str | None:
    """The arc a worktree's Codex loop ledger names; absent ledger means no arc."""
    if raw is None:
        return None
    arc = json.loads(raw).get("arc_id")
    if not isinstance(arc, str) or not arc:
        raise ValueError(f"{LOOP_STATE}: arc_id must be a nonempty string")
    return arc


def worktree_profile(root: Path) -> Profile:
    """[LAW:single-enforcer] WP-02 `select_profile` decides every bound unit. A worktree
    with no loop arc has no unit and keeps the existing hooks, as does an arc a readable
    policy does not enroll. An arc whose enrollment cannot be read is selected under the
    arc's own name, which `select_profile` holds. Trial also needs Git to run the gate
    there; without it nothing would check the unit's commits."""
    policy = observe_policy()
    try:
        raw: bytes | None = (root / LOOP_STATE).read_bytes()
    except FileNotFoundError:
        raw = None
    arc = loop_arc(raw)
    if arc is None:
        return Legacy()
    unit = arc
    if isinstance(policy, WorkflowPolicy):
        member = next((entry for entry in policy.eligible_units if entry.arc == arc), None)
        if member is None:
            return Legacy()
        unit = member.unit
    repository = observe_repository(root)
    selection = select_profile(
        policy,
        SelectionFacts(
            repository=repository,
            unit=unit,
            arc=arc,
            trial_relation="unknown",
            admission="unknown",
            activation=read_activation(),
        ),
    )
    gated = gate_bound(root)
    match selection.kind:
        case "trial" if isinstance(policy, WorkflowPolicy) and gated:
            return Trial(unit, repository, policy)
        case "trial":
            return Held(("commit_gate_unbound",))
        case "legacy":
            return Legacy()
        case _:
            return Held(selection.reasons or ("policy_mismatch",))


def gate_bound(root: Path) -> bool:
    """[LAW:effects-at-boundaries] whether Git runs `root`'s `.githooks/pre-commit`: its
    hook directory, which follows core.hooksPath, is that one and the hook can run."""
    hooks = root / _git(root, "rev-parse", "--git-path", "hooks").decode("utf-8").strip()
    gate = root / GATE_HOOKS
    return hooks.resolve() == gate.resolve() and os.access(gate / "pre-commit", os.X_OK)


def repository_root(path: Path) -> Path | None:
    """[LAW:effects-at-boundaries] the top level of the repository containing `path`, so
    a commit spelled from a subdirectory routes by its worktree; None outside any."""
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    return Path(proc.stdout.strip()) if proc.returncode == 0 else None


def profile_at(path: Path) -> Profile:
    root = repository_root(path)
    return Legacy() if root is None else worktree_profile(root)


# --- staged scope ------------------------------------------------------------------------


@dataclass(frozen=True)
class StagedScope:
    """What a commit records: staged non-deleted paths, staged deletions, those staged
    paths whose worktree bytes differ from the index (WS-08: verified only by checking
    staged bytes), every path the index tracks, and the index's identity, a digest of
    every entry's mode, object and stage."""

    paths: tuple[str, ...]
    deleted: tuple[str, ...]
    divergent: tuple[str, ...]
    tracked: tuple[str, ...]
    index: str


def _z_fields(raw: bytes) -> list[str]:
    return [field.decode("utf-8") for field in raw.split(b"\0") if field]


def parse_staged(name_status: bytes, unstaged: bytes, stage: bytes) -> StagedScope:
    """The single checkpoint for Git's `-z` listings (`git diff --cached --name-status
    --no-renames -z`, `git diff --name-only -z` and `git ls-files --stage -z`)."""
    fields = _z_fields(name_status)
    if len(fields) % 2:
        raise ValueError("staged listing: status without a path")
    entries = list(zip(fields[::2], fields[1::2], strict=True))
    paths = tuple(path for status, path in entries if status != "D")
    worktree_changed = set(_z_fields(unstaged))
    return StagedScope(
        paths,
        tuple(path for status, path in entries if status == "D"),
        tuple(path for path in paths if path in worktree_changed),
        tuple(dict.fromkeys(row.split("\t", 1)[1] for row in _z_fields(stage))),
        hashlib.sha256(stage).hexdigest(),
    )


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def observe_staged(root: Path) -> StagedScope:
    """[LAW:effects-at-boundaries] the actual index and worktree state, never a command's
    spelling."""
    return parse_staged(
        _git(root, "diff", "--cached", "--name-status", "--no-renames", "-z"),
        _git(root, "diff", "--name-only", "-z"),
        _git(root, "ls-files", "--stage", "-z"),
    )


def changed_worktree_paths(root: Path) -> tuple[str, ...]:
    """Stop's subjects: tracked changes against HEAD, deletions excluded, plus genuine
    untracked files."""
    tracked = _z_fields(_git(root, "diff", "--name-only", "--diff-filter=d", "-z", "HEAD"))
    untracked = _z_fields(_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
    return tuple(sorted(set(tracked) | set(untracked)))


def recorded_index(root: Path, index_file: str | None) -> Outcome:
    """[LAW:single-enforcer] staging stays explicit (WS-07). Git names the index it will
    record in GIT_INDEX_FILE, relative to the worktree top, or leaves it unset outside a
    hook; it is the repository's own index only for a commit of exactly what was staged."""
    own = Path(_git(root, "rev-parse", "--absolute-git-dir").decode("utf-8").strip()) / "index"
    recorded = own if index_file is None else root / index_file
    if recorded.resolve() == own.resolve():
        return PASSED
    return Outcome(
        "held",
        ("invalid_input",),
        (
            f"staging stays explicit: this commit records {recorded.name}, not the staged "
            "index; stage the paths, then commit without -a, -i, -o, -p or a pathspec",
        ),
    )


@contextmanager
def index_snapshot(root: Path, environment: Mapping[str, str]) -> Generator[Path]:
    """[LAW:effects-at-boundaries] a private Git checkout of exactly the tree the commit
    records, at the root's HEAD with its origin, so a check that reads files or asks Git
    (`ls-files`, `grep --cached`, `diff --cached`) sees the staged bytes and no unstaged
    or untracked work. It borrows the root's objects and writes no root ref or worktree;
    its own Git commands get `environment`, never the hook's GIT_DIR or GIT_INDEX_FILE."""
    tree = _git(root, "write-tree").decode("utf-8").strip()
    head = _git(root, "rev-parse", "--verify", "HEAD").decode("utf-8").strip()
    objects = root / _git(root, "rev-parse", "--git-path", "objects").decode("utf-8").strip()
    origin = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"], capture_output=True, text=True
    )
    with tempfile.TemporaryDirectory(prefix="workflow-commit-") as directory:
        snapshot = Path(directory)

        def inside(*args: str) -> None:
            subprocess.run(
                ["git", "-C", directory, *args], env=dict(environment), capture_output=True,
                check=True,
            )  # fmt: skip

        inside("init", "-q")
        (snapshot / ".git" / "objects" / "info" / "alternates").write_text(f"{objects.resolve()}\n")
        inside("read-tree", tree)
        inside("checkout-index", "--all")
        inside("update-ref", "--no-deref", "HEAD", head)
        for url in [origin.stdout.strip()] if origin.returncode == 0 else []:
            inside("remote", "add", "origin", url)
        yield snapshot


# --- obligations -------------------------------------------------------------------------


@dataclass(frozen=True)
class Check:
    """One checker execution. `subject`, when set, is fed on stdin as the scope's exact
    bytes; every other input is read from the directory it runs in. Exit 0 passes, 1
    reports findings, anything else means it could not decide."""

    name: str
    version: str
    argv: tuple[str, ...]
    subject: str | None
    domains: tuple[str, ...]
    explicit: tuple[str, ...]
    timeout: float


@dataclass(frozen=True)
class Gap:
    """A required local check that cannot be formed; it holds until supplied."""

    detail: str


Obligation = Check | Gap


@dataclass(frozen=True)
class Toolchain:
    """The checker environment, observed once per gate: the project `uv run` uses, the
    Ruff command, and the identity of Ruff, Bash and the `uv run` environment (uv, its
    interpreter and installed distributions). An identity is None when it could not be
    observed, which makes each check needing it a `Gap`."""

    project: Path
    ruff_argv: tuple[str, ...]
    ruff: str | None
    bash: str | None
    python: str | None


# Run by the `uv run` interpreter in isolated mode: its version and a digest of the bytes
# of every file under its environment and import path, so reinstalling or editing pytest,
# a plugin, any dependency or an editable source it imports changes the checker identity.
# [LAW:one-source-of-truth] the files themselves, not RECORD's install-time account of
# them; bytecode caches are derived from them and written by every run.
ENVIRONMENT_PROBE = """\
import hashlib, os, platform, sys

def files(root):
    if os.path.isfile(root):
        yield root
    for top, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        yield from (os.path.join(top, name) for name in sorted(names))

paths = sorted({os.path.realpath(p) for p in (sys.prefix, *sys.path)})
digest = hashlib.sha256()
for root in [r for r in paths if not any(r.startswith(o + os.sep) for o in paths)]:
    for path in files(root):
        with open(path, "rb") as handle:
            content = hashlib.file_digest(handle, "sha256").hexdigest()
        digest.update(f"{os.path.relpath(path, root)}\\0{content}\\n".encode())
print(f"Python {platform.python_version()}; environment sha256:{digest.hexdigest()}")
"""


def uv_prefix(project: Path) -> tuple[str, ...]:
    """`uv run` in `project`'s environment, unsynced: commit checks run from an index
    snapshot, which `uv` must neither adopt as a project nor sync from."""
    return ("uv", "run", "--quiet", "--project", str(project), "--no-sync")


# [LAW:one-source-of-truth] a fenced copy of the record producers CI runs
# (.github/workflows/ci.yml); a test asserts each still appears there.
RECORD_PRODUCERS: tuple[tuple[str, ...], ...] = (
    ("tools/substitution_ledger.py", "--check"),
    ("tools/claude_md_citation_resolver.py", "--check"),
    ("tools/arc_ledger.py", "--check"),
    ("tools/forward_register.py", "--check"),
    ("tools/roadmap_status_refresh.py", "--check"),
    ("tools/semantic_overlay/overlay.py", "check"),
    ("tools/qa_evidence_matrix.py", "--check"),
    ("tools/closure_gate.py", "--check"),
    ("tools/merge_gate_log.py", "check"),
    ("tools/clearance_frontmatter.py", "--check"),
    ("tools/artifact_heads.py", "--check"),
    ("tools/artifact_heads.py", "--check-completeness"),
)
# Named higher-risk subjects and the local tests they add (WS-07 explicit expansion).
RISK_EXPANSIONS: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "hook and guard parity",
        (".codex/", ".claude/", ".githooks/", "tools/hooks/"),
        ("tools/test_codex_workflow_parity.py",),
    ),
)
_SOURCE_SUFFIXES = (".py", ".sh")
_TEST_FILES = (":(glob)**/test_*.py", ":(glob)**/test_*.sh")


def _top(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else ""


def source_subjects(paths: Sequence[str]) -> tuple[str, ...]:
    return tuple(path for path in paths if path.endswith(_SOURCE_SUFFIXES))


def changed_subjects(staged: StagedScope) -> tuple[str, ...]:
    """[LAW:one-source-of-truth] the source subjects a commit changes, deletions included:
    removing a source can break the tests that remain, so they run as its behavior check."""
    return source_subjects((*staged.paths, *staged.deleted))


def behavior_tests(path: str, tracked: Sequence[str]) -> tuple[str, ...]:
    """A source subject's sibling tests the index records: itself when it is a test,
    otherwise every tracked `test_<name>` under the same top-level directory."""
    name = PurePosixPath(path).name
    if name.startswith("test_"):
        return tuple(test for test in tracked if test == path)
    wanted = "test_" + name.replace("-", "_")
    return tuple(t for t in tracked if PurePosixPath(t).name == wanted and _top(t) == _top(path))


def subject_terms(path: str) -> tuple[str, ...]:
    """What a test names to exercise a subject: its file name and, for Python, its dotted
    module (`*/src/pkg/x.py` is `pkg.x`)."""
    pure = PurePosixPath(path)
    parts = pure.with_suffix("").parts
    parts = parts[parts.index("src") + 1 :] if "src" in parts else parts
    module = ".".join(parts[:-1] if parts[-1:] == ("__init__",) else parts)
    return (pure.name, module) if pure.suffix == ".py" and module else (pure.name,)


def risk_tests(path: str) -> tuple[str, ...]:
    return tuple(
        test
        for _, prefixes, added in RISK_EXPANSIONS
        if path.startswith(prefixes)
        for test in added
    )


def tests_for(
    path: str, tracked: Sequence[str], naming: Mapping[str, Sequence[str]]
) -> tuple[str, ...]:
    """[LAW:single-enforcer] a source subject's behavior tests: its siblings, every staged
    test naming its file or module (`naming`, from `observe_naming`), and its named risk
    expansion. Only an empty union is a gap."""
    return tuple(
        dict.fromkeys(
            [
                *behavior_tests(path, tracked),
                *(test for term in subject_terms(path) for test in naming[term]),
                *risk_tests(path),
            ]
        )
    )


def observe_naming(root: Path, terms: Iterable[str]) -> dict[str, tuple[str, ...]]:
    """[LAW:effects-at-boundaries] for each term, the staged test files that contain it."""
    return {term: _staged_tests_naming(root, term) for term in dict.fromkeys(terms)}


def _staged_tests_naming(root: Path, term: str) -> tuple[str, ...]:
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "grep",
            "--cached",
            "-l",
            "-z",
            "-F",
            "-e",
            term,
            "--",
            *_TEST_FILES,
        ],
        capture_output=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise OSError(f"git grep {term!r} in {root}: {proc.stderr.decode('utf-8', 'replace')}")
    return tuple(_z_fields(proc.stdout))


def _uv_check(
    name: str,
    toolchain: Toolchain,
    argv: tuple[str, ...],
    subject: str | None,
    domains: tuple[str, ...],
    explicit: tuple[str, ...],
    timeout: float,
) -> Obligation:
    """A check `uv run` executes, identified by the environment it resolves."""
    if toolchain.python is None:
        return Gap(f"{name}: the uv interpreter identity is unavailable")
    argv = (*uv_prefix(toolchain.project), *argv)
    return Check(name, toolchain.python, argv, subject, domains, explicit, timeout)


def _test_check(test: str, code_roots: tuple[str, ...], toolchain: Toolchain) -> Obligation:
    explicit = tuple(sorted({*LOCKED_INPUTS, test}))
    if test.endswith(".py"):
        argv = ("pytest", "-q", "-p", "no:cacheprovider", test)
        return _uv_check("pytest", toolchain, argv, None, code_roots, explicit, 100.0)
    if toolchain.bash is None:
        return Gap(f"{test}: the bash version is unavailable")
    return Check("bash-test", toolchain.bash, ("bash", test), None, code_roots, explicit, 60.0)


def ruff_obligations(paths: Sequence[str], toolchain: Toolchain) -> tuple[Obligation, ...]:
    """Ruff lint and format over each changed Python subject's exact bytes."""
    subjects = [path for path in paths if path.endswith(".py")]
    if subjects and toolchain.ruff is None:
        return (Gap("ruff is unavailable"),)
    return tuple(
        Check(
            name,
            str(toolchain.ruff),
            (*toolchain.ruff_argv, *args, "--config", RUFF_CONFIG, "--stdin-filename", path, "-"),
            path,
            (),
            (path, RUFF_CONFIG),
            30.0,
        )
        for path in subjects
        for name, args in (
            ("ruff-check", ("check", "--quiet", "--output-format=concise")),
            ("ruff-format", ("format", "--check")),
        )
    )


def _record_check(producer: tuple[str, ...], toolchain: Toolchain) -> Obligation:
    name = f"record-{PurePosixPath(producer[0]).stem}"
    return _uv_check(name, toolchain, ("python", *producer), None, (".",), LOCKED_INPUTS, 60.0)


def _json_check(path: str, toolchain: Toolchain) -> Obligation:
    lines = ("--json-lines",) if path.endswith(".jsonl") else ()
    argv = ("python", "-m", "json.tool", *lines)
    return _uv_check("json", toolchain, argv, path, (), LOCKED_INPUTS, 30.0)


def commit_obligations(
    staged: StagedScope,
    policy: WorkflowPolicy,
    toolchain: Toolchain,
    naming: Mapping[str, Sequence[str]],
) -> tuple[Obligation, ...]:
    """[LAW:single-enforcer] the one place WS-07's proportionate local set is decided for
    a staged scope; required CI stays a later gate. A record under a risk prefix adds its
    expansion, and a deletion can orphan any record reference, so it runs the record
    producers. Only a staged subject can lack a test: a deleted one runs whatever tests of
    it remain."""
    code_roots = parse_classification(policy.rules["artifact_roots"]).code_roots
    tests = {path: tests_for(path, staged.tracked, naming) for path in changed_subjects(staged)}
    records = [path for path in staged.paths if not path.endswith(_SOURCE_SUFFIXES)]
    selected = [
        *(test for found in tests.values() for test in found),
        *(test for path in records for test in risk_tests(path)),
    ]
    return (
        *ruff_obligations(staged.paths, toolchain),
        *(
            Gap(f"{path}: no behavior test names it")
            for path in source_subjects(staged.paths)
            if not tests[path]
        ),
        *(_test_check(test, code_roots, toolchain) for test in dict.fromkeys(selected)),
        *(_record_check(p, toolchain) for p in RECORD_PRODUCERS if records or staged.deleted),
        *(_json_check(path, toolchain) for path in records if path.endswith((".json", ".jsonl"))),
    )


# --- checks ------------------------------------------------------------------------------


@dataclass(frozen=True)
class Outcome:
    result: Result
    reasons: tuple[ReasonCode, ...]
    detail: tuple[str, ...]


PASSED = Outcome("passed", (), ())
_SEVERITY: tuple[Result, ...] = ("error", "failed", "held", "passed")


def combine(outcomes: Sequence[Outcome]) -> Outcome:
    """The most severe result, keeping every reason and detail line."""
    levels = {"passed", *(o.result for o in outcomes)}
    return Outcome(
        next(level for level in _SEVERITY if level in levels),
        tuple(dict.fromkeys(r for o in outcomes for r in o.reasons)),
        tuple(line for o in outcomes for line in o.detail),
    )


Runner = Callable[
    [Sequence[str], bytes, Path, float, Mapping[str, str]], subprocess.CompletedProcess[bytes]
]
Clock = Callable[[], float]


def checker_environment(source: Mapping[str, str]) -> dict[str, str]:
    """The `CHECK_VARIABLES` that `source` sets: everything a check receives."""
    return {name: source[name] for name in CHECK_VARIABLES if name in source}


# Run by the gate's interpreter in isolated mode as each checker's parent: a child
# subreaper, so every descendant that leaves the checker's process group or session is
# re-parented here rather than to init. It runs the checker with exactly the given
# environment, ends it at its timeout, then kills and reaps every descendant still
# alive before reporting the checker's status. It cannot decide (125) if it cannot
# become a subreaper.
SUPERVISOR = """\
import ctypes, json, os, signal, subprocess, sys

def children():
    me = str(os.getpid())
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            with open(f"/proc/{pid}/stat") as stat:
                parent = stat.read().rsplit(")", 1)[1].split()[1]
        except (FileNotFoundError, ProcessLookupError):
            continue  # a process that exited after the listing
        if parent == me:
            yield int(pid)

def finish(code, message):
    print(message, file=sys.stderr)
    sys.exit(code)

PR_SET_CHILD_SUBREAPER = 36
libc = ctypes.CDLL(None, use_errno=True)
if not hasattr(libc, "prctl") or libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) != 0:
    finish(125, f"checker supervisor: no subreaper: {os.strerror(ctypes.get_errno())}")
environment, timeout, argv = json.loads(sys.argv[1]), float(sys.argv[2]), sys.argv[3:]
try:
    checker = subprocess.Popen(argv, env=environment)
except OSError as exc:
    finish(127, str(exc))
try:
    code = checker.wait(timeout)
except subprocess.TimeoutExpired:
    code = None
# Our children are only the checker and descendants re-parented to us; each stays
# ours, so its PID stays valid, until the waitpid below reaps it.
while left := list(children()):
    for pid in left:
        os.kill(pid, signal.SIGKILL)
    os.waitpid(-1, 0)
if code is None:
    finish(124, "checker timed out")
sys.exit(code if code >= 0 else 128 - code)
"""
# The supervisor's own start and sweep beyond the checker's timeout; past it the
# supervisor itself is ended and the check is undecided.
SUPERVISOR_GRACE_SECONDS = 10.0


def run_bounded(
    argv: Sequence[str], stdin: bytes, cwd: Path, timeout: float, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[bytes]:
    """[LAW:effects-at-boundaries] one checker in `cwd` with exactly `environment`, under
    `SUPERVISOR`, so nothing the checker started outlives its result. A timeout or a
    missing executable is an undecided result, never a pass."""
    supervised = [sys.executable, "-I", "-c", SUPERVISOR, json.dumps(dict(environment))]
    try:
        proc = subprocess.Popen(
            [*supervised, str(timeout), *argv],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=dict(environment),
            start_new_session=True,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(list(argv), 127, b"", str(exc).encode())
    with proc:
        try:
            stdout, stderr = proc.communicate(stdin, timeout=timeout + SUPERVISOR_GRACE_SECONDS)
            result = subprocess.CompletedProcess(list(argv), proc.returncode, stdout, stderr)
        except subprocess.TimeoutExpired:
            result = subprocess.CompletedProcess(
                list(argv), 124, b"", b"checker supervisor did not finish"
            )
        finally:
            # [LAW:no-ambient-temporal-coupling] the supervisor's group ends here, not
            # whenever its members do; an empty group is already ended.
            with suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGKILL)
    return result


def ruff_command(project: Path) -> tuple[str, ...]:
    return ("ruff",) if shutil.which("ruff") else (*uv_prefix(project), "ruff")


def _first_line(proc: subprocess.CompletedProcess[bytes]) -> str | None:
    lines = proc.stdout.decode("utf-8", "replace").strip().splitlines()
    return lines[0] if proc.returncode == 0 and lines else None


def observe_toolchain(root: Path, run: Runner, environment: Mapping[str, str]) -> Toolchain:
    """[LAW:effects-at-boundaries] each checker's identity, probed from `root` in the
    environment the checks receive."""
    ruff_argv = ruff_command(root)

    def probe(*argv: str) -> str | None:
        return _first_line(run(argv, b"", root, 30.0, environment))

    uv = probe("uv", "--version")
    python = probe(*uv_prefix(root), "python", "-I", "-c", ENVIRONMENT_PROBE)
    return Toolchain(
        root,
        ruff_argv,
        probe(*ruff_argv, "--version"),
        probe("bash", "--version"),
        None if uv is None or python is None else f"{uv}; {python}",
    )


def _subject_bytes(root: Path, scope: Scope, path: str) -> bytes:
    match scope:
        case WorkingTree():
            return (root / path).read_bytes()
        case Index():
            return _git(root, "show", f":{path}")


def _receipt_path(manifest: InputManifest) -> Path:
    name = f"{manifest.unit}.{manifest.checker.name}.{manifest.head[:12]}.{manifest.key[:16]}"
    return CHECK_ROOT / f"{name}.json"


def publish_receipt(path: Path, record: dict[str, object]) -> None:
    """[LAW:effects-at-boundaries] WS-08 §10.3: private bytes, fsync, a no-overwrite
    atomic link, a directory sync and a hash readback; any failure raises."""
    raw = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink()
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(raw).digest():
        raise OSError(f"{path}: readback differs from the published bytes")


def stored_pass(stored: Path, manifest: InputManifest) -> bool:
    """[LAW:single-enforcer] whether the receipt stored for `manifest` passes it."""
    try:
        raw = stored.read_bytes()
    except FileNotFoundError:
        return False
    return reuse_result(load_receipt(raw), manifest).reusable


def run_check(
    root: Path,
    trial: Trial,
    scope: Scope,
    check: Check,
    cwd: Path,
    *,
    created_at: str,
    environment: Mapping[str, str],
    run: Runner,
    timeout: float,
) -> Outcome:
    """One check: reuse an accepted identical result, otherwise run it in `cwd`, which
    holds exactly the scope's files, with exactly `environment`, and publish a passed
    receipt for later reuse."""
    label = check.subject or " ".join(check.argv)
    request = CheckRequest(
        unit=trial.unit,
        repository=trial.repository,
        scope=scope,
        policy=trial.policy,
        checker=Checker(check.name, check.version, check.argv),
        domains=check.domains,
        explicit=tuple(sorted({*check.explicit, *([check.subject] if check.subject else [])})),
        environment=environment,
        material_base=None,
        closure="declared",
    )
    try:
        manifest = build_manifest(root, request)
    except (EvidenceError, subprocess.CalledProcessError) as exc:
        return Outcome("held", ("invalid_input",), (f"{label}: inputs unobservable: {exc}",))
    if manifest.refusals:
        codes = ", ".join(r.code for r in manifest.refusals)
        return Outcome("held", ("identity_mismatch",), (f"{label}: inputs refused: {codes}",))
    stored = _receipt_path(manifest)
    if stored_pass(stored, manifest):
        return PASSED
    if timeout <= 0:
        return Outcome("held", ("check_pending",), (f"{label}: commit check budget exhausted",))
    content = b"" if check.subject is None else _subject_bytes(root, scope, check.subject)
    entry = next((e for e in manifest.files if e.path == check.subject), None)
    # [LAW:single-enforcer] the checker sees only the bytes the manifest identified; an
    # edit between observation and execution invalidates the binding.
    if entry is not None and hashlib.sha256(content).hexdigest() != entry.sha256:
        return Outcome("held", ("binding_stale",), (f"{label}: changed while being checked",))
    proc = run(check.argv, content, cwd, timeout, environment)
    output = (proc.stdout + proc.stderr).decode("utf-8", "replace").strip()[-2000:]
    if proc.returncode == 1:
        return Outcome("failed", ("check_failed",), (f"{label}: {check.name}: {output}",))
    if proc.returncode != 0:
        return Outcome(
            "held", ("check_pending",), (f"{label}: {check.name} could not decide: {output}",)
        )
    record = check_receipt(
        manifest,
        record_id=stored.stem,
        producer={"tool": "workflow_commit", "version": "3"},
        created_at=created_at,
        result="passed",
        artifacts=[],
    )
    try:
        publish_receipt(stored, record)
    except FileExistsError:
        # A concurrent identical check published first and the link never overwrites;
        # its receipt is the stored result, accepted only as any stored one is.
        if not stored_pass(stored, manifest):
            return Outcome(
                "error", ("publication_uncertain",), (f"{label}: {stored} does not verify it",)
            )
    except OSError as exc:
        return Outcome("error", ("publication_uncertain",), (f"{label}: receipt: {exc}",))
    return PASSED


def run_obligations(
    root: Path,
    trial: Trial,
    scope: Scope,
    obligations: Sequence[Obligation],
    cwd: Path,
    *,
    created_at: str,
    environment: Mapping[str, str],
    run: Runner,
    clock: Clock,
) -> Outcome:
    """Every obligation in order within one time budget, each run in `cwd`; a Gap holds."""
    deadline = clock() + COMMIT_BUDGET_SECONDS
    outcomes: list[Outcome] = []
    for obligation in obligations:
        match obligation:
            case Gap(detail=detail):
                outcomes.append(Outcome("held", ("check_pending",), (detail,)))
            case Check() as check:
                remaining = min(check.timeout, deadline - clock())
                outcomes.append(
                    run_check(
                        root,
                        trial,
                        scope,
                        check,
                        cwd,
                        created_at=created_at,
                        environment=environment,
                        run=run,
                        timeout=remaining,
                    )
                )
    return combine(outcomes)


def rebound(before: StagedScope, after: StagedScope) -> Outcome:
    """[LAW:single-enforcer] the checks describe the index observed before them; a change
    to it, or to which staged paths the worktree differs from, while they ran voids that
    binding."""
    if (after.index, after.divergent) == (before.index, before.divergent):
        return PASSED
    return Outcome(
        "held",
        ("binding_stale",),
        ("the index or a staged path changed while the commit checks ran; commit again",),
    )


def commit_outcome(
    root: Path,
    trial: Trial,
    *,
    created_at: str,
    environment: Mapping[str, str],
    run: Runner = run_bounded,
    clock: Clock = time.monotonic,
) -> Outcome:
    """The trial commit gate: the actual staged scope, its proportionate checks over a
    snapshot of exactly that index, then the index observed again."""
    staged = observe_staged(root)
    if staged.divergent:
        return Outcome(
            "held",
            ("binding_stale",),
            tuple(
                f"{path}: worktree differs from the index; restage it or check the staged bytes"
                for path in staged.divergent
            ),
        )
    terms = (term for path in changed_subjects(staged) for term in subject_terms(path))
    toolchain = observe_toolchain(root, run, environment)
    obligations = commit_obligations(staged, trial.policy, toolchain, observe_naming(root, terms))
    with index_snapshot(root, environment) as snapshot:
        checked = run_obligations(
            root, trial, Index(), obligations, snapshot,
            created_at=created_at, environment=environment, run=run, clock=clock,
        )  # fmt: skip
    return combine([checked, rebound(staged, observe_staged(root))])


def stop_outcome(
    root: Path,
    trial: Trial,
    *,
    created_at: str,
    environment: Mapping[str, str],
    run: Runner = run_bounded,
    clock: Clock = time.monotonic,
) -> Outcome:
    """Stop stays lint-only: Ruff over the changed working-tree subjects."""
    toolchain = observe_toolchain(root, run, environment)
    obligations = ruff_obligations(changed_worktree_paths(root), toolchain)
    return run_obligations(
        root, trial, WorkingTree(), obligations, root,
        created_at=created_at, environment=environment, run=run, clock=clock,
    )  # fmt: skip


def pre_commit_outcome(
    root: Path, profile: Profile, index_file: str | None, *, created_at: str,
    environment: Mapping[str, str],
) -> Outcome:  # fmt: skip
    """The trial commit gate Git runs before recording `root`'s commit."""
    match profile:
        case Legacy():
            return PASSED
        case Held(reasons=reasons):
            return Outcome(
                "held", ("policy_mismatch",), (f"trial selection held: {', '.join(reasons)}",)
            )
        case Trial() as trial:
            staging = recorded_index(root, index_file)
            if staging.result != "passed":
                return staging
            return commit_outcome(root, trial, created_at=created_at, environment=environment)


# --- CLI (Stop and pre-commit hooks) ---------------------------------------------------


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# [LAW:one-source-of-truth] the spec's check exit contract (WS-06), shared by the gate.
EXIT_CODES: Mapping[Result, int] = {"passed": 0, "held": 3, "failed": 4, "error": 5}


def main(argv: list[str]) -> int:
    """`stop --root <dir>`: one JSON object naming the profile and, for trial work, the
    outcome; legacy output tells the caller to run its existing gate unchanged.
    `pre-commit --root <dir>`: Git's hook gate; the exit code is the outcome (0 passed or
    legacy, 3 held, 4 failed, 5 error, 2 usage) and stderr explains anything else."""
    if len(argv) != 3 or argv[0] not in ("stop", "pre-commit") or argv[1] != "--root":
        print("usage: workflow_commit.py stop|pre-commit --root <dir>", file=sys.stderr)
        return 2
    root = Path(argv[2]).resolve()
    profile = worktree_profile(root)
    environment = checker_environment(os.environ)
    if argv[0] == "pre-commit":
        outcome = pre_commit_outcome(
            root, profile, os.environ.get("GIT_INDEX_FILE"), created_at=now(),
            environment=environment,
        )  # fmt: skip
        if outcome.result != "passed":
            print(
                "\n".join((*outcome.detail, f"reason_codes: {', '.join(outcome.reasons)}")),
                file=sys.stderr,
            )
        return EXIT_CODES[outcome.result]
    match profile:
        case Legacy():
            output: dict[str, object] = {"profile": "legacy"}
        case Held(reasons=reasons):
            output = {
                "profile": "held",
                "result": "held",
                "reason_codes": list(reasons),
                "detail": [],
            }
        case Trial():
            outcome = stop_outcome(root, profile, created_at=now(), environment=environment)
            output = {
                "profile": "trial",
                "result": outcome.result,
                "reason_codes": list(outcome.reasons),
                "detail": list(outcome.detail),
            }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

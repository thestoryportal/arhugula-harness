#!/usr/bin/env python3
"""WO-U06 / WP-04 — proportionate trial commits and changed-subject reuse (spec WS-07,
WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

`read_commits` finds every commit a Bash command can make — through `git -C`, `cd`,
subshells, wrappers and aliases — and reports a command whose commit effect it cannot
identify as `Unreadable`, which holds trial work. Each commit is routed by its repository
top level: legacy work keeps the existing hooks unchanged, a held selection holds, and a
trial commit must leave staging explicit (`commit_selection`), because only then is the
inspected index exactly what Git records.

A trial commit is checked over that index: `parse_staged` turns Git's listings into a
`StagedScope`, and a staged path whose worktree bytes differ from the index holds
(`binding_stale`). `commit_obligations` names the proportionate local set (WS-07):
Ruff lint and format for each changed Python subject, the sibling behavior test of each
changed Python or shell subject, the named risk expansion for hook and guard paths, the
CI record producers for any record path, and a parser for JSON records. A subject with
no behavior test is a `Gap` and holds. There is no whole-project Pyright, suite or
closeout. Stop runs the Ruff subset over the working tree.

Every check is keyed by its WP-03 input manifest and runs from the repository root. A
stored passed receipt is reused only when `reuse_result` accepts it for the current
manifest, so an unchanged commit or turn runs nothing, while any material change runs
the check again. A check that reads the working tree holds when an unstaged or untracked
path falls in its inputs, so a receipt never describes bytes the commit does not record.
Failed, unavailable or unreadable results are never reused as a pass.

`worktree_profile` routes a worktree: only a unit bound through its Codex loop arc can
select `trial` (WP-02 `select_profile`). Until the coherent activation (WP-17) every unit
selects `legacy`, so this path is inactive.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Iterator, Sequence
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
# Below the pre-commit hook's 130 s timeout, so the gate decides before Codex gives up.
COMMIT_BUDGET_SECONDS = 110.0
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
    arc's own name, which `select_profile` holds."""
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
    match selection.kind:
        case "trial" if isinstance(policy, WorkflowPolicy):
            return Trial(unit, repository, policy)
        case "legacy":
            return Legacy()
        case _:
            return Held(selection.reasons or ("policy_mismatch",))


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


# --- commit commands ---------------------------------------------------------------------


@dataclass(frozen=True)
class CommitCommand:
    """A `git commit` the command runs: its working directory and its arguments."""

    root: Path
    args: tuple[str, ...]


@dataclass(frozen=True)
class Unreadable:
    """The command may commit, but where or how cannot be determined from its text."""

    reason: str


AliasLookup = Callable[[Path, str], str | None]
_HEREDOC = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z0-9_.-]+)\2")
_ASSIGNMENT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=")
_GIT_INSIDE = re.compile(r"(?:\$\(|`|&&|;|\|)\s*(?:\S*/)?git(?:\s|$)")
_GIT_WORD = re.compile(r"(?:^|[\s/])git(?:\s|$)")
# Programs that run their arguments unchanged in this shell's directory.
_WRAPPERS = frozenset({"rtk", "command", "exec", "nohup", "time"})
# Programs that run a command assembled from their arguments, where this reader cannot
# follow the directory or the expansion.
_RUNNERS = frozenset(
    {"xargs", "timeout", "sh", "bash", "zsh", "dash", "eval", "find", "nice", "sudo"}
    | {"watch", "parallel", "script", "flock", "stdbuf", "ionice", "setsid", "env"}
)
_GIT_FLAGS = frozenset(
    {"--no-pager", "-P", "-p", "--paginate", "--no-optional-locks", "--literal-pathspecs"}
    | {"--no-replace-objects", "--noglob-pathspecs"}
)
_ALIAS_DEPTH = 8


def strip_heredocs(text: str) -> str | None:
    """`text` without here-document bodies, which are data rather than commands; None
    when a body never reaches its terminator."""
    lines: list[str] = []
    pending: list[tuple[str, bool]] = []
    quote = ""
    for line in text.split("\n"):
        if pending:
            delimiter, tabs = pending[0]
            if (line.lstrip("\t") if tabs else line) == delimiter:
                pending.pop(0)
            continue
        lines.append(line)
        quote = _scan_heredocs(line, quote, pending)
    return None if pending else "\n".join(lines)


def _scan_heredocs(line: str, quote: str, pending: list[tuple[str, bool]]) -> str:
    """Append each `<<` operator outside single quotes to `pending`; return the quote
    still open at the end of the line. Double quotes do not hide one, because a
    here-document inside `"$(...)"` is still read by the shell."""
    index = 0
    while index < len(line):
        char = line[index]
        if quote == "'":
            quote = "" if char == "'" else quote
        elif char == "\\":
            index += 1
        elif quote == '"' and char == '"':
            quote = ""
        elif not quote and char in "'\"":
            quote = char
        elif line.startswith("<<", index) and not line.startswith("<<<", index):
            match = _HEREDOC.match(line, index)
            if match:
                pending.append((match.group(3), match.group(1) == "-"))
                index = match.end() - 1
        index += 1
    return quote


def _tokens(text: str) -> list[str]:
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()<>\n")
    lexer.whitespace = " \t\r"
    lexer.commenters = ""
    lexer.whitespace_split = True
    return list(lexer)


def _program(word: str) -> str:
    return PurePosixPath(word).name


def _moved(cwd: Path | None, target: str) -> Path | None:
    if "$" in target or "`" in target or target.startswith("~") or target == "-":
        return None
    return Path(target) if target.startswith("/") else None if cwd is None else cwd / target


def _git_command(
    words: list[str], cwd: Path | None, aliases: AliasLookup, depth: int = 0
) -> tuple[CommitCommand, ...] | Unreadable:
    """`words` after the `git` program: its global options, then the subcommand."""
    root, rest = cwd, iter(words)
    for word in rest:
        if word == "-C":
            root = _moved(root, next(rest, "$"))
        elif word == "-c":
            if next(rest, "").lower().startswith("alias."):
                return Unreadable("an alias defined on the command line")
        elif word in _GIT_FLAGS:
            continue
        elif word.startswith("-"):
            return Unreadable(f"git option {word!r} can change what is committed")
        elif root is None:
            return Unreadable("git runs in a directory that cannot be determined")
        elif word == "commit":
            return (CommitCommand(root, tuple(rest)),)
        else:
            expansion = aliases(root, word)
            if expansion is None:
                return ()
            if expansion.startswith("!"):
                runs_git = _GIT_WORD.search(expansion[1:]) or "commit" in expansion
                return Unreadable(f"shell alias {word!r} runs git") if runs_git else ()
            if depth >= _ALIAS_DEPTH:
                return Unreadable(f"alias {word!r} nests too deeply")
            try:
                expanded = shlex.split(expansion)
            except ValueError:
                return Unreadable(f"alias {word!r} is not readable")
            return _git_command([*expanded, *rest], root, aliases, depth + 1)
    return ()


def _simple_command(
    words: list[str], cwd: Path | None, aliases: AliasLookup
) -> tuple[Path | None, tuple[CommitCommand, ...] | Unreadable]:
    """One simple command: the directory after it, and the commits it makes."""
    if any(_GIT_INSIDE.search(word) for word in words):
        return cwd, Unreadable("git runs inside a substitution or a quoted command")
    index = 0
    while index < len(words):
        assignment = _ASSIGNMENT.match(words[index])
        if assignment and assignment.group(1).startswith("GIT_"):
            return cwd, Unreadable(f"{assignment.group(1)} changes how git commits")
        program, following = _program(words[index]), "".join(words[index + 1 : index + 2])
        # `env` with only assignments is a wrapper; with options it is a runner.
        if (
            assignment
            or program in _WRAPPERS
            or (program == "env" and not following.startswith("-"))
        ):
            index += 1
            continue
        break
    program, arguments = (_program(words[index]), words[index + 1 :]) if words[index:] else ("", [])
    if program in {"cd", "pushd"}:
        return (_moved(cwd, arguments[0]) if len(arguments) == 1 else None), ()
    if program == "popd":
        return None, ()
    if program == "git":
        return cwd, _git_command(arguments, cwd, aliases)
    if program in _RUNNERS and any(_GIT_WORD.search(word) for word in arguments):
        return cwd, Unreadable(f"{program} runs a git command this reader cannot follow")
    return cwd, ()


def read_commits(
    command: str, cwd: Path, aliases: AliasLookup
) -> tuple[CommitCommand, ...] | Unreadable:
    """[LAW:parse-dont-validate] every commit the Bash `command` makes, each with the
    directory it runs in, or why that cannot be known. Text that never names git
    makes no commit."""
    if "git" not in command:
        return ()
    text = strip_heredocs(command)
    if text is None:
        return Unreadable("a here-document never ends")
    try:
        tokens = _tokens(text)
    except ValueError as exc:
        return Unreadable(f"unbalanced quoting: {exc}")
    found: list[CommitCommand] = []
    stack: list[Path | None] = []
    here: Path | None = cwd
    words: list[str] = []
    stream: Iterator[str] = iter(tokens)

    def finish() -> Unreadable | None:
        nonlocal here
        here, commits = _simple_command(words, here, aliases) if words else (here, ())
        words.clear()
        if isinstance(commits, Unreadable):
            return commits
        found.extend(commits)
        return None

    for token in stream:
        if not set(token) <= set(";&|()<>\n"):
            words.append(token)
            continue
        if "<" in token or ">" in token:
            if "(" in token:
                return Unreadable("process substitution")
            if words and words[-1].isdigit():
                words.pop()  # the redirected descriptor, as in `2>`
            next(stream, None)  # the redirect target is not a command word
            continue
        if failure := finish():
            return failure
        for char in token:
            if char == "(":
                stack.append(here)
            elif char == ")":
                if not stack:
                    return Unreadable("unbalanced parentheses")
                here = stack.pop()
    if failure := finish():
        return failure
    return tuple(found)


_SELECT_SHORT = frozenset("aiop")
_VALUE_SHORT = frozenset("mFCct")
_FLAG_SHORT = frozenset("qsve")
_VALUE_LONG = frozenset({"message", "file", "reuse-message", "reedit-message", "template"})
_FLAG_LONG = frozenset(
    {"quiet", "signoff", "verbose", "edit", "no-edit", "amend", "allow-empty"}
    | {"allow-empty-message"}
)


def commit_selection(args: Sequence[str]) -> str | None:
    """Why `git commit args` would record something other than the inspected index, or
    None when staging stays explicit. Path, all-tracked, interactive and unrecognized
    options select or rewrite contents after the hook has looked, so they are refused."""
    rest = iter(args)
    for arg in rest:
        if arg == "--" or arg == "-" or not arg.startswith("-"):
            return f"{arg!r} selects paths to commit"
        if arg.startswith("--"):
            name, equals, _ = arg[2:].partition("=")
            if name in _VALUE_LONG:
                if not equals:
                    next(rest, None)
                continue
            if name in _FLAG_LONG and not equals:
                continue
            return f"{arg!r} is not an explicit-staging option"
        for position, flag in enumerate(arg[1:], start=2):
            if flag in _VALUE_SHORT:
                if position == len(arg):
                    next(rest, None)
                break
            if flag in _SELECT_SHORT or flag not in _FLAG_SHORT:
                return f"{arg!r} is not an explicit-staging option"
    return None


def observe_alias(root: Path, name: str) -> str | None:
    """[LAW:effects-at-boundaries] Git's own alias resolution for `root`."""
    proc = subprocess.run(
        ["git", "-C", str(root), "config", "--get", f"alias.{name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise OSError(f"git config alias.{name} in {root}: {proc.stderr.strip()}")
    return proc.stdout.strip() if proc.returncode == 0 else None


# --- staged scope ------------------------------------------------------------------------


@dataclass(frozen=True)
class StagedScope:
    """What a commit records and what surrounds it: staged non-deleted paths, staged
    deletions, those staged paths whose worktree bytes differ from the index (WS-08:
    verified only by checking staged bytes), every unstaged or untracked path, and every
    path the index tracks."""

    paths: tuple[str, ...]
    deleted: tuple[str, ...]
    divergent: tuple[str, ...]
    dirty: tuple[str, ...]
    tracked: tuple[str, ...]


def _z_fields(raw: bytes) -> list[str]:
    return [field.decode("utf-8") for field in raw.split(b"\0") if field]


def parse_staged(
    name_status: bytes, unstaged: bytes, untracked: bytes, tracked: bytes
) -> StagedScope:
    """The single checkpoint for Git's `-z` listings (`git diff --cached --name-status
    --no-renames -z`, `git diff --name-only -z`, `git ls-files --others
    --exclude-standard -z` and `git ls-files -z`)."""
    fields = _z_fields(name_status)
    if len(fields) % 2:
        raise ValueError("staged listing: status without a path")
    entries = list(zip(fields[::2], fields[1::2], strict=True))
    paths = tuple(path for status, path in entries if status != "D")
    worktree_changed = _z_fields(unstaged)
    return StagedScope(
        paths,
        tuple(path for status, path in entries if status == "D"),
        tuple(path for path in paths if path in set(worktree_changed)),
        tuple(sorted({*worktree_changed, *_z_fields(untracked)})),
        tuple(_z_fields(tracked)),
    )


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def observe_staged(root: Path) -> StagedScope:
    """[LAW:effects-at-boundaries] the actual index and worktree state, never a command's
    spelling."""
    return parse_staged(
        _git(root, "diff", "--cached", "--name-status", "--no-renames", "-z"),
        _git(root, "diff", "--name-only", "-z"),
        _git(root, "ls-files", "--others", "--exclude-standard", "-z"),
        _git(root, "ls-files", "-z"),
    )


def changed_worktree_paths(root: Path) -> tuple[str, ...]:
    """Stop's subjects: tracked changes against HEAD, deletions excluded, plus genuine
    untracked files."""
    tracked = _z_fields(_git(root, "diff", "--name-only", "--diff-filter=d", "-z", "HEAD"))
    untracked = _z_fields(_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
    return tuple(sorted(set(tracked) | set(untracked)))


# --- obligations -------------------------------------------------------------------------


@dataclass(frozen=True)
class Check:
    """One checker execution from the repository root. `subject`, when set, is fed on
    stdin as the scope's exact bytes; every other input is read from the working tree.
    Exit 0 passes, 1 reports findings, anything else means it could not decide."""

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

_UV = ("uv", "run", "--quiet")
_PYTEST = (*_UV, "pytest", "-q", "-p", "no:cacheprovider")
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


def _top(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else ""


def behavior_tests(path: str, tracked: Sequence[str]) -> tuple[str, ...]:
    """The narrowest behavior tests for a source subject: itself when it is a test,
    otherwise every tracked sibling `test_<name>` under the same top-level directory."""
    name = PurePosixPath(path).name
    if name.startswith("test_"):
        return (path,)
    wanted = "test_" + name.replace("-", "_")
    return tuple(t for t in tracked if PurePosixPath(t).name == wanted and _top(t) == _top(path))


def _test_check(test: str, code_roots: tuple[str, ...]) -> Check:
    python = test.endswith(".py")
    return Check(
        "pytest" if python else "bash-test",
        "uv.lock" if python else "bash",
        (*_PYTEST, test) if python else ("bash", test),
        None,
        code_roots,
        tuple(sorted({*LOCKED_INPUTS, test})),
        100.0 if python else 60.0,
    )


def ruff_obligations(paths: Sequence[str], ruff_version: str | None) -> tuple[Obligation, ...]:
    """Ruff lint and format over each changed Python subject's exact bytes."""
    subjects = [path for path in paths if path.endswith(".py")]
    if subjects and ruff_version is None:
        return (Gap("ruff is unavailable"),)
    return tuple(
        Check(
            name,
            str(ruff_version),
            (*ruff_command(), *args, "--config", RUFF_CONFIG, "--stdin-filename", path, "-"),
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


def _record_check(producer: tuple[str, ...]) -> Check:
    name = f"record-{PurePosixPath(producer[0]).stem}"
    return Check(name, "uv.lock", (*_UV, "python", *producer), None, (".",), LOCKED_INPUTS, 60.0)


def _json_check(path: str) -> Check:
    lines = ("--json-lines",) if path.endswith(".jsonl") else ()
    argv = (*_UV, "python", "-m", "json.tool", *lines)
    return Check("json", "uv.lock", argv, path, (), LOCKED_INPUTS, 30.0)


def commit_obligations(
    paths: Sequence[str],
    deleted: Sequence[str],
    tracked: Sequence[str],
    policy: WorkflowPolicy,
    ruff_version: str | None,
) -> tuple[Obligation, ...]:
    """[LAW:single-enforcer] the one place WS-07's proportionate local set is decided for
    a staged scope; required CI stays a later gate. A deletion can orphan any record
    reference, so it runs the record producers."""
    code_roots = parse_classification(policy.rules["artifact_roots"]).code_roots
    tests = {
        path: behavior_tests(path, tracked) for path in paths if path.endswith(_SOURCE_SUFFIXES)
    }
    risk_tests = [
        test
        for _, prefixes, added in RISK_EXPANSIONS
        if any(path.startswith(prefixes) for path in paths)
        for test in added
    ]
    records = [path for path in paths if not path.endswith(_SOURCE_SUFFIXES)]
    return (
        *ruff_obligations(paths, ruff_version),
        *(
            Gap(f"{path}: no behavior test under its top directory")
            for path, found in tests.items()
            if not found
        ),
        *(
            _test_check(test, code_roots)
            for test in dict.fromkeys(
                [*(t for found in tests.values() for t in found), *risk_tests]
            )
        ),
        *(_record_check(producer) for producer in RECORD_PRODUCERS if records or deleted),
        *(_json_check(path) for path in records if path.endswith((".json", ".jsonl"))),
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


Runner = Callable[[Sequence[str], bytes, Path, float], subprocess.CompletedProcess[bytes]]
Clock = Callable[[], float]


def run_bounded(
    argv: Sequence[str], stdin: bytes, cwd: Path, timeout: float
) -> subprocess.CompletedProcess[bytes]:
    """[LAW:effects-at-boundaries] one checker process in `cwd`; a timeout or a missing
    executable is an undecided result, never a pass."""
    try:
        return subprocess.run(
            list(argv), input=stdin, cwd=cwd, capture_output=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(list(argv), 124, b"", b"checker timed out")
    except OSError as exc:
        return subprocess.CompletedProcess(list(argv), 127, b"", str(exc).encode())


def ruff_command() -> tuple[str, ...]:
    return ("ruff",) if shutil.which("ruff") else (*_UV, "ruff")


def ruff_version(root: Path, run: Runner) -> str | None:
    proc = run([*ruff_command(), "--version"], b"", root, 30.0)
    return proc.stdout.decode().strip() if proc.returncode == 0 and proc.stdout else None


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


def _within(path: str, root: str) -> bool:
    return root == "." or path == root or path.startswith(root.rstrip("/") + "/")


def run_check(
    root: Path,
    trial: Trial,
    scope: Scope,
    check: Check,
    dirty: Sequence[str],
    *,
    created_at: str,
    run: Runner,
    timeout: float,
) -> Outcome:
    """One check: reuse an accepted identical result, otherwise run it on exactly the
    manifest's inputs and publish a passed receipt for later reuse."""
    label = check.subject or " ".join(check.argv)
    request = CheckRequest(
        unit=trial.unit,
        repository=trial.repository,
        scope=scope,
        policy=trial.policy,
        checker=Checker(check.name, check.version, check.argv),
        domains=check.domains,
        explicit=tuple(sorted({*check.explicit, *([check.subject] if check.subject else [])})),
        environment={},
        material_base=None,
        closure="declared",
    )
    # [LAW:single-enforcer] a check reads every input except its stdin subject from the
    # working tree; an unstaged or untracked path among them is not what is recorded.
    reads = (*check.domains, *(path for path in check.explicit if path != check.subject))
    stale = [path for path in dirty if any(_within(path, read) for read in reads)]
    if stale:
        return Outcome(
            "held",
            ("binding_stale",),
            (f"{label}: reads unstaged or untracked {', '.join(stale)}; stage or remove them",),
        )
    try:
        manifest = build_manifest(root, request)
    except (EvidenceError, subprocess.CalledProcessError) as exc:
        return Outcome("held", ("invalid_input",), (f"{label}: inputs unobservable: {exc}",))
    if manifest.refusals:
        codes = ", ".join(r.code for r in manifest.refusals)
        return Outcome("held", ("identity_mismatch",), (f"{label}: inputs refused: {codes}",))
    stored = _receipt_path(manifest)
    if stored.exists() and reuse_result(load_receipt(stored.read_bytes()), manifest).reusable:
        return PASSED
    if timeout <= 0:
        return Outcome("held", ("check_pending",), (f"{label}: commit check budget exhausted",))
    content = b"" if check.subject is None else _subject_bytes(root, scope, check.subject)
    entry = next((e for e in manifest.files if e.path == check.subject), None)
    # [LAW:single-enforcer] the checker sees only the bytes the manifest identified; an
    # edit between observation and execution invalidates the binding.
    if entry is not None and hashlib.sha256(content).hexdigest() != entry.sha256:
        return Outcome("held", ("binding_stale",), (f"{label}: changed while being checked",))
    proc = run(check.argv, content, root, timeout)
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
        producer={"tool": "workflow_commit", "version": "2"},
        created_at=created_at,
        result="passed",
        artifacts=[],
    )
    try:
        publish_receipt(stored, record)
    except OSError as exc:
        return Outcome("error", ("publication_uncertain",), (f"{label}: receipt: {exc}",))
    return PASSED


def run_obligations(
    root: Path,
    trial: Trial,
    scope: Scope,
    obligations: Sequence[Obligation],
    dirty: Sequence[str],
    *,
    created_at: str,
    run: Runner,
    clock: Clock,
) -> Outcome:
    """Every obligation in order within one time budget; a Gap holds."""
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
                        dirty,
                        created_at=created_at,
                        run=run,
                        timeout=remaining,
                    )
                )
    return combine(outcomes)


def commit_outcome(
    root: Path,
    trial: Trial,
    *,
    created_at: str,
    run: Runner = run_bounded,
    clock: Clock = time.monotonic,
) -> Outcome:
    """The trial commit gate: the actual staged scope, then its proportionate checks."""
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
    obligations = commit_obligations(
        staged.paths, staged.deleted, staged.tracked, trial.policy, ruff_version(root, run)
    )
    return run_obligations(
        root,
        trial,
        Index(),
        obligations,
        staged.dirty,
        created_at=created_at,
        run=run,
        clock=clock,
    )


def stop_outcome(
    root: Path,
    trial: Trial,
    *,
    created_at: str,
    run: Runner = run_bounded,
    clock: Clock = time.monotonic,
) -> Outcome:
    """Stop stays lint-only: Ruff over the changed working-tree subjects."""
    obligations = ruff_obligations(changed_worktree_paths(root), ruff_version(root, run))
    return run_obligations(
        root, trial, WorkingTree(), obligations, (), created_at=created_at, run=run, clock=clock
    )


def route_commit(commit: CommitCommand, *, created_at: str, run: Runner, clock: Clock) -> Outcome:
    """One commit, gated by the profile of the repository it records into."""
    root = repository_root(commit.root)
    match (root, Legacy() if root is None else worktree_profile(root)):
        case (Path() as top, Trial() as trial):
            selection = commit_selection(commit.args)
            if selection is not None:
                return Outcome(
                    "held", ("invalid_input",), (f"staging stays explicit: {selection}",)
                )
            return commit_outcome(top, trial, created_at=created_at, run=run, clock=clock)
        case (_, Held(reasons=reasons)):
            return Outcome(
                "held", ("policy_mismatch",), (f"trial selection held: {', '.join(reasons)}",)
            )
        case _:
            return PASSED


def command_outcome(
    command: str,
    cwd: Path,
    *,
    created_at: str,
    aliases: AliasLookup = observe_alias,
    run: Runner = run_bounded,
    clock: Clock = time.monotonic,
) -> Outcome:
    """The pre-commit gate for one Bash command: each commit it makes is routed by its
    own repository; a command whose commit effect cannot be read holds trial work."""
    commits = read_commits(command, cwd, aliases)
    match commits:
        case Unreadable(reason=reason):
            if isinstance(profile_at(cwd), Legacy):
                return PASSED
            return Outcome("held", ("invalid_input",), (f"commit effect unreadable: {reason}",))
        case _:
            return combine(
                [route_commit(c, created_at=created_at, run=run, clock=clock) for c in commits]
            )


# --- CLI (Stop hook) ---------------------------------------------------------------------


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def main(argv: list[str]) -> int:
    """`stop --root <dir>`: one JSON object naming the profile and, for trial work, the
    outcome. Legacy output tells the caller to run its existing gate unchanged."""
    if len(argv) != 3 or argv[0] != "stop" or argv[1] != "--root":
        print("usage: workflow_commit.py stop --root <dir>", file=sys.stderr)
        return 2
    root = Path(argv[2]).resolve()
    profile = worktree_profile(root)
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
            outcome = stop_outcome(root, profile, created_at=now())
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

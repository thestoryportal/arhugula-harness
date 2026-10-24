#!/usr/bin/env python3
"""WO-U06 / WP-04 — proportionate trial commits and changed-subject reuse (spec WS-07,
WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

`read_commits` reads what a Bash command does to Git: every commit it makes, through
quoting, `git -C`, `cd`, subshells, command substitutions, wrappers, shells, `eval` and
aliases, and whether anything that can change the index or worktree runs before or
alongside one. The gate inspects the index before the command runs, so such a commit is
`Unreadable`, as is any command whose commit effect the reader cannot follow; that passes
only while no worktree can select a trial profile. A script or program run from a file
is the reader's limit: it counts as an effect, but commits inside it are not followed.

Each commit is routed by its repository top level: legacy work keeps the existing hooks
unchanged, a held selection holds, and a trial commit must leave staging explicit
(`commit_selection`), because only then is the inspected index exactly what Git records.
`parse_staged` turns Git's listings into a `StagedScope`, and a staged path whose
worktree bytes differ from the index holds (`binding_stale`). `commit_obligations` names
the proportionate local set (WS-07): Ruff lint and format for each changed Python
subject, the behavior tests of each changed Python or shell subject (`tests_for`), the
named risk expansion for hook and guard paths, the CI record producers for any record
path, and a parser for JSON records. A subject with no behavior test is a `Gap` and
holds. There is no whole-project Pyright, suite or closeout. Stop runs the Ruff subset
over the working tree.

Commit checks run in a private checkout of exactly the index (`index_snapshot`), so
unstaged or untracked work neither reaches nor blocks them, and the index is observed
again once they finish: a change while they ran holds. Every check is keyed by its WP-03
input manifest, which includes the observed checker identity (`Toolchain`). A stored
passed receipt is reused only when `reuse_result` accepts it for the current manifest,
so an unchanged commit or turn runs nothing, while any material change runs the check
again. Failed, unavailable or unreadable results are never reused as a pass.

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
import tempfile
import time
from collections.abc import Callable, Generator, Iterable, Mapping, Sequence
from contextlib import contextmanager
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
    ActivationAbsent,
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
    """The command may commit, but where, how or over what cannot be determined from its
    text."""

    reason: str


@dataclass(frozen=True)
class Reading:
    """What a command does that the commit gate needs: the commits it makes, in order, and
    the first thing it runs that can change the index, worktree or HEAD, None while it
    only reads. A commit is such an effect for whatever runs after it."""

    commits: tuple[CommitCommand, ...] = ()
    effect: str | None = None


class _UnreadableError(Exception):
    """Raised inside the reader; `read_commits` returns it as `Unreadable`."""


@dataclass(frozen=True)
class Wrapper:
    """A program that runs the command after its options and `operands` leading operands:
    options that take a value, options that take none, options whose value is the
    command's directory, and options after which it runs no command at all."""

    valued: frozenset[str] = frozenset()
    flags: frozenset[str] = frozenset()
    operands: int = 0
    chdir: frozenset[str] = frozenset()
    stops: frozenset[str] = frozenset()


def _names(*names: str) -> frozenset[str]:
    return frozenset(names)


AliasLookup = Callable[[Path, str], str | None]
# [LAW:one-type-per-behavior] each wrapper is data for the one option reader, `_unwrap`.
WRAPPERS: Mapping[str, Wrapper] = {
    "rtk": Wrapper(),
    "nohup": Wrapper(),
    "command": Wrapper(flags=_names("-p"), stops=_names("-v", "-V")),
    "exec": Wrapper(valued=_names("-a"), flags=_names("-c", "-l")),
    "time": Wrapper(
        valued=_names("-o", "-f", "--output", "--format"),
        flags=_names("-p", "-v", "-a", "--verbose", "--append", "--portability"),
    ),
    "timeout": Wrapper(
        valued=_names("-s", "-k", "--signal", "--kill-after"),
        flags=_names("-v", "--verbose", "--preserve-status", "--foreground"),
        operands=1,
    ),
    "nice": Wrapper(valued=_names("-n", "--adjustment")),
    "stdbuf": Wrapper(valued=_names("-i", "-o", "-e", "--input", "--output", "--error")),
    "ionice": Wrapper(
        valued=_names("-c", "-n", "--class", "--classdata"), flags=_names("-t", "--ignore")
    ),
    "setsid": Wrapper(flags=_names("-c", "-f", "-w", "--ctty", "--fork", "--wait")),
    "env": Wrapper(
        valued=_names("-u", "--unset"),
        flags=_names("-i", "-0", "-v", "--ignore-environment", "--null", "--debug"),
        chdir=_names("-C", "--chdir"),
    ),
}
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
_SHELL_VALUED = frozenset({"-o", "+o", "-O", "+O", "--rcfile", "--init-file"})
_INTERPRETER = re.compile(r"python[0-9.]*|node|perl|ruby")
_INLINE_CODE = re.compile(r"-[A-Za-z]*[ceE]|--eval|--print|-p")
# Programs that run a command assembled from their arguments in a way this reader does
# not follow.
_RUNNERS = frozenset({"xargs", "find", "parallel", "watch", "sudo", "script", "flock"})
# Compound commands whose bodies run repeatedly or by pattern.
_COMPOUND = frozenset({"for", "case", "select", "function", "coproc"})
_RESERVED = frozenset({"if", "then", "else", "elif", "do", "while", "until", "!"})
_ASSIGNS = frozenset({"export", "declare", "typeset", "local", "readonly"})
# Commands that change neither the index nor the worktree unless their output is
# redirected to a file.
_READ_ONLY = frozenset(
    {"cd", "pushd", "popd", "true", "false", ":", "echo", "printf", "cat", "pwd", "ls"}
    | {"head", "tail", "grep", "wc", "date", "basename", "dirname", "which", "type"}
    | {"test", "[", "[[", "sleep", "exit", "fi", "done", "}"}
)
_READ_ONLY_GIT = frozenset({"status", "diff", "log", "show", "rev-parse", "ls-files"})
_GIT_FLAGS = frozenset(
    {"--no-pager", "-P", "-p", "--paginate", "--no-optional-locks", "--literal-pathspecs"}
    | {"--no-replace-objects", "--noglob-pathspecs"}
)
_HEREDOC = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z0-9_.-]+)\2")
_ASSIGNMENT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=")
_GIT_WORD = re.compile(r"\bgit\b")
_SUBSTITUTION = re.compile("\\$\0(\\d+)\0")
# A program word holding one of these is the result of an expansion this reader does not
# perform.
_EXPANDS = frozenset("$`*?[{")
_PUNCTUATION = frozenset(";&|()<>\n")
_DEPTH = 8


def _strip_heredocs(text: str) -> str:
    """`text` without here-document operators and bodies, which are data rather than
    commands. A body that never ends, or one whose unquoted delimiter lets the shell run a
    substitution inside it, is unreadable."""
    lines: list[str] = []
    pending: list[tuple[str, bool, bool]] = []
    quote = ""
    for line in text.split("\n"):
        if pending:
            delimiter, tabs, literal = pending[0]
            if (line.lstrip("\t") if tabs else line) == delimiter:
                pending.pop(0)
            elif not literal and ("$(" in line or "`" in line):
                raise _UnreadableError("a here-document with an unquoted delimiter substitutes")
            continue
        kept, quote = _scan_heredocs(line, quote, pending)
        lines.append(kept)
    if pending:
        raise _UnreadableError("a here-document never ends")
    return "\n".join(lines)


def _scan_heredocs(line: str, quote: str, pending: list[tuple[str, bool, bool]]) -> tuple[str, str]:
    """`line` without its `<<` operators outside single quotes, each appended to `pending`,
    and the quote still open at its end. Double quotes do not hide one, because a
    here-document inside `"$(...)"` is still read by the shell."""
    kept: list[str] = []
    index = 0
    while index < len(line):
        char = line[index]
        match = None if quote == "'" else _HEREDOC.match(line, index)
        if line.startswith("<<<", index):
            kept.append("<<<")
            index += 3
            continue
        if match:
            pending.append((match.group(3), match.group(1) == "-", bool(match.group(2))))
            index = match.end()
            continue
        if quote == "'":
            quote = "" if char == "'" else quote
        elif char == "\\":
            kept.append(line[index : index + 2])
            index += 2
            continue
        elif quote == '"' and char == '"':
            quote = ""
        elif not quote and char in "'\"":
            quote = char
        kept.append(char)
        index += 1
    return "".join(kept), quote


def lift_substitutions(text: str) -> tuple[str, tuple[str, ...]]:
    """`text` with each outermost command substitution outside single quotes, `$(...)` or
    backquoted, replaced by a `$<NUL>n<NUL>` marker, and the bodies in order. The marker
    stays inside its word, so a program word made from a substitution's output is still
    visibly an expansion, and the body is read where that word's command runs."""
    if "\0" in text:
        raise _UnreadableError("a NUL byte in the command")
    out: list[str] = []
    bodies: list[str] = []
    quote, index = "", 0
    while index < len(text):
        char = text[index]
        if quote != "'" and (text.startswith("$(", index) or char == "`"):
            start = index + 2 if char == "$" else index + 1
            index = _paren_end(text, start) if char == "$" else _backquote_end(text, start)
            out.append(f"$\0{len(bodies)}\0")
            bodies.append(text[start : index - 1])
            continue
        if quote == "'":
            quote = "" if char == "'" else quote
        elif char == "\\":
            out.append(text[index : index + 2])
            index += 2
            continue
        elif char == '"':
            quote = "" if quote else '"'
        elif char == "'" and not quote:
            quote = "'"
        out.append(char)
        index += 1
    return "".join(out), tuple(bodies)


def _backquote_end(text: str, start: int) -> int:
    """Just past the backquote that closes the body starting at `start`."""
    index = start
    while index < len(text):
        if text.startswith("\\`", index):
            raise _UnreadableError("nested backquotes")
        if text[index] == "`":
            return index + 1
        index += 2 if text[index] == "\\" else 1
    raise _UnreadableError("a command substitution never ends")


def _paren_end(text: str, start: int) -> int:
    """Just past the `)` that closes the `$(` body starting at `start`, skipping quoted
    text and nested substitutions."""
    quote, depth, index = "", 0, start
    while index < len(text):
        char = text[index]
        if quote == "'":
            quote = "" if char == "'" else quote
        elif char == "\\":
            index += 1
        elif text.startswith("$(", index):
            index = _paren_end(text, index + 2) - 1
        elif char == "`":
            index = _backquote_end(text, index + 1) - 1
        elif char == '"':
            quote = "" if quote else '"'
        elif not quote and char == "'":
            quote = "'"
        elif not quote and char == ")" and depth == 0:
            return index + 1
        elif not quote and char in "()":
            depth += 1 if char == "(" else -1
        index += 1
    raise _UnreadableError("a command substitution never ends")


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


def _nested(text: str) -> str:
    """Command text a shell, `eval` or alias runs, which must be literal to be read."""
    if _SUBSTITUTION.search(text):
        raise _UnreadableError("it runs the output of a command substitution")
    return text


@dataclass(frozen=True)
class _Context:
    aliases: AliasLookup
    mentions_git: bool


def _then(before: Reading, after: Reading) -> Reading:
    """`after` once `before` has finished. A commit after an effect may record what the
    effect changed, which the gate never inspected."""
    if after.commits and before.effect is not None:
        raise _UnreadableError(
            f"{before.effect} runs before a commit and can change what it records"
        )
    return Reading((*before.commits, *after.commits), before.effect or after.effect)


def _alongside(members: Sequence[Reading]) -> Reading:
    """A pipeline's members, which all run at once."""
    effects = [member.effect for member in members if member.effect is not None]
    commits = tuple(commit for member in members for commit in member.commits)
    if commits and len(effects) > 1:
        raise _UnreadableError(f"{', '.join(effects)} run together, alongside a commit")
    return Reading(commits, next(iter(effects), None))


def _option(arg: str) -> tuple[str, str | None]:
    """An option's name and its attached value: `--name=value` or `-xVALUE`."""
    if arg.startswith("--"):
        name, equals, value = arg.partition("=")
        return name, value if equals else None
    return arg[:2], arg[2:] or None


def _unwrap(program: str, args: list[str], cwd: Path | None) -> tuple[list[str], Path | None]:
    """The command a wrapper runs and the directory it runs in; an option this reader does
    not know is unreadable, because it may change either."""
    wrapper, index, here = WRAPPERS[program], 0, cwd
    while index < len(args) and args[index].startswith("-") and args[index] != "-":
        arg = args[index]
        index += 1
        if arg == "--":
            break
        name, attached = _option(arg)
        if name in wrapper.stops:
            return [], here
        if name in wrapper.valued | wrapper.chdir:
            value = attached if attached is not None else "".join(args[index : index + 1]) or "$"
            index += 0 if attached is not None else 1
            here = _moved(here, value) if name in wrapper.chdir else here
        elif name not in wrapper.flags or attached is not None:
            raise _UnreadableError(f"{program} option {arg!r} is not one this reader knows")
    return args[index + wrapper.operands :], here


def _git_command(words: list[str], cwd: Path | None, context: _Context, depth: int) -> Reading:
    """`words` after the `git` program: its global options, then the subcommand."""
    root, rest = cwd, iter(words)
    for word in rest:
        if word == "-C":
            root = _moved(root, next(rest, "$"))
        elif word == "-c":
            if next(rest, "").lower().startswith("alias."):
                raise _UnreadableError("an alias defined on the command line")
        elif word in _GIT_FLAGS:
            continue
        elif word.startswith("-"):
            raise _UnreadableError(f"git option {word!r} can change what is committed")
        elif _EXPANDS & set(word):
            raise _UnreadableError(f"the git subcommand {word!r} is an expansion")
        elif word in _READ_ONLY_GIT:
            writes = any(arg.startswith("--output") for arg in rest)
            return Reading((), f"git {word} --output" if writes else None)
        elif root is None:
            raise _UnreadableError("git runs in a directory that cannot be determined")
        elif word == "commit":
            return Reading((CommitCommand(root, tuple(rest)),), "git commit")
        else:
            return _git_alias(word, list(rest), root, context, depth)
    return Reading()


def _git_alias(word: str, rest: list[str], root: Path, context: _Context, depth: int) -> Reading:
    """A git subcommand other than commit: an effect, or the alias it expands to."""
    expansion = context.aliases(root, word)
    if expansion is None:
        return Reading((), f"git {word}")
    if expansion.startswith("!"):
        if _GIT_WORD.search(expansion[1:]) or "commit" in expansion:
            raise _UnreadableError(f"shell alias {word!r} runs git")
        return Reading((), f"git {word}")
    if depth >= _DEPTH:
        raise _UnreadableError(f"alias {word!r} nests too deeply")
    try:
        expanded = shlex.split(_nested(expansion))
    except ValueError as exc:
        raise _UnreadableError(f"alias {word!r} is not readable") from exc
    return _git_command([*expanded, *rest], root, context, depth + 1)


def _shell(
    program: str, args: list[str], cwd: Path | None, context: _Context, depth: int
) -> Reading:
    """A shell: its `-c` script is read in `cwd`; a script file is the reader's limit;
    commands from its input are unreadable when the command names git."""
    index, inline = 0, False
    while index < len(args) and args[index].startswith(("-", "+")) and args[index] not in "-+":
        arg = args[index]
        index += 1
        if arg == "--":
            break
        if arg in _SHELL_VALUED:
            index += 1
        elif not arg.startswith("--"):
            inline = inline or "c" in arg[1:]
    operands = args[index:]
    if inline and operands:
        return _read(_nested(operands[0]), cwd, context, depth + 1)
    if (inline or not operands or operands[0] == "-") and context.mentions_git:
        raise _UnreadableError(f"{program} reads commands this reader cannot see")
    return Reading((), " ".join([program, *operands[:1]]))


def _interpreter(program: str, args: list[str], context: _Context) -> Reading:
    """An interpreter runs code from an argument, its input or a file. Inline code naming
    git, or code from its input when the command names git, is unreadable; a program
    file is the reader's limit."""
    inline = any(_INLINE_CODE.fullmatch(arg) for arg in args)
    stdin = "-" in args or all(arg.startswith("-") for arg in args)
    if (inline and any(_GIT_WORD.search(arg) for arg in args)) or (
        stdin and not inline and context.mentions_git
    ):
        raise _UnreadableError(f"{program} runs code that names git")
    return Reading((), program)


def _program_reading(
    program: str, arguments: list[str], cwd: Path | None, context: _Context, depth: int
) -> Reading:
    """What one program does, run in `cwd` with `arguments`."""
    if program == "git":
        return _git_command(arguments, cwd, context, depth)
    if program in _SHELLS:
        return _shell(program, arguments, cwd, context, depth)
    if program == "eval":
        return _read(_nested(" ".join(arguments)), cwd, context, depth + 1)
    if program in _ASSIGNS:
        if any(word.startswith("GIT_") for word in arguments):
            raise _UnreadableError(f"{program} sets a GIT_ variable that changes how git commits")
        return Reading()
    if program in _READ_ONLY:
        return Reading()
    if program in _COMPOUND and context.mentions_git:
        raise _UnreadableError(f"a {program} compound command runs git this reader cannot follow")
    if _INTERPRETER.fullmatch(program):
        return _interpreter(program, arguments, context)
    if program in _RUNNERS and any(_GIT_WORD.search(word) for word in arguments):
        raise _UnreadableError(f"{program} runs a git command this reader cannot follow")
    return Reading((), program)


def _command(
    words: list[str], cwd: Path | None, context: _Context, depth: int
) -> tuple[Path | None, Reading]:
    """One simple command whose substitutions were already read: the shell's directory
    after it, and what it does."""
    run_dir = cwd
    while words:
        assignment = _ASSIGNMENT.match(words[0])
        if assignment and assignment.group(1).startswith("GIT_"):
            raise _UnreadableError(f"{assignment.group(1)} changes how git commits")
        if assignment or words[0] in _RESERVED:
            words = words[1:]
        elif _program(words[0]) in WRAPPERS and not _EXPANDS & set(words[0]):
            words, run_dir = _unwrap(_program(words[0]), words[1:], run_dir)
        else:
            break
    if not words:
        return cwd, Reading()
    word, arguments = words[0], words[1:]
    program = _program(word)
    if word not in _READ_ONLY and _EXPANDS & set(word):
        raise _UnreadableError(f"the program {word!r} is an expansion this reader cannot resolve")
    if program in {"cd", "pushd"}:
        return (_moved(cwd, arguments[0]) if len(arguments) == 1 else None), Reading()
    if program == "popd":
        return None, Reading()
    return cwd, _program_reading(program, arguments, run_dir, context, depth)


def _read(text: str, cwd: Path | None, context: _Context, depth: int) -> Reading:
    """[LAW:single-enforcer] the one reading of command text: its pipelines in order, each
    simple command read in the directory the shell is in when it runs, after the
    substitutions in its words."""
    if depth > _DEPTH:
        raise _UnreadableError("commands nest too deeply")
    lifted, bodies = lift_substitutions(_strip_heredocs(text))
    try:
        tokens = _tokens(lifted)
    except ValueError as exc:
        raise _UnreadableError(f"unbalanced quoting: {exc}") from exc
    sequence, pipeline = Reading(), list[Reading]()
    stack: list[Path | None] = []
    here: Path | None = cwd
    words: list[str] = []
    targets: list[str] = []
    output: list[str] = []
    background = False
    stream = iter(tokens)

    def simple() -> None:
        nonlocal here
        reading = Reading()
        for word in (*words, *targets):
            for match in _SUBSTITUTION.finditer(word):
                body = _read(bodies[int(match.group(1))], here, context, depth + 1)
                reading = _then(reading, body)
        here, command = _command(list(words), here, context, depth)
        effect = command.effect or next((f"output to {target}" for target in output), None)
        pipeline.append(_then(reading, Reading(command.commits, effect)))
        words.clear()
        targets.clear()
        output.clear()

    def settle() -> None:
        nonlocal sequence
        sequence = _then(sequence, _alongside(pipeline))
        pipeline.clear()

    for token in stream:
        if not set(token) <= _PUNCTUATION:
            words.append(token)
        elif "<" in token or ">" in token:
            if "(" in token:
                raise _UnreadableError("process substitution")
            if words and words[-1].isdigit():
                words.pop()  # the redirected descriptor, as in `2>`
            target = next(stream, "")  # a file, not a command word
            targets.append(target)
            if ">" in token and target not in ("/dev/null", "-") and not target.isdigit():
                output.append(target)
        else:
            simple()
            for char in token:
                if char == "(":
                    stack.append(here)
                elif char == ")":
                    if not stack:
                        raise _UnreadableError("unbalanced parentheses")
                    here = stack.pop()
            alone = "&" in token.replace("&&", "").replace("|&", "|")
            background = background or alone
            if alone or any(separator in token for separator in (";", "\n", "&&", "||")):
                settle()
    simple()
    settle()
    if background and sequence.commits:
        raise _UnreadableError("a background job runs alongside the commit")
    return sequence


def read_commits(
    command: str, cwd: Path, aliases: AliasLookup
) -> tuple[CommitCommand, ...] | Unreadable:
    """[LAW:parse-dont-validate] every commit the Bash `command` makes, each with the
    directory it runs in, or why that cannot be known. A commit after or alongside
    anything that can change what it records is unreadable: the gate inspects the index
    before the command runs."""
    context = _Context(aliases, bool(_GIT_WORD.search(command)))
    try:
        return _read(command, cwd, context, 0).commits
    except _UnreadableError as exc:
        return Unreadable(str(exc))


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


@contextmanager
def index_snapshot(root: Path) -> Generator[Path]:
    """[LAW:effects-at-boundaries] a private checkout of exactly the index, so a check that
    reads files sees the bytes the commit records and no unstaged or untracked work."""
    with tempfile.TemporaryDirectory(prefix="workflow-commit-") as directory:
        _git(root, "checkout-index", "--all", f"--prefix={directory}/")
        yield Path(directory)


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
    Ruff command, and the identity of Ruff, Bash and the `uv run` interpreter. An
    identity is None when it could not be observed, which makes each check needing it a
    `Gap`."""

    project: Path
    ruff_argv: tuple[str, ...]
    ruff: str | None
    bash: str | None
    python: str | None


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


def behavior_tests(path: str, tracked: Sequence[str]) -> tuple[str, ...]:
    """A source subject's sibling tests: itself when it is a test, otherwise every tracked
    `test_<name>` under the same top-level directory."""
    name = PurePosixPath(path).name
    if name.startswith("test_"):
        return (path,)
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
    """A check `uv run` executes, identified by the interpreter it resolves."""
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
    producers."""
    code_roots = parse_classification(policy.rules["artifact_roots"]).code_roots
    tests = {
        path: tests_for(path, staged.tracked, naming) for path in source_subjects(staged.paths)
    }
    records = [path for path in staged.paths if not path.endswith(_SOURCE_SUFFIXES)]
    selected = [
        *(test for found in tests.values() for test in found),
        *(test for path in records for test in risk_tests(path)),
    ]
    return (
        *ruff_obligations(staged.paths, toolchain),
        *(Gap(f"{path}: no behavior test names it") for path, found in tests.items() if not found),
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


def ruff_command(project: Path) -> tuple[str, ...]:
    return ("ruff",) if shutil.which("ruff") else (*uv_prefix(project), "ruff")


def _first_line(proc: subprocess.CompletedProcess[bytes]) -> str | None:
    lines = proc.stdout.decode("utf-8", "replace").strip().splitlines()
    return lines[0] if proc.returncode == 0 and lines else None


def observe_toolchain(root: Path, run: Runner) -> Toolchain:
    """[LAW:effects-at-boundaries] each checker's identity, probed from `root`."""
    ruff_argv = ruff_command(root)

    def probe(*argv: str) -> str | None:
        return _first_line(run(argv, b"", root, 30.0))

    uv, python = probe("uv", "--version"), probe(*uv_prefix(root), "python", "--version")
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


def run_check(
    root: Path,
    trial: Trial,
    scope: Scope,
    check: Check,
    cwd: Path,
    *,
    created_at: str,
    run: Runner,
    timeout: float,
) -> Outcome:
    """One check: reuse an accepted identical result, otherwise run it in `cwd`, which
    holds exactly the scope's files, and publish a passed receipt for later reuse."""
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
    proc = run(check.argv, content, cwd, timeout)
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
    terms = (term for path in source_subjects(staged.paths) for term in subject_terms(path))
    toolchain = observe_toolchain(root, run)
    obligations = commit_obligations(staged, trial.policy, toolchain, observe_naming(root, terms))
    with index_snapshot(root) as snapshot:
        checked = run_obligations(
            root, trial, Index(), obligations, snapshot,
            created_at=created_at, run=run, clock=clock,
        )  # fmt: skip
    return combine([checked, rebound(staged, observe_staged(root))])


def stop_outcome(
    root: Path,
    trial: Trial,
    *,
    created_at: str,
    run: Runner = run_bounded,
    clock: Clock = time.monotonic,
) -> Outcome:
    """Stop stays lint-only: Ruff over the changed working-tree subjects."""
    obligations = ruff_obligations(changed_worktree_paths(root), observe_toolchain(root, run))
    return run_obligations(
        root, trial, WorkingTree(), obligations, root, created_at=created_at, run=run, clock=clock
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


def trial_dormant() -> bool:
    """[LAW:effects-at-boundaries] True only while no worktree can select a non-legacy
    profile: the policy reads and no activation receipt exists, so WP-02 selects `legacy`
    for every unit."""
    policy, activation = observe_policy(), read_activation()
    return isinstance(policy, WorkflowPolicy) and isinstance(activation, ActivationAbsent)


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
    own repository. A command whose commit effect cannot be read could record into any
    worktree, so it holds unless none can select trial."""
    match read_commits(command, cwd, aliases):
        case Unreadable(reason=reason):
            if trial_dormant():
                return PASSED
            return Outcome("held", ("invalid_input",), (f"commit effect unreadable: {reason}",))
        case commits:
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

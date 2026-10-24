#!/usr/bin/env python3
"""WO-U06 / WP-04 — proportionate trial commits and changed-subject reuse (spec WS-07,
WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

A trial-profile commit is checked over the scope it actually records: `parse_staged`
turns Git's index listing into a `StagedScope`, and a staged path whose worktree bytes
differ from the index holds the commit (`binding_stale`) — a worktree result never
stands in for staged bytes. Changed Python subjects then get Ruff lint and format checks,
each over one subject's exact bytes in one scope; there is no whole-project Pyright,
suite or closeout, and a record-only commit runs no Python checker at all. Stop checks the
same subjects in the working tree.

Every check is keyed by its WP-03 input manifest. A stored passed receipt is reused only
when `reuse_result` accepts it for the current manifest, so an unchanged turn or a
repeated commit runs nothing, while any material change — subject bytes, mode, Ruff
config or version, head — runs the checker again. Failed, unavailable or unreadable
results are never reused as a pass.

`worktree_profile` routes a worktree: only a unit bound through its Codex loop arc can
select `trial` (WP-02 `select_profile`); legacy work keeps the existing hooks unchanged,
and a held selection holds the commit. Until the coherent activation (WP-17) every unit
selects `legacy`, so this path is inactive.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

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
CHECK_TIMEOUT_SECONDS = 30
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
    with no loop arc enrolled in a readable policy has no unit to select for, so it keeps
    the existing hooks, whose local gates are a superset of the trial's."""
    policy = observe_policy()
    try:
        raw: bytes | None = (root / LOOP_STATE).read_bytes()
    except FileNotFoundError:
        raw = None
    arc = loop_arc(raw)
    member = next(
        (
            entry
            for entry in (policy.eligible_units if isinstance(policy, WorkflowPolicy) else ())
            if entry.arc == arc
        ),
        None,
    )
    if member is None or not isinstance(policy, WorkflowPolicy):
        return Legacy()
    repository = observe_repository(root)
    selection = select_profile(
        policy,
        SelectionFacts(
            repository=repository,
            unit=member.unit,
            arc=arc,
            trial_relation="unknown",
            admission="unknown",
            activation=read_activation(),
        ),
    )
    match selection.kind:
        case "trial":
            return Trial(member.unit, repository, policy)
        case "legacy":
            return Legacy()
        case "held":
            return Held(selection.reasons)


# --- staged scope ------------------------------------------------------------------------


@dataclass(frozen=True)
class StagedScope:
    """What a commit records: staged non-deleted paths, and those whose worktree bytes
    differ from the index (WS-08: such a path is verified only by checking staged bytes)."""

    paths: tuple[str, ...]
    divergent: tuple[str, ...]


def _z_fields(raw: bytes) -> list[str]:
    return [field.decode("utf-8") for field in raw.split(b"\0") if field]


def parse_staged(name_status: bytes, unstaged: bytes) -> StagedScope:
    """The single checkpoint for Git's `-z` index listings (`git diff --cached
    --name-status --no-renames -z` and `git diff --name-only -z`)."""
    fields = _z_fields(name_status)
    if len(fields) % 2:
        raise ValueError("staged listing: status without a path")
    paths = tuple(
        path for status, path in zip(fields[::2], fields[1::2], strict=True) if status != "D"
    )
    worktree_changed = set(_z_fields(unstaged))
    return StagedScope(paths, tuple(path for path in paths if path in worktree_changed))


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def observe_staged(root: Path) -> StagedScope:
    """[LAW:effects-at-boundaries] the actual index and worktree state, never a command's
    spelling."""
    return parse_staged(
        _git(root, "diff", "--cached", "--name-status", "--no-renames", "-z"),
        _git(root, "diff", "--name-only", "-z"),
    )


def changed_worktree_paths(root: Path) -> tuple[str, ...]:
    """Stop's subjects: tracked changes against HEAD, deletions excluded, plus genuine
    untracked files."""
    tracked = _z_fields(_git(root, "diff", "--name-only", "--diff-filter=d", "-z", "HEAD"))
    untracked = _z_fields(_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
    return tuple(sorted(set(tracked) | set(untracked)))


def python_subjects(paths: Sequence[str]) -> tuple[str, ...]:
    return tuple(path for path in paths if path.endswith(".py"))


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


@dataclass(frozen=True)
class RuffCheck:
    """One Ruff subcommand over one subject read from stdin: exit 0 passes, 1 reports
    findings, anything else means the checker could not decide."""

    name: str
    args: tuple[str, ...]


RUFF_CHECKS = (
    RuffCheck("ruff-check", ("check", "--quiet", "--output-format=concise")),
    RuffCheck("ruff-format", ("format", "--check")),
)
Runner = Callable[[list[str], bytes], subprocess.CompletedProcess[bytes]]


def run_bounded(argv: list[str], stdin: bytes) -> subprocess.CompletedProcess[bytes]:
    """[LAW:effects-at-boundaries] one checker process; a timeout or a missing executable
    is an undecided result, never a pass."""
    try:
        return subprocess.run(
            argv, input=stdin, capture_output=True, timeout=CHECK_TIMEOUT_SECONDS, check=False
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(argv, 124, b"", b"checker timed out")
    except OSError as exc:
        return subprocess.CompletedProcess(argv, 127, b"", str(exc).encode())


def ruff_command() -> list[str]:
    return ["ruff"] if shutil.which("ruff") else ["uv", "run", "--quiet", "ruff"]


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


def check_subject(
    root: Path,
    trial: Trial,
    scope: Scope,
    path: str,
    ruff: RuffCheck,
    *,
    version: str,
    created_at: str,
    run: Runner = run_bounded,
) -> Outcome:
    """One Ruff check over one subject: reuse an accepted identical result, otherwise run
    it on exactly the manifest's bytes and publish a passed receipt for later reuse."""
    request = CheckRequest(
        unit=trial.unit,
        repository=trial.repository,
        scope=scope,
        policy=trial.policy,
        checker=Checker(ruff.name, version, ruff.args),
        domains=(),
        explicit=tuple(sorted({path, RUFF_CONFIG})),
        environment={},
        material_base=None,
        closure="declared",
    )
    try:
        manifest = build_manifest(root, request)
    except (EvidenceError, subprocess.CalledProcessError) as exc:
        return Outcome("held", ("invalid_input",), (f"{path}: inputs unobservable: {exc}",))
    if manifest.refusals:
        codes = ", ".join(r.code for r in manifest.refusals)
        return Outcome("held", ("identity_mismatch",), (f"{path}: inputs refused: {codes}",))
    stored = _receipt_path(manifest)
    if stored.exists() and reuse_result(load_receipt(stored.read_bytes()), manifest).reusable:
        return PASSED
    content = _subject_bytes(root, scope, path)
    entry = next(e for e in manifest.files if e.path == path)
    # [LAW:single-enforcer] the checker sees only the bytes the manifest identified; an
    # edit between observation and execution invalidates the binding.
    if hashlib.sha256(content).hexdigest() != entry.sha256:
        return Outcome("held", ("binding_stale",), (f"{path}: changed while being checked",))
    proc = run([*ruff_command(), *ruff.args, "--stdin-filename", path, "-"], content)
    output = (proc.stdout + proc.stderr).decode("utf-8", "replace").strip()
    if proc.returncode == 1:
        return Outcome("failed", ("check_failed",), (f"{path}: {ruff.name}: {output}",))
    if proc.returncode != 0:
        return Outcome(
            "held", ("check_pending",), (f"{path}: {ruff.name} could not run: {output}",)
        )
    record = check_receipt(
        manifest,
        record_id=stored.stem,
        producer={"tool": "workflow_commit", "version": "1"},
        created_at=created_at,
        result="passed",
        artifacts=[],
    )
    try:
        publish_receipt(stored, record)
    except OSError as exc:
        return Outcome("error", ("publication_uncertain",), (f"{path}: receipt: {exc}",))
    return PASSED


def ruff_version(run: Runner = run_bounded) -> str | None:
    proc = run([*ruff_command(), "--version"], b"")
    return proc.stdout.decode().strip() if proc.returncode == 0 and proc.stdout else None


def check_subjects(
    root: Path,
    trial: Trial,
    scope: Scope,
    paths: Sequence[str],
    *,
    created_at: str,
    run: Runner = run_bounded,
) -> Outcome:
    """Ruff over each changed Python subject; no subjects means nothing to run."""
    subjects = python_subjects(paths)
    if not subjects:  # a record-only scope has no Python checker to run
        return PASSED
    version = ruff_version(run)
    if version is None:
        return Outcome("held", ("check_pending",), ("ruff is unavailable",))
    return combine(
        [
            check_subject(
                root, trial, scope, path, ruff, version=version, created_at=created_at, run=run
            )
            for path in subjects
            for ruff in RUFF_CHECKS
        ]
    )


def commit_outcome(
    root: Path, trial: Trial, *, created_at: str, run: Runner = run_bounded
) -> Outcome:
    """The trial commit gate: the actual staged scope, then its changed-subject checks."""
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
    return check_subjects(root, trial, Index(), staged.paths, created_at=created_at, run=run)


def stop_outcome(
    root: Path, trial: Trial, *, created_at: str, run: Runner = run_bounded
) -> Outcome:
    return check_subjects(
        root, trial, WorkingTree(), changed_worktree_paths(root), created_at=created_at, run=run
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

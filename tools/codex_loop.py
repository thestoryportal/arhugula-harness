#!/usr/bin/env python3
"""Local state machine for the Codex autonomous development loop.

The state file is intentionally local and gitignored. It makes the current loop
phase inspectable across resumes without turning transient agent progress into a
tracked project artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

STATE_PATH = Path(".harness/codex_loop_state.json")
PRE_CLOSEOUT_GATES = (
    "worktree_ready",
    "preflight",
    "plan",
    "red",
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
)
DEVELOPMENT_GATES = (
    *PRE_CLOSEOUT_GATES,
    "closeout",
)
SHIP_GATES = (
    "commit",
    "push",
    "pr_opened",
    "ci_green",
    "merged",
    "post_merge_refresh",
    "main_synced",
    "worktree_disposition",
)
REQUIRED_GATES = (*DEVELOPMENT_GATES, *SHIP_GATES)
STATUSES = ("passed", "failed", "blocked", "skipped")
PRE_COMMIT_WORKTREE_GATES = (
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
    "closeout",
)
CLEAN_WORKTREE_RECORD_GATES = (
    "commit",
    "push",
    "pr_opened",
    "ci_green",
    "merged",
    "post_merge_refresh",
    "main_synced",
    "worktree_disposition",
)


@dataclass(frozen=True)
class GitIdentity:
    root: Path
    branch: str
    head8: str
    worktree_fingerprint: str
    content_fingerprint: str
    linked_worktree: bool


def _run(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args=args, returncode=127, stdout="", stderr=str(exc))


def _out(args: list[str], *, cwd: Path) -> str:
    proc = _run(args, cwd=cwd)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _run_bytes(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(
            args=args,
            returncode=127,
            stdout=b"",
            stderr=str(exc).encode("utf-8", errors="replace"),
        )


def worktree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    pathspec = ["--", ".", f":(exclude){STATE_PATH.as_posix()}"]

    def add(label: str, payload: bytes) -> None:
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")

    for label, args in (
        ("status", ["git", "status", "--short", "--untracked-files=all", *pathspec]),
        ("diff", ["git", "diff", "--binary", "--no-ext-diff", *pathspec]),
        ("cached", ["git", "diff", "--cached", "--binary", "--no-ext-diff", *pathspec]),
    ):
        proc = _run_bytes(args, cwd=root)
        add(f"{label}:returncode", str(proc.returncode).encode("ascii"))
        add(f"{label}:stdout", proc.stdout)
        add(f"{label}:stderr", proc.stderr)

    proc = _run_bytes(
        ["git", "ls-files", "--others", "--exclude-standard", "-z", *pathspec], cwd=root
    )
    add("untracked:returncode", str(proc.returncode).encode("ascii"))
    add("untracked:stderr", proc.stderr)
    for rel_raw in sorted(part for part in proc.stdout.split(b"\0") if part):
        rel = rel_raw.decode("utf-8", errors="surrogateescape")
        add("untracked:path", rel_raw)
        try:
            add("untracked:sha256", hashlib.sha256((root / rel).read_bytes()).hexdigest().encode())
        except OSError as exc:
            add("untracked:error", str(exc).encode("utf-8", errors="replace"))
    return digest.hexdigest()[:16]


def content_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    pathspec = ["--", ".", f":(exclude){STATE_PATH.as_posix()}"]

    def add(label: str, payload: bytes) -> None:
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")

    stage_proc = _run_bytes(["git", "ls-files", "--stage", "-z", *pathspec], cwd=root)
    stage_metadata: dict[bytes, bytes] = {}
    for entry in (part for part in stage_proc.stdout.split(b"\0") if part):
        if b"\t" not in entry:
            continue
        metadata, rel_raw = entry.split(b"\t", 1)
        stage_metadata[rel_raw] = metadata
    add("stage:returncode", str(stage_proc.returncode).encode("ascii"))
    add("stage:stderr", stage_proc.stderr)

    proc = _run_bytes(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", *pathspec],
        cwd=root,
    )
    add("ls-files:returncode", str(proc.returncode).encode("ascii"))
    add("ls-files:stderr", proc.stderr)
    for rel_raw in sorted(set(part for part in proc.stdout.split(b"\0") if part)):
        rel = rel_raw.decode("utf-8", errors="surrogateescape")
        path = root / rel
        if not path.exists() and not path.is_symlink():
            continue
        add("path", rel_raw)
        if path.is_symlink():
            add("kind", b"symlink")
            try:
                add("target", str(path.readlink()).encode("utf-8", errors="surrogateescape"))
            except OSError as exc:
                add("target:error", str(exc).encode("utf-8", errors="replace"))
        elif path.is_file():
            add("kind", b"file")
            try:
                executable = b"1" if path.stat().st_mode & 0o111 else b"0"
                add("executable", executable)
            except OSError as exc:
                add("executable:error", str(exc).encode("utf-8", errors="replace"))
            try:
                add("sha256", hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
            except OSError as exc:
                add("file:error", str(exc).encode("utf-8", errors="replace"))
        else:
            add("kind", b"other")
            stage = stage_metadata.get(rel_raw)
            if stage is not None:
                add("stage", stage)
    return digest.hexdigest()[:16]


def dirty_status(root: Path) -> str:
    pathspec = ["--", ".", f":(exclude){STATE_PATH.as_posix()}"]
    proc = _run(["git", "status", "--short", "--untracked-files=all", *pathspec], cwd=root)
    if proc.returncode != 0:
        return "<status unavailable>"
    return proc.stdout.strip()


def _resolve_git_path(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def is_linked_worktree(root: Path) -> bool:
    superproject = _out(["git", "rev-parse", "--show-superproject-working-tree"], cwd=root)
    if superproject:
        return False
    git_dir = _out(["git", "rev-parse", "--git-dir"], cwd=root)
    git_common_dir = _out(["git", "rev-parse", "--git-common-dir"], cwd=root)
    if not git_dir or not git_common_dir:
        return False
    return _resolve_git_path(root, git_dir) != _resolve_git_path(root, git_common_dir)


def _worktree_paths(root: Path) -> tuple[set[Path], str | None]:
    proc = _run(["git", "worktree", "list", "--porcelain"], cwd=root)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "git worktree list failed"
        return set(), detail
    paths: set[Path] = set()
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            paths.add(Path(line.removeprefix("worktree ")).resolve())
    return paths, None


def _local_branch_exists(root: Path, branch: str) -> bool:
    if not branch or branch == "DETACHED":
        return False
    proc = _run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root)
    return proc.returncode == 0


def git_identity(start: Path) -> GitIdentity:
    root_s = _out(["git", "rev-parse", "--show-toplevel"], cwd=start)
    root = Path(root_s).resolve() if root_s else start.resolve()
    branch = _out(["git", "branch", "--show-current"], cwd=root) or "DETACHED"
    head8 = _out(["git", "rev-parse", "--short=8", "HEAD"], cwd=root)
    return GitIdentity(
        root=root,
        branch=branch,
        head8=head8,
        worktree_fingerprint=worktree_fingerprint(root),
        content_fingerprint=content_fingerprint(root),
        linked_worktree=is_linked_worktree(root),
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()  # noqa: UP017 - /usr/bin/python3 may be 3.9.


def state_path(root: Path) -> Path:
    return root / STATE_PATH


def load_state(root: Path) -> dict[str, Any]:
    path = state_path(root)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit("loop_state_missing: run `just codex-loop-start <arc>` first") from exc
    if not isinstance(raw, dict):
        raise SystemExit("loop_state_invalid: expected object")
    state = cast("dict[str, Any]", raw)
    if "events" not in state:
        state["events"] = []
    return state


def write_state(root: Path, state: dict[str, Any]) -> Path:
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def start(args: argparse.Namespace) -> int:
    git = git_identity(Path.cwd())
    state = {
        "schema_version": 1,
        "arc_id": args.arc,
        "started_at": _now(),
        "updated_at": _now(),
        "root": str(git.root),
        "branch": git.branch,
        "head8": git.head8,
        "worktree_fingerprint": git.worktree_fingerprint,
        "content_fingerprint": git.content_fingerprint,
        "linked_worktree": git.linked_worktree,
        "events": [],
        "required_gates": list(REQUIRED_GATES),
    }
    path = write_state(git.root, state)
    print(f"loop_state_started: {path}")
    print(f"arc_id: {args.arc}")
    print(f"next_gate: {REQUIRED_GATES[0]}")
    return 0


def record(args: argparse.Namespace) -> int:
    git = git_identity(Path.cwd())
    state = load_state(git.root)
    latest = _latest_by_phase(state)
    if args.phase == "worktree_ready" and git.linked_worktree is not True:
        raise SystemExit("worktree_ready gate must be recorded in a linked worktree")
    if args.phase in CLEAN_WORKTREE_RECORD_GATES:
        dirty = dirty_status(git.root)
        if dirty:
            raise SystemExit(f"{args.phase} gate requires a clean worktree; status:\n{dirty}")
    if args.phase == "worktree_disposition":
        issues = _worktree_disposition_issues(state, latest, git)
        if issues:
            raise SystemExit(
                "worktree_disposition gate requires completed hygiene:\n- " + "\n- ".join(issues)
            )
    if args.phase == "commit":
        closeout = latest.get("closeout")
        if closeout is None:
            raise SystemExit("commit gate requires a prior closeout gate")
        if git.head8 == closeout.get("head8"):
            raise SystemExit("commit gate must be recorded after a commit changes HEAD")
        if git.content_fingerprint != closeout.get("content_fingerprint"):
            raise SystemExit("commit gate content differs from closeout content")
    events_obj = state.get("events")
    if not isinstance(events_obj, list):
        raise SystemExit("loop_state_invalid: events must be a list")
    events = cast("list[Any]", events_obj)
    event = {
        "recorded_at": _now(),
        "phase": args.phase,
        "status": args.status,
        "command": args.command,
        "evidence": args.evidence,
        "branch": git.branch,
        "head8": git.head8,
        "worktree_fingerprint": git.worktree_fingerprint,
        "content_fingerprint": git.content_fingerprint,
        "linked_worktree": git.linked_worktree,
    }
    if args.phase == "commit":
        closeout = latest.get("closeout")
        if closeout is not None:
            event["validated_phase"] = "closeout"
            event["validated_head8"] = closeout.get("head8")
            event["validated_worktree_fingerprint"] = closeout.get("worktree_fingerprint")
            event["validated_content_fingerprint"] = closeout.get("content_fingerprint")
    events.append(event)
    state["updated_at"] = _now()
    state["branch"] = git.branch
    state["head8"] = git.head8
    state["worktree_fingerprint"] = git.worktree_fingerprint
    state["content_fingerprint"] = git.content_fingerprint
    state["linked_worktree"] = git.linked_worktree
    path = write_state(git.root, state)
    print(f"loop_event_recorded: {args.phase}={args.status}")
    print(f"loop_state: {path}")
    return 0


def _latest_by_phase_with_index(state: dict[str, Any]) -> dict[str, tuple[int, dict[str, Any]]]:
    latest: dict[str, tuple[int, dict[str, Any]]] = {}
    events_obj = state.get("events", [])
    if not isinstance(events_obj, list):
        return latest
    events = cast("list[Any]", events_obj)
    for index, event_obj in enumerate(events):
        if not isinstance(event_obj, dict):
            continue
        event = cast("dict[str, Any]", event_obj)
        phase = event.get("phase")
        if isinstance(phase, str):
            latest[phase] = (index, event)
    return latest


def _latest_by_phase(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {phase: event for phase, (_, event) in _latest_by_phase_with_index(state).items()}


def _worktree_disposition_issues(
    state: dict[str, Any],
    latest: dict[str, dict[str, Any]],
    current: GitIdentity,
) -> list[str]:
    worktree_ready = latest.get("worktree_ready")
    if worktree_ready is None or worktree_ready.get("linked_worktree") is not True:
        return []
    root_raw = state.get("root")
    if not isinstance(root_raw, str) or not root_raw:
        return ["loop state missing original arc worktree root"]
    issues: list[str] = []
    original_root = Path(root_raw).expanduser().resolve()
    worktree_paths, worktree_list_error = _worktree_paths(current.root)
    if worktree_list_error is not None:
        issues.append(f"unable to verify registered worktrees: {worktree_list_error}")
    elif original_root in worktree_paths:
        issues.append(f"original arc worktree is still registered: {original_root}")
    original_branch = worktree_ready.get("branch")
    if isinstance(original_branch, str):
        if _local_branch_exists(current.root, original_branch):
            issues.append(f"local topic branch still exists: {original_branch}")
    return issues


def worktree_disposition_issues(
    state: dict[str, Any],
    latest: dict[str, dict[str, Any]],
    current: GitIdentity,
) -> list[str]:
    return _worktree_disposition_issues(state, latest, current)


def _order_issues(
    latest: dict[str, tuple[int, dict[str, Any]]], required_gates: tuple[str, ...]
) -> list[str]:
    positions: list[tuple[str, int]] = [
        (phase, latest[phase][0]) for phase in required_gates if phase in latest
    ]
    issues: list[str] = []
    for offset, (phase, index) in enumerate(positions[1:], start=1):
        previous_phase, previous_index = positions[offset - 1]
        if previous_index > index:
            issues.append(
                f"gate order invalid: {previous_phase} recorded after {phase}; "
                + "required order is "
                + " -> ".join(required_gates)
            )
            break
    return issues


def _identity_issues(
    state: dict[str, Any],
    latest: dict[str, tuple[int, dict[str, Any]]],
    current: GitIdentity,
) -> list[str]:
    issues: list[str] = []
    state_branch = state.get("branch")
    state_head8 = state.get("head8")
    if state_branch != current.branch or state_head8 != current.head8:
        issues.append(
            "loop state recorded for "
            f"branch={state_branch or '<missing>'} head={state_head8 or '<missing>'}; "
            f"current branch={current.branch} head={current.head8}"
        )
    state_fingerprint = state.get("worktree_fingerprint")
    if state_fingerprint != current.worktree_fingerprint:
        issues.append(
            "loop state recorded for "
            f"worktree={state_fingerprint or '<missing>'}; "
            f"current worktree={current.worktree_fingerprint}"
        )
    closeout_entry = latest.get("closeout")
    if closeout_entry is not None:
        closeout = closeout_entry[1]
        closeout_branch = closeout.get("branch")
        closeout_head8 = closeout.get("head8")
        closeout_worktree = closeout.get("worktree_fingerprint")
        for phase in PRE_COMMIT_WORKTREE_GATES:
            entry = latest.get(phase)
            if entry is None:
                continue
            event = entry[1]
            if event.get("branch") != closeout_branch or event.get("head8") != closeout_head8:
                issues.append(
                    f"{phase} gate recorded for branch={event.get('branch') or '<missing>'} "
                    f"head={event.get('head8') or '<missing>'}; "
                    f"closeout branch={closeout_branch or '<missing>'} "
                    f"head={closeout_head8 or '<missing>'}"
                )
            if event.get("worktree_fingerprint") != closeout_worktree:
                issues.append(
                    f"{phase} gate recorded for "
                    f"worktree={event.get('worktree_fingerprint') or '<missing>'}; "
                    f"closeout worktree={closeout_worktree or '<missing>'}"
                )
    return issues


def check_state(state: dict[str, Any], *, current: GitIdentity | None = None) -> list[str]:
    latest_with_index = _latest_by_phase_with_index(state)
    latest = {phase: event for phase, (_, event) in latest_with_index.items()}
    issues: list[str] = []
    missing = [phase for phase in REQUIRED_GATES if phase not in latest]
    if missing:
        issues.append("missing required gates: " + ", ".join(missing))
    issues.extend(_order_issues(latest_with_index, REQUIRED_GATES))
    if current is not None:
        issues.extend(_identity_issues(state, latest_with_index, current))
    red = latest.get("red")
    if red is not None and red.get("status") != "failed":
        issues.append("red gate must record status=failed before implementation")
    worktree_ready = latest.get("worktree_ready")
    if worktree_ready is not None and worktree_ready.get("linked_worktree") is not True:
        issues.append("worktree_ready gate must be recorded in a linked worktree")
    if "worktree_disposition" in latest and current is not None:
        issues.extend(_worktree_disposition_issues(state, latest, current))
    commit = latest.get("commit")
    closeout = latest.get("closeout")
    if commit is not None and closeout is not None:
        if commit.get("validated_phase") != "closeout":
            issues.append("commit gate must link to the closeout gate it ships")
        if commit.get("validated_head8") != closeout.get("head8"):
            issues.append("commit gate validated_head8 must match closeout head")
        if commit.get("validated_worktree_fingerprint") != closeout.get("worktree_fingerprint"):
            issues.append("commit gate validated_worktree_fingerprint must match closeout worktree")
        if commit.get("validated_content_fingerprint") != closeout.get("content_fingerprint"):
            issues.append("commit gate validated_content_fingerprint must match closeout content")
        if commit.get("content_fingerprint") != closeout.get("content_fingerprint"):
            issues.append("commit gate content must match closeout content")
    for phase in REQUIRED_GATES:
        event = latest.get(phase)
        if event is None or phase == "red":
            continue
        if event.get("status") != "passed":
            issues.append(f"{phase} gate must record status=passed")
    blocked = [
        str(event.get("phase")) for event in latest.values() if event.get("status") == "blocked"
    ]
    if blocked:
        issues.append("blocked gates present: " + ", ".join(sorted(blocked)))
    return issues


def next_gate(state: dict[str, Any]) -> str:
    latest = _latest_by_phase(state)
    for phase in REQUIRED_GATES:
        event = latest.get(phase)
        if event is None:
            return phase
        if phase == "red" and event.get("status") != "failed":
            return phase
        if phase != "red" and event.get("status") != "passed":
            return phase
    return "<complete>"


def status(_: argparse.Namespace) -> int:
    git = git_identity(Path.cwd())
    state = load_state(git.root)
    latest = _latest_by_phase(state)
    print(f"arc_id: {state.get('arc_id', '<missing>')}")
    print(f"branch: {state.get('branch', '<missing>')}")
    print(f"head8: {state.get('head8', '<missing>')}")
    print(f"next_gate: {next_gate(state)}")
    for phase in REQUIRED_GATES:
        event = latest.get(phase)
        current = "<missing>" if event is None else str(event.get("status", "<missing>"))
        print(f"- {phase}: {current}")
    return 0


def check(_: argparse.Namespace) -> int:
    git = git_identity(Path.cwd())
    state = load_state(git.root)
    issues = check_state(state, current=git)
    if issues:
        print("loop state incomplete")
        for issue in issues:
            print(f"- {issue}")
        print(f"next_gate: {next_gate(state)}")
        return 1
    print("loop state OK")
    print(f"arc_id: {state.get('arc_id', '<missing>')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Codex autonomous loop state helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--arc", required=True)
    p_start.set_defaults(func=start)

    p_record = sub.add_parser("record")
    p_record.add_argument("--phase", required=True, choices=REQUIRED_GATES)
    p_record.add_argument("--status", required=True, choices=STATUSES)
    p_record.add_argument("--command", required=True)
    p_record.add_argument("--evidence", required=True)
    p_record.set_defaults(func=record)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=status)

    p_check = sub.add_parser("check")
    p_check.set_defaults(func=check)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

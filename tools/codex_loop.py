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
REQUIRED_GATES = (
    "preflight",
    "plan",
    "red",
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
    "closeout",
)
STATUSES = ("passed", "failed", "blocked", "skipped")
CURRENT_WORKTREE_GATES = (
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
    "closeout",
)


@dataclass(frozen=True)
class GitIdentity:
    root: Path
    branch: str
    head8: str
    worktree_fingerprint: str


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
    events_obj = state.get("events")
    if not isinstance(events_obj, list):
        raise SystemExit("loop_state_invalid: events must be a list")
    events = cast("list[Any]", events_obj)
    events.append(
        {
            "recorded_at": _now(),
            "phase": args.phase,
            "status": args.status,
            "command": args.command,
            "evidence": args.evidence,
            "branch": git.branch,
            "head8": git.head8,
            "worktree_fingerprint": git.worktree_fingerprint,
        }
    )
    state["updated_at"] = _now()
    state["branch"] = git.branch
    state["head8"] = git.head8
    state["worktree_fingerprint"] = git.worktree_fingerprint
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
    for phase in REQUIRED_GATES:
        entry = latest.get(phase)
        if entry is None:
            continue
        event = entry[1]
        event_branch = event.get("branch")
        event_head8 = event.get("head8")
        if event_branch != current.branch or event_head8 != current.head8:
            issues.append(
                f"{phase} gate recorded for "
                f"branch={event_branch or '<missing>'} head={event_head8 or '<missing>'}; "
                f"current branch={current.branch} head={current.head8}"
            )
        event_fingerprint = event.get("worktree_fingerprint")
        if phase in CURRENT_WORKTREE_GATES and event_fingerprint != current.worktree_fingerprint:
            issues.append(
                f"{phase} gate recorded for "
                f"worktree={event_fingerprint or '<missing>'}; "
                f"current worktree={current.worktree_fingerprint}"
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
    p_record.add_argument("--phase", required=True)
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

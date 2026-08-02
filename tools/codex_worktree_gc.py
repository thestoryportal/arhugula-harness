#!/usr/bin/env python3
"""Codex-facing safe git worktree garbage collector.

Dry-run is the default. The reap path removes only linked worktrees that are
clean, not current/default, have no live Claude/Codex session, and are proven
merged either by ancestry or exact merged-PR head SHA. Removal uses the same
mutex and session-lease authority as SessionStart, plus a removal-side quarantine
transaction. Branch refs are never deleted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

SAFE_WORKTREE_REMOVE = Path(__file__).resolve().parent / "hooks" / "safe-worktree-remove.sh"

REGENERABLE_IGNORED = re.compile(
    r"^!! ("
    r"(.*/)?("
    r"\.harness/|__pycache__/|.*\.py[co]|.*\.egg-info/|\.pytest_cache/|"
    r"\.ruff_cache/|\.pyright/|\.mypy_cache/|\.venv/|venv/|env/|"
    r"dist/|build/|htmlcov/|coverage\.xml|\.coverage|\.DS_Store|.*\.swp|"
    r"\.vscode/|\.idea/|node_modules/"
    r")|"
    r"\.claude/(skills/|settings\.local\.json)|"
    r"\.impeccable/"
    r")"
)


@dataclass(frozen=True)
class Worktree:
    path: Path
    head: str
    branch: str


@dataclass(frozen=True)
class MergedPr:
    number: int
    head_ref_name: str
    head_ref_oid: str


@dataclass(frozen=True)
class Disposition:
    worktree: Worktree
    action: str
    reason: str
    proof: str = ""
    size_bytes: int = 0


class SessionState(Enum):
    INACTIVE = "inactive"
    LIVE = "live"
    UNKNOWN = "unknown"


def _run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 30,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        process = subprocess.Popen(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            message = f"command timed out after {timeout} seconds"
            stderr = f"{stderr.rstrip()}\n{message}".lstrip()
            return subprocess.CompletedProcess(args, 124, stdout, stderr)
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args=args, returncode=127, stdout="", stderr=str(exc))


def _out(args: list[str], *, cwd: Path, timeout: int = 30) -> str:
    proc = _run(args, cwd=cwd, timeout=timeout)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def repo_root(start: Path) -> Path:
    out = _out(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(out).resolve() if out else start.resolve()


def default_branch(repo: Path) -> str:
    out = _out(["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd=repo)
    return out.removeprefix("origin/") if out else "main"


def default_ref(repo: Path, branch: str) -> str:
    remote = f"origin/{branch}"
    if _run(["git", "rev-parse", "--verify", "--quiet", remote], cwd=repo).returncode == 0:
        return remote
    return branch


def parse_worktrees(repo: Path) -> list[Worktree]:
    raw = _out(["git", "worktree", "list", "--porcelain"], cwd=repo)
    worktrees: list[Worktree] = []
    record: dict[str, str] = {}
    for line in [*raw.splitlines(), ""]:
        if not line:
            if record.get("path"):
                branch = record.get("branch", "")
                worktrees.append(
                    Worktree(
                        path=Path(record["path"]),
                        head=record.get("head", ""),
                        branch=branch.removeprefix("refs/heads/"),
                    )
                )
            record = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            record["path"] = value
        elif key == "HEAD":
            record["head"] = value
        elif key == "branch":
            record["branch"] = value
    return worktrees


def merged_prs(repo: Path, *, enabled: bool) -> tuple[dict[str, MergedPr], bool]:
    if not enabled:
        return {}, False
    proc = _run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "300",
            "--json",
            "number,headRefName,headRefOid",
        ],
        cwd=repo,
        timeout=20,
    )
    if proc.returncode != 0:
        return {}, False
    try:
        rows = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return {}, False
    prs: dict[str, MergedPr] = {}
    for row in rows:
        branch = str(row.get("headRefName") or "")
        oid = str(row.get("headRefOid") or "")
        if not branch or not oid:
            continue
        prs[branch] = MergedPr(
            number=int(row.get("number") or 0),
            head_ref_name=branch,
            head_ref_oid=oid,
        )
    return prs, True


def physical(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path


def local_state(path: Path) -> list[str]:
    raw = _out(["git", "status", "--porcelain", "--ignored"], cwd=path)
    residue: list[str] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        if REGENERABLE_IGNORED.search(line):
            continue
        residue.append(line)
    return residue


def is_ancestor(repo: Path, head: str, ref: str) -> bool:
    if not head or not ref:
        return False
    return _run(["git", "merge-base", "--is-ancestor", head, ref], cwd=repo).returncode == 0


def session_state(path: Path, *, home: Path) -> SessionState:
    env = os.environ.copy()
    env.update({"CLAUDE_PROJECT_DIR": str(path), "HOME": str(home)})
    proc = _run(
        ["/bin/bash", str(SAFE_WORKTREE_REMOVE), "--status", str(path)],
        cwd=path,
        timeout=10,
        env=env,
    )
    if proc.returncode == 0:
        return SessionState.LIVE
    if proc.returncode == 1:
        return SessionState.INACTIVE
    return SessionState.UNKNOWN


def tree_size(path: Path) -> int:
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d != ".git"]
            for name in files:
                try:
                    total += (Path(root) / name).stat().st_size
                except OSError:
                    continue
    except OSError:
        return 0
    return total


def classify(
    repo: Path,
    worktrees: list[Worktree],
    *,
    current: Path,
    default: str,
    base_ref: str,
    prs: dict[str, MergedPr],
    gh_available: bool,
    include_sizes: bool,
    home: Path,
) -> list[Disposition]:
    current_physical = physical(current)
    dispositions: list[Disposition] = []
    for wt in worktrees:
        size = tree_size(wt.path) if include_sizes else 0
        if physical(wt.path) == current_physical:
            dispositions.append(Disposition(wt, "skip", "current-worktree", size_bytes=size))
            continue
        if not wt.branch:
            dispositions.append(Disposition(wt, "skip", "detached-head", size_bytes=size))
            continue
        if wt.branch == default:
            dispositions.append(Disposition(wt, "skip", "default-branch", size_bytes=size))
            continue
        residue = local_state(wt.path)
        if residue:
            reason = "local-state: " + ", ".join(residue[:3])
            dispositions.append(Disposition(wt, "skip", reason[:220], size_bytes=size))
            continue
        state = session_state(wt.path, home=home)
        if state is SessionState.LIVE:
            dispositions.append(
                Disposition(wt, "skip", "live-claude-codex-session", size_bytes=size)
            )
            continue
        if state is SessionState.UNKNOWN:
            dispositions.append(
                Disposition(wt, "skip", "session-state-unavailable", size_bytes=size)
            )
            continue
        if is_ancestor(repo, wt.head, base_ref):
            dispositions.append(
                Disposition(wt, "candidate", "merged-by-ancestry", base_ref, size_bytes=size)
            )
            continue
        pr = prs.get(wt.branch)
        if pr and pr.head_ref_oid == wt.head:
            dispositions.append(
                Disposition(
                    wt,
                    "candidate",
                    "merged-pr-head",
                    f"PR #{pr.number}",
                    size_bytes=size,
                )
            )
            continue
        if not gh_available:
            dispositions.append(
                Disposition(wt, "skip", "no-merge-proof-gh-unavailable", size_bytes=size)
            )
        elif pr:
            dispositions.append(Disposition(wt, "skip", "merged-pr-head-mismatch", size_bytes=size))
        else:
            dispositions.append(Disposition(wt, "skip", "no-merge-proof", size_bytes=size))
    return dispositions


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def render(dispositions: list[Disposition], *, reap: bool, gh_available: bool) -> str:
    candidates = [d for d in dispositions if d.action == "candidate"]
    skipped = [d for d in dispositions if d.action != "candidate"]
    total = sum(d.size_bytes for d in candidates)
    lines = [
        f"Codex worktree GC {'reap' if reap else 'dry-run'}",
        f"gh_merged_prs_available: {str(gh_available).lower()}",
        f"candidates: {len(candidates)} ({human_size(total)})",
    ]
    for d in candidates:
        proof = f", {d.proof}" if d.proof else ""
        lines.append(
            f"  - {d.worktree.path} [{d.worktree.branch}] "
            f"{d.reason}{proof}, {human_size(d.size_bytes)}"
        )
    lines.append(f"skipped: {len(skipped)}")
    for d in skipped:
        lines.append(f"  - {d.worktree.path} [{d.worktree.branch or 'detached'}] {d.reason}")
    if not reap and candidates:
        lines.append("Run `just codex-worktree-gc --reap` to remove only the candidates above.")
    return "\n".join(lines)


def to_json(dispositions: list[Disposition], *, gh_available: bool) -> str:
    payload: dict[str, Any] = {
        "gh_merged_prs_available": gh_available,
        "candidates": [],
        "skipped": [],
    }
    for d in dispositions:
        row = {
            "path": str(d.worktree.path),
            "branch": d.worktree.branch,
            "head": d.worktree.head,
            "reason": d.reason,
            "proof": d.proof,
            "size_bytes": d.size_bytes,
        }
        payload["candidates" if d.action == "candidate" else "skipped"].append(row)
    return json.dumps(payload, indent=2, sort_keys=True)


def reap_candidates(repo: Path, dispositions: list[Disposition]) -> int:
    failures = 0
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(repo)
    for d in dispositions:
        if d.action != "candidate":
            continue
        proc = _run(
            ["/bin/bash", str(SAFE_WORKTREE_REMOVE), str(d.worktree.path)],
            cwd=repo,
            timeout=60,
            env=env,
        )
        if proc.returncode == 3:
            print(f"skipped removal of {d.worktree.path}: live Claude/Codex session")
            continue
        if proc.returncode == 4:
            print(f"skipped removal of {d.worktree.path}: local state appeared")
            continue
        if proc.returncode == 7:
            print(f"skipped removal of {d.worktree.path}: retained process reference")
            continue
        if proc.returncode == 8:
            print(f"restored interrupted quarantine for {d.worktree.path}; retry later")
            continue
        if proc.returncode != 0:
            failures += 1
            print(
                f"failed to remove {d.worktree.path}: {proc.stderr.strip() or proc.stdout.strip()}",
                file=sys.stderr,
            )
    _run(["git", "worktree", "prune"], cwd=repo, timeout=30)
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository/worktree path to inspect")
    parser.add_argument("--reap", action="store_true", help="remove safe candidates")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--no-gh", action="store_true", help="skip GitHub PR merge proof")
    parser.add_argument("--no-size", action="store_true", help="skip worktree size calculation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cwd = Path(args.repo).resolve()
    repo = repo_root(cwd)
    default = default_branch(repo)
    base_ref = default_ref(repo, default)
    prs, gh_available = merged_prs(repo, enabled=not args.no_gh)
    worktrees = parse_worktrees(repo)
    dispositions = classify(
        repo,
        worktrees,
        current=repo,
        default=default,
        base_ref=base_ref,
        prs=prs,
        gh_available=gh_available,
        include_sizes=not args.no_size,
        home=Path.home(),
    )
    if args.json:
        print(to_json(dispositions, gh_available=gh_available))
    else:
        print(render(dispositions, reap=args.reap, gh_available=gh_available))
    failures = reap_candidates(repo, dispositions) if args.reap else 0
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

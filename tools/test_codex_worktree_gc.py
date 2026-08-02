"""Tests for the Codex worktree garbage collector."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_worktree_gc as gc

ROOT = Path(__file__).resolve().parents[1]
# This module exercises normal hooks even when invoked from an isolated reviewer.
os.environ.pop("HARNESS_CODEX_REVIEW_ISOLATED", None)


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "codex@example.test")
    _git(repo, "config", "user.name", "Codex Test")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "base")
    _git(repo, "branch", "-m", "main")
    return repo


def _add_worktree(repo: Path, tmp_path: Path, branch: str) -> Path:
    path = tmp_path / branch.replace("/", "-")
    _git(repo, "branch", branch)
    _git(repo, "worktree", "add", str(path), branch)
    return path


def _run_hook(
    script: str,
    worktree: Path,
    session_id: str,
    *,
    home: Path,
    action: str | None = None,
    isolated: bool = False,
    source: str = "startup",
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({"CLAUDE_PROJECT_DIR": str(worktree), "HOME": str(home)})
    if isolated:
        env["HARNESS_CODEX_REVIEW_ISOLATED"] = "1"
    args = ["bash", str(ROOT / "tools" / "hooks" / script)]
    if action is not None:
        args.append(action)
    return subprocess.run(
        args,
        cwd=worktree,
        input=json.dumps({"session_id": session_id, "cwd": str(worktree), "source": source}),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )


def _dispositions(repo: Path) -> list[gc.Disposition]:
    return gc.classify(
        repo,
        gc.parse_worktrees(repo),
        current=repo,
        default="main",
        base_ref="main",
        prs={},
        gh_available=False,
        include_sizes=False,
        home=repo,
    )


def test_merged_clean_nondefault_worktree_is_candidate_by_ancestry(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    path = _add_worktree(repo, tmp_path, "codex/done")

    dispositions = _dispositions(repo)

    candidate = next(d for d in dispositions if d.worktree.path == path)
    assert candidate.action == "candidate"
    assert candidate.reason == "merged-by-ancestry"


def test_dirty_worktree_is_skipped_even_when_branch_is_merged(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    path = _add_worktree(repo, tmp_path, "codex/dirty")
    (path / "scratch.txt").write_text("local\n", encoding="utf-8")

    dispositions = _dispositions(repo)

    skipped = next(d for d in dispositions if d.worktree.path == path)
    assert skipped.action == "skip"
    assert skipped.reason.startswith("local-state:")


def test_unmerged_worktree_is_skipped_without_pr_proof(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    path = _add_worktree(repo, tmp_path, "codex/unmerged")
    (path / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-m", "feature")

    dispositions = _dispositions(repo)

    skipped = next(d for d in dispositions if d.worktree.path == path)
    assert skipped.action == "skip"
    assert skipped.reason == "no-merge-proof-gh-unavailable"


def test_exact_merged_pr_head_is_candidate_without_ancestry(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    path = _add_worktree(repo, tmp_path, "codex/squashed")
    (path / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-m", "feature")
    head = _git(path, "rev-parse", "HEAD")

    dispositions = gc.classify(
        repo,
        gc.parse_worktrees(repo),
        current=repo,
        default="main",
        base_ref="main",
        prs={"codex/squashed": gc.MergedPr(12, "codex/squashed", head)},
        gh_available=True,
        include_sizes=False,
        home=repo,
    )

    candidate = next(d for d in dispositions if d.worktree.path == path)
    assert candidate.action == "candidate"
    assert candidate.reason == "merged-pr-head"
    assert candidate.proof == "PR #12"


def test_merged_pr_name_with_different_head_is_skipped(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    path = _add_worktree(repo, tmp_path, "codex/reused")
    (path / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-m", "feature")

    dispositions = gc.classify(
        repo,
        gc.parse_worktrees(repo),
        current=repo,
        default="main",
        base_ref="main",
        prs={"codex/reused": gc.MergedPr(12, "codex/reused", "0" * 40)},
        gh_available=True,
        include_sizes=False,
        home=repo,
    )

    skipped = next(d for d in dispositions if d.worktree.path == path)
    assert skipped.action == "skip"
    assert skipped.reason == "merged-pr-head-mismatch"


def test_reap_removes_only_candidates_and_keeps_branches(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    done = _add_worktree(repo, tmp_path, "codex/done")
    dirty = _add_worktree(repo, tmp_path, "codex/dirty")
    (dirty / "scratch.txt").write_text("local\n", encoding="utf-8")

    rc = gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"])

    assert rc == 0
    assert not done.exists()
    assert dirty.exists()
    assert _git(repo, "rev-parse", "--verify", "codex/done")


def test_run_timeout_delivers_term_before_forced_kill(tmp_path: Path) -> None:
    marker = tmp_path / "term-delivered"
    env = os.environ.copy()
    env["TERM_MARKER"] = str(marker)

    proc = gc._run(
        [
            "bash",
            "-c",
            "trap 'printf term > \"$TERM_MARKER\"; exit 42' TERM; while :; do sleep 1; done",
        ],
        cwd=tmp_path,
        timeout=1,
        env=env,
    )

    assert proc.returncode == 124
    assert marker.read_text(encoding="utf-8") == "term"


def test_reap_rechecks_session_lease_after_candidate_classification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_repo(tmp_path)
    worktree = _add_worktree(repo, tmp_path, "codex/classified-live")
    dispositions = _dispositions(repo)
    candidate = next(d for d in dispositions if d.worktree.path == worktree)
    assert candidate.action == "candidate"
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    start = _run_hook(
        "codex-session-start.sh",
        worktree,
        "classified-live",
        home=home,
        isolated=True,
    )
    assert start.returncode == 0, start.stderr
    lease = next((repo / ".git" / "codex-worktree-sessions").rglob("session-classified-live.lease"))
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "active"
    os.utime(lease, (0, 0))

    assert gc.reap_candidates(repo, dispositions) == 0
    assert worktree.exists()

    end = _run_hook(
        "codex-session-end.sh",
        worktree,
        "classified-live",
        home=home,
        isolated=True,
    )
    assert end.returncode == 0, end.stderr


def test_normal_session_start_activates_lease_until_session_end(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    hook_root = tmp_path / "normal-hook-root"
    hook_dir = hook_root / "tools" / "hooks"
    posture_dir = hook_root / ".codex" / "hooks"
    roadmap_dir = hook_root / "tools" / "roadmap-audit"
    hook_dir.mkdir(parents=True)
    posture_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    for name in (
        "codex-session-start.sh",
        "codex-session-end.sh",
        "session-lease.sh",
        "lib.sh",
    ):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    (posture_dir / "session_start.py").write_text("print('posture ready')\n", encoding="utf-8")
    (roadmap_dir / "session-start.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (hook_dir / "loop-gc.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (hook_dir / "session-end-cleanup.sh").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
    env = os.environ.copy()
    env.pop("HARNESS_CODEX_REVIEW_ISOLATED", None)
    env.update({"CLAUDE_PROJECT_DIR": str(repo), "HOME": str(home)})
    payload = json.dumps({"session_id": "normal-activation", "cwd": str(repo)})

    start = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=repo,
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert start.returncode == 0, start.stderr
    assert json.loads(start.stdout)["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    lease = next(
        (repo / ".git" / "codex-worktree-sessions").rglob("session-normal-activation.lease")
    )
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "active"

    end = subprocess.run(
        ["bash", str(hook_dir / "codex-session-end.sh")],
        cwd=repo,
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert end.returncode == 0, end.stderr
    assert not lease.exists()


def test_reap_from_linked_worktree_never_removes_that_worktree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    worktree = _add_worktree(repo, tmp_path, "codex/current")
    previous = Path.cwd()

    try:
        os.chdir(worktree)
        assert gc.repo_root(Path(".")) == worktree.resolve()
        rc = gc.main(["--repo", ".", "--reap", "--no-gh", "--no-size"])
    finally:
        os.chdir(previous)

    assert rc == 0
    assert worktree.exists()
    assert "current-worktree" in capsys.readouterr().out


def test_production_gc_refuses_aged_active_session_until_session_end(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path)
    worktree = _add_worktree(repo, tmp_path, "codex/live")
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    start = _run_hook(
        "codex-session-start.sh",
        worktree,
        "gc-live",
        home=home,
        isolated=True,
    )
    assert start.returncode == 0, start.stderr
    lease = next((repo / ".git" / "codex-worktree-sessions").rglob("session-gc-live.lease"))
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "active"
    os.utime(lease, (0, 0))

    assert gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"]) == 0
    assert worktree.exists()

    end = _run_hook(
        "codex-session-end.sh",
        worktree,
        "gc-live",
        home=home,
        isolated=True,
    )
    assert end.returncode == 0, end.stderr
    assert gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"]) == 0
    assert not worktree.exists()


def test_production_gc_recovers_abandoned_starting_lease_after_grace(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path)
    worktree = _add_worktree(repo, tmp_path, "codex/abandoned-start")
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("HARNESS_WORKTREE_STARTING_LEASE_WINDOW_MIN", "3")

    start = _run_hook(
        "session-lease.sh",
        worktree,
        "gc-abandoned",
        home=home,
        action="start",
    )
    assert start.returncode == 0, start.stderr
    lease = next((repo / ".git" / "codex-worktree-sessions").rglob("session-gc-abandoned.lease"))
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "starting"

    assert gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"]) == 0
    assert worktree.exists()

    os.utime(lease, (0, 0))
    assert gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"]) == 0
    assert not worktree.exists()


def test_session_start_posture_failure_releases_starting_lease(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    hook_root = tmp_path / "hook-root"
    hook_dir = hook_root / "tools" / "hooks"
    posture_dir = hook_root / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    posture_dir.mkdir(parents=True)
    for name in ("codex-session-start.sh", "session-lease.sh", "lib.sh"):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    (posture_dir / "session_start.py").write_text("raise SystemExit(9)\n", encoding="utf-8")

    env = os.environ.copy()
    env.update({"CLAUDE_PROJECT_DIR": str(repo), "HOME": str(home)})
    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=repo,
        input=json.dumps({"session_id": "posture-failed", "cwd": str(repo)}),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 9
    assert not list((repo / ".git" / "codex-worktree-sessions").rglob("*.lease"))


def test_failed_repeated_compact_start_preserves_active_lease_until_session_end(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    worktree = _add_worktree(repo, tmp_path, "codex/compact-failure")
    home = tmp_path / "home"
    home.mkdir()

    first = _run_hook(
        "codex-session-start.sh",
        worktree,
        "same-root",
        home=home,
        isolated=True,
    )
    assert first.returncode == 0, first.stderr
    lease = next((repo / ".git" / "codex-worktree-sessions").rglob("session-same-root.lease"))
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "active"

    hook_root = tmp_path / "failing-hook-root"
    hook_dir = hook_root / "tools" / "hooks"
    posture_dir = hook_root / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    posture_dir.mkdir(parents=True)
    for name in ("codex-session-start.sh", "session-lease.sh", "lib.sh"):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    (posture_dir / "session_start.py").write_text("raise SystemExit(9)\n", encoding="utf-8")

    env = os.environ.copy()
    env.update({"CLAUDE_PROJECT_DIR": str(worktree), "HOME": str(home)})
    repeated = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=worktree,
        input=json.dumps({"session_id": "same-root", "cwd": str(worktree), "source": "compact"}),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert repeated.returncode == 9
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "active"
    os.utime(lease, (0, 0))
    assert gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"]) == 0
    assert worktree.exists()

    end = _run_hook(
        "codex-session-end.sh",
        worktree,
        "same-root",
        home=home,
        isolated=True,
    )
    assert end.returncode == 0, end.stderr
    assert gc.main(["--repo", str(repo), "--reap", "--no-gh", "--no-size"]) == 0
    assert not worktree.exists()


def test_successful_repeated_compact_start_preserves_active_lease_identity(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    worktree = _add_worktree(repo, tmp_path, "codex/compact-success")
    home = tmp_path / "home"
    home.mkdir()

    first = _run_hook(
        "codex-session-start.sh",
        worktree,
        "same-root-success",
        home=home,
        isolated=True,
    )
    assert first.returncode == 0, first.stderr
    lease = next(
        (repo / ".git" / "codex-worktree-sessions").rglob("session-same-root-success.lease")
    )
    original_inode = lease.stat().st_ino
    original_content = lease.read_text(encoding="utf-8")

    repeated = _run_hook(
        "codex-session-start.sh",
        worktree,
        "same-root-success",
        home=home,
        isolated=True,
        source="compact",
    )

    assert repeated.returncode == 0, repeated.stderr
    assert lease.stat().st_ino == original_inode
    assert lease.read_text(encoding="utf-8") == original_content

"""Tests for the Codex worktree garbage collector."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_worktree_gc as gc


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

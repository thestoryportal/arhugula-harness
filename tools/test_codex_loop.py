"""Tests for the Codex autonomous loop state tool.

The loop state is the local, machine-readable companion to the human-readable
Codex workflow docs. It records gates as evidence, not agent memory.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "codex_loop.py"
FULL_LIFECYCLE_GATES = [
    "worktree_ready",
    "preflight",
    "plan",
    "red",
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
    "closeout",
    "commit",
    "push",
    "pr_opened",
    "ci_green",
    "merged",
    "post_merge_refresh",
    "main_synced",
    "worktree_disposition",
]


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return proc.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "codex@example.test")
    _git(repo, "config", "user.name", "Codex Test")
    (repo / "README.md").write_text("# repo\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "baseline")
    return repo


def _init_linked_worktree(tmp_path: Path) -> Path:
    repo = _init_repo(tmp_path)
    worktree = tmp_path / "worktree"
    _git(repo, "worktree", "add", str(worktree), "-b", "feature")
    return worktree


def _record_gate(repo: Path, phase: str, status: str) -> subprocess.CompletedProcess[str]:
    return _run(
        repo,
        "record",
        "--phase",
        phase,
        "--status",
        status,
        "--command",
        f"just {phase}",
        "--evidence",
        f"{phase} evidence",
    )


def _record_full_lifecycle(repo: Path, *, red_status: str = "failed") -> None:
    marker = _git(repo, "rev-parse", "--short", "HEAD")
    (repo / "README.md").write_text(
        f"# repo\nfull lifecycle {marker} {red_status}\n", encoding="utf-8"
    )
    for phase in FULL_LIFECYCLE_GATES:
        if phase == "commit":
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-m", "full lifecycle change")
        status = red_status if phase == "red" else "passed"
        proc = _record_gate(repo, phase, status)
        assert proc.returncode == 0, proc.stderr


def test_start_writes_ignored_loop_state_with_git_identity(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    proc = _run(repo, "start", "--arc", "B-LOOP")

    assert proc.returncode == 0, proc.stderr
    state_path = repo / ".harness" / "codex_loop_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload["arc_id"] == "B-LOOP"
    assert payload["branch"] == _git(repo, "branch", "--show-current")
    assert payload["head8"] == _git(repo, "rev-parse", "--short=8", "HEAD")
    assert isinstance(payload["worktree_fingerprint"], str)
    assert payload["events"] == []
    assert payload["required_gates"] == FULL_LIFECYCLE_GATES


def test_check_requires_git_shipping_lifecycle_after_closeout(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    (repo / "README.md").write_text("# repo\nreviewed change\n", encoding="utf-8")

    for phase in (
        "worktree_ready",
        "preflight",
        "plan",
        "red",
        "implementation",
        "narrow_verify",
        "local_gate",
        "decorrelated_review",
        "closeout",
    ):
        proc = _record_gate(repo, phase, "failed" if phase == "red" else "passed")
        assert proc.returncode == 0, proc.stderr

    proc = _run(repo, "check")

    assert proc.returncode == 1
    assert (
        "missing required gates: "
        "commit, push, pr_opened, ci_green, merged, post_merge_refresh, "
        "main_synced, worktree_disposition"
    ) in proc.stdout


def test_record_worktree_ready_rejects_root_checkout(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0

    proc = _record_gate(repo, "worktree_ready", "passed")

    assert proc.returncode == 1
    assert "worktree_ready gate must be recorded in a linked worktree" in proc.stderr


def test_commit_gate_rejects_content_changed_after_closeout(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    (repo / "README.md").write_text("# repo\nreviewed change\n", encoding="utf-8")
    for phase in (
        "worktree_ready",
        "preflight",
        "plan",
        "red",
        "implementation",
        "narrow_verify",
        "local_gate",
        "decorrelated_review",
        "closeout",
    ):
        proc = _record_gate(repo, phase, "failed" if phase == "red" else "passed")
        assert proc.returncode == 0, proc.stderr

    (repo / "README.md").write_text("# repo\nunreviewed change\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "change after closeout")

    proc = _record_gate(repo, "commit", "passed")

    assert proc.returncode == 1
    assert "commit gate content differs from closeout content" in proc.stderr


def test_commit_gate_rejects_mode_changed_after_closeout(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    _git(repo, "config", "core.filemode", "true")
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    for phase in (
        "worktree_ready",
        "preflight",
        "plan",
        "red",
        "implementation",
        "narrow_verify",
        "local_gate",
        "decorrelated_review",
        "closeout",
    ):
        proc = _record_gate(repo, phase, "failed" if phase == "red" else "passed")
        assert proc.returncode == 0, proc.stderr

    (repo / "README.md").chmod(0o755)
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "mode change after closeout")

    proc = _record_gate(repo, "commit", "passed")

    assert proc.returncode == 1
    assert "commit gate content differs from closeout content" in proc.stderr


def test_check_accepts_lifecycle_completed_after_main_sync_on_main(tmp_path: Path) -> None:
    main_repo = _init_repo(tmp_path)
    repo = tmp_path / "feature"
    _git(main_repo, "worktree", "add", str(repo), "-b", "feature")
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    (repo / "README.md").write_text("# repo\nfeature change\n", encoding="utf-8")
    for phase in (
        "worktree_ready",
        "preflight",
        "plan",
        "red",
        "implementation",
        "narrow_verify",
        "local_gate",
        "decorrelated_review",
        "closeout",
    ):
        proc = _record_gate(repo, phase, "failed" if phase == "red" else "passed")
        assert proc.returncode == 0, proc.stderr
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "feature change")
    for phase in ("commit", "push", "pr_opened", "ci_green", "merged"):
        proc = _record_gate(repo, phase, "passed")
        assert proc.returncode == 0, proc.stderr

    _git(main_repo, "merge", "--ff-only", "feature")
    state_text = (repo / ".harness" / "codex_loop_state.json").read_text(encoding="utf-8")
    state_dir = main_repo / ".harness"
    state_dir.mkdir(exist_ok=True)
    (state_dir / "codex_loop_state.json").write_text(state_text, encoding="utf-8")
    for phase in ("post_merge_refresh", "main_synced", "worktree_disposition"):
        proc = _record_gate(main_repo, phase, "passed")
        assert proc.returncode == 0, proc.stderr

    proc = _run(main_repo, "check")

    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_check_requires_required_gates_and_red_failure_evidence(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0

    incomplete = _run(repo, "check")

    assert incomplete.returncode == 1
    assert "missing required gates" in incomplete.stdout

    _record_full_lifecycle(repo, red_status="passed")

    bad_red = _run(repo, "check")

    assert bad_red.returncode == 1
    assert "red gate must record status=failed" in bad_red.stdout

    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    _record_full_lifecycle(repo)

    complete = _run(repo, "check")

    assert complete.returncode == 0
    assert "loop state OK" in complete.stdout


def test_check_rejects_latest_required_gate_events_recorded_out_of_order(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    (repo / "README.md").write_text("# repo\nout-of-order change\n", encoding="utf-8")

    for phase in (
        "worktree_ready",
        "preflight",
        "plan",
        "implementation",
        "narrow_verify",
        "local_gate",
        "decorrelated_review",
        "closeout",
        "commit",
        "push",
        "pr_opened",
        "ci_green",
        "merged",
        "post_merge_refresh",
        "main_synced",
        "worktree_disposition",
    ):
        if phase == "commit":
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-m", "out-of-order change")
        proc = _record_gate(repo, phase, "passed")
        assert proc.returncode == 0, proc.stderr
    late_red = _record_gate(repo, "red", "failed")
    assert late_red.returncode == 0, late_red.stderr

    proc = _run(repo, "check")

    assert proc.returncode == 1
    assert "gate order invalid: red recorded after implementation" in proc.stdout


def test_check_rejects_loop_state_from_stale_branch_or_head(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0

    _record_full_lifecycle(repo)

    state_path = repo / ".harness" / "codex_loop_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["branch"] = "stale-branch"
    payload["events"][-1]["head8"] = "deadbeef"
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = _run(repo, "check")

    assert proc.returncode == 1
    assert "loop state recorded for branch=stale-branch" in proc.stdout


def test_check_rejects_post_gate_worktree_edits(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0

    _record_full_lifecycle(repo)
    (repo / "README.md").write_text("# repo\npost-gate edit\n", encoding="utf-8")

    proc = _run(repo, "check")

    assert proc.returncode == 1
    assert "loop state recorded for worktree=" in proc.stdout


def test_status_reports_next_missing_gate(tmp_path: Path) -> None:
    repo = _init_linked_worktree(tmp_path)
    assert _run(repo, "start", "--arc", "B-LOOP").returncode == 0
    assert (
        _run(
            repo,
            "record",
            "--phase",
            "worktree_ready",
            "--status",
            "passed",
            "--command",
            "git worktree ready",
            "--evidence",
            "linked worktree",
        ).returncode
        == 0
    )

    proc = _run(repo, "status")

    assert proc.returncode == 0
    assert "next_gate: preflight" in proc.stdout


def test_justfile_exposes_autonomous_loop_and_coderabbit_review() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert 'codex-autonomous-arc arc="manual"' in justfile
    assert "codex-loop-record *args" in justfile
    assert "codex-loop-check" in justfile
    assert "coderabbit-review *ARGS" in justfile
    assert (
        "worktree_ready -> preflight -> plan -> red(status=failed) -> implementation "
        "-> narrow_verify -> local_gate -> decorrelated_review -> closeout -> commit "
        "-> push -> pr_opened -> ci_green -> merged -> post_merge_refresh -> "
        "main_synced -> worktree_disposition"
    ) in justfile
    assert ".harness/codex_loop_state.json" in gitignore


def test_just_codex_loop_record_preserves_spaced_arguments() -> None:
    state_path = ROOT / ".harness" / "codex_loop_state.json"
    original = state_path.read_bytes() if state_path.exists() else None
    try:
        start = subprocess.run(
            ["just", "codex-loop-start", "TEST-SPACES"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert start.returncode == 0, start.stderr
        record = subprocess.run(
            [
                "just",
                "codex-loop-record",
                "--phase",
                "plan",
                "--status",
                "passed",
                "--command",
                "controller plan",
                "--evidence",
                "evidence with spaces",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert record.returncode == 0, record.stderr
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        event = payload["events"][-1]
        assert event["command"] == "controller plan"
        assert event["evidence"] == "evidence with spaces"
    finally:
        if original is None:
            state_path.unlink(missing_ok=True)
        else:
            state_path.write_bytes(original)

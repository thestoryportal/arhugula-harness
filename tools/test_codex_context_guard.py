"""Tests for Codex deterministic context guard.

The guard is the Codex-side anti-rot instrument: it turns context freshness,
worktree isolation, cite/drift hygiene, and closeout tracking into objective
checks instead of remembered process.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_context_guard as cg


def _state(**overrides) -> cg.GuardState:
    base = cg.GuardState(
        root=Path("/repo"),
        cwd=Path("/repo"),
        branch="feature",
        default_branch="main",
        head8="abc12345",
        git_dir=".git/worktrees/feature",
        is_linked_worktree=True,
        status_entries=[],
        changed_files=[],
        dashboard=cg.DashboardState(
            hash="abc",
            git_head="abc12345",
            last_refreshed="2026-06-05T00:00:00-06:00",
        ),
        computed_hash="abc",
        open_prs="",
        open_prs_available=True,
        fork_doc_count=0,
        latest_retirement_batch=".harness/phase-7d-retirement-events-batch-51.md",
        lag_expected=False,
        dashboard_snapshot_current=True,
    )
    return cg.GuardState(**{**base.__dict__, **overrides})


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
    (repo / ".harness").mkdir()
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `000000000000` |",
                "| `git_head` | `00000000` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "baseline")
    return repo


def test_root_checkout_edits_are_hard_failure() -> None:
    state = _state(
        git_dir=".git",
        is_linked_worktree=False,
        status_entries=[" M AGENTS.md"],
        changed_files=["AGENTS.md"],
    )

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "ROOT_CHECKOUT_EDIT" and f.severity == "hard" for f in findings)


def test_linked_worktree_edits_satisfy_isolation() -> None:
    state = _state(status_entries=[" M AGENTS.md"], changed_files=["AGENTS.md"])

    findings = cg.validate(state, mode="closeout")

    assert not any(f.code == "ROOT_CHECKOUT_EDIT" for f in findings)


def test_design_and_implementation_mix_is_hard_failure() -> None:
    state = _state(
        status_entries=[
            " M design-substrate/Spec_Control_Plane_v1_30.md",
            " M harness-cp/src/harness_cp/foo.py",
        ],
        changed_files=[
            "design-substrate/Spec_Control_Plane_v1_30.md",
            "harness-cp/src/harness_cp/foo.py",
        ],
    )

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "DESIGN_IMPL_MIX" and f.severity == "hard" for f in findings)


def test_design_and_codex_tooling_mix_is_hard_failure() -> None:
    state = _state(
        status_entries=[
            " M .harness/class_3_drift_codex_guard.md",
            " M tools/codex_context_guard.py",
        ],
        changed_files=[
            ".harness/class_3_drift_codex_guard.md",
            "tools/codex_context_guard.py",
        ],
    )

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "DESIGN_IMPL_MIX" and f.severity == "hard" for f in findings)


def test_dashboard_snapshot_does_not_count_as_design_impl_mix() -> None:
    state = _state(
        status_entries=[
            " M .harness/class_1_fork_harness_toml_default_discovery_unimplemented.md",
            " M Project_Roadmap_v1.md",
            " M tools/dashboard/roadmap.html",
        ],
        changed_files=[
            ".harness/class_1_fork_harness_toml_default_discovery_unimplemented.md",
            "Project_Roadmap_v1.md",
            "tools/dashboard/roadmap.html",
        ],
        dashboard_snapshot_current=True,
    )

    findings = cg.validate(state, mode="closeout")

    assert not any(f.code == "DESIGN_IMPL_MIX" for f in findings)


def test_committed_diff_range_drives_guard_changed_files(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "Project_Roadmap_v1.md").write_text("# roadmap\n", encoding="utf-8")
    (repo / "tools").mkdir()
    (repo / "tools" / "codex_context_guard.py").write_text("# guard\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "guard change")
    head = _git(repo, "rev-parse", "HEAD")

    state = cg.derive(repo, base_ref=base, head_ref=head)

    assert state.changed_files == ["Project_Roadmap_v1.md", "tools/codex_context_guard.py"]


def test_committed_diff_range_enforces_design_impl_mix_in_clean_checkout(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD")
    (repo / ".harness" / "class_3_drift_codex_guard.md").write_text("drift\n", encoding="utf-8")
    (repo / ".codex").mkdir()
    (repo / ".codex" / "hooks").mkdir()
    (repo / ".codex" / "hooks" / "stop_gate.py").write_text("# hook\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "mixed committed change")
    head = _git(repo, "rev-parse", "HEAD")

    state = cg.derive(repo, base_ref=base, head_ref=head)
    findings = cg.validate(state, mode="check")

    assert state.status_entries == []
    assert any(f.code == "DESIGN_IMPL_MIX" and f.severity == "hard" for f in findings)


def test_branch_diff_mode_uses_merge_base_when_worktree_is_clean(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "-m", "main")
    _git(repo, "checkout", "-b", "feature")
    (repo / ".harness" / "class_3_drift_codex_guard.md").write_text("drift\n", encoding="utf-8")
    (repo / "justfile").write_text("codex-context-check:\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "mixed committed branch change")

    state = cg.derive(repo, include_branch_diff=True)
    findings = cg.validate(state, mode="check")

    assert state.status_entries == []
    assert state.changed_files == [".harness/class_3_drift_codex_guard.md", "justfile"]
    assert any(f.code == "DESIGN_IMPL_MIX" and f.severity == "hard" for f in findings)


def test_dashboard_drift_on_default_branch_is_hard_failure() -> None:
    state = _state(
        branch="main",
        git_dir=".git",
        is_linked_worktree=False,
        computed_hash="newhash",
        dashboard=cg.DashboardState(hash="oldhash", git_head="abc12345", last_refreshed="old"),
    )

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "ROADMAP_DASHBOARD_DRIFT" and f.severity == "hard" for f in findings)


def test_dashboard_drift_allowance_does_not_downgrade_default_branch() -> None:
    state = _state(
        branch="main",
        git_dir=".git",
        is_linked_worktree=False,
        computed_hash="newhash",
        dashboard=cg.DashboardState(hash="oldhash", git_head="abc12345", last_refreshed="old"),
    )

    findings = cg.validate(state, mode="preflight", allow_dashboard_drift=True)

    assert any(f.code == "ROADMAP_DASHBOARD_DRIFT" and f.severity == "hard" for f in findings)
    assert not any(f.code == "ROADMAP_DASHBOARD_DRIFT_ALLOWED" for f in findings)


def test_lag_expected_dashboard_drift_has_specific_warning_code() -> None:
    state = _state(branch="main", computed_hash="newhash", lag_expected=True)

    findings = cg.validate(state, mode="preflight")

    assert any(
        f.code == "ROADMAP_DASHBOARD_LAG_EXPECTED" and f.severity == "warn" for f in findings
    )
    assert not any(f.code == "ROADMAP_DASHBOARD_BRANCH_DIVERGED" for f in findings)


def test_status_refresh_with_dashboard_snapshot_counts_as_expected_lag(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "tools").mkdir()
    (repo / "tools" / "dashboard").mkdir()
    (repo / "tools" / "dashboard" / "roadmap.html").write_text("snapshot\n", encoding="utf-8")
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")

    assert cg._lag_expected(repo)


def test_dashboard_snapshot_normalization_ignores_only_live_head() -> None:
    base = (
        b'<meta name="dashboard-live-head" content="abc123"/>'
        b'const DATA = {"live_head": "abc123", "actions": [1]};'
    )
    same_except_head = (
        b'<meta name="dashboard-live-head" content="def456"/>'
        b'const DATA = {"live_head": "def456", "actions": [1]};'
    )
    changed_payload = (
        b'<meta name="dashboard-live-head" content="def456"/>'
        b'const DATA = {"live_head": "def456", "actions": [2]};'
    )

    assert cg._normalize_dashboard_snapshot(base) == (
        cg._normalize_dashboard_snapshot(same_except_head)
    )
    assert cg._normalize_dashboard_snapshot(base) != (
        cg._normalize_dashboard_snapshot(changed_payload)
    )


def test_status_refresh_with_unrelated_file_is_not_expected_lag(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "Project_Roadmap_v1.md").write_text("roadmap\n", encoding="utf-8")
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")

    assert not cg._lag_expected(repo)


def test_dashboard_drift_off_default_branch_is_advisory() -> None:
    state = _state(computed_hash="newhash")

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "ROADMAP_DASHBOARD_BRANCH_DIVERGED" for f in findings)
    assert not any(f.code == "ROADMAP_DASHBOARD_DRIFT" for f in findings)


def test_roadmap_change_requires_human_dashboard_snapshot() -> None:
    state = _state(
        status_entries=[" M Project_Roadmap_v1.md"],
        changed_files=["Project_Roadmap_v1.md"],
        dashboard_snapshot_current=False,
    )

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "DASHBOARD_SNAPSHOT_STALE" and f.severity == "hard" for f in findings)


def test_cite_bearing_changes_require_overlay_check_evidence() -> None:
    state = _state(
        status_entries=[" M harness-is/src/harness_is/entry_hash.py"],
        changed_files=["harness-is/src/harness_is/entry_hash.py"],
    )

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "OVERLAY_CHECK_REQUIRED" for f in findings)


def test_missing_required_checkpoint_is_hard_failure(tmp_path: Path) -> None:
    state = _state(root=tmp_path)

    findings = cg.validate(state, mode="check", require_fresh_checkpoint=True)

    assert any(f.code == "CONTEXT_CHECKPOINT_MISSING" and f.severity == "hard" for f in findings)


def test_fresh_checkpoint_satisfies_required_checkpoint(tmp_path: Path) -> None:
    state = _state(root=tmp_path, changed_files=["AGENTS.md"], status_entries=[" M AGENTS.md"])
    cg.write_checkpoint(state, label="test", findings=[])

    findings = cg.validate(state, mode="check", require_fresh_checkpoint=True)

    assert not any(f.code.startswith("CONTEXT_CHECKPOINT_") for f in findings)


def test_stale_checkpoint_is_hard_failure(tmp_path: Path) -> None:
    old_state = _state(root=tmp_path, changed_files=["AGENTS.md"], status_entries=[" M AGENTS.md"])
    new_state = _state(root=tmp_path, changed_files=["justfile"], status_entries=[" M justfile"])
    cg.write_checkpoint(old_state, label="test", findings=[])

    findings = cg.validate(new_state, mode="check", require_fresh_checkpoint=True)

    assert any(f.code == "CONTEXT_CHECKPOINT_STALE" and f.severity == "hard" for f in findings)


def test_credential_gate_log_redacts_secret_like_values(tmp_path: Path) -> None:
    state = _state(root=tmp_path, head8="deadbeef")

    path = cg.append_credential_gate(
        state,
        unit="R-1840",
        gate="OPENAI_API_KEY required for mixed-provider exercise",
        forward_closed="mock/provider-free tests passed; only live provider call remains",
        resume="ask operator for OPENAI_API_KEY authorization, then run live e2e",
        command="OPENAI_API_KEY=sk-secret uv run pytest live_test.py",
    )

    assert path == tmp_path / ".harness" / "codex_credential_gates.jsonl"
    raw = path.read_text(encoding="utf-8")
    assert "sk-secret" not in raw
    assert "OPENAI_API_KEY=<redacted>" in raw
    assert '"unit": "R-1840"' in raw


def test_credential_gate_log_requires_forward_closed_evidence(tmp_path: Path) -> None:
    state = _state(root=tmp_path)

    try:
        cg.append_credential_gate(
            state,
            unit="R-1840",
            gate="OPENAI_API_KEY required",
            forward_closed="",
            resume="ask operator for OPENAI_API_KEY authorization",
            command="uv run pytest live_test.py",
        )
    except ValueError as exc:
        assert "forward_closed" in str(exc)
    else:
        raise AssertionError("append_credential_gate should require forward_closed evidence")


def test_credential_gate_ledger_change_requires_tracking_surface() -> None:
    state = _state(
        status_entries=[" M .harness/codex_credential_gates.jsonl"],
        changed_files=[".harness/codex_credential_gates.jsonl"],
    )

    findings = cg.validate(state, mode="closeout")

    assert any(
        f.code == "CREDENTIAL_GATE_TRACKING_REQUIRED" and f.severity == "hard" for f in findings
    )


def test_unavailable_open_prs_are_explicit_warning() -> None:
    state = _state(open_prs="", open_prs_available=False)

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "OPEN_PRS_UNAVAILABLE" and f.severity == "warn" for f in findings)

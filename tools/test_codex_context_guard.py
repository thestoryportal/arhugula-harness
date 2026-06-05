"""Tests for Codex deterministic context guard.

The guard is the Codex-side anti-rot instrument: it turns context freshness,
worktree isolation, cite/drift hygiene, and closeout tracking into objective
checks instead of remembered process.
"""

from __future__ import annotations

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
        fork_doc_count=0,
        latest_retirement_batch=".harness/phase-7d-retirement-events-batch-51.md",
        lag_expected=False,
        dashboard_snapshot_current=True,
    )
    return cg.GuardState(**{**base.__dict__, **overrides})


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


def test_dashboard_drift_can_be_downgraded_for_ci_runtime_smoke() -> None:
    state = _state(
        branch="main",
        git_dir=".git",
        is_linked_worktree=False,
        computed_hash="newhash",
        dashboard=cg.DashboardState(hash="oldhash", git_head="abc12345", last_refreshed="old"),
    )

    findings = cg.validate(state, mode="preflight", allow_dashboard_drift=True)

    assert any(f.code == "ROADMAP_DASHBOARD_DRIFT_ALLOWED" for f in findings)
    assert not any(f.code == "ROADMAP_DASHBOARD_DRIFT" for f in findings)


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

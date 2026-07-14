"""Tests for Codex deterministic context guard.

The guard is the Codex-side anti-rot instrument: it turns context freshness,
worktree isolation, cite/drift hygiene, and closeout tracking into objective
checks instead of remembered process.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_context_guard as cg
import codex_loop as cl


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
        roadmap_status=cg.RoadmapStatusState(
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
        owed_lag=False,
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


def _write_roadmap_status(repo: Path, *, git_head: str) -> None:
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `abcdefabcdef` |",
                f"| `git_head` | `{git_head}` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


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


def test_clearance_marker_exempts_bundled_absorption() -> None:
    # CLAUDE.md §11.4 + §4.5: a spec amendment co-landing with impl behind a
    # clearance marker is a RATIFIED bundled-absorption arc (the R-FS-1 B-* pattern),
    # not silent absorption — mirror the X-AL-3 (§4.4) back-flow recognition.
    state = _state(
        changed_files=[
            "design-substrate/Spec_Harness_Runtime_v1.md",
            "harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py",
            "harness-runtime/tests/test_lifecycle_llm_dispatch.py",
            ".harness/clearance/Spec_Harness_Runtime-v1_65-cleared-2026-06-20.md",
        ],
    )

    findings = cg.validate(state, mode="closeout")

    assert not any(f.code == "DESIGN_IMPL_MIX" for f in findings)


def test_design_impl_with_fork_doc_but_no_clearance_marker_still_hard() -> None:
    # Narrowness guard: a fork doc alone is NOT the bundled-absorption signal — only
    # a clearance marker (§4.5) is. Design + impl without a clearance marker still
    # hard-fails (a silent mix is not legitimized by an unratified fork doc).
    state = _state(
        changed_files=[
            "design-substrate/Spec_Harness_Runtime_v1.md",
            "harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py",
            ".harness/class_2_fork_b_l2_fallback_composition.md",
        ],
    )

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "DESIGN_IMPL_MIX" and f.severity == "hard" for f in findings)


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


def test_roadmap_status_drift_on_default_branch_is_hard_failure() -> None:
    state = _state(
        branch="main",
        git_dir=".git",
        is_linked_worktree=False,
        computed_hash="newhash",
        roadmap_status=cg.RoadmapStatusState(
            hash="oldhash", git_head="abc12345", last_refreshed="old"
        ),
    )

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "ROADMAP_STATUS_DRIFT" and f.severity == "hard" for f in findings)


def test_roadmap_drift_allowance_does_not_downgrade_default_branch() -> None:
    state = _state(
        branch="main",
        git_dir=".git",
        is_linked_worktree=False,
        computed_hash="newhash",
        roadmap_status=cg.RoadmapStatusState(
            hash="oldhash", git_head="abc12345", last_refreshed="old"
        ),
    )

    findings = cg.validate(state, mode="preflight", allow_roadmap_drift=True)

    assert any(f.code == "ROADMAP_STATUS_DRIFT" and f.severity == "hard" for f in findings)
    assert not any(f.code == "ROADMAP_STATUS_DRIFT_ALLOWED" for f in findings)


def test_lag_expected_roadmap_drift_has_specific_warning_code() -> None:
    state = _state(branch="main", computed_hash="newhash", lag_expected=True)

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "ROADMAP_STATUS_LAG_EXPECTED" and f.severity == "warn" for f in findings)
    assert not any(f.code == "ROADMAP_STATUS_BRANCH_DIVERGED" for f in findings)


def test_owed_lag_without_allow_roadmap_drift_still_hard_fails_on_default_branch() -> None:
    # The Codex round-4 finding this guards: a HEAD that is one commit past a
    # verified refresh (owed_lag=True) must NOT be silently downgraded to a
    # warning for callers that don't pass --allow-roadmap-drift — i.e. the
    # session-start hook and `just codex-preflight`, which must force the
    # owed refresh before further work proceeds, even though CI on the exact
    # same commit (with the flag) passes clean.
    state = _state(branch="main", computed_hash="newhash", lag_expected=False, owed_lag=True)

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "ROADMAP_STATUS_DRIFT" and f.severity == "hard" for f in findings)
    assert not any(f.code == "ROADMAP_STATUS_LAG_EXPECTED" for f in findings)


def test_owed_lag_with_allow_roadmap_drift_downgrades_to_warn_on_default_branch() -> None:
    # The CI-side fix this round-4 finding demands: the post-merge `push`
    # trigger passes --allow-roadmap-drift unconditionally, and on that exact
    # invocation an owed_lag=True HEAD must warn, not hard-fail — this is the
    # scenario the whole arc originally set out to fix (CI red on the first
    # run after every content merge to main).
    state = _state(branch="main", computed_hash="newhash", lag_expected=False, owed_lag=True)

    findings = cg.validate(state, mode="check", allow_roadmap_drift=True)

    assert any(f.code == "ROADMAP_STATUS_LAG_EXPECTED" and f.severity == "warn" for f in findings)
    assert not any(f.code == "ROADMAP_STATUS_DRIFT" for f in findings)


def test_status_refresh_alone_counts_as_expected_lag(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    parent_sha = _git(repo, "rev-parse", "--short=8", "HEAD")
    _write_roadmap_status(repo, git_head=parent_sha)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")

    assert cg._lag_expected(repo)


def test_merged_status_refresh_alone_counts_as_expected_lag(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "-m", "main")
    parent_sha = _git(repo, "rev-parse", "--short=8", "HEAD")
    _git(repo, "checkout", "-b", "refresh")
    _write_roadmap_status(repo, git_head=parent_sha)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "refresh", "-m", "Merge pull request #123 from test/refresh")

    assert cg._lag_expected(repo)


def test_merged_status_refresh_with_unrelated_payload_is_not_expected_lag(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "-m", "main")
    _git(repo, "checkout", "-b", "refresh")
    (repo / "unrelated.txt").write_text("payload\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "add unrelated payload")
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "refresh", "-m", "Merge pull request #123 from test/refresh")

    assert not cg._lag_expected(repo)


def test_status_refresh_with_unrelated_file_is_not_expected_lag(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "Project_Roadmap_v1.md").write_text("roadmap\n", encoding="utf-8")
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")

    assert not cg._lag_expected(repo)


def test_content_merge_right_after_refresh_counts_as_owed_lag(tmp_path: Path) -> None:
    # The real repeating topology: content commit -> terminating refresh commit
    # (touches roadmap_status.md, describing the content commit as its own parent)
    # -> the NEXT content commit, which does NOT touch roadmap_status.md at all and
    # so still carries the refresh's recorded value. This is the "owed lag" case
    # (distinct from `_lag_expected`'s HEAD-is-refresh case) — a commit can never
    # record its own not-yet-computed SHA, and neither can the commit after it if
    # that commit doesn't touch the file.
    repo = _init_repo(tmp_path)
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: first content merge")
    content_sha = _git(repo, "rev-parse", "HEAD")
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `abcdefabcdef` |",
                f"| `git_head` | `{content_sha[:8]}` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    (repo / "feature2.py").write_text("# second content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: next content merge, does not touch roadmap_status.md")

    assert cg._owed_lag(repo)


def test_content_merge_two_commits_past_refresh_is_not_owed_lag(tmp_path: Path) -> None:
    # Two content commits stacked after the refresh without touching
    # roadmap_status.md again: genuinely unreconciled drift (two commits, not one),
    # must still hard-fail rather than be silently tolerated.
    repo = _init_repo(tmp_path)
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: first content merge")
    content_sha = _git(repo, "rev-parse", "HEAD")
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `abcdefabcdef` |",
                f"| `git_head` | `{content_sha[:8]}` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    (repo / "feature2.py").write_text("# second content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: next content merge")
    (repo / "feature3.py").write_text("# third content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: second unrefreshed content merge")

    assert not cg._owed_lag(repo)


def test_stale_status_touch_before_content_commit_is_not_owed_lag(
    tmp_path: Path,
) -> None:
    # An accidental/malformed edit to roadmap_status.md that is NOT a verified
    # terminating refresh (wrong title, or touches other files too) must never be
    # mistaken for a real refresh just because it's positionally the last touch —
    # position alone is not sufficient; the last-touch commit must independently
    # prove it was a genuine refresh (title + exact file set).
    repo = _init_repo(tmp_path)
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `deadbeefdead` |",
                "| `git_head` | `deadbeef` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "docs: accidental stale status edit")
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: content merge")

    assert not cg._owed_lag(repo)


def test_malformed_status_edit_right_after_refresh_is_not_owed_lag(
    tmp_path: Path,
) -> None:
    # The parent-based allowance exists for a HEAD that does NOT touch the status
    # file at all. If HEAD itself edits roadmap_status.md — wrong title, or
    # bundled with unrelated content — it must qualify as a refresh entirely on
    # its own merits, never by riding its parent's lag allowance. Otherwise a
    # malformed/bundled edit landing right after a real refresh would silently
    # downgrade genuine hard drift to a warning.
    repo = _init_repo(tmp_path)
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: first content merge")
    content_sha = _git(repo, "rev-parse", "HEAD")
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `abcdefabcdef` |",
                f"| `git_head` | `{content_sha[:8]}` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    (repo / ".harness" / "roadmap_status.md").write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|---|---|",
                "| `workspace_state_hash` | `deadbeefdead` |",
                "| `git_head` | `deadbeef` |",
                "| `last_refreshed` | 2026-06-05T00:00:00-06:00 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "feature2.py").write_text("# bundled content\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "docs: bundled bad status edit")

    assert not cg._owed_lag(repo)


def test_content_merge_after_merge_based_refresh_counts_as_owed_lag(
    tmp_path: Path,
) -> None:
    # A terminating refresh landed via `git merge --no-ff` (2-parent merge commit)
    # rather than a squash — git's default path-limited history simplification
    # hides that merge commit in favor of the refresh branch's own commit, so a
    # naive "last commit touching the path" lookup would resolve to the WRONG
    # commit relative to the next content commit's actual parent (the merge
    # commit itself). Checking HEAD's parent directly for verified-refresh shape
    # (recursing through the merge) must still recognize this topology.
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "-m", "main")
    parent_sha = _git(repo, "rev-parse", "--short=8", "HEAD")
    _git(repo, "checkout", "-b", "refresh")
    _write_roadmap_status(repo, git_head=parent_sha)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "refresh", "-m", "Merge pull request #123 from test/refresh")
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: next content merge")

    assert cg._owed_lag(repo)


def test_refresh_with_stale_git_head_is_not_verified(tmp_path: Path) -> None:
    # A commit with the right title and the right lone-file shape, but whose
    # roadmap_status.md content records a `git_head` that does NOT match its
    # own parent's SHA (stale/malformed/wrong content) must not pass as a
    # verified refresh — shape alone (title + file set) is not sufficient;
    # the recorded content must actually describe this commit's own parent.
    repo = _init_repo(tmp_path)
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: first content merge")
    _write_roadmap_status(repo, git_head="deadbeef")  # wrong: not this commit's parent SHA
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")

    assert not cg._lag_expected(repo)


def test_content_merge_after_stale_git_head_refresh_is_not_owed_lag(tmp_path: Path) -> None:
    # The owed-lag path must inherit the same content-validation protection:
    # a content commit right after a shape-only "refresh" (wrong git_head)
    # must not be tolerated as owed lag either.
    repo = _init_repo(tmp_path)
    (repo / "feature.py").write_text("# content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: first content merge")
    _write_roadmap_status(repo, git_head="deadbeef")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    (repo / "feature2.py").write_text("# second content change\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: next content merge")

    assert not cg._owed_lag(repo)


def test_stale_refresh_branch_merged_after_main_advanced_is_not_verified(
    tmp_path: Path,
) -> None:
    # The exact topology the merge-wrapped content check must catch: a refresh
    # branch is created at commit A, `main` advances on its own to commit B
    # (an unrelated content commit lands directly on main), and only THEN is
    # the now-stale refresh branch merged in with `--no-ff`. The merge's file
    # set still looks like a clean single-file refresh, and the refresh
    # branch tip is itself perfectly self-consistent (it correctly recorded
    # A as its own parent) — but the merged content still records A, while
    # the merge's real predecessor state is B, not A. This must NOT verify.
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "-m", "main")
    a_sha = _git(repo, "rev-parse", "--short=8", "HEAD")
    _git(repo, "checkout", "-b", "refresh")
    _write_roadmap_status(repo, git_head=a_sha)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ops: roadmap status refresh post-test")
    _git(repo, "checkout", "main")
    (repo / "feature.py").write_text("# content change while refresh pending\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: content merge while refresh branch pending")
    _git(repo, "merge", "--no-ff", "refresh", "-m", "Merge pull request #123 from test/refresh")

    assert not cg._lag_expected(repo)


def test_roadmap_drift_off_default_branch_is_advisory() -> None:
    state = _state(computed_hash="newhash")

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "ROADMAP_STATUS_BRANCH_DIVERGED" for f in findings)
    assert not any(f.code == "ROADMAP_STATUS_DRIFT" for f in findings)


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


def test_credential_gate_log_redacts_bearer_token_without_name_prefix(tmp_path: Path) -> None:
    """Regression — a Bearer-token-shaped secret (no `NAME=` prefix) must be
    redacted too. Previously only NAME=VALUE-shaped values matched, so a
    Bearer token passed via `--command` landed verbatim in the
    non-gitignored, actively-committed credential-gate ledger."""
    state = _state(root=tmp_path, head8="deadbeef")

    path = cg.append_credential_gate(
        state,
        unit="R-1840",
        gate="live API call requires a bearer credential",
        forward_closed="mock tests passed; only live provider call remains",
        resume="ask operator for a fresh bearer token, then run live e2e",
        command="curl -H 'Authorization: Bearer sk-live-abcdef1234567890' https://api.example.com",
    )

    raw = path.read_text(encoding="utf-8")
    assert "sk-live-abcdef1234567890" not in raw
    assert "<redacted>" in raw


def test_credential_gate_log_redacts_bare_vendor_prefixed_key(tmp_path: Path) -> None:
    """Regression — a bare vendor-prefixed API key (no `NAME=` prefix, no
    `Bearer` keyword) must also be redacted."""
    state = _state(root=tmp_path, head8="deadbeef")

    path = cg.append_credential_gate(
        state,
        unit="R-1840",
        gate="live GitHub API call requires a PAT",
        forward_closed="mock tests passed; only live GitHub call remains",
        resume="ask operator for a fresh PAT, then run live e2e",
        command="gh api /user --header 'ghp_1234567890abcdef1234567890abcdef1234'",
    )

    raw = path.read_text(encoding="utf-8")
    assert "ghp_1234567890abcdef1234567890abcdef1234" not in raw
    assert "<redacted>" in raw


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


def test_incomplete_codex_loop_state_blocks_closeout(tmp_path: Path) -> None:
    loop_dir = tmp_path / ".harness"
    loop_dir.mkdir()
    (loop_dir / "codex_loop_state.json").write_text(
        """{
  "arc_id": "B-LOOP",
  "events": [
    {
      "phase": "preflight",
      "status": "passed",
      "command": "just codex-preflight",
      "evidence": "checkpoint written"
    }
  ]
}
""",
        encoding="utf-8",
    )
    state = _state(root=tmp_path)

    findings = cg.validate(state, mode="closeout")

    assert any(f.code == "CODEX_LOOP_INCOMPLETE" and f.severity == "hard" for f in findings)


def test_complete_codex_loop_state_satisfies_closeout(tmp_path: Path) -> None:
    loop_dir = tmp_path / ".harness"
    loop_dir.mkdir()
    fingerprint = cg.worktree_fingerprint(tmp_path)
    events = [
        {
            "phase": phase,
            "status": "failed" if phase == "red" else "passed",
            "branch": "feature",
            "head8": "abc12345",
            "worktree_fingerprint": fingerprint,
            "linked_worktree": True,
        }
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
        )
    ]
    (loop_dir / "codex_loop_state.json").write_text(
        json.dumps(
            {
                "arc_id": "B-LOOP",
                "branch": "feature",
                "head8": "abc12345",
                "worktree_fingerprint": fingerprint,
                "events": events,
            }
        ),
        encoding="utf-8",
    )
    state = _state(root=tmp_path)

    findings = cg.validate(state, mode="closeout")

    assert not any(f.code == "CODEX_LOOP_INCOMPLETE" for f in findings)


def test_complete_shipped_codex_loop_state_satisfies_main_closeout(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    identity = cl.git_identity(repo)
    loop_dir = repo / ".harness"
    feature_branch = "codex/loop-closeout-guard-fix"
    feature_head = "feedface"
    feature_worktree = "feature-worktree"
    reviewed_content = "reviewed-content"
    events: list[dict[str, object]] = []
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
        events.append(
            {
                "phase": phase,
                "status": "failed" if phase == "red" else "passed",
                "branch": feature_branch,
                "head8": feature_head,
                "worktree_fingerprint": feature_worktree,
                "content_fingerprint": reviewed_content,
                "linked_worktree": True,
            }
        )
    events.append(
        {
            "phase": "commit",
            "status": "passed",
            "branch": feature_branch,
            "head8": "c0ffee00",
            "worktree_fingerprint": feature_worktree,
            "content_fingerprint": reviewed_content,
            "linked_worktree": True,
            "validated_phase": "closeout",
            "validated_head8": feature_head,
            "validated_worktree_fingerprint": feature_worktree,
            "validated_content_fingerprint": reviewed_content,
        }
    )
    for phase in ("push", "pr_opened", "ci_green", "merged"):
        events.append(
            {
                "phase": phase,
                "status": "passed",
                "branch": feature_branch,
                "head8": "c0ffee00",
                "worktree_fingerprint": feature_worktree,
                "content_fingerprint": reviewed_content,
                "linked_worktree": True,
            }
        )
    for phase in ("post_merge_refresh", "main_synced", "worktree_disposition"):
        events.append(
            {
                "phase": phase,
                "status": "passed",
                "branch": identity.branch,
                "head8": identity.head8,
                "worktree_fingerprint": identity.worktree_fingerprint,
                "content_fingerprint": identity.content_fingerprint,
                "linked_worktree": identity.linked_worktree,
            }
        )
    (loop_dir / "codex_loop_state.json").write_text(
        json.dumps(
            {
                "arc_id": "B-LOOP",
                "root": str(tmp_path / "removed-feature-worktree"),
                "branch": identity.branch,
                "head8": identity.head8,
                "worktree_fingerprint": identity.worktree_fingerprint,
                "content_fingerprint": identity.content_fingerprint,
                "required_gates": list(cl.REQUIRED_GATES),
                "events": events,
            }
        ),
        encoding="utf-8",
    )
    state = cg.derive(repo)

    findings = cg.validate(state, mode="closeout")

    assert not any(f.code == "CODEX_LOOP_INCOMPLETE" for f in findings)


def test_stale_complete_shipped_codex_loop_state_is_archived_evidence(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    shipped_identity = cl.git_identity(repo)
    loop_dir = repo / ".harness"
    feature_branch = "codex/loop-closeout-guard-fix"
    feature_head = "feedface"
    feature_worktree = "feature-worktree"
    reviewed_content = "reviewed-content"
    events: list[dict[str, object]] = []
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
        events.append(
            {
                "phase": phase,
                "status": "failed" if phase == "red" else "passed",
                "branch": feature_branch,
                "head8": feature_head,
                "worktree_fingerprint": feature_worktree,
                "content_fingerprint": reviewed_content,
                "linked_worktree": True,
            }
        )
    events.append(
        {
            "phase": "commit",
            "status": "passed",
            "branch": feature_branch,
            "head8": "c0ffee00",
            "worktree_fingerprint": feature_worktree,
            "content_fingerprint": reviewed_content,
            "linked_worktree": True,
            "validated_phase": "closeout",
            "validated_head8": feature_head,
            "validated_worktree_fingerprint": feature_worktree,
            "validated_content_fingerprint": reviewed_content,
        }
    )
    for phase in ("push", "pr_opened", "ci_green", "merged"):
        events.append(
            {
                "phase": phase,
                "status": "passed",
                "branch": feature_branch,
                "head8": "c0ffee00",
                "worktree_fingerprint": feature_worktree,
                "content_fingerprint": reviewed_content,
                "linked_worktree": True,
            }
        )
    for phase in ("post_merge_refresh", "main_synced", "worktree_disposition"):
        events.append(
            {
                "phase": phase,
                "status": "passed",
                "branch": shipped_identity.branch,
                "head8": shipped_identity.head8,
                "worktree_fingerprint": shipped_identity.worktree_fingerprint,
                "content_fingerprint": shipped_identity.content_fingerprint,
                "linked_worktree": shipped_identity.linked_worktree,
            }
        )
    (loop_dir / "codex_loop_state.json").write_text(
        json.dumps(
            {
                "arc_id": "B-LOOP",
                "root": str(tmp_path / "removed-feature-worktree"),
                "branch": shipped_identity.branch,
                "head8": shipped_identity.head8,
                "worktree_fingerprint": shipped_identity.worktree_fingerprint,
                "content_fingerprint": shipped_identity.content_fingerprint,
                "required_gates": list(cl.REQUIRED_GATES),
                "events": events,
            }
        ),
        encoding="utf-8",
    )
    (repo / "later.txt").write_text("main advanced after shipped loop\n", encoding="utf-8")
    _git(repo, "add", "later.txt")
    _git(repo, "commit", "-m", "advance main")
    state = cg.derive(repo)

    findings = cg.validate(state, mode="closeout")

    assert not any(f.code == "CODEX_LOOP_INCOMPLETE" for f in findings)


def test_out_of_order_codex_loop_state_blocks_closeout(tmp_path: Path) -> None:
    loop_dir = tmp_path / ".harness"
    loop_dir.mkdir()
    fingerprint = cg.worktree_fingerprint(tmp_path)
    events = [
        {
            "phase": phase,
            "status": "failed" if phase == "red" else "passed",
            "branch": "feature",
            "head8": "abc12345",
            "worktree_fingerprint": fingerprint,
            "linked_worktree": True,
        }
        for phase in (
            "worktree_ready",
            "preflight",
            "plan",
            "implementation",
            "narrow_verify",
            "local_gate",
            "decorrelated_review",
            "red",
        )
    ]
    (loop_dir / "codex_loop_state.json").write_text(
        json.dumps(
            {
                "arc_id": "B-LOOP",
                "branch": "feature",
                "head8": "abc12345",
                "worktree_fingerprint": fingerprint,
                "events": events,
            }
        ),
        encoding="utf-8",
    )
    state = _state(root=tmp_path)

    findings = cg.validate(state, mode="closeout")

    assert any(
        f.code == "CODEX_LOOP_INCOMPLETE"
        and "gate order invalid: red recorded after implementation" in f.message
        for f in findings
    )


def test_stale_codex_loop_state_blocks_closeout(tmp_path: Path) -> None:
    loop_dir = tmp_path / ".harness"
    loop_dir.mkdir()
    fingerprint = cg.worktree_fingerprint(tmp_path)
    events = [
        {
            "phase": phase,
            "status": "failed" if phase == "red" else "passed",
            "branch": "feature",
            "head8": "abc12345",
            "worktree_fingerprint": fingerprint,
            "linked_worktree": True,
        }
        for phase in (
            "worktree_ready",
            "preflight",
            "plan",
            "red",
            "implementation",
            "narrow_verify",
            "local_gate",
            "decorrelated_review",
        )
    ]
    events[-1]["head8"] = "deadbeef"
    (loop_dir / "codex_loop_state.json").write_text(
        json.dumps(
            {
                "arc_id": "B-LOOP",
                "branch": "stale-branch",
                "head8": "abc12345",
                "worktree_fingerprint": fingerprint,
                "events": events,
            }
        ),
        encoding="utf-8",
    )
    state = _state(root=tmp_path)

    findings = cg.validate(state, mode="closeout")

    assert any(
        f.code == "CODEX_LOOP_INCOMPLETE"
        and "loop state recorded for branch=stale-branch" in f.message
        and "decorrelated_review gate recorded for" in f.message
        for f in findings
    )


def test_stale_codex_loop_worktree_fingerprint_blocks_closeout(tmp_path: Path) -> None:
    loop_dir = tmp_path / ".harness"
    loop_dir.mkdir()
    fingerprint = cg.worktree_fingerprint(tmp_path)
    events = [
        {
            "phase": phase,
            "status": "failed" if phase == "red" else "passed",
            "branch": "feature",
            "head8": "abc12345",
            "worktree_fingerprint": fingerprint,
            "linked_worktree": True,
        }
        for phase in (
            "worktree_ready",
            "preflight",
            "plan",
            "red",
            "implementation",
            "narrow_verify",
            "local_gate",
            "decorrelated_review",
        )
    ]
    events[-1]["worktree_fingerprint"] = "stale-worktree"
    (loop_dir / "codex_loop_state.json").write_text(
        json.dumps(
            {
                "arc_id": "B-LOOP",
                "branch": "feature",
                "head8": "abc12345",
                "worktree_fingerprint": "stale-worktree",
                "events": events,
            }
        ),
        encoding="utf-8",
    )
    state = _state(root=tmp_path)

    findings = cg.validate(state, mode="closeout")

    assert any(
        f.code == "CODEX_LOOP_INCOMPLETE"
        and "loop state recorded for worktree=stale-worktree" in f.message
        and "decorrelated_review gate recorded for worktree=stale-worktree" in f.message
        for f in findings
    )


def test_unavailable_open_prs_are_explicit_warning() -> None:
    state = _state(open_prs="", open_prs_available=False)

    findings = cg.validate(state, mode="preflight")

    assert any(f.code == "OPEN_PRS_UNAVAILABLE" and f.severity == "warn" for f in findings)

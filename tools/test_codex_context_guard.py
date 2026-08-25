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


# --- U-HE-33: emitting detections (C-HE-12) ---------------------------------

from datetime import UTC  # noqa: E402  -- section-local import, same posture as fr below

import finding_record as fr  # noqa: E402  -- shares the tools/ sys.path insert above


def _isolate_gate_log(monkeypatch, tmp_path: Path) -> Path:
    """Redirect the C-HE-24 record so detection tests never write the tracked log."""
    log = tmp_path / "merge-gate-log.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    return log


def _adjudicate(row: dict, disposition: str) -> None:
    fr.append_row(
        {
            **row,
            "record_kind": "finding_adjudication",
            "ts": "2099-01-01T00:00:00Z",
            "disposition": disposition,
            "disposition_actor": "operator",
        }
    )


OPEN_HEAD = {"arc_id": "pr-9", "state": "open", "pr": 9}


def test_split_brain_ledger_duplicate_arc_id(tmp_path, monkeypatch) -> None:
    log = _isolate_gate_log(monkeypatch, tmp_path)
    ledger = tmp_path / "arc-metrics.jsonl"
    ledger.write_text(
        '{"arc_id":"pr-1","record_kind":"arc"}\n{"arc_id":"pr-1","record_kind":"arc"}\n'
    )

    fs = cg.check_split_brain(ledger, lane_id="lane-x")

    assert [f.code for f in fs] == ["SPLIT_BRAIN_LEDGER"]
    assert fs[0].severity == "hard"
    assert "lane-x" in fs[0].message
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    assert [r["producer"] for r in rows] == ["SPLIT_BRAIN_LEDGER"]
    assert rows[0]["lane_id"] == "lane-x"
    assert rows[0]["arc_id"] == "pr-1"
    assert rows[0]["record_kind"] == "finding"


def test_split_brain_ignores_non_arc_rows_and_clean(tmp_path, monkeypatch) -> None:
    _isolate_gate_log(monkeypatch, tmp_path)
    ledger = tmp_path / "arc-metrics.jsonl"
    ledger.write_text(
        '{"arc_id":"pr-1","record_kind":"arc"}\n{"arc_id":"pr-1","record_kind":"round"}\n'
    )

    assert cg.check_split_brain(ledger, lane_id="l") == []
    assert cg.check_split_brain(tmp_path / "absent.jsonl", lane_id="l") == []


def test_base_toctou(tmp_path, monkeypatch) -> None:
    log = _isolate_gate_log(monkeypatch, tmp_path)

    fs = cg.check_base_toctou([("m" * 40, "b" * 40, "c" * 40)], lane_id="l")

    assert [f.code for f in fs] == ["BASE_TOCTOU"]
    assert fs[0].severity == "hard"
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    assert [r["producer"] for r in rows] == ["BASE_TOCTOU"]
    assert cg.check_base_toctou([("m" * 40, "b" * 40, "b" * 40)], lane_id="l") == []


def test_orphaned_reservation(tmp_path, monkeypatch) -> None:
    _isolate_gate_log(monkeypatch, tmp_path)
    monkeypatch.setattr(cg, "_reservation_head_current", lambda arc_id: dict(OPEN_HEAD))
    monkeypatch.setattr(cg, "_gh_pr_state", lambda pr: "MERGED")
    monkeypatch.setattr(cg, "_blocked_lease_older_than_bound", lambda: None)

    fs = cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l")

    assert [f.code for f in fs] == ["ORPHANED_RESERVATION"]
    assert fs[0].severity == "warn"


def test_orphaned_reservation_blocked_lease_past_bound(tmp_path, monkeypatch) -> None:
    _isolate_gate_log(monkeypatch, tmp_path)
    monkeypatch.setattr(
        cg,
        "_blocked_lease_older_than_bound",
        lambda: {
            "pr": 5,
            "reservation_id": "u-x",
            "state": "blocked",
            "lease_token": "aabbccddeeff0011",
            "blocked_at_sha": "d" * 40,
        },
    )

    fs = cg.check_orphaned_reservations([], lane_id="l")

    assert [f.code for f in fs] == ["ORPHANED_RESERVATION"]
    # token + sha discriminate distinct block events: a successor lease blocked again
    # must not recall a prior event's suppression through identical evidence
    assert "aabbccdd" in fs[0].message and "d" * 12 in fs[0].message


def test_json_report_carries_lane_id(monkeypatch) -> None:
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-7")

    report = json.loads(cg._json_report(_state(), []))

    assert report["lane_id"] == "lane-7"


def test_check_mode_on_default_branch_runs_detections(monkeypatch) -> None:
    """The wiring witness: `check` on the default branch invokes all three detections;
    any other branch/mode combination invokes none."""
    calls: list[str] = []
    monkeypatch.setattr(
        cg,
        "check_split_brain",
        lambda ledger, *, lane_id: calls.append("split") or [],
    )
    monkeypatch.setattr(
        cg,
        "check_base_toctou",
        lambda merges, *, lane_id: calls.append("toctou") or [],
    )
    monkeypatch.setattr(
        cg,
        "check_orphaned_reservations",
        lambda heads, *, lane_id: calls.append("orphan") or [],
    )
    monkeypatch.setattr(cg, "_reservation_heads", lambda: ([], []))
    monkeypatch.setattr(cg, "_recent_main_merges", lambda root, heads: ([], []))

    cg.validate(_state(branch="main"), mode="check")
    assert calls == ["split", "toctou", "orphan"]

    calls.clear()
    cg.validate(_state(branch="feature"), mode="check")
    cg.validate(_state(branch="main"), mode="preflight")
    assert calls == []


def test_detection_emit_once_and_adjudication_recall(tmp_path, monkeypatch) -> None:
    """A repeated identical detection appends no duplicate row; a lineage whose LAST
    disposition is `suppressed`/`rejected` is recalled (returns None); an `accepted`
    disposition means CONFIRMED REAL and keeps the projection surfacing."""
    log = _isolate_gate_log(monkeypatch, tmp_path)
    mismatch = [("m" * 40, "b" * 40, "c" * 40)]

    first = cg.check_base_toctou(mismatch, lane_id="l")
    second = cg.check_base_toctou(mismatch, lane_id="l")

    assert [f.code for f in first] == [f.code for f in second] == ["BASE_TOCTOU"]
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(rows) == 1  # emit-once: the second identical observation did not re-append

    _adjudicate(rows[0], "accepted")
    assert [f.code for f in cg.check_base_toctou(mismatch, lane_id="l")] == ["BASE_TOCTOU"]

    # a still-present condition later suppressed by the operator IS recalled
    _isolate_gate_log(monkeypatch, tmp_path / "second")
    (tmp_path / "second").mkdir(exist_ok=True)
    fs = cg.check_base_toctou(mismatch, lane_id="l")
    assert [f.code for f in fs] == ["BASE_TOCTOU"]
    rows2 = [
        json.loads(line)
        for line in (tmp_path / "second" / "merge-gate-log.jsonl").read_text().splitlines()
    ]
    _adjudicate(rows2[0], "suppressed")
    assert cg.check_base_toctou(mismatch, lane_id="l") == []


def test_detection_new_evidence_mints_new_ordinal(tmp_path, monkeypatch) -> None:
    """Ids come from append_observations' locked mint, never a hand-built ordinal --
    drifted evidence at one site lands as a NEW observation."""
    _isolate_gate_log(monkeypatch, tmp_path)
    monkeypatch.setattr(cg, "_reservation_head_current", lambda arc_id: dict(OPEN_HEAD))
    monkeypatch.setattr(cg, "_blocked_lease_older_than_bound", lambda: None)

    monkeypatch.setattr(cg, "_gh_pr_state", lambda pr: "MERGED")
    fs = cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l")
    assert [f.code for f in fs] == ["ORPHANED_RESERVATION"]
    monkeypatch.setattr(cg, "_gh_pr_state", lambda pr: "CLOSED")
    fs = cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l")
    assert [f.code for f in fs] == ["ORPHANED_RESERVATION"]

    rows = fr.read_rows()
    assert len(rows) == 2
    assert rows[0]["finding_id"] != rows[1]["finding_id"]
    assert {r["finding_id"].rsplit(":", 1)[1] for r in rows} == {"1", "2"}


def test_adjudication_does_not_suppress_new_evidence(tmp_path, monkeypatch) -> None:
    """C-HE-24 §5 adjudicates ONE finding_id -- a suppression at a site must not
    swallow a NEW observation with different evidence there."""
    _isolate_gate_log(monkeypatch, tmp_path)
    monkeypatch.setattr(cg, "_reservation_head_current", lambda arc_id: dict(OPEN_HEAD))
    monkeypatch.setattr(cg, "_blocked_lease_older_than_bound", lambda: None)

    monkeypatch.setattr(cg, "_gh_pr_state", lambda pr: "MERGED")
    assert len(cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l")) == 1
    _adjudicate(fr.read_rows()[0], "suppressed")

    assert cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l") == []  # recalled
    monkeypatch.setattr(cg, "_gh_pr_state", lambda pr: "CLOSED")
    assert len(cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l")) == 1


def test_adjudication_is_lane_scoped(tmp_path, monkeypatch) -> None:
    """Lane A's suppressed lineage does not stand in for lane B -- a new lane
    re-observing the same evidence appends its own lane-attributed row."""
    log = _isolate_gate_log(monkeypatch, tmp_path)
    mismatch = [("m" * 40, "b" * 40, "c" * 40)]

    assert [f.code for f in cg.check_base_toctou(mismatch, lane_id="lane-a")] == ["BASE_TOCTOU"]
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    _adjudicate(rows[0], "suppressed")

    assert cg.check_base_toctou(mismatch, lane_id="lane-a") == []  # lane A: recalled
    assert [f.code for f in cg.check_base_toctou(mismatch, lane_id="lane-b")] == ["BASE_TOCTOU"]
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    lane_b_rows = [r for r in rows if r.get("lane_id") == "lane-b"]
    assert len(lane_b_rows) == 1  # lane B's own attribution row landed


def test_orphan_emission_revalidates_current_generation(tmp_path, monkeypatch) -> None:
    """A normal open->merged transition landing between the snapshot and the GitHub
    answer must not be recorded as an orphan."""
    log = _isolate_gate_log(monkeypatch, tmp_path)
    monkeypatch.setattr(cg, "_gh_pr_state", lambda pr: "MERGED")
    monkeypatch.setattr(cg, "_blocked_lease_older_than_bound", lambda: None)
    monkeypatch.setattr(
        cg,
        "_reservation_head_current",
        lambda arc_id: {"arc_id": "pr-9", "state": "merged", "pr": 9},
    )

    assert cg.check_orphaned_reservations([dict(OPEN_HEAD)], lane_id="l") == []
    assert not log.exists()  # no durable row for the ordinary completion


def test_recent_main_merges_joins_real_git(tmp_path, monkeypatch) -> None:
    """The production join witnessed against a real git history -- a landing whose
    reservation records merge_sha/base_sha attributes with the commit's actual first
    parent; a landing with no reservation is reported unattributed."""
    repo = _init_repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "landed.txt").write_text("landed\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "landing")
    tip = _git(repo, "rev-parse", "HEAD")
    heads = [{"arc_id": "u-x", "state": "merged", "merge_sha": tip, "base_sha": base}]

    merges, unattributed = cg._recent_main_merges(repo, heads)

    assert merges == [(tip, base, base)]  # first parent read from git == verified base
    assert unattributed == [base]  # the baseline commit has no reservation
    assert cg.check_base_toctou(merges, lane_id="l") == []


def test_reservation_heads_partial_failure_is_surfaced(tmp_path, monkeypatch) -> None:
    """One unreadable head does not discard the valid heads, and the failure is
    returned for the suite to surface as a hard partial-failure finding."""
    import reservations as rs

    store = tmp_path / "reservations"
    (store / "good-arc").mkdir(parents=True)
    (store / "bad-arc").mkdir()
    good = {"arc_id": "good-arc", "state": "open", "pr": 7}
    monkeypatch.setattr(rs, "reservations_root", lambda: store)

    def fake_current(arc_id):
        if arc_id == "bad-arc":
            raise ValueError("corrupt head record")
        return (1, good)

    monkeypatch.setattr(rs, "current", fake_current)

    heads, unreadable = cg._reservation_heads()

    assert heads == [good]
    assert unreadable == ["bad-arc"]


def test_suite_surfaces_unreadable_heads_as_hard(monkeypatch, tmp_path) -> None:
    _isolate_gate_log(monkeypatch, tmp_path)
    (tmp_path / "arc-metrics.jsonl").write_text("")
    monkeypatch.setattr(cg, "_reservation_heads", lambda: ([], ["bad-arc"]))
    monkeypatch.setattr(cg, "_recent_main_merges", lambda root, heads: ([], []))
    monkeypatch.setattr(cg, "check_orphaned_reservations", lambda heads, *, lane_id: [])

    findings = cg._emitting_detections_safe(tmp_path, "l")

    hard = [f for f in findings if f.code == "DETECTIONS_UNAVAILABLE"]
    assert len(hard) == 1 and hard[0].severity == "hard"
    assert "bad-arc" in hard[0].message


def test_dispatch_runs_whole_suite_via_uv_when_layer_unimportable(monkeypatch) -> None:
    """reservations.py / merge_door.py themselves need the uv env (datetime.UTC is
    3.11+), so a stdlib venue must not silently no-op the store-reading detections --
    the WHOLE suite dispatches through `uv run` and the child's findings come back as
    this process's Findings."""
    monkeypatch.setattr(cg, "_record_layer_importable", lambda: False)
    calls: list[list[str]] = []

    def fake_run(args, *, cwd, timeout=20):
        calls.append(args)
        payload = json.dumps([{"severity": "hard", "code": "BASE_TOCTOU", "message": "[l] ev"}])
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=payload, stderr="")

    monkeypatch.setattr(cg, "_run", fake_run)

    findings = cg._emitting_detections_dispatch(Path("/repo"), "l")

    assert findings == [cg.Finding("hard", "BASE_TOCTOU", "[l] ev")]
    assert calls[0][:4] == ["uv", "run", "python", "-c"]
    assert calls[0][-2:] == ["/repo", "l"]


def test_dispatch_failure_is_unlooked_not_clean(monkeypatch) -> None:
    """When neither the in-process layer nor the uv fallback can run, the guard says so
    with a HARD Finding -- an empty detection set must never be indistinguishable from
    "could not look", and the blocking CI context must go red."""
    monkeypatch.setattr(cg, "_record_layer_importable", lambda: False)
    monkeypatch.setattr(
        cg,
        "_run",
        lambda args, *, cwd, timeout=20: subprocess.CompletedProcess(
            args=args, returncode=1, stdout="", stderr="uv: not found"
        ),
    )

    findings = cg._emitting_detections_dispatch(Path("/repo"), "l")

    assert [f.code for f in findings] == ["DETECTIONS_UNAVAILABLE"]
    assert findings[0].severity == "hard"  # blocking CI must go red on UNLOOKED
    assert "uv: not found" in findings[0].message


def test_in_process_suite_raise_is_hard_unavailable(monkeypatch) -> None:
    """A store-level refusal (symlinked store, unreadable history, failed gh) propagates
    out of the suite and becomes a HARD finding at the one dispatch enforcement point --
    never an empty (clean-looking) result."""

    def raise_store(root, lane, findings):
        raise RuntimeError("QUEUE_DIR/reservations is a symlink -- refused")

    monkeypatch.setattr(cg, "_record_layer_importable", lambda: True)
    monkeypatch.setattr(cg, "_emitting_detections", raise_store)

    findings = cg._emitting_detections_dispatch(Path("/repo"), "l")

    assert [f.code for f in findings] == ["DETECTIONS_UNAVAILABLE"]
    assert findings[0].severity == "hard"
    assert "symlink" in findings[0].message


def test_reservation_store_refusal_propagates(monkeypatch) -> None:
    """_reservation_heads does not convert a refused store into an empty one -- the
    containment failure must reach the dispatch boundary."""
    import reservations as rs

    def refuse():
        raise rs.ReservationError("QUEUE_DIR/reservations is a symlink -- refused")

    monkeypatch.setattr(rs, "reservations_root", refuse)

    try:
        cg._reservation_heads()
    except rs.ReservationError:
        pass
    else:
        raise AssertionError("a refused store must propagate, not read as empty")


def test_failed_git_log_raises_not_clean(tmp_path) -> None:
    """An unreadable history raises (dispatch -> hard finding) instead of returning an
    empty, clean-looking merge set."""
    not_a_repo = tmp_path / "empty"
    not_a_repo.mkdir()

    try:
        cg._recent_main_merges(not_a_repo, [])
    except RuntimeError as exc:
        assert "git log" in str(exc)
    else:
        raise AssertionError("a failed git log must raise, not report clean")


def test_gh_failure_raises_not_not_merged(monkeypatch) -> None:
    """A missing/unauthenticated gh raises (dispatch -> hard finding) -- it must not
    read as "PR not merged/closed" and let orphans evade detection."""

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="auth")

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        cg._gh_pr_state(9)
    except RuntimeError as exc:
        assert "gh pr view 9" in str(exc)
    else:
        raise AssertionError("a failed gh query must raise, not read as open")


def test_dirty_checkout_skips_suite_with_hard_finding(monkeypatch) -> None:
    """Isolation before emission (codex r6, widened r13): on ANY dirty default-branch
    checkout the suite does not run (a dirty linked worktree's uncommitted gate-log
    edit would otherwise be trusted as the suppression authority); a dirty ROOT
    checkout also reports ROOT_CHECKOUT_EDIT; a clean checkout runs the suite."""
    calls: list[str] = []
    monkeypatch.setattr(
        cg, "_emitting_detections_dispatch", lambda root, lane: calls.append("ran") or []
    )

    dirty_root = _state(
        branch="main",
        git_dir=".git",
        is_linked_worktree=False,
        status_entries=[" M .harness/merge-gate-log.jsonl"],
        changed_files=[".harness/merge-gate-log.jsonl"],
    )
    findings = cg.validate(dirty_root, mode="check")
    assert calls == []
    assert any(f.code == "DETECTIONS_UNAVAILABLE" and f.severity == "hard" for f in findings)
    assert any(f.code == "ROOT_CHECKOUT_EDIT" and f.severity == "hard" for f in findings)

    dirty_worktree = _state(branch="main", status_entries=[" M x.py"], changed_files=["x.py"])
    findings = cg.validate(dirty_worktree, mode="check")
    assert calls == []
    assert any(f.code == "DETECTIONS_UNAVAILABLE" and f.severity == "hard" for f in findings)

    clean_worktree = _state(branch="main")
    cg.validate(clean_worktree, mode="check")
    assert calls == ["ran"]


def test_ci_pins_split_brain_job() -> None:
    """The blocking split-brain CI job is pinned: deleting or de-blocking it reds this
    test, and its run block carries both the corrupt-ledger validation and the
    duplicate check."""
    import yaml

    ci = yaml.safe_load(
        (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml").read_text()
    )
    job = ci["jobs"]["split-brain"]
    assert job["name"] == "split-brain ledger backstop — blocking"
    assert "if" not in job  # runs on PRs too; a push-only blocking job bricks PR merges
    run = job["steps"][-1]["run"]
    assert "jq empty .harness/arc-metrics.jsonl" in run
    assert "uniq -d" in run and "SPLIT_BRAIN_LEDGER" in run


def test_planted_file_at_store_path_refuses(tmp_path, monkeypatch) -> None:
    """A regular file planted at the reservations-root path must refuse (dispatch ->
    hard finding), never read as an empty store that disables orphan detection and
    verified-base attribution."""
    import reservations as rs

    fake = tmp_path / "reservations"
    fake.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(rs, "reservations_root", lambda: fake)

    try:
        cg._reservation_heads()
    except RuntimeError as exc:
        assert "not a directory" in str(exc)
    else:
        raise AssertionError("a planted file at the store path must refuse")


def test_fallback_output_shape_is_validated(monkeypatch) -> None:
    """Valid JSON of the wrong shape ({} or non-dict elements) must be UNLOOKED, not a
    clean empty suite."""
    monkeypatch.setattr(cg, "_record_layer_importable", lambda: False)

    def run_with(stdout):
        monkeypatch.setattr(
            cg,
            "_run",
            lambda args, *, cwd, timeout=20: subprocess.CompletedProcess(
                args=args, returncode=0, stdout=stdout, stderr=""
            ),
        )
        return cg._emitting_detections_dispatch(Path("/repo"), "l")

    for bad in ("{}", "[1, 2]", '[{"severity": "hard"}]'):
        findings = run_with(bad)
        assert [f.code for f in findings] == ["DETECTIONS_UNAVAILABLE"], bad
        assert findings[0].severity == "hard"

    assert run_with("[]") == []  # a genuinely empty suite stays clean


def test_mid_suite_abort_preserves_earlier_findings(tmp_path, monkeypatch) -> None:
    """A raise in a later detector must not discard earlier detectors' findings (whose
    durable rows already appended) -- the abort is APPENDED as a hard finding and the
    report says aborted-after-N, never "the suite did not run"."""
    log = _isolate_gate_log(monkeypatch, tmp_path)
    ledger = tmp_path / "arc-metrics.jsonl"
    ledger.write_text(
        '{"arc_id":"pr-1","record_kind":"arc"}\n{"arc_id":"pr-1","record_kind":"arc"}\n'
    )
    monkeypatch.setattr(cg, "ARC_METRICS_JSONL", Path("arc-metrics.jsonl"))

    def raise_heads():
        raise RuntimeError("store went away mid-suite")

    monkeypatch.setattr(cg, "_reservation_heads", raise_heads)

    findings = cg._emitting_detections_safe(tmp_path, "l")

    assert [f.code for f in findings] == ["SPLIT_BRAIN_LEDGER", "DETECTIONS_UNAVAILABLE"]
    assert "aborted after 1 finding" in findings[1].message
    assert log.exists()  # the split-brain row landed and kept its projection


def test_schema_corrupt_head_is_unreadable_not_missing(tmp_path, monkeypatch) -> None:
    """A syntactically-valid but schema-corrupt head ({}) and a regular file where an
    arc directory belongs both surface as unreadable -- neither silently removes the
    arc from detection."""
    import reservations as rs

    store = tmp_path / "reservations"
    (store / "good-arc").mkdir(parents=True)
    (store / "corrupt-arc").mkdir()
    (store / "planted-file").write_text("x", encoding="utf-8")
    good = {"arc_id": "good-arc", "state": "open", "pr": 7}
    monkeypatch.setattr(rs, "reservations_root", lambda: store)
    monkeypatch.setattr(rs, "current", lambda arc_id: (1, good if arc_id == "good-arc" else {}))

    heads, unreadable = cg._reservation_heads()

    assert heads == [good]
    assert unreadable == ["corrupt-arc", "planted-file"]


def test_revalidation_raises_on_schema_corrupt_head(monkeypatch) -> None:
    import reservations as rs

    monkeypatch.setattr(rs, "current", lambda arc_id: (1, {}))

    try:
        cg._reservation_head_current("pr-9")
    except RuntimeError as exc:
        assert "schema-corrupt" in str(exc)
    else:
        raise AssertionError("a schema-corrupt head must raise on revalidation")


def test_symlinked_lease_refused(tmp_path, monkeypatch) -> None:
    """read_lease() follows the LEASE symlink, so the strict wrapper must refuse it
    before a forged target reaches any check."""
    import merge_door as md

    target = tmp_path / "target.json"
    target.write_text(json.dumps({"lease_token": "t", "state": "held"}), encoding="utf-8")
    link = tmp_path / "LEASE"
    link.symlink_to(target)
    monkeypatch.setattr(md, "LEASE", link)

    try:
        cg._door_lease_strict()
    except RuntimeError as exc:
        assert "symlink" in str(exc)
    else:
        raise AssertionError("a symlinked LEASE must refuse")


def test_symlinked_blocked_sidecar_refused(tmp_path, monkeypatch) -> None:
    """A symlinked blocked sidecar could carry a manipulated timestamp that keeps the
    stale-lease detection permanently below its bound -- refuse it."""
    import merge_door as md

    door = tmp_path / "door"
    door.mkdir()
    lease_file = door / "LEASE"
    lease_file.write_text(json.dumps({"lease_token": "tok", "state": "held"}), encoding="utf-8")
    forged = door / "forged.json"
    forged.write_text(
        json.dumps(
            {
                "blocked_at_sha": "e" * 40,
                "blocked_reason": "x",
                "blocked_at": "2099-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (door / "LEASE.tok.blocked").symlink_to(forged)
    monkeypatch.setattr(md, "DOOR", door)
    monkeypatch.setattr(md, "LEASE", lease_file)

    try:
        cg._door_lease_strict()
    except RuntimeError as exc:
        assert "sidecar" in str(exc)
    else:
        raise AssertionError("a symlinked blocked sidecar must refuse")


def test_bare_forged_adjudication_does_not_suppress(tmp_path, monkeypatch) -> None:
    """A standalone adjudication row appended raw (no finding lineage) must not mute a
    hard detection -- suppression requires a validated finding row PLUS its validated
    adjudication (codex r9)."""
    log = _isolate_gate_log(monkeypatch, tmp_path)
    mismatch = [("m" * 40, "b" * 40, "c" * 40)]
    evidence = (
        f"merge {'m' * 12} first parent {'b' * 12} != verified base {'c' * 12} -- "
        "race window hit; re-validate"
    )
    forged = {
        "finding_id": f"BASE_TOCTOU:nohead:{fr.location_hash('merge-' + 'm' * 12)}:1",
        "record_kind": "finding_adjudication",
        "ts": "2099-01-01T00:00:00Z",
        "arc_id": "merge-" + "m" * 12,
        "lane_id": "l",
        "location": "merge-" + "m" * 12,
        "observed_evidence": evidence,
        "expected_contract": "C-HE-12",
        "severity": "hard",
        "finding_type": "terminal-base_toctou",
        "lineage_claim": "guard",
        "producer": "BASE_TOCTOU",
        "head_sha": None,
        "base_sha": None,
        "diff_digest": None,
        "round_n": None,
        "cause_attribution": "base_toctou",
        "disposition": "suppressed",
        "disposition_actor": "operator",
        "unique_catch": None,
    }
    log.write_text(json.dumps(forged) + "\n", encoding="utf-8")

    fs = cg.check_base_toctou(mismatch, lane_id="l")

    assert [f.code for f in fs] == ["BASE_TOCTOU"]  # the forgery muted nothing


def test_blocked_lease_missing_blocked_at_raises(monkeypatch) -> None:
    """A blocked lease always carries blocked_at (mark_blocked writes it); absence is
    malformed door state, never 'not stale'."""
    import merge_door as md

    monkeypatch.setattr(
        cg, "_door_lease_strict", lambda: {"state": "blocked", "pr": 5, "lease_token": "t"}
    )
    monkeypatch.setattr(md, "POST_MERGE_CI_BOUND_S", 1)

    try:
        cg._blocked_lease_older_than_bound()
    except RuntimeError as exc:
        assert "blocked_at" in str(exc)
    else:
        raise AssertionError("missing blocked_at must raise, not read as not-stale")


def test_valid_head_binds_enum_and_directory() -> None:
    """A typo'd state would be silently skipped by every == comparison; an arc_id
    differing from its directory would consult another reservation (codex r10)."""
    assert cg._valid_head({"arc_id": "a", "state": "open"}, arc_id="a") is True
    assert cg._valid_head({"arc_id": "a", "state": "opne"}, arc_id="a") is False
    assert cg._valid_head({"arc_id": "b", "state": "open"}, arc_id="a") is False


def test_symlinked_door_dir_refused_in_lease_read(tmp_path, monkeypatch) -> None:
    """A symlinked door dir relocates LEASE and every sidecar to external state; each
    child check would pass against the forged targets (codex r10 -- the r7 retraction
    dropped this check with the attestation and it is restored here)."""
    import merge_door as md

    real = tmp_path / "real"
    real.mkdir()
    (real / "LEASE").write_text(json.dumps({"lease_token": "t", "state": "held"}), encoding="utf-8")
    door = tmp_path / "merge-door"
    door.symlink_to(real)
    monkeypatch.setattr(md, "DOOR", door)
    monkeypatch.setattr(md, "LEASE", door / "LEASE")

    try:
        cg._door_lease_strict()
    except RuntimeError as exc:
        assert "symlink" in str(exc)
    else:
        raise AssertionError("a symlinked door dir must refuse")


def test_core_mutated_adjudication_does_not_suppress(tmp_path, monkeypatch) -> None:
    """An adjudication reusing a REAL finding_id but mutating immutable core (lane_id)
    passes fr.validate in isolation and must still not mute (codex r12: cross-row
    core + ts invariants re-checked at read time)."""
    log = _isolate_gate_log(monkeypatch, tmp_path)
    mismatch = [("m" * 40, "b" * 40, "c" * 40)]

    assert [f.code for f in cg.check_base_toctou(mismatch, lane_id="l")] == ["BASE_TOCTOU"]
    row = json.loads(log.read_text().splitlines()[0])
    forged = {
        **row,
        "record_kind": "finding_adjudication",
        "ts": "2099-01-01T00:00:00Z",
        "disposition": "suppressed",
        "disposition_actor": "operator",
        "lane_id": "attacker-lane",  # mutated immutable core
    }
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(forged) + "\n")

    assert [f.code for f in cg.check_base_toctou(mismatch, lane_id="l")] == ["BASE_TOCTOU"]


def test_blocked_lease_age_arithmetic_uses_real_bounds(monkeypatch) -> None:
    """The age comparison itself, against the real POST_MERGE_CI_BOUND_S +
    REFRESH_BOUND_S constants (codex r13: stubbing the whole helper left the
    arithmetic unexercised)."""

    def lease_at(ts):
        return {
            "state": "blocked",
            "pr": 5,
            "lease_token": "tok",
            "reservation_id": "u-x",
            "blocked_at_sha": "d" * 40,
            "blocked_at": ts,
        }

    monkeypatch.setattr(cg, "_door_lease_strict", lambda: lease_at("1970-01-01T00:00:00Z"))
    assert cg._blocked_lease_older_than_bound()["pr"] == 5  # far past the bound

    from datetime import datetime, timedelta

    recent = (datetime.now(UTC) - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    monkeypatch.setattr(cg, "_door_lease_strict", lambda: lease_at(recent))
    assert cg._blocked_lease_older_than_bound() is None  # within the bound

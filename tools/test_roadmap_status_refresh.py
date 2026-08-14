"""Tests for tools/roadmap_status_refresh.py.

The load-bearing test is `test_hash_parity_with_bash_hook` — every other test
can be wrong in a merely-annoying way; a hash-parity break silently makes
every future session's SessionStart hook report false `[ROADMAP DRIFT]`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import roadmap_status_refresh as rsr

ROOT = Path(__file__).resolve().parents[1]
LIB_SH = ROOT / "tools" / "hooks" / "lib.sh"


def _bash_hook_state_hash(head8: str, prs_csv: str, forks: str, batch: str) -> str:
    out = subprocess.run(
        [
            "bash",
            "-c",
            f'source {LIB_SH} && hook_state_hash "$1" "$2" "$3" "$4"',
            "_",
            head8,
            prs_csv,
            forks,
            batch,
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


@pytest.mark.parametrize(
    "head8,prs_csv,forks,batch",
    [
        ("c70b3296", "", "91", ".harness/phase-7d-retirement-events-batch-57.md"),
        ("abcd1234", "3:foo,7:bar", "5", ".harness/phase-7d-retirement-events-batch-9.md"),
        ("00000000", "", "0", ""),
    ],
)
def test_hash_parity_with_bash_hook(head8, prs_csv, forks, batch):
    """Python hash12() must byte-match bash hook_state_hash for every input shape."""
    assert rsr.hash12(head8, prs_csv, forks, batch) == _bash_hook_state_hash(
        head8, prs_csv, forks, batch
    )


def test_hash12_matches_known_recipe():
    # sha256("a|b|c|d")[:12] computed independently (python -c) as a pinned literal.
    assert rsr.hash12("a", "b", "c", "d") == "b54856b7a870"


SAMPLE = """# Roadmap status dashboard

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `deadbeef0000` |
| `last_refreshed` | 2026-01-01T00:00:00Z |
| `git_head` | `aaaaaaaa` — old note |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-1.md` |
| `open_fork_doc_count` | 3 |

**Hash recipe.** stuff.

---

## Next action

Some agent-authored prose that must survive untouched.

**Current next action (post-#1).** The next implementable unit is `R-1`.

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none)* | — | — | No open PRs at refresh time. |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #2 | 2026-01-02 | second |
| PR #1 | 2026-01-01 | first |

---

## Drift detection log

| Date | Source | Resolution |
|---|---|---|
| 2026-01-05 | e5 | r5 |
| 2026-01-04 | e4 | r4 |
| 2026-01-03 | e3 | r3 |
"""


def test_prepend_recently_completed_caps_and_dedups():
    text = rsr.prepend_recently_completed(SAMPLE, "PR #3", "2026-01-03", "third")
    rows = rsr._get_table_data_rows(text, rsr.RECENTLY_COMPLETED_HEADING)
    assert rows[0].startswith("| PR #3 |")
    assert len(rows) == 3  # was 2, capped well under 5

    # idempotent re-application with the same PR ref replaces, not duplicates
    text2 = rsr.prepend_recently_completed(text, "PR #3", "2026-01-03", "third (updated)")
    rows2 = rsr._get_table_data_rows(text2, rsr.RECENTLY_COMPLETED_HEADING)
    assert sum(1 for r in rows2 if r.startswith("| PR #3 |")) == 1
    assert "updated" in rows2[0]


def test_prepend_recently_completed_respects_cap_of_5():
    text = SAMPLE
    for n in range(3, 9):
        text = rsr.prepend_recently_completed(text, f"PR #{n}", f"2026-01-0{n}", f"note {n}")
    rows = rsr._get_table_data_rows(text, rsr.RECENTLY_COMPLETED_HEADING)
    assert len(rows) == 5
    assert rows[0].startswith("| PR #8 |")


def test_trim_drift_log_is_pure_and_writes_nothing(tmp_path):
    """trim_drift_log() must never touch disk itself — callers decide whether to
    write, so --dry-run has zero side effects (regression: an earlier version
    wrote the archive unconditionally, silently mutating it even under --dry-run)."""
    archive = tmp_path / "archive.md"
    text = SAMPLE
    for n in range(6, 20):
        text = rsr.prepend_drift_log(text, f"2026-02-{n:02d}", f"src{n}", f"res{n}")
    rsr.trim_drift_log(text, archive, cap=rsr.DRIFT_LOG_CAP)
    assert not archive.exists()


def test_trim_drift_log_moves_overflow_to_archive(tmp_path):
    archive = tmp_path / "archive.md"
    text = SAMPLE
    for n in range(6, 13):
        text = rsr.prepend_drift_log(text, f"2026-02-{n:02d}", f"src{n}", f"res{n}")
    rows_before = rsr._get_table_data_rows(text, rsr.DRIFT_LOG_HEADING)
    assert len(rows_before) == 10  # 3 original + 7 new

    trimmed, new_archive_text, moved = rsr.trim_drift_log(text, archive, cap=rsr.DRIFT_LOG_CAP)
    rows_after = rsr._get_table_data_rows(trimmed, rsr.DRIFT_LOG_HEADING)
    assert len(rows_after) <= rsr.DRIFT_LOG_CAP
    assert moved == 0  # exactly at cap, nothing to move yet
    assert new_archive_text is None  # nothing to write

    # push it over the cap
    text2 = rsr.prepend_drift_log(trimmed, "2026-02-20", "src20", "res20")
    trimmed2, new_archive_text2, moved2 = rsr.trim_drift_log(text2, archive, cap=rsr.DRIFT_LOG_CAP)
    rows_final = rsr._get_table_data_rows(trimmed2, rsr.DRIFT_LOG_HEADING)
    assert len(rows_final) == rsr.DRIFT_LOG_CAP
    assert moved2 == 1
    assert new_archive_text2 is not None
    assert "e3" in new_archive_text2  # oldest original row landed in the archive
    assert not archive.exists()  # still nothing written — caller's job


def test_trim_drift_log_idempotent_second_run_moves_nothing(tmp_path):
    archive = tmp_path / "archive.md"
    text = SAMPLE
    for n in range(6, 14):
        text = rsr.prepend_drift_log(text, f"2026-02-{n:02d}", f"src{n}", f"res{n}")
    once, once_archive_text, moved1 = rsr.trim_drift_log(text, archive, cap=rsr.DRIFT_LOG_CAP)
    assert moved1 > 0
    assert once_archive_text is not None
    archive.write_text(once_archive_text)  # simulate the caller's write
    twice, twice_archive_text, moved2 = rsr.trim_drift_log(once, archive, cap=rsr.DRIFT_LOG_CAP)
    assert moved2 == 0
    assert twice_archive_text is None
    assert once == twice


def test_prepend_drift_log_is_noop_on_identical_reapply():
    text = rsr.prepend_drift_log(SAMPLE, "2026-01-06", "e6", "r6")
    text2 = rsr.prepend_drift_log(text, "2026-01-06", "e6", "r6")
    assert text == text2


def test_refresh_in_flight_renders_open_prs():
    state = rsr.WorkspaceState(
        head8="cafebabe", prs_csv="10:feat-a,20:feat-b", fork_count="4", batch_path="x"
    )
    text = rsr.refresh_in_flight(SAMPLE, state)
    rows = rsr._get_table_data_rows(text, rsr.IN_FLIGHT_HEADING)
    assert len(rows) == 2
    assert "#10" in rows[0] and "feat-a" in rows[0]


def test_refresh_in_flight_none_open():
    state = rsr.WorkspaceState(head8="cafebabe", prs_csv="", fork_count="4", batch_path="x")
    text = rsr.refresh_in_flight(SAMPLE, state)
    rows = rsr._get_table_data_rows(text, rsr.IN_FLIGHT_HEADING)
    assert len(rows) == 1
    assert "none" in rows[0]


def test_refresh_anchor_updates_hash_and_preserves_untouched_sections():
    state = rsr.WorkspaceState(
        head8="cafebabe", prs_csv="", fork_count="7", batch_path=".harness/batch-9.md"
    )
    text = rsr.refresh_anchor(SAMPLE, state, "new note", "2026-03-01T00:00:00Z")
    assert f"`{state.hash12()}`" in text
    assert "`cafebabe` — new note" in text
    assert "Some agent-authored prose that must survive untouched." in text


def test_validate_flags_cap_violations():
    text = SAMPLE
    for n in range(6, 20):
        text = rsr._replace_table_data_rows(
            text,
            rsr.DRIFT_LOG_HEADING,
            [f"| 2026-02-{i:02d} | e{i} | r{i} |" for i in range(6, n)],
        )
    violations = rsr.validate(text)
    assert any("exceeds cap" in v and "Drift detection log" in v for v in violations)


def test_validate_clean_sample_has_no_cap_violations():
    violations = rsr.validate(SAMPLE)
    cap_violations = [v for v in violations if "exceeds cap" in v or "duplicate" in v]
    assert cap_violations == []


# --- U-CTX-03: head byte budget + archive-bypass guard ------------------------


def test_validate_clean_sample_is_under_byte_budget():
    violations = rsr.validate(SAMPLE)
    assert not any("head byte budget" in v for v in violations)


def test_head_byte_budget_constant_is_pinned():
    # Merge-gate lens 3 on this arc: the bloat test below reads the constant
    # and therefore SELF-SCALES — a silent 10x raise of the budget would keep
    # every witness green. The ratified R1 rule-3 figure is a literal pin.
    assert rsr.HEAD_BYTE_BUDGET == 25_600


def test_validate_flags_byte_budget_violation():
    # Bloat the Next action prose well past HEAD_BYTE_BUDGET without touching
    # any other section's structure.
    bloated = SAMPLE.replace(
        "Some agent-authored prose that must survive untouched.",
        "x" * (rsr.HEAD_BYTE_BUDGET + 500),
    )
    violations = rsr.validate(bloated)
    assert any("head byte budget" in v for v in violations)


def test_validate_clean_sample_has_no_inline_history_violation():
    violations = rsr.validate(SAMPLE)
    assert not any("Prior next action" in v and "Round N" in v for v in violations)


def test_validate_flags_inline_prior_next_action_paragraph():
    # This is the U-CTX-03 AC #2 mutation-probe target: a `Prior next action`
    # paragraph re-accumulating inline in "## Next action" instead of living in
    # NEXT_ACTION_ARCHIVE is exactly the regression the archive split guards
    # against.
    regressed = SAMPLE.replace(
        "Some agent-authored prose that must survive untouched.",
        "Some agent-authored prose that must survive untouched.\n\n"
        "**Prior next action (post-#999).** Some stale round that should have "
        "been archived instead.",
    )
    violations = rsr.validate(regressed)
    assert any("Prior next action" in v for v in violations)


def test_validate_flags_inline_round_n_paragraph():
    regressed = SAMPLE.replace(
        "Some agent-authored prose that must survive untouched.",
        "Some agent-authored prose that must survive untouched.\n\n"
        "**Round 12 — some stale round that should have been archived.**",
    )
    violations = rsr.validate(regressed)
    assert any("Round N" in v for v in violations)


def test_next_action_archive_is_distinct_from_drift_log_archive():
    # U-CTX-03 AC #2's structural half: the two archives must never collapse
    # into the same file, or a drift-log trim's write would silently also be a
    # next-action-archive write.
    assert rsr.NEXT_ACTION_ARCHIVE.resolve() != rsr.DEFAULT_ARCHIVE.resolve()


def test_validate_flags_zero_current_next_action_paragraphs():
    # codex round-5: zero Current paragraphs = the live pointer is gone.
    broken = SAMPLE.replace("**Current next action (post-#1).**", "**Formerly current.**")
    violations = rsr.validate(broken)
    assert any("exactly ONE" in v and "found 0" in v for v in violations)


def test_validate_flags_duplicate_current_next_action_paragraphs():
    # codex round-5: a forgotten replace leaves TWO Currents; hook_roadmap_next
    # would consume whichever comes first (a potentially stale pointer) while
    # the Prior/Round-N inline-history regex stays silent.
    doubled = SAMPLE.replace(
        "**Current next action (post-#1).** The next implementable unit is `R-1`.",
        "**Current next action (post-#1).** The next implementable unit is `R-1`.\n\n"
        "**Current next action (post-#2).** The next implementable unit is `R-2`.",
    )
    violations = rsr.validate(doubled)
    assert any("exactly ONE" in v and "found 2" in v for v in violations)


def _git_scratch_repo(tmp_path: Path, title: str, files: dict[str, str]) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    env_cmds = [
        ["git", "init", "-q"],
        ["git", "config", "user.email", "t@t"],
        ["git", "config", "user.name", "t"],
    ]
    for cmd in env_cmds:
        subprocess.run(cmd, cwd=repo, check=True, capture_output=True)
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        subprocess.run(["git", "add", rel], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", title], cwd=repo, check=True, capture_output=True)
    return repo


def test_head_refresh_shape_flags_refresh_commit_touching_archive(tmp_path):
    # U-CTX-03 AC #2's git-shape half (codex round-2): a refresh-titled HEAD
    # whose changed-set includes the next-action archive must be a violation.
    repo = _git_scratch_repo(
        tmp_path,
        "ops: roadmap status refresh post-#9999",
        {
            ".harness/roadmap_status.md": "x",
            ".harness/roadmap-next-action-archive.md": "y",
        },
    )
    violations = rsr.check_head_refresh_shape(repo)
    assert len(violations) == 1
    assert "EXACTLY" in violations[0]


def test_head_refresh_shape_clean_on_single_file_refresh(tmp_path):
    repo = _git_scratch_repo(
        tmp_path,
        "ops: roadmap status refresh post-#9999",
        {".harness/roadmap_status.md": "x"},
    )
    assert rsr.check_head_refresh_shape(repo) == []


def test_head_refresh_shape_skips_at_shallow_boundary(tmp_path):
    # codex round-3: a depth-1 CI checkout makes `git show HEAD` list the
    # ENTIRE tree (parentless root-commit diff) — judging the set there would
    # fail every legitimate refresh. The check must SKIP at a shallow
    # boundary (the arc-ledger CI job fetches full history, so the gate still
    # enforces where a parent exists).
    origin = _git_scratch_repo(
        tmp_path,
        "seed: base",
        {".harness/roadmap_status.md": "base", "other.md": "x"},
    )
    (origin / ".harness" / "roadmap_status.md").write_text("refreshed")
    subprocess.run(
        ["git", "commit", "-aqm", "ops: roadmap status refresh post-#9999"],
        cwd=origin,
        check=True,
        capture_output=True,
    )
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(shallow)],
        check=True,
        capture_output=True,
    )
    # sanity: this IS the failure shape being guarded against — at depth 1 the
    # refresh-titled HEAD's `git show` lists both tracked files.
    assert rsr.check_head_refresh_shape(shallow) == []


def test_cli_rejects_archive_aliased_onto_target_checkouts_archive(tmp_path, capsys):
    # codex round-3: with --status pointing at ANOTHER checkout, that
    # checkout's own next-action archive must be recognized as protected too.
    other = tmp_path / "other"
    (other / ".harness").mkdir(parents=True)
    status = other / ".harness" / "roadmap_status.md"
    status.write_text("stub")
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(other / ".harness" / "roadmap-next-action-archive.md"),
            "--check",
        ]
    )
    assert rc == 2
    assert "protected next-action archive" in capsys.readouterr().err


def test_head_refresh_shape_fails_closed_on_git_error_inside_work_tree(tmp_path, monkeypatch):
    # codex round-4: a git failure INSIDE a detected work tree must be a
    # violation, not a skip — returning [] there reports success without
    # enforcing the file-set gate at all. (A non-git dir still skips: the
    # is-inside-work-tree probe answers that intentionally.)
    repo = _git_scratch_repo(
        tmp_path,
        "ops: roadmap status refresh post-#9999",
        {".harness/roadmap_status.md": "x"},
    )
    real_run = subprocess.run

    def failing_git(cmd, *args, **kwargs):
        if cmd[:2] == ["git", "log"]:
            raise subprocess.TimeoutExpired(cmd, 10)
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(rsr.subprocess, "run", failing_git)
    violations = rsr.check_head_refresh_shape(repo)
    assert len(violations) == 1
    assert "failing closed" in violations[0]


def test_head_refresh_shape_skips_non_git_directory(tmp_path):
    assert rsr.check_head_refresh_shape(tmp_path) == []


def test_head_refresh_shape_fails_closed_when_probe_errors_with_git_marker(tmp_path, monkeypatch):
    # codex round-8: probe error in a dir carrying a .git marker is a real
    # checkout whose git is broken — must be a violation, not a skip.
    repo = _git_scratch_repo(
        tmp_path, "ops: roadmap status refresh post-#9999", {".harness/roadmap_status.md": "x"}
    )

    def raising_probe(cmd, *args, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 10)

    monkeypatch.setattr(rsr.subprocess, "run", raising_probe)
    violations = rsr.check_head_refresh_shape(repo)
    assert len(violations) == 1
    assert "failing closed" in violations[0]


def test_informational_severity_is_prefix_structural_not_substring():
    # codex round-8: a HARD violation whose interpolated text merely CONTAINS
    # the word "informational" must never be softened — severity is carried by
    # the validator's own prefix, not by substring search.
    hard_msg = "refresh touched informational-notes.md — wrong changed-file set"
    assert not hard_msg.startswith(rsr.INFORMATIONAL_PREFIX)
    soft_msg = rsr.INFORMATIONAL_PREFIX + "hash lag, verify carve-out"
    assert soft_msg.startswith(rsr.INFORMATIONAL_PREFIX)


def _merge_no_ff(repo: Path, branch: str, merge_title: str) -> None:
    subprocess.run(
        ["git", "merge", "--no-ff", "-q", "-m", merge_title, branch],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def test_head_refresh_shape_accepts_merge_wrapped_single_file_refresh(tmp_path):
    # codex round-9: a `git merge --no-ff`-landed refresh keeps the reserved
    # prefix on a MERGE commit, where plain `git show --name-only` (combined
    # diff) can return NO paths — the gate must judge the FIRST-PARENT diff
    # and accept the legitimate one-file shape.
    repo = _git_scratch_repo(tmp_path, "seed: base", {".harness/roadmap_status.md": "base"})
    subprocess.run(
        ["git", "checkout", "-q", "-b", "refresh-branch"], cwd=repo, check=True, capture_output=True
    )
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed")
    subprocess.run(
        ["git", "commit", "-aqm", "ops: roadmap status refresh post-#9999"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "-q", "-"], cwd=repo, check=True, capture_output=True)
    _merge_no_ff(repo, "refresh-branch", "ops: roadmap status refresh post-#9999")
    assert rsr.check_head_refresh_shape(repo) == []


def test_head_refresh_shape_flags_merge_wrapped_refresh_touching_extra_files(tmp_path):
    repo = _git_scratch_repo(tmp_path, "seed: base", {".harness/roadmap_status.md": "base"})
    subprocess.run(
        ["git", "checkout", "-q", "-b", "wide-branch"], cwd=repo, check=True, capture_output=True
    )
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed")
    (repo / "extra.md").write_text("x")
    subprocess.run(["git", "add", "extra.md"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-aqm", "ops: roadmap status refresh post-#9999"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "-q", "-"], cwd=repo, check=True, capture_output=True)
    _merge_no_ff(repo, "wide-branch", "ops: roadmap status refresh post-#9999")
    violations = rsr.check_head_refresh_shape(repo)
    assert len(violations) == 1
    assert "extra.md" in violations[0]


def test_head_refresh_shape_pr_title_governs_over_commit_subject(tmp_path):
    # codex round-10: the §12.2.1 invariant binds on the PR TITLE. A refresh-
    # titled PR whose head commit carries an ORDINARY subject, with an extra
    # file hidden across base..head, must be flagged when judged in PR context
    # (title_override + base) — the head-commit subject alone would skip.
    repo = _git_scratch_repo(tmp_path, "seed: base", {".harness/roadmap_status.md": "base"})
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    (repo / ".harness" / "roadmap_status.md").write_text("refreshed")
    (repo / "extra.md").write_text("x")
    subprocess.run(["git", "add", "extra.md"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-aqm", "chore: ordinary commit subject"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    # head-commit-subject judgement alone: skips (ordinary subject)
    assert rsr.check_head_refresh_shape(repo) == []
    # PR-context judgement: PR title + whole base...head diff → violation
    violations = rsr.check_head_refresh_shape(
        repo,
        base=base_sha,
        title_override="ops: roadmap status refresh post-#9999",
    )
    assert len(violations) == 1
    assert "extra.md" in violations[0]
    # ...and a content-titled PR with the same diff is not the gate's business
    assert (
        rsr.check_head_refresh_shape(repo, base=base_sha, title_override="feat: some content PR")
        == []
    )


def test_head_refresh_shape_noop_on_content_commit(tmp_path):
    # a content-titled commit may touch anything — the shape rule binds only
    # refresh-titled commits.
    repo = _git_scratch_repo(
        tmp_path,
        "feat: some content change",
        {
            ".harness/roadmap_status.md": "x",
            ".harness/roadmap-next-action-archive.md": "y",
        },
    )
    assert rsr.check_head_refresh_shape(repo) == []


def test_cli_fails_closed_on_unset_shape_title_env(monkeypatch, capsys):
    # codex round-12: an unset/empty --shape-title-env variable must be a hard
    # refusal, not a silent fallback to the commit subject.
    monkeypatch.delenv("SHAPE_TITLE_PROBE", raising=False)
    rc = rsr.main(["--check", "--shape-title-env", "SHAPE_TITLE_PROBE"])
    assert rc == 2
    assert "unset or empty" in capsys.readouterr().err
    monkeypatch.setenv("SHAPE_TITLE_PROBE", "")
    rc = rsr.main(["--check", "--shape-title-env", "SHAPE_TITLE_PROBE"])
    assert rc == 2


def test_cli_rejects_case_variant_archive_alias_on_case_insensitive_fs(tmp_path, capsys):
    # codex round-11: on a case-insensitive filesystem (macOS default) an
    # upper-cased spelling names the SAME file while resolve() preserves
    # casing — file identity (samefile) must close the alias. Skipped on
    # case-sensitive filesystems where the variant is genuinely a different
    # (nonexistent) path.
    probe = tmp_path / "case_probe.txt"
    probe.write_text("x")
    if not (tmp_path / "CASE_PROBE.TXT").exists():
        pytest.skip("case-sensitive filesystem — the alias cannot exist here")
    variant = Path(str(rsr.NEXT_ACTION_ARCHIVE).upper())
    rc = rsr.main(["--archive", str(variant), "--check"])
    assert rc == 2
    assert "protected next-action archive" in capsys.readouterr().err


def test_cli_rejects_archive_aliased_onto_next_action_archive(capsys):
    # U-CTX-03 AC #2's runtime half: the structural check above compares only
    # the hard-coded defaults, so a caller passing
    # `--archive .harness/roadmap-next-action-archive.md` would otherwise let a
    # drift-log overflow rewrite the protected round history. main() must
    # reject the effective path before any write-capable mode runs.
    rc = rsr.main(["--archive", str(rsr.NEXT_ACTION_ARCHIVE), "--check"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "protected next-action archive" in err


def test_actual_roadmap_status_is_under_byte_budget_and_has_no_inline_history():
    """Runs --check's own validate() against the REAL post-truncation
    .harness/roadmap_status.md (not a synthetic SAMPLE) — the concrete AC #2 +
    AC #3 regression guard for the U-CTX-03 truncation itself."""
    text = rsr.DEFAULT_STATUS.read_text(encoding="utf-8")
    assert len(text.encode("utf-8")) <= rsr.HEAD_BYTE_BUDGET
    violations = rsr.validate(text)
    hard = [v for v in violations if not v.startswith(rsr.INFORMATIONAL_PREFIX)]
    assert hard == [], hard


def test_actual_next_action_archive_exists_and_is_not_referenced_as_a_read_target():
    """U-CTX-05: the archive must exist (nothing was silently dropped) and must
    never be named as something to be READ WHOLESALE by any doc in-repo — grep
    is the query-not-Read discipline, not a wholesale read instruction."""
    assert rsr.NEXT_ACTION_ARCHIVE.is_file()
    archive_text = rsr.NEXT_ACTION_ARCHIVE.read_text(encoding="utf-8")
    assert "Prior next action (post-#1285)" in archive_text
    # Superseded rounds carry the label the LIVE dashboard demoted them to —
    # verbatim provenance (codex round-2 catch: an archived round labelled
    # "Current" after supersession left two "Current" entries).
    assert "Prior next action (post-#1290)" in archive_text
    # PRIOR-ONLY (codex round-6, resolution (b)): the current round lives ONLY
    # in the live head — R1 rule 2 means the one-file terminating refresh can
    # never rotate this archive, so it must not claim currency at all.
    assert archive_text.count("**Current next action (") == 0
    # ...and the live head's current round must NOT already sit in the archive.
    status_text = (ROOT / ".harness" / "roadmap_status.md").read_text(encoding="utf-8")
    import re as _re

    m = _re.search(r"\*\*Current next action \((post-#\d+)\)", status_text)
    assert m is not None
    assert f"({m.group(1)})" not in archive_text


# --- Drift-log BYTE budget (the cap that row-count alone never enforced) ------

SAMPLE_ARCHIVE = (
    "# Roadmap next-action round archive\n\n"
    "Header prose describing the archive.\n\n"
    "---\n\n"
    "**Prior next action (post-#0).** An older round.\n"
)


def _fat_drift_row(n: int, size: int = 1_200) -> tuple[str, str, str]:
    return (f"2026-03-{n:02d}", f"src{n}", "r" * size)


def test_drift_log_byte_budget_trims_rows_the_row_cap_alone_would_keep(tmp_path):
    """The 2026-08-13 saturation in one assertion: ten rows is a LEGAL row count,
    yet those ten rows were 9,620 B — 38% of the whole-file budget. Row count
    could never see it, so the head saturated while --check reported OK."""
    archive = tmp_path / "archive.md"
    text = SAMPLE
    for n in range(1, 8):
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    rows_before = rsr._get_table_data_rows(text, rsr.DRIFT_LOG_HEADING)
    assert len(rows_before) <= rsr.DRIFT_LOG_CAP, "row cap alone is NOT violated here"

    trimmed, new_archive_text, moved = rsr.trim_drift_log(text, archive)
    assert moved > 0, "byte budget must trim what the row cap accepts"
    kept = rsr._get_table_data_rows(trimmed, rsr.DRIFT_LOG_HEADING)
    kept_bytes = sum(len(r.encode("utf-8")) + 1 for r in kept)
    assert kept_bytes <= rsr.DRIFT_LOG_BYTE_BUDGET
    # lossless: every trimmed row is in the archive text, none deleted
    assert new_archive_text is not None
    for row in rows_before[len(kept) :]:
        assert row in new_archive_text


def test_drift_log_always_keeps_the_newest_row_even_when_oversized(tmp_path):
    """max(1, ...): an empty data-row block would leave a dangling table header
    that `_table_block_span` can no longer parse, so a single row larger than the
    whole budget is KEPT and reported, never trimmed into unparseability."""
    archive = tmp_path / "archive.md"
    text = rsr.prepend_drift_log(
        SAMPLE, "2026-04-01", "huge", "z" * (rsr.DRIFT_LOG_BYTE_BUDGET * 2)
    )
    trimmed, _, _ = rsr.trim_drift_log(text, archive)
    kept = rsr._get_table_data_rows(trimmed, rsr.DRIFT_LOG_HEADING)
    assert len(kept) == 1
    assert "huge" in kept[0]
    # still structurally parseable — the actual failure mode being guarded
    assert rsr._get_table_data_rows(trimmed, rsr.DRIFT_LOG_HEADING) == kept


def test_validate_flags_drift_log_byte_overflow_as_hard_violation():
    text = SAMPLE
    for n in range(1, 8):
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    violations = rsr.validate(text)
    # INFORMATIONAL, not hard: the whole-file HEAD_BYTE_BUDGET is the load-bearing
    # cap. A sub-budget that hard-blocks CI while the real cap is satisfied would
    # red `main` for every arc between this budget landing and the next trim.
    soft = [v for v in violations if v.startswith(rsr.INFORMATIONAL_PREFIX)]
    assert any("guidance budget" in v for v in soft), violations


# --- Next-action rotation (the relief valve --refresh structurally cannot be) --


def test_rotate_next_action_demotes_the_old_round_and_installs_the_new_one():
    new_text, new_archive = rsr.rotate_next_action(
        SAMPLE, SAMPLE_ARCHIVE, "1338", "The prevention arc is landed."
    )
    # live head carries exactly ONE Current paragraph, and it is the NEW one
    assert new_text.count("**Current next action (") == 1
    assert "**Current next action (post-#1338).** The prevention arc is landed." in new_text
    assert "The next implementable unit is `R-1`." not in new_text
    # the demoted round is in the archive, relabelled, body verbatim
    assert new_archive is not None
    assert "**Prior next action (post-#1).** The next implementable unit is `R-1`." in new_archive
    # ...and never as a second Current (the two-Current defect codex round-6 caught)
    assert new_archive.count("**Current next action (") == 0
    # most-recent-first: the newly demoted round precedes the older one
    assert new_archive.index("(post-#1).") < new_archive.index("(post-#0).")


def test_rotate_next_action_output_passes_the_validate_the_ci_gate_runs():
    """The rotation must not merely look right — it must satisfy the exact
    single-Current / no-inline-history invariants `--check` enforces."""
    new_text, _ = rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, "1338", "Body.")
    violations = rsr.validate(new_text)
    structural = [
        v
        for v in violations
        if not v.startswith(rsr.INFORMATIONAL_PREFIX) and rsr.NEXT_ACTION_HEADING in v
    ]
    assert structural == [], structural


def test_rotate_next_action_is_idempotent_on_the_archive():
    """Re-running must never double-append the demoted round."""
    _once, archive_once = rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, "1338", "Body.")
    assert archive_once is not None
    # rotating the SAME source round again against the already-updated archive
    _, archive_twice = rsr.rotate_next_action(SAMPLE, archive_once, "1338", "Body.")
    assert archive_twice is None, "already-archived round must not be re-appended"


def test_rotate_next_action_refuses_when_there_is_no_current_paragraph():
    with pytest.raises(rsr.RoadmapStatusError, match="no `\\*\\*Current next action"):
        rsr.rotate_next_action("## Next action\n\nnothing here\n", SAMPLE_ARCHIVE, "1", "x")


def test_rotate_next_action_refuses_an_archive_with_no_insertion_rule():
    with pytest.raises(rsr.RoadmapStatusError, match="insertion point"):
        rsr.rotate_next_action(SAMPLE, "# archive with no rule\n", "1338", "Body.")


# --- §12.2.1 enforced, not merely documented ---------------------------------


def test_refresh_refuses_the_two_file_commit_it_used_to_write_silently(tmp_path, capsys):
    """The regression this whole arc exists for: --refresh silently wrote the
    drift archive too whenever the log overflowed, producing a two-file commit
    that CANNOT be a terminating refresh (§12.2.1). It must refuse and name the
    mode that legitimately does the move — never half-write."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    text = SAMPLE
    for n in range(1, 8):
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    status.write_text(text)
    (tmp_path / ".harness" / "roadmap-next-action-archive.md").write_text(SAMPLE_ARCHIVE)
    archive = tmp_path / "drift_archive.md"

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(archive),
            "--refresh",
            "--pr",
            "PR #9999",
            "--date",
            "2026-08-14",
            "--notes",
            "n",
        ]
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert "TWO-FILE commit" in err
    assert "--trim-drift-log" in err
    # fail CLOSED: neither file may be touched by the refused run
    assert not archive.exists()
    assert status.read_text() == text


def test_rotate_next_action_cli_writes_status_and_archive(tmp_path, capsys):
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    na_archive = tmp_path / ".harness" / "roadmap-next-action-archive.md"
    na_archive.write_text(SAMPLE_ARCHIVE)

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(tmp_path / "drift_archive.md"),
            "--rotate-next-action",
            "New body.",
            "--pr",
            "#1338",
        ]
    )
    assert rc == 0
    assert "**Current next action (post-#1338).** New body." in status.read_text()
    assert "**Prior next action (post-#1).**" in na_archive.read_text()
    # the mode must SAY it is not the terminating refresh
    assert "CONTENT commit" in capsys.readouterr().err


def test_rotate_next_action_cli_requires_a_pr(tmp_path):
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    with pytest.raises(SystemExit):
        rsr.main(["--status", str(status), "--rotate-next-action", "body"])


# --- out-of-family review round 1: two byte-budget fail-opens ----------------


def test_validate_flags_a_single_oversized_row_that_trimming_cannot_fix():
    """FAIL-OPEN (codex round 1): judging "would a trim change the row count"
    instead of judging the BYTES means one 5 KB row reports clean — the newest
    row is always retained, so `len(drift) > keep_n` is False while the section
    sits 67% over budget. Those are different questions."""
    text = rsr._replace_table_data_rows(
        SAMPLE, rsr.DRIFT_LOG_HEADING, ["| 2026-01-09 | huge | " + "z" * 5000 + " |"]
    )
    soft = [v for v in rsr.validate(text) if v.startswith(rsr.INFORMATIONAL_PREFIX)]
    budget = [v for v in soft if "guidance budget" in v]
    assert budget, rsr.validate(text)
    assert "trimming cannot help" in budget[0]


def test_refresh_applies_a_trim_that_needs_no_archive_write(tmp_path, capsys):
    """FAIL-OPEN (codex round 1): when the overflow rows are ALREADY in the
    archive (idempotent re-run, or a --trim-drift-log whose archive write landed
    and whose status write did not), trim_drift_log returns changed status text
    with new_archive_text=None. --refresh read only the None, discarded the
    trimmed text, wrote a still-over-budget status and reported SUCCESS."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    text = SAMPLE
    for n in range(1, 8):
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    status.write_text(text)
    (tmp_path / ".harness" / "roadmap-next-action-archive.md").write_text(SAMPLE_ARCHIVE)
    archive = tmp_path / "drift_archive.md"

    # Pre-populate the archive with exactly the overflow, so no WRITE is owed.
    _, archive_text, _ = rsr.trim_drift_log(text, archive)
    assert archive_text is not None
    archive.write_text(archive_text)
    archive_before = archive.read_text()

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(archive),
            "--refresh",
            "--pr",
            "PR #9999",
            "--date",
            "2026-08-14",
            "--notes",
            "n",
        ]
    )
    assert rc == 0, capsys.readouterr()
    written = status.read_text()
    kept = rsr._get_table_data_rows(written, rsr.DRIFT_LOG_HEADING)
    kept_bytes = sum(len(r.encode("utf-8")) + 1 for r in kept)
    assert kept_bytes <= rsr.DRIFT_LOG_BYTE_BUDGET, "refresh wrote a still-over-budget status"
    # ...and it stayed a ONE-FILE write: the archive is untouched.
    assert archive.read_text() == archive_before


def test_rotate_next_action_refuses_an_empty_body():
    """[P2] (codex round 3): an unset shell variable would archive the live
    pointer and install a marker with no actionable text — and validate() only
    COUNTS the marker, so the empty frontier passed --check too."""
    with pytest.raises(rsr.RoadmapStatusError, match="non-empty body"):
        rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, "1338", "   ")


def test_rotate_next_action_accepts_the_documented_pr_form():
    """[P2] (codex round 2): `--pr` is documented as accepting `PR #1234`, but
    lstrip("#") produced the malformed label `(post-#PR #1234)`, which
    validate() then accepted."""
    for form in ("1234", "#1234", "PR #1234"):
        text, _ = rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, form, "Body.")
        assert "**Current next action (post-#1234).** Body." in text, form
    with pytest.raises(rsr.RoadmapStatusError, match="not a PR number"):
        rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, "not-a-pr", "Body.")


def test_rotate_next_action_is_a_no_op_when_rerun_against_its_own_output():
    """[P2] (codex round 2): re-running read the NEWLY INSTALLED paragraph as the
    current one, demoted it into the archive, and left it live as Current — so
    the archive claimed a live round was Prior. The original idempotency test
    missed it by re-running against the ORIGINAL text, not the output."""
    once, archive_once = rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, "1338", "Body.")
    assert archive_once is not None
    twice, archive_twice = rsr.rotate_next_action(once, archive_once, "1338", "Body.")
    assert twice == once
    assert archive_twice is None


def test_rotate_next_action_cli_refuses_to_write_over_the_hard_byte_cap(tmp_path, capsys):
    """[P2] (codex round 4): installing an oversized body wrote every file and
    exited 0, shipping a status file this tool's OWN validate() rejects — a
    guaranteed red on the next run."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    na_archive = tmp_path / ".harness" / "roadmap-next-action-archive.md"
    na_archive.write_text(SAMPLE_ARCHIVE)
    before = status.read_text()

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(tmp_path / "drift.md"),
            "--rotate-next-action",
            "x" * (rsr.HEAD_BYTE_BUDGET + 100),
            "--pr",
            "1338",
        ]
    )
    assert rc == 2
    assert "hard cap" in capsys.readouterr().err
    # fail CLOSED: neither file may be written by the refused run
    assert status.read_text() == before
    assert na_archive.read_text() == SAMPLE_ARCHIVE


def test_rotate_next_action_rejects_a_multi_paragraph_body():
    """[P2] (codex round 5): a multi-paragraph body wrote fine, but only its
    FIRST paragraph would ever be archived — the rest stays in the live section
    permanently, growing the head while validation still passes."""
    with pytest.raises(rsr.RoadmapStatusError, match="SINGLE paragraph"):
        rsr.rotate_next_action(SAMPLE, SAMPLE_ARCHIVE, "1338", "First para.\n\nSecond para.")


def test_trim_drift_log_can_carry_the_new_drift_event(tmp_path, capsys):
    """[P1] (codex round 5): a drift event that OVERFLOWS the log deadlocked the
    documented `--refresh --drift-source` workflow — --refresh prepends the row,
    the trim then needs an archive write, and --refresh refuses; while
    pre-running --trim-drift-log was a NO-OP because the row did not exist yet.
    The content mode now carries the event, so the refresh is genuinely one-file."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    text = SAMPLE
    for n in range(1, 3):
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    status.write_text(text)
    (tmp_path / ".harness" / "roadmap-next-action-archive.md").write_text(SAMPLE_ARCHIVE)
    archive = tmp_path / "drift_archive.md"

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(archive),
            "--trim-drift-log",
            "--drift-source",
            "the new event",
            "--drift-resolution",
            "r" * 2500,
            "--date",
            "2026-08-14",
        ]
    )
    assert rc == 0, capsys.readouterr()
    rows = rsr._get_table_data_rows(status.read_text(), rsr.DRIFT_LOG_HEADING)
    assert "the new event" in rows[0], "the new event must be live, not archived away"
    kept = sum(len(r.encode("utf-8")) + 1 for r in rows)
    assert kept <= rsr.DRIFT_LOG_BYTE_BUDGET

    # ...and the terminating refresh is now genuinely a ONE-FILE write.
    archive_before = archive.read_text()
    rc2 = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(archive),
            "--refresh",
            "--pr",
            "PR #9999",
            "--date",
            "2026-08-14",
            "--notes",
            "n",
        ]
    )
    assert rc2 == 0, capsys.readouterr()
    assert archive.read_text() == archive_before


def test_trim_drift_log_persists_a_small_event_that_needs_no_trimming(tmp_path, capsys):
    """[P2] (codex round 6) — a regression the round-5 fix introduced: a small
    event leaves the log under both limits, so trim_drift_log is a no-op and the
    `new_text != text` guard compared the already-prepended text against itself.
    The event was silently DROPPED while the command printed 'moved 0', exit 0."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(tmp_path / "drift.md"),
            "--trim-drift-log",
            "--drift-source",
            "a small new event",
            "--drift-resolution",
            "resolved",
            "--date",
            "2026-08-14",
        ]
    )
    assert rc == 0, capsys.readouterr()
    rows = rsr._get_table_data_rows(status.read_text(), rsr.DRIFT_LOG_HEADING)
    assert "a small new event" in rows[0], "the event must actually be written"


def test_rotate_next_action_keeps_the_drift_archive_in_the_target_checkout(tmp_path, capsys):
    """[P2] (codex round 7): the rotation path derived the NEXT-ACTION archive
    from the target checkout but passed the module-global DRIFT archive, so a
    cross-checkout rotation removed rows from the TARGET status and appended them
    to the CALLER's archive — contaminating one checkout and leaving the target
    without its history."""
    harness = tmp_path / ".harness"
    harness.mkdir(parents=True)
    status = harness / "roadmap_status.md"
    text = SAMPLE
    for n in range(1, 8):
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    status.write_text(text)
    (harness / "roadmap-next-action-archive.md").write_text(SAMPLE_ARCHIVE)
    target_archive = harness / "roadmap_drift_log_archive.md"
    caller_archive_before = (
        rsr.DEFAULT_ARCHIVE.read_text() if rsr.DEFAULT_ARCHIVE.is_file() else None
    )

    rc = rsr.main(["--status", str(status), "--rotate-next-action", "New body.", "--pr", "1338"])
    assert rc == 0, capsys.readouterr()
    assert target_archive.is_file(), "overflow must land in the TARGET checkout's archive"
    if caller_archive_before is not None:
        assert rsr.DEFAULT_ARCHIVE.read_text() == caller_archive_before, "caller contaminated"

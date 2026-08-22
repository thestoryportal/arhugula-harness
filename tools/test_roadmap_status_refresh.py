"""Tests for tools/roadmap_status_refresh.py.

The load-bearing test is `test_hash_parity_with_bash_hook` — every other test
can be wrong in a merely-annoying way; a hash-parity break silently makes
every future session's SessionStart hook report false `[ROADMAP DRIFT]`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# `tools/` is not a package and pytest runs under `--import-mode=importlib`, which does
# NOT put this directory on `sys.path`. Without this insert the module imports only when
# some OTHER test file in the same invocation happens to have inserted it first — an
# order-dependent pass that vanishes the moment that sibling is renamed (B-184 close-out 3).
sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    # ROW overflow (the HARD cap), not byte overflow: the refresh deliberately
    # does not enforce the SOFT byte guidance.
    for n in range(1, 14):
        text = rsr.prepend_drift_log(text, f"2026-05-{n:02d}", f"s{n}", f"r{n}")
    status.write_text(text)
    (tmp_path / ".harness" / "roadmap-next-action-archive.md").write_text(SAMPLE_ARCHIVE)
    archive = tmp_path / "drift_archive.md"

    # Pre-populate the archive with exactly the overflow, so no WRITE is owed.
    _, archive_text, _ = rsr.trim_drift_log(text, archive, byte_budget=sys.maxsize)
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
    assert len(kept) <= rsr.DRIFT_LOG_CAP, "refresh wrote a still-over-CAP status"
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


def test_trim_drift_log_refuses_to_write_over_the_hard_byte_cap(tmp_path, capsys):
    """[P2] (codex round 9): a large new resolution is RETAINED by
    _drift_keep_count (the newest row always survives), so this path wrote past
    HEAD_BYTE_BUDGET and exited 0 — producing a status file validate()
    immediately hard-rejects, guaranteeing the next CI check fails."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    before = status.read_text()
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(tmp_path / "drift.md"),
            "--trim-drift-log",
            "--drift-source",
            "huge",
            "--drift-resolution",
            "z" * (rsr.HEAD_BYTE_BUDGET + 1000),
            "--date",
            "2026-08-14",
        ]
    )
    assert rc == 2
    assert "hard cap" in capsys.readouterr().err
    assert status.read_text() == before, "must fail CLOSED"


# --- out-of-family review round 11: the PR-compatible split ------------------
def test_refresh_installs_the_next_action_in_the_same_single_file_write(tmp_path, capsys):
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    # step 1 first: the refresh REFUSES to replace an unarchived round
    (tmp_path / ".harness" / "roadmap-next-action-archive.md").write_text(
        rsr.archive_current_next_action(SAMPLE, SAMPLE_ARCHIVE) or SAMPLE_ARCHIVE
    )
    archive = tmp_path / "drift.md"

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(archive),
            "--refresh",
            "--pr",
            "PR #1338",
            "--date",
            "2026-08-14",
            "--notes",
            "shipped",
            "--next-action",
            "The prevention arc is landed; next is the B-71 impl leg.",
        ]
    )
    assert rc == 0, capsys.readouterr()
    written = status.read_text()
    assert "**Current next action (post-#1338).** The prevention arc is landed;" in written
    assert written.count("**Current next action (") == 1
    assert not archive.exists(), "the terminating refresh must stay a ONE-FILE write"
    hard = [v for v in rsr.validate(written, status) if not v.startswith(rsr.INFORMATIONAL_PREFIX)]
    assert hard == [], hard


def test_install_next_action_rejects_empty_multiparagraph_and_bad_pr():
    with pytest.raises(rsr.RoadmapStatusError, match="non-empty body"):
        rsr.install_next_action(SAMPLE, "1338", "  ")
    with pytest.raises(rsr.RoadmapStatusError, match="SINGLE paragraph"):
        rsr.install_next_action(SAMPLE, "1338", "a\n\nb")
    with pytest.raises(rsr.RoadmapStatusError, match="not a PR number"):
        rsr.install_next_action(SAMPLE, "nope", "body")


def test_refresh_refuses_to_write_over_the_hard_byte_cap(tmp_path, capsys):
    """[P2] (codex round 12): --next-action can push the head past the cap, and
    writing it would ship a status file --check rejects. The rotation and trim
    paths already refused; this one did not."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    na = tmp_path / ".harness" / "roadmap-next-action-archive.md"
    na.write_text(rsr.archive_current_next_action(SAMPLE, SAMPLE_ARCHIVE) or SAMPLE_ARCHIVE)
    before = status.read_text()
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(tmp_path / "drift.md"),
            "--refresh",
            "--pr",
            "1338",
            "--date",
            "2026-08-14",
            "--notes",
            "n",
            "--next-action",
            "x" * (rsr.HEAD_BYTE_BUDGET + 100),
        ]
    )
    assert rc == 2
    assert "hard cap" in capsys.readouterr().err
    assert status.read_text() == before, "must fail CLOSED"


# --- B-168 exit (iii): archive round N-1, so all three constraints hold -------


def test_archive_superseded_never_touches_the_status_file(tmp_path, capsys, monkeypatch):
    """`B-168` exit (iii). Archiving the round that is still CURRENT breaks the
    archive's prior-only invariant; archiving the SUPERSEDED one preserves it,
    and the write may then ride an ordinary content PR."""
    na = tmp_path / "archive.md"
    na.write_text(SAMPLE_ARCHIVE)
    superseded = "**Current next action (post-#999).** An older round."
    out = rsr.archive_superseded_round(superseded, na.read_text())
    assert out is not None
    assert "**Prior next action (post-#999).** An older round." in out
    assert out.count("**Current next action (") == 0
    # idempotent
    assert rsr.archive_superseded_round(superseded, out) is None


def test_find_superseded_round_skips_the_live_round():
    """It must never return the round that is still live — that is the whole
    point of exit (iii)."""
    live = rsr.DEFAULT_STATUS.read_text()
    live_label = rsr._current_round_label(live)
    assert live_label is not None
    found = rsr.find_superseded_round(rsr.DEFAULT_STATUS, rsr.ROOT)
    if found is not None:
        label, _ = found
        assert label != live_label


def test_install_next_action_does_not_require_prior_archiving():
    """Deliberate: under exit (iii) the archive lags by exactly one arc BY
    DESIGN. An earlier draft enforced archive-before-replace, which silently
    encoded a DIFFERENT exit and made the refresh unrunnable when it is needed."""
    out = rsr.install_next_action(SAMPLE, "1338", "New body.")
    assert "**Current next action (post-#1338).** New body." in out


def test_find_superseded_round_fails_closed_when_history_is_unreadable(tmp_path):
    """[P2] (codex round 14): `_sh` degrades to "" on any git failure, so an
    unreadable history returned None and the CLI reported 'nothing to archive'
    — leaving the owed round permanently unarchived while later runs move on to
    newer ones. 'None superseded' and 'cannot see the history' are different
    answers and must not share an exit path."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    status.write_text(SAMPLE)
    with pytest.raises(rsr.RoadmapStatusError, match="no history"):
        rsr.find_superseded_round(status, tmp_path)


def test_find_superseded_round_works_in_this_shallow_repo():
    """Shallowness is checked only on the NOT-FOUND path: this workspace is
    normally a shallow clone, so refusing up front would break the documented
    workflow outright. A round that IS found is a valid answer regardless."""
    found = rsr.find_superseded_round(rsr.DEFAULT_STATUS, rsr.ROOT)
    assert found is not None
    label, paragraph = found
    assert label != rsr._current_round_label(rsr.DEFAULT_STATUS.read_text())
    assert paragraph.startswith("**Current next action (")


def test_refresh_is_not_blocked_by_the_soft_byte_budget(tmp_path, capsys):
    """Found by dogfooding the very refresh this arc owed: keying the two-file
    refusal on the SOFT byte guidance as well as the HARD row cap made EVERY
    terminating refresh refuse the moment the live drift log exceeded guidance.
    A soft budget must never gate a hard path."""
    status = tmp_path / ".harness" / "roadmap_status.md"
    status.parent.mkdir(parents=True)
    text = SAMPLE
    for n in range(1, 6):  # over the BYTE budget, under the ROW cap
        text = rsr.prepend_drift_log(text, *_fat_drift_row(n))
    rows = rsr._get_table_data_rows(text, rsr.DRIFT_LOG_HEADING)
    assert len(rows) <= rsr.DRIFT_LOG_CAP, "precondition: row cap NOT exceeded"
    assert sum(len(r.encode()) + 1 for r in rows) > rsr.DRIFT_LOG_BYTE_BUDGET
    status.write_text(text)
    (tmp_path / ".harness" / "roadmap-next-action-archive.md").write_text(SAMPLE_ARCHIVE)
    archive = tmp_path / "drift.md"

    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(archive),
            "--refresh",
            "--pr",
            "PR #1338",
            "--date",
            "2026-08-14",
            "--notes",
            "shipped",
            "--next-action",
            "Next is the B-71 impl leg.",
        ]
    )
    assert rc == 0, capsys.readouterr()
    assert not archive.exists(), "still a ONE-FILE write"
    assert "**Current next action (post-#1338).** Next is the B-71 impl leg." in status.read_text()


# --- U-HE-28: --emit-refresh-pr-json (C-HE-06 §4(viii) continuation producer) ---------


class _P:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _scripted_run(script, calls):
    """Fake subprocess.run: first matching prefix wins; unmatched → success/empty.

    `script` is a list of (prefix_tuple, _P); `calls` records every argv.
    """

    def run(args, **kw):
        calls.append(list(args))
        for prefix, resp in script:
            if tuple(args[: len(prefix)]) == tuple(prefix):
                return resp
        return _P()

    return run


def test_emit_refresh_pr_idempotent_existing_open_pr():
    """Crash after `gh pr create`: the branch's open PR is returned, nothing re-created."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            )
        ],
        calls,
    )
    out = rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert out == {"pr": 321, "head_sha": "abc123def"}
    assert not any(c[:2] == ["git", "checkout"] for c in calls)
    assert not any(c[:3] == ["gh", "pr", "create"] for c in calls)


def test_emit_refresh_pr_pushed_branch_without_pr_creates_on_it():
    """Crash between push and create: PR is created ON the pushed branch, no new commit."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=0)),
            (("gh", "pr", "create"), _P(stdout="https://github.com/o/r/pull/77")),
            (("git", "rev-parse", "HEAD"), _P(stdout="feedbeef")),
        ],
        calls,
    )
    out = rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert out == {"pr": 77, "head_sha": "feedbeef"}
    assert [
        "git",
        "checkout",
        "-q",
        "-B",
        "roadmap-refresh-post-55",
        "origin/roadmap-refresh-post-55",
    ] in calls
    assert not any(c[:2] == ["git", "commit"] for c in calls)
    create = next(c for c in calls if c[:3] == ["gh", "pr", "create"])
    assert create[3:5] == ["--base", "main"]  # r10 P1 pin, r11 P3 witness


def test_emit_refresh_pr_fresh_path_branches_from_main_then_refreshes():
    """As-built correction: fetch + branch from origin/main BEFORE the refresh runs, so
    the refresh commit's recorded git_head is its own parent and the PR diff is
    roadmap-status-only. Commit title carries the §12.2.1 prefix."""
    calls: list[list[str]] = []
    seen: dict[str, int] = {}

    def do_refresh():
        seen["refresh_at_call_index"] = len(calls)

    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=2)),
            (("git", "diff", "--cached", "--name-only"), _P(stdout=".harness/roadmap_status.md")),
            (("gh", "pr", "create"), _P(stdout="https://github.com/o/r/pull/88")),
            (("git", "rev-parse", "HEAD"), _P(stdout="cafebabe")),
        ],
        calls,
    )
    out = rsr.emit_refresh_pr(55, run=run, do_refresh=do_refresh)
    assert out == {"pr": 88, "head_sha": "cafebabe"}
    checkout = ["git", "checkout", "-q", "-B", "roadmap-refresh-post-55", "origin/main"]
    assert checkout in calls
    assert ["git", "fetch", "-q", "origin", "+refs/heads/main:refs/remotes/origin/main"] in calls
    create = next(c for c in calls if c[:3] == ["gh", "pr", "create"])
    assert create[3:5] == ["--base", "main"]  # r10 P1 pin, r11 P3 witness
    assert seen["refresh_at_call_index"] >= calls.index(checkout) + 1
    assert ["git", "commit", "-m", "ops: roadmap status refresh post-#55"] in calls
    assert ["git", "push", "-u", "origin", "roadmap-refresh-post-55"] in calls


def test_emit_refresh_pr_refuses_two_file_commit():
    """§12.2.1: a staged set that is not exactly roadmap_status.md aborts pre-commit."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=2)),
            (
                ("git", "diff", "--cached", "--name-only"),
                _P(stdout=".harness/roadmap_status.md\n.harness/arc-ledger.yaml"),
            ),
        ],
        calls,
    )
    with pytest.raises(SystemExit, match=r"exactly \.harness/roadmap_status\.md"):
        rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert not any(c[:2] == ["git", "commit"] for c in calls)


def test_emit_refresh_pr_subcommand_failure_aborts_nonzero():
    """Any failing git/gh step raises (non-zero exit, no JSON) → the door blocks (viii)."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=2)),
            (("git", "diff", "--cached", "--name-only"), _P(stdout=".harness/roadmap_status.md")),
            (("git", "push"), _P(returncode=1, stderr="remote rejected")),
        ],
        calls,
    )
    with pytest.raises(SystemExit, match="remote rejected"):
        rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert not any(c[:3] == ["gh", "pr", "create"] for c in calls)


def test_cli_dispatch_emit_refresh_pr_json(monkeypatch, capsys):
    """--emit-refresh-pr-json N dispatches before any status read and prints the JSON."""
    monkeypatch.setattr(rsr, "emit_refresh_pr", lambda n, **kw: {"pr": n + 1, "head_sha": "aa"})
    rc = rsr.main(["--emit-refresh-pr-json", "55"])
    assert rc == 0
    assert '"pr": 56' in capsys.readouterr().out


def test_cli_emit_mode_stdout_is_json_only(monkeypatch, capsys):
    """codex r1 P1: merge_door json-parses the ENTIRE captured stdout of this mode.
    Nested progress prints (the in-process --refresh, anything else) must land on
    stderr; real stdout carries exactly the one JSON line."""

    def noisy_emit(n, **kw):
        print("refreshed .harness/roadmap_status.md: hash=abc")  # nested progress line
        return {"pr": n, "head_sha": "aa"}

    monkeypatch.setattr(rsr, "emit_refresh_pr", noisy_emit)
    rc = rsr.main(["--emit-refresh-pr-json", "55"])
    captured = capsys.readouterr()
    assert rc == 0
    import json as _json

    assert _json.loads(captured.out) == {"pr": 55, "head_sha": "aa"}
    assert "refreshed" in captured.err


def test_emit_refresh_pr_indeterminate_ls_remote_aborts():
    """codex r1 P2: only ls-remote exit 2 means 'no matching ref'. Auth/transport
    failures must abort — NOT select the fresh path and reset a pushed branch."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=128, stderr="fatal: could not read")),
        ],
        calls,
    )
    with pytest.raises(SystemExit, match="could not verify remote state"):
        rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert not any(c[:2] == ["git", "checkout"] for c in calls)


def _fresh_path_script():
    return [
        (("gh", "pr", "list"), _P(stdout="")),
        (("git", "ls-remote"), _P(returncode=2)),
        (("git", "diff", "--cached", "--name-only"), _P(stdout=".harness/roadmap_status.md")),
        (("gh", "pr", "create"), _P(stdout="https://github.com/o/r/pull/90")),
        (("git", "rev-parse", "HEAD"), _P(stdout="beadfeed")),
    ]


def test_emit_refresh_pr_consumes_matching_next_action_draft(monkeypatch, tmp_path):
    """codex r2 P2: the ship-pr-authored draft names THIS landing -> its body flows
    into the in-process refresh as --next-action and the draft is consumed."""
    argv_seen: dict[str, list[str]] = {}
    monkeypatch.setattr(rsr, "main", lambda argv: (argv_seen.setdefault("argv", argv) and 0) or 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 55\nThe next implementable unit is `U-HE-29` per the S4c order.\n")
    calls: list[list[str]] = []
    out = rsr.emit_refresh_pr(55, run=_scripted_run(_fresh_path_script(), calls))
    assert out["pr"] == 90
    assert not draft.exists()
    argv = argv_seen["argv"]
    assert "--next-action" in argv
    assert argv[argv.index("--next-action") + 1].startswith("The next implementable unit")


def test_emit_refresh_pr_ignores_mismatched_draft(monkeypatch, tmp_path, capsys):
    """A stale draft from an aborted arc must never install another arc's pointer:
    left in place, warned on stderr, no --next-action in the refresh argv."""
    argv_seen: dict[str, list[str]] = {}
    monkeypatch.setattr(rsr, "main", lambda argv: (argv_seen.setdefault("argv", argv) and 0) or 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 54\nstale pointer body\n")
    calls: list[list[str]] = []
    rsr.emit_refresh_pr(55, run=_scripted_run(_fresh_path_script(), calls))
    assert draft.exists()  # left for inspection
    assert "--next-action" not in argv_seen["argv"]
    err = capsys.readouterr().err
    assert "does not name post-pr: 55" in err
    assert "post-pr: 54" not in err  # r14 P2: content never interpolated
    # codex r5 P2: the door discards stderr on success — the warning must ALSO ride
    # the refresh PR body, the venue the operator reads
    create = next(c for c in calls if c[:3] == ["gh", "pr", "create"])
    body_arg = create[create.index("--body") + 1]
    assert "a next-action draft was present" in body_arg
    assert "post-pr: 54" not in body_arg  # r14 P2: nothing from the file is published


def test_emit_refresh_pr_explicit_flag_wins_over_draft(monkeypatch, tmp_path):
    """--next-action passed explicitly is authoritative; the draft is not consumed."""
    argv_seen: dict[str, list[str]] = {}
    monkeypatch.setattr(rsr, "main", lambda argv: (argv_seen.setdefault("argv", argv) and 0) or 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 55\ndraft body\n")
    calls: list[list[str]] = []
    rsr.emit_refresh_pr(
        55, next_action="explicit body", run=_scripted_run(_fresh_path_script(), calls)
    )
    argv = argv_seen["argv"]
    assert argv[argv.index("--next-action") + 1] == "explicit body"
    # r6 P2 rule (supersedes the r5 retire-on-override): the draft's body was NOT
    # represented in this refresh — unrepresented authoring is never deleted
    assert draft.exists()


def test_emit_refresh_pr_push_failure_keeps_draft(monkeypatch, tmp_path):
    """codex r3 P2: the draft is retired only once its content is durably represented
    by the pushed branch — a push failure must leave it for the retry."""
    monkeypatch.setattr(rsr, "main", lambda argv: 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 55\npointer body here.\n")
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=2)),
            (("git", "diff", "--cached", "--name-only"), _P(stdout=".harness/roadmap_status.md")),
            (("git", "push"), _P(returncode=1, stderr="remote rejected")),
        ],
        calls,
    )
    with pytest.raises(SystemExit):
        rsr.emit_refresh_pr(55, run=run)
    assert draft.exists()  # the retry re-reads it


def test_emit_refresh_pr_resume_paths_retire_matching_draft(monkeypatch, tmp_path):
    """A matching draft at a resume path is already represented by the pushed refresh
    commit — retired there; a mismatched draft is another arc's and stays."""
    monkeypatch.setattr(rsr, "main", lambda argv: 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 55\npointer body here.\n")
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            ),
            # live pointer body EQUALS the draft body (r8 P2) -> retire
            (
                ("git", "show"),
                _P(stdout="**Current next action (post-#55).** pointer body here."),
            ),
        ],
        calls,
    )
    rsr.emit_refresh_pr(55, run=run)
    assert not draft.exists()
    # a CORRECTED same-PR draft whose body is NOT in the pushed commit survives (r6 P2)
    draft.write_text("post-pr: 55\ncorrected pointer body\n")
    calls2: list[list[str]] = []
    run2 = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            ),
            # OLD pointer content only — the correction is not represented
            (
                ("git", "show"),
                _P(stdout="**Current next action (post-#55).** pointer body here.\\n"),
            ),
        ],
        calls2,
    )
    with pytest.raises(SystemExit, match="does not represent the authored"):
        rsr.emit_refresh_pr(55, run=run2)
    assert draft.exists()
    # another arc's draft is untouched regardless
    draft.write_text("post-pr: 54\nother arc's body\n")
    calls3: list[list[str]] = []
    run3 = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            )
        ],
        calls3,
    )
    rsr.emit_refresh_pr(55, run=run3)
    assert draft.exists()


def test_emit_refresh_pr_rejects_retargeted_or_reused_open_pr():
    """r7 P2: the idempotent resume must identity-gate the found PR — a retargeted or
    reused PR on the deterministic branch never persists for the door to merge."""
    for bad in (
        "321\tabc123def\trelease-x\tfalse\tops: roadmap status refresh post-#55",
        "321\tabc123def\tmain\tfalse\tsome unrelated PR title",
        # r10 P1: a FORK PR squatting the deterministic branch name
        "321\tabc123def\tmain\ttrue\tops: roadmap status refresh post-#55",
    ):
        calls: list[list[str]] = []
        run = _scripted_run([(("gh", "pr", "list"), _P(stdout=bad))], calls)
        with pytest.raises(SystemExit, match="not this landing's terminating refresh"):
            rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)


def test_emit_refresh_pr_draft_body_elsewhere_in_file_is_not_representation(monkeypatch, tmp_path):
    """r7 P2: the draft body appearing in a notes cell (not the live pointer
    paragraph) is NOT pointer installation — the draft survives."""
    monkeypatch.setattr(rsr, "main", lambda argv: 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 55\npointer body here.\n")
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            ),
            (
                ("git", "show"),
                _P(
                    stdout="**Current next action (post-#55).** something else.\n\n"
                    "| PR #55 | 2026-08-22 | pointer body here. |\n"
                ),
            ),
        ],
        calls,
    )
    # r14 P2: an unrepresented same-PR draft REFUSES the resume (it survives)
    with pytest.raises(SystemExit, match="does not represent the authored"):
        rsr.emit_refresh_pr(55, run=run)
    assert draft.exists()


def test_emit_refresh_pr_resume_paths_refuse_unappliable_flags(monkeypatch):
    """r10 P2 (supersedes the r7 warn-and-continue): a resume cannot apply supplied
    flags — both resume paths REFUSE instead of silently landing the old pointer."""
    # pushed-branch path
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=0)),
        ],
        calls,
    )
    with pytest.raises(SystemExit, match="cannot be applied"):
        rsr.emit_refresh_pr(55, next_action="late pointer", run=run, do_refresh=lambda: None)
    assert not any(c[:3] == ["gh", "pr", "create"] for c in calls)
    # existing-open-PR path
    calls2: list[list[str]] = []
    run2 = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            )
        ],
        calls2,
    )
    with pytest.raises(SystemExit, match="cannot be applied"):
        rsr.emit_refresh_pr(55, notes="late notes", run=run2, do_refresh=lambda: None)


def test_cli_emit_mode_refuses_dry_run(capsys):
    """r11 P2: the emitter mutates (checkout/commit/push/PR) — --dry-run refuses."""
    rc = rsr.main(["--emit-refresh-pr-json", "55", "--dry-run"])
    assert rc == 2
    assert "cannot be combined with --dry-run" in capsys.readouterr().err
    # r18 P2: every other operation selector refuses too
    rc = rsr.main(["--emit-refresh-pr-json", "55", "--check"])
    assert rc == 2
    assert "cannot be combined with --check" in capsys.readouterr().err


def test_emit_refresh_pr_stale_label_pointer_is_not_representation(monkeypatch, tmp_path):
    """r11 P2: a pushed pointer labeled post-#54 whose body equals the post-#55 draft
    is NOT installation of this landing's pointer — the draft survives."""
    monkeypatch.setattr(rsr, "main", lambda argv: 0)
    draft = tmp_path / "draft"
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    draft.write_text("post-pr: 55\npointer body here.\n")
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (
                ("gh", "pr", "list"),
                _P(stdout="321\tabc123def\tmain\tfalse\tops: roadmap status refresh post-#55"),
            ),
            (
                ("git", "show"),
                _P(stdout="**Current next action (post-#54).** pointer body here."),
            ),
        ],
        calls,
    )
    # r14 P2: the stale-label pointer leaves the draft unrepresented -> refuse
    with pytest.raises(SystemExit, match="does not represent the authored"):
        rsr.emit_refresh_pr(55, run=run)
    assert draft.exists()


def test_emit_refresh_pr_pushed_branch_provenance_refusal():
    """r12 P2: a pre-pushed same-name branch NOT descending directly from the
    just-merged main tip is never wrapped in the trusted refresh PR."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=0)),
            (("git", "rev-parse", "origin/roadmap-refresh-post-55^"), _P(stdout="a" * 40)),
            (("git", "rev-parse", "origin/main"), _P(stdout="b" * 40)),
        ],
        calls,
    )
    with pytest.raises(SystemExit, match="does not descend directly"):
        rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert not any(c[:3] == ["gh", "pr", "create"] for c in calls)


def test_emit_refresh_pr_pushed_branch_provenance_pass():
    """The genuine crash-recovery branch (parent == main tip) proceeds to PR creation."""
    calls: list[list[str]] = []
    run = _scripted_run(
        [
            (("gh", "pr", "list"), _P(stdout="")),
            (("git", "ls-remote"), _P(returncode=0)),
            (("git", "rev-parse", "origin/roadmap-refresh-post-55^"), _P(stdout="m" * 40)),
            (("git", "rev-parse", "origin/main"), _P(stdout="m" * 40)),
            (("gh", "pr", "create"), _P(stdout="https://github.com/o/r/pull/77")),
            (("git", "rev-parse", "HEAD"), _P(stdout="feedbeef")),
        ],
        calls,
    )
    out = rsr.emit_refresh_pr(55, run=run, do_refresh=lambda: None)
    assert out["pr"] == 77


def test_emit_refresh_pr_refuses_symlinked_draft(monkeypatch, tmp_path):
    """r13 P1: a planted symlink at the draft path must never leak an outside file
    into the refresh PR body or the committed pointer — refused no-follow, left."""
    argv_seen: dict[str, list[str]] = {}
    monkeypatch.setattr(rsr, "main", lambda argv: (argv_seen.setdefault("argv", argv) and 0) or 0)
    outside = tmp_path / "outside.txt"
    outside.write_text("post-pr: 55\nexfiltrated content\n")
    draft = tmp_path / "draft"
    draft.symlink_to(outside)
    monkeypatch.setattr(rsr, "NEXT_ACTION_DRAFT", draft)
    calls: list[list[str]] = []
    rsr.emit_refresh_pr(55, run=_scripted_run(_fresh_path_script(), calls))
    assert "--next-action" not in argv_seen["argv"]
    assert draft.is_symlink()  # left in place
    create = next(c for c in calls if c[:3] == ["gh", "pr", "create"])
    assert "exfiltrated" not in create[create.index("--body") + 1]

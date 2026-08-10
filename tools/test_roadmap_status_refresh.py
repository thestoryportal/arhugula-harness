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
    hard = [v for v in violations if "informational" not in v]
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

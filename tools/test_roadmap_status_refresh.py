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

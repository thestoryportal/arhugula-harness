"""Witnesses for the deterministic parsing rules behind `/prime`.

Each test pins a rule whose violation would silently corrupt the report rather than
fail it -- a misparsed PR reference, a lexical id sort, or a session boundary that
swallows a gap. The `row_pr` cases are regression witnesses: an earlier draft took the
max of every digit run in the field and read `2026` out of a bare date, which silently
dropped real closures out of the throughput window.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prime_report

# ------------------------------------------------------------------ row_pr


def test_row_pr_ignores_bare_dates_and_takes_the_highest_hash_reference() -> None:
    """The regression: `2026-08-05` must not out-rank a real `#1241`."""
    item = {
        "pr": (
            "#1224 (the combined fork filing) + #1233 (the 2026-08-05 ratification "
            "record) + #1241 (the build leg — CLOSES this row)"
        )
    }
    assert prime_report.row_pr(item) == 1241


def test_row_pr_is_none_when_the_field_cites_no_pr() -> None:
    """An operator ratification with no PR must be unmapped, never imputed."""
    item = {"pr": "ratified-2026-07-21 (operator AUQ: MTC-only scoping ratified as-is)"}
    assert prime_report.row_pr(item) is None


def test_row_pr_is_none_when_the_field_is_absent() -> None:
    assert prime_report.row_pr({}) is None


def test_row_pr_reads_a_single_plain_reference() -> None:
    assert prime_report.row_pr({"pr": "#994"}) == 994


# ------------------------------------------------- pr_merge_timestamps


def test_pr_timestamps_only_match_a_trailing_squash_reference() -> None:
    """A `#N` in the middle of a subject is a mention, not the merge of that PR."""
    commits = [
        prime_report.Commit("a" * 40, 300, "fix(od): B-164 — the late-arrival path (#1336)"),
        prime_report.Commit("b" * 40, 200, "ops: roadmap status refresh post-#1350"),
    ]
    stamps = prime_report.pr_merge_timestamps(commits)
    assert stamps == {1336: 300}


def test_pr_timestamps_keep_the_newest_commit_for_a_repeated_reference() -> None:
    commits = [
        prime_report.Commit("a" * 40, 900, "revert: something (#42)"),
        prime_report.Commit("b" * 40, 100, "feat: original (#42)"),
    ]
    assert prime_report.pr_merge_timestamps(commits)[42] == 900


# --------------------------------------------------------------- id_key


def test_id_key_sorts_numerically_not_lexically() -> None:
    """Lexical order would put B-104 before B-16 and scramble the whole listing."""
    ordered = sorted(["B-104", "B-16", "B-2", "B-30"], key=prime_report.id_key)
    assert ordered == ["B-2", "B-16", "B-30", "B-104"]


def test_id_key_separates_distinct_prefixes() -> None:
    ordered = sorted(["R-1", "B-16"], key=prime_report.id_key)
    assert ordered == ["B-16", "R-1"]


def test_id_key_tolerates_an_unparseable_id() -> None:
    assert prime_report.id_key("weird") == ("weird", 0)


# ------------------------------------------------- cluster_sessions


def _commit(ts: int) -> prime_report.Commit:
    return prime_report.Commit(f"{ts:040d}", ts, f"subject {ts}")


def test_cluster_sessions_splits_on_a_gap_wider_than_the_threshold() -> None:
    hour = 3600
    commits = [_commit(100 * hour), _commit(99 * hour), _commit(50 * hour)]
    sessions = prime_report.cluster_sessions(commits, gap_hours=5.0)
    assert [len(s) for s in sessions] == [2, 1]


def test_cluster_sessions_keeps_one_session_when_every_gap_is_under_threshold() -> None:
    hour = 3600
    commits = [_commit(100 * hour), _commit(98 * hour), _commit(96 * hour)]
    assert len(prime_report.cluster_sessions(commits, gap_hours=5.0)) == 1


def test_cluster_sessions_treats_a_gap_exactly_at_threshold_as_same_session() -> None:
    """The split is strictly greater-than, so the boundary is not off by one."""
    hour = 3600
    commits = [_commit(10 * hour), _commit(5 * hour)]
    assert len(prime_report.cluster_sessions(commits, gap_hours=5.0)) == 1


def test_cluster_sessions_handles_a_single_commit() -> None:
    assert prime_report.cluster_sessions([_commit(42)], gap_hours=5.0) == [[_commit(42)]]


# ----------------------------------------------------------------- brief


def test_brief_collapses_whitespace_and_leaves_short_text_intact() -> None:
    assert prime_report.brief("a  b\n c", width=40) == "a b c"


def test_brief_truncates_at_a_word_boundary_with_an_ellipsis() -> None:
    out = prime_report.brief("alpha beta gamma delta epsilon", width=20)
    assert out.endswith("…")
    assert " " not in out[-2:]  # no dangling space before the ellipsis
    assert len(out) <= 21


def test_brief_accepts_a_non_string_without_raising() -> None:
    assert prime_report.brief(1234, width=40) == "1234"


# -------------------------------------------------------------- fmt_span


def test_fmt_span_uses_minutes_below_the_hour_threshold() -> None:
    assert prime_report.fmt_span(45) == "45m"


def test_fmt_span_switches_to_hours_for_long_spans() -> None:
    assert prime_report.fmt_span(120) == "2.0h"


def test_fmt_span_drops_the_decimal_for_very_long_spans() -> None:
    assert prime_report.fmt_span(6000) == "100h"


# ------------------------------------------------------------ fail-loud


def test_run_raises_unavailable_rather_than_returning_empty_on_failure() -> None:
    """A command that fails must never be mistaken for a command that found nothing."""
    try:
        prime_report.run("git", "cat-file", "-e", "definitely-not-a-ref")
    except prime_report.UnavailableError as exc:
        assert "git cat-file" in str(exc)
    else:
        raise AssertionError("expected UnavailableError")


def test_run_can_return_output_from_a_nonzero_exit_when_check_is_disabled() -> None:
    """The context guard exits non-zero as a verdict; its stdout is still the answer."""
    out = prime_report.run("git", "cat-file", "-e", "nope", check=False)
    assert out == ""


def test_load_register_raises_unavailable_on_a_shape_it_cannot_read() -> None:
    try:
        prime_report.load_register("just: a scalar", "synthetic")
    except prime_report.UnavailableError as exc:
        assert "synthetic" in str(exc)
    else:
        raise AssertionError("expected UnavailableError")

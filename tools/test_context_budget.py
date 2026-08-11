"""Tests for tools/context_budget.py — the R-CTX-1 first-turn context-budget
instrument, including the errata E4 post-compaction selector
(``post_compaction_first_turns``) that register row B-148's close_out gates on
being TESTED before the program can close.

Every numbered witness below traces to a codex review finding on PR #1294
(regression protection is the point, not novel coverage). End-to-end tests of
``main()`` / ``collect_all()`` use the ``td`` fixture, which MONKEYPATCHES the
home directory to a per-test ``tmp_path`` (codex P2 on this PR: writing under
the operator's real ``~/.claude/projects`` both touched real data and
PermissionError'd under managed sandbox profiles) and then exercises the
tool's real ``project_transcript_dir`` derivation against that fake home.
Pure functions that take an arbitrary ``Path`` (``first_turn_total``,
``post_compaction_first_turns``, ``sidechain_first_turns``, ``collect_all``)
are exercised directly against plain ``tmp_path`` fixtures. pytest's tmp_path
lifecycle owns all cleanup — nothing outside the test tree is ever written.

Mutation-probe map (what regresses silently if each witness is removed):

- test_post_compaction_two_boundaries_two_rows:
  merging/dropping per-boundary rows; trigger not threaded from its boundary
- test_post_compaction_consecutive_boundaries_only_latest:
  pending_trigger not reset/overwritten on a second boundary
- test_post_compaction_only_first_turn_per_boundary_captured:
  merging per-boundary rows — deleting the pending_trigger reset (one row
  per boundary is the selector's core invariant; every other fixture has
  exactly one capturable record per boundary, so only this one catches it)
- test_post_compaction_dedup_within_request:
  removing the seen_request_ids dedup in the E4 selector
- test_post_compaction_zero_usage_skip_then_real_usage:
  marking a zero-usage requestId "seen" (drops the real chunk that follows)
- test_post_compaction_non_sidechain_filter:
  dropping the isSidechain guard in the E4 selector
- test_post_compaction_no_boundary_returns_empty:
  scanning for assistant records even with no boundary seen
- test_post_compaction_missing_trigger_metadata_defaults_unknown:
  KeyError / crash instead of the "unknown" fallback
- test_headline_cli_only_by_rule_not_plurality:
  eligibility computed by majority cohort instead of the fixed /cli rule
- test_sdk_dominated_corpus_refuses_undersized_headline:
  silently undersizing the headline instead of refusing (exit 1)
- test_sessions_must_be_at_least_one / _negative:
  removing the _positive_int floor (0/negative silently accepted)
- test_first_turn_zero_usage_not_marked_seen_later_chunk_selected:
  marking a zero-usage requestId seen in first_turn_total
- test_first_turn_malformed_non_tail_line_raises:
  swallowing a malformed non-tail line instead of failing closed
- test_first_turn_unterminated_trailing_fragment_tolerated:
  over-eagerly raising on a benign in-progress (unterminated) tail fragment
- test_first_turn_newline_terminated_malformed_tail_fails_closed:
  tolerating a COMPLETED (newline-terminated) corrupt final record
- test_collect_all_ranks_by_first_turn_timestamp_not_mtime:
  ranking by file mtime instead of the row's own first-turn timestamp
- test_post_compaction_excludes_ineligible_sdk_sessions_boundary:
  scanning ineligible (non-cli) session files for post-compaction events
- test_post_compaction_event_time_windowed_not_parent_first_turn:
  windowing by parent session's first-turn time instead of the event's own
- test_sidechains_excluded_for_ineligible_sdk_parent_session:
  scanning an ineligible session's subagents directory
- test_sidechain_first_turns_one_per_agent_file:
  dropping a sibling agent file from the per-agent enumeration
- test_sidechain_first_turns_only_first_real_call_per_agent_file:
  reading past the first real call in one agent file (missing break)
- test_summary_mean_is_exact_float_not_truncated:
  int() truncation instead of float() on the mean/median
- test_main_unreadable_transcript_file_aborts_cleanly:
  an uncaught OSError propagating out of main() instead of exit 1
- test_main_malformed_transcript_aborts_cleanly:
  MalformedTranscriptError missing from main()'s except tuples
- test_main_unicode_decode_error_from_torn_multibyte_tail:
  UnicodeDecodeError not in main()'s except tuple
- test_project_transcript_dir_derives_real_home_slug:
  slug derivation (/ -> -) drifting from the real transcript path
"""

from __future__ import annotations

import json
import math
import os
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import context_budget
import pytest

# --------------------------------------------------------------------------
# Record builders
# --------------------------------------------------------------------------


def _rec(
    *,
    request_id: str | None,
    timestamp: str,
    input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
    is_sidechain: bool = False,
    session_kind: str | None = None,
    entrypoint: str | None = "cli",
    rec_type: str = "assistant",
) -> dict[str, Any]:
    """One transcript-line-shaped assistant (or other) record."""
    rec: dict[str, Any] = {
        "type": rec_type,
        "timestamp": timestamp,
        "requestId": request_id,
        "message": {
            "usage": {
                "input_tokens": input_tokens,
                "cache_creation_input_tokens": cache_creation_input_tokens,
                "cache_read_input_tokens": cache_read_input_tokens,
            }
        },
    }
    if is_sidechain:
        rec["isSidechain"] = True
    if session_kind is not None:
        rec["sessionKind"] = session_kind
    if entrypoint is not None:
        rec["entrypoint"] = entrypoint
    return rec


def _compact(trigger: str = "manual") -> dict[str, Any]:
    return {
        "type": "system",
        "subtype": "compact_boundary",
        "compactMetadata": {"trigger": trigger},
    }


def _write_jsonl(path: Path, records: list[dict[str, Any] | str]) -> None:
    """Write one JSONL transcript file; a raw ``str`` entry is injected verbatim
    (used to plant a malformed line)."""
    lines = [r if isinstance(r, str) else json.dumps(r) for r in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Fixture: real derived transcript directory (for main()/collect_all() e2e)
# --------------------------------------------------------------------------


@pytest.fixture
def td(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[Path, Path]]:
    """A (project_dir, transcript_dir) pair with HOME redirected to tmp_path
    (codex P2: writing into the REAL ``~/.claude/projects`` both touched
    operator data and PermissionError'd under the managed workspace-write
    profile). ``project_transcript_dir`` derives from ``Path.home()``, so the
    monkeypatched HOME keeps every fixture inside the writable test tree;
    pytest's tmp_path lifecycle owns cleanup.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    def _fake_home() -> Path:
        return fake_home

    monkeypatch.setattr(Path, "home", staticmethod(_fake_home))
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    transcript_dir = context_budget.project_transcript_dir(project_dir)
    transcript_dir.mkdir(parents=True)
    yield project_dir, transcript_dir


# --------------------------------------------------------------------------
# project_transcript_dir — slug derivation
# --------------------------------------------------------------------------


def test_project_transcript_dir_derives_real_home_slug(tmp_path: Path) -> None:
    project_dir = tmp_path / "myproj"
    project_dir.mkdir()
    expected = Path.home() / ".claude" / "projects" / str(project_dir.resolve()).replace("/", "-")
    assert context_budget.project_transcript_dir(project_dir) == expected


# --------------------------------------------------------------------------
# 1. post_compaction_first_turns — the E4 selector
# --------------------------------------------------------------------------


def test_post_compaction_two_boundaries_two_rows_with_triggers(tmp_path: Path) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _rec(request_id="r0", timestamp="2026-08-10T09:00:00Z", input_tokens=100),
            _compact("manual"),
            _rec(request_id="r1", timestamp="2026-08-10T09:05:00Z", input_tokens=200),
            _compact("auto"),
            _rec(request_id="r2", timestamp="2026-08-10T09:10:00Z", input_tokens=300),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert [r["trigger"] for r in rows] == ["manual", "auto"]
    assert [r["post_compaction_total"] for r in rows] == [200, 300]


def test_post_compaction_consecutive_boundaries_only_latest_trigger_counts(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _compact("manual"),
            _compact("auto"),
            _rec(request_id="r1", timestamp="t1", input_tokens=77),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert len(rows) == 1
    assert rows[0]["trigger"] == "auto"


def test_post_compaction_only_first_turn_per_boundary_captured(tmp_path: Path) -> None:
    # merge-gate lens 3 (PR #1297): every earlier fixture had exactly ONE
    # capturable record per boundary, so deleting the `pending_trigger = None`
    # reset — the selector's one-row-per-boundary invariant — survived the
    # entire suite. Here a boundary is followed by TWO distinct capturable
    # records; only the FIRST may yield a row.
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _compact("manual"),
            _rec(request_id="ra", timestamp="t1", input_tokens=111),
            _rec(request_id="rb", timestamp="t2", input_tokens=222),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert [r["post_compaction_total"] for r in rows] == [111]


def test_post_compaction_dedup_within_request(tmp_path: Path) -> None:
    # codex P2 (vacuous-probe repair): the repeated requestId sits AFTER a
    # SECOND boundary, so `pending_trigger` is armed again and dedup is the
    # ONLY reason the duplicate is skipped — removing `seen_request_ids`
    # would capture r1's 999-token chunk for boundary 2 and fail both
    # assertions below.
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _compact("manual"),
            _rec(request_id="r1", timestamp="t1", input_tokens=100),
            _compact("auto"),
            _rec(request_id="r1", timestamp="t1b", input_tokens=999),
            _rec(request_id="r2", timestamp="t2", input_tokens=200),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert [r["post_compaction_total"] for r in rows] == [100, 200]
    assert [r["trigger"] for r in rows] == ["manual", "auto"]


def test_post_compaction_zero_usage_skip_then_real_usage_same_request(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _compact("manual"),
            _rec(request_id="r1", timestamp="t1", input_tokens=0),
            _rec(request_id="r1", timestamp="t2", input_tokens=150),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert len(rows) == 1
    assert rows[0]["post_compaction_total"] == 150


def test_post_compaction_non_sidechain_filter(tmp_path: Path) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _compact("manual"),
            _rec(request_id="r-side", timestamp="t1", input_tokens=500, is_sidechain=True),
            _rec(request_id="r-main", timestamp="t2", input_tokens=250),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert len(rows) == 1
    assert rows[0]["post_compaction_total"] == 250
    assert rows[0]["request_id"] == "r-main"


def test_post_compaction_no_boundary_returns_empty(tmp_path: Path) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(path, [_rec(request_id="r1", timestamp="t1", input_tokens=100)])
    assert context_budget.post_compaction_first_turns(path) == []


def test_post_compaction_missing_trigger_metadata_defaults_unknown(tmp_path: Path) -> None:
    # Both absence shapes (merge-gate lens 3): compactMetadata missing entirely
    # (non-dict branch) AND present-but-trigger-keyless (dict .get default).
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            {"type": "system", "subtype": "compact_boundary"},
            _rec(request_id="r1", timestamp="t1", input_tokens=100),
            {"type": "system", "subtype": "compact_boundary", "compactMetadata": {}},
            _rec(request_id="r2", timestamp="t2", input_tokens=200),
        ],
    )
    rows = context_budget.post_compaction_first_turns(path)
    assert [r["trigger"] for r in rows] == ["unknown", "unknown"]


# --------------------------------------------------------------------------
# 2. Cohort eligibility — headline is 'cli' entrypoint ONLY, by rule
# --------------------------------------------------------------------------


def test_headline_cli_only_by_rule_not_plurality(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    # ONE cli session (fewer) outnumbered by THREE sdk sessions (more) — cli
    # must still win the headline, because eligibility is a RULE (entrypoint
    # == 'cli'), never "whichever cohort has more sessions".
    _write_jsonl(
        transcript_dir / "cli1.jsonl",
        [
            _rec(
                request_id="c1",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=500,
                entrypoint="cli",
            )
        ],
    )
    for i in range(3):
        _write_jsonl(
            transcript_dir / f"sdk{i}.jsonl",
            [
                _rec(
                    request_id=f"s{i}",
                    timestamp=f"2026-08-10T08:0{i}:00Z",
                    input_tokens=999,
                    entrypoint="sdk-cli",
                )
            ],
        )
    rc = context_budget.main(["--project-dir", str(project_dir), "--sessions", "1", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["summary"]["headline_sessions"] == 1
    assert payload["summary"]["headline_cohort"] == "*/cli"
    assert payload["sessions"][0]["first_turn_total"] == 500


def test_sdk_dominated_corpus_refuses_undersized_headline(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    _write_jsonl(
        transcript_dir / "cli1.jsonl",
        [
            _rec(
                request_id="c1",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=500,
                entrypoint="cli",
            )
        ],
    )
    for i in range(3):
        _write_jsonl(
            transcript_dir / f"sdk{i}.jsonl",
            [
                _rec(
                    request_id=f"s{i}",
                    timestamp=f"2026-08-10T08:0{i}:00Z",
                    input_tokens=999,
                    entrypoint="sdk-cli",
                )
            ],
        )
    rc = context_budget.main(["--project-dir", str(project_dir), "--sessions", "2", "--json"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "only 1 eligible" in err
    assert "Refusing to compute an undersized headline" in err


def test_sessions_must_be_at_least_one_argparse_rejects(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        context_budget.main(["--sessions", "0"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "must be >= 1" in err


def test_sessions_negative_argparse_rejects(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        context_budget.main(["--sessions", "-1"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "must be >= 1" in err


# --------------------------------------------------------------------------
# 3. First-turn selection
# --------------------------------------------------------------------------


def test_first_turn_zero_usage_not_marked_seen_later_chunk_selected(tmp_path: Path) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            _rec(request_id="r1", timestamp="t0", input_tokens=0),
            _rec(request_id="r1", timestamp="t1", input_tokens=321),
        ],
    )
    row = context_budget.first_turn_total(path)
    assert row is not None
    assert row["first_turn_total"] == 321
    assert row["request_id"] == "r1"


def test_first_turn_malformed_non_tail_line_raises(tmp_path: Path) -> None:
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            json.dumps(_rec(request_id="r1", timestamp="t0", input_tokens=10)),
            "{not valid json",
            json.dumps(_rec(request_id="r2", timestamp="t1", input_tokens=20)),
        ],
    )
    with pytest.raises(context_budget.MalformedTranscriptError):
        context_budget.first_turn_total(path)


def test_first_turn_unterminated_trailing_fragment_tolerated(tmp_path: Path) -> None:
    # codex round-3: the benign shape is an UNTERMINATED final fragment — the
    # write is in progress, so no trailing newline exists yet. (_write_jsonl
    # always appends one, so this fixture writes manually.)
    path = tmp_path / "sess1.jsonl"
    good = json.dumps(_rec(request_id="r1", timestamp="t0", input_tokens=10))
    path.write_text(good + "\n{still writing...", encoding="utf-8")
    row = context_budget.first_turn_total(path)
    assert row is not None
    assert row["first_turn_total"] == 10


def test_first_turn_newline_terminated_malformed_tail_fails_closed(tmp_path: Path) -> None:
    # codex round-3: a NEWLINE-TERMINATED malformed final record was COMPLETED
    # by its writer — real corruption, not an append in progress. Tolerating
    # it returned a plausible metric for a corrupt transcript.
    path = tmp_path / "sess1.jsonl"
    _write_jsonl(
        path,
        [
            json.dumps(_rec(request_id="r1", timestamp="t0", input_tokens=10)),
            "{completed corrupt record",
        ],
    )
    with pytest.raises(context_budget.MalformedTranscriptError, match="newline-terminated"):
        context_budget.first_turn_total(path)


# --------------------------------------------------------------------------
# 4. Ranking by first-turn timestamp, not mtime
# --------------------------------------------------------------------------


def test_collect_all_ranks_by_first_turn_timestamp_not_mtime(tmp_path: Path) -> None:
    directory = tmp_path / "transcripts"
    directory.mkdir()
    newer_ts_path = directory / "sess_newer_ts.jsonl"
    older_ts_path = directory / "sess_older_ts.jsonl"
    _write_jsonl(
        newer_ts_path, [_rec(request_id="a", timestamp="2026-08-10T12:00:00Z", input_tokens=111)]
    )
    _write_jsonl(
        older_ts_path, [_rec(request_id="b", timestamp="2026-08-01T12:00:00Z", input_tokens=222)]
    )
    # Invert mtimes relative to timestamp order: the OLDER-timestamped file
    # gets touched LAST (newest mtime), the NEWER-timestamped file gets an
    # older mtime.
    old_mtime = time.time() - 10_000
    new_mtime = time.time()
    os.utime(newer_ts_path, (old_mtime, old_mtime))
    os.utime(older_ts_path, (new_mtime, new_mtime))
    rows = context_budget.collect_all(directory)
    assert [r["session"] for r in rows] == ["sess_newer_ts", "sess_older_ts"]


# --------------------------------------------------------------------------
# 5. Deep views: cohort-filtered + event-time-windowed to the headline span
# --------------------------------------------------------------------------


def test_post_compaction_excludes_ineligible_sdk_sessions_boundary(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    _write_jsonl(
        transcript_dir / "cli1.jsonl",
        [
            _rec(
                request_id="c1",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=500,
                entrypoint="cli",
            )
        ],
    )
    _write_jsonl(
        transcript_dir / "sdk1.jsonl",
        [
            _rec(
                request_id="s0",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=400,
                entrypoint="sdk-cli",
            ),
            _compact("manual"),
            _rec(
                request_id="s1",
                timestamp="2026-08-10T09:05:00Z",
                input_tokens=600,
                entrypoint="sdk-cli",
            ),
        ],
    )
    rc = context_budget.main(
        ["--project-dir", str(project_dir), "--sessions", "1", "--json", "--post-compaction"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["post_compaction"] == []
    assert payload["summary"]["post_compaction_measured"] == 0


def test_post_compaction_event_time_windowed_not_parent_first_turn(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    newest = transcript_dir / "cli_newest.jsonl"
    old_with_fresh_boundary = transcript_dir / "cli_old_fresh_boundary.jsonl"
    old_with_stale_boundary = transcript_dir / "cli_old_stale_boundary.jsonl"

    # --sessions 1: the headline window is defined by THIS session's own
    # first-turn timestamp alone.
    _write_jsonl(
        newest,
        [
            _rec(
                request_id="n1",
                timestamp="2026-08-10T12:00:00Z",
                input_tokens=700,
                entrypoint="cli",
            )
        ],
    )

    # This session's OWN first turn is old (never makes the top-1 headline),
    # but its compaction event's OWN timestamp falls inside the window
    # (>= window_start) — the row MUST be included: windowing is by the
    # event's own timestamp, not by whether its parent session is headline.
    _write_jsonl(
        old_with_fresh_boundary,
        [
            _rec(
                request_id="o1", timestamp="2026-08-01T00:00:00Z", input_tokens=50, entrypoint="cli"
            ),
            _compact("manual"),
            _rec(
                request_id="o2",
                timestamp="2026-08-10T12:30:00Z",
                input_tokens=800,
                entrypoint="cli",
            ),
        ],
    )

    # This session's compaction event is entirely BEFORE the window — the
    # row MUST be excluded.
    _write_jsonl(
        old_with_stale_boundary,
        [
            _rec(
                request_id="p1", timestamp="2026-08-01T00:00:00Z", input_tokens=50, entrypoint="cli"
            ),
            _compact("auto"),
            _rec(
                request_id="p2",
                timestamp="2026-08-01T01:00:00Z",
                input_tokens=900,
                entrypoint="cli",
            ),
        ],
    )

    rc = context_budget.main(
        ["--project-dir", str(project_dir), "--sessions", "1", "--json", "--post-compaction"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    totals = {row["post_compaction_total"] for row in payload["post_compaction"]}
    assert 800 in totals
    assert 900 not in totals


def test_sidechains_excluded_for_ineligible_sdk_parent_session(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    _write_jsonl(
        transcript_dir / "cli1.jsonl",
        [
            _rec(
                request_id="c1",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=500,
                entrypoint="cli",
            )
        ],
    )
    _write_jsonl(
        transcript_dir / "sdk1.jsonl",
        [
            _rec(
                request_id="s1",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=400,
                entrypoint="sdk-cli",
            )
        ],
    )
    subagents_dir = transcript_dir / "sdk1" / "subagents"
    subagents_dir.mkdir(parents=True)
    _write_jsonl(
        subagents_dir / "agent-x.jsonl",
        [_rec(request_id="ax", timestamp="2026-08-10T09:01:00Z", input_tokens=1234)],
    )
    rc = context_budget.main(
        ["--project-dir", str(project_dir), "--sessions", "1", "--json", "--sidechains"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["sidechains"] == []


def test_sidechain_rows_reach_main_json_for_eligible_parent(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    # codex round-2: the negative case alone let the whole
    # `side_rows.extend(...)` wiring be deleted with the suite green — this
    # positive round trip pins that an ELIGIBLE parent's subagent rows reach
    # the JSON entry point with the right totals AND that all three USAGE
    # fields (incl. both cache components) are summed.
    project_dir, transcript_dir = td
    _write_jsonl(
        transcript_dir / "cli9.jsonl",
        [
            _rec(
                request_id="c9",
                timestamp="2026-08-10T09:00:00Z",
                input_tokens=100,
                cache_creation_input_tokens=70000,
                cache_read_input_tokens=23000,
                entrypoint="cli",
            )
        ],
    )
    subagents_dir = transcript_dir / "cli9" / "subagents"
    subagents_dir.mkdir(parents=True)
    _write_jsonl(
        subagents_dir / "agent-a.jsonl",
        [
            _rec(
                request_id="sa1",
                timestamp="2026-08-10T09:01:00Z",
                input_tokens=5,
                cache_creation_input_tokens=60000,
                cache_read_input_tokens=15000,
            )
        ],
    )
    rc = context_budget.main(
        ["--project-dir", str(project_dir), "--sessions", "1", "--json", "--sidechains"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert [r["sidechain_total"] for r in payload["sidechains"]] == [75005]
    assert payload["summary"]["sidechain_first_turns_measured"] == 1
    # headline itself must sum input + BOTH cache components (kills a
    # USAGE_FIELDS shrink): 100 + 70000 + 23000
    assert payload["sessions"][0]["first_turn_total"] == 93100


def test_post_compaction_summary_aggregates_are_exact(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    # codex round-2: rows existed but the AGGREGATES were never asserted —
    # post_compaction_mean could be hardcoded 0.0 with the suite green.
    # Three distinct events with cache components: totals 1000, 2000, 4000
    # → median 2000.0, mean 7000/3 (exact float, not truncated).
    project_dir, transcript_dir = td
    _write_jsonl(
        transcript_dir / "cli7.jsonl",
        [
            _rec(
                request_id="h1", timestamp="2026-08-10T08:00:00Z", input_tokens=50, entrypoint="cli"
            ),
            _compact("manual"),
            _rec(
                request_id="e1",
                timestamp="2026-08-10T08:10:00Z",
                input_tokens=200,
                cache_creation_input_tokens=500,
                cache_read_input_tokens=300,
                entrypoint="cli",
            ),
            _compact("auto"),
            _rec(
                request_id="e2",
                timestamp="2026-08-10T08:20:00Z",
                input_tokens=1000,
                cache_creation_input_tokens=600,
                cache_read_input_tokens=400,
                entrypoint="cli",
            ),
            _compact("auto"),
            _rec(
                request_id="e3",
                timestamp="2026-08-10T08:30:00Z",
                input_tokens=3000,
                cache_creation_input_tokens=700,
                cache_read_input_tokens=300,
                entrypoint="cli",
            ),
        ],
    )
    rc = context_budget.main(
        ["--project-dir", str(project_dir), "--sessions", "1", "--json", "--post-compaction"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert [r["post_compaction_total"] for r in payload["post_compaction"]] == [4000, 2000, 1000]
    assert payload["summary"]["post_compaction_measured"] == 3
    assert payload["summary"]["post_compaction_median"] == 2000.0
    assert math.isclose(payload["summary"]["post_compaction_mean"], 7000 / 3)


# --------------------------------------------------------------------------
# 6. Sidechains — one first-turn row per subagent file
# --------------------------------------------------------------------------


def test_sidechain_first_turns_one_per_agent_file(tmp_path: Path) -> None:
    parent_dir = tmp_path / "sessions"
    parent_dir.mkdir()
    session_path = parent_dir / "sess1.jsonl"
    subagents_dir = parent_dir / "sess1" / "subagents"
    subagents_dir.mkdir(parents=True)
    _write_jsonl(
        subagents_dir / "agent-1.jsonl", [_rec(request_id="a1", timestamp="t1", input_tokens=111)]
    )
    _write_jsonl(
        subagents_dir / "agent-2.jsonl", [_rec(request_id="a2", timestamp="t2", input_tokens=222)]
    )
    rows = context_budget.sidechain_first_turns(session_path)
    assert {r["agent"] for r in rows} == {"agent-1", "agent-2"}
    assert {r["sidechain_total"] for r in rows} == {111, 222}


def test_sidechain_first_turns_only_first_real_call_per_agent_file(tmp_path: Path) -> None:
    parent_dir = tmp_path / "sessions"
    parent_dir.mkdir()
    session_path = parent_dir / "sess1.jsonl"
    subagents_dir = parent_dir / "sess1" / "subagents"
    subagents_dir.mkdir(parents=True)
    _write_jsonl(
        subagents_dir / "agent-1.jsonl",
        [
            _rec(request_id="a1", timestamp="t1", input_tokens=0),  # zero-usage: skipped
            _rec(request_id="a1", timestamp="t2", input_tokens=111),  # first real call
            _rec(request_id="a2", timestamp="t3", input_tokens=999),  # a LATER call: NOT counted
        ],
    )
    rows = context_budget.sidechain_first_turns(session_path)
    assert len(rows) == 1
    assert rows[0]["sidechain_total"] == 111


def test_sidechain_first_turns_no_subagents_dir_returns_empty(tmp_path: Path) -> None:
    session_path = tmp_path / "sess1.jsonl"
    assert context_budget.sidechain_first_turns(session_path) == []


# --------------------------------------------------------------------------
# 7. Summary medians/means are exact
# --------------------------------------------------------------------------


def test_summary_mean_is_exact_float_not_truncated(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    totals = [100, 100, 101]  # mean = 100.333... — NOT integer-valued
    for i, total in enumerate(totals):
        _write_jsonl(
            transcript_dir / f"cli{i}.jsonl",
            [
                _rec(
                    request_id=f"r{i}",
                    timestamp=f"2026-08-10T09:0{i}:00Z",
                    input_tokens=total,
                    entrypoint="cli",
                )
            ],
        )
    rc = context_budget.main(["--project-dir", str(project_dir), "--sessions", "3", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    expected_mean = sum(totals) / len(totals)
    mean_first_turn = payload["summary"]["mean_first_turn"]
    assert isinstance(mean_first_turn, float)
    assert math.isclose(mean_first_turn, expected_mean)
    # The regression this guards: silently narrowing to int() would read
    # 100.333... as 100 — assert the two disagree.
    assert mean_first_turn != int(expected_mean)
    assert payload["summary"]["median_first_turn"] == 100.0
    assert isinstance(payload["summary"]["median_first_turn"], float)


# --------------------------------------------------------------------------
# 8. Fail-closed aborts: unreadable file / torn multibyte tail
# --------------------------------------------------------------------------


def test_main_unreadable_transcript_file_aborts_cleanly(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("running as root; permission bits are not enforced")
    project_dir, transcript_dir = td
    path = transcript_dir / "broken.jsonl"
    _write_jsonl(path, [_rec(request_id="r1", timestamp="t1", input_tokens=100, entrypoint="cli")])
    path.chmod(0o000)
    try:
        # main() must return 1 cleanly — if OSError escaped uncaught, this
        # call itself would raise and the test would error rather than pass.
        rc = context_budget.main(["--project-dir", str(project_dir), "--sessions", "1", "--json"])
    finally:
        path.chmod(0o644)  # restore so the td fixture's rmtree can remove it
    err = capsys.readouterr().err
    assert rc == 1
    assert "unreadable transcript" in err


def test_main_unicode_decode_error_from_torn_multibyte_tail_aborts_cleanly(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, transcript_dir = td
    path = transcript_dir / "torn.jsonl"
    good_line = json.dumps(
        _rec(request_id="r1", timestamp="t1", input_tokens=100, entrypoint="cli")
    )
    with path.open("wb") as fh:
        fh.write((good_line + "\n").encode("utf-8"))
        # An incomplete 2-of-3-byte UTF-8 sequence at true EOF (no trailing
        # newline) — simulates a tail torn mid-flush inside a multibyte char.
        fh.write("☺".encode()[:2])
    # main() must return 1 cleanly — an uncaught UnicodeDecodeError would
    # make this call raise instead of returning, failing the test itself.
    rc = context_budget.main(["--project-dir", str(project_dir), "--sessions", "1", "--json"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "unreadable transcript" in err


def test_main_malformed_transcript_aborts_cleanly(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    # merge-gate lens 3: MalformedTranscriptError was proven to raise at the
    # HELPER but never driven through main()'s except tuples — removing it
    # from those tuples survived the suite (it is a ValueError, covered by
    # neither OSError nor UnicodeDecodeError).
    project_dir, transcript_dir = td
    _write_jsonl(
        transcript_dir / "corrupt.jsonl",
        [
            "{malformed non-tail line",
            json.dumps(_rec(request_id="r1", timestamp="t1", input_tokens=100)),
        ],
    )
    rc = context_budget.main(["--project-dir", str(project_dir), "--sessions", "1", "--json"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "unreadable transcript" in err


# --------------------------------------------------------------------------
# Coverage-bar rounding: no transcript dir / empty transcript dir
# --------------------------------------------------------------------------


def test_main_no_transcript_dir_aborts_cleanly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir = tmp_path / "nowhere"
    project_dir.mkdir()
    # Deliberately do NOT create the derived transcript dir.
    rc = context_budget.main(["--project-dir", str(project_dir), "--json"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "no transcript dir at" in err


def test_main_empty_transcript_dir_aborts_cleanly(
    td: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    project_dir, _transcript_dir = td
    rc = context_budget.main(["--project-dir", str(project_dir), "--json"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "no measurable sessions under" in err

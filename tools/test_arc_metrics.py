"""Tests for the arc-metrics ledger (B-170).

The load-bearing property under test is FAIL-CLOSED: an absent measurement must
never be recorded as a measured zero, and "could not look" must never be
reported as "looked and found nothing". Every test below has a mutation probe
noted -- revert the guard it covers and the test must red.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_metrics as am


# mutation-probe: delete the `if not logs: raise` guard in round_metrics()
def test_zero_matched_round_logs_aborts_rather_than_recording_zero(tmp_path: Path):
    """An unlooked path must not become '0 rounds'."""
    with pytest.raises(am.AbortError) as exc:
        am.round_metrics([str(tmp_path / "nothing-here-*.log")])
    assert "zero files matched" in str(exc.value)
    assert "unlooked" in str(exc.value)


# mutation-probe: delete the `if shutil.which(...) is None: raise` guard in run()
def test_missing_binary_aborts_with_named_cause():
    with pytest.raises(am.AbortError) as exc:
        am.run(["definitely-not-a-real-binary-xyz", "--version"], what="probe")
    assert "not on PATH" in str(exc.value)


# mutation-probe: change `if r.get("conclusion") != "success": continue` to pass
def test_cancelled_ci_run_excluded_from_durations(monkeypatch):
    """A ~65s cancelled run is NOT a fast green -- it must not enter the baseline."""
    sha = "abc123def4567890abc123def4567890abc123de"  # full 40 chars
    payload = json.dumps(
        [
            {
                "headSha": sha,
                "createdAt": "2026-08-14T09:00:00Z",
                "updatedAt": "2026-08-14T09:06:00Z",
                "conclusion": "success",
                "event": "push",
            },
            {
                "headSha": sha,
                "createdAt": "2026-08-14T09:10:00Z",
                "updatedAt": "2026-08-14T09:11:05Z",
                "conclusion": "cancelled",
                "event": "push",
            },
        ]
    )
    monkeypatch.setattr(am, "run", lambda *a, **k: payload)
    seen, durations = am.ci_metrics(sha)
    assert seen == 2, "both runs should be counted as seen"
    assert durations == [360.0], "only the successful run contributes timing"


def _merged_row(arc_id: str = "pr-1338", pr: int = 1338) -> am.ArcRow:
    """A row that satisfies the merged-arc precondition in append()."""
    return am.ArcRow(
        arc_id=arc_id,
        pr=pr,
        merged_at="2026-08-14T09:30:00Z",
        merge_sha="abc123def4567890abc123def4567890abc123de",
    )


# mutation-probe: delete the duplicate-arc_id guard in append()
def test_duplicate_arc_id_refused(monkeypatch, tmp_path: Path):
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.append(_merged_row())
    with pytest.raises(am.AbortError) as exc:
        am.append(_merged_row())
    assert "already in ledger" in str(exc.value)
    assert len(ledger.read_text().strip().splitlines()) == 1


# mutation-probe: delete the `if not row.merged_at or not row.merge_sha` guard
def test_unmerged_arc_refused_and_does_not_burn_the_arc_id(monkeypatch, tmp_path: Path):
    """A premature capture must not persist, or the real one is locked out."""
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    with pytest.raises(am.AbortError) as exc:
        am.append(am.ArcRow(arc_id="pr-1338", pr=1338))
    assert "unmerged arc" in str(exc.value)
    assert not ledger.exists(), "a refused row must leave no trace"
    # the arc_id is still free, so the correct post-merge capture succeeds
    am.append(_merged_row())
    assert len(ledger.read_text().strip().splitlines()) == 1


# mutation-probe: delete the FULL_SHA_LEN check at the top of ci_metrics()
def test_abbreviated_sha_refused_rather_than_recording_empty_ci(monkeypatch):
    """`gh run list --commit <abbrev>` returns [] for commits that DO have runs."""
    monkeypatch.setattr(am, "run", lambda *a, **k: "[]")
    with pytest.raises(am.AbortError) as exc:
        am.ci_metrics("84b84237")
    assert "full 40-char SHA" in str(exc.value)


# mutation-probe: make read_ledger() swallow JSONDecodeError and return []
def test_corrupt_ledger_line_aborts(monkeypatch, tmp_path: Path):
    ledger = tmp_path / "arc-metrics.jsonl"
    ledger.write_text('{"arc_id": "ok"}\nNOT-JSON\n')
    monkeypatch.setattr(am, "LEDGER", ledger)
    with pytest.raises(am.AbortError) as exc:
        am.read_ledger()
    assert "line 2" in str(exc.value)


# mutation-probe: change fmt_span to return a bare mean
def test_summary_reports_median_with_range_never_bare_mean():
    """Measured round variance is ~5x; a bare mean misleads."""
    out = am.fmt_span([60.0, 120.0, 3600.0])
    assert "n=3" in out
    assert "1.0-60.0" in out, "range must be shown"
    assert out.startswith("2.0m"), "median, not mean (mean would be 21.0m)"


# mutation-probe: make drain() clear the queue unconditionally instead of keeping failures
def test_drain_keeps_an_entry_whose_capture_failed(monkeypatch, tmp_path: Path):
    """A transient gh failure must cost a retry, never the row."""
    queue = tmp_path / "queue.jsonl"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE", queue)
    monkeypatch.setattr(am, "LEDGER", ledger)
    queue.write_text(json.dumps({"pr": 1338, "arc_id": "pr-1338"}) + "\n")

    def boom(_args):
        raise am.AbortError("gh unavailable")

    monkeypatch.setattr(am, "extract", boom)
    am.drain(am.argparse.Namespace())

    assert len(am.read_queue()) == 1, "a failed capture stays queued for retry"
    assert not ledger.exists()


# mutation-probe: delete the `if arc_id in known: continue` branch in drain()
def test_drain_drops_an_entry_already_in_the_ledger(monkeypatch, tmp_path: Path):
    queue = tmp_path / "queue.jsonl"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE", queue)
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.append(_merged_row("pr-1338", 1338))
    queue.write_text(json.dumps({"pr": 1338, "arc_id": "pr-1338"}) + "\n")

    am.drain(am.argparse.Namespace())

    assert am.read_queue() == [], "an already-folded arc leaves the queue"
    assert len(ledger.read_text().strip().splitlines()) == 1, "and is not duplicated"


# mutation-probe: point QUEUE at a path inside the repo
def test_queue_lives_outside_the_repo():
    """A topic worktree is disposed at loop completion; anything queued in it dies."""
    assert am.REPO not in am.QUEUE.parents, (
        f"queue {am.QUEUE} must not sit inside the repo, or arc closure "
        "both strands the row and blocks worktree disposal"
    )


def test_empty_span_is_dashes_not_zero():
    assert am.fmt_span([]) == "--"


# mutation-probe: default arc_type to "inventing" instead of leaving it None
def test_unclassified_judgement_fields_are_marked_unmapped_not_guessed(monkeypatch):
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 100,
            "deletions": 2,
            "changedFiles": 3,
            "commits": [{}],
            "createdAt": "2026-08-14T09:00:00Z",
            "mergedAt": "2026-08-14T09:30:00Z",
            "mergeCommit": None,
            "title": "t",
        },
    )
    args = am.argparse.Namespace(
        pr=999,
        arc_id=None,
        arc_type=None,
        decisions=None,
        round_logs=None,
        levers=None,
        notes="",
    )
    row = am.extract(args)
    assert row.arc_type is None
    assert row.decision_count is None
    assert row.provenance["arc_type"].startswith("unmapped")
    assert row.provenance["decision_count"].startswith("unmapped")
    assert row.provenance["round_fields"].startswith("unmapped")
    assert row.total_arc_wall_s == 1800.0


# mutation-probe: drop the `bare` term from count_p1()
def test_both_round_log_dialects_are_counted():
    """Counting only [P1] silently reports zero for commit-message logs."""
    codex = "noise\n[P1] a finding\nnoise\n[P1] a finding\n"  # same finding twice -> 1
    commit = "spec(cp): B-71 round 3 -- x\n\nP1 A CARRIED ROW RESETS AN ECHO.\n"
    assert am.count_p1(codex) == 1, "codex dialect: duplicate printing collapses"
    assert am.count_p1(commit) == 1, "commit dialect: bare P1, not duplicated"
    assert am.count_p1("no findings at all\n") == 0
    # A P1 mid-sentence is prose, not a finding tag.
    assert am.count_p1("we discussed P1 issues generally\n") == 0


# mutation-probe: drop the `^` line anchor from the bracketed pattern in count_p1()
def test_contextual_p1_mentions_are_not_findings():
    """Measured on the real B-40 round-1 log: both [P1] hits were prose."""
    quoted_past_review = (
        "the ledger entry says: R1 -- two real [P1]s advisor+author missed, then\n"
        "a skill doc shows the format `[P1] (confidence: 9/10) app/models/user.rb:42`\n"
    )
    assert am.count_p1(quoted_past_review) == 0, "a quoted/example tag is not a finding"


# mutation-probe: drop the rsplit on FINAL_REVIEW_MARKER in count_p1()
def test_only_the_final_review_block_is_counted():
    """An earlier round quoted in the transcript must not leak into this round."""
    text = (
        "Full review comments:\n- [P1] an OLD finding from a quoted round\n"
        "...later, the real review...\n"
        "Full review comments:\n- [P2] only a P2 this round\n"
    )
    assert am.count_p1(text) == 0, "the last block has no P1; the earlier one is stale"


# mutation-probe: make arc_duration() return total_arc_wall_s first
def test_arc_duration_prefers_real_span_over_pr_window():
    """#1337 measured: 6.1 min of PR window against 269.2 min of actual arc."""
    with_rounds = {"total_arc_wall_s": 366.0, "arc_span_s": 16152.6}
    assert am.arc_duration(with_rounds) == 16152.6, "the PR window is not the arc"
    # It cuts the other way too: a merged PR can sit open long after review ended.
    sat_open = {"total_arc_wall_s": 32892.0, "arc_span_s": 2664.0}
    assert am.arc_duration(sat_open) == 2664.0
    # No round data -> the PR window is the only thing left, and is used.
    assert am.arc_duration({"total_arc_wall_s": 900.0}) == 900.0
    assert am.arc_duration({}) is None


def test_p1_count_halves_the_codex_duplicate_printing(tmp_path: Path):
    """The codex CLI prints each finding twice; a single [P1] pair is ONE finding."""
    a = tmp_path / "r1.log"
    b = tmp_path / "r2.log"
    a.write_text("[P1] a real finding\n[P1] a real finding\n")  # 2 raw -> 1 true
    b.write_text("no findings here\n")  # 0
    os.utime(a, (1_000_000, 1_000_000))
    os.utime(b, (1_000_600, 1_000_600))
    logs, gaps, p1 = am.round_metrics([str(tmp_path / "r*.log")])
    assert len(logs) == 2
    assert gaps == [600.0]
    assert p1 == [1], "round 1 carried a P1; round 2 did not"

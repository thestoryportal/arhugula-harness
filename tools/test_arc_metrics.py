"""Tests for the arc-metrics ledger (B-170).

The load-bearing property under test is FAIL-CLOSED: an absent measurement must
never be recorded as a measured zero, and "could not look" must never be
reported as "looked and found nothing". Every test below has a mutation probe
noted -- revert the guard it covers and the test must red.
"""

from __future__ import annotations

import json
import os
import socket
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


def _queue_entry(qdir: Path, arc_id: str, pr: int) -> Path:
    """Write one queued-arc file, the shape `queue` emits."""
    qdir.mkdir(parents=True, exist_ok=True)
    path = qdir / f"{arc_id}.json"
    path.write_text(json.dumps({"pr": pr, "arc_id": arc_id}))
    return path


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
    qdir = tmp_path / "queue"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", ledger)
    _queue_entry(qdir, "pr-1338", 1338)

    def boom(_args):
        raise am.AbortError("gh unavailable")

    monkeypatch.setattr(am, "extract", boom)
    am.drain(am.argparse.Namespace())

    assert len(am.read_queue()) == 1, "a failed capture stays queued for retry"
    assert not ledger.exists()


# mutation-probe: release the entry on `arc_id in local` instead of `in committed`
def test_a_locally_appended_row_holds_its_queue_entry(monkeypatch, tmp_path: Path):
    """A working-tree row is not durable; the declarations live nowhere else."""
    qdir = tmp_path / "queue"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "committed_arc_ids", set)
    am.append(_merged_row("pr-1338", 1338))
    _queue_entry(qdir, "pr-1338", 1338)

    assert am.drain(am.argparse.Namespace()) == 1, "held work is not success"
    assert [e["arc_id"] for _p, e in am.read_queue()] == ["pr-1338"]
    assert len(ledger.read_text().strip().splitlines()) == 1, "and is not duplicated"


# mutation-probe: change MERGED_REF back to "HEAD" in committed_arc_ids()
def test_release_is_gated_on_merged_history_not_the_topic_branch(monkeypatch):
    """A topic-branch commit can still be reset or abandoned; merged history cannot."""
    seen = {}

    def fake_run(cmd, *, what):
        seen["cmd"] = cmd
        raise am.AbortError("not found")

    monkeypatch.setattr(am, "run", fake_run)
    assert am.committed_arc_ids() == set(), "unreadable merged history releases nothing"
    ref = seen["cmd"][2].split(":")[0]
    assert ref != "HEAD", "HEAD includes the not-yet-merged topic commit"
    assert ref == am.MERGED_REF


# mutation-probe: drop the arc_span_s lower-bound provenance label in extract()
def test_arc_span_is_labelled_a_lower_bound(monkeypatch):
    """mtime marks round COMPLETION, so round 1's own duration is missing."""
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 10,
            "deletions": 0,
            "changedFiles": 1,
            "commits": [{}],
            "createdAt": "2026-08-14T09:00:00Z",
            "mergedAt": "2026-08-14T12:00:00Z",
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
        round_snapshot={
            "review_rounds": 1,
            "round_wall_s": [],
            "p1_rounds": [],
            "first_round_at": "2026-08-14T11:00:00+00:00",
            "last_round_at": "2026-08-14T11:00:00+00:00",
            "round_log_source": "/tmp/logs",
        },
    )
    row = am.extract(args)
    assert row.arc_span_s == 3600.0
    assert row.provenance["arc_span_s"].startswith("derived:lower-bound"), (
        "an unlabelled span reads as the whole arc when it is only its tail"
    )


# mutation-probe: delete the `if arc_id in committed: unlink` branch in drain()
def test_entry_is_released_once_the_row_reaches_committed_history(monkeypatch, tmp_path: Path):
    qdir = tmp_path / "queue"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "committed_arc_ids", lambda: {"pr-1338"})
    am.append(_merged_row("pr-1338", 1338))
    _queue_entry(qdir, "pr-1338", 1338)

    assert am.drain(am.argparse.Namespace()) == 0
    assert am.read_queue() == [], "committed means the capture can finally go"


# mutation-probe: make drain() rewrite the whole queue instead of unlinking per file
def test_drain_does_not_erase_an_entry_queued_while_it_runs(monkeypatch, tmp_path: Path):
    """Parallel arcs are supported, so a concurrent queue must survive a drain."""
    qdir = tmp_path / "queue"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", ledger)
    _queue_entry(qdir, "pr-1338", 1338)

    def extract_then_another_arc_queues(_args):
        # a second arc queues mid-drain, as a parallel lane would
        _queue_entry(qdir, "pr-1341", 1341)
        return _merged_row("pr-1338", 1338)

    monkeypatch.setattr(am, "extract", extract_then_another_arc_queues)
    am.drain(am.argparse.Namespace())

    still = [e["arc_id"] for _p, e in am.read_queue()]
    assert "pr-1341" in still, "the concurrently-queued arc must not be erased"


# mutation-probe: unlink the queued file BEFORE append(extract(...)) succeeds
def test_a_failed_capture_leaves_its_queued_file_on_disk(monkeypatch, tmp_path: Path):
    """The retry must survive a crash between capture and cleanup."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")
    path = _queue_entry(qdir, "pr-1338", 1338)

    def boom(_args):
        raise am.AbortError("gh unavailable")

    monkeypatch.setattr(am, "extract", boom)
    am.drain(am.argparse.Namespace())
    assert path.exists(), "a queued file is unlinked only once its row is durable"


# mutation-probe: make drain() return 0 unconditionally
def test_drain_exits_nonzero_when_an_entry_is_still_queued(monkeypatch, tmp_path: Path):
    """Exit 0 with work pending would read as a completed fold to automation."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")
    _queue_entry(qdir, "pr-1338", 1338)

    def boom(_args):
        raise am.AbortError("gh unavailable")

    monkeypatch.setattr(am, "extract", boom)
    assert am.drain(am.argparse.Namespace()) == 1


# mutation-probe: change the queued-file open mode from "x" to "w"
def test_queueing_the_same_arc_twice_is_refused(monkeypatch, tmp_path: Path):
    """A second queue must not silently overwrite the first session's judgements."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    args = am.argparse.Namespace(
        pr=1338,
        arc_id=None,
        arc_type="applying",
        decisions=1,
        round_logs=None,
        levers=None,
        notes="first",
    )
    am.queue_capture(args)
    args.notes = "second"
    with pytest.raises(am.AbortError) as exc:
        am.queue_capture(args)
    assert "already queued" in str(exc.value)
    assert json.loads((qdir / "pr-1338.json").read_text())["notes"] == "first"


# mutation-probe: re-wrap the ci_metrics call in extract() with `except AbortError`
def test_transient_ci_failure_aborts_rather_than_persisting_an_unmapped_row(monkeypatch):
    """A gh outage is not an absent input; swallowing it makes the loss permanent."""
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 10,
            "deletions": 0,
            "changedFiles": 1,
            "commits": [{}],
            "createdAt": "2026-08-14T09:00:00Z",
            "mergedAt": "2026-08-14T09:30:00Z",
            "mergeCommit": {"oid": "a" * 40},
            "title": "t",
        },
    )

    def gh_down(*_a, **_k):
        raise am.AbortError("gh run list: exit 1 ... network unreachable")

    monkeypatch.setattr(am, "run", gh_down)
    args = am.argparse.Namespace(
        pr=999, arc_id=None, arc_type=None, decisions=None, round_logs=None, levers=None, notes=""
    )
    with pytest.raises(am.AbortError):
        am.extract(args)


# mutation-probe: drop the de-duplication in round_metrics()
def test_overlapping_globs_do_not_double_count_a_round(tmp_path: Path):
    a = tmp_path / "r1.log"
    b = tmp_path / "r2.log"
    a.write_text("x\n")
    b.write_text("y\n")
    os.utime(a, (1_000_000, 1_000_000))
    os.utime(b, (1_000_600, 1_000_600))
    logs, gaps, _ = am.round_metrics([str(tmp_path / "r*.log"), str(tmp_path / "r1*.log")])
    assert len(logs) == 2, "the same file matched twice is still one round"
    assert gaps == [600.0], "and introduces no spurious zero-second gap"


# mutation-probe: change the review-rounds median format back to :.0f
def test_partial_rows_are_excluded_from_exact_aggregates(monkeypatch, tmp_path: Path, capsys):
    """A surviving fragment must not be averaged in as a whole arc."""
    ledger = tmp_path / "arc-metrics.jsonl"
    rows = [
        {"arc_id": "a", "review_rounds": 4, "arc_span_s": 6000.0, "levers_active": []},
        {"arc_id": "b", "review_rounds": 5, "arc_span_s": 6000.0, "levers_active": []},
        {
            "arc_id": "frag",
            "review_rounds": 1,
            "arc_span_s": 60.0,
            "levers_active": [],
            "round_completeness": "partial-suffix",
        },
    ]
    ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.summary(am.argparse.Namespace())
    out = capsys.readouterr().out
    assert "review rounds    4.5" in out, "median of [4,5] is 4.5, not 4"
    assert "EXCLUDED" in out and "frag>=1" in out


# mutation-probe: point QUEUE_DIR at a path inside the repo
def test_queue_lives_outside_the_repo():
    """A topic worktree is disposed at loop completion; anything queued in it dies."""
    assert am.REPO not in am.QUEUE_DIR.parents, (
        f"queue {am.QUEUE_DIR} must not sit inside the repo, or arc closure "
        "both strands the row and blocks worktree disposal"
    )


# mutation-probe: default round_wall_s/p1_rounds back to field(default_factory=list)
def test_absent_round_data_is_null_not_an_empty_list():
    """[] is a real measurement -- a 1-round arc has no gaps, a clean arc no P1s."""
    row = am.ArcRow(arc_id="pr-1", pr=1)
    assert row.round_wall_s is None, "unsupplied round data must not look measured"
    assert row.p1_rounds is None


# mutation-probe: collapse the by_levers grouping back to one TREATED cohort
def test_treated_cohorts_stay_separated_by_lever(monkeypatch, tmp_path: Path, capsys):
    """Averaging B-171 against B-173 would report a blend as an effect."""
    ledger = tmp_path / "arc-metrics.jsonl"
    rows = [
        {"arc_id": "b", "review_rounds": 4, "arc_span_s": 6000.0, "levers_active": []},
        {"arc_id": "t1", "review_rounds": 2, "arc_span_s": 600.0, "levers_active": ["B-171"]},
        {"arc_id": "t2", "review_rounds": 9, "arc_span_s": 9000.0, "levers_active": ["B-173"]},
    ]
    ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.summary(am.argparse.Namespace())
    out = capsys.readouterr().out
    assert "TREATED [B-171]" in out and "TREATED [B-173]" in out
    assert "lever cohorts: 2" in out


# mutation-probe: store the globs/paths instead of derived metrics in queue_capture()
def test_queue_snapshots_derived_metrics_not_a_live_glob(monkeypatch, tmp_path: Path):
    """Logs are mutable; only the metrics measured at closure describe the arc."""
    qdir = tmp_path / "queue"
    logs = tmp_path / "logs"
    logs.mkdir()
    a, b = logs / "round1.log", logs / "round2.log"
    a.write_text("[P1] a real finding\n")
    b.write_text("clean\n")
    os.utime(a, (1_000_000, 1_000_000))
    os.utime(b, (1_000_600, 1_000_600))
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    am.queue_capture(
        am.argparse.Namespace(
            pr=1338,
            arc_id=None,
            arc_type="applying",
            decisions=1,
            round_logs=[str(logs / "round*.log")],
            levers=None,
            notes="",
        )
    )
    snap = json.loads((qdir / "pr-1338.json").read_text())["round_snapshot"]
    assert snap["review_rounds"] == 2
    assert snap["round_wall_s"] == [600.0]
    assert snap["p1_rounds"] == [1]

    # After closure the world moves on: a later arc adds a matching file, and a
    # re-run rewrites and re-times one of the originals.
    (logs / "round3.log").write_text("later\n")
    b.write_text("[P1] a finding that was NOT in this arc\n")
    os.utime(b, (2_000_000, 2_000_000))

    frozen = json.loads((qdir / "pr-1338.json").read_text())["round_snapshot"]
    assert frozen == snap, "the queued metrics must not track later edits"


# mutation-probe: delete the os.rename claim in drain()
def test_a_claimed_arc_is_skipped_by_a_concurrent_drain(monkeypatch, tmp_path: Path):
    """Two drains must not both append the same arc past the duplicate guard."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")
    path = _queue_entry(qdir, "pr-1338", 1338)
    stale_listing = am.read_queue()

    # A peer drain claimed AND finished this arc after we listed it, so our
    # rename finds nothing. Losing that race must be a skip, not a re-capture.
    path.unlink()
    monkeypatch.setattr(am, "read_queue", lambda: stale_listing)

    calls = []
    monkeypatch.setattr(am, "extract", lambda a: calls.append(a) or _merged_row())
    am.drain(am.argparse.Namespace())
    assert calls == [], "an arc already claimed elsewhere is not captured again"


# mutation-probe: split _claim_arc into rename-then-stamp
def test_a_claim_is_never_observable_without_its_owner_stamp(monkeypatch, tmp_path: Path):
    """An unstamped claim reads as 'dead owner' and gets stolen from a live one."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    path = _queue_entry(qdir, "pr-1338", 1338)
    entry = json.loads(path.read_text())

    taken = am._claim_arc(path, entry)
    assert taken is not None and taken.exists()
    assert not path.exists(), "the source is released only after the claim exists"
    stamped = json.loads(taken.read_text())["_claim"]
    assert stamped["pid"] == os.getpid()
    assert stamped["host"] == socket.gethostname()
    # and the stamp is what liveness reads, so a live owner is never 'dead'
    assert am._claim_owner_is_dead(taken) is False


# mutation-probe: catch OSError broadly in _claim_arc and report a lost race
def test_a_non_race_claim_failure_aborts_rather_than_reporting_a_lost_race(
    monkeypatch, tmp_path: Path
):
    """Reporting an I/O failure as a peer claim lets an incomplete drain exit 0."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    path = _queue_entry(qdir, "pr-1338", 1338)
    entry = json.loads(path.read_text())

    def unwritable(*_a, **_k):
        raise PermissionError(13, "read-only file system")

    monkeypatch.setattr(Path, "open", unwritable)
    with pytest.raises(am.AbortError) as exc:
        am._claim_arc(path, entry)
    assert "cannot claim" in str(exc.value)


# mutation-probe: delete the _recover_dead_claims() call at the top of drain()
def test_claim_from_a_dead_drain_is_recovered(monkeypatch, tmp_path: Path):
    """A crashed drain must not strand the arc where read_queue never looks."""
    qdir = tmp_path / "queue"
    qdir.mkdir(parents=True)
    dead_pid = 999_999_999  # not a live process
    (qdir / "pr-1338.taken").write_text(
        json.dumps(
            {
                "pr": 1338,
                "arc_id": "pr-1338",
                "_claim": {"pid": dead_pid, "host": socket.gethostname()},
            }
        )
    )
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")
    monkeypatch.setattr(am, "extract", lambda _a: _merged_row())
    am.drain(am.argparse.Namespace())
    assert not (qdir / "pr-1338.taken").exists(), "the dead owner's claim was recovered"


# mutation-probe: drop the _process_is_alive() check in _recover_dead_claims()
def test_claim_held_by_a_live_drain_is_not_stolen(monkeypatch, tmp_path: Path):
    """Recovering a live peer's claim reproduces the duplicate row it prevents."""
    qdir = tmp_path / "queue"
    qdir.mkdir(parents=True)
    claim = qdir / "pr-1338.taken"
    claim.write_text(
        json.dumps(
            {
                "pr": 1338,
                "arc_id": "pr-1338",
                # our own pid is, by construction, alive
                "_claim": {"pid": os.getpid(), "host": socket.gethostname()},
            }
        )
    )
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")
    calls = []
    monkeypatch.setattr(am, "extract", lambda a: calls.append(a) or _merged_row())
    am.drain(am.argparse.Namespace())
    assert claim.exists(), "a live owner keeps its claim"
    assert calls == [], "and its arc is not captured a second time"


# mutation-probe: recover a foreign-host claim instead of leaving it
def test_claim_held_on_another_host_is_left_alone(monkeypatch, tmp_path: Path):
    """Liveness is unknowable from here, so the safe move is to not touch it."""
    qdir = tmp_path / "queue"
    qdir.mkdir(parents=True)
    claim = qdir / "pr-1338.taken"
    claim.write_text(
        json.dumps(
            {
                "pr": 1338,
                "arc_id": "pr-1338",
                "_claim": {"pid": 999_999_999, "host": "some-other-machine"},
            }
        )
    )
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")
    am.drain(am.argparse.Namespace())
    assert claim.exists(), "a claim on another host is reported, never stolen"


# mutation-probe: change fmt_span's empty-input branch to return "0"
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


# mutation-probe: delete the `if span < 0: raise` guard in extract()
def test_round_log_postdating_the_merge_aborts(monkeypatch):
    """A negative span is a broken input, and negatives are truthy in medians."""
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 10,
            "deletions": 0,
            "changedFiles": 1,
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
        # a copied log stamped AFTER the merge
        round_snapshot={
            "review_rounds": 1,
            "round_wall_s": [],
            "p1_rounds": [],
            "first_round_at": "2026-08-14T11:00:00+00:00",
            "last_round_at": "2026-08-14T11:00:00+00:00",
            "round_log_source": "/tmp/logs",
        },
    )
    with pytest.raises(am.AbortError) as exc:
        am.extract(args)
    assert "postdates" in str(exc.value)


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


# mutation-probe: count raw [P1] occurrences instead of distinct finding lines
def test_p1_count_collapses_the_codex_duplicate_printing(tmp_path: Path):
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

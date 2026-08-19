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


# mutation-probe: pool arc_span_s and total_arc_wall_s into one `arcs` list
def test_arc_spans_and_pr_windows_are_never_pooled(monkeypatch, tmp_path: Path, capsys):
    """They measure different things; a median over the mixture means nothing."""
    ledger = tmp_path / "arc-metrics.jsonl"
    rows = [
        # a real span, and a PR window that is 10x larger
        {"arc_id": "spanned", "arc_span_s": 600.0, "total_arc_wall_s": 99.0, "levers_active": []},
        {"arc_id": "windowed", "total_arc_wall_s": 6000.0, "levers_active": []},
    ]
    ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.summary(am.argparse.Namespace())
    out = capsys.readouterr().out
    assert "arc span         10.0m (n=1" in out, "only the spanned row is an arc span"
    assert "PR-open window   100.0m (n=1" in out, "the window is reported on its own line"


# mutation-probe: make publish_exclusive open(path,"x") and write in place
def test_an_interrupted_publish_leaves_no_wedged_file(monkeypatch, tmp_path: Path):
    """A truncated queue entry is not a lost write -- it is a deadlock.

    read_queue() aborts on malformed JSON forever, while re-queueing the same
    arc is refused because the name exists. So a failed serialization must
    leave the destination ABSENT, not partial.
    """
    dest = tmp_path / "pr-1338.json"

    def die(_src, _dst, *_a, **_k):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(os, "link", die)
    with pytest.raises(OSError):
        am.publish_exclusive(dest, json.dumps({"pr": 1338}))
    monkeypatch.undo()

    assert not dest.exists(), "an interrupted publish must not wedge the name"
    assert list(tmp_path.iterdir()) == [], "and must not strand its temp file"
    # the name is still free, so the arc can simply be queued again
    am.publish_exclusive(dest, json.dumps({"pr": 1338}))
    assert json.loads(dest.read_text())["pr"] == 1338


# mutation-probe: replace os.link with os.replace in publish_exclusive
def test_publish_exclusive_still_refuses_a_taken_name(tmp_path: Path):
    """Atomicity must not cost exclusivity -- both call sites depend on it."""
    dest = tmp_path / "pr-1338.json"
    am.publish_exclusive(dest, json.dumps({"first": True}))
    with pytest.raises(FileExistsError):
        am.publish_exclusive(dest, json.dumps({"second": True}))
    assert json.loads(dest.read_text()) == {"first": True}, "the winner is not overwritten"


# mutation-probe: delete the arc_id path-component guard in queue_capture()
def test_an_arc_id_that_escapes_the_queue_dir_is_refused(monkeypatch, tmp_path: Path):
    """An escaped file reports success and is then never drained."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    for bad in ("../escaped", "nested/id", "/absolute", ".."):
        args = am.argparse.Namespace(
            pr=1338,
            arc_id=bad,
            arc_type="applying",
            decisions=1,
            round_logs=None,
            levers=None,
            notes="",
        )
        with pytest.raises(am.AbortError) as exc:
            am.queue_capture(args)
        assert "unsafe --arc-id" in str(exc.value), bad
    assert not (tmp_path / "escaped.json").exists(), "nothing lands outside the queue"


# mutation-probe: revert the `is not None` checks in summary()/arc_duration() to truthiness
def test_a_measured_zero_duration_is_not_treated_as_absent(monkeypatch, tmp_path: Path, capsys):
    """0.0 is a measurement; dropping it is absent-vs-zero pointing the other way."""
    assert am.arc_duration({"arc_span_s": 0.0, "total_arc_wall_s": 900.0}) == 0.0, (
        "a zero span must not silently fall through to the PR window"
    )
    ledger = tmp_path / "arc-metrics.jsonl"
    ledger.write_text(
        json.dumps({"arc_id": "z", "arc_span_s": 0.0, "levers_active": []})
        + "\n"
        + json.dumps({"arc_id": "w", "total_arc_wall_s": 600.0, "levers_active": []})
        + "\n"
    )
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.summary(am.argparse.Namespace())
    out = capsys.readouterr().out
    assert "arc span         0.0m (n=1" in out, "the zero span is counted, not dropped"
    assert "PR-open window   10.0m (n=1" in out, "and is not reclassified as a window"


# mutation-probe: rename a subcommand or drop a set_defaults(func=...) in main()
def test_the_real_cli_path_is_wired(monkeypatch, tmp_path: Path, capsys):
    """Every other test bypasses argparse; `just arc-metrics` does not.

    The production entry point is `justfile` -> `python tools/arc_metrics.py "$@"`
    -> `main(argv)`. A renamed flag, a dropped `set_defaults(func=...)`, or a
    removed exit-code wrapper would leave every direct-call test green while
    breaking the command ship-pr actually runs.
    """
    qdir = tmp_path / "queue"
    ledger = tmp_path / "arc-metrics.jsonl"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "LEDGER", ledger)

    # queue: subparser + required declared flags + func dispatch
    assert am.main(["queue", "--pr", "1338", "--arc-type", "applying", "--decisions", "1"]) == 0
    assert (qdir / "pr-1338.json").exists()

    # summary: reads the ledger through the same dispatch
    ledger.write_text(json.dumps({"arc_id": "a", "arc_span_s": 600.0, "levers_active": []}) + "\n")
    assert am.main(["summary"]) == 0
    assert "arc span" in capsys.readouterr().out

    # the AbortError -> exit 2 wrapper, through the real CLI rather than a raise
    ledger.unlink()
    assert am.main(["summary"]) == 2, "a failed run must exit non-zero, not raise"


# mutation-probe: drop `required=True` from queue's --arc-type/--decisions
def test_the_cli_refuses_a_queue_without_its_declared_judgements(monkeypatch, tmp_path: Path):
    """argparse is where that requirement actually lives; nothing else checks it."""
    monkeypatch.setattr(am, "QUEUE_DIR", tmp_path / "queue")
    with pytest.raises(SystemExit) as exc:
        am.main(["queue", "--pr", "1338"])
    assert exc.value.code != 0


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
    rc = am.drain(am.argparse.Namespace())
    assert calls == [], "an arc already claimed elsewhere is not captured again"
    assert rc == 1, "a peer's in-flight claim is outstanding work, not success"


# mutation-probe: split _claim_arc into rename-then-stamp
def test_a_claim_is_never_observable_without_its_owner_stamp(monkeypatch, tmp_path: Path):
    """An unstamped claim reads as 'dead owner' and gets stolen from a live one."""
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    path = _queue_entry(qdir, "pr-1338", 1338)
    entry = json.loads(path.read_text())

    # Watch the DESTINATION as it is published, not just the end state. A
    # create-then-write (or rename-then-stamp) refactor produces an identical
    # final file, so poststate alone cannot see the partial window a peer would
    # misread — as "no owner" (dead, steal it) or as unverifiable (held forever).
    seen: list[str] = []
    real_link = os.link

    def spy_link(src, dst, *a, **k):
        # at the instant the destination appears, it must already be complete
        real_link(src, dst, *a, **k)
        seen.append(Path(dst).read_text())

    monkeypatch.setattr(os, "link", spy_link)
    taken = am._claim_arc(path, entry)
    monkeypatch.undo()

    assert taken is not None and taken.exists()
    assert not path.exists(), "the source is released only after the claim exists"
    assert len(seen) == 1, f"the claim is published once, saw {len(seen)}"
    assert "_claim" in seen[0], "the name never exists without its owner stamp"
    assert json.loads(seen[0]), "and never exists holding truncated JSON"

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
    # Name the FIRST-round guard specifically. Both guards say "postdates", so
    # asserting on that word alone would pass via the sibling guard and witness
    # nothing about the one this probe names.
    assert "first round log" in str(exc.value)


# mutation-probe: delete the last_round_at-vs-merged_at check in extract()
def test_last_round_log_postdating_the_merge_aborts(monkeypatch):
    """Guarding only the START still accepts a set that reaches past the arc."""
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 10,
            "deletions": 0,
            "changedFiles": 1,
            "commits": [{}],
            "createdAt": "2026-08-14T09:00:00Z",
            "mergedAt": "2026-08-14T10:00:00Z",
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
            "review_rounds": 3,
            "round_wall_s": [600.0, 600.0],
            "p1_rounds": [],
            # starts inside the arc, so the span stays positive and innocent...
            "first_round_at": "2026-08-14T09:30:00+00:00",
            # ...but the set reaches past the merge
            "last_round_at": "2026-08-14T11:00:00+00:00",
            "round_log_source": "/tmp/logs",
        },
    )
    with pytest.raises(am.AbortError) as exc:
        am.extract(args)
    assert "last round log" in str(exc.value)


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
    # p1_rounds is built with `count_p1(...) >= 1`, a THRESHOLD -- so a raw
    # un-deduped count of 2 would still yield [1] and leave this test green.
    # Assert the count itself, or this stops witnessing the collapse it names.
    assert am.count_p1(a.read_text()) == 1, "two emissions of one finding are one finding"


# ── C-HE-19: CI terminal states -- CANCELLED is INCOMPLETE, never green (U-HE-08) ────────
# mutation-probe: add "cancelled" to CI_GREEN in arc_metrics
@pytest.mark.parametrize(
    "conclusion,green",
    [
        ("success", True),
        ("failure", False),
        ("cancelled", False),
        ("", False),
        (None, False),
        ("SUCCESS", True),
        ("CANCELLED", False),
        ("skipped", False),
        ("timed_out", False),
    ],
)
def test_ci_state_cancelled_incomplete(conclusion, green):
    assert am.ci_is_green(conclusion) is green
    assert am.CI_TERMINAL == ("SUCCESS", "FAILURE", "CANCELLED")
    assert am.CI_GREEN == frozenset({"SUCCESS"})


def test_ci_green_timing_uses_the_one_predicate(monkeypatch):
    """The green-timing exclusion consumes `ci_is_green`: a cancelled run never enters the
    baseline even if the raw conclusion filter were edited."""
    runs = [
        {
            "headSha": "a" * 40,
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:01:05Z",
            "conclusion": "cancelled",
            "event": "push",
        },
        {
            "headSha": "a" * 40,
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:05:50Z",
            "conclusion": "success",
            "event": "push",
        },
    ]
    monkeypatch.setattr(am, "run", lambda *a, **k: json.dumps(runs))
    seen: list[str | None] = []
    real = am.ci_is_green

    def spy(c):
        seen.append(c)
        return real(c)

    monkeypatch.setattr(am, "ci_is_green", spy)
    n, durations = am.ci_metrics("a" * 40)
    assert n == 2 and durations == [350.0]
    assert seen == ["cancelled", "success"]


# ---- U-HE-10 (C-HE-05): per-process REPO / LEDGER overrides -----------------------------


def test_env_overrides(tmp_path: Path):
    """Two subprocesses with different ARC_METRICS_REPO observe different LEDGER paths and
    one QUEUE_DIR (C-HE-05 Verification)."""
    import subprocess

    q = tmp_path / "queue"
    code = (
        "import arc_metrics as am, json; "
        "print(json.dumps({'ledger': str(am.LEDGER), 'queue': str(am.QUEUE_DIR)}))"
    )
    outs = []
    for name in ("wt-a", "wt-b"):
        env = {
            **os.environ,
            "ARC_METRICS_REPO": str(tmp_path / name),
            "ARC_METRICS_QUEUE_DIR": str(q),
            "PYTHONPATH": str(Path(__file__).resolve().parent),
        }
        env.pop("ARC_METRICS_LEDGER", None)
        proc = subprocess.run(
            [sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True
        )
        outs.append(json.loads(proc.stdout))
    assert outs[0]["ledger"] != outs[1]["ledger"]
    assert outs[0]["queue"] == outs[1]["queue"] == str(q)
    assert outs[0]["ledger"].endswith("wt-a/.harness/arc-metrics.jsonl")


def test_env_override_ledger_wins_over_repo(tmp_path: Path):
    """ARC_METRICS_LEDGER names the file directly; ARC_METRICS_REPO only supplies the default."""
    import subprocess

    code = "import arc_metrics as am; print(am.LEDGER)"
    env = {
        **os.environ,
        "ARC_METRICS_REPO": str(tmp_path / "wt"),
        "ARC_METRICS_LEDGER": str(tmp_path / "elsewhere.jsonl"),
        "PYTHONPATH": str(Path(__file__).resolve().parent),
    }
    proc = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True
    )
    assert proc.stdout.strip() == str(tmp_path / "elsewhere.jsonl")


def test_env_override_defaults_unchanged(monkeypatch):
    """C-HE-05 Invariants: unset -> the checkout root and its tracked ledger."""
    import importlib

    monkeypatch.delenv("ARC_METRICS_REPO", raising=False)
    monkeypatch.delenv("ARC_METRICS_LEDGER", raising=False)
    mod = importlib.reload(am)
    try:
        assert mod.REPO == Path(am.__file__).resolve().parent.parent
        assert mod.LEDGER == mod.REPO / ".harness" / "arc-metrics.jsonl"
    finally:
        importlib.reload(am)


# ---- U-HE-11 (C-HE-25): arc-row field extension + null-safe lane cohort -----------------

NEW_FIELDS = [
    "record_kind",
    "reviewer_identity",
    "prompt_version",
    "config_hash",
    "arc_type_open",
    "arc_type_close",
    "arc_type_declared_at",
    "round_outcomes",
    "head_sha",
    "base_sha",
    "lane_id",
    "concurrent_lanes_at_open",
    "concurrent_lanes_min",
    "concurrent_lanes_max",
    "phases",
]


def test_arc_row_schema_has_c_he_25_fields():
    from dataclasses import asdict

    d = asdict(am.ArcRow(arc_id="pr-1"))
    for f in NEW_FIELDS:
        assert f in d, f
    assert d["record_kind"] == "arc" and d["phases"] == {} and d["round_outcomes"] == {}


def test_ledger_rows_are_all_record_kind_arc():
    """C-HE-24 §2 / C-HE-25: the tracked ledger carries ONLY arc rows (historical rows read
    as `arc` via the null default)."""
    rows = am.read_ledger()
    assert rows, "tracked ledger is empty -- the test has nothing to witness"
    for r in rows:
        assert r.get("record_kind", "arc") == "arc"


# mutation-probe: drop the `by_lanes` grouping block in summary()
def test_cohort_split_null_safe(monkeypatch, tmp_path: Path, capsys):
    import argparse

    ledger = tmp_path / "l.jsonl"
    rows = [
        {
            "arc_id": "a",
            "levers_active": [],
            "arc_span_s": 60.0,
            "review_rounds": 1,
            "round_completeness": "complete",
        },
        {
            "arc_id": "b",
            "levers_active": [],
            "arc_span_s": 120.0,
            "review_rounds": 2,
            "round_completeness": "complete",
            "concurrent_lanes_at_open": 2,
        },
    ]
    ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    monkeypatch.setattr(am, "LEDGER", ledger)
    assert am.summary(argparse.Namespace()) == 0
    out = capsys.readouterr().out
    assert "LANES [concurrent_lanes_at_open=null] (n=1)" in out
    assert "LANES [concurrent_lanes_at_open=2] (n=1)" in out
    assert "concurrent_lanes_at_open=None" not in out


# ---- U-HE-12 (C-HE-26 §2): arc_type_open / arc_type_close on the single arc row ---------


# mutation-probe: drop the `len(hits) != 1` guard in relabel_arc_type_close()
def test_arc_type_at_open(monkeypatch, tmp_path: Path):
    """Close-time relabel: ONE arc row, arc_type_open != arc_type_close, no duplicate arc_id."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    row = am.ArcRow(
        arc_id="pr-9",
        merged_at="2026-08-18T00:00:00Z",
        merge_sha="x",
        arc_type_open="inventing",
        arc_type_declared_at="open",
    )
    am.append(row)
    am.relabel_arc_type_close("pr-9", "applying")
    rows = am.read_ledger()
    assert len(rows) == 1
    assert rows[0]["arc_type_open"] == "inventing" and rows[0]["arc_type_close"] == "applying"
    # an unknown arc or a duplicate is refused, never "fixed" by appending a second row
    with pytest.raises(am.AbortError, match="expected exactly one arc row"):
        am.relabel_arc_type_close("pr-404", "applying")
    with pytest.raises(am.AbortError, match="must be inventing"):
        am.relabel_arc_type_close("pr-9", "refactoring")
    assert len(am.read_ledger()) == 1


def test_relabel_leaves_every_other_row_byte_identical(monkeypatch, tmp_path: Path):
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    other = {"arc_id": "pr-1", "arc_type": "inventing", "notes": "historical row, no new keys"}
    ledger.write_text(json.dumps(other, sort_keys=True) + "\n")
    am.append(am.ArcRow(arc_id="pr-2", merged_at="2026-08-18T00:00:00Z", merge_sha="y"))
    am.relabel_arc_type_close("pr-2", "applying")
    lines = ledger.read_text().splitlines()
    assert lines[0] == json.dumps(other, sort_keys=True)
    assert json.loads(lines[1])["arc_type_close"] == "applying"


def test_extract_records_which_side_declared_the_label(monkeypatch):
    import argparse

    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {"additions": 1, "changedFiles": 1, "createdAt": "2026-01-01T00:00:00Z"},
    )
    base = dict(pr=1, arc_id=None, round_logs=None, decisions=None, levers=None, notes="")
    row = am.extract(argparse.Namespace(**base, arc_type="inventing", arc_type_declared_at="open"))
    assert (row.arc_type_open, row.arc_type_close, row.arc_type_declared_at) == (
        "inventing",
        None,
        "open",
    )
    row = am.extract(argparse.Namespace(**base, arc_type="applying", arc_type_declared_at="close"))
    assert (row.arc_type_open, row.arc_type_close, row.arc_type_declared_at) == (
        None,
        "applying",
        "close",
    )
    # a drain-built Namespace from a pre-U-HE-12 queue entry has no declared_at: reads as close
    row = am.extract(argparse.Namespace(**base, arc_type="applying"))
    assert (row.arc_type_close, row.arc_type_declared_at) == ("applying", "close")
    row = am.extract(argparse.Namespace(**base, arc_type=None))
    assert (row.arc_type_open, row.arc_type_close, row.arc_type_declared_at) == (None, None, None)


def test_relabel_cli_is_wired(monkeypatch, tmp_path: Path, capsys):
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.append(am.ArcRow(arc_id="pr-3", merged_at="2026-08-18T00:00:00Z", merge_sha="z"))
    assert am.main(["relabel", "--arc-id", "pr-3", "--arc-type-close", "inventing"]) == 0
    assert am.read_ledger()[0]["arc_type_close"] == "inventing"
    assert am.main(["relabel", "--arc-id", "pr-3", "--arc-type-close", "inventing"]) == 0
    assert len(am.read_ledger()) == 1

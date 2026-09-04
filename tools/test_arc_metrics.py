"""Tests for the arc-metrics ledger (B-170).

The load-bearing property under test is FAIL-CLOSED: an absent measurement must
never be recorded as a measured zero, and "could not look" must never be
reported as "looked and found nothing". Every test below has a mutation probe
noted -- revert the guard it covers and the test must red.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_metrics as am
import reservations as rs


@pytest.fixture(autouse=True)
def _reservations_isolated(tmp_path_factory, monkeypatch):
    """Isolate the reservation store per test and silence the fail-closed loop emitter.

    U-HE-19 wires drain through reservations: a legacy (reservation-less) queue entry is
    bootstrap-reserved at drain, which would otherwise (a) write into the REAL shared
    QUEUE_DIR/reservations and (b) raise from the fail-closed emit_loop_row until U-HE-29
    lands loop_log_structured. Tests exercising either behaviour re-patch explicitly."""
    monkeypatch.setattr(rs, "QUEUE_DIR", tmp_path_factory.mktemp("resq"))
    monkeypatch.setattr(rs, "emit_loop_row", lambda *a, **k: None)


@pytest.fixture
def qdir_res(tmp_path, monkeypatch):
    """One tmp dir as BOTH the arc_metrics queue and the reservations store root."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    return q


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


def _append_unfenced(row):
    """Legacy guard unit tests predate reservations: stub the holder seam for ONE call
    (the production path has no bypass parameter -- codex U-HE-19 r8 P2)."""
    orig = am._require_reservation_holder
    am._require_reservation_holder = lambda r: None
    try:
        am.append(row)
    finally:
        am._require_reservation_holder = orig


def _queue_entry(qdir: Path, arc_id: str, pr: int) -> Path:
    """Write one queued-arc file, the shape `queue` emits."""
    qdir.mkdir(parents=True, exist_ok=True)
    path = qdir / f"{arc_id}.json"
    # arc_type present so the U-HE-19 bootstrap reserve at drain succeeds
    path.write_text(json.dumps({"pr": pr, "arc_id": arc_id, "arc_type": "inventing"}))
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
    _append_unfenced(_merged_row())
    with pytest.raises(am.AbortError) as exc:
        _append_unfenced(_merged_row())
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
    _append_unfenced(_merged_row())
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
    _append_unfenced(_merged_row("pr-1338", 1338))
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
    _append_unfenced(_merged_row("pr-1338", 1338))
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
    a.write_text("x\ncodex-review: BLOCK\n")
    b.write_text("y\ncodex-review: APPROVE\n")
    os.utime(a, (1_000_000, 1_000_000))
    os.utime(b, (1_000_600, 1_000_600))
    logs, gaps, _, _ = am.round_metrics([str(tmp_path / "r*.log"), str(tmp_path / "r1*.log")])
    assert len(logs) == 2, "the same file matched twice is still one round"
    assert gaps == [600.0], "and introduces no spurious zero-second gap"


def _round_log(tmp_path: Path, name: str, text: str, mtime: int) -> Path:
    f = tmp_path / name
    f.write_text(text)
    os.utime(f, (mtime, mtime))
    return f


# ── C-HE-25 v1.6 X6c: rounds derive from log CONTENT, never file position (U-HE-46) ─────
# mutation-probe: number rounds by file position (mtime order + positional indices),
# or count GATE_REFUSED transcripts as rounds -> red
def test_round_derivation_from_content_not_file_position(tmp_path: Path):
    """[B] F15 witness: the landed u-he-35 round-dir shape is 10 rounds, P1s at r1+r10.

    The 12-file directory (r1..r11.log + r9-verdict.log) carries two GATE_REFUSED
    transcripts (r9: SWEEP_MISSING; r11: BUDGET_EXHAUSTED) and r9's retry under the
    fresh per-attempt name. File-position derivation read it as the corrupted
    ``review_rounds: 12`` with ``p1_rounds: [1, 11]``.
    """
    block = "codex-review: BLOCK\n"
    p1 = "- [P1] tools/x.py:1: a real finding\n"
    t = 1_000_000
    for n in range(1, 9):  # r1..r8 real rounds; only r1 carries a P1
        _round_log(tmp_path, f"r{n}.log", (p1 if n == 1 else "") + block, t)
        t += 600
    _round_log(
        tmp_path, "r9.log", "review gate: ...\ncodex-review: GATE_REFUSED (SWEEP_MISSING)\n", t
    )
    # r9's retry publishes under a fresh name; publish-failure noise FOLLOWS the verdict
    _round_log(
        tmp_path,
        "r9-verdict.log",
        block + "round_log_publish: refused 'r9.log': destination already exists\n",
        t + 600,
    )
    _round_log(tmp_path, "r10.log", p1 + block, t + 1200)
    _round_log(tmp_path, "r11.log", "codex-review: GATE_REFUSED (BUDGET_EXHAUSTED)\n", t + 1800)

    logs, gaps, p1_rounds, round_ids = am.round_metrics([str(tmp_path / "r*.log")])
    assert len(logs) == 10, "refused launches are not rounds"
    assert p1_rounds == [1, 10], "P1s key by ROUND ID, not by position in a listing"
    assert [f.name for f in logs] == [
        *(f"r{n}.log" for n in range(1, 9)),
        "r9-verdict.log",
        "r10.log",
    ], "the retry's fresh-named log IS round 9; both refused transcripts are excluded"
    assert len(gaps) == 9, "gaps pair the 10 real rounds only"
    assert round_ids == list(range(1, 11)), (
        "the id list is the set's own testimony; labels are the classifier's"
    )


# mutation-probe: classify a suffix-only set as "complete", or grant "complete"
# without the reservation authority confirming the tail -> red
def test_completeness_labels_are_evidence_gated(monkeypatch):
    """One classifier: min>1 is the set's own proof of a missing prefix;
    "complete" needs the reservation authority to confirm the tail; anything
    the evidence cannot back is "unknown" (a lower bound, never a guess)."""
    monkeypatch.setattr(am, "_recorded_rounds", lambda arc_id: set(range(1, 11)))
    assert am._completeness_for("x", list(range(1, 11))) == "complete"
    assert am._completeness_for("x", [4, 5, 6, 7, 8, 9, 10]) == "partial-suffix", (
        "recorded rounds missing BEFORE the observed start are a lost prefix, not corruption"
    )
    with pytest.raises(am.AbortError, match=r"round\(s\) \[4, 5, 6, 7, 8, 9, 10\]"):
        am._completeness_for("x", [1, 2, 3])  # a surviving prefix hides a recorded tail
    with pytest.raises(am.AbortError, match=r"round\(s\) \[10\]"):
        # round 10 is recorded, so a transcript that reads refused for it is
        # forged or mangled -- the round cannot be silently discarded
        am._completeness_for("x", list(range(1, 10)))

    monkeypatch.setattr(am, "_recorded_rounds", lambda arc_id: set())
    assert am._completeness_for("x", list(range(1, 11))) == "unknown", (
        "no authority is never 'complete'"
    )
    monkeypatch.setattr(am, "_recorded_rounds", lambda arc_id: set(range(1, 8)))
    assert am._completeness_for("x", list(range(1, 11))) == "unknown", (
        "an under-recording authority (fallback-id rounds) cannot confirm the tail"
    )


def test_suffix_only_set_is_classified_partial_and_reaches_the_snapshot(
    monkeypatch, tmp_path: Path
):
    """queue_capture carries the classifier's label into the snapshot, so the
    row cannot ride the schema's "complete" default into exact cohort medians."""
    logs = tmp_path / "logs"
    logs.mkdir()
    _round_log(logs, "r8.log", "codex-review: BLOCK\n", 1_000_000)
    _round_log(logs, "r9.log", "codex-review: BLOCK\n", 1_000_600)
    _round_log(logs, "r10.log", "codex-review: APPROVE\n", 1_001_200)
    _, _, _, round_ids = am.round_metrics([str(logs / "r*.log")])
    assert round_ids == [8, 9, 10]

    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(am, "_recorded_rounds", lambda arc_id: set(range(1, 11)))
    am.queue_capture(
        am.argparse.Namespace(
            pr=1999,
            arc_id=None,
            arc_type="applying",
            decisions=0,
            round_logs=[str(logs / "r*.log")],
            levers=None,
            notes="",
        )
    )
    snap = json.loads((qdir / "pr-1999.json").read_text())["round_snapshot"]
    assert snap["round_completeness"] == "partial-suffix"


# mutation-probe: drop the snapshot round_completeness read in extract() -> red
def test_extract_carries_snapshot_completeness_and_defaults_legacy(monkeypatch):
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 10,
            "deletions": 0,
            "changedFiles": 1,
            "commits": [{}],
            "createdAt": "2026-08-14T09:00:00Z",
            "mergedAt": None,
            "mergeCommit": None,
            "title": "t",
        },
    )
    snapshot = {
        "review_rounds": 3,
        "round_wall_s": [600.0, 600.0],
        "p1_rounds": [],
        "first_round_at": "2026-08-14T11:00:00+00:00",
        "last_round_at": "2026-08-14T11:20:00+00:00",
        "round_log_source": "/tmp/logs",
        "round_completeness": "partial-suffix",
    }
    args = dict(
        pr=999, arc_id=None, arc_type=None, decisions=None, round_logs=None, levers=None, notes=""
    )
    row = am.extract(am.argparse.Namespace(**args, round_snapshot=snapshot))
    assert row.round_completeness == "partial-suffix"

    # Pre-X6c snapshots were computed positionally over arbitrary surviving
    # subsets -- their stored counts and gaps may themselves be corrupt, so no
    # legacy shape earns anything but "unknown" (not even a suffix bound).
    legacy = {k: v for k, v in snapshot.items() if k != "round_completeness"}
    legacy["matched"] = ["/x/r8.log", "/x/r9.log", "/x/r10.log"]
    row = am.extract(am.argparse.Namespace(**args, round_snapshot=legacy))
    assert row.round_completeness == "unknown"

    del legacy["matched"]
    row = am.extract(am.argparse.Namespace(**args, round_snapshot=legacy))
    assert row.round_completeness == "unknown", "no evidence is never a claim of completeness"


def test_reviewer_unavailable_is_a_round_and_any_wrapper_label_counts(tmp_path: Path):
    """The C-HE-25 per-round terminal enum includes REVIEWER_UNAVAILABLE.

    A failover transcript carries the primary's REVIEWER_UNAVAILABLE terminal
    and then the verdict that stands under the ``gemini-review (failover)``
    label (codex_review._report); both shapes classify as rounds, and the
    failover line — the LAST matching terminal — is the one read. (agy_review's
    standalone ``VERDICT:`` dialect is not a round-log producer; such a
    transcript aborts as terminal-less by design.)
    """
    _round_log(
        tmp_path, "r1.log", "codex-review: REVIEWER_UNAVAILABLE (transient: timeout)\n", 1_000_000
    )
    _round_log(
        tmp_path,
        "r2.log",
        "codex-review: REVIEWER_UNAVAILABLE (permanent: no binary)\n"
        "gemini-review (failover): BLOCK\n",
        1_000_600,
    )
    logs, _, _, _ = am.round_metrics([str(tmp_path / "r*.log")])
    assert len(logs) == 2


def test_two_real_transcripts_claiming_one_round_abort(tmp_path: Path):
    _round_log(tmp_path, "r3.log", "codex-review: BLOCK\n", 1_000_000)
    _round_log(tmp_path, "r3-verdict.log", "codex-review: APPROVE\n", 1_000_600)
    with pytest.raises(am.AbortError, match="claim round 3"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_terminal_less_transcript_aborts_rather_than_classifying(tmp_path: Path):
    _round_log(tmp_path, "r1.log", "some partial output with no verdict\n", 1_000_000)
    with pytest.raises(am.AbortError, match="no wrapper terminal line"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_refused_attempt_beside_real_retry_collapses_to_one_round(tmp_path: Path):
    """merge-gate witness lens (PR #1471): the headline X6b claim — a
    GATE_REFUSED-terminal attempt beside its real-terminal retry is ONE round,
    keyed to the retry's transcript — exercised directly through round_metrics
    (the GATE_REFUSED filter is a different branch than the terminal-less one)."""
    _round_log(tmp_path, "r1-a1.log", "codex-review: GATE_REFUSED (SWEEP_MISSING)\n", 1_000_000)
    _round_log(tmp_path, "r1-a2.log", "codex-review: BLOCK\n", 1_000_600)
    logs, _, _, ids = am.round_metrics([str(tmp_path / "r*.log")])
    assert [f.name for f in logs] == ["r1-a2.log"]
    assert ids == [1]


def test_terminal_less_attempt_beside_terminal_bearing_retry_is_excluded(tmp_path: Path):
    """U-HE-49 codex r2: the wrapper crashed/was killed mid-attempt, so the
    write-once r1-a1.log carries no terminal; the retry published r1-a2.log.
    The partial file is a FAILED attempt of a classifiable round — excluded like
    a refused launch, never a poisoned evidence set."""
    _round_log(tmp_path, "r1-a1.log", "partial transcript, wrapper killed\n", 1_000_000)
    _round_log(tmp_path, "r1-a2.log", "codex-review: BLOCK\n", 1_000_600)
    logs, _, _, ids = am.round_metrics([str(tmp_path / "r*.log")])
    assert [f.name for f in logs] == ["r1-a2.log"]
    assert ids == [1]


def test_lone_terminal_less_attempt_still_aborts(tmp_path: Path):
    """Without a terminal-bearing sibling, a crashed attempt and a truncated
    REAL round read identically — refuse rather than undercount."""
    _round_log(tmp_path, "r1-a1.log", "partial transcript, wrapper killed\n", 1_000_000)
    _round_log(tmp_path, "r2-a1.log", "codex-review: BLOCK\n", 1_000_600)
    with pytest.raises(am.AbortError, match="no wrapper terminal line"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_foreign_terminal_less_name_beside_real_attempt_aborts(tmp_path: Path):
    """codex r3: a terminal-less file OUTSIDE the minted r<N>-a<K> sequence
    (`r1-notes.log`) is foreign evidence, never a suppressible failed attempt."""
    _round_log(tmp_path, "r1-notes.log", "scratch notes, no verdict\n", 1_000_000)
    _round_log(tmp_path, "r1-a1.log", "codex-review: BLOCK\n", 1_000_600)
    with pytest.raises(am.AbortError, match="foreign or contradictory"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_foreign_attempt_suffixed_name_beside_real_attempt_aborts(tmp_path: Path):
    """codex r4: a foreign name that HAPPENS to end in -a<K> (`r1-notes-a1.log`)
    is not in the real attempt's minted family (stem minus suffix differs) —
    the K-ordering check alone must not suppress it."""
    _round_log(tmp_path, "r1-notes-a1.log", "scratch notes, no verdict\n", 1_000_000)
    _round_log(tmp_path, "r1-a2.log", "codex-review: BLOCK\n", 1_000_600)
    with pytest.raises(am.AbortError, match="foreign or contradictory"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_all_foreign_attempt_family_aborts_not_self_suppresses(tmp_path: Path):
    """codex r7: a foreign family can be internally consistent — terminal-less
    `r1-notes-a1.log` beside terminal-bearing `r1-notes-a2.log` — but launch()
    only mints the canonical `r<rid>-a<K>.log`, so suppression requires the
    canonical base on BOTH sides."""
    _round_log(tmp_path, "r1-notes-a1.log", "partial, foreign family\n", 1_000_000)
    _round_log(tmp_path, "r1-notes-a2.log", "codex-review: BLOCK\n", 1_000_600)
    with pytest.raises(am.AbortError, match="foreign or contradictory"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_non_minted_attempt_suffix_is_foreign_not_an_earlier_attempt(tmp_path: Path):
    """codex r5: attempt_destination only mints positive canonical decimals, so a
    terminal-less `r1-a0.log` (or `-a01`) is foreign evidence — it must not pass
    the same-family ordering check as an 'earlier attempt'."""
    _round_log(tmp_path, "r1-a0.log", "partial, non-minted suffix\n", 1_000_000)
    _round_log(tmp_path, "r1-a1.log", "codex-review: BLOCK\n", 1_000_600)
    with pytest.raises(am.AbortError, match="foreign or contradictory"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_terminal_less_attempt_minted_after_completed_round_aborts(tmp_path: Path):
    """codex r3: a crashed r1-a2 AFTER r1-a1 completed is contradictory (the
    launch guard refuses retrying a recorded round) — expose it, don't suppress."""
    _round_log(tmp_path, "r1-a1.log", "codex-review: BLOCK\n", 1_000_000)
    _round_log(tmp_path, "r1-a2.log", "partial transcript, wrapper killed\n", 1_000_600)
    with pytest.raises(am.AbortError, match="foreign or contradictory"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_unparseable_round_name_aborts(tmp_path: Path):
    _round_log(tmp_path, "final.log", "codex-review: APPROVE\n", 1_000_000)
    with pytest.raises(am.AbortError, match="cannot parse a round id"):
        am.round_metrics([str(tmp_path / "*.log")])


def test_internal_round_id_gap_aborts_rather_than_undercounting(tmp_path: Path):
    """r1 + r3 with r2 missing is a broken evidence set, not a two-round arc."""
    _round_log(tmp_path, "r1.log", "codex-review: BLOCK\n", 1_000_000)
    _round_log(tmp_path, "r3.log", "codex-review: APPROVE\n", 1_000_600)
    with pytest.raises(am.AbortError, match=r"round id\(s\) 2 are missing"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_gap_detection_never_materializes_the_id_range(tmp_path: Path):
    """Filename ids are caller-controlled input; r1 + r100000000 must refuse as
    a span, not build a hundred-million-element set."""
    _round_log(tmp_path, "r1.log", "codex-review: BLOCK\n", 1_000_000)
    _round_log(tmp_path, "r100000000.log", "codex-review: APPROVE\n", 1_000_600)
    with pytest.raises(am.AbortError, match=r"round id\(s\) 2-99999999 are missing"):
        am.round_metrics([str(tmp_path / "r*.log")])


# mutation-probe: drop the recorded-but-unclassified refusal in _completeness_for -> red
def test_surviving_prefix_is_refused_when_the_reservation_recorded_more_rounds(
    monkeypatch, tmp_path: Path
):
    """r1..r3 of an arc whose reservation accreted rounds through 10 is a
    missing-tail evidence set, not a complete three-round arc."""
    logs = tmp_path / "logs"
    logs.mkdir()
    for n in (1, 2, 3):
        _round_log(logs, f"r{n}.log", "codex-review: BLOCK\n", 1_000_000 + n * 600)
    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    ns = dict(
        pr=1998,
        arc_id=None,
        arc_type="applying",
        decisions=0,
        round_logs=[str(logs / "r*.log")],
        levers=None,
        notes="",
    )
    # Authority through the REAL union: the reservation half is empty (the
    # best-effort recorder failed), and the fail-closed gate log alone carries
    # the recorded rounds -- dropping the gate-log half of _recorded_rounds
    # makes both arms below misbehave (no abort; then no "complete").
    monkeypatch.setattr(am, "_reservation_recorded_rounds", lambda arc_id: set())
    gate = tmp_path / "gate.jsonl"
    gate.write_text(
        "".join(
            json.dumps({"arc_id": "pr-1998", "round_n": n, "producer": "codex_review_wrapper"})
            + "\n"
            for n in range(1, 11)
        )
    )
    monkeypatch.setattr(am, "GATE_LOG", gate)
    with pytest.raises(am.AbortError, match="no surviving log classifies"):
        am.queue_capture(am.argparse.Namespace(**ns))

    # Authority-confirmed tail (recorded == observed) passes as "complete".
    gate.write_text(
        "".join(
            json.dumps({"arc_id": "pr-1998", "round_n": n, "producer": "codex_review_wrapper"})
            + "\n"
            for n in (1, 2, 3)
        )
    )
    assert am.queue_capture(am.argparse.Namespace(**ns)) == 0
    snap = json.loads((qdir / "pr-1998.json").read_text())["round_snapshot"]
    assert snap["round_completeness"] == "complete"


# mutation-probe: drop the gate-log half of _recorded_rounds -> red
def test_recorded_rounds_unions_the_fail_closed_gate_log(monkeypatch, tmp_path: Path):
    """The reservation recorder is best-effort (its writer swallows persistence
    failures); the C-HE-24 gate log is write-first. A round present only in the
    gate log must still count as recorded."""
    import reservations as rs

    gate = tmp_path / "gate.jsonl"
    rows = [
        {"arc_id": "x", "round_n": 10, "producer": "codex_review_wrapper"},
        {"arc_id": "other", "round_n": 3, "producer": "codex_review_wrapper"},
        {"arc_id": "x", "producer": "codex_review_wrapper"},  # no round_n
        # Mixed-producer witness: lens/probe rows number their OWN round
        # spaces -- an unrelated r1/r2 here must neither certify nor abort
        # the review-round evidence.
        {"arc_id": "x", "round_n": 1, "producer": "merge-gate-concurrency"},
        {"arc_id": "x", "round_n": 2, "producer": "reviewer_concurrency_probe"},
        {"arc_id": "x", "round_n": 5, "producer": "gemini_review_wrapper"},
    ]
    gate.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(am, "GATE_LOG", gate)
    monkeypatch.setattr(
        rs, "current", lambda arc_id: (1, {"round_outcomes": {"1/codex": {}, "2/codex": {}}})
    )
    assert am._recorded_rounds("x") == {1, 2, 5, 10}, (
        "wrapper rounds (both channels) count; lens/probe round spaces do not"
    )
    monkeypatch.setattr(am, "GATE_LOG", tmp_path / "absent.jsonl")
    assert am._recorded_rounds("x") == {1, 2}


def test_reservation_recorded_rounds_reads_the_head_outcomes(monkeypatch):
    """Keys carry the writer's real "<round>/<channel>" shape (verified live:
    record_round_outcome_if_reserved writes {"1/codex": {...}})."""
    import reservations as rs

    outcomes = {"1/codex": {}, "10/codex": {}, "2/gemini": {}}
    monkeypatch.setattr(rs, "current", lambda arc_id: (3, {"round_outcomes": outcomes}))
    assert am._reservation_recorded_rounds("x") == {1, 2, 10}
    monkeypatch.setattr(rs, "current", lambda arc_id: None)
    assert am._reservation_recorded_rounds("x") == set()
    monkeypatch.setattr(rs, "current", lambda arc_id: (1, {"round_outcomes": {}}))
    assert am._reservation_recorded_rounds("x") == set()


def test_all_refused_launches_abort_rather_than_recording_an_empty_arc(tmp_path: Path):
    _round_log(tmp_path, "r1.log", "codex-review: GATE_REFUSED (SWEEP_MISSING)\n", 1_000_000)
    with pytest.raises(am.AbortError, match="refused launch"):
        am.round_metrics([str(tmp_path / "r*.log")])


def test_mtime_regression_against_round_id_order_aborts(tmp_path: Path):
    """A copied/re-touched log would otherwise enter round_wall_s as a negative gap."""
    _round_log(tmp_path, "r1.log", "codex-review: BLOCK\n", 1_000_600)
    _round_log(tmp_path, "r2.log", "codex-review: APPROVE\n", 1_000_000)
    with pytest.raises(am.AbortError, match="predates"):
        am.round_metrics([str(tmp_path / "r*.log")])


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


# mutation-probe: median the whole lane cohort instead of its complete rows,
# or pool an unknown row's round_wall_s into the cohort/global gap aggregates -> red
def test_lane_cohort_medians_exclude_lower_bound_rows(monkeypatch, tmp_path: Path, capsys):
    """C-HE-28 lane metrics are exact aggregates too: a partial-suffix or
    unknown row is a lower bound and must not enter the lane median -- and an
    unknown row's gaps (position-era corruption) must reach NO round-wall
    aggregate, cohort or global."""
    ledger = tmp_path / "arc-metrics.jsonl"
    rows = [
        {
            "arc_id": "a",
            "review_rounds": 4,
            "round_wall_s": [600.0],
            "levers_active": [],
            "concurrent_lanes_at_open": 1,
        },
        {"arc_id": "b", "review_rounds": 5, "levers_active": [], "concurrent_lanes_at_open": 1},
        {
            "arc_id": "frag",
            "review_rounds": 1,
            # An extreme position-era gap: visible in any aggregate it leaks into.
            "round_wall_s": [999_999.0],
            "levers_active": [],
            "concurrent_lanes_at_open": 1,
            "round_completeness": "unknown",
        },
        # A partial-suffix row is the OTHER lower-bound class: its true suffix
        # gaps pool, but its round count must stay out of the exact lane
        # median (a `!= "unknown"` filter would readmit it).
        {
            "arc_id": "sfx",
            "review_rounds": 2,
            "round_wall_s": [1200.0],
            "levers_active": [],
            "concurrent_lanes_at_open": 1,
            "round_completeness": "partial-suffix",
        },
    ]
    ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(am, "LEDGER", ledger)
    am.summary(am.argparse.Namespace())
    out = capsys.readouterr().out
    # stored value 1 is ONE SIBLING, i.e. 2 lanes (`lanes_at_open` = siblings + 1).
    lanes = out[out.index("-- LANES [lanes_at_open=2]") :]
    assert "review rounds    4.5 (n=2" in lanes, (
        "median of [4,5]; both the unknown AND the partial-suffix row are out"
    )
    assert "2 lower-bound row(s) excluded" in lanes
    # 999999s = 16666.6m: the corrupt unknown gap must appear nowhere -- not in
    # the cohort round-wall line, not in the closing global variance spread --
    # while the partial-suffix row's 1200s gap DOES pool (a true measurement of
    # its surviving suffix).
    assert "16666" not in out
    assert "15.0m (n=2, 10.0-20.0)" in out, "the partial-suffix row's true 1200s gap pools"


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


# mutation-probe: point QUEUE_DIR's home-default arm at a path inside the repo
def test_queue_lives_outside_the_repo():
    """A topic worktree is disposed at loop completion; anything queued in it dies.

    Checked through an isolated import with the queue variable UNSET: under a tools
    session the conftest belt owns `ARC_METRICS_QUEUE_DIR` before collection, so this
    process's own `am.QUEUE_DIR` always carries the belt — never the production
    default this test exists to pin (codex rounds 3-5 on the skills PR: mutating the
    default to a repo-resident path left the in-process assertion green).
    """
    # [LAW:verifiable-goals] the witness must see the mechanism — the import-time
    # default with the variable absent — not the session belt that shadows it.
    probe = (
        "import json, arc_metrics as am\n"
        "print(json.dumps({'queue': str(am.QUEUE_DIR), 'repo': str(am.REPO)}))\n"
    )
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("ARC_METRICS_QUEUE_DIR", "ARC_METRICS_QUEUE_DIR_PREBELT")
    }
    out = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
        cwd=Path(am.__file__).resolve().parent,
        env=env,
    ).stdout
    got = json.loads(out)
    queue, repo = Path(got["queue"]), Path(got["repo"])
    assert repo not in queue.parents and queue != repo, (
        f"default queue {queue} must not sit inside the repo, or arc closure "
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
    a.write_text("[P1] a real finding\ncodex-review: BLOCK\n")
    b.write_text("clean\ncodex-review: APPROVE\n")
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
    monkeypatch.setattr(am, "read_queue", lambda invalid=None: stale_listing)

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
    # A SYSTEMIC fault (permission/I/O, C-HE-04 SS3) keeps its OSError identity so
    # drain() can abort the whole loop once -- it must not be softened per-arc.
    with pytest.raises(PermissionError):
        am._claim_arc(path, entry)

    def transient(*_a, **_k):
        raise OSError(24, "too many open files")  # EMFILE: per-arc, not systemic

    monkeypatch.setattr(Path, "open", transient)
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
    # 2 raw -> 1 true
    a.write_text("[P1] a real finding\n[P1] a real finding\ncodex-review: BLOCK\n")
    b.write_text("no findings here\ncodex-review: APPROVE\n")  # 0
    os.utime(a, (1_000_000, 1_000_000))
    os.utime(b, (1_000_600, 1_000_600))
    logs, gaps, p1, _ = am.round_metrics([str(tmp_path / "r*.log")])
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
        # Row "a" above has the key ABSENT; this one CARRIES an explicit null. The
        # spec's Verification bullet asks that the split group "without error on
        # `null`", so the null case needs a row that actually holds one — before
        # U-HE-38 this test asserted the null label against an absent-key row, which
        # is the conflation itself.
        {
            "arc_id": "c",
            "levers_active": [],
            "arc_span_s": 180.0,
            "review_rounds": 3,
            "round_completeness": "complete",
            "concurrent_lanes_at_open": None,
        },
    ]
    ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    monkeypatch.setattr(am, "LEDGER", ledger)
    assert am.summary(argparse.Namespace()) == 0
    out = capsys.readouterr().out
    # C-HE-25: a row lacking the KEY predates the field and IS the N=1 baseline
    # (C-HE-28 §3 places 18 such rows at N=1). Only an explicit null is an unknown.
    assert "LANES [lanes_at_open=1] (n=1)" in out, "absent key -> the 1-lane baseline"
    assert "LANES [lanes_at_open=null] (n=1)" in out, "explicit null stays unknown"
    # row "b" stores 2 SIBLINGS, which is 3 lanes.
    assert "LANES [lanes_at_open=3] (n=1)" in out
    assert "lanes_at_open=None" not in out


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
    _append_unfenced(row)
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
    _append_unfenced(am.ArcRow(arc_id="pr-2", merged_at="2026-08-18T00:00:00Z", merge_sha="y"))
    am.relabel_arc_type_close("pr-2", "applying")
    lines = ledger.read_text().splitlines()
    assert lines[0] == json.dumps(other, sort_keys=True)
    assert json.loads(lines[1])["arc_type_close"] == "applying"


def test_extract_records_which_side_declared_the_label(monkeypatch):
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


# mutation-probe: drop the `if current != snapshot:` abort in relabel_arc_type_close()
def test_relabel_aborts_when_the_ledger_changed_underneath(monkeypatch, tmp_path: Path):
    """A concurrent append between the read and the replace is NOT discarded (codex R2 P2):
    the relabel detects the changed bytes, writes nothing, and the appended row survives."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    _append_unfenced(am.ArcRow(arc_id="pr-1", merged_at="2026-08-18T00:00:00Z", merge_sha="a"))
    real_read = am.read_ledger

    def read_then_concurrent_append():
        rows = real_read()
        with ledger.open("a") as fh:  # another session's drain lands mid-relabel
            fh.write(json.dumps({"arc_id": "pr-2", "record_kind": "arc"}, sort_keys=True) + "\n")
        return rows

    monkeypatch.setattr(am, "read_ledger", read_then_concurrent_append)
    with pytest.raises(am.AbortError, match="ledger changed"):
        am.relabel_arc_type_close("pr-1", "applying")
    monkeypatch.setattr(am, "read_ledger", real_read)
    rows = am.read_ledger()
    assert [r["arc_id"] for r in rows] == ["pr-1", "pr-2"]
    assert rows[0].get("arc_type_close") is None  # nothing written
    assert not list(tmp_path.glob(".l.jsonl.*.tmp"))
    am.relabel_arc_type_close("pr-1", "applying")  # the retry succeeds
    assert am.read_ledger()[0]["arc_type_close"] == "applying"


# mutation-probe: drop the `claim_ledger(LEDGER)` line in append()
def test_append_and_relabel_are_mutually_exclusive_by_claim(monkeypatch, tmp_path: Path):
    """codex R3 P2: the two ledger writers exclude each other through the CAS claim file (no
    flock here, C-HE-02 §1); a live claim aborts the other writer loudly, a dead owner's claim
    is reclaimed, and the claim never outlives its writer."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "QUEUE_DIR", tmp_path / "queue")
    _append_unfenced(am.ArcRow(arc_id="pr-1", merged_at="2026-08-18T00:00:00Z", merge_sha="a"))
    claim = am._ledger_claim_path(ledger)
    # C-HE-02 §2: the claim is QUEUE_DIR-adjacent, never beside the (REPO-resident) ledger
    assert claim.parent == tmp_path / "queue" and not claim.exists()
    assert am._ledger_claim_path(tmp_path / "other.jsonl") != claim  # keyed per ledger path
    # a LIVE claim (this process) blocks both writers
    am.publish_exclusive(
        claim, json.dumps({"_claim": {"pid": os.getpid(), "host": socket.gethostname()}})
    )
    with pytest.raises(am.AbortError, match="claimed by another writer"):
        _append_unfenced(am.ArcRow(arc_id="pr-2", merged_at="2026-08-18T00:00:00Z", merge_sha="b"))
    with pytest.raises(am.AbortError, match="claimed by another writer"):
        am.relabel_arc_type_close("pr-1", "applying")
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-1"]
    claim.unlink()
    # a DEAD owner's claim (this host) is reclaimed once and the write proceeds
    am.publish_exclusive(
        claim, json.dumps({"_claim": {"pid": 2**22 + 12345, "host": socket.gethostname()}})
    )
    am.relabel_arc_type_close("pr-1", "applying")
    assert am.read_ledger()[0]["arc_type_close"] == "applying" and not claim.exists()
    # a foreign-host claim is never reclaimed (cannot tell) -> abort
    am.publish_exclusive(claim, json.dumps({"_claim": {"pid": 1, "host": "other-host"}}))
    with pytest.raises(am.AbortError, match="claimed by another writer"):
        _append_unfenced(am.ArcRow(arc_id="pr-3", merged_at="2026-08-18T00:00:00Z", merge_sha="c"))
    claim.unlink()
    # the claim is released even when the write aborts inside it
    with pytest.raises(am.AbortError, match="already in ledger"):
        _append_unfenced(am.ArcRow(arc_id="pr-1", merged_at="2026-08-18T00:00:00Z", merge_sha="a"))
    assert not claim.exists()


# mutation-probe: drop the `if moved != judged:` restore-and-refuse branch in _reclaim_dead_claim()
def test_dead_claim_reclaim_never_steals_a_peers_fresh_live_claim(monkeypatch, tmp_path: Path):
    """codex R8 P2: two writers judge the same claim dead; A reclaims and publishes its LIVE
    claim; B must not remove A's. B moves the file aside and re-reads it: not the bytes it
    judged -> restored, B aborts, A's claim stands."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "QUEUE_DIR", tmp_path / "queue")
    (tmp_path / "queue").mkdir()
    claim = am._ledger_claim_path(ledger)
    dead = json.dumps({"_claim": {"pid": 2**22 + 4242, "host": socket.gethostname()}})
    live = json.dumps({"_claim": {"pid": os.getpid(), "host": socket.gethostname()}})
    am.publish_exclusive(claim, dead)
    real_dead = am._claim_owner_is_dead

    def judged_dead_then_peer_reclaims_and_publishes(path):
        verdict = real_dead(path)  # True: the stamp is dead
        claim.write_text(live)  # ...but peer A reclaimed + published ITS live claim meanwhile
        return verdict

    monkeypatch.setattr(am, "_claim_owner_is_dead", judged_dead_then_peer_reclaims_and_publishes)
    with pytest.raises(am.AbortError, match="claimed by another writer"):
        _append_unfenced(am.ArcRow(arc_id="pr-1", merged_at="2026-08-18T00:00:00Z", merge_sha="a"))
    assert claim.read_text() == live  # A's claim survived, byte-identical
    assert not list((tmp_path / "queue").glob(".ledger-claim-*.dead.*"))
    assert not ledger.exists()


def test_relabel_cli_is_wired(monkeypatch, tmp_path: Path, capsys):
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    _append_unfenced(am.ArcRow(arc_id="pr-3", merged_at="2026-08-18T00:00:00Z", merge_sha="z"))
    assert am.main(["relabel", "--arc-id", "pr-3", "--arc-type-close", "inventing"]) == 0
    assert am.read_ledger()[0]["arc_type_close"] == "inventing"
    assert am.main(["relabel", "--arc-id", "pr-3", "--arc-type-close", "inventing"]) == 0
    assert len(am.read_ledger()) == 1


# ─── U-HE-15: drain fault isolation + capture durability (C-HE-04 §1/§3/§4/§7) ──


def _queue_entries(am_mod, tmp_path, monkeypatch, n):
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am_mod, "QUEUE_DIR", q)
    monkeypatch.setattr(am_mod, "LEDGER", tmp_path / "l.jsonl")
    for i in range(1, n + 1):
        (q / f"pr-{i}.json").write_text(
            json.dumps({"pr": i, "arc_id": f"pr-{i}", "arc_type": "inventing", "decisions": 1})
        )
    return q


# mutation-probe: remove the `except AbortError` clause in drain()'s loop (let the exception escape)
def test_drain_fault_isolation(tmp_path, monkeypatch):
    """Entry 1 raises INSIDE _claim_arc; entries 2..n are still processed (C-HE-04 §3)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 3)
    real_claim = am._claim_arc

    def boom(path, entry):
        if entry["pr"] == 1:
            raise am.AbortError("cannot claim pr-1: injected")
        return real_claim(path, entry)

    monkeypatch.setattr(am, "_claim_arc", boom)
    monkeypatch.setattr(am, "committed_arc_ids", set)
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id=a.arc_id,
            pr=a.pr,
            merged_at="2026-08-19T00:00:00Z",
            merge_sha="abc123def4567890abc123def4567890abc123de",
        ),
    )
    rc = am.drain(argparse.Namespace())
    ledger = [r["arc_id"] for r in am.read_ledger()]
    assert ledger == ["pr-2", "pr-3"], "the fault in pr-1 must not abandon pr-2/pr-3"
    assert rc == 1  # pr-1 kept; two appended rows are held pending commit
    assert (q / "pr-1.json").exists(), "the faulted entry stays queued for retry"


def test_drain_systemic_oserror_aborts_once(tmp_path, monkeypatch, capsys):
    """A queue-dir permission fault aborts the loop with ONE message (C-HE-04 §3)."""
    _queue_entries(am, tmp_path, monkeypatch, 3)

    def perm(path, entry):
        raise PermissionError(13, "queue dir read-only")

    monkeypatch.setattr(am, "_claim_arc", perm)
    monkeypatch.setattr(am, "committed_arc_ids", set)
    rc = am.drain(argparse.Namespace())
    out = capsys.readouterr()
    assert rc == 2
    # Count the full marker phrase: tmp_path embeds this test's own name, which
    # itself contains "systemic" -- the bare token would self-match via QUEUE_DIR.
    n = (out.out + out.err).count("ABORT: systemic queue fault")
    assert n == 1, "one abort message, no per-entry repeats"


def test_recover_dead_claims_fnf_guarded(tmp_path, monkeypatch):
    """A peer restoring the same dead claim first must not raise (C-HE-04 §1)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    taken = q / "pr-7.taken"
    taken.write_text(json.dumps({"pr": 7, "_claim": {"pid": 999999, "host": socket.gethostname()}}))
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    real_rename = os.rename

    def peer_restored_first(src, dst):
        # The real race (C-HE-04 SS1): a peer's _recover_dead_claims restored the
        # entry (json published, .taken gone) between our scan and the move-aside
        # rename -- the losing racer's rename raises FNF and must log-and-yield.
        (q / "pr-7.json").write_text(json.dumps({"pr": 7}))
        Path(src).unlink()
        return real_rename(src, dst)  # raises FileNotFoundError

    monkeypatch.setattr(am.os, "rename", peer_restored_first)
    am._recover_dead_claims()  # must NOT raise
    assert (q / "pr-7.json").exists(), "the capture is held by the winning racer"


def test_recover_dead_claims_systemic_fault_aborts_drain(tmp_path, monkeypatch, capsys):
    """A systemic queue-dir fault during pre-loop recovery aborts drain with the same
    single message + exit 2 as an in-loop systemic fault -- never a raw traceback."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    taken = q / "pr-7.taken"
    taken.write_text(json.dumps({"pr": 7, "_claim": {"pid": 999999, "host": socket.gethostname()}}))
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)

    def perm(src, dst):
        raise PermissionError(13, "queue dir read-only")

    monkeypatch.setattr(am.os, "link", perm)  # recovery's restore is an exclusive link
    rc = am.drain(argparse.Namespace())
    out = capsys.readouterr()
    assert rc == 2
    assert (out.out + out.err).count("ABORT: systemic queue fault") == 1


def test_read_queue_skips_an_entry_a_peer_released_mid_scan(tmp_path, monkeypatch):
    """FNF between the glob and the read = no longer pending; skipped, never raised."""
    _queue_entries(am, tmp_path, monkeypatch, 2)
    real_read = Path.read_text

    def vanish_first(self, *a, **k):
        if self.name == "pr-1.json":
            self.unlink()
            raise FileNotFoundError(str(self))
        return real_read(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", vanish_first)
    assert [e["arc_id"] for _p, e in am.read_queue()] == ["pr-2"]


def test_read_queue_systemic_fault_aborts_drain_once(tmp_path, monkeypatch, capsys):
    """A permission fault reading the queue aborts with ONE message + exit 2."""
    _queue_entries(am, tmp_path, monkeypatch, 2)

    def perm(self, *a, **k):
        raise PermissionError(13, "queue dir unreadable")

    monkeypatch.setattr(Path, "read_text", perm)
    monkeypatch.setattr(am.os, "access", lambda *a, **k: False)  # the DIR itself unreadable
    rc = am.drain(argparse.Namespace())
    out = capsys.readouterr()
    assert rc == 2
    assert (out.out + out.err).count("ABORT: systemic queue fault") == 1


def test_malformed_entry_is_kept_and_does_not_abort_the_loop(tmp_path, monkeypatch):
    """Valid JSON with missing fields is a per-arc content fault (C-HE-04 SS3)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 2)
    (q / "pr-0.json").write_text(json.dumps({"note": "no pr field"}))  # sorts first
    monkeypatch.setattr(am, "committed_arc_ids", set)
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id=a.arc_id,
            pr=a.pr,
            merged_at="2026-08-19T00:00:00Z",
            merge_sha="abc123def4567890abc123def4567890abc123de",
        ),
    )
    rc = am.drain(argparse.Namespace())
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-1", "pr-2"]
    assert rc == 1 and (q / "pr-0.json").exists(), "malformed entry kept, others drained"


def test_recovery_rejudges_after_move_aside_and_returns_a_live_reclaim(tmp_path, monkeypatch):
    """Between the liveness check and the restore a live drain re-claims under the
    same .taken name: recovery must put the LIVE claim straight back (C-HE-04 SS1)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    taken = q / "pr-7.taken"
    taken.write_text(json.dumps({"pr": 7, "_claim": {"pid": 999999, "host": socket.gethostname()}}))
    live = json.dumps({"pr": 7, "_claim": {"pid": os.getpid(), "host": socket.gethostname()}})
    real_dead = am._claim_owner_is_dead
    calls = {"n": 0}

    def dead_then_restamped(path):
        calls["n"] += 1
        if calls["n"] == 1:
            verdict = real_dead(path)  # True: the on-disk stamp is dead
            taken.write_text(live)  # ...but a live drain re-claims the NAME now
            return verdict
        return real_dead(path)  # re-judge of the moved bytes

    monkeypatch.setattr(am, "_claim_owner_is_dead", dead_then_restamped)
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: pid == os.getpid())
    am._recover_dead_claims()
    # The restamp landed before the rename, so the aside held LIVE bytes; the
    # re-judge must return them to the .taken name untouched -- a live claim is
    # never yanked to .json (the pathname-keyed-replace defect this pins).
    assert taken.exists(), "the live claim is back under its name"
    assert json.loads(taken.read_text())["_claim"]["pid"] == os.getpid()
    assert not (q / "pr-7.json").exists(), "no restore of a live claim"
    assert not list(q.glob("*.taken.recover.*")), "no aside left behind"


def test_recovery_restores_an_orphaned_aside_from_a_dead_recoverer(tmp_path, monkeypatch):
    """A recoverer that died between rename-aside and restore must not strand the arc."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    (q / f"pr-7.taken.recover.{socket.gethostname()}.999999").write_text(
        json.dumps({"pr": 7, "_claim": {"pid": 999998, "host": socket.gethostname()}})
    )
    # A FOREIGN-host recoverer's aside is unjudgeable from here: left alone.
    (q / "pr-8.taken.recover.elsewhere.invalid.999999").write_text(
        json.dumps({"pr": 8, "_claim": {"pid": 999998, "host": "elsewhere.invalid"}})
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    am._recover_dead_claims()
    assert (q / "pr-7.json").exists(), "orphaned aside restored to the queue"
    assert not (q / "pr-8.json").exists(), "foreign-host aside never judged dead"
    assert list(q.glob("*.taken.recover.*")) == [q / "pr-8.taken.recover.elsewhere.invalid.999999"]


# mutation-probe: comment out the `except FileExistsError` drop-stale tail in _restore_or_republish
def test_restore_never_clobbers_a_newer_requeue(tmp_path, monkeypatch):
    """While an arc is claimed its .json name is free; a concurrent re-queue that
    published UPDATED declarations there must survive the stale restore (C-HE-04 SS4)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    stale = {"pr": 3, "arc_id": "pr-3", "decisions": 1}
    taken = q / "pr-3.taken"
    taken.write_text(json.dumps({**stale, "_claim": {"pid": os.getpid(), "host": "h"}}))
    newer = json.dumps({"pr": 3, "arc_id": "pr-3", "decisions": 9, "notes": "corrected"})
    (q / "pr-3.json").write_text(newer)  # concurrent queue_capture during the claim window
    am._restore_or_republish(taken, q / "pr-3.json", stale)
    assert (q / "pr-3.json").read_text() == newer, "newer capture survives"
    assert not taken.exists(), "the stale claimed copy is dropped"


def test_malformed_entry_after_claim_restores_before_kept(tmp_path, monkeypatch):
    """A field fault surfacing AFTER the claim (Namespace construction) must restore
    the entry -- never leave a wedged .taken under a live pid (codex r4 P2)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "committed_arc_ids", set)
    # arc_id present (so the pre-claim derivation succeeds); pr missing (raises
    # KeyError in the post-claim Namespace construction).
    (q / "pr-4.json").write_text(json.dumps({"arc_id": "pr-4"}))
    rc = am.drain(argparse.Namespace())
    assert rc == 1
    assert (q / "pr-4.json").exists(), "entry restored despite the post-claim fault"
    assert not list(q.glob("*.taken")), "no wedged claim left behind"


def test_one_invalid_json_entry_does_not_abandon_the_rest(tmp_path, monkeypatch, capsys):
    """A truncated queue file is a per-arc content fault: reported + kept, the other
    entries still drain, and the run exits nonzero for attention (C-HE-04 SS3)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    (q / "pr-0-bad.json").write_text('{"pr": 1, TRUNC')
    (q / "pr-0-list.json").write_text("[]")  # valid JSON, not an object
    monkeypatch.setattr(am, "committed_arc_ids", set)
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id=a.arc_id,
            pr=a.pr,
            merged_at="2026-08-19T00:00:00Z",
            merge_sha="abc123def4567890abc123def4567890abc123de",
        ),
    )
    rc = am.drain(argparse.Namespace())
    err = capsys.readouterr().err
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-1"], "the valid entry drained"
    assert rc == 1
    assert (q / "pr-0-bad.json").exists() and (q / "pr-0-list.json").exists()
    assert "needs human repair" in err


def _queue_args(arc_id):
    return argparse.Namespace(
        pr=1,
        arc_id=arc_id,
        arc_type="inventing",
        decisions=1,
        round_logs=None,
        levers=None,
        notes="",
    )


def test_arc_id_length_capped_for_recovery_suffix_budget(tmp_path, monkeypatch):
    """An arc_id accepted at queue time must survive recovery's host+pid suffix --
    measured in BYTES (multi-byte UTF-8 counts), not characters."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    with pytest.raises(am.AbortError, match="too long"):
        am.queue_capture(_queue_args("x" * 300))
    with pytest.raises(am.AbortError, match="too long"):
        am.queue_capture(_queue_args("\u00e9" * 130))  # 260 bytes in 130 chars


def test_arc_id_rejects_the_reserved_taken_namespace(tmp_path, monkeypatch):
    """'.taken' inside an arc_id would collide with / misparse claim + recovery names."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    with pytest.raises(am.AbortError, match="reserved"):
        am.queue_capture(_queue_args("a.taken.recover.b"))


def test_capture_at_risk_reported_when_restore_itself_fails(tmp_path, monkeypatch, capsys):
    """If the .taken vanished AND the exclusive re-publish fails, drain must say
    CAPTURE AT RISK with the payload -- never a false KEPT QUEUED (C-HE-04 SS7)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(am, "committed_arc_ids", set)

    def steal_then_abort(a):
        (q / "pr-1.taken").unlink()
        raise am.AbortError("no round logs")

    monkeypatch.setattr(am, "extract", steal_then_abort)
    real_publish = am.publish_exclusive

    def emfile_on_republish(path, payload):
        if path.suffix == ".json":  # the restore's re-publish; the claim still works
            raise OSError(24, "EMFILE")
        return real_publish(path, payload)

    monkeypatch.setattr(am, "publish_exclusive", emfile_on_republish)
    rc = am.drain(argparse.Namespace())
    err = capsys.readouterr().err
    assert rc == 2, "a lost capture is exit 2, never a routine 'still queued' 1"
    assert "CAPTURE AT RISK" in err and '"arc_id": "pr-1"' in err
    assert "KEPT QUEUED" not in err
    assert "CAPTURE(S) AT RISK" in err, "the summary names the loss, not a false kept-count"


def test_a_directory_named_like_an_entry_is_isolated(tmp_path, monkeypatch, capsys):
    """A directory matching *.json is a per-path fault: reported + kept, rest drained."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    (q / "pr-0-dir.json").mkdir()
    monkeypatch.setattr(am, "committed_arc_ids", set)
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id=a.arc_id,
            pr=a.pr,
            merged_at="2026-08-19T00:00:00Z",
            merge_sha="abc123def4567890abc123def4567890abc123de",
        ),
    )
    rc = am.drain(argparse.Namespace())
    err = capsys.readouterr().err
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-1"]
    assert rc == 1 and "unreadable" in err


def test_rejudge_return_never_overwrites_a_newer_claim(tmp_path, monkeypatch):
    """Returning a live aside must not clobber a NEWER claim created meanwhile."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    taken = q / "pr-7.taken"
    taken.write_text(json.dumps({"pr": 7, "_claim": {"pid": 999999, "host": socket.gethostname()}}))
    newer = json.dumps({"pr": 7, "_claim": {"pid": os.getpid(), "host": socket.gethostname()}})
    live = json.dumps({"pr": 7, "_claim": {"pid": os.getpid() + 1, "host": socket.gethostname()}})
    real_dead = am._claim_owner_is_dead
    calls = {"n": 0}

    def dead_then_two_claims(path):
        calls["n"] += 1
        if calls["n"] == 1:
            verdict = real_dead(path)  # True on the on-disk dead stamp
            taken.write_text(live)  # a live drain re-claims the name...
            return verdict
        # ...and while the aside is out, ANOTHER claim lands under the name.
        if calls["n"] == 2:
            taken.write_text(newer)
        return real_dead(path)

    monkeypatch.setattr(am, "_claim_owner_is_dead", dead_then_two_claims)
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: pid in (os.getpid(), os.getpid() + 1))
    am._recover_dead_claims()
    assert json.loads(taken.read_text()) == json.loads(newer), "the newer claim survives"
    assert not list(q.glob("*.taken.recover.*")), "the displaced aside is dropped"


def test_kill_after_claim_is_wired_into_drain(tmp_path):
    """ARC_METRICS_TEST_KILL_AFTER=claim kills a REAL drain right after _claim_arc:
    exit 137, the claim held (.taken exists), the entry taken (.json gone). Witnesses
    the production call-site wiring, not just the seam helper."""
    q = tmp_path / "queue"
    q.mkdir()
    (q / "pr-1.json").write_text(
        json.dumps({"pr": 1, "arc_id": "pr-1", "arc_type": "inventing", "decisions": 1})
    )
    code = "import arc_metrics as am, argparse; am.drain(argparse.Namespace())"
    r = subprocess.run(
        [sys.executable, "-c", code],
        env={
            **os.environ,
            "PYTHONPATH": str(_TOOLS_DIR),
            "ARC_METRICS_TEST_KILL_AFTER": "claim",
            "ARC_METRICS_QUEUE_DIR": str(q),
            "ARC_METRICS_REPO": str(tmp_path),
            "ARC_METRICS_LEDGER": str(tmp_path / "l.jsonl"),
        },
        capture_output=True,
        text=True,
    )
    assert r.returncode == 137, r.stderr
    assert (q / "pr-1.taken").exists(), "killed AFTER the claim: the claim survives"
    assert not (q / "pr-1.json").exists()


# mutation-probe: replace _restore_or_republish's publish_exclusive fallback with a bare os.replace
def test_e9_capture_republish(tmp_path, monkeypatch):
    """A drain that appended must not return with the arc's queue entry absent (C-HE-04 §4)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(am, "committed_arc_ids", set)

    def extract_and_steal(a):
        # peer removes the winner's .taken between append and restore (E9)
        (q / "pr-1.taken").unlink()
        return am.ArcRow(
            arc_id="pr-1",
            pr=1,
            merged_at="2026-08-19T00:00:00Z",
            merge_sha="abc123def4567890abc123def4567890abc123de",
        )

    monkeypatch.setattr(am, "extract", extract_and_steal)
    am.drain(argparse.Namespace())
    assert (q / "pr-1.json").exists(), "entry re-published from the in-memory capture"
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-1"]


def test_abort_branch_restores_before_kept_queued(tmp_path, monkeypatch, capsys):
    """On AbortError the entry is durably back BEFORE `KEPT QUEUED` is reported (C-HE-04 §7)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(am, "committed_arc_ids", set)

    def abort(a):
        (q / "pr-1.taken").unlink()
        raise am.AbortError("no round logs")

    monkeypatch.setattr(am, "extract", abort)
    am.drain(argparse.Namespace())
    assert (q / "pr-1.json").exists(), "restore-or-republish ran on the abort branch"
    assert "KEPT QUEUED" in capsys.readouterr().err


# ─── U-HE-16: C-HE-02 witnesses — lock-free grep, takeover, kill seam ───────────

_TOOLS_DIR = Path(__file__).resolve().parent
COORD_MODULES = ["tools/arc_metrics.py", "tools/merge_door.py", "tools/reservations.py"]


def test_no_flock_fcntl_in_coordination_modules():
    """C-HE-02 §1 invariant: no flock/fcntl in the three lane-coordination modules."""
    for m in COORD_MODULES:
        p = _TOOLS_DIR.parent / m
        if p.exists():
            assert not re.search(r"flock|fcntl", p.read_text()), m


# mutation-probe: comment out the unknown-is-live guard in _claim_owner_is_dead()
def test_takeover_token_compare(tmp_path, monkeypatch):
    """Two dead-owner takeovers on one claim: exactly one wins the second publish_exclusive;
    the loser yields; unverifiable ownership is never judged dead (C-HE-02 §6)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    entry = {"pr": 5, "arc_id": "pr-5"}
    (q / "pr-5.json").write_text(json.dumps(entry))
    (q / "pr-5.taken").write_text(
        json.dumps({**entry, "_claim": {"pid": 999999, "host": socket.gethostname()}})
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: pid == os.getpid())
    wins = [am._claim_arc(q / "pr-5.json", entry), am._claim_arc(q / "pr-5.json", entry)]
    assert sum(w is not None for w in wins) == 1
    # Exactly one claim file remains and it is stamped by the WINNER (this pid) --
    # a non-exclusive second write would have restamped it.
    takens = list(q.glob("*.taken"))
    assert [t.name for t in takens] == ["pr-5.taken"]
    assert json.loads(takens[0].read_text())["_claim"]["pid"] == os.getpid()
    assert am._claim_owner_is_dead(q / "pr-5.taken") is False  # the winner (this pid) is alive
    # A foreign-host claim is unverifiable from here: NEVER dead, even with a dead pid.
    (q / "pr-9.taken").write_text(
        json.dumps({"pr": 9, "_claim": {"pid": 999999, "host": "elsewhere.invalid"}})
    )
    assert am._claim_owner_is_dead(q / "pr-9.taken") is False


# mutation-probe: comment out the stale-judgment re-judge guard in _claim_arc's takeover
def test_stale_dead_judgment_cannot_delete_a_fresh_live_claim(tmp_path, monkeypatch):
    """Two contenders both judged the dead owner; the slower one's takeover runs
    AFTER the winner published a live claim. The atomic-rename + re-judge must
    return the live claim untouched and yield (codex r8 P1)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    entry = {"pr": 5, "arc_id": "pr-5"}
    (q / "pr-5.json").write_text(json.dumps(entry))
    (q / "pr-5.taken").write_text(
        json.dumps({**entry, "_claim": {"pid": 999999, "host": socket.gethostname()}})
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: pid == os.getpid())
    first = am._claim_arc(q / "pr-5.json", entry)
    assert first is not None, "the winner's takeover succeeds"
    # The entry is re-published (as a concurrent queue_capture legitimately can),
    # and contender B arrives carrying a STALE dead-judgment of the claim name.
    (q / "pr-5.json").write_text(json.dumps(entry))
    real_dead = am._claim_owner_is_dead
    calls = {"n": 0}

    def stale_once(path):
        calls["n"] += 1
        if calls["n"] == 1:
            return True  # B's stale judgment of the now-live claim
        return real_dead(path)

    monkeypatch.setattr(am, "_claim_owner_is_dead", stale_once)
    second = am._claim_arc(q / "pr-5.json", entry)
    assert second is None, "the stale judge yields"
    taken = q / "pr-5.taken"
    assert taken.exists(), "the winner's live claim survived the stale takeover"
    assert json.loads(taken.read_text())["_claim"]["pid"] == os.getpid()
    assert not list(q.glob("*.taken.recover.*")), "no aside left behind"


def test_vanished_entry_under_claim_is_republished_not_deleted(tmp_path, monkeypatch):
    """If the .json vanished between listing and claiming, the claimer must re-publish
    the capture it holds and yield -- never delete the only copy (codex r10 P1)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    entry = {"pr": 6, "arc_id": "pr-6"}
    path = q / "pr-6.json"
    # listed, then gone before the claim ran (a dead claimer consumed it)
    result = am._claim_arc(path, entry)
    assert result is None
    assert path.exists(), "the capture is durably back in the queue"
    assert json.loads(path.read_text())["pr"] == 6


# mutation-probe: comment out the `if current != entry` corrected-declarations guard in _claim_arc
def test_corrected_declarations_survive_a_stale_claimer(tmp_path, monkeypatch):
    """A producer that re-queued corrected declarations after this drain's listing
    must not have them consumed by the stale listing (codex r10 P1)."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    stale = {"pr": 6, "arc_id": "pr-6", "decisions": 1}
    corrected = {"pr": 6, "arc_id": "pr-6", "decisions": 9}
    path = q / "pr-6.json"
    path.write_text(json.dumps(corrected))
    result = am._claim_arc(path, stale)
    assert result is None, "the stale claimer yields"
    assert json.loads(path.read_text()) == corrected, "corrected declarations intact"
    assert not list(q.glob("*.taken")), "no stale claim left behind"


def test_kill_after_seam_exits_137():
    """ARC_METRICS_TEST_KILL_AFTER=<step> is a real process death (C-HE-04 verification (vi))."""
    code = (
        "import os; os.environ['ARC_METRICS_TEST_KILL_AFTER']='x'; "
        "import arc_metrics as am; am._kill_after('x'); print('alive')"
    )
    r = subprocess.run(
        [sys.executable, "-c", code],
        env={**os.environ, "PYTHONPATH": str(_TOOLS_DIR)},
        capture_output=True,
        text=True,
    )
    assert r.returncode == 137
    assert "alive" not in r.stdout


# ─── U-HE-19: drain ⇄ reservation integration (C-HE-04 §2/§4/§5, C-HE-03 §4/§6) ─────


# mutation-probe: drop the holder check in append()
def test_append_refuses_unless_holder(tmp_path, monkeypatch, qdir_res):
    """C-HE-04 §2(ii): append() refuses unless THIS lane holds the open reservation."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-40", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-40", "A")
    with pytest.raises(am.AbortError, match="holder"):
        am.append(am.ArcRow(arc_id="pr-40", merged_at="t", merge_sha="s"))
    monkeypatch.setattr(am, "LANE_ID", "A")
    am.append(am.ArcRow(arc_id="pr-40", merged_at="t", merge_sha="s"))
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-40"]


# mutation-probe: drop the pending->open flip in _drain_one
def test_drain_flips_before_append_and_folds_reservation_fields(tmp_path, monkeypatch):
    """C-HE-04 §2 order (flip BEFORE append) + the C-HE-27 §3 / C-HE-25 / C-HE-26 §1 fold."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="applying")
    rs.record_phase("pr-1", "execute", "start", ts="2026-08-20T00:00:00Z")
    rs.record_round_outcome("pr-1", 1, channel="codex", terminal="APPROVE", finding_count=0)
    rs.update_payload("pr-1", {"head_sha": "abc123f", "base_sha": "def456a"})
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    order = []
    real_append = am.append
    monkeypatch.setattr(
        am,
        "append",
        lambda row: (order.append(("append", rs.current("pr-1")[1]["state"])), real_append(row))[1],
    )
    monkeypatch.setattr(
        am, "extract", lambda a: am.ArcRow(arc_id="pr-1", merged_at="t", merge_sha="s")
    )
    am.drain(argparse.Namespace())
    assert order == [("append", "open")], (
        "flip BEFORE append; terminalization follows append so the open-head "
        "recovery paths stay alive (codex r9 P1)"
    )
    row = am.read_ledger()[0]
    assert row["arc_type_open"] == "applying" and row["lane_id"] == "A"
    assert row["arc_type"] == "applying" and row["arc_type_declared_at"] == "open", (
        "canonical label follows the open-time provenance (codex r6 P2)"
    )
    assert row["phases"]["execute"]["start"] == "2026-08-20T00:00:00Z"
    assert row["round_outcomes"] == {
        "1": {"channel": "codex", "terminal": "APPROVE", "finding_count": 0}
    }
    assert row["head_sha"] == "abc123f" and row["base_sha"] == "def456a", (
        "sha provenance folds (codex r20 P3)"
    )
    assert row["concurrent_lanes_at_open"] == 0


# mutation-probe: drop transfer_holder() from _recover_dead_claims
def test_recover_transfers_holder_to_recoverer(tmp_path, monkeypatch, qdir_res):
    """C-HE-04 §4 / C-HE-03 §6 (the named D2 exception): restoring a dead owner's claim
    transfers the open reservation's holder to the recovering lane in the same step."""
    q = qdir_res
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-50", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-50", "A")
    (q / "pr-50.taken").write_text(
        json.dumps(
            {
                "pr": 50,
                "arc_id": "pr-50",
                "_claim": {"pid": 999999, "host": socket.gethostname(), "lane_id": "A"},
            }
        )
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    am._recover_dead_claims()
    assert (q / "pr-50.json").exists() and rs.holder("pr-50") == "B"


# mutation-probe: drop the open-held-by-another-lane drop branch in _reconcile_local_rows
def test_local_row_reconciliation_drops_superseded_rows(tmp_path, monkeypatch, qdir_res):
    """C-HE-04 §5: uncommitted local rows whose reservation is held/merged by ANOTHER
    lane are dropped at drain start; this lane's own rows survive."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    ledger.write_text(
        json.dumps({"arc_id": "pr-60", "record_kind": "arc"})
        + "\n"
        + json.dumps({"arc_id": "pr-61", "record_kind": "arc"})
        + "\n"
    )
    rs.reserve("pr-60", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-60", "B")  # held by another lane
    rs.reserve("pr-61", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-61", "A")  # ours
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    am._reconcile_local_rows()
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-61"]


def test_bootstrap_emit_failure_is_per_arc_and_next_drain_proceeds(tmp_path, monkeypatch, capsys):
    """The fail-closed loop emitter (loop_log_structured lands at U-HE-29) raising at the
    legacy bootstrap is a PER-ARC fault: entry kept + loud, no wedged claim -- and because
    the reservation is created BEFORE the emit, the NEXT drain proceeds without it."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    monkeypatch.setattr(am, "extract", lambda a: _merged_row("pr-1", 1))

    def boom(*a, **k):
        raise rs.LoopStatusWriteError("loop row not written")

    monkeypatch.setattr(rs, "emit_loop_row", boom)
    rc = am.drain(argparse.Namespace())
    err = capsys.readouterr().err
    assert rc == 1 and "KEPT QUEUED" in err
    assert (q / "pr-1.json").exists() and not list(q.glob("*.taken"))
    assert rs.current("pr-1")[1]["state"] == "pending", "reservation created before the emit"
    monkeypatch.setattr(rs, "emit_loop_row", lambda *a, **k: None)
    rc = am.drain(argparse.Namespace())
    assert rc == 1, "added row held pending commit"
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-1"]


def test_recovery_never_transfers_from_a_live_holder_via_a_non_holder_claim(
    tmp_path, monkeypatch, qdir_res
):
    """codex U-HE-19 r1 P1: a NON-holder lane can claim a held entry and die; recovering
    its claim must NOT move the live holder's reservation -- the transfer requires the
    dead claimant's stamped lane to BE the holder. An unstamped claim proves nothing."""
    q = qdir_res
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-51", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-51", "A")  # holder A is alive elsewhere
    (q / "pr-51.taken").write_text(
        json.dumps(
            {
                "pr": 51,
                "arc_id": "pr-51",
                "_claim": {"pid": 999999, "host": socket.gethostname(), "lane_id": "C"},
            }
        )
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    am._recover_dead_claims()
    assert (q / "pr-51.json").exists(), "the entry itself is still recovered"
    assert rs.holder("pr-51") == "A", "the live holder keeps the reservation"
    # an UNSTAMPED dead claim (legacy shape) likewise proves nothing
    (q / "pr-52.taken").write_text(
        json.dumps(
            {"pr": 52, "arc_id": "pr-52", "_claim": {"pid": 999999, "host": socket.gethostname()}}
        )
    )
    rs.reserve("pr-52", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-52", "A")
    am._recover_dead_claims()
    assert rs.holder("pr-52") == "A", "no lane identity in the claim -> no transfer"


def test_cmd_extract_backfill_reserves_first_and_holder_rule_stands(
    tmp_path, monkeypatch, qdir_res, capsys
):
    """codex U-HE-19 r1-r4 P2 lineage: the manual backfill mints its own reservation
    (reserve's exclusive-create CAS is the race fence -- no holder bypass exists), and
    an arc already reserved by another lane keeps the C-HE-04 §2 holder rule."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "B")
    ns = argparse.Namespace(dry_run=False)
    classified = am.ArcRow(arc_id="pr-70", pr=70, merged_at="t", merge_sha="s", arc_type="applying")
    monkeypatch.setattr(am, "extract", lambda a: classified)
    assert am.cmd_extract(ns) == 0
    out = capsys.readouterr().out
    assert "reserved by this lane" in out and "terminalized merged" in out
    assert rs.current("pr-70")[1]["state"] == "merged"
    assert rs.current("pr-70")[1]["lane_id"] == "B"
    folded = am.read_ledger()[0]
    assert folded["lane_id"] is None and folded["concurrent_lanes_at_open"] is None, (
        "historical fields stay NULL (codex r16/r18 flip adjudicated: a synthetic"
        " backfill reservation's lane/sensor would be false derived data -- C-HE-25's"
        " additive-null model governs historical rows)"
    )
    # unclassified backfill is refused (C-HE-26 §1: the minted reservation needs a label)
    monkeypatch.setattr(am, "extract", lambda a: _merged_row("pr-72", 72))
    with pytest.raises(am.AbortError, match="arc-type"):
        am.cmd_extract(ns)
    # an arc reserved+opened by another lane keeps the holder rule
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id="pr-71", pr=71, merged_at="t", merge_sha="s", arc_type="applying"
        ),
    )
    rs.reserve("pr-71", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-71", "A")
    with pytest.raises(am.AbortError, match="holder"):
        am.cmd_extract(ns)
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-70"]


def test_lane_id_fallback_is_stable_across_invocations():
    """codex U-HE-19 r1 P2: the fallback lane id must not embed the pid -- a retrying
    CLI invocation is the SAME lane. Stable per (host, worktree), ':'-free, non-empty."""
    expected = (
        f"{socket.gethostname().split('.')[0]}-{am.REPO.name}-"
        f"{__import__('hashlib').sha256(str(am.REPO.resolve()).encode()).hexdigest()[:8]}"
    )[:64].replace(":", "-")
    if os.environ.get("HARNESS_LANE_ID"):
        assert am.LANE_ID == os.environ["HARNESS_LANE_ID"]
    else:
        assert am.LANE_ID == expected
    assert am.LANE_ID and ":" not in am.LANE_ID


def test_merged_reservation_holds_entry_until_committed(tmp_path, monkeypatch):
    """codex U-HE-19 r2 P1: a merged reservation proves the PR merged, not that any row
    exists -- the entry is held (never released) until the arc is in COMMITTED history
    (the C-HE-04 invariant's only release path)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="applying")
    rs.open_with_sensor("pr-1", "A")
    rs.transition("pr-1", "merged", lane_id="A")
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    rc = am.drain(argparse.Namespace())
    assert rc == 1 and (q / "pr-1.json").exists(), "sole capture held, never deleted"
    assert am.read_ledger() == [], "nothing appended for a terminal reservation"
    monkeypatch.setattr(am, "committed_arc_ids", lambda: {"pr-1"})
    rc = am.drain(argparse.Namespace())
    assert rc == 0 and not (q / "pr-1.json").exists(), "committed history releases it"


def test_local_row_reconciliation_keeps_merged_without_committed_row(
    tmp_path, monkeypatch, qdir_res
):
    """codex U-HE-19 r2 P1: merged-by-another-lane without a committed replacement row
    may be the ONLY capture of that arc -- kept (loudly), never dropped."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    ledger.write_text(json.dumps({"arc_id": "pr-62", "record_kind": "arc"}) + "\n")
    rs.reserve("pr-62", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-62", "B")
    rs.transition("pr-62", "merged", lane_id="B")
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    am._reconcile_local_rows()
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-62"], "sole capture survives"


def test_merged_holder_own_capture_drains_normally(tmp_path, monkeypatch):
    """codex U-HE-19 r3 P1: post-U-HE-22 the merge door flips open->merged BEFORE the
    closure capture drains -- the merged HOLDER's own first append is the ordinary
    capture path (C-HE-03 §6 forbids re-append, not the holder's first capture)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="applying")
    rs.open_with_sensor("pr-1", "A")
    rs.record_phase("pr-1", "execute", "start", ts="2026-08-20T00:00:00Z")
    rs.transition("pr-1", "merged", lane_id="A")
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    monkeypatch.setattr(
        am, "extract", lambda a: am.ArcRow(arc_id="pr-1", merged_at="t", merge_sha="s")
    )
    rc = am.drain(argparse.Namespace())
    assert rc == 1, "appended, held pending commit"
    row = am.read_ledger()[0]
    assert row["arc_id"] == "pr-1" and row["lane_id"] == "A"
    assert row["phases"]["execute"]["start"] == "2026-08-20T00:00:00Z", "fold still runs"
    assert (q / "pr-1.json").exists(), "entry held until the row commits"


def test_fallback_lane_id_keeps_digest_under_long_names():
    """codex U-HE-19 r3 P2: the ≤64 budget must trim the NAME, never the path digest --
    two long-common-prefix worktrees must not collide into one lane identity."""
    a = am._fallback_lane_id("host.example.com", Path("/tmp/w/" + "x" * 80 + "-one"))
    b = am._fallback_lane_id("host.example.com", Path("/tmp/w/" + "x" * 80 + "-two"))
    assert a != b, "distinct worktrees keep distinct identities"
    assert len(a) <= 64 and len(b) <= 64
    assert ":" not in a and a


def test_local_row_reconciliation_drops_divergent_committed_duplicate(
    tmp_path, monkeypatch, qdir_res
):
    """codex U-HE-19 r3 P2: once a replacement row for the arc is in COMMITTED history,
    a divergent local duplicate is provably stale -- dropped; a row that IS the
    committed content is kept."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    committed_row = {"arc_id": "pr-80", "record_kind": "arc", "notes": "committed"}
    stale_row = {"arc_id": "pr-81", "record_kind": "arc", "notes": "stale divergent"}
    ledger.write_text(
        json.dumps(committed_row, sort_keys=True)
        + "\n"
        + json.dumps(stale_row, sort_keys=True)
        + "\n"
    )
    replacement = {"arc_id": "pr-81", "record_kind": "arc", "notes": "the real one"}
    # the discriminator (codex r10 P2): replacement fires only when a PEER's
    # reservation shows the arc was superseded -- reserve pr-81 as another lane's
    rs.reserve("pr-81", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-81", "B")
    rs.transition("pr-81", "merged", lane_id="B")
    monkeypatch.setattr(am, "committed_arc_ids", lambda: {"pr-80", "pr-81"})
    monkeypatch.setattr(
        am,
        "_committed_ledger_lines",
        lambda: {
            json.dumps(committed_row, sort_keys=True),
            json.dumps(replacement, sort_keys=True),
        },
    )
    am._reconcile_local_rows()
    rows = am.read_ledger()
    assert [r["arc_id"] for r in rows] == ["pr-80", "pr-81"], (
        "committed content kept; the divergent row CONVERGES to canonical, never a bare"
        " deletion (codex r9 P2: it may be pre-rebase baseline content)"
    )
    assert rows[1] == replacement, "the committed canonical content replaced the stale bytes"


def test_cmd_extract_backfill_loses_the_reservation_race_loudly(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r4 P2: a peer reserving between the backfill's check and its own
    reserve() loses NOTHING to a window -- the store's exclusive-create CAS refuses,
    the command aborts loudly, and no row is appended."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "B")
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id="pr-90", pr=90, merged_at="t", merge_sha="s", arc_type="applying"
        ),
    )
    real_current = rs.current
    calls = {"n": 0}

    def peer_reserves_after_the_check(arc_id):
        out = real_current(arc_id)
        calls["n"] += 1
        if calls["n"] == 1 and out is None:
            monkeypatch.setattr(rs, "current", real_current)
            rs.reserve("pr-90", lane_id="A", branch="b", arc_type="inventing")
        return out

    monkeypatch.setattr(rs, "current", peer_reserves_after_the_check)
    with pytest.raises(am.AbortError, match="reservation race"):
        am.cmd_extract(argparse.Namespace(dry_run=False))
    assert am.read_ledger() == [], "nothing appended after the lost race"
    assert rs.current("pr-90")[1]["lane_id"] == "A", "the peer's reservation stands"


# mutation-probe: drop _transfer_reservation_to_recoverer() from the orphaned-aside route
def test_recovery_transfers_holder_on_the_orphaned_aside_route(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r5 P3: the SECOND dead-owner restore site -- an aside orphaned by a
    recoverer that died between rename and restore -- must also run the C-HE-04 §4
    holder transfer when the embedded dead claimant was the holder."""
    q = qdir_res
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-53", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-53", "A")
    (q / f"pr-53.taken.recover.{socket.gethostname()}.999999").write_text(
        json.dumps(
            {
                "pr": 53,
                "arc_id": "pr-53",
                "_claim": {"pid": 999998, "host": socket.gethostname(), "lane_id": "A"},
            }
        )
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    am._recover_dead_claims()
    assert (q / "pr-53.json").exists(), "orphaned aside restored to the queue"
    assert rs.holder("pr-53") == "B", "the dead holder's reservation transferred"


def test_merged_append_refused_once_a_row_is_in_committed_history(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r6 P1: the merged-holder admission covers only the NOT-YET-COMMITTED
    first capture -- a same-lane append from a reset/another worktree ledger against a
    committed arc is the C-HE-03 §6 re-append and is refused."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")  # fresh (reset) ledger
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-95", lane_id="A", branch="b", arc_type="applying")
    rs.open_with_sensor("pr-95", "A")
    rs.transition("pr-95", "merged", lane_id="A")
    committed_line = json.dumps({"arc_id": "pr-95", "record_kind": "arc"}, sort_keys=True)
    monkeypatch.setattr(am, "_committed_ledger_lines", lambda: {committed_line})
    with pytest.raises(am.AbortError, match="re-append refused"):
        am.append(am.ArcRow(arc_id="pr-95", merged_at="t", merge_sha="s"))
    # UNREADABLE history is a tri-state unknown: HOLD, never fail open (codex r7 P1)
    monkeypatch.setattr(am, "_committed_ledger_lines", lambda: None)
    with pytest.raises(am.AbortError, match="unreadable"):
        am.append(am.ArcRow(arc_id="pr-95", merged_at="t", merge_sha="s"))
    # KNOWN-empty committed history is the legitimate first capture
    monkeypatch.setattr(am, "_committed_ledger_lines", lambda: set())
    am.append(am.ArcRow(arc_id="pr-95", merged_at="t", merge_sha="s"))


def test_interrupted_terminalization_is_completed_on_the_held_retry(tmp_path, monkeypatch):
    """codex U-HE-19 r6 P2: a crash between append and the open->merged flip leaves the
    row local and the head open; the retry's `arc_id in local` hold must FINISH the
    terminalization instead of parking the head open forever."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="applying")
    rs.open_with_sensor("pr-1", "A")  # the interrupted drain's flip survived
    (tmp_path / "l.jsonl").write_text(
        json.dumps({"arc_id": "pr-1", "record_kind": "arc"}) + "\n"
    )  # ...and so did its appended local row
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    rc = am.drain(argparse.Namespace())
    assert rc == 1 and (q / "pr-1.json").exists(), "entry held pending commit"
    head = rs.current("pr-1")[1]
    assert head["state"] == "merged" and head["pr"] == 1, (
        "the deferred terminalization completed on the retry"
    )


def test_cmd_extract_refuses_a_normal_same_lane_reservation(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r9 P2: manual extract must not consume a NORMAL reserved arc --
    that append would skip the drain's reservation fold and deadlock the queued
    drain's correct row behind the duplicate guard."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "A")
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id="pr-96", pr=96, merged_at="t", merge_sha="s", arc_type="applying"
        ),
    )
    rs.reserve("pr-96", lane_id="A", branch="feat/real-arc", arc_type="applying")
    with pytest.raises(am.AbortError, match="queue"):
        am.cmd_extract(argparse.Namespace(dry_run=False))
    assert not (tmp_path / "l.jsonl").exists(), "nothing appended"
    rs.open_with_sensor("pr-96", "A")
    with pytest.raises(am.AbortError, match="queue"):
        am.cmd_extract(argparse.Namespace(dry_run=False))


def test_late_accretion_is_refolded_into_the_local_row(tmp_path, monkeypatch):
    """codex U-HE-19 r8/r9: an accretion CAS landing between the fold read and the
    generation-bound terminalization must reach the one arc row -- via the local-row
    re-fold, not a silent omission (and append still ran under an OPEN head)."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="applying")
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    monkeypatch.setattr(
        am, "extract", lambda a: am.ArcRow(arc_id="pr-1", merged_at="t", merge_sha="s")
    )
    real_append = am.append

    def append_then_late_accretion(row):
        real_append(row)
        # a concurrent record_phase CAS lands AFTER the fold read, BEFORE terminalize
        rs.record_phase("pr-1", "execute", "end", ts="2026-08-20T01:00:00Z")

    monkeypatch.setattr(am, "append", append_then_late_accretion)
    rc = am.drain(argparse.Namespace())
    assert rc == 1
    row = am.read_ledger()[0]
    assert row["phases"]["execute"]["end"] == "2026-08-20T01:00:00Z", (
        "the late accretion reached the row via the re-fold"
    )
    assert rs.current("pr-1")[1]["state"] == "merged"


def test_reconciliation_keeps_a_legit_local_update_to_a_committed_row(
    tmp_path, monkeypatch, qdir_res
):
    """codex U-HE-19 r10 P2: a local line differing from committed history with NO
    superseding peer reservation is a legitimate pending update (e.g. a relabel) or
    pre-rebase baseline content -- kept untouched, never overwritten."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    local_update = {"arc_id": "pr-82", "record_kind": "arc", "arc_type_close": "applying"}
    ledger.write_text(json.dumps(local_update, sort_keys=True) + "\n")
    committed_version = {"arc_id": "pr-82", "record_kind": "arc"}
    monkeypatch.setattr(am, "committed_arc_ids", lambda: {"pr-82"})
    monkeypatch.setattr(
        am,
        "_committed_ledger_lines",
        lambda: {json.dumps(committed_version, sort_keys=True)},
    )
    am._reconcile_local_rows()
    assert am.read_ledger() == [local_update], "the pending relabel survived"


def test_reconciliation_never_leaves_two_rows_for_one_committed_arc(
    tmp_path, monkeypatch, qdir_res
):
    """codex U-HE-19 r10 P2: a canonical FIRST occurrence must still mark the aid, so
    a divergent second occurrence is dropped -- never replaced into a second copy."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    canonical = {"arc_id": "pr-83", "record_kind": "arc"}
    divergent = {"arc_id": "pr-83", "record_kind": "arc", "notes": "stale duplicate"}
    ledger.write_text(
        json.dumps(canonical, sort_keys=True) + "\n" + json.dumps(divergent, sort_keys=True) + "\n"
    )
    monkeypatch.setattr(am, "committed_arc_ids", lambda: {"pr-83"})
    monkeypatch.setattr(
        am, "_committed_ledger_lines", lambda: {json.dumps(canonical, sort_keys=True)}
    )
    am._reconcile_local_rows()
    assert am.read_ledger() == [canonical], "exactly one row survives"


def test_merged_append_holds_on_unparseable_committed_history(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r10 P2: corruption in committed history reads as UNREADABLE, never
    as absence -- the merged-path append holds."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-97", lane_id="A", branch="b", arc_type="applying")
    rs.open_with_sensor("pr-97", "A")
    rs.transition("pr-97", "merged", lane_id="A")
    monkeypatch.setattr(am, "_committed_ledger_lines", lambda: {'{"arc_id": TRUNC'})
    with pytest.raises(am.AbortError, match="unparseable"):
        am.append(am.ArcRow(arc_id="pr-97", merged_at="t", merge_sha="s"))


def test_failed_refold_heals_on_the_next_held_pass(tmp_path, monkeypatch):
    """codex U-HE-19 r10 P2: a refold that failed after the terminal flip heals on the
    next drain's held pass -- the merged-ours branch re-projects idempotently."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="applying")
    rs.open_with_sensor("pr-1", "A")
    rs.record_phase("pr-1", "execute", "start", ts="2026-08-20T00:00:00Z")
    rs.transition("pr-1", "merged", lane_id="A")
    # the crashed drain appended a PRE-accretion row and never refolded
    (tmp_path / "l.jsonl").write_text(
        json.dumps({"arc_id": "pr-1", "record_kind": "arc", "phases": {}}) + "\n"
    )
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    rc = am.drain(argparse.Namespace())
    assert rc == 1 and (q / "pr-1.json").exists(), "entry held pending commit"
    row = am.read_ledger()[0]
    assert row["phases"]["execute"]["start"] == "2026-08-20T00:00:00Z", (
        "the held pass re-projected the terminal head onto the local row"
    )


def test_backfill_resume_refuses_a_mismatched_reservation_payload(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r11 P2: lane+branch alone do not bind a backfill reservation to
    THIS invocation -- a mismatched recorded pr/arc_type is refused, not consumed."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-98", lane_id="B", branch=am.BACKFILL_BRANCH, arc_type="inventing")
    rs.update_payload("pr-98", {"pr": 998})
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id="pr-98", pr=99, merged_at="t", merge_sha="s", arc_type="applying"
        ),
    )
    with pytest.raises(am.AbortError, match="not this command's reservation"):
        am.cmd_extract(argparse.Namespace(dry_run=False))
    assert not (tmp_path / "l.jsonl").exists() and rs.current("pr-98")[1]["state"] == "pending"


def test_backfill_discriminator_cannot_be_a_real_branch(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r12 P2: the resume discriminator contains ':' -- illegal in a git
    ref -- so a NORMAL arc whose branch merely resembles a backfill can never be
    misclassified; and a same-lane normal reservation is still refused."""
    assert ":" in am.BACKFILL_BRANCH
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "A")
    monkeypatch.setattr(
        am,
        "extract",
        lambda a: am.ArcRow(
            arc_id="pr-99", pr=99, merged_at="t", merge_sha="s", arc_type="applying"
        ),
    )
    # a plausible-looking REAL branch name is still a normal reservation -> refused
    rs.reserve("pr-99", lane_id="A", branch="historical-backfill", arc_type="applying")
    with pytest.raises(am.AbortError, match="queue"):
        am.cmd_extract(argparse.Namespace(dry_run=False))
    assert not (tmp_path / "l.jsonl").exists()


# mutation-probe: drop the stash-time transfer in _claim_arc's takeover
def test_claim_arc_takeover_transfers_the_dead_holders_reservation(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r12 P2: the mid-drain takeover in _claim_arc is a THIRD dead-owner
    consumption site -- it too must run the C-HE-04 §4 transfer from the lane-stamped
    claim bytes before discarding them."""
    q = qdir_res
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-54", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-54", "A")
    entry = {"pr": 54, "arc_id": "pr-54", "arc_type": "inventing"}
    path = q / "pr-54.json"
    path.write_text(json.dumps(entry))
    (q / "pr-54.taken").write_text(
        json.dumps(
            {**entry, "_claim": {"pid": 999999, "host": socket.gethostname(), "lane_id": "A"}}
        )
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    taken = am._claim_arc(path, entry)
    assert taken is not None and taken.exists(), "the takeover claimed the entry"
    assert rs.holder("pr-54") == "B", "the dead holder's reservation transferred"


def test_bootstrap_honors_the_entrys_declared_at(tmp_path, monkeypatch):
    """codex U-HE-19 r13 P2: a legacy entry declared at OPEN must bootstrap an
    open-declared reservation -- row provenance and reservation must agree."""
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(am, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    (q / "pr-1.json").write_text(
        json.dumps(
            {"pr": 1, "arc_id": "pr-1", "arc_type": "applying", "arc_type_declared_at": "open"}
        )
    )
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    monkeypatch.setattr(
        am, "extract", lambda a: am.ArcRow(arc_id="pr-1", merged_at="t", merge_sha="s")
    )
    am.drain(argparse.Namespace())
    head = rs.current("pr-1")[1]
    assert head["arc_type_declared_at"] == "open"
    row = am.read_ledger()[0]
    assert row["arc_type_declared_at"] == "open" and row["arc_type_open"] == "applying"


def test_non_object_reservation_head_is_isolated_at_reconciliation(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r13 P2: a syntactically valid NON-OBJECT head must not abort the
    drain -- the row is kept per-row, loudly."""
    q = qdir_res
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    ledger.write_text(json.dumps({"arc_id": "pr-86", "record_kind": "arc"}) + "\n")
    d = q / "reservations" / "pr-86"
    d.mkdir(parents=True)
    (d / "1.json").write_text("[1, 2]")  # valid JSON, not an object
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    am._reconcile_local_rows()  # must NOT raise
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-86"], "row kept"


def test_backfill_retry_without_arc_type_takes_the_reservations_label(
    tmp_path, monkeypatch, qdir_res
):
    """codex U-HE-19 r17 P2: a crash-retry that omits --arc-type still records the
    minted reservation's close-declared classification, never a null label."""
    monkeypatch.setattr(am, "LEDGER", tmp_path / "l.jsonl")
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve(
        "pr-73",
        lane_id="B",
        branch=am.BACKFILL_BRANCH,
        arc_type="applying",
        arc_type_declared_at="close",  # exactly as the backfill mints it
    )
    monkeypatch.setattr(
        am, "extract", lambda a: am.ArcRow(arc_id="pr-73", pr=73, merged_at="t", merge_sha="s")
    )
    assert am.cmd_extract(argparse.Namespace(dry_run=False)) == 0
    row = am.read_ledger()[0]
    assert row["arc_type"] == "applying" and row["arc_type_close"] == "applying"
    assert row["arc_type_declared_at"] == "close"


def test_directory_shaped_generation_is_isolated_at_reconciliation(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r17 P2: IsADirectoryError from a corrupt generation is per-row --
    the drain start must not abort on it."""
    q = qdir_res
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    ledger.write_text(json.dumps({"arc_id": "pr-87", "record_kind": "arc"}) + "\n")
    (q / "reservations" / "pr-87" / "1.json").mkdir(parents=True)
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    am._reconcile_local_rows()  # must NOT raise
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-87"], "row kept"


def test_drain_never_hijacks_a_backfill_pending_reservation(tmp_path, monkeypatch):
    """merge-gate r1 concurrency P2: a pending head minted by the cmd_extract backfill
    is not drain's to flip -- the entry is held for that flow, both captures survive."""
    q = _queue_entries(am, tmp_path, monkeypatch, 1)
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    monkeypatch.setattr(am, "LANE_ID", "A")
    rs.reserve(
        "pr-1",
        lane_id="A",
        branch=am.BACKFILL_BRANCH,
        arc_type="applying",
        arc_type_declared_at="close",
    )
    monkeypatch.setattr(am, "committed_arc_ids", lambda: set())
    monkeypatch.setattr(
        am, "extract", lambda a: am.ArcRow(arc_id="pr-1", merged_at="t", merge_sha="s")
    )
    rc = am.drain(argparse.Namespace())
    assert rc == 1 and (q / "pr-1.json").exists(), "entry held, not consumed"
    assert am.read_ledger() == [], "drain appended nothing"
    assert rs.current("pr-1")[1]["state"] == "pending", "the backfill's head untouched"
    # merge-gate r2: the SAME hold applies in every state -- the open and merged
    # windows of the backfill are equally not drain's to consume
    rs.open_with_sensor("pr-1", "A")
    rc = am.drain(argparse.Namespace())
    assert rc == 1 and (q / "pr-1.json").exists() and am.read_ledger() == []
    assert rs.current("pr-1")[1]["state"] == "open", "open backfill head untouched"
    rs.transition("pr-1", "merged", lane_id="A")
    rc = am.drain(argparse.Namespace())
    assert rc == 1 and (q / "pr-1.json").exists() and am.read_ledger() == []
    assert rs.current("pr-1")[1]["state"] == "merged", "merged backfill head untouched"


# mutation-probe: drop _transfer_reservation_to_recoverer() from the swept-leftover-claim branch
def test_swept_leftover_claim_still_transfers_the_dead_holders_reservation(
    tmp_path, monkeypatch, qdir_res
):
    """merge-gate r1 witness P2: the FOURTH dead-owner consumption site -- a dead
    leftover .taken whose entry is already back -- must also run the C-HE-04 §4
    transfer from the re-judged bytes before sweeping them."""
    q = qdir_res
    monkeypatch.setattr(am, "LANE_ID", "B")
    rs.reserve("pr-55", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-55", "A")
    entry = {"pr": 55, "arc_id": "pr-55", "arc_type": "inventing"}
    (q / "pr-55.json").write_text(json.dumps(entry))  # the entry is already durably back
    (q / "pr-55.taken").write_text(
        json.dumps(
            {**entry, "_claim": {"pid": 999999, "host": socket.gethostname(), "lane_id": "A"}}
        )
    )
    monkeypatch.setattr(am, "_process_is_alive", lambda pid: False)
    am._recover_dead_claims()
    assert not (q / "pr-55.taken").exists(), "the dead leftover claim was swept"
    assert (q / "pr-55.json").exists(), "the restored entry untouched"
    assert rs.holder("pr-55") == "B", "the dead holder's reservation transferred"


def test_reconciliation_stops_when_committed_history_is_unreadable(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r21 P2: unknown committed history must reconcile NOTHING -- an
    unreadable MERGED_REF would misclassify committed baseline rows as droppable."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    ledger.write_text(json.dumps({"arc_id": "pr-88", "record_kind": "arc"}) + "\n")
    rs.reserve("pr-88", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-88", "B")  # would be dropped if reconciliation ran
    monkeypatch.setattr(am, "_committed_ledger_lines", lambda: None)
    am._reconcile_local_rows()
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-88"], (
        "nothing reconciled while history is unknown"
    )


def test_reconciliation_stops_on_a_corrupt_committed_line(tmp_path, monkeypatch, qdir_res):
    """codex U-HE-19 r22 P2: an unparseable committed line means the snapshot cannot
    support destructive judgments -- reconcile NOTHING."""
    ledger = tmp_path / "l.jsonl"
    monkeypatch.setattr(am, "LEDGER", ledger)
    monkeypatch.setattr(am, "LANE_ID", "A")
    ledger.write_text(json.dumps({"arc_id": "pr-89", "record_kind": "arc"}) + "\n")
    rs.reserve("pr-89", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-89", "B")  # would be dropped if reconciliation ran
    monkeypatch.setattr(am, "_committed_ledger_lines", lambda: {'{"arc_id": TRUNC'})
    am._reconcile_local_rows()
    assert [r["arc_id"] for r in am.read_ledger()] == ["pr-89"], "row survived corruption"


# ------------------------------------------------------- U-HE-34: phase spans + N6 (C-HE-27)


def test_phase_spans_no_deltas():
    """Static witness (C-HE-27 §2): no metrics reader derives a duration from the gap
    between two records -- end_of_row_n - start_of_row_{n-1} is a different quantity
    indistinguishable from a real measurement once a record is dropped or reordered.
    Mutation probe: index a neighbouring row's timestamp in n6 -> this reds."""
    tools = Path(am.__file__).resolve().parent
    src = (tools / "arc_metrics.py").read_text()
    # The plan's guard ("phases[" in src AND "prev" in the n6 body) is vacuously green
    # while no reader indexes phases at all -- inspect n6's body unconditionally so
    # introducing a neighbouring-row variable ever reds this.
    n6_body = src.split("def n6")[1].split("\ndef ")[0]
    # \b: the docstring's own "problems prevented per hour" must not trip the witness.
    assert not re.search(r"\bprev\b", n6_body)
    for reader in ("arc_metrics.py", "shadow_trial.py", "lanes_pilot_report.py"):
        p = tools / reader
        if p.exists():
            assert not re.search(
                r"rows\[\s*\w+\s*-\s*1\s*\]\[['\"](captured_at|merged_at|ts)['\"]\]",
                p.read_text(),
            ), reader


def test_out_of_order_rows_still_yield_correct_spans():
    """C-HE-27 §2 verification: spans come from each phase's OWN {start,end} pair, so
    phase entries listed in any order still measure correctly."""
    row = {
        "phases": {
            "verify": {"end": "2026-08-18T01:00:00Z", "start": "2026-08-18T00:30:00Z"},
            "edit": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T00:20:00Z"},
        }
    }
    s = am.phase_spans(row)
    assert s["verify"] == 1800.0 and s["edit"] == 1200.0


def test_n6_formula():
    """C-HE-27 §4: accepted-count / (verify+edit) hours; verify spans of rounds that
    terminated REVIEWER_UNAVAILABLE are excluded from the denominator (bucketed), so
    reviewer downtime cannot deflate N6. Mutation probe: count arc b's verify span in
    the denominator -> n6 halves and this reds."""
    rows = [
        {
            "arc_id": "a",
            "phases": {
                "verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"},
                "edit": {"start": "2026-08-18T01:00:00Z", "end": "2026-08-18T02:00:00Z"},
            },
            "round_outcomes": {"1": {"terminal": "APPROVE"}},
        },
        {
            "arc_id": "b",
            "phases": {"verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T02:00:00Z"}},
            "round_outcomes": {"1": {"terminal": "REVIEWER_UNAVAILABLE"}},
        },
    ]
    # Legal append order (the emitter refuses a finding row AFTER its adjudication --
    # test_retry_after_adjudication_is_rejected): raw finding first, adjudication last,
    # so the file-order reducer (C-HE-24 §5) lands on the accepted adjudication. The
    # plan's fixture listed the adjudication first; that shape is emitter-illegal and
    # reduces to disposition=None (as-built deviation, noted in the PR body).
    gate = [
        {
            "finding_id": "f1",
            "arc_id": "a",
            "disposition": None,
            "ts": "t1",
            "record_kind": "finding",
        },
        {
            "finding_id": "f1",
            "arc_id": "a",
            "disposition": "accepted",
            "ts": "t2",
            "record_kind": "finding_adjudication",
        },
        {
            "finding_id": "f2",
            "arc_id": "a",
            "disposition": "rejected",
            "ts": "t1",
            "record_kind": "finding_adjudication",
        },
        # OUT-OF-WINDOW accepted finding (codex U-HE-34 r1): its arc has no measured
        # phases, so counting it would divide historical acceptances by only the
        # window's hours. Mutation probe: drop the window filter -> n6 doubles, reds.
        {
            "finding_id": "f3",
            "arc_id": "z-historical",
            "disposition": "accepted",
            "ts": "t3",
            "record_kind": "finding_adjudication",
        },
    ]
    n6, hours, excluded_s = am.n6(rows, gate)
    assert n6 == pytest.approx(0.5) and hours == 2.0 and excluded_s == 7200.0


def test_n6_buckets_explicit_verify_unavailable_span():
    """C-HE-27 §4: failover downtime is recorded as a `verify_unavailable` span NESTED
    inside verify, so it is SUBTRACTED from verify's denominator contribution and
    bucketed into excluded seconds. Mutation probe: stop subtracting -> hours 0.5->1.0
    and this reds."""
    rows = [
        {
            "arc_id": "a",
            "phases": {
                "verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"},
                "verify_unavailable": {
                    "start": "2026-08-18T00:10:00Z",
                    "end": "2026-08-18T00:40:00Z",
                },
            },
            "round_outcomes": {"1": {"terminal": "APPROVE"}},
        }
    ]
    n6, hours, excluded_s = am.n6(rows, [])
    # 0.0 here is a MEASURED zero (half an hour of review, nothing accepted), not absence.
    assert n6 == 0.0 and hours == 0.5 and excluded_s == 1800.0


def test_n6_round1_terminal_governs_verify_exclusion():
    """verify is the ROUND-1 window, so only round 1's terminal can invalidate it: a
    later round's REVIEWER_UNAVAILABLE must not erase valid round-1 review hours.
    Mutation probe: revert to an any()-over-all-rounds scan -> hours 1.0->0.0, reds."""
    rows = [
        {
            "arc_id": "a",
            "phases": {"verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"}},
            "round_outcomes": {
                "1/codex": {"terminal": "APPROVE"},
                "2/codex": {"terminal": "REVIEWER_UNAVAILABLE"},
            },
        }
    ]
    n6, hours, excluded_s = am.n6(rows, [])
    assert n6 == 0.0 and hours == 1.0 and excluded_s == 0.0


def test_n6_numerator_ignores_zero_hour_arcs():
    """An accepted finding from an arc contributing NO measured verify/edit hours must
    not enter the numerator -- it would divide by hours it never spent (codex r2).
    Mutation probe: window on row presence instead of contribution -> n6 1.0->2.0."""
    rows = [
        {
            "arc_id": "a",
            "phases": {"verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"}},
            "round_outcomes": {"1": {"terminal": "APPROVE"}},
        },
        {"arc_id": "spanless", "phases": {}, "round_outcomes": {}},
    ]
    gate = [
        {
            "finding_id": "fa",
            "arc_id": "a",
            "disposition": "accepted",
            "ts": "t1",
            "record_kind": "finding_adjudication",
        },
        {
            "finding_id": "fs",
            "arc_id": "spanless",
            "disposition": "accepted",
            "ts": "t1",
            "record_kind": "finding_adjudication",
        },
    ]
    n6, hours, _excluded_s = am.n6(rows, gate)
    assert n6 == pytest.approx(1.0) and hours == 1.0


def test_n6_round1_unavailable_does_not_double_count_nested_downtime():
    """When round 1 terminated unavailable, the WHOLE verify span is excluded; a nested
    explicit `verify_unavailable` span is part of that window and must not be summed
    again (codex r3: 60m verify + nested 30m downtime reported 90m excluded).
    Mutation probe: add vu unconditionally -> excluded 3600->5400 and this reds."""
    rows = [
        {
            "arc_id": "a",
            "phases": {
                "verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"},
                "verify_unavailable": {
                    "start": "2026-08-18T00:10:00Z",
                    "end": "2026-08-18T00:40:00Z",
                },
            },
            "round_outcomes": {"1": {"terminal": "REVIEWER_UNAVAILABLE"}},
        }
    ]
    n6, hours, excluded_s = am.n6(rows, [])
    assert n6 is None and hours == 0.0 and excluded_s == 3600.0


def test_n6_downtime_overlap_is_interval_arithmetic():
    """codex r5: the downtime window carries timestamps, so each phase loses exactly
    its measured OVERLAP -- an outage overlapping edit is removed from edit, and an
    outage outside both phases removes nothing. Mutation probe: revert to the scalar
    verify-only clip -> the edit-overlap case reports 2.0h instead of 1.5h, reds."""
    # vu 00:30-01:30 straddles verify's tail (30m) and edit's head (30m):
    # denominator = (1h - 0.5h) + (1h - 0.5h) = 1.0h; excluded = 1h.
    straddle = [
        {
            "arc_id": "a",
            "phases": {
                "verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"},
                "edit": {"start": "2026-08-18T01:00:00Z", "end": "2026-08-18T02:00:00Z"},
                "verify_unavailable": {
                    "start": "2026-08-18T00:30:00Z",
                    "end": "2026-08-18T01:30:00Z",
                },
            },
            "round_outcomes": {"1": {"terminal": "APPROVE"}},
        }
    ]
    n6, hours, excluded_s = am.n6(straddle, [])
    assert n6 == 0.0 and hours == 1.0 and excluded_s == 3600.0
    # vu disjoint from both phases: nothing subtracted, still bucketed.
    disjoint = [
        {
            "arc_id": "a",
            "phases": {
                "verify": {"start": "2026-08-18T00:00:00Z", "end": "2026-08-18T01:00:00Z"},
                "verify_unavailable": {
                    "start": "2026-08-18T05:00:00Z",
                    "end": "2026-08-18T05:30:00Z",
                },
            },
            "round_outcomes": {"1": {"terminal": "APPROVE"}},
        }
    ]
    n6, hours, excluded_s = am.n6(disjoint, [])
    assert n6 == 0.0 and hours == 1.0 and excluded_s == 1800.0


def test_phase_spans_negative_span_fails_loud():
    """A reversed pair (end before start) is corrupt phase state -- the edges are
    recorded independently so the shape is representable; it must abort, never flow
    a negative duration into N6."""
    row = {
        "arc_id": "a",
        "phases": {"verify": {"start": "2026-08-18T02:00:00Z", "end": "2026-08-18T01:00:00Z"}},
    }
    with pytest.raises(am.AbortError, match="end precedes start"):
        am.phase_spans(row)


# ---------------------------------------------------------------------------
# U-HE-38 / C-HE-28: joint (concurrent_lanes_at_open, arc_type) cohorts, the
# ROADMAP_STATUS_DRIFT join, and the correlational header.
# ---------------------------------------------------------------------------


#: lanes -> the SIBLING count the producer actually stores (`open_with_sensor` sets it
#: from `sibling_open_count`, which excludes the arc itself, so a solo arc stores 0).
#: Fixtures use the producer's real scale, including 0, rather than writing lane counts
#: into a sibling field.
_SIBLINGS_FOR_LANES = {1: 0, 2: 1, 4: 3}


def _joint_rows() -> list[dict]:
    """C-HE-28 Verification fixture: N=1/2/4 LANES x arc_type, three arcs per cell."""
    return [
        {
            "arc_id": f"{n}-{t}-{i}",
            "levers_active": [],
            "arc_span_s": 60.0 * n,
            "review_rounds": 1,
            "round_completeness": "complete",
            "concurrent_lanes_at_open": _SIBLINGS_FOR_LANES[n],
            "arc_type_open": t,
            "lane_id": f"lane-{n}",
        }
        for n in (1, 2, 4)
        for t in ("inventing", "applying")
        for i in range(3)
    ]


def _drift_row(arc_id: str, lane_id: str, **over) -> dict:
    """A refresh-collision row, lane-attributed per C-HE-24 §6.

    The detection names itself in `producer`, which is where every durable detection
    in the live log names its site, and `finding_type` carries the closed lifecycle
    vocabulary. B-237 records that contract for the unbuilt emitter.
    """
    return {
        "finding_id": f"codex_context_guard:head:{arc_id}:1",
        "producer": "ROADMAP_STATUS_DRIFT",
        "finding_type": "terminal-block",
        "record_kind": "finding",
        "disposition": None,
        "lane_id": lane_id,
        "arc_id": arc_id,
    } | over


def _run_summary(tmp_path: Path, monkeypatch, capsys, rows: list[dict], gate: list[dict] | None):
    ledger = tmp_path / "l.jsonl"
    ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(am, "LEDGER", ledger)
    if gate is None:
        monkeypatch.setattr(am, "GATE_LOG", tmp_path / "absent.jsonl")
    else:
        path = tmp_path / "g.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in gate))
        monkeypatch.setattr(am, "GATE_LOG", path)
    am.summary(argparse.Namespace())
    return capsys.readouterr().out


# mutation-probe: match the drift class on `producer` (the plan skeleton's
# predicate) instead of `finding_type` -> the numerator empties and both the
# `N=4: 1/6` cell and the "1 ROADMAP_STATUS_DRIFT row(s)" line go red.
def test_cohort_by_concurrent_lanes_at_open_and_arc_type(tmp_path: Path, monkeypatch, capsys):
    """The joint split, its medians, the correlational header, and a drift row
    joined to its arc's lane count."""
    out = _run_summary(
        tmp_path,
        monkeypatch,
        capsys,
        _joint_rows(),
        [
            _drift_row("4-inventing-0", "lane-4"),
            # Negative control: a real reviewer finding shares the log and the
            # arc space, and must NOT enter the refresh-collision numerator.
            {
                "finding_id": "codex_review_wrapper:head:abc:1",
                "producer": "codex_review_wrapper",
                "finding_type": "terminal-block",
                "lane_id": "lane-4",
                "arc_id": "4-applying-0",
            },
        ],
    )
    assert "CORRELATIONAL" in out and "operator-chosen" in out
    # Both key components render through json.dumps, so an absent label could
    # never be mistaken for a string (see test_joint_cohort_labels_null below).
    assert '-- JOINT (N=2, "applying") (n=3) arc span 2.0m (n=3, 2.0-2.0)' in out
    assert '-- JOINT (N=1, "inventing") (n=3) arc span 1.0m (n=3, 1.0-1.0)' in out
    assert '-- JOINT (N=4, "applying") (n=3) arc span 4.0m (n=3, 4.0-4.0)' in out
    assert "N=1: --/0 of 6, N=2: --/0 of 6, N=4: 1/1" in out, (
        "per cohort, and both sides are ARCS: 1 affected of 1 observed at N=4; the other "
        "cohorts had no arc observed at all, so they carry no denominator to divide"
    )
    assert "1 distinct ROADMAP_STATUS_DRIFT finding(s)" in out
    assert "1 of 3 cohort(s) had an arc" in out, "per-cohort measurability is reported"


def test_drift_join_never_reports_an_absent_log_as_a_measured_zero(
    tmp_path: Path, monkeypatch, capsys
):
    """Absent gate log: the numerator is stated as 0 rows out of 0, alongside
    N6's explicit "gate log absent" -- neither reads as a collision-free cohort."""
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), None)
    assert "0 distinct ROADMAP_STATUS_DRIFT finding(s)" in out and "among 0 gate" in out
    assert "never looked at" in out, "the caveat naming the ambiguity must print"
    assert "N6 problems-prevented/hour  -- (gate log absent" in out


# mutation-probe: drop the unjoinable/mismatch counters and print only the hits
# -> the two rows the join could not honour vanish silently.
def test_drift_rows_that_do_not_join_are_counted_not_dropped(tmp_path: Path, monkeypatch, capsys):
    """A drift row whose arc is absent from the ledger, and one whose lane_id
    contradicts the ledger's, are each reported rather than skipped past. A
    ledger row with no lane_id is ABSENT, not disagreeing, so it is no mismatch."""
    rows = _joint_rows()
    rows.append(
        {
            "arc_id": "legacy-0",
            "levers_active": [],
            "arc_span_s": 60.0,
            "review_rounds": 1,
            "round_completeness": "complete",
            "concurrent_lanes_at_open": 0,  # 0 siblings == 1 lane
            "arc_type_open": "applying",
            "lane_id": None,  # predates the lane field
        }
    )
    out = _run_summary(
        tmp_path,
        monkeypatch,
        capsys,
        rows,
        [
            _drift_row("4-inventing-0", "lane-4"),  # joins, lane agrees
            _drift_row("no-such-arc", "lane-9"),  # unjoinable
            _drift_row("2-applying-1", "lane-WRONG"),  # joins, lane disagrees
            _drift_row("legacy-0", "lane-anything"),  # ledger lane_id is absent
        ],
    )
    # `drift` is the ATTRIBUTABLE subset: the unjoinable and the lane-mismatched rows
    # are observed but never become incidences, so 4 rows yield 2 distinct findings.
    assert "2 distinct ROADMAP_STATUS_DRIFT finding(s)" in out
    assert (
        "4 drift-class row(s) of any kind observed, 1 unjoinable, 1 EXCLUDED for a lane_id" in out
    )
    # The lane-disagreeing row joined arc "2-applying-1" by arc_id, so an arc_id-only
    # numerator would read N=2: 1/6. It is excluded, so N=2 stays 0: a cell built from
    # rows whose two attributions contradict each other measures nothing.
    # N=2's only row was lane-mismatched, so it is unattributable: that cohort was
    # never validly looked at and reads `--`, not a measured 0. The legacy row sits at
    # N=1 (absent key = C-HE-25 baseline) and was observed, so N=1 has a denominator.
    assert "N=1: 1/1, N=2: --/0 of 6, N=4: 1/1" in out


def test_joint_cohort_labels_null_and_sorts_the_unlabelled_cells_last(
    tmp_path: Path, monkeypatch, capsys
):
    """An unlabelled component groups under `null` -- a key, not an error -- rendered
    as the JSON literal so it can never read as a cohort named "None", and sorted
    after every labelled cell. Both axes are exercised: an unlabelled `arc_type_open`,
    and an explicitly-null lane count (a row lacking the lane KEY is the N=1 baseline
    instead, per C-HE-25, which the predating-row test pins)."""
    rows = _joint_rows()[:3]
    rows.append({"arc_id": "old-0", "levers_active": [], "review_rounds": 2})
    rows.append(
        {
            "arc_id": "unknown-0",
            "levers_active": [],
            "review_rounds": 2,
            "concurrent_lanes_at_open": None,
            "arc_type_open": None,
        }
    )
    out = _run_summary(tmp_path, monkeypatch, capsys, rows, [])
    joint = out.split("-- JOINT", 1)[1]
    assert "-- JOINT (N=1, null) (n=1) arc span --" in out, "unlabelled arc_type renders null"
    assert "-- JOINT (N=null, null) (n=1) arc span --" in out, "explicit null lane count"
    assert "None" not in joint, "never a cohort named None"
    assert out.index('(N=1, "inventing")') < out.index("(N=null, null)"), "labelled cells first"
    assert "N=1: --/0 of 4, N=null: --/0 of 1" in out


# mutation-probe: count `gate_rows` directly instead of reducing by finding_id ->
# the adjudicated finding is counted twice and N=4 reads 2/6.
def test_drift_incidence_counts_findings_not_log_rows(tmp_path: Path, monkeypatch, capsys):
    """An adjudication row copies finding_type/arc_id verbatim from its finding
    (measured at U-HE-38 r1: 527 of 2260 finding_ids), so counting rows would count
    every adjudicated collision at least twice -- and could push a cell's numerator
    past its own denominator. One finding is one incidence."""
    finding = _drift_row("4-inventing-0", "lane-4")
    adjudication = finding | {"record_kind": "finding_adjudication", "disposition": "accepted"}
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), [finding, adjudication])
    assert "N=4: 1/1" in out, "one finding, two rows -> one affected arc of one observed"
    assert "1 distinct ROADMAP_STATUS_DRIFT finding(s)" in out
    assert "among 2 gate" in out, "the row count stays visible beside the finding count"


# mutation-probe: drop the `disposition != "rejected"` filter -> N=4 reads 1/6.
def test_a_refuted_drift_finding_is_not_a_collision(tmp_path: Path, monkeypatch, capsys):
    """Last-write-wins over finding_id, then `rejected` drops out: the same rule
    C-HE-29 §2 states for unique_catch. A refuted collision is not a collision."""
    finding = _drift_row("4-inventing-0", "lane-4")
    refutation = finding | {"record_kind": "finding_adjudication", "disposition": "rejected"}
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), [finding, refutation])
    assert "N=4: 0/1" in out, "the arc was observed, so 0 is a measurement here"
    assert "0 distinct ROADMAP_STATUS_DRIFT finding(s)" in out


# mutation-probe: widen the predicate back to `DRIFT_DETECTION in (finding_type,
# producer)` -> the finding_type-only row below is counted and this test goes red.
def test_drift_detection_binds_to_producer_only(tmp_path: Path, monkeypatch, capsys):
    """`producer` names the detection site; `finding_type` carries the closed lifecycle
    vocabulary and is an unconstrained string. Binding to producer alone is what stops
    an unrelated producer's row, whose classification happens to carry this name, being
    counted as a refresh collision. B-237 records that obligation for the emitter."""
    out = _run_summary(
        tmp_path,
        monkeypatch,
        capsys,
        _joint_rows(),
        [_drift_row("2-applying-0", "lane-2")],
    )
    assert "N=2: 1/1" in out, "the producer carrier counts"

    # The name in `finding_type` instead: NOT a detection, however suggestive.
    out = _run_summary(
        tmp_path,
        monkeypatch,
        capsys,
        _joint_rows(),
        [
            _drift_row("2-applying-0", "lane-2")
            | {"producer": "some-other-checker", "finding_type": "ROADMAP_STATUS_DRIFT"}
        ],
    )
    assert "N=2: --/0 of 6" in out, "finding_type is not the carrier"
    assert "0 drift-class row(s) of any kind observed" in out

    # Negative control: the name only in free text is not a detection.
    out = _run_summary(
        tmp_path,
        monkeypatch,
        capsys,
        _joint_rows(),
        [
            {
                "finding_id": "codex_review_wrapper:head:x:1",
                "producer": "codex_review_wrapper",
                "finding_type": "terminal-block",
                "record_kind": "finding",
                "disposition": None,
                "lane_id": "lane-2",
                "arc_id": "2-applying-0",
                "observed_evidence": "a review finding that merely mentions "
                "ROADMAP_STATUS_DRIFT in its prose",
            }
        ],
    )
    # Sharper than 0/6: the row is not even OBSERVED, so the cell is unavailable.
    assert "N=2: --/0 of 6" in out and "0 drift-class row(s) of any kind observed" in out


# mutation-probe: drop the `if measurable` guard and always render hits[n] -> the
# unwired case prints 0/6 and this test goes red.
def test_an_unobserved_numerator_renders_unavailable_not_zero(tmp_path: Path, monkeypatch, capsys):
    """No drift-class row of any kind means the numerator was never looked at. The
    denominator is real and stays visible; the numerator is `--`. A prose caveat
    cannot stop a parser or a truncated paste from reading `0/6` as a rate."""
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), [])
    assert "N=1: --/0 of 6, N=2: --/0 of 6, N=4: --/0 of 6" in out
    assert "0/6" not in out, "an unwired source must never render a digit numerator"
    assert "never looked at" in out


def test_a_no_finding_marker_makes_a_zero_legitimate(tmp_path: Path, monkeypatch, capsys):
    """C-HE-29 §2's device: a `no_finding` marker records that the emitter looked and
    saw nothing, which is observation without incidence. It makes the cohort countable
    -- so 0 becomes a measurement -- while contributing nothing to the numerator."""
    marker = _drift_row("4-inventing-0", "lane-4") | {
        "record_kind": "no_finding",
        "finding_id": "codex_context_guard:head:marker:1",
    }
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), [marker])
    # Per cohort: the marker names an N=4 arc, so ONLY N=4 becomes countable. The
    # other cohorts were not looked at and must not inherit its zero.
    assert "N=1: --/0 of 6, N=2: --/0 of 6, N=4: 0/1" in out
    assert "0 distinct ROADMAP_STATUS_DRIFT finding(s)" in out, "a marker is not an incidence"
    assert "1 drift-class row(s) of any kind observed" in out
    assert "1 of 3 cohort(s) had an arc" in out


# mutation-probe: replace lanes_at_open() with r.get("concurrent_lanes_at_open") ->
# the two populations pool into one N=null cohort and this test goes red.
def test_a_row_predating_the_lane_field_is_not_a_row_that_recorded_null(
    tmp_path: Path, monkeypatch, capsys
):
    """Two different facts that `dict.get()` renders identically. A row whose KEY IS
    ABSENT predates the field and IS C-HE-25's implicit N=1 baseline — C-HE-28 §3
    places 18 such rows at `(N=1, ...)` at a HEAD where no row carried the field. A row
    CARRYING an explicit null has the field and its best-effort C-HE-03 §7 sensor
    recorded nothing: an unknown, not a baseline. Pooling them puts a known cohort into
    an unknown one."""
    rows = [
        # predates the field entirely
        {
            "arc_id": "old-0",
            "levers_active": [],
            "arc_span_s": 60.0,
            "review_rounds": 1,
            "round_completeness": "complete",
            "arc_type_open": None,
        },
        # has the field; the sensor recorded nothing
        {
            "arc_id": "new-0",
            "levers_active": [],
            "arc_span_s": 600.0,
            "review_rounds": 1,
            "round_completeness": "complete",
            "concurrent_lanes_at_open": None,
            "arc_type_open": None,
        },
    ]
    # A THIRD row, storing 0 siblings: a solo arc recorded by the live sensor. It is
    # ONE LANE, so it belongs in the same cohort as the pre-field row — which is what
    # makes C-HE-28 §3's "(N=1, ...) n=18" true of a HEAD where no row carried the
    # field. Reporting the raw field would split them and label this one `N=0`.
    rows.append(
        {
            "arc_id": "solo-0",
            "levers_active": [],
            "arc_span_s": 60.0,
            "review_rounds": 1,
            "round_completeness": "complete",
            "concurrent_lanes_at_open": 0,
            "arc_type_open": None,
        }
    )
    out = _run_summary(tmp_path, monkeypatch, capsys, rows, [])
    assert "-- JOINT (N=1, null) (n=2) arc span" in out, (
        "absent key and 0 siblings are the same 1-lane cohort"
    )
    assert "-- JOINT (N=null, null) (n=1) arc span 10.0m" in out, "explicit null is unknown"
    assert "N=0" not in out, "no arc runs in zero lanes; the stored 0 is a SIBLING count"
    assert "N=1: --/0 of 2, N=null: --/0 of 1" in out
    joint_lines = [ln for ln in out.splitlines() if ln.startswith("-- JOINT")]
    assert len(joint_lines) == 2, (
        "two cells: the 1-lane cohort (pre-field + solo) and the unknown one — the "
        "explicit null must never be absorbed into a measured cohort"
    )


# mutation-probe: count findings instead of distinct affected arcs -> N=4 reads 2/1,
# a proportion greater than one, and this test goes red.
def test_two_collisions_on_one_arc_are_one_affected_arc(tmp_path: Path, monkeypatch, capsys):
    """Reducing by finding_id removes duplicate ROWS for one finding; it does nothing
    about two DIFFERENT findings on the same arc, which carry distinct finding_ids and
    would each increment a finding-based numerator. The arc appears once in the
    denominator, so a finding count can exceed it — `2/1` is not a thing incidence can
    be. Both sides of the ratio are distinct arcs."""
    first = _drift_row("4-inventing-0", "lane-4")
    second = _drift_row("4-inventing-0", "lane-4") | {
        "finding_id": "codex_context_guard:head:4-inventing-0:2"
    }
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), [first, second])
    assert "N=4: 1/1" in out, "one arc affected, however many times it collided"
    assert "2/1" not in out, "a proportion above one is unrepresentable, not merely unlikely"
    assert "2 distinct ROADMAP_STATUS_DRIFT finding(s)" in out, "both findings are still seen"


def test_an_unobserved_arc_contributes_no_exposure(tmp_path: Path, monkeypatch, capsys):
    """The denominator is arcs actually LOOKED AT, never cohort size. Six arcs ran at
    N=4 and one was observed: reporting `0/6` would assert five unobserved arcs were
    collision-free, which is the empty-versus-unlooked confusion hiding in the
    denominator after being driven out of the flag and the numerator."""
    marker = _drift_row("4-inventing-0", "lane-4") | {
        "record_kind": "no_finding",
        "finding_id": "codex_context_guard:head:marker:1",
    }
    out = _run_summary(tmp_path, monkeypatch, capsys, _joint_rows(), [marker])
    assert "N=4: 0/1" in out, "one observed arc, no collision on it"
    assert "0/6" not in out, "cohort size is not exposure"
    assert "N=1: --/0 of 6" in out, "an entirely unobserved cohort still names its size"

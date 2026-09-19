"""U-HE-57: per-arc wall-clock, the tracked outcome of spec v1.9 (C-HE-28 §2, X9h)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arc_wallclock as aw
import reservations as rs

T0 = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


def _t(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def _timeline(arc="a", *, review=(10, 40), merged=50, released=60, lanes=None) -> aw.Timeline:
    first, last = review if review else (None, None)
    return aw.Timeline(
        arc_id=arc,
        pr=1,
        reserved=T0,
        review_start=_t(first) if first is not None else None,
        last_review=_t(last) if last is not None else None,
        merged=_t(merged),
        released=_t(released) if released is not None else None,
        lanes=lanes,
    )


def test_phases_split_the_arc_at_its_recorded_instants():
    ph = aw.phases(_timeline())
    assert ph == {"build": 10, "review": 30, "to_merge": 10, "door": 10, "total": 60}


def test_an_unrecorded_release_leaves_total_unmeasured_not_shortened():
    # total is reserved -> release (X9h); ending it at the merge would understate the arc
    ph = aw.phases(_timeline(review=None, released=None))
    assert ph["build"] is None and ph["review"] is None and ph["door"] is None
    assert ph["total"] is None
    assert ph["to_merge"] is None


def test_summary_mean_and_median_are_distinct_statistics():
    s = aw.summarize(
        [_timeline("a", released=30), _timeline("b", released=40), _timeline("c", released=110)]
    )
    assert s["total"] == {"n": 3, "mean": 60, "median": 40}


def test_summary_counts_only_arcs_that_recorded_the_phase():
    s = aw.summarize([_timeline("a", released=60), _timeline("b", released=None)])
    assert s["total"]["n"] == 1 and s["to_merge"]["n"] == 2


def test_cohorts_split_the_total_by_lanes_in_numeric_order_unknown_last():
    tl = [
        _timeline("a", released=30, lanes=1),
        _timeline("b", released=50, lanes=1),
        _timeline("c", released=120, lanes=10),
        _timeline("d", released=90, lanes=None),
        _timeline("e", released=70, lanes=2),
    ]
    c = aw.by_cohort(tl)
    assert list(c) == [1, 2, 10, None]
    assert c[1] == {"n": 2, "mean": 40, "median": 40}
    assert c[10]["mean"] == 120 and c[None]["mean"] == 90


def test_latest_windows_measured_and_unmeasured_arcs_together_by_reservation():
    old = aw.Timeline("old", 1, _t(0), None, None, _t(10), _t(20), 1)
    mid = aw.Timeline("mid", 2, _t(5), None, None, _t(90), _t(95), 1)
    older_gap = aw.Unmeasured("older-gap", _t(-5), "git cannot resolve")
    newest_gap = aw.Unmeasured("newest-gap", _t(30), "git cannot resolve")
    # the newest arc is unmeasured: it holds its window slot, it is not replaced by an
    # older measurable arc, and older unmeasured arcs fall outside the window
    assert aw.latest([old, mid], [older_gap, newest_gap], 1) == ([], [newest_gap])
    assert aw.latest([mid, old], [older_gap, newest_gap], 2) == ([mid], [newest_gap])


def test_goal_is_met_at_exactly_sixty_minutes_and_not_above():
    assert "-> MET" in aw.render([_timeline(released=60)], [])
    assert "-> NOT MET" in aw.render([_timeline(released=61)], [])
    assert aw.goal_verdict(None) == "no arcs with a recorded release"


def test_last_review_is_the_latest_review_row_only():
    rows = [
        {"arc_id": "a", "producer": "merge-gate-concurrency", "ts": "2026-09-18T12:40:00Z"},
        {"arc_id": "a", "producer": "codex_review_wrapper", "ts": "2026-09-18T12:10:00Z"},
        {"arc_id": "a", "producer": "claude_absorber", "ts": "2026-09-18T11:00:00Z"},
        {"arc_id": "a", "producer": "merge-door", "ts": "2026-09-18T14:00:00Z"},
    ]
    assert aw._last_review(rows) == {"a": _t(40)}


# ── the effectful edge, over real stores ─────────────────────────────────────


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def stores(tmp_path, monkeypatch):
    """A queue (reservations + door), an empty gate log and a repo with one landing (#7)."""
    queue = tmp_path / "queue"
    (queue / "reservations").mkdir(parents=True)
    (queue / "merge-door").mkdir()
    monkeypatch.setattr(rs, "QUEUE_DIR", queue)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    ident = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
    _git(repo, *ident, "commit", "-q", "--allow-empty", "-m", "land (#7)")
    sha = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "update-ref", "refs/remotes/origin/main", sha)
    log = tmp_path / "log.jsonl"
    log.write_text("")
    return queue, repo, log, sha


def _reserve(queue: Path, arc: str, **rec) -> None:
    (queue / "reservations" / arc).mkdir()
    base = {"state": "merged", "reserved_at": "2026-09-18T12:00:00Z", "pr": None}
    (queue / "reservations" / arc / "1.json").write_text(json.dumps(base | rec))


def _release(queue: Path, token: str, arc: str, at: datetime) -> None:
    f = queue / "merge-door" / f"released.{token}"
    f.write_text(json.dumps({"reservation_id": arc}))
    os.utime(f, (at.timestamp(), at.timestamp()))


def test_load_reads_the_stores_and_names_unmeasurable_arcs(stores):
    queue, repo, log, sha = stores
    verify = {"verify": {"start": "2026-09-18T12:05:00Z", "end": "2026-09-18T12:09:00Z"}}
    _reserve(queue, "with-sha", merge_sha=sha, pr=7, concurrent_lanes_at_open=2, phases=verify)
    _reserve(queue, "by-subject", merge_sha=None, pr=7, concurrent_lanes_at_open=None)
    _reserve(queue, "bypassed", merge_sha=None, pr=None)
    _reserve(queue, "lost-sha", merge_sha="0" * 40, pr=8)
    _reserve(queue, "open", state="open")
    _release(queue, "tok", "with-sha", _t(75))
    _release(queue, "tok0", "with-sha", _t(65))  # an earlier release record of the same arc
    row = {"arc_id": "with-sha", "producer": "codex_review_wrapper", "ts": "2026-09-18T12:10:00Z"}
    log.write_text(json.dumps(row) + "\n")
    timelines, unmeasured = aw.load(log, repo, queue / "merge-door")
    by_arc = {t.arc_id: t for t in timelines}
    assert set(by_arc) == {"with-sha", "by-subject"}
    assert by_arc["with-sha"].released == _t(75)  # the LATEST released record's mtime
    assert by_arc["with-sha"].review_start == _t(5)  # the verify span, not the first row
    assert by_arc["with-sha"].last_review == _t(10)
    assert by_arc["by-subject"].review_start is None  # no span recorded: no substitute
    assert by_arc["with-sha"].merged_source == "reservation"
    # the sensor stores siblings; the cohort key is lanes (arc_metrics.lanes_at_open)
    assert by_arc["with-sha"].lanes == 3
    assert by_arc["by-subject"].lanes is None  # an explicit null is unknown
    assert by_arc["by-subject"].merged_source == "git-subject"
    assert by_arc["by-subject"].released is None
    # one arc git cannot resolve is unmeasured; the rest of the report stands
    assert {u.arc_id: u.reason.split(" ")[0] for u in unmeasured} == {
        "bypassed": "merged",
        "lost-sha": "git",
    }


def test_a_missing_reservation_store_fails_loudly(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "QUEUE_DIR", tmp_path / "missing")
    with pytest.raises(aw.StoreError, match="reservation store"):
        aw.load(tmp_path / "log.jsonl", tmp_path, tmp_path / "door")


def test_a_corrupt_reservation_is_a_store_error_not_a_traceback(stores):
    queue, repo, log, _ = stores
    (queue / "reservations" / "a").mkdir()
    (queue / "reservations" / "a" / "1.json").write_text("{not json")
    with pytest.raises(aw.StoreError, match="reservation store unreadable"):
        aw.load(log, repo, queue / "merge-door")


def test_a_planted_generation_symlink_is_refused_by_the_canonical_reader(stores, tmp_path):
    queue, repo, log, _ = stores
    forged = tmp_path / "forged.json"
    forged.write_text(json.dumps({"state": "merged", "reserved_at": "2026-09-18T12:00:00Z"}))
    (queue / "reservations" / "a").mkdir()
    (queue / "reservations" / "a" / "1.json").symlink_to(forged)
    with pytest.raises(aw.StoreError, match="symlink"):
        aw.load(log, repo, queue / "merge-door")


def test_a_non_generation_file_beside_the_generations_is_ignored(stores):
    queue, repo, log, sha = stores
    _reserve(queue, "a", merge_sha=sha, pr=7)
    (queue / "reservations" / "a" / "notes.json").write_text("{}")
    timelines, _ = aw.load(log, repo, queue / "merge-door")
    assert [t.arc_id for t in timelines] == ["a"]


def test_a_corrupt_release_record_is_a_store_error(stores):
    queue, *_ = stores
    (queue / "merge-door" / "released.tok").write_text("{not json")
    with pytest.raises(aw.StoreError, match="release record"):
        aw._releases(queue / "merge-door")


def test_last_must_be_positive(capsys):
    for bad in ("0", "-3"):
        with pytest.raises(SystemExit) as exc:
            aw.main(["--last", bad])
        assert exc.value.code == 2
    assert "must be >= 1" in capsys.readouterr().err


def test_a_reservation_older_than_the_sensor_is_the_one_lane_baseline(stores):
    queue, repo, log, sha = stores
    _reserve(queue, "legacy", merge_sha=sha, pr=7)  # no concurrent_lanes_at_open key
    timelines, _ = aw.load(log, repo, queue / "merge-door")
    assert [t.lanes for t in timelines] == [1]


def test_an_unreadable_origin_main_only_unmeasures_arcs_that_need_it(stores):
    queue, repo, log, sha = stores
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    _reserve(queue, "with-sha", merge_sha=sha, pr=7)
    _reserve(queue, "by-subject", merge_sha=None, pr=7)
    timelines, unmeasured = aw.load(log, repo, queue / "merge-door")
    assert [t.arc_id for t in timelines] == ["with-sha"]
    assert [u.arc_id for u in unmeasured] == ["by-subject"]
    assert "origin/main" in unmeasured[0].reason


def test_a_symlinked_release_record_is_refused(stores, tmp_path):
    queue, *_ = stores
    forged = tmp_path / "forged"
    forged.write_text(json.dumps({"reservation_id": "a"}))
    (queue / "merge-door" / "released.tok").symlink_to(forged)
    with pytest.raises(aw.StoreError, match="symlink"):
        aw._releases(queue / "merge-door")


def test_a_symlinked_door_directory_is_refused(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "door").symlink_to(tmp_path / "real")
    with pytest.raises(aw.StoreError, match="symlink"):
        aw._releases(tmp_path / "door")


def test_the_cli_publishes_lanes_cohorts_and_the_goal(stores, monkeypatch, capsys):
    queue, repo, log, sha = stores
    _reserve(queue, "solo", merge_sha=sha, pr=7, concurrent_lanes_at_open=0)
    _release(queue, "tok", "solo", _t(45))
    monkeypatch.setattr(aw, "GATE_LOG", log)
    monkeypatch.setattr(aw, "REPO", repo)
    monkeypatch.setattr(aw.merge_door, "DOOR", queue / "merge-door")
    assert aw.main(["--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["arcs"][0]["lanes"] == 1 and out["arcs"][0]["total"] == 45
    assert out["arcs"][0]["merged_source"] == "reservation"
    assert out["by_lanes"] == {"1": {"n": 1, "mean": 45, "median": 45}}
    assert out["goal"] == "MET"
    assert aw.main([]) == 0
    text = capsys.readouterr().out
    assert "  1                       1       45       45" in text
    assert "-> MET" in text


def test_a_reservation_merge_sha_takes_precedence_over_the_squash_subject(stores):
    queue, repo, log, first = stores
    env = {**os.environ, "GIT_COMMITTER_DATE": "2026-09-18T15:00:00Z"}
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
         "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "later (#9)"],
        check=True, env=env,
    )  # fmt: skip
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    _reserve(queue, "a", merge_sha=first, pr=9)
    (t,), _ = aw.load(log, repo, queue / "merge-door")
    assert t.merged_source == "reservation"
    assert t.merged == aw._commit_time(repo, first)
    assert t.merged != aw._commit_time(repo, "HEAD")

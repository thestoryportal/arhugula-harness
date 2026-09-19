"""U-HE-57: per-arc wall-clock, the tracked outcome of spec v1.9 (C-HE-28 §2, X9h)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arc_wallclock as aw

T0 = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


def _t(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def _timeline(arc="a", *, review=(10, 40), merged=50, released=60) -> aw.Timeline:
    first, last = review if review else (None, None)
    return aw.Timeline(
        arc_id=arc,
        pr=1,
        reserved=T0,
        first_review=_t(first) if first is not None else None,
        last_review=_t(last) if last is not None else None,
        merged=_t(merged),
        released=_t(released) if released is not None else None,
    )


def test_phases_split_the_arc_at_its_recorded_instants():
    ph = aw.phases(_timeline())
    assert ph == {"build": 10, "review": 30, "to_merge": 10, "door": 10, "total": 60}


def test_a_missing_instant_leaves_only_its_phases_unrecorded():
    ph = aw.phases(_timeline(review=None, released=None))
    assert ph["build"] is None and ph["review"] is None and ph["door"] is None
    assert ph["total"] == 50  # falls back to the merge instant, never dropped


def test_summary_reports_mean_median_and_count_per_phase():
    s = aw.summarize([_timeline("a", released=60), _timeline("b", released=120)])
    assert s["total"] == {"n": 2, "mean": 90, "median": 90}


def test_latest_keeps_the_most_recently_merged_arcs():
    old, new = _timeline("old", merged=10, released=20), _timeline("new", merged=90, released=95)
    assert [t.arc_id for t in aw.latest([new, old], 1)] == ["new"]


def test_render_states_whether_the_goal_is_met():
    assert "-> MET" in aw.render([_timeline(released=45)], [])
    assert "-> NOT MET" in aw.render([_timeline(released=90)], [])


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


def test_load_reads_the_stores_and_names_unmeasurable_arcs(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(
        repo,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "land (#7)",
    )
    sha = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "update-ref", "refs/remotes/origin/main", sha)
    queue = tmp_path / "queue"
    for arc, rec in (
        (
            "with-sha",
            {"state": "merged", "merge_sha": sha, "pr": 7, "reserved_at": "2026-09-18T12:00:00Z"},
        ),
        (
            "by-subject",
            {"state": "merged", "merge_sha": None, "pr": 7, "reserved_at": "2026-09-18T12:00:00Z"},
        ),
        (
            "bypassed",
            {
                "state": "merged",
                "merge_sha": None,
                "pr": None,
                "reserved_at": "2026-09-18T12:00:00Z",
            },
        ),
        ("open", {"state": "open", "reserved_at": "2026-09-18T12:00:00Z"}),
    ):
        (queue / "reservations" / arc).mkdir(parents=True)
        (queue / "reservations" / arc / "1.json").write_text(json.dumps(rec))
    door = queue / "merge-door"
    door.mkdir()
    (door / "released.tok").write_text(json.dumps({"reservation_id": "with-sha"}))
    (door / "transition.tok").write_text(json.dumps({"created_at": "2026-09-18T13:00:00Z"}))
    log = tmp_path / "log.jsonl"
    log.write_text(
        json.dumps(
            {"arc_id": "with-sha", "producer": "codex_review_wrapper", "ts": "2026-09-18T12:10:00Z"}
        )
        + "\n"
    )
    timelines, unmeasured = aw.load(queue, log, repo)
    by_arc = {t.arc_id: t for t in timelines}
    assert set(by_arc) == {"with-sha", "by-subject"}
    assert by_arc["with-sha"].released == datetime(2026, 9, 18, 13, 0, tzinfo=UTC)
    assert by_arc["with-sha"].first_review == datetime(2026, 9, 18, 12, 10, tzinfo=UTC)
    assert by_arc["by-subject"].merged_source == "git-subject"
    assert [u.arc_id for u in unmeasured] == ["bypassed"]


def test_an_unreadable_store_fails_loudly(tmp_path):
    try:
        aw.load(tmp_path / "missing", tmp_path / "log.jsonl", tmp_path)
    except aw.StoreError as exc:
        assert "reservation store" in str(exc)
    else:
        raise AssertionError("a missing reservation store must raise StoreError")


def _store(tmp_path: Path, rec_text: str) -> Path:
    queue = tmp_path / "queue"
    (queue / "reservations" / "a").mkdir(parents=True)
    (queue / "reservations" / "a" / "1.json").write_text(rec_text)
    (queue / "merge-door").mkdir()
    return queue


def test_a_corrupt_record_is_a_store_error_not_a_traceback(tmp_path):
    queue = _store(tmp_path, "{not json")
    (tmp_path / "log.jsonl").write_text("")
    try:
        aw.load(queue, tmp_path / "log.jsonl", tmp_path)
    except aw.StoreError as exc:
        assert "1.json" in str(exc)
    else:
        raise AssertionError("a corrupt reservation must raise StoreError")


def test_a_release_whose_marker_was_gcd_is_unrecorded_not_an_error(tmp_path):
    queue = _store(tmp_path, json.dumps({"state": "open", "reserved_at": "2026-09-18T12:00:00Z"}))
    (queue / "merge-door" / "released.tok").write_text(json.dumps({"reservation_id": "a"}))
    assert aw._releases(queue / "merge-door") == {}


def test_last_must_be_positive(capsys):
    for bad in ("0", "-3"):
        try:
            aw.main(["--last", bad])
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError(f"--last {bad} must be refused")
    assert "must be >= 1" in capsys.readouterr().err

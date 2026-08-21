"""C-HE-06 merge-door lease — U-HE-22 primitive half (first half; the landing driver's
tests arrive with U-HE-23). No skip; no live gh (the primitive half never shells out).

Deadness is adjudicated deterministically: the fixture patches ``md._process_is_alive``
to "alive iff it is THIS process" — a fixed sentinel pid (999999) can be a live pid where
pid_max exceeds it (Linux CI's default pid_max is 4194304; the U-HE-20 r2 P3 class), so
the sentinel must never reach the real ``kill(0)`` probe.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import merge_door as md
import reservations as rs


@pytest.fixture
def door(tmp_path, monkeypatch):
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(md, "QUEUE_DIR", q)
    monkeypatch.setattr(md, "DOOR", q / "merge-door")
    monkeypatch.setattr(md, "LEASE", q / "merge-door" / "LEASE")
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    # Deterministic deadness on every platform: alive iff it is this very process.
    monkeypatch.setattr(md, "_process_is_alive", lambda pid: pid == os.getpid())
    rs.reserve("pr-1", lane_id="A", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-1", "A")
    return q


def _acq(lane="A", arc="pr-1", pr=1, now=1000.0):
    return md.acquire(
        lane_id=lane, arc_id=arc, pr=pr, head_sha="h" * 40, base_sha="b" * 40, now=now
    )


def test_acquire_payload_and_required_fields(door):
    lease = _acq()
    for k in (
        "lease_token",
        "lane_id",
        "reservation_id",
        "pr",
        "head_sha",
        "base_sha",
        "acquired_at",
        "pid",
        "host",
        "merge_attempted_at",
        "state",
        "blocked_at_sha",
        "blocked_reason",
    ):
        assert k in lease
    assert len(lease["lease_token"]) == 32
    assert lease["state"] == "held"
    assert lease["reservation_id"] == "pr-1"


# mutation-probe: drop acquire()'s LeaseHeld raise in the FileExistsError clause
def test_contention_fail_fast(door):
    _acq()
    # B must pass the P2 holder check to REACH the door (the plan sketch's
    # `_acq(lane="B", arc="pr-1")` trips HolderInvariant on A's arc first and never
    # exercises contention): B contends holding its OWN open reservation.
    rs.reserve("pr-2", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-2", "B")
    with pytest.raises(md.LeaseHeld):
        _acq(lane="B", arc="pr-2", pr=2)


# mutation-probe: drop acquire()'s P2 holder-invariant check (pending/foreign reservations acquire)
def test_lease_holder_invariant(door):
    rs.reserve("pr-2", lane_id="B", branch="b", arc_type="inventing")  # pending, not open
    with pytest.raises(md.HolderInvariant):
        md.acquire(lane_id="B", arc_id="pr-2", pr=2, head_sha="h" * 40, base_sha="b" * 40)
    with pytest.raises(md.HolderInvariant):
        # open but held by A
        md.acquire(lane_id="B", arc_id="pr-1", pr=1, head_sha="h" * 40, base_sha="b" * 40)


def test_rate_counter_ignores_tmp_remnants(door):
    (md.DOOR / "attempts" / "A").mkdir(parents=True)
    # a crashed publish_exclusive left this
    (md.DOOR / "attempts" / "A" / ".1000.000000.4242.tmp").write_text("")
    _acq(now=1000.0)  # must not raise ValueError


# mutation-probe: drop _rate_check()'s RATE_K refusal (the 6th attempt sails through as LeaseHeld)
def test_rate_limit_sixth_refused(door):
    _acq(now=0.0)  # attempt 1 succeeds -> lease held
    for i in range(4):  # attempts 2..5 contend (LeaseHeld, counted)
        with pytest.raises(md.LeaseHeld):
            _acq(lane="A", now=1.0 + i)
    with pytest.raises(md.RateLimited):
        # 6th within 60 s -> refused (lease_acquire_rate_exceeded), NOT LeaseHeld
        _acq(lane="A", now=10.0)
    with pytest.raises(md.LeaseHeld):
        _acq(lane="A", now=61.5)  # window slid -> ordinary contention again


# mutation-probe: drop release()'s win_marker guard (path-only unlink without the marker CAS)
def test_marker_race_exactly_one_wins(door):
    lease = _acq()
    assert md.win_marker(lease["lease_token"], "release") is not None
    assert md.win_marker(lease["lease_token"], "reclaim") is None
    with pytest.raises(md.MarkerLost):
        md.release(lease)  # holder lost the marker → must stop driving


def test_release_then_history_file(door):
    lease = _acq()
    md.release(lease)
    assert md.read_lease() is None
    assert (md.DOOR / f"released.{lease['lease_token']}").exists()


def test_reclaim_two_step_and_transfers_merge_authority_only(door):
    lease = _acq(lane="A")
    with pytest.raises(md.LeaseError, match="live"):
        # same lane, holder pid ALIVE → refused (round-2 P1)
        md.reclaim(lease, lane_id="A", ground_state="OPEN")
    dead = {**lease, "pid": 999999}
    new = md.reclaim(dead, lane_id="B", ground_state="OPEN")
    assert new["lease_token"] != lease["lease_token"]
    assert new["lane_id"] == "B"
    assert new["pr"] == 1
    assert rs.holder("pr-1") == "A"  # reservation ownership NOT transferred (P2)
    assert (md.DOOR / f"reclaimed.{lease['lease_token']}").exists()


# mutation-probe: drop reclaim()'s post-publish token re-check (a foreign lease is adopted)
def test_reclaim_never_adopts_a_foreign_lease(door, monkeypatch):
    lease = _acq(lane="A")
    dead = {**lease, "pid": 999999}
    real_publish = md._publish_fresh

    def sneak_in(fresh):
        # another lane grabs the free door in the move->publish window
        rs.reserve("pr-9", lane_id="C", branch="b", arc_type="inventing")
        rs.open_with_sensor("pr-9", "C")
        md.acquire(lane_id="C", arc_id="pr-9", pr=9, head_sha="h" * 40, base_sha="b" * 40)
        real_publish(fresh)  # FileExistsError swallowed inside

    monkeypatch.setattr(md, "_publish_fresh", sneak_in)
    with pytest.raises(md.LeaseError, match="lost the door"):
        md.reclaim(dead, lane_id="B", ground_state="OPEN")
    assert md.read_lease()["lane_id"] == "C"  # the foreign lease is untouched; nothing drove pr 1


# mutation-probe: drop complete_dead_marker()'s _publish_fresh completion (the fresh lease is lost)
def test_crashed_reclaimer_completed_by_third_party_publishes_fresh_lease(door):
    """Reclaimer wins the marker (payload carries the fresh lease), moves the old lease
    aside, then dies before publishing. A third party completing the marker MUST publish
    the fresh token -- otherwise the door reads free and the attempted-state continuation
    is lost (Codex round-2 P1)."""
    lease = _acq(lane="A")
    md.mark_attempted(lease)
    dead = {**lease, "pid": 999999}
    fresh = {
        **dead,
        "lease_token": "f" * 32,
        "lane_id": "B",
        "pid": 999998,
        "state": "held",
        "merge_attempted_at": md.read_lease()["merge_attempted_at"],
    }
    m = md.win_marker(lease["lease_token"], "reclaim", extra={"fresh_lease": fresh})
    body = json.loads(m.read_text())
    body["pid"] = 999999
    m.write_text(json.dumps(body))  # creator died
    md._move_lease(lease["lease_token"], "reclaimed")  # ...after moving the old lease aside
    assert md.read_lease() is None  # door LOOKS free: the hazard
    assert md.complete_dead_marker(m) is True
    got = md.read_lease()
    assert got and got["lease_token"] == "f" * 32
    assert got["merge_attempted_at"] is not None
    assert md.complete_dead_marker(m) is False  # idempotent


# mutation-probe: drop complete_dead_marker()'s _move_lease completion (door stays locked)
def test_dead_marker_completed_by_third_party(door):
    lease = _acq()
    m = md.win_marker(lease["lease_token"], "release")
    body = json.loads(m.read_text())
    body["pid"] = 999999
    m.write_text(json.dumps(body))  # creator died mid-release
    assert md.complete_dead_marker(m) is True
    assert md.read_lease() is None  # door open again
    assert md.complete_dead_marker(m) is False  # idempotent: already done


def test_mark_attempted_is_crash_safe_sidecar(door):
    lease = _acq()
    md.mark_attempted(lease)
    assert (md.DOOR / f"LEASE.{lease['lease_token']}.attempted").exists()
    assert md.read_lease()["merge_attempted_at"] is not None
    md.mark_attempted(lease)  # idempotent


def test_blocked_and_unblock_through_marker(door):
    lease = _acq()
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    assert md.read_lease()["state"] == "blocked"
    with pytest.raises(md.LeaseError):
        md.unblock(pr=1, blocked_at_sha="x" * 40, lane_id="A")  # keyed to blocked_at_sha
    md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")
    assert md.read_lease() is None

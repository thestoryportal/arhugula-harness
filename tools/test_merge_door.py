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


def _kill_holder():
    """Test-side crash simulation: rewrite the persisted LEASE with a provably-dead pid.
    (Production never mutates LEASE in place; reclaim adjudicates from this persisted
    record, so simulating a dead holder means changing the record, not the caller dict.)"""
    body = json.loads(md.LEASE.read_text())
    body["pid"] = 999999
    md.LEASE.write_text(json.dumps(body, sort_keys=True))


def test_reclaim_two_step_and_transfers_merge_authority_only(door):
    lease = _acq(lane="A")
    with pytest.raises(md.LeaseError, match="live"):
        # same lane, holder pid ALIVE → refused (round-2 P1)
        md.reclaim(lease, lane_id="A", ground_state="OPEN")
    _kill_holder()
    new = md.reclaim(lease, lane_id="B", ground_state="OPEN")
    assert new["lease_token"] != lease["lease_token"]
    assert new["lane_id"] == "B"
    assert new["pr"] == 1
    assert rs.holder("pr-1") == "A"  # reservation ownership NOT transferred (P2)
    assert (md.DOOR / f"reclaimed.{lease['lease_token']}").exists()


# mutation-probe: drop reclaim()'s post-publish token re-check (a foreign lease is adopted)
def test_reclaim_never_adopts_a_foreign_lease(door, monkeypatch):
    lease = _acq(lane="A")
    _kill_holder()
    real_publish = md._publish_fresh

    def sneak_in(fresh):
        # another lane grabs the free door in the move->publish window
        rs.reserve("pr-9", lane_id="C", branch="b", arc_type="inventing")
        rs.open_with_sensor("pr-9", "C")
        md.acquire(lane_id="C", arc_id="pr-9", pr=9, head_sha="h" * 40, base_sha="b" * 40)
        real_publish(fresh)  # FileExistsError swallowed inside

    monkeypatch.setattr(md, "_publish_fresh", sneak_in)
    with pytest.raises(md.LeaseError, match="lost the door"):
        md.reclaim(lease, lane_id="B", ground_state="OPEN")
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


# ── codex U-HE-22 r1 corrections ─────────────────────────────────────────────


# mutation-probe: drop reclaim()'s persisted-lease deadness check (a forged dict displaces)
def test_forged_caller_dict_cannot_displace_live_holder(door):
    """Deadness comes from the PERSISTED lease: a caller copying the lease dict and
    substituting a dead pid must NOT reclaim while the real holder is driving (r1 P1)."""
    lease = _acq(lane="A")
    forged = {**lease, "pid": 999999}
    with pytest.raises(md.LeaseError, match="live"):
        md.reclaim(forged, lane_id="B", ground_state="OPEN")
    assert md.read_lease()["lease_token"] == lease["lease_token"]  # holder undisturbed


def test_reclaim_requires_the_door_current_lease(door):
    lease = _acq(lane="A")
    md.release(lease)
    with pytest.raises(md.LeaseError, match="stale reclaim"):
        md.reclaim(lease, lane_id="B", ground_state="OPEN")  # door no longer holds it


# mutation-probe: drop reclaim()'s DoorBlocked refusal (self-resume bypasses unblock)
def test_reclaim_refuses_blocked_lease(door):
    """A blocked door resumes ONLY through the operator-keyed unblock (r1 P1)."""
    lease = _acq(lane="A")
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    _kill_holder()
    with pytest.raises(md.DoorBlocked):
        md.reclaim(lease, lane_id="A", ground_state="OPEN")
    md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")  # the sanctioned path still works
    assert md.read_lease() is None


# mutation-probe: drop _publish_fresh()'s refresh-sidecar republish (continuation lost)
def test_reclaim_preserves_refresh_continuation(door):
    """The refresh continuation survives self-resume as sidecars under the NEW token; the
    base LEASE payload never absorbs it (r1 P1)."""
    lease = _acq(lane="A")
    md.mark_attempted(lease)
    from arc_metrics import publish_exclusive

    publish_exclusive(
        md._sidecar(lease["lease_token"], "refresh"),
        json.dumps({"refresh_head": "r" * 40}),
    )
    md.mark_attempted(lease, suffix="refresh")
    _kill_holder()
    new = md.reclaim(lease, lane_id="B", ground_state="OPEN")
    view = md.read_lease()
    assert view["lease_token"] == new["lease_token"]
    assert view["refresh"]["refresh_head"] == "r" * 40
    assert view["refresh"]["merge_attempted_at"] is not None
    assert view["merge_attempted_at"] is not None
    assert "refresh" not in json.loads(md.LEASE.read_text())  # sidecar-carried, not payload


def _crashed_reclaim_marker(lease):
    """Marker whose creator died after moving the old lease aside, before publishing."""
    dead = {**lease, "pid": 999999}
    fresh = {**dead, "lease_token": "f" * 32, "lane_id": "B", "pid": 999998, "state": "held"}
    m = md.win_marker(lease["lease_token"], "reclaim", extra={"fresh_lease": fresh})
    body = json.loads(m.read_text())
    body["pid"] = 999999
    m.write_text(json.dumps(body))
    md._move_lease(lease["lease_token"], "reclaimed")
    return m


# mutation-probe: drop complete_dead_marker()'s reservation-state gate (stale resurrection)
def test_completion_requires_live_reservation(door):
    """A stale reclaim marker must not resurrect authority for a TERMINATED arc:
    completion publishes only while the reservation reads `open` or `merged` (r1 P1,
    narrowed r2 P1 — `merged` is the legitimate §4(vi)–(ix) continuation state)."""
    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    rs.reserve("pr-99", lane_id="A", branch="b", arc_type="inventing")  # the superseder
    rs.transition("pr-1", "abandoned", lane_id="A", superseded_by="pr-99")
    assert md.complete_dead_marker(m) is False
    assert md.read_lease() is None  # nothing resurrected


def test_completion_allowed_during_merged_continuation(door):
    """A post-merge reclaimer crash between move and publish MUST still be completable —
    the reservation legitimately reads `merged` through post-merge CI + refresh; refusing
    would let another lane acquire mid-continuation (r2 P1)."""
    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    rs.transition("pr-1", "merged", lane_id="A")  # the §4(vi) flip happened
    assert md.complete_dead_marker(m) is True
    assert md.read_lease()["lease_token"] == "f" * 32  # continuation restored


# mutation-probe: drop release()'s persisted-state re-read (blocked/stale release passes)
def test_release_refuses_blocked_and_stale(door):
    """release() adjudicates from the persisted lease (r2 P1): a blocked door releases
    only through unblock, and a stale dict must never move ANOTHER lane's lease aside."""
    lease = _acq(lane="A")
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    with pytest.raises(md.DoorBlocked):
        md.release(lease)  # caller's dict still says held; persisted view says blocked
    md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")  # door free again
    # Door cycles to another lane; the old dict must not release the new holder's lease.
    rs.reserve("pr-9", lane_id="C", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-9", "C")
    other = md.acquire(lane_id="C", arc_id="pr-9", pr=9, head_sha="h" * 40, base_sha="b" * 40)
    with pytest.raises(md.LeaseError, match="stale release"):
        md.release(lease)
    assert md.read_lease()["lease_token"] == other["lease_token"]  # C undisturbed


# mutation-probe: drop reclaim()'s reservation-state re-check (terminated arc reclaimed)
def test_reclaim_refuses_terminated_reservation(door):
    """A dead lease whose arc was abandoned/superseded (PR may still be OPEN on GitHub)
    must not regain merge-driving authority (r2 P2)."""
    lease = _acq(lane="A")
    _kill_holder()
    rs.reserve("pr-99", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-1", "abandoned", lane_id="A", superseded_by="pr-99")
    with pytest.raises(md.LeaseError, match="terminated"):
        md.reclaim(lease, lane_id="B", ground_state="OPEN")


# mutation-probe: drop gc()'s attempts symlink/containment skip (escape deleted)
def test_gc_never_follows_attempts_symlink(door, tmp_path):
    """A planted attempts/<lane> symlink must not let GC unlink files outside QUEUE_DIR
    (r2 P1); concurrent-collector FileNotFoundError yields rather than aborting (r2 P3)."""
    outside = tmp_path / "outside-store"
    outside.mkdir()
    victim = outside / "1000.000000"
    victim.write_text("precious")
    os.utime(victim, (0, 0))  # ancient
    (md.DOOR / "attempts").mkdir(parents=True, exist_ok=True)
    (md.DOOR / "attempts" / "evil").symlink_to(outside)
    removed = md.gc()
    assert victim.exists()  # the escape was never followed
    assert not any("outside-store" in str(p) for p in removed)


# mutation-probe: drop _rate_check()'s _check_lane_id containment call
def test_lane_id_containment(door, tmp_path):
    """lane_id becomes a path component of the attempts store — absolute or traversing
    values must be refused BEFORE any filesystem write (r1 P2). The raises-match is
    deliberately the containment refusal itself: without the guard a bad lane still
    raises a DOWNSTREAM LeaseError (HolderInvariant) — after creating the escaped
    directory — so a bare LeaseError assertion would not kill the mutation."""
    escape = tmp_path / "outside-door-escape"
    for bad in (str(escape), "../evil", "a/b", ".hidden", "a:b", ""):
        with pytest.raises(md.LeaseError, match="bad lane_id"):
            _acq(lane=bad)
    assert not escape.exists()  # nothing was written outside the attempts store


def test_refused_attempt_is_recorded(door):
    """Record-then-count (r1 P2): the refusing 6th attempt is itself recorded, so a burst
    cannot under-count a not-yet-recorded peer; the LEASE CAS remains the safety fence."""
    _acq(now=0.0)
    for i in range(4):
        with pytest.raises(md.LeaseHeld):
            _acq(lane="A", now=1.0 + i)
    with pytest.raises(md.RateLimited):
        _acq(lane="A", now=10.0)
    files = [p for p in (md.DOOR / "attempts" / "A").iterdir() if not p.name.startswith(".")]
    assert len(files) == 6  # the refusal recorded its attempt too

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
import subprocess
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
    # ship-pr back-fills the merge tuple BEFORE the door (C-HE-03 §3); acquire()
    # cross-checks its inputs against this snapshot (codex r4 P2).
    rs.update_payload("pr-1", {"pr": 1, "head_sha": "a" * 40, "base_sha": "b" * 40})
    return q


def _open_backfilled(arc: str, lane: str, pr: int) -> None:
    rs.reserve(arc, lane_id=lane, branch="b", arc_type="inventing")
    rs.open_with_sensor(arc, lane)
    rs.update_payload(arc, {"pr": pr, "head_sha": "a" * 40, "base_sha": "b" * 40})


def _acq(lane="A", arc="pr-1", pr=1, now=1000.0):
    return md.acquire(
        lane_id=lane, arc_id=arc, pr=pr, head_sha="a" * 40, base_sha="b" * 40, now=now
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
    _open_backfilled("pr-2", "B", 2)
    with pytest.raises(md.LeaseHeld):
        _acq(lane="B", arc="pr-2", pr=2)


# mutation-probe: drop acquire()'s P2 holder-invariant check (pending/foreign reservations acquire)
def test_lease_holder_invariant(door):
    rs.reserve("pr-2", lane_id="B", branch="b", arc_type="inventing")  # pending, not open
    with pytest.raises(md.HolderInvariant):
        md.acquire(lane_id="B", arc_id="pr-2", pr=2, head_sha="a" * 40, base_sha="b" * 40)
    with pytest.raises(md.HolderInvariant):
        # open but held by A
        md.acquire(lane_id="B", arc_id="pr-1", pr=1, head_sha="a" * 40, base_sha="b" * 40)
    # Discriminates the PRE-check from the r3 post-publication re-validation (which also
    # raises HolderInvariant but only AFTER transiently publishing + self-releasing): the
    # pre-check path must never publish at all — no lease, no self-heal history artifact.
    assert md.read_lease() is None
    assert not list(md.DOOR.glob("released.*"))


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
    import time as _time

    lease = _acq()
    md.release(lease)
    assert md.read_lease() is None
    hist = md.DOOR / f"released.{lease['lease_token']}"
    assert hist.exists()
    # r3 P3: the history clock starts at the TRANSITION (rename re-stamps mtime), so gc's
    # 30-day retention runs from release, not from a possibly-ancient acquisition.
    assert abs(_time.time() - hist.stat().st_mtime) < 120


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
        _open_backfilled("pr-9", "C", 9)
        md.acquire(lane_id="C", arc_id="pr-9", pr=9, head_sha="a" * 40, base_sha="b" * 40)
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
    md.mark_blocked(lease, sha="c" * 40, reason="post_merge_ci_not_green")
    assert md.read_lease()["state"] == "blocked"
    with pytest.raises(md.LeaseError):
        md.unblock(pr=1, blocked_at_sha="x" * 40, lane_id="A")  # keyed to blocked_at_sha
    fresh = md.unblock(pr=1, blocked_at_sha="c" * 40, lane_id="A")
    # r3 P1: unblock mints a REPLACEMENT lease (the door typically blocks mid-continuation,
    # when the reservation reads `merged` and acquire() would refuse a re-acquire).
    view = md.read_lease()
    assert view["lease_token"] == fresh["lease_token"]
    assert view["state"] == "held" and view["pr"] == 1
    md.release(fresh)  # a lane that wants the door free releases the successor normally
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
    md.mark_blocked(lease, sha="c" * 40, reason="post_merge_ci_not_green")
    _kill_holder()
    with pytest.raises(md.DoorBlocked):
        md.reclaim(lease, lane_id="A", ground_state="OPEN")
    successor = md.unblock(pr=1, blocked_at_sha="c" * 40, lane_id="A")  # the sanctioned path
    assert md.read_lease()["lease_token"] == successor["lease_token"]


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
    # r9 P2: a claim that completed NOTHING is relinquished, keeping completion retryable
    assert not (md.DOOR / f"completed.{lease['lease_token']}").exists()
    # Discriminates the PRE-gate from the r8 post-publish retraction (which also ends with
    # an empty door, but only after transiently publishing + self-releasing): the pre-gate
    # path never publishes, so no released.* self-heal artifact may exist.
    assert not list(md.DOOR.glob("released.*"))


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
    md.mark_blocked(lease, sha="c" * 40, reason="post_merge_ci_not_green")
    with pytest.raises(md.DoorBlocked):
        md.release(lease)  # caller's dict still says held; persisted view says blocked
    successor = md.unblock(pr=1, blocked_at_sha="c" * 40, lane_id="A")
    md.release(successor)  # door free again
    # Door cycles to another lane; the old dict must not release the new holder's lease.
    _open_backfilled("pr-9", "C", 9)
    other = md.acquire(lane_id="C", arc_id="pr-9", pr=9, head_sha="a" * 40, base_sha="b" * 40)
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


# mutation-probe: drop unblock()'s fresh-lease publish + post-check (continuation stranded)
def test_unblock_resumes_continuation(door):
    """The door typically blocks DURING the merged continuation — unblock must hand the
    named lane a replacement lease (with the continuation sidecars carried over), not an
    empty door that acquire() can no longer pass (r3 P1)."""
    lease = _acq(lane="A")
    md.mark_attempted(lease)
    md.mark_blocked(lease, sha="c" * 40, reason="post_merge_ci_not_green")
    rs.transition("pr-1", "merged", lane_id="A")  # the §4(vi) flip already happened
    fresh = md.unblock(pr=1, blocked_at_sha="c" * 40, lane_id="A")
    view = md.read_lease()
    assert view["lease_token"] == fresh["lease_token"]
    assert view["state"] == "held"
    assert view["merge_attempted_at"] is not None  # continuation state carried over
    with pytest.raises(md.HolderInvariant):
        # and the door was NEVER free in a state a re-acquire could have passed:
        md.acquire(lane_id="A", arc_id="pr-1", pr=1, head_sha="a" * 40, base_sha="b" * 40)


def test_reclaim_gate_uses_persisted_reservation_id(door):
    """The reservation gate reads the PERSISTED reservation_id — a caller keeping the valid
    token but substituting another active arc's id must not bypass the terminated-arc
    refusal (r3 P1)."""
    lease = _acq(lane="A")
    _kill_holder()
    rs.reserve("pr-99", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-1", "abandoned", lane_id="A", superseded_by="pr-99")
    rs.reserve("pr-9", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-9", "B")
    forged = {**lease, "reservation_id": "pr-9"}  # an open arc, not the lease's own
    with pytest.raises(md.LeaseError, match="terminated"):
        md.reclaim(forged, lane_id="B", ground_state="OPEN")


# mutation-probe: drop acquire()'s post-publication re-validation (terminal-arc lease kept)
def test_acquire_revalidates_after_publish(door, monkeypatch):
    """The pre-check and the exclusive create are separate operations: a reconciliation
    terminalizing the reservation in between must not leave a live lease on a terminal
    arc — acquire self-releases through the marker and refuses (r3 P2)."""
    real_current = rs.current
    calls = {"n": 0}

    def flipping_current(arc_id):
        calls["n"] += 1
        cur = real_current(arc_id)
        if calls["n"] >= 2 and cur is not None:
            # the concurrent reconciliation flipped it terminal between check and publish
            return (cur[0], {**cur[1], "state": "merged"})
        return cur

    monkeypatch.setattr(rs, "current", flipping_current)
    with pytest.raises(md.HolderInvariant, match="changed during acquisition"):
        _acq(lane="A")
    monkeypatch.setattr(rs, "current", real_current)
    assert md.read_lease() is None  # self-released, never left held
    assert list(md.DOOR.glob("released.*"))  # through the marker discipline, not an unlink


# ── codex U-HE-22 r4 corrections ─────────────────────────────────────────────


# mutation-probe: drop acquire()'s reservation-tuple cross-check (authority link broken)
def test_acquire_requires_backfilled_matching_tuple(door):
    """The lease must carry the reservation's OWN back-filled merge tuple (C-HE-03 §3) —
    unrelated caller inputs or a not-yet-back-filled reservation refuse (r4 P2)."""
    rs.reserve("pr-3", lane_id="B", branch="b", arc_type="inventing")
    rs.open_with_sensor("pr-3", "B")  # opened but NOT back-filled
    with pytest.raises(md.LeaseError, match="not back-filled"):
        md.acquire(lane_id="B", arc_id="pr-3", pr=3, head_sha="a" * 40, base_sha="b" * 40)
    with pytest.raises(md.LeaseError, match="diverge"):
        md.acquire(lane_id="A", arc_id="pr-1", pr=1, head_sha="c" * 40, base_sha="b" * 40)
    assert md.read_lease() is None


# mutation-probe: drop _publish_fresh()'s final LEASE publish (continuation never re-presented)
def test_publish_fresh_sidecars_before_lease(door, monkeypatch):
    """Crash ordering (r4 P1): sidecars publish FIRST, the LEASE LAST — a crash between a
    published LEASE and its sidecars would present an apparently-refresh-free lease and a
    later self-resume would lose (then re-issue) the recorded refresh/attempt state."""
    real_publish = md.publish_exclusive

    def die_on_lease(path, payload):
        if path == md.LEASE:
            raise RuntimeError("crashed before the LEASE publish")
        real_publish(path, payload)

    fresh = {
        "lease_token": "f" * 32,
        "lane_id": "B",
        "reservation_id": "pr-1",
        "pr": 1,
        "head_sha": "a" * 40,
        "base_sha": "b" * 40,
        "acquired_at": "2026-08-20T00:00:00Z",
        "pid": 1,
        "host": "x",
        "merge_attempted_at": "2026-08-20T00:00:00Z",
        "state": "held",
        "blocked_at_sha": None,
        "blocked_reason": None,
        "refresh": {"pr": 999, "merge_attempted_at": "2026-08-20T00:00:01Z"},
    }
    md.DOOR.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(md, "publish_exclusive", die_on_lease)
    with pytest.raises(RuntimeError):
        md._publish_fresh(fresh)
    assert md.read_lease() is None  # no half-published lease
    assert md._sidecar("f" * 32, "refresh").exists()  # continuation already durable
    monkeypatch.setattr(md, "publish_exclusive", real_publish)
    md._publish_fresh(fresh)  # idempotent completion
    view = md.read_lease()
    assert view["refresh"]["pr"] == 999
    assert view["refresh"]["merge_attempted_at"] is not None


# mutation-probe: drop unblock()'s refresh-pr key acceptance (documented recovery fails)
def test_unblock_accepts_refresh_pr(door):
    """A refresh-CI block is keyed by the REFRESH PR the continuation recorded — the
    documented `merge-door-unblock <refresh-pr>` recovery must not key-mismatch (r4 P2)."""
    lease = _acq(lane="A")
    from arc_metrics import publish_exclusive

    publish_exclusive(md._sidecar(lease["lease_token"], "refresh"), json.dumps({"pr": 999}))
    md.mark_blocked(lease, sha="c" * 40, reason="refresh_ci_not_green")
    successor = md.unblock(pr=999, blocked_at_sha="c" * 40, lane_id="A")
    assert md.read_lease()["lease_token"] == successor["lease_token"]
    assert successor["refresh"]["pr"] == 999  # continuation carried to the successor


# mutation-probe: drop _rate_check()'s writer-side attempts symlink refusal
def test_rate_store_refuses_symlinked_attempts(door, tmp_path):
    """The WRITER must not follow a planted attempts symlink either — no attempt files
    outside QUEUE_DIR, no rate authority derived from external contents (r4 P2)."""
    outside = tmp_path / "outside-rate"
    outside.mkdir()
    md.DOOR.mkdir(parents=True, exist_ok=True)
    (md.DOOR / "attempts").symlink_to(outside)
    with pytest.raises(md.LeaseError, match="attempts is a symlink"):
        _acq(lane="A")
    assert list(outside.iterdir()) == []  # nothing written through the link


# mutation-probe: drop complete_dead_marker()'s closed-action check (typo archives a lease)
def test_unknown_marker_action_fails_closed(door):
    """win_marker refuses an unknown action; a malformed PERSISTED marker never archives
    the live lease as a pseudo-reclaim (r4 P2)."""
    lease = _acq(lane="A")
    with pytest.raises(md.LeaseError, match="unknown transition action"):
        md.win_marker(lease["lease_token"], "typo-action")
    m = md.DOOR / f"transition.{lease['lease_token']}"
    from arc_metrics import publish_exclusive

    publish_exclusive(
        m,
        json.dumps({"pid": 999999, "host": md.socket.gethostname(), "target_action": "typo"}),
    )
    assert md.complete_dead_marker(m) is False
    assert md.read_lease()["lease_token"] == lease["lease_token"]  # lease intact
    # r10 P2: a parseable-but-malformed marker (missing pid) refuses, never raises
    m.unlink()
    publish_exclusive(m, json.dumps({"host": md.socket.gethostname(), "target_action": "release"}))
    assert md.complete_dead_marker(m) is False
    assert md.read_lease()["lease_token"] == lease["lease_token"]


def test_history_sidecars_restamped_on_transition(door):
    """gc's 30-day retention runs from the TRANSITION for the sidecars too (r4 P3)."""
    import time as _time

    lease = _acq(lane="A")
    md.mark_attempted(lease)
    side = md._sidecar(lease["lease_token"], "attempted")
    os.utime(side, (0, 0))  # pretend the block/attempt happened ages ago
    md.release(lease)
    assert abs(_time.time() - side.stat().st_mtime) < 120


# ── codex U-HE-22 r6 corrections ─────────────────────────────────────────────


# mutation-probe: drop _check_door()'s symlink refusal (writes land outside QUEUE_DIR)
def test_writers_refuse_symlinked_door(door, tmp_path):
    """Every write path refuses a planted QUEUE_DIR/merge-door symlink — acquire's rate
    store, markers and sidecars must never land in the link's target (r6 P2)."""
    outside = tmp_path / "outside-door-writer"
    outside.mkdir()
    link = tmp_path / "queue" / "merge-door"
    link.symlink_to(outside)
    with pytest.raises(md.LeaseError, match="merge-door is a symlink"):
        _acq(lane="A")
    with pytest.raises(md.LeaseError, match="merge-door is a symlink"):
        md.win_marker("t" * 32, "release")
    assert list(outside.iterdir()) == []


# mutation-probe: drop complete_dead_marker()'s dead-claimant claim break (stranded forever)
def test_dead_claimant_claim_is_broken(door):
    """A completer that died between claiming and acting must not strand completion — a
    later completer breaks a provably-dead claimant's claim and the pass after that
    completes (r6 P1)."""
    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    from arc_metrics import publish_exclusive

    publish_exclusive(
        md.DOOR / f"completed.{lease['lease_token']}",
        json.dumps({"pid": 999999, "host": md.socket.gethostname(), "at": "t"}),
    )
    assert md.complete_dead_marker(m) is False  # this pass breaks the dead claim
    assert not (md.DOOR / f"completed.{lease['lease_token']}").exists()
    assert md.complete_dead_marker(m) is True  # the next pass completes
    assert md.read_lease()["lease_token"] == "f" * 32


# mutation-probe: drop gc()'s completed-tombstone ordering skip (marker executable again)
def test_gc_retires_transition_before_its_completion_tombstone(door):
    """The completion tombstone must OUTLIVE its transition marker: a pass that removed
    completed.<T> while transition.<T> survived would make the dead marker executable
    again (r7 P2). Pass 1 removes the marker and keeps the tombstone; pass 2 removes it."""
    from datetime import UTC, datetime, timedelta

    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    assert md.complete_dead_marker(m) is True
    tok = lease["lease_token"]
    future = datetime.now(UTC) + timedelta(days=md.GC_KEEP_DAYS + 1)
    removed1 = {p.name for p in md.gc(now=future)}
    assert f"transition.{tok}" in removed1
    assert f"completed.{tok}" not in removed1
    assert (md.DOOR / f"completed.{tok}").exists()  # tombstone outlives the marker
    removed2 = {p.name for p in md.gc(now=future)}
    assert f"completed.{tok}" in removed2


def test_live_claim_survives_a_breaker_pass(door):
    """The adjudicate-after-rename break restores a LIVE claimant's claim rather than
    unlinking it by pathname (r7 P1)."""
    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    from arc_metrics import publish_exclusive

    claim = md.DOOR / f"completed.{lease['lease_token']}"
    publish_exclusive(
        claim,
        json.dumps({"pid": os.getpid(), "host": md.socket.gethostname(), "at": "t"}),
    )
    assert md.complete_dead_marker(m) is False  # live claimant: yielded, not broken
    assert claim.exists()  # the live claim was restored, never lost


# ── codex U-HE-22 r8 corrections ─────────────────────────────────────────────


# mutation-probe: drop reclaim()'s post-publish terminal retraction (authority restored)
def test_reclaim_retracts_on_midflight_terminalization(door, monkeypatch):
    """The reservation gate is check-then-act: terminalized between rs.current() and the
    successor publish, the successor must self-release, never stand (r8 P1)."""
    lease = _acq(lane="A")
    _kill_holder()
    real_current = rs.current
    calls = {"n": 0}

    def flipping(arc_id):
        calls["n"] += 1
        cur = real_current(arc_id)
        if calls["n"] >= 2 and cur is not None:
            # terminalized after the gate read and before the retract re-check
            return (cur[0], {**cur[1], "state": "abandoned"})
        return cur

    monkeypatch.setattr(rs, "current", flipping)
    with pytest.raises(md.LeaseError, match="retracted"):
        md.reclaim(lease, lane_id="B", ground_state="OPEN")
    monkeypatch.setattr(rs, "current", real_current)
    assert md.read_lease() is None  # the successor did not stand


# mutation-probe: drop complete_dead_marker()'s containment preamble (forged marker moves LEASE)
def test_completion_refuses_symlinked_or_foreign_marker(door, tmp_path):
    """A planted symlink named like a marker, or a file outside DOOR, must never move the
    current LEASE (r8 P2)."""
    lease = _acq(lane="A")
    outside = tmp_path / "forged.json"
    outside.write_text(
        json.dumps({"pid": 999999, "host": md.socket.gethostname(), "target_action": "release"})
    )
    link = md.DOOR / f"transition.{lease['lease_token']}"
    link.symlink_to(outside)
    assert md.complete_dead_marker(link) is False
    assert md.read_lease()["lease_token"] == lease["lease_token"]  # lease untouched
    foreign = tmp_path / f"transition.{lease['lease_token']}"
    foreign.write_text(outside.read_text())
    assert md.complete_dead_marker(foreign) is False
    assert md.read_lease()["lease_token"] == lease["lease_token"]


# ── merge-gate r1 corrections (PR #1413) ─────────────────────────────────────


def _forge_holder(host="another-host", pid=999999):
    """Rewrite the persisted LEASE with a FOREIGN host (and dead-looking pid): a pid
    number is meaningless across hosts, so the mismatch must read as unverifiable."""
    body = json.loads(md.LEASE.read_text())
    body["host"] = host
    body["pid"] = pid
    md.LEASE.write_text(json.dumps(body, sort_keys=True))


def test_cross_host_lease_is_unverifiable_not_reclaimable(door):
    """merge-gate r1 witness P2: a lease whose holder lives on ANOTHER host must refuse
    reclaim even with a dead-looking pid — deadness is only adjudicable on the holder's
    own host; anything else is split-brain of the single-writer fence."""
    lease = _acq(lane="A")
    _forge_holder()
    with pytest.raises(md.LeaseError, match="unverifiable"):
        md.reclaim(lease, lane_id="B", ground_state="OPEN")
    assert md.read_lease()["lease_token"] == lease["lease_token"]  # holder undisturbed


def test_cross_host_marker_and_claim_are_unverifiable(door):
    """Same property at the completion surfaces: a foreign-host marker never completes,
    and a foreign-host completion claim is never broken."""
    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    body = json.loads(m.read_text())
    body["host"] = "another-host"
    m.write_text(json.dumps(body))
    assert md.complete_dead_marker(m) is False  # foreign creator: unverifiable
    body["host"] = md.socket.gethostname()
    m.write_text(json.dumps(body))
    from arc_metrics import publish_exclusive

    claim = md.DOOR / f"completed.{lease['lease_token']}"
    publish_exclusive(claim, json.dumps({"pid": 999999, "host": "another-host", "at": "t"}))
    assert md.complete_dead_marker(m) is False  # foreign claim: never broken
    assert claim.exists()


# mutation-probe: drop _move_lease()'s pre-rename re-stamp block (stale-mtime record GC'd)
def test_aged_lease_history_is_born_fresh(door):
    """merge-gate r1 concurrency P2: the transition record must be BORN with the fresh
    transition-time mtime (stamped pre-rename) — a >30d-stale mtime surviving into the
    history name would let a concurrent gc() unlink it before the re-stamp lands."""
    lease = _acq(lane="A")
    md.mark_attempted(lease)
    os.utime(md.LEASE, (0, 0))  # the lease sat blocked/held for ages
    side = md._sidecar(lease["lease_token"], "attempted")
    os.utime(side, (0, 0))
    md.release(lease)
    import time as _time

    hist = md.DOOR / f"released.{lease['lease_token']}"
    assert abs(_time.time() - hist.stat().st_mtime) < 120
    assert abs(_time.time() - side.stat().st_mtime) < 120


# ── codex U-HE-22 r5 corrections ─────────────────────────────────────────────


# mutation-probe: drop complete_dead_marker()'s exclusive completion claim
def test_completion_takes_exclusive_claim(door):
    """Concurrent completers serialize on an exclusive-create claim — without it, two
    callers can both validate the old token and the loser's rename strips a foreign
    holder's live fence (r5 P1). The claim artifact is the witness of the mechanism."""
    lease = _acq(lane="A")
    m = _crashed_reclaim_marker(lease)
    assert md.complete_dead_marker(m) is True
    assert (md.DOOR / f"completed.{lease['lease_token']}").exists()
    # a second completer yields on the claim; a foreign holder is never touched
    md.release(md.read_lease())
    _open_backfilled("pr-9", "C", 9)
    other = md.acquire(lane_id="C", arc_id="pr-9", pr=9, head_sha="a" * 40, base_sha="b" * 40)
    assert md.complete_dead_marker(m) is False
    assert md.read_lease()["lease_token"] == other["lease_token"]


# mutation-probe: drop unblock()'s reservation-state gate (terminated arc regains authority)
def test_unblock_refuses_terminated_reservation(door):
    """A blocked arc abandoned/superseded meanwhile must not regain merge authority
    through unblock — same terminal refusal as reclaim (r5 P2)."""
    lease = _acq(lane="A")
    md.mark_blocked(lease, sha="c" * 40, reason="post_merge_ci_not_green")
    rs.reserve("pr-99", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-1", "abandoned", lane_id="A", superseded_by="pr-99")
    with pytest.raises(md.LeaseError, match="terminated"):
        md.unblock(pr=1, blocked_at_sha="c" * 40, lane_id="A")


# mutation-probe: drop gc()'s symlinked-DOOR refusal (history deleted through the link)
def test_gc_refuses_symlinked_door(door, tmp_path, monkeypatch):
    """A planted QUEUE_DIR/merge-door symlink must not have its target's history files
    unlinked through the gc walk (r5 P1)."""
    outside = tmp_path / "outside-door"
    outside.mkdir()
    victim = outside / ("released." + "x" * 32)
    victim.write_text("history")
    os.utime(victim, (0, 0))  # far older than GC_KEEP_DAYS
    link = tmp_path / "door-link"
    link.symlink_to(outside)
    monkeypatch.setattr(md, "DOOR", link)
    monkeypatch.setattr(md, "LEASE", link / "LEASE")
    assert md.gc() == []
    assert victim.exists()


# mutation-probe: drop _rate_check()'s per-lane symlink refusal
def test_rate_store_refuses_symlinked_lane(door, tmp_path):
    """attempts/<lane> may itself be the planted symlink — mkdir(exist_ok=True) follows a
    symlink-to-dir silently; the writer must refuse (r5 P2)."""
    outside = tmp_path / "outside-lane"
    outside.mkdir()
    (md.DOOR / "attempts").mkdir(parents=True, exist_ok=True)
    (md.DOOR / "attempts" / "A").symlink_to(outside)
    with pytest.raises(md.LeaseError, match="is a symlink"):
        _acq(lane="A")
    assert list(outside.iterdir()) == []


# mutation-probe: drop gc()'s parent-level attempts symlink guard (escape via attempts itself)
def test_gc_attempts_dir_itself_symlink(door, tmp_path):
    """The attempts DIRECTORY itself may be the planted symlink — its ordinary child dirs
    would pass the per-lane check while living outside QUEUE_DIR (r3 P1)."""
    outside = tmp_path / "outside-parent"
    (outside / "lane-x").mkdir(parents=True)
    victim = outside / "lane-x" / "1000.000000"
    victim.write_text("precious")
    os.utime(victim, (0, 0))
    md.DOOR.mkdir(parents=True, exist_ok=True)
    (md.DOOR / "attempts").symlink_to(outside)
    md.gc()
    assert victim.exists()


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


# ══ U-HE-23: landing driver — second half ═══════════════════════════════════════════════

TOOLS = Path(__file__).resolve().parent


class FakeGround:
    """In-memory gh/git with a call log; `merge_calls` is THE mutation-probe surface for
    'never re-issue after MERGED'. As-built vs the plan sketch: state is PER-PR (the
    sketch's single shared dict made gh_view(1) report the refresh PR's state after the
    continuation began, breaking every resume assertion)."""

    def __init__(self, *, head="a" * 40, base="b" * 40, tree="d" * 40, ci="success"):
        self.states = {
            1: {
                "state": "OPEN",
                "headRefOid": head,
                "baseRefOid": base,
                "mergedAt": None,
                "mergeCommit": None,
            }
        }
        self.tree, self.ci, self.merge_calls, self.t = tree, ci, [], 0.0

    def gh_view(self, pr):
        return dict(self.states[pr])

    def gh_merge(self, pr, head, timeout):
        self.merge_calls.append((pr, head))
        self.states[pr].update(state="MERGED", mergedAt="now", mergeCommit={"oid": "c" * 40})
        return subprocess.CompletedProcess([], 0, "", "")

    def gh_runs_for_sha(self, sha):
        return [{"status": "completed", "conclusion": self.ci, "event": "push"}]

    def gh_main_runs_in_progress(self):
        return 1

    def git_merge_tree(self, base, head):
        return self.tree

    def git_first_parent(self, sha):
        return self.states[1]["baseRefOid"]

    def clock(self):
        return self.t

    def sleep(self, s):
        self.t += s

    def codex_worktree_present(self):
        return False

    def add_refresh_pr(self):
        self.states[2] = {
            "state": "OPEN",
            "headRefOid": "r" * 40,
            "baseRefOid": "c" * 40,
            "mergedAt": None,
            "mergeCommit": None,
        }
        return 2, "r" * 40


def _land(door, g, **kw):
    rs.update_payload("pr-1", {"attested_merge_tree": "d" * 40})
    return md.land(1, lane_id="A", arc_id="pr-1", ground=g, refresh=kw.pop("refresh", None), **kw)


def test_happy_path_lands_holds_through_ci_and_releases(door):
    g = FakeGround()
    assert _land(door, g) == "released"
    assert g.merge_calls == [(1, "a" * 40)]
    assert rs.current("pr-1")[1]["state"] == "merged"
    assert md.read_lease() is None


def test_local_base_cas_check_fails_door_on_tree_mismatch(door):
    g = FakeGround(tree="x" * 40)
    with pytest.raises(md.DoorFailed, match="attested"):
        _land(door, g)
    assert g.merge_calls == []
    assert md.read_lease() is None  # released via §6, re-gate


def test_head_base_mismatch_releases_and_regates(door):
    g = FakeGround(head="e" * 40)
    with pytest.raises(md.DoorFailed, match="head/base"):
        _land(door, g)
    assert md.read_lease() is None


# mutation-probe: drop reconcile_ground()'s MERGED return (blind re-issue after MERGED)
def test_timeout_reconcile_merged_calls_once(door):
    """gh pr merge hangs past 120 s but the server landed it: ground truth MERGED ->
    call log stays 1 (the C-HE-06 Invariant)."""
    g = FakeGround()

    def merge_hang(pr, head, timeout):
        g.merge_calls.append((pr, head))
        g.states[pr].update(state="MERGED", mergedAt="now", mergeCommit={"oid": "c" * 40})
        g.t += timeout + 1
        raise subprocess.TimeoutExpired("gh", timeout)

    g.gh_merge = merge_hang
    assert _land(door, g) == "released"
    assert len(g.merge_calls) == 1  # never re-issued after MERGED


def test_timeout_reconcile_open_reissues_exactly_once(door):
    g = FakeGround()
    n = {"k": 0}

    def merge_first_hangs(pr, head, timeout):
        n["k"] += 1
        g.merge_calls.append((pr, head))
        if n["k"] == 1:
            g.t += timeout + 1
            raise subprocess.TimeoutExpired("gh", timeout)
        g.states[pr].update(state="MERGED", mergedAt="now", mergeCommit={"oid": "c" * 40})
        return subprocess.CompletedProcess([], 0, "", "")

    g.gh_merge = merge_first_hangs
    assert _land(door, g) == "released"
    assert len(g.merge_calls) == 2


# mutation-probe: decide the post-attempt handler from the caller dict instead of read_lease()
def test_failure_after_attempt_blocks_never_releases(door):
    """Both merge attempts time out and ground truth stays OPEN → reissue exhausted AFTER
    the attempted marker: the door must BLOCK (HITL), not release (Codex round-2 P1)."""
    g = FakeGround()

    def always_hang(pr, head, timeout):
        g.merge_calls.append((pr, head))
        g.t += timeout + 1
        raise subprocess.TimeoutExpired("gh", timeout)

    g.gh_merge = always_hang
    with pytest.raises(md.DoorBlocked, match="merge_reissue_exhausted"):
        _land(door, g)
    lease = md.read_lease()
    assert lease is not None and lease["state"] == "blocked"
    assert len(g.merge_calls) == 2


def test_inflight_first_attempt_then_reissue(door):
    """T6: a delayed first landing -- exactly one MERGED outcome; nothing proceeds past
    (v) on an error path."""
    g = FakeGround()

    def delayed(pr, head, timeout):
        g.merge_calls.append((pr, head))
        g.t += timeout + 1
        # the server lands it a moment AFTER our timeout fires:
        g.states[pr].update(state="MERGED", mergedAt="later", mergeCommit={"oid": "c" * 40})
        raise subprocess.TimeoutExpired("gh", timeout)

    g.gh_merge = delayed
    assert _land(door, g) == "released"
    assert len(g.merge_calls) == 1


# mutation-probe: make wait_post_merge_ci treat any completed conclusion as green
def test_post_merge_ci_blocked_and_unblock(door):
    """CANCELLED blocks the door (C-HE-19 §2 ci_is_green)."""
    g = FakeGround(ci="cancelled")
    with pytest.raises(md.DoorBlocked):
        _land(door, g)
    lease = md.read_lease()
    assert lease["state"] == "blocked"
    assert lease["blocked_reason"] == "post_merge_ci_not_green"
    md.unblock(pr=1, blocked_at_sha=lease["blocked_at_sha"], lane_id="A")
    assert md.read_lease() is not None  # unblock mints the continuation successor (r3 P1)


# mutation-probe: drop the mark_blocked/raise after the first-parent mismatch (emit-only)
def test_base_toctou_blocks_door(door):
    g = FakeGround()
    g.git_first_parent = lambda sha: "e" * 40  # landed on a base other than the verified one
    with pytest.raises(md.DoorBlocked, match="base_toctou"):
        _land(door, g)
    lease = md.read_lease()
    assert lease["state"] == "blocked"
    assert lease["blocked_reason"] == "base_toctou_first_parent_mismatch"
    assert rs.current("pr-1")[1]["state"] == "merged"  # the fact recorded; the DOOR blocks


def test_refresh_ci_failure_emits_hitl_and_blocks(door, monkeypatch):
    rows = []
    monkeypatch.setattr(rs, "emit_loop_row", lambda k, ln, c, d: rows.append((k, c)))
    g = FakeGround()
    rs.update_payload("pr-1", {"attested_merge_tree": "d" * 40})
    calls = {"n": 0}

    def runs(sha):
        calls["n"] += 1
        # main run green, refresh run red
        concl = "success" if calls["n"] == 1 else "failure"
        return [{"status": "completed", "conclusion": concl, "event": "push"}]

    g.gh_runs_for_sha = runs
    with pytest.raises(md.DoorBlocked):
        md.land(1, lane_id="A", arc_id="pr-1", ground=g, refresh=g.add_refresh_pr)
    assert md.read_lease()["blocked_reason"] == "refresh_ci_not_green"
    assert (
        "DEFERRED-HIL",
        "merge-door-post-merge-ci:HITL-recoverable:refresh_ci_not_green",
    ) in rows


# mutation-probe: force a second acquire() call before the refresh PR merge
def test_continuation_no_reacquire(door, monkeypatch):
    g = FakeGround()
    acquires = []
    real = md.acquire
    monkeypatch.setattr(md, "acquire", lambda **kw: (acquires.append(1), real(**kw))[1])
    rs.update_payload("pr-1", {"attested_merge_tree": "d" * 40})
    assert md.land(1, lane_id="A", arc_id="pr-1", ground=g, refresh=g.add_refresh_pr) == "released"
    assert acquires == [1]
    assert [c[0] for c in g.merge_calls] == [1, 2]


# mutation-probe: drop the `recorded is not None` branch (always call refresh())
def test_resume_uses_recorded_refresh_never_a_second_pr(door, monkeypatch):
    g = FakeGround()
    calls = []
    rs.update_payload("pr-1", {"attested_merge_tree": "d" * 40})

    def refresh():
        calls.append(1)
        return g.add_refresh_pr()

    monkeypatch.setenv("MERGE_DOOR_TEST_KILL_AFTER", "refresh-attempted")
    monkeypatch.setattr(
        md.os, "_exit", lambda code: (_ for _ in ()).throw(SystemExit(code))
    )  # in-process stand-in for the kill
    with pytest.raises(SystemExit):
        md.land(1, lane_id="A", arc_id="pr-1", ground=g, refresh=refresh)
    monkeypatch.delenv("MERGE_DOOR_TEST_KILL_AFTER")
    lease = md.read_lease()
    assert lease["refresh"] == {
        "pr": 2,
        "head_sha": "r" * 40,
        "merge_attempted_at": lease["refresh"]["merge_attempted_at"],
    }
    assert md.land(1, lane_id="A", arc_id="pr-1", ground=g, refresh=refresh, lease=lease) == (
        "released"
    )
    assert calls == [1]  # refresh() called ONCE across crash + resume


def test_wait_for_door_backoff_numbers_and_budget(door):
    t = {"now": 0.0}
    sleeps = []

    def try_acquire():
        raise md.LeaseHeld("held")

    with pytest.raises(md.BudgetExhausted, match="lease_acquire_budget_exhausted"):
        md.wait_for_door(
            try_acquire,
            clock=lambda: t["now"],
            sleep=lambda s: (sleeps.append(s), t.__setitem__("now", t["now"] + s)),
            rng=lambda: 1.0,
        )
    assert len(sleeps) == 11
    assert sleeps[0] == 30.0 and sleeps[1] == 60.0 and max(sleeps) == 600.0
    # rate-limit refusals wait but never count against the 12
    k = {"n": 0}

    def rl():
        k["n"] += 1
        if k["n"] <= 3:
            raise md.RateLimited("rate")
        raise md.LeaseHeld("held")

    sleeps.clear()
    with pytest.raises(md.BudgetExhausted):
        md.wait_for_door(
            rl, clock=lambda: t["now"], sleep=lambda s: sleeps.append(s), rng=lambda: 1.0
        )
    assert len(sleeps) == 11 + 3


def _fake_gh(bindir: Path, state: Path, log: Path, tree: str) -> None:
    """A `gh` + `git` shim on PATH: pr view answers from state.json; pr merge appends to
    merge-calls.log and flips state.json to MERGED; run list reports success; git
    merge-tree returns the attested tree; other git calls pass through."""
    (bindir / "gh").write_text(
        f"""#!/usr/bin/env bash
case "$*" in
  *"pr view"*) cat "{state}" ;;
  *"pr merge"*) echo "$*" >> "{log}"; python3 - <<'PY2'
import json
p = "{state}"
s = json.load(open(p))
s.update(state="MERGED", mergedAt="now", mergeCommit={{"oid": "c" * 40}})
json.dump(s, open(p, "w"))
PY2
  ;;
  *"run list"*"--commit"*)
    echo '[{{"status":"completed","conclusion":"success","event":"push"}}]' ;;
  *"run list"*) echo '[]' ;;
  *) echo "fake gh: unhandled $*" >&2; exit 1 ;;
esac
"""
    )
    (bindir / "git").write_text(
        f"""#!/usr/bin/env bash
if [ "$1" = "-C" ]; then shift 2; fi
case "$1 $2" in
  "merge-tree --write-tree") echo "{tree}" ;;
  "rev-parse "*) echo "{"b" * 40}" ;;
  "worktree list") echo "worktree /x" ;;
  *) exec /usr/bin/git "$@" ;;
esac
"""
    )
    for f in ("gh", "git"):
        (bindir / f).chmod(0o755)


def _land_cmd() -> list[str]:
    return [
        sys.executable,
        str(TOOLS / "merge_door.py"),
        "land",
        "1",
        "--lane-id",
        "A",
        "--arc-id",
        "pr-1",
        "--no-refresh",
    ]


@pytest.mark.parametrize(
    "kill,expect_merge_calls,resume_state",
    [
        ("attempted", 1, "released"),
        ("confirm", 1, "released"),
        ("reservation-merged", 1, "released"),
        ("release", 1, "no-lease"),
    ],
)
def test_ac2_c_crash_resume(door, tmp_path, monkeypatch, kill, expect_merge_calls, resume_state):
    """AC#2(c): a REAL subprocess killed at the named step (os._exit 137), then resumed;
    the merge is issued at most once across crash + resume."""
    q = door
    bindir = tmp_path / "bin"
    bindir.mkdir()
    state = tmp_path / "state.json"
    log = tmp_path / "merge-calls.log"
    state.write_text(
        json.dumps(
            {
                "state": "OPEN",
                "headRefOid": "a" * 40,
                "baseRefOid": "b" * 40,
                "mergedAt": None,
                "mergeCommit": None,
            }
        )
    )
    _fake_gh(bindir, state, log, "d" * 40)
    rs.update_payload("pr-1", {"attested_merge_tree": "d" * 40})
    env = {
        **os.environ,
        "PATH": f"{bindir}:{os.environ['PATH']}",
        "ARC_METRICS_QUEUE_DIR": str(q),
        "PYTHONPATH": str(TOOLS),
        "HARNESS_LANE_ID": "A",
    }
    p1 = subprocess.run(
        _land_cmd(),
        env={**env, "MERGE_DOOR_TEST_KILL_AFTER": kill},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert p1.returncode == 137, p1.stderr
    if kill == "reservation-merged":
        assert md.read_lease() is not None
        assert rs.current("pr-1")[1]["state"] == "merged"
    p2 = subprocess.run(_land_cmd(), env=env, capture_output=True, text=True, timeout=120)
    assert p2.returncode == 0, p2.stderr
    calls = log.read_text().splitlines() if log.exists() else []
    assert len(calls) == expect_merge_calls, calls
    if resume_state == "released":
        assert md.read_lease() is None
        assert any(md.DOOR.glob("released.*"))
    else:
        assert "nothing to land" in (p2.stdout + p2.stderr)

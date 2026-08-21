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
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    assert md.read_lease()["state"] == "blocked"
    with pytest.raises(md.LeaseError):
        md.unblock(pr=1, blocked_at_sha="x" * 40, lane_id="A")  # keyed to blocked_at_sha
    fresh = md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")
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
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    _kill_holder()
    with pytest.raises(md.DoorBlocked):
        md.reclaim(lease, lane_id="A", ground_state="OPEN")
    successor = md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")  # the sanctioned path
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
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    with pytest.raises(md.DoorBlocked):
        md.release(lease)  # caller's dict still says held; persisted view says blocked
    successor = md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")
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
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    rs.transition("pr-1", "merged", lane_id="A")  # the §4(vi) flip already happened
    fresh = md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")
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
    md.mark_blocked(lease, sha="m" * 40, reason="refresh_ci_not_green")
    successor = md.unblock(pr=999, blocked_at_sha="m" * 40, lane_id="A")
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
    publish_exclusive(
        m, json.dumps({"host": md.socket.gethostname(), "target_action": "release"})
    )
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
    md.mark_blocked(lease, sha="m" * 40, reason="post_merge_ci_not_green")
    rs.reserve("pr-99", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-1", "abandoned", lane_id="A", superseded_by="pr-99")
    with pytest.raises(md.LeaseError, match="terminated"):
        md.unblock(pr=1, blocked_at_sha="m" * 40, lane_id="A")


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

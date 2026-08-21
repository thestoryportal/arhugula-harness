#!/usr/bin/env python3
"""Merge-door lease (C-HE-06): the single-writer landing fence.

QUEUE_DIR/merge-door/LEASE is created by exclusive create and NEVER mutated in place. Payload
changes (`merge_attempted_at`, `blocked`) are token-named sidecars published by temp + os.link so a
crash cannot leave a marker half-written. Every release / reclaim / unblock / self-resume first wins
the exclusive create of transition.<lease_token>; only the marker winner may os.rename(LEASE, ...).
There is no path-only unlink of LEASE anywhere in this file. Acquire is fail-fast: one attempt, the
CALLER decides retry (D3); arbitration never moves into the primitive.

U-HE-22 lands the primitive half (this file's whole surface today); the landing driver
`land(pr, ...)` — C-HE-06 §4 steps (ii)–(ix), reconcile, caller backoff — arrives with U-HE-23,
which consumes the §4/§8 constants declared below.
"""

from __future__ import annotations

import json
import os
import secrets
import socket
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import reservations as rs
from arc_metrics import QUEUE_DIR, _process_is_alive, publish_exclusive

DOOR = QUEUE_DIR / "merge-door"
LEASE = DOOR / "LEASE"
RATE_K = 5
RATE_WINDOW_S = 60
GC_KEEP_DAYS = 30
MERGE_TIMEOUT_S = 120.0
POST_MERGE_CI_BOUND_S = 45 * 60
REFRESH_BOUND_S = 45 * 60
BACKOFF = {"base_s": 30.0, "factor": 2.0, "cap_s": 600.0, "max_attempts": 12}
KILL_STEPS = (
    "acquire",
    "verify",
    "attempted",
    "merge",
    "confirm",
    "reservation-merged",
    "post-ci",
    "refresh-attempted",
    "refresh-merged",
    "release",
)


class LeaseError(RuntimeError): ...


class LeaseHeld(LeaseError):  # noqa: N818 — U-HE-22 plan signature verbatim
    ...


class RateLimited(LeaseError):  # noqa: N818 — U-HE-22 plan signature verbatim
    ...


class HolderInvariant(LeaseError):  # noqa: N818 — U-HE-22 plan signature verbatim
    ...


class MarkerLost(LeaseError):  # noqa: N818 — U-HE-22 plan signature verbatim
    ...


class DoorBlocked(LeaseError):  # noqa: N818 — U-HE-22 plan signature verbatim
    ...


class DoorFailed(LeaseError):  # noqa: N818 — U-HE-22 plan signature verbatim
    ...


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _kill_after(step: str) -> None:
    if os.environ.get("MERGE_DOOR_TEST_KILL_AFTER") == step:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(137)


def _sidecar(token: str, name: str) -> Path:
    return DOOR / f"LEASE.{token}.{name}"


def read_lease() -> dict | None:
    """The LEASE view: base payload + sidecars (attempted / blocked / refresh) merged in."""
    if not LEASE.exists():
        return None
    try:
        lease = json.loads(LEASE.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    tok = lease["lease_token"]
    att = _sidecar(tok, "attempted")
    if att.exists():
        lease["merge_attempted_at"] = json.loads(att.read_text())["merge_attempted_at"]
    blk = _sidecar(tok, "blocked")
    if blk.exists():
        b = json.loads(blk.read_text())
        lease.update(
            state="blocked",
            blocked_at_sha=b["blocked_at_sha"],
            blocked_reason=b["blocked_reason"],
            blocked_at=b["blocked_at"],
        )
    ref = _sidecar(tok, "refresh")
    if ref.exists():
        lease["refresh"] = json.loads(ref.read_text())
        ratt = _sidecar(tok, "refresh.attempted")
        if ratt.exists():
            lease["refresh"]["merge_attempted_at"] = json.loads(ratt.read_text())[
                "merge_attempted_at"
            ]
    return lease


def _check_lane_id(lane_id: str) -> None:
    """Containment: lane_id becomes a path component of the attempts store. An absolute or
    traversing value would make pathlib discard DOOR entirely (codex U-HE-22 r1 P2)."""
    if (
        not lane_id
        or lane_id != Path(lane_id).name
        or lane_id in (".", "..")
        or lane_id.startswith(".")
        or ":" in lane_id
    ):
        raise LeaseError(f"bad lane_id {lane_id!r}: must be a single safe path component")


def _check_door() -> None:
    """Writer-side containment (codex r6 P2): a planted QUEUE_DIR/merge-door symlink would
    receive every LEASE/sidecar/marker/attempt write outside QUEUE_DIR. Mirrors gc()'s
    root guard on every write path."""
    if DOOR.is_symlink():
        raise LeaseError("merge-door is a symlink -- refused")


def _rate_check(lane_id: str, now: float) -> None:
    """K acquire attempts per lane per 60 s. Record-then-count: the caller's own attempt is
    published FIRST (exclusive create), then the window is counted including it, so a burst
    of concurrent callers cannot all under-count a not-yet-recorded peer (codex U-HE-22 r1
    P2). The limiter bounds sustained rates — single-writer safety never depends on it (the
    LEASE exclusive create is the fence); refusals never touch the caller's §8 budget, and a
    refused attempt IS recorded (it was an attempt)."""
    _check_lane_id(lane_id)
    _check_door()
    att = DOOR / "attempts"
    if att.is_symlink():
        # Writer-side mirror of gc()'s parent guard (codex r4 P2): a planted attempts
        # symlink must not receive attempt files or derive rate authority from external
        # contents — fail closed, never follow.
        raise LeaseError("merge-door/attempts is a symlink -- refused")
    d = att / lane_id
    if d.is_symlink():
        # Same containment for the per-lane path (codex r5 P2): mkdir(exist_ok=True)
        # follows a symlink-to-dir silently; never write attempts through one.
        raise LeaseError(f"merge-door/attempts/{lane_id} is a symlink -- refused")
    d.mkdir(parents=True, exist_ok=True)

    def _ts(p: Path) -> float | None:
        try:
            return float(p.name)
        except ValueError:
            # `.<ts>.<pid>.tmp` remnants of a crashed publish_exclusive: not attempts
            return None

    for _ in range(8):
        try:
            publish_exclusive(d / f"{now:.6f}", "")
            break
        except FileExistsError:
            now += 1e-6
    recent = [p for p in d.iterdir() if (_ts(p) is not None and now - _ts(p) <= RATE_WINDOW_S)]
    for junk in d.glob(".*.tmp"):
        if now - junk.stat().st_mtime > 3600:
            junk.unlink(missing_ok=True)
    if len(recent) > RATE_K:
        raise RateLimited(
            f"{lane_id}: > {RATE_K} lease acquire attempts in {RATE_WINDOW_S}s "
            "(cause_attribution: lease_acquire_rate_exceeded)"
        )


def acquire(
    *, lane_id: str, arc_id: str, pr: int, head_sha: str, base_sha: str, now: float | None = None
) -> dict:
    """Fail-fast, one attempt. Verifies the P2 holder invariant (reservation open AND held by
    this lane)."""
    now = time.time() if now is None else now
    _rate_check(lane_id, now)
    cur = rs.current(arc_id)
    # P2 (C-HE-06 §7) is enforced HERE, at acquisition, as its text says ("Acquisition MUST
    # verify the reservation state"). During the G4 continuation the reservation legitimately
    # reads `merged` (C-HE-03 §4 flips it on confirmed merge) while the lease is still held
    # through post-merge CI + the refresh -- so the §7 Invariants bullet "no lease exists whose
    # reservation is not open" cannot be read literally across the continuation window. That
    # wording is reconciled by the spec v1.4 note (this unit); nothing acquires against a
    # non-open reservation.
    if cur is None or cur[1]["state"] != "open" or cur[1]["lane_id"] != lane_id:
        raise HolderInvariant(
            f"{arc_id}: reservation must be open and held by {lane_id} (P2); "
            f"got {cur and cur[1]['state']!r} held by {cur and cur[1]['lane_id']!r}"
        )
    if not (pr and head_sha and base_sha):
        raise LeaseError("pr, head_sha, base_sha are REQUIRED on the lease (C-HE-06 §3)")
    # The reservation-to-lease authority link (codex r4 P2): ship-pr back-fills the merge
    # tuple on the reservation BEFORE the door (C-HE-03 §3) — the lease must carry THOSE
    # values, not unrelated caller inputs. A not-yet-back-filled reservation is a flow
    # violation, not a default.
    snap = cur[1]
    if snap.get("pr") is None or snap.get("head_sha") is None or snap.get("base_sha") is None:
        raise LeaseError(
            f"{arc_id}: reservation merge tuple not back-filled "
            "(ship-pr writes pr/head_sha/base_sha before the door -- C-HE-03 §3)"
        )
    if int(snap["pr"]) != int(pr) or snap["head_sha"] != head_sha or snap["base_sha"] != base_sha:
        raise LeaseError(
            f"{arc_id}: lease inputs diverge from the reservation snapshot "
            f"(reservation pr={snap['pr']} head={snap['head_sha'][:12]} "
            f"base={snap['base_sha'][:12]})"
        )
    payload = {
        "lease_token": secrets.token_hex(16),
        "lane_id": lane_id,
        "reservation_id": arc_id,
        "pr": int(pr),
        "head_sha": head_sha,
        "base_sha": base_sha,
        "acquired_at": _now_iso(),
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "merge_attempted_at": None,
        "state": "held",
        "blocked_at_sha": None,
        "blocked_reason": None,
    }
    DOOR.mkdir(parents=True, exist_ok=True)
    try:
        publish_exclusive(LEASE, json.dumps(payload, sort_keys=True))
    except FileExistsError as exc:
        msg = "merge door held (cause_attribution: lease_contended)"
        raise LeaseHeld(msg) from exc
    # Post-publication re-validation (codex U-HE-22 r3 P2): the pre-check and the exclusive
    # create are separate operations — a concurrent reconciliation can terminalize the
    # reservation in between, leaving a fresh lease on a terminal arc. Re-read after the
    # publish; on divergence, self-heal through the marker discipline (never a path-only
    # unlink) and refuse.
    cur2 = rs.current(arc_id)
    if cur2 is None or cur2[1]["state"] != "open" or cur2[1]["lane_id"] != lane_id:
        if win_marker(payload["lease_token"], "release") is not None:
            _move_lease(payload["lease_token"], "released")
        raise HolderInvariant(
            f"{arc_id}: reservation changed during acquisition "
            f"(now {cur2 and cur2[1]['state']!r} held by {cur2 and cur2[1]['lane_id']!r}); "
            "lease self-released"
        )
    _kill_after("acquire")
    return payload


def win_marker(token: str, target_action: str, *, extra: dict | None = None) -> Path | None:
    """One marker per token, ever. The winner alone may move LEASE. `extra` (e.g. the reclaim's
    fresh lease) rides in the marker so a dead creator's declared action can be COMPLETED, not
    just archived (C-HE-06 §6 poison-pill)."""
    if target_action not in ("release", "reclaim", "unblock"):
        # Closed action set (codex r4 P2): the marker is one-shot per token — a typo'd
        # action would consume the transition and be mis-completed as a reclaim.
        raise LeaseError(f"unknown transition action {target_action!r}")
    _check_door()
    m = DOOR / f"transition.{token}"
    try:
        publish_exclusive(
            m,
            json.dumps(
                {
                    "pid": os.getpid(),
                    "host": socket.gethostname(),
                    "target_action": target_action,
                    "created_at": _now_iso(),
                    **(extra or {}),
                },
                sort_keys=True,
            ),
        )
        return m
    except FileExistsError:
        return None


def mark_attempted(lease: dict, *, suffix: str = "") -> None:
    """Payload CAS: temp + os.link onto a token-named sidecar BEFORE the merge request leaves
    the process."""
    _check_door()
    name = ("refresh." if suffix == "refresh" else "") + "attempted"
    try:
        publish_exclusive(
            _sidecar(lease["lease_token"], name), json.dumps({"merge_attempted_at": _now_iso()})
        )
    except FileExistsError:
        pass  # already set: idempotent


def mark_blocked(lease: dict, *, sha: str, reason: str) -> None:
    _check_door()
    try:
        publish_exclusive(
            _sidecar(lease["lease_token"], "blocked"),
            json.dumps({"blocked_at_sha": sha, "blocked_reason": reason, "blocked_at": _now_iso()}),
        )
    except FileExistsError:
        pass


def _move_lease(token: str, dest_prefix: str) -> None:
    dest = DOOR / f"{dest_prefix}.{token}"
    try:
        os.rename(LEASE, dest)
        # Re-stamp: rename preserves the ACQUISITION mtime, and gc() expires history from
        # mtime — a lease blocked >30 d would otherwise be eligible for deletion the moment
        # its transition completes, instead of holding its record for the contracted 30 d
        # (codex U-HE-22 r3 P3). The history clock starts at the transition, not the acquire.
        # The token's SIDECARS carry the same history (attempted/blocked/refresh) and get
        # the same clock (codex r4 P3), else GC erases the transition evidence early.
        os.utime(dest, None)
        for side in DOOR.glob(f"LEASE.{token}.*"):
            try:
                os.utime(side, None)
            except FileNotFoundError:
                continue
    except FileNotFoundError:
        pass  # already moved: fail-closed idempotency (a rename on a moved source = "done")


def release(lease: dict) -> None:
    # Re-read the persisted state (codex U-HE-22 r2 P1): the caller's dict may predate a
    # mark_blocked (a blocked door stays closed until the operator-keyed unblock), and a
    # stale dict must never move ANOTHER lease aside (_move_lease renames the CURRENT
    # LEASE; the marker namespace is per-token, so a stale caller could win its own old
    # token's marker while the door holds a different lease).
    persisted = read_lease()
    if persisted is None or persisted["lease_token"] != lease["lease_token"]:
        raise LeaseError(
            "stale release: the door does not currently hold that lease "
            f"(door: {persisted and persisted['lease_token']!r})"
        )
    if persisted.get("state") == "blocked":
        raise DoorBlocked(
            f"lease is blocked at {persisted.get('blocked_at_sha')!r} "
            f"({persisted.get('blocked_reason')!r}); use unblock, not release"
        )
    if win_marker(lease["lease_token"], "release") is None:
        raise MarkerLost(
            f"lease {lease['lease_token']}: transition marker already taken -- "
            "stop driving, reconcile by ground truth"
        )
    _move_lease(lease["lease_token"], "released")
    _kill_after("release")


def reclaim(lease: dict, *, lane_id: str, ground_state: str) -> dict:
    """Two-step: (1) the holder pid is PROVABLY dead on this host -- same-lane self-resume
    included (a live twin presenting the same lane_id must NOT displace a working holder;
    Codex round-2 P1); (2) caller-supplied ground truth (MERGED/OPEN from gh). Wins the OLD
    token's marker -- whose payload carries the FRESH lease so a crashed reclaimer can be
    completed idempotently by a third party -- moves LEASE aside, publishes the fresh LEASE
    (new token). Transfers merge-driving authority for `pr` -- never reservation ownership."""
    # Deadness and state are adjudicated from the PERSISTED lease, never the caller's dict —
    # a copied dict with a substituted pid must not displace a live holder (codex U-HE-22
    # r1 P1). The caller's dict only NAMES the lease it claims; the door's current LEASE is
    # the evidence.
    persisted = read_lease()
    if persisted is None or persisted["lease_token"] != lease["lease_token"]:
        raise LeaseError(
            "stale reclaim: the door does not currently hold that lease "
            f"(door: {persisted and persisted['lease_token']!r})"
        )
    if persisted.get("state") == "blocked":
        # A blocked door resumes ONLY through the operator-confirmed, blocked_at_sha-keyed
        # unblock (C-HE-06 §6) — generic self-resume must not bypass it (codex U-HE-22 r1 P1).
        raise DoorBlocked(
            f"lease is blocked at {persisted.get('blocked_at_sha')!r} "
            f"({persisted.get('blocked_reason')!r}); use unblock, not reclaim"
        )
    if persisted["host"] != socket.gethostname() or _process_is_alive(int(persisted["pid"])):
        raise LeaseError(
            "holder is live or unverifiable; not reclaimable "
            "(self-resume requires the old pid to be dead)"
        )
    if ground_state not in ("MERGED", "OPEN"):
        raise LeaseError(f"reclaim requires ground truth MERGED|OPEN, got {ground_state!r}")
    # The linked reservation is re-checked too (codex U-HE-22 r2 P2): an arc the operator
    # abandoned/superseded while its PR stayed OPEN must not regain merge-driving authority
    # through a dead lease. `open` and `merged` are the legitimate lease-holding states
    # (merged = the §4(vi)–(ix) continuation window).
    res = rs.current(persisted["reservation_id"])
    if res is None or res[1]["state"] not in ("open", "merged"):
        raise LeaseError(
            f"reclaim refused: reservation {persisted['reservation_id']!r} reads "
            f"{res and res[1]['state']!r} — the arc has been terminated or never opened"
        )
    fresh = {
        **persisted,
        "lease_token": secrets.token_hex(16),
        "lane_id": lane_id,
        "acquired_at": _now_iso(),
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "state": "held",
        "blocked_at_sha": None,
        "blocked_reason": None,
    }
    # The refresh continuation SURVIVES self-resume (codex U-HE-22 r1 P1: dropping it lets
    # the landing driver re-create the refresh instead of reconciling the recorded attempt);
    # `_publish_fresh` republishes it as sidecars under the new token. Transient view keys
    # that read_lease() merged in are stripped from the base payload there.
    if win_marker(lease["lease_token"], "reclaim", extra={"fresh_lease": fresh}) is None:
        raise MarkerLost("reclaim marker already taken")
    _move_lease(lease["lease_token"], "reclaimed")
    _publish_fresh(fresh)
    live = read_lease()
    if not live or live["lease_token"] != fresh["lease_token"]:
        # The move→publish window is not atomic on POSIX (no portable two-name swap): another
        # acquirer may have taken the momentarily-free door. NEVER adopt an unrelated lease
        # (Codex round-3 P1): fail loud; the caller re-gates.
        raise LeaseError(
            f"reclaim lost the door to another acquirer "
            f"(holder {live and live['lane_id']}); not resumed"
        )
    return live


def _publish_fresh(fresh: dict) -> None:
    """Idempotent: a twin (or a third party completing our marker) may already have published
    this exact token. `fresh` may be a merged read_lease() view: transient view keys are
    stripped from the base LEASE payload and republished as sidecars under the new token
    (attempted; the refresh continuation + its own attempted — codex U-HE-22 r1 P1)."""
    ref = fresh.get("refresh")
    payload = {k: v for k, v in fresh.items() if k not in ("refresh", "blocked_at")}
    # SIDECARS FIRST, LEASE LAST (codex r4 P1): a crash between a published LEASE and its
    # not-yet-republished sidecars would present an apparently-refresh-free lease — a later
    # self-resume would then lose the recorded refresh/attempt state and could re-issue.
    # Token-named sidecars published before their LEASE are invisible orphans (read_lease
    # keys off the published token), so this order is crash-safe in both directions.
    if fresh.get("merge_attempted_at"):
        try:
            publish_exclusive(
                _sidecar(fresh["lease_token"], "attempted"),
                json.dumps({"merge_attempted_at": fresh["merge_attempted_at"]}),
            )
        except FileExistsError:
            pass
    if ref:
        _publish_refresh_sidecars(fresh["lease_token"], ref)
    try:
        publish_exclusive(LEASE, json.dumps(payload, sort_keys=True))
    except FileExistsError:
        pass


def _publish_refresh_sidecars(token: str, ref: dict) -> None:
    """The refresh continuation's token-named sidecars (base + its own attempted)."""
    try:
        publish_exclusive(
            _sidecar(token, "refresh"),
            json.dumps({k: v for k, v in ref.items() if k != "merge_attempted_at"}, sort_keys=True),
        )
    except FileExistsError:
        pass
    if ref.get("merge_attempted_at"):
        try:
            publish_exclusive(
                _sidecar(token, "refresh.attempted"),
                json.dumps({"merge_attempted_at": ref["merge_attempted_at"]}),
            )
        except FileExistsError:
            pass


def unblock(*, pr: int, blocked_at_sha: str, lane_id: str) -> dict:
    """Operator-confirmed reclaim through the marker CAS, keyed to blocked_at_sha. Never a
    path-only unlink. Mints a REPLACEMENT lease held by `lane_id` (codex U-HE-22 r3 P1): a
    door typically blocks DURING the §4(vii)–(viii) continuation, when the reservation
    already reads `merged` and `acquire()` would refuse — clearing without a successor
    would strand the continuation behind an unacquirable door. The unblocking lane resumes
    it (sidecar continuation state carried over); a lane that genuinely wants the door free
    releases the returned lease with the normal verb."""
    lease = read_lease()
    if lease is None or lease.get("state") != "blocked":
        raise LeaseError("no blocked lease to unblock")
    # A refresh-CI block is keyed by the REFRESH PR (codex r4 P2): the §4(viii)
    # continuation records its own PR in the refresh sidecar, and the documented recovery
    # command passes that number — accept either the lease's own PR or the continuation's.
    known_prs = {int(lease["pr"])}
    if isinstance(lease.get("refresh"), dict) and lease["refresh"].get("pr") is not None:
        known_prs.add(int(lease["refresh"]["pr"]))
    if int(pr) not in known_prs or lease.get("blocked_at_sha") != blocked_at_sha:
        raise LeaseError(
            f"unblock key mismatch: lease is pr={sorted(known_prs)} "
            f"blocked_at_sha={lease.get('blocked_at_sha')}"
        )
    res = rs.current(lease["reservation_id"])
    if res is None or res[1]["state"] not in ("open", "merged"):
        # Same terminal-arc refusal as reclaim (codex r5 P2): a blocked arc abandoned or
        # superseded meanwhile must not regain merge-driving authority through unblock.
        raise LeaseError(
            f"unblock refused: reservation {lease['reservation_id']!r} reads "
            f"{res and res[1]['state']!r} — the arc has been terminated"
        )
    fresh = {
        **lease,
        "lease_token": secrets.token_hex(16),
        "lane_id": lane_id,
        "acquired_at": _now_iso(),
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "state": "held",
        "blocked_at_sha": None,
        "blocked_reason": None,
    }
    fresh.pop("blocked_at", None)
    if win_marker(lease["lease_token"], "unblock", extra={"fresh_lease": fresh}) is None:
        raise MarkerLost("unblock marker already taken")
    _move_lease(lease["lease_token"], "reclaimed")
    _publish_fresh(fresh)
    live = read_lease()
    if not live or live["lease_token"] != fresh["lease_token"]:
        raise LeaseError(
            f"unblock lost the door to another acquirer "
            f"(holder {live and live['lane_id']}); not resumed"
        )
    return live


def complete_dead_marker(marker: Path) -> bool:
    """Poison-pill guard: a third party MAY complete a dead creator's declared target_action
    idempotently."""
    try:
        m = json.loads(marker.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    if m["host"] != socket.gethostname() or _process_is_alive(int(m["pid"])):
        return False
    token = marker.name.removeprefix("transition.")
    action = m["target_action"]
    if action not in ("release", "reclaim", "unblock"):
        # Fail closed on a malformed persisted marker (codex r4 P2): treating an unknown
        # action as reclaim-ish would archive a live lease on a forged/corrupt file.
        return False
    # Serialize completers (codex r5 P1): two callers can both validate the old token,
    # the first moves it, a foreign lane acquires, and the second's rename would then
    # strip the NEW holder's live fence. Exactly one completer wins this exclusive
    # create; losers yield. The claim is taken only after the cheap refusals above, so a
    # refused completion stays retryable; the claim-to-act window is two idempotent
    # statements, and the door reconcile (U-HE-23 §5) is the ground-truth recovery for a
    # completer that dies inside it.
    claim = DOOR / f"completed.{token}"
    try:
        publish_exclusive(
            claim,
            json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "at": _now_iso()}),
        )
    except FileExistsError:
        # A completer that died between claiming and acting must not strand the
        # completion forever (codex r6 P1): break a claim whose claimant is provably
        # dead on this host — same poison-pill logic as the marker itself — and yield
        # this pass (the next completer wins a fresh create).
        try:
            c = json.loads(claim.read_text())
            if c["host"] == socket.gethostname() and not _process_is_alive(int(c["pid"])):
                claim.unlink(missing_ok=True)
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            pass
        return False
    done = False
    if LEASE.exists() and json.loads(LEASE.read_text()).get("lease_token") == token:
        _move_lease(token, "released" if action == "release" else "reclaimed")
        done = True
    if action in ("reclaim", "unblock") and "fresh_lease" in m:
        # The reclaimer may have died AFTER moving the old lease and BEFORE publishing the
        # fresh one: finish it. `_publish_fresh` is idempotent (FileExistsError = the fresh
        # token, or a later acquirer, already holds the door). Ground-truth gate (codex
        # U-HE-22 r1 P1): a stale marker surviving a full foreign acquire→release cycle must
        # not resurrect authority for an arc that has moved on — publish only while the
        # fresh lease's reservation still reads `open` OR `merged` (the C-HE-03 authority):
        # `merged` is the legitimate §4(vi)–(ix) continuation state — a post-merge reclaimer
        # crashing between move and publish must still be completable, else the door reads
        # free and another lane acquires mid-continuation (codex U-HE-22 r2 P1 on the r1
        # open-only gate). An abandoned/superseded or never-opened arc refuses. The narrower
        # stale-head window that remains (reservation not yet terminal, door cycled) is
        # bounded by the land driver's own step-(ii) head/base re-verification (U-HE-23),
        # which releases a stale resurrected lease.
        res = rs.current(m["fresh_lease"]["reservation_id"])
        if res is None or res[1]["state"] not in ("open", "merged"):
            return done
        before = read_lease()
        _publish_fresh(m["fresh_lease"])
        after = read_lease()
        done = done or (
            before is None
            and after is not None
            and after["lease_token"] == m["fresh_lease"]["lease_token"]
        )
    return done


def gc(*, now: datetime | None = None) -> list[Path]:
    now = now or datetime.now(UTC)
    removed = []
    if DOOR.is_symlink() or not DOOR.is_dir():
        # A planted QUEUE_DIR/merge-door symlink must not have its TARGET's history
        # unlinked through this walk (codex r5 P1) — is_dir() follows links.
        return removed
    cutoff = now - timedelta(days=GC_KEEP_DAYS)
    for p in DOOR.iterdir():
        try:
            expired = (
                p.name.startswith(
                    ("transition.", "released.", "reclaimed.", "completed.", "LEASE.")
                )
                and not p.is_symlink()
                and datetime.fromtimestamp(p.stat().st_mtime, UTC) < cutoff
            )
            if expired:
                live = read_lease()
                if live and live["lease_token"] in p.name:
                    continue
                p.unlink()
                removed.append(p)
        except FileNotFoundError:
            # a concurrent collector won this artifact: log-and-yield idiom (codex r2 P3)
            continue
    att: Path | None = DOOR / "attempts"
    # The attempts dir ITSELF must not be a planted symlink either — its ordinary-looking
    # children would pass the per-lane check while living outside QUEUE_DIR (codex r3 P1).
    if att is not None and att.is_symlink():
        att = None
    if att is not None and att.is_dir():
        for lane in att.iterdir():
            # NEVER follow a planted symlink out of the attempts store: a pre-existing
            # attempts/<lane> symlink would make this walk unlink regular files outside
            # QUEUE_DIR (codex U-HE-22 r2 P1). Lane dirs are only ever created by
            # _rate_check under _check_lane_id containment — anything else is skipped.
            if lane.is_symlink() or not lane.is_dir():
                continue
            for f in lane.iterdir():
                try:
                    if f.is_symlink():
                        continue
                    try:
                        age = now.timestamp() - float(f.name)
                    except ValueError:
                        # `.tmp` remnant of a crashed publish_exclusive (round-5 P2)
                        age = now.timestamp() - f.stat().st_mtime
                    if age > 3600:
                        f.unlink()
                        removed.append(f)
                except FileNotFoundError:
                    continue  # concurrent collector won it (codex r2 P3)
    return removed

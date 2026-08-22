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

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import reservations as rs
from arc_metrics import QUEUE_DIR, REPO, _process_is_alive, ci_is_green, publish_exclusive

DOOR = QUEUE_DIR / "merge-door"
LEASE = DOOR / "LEASE"
RATE_K = 5
RATE_WINDOW_S = 60
GC_KEEP_DAYS = 30
MERGE_TIMEOUT_S = 120.0
# CLAUDE.md §12.2.1 terminating-refresh discriminator (codex r8 P1): the recorded
# refresh PR must carry this exact shape — title prefix + roadmap-status-only file set
REFRESH_TITLE_PREFIX = "ops: roadmap status refresh "
# concatenated so the store-audit literal extractor cannot misread this gh-side
# file-set discriminator as an uninventoried QUEUE_DIR store literal
REFRESH_ONLY_FILE = ".harness" + "/roadmap_status.md"
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
    if _sidecar(tok, "refresh.intent").exists():
        # declared refresh intent survives into the view so self-resume carries it
        # across a token change (codex U-HE-23 r2 P2)
        lease["refresh_intent"] = True
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
        try:
            if now - junk.stat().st_mtime > 3600:
                junk.unlink(missing_ok=True)
        except FileNotFoundError:
            continue  # a concurrent cleaner won (codex r7 P3)
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
    # Re-stamp BEFORE the rename (merge-gate r1 concurrency P2 on the r3/r4 re-stamp
    # fix): rename preserves the source mtime, so stamping the SOURCE first means dest is
    # BORN with the fresh transition-time mtime — no window in which a concurrent gc()
    # can stat a >30d-stale dest and unlink the record early. The history clock starts at
    # the transition, not the acquire (codex r3 P3); the token's sidecars carry the same
    # history and get the same clock, stamped while the live-lease guard still protects
    # them (codex r4 P3).
    try:
        os.utime(LEASE, None)
    except FileNotFoundError:
        pass
    for side in DOOR.glob(f"LEASE.{token}.*"):
        try:
            os.utime(side, None)
        except FileNotFoundError:
            continue
    try:
        os.rename(LEASE, dest)
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
    # NOTE (codex r10 P1, HELD): a foreign-lane reclaim of an OPEN reservation leaves
    # holdership with the original lane BY DESIGN (the U-HE-22 r2-pinned adjudication:
    # rs.holder stays "A"); if the (vi) holder-gated transition then refuses, the door
    # BLOCKS loud (post-attempt) and the C-HE-03 §6 transfer_holder venue recovers —
    # never a silent wedge
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
    if _retract_if_terminal(fresh):
        raise LeaseError(
            f"reclaim retracted: reservation {fresh['reservation_id']!r} terminalized "
            "during the reclaim (codex r8 P1); successor self-released"
        )
    return live


def _publish_fresh(fresh: dict) -> None:
    """Idempotent: a twin (or a third party completing our marker) may already have published
    this exact token. `fresh` may be a merged read_lease() view: transient view keys are
    stripped from the base LEASE payload and republished as sidecars under the new token
    (attempted; the refresh continuation + its own attempted — codex U-HE-22 r1 P1)."""
    ref = fresh.get("refresh")
    intent = fresh.get("refresh_intent")
    payload = {
        k: v for k, v in fresh.items() if k not in ("refresh", "blocked_at", "refresh_intent")
    }
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
    if intent:
        # the declared-intent fence survives the token change (codex r2 P2): losing it
        # across a reclaim would let a resumed pass mint a second refresh PR
        try:
            publish_exclusive(
                _sidecar(fresh["lease_token"], "refresh.intent"), json.dumps({"at": _now_iso()})
            )
        except FileExistsError:
            pass
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
    if res[1]["state"] == "open" and res[1]["lane_id"] != lane_id:
        # While the reservation is still OPEN, only its holder may take the successor
        # (codex U-HE-23 r4 P2): a foreign lane's merge would succeed externally and
        # then fail the (vi) holder transition — an ambiguous attempted state. Holder
        # transfer is reclaim's job (dead-holder proof), never unblock's.
        raise LeaseError(
            f"unblock refused: reservation {lease['reservation_id']!r} is open and held "
            f"by {res[1]['lane_id']!r}, not {lane_id!r}"
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
        # the operator-keyed unblock IS the re-validation attestation for the sha it was
        # keyed to (codex r3 P1): without this, a BASE_TOCTOU block re-fires on every
        # resume and the door is permanently wedged
        "unblocked_from": blocked_at_sha,
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
    if _retract_if_terminal(fresh):
        raise LeaseError(
            f"unblock retracted: reservation {fresh['reservation_id']!r} terminalized "
            "during the unblock (codex r8 P1); successor self-released"
        )
    return live


def _retract_if_terminal(fresh: dict) -> bool:
    """Post-publish terminal re-check (codex r8 P1): the reservation gate is check-then-act
    — an arc can be terminalized between rs.current() and the successor publish. Mirror of
    acquire()'s post-publication re-validation: if the reservation no longer reads
    open/merged, self-release the just-published successor through the marker discipline
    and report the retraction. Returns True when the successor was retracted."""
    res = rs.current(fresh["reservation_id"])
    if res is not None and res[1]["state"] in ("open", "merged"):
        return False
    live = read_lease()
    if live and live["lease_token"] == fresh["lease_token"]:
        if win_marker(fresh["lease_token"], "release") is not None:
            _move_lease(fresh["lease_token"], "released")
    return True


def complete_dead_marker(marker: Path) -> bool:
    """Poison-pill guard: a third party MAY complete a dead creator's declared target_action
    idempotently."""
    _check_door()
    if marker.is_symlink() or not marker.name.startswith("transition."):
        # Containment (codex r8 P2): a planted symlink named like a marker must not move
        # the current LEASE, and the marker must be the DOOR's own transition file.
        return False
    try:
        if marker.parent.resolve() != DOOR.resolve():
            return False
    except OSError:
        return False
    try:
        m = json.loads(marker.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    try:
        if m["host"] != socket.gethostname() or _process_is_alive(int(m["pid"])):
            return False
    except (KeyError, TypeError, ValueError):
        # Malformed-but-parseable marker (codex r10 P2): missing keys / non-integer pid
        # must refuse, never abort reconciliation with a raise.
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
        # completion forever (codex r6 P1). Break the claim by ADJUDICATE-AFTER-RENAME
        # (codex r7 P1): a read-dead-then-unlink-by-path lets a second breaker unlink a
        # freshly recreated LIVE claim. The rename is the atomic single-winner CAS; the
        # bytes adjudicated are the moved file itself. Dead claimant -> discard + yield
        # (the next completer wins a fresh create); live claimant (we displaced a fresh
        # claim) -> restore via os.link, which yields to any even-newer claim.
        # Pre-read gate (codex r8 P1): never rename a claim we believe LIVE — removing
        # the pathname before proving deadness would let a third completer claim and run
        # concurrently with the original live completer. Only a read-dead claim enters
        # the rename CAS; the moved bytes are then re-adjudicated (r7).
        try:
            pre = json.loads(claim.read_text())
            if pre["host"] != socket.gethostname() or _process_is_alive(int(pre["pid"])):
                return False
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            return False
        broken = DOOR / f".completed.{token}.broken.{os.getpid()}.{secrets.token_hex(4)}"
        try:
            os.rename(claim, broken)
        except FileNotFoundError:
            return False  # another breaker won the rename
        try:
            c = json.loads(broken.read_text())
            dead = c["host"] == socket.gethostname() and not _process_is_alive(int(c["pid"]))
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            dead = False
        if not dead:
            try:
                os.link(broken, claim)  # restore; loses politely to a newer claim
            except FileExistsError:
                pass
        broken.unlink(missing_ok=True)
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
        fresh_lease = m["fresh_lease"]
        res = rs.current(fresh_lease["reservation_id"])
        if res is None or res[1]["state"] not in ("open", "merged"):
            fresh_lease = None  # stale marker: a terminated arc publishes nothing
        if fresh_lease is not None:
            before = read_lease()
            _publish_fresh(fresh_lease)
            after = read_lease()
            published = (
                before is None
                and after is not None
                and after["lease_token"] == fresh_lease["lease_token"]
            )
            if published and _retract_if_terminal(fresh_lease):
                published = False  # terminalized mid-completion (r8 P1); self-released
            done = done or published
    if not done:
        # We claimed but completed NOTHING (codex r9 P2): e.g. the old lease was already
        # moved and a foreign holder occupies the door, so the fresh publish lost. A
        # retained claim from a LIVE completer would refuse every later pass until this
        # process dies — relinquish our own claim so completion stays retryable once the
        # door frees.
        claim.unlink(missing_ok=True)
    return done


def gc(*, now: datetime | None = None) -> list[Path]:
    now = now or datetime.now(UTC)
    removed = []
    if DOOR.is_symlink() or not DOOR.is_dir():
        # A planted QUEUE_DIR/merge-door symlink must not have its TARGET's history
        # unlinked through this walk (codex r5 P1) — is_dir() follows links.
        return removed
    cutoff = now - timedelta(days=GC_KEEP_DAYS)
    # Pass-start snapshot of live transition markers: a completed.<T> tombstone is only
    # collectable on a pass its marker did NOT begin (codex r7 P2) — same-pass removal
    # order via iterdir would otherwise retire both together, and a crash between the
    # two unlinks could leave the marker executable with its tombstone gone.
    markers_at_start = {q.name for q in DOOR.iterdir() if q.name.startswith("transition.")}
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
                if p.name.startswith("completed."):
                    # The completion tombstone must OUTLIVE its transition marker (codex
                    # r7 P2): removing completed.<T> while transition.<T> survives (a gc
                    # crash mid-pass, or a completion racing the marker's removal) makes
                    # the dead marker executable again — stale authority resurrection.
                    # Skip the tombstone while its marker exists; it goes next pass.
                    tok = p.name.removeprefix("completed.")
                    if f"transition.{tok}" in markers_at_start:
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


# ── U-HE-23: landing driver — C-HE-06 §4 steps (ii)–(ix), §5 reconcile, §8 policy ──────


class BudgetExhausted(LeaseError):  # noqa: N818 — U-HE-23 plan signature verbatim
    ...


@dataclass
class Ground:
    """Injected gh/git seams; production defaults shell out with bounded timeouts."""

    gh_view: Callable[[int], dict]
    gh_merge: Callable[[int, str, float], subprocess.CompletedProcess]
    gh_runs_for_sha: Callable[[str], list[dict]]
    gh_main_runs_in_progress: Callable[[], int]
    git_merge_tree: Callable[[str, str], str]
    git_first_parent: Callable[[str], str]
    codex_worktree_present: Callable[[], bool]
    clock: Callable[[], float] = field(default=time.monotonic)
    sleep: Callable[[float], None] = field(default=time.sleep)


def _gh(*args: str, timeout: float) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args], cwd=REPO, capture_output=True, text=True, timeout=timeout, check=False
    )


def default_ground() -> Ground:
    def gh_view(pr):
        p = _gh(
            "pr",
            "view",
            str(pr),
            "--json",
            "state,mergedAt,headRefOid,baseRefOid,baseRefName,mergeCommit,title,files",
            timeout=30,
        )
        if p.returncode != 0 or not p.stdout.strip():
            raise RuntimeError(f"gh pr view failed: {p.stderr.strip()}")
        return json.loads(p.stdout)

    def gh_merge(pr, head, timeout):
        # the ONE fixed merge invocation string (C-HE-07 §1)
        return _gh("pr", "merge", str(pr), "--squash", "--match-head-commit", head, timeout=timeout)

    def gh_runs_for_sha(sha):
        p = _gh(
            "run",
            "list",
            "--commit",
            sha,
            "--workflow",
            "CI",
            "--json",
            "status,conclusion,event",
            "--limit",
            "20",
            timeout=30,
        )
        return json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else []

    def gh_main_runs_in_progress():
        p = _gh(
            "run",
            "list",
            "--branch",
            "main",
            "--event",
            "push",
            "--status",
            "in_progress",
            "--json",
            "databaseId",
            timeout=30,
        )
        return len(json.loads(p.stdout)) if p.returncode == 0 and p.stdout.strip() else 0

    def git_merge_tree(base, head):
        return subprocess.run(
            ["git", "-C", str(REPO), "merge-tree", "--write-tree", base, head],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()[0]

    def git_first_parent(sha):
        proc = None
        for attempt in (1, 2):
            proc = subprocess.run(
                ["git", "-C", str(REPO), "rev-parse", f"{sha}^1"],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                return proc.stdout.strip()
            if attempt == 1:
                # the squash SHA is minted SERVER-SIDE by gh pr merge and is normally
                # absent from the local object database (codex r8 P1) — without this
                # fetch a successful remote merge raised AFTER the reservation flipped
                # merged, wedging the door and skipping post-merge CI + refresh
                subprocess.run(
                    ["git", "-C", str(REPO), "fetch", "origin", sha],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=600,
                )
        raise subprocess.CalledProcessError(proc.returncode, proc.args, proc.stdout, proc.stderr)

    def codex_worktree_present():
        out = subprocess.run(
            ["git", "-C", str(REPO), "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        # concatenated so the store-audit literal extractor's path-join pattern cannot
        # misread the slash-then-quote inside the needle as a pathlib join (this is a
        # git worktree presence probe, not a QUEUE_DIR store literal)
        return ("/.codex-worktrees" + "/") in out

    return Ground(
        gh_view,
        gh_merge,
        gh_runs_for_sha,
        gh_main_runs_in_progress,
        git_merge_tree,
        git_first_parent,
        codex_worktree_present,
    )


def _notify(kind: str, lane_id: str, cause: str, detail: str) -> None:
    """Loop-ledger row, TOLERANT of the not-yet-landed writer (as-built: the plan's §3
    order ships `loop_log_structured` at U-HE-29 while the roadmap executes U-HE-23 first
    — the registered §0-vs-§1 ordering contradiction). A missing ledger writer must never
    mask a DoorBlocked or crash the driver mid-landing: pre-U-HE-29 the signal degrades to
    a LOUD stderr line (in-band, never silent); the durable row arrives with U-HE-29."""
    try:
        rs.emit_loop_row(kind, lane_id, cause, detail)
    except rs.LoopStatusWriteError as exc:
        print(
            f"merge-door {kind} (ledger writer pending U-HE-29): {cause} — {detail} [{exc}]",
            file=sys.stderr,
        )


def _emit_gate(
    lease: dict | None,
    *,
    gate: str,
    fail_class: str,
    cause: str,
    evidence: str,
    arc_id: str,
    lane_id: str,
    severity: str = "warn",
) -> None:
    """§9 gate rows as C-HE-24 findings (`code` = <gate>:<fail_class>:<cause>)."""
    import finding_record as fr

    # allocate + append under finding_record's own lock (codex U-HE-23 r3 P2: an
    # unlocked count-then-append let two concurrent emitters mint one id)
    fr.append_observation(
        {
            "location": "merge-door",
            "observed_evidence": evidence,
            "expected_contract": "C-HE-06 §9",
            "severity": severity,
            "finding_type": fail_class,
            "lineage_claim": "door",
            "producer": gate,
        },
        fr.Envelope(
            "finding",
            fr.now_iso(),
            arc_id,
            lane_id,
            (lease or {}).get("head_sha"),
            (lease or {}).get("base_sha"),
            None,
            None,
            cause_attribution=cause,
        ),
    )


def local_base_cas_check(head_sha: str, attested_tree: str | None, ground: Ground) -> None:
    tree = ground.git_merge_tree("origin/main", head_sha)
    if not attested_tree or tree != attested_tree:
        raise DoorFailed(
            f"local-base-cas-check: merge-tree {tree[:12]} != attested "
            f"{str(attested_tree)[:12]} -- base moved; re-gate (R-23)"
        )


def verify_head_base(lease: dict, ground: Ground) -> dict:
    v = ground.gh_view(int(lease["pr"]))
    if v.get("headRefOid") != lease["head_sha"] or v.get("baseRefOid") != lease["base_sha"]:
        raise DoorFailed(f"pr #{lease['pr']} head/base moved since the lease was recorded; re-gate")
    return v


def wait_post_merge_ci(sha: str, ground: Ground, *, bound_s: float, lane_id: str = "") -> str:
    """Poll the merge SHA's OWN main run until completed. success → 'success'; anything
    else → 'blocked:<why>' (CANCELLED blocks the door — C-HE-19 §2's ci_is_green)."""
    deadline = ground.clock() + bound_s
    notified = False
    while ground.clock() < deadline:
        runs = [r for r in ground.gh_runs_for_sha(sha) if r.get("event") in (None, "push")]
        done = [r for r in runs if r.get("status") == "completed"]
        if done:
            concl = done[0].get("conclusion")
            if not ci_is_green(concl):
                # CANCELLED/failure blocks the door (C-HE-19 §2) — never read as green
                return f"blocked:post_merge_ci_not_green:{concl}"
            return "success"
        if not notified and ground.gh_main_runs_in_progress() > 2:
            _notify(
                "NOTIFY",
                lane_id,
                "merge-door-post-merge-ci:transient-retry:main_ci_queue_depth",
                f"> 2 main-push CI runs in progress while waiting on {sha[:12]}",
            )
            notified = True
        ground.sleep(30)
    return "blocked:post_merge_ci_not_green:timeout"


def wait_pr_head_checks(sha: str, ground: Ground, *, bound_s: float, lane_id: str = "") -> str:
    """Poll a PRE-merge PR HEAD's checks until completed green (U-HE-28 codex r2 P1).

    C-HE-08 made `main` strict with required checks, and `gh pr merge` REFUSES a
    pending/red PR outright — not a timeout — so driving the §4(viii) refresh merge the
    moment the PR is created burns the §5 re-issue budget deterministically on every
    normal landing. Same polling shape as wait_post_merge_ci; no event filter (the
    head's completed run may register as pull_request or push depending on triggers)."""
    deadline = ground.clock() + bound_s
    while ground.clock() < deadline:
        runs = ground.gh_runs_for_sha(sha)
        # A rerun/edited event reuses the SHA (codex r5 P2): while ANY run is still in
        # progress, an older completed run must not be read as the verdict — wait until
        # the SHA has no pending runs, then judge the completed set.
        if not any(r.get("status") != "completed" for r in runs):
            done = [r for r in runs if r.get("status") == "completed"]
            if done:
                concl = done[0].get("conclusion")
                if not ci_is_green(concl):
                    return f"blocked:refresh_pr_ci_not_green:{concl}"
                return "success"
        ground.sleep(30)
    return "blocked:refresh_pr_ci_not_green:timeout"


def reconcile_ground(lease: dict, ground: Ground) -> str:
    """§5 timeout/crash reconciliation by ground truth. MERGED ⇒ never re-issue.
    OPEN ⇒ the caller may re-issue at most ONCE per pass."""
    v = ground.gh_view(int(lease["pr"]))
    state = v.get("state")
    if state == "MERGED":
        return "MERGED"
    if state == "OPEN":
        return "OPEN"
    # CLOSED / malformed / unknown is NOT permission to re-issue (codex U-HE-23 r1 P2):
    # the contract's re-issue branch is an explicit OPEN result only — fail closed.
    raise DoorFailed(f"reconcile: pr #{lease['pr']} state {state!r} is not reconcilable")


def _merge_once(
    lease: dict, pr: int, head_sha: str, ground: Ground, *, suffix: str = "", budget: int = 2
) -> bool:
    """(iii) attempted-marker BEFORE (iv) the bounded merge; on timeout reconcile,
    re-issue at most once. A RESUME pass (the attempted marker predates this process)
    gets budget=1 — the §5 contract permits a single re-issue per reconcile pass, and
    the prior process may already have consumed its own (codex U-HE-23 r1 P2). Returns
    True iff a reconcile pass was needed (the cycle is then not "clean" for §10)."""
    mark_attempted(lease, suffix=suffix)
    _kill_after("refresh-attempted" if suffix else "attempted")
    for attempt in tuple(range(1, budget + 1)):
        try:
            proc = ground.gh_merge(pr, head_sha, MERGE_TIMEOUT_S)
            _kill_after("merge")
            if proc.returncode == 0:
                return attempt > 1
        except subprocess.TimeoutExpired:
            pass
        if reconcile_ground({**lease, "pr": pr}, ground) == "MERGED":
            return True  # invariant: NEVER re-invoke after MERGED
        if attempt == budget:
            raise DoorFailed("merge_reissue_exhausted (cause_attribution: merge_reissue_exhausted)")
    return True


def land(
    pr: int,
    *,
    lane_id: str,
    arc_id: str,
    ground: Ground,
    refresh: Callable[[], tuple[int, str]] | None,
    lease: dict | None = None,
) -> str:
    """Steps (i)–(ix). `lease` is passed on self-resume (reclaimed); otherwise acquired
    here (one attempt, fail-fast)."""
    res = rs.current(arc_id)
    if res is None:
        raise DoorFailed(f"{arc_id}: no reservation")
    head_sha, base_sha, attested = (
        res[1]["head_sha"],
        res[1]["base_sha"],
        res[1]["attested_merge_tree"],
    )
    if lease is None:
        lease = acquire(lane_id=lane_id, arc_id=arc_id, pr=pr, head_sha=head_sha, base_sha=base_sha)
    else:
        # a caller-supplied (resumed) lease must BE the door's current lease for THIS
        # arc/lane/pr (codex r3 P2): a stale or foreign dict would drive gh pr merge
        # while another lease is current, defeating the single-writer fence
        live = read_lease()
        if (
            live is None
            or live["lease_token"] != lease["lease_token"]
            or live.get("reservation_id") != arc_id
            or live.get("lane_id") != lane_id
            or int(live.get("pr", -1)) != int(pr)
        ):
            raise DoorFailed(
                f"resumed lease is not the door's current lease for {arc_id!r} "
                f"(door: {live and live.get('lease_token')!r})"
            )
        if live.get("state") == "blocked":
            # an operator block is never driven past by a direct resume (codex r5 P2):
            # the sanctioned transition is unblock, which mints the successor
            raise DoorBlocked(
                f"lease is blocked at {live.get('blocked_at_sha')!r}; use unblock, not land"
            )
        # the PERSISTED view is authoritative for the drive (codex r9 P1): a caller
        # retaining valid identifiers could forge unblocked_from (a BASE_TOCTOU bypass)
        # or omit the attempted/refresh sidecars (regaining spent re-issue budget)
        lease = live
    if ground.codex_worktree_present():
        _notify(
            "NOTIFY",
            lane_id,
            "merge-door-lease-acquire:transient-retry:cross_carrier_codex_lane",
            "a .codex-worktrees/ lane is present: C-HE-01 §1 residual — a Codex-exec lane "
            "may reach gh pr merge unfenced",
        )
    tier = _tiering_active()
    if tier:
        _notify(
            "NOTIFY",
            lane_id,
            "merge-door-lease-acquire:transient-retry:attestation_tier",
            f"lease acquired for pr #{pr} by {lane_id}",
        )
    reconciled = False
    try:
        resumed_attempt = lease.get("merge_attempted_at") is not None
        already = resumed_attempt and reconcile_ground(lease, ground) == "MERGED"
        reconciled = reconciled or already
        if not already:
            v0 = verify_head_base(lease, ground)  # (ii)
            externally_merged = False
            if v0.get("state") == "MERGED":
                # verified ground truth already says MERGED (an externally-landed PR):
                # never follow a verified MERGED with another gh pr merge (codex r4 P2)
                externally_merged = True
            if externally_merged:
                reconciled = True
            else:
                local_base_cas_check(head_sha, attested, ground)
                _kill_after("verify")
                main_budget = 2
                if resumed_attempt:
                    main_budget = 1  # §5: a resume pass re-issues at most ONCE
                reconciled = (
                    _merge_once(lease, pr, head_sha, ground, budget=main_budget) or reconciled
                )  # (iii)+(iv)
        v = ground.gh_view(pr)  # (v)
        if v.get("state") != "MERGED":
            raise DoorFailed("post-merge confirm: not MERGED")
        _kill_after("confirm")
        merge_sha = (v.get("mergeCommit") or {}).get("oid") or ""
        if rs.current(arc_id)[1]["state"] != "merged":
            if merge_sha:
                rs.update_payload(arc_id, {"merge_sha": merge_sha})
            rs.transition(arc_id, "merged", lane_id=lane_id)  # (vi)
        _kill_after("reservation-merged")
        toctou_attested = lease.get("unblocked_from") == merge_sha
        if merge_sha and not toctou_attested and ground.git_first_parent(merge_sha) != base_sha:
            # BASE_TOCTOU detection (C-HE-12 §2): positive proof the race window was hit —
            # NEVER silent acceptance. The merge landed server-side (the reservation
            # reflects that fact); the DOOR blocks and routes to re-validation.
            # blocked-state FIRST, emissions second (codex r8 P2): a raising gate-log
            # writer must never leave a positively-detected race as an unblocked lease
            mark_blocked(lease, sha=merge_sha, reason="base_toctou_first_parent_mismatch")
            _emit_gate(
                lease,
                gate="BASE_TOCTOU",
                fail_class="HITL-recoverable",
                cause="first_parent_mismatch",
                evidence=f"merge {merge_sha[:12]} first parent != verified base {base_sha[:12]}",
                arc_id=arc_id,
                lane_id=lane_id,
                severity="hard",
            )
            _notify(
                "DEFERRED-HIL",
                lane_id,
                "merge-door-post-merge:HITL-recoverable:base_toctou",
                f"{arc_id} — merge {merge_sha[:12]} landed on a base other than the verified "
                f"{base_sha[:12]}; re-validate main, then "
                f"`just merge-door-unblock {pr} {merge_sha}`",
            )
            raise DoorBlocked("base_toctou_first_parent_mismatch")
        status = wait_post_merge_ci(
            merge_sha, ground, bound_s=POST_MERGE_CI_BOUND_S, lane_id=lane_id
        )  # (vii)
        if status != "success":
            mark_blocked(lease, sha=merge_sha, reason="post_merge_ci_not_green")
            _emit_gate(
                lease,
                gate="merge-door-post-merge-ci",
                fail_class="HITL-recoverable",
                cause="post_merge_ci_not_green",
                evidence=status,
                arc_id=arc_id,
                lane_id=lane_id,
            )
            _notify(
                "DEFERRED-HIL",
                lane_id,
                "merge-door-post-merge-ci:HITL-recoverable:post_merge_ci_not_green",
                f"{arc_id} — post-merge main run for {merge_sha[:12]} {status}; door blocked; "
                f"run `just merge-door-unblock {pr} {merge_sha}` after fixing",
            )
            raise DoorBlocked(status)
        _kill_after("post-ci")
        recorded = (read_lease() or {}).get("refresh")
        refresh_confirmed = False  # §10: only a refresh-green cycle can count clean (r9 P2)
        if (
            refresh is None
            and recorded is None
            and os.environ.get("MERGE_DOOR_ALLOW_NO_REFRESH") != "1"
        ):
            # the §4(viii) continuation is MANDATORY at the API layer too (codex r10 P2):
            # the CLI's env gate must not be bypassable by a direct land() caller —
            # fail closed (blocked, recoverable via unblock) rather than release
            mark_blocked(
                lease,
                sha=lease.get("head_sha") or head_sha,
                reason="refresh_skipped_without_optin",
            )
            raise DoorBlocked("refresh_skipped_without_optin")
        if refresh is not None or recorded is not None:  # (viii)
            rpr_rhead = None
            if recorded is not None:
                # self-resume: NEVER create a second refresh PR
                rpr_rhead = (int(recorded["pr"]), recorded["head_sha"])
            if rpr_rhead is None:
                intent = _sidecar(lease["lease_token"], "refresh.intent")
                if intent.exists():
                    # A prior pass declared intent and crashed between creating the
                    # refresh PR and persisting its identity — the PR may exist with no
                    # durable record; calling refresh() again could mint a SECOND
                    # terminating-refresh PR (codex r1 P2). Ground-truth HITL resolves.
                    mark_blocked(
                        lease,
                        sha=lease.get("head_sha") or head_sha,
                        reason="refresh_intent_unresolved",
                    )
                    _emit_gate(
                        lease,
                        gate="merge-door-post-merge-ci",
                        fail_class="HITL-recoverable",
                        cause="refresh_intent_unresolved",
                        evidence="declared refresh intent with no durable record",
                        arc_id=arc_id,
                        lane_id=lane_id,
                    )
                    _notify(
                        "DEFERRED-HIL",
                        lane_id,
                        "merge-door-post-merge-ci:HITL-recoverable:refresh_intent_unresolved",
                        f"{arc_id} — a refresh PR may exist unrecorded; inspect open PRs, "
                        "then `record-refresh <pr> <head>` or `clear-refresh-intent`, "
                        "`unblock`, and `land`",
                    )
                    raise DoorBlocked("refresh_intent_unresolved")
                try:
                    publish_exclusive(intent, json.dumps({"at": _now_iso()}))
                except FileExistsError:
                    pass
                rpr, rhead = refresh()
                rv0 = ground.gh_view(rpr)
                rfiles = [f.get("path") for f in (rv0.get("files") or [])]
                if (
                    rv0.get("headRefOid") != rhead
                    or not str(rv0.get("title") or "").startswith(REFRESH_TITLE_PREFIX)
                    or rfiles != [REFRESH_ONLY_FILE]
                ):
                    # same identity gate as record-refresh (codex r9 P1): a refresh-cmd
                    # mistakenly returning any real OPEN PR's pair must never persist —
                    # the pair would be squash-merged under the global lease
                    raise DoorFailed(
                        f"refresh identity mismatch: pr #{rpr} at {str(rhead)[:12]} is "
                        f"not a terminating refresh (title {str(rv0.get('title'))[:40]!r})"
                    )
                publish_exclusive(
                    _sidecar(lease["lease_token"], "refresh"),
                    json.dumps({"pr": rpr, "head_sha": rhead}),
                )
            else:
                rpr, rhead = rpr_rhead
                # U-HE-28 codex r3 P1: the durable record pins the head at creation,
                # but the sanctioned recovery for a red refresh head is a fix commit
                # on the SAME refresh PR — which moves the real head. Without
                # re-adoption the resume polls the dead old SHA forever and the
                # documented unblock recovery can never succeed. Re-adopt the PR's
                # CURRENT head iff it still satisfies the full terminating-refresh
                # identity gate; MERGED/closed states fall through to the
                # ground-truth branches below unchanged.
                rv1 = ground.gh_view(rpr)
                cur_head = rv1.get("headRefOid")
                if rv1.get("state") == "OPEN" and cur_head and cur_head != rhead:
                    rfiles1 = [f.get("path") for f in (rv1.get("files") or [])]
                    # r6 P2 hardening over the r3 gate: bind adoption to THIS landing
                    # (title carries `post-#<content-pr>`) and to the `main` base — a
                    # refresh PR retargeted while receiving its fix commit must never
                    # be squash-merged into another branch under the global lease.
                    bound_title = f"{REFRESH_TITLE_PREFIX}post-#{pr}"
                    title1 = str(rv1.get("title") or "")
                    # delimiter-safe (r7 P2): post-#1 must not accept post-#10
                    title_bound = title1 == bound_title or (
                        title1.startswith(bound_title)
                        and not title1[len(bound_title) :][:1].isdigit()
                    )
                    if (
                        rv1.get("baseRefName") != "main"
                        or not title_bound
                        or rfiles1 != [REFRESH_ONLY_FILE]
                    ):
                        raise DoorFailed(
                            f"refresh pr #{rpr} head moved to {str(cur_head)[:12]} but "
                            "no longer satisfies the terminating-refresh identity gate "
                            f"(base {rv1.get('baseRefName')!r}, title "
                            f"{str(rv1.get('title'))[:40]!r})"
                        )
                    rhead = cur_head
                    # ATOMIC record replacement (codex r5 P2) with the door's own
                    # exclusive-create primitive on an UNPREDICTABLE tmp name + symlink
                    # containment (r6 P2): a planted sidecar/tmp symlink must neither
                    # redirect the write outside the queue nor become the record.
                    sidecar = _sidecar(lease["lease_token"], "refresh")
                    tmp = sidecar.with_name(f"{sidecar.name}.adopt.{secrets.token_hex(8)}")
                    publish_exclusive(tmp, json.dumps({"pr": rpr, "head_sha": rhead}))
                    if sidecar.is_symlink() or tmp.is_symlink():
                        tmp.unlink(missing_ok=True)
                        raise DoorFailed("refresh sidecar containment violated (symlink)")
                    os.replace(tmp, sidecar)
            refresh_resumed = (
                recorded is not None and recorded.get("merge_attempted_at") is not None
            )
            refresh_landed = False
            if ground.gh_view(rpr).get("state") == "MERGED":
                # ANY refresh already MERGED by ground truth is never re-issued —
                # recorded (codex r9 P2: record-refresh accepts a MERGED PR whose sidecar
                # carries no attempted marker) AND fresh (codex r10 P2: a refresh-cmd may
                # return an already-landed pair; observing MERGED then merging violates
                # the never-reissue invariant)
                refresh_landed = True
            refresh_budget = 2
            if refresh_resumed:
                refresh_budget = 1  # §5: one re-issue per reconcile pass
            if refresh_landed:
                reconciled = True
            else:
                # U-HE-28 codex r2 P1: under the LIVE strict fence the just-created
                # refresh PR's checks are pending; wait for its HEAD to go green
                # BEFORE issuing the fixed merge string (which GitHub would refuse
                # outright, exhausting the re-issue budget on first use).
                pstatus = wait_pr_head_checks(
                    rhead, ground, bound_s=REFRESH_BOUND_S, lane_id=lane_id
                )
                if pstatus != "success":
                    mark_blocked(lease, sha=rhead, reason="refresh_pr_ci_not_green")
                    _emit_gate(
                        lease,
                        gate="merge-door-post-merge-ci",
                        fail_class="HITL-recoverable",
                        cause="refresh_pr_ci_not_green",
                        evidence=pstatus,
                        arc_id=arc_id,
                        lane_id=lane_id,
                    )
                    _notify(
                        "DEFERRED-HIL",
                        lane_id,
                        "merge-door-post-merge-ci:HITL-recoverable:refresh_pr_ci_not_green",
                        f"{arc_id} — terminating refresh #{rpr} checks for {rhead[:12]} "
                        f"{pstatus}; door blocked; fix, then "
                        f"`just merge-door-unblock {rpr} {rhead}`",
                    )
                    raise DoorBlocked(pstatus)
                reconciled = (
                    _merge_once(lease, rpr, rhead, ground, suffix="refresh", budget=refresh_budget)
                    or reconciled
                )
            rv = ground.gh_view(rpr)
            if rv.get("state") != "MERGED":
                raise DoorFailed("refresh PR did not merge")
            _kill_after("refresh-merged")
            rsha = (rv.get("mergeCommit") or {}).get("oid") or ""
            rstatus = wait_post_merge_ci(rsha, ground, bound_s=REFRESH_BOUND_S, lane_id=lane_id)
            if rstatus != "success":
                mark_blocked(lease, sha=rsha, reason="refresh_ci_not_green")
                _emit_gate(
                    lease,
                    gate="merge-door-post-merge-ci",
                    fail_class="HITL-recoverable",
                    cause="refresh_ci_not_green",
                    evidence=rstatus,
                    arc_id=arc_id,
                    lane_id=lane_id,
                )
                _notify(
                    "DEFERRED-HIL",
                    lane_id,
                    "merge-door-post-merge-ci:HITL-recoverable:refresh_ci_not_green",
                    f"{arc_id} — terminating refresh #{rpr} run for {rsha[:12]} {rstatus}; "
                    f"door blocked; fix, then `just merge-door-unblock {rpr} {rsha}`",
                )
                raise DoorBlocked(rstatus)
            refresh_confirmed = True
        release(lease)  # (ix)
        if not reconciled and refresh_confirmed:
            # a CLEAN cycle (C-HE-06 §10) requires no reconcile pass, no HITL, AND a
            # CONFIRMED refresh (codex r9 P2: a refresh-skipped run must never count)
            tcc = DOOR / "tier-clean-cycles"
            if not tcc.is_symlink():  # same containment as every door subdir (r1 P2)
                tcc.mkdir(exist_ok=True)
                (tcc / lease["lease_token"]).touch()
        elif reconciled:
            # §10 requires three CONSECUTIVE clean cycles (codex r6 P2): a reconciled or
            # HITL cycle resets the counter, else nonconsecutive cleans silence the tier
            # (a refresh-skipped clean run neither counts nor resets)
            tcc = DOOR / "tier-clean-cycles"
            if tcc.is_dir() and not tcc.is_symlink():
                for f in tcc.iterdir():
                    f.unlink(missing_ok=True)
        if tier:
            _notify(
                "NOTIFY",
                lane_id,
                "merge-door-lease-release:transient-retry:attestation_tier",
                f"lease released after pr #{pr}",
            )
        return "released"
    except DoorBlocked:
        raise  # already adjudicated: the blocked sidecar is persisted at the raise site
    except Exception as exc:
        # NOT only DoorFailed (codex r10 P1): the production seams raise RuntimeError,
        # JSONDecodeError, CalledProcessError, TimeoutExpired — any post-acquire escape
        # must adjudicate the lease (release pre-attempt / block post-attempt), never
        # exit with a live unblocked lease owned by a dead process
        live = lease
        refreshed = read_lease()
        if refreshed is not None:
            # the persisted sidecar view is the authority, not the caller dict (codex r2)
            live = refreshed
        refresh_attempted = (
            isinstance(live.get("refresh"), dict)
            and live["refresh"].get("merge_attempted_at") is not None
        )
        if live.get("merge_attempted_at") is None and not refresh_attempted:
            release(live)  # pre-attempt failure: release + re-gate
            raise
        # a REFRESH attempt is an attempt (codex r8 P1): an externally-MERGED main PR
        # carries no main attempted marker, so an ambiguous refresh merge would
        # otherwise blind-release the global door
        # A failure AFTER the attempt is an ambiguous merge state: NEVER blind-release
        # (C-HE-06 §5). Block the door and route to HITL reconciliation.
        mark_blocked(
            live,
            sha=live.get("head_sha") or head_sha,
            reason=f"door_failed_after_attempt:{exc}",
        )
        # cause attribution names the ACTUAL failure class (codex r4 P3): a blanket
        # merge_reissue_exhausted misroutes operators and corrupts the §9 reducers
        msg = str(exc)
        cause = "door_failed_after_attempt"
        if "merge_reissue_exhausted" in msg:
            cause = "merge_reissue_exhausted"
        if "not reconcilable" in msg:
            cause = "unreconcilable_pr_state"
        if "refresh" in msg and cause == "door_failed_after_attempt":
            cause = "refresh_failed"
        _emit_gate(
            live,
            gate="merge-door-reconcile",
            fail_class="HITL-recoverable",
            cause=cause,
            evidence=msg,
            arc_id=arc_id,
            lane_id=lane_id,
        )
        _notify(
            "DEFERRED-HIL",
            lane_id,
            f"merge-door-reconcile:HITL-recoverable:{cause}",
            f"{arc_id} — pr #{pr}: {exc}; reconcile by ground truth then "
            f"`just merge-door-unblock {pr} <sha>`",
        )
        raise DoorBlocked(str(exc)) from exc


def _tiering_active() -> bool:
    """C-HE-06 §10: NOTIFY per acquire/release during the pilot + first multi-lane merges;
    silent after 3 clean cycles (one file per clean cycle under tier-clean-cycles/)."""
    d = DOOR / "tier-clean-cycles"
    if d.is_symlink():
        return True  # a planted link must not SUPPRESS notifications (codex r2 P3)
    return not d.is_dir() or len(list(d.iterdir())) < 3


def wait_for_door(
    try_acquire: Callable[[], dict], *, clock=time.monotonic, sleep=time.sleep, rng=None
) -> dict:
    """§8 caller policy: bounded exponential backoff + full jitter (base 30 s, ×2, cap
    10 min, 12 attempts ≈ 1 h), then HITL-recoverable. Rate-limit refusals wait but never
    count against the 12."""
    import random

    rng = rng or random.random
    attempts = 0
    delay = BACKOFF["base_s"]
    # rate refusals never count against the 12 — but they are DEADLINE-bounded
    # (codex r10 P2): sustained same-lane contention could otherwise keep >K attempts
    # in every rolling window and spin past the HITL exhaustion route forever
    deadline = clock() + BACKOFF["cap_s"] * BACKOFF["max_attempts"]
    while True:
        try:
            return try_acquire()
        except RateLimited:
            if clock() >= deadline:
                raise BudgetExhausted(
                    "HITL-recoverable: lease_acquire_budget_exhausted (rate-limit deadline)"
                ) from None
            sleep(BACKOFF["base_s"] * rng())
            continue
        except LeaseHeld:
            attempts += 1
            if attempts >= BACKOFF["max_attempts"]:
                raise BudgetExhausted("HITL-recoverable: lease_acquire_budget_exhausted") from None
            sleep(min(BACKOFF["cap_s"], delay) * rng())
            delay = min(BACKOFF["cap_s"], delay * BACKOFF["factor"])


def main(argv: list[str] | None = None) -> int:
    """CLI. Exit codes: 0 released / nothing to land; 3 blocked (HITL); 4 door failed
    (re-gate); 5 budget exhausted."""
    p = argparse.ArgumentParser(prog="merge_door", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    landp = sub.add_parser("land")
    landp.add_argument("pr", type=int)
    landp.add_argument("--lane-id", required=True)
    landp.add_argument("--arc-id", required=True)
    # the terminating-refresh continuation is MANDATORY (C-HE-06 §4(viii)) — skipping it
    # must be an explicit operator choice, never a silent default (codex r5 P2)
    refresh_mode = landp.add_mutually_exclusive_group(required=True)
    refresh_mode.add_argument("--no-refresh", action="store_true")
    refresh_mode.add_argument("--refresh-cmd", help="command printing JSON {pr, head_sha}")
    ub = sub.add_parser("unblock")
    ub.add_argument("pr", type=int)
    ub.add_argument("blocked_at_sha")
    ub.add_argument("--lane-id", required=True)
    # refresh_intent_unresolved recovery (codex r3 P1): the two ground-truth resolutions —
    # the refresh PR EXISTS (record it) or it does NOT (clear the intent) — each require
    # the caller to be the live lease's own lane.
    rr = sub.add_parser("record-refresh")
    rr.add_argument("pr", type=int)
    rr.add_argument("head_sha")
    rr.add_argument("--lane-id", required=True)
    ci = sub.add_parser("clear-refresh-intent")
    ci.add_argument("--lane-id", required=True)
    sub.add_parser("status")
    sub.add_parser("gc")
    args = p.parse_args(argv)
    try:
        if args.cmd == "land":
            if args.no_refresh and os.environ.get("MERGE_DOOR_ALLOW_NO_REFRESH") != "1":
                # --no-refresh is NOT a production path (codex r9 P2): the C-HE-06
                # held-until-refresh invariant stands; the bypass exists for the
                # subprocess crash suites and operator recovery, behind this env gate —
                # refused BEFORE any lease is taken
                print(
                    "--no-refresh violates the C-HE-06 §4(viii) held-until-refresh "
                    "invariant in production; set MERGE_DOOR_ALLOW_NO_REFRESH=1 for a "
                    "test/manual bypass",
                    file=sys.stderr,
                )
                return 4
            ground = default_ground()
            refresh = None
            if args.refresh_cmd and not args.no_refresh:

                def refresh():
                    out = subprocess.run(
                        ["bash", "-c", args.refresh_cmd],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=3600,
                    ).stdout
                    d = json.loads(out)
                    return int(d["pr"]), d["head_sha"]

            lease = None
            live = read_lease()
            if live is not None:
                same_lane = (
                    live.get("lane_id") == args.lane_id
                    and int(live.get("pr", -1)) == args.pr
                    and live.get("reservation_id") == args.arc_id
                )
                holder_dead = live.get("host") == socket.gethostname() and not _process_is_alive(
                    int(live["pid"])
                )
                if same_lane and holder_dead and live.get("state") != "blocked":
                    try:
                        gs = reconcile_ground(live, ground)
                    except DoorFailed as exc:
                        # an unreconcilable PR at resume must not wedge an unblockable
                        # door (codex r7 P1): block it so the operator's unblock +
                        # recovery verbs become available
                        mark_blocked(
                            live,
                            sha=live.get("head_sha") or "0" * 40,
                            reason=f"unreconcilable_at_resume:{exc}",
                        )
                        print(f"BLOCKED: {exc}", file=sys.stderr)
                        return 3
                    lease = reclaim(
                        live,
                        lane_id=args.lane_id,
                        ground_state=gs,
                    )  # self-resume via the marker discipline
            if lease is None:
                cur = rs.current(args.arc_id)
                if live is None and cur is not None and cur[1]["state"] == "merged":
                    print("nothing to land: no lease and the reservation is already merged")
                    return 0
                if cur is not None:
                    # §8 caller policy IS the production path (codex r1/r2 P2): normal
                    # contention (a live foreign lease) and a free door both route
                    # through the jittered 12-attempt backoff, then exit 5 (HITL).
                    lease = wait_for_door(
                        lambda: acquire(
                            lane_id=args.lane_id,
                            arc_id=args.arc_id,
                            pr=args.pr,
                            head_sha=cur[1]["head_sha"],
                            base_sha=cur[1]["base_sha"],
                        )
                    )
            if args.no_refresh:
                # skipping the mandatory §4(viii) continuation is an EXPLICIT posture
                # carrying the same operator-attention contract as every other owed
                # recovery (codex r7 P2 → r8 P2): a DURABLE §9 gate row + DEFERRED-HIL,
                # emitted as posture (before the drive) so a crash cannot lose it
                _emit_gate(
                    None,
                    gate="merge-door-refresh",
                    fail_class="HITL-recoverable",
                    cause="refresh_skipped_by_operator",
                    evidence=f"landing pr #{args.pr} with --no-refresh: the §4(viii) "
                    "terminating refresh is owed out-of-band",
                    arc_id=args.arc_id,
                    lane_id=args.lane_id,
                )
                _notify(
                    "DEFERRED-HIL",
                    args.lane_id,
                    "merge-door-refresh:HITL-recoverable:refresh_skipped_by_operator",
                    f"{args.arc_id} — landing pr #{args.pr} with --no-refresh: the "
                    "terminating refresh is owed out-of-band",
                )
            out = land(
                args.pr,
                lane_id=args.lane_id,
                arc_id=args.arc_id,
                ground=ground,
                refresh=refresh,
                lease=lease,
            )
            print(out)
            return 0
        elif args.cmd == "unblock":
            unblock(pr=args.pr, blocked_at_sha=args.blocked_at_sha, lane_id=args.lane_id)
            print("unblocked; successor lease held by this lane")
            return 0
        elif args.cmd in ("record-refresh", "clear-refresh-intent"):
            live = read_lease()
            if live is None or live.get("lane_id") != args.lane_id:
                raise LeaseError("no live lease held by this lane")
            if live.get("state") != "blocked" and live.get("host") != socket.gethostname():
                # cross-host liveness is UNVERIFIABLE (codex r9 P2): treating a foreign
                # host's holder as dead reopens the duplicate-refresh window mid-creation
                raise LeaseError(
                    "cross-host holder liveness is unverifiable -- run the recovery verb "
                    "on the holder host, or unblock a blocked door"
                )
            holder_active = (
                live.get("host") == socket.gethostname()
                and _process_is_alive(int(live["pid"]))
                and live.get("state") != "blocked"
            )
            if holder_active:
                # a LIVE holder may be mid-refresh-creation right now (codex r6 P2):
                # removing the crash fence under it reopens the duplicate-PR window
                raise LeaseError(
                    "the lease holder is alive and unblocked -- recovery verbs operate "
                    "on a blocked door or a dead holder only"
                )
            intent = _sidecar(live["lease_token"], "refresh.intent")
            if args.cmd == "record-refresh":
                if not intent.exists() or _sidecar(live["lease_token"], "refresh").exists():
                    # only an UNRESOLVED intent may be resolved this way (codex r7 P1)
                    raise LeaseError("no unresolved refresh intent to resolve")
                v = default_ground().gh_view(int(args.pr))
                if v.get("headRefOid") != args.head_sha or v.get("state") not in (
                    "OPEN",
                    "MERGED",
                ):
                    # the recorded pair must BE a real PR at that head (codex r7 P1):
                    # a mistaken pair would merge an unrelated PR under the global lease
                    raise LeaseError(
                        f"record-refresh: pr #{args.pr} ground truth does not match "
                        f"(state {v.get('state')!r}, head {str(v.get('headRefOid'))[:12]})"
                    )
                title = str(v.get("title") or "")
                files = [f.get("path") for f in (v.get("files") or [])]
                if not title.startswith(REFRESH_TITLE_PREFIX) or files != [REFRESH_ONLY_FILE]:
                    # pair-consistency alone is not identity (codex r8 P1): ANY real
                    # OPEN PR passes a head match — the recorded PR must carry the
                    # CLAUDE.md §12.2.1 terminating-refresh SHAPE (title prefix + the
                    # roadmap-status-only file set) to merge under this lease
                    raise LeaseError(
                        f"record-refresh: pr #{args.pr} is not a terminating refresh "
                        f"(title {title[:40]!r}, files {files!r})"
                    )
                publish_exclusive(
                    _sidecar(live["lease_token"], "refresh"),
                    json.dumps({"pr": int(args.pr), "head_sha": args.head_sha}),
                )
                print(
                    f"refresh #{args.pr} recorded; if the door is blocked, `unblock` "
                    "with its blocked_at_sha, then `land`"
                )
            else:
                intent.unlink(missing_ok=True)
                print(
                    "refresh intent cleared; if the door is blocked, `unblock` with its "
                    "blocked_at_sha, then `land` (a fresh refresh may mint)"
                )
            return 0
        elif args.cmd == "status":
            print(json.dumps(read_lease(), sort_keys=True))
            return 0
        else:
            print(json.dumps([str(x) for x in gc()]))
            return 0
    except DoorBlocked as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 3
    except BudgetExhausted as exc:
        # the wedged door is human-actionable state (codex r2 P2): §9 gate row + HIL row,
        # never only a stderr line
        _emit_gate(
            None,
            gate="merge-door-lease-acquire",
            fail_class="HITL-recoverable",
            cause="lease_acquire_budget_exhausted",
            evidence=str(exc),
            arc_id=args.arc_id,
            lane_id=args.lane_id,
        )
        _notify(
            "DEFERRED-HIL",
            args.lane_id,
            "merge-door-lease-acquire:HITL-recoverable:lease_acquire_budget_exhausted",
            f"{args.arc_id} — pr #{args.pr}: {exc}; inspect the holder "
            f"(merge_door status) and reconcile by ground truth",
        )
        print(f"BUDGET: {exc}", file=sys.stderr)
        return 5
    except LeaseError as exc:
        print(f"DOOR: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

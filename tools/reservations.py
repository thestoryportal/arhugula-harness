#!/usr/bin/env python3
"""Arc reservation record (C-HE-03): three-state, PR-tagged, generation-versioned.

One reservation per arc_id at QUEUE_DIR/reservations/<arc_id>/<gen>.json. Each file is an
IMMUTABLE FULL SNAPSHOT created by exclusive create; the current record is the highest gen.
Every mutation is one CAS: read head n -> build the complete new payload -> exclusive-create
<n+1>.json. Losing the CAS means re-read, RE-VALIDATE the intended transition against the new
head's state, then retry (<= 8). There is no rename or replace on reservation records, ever.

States: pending -> open -> {merged | abandoned}. No tier reclaims on elapsed time (D8):
staleness is reconciled from ground truth or escalated to a human (see reconcile(), U-HE-18).
`_provenance.pid/host` MUST NOT be read by any state-machine decision -- the reservation spans
an hours-long handoff; liveness and validity are decoupled -- with the single named exception
of dead-claim recovery transfer (transfer_holder, C-HE-03 §6).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import socket
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from arc_metrics import QUEUE_DIR, REPO, _process_is_alive, publish_exclusive

STATES = ("pending", "open", "merged", "abandoned")
TERMINAL = frozenset({"merged", "abandoned"})
LEGAL_TRANSITIONS = frozenset(
    {("pending", "open"), ("open", "merged"), ("open", "abandoned"), ("pending", "abandoned")}
)
CAS_RETRIES = 8
SEQ_RETRIES = 64
CHAIN_DEPTH_CAP = 5
STALE_AFTER_S = 24 * 3600
GC_KEEP_DAYS = 30
ARC_TYPES = ("inventing", "applying")
PHASES = (
    "queue",
    "execute",
    "capture",
    "absorb",
    "edit",
    "verify",
    "result_capture_process_exit",
    "result_capture_log_write",
    "verify_unavailable",
)
_STATE_KEYS = frozenset({"state", "generation", "prev_generation", "seq", "arc_id", "_provenance"})
#: The ONLY payload fields a caller may set after `reserve()` (Codex round-1 P1): back-fills +
#: sensors + pilot tag. `lane_id` moves only via transition(pending->open) or transfer_holder();
#: `arc_type`/`arc_type_declared_at`/`reserved_at`/`superseded_by`/`phases`/`round_outcomes`
#: have their own dedicated writers.
PAYLOAD_MUTABLE = frozenset(
    {
        "pr",
        "head_sha",
        "base_sha",
        "attested_merge_tree",
        "merge_sha",
        "concurrent_lanes_min",
        "concurrent_lanes_max",
        "pilot_run_id",
    }
)
TRANSITION_MUTABLE = PAYLOAD_MUTABLE | {"concurrent_lanes_at_open"}
#: C-HE-03 §3 value domains for the mutable fields (codex round-2 P2): int-typed fields are
#: `<int|null>` (bool excluded — it IS an int subclass), sha/oid/tag fields `<str|null>`,
#: lane-count sensors nonnegative. Enforced at the single write funnel (`_check_updates`).
_INT_FIELDS = frozenset({"pr"})
_COUNT_FIELDS = frozenset(
    {"concurrent_lanes_min", "concurrent_lanes_max", "concurrent_lanes_at_open"}
)
_STR_FIELDS = frozenset({"pilot_run_id"})
#: `<sha|null>` / `<oid|null>` fields (C-HE-03 §3): nonempty hex, 7-64 chars (abbreviated
#: through sha256) -- an empty or malformed value in an immutable snapshot would poison the
#: C-HE-06 step (ii) head/base confirmation and the merge-tree compare (codex round-11 P3).
_SHA_FIELDS = frozenset({"head_sha", "base_sha", "attested_merge_tree", "merge_sha"})
_SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")


class ReservationError(RuntimeError):
    """Named, fail-closed. Never swallowed."""


class ReservationHeld(ReservationError):  # noqa: N818 — U-HE-17 plan signature verbatim
    """A pending/open reservation exists: a second lane's selection MUST fail (C-HE-03 §4)."""


class IllegalTransition(ReservationError):  # noqa: N818 — U-HE-17 plan signature verbatim
    """The intended transition is not legal from the (re-read) head state."""


class ChainError(ReservationError):
    """superseded_by chain cycle or depth > CHAIN_DEPTH_CAP."""


class RoundOutcomeConflict(ReservationError):  # noqa: N818 — Conflict IS the condition named
    """The requested round_n is already recorded with different content (append-only map).
    Carries the existing row as `.existing` so callers can distinguish a cross-channel
    collision (failover leg -> allocate a fallback key) from a same-channel anomaly
    (report loudly, never renumber) — codex round-7 P2."""

    def __init__(self, msg: str, existing: dict | None = None) -> None:
        super().__init__(msg)
        self.existing = existing or {}


class LoopStatusWriteError(ReservationError):
    """The shared loop_status.md could not be written -- an operator recovery signal would
    be lost."""


def reservations_root() -> Path:
    r = QUEUE_DIR / "reservations"
    if r.is_symlink():
        # the containment fences below all derive their boundary from THIS path; a planted
        # QUEUE_DIR/reservations symlink would relocate the entire store outside QUEUE_DIR
        # and make every relative check pass against the external target (codex round-11
        # P2). Refusing here, at the single source, closes the whole location class.
        raise ReservationError("QUEUE_DIR/reservations is a symlink -- refused")
    return r


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_id(name: str, value: str) -> None:
    # every caller passes an AUTHORITY-bearing id (lane_id at reserve/transition/transfer):
    # None or empty is indistinguishable from "no holder" in every reader and would let two
    # None-holders satisfy the holder fence (codex round-9 P3, round-11 P2).
    if value is None or value == "":
        raise ReservationError(f"{name} must be a nonempty identifier, got {value!r}")
    if ":" in value:
        raise ReservationError(
            f"{name} must not contain ':' (finding_id/code delimiter): {value!r}"
        )


def mint_lane_id(worktree: Path) -> str:
    host = socket.gethostname().split(".")[0].replace(":", "-")
    return f"{host}-{worktree.name}-{secrets.token_hex(4)}".replace(":", "-")


def _dir(arc_id: str) -> Path:
    # Mirror the closure queue's arc_id rules (arc_metrics.queue_capture) so an id that
    # reserves here can always drain there (codex round-12 P3): a single safe path
    # component; dot-prefixed ids are infrastructure (`.seq`, stagers) and invisible to
    # sibling_open_count/gc (codex round-2 P3); `.taken` is the claim/recovery namespace;
    # the worst-case recovery filename must stay under NAME_MAX in bytes.
    if arc_id != Path(arc_id).name or arc_id in ("", "..") or arc_id.startswith("."):
        raise ReservationError(f"bad arc_id {arc_id!r}")
    if ".taken" in arc_id:
        raise ReservationError(f"bad arc_id {arc_id!r}: '.taken' is a reserved suffix")
    worst = f"{arc_id}.taken.recover.{socket.gethostname()}.{os.getpid()}".encode()
    if len(worst) > 240:
        raise ReservationError(f"bad arc_id: {len(worst)} bytes with recovery suffix (max 240)")
    d = reservations_root() / arc_id
    # A pre-planted symlink at reservations/<arc_id> would let every read follow forged
    # state and every write escape QUEUE_DIR (mkdir(exist_ok=True) accepts a link to a
    # directory; publish_exclusive would then create gens at its target) -- refuse at the
    # single path funnel, not only in gc (codex round-8 P2).
    if d.is_symlink():
        raise ReservationError(f"{arc_id}: reservation path is a symlink -- refused")
    return d


def _check_updates(fn: str, updates: dict, allowed: frozenset[str]) -> None:
    """Allowlist + C-HE-03 §3 value-domain check at the single write funnel."""
    bad = set(updates) - allowed
    if bad:
        raise ReservationError(f"{fn} may not set {sorted(bad)}; allowed: {sorted(allowed)}")
    for k, v in updates.items():
        if v is None:
            continue
        if k in _INT_FIELDS and (isinstance(v, bool) or not isinstance(v, int)):
            raise ReservationError(f"{fn}: {k} must be int|null (C-HE-03 §3), got {v!r}")
        if k in _COUNT_FIELDS and (isinstance(v, bool) or not isinstance(v, int) or v < 0):
            raise ReservationError(f"{fn}: {k} must be a nonnegative int|null, got {v!r}")
        if k in _STR_FIELDS and not isinstance(v, str):
            raise ReservationError(f"{fn}: {k} must be str|null (C-HE-03 §3), got {v!r}")
        if k in _SHA_FIELDS and (not isinstance(v, str) or not _SHA_RE.match(v)):
            raise ReservationError(
                f"{fn}: {k} must be a 7-64 char lowercase-hex sha/oid or null "
                f"(C-HE-03 §3), got {v!r}"
            )


def alloc_seq() -> int:
    """Filesystem-derived monotonic counter (never date-sourced, C-HE-03 §3)."""
    d = reservations_root() / ".seq"
    d.mkdir(parents=True, exist_ok=True)
    # same containment fence as _write_gen: a pre-planted `.seq` symlink would let external
    # contents control the ordering authority (codex round-10 P2)
    if d.is_symlink() or not d.resolve().is_relative_to(reservations_root().resolve()):
        raise ReservationError(".seq allocator path escaped QUEUE_DIR -- refused")
    for _ in range(SEQ_RETRIES):
        existing = [int(p.name) for p in d.iterdir() if p.name.isdigit()]
        n = (max(existing) if existing else 0) + 1
        try:
            publish_exclusive(d / str(n), "")
            return n
        except FileExistsError:
            continue
    raise ReservationError(f"seq allocation lost {SEQ_RETRIES} races")


def current(arc_id: str) -> tuple[int, dict] | None:
    d = _dir(arc_id)
    if not d.is_dir():
        return None
    gens = []
    for gp in d.glob("*.json"):
        if not gp.stem.isdigit():
            continue
        if gp.is_symlink():
            # a planted per-FILE symlink (e.g. 999.json -> outside) must never inject a
            # forged head that CAS operations would treat as authoritative, and must never
            # be silently ignored either -- fail loudly at the single read funnel
            # (codex round-10 P2).
            raise ReservationError(f"{arc_id}: generation file {gp.name} is a symlink -- refused")
        gens.append(int(gp.stem))
    if not gens:
        return None
    head = max(gens)
    return head, json.loads((d / f"{head}.json").read_text())


def _provenance() -> dict:
    return {"pid": os.getpid(), "host": socket.gethostname(), "reachable_from_state_machine": False}


def _write_gen(arc_id: str, gen: int, payload: dict) -> None:
    d = _dir(arc_id)
    d.mkdir(parents=True, exist_ok=True)
    # Re-check AFTER mkdir, immediately before publish: _dir()'s check alone is TOCTOU --
    # a link installed between check and write would be followed by mkdir(exist_ok=True)
    # (codex round-9 P2). Cooperative-lane model (X-AL-1): this narrows the window to the
    # syscall gap; a hostile-adversary fence is the merge-door's C-HE-08 concern, not this
    # record's.
    if d.is_symlink() or not d.resolve().is_relative_to(reservations_root().resolve()):
        raise ReservationError(f"{arc_id}: reservation path escaped QUEUE_DIR -- refused")
    publish_exclusive(d / f"{gen}.json", json.dumps(payload, sort_keys=True))


def reserve(
    arc_id: str, *, lane_id: str, branch: str, arc_type: str, arc_type_declared_at: str = "open"
) -> dict:
    """(none) -> pending at arc OPEN. Refuses if a pending/open reservation exists
    (selection-time fence)."""
    _check_id("lane_id", lane_id)
    if arc_type_declared_at not in ("open", "close"):
        # reserve() IS the open-time capture point (C-HE-26 §1) -- arbitrary labels are
        # refused (codex round-6 P3). "close" is legal ONLY for the documented one-time
        # legacy-queue bootstrap at drain (plan §6 open item 3 / U-HE-19 / U-HE-44
        # forward-register row; codex round-13 P2): entries queued before reservations
        # existed are reserved at drain with the truthful close-time label.
        raise ReservationError(
            f"arc_type_declared_at must be 'open' or 'close' (C-HE-03 §3), "
            f"got {arc_type_declared_at!r}"
        )
    if arc_type not in ARC_TYPES:
        raise ReservationError(
            f"arc_type is required at open and must be one of {ARC_TYPES} (C-HE-26 §1); "
            f"got {arc_type!r}"
        )
    cur = current(arc_id)
    if cur is not None:
        state = cur[1]["state"]
        if state in ("pending", "open"):
            raise ReservationHeld(
                f"{arc_id}: reservation is {state} (held by {cur[1]['lane_id']}) "
                "-- selection refused"
            )
        raise ReservationError(
            f"{arc_id}: reservation already terminal ({state}); arc_id reuse is not a path"
        )
    ts = now_iso()
    payload = {
        "arc_id": arc_id,
        "generation": 1,
        "prev_generation": None,
        "state": "pending",
        "lane_id": lane_id,
        "branch": branch,
        "pr": None,
        "head_sha": None,
        "base_sha": None,
        "attested_merge_tree": None,
        "arc_type": arc_type,
        "arc_type_declared_at": arc_type_declared_at,
        "reserved_at": ts,
        "transitioned_at": ts,
        "seq": alloc_seq(),
        "superseded_by": None,
        "concurrent_lanes_at_open": None,
        "phases": {},
        "round_outcomes": {},
        "merge_sha": None,
        "_provenance": _provenance(),
    }
    try:
        _write_gen(arc_id, 1, payload)
    except FileExistsError as exc:
        raise ReservationHeld(f"{arc_id}: another lane reserved it first") from exc
    return payload


def _cas_next(arc_id: str, build: Callable[[dict], dict]) -> dict:
    """Read head -> build complete new payload -> exclusive-create <n+1>. Loser re-reads and
    re-validates."""
    for _ in range(CAS_RETRIES):
        cur = current(arc_id)
        if cur is None:
            raise ReservationError(f"{arc_id}: no reservation")
        gen, head = cur
        new = build(dict(head))  # MUST re-validate against THIS head; raises if now illegal
        new.update(
            generation=gen + 1, prev_generation=gen, seq=alloc_seq(), _provenance=_provenance()
        )
        try:
            _write_gen(arc_id, gen + 1, new)
            return new
        except FileExistsError:
            continue  # lost the CAS: loop re-reads the new head and re-validates
    raise ReservationError(f"{arc_id}: CAS lost {CAS_RETRIES} times")


def transition(
    arc_id: str,
    to_state: str,
    *,
    lane_id: str,
    updates: dict | None = None,
    superseded_by: str | None = None,
    expect: dict | None = None,
) -> dict:
    _check_id("lane_id", lane_id)
    if to_state == "abandoned" and not superseded_by:
        raise ReservationError("superseded_by is MANDATORY on abandoned (C-HE-03 §2)")
    if superseded_by is not None:
        _dir(superseded_by)  # shape check: same rules as any arc_id (codex round-6 P2)
    if to_state != "abandoned" and superseded_by:
        # superseded_by belongs to `abandoned` records only (C-HE-03 §2); a merged record
        # carrying a supersession pointer is mutually inconsistent landing metadata
        # (codex round-4 P2).
        raise ReservationError(
            f"superseded_by is only legal on abandoned, not {to_state} (C-HE-03 §2)"
        )
    if updates and "concurrent_lanes_at_open" in updates and to_state != "open":
        # the sensor is captured at the pending->open flip and never rewritten by a later
        # transition (C-HE-03 §7; codex round-4 P2).
        raise ReservationError(
            "concurrent_lanes_at_open is captured only at the pending->open flip (C-HE-03 §7)"
        )

    def build(head: dict) -> dict:
        if (head["state"], to_state) not in LEGAL_TRANSITIONS:
            raise IllegalTransition(
                f"{arc_id}: {head['state']}->{to_state} is illegal from head gen "
                f"{head['generation']}"
            )
        if expect:
            # Bind the transition to the head the caller's decision was made against
            # (codex U-HE-18 r1 P1): a reconcile that confirmed PR N merged must not
            # terminalize a head whose `pr` was concurrently re-bound to N+1. Validated
            # INSIDE the CAS build so a lost race re-validates against the new head.
            for k, v in expect.items():
                if head.get(k) != v:
                    raise IllegalTransition(
                        f"{arc_id}: {k} changed since the ground-truth check "
                        f"({head.get(k)!r} != {v!r}); re-reconcile against the new head"
                    )
        if head["state"] == "open" and head["lane_id"] != lane_id:
            # holder-only: an `open` reservation is terminalized only by the lane that holds
            # it (C-HE-03 §6; Codex round-3 P1). pending->abandoned by a superseding arc has
            # no holder yet and stays open to any lane.
            raise IllegalTransition(
                f"{arc_id}: {head['state']}->{to_state} requires the holder "
                f"({head['lane_id']}), not {lane_id}"
            )
        if superseded_by:
            sup = current(superseded_by)
            if sup is None:
                # the chain walks reservation-to-reservation (C-HE-03 §2); committing a
                # pointer at a missing reservation into an IMMUTABLE terminal head would
                # make walk_terminal raise forever with no repair (codex round-6 P2).
                raise ReservationError(
                    f"{arc_id}: superseded_by names a missing reservation "
                    f"{superseded_by!r}; reserve the superseding arc first (C-HE-03 §2)"
                )
            if head["state"] == "pending" and sup[1]["lane_id"] != lane_id:
                # C-HE-03 §5: pending->abandoned happens only via an operator RESOLVED-HIL
                # or a superseding arc -- both resolve through a superseder the resolving
                # lane OWNS; without this any lane could remove another lane's scheduling
                # fence (codex round-8 P1). Scoped to PENDING heads only: open->abandoned
                # is already gated by the §6 open-holder rule above, and the open holder
                # may legitimately point at a superseder another lane owns
                # (codex round-9 P2).
                raise IllegalTransition(
                    f"{arc_id}: pending abandonment requires the caller to hold the "
                    f"superseding reservation {superseded_by!r} (held by "
                    f"{sup[1]['lane_id']}, not {lane_id}) -- C-HE-03 §5"
                )
        head["state"] = to_state
        head["transitioned_at"] = now_iso()
        if superseded_by:
            head["superseded_by"] = superseded_by
        if to_state == "open":
            head["lane_id"] = lane_id  # the holder = the draining lane
        if updates:
            _check_updates("transition()", updates, TRANSITION_MUTABLE)
            head.update(updates)
        return head

    return _cas_next(arc_id, build)


def update_payload(arc_id: str, updates: dict) -> dict:
    """Payload-only CAS restricted to PAYLOAD_MUTABLE (pr / head_sha / base_sha /
    attested_merge_tree / concurrent_lanes_min|max / pilot_run_id). Never a state change,
    never the holder, never the open-time labels.

    Concurrency note (codex round-2 P2, registered): on a CAS loss the re-applied field
    values are last-writer-wins. The merge-door tuple fields (`head_sha`/`base_sha`/
    `attested_merge_tree`) are single-writer by flow -- the holder lane's own ship-pr
    back-fills them (C-HE-03 §3) -- and C-HE-06 step (ii) re-confirms head/base against
    `gh` and byte-compares the merge tree at the door, so a stale tuple cannot merge.
    The flow-level wiring lands at U-HE-19/U-HE-21."""

    def build(head: dict) -> dict:
        # backfills are open-window operations (C-HE-03 §3: ship-pr writes them before the
        # merged flip); a CAS replay onto a terminal head could stamp stale SHAs over the
        # terminal audit used by attestation checks (codex round-5 P2).
        _refuse_terminal_accretion(arc_id, "update_payload", head)
        _check_updates("update_payload", updates, PAYLOAD_MUTABLE)
        head.update(updates)
        return head

    return _cas_next(arc_id, build)


def transfer_holder(arc_id: str, *, from_lane_id: str, to_lane_id: str) -> dict:
    """The NAMED D2 exception (C-HE-03 §6): dead-claim recovery transfers an `open`
    reservation's holder to the recovering lane in the same recovery step. Precondition
    re-validated on the head.

    Authorization boundary (codex round-2 P2, registered): the DEADNESS adjudication --
    `_recover_dead_claims()`'s pid+host liveness check on the restored `.taken` -- lives at
    the recovery call site (C-HE-03 §6 [V]; lands with the drain integration, U-HE-19).
    This primitive records the transfer; it is a cooperative-coordination CAS, not a
    security fence -- exactly as `transition()` trusts its caller's `lane_id`."""
    _check_id("lane_id", to_lane_id)

    def build(head: dict) -> dict:
        if head["state"] != "open" or head["lane_id"] != from_lane_id:
            raise IllegalTransition(
                f"{arc_id}: transfer precondition stale (state={head['state']}, "
                f"holder={head['lane_id']})"
            )
        head["lane_id"] = to_lane_id
        head["transitioned_at"] = now_iso()
        return head

    return _cas_next(arc_id, build)


def _refuse_terminal_accretion(arc_id: str, fn: str, head: dict) -> None:
    """Accretion is confined to the active arc window (C-HE-03 §3, C-HE-27 §3: `during the
    open window`): a late emitter publishing generations onto a merged/abandoned record
    would race terminal audit data with post-merge activity (codex round-4 P2)."""
    if head["state"] in TERMINAL:
        raise IllegalTransition(
            f"{arc_id}: {fn} on a {head['state']} reservation -- accretion is confined "
            "to the open window (C-HE-03 §3)"
        )


def _outcome_row(channel: str, terminal: str, finding_count: int) -> dict:
    """C-HE-25 outcome value with domains enforced at the write funnel: terminal from the
    C-HE-16 §3 triple; finding_count a nonnegative int, bool excluded (codex round-8 P3)."""
    if terminal not in ("APPROVE", "BLOCK", "REVIEWER_UNAVAILABLE"):
        raise ReservationError(
            f"terminal must be APPROVE|BLOCK|REVIEWER_UNAVAILABLE, got {terminal!r}"
        )
    if isinstance(finding_count, bool) or not isinstance(finding_count, int) or finding_count < 0:
        raise ReservationError(f"finding_count must be a nonnegative int, got {finding_count!r}")
    if not channel or "/" in channel or ":" in channel:
        raise ReservationError(f"channel must be a nonempty '/'-free, ':'-free id, got {channel!r}")
    return {"channel": channel, "terminal": terminal, "finding_count": finding_count}


def record_phase(arc_id: str, phase: str, edge: str, ts: str | None = None) -> dict:
    if phase not in PHASES or edge not in ("start", "end"):
        raise ReservationError(f"bad phase/edge {phase!r}/{edge!r}")
    if ts is not None:
        try:
            datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError) as exc:
            # a malformed timestamp in an immutable snapshot poisons every later duration
            # read of the C-HE-27 phase record (codex round-12 P3)
            raise ReservationError(
                f"ts must be ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ): {ts!r}"
            ) from exc

    def build(head: dict) -> dict:
        _refuse_terminal_accretion(arc_id, "record_phase", head)
        slot = head.setdefault("phases", {}).setdefault(phase, {})
        val = ts or now_iso()
        existing = slot.get(edge)
        if existing is not None:
            if ts is None or ts == existing:
                # replay-idempotent (codex round-14/15 P2): the edge is already durably
                # recorded; a retry without an explicit timestamp (the CLI's only form)
                # or with the identical one is a no-op, so a crash after publication has
                # a usable resume path.
                return head
            # an EXPLICIT different timestamp is a rewrite of a durable measurement
            # (C-HE-27 §3) -- N6 reads only the folded head; refuse.
            raise ReservationError(
                f"{arc_id}: phase {phase}.{edge} already recorded ({existing}); "
                f"refusing rewrite to {val}"
            )
        slot[edge] = val
        return head

    return _cas_next(arc_id, build)


def record_round_outcome(
    arc_id: str, round_n: int, *, channel: str, terminal: str, finding_count: int
) -> dict:
    """C-HE-25 per-round terminal outcome, accreted on the reservation during the open window
    (like phases) and folded into the arc row at drain. `terminal` MUST be one of the
    C-HE-16 §3 triple.

    Keying (codex rounds 3/5/6/7/8/9 P2 -- this composite key dissolves the whole class):
    the map key is `"<round_n>/<channel>"`. Gate-log rounds are scoped per (arc, producer)
    (`round_n_for`), so a D-C failover's two legs legitimately share a round NUMBER --
    (round, channel) is the stable identity: no cross-channel collision, no renumbering,
    exact joins back to the gate log, and CAS-retry idempotence for free (same key, same
    content). The map stays APPEND-ONLY: a same-key re-record with DIFFERENT content
    raises RoundOutcomeConflict (never a silent overwrite); an identical re-record is
    idempotent. The C-HE-25 `{round_n: ...}` ARC-ROW shape is owed by the drain fold
    (U-HE-19), which projects these keys; the reservation-side carrier shape is plan-level
    (`round_outcomes` is not in the C-HE-03 §3 payload enumeration)."""
    row = _outcome_row(channel, terminal, finding_count)
    if isinstance(round_n, bool) or not isinstance(round_n, int) or round_n < 0:
        # the gate record's round is a nonnegative integer; int() coercion would collapse
        # floats and admit booleans/negatives into keys (codex round-12 P3)
        raise ReservationError(f"round_n must be a nonnegative int, got {round_n!r}")
    key = f"{round_n}/{channel}"

    def build(head: dict) -> dict:
        _refuse_terminal_accretion(arc_id, "record_round_outcome", head)
        outcomes = head.setdefault("round_outcomes", {})
        existing = outcomes.get(key)
        if existing is not None and existing != row:
            raise RoundOutcomeConflict(
                f"{arc_id}: round {key} already recorded "
                f"({existing['channel']}/{existing['terminal']}); the audit map is "
                "append-only (C-HE-25)",
                existing,
            )
        outcomes[key] = dict(row)
        return head

    return _cas_next(arc_id, build)


def fold_round_outcomes(outcomes: dict) -> dict:
    """Project the composite `"<round>/<channel>"` carrier into the C-HE-25 ARC-ROW shape
    `{round_n: {channel, terminal, finding_count}}` -- the committed projection the U-HE-19
    drain fold calls (codex round-10/13 P2). Per round NUMBER the DECIDING leg wins: a D-C
    failover's REVIEWER_UNAVAILABLE leg is superseded by the failover verdict at the same
    number (C-HE-17: the failover verdict blocks); it is kept only when no decided leg
    exists. Nothing is lost: the N6 denominator exclusion travels via
    `phases.verify_unavailable` (C-HE-27 §4), and the full two-leg detail stays durable in
    the reservation history and the gate log. Two DECIDED legs at one number cannot arise
    from the wrapper flow (the failover fires only on REVIEWER_UNAVAILABLE); if present,
    the projection fails loudly rather than drop audit."""
    folded: dict = {}
    for key, row in outcomes.items():
        n = key.split("/", 1)[0]
        prior = folded.get(n)
        if prior is None:
            folded[n] = dict(row)
        elif (
            prior["terminal"] == "REVIEWER_UNAVAILABLE"
            and row["terminal"] != "REVIEWER_UNAVAILABLE"
        ):
            folded[n] = dict(row)
        elif row["terminal"] == "REVIEWER_UNAVAILABLE":
            if prior["terminal"] == "REVIEWER_UNAVAILABLE":
                # both legs unavailable: the FAILOVER leg (written later; dict order is
                # insertion order through the JSON round-trip) is the round's deciding
                # gate (C-HE-17), so its channel attribution stands (codex r18 P3)
                folded[n] = dict(row)
            continue
        else:
            raise ReservationError(
                f"round {n}: two decided legs ({prior['channel']}/{prior['terminal']} vs "
                f"{row['channel']}/{row['terminal']}) cannot fold to one C-HE-25 entry"
            )
    return folded


def holder(arc_id: str) -> str | None:
    cur = current(arc_id)
    return cur[1]["lane_id"] if cur and cur[1]["state"] == "open" else None


def selectable(arc_id: str) -> bool:
    cur = current(arc_id)
    return cur is None


def sibling_open_count(exclude_arc_id: str) -> int:
    root = reservations_root()
    if not root.is_dir():
        return 0
    n = 0
    for d in root.iterdir():
        if d.name.startswith(".") or d.name == exclude_arc_id:
            continue
        try:
            cur = current(d.name)
            if cur and cur[1]["state"] == "open":
                n += 1
        except (ReservationError, OSError, ValueError, KeyError, TypeError):
            # Best-effort snapshot (C-HE-03 §7, `derived`, codex r2 P2 sibling): a corrupt
            # or symlinked sibling is not countable and must not crash the pending->open
            # flip it decorates.
            continue
    return n


def walk_terminal(arc_id: str) -> dict:
    """Follow superseded_by reservation-to-reservation. Repeated arc_id -> cycle (raise);
    depth cap 5."""
    seen: set[str] = set()
    depth = 0
    while True:
        if arc_id in seen:
            raise ChainError(f"superseded_by cycle at {arc_id}")
        seen.add(arc_id)
        cur = current(arc_id)
        if cur is None:
            raise ChainError(f"chain points at missing reservation {arc_id}")
        head = cur[1]
        if head["state"] != "abandoned":
            return head
        depth += 1
        if depth > CHAIN_DEPTH_CAP:
            raise ChainError(f"superseded_by depth > {CHAIN_DEPTH_CAP}")
        arc_id = head["superseded_by"]


def gc(*, now: datetime | None = None) -> list[Path]:
    """Prune gens strictly below the head older than terminal + 30 d; sweep orphaned
    .<gen>.<pid>.tmp (pid dead on this host and > 1 h old). The head is NEVER pruned."""
    now = now or datetime.now(UTC)
    removed: list[Path] = []
    root = reservations_root()
    if not root.is_dir():
        return removed
    resolved_root = root.resolve()
    for d in root.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        if d.is_symlink() or not d.resolve().is_relative_to(resolved_root):
            # Path.is_dir() follows symlinks: a link planted under the shared writable root
            # could make GC read a forged terminal head and unlink files OUTSIDE QUEUE_DIR.
            # GC never traverses a symlink or leaves the resolved root (codex round-7 P2).
            continue
        # Sweep tmps BEFORE the head check: a crash during first-generation publication
        # leaves a directory with only `.1.json.<pid>.tmp` and no head at all — skipping it
        # would orphan that stager forever (codex round-3 P3).
        for tmp in d.glob(".*.tmp"):
            parts = tmp.name.split(".")
            pid = int(parts[-2]) if len(parts) >= 3 and parts[-2].isdigit() else None
            # glob -> stat -> unlink races normal publication (publish_exclusive removes its
            # stager) and concurrent gc processes; a vanished entry is the goal state, never a
            # sweep-aborting error (codex round-1 P2; C-HE-04 §4 vanished-entry doctrine).
            try:
                old = datetime.fromtimestamp(tmp.stat().st_mtime, UTC) < now - timedelta(hours=1)
                if old and (pid is None or not _process_is_alive(pid)):
                    tmp.unlink()
                    removed.append(tmp)
            except FileNotFoundError:
                continue
        cur = current(d.name)
        if cur is None:
            continue
        head_gen, head = cur
        # Retention = terminalization + 30 d (C-HE-03 §1): derived from the TERMINAL head's
        # transitioned_at, never from each historical file's own age (a long-open arc that
        # terminalizes today keeps its history).
        if head["state"] in TERMINAL:
            terminal_at = datetime.strptime(head["transitioned_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
            if now - terminal_at > timedelta(days=GC_KEEP_DAYS):
                for p in d.glob("*.json"):
                    if p.stem.isdigit() and int(p.stem) < head_gen:
                        try:
                            p.unlink()
                        except FileNotFoundError:
                            continue  # a concurrent gc already pruned it: the goal state holds
                        removed.append(p)
    return removed


def emit_loop_row(kind: str, lane_id: str, cause: str, detail: str) -> None:
    """Append a structured row to the SHARED loop_status.md through loop_lib.sh -- one writer
    of the ledger format (C-HE-09 §3, U-HE-29 `loop_log_structured`). RAISES
    LoopStatusWriteError on write failure.

    Landing order (plan §3): `loop_log_structured` ships at U-HE-29 (S4d). Until it lands,
    every call fails CLOSED here (`bash` exits 127 -> LoopStatusWriteError) -- loud by design,
    never a silently dropped operator signal. No U-HE-17 caller invokes this yet; the first
    callers arrive with U-HE-18/U-HE-29."""
    script = (
        "source tools/hooks/lib.sh; source tools/hooks/loop_lib.sh; "
        'loop_log_structured "$1" "$2" "$3" "$4"'
    )
    try:
        proc = subprocess.run(
            ["bash", "-c", script, "_", kind, lane_id, cause, detail],
            cwd=REPO,
            check=False,
            timeout=10,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LoopStatusWriteError(f"loop row not written ({exc})") from exc
    if proc.returncode != 0:
        # An unrecorded DEFERRED-HIL / NOTIFY is a lost operator signal: propagate (Codex
        # round-3 P2). Callers that hold durable state elsewhere (a blocked lease sidecar)
        # still surface this as a hard error to stderr + exit.
        raise LoopStatusWriteError(
            f"loop row not written: {proc.stderr.strip() or 'loop_log_structured failed'}"
        )


def open_with_sensor(arc_id: str, lane_id: str) -> dict:
    """pending -> open at drain start, recording the best-effort sibling-open snapshot
    (C-HE-03 §7: `derived`, never `declared` -- D7/M8)."""
    n = sibling_open_count(arc_id)
    return transition(arc_id, "open", lane_id=lane_id, updates={"concurrent_lanes_at_open": n})


def _aged(ts: str, now: datetime) -> bool:
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    return (now - dt).total_seconds() > STALE_AFTER_S


def _gh_view(pr: int) -> dict:
    """`gh pr view`-backed ground truth (C-HE-03 §5), bounded 30 s. ANY failure raises;
    reconcile() catches it and fails safe to "still open, not reclaimable"."""
    proc = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", "state,mergedAt"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise ReservationError(f"gh pr view {pr} failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def reconcile(
    arc_id: str,
    *,
    gh_view: Callable[[int], dict],
    superseded_by: str | None = None,
    now: datetime | None = None,
) -> str:
    """Staleness by GROUND TRUTH -- HITL, never TTL (C-HE-03 §5, C-HE-20, D8). Returns the
    head state after the pass; a stuck/aged head emits NOTIFY + DEFERRED-HIL (C-HE-20 §1)
    and stays UNCHANGED -- `pending`/`open` leave only by operator RESOLVED-HIL, a
    superseding arc (`superseded_by`), or confirmed ground truth."""
    now = now or datetime.now(UTC)
    cur = current(arc_id)
    if cur is None:
        raise ReservationError(f"{arc_id}: no reservation")
    head = cur[1]
    lane = head["lane_id"]
    if head["state"] in TERMINAL:
        return head["state"]
    if head["state"] == "pending":
        if _aged(head["reserved_at"], now):
            # Durable HITL row FIRST (C-HE-20 §1): emit_loop_row fails closed, so if the
            # informational NOTIFY went first and raised, the recoverable escalation row
            # would never be attempted (codex U-HE-18 r1 P2).
            emit_loop_row(
                "DEFERRED-HIL",
                lane,
                "reservation-stale:HITL-recoverable:pending_aged",
                f"{arc_id} -- aged pending reservation needs operator disposition "
                f"(RESOLVED-HIL or superseding arc)",
            )
            emit_loop_row(
                "NOTIFY",
                lane,
                "reservation-stale:HITL-recoverable:pending_aged",
                f"{arc_id} pending > 24h; state unchanged",
            )
        return "pending"
    # open
    if head["pr"] is None:
        if _aged(head["transitioned_at"], now):
            emit_loop_row(
                "DEFERRED-HIL",
                lane,
                "reservation-stale:HITL-recoverable:open_no_pr",
                f"{arc_id} -- open reservation with no PR needs operator disposition",
            )
            emit_loop_row(
                "NOTIFY",
                lane,
                "reservation-stale:HITL-recoverable:open_no_pr",
                f"{arc_id} open > 24h with no PR; state unchanged",
            )
        return "open"
    try:
        view = gh_view(int(head["pr"]))
    except Exception as exc:  # ANY gh failure fails safe (C-HE-03 §5)
        print(
            f"reservations: gh transient for {arc_id}: {exc}; still open, not reclaimable",
            file=sys.stderr,
        )
        return "open"
    state = (view or {}).get("state")
    if state in ("MERGED", "CLOSED") and (state == "MERGED" or superseded_by):
        to_state = "merged" if state == "MERGED" else "abandoned"
        try:
            transition(
                arc_id,
                to_state,
                lane_id=lane,
                superseded_by=superseded_by if to_state == "abandoned" else None,
                expect={"pr": head["pr"]},
            )
        except IllegalTransition:
            # Lost a race since the ground-truth check (codex U-HE-18 r1 P1/P2): the head
            # terminalized concurrently (another reconcile pass won -- idempotent, return
            # its terminal state), the holder transferred, or `pr` was re-bound. All
            # resolve fail-safe: report the CURRENT head; a live head re-reconciles on
            # the next pass against the new ground truth.
            cur2 = current(arc_id)
            head2 = cur2[1] if cur2 else None
            if head2 is not None and head2["state"] in TERMINAL:
                return head2["state"]
            return "open"
        return to_state
    if state == "CLOSED":
        emit_loop_row(
            "DEFERRED-HIL",
            lane,
            "reservation-stale:HITL-recoverable:closed_no_pointer",
            f"{arc_id} -- PR #{head['pr']} CLOSED without a superseding pointer; "
            f"confirm abandonment",
        )
        return "open"
    if _aged(head["transitioned_at"], now):
        emit_loop_row(
            "DEFERRED-HIL",
            lane,
            "reservation-stale:HITL-recoverable:open_stuck",
            f"{arc_id} -- stuck open reservation; operator disposition needed",
        )
        emit_loop_row(
            "NOTIFY",
            lane,
            "reservation-stale:HITL-recoverable:open_stuck",
            f"{arc_id} open > 24h, PR #{head['pr']} still OPEN; state unchanged",
        )
    return "open"


def reconcile_all(
    *, gh_view: Callable[[int], dict] | None = None, now: datetime | None = None
) -> dict[str, str]:
    """One ground-truth pass over every non-terminal reservation (session start + the merge
    lane). Per-arc fault isolation (C-HE-04 §3 analog): one arc's failure -- e.g. the
    fail-closed emit_loop_row before U-HE-29 lands `loop_log_structured` -- must not abandon
    the remaining pass; it lands in-band as an `ERROR: ...` value and the CLI exits 2."""
    view = gh_view or _gh_view
    out: dict[str, str] = {}
    root = reservations_root()
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        if d.name.startswith(".") or not d.is_dir():
            continue
        try:
            # The head read is inside the guarded region too (codex U-HE-18 r1 P2): one
            # symlinked/corrupt reservation must not abort the pass before later arcs.
            cur = current(d.name)
            if cur is None or cur[1]["state"] in TERMINAL:
                continue
            out[d.name] = reconcile(d.name, gh_view=view, now=now)
        except (ReservationError, OSError, ValueError, KeyError, TypeError) as exc:
            # KeyError/TypeError: a syntactically-valid but schema-malformed head ({} or a
            # non-object) must isolate like any other corrupt reservation (codex r2 P2).
            out[d.name] = f"ERROR: {exc!r}"
    return out


def _write_store_log(result: dict[str, str], rc: int) -> None:
    """Record the pass at <reservations_root>/.reconcile.log -- the durable venue the NEXT
    session-start surfaces until U-HE-29 lands the loop-ledger emitter (codex r2 P2). The
    write is store-owned and O_NOFOLLOW (codex r2 P1): reservations_root() refuses a
    symlinked store, and a planted symlink at the log path itself raises instead of
    truncating an arbitrary file. Overwrite-in-place: one file, last pass wins."""
    path = reservations_root() / ".reconcile.log"
    payload = json.dumps({"ts": now_iso(), "rc": rc, "result": result}, sort_keys=True) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w") as fh:
        fh.write(payload)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="reservations", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reserve")
    r.add_argument("--arc-id", required=True)
    r.add_argument("--lane-id", required=True)
    r.add_argument("--branch", required=True)
    r.add_argument("--arc-type", choices=ARC_TYPES, required=True)
    t = sub.add_parser("transition")
    t.add_argument("--arc-id", required=True)
    t.add_argument("--to", choices=STATES, required=True)
    t.add_argument("--lane-id", required=True)
    t.add_argument("--superseded-by")
    t.add_argument("--set", nargs="*", default=[])
    u = sub.add_parser("update")
    u.add_argument("--arc-id", required=True)
    u.add_argument("--set", nargs="+", required=True)
    ph = sub.add_parser("phase")
    ph.add_argument("--arc-id", required=True)
    ph.add_argument("--phase", choices=PHASES, required=True)
    ph.add_argument("--edge", choices=["start", "end"], required=True)
    ro = sub.add_parser("round")
    ro.add_argument("--arc-id", required=True)
    ro.add_argument("--round", type=int, required=True)
    ro.add_argument("--channel", required=True)
    ro.add_argument(
        "--terminal", choices=["APPROVE", "BLOCK", "REVIEWER_UNAVAILABLE"], required=True
    )
    ro.add_argument("--findings", type=int, default=0)
    s = sub.add_parser("show")
    s.add_argument("--arc-id", required=True)
    h = sub.add_parser("holder")
    h.add_argument("--arc-id", required=True)
    se = sub.add_parser("selectable")
    se.add_argument("--arc-id", required=True)
    sub.add_parser("gc")
    ml = sub.add_parser("mint-lane-id")
    ml.add_argument("--worktree", default=".")
    rc = sub.add_parser("reconcile")
    rc.add_argument("--arc-id", required=True)
    rc.add_argument("--superseded-by")
    ra = sub.add_parser("reconcile-all")
    ra.add_argument("--log-to-store", action="store_true")
    args = p.parse_args(argv)

    def coerce(v: str):
        # JSON where it parses, raw string otherwise: a hex SHA beginning with a digit
        # (`head_sha=4be86e...`) must land as a string, never a JSONDecodeError
        # (codex round-1 P1).
        if v[:1] in '0123456789{["n-':
            try:
                return json.loads(v)
            except ValueError:
                return v
        return v

    def kv(items: list[str]) -> dict:
        return {k: coerce(v) for k, v in (i.split("=", 1) for i in items)}

    try:
        if args.cmd == "reserve":
            out = reserve(
                args.arc_id, lane_id=args.lane_id, branch=args.branch, arc_type=args.arc_type
            )
        elif args.cmd == "transition":
            out = transition(
                args.arc_id,
                args.to,
                lane_id=args.lane_id,
                updates=kv(args.set) or None,
                superseded_by=args.superseded_by,
            )
        elif args.cmd == "update":
            out = update_payload(args.arc_id, kv(args.set))
        elif args.cmd == "phase":
            out = record_phase(args.arc_id, args.phase, args.edge)
        elif args.cmd == "round":
            out = record_round_outcome(
                args.arc_id,
                args.round,
                channel=args.channel,
                terminal=args.terminal,
                finding_count=args.findings,
            )
        elif args.cmd == "show":
            cur = current(args.arc_id)
            out = cur[1] if cur else None
        elif args.cmd == "holder":
            print(holder(args.arc_id) or "")
            return 0
        elif args.cmd == "selectable":
            return 0 if selectable(args.arc_id) else 1
        elif args.cmd == "gc":
            out = [str(x) for x in gc()]
        elif args.cmd == "reconcile":
            out = reconcile(args.arc_id, gh_view=_gh_view, superseded_by=args.superseded_by)
            print(json.dumps(out, sort_keys=True))
            return 0
        elif args.cmd == "reconcile-all":
            out = reconcile_all()
            rc_all = 2 if any(v.startswith("ERROR") for v in out.values()) else 0
            if args.log_to_store:
                try:
                    _write_store_log(out, rc_all)
                except OSError as exc:
                    # a refused/failed store log is a LOST durable signal pre-U-HE-29:
                    # loud + nonzero, never silent (codex r2 P1).
                    print(f"ABORT: store log not written: {exc}", file=sys.stderr)
                    rc_all = 2
            print(json.dumps(out, sort_keys=True))
            return rc_all
        else:
            print(mint_lane_id(Path(args.worktree).resolve()))
            return 0
        print(json.dumps(out, sort_keys=True))
        return 0
    except ReservationError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

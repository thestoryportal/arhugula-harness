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
_STR_FIELDS = frozenset(
    {"head_sha", "base_sha", "attested_merge_tree", "merge_sha", "pilot_run_id"}
)


class ReservationError(RuntimeError):
    """Named, fail-closed. Never swallowed."""


class ReservationHeld(ReservationError):  # noqa: N818 — U-HE-17 plan signature verbatim
    """A pending/open reservation exists: a second lane's selection MUST fail (C-HE-03 §4)."""


class IllegalTransition(ReservationError):  # noqa: N818 — U-HE-17 plan signature verbatim
    """The intended transition is not legal from the (re-read) head state."""


class ChainError(ReservationError):
    """superseded_by chain cycle or depth > CHAIN_DEPTH_CAP."""


class RoundOutcomeConflict(ReservationError):  # noqa: N818 — Conflict IS the condition named
    """The requested round_n is already recorded with different content (append-only map)."""


class LoopStatusWriteError(ReservationError):
    """The shared loop_status.md could not be written -- an operator recovery signal would
    be lost."""


def reservations_root() -> Path:
    return QUEUE_DIR / "reservations"


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_id(name: str, value: str | None) -> None:
    if value is not None and ":" in value:
        raise ReservationError(
            f"{name} must not contain ':' (finding_id/code delimiter): {value!r}"
        )


def mint_lane_id(worktree: Path) -> str:
    host = socket.gethostname().split(".")[0].replace(":", "-")
    return f"{host}-{worktree.name}-{secrets.token_hex(4)}".replace(":", "-")


def _dir(arc_id: str) -> Path:
    # dot-prefixed ids are reserved for infrastructure (`.seq`, `.<gen>.<pid>.tmp` stagers)
    # and are skipped by sibling_open_count/gc -- a reservation there would be invisible to
    # coordination and retention (codex round-2 P3).
    if "/" in arc_id or arc_id in ("", "..") or arc_id.startswith("."):
        raise ReservationError(f"bad arc_id {arc_id!r}")
    return reservations_root() / arc_id


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


def alloc_seq() -> int:
    """Filesystem-derived monotonic counter (never date-sourced, C-HE-03 §3)."""
    d = reservations_root() / ".seq"
    d.mkdir(parents=True, exist_ok=True)
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
    gens = sorted((int(p.stem) for p in d.glob("*.json") if p.stem.isdigit()), reverse=True)
    if not gens:
        return None
    head = gens[0]
    return head, json.loads((d / f"{head}.json").read_text())


def _provenance() -> dict:
    return {"pid": os.getpid(), "host": socket.gethostname(), "reachable_from_state_machine": False}


def _write_gen(arc_id: str, gen: int, payload: dict) -> None:
    d = _dir(arc_id)
    d.mkdir(parents=True, exist_ok=True)
    publish_exclusive(d / f"{gen}.json", json.dumps(payload, sort_keys=True))


def reserve(
    arc_id: str, *, lane_id: str, branch: str, arc_type: str, arc_type_declared_at: str = "open"
) -> dict:
    """(none) -> pending at arc OPEN. Refuses if a pending/open reservation exists
    (selection-time fence)."""
    _check_id("lane_id", lane_id)
    if arc_type_declared_at != "open":
        # reserve() IS the open-time capture point (C-HE-26 §1); a reservation minted with
        # declared_at='close' would contaminate the cohort label downstream (codex round-6 P3).
        raise ReservationError(
            f"arc_type_declared_at must be 'open' at reserve(), got {arc_type_declared_at!r}"
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
        if head["state"] == "open" and head["lane_id"] != lane_id:
            # holder-only: an `open` reservation is terminalized only by the lane that holds
            # it (C-HE-03 §6; Codex round-3 P1). pending->abandoned by a superseding arc has
            # no holder yet and stays open to any lane.
            raise IllegalTransition(
                f"{arc_id}: {head['state']}->{to_state} requires the holder "
                f"({head['lane_id']}), not {lane_id}"
            )
        if superseded_by and current(superseded_by) is None:
            # the chain walks reservation-to-reservation (C-HE-03 §2); committing a pointer
            # at a missing reservation into an IMMUTABLE terminal head would make
            # walk_terminal raise forever with no legal repair transition (codex round-6 P2).
            raise ReservationError(
                f"{arc_id}: superseded_by names a missing reservation {superseded_by!r}; "
                "reserve the superseding arc first (C-HE-03 §2)"
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


def record_phase(arc_id: str, phase: str, edge: str, ts: str | None = None) -> dict:
    if phase not in PHASES or edge not in ("start", "end"):
        raise ReservationError(f"bad phase/edge {phase!r}/{edge!r}")

    def build(head: dict) -> dict:
        _refuse_terminal_accretion(arc_id, "record_phase", head)
        head.setdefault("phases", {}).setdefault(phase, {})[edge] = ts or now_iso()
        return head

    return _cas_next(arc_id, build)


def record_round_outcome(
    arc_id: str, round_n: int, *, channel: str, terminal: str, finding_count: int
) -> dict:
    """C-HE-25 per-round terminal outcome, accreted on the reservation during the open window
    (like phases) and folded into the arc row at drain. `terminal` MUST be one of the
    C-HE-16 §3 triple.

    The map is APPEND-ONLY per round (codex round-3 P2): a conflicting re-record of an
    existing round_n RAISES instead of silently overwriting — a D-C failover leg that erased
    the codex REVIEWER_UNAVAILABLE row would corrupt the durable audit and the C-HE-27 §4
    N6 denominator exclusion. Callers allocate a fresh round_n per recorded outcome; an
    identical re-record is idempotent."""
    if terminal not in ("APPROVE", "BLOCK", "REVIEWER_UNAVAILABLE"):
        raise ReservationError(
            f"terminal must be APPROVE|BLOCK|REVIEWER_UNAVAILABLE, got {terminal!r}"
        )
    row = {"channel": channel, "terminal": terminal, "finding_count": int(finding_count)}

    def build(head: dict) -> dict:
        _refuse_terminal_accretion(arc_id, "record_round_outcome", head)
        outcomes = head.setdefault("round_outcomes", {})
        existing = outcomes.get(str(int(round_n)))
        if existing is not None and existing != row:
            raise RoundOutcomeConflict(
                f"{arc_id}: round {round_n} already recorded "
                f"({existing['channel']}/{existing['terminal']}); the audit map is "
                "append-only — allocate a new round_n (C-HE-25)"
            )
        outcomes[str(int(round_n))] = dict(row)
        return head

    return _cas_next(arc_id, build)


def record_round_outcome_next(
    arc_id: str, *, channel: str, terminal: str, finding_count: int
) -> dict:
    """Record at the smallest unused integer round key — arc-level allocation preserving the
    C-HE-25 map shape. Used when the caller's producer-scoped round number is already taken
    by a DIFFERENT channel: gate-log rounds are per (arc, producer) (`round_n_for`), so a
    D-C failover's two legs can both carry the same number arc-level (codex round-5 P2).
    Allocation happens inside the CAS build, so a lost CAS re-reads and re-allocates."""
    if terminal not in ("APPROVE", "BLOCK", "REVIEWER_UNAVAILABLE"):
        raise ReservationError(
            f"terminal must be APPROVE|BLOCK|REVIEWER_UNAVAILABLE, got {terminal!r}"
        )
    row = {"channel": channel, "terminal": terminal, "finding_count": int(finding_count)}

    def build(head: dict) -> dict:
        _refuse_terminal_accretion(arc_id, "record_round_outcome_next", head)
        outcomes = head.setdefault("round_outcomes", {})
        nxt = max((int(k) for k in outcomes if k.isdigit()), default=0) + 1
        outcomes[str(nxt)] = dict(row)
        return head

    return _cas_next(arc_id, build)


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
        cur = current(d.name)
        if cur and cur[1]["state"] == "open":
            n += 1
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
    for d in root.iterdir():
        if not d.is_dir() or d.name.startswith("."):
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

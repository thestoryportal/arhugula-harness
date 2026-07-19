"""Dispatch-time cancellation carriers — cancel token + job-wide effect fence.

B-48 (U-RT-143; Runtime spec v1.102 §14.8.10.3 — carrier shapes are
implementation discretion, contract terms binding). The THREE mandatory
parts of the cancellation policy ride ONE carrier:

1. **Cooperative CANCEL TOKEN** — consulted by the child driver at every
   step boundary AND at every effect-entry point inside a step (the
   per-attempt retry loop checks it before any new provider/tool/webhook
   attempt; codex round-37).
2. **JOB-WIDE EFFECT FENCE** the token trips — once tripped, no further
   F2/audit writes begin anywhere in the offloaded job (the four post-child
   `_compose_and_persist_audit` persists included).
3. **Bounded JOIN to the fence acknowledgement** — `wait_ack` classifies the
   outcome per the §14.8.10.3 fence-ack contract (codex rounds 10/11/12/40):
   acked + nothing-in-flight-at-trip → effects genuinely unambiguous;
   acked + in-flight-at-trip → `fence_acked_effect_ambiguous` (the operation
   may have completed after the trip — an ack alone proves nothing; worker
   FINISHED, no drain report owed); grace expired unacked →
   `worker_draining_under_fence` (AMBIGUOUS-EFFECTS / PERMANENTLY TERMINAL).

**Cascade through recursive descent.** Descendant executor jobs link the
ancestor's token at construction (``DispatchCancelToken(parent=...)``);
tripping an ancestor fences the whole descent chain — a timed-out child
blocked inside a nested ``SUB_AGENT_DISPATCH`` cannot reach its own next
token check while the grandchild runs as a separate job (§14.8.10.3).

**Why this module is CP-owned.** The token is consulted on BOTH sides of
the package boundary: the CP child driver's step-boundary checks and the CP
fan-out barrier-deadline trip (the §14.8.10.4 parent→job channel), plus the
runtime offload venue / facade / post-child audit sites. `harness-runtime`
imports `harness-cp` freely; the reverse is forbidden — so the carrier homes
CP-side (the `SubAgentChildPausedError` precedent at
`workflow_driver_types.py`), reaching runtime sites via the ambient
``DISPATCH_CANCEL_TOKEN_VAR`` (per-job isolation through the offload's
``contextvars.copy_context()`` carry).
"""

from __future__ import annotations

import threading
from contextvars import ContextVar
from enum import StrEnum
from typing import final

__all__ = [
    "DISPATCH_CANCEL_TOKEN_VAR",
    "DispatchCancelToken",
    "DispatchFenceTrippedSignal",
    "FenceAckOutcome",
]


class FenceAckOutcome(StrEnum):
    """The §14.8.10.3 bounded-join outcomes (two-outcome ack + drain)."""

    ACKED_CLEAN = "acked_clean"
    """Fence acked within the grace AND no effect-bearing operation was in
    flight at trip time (the fence tripped BETWEEN operations) — the
    surfaced `StepDispatchTimeoutError` carries NO drain disposition."""

    ACKED_EFFECT_AMBIGUOUS = "fence_acked_effect_ambiguous"
    """Fence acked within the grace but an effect-bearing operation WAS in
    flight at trip (it may have completed after the trip). AMBIGUOUS-EFFECTS
    / PERMANENTLY TERMINAL exactly like the drain case — but the worker is
    FINISHED, so no drain report is owed (distinct value; codex round-40:
    reusing `worker_draining_under_fence` would falsely report an active
    drain)."""

    UNACKED_DRAINING = "worker_draining_under_fence"
    """Grace expired with the worker still inside a blocking call.
    AMBIGUOUS-EFFECTS / PERMANENTLY TERMINAL: no automatic retry path;
    workflow re-run after drain is an OPERATOR action informed by the drain
    report. Never silent abandonment, never a pretended completion."""


class DispatchFenceTrippedSignal(BaseException):
    """Raised by `check()` / `effect_entry()` when the fence is tripped.

    A `BaseException` (the `HITLPauseRequestedSignal` precedent) so generic
    `except Exception` recovery arms inside the child cannot swallow the
    fence — it must propagate to the job boundary, where the runtime
    discards in-flight step results per the at-most-once effect discipline.
    """


@final
class DispatchCancelToken:
    """Cooperative cancel token + job-wide effect fence + fence-ack carrier.

    Thread-safe: tripped from the parent side (facade timeout / fan-out
    barrier deadline / cascade) while consulted from the worker side (step
    boundaries, effect entries, post-child persists).
    """

    __slots__ = (
        "_ack_deferred_to_job",
        "_ack_event",
        "_children",
        "_effects_in_flight",
        "_inflight_at_trip",
        "_lock",
        "_tripped_event",
    )

    def __init__(self, *, parent: DispatchCancelToken | None = None) -> None:
        self._lock = threading.Lock()
        self._tripped_event = threading.Event()
        self._ack_event = threading.Event()
        self._effects_in_flight = 0
        self._inflight_at_trip = False
        self._ack_deferred_to_job = False
        self._children: list[DispatchCancelToken] = []
        if parent is not None:
            parent._link_child(self)

    # -- cascade --------------------------------------------------------------

    def _link_child(self, child: DispatchCancelToken) -> None:
        with self._lock:
            self._children.append(child)
            already_tripped = self._tripped_event.is_set()
        if already_tripped and child.trip():
            # A late-joining descendant whose own effect was in flight at
            # ITS trip must still mark THIS token ambiguous — see `trip()`'s
            # docstring on why descendant ambiguity bubbles up.
            with self._lock:
                self._inflight_at_trip = True

    def trip(self) -> bool:
        """Trip the fence; cascades through the whole descent chain.

        Atomically records whether an effect-bearing operation was in flight
        at trip time (the fence-ack contract's in-flight flag) — THEN bubbles
        up any descendant's own in-flight-at-trip flag: a grandchild's effect
        landing after ITS trip is exactly as ambiguous to the operator as
        this token's own effect would be, so the top-level `wait_ack()` must
        report ambiguous whenever ANY token in the descent chain does, not
        only when THIS token's own `_effects_in_flight` was nonzero.
        Returns the (possibly bubbled-up) in-flight-at-trip flag so a caller
        cascading from an ancestor can bubble it further.
        """
        with self._lock:
            if self._tripped_event.is_set():
                return self._inflight_at_trip
            self._inflight_at_trip = self._effects_in_flight > 0
            self._tripped_event.set()
            children = tuple(self._children)
        descendant_inflight = False
        for child in children:
            if child.trip():
                descendant_inflight = True
        if descendant_inflight:
            with self._lock:
                self._inflight_at_trip = True
        return self._inflight_at_trip

    # -- consultation (worker side) -------------------------------------------

    @property
    def tripped(self) -> bool:
        return self._tripped_event.is_set()

    def check(self) -> None:
        """Step-boundary / effect-entry consult: raise if the fence is tripped."""
        if self._tripped_event.is_set():
            raise DispatchFenceTrippedSignal

    class _EffectEntry:
        __slots__ = ("_token",)

        def __init__(self, token: DispatchCancelToken) -> None:
            self._token = token

        def __enter__(self) -> None:
            token = self._token
            with token._lock:
                if token._tripped_event.is_set():
                    raise DispatchFenceTrippedSignal
                token._effects_in_flight += 1

        def __exit__(self, *exc_info: object) -> None:
            token = self._token
            with token._lock:
                token._effects_in_flight -= 1

    def effect_entry(self) -> DispatchCancelToken._EffectEntry:
        """Guard an effect-bearing operation (F2/audit write; provider/tool/
        webhook attempt). Entering consults the fence (tripped → no new
        effect begins); while held, the operation counts as in-flight for
        the trip-time flag. The fence cannot abort an operation already
        inside the guard — the honestly-stated limit (§14.8.10.3)."""
        return DispatchCancelToken._EffectEntry(self)

    # -- acknowledgement (job boundary) ---------------------------------------

    def ack(self) -> None:
        """The job acknowledges the fence: it has terminated (no further
        operations will begin). Called at the job boundary's finally."""
        self._ack_event.set()

    def defer_ack_to_job(self) -> None:
        """Transfer ack ownership from the loop-side task to the WORKER job.

        For an OFFLOADED dispatch, cancelling the loop-side task fires the
        task's finally while the worker may still be running — a task-level
        ack there would falsely report the fence drained (the worker can
        still start operations). The offload venue calls this before
        submitting; `ack_from_task` then no-ops and only the worker job's
        own finally acks."""
        with self._lock:
            self._ack_deferred_to_job = True

    def ack_from_task(self) -> None:
        """Ack from the loop-side task's finally — honored only when ack
        ownership was NOT deferred to a worker job (the direct-await path,
        where task completion/cancellation-propagation IS job termination)."""
        with self._lock:
            deferred = self._ack_deferred_to_job
        if not deferred:
            self._ack_event.set()

    def wait_ack(self, *, grace_seconds: float) -> FenceAckOutcome:
        """Bounded join to the fence acknowledgement; never blocks past grace."""
        acked = self._ack_event.wait(timeout=grace_seconds)
        if not acked:
            return FenceAckOutcome.UNACKED_DRAINING
        with self._lock:
            inflight_at_trip = self._inflight_at_trip
        return (
            FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS
            if inflight_at_trip
            else FenceAckOutcome.ACKED_CLEAN
        )


# The ambient per-job token channel. The runtime facade binds a fresh token
# (linked to any ambient ancestor — the cascade) inside the loop-side task;
# the offload's `contextvars.copy_context()` carries it into the worker, so
# the child driver's step boundaries, the retry loop's effect entries, the
# four post-child audit persists, and any NESTED facade dispatch (descent
# link) all read the SAME job token. Per-job isolation comes from the
# per-submission context copy — no cross-run bleed on a shared/daemon loop.
DISPATCH_CANCEL_TOKEN_VAR: ContextVar[DispatchCancelToken | None] = ContextVar(
    "dispatch_cancel_token", default=None
)

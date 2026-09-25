"""B-104 Task 5a F4: run a body only after its claim's ``started`` frame is durable.

The single unit that owns the order for a resumed record: `claim` (which proves admission and
takes the lease), then `mark_started` (which fsyncs the ``started`` frame before returning), then
the body, then one release of the lease on every exit. It is non-invoking: no production path
calls it yet, and stage 5 still binds the always-refusing admission.

[LAW:types-are-the-program] The gateway takes a store, a ref, a typed admission and a
body. It never accepts a `HeldClaim` or `StartedClaim` from its caller: the only started claim in
its scope is the one `mark_started` returns inside this call. The closable claim stays private
to this unit; the body gets only a nonclosable `StartedProof` (how a child's own authority is
built), so the body cannot be reached on a claim that was merely claimed or handed in, and it
cannot release its own lease.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum

from harness_core import JournalRecordRef

from harness_runtime.lifecycle.resume_claim_store import (
    Admission,
    ClaimBusyError,
    ClaimRefusedError,
    ResumeClaimStore,
    StartedProof,
)

__all__ = ["GatewayPhase", "GatewayRefusal", "run_started"]


class GatewayPhase(StrEnum):
    """Which gateway step refused: the claim (admission and lease) or the durable start."""

    CLAIM = "claim"
    START = "start"


class GatewayRefusal(Exception):  # noqa: N818 (a refusal, named for the domain not `Error`)
    """The gateway's two EXPECTED refusals, typed by phase, with the store's error as `cause`.

    [LAW:types-are-the-program] `phase` and the type of `cause` are the closed vocabulary a
    consumer maps from, so no one parses message text: `CLAIM` carries `ClaimRefusedError` or
    `ClaimBusyError`, `START` carries `ClaimRefusedError`. The body has not run in either case.
    Everything else (placement faults, journal-lock timeout, raw `OSError`, body errors) is not a
    refusal and propagates as itself.
    """

    def __init__(self, phase: GatewayPhase, cause: ClaimRefusedError | ClaimBusyError) -> None:
        super().__init__(str(cause))
        self.phase = phase
        self.cause = cause


def run_started[R](
    store: ResumeClaimStore,
    ref: JournalRecordRef,
    admission: Admission,
    body: Callable[[StartedProof], R],
    *,
    deadline_seconds: float | None = None,
) -> R:
    """Claim `ref`, durably start it, run `body(started)`, and release the lease exactly once.

    `started` is the nonclosable proof of the claim this call durably started: the body can read
    its identity and admit children through it, but cannot release the lease (this call alone does).

    A refused or busy claim raises `GatewayRefusal(CLAIM, ...)`; a refused start (including a
    failed `started` write or fsync) raises `GatewayRefusal(START, ...)`. Any other fault and any
    body failure propagate unchanged. The body is never called unless `mark_started` returned, so
    a claim that is only claimed, refused, busy or whose `started` frame is not durable never
    reaches it. The lease is
    held through the whole body and released in `finally` on every exit, including
    `BaseException`; a claim whose body failed stays ``started`` (sticky), never re-runnable.
    """
    try:
        held = store.claim(ref, admission, deadline_seconds=deadline_seconds)
    except (ClaimRefusedError, ClaimBusyError) as exc:
        raise GatewayRefusal(GatewayPhase.CLAIM, exc) from exc
    try:
        # [LAW:no-ambient-temporal-coupling] The order is this statement sequence and nothing else:
        # the started frame is durable before the body is even referenced.
        try:
            started = store.mark_started(held, deadline_seconds=deadline_seconds)
        except ClaimRefusedError as exc:
            raise GatewayRefusal(GatewayPhase.START, exc) from exc
        return body(started.proof())
    finally:
        held.close()

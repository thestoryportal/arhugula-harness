"""B-104 S1: the unbound child admission that claims through a started parent.

`ClaimedChildAdmission` implements the `DurableChildAdmission.run_admitted` seam over the
non-invoking started-body gateway: it claims the verified child under `ParentCarriedAdmission`,
durably starts it, runs the body, and releases the lease once. Its only job beyond that is the
mapping of the gateway's typed refusals to `ChildResumeRefusedError`, by (phase, cause type):

| gateway refusal            | `ChildResumeRefusal` |
| CLAIM, `ClaimRefusedError` | `claim-refused`      |
| CLAIM, `ClaimBusyError`    | `claim-busy`         |
| START, `ClaimRefusedError` | `start-refused`      |

Nothing is parsed from message text; `detail` carries the store's human text only. Any other
fault (placement, journal-lock timeout, raw `OSError`, a body error) is not a refusal and
propagates as itself. It is NOT bound anywhere: stage 5 still binds `RefuseDurableChildAdmission`,
and the parent's `StartedClaim` it takes exists for tests until the Task 5b handoff.
"""

from __future__ import annotations

from collections.abc import Callable

from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError

from harness_runtime.lifecycle.durable_child_admission import VerifiedChildRecord
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimBusyError,
    ClaimRefusedError,
    ParentCarriedAdmission,
    ResumeClaimStore,
    StartedClaim,
)
from harness_runtime.lifecycle.started_body_gateway import (
    GatewayPhase,
    GatewayRefusal,
    run_started,
)

__all__ = ["ClaimedChildAdmission"]


def _reason_of(refusal: GatewayRefusal) -> ChildResumeRefusal | None:
    """The refusal reason for a typed gateway refusal, or `None` for an unmapped combination."""
    match (refusal.phase, refusal.cause):
        case (GatewayPhase.CLAIM, ClaimRefusedError()):
            return ChildResumeRefusal.CLAIM_REFUSED
        case (GatewayPhase.CLAIM, ClaimBusyError()):
            return ChildResumeRefusal.CLAIM_BUSY
        case (GatewayPhase.START, ClaimRefusedError()):
            return ChildResumeRefusal.START_REFUSED
        case _:
            return None


class ClaimedChildAdmission:
    """`DurableChildAdmission` over `run_started` with the parent's started claim (unbound)."""

    def __init__(
        self,
        store: ResumeClaimStore,
        parent: StartedClaim,
        *,
        deadline_seconds: float | None = None,
    ) -> None:
        self._store = store
        self._parent = parent
        self._deadline_seconds = deadline_seconds

    def run_admitted[R](self, verified: VerifiedChildRecord, body: Callable[[], R]) -> R:
        entered = False

        def guarded() -> R:
            nonlocal entered
            entered = True
            return body()

        try:
            return run_started(
                self._store,
                verified.ref,
                ParentCarriedAdmission(self._parent),
                guarded,
                deadline_seconds=self._deadline_seconds,
            )
        except GatewayRefusal as refusal:
            reason = _reason_of(refusal)
            # A refusal raised by the BODY (a nested child's gateway) is the body's, and an
            # unmapped combination is a fault: neither is this child's refusal.
            if entered or reason is None:
                raise
            raise ChildResumeRefusedError(reason, str(refusal.cause)) from refusal

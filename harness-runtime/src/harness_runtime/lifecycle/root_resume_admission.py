"""B-104: a durable root `resume_handle` is claimed and durably started before its body runs.

`api.resume` reads one exact root record before bootstrap and hands its address — the journal
directory it read and the `JournalRecordRef` of that same read — to the in-process
`run_workflow` tool as a `DurableRootResume`. The tool's `asyncio.to_thread` worker calls
`run`, which places that directory under the verified external state root, claims the ref as
the journal's current latest root record, fsyncs ``started`` (`run_started`), and only then
runs the workflow body with a `ClaimedChildAdmission` over the root's `StartedProof` as CP's
`child_resume_authority`. Running in the worker is what makes the lease outlive a drain
timeout: the API may return ``drained`` while the worker still owns the lease, which
`run_started` releases only when the body returns.

A fresh run or a caller-supplied snapshot is `UNCLAIMED`: no claim and no authority, so
stage 5's refusing child admission stays the fallback there.

A refusal before the body — placement, a refused or busy claim, a start that is not durable —
becomes a `ResumeClaimRefusedError` recorded on the request, because typed errors do not
survive the MCP text boundary; `api.resume` raises it. Faults once the body has begun (a
child's own refusal included) propagate as themselves.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final

from harness_core import JournalRecordRef
from harness_cp.workflow_driver_types import ChildResumeAuthority

from harness_runtime.config import state_placement
from harness_runtime.config.state_placement import StateRootPlacementError, place_state_dir
from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimBusyError,
    ClaimRefusedError,
    ResumeClaimStore,
    RootLatestAdmission,
    StartedProof,
)
from harness_runtime.lifecycle.started_body_gateway import (
    GatewayPhase,
    GatewayRefusal,
    run_started,
)

if TYPE_CHECKING:
    from harness_runtime.types import HarnessContext

__all__ = [
    "UNCLAIMED",
    "DurableRootResume",
    "ResumeAdmission",
    "ResumeClaimRefusedError",
    "RootResumeRefusal",
]

type Body[R] = Callable[[ChildResumeAuthority | None], R]
"""The workflow body: CP's `execute_workflow`, given the root's child authority (or none)."""


class RootResumeRefusal(StrEnum):
    """Why a durable root record was not admitted; its body never ran."""

    PLACEMENT = "placement"
    CLAIM_REFUSED = "claim-refused"
    CLAIM_BUSY = "claim-busy"
    START_REFUSED = "start-refused"


class ResumeClaimRefusedError(Exception):
    """`RT-FAIL-RESUME-CLAIM-REFUSED` — the durable root record was not admitted (B-104).

    `reason` is the stable discriminator; the typed refusal it was mapped from (a
    `GatewayRefusal` or `StateRootPlacementError`) is the `__cause__`. The message names the
    reason only, never a path. `claim-busy` is the one retryable reason: another holder is live.
    """

    def __init__(self, reason: RootResumeRefusal) -> None:
        super().__init__(
            f"RT-FAIL-RESUME-CLAIM-REFUSED:{reason.value}: the durable root record was not "
            "admitted and its workflow body did not run (B-104)."
        )
        self.reason: RootResumeRefusal = reason


def _reason_of(refusal: GatewayRefusal | StateRootPlacementError) -> RootResumeRefusal | None:
    """The root refusal for a typed pre-body refusal, or `None` for an unmapped combination."""
    match refusal:
        case StateRootPlacementError():
            return RootResumeRefusal.PLACEMENT
        case GatewayRefusal(phase=GatewayPhase.CLAIM, cause=ClaimRefusedError()):
            return RootResumeRefusal.CLAIM_REFUSED
        case GatewayRefusal(phase=GatewayPhase.CLAIM, cause=ClaimBusyError()):
            return RootResumeRefusal.CLAIM_BUSY
        case GatewayRefusal(phase=GatewayPhase.START, cause=ClaimRefusedError()):
            return RootResumeRefusal.START_REFUSED
        case _:
            return None


class DurableRootResume:
    """The exact root record `api.resume` read, admitted inside the resume worker.

    [LAW:one-source-of-truth] `journal_dir` and `ref` come from ONE pre-bootstrap read and are
    the record's only address: the worker never re-reads the journal or derives a directory,
    and the store re-proves under its journal lock that `ref` is still that directory's latest
    depth-0 record.

    `refusal` has one writer (`run`, before any body) and one reader (`api.resume`, after the
    tool call raised); it stays `None` whenever the body was reached.
    """

    def __init__(self, *, journal_dir: Path, ref: JournalRecordRef) -> None:
        self.journal_dir: Final = journal_dir
        self.ref: Final = ref
        self.refusal: ResumeClaimRefusedError | None = None

    def run[R](self, ctx: HarnessContext, body: Body[R]) -> R:
        """Claim, durably start, run `body` with the root's child authority, release once."""
        entered = False
        try:
            store = ResumeClaimStore(
                placement=place_state_dir(
                    self.journal_dir,
                    ctx.config,
                    ctx.verified_state_root,
                    what="durable resume journal directory",
                    # Looked up at call time: the same verifier stage 1 stamped the root with.
                    filesystem_type=state_placement.linux_filesystem_type,
                ),
                tenant_id=ctx.config.tenant_id,
            )

            def started_body(started: StartedProof) -> R:
                nonlocal entered
                entered = True
                # [LAW:no-ambient-temporal-coupling] Built only once `started` is durable; each
                # carried child claims through it and a grandchild through its child.
                return body(ClaimedChildAdmission(store, started))

            return run_started(store, self.ref, RootLatestAdmission(), started_body)
        except (GatewayRefusal, StateRootPlacementError) as exc:
            reason = None if entered else _reason_of(exc)
            # A refusal raised inside the body is the body's, and an unmapped one is a fault.
            if reason is None:
                raise
            self.refusal = ResumeClaimRefusedError(reason)
            raise self.refusal from exc


class _Unclaimed:
    """A fresh run or caller-supplied snapshot: outside the claim contract, no authority."""

    refusal: Final = None

    def run[R](self, ctx: HarnessContext, body: Body[R]) -> R:
        _ = ctx
        return body(None)


UNCLAIMED: Final = _Unclaimed()

type ResumeAdmission = DurableRootResume | _Unclaimed
"""What the `run_workflow` worker runs its body through; the tool's default is `UNCLAIMED`."""

"""B-104 Task 4c: verify a durable paused child's exact record, then require admission.

Between Task 4c and Task 5 no durable paused child may run. The runner therefore parses a
resume capture into a `VerifiedChildRecord` (the one proof of "this is exactly the journal
record the parent carried, at exactly this depth") and hands it to a REQUIRED admission
step. The only production binding today, `RefuseDurableChildAdmission`, always refuses;
Task 5 replaces it with the parent-carried claim, the fsynced `started` record and the
worker-owned lease behind the same `DurableChildAdmission` seam.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from harness_core import JournalRecordRef
from harness_cp.pause_resume_protocol_types import PausedChildCapture, PauseSnapshot
from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError

from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol

__all__ = [
    "DurableChildAdmission",
    "RefuseDurableChildAdmission",
    "VerifiedChildRecord",
    "verify_durable_child_resume",
]


@dataclass(frozen=True)
class VerifiedChildRecord:
    """A child resume proven to be the exact journal record its parent carried."""

    ref: JournalRecordRef
    snapshot: PauseSnapshot
    depth: int


class DurableChildAdmission(Protocol):
    """The seam between verification and execution of a durable paused child.

    Implementations return only to admit; they raise `ChildResumeRefusedError` otherwise.
    """

    def admit(self, verified: VerifiedChildRecord) -> None: ...


class RefuseDurableChildAdmission:
    """The Task 4c production binding: no claim/started gateway exists yet, so refuse."""

    def admit(self, verified: VerifiedChildRecord) -> None:
        raise ChildResumeRefusedError(
            ChildResumeRefusal.GATEWAY_NOT_INSTALLED,
            f"no claim/started gateway for child record {verified.ref.workflow_id!r}"
            f"#{verified.ref.record_count}",
        )


def verify_durable_child_resume(
    protocol: DurablePauseResumeProtocol, capture: PausedChildCapture, *, descent_depth: int
) -> VerifiedChildRecord:
    """Parse `capture` into a `VerifiedChildRecord` or refuse before anything runs.

    [LAW:parse-dont-validate] The one dedicated unit; downstream code takes the proving
    type. The record is read by its exact position and digest (`read_exact`), never as the
    journal's latest, so same-workflow siblings N and N+1 each verify against their own
    line. Refuses a missing ref (legacy), an unreadable or altered record, a snapshot that
    is not byte-for-byte the journaled one, and any depth other than the child's own.
    """
    ref = capture.child_record_ref
    if ref is None:
        raise ChildResumeRefusedError(
            ChildResumeRefusal.MISSING_REF,
            f"paused child {capture.child_workflow_id!r} carries no journal record ref",
        )
    at_ref = protocol.read_exact(ref)
    if at_ref is None:
        raise ChildResumeRefusedError(
            ChildResumeRefusal.UNREADABLE_RECORD,
            f"no verifiable journal record at {ref.workflow_id!r}#{ref.record_count}",
        )
    if at_ref.snapshot != capture.child_snapshot:
        raise ChildResumeRefusedError(
            ChildResumeRefusal.SNAPSHOT_MISMATCH,
            f"journal record {ref.workflow_id!r}#{ref.record_count} is not the carried snapshot",
        )
    if at_ref.depth != descent_depth:
        raise ChildResumeRefusedError(
            ChildResumeRefusal.DEPTH_MISMATCH,
            f"journal record depth {at_ref.depth!r}, resuming child depth {descent_depth}",
        )
    return VerifiedChildRecord(ref=ref, snapshot=at_ref.snapshot, depth=descent_depth)

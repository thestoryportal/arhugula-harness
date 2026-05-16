"""Pause/resume protocol + state_summary snapshot capture — U-CP-49.

Implements C-CP-22 §22.1 (the pause/resume protocol). Declares the
`PauseReason` enum, the `PauseEvent` record, the `ResumeAttempt` record, the
`ResumeOutcomeKind` enum, the `ResumeOutcome` record, and the two protocol
functions `capture_pause_snapshot` / `attempt_resume`.

The pause protocol captures a `StateSummary` snapshot plus the pause-time
`ExternalReference` set (U-CP-30); the resume protocol reads the snapshot back,
integrity-verifies it via the F2 hash chain, and consumes the U-CP-50
material-diff result to decide a clean resume / revalidated resume / abort.

Material-diff detection delegates to U-CP-50 — this unit consumes the result,
it does not recompute (acceptance #7). `MaterialDiff` is imported from U-CP-50
at runtime; U-CP-50's reciprocal `PauseEvent` reference is `TYPE_CHECKING`-only
(annotation-level), so the U-CP-49 ↔ U-CP-50 plan-declared mutual dependency
does not become a Python import cycle.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2.8 U-CP-49 (preserved
verbatim through v2.9); Spec_Control_Plane_v1_2.md §22 C-CP-22 §22.1;
ADR-D5 v1.3 §1.11.
"""

from __future__ import annotations

from enum import StrEnum

from harness_core import EntryID, WorkflowID
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.handoff_context import ExternalReference, StateSummary
from harness_cp.material_diff_detection import MaterialDiff


class PauseReason(StrEnum):
    """The 4 workflow-pause reasons (C-CP-22 §22.1)."""

    HITL_INVOCATION_PENDING = "hitl-invocation-pending"
    CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE = "cross-deployment-bridging-arc-pause"
    OPERATOR_INITIATED_PAUSE = "operator-initiated-pause"
    ENGINE_NATIVE_PAUSE = "engine-native-pause"
    """event-sourced-replay / reconciler engines."""


class PauseEvent(BaseModel):
    """A workflow-pause event with state snapshot (C-CP-22 §22.1).

    Five fields verbatim per §22.1.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    paused_at: str
    """ISO-8601 pause timestamp."""

    pause_reason: PauseReason
    state_summary_snapshot: StateSummary
    external_refs_captured: tuple[ExternalReference, ...]
    pause_audit_entry_id: EntryID


class ResumeAttempt(BaseModel):
    """A workflow-resume attempt (C-CP-22 §22.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    paused_workflow_id: WorkflowID
    resume_at: str
    """ISO-8601 resume timestamp."""

    resume_request_actor: ActorIdentity


class ResumeOutcomeKind(StrEnum):
    """The 4 resume outcomes (C-CP-22 §22.1)."""

    RESUME_CLEAN = "resume-clean"
    """No material diff; resume immediately."""

    RESUME_AFTER_REVALIDATION = "resume-after-revalidation"
    """Material diff detected; revalidation completed; resume."""

    ABORT_REVALIDATION_FAILED = "abort-revalidation-failed"
    """Material diff detected; revalidation failed; escalate to HITL."""

    ABORT_SNAPSHOT_CORRUPTED = "abort-snapshot-corrupted"
    """Snapshot integrity violated."""


class ResumeOutcome(BaseModel):
    """The outcome of a resume attempt (C-CP-22 §22.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome_kind: ResumeOutcomeKind
    material_diff: tuple[MaterialDiff, ...]
    """The U-CP-50 material-diff set — empty for `RESUME_CLEAN`. (The v2.1
    signature names a singular `Optional<MaterialDiff>`; v2.9 §0.3 re-specifies
    `MaterialDiff` as a per-reference record, so this is the diff-set.)"""

    context_revalidated: bool
    resume_audit_entry_id: EntryID | None


def capture_pause_snapshot(
    workflow_id: WorkflowID, pause_reason: PauseReason
) -> PauseEvent:
    """Capture a pause snapshot for a workflow (C-CP-22 §22.1).

    Captures the `StateSummary` snapshot plus the pause-time
    `ExternalReference` set per the U-CP-30 `ExternalReference.snapshot_capture_at_pause`
    field (acceptance #3); the `pause_audit_entry_id` is written via the U-IS-11
    F2 append with `response_hash = sha256(canonicalize(PauseEvent))`
    (acceptance #4). This is the protocol surface — the concrete F2 append and
    snapshot serialization compose against the IS substrate at integration
    time; the snapshot serialization format is deferred to implementation
    discretion per §22.1 (acceptance #9).
    """
    _ = (workflow_id, pause_reason)
    raise NotImplementedError(
        "capture_pause_snapshot composes the U-IS-11 F2 append + snapshot "
        "serialization; the CP plan U-CP-49 unit declares the pause-protocol "
        "surface (C-CP-22 §22.1)."
    )


def attempt_resume(attempt: ResumeAttempt) -> ResumeOutcome:
    """Attempt to resume a paused workflow (C-CP-22 §22.1).

    Reads the pause snapshot via the U-IS-12 bounded-read keyed on
    `paused_workflow_id` (acceptance #5), integrity-verifies it via the U-IS-09
    `prior_event_hash` chain, then consumes the U-CP-50 material-diff result
    (acceptance #7 — delegated, not recomputed) to select the
    `ResumeOutcomeKind`: a clean resume when the diff-set is empty, a
    revalidated resume when revalidation completes, an abort on revalidation
    failure or snapshot corruption.

    The resume protocol is deterministic given (pause_snapshot, current_state,
    material_diff) — no inference path (acceptance #10).
    """
    _ = attempt
    raise NotImplementedError(
        "attempt_resume composes the U-IS-12 bounded-read + U-IS-09 chain "
        "verification + U-CP-50 material-diff consumption; the CP plan "
        "U-CP-49 unit declares the resume-protocol surface (C-CP-22 §22.1)."
    )


def classify_resume(
    diff: tuple[MaterialDiff, ...], revalidation_succeeded: bool
) -> ResumeOutcomeKind:
    """Classify a resume outcome from the material-diff set (C-CP-22 §22.1).

    Deterministic: an empty diff-set is `RESUME_CLEAN`; a non-empty diff-set
    resumes after revalidation when revalidation succeeds, else aborts. This is
    the pure decision core of `attempt_resume` (acceptance #10).
    """
    if not any(d.is_material for d in diff):
        return ResumeOutcomeKind.RESUME_CLEAN
    if revalidation_succeeded:
        return ResumeOutcomeKind.RESUME_AFTER_REVALIDATION
    return ResumeOutcomeKind.ABORT_REVALIDATION_FAILED

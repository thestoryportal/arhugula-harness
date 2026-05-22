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


# ---------------------------------------------------------------------------
# C-CP-26 PauseResumeProtocol (NEW at CP spec v1.10; renamed identifiers at
# v1.11 per path γ disambiguation). U-CP-63 capture_pause_snapshot landing.
#
# Per CP spec v1.11 §26 NEW NOTE coexistence: this class-method surface
# coexists with the OLD U-CP-49 free-function surface above. They are
# distinct architectural primitives at distinct layers — engine-layer
# replay-pause (above) vs workflow-layer explicit-pause (below).
# ---------------------------------------------------------------------------

import hashlib
import json
from collections.abc import Callable

from harness_cp.pause_resume_protocol_types import (
    MaterialDiffPolicy,
    PauseSnapshot,
    ResumeResult,
    WorkflowPauseReason,
)


# CP fail class identifiers per CP spec v1.11 §26.5.
CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION: str = "CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION"
CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED: str = "CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED"
CP_FAIL_RESUME_OPERATOR_ARBITRATION_OWED: str = "CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED"


PauseContextReader = Callable[[], tuple[StateSummary, str]]
"""Provider returning (current state_summary, current state_ledger_anchor entry_hash).

Impl-discretion FACTOR-OUT for the C-CP-26 PauseResumeProtocol class body.
CP spec v1.11 §26.1 signature is locked at 4 method params; §26.3 enumerates
state_ledger_writer + state_ledger_reader as constructor refs but doesn't
specify how the current state_summary or current entry_hash gets read at
capture-time. The workflow driver — which holds both per its own composition
— supplies a reader callable at stage 5 LOOP_INIT bootstrap. This is the
U-CP-60 precedent pattern (operator-supplied substrate injected at __init__;
internal state held by the framework instance).

The reader returns a tuple to keep the call site atomic — both values are
needed together at every capture; splitting into two readers would risk
inconsistency if the underlying ledger advances between reads.
"""


class PauseResumeProtocol:
    """Concrete C-CP-26 PauseResumeProtocol per CP spec v1.11 §26.1.

    Workflow-layer explicit-pause + material-diff resumption protocol.
    Distinct from the engine-layer C-CP-22 §22.1 surface above (free
    functions `capture_pause_snapshot` / `attempt_resume` / `classify_resume`
    landed at U-CP-49). Per CP spec v1.11 §26 NEW NOTE coexistence: the two
    surfaces coexist as distinct architectural primitives at distinct layers.

    **Constructor refs.** Per §26.3 stage 5 LOOP_INIT instantiation:
    `state_ledger_writer` + `state_ledger_reader` are spec-enumerated. The
    `pause_context_reader` is an impl-discretion FACTOR-OUT (see module-level
    docstring): the workflow driver supplies a callable returning the current
    (state_summary, state_ledger_anchor) tuple — needed at capture-time to
    compose the snapshot_hash + populate the state_ledger_anchor field.

    **AC #1 / U-CP-63 — snapshot_hash composition.** sha256 hex over
    canonical JSON serialization of (workflow_id + run_id + step_index +
    state_summary). Deterministic — equal inputs yield equal hashes.

    **AC #2 / U-CP-63 — immutability.** The returned `PauseSnapshot` is a
    frozen Pydantic v2 model (`model_config = ConfigDict(frozen=True)`).
    §26.6 invariant 1: "Snapshot is immutable once captured. No mutation
    after pause."

    **AC #3 / U-CP-63 — state-ledger anchor.** Populated with the current
    `entry_hash` per C-IS-05 §5 via the pause_context_reader. Material-diff
    detection at U-CP-64 will check reachability from the current entry chain.
    """

    def __init__(
        self,
        *,
        state_ledger_writer: object,
        state_ledger_reader: object,
        pause_context_reader: PauseContextReader,
    ) -> None:
        """Construct with state-ledger refs + pause-context reader callable.

        `state_ledger_writer` / `state_ledger_reader` typed as `object`
        rather than against `LedgerWriterLike` / `LedgerReaderLike` Protocols
        to avoid a CP→CP within-axis circular import at this module (the
        Protocols live at `harness_cp.workflow_driver`). U-CP-64 will narrow
        the type when material-diff detection consumes the reader surface.
        """
        self._state_ledger_writer = state_ledger_writer
        self._state_ledger_reader = state_ledger_reader
        self._pause_context_reader = pause_context_reader

    async def capture_pause_snapshot(
        self,
        workflow_id: str,
        run_id: str,
        step_index: int,
        pause_reason: WorkflowPauseReason,
    ) -> PauseSnapshot:
        """Capture a workflow-layer pause snapshot per CP spec v1.11 §26.1.

        Per §26.6 invariants 1-3:
        1. Snapshot is immutable once captured (frozen Pydantic model).
        2. Resume must validate snapshot_hash (U-CP-64 responsibility).
        3. State-ledger anchor populated from current entry_hash; material
           diff defined as state_ledger_anchor divergence at resume time.
        """
        state_summary, state_ledger_anchor = self._pause_context_reader()
        snapshot_hash = _compute_snapshot_hash(
            workflow_id=workflow_id,
            run_id=run_id,
            step_index=step_index,
            state_summary=state_summary,
        )
        return PauseSnapshot(
            workflow_id=workflow_id,
            run_id=run_id,
            step_index=step_index,
            pause_reason=pause_reason,
            state_summary=state_summary,
            snapshot_hash=snapshot_hash,
            created_at=_now_epoch_ms(),
            state_ledger_anchor=state_ledger_anchor,
        )

    async def attempt_resume(
        self,
        snapshot: PauseSnapshot,
        *,
        material_diff_policy: MaterialDiffPolicy,
    ) -> ResumeResult:
        """Attempt workflow resumption from a pause snapshot per CP spec v1.11 §26.1.

        Per §26.6 invariants 4-5:
        4. Per-pause-reason routing — each WorkflowPauseReason has its own
           resume policy default (operator-configurable at bootstrap per §26.7;
           U-CP-64 does NOT consume the per-reason routing — the caller selects
           `material_diff_policy` based on the routing it wants for this resume).
        5. Coexist with U-CP-56 prefix-replay-based resumption — this method
           handles explicit-pause resumption; U-CP-56 handles prefix-replay.
           The two paths are non-overlapping and operate at different layers.

        AC #1: snapshot_hash validated by recomputing canonical hash; mismatch
               → CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION (snapshot corrupted in transit
               or storage).
        AC #2: material diff = state_ledger_anchor divergence at resume time
               (snapshot's anchor no longer equal to current entry chain head).
               MVP cheap-correct interpretation: anchor equality check. Deeper
               reachability traversal across prior_event_hash chains is impl-
               discretion per §26.7 spirit; can be substituted by a stronger
               predicate via `_anchor_reachable_predicate` override at U-CP-22
               implementation arc when the LedgerReader gains reachability API.
        AC #3: STRICT + diff → CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED (abort).
        AC #4: OPERATOR_ARBITRATE + diff → CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED
               (HITL escalation owed — caller opens the gate; this method emits
               the fail-class marker, the actual gate-open is a future arc
               similar to U-CP-61 validator-escalation→HITL link via span_id).
        """
        # AC #1 — validate snapshot_hash by recomputing canonical hash
        expected_hash = _compute_snapshot_hash(
            workflow_id=snapshot.workflow_id,
            run_id=snapshot.run_id,
            step_index=snapshot.step_index,
            state_summary=snapshot.state_summary,
        )
        if expected_hash != snapshot.snapshot_hash:
            return ResumeResult(
                resumed=False,
                diff_detected=False,
                fail_class=CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION,
            )

        # AC #2 — detect material diff via state_ledger_anchor divergence
        _current_state_summary, current_anchor = self._pause_context_reader()
        diff_detected = self._is_material_diff(snapshot, current_anchor)

        if not diff_detected:
            # Clean resume — no diff, no fail-class
            return ResumeResult(resumed=True, diff_detected=False)

        # Diff detected — compute diff summary hash + branch on policy
        diff_summary_hash = _compute_diff_summary_hash(
            snapshot_anchor=snapshot.state_ledger_anchor,
            current_anchor=current_anchor,
        )

        if material_diff_policy is MaterialDiffPolicy.STRICT:
            # AC #3
            return ResumeResult(
                resumed=False,
                diff_detected=True,
                diff_summary_hash=diff_summary_hash,
                fail_class=CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED,
            )
        if material_diff_policy is MaterialDiffPolicy.OPERATOR_ARBITRATE:
            # AC #4 — HITL arbitration owed; caller opens gate
            return ResumeResult(
                resumed=False,
                diff_detected=True,
                diff_summary_hash=diff_summary_hash,
                fail_class=CP_FAIL_RESUME_OPERATOR_ARBITRATION_OWED,
            )
        # LENIENT — diff permitted; resumption proceeds with diff_detected marker
        return ResumeResult(
            resumed=True,
            diff_detected=True,
            diff_summary_hash=diff_summary_hash,
        )

    def _is_material_diff(self, snapshot: PauseSnapshot, current_anchor: str) -> bool:
        """Material-diff predicate per §26.6 invariant 3.

        MVP: anchor equality check. Snapshot anchor != current anchor → diff.
        Future arc (U-CP-22 implementation) may substitute a chain-reachability
        traversal via the LedgerReader; this method is the predicate seam.
        """
        return snapshot.state_ledger_anchor != current_anchor


def _compute_snapshot_hash(
    *,
    workflow_id: str,
    run_id: str,
    step_index: int,
    state_summary: StateSummary,
) -> str:
    """sha256 hex over canonical JSON of (workflow_id, run_id, step_index, state_summary).

    Mirrors the `canonicalize_brief` / `compute_brief_summary_hash` pattern at
    `harness_cp.sub_agent_brief` — sorted-key JSON, compact separators,
    UTF-8 encoded. Deterministic.
    """
    canonical = {
        "workflow_id": workflow_id,
        "run_id": run_id,
        "step_index": step_index,
        "state_summary": state_summary.model_dump(mode="json"),
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _now_epoch_ms() -> int:
    """Current epoch milliseconds for PauseSnapshot.created_at."""
    import time

    return int(time.time() * 1000)


def _compute_diff_summary_hash(
    *,
    snapshot_anchor: str,
    current_anchor: str,
) -> str:
    """sha256 hex over (snapshot_anchor, current_anchor) for ResumeResult.diff_summary_hash.

    MVP shape per §26.7 deferred-to-implementation-discretion: the spec
    states "diff_summary_hash content shape — sha256 of diff serialization;
    format owed to U-CP-22 implementation arc". U-CP-64 lands an MVP shape
    capturing the two anchors that diverged; U-CP-22 implementation may
    substitute a richer serialization (e.g., enumerating the per-reference
    diff entries from the LedgerReader).
    """
    canonical = {
        "snapshot_anchor": snapshot_anchor,
        "current_anchor": current_anchor,
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()

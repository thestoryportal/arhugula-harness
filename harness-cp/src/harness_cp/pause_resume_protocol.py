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

import hashlib
import json
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from harness_core import EntryID, WorkflowID
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.handoff_context import ExternalReference, StateSummary
from harness_cp.material_diff_detection import MaterialDiff
from harness_cp.pause_resume_protocol_types import (
    MaterialDiffPolicy,
    PauseSnapshot,
    ResumeContext,
    ResumeResult,
    WorkflowPauseReason,
)


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


def capture_pause_snapshot(workflow_id: WorkflowID, pause_reason: PauseReason) -> PauseEvent:
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
        resume_context: ResumeContext | None = None,
    ) -> ResumeResult:
        """Attempt workflow resumption from a pause snapshot per CP spec v1.11 §26.1.

        ``resume_context`` (NEW at CP spec v1.16 §26.8.5; backward-compatible
        default None) is the operator-supplied resume-time context envelope.
        This method INGESTS but does NOT consume the parameter at v1.16 —
        propagation to the resumed-step HITL gate is the runtime-side caller's
        responsibility per CP spec v1.16 §26.8.5 method-body-posture framing.
        Existing callers pass no ``resume_context`` → receive None default →
        identical control flow to pre-v1.16 baseline.

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


# ---------------------------------------------------------------------------
# U-CP-65 — pause.captured + resume.attempted span emission
#
# Per CP spec v1.11 §26.4 + OD spec v1.9 §C-OD-30.1 (Pattern-P1 byte-exact
# alignment): 2 spans, 4 attributes each.
#
# Module-level emit helpers, caller-side invocation (mirrors U-CP-61
# validator.* span emission at workflow_driver post-dispatch hook — keeps
# the PauseResumeProtocol class decoupled from tracer dependencies).
#
# Soft-dep on U-OD-51 per CP plan v2.17 §4 (preserved from v2.15): attribute
# names are runtime-emitted as string literals; OD schema module is NOT
# imported at runtime. Pattern-P1 alignment verified by integration test
# against OD canonical schema (test-time only).
# ---------------------------------------------------------------------------


# §C-OD-30.1 resume.outcome 3-class enum values, plus an MVP 4th value for
# the corruption path not enumerated at OD spec v1.9 §C-OD-30.1. The OD
# enum lists {resumed, diff_aborted, arbitration_owed}; corruption is a CP
# fail class (§26.5) but lacks a matching OD outcome value. Caller convention:
# DO NOT emit resume.attempted span on corruption — corruption is a
# pre-resume validation failure, not a "resume invoked" event per §26.4
# trigger. RESUME_OUTCOME_DIFF_ABORTED / ARBITRATION_OWED / RESUMED are
# the only legal values runtime-emitted; corruption surfaces via fail-class
# on ResumeResult, not via span outcome.
RESUME_OUTCOME_RESUMED: str = "resumed"
RESUME_OUTCOME_DIFF_ABORTED: str = "diff_aborted"
RESUME_OUTCOME_ARBITRATION_OWED: str = "arbitration_owed"


def emit_pause_captured_span(snapshot: PauseSnapshot, *, tracer: Any) -> None:
    """Emit `pause.captured` span with 4 attributes per OD spec v1.9 §C-OD-30.1.

    AC #1: 4 attributes (pause.reason, pause.snapshot_hash, pause.step_index,
    pause.state_ledger_anchor) per §26.4 + §C-OD-30.1.
    AC #3: head=1.0 always-sampled (sampling policy is TracerProvider-level
    configuration; this helper emits unconditionally; sampling enforced by
    the provider).
    AC #4: attribute names byte-exact per OD canonical schema.

    Caller-side invocation per the U-CP-61 pattern: workflow driver invokes
    `protocol.capture_pause_snapshot(...)`, then this helper with the returned
    snapshot + driver-held tracer.
    """
    with tracer.start_as_current_span("pause.captured") as span:
        span.set_attribute("pause.reason", snapshot.pause_reason.value)
        span.set_attribute("pause.snapshot_hash", snapshot.snapshot_hash)
        span.set_attribute("pause.step_index", snapshot.step_index)
        span.set_attribute("pause.state_ledger_anchor", snapshot.state_ledger_anchor)


def emit_resume_attempted_span(
    snapshot: PauseSnapshot,
    result: ResumeResult,
    *,
    tracer: Any,
    diff_policy: MaterialDiffPolicy,
) -> None:
    """Emit `resume.attempted` span with 4 attributes per OD spec v1.9 §C-OD-30.1.

    AC #2: 4 attributes (resume.snapshot_hash, resume.diff_detected,
    resume.diff_policy, resume.outcome) per §26.4 + §C-OD-30.1.
    AC #3: head=1.0 always-sampled (sampling policy TracerProvider-level).
    AC #4: attribute names byte-exact per OD canonical schema.

    Caller convention: DO NOT invoke on corruption path. Per the §C-OD-30.1
    `resume.outcome` enum (resumed / diff_aborted / arbitration_owed),
    corruption has no matching outcome value — corruption is a pre-resume
    validation failure surfaced via ResumeResult.fail_class. Workflow driver
    checks `result.fail_class != CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION` before
    invoking this helper.
    """
    outcome = _derive_resume_outcome(result)
    with tracer.start_as_current_span("resume.attempted") as span:
        span.set_attribute("resume.snapshot_hash", snapshot.snapshot_hash)
        span.set_attribute("resume.diff_detected", result.diff_detected)
        span.set_attribute("resume.diff_policy", diff_policy.value)
        span.set_attribute("resume.outcome", outcome)


def _derive_resume_outcome(result: ResumeResult) -> str:
    """Map ResumeResult to §C-OD-30.1 `resume.outcome` 3-class enum value.

    - fail_class CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED → "diff_aborted"
    - fail_class CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED → "arbitration_owed"
    - else (resumed=True or LENIENT-with-diff) → "resumed"

    Corruption fail-class is NOT enumerated at OD §C-OD-30.1 outcome enum;
    caller-side guard prevents this helper from being invoked on corruption
    paths (see `emit_resume_attempted_span` docstring).
    """
    if result.fail_class == CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED:
        return RESUME_OUTCOME_DIFF_ABORTED
    if result.fail_class == CP_FAIL_RESUME_OPERATOR_ARBITRATION_OWED:
        return RESUME_OUTCOME_ARBITRATION_OWED
    return RESUME_OUTCOME_RESUMED


# Resolve forward-ref `HITLResult` on ResumeContext per CP spec v1.16 §26.8.1.
# The types module guards `HITLResult` under TYPE_CHECKING to avoid the
# hitl_placement → workflow_driver_types → pause_resume_protocol_types cycle;
# this module sits outside that cycle and rebuilds the model so runtime
# validation resolves the field annotation.
from harness_cp.hitl_placement import HITLResult as _HITLResult  # noqa: E402

ResumeContext.model_rebuild(_types_namespace={"HITLResult": _HITLResult})


# --- U-CP-76 §16.5 greenfield composer — CP→IS state-ledger emission -------
#
# `emit_pause_resume_state_ledger_entry` is the §16.5 row U-CP-30 greenfield
# composer producing the IS-anchored state-ledger entry per CP spec v1.26
# §16.5.3 + §16.5.4 + §16.5.5 + §16.5.7 at workflow-layer protocol-class method
# invocations. ZERO CP audit-ledger entry is emitted per §16.5.9 invariant 5
# (greenfield composer). Orthogonal to U-CP-78/U-CP-79 engine-layer free-function
# emissions per CP spec v1.11 §26 NEW NOTE 2-layer coexistence — the two layers
# share `cp.*` action_id namespace but discriminate via distinct action_id
# identifiers (`cp.pause-resume-protocol` here vs `cp.pause-captured` /
# `cp.resume-attempted` at U-CP-78/U-CP-79).

from collections.abc import Awaitable, Mapping  # noqa: E402
from datetime import UTC, datetime  # noqa: E402

from harness_is.state_ledger_entry_schema import (  # noqa: E402
    Actor,
    ActorClass,
    Identifier,
)
from harness_is.state_ledger_write import EntryPayload, WriteResult  # noqa: E402

from harness_cp.state_ledger_canonicalization import (  # noqa: E402
    _canonicalize_outcome_bytes,
)


class PauseResumeProtocolEventKind(StrEnum):
    """Workflow-layer `PauseResumeProtocol` class-method transition discriminator.

    Discriminates `cp.pause-resume-protocol` state-ledger entries by which
    `PauseResumeProtocol` class method fired. Distinct from the engine-layer
    free-function surface (`capture_pause_snapshot` / `attempt_resume` at module
    top) which emits under `cp.pause-captured` / `cp.resume-attempted` per
    U-CP-78/U-CP-79; the two layers coexist per CP spec v1.11 §26 NEW NOTE.
    """

    PAUSE_CAPTURED = "pause-captured"
    """Fired post-`PauseResumeProtocol.capture_pause_snapshot(...)` return."""

    RESUME_ATTEMPTED = "resume-attempted"
    """Fired post-`PauseResumeProtocol.attempt_resume(...)` return (success or fail)."""


_PAUSE_RESUME_ACTION_ID = "cp.pause-resume-protocol"
"""CP spec v1.26 §16.5.3 row U-CP-30 canonical action_id."""

_RECORD_SEPARATOR = b"\x1e"
"""ASCII 0x1E (record-separator) byte — CP spec v1.26 §16.5.4 canonical-form
rule shared across §16.5 composers."""


def _pause_resume_idempotency_key(
    workflow_id: str,
    step_id: str,
    protocol_event_kind: PauseResumeProtocolEventKind,
    event_sequence_id: int,
    outcome_hash_hex: str,
) -> str:
    """Compose the U-CP-30 idempotency-key per CP spec v1.26 §16.5.4 row 3.

    Bytes are the 0x1E-separated 5-tuple `(workflow_id, step_id,
    protocol_event_kind, event_sequence_id, sha256(outcome_canonical_bytes)
    .hex())`; SHA-256-hashed; hex-64 encoded. v1.25 disambiguator segments
    preserved verbatim per Q-β.i-1(a); the outcome-hash suffix carries the
    Q5(a) "hash-over-outcome-bytes" semantic at the dedup-key discriminator.
    """
    segments = [
        workflow_id.encode("utf-8"),
        step_id.encode("utf-8"),
        protocol_event_kind.value.encode("utf-8"),
        str(event_sequence_id).encode("utf-8"),
        outcome_hash_hex.encode("utf-8"),
    ]
    return hashlib.sha256(_RECORD_SEPARATOR.join(segments)).hexdigest()


async def emit_pause_resume_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    protocol_event_kind: PauseResumeProtocolEventKind,
    event_sequence_id: int,
    protocol_state_snapshot: Mapping[str, Any],
    actor: ActorIdentity,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],
) -> WriteResult:
    """Compose + emit the §16.5 IS-anchored state-ledger entry for U-CP-30.

    Per CP spec v1.26 §16.5.3: produces `EntryPayload` per IS HEAD 4-field shape
    `(action_id, idempotency_key, actor, timestamp)`. `response_hash` and
    `prior_event_hash` are IS-internal — composer does NOT control them
    (C-IS-06 §6.2 + C-IS-13 §13.5). The outcome-bytes semantic at §16.5.5 row
    U-CP-30 (protocol-state-transition outcome canonical JSON bytes — the
    protocol state snapshot after the class-level event) is carried at the
    `idempotency_key` discriminator per §16.5.4 + Q-β.i-1(a).

    Fires at workflow-layer protocol-class method invocations per §16.5.7;
    `protocol_event_kind` discriminates the transition. ZERO `CPAuditLedgerEntry`
    is constructed per §16.5.9 invariant 5. Orthogonal to engine-layer free-
    function emissions at U-CP-78/U-CP-79 per CP spec v1.11 §26 NEW NOTE 2-layer
    coexistence (distinct action_id namespaces; this composer emits
    `cp.pause-resume-protocol`; engine-layer emits `cp.pause-captured` /
    `cp.resume-attempted`).

    Composer awaits `ledger_writer(payload)` return per §16.5.9 invariant 4;
    does NOT condition on `WriteResult` variant.
    """
    outcome_canonical_bytes = _canonicalize_outcome_bytes(protocol_state_snapshot)
    outcome_hash_hex = hashlib.sha256(outcome_canonical_bytes).hexdigest()
    idempotency_key = _pause_resume_idempotency_key(
        workflow_id,
        step_id,
        protocol_event_kind,
        event_sequence_id,
        outcome_hash_hex,
    )
    payload = EntryPayload(
        action_id=Identifier(_PAUSE_RESUME_ACTION_ID),
        idempotency_key=Identifier(idempotency_key),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id=str(actor)),
        timestamp=datetime.now(UTC),
        procedural_tier_snapshot_ref=procedural_tier_snapshot_resolver(),
    )
    return await ledger_writer(payload)


# --- U-CP-78 §16.5 greenfield composer — CP→IS state-ledger emission -------
#
# `emit_pause_captured_state_ledger_entry` is the §16.5 row U-CP-49 greenfield
# composer producing the IS-anchored state-ledger entry per CP spec v1.26
# §16.5.3 + §16.5.4 + §16.5.5 + §16.5.7 at the engine-layer free-function
# `capture_pause_snapshot(...)` invocation site (line 106). ZERO CP audit-ledger
# entry is emitted per §16.5.9 invariant 5 (greenfield composer). Orthogonal to
# the workflow-layer U-CP-76 emission at `PauseResumeProtocol` class methods
# per CP spec v1.11 §26 NEW NOTE 2-layer coexistence — engine-layer emits under
# `cp.pause-captured` action_id; workflow-layer emits `cp.pause-resume-protocol`.


_PAUSE_CAPTURED_ACTION_ID = "cp.pause-captured"
"""CP spec v1.26 §16.5.3 row U-CP-49 canonical action_id (engine-layer)."""


def _pause_captured_idempotency_key(
    workflow_id: str,
    step_id: str,
    pause_event_id: str,
    snapshot_hash: str,
    outcome_hash_hex: str,
) -> str:
    """Compose the U-CP-49 idempotency-key per CP spec v1.26 §16.5.4 row 5.

    Bytes are the 0x1E-separated 5-tuple `(workflow_id, step_id, pause_event_id,
    snapshot_hash, sha256(outcome_canonical_bytes).hex())`; SHA-256-hashed;
    hex-64 encoded.

    The `snapshot_hash` segment (position 4) is the pre-computed
    `PauseSnapshot.snapshot_hash` field per `_compute_snapshot_hash` (line 399);
    v1.25 disambiguator preserved verbatim per Q-β.i-1(a). The outcome-hash
    suffix segment (position 5) is INDEPENDENTLY computed via
    `_canonicalize_outcome_bytes` over the full `PauseSnapshot` canonical JSON
    bytes — distinct value from `snapshot_hash` field, distinct semantic per
    Q5(a) "hash-over-outcome-bytes".
    """
    segments = [
        workflow_id.encode("utf-8"),
        step_id.encode("utf-8"),
        pause_event_id.encode("utf-8"),
        snapshot_hash.encode("utf-8"),
        outcome_hash_hex.encode("utf-8"),
    ]
    return hashlib.sha256(_RECORD_SEPARATOR.join(segments)).hexdigest()


async def emit_pause_captured_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    pause_event_id: str,
    pause_snapshot: PauseSnapshot,
    actor: ActorIdentity,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],
) -> WriteResult:
    """Compose + emit the §16.5 IS-anchored state-ledger entry for U-CP-49.

    Per CP spec v1.26 §16.5.3: produces `EntryPayload` per IS HEAD 4-field shape
    `(action_id, idempotency_key, actor, timestamp)`. `response_hash` and
    `prior_event_hash` are IS-internal — composer does NOT control them
    (C-IS-06 §6.2 + C-IS-13 §13.5). The outcome-bytes semantic at §16.5.5 row
    U-CP-49 (`PauseSnapshot` canonical JSON bytes) is carried at the
    `idempotency_key` discriminator per §16.5.4 + Q-β.i-1(a).

    Fires AFTER `capture_pause_snapshot(...)` at line 106 returns the
    `PauseSnapshot` and BEFORE the snapshot returns to the caller per §16.5.7.
    Engine-layer surface; ZERO `CPAuditLedgerEntry` is constructed per §16.5.9
    invariant 5. Orthogonal to U-CP-76 workflow-layer emission per CP spec
    v1.11 §26 NEW NOTE 2-layer coexistence (distinct action_id namespaces;
    this composer emits `cp.pause-captured`; workflow-layer emits
    `cp.pause-resume-protocol`).

    Note: `pause_snapshot.snapshot_hash` (position 4) and the outcome-hash
    suffix (position 5) are DISTINCT — the snapshot_hash field is pre-computed
    at capture time via `_compute_snapshot_hash` over a restricted canonical
    bytes form (`workflow_id` + `run_id` + `step_index` + `state_summary` per
    line 399); the outcome-hash suffix is independently computed over the FULL
    `PauseSnapshot` canonical JSON bytes via `_canonicalize_outcome_bytes`.

    Composer awaits `ledger_writer(payload)` return per §16.5.9 invariant 4;
    does NOT condition on `WriteResult` variant.
    """
    outcome_canonical_bytes = _canonicalize_outcome_bytes(pause_snapshot)
    outcome_hash_hex = hashlib.sha256(outcome_canonical_bytes).hexdigest()
    idempotency_key = _pause_captured_idempotency_key(
        workflow_id,
        step_id,
        pause_event_id,
        pause_snapshot.snapshot_hash,
        outcome_hash_hex,
    )
    payload = EntryPayload(
        action_id=Identifier(_PAUSE_CAPTURED_ACTION_ID),
        idempotency_key=Identifier(idempotency_key),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id=str(actor)),
        timestamp=datetime.now(UTC),
        procedural_tier_snapshot_ref=procedural_tier_snapshot_resolver(),
    )
    return await ledger_writer(payload)


# --- U-CP-79 §16.5 greenfield composer — CP→IS state-ledger emission -------
#
# `emit_resume_attempted_state_ledger_entry` is the §16.5 row U-CP-50 greenfield
# composer producing the IS-anchored state-ledger entry per CP spec v1.26
# §16.5.3 + §16.5.4 + §16.5.5 + §16.5.7 at the engine-layer free-function
# `attempt_resume(...)` invocation site (line 128). Fires at BOTH success and
# failure `ResumeOutcome` resolutions per AC #5 — failure is a recorded outcome
# via `ResumeOutcome.outcome_kind = ABORT_*`, not a swallowed exception. ZERO
# CP audit-ledger entry is emitted per §16.5.9 invariant 5 (greenfield).
# Orthogonal to U-CP-76 workflow-layer per CP spec v1.11 §26 NEW NOTE 2-layer
# coexistence — engine-layer emits `cp.resume-attempted`; workflow-layer emits
# `cp.pause-resume-protocol`.


_RESUME_ATTEMPTED_ACTION_ID = "cp.resume-attempted"
"""CP spec v1.26 §16.5.3 row U-CP-50 canonical action_id (engine-layer)."""


def _resume_attempted_idempotency_key(
    workflow_id: str,
    step_id: str,
    resume_event_id: str,
    resume_attempt_count: int,
    outcome_hash_hex: str,
) -> str:
    """Compose the U-CP-50 idempotency-key per CP spec v1.26 §16.5.4 row 6.

    Bytes are the 0x1E-separated 5-tuple `(workflow_id, step_id,
    resume_event_id, resume_attempt_count, sha256(outcome_canonical_bytes)
    .hex())`; SHA-256-hashed; hex-64 encoded.

    The `resume_attempt_count` segment (position 4) discriminates retry
    attempts at the same `resume_event_id` (v1.25 disambiguator preserved
    verbatim per Q-β.i-1(a)). The outcome-hash suffix segment (position 5) is
    independently computed via `_canonicalize_outcome_bytes` over the
    `ResumeOutcome` canonical JSON bytes per Q5(a) "hash-over-outcome-bytes".
    """
    segments = [
        workflow_id.encode("utf-8"),
        step_id.encode("utf-8"),
        resume_event_id.encode("utf-8"),
        str(resume_attempt_count).encode("utf-8"),
        outcome_hash_hex.encode("utf-8"),
    ]
    return hashlib.sha256(_RECORD_SEPARATOR.join(segments)).hexdigest()


async def emit_resume_attempted_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    resume_event_id: str,
    resume_attempt_count: int,
    resume_outcome: ResumeOutcome,
    actor: ActorIdentity,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],
) -> WriteResult:
    """Compose + emit the §16.5 IS-anchored state-ledger entry for U-CP-50.

    Per CP spec v1.26 §16.5.3: produces `EntryPayload` per IS HEAD 4-field shape
    `(action_id, idempotency_key, actor, timestamp)`. `response_hash` and
    `prior_event_hash` are IS-internal — composer does NOT control them
    (C-IS-06 §6.2 + C-IS-13 §13.5). The outcome-bytes semantic at §16.5.5 row
    U-CP-50 (`ResumeOutcome` canonical JSON bytes — includes `outcome_kind` +
    material_diff + context_revalidated + resume_audit_entry_id per impl line
    91) is carried at the `idempotency_key` discriminator per §16.5.4 +
    Q-β.i-1(a).

    Fires AFTER `attempt_resume(...)` at line 128 resolves the `ResumeOutcome`
    and BEFORE the outcome returns to the caller per §16.5.7. Fires at BOTH
    success outcomes (`RESUME_CLEAN` / `RESUME_AFTER_REVALIDATION`) and failure
    outcomes (`ABORT_REVALIDATION_FAILED` / `ABORT_SNAPSHOT_CORRUPTED`) per
    AC #5 — failure is a recorded outcome via `ResumeOutcome.outcome_kind =
    ABORT_*`, not a swallowed exception.

    Engine-layer surface; ZERO `CPAuditLedgerEntry` is constructed per §16.5.9
    invariant 5. Orthogonal to U-CP-76 workflow-layer emission per CP spec
    v1.11 §26 NEW NOTE 2-layer coexistence (distinct action_id namespaces;
    this composer emits `cp.resume-attempted`; workflow-layer emits
    `cp.pause-resume-protocol`).

    Composer awaits `ledger_writer(payload)` return per §16.5.9 invariant 4;
    does NOT condition on `WriteResult` variant.
    """
    outcome_canonical_bytes = _canonicalize_outcome_bytes(resume_outcome)
    outcome_hash_hex = hashlib.sha256(outcome_canonical_bytes).hexdigest()
    idempotency_key = _resume_attempted_idempotency_key(
        workflow_id,
        step_id,
        resume_event_id,
        resume_attempt_count,
        outcome_hash_hex,
    )
    payload = EntryPayload(
        action_id=Identifier(_RESUME_ATTEMPTED_ACTION_ID),
        idempotency_key=Identifier(idempotency_key),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id=str(actor)),
        timestamp=datetime.now(UTC),
        procedural_tier_snapshot_ref=procedural_tier_snapshot_resolver(),
    )
    return await ledger_writer(payload)

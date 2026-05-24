"""C-CP-26 PauseResumeProtocol type carriers — 2 enums + 2 envelope models.

U-CP-62 — first unit of cluster 10-CP-B. Declares the type carriers that the
C-CP-26 PauseResumeProtocol class body (U-CP-63 capture_pause_snapshot + U-CP-64
attempt_resume) and the pause/resume span emitter (U-CP-65) consume at runtime:

- `WorkflowPauseReason` — 5-class workflow-layer pause taxonomy (CP spec v1.11
  §26.2; renamed from `PauseReason` at v1.11 per path γ disambiguation)
- `MaterialDiffPolicy` — 3-class material-diff resumption policy (STRICT default
  per Decision 2.D7)
- `PauseSnapshot` — 8-field pause-snapshot envelope with state-ledger-anchored
  snapshot-hash
- `ResumeResult` — 5-field resume-attempt outcome envelope

Member string values are cited verbatim from CP spec v1.11 §26.2. `PauseSnapshot`
+ `ResumeResult` use frozen Pydantic v2 models (matching the U-CP-58/U-CP-59
precedent at cluster 10-CP-A; the spec's `@dataclass(frozen=True)` declaration
maps to `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` per repo
discipline).

**Naming note (path γ disambiguation, 2026-05-21).** `WorkflowPauseReason`
(workflow-layer) is distinct from the C-CP-22 §22.1 `PauseReason` (engine-layer
replay-pause taxonomy) homed at `harness_cp.pause_resume_protocol`. The two
enums occupy different architectural layers: C-CP-22 = engine-native pause +
replay-resumption mechanics (U-CP-49 surface); C-CP-26 = workflow-driver
explicit-pause + material-diff resumption mechanics. Per workspace
`.harness/class_1_fork_u_cp_63_pause_reason_collision.md` operator-ratified
path γ + CP spec v1.11 §26 NEW NOTE coexistence.

Authority: CP spec v1.11 §26.2 (NEW C-CP-26 PauseResumeProtocol; path γ
identifier rename absorbed); plan unit U-CP-62 (CP plan v2.17 §1).
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from harness_cp.handoff_context import StateSummary

if TYPE_CHECKING:
    from harness_cp.hitl_placement import HITLResult


class WorkflowPauseReason(StrEnum):
    """The 5-class workflow-layer pause reason (CP spec v1.11 §26.2).

    Distinct from the engine-layer `PauseReason` at C-CP-22 §22.1 / U-CP-49.
    Per CP spec v1.11 §26 NEW NOTE: C-CP-22 anchors at engine-native pause +
    replay-resumption; C-CP-26 anchors at workflow-driver explicit-pause +
    material-diff resumption. The two protocols coexist as distinct
    architectural primitives at distinct layers.
    """

    EXPLICIT_OPERATOR = "explicit_operator"
    """Operator-initiated pause from outside the workflow loop."""

    HITL_PENDING = "hitl_pending"
    """HITL gate opened; workflow paused awaiting operator response."""

    VALIDATOR_ESCALATION = "validator_escalation"
    """Validator framework escalated to HITL; workflow paused for arbitration."""

    TIMEOUT_BOUNDARY = "timeout_boundary"
    """Step or workflow-layer timeout boundary crossed; system-triggered pause."""

    EXTERNAL_DEPENDENCY = "external_dependency"
    """External dependency unavailable (e.g., MCP server, LLM provider);
    system-triggered pause pending dependency recovery."""


class MaterialDiffPolicy(StrEnum):
    """The 3-class material-diff resumption policy (CP spec v1.11 §26.2).

    `STRICT` is the default per Decision 2.D7 RATIFIED — any diff aborts
    resumption. `LENIENT` permits resumption when only non-behavior-changing
    diffs are detected. `OPERATOR_ARBITRATE` escalates any diff to HITL.
    """

    STRICT = "strict"
    """Any diff aborts resumption (DEFAULT per Decision 2.D7)."""

    LENIENT = "lenient"
    """Only behavior-changing diffs abort resumption."""

    OPERATOR_ARBITRATE = "operator_arbitrate"
    """Any diff escalates to HITL for operator arbitration."""


class PauseSnapshot(BaseModel):
    """8-field pause-snapshot envelope (CP spec v1.11 §26.2).

    Captures the pause-point state digest plus the state-ledger anchor and
    a canonical-serialization sha256 snapshot hash. Frozen after capture per
    §26.6 invariant 1; resume must validate `snapshot_hash` per invariant 2.

    The `state_ledger_anchor` carries the C-IS-05 §5 `entry_hash` at the
    pause point; material-diff detection at U-CP-64 checks whether this
    anchor remains reachable from the current entry chain (§26.6 invariant 3).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    """Workflow identifier owning this pause."""

    run_id: str
    """Run identifier owning this pause."""

    step_index: int
    """Step index at which pause was captured."""

    pause_reason: WorkflowPauseReason
    """Why the workflow paused (5-class enum per §26.2)."""

    state_summary: StateSummary
    """Across-turn state digest at pause point (Pattern-D inherited from CP
    plan v2.9 + C-CP-13 §13.4)."""

    snapshot_hash: str
    """sha256 hex string (64 chars) over canonical serialization of
    (workflow_id + run_id + step_index + state_summary)."""

    created_at: int
    """Epoch ms at snapshot capture."""

    state_ledger_anchor: str
    """C-IS-05 §5 `entry_hash` at pause point. Material-diff detection at
    U-CP-64 checks reachability from current entry chain."""


class ResumeResult(BaseModel):
    """5-field resume-attempt outcome envelope (CP spec v1.11 §26.2).

    Reports whether the resumption succeeded, whether a material diff was
    detected, and the optional new `run_id` if resumption required a fresh
    run identifier. `diff_summary_hash` is sha256 of the diff serialization
    (format owed to U-CP-22 implementation arc per §26.7).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    resumed: bool
    """True iff workflow resumed successfully; False on diff-abort, snapshot
    corruption, or arbitration-owed escalation."""

    diff_detected: bool
    """True iff U-CP-64 material-diff detection found a diff."""

    diff_summary_hash: str | None = None
    """sha256 hex of diff-set canonical serialization; None when no diff
    detected. Format owed to U-CP-22 implementation per §26.7."""

    new_run_id: str | None = None
    """Fresh run_id if resumption required one; None when same run_id reused."""

    fail_class: str | None = None
    """CP-FAIL-* class identifier on resume failure; None on clean resume.
    One of CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION, CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED,
    CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED per §26.5."""


class ResumeContext(BaseModel):
    """Operator-supplied resume-time context envelope (CP spec v1.16 §26.8.1).

    Authored at CP spec v1.16 to enable HITL-gate-as-pause-trigger composition
    per runtime spec v1.21 §14.14.7 deferred-discretion residual (i) resolution.
    The envelope carries operator-supplied data the resumed step must consume
    during the resume cycle. v1.16 authors a single field for the durable-async
    HITL response delivery surface; future arcs may extend per v1.16 §26.8.1
    change-note adjacent defect (i).

    Consumed by runtime spec v1.24 §14.8.2 step 4-bis (the HITL gate composer
    body durable-async branch on resumed-step re-entry). The CP-side
    `attempt_resume(...)` method ingests but does NOT consume `ResumeContext`
    per CP spec v1.16 §26.8.5 method-body-posture-at-v1.16 framing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hitl_response: HITLResult | None = None
    """Operator HITL response delivered during durable-async pause.

    None when the pause was not correlated with a HITL gate (e.g.,
    EXPLICIT_OPERATOR, TIMEOUT_BOUNDARY, EXTERNAL_DEPENDENCY pause reasons).
    Populated HITLResult when the pause was triggered by a HITL gate composer
    body firing on durable-async cell synchrony per C-CP-18 §18.1 and the
    operator has delivered a response via the inbound webhook endpoint.
    HITLResult shape canonical at C-CP-17 §17.1.1 (`harness_cp.hitl_placement`).
    """

"""`WorkflowManifestEntry` schema — U-CP-13.

Implements C-CP-06 §6.1 (the workflow-manifest-entry shape). Declares the
`WorkflowManifestEntry` record (10 top-level fields) and the constituent
`StepOverride` record.

`WorkflowManifestEntry` is the canonical per-workflow customization-persistence
shape: it binds a workflow to its workload class, persona tier, engine class,
topology pattern, per-layer routing budgets, cross-family fallback chain, HITL
placements, optional sub-agent briefs, and per-step overrides.

`workload_class` and `persona_tier` are mandatory (no default) per ADR-F1 v1.2
workload-class commitment — validation rejects missing values. `topology_pattern`
admissibility is verified against the U-CP-22 `is_admissible` predicate at
validation time; `engine_class` against the U-CP-16 candidate mapping.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2 U-CP-13 (preserved
verbatim into v2.2/v2.3; v2.5 §0.5 + v2.6 §0.11 dependency-edge deltas —
`[U-CP-00]` for `WorkloadClass`, `[U-CORE-01]` for `StepID`, `[U-CP-00c]` for
`ModelBinding`, `[U-CP-30]` for `HandoffContext`-family substrate);
Spec_Control_Plane_v1_2.md §6 C-CP-06 §6.1 (preserved verbatim into v1.3);
ADR-F1 v1.2 §Decision workload-class commitment; ADR-F3 v1.1.
"""

from __future__ import annotations

from harness_core import PersonaTier, StepID, WorkloadClass
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import FallbackChain
from harness_cp.engine_class import EngineClass
from harness_cp.hitl_placement import HITLPlacement
from harness_cp.layer_budget import LayerBudget
from harness_cp.sub_agent_brief import SubAgentBrief
from harness_cp.topology_pattern import TopologyPattern


class StepOverride(BaseModel):
    """A per-step override of manifest-entry defaults (C-CP-06 §6.1).

    Populated for pipeline-automation per-stage customization. Each field is
    optional — an absent field inherits the manifest-entry default. The
    override is applied field-by-field by the U-CP-14 per-step override
    evaluator (`resolve_step_binding`).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: StepID
    model_binding: ModelBinding | None = None
    engine_class: EngineClass | None = None
    hitl_placement: HITLPlacement | None = None


class WorkflowManifestEntry(BaseModel):
    """The workflow-manifest-entry shape — canonical per-workflow customization.

    Exactly ten top-level fields per C-CP-06 §6.1 verbatim. `workload_class`
    and `persona_tier` are mandatory (no default) per ADR-F1 v1.2; the absence
    of a default means Pydantic validation rejects a missing value.
    `topology_pattern` admissibility is verified against the U-CP-22
    `is_admissible` predicate at validation time; `engine_class` against the
    U-CP-16 candidate mapping. `hitl_placements` is ordered by placement-kind
    precedence per the U-CP-38 `HITLPlacement` schema.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    workload_class: WorkloadClass
    """Mandatory — no default (ADR-F1 v1.2 workload-class commitment)."""

    persona_tier: PersonaTier
    """Mandatory — no default (ADR-F1 v1.2 workload-class commitment)."""

    engine_class: EngineClass
    topology_pattern: TopologyPattern
    layer_budgets: tuple[LayerBudget, ...]
    """Per-layer routing-budget overrides."""

    fallback_chain: FallbackChain
    """Overrides for the cross-family fallback chain."""

    hitl_placements: tuple[HITLPlacement, ...]
    """Declared per workflow per C-CP-17 §17.3."""

    sub_agent_briefs: tuple[SubAgentBrief, ...] | None = None
    """For fan-out patterns."""

    per_step_overrides: dict[StepID, StepOverride]
    """Populated for pipeline-automation per-stage customization."""

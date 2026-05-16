"""3-placement HITL enum + `hitl_gate` signature + `HITLPlacement` schema — U-CP-38.

Implements C-CP-17 §17.1 (the closed 3-placement enumeration), §17.1.1 (the
`hitl_gate(...)` topology-primitive interface signature + `HITLResult` return
shape), and §17.3 (the `HITLPlacement` workflow-definition-surface schema).

Declares the closed 3-value `HITLPlacementKind` enum, the per-placement
`HITLPlacementTrigger` table (`HITL_PLACEMENT_TRIGGERS`, 3 entries), the
`HITLResult` 6-field result record, the `hitl_gate` 5-parameter interface
signature, and the `HITLPlacement` 4-field workflow-definition schema.

`hitl_gate` is an **interface signature** — its body is a `NotImplementedError`
stub. C-CP-17 §17.1.1 commits the signature shape; the runtime gate-delivery
mechanism (cell synchrony, durable-async signal-and-wait) is composed by later
HITL units (U-CP-39 rewriting, U-CP-52 timeout-degradation). This unit declares
the contract surface only.

`ToolName` (the `HITLPlacement.tool_filter` element type) is the AS-owned
tool-name concept; no `ToolName` NewType is landed in `harness_as` — the spec
treats tool names as plain strings, so the element type is `str` (a faithful
materialization, consistent with the U-CP-04 `retry_policies` key precedent).
`Duration` (the `timeout` field) is rendered as `int | None` — a millisecond
wall-clock budget; `None` for sync-blocking, bounded for durable-async per
C-CP-21 §21.3. The concrete `Duration` value type is deferred per spec §17.3.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2 U-CP-38 (preserved
verbatim — symbolic-only enum references at v2.2/v2.3/v2.4);
Spec_Control_Plane_v1_2.md §17 C-CP-17 §17.1 + §17.1.1 + §17.3 (preserved
verbatim into v1.3); ADR-D5 v1.3 §1.3 + §1.3.1.
"""

from __future__ import annotations

from enum import StrEnum

from harness_core.identity import EntryID
from pydantic import BaseModel, ConfigDict

from harness_cp.handoff_context import HandoffContext, ProposedAction
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.topology_pattern import CascadePolicy


class HITLPlacementKind(StrEnum):
    """The closed 3-value HITL placement enumeration (C-CP-17 §17.1).

    The placement set is **closed** at D5 per ADR-D5 v1.3 §1.3; extension is a
    Workflow §4.1.2 Class-2 D5 revision. Member string values are the §17.1
    "Placement" column verbatim.
    """

    PRE_ACTION = "pre-action"
    """Before any tool call where `_hitl_required` is true (C-CP-17 §17.1)."""

    SUB_AGENT_BOUNDARY = "sub-agent-boundary"
    """At parent-child handoff (HandoffContext serialization point)."""

    VALIDATOR_ESCALATION = "validator-escalation"
    """After retry-budget exhaustion (3rd validator fail)."""


class HITLPlacementTrigger(BaseModel):
    """A per-placement trigger row of the C-CP-17 §17.1 table."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    placement_kind: HITLPlacementKind
    trigger_summary: str
    """The §17.1 "Trigger" column verbatim."""

    cell_applicability_qualifier: str
    """The §17.1 "Cell applicability" column verbatim."""


#: The C-CP-17 §17.1 three-placement trigger table — exactly 3 entries.
#: Closed at cardinality 3; extension is a Workflow §4.1.2 Class-2 D5 revision.
HITL_PLACEMENT_TRIGGERS: tuple[HITLPlacementTrigger, ...] = (
    HITLPlacementTrigger(
        placement_kind=HITLPlacementKind.PRE_ACTION,
        trigger_summary=(
            "Before any tool call where _hitl_required(tool, server, "
            "persona_tier) == true per C-CP-19 §19.1 composition"
        ),
        cell_applicability_qualifier="All cells of C-CP-18 matrix",
    ),
    HITLPlacementTrigger(
        placement_kind=HITLPlacementKind.SUB_AGENT_BOUNDARY,
        trigger_summary=(
            "At parent-child handoff per Cluster 4 §2.4.4 [HIGH] "
            "(HandoffContext serialization point per C-CP-13 §13.1)"
        ),
        cell_applicability_qualifier=(
            "All cells; sub-agent interrupt stranding mitigated via "
            "cascade-timeout per C-CP-21 §21.3"
        ),
    ),
    HITLPlacementTrigger(
        placement_kind=HITLPlacementKind.VALIDATOR_ESCALATION,
        trigger_summary=(
            "After retry-budget exhaustion (3rd validator fail per "
            "Cluster 4 §2.2.3 [HIGH])"
        ),
        cell_applicability_qualifier="All cells",
    ),
)


class HITLResult(BaseModel):
    """The result of a `hitl_gate(...)` invocation (C-CP-17 §17.1.1).

    Six fields verbatim. `edited_proposal` is populated only when
    `response == HITLResponse.EDIT`; `response_text` only when
    `response == HITLResponse.RESPOND`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    response: HITLResponse
    edited_proposal: ProposedAction | None = None
    """Populated only when `response == HITLResponse.EDIT`."""

    response_text: str | None = None
    """Populated only when `response == HITLResponse.RESPOND`."""

    timestamp: str
    """ISO-8601 timestamp."""

    audit_ledger_entry_id: EntryID
    """Per C-CP-20 §20.1 entry shape."""

    response_summary_hash: str
    """SHA-256 hex-64 over the canonicalized response payload."""


class HITLPlacement(BaseModel):
    """A workflow-definition HITL placement declaration (C-CP-17 §17.3).

    Four fields verbatim. Multiple placements per workflow are admitted. The
    `tool_filter` glob/regex semantics are deferred to implementation
    discretion per §17.3.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    position: HITLPlacementKind
    tool_filter: tuple[str, ...] | None = None
    """`pre-action` — limits which tools trigger the gate. Element type is
    `str` (AS-owned tool name); no AS `ToolName` NewType is landed."""

    cascade_policy: CascadePolicy | None = None
    """Overrides the workload-class default per C-CP-11 §11.1."""

    timeout: int | None = None
    """Overrides the cell synchrony-class default; millisecond wall-clock
    budget. `Duration` rendered as `int`; concrete type deferred per §17.3."""


def hitl_gate(
    placement: HITLPlacementKind,
    handoff_context: HandoffContext,
    response_palette: set[HITLResponse],
    timeout: int | None,
    cascade_policy: CascadePolicy,
) -> HITLResult:
    """The HITL topology-primitive interface signature (C-CP-17 §17.1.1).

    Five parameters verbatim; returns `HITLResult` (6 fields). `response_palette`
    is a `Set[HITLResponse]` (NOT a `List`) — the palette is a set per the
    U-CP-48 restriction rule. `timeout` is `None` for sync-blocking cells and
    bounded for durable-async cells per C-CP-21 §21.3.

    This is an **interface signature**. The concrete gate-delivery mechanism
    (cell synchrony, durable-async signal-and-wait) is composed by U-CP-39
    (HITL-as-tool-call rewriting) and U-CP-52 (timeout-degradation). C-CP-17
    §17.1.1 commits the signature shape only; this unit declares the contract
    surface.
    """
    raise NotImplementedError(
        "hitl_gate is an interface signature (C-CP-17 §17.1.1); the "
        "gate-delivery mechanism is composed by U-CP-39 / U-CP-52."
    )

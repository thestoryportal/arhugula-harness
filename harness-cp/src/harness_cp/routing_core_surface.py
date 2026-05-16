"""Thin routing core surface — `infer` entry-point — U-CP-03.

Implements C-CP-01 §1.1 (the thin routing core API surface). Declares the
`InferenceRequest` API envelope, the `InferenceResponse` record, and `infer` —
the single LLM-inference entry-point at the CP layer.

`infer` is the **probabilistic core** of the deterministic outer harness per
ADD §5.3.3: everything around it (chain-advancement, cascade-enforcement,
retry, breaker, HITL) is deterministic; `infer` is the one probabilistic
boundary. It orchestrates layered routing -> provider dispatch -> response
materialization. Routing-strategy resolution delegates to U-CP-05; provider
dispatch delegates to provider SDK adapters (out of scope at the CP plan; the
AS plan declares the MCP server SDK boundaries).

Note on `InferenceRequest`: this is the C-CP-01 §1.1 *API envelope* — a
6-field record carrying the routing-discriminator fields plus the
provider-agnostic payload. It is distinct from the module-local
`type InferenceRequest = ProviderAgnosticPayload` aliases at
`fall_through_procedure.py` / `layered_routing_strategy.py`, which name the
*inner* routing-call payload surface per Implementation Plan v2.9 §0.1 item 3
(the §0.1 unification is scoped to "U-CP-05/08 routing-call signature
positions" — it does NOT revise the U-CP-03 body).

Authority: Implementation_Plan_Control_Plane_v2_1.md §2 U-CP-03 (preserved
verbatim through v2.9 — v2.9 is a multi-body delta that does not touch U-CP-03);
Spec_Control_Plane_v1_2.md §1 C-CP-01 §1.1; Architectural_Design_Document_v1_3.md
§5.3.3.
"""

from __future__ import annotations

from harness_core import PersonaTier, WorkloadClass
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import (
    AgentRole,
    ProviderAgnosticPayload,
    RoutingDecisionTrace,
    TraceContext,
)


class InferenceRequest(BaseModel):
    """The C-CP-01 §1.1 inference-request API envelope.

    Carries the routing-discriminator fields (`agent_role`, `workload_class`,
    `persona_tier`) consumed by the layered-routing-strategy per C-CP-02 §2.1,
    the context-token count, the provider-agnostic request payload, and the
    trace context for `routing.*` span attribution.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    agent_role: AgentRole
    workload_class: WorkloadClass
    persona_tier: PersonaTier
    context_tokens: int
    request_payload: ProviderAgnosticPayload
    trace_context: TraceContext
    """For `routing.*` span attribution (U-CP-01)."""


class InferenceResponse(BaseModel):
    """The C-CP-01 §1.1 inference-response record.

    `routing_decision` is populated by U-CP-05 at routing-time and carries the
    routing layer + candidate + decision latency.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider_used: str
    model_used: str
    routing_decision: RoutingDecisionTrace
    """layer + candidate + decision_ms — populated by U-CP-05 at routing-time."""

    response_payload: ProviderAgnosticPayload
    tokens_in: int
    tokens_out: int
    cached_tokens_in: int


def infer(request: InferenceRequest) -> InferenceResponse:
    """The thin routing core surface — the single LLM-inference entry-point.

    All downstream LLM calls at the CP layer flow through this surface
    (acceptance #1). `infer` orchestrates layered routing -> provider dispatch
    -> response materialization: the routing strategy delegates to U-CP-05 and
    provider dispatch delegates to the provider SDK adapters (out of scope at
    the CP plan).

    `infer` is the probabilistic core of the deterministic outer harness per
    ADD §5.3.3 (acceptance #4). The CP plan declares the surface; the
    end-to-end orchestration (U-CP-05 routing strategy + AS-plan provider
    dispatch) composes against it at integration time.
    """
    raise NotImplementedError(
        "infer orchestration composes U-CP-05 routing-strategy resolution with "
        "the AS-plan provider SDK dispatch boundary; the CP plan U-CP-03 unit "
        "declares the thin core surface only (C-CP-01 §1.1)."
    )

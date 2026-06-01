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

from collections.abc import Awaitable, Callable, Mapping

from harness_core import PersonaTier, WorkloadClass
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import (
    AgentRole,
    ProviderAgnosticPayload,
    RoutingDecisionTrace,
    TraceContext,
)
from harness_cp.layer_budget import DEFAULT_LAYER_BUDGETS, LayerBudget
from harness_cp.layered_routing_strategy import LayerDecisionFn, route
from harness_cp.routing_layer import RoutingLayer
from harness_cp.routing_manifest_residence import RoutingManifest


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


class ProviderDispatchResult(BaseModel):
    """The materialization inputs returned by the injected provider-dispatch
    callable (R-300 activation).

    `infer` composes the layered routing decision (`route` per U-CP-05) with a
    provider-dispatch callable injected by the caller. Provider dispatch is
    "out of scope at the CP plan" (C-CP-01 §1.1 "deferred to implementation
    discretion: ... specific provider-adapter binding library"); the runtime
    composes its provider-SDK closure and hands the post-call materialization
    inputs back through this record so `infer` can assemble the
    `InferenceResponse`. CP-pure: no harness-runtime import — the callable is a
    closure, not a dependency.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    response_payload: ProviderAgnosticPayload
    tokens_in: int
    tokens_out: int
    cached_tokens_in: int


# The injected provider-dispatch callable. Given the routing-selected
# `provider` + `model`, the request payload, and the routing trace (for
# `routing.*` span attribution on the caller's `llm.inference` span), it
# performs the provider SDK call and returns the materialization inputs.
# Async per the asyncio concurrency commitment (Target Stack §5.1) — the
# runtime provider-SDK boundary is async; `infer` awaits it.
type ProviderDispatchFn = Callable[
    [str, str, ProviderAgnosticPayload, RoutingDecisionTrace],
    Awaitable[ProviderDispatchResult],
]


class RoutingCandidateUnresolvedError(RuntimeError):
    """No routing layer produced a candidate (final fall-through with empty
    candidate), or the candidate is not a well-formed ``"provider:model"``
    string. Surfaced by `infer` after `route` per U-CP-05."""


async def infer(
    request: InferenceRequest,
    *,
    dispatch: ProviderDispatchFn,
    manifest: RoutingManifest,
    layer_decisions: Mapping[RoutingLayer, LayerDecisionFn],
    budgets: tuple[LayerBudget, ...] = DEFAULT_LAYER_BUDGETS,
    budget_exhausted: frozenset[RoutingLayer] = frozenset(),
) -> InferenceResponse:
    """The thin routing core surface — the single LLM-inference entry-point.

    All downstream LLM calls at the CP layer flow through this surface
    (acceptance #1). `infer` orchestrates layered routing -> provider dispatch
    -> response materialization: the routing strategy delegates to U-CP-05
    (`route`) and provider dispatch delegates to the injected `dispatch`
    callable (the provider SDK adapters are out of scope at the CP plan per
    C-CP-01 §1.1; the runtime composes its provider-SDK closure here).

    `infer` is the probabilistic core of the deterministic outer harness per
    ADD §5.3.3 (acceptance #4): everything around it (chain-advancement,
    cascade-enforcement, retry, breaker, HITL) is deterministic.

    R-300 activation (2026-06-01): the v1.6-era `NotImplementedError` stub is
    lifted. `infer`:
      1. routes the inner payload through the layered strategy (`route` per
         U-CP-05) -> `RoutingDecisionTrace` (`routing_decision`, acceptance
         #3); the DECLARATIVE manifest layer carries `layer == "manifest"`
         (`RoutingLayer.DECLARATIVE.value`);
      2. parses the selected ``"provider:model"`` candidate;
      3. invokes the injected `dispatch` callable with the routed
         provider/model + the routing trace;
      4. materializes the `InferenceResponse`.

    Per-layer time budgets are bound per C-CP-03 (`budgets`, default
    `DEFAULT_LAYER_BUDGETS`).

    Raises
    ------
    RoutingCandidateUnresolvedError
        No layer produced a candidate, or the candidate is malformed.
    """
    trace = route(
        request.request_payload,
        manifest,
        dict(layer_decisions),
        budgets,
        budget_exhausted=budget_exhausted,
    )
    provider, sep, model = trace.candidate.partition(":")
    if not sep or not provider or not model:
        raise RoutingCandidateUnresolvedError(
            f"routing produced no well-formed 'provider:model' candidate "
            f"(layer={trace.layer!r}, candidate={trace.candidate!r})"
        )
    result = await dispatch(provider, model, request.request_payload, trace)
    return InferenceResponse(
        provider_used=provider,
        model_used=model,
        routing_decision=trace,
        response_payload=result.response_payload,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        cached_tokens_in=result.cached_tokens_in,
    )

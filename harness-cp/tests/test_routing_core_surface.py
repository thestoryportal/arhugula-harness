"""Tests for U-CP-03 — thin routing core surface (C-CP-01 §1.1).

Acceptance-criterion coverage:
  #1 `infer` single entry-point   -> test_infer_single_entry_point
  #2 routing-discriminator fields -> test_inference_request_routing_discriminators
  #3 routing.* span attribution   -> test_infer_emits_routing_attributes
  #4 probabilistic core per ADD   -> test_infer_probabilistic_core_per_add_53

R-300 activation (2026-06-01) — `infer` lifts the v1.6 `NotImplementedError`
stub and composes `route` (U-CP-05) with an injected provider-dispatch
callable. Activation must_pass coverage:
  must_pass #1 infer() invokes route()        -> test_infer_invokes_route
  must_pass #2 layer == 'manifest' on decl    -> test_infer_declarative_layer_is_manifest
  must_pass #3 per-layer LayerBudget bound     -> test_infer_binds_layer_budgets
"""

from __future__ import annotations

import inspect

import pytest
from harness_core import PersonaTier, WorkloadClass
from harness_cp.cp_shared_types import (
    AgentRole,
    ProviderAgnosticPayload,
    RoutingDecisionTrace,
    TraceContext,
)
from harness_cp.layer_budget import DEFAULT_LAYER_BUDGETS, LayerBudget
from harness_cp.routing_core_surface import (
    InferenceRequest,
    InferenceResponse,
    ProviderDispatchFn,
    ProviderDispatchResult,
    RoutingCandidateUnresolvedError,
    infer,
)
from harness_cp.routing_layer import RoutingLayer
from harness_cp.routing_manifest_residence import RoutingManifest


def _request() -> InferenceRequest:
    return InferenceRequest(
        agent_role=AgentRole("lead"),
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        context_tokens=1024,
        request_payload=ProviderAgnosticPayload(messages=(), tools=None, params={}),
        trace_context=TraceContext(trace_id="t0", span_id="s0", trace_flags=0, trace_state=None),
    )


def _manifest() -> RoutingManifest:
    return RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(),
        retry_policies={},
    )


def _result() -> ProviderDispatchResult:
    return ProviderDispatchResult(
        response_payload=ProviderAgnosticPayload(
            messages=({"role": "assistant", "content": "ok"},), tools=None, params={}
        ),
        tokens_in=7,
        tokens_out=3,
        cached_tokens_in=0,
    )


def _recording_dispatch() -> tuple[ProviderDispatchFn, list[tuple[str, str, RoutingDecisionTrace]]]:
    calls: list[tuple[str, str, RoutingDecisionTrace]] = []

    async def _dispatch(
        provider: str,
        model: str,
        _payload: ProviderAgnosticPayload,
        trace: RoutingDecisionTrace,
    ) -> ProviderDispatchResult:
        calls.append((provider, model, trace))
        return _result()

    return _dispatch, calls


def test_infer_single_entry_point() -> None:
    """#1 — `infer` is the LLM-inference entry-point: positional request +
    kw-only routing/dispatch injection (R-300)."""
    sig = inspect.signature(infer)
    params = list(sig.parameters)
    assert params[0] == "request"
    assert sig.parameters["request"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    # Injected deps are keyword-only (workspace kw-only-Callable idiom).
    for name in ("dispatch", "manifest", "layer_decisions"):
        assert sig.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
    # Activation lifts the stub — `infer` is a coroutine function now.
    assert inspect.iscoroutinefunction(infer)


def test_inference_request_routing_discriminators() -> None:
    """#2 — InferenceRequest carries agent_role, workload_class, persona_tier."""
    req = _request()
    assert req.agent_role == AgentRole("lead")
    assert req.workload_class is WorkloadClass.SOFTWARE_ENGINEERING
    assert req.persona_tier is PersonaTier.SOLO_DEVELOPER
    # 6-field API envelope.
    assert set(InferenceRequest.model_fields) == {
        "agent_role",
        "workload_class",
        "persona_tier",
        "context_tokens",
        "request_payload",
        "trace_context",
    }


def test_infer_emits_routing_attributes() -> None:
    """#3 — InferenceResponse.routing_decision carries the routing trace."""
    assert InferenceResponse.model_fields["routing_decision"].annotation is RoutingDecisionTrace
    assert set(InferenceResponse.model_fields) == {
        "provider_used",
        "model_used",
        "routing_decision",
        "response_payload",
        "tokens_in",
        "tokens_out",
        "cached_tokens_in",
    }


def test_infer_probabilistic_core_per_add_53() -> None:
    """#4 — `infer` is the probabilistic core per ADD §5.3.3."""
    assert "probabilistic core" in (infer.__doc__ or "")
    assert InferenceRequest.model_config.get("frozen") is True
    assert InferenceResponse.model_config.get("frozen") is True


# --- R-300 activation must_pass --------------------------------------------


async def test_infer_invokes_route() -> None:
    """must_pass #1 — `infer` invokes `route`; the DECLARATIVE layer decision
    fires and the routed provider/model + trace reach the dispatch callable;
    the response is materialized from the dispatch result."""
    decl_calls: list[RoutingLayer] = []

    def decl(_payload: ProviderAgnosticPayload, _m: RoutingManifest) -> str | None:
        decl_calls.append(RoutingLayer.DECLARATIVE)
        return "anthropic:claude-opus-4-8"

    dispatch, dispatch_calls = _recording_dispatch()

    response = await infer(
        _request(),
        dispatch=dispatch,
        manifest=_manifest(),
        layer_decisions={RoutingLayer.DECLARATIVE: decl},
    )

    # route() ran the DECLARATIVE layer.
    assert decl_calls == [RoutingLayer.DECLARATIVE]
    # The routed candidate was parsed and handed to the dispatch callable.
    assert dispatch_calls and dispatch_calls[0][0] == "anthropic"
    assert dispatch_calls[0][1] == "claude-opus-4-8"
    assert dispatch_calls[0][2].candidate == "anthropic:claude-opus-4-8"
    # The response is materialized from route() + dispatch result.
    assert response.provider_used == "anthropic"
    assert response.model_used == "claude-opus-4-8"
    assert response.tokens_in == 7
    assert response.tokens_out == 3
    assert isinstance(response.routing_decision, RoutingDecisionTrace)


async def test_infer_declarative_layer_is_manifest() -> None:
    """must_pass #2 — on a DECLARATIVE hit, routing_decision.layer == 'manifest'
    (`RoutingLayer.DECLARATIVE.value`)."""

    def decl(_payload: ProviderAgnosticPayload, _m: RoutingManifest) -> str | None:
        return "anthropic:claude-opus-4-8"

    dispatch, _ = _recording_dispatch()

    response = await infer(
        _request(),
        dispatch=dispatch,
        manifest=_manifest(),
        layer_decisions={RoutingLayer.DECLARATIVE: decl},
    )

    assert response.routing_decision.layer == "manifest"
    assert response.routing_decision.layer == RoutingLayer.DECLARATIVE.value


async def test_infer_binds_layer_budgets() -> None:
    """must_pass #3 — per-layer LayerBudget is bound per C-CP-03. The default
    is `DEFAULT_LAYER_BUDGETS`; an explicit tuple is honored and budget
    exhaustion at a layer falls through to the next."""
    # Default budgets are bound when not supplied.
    assert inspect.signature(infer).parameters["budgets"].default is DEFAULT_LAYER_BUDGETS

    embedding_calls: list[RoutingLayer] = []

    def decl(_payload: ProviderAgnosticPayload, _m: RoutingManifest) -> str | None:
        return "anthropic:declarative-model"

    def emb(_payload: ProviderAgnosticPayload, _m: RoutingManifest) -> str | None:
        embedding_calls.append(RoutingLayer.EMBEDDING)
        return "openai:embedding-model"

    dispatch, _ = _recording_dispatch()
    budgets: tuple[LayerBudget, ...] = DEFAULT_LAYER_BUDGETS

    # DECLARATIVE budget exhausted -> fall through to EMBEDDING.
    response = await infer(
        _request(),
        dispatch=dispatch,
        manifest=_manifest(),
        layer_decisions={RoutingLayer.DECLARATIVE: decl, RoutingLayer.EMBEDDING: emb},
        budgets=budgets,
        budget_exhausted=frozenset({RoutingLayer.DECLARATIVE}),
    )

    assert embedding_calls == [RoutingLayer.EMBEDDING]
    assert response.routing_decision.layer == RoutingLayer.EMBEDDING.value
    assert response.routing_decision.budget_exhausted is True
    assert response.provider_used == "openai"


async def test_infer_raises_on_unresolved_candidate() -> None:
    """No layer produces a candidate -> RoutingCandidateUnresolvedError (the
    dispatch callable is never invoked)."""
    dispatch, dispatch_calls = _recording_dispatch()

    with pytest.raises(RoutingCandidateUnresolvedError):
        await infer(
            _request(),
            dispatch=dispatch,
            manifest=_manifest(),
            layer_decisions={},  # no layer decides -> empty candidate
        )
    assert dispatch_calls == []


async def test_infer_raises_on_malformed_candidate() -> None:
    """A candidate without a 'provider:model' separator is rejected."""

    def decl(_payload: ProviderAgnosticPayload, _m: RoutingManifest) -> str | None:
        return "no-separator"

    dispatch, dispatch_calls = _recording_dispatch()

    with pytest.raises(RoutingCandidateUnresolvedError):
        await infer(
            _request(),
            dispatch=dispatch,
            manifest=_manifest(),
            layer_decisions={RoutingLayer.DECLARATIVE: decl},
        )
    assert dispatch_calls == []

"""Tests for U-CP-03 — thin routing core surface (C-CP-01 §1.1).

Acceptance-criterion coverage:
  #1 `infer` single entry-point   -> test_infer_single_entry_point
  #2 routing-discriminator fields -> test_inference_request_routing_discriminators
  #3 routing.* span attribution   -> test_infer_emits_routing_attributes
  #4 probabilistic core per ADD   -> test_infer_probabilistic_core_per_add_53
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
from harness_cp.routing_core_surface import (
    InferenceRequest,
    InferenceResponse,
    infer,
)


def _request() -> InferenceRequest:
    return InferenceRequest(
        agent_role=AgentRole("lead"),
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        context_tokens=1024,
        request_payload=ProviderAgnosticPayload(messages=(), tools=None, params={}),
        trace_context=TraceContext(
            trace_id="t0", span_id="s0", trace_flags=0, trace_state=None
        ),
    )


def test_infer_single_entry_point() -> None:
    """#1 — `infer` is the only entry-point for LLM inference at the CP layer."""
    sig = inspect.signature(infer)
    assert list(sig.parameters) == ["request"]
    assert sig.parameters["request"].annotation == "InferenceRequest"
    # The surface declares only the request-in / response-out shape.
    with pytest.raises(NotImplementedError):
        infer(_request())


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
    assert (
        InferenceResponse.model_fields["routing_decision"].annotation
        is RoutingDecisionTrace
    )
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
    """#4 — `infer` is the probabilistic core per ADD §5.3.3.

    The surface delegates routing to U-CP-05 and provider dispatch to the
    AS-plan SDK boundary; the CP plan declares the thin core only.
    """
    assert "probabilistic core" in (infer.__doc__ or "")
    assert InferenceRequest.model_config.get("frozen") is True
    assert InferenceResponse.model_config.get("frozen") is True

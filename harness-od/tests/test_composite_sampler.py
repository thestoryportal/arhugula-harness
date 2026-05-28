"""C-OD-09 + C-OD-10 HarnessCompositeSampler tests.

Closes H_T-OD-3 retirement gate "project-authored composite head/tail
sampler subclass" at the SDK boundary. Tests verify §9.2 always-sampled
discipline (literals + dot-anchored prefixes) honored regardless of
trace_id ratio, base-rate gating for non-always-sampled events, and
ParentBased propagation through the canonical wrapping pattern.
"""

from __future__ import annotations

import pytest
from opentelemetry.sdk.trace.sampling import Decision, ParentBased
from opentelemetry.trace import SpanContext, SpanKind, TraceFlags
from opentelemetry.trace.span import NonRecordingSpan
from opentelemetry import context as ot_context
from opentelemetry import trace as ot_trace

from harness_od.composite_sampler import (
    HarnessCompositeSampler,
    build_default_sampler,
)
from harness_od.sampling_mode import (
    ALWAYS_SAMPLED_EVENT_CLASSES,
    is_always_sampled,
)


# Concrete span names exercising each §9.2 row.
_LITERAL_ALWAYS_SAMPLED = (
    "sandbox.violation",
    "sandbox.tier_escalation",
    "hitl.gate.evaluated",
    "hitl.invocation.opened",
    "hitl.invocation.responded",
    "hitl.invocation.timed_out",
    "fallback.triggered",
    "breaker.tripped",
    "topology.fanout.opened",
    "topology.fanout.closed",
    "subagent.span",
    "mcp.tool.call",
    "files.operation",
    "memory.operation",
    "managed_agents.runtime",
    "skill.activation",
)


# ---------------------------------------------------------------------------
# §9.2 substrate — is_always_sampled literal + prefix resolution.
# ---------------------------------------------------------------------------


def test_canonical_set_carries_18_entries_per_spec_9_2() -> None:
    assert len(ALWAYS_SAMPLED_EVENT_CLASSES) == 18


@pytest.mark.parametrize("name", _LITERAL_ALWAYS_SAMPLED)
def test_is_always_sampled_matches_literal_entries(name: str) -> None:
    assert is_always_sampled(name) is True


@pytest.mark.parametrize(
    "name",
    [
        "audit.signature.write",
        "audit.cp.dispatch",
        "audit.entry",
        "validator.fail.semantic_inconsistency",
        "validator.fail.permanence",
    ],
)
def test_is_always_sampled_matches_dot_anchored_prefixes(name: str) -> None:
    assert is_always_sampled(name) is True


def test_is_always_sampled_dot_anchor_forecloses_bare_prefix_collision() -> None:
    # "audit" alone (no dot) must not be a prefix match — the dot anchor in
    # `audit.` enforces sub-namespace structure per spec §9.2 prose.
    assert is_always_sampled("audit") is False
    assert is_always_sampled("auditor") is False
    assert is_always_sampled("validator.fail") is False
    assert is_always_sampled("validator.failed") is False


@pytest.mark.parametrize(
    "name", ["chat", "execute_tool", "sandbox.enter", "sandbox.exit", "tool.call"]
)
def test_is_always_sampled_rejects_base_rate_set_members(name: str) -> None:
    assert is_always_sampled(name) is False


# ---------------------------------------------------------------------------
# HarnessCompositeSampler — root sampling decision at SDK boundary.
# ---------------------------------------------------------------------------


def _result_records(decision: Decision) -> bool:
    return decision == Decision.RECORD_AND_SAMPLE


@pytest.mark.parametrize("name", _LITERAL_ALWAYS_SAMPLED)
def test_always_sampled_literal_at_base_rate_zero_still_samples(name: str) -> None:
    """§9.2 floor inviolable: always-sampled members sample regardless of
    base_rate; even base_rate=0.0 cannot suppress them."""
    sampler = HarnessCompositeSampler(base_rate=0.0)
    result = sampler.should_sample(
        parent_context=None,
        trace_id=0x12345678901234567890123456789012,
        name=name,
    )
    assert _result_records(result.decision)


def test_always_sampled_prefix_at_base_rate_zero_still_samples() -> None:
    sampler = HarnessCompositeSampler(base_rate=0.0)
    for name in ("audit.signature.write", "validator.fail.semantic_inconsistency"):
        result = sampler.should_sample(
            parent_context=None,
            trace_id=0x12345678901234567890123456789012,
            name=name,
        )
        assert _result_records(result.decision), f"failed at {name}"


def test_base_rate_one_samples_non_always_sampled_event() -> None:
    sampler = HarnessCompositeSampler(base_rate=1.0)
    result = sampler.should_sample(
        parent_context=None,
        trace_id=0x12345678901234567890123456789012,
        name="chat",
    )
    assert _result_records(result.decision)


def test_base_rate_zero_drops_non_always_sampled_event() -> None:
    sampler = HarnessCompositeSampler(base_rate=0.0)
    result = sampler.should_sample(
        parent_context=None,
        trace_id=0x12345678901234567890123456789012,
        name="chat",
    )
    assert not _result_records(result.decision)


def test_base_rate_validation_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="base_rate must be in"):
        HarnessCompositeSampler(base_rate=-0.1)
    with pytest.raises(ValueError, match="base_rate must be in"):
        HarnessCompositeSampler(base_rate=1.5)


def test_base_rate_property_surfaces_constructor_value() -> None:
    assert HarnessCompositeSampler(base_rate=0.25).base_rate == 0.25


def test_get_description_surfaces_spec_citation() -> None:
    desc = HarnessCompositeSampler(base_rate=1.0).get_description()
    assert "C-OD-09" in desc
    assert "1.0" in desc


# ---------------------------------------------------------------------------
# build_default_sampler — ParentBased wrapping per OTel canonical pattern.
# ---------------------------------------------------------------------------


def test_build_default_sampler_returns_parent_based_wrapper() -> None:
    sampler = build_default_sampler()
    assert isinstance(sampler, ParentBased)


def test_parent_based_root_decision_at_always_sampled_name() -> None:
    sampler = build_default_sampler(base_rate=0.0)
    result = sampler.should_sample(
        parent_context=None,
        trace_id=0x12345678901234567890123456789012,
        name="sandbox.violation",
        kind=SpanKind.INTERNAL,
    )
    assert _result_records(result.decision)


def test_parent_based_inherits_sampled_parent_decision() -> None:
    """OTel ParentBased canonical contract: child of a sampled parent samples
    regardless of the inner root sampler's decision."""
    sampler = build_default_sampler(base_rate=0.0)
    parent_context = SpanContext(
        trace_id=0x12345678901234567890123456789012,
        span_id=0x1234567890123456,
        is_remote=False,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
    )
    ctx = ot_trace.set_span_in_context(NonRecordingSpan(parent_context))
    result = sampler.should_sample(
        parent_context=ctx,
        trace_id=parent_context.trace_id,
        name="chat",  # would not sample at base_rate=0.0 at root
        kind=SpanKind.INTERNAL,
    )
    assert _result_records(result.decision)


def test_parent_based_inherits_unsampled_parent_decision() -> None:
    """OTel ParentBased canonical contract: child of an unsampled parent does
    not sample even if the name would always-sample at root."""
    sampler = build_default_sampler(base_rate=1.0)
    parent_context = SpanContext(
        trace_id=0x12345678901234567890123456789012,
        span_id=0x1234567890123456,
        is_remote=False,
        trace_flags=TraceFlags(TraceFlags.DEFAULT),  # not sampled
    )
    ctx = ot_trace.set_span_in_context(NonRecordingSpan(parent_context))
    result = sampler.should_sample(
        parent_context=ctx,
        trace_id=parent_context.trace_id,
        name="sandbox.violation",  # always-sampled at root, but parent says no
        kind=SpanKind.INTERNAL,
    )
    assert not _result_records(result.decision)

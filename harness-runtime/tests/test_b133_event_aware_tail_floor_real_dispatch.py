"""U-OD-59 (`B-133`) — the REAL-DISPATCH half of the event-aware §9.2 floor witnesses.

Authority: `Spec_Operational_Discipline_v1_38.md` §C-OD-09 §9.2.1 (the
event-aware tail arm + the declared HEAD bound) +
`Implementation_Plan_Operational_Discipline_v2_33.md` U-OD-59.

**Why an OD unit's witnesses live in `harness-runtime/tests`.** U-OD-59 is an
OD unit and its subject — `TailKeepSpanProcessor` — is OD-owned. But these five
witnesses drive a REAL `RetryBreakerFallbackDispatcher`, which is a
`harness_runtime` surface, and **`harness-od` does not declare `harness-runtime`
as a dependency and must not**: OD is the consumer-most-downstream axis, so the
`axis-isolation — harness-od` CI leg syncs ONLY `harness-od` + its declared deps
and a `harness_runtime` import there fails collection. The homing is therefore
the honest one rather than a marker dodge: **the real-dispatch half is genuinely
runtime-homed** (runtime consumes the tail processor in production and imports
`harness_od` freely), and the OD-only half stays at
`harness-od/tests/test_b133_event_aware_tail_floor.py`, where it pins the
processor's own contract with no runtime present. The `_real_dispatch`
suffix is not decoration: both `tests/` directories are packages (`__init__.py`),
so two modules sharing a basename collide into one importable `tests.<name>` and
pytest silently attributes one file's cases to both paths — repo-wide basename
uniqueness holds across all 515 test modules and is preserved here.

**These five witnesses** (preserved verbatim from the pre-split module, modulo
this docstring):

| ID | Witness |
|---|---|
| W1 | Counterfactual — the carrier span fails BOTH name-shaped predicates, and a carrier whose events are all non-members is still dropped |
| W2 | `fallback.exhausted` survives the tail via a REAL exhausted dispatch |
| W3 | `fallback.triggered` survives the tail via a REAL capability-shortfall dispatch |
| W4 | `breaker.tripped` survives the tail via a REAL charging-fault dispatch |
| W5 | HEAD-half DECLARED BOUND — the head sampler at `base_rate=0.0` still drops the event carrier, while a span NAMED `fallback.exhausted` survives |

W6–W14 (the OD-only half, including the W13/W14 production-cell bound witnesses,
which compose only `build_default_sampler` + `TailKeepSpanProcessor` and need no
runtime surface) stay in the OD module. The PD-8 probe table lives there too.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_core import PersonaTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_od.composite_sampler import build_default_sampler
from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_classification import is_classification_trigger
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchPayloadShapeError,
    LLMDispatchProviderUnreachableError,
)
from harness_runtime.lifecycle.retry_breaker import (
    DEFAULT_COOLDOWN_SECONDS,
    DEFAULT_FAIL_THRESHOLD,
    DEFAULT_RETRY_POLICY,
    RuntimeRetryBreaker,
)
from harness_runtime.lifecycle.retry_breaker_fallback import (
    RESERVED_LLM_DISPATCH_KEY,
    RetryBreakerFallbackDispatcher,
    RetryBreakerFallbackExhaustedError,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

CARRIER_SPAN_NAME = "harness.runtime.retry_breaker_fallback"


# ---------------------------------------------------------------------------
# Real-dispatch fixtures (mirrors of the U-RT-58 suite's fakes).
# ---------------------------------------------------------------------------


@dataclass
class _MockInner:
    """Raises the supplied fault on every `dispatch` (drives to exhaustion)."""

    outcomes: list[Mapping[str, Any] | BaseException]
    calls: list[Any] = field(default_factory=list)
    _cursor: int = 0

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> Mapping[str, Any]:
        self.calls.append((binding, step))
        outcome = self.outcomes[min(self._cursor, len(self.outcomes) - 1)]
        self._cursor += 1
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _candidate(provider: str, model: str) -> ProviderCandidate:
    family_map = {
        "anthropic": ProviderFamily.ANTHROPIC,
        "openai": ProviderFamily.OPENAI,
    }
    return ProviderCandidate(provider=provider, model=model, family=family_map[provider])


def _binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider="anthropic", model="claude-test-1"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 100},
        },
    )


def _thinking_step() -> WorkflowStep:
    """An INFERENCE_STEP requiring the THINKING capability (C-CP-03 §3.3)."""
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "think hard"}],
            "tools": None,
            "params": {"thinking": {"type": "enabled", "budget_tokens": 4096}},
        },
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="test-step-key",
        tenant_id=None,
        step_index=0,
    )


def _registry(*, max_attempts: int = 2, fail_threshold: int = DEFAULT_FAIL_THRESHOLD):
    return RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=max_attempts, backoff="full_jitter", jitter="full_jitter"
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        fail_threshold=fail_threshold,
        cooldown_seconds=DEFAULT_COOLDOWN_SECONDS,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )


async def _noop_sleep(_seconds: float) -> None:
    return None


def _tail_provider(*, base_rate: float = 1.0) -> tuple[TracerProvider, InMemorySpanExporter, Any]:
    """The REAL production processor chain: composite sampler + tail-keep."""
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider(sampler=build_default_sampler(base_rate=base_rate))
    provider.add_span_processor(tail)
    return provider, exporter, tail


async def _dispatch_exhausted(
    provider: TracerProvider,
    *,
    fault: BaseException,
    step: WorkflowStep,
    fail_threshold: int = DEFAULT_FAIL_THRESHOLD,
) -> None:
    """Drive a REAL dispatch to fallback-chain exhaustion."""
    chain = FallbackChain(
        primary=_candidate("anthropic", "claude-test-1"),
        same_family=(_candidate("anthropic", "claude-test-2"),),
        cross_family=(),
        terminal=None,
    )
    wrapper = RetryBreakerFallbackDispatcher(
        inner=_MockInner(outcomes=[fault]),
        retry_breaker=_registry(max_attempts=2, fail_threshold=fail_threshold),
        fallback_chain=chain,
        tracer_provider=provider,
        sleep_fn=_noop_sleep,
    )
    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding(), step, step_context=_step_context())


async def _dispatch_capability_shortfall(provider: TracerProvider) -> None:
    """Drive a REAL capability-shortfall exhaustion (emits `fallback.triggered`)."""
    chain = FallbackChain(
        primary=_candidate("openai", "gpt-test-1"),
        same_family=(),
        cross_family=(_candidate("openai", "gpt-test-2"),),
        terminal=None,
    )
    wrapper = RetryBreakerFallbackDispatcher(
        inner=_MockInner(outcomes=[]),
        retry_breaker=_registry(max_attempts=1),
        fallback_chain=chain,
        tracer_provider=provider,
        sleep_fn=_noop_sleep,
    )
    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding(), _thinking_step(), step_context=_step_context())


def _exported_event_names(exporter: InMemorySpanExporter) -> set[str]:
    return {e.name for s in exporter.get_finished_spans() for e in s.events}


# ---------------------------------------------------------------------------
# W1 — the counterfactual (what the pre-repair shape asserted).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_w1_carrier_span_fails_both_name_shaped_predicates() -> None:
    """The `B-133` defect shape, asserted rather than described.

    The dispatch carrier span is in NEITHER §9.2 (by name) NOR §10.2 (by the
    trigger predicate) — so under a name-only classification the whole trace,
    always-sampled event included, is dropped at root close. This assertion is
    what makes the repair load-bearing: if either predicate ever became True by
    name, the event arm would be redundant and this witness would go red.
    """
    provider, exporter, _ = _tail_provider(base_rate=1.0)
    plain_exporter = InMemorySpanExporter()
    plain_provider = TracerProvider(sampler=build_default_sampler(base_rate=1.0))
    plain_provider.add_span_processor(SimpleSpanProcessor(plain_exporter))
    await _dispatch_exhausted(
        plain_provider, fault=LLMDispatchProviderUnreachableError("anthropic"), step=_step()
    )
    plain_provider.force_flush()
    carrier = next(s for s in plain_exporter.get_finished_spans() if s.name == CARRIER_SPAN_NAME)
    assert is_always_sampled(carrier.name, carrier.attributes) is False
    assert is_classification_trigger(carrier) is False
    assert "fallback.exhausted" in {e.name for e in carrier.events}

    # Live control: a carrier whose events are ALL non-members is still dropped.
    tracer = provider.get_tracer("w1")
    with tracer.start_as_current_span(CARRIER_SPAN_NAME) as span:
        span.add_event("retry.skipped")
        span.add_event("exception")
    assert exporter.get_finished_spans() == ()


# ---------------------------------------------------------------------------
# W2-W4 — post-repair survival, all three members, REAL processor chain.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_w2_fallback_exhausted_survives_the_tail() -> None:
    """A REAL exhausted dispatch's `fallback.exhausted` reaches the exporter."""
    provider, exporter, tail = _tail_provider(base_rate=1.0)
    await _dispatch_exhausted(
        provider, fault=LLMDispatchProviderUnreachableError("anthropic"), step=_step()
    )
    # No `force_flush` — survival must come from the arm, not the drain path.
    assert "fallback.exhausted" in _exported_event_names(exporter)
    assert tail.buffered_trace_count == 0


@pytest.mark.asyncio
async def test_w3_fallback_triggered_survives_the_tail() -> None:
    """A REAL capability-shortfall dispatch's `fallback.triggered` reaches the exporter."""
    provider, exporter, tail = _tail_provider(base_rate=1.0)
    await _dispatch_capability_shortfall(provider)
    assert "fallback.triggered" in _exported_event_names(exporter)
    assert tail.buffered_trace_count == 0


@pytest.mark.asyncio
async def test_w4_breaker_tripped_survives_the_tail() -> None:
    """A REAL charging-fault dispatch's `breaker.tripped` reaches the exporter.

    `LLMDispatchPayloadShapeError` is a CHARGING fault (it is not one of the
    §14.6.3 five waived types), so `record_failure` fires and the breaker trips
    at `fail_threshold=1`, emitting the event on the carrier span.
    """
    provider, exporter, tail = _tail_provider(base_rate=1.0)
    await _dispatch_exhausted(
        provider,
        fault=LLMDispatchPayloadShapeError("bad shape"),
        step=_step(),
        fail_threshold=1,
    )
    assert "breaker.tripped" in _exported_event_names(exporter)
    assert tail.buffered_trace_count == 0


# ---------------------------------------------------------------------------
# W5 — the HEAD-half DECLARED BOUND, pinned honestly.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_w5_head_sampler_still_drops_the_event_carrier_declared_bound() -> None:
    """OD spec v1.38 §9.2.1 term 4 — the HEAD half is NOT repaired by this arm.

    A span's events do not exist at span creation, so `should_sample` has
    nothing to inspect; at `base_rate < 1` the event carrier is dropped before
    any processor runs. Asserted, not glossed — and paired with the discriminator
    that a span NAMED `fallback.exhausted` DOES survive the same sampler, which
    is what makes "event-shaped, not name-shaped" the operative cause.

    This bound is NOT vacuous: `team-binding x local-development` is
    HEAD_BASED_DEV at a §10.3 default base-rate of 0.5 and engages no tail
    processor, so the three event-shaped members are still dropped there.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    await _dispatch_exhausted(
        provider, fault=LLMDispatchProviderUnreachableError("anthropic"), step=_step()
    )
    provider.force_flush()
    assert exporter.get_finished_spans() == ()

    # Discriminator: the SAME sampler keeps a NAME-shaped member.
    tracer = provider.get_tracer("w5")
    with tracer.start_as_current_span("fallback.exhausted"):
        pass
    provider.force_flush()
    assert [s.name for s in exporter.get_finished_spans()] == ["fallback.exhausted"]

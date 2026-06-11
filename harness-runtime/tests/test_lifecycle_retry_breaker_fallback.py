"""Tests for U-RT-58 — retry / breaker / fallback composer wrapping C-RT-15
(`Spec_Harness_Runtime_v1.md` v1.4 §14.6 C-RT-16).

Acceptance-criterion coverage:

  AC #1  — Protocol satisfaction (``StepDispatcher`` from CP workflow driver).
  AC #2  — Per-candidate iteration verified across a 3-candidate chain.
  AC #3  — Per-candidate retry-then-success under ``RetryPolicy(max_attempts=3)``.
  AC #4  — ``retry.*`` 6-attribute namespace emission per C-CP-03 §3.5.
  AC #5  — ``fallback.exhausted`` emission + ``RetryBreakerFallbackExhaustedError``.
  AC #6  — Breaker pre-check (OPEN → skip) + ``harness.breaker.*`` emission.
  AC #7  — Nested-span hierarchy (outer → per-attempt; verified via
           InMemorySpanExporter parent-span-id linkage).
  AC #8  — Reserved registry key extension + ``ReservedToolNameError`` at
           manifest validation.
  AC #9  — Bootstrap stage 5 wrap (``ctx.llm_dispatcher`` post-condition is
           the wrapper; ``.inner`` is the bare ``RuntimeLLMDispatcher``).
  AC #10 — Phase 7d retirement-event prerequisite (post-landing; tracked at
           the retirement event file, not this test).

Test conventions follow ``tests/test_lifecycle_llm_dispatch.py``:
in-memory OTel span exporter + SimpleSpanProcessor for synchronous flushing.
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
from harness_cp.provider_capabilities import ProviderCapability
from harness_cp.routing_manifest_residence import (
    ReservedToolNameError,
    RetryPolicy,
    RoutingManifest,
    validate_routing_manifest,
)
from harness_cp.workflow_driver import StepDispatcher
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_od.harness_breaker_schema import BreakerScope
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchPayloadShapeError,
    LLMDispatchProviderUnreachableError,
    RuntimeLLMDispatcher,
)
from harness_runtime.lifecycle.retry_breaker import (
    DEFAULT_RETRY_POLICY,
    BreakerStateMachine,
    BreakerTransition,
    RuntimeRetryBreaker,
    materialize_retry_breaker_stage,
)
from harness_runtime.lifecycle.retry_breaker_fallback import (
    DEFAULT_LLM_DISPATCH_RETRY_POLICY,
    RESERVED_LLM_DISPATCH_KEY,
    RetryBreakerFallbackDispatcher,
    RetryBreakerFallbackExhaustedError,
    _required_capabilities,
    materialize_retry_breaker_fallback_dispatcher_stage,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# ---------------------------------------------------------------------------
# Fakes.
# ---------------------------------------------------------------------------


@dataclass
class _MockInnerDispatcher:
    """Records each `dispatch` call; returns canned outcomes per attempt.

    ``outcomes`` is a list of either ``Mapping[str, Any]`` (success) or
    ``BaseException`` instances (raise this exception). The mock advances
    through the list one entry per ``dispatch`` call. If the list exhausts,
    further calls raise ``IndexError`` (test failure signal — the test set
    up wrong outcome count)."""

    outcomes: list[Mapping[str, Any] | BaseException]
    calls: list[tuple[StepEffectiveBinding, WorkflowStep]] = field(default_factory=list)
    _cursor: int = 0

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> Mapping[str, Any]:
        # `step_context` accepted at v1.6 Path A per amended StepDispatcher
        # Protocol (C-RT-17 resolution); mock inner does not consume.
        self.calls.append((binding, step))
        if self._cursor >= len(self.outcomes):
            raise IndexError(
                f"_MockInnerDispatcher exhausted after {self._cursor} calls; "
                f"test outcome-list under-supplied"
            )
        outcome = self.outcomes[self._cursor]
        self._cursor += 1
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


def _candidate(provider: str, model: str) -> ProviderCandidate:
    # ``ProviderFamily`` enum is 4-valued per C-CP-04 §4.1: ANTHROPIC / OPENAI /
    # GOOGLE / LOCAL_OPEN_WEIGHT. "ollama" maps to LOCAL_OPEN_WEIGHT for tests.
    family_map = {
        "anthropic": ProviderFamily.ANTHROPIC,
        "openai": ProviderFamily.OPENAI,
        "ollama": ProviderFamily.LOCAL_OPEN_WEIGHT,
    }
    return ProviderCandidate(provider=provider, model=model, family=family_map[provider])


def _chain(
    primary: ProviderCandidate,
    *,
    same_family: tuple[ProviderCandidate, ...] = (),
    cross_family: tuple[ProviderCandidate, ...] = (),
    terminal: ProviderCandidate | None = None,
) -> FallbackChain:
    return FallbackChain(
        primary=primary,
        same_family=same_family,
        cross_family=cross_family,
        terminal=terminal,
    )


def _binding(provider: str = "anthropic", model: str = "claude-test-1") -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider=provider, model=model),
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


def _tracer_provider_with_exporter() -> tuple[TracerProvider, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exporter))
    return tp, exporter


def _step_context(step_index: int = 0) -> StepExecutionContext:
    """Default step_context for v1.6 Path A test fixtures.

    C-RT-16 wrapper accepts step_context but does not consume it at v1.6;
    pass-through to the inner C-RT-15 dispatcher per the Protocol
    conformance discipline.
    """
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id=f"workflow:test-wf:step:{step_index}",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="test-step-key",
        tenant_id=None,
        step_index=step_index,
    )


def _retry_breaker_with_llm_policy(*, max_attempts: int = 3) -> RuntimeRetryBreaker:
    """Construct a registry with the reserved LLM-dispatch policy pre-bound.

    Mirrors what ``materialize_retry_breaker_stage`` does at bootstrap; used
    where the bootstrap path isn't exercised end-to-end."""
    return RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=max_attempts,
                backoff="full_jitter",
                jitter="full_jitter",
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        base_delay_seconds=0.0,  # makes computed delays small for tests
        delay_cap_seconds=0.01,
    )


async def _noop_sleep(_seconds: float) -> None:
    """Sleep mock — keeps async tests fast and deterministic."""
    return None


# ---------------------------------------------------------------------------
# AC #1 — Protocol satisfaction.
# ---------------------------------------------------------------------------


def test_wrapper_satisfies_step_dispatcher_protocol() -> None:
    """The wrapper structurally satisfies the CP-side ``StepDispatcher``
    Protocol — the driver's call site at `workflow_driver.py:379` accepts
    the wrapper unchanged."""
    tp, _ = _tracer_provider_with_exporter()
    inner = _MockInnerDispatcher(outcomes=[])
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=_retry_breaker_with_llm_policy(),
        fallback_chain=_chain(_candidate("anthropic", "claude-test-1")),
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )
    assert isinstance(wrapper, StepDispatcher)


# ---------------------------------------------------------------------------
# AC #2 — Per-candidate iteration across a 3-candidate chain.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterates_three_candidates_until_success() -> None:
    """Mock inner that fails transient on candidates 0+1 and succeeds on
    candidate 2; assert the wrapper iterates all three and returns the
    candidate-2 result."""
    primary = _candidate("anthropic", "claude-test-1")
    same_family = (_candidate("anthropic", "claude-test-2"),)
    cross_family = (_candidate("openai", "gpt-test-1"),)
    chain = _chain(primary, same_family=same_family, cross_family=cross_family)

    # max_attempts=1 → each candidate gets one attempt; fails advance to next.
    breaker = _retry_breaker_with_llm_policy(max_attempts=1)
    inner = _MockInnerDispatcher(
        outcomes=[
            RuntimeError("transient on candidate 0"),
            RuntimeError("transient on candidate 1"),
            {"result": "candidate-2-success"},
        ]
    )
    tp, _ = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    result = await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    assert result == {"result": "candidate-2-success"}

    # All three candidates exercised; rebound binding observable.
    assert len(inner.calls) == 3
    seen_providers = [call[0].model_binding.provider for call in inner.calls]
    seen_models = [call[0].model_binding.model for call in inner.calls]
    assert seen_providers == ["anthropic", "anthropic", "openai"]
    assert seen_models == ["claude-test-1", "claude-test-2", "gpt-test-1"]


# ---------------------------------------------------------------------------
# AC #3 — Per-candidate retry-then-success under max_attempts=3.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retries_twice_then_succeeds_on_attempt_3() -> None:
    """Mock inner that fails (transient) twice then succeeds on attempt 3
    under ``RetryPolicy(max_attempts=3)``; assert success without iterating
    to the next candidate; verify three per-attempt spans."""
    primary = _candidate("anthropic", "claude-test-1")
    chain = _chain(primary)
    breaker = _retry_breaker_with_llm_policy(max_attempts=3)
    inner = _MockInnerDispatcher(
        outcomes=[
            RuntimeError("transient attempt 0"),
            RuntimeError("transient attempt 1"),
            {"result": "success-on-attempt-3"},
        ]
    )
    sleep_calls: list[float] = []

    async def _recording_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_recording_sleep,
    )

    result = await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    assert result == {"result": "success-on-attempt-3"}
    assert len(inner.calls) == 3
    # Two sleeps between three attempts.
    assert len(sleep_calls) == 2

    # Verify three per-attempt spans + one outer span.
    spans = exporter.get_finished_spans()
    attempt_spans = [s for s in spans if s.name == "harness.runtime.retry_attempt"]
    assert len(attempt_spans) == 3
    outer_spans = [s for s in spans if s.name == "harness.runtime.retry_breaker_fallback"]
    assert len(outer_spans) == 1

    # Final attempt is the success path — canonical CP §3.5 sampling discipline
    # omits `retry.fail_class` on success (presence is the tail-keep fail signal).
    last_attempt = attempt_spans[-1]
    assert last_attempt.attributes is not None
    assert "retry.fail_class" not in last_attempt.attributes


# ---------------------------------------------------------------------------
# AC #4 — retry.* 6-attribute namespace emission per C-CP-03 §3.5.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_six_attribute_namespace_emitted_per_attempt() -> None:
    """Each per-attempt span carries the canonical CP §3.5 6-attribute namespace
    (per Spec_Control_Plane_v1_3.md §3.5 + ADR-D1 v1.2 §1.1.1): ``retry.attempt_number``
    (1-indexed), ``retry.original_span_id`` (16-hex outer-span-id),
    ``retry.delay_ms``, ``retry.cause_attribution``, ``retry.fail_class``
    (`ValidatorRetryExitClass` enum), ``engine.replay_disposition`` (via
    `REPLAY_DISPOSITION_MAPPING[binding.engine_class]`).

    Path A resolution of `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md`
    landed at runtime spec v1.5 + plan v2.4 (2026-05-20); previously named
    `retry.attempt` / `retry.attempt_count` / `retry.policy_id` / `retry.backoff_ms`
    / `retry.cause_class` / `retry.terminal` — drifted names per the runtime
    spec v1.4 step 4 phrasing, NOT canonical."""
    from harness_cp.engine_namespace import REPLAY_DISPOSITION_MAPPING

    primary = _candidate("anthropic", "claude-test-1")
    chain = _chain(primary)
    breaker = _retry_breaker_with_llm_policy(max_attempts=3)
    inner = _MockInnerDispatcher(
        outcomes=[
            RuntimeError("transient attempt 0"),
            {"result": "ok"},
        ]
    )
    tp, exporter = _tracer_provider_with_exporter()
    binding = _binding()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    await wrapper.dispatch(binding, _step(), step_context=_step_context())
    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    attempts = [s for s in spans if s.name == "harness.runtime.retry_attempt"]
    assert len(attempts) == 2

    expected_replay = REPLAY_DISPOSITION_MAPPING[binding.engine_class].value
    expected_original_span_id = format(outer.context.span_id, "016x")

    # First attempt (transient → retry).
    first = attempts[0].attributes
    assert first is not None
    assert first["retry.attempt_number"] == 1  # 1-indexed per CP §3.5
    assert first["retry.original_span_id"] == expected_original_span_id
    assert first["engine.replay_disposition"] == expected_replay
    assert first["retry.cause_attribution"] == "transient-retry"
    assert first["retry.fail_class"] == "transient-retry"
    assert "retry.delay_ms" in first

    # Second attempt (success — fail_class omitted by canonical sampling
    # discipline; presence of `retry.fail_class` is tail-keep signal).
    second = attempts[1].attributes
    assert second is not None
    assert second["retry.attempt_number"] == 2
    assert second["retry.original_span_id"] == expected_original_span_id
    assert second["engine.replay_disposition"] == expected_replay
    assert second["retry.delay_ms"] == 0
    # On success path canonical sampling discipline says fail_class omitted.
    assert "retry.fail_class" not in second


# ---------------------------------------------------------------------------
# AC #5 — fallback.exhausted emission + typed terminal error.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fallback_exhausted_emits_and_raises_typed() -> None:
    """All candidates fail-fast (provider-unreachable); the wrapper iterates,
    emits ``fallback.exhausted`` on the outer span, and raises
    ``RetryBreakerFallbackExhaustedError`` mapping to
    ``RT-FAIL-FALLBACK-EXHAUSTED``."""
    primary = _candidate("anthropic", "claude-test-1")
    same_family = (_candidate("anthropic", "claude-test-2"),)
    chain = _chain(primary, same_family=same_family)
    breaker = _retry_breaker_with_llm_policy(max_attempts=2)
    inner = _MockInnerDispatcher(
        outcomes=[
            LLMDispatchProviderUnreachableError("anthropic"),
            LLMDispatchProviderUnreachableError("anthropic"),
        ]
    )
    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    with pytest.raises(RetryBreakerFallbackExhaustedError) as exc_info:
        await wrapper.dispatch(_binding(), _step(), step_context=_step_context())

    # Carries the last-failed candidate for attribution.
    assert exc_info.value.failed.provider == "anthropic"
    assert exc_info.value.failed.model == "claude-test-2"
    # Maps to the RT-FAIL-FALLBACK-EXHAUSTED token.
    assert "RT-FAIL-FALLBACK-EXHAUSTED" in str(exc_info.value)

    # Outer span carries the fallback.exhausted event.
    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    event_names = [e.name for e in outer.events]
    assert "fallback.exhausted" in event_names
    exhausted_event = next(e for e in outer.events if e.name == "fallback.exhausted")
    assert exhausted_event.attributes is not None
    assert exhausted_event.attributes["fallback.chain_length"] == 2


@pytest.mark.asyncio
async def test_payload_shape_error_treated_as_fail_fast() -> None:
    """``LLMDispatchPayloadShapeError`` is fail-fast per D2 — the candidate
    is abandoned without consuming the retry budget."""
    primary = _candidate("anthropic", "claude-test-1")
    same_family = (_candidate("anthropic", "claude-test-2"),)
    chain = _chain(primary, same_family=same_family)
    breaker = _retry_breaker_with_llm_policy(max_attempts=5)
    inner = _MockInnerDispatcher(
        outcomes=[
            LLMDispatchPayloadShapeError("missing messages key"),
            {"result": "candidate-1-ok"},
        ]
    )
    tp, _ = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    result = await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    assert result == {"result": "candidate-1-ok"}
    # Exactly 2 inner calls: one fail-fast on candidate 0; one success on candidate 1.
    # Even though max_attempts=5, fail-fast doesn't burn the budget.
    assert len(inner.calls) == 2


# ---------------------------------------------------------------------------
# AC #6 — Breaker pre-check + harness.breaker.* emission.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_breaker_open_skips_candidate_emits_retry_skipped() -> None:
    """An OPEN breaker on candidate 0 causes the wrapper to emit
    ``retry.skipped`` and advance to candidate 1 without invoking the inner
    dispatcher for candidate 0."""
    primary = _candidate("anthropic", "claude-test-1")
    same_family = (_candidate("anthropic", "claude-test-2"),)
    chain = _chain(primary, same_family=same_family)
    breaker = _retry_breaker_with_llm_policy(max_attempts=3)

    # Pre-trip candidate-0's breaker to OPEN.
    pre_breaker = breaker.get_breaker(BreakerScope.PER_MODEL, "anthropic:claude-test-1")
    pre_breaker.state = pre_breaker.state.__class__("open")  # set to OPEN
    assert pre_breaker.should_attempt() is False

    inner = _MockInnerDispatcher(outcomes=[{"result": "candidate-1-ok"}])
    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    result = await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    assert result == {"result": "candidate-1-ok"}
    # Inner was called only for candidate 1 (candidate 0 was skipped).
    assert len(inner.calls) == 1
    assert inner.calls[0][0].model_binding.model == "claude-test-2"

    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    event_names = [e.name for e in outer.events]
    assert "retry.skipped" in event_names
    skipped = next(e for e in outer.events if e.name == "retry.skipped")
    assert skipped.attributes is not None
    assert skipped.attributes["retry.skipped.reason"] == "breaker-open"
    assert skipped.attributes["retry.skipped.candidate"] == "anthropic:claude-test-1"


@pytest.mark.asyncio
async def test_breaker_transition_emitted_via_registry() -> None:
    """When the breaker trips CLOSED → OPEN after the fail-threshold, the
    composer invokes ``RuntimeRetryBreaker.emit_breaker_transition_event``."""
    # Use a per-test registry with fail_threshold=1 → first failure trips.
    breaker = RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=1, backoff="full_jitter", jitter="full_jitter"
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        fail_threshold=1,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )

    # Spy on emit_breaker_transition_event via a wrapper (slots dataclass
    # disallows monkey-patching; we wrap the registry instead).
    emissions: list[BreakerTransition] = []

    @dataclass
    class _SpyingRegistry:
        inner: RuntimeRetryBreaker

        def get_policy(self, tool_name: str) -> RetryPolicy:
            return self.inner.get_policy(tool_name)

        def get_breaker(self, scope: BreakerScope, identifier: str) -> BreakerStateMachine:
            return self.inner.get_breaker(scope, identifier)

        def compute_delay_seconds(self, attempt: int, rng: Any | None = None) -> float:
            return self.inner.compute_delay_seconds(attempt, rng)

        def advance_staircase(self, current: Any, cause: Any, attempt: int) -> Any:
            return self.inner.advance_staircase(current, cause, attempt)

        def emit_breaker_transition_event(
            self, transition: Any, parent_span_ref: Any, **kwargs: Any
        ) -> Any:
            emissions.append(transition)
            return self.inner.emit_breaker_transition_event(transition, parent_span_ref, **kwargs)

    spying = _SpyingRegistry(inner=breaker)

    primary = _candidate("anthropic", "claude-test-1")
    same_family = (_candidate("anthropic", "claude-test-2"),)
    chain = _chain(primary, same_family=same_family)
    inner = _MockInnerDispatcher(
        outcomes=[
            LLMDispatchProviderUnreachableError("anthropic"),  # fail-fast → record_failure
            {"result": "candidate-1-ok"},
        ]
    )
    tp, _ = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=spying,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    # One emission (candidate 0's breaker CLOSED → OPEN on first failure
    # because fail_threshold=1).
    assert len(emissions) == 1
    assert emissions[0].to_state.value == "open"


# ---------------------------------------------------------------------------
# AC #7 — Nested-span hierarchy verified via parent-span-id linkage.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_nested_span_hierarchy_outer_parent_of_attempts() -> None:
    """Per-attempt ``harness.runtime.retry_attempt`` spans nest inside the
    outer ``harness.runtime.retry_breaker_fallback`` span."""
    primary = _candidate("anthropic", "claude-test-1")
    chain = _chain(primary)
    breaker = _retry_breaker_with_llm_policy(max_attempts=2)
    inner = _MockInnerDispatcher(
        outcomes=[
            RuntimeError("transient attempt 0"),
            {"result": "ok"},
        ]
    )
    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    attempts = [s for s in spans if s.name == "harness.runtime.retry_attempt"]
    assert len(attempts) == 2
    for attempt in attempts:
        assert attempt.parent is not None
        assert attempt.parent.span_id == outer.context.span_id


# ---------------------------------------------------------------------------
# AC #8 — Reserved registry key + ReservedToolNameError at validation.
# ---------------------------------------------------------------------------


def test_reserved_registry_key_populated_after_bootstrap() -> None:
    """``materialize_retry_breaker_stage`` injects the reserved
    ``"llm_dispatch"`` key into the registry's policy map."""
    manifest = RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(_chain(_candidate("anthropic", "claude-test-1")),),
        retry_policies={},  # no operator override
    )
    config = _runtime_config(manifest)
    stage = materialize_retry_breaker_stage(config)
    policy = stage.registry.get_policy(RESERVED_LLM_DISPATCH_KEY)
    assert policy.max_attempts == DEFAULT_LLM_DISPATCH_RETRY_POLICY.max_attempts
    assert policy.backoff == DEFAULT_LLM_DISPATCH_RETRY_POLICY.backoff


def test_reserved_tool_name_error_on_operator_supplied_key() -> None:
    """Operator-supplied ``"llm_dispatch"`` in ``retry_policies`` raises
    ``ReservedToolNameError`` at manifest validation time."""
    manifest = RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(_chain(_candidate("anthropic", "claude-test-1")),),
        retry_policies={
            "llm_dispatch": RetryPolicy(
                max_attempts=99, backoff="full_jitter", jitter="full_jitter"
            )
        },
    )
    with pytest.raises(ReservedToolNameError) as exc_info:
        validate_routing_manifest(manifest)
    assert exc_info.value.reserved_name == "llm_dispatch"


def test_valid_manifest_passes_with_non_reserved_tool_names() -> None:
    """Non-reserved tool names in ``retry_policies`` do not raise."""
    manifest = RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(_chain(_candidate("anthropic", "claude-test-1")),),
        retry_policies={
            "my_tool": RetryPolicy(max_attempts=2, backoff="full_jitter", jitter="full_jitter")
        },
    )
    assert validate_routing_manifest(manifest) is None


# ---------------------------------------------------------------------------
# AC #9 — Bootstrap stage 5 wrap.
# ---------------------------------------------------------------------------


def test_materialize_factory_wraps_inner_dispatcher() -> None:
    """The factory returns a wrapper whose ``.inner`` is the bare
    ``RuntimeLLMDispatcher``."""
    tp, _ = _tracer_provider_with_exporter()
    providers: dict[str, Any] = {"anthropic": object()}
    bare = RuntimeLLMDispatcher(providers=providers, tracer_provider=tp)

    breaker = _retry_breaker_with_llm_policy()
    chain = _chain(_candidate("anthropic", "claude-test-1"))
    wrapper = materialize_retry_breaker_fallback_dispatcher_stage(
        inner=bare,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
    )
    assert isinstance(wrapper, RetryBreakerFallbackDispatcher)
    assert isinstance(wrapper, StepDispatcher)
    assert wrapper.inner is bare


# ---------------------------------------------------------------------------
# Defensive — degenerate fallback chain (single primary) fails closed.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_candidate_chain_fail_fast_exhausts() -> None:
    """A 1-candidate chain whose only candidate fails-fast exhausts
    immediately."""
    primary = _candidate("anthropic", "claude-test-1")
    chain = _chain(primary)
    breaker = _retry_breaker_with_llm_policy(max_attempts=1)
    inner = _MockInnerDispatcher(outcomes=[LLMDispatchProviderUnreachableError("anthropic")])
    tp, _ = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding(), _step(), step_context=_step_context())


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _runtime_config(manifest: RoutingManifest) -> Any:
    """Construct a minimal ``RuntimeConfig`` with the given manifest.

    Tests that only need ``materialize_retry_breaker_stage`` don't require
    the full config — they need ``config.routing_manifest`` reachable."""

    @dataclass(frozen=True)
    class _MinimalConfig:
        routing_manifest: RoutingManifest

    return _MinimalConfig(routing_manifest=manifest)


# ---------------------------------------------------------------------------
# R-CL-P1 — C-CP-03 §3.3 capability-shortfall fallback (capability-preservation).
# ---------------------------------------------------------------------------


def _thinking_step() -> WorkflowStep:
    """An INFERENCE_STEP whose payload requests extended thinking.

    ``params["thinking"]`` set -> the call requires the ``THINKING`` provider
    capability per ``_required_capabilities`` (C-CP-03 §3.3 derivation)."""
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "think hard"}],
            "tools": None,
            "params": {"thinking": {"type": "enabled", "budget_tokens": 4096}},
        },
    )


def test_required_capabilities_derivation() -> None:
    """``_required_capabilities`` maps the payload to the C-CP-01 §1.2 capability
    discriminators: ``tools`` -> TOOLS, ``params['thinking']`` -> THINKING."""
    # Neither tools nor thinking -> empty (the common path; pre-check no-op).
    assert _required_capabilities(_step()) == frozenset()
    # thinking param -> THINKING.
    assert _required_capabilities(_thinking_step()) == frozenset({ProviderCapability.THINKING})
    # tools present -> TOOLS.
    tools_step = WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "use a tool"}],
            "tools": [{"name": "calc"}],
            "params": {},
        },
    )
    assert _required_capabilities(tools_step) == frozenset({ProviderCapability.TOOLS})
    # both -> {TOOLS, THINKING}.
    both_step = WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "x"}],
            "tools": [{"name": "calc"}],
            "params": {"thinking": {"type": "enabled"}},
        },
    )
    assert _required_capabilities(both_step) == frozenset(
        {ProviderCapability.TOOLS, ProviderCapability.THINKING}
    )


@pytest.mark.asyncio
async def test_capability_shortfall_skips_incapable_primary_before_provider_call() -> None:
    """A thinking step at a non-thinking primary advances to a thinking-capable
    cross-family candidate WITHOUT calling the incapable provider (C-CP-03 §3.3
    advance-before-error). Uses the *real* runtime model-ID shape
    ``claude-opus-4-7`` (the Anthropic extended-thinking tier per
    ``reflect_provider_capabilities.supports_thinking``) — not the short §13.4
    token — so the test exercises the format runtime bindings actually carry."""
    primary = _candidate("openai", "gpt-test-1")  # supports_thinking == False
    cross_family = (_candidate("anthropic", "claude-opus-4-7"),)  # supports_thinking == True
    chain = _chain(primary, cross_family=cross_family)
    breaker = _retry_breaker_with_llm_policy(max_attempts=1)
    # One inner call expected — the capable anthropic candidate. The incapable
    # openai primary must be skipped before any provider dispatch.
    inner = _MockInnerDispatcher(outcomes=[{"result": "thinking-ok"}])
    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    result = await wrapper.dispatch(_binding(), _thinking_step(), step_context=_step_context())
    assert result == {"result": "thinking-ok"}

    # The incapable primary was NEVER dispatched; only the capable candidate.
    assert len(inner.calls) == 1
    assert inner.calls[0][0].model_binding.provider == "anthropic"
    assert inner.calls[0][0].model_binding.model == "claude-opus-4-7"

    # Outer span carries the §3.3 fallback.triggered (capability_shortfall) event.
    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    triggered = [e for e in outer.events if e.name == "fallback.triggered"]
    assert len(triggered) == 1
    attrs = triggered[0].attributes
    assert attrs is not None
    assert attrs["fallback.cause"] == "capability_shortfall"
    assert attrs["fallback.from_provider"] == "openai"
    assert attrs["fallback.from_model"] == "gpt-test-1"
    assert attrs["fallback.required_capability"] == "thinking"


@pytest.mark.asyncio
async def test_capability_shortfall_exhausts_when_no_capable_candidate() -> None:
    """A thinking step with no thinking-capable candidate fails-closed
    (``RetryBreakerFallbackExhaustedError``) WITHOUT any provider call — the
    capability-preservation guarantee: better to fail than silently serve a
    thinking step on a non-thinking model (§3.2 step 3 / §3.3)."""
    primary = _candidate("openai", "gpt-test-1")  # no thinking
    cross_family = (_candidate("ollama", "llama-test-1"),)  # no thinking
    chain = _chain(primary, cross_family=cross_family)
    breaker = _retry_breaker_with_llm_policy(max_attempts=1)
    inner = _MockInnerDispatcher(outcomes=[])  # must never be called
    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding(), _thinking_step(), step_context=_step_context())

    # No provider was ever dispatched (both candidates skipped pre-call).
    assert len(inner.calls) == 0
    # Two capability_shortfall triggers + a terminal fallback.exhausted.
    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    triggered = [e for e in outer.events if e.name == "fallback.triggered"]
    assert len(triggered) == 2
    assert all(e.attributes["fallback.cause"] == "capability_shortfall" for e in triggered)
    # The terminal fallback.exhausted attributes the shortfall cause, NOT
    # retry-exhaustion (no provider attempt ran) — accurate failure-mode telemetry.
    exhausted = next(e for e in outer.events if e.name == "fallback.exhausted")
    assert exhausted.attributes is not None
    assert exhausted.attributes["fallback.exhaustion_cause"] == "capability-shortfall"
    assert exhausted.attributes["fallback.last_failure_class"] == "capability-shortfall"


@pytest.mark.asyncio
async def test_no_capability_requirement_is_behavior_neutral() -> None:
    """A step with no tools + no thinking param derives an empty capability set;
    the §3.3 pre-check is a no-op and the primary dispatches normally — the
    no-regression guard for the common path (existing fixtures use
    ``params:{max_tokens:…}``)."""
    primary = _candidate("openai", "gpt-test-1")  # would shortfall IF thinking required
    chain = _chain(primary)
    breaker = _retry_breaker_with_llm_policy(max_attempts=1)
    inner = _MockInnerDispatcher(outcomes=[{"result": "ok"}])
    tp, exporter = _tracer_provider_with_exporter()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=tp,
        sleep_fn=_noop_sleep,
    )

    result = await wrapper.dispatch(_binding(), _step(), step_context=_step_context())
    assert result == {"result": "ok"}
    assert len(inner.calls) == 1
    assert inner.calls[0][0].model_binding.provider == "openai"
    # No capability-shortfall event emitted.
    spans = exporter.get_finished_spans()
    outer = next(s for s in spans if s.name == "harness.runtime.retry_breaker_fallback")
    assert "fallback.triggered" not in [e.name for e in outer.events]

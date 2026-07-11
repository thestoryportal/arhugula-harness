"""B-18-3C-PREWARM-COHORTKEY — unit witnesses for `CohortKeyCapable` delegation chain.

Tests `RuntimeLLMDispatcher.cohort_key()` in isolation plus the delegation stubs on
the three runtime wrappers that sit above it in the production dispatcher chain:
`RuntimeHITLGateComposer → RetryBreakerFallbackDispatcher → SyncDispatcherFacade`.

Acceptance-criterion coverage (DDR §11.5; fork doc §3):

  RK-1  `RuntimeLLMDispatcher.cohort_key()` returns a 16-hex-char string when
        cache-stable (frozen_tool_superset not None, memory_runtime None).
  RK-2  Returns None when `memory_runtime is not None`.
  RK-3  Returns None when `frozen_tool_superset is None`.
  RK-4  Same parameters → identical key (deterministic hash).
  RK-5  Different `thinking` values → different keys.
  RK-6  Different providers → different keys.
  RK-7  `SyncDispatcherFacade.cohort_key()` delegates to CohortKeyCapable inner.
  RK-8  `SyncDispatcherFacade.cohort_key()` returns None for non-capable inner.
  RK-9  `RetryBreakerFallbackDispatcher.cohort_key()` delegates to CohortKeyCapable inner.
  RK-10 `RetryBreakerFallbackDispatcher.cohort_key()` returns None for non-capable inner.
  RK-11 `RuntimeHITLGateComposer.cohort_key()` delegates to CohortKeyCapable inner.
  RK-12 `RuntimeHITLGateComposer.cohort_key()` returns None for non-capable inner.
  RK-13 Full production chain: SyncDispatcherFacade → RetryBreakerFallbackDispatcher →
        RuntimeHITLGateComposer → RuntimeLLMDispatcher delivers the bottom-layer hash.

Authority: `.harness/class_2_fork_b18_cohortkey_fork_a_vs_b.md`;
`Spec_Control_Plane_v1_88.md` §25.15–§25.16.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping
from typing import Any, cast

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
from harness_cp.hitl_placement import HITLPlacementKind
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.workflow_driver import CohortKeyCapable
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.lifecycle.retry_breaker import (
    DEFAULT_RETRY_POLICY,
    RuntimeRetryBreaker,
)
from harness_runtime.lifecycle.retry_breaker_fallback import (
    RESERVED_LLM_DISPATCH_KEY,
    RetryBreakerFallbackDispatcher,
)
from harness_runtime.lifecycle.sync_dispatcher_facade import SyncDispatcherFacade
from opentelemetry.trace import NoOpTracerProvider

# ---------------------------------------------------------------------------
# Shared stubs
# ---------------------------------------------------------------------------

_PROVIDER = "anthropic"
_MODEL = "claude-haiku-4-5"
_FTS: tuple[Mapping[str, Any], ...] = (
    {"type": "function", "name": "test_tool", "description": "d", "input_schema": {}},
)


def _binding(
    *,
    provider: str = _PROVIDER,
    model: str = _MODEL,
) -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider=provider, model=model),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step(*, thinking: bool | None = None) -> WorkflowStep:
    payload: dict[str, Any] = {"messages": [{"role": "user", "content": "hi"}]}
    if thinking is not None:
        payload["params"] = {"thinking": thinking}
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload=payload,
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-rt"),
        parent_entry_hash="",
        parent_idempotency_key="test-key",
        tenant_id=None,
        step_index=0,
    )


def _llm_dispatcher(
    *,
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = _FTS,
    memory_runtime: Any = None,
) -> RuntimeLLMDispatcher:
    return RuntimeLLMDispatcher(
        providers={},
        tracer_provider=NoOpTracerProvider(),
        frozen_tool_superset=frozen_tool_superset,
        memory_runtime=memory_runtime,
    )


def _chain(provider: str = _PROVIDER) -> FallbackChain:
    return FallbackChain(
        primary=ProviderCandidate(
            provider=provider,
            model=_MODEL,
            family=ProviderFamily.ANTHROPIC,
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )


def _retry_breaker() -> RuntimeRetryBreaker:
    return RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=1,
                backoff="full_jitter",
                jitter="full_jitter",
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )


# A stub that IS CohortKeyCapable (has cohort_key method).
class _CohortKeyCapableStub:
    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "stub-cohort-key"

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        return {}


# A stub that is NOT CohortKeyCapable (no cohort_key method).
class _NonCapableStub:
    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        return {}


# ---------------------------------------------------------------------------
# RK-1 through RK-6 — RuntimeLLMDispatcher.cohort_key()
# ---------------------------------------------------------------------------


def test_cohort_key_returns_16hex_string() -> None:
    """RK-1: basic return is a 16-char lowercase hex string."""
    disp = _llm_dispatcher()
    key = disp.cohort_key(_binding(), _step())
    assert key is not None
    assert len(key) == 16
    assert re.fullmatch(r"[0-9a-f]{16}", key), f"not hex: {key!r}"


def test_cohort_key_memory_runtime_bound_returns_none() -> None:
    """RK-2: memory_runtime is not None → returns None (prefix unstable)."""
    disp = _llm_dispatcher(memory_runtime=object())
    assert disp.cohort_key(_binding(), _step()) is None


def test_cohort_key_no_frozen_tool_superset_returns_none() -> None:
    """RK-3: frozen_tool_superset is None → returns None (no stable cache marker)."""
    disp = _llm_dispatcher(frozen_tool_superset=None)
    assert disp.cohort_key(_binding(), _step()) is None


def test_cohort_key_deterministic() -> None:
    """RK-4: same dispatcher + same params → identical key on repeated calls."""
    disp = _llm_dispatcher()
    b = _binding()
    s = _step()
    key_a = disp.cohort_key(b, s)
    key_b = disp.cohort_key(b, s)
    assert key_a is not None
    assert key_a == key_b


def test_cohort_key_different_thinking_different_keys() -> None:
    """RK-5: thinking=True vs thinking=None → different hash → different keys."""
    disp = _llm_dispatcher()
    b = _binding()
    key_thinking = disp.cohort_key(b, _step(thinking=True))
    key_plain = disp.cohort_key(b, _step())
    assert key_thinking is not None
    assert key_plain is not None
    assert key_thinking != key_plain


def test_cohort_key_different_providers_different_keys() -> None:
    """RK-6: different provider value in binding → different keys."""
    disp = _llm_dispatcher()
    key_anthropic = disp.cohort_key(_binding(provider="anthropic"), _step())
    key_openai = disp.cohort_key(_binding(provider="openai"), _step())
    assert key_anthropic is not None
    assert key_openai is not None
    assert key_anthropic != key_openai


# ---------------------------------------------------------------------------
# RK-7 through RK-8 — SyncDispatcherFacade.cohort_key()
# ---------------------------------------------------------------------------


def test_sync_facade_delegates_cohort_key_to_capable_inner() -> None:
    """RK-7: SyncDispatcherFacade with CohortKeyCapable inner delegates correctly."""
    loop = asyncio.new_event_loop()
    try:
        inner = _CohortKeyCapableStub()
        facade = SyncDispatcherFacade(
            inner=cast(Any, inner),
            loop=loop,
            result_timeout_seconds=30.0,
        )
        assert isinstance(facade, CohortKeyCapable)
        key = facade.cohort_key(_binding(), _step())
        assert key == "stub-cohort-key"
    finally:
        loop.close()


def test_sync_facade_non_capable_inner_returns_none() -> None:
    """RK-8: SyncDispatcherFacade with non-CohortKeyCapable inner returns None."""
    loop = asyncio.new_event_loop()
    try:
        inner = _NonCapableStub()
        facade = SyncDispatcherFacade(
            inner=cast(Any, inner),
            loop=loop,
            result_timeout_seconds=30.0,
        )
        assert isinstance(facade, CohortKeyCapable)
        key = facade.cohort_key(_binding(), _step())
        assert key is None
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# RK-9 through RK-10 — RetryBreakerFallbackDispatcher.cohort_key()
# ---------------------------------------------------------------------------


async def _noop_sleep(_s: float) -> None:
    pass


def test_retry_breaker_delegates_cohort_key_to_capable_inner() -> None:
    """RK-9: RetryBreakerFallbackDispatcher with CohortKeyCapable inner delegates."""
    inner = _CohortKeyCapableStub()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=cast(Any, inner),
        retry_breaker=_retry_breaker(),
        fallback_chain=_chain(),
        tracer_provider=NoOpTracerProvider(),
        sleep_fn=_noop_sleep,
    )
    assert isinstance(wrapper, CohortKeyCapable)
    key = wrapper.cohort_key(_binding(), _step())
    assert key == "stub-cohort-key"


def test_retry_breaker_non_capable_inner_returns_none() -> None:
    """RK-10: RetryBreakerFallbackDispatcher with non-CohortKeyCapable inner returns None."""
    inner = _NonCapableStub()
    wrapper = RetryBreakerFallbackDispatcher(
        inner=cast(Any, inner),
        retry_breaker=_retry_breaker(),
        fallback_chain=_chain(),
        tracer_provider=NoOpTracerProvider(),
        sleep_fn=_noop_sleep,
    )
    assert isinstance(wrapper, CohortKeyCapable)
    key = wrapper.cohort_key(_binding(), _step())
    assert key is None


# ---------------------------------------------------------------------------
# RK-11 through RK-12 — RuntimeHITLGateComposer.cohort_key()
# ---------------------------------------------------------------------------


def _hitl_composer(inner: Any) -> RuntimeHITLGateComposer:
    return RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(Any, None),
        ledger_writer=cast(Any, None),
        audit_writer=cast(Any, None),
        tracer_provider=NoOpTracerProvider(),
        audit_signing_key_id="test-key-id",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: cast(Any, None),
    )


def test_hitl_composer_delegates_cohort_key_to_capable_inner() -> None:
    """RK-11: RuntimeHITLGateComposer with CohortKeyCapable inner delegates correctly."""
    composer = _hitl_composer(_CohortKeyCapableStub())
    assert isinstance(composer, CohortKeyCapable)
    key = composer.cohort_key(_binding(), _step())
    assert key == "stub-cohort-key"


def test_hitl_composer_non_capable_inner_returns_none() -> None:
    """RK-12: RuntimeHITLGateComposer with non-CohortKeyCapable inner returns None."""
    composer = _hitl_composer(_NonCapableStub())
    assert isinstance(composer, CohortKeyCapable)
    key = composer.cohort_key(_binding(), _step())
    assert key is None


# ---------------------------------------------------------------------------
# RK-13 — full production chain end-to-end witness
# ---------------------------------------------------------------------------


def test_full_production_chain_delegates_cohort_key() -> None:
    """RK-13: The assembled production chain delivers the bottom-layer hash.

    Mirrors the production stack at inference-step dispatch:
        SyncDispatcherFacade
          → RetryBreakerFallbackDispatcher
          → RuntimeHITLGateComposer
          → RuntimeLLMDispatcher

    Calling `.cohort_key()` on the outer SyncDispatcherFacade must propagate
    through all three wrappers and return the same 16-hex key as the bottom-level
    `RuntimeLLMDispatcher.cohort_key()` call.  A silent isinstance=False at any
    intermediate hop would return None instead — this test catches that.
    """
    binding = _binding()
    step = _step()

    # Bottom: the real dispatcher that computes the hash.
    llm_disp = _llm_dispatcher()  # frozen_tool_superset=_FTS, memory_runtime=None
    expected_key = llm_disp.cohort_key(binding, step)
    assert expected_key is not None, "pre-condition: LLM dispatcher must produce a key"

    # Assemble the production wrapper chain (inner → outer).
    hitl = _hitl_composer(llm_disp)
    rbf = RetryBreakerFallbackDispatcher(
        inner=cast(Any, hitl),
        retry_breaker=_retry_breaker(),
        fallback_chain=_chain(),
        tracer_provider=NoOpTracerProvider(),
        sleep_fn=_noop_sleep,
    )
    loop = asyncio.new_event_loop()
    try:
        facade = SyncDispatcherFacade(
            inner=rbf,
            loop=loop,
            result_timeout_seconds=30.0,
        )
        # The CP driver calls cohort_key() on whatever SyncDispatcherFacade wraps.
        assert isinstance(facade, CohortKeyCapable)
        chain_key = facade.cohort_key(binding, step)
        assert chain_key is not None, "full chain must not return None (warmup would never fire)"
        assert chain_key == expected_key, f"chain returned {chain_key!r}, expected {expected_key!r}"
    finally:
        loop.close()

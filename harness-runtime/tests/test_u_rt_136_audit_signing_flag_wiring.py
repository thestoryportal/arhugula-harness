"""`U-RT-136` ⊕ `U-CP-73` — ten-site flag-consult wiring + post-effect
carrier + catch-ordering fence witnesses (runtime halves).

Implements `Implementation_Plan_Harness_Runtime_v2_49.md` §1.3 (Runtime spec
v1.101 surface D; OD v1.34 §21.2.3 rows 1/5/7; CP v1.101 §2). The plan-named
witnesses here:

- `test_each_of_ten_handler_sites_raises_under_flag_on_and_logs_under_off`
  (parametrized over the ten `except AUDIT_SIGNING_HARD_FAILURES` sites);
- `test_post_effect_failure_carrier_preserves_result` (acc 1b — the carrier
  through the REAL `RuntimeLLMDispatcher.dispatch` path);
- `test_post_effect_fence_ahead_of_classifier_at_every_site_class_result_preserved`
  (acc 3 / CP witness (e) runtime half — the LLM per-candidate classifier and
  the tool retry wrapper; the webhook + sub-agent site-class carriers are
  witnessed in their own lifecycle test files, reusing those fixtures).

Site-class carrier siblings (same-arc, other files):
`test_lifecycle_webhook_delivery_composer.py::test_u_rt_136_*`,
`test_lifecycle_sub_agent_dispatch.py::test_u_rt_136_*`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, cast

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
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_runtime.lifecycle.audit_signing_errors import (
    AUDIT_SIGNING_HARD_FAILURES,
    AuditSigningFailedError,
    PostEffectAuditSigningError,
    PostEffectClass,
)
from harness_runtime.lifecycle.retry_breaker import BreakerStateMachine
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_AUDIT_LOGGER = "harness.runtime.audit_signing"


def _family_exc() -> AuditSigningFailedError:
    return AuditSigningFailedError("kms unavailable (u-rt-136 test)")


async def _raise_family_offload(*_a: Any, **_k: Any) -> Any:
    raise _family_exc()


def _raise_family_sync(*_a: Any, **_k: Any) -> Any:
    raise _family_exc()


def _tp() -> TracerProvider:
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
    return tp


def _span_stub() -> Any:
    return SimpleNamespace(
        get_span_context=lambda: SimpleNamespace(span_id=1),
        set_attribute=lambda *_a, **_k: None,
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf-136",
        parent_action_id="workflow:test-wf-136:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-u-rt-136"),
        parent_entry_hash="",
        parent_idempotency_key="u136-idem",
        tenant_id=None,
        step_index=0,
    )


class _MockLedgerWriter:
    def __init__(self, *, raise_family: bool = False) -> None:
        self.raise_family = raise_family
        self.appends: list[Any] = []

    def append(self, payload: Any, key: Any) -> Any:
        if self.raise_family:
            raise _family_exc()
        self.appends.append((payload, key))
        return ("entry-hash", payload, key)


class _MockAuditWriter:
    def __init__(self, *, raise_family: bool = False) -> None:
        self.raise_family = raise_family
        self.appends: list[Any] = []

    def append(self, *, tenant_id: Any, audit_entry: Any) -> Any:
        if self.raise_family:
            raise _family_exc()
        self.appends.append((tenant_id, audit_entry))
        return ("write-result", audit_entry)


# ---------------------------------------------------------------------------
# The ten site triggers. Each returns an awaitable that drives the REAL
# module code containing that `except AUDIT_SIGNING_HARD_FAILURES` arm with a
# family raise reaching it. Under flag OFF each must complete (the
# loudly-surfaced ERROR-logged proceed, byte-preserved); under flag ON each
# must re-raise a member of the typed family.
# ---------------------------------------------------------------------------


async def _site_hitl_offload(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.hitl_gate_composer as hitl_mod

    monkeypatch.setattr(hitl_mod, "run_audit_off_loop", _raise_family_offload)
    composer = hitl_mod.RuntimeHITLGateComposer.__new__(hitl_mod.RuntimeHITLGateComposer)
    composer.audit_signing_fail_closed = flag
    # raise_on_failure=False is the arm under test — the True arm already
    # raised (as HITLGateAuditComposeError) before this unit.
    result = await hitl_mod.RuntimeHITLGateComposer._compose_and_persist_audit_off_loop(
        composer, raise_on_failure=False
    )
    assert result == (None, None)


def _hitl_composer(*, flag: bool, ledger: _MockLedgerWriter) -> Any:
    from harness_od.audit_ledger_types import SignatureAlgorithm
    from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer

    return RuntimeHITLGateComposer(
        inner=cast(Any, object()),
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(Any, object()),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, _MockAuditWriter()),
        tracer_provider=_tp(),
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        audit_signing_fail_closed=flag,
    )


async def _site_hitl_direct(_monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    composer = _hitl_composer(flag=flag, ledger=_MockLedgerWriter(raise_family=True))
    cp_entry, write_result = composer._compose_and_persist_audit(
        parent_action_id=cast(Any, "workflow:test-wf-136:step:0"),
        placement=HITLPlacement(position=HITLPlacementKind.PRE_ACTION),
        cell=cast(Any, None),
        gate_result=None,
        step_context=_step_context(),
        raise_on_failure=False,
        auto_approved=True,
    )
    assert cp_entry is not None
    assert write_result is None


async def _site_sub_agent_direct(_monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    from harness_runtime.lifecycle.sub_agent_dispatch import RuntimeSubAgentDispatcher

    dispatcher = RuntimeSubAgentDispatcher.__new__(RuntimeSubAgentDispatcher)
    dispatcher.handoff_registry = cast(
        Any,
        SimpleNamespace(
            dispatch_response_hash=lambda _b: "0" * 64,
            compose_dispatch_audit=lambda **_k: SimpleNamespace(),
        ),
    )
    dispatcher.ledger_writer = cast(Any, _MockLedgerWriter(raise_family=True))
    dispatcher.procedural_tier_snapshot_resolver = lambda: Identifier("b" * 64)
    dispatcher.audit_signing_fail_closed = flag
    payload = SimpleNamespace(brief=object(), child_workflow_id="child-wf")
    descent = SimpleNamespace()
    cp_entry, write_result = dispatcher._compose_and_persist_audit(
        parent_action_id=cast(Any, "workflow:test-wf-136:step:0"),
        descent=descent,
        payload=cast(Any, payload),
        step_context=_step_context(),
        raise_on_failure=False,
    )
    assert cp_entry is not None
    assert write_result is None


def _webhook_composer(*, flag: bool) -> Any:
    from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryComposer

    return WebhookDeliveryComposer(
        retry_max_attempts=1,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        workflow_id="test-wf-136",
        parent_action_id="workflow:test-wf-136:step:0",
        parent_idempotency_key="u136-idem",
        audit_signing_fail_closed=flag,
    )


async def _site_webhook_offload(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.webhook_delivery_composer as webhook_mod

    monkeypatch.setattr(webhook_mod, "run_audit_off_loop", _raise_family_offload)
    assert await _webhook_composer(flag=flag)._attribute_webhook_cost_off_loop() is None


async def _site_webhook_direct(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.cost_attribution_webhook_dispatch as attr_mod

    monkeypatch.setattr(attr_mod, "attribute_webhook_dispatch_cost", _raise_family_sync)
    _webhook_composer(flag=flag)._attribute_webhook_cost_best_effort(
        url="https://ops.example.com/hitl",
        request_body={"k": "v"},
        idempotency_key="u136-idem",
    )


def _tool_dispatcher(*, flag: bool) -> Any:
    from harness_runtime.lifecycle.runtime_tool_dispatcher import RuntimeToolDispatcher

    host = SimpleNamespace(server_name="srv", tool_registry=SimpleNamespace(names=lambda: []))
    return RuntimeToolDispatcher.for_single_host(
        mcp_client_host=cast(Any, host),
        per_server_trust_evaluator=cast(Any, object()),
        mcp_namespace_emitter=cast(Any, object()),
        trust_policy=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        rate_table=cast(Any, object()),
        audit_signing_fail_closed=flag,
    )


async def _site_tool_offload(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.runtime_tool_dispatcher as tool_mod

    monkeypatch.setattr(tool_mod, "run_audit_off_loop", _raise_family_offload)
    assert await _tool_dispatcher(flag=flag)._attribute_tool_cost_off_loop() is None


async def _site_tool_direct(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.cost_attribution_tool_dispatch as attr_mod

    monkeypatch.setattr(attr_mod, "attribute_tool_dispatch_cost", _raise_family_sync)
    _tool_dispatcher(flag=flag)._attribute_tool_cost_best_effort(
        outer_span=_span_stub(),
        tool_id="echo",
        tool_args={},
        response={"ok": True},
        idempotency_key="u136-idem",
        step_context=_step_context(),
    )


def _llm_kwargs(flag: bool) -> dict[str, Any]:
    return {
        "span": _span_stub(),
        "cost_chain": object(),
        "audit_writer": object(),
        "rate_table": object(),
        "audit_signing_fail_closed": flag,
        "provider_name": "anthropic",
        "model": "m",
        "parent_idempotency_key": "k",
        "workflow_id": "w",
        "parent_action_id": "a",
        "input_tokens": 1,
        "output_tokens": 1,
        "cache_creation": None,
        "cache_read": None,
        "tenant_id": None,
    }


async def _site_llm_offload(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.llm_dispatch as llm_mod

    monkeypatch.setattr(llm_mod, "run_audit_off_loop", _raise_family_offload)
    await llm_mod._attribute_cost_off_loop_best_effort(**_llm_kwargs(flag))


async def _site_llm_direct(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.cost_attribution_llm_dispatch as attr_mod
    from harness_runtime.lifecycle.llm_dispatch import _attribute_cost_best_effort

    monkeypatch.setattr(attr_mod, "attribute_llm_dispatch_cost", _raise_family_sync)
    _attribute_cost_best_effort(**_llm_kwargs(flag))


async def _site_validator_hook(monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
    import harness_runtime.lifecycle.cost_attribution_validator_dispatch as hook_mod

    monkeypatch.setattr(hook_mod, "run_audit_off_loop", _raise_family_offload)
    hook = hook_mod.CostAttributingValidatorHook(
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        audit_signing_fail_closed=flag,
    )
    await hook.on_post_evaluate(
        step=cast(Any, SimpleNamespace(step_id="s")),
        step_context=cast(Any, _step_context()),
        evaluation=cast(
            Any,
            SimpleNamespace(
                burden_count=0,
                result=SimpleNamespace(outcome=SimpleNamespace(value="pass")),
            ),
        ),
        execution_time_ms=1.0,
    )


_TEN_SITES = [
    ("hitl_gate_composer.py offload boundary", _site_hitl_offload),
    ("hitl_gate_composer.py compose-audit", _site_hitl_direct),
    ("sub_agent_dispatch.py compose-audit", _site_sub_agent_direct),
    ("webhook_delivery_composer.py offload boundary", _site_webhook_offload),
    ("webhook_delivery_composer.py cost best-effort", _site_webhook_direct),
    ("runtime_tool_dispatcher.py offload boundary", _site_tool_offload),
    ("runtime_tool_dispatcher.py cost best-effort", _site_tool_direct),
    ("llm_dispatch.py offload boundary", _site_llm_offload),
    ("llm_dispatch.py cost best-effort", _site_llm_direct),
    ("cost_attribution_validator_dispatch.py hook", _site_validator_hook),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("site_name", "trigger"), _TEN_SITES, ids=[s for s, _ in _TEN_SITES])
async def test_each_of_ten_handler_sites_raises_under_flag_on_and_logs_under_off(
    site_name: str,
    trigger: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Acc 1 (OD v1.34 §21.2.3 rows 1/5): each of the TEN enumerated
    `except AUDIT_SIGNING_HARD_FAILURES` handler sites consults the resolved
    `audit_signing_fail_closed` — ON raises the typed family; OFF preserves
    the loudly-surfaced (ERROR-logged) proceed verbatim.

    Mutation probe (per site): deleting the site's `if ...fail_closed: raise`
    arm makes the ON leg complete without raising → FAILS here."""
    # OFF leg — completes AND the ERROR-log surfaced (loud, not silent).
    with caplog.at_level(logging.ERROR, logger=_AUDIT_LOGGER):
        await trigger(monkeypatch, False)
    assert any(r.levelno == logging.ERROR for r in caplog.records), (
        f"{site_name}: flag OFF must keep the loudly-surfaced ERROR log"
    )

    # ON leg — the typed family raises through the site.
    with pytest.raises(AUDIT_SIGNING_HARD_FAILURES):
        await trigger(monkeypatch, True)


# ---------------------------------------------------------------------------
# Acc 1b — the result-preserving post-effect carrier through the REAL
# `RuntimeLLMDispatcher.dispatch` path (provider-response effect class).
# ---------------------------------------------------------------------------


@dataclass
class _Usage:
    input_tokens: int = 10
    output_tokens: int = 5
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclass
class _ProviderResponse:
    id: str
    usage: _Usage

    def model_dump(self) -> dict[str, Any]:
        return {"id": self.id, "content": [{"text": "ok"}]}


class _AnthropicMessages:
    async def create(self, **_kwargs: Any) -> _ProviderResponse:
        return _ProviderResponse(id="msg_u136_carrier", usage=_Usage())


@dataclass
class _AnthropicFakeAdapter:
    client: Any


def _llm_dispatcher(*, flag: bool) -> Any:
    from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher

    adapter = _AnthropicFakeAdapter(SimpleNamespace(messages=_AnthropicMessages()))
    return RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        audit_signing_fail_closed=flag,
    )


def _inference_binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider="anthropic", model="test-model-1"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _inference_step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 100},
        },
    )


@pytest.mark.asyncio
async def test_post_effect_failure_carrier_preserves_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Acc 1b: a signing failure AFTER a fake completed provider response
    raises `PostEffectAuditSigningError`, and the caught carrier yields the
    ORIGINAL result object — the completed PAID effect is not discarded.

    Mutation probe: swapping the dispatch-site carrier wrap for a bare
    re-raise loses the result (`exc.result` gone / wrong type) and FAILS."""
    import harness_runtime.lifecycle.llm_dispatch as llm_mod

    async def _signing_fails(**_k: Any) -> None:
        raise _family_exc()

    monkeypatch.setattr(llm_mod, "_attribute_cost_off_loop_best_effort", _signing_fails)

    dispatcher = _llm_dispatcher(flag=True)
    with pytest.raises(PostEffectAuditSigningError) as excinfo:
        await dispatcher.dispatch(
            _inference_binding(), _inference_step(), step_context=_step_context()
        )

    carrier = excinfo.value
    assert carrier.effect_class is PostEffectClass.PROVIDER_RESPONSE
    result = cast("dict[str, Any]", carrier.result)
    assert result["id"] == "msg_u136_carrier", (
        "the carrier must yield the ORIGINAL completed provider response"
    )
    # Family membership — every existing `isinstance(exc, AUDIT_SIGNING_
    # HARD_FAILURES)` discriminator sees the carrier.
    assert isinstance(carrier, AUDIT_SIGNING_HARD_FAILURES)


# ---------------------------------------------------------------------------
# Acc 3 / CP v1.101 §2 witness (e), runtime half — the ordered fence at the
# per-attempt classifiers: never TRANSIENT_RETRY, never candidate-advance,
# never breaker-failure; result preserved on the carrier.
# ---------------------------------------------------------------------------


@dataclass
class _CarrierRaisingInner:
    """Inner dispatcher: the effect COMPLETES, then signing fails post-effect
    (the shape the real inner produces under flag ON)."""

    result_payload: dict[str, Any]
    calls: int = 0

    async def dispatch(self, *_a: Any, **_k: Any) -> Any:
        self.calls += 1
        raise PostEffectAuditSigningError(
            "audit signing failed after a completed provider response (test)",
            effect_class=PostEffectClass.PROVIDER_RESPONSE,
            result=self.result_payload,
        )


@dataclass
class _StubRegistry:
    """Registry stub returning a REAL BreakerStateMachine (the wrapper
    isinstance-narrows) plus the reserved LLM policy."""

    breaker: BreakerStateMachine
    policy: RetryPolicy = field(
        default_factory=lambda: RetryPolicy(
            max_attempts=3, backoff="full_jitter", jitter="full_jitter"
        )
    )

    def get_policy(self, _key: str) -> RetryPolicy:
        return self.policy

    def get_breaker(self, _scope: Any, _identifier: str) -> object:
        return self.breaker

    def advance_staircase(self, *_a: Any, **_k: Any) -> Any:  # pragma: no cover
        raise AssertionError("staircase must never be consulted for a fenced signing failure")

    def compute_delay_seconds(self, _attempt: int) -> float:  # pragma: no cover
        return 0.0

    def emit_breaker_transition_event(self, *_a: Any, **_k: Any) -> None:  # pragma: no cover
        return None


@pytest.mark.asyncio
async def test_post_effect_fence_ahead_of_classifier_at_every_site_class_result_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CP v1.101 §2 catch-ordering (LLM provider-response site class): the
    typed family is caught AHEAD of `_run_per_candidate_attempts`' generic
    `except Exception` classifier — a post-effect signing failure is NEVER
    `TRANSIENT_RETRY` (attempt count stays 1: no re-fired PAID call), NEVER
    candidate-advance, NEVER `record_failure`, and the carrier's result
    survives to the caller.

    Mutation probe: removing the fence arm routes the carrier into the
    generic arm → staircase consult (asserts here) / breaker record /
    retry — each FAILS this test."""
    from harness_od.harness_breaker_schema import BreakerScope
    from harness_runtime.lifecycle.retry_breaker_fallback import (
        RetryBreakerFallbackDispatcher,
    )

    breaker = BreakerStateMachine(scope=BreakerScope.PER_MODEL, identifier="anthropic:test-model-1")
    failures: list[Any] = []
    original_record_failure = BreakerStateMachine.record_failure

    def _spy_record_failure(self: BreakerStateMachine, *a: Any, **k: Any) -> Any:
        failures.append((a, k))
        return original_record_failure(self, *a, **k)

    monkeypatch.setattr(BreakerStateMachine, "record_failure", _spy_record_failure)

    inner = _CarrierRaisingInner(result_payload={"id": "msg_fence_preserved"})
    wrapper = RetryBreakerFallbackDispatcher(
        inner=cast(Any, inner),
        retry_breaker=cast(Any, _StubRegistry(breaker=breaker)),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="anthropic", model="test-model-1", family=ProviderFamily.ANTHROPIC
            ),
            same_family=(),
            cross_family=(),
            terminal=None,
        ),
        tracer_provider=_tp(),
    )

    with pytest.raises(PostEffectAuditSigningError) as excinfo:
        await wrapper.dispatch(
            _inference_binding(), _inference_step(), step_context=_step_context()
        )

    assert inner.calls == 1, "a fenced post-effect signing failure must NEVER retry"
    assert failures == [], "a fenced post-effect signing failure must NEVER record breaker failure"
    assert cast("dict[str, Any]", excinfo.value.result)["id"] == "msg_fence_preserved"


@pytest.mark.asyncio
async def test_tool_retry_wrapper_fence_ahead_of_transient_and_fail_fast_arms() -> None:
    """CP v1.101 §2 catch-ordering (tool-execution site class): the tool
    retry wrapper's fence propagates the carrier without a retry attempt and
    without stamping any staircase `retry.fail_class`."""
    from harness_runtime.lifecycle.retry_breaker_tool import RetryBreakerToolDispatcher

    inner = _CarrierRaisingInner(result_payload={"tool": "echo-result"})
    registry = SimpleNamespace(
        get_policy=lambda _k: RetryPolicy(
            max_attempts=3, backoff="full_jitter", jitter="full_jitter"
        ),
        advance_staircase=lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("staircase must never see a fenced signing failure")
        ),
        compute_delay_seconds=lambda _a: 0.0,
    )
    wrapper = RetryBreakerToolDispatcher(
        inner=cast(Any, inner),
        retry_breaker=cast(Any, registry),
        tracer_provider=_tp(),
    )
    step = WorkflowStep(
        step_id=StepID("step-tool-1"),
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": "echo", "tool_args": {}},
    )
    with pytest.raises(PostEffectAuditSigningError) as excinfo:
        await wrapper.dispatch(_inference_binding(), step, step_context=_step_context())
    assert inner.calls == 1
    assert cast("dict[str, Any]", excinfo.value.result)["tool"] == "echo-result"


# ---------------------------------------------------------------------------
# Acc 4 wiring — the composition root injects the CP carve-out + the
# flag-consulting hook ONLY under the resolved-ON policy.
# ---------------------------------------------------------------------------


def _runtime_config(tmp_path: Any, *, fail_closed_explicit: bool) -> Any:
    from harness_core.deployment_surface import DeploymentSurface
    from harness_cp.topology_pattern import TopologyPattern
    from harness_runtime.types import (
        CollectorConfig,
        OTelConfig,
        PathBindingConfig,
        ProviderSecretsConfig,
        RuntimeConfig,
        ValidatorFrameworkConfig,
    )

    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        # Solo tier + EXPLICIT true resolves ON (per-persona default is OFF
        # at solo; explicit opt-in is valid at every tier per §21.2.3 row 2)
        # — this keeps the wiring witness free of the MTC bootstrap
        # invariants (backend/tenant/record), which U-RT-134 owns.
        audit_signing_fail_closed=True if fail_closed_explicit else None,
        validator_framework_config=ValidatorFrameworkConfig(),
    )


@pytest.mark.asyncio
async def test_validator_framework_factory_injects_carve_out_only_under_resolved_on(
    tmp_path: Any,
) -> None:
    """Acc 4 (CP v1.101 §2 rows 1+3, composition-root half): the REAL
    stage-4 factory injects `AUDIT_SIGNING_HARD_FAILURES` as the CP firing
    site's raise-through tuple AND makes the hook flag-consulting under
    resolved-ON; under resolved-OFF the tuple is EMPTY (invariant 2's swallow
    unconditional) and the hook proceeds.

    Mutation probe: unconditionally injecting the family (dropping the
    flag consult at the factory) makes the OFF leg's tuple non-empty →
    FAILS."""
    from harness_runtime.bootstrap.factories.validator_framework_factory import (
        materialize_validator_framework_stage,
    )
    from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
        resolve_audit_signing_fail_closed,
    )

    on_cfg = _runtime_config(tmp_path, fail_closed_explicit=True)
    assert resolve_audit_signing_fail_closed(on_cfg) is True
    framework_on = await materialize_validator_framework_stage(
        on_cfg,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        audit_signing_fail_closed=resolve_audit_signing_fail_closed(on_cfg),
    )
    assert framework_on is not None
    assert framework_on._audit_signing_raise_through == AUDIT_SIGNING_HARD_FAILURES  # type: ignore[attr-defined]
    assert framework_on._post_evaluate_hook._audit_signing_fail_closed is True  # type: ignore[union-attr]

    off_cfg = _runtime_config(tmp_path, fail_closed_explicit=False)
    assert resolve_audit_signing_fail_closed(off_cfg) is False
    framework_off = await materialize_validator_framework_stage(
        off_cfg,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        audit_signing_fail_closed=resolve_audit_signing_fail_closed(off_cfg),
    )
    assert framework_off is not None
    assert framework_off._audit_signing_raise_through == ()  # type: ignore[attr-defined]
    assert framework_off._post_evaluate_hook._audit_signing_fail_closed is False  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_flag_on_typed_family_raises_through_real_framework_evaluate(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end through the REAL factory-built framework + REAL hook:
    under resolved-ON a signing failure inside the hook's audit offload
    raises THROUGH `ConcreteValidatorFramework.evaluate` (the §28.10.4
    invariant-2 carve-out); under resolved-OFF the same failure is
    ERROR-logged and `evaluate` returns the evaluation (invariant 2)."""
    import harness_runtime.lifecycle.cost_attribution_validator_dispatch as hook_mod
    from harness_cp.validator_framework_types import (
        ValidatorOutcome,
        ValidatorResult,
    )
    from harness_runtime.bootstrap.factories.validator_framework_factory import (
        materialize_validator_framework_stage,
    )

    monkeypatch.setattr(hook_mod, "run_audit_off_loop", _raise_family_offload)

    class _PassValidator:
        async def validate(self, _step: Any, _result: Any, *, step_context: Any) -> Any:
            _ = step_context
            return ValidatorResult(
                outcome=ValidatorOutcome.PASS,
                fail_class=None,
                cause_attribution=None,
                confidence=None,
                detail="",
            )

    async def _build(cfg: Any) -> Any:
        from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
            resolve_audit_signing_fail_closed,
        )

        framework = await materialize_validator_framework_stage(
            cfg,
            rate_table=cast(Any, object()),
            cost_chain=cast(Any, object()),
            audit_writer=cast(Any, object()),
            audit_signing_fail_closed=resolve_audit_signing_fail_closed(cfg),
        )
        assert framework is not None
        # The v1.18 factory builds an empty registry; bind one validator so
        # evaluate() reaches the hook-firing site through the real body.
        framework._validator_registry = {StepID("step-001"): _PassValidator()}  # type: ignore[attr-defined]
        return framework

    step = WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={},
    )

    framework_on = await _build(_runtime_config(tmp_path, fail_closed_explicit=True))
    with pytest.raises(AUDIT_SIGNING_HARD_FAILURES):
        await framework_on.evaluate(step, {}, step_context=_step_context())

    framework_off = await _build(_runtime_config(tmp_path, fail_closed_explicit=False))
    evaluation = await framework_off.evaluate(step, {}, step_context=_step_context())
    assert evaluation.result.outcome is ValidatorOutcome.PASS


# ---------------------------------------------------------------------------
# Acc 1b, outermost-boundary half (out-of-family Codex round-1 P1) — the
# audit-failure report at the facade + the caller-carried result reference.
# ---------------------------------------------------------------------------


def test_carrier_message_carries_effect_class_and_result_ref() -> None:
    """The CP driver stringifies step exceptions into `RunResult.fail_class`
    (it cannot import the carrier), so the caller-visible failure surface
    must carry the result REFERENCE inside the message itself — joining the
    fail_class string to the audit-failure report log line.

    Mutation probe: dropping the message suffix (or the `result_ref`
    attribute) severs the caller→report join and FAILS."""
    carrier = PostEffectAuditSigningError(
        "audit signing failed after a completed provider response (test)",
        effect_class=PostEffectClass.PROVIDER_RESPONSE,
        result={"id": "msg_ref"},
    )
    assert carrier.result_ref.startswith("post-effect-")
    assert f"result_ref={carrier.result_ref}" in str(carrier)
    assert "effect_class=provider-response" in str(carrier)


@pytest.mark.asyncio
async def test_facade_consumes_carrier_into_audit_failure_report_and_reraises(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The REAL `SyncDispatcherFacade` — the outermost runtime dispatch
    boundary every step-kind path funnels through — consumes the carrier
    into the structured audit-failure report (ERROR log keyed by
    `result_ref`, carrying the preserved payload) and re-raises it intact.

    Mutation probe: deleting the facade's carrier arm drops the report
    (no `result_ref` ERROR record) and FAILS."""
    import asyncio

    from harness_runtime.lifecycle.sync_dispatcher_facade import (
        materialize_sync_dispatcher_facade,
    )

    inner = _CarrierRaisingInner(result_payload={"id": "msg_facade_preserved"})
    facade = materialize_sync_dispatcher_facade(cast(Any, inner), result_timeout_seconds=10.0)

    with caplog.at_level(logging.ERROR, logger=_AUDIT_LOGGER):
        with pytest.raises(PostEffectAuditSigningError) as excinfo:
            await asyncio.to_thread(
                facade.dispatch,
                _inference_binding(),
                _inference_step(),
                step_context=_step_context(),
            )

    carrier = excinfo.value
    report_records = [
        r
        for r in caplog.records
        if r.levelno == logging.ERROR and carrier.result_ref in r.getMessage()
    ]
    assert report_records, "the facade must emit the result_ref-keyed audit-failure report"
    assert "msg_facade_preserved" in report_records[0].getMessage(), (
        "the report must carry the preserved effect payload"
    )
    # The re-raised carrier still holds the payload for any richer consumer.
    assert cast("dict[str, Any]", carrier.result)["id"] == "msg_facade_preserved"

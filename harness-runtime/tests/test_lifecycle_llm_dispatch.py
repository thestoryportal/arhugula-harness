"""Tests for the LLM-dispatch composer (U-RT-52, C-RT-15).

Covers per the U-RT-52 plan body acceptance criteria:

  AC #1  — Protocol satisfaction (`StepDispatcher` from CP workflow driver).
  AC #2  — Per-provider dispatch (anthropic / openai / ollama).
  AC #3  — GenAI semconv 1.41.0 span attribute emission.
  AC #4  — `anthropic.*` cache attributes — conditional on provider==anthropic.
  AC #5  — `RT-FAIL-PROVIDER-UNREACHABLE` wiring for absent provider.
  AC #6  — Async-only invariant (composer is async).
  AC #7  — Bootstrap stage 5 binding via `materialize_llm_dispatcher_stage`.

Plus a Class 3 fork residual: `RT-FAIL-PAYLOAD-SHAPE` typed error when
`step.step_payload` cannot be coerced to `ProviderAgnosticPayload`.

Test conventions follow `tests/test_lifecycle_span_processor.py` —
in-memory OTel span exporter + simple SimpleSpanProcessor for
synchronous flushing under test.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

import pytest
from harness_core import PersonaTier
from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver import StepDispatcher
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchBindError,
    LLMDispatchPayloadShapeError,
    LLMDispatchProviderUnreachableError,
    RuntimeLLMDispatcher,
    materialize_llm_dispatcher_stage,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# ---------------------------------------------------------------------------
# Fakes.
# ---------------------------------------------------------------------------


@dataclass
class _Usage:
    """Anthropic / OpenAI usage carrier — duck-typed."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    cache_read_input_tokens: int | None = None


@dataclass
class _ProviderResponse:
    """Fake provider response — exposes `.usage`, `.id`, and `model_dump()`."""

    id: str
    usage: _Usage
    _dump: dict[str, Any]

    def model_dump(self) -> dict[str, Any]:
        return self._dump


@dataclass
class _OllamaResponse:
    """Ollama returns prompt_eval_count / eval_count, no `.usage` object."""

    prompt_eval_count: int
    eval_count: int
    _dump: dict[str, Any]

    def model_dump(self) -> dict[str, Any]:
        return self._dump


class _AnthropicMessages:
    """Records kwargs of the last `create` call; returns a canned response."""

    def __init__(self) -> None:
        self.last_kwargs: dict[str, Any] | None = None
        self.canned_response = _ProviderResponse(
            id="msg_test_001",
            usage=_Usage(
                input_tokens=10,
                output_tokens=5,
                cache_creation_input_tokens=2,
                cache_read_input_tokens=3,
            ),
            _dump={"id": "msg_test_001", "content": [{"text": "ok"}]},
        )

    async def create(self, **kwargs: Any) -> _ProviderResponse:
        self.last_kwargs = kwargs
        return self.canned_response


class _AnthropicClient:
    def __init__(self) -> None:
        self.messages = _AnthropicMessages()


@dataclass
class _AnthropicFakeAdapter:
    client: _AnthropicClient


class _OpenAICompletions:
    def __init__(self) -> None:
        self.last_kwargs: dict[str, Any] | None = None
        self.canned_response = _ProviderResponse(
            id="cmpl_test_001",
            usage=_Usage(prompt_tokens=15, completion_tokens=7),
            _dump={"id": "cmpl_test_001", "choices": [{"message": {"content": "ok"}}]},
        )

    async def create(self, **kwargs: Any) -> _ProviderResponse:
        self.last_kwargs = kwargs
        return self.canned_response


class _OpenAIChat:
    def __init__(self) -> None:
        self.completions = _OpenAICompletions()


class _OpenAIClient:
    def __init__(self) -> None:
        self.chat = _OpenAIChat()


@dataclass
class _OpenAIFakeAdapter:
    client: _OpenAIClient


class _OllamaClient:
    def __init__(self) -> None:
        self.last_kwargs: dict[str, Any] | None = None
        self.canned_response = _OllamaResponse(
            prompt_eval_count=20,
            eval_count=8,
            _dump={"model": "llama3", "message": {"content": "ok"}},
        )

    async def chat(self, **kwargs: Any) -> _OllamaResponse:
        self.last_kwargs = kwargs
        return self.canned_response


@dataclass
class _OllamaFakeAdapter:
    client: _OllamaClient


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


def _binding(provider: str, model: str = "test-model-1") -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider=provider, model=model),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step(payload: dict[str, Any] | None = None) -> WorkflowStep:
    if payload is None:
        payload = {
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 100},
        }
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload=payload,
    )


def _tracer_provider_with_exporter() -> tuple[TracerProvider, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exporter))
    return tp, exporter


def _step_context(step_index: int = 0) -> StepExecutionContext:
    """Default step_context for v1.6 Path A test fixtures.

    Composes the 8-field StepExecutionContext with MVP defaults per the
    type's docstring. Tests that exercise step_context semantics override
    individual fields; the C-RT-15 inner LLM dispatcher does not consume
    step_context at v1.6, so this default is sufficient for dispatch tests.
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


# ---------------------------------------------------------------------------
# AC #1 — Protocol satisfaction.
# ---------------------------------------------------------------------------


def test_runtime_dispatcher_satisfies_step_dispatcher_protocol() -> None:
    """`RuntimeLLMDispatcher` is structurally a `StepDispatcher` per
    `harness_cp.workflow_driver.StepDispatcher` (runtime-checkable).
    """
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(_AnthropicClient())},
        tracer_provider=tp,
    )
    assert isinstance(dispatcher, StepDispatcher)


# ---------------------------------------------------------------------------
# AC #2 — Per-provider dispatch round-trip.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_anthropic_round_trip() -> None:
    """Anthropic branch calls `client.messages.create(model=..., **kwargs)`."""
    adapter = _AnthropicFakeAdapter(_AnthropicClient())
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"anthropic": adapter}, tracer_provider=tp)

    result = await dispatcher.dispatch(_binding("anthropic"), _step(), step_context=_step_context())

    assert adapter.client.messages.last_kwargs is not None
    assert adapter.client.messages.last_kwargs["model"] == "test-model-1"
    assert adapter.client.messages.last_kwargs["messages"] == [{"role": "user", "content": "hi"}]
    assert adapter.client.messages.last_kwargs["max_tokens"] == 100
    assert result["id"] == "msg_test_001"


@pytest.mark.asyncio
async def test_dispatch_openai_round_trip() -> None:
    """OpenAI branch calls `client.chat.completions.create(...)`."""
    adapter = _OpenAIFakeAdapter(_OpenAIClient())
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"openai": adapter}, tracer_provider=tp)

    result = await dispatcher.dispatch(_binding("openai"), _step(), step_context=_step_context())

    assert adapter.client.chat.completions.last_kwargs is not None
    assert adapter.client.chat.completions.last_kwargs["model"] == "test-model-1"
    assert result["id"] == "cmpl_test_001"


@pytest.mark.asyncio
async def test_dispatch_ollama_round_trip() -> None:
    """Ollama branch calls `client.chat(...)`."""
    adapter = _OllamaFakeAdapter(_OllamaClient())
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"ollama": adapter}, tracer_provider=tp)

    result = await dispatcher.dispatch(_binding("ollama"), _step(), step_context=_step_context())

    assert adapter.client.last_kwargs is not None
    assert adapter.client.last_kwargs["model"] == "test-model-1"
    assert result["message"]["content"] == "ok"


# ---------------------------------------------------------------------------
# AC #3 — GenAI semconv span attributes.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_genai_span_emits_required_attributes_for_openai() -> None:
    """Span carries gen_ai.system, gen_ai.request.model, gen_ai.usage.*."""
    adapter = _OpenAIFakeAdapter(_OpenAIClient())
    tp, exporter = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"openai": adapter}, tracer_provider=tp)

    await dispatcher.dispatch(
        _binding("openai", model="gpt-4o-mini"),
        _step(),
        step_context=_step_context(),
    )

    finished = exporter.get_finished_spans()
    assert len(finished) == 1
    span = finished[0]
    attrs = span.attributes or {}
    assert span.name == "gen_ai.openai.chat.completions"
    assert attrs["gen_ai.system"] == "openai"
    assert attrs["gen_ai.request.model"] == "gpt-4o-mini"
    assert attrs["gen_ai.usage.input_tokens"] == 15
    assert attrs["gen_ai.usage.output_tokens"] == 7
    assert attrs["gen_ai.response.id"] == "cmpl_test_001"


@pytest.mark.asyncio
async def test_genai_span_handles_ollama_usage_shape() -> None:
    """Ollama's `prompt_eval_count` / `eval_count` populate input/output tokens."""
    adapter = _OllamaFakeAdapter(_OllamaClient())
    tp, exporter = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"ollama": adapter}, tracer_provider=tp)

    await dispatcher.dispatch(_binding("ollama"), _step(), step_context=_step_context())

    finished = exporter.get_finished_spans()
    assert len(finished) == 1
    attrs = finished[0].attributes or {}
    assert attrs["gen_ai.usage.input_tokens"] == 20
    assert attrs["gen_ai.usage.output_tokens"] == 8
    # Ollama has no response.id — attribute should be absent.
    assert "gen_ai.response.id" not in attrs


# ---------------------------------------------------------------------------
# AC #4 — anthropic.* conditional emission.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_anthropic_cache_attributes_emitted_only_for_anthropic_provider() -> None:
    """anthropic.cache_* present for anthropic; absent for openai/ollama."""
    # Anthropic — attributes present.
    anth_tp, anth_exporter = _tracer_provider_with_exporter()
    anth = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(_AnthropicClient())},
        tracer_provider=anth_tp,
    )
    await anth.dispatch(_binding("anthropic"), _step(), step_context=_step_context())
    anth_attrs = (anth_exporter.get_finished_spans()[0].attributes) or {}
    assert anth_attrs["anthropic.cache_creation_input_tokens"] == 2
    assert anth_attrs["anthropic.cache_read_input_tokens"] == 3

    # OpenAI — attributes absent.
    oa_tp, oa_exporter = _tracer_provider_with_exporter()
    oa = RuntimeLLMDispatcher(
        providers={"openai": _OpenAIFakeAdapter(_OpenAIClient())},
        tracer_provider=oa_tp,
    )
    await oa.dispatch(_binding("openai"), _step(), step_context=_step_context())
    oa_attrs = (oa_exporter.get_finished_spans()[0].attributes) or {}
    assert not any(k.startswith("anthropic.") for k in oa_attrs)


@pytest.mark.asyncio
async def test_anthropic_cache_breakpoint_id_and_ttl_extracted_from_request() -> None:
    """When the payload carries cache_control directives, breakpoint_id +
    ttl_seconds attributes are set per C-AS-14 §14.2.
    """
    adapter = _AnthropicFakeAdapter(_AnthropicClient())
    tp, exporter = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"anthropic": adapter}, tracer_provider=tp)

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "cached prefix",
                        "cache_control": {"type": "ephemeral", "ttl": "1h"},
                    },
                ],
            },
        ],
        "tools": None,
        "params": {"max_tokens": 100},
    }
    await dispatcher.dispatch(_binding("anthropic"), _step(payload), step_context=_step_context())

    attrs = (exporter.get_finished_spans()[0].attributes) or {}
    assert attrs["anthropic.cache_breakpoint_id"] == "msg-0"
    assert attrs["anthropic.cache_ttl_seconds"] == 3600


# ---------------------------------------------------------------------------
# AC #5 — RT-FAIL-PROVIDER-UNREACHABLE.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unknown_provider_raises_unreachable_error() -> None:
    """Provider not in `ctx.providers` → `LLMDispatchProviderUnreachableError`."""
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(_AnthropicClient())},
        tracer_provider=tp,
    )
    with pytest.raises(LLMDispatchProviderUnreachableError) as excinfo:
        await dispatcher.dispatch(_binding("openai"), _step(), step_context=_step_context())
    assert excinfo.value.provider_name == "openai"
    assert "RT-FAIL-PROVIDER-UNREACHABLE" in str(excinfo.value)


# ---------------------------------------------------------------------------
# AC #6 — Async-only invariant.
# ---------------------------------------------------------------------------


def test_dispatch_method_is_coroutine_function() -> None:
    """`RuntimeLLMDispatcher.dispatch` is async per C-RT-15 invariant."""
    assert inspect.iscoroutinefunction(RuntimeLLMDispatcher.dispatch)


# ---------------------------------------------------------------------------
# AC #7 — Factory binding.
# ---------------------------------------------------------------------------


def test_materialize_factory_builds_dispatcher() -> None:
    """`materialize_llm_dispatcher_stage` returns a `RuntimeLLMDispatcher`."""
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = materialize_llm_dispatcher_stage(
        providers={"anthropic": _AnthropicFakeAdapter(_AnthropicClient())},
        tracer_provider=tp,
    )
    assert isinstance(dispatcher, RuntimeLLMDispatcher)


def test_materialize_factory_raises_on_empty_providers() -> None:
    """Empty providers map → `LLMDispatchBindError` per X-AL-2 bounded contract."""
    tp, _ = _tracer_provider_with_exporter()
    with pytest.raises(LLMDispatchBindError):
        materialize_llm_dispatcher_stage(providers={}, tracer_provider=tp)


# ---------------------------------------------------------------------------
# Class 3 residual — payload shape error.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mis_shaped_payload_raises_payload_shape_error() -> None:
    """Payload missing `messages` → `LLMDispatchPayloadShapeError`."""
    adapter = _AnthropicFakeAdapter(_AnthropicClient())
    tp, _ = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"anthropic": adapter}, tracer_provider=tp)

    bad_step = WorkflowStep(
        step_id=StepID("step-bad"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"not_messages": "oops"},
    )
    with pytest.raises(LLMDispatchPayloadShapeError):
        await dispatcher.dispatch(_binding("anthropic"), bad_step, step_context=_step_context())


# ---------------------------------------------------------------------------
# AS-8 anthropic.* 6-attr extension per C-AS-14 §14.2 rows 5-10.
# Closes the request-side + model-derived attr emission gap. Anthropic SDK
# parameter sources resolved via context7 at AS-8 discriminator audit.
# ---------------------------------------------------------------------------


async def _dispatch_with_payload(
    payload: dict[str, Any],
    *,
    model: str = "claude-sonnet-4-6",
) -> dict[str, Any]:
    """Dispatch + return the gen_ai span's attribute dict."""
    adapter = _AnthropicFakeAdapter(_AnthropicClient())
    tp, exporter = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(providers={"anthropic": adapter}, tracer_provider=tp)
    await dispatcher.dispatch(
        _binding("anthropic", model=model),
        _step(payload),
        step_context=_step_context(),
    )
    return dict((exporter.get_finished_spans()[0].attributes) or {})


def _default_payload(params: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "messages": [{"role": "user", "content": "hi"}],
        "tools": None,
        "params": params or {"max_tokens": 100},
    }


@pytest.mark.asyncio
async def test_anthropic_tokenizer_version_always_emits_v1_for_non_opus_47() -> None:
    """§14.2 row 9 — strict reading: v2 only for Opus 4.7; else v1.

    `tokenizer_version` is always-emitted (the only non-optional of the 6
    new attrs); model-derived from the binding's `model` string.
    """
    attrs = await _dispatch_with_payload(_default_payload(), model="claude-sonnet-4-6")
    assert attrs["anthropic.tokenizer_version"] == "v1"


@pytest.mark.asyncio
async def test_anthropic_tokenizer_version_emits_v2_for_opus_47() -> None:
    """§14.2 row 9 — Opus 4.7 model strings get tokenizer_version=v2."""
    attrs = await _dispatch_with_payload(
        _default_payload(), model="claude-opus-4-7-20250101"
    )
    assert attrs["anthropic.tokenizer_version"] == "v2"


@pytest.mark.asyncio
async def test_anthropic_thinking_mode_emits_when_thinking_config_present() -> None:
    """§14.2 row 5 — `thinking.type` from payload.params emits as enum string."""
    attrs = await _dispatch_with_payload(
        _default_payload(
            {"max_tokens": 100, "thinking": {"type": "enabled", "budget_tokens": 2048}}
        )
    )
    assert attrs["anthropic.thinking_mode"] == "enabled"


@pytest.mark.asyncio
async def test_anthropic_thinking_mode_omitted_when_thinking_absent() -> None:
    """§14.2 row 5 — optional field; omitted when payload lacks `thinking`."""
    attrs = await _dispatch_with_payload(_default_payload())
    assert "anthropic.thinking_mode" not in attrs


@pytest.mark.asyncio
async def test_anthropic_thinking_budget_tokens_emits_when_present() -> None:
    """§14.2 row 6 — `thinking.budget_tokens` from payload.params."""
    attrs = await _dispatch_with_payload(
        _default_payload(
            {"max_tokens": 100, "thinking": {"type": "enabled", "budget_tokens": 4096}}
        )
    )
    assert attrs["anthropic.thinking_budget_tokens"] == 4096


@pytest.mark.asyncio
async def test_anthropic_thinking_budget_tokens_omitted_when_thinking_absent() -> None:
    attrs = await _dispatch_with_payload(_default_payload())
    assert "anthropic.thinking_budget_tokens" not in attrs


@pytest.mark.asyncio
async def test_anthropic_thinking_effort_emits_when_output_config_effort_present() -> None:
    """§14.2 row 7 — `output_config.effort` is a beta SDK field (nested)."""
    attrs = await _dispatch_with_payload(
        _default_payload(
            {"max_tokens": 100, "output_config": {"effort": "high"}}
        )
    )
    assert attrs["anthropic.thinking_effort"] == "high"


@pytest.mark.asyncio
async def test_anthropic_thinking_effort_omitted_when_output_config_absent() -> None:
    attrs = await _dispatch_with_payload(_default_payload())
    assert "anthropic.thinking_effort" not in attrs


@pytest.mark.asyncio
async def test_anthropic_batch_id_emits_when_operator_supplies_marker() -> None:
    """§14.2 row 8 — batch_id is operator-supplied out-of-band marker (Batch
    API submission). Not in the synchronous messages.create SDK params.
    """
    attrs = await _dispatch_with_payload(
        _default_payload({"max_tokens": 100, "batch_id": "batch_test_001"})
    )
    assert attrs["anthropic.batch_id"] == "batch_test_001"


@pytest.mark.asyncio
async def test_anthropic_batch_id_omitted_when_not_supplied() -> None:
    attrs = await _dispatch_with_payload(_default_payload())
    assert "anthropic.batch_id" not in attrs


@pytest.mark.asyncio
async def test_anthropic_inference_geo_emits_when_supplied() -> None:
    """§14.2 row 10 — `inference_geo` from payload.params (data-residency)."""
    attrs = await _dispatch_with_payload(
        _default_payload({"max_tokens": 100, "inference_geo": "us"})
    )
    assert attrs["anthropic.inference_geo"] == "us"


@pytest.mark.asyncio
async def test_anthropic_inference_geo_omitted_when_absent() -> None:
    attrs = await _dispatch_with_payload(_default_payload())
    assert "anthropic.inference_geo" not in attrs


@pytest.mark.asyncio
async def test_anthropic_six_attrs_all_emit_together_when_payload_complete() -> None:
    """Integration: when payload supplies all optional sources, all 6 attrs land."""
    attrs = await _dispatch_with_payload(
        _default_payload(
            {
                "max_tokens": 100,
                "thinking": {"type": "enabled", "budget_tokens": 2048},
                "output_config": {"effort": "medium"},
                "batch_id": "batch_test_002",
                "inference_geo": "us",
            }
        ),
        model="claude-opus-4-7-20260101",
    )
    assert attrs["anthropic.thinking_mode"] == "enabled"
    assert attrs["anthropic.thinking_budget_tokens"] == 2048
    assert attrs["anthropic.thinking_effort"] == "medium"
    assert attrs["anthropic.batch_id"] == "batch_test_002"
    assert attrs["anthropic.tokenizer_version"] == "v2"
    assert attrs["anthropic.inference_geo"] == "us"


@pytest.mark.asyncio
async def test_anthropic_six_attrs_absent_for_non_anthropic_providers() -> None:
    """Per AS-AL-3 — anthropic.* emitted ONLY when provider=='anthropic'."""
    oa_tp, oa_exporter = _tracer_provider_with_exporter()
    oa = RuntimeLLMDispatcher(
        providers={"openai": _OpenAIFakeAdapter(_OpenAIClient())},
        tracer_provider=oa_tp,
    )
    await oa.dispatch(_binding("openai"), _step(), step_context=_step_context())
    oa_attrs = (oa_exporter.get_finished_spans()[0].attributes) or {}
    for key in (
        "anthropic.thinking_mode",
        "anthropic.thinking_budget_tokens",
        "anthropic.thinking_effort",
        "anthropic.batch_id",
        "anthropic.tokenizer_version",
        "anthropic.inference_geo",
    ):
        assert key not in oa_attrs

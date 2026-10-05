"""P2-1: a provider retry must never replay a tool effect that already started.

Through the REAL C-RT-16 retry wrapper over the REAL C-RT-15 dispatcher and the REAL
C-RT-38 loop (Runtime v1.134 §14.27 post-effect fence). A model turn dispatches an AUTO
tool, then the continuation call fails with a retryable 5xx. Before the fence the
wrapper re-ran the whole dispatch: the model asked again and the tool ran twice with no
operator involved. After it, the failure surfaces once as the post-effect carrier: one
tool effect, one attempt, no candidate advance. A failure BEFORE any effect still takes
today's retry staircase.

Provider-free: scripted provider clients, recording tool dispatcher and auditor. This is
source evidence only; no installed or live provider behavior is claimed.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal
from harness_od.audit_signing_errors import AuditSigningFailedError
from harness_od.harness_breaker_schema import BreakerScope
from harness_runtime.lifecycle.hitl_placement import RuntimeHITLPlacementRegistry
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLToolCallAssessment,
    HITLToolLoopContext,
    ModelToolCall,
    RuntimeHITLToolLoop,
)
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchPayloadShapeError,
    RuntimeLLMDispatcher,
)
from harness_runtime.lifecycle.retry_breaker import DEFAULT_RETRY_POLICY, RuntimeRetryBreaker
from harness_runtime.lifecycle.retry_breaker_fallback import (
    RESERVED_LLM_DISPATCH_KEY,
    RetryBreakerFallbackDispatcher,
    RetryPolicy,
)
from opentelemetry.sdk.trace import TracerProvider

from .test_hitl_tool_loop import _Auditor, _Gate, _wiring
from .test_lifecycle_llm_dispatch import (
    _AnthropicToolTurnResponse,
    _binding,
    _FakeStandardMemoryToolExecutor,
    _ollama_dump,
    _ollama_memory_context,
    _ollama_write_note_dump,
    _OllamaResponse,
    _prompt_extension_memory_context,
    _real_memory_tool_executor,
    _step,
    _step_context,
    _Usage,
)


class _ProviderOverloaded(Exception):
    """A retryable provider failure: 529 is neither 401 nor 403, so it is TRANSIENT_RETRY."""

    status_code = 529


class _ScriptedCalls:
    """Each call pops the next scripted item: an exception to raise, or a response."""

    def __init__(self, script: list[Any]) -> None:
        self.script = script
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


@dataclass
class _AnthropicAdapter:
    script: list[Any]
    client: Any = None

    def __post_init__(self) -> None:
        messages = type("Messages", (), {})()
        messages.create = _ScriptedCalls(self.script)
        self.client = type("Client", (), {"messages": messages})()


@dataclass
class _OllamaAdapter:
    script: list[Any]
    client: Any = None

    def __post_init__(self) -> None:
        client = type("Client", (), {})()
        client.chat = _ScriptedCalls(self.script)
        self.client = client


class _Tools:
    """Records every C-RT-38 dispatch; optionally raises AFTER being entered (ambiguous)."""

    def __init__(self, *, raise_after_entry: bool = False) -> None:
        self.calls: list[ModelToolCall] = []
        self.raise_after_entry = raise_after_entry

    async def dispatch(self, call: ModelToolCall, context: HITLToolLoopContext) -> dict[str, Any]:
        _ = context
        self.calls.append(call)
        if self.raise_after_entry:
            raise ConnectionResetError("tool host dropped the connection mid-call")
        return {"ok": True}


def _auto_loop(tmp_path: Path, tools: _Tools) -> RuntimeHITLToolLoop:
    return RuntimeHITLToolLoop(
        wiring=_wiring(tmp_path),
        placement_registry=RuntimeHITLPlacementRegistry(),
        assess=lambda _call, _context: HITLToolCallAssessment(GateLevel.AUTO, "mcp-main"),
        gate=_Gate(),
        dispatcher=tools,
        response_auditor=_Auditor(),
    )


@dataclass
class _Attempts:
    """A pass-through spy over the REAL dispatcher: counts wrapper attempts only."""

    inner: RuntimeLLMDispatcher
    calls: list[Any] = field(default_factory=list)

    async def dispatch(self, binding: Any, step: Any, *, step_context: Any = None) -> Any:
        self.calls.append(binding)
        return await self.inner.dispatch(binding, step, step_context=step_context)


def _wrapper(inner: _Attempts, provider: str, family: ProviderFamily) -> Any:
    breaker = RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=3, backoff="full_jitter", jitter="full_jitter"
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        fail_threshold=5,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )

    async def _no_sleep(_seconds: float) -> None:
        return None

    return RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=breaker,
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(provider=provider, model="m", family=family),
            same_family=(),
            cross_family=(),
        ),
        tracer_provider=TracerProvider(),
        sleep_fn=_no_sleep,
    )


def _anthropic_tool_turn(tool_use_id: str) -> _AnthropicToolTurnResponse:
    return _AnthropicToolTurnResponse(
        id=f"msg_{tool_use_id}",
        content=[{"type": "tool_use", "id": tool_use_id, "name": "echo", "input": {"v": 1}}],
        stop_reason="tool_use",
        usage=_Usage(input_tokens=1, output_tokens=1),
    )


def _anthropic_text() -> _AnthropicToolTurnResponse:
    return _AnthropicToolTurnResponse(
        id="msg_final",
        content=[{"type": "text", "text": "done"}],
        stop_reason="end_turn",
        usage=_Usage(input_tokens=1, output_tokens=1),
    )


def _anthropic_step() -> Any:
    return _step(
        {
            "messages": [{"role": "user", "content": "go"}],
            "tools": [{"name": "echo", "server": "mcp-main", "input_schema": {"type": "object"}}],
            "params": {"max_tokens": 100},
        }
    )


def _ollama_tool_turn() -> _OllamaResponse:
    return _OllamaResponse(
        prompt_eval_count=1,
        eval_count=1,
        _dump=_ollama_dump(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "echo", "arguments": {"v": 1}}}],
            }
        ),
    )


def _ollama_text() -> _OllamaResponse:
    return _OllamaResponse(
        prompt_eval_count=1,
        eval_count=1,
        _dump=_ollama_dump({"role": "assistant", "content": "done"}),
    )


_ECHO_SUPERSET = ({"name": "echo", "description": "echo", "input_schema": {"type": "object"}},)


async def _run(wrapper: Any, provider: str, step: Any) -> BaseException | None:
    try:
        await wrapper.dispatch(_binding(provider, model="m"), step, step_context=_step_context())
    except Exception as exc:
        return exc
    return None


def _assert_post_effect_carrier(raised: BaseException | None, cause: type[BaseException]) -> None:
    assert raised is not None, "a post-effect failure must surface, not be retried into success"
    assert type(raised).__name__ == "PostToolEffectError", type(raised)
    assert isinstance(raised.__cause__, cause)


async def test_anthropic_continuation_failure_after_a_tool_effect_is_never_replayed(
    tmp_path: Path,
) -> None:
    tools = _Tools()
    adapter = _AnthropicAdapter(
        # attempt 1: tool turn, then a retryable 5xx; any replay would ask (and run) again
        [
            _anthropic_tool_turn("toolu_a"),
            _ProviderOverloaded("overloaded"),
            _anthropic_tool_turn("toolu_b"),
            _anthropic_text(),
        ]
    )
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={"anthropic": adapter},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
        )
    )

    raised = await _run(
        _wrapper(attempts, "anthropic", ProviderFamily.ANTHROPIC), "anthropic", _anthropic_step()
    )

    assert len(tools.calls) == 1, f"the tool effect ran {len(tools.calls)} times"
    assert len(attempts.calls) == 1
    _assert_post_effect_carrier(raised, _ProviderOverloaded)


async def test_ollama_continuation_failure_after_a_tool_effect_is_never_replayed(
    tmp_path: Path,
) -> None:
    tools = _Tools()
    adapter = _OllamaAdapter(
        [
            _ollama_tool_turn(),
            _ProviderOverloaded("overloaded"),
            _ollama_tool_turn(),
            _ollama_text(),
        ]
    )
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={"ollama": adapter},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            frozen_tool_superset=_ECHO_SUPERSET,
        )
    )

    raised = await _run(
        _wrapper(attempts, "ollama", ProviderFamily.LOCAL_OPEN_WEIGHT), "ollama", _step()
    )

    assert len(tools.calls) == 1, f"the tool effect ran {len(tools.calls)} times"
    assert len(attempts.calls) == 1
    _assert_post_effect_carrier(raised, _ProviderOverloaded)


async def test_an_ambiguous_tool_dispatch_failure_is_never_replayed(tmp_path: Path) -> None:
    """The dispatcher was entered and then raised: the effect may have happened."""
    tools = _Tools(raise_after_entry=True)
    adapter = _AnthropicAdapter(
        [_anthropic_tool_turn("toolu_a"), _anthropic_tool_turn("toolu_b"), _anthropic_text()]
    )
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={"anthropic": adapter},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
        )
    )

    raised = await _run(
        _wrapper(attempts, "anthropic", ProviderFamily.ANTHROPIC), "anthropic", _anthropic_step()
    )

    assert len(tools.calls) == 1, f"the tool host was entered {len(tools.calls)} times"
    assert len(attempts.calls) == 1
    _assert_post_effect_carrier(raised, ConnectionResetError)


@pytest.mark.parametrize("provider", ["anthropic", "ollama"])
async def test_a_failure_before_any_tool_effect_still_retries(
    tmp_path: Path, provider: str
) -> None:
    """Control: the first model call fails, no tool ran, and the staircase retries."""
    tools = _Tools()
    if provider == "anthropic":
        adapter: Any = _AnthropicAdapter([_ProviderOverloaded("overloaded"), _anthropic_text()])
        step, family, extra = _anthropic_step(), ProviderFamily.ANTHROPIC, {}
    else:
        adapter = _OllamaAdapter([_ProviderOverloaded("overloaded"), _ollama_text()])
        step, family = _step(), ProviderFamily.LOCAL_OPEN_WEIGHT
        extra = {"frozen_tool_superset": _ECHO_SUPERSET}
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={provider: adapter},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            **extra,
        )
    )

    raised = await _run(_wrapper(attempts, provider, family), provider, step)

    assert raised is None
    assert len(attempts.calls) == 2
    assert tools.calls == []


# --- correction (independent reviews of bb275eff) -------------------------------------
# The fence is owned by the WHOLE retried dispatch (one per `RuntimeLLMDispatcher.dispatch`
# call), so post-tool bookkeeping such as turn capture is inside it; the carrier keeps the
# failure's ORIGIN so a provider fault still charges the provider breaker (C-RT-16 §14.6.4)
# while replay stays forbidden; and a served Ollama memory write is an effect.


def _chain(provider: str, family: ProviderFamily) -> FallbackChain:
    """The automatic memory runtime requires the dispatcher's fallback-chain binding."""
    return FallbackChain(
        primary=ProviderCandidate(provider=provider, model="m", family=family),
        same_family=(),
        cross_family=(),
    )


class _CaptureFails:
    """A memory runtime whose turn capture always fails, after the provider turn ended."""

    standard_memory_tool_executor = None

    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.captures = 0

    def compose_for_dispatch(self, **kwargs: Any) -> Any:
        _ = kwargs
        return _prompt_extension_memory_context(provider=self.provider)

    def capture_turn_completion(self, **kwargs: Any) -> None:
        _ = kwargs
        self.captures += 1
        raise RuntimeError("memory capture failed: turn_completion")


@pytest.mark.parametrize("provider", ["anthropic", "ollama"])
async def test_a_capture_failure_after_a_tool_effect_is_never_replayed(
    tmp_path: Path, provider: str
) -> None:
    tools, capture = _Tools(), _CaptureFails(provider)
    if provider == "anthropic":
        adapter: Any = _AnthropicAdapter(
            [
                _anthropic_tool_turn(f"toolu_{n}") if n % 2 == 0 else _anthropic_text()
                for n in range(6)
            ]
        )
        step, family, extra = _anthropic_step(), ProviderFamily.ANTHROPIC, {}
    else:
        adapter = _OllamaAdapter(
            [_ollama_tool_turn() if n % 2 == 0 else _ollama_text() for n in range(6)]
        )
        step, family = _step(), ProviderFamily.LOCAL_OPEN_WEIGHT
        extra = {"frozen_tool_superset": _ECHO_SUPERSET}
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={provider: adapter},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            memory_runtime=capture,
            fallback_chain=_chain(provider, family),
            **extra,
        )
    )

    raised = await _run(_wrapper(attempts, provider, family), provider, step)

    assert (len(tools.calls), capture.captures, len(attempts.calls)) == (1, 1, 1)
    _assert_post_effect_carrier(raised, RuntimeError)
    assert raised is not None and getattr(raised, "origin", None) == "non-provider"


def _ollama_breaker_case(tmp_path: Path, script: list[Any], tools: _Tools) -> tuple[Any, Any, Any]:
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={"ollama": _OllamaAdapter(script)},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            frozen_tool_superset=_ECHO_SUPERSET,
        )
    )
    wrapper = _wrapper(attempts, "ollama", ProviderFamily.LOCAL_OPEN_WEIGHT)
    breaker = wrapper.retry_breaker.get_breaker(BreakerScope.PER_MODEL, "ollama:m")
    return attempts, wrapper, breaker


async def test_a_post_effect_provider_fault_charges_the_closed_breaker_once(tmp_path: Path) -> None:
    tools = _Tools()
    attempts, wrapper, breaker = _ollama_breaker_case(
        tmp_path, [_ollama_tool_turn(), _ProviderOverloaded("overloaded")], tools
    )

    raised = await _run(wrapper, "ollama", _step())

    assert (len(tools.calls), len(attempts.calls)) == (1, 1)
    _assert_post_effect_carrier(raised, _ProviderOverloaded)
    assert getattr(raised, "origin", None) == "provider"
    assert breaker.fail_count == 1 and breaker.state.value == "closed"


@pytest.mark.parametrize("after_effect", [False, True], ids=["pre-effect", "post-effect"])
async def test_a_half_open_trial_provider_fault_is_charged_and_re_opens(
    tmp_path: Path, after_effect: bool
) -> None:
    """§14.6.4 cell 5 holds whether or not a tool ran first: 5 -> 6, OPEN, fresh cooldown."""
    tools = _Tools()
    script: list[Any] = [_ProviderOverloaded("overloaded")]
    if after_effect:
        script.insert(0, _ollama_tool_turn())
    attempts, wrapper, breaker = _ollama_breaker_case(tmp_path, script, tools)
    for _ in range(breaker.fail_threshold):
        breaker.record_failure(now=0.0)
    assert (breaker.fail_count, breaker.state.value, breaker.opened_at) == (5, "open", 0.0)

    await _run(wrapper, "ollama", _step())

    assert len(attempts.calls) == 1 and len(tools.calls) == int(after_effect)
    assert (breaker.fail_count, breaker.state.value) == (6, "open")
    assert breaker.opened_at is not None and breaker.opened_at > 0.0


class _HttpLookingToolError(Exception):
    """A tool-host failure that LOOKS like an HTTP 529: it is not a provider fault."""

    status_code = 529


class _ToolsFailingWithHttpShape(_Tools):
    async def dispatch(self, call: ModelToolCall, context: HITLToolLoopContext) -> dict[str, Any]:
        self.calls.append(call)
        raise _HttpLookingToolError("tool host answered 529")


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
async def test_a_non_provider_post_effect_failure_never_charges_the_breaker(
    tmp_path: Path, half_open: bool
) -> None:
    tools = _ToolsFailingWithHttpShape()
    attempts, wrapper, breaker = _ollama_breaker_case(tmp_path, [_ollama_tool_turn()], tools)
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    before = breaker.fail_count

    raised = await _run(wrapper, "ollama", _step())

    assert (len(tools.calls), len(attempts.calls)) == (1, 1)
    _assert_post_effect_carrier(raised, _HttpLookingToolError)
    assert getattr(raised, "origin", None) == "non-provider"
    assert breaker.fail_count == before
    if half_open:
        # Inconclusive trial (§14.6.4 cells 6-8): re-armed OPEN with the ratified fresh
        # cooldown and fail_count UNCHANGED (asserted above) - released, never charged.
        assert breaker.state.value == "open"
        assert breaker.opened_at is not None and breaker.opened_at > 0.0


class _CountingMemory:
    """Counts executions of a REAL executor; validation and execution are its own."""

    def __init__(self, real: Any) -> None:
        self.real = real
        self.requests: list[Any] = []

    def validate(self, request: Any) -> Any:
        return self.real.validate(request)

    def execute(self, request: Any) -> Any:
        self.requests.append(request)
        return self.real.execute(request)


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
async def test_a_served_ollama_memory_write_then_provider_fault_is_never_replayed(
    tmp_path: Path, half_open: bool
) -> None:
    """A real `memory.write_note` persists once; the following 529 is still charged."""
    memory = _CountingMemory(_real_memory_tool_executor(tmp_path))
    write_turn = _OllamaResponse(
        prompt_eval_count=1,
        eval_count=1,
        _dump=_ollama_write_note_dump(
            note="A3 durable once", scope_ref="scope:u-mem-16", policy_ref="policy:u-mem-16"
        ),
    )
    tools = _Tools()
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={
                "ollama": _OllamaAdapter(
                    [write_turn, _ProviderOverloaded("overloaded"), write_turn, _ollama_text()]
                )
            },
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            frozen_tool_superset=_ECHO_SUPERSET,
            memory_context=_ollama_memory_context(),
            standard_memory_tool_executor=memory,
        )
    )
    wrapper = _wrapper(attempts, "ollama", ProviderFamily.LOCAL_OPEN_WEIGHT)
    breaker = wrapper.retry_breaker.get_breaker(BreakerScope.PER_MODEL, "ollama:m")
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    before = breaker.fail_count

    raised = await _run(wrapper, "ollama", _step())

    assert (len(memory.requests), len(attempts.calls), len(tools.calls)) == (1, 1, 0)
    assert memory.requests[0].tool_name == "memory.write_note"
    persisted = [
        path
        for path in (tmp_path / "memory").rglob("*")
        if path.is_file() and "A3 durable once" in path.read_text()
    ]
    assert persisted, "the write returned but no persisted note holds its text"
    _assert_post_effect_carrier(raised, _ProviderOverloaded)
    assert getattr(raised, "origin", None) == "provider"
    assert breaker.fail_count == before + 1


# --- provider response parsing is part of the provider boundary (§14.6.3 row 2b, cell 2) ---


def _malformed_reply(provider: str) -> Any:
    """The provider's OWN reply is malformed: a tool_use with no id / tool_calls not a list."""
    if provider == "anthropic":
        reply = _anthropic_tool_turn("malformed")
        del reply.content[0]["id"]
        return reply
    return _OllamaResponse(
        prompt_eval_count=1,
        eval_count=1,
        _dump=_ollama_dump({"role": "assistant", "content": "", "tool_calls": "not-a-list"}),
    )


def _provider_case(
    tmp_path: Path, provider: str, script: list[Any], tools: _Tools, **extra: Any
) -> tuple[Any, Any, Any, Any]:
    if provider == "anthropic":
        adapter: Any = _AnthropicAdapter(script)
        family, step = ProviderFamily.ANTHROPIC, _anthropic_step()
    else:
        adapter = _OllamaAdapter(script)
        family, step = ProviderFamily.LOCAL_OPEN_WEIGHT, _step()
        extra.setdefault("frozen_tool_superset", _ECHO_SUPERSET)
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={provider: adapter},
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            **extra,
        )
    )
    wrapper = _wrapper(attempts, provider, family)
    breaker = wrapper.retry_breaker.get_breaker(BreakerScope.PER_MODEL, f"{provider}:m")
    return attempts, wrapper, breaker, step


def _first_tool_turn(provider: str) -> Any:
    return _anthropic_tool_turn("first") if provider == "anthropic" else _ollama_tool_turn()


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
@pytest.mark.parametrize("after_effect", [False, True], ids=["pre-effect", "post-effect"])
@pytest.mark.parametrize("provider", ["anthropic", "ollama"])
async def test_a_malformed_provider_reply_is_charged_whether_or_not_a_tool_ran(
    tmp_path: Path, provider: str, after_effect: bool, half_open: bool
) -> None:
    """Parsing the provider's own reply is provider health: the same malformed reply charges
    the breaker before and after a tool effect, with one effect and one attempt."""
    tools = _Tools()
    script: list[Any] = [_malformed_reply(provider)]
    if after_effect:
        script.insert(0, _first_tool_turn(provider))
    attempts, wrapper, breaker, step = _provider_case(tmp_path, provider, script, tools)
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    before = breaker.fail_count

    raised = await _run(wrapper, provider, step)

    assert (len(tools.calls), len(attempts.calls)) == (int(after_effect), 1)
    if after_effect:
        _assert_post_effect_carrier(raised, LLMDispatchPayloadShapeError)
        assert getattr(raised, "origin", None) == "provider"
    assert breaker.fail_count == before + 1
    if half_open:
        assert breaker.state.value == "open"
        assert breaker.opened_at is not None and breaker.opened_at > 0.0


class _MemoryFailsWithHttpShape(_FakeStandardMemoryToolExecutor):
    """A memory executor failure that LOOKS like an HTTP 529: never a provider fault."""

    def execute(self, request: Any) -> dict[str, object]:
        self.requests.append(request)
        raise _HttpLookingToolError("memory executor answered 529")


async def test_a_memory_executor_failure_after_an_effect_is_never_a_provider_fault(
    tmp_path: Path,
) -> None:
    """Control: the provider boundary covers the reply's parsing, not memory execution."""
    memory = _MemoryFailsWithHttpShape()
    search_turn = _OllamaResponse(
        prompt_eval_count=1,
        eval_count=1,
        _dump=_ollama_dump(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "echo", "arguments": {"v": 1}}},
                    {
                        "function": {
                            "name": "memory.search",
                            "arguments": {
                                "query": "x",
                                "scope_ref": "scope:u-mem-16",
                                "policy_ref": "policy:u-mem-16",
                            },
                        }
                    },
                ],
            }
        ),
    )
    tools = _Tools()
    attempts, wrapper, breaker, step = _provider_case(
        tmp_path,
        "ollama",
        [search_turn],
        tools,
        memory_context=_ollama_memory_context(),
        standard_memory_tool_executor=memory,
    )
    for _ in range(breaker.fail_threshold):
        breaker.record_failure(now=0.0)

    raised = await _run(wrapper, "ollama", step)

    assert (len(tools.calls), len(memory.requests), len(attempts.calls)) == (1, 1, 1)
    _assert_post_effect_carrier(raised, _HttpLookingToolError)
    assert getattr(raised, "origin", None) == "non-provider"
    assert breaker.fail_count == 5 and breaker.state.value == "open"


class _CaptureSigningFails(_CaptureFails):
    def capture_turn_completion(self, **kwargs: Any) -> None:
        _ = kwargs
        self.captures += 1
        raise AuditSigningFailedError("signing backend unavailable")


async def test_a_signing_hard_failure_after_an_effect_keeps_its_own_carrier(
    tmp_path: Path,
) -> None:
    """Control: the dispatch-wide fence never re-wraps the U-RT-136 signing family."""
    tools, capture = _Tools(), _CaptureSigningFails("anthropic")
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={
                "anthropic": _AnthropicAdapter([_anthropic_tool_turn("toolu_a"), _anthropic_text()])
            },
            tracer_provider=TracerProvider(),
            hitl_tool_loop=_auto_loop(tmp_path, tools),
            memory_runtime=capture,
            fallback_chain=_chain("anthropic", ProviderFamily.ANTHROPIC),
        )
    )

    raised = await _run(
        _wrapper(attempts, "anthropic", ProviderFamily.ANTHROPIC), "anthropic", _anthropic_step()
    )

    assert type(raised) is AuditSigningFailedError
    assert (len(tools.calls), len(attempts.calls)) == (1, 1)


@pytest.mark.parametrize(
    "signal",
    [asyncio.CancelledError("cancelled"), DispatchFenceTrippedSignal("tripped")],
    ids=["cancelled", "dispatch-fence-tripped"],
)
async def test_a_control_signal_after_an_effect_keeps_its_identity_and_never_charges(
    tmp_path: Path, signal: BaseException
) -> None:
    """Control: a `BaseException` signal at the provider call after an effect is neither
    wrapped nor charged; the half-open trial is released, re-armed OPEN."""
    tools = _Tools()
    attempts, wrapper, breaker, step = _provider_case(
        tmp_path, "ollama", [_ollama_tool_turn(), signal], tools
    )
    for _ in range(breaker.fail_threshold):
        breaker.record_failure(now=0.0)

    with pytest.raises(BaseException) as raised:
        await wrapper.dispatch(_binding("ollama", model="m"), step, step_context=_step_context())

    assert raised.value is signal
    assert (len(tools.calls), len(attempts.calls)) == (1, 1)
    assert (breaker.fail_count, breaker.state.value) == (5, "open")
    assert breaker.opened_at is not None and breaker.opened_at > 0.0


# --- the Anthropic arm of the post-effect origin and control-identity rules -----------
# Anthropic-route witnesses of the shared non-provider-origin and control-identity rules
# (the Ollama route carries its own cases): the fence and the retry wrapper hold them on
# every provider route, not only the one that first exercised them.


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
async def test_an_anthropic_non_provider_post_effect_failure_never_charges_the_breaker(
    tmp_path: Path, half_open: bool
) -> None:
    tools = _ToolsFailingWithHttpShape()
    attempts, wrapper, breaker, step = _provider_case(
        tmp_path, "anthropic", [_anthropic_tool_turn("toolu_a")], tools
    )
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    before = breaker.fail_count

    raised = await _run(wrapper, "anthropic", step)

    assert (len(tools.calls), len(attempts.calls)) == (1, 1)
    _assert_post_effect_carrier(raised, _HttpLookingToolError)
    assert getattr(raised, "origin", None) == "non-provider"
    assert breaker.fail_count == before
    if half_open:
        assert breaker.state.value == "open"
        assert breaker.opened_at is not None and breaker.opened_at > 0.0


@pytest.mark.parametrize(
    "signal",
    [asyncio.CancelledError("cancelled"), DispatchFenceTrippedSignal("tripped")],
    ids=["cancelled", "dispatch-fence-tripped"],
)
async def test_an_anthropic_control_signal_after_an_effect_keeps_its_identity_and_never_charges(
    tmp_path: Path, signal: BaseException
) -> None:
    tools = _Tools()
    attempts, wrapper, breaker, step = _provider_case(
        tmp_path, "anthropic", [_anthropic_tool_turn("toolu_a"), signal], tools
    )
    for _ in range(breaker.fail_threshold):
        breaker.record_failure(now=0.0)

    with pytest.raises(BaseException) as raised:
        await wrapper.dispatch(_binding("anthropic", model="m"), step, step_context=_step_context())

    assert raised.value is signal
    assert (len(tools.calls), len(attempts.calls)) == (1, 1)
    assert (breaker.fail_count, breaker.state.value) == (5, "open")
    assert breaker.opened_at is not None and breaker.opened_at > 0.0


# --- U-RT-157a registered residual (spec v1.134 Scope limits): a no-dispatch answer is no effect


class _RewriteSpy:
    """Delegates to the REAL wiring and records which call id each rewrite record names."""

    def __init__(self, wiring: Any) -> None:
        self.wiring = wiring
        self.rewrite_ids: list[str] = []

    async def emit_hitl_tool_call_rewriting_state_ledger_entry(self, **kwargs: Any) -> Any:
        self.rewrite_ids.append(kwargs["tool_call_id"])
        return await self.wiring.emit_hitl_tool_call_rewriting_state_ledger_entry(**kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.wiring, name)


@pytest.mark.parametrize(
    "answer", [HITLResponse.REJECT, HITLResponse.RESPOND, HITLResponse.APPROVE]
)
async def test_a_no_dispatch_answer_then_a_transient_failure_is_re_asked_not_replayed(
    tmp_path: Path, answer: HITLResponse
) -> None:
    """REJECT and RESPOND start no effect, so the transient continuation failure retries:
    the re-asked call is prompted again and re-recorded under the new reply's id. APPROVE
    is the control on the same script: its dispatch starts the fence, so the same failure
    surfaces once as the carrier and nothing is re-asked."""
    tools, gate, auditor = _Tools(), _Gate(answer), _Auditor()
    rewrites = _RewriteSpy(_wiring(tmp_path))
    loop = RuntimeHITLToolLoop(
        wiring=rewrites,  # type: ignore[arg-type]
        placement_registry=RuntimeHITLPlacementRegistry(),
        assess=lambda _call, _context: HITLToolCallAssessment(GateLevel.ASK, "mcp-main"),
        gate=gate,
        dispatcher=tools,
        response_auditor=auditor,
    )
    adapter = _AnthropicAdapter(
        [
            _anthropic_tool_turn("toolu_a"),
            _ProviderOverloaded("overloaded"),
            _anthropic_tool_turn("toolu_b"),
            _anthropic_text(),
        ]
    )
    attempts = _Attempts(
        RuntimeLLMDispatcher(
            providers={"anthropic": adapter}, tracer_provider=TracerProvider(), hitl_tool_loop=loop
        )
    )

    raised = await _run(
        _wrapper(attempts, "anthropic", ProviderFamily.ANTHROPIC), "anthropic", _anthropic_step()
    )

    prompted = [call.tool_call_id for call in gate.calls]
    audited = [call.tool_call_id for call, _level, _decision in auditor.calls]
    if answer is HITLResponse.APPROVE:
        _assert_post_effect_carrier(raised, _ProviderOverloaded)
        assert (len(tools.calls), len(attempts.calls)) == (1, 1)
        assert prompted == audited == rewrites.rewrite_ids == ["toolu_a"]
    else:
        assert raised is None, "a no-dispatch answer is not an effect: the attempt retries"
        assert (len(tools.calls), len(attempts.calls)) == (0, 2)
        assert prompted == audited == rewrites.rewrite_ids == ["toolu_a", "toolu_b"]

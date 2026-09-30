"""First-release slice A: Ollama never passes an unserved model tool call through.

The harness does not dispatch model-emitted MCP tool calls on the Ollama route. A tool
call it cannot serve used to come back as the step's successful output, unexecuted and
unrecorded. Now each such call is answered with a provider-valid `role:"tool"` refusal,
recorded as a `policy_override`, and the turn continues so the model can answer in text.
Memory tool calls are still served; nothing else is ever executed.

Provider-free: the scripted Ollama client and memory executor fakes of the dispatch suite.
"""

from __future__ import annotations

from typing import Any

import pytest
from harness_as.memory_tool_contracts import MemoryToolName
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher

from .test_lifecycle_llm_dispatch import (
    _binding,
    _degraded_serve_spans,
    _FakeStandardMemoryToolExecutor,
    _ollama_dump,
    _ollama_memory_context,
    _OllamaClient,
    _OllamaFakeAdapter,
    _OllamaResponse,
    _step,
    _step_context,
    _tracer_provider_with_exporter,
    _unserved_tool_call_spans,
)

REFUSAL = "policy refused this tool call: model tool calls are not supported on this route"

WEATHER = {"function": {"name": "weather.lookup", "arguments": {"city": "lisbon"}}}
ECHO = {"function": {"name": "echo", "arguments": {"value": "x"}}}
MEMORY_SEARCH = {
    "function": {
        "name": "memory.search",
        "arguments": {"query": "x", "scope_ref": "scope:u-mem-16", "policy_ref": "policy:u-mem-16"},
    }
}


def _asks(*calls: dict[str, Any]) -> _OllamaResponse:
    return _OllamaResponse(
        prompt_eval_count=20,
        eval_count=8,
        _dump=_ollama_dump({"role": "assistant", "content": "", "tool_calls": list(calls)}),
    )


def _tools_step() -> Any:
    return _step(
        {
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [
                {"type": "function", "function": {"name": n, "parameters": {"type": "object"}}}
                for n in ("weather.lookup", "echo")
            ],
            "params": {"max_tokens": 100},
        }
    )


def _policy_overrides(exporter: Any) -> int:
    return sum(
        1
        for span in exporter.get_finished_spans()
        if (span.attributes or {}).get("sandbox.fail.class") == "policy_override"
    )


def _plain(client: _OllamaClient) -> tuple[RuntimeLLMDispatcher, Any]:
    tp, exporter = _tracer_provider_with_exporter()
    return RuntimeLLMDispatcher(
        providers={"ollama": _OllamaFakeAdapter(client)}, tracer_provider=tp
    ), exporter


def _with_memory(
    client: _OllamaClient, executor: _FakeStandardMemoryToolExecutor
) -> tuple[RuntimeLLMDispatcher, Any]:
    tp, exporter = _tracer_provider_with_exporter()
    return (
        RuntimeLLMDispatcher(
            providers={"ollama": _OllamaFakeAdapter(client)},
            tracer_provider=tp,
            memory_context=_ollama_memory_context(),
            standard_memory_tool_executor=executor,
        ),
        exporter,
    )


# --- plain Ollama arm ------------------------------------------------------------------


async def test_the_plain_arm_refuses_an_unserved_call_and_continues_the_turn() -> None:
    client = _OllamaClient()
    client.responses = [_asks(WEATHER)]  # then the canned text reply "ok"
    dispatcher, exporter = _plain(client)

    result = await dispatcher.dispatch(
        _binding("ollama"), _tools_step(), step_context=_step_context()
    )

    assert len(client.calls) == 2, "the refusal must be carried back to the model"
    *_, assistant, refusal = client.calls[1]["messages"]
    assert assistant["tool_calls"] == [WEATHER]
    assert refusal == {"role": "tool", "tool_name": "weather.lookup", "content": REFUSAL}
    assert client.calls[1]["tools"] == client.calls[0]["tools"]
    assert result["message"]["content"] == "ok"
    assert "tool_calls" not in result["message"]
    assert _policy_overrides(exporter) == 1


async def test_every_call_in_a_batch_gets_its_own_refusal_in_call_order() -> None:
    client = _OllamaClient()
    client.responses = [_asks(WEATHER, ECHO, WEATHER)]
    dispatcher, _exporter = _plain(client)

    await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    answers = client.calls[1]["messages"][-3:]
    assert [a["tool_name"] for a in answers] == ["weather.lookup", "echo", "weather.lookup"]
    assert all(
        a == {"role": "tool", "tool_name": a["tool_name"], "content": REFUSAL} for a in answers
    )


async def test_a_memory_named_call_without_the_memory_route_is_refused_not_executed() -> None:
    client = _OllamaClient()
    client.responses = [_asks(MEMORY_SEARCH)]
    dispatcher, _exporter = _plain(client)

    result = await dispatcher.dispatch(_binding("ollama"), _step(), step_context=_step_context())

    assert client.calls[1]["messages"][-1] == {
        "role": "tool",
        "tool_name": "memory.search",
        "content": REFUSAL,
    }
    assert result["message"]["content"] == "ok"


async def test_the_plain_arm_stops_repeated_requests_at_the_iteration_bound() -> None:
    client = _OllamaClient()
    client.canned_response = _asks(WEATHER)
    dispatcher, _exporter = _plain(client)

    with pytest.raises(RuntimeError) as excinfo:
        await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    assert "exceeded 16 continuation turns" in str(excinfo.value)
    assert len(client.calls) == 16


async def test_a_nameless_tool_call_is_refused_not_passed_through() -> None:
    client = _OllamaClient()
    client.responses = [_asks({"function": {"arguments": {}}})]
    dispatcher, _exporter = _plain(client)

    result = await dispatcher.dispatch(
        _binding("ollama"), _tools_step(), step_context=_step_context()
    )

    assert client.calls[1]["messages"][-1] == {
        "role": "tool",
        "tool_name": None,
        "content": REFUSAL,
    }
    assert result["message"]["content"] == "ok"


async def test_a_text_reply_is_unchanged() -> None:
    client = _OllamaClient()
    dispatcher, exporter = _plain(client)

    result = await dispatcher.dispatch(
        _binding("ollama"), _tools_step(), step_context=_step_context()
    )

    assert len(client.calls) == 1
    assert result["message"]["content"] == "ok"
    assert _policy_overrides(exporter) == 0


# --- standard-memory Ollama arm ---------------------------------------------------------


async def test_a_mixed_batch_serves_only_the_memory_calls_and_refuses_the_rest() -> None:
    client = _OllamaClient()
    client.responses = [_asks(WEATHER, MEMORY_SEARCH, ECHO)]
    executor = _FakeStandardMemoryToolExecutor()
    dispatcher, exporter = _with_memory(client, executor)

    result = await dispatcher.dispatch(
        _binding("ollama"), _tools_step(), step_context=_step_context()
    )

    assert [r.tool_name for r in executor.requests] == [MemoryToolName.SEARCH]
    answers = client.calls[1]["messages"][-3:]
    assert [a["tool_name"] for a in answers] == ["weather.lookup", "memory.search", "echo"]
    assert answers[0]["content"] == REFUSAL and answers[2]["content"] == REFUSAL
    assert answers[1]["content"] != REFUSAL  # the served memory result
    assert result["message"]["content"] == "ok"
    assert _policy_overrides(exporter) == 1
    assert _unserved_tool_call_spans(exporter) == [], "the memory call was served"
    assert _degraded_serve_spans(exporter) == [], "the tools-unsupported fallback did not run"


async def test_a_caller_only_batch_on_the_memory_arm_is_refused_not_executed() -> None:
    hallucinated = {"function": {"name": "memory_search", "arguments": {}}}
    client = _OllamaClient()
    client.responses = [_asks(hallucinated)]
    executor = _FakeStandardMemoryToolExecutor()
    dispatcher, exporter = _with_memory(client, executor)

    result = await dispatcher.dispatch(_binding("ollama"), _step(), step_context=_step_context())

    assert executor.requests == []
    assert client.calls[1]["messages"][-1] == {
        "role": "tool",
        "tool_name": "memory_search",
        "content": REFUSAL,
    }
    assert result["message"]["content"] == "ok"
    assert _unserved_tool_call_spans(exporter) == []


async def test_the_memory_arm_stops_repeated_refusals_at_the_iteration_bound() -> None:
    client = _OllamaClient()
    client.canned_response = _asks(WEATHER)
    executor = _FakeStandardMemoryToolExecutor()
    dispatcher, _exporter = _with_memory(client, executor)

    with pytest.raises(RuntimeError) as excinfo:
        await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    assert "exceeded 16 continuation turns" in str(excinfo.value)
    assert len(client.calls) == 16
    assert executor.requests == []


# --- one trace record per refusal (Codex HOLD ollama-unserved-tool-refusal-codex-1) ---------

REFUSAL_EVENT = "ollama.tool_call.refused"
EXHAUSTED_EVENT = "ollama.tool_loop.exhausted"


def _events(exporter: Any, name: str) -> list[dict[str, Any]]:
    return [
        dict(event.attributes or {})
        for span in exporter.get_finished_spans()
        for event in span.events
        if event.name == name
    ]


def _refused(turn: int, index: int, tool: str) -> dict[str, Any]:
    return {"tool.call.turn": turn, "tool.call.index": index, "gen_ai.tool.name": tool}


async def test_three_refusals_are_three_ordered_records_without_arguments() -> None:
    client = _OllamaClient()
    client.responses = [_asks(WEATHER, ECHO, WEATHER)]
    dispatcher, exporter = _plain(client)

    await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    assert _events(exporter, REFUSAL_EVENT) == [
        _refused(0, 0, "weather.lookup"),
        _refused(0, 1, "echo"),
        _refused(0, 2, "weather.lookup"),
    ]
    # The enclosing dispatch classification is unchanged: one span carries it.
    assert _policy_overrides(exporter) == 1


async def test_a_mixed_batch_records_only_its_refused_calls_by_position() -> None:
    client = _OllamaClient()
    client.responses = [_asks(WEATHER, MEMORY_SEARCH, ECHO)]
    dispatcher, exporter = _with_memory(client, _FakeStandardMemoryToolExecutor())

    await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    assert _events(exporter, REFUSAL_EVENT) == [
        _refused(0, 0, "weather.lookup"),
        _refused(0, 2, "echo"),
    ]


async def test_a_served_only_batch_records_no_refusal() -> None:
    client = _OllamaClient()
    client.responses = [_asks(MEMORY_SEARCH)]
    dispatcher, exporter = _with_memory(client, _FakeStandardMemoryToolExecutor())

    await dispatcher.dispatch(_binding("ollama"), _step(), step_context=_step_context())

    assert _events(exporter, REFUSAL_EVENT) == []
    assert _events(exporter, EXHAUSTED_EVENT) == []
    assert _policy_overrides(exporter) == 0


async def test_a_nameless_refusal_is_recorded_by_position_only() -> None:
    client = _OllamaClient()
    client.responses = [_asks({"function": {"arguments": {"secret": "x"}}})]
    dispatcher, exporter = _plain(client)

    await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    assert _events(exporter, REFUSAL_EVENT) == [{"tool.call.turn": 0, "tool.call.index": 0}]


@pytest.mark.parametrize("arm", ["plain", "memory"])
async def test_the_terminal_turn_records_exhaustion_not_a_refusal_it_never_sent(arm: str) -> None:
    client = _OllamaClient()
    client.canned_response = _asks(WEATHER, ECHO)
    if arm == "plain":
        dispatcher, exporter = _plain(client)
    else:
        dispatcher, exporter = _with_memory(client, _FakeStandardMemoryToolExecutor())

    with pytest.raises(RuntimeError, match="exceeded 16 continuation turns"):
        await dispatcher.dispatch(_binding("ollama"), _tools_step(), step_context=_step_context())

    refused = _events(exporter, REFUSAL_EVENT)
    # Turns 0..14 were answered (two refusals each, both carried to the model); turn 15
    # never gets a continuation, so it is recorded once as exhaustion, not as refusals.
    assert [(e["tool.call.turn"], e["tool.call.index"]) for e in refused] == [
        (turn, index) for turn in range(15) for index in (0, 1)
    ]
    assert _events(exporter, EXHAUSTED_EVENT) == [{"tool.call.turn": 15, "tool.call.count": 2}]

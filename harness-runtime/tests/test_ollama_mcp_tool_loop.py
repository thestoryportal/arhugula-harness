"""Runtime v1.134 C-RT-38 on the Ollama route: model-emitted MCP tools go through the loop.

With an effective frozen tool superset AND the bound `RuntimeHITLToolLoop`, the Ollama
dispatch puts the superset on the wire (replacing `payload.tools`, including a descended
child's empty superset) and sends every non-memory call through the REAL C-RT-38 loop:
assessment, operator gate, audit-before-effect, then the dispatcher. Memory calls stay
with the memory executor; answers follow call order. Without a superset or a loop the
first-release refusal path is unchanged.

Provider-free: scripted Ollama client, recording gate/auditor/dispatcher over the real
loop, CP/IS wiring and state ledger. Source evidence only, not an installed or live
Ollama tool-calling claim.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_response_palette import HITLResponse
from harness_runtime.lifecycle.hitl_placement import RuntimeHITLPlacementRegistry
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLGateDecision,
    HITLToolCallAssessment,
    HITLToolLoopContext,
    ModelToolCall,
    RuntimeHITLToolLoop,
)
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher

from .test_hitl_tool_loop import _Auditor, _wiring
from .test_lifecycle_llm_dispatch import (
    _binding,
    _FakeStandardMemoryToolExecutor,
    _ollama_dump,
    _ollama_memory_context,
    _OllamaClient,
    _OllamaFakeAdapter,
    _OllamaResponse,
    _step,
    _step_context,
    _tracer_provider_with_exporter,
)

REFUSAL = "policy refused this tool call"
UNSERVED = f"{REFUSAL}: model tool calls are not supported on this route"
ECHO = {"function": {"name": "echo", "arguments": {"value": "x"}}}
MEMORY_SEARCH = {
    "function": {
        "name": "memory.search",
        "arguments": {"query": "x", "scope_ref": "scope:u-mem-16", "policy_ref": "policy:u-mem-16"},
    }
}
SUPERSET = (
    {"name": "echo", "description": "Echo a value", "input_schema": {"type": "object"}},
    {"name": "search_tools", "description": "Find tools", "input_schema": {"type": "object"}},
    # An Anthropic-native entry with no input_schema has no Ollama projection.
    {"type": "memory_20250818", "name": "memory"},
)
CHILD_SUPERSET = (
    {"name": "echo", "description": "Echo a value", "input_schema": {"type": "object"}},
)
PROJECTED = [
    {
        "type": "function",
        "function": {
            "name": "echo",
            "description": "Echo a value",
            "parameters": {"type": "object"},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_tools",
            "description": "Find tools",
            "parameters": {"type": "object"},
        },
    },
]


def _asks(*calls: dict[str, Any], prompt: int = 20, output: int = 8) -> _OllamaResponse:
    return _OllamaResponse(
        prompt_eval_count=prompt,
        eval_count=output,
        _dump=_ollama_dump({"role": "assistant", "content": "", "tool_calls": list(calls)}),
    )


def _step_declaring_other_tools() -> Any:
    """`payload.tools` names a tool the superset does not: it must never reach the wire."""
    return _step(
        {
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"type": "function", "function": {"name": "weather.lookup"}}],
            "params": {"max_tokens": 100},
        }
    )


class _Gate:
    def __init__(self, decision: HITLGateDecision | None = None) -> None:
        self.decision = decision or HITLGateDecision(response=HITLResponse.APPROVE)
        self.asked: list[ModelToolCall] = []

    async def decide(
        self, *, call: ModelToolCall, context: HITLToolLoopContext, palette: frozenset[Any]
    ) -> HITLGateDecision:
        _ = (context, palette)
        self.asked.append(call)
        return self.decision


class _Tools:
    def __init__(self) -> None:
        self.calls: list[ModelToolCall] = []

    async def dispatch(self, call: ModelToolCall, context: HITLToolLoopContext) -> dict[str, Any]:
        _ = context
        self.calls.append(call)
        return {"echoed": dict(call.arguments)}


def _loop(
    tmp_path: Path,
    *,
    level: GateLevel = GateLevel.AUTO,
    gate: _Gate | None = None,
    assess: Any = None,
) -> tuple[RuntimeHITLToolLoop, _Gate, _Tools, _Auditor]:
    gate, tools, auditor = gate or _Gate(), _Tools(), _Auditor()
    loop = RuntimeHITLToolLoop(
        wiring=_wiring(tmp_path),
        placement_registry=RuntimeHITLPlacementRegistry(),
        assess=assess or (lambda _call, _context: HITLToolCallAssessment(level, "mcp-main")),
        gate=gate,
        dispatcher=tools,
        response_auditor=auditor,
    )
    return loop, gate, tools, auditor


def _dispatcher(
    client: _OllamaClient,
    loop: RuntimeHITLToolLoop | None,
    *,
    superset: Any = SUPERSET,
    child_superset: Any = None,
    memory: _FakeStandardMemoryToolExecutor | None = None,
) -> tuple[RuntimeLLMDispatcher, Any]:
    tp, exporter = _tracer_provider_with_exporter()
    extra: dict[str, Any] = {}
    if memory is not None:
        extra = {
            "memory_context": _ollama_memory_context(),
            "standard_memory_tool_executor": memory,
        }
    return (
        RuntimeLLMDispatcher(
            providers={"ollama": _OllamaFakeAdapter(client)},
            tracer_provider=tp,
            hitl_tool_loop=loop,
            frozen_tool_superset=superset,
            child_frozen_tool_superset=child_superset,
            **extra,
        ),
        exporter,
    )


async def _dispatch(dispatcher: RuntimeLLMDispatcher, *, depth: int = 0) -> Any:
    context = _step_context().model_copy(update={"descent_depth": depth})
    return await dispatcher.dispatch(
        _binding("ollama"), _step_declaring_other_tools(), step_context=context
    )


def _answers(client: _OllamaClient, turn: int = 1) -> list[dict[str, Any]]:
    return [m for m in client.calls[turn]["messages"] if m.get("role") == "tool"]


# --- 1. the projection is the wire, for root and descended steps ------------------------


async def test_the_superset_projection_replaces_payload_tools_on_the_wire(tmp_path: Path) -> None:
    client = _OllamaClient()
    loop, *_ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop)

    await _dispatch(dispatcher)

    assert client.calls[0]["tools"] == PROJECTED


async def test_a_descended_step_sends_the_child_superset(tmp_path: Path) -> None:
    client = _OllamaClient()
    loop, *_ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop, child_superset=CHILD_SUPERSET)

    await _dispatch(dispatcher, depth=1)

    assert client.calls[0]["tools"] == PROJECTED[:1]


async def test_an_empty_child_superset_sends_no_tools_never_the_step_tools(tmp_path: Path) -> None:
    client = _OllamaClient()
    loop, *_ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop, child_superset=None)

    await _dispatch(dispatcher, depth=1)

    assert client.calls[0]["tools"] == []


# --- 2-4. each operator outcome reaches the model through the real loop -----------------


async def test_an_approved_call_is_audited_dispatched_once_and_answered(tmp_path: Path) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO)]
    loop, gate, tools, auditor = _loop(tmp_path, level=GateLevel.ASK)
    dispatcher, _ = _dispatcher(client, loop)

    result = await _dispatch(dispatcher)

    assert [c.tool for c in tools.calls] == ["echo"]
    assert [c.tool for c, *_ in auditor.calls] == ["echo"]
    assert len(gate.asked) == 1
    [answer] = _answers(client)
    assert answer["tool_name"] == "echo"
    assert json.loads(answer["content"]) == {"echoed": {"value": "x"}}
    assert result["message"]["content"] == "ok"


@pytest.mark.parametrize(
    ("level", "decision", "expected"),
    [
        (GateLevel.ASK, HITLGateDecision(response=HITLResponse.REJECT), None),
        (
            GateLevel.ASK,
            HITLGateDecision(response=HITLResponse.RESPOND, response_text="use the cache"),
            "use the cache",
        ),
        (GateLevel.DENY, HITLGateDecision(response=HITLResponse.REJECT), REFUSAL),
        (
            GateLevel.DENY,
            HITLGateDecision(response=HITLResponse.RESPOND, response_text="not here"),
            f"{REFUSAL}: not here",
        ),
    ],
    ids=["ask-reject", "ask-respond", "deny-reject", "deny-respond"],
)
async def test_a_refused_or_answered_call_is_never_dispatched(
    tmp_path: Path, level: GateLevel, decision: HITLGateDecision, expected: str | None
) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO)]
    loop, _, tools, _ = _loop(tmp_path, level=level, gate=_Gate(decision))
    dispatcher, _ = _dispatcher(client, loop)

    await _dispatch(dispatcher)

    assert tools.calls == []
    [answer] = _answers(client)
    assert answer["tool_name"] == "echo"
    if expected is None:
        assert answer["content"] == "HITL rejected or skipped this tool call."
    else:
        assert answer["content"] == expected


async def test_an_evaluator_failure_is_a_typed_refusal_without_prompt(tmp_path: Path) -> None:
    def fails(_call: ModelToolCall, _context: HITLToolLoopContext) -> HITLToolCallAssessment:
        raise LookupError("registry unavailable")

    client = _OllamaClient()
    client.responses = [_asks(ECHO)]
    loop, gate, tools, _ = _loop(tmp_path, assess=fails)
    dispatcher, exporter = _dispatcher(client, loop)

    await _dispatch(dispatcher)

    assert (gate.asked, tools.calls) == ([], [])
    assert _answers(client)[0]["content"] == REFUSAL
    classes = [
        (s.attributes or {}).get("sandbox.fail.class") for s in exporter.get_finished_spans()
    ]
    assert classes.count("policy_override") >= 1


@pytest.mark.parametrize("edited", [{"value": "edited"}, {}], ids=["object", "empty-object"])
async def test_edit_dispatches_exactly_the_edited_arguments(
    tmp_path: Path, edited: dict[str, Any]
) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO)]
    gate = _Gate(HITLGateDecision(response=HITLResponse.EDIT, edited_arguments=edited))
    loop, _, tools, _ = _loop(tmp_path, level=GateLevel.ASK, gate=gate)
    dispatcher, _ = _dispatcher(client, loop)

    await _dispatch(dispatcher)

    assert [dict(c.arguments) for c in tools.calls] == [edited]


# --- 5. mixed memory + MCP batch: both served, answers in call order --------------------


async def test_a_mixed_batch_serves_memory_and_mcp_in_call_order(tmp_path: Path) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO, MEMORY_SEARCH, ECHO)]
    loop, _, tools, _ = _loop(tmp_path)
    memory = _FakeStandardMemoryToolExecutor()
    dispatcher, _ = _dispatcher(client, loop, memory=memory)

    await _dispatch(dispatcher)

    assert [a["tool_name"] for a in _answers(client)] == ["echo", "memory.search", "echo"]
    assert len(tools.calls) == 2 and len(memory.requests) == 1
    tool_names = [t["function"]["name"] for t in client.calls[0]["tools"]]
    assert tool_names[:2] == ["echo", "search_tools"] and "memory.search" in tool_names


# --- 6. identity: distinct per call, a fresh nonce per dispatch invocation ---------------


_ID = re.compile(r"^ollama:(?P<nonce>[0-9a-f]{32}):(?P<turn>\d+):(?P<index>\d+)$")


async def test_call_ids_are_distinct_and_never_reused_across_dispatches(tmp_path: Path) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO, ECHO), _OllamaClient().canned_response, _asks(ECHO)]
    loop, _, tools, _ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop)

    await _dispatch(dispatcher)
    await _dispatch(dispatcher)

    ids = [_ID.match(c.tool_call_id) for c in tools.calls]
    assert all(ids), [c.tool_call_id for c in tools.calls]
    first, second, third = (m.groupdict() for m in ids if m is not None)
    assert (first["turn"], first["index"], second["index"]) == ("0", "0", "1")
    assert first["nonce"] == second["nonce"] != third["nonce"]
    assert "tool_call_id" not in json.dumps(client.calls[1]["messages"])


# --- 7. without both a superset and a loop the first-release refusal is unchanged --------


@pytest.mark.parametrize("bound", ["loop-only", "superset-only"])
async def test_without_superset_and_loop_the_refusal_path_is_unchanged(
    tmp_path: Path, bound: str
) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO)]
    loop, _, tools, _ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(
        client,
        loop if bound == "loop-only" else None,
        superset=None if bound == "loop-only" else SUPERSET,
    )

    await _dispatch(dispatcher)

    assert tools.calls == []
    assert client.calls[0]["tools"] == [
        {"type": "function", "function": {"name": "weather.lookup"}}
    ]
    assert _answers(client) == [{"role": "tool", "tool_name": "echo", "content": UNSERVED}]


# --- 8. tools-unsupported: one bare retry, recorded, nothing dispatched ------------------


class _ToolsUnsupported(Exception):
    def __init__(self) -> None:
        super().__init__("llama3.2:1b does not support tools")
        self.error = "registry.ollama.ai/library/llama3.2:1b does not support tools"
        self.status_code = 400


_ToolsUnsupported.__name__ = "ResponseError"


async def test_a_tools_unsupported_model_gets_one_bare_retry_and_no_dispatch(
    tmp_path: Path,
) -> None:
    client = _OllamaClient()
    client.errors = [_ToolsUnsupported()]
    loop, _, tools, _ = _loop(tmp_path)
    dispatcher, exporter = _dispatcher(client, loop)

    result = await _dispatch(dispatcher)

    assert len(client.calls) == 2
    assert "tools" not in client.calls[1]
    assert tools.calls == [] and result["message"]["content"] == "ok"
    events = [e.name for s in exporter.get_finished_spans() for e in s.events]
    assert "ollama.tools_unsupported" in events


async def test_a_mid_loop_tools_rejection_still_raises(tmp_path: Path) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO)]
    client.errors = [None, _ToolsUnsupported()]
    loop, *_ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop)

    with pytest.raises(Exception, match="does not support tools"):
        await _dispatch(dispatcher)


# --- 9-10. the bound and the usage ---------------------------------------------------------


async def test_the_iteration_bound_still_ends_in_the_typed_error(tmp_path: Path) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO) for _ in range(16)]
    loop, *_ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop)

    with pytest.raises(RuntimeError, match="16"):
        await _dispatch(dispatcher)


async def test_usage_is_summed_across_tool_turns(tmp_path: Path) -> None:
    client = _OllamaClient()
    client.responses = [_asks(ECHO, prompt=5, output=3)]  # then canned 20/8
    loop, *_ = _loop(tmp_path)
    dispatcher, exporter = _dispatcher(client, loop)

    await _dispatch(dispatcher)

    [span] = [s for s in exporter.get_finished_spans() if s.name.startswith("chat ")]
    attrs = span.attributes or {}
    assert (attrs["gen_ai.usage.input_tokens"], attrs["gen_ai.usage.output_tokens"]) == (25, 11)


# --- malformed model calls are refused to the model, never dispatched ----------------------


@pytest.mark.parametrize(
    "call",
    [
        {"function": {"arguments": {"value": "x"}}},
        {"function": {"name": "echo", "arguments": "not json"}},
        {"function": {"name": "echo", "arguments": "[1]"}},
    ],
    ids=["no-name", "non-json-args", "non-object-args"],
)
async def test_a_malformed_call_is_refused_without_entering_the_loop(
    tmp_path: Path, call: dict[str, Any]
) -> None:
    client = _OllamaClient()
    client.responses = [_asks(call)]
    loop, gate, tools, _ = _loop(tmp_path)
    dispatcher, _ = _dispatcher(client, loop)

    await _dispatch(dispatcher)

    assert (gate.asked, tools.calls) == ([], [])
    [answer] = _answers(client)
    assert answer["content"].startswith(REFUSAL)

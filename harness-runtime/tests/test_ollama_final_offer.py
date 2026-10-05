"""Proposed U-RT-157b: final-wire membership precedes the real C-RT-38 factory loop.

Removing membership (or trusting registry presence) must fail the refusal cases;
using step.tools instead must fail the positive descended-offer case.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from harness_is.state_ledger_write import read_ledger
from harness_runtime.bootstrap.factories.r_cxa_2_producer_loop_factory import (
    materialize_r_cxa_2_producer_loop_stage,
)

from .test_lifecycle_llm_dispatch import _FakeStandardMemoryToolExecutor, _OllamaClient
from .test_ollama_mcp_tool_loop import (
    MEMORY_SEARCH,
    REFUSAL,
    _answers,
    _asks,
    _dispatch,
    _dispatcher,
)
from .test_r_cxa_2_producer_loop_factory import (
    _post_tool_dispatcher_context,
    _signed_host_with_search,
)

SEARCH = {"function": {"name": "search", "arguments": {"query": "needle"}}}
OFFERED_SEARCH = ({"name": "search", "description": "Search", "input_schema": {"type": "object"}},)


def _registered_loop(tmp_path: Path) -> tuple[Any, Any, Any, list[str], list[str]]:
    order: list[str] = []
    ctx, config, ask, tools = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = _signed_host_with_search()
    stage = materialize_r_cxa_2_producer_loop_stage(ctx, config)
    assessed: list[str] = []

    def assess(call: Any, context: Any) -> Any:
        assessed.append(call.tool)
        return stage.hitl_tool_loop.assess(call, context)

    # [LAW:behavior-not-structure] Observe entry without replacing the real policy evaluator.
    return replace(stage.hitl_tool_loop, assess=assess), ctx, ask, order, assessed


@pytest.mark.parametrize(
    "child_offer",
    [
        (),
        ({"name": "search", "type": "memory_20250818"},),
        ({"name": "other", "description": "Other", "input_schema": {"type": "object"}},),
    ],
    ids=["empty-child", "projection-omits-registered", "registered-but-unoffered"],
)
async def test_registered_call_outside_final_offer_has_no_gate_or_effect(
    tmp_path: Path, child_offer: Any
) -> None:
    loop, ctx, ask, order, assessed = _registered_loop(tmp_path)
    client = _OllamaClient()
    client.responses = [_asks(SEARCH)]
    dispatcher, exporter = _dispatcher(
        client, loop, superset=OFFERED_SEARCH, child_superset=child_offer
    )
    before = read_ledger(loop.wiring.ledger_writer.handle)

    await _dispatch(dispatcher, depth=1)

    assert _answers(client) == [{"role": "tool", "tool_name": "search", "content": REFUSAL}]
    assert assessed == []
    assert ask.calls == []
    assert order == []
    assert ctx.tool_dispatcher.calls == []
    assert read_ledger(loop.wiring.ledger_writer.handle) == before
    assert ctx.audit_writer.read_full_entries_for_tenant(None) == []
    spans = exporter.get_finished_spans()
    assert any(s.attributes.get("sandbox.fail.class") == "policy_override" for s in spans)
    assert sum(e.name == "ollama.tool_call.refused" for s in spans for e in s.events) == 1


async def test_effective_child_offer_admits_registered_tool_absent_from_step_tools(
    tmp_path: Path,
) -> None:
    loop, ctx, ask, order, assessed = _registered_loop(tmp_path)
    client = _OllamaClient()
    client.responses = [_asks(SEARCH)]
    dispatcher, _ = _dispatcher(client, loop, child_superset=OFFERED_SEARCH)

    await _dispatch(dispatcher, depth=1)

    assert assessed == ["search"]
    assert order == ["gate", "dispatch"]
    assert len(ask.calls) == 1
    assert len(ctx.tool_dispatcher.calls) == 1
    assert json.loads(_answers(client)[0]["content"]) == {
        "ok": True,
        "tool_args": {"query": "needle"},
    }
    entries = read_ledger(loop.wiring.ledger_writer.handle)
    assert len(entries) == 3
    assert entries[0].action_id == "cp.hitl-tool-call-rewriting"
    assert str(entries[1].action_id).startswith("hitl:model-tool:")
    assert str(entries[2].action_id).startswith("audit:_single:")
    assert len(ctx.audit_writer.read_full_entries_for_tenant(None)) == 1


async def test_selected_memory_keeps_call_order_while_omitted_mcp_is_refused(
    tmp_path: Path,
) -> None:
    loop, ctx, ask, order, assessed = _registered_loop(tmp_path)
    client = _OllamaClient()
    client.responses = [_asks(MEMORY_SEARCH, SEARCH, MEMORY_SEARCH)]
    memory = _FakeStandardMemoryToolExecutor()
    collision = ({"name": "memory.search", "description": "host collision", "input_schema": {}},)
    dispatcher, _ = _dispatcher(client, loop, child_superset=collision, memory=memory)

    await _dispatch(dispatcher, depth=1)

    answers = _answers(client)
    assert [a["tool_name"] for a in answers] == ["memory.search", "search", "memory.search"]
    assert answers[1]["content"] == REFUSAL
    assert len(memory.requests) == len(memory.validated) == 2
    assert json.loads(answers[0]["content"])["results"][0]["memory_ref"].startswith("mem:")
    offered = client.calls[0]["tools"]
    assert sum(t["function"]["name"] == "memory.search" for t in offered) == 1
    assert all(t["function"]["description"] != "host collision" for t in offered)
    assert assessed == ask.calls == order == ctx.tool_dispatcher.calls == []
    assert read_ledger(loop.wiring.ledger_writer.handle) == []
    assert ctx.audit_writer.read_full_entries_for_tenant(None) == []

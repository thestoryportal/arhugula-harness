"""Codex HOLD correction for the model tool-call DENY slice.

1. The evaluator's runtime value is parsed at one boundary: only a typed assessment
   carrying a real `GateLevel` and a named owner proceeds. Anything else refuses with no
   prompt, no rewrite record and no dispatch, and the model sees an `is_error` result.
2. The operator is asked, and the rewrite is recorded, under the host that owns the tool
   in the registry that trust and dispatch use, never the model-supplied `server` label.

Provider-free: host, operator, dispatcher and provider-client doubles only.
"""

from __future__ import annotations

import asyncio
import enum
from pathlib import Path
from typing import Any, cast

import pytest
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_response_palette import HITLResponse
from harness_is.state_ledger_write import read_ledger
from harness_runtime.bootstrap.factories.r_cxa_2_producer_loop_factory import (
    materialize_r_cxa_2_producer_loop_stage,
)
from harness_runtime.lifecycle.ask_user_question_surface import AskUserQuestionResult
from harness_runtime.lifecycle.hitl_placement import RuntimeHITLPlacementRegistry
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLGateDecision,
    HITLToolCallAssessment,
    HITLToolLoopContext,
    HITLToolRefusalReason,
    ModelToolCall,
    RuntimeHITLToolLoop,
)
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher

from .test_hitl_tool_loop import _Auditor
from .test_hitl_tool_loop_deny import _Host
from .test_lifecycle_llm_dispatch import (
    _AnthropicFakeAdapter,
    _binding,
    _step,
    _step_context,
    _tracer_provider_with_exporter,
    _two_tool_step_payload,
    _two_tool_use_turn_client,
)
from .test_r_cxa_2_producer_loop_factory import _context, _post_tool_dispatcher_context

ALL = frozenset(HITLResponse)
DENY_PALETTE = frozenset({HITLResponse.REJECT, HITLResponse.RESPOND})

HOSTS = {
    "real-l0-host": _Host(MCPTrustTier.LEVEL_0_REFUSE_REMOTE, "delete_file"),
    "real-l1-host": _Host(MCPTrustTier.LEVEL_1_SIGNED_PINNED, "read_file"),
    "real-l3-host": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "list_dir"),
}


class _Operator:
    """Ask surface double that records the exact prompt text and offered palette."""

    def __init__(self, response: HITLResponse) -> None:
        self.response = response
        self.prompts: list[str] = []
        self.offered: list[frozenset[HITLResponse]] = []

    async def ask(
        self, prompt: str, options: tuple[HITLResponse, ...], timeout: float | None
    ) -> AskUserQuestionResult:
        _ = timeout
        self.prompts.append(prompt)
        self.offered.append(frozenset(options))
        return AskUserQuestionResult(response=self.response, latency_ms=1.0)


def _call(tool: str, server: str, tool_call_id: str = "call-1") -> ModelToolCall:
    return ModelToolCall(
        tool_call_id=tool_call_id,
        tool=tool,
        server=server,
        arguments={"query": "q"},
        provider="fixture-provider",
        model="fixture-model",
    )


def _stage(
    tmp_path: Path, hosts: dict[str, Any], response: HITLResponse
) -> tuple[RuntimeHITLToolLoop, _Operator, Any]:
    ctx, config, _surface, dispatcher = _post_tool_dispatcher_context(tmp_path, [])
    ctx.mcp_client_hosts = hosts
    operator = _Operator(response)
    ctx.ask_user_question_surface = operator
    return materialize_r_cxa_2_producer_loop_stage(ctx, config).hitl_tool_loop, operator, dispatcher


# --- finding 1: a malformed evaluator value is a typed no-prompt, no-dispatch refusal ----


class _Foreign(enum.Enum):
    AUTO = "auto"


MALFORMED = {
    "none": None,
    "str-deny": "deny",
    "str-auto": "auto",
    "int": 0,
    "foreign-enum": _Foreign.AUTO,
    "bare-level-not-assessment": GateLevel.AUTO,
    "assessment-level-none": HITLToolCallAssessment(level=cast(Any, None), owner="real-l1-host"),
    "assessment-level-str": HITLToolCallAssessment(level=cast(Any, "auto"), owner="real-l1-host"),
    "assessment-owner-empty": HITLToolCallAssessment(level=GateLevel.AUTO, owner=""),
    "assessment-owner-none": HITLToolCallAssessment(level=GateLevel.AUTO, owner=cast(Any, None)),
}


@pytest.mark.parametrize("value", list(MALFORMED.values()), ids=list(MALFORMED))
@pytest.mark.parametrize("response", [HITLResponse.APPROVE, HITLResponse.EDIT])
def test_a_malformed_evaluator_value_refuses_without_prompt_rewrite_or_dispatch(
    tmp_path: Path, value: object, response: HITLResponse
) -> None:
    stage_loop, operator, dispatcher = _stage(tmp_path, HOSTS, response)
    loop = RuntimeHITLToolLoop(
        wiring=stage_loop.wiring,
        placement_registry=stage_loop.placement_registry,
        assess=lambda _call, _context: cast(Any, value),
        gate=stage_loop.gate,
        dispatcher=stage_loop.dispatcher,
        response_auditor=stage_loop.response_auditor,
    )

    (result,) = asyncio.run(loop.run_tool_calls([_call("read_file", "real-l1-host")], _context()))

    assert operator.prompts == []
    assert dispatcher.calls == []
    assert result.dispatched is False
    assert result.rewritten_tool_call is None
    assert read_ledger(loop.wiring.ledger_writer.handle) == []
    assert result.refusal is not None
    assert result.refusal.reason is HITLToolRefusalReason.MALFORMED_GATE_LEVEL


class _RecordingGate:
    def __init__(self) -> None:
        self.calls: list[ModelToolCall] = []

    async def decide(
        self, *, call: ModelToolCall, context: HITLToolLoopContext, palette: frozenset[HITLResponse]
    ) -> HITLGateDecision:
        _ = (context, palette)
        self.calls.append(call)
        return HITLGateDecision(response=HITLResponse.APPROVE)


class _RecordingDispatcher:
    def __init__(self) -> None:
        self.calls: list[ModelToolCall] = []

    async def dispatch(self, call: ModelToolCall, context: HITLToolLoopContext) -> dict[str, Any]:
        _ = context
        self.calls.append(call)
        return {"ok": True}


@pytest.mark.parametrize("malformed", [None, "deny", 0], ids=["none", "str", "int"])
async def test_a_malformed_evaluator_value_reaches_the_model_as_an_error_and_the_turn_continues(
    malformed: object,
) -> None:
    gate, tools = _RecordingGate(), _RecordingDispatcher()

    def assess(call: ModelToolCall, _context: HITLToolLoopContext) -> Any:
        if call.tool_call_id == "toolu_001":
            return malformed
        return HITLToolCallAssessment(level=GateLevel.AUTO, owner="srv")

    loop = RuntimeHITLToolLoop(
        wiring=cast(Any, None),  # never reached: no call here is asked
        placement_registry=RuntimeHITLPlacementRegistry(),
        assess=assess,
        gate=gate,
        dispatcher=tools,
        response_auditor=_Auditor(),
    )
    client = _two_tool_use_turn_client()
    tp, exporter = _tracer_provider_with_exporter()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(client)},
        tracer_provider=tp,
        hitl_tool_loop=loop,
    )

    await dispatcher.dispatch(
        _binding("anthropic", model="claude-test"),
        _step(_two_tool_step_payload()),
        step_context=_step_context(),
    )

    assert len(client.messages.calls) == 2  # the next model turn carries both results
    refused, allowed = client.messages.calls[1]["messages"][-1]["content"]
    assert refused["tool_use_id"] == "toolu_001"
    assert refused["is_error"] is True
    assert refused["content"] == "policy refused this tool call"
    assert allowed["tool_use_id"] == "toolu_002"
    assert "is_error" not in allowed
    assert gate.calls == []
    assert [c.tool_call_id for c in tools.calls] == ["toolu_002"]
    classes = [
        span.attributes.get("sandbox.fail.class")
        for span in exporter.get_finished_spans()
        if span.attributes is not None
    ]
    assert classes.count("policy_override") == 1


# --- finding 2: the canonical registry owner, not the supplied label ----------------------


@pytest.mark.parametrize(
    ("tool", "owner", "palette", "dispatches"),
    [
        ("delete_file", "real-l0-host", DENY_PALETTE, 0),
        ("read_file", "real-l1-host", ALL, 1),
        ("list_dir", "real-l3-host", ALL, 1),
    ],
)
@pytest.mark.parametrize(
    "supplied",
    ["honest", "spoofed-l0-host", "wrong-alias", "", "anthropic"],
    ids=["honest", "spoofed", "wrong-alias", "missing", "provider-default"],
)
def test_the_operator_and_the_rewrite_name_the_registry_owner_whatever_the_model_supplied(
    tmp_path: Path,
    tool: str,
    owner: str,
    palette: frozenset[HITLResponse],
    dispatches: int,
    supplied: str,
) -> None:
    server = {
        "honest": owner,
        "wrong-alias": next(name for name in HOSTS if name != owner),
    }.get(supplied, supplied)
    loop, operator, dispatcher = _stage(tmp_path, HOSTS, HITLResponse.APPROVE)

    (result,) = asyncio.run(loop.run_tool_calls([_call(tool, server)], _context()))

    assert operator.prompts == [f"HITL tool call {tool} on {owner}"]
    assert operator.offered == [palette]  # the owner's real trust, not the label's
    assert result.rewritten_tool_call is not None
    assert result.rewritten_tool_call.server == owner
    assert len(dispatcher.calls) == dispatches
    if dispatches:
        assert dispatcher.calls[0][1].step_payload["tool_id"] == tool


@pytest.mark.parametrize("supplied", ["anthropic", "", "spoofed-l0-host"])
def test_search_tools_is_asked_as_the_in_process_owner(tmp_path: Path, supplied: str) -> None:
    loop, operator, dispatcher = _stage(tmp_path, HOSTS, HITLResponse.APPROVE)

    (result,) = asyncio.run(loop.run_tool_calls([_call("search_tools", supplied)], _context()))

    assert operator.prompts == ["HITL tool call search_tools on <in-process>"]
    assert operator.offered == [ALL]
    assert result.rewritten_tool_call is not None
    assert result.rewritten_tool_call.server == "<in-process>"
    assert result.dispatched is True
    assert dispatcher.calls == []  # answered in process, never the MCP dispatcher


def test_an_unregistered_tool_is_asked_as_unregistered_and_never_dispatches(
    tmp_path: Path,
) -> None:
    loop, operator, dispatcher = _stage(tmp_path, HOSTS, HITLResponse.APPROVE)

    (result,) = asyncio.run(loop.run_tool_calls([_call("not_a_tool", "real-l3-host")], _context()))

    assert operator.prompts == ["HITL tool call not_a_tool on <unregistered>"]
    assert operator.offered == [DENY_PALETTE]
    assert result.rewritten_tool_call is not None
    assert result.rewritten_tool_call.server == "<unregistered>"
    assert dispatcher.calls == []


def test_the_loop_hands_the_gate_and_dispatcher_the_assessed_owner(tmp_path: Path) -> None:
    stage_loop, _operator, _dispatcher = _stage(tmp_path, HOSTS, HITLResponse.APPROVE)
    gate, tools = _RecordingGate(), _RecordingDispatcher()
    loop = RuntimeHITLToolLoop(
        wiring=stage_loop.wiring,
        placement_registry=stage_loop.placement_registry,
        assess=lambda _call, _context: HITLToolCallAssessment(
            level=GateLevel.ASK, owner="canonical-host"
        ),
        gate=gate,
        dispatcher=tools,
        response_auditor=_Auditor(),
    )

    (result,) = asyncio.run(loop.run_tool_calls([_call("read_file", "spoofed")], _context()))

    assert [c.server for c in gate.calls] == ["canonical-host"]
    assert [c.server for c in tools.calls] == ["canonical-host"]
    assert result.rewritten_tool_call is not None
    assert result.rewritten_tool_call.server == "canonical-host"

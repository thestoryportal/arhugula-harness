"""Model tool-call DENY enforcement through the real stage-5 factory and tool loop.

The gate level comes from the owning MCP host's real trust tier (never a constant), the
operator sees only the palette that level allows, and no DENY outcome ever dispatches.
Provider-free: host and dispatcher doubles only. Scope is the DENY slice; the C-CP-20
operator-response audit is a separate, later slice and is not asserted here.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.hitl_response_palette import HITLResponse
from harness_runtime.bootstrap.factories.r_cxa_2_producer_loop_factory import (
    materialize_r_cxa_2_producer_loop_stage,
)
from harness_runtime.lifecycle.ask_user_question_surface import AskUserQuestionResult
from harness_runtime.lifecycle.hitl_tool_loop import ModelToolCall
from harness_runtime.lifecycle.tool_registry import ToolRegistry

from .test_r_cxa_2_producer_loop_factory import (
    _context,
    _post_tool_dispatcher_context,
    _ToolDispatcher,
)

ALL = frozenset(HITLResponse)
DENY_PALETTE = frozenset({HITLResponse.REJECT, HITLResponse.RESPOND})


class _Host:
    """`MCPClientHost` stand-in: the two attributes the trust and blast lookups read."""

    def __init__(self, trust: MCPTrustTier, *tools: str) -> None:
        self.trust_tier = trust
        self.tool_registry = ToolRegistry()
        for name in tools:
            self.tool_registry.register(
                ToolContract(
                    name=name,
                    description=name,
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    minimum_tier=SandboxTier.TIER_1_PROCESS,
                    blast_radius_tier=BlastRadiusTier.READ_ONLY,
                )
            )


class _BrokenHost:
    """A registered host whose registry lookup fails in an unexpected way."""

    trust_tier = MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT

    class _Registry:
        def get(self, _name: str) -> object:
            raise RuntimeError("registry offline")

    tool_registry = _Registry()


class _Operator:
    """Ask surface double answering with a scripted response; records what it was offered."""

    def __init__(self, order: list[str], response: HITLResponse, **fields: Any) -> None:
        self.order = order
        self.response = response
        self.fields = fields
        self.offered: list[frozenset[HITLResponse]] = []

    async def ask(
        self, prompt: str, options: tuple[HITLResponse, ...], timeout: float | None
    ) -> AskUserQuestionResult:
        _ = (prompt, timeout)
        self.order.append("gate")
        self.offered.append(frozenset(options))
        return AskUserQuestionResult(response=self.response, latency_ms=1.0, **self.fields)


def _call(tool: str, tool_call_id: str = "call-1") -> ModelToolCall:
    return ModelToolCall(
        tool_call_id=tool_call_id,
        tool=tool,
        server="srv",
        arguments={"query": "q"},
        provider="fixture-provider",
        model="fixture-model",
    )


def _run(
    tmp_path: Path,
    hosts: dict[str, Any],
    tool: str,
    response: HITLResponse,
    **fields: Any,
) -> tuple[Any, _Operator, _ToolDispatcher]:
    order: list[str] = []
    ctx, config, _surface, dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = hosts
    operator = _Operator(order, response, **fields)
    ctx.ask_user_question_surface = operator
    stage = materialize_r_cxa_2_producer_loop_stage(ctx, config)
    results = asyncio.run(stage.hitl_tool_loop.run_tool_calls([_call(tool)], _context()))
    return results[0], operator, dispatcher


@pytest.mark.parametrize("response", list(HITLResponse))
def test_a_tool_on_an_l0_host_offers_only_reject_and_respond_and_never_dispatches(
    tmp_path: Path, response: HITLResponse
) -> None:
    hosts = {"srv": _Host(MCPTrustTier.LEVEL_0_REFUSE_REMOTE, "read_file")}

    result, operator, dispatcher = _run(tmp_path, hosts, "read_file", response)

    assert operator.offered == [DENY_PALETTE]
    assert result.dispatched is False
    assert dispatcher.calls == []


@pytest.mark.parametrize(
    "trust", [MCPTrustTier.LEVEL_1_SIGNED_PINNED, MCPTrustTier.LEVEL_2_SANDBOX_ALL]
)
def test_a_tool_on_an_l1_or_l2_host_still_asks_with_every_response_and_dispatches_on_approve(
    tmp_path: Path, trust: MCPTrustTier
) -> None:
    result, operator, dispatcher = _run(
        tmp_path, {"srv": _Host(trust, "read_file")}, "read_file", HITLResponse.APPROVE
    )

    assert operator.offered == [ALL]
    assert result.dispatched is True
    assert len(dispatcher.calls) == 1


def test_edit_on_an_asked_tool_dispatches_the_edited_arguments(tmp_path: Path) -> None:
    result, _operator, dispatcher = _run(
        tmp_path,
        {"srv": _Host(MCPTrustTier.LEVEL_1_SIGNED_PINNED, "read_file")},
        "read_file",
        HITLResponse.EDIT,
        edited_proposal=json.dumps({"query": "edited"}),
    )

    assert result.dispatched is True
    assert dispatcher.calls[0][1].step_payload["tool_args"] == {"query": "edited"}


def test_a_tool_on_an_l3_host_is_asked_not_denied(tmp_path: Path) -> None:
    result, operator, dispatcher = _run(
        tmp_path,
        {"srv": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "read_file")},
        "read_file",
        HITLResponse.APPROVE,
    )

    assert operator.offered == [ALL]
    assert result.dispatched is True
    assert len(dispatcher.calls) == 1


@pytest.mark.parametrize("response", list(HITLResponse))
def test_an_unregistered_tool_is_denied(tmp_path: Path, response: HITLResponse) -> None:
    hosts = {"srv": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "read_file")}

    result, operator, dispatcher = _run(tmp_path, hosts, "not_a_tool", response)

    assert operator.offered == [DENY_PALETTE]
    assert result.dispatched is False
    assert dispatcher.calls == []


def test_search_tools_is_not_refused_by_the_host_less_default(tmp_path: Path) -> None:
    result, operator, _dispatcher = _run(tmp_path, {}, "search_tools", HITLResponse.APPROVE)

    assert operator.offered == [ALL]
    assert result.dispatched is True


def test_an_evaluator_failure_refuses_without_prompting_or_dispatching(tmp_path: Path) -> None:
    result, operator, dispatcher = _run(
        tmp_path, {"srv": _BrokenHost()}, "read_file", HITLResponse.APPROVE
    )

    assert operator.offered == []
    assert result.dispatched is False
    assert dispatcher.calls == []


# --- typed refusal, floors, ledger (API-level behavior) ---------------------------------

from dataclasses import replace

from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_as_tool_call_rewriting import (
    RewrittenToolCall,
    _canonicalize_outcome_bytes,  # pyright: ignore[reportPrivateUsage]
    _hitl_tool_call_rewriting_idempotency_key,  # pyright: ignore[reportPrivateUsage]
)
from harness_is.state_ledger_write import read_ledger
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLGateDecision,
    HITLToolLoopContext,
    HITLToolRefusalReason,
    RuntimeHITLToolLoop,
)

L0_HOSTS = {"srv": _Host(MCPTrustTier.LEVEL_0_REFUSE_REMOTE, "read_file")}
L3_HOSTS = {"srv": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "read_file")}


def test_respond_under_deny_refuses_but_preserves_the_operators_text(tmp_path: Path) -> None:
    result, _operator, dispatcher = _run(
        tmp_path, L0_HOSTS, "read_file", HITLResponse.RESPOND, response_text="use another tool"
    )

    assert result.dispatched is False
    assert dispatcher.calls == []
    assert result.refusal is not None
    assert result.refusal.reason is HITLToolRefusalReason.POLICY_DENY
    assert result.refusal.response_text == "use another tool"


@pytest.mark.parametrize("response", [HITLResponse.APPROVE, HITLResponse.EDIT])
def test_an_adapter_answer_outside_the_deny_palette_is_refused(
    tmp_path: Path, response: HITLResponse
) -> None:
    result, _operator, dispatcher = _run(tmp_path, L0_HOSTS, "read_file", response)

    assert dispatcher.calls == []
    assert result.refusal is not None
    assert result.refusal.reason is HITLToolRefusalReason.RESPONSE_OUTSIDE_PALETTE


def test_reject_under_deny_is_a_policy_refusal_not_a_silent_skip(tmp_path: Path) -> None:
    result, _operator, _dispatcher = _run(tmp_path, L0_HOSTS, "read_file", HITLResponse.REJECT)

    assert result.refusal is not None
    assert result.refusal.reason is HITLToolRefusalReason.POLICY_DENY
    assert result.refusal.response_text is None


def test_an_evaluator_failure_is_a_typed_refusal_with_no_ledger_entry(tmp_path: Path) -> None:
    order: list[str] = []
    ctx, config, _surface, _dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = {"srv": _BrokenHost()}
    stage = materialize_r_cxa_2_producer_loop_stage(ctx, config)

    results = asyncio.run(stage.hitl_tool_loop.run_tool_calls([_call("read_file")], _context()))

    assert results[0].refusal is not None
    assert results[0].refusal.reason is HITLToolRefusalReason.EVALUATOR_FAILED
    assert results[0].rewritten_tool_call is None
    assert read_ledger(stage.hitl_tool_loop.wiring.ledger_writer.handle) == []


class _ScriptedGate:
    def __init__(self, reply: object) -> None:
        self.reply = reply
        self.palettes: list[frozenset[HITLResponse]] = []

    async def decide(
        self, *, call: ModelToolCall, context: HITLToolLoopContext, palette: frozenset[HITLResponse]
    ) -> Any:
        _ = (call, context)
        self.palettes.append(palette)
        return self.reply


def _loop_with(stage_loop: RuntimeHITLToolLoop, gate: _ScriptedGate) -> RuntimeHITLToolLoop:
    return replace(stage_loop, gate=gate)


@pytest.mark.parametrize("hosts", [L0_HOSTS, L3_HOSTS], ids=["deny", "ask"])
def test_a_malformed_adapter_reply_never_dispatches(tmp_path: Path, hosts: dict[str, Any]) -> None:
    order: list[str] = []
    ctx, config, _surface, dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = hosts
    loop = materialize_r_cxa_2_producer_loop_stage(ctx, config).hitl_tool_loop
    gate = _ScriptedGate(reply=None)

    results = asyncio.run(_loop_with(loop, gate).run_tool_calls([_call("read_file")], _context()))

    assert dispatcher.calls == []
    assert results[0].refusal is not None
    assert results[0].refusal.reason is HITLToolRefusalReason.MALFORMED_GATE_REPLY


def test_a_response_the_palette_omits_is_refused_even_under_ask(tmp_path: Path) -> None:
    order: list[str] = []
    ctx, config, _surface, dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = L3_HOSTS
    loop = materialize_r_cxa_2_producer_loop_stage(ctx, config).hitl_tool_loop
    untrusted = replace(_context(), cross_trust_boundary_state=_untrusted_mcp())
    gate = _ScriptedGate(reply=HITLGateDecision(response=HITLResponse.APPROVE))

    results = asyncio.run(_loop_with(loop, gate).run_tool_calls([_call("read_file")], untrusted))

    assert gate.palettes == [DENY_PALETTE]  # the cross-trust narrowing is what was offered
    assert dispatcher.calls == []
    assert results[0].refusal is not None


def _untrusted_mcp() -> Any:
    from harness_cp.validator_fail_transient_staircase import CrossTrustBoundaryState

    return CrossTrustBoundaryState.UNTRUSTED_MCP_ACTIVE


def _with_floor(floor: GateLevel) -> HITLToolLoopContext:
    return replace(_context(), inherited_gate_floor=floor)


def _run_with_context(
    tmp_path: Path, context: HITLToolLoopContext
) -> tuple[Any, _Operator, _ToolDispatcher]:
    order: list[str] = []
    ctx, config, _surface, dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = L3_HOSTS
    operator = _Operator(order, HITLResponse.APPROVE)
    ctx.ask_user_question_surface = operator
    stage = materialize_r_cxa_2_producer_loop_stage(ctx, config)
    results = asyncio.run(stage.hitl_tool_loop.run_tool_calls([_call("read_file")], context))
    return results[0], operator, dispatcher


def test_a_descended_step_under_a_deny_parent_refuses_even_an_l3_tool(tmp_path: Path) -> None:
    result, operator, dispatcher = _run_with_context(tmp_path, _with_floor(GateLevel.DENY))

    assert operator.offered == [DENY_PALETTE]
    assert dispatcher.calls == []
    assert result.refusal is not None


def test_a_descended_step_under_an_ask_parent_still_prompts(tmp_path: Path) -> None:
    result, operator, dispatcher = _run_with_context(tmp_path, _with_floor(GateLevel.ASK))

    assert operator.offered == [ALL]
    assert result.dispatched is True
    assert len(dispatcher.calls) == 1


def test_the_rewrite_ledger_entry_records_the_narrowed_palette(tmp_path: Path) -> None:
    order: list[str] = []
    ctx, config, _surface, _dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    ctx.mcp_client_hosts = L0_HOSTS
    ctx.ask_user_question_surface = _Operator(order, HITLResponse.REJECT)
    stage = materialize_r_cxa_2_producer_loop_stage(ctx, config)

    results = asyncio.run(stage.hitl_tool_loop.run_tool_calls([_call("read_file")], _context()))

    rewritten = results[0].rewritten_tool_call
    assert rewritten is not None and rewritten.response_palette == DENY_PALETTE
    (entry,) = read_ledger(stage.hitl_tool_loop.wiring.ledger_writer.handle)

    def _key(palette: frozenset[HITLResponse]) -> str:
        outcome = RewrittenToolCall.model_validate(
            {**rewritten.model_dump(), "response_palette": palette}
        )
        assert rewritten.variant is not None
        return _hitl_tool_call_rewriting_idempotency_key(
            "wf-1",
            "step-1",
            "call-1",
            rewritten.variant.value,
            hashlib.sha256(_canonicalize_outcome_bytes(outcome)).hexdigest(),
        )

    assert str(entry.idempotency_key) == _key(DENY_PALETTE)
    assert str(entry.idempotency_key) != _key(ALL)

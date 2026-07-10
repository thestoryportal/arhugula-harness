"""U-1 slice 3a (B-18) — the DESCENDED sub-agent (child) frozen tool superset.

Closes the F1 latent C10 condition-2 gap surfaced in slice 1
(`.harness/u1-slice3-findings-and-f1-c10-gap.md`): a sub-agent (child-workflow)
inference step must NOT emit the parent's ``external-irreversible`` tools into
its inference context. The ADR-D4 §1.5 default-downgrade **REMOVE** half drops
those tools from a descended child's visibility superset.

Two witness layers, both provider-free:

1. **Compute-level** — ``compute_frozen_tool_superset(..., remove_tiers=...)``
   drops external-irreversible tools while keeping read-only / local-mutation /
   external-reversible (+ the memory tool).
2. **Dispatch-level** (the load-bearing by-execution witness) — a real
   ``RuntimeLLMDispatcher.dispatch`` with an MCP host carrying an
   ``EXTERNAL_IRREVERSIBLE`` tool T: a TOP-LEVEL inference emits T on the wire;
   a DESCENDED inference (``step_context.sub_agent_descent=True``) does NOT.
   At MVP the supersets are ``None`` (no MCP tools), so the fixture MUST carry a
   real irreversible tool for the test to prove anything.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_core import PersonaTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.frozen_tool_superset import (
    CHILD_DOWNGRADE_REMOVE_TIERS,
    compute_frozen_tool_superset,
)
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.lifecycle.memory_tool_dispatch import MEMORY_TOOL_TYPE
from harness_runtime.lifecycle.tool_registry import ToolRegistry
from opentelemetry.sdk.trace import TracerProvider


# --------------------------------------------------------------------------
# Offline fixtures — fake MCP hosts + tiered tool contracts
# --------------------------------------------------------------------------
class _FakeHost:
    """Minimal MCPClientHost stand-in exposing `.tool_registry` only."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.tool_registry = registry


def _contract(name: str, tier: BlastRadiusTier) -> ToolContract:
    return ToolContract(
        name=name,
        description=f"{name} tool",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        minimum_tier=SandboxTier.TIER_1_PROCESS,
        blast_radius_tier=tier,
    )


def _registry(contracts: Iterable[ToolContract]) -> ToolRegistry:
    reg = ToolRegistry()
    for c in contracts:
        reg.register(c)
    return reg


def _all_tier_hosts() -> dict[str, Any]:
    """One host carrying a tool at each of the four blast-radius tiers."""
    return {
        "srv": _FakeHost(
            _registry(
                [
                    _contract("read_tool", BlastRadiusTier.READ_ONLY),
                    _contract("local_tool", BlastRadiusTier.LOCAL_MUTATION),
                    _contract("reversible_tool", BlastRadiusTier.EXTERNAL_REVERSIBLE),
                    _contract("irreversible_tool", BlastRadiusTier.EXTERNAL_IRREVERSIBLE),
                ]
            )
        )
    }


def _names(superset: tuple[Any, ...] | None) -> list[str]:
    assert superset is not None
    return [t["name"] for t in superset if "name" in t and "input_schema" in t]


# ==========================================================================
# Layer 1 — compute-level REMOVE filter
# ==========================================================================
def test_child_superset_drops_external_irreversible_keeps_the_rest() -> None:
    hosts = _all_tier_hosts()
    full = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    child = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    # Parent SEES the irreversible tool; child does NOT.
    assert "irreversible_tool" in _names(full)
    assert "irreversible_tool" not in _names(child)
    # The other three tiers stay VISIBLE in the child (only REMOVE, per §1.5).
    assert set(_names(child)) == {"read_tool", "local_tool", "reversible_tool"}


def test_full_superset_default_is_byte_identical_to_no_filter() -> None:
    hosts = _all_tier_hosts()
    default = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    empty_filter = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=frozenset()
    )
    assert default == empty_filter


def test_child_downgrade_is_idempotent_uniform_across_depth() -> None:
    # The child ceiling is uniform (READ_ONLY), so a descended child and a
    # descended grandchild compute the SAME downgraded set from the SAME hosts
    # (monotonic-sticky descent — REMOVE drops nothing more the second time).
    hosts = _all_tier_hosts()
    child = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    grandchild = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    assert child == grandchild


def test_child_superset_none_when_only_irreversible_tools() -> None:
    # A registry whose only tool is external-irreversible → child union empty →
    # None → the descended dispatch falls back to `payload.tools` (no leak).
    hosts = {
        "srv": _FakeHost(
            _registry([_contract("only_irrev", BlastRadiusTier.EXTERNAL_IRREVERSIBLE)])
        )
    }
    assert compute_frozen_tool_superset(hosts, include_memory_tool=False) is not None
    assert (
        compute_frozen_tool_superset(
            hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
        )
        is None
    )


def test_memory_tool_retained_in_child_superset() -> None:
    # The memory tool is NOT blast-radius-classified → it survives the REMOVE
    # filter (a descended memory-capable child still sees its memory tool).
    hosts = {
        "srv": _FakeHost(
            _registry([_contract("irreversible_tool", BlastRadiusTier.EXTERNAL_IRREVERSIBLE)])
        )
    }
    child = compute_frozen_tool_superset(
        hosts, include_memory_tool=True, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    assert child == ({"type": MEMORY_TOOL_TYPE, "name": "memory"},)


# ==========================================================================
# Layer 2 — dispatch-level witness (real RuntimeLLMDispatcher.dispatch)
# ==========================================================================
class _Usage:
    def __init__(self) -> None:
        self.input_tokens = 10
        self.output_tokens = 5
        self.cache_creation_input_tokens = 0
        self.cache_read_input_tokens = 0


class _Response:
    def __init__(self) -> None:
        self.id = "msg_test"
        self.usage = _Usage()

    def model_dump(self) -> dict[str, Any]:
        return {"id": self.id, "content": [{"text": "ok"}]}


class _AnthropicMessages:
    def __init__(self) -> None:
        self.last_kwargs: dict[str, Any] | None = None

    async def create(self, **kwargs: Any) -> _Response:
        self.last_kwargs = kwargs
        return _Response()


class _AnthropicClient:
    def __init__(self) -> None:
        self.messages = _AnthropicMessages()


class _AnthropicFakeAdapter:
    def __init__(self, client: _AnthropicClient) -> None:
        self.client = client


def _binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider="anthropic", model="claude-test"),
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
            "params": {"max_tokens": 16},
        },
    )


def _step_context(*, sub_agent_descent: bool) -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="test-step-key",
        tenant_id=None,
        step_index=0,
        sub_agent_descent=sub_agent_descent,
    )


def _dispatcher_with_supersets() -> tuple[RuntimeLLMDispatcher, _AnthropicClient]:
    hosts = _all_tier_hosts()
    full = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    child = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    client = _AnthropicClient()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        frozen_tool_superset=full,
        child_frozen_tool_superset=child,
    )
    return dispatcher, client


@pytest.mark.asyncio
async def test_top_level_dispatch_emits_irreversible_tool_on_the_wire() -> None:
    dispatcher, client = _dispatcher_with_supersets()
    await dispatcher.dispatch(
        _binding(), _step(), step_context=_step_context(sub_agent_descent=False)
    )
    wire_tools = [t["name"] for t in (client.messages.last_kwargs or {})["tools"]]
    assert "irreversible_tool" in wire_tools


@pytest.mark.asyncio
async def test_descended_child_dispatch_omits_irreversible_tool_on_the_wire() -> None:
    dispatcher, client = _dispatcher_with_supersets()
    await dispatcher.dispatch(
        _binding(), _step(), step_context=_step_context(sub_agent_descent=True)
    )
    wire_tools = [t["name"] for t in (client.messages.last_kwargs or {})["tools"]]
    # F1 CLOSED: the descended child does NOT see the parent's irreversible tool,
    # but DOES still see the read-only / local-mutation / external-reversible set.
    assert "irreversible_tool" not in wire_tools
    assert {"read_tool", "local_tool", "reversible_tool"} <= set(wire_tools)


def _step_declaring(tools: list[dict[str, Any]]) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": tools,
            "params": {"max_tokens": 16},
        },
    )


@pytest.mark.asyncio
async def test_descended_child_all_removed_sends_empty_tools_not_payload_fallback() -> None:
    # Out-of-family Codex [P2] regression: when the parent registry holds ONLY an
    # external-irreversible tool, the child superset is None (ALL removed). A
    # descended child whose STEP DECLARES that tool must NOT fall back to
    # `payload.tools` (which would re-expose the removed tool) — it must send an
    # EMPTY tools list. The two `None` meanings (no-MCP-tools vs all-removed) are
    # disambiguated by the parent superset being non-None.
    hosts = {
        "srv": _FakeHost(
            _registry([_contract("irreversible_tool", BlastRadiusTier.EXTERNAL_IRREVERSIBLE)])
        )
    }
    full = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    child = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    assert full is not None and child is None  # parent has T; child dropped it all
    client = _AnthropicClient()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        frozen_tool_superset=full,
        child_frozen_tool_superset=child,
    )
    declared = [
        {"name": "irreversible_tool", "description": "d", "input_schema": {"type": "object"}}
    ]
    await dispatcher.dispatch(
        _binding(), _step_declaring(declared), step_context=_step_context(sub_agent_descent=True)
    )
    # Empty child superset → `tools: []` on the wire — the declared irreversible
    # tool is NOT re-exposed via the payload.tools fallback.
    assert (client.messages.last_kwargs or {})["tools"] == []


@pytest.mark.asyncio
async def test_top_level_all_removed_step_still_uses_payload_tools() -> None:
    # Contrast: a TOP-LEVEL (non-descended) dispatch is unaffected — the full
    # superset (which HAS the irreversible tool) replaces payload.tools, so the
    # top-level agent still sees it (only the descended child is downgraded).
    hosts = {
        "srv": _FakeHost(
            _registry([_contract("irreversible_tool", BlastRadiusTier.EXTERNAL_IRREVERSIBLE)])
        )
    }
    full = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    child = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, remove_tiers=CHILD_DOWNGRADE_REMOVE_TIERS
    )
    client = _AnthropicClient()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        frozen_tool_superset=full,
        child_frozen_tool_superset=child,
    )
    await dispatcher.dispatch(
        _binding(), _step(), step_context=_step_context(sub_agent_descent=False)
    )
    wire = [t["name"] for t in (client.messages.last_kwargs or {})["tools"]]
    assert "irreversible_tool" in wire

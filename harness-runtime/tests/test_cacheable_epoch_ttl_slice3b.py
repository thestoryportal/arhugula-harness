"""U-1 slice 3b (B-18) — workload-class-aware Anthropic prompt-cache ttl.

Materializes the ttl-selection half of the ADR-D3 §1.5 cacheable-epoch contract
(`ttl: 5min default; 1hr at Persona §6 cost-ceiling cells`). The run's
`workload_class` (bound at bootstrap stage 5) selects the 1hr tier iff the
operator opted that class into `RuntimeConfig.prompt_cache_long_ttl_workloads`,
else the 5min default. The selected ttl rides `RuntimeLLMDispatcher.cache_ttl`
and is consumed at the translate seam where the `cache_control` breakpoint is
placed (tools block, slice 1; OR system block, slice 2).

Three witness layers, all provider-free (no paid Anthropic calls):

1. **Selection** — `select_cache_ttl` pure function.
2. **Translate seam** — `_payload_to_anthropic_kwargs(..., cache_ttl=...)` emits
   the chosen ttl on the marker (tools-block AND system-block paths); the default
   `"5m"` reproduces the pre-slice-3b directive byte-for-byte.
3. **Full-chain dispatch** — a real `RuntimeLLMDispatcher` bound with
   `cache_ttl="1h"` emits `ttl: "1h"` on the wire marker (the load-bearing
   by-execution witness that `self.cache_ttl` reaches `messages.create`).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_core import PersonaTier
from harness_core.deployment_surface import DeploymentSurface
from harness_core.identity import StepID
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ModelBinding, ProviderAgnosticPayload
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.cacheable_epoch import (
    DEFAULT_CACHE_TTL,
    LONG_CACHE_TTL,
    CacheTTL,
    select_cache_ttl,
)
from harness_runtime.lifecycle.frozen_tool_superset import compute_frozen_tool_superset
from harness_runtime.lifecycle.llm_dispatch import (
    RuntimeLLMDispatcher,
    _payload_to_anthropic_kwargs,
)
from harness_runtime.types import OTelConfig, RuntimeConfig
from opentelemetry.sdk.trace import TracerProvider
from pydantic import ValidationError

# --------------------------------------------------------------------------
# Offline fixtures
# --------------------------------------------------------------------------
_ALL = frozenset(WorkloadClass)


class _FakeHost:
    def __init__(self, registry: Any) -> None:
        self.tool_registry = registry


def _contract(name: str, *, schema: dict[str, Any] | None = None) -> ToolContract:
    return ToolContract(
        name=name,
        description="d",
        input_schema=schema if schema is not None else {"type": "object"},
        output_schema={"type": "object"},
        minimum_tier=SandboxTier.TIER_1_PROCESS,
        blast_radius_tier=BlastRadiusTier.READ_ONLY,
    )


def _registry(contracts: Iterable[ToolContract]) -> Any:
    from harness_runtime.lifecycle.tool_registry import ToolRegistry

    reg = ToolRegistry()
    for c in contracts:
        reg.register(c)
    return reg


def _big_schema(field_count: int) -> dict[str, Any]:
    """A schema big enough that the serialized superset alone clears the ≥4096-tok
    (~16KB serialized) non-vacuity floor (mirrors the slice-2 fixture)."""
    return {
        "type": "object",
        "properties": {
            f"field_{i}": {
                "type": "string",
                "description": "x" * 200,
                "title": f"Field number {i} with a long descriptive title",
            }
            for i in range(field_count)
        },
    }


def _big_superset() -> tuple[Any, ...]:
    """A superset whose serialized size alone clears the ≥4096-tok non-vacuity floor."""
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("alpha", schema=_big_schema(80))]))},
        include_memory_tool=False,
    )
    assert superset is not None
    # Guard the fixture itself: below the floor the marker never lands and every
    # ttl assertion below would vacuously KeyError rather than test the ttl.
    from harness_runtime.lifecycle.llm_dispatch import _superset_clears_non_vacuity_floor

    assert _superset_clears_non_vacuity_floor(superset)
    return superset


def _payload() -> ProviderAgnosticPayload:
    return ProviderAgnosticPayload(
        messages=({"role": "user", "content": "hi"},),
        tools=None,
        params={"max_tokens": 16},
    )


_SYSTEM = "You are the active harness prompt."


# ==========================================================================
# Layer 1 — select_cache_ttl (pure selection)
# ==========================================================================
def test_select_ttl_empty_optin_is_always_default_5m() -> None:
    for wc in WorkloadClass:
        assert select_cache_ttl(wc, frozenset()) == DEFAULT_CACHE_TTL == "5m"


def test_select_ttl_member_class_gets_1h() -> None:
    optin = frozenset({WorkloadClass.PIPELINE_AUTOMATION})
    assert select_cache_ttl(WorkloadClass.PIPELINE_AUTOMATION, optin) == LONG_CACHE_TTL == "1h"


def test_select_ttl_non_member_class_stays_5m() -> None:
    optin = frozenset({WorkloadClass.PIPELINE_AUTOMATION})
    assert select_cache_ttl(WorkloadClass.RESEARCH, optin) == "5m"


def test_select_ttl_none_workload_is_default_even_if_all_optin() -> None:
    # No run workload (bare/non-inference) → default, never 1h.
    assert select_cache_ttl(None, _ALL) == "5m"


def _config(long_ttl: list[str] | None = None) -> RuntimeConfig:
    """A minimal valid RuntimeConfig; `long_ttl` is the raw operator-supplied
    list of workload-class STRINGS (the TOML/JSON/kwarg shape)."""
    kwargs: dict[str, Any] = {
        "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
        "repository_root": Path("/tmp"),
        "otel": OTelConfig(otlp_endpoint="http://localhost:4318"),
        "default_topology": TopologyPattern.SINGLE_THREADED_LINEAR,
    }
    if long_ttl is not None:
        kwargs["prompt_cache_long_ttl_workloads"] = long_ttl
    return RuntimeConfig(**kwargs)


def test_config_coerces_string_list_to_workload_class_frozenset_then_selects_1h() -> None:
    # The load-bearing operator path: a raw string list on RuntimeConfig coerces
    # to a frozenset of ENUM members (not bare strings), and feeding it to
    # `select_cache_ttl` yields 1h for a member and 5m for a non-member. Without
    # this, the coercion could silently misbehave and an opted-in operator would
    # get 5m anyway (a cost feature that is secretly a no-op).
    cfg = _config(long_ttl=["pipeline-automation"])
    optin = cfg.prompt_cache_long_ttl_workloads
    assert optin == frozenset({WorkloadClass.PIPELINE_AUTOMATION})
    assert all(isinstance(x, WorkloadClass) for x in optin)
    assert select_cache_ttl(WorkloadClass.PIPELINE_AUTOMATION, optin) == "1h"
    assert select_cache_ttl(WorkloadClass.RESEARCH, optin) == "5m"


def test_config_default_optin_is_empty_frozenset() -> None:
    # The zero-config default → every class 5m (byte-identical to pre-slice-3b).
    assert _config().prompt_cache_long_ttl_workloads == frozenset()


def test_config_rejects_unknown_workload_class() -> None:
    # A bad opt-in value is fail-loud at construction (not silently dropped).
    with pytest.raises(ValidationError):
        _config(long_ttl=["not-a-real-workload-class"])


# ==========================================================================
# Layer 2 — translate seam emits the selected ttl on the marker
# ==========================================================================
def test_tools_block_marker_carries_1h_when_selected() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(
        _payload(), system=None, frozen_tool_superset=superset, cache_ttl="1h"
    )
    assert kwargs["tools"][-1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


def test_system_block_marker_carries_1h_when_selected() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(
        _payload(), system=_SYSTEM, frozen_tool_superset=superset, cache_ttl="1h"
    )
    assert kwargs["system"] == [
        {"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral", "ttl": "1h"}}
    ]
    assert all("cache_control" not in t for t in kwargs["tools"])


def test_default_ttl_is_5m_byte_identical_tools_block() -> None:
    # Omitting cache_ttl reproduces the pre-slice-3b directive verbatim.
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(_payload(), system=None, frozen_tool_superset=superset)
    assert kwargs["tools"][-1]["cache_control"] == {"type": "ephemeral", "ttl": "5m"}


def test_default_ttl_is_5m_byte_identical_system_block() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=superset)
    assert kwargs["system"] == [
        {"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral", "ttl": "5m"}}
    ]


def test_ttl_only_changes_ttl_value_not_which_block_is_marked() -> None:
    # ttl is orthogonal to slice 1/2 placement: with a system prompt the single
    # breakpoint is on the system block for BOTH ttls (tools stay unmarked).
    superset = _big_superset()
    for ttl in ("5m", "1h"):
        kwargs = _payload_to_anthropic_kwargs(
            _payload(), system=_SYSTEM, frozen_tool_superset=superset, cache_ttl=ttl
        )
        system_markers = sum(
            1 for b in kwargs["system"] if isinstance(b, dict) and "cache_control" in b
        )
        tool_markers = sum(1 for t in kwargs["tools"] if "cache_control" in t)
        assert system_markers == 1
        assert tool_markers == 0


# ==========================================================================
# Layer 3 — full-chain dispatch witness (self.cache_ttl reaches the wire)
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


def _step_context() -> StepExecutionContext:
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
        sub_agent_descent=False,
    )


def _dispatcher(cache_ttl: CacheTTL) -> tuple[RuntimeLLMDispatcher, _AnthropicClient]:
    client = _AnthropicClient()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        frozen_tool_superset=_big_superset(),
        cache_ttl=cache_ttl,
    )
    return dispatcher, client


@pytest.mark.asyncio
async def test_dispatcher_cache_ttl_1h_reaches_the_wire_marker() -> None:
    dispatcher, client = _dispatcher("1h")
    await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    wire_tools = (client.messages.last_kwargs or {})["tools"]
    assert wire_tools[-1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


@pytest.mark.asyncio
async def test_dispatcher_default_cache_ttl_is_5m_on_the_wire() -> None:
    # A dispatcher constructed WITHOUT cache_ttl defaults to 5m (byte-identical).
    client = _AnthropicClient()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _AnthropicFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        frozen_tool_superset=_big_superset(),
    )
    assert dispatcher.cache_ttl == "5m"
    await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    wire_tools = (client.messages.last_kwargs or {})["tools"]
    assert wire_tools[-1]["cache_control"] == {"type": "ephemeral", "ttl": "5m"}

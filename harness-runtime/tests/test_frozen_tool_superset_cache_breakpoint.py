"""U-1 (B-18) — offline tests for the Anthropic prompt-cache `cache_control`
breakpoint on the frozen tool superset (ADR-D3 §1.5 slice 1).

Provider-free lane: exercises the pure translate seam
(`_payload_to_anthropic_kwargs`) + the superset-computation helper
(`compute_frozen_tool_superset`) directly. NO paid provider calls. The
credential-gated live cache-hit proof lives at the bottom, marked
`@pytest.mark.e2e` (kept OUT of the provider-free lanes) — it is a PAID
Anthropic call and MUST NOT be run here.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from typing import Any

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_runtime.lifecycle.frozen_tool_superset import (
    compute_frozen_tool_superset,
)
from harness_runtime.lifecycle.llm_dispatch import _payload_to_anthropic_kwargs
from harness_runtime.lifecycle.memory_tool_dispatch import MEMORY_TOOL_TYPE
from harness_runtime.lifecycle.tool_registry import ToolRegistry


# --------------------------------------------------------------------------
# Fixtures — offline fake MCP hosts (no real server startup)
# --------------------------------------------------------------------------
class _FakeHost:
    """Minimal stand-in for an MCPClientHost — exposes `.tool_registry` only.

    The frozen-superset computation reads only `host.tool_registry.names()` /
    `.get(name)`, so a real (already-started) `ToolRegistry` populated directly
    is a faithful offline substitute.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self.tool_registry = registry


def _contract(
    name: str, *, description: str = "d", schema: dict[str, Any] | None = None
) -> ToolContract:
    return ToolContract(
        name=name,
        description=description,
        input_schema=schema if schema is not None else {"type": "object"},
        output_schema={"type": "object"},
        minimum_tier=SandboxTier.TIER_1_PROCESS,
        blast_radius_tier=BlastRadiusTier.READ_ONLY,
    )


def _registry(contracts: Iterable[ToolContract]) -> ToolRegistry:
    reg = ToolRegistry()
    for c in contracts:
        reg.register(c)
    return reg


def _big_schema(field_count: int) -> dict[str, Any]:
    """A schema big enough that the serialized superset clears the ≥4096-tok
    (~16KB serialized) non-vacuity floor."""
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
    """A superset whose serialized size clears the ≥4096-tok floor."""
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("alpha", schema=_big_schema(60))]))},
        include_memory_tool=False,
    )
    assert superset is not None
    return superset


def _payload(
    *, tools: tuple[Any, ...] | None = None, params: dict[str, Any] | None = None
) -> ProviderAgnosticPayload:
    return ProviderAgnosticPayload(
        messages=({"role": "user", "content": "hi"},),
        tools=tools,
        params=params if params is not None else {"max_tokens": 16},
    )


_CACHE_CONTROL = {"cache_control": {"type": "ephemeral", "ttl": "5m"}}


# --------------------------------------------------------------------------
# Emission — cache_control on the last block when bound + gates pass
# --------------------------------------------------------------------------
def test_bound_superset_marks_last_tool_and_replaces_payload_tools() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(_payload(), frozen_tool_superset=superset)

    # The wire tools equal the frozen superset, order-stable, save for the
    # cache_control marker on the last block.
    assert kwargs["tools"][-1]["cache_control"] == _CACHE_CONTROL["cache_control"]
    stripped_last = {k: v for k, v in kwargs["tools"][-1].items() if k != "cache_control"}
    assert tuple([*kwargs["tools"][:-1], stripped_last]) == superset


def test_memory_server_tool_block_never_receives_the_marker() -> None:
    # A memory-capable superset appends the server-side memory tool (`type` +
    # `name`, NO `input_schema`) LAST. The cache_control marker must land on the
    # last CLIENT tool (input_schema-bearing), NEVER the server-tool block —
    # server-tool blocks may not accept cache_control (a silent cache miss).
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("alpha", schema=_big_schema(60))]))},
        include_memory_tool=True,
    )
    assert superset is not None
    # the memory block is last and is a server-side tool (no input_schema).
    assert superset[-1]["type"] == MEMORY_TOOL_TYPE
    assert "input_schema" not in superset[-1]

    kwargs = _payload_to_anthropic_kwargs(_payload(), frozen_tool_superset=superset)
    wire = kwargs["tools"]
    # the trailing memory block carries NO cache_control.
    assert "cache_control" not in wire[-1]
    # exactly one block carries cache_control, and it is a client tool.
    marked = [t for t in wire if "cache_control" in t]
    assert len(marked) == 1
    assert "input_schema" in marked[0]


def test_bound_superset_does_not_mutate_frozen_tuple() -> None:
    superset = _big_superset()
    _payload_to_anthropic_kwargs(_payload(), frozen_tool_superset=superset)
    # The frozen tuple's dicts must NOT gain cache_control in place.
    assert all("cache_control" not in tool for tool in superset)


# --------------------------------------------------------------------------
# Byte-stability — the load-bearing "actually caches something" proof
# --------------------------------------------------------------------------
def test_two_dispatches_same_superset_are_byte_identical() -> None:
    superset = _big_superset()
    kwargs_a = _payload_to_anthropic_kwargs(_payload(), frozen_tool_superset=superset)
    kwargs_b = _payload_to_anthropic_kwargs(_payload(), frozen_tool_superset=superset)

    def _canon(tools: Any) -> str:
        return json.dumps(tools, sort_keys=True, separators=(",", ":"))

    assert _canon(kwargs_a["tools"]) == _canon(kwargs_b["tools"])


# --------------------------------------------------------------------------
# No-regression — None superset is byte-identical to the legacy path
# --------------------------------------------------------------------------
def test_none_superset_is_byte_identical_to_legacy_tools_path() -> None:
    tools = ({"name": "legacy", "description": "d", "input_schema": {"type": "object"}},)
    payload = _payload(tools=tools)

    legacy = _payload_to_anthropic_kwargs(payload, frozen_tool_superset=None)
    assert legacy["tools"] == list(payload.tools)  # type: ignore[arg-type]
    assert all("cache_control" not in tool for tool in legacy["tools"])


def test_none_superset_and_no_payload_tools_omits_tools_key() -> None:
    payload = _payload(tools=None)
    kwargs = _payload_to_anthropic_kwargs(payload, frozen_tool_superset=None)
    assert "tools" not in kwargs


# --------------------------------------------------------------------------
# Non-vacuity gate — below the ≥4096-tok floor emits NO marker
# --------------------------------------------------------------------------
def test_below_floor_superset_emits_no_cache_control() -> None:
    small = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("tiny")]))},
        include_memory_tool=False,
    )
    assert small is not None
    kwargs = _payload_to_anthropic_kwargs(_payload(), frozen_tool_superset=small)
    # Tools are sent (stable prefix) but WITHOUT the vacuous marker.
    assert kwargs["tools"] == list(small)
    assert all("cache_control" not in tool for tool in kwargs["tools"])


# --------------------------------------------------------------------------
# Extended-thinking gate — no breakpoint when thinking is enabled
# --------------------------------------------------------------------------
def test_extended_thinking_mode_skips_breakpoint() -> None:
    superset = _big_superset()
    payload = _payload(
        params={"max_tokens": 16, "thinking": {"type": "enabled", "budget_tokens": 1024}}
    )
    kwargs = _payload_to_anthropic_kwargs(payload, frozen_tool_superset=superset)
    # Superset still sent (stable prefix), but no marker under extended thinking.
    assert kwargs["tools"] == list(superset)
    assert all("cache_control" not in tool for tool in kwargs["tools"])


# --------------------------------------------------------------------------
# Superset computation — deterministic order + dedup + memory inclusion
# --------------------------------------------------------------------------
def test_superset_is_sorted_by_name_across_hosts() -> None:
    hosts = {
        "srv_b": _FakeHost(_registry([_contract("zeta"), _contract("alpha")])),
        "srv_a": _FakeHost(_registry([_contract("mike")])),
    }
    superset = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    assert superset is not None
    assert [t["name"] for t in superset] == ["alpha", "mike", "zeta"]


def test_superset_is_deterministic_across_two_builds() -> None:
    def _hosts() -> dict[str, Any]:
        return {
            "srv_b": _FakeHost(
                _registry([_contract("zeta", schema=_big_schema(3)), _contract("alpha")])
            ),
            "srv_a": _FakeHost(_registry([_contract("mike")])),
        }

    first = compute_frozen_tool_superset(_hosts(), include_memory_tool=False)
    second = compute_frozen_tool_superset(_hosts(), include_memory_tool=False)
    assert first is not None and second is not None
    assert json.dumps(list(first), sort_keys=True) == json.dumps(list(second), sort_keys=True)


def test_input_schema_keys_are_canonicalized_recursively() -> None:
    unsorted = {"b": 1, "a": {"d": 2, "c": 3}}
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("t", schema=unsorted)]))},
        include_memory_tool=False,
    )
    assert superset is not None
    serialized = json.dumps(superset[0]["input_schema"])
    # Recursive key-sort: "a" before "b" at top level, "c" before "d" nested.
    assert serialized.index('"a"') < serialized.index('"b"')
    assert serialized.index('"c"') < serialized.index('"d"')


def test_memory_tool_included_when_flagged() -> None:
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("alpha")]))},
        include_memory_tool=True,
    )
    assert superset is not None
    assert superset[-1] == {"type": MEMORY_TOOL_TYPE, "name": "memory"}


def test_empty_union_returns_none() -> None:
    assert compute_frozen_tool_superset(None, include_memory_tool=False) is None
    assert compute_frozen_tool_superset({}, include_memory_tool=False) is None


def test_memory_only_run_still_produces_a_superset() -> None:
    superset = compute_frozen_tool_superset(None, include_memory_tool=True)
    assert superset == ({"type": MEMORY_TOOL_TYPE, "name": "memory"},)


# ==========================================================================
# CREDENTIAL-GATED LIVE e2e — PAID Anthropic call. DO NOT RUN in CI / offline
# lanes. Marked `@pytest.mark.e2e` so it is deselected from provider-free
# runs. Left here as the load-bearing live cache-hit proof (build, don't fire).
# ==========================================================================
@pytest.mark.e2e
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="live Anthropic cache-hit proof — requires ANTHROPIC_API_KEY (PAID call)",
)
async def test_live_frozen_superset_cache_hit() -> None:  # pragma: no cover
    """Two identical-prefix real Anthropic dispatches: call 1 creates the cache,
    call 2 reads it. Asserts `usage.cache_creation_input_tokens > 0` then
    `usage.cache_read_input_tokens > 0` (`llm_dispatch.py` cache-attr sites).

    PAID call — surfaced at the operator's paid-call boundary, NOT auto-fired.
    """
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(
        _payload(params={"max_tokens": 16}), frozen_tool_superset=superset
    )
    model = "claude-3-5-haiku-latest"

    first = await client.messages.create(model=model, **kwargs)
    assert (first.usage.cache_creation_input_tokens or 0) > 0

    second = await client.messages.create(model=model, **kwargs)
    assert (second.usage.cache_read_input_tokens or 0) > 0

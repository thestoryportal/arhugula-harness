"""U-1 (B-18) slice 2 — offline tests for the Anthropic prompt-cache
``cache_control`` breakpoint MOVED to the system content-block array (ADR-D3
§1.5 full parent breakpoint = end of ``[tools + system]``).

Provider-free lane: exercises the pure translate seam
(``_payload_to_anthropic_kwargs``) directly with a ``system`` prompt + a bound
frozen superset. NO paid provider calls. The credential-gated live combined
``[tools + system]`` cache-hit proof lives at the bottom, marked
``@pytest.mark.e2e`` (kept OUT of the provider-free lanes) — it is a PAID
Anthropic call and MUST NOT be run here (build, don't fire).

Slice 1's tools-block-marker behavior is preserved when NO system prompt is
present; those cases are covered at
``test_frozen_tool_superset_cache_breakpoint.py``. This module covers the
slice-2 delta: the single breakpoint moves to the system block when a system
prompt is present and the combined prefix clears floor, the tools go unmarked
(no double-marking), and every below-floor / no-superset / extended-thinking
path keeps the plain-string ``system`` (byte-identical to slice 1).
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
from harness_runtime.lifecycle.llm_dispatch import (
    _payload_to_anthropic_kwargs,
    _payload_to_ollama_kwargs,
    _payload_to_openai_kwargs,
)


# --------------------------------------------------------------------------
# Fixtures — offline fake MCP hosts (no real server startup)
# --------------------------------------------------------------------------
class _FakeHost:
    """Minimal stand-in for an MCPClientHost — exposes `.tool_registry` only."""

    def __init__(self, registry: Any) -> None:
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


def _registry(contracts: Iterable[ToolContract]) -> Any:
    from harness_runtime.lifecycle.tool_registry import ToolRegistry

    reg = ToolRegistry()
    for c in contracts:
        reg.register(c)
    return reg


def _big_schema(field_count: int) -> dict[str, Any]:
    """A schema big enough that the serialized superset alone clears the ≥4096-tok
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
    """A superset whose serialized size alone clears the ≥4096-tok floor."""
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("alpha", schema=_big_schema(60))]))},
        include_memory_tool=False,
    )
    assert superset is not None
    return superset


def _small_superset() -> tuple[Any, ...]:
    """A tiny superset whose serialized size is far below the floor."""
    superset = compute_frozen_tool_superset(
        {"srv": _FakeHost(_registry([_contract("tiny")]))},
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


_CACHE_CONTROL = {"type": "ephemeral", "ttl": "5m"}
_SYSTEM = "You are the active harness prompt."


# --------------------------------------------------------------------------
# Slice-2 emission — the single breakpoint moves to the system block
# --------------------------------------------------------------------------
def test_system_present_combined_over_floor_marks_system_block_not_tools() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=superset)

    # `system` is the OQ-1 content-block array with the breakpoint on its last block.
    assert kwargs["system"] == [{"type": "text", "text": _SYSTEM, "cache_control": _CACHE_CONTROL}]
    # `tools` is the frozen superset with NO cache_control (marker moved to system).
    assert kwargs["tools"] == list(superset)
    assert all("cache_control" not in t for t in kwargs["tools"])


def test_exactly_one_breakpoint_across_system_and_tools() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=superset)
    tool_markers = sum(1 for t in kwargs["tools"] if "cache_control" in t)
    system_markers = sum(
        1 for block in kwargs["system"] if isinstance(block, dict) and "cache_control" in block
    )
    assert tool_markers == 0
    assert system_markers == 1


def test_system_marker_only_when_combined_clears_floor_via_system_length() -> None:
    """A small superset (below the superset-only floor) PLUS a very large system
    prompt whose combined length clears the floor still marks the system block —
    the floor is the COMBINED prefix, not the superset alone."""
    small = _small_superset()
    huge_system = "s" * 20000  # ~5000 tok alone; combined easily clears the floor
    kwargs = _payload_to_anthropic_kwargs(
        _payload(), system=huge_system, frozen_tool_superset=small
    )
    assert kwargs["system"] == [
        {"type": "text", "text": huge_system, "cache_control": _CACHE_CONTROL}
    ]
    assert all("cache_control" not in t for t in kwargs["tools"])


# --------------------------------------------------------------------------
# No system prompt — slice-1 behavior preserved (marker on last client tool)
# --------------------------------------------------------------------------
def test_no_system_but_superset_over_floor_keeps_slice1_tools_marker() -> None:
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(_payload(), system=None, frozen_tool_superset=superset)

    assert "system" not in kwargs
    assert kwargs["tools"][-1]["cache_control"] == _CACHE_CONTROL
    stripped_last = {k: v for k, v in kwargs["tools"][-1].items() if k != "cache_control"}
    assert tuple([*kwargs["tools"][:-1], stripped_last]) == superset


# --------------------------------------------------------------------------
# Below-floor — plain string system, NO marker anywhere
# --------------------------------------------------------------------------
def test_system_present_combined_below_floor_plain_string_no_marker() -> None:
    small = _small_superset()  # combined with a short system stays below floor
    kwargs = _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=small)

    # Plain string system (byte-identical to slice 1 / pre-slice-2).
    assert kwargs["system"] == _SYSTEM
    # Tools sent unmarked (stable prefix, but nothing cacheable this dispatch).
    assert kwargs["tools"] == list(small)
    assert all("cache_control" not in t for t in kwargs["tools"])


# --------------------------------------------------------------------------
# Extended-thinking — no marker; plain string system
# --------------------------------------------------------------------------
def test_extended_thinking_skips_system_marker_plain_string() -> None:
    superset = _big_superset()
    payload = _payload(
        params={"max_tokens": 16, "thinking": {"type": "enabled", "budget_tokens": 1024}}
    )
    kwargs = _payload_to_anthropic_kwargs(payload, system=_SYSTEM, frozen_tool_superset=superset)

    assert kwargs["system"] == _SYSTEM
    assert kwargs["tools"] == list(superset)
    assert all("cache_control" not in t for t in kwargs["tools"])


# --------------------------------------------------------------------------
# Byte-stability — two dispatches, same system + superset → byte-identical
# --------------------------------------------------------------------------
def test_two_dispatches_same_system_and_superset_are_byte_identical() -> None:
    superset = _big_superset()
    a = _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=superset)
    b = _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=superset)

    def _canon(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    assert _canon(a["system"]) == _canon(b["system"])
    assert _canon(a["tools"]) == _canon(b["tools"])


# --------------------------------------------------------------------------
# No-regression — None system + None superset is byte-identical to legacy
# --------------------------------------------------------------------------
def test_none_system_and_none_superset_is_byte_identical_legacy_path() -> None:
    payload_tools = ({"name": "legacy", "description": "d", "input_schema": {"type": "object"}},)
    payload = _payload(tools=payload_tools)

    kwargs = _payload_to_anthropic_kwargs(payload, system=None, frozen_tool_superset=None)
    assert "system" not in kwargs
    assert kwargs["tools"] == list(payload_tools)
    assert all("cache_control" not in t for t in kwargs["tools"])


def test_bound_superset_not_mutated_by_system_marker_path() -> None:
    superset = _big_superset()
    _payload_to_anthropic_kwargs(_payload(), system=_SYSTEM, frozen_tool_superset=superset)
    # The frozen superset's dicts must NOT gain cache_control in place.
    assert all("cache_control" not in tool for tool in superset)


# --------------------------------------------------------------------------
# Provider isolation — OpenAI/Ollama keep the `role:"system"` message form
# (ADR-F1: no Anthropic-specific system-array structure leaks to them)
# --------------------------------------------------------------------------
def test_openai_translate_keeps_role_system_message_not_array() -> None:
    kwargs = _payload_to_openai_kwargs(_payload(), system=_SYSTEM)
    assert kwargs["messages"][0] == {"role": "system", "content": _SYSTEM}
    # `system` is NOT a top-level Anthropic-style block array on the openai path.
    assert "system" not in kwargs


def test_ollama_translate_keeps_role_system_message_not_array() -> None:
    kwargs = _payload_to_ollama_kwargs(_payload(), system=_SYSTEM)
    assert kwargs["messages"][0] == {"role": "system", "content": _SYSTEM}
    assert "system" not in kwargs


# ==========================================================================
# CREDENTIAL-GATED LIVE e2e — PAID Anthropic call. DO NOT RUN in CI / offline
# lanes. Marked `@pytest.mark.e2e` so it is deselected from the `-m "not e2e"`
# provider-free lanes. Left here as the load-bearing live combined
# `[tools + system]` cache-hit proof (build, don't fire).
#
# Double-gated (Codex out-of-family review): the `e2e` marker alone does NOT
# stop a bare targeted `pytest <file>` (only the curated `just`/CI lanes pass
# `-m "not e2e"`), so a mere `ANTHROPIC_API_KEY` presence would auto-fire two
# PAID calls on an ordinary local run. Gate on an ADDITIONAL explicit opt-in env
# var `HARNESS_LIVE_ANTHROPIC_CACHE_E2E=1` (mirrors the workspace live-e2e
# convention, e.g. `MANAGED_AGENTS_E2E_*`) so the paid call is NEVER fired
# without deliberate operator opt-in — the `[[feedback-background-agent-no-
# unilateral-paid-calls-or-secret-relocation]]` boundary.
# ==========================================================================
@pytest.mark.e2e
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY")
    or not os.environ.get("HARNESS_LIVE_ANTHROPIC_CACHE_E2E"),
    reason=(
        "live Anthropic [tools+system] cache-hit proof — requires ANTHROPIC_API_KEY "
        "AND explicit HARNESS_LIVE_ANTHROPIC_CACHE_E2E=1 opt-in (PAID call; never auto-fired)"
    ),
)
async def test_live_system_block_combined_cache_hit() -> None:  # pragma: no cover
    """Two identical-prefix real Anthropic dispatches with a system-block
    breakpoint: call 1 creates the `[tools + system]` cache, call 2 reads it.
    Asserts `usage.cache_creation_input_tokens > 0` then
    `usage.cache_read_input_tokens > 0`.

    PAID call — surfaced at the operator's paid-call boundary, NOT auto-fired.
    """
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    superset = _big_superset()
    kwargs = _payload_to_anthropic_kwargs(
        _payload(params={"max_tokens": 16}),
        system=_SYSTEM,
        frozen_tool_superset=superset,
    )
    # Sanity: the breakpoint is on the system block (the slice-2 position).
    assert isinstance(kwargs["system"], list)
    assert kwargs["system"][-1]["cache_control"] == _CACHE_CONTROL
    model = "claude-3-5-haiku-latest"

    first = await client.messages.create(model=model, **kwargs)
    assert (first.usage.cache_creation_input_tokens or 0) > 0

    second = await client.messages.create(model=model, **kwargs)
    assert (second.usage.cache_read_input_tokens or 0) > 0

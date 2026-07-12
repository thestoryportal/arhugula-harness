"""B-TOOL-SEARCH-RUNTIME — offline tests for the `search_tools` capability-
discovery mechanism (AS spec v1.13 §13.7; ADR-D3 v1.2 §1.1 primitive #2
`tool_search` facet; §1.5 cache-prefix integrity discipline).

Provider-free lane: exercises `compute_frozen_tool_superset`'s new
`defer_names` parameter + `harness_runtime.lifecycle.tool_search` directly.
NO paid provider calls.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_runtime.lifecycle.frozen_tool_superset import compute_frozen_tool_superset
from harness_runtime.lifecycle.tool_registry import ToolRegistry
from harness_runtime.lifecycle.tool_search import (
    SEARCH_TOOLS_CONTRACT,
    SEARCH_TOOLS_TOOL_NAME,
    compute_deferred_tool_index,
    dispatch_search_tools,
)
from harness_runtime.types import ToolName


class _FakeHost:
    """Minimal stand-in for an MCPClientHost — exposes `.tool_registry` only."""

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


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _three_tool_hosts() -> dict[str, Any]:
    return {
        "srv": _FakeHost(
            _registry(
                [
                    _contract("alpha_reader", description="reads alpha files"),
                    _contract("beta_writer", description="writes beta records"),
                    _contract("gamma_search", description="searches the gamma index"),
                ]
            )
        )
    }


# --------------------------------------------------------------------------
# Additive/non-breaking — default `defer_names` is byte-identical
# --------------------------------------------------------------------------
def test_default_defer_names_is_byte_identical_to_pre_v1_13() -> None:
    hosts = _three_tool_hosts()
    with_default_arg = compute_frozen_tool_superset(
        hosts, include_memory_tool=False, defer_names=frozenset()
    )
    without_arg = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    assert with_default_arg is not None
    assert _canon(with_default_arg) == _canon(without_arg)
    assert all(t["name"] != SEARCH_TOOLS_TOOL_NAME for t in with_default_arg)


def test_defer_names_naming_nothing_present_is_a_no_op() -> None:
    hosts = _three_tool_hosts()
    superset = compute_frozen_tool_superset(
        hosts,
        include_memory_tool=False,
        defer_names=frozenset({ToolName("does_not_exist")}),
    )
    baseline = compute_frozen_tool_superset(hosts, include_memory_tool=False)
    assert _canon(superset) == _canon(baseline)


# --------------------------------------------------------------------------
# Deferred tool omission + search_tools stub presence
# --------------------------------------------------------------------------
def test_deferred_tool_omitted_and_search_stub_appended() -> None:
    hosts = _three_tool_hosts()
    superset = compute_frozen_tool_superset(
        hosts,
        include_memory_tool=False,
        defer_names=frozenset({ToolName("beta_writer")}),
    )
    assert superset is not None
    names = [t["name"] for t in superset]
    assert "beta_writer" not in names
    assert names == ["alpha_reader", "gamma_search", SEARCH_TOOLS_TOOL_NAME]
    assert superset[-1] == dict(SEARCH_TOOLS_CONTRACT)


def test_deferring_all_tools_leaves_only_the_search_stub() -> None:
    hosts = _three_tool_hosts()
    all_names = frozenset(
        {ToolName("alpha_reader"), ToolName("beta_writer"), ToolName("gamma_search")}
    )
    superset = compute_frozen_tool_superset(hosts, include_memory_tool=False, defer_names=all_names)
    assert superset == (dict(SEARCH_TOOLS_CONTRACT),)


# --------------------------------------------------------------------------
# Search round-trip
# --------------------------------------------------------------------------
def test_search_matches_by_name_substring() -> None:
    hosts = _three_tool_hosts()
    deferred = compute_deferred_tool_index(
        hosts, frozenset({ToolName("alpha_reader"), ToolName("beta_writer")})
    )
    results = dispatch_search_tools("alpha", deferred)
    assert [r["name"] for r in results] == ["alpha_reader"]
    assert results[0]["input_schema"] == {"type": "object"}


def test_search_matches_by_description_substring_case_insensitive() -> None:
    hosts = _three_tool_hosts()
    deferred = compute_deferred_tool_index(
        hosts, frozenset({ToolName("alpha_reader"), ToolName("beta_writer")})
    )
    results = dispatch_search_tools("RECORDS", deferred)
    assert [r["name"] for r in results] == ["beta_writer"]


def test_search_no_match_returns_empty_tuple() -> None:
    hosts = _three_tool_hosts()
    deferred = compute_deferred_tool_index(hosts, frozenset({ToolName("alpha_reader")}))
    assert dispatch_search_tools("no-such-thing", deferred) == ()


def test_search_empty_query_returns_every_deferred_tool_sorted() -> None:
    hosts = _three_tool_hosts()
    deferred = compute_deferred_tool_index(
        hosts, frozenset({ToolName("gamma_search"), ToolName("alpha_reader")})
    )
    results = dispatch_search_tools("", deferred)
    assert [r["name"] for r in results] == ["alpha_reader", "gamma_search"]


def test_search_never_returns_a_non_deferred_tool() -> None:
    hosts = _three_tool_hosts()
    deferred = compute_deferred_tool_index(hosts, frozenset({ToolName("alpha_reader")}))
    # "gamma_search" is not in the deferred set even though the query text
    # would otherwise substring-match its own name.
    results = dispatch_search_tools("gamma_search", deferred)
    assert results == ()


# --------------------------------------------------------------------------
# Cache-prefix invariance — the §13.7 point 4 acceptance witness
# --------------------------------------------------------------------------
def test_tools_bytes_unchanged_across_any_number_of_searches() -> None:
    """Load-bearing witness: `compute_frozen_tool_superset` output is
    byte-identical before and after dispatching any number of `search_tools`
    calls within the same epoch — searches are ordinary tool result content,
    never a `tools[]` mutation (ADR-D3 §1.5)."""
    hosts = _three_tool_hosts()
    defer_names = frozenset({ToolName("beta_writer"), ToolName("gamma_search")})

    before = compute_frozen_tool_superset(hosts, include_memory_tool=False, defer_names=defer_names)
    assert before is not None

    deferred = compute_deferred_tool_index(hosts, defer_names)
    for query in ("beta", "gamma", "", "no-match-at-all", "beta"):
        dispatch_search_tools(query, deferred)

    after = compute_frozen_tool_superset(hosts, include_memory_tool=False, defer_names=defer_names)
    assert _canon(before) == _canon(after)

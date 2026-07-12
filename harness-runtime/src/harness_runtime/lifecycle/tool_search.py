"""B-TOOL-SEARCH-RUNTIME — `tool_search` capability-discovery mechanism.

Per `Spec_Action_Surface_v1.md` v1.13 §13.7 (ADR-D3 v1.2 §1.1 primitive #2
"MCP-as-code" `tool_search` facet; §1.5 cache-prefix integrity discipline —
"per-MCP capability discovery via `tool_search` rather than `tools[]`
mutation"). Composes with, and does not replace,
``harness_runtime.lifecycle.frozen_tool_superset``: a caller opts a subset of
registered MCP tools into ``defer_names`` at
``compute_frozen_tool_superset(...)``; those tools are omitted from the eager
``tools[]`` union, and this module provides the on-demand discovery path for
them via the static ``search_tools`` tool.

Deterministic, minimal, hand-rolled (no search-library framework pull per the
§3.2 framework-pull discipline): case-insensitive substring match against
each deferred tool's ``name`` + ``description``, sorted by name. Match
sophistication beyond this is §13.7 implementation discretion.

Distinct from ``harness_runtime.lifecycle.skill_activation.SkillActivationMode.
TOOL_SEARCH`` — that enum value records the activation mode of a *Skill*
selected at the per-LLM-dispatch hook; this module is MCP tool discovery.
Unrelated mechanisms that may co-occur in the same dispatch.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from harness_runtime.types import ToolName

__all__ = [
    "SEARCH_TOOLS_CONTRACT",
    "SEARCH_TOOLS_TOOL_NAME",
    "compute_deferred_tool_index",
    "dispatch_search_tools",
]

#: The tool name the model invokes to discover a deferred tool's full schema.
SEARCH_TOOLS_TOOL_NAME = "search_tools"

#: Static, fixed-shape contract for the search tool itself. Present in the
#: frozen superset (`frozen_tool_superset.compute_frozen_tool_superset`)
#: whenever the caller defers ≥1 tool; never mutated per-search — this fixed
#: shape is what keeps the superset byte-invariant across search activity
#: (§13.7 point 3/4).
SEARCH_TOOLS_CONTRACT: Mapping[str, Any] = {
    "name": SEARCH_TOOLS_TOOL_NAME,
    "description": (
        "Search for full tool schemas among MCP tools not eagerly listed above. "
        "Returns matching tools' {name, description, input_schema}; does not "
        "register or make the tool directly callable — invoke the returned "
        "name once known."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}


def compute_deferred_tool_index(
    mcp_client_hosts: Mapping[Any, Any] | None,
    defer_names: frozenset[ToolName],
) -> Mapping[str, Mapping[str, Any]]:
    """Project the deferred subset of registered MCP tools to their full schemas.

    Mirrors the projection in ``compute_frozen_tool_superset`` (same
    ``{name, description, input_schema}`` shape) but keeps ONLY tools whose
    name is in ``defer_names`` — the complement of the eager union. Walks the
    same ``ctx.mcp_client_hosts`` dispatch-scoped registry (C10 condition 2).

    Empty ``defer_names`` (or no host holds a matching name) → empty mapping.
    """
    if not defer_names or mcp_client_hosts is None:
        return {}
    deferred: dict[str, Mapping[str, Any]] = {}
    for host in mcp_client_hosts.values():
        registry = host.tool_registry
        for name in registry.names():
            if name not in defer_names:
                continue
            contract = registry.get(name)
            deferred[str(contract.name)] = {
                "name": contract.name,
                "description": contract.description,
                "input_schema": contract.input_schema,
            }
    return deferred


def dispatch_search_tools(
    query: str,
    deferred_index: Mapping[str, Mapping[str, Any]],
) -> tuple[Mapping[str, Any], ...]:
    """Return the deferred tools matching ``query`` — the ``search_tools`` result.

    Ordinary tool-result content (a normal dispatch return value); this
    NEVER touches ``tools[]``. Case-insensitive substring match against each
    deferred tool's ``name`` + ``description``; sorted by name for
    determinism. An empty ``query`` matches every deferred tool (a listing
    query); no match → empty tuple.
    """
    needle = query.casefold()
    matches = [
        schema
        for name, schema in deferred_index.items()
        if needle in name.casefold() or needle in str(schema["description"]).casefold()
    ]
    matches.sort(key=lambda schema: str(schema["name"]))
    return tuple(matches)

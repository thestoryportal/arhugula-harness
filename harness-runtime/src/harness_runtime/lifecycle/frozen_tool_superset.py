"""U-1 (B-18) — deterministic frozen tool superset for the Anthropic
prompt-cache ``cache_control`` breakpoint (ADR-D3 §1.5 slice 1).

The frozen tool superset is the deterministically-ordered union of every
registered MCP tool contract (projected to the Anthropic
``{name, description, input_schema}`` dict), plus the Anthropic Memory tool
definition when the run may use memory. It is computed ONCE at bootstrap
stage 5 (top-level, single-privilege-tier dispatch per the C10 blast-radius
verdict at ``.harness/u1-slice1-c10-blast-radius-verdict.md``) and bound on
the ``RuntimeLLMDispatcher`` as ``frozen_tool_superset``. The Anthropic
translate seam places a ``cache_control`` breakpoint on its last block so the
stable tools prefix caches across dispatches.

**Deterministic order is load-bearing.** A nondeterministic wire order is a
SILENT cache miss (cost regression), forbidden by the no-silent-failure
discipline. The union is sorted by tool ``name`` and each ``input_schema`` is
canonicalized with the committed hand-rolled JCS-style scheme (recursive
sorted keys) — the same scheme used at ``harness_is.entry_hash.canonicalize``
and ``harness_as.secret_outputs_hash`` (no JCS framework pulled per the §3.2
framework-pull discipline).

Empty union (no MCP tools + no memory) → ``None`` → the dispatcher's
byte-identical legacy path (``payload.tools``).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from harness_runtime.lifecycle.memory_tool_dispatch import MEMORY_TOOL_TYPE

#: The Anthropic Memory tool definition (``ADR-D3 v1.2 §1.1 #11``; the
#: step-declared server-tool shape mirrored at the integration fixtures). A
#: typed server tool — carries ``type`` + ``name`` only (no ``input_schema``).
_MEMORY_TOOL_DEFINITION: dict[str, Any] = {"type": MEMORY_TOOL_TYPE, "name": "memory"}


def _canonicalize_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Return ``schema`` with object keys deterministically sorted (recursive).

    Round-trips through the committed hand-rolled JCS-style serialization
    (``json.dumps(..., sort_keys=True, separators=(",", ":"),
    ensure_ascii=False)``) so the resulting dict has a stable, byte-reproducible
    key order at every nesting depth. Reuses the exact scheme at
    ``harness_is.entry_hash.canonicalize`` / ``harness_as.secret_outputs_hash``
    rather than hand-rolling a new canonicalizer.
    """
    return json.loads(json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def compute_frozen_tool_superset(
    mcp_client_hosts: Mapping[Any, Any] | None,
    *,
    include_memory_tool: bool,
) -> tuple[Mapping[str, Any], ...] | None:
    """Compute the deterministic frozen tool superset from the MCP registries.

    ``mcp_client_hosts`` is ``ctx.mcp_client_hosts`` (``dict[ServerName,
    MCPClientHost]``) — the DISPATCH-scoped resolved registry (C10 condition 2:
    derive from THIS dispatch's own registry, never a captured parent set, so
    per-privilege-tier partitioning is correct-by-construction once slice 3
    lands). Each host's ``tool_registry`` (immutable post-``start()`` per
    §14.9.1) is walked; each ``ToolContract`` is projected to the Anthropic
    ``{name, description, input_schema}`` dict.

    ``include_memory_tool`` — when True (the run is memory-capable at stage 5:
    ``memory_tool_registry`` + ``deployment_surface`` bound), the Memory tool
    definition is appended so a memory step's step-declared memory tool is NOT
    dropped from the wire when the superset REPLACES ``payload.tools``.

    Cross-host name collisions already fail loud at ``build_tool_routing_index``
    (``runtime_tool_dispatcher_factory.py``), so a same-name dedup here is safe
    (a collision would have aborted bootstrap). Sort by tool ``name`` for a
    deterministic, cache-stable wire order.

    Returns ``None`` for an empty union (no MCP tools + no memory) → the
    dispatcher's byte-identical legacy path.
    """
    projected: dict[str, Mapping[str, Any]] = {}
    if mcp_client_hosts is not None:
        for host in mcp_client_hosts.values():
            registry = host.tool_registry
            for name in registry.names():
                contract = registry.get(name)
                # DEDUP by name (collision is impossible post-bootstrap; last
                # write is identical to first). Deterministic projection.
                projected[str(contract.name)] = {
                    "name": contract.name,
                    "description": contract.description,
                    "input_schema": _canonicalize_schema(contract.input_schema),
                }

    ordered: list[Mapping[str, Any]] = [projected[name] for name in sorted(projected)]

    if include_memory_tool:
        ordered.append(dict(_MEMORY_TOOL_DEFINITION))

    if not ordered:
        return None
    return tuple(ordered)

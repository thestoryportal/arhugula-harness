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

from harness_as.sandbox_tier import BlastRadiusTier

from harness_runtime.lifecycle.memory_tool_dispatch import MEMORY_TOOL_TYPE
from harness_runtime.lifecycle.tool_search import SEARCH_TOOLS_CONTRACT
from harness_runtime.types import ToolName

#: The Anthropic Memory tool definition (``ADR-D3 v1.2 §1.1 #11``; the
#: step-declared server-tool shape mirrored at the integration fixtures). A
#: typed server tool — carries ``type`` + ``name`` only (no ``input_schema``).
_MEMORY_TOOL_DEFINITION: dict[str, Any] = {"type": MEMORY_TOOL_TYPE, "name": "memory"}

#: U-1 slice 3a (B-18) — the blast-radius tiers a DESCENDED sub-agent (child)
#: registry REMOVEs from its visibility superset, per the ADR-D4 §1.5
#: default-downgrade rule: only ``external-irreversible`` is dropped (the
#: ``REMOVE`` disposition). ``local-mutation``/``external-reversible`` stay
#: VISIBLE (``external-reversible``'s ``DOWNGRADE_TO_ASK`` is a gate-level
#: concern, enforced at the HITL gate, not a visibility one). The child ceiling
#: is uniform (`compute_child_blast_radius_ceiling` → READ_ONLY), so the REMOVE
#: is tier-uniform and idempotent — a grandchild re-filtering an already-filtered
#: parent union drops nothing more (monotonic-sticky descent is correct).
CHILD_DOWNGRADE_REMOVE_TIERS: frozenset[BlastRadiusTier] = frozenset(
    {BlastRadiusTier.EXTERNAL_IRREVERSIBLE}
)


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
    remove_tiers: frozenset[BlastRadiusTier] = frozenset(),
    defer_names: frozenset[ToolName] = frozenset(),
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

    ``remove_tiers`` — U-1 slice 3a (B-18): the ADR-D4 §1.5 sub-agent
    default-downgrade **REMOVE** half. When a descended sub-agent (child)
    dispatch computes its own visibility superset, tools whose
    ``ToolContract.blast_radius_tier`` is in ``remove_tiers`` are OMITTED from
    the union (the child registry does not surface them; the parent must invoke
    them directly post-synthesis). The stage-5 caller passes
    ``frozenset({BlastRadiusTier.EXTERNAL_IRREVERSIBLE})`` for the child
    superset and ``frozenset()`` for the full top-level superset. Filtered at
    COMPUTE time (where ``blast_radius_tier`` is in hand — the projected tuple
    drops it). The Memory tool is NOT blast-radius-classified and is retained.
    Default ``frozenset()`` → byte-identical to the pre-slice-3a full union.
    ``local-mutation`` and ``external-reversible`` tools stay VISIBLE (the
    latter's ``DOWNGRADE_TO_ASK`` is a gate-level concern, not a visibility one,
    enforced separately at the HITL gate — not here).

    ``defer_names`` — B-TOOL-SEARCH-RUNTIME (AS spec v1.13 §13.7): tools whose
    name is in ``defer_names`` are OMITTED from the eager union entirely (their
    full schema is not sent up front — discover them via the ``search_tools``
    tool instead, see ``harness_runtime.lifecycle.tool_search``). When
    ``defer_names`` causes ≥1 tool to actually be omitted, exactly one static
    ``search_tools`` stub entry (``SEARCH_TOOLS_CONTRACT`` — fixed shape,
    never derived from the deferred set) is appended to the ordered union so
    the model can discover the deferred schemas on demand. Default
    ``frozenset()`` → byte-identical to the pre-v1.13 union (no search stub,
    no tools omitted).

    Cross-host name collisions already fail loud at ``build_tool_routing_index``
    (``runtime_tool_dispatcher_factory.py``), so a same-name dedup here is safe
    (a collision would have aborted bootstrap). Sort by tool ``name`` for a
    deterministic, cache-stable wire order.

    Returns ``None`` for an empty union (no MCP tools + no memory) → the
    dispatcher's byte-identical legacy path.
    """
    projected: dict[str, Mapping[str, Any]] = {}
    deferred_count = 0
    if mcp_client_hosts is not None:
        for host in mcp_client_hosts.values():
            registry = host.tool_registry
            for name in registry.names():
                contract = registry.get(name)
                # ADR-D4 §1.5 REMOVE: a descended child registry OMITS tools at a
                # removed blast-radius tier (external-irreversible). `remove_tiers`
                # is empty for the top-level superset → no filtering.
                if contract.blast_radius_tier in remove_tiers:
                    continue
                # B-TOOL-SEARCH-RUNTIME (AS spec v1.13 §13.7): a deferred tool is
                # OMITTED from the eager union — discoverable via `search_tools`
                # instead. `defer_names` is empty by default → no filtering.
                if name in defer_names:
                    deferred_count += 1
                    continue
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

    if deferred_count:
        ordered.append(dict(SEARCH_TOOLS_CONTRACT))

    if not ordered:
        return None
    return tuple(ordered)

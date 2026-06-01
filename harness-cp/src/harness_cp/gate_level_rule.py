"""4-axis multiplicative gate-level rule + monotonicity + `_hitl_required` — U-CP-43.

Implements C-CP-19 §19.1 (the multiplicative gate-level `max()` rule), §19.2
(cross-persona-tier monotonicity), and §19.4 (the `_hitl_required` predicate).

**Partial land — halt-route-split-AC.** CP plan v2.20 §0.8 row 2 PARTIAL-ADVANCE
preserves one spec-silence finding:

  - `MCP_TRUST_GATE_LEVEL_FLOOR` — AS spec C-AS-10 §10.3 4-level enumeration is
    canonical at AS-side (per CP spec v1.14 narrative reconciliation), but the
    per-tier → gate-level mapping (`MCPTrustTier` → `GateLevel`) remains
    spec-silent at both CP §19.1 and AS §10.3. Mapping owed at separate
    follow-on spec-extension arc.

Per the v2.20 (B2) plan-follows-spec disposition (operator AskUserQuestion
2026-05-24 + CP spec v1.15 §19.1.1 publication), the v2.4-era `deployment_surface`
axis is DROPPED — it belongs at §19.3 D2-layer sandbox composition only, NOT
§19.1 D5-layer HITL composition. The `per_tool_gate_level` axis is ADDED — it
IS the gate-level value declared per-tool at C-AS-03 SKILL.md frontmatter /
MCP server manifest (degenerate axis: no per-tier mapping; consumed directly).

The materializable surface AS LANDED: the §19.1/§16.2-conformed `GateLevel`
3-value enum, the `BLAST_RADIUS` + `PERSONA_TIER` §19.1-verbatim floors, the
`per_tool_gate_level` direct-input axis (v2.20), the `gate_level` multiplicative
`max()` rule over those three axes, cross-persona-tier monotonicity (§19.2),
and the `_hitl_required` predicate (§19.4). MCP_TRUST 4th axis remains
unmaterialized per §0.8 row 2 PARTIAL-ADVANCE.

Authority: Implementation_Plan_Control_Plane_v2_20.md §1 U-CP-43 canonical-reading
amendment (v2.20 — `GateLevelInput` field-set conformed to spec-canonical
4-axis per CP spec v1.15 §19.1.1.1: add `per_tool_gate_level`, drop
`deployment_surface`); Spec_Control_Plane_v1_15.md §19.1.1 NEW canonical 4-axis
statement + Spec_Control_Plane_v1_2.md §19.1 (preserved-by-reference)
composition formula + §19.4 `_hitl_required` predicate.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum

from harness_as import BlastRadiusTier
from harness_core import PersonaTier
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import Axis, MCPTrustTier


class GateLevel(StrEnum):
    """The 3-value gate-level domain (C-CP-19 §19.1 + §16.2, verbatim).

    The v2.4 amendment conformed this enum to the CP spec §19.1 `gate_level`
    value domain (`{auto, ask, deny}`) — the v2.1/v2.3 enum carried the
    divergent 4-value ladder. Escalation-monotonic per §19.1/§19.4:
    `AUTO < ASK < DENY` (`auto` → no HITL; `ask` → HITL rewrite; `deny` →
    structural rejection + HITL). Closed at cardinality 3 (acceptance #1).
    """

    AUTO = "auto"
    ASK = "ask"
    DENY = "deny"


class _GateRank(IntEnum):
    """Monotonic escalation rank for `GateLevel` `max()` composition (§19.1)."""

    AUTO = 0
    ASK = 1
    DENY = 2


_RANK: dict[GateLevel, _GateRank] = {
    GateLevel.AUTO: _GateRank.AUTO,
    GateLevel.ASK: _GateRank.ASK,
    GateLevel.DENY: _GateRank.DENY,
}
_BY_RANK: dict[_GateRank, GateLevel] = {v: k for k, v in _RANK.items()}


class GateLevelInput(BaseModel):
    """The 4-axis input set for the gate-level rule (U-CP-43, v2.20 conformed).

    Conformed to spec-canonical 4-axis per CP spec v1.15 §19.1.1.1: `{
    per_tool_gate_level, blast_radius_tier, persona_tier, mcp_trust_tier }`.
    The `deployment_surface` axis was DROPPED at v2.20 — `deployment_surface`
    belongs at §19.3 D2-layer sandbox composition only, NOT §19.1 D5-layer
    HITL composition (CP spec v1.15 §19.1.1 (v) non-axis statement). The
    `per_tool_gate_level` axis was ADDED at v2.20 — it IS the gate-level value
    declared per-tool at C-AS-03 SKILL.md frontmatter / MCP server manifest
    (degenerate per CP spec v1.15 §19.1.1 (i): no per-tier mapping; consumed
    directly at `max()`).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    per_tool_gate_level: GateLevel
    """Spec-canonical axis (v2.20 ADDED per CP spec v1.15 §19.1.1 (i)). The
    per-tool gate-level value declared per-tool at C-AS-03 SKILL.md frontmatter
    / MCP server manifest `tier` field (`{auto, ask, deny}`). Degenerate axis:
    no per-tier mapping table; consumed directly at `gate_level()` `max()`."""

    persona_tier: PersonaTier
    blast_radius_tier: BlastRadiusTier

    mcp_trust_tier: MCPTrustTier
    """Spec-canonical axis. [§0.8 row 2 PARTIAL-ADVANCE] AS spec C-AS-10 §10.3
    4-level enumeration is canonical at AS-side (cardinality narrative
    reconciled at CP spec v1.14); per-tier → gate-level mapping
    (`MCP_TRUST_GATE_LEVEL_FLOOR`) is spec-silent at both CP §19.1 and AS §10.3
    so this field is unconsumed by `gate_level()` until the mapping lands at
    follow-on spec-extension arc. The field type is the landed U-CP-00c
    `MCPTrustTier` enum."""


class GateLevelComputation(BaseModel):
    """The result of a gate-level computation (C-CP-19 §19.1).

    `per_axis_floors` carries the three materialized axes (`PER_TOOL_GATE_LEVEL`,
    `BLAST_RADIUS`, `PERSONA_TIER`) at v2.20; the `MCP_TRUST` 4th axis remains
    §0.8 row 2 PARTIAL-ADVANCE (per-tier mapping spec-silent at both CP §19.1
    and AS §10.3 — owed at follow-on spec-extension arc). `composition_winner`
    identifies which axis set the winning floor — retained as an internal field
    with no downstream audit sink at v2.4 (the `audit.gate.*` namespace was
    dissolved at v2.4 U-CP-46).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    inputs: GateLevelInput
    per_axis_floors: dict[Axis, GateLevel]
    composition_winner: Axis
    computed_gate_level: GateLevel


# --- §19.1 conformed floors (the two materialized axes) ---------------------

BLAST_RADIUS_GATE_LEVEL_FLOOR: dict[BlastRadiusTier, GateLevel] = {
    BlastRadiusTier.READ_ONLY: GateLevel.AUTO,
    BlastRadiusTier.LOCAL_MUTATION: GateLevel.ASK,
    BlastRadiusTier.EXTERNAL_REVERSIBLE: GateLevel.ASK,
    BlastRadiusTier.EXTERNAL_IRREVERSIBLE: GateLevel.ASK,
}
"""C-CP-19 §19.1 `blast_radius_floor` block, verbatim (acceptance #3).

`read-only` → `AUTO`; `local-mutation` → `ASK` (configurable to `AUTO` at
solo-developer per §19.1); `external-reversible` → `ASK`;
`external-irreversible` → `ASK` (with dual-control at multi-tenant-compliance
per §19.1).
"""

PERSONA_TIER_GATE_LEVEL_FLOOR: dict[PersonaTier, GateLevel] = {
    PersonaTier.SOLO_DEVELOPER: GateLevel.ASK,
    PersonaTier.TEAM_BINDING: GateLevel.ASK,
    PersonaTier.MULTI_TENANT_COMPLIANCE: GateLevel.ASK,
}
"""C-CP-19 §19.1 `persona_tier_floor` block, verbatim (acceptance #4).

All three persona tiers map to `ASK` per §19.1: `solo-developer` (operator may
override to `AUTO` for non-irreversible), `team-binding` (audit ledger
required), `multi-tenant-compliance` (audit ledger + cryptographic signature;
dual-control on external-irreversible). The v2.1/v2.3 acc #3 divergent ladder
(`GATE_NONE` / `GATE_NOTIFY` / `GATE_APPROVE`) was conformed away at v2.4.
"""


def gate_level(input: GateLevelInput) -> GateLevelComputation:
    """Compute the gate level — `max()` over the materialized per-axis floors.

    C-CP-19 §19.1 composition rule: `max()` over the per-axis floors.
    Deterministic given inputs. **v2.20 — 3-axis materialized:** the
    `max()` ranges over the three materialized §19.1-conformed inputs
    (`PER_TOOL_GATE_LEVEL` direct, `BLAST_RADIUS` floor, `PERSONA_TIER` floor)
    per CP spec v1.15 §19.1.1.1. The `MCP_TRUST` 4th axis remains
    §0.8 row 2 PARTIAL-ADVANCE — per-tier → gate-level mapping spec-silent
    until follow-on spec-extension arc.
    """
    per_tool_floor = input.per_tool_gate_level  # degenerate — IS the value
    blast_floor = BLAST_RADIUS_GATE_LEVEL_FLOOR[input.blast_radius_tier]
    persona_floor = PERSONA_TIER_GATE_LEVEL_FLOOR[input.persona_tier]
    per_axis_floors: dict[Axis, GateLevel] = {
        Axis.PER_TOOL_GATE_LEVEL: per_tool_floor,
        Axis.BLAST_RADIUS: blast_floor,
        Axis.PERSONA_TIER: persona_floor,
    }
    # max() over the materialized floors by escalation rank.
    winner_axis = max(per_axis_floors.items(), key=lambda kv: _RANK[kv[1]])[0]
    computed = _BY_RANK[max(_RANK[lv] for lv in per_axis_floors.values())]
    return GateLevelComputation(
        inputs=input,
        per_axis_floors=per_axis_floors,
        composition_winner=winner_axis,
        computed_gate_level=computed,
    )


def hitl_required(input: GateLevelInput) -> bool:
    """Return `true` iff `computed_gate_level ∈ {ASK, DENY}` (C-CP-19 §19.4).

    The CP plan signature names this predicate `_hitl_required`; `_hitl_required`
    is exported below as a module-level alias for spec-name fidelity. Consumed
    at the U-CP-39 rewriting algorithm.
    """
    return gate_level(input).computed_gate_level in (GateLevel.ASK, GateLevel.DENY)


_hitl_required = hitl_required
"""Spec-name alias — CP plan U-CP-43 signature names the predicate
`_hitl_required` (C-CP-19 §19.4). Public callers use `hitl_required`."""


def assert_cross_persona_monotonicity(from_tier: PersonaTier, to_tier: PersonaTier) -> None:
    """Enforce §19.2 cross-persona-tier monotonicity.

    Under bridging-arc traversal across persona tiers, `persona_tier_floor`
    ascends monotonically (never descends). A tier downgrade is structurally
    prohibited — it raises `ValueError` (the manifest-validation error per
    §19.2). The persona-tier order is `solo-developer < team-binding <
    multi-tenant-compliance`.
    """
    order: dict[PersonaTier, int] = {
        PersonaTier.SOLO_DEVELOPER: 0,
        PersonaTier.TEAM_BINDING: 1,
        PersonaTier.MULTI_TENANT_COMPLIANCE: 2,
    }
    if order[to_tier] < order[from_tier]:
        raise ValueError(
            f"cross-persona-tier monotonicity violated (§19.2): "
            f"{from_tier.value} -> {to_tier.value} descends the persona-tier axis"
        )

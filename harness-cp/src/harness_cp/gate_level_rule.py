"""4-axis multiplicative gate-level rule + monotonicity + `_hitl_required` — U-CP-43.

Implements C-CP-19 §19.1 (the multiplicative gate-level `max()` rule), §19.2
(cross-persona-tier monotonicity), and §19.4 (the `_hitl_required` predicate).

**Partial land — halt-route-split-AC.** CP plan v2.4 §0.8 carries two
spec-silence findings the plan body itself leaves flagged (acc #5/#6):

  - `MCP_TRUST_GATE_LEVEL_FLOOR` — CP spec §19.1 names a "C10 five-tier
    framework" for `per_mcp_server_trust_floor` but does NOT enumerate the
    per-tier → gate-level mapping; the spec is genuinely silent.
  - `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` — CP spec §19.1's 4-axis `max()`
    does not carry `deployment_surface` as an axis (deployment-surface gating
    appears only inside `sandbox_tier_floor` at §19.3); the spec carries no
    per-deployment-surface → gate-level mapping.

Per the plan's own acc #5/#6 ("authoring them now would bake an unverified
mapping") these two floor tables are NOT materialized. Acc #5 / #6 are struck;
acc #2 is degraded to a `max()` over the two materialized §19.1-conformed
floors (`BLAST_RADIUS` + `PERSONA_TIER`); acc #9 is informational. See
`.harness/class_1_tension_u_cp_43_spec_silent_floors.md`.

The materializable surface IS landed: the §19.1/§16.2-conformed `GateLevel`
3-value enum, the `BLAST_RADIUS` + `PERSONA_TIER` §19.1-verbatim floors, the
`gate_level` multiplicative `max()` rule over those two axes, cross-persona-
tier monotonicity (§19.2), and the `_hitl_required` predicate (§19.4).

Authority: Implementation_Plan_Control_Plane_v2_4.md §2 U-CP-43 (v2.4
amendment — `GateLevel` + `BLAST_RADIUS` + `PERSONA_TIER` floors conformed to
CP spec §19.1/§16.2 verbatim; `MCP_TRUST` + `DEPLOYMENT_SURFACE` floors
carried per §0.8); Spec_Control_Plane_v1_3.md §19 C-CP-19 §19.1 + §19.2 + §19.4
+ §16.2.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum

from harness_as import BlastRadiusTier
from harness_core import DeploymentSurface, PersonaTier
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
    """The 4-axis input set for the gate-level rule (U-CP-43 plan signature).

    NOTE — the plan's 4-axis input set is `{persona_tier, blast_radius_tier,
    deployment_surface, mcp_trust_tier}`; CP spec §19.1's 4-axis `max()` is
    over `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor,
    persona_tier_floor}`. The input-set divergence is the §0.8 carry (acc #9 —
    informational). The record is authored at the plan's declared shape; only
    the `persona_tier` + `blast_radius_tier` axes have materialized floors.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    persona_tier: PersonaTier
    blast_radius_tier: BlastRadiusTier
    deployment_surface: DeploymentSurface
    """Plan-signature axis. [carried per §0.8] No
    `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` is materialized — §19.1 does not
    carry deployment-surface as a `max()` axis — so this field is unconsumed
    by `gate_level()`. The field type is the landed `DeploymentSurface` enum."""

    mcp_trust_tier: MCPTrustTier
    """Plan-signature axis. [carried per §0.8] No `MCP_TRUST_GATE_LEVEL_FLOOR`
    is materialized — §19.1 is silent on the per-trust-tier → gate-level
    mapping — so this field is unconsumed by `gate_level()`. The field type is
    the landed U-CP-00c `MCPTrustTier` enum (no re-declaration, per v2.9 §0)."""


class GateLevelComputation(BaseModel):
    """The result of a gate-level computation (C-CP-19 §19.1).

    `per_axis_floors` carries only the two materialized axes (`BLAST_RADIUS`,
    `PERSONA_TIER`); the `MCP_TRUST` / `PER_TOOL_GATE_LEVEL` / sandbox axes are
    §0.8-carried and absent. `composition_winner` identifies which axis set the
    winning floor — retained as an internal field with no downstream audit sink
    at v2.4 (the `audit.gate.*` namespace was dissolved at v2.4 U-CP-46).
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
    Deterministic given inputs. **Degraded per §0.8 (acc #2 carry):** the
    `max()` ranges over the two materialized §19.1-conformed floors
    (`BLAST_RADIUS`, `PERSONA_TIER`) only; the `MCP_TRUST` and (plan-invented)
    `DEPLOYMENT_SURFACE` axes are spec-silent and not materialized.
    """
    blast_floor = BLAST_RADIUS_GATE_LEVEL_FLOOR[input.blast_radius_tier]
    persona_floor = PERSONA_TIER_GATE_LEVEL_FLOOR[input.persona_tier]
    per_axis_floors: dict[Axis, GateLevel] = {
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


def assert_cross_persona_monotonicity(
    from_tier: PersonaTier, to_tier: PersonaTier
) -> None:
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

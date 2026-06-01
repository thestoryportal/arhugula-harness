"""Tests for U-CP-43 — 4-axis multiplicative gate-level rule (C-CP-19 §19.1/§19.2/§19.4).

Acceptance-criterion coverage (v2.20 amendment per CP spec v1.15 §19.1.1):
  #1 GateLevel cardinality 3              -> test_gate_level_cardinality_three,
                                             test_gate_level_values_match_spec_19_1_16_2
  #2 max() over materialized floors       -> test_gate_level_max_composition_over_materialized_floors
  #3 BLAST_RADIUS floor §19.1 verbatim    -> test_blast_radius_floor_match_spec_19_1
  #4 PERSONA_TIER floor all three ASK     -> test_persona_tier_floor_all_three_ask
  #6 (v2.20 NEW) per_tool_gate_level axis -> test_per_tool_gate_level_axis_in_max_composition,
                                             test_per_tool_gate_level_degenerate_no_floor_table
  #7 cross-persona monotonicity §19.2     -> test_cross_persona_monotonicity
  #8 _hitl_required ask-or-deny §19.4     -> test_hitl_required_predicate_ask_or_deny
  #9 (v2.20 NEW) GateLevelInput field-set -> test_gate_level_input_no_deployment_surface_field
  #10 composition_winner attribution      -> test_composition_winner_attribution

Acc #5 (MCP_TRUST floor) preserved §0.8 row 2 PARTIAL-ADVANCE — per-tier mapping
spec-silent at both CP §19.1 + AS §10.3; owed at follow-on spec-extension arc.
Acc #6 (DEPLOYMENT_SURFACE floor) RETIRED at v2.20 per CP spec v1.15 §19.1.1 (v)
non-axis statement. New per_tool_gate_level tests authored at v2.20 (NEW acc #6).
"""

from __future__ import annotations

import pytest
from harness_as import BlastRadiusTier
from harness_core import PersonaTier
from harness_cp.cp_shared_types import Axis, MCPTrustTier
from harness_cp.gate_level_rule import (
    BLAST_RADIUS_GATE_LEVEL_FLOOR,
    PERSONA_TIER_GATE_LEVEL_FLOOR,
    GateLevel,
    GateLevelInput,
    assert_cross_persona_monotonicity,
    gate_level,
    hitl_required,
)


def _input(
    persona: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    blast: BlastRadiusTier = BlastRadiusTier.READ_ONLY,
    per_tool: GateLevel = GateLevel.AUTO,
) -> GateLevelInput:
    return GateLevelInput(
        per_tool_gate_level=per_tool,
        persona_tier=persona,
        blast_radius_tier=blast,
        mcp_trust_tier=MCPTrustTier.LEVEL_1_SIGNED_PINNED,
    )


def test_gate_level_cardinality_three() -> None:
    """#1 — GateLevel declares exactly three values."""
    assert len(GateLevel) == 3


def test_gate_level_values_match_spec_19_1_16_2() -> None:
    """#1 — GateLevel values are {auto, ask, deny} per §19.1/§16.2 verbatim."""
    assert {m.value for m in GateLevel} == {"auto", "ask", "deny"}


def test_gate_level_max_composition_over_materialized_floors() -> None:
    """#2 (v2.20) — max() over the three materialized floors.

    PER_TOOL_GATE_LEVEL + BLAST_RADIUS + PERSONA_TIER floors compose by
    escalation rank. `external-irreversible` (ASK) + solo-developer (ASK) +
    per_tool AUTO -> ASK.
    """
    comp = gate_level(_input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.EXTERNAL_IRREVERSIBLE))
    assert comp.computed_gate_level is GateLevel.ASK
    # read-only + solo + per_tool AUTO -> max(AUTO, AUTO, ASK) = ASK (persona wins).
    comp2 = gate_level(_input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.READ_ONLY))
    assert comp2.computed_gate_level is GateLevel.ASK
    assert set(comp.per_axis_floors) == {
        Axis.PER_TOOL_GATE_LEVEL,
        Axis.BLAST_RADIUS,
        Axis.PERSONA_TIER,
    }


def test_per_tool_gate_level_axis_in_max_composition() -> None:
    """#6 (v2.20 NEW) — per_tool_gate_level participates in max() composition.

    Per CP spec v1.15 §19.1.1 (i): per_tool_gate_level IS the gate-level value
    declared per-tool at C-AS-03 SKILL.md frontmatter; degenerate axis with no
    per-tier mapping; consumed directly at max().
    """
    # per_tool DENY dominates persona ASK + blast AUTO.
    comp = gate_level(_input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.READ_ONLY, GateLevel.DENY))
    assert comp.computed_gate_level is GateLevel.DENY
    assert comp.composition_winner is Axis.PER_TOOL_GATE_LEVEL
    assert comp.per_axis_floors[Axis.PER_TOOL_GATE_LEVEL] is GateLevel.DENY


def test_per_tool_gate_level_degenerate_no_floor_table() -> None:
    """#6 (v2.20 NEW) — no PER_TOOL_GATE_LEVEL_FLOOR constant exists.

    per_tool_gate_level IS the GateLevel value (per CP spec v1.15 §19.1.1 (i)
    degenerate axis); no per-tier → gate-level mapping table needed.
    """
    import harness_cp.gate_level_rule as glr

    assert not hasattr(glr, "PER_TOOL_GATE_LEVEL_FLOOR")


def test_gate_level_input_no_deployment_surface_field() -> None:
    """#9 (v2.20 NEW) — GateLevelInput field-set conformed to spec-canonical 4-axis.

    Per CP spec v1.15 §19.1.1 (v) non-axis statement: deployment_surface is
    NOT a §19.1 D5-layer axis (belongs at §19.3 D2-layer sandbox composition
    only). v2.20 drops the field from GateLevelInput.
    """
    assert "deployment_surface" not in GateLevelInput.model_fields
    assert "per_tool_gate_level" in GateLevelInput.model_fields
    assert set(GateLevelInput.model_fields) == {
        "per_tool_gate_level",
        "persona_tier",
        "blast_radius_tier",
        "mcp_trust_tier",
    }


def test_blast_radius_floor_match_spec_19_1() -> None:
    """#3 — BLAST_RADIUS_GATE_LEVEL_FLOOR matches §19.1 blast_radius_floor verbatim."""
    assert BLAST_RADIUS_GATE_LEVEL_FLOOR == {
        BlastRadiusTier.READ_ONLY: GateLevel.AUTO,
        BlastRadiusTier.LOCAL_MUTATION: GateLevel.ASK,
        BlastRadiusTier.EXTERNAL_REVERSIBLE: GateLevel.ASK,
        BlastRadiusTier.EXTERNAL_IRREVERSIBLE: GateLevel.ASK,
    }


def test_persona_tier_floor_all_three_ask() -> None:
    """#4 — all three persona tiers map to ASK per §19.1 persona_tier_floor."""
    assert set(PERSONA_TIER_GATE_LEVEL_FLOOR.values()) == {GateLevel.ASK}
    assert set(PERSONA_TIER_GATE_LEVEL_FLOOR) == set(PersonaTier)


def test_cross_persona_monotonicity() -> None:
    """#7 — persona-tier ascends monotonically; descent is structurally prohibited."""
    # Ascending / equal transitions are admissible.
    assert_cross_persona_monotonicity(PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING)
    assert_cross_persona_monotonicity(PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert_cross_persona_monotonicity(PersonaTier.TEAM_BINDING, PersonaTier.TEAM_BINDING)
    # A descent raises (the §19.2 manifest-validation error).
    with pytest.raises(ValueError, match="monotonicity violated"):
        assert_cross_persona_monotonicity(
            PersonaTier.MULTI_TENANT_COMPLIANCE, PersonaTier.SOLO_DEVELOPER
        )


def test_hitl_required_predicate_ask_or_deny() -> None:
    """#8 — _hitl_required true iff computed_gate_level ∈ {ASK, DENY} per §19.4."""
    # Every materialized input produces ASK (both floors are AUTO/ASK) -> HITL.
    assert hitl_required(_input()) is True
    assert (
        hitl_required(
            _input(PersonaTier.MULTI_TENANT_COMPLIANCE, BlastRadiusTier.EXTERNAL_IRREVERSIBLE)
        )
        is True
    )


def test_composition_winner_attribution() -> None:
    """#10 — composition_winner identifies which axis set the winning floor."""
    comp = gate_level(_input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.READ_ONLY))
    # read-only blast floor is AUTO, persona floor is ASK -> persona wins.
    assert comp.composition_winner is Axis.PERSONA_TIER
    assert comp.computed_gate_level is GateLevel.ASK


def test_gate_level_monotonic_ordering() -> None:
    """#1 — escalation ordering AUTO < ASK < DENY is preserved by the rule."""
    # AUTO < ASK < DENY escalation: read-only+solo -> ASK (persona ASK wins);
    # the rule never emits a level below the highest materialized floor.
    comp = gate_level(_input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.READ_ONLY))
    assert comp.computed_gate_level is GateLevel.ASK
    assert comp.per_axis_floors[Axis.BLAST_RADIUS] is GateLevel.AUTO

"""Tests for U-CP-43 — 4-axis multiplicative gate-level rule (C-CP-19 §19.1/§19.2/§19.4).

Acceptance-criterion coverage (v2.4 amendment):
  #1 GateLevel cardinality 3              -> test_gate_level_cardinality_three,
                                             test_gate_level_values_match_spec_19_1_16_2
  #2 max() over materialized floors       -> test_gate_level_max_composition_over_materialized_floors
  #3 BLAST_RADIUS floor §19.1 verbatim    -> test_blast_radius_floor_match_spec_19_1
  #4 PERSONA_TIER floor all three ASK     -> test_persona_tier_floor_all_three_ask
  #7 cross-persona monotonicity §19.2     -> test_cross_persona_monotonicity
  #8 _hitl_required ask-or-deny §19.4     -> test_hitl_required_predicate_ask_or_deny
  #10 composition_winner attribution      -> test_composition_winner_attribution

Acc #5 (MCP_TRUST floor) + #6 (DEPLOYMENT_SURFACE floor) STRUCK — §0.8 spec-
silence carry; see .harness/class_1_tension_u_cp_43_spec_silent_floors.md.
Carried-item tests deliberately NOT authored (would bake an unverified mapping).
"""

from __future__ import annotations

import pytest

from harness_as import BlastRadiusTier
from harness_core import PersonaTier

from harness_cp.cp_shared_types import Axis
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
) -> GateLevelInput:
    return GateLevelInput(
        persona_tier=persona,
        blast_radius_tier=blast,
        deployment_surface="self-hosted-server",
        mcp_trust_tier="level-1-signed-pinned",
    )


def test_gate_level_cardinality_three() -> None:
    """#1 — GateLevel declares exactly three values."""
    assert len(GateLevel) == 3


def test_gate_level_values_match_spec_19_1_16_2() -> None:
    """#1 — GateLevel values are {auto, ask, deny} per §19.1/§16.2 verbatim."""
    assert {m.value for m in GateLevel} == {"auto", "ask", "deny"}


def test_gate_level_max_composition_over_materialized_floors() -> None:
    """#2 (degraded per §0.8) — max() over the two materialized floors.

    Both BLAST_RADIUS and PERSONA_TIER floors compose by escalation rank;
    `external-irreversible` (ASK) + solo-developer (ASK) -> ASK.
    """
    comp = gate_level(
        _input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.EXTERNAL_IRREVERSIBLE)
    )
    assert comp.computed_gate_level is GateLevel.ASK
    # read-only + solo -> max(AUTO, ASK) = ASK (persona floor wins).
    comp2 = gate_level(_input(PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.READ_ONLY))
    assert comp2.computed_gate_level is GateLevel.ASK
    assert set(comp.per_axis_floors) == {Axis.BLAST_RADIUS, Axis.PERSONA_TIER}


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
    assert_cross_persona_monotonicity(
        PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING
    )
    assert_cross_persona_monotonicity(
        PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE
    )
    assert_cross_persona_monotonicity(
        PersonaTier.TEAM_BINDING, PersonaTier.TEAM_BINDING
    )
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
            _input(PersonaTier.MULTI_TENANT_COMPLIANCE,
                   BlastRadiusTier.EXTERNAL_IRREVERSIBLE)
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

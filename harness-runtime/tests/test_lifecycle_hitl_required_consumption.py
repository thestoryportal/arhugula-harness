"""U-RT-90 unit tests — `_hitl_required` 4-axis consumption per Reading B.

Covers runtime spec v1.22 §14.8.2 step 4c — thin wrapper around CP-axis
`harness_cp.gate_level_rule.hitl_required` (CP-as-landed degraded 2-axis
composition per CP plan v2.4 §0.8 carry).
"""

from __future__ import annotations

from harness_as import BlastRadiusTier
from harness_core import DeploymentSurface, PersonaTier
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.gate_level_rule import GateLevelInput

from harness_runtime.lifecycle.hitl_required_consumption import (
    evaluate_hitl_required,
)


def _input(
    persona: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    blast_radius: BlastRadiusTier = BlastRadiusTier.READ_ONLY,
) -> GateLevelInput:
    """Construct a GateLevelInput with sentinel defaults for unconsumed axes.

    CP-as-landed `deployment_surface` and `mcp_trust_tier` are field-required
    but `gate_level()` does not consume them per CP plan v2.4 §0.8 carry —
    any value works; using LOCAL_DEVELOPMENT + LEVEL_0_REFUSE_REMOTE as sentinels.
    """
    return GateLevelInput(
        persona_tier=persona,
        blast_radius_tier=blast_radius,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
    )


class TestEvaluateHitlRequired:
    """4-axis composition coverage per C-CP-19 §19.1 + §19.4 (AC #2)."""

    def test_read_only_blast_radius_alone_does_not_force_hitl_unless_persona_floor_applies(self) -> None:
        """READ_ONLY blast → AUTO; but persona floor for all 3 tiers = ASK → True."""
        # All 3 persona tiers map to ASK per PERSONA_TIER_GATE_LEVEL_FLOOR.
        # So max(blast=AUTO, persona=ASK) = ASK → True.
        result = evaluate_hitl_required(_input(blast_radius=BlastRadiusTier.READ_ONLY))
        assert result is True

    def test_external_irreversible_blast_radius_forces_hitl(self) -> None:
        """EXTERNAL_IRREVERSIBLE → ASK; combined with persona ASK → True."""
        result = evaluate_hitl_required(
            _input(blast_radius=BlastRadiusTier.EXTERNAL_IRREVERSIBLE)
        )
        assert result is True

    def test_all_persona_tiers_yield_hitl_required(self) -> None:
        """Per PERSONA_TIER_GATE_LEVEL_FLOOR all 3 tiers map to ASK → True."""
        for persona in (
            PersonaTier.SOLO_DEVELOPER,
            PersonaTier.TEAM_BINDING,
            PersonaTier.MULTI_TENANT_COMPLIANCE,
        ):
            result = evaluate_hitl_required(_input(persona=persona))
            assert result is True, f"persona={persona!r} did not yield True"

    def test_local_mutation_blast_radius_with_solo_developer(self) -> None:
        """LOCAL_MUTATION → ASK; max(ASK, ASK) = ASK → True."""
        result = evaluate_hitl_required(
            _input(
                persona=PersonaTier.SOLO_DEVELOPER,
                blast_radius=BlastRadiusTier.LOCAL_MUTATION,
            )
        )
        assert result is True


class TestPureFunctionGuarantee:
    """AC #3 — idempotent + no module state."""

    def test_same_input_same_output(self) -> None:
        """Calling twice yields identical results."""
        input_a = _input()
        result1 = evaluate_hitl_required(input_a)
        result2 = evaluate_hitl_required(input_a)
        assert result1 == result2

    def test_no_input_mutation(self) -> None:
        """Input GateLevelInput is frozen (Pydantic v2 frozen=True); cannot be mutated."""
        input_a = _input()
        # Per CP-axis gate_level_rule GateLevelInput.model_config: frozen=True.
        # Calling evaluate_hitl_required must not raise (the function reads only).
        result = evaluate_hitl_required(input_a)
        assert isinstance(result, bool)

"""Tests for U-CP-66 — C-CP-27 PerServerTrust enum carriers.

U-CP-66 ACs (CP plan v2.15 §1, preserved at v2.17):
  AC #1 MCPPrimitive 4-class enum matches §27.2 verbatim
  AC #2 TrustDecisionReason 6-class enum includes UNKNOWN_SERVER_TIER_FLOOR_PASS
        + UNKNOWN_SERVER_TIER_FLOOR_VIOLATION per Decision 3.D1 RATIFIED
  AC #3 TierDerivationRule 3-class enum (CONSERVATIVE / PROTOCOL_VERSION_TABLE /
        OPERATOR_HOOK)
  AC #4 All enums frozen + hashable
  AC #5 pyright strict mode passes (project-level type-check; not unit-tested
        here — verified via uv-workspace lint task)
"""

from __future__ import annotations

import pytest

from harness_cp.per_server_trust_types import (
    MCPPrimitive,
    TierDerivationRule,
    TrustDecisionReason,
)


# ---------------------------------------------------------------------------
# AC #1 — MCPPrimitive 4-class verbatim
# ---------------------------------------------------------------------------


def test_mcp_primitive_has_exactly_four_members() -> None:
    """AC #1 — MCPPrimitive declares exactly four members."""
    assert len(MCPPrimitive) == 4


def test_mcp_primitive_member_values_verbatim() -> None:
    """AC #1 — values match C-AS-14 §14.3 + CP §27.2 verbatim."""
    assert {p.value for p in MCPPrimitive} == {
        "tool",
        "resource",
        "prompt",
        "sampling",
    }


def test_mcp_primitive_is_str_subclass() -> None:
    """StrEnum members are str subclasses (consumable as attribute values)."""
    assert isinstance(MCPPrimitive.TOOL, str)
    assert MCPPrimitive.TOOL == "tool"


# ---------------------------------------------------------------------------
# AC #2 — TrustDecisionReason 6-class with both UNKNOWN_SERVER_*
# ---------------------------------------------------------------------------


def test_trust_decision_reason_has_exactly_six_members() -> None:
    """AC #2 — TrustDecisionReason declares exactly six members."""
    assert len(TrustDecisionReason) == 6


def test_trust_decision_reason_includes_unknown_server_pass() -> None:
    """AC #2 — UNKNOWN_SERVER_TIER_FLOOR_PASS present (Decision 3.D1)."""
    assert TrustDecisionReason.UNKNOWN_SERVER_TIER_FLOOR_PASS.value == (
        "unknown_server_tier_floor_pass"
    )


def test_trust_decision_reason_includes_unknown_server_violation() -> None:
    """AC #2 — UNKNOWN_SERVER_TIER_FLOOR_VIOLATION present (Decision 3.D1)."""
    assert TrustDecisionReason.UNKNOWN_SERVER_TIER_FLOOR_VIOLATION.value == (
        "unknown_server_tier_floor_violation"
    )


def test_trust_decision_reason_member_values_verbatim() -> None:
    """AC #2 — all 6 values match CP spec v1.10 §27.2 verbatim."""
    assert {r.value for r in TrustDecisionReason} == {
        "explicit_allow",
        "explicit_deny",
        "tier_floor_pass",
        "tier_floor_violation",
        "unknown_server_tier_floor_pass",
        "unknown_server_tier_floor_violation",
    }


# ---------------------------------------------------------------------------
# AC #3 — TierDerivationRule 3-class
# ---------------------------------------------------------------------------


def test_tier_derivation_rule_has_exactly_three_members() -> None:
    """AC #3 — TierDerivationRule declares exactly three members."""
    assert len(TierDerivationRule) == 3


def test_tier_derivation_rule_member_values_verbatim() -> None:
    """AC #3 — values match CP spec v1.10 §27.2 verbatim."""
    assert {r.value for r in TierDerivationRule} == {
        "conservative",
        "protocol_version_table",
        "operator_hook",
    }


# ---------------------------------------------------------------------------
# AC #4 — all enums frozen + hashable
# ---------------------------------------------------------------------------


def test_enums_members_are_hashable() -> None:
    """AC #4 — enum members usable as dict keys / set members."""
    bag = {
        MCPPrimitive.TOOL,
        TrustDecisionReason.EXPLICIT_ALLOW,
        TierDerivationRule.CONSERVATIVE,
    }
    assert len(bag) == 3


def test_enums_members_are_immutable() -> None:
    """AC #4 — StrEnum members reject attribute reassignment."""
    with pytest.raises((AttributeError, TypeError)):
        MCPPrimitive.TOOL.value = "mutated"  # type: ignore[misc]

"""Tests for U-CP-58 — C-CP-25 ValidatorFramework type carriers.

ACs from CP plan v2.16 §1 (= v2.15 §1 U-CP-58 preserved):
  AC #1 ValidatorOutcome has exactly 5 members matching spec §25.2 verbatim values
  AC #2 ValidatorFailClass has exactly 5 members matching spec §25.2
  AC #3 ValidatorNextAction has exactly 4 members (PROCEED / RETRY / ESCALATE_HITL / ABORT)
  AC #4 All enums frozen + hashable
  AC #5 pyright strict mode passes (verified at workspace `uv run pyright` invocation)
"""

from __future__ import annotations

from harness_cp.validator_framework_types import (
    ValidatorFailClass,
    ValidatorNextAction,
    ValidatorOutcome,
)


# --- AC #1 ----------------------------------------------------------------


def test_validator_outcome_has_exactly_five_members() -> None:
    """AC #1 — ValidatorOutcome 5 members."""
    assert len(ValidatorOutcome) == 5


def test_validator_outcome_member_values_verbatim() -> None:
    """AC #1 — member string values match spec §25.2 verbatim."""
    assert {c.value for c in ValidatorOutcome} == {
        "pass",
        "revalidate",
        "escalate",
        "permanent_fail",
        "operator_burden_exceeded",
    }


def test_validator_outcome_member_names() -> None:
    """AC #1 — member names PASS / REVALIDATE / ESCALATE / PERMANENT_FAIL / OPERATOR_BURDEN_EXCEEDED."""
    assert {c.name for c in ValidatorOutcome} == {
        "PASS",
        "REVALIDATE",
        "ESCALATE",
        "PERMANENT_FAIL",
        "OPERATOR_BURDEN_EXCEEDED",
    }


# --- AC #2 ----------------------------------------------------------------


def test_validator_fail_class_has_exactly_five_members() -> None:
    """AC #2 — ValidatorFailClass 5 members."""
    assert len(ValidatorFailClass) == 5


def test_validator_fail_class_member_values_verbatim() -> None:
    """AC #2 — member string values match spec §25.2 verbatim."""
    assert {c.value for c in ValidatorFailClass} == {
        "schema_violation",
        "semantic_inconsistency",
        "safety_policy",
        "resource_constraint",
        "external_rejection",
    }


def test_validator_fail_class_distinct_from_retry_exit_class() -> None:
    """Path β disambiguation: the NEW C-CP-25 ValidatorFailClass is distinct
    from the OLD C-CP-21 ValidatorRetryExitClass at harness_cp.validator_fail_taxonomy.
    """
    from harness_cp.validator_fail_taxonomy import ValidatorRetryExitClass

    assert ValidatorFailClass is not ValidatorRetryExitClass
    new_values = {c.value for c in ValidatorFailClass}
    old_values = {c.value for c in ValidatorRetryExitClass}
    assert new_values.isdisjoint(old_values)


# --- AC #3 ----------------------------------------------------------------


def test_validator_next_action_has_exactly_four_members() -> None:
    """AC #3 — ValidatorNextAction 4 members."""
    assert len(ValidatorNextAction) == 4


def test_validator_next_action_member_names() -> None:
    """AC #3 — member names PROCEED / RETRY / ESCALATE_HITL / ABORT."""
    assert {c.name for c in ValidatorNextAction} == {
        "PROCEED",
        "RETRY",
        "ESCALATE_HITL",
        "ABORT",
    }


# --- AC #4 ----------------------------------------------------------------


def test_validator_outcome_hashable() -> None:
    """AC #4 — Enum members are hashable; can populate a set."""
    members = {c for c in ValidatorOutcome}
    assert len(members) == 5


def test_validator_fail_class_hashable() -> None:
    """AC #4 — Enum members are hashable."""
    members = {c for c in ValidatorFailClass}
    assert len(members) == 5


def test_validator_next_action_hashable() -> None:
    """AC #4 — Enum members are hashable."""
    members = {c for c in ValidatorNextAction}
    assert len(members) == 4


def test_enums_frozen_at_attribute_level() -> None:
    """AC #4 — Enum members reject mutation (StrEnum is immutable-by-design)."""
    import pytest

    with pytest.raises(AttributeError):
        ValidatorOutcome.PASS.value = "mutated"  # type: ignore[misc]

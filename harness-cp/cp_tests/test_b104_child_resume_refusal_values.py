"""B-104 S1: the closed set of `ChildResumeRefusal` values (six filed at CP v1.123, nine with S1).

The value is written into a terminal fail class, so adding or renaming a member is a contract
change; this test makes that a deliberate act. The three claim/start members are exercised by the
Runtime admission tests; here only the set, spelling and fail-class rendering are pinned.
"""

from __future__ import annotations

from harness_cp.workflow_driver import _refused_fail_class  # pyright: ignore[reportPrivateUsage]
from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError

_SIX_FILED_AT_V1_123 = {
    "missing-ref",
    "unreadable-record",
    "snapshot-mismatch",
    "depth-mismatch",
    "gateway-not-installed",
    "workflow-mismatch",
}
_THREE_ADDED_BY_S1 = {"claim-refused", "claim-busy", "start-refused"}


def test_the_refusal_set_is_exactly_the_six_filed_values_plus_the_three_s1_values() -> None:
    values = {member.value for member in ChildResumeRefusal}

    assert values == _SIX_FILED_AT_V1_123 | _THREE_ADDED_BY_S1
    assert len(ChildResumeRefusal) == 9
    assert _SIX_FILED_AT_V1_123.isdisjoint(_THREE_ADDED_BY_S1)


def test_the_new_members_have_the_exact_wire_spelling() -> None:
    assert ChildResumeRefusal("claim-refused").name == "CLAIM_REFUSED"
    assert ChildResumeRefusal("claim-busy").name == "CLAIM_BUSY"
    assert ChildResumeRefusal("start-refused").name == "START_REFUSED"


def test_the_fail_class_sorts_old_and_new_reasons_with_the_signing_suffix_last() -> None:
    refusals = {
        0: ChildResumeRefusedError(ChildResumeRefusal.START_REFUSED),
        1: ChildResumeRefusedError(ChildResumeRefusal.DEPTH_MISMATCH, audit_signing_failed=True),
        2: ChildResumeRefusedError(ChildResumeRefusal.CLAIM_BUSY),
        3: ChildResumeRefusedError(ChildResumeRefusal.CLAIM_BUSY),
    }

    assert _refused_fail_class("parallelization-child-resume-refused", refusals) == (
        "parallelization-child-resume-refused "
        "(claim-busy; depth-mismatch; start-refused; audit-signing-failed)"
    )

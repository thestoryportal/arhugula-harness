"""U-CORE-03 — shared sub-agent dispatch capacity-exhausted error tests.

Tests per Implementation_Plan_Harness_Core_v1_3.md §1 U-CORE-03 acceptance
criteria (PD-8 mutation-probed): the constructor round-trip witness (dropping
a field fails) and the cross-package leaf-safety witness (both `harness_cp`
and `harness_runtime` import the class without a cycle; relocating it into
`harness_runtime` makes the CP import fail).
"""

from __future__ import annotations

import pytest
from harness_core import SubAgentDispatchCapacityError


def test_capacity_error_carries_step_and_descent() -> None:
    """AC #1 — step id + descent chain + counts surface on the raised instance."""
    with pytest.raises(SubAgentDispatchCapacityError) as excinfo:
        raise SubAgentDispatchCapacityError(
            requested_frames=6,
            available_capacity=2,
            step_id="step-fanout-3",
            descent_chain=("wf-root", "step-parent-1", "step-fanout-3"),
        )
    err = excinfo.value
    assert err.requested_frames == 6
    assert err.available_capacity == 2
    assert err.step_id == "step-fanout-3"
    assert err.descent_chain == ("wf-root", "step-parent-1", "step-fanout-3")
    # C1 step-attributability: the message NAMES the overflowing step and the
    # descent chain — never a generic executor error.
    message = str(err)
    assert "step-fanout-3" in message
    assert "wf-root -> step-parent-1 -> step-fanout-3" in message
    assert "6 frame(s)" in message
    assert "2 available" in message


def test_capacity_error_root_descent_and_carrier_shape() -> None:
    """AC #1/#2 — empty descent chain renders <root>; slotted carrier, no dict."""
    err = SubAgentDispatchCapacityError(
        requested_frames=1,
        available_capacity=0,
        step_id="step-solo",
        descent_chain=(),
    )
    assert "<root>" in str(err)
    # Slotted per the harness-core carrier conventions (AC #2). BaseException
    # itself carries __dict__, so the check is the declared slot set.
    assert set(SubAgentDispatchCapacityError.__slots__) == {
        "requested_frames",
        "available_capacity",
        "step_id",
        "descent_chain",
    }


def test_capacity_error_importable_from_cp_and_runtime_without_cycle() -> None:
    """AC #2 — leaf-safe: the packages that raise/handle it import it cleanly.

    Mutation probe: relocating the class into `harness_runtime` makes the CP
    import fail (harness-cp has no harness-runtime dependency).
    """
    import harness_cp  # noqa: F401  (import proves no cycle through harness_core)
    import harness_runtime  # noqa: F401
    from harness_core.sub_agent_dispatch_capacity import (
        SubAgentDispatchCapacityError as DirectImport,
    )

    assert DirectImport is SubAgentDispatchCapacityError

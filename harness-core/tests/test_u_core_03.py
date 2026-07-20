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


def test_capacity_error_carries_canonical_rt_fail_class_marker() -> None:
    """B-48 (codex round-4 [P2] "surface the canonical capacity failure
    class"): `harness_cp.workflow_driver._step_fail_class` reads
    `getattr(exc, "rt_fail_class", None)` (it cannot import runtime/core
    exception TYPES across some boundaries, so it name/attribute-matches) —
    without this marker, a persisted/user-facing failure would surface the
    bare Python class name `SubAgentDispatchCapacityError` instead of the
    Runtime spec v1.102 §14.8.10.5 taxonomy code."""
    err = SubAgentDispatchCapacityError(
        requested_frames=1, available_capacity=0, step_id="s", descent_chain=()
    )
    assert err.rt_fail_class == "RT-FAIL-SUB-AGENT-DISPATCH-CAPACITY"
    assert type(err).rt_fail_class == "RT-FAIL-SUB-AGENT-DISPATCH-CAPACITY"


def test_capacity_error_direct_import_matches_package_export() -> None:
    """AC #2 — the package-level re-export is the same object as the direct
    carrier-module import (no shadowing/copy)."""
    from harness_core.sub_agent_dispatch_capacity import (
        SubAgentDispatchCapacityError as DirectImport,
    )

    assert DirectImport is SubAgentDispatchCapacityError


# NB: the cross-package "harness_cp AND harness_runtime both import this
# without a cycle" leaf-safety witness lives at
# `harness-runtime/tests/test_u_core_03_cross_package_import.py` — it needs
# BOTH sibling axis packages installed simultaneously, which the CI axis-
# isolation job for harness-core deliberately does NOT provide (harness-core
# must have zero import dependency on its consumers; a test requiring their
# presence cannot run inside harness-core's own isolated job).

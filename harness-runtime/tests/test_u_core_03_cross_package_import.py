"""U-CORE-03 — cross-package leaf-safety witness for the shared capacity error.

Homed here (not `harness-core/tests/`) because it requires BOTH `harness_cp`
and `harness_runtime` installed simultaneously — harness-runtime's own
dependency set (it consumes `harness-cp`) guarantees that, while the
harness-core axis-isolation CI job deliberately does NOT install sibling
axis packages (harness-core must have zero import dependency on its
consumers).

Authority: Implementation_Plan_Harness_Core_v1_3.md §1 U-CORE-03 AC #2.
"""

from __future__ import annotations


def test_capacity_error_importable_from_cp_and_runtime_without_cycle() -> None:
    """AC #2 — leaf-safe: the packages that raise/handle it import it cleanly.

    Mutation probe: relocating the class into `harness_runtime` makes the CP
    import fail (harness-cp has no harness-runtime dependency).
    """
    import harness_cp  # noqa: F401  (import proves no cycle through harness_core)
    import harness_runtime  # noqa: F401
    from harness_core import SubAgentDispatchCapacityError
    from harness_core.sub_agent_dispatch_capacity import (
        SubAgentDispatchCapacityError as DirectImport,
    )

    assert DirectImport is SubAgentDispatchCapacityError

"""Shared sub-agent dispatch capacity-exhausted error — U-CORE-03.

Implements the canonical typed raise of Runtime spec v1.102 §14.8.10.5 (the
fail-class row maps to this type) + the CP-declared capacity-authority
Protocol's raise contract (CP plan v2.39 §0; CP spec v1.102 §1). Authored at
the RATIFIED B-48 sync sub-agent dispatch offload arc
(`.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md`, option B,
2026-07-18; Core plan v1.3 §1).

Carrier-home discipline: both `harness_cp` (fan-out admission through the
capacity-authority Protocol, U-CP-101) and `harness_runtime` (the §14.8.10
executor's own fail-fast, U-RT-141) raise/handle the SAME type — a cross-axis
type in one axis package is the Class-1 cycle hazard, so it homes here.

The class is a CARRIER, not an authority: every field is constructor-supplied
by the raising site; no capacity logic lives here. It is raised at ADMISSION
time only — it never fires for an already-admitted job; lease lifecycle
(held to actual job termination or fence-drain acknowledgement, exactly-once
release) is executor-owned (Runtime plan v2.50 U-RT-141), not error-owned.
"""

from __future__ import annotations


class SubAgentDispatchCapacityError(Exception):
    """Typed fail-fast raised when dispatch admission against the shared frame budget fails.

    NEVER queued, no best-effort degradation (C9); names the overflowing
    dispatch step and carries the descent chain so the failure is
    step-attributable by the driver/topology machinery (C1), never a generic
    executor error.
    """

    __slots__ = ("available_capacity", "descent_chain", "requested_frames", "step_id")

    def __init__(
        self,
        *,
        requested_frames: int,
        available_capacity: int,
        step_id: str,
        descent_chain: tuple[str, ...],
    ) -> None:
        self.requested_frames = requested_frames
        self.available_capacity = available_capacity
        self.step_id = step_id
        self.descent_chain = descent_chain
        chain = " -> ".join(descent_chain) if descent_chain else "<root>"
        super().__init__(
            f"sub-agent dispatch capacity exhausted at step {step_id!r} "
            f"(descent chain: {chain}): requested {requested_frames} frame(s), "
            f"{available_capacity} available under the shared frame budget"
        )

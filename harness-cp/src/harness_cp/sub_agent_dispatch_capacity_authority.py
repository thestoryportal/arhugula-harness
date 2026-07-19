"""CP capacity-authority Protocol + default bounded authority — U-CP-101.

Implements the CP-declared capacity-authority carrier of CP plan v2.39 §0
(CP spec v1.102 §1 — C-CP-25 §25.11 fan-out capacity gating): a RAISE-CAPABLE
frame-unit admission surface the amended fan-out sites (U-CP-85/86/88) admit
through, plus the CP-OWNED DEFAULT bounded authority — the never-ungated
fallback (process-local frame budget, default 256, construction-overridable).

Cycle-safe seam: `harness-cp` has NO `harness-runtime` dependency — the
runtime executor (Runtime spec v1.102 §14.8.10.1, plan v2.50 U-RT-141)
supplies an adapter IMPLEMENTING this Protocol at the `harness-runtime`
composition root and injects it through the existing DriverContext/runtime-
services pattern; when nothing is injected, the default authority gates
identically (one authority per process — the default is a fallback instance,
never a second live authority).

Admission semantics (CP spec v1.102 §1 rows 1-6):

- `reserve` — single-dispatch admission: atomic all-frames-or-fail-fast; on
  exhaustion RAISES the shared `harness_core.SubAgentDispatchCapacityError`
  carrying the overflowing dispatch step + descent chain (C1 step-attributable,
  never a generic executor error). NEVER queues (C9).
- `reserve_fanout` — fan-out-level ATOMIC allocation: ONE call, under ONE
  lock hold, returning a per-branch result set — admitted branch leases plus
  deterministic (input-order fitting-prefix) per-branch rejections, each
  rejection carrying the shared error's data. Never partial-then-raise, never
  incremental hold-and-wait (per-branch-only atomicity lets two racing
  fan-outs mutually degrade when either could have run whole).
- Leases are released EXACTLY-ONCE across success / failure / pause /
  cancellation / timeout; the lease is held until ACTUAL job termination or
  fence-drain acknowledgement — lease lifecycle is executor-owned at the
  runtime adapter (U-RT-141), and the default authority applies the same
  exactly-once discipline.
"""

from __future__ import annotations

import threading
from contextvars import ContextVar
from typing import Protocol, final, runtime_checkable

from harness_core import SubAgentDispatchCapacityError

# The CP-owned default frame budget (CP plan v2.39 §0: "a CP module constant,
# construction-overridable"). Mirrors the Runtime C-RT-03
# `sub_agent_dispatch_max_workers` default; the RuntimeConfig value becomes
# authoritative only when the runtime adapter is composed (U-RT-141).
DEFAULT_SUB_AGENT_DISPATCH_FRAME_BUDGET = 256


@final
class CapacityLease:
    """A per-branch/per-dispatch frame lease over an admitting authority.

    Exactly-once release: the first `release()` returns the frames to the
    budget and returns True; every subsequent call is a no-op returning False.
    """

    __slots__ = ("_frames", "_release_fn", "_released", "step_id")

    def __init__(self, *, frames: int, step_id: str, release_fn: object) -> None:
        self._frames = frames
        self.step_id = step_id
        # Stored as object to keep the carrier dumb; invoked via a narrow cast.
        self._release_fn = release_fn
        self._released = False

    @property
    def frames(self) -> int:
        return self._frames

    @property
    def released(self) -> bool:
        return self._released

    def release(self) -> bool:
        """Return the leased frames to the budget; exactly-once."""
        if self._released:
            return False
        self._released = True
        fn = self._release_fn
        assert callable(fn)
        fn(self._frames)
        return True


# Per-branch admission outcome of a fan-out-level atomic allocation: an
# admitted lease OR the (unraised) rejection error carrying the U-CORE-03
# data for that branch. Discriminate with isinstance.
BranchAdmission = CapacityLease | SubAgentDispatchCapacityError

# Double-charge discriminator (occupied+N+S accounting, Runtime spec v1.102
# §14.8.10.1): a fan-out branch's inner-dispatch frame is charged AT THE
# FAN-OUT's atomic allocation (2 frames per sync SUB_AGENT_DISPATCH branch),
# so the runtime offload venue must NOT reserve again inside that branch.
# The gated fan-out sites bind the branch's lease here before dispatching the
# branch (`asyncio.to_thread` copies context into the branch worker); the
# runtime facade re-binds it across the loop bridge; the offload venue reads
# it — present → frames already leased (skip reservation), absent → the
# single-frame non-fan-out reservation applies.
BRANCH_CAPACITY_LEASE_VAR: ContextVar[CapacityLease | None] = ContextVar(
    "branch_capacity_lease", default=None
)


@runtime_checkable
class CapacityAuthority(Protocol):
    """The CP-declared admission surface fan-out/dispatch sites admit through.

    Structural: the runtime executor adapter (U-RT-141) satisfies it without
    importing this module's default implementation.
    """

    def reserve(
        self,
        frames: int,
        *,
        step_id: str,
        descent_chain: tuple[str, ...],
    ) -> CapacityLease:
        """Atomically reserve `frames` or raise `SubAgentDispatchCapacityError`.

        All-frames-or-fail-fast; never queues; never partially acquires.
        """
        ...

    def reserve_fanout(
        self,
        branch_requirements: tuple[int, ...],
        *,
        step_ids: tuple[str, ...],
        descent_chain: tuple[str, ...],
    ) -> tuple[BranchAdmission, ...]:
        """Atomically decide a WHOLE fan-out's admission in one call.

        Returns one result per branch, positionally aligned with the inputs:
        the fitting prefix (input order) is acquired as leases; deterministic
        excess branches get per-branch rejection errors (unraised). Never
        partial-then-raise; never retry-after-reject.
        """
        ...


@final
class DefaultCapacityAuthority:
    """The CP-owned default bounded authority (never-ungated fallback).

    Process-local frame budget; thread-safe (fan-out branch dispatching spans
    threads). Gates identically to the composed runtime authority; the budget
    ceiling is fixed at construction.
    """

    __slots__ = ("_available", "_budget", "_lock")

    def __init__(self, *, frame_budget: int = DEFAULT_SUB_AGENT_DISPATCH_FRAME_BUDGET) -> None:
        if frame_budget < 1:
            msg = f"frame_budget must be >= 1, got {frame_budget}"
            raise ValueError(msg)
        self._budget = frame_budget
        self._available = frame_budget
        self._lock = threading.Lock()

    @property
    def frame_budget(self) -> int:
        return self._budget

    @property
    def available(self) -> int:
        with self._lock:
            return self._available

    def _release(self, frames: int) -> None:
        with self._lock:
            self._available = min(self._budget, self._available + frames)

    def reserve(
        self,
        frames: int,
        *,
        step_id: str,
        descent_chain: tuple[str, ...],
    ) -> CapacityLease:
        with self._lock:
            if frames > self._available:
                raise SubAgentDispatchCapacityError(
                    requested_frames=frames,
                    available_capacity=self._available,
                    step_id=step_id,
                    descent_chain=descent_chain,
                )
            self._available -= frames
        return CapacityLease(frames=frames, step_id=step_id, release_fn=self._release)

    def reserve_fanout(
        self,
        branch_requirements: tuple[int, ...],
        *,
        step_ids: tuple[str, ...],
        descent_chain: tuple[str, ...],
    ) -> tuple[BranchAdmission, ...]:
        if len(branch_requirements) != len(step_ids):
            msg = (
                "branch_requirements and step_ids must align: "
                f"{len(branch_requirements)} != {len(step_ids)}"
            )
            raise ValueError(msg)
        results: list[BranchAdmission] = []
        with self._lock:
            remaining = self._available
            acquired = 0
            for frames, step_id in zip(branch_requirements, step_ids, strict=True):
                if frames <= remaining:
                    remaining -= frames
                    acquired += frames
                    results.append(
                        CapacityLease(frames=frames, step_id=step_id, release_fn=self._release)
                    )
                else:
                    # Deterministic excess: input-order fitting prefix only.
                    results.append(
                        SubAgentDispatchCapacityError(
                            requested_frames=frames,
                            available_capacity=remaining,
                            step_id=step_id,
                            descent_chain=descent_chain,
                        )
                    )
            self._available -= acquired
        return tuple(results)

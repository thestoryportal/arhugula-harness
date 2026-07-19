"""U-CP-101 — CP capacity-authority Protocol + default bounded authority tests.

Tests per Implementation_Plan_Control_Plane_v2_39.md NEW U-CP-101 (PD-8
mutation-probed): the default authority gates at 256 and raises the shared
`harness_core` error with step context (mutation probe: an ungated default
passes unbounded fan-out and fails); lease release is exactly-once across
outcome paths; the fan-out-level atomic allocation returns fitting-prefix
leases + deterministic per-branch rejections and never mutually degrades two
racing whole-fits fan-outs (U-CP-86 witness
`test_simultaneous_fanout_admission_no_mutual_degradation` — authority half).
"""

from __future__ import annotations

import threading

import pytest
from harness_core import SubAgentDispatchCapacityError
from harness_cp.sub_agent_dispatch_capacity_authority import (
    DEFAULT_SUB_AGENT_DISPATCH_FRAME_BUDGET,
    CapacityAuthority,
    CapacityLease,
    DefaultCapacityAuthority,
)


def test_default_authority_gates_at_256_and_raises_core_error_with_step_context() -> None:
    """The never-ungated fallback: default budget 256; typed step-attributable raise."""
    authority = DefaultCapacityAuthority()
    assert authority.frame_budget == DEFAULT_SUB_AGENT_DISPATCH_FRAME_BUDGET == 256
    lease = authority.reserve(256, step_id="step-a", descent_chain=("wf", "step-a"))
    # Mutation probe half: an ungated default would admit this next frame.
    with pytest.raises(SubAgentDispatchCapacityError) as excinfo:
        authority.reserve(1, step_id="step-b", descent_chain=("wf", "step-b"))
    err = excinfo.value
    assert err.requested_frames == 1
    assert err.available_capacity == 0
    assert err.step_id == "step-b"
    assert err.descent_chain == ("wf", "step-b")
    lease.release()
    assert authority.available == 256


def test_default_authority_satisfies_protocol_structurally() -> None:
    assert isinstance(DefaultCapacityAuthority(), CapacityAuthority)


def test_default_authority_rejects_budget_below_one() -> None:
    with pytest.raises(ValueError, match="frame_budget"):
        DefaultCapacityAuthority(frame_budget=0)


def test_protocol_lease_release_exactly_once_across_outcomes() -> None:
    """Exactly-once release: repeated release attempts (the five outcome paths
    each racing to release) return frames to the budget only once."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    lease = authority.reserve(3, step_id="s1", descent_chain=("s1",))
    assert authority.available == 1
    assert lease.release() is True
    # success / failure / pause / cancellation / timeout paths may all attempt
    # release; every attempt after the first is a no-op.
    for _ in range(4):
        assert lease.release() is False
    assert authority.available == 4  # not 4 + 3*n over-credit


def test_release_unless_job_bound_atomic_vs_bind() -> None:
    """CP branch teardown's atomic bound-check-and-release.

    Mutation probe: reverting the CP call sites to a bare
    `if not lease.job_bound: lease.release()` reintroduces a TOCTOU window
    between the read and the call — a `bind_release_to_job()` landing in
    that window lets teardown double-release alongside the job's own
    later release. `release_unless_job_bound` collapses the check and the
    released-flip into one critical section, so once bound, teardown's call
    is provably a no-op regardless of interleaving.
    """
    authority = DefaultCapacityAuthority(frame_budget=4)
    lease = authority.reserve(3, step_id="s1", descent_chain=("s1",))
    assert authority.available == 1
    lease.bind_release_to_job()
    # Teardown's guarded call must be a no-op once bound — frames stay held
    # for the job's own done-callback release, never double-credited here.
    assert lease.release_unless_job_bound() is False
    assert authority.available == 1
    assert lease.release() is True
    assert authority.available == 4


def test_release_unless_job_bound_releases_when_not_bound() -> None:
    authority = DefaultCapacityAuthority(frame_budget=4)
    lease = authority.reserve(3, step_id="s1", descent_chain=("s1",))
    assert lease.release_unless_job_bound() is True
    assert authority.available == 4
    assert lease.release_unless_job_bound() is False  # exactly-once


def test_bind_release_to_job_reports_false_when_already_released() -> None:
    """The reverse race: `release_unless_job_bound()` can win BEFORE
    `bind_release_to_job()` lands (a cooperatively-cancelled caller's
    `future.cancel()` only requests cancellation at the next await point, so
    synchronous offload-setup code can still run after the caller already
    released). Mutation probe: reverting `bind_release_to_job` to the bare
    `self._job_bound = True` write (no `_released` check, no return value)
    would report success here regardless — the caller could not distinguish
    a genuine bind from a lease that already returned its frames to the
    budget."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    lease = authority.reserve(3, step_id="s1", descent_chain=("s1",))
    assert lease.release_unless_job_bound() is True
    assert authority.available == 4
    assert lease.bind_release_to_job() is False
    assert lease.job_bound is False  # never flips once already released


def test_bind_release_to_job_reports_true_when_not_yet_released() -> None:
    authority = DefaultCapacityAuthority(frame_budget=4)
    lease = authority.reserve(3, step_id="s1", descent_chain=("s1",))
    assert lease.bind_release_to_job() is True
    assert lease.job_bound is True
    # Once bound, teardown's guarded release is a no-op — frames stay held.
    assert lease.release_unless_job_bound() is False
    assert authority.available == 1


def test_reserve_fanout_whole_fit_returns_all_leases() -> None:
    authority = DefaultCapacityAuthority(frame_budget=8)
    results = authority.reserve_fanout(
        (2, 2, 2),
        step_ids=("b0", "b1", "b2"),
        descent_chain=("wf", "fanout"),
    )
    assert all(isinstance(r, CapacityLease) for r in results)
    assert authority.available == 2


def test_reserve_fanout_fitting_prefix_deterministic_rejections() -> None:
    """Excess branches get per-branch rejections carrying the error data;
    only the input-order fitting prefix is acquired — never partial-then-raise."""
    authority = DefaultCapacityAuthority(frame_budget=5)
    results = authority.reserve_fanout(
        (2, 2, 2),
        step_ids=("b0", "b1", "b2"),
        descent_chain=("wf", "fanout"),
    )
    assert isinstance(results[0], CapacityLease)
    assert isinstance(results[1], CapacityLease)
    rejection = results[2]
    assert isinstance(rejection, SubAgentDispatchCapacityError)
    assert rejection.requested_frames == 2
    assert rejection.available_capacity == 1
    assert rejection.step_id == "b2"
    assert authority.available == 1


def test_reserve_fanout_prefix_break_rejects_all_after_first_miss() -> None:
    """A later SMALLER branch must not admit after an earlier branch missed.

    Mutation probe: dropping the `admitting` early-stop lets branch 1 (needs
    1, and 1 is still available since branch 0's failed 2-frame request never
    touched `remaining`) wrongly admit after branch 0 was rejected — breaking
    the documented "input-order fitting prefix" invariant.
    """
    authority = DefaultCapacityAuthority(frame_budget=1)
    results = authority.reserve_fanout(
        (2, 1),
        step_ids=("b0", "b1"),
        descent_chain=("wf", "fanout"),
    )
    assert isinstance(results[0], SubAgentDispatchCapacityError)
    assert isinstance(results[1], SubAgentDispatchCapacityError)
    assert results[1].requested_frames == 1
    assert results[1].available_capacity == 1
    # Nothing was acquired — the whole-fan-out budget is untouched.
    assert authority.available == 1


def test_reserve_fanout_misaligned_inputs_rejected() -> None:
    authority = DefaultCapacityAuthority(frame_budget=4)
    with pytest.raises(ValueError, match="align"):
        authority.reserve_fanout((1, 1), step_ids=("b0",), descent_chain=())


def test_simultaneous_fanout_admission_no_mutual_degradation() -> None:
    """Two 3-frame fan-outs vs 4 free — one runs WHOLE, the other degrades
    deterministically (mutation probe: per-branch incremental acquisition
    interleaves and degrades both)."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    barrier = threading.Barrier(2)
    outcomes: list[tuple[int, int]] = []  # (admitted, rejected) per fan-out
    lock = threading.Lock()

    def run_fanout(tag: str) -> None:
        barrier.wait()
        results = authority.reserve_fanout(
            (1, 1, 1),
            step_ids=(f"{tag}-0", f"{tag}-1", f"{tag}-2"),
            descent_chain=("wf", tag),
        )
        admitted = sum(1 for r in results if isinstance(r, CapacityLease))
        with lock:
            outcomes.append((admitted, 3 - admitted))

    threads = [threading.Thread(target=run_fanout, args=(t,)) for t in ("fa", "fb")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    admitted_counts = sorted(a for a, _ in outcomes)
    # One fan-out runs whole (3/3); the other gets exactly the remaining 1.
    assert admitted_counts == [1, 3]

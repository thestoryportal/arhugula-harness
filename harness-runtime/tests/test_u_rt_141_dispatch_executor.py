"""U-RT-141 — grow-on-demand dispatch executor + shared frame budget tests.

Tests per Implementation_Plan_Harness_Runtime_v2_50.md §1.2 (PD-8
mutation-probed): cap saturation fail-fast with provably zero queue growth,
grow-on-demand worker discipline (spawn when none free, idle reuse, named
daemon threads), drain-with-deadline that never joins a blocked worker,
whole-fan-out atomic admission under concurrent fan-outs, and the adapter
satisfying the CP-declared `CapacityAuthority` Protocol. The fence-ack lease
witnesses ride U-RT-143's suite (the fence carrier lands there); the
context-binding and CP-integration witnesses ride the CP-gating suite.
"""

from __future__ import annotations

import threading
import time

import pytest
from harness_core import SubAgentDispatchCapacityError
from harness_cp.sub_agent_dispatch_capacity_authority import (
    CapacityAuthority,
    CapacityLease,
)
from harness_runtime.lifecycle.sub_agent_dispatch_executor import (
    DISPATCH_WORKER_THREAD_NAME_PREFIX,
    RuntimeCapacityAuthorityAdapter,
    SubAgentDispatchExecutor,
)


def test_cap_saturation_next_dispatch_fails_immediately_typed_and_enqueues_nothing() -> None:
    """Filing §4 item 9 — deterministic cap+1: every frame occupied, one more
    dispatch raises the typed error IMMEDIATELY with zero queue growth
    (mutation probe: swapping fail-fast for enqueue hangs/fails this witness)."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    leases = [executor.reserve(2, step_id=f"s{i}", descent_chain=(f"s{i}",)) for i in range(2)]
    assert executor.available_frames == 0
    started = time.monotonic()
    with pytest.raises(SubAgentDispatchCapacityError) as excinfo:
        executor.reserve(1, step_id="s-over", descent_chain=("s-over",))
    elapsed = time.monotonic() - started
    assert elapsed < 0.5  # immediate — no queue wait
    assert excinfo.value.step_id == "s-over"
    # Provably zero queue growth: the work queue holds no pending item for the
    # rejected dispatch (admission never reached submission).
    assert executor._work.qsize() == 0
    for lease in leases:
        lease.release()
    assert executor.available_frames == 4


def test_grow_on_demand_workers_named_daemon_and_reused() -> None:
    """§14.8.10.1 AC #1 — spawn when no free worker; idle reuse; named daemon."""
    executor = SubAgentDispatchExecutor(frame_budget=8)
    seen_threads: list[tuple[str, bool]] = []
    record_lock = threading.Lock()

    def job() -> str:
        current = threading.current_thread()
        with record_lock:
            seen_threads.append((current.name, current.daemon))
        return current.name

    # Two sequential jobs: the second reuses the idle worker (no second spawn).
    name_a = executor.submit(job).result(timeout=5)
    name_b = executor.submit(job).result(timeout=5)
    assert name_a == name_b
    assert all(
        name.startswith(DISPATCH_WORKER_THREAD_NAME_PREFIX) and daemon
        for name, daemon in seen_threads
    )

    # Two CONCURRENT jobs: no free worker at the second submit -> a new worker.
    gate = threading.Event()

    def blocking_job() -> str:
        gate.wait(timeout=5)
        return threading.current_thread().name

    fut1 = executor.submit(blocking_job)
    fut2 = executor.submit(blocking_job)
    gate.set()
    names = {fut1.result(timeout=5), fut2.result(timeout=5)}
    assert len(names) == 2  # mutation probe: a single-worker queue serializes


def test_shutdown_drain_with_deadline_never_blocks_on_loop_bridged_worker() -> None:
    """§14.8.10.1 AC #5 — drain polls join-free and returns at the deadline
    even while a worker is wedged inside a (simulated) loop-bridged call."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    release = threading.Event()

    def wedged_job() -> None:
        release.wait(timeout=30)  # simulates a worker bridged into the loop

    executor.submit(wedged_job)
    started = time.monotonic()
    completed, still_outstanding = executor.drain(deadline_seconds=0.2)
    elapsed = time.monotonic() - started
    assert elapsed < 2.0  # returned at the deadline, not the worker's 30s
    assert still_outstanding == 1
    release.set()
    del completed


def test_completed_job_count_tracks_real_completions_not_spawned_workers() -> None:
    """The `_completed` counter (feeding `drain()`'s first return element)
    must track actual job completions, not spawned worker threads.

    Mutation probe: computing `self._spawned - still_outstanding` instead of
    a real completion counter undercounts whenever a worker is reused — one
    spawned worker serially completing 3 jobs has `_spawned == 1`, so that
    formula reports 1 completion instead of 3. Sequential submission (each
    `.result()` awaited before the next `submit`) guarantees idle-worker
    reuse, never a second spawn (same assumption as the sibling
    `test_grow_on_demand_workers_named_daemon_and_reused` witness).
    """
    executor = SubAgentDispatchExecutor(frame_budget=8)
    for _ in range(3):
        executor.submit(lambda: None).result(timeout=5)
    assert executor._spawned == 1  # reused the same idle worker every time
    assert executor._completed == 3


def test_drain_completed_count_uses_real_counter_not_spawned_tally() -> None:
    """`drain()`'s first return element must come from the real completion
    counter, not `_spawned - still_outstanding` — a `_spawned` tally
    inflated by earlier, unrelated worker churn must not leak into this
    call's completed count.

    Mutation probe: reverting to `self._spawned - still_outstanding` would
    report 50 completions (the artificially inflated spawn tally minus zero
    outstanding) instead of the real 1.
    """
    executor = SubAgentDispatchExecutor(frame_budget=8)
    executor._spawned = 50  # simulates unrelated worker churn earlier in life
    gate = threading.Event()
    executor.submit(lambda: gate.wait(timeout=5))
    completed, still_outstanding = executor.drain(deadline_seconds=0.1)
    assert completed == 0
    assert still_outstanding == 1
    gate.set()
    completed, still_outstanding = executor.drain(deadline_seconds=5.0)
    assert completed == 1
    assert still_outstanding == 0


def test_atomic_reservation_no_partial_acquisition_under_concurrent_fanouts() -> None:
    """Whole-fan-out atomicity: two racing 3-frame fan-outs vs 4 free — one
    whole, one deterministically degraded (executor-budget variant of the
    U-CP-101 witness; mutation probe: per-branch incremental acquisition
    degrades both)."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    barrier = threading.Barrier(2)
    admitted_counts: list[int] = []
    record_lock = threading.Lock()

    def run_fanout(tag: str) -> None:
        barrier.wait()
        results = executor.reserve_fanout(
            (1, 1, 1),
            step_ids=(f"{tag}-0", f"{tag}-1", f"{tag}-2"),
            descent_chain=("wf", tag),
        )
        with record_lock:
            admitted_counts.append(sum(1 for r in results if isinstance(r, CapacityLease)))

    threads = [threading.Thread(target=run_fanout, args=(t,)) for t in ("fa", "fb")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(admitted_counts) == [1, 3]


def test_reserve_fanout_prefix_break_rejects_all_after_first_miss_at_executor() -> None:
    """Executor-budget variant of the U-CP-101 fitting-prefix witness.

    Mutation probe: dropping the `admitting` early-stop lets a later smaller
    branch (needs 1, still available since the earlier miss never touched
    `remaining`) wrongly admit after an earlier branch was rejected.
    """
    executor = SubAgentDispatchExecutor(frame_budget=1)
    results = executor.reserve_fanout(
        (2, 1),
        step_ids=("b0", "b1"),
        descent_chain=("wf", "fanout"),
    )
    assert isinstance(results[0], SubAgentDispatchCapacityError)
    assert isinstance(results[1], SubAgentDispatchCapacityError)
    assert results[1].requested_frames == 1
    assert executor.available_frames == 1


def test_lease_release_exactly_once_at_executor_budget() -> None:
    """Exactly-once release across racing outcome paths at the REAL budget."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    lease = executor.reserve(3, step_id="s1", descent_chain=("s1",))
    assert executor.available_frames == 1
    assert lease.release() is True
    for _ in range(4):
        assert lease.release() is False
    assert executor.available_frames == 4


def test_adapter_satisfies_cp_protocol_and_shares_the_one_budget() -> None:
    """The composition-root adapter IS the CP authority over the real budget:
    frames reserved through the adapter deplete the executor's own admission
    (one budget, two admission surfaces — never two live authorities)."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    adapter = RuntimeCapacityAuthorityAdapter(executor)
    assert isinstance(adapter, CapacityAuthority)
    lease = adapter.reserve(3, step_id="cp-branch", descent_chain=("wf", "cp-branch"))
    # The executor's own admission sees the CP-held frames as occupied.
    with pytest.raises(SubAgentDispatchCapacityError):
        executor.reserve(2, step_id="rt-dispatch", descent_chain=("rt-dispatch",))
    assert executor.occupied_frames == 3
    lease.release()
    assert executor.available_frames == 4


def test_executor_rejects_budget_below_one() -> None:
    with pytest.raises(ValueError, match="frame_budget"):
        SubAgentDispatchExecutor(frame_budget=0)

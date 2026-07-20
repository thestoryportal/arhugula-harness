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
from typing import Any

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
    # Provably zero queue growth: a rejected admission never reaches
    # `submit()` at all — no outstanding future, no idle channel consumed,
    # no worker spawned (admission never reached submission).
    assert executor._outstanding == set()
    assert executor._idle_channels == []
    assert executor._spawned == 0
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


def test_submit_rolls_back_bookkeeping_when_thread_start_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-48 (codex round-4 [P2] "roll back submission when worker creation
    fails"): if the OS refuses a new thread, `submit()` must roll back
    `_outstanding`/`_spawned` and re-raise — without this, a phantom future
    stays in `_outstanding` forever (`drain()` never reaches zero outstanding)
    and `_spawned` over-counts a worker that never ran."""
    executor = SubAgentDispatchExecutor(frame_budget=4)

    def _start_raises(self: threading.Thread) -> None:
        raise RuntimeError("can't start new thread (simulated OS refusal)")

    monkeypatch.setattr(threading.Thread, "start", _start_raises)

    with pytest.raises(RuntimeError, match="can't start new thread"):
        executor.submit(lambda: "never runs")

    assert executor._outstanding == set()
    assert executor._spawned == 0
    # The executor is still usable afterward (state genuinely rolled back,
    # not merely masked) — restore real thread starting and confirm a
    # normal submit still works.
    monkeypatch.undo()
    assert executor.submit(lambda: "ok").result(timeout=5) == "ok"


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


def test_drain_stops_idle_workers_so_they_do_not_leak_across_process_lifetime() -> None:
    """Round-5b codex [P2] #4 "stop idle dispatch workers during shutdown": a
    worker that finished its job and is sitting idle (blocked on its own
    channel) must actually TERMINATE when `drain()` runs. Track A is
    bootstrap-per-`run()`-call (no cached `HarnessContext`) — without this, a
    long-running server process accumulates one leaked, permanently-blocked
    daemon thread per call that dispatched at least one sync sub-agent,
    unboundedly over the process's lifetime.

    Mutation probe: removing the idle-channel stop-sentinel sweep from
    `drain()` leaves this worker thread alive (still blocked on
    `channel.get()`) well past this test's poll window.

    Identifies the worker by the actual `threading.Thread` OBJECT (not by
    name) — worker names are per-executor-instance sequential
    (`...-dispatch-1`, `...-dispatch-2`, ...), so a name alone can collide
    with an unrelated worker from a DIFFERENT executor instance elsewhere in
    this test module's run."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    worker_holder: list[threading.Thread] = []

    def job() -> None:
        worker_holder.append(threading.current_thread())

    executor.submit(job).result(timeout=5)
    worker = worker_holder[0]
    # The worker is idle now — registered on its own channel, blocked on `.get()`.
    assert worker.is_alive()

    executor.drain(deadline_seconds=0.2)

    # Join-free by design (per this module's own drain discipline) — poll for
    # the woken thread to actually return.
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and worker.is_alive():
        time.sleep(0.01)
    assert not worker.is_alive(), (
        f"worker thread {worker.name!r} is still alive after drain() — "
        f"the idle-channel stop sentinel was not sent"
    )


def test_drain_stops_a_worker_that_finishes_strictly_after_the_drain_snapshot() -> None:
    """Codex round-7 [P2] "stop workers that finish after the drain snapshot":
    round-5b's fix only sentinels workers ALREADY idle when `drain()` takes its
    snapshot. A worker whose job is still OUTSTANDING at that snapshot — and
    finishes strictly AFTER `drain()` has already swept + returned — would
    re-register on a fresh channel `drain()` will never look at again and
    block forever, the same leaked-daemon-thread hazard round-5b closed for
    the already-idle case.

    Mutation probe: reverting `_worker()`'s `if self._draining: return` guard
    (restoring plain unconditional re-registration) makes this worker block on
    `my_channel.get()` forever — the join-with-timeout below observes
    `is_alive() is True` past the poll window instead of the thread exiting.
    """
    executor = SubAgentDispatchExecutor(frame_budget=4)
    job_release = threading.Event()
    worker_holder: list[threading.Thread] = []

    def late_finishing_job() -> None:
        worker_holder.append(threading.current_thread())
        job_release.wait(timeout=5)

    future = executor.submit(late_finishing_job)

    # `drain()` times out with the job still outstanding — its own snapshot +
    # sweep + `_draining=True` flip all happen while the worker is still
    # blocked inside `late_finishing_job`, well before it ever reaches the
    # re-registration point.
    completed, still_outstanding = executor.drain(deadline_seconds=0.2)
    assert still_outstanding == 1
    assert completed == 0
    assert executor._draining is True

    # NOW the job finishes — strictly after drain's snapshot/sweep returned.
    job_release.set()
    future.result(timeout=5)
    worker = worker_holder[0]

    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and worker.is_alive():
        time.sleep(0.01)
    assert not worker.is_alive(), (
        f"worker thread {worker.name!r} is still alive after finishing its "
        f"job strictly after drain()'s snapshot — it re-registered as idle "
        f"on a channel drain() will never sweep again"
    )
    # It never got the chance to publish a channel drain() could sweep.
    assert executor._idle_channels == []


def test_reserve_rejects_once_draining_has_begun() -> None:
    """Codex round-8 [P1] "reject new admissions after drain begins" —
    `reserve()` must consult `_draining`, not just capacity. Without this,
    the survivor of a shutdown-in-progress could reserve fresh frames and
    launch NEW work against an executor whose observability/provider
    clients later shutdown steps may already be closing.

    Mutation probe: dropping the `self._draining or` disjunct from
    `reserve()`'s guard condition makes this call succeed (plenty of frames
    free) instead of raising.
    """
    executor = SubAgentDispatchExecutor(frame_budget=4)
    executor.begin_draining()
    with pytest.raises(SubAgentDispatchCapacityError):
        executor.reserve(1, step_id="late", descent_chain=("late",))


def test_reserve_fanout_rejects_every_branch_once_draining_has_begun() -> None:
    """Codex round-8 [P1] sibling witness for `reserve_fanout()` — same
    rationale, whole-fan-out shape (every branch rejected, not a partial
    admit).

    Mutation probe: reverting `admitting = not self._draining` to
    `admitting = True` lets every branch admit despite draining (plenty of
    frames free).
    """
    executor = SubAgentDispatchExecutor(frame_budget=4)
    executor.begin_draining()
    results = executor.reserve_fanout(
        (1, 1), step_ids=("late-0", "late-1"), descent_chain=("wf", "late")
    )
    assert all(isinstance(r, SubAgentDispatchCapacityError) for r in results)
    assert executor.available_frames == 4  # nothing was charged


def test_submit_rejects_once_draining_has_begun() -> None:
    """Codex round-8 [P1] sibling witness for `submit()` — the caller may
    already hold a lease reserved BEFORE draining started (a legitimate
    race), but LAUNCHING the job past this point means running NEW work
    against a shutting-down executor. `submit()` must reject independently
    of whether the caller's own admission predates the drain.

    Mutation probe: removing the `if self._draining: raise ...` guard from
    `submit()` lets this job actually run (the worker would execute `fn`)
    instead of raising before ever touching `_outstanding`.
    """
    executor = SubAgentDispatchExecutor(frame_budget=4)
    lease = executor.reserve(1, step_id="pre-drain", descent_chain=("pre-drain",))
    executor.begin_draining()
    with pytest.raises(SubAgentDispatchCapacityError):
        executor.submit(lambda: "should never run", step_id="pre-drain")
    assert executor._outstanding == set()
    lease.release()


def test_begin_draining_is_idempotent_and_drain_still_reports_correctly() -> None:
    """A caller may invoke `begin_draining()` eagerly (before a bounded wait
    with no remaining budget) and `drain()` may ALSO call it again as its
    own first step — the second call must be a harmless no-op, not a
    double-sentinel or a crash, and `drain()`'s own return value must still
    be correct."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    executor.submit(lambda: None).result(timeout=5)  # leaves one idle worker
    executor.begin_draining()
    assert executor._draining is True
    assert executor._idle_channels == []
    completed, still_outstanding = executor.drain(deadline_seconds=0.1)
    assert completed == 0
    assert still_outstanding == 0


def test_job_done_runs_after_future_is_already_published(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex round-9 [P2] "complete futures before marking executor jobs
    done" — `_job_done()` (which removes the future from `_outstanding`,
    the state `drain()`'s poll loop reads) must run AFTER the future has
    published its result via `set_result()`/`set_exception()` — those calls
    fire the future's done-callbacks (lease release, the `asyncio.wrap_
    future` bridge) SYNCHRONOUSLY. With the old ordering, `drain()` could
    observe zero outstanding in the narrow window before those callbacks
    had actually run.

    Mutation probe: reverting `_run_job()` to call `_job_done(future)`
    BEFORE `future.set_result(result)` makes the spied `future.done()`
    snapshot below read `False` instead of `True` at the moment `_job_done`
    is invoked.
    """
    executor = SubAgentDispatchExecutor(frame_budget=4)
    observed_done_state: list[bool] = []
    real_job_done = executor._job_done

    def _spy_job_done(future: Any) -> None:
        observed_done_state.append(future.done())
        real_job_done(future)

    monkeypatch.setattr(executor, "_job_done", _spy_job_done)
    assert executor.submit(lambda: "ok").result(timeout=5) == "ok"
    assert observed_done_state == [True], (
        "_job_done() ran while the future was not yet done — a completion "
        "callback (lease release, asyncio bridge) may not have fired before "
        "drain() could observe this job as no longer outstanding"
    )


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

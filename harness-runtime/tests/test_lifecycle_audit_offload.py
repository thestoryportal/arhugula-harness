"""`run_audit_off_loop` — dedicated audit-offload executor witnesses.

Codex round-2 (B-47 PR B2a): audit composition must run on its OWN executor
(the loop's default pool can be exhausted by CP drivers blocking in
`SyncDispatcherFacade`, deadlocking any audit job queued there) and a
cancelled offload must JOIN its uninterruptible worker so no audit write
lands after the step was reported cancelled/timed out.
"""

from __future__ import annotations

import asyncio
import contextvars
import threading

import pytest
from harness_runtime.lifecycle.audit_offload import run_audit_off_loop


@pytest.mark.asyncio
async def test_offload_runs_when_default_executor_is_exhausted() -> None:
    """Codex round-2 P1 — with every default-executor worker blocked (the
    daemon-concurrency driver picture), the audit offload must still run:
    it owns a dedicated pool."""
    loop = asyncio.get_running_loop()
    release = threading.Event()
    # Saturate the DEFAULT executor (max_workers = min(32, cpu+4)).
    blockers = [loop.run_in_executor(None, release.wait, 10.0) for _ in range(32)]
    try:
        result = await asyncio.wait_for(run_audit_off_loop(lambda: "signed"), timeout=5.0)
        assert result == "signed"
    finally:
        release.set()
        await asyncio.gather(*blockers)


@pytest.mark.asyncio
async def test_cancelled_offload_joins_worker_before_cancellation_completes() -> None:
    """Codex round-2 P1 — cancellation cannot interrupt a worker already
    signing/writing; the helper must hold the cancellation open until the
    worker finishes, so an audit write never lands AFTER the step was
    reported cancelled."""
    started = threading.Event()
    release = threading.Event()
    wrote: list[str] = []

    def _work() -> None:
        started.set()
        assert release.wait(timeout=10.0)
        wrote.append("audit-write")

    task = asyncio.create_task(run_audit_off_loop(_work))
    assert await asyncio.to_thread(started.wait, 10.0)

    task.cancel()
    await asyncio.sleep(0.1)
    # Cancellation is BLOCKED on the join while the worker is mid-write.
    assert not task.done()

    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    # By the time the cancellation was observable, the write had landed.
    assert wrote == ["audit-write"]


@pytest.mark.asyncio
async def test_offload_propagates_contextvars() -> None:
    """`loop.run_in_executor` does not copy context (unlike to_thread); the
    helper copies it explicitly so the run-scoped cost-accumulator proxy
    and OTel span context resolve in the worker."""
    var: contextvars.ContextVar[str] = contextvars.ContextVar("audit_offload_probe")
    var.set("run-scoped-value")
    assert await run_audit_off_loop(var.get) == "run-scoped-value"


@pytest.mark.asyncio
async def test_facade_timeout_waits_for_inflight_audit_work() -> None:
    """Codex round-3 P1 — cancelling the facade's wrapper future marks it
    cancelled immediately; without an explicit acknowledgement the audit
    worker's writes could land AFTER StepDispatchTimeoutError was raised.
    The facade's timeout path drains in-flight audit work: by the time the
    timeout surfaces, the write has landed — never after."""
    from typing import Any

    from harness_runtime.lifecycle.sync_dispatcher_facade import (
        StepDispatchTimeoutError,
        materialize_sync_dispatcher_facade,
    )

    started = threading.Event()
    release = threading.Event()
    wrote: list[str] = []

    def _slow_audit_write() -> None:
        started.set()
        assert release.wait(timeout=10.0)
        wrote.append("audit-write")

    class _Inner:
        async def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Any:
            await run_audit_off_loop(_slow_audit_write)
            return {}

    facade = materialize_sync_dispatcher_facade(_Inner(), result_timeout_seconds=0.2)

    outcome: list[tuple[str, list[str]]] = []

    def _drive() -> None:
        try:
            facade.dispatch(None, None, step_context=None)  # type: ignore[arg-type]
            outcome.append(("returned", list(wrote)))
        except StepDispatchTimeoutError:
            # Snapshot at RAISE time — the drain must have completed the
            # write BEFORE the timeout became observable.
            outcome.append(("timeout", list(wrote)))

    driver = threading.Thread(target=_drive, daemon=True)
    driver.start()
    assert await asyncio.to_thread(started.wait, 10.0)

    # Past the 0.2s bound the facade is in its drain, held by the worker.
    await asyncio.sleep(0.6)
    assert driver.is_alive(), "facade surfaced the timeout without draining"
    assert wrote == []

    release.set()
    await asyncio.to_thread(driver.join, 10.0)
    assert outcome == [("timeout", ["audit-write"])]


@pytest.mark.asyncio
async def test_unacked_cancellation_flags_timeout_unresolved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex rounds 4-5 — when the dispatch task cannot acknowledge
    cancellation within the grace (stalled audit work), the timeout must be
    flagged UNRESOLVED via `audit_drain_incomplete` while KEEPING the exact
    `StepDispatchTimeoutError` type name: harness-cp's driver classifies by
    `type(exc).__name__`, so a subclass would silently fall out of the
    RT-FAIL-STEP-DISPATCH-TIMEOUT taxonomy."""
    from typing import Any

    from harness_runtime.lifecycle import sync_dispatcher_facade as facade_module
    from harness_runtime.lifecycle.sync_dispatcher_facade import (
        StepDispatchTimeoutError,
        materialize_sync_dispatcher_facade,
    )

    monkeypatch.setattr(facade_module, "_AUDIT_DRAIN_GRACE_SECONDS", 0.2)

    started = threading.Event()
    release = threading.Event()

    def _outlives_the_grace() -> None:
        started.set()
        assert release.wait(timeout=10.0)

    class _Inner:
        async def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Any:
            await run_audit_off_loop(_outlives_the_grace)
            return {}

    facade = materialize_sync_dispatcher_facade(_Inner(), result_timeout_seconds=0.2)

    outcome: list[tuple[str, bool]] = []

    def _drive() -> None:
        try:
            facade.dispatch(None, None, step_context=None)  # type: ignore[arg-type]
            outcome.append(("returned", False))
        except StepDispatchTimeoutError as exc:
            outcome.append((type(exc).__name__, getattr(exc, "audit_drain_incomplete", False)))

    driver = threading.Thread(target=_drive, daemon=True)
    driver.start()
    assert await asyncio.to_thread(started.wait, 10.0)
    await asyncio.to_thread(driver.join, 10.0)
    release.set()

    # Exact type name preserved for the driver taxonomy; UNRESOLVED flagged.
    assert outcome == [("StepDispatchTimeoutError", True)]


@pytest.mark.asyncio
async def test_audit_offload_workers_are_daemon_threads() -> None:
    """Codex round-5 P1 — ThreadPoolExecutor workers are non-daemon and the
    interpreter JOINS them at exit: a stalled KMS sign would hold the whole
    process open after bounded shutdown already returned. The hand-rolled
    executor's workers must be daemon."""
    await run_audit_off_loop(lambda: "warm")
    workers = [t_ for t_ in threading.enumerate() if t_.name.startswith("harness-audit-offload")]
    assert workers, "no audit-offload worker thread found"
    assert all(t_.daemon for t_ in workers)


@pytest.mark.asyncio
async def test_no_audit_write_lands_after_timeout_surfaces() -> None:
    """Codex round-5 P1 — a dispatch busy in SYNC work on the loop has not
    SUBMITTED its audit job when the facade cancels; an empty-snapshot
    drain would let the write land after the timeout raise. The
    per-dispatch ack closes it: whatever the task's audit path did is
    finished before the raise; nothing lands afterwards."""
    import time as time_module
    from typing import Any

    from harness_runtime.lifecycle.sync_dispatcher_facade import (
        StepDispatchTimeoutError,
        materialize_sync_dispatcher_facade,
    )

    wrote: list[str] = []

    class _Inner:
        async def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Any:
            # Sync work ON the loop delays cancellation delivery past the
            # facade's bound — the audit job is not yet submitted when the
            # facade cancels.
            time_module.sleep(0.5)  # noqa: ASYNC251 — deliberately BLOCKS the loop (the scenario under test)
            await run_audit_off_loop(lambda: wrote.append("late-audit-write"))
            return {}

    facade = materialize_sync_dispatcher_facade(_Inner(), result_timeout_seconds=0.1)

    snapshot_at_raise: list[list[str]] = []

    def _drive() -> None:
        try:
            facade.dispatch(None, None, step_context=None)  # type: ignore[arg-type]
        except StepDispatchTimeoutError:
            snapshot_at_raise.append(list(wrote))

    driver = threading.Thread(target=_drive, daemon=True)
    driver.start()
    await asyncio.to_thread(driver.join, 10.0)
    assert snapshot_at_raise, "facade did not raise the step timeout"

    # Nothing may land AFTER the raise: whatever was written at raise time
    # is the final state.
    await asyncio.sleep(1.0)
    assert wrote == snapshot_at_raise[0]


@pytest.mark.asyncio
async def test_burst_after_warmup_runs_concurrently() -> None:
    """Codex round-6 P1 — the idle-count spawn heuristic never RESERVED the
    capacity a burst observed: four jobs after a warm-up all saw idle > 0
    and serialized on ONE worker, pushing concurrent dispatches past their
    timeouts. Spawning now tracks outstanding demand: a 4-job burst must
    reach 4 concurrent workers."""
    from harness_runtime.lifecycle.audit_offload import AUDIT_OFFLOAD_MAX_WORKERS

    await run_audit_off_loop(lambda: "warm-up")

    barrier = threading.Barrier(AUDIT_OFFLOAD_MAX_WORKERS, timeout=10.0)

    def _job() -> str:
        barrier.wait()  # passes ONLY if all four run concurrently
        return "done"

    results = await asyncio.wait_for(
        asyncio.gather(*(run_audit_off_loop(_job) for _ in range(AUDIT_OFFLOAD_MAX_WORKERS))),
        timeout=8.0,
    )
    assert results == ["done"] * AUDIT_OFFLOAD_MAX_WORKERS


def test_for_single_host_forwards_signing_backend() -> None:
    """Codex round-6 P2 — the single-host convenience constructor dropped
    the signing backend, leaving single-server KMS deployments on
    placeholder-signed tool cost audits."""
    from types import SimpleNamespace
    from typing import Any, cast

    from harness_runtime.lifecycle.runtime_tool_dispatcher import RuntimeToolDispatcher

    sentinel = object()
    host = SimpleNamespace(
        server_name="s1",
        tool_registry=SimpleNamespace(names=lambda: []),
    )
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=cast(Any, host),
        per_server_trust_evaluator=cast(Any, object()),
        mcp_namespace_emitter=cast(Any, object()),
        trust_policy=cast(Any, object()),
        signing_backend=sentinel,
    )
    assert dispatcher._signing_backend is sentinel


@pytest.mark.asyncio
async def test_join_survives_repeated_cancellation() -> None:
    """Codex round-8 P1 — a facade timeout followed by an outer/shutdown
    cancellation delivered a SECOND CancelledError that the single suppress
    absorbed once and exited with the worker still running: the write could
    land after the caller observed cancellation. The join must hold across
    repeated cancellations until the worker actually finished."""
    started = threading.Event()
    release = threading.Event()
    wrote: list[str] = []

    def _work() -> None:
        started.set()
        assert release.wait(timeout=10.0)
        wrote.append("audit-write")

    task = asyncio.create_task(run_audit_off_loop(_work))
    assert await asyncio.to_thread(started.wait, 10.0)

    task.cancel()
    await asyncio.sleep(0.1)
    task.cancel()  # the second cancellation (outer task / shutdown)
    await asyncio.sleep(0.1)
    assert not task.done(), "join abandoned after the second cancellation"

    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    # The write landed BEFORE the cancellation became observable.
    assert wrote == ["audit-write"]


@pytest.mark.asyncio
async def test_stalled_worker_detaches_after_bounded_join_grace(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Codex round-10 P1 — the repeated-cancellation join was UNBOUNDED:
    asyncio.run's cancellation cleanup waits for the pending task, so a
    stalled KMS sign held process exit indefinitely despite the daemon
    worker. Past the grace the worker detaches with a loud ERROR; the task
    completes cancelled within the bound."""
    import logging as logging_module

    from harness_runtime.lifecycle import audit_offload as offload_module

    monkeypatch.setattr(offload_module, "AUDIT_CANCEL_JOIN_GRACE_SECONDS", 0.3)

    started = threading.Event()
    release = threading.Event()

    def _stalled() -> None:
        started.set()
        release.wait(timeout=30.0)

    task = asyncio.create_task(run_audit_off_loop(_stalled))
    assert await asyncio.to_thread(started.wait, 10.0)

    with caplog.at_level(logging_module.ERROR, logger="harness.runtime.audit_signing"):
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(task), timeout=3.0)

    assert any("outlived" in r.message for r in caplog.records)
    release.set()


@pytest.mark.asyncio
async def test_capacity_recovers_after_detaching_stalled_workers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-12 P1 — a detached (stalled) worker still occupied a pool
    slot: with every worker stalled-detached, later audit jobs queued
    forever and the breaker never opened. Detach now releases the slot so
    the next submit spawns a replacement."""
    from harness_runtime.lifecycle import audit_offload as offload_module
    from harness_runtime.lifecycle.audit_offload import AUDIT_OFFLOAD_MAX_WORKERS

    monkeypatch.setattr(offload_module, "AUDIT_CANCEL_JOIN_GRACE_SECONDS", 0.2)

    started = threading.Barrier(AUDIT_OFFLOAD_MAX_WORKERS + 1, timeout=10.0)
    release = threading.Event()

    def _stalled() -> None:
        started.wait()
        release.wait(timeout=30.0)

    # Stall EVERY worker, then detach them all via cancellation.
    tasks = [
        asyncio.create_task(run_audit_off_loop(_stalled)) for _ in range(AUDIT_OFFLOAD_MAX_WORKERS)
    ]
    await asyncio.to_thread(started.wait)
    for task in tasks:
        task.cancel()
    for task in tasks:
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(task), timeout=5.0)

    # A NEW audit job must still run — a replacement worker serves it.
    result = await asyncio.wait_for(run_audit_off_loop(lambda: "recovered"), timeout=5.0)
    assert result == "recovered"
    release.set()


@pytest.mark.asyncio
async def test_detached_workers_retire_and_thread_count_converges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-13 P2 — a detached worker whose stalled job eventually
    returned kept serving the queue forever alongside its replacement:
    repeated detaches grew the thread count without bound and allowed
    concurrency above the cap. Detached workers now retire when their
    stalled job finishes; the pool converges back to <= cap."""
    import time as time_module

    from harness_runtime.lifecycle import audit_offload as offload_module
    from harness_runtime.lifecycle.audit_offload import AUDIT_OFFLOAD_MAX_WORKERS

    monkeypatch.setattr(offload_module, "AUDIT_CANCEL_JOIN_GRACE_SECONDS", 0.2)

    started = threading.Barrier(AUDIT_OFFLOAD_MAX_WORKERS + 1, timeout=10.0)
    release = threading.Event()

    def _stalled() -> None:
        started.wait()
        release.wait(timeout=30.0)

    tasks = [
        asyncio.create_task(run_audit_off_loop(_stalled)) for _ in range(AUDIT_OFFLOAD_MAX_WORKERS)
    ]
    await asyncio.to_thread(started.wait)
    for task in tasks:
        task.cancel()
    for task in tasks:
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(task), timeout=5.0)

    # Replacement capacity works while the stalled originals linger.
    assert await asyncio.wait_for(run_audit_off_loop(lambda: "ok"), timeout=5.0) == "ok"

    # Let every stalled job finish: its (marked) worker must EXIT, so the
    # ALIVE audit-offload thread count converges back to <= cap.
    release.set()
    deadline = time_module.monotonic() + 8.0
    while time_module.monotonic() < deadline:
        alive = [
            t_
            for t_ in threading.enumerate()
            if t_.name.startswith("harness-audit-offload") and t_.is_alive()
        ]
        if len(alive) <= AUDIT_OFFLOAD_MAX_WORKERS:
            break
        await asyncio.sleep(0.05)
    assert len(alive) <= AUDIT_OFFLOAD_MAX_WORKERS, [t_.name for t_ in alive]


def test_release_is_noop_when_worker_already_finished() -> None:
    """Codex round-14 P2 — a stalled job can finish between the caller's
    done() check and the release lock: the worker has already moved on, so
    releasing would leak an unconsumed retire marker and spawn a
    replacement alongside a live worker. Membership in the serving set
    (same lock) makes the release a no-op in that boundary race."""
    from harness_runtime.lifecycle.audit_offload import _DaemonThreadAuditExecutor

    executor = _DaemonThreadAuditExecutor(2)
    future = executor.submit(lambda: "done")
    assert future.result(timeout=5.0) == "done"

    spawned_before = executor._spawned
    executor.release_stalled_slot(future)
    assert executor._spawned == spawned_before
    assert future not in executor._retire_after


@pytest.mark.asyncio
async def test_already_queued_job_served_after_detaching_all_workers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-15 P1 — worker creation happened only in submit(): a job
    ALREADY queued when every worker detached hung until some later
    submission. The release path now spawns replacement capacity for
    existing outstanding demand."""
    from harness_runtime.lifecycle import audit_offload as offload_module
    from harness_runtime.lifecycle.audit_offload import AUDIT_OFFLOAD_MAX_WORKERS

    monkeypatch.setattr(offload_module, "AUDIT_CANCEL_JOIN_GRACE_SECONDS", 0.2)

    started = threading.Barrier(AUDIT_OFFLOAD_MAX_WORKERS + 1, timeout=10.0)
    release = threading.Event()

    def _stalled() -> None:
        started.wait()
        release.wait(timeout=30.0)

    stall_tasks = [
        asyncio.create_task(run_audit_off_loop(_stalled)) for _ in range(AUDIT_OFFLOAD_MAX_WORKERS)
    ]
    await asyncio.to_thread(started.wait)

    # Queue one MORE job while every worker is stalled — no further submits
    # will follow it.
    queued = asyncio.create_task(run_audit_off_loop(lambda: "served"))
    await asyncio.sleep(0.05)

    for task in stall_tasks:
        task.cancel()
    for task in stall_tasks:
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(task), timeout=5.0)

    assert await asyncio.wait_for(queued, timeout=5.0) == "served"
    release.set()


def test_detached_worker_cap_stops_capacity_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-15 P1 — unlimited detach-driven replacement grows threads
    and in-flight KMS calls without bound against a hung backend. At the
    cap, release keeps the slot occupied (jobs queue; callers time out
    boundedly)."""
    import time as time_module

    from harness_runtime.lifecycle import audit_offload as offload_module
    from harness_runtime.lifecycle.audit_offload import _DaemonThreadAuditExecutor

    monkeypatch.setattr(offload_module, "AUDIT_DETACHED_WORKER_CAP", 1)

    executor = _DaemonThreadAuditExecutor(2)
    release = threading.Event()
    started = threading.Barrier(3, timeout=10.0)

    def _stalled() -> None:
        started.wait()
        release.wait(timeout=30.0)

    futures = [executor.submit(_stalled) for _ in range(2)]
    started.wait()

    executor.release_stalled_slot(futures[0])  # honored (cap 1)
    executor.release_stalled_slot(futures[1])  # refused at the cap
    with executor._lock:
        assert executor._detached_live == 1
        # Honored release: slot freed AND replacement spawned for the
        # outstanding demand (net 2). The REFUSED release changed nothing —
        # without the cap it would have pushed detached_live to 2 and
        # spawned another replacement.
        assert executor._spawned == 2

    def _detached_live_now() -> int:
        # Function boundary defeats pyright literal-narrowing (the value is
        # mutated by worker threads).
        with executor._lock:
            return executor._detached_live

    release.set()
    deadline = time_module.monotonic() + 5.0
    while time_module.monotonic() < deadline:
        if _detached_live_now() == 0:
            break
        time_module.sleep(0.02)
    assert _detached_live_now() == 0  # retired worker returned its token


def test_cap_refused_stall_reclaimed_when_capacity_reopens() -> None:
    """Codex round-16 P1 — a cap-refused stalled future kept its slot
    forever even after an older detached worker finished and returned its
    token. The retire path now reclaims one refused stall per returned
    token."""
    import time as time_module

    from harness_runtime.lifecycle import audit_offload as offload_module
    from harness_runtime.lifecycle.audit_offload import _DaemonThreadAuditExecutor

    executor = _DaemonThreadAuditExecutor(2)
    ev0, ev1 = threading.Event(), threading.Event()
    started = threading.Barrier(3, timeout=10.0)

    def _stall(ev: threading.Event) -> None:
        started.wait()
        ev.wait(timeout=30.0)

    f0 = executor.submit(lambda: _stall(ev0))
    f1 = executor.submit(lambda: _stall(ev1))
    started.wait()

    original_cap = offload_module.AUDIT_DETACHED_WORKER_CAP
    try:
        offload_module.AUDIT_DETACHED_WORKER_CAP = 1  # type: ignore[misc]
        executor.release_stalled_slot(f0)  # honored
        executor.release_stalled_slot(f1)  # refused, recorded

        with executor._lock:
            assert executor._detached_live == 1
            assert f1 in executor._cap_refused

        # The honored stall finishes: its worker retires and returns the
        # token — the refused stall must be reclaimed (released + marked).
        ev0.set()
        deadline = time_module.monotonic() + 5.0
        reclaimed = False
        while time_module.monotonic() < deadline:
            with executor._lock:
                reclaimed = f1 in executor._retire_after and not executor._cap_refused
            if reclaimed:
                break
            time_module.sleep(0.02)
        assert reclaimed, "refused stall was not reclaimed when capacity reopened"
    finally:
        offload_module.AUDIT_DETACHED_WORKER_CAP = original_cap  # type: ignore[misc]
        ev1.set()
        ev0.set()


def test_submit_fails_fast_when_queue_saturated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-16 P1 — with every worker hung, each further dispatch
    enqueued (future, fn, context) forever: sustained traffic during a
    hung-backend outage could exhaust memory. At the queue cap, submit
    fails the future immediately with the TYPED signing failure the
    best-effort sites surface loudly."""
    from harness_runtime.lifecycle import audit_offload as offload_module
    from harness_runtime.lifecycle.audit_offload import (
        AuditSigningFailedError,
        _DaemonThreadAuditExecutor,
    )

    monkeypatch.setattr(offload_module, "AUDIT_OFFLOAD_QUEUE_CAP", 2)

    executor = _DaemonThreadAuditExecutor(1)
    release = threading.Event()
    started = threading.Event()

    def _stall() -> None:
        started.set()
        release.wait(timeout=30.0)

    executor.submit(_stall)
    assert started.wait(timeout=10.0)
    executor.submit(lambda: None)  # queued (outstanding=2 == cap)

    saturated = executor.submit(lambda: None)
    with pytest.raises(AuditSigningFailedError, match="saturated"):
        saturated.result(timeout=1.0)
    release.set()

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
            time_module.sleep(0.5)
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
    assert dispatcher._signing_backend is sentinel  # noqa: SLF001


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

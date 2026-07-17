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

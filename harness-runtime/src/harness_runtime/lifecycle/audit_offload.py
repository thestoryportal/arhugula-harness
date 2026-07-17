"""Dedicated off-loop executor for audit composition — B-47 PR B2a.

Out-of-family Codex round-2 findings on the PR B2a landing:

**Why not `asyncio.to_thread` (P1 — executor exhaustion deadlock).** The CP
driver's sync `execute_workflow` runs in the LOOP'S DEFAULT executor
(`asyncio.to_thread(execute_workflow, ...)` at `api.py`), and under daemon
concurrency every default-pool worker can be a driver blocking in
`SyncDispatcherFacade.dispatch` awaiting a loop coroutine. An audit offload
queued onto that same exhausted pool can never start, so every dispatch
stalls until timeout. Audit composition therefore runs on its OWN small
executor — audit jobs are short (one sign + file writes), so a small pool
suffices and can never be occupied by long-running drivers.

**Join-on-cancel (P1 — no post-timeout audit commits).** When a step's
dispatch is cancelled (`SyncDispatcherFacade` timeout), cancelling the
awaiting coroutine cannot interrupt a worker already signing/writing — left
detached it could land F2/sidecar/ledger writes AFTER the step was reported
timed out, racing retries and shutdown. On cancellation the helper JOINS the
in-flight worker (awaits its completion, suppressing its outcome) before
letting the cancellation complete: whatever the worker wrote is durable
BEFORE the caller observes the cancellation, never after.

`contextvars` are copied explicitly (`loop.run_in_executor` does not copy
context the way `asyncio.to_thread` does) so the run-scoped cost-accumulator
proxy and OTel span context still resolve in the worker.
"""

from __future__ import annotations

import asyncio
import contextlib
import contextvars
import functools
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Final

__all__ = [
    "AUDIT_OFFLOAD_MAX_WORKERS",
    "drain_inflight_audit_work",
    "run_audit_off_loop",
]

#: Small by design: audit jobs are short-lived (one signature + local file
#: writes); long-running work (drivers, child workflows) must never run
#: here or the exhaustion-deadlock this pool exists to prevent returns.
AUDIT_OFFLOAD_MAX_WORKERS: Final[int] = 4

_AUDIT_OFFLOAD_EXECUTOR: Final[ThreadPoolExecutor] = ThreadPoolExecutor(
    max_workers=AUDIT_OFFLOAD_MAX_WORKERS,
    thread_name_prefix="harness-audit-offload",
)

# In-flight audit jobs (codex round-3 P1 on PR B2a): `SyncDispatcherFacade`'s
# timeout path cancels its `run_coroutine_threadsafe` future, which is marked
# cancelled IMMEDIATELY — the facade has no handle on the coroutine's actual
# completion, so the run_audit_off_loop join alone cannot stop an audit write
# from landing after `StepDispatchTimeoutError` was raised. The facade calls
# `drain_inflight_audit_work` (sync, from its worker thread) after cancelling
# so every worker that was signing/writing at cancel time completes BEFORE
# the timeout is surfaced. Scoped to ALL in-flight jobs, not per-step — audit
# jobs are short and over-waiting is harmless; per-step keying is not worth
# the plumbing.
_INFLIGHT_LOCK: Final[threading.Lock] = threading.Lock()
_INFLIGHT: Final[set[Any]] = set()


def drain_inflight_audit_work(timeout_seconds: float) -> bool:
    """Block (bounded) until every currently in-flight audit job completes.

    Sync — callable from worker threads (the facade's timeout path), NEVER
    from the event loop. Returns False when the bound expired with jobs
    still running (the caller surfaces its timeout regardless; the residual
    risk window is then explicit, not silent).
    """
    with _INFLIGHT_LOCK:
        pending = list(_INFLIGHT)
    if not pending:
        return True
    from concurrent.futures import wait as _wait

    done, not_done = _wait(pending, timeout=timeout_seconds)
    _ = done
    return not not_done


def _discard_inflight(future: Any) -> None:
    with _INFLIGHT_LOCK:
        _INFLIGHT.discard(future)


async def run_audit_off_loop(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Run sync audit composition on the dedicated executor; join on cancel."""
    loop = asyncio.get_running_loop()
    context = contextvars.copy_context()
    call = functools.partial(context.run, functools.partial(fn, *args, **kwargs))
    # Submit DIRECTLY (not run_in_executor): task cancellation marks the
    # asyncio wrapper future cancelled even while the worker keeps running,
    # so the join below must hold the CONCURRENT future, which faithfully
    # reports the worker's real completion.
    concurrent_future = _AUDIT_OFFLOAD_EXECUTOR.submit(call)
    with _INFLIGHT_LOCK:
        _INFLIGHT.add(concurrent_future)
    concurrent_future.add_done_callback(_discard_inflight)
    try:
        return await asyncio.wrap_future(concurrent_future)
    except asyncio.CancelledError:
        # The worker cannot be interrupted mid-write; join it so its audit
        # writes are complete BEFORE the cancellation is observed — never
        # landing after the step was reported timed out. `cancel()` only
        # succeeds for a job still QUEUED (nothing written — safe to drop).
        # The join bridges via a daemon thread + call_soon_threadsafe (the
        # shutdown `_run_fsync_bounded` pattern): waiting on the audit pool
        # itself could deadlock it, and the default pool is the exhaustion
        # hazard this module exists to avoid. The worker's own outcome is
        # suppressed — the step is being abandoned either way.
        if not concurrent_future.cancel():
            joined = asyncio.Event()

            def _join_then_signal() -> None:
                with contextlib.suppress(BaseException):
                    concurrent_future.result()
                with contextlib.suppress(RuntimeError):
                    loop.call_soon_threadsafe(joined.set)

            threading.Thread(
                target=_join_then_signal, daemon=True, name="harness-audit-join"
            ).start()
            with contextlib.suppress(asyncio.CancelledError):
                await joined.wait()
        raise

"""Dedicated off-loop executor for audit composition — B-47 PR B2a.

**Cite anchors.** The executor itself is the pool `Spec_Harness_Runtime_v1.md`
v1.102 §14.8.10.1 names verbatim as "the 4-worker audit-offload executor" when
ruling it INELIGIBLE for B-48's sub-agent offload (the sibling grow-on-demand
executor at `lifecycle/sub_agent_dispatch_executor.py`, U-RT-141). Beyond the
B-47 audit-write venue, this module hosts `resolve_result_ref_off_loop` — the
off-loop half of **U-RT-145**'s §14.8.11 protected-result-store resolution
(B-65-A); see that function's own docstring for the codex round-4 P1 grounding.
A THIRD tenant lives here but on its OWN pool: the durable pause-journal
capture (`B-103`, `lifecycle/durable_pause_resume_protocol.py`) runs via
`run_pause_journal_off_loop` against `_PAUSE_JOURNAL_OFFLOAD_EXECUTOR`. Its
blocking `fcntl.flock` wait does NOT fit the audit pool's short-job profile,
and reusing that pool would let contended captures stall audit signing — the
same reasoning §14.8.10.1 applied when ruling it ineligible for B-48. Both
pools share one join-on-cancel body (`_run_off_loop_join_on_cancel`); only the
executor and the grace differ.

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
import logging
import queue
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any, Final

from harness_runtime.lifecycle.audit_signing_errors import AuditSigningFailedError
from harness_runtime.lifecycle.protected_result_store import (
    ProtectedResultStore,
    ResultRefValue,
    UnresolvableResultRef,
    resolve_result_ref,
)

__all__ = [
    "AUDIT_OFFLOAD_MAX_WORKERS",
    "PAUSE_JOURNAL_CANCEL_JOIN_GRACE_SECONDS",
    "PAUSE_JOURNAL_OFFLOAD_MAX_WORKERS",
    "resolve_result_ref_off_loop",
    "run_audit_off_loop",
    "run_off_loop_detach_on_cancel",
    "run_pause_journal_off_loop",
]

#: Small by design: audit jobs are short-lived (one signature + local file
#: writes); long-running work (drivers, child workflows) must never run
#: here or the exhaustion-deadlock this pool exists to prevent returns.
AUDIT_OFFLOAD_MAX_WORKERS: Final[int] = 4

#: Bounded cancellation-join grace (codex round-10 P1) — matches the
#: facade's ack grace: long enough for one KMS sign + local file writes,
#: short enough that a stalled backend cannot hold process exit.
AUDIT_CANCEL_JOIN_GRACE_SECONDS: Final[float] = 10.0

#: Hard bound on concurrently-detached (stalled, still-running) workers
#: (codex round-15 P1): each detach spawns replacement capacity, so
#: sustained traffic against a hung KMS would otherwise accumulate
#: unbounded threads and in-flight requests. At the cap, further detaches
#: stop releasing capacity — later audit jobs queue and their callers hit
#: their own bounded timeouts instead of growing the pool.
AUDIT_DETACHED_WORKER_CAP: Final[int] = 8

#: Pause-journal capture runs on its OWN pool, never the audit pool
#: (out-of-family Codex [P1] round 1 on the `B-103` arc). Its wait is a
#: BLOCKING `fcntl.flock` on a peer process's append, which does not fit the
#: "short-lived, one sign + local writes" profile `AUDIT_OFFLOAD_MAX_WORKERS`
#: is sized for: four contended captures would occupy every audit slot and
#: stall unrelated audit-signing / ref-resolution jobs. Runtime spec v1.102
#: §14.8.10.1 already ruled this same 4-worker pool INELIGIBLE for `B-48`'s
#: sub-agent offload on the identical reasoning — isolation here follows that
#: ruling rather than re-testing it.
PAUSE_JOURNAL_OFFLOAD_MAX_WORKERS: Final[int] = 4

#: Cancellation-join grace for a pause capture. Longer than the audit grace:
#: the audit bound is calibrated for a stalled remote KMS, whereas this wait is
#: a same-host advisory lock held by a peer harness process for exactly one
#: append — so waiting longer is far more likely to reach a durable record than
#: to be waiting on something permanently wedged.
PAUSE_JOURNAL_CANCEL_JOIN_GRACE_SECONDS: Final[float] = 30.0

#: Hard bound on QUEUED-but-unserved audit jobs (codex round-16 P1): with
#: every worker hung and the detach cap reached, each further dispatch
#: enqueued its (future, fn, context) tuple forever — sustained traffic
#: during a hung-backend outage could exhaust memory. At the cap, submit
#: fails the future immediately with the TYPED signing failure (loudly
#: surfaced by every best-effort site), keeping memory bounded.
AUDIT_OFFLOAD_QUEUE_CAP: Final[int] = 64


class _DaemonThreadAuditExecutor:
    """Hand-rolled daemon-thread work queue (framework-pull discipline).

    NOT `ThreadPoolExecutor` (codex round-5 P1): its workers are non-daemon
    and the interpreter JOINS them at exit — a KMS signing call that stalls
    or merely outlives the shutdown budget would hold the whole process
    open after the bounded runtime shutdown already returned its timeout
    report. Daemon workers die with the process; a queued-but-unstarted job
    still supports `Future.cancel()` via `set_running_or_notify_cancel`.
    """

    def __init__(self, max_workers: int, thread_name_prefix: str = "harness-audit-offload") -> None:
        self._max_workers = max_workers
        # Per-INSTANCE thread naming (`B-103`): a second pool sharing the audit
        # pool's thread-name prefix would make the two indistinguishable both to
        # an operator reading a stack dump and to the thread-count assertions
        # this module's own tests make against the audit pool.
        self._thread_name_prefix = thread_name_prefix
        self._queue: queue.SimpleQueue[tuple[Future[Any], Callable[[], Any]]] = queue.SimpleQueue()
        self._lock = threading.Lock()
        self._spawned = 0
        # Futures whose worker must EXIT after finishing them (codex
        # round-13 P2): a detached worker whose stalled job eventually
        # returned would otherwise keep serving the queue forever alongside
        # its replacement — repeated detaches grew the thread count without
        # bound and allowed concurrency above the cap.
        self._retire_after: set[Future[Any]] = set()
        # Futures currently being SERVED by a worker (codex round-14 P2):
        # membership decides — under the one lock — whether a stalled-slot
        # release is real (worker still busy: decrement + mark retire) or a
        # boundary-race no-op (the job finished between the caller's done()
        # check and this lock: nothing to release, no marker to leak).
        self._serving: set[Future[Any]] = set()
        # Detached workers whose stalled call is still running (codex
        # round-15 P1) — bounded by AUDIT_DETACHED_WORKER_CAP.
        self._detached_live = 0
        # Stalled futures whose release was refused at the detach cap
        # (codex round-16 P1) — reclaimed one-for-one when a retired
        # worker returns its detached-live token.
        self._cap_refused: set[Future[Any]] = set()
        # Jobs submitted and not yet finished (codex round-6 P1): the
        # earlier idle-count heuristic never RESERVED the idle capacity a
        # burst observed, so four jobs after a warm-up all saw idle > 0 and
        # ran serialized on one worker. Spawning tracks outstanding demand
        # instead: workers exist while spawned < min(cap, outstanding).
        self._outstanding = 0

    def submit(self, fn: Callable[[], Any]) -> Future[Any]:
        future: Future[Any] = Future()
        with self._lock:
            if self._outstanding >= AUDIT_OFFLOAD_QUEUE_CAP:
                saturated = AuditSigningFailedError(
                    f"audit offload saturated: {self._outstanding} jobs "
                    f"outstanding against a stalled backend — failing fast "
                    f"instead of queueing unboundedly"
                )
                future.set_exception(saturated)
                return future
            self._outstanding += 1
            self._spawn_for_demand_locked()
        self._queue.put((future, fn))
        return future

    def _spawn_for_demand_locked(self) -> None:
        """Spawn a worker when outstanding demand warrants — caller holds
        the lock."""
        if self._spawned < min(self._max_workers, self._outstanding):
            self._spawned += 1
            threading.Thread(
                target=self._worker,
                daemon=True,
                name=f"{self._thread_name_prefix}-{self._spawned}",
            ).start()

    def release_stalled_slot(self, stalled_future: Future[Any]) -> None:
        """Recover pool capacity after a detach (codex round-12 P1).

        A DETACHED worker (stalled KMS/filesystem call that outlived the
        cancellation-join grace) still occupied a pool slot: once all
        workers were stalled-detached, every later audit job queued forever
        and the breaker could never open. Decrementing `_spawned` lets the
        next submit spawn a replacement; when a stalled worker eventually
        finishes it simply serves the queue alongside — a transient
        over-spawn bounded by the number of detach events, all daemon.
        """
        with self._lock:
            if stalled_future not in self._serving:
                # Boundary race (codex round-14 P2): the job finished after
                # the caller's done() check — its worker already moved on.
                # Releasing here would leak an unconsumed retire marker and
                # spawn a replacement alongside a live worker.
                return
            if self._detached_live >= AUDIT_DETACHED_WORKER_CAP:
                # Codex round-15 P1: unlimited detach-driven replacement
                # would grow threads + in-flight KMS calls without bound
                # against a hung backend. At the cap, keep the slot
                # occupied — later jobs queue and their callers time out
                # boundedly instead.
                self._cap_refused.add(stalled_future)
                logging.getLogger("harness.runtime.audit_signing").error(
                    "audit-offload detached-worker cap (%d) reached — not "
                    "releasing further capacity while stalled calls are "
                    "outstanding; subsequent audit jobs will queue (refusal "
                    "recorded; reclaimed when capacity reopens)",
                    AUDIT_DETACHED_WORKER_CAP,
                )
                return
            self._detached_live += 1
            self._spawned = max(0, self._spawned - 1)
            self._retire_after.add(stalled_future)
            # Codex round-15 P1 (queued-orphan half): worker creation
            # otherwise happens only in submit() — jobs ALREADY queued when
            # every worker detached would hang until some later submission.
            self._spawn_for_demand_locked()

    def _reclaim_refused_locked(self) -> None:
        """Release one cap-refused stalled future now that a detached-live
        token returned (codex round-16 P1) — caller holds the lock. Without
        this, a still-hung replacement kept its slot forever once refused,
        even after capacity reopened."""
        while self._cap_refused and self._detached_live < AUDIT_DETACHED_WORKER_CAP:
            candidate = self._cap_refused.pop()
            if candidate not in self._serving:
                continue  # finished while waiting — nothing to release
            self._detached_live += 1
            self._spawned = max(0, self._spawned - 1)
            self._retire_after.add(candidate)
            self._spawn_for_demand_locked()
            return

    def _worker(self) -> None:
        while True:
            future, fn = self._queue.get()
            if self._serve(future, fn):
                # Slot released at detach; the replacement serves the queue.
                # Exit AFTER the finally (ruff B012, codex round-14 P1: a
                # return inside finally would suppress in-flight exceptions).
                return

    def _serve(self, future: Future[Any], fn: Callable[[], Any]) -> bool:
        """Run one job; return True when this worker must retire."""
        with self._lock:
            self._serving.add(future)
        try:
            if future.set_running_or_notify_cancel():
                try:
                    result = fn()
                except BaseException as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(result)
        finally:
            with self._lock:
                self._serving.discard(future)
                self._outstanding -= 1
                retire = future in self._retire_after
                self._retire_after.discard(future)
                if retire:
                    self._detached_live -= 1
                    self._reclaim_refused_locked()
        return retire


_AUDIT_OFFLOAD_EXECUTOR: Final[_DaemonThreadAuditExecutor] = _DaemonThreadAuditExecutor(
    AUDIT_OFFLOAD_MAX_WORKERS
)

#: `B-103`'s dedicated pool. A SECOND INSTANCE of the same hand-rolled executor
#: — not a new mechanism: every property that pool needs (daemon workers,
#: cancel-a-queued-job, detach-and-replace, slot release, saturation refusal)
#: is already built and reviewed here. What isolation buys is that a wedged
#: peer holding a journal lock can exhaust ONLY pause-journal capacity.
_PAUSE_JOURNAL_OFFLOAD_EXECUTOR: Final[_DaemonThreadAuditExecutor] = _DaemonThreadAuditExecutor(
    PAUSE_JOURNAL_OFFLOAD_MAX_WORKERS,
    thread_name_prefix="harness-pause-journal-offload",
)


async def _run_off_loop_join_on_cancel(
    executor: _DaemonThreadAuditExecutor,
    grace_seconds: float,
    what: str,
    fn: Callable[..., Any],
    /,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run `fn` on `executor`; on cancellation JOIN the worker, bounded by grace.

    Extracted at the `B-103` arc so the pause-journal pool reuses this
    already-reviewed body verbatim instead of growing a second copy of it. The
    audit path's behaviour is unchanged — `run_audit_off_loop` is now a thin
    binding of (audit executor, audit grace) onto this function.
    """
    context = contextvars.copy_context()
    call = functools.partial(context.run, functools.partial(fn, *args, **kwargs))
    # Submit DIRECTLY (not run_in_executor): task cancellation marks the
    # asyncio wrapper future cancelled even while the worker keeps running,
    # so the join below must hold the CONCURRENT future, which faithfully
    # reports the worker's real completion.
    concurrent_future = executor.submit(call)
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
            # Join the uninterruptible worker across REPEATED cancellations
            # (codex round-8 P1): a facade timeout followed by an outer
            # task/shutdown cancellation delivered a second CancelledError
            # that a single suppress absorbed once and then exited with the
            # worker still running — the write could land after the caller
            # observed cancellation. Each further CancelledError is absorbed
            # and the join resumes (10ms poll, only during this
            # already-cancelled window) — but BOUNDED (codex round-10 P1):
            # asyncio.run's cancellation cleanup waits for this pending
            # task, so an unbounded join let a stalled KMS sign hold
            # process exit indefinitely despite the daemon worker. Past the
            # grace the worker is DETACHED with a loud ERROR — the residual
            # (a possibly-late write) is then explicit and bounded, the
            # same unresolved semantics the facade flags via
            # audit_drain_incomplete.
            deadline = time.monotonic() + grace_seconds
            while not concurrent_future.done() and time.monotonic() < deadline:
                with contextlib.suppress(asyncio.CancelledError):
                    await asyncio.sleep(0.01)
            if not concurrent_future.done():
                executor.release_stalled_slot(concurrent_future)
                logging.getLogger("harness.runtime.audit_signing").error(
                    "%s worker outlived the %.0fs cancellation "
                    "join grace — detaching (daemon worker cannot hold "
                    "process exit); its write may land late",
                    what,
                    grace_seconds,
                )
        raise


async def run_audit_off_loop(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Run sync audit composition on the dedicated executor; join on cancel."""
    return await _run_off_loop_join_on_cancel(
        _AUDIT_OFFLOAD_EXECUTOR,
        AUDIT_CANCEL_JOIN_GRACE_SECONDS,
        "audit offload",
        fn,
        *args,
        **kwargs,
    )


async def run_pause_journal_off_loop(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Run the sync durable pause-journal capture off-loop; join on cancel (`B-103`).

    Its own pool, deliberately (out-of-family Codex [P1] round 1 on this arc):
    the wait here is a BLOCKING `fcntl.flock` on a peer process's append, and
    running that on the shared 4-worker audit pool would let four contended
    captures stall unrelated audit-signing and ref-resolution jobs. Runtime spec
    v1.102 §14.8.10.1 already ruled that pool ineligible for `B-48`'s offload on
    the same reasoning.

    **Join-on-cancel, and its BOUNDED residual, stated exactly.** A cancelled
    capture joins the worker so the append is durable BEFORE the cancellation is
    observed — the ordering the pre-`B-103` synchronous call had for free (the
    loop could not even deliver a cancellation while blocked in `flock`). That
    guarantee holds *up to* `PAUSE_JOURNAL_CANCEL_JOIN_GRACE_SECONDS`. Past it
    the worker is detached with a loud ERROR and its append MAY land after the
    caller observed cancellation — journaling a pause for an abandoned run.
    Registered at `B-105`, not silently absorbed. Severity is bounded by a
    property the substrate already documents: the journal writes no
    pause-resolved marker (`B-104`), so Runtime spec v1.108 §13.7 already scopes
    the enumeration to an UPPER BOUND that can over-report outstanding pauses —
    a late-landing record is within that documented imprecision, not a new
    corruption class.
    """
    return await _run_off_loop_join_on_cancel(
        _PAUSE_JOURNAL_OFFLOAD_EXECUTOR,
        PAUSE_JOURNAL_CANCEL_JOIN_GRACE_SECONDS,
        "pause-journal offload",
        fn,
        *args,
        **kwargs,
    )


async def run_off_loop_detach_on_cancel(
    fn: Callable[..., Any], /, *args: Any, **kwargs: Any
) -> Any:
    """Like `run_audit_off_loop` but does NOT join on cancellation (codex
    [P2] round 9 on the B-65-A arc).

    `run_audit_off_loop`'s bounded join-then-detach exists so an in-flight
    AUDIT write's durability is guaranteed before its caller observes
    cancellation — that grace (`AUDIT_CANCEL_JOIN_GRACE_SECONDS`, a fixed
    10s) is calibrated for that one caller profile. Reusing it for
    `shutdown()`'s opportunistic GC sweep (round-8 fix) made
    `shutdown(timeout=X)` able to overrun its OWN advertised deadline by up
    to that grace, because `asyncio.wait_for`'s cancellation had to wait
    for the inner join to finish before propagating. The sweep has no
    durability requirement of its own — an incomplete sweep just leaves
    stale entries for the NEXT opportunistic/bootstrap sweep to reap — so
    this variant cancels the concurrent future if it hasn't started yet,
    and otherwise detaches immediately: the worker keeps running on its
    daemon thread (harmless — daemon threads die with the process). The
    caller's OWN `asyncio.wait_for(..., timeout=...)` is the only bound
    that matters.

    **Releases the pool slot on detach (codex [P2] round 10).** A detach
    that never calls `release_stalled_slot` — as an earlier version of
    this function did not — leaves the stalled worker's slot permanently
    counted against the shared, only-4-workers-wide `_AUDIT_OFFLOAD_
    EXECUTOR`: since `shutdown()` runs per `api.run`/`resume` invocation,
    a handful of stalled sweeps across a long-lived process's lifetime
    could exhaust every worker and starve subsequent audit-signing/
    ref-resolution jobs entirely. `release_stalled_slot` is the SAME
    mechanism `run_audit_off_loop`'s own detach path already uses, and its
    `_serving`-membership check makes it safe even if the job happened to
    finish in the race window between this cancellation and the call.
    """
    context = contextvars.copy_context()
    call = functools.partial(context.run, functools.partial(fn, *args, **kwargs))
    concurrent_future = _AUDIT_OFFLOAD_EXECUTOR.submit(call)
    try:
        return await asyncio.wrap_future(concurrent_future)
    except asyncio.CancelledError:
        if not concurrent_future.cancel():
            _AUDIT_OFFLOAD_EXECUTOR.release_stalled_slot(concurrent_future)
        raise


async def resolve_result_ref_off_loop(
    store: ProtectedResultStore | None, tenant_id: str | None, result: object
) -> ResultRefValue:
    """Off-loop `resolve_result_ref` (B-65-A codex round-4 P1).

    `resolve_result_ref` calls into `write_once`, whose I/O (pickle + encrypt
    + fsync, plus an opportunistic decrypt-sweep) is exactly the class of
    work `asyncio.to_thread` must not carry — the loop's default executor is
    the same exhaustion-deadlock hazard `run_audit_off_loop` exists to avoid
    (see module docstring). `resolve_result_ref`/`write_once` never raise
    for any expected failure class (collision / serializer / encryption /
    durable-publication I/O) — they degrade to `UnresolvableResultRef`.
    Absent cancellation, the ONLY way this offload can raise is the
    executor's own queue-saturation guard (`_DaemonThreadAuditExecutor.
    submit` at `AUDIT_OFFLOAD_QUEUE_CAP`), which never runs
    `resolve_result_ref` at all — caught here and folded into the same
    discriminated-unresolvable contract.

    **Documented residual (codex [P1] round 9; advisor-reviewed, NOT
    fixed).** If the awaiting task is cancelled while the offloaded write
    is in flight (e.g. `SyncDispatcherFacade`'s `result_timeout_seconds`
    expiring exactly during post-effect ref-resolution), `run_audit_off_
    loop`'s `CancelledError` propagates straight through this wrapper — it
    is deliberately NOT caught here, since suppressing cancellation to
    force a return value would violate asyncio's cancellation contract
    (see `test_cancelled_ref_resolution_loses_carrier_but_write_lands_
    durably`). The raise-site's `PostEffectAuditSigningError` carrier is
    then never constructed and its `result_ref` is lost to that caller.
    This is ACCEPTABLE degradation, not data loss: `run_audit_off_loop`'s
    join-on-cancel still guarantees the write lands durably BEFORE the
    cancellation is observed, and every envelope carries its own
    `tenant_id` + `written_at` — the same fields `ProtectedResultStore.
    gc_sweep()` already decrypts and scans for TTL purposes — so an
    orphaned entry remains discoverable via a full-store enumerate-and-
    decrypt scan even without this carrier's pointer.
    """
    try:
        return await run_audit_off_loop(resolve_result_ref, store, tenant_id, result)
    except AuditSigningFailedError as exc:
        return UnresolvableResultRef(reason=f"result-ref offload saturated: {exc}")

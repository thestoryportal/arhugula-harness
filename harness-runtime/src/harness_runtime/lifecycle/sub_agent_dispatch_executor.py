"""Grow-on-demand sub-agent dispatch executor + shared frame budget — U-RT-141.

Implements Runtime spec v1.102 §14.8.10.1 (B-48, option B ratified 2026-07-18):
a CUSTOM grow-on-demand executor for offloaded sync `SUB_AGENT_DISPATCH`
inners, admission over the ONE shared frame budget
(`RuntimeConfig.sub_agent_dispatch_max_workers`, occupied+N+S accounting),
atomic reservation with LEASE semantics, fail-fast at the cap NEVER queue,
and lifecycle on its own terms (daemon workers; drain-with-deadline that
never blocks on loop-bridged workers).

Why not the existing pools (filing §2 ineligibility grounds):

- the 4-worker audit-offload executor (`audit_offload.py`) is queue-capped
  and sized for short signing jobs — a recursive sub-agent descent whose
  ancestors hold every worker deadlocks a fixed pool;
- the loop's default `ThreadPoolExecutor` is loop-owned and shared with
  `asyncio.to_thread` traffic — the same exhaustion hazard, plus shutdown
  coupling to loop close.

Grow-on-demand forecloses the recursive-offload deadlock: an ADMITTED job
always gets a worker immediately (idle reuse or a fresh daemon thread);
capacity is governed by FRAME admission, never worker count. A job that
cannot be admitted fails fast with the shared typed
`harness_core.SubAgentDispatchCapacityError` — no queueing in ANY variant
(a queued descendant whose parents hold every worker is the filing §2
recursive-offload deadlock).

The CP fan-out reaches this budget through `RuntimeCapacityAuthorityAdapter`
— the composition-root adapter implementing the CP-declared
`harness_cp.sub_agent_dispatch_capacity_authority.CapacityAuthority`
Protocol (U-CP-101; the ONE Runtime→CP edge, cycle-safe direction). The
adapter is bound into the frozen `HarnessContext` as `capacity_authority`
(C-RT-04 field-addition minor-bump path, `bare_llm_dispatcher` precedent)
so a configured cap reaches CP admission instead of the CP default-256
fallback.

Lease lifecycle (executor-owned): a job's frames are held until ACTUAL job
termination or fence-drain acknowledgement — a drained-under-fence or
abandoned worker keeps its frames until its fence acks; parent return never
releases. Release is EXACTLY-ONCE across success / failure / pause /
cancellation / timeout (the `CapacityLease` exactly-once guard).

Cross-bootstrap capacity-authority continuity — U-RT-146 (Runtime spec
v1.104 §14.8.10.6, RATIFIED B-59 fork option A). `FrameLedger` factors the
budget/available accounting OUT of `SubAgentDispatchExecutor` so it can
survive across sequential `api.run()` invocations within one process: stage 5
(`bootstrap/stage_5_loop_init.py`) adopts the process-lifetime ledger via
`adopt_or_create_process_capacity_ledger()` instead of always constructing a
fresh budget, while still constructing a FRESH `SubAgentDispatchExecutor`
(worker pool + `_draining` flag) every bootstrap bound to that ledger — the
executor object itself never crosses a bootstrap boundary (its `_draining`
flag is permanent once flipped; see `drain()`). The executor's admission
methods (`reserve`/`reserve_fanout`/`submit`/`begin_draining`) all acquire
`self._admission_lock`, which IS `ledger.lock` (the same object, never a
second separately-acquired lock) — this keeps the `_draining` check and the
ledger's capacity decision ONE atomic critical section across the split.
"""

from __future__ import annotations

import queue
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any, Final

from harness_core import SubAgentDispatchCapacityError
from harness_cp.sub_agent_dispatch_capacity_authority import (
    BranchAdmission,
    CapacityLease,
)

__all__ = [
    "DISPATCH_WORKER_THREAD_NAME_PREFIX",
    "CapacityAuthorityBudgetShrinkError",
    "FrameLedger",
    "RuntimeCapacityAuthorityAdapter",
    "SubAgentDispatchExecutor",
    "adopt_or_create_process_capacity_ledger",
    "reset_capacity_authority_for_tests",
]

DISPATCH_WORKER_THREAD_NAME_PREFIX: Final[str] = "harness-subagent-dispatch"

# Drain poll interval (seconds). Drain NEVER joins worker threads — a worker
# bridged into the event loop via `run_coroutine_threadsafe` would deadlock a
# thread-join from the loop thread; polling futures is join-free.
_DRAIN_POLL_SECONDS: Final[float] = 0.01

#: A queued job: the caller's future + the job callable. `None` is a
#: defensive stop-sentinel (never sent in production — workers are daemon
#: threads with lifecycle on the executor's own terms per §14.8.10.1; kept
#: as a safe `_worker` exit path, not load-bearing).
_WorkItem = tuple[Future[Any], Callable[[], Any]] | None


class CapacityAuthorityBudgetShrinkError(RuntimeError):
    """`RT-FAIL-CAPACITY-AUTHORITY-BUDGET-SHRINK` typed carrier (Runtime spec
    v1.104 §14.8.10.5) — raised at bootstrap adoption when the newly
    configured `sub_agent_dispatch_max_workers` would shrink the adopted
    process-lifetime `FrameLedger`'s budget below its CURRENT occupied
    count. Bootstrap-time-only (the budget is fixed once bootstrap
    completes); never a silent clamp or a silent over-cap.
    """

    rt_fail_class = "RT-FAIL-CAPACITY-AUTHORITY-BUDGET-SHRINK"

    __slots__ = ("configured_budget", "occupied_frames")

    def __init__(self, *, configured_budget: int, occupied_frames: int) -> None:
        self.configured_budget = configured_budget
        self.occupied_frames = occupied_frames
        super().__init__(
            f"RT-FAIL-CAPACITY-AUTHORITY-BUDGET-SHRINK: configured "
            f"sub_agent_dispatch_max_workers={configured_budget} is below the "
            f"process-lifetime capacity ledger's current occupied frame count "
            f"({occupied_frames}); shrink refused at bootstrap."
        )


class FrameLedger:
    """Process-lifetime frame-budget ledger — U-RT-146 (Runtime spec v1.104
    §14.8.10.6). Holds ONLY the budget/available accounting that survives
    across sequential `api.run()` bootstrap invocations within one process;
    the per-bootstrap `SubAgentDispatchExecutor` (worker pool + `_draining`
    flag) is rebuilt fresh every bootstrap and DELEGATES its admission
    decisions here through the SAME `lock` object it exposes — never a
    second, separately-acquired lock (that would reopen a window where
    `begin_draining()` flips between an admission's draining-check and its
    capacity decision).

    `budget`/`available` are RAW fields, not lock-guarded properties —
    every read/write site (in this module) holds `lock` explicitly around
    them as part of a larger combined critical section (e.g. the
    draining-check-plus-capacity-decision in `SubAgentDispatchExecutor.
    reserve`); a self-locking property would deadlock a caller that already
    holds this same non-reentrant `Lock`.
    """

    def __init__(self, *, frame_budget: int) -> None:
        if frame_budget < 1:
            msg = f"frame_budget must be >= 1, got {frame_budget}"
            raise ValueError(msg)
        self.lock = threading.Lock()
        self.budget = frame_budget
        self.available = frame_budget

    def reconcile_budget(self, new_budget: int) -> None:
        """Adopt-time reconciliation (AC #2) — atomic with any concurrent
        `reserve`/`release` under the SAME lock those calls use, never an
        unsynchronized read-then-write a straggler release could race.

        Growing the budget is honored immediately. Shrinking to AT OR ABOVE
        the current occupied count is honored immediately at the new,
        smaller budget. Shrinking BELOW the current occupied count is
        refused typed — bootstrap must not proceed with a negative or
        silently-clamped `available` count.
        """
        if new_budget < 1:
            msg = f"frame_budget must be >= 1, got {new_budget}"
            raise ValueError(msg)
        with self.lock:
            occupied = self.budget - self.available
            if new_budget < occupied:
                raise CapacityAuthorityBudgetShrinkError(
                    configured_budget=new_budget,
                    occupied_frames=occupied,
                )
            self.budget = new_budget
            self.available = new_budget - occupied


#: Process-lifetime capacity ledger holder (module-global; mirrors
#: `harness_runtime.drain._process_drained`'s shape — see that module for
#: the precedent this follows). `None` until the process's first bootstrap
#: adopts (constructs) it.
_process_capacity_ledger: FrameLedger | None = None


def adopt_or_create_process_capacity_ledger(frame_budget: int) -> FrameLedger:
    """Bootstrap-time adopt-or-construct (U-RT-146 AC #1/#2).

    On a process's FIRST bootstrap, constructs a fresh `FrameLedger` and
    adopts it as the process-lifetime authority. On every SUBSEQUENT
    bootstrap in the same process, ADOPTS the existing ledger instead of
    constructing a new one, reconciling its budget against the newly
    configured `frame_budget` (may raise `CapacityAuthorityBudgetShrinkError`
    per `FrameLedger.reconcile_budget`).
    """
    global _process_capacity_ledger
    if _process_capacity_ledger is None:
        _process_capacity_ledger = FrameLedger(frame_budget=frame_budget)
    else:
        _process_capacity_ledger.reconcile_budget(frame_budget)
    return _process_capacity_ledger


def reset_capacity_authority_for_tests() -> None:
    """Reset the module-level process-lifetime ledger — test-only escape
    hatch (see `harness_runtime.drain.reset_process_drained_for_tests` for
    the precedent this mirrors). Production callers must not invoke this;
    the function name encodes the contract.
    """
    global _process_capacity_ledger
    _process_capacity_ledger = None


class SubAgentDispatchExecutor:
    """Custom grow-on-demand executor over the ONE shared frame budget.

    Worker discipline (§14.8.10.1): a worker thread is created when no free
    worker exists; idle workers are reused; threads are named
    ``harness-subagent-dispatch-<n>``; all workers are daemon (lifecycle on
    the executor's own terms — never joined at interpreter exit).

    Frame discipline: `reserve`/`reserve_fanout` are the ADMISSION surface
    (atomic, fail-fast, never queue); `submit` runs an ALREADY-ADMITTED
    job — submission itself never blocks on capacity.
    """

    def __init__(
        self,
        *,
        frame_budget: int | None = None,
        ledger: FrameLedger | None = None,
    ) -> None:
        if ledger is None:
            if frame_budget is None:
                msg = "SubAgentDispatchExecutor requires frame_budget or ledger"
                raise ValueError(msg)
            ledger = FrameLedger(frame_budget=frame_budget)
        elif frame_budget is not None:
            msg = "frame_budget and ledger are mutually exclusive"
            raise ValueError(msg)
        self._ledger = ledger
        # IDENTICAL lock object as the ledger's — never a second,
        # separately-acquired lock (U-RT-146 AC #1c; the codex round-4
        # structural witness asserts `executor._admission_lock is
        # ledger.lock`). Guards BOTH the frame accounting (delegated to
        # `self._ledger`) and this executor's own per-bootstrap
        # `_draining`/`_idle_channels`/`_outstanding`/`_completed` state as
        # ONE combined critical section.
        self._admission_lock = ledger.lock
        # Per-worker hand-off channels (§14.8.10.1 "idle reuse" — B-48 codex
        # round-4: a SHARED queue lets any looped-back worker race for ANY
        # queued item, so "reuse worker X" was not actually a hand-off to X —
        # a freshly-spawned worker finishing its own (possibly instant) job
        # could loop back and steal a job a `submit()` call believed it had
        # handed to a SPECIFIC already-idle worker, silently serializing two
        # "concurrent" jobs onto one thread while another sits starved. A
        # channel is exclusive to exactly one worker: `submit()` atomically
        # pops one from `_idle_channels` under `_lock` (guaranteeing that
        # worker — and only that worker — receives this job), or spawns a
        # fresh worker and hands its job directly via thread args (bypassing
        # channels entirely, so a brand-new worker never contests a reuse
        # claim either).
        self._idle_channels: list[queue.SimpleQueue[_WorkItem]] = []
        self._spawned = 0
        self._completed = 0
        self._outstanding: set[Future[Any]] = set()
        # codex round-7 [P2] "stop workers that finish after the drain
        # snapshot" — see `drain()` + `_worker()` for the race this closes.
        self._draining = False

    # -- frame budget (the ONE shared budget; occupied+N+S accounting) --------

    @property
    def frame_budget(self) -> int:
        with self._admission_lock:
            return self._ledger.budget

    @property
    def available_frames(self) -> int:
        with self._admission_lock:
            return self._ledger.available

    @property
    def occupied_frames(self) -> int:
        """Frames held by admitted jobs — ancestors blocked on descendants AND
        concurrent workflows both count (admission is against AVAILABLE
        capacity, never the local fan-out alone)."""
        with self._admission_lock:
            return self._ledger.budget - self._ledger.available

    def _release_frames(self, frames: int) -> None:
        with self._admission_lock:
            self._ledger.available = min(self._ledger.budget, self._ledger.available + frames)

    def reserve(
        self,
        frames: int,
        *,
        step_id: str,
        descent_chain: tuple[str, ...],
    ) -> CapacityLease:
        """Atomic all-frames-or-fail-fast single-dispatch admission.

        At the cap the typed capacity error raises IMMEDIATELY — never queue
        (§14.8.10.1; the U-RT-140 taxonomy row RT-FAIL-SUB-AGENT-DISPATCH-
        CAPACITY maps to the raised `harness_core` type).

        Codex round-8 [P1] "reject new admissions after drain begins" — once
        `begin_draining()`/`drain()` has run, the executor is shutting down
        (later shutdown steps close the observability/provider clients any
        newly-admitted job's dispatch would need); admission must close
        atomically with that transition, not just the launch-time `submit()`
        gate below.
        """
        with self._admission_lock:
            if self._draining or frames > self._ledger.available:
                raise SubAgentDispatchCapacityError(
                    requested_frames=frames,
                    available_capacity=0 if self._draining else self._ledger.available,
                    step_id=step_id,
                    descent_chain=descent_chain,
                )
            self._ledger.available -= frames
        return CapacityLease(frames=frames, step_id=step_id, release_fn=self._release_frames)

    def reserve_fanout(
        self,
        branch_requirements: tuple[int, ...],
        *,
        step_ids: tuple[str, ...],
        descent_chain: tuple[str, ...],
    ) -> tuple[BranchAdmission, ...]:
        """Whole-fan-out ATOMIC admission (§14.8.10.1; CP spec v1.102 §1 row 3).

        One lock hold decides the entire fan-out: the input-order fitting
        prefix is acquired as per-branch leases; deterministic excess branches
        get per-branch rejections. Never incremental hold-and-wait (racing
        per-branch acquisition lets two fan-outs mutually degrade when either
        could have run whole); never partial-then-raise.

        Codex round-8 [P1] "reject new admissions after drain begins" — same
        rationale as `reserve()`; once draining, every branch is rejected
        (the existing deterministic-excess shape, starting from `admitting
        = False` instead of discovering the miss mid-scan).
        """
        if len(branch_requirements) != len(step_ids):
            msg = (
                "branch_requirements and step_ids must align: "
                f"{len(branch_requirements)} != {len(step_ids)}"
            )
            raise ValueError(msg)
        results: list[BranchAdmission] = []
        with self._admission_lock:
            remaining = self._ledger.available
            acquired = 0
            admitting = not self._draining
            for frames, step_id in zip(branch_requirements, step_ids, strict=True):
                if admitting and frames <= remaining:
                    remaining -= frames
                    acquired += frames
                    results.append(
                        CapacityLease(
                            frames=frames,
                            step_id=step_id,
                            release_fn=self._release_frames,
                        )
                    )
                else:
                    # Deterministic excess: input-order fitting prefix only —
                    # once one branch misses, every later branch is rejected
                    # too, even a smaller one that would individually fit.
                    admitting = False
                    results.append(
                        SubAgentDispatchCapacityError(
                            requested_frames=frames,
                            available_capacity=remaining,
                            step_id=step_id,
                            descent_chain=descent_chain,
                        )
                    )
            self._ledger.available -= acquired
        return tuple(results)

    # -- job submission (grow-on-demand workers) ------------------------------

    def submit(self, fn: Callable[[], Any], *, step_id: str = "<unknown-step>") -> Future[Any]:
        """Run an ALREADY-ADMITTED job on a worker; grow-on-demand, no queue wait.

        The caller holds the job's frame lease (admission happened at
        `reserve`/`reserve_fanout` or at the CP fan-out via the adapter);
        submission itself never blocks: an idle worker picks the job up
        immediately, or a fresh daemon worker is spawned for it.

        Reuse hands the job to a SPECIFIC popped-under-`_lock` channel —
        exclusive to exactly one worker — never a shared queue every worker
        polls (a shared queue lets a DIFFERENT worker that loops back first
        win the race to dequeue a job "reuse" believed was earmarked for a
        specific already-idle worker, silently serializing two "concurrent"
        submissions onto one thread while the intended worker starves; the
        recursive-offload deadlock hazard this executor exists to
        foreclose). A freshly-spawned worker's job is handed to it directly
        via thread constructor args, bypassing channels entirely too.

        Codex round-8 [P1] "reject new admissions after drain begins" — the
        caller may already hold a frame lease reserved BEFORE draining
        started (a legitimate race: shutdown can begin between an already-
        successful `reserve()`/`reserve_fanout()` and this call), but
        LAUNCHING the job past this point means running NEW work against an
        executor whose shutdown is already underway — including against
        provider/observability clients later shutdown steps may already
        have closed. Reject here too, symmetric with `reserve`/
        `reserve_fanout`; the caller's existing `except BaseException:
        release lease; raise` rollback (already required for the thread-
        start-failure path below) handles this identically.
        """
        future: Future[Any] = Future()
        with self._admission_lock:
            if self._draining:
                raise SubAgentDispatchCapacityError(
                    requested_frames=0,
                    available_capacity=0,
                    step_id=step_id,
                    descent_chain=(step_id,),
                )
            self._outstanding.add(future)
            channel = self._idle_channels.pop() if self._idle_channels else None
            if channel is None:
                self._spawned += 1
                worker_name = f"{DISPATCH_WORKER_THREAD_NAME_PREFIX}-{self._spawned}"
            else:
                worker_name = None
        if worker_name is not None:
            try:
                threading.Thread(
                    target=self._worker,
                    args=(future, fn),
                    daemon=True,
                    name=worker_name,
                ).start()
            except BaseException:
                # codex round-4 [P2] "roll back submission when worker
                # creation fails" — the OS refused a new thread (e.g.
                # `RuntimeError: can't start new thread`). `future` was
                # never returned to the caller, so nothing else will ever
                # call `_job_done` for it — without this rollback it stays
                # in `_outstanding` forever (`drain()` never reaches zero)
                # and `_spawned` over-counts a worker that never ran. Re-raise
                # so the caller's own admission/lease cleanup still fires
                # (exactly as it would for any other `submit()` exception).
                with self._admission_lock:
                    self._outstanding.discard(future)
                    self._spawned -= 1
                raise
        else:
            assert channel is not None
            channel.put((future, fn))
        return future

    def _worker(
        self,
        first_future: Future[Any],
        first_fn: Callable[[], Any],
    ) -> None:
        self._run_job(first_future, first_fn)
        my_channel: queue.SimpleQueue[_WorkItem] = queue.SimpleQueue()
        while True:
            # Register as idle-and-listening on OUR OWN channel BEFORE
            # blocking on it — a `submit()` racing in here can only ever pop
            # THIS channel (exclusive), so it's safe to publish first: any
            # job it pushes just waits in the channel's own buffer until we
            # reach `.get()` below.
            #
            # codex round-7 [P2] "stop workers that finish after the drain
            # snapshot" — `drain()` sweeps + sentinels `_idle_channels`
            # ONCE, under this SAME lock, and flips `_draining` under that
            # same hold. A worker finishing its job strictly AFTER that
            # sweep would otherwise re-register on a channel `drain()` will
            # never look at again, blocking forever on `.get()` (an
            # unbounded per-`run()`-call daemon-thread leak on a long-lived
            # server process). Checking `_draining` here, under the SAME
            # lock `drain()` uses for its own set-and-sweep, makes the two
            # sides strictly ordered — whichever runs first under the lock
            # is the one that's honored, so a late worker self-exits instead
            # of registering into a channel nothing will ever signal.
            with self._admission_lock:
                if self._draining:
                    return
                self._idle_channels.append(my_channel)
            item = my_channel.get()
            if item is None:
                return
            future, fn = item
            self._run_job(future, fn)

    def _run_job(self, future: Future[Any], fn: Callable[[], Any]) -> None:
        # Codex round-9 [P2] "complete futures before marking executor jobs
        # done" — publish the result/exception BEFORE `_job_done()` removes
        # this future from `_outstanding`. `Future.set_result`/
        # `set_exception` fire the future's done-callbacks (lease release,
        # the `asyncio.wrap_future` bridge) SYNCHRONOUSLY on this thread;
        # the old ordering removed the future from `_outstanding` first, so
        # `drain()`'s poll loop (`len(self._outstanding) == 0`) could
        # observe "fully drained" in the narrow window before those
        # callbacks had actually run. The `not future.set_running_or_notify_
        # cancel()` branch is unaffected — that path means the future was
        # ALREADY cancelled (and its own callbacks already fired) by
        # whoever called `.cancel()` on it, before this method ever ran.
        if not future.set_running_or_notify_cancel():
            self._job_done(future)
            return
        try:
            result = fn()
        except BaseException as exc:
            future.set_exception(exc)
            self._job_done(future)
        else:
            future.set_result(result)
            self._job_done(future)

    def _job_done(self, future: Future[Any]) -> None:
        with self._admission_lock:
            self._outstanding.discard(future)
            self._completed += 1

    # -- lifecycle on its own terms (§14.8.10.1) ------------------------------

    def begin_draining(self) -> None:
        """Synchronous, non-blocking: close the ENTIRE admission surface and
        stop currently-idle workers. Idempotent (safe to call more than
        once — a repeat call sees `_draining` already True and simply sweeps
        whatever is, or isn't, sitting in `_idle_channels`).

        Codex round-8 [P1] "reject new admissions after drain begins" +
        [P2] "enter draining state before scheduling the bounded wait":
        `drain()`'s own flag-flip (round-7 [P2]) only happened at the TAIL of
        its poll loop — reachable only if `drain()` itself got a chance to
        run. A caller that bounds drain scheduling in a zero/near-zero
        `asyncio.wait_for` budget can have the whole coroutine (including
        `drain()`'s body) cancelled before it ever starts, so `_draining`
        never flips and `reserve`/`reserve_fanout`/`submit` keep admitting +
        launching NEW work against an executor whose shutdown is already
        underway — including after later shutdown steps have closed the
        observability/provider clients that work would need. Splitting this
        out as a plain synchronous method lets the caller invoke it directly
        (no `await`, no scheduling delay, no timeout budget) BEFORE it even
        considers a bounded wait, so the admission surface always closes
        regardless of how much wall-clock budget remains.
        """
        with self._admission_lock:
            idle_channels = list(self._idle_channels)
            self._idle_channels.clear()
            self._draining = True
        for channel in idle_channels:
            channel.put(None)

    def drain(self, *, deadline_seconds: float) -> tuple[int, int]:
        """Drain-with-deadline at shutdown; NEVER blocks on loop-bridged workers.

        Polls outstanding futures (join-free) until done or deadline. Returns
        ``(completed_within_deadline, still_outstanding_at_deadline)`` — the
        first element is jobs whose done-callback actually fired during THIS
        drain call (a real completion count, not spawned-worker count: a
        single reused worker can complete many jobs, so `_spawned -
        still_outstanding` undercounts whenever idle-worker reuse happens).
        Abandoned (still-outstanding) workers are daemon threads — they
        cannot block interpreter exit, and their frame leases stay held
        until their fence acks (the lease discipline; never released by
        drain itself).

        Round-5b codex [P2] #4 "stop idle dispatch workers during shutdown":
        every currently-IDLE worker (nothing outstanding on it) gets the
        stop sentinel so its blocked channel `.get()` wakes and the thread
        exits, rather than blocking forever. Track A is bootstrap-per-`run()`
        call (no cached `HarnessContext`) — without this, a long-running
        server process accumulates one leaked, permanently-blocked daemon
        thread set per call that dispatched at least one sync sub-agent,
        unboundedly over the process's lifetime (daemon-ness only means the
        thread never blocks interpreter EXIT — it says nothing about
        accumulating for the remaining lifetime of a process that outlives
        any single `run()` call). Best-effort: a worker that finishes its
        OWN job strictly AFTER this method's outstanding-count snapshot
        races the stop sweep — it re-registers as idle and blocks again,
        exactly as before this fix (drain is a shutdown-time operation, not
        a live-traffic guarantee); the lease discipline above is unaffected
        either way.
        """
        self.begin_draining()
        deadline = time.monotonic() + deadline_seconds
        with self._admission_lock:
            completed_before = self._completed
        while time.monotonic() < deadline:
            with self._admission_lock:
                outstanding = len(self._outstanding)
            if outstanding == 0:
                break
            time.sleep(_DRAIN_POLL_SECONDS)
        with self._admission_lock:
            still_outstanding = len(self._outstanding)
            completed_during = self._completed - completed_before
        return (completed_during, still_outstanding)


class RuntimeCapacityAuthorityAdapter:
    """The composition-root adapter implementing CP's `CapacityAuthority`.

    Structurally satisfies
    `harness_cp.sub_agent_dispatch_capacity_authority.CapacityAuthority`
    (U-CP-101) over the REAL executor budget, so a configured
    `sub_agent_dispatch_max_workers` reaches CP fan-out admission instead of
    the CP default-256 fallback (U-RT-141 binding chain; the `HarnessContext.
    capacity_authority` C-RT-04 field carries it to the driver's structural
    `DriverContext` read).
    """

    __slots__ = ("_executor",)

    def __init__(self, executor: SubAgentDispatchExecutor) -> None:
        self._executor = executor

    def reserve(
        self,
        frames: int,
        *,
        step_id: str,
        descent_chain: tuple[str, ...],
    ) -> CapacityLease:
        return self._executor.reserve(frames, step_id=step_id, descent_chain=descent_chain)

    def reserve_fanout(
        self,
        branch_requirements: tuple[int, ...],
        *,
        step_ids: tuple[str, ...],
        descent_chain: tuple[str, ...],
    ) -> tuple[BranchAdmission, ...]:
        return self._executor.reserve_fanout(
            branch_requirements, step_ids=step_ids, descent_chain=descent_chain
        )

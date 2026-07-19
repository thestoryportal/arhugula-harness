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
    "RuntimeCapacityAuthorityAdapter",
    "SubAgentDispatchExecutor",
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

    def __init__(self, *, frame_budget: int) -> None:
        if frame_budget < 1:
            msg = f"frame_budget must be >= 1, got {frame_budget}"
            raise ValueError(msg)
        self._budget = frame_budget
        self._available = frame_budget
        self._lock = threading.Lock()
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
        return self._budget

    @property
    def available_frames(self) -> int:
        with self._lock:
            return self._available

    @property
    def occupied_frames(self) -> int:
        """Frames held by admitted jobs — ancestors blocked on descendants AND
        concurrent workflows both count (admission is against AVAILABLE
        capacity, never the local fan-out alone)."""
        with self._lock:
            return self._budget - self._available

    def _release_frames(self, frames: int) -> None:
        with self._lock:
            self._available = min(self._budget, self._available + frames)

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
        """
        with self._lock:
            if frames > self._available:
                raise SubAgentDispatchCapacityError(
                    requested_frames=frames,
                    available_capacity=self._available,
                    step_id=step_id,
                    descent_chain=descent_chain,
                )
            self._available -= frames
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
        """
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
            admitting = True
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
            self._available -= acquired
        return tuple(results)

    # -- job submission (grow-on-demand workers) ------------------------------

    def submit(self, fn: Callable[[], Any]) -> Future[Any]:
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
        """
        future: Future[Any] = Future()
        with self._lock:
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
                with self._lock:
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
            with self._lock:
                if self._draining:
                    return
                self._idle_channels.append(my_channel)
            item = my_channel.get()
            if item is None:
                return
            future, fn = item
            self._run_job(future, fn)

    def _run_job(self, future: Future[Any], fn: Callable[[], Any]) -> None:
        if not future.set_running_or_notify_cancel():
            self._job_done(future)
            return
        try:
            result = fn()
        except BaseException as exc:
            self._job_done(future)
            future.set_exception(exc)
        else:
            self._job_done(future)
            future.set_result(result)

    def _job_done(self, future: Future[Any]) -> None:
        with self._lock:
            self._outstanding.discard(future)
            self._completed += 1

    # -- lifecycle on its own terms (§14.8.10.1) ------------------------------

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
        deadline = time.monotonic() + deadline_seconds
        with self._lock:
            completed_before = self._completed
        while time.monotonic() < deadline:
            with self._lock:
                outstanding = len(self._outstanding)
            if outstanding == 0:
                break
            time.sleep(_DRAIN_POLL_SECONDS)
        with self._lock:
            still_outstanding = len(self._outstanding)
            completed_during = self._completed - completed_before
            idle_channels = list(self._idle_channels)
            self._idle_channels.clear()
            # codex round-7 [P2] — flip under the SAME lock hold as the
            # sweep above, closing the race with `_worker()`'s own
            # check-then-append (also lock-held): a worker that hasn't
            # registered yet when this runs sees `_draining=True` on its
            # next re-registration attempt and self-exits instead; a worker
            # already registered here got its sentinel in this sweep.
            self._draining = True
        for channel in idle_channels:
            channel.put(None)
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

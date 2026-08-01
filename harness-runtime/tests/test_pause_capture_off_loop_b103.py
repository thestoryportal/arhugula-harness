"""`B-103` — the pause journal's blocking `flock` runs OFF the event loop.

The register's close_out (`.harness/forward-register.yaml`, `B-103`) names the
defect: ``DurablePauseResumeProtocol.capture_pause_snapshot`` is an ``async def``
that called the SYNCHRONOUS ``JournalWorkflowPauseStore.capture()`` inline, and
that call's ``_append`` takes ``cross_process_journal_lock`` — a blocking
``fcntl.flock(fd, LOCK_EX)``. While a second OS process held that lock, the
acquisition blocked the loop THREAD: no other coroutine ran and no pending timer
fired until the holder released.

**The witness is by EXECUTION, and it is a DERIVED MATRIX.** The close_out names
the mutation probe as *"the direct synchronous call, under which that witness
must fail"*. Rather than record a one-time manual probe in prose, both arms ship:
every liveness/cancellation witness below is parametrized over the SHIPPED path
and a mutant that reproduces the pre-`B-103` shape, with OPPOSITE expectations.
The probe is therefore re-run by CI on every commit and cannot silently rot into
a green-either-way assertion (`[[mutation-probe-load-bearing-witness]]`).

**What is NOT changed, pinned here because the close_out forbids changing it.**

1. **Lock GRANULARITY** — still one per-workflow lock, same construction, same
   inode. Witnessed at `test_the_off_loop_capture_locks_exactly_the_same_target`,
   and by the whole of `test_journal_pause_store_cross_process_append_b97.py`
   staying green untouched.
2. **The READ path** — still takes no lock and is still SYNCHRONOUS. Witnessed at
   `test_the_read_path_is_untouched_by_the_offload`. That property is what keeps
   Runtime spec v1.107 §30's ``empty-journal`` INDETERMINATE clause exact as
   written, and therefore why this arc — like `B-97`(b) before it — owes no spec
   text.

**Spec posture (confirmed before building, per the close_out's instruction).**
Runtime spec v1.108 §14.8.1's v1.102 paragraph states the governing principle
verbatim: *"The wrap chain above pins composition, not execution venue"*, and
selects an off-loop venue for a blocking sync inner without altering any
contract surface. This arc is the same class — venue only. No contract term, no
config scalar, no failure class, no record shape and no observable surface moves.
No fork is owed.
"""

from __future__ import annotations

import asyncio
import inspect
import subprocess
import sys
import time
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle import audit_offload
from harness_runtime.lifecycle.audit_offload import run_off_loop_detach_on_cancel
from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_LOCK_SUFFIX,
    JournalWorkflowPauseStore,
    pause_journal_filename,
)

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32",
    reason="`cross_process_journal_lock` deliberately no-ops on Windows (no fcntl; the "
    "B-45 register row), so nothing blocks and the loop-starvation contrast this module "
    "measures does not exist there.",
)

_WORKFLOW_ID = "wf-b103-off-loop"
_ANCHOR = "0" * 64

_READY_TIMEOUT = 30.0
"""A cold child interpreter's own import of `harness_runtime` costs seconds here."""

_HOLD_SECONDS = 3.0
"""How long the second OS process holds the journal lock.

SELF-releasing on a timer inside the child, NOT on a marker written by the
parent — under the MUTANT arm the parent's loop thread is precisely what is
blocked, so it could never write a release marker and the test would deadlock
rather than fail. Every arm terminates on the child's own clock.
"""

_OBSERVE_AFTER = 0.6
"""When the parent samples loop liveness, measured from the child's lock-held signal."""

_LIVE_BOUND = 1.5
"""The discriminator, sitting between `_OBSERVE_AFTER` and `_HOLD_SECONDS`.

A LIVE loop delivers its due callbacks at their due time (~`_OBSERVE_AFTER` and
~`_TIMER_DELAY`), comfortably under this. A loop BLOCKED in `flock` delivers
every overdue callback only when the child releases (~`_HOLD_SECONDS`),
comfortably over it. The gap is 2.5x on both sides — this is a starvation
witness, not a wall-clock race.
"""

_TICK = 0.02
_TIMER_DELAY = 0.15


# --------------------------------------------------------------------------
# Substrate
# --------------------------------------------------------------------------


_CHILD_HOLD_LOCK_SCRIPT = """
import sys, time
from pathlib import Path
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore, cross_process_journal_lock,
)

journal_dir, workflow_id, held_marker, hold_seconds = sys.argv[1:5]
store = JournalWorkflowPauseStore(journal_dir=Path(journal_dir), tenant_id=None)
Path(journal_dir).mkdir(parents=True, exist_ok=True)
# The MODULE-LEVEL lock the store itself delegates to — the same lock, of the
# same construction, on the same inode (`B-97`(a) promotion).
with cross_process_journal_lock(store._journal_file(workflow_id)):
    Path(held_marker).write_text("held")
    time.sleep(float(hold_seconds))
"""


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _store(journal_dir: Path) -> JournalWorkflowPauseStore:
    return JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)


def _journal_file(journal_dir: Path) -> Path:
    return journal_dir / pause_journal_filename(None, _WORKFLOW_ID)


def _lock_file(journal_dir: Path) -> Path:
    journal = _journal_file(journal_dir)
    return journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX)


class _PreB103Protocol(DurablePauseResumeProtocol):
    """THE MUTATION: the pre-`B-103` shape — `capture()` called inline, on the loop.

    Reproduced as a subclass rather than by editing the shipped method, so the
    probe is permanent. It keeps its OWN store reference (rather than reaching
    into the parent's) so nothing here depends on a private attribute.
    """

    def __init__(self, *, store: JournalWorkflowPauseStore, **kwargs: Any) -> None:
        super().__init__(store=store, **kwargs)
        self._direct_store = store

    async def capture_pause_snapshot(  # type: ignore[override]
        self,
        workflow_id: str,
        run_id: str,
        step_index: int,
        pause_reason: WorkflowPauseReason,
        **carriers: Any,
    ) -> PauseSnapshot:
        snapshot = await PauseResumeProtocol.capture_pause_snapshot(
            self, workflow_id, run_id, step_index, pause_reason, **carriers
        )
        self._direct_store.capture(snapshot)
        return snapshot


class _DetachOnCancelProtocol(DurablePauseResumeProtocol):
    """THE CANCELLATION MUTATION: off-loop, but DETACHING instead of joining.

    The alternative primitive considered and rejected at this arc. Off-loop
    enough to keep the loop live — so it passes every liveness witness — but it
    lets the append land AFTER the caller observes cancellation. That difference
    is what `test_a_cancelled_capture_is_durable_before_cancellation_is_observed`
    discriminates.
    """

    def __init__(self, *, store: JournalWorkflowPauseStore, **kwargs: Any) -> None:
        super().__init__(store=store, **kwargs)
        self._direct_store = store

    async def capture_pause_snapshot(  # type: ignore[override]
        self,
        workflow_id: str,
        run_id: str,
        step_index: int,
        pause_reason: WorkflowPauseReason,
        **carriers: Any,
    ) -> PauseSnapshot:
        snapshot = await PauseResumeProtocol.capture_pause_snapshot(
            self, workflow_id, run_id, step_index, pause_reason, **carriers
        )
        await run_off_loop_detach_on_cancel(self._direct_store.capture, snapshot)
        return snapshot


def _protocol(
    journal_dir: Path, factory: type[DurablePauseResumeProtocol] = DurablePauseResumeProtocol
) -> DurablePauseResumeProtocol:
    return factory(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_summary(), _ANCHOR),
        store=_store(journal_dir),
    )


def _await_marker(marker: Path, *, what: str, timeout: float = _READY_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout
    while not marker.exists():
        assert time.monotonic() < deadline, f"{what} never appeared"
        time.sleep(0.02)


@contextmanager
def _second_process_holding_the_lock(
    journal_dir: Path, *, hold_seconds: float = _HOLD_SECONDS
) -> Generator[None]:
    """A GENUINE second OS process holding this workflow's journal lock.

    `subprocess`, never `multiprocessing`: `fork` after a lock is held is the
    documented workspace deadlock hazard, and `spawn`'s pickle-by-module-name
    resolution is ambiguous across this monorepo's several same-named `tests`
    packages. A thread would prove nothing — `flock` exclusion is per-open-file-
    description and kernel-side.
    """
    held = journal_dir.parent / "child_held"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-c",
            _CHILD_HOLD_LOCK_SCRIPT,
            str(journal_dir),
            _WORKFLOW_ID,
            str(held),
            str(hold_seconds),
        ]
    )
    try:
        _await_marker(held, what="the child's lock-held signal")
        yield
    finally:
        if proc.poll() is None:
            proc.wait(timeout=_READY_TIMEOUT)


@dataclass(frozen=True)
class _Liveness:
    """What the loop managed to do while the capture was blocked."""

    sample_latency: float
    """How long a `sleep(_OBSERVE_AFTER)` on the MAIN coroutine actually took."""

    timer_latency: float
    """How long a `loop.call_later(_TIMER_DELAY, ...)` callback actually took to fire."""

    ticks: int
    """How many iterations an UNRELATED concurrent coroutine completed."""

    capture_pending_at_sample: bool
    """Whether the capture was still blocked when sampled — without this, a fast
    capture (no contention) would satisfy every liveness assertion vacuously."""


async def _sample_loop_liveness(protocol: DurablePauseResumeProtocol, run_id: str) -> _Liveness:
    loop = asyncio.get_running_loop()
    ticks = 0
    stop = asyncio.Event()

    async def _unrelated_workflow() -> None:
        nonlocal ticks
        while not stop.is_set():
            await asyncio.sleep(_TICK)
            ticks += 1

    fired_at: list[float] = []
    started = time.monotonic()
    loop.call_later(_TIMER_DELAY, lambda: fired_at.append(time.monotonic()))
    ticker = asyncio.create_task(_unrelated_workflow())
    await asyncio.sleep(0)  # let the unrelated coroutine reach its first await

    capture = asyncio.create_task(
        protocol.capture_pause_snapshot(_WORKFLOW_ID, run_id, 0, WorkflowPauseReason.HITL_PENDING)
    )
    sample_started = time.monotonic()
    await asyncio.sleep(_OBSERVE_AFTER)
    observed = _Liveness(
        sample_latency=time.monotonic() - sample_started,
        timer_latency=(fired_at[0] - started) if fired_at else float("inf"),
        ticks=ticks,
        capture_pending_at_sample=not capture.done(),
    )

    stop.set()
    await ticker
    await capture  # completes once the child releases; never left dangling
    return observed


# --------------------------------------------------------------------------
# W1 — loop liveness under a held journal lock (THE close_out witness)
# --------------------------------------------------------------------------


@requires_posix_flock
@pytest.mark.parametrize(
    ("factory", "off_loop"),
    [
        pytest.param(DurablePauseResumeProtocol, True, id="shipped-off-loop"),
        pytest.param(_PreB103Protocol, False, id="mutant-direct-synchronous-call"),
    ],
)
async def test_the_loop_stays_live_while_a_second_process_holds_the_journal_lock(
    tmp_path: Path, factory: type[DurablePauseResumeProtocol], off_loop: bool
) -> None:
    """THE witness the `B-103` close_out specifies, plus its mutation probe.

    A genuinely separate OS process holds workflow `W`'s journal lock. This
    process captures a pause for `W` through the durable protocol. While that
    capture is blocked on the lock:

    - an UNRELATED concurrent coroutine must keep advancing, and
    - a PENDING loop timer must fire at its due time.

    Under the shipped off-loop path both hold. Under the mutant — the direct
    synchronous call, exactly the pre-`B-103` shape — the loop thread is inside
    `flock` and NEITHER holds: every overdue callback is delivered only when the
    child releases. The `capture_pending_at_sample` assertion is what stops the
    off-loop arm from passing vacuously on a capture that never contended.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    protocol = _protocol(journal_dir, factory)

    with _second_process_holding_the_lock(journal_dir):
        observed = await _sample_loop_liveness(protocol, run_id="run-liveness")

    if off_loop:
        # Non-vacuity guard, and it belongs to THIS arm only. Off-loop, the
        # sampler runs on time and must find the capture still blocked — without
        # this, a run where the child never held the lock would satisfy every
        # liveness assertion below while witnessing nothing. In the mutant arm
        # the same check is meaningless BY CONSTRUCTION: the loop is frozen
        # inside `flock`, so by the time it can run the sampler at all the
        # release has already happened and the capture has already finished.
        # Its non-vacuity guard is the starvation itself — a sample latency of
        # ~`_HOLD_SECONDS` cannot occur unless the child really held the lock.
        assert observed.capture_pending_at_sample, (
            "the capture completed before the sample — the child was not holding "
            "the lock and this run witnessed nothing"
        )
        assert observed.sample_latency < _LIVE_BOUND, (
            f"the main coroutine's sleep took {observed.sample_latency:.2f}s — the "
            "loop thread was blocked in the journal's flock"
        )
        assert observed.timer_latency < _LIVE_BOUND, (
            f"a pending loop timer fired {observed.timer_latency:.2f}s late — the "
            "loop thread was blocked in the journal's flock"
        )
        assert observed.ticks >= 5, (
            f"an unrelated concurrent coroutine advanced only {observed.ticks} times "
            f"in {_OBSERVE_AFTER}s — the loop was starved"
        )
    else:
        assert observed.sample_latency >= _LIVE_BOUND, (
            "MUTATION PROBE FAILED TO REPRODUCE: the direct synchronous call did not "
            "starve the loop, so the off-loop arm above proves nothing"
        )
        assert observed.timer_latency >= _LIVE_BOUND, (
            "MUTATION PROBE FAILED TO REPRODUCE: a pending timer fired on time despite "
            "the inline blocking flock"
        )
        assert observed.ticks <= 3, (
            f"MUTATION PROBE FAILED TO REPRODUCE: an unrelated coroutine advanced "
            f"{observed.ticks} times while the loop was supposedly blocked"
        )


@requires_posix_flock
async def test_the_blocked_capture_still_lands_the_record_once_the_lock_is_released(
    tmp_path: Path,
) -> None:
    """Liveness must not have been bought by dropping the write.

    The off-loop capture is not fire-and-forget: it is awaited, so by the time
    `capture_pause_snapshot` returns the snapshot is durable — the property this
    method's docstring has always promised (*"journaled BEFORE it is returned"*).
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    protocol = _protocol(journal_dir)

    with _second_process_holding_the_lock(journal_dir):
        returned = await protocol.capture_pause_snapshot(
            _WORKFLOW_ID, "run-durable", 0, WorkflowPauseReason.HITL_PENDING
        )

    read = _store(journal_dir).read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None
    assert read.snapshot.run_id == "run-durable"
    assert read.snapshot.snapshot_hash == returned.snapshot_hash


# --------------------------------------------------------------------------
# W2 — cancellation semantics of the chosen primitive
# --------------------------------------------------------------------------


@requires_posix_flock
@pytest.mark.parametrize(
    ("factory", "joins"),
    [
        pytest.param(DurablePauseResumeProtocol, True, id="shipped-join-on-cancel"),
        pytest.param(_DetachOnCancelProtocol, False, id="mutant-detach-on-cancel"),
    ],
)
async def test_a_cancelled_capture_is_durable_before_cancellation_is_observed(
    tmp_path: Path, factory: type[DurablePauseResumeProtocol], joins: bool
) -> None:
    """Why `run_audit_off_loop` (join) and not `run_off_loop_detach_on_cancel`.

    A capture cancelled while blocked on the journal lock cannot be interrupted —
    `flock` is uninterruptible from the loop side either way. The question is only
    whether the append is durable BEFORE the caller observes the cancellation, or
    lands afterwards.

    - **Shipped (join):** the record is on disk at the moment `CancelledError` is
      observed — up to `PAUSE_JOURNAL_CANCEL_JOIN_GRACE_SECONDS`. This test's
      hold is deliberately well inside that grace; the past-grace detach is a
      REGISTERED residual (`B-105`), not a claimed guarantee, and the detach
      mechanism itself is already witnessed at `test_lifecycle_audit_offload.py`
      against the shared body both pools now use.
    - **Mutant (detach):** `CancelledError` is observed immediately and the record
      is NOT yet on disk — it lands later, from a worker the caller has stopped
      tracking. That is a pause journaled after the run stopped reporting it, which
      `api.resume` would then honour.

    Both arms assert the record ULTIMATELY lands, so this discriminates ordering,
    not loss.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    protocol = _protocol(journal_dir, factory)
    store = _store(journal_dir)

    with _second_process_holding_the_lock(journal_dir):
        capture = asyncio.create_task(
            protocol.capture_pause_snapshot(
                _WORKFLOW_ID, "run-cancelled", 0, WorkflowPauseReason.HITL_PENDING
            )
        )
        await asyncio.sleep(_OBSERVE_AFTER)  # let it reach the blocking acquisition
        assert not capture.done(), "the capture never blocked — nothing to cancel"

        capture.cancel()
        with pytest.raises(asyncio.CancelledError):
            await capture

        landed_at_observation = store.read_latest(_WORKFLOW_ID) is not None

    assert landed_at_observation is joins, (
        "join-on-cancel must make the record durable BEFORE the cancellation is "
        "observed; detach-on-cancel must not — if both behave alike, the primitive "
        "choice documented at capture_pause_snapshot is unwitnessed"
    )

    deadline = time.monotonic() + _READY_TIMEOUT
    while store.read_latest(_WORKFLOW_ID) is None:
        assert time.monotonic() < deadline, "the cancelled capture's record never landed"
        await asyncio.sleep(0.05)
    assert store.read_latest(_WORKFLOW_ID).run_id == "run-cancelled"  # type: ignore[union-attr]


# --------------------------------------------------------------------------
# W3 — the two things `B-103` forbids changing
# --------------------------------------------------------------------------


@requires_posix_flock
async def test_the_off_loop_capture_locks_exactly_the_same_target(tmp_path: Path) -> None:
    """GRANULARITY is untouched: one lock, this workflow's journal, same inode.

    The close_out forbids changing the lock's granularity (settled at `B-97`(b)
    against a directory-tree alternative). The offload moves the VENUE of the
    acquisition and nothing else — so the acquisition recorded here must be the
    same single per-workflow target the synchronous path took, and the lock file
    on disk must be the one derived from the tenant-composite key.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    acquired: list[Path] = []
    real: Callable[..., Any] = JournalWorkflowPauseStore._cross_process_append_lock  # pyright: ignore[reportPrivateUsage]

    @contextmanager
    def _recording(self: JournalWorkflowPauseStore, journal_path: Path) -> Generator[None]:
        acquired.append(journal_path)
        with real(self, journal_path):
            yield

    protocol = _protocol(journal_dir)
    JournalWorkflowPauseStore._cross_process_append_lock = _recording  # type: ignore[method-assign]
    try:
        await protocol.capture_pause_snapshot(
            _WORKFLOW_ID, "run-granularity", 0, WorkflowPauseReason.HITL_PENDING
        )
    finally:
        JournalWorkflowPauseStore._cross_process_append_lock = real  # type: ignore[method-assign]

    assert acquired == [_journal_file(journal_dir)], (
        "the off-loop write must lock THIS workflow's journal, exactly once — a "
        "changed granularity would show up here as a different or extra target"
    )
    assert _lock_file(journal_dir).exists()


async def test_the_read_path_is_untouched_by_the_offload(tmp_path: Path) -> None:
    """The READ path takes no lock and is still SYNCHRONOUS.

    The close_out forbids changing it, because its no-lock property is what keeps
    Runtime spec v1.107 §30's `empty-journal` INDETERMINATE clause exact as
    written. The store's own surface is unchanged too — `capture()` stays sync;
    only its ONE async caller changed where it runs it.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    acquired: list[Path] = []
    real: Callable[..., Any] = JournalWorkflowPauseStore._cross_process_append_lock  # pyright: ignore[reportPrivateUsage]

    @contextmanager
    def _recording(self: JournalWorkflowPauseStore, journal_path: Path) -> Generator[None]:
        acquired.append(journal_path)
        with real(self, journal_path):
            yield

    protocol = _protocol(journal_dir)
    store = _store(journal_dir)
    JournalWorkflowPauseStore._cross_process_append_lock = _recording  # type: ignore[method-assign]
    try:
        await protocol.capture_pause_snapshot(
            _WORKFLOW_ID, "run-read", 0, WorkflowPauseReason.HITL_PENDING
        )
        acquired.clear()
        assert store.read_latest_attributed(_WORKFLOW_ID).snapshot is not None
        assert store.read_latest(_WORKFLOW_ID) is not None
    finally:
        JournalWorkflowPauseStore._cross_process_append_lock = real  # type: ignore[method-assign]

    assert acquired == [], "the read path acquired the write lock"
    for name in ("read_latest", "read_latest_attributed", "capture"):
        member = getattr(JournalWorkflowPauseStore, name)
        assert not inspect.iscoroutinefunction(member), (
            f"JournalWorkflowPauseStore.{name} became async — the offload belongs at "
            "the ONE async caller, not on the store's surface"
        )


@requires_posix_flock
async def test_a_read_still_completes_while_the_off_loop_capture_is_blocked(
    tmp_path: Path,
) -> None:
    """The liveness half of the same decision, end to end through the async path.

    A second OS process holds the lock, this process's off-loop capture is blocked
    on it, and a read STILL returns promptly — the write lock excludes writers, and
    only writers.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    protocol = _protocol(journal_dir)
    store = _store(journal_dir)
    await protocol.capture_pause_snapshot(
        _WORKFLOW_ID, "run-before-hold", 0, WorkflowPauseReason.HITL_PENDING
    )

    with _second_process_holding_the_lock(journal_dir):
        blocked = asyncio.create_task(
            protocol.capture_pause_snapshot(
                _WORKFLOW_ID, "run-blocked", 0, WorkflowPauseReason.HITL_PENDING
            )
        )
        await asyncio.sleep(_OBSERVE_AFTER)
        assert not blocked.done(), "the capture never blocked — nothing to witness"

        started = time.monotonic()
        read = store.read_latest_attributed(_WORKFLOW_ID)
        elapsed = time.monotonic() - started
        assert read.snapshot is not None and read.snapshot.run_id == "run-before-hold"
        assert elapsed < _LIVE_BOUND, (
            f"the read blocked for {elapsed:.2f}s while a writer held the lock — it "
            "must not take that lock"
        )
        await blocked


# --------------------------------------------------------------------------
# W4 — the offload venue itself
# --------------------------------------------------------------------------


async def test_the_capture_is_dispatched_to_the_dedicated_offload_pool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The capture leaves the loop thread, and NOT via the loop's default executor.

    `asyncio.to_thread` was rejected: the CP driver's sync `execute_workflow`
    already runs in the default executor while awaiting loop coroutines, so a
    capture queued there could wait behind the very drivers waiting on it
    (`audit_offload`'s module docstring — the documented exhaustion deadlock).
    Both halves are asserted: a DIFFERENT thread ran the append, and the default
    executor was never asked to.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    default_executor_calls: list[object] = []
    real_to_thread = asyncio.to_thread

    async def _tracking_to_thread(func: Callable[..., Any], /, *a: Any, **kw: Any) -> Any:
        default_executor_calls.append(func)
        return await real_to_thread(func, *a, **kw)

    monkeypatch.setattr(asyncio, "to_thread", _tracking_to_thread)

    append_threads: list[str] = []
    real_capture = JournalWorkflowPauseStore.capture

    def _recording(self: JournalWorkflowPauseStore, snapshot: PauseSnapshot) -> None:
        import threading

        append_threads.append(threading.current_thread().name)
        real_capture(self, snapshot)

    monkeypatch.setattr(JournalWorkflowPauseStore, "capture", _recording)

    import threading

    loop_thread = threading.current_thread().name
    await _protocol(journal_dir).capture_pause_snapshot(
        _WORKFLOW_ID, "run-venue", 0, WorkflowPauseReason.HITL_PENDING
    )

    assert append_threads and append_threads[0] != loop_thread, (
        "the journal append ran on the loop thread — it was not offloaded at all"
    )
    assert default_executor_calls == [], (
        "the capture was dispatched through `asyncio.to_thread` (the loop's DEFAULT "
        "executor) — the exhaustion-deadlock hazard this offload avoids"
    )


async def test_the_capture_never_occupies_the_shared_audit_pool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pool ISOLATION — the fix for out-of-family Codex [P1] round 1 on this arc.

    A journal-lock wait does not fit the audit pool's "short-lived, one sign +
    local writes" profile: four contended captures there would occupy every one
    of `AUDIT_OFFLOAD_MAX_WORKERS` and stall unrelated audit-signing and
    ref-resolution jobs, which then fail once the shared queue saturates.
    Runtime spec v1.102 §14.8.10.1 already ruled that same 4-worker pool
    INELIGIBLE for `B-48`'s offload on identical reasoning.

    Asserted as an EXCLUSION, not just a presence: the pause pool is submitted
    to, and the audit pool is not touched at all. A presence-only assertion
    would still pass if the capture were submitted to both.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    audit_submits: list[object] = []
    pause_submits: list[object] = []
    real_audit = audit_offload._AUDIT_OFFLOAD_EXECUTOR.submit  # pyright: ignore[reportPrivateUsage]
    real_pause = audit_offload._PAUSE_JOURNAL_OFFLOAD_EXECUTOR.submit  # pyright: ignore[reportPrivateUsage]

    def _rec_audit(fn: Callable[[], Any]) -> Any:
        audit_submits.append(fn)
        return real_audit(fn)

    def _rec_pause(fn: Callable[[], Any]) -> Any:
        pause_submits.append(fn)
        return real_pause(fn)

    monkeypatch.setattr(
        audit_offload._AUDIT_OFFLOAD_EXECUTOR,  # pyright: ignore[reportPrivateUsage]
        "submit",
        _rec_audit,
    )
    monkeypatch.setattr(
        audit_offload._PAUSE_JOURNAL_OFFLOAD_EXECUTOR,  # pyright: ignore[reportPrivateUsage]
        "submit",
        _rec_pause,
    )

    await _protocol(journal_dir).capture_pause_snapshot(
        _WORKFLOW_ID, "run-pool", 0, WorkflowPauseReason.HITL_PENDING
    )

    assert len(pause_submits) == 1, "the capture did not go to the pause-journal pool"
    assert audit_submits == [], (
        "the capture occupied a slot on the SHARED audit pool — a contended "
        "journal lock could then stall unrelated audit-signing work"
    )
    assert (
        audit_offload._PAUSE_JOURNAL_OFFLOAD_EXECUTOR  # pyright: ignore[reportPrivateUsage]
        is not audit_offload._AUDIT_OFFLOAD_EXECUTOR  # pyright: ignore[reportPrivateUsage]
    )


async def test_capture_returns_the_composed_snapshot_unchanged(tmp_path: Path) -> None:
    """The offload is a venue change only — the returned object is the parent's.

    Every carrier the CP parent composes must survive the round trip; an offload
    that returned a re-read or re-validated snapshot would be a silent semantic
    change on a path whose identity (`snapshot_hash`) is load-bearing.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    returned = await _protocol(journal_dir).capture_pause_snapshot(
        _WORKFLOW_ID, "run-identity", 3, WorkflowPauseReason.HITL_PENDING
    )
    assert returned.workflow_id == _WORKFLOW_ID
    assert returned.run_id == "run-identity"
    assert returned.step_index == 3
    assert returned.pause_reason is WorkflowPauseReason.HITL_PENDING
    assert returned.state_ledger_anchor == _ANCHOR

    journaled = _store(journal_dir).read_latest(_WORKFLOW_ID)
    assert journaled is not None
    assert journaled.snapshot_hash == returned.snapshot_hash


async def test_repeated_captures_do_not_leak_the_offload_pool(tmp_path: Path) -> None:
    """A capture per pause, over the pool's whole width, keeps working.

    `run_audit_off_loop` runs on a shared 4-worker pool. A capture that failed to
    release its slot would starve audit signing after a handful of pauses — this
    drives more captures than the pool is wide and asserts every record landed.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    protocol = _protocol(journal_dir)

    captures: Sequence[PauseSnapshot] = await asyncio.gather(
        *(
            protocol.capture_pause_snapshot(
                _WORKFLOW_ID, f"run-{i}", i, WorkflowPauseReason.HITL_PENDING
            )
            for i in range(12)
        )
    )
    assert len(captures) == 12

    lines = _journal_file(journal_dir).read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 12, "a concurrent capture was lost or duplicated under the lock"
    assert _store(journal_dir).read_latest(_WORKFLOW_ID) is not None

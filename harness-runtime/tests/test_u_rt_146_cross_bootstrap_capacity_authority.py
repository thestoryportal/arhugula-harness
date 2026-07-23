"""U-RT-146 — cross-bootstrap capacity-authority continuity tests.

Tests per Implementation_Plan_Harness_Runtime_v2_52.md §1.1 (PD-8
mutation-probed): the process-lifetime `FrameLedger` is adopted across
sequential `api.run()` bootstraps within one process while the per-bootstrap
`SubAgentDispatchExecutor` (worker pool + `_draining` flag) is always
rebuilt fresh; the ledger split preserves the pre-existing ONE-lock
draining-check-plus-capacity-decision invariant; budget reconciliation on
adoption honors growth/valid-shrink immediately and refuses an invalid
shrink typed; every admission surface (fan-out and direct) sees the SAME
residual; release/no-double-release/interpreter-exit posture are unaffected
by the split.
"""

from __future__ import annotations

import inspect
import threading
import time

import pytest
from harness_core import SubAgentDispatchCapacityError
from harness_runtime.lifecycle import sub_agent_dispatch_executor as sade_module
from harness_runtime.lifecycle.sub_agent_dispatch_executor import (
    CapacityAuthorityBudgetShrinkError,
    FrameLedger,
    SubAgentDispatchExecutor,
    adopt_or_create_process_capacity_ledger,
)


def test_cross_bootstrap_fanout_admission_sees_residual_not_full_budget() -> None:
    """Fork §4 item 1 — the defect's direct witness. Run 1 leaves a worker
    draining past its shutdown deadline (an unreleased lease occupies
    frames); run 2's fan-out admission must see `budget - occupied`, never
    the full configured budget.

    Mutation probe: reverting stage 5 to unconditional fresh-construction
    (a fresh `FrameLedger` every bootstrap instead of adopting) makes run 2
    see the full budget instead of the residual — over-admission reproduces.
    """
    ledger1 = adopt_or_create_process_capacity_ledger(4)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    # Simulates a still-draining worker from run 1: reserved but never
    # released (the lease releases only via its own done-callback, never at
    # bootstrap teardown — §14.8.10.1/§14.8.10.3).
    executor1.reserve(2, step_id="run1-straggler", descent_chain=("run1-straggler",))

    # Run 2: a FRESH executor bound to the ADOPTED (not fresh) ledger.
    ledger2 = adopt_or_create_process_capacity_ledger(4)
    assert ledger2 is ledger1
    executor2 = SubAgentDispatchExecutor(ledger=ledger2)

    assert executor2.available_frames == 2  # 4 - 2 occupied, never the full 4
    results = executor2.reserve_fanout(
        (3,), step_ids=("run2-branch",), descent_chain=("wf", "run2-branch")
    )
    assert isinstance(results[0], SubAgentDispatchCapacityError)  # 3 > residual 2
    results = executor2.reserve_fanout(
        (2,), step_ids=("run2-branch-fits",), descent_chain=("wf", "run2-branch-fits")
    )
    assert results[0].frames == 2


def test_reusing_executor_object_across_bootstrap_permanently_rejects_admission() -> None:
    """Ledger-vs-executor-object witness (codex round-1 on this rider): a
    NEGATIVE control proving why the ledger/executor split is required.

    Mutation probe: an implementation that adopts the PRIOR bootstrap's
    executor OBJECT (not just its ledger) after that object's `drain()` ran
    fails EVERY subsequent admission permanently — distinguishing this
    failure mode from the over-admission the primary witness guards
    against.
    """
    ledger = FrameLedger(frame_budget=4)
    executor_run1 = SubAgentDispatchExecutor(ledger=ledger)
    executor_run1.drain(deadline_seconds=0.05)

    with pytest.raises(SubAgentDispatchCapacityError):
        executor_run1.reserve(1, step_id="run2-reuse-bug", descent_chain=("run2-reuse-bug",))
    assert ledger.available == 4  # the ledger itself is fine — only reuse is the bug

    # The CORRECT pattern: a FRESH executor bound to the SAME ledger admits normally.
    executor_run2 = SubAgentDispatchExecutor(ledger=ledger)
    lease = executor_run2.reserve(1, step_id="run2-correct", descent_chain=("run2-correct",))
    assert lease.frames == 1


def test_reserve_and_begin_draining_share_the_identical_lock_object() -> None:
    """Item 1c atomicity (codex round-4 sharpened — structural, not
    timing-dependent). A live timing-based race cannot deterministically
    force the split-lock failure window; the deterministic witness is
    structural identity of the lock object `reserve`/`reserve_fanout`/
    `submit` acquire and the one `begin_draining()` acquires.

    Mutation probe: an implementation using two separate `threading.Lock()`
    instances — one for the executor's `_draining` flag, one for the
    ledger's `_available` — fails this witness immediately (the two lock
    objects are not identical), even though it might pass any test that
    only checks final outcomes under lucky scheduling.
    """
    ledger = FrameLedger(frame_budget=4)
    executor = SubAgentDispatchExecutor(ledger=ledger)
    assert executor._admission_lock is ledger.lock


def test_cross_bootstrap_direct_dispatch_admission_sees_residual() -> None:
    """Fork §4 item 1b — the direct-dispatch twin. Same two-run setup as
    the fan-out witness, but run 2 issues a single non-fan-out `reserve(1)`
    offload instead of a fan-out.

    Mutation probe: an implementation that globalizes ONLY the fan-out
    adapter's accounting while leaving direct `reserve()` on a fresh
    per-bootstrap budget fails THIS witness while the fan-out witness still
    passes — pins that both surfaces, not just one, back onto the shared
    ledger.
    """
    ledger1 = adopt_or_create_process_capacity_ledger(4)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    executor1.reserve(3, step_id="run1-straggler", descent_chain=("run1-straggler",))

    ledger2 = adopt_or_create_process_capacity_ledger(4)
    executor2 = SubAgentDispatchExecutor(ledger=ledger2)

    assert executor2.available_frames == 1
    with pytest.raises(SubAgentDispatchCapacityError):
        executor2.reserve(2, step_id="run2-direct", descent_chain=("run2-direct",))
    lease = executor2.reserve(1, step_id="run2-direct-ok", descent_chain=("run2-direct-ok",))
    assert lease.frames == 1


def test_straggler_done_callback_releases_into_adopted_ledger() -> None:
    """Fork §4 item 2 — straggler release correctness: run 1's draining
    worker's eventual completion releases its frame into the SAME ledger
    run 2 read; a subsequent admission after the release succeeds at the
    now-correct residual.

    Mutation probe: routing the release into a stale/discarded ledger
    object leaves run 2 permanently under-admitted and fails.
    """
    ledger1 = adopt_or_create_process_capacity_ledger(4)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    lease = executor1.reserve(3, step_id="run1-straggler", descent_chain=("run1-straggler",))

    ledger2 = adopt_or_create_process_capacity_ledger(4)
    executor2 = SubAgentDispatchExecutor(ledger=ledger2)
    assert executor2.available_frames == 1

    assert lease.release() is True  # the straggler's eventual done-callback firing
    assert executor2.available_frames == 4

    lease2 = executor2.reserve(
        4, step_id="run2-after-release", descent_chain=("run2-after-release",)
    )
    assert lease2.frames == 4


def test_no_double_release_across_bootstrap_boundary() -> None:
    """Fork §4 item 2 — a release path that fires twice (once at
    hypothetical bootstrap teardown, once at the real done-callback) must
    be caught; asserts occupied-count arithmetic stays consistent, not
    merely non-negative.

    Mutation probe: an exactly-once guard that is lost across the ledger
    split would over-release and inflate `available_frames` past the
    configured budget.
    """
    ledger1 = adopt_or_create_process_capacity_ledger(4)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    lease = executor1.reserve(2, step_id="s", descent_chain=("s",))

    ledger2 = adopt_or_create_process_capacity_ledger(4)
    executor2 = SubAgentDispatchExecutor(ledger=ledger2)

    assert lease.release() is True
    assert lease.release() is False  # exactly-once guard holds ACROSS the boundary
    assert executor2.available_frames == 4  # never over-released past the budget


def test_straggler_release_races_budget_reconciliation_under_same_lock() -> None:
    """Fork §4 item 2 sharpened (codex round-1): run 2's bootstrap
    reconciles the budget concurrently with run 1's straggler done-callback
    releasing its lease. Both operations MUST serialize under the ledger's
    single lock so neither the release nor the reconciliation's read of
    `occupied` is lost.

    Two independent detection mechanisms, since either alone has a gap
    (codex round-2 on this witness):

    1. Lock-instrumentation overlap detection — catches a mutation that
       still acquires SOME lock but a SEPARATE one from `release()`'s.
       Gap: an implementation that DROPS locking from `reconcile_budget`
       entirely never touches the instrumented wrapper, so this alone
       reports "no overlap" even though the underlying race exists.
    2. A final-state invariant, repeated across many trials — regardless
       of interleaving order, a CORRECT (fully-locked) implementation
       always converges to `available == budget == 3` once both operations
       complete (release conserves total frames; reconcile's math sees
       whatever `occupied` it observes at the instant it runs, and either
       ordering nets out identically). An unsynchronized reconcile racing
       a real concurrent release can produce a torn read-modify-write that
       violates this invariant — repeating the race increases the chance
       of a real interleaving actually landing on a losing schedule.
    """
    for _ in range(50):
        _run_one_release_reconcile_race_trial()


def _run_one_release_reconcile_race_trial() -> None:
    ledger = FrameLedger(frame_budget=4)

    # `threading.Lock` instances are C-level objects whose methods cannot be
    # monkeypatched — swap in a plain-Python recording wrapper BEFORE
    # constructing the executor, so `executor._admission_lock` (captured at
    # construction time) and `ledger.lock` (read fresh by
    # `reconcile_budget`) are the SAME instrumented object end-to-end.
    active_holders = 0
    overlap_detected = threading.Event()
    counter_lock = threading.Lock()
    real_lock = threading.Lock()

    class _RecordingLock:
        def acquire(self, *args: object, **kwargs: object) -> bool:
            nonlocal active_holders
            acquired = real_lock.acquire(*args, **kwargs)
            if acquired:
                with counter_lock:
                    active_holders += 1
                    if active_holders > 1:
                        overlap_detected.set()
            return acquired

        def release(self) -> None:
            nonlocal active_holders
            with counter_lock:
                active_holders -= 1
            real_lock.release()

        def __enter__(self) -> None:
            self.acquire()

        def __exit__(self, *exc: object) -> None:
            self.release()

    ledger.lock = _RecordingLock()  # type: ignore[assignment]
    executor = SubAgentDispatchExecutor(ledger=ledger)
    lease = executor.reserve(3, step_id="straggler", descent_chain=("straggler",))

    barrier = threading.Barrier(2)
    results: dict[str, object] = {}

    def do_release() -> None:
        barrier.wait(timeout=5)
        results["released"] = lease.release()

    def do_reconcile() -> None:
        barrier.wait(timeout=5)
        try:
            ledger.reconcile_budget(3)
            results["reconciled"] = True
        except CapacityAuthorityBudgetShrinkError:
            results["reconciled"] = False

    t1 = threading.Thread(target=do_release)
    t2 = threading.Thread(target=do_reconcile)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)

    assert not overlap_detected.is_set(), (
        "release() and reconcile_budget() held the ledger's lock concurrently "
        "— not serialized under the SAME lock"
    )
    assert results["released"] is True
    # Valid whether reconcile observed occupied=3 (pre-release) or
    # occupied=0 (post-release) — 3 >= either, so the shrink is honored
    # either way.
    assert results["reconciled"] is True
    # Order-agnostic final invariant: release conserves total frames and
    # reconcile's math nets out identically either way — a torn/lost update
    # (unsynchronized reconcile) can violate this.
    assert ledger.budget == 3
    assert ledger.available == 3


def test_reconcile_budget_reads_and_writes_occupied_atomically_under_the_lock() -> None:
    """Structural witness (mirrors item 1c's own "a live timing-based race
    cannot deterministically force this" lesson) for the read-then-write
    inside `reconcile_budget`: the `occupied` read, the shrink-refusal
    check, and both writes to `budget`/`available` must all execute inside
    ONE `with self.lock:` block — never acquired-and-released partway
    through, which would let a concurrent `release()` land between the read
    and the write and silently discard it (fork §4 item 2's sharpened
    concern, codex round-2).

    Empirically, 150 trials of the sibling threaded race witness above
    (`test_straggler_release_races_budget_reconciliation_under_same_lock`)
    did NOT reproduce a lost update even with locking removed from
    `reconcile_budget` — CPython's GIL makes the plain-attribute
    read-modify-write in this method's short body effectively atomic
    against a two-thread race in practice, so a timing-based test alone
    cannot reliably catch this mutation. The deterministic check is
    structural, exactly as item 1c's own lock-identity witness argues:
    `reconcile_budget` must acquire `self.lock` EXACTLY ONCE, covering the
    occupied-read through the final `available` write as one critical
    section — a two-lock or lock-then-release-then-relock implementation
    would need a second `self.lock` occurrence to reacquire.
    """
    source = inspect.getsource(FrameLedger.reconcile_budget)
    assert source.count("self.lock") == 1


def test_budget_grow_across_bootstraps_honored_immediately() -> None:
    """Fork §4 item 3 — budget reconfiguration: run 2 configures a LARGER
    `sub_agent_dispatch_max_workers`; the adopted ledger's available
    capacity reflects the growth immediately."""
    ledger1 = adopt_or_create_process_capacity_ledger(4)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    lease = executor1.reserve(2, step_id="s", descent_chain=("s",))

    ledger2 = adopt_or_create_process_capacity_ledger(8)
    assert ledger2 is ledger1
    executor2 = SubAgentDispatchExecutor(ledger=ledger2)
    assert executor2.frame_budget == 8
    assert executor2.available_frames == 6  # 8 - 2 occupied, growth honored immediately

    lease.release()
    assert executor2.available_frames == 8


def test_budget_shrink_below_occupied_refused_typed_at_bootstrap() -> None:
    """Fork §4 item 3 — run 2 configures a budget below run 1's still-
    occupied count; bootstrap raises `CapacityAuthorityBudgetShrinkError`
    naming both the configured budget and the occupied count.

    Mutation probe: silently clamping `available` to 0 instead of raising,
    or proceeding with a negative `available`, fails this witness.
    """
    ledger1 = adopt_or_create_process_capacity_ledger(8)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    executor1.reserve(5, step_id="s", descent_chain=("s",))

    with pytest.raises(CapacityAuthorityBudgetShrinkError) as excinfo:
        adopt_or_create_process_capacity_ledger(3)
    assert excinfo.value.configured_budget == 3
    assert excinfo.value.occupied_frames == 5
    assert excinfo.value.rt_fail_class == "RT-FAIL-CAPACITY-AUTHORITY-BUDGET-SHRINK"

    # The refused reconciliation must leave the ledger's state UNCHANGED.
    assert ledger1.budget == 8
    assert ledger1.available == 3


def test_budget_shrink_at_or_above_occupied_honored_immediately() -> None:
    """Fork §4 item 3 codex round-2: run 2 configures a budget SMALLER than
    run 1's original budget but still AT OR ABOVE run 1's current occupied
    count — the shrink is honored immediately at the new smaller budget.

    Mutation probe: an implementation that rejects every shrink regardless
    of the occupied count, OR that silently retains the old larger budget,
    fails THIS witness while the below-occupied refusal witness still
    passes — distinguishes valid-shrink-honored from invalid-shrink-refused.
    """
    ledger1 = adopt_or_create_process_capacity_ledger(8)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    executor1.reserve(5, step_id="s", descent_chain=("s",))

    ledger2 = adopt_or_create_process_capacity_ledger(5)  # shrink to EXACTLY occupied
    assert ledger2 is ledger1
    executor2 = SubAgentDispatchExecutor(ledger=ledger2)
    assert executor2.frame_budget == 5
    assert executor2.available_frames == 0
    with pytest.raises(SubAgentDispatchCapacityError):
        executor2.reserve(1, step_id="over", descent_chain=("over",))


def test_no_new_join_introduced_at_adopt_path() -> None:
    """Fork §4 item 5 — interpreter-exit posture: the adopt-or-construct
    branch and the reconciliation method perform no blocking join; existing
    shutdown-drain-with-deadline coverage from U-RT-141 is unaffected.

    Static assertion (the adopt path is not a live-traffic/timing surface —
    a source-level check is deterministic where a timing-based one would be
    flaky): neither `adopt_or_create_process_capacity_ledger` nor
    `FrameLedger.reconcile_budget` calls `.join(`.
    """
    source = inspect.getsource(sade_module.adopt_or_create_process_capacity_ledger)
    source += inspect.getsource(FrameLedger.reconcile_budget)
    assert ".join(" not in source

    # Behavioral corroboration: adopting with a still-outstanding lease from
    # a prior "bootstrap" returns promptly, never blocking on that lease.
    ledger1 = adopt_or_create_process_capacity_ledger(4)
    executor1 = SubAgentDispatchExecutor(ledger=ledger1)
    lease = executor1.reserve(2, step_id="s", descent_chain=("s",))
    started = time.monotonic()
    ledger2 = adopt_or_create_process_capacity_ledger(4)
    elapsed = time.monotonic() - started
    assert elapsed < 0.5
    assert ledger2 is ledger1
    lease.release()

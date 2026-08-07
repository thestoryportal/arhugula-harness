"""B-93 — the deadline primitive itself (`harness_core.cross_process_lock_deadline`).

Unit-level witnesses for the mechanism the nine acquisition sites share. The
per-SITE witnesses (a genuine second OS process holding each of the nine locks)
live beside their carriers at `harness-is/tests/test_b93_lock_deadline_is_sites.py`
and `harness-runtime/tests/test_b93_lock_deadline_runtime_sites.py`; this file
pins the properties those witnesses would not distinguish:

- an UNCONTENDED acquisition succeeds even with an already-spent budget (the
  bound is on WAITING, never on acquiring);
- a CONTENDED acquisition raises the typed error, and raises it WITHOUT holding
  the lock;
- the deadline is ABSOLUTE, so threading it through a multi-site entry surface
  or a retry loop cannot re-arm it (the end-to-end contract);
- non-contention errors propagate unchanged rather than being folded into a
  timeout.
"""

from __future__ import annotations

import errno
import os
import sys
import time
from pathlib import Path

import pytest
from harness_core import CrossProcessLockTimeoutError
from harness_core.cross_process_lock_deadline import (
    DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS,
    CrossProcessLockDeadline,
    flock_until_deadline,
)

# `fcntl` is POSIX-only and this module imports it at collection time for its
# in-process contention helpers. A module-level `import fcntl` would raise
# `ModuleNotFoundError` on Windows BEFORE pytest could evaluate any skip marker,
# so collecting the whole `harness-core` suite would fail on a host OS
# `Target_Stack_Commitment_v1.md:42` (C-STK-10) commits to. Skipping at module
# level keeps the suite collectable there and skipped rather than broken
# *(out-of-family review round 4 [P2], accepted)*.
if sys.platform == "win32":  # pragma: no cover — POSIX-only CI
    pytest.skip(
        "the cross-process lock deadline is exercised through `fcntl.flock`, "
        "which Windows does not provide (the B-45 carve-out)",
        allow_module_level=True,
    )

import fcntl  # POSIX-only; guarded by the module-level skip above

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32", reason="fcntl.flock is POSIX-only (the B-45 carve-out)"
)


def _held_fd(path: Path) -> int:
    """Open `path` and hold LOCK_EX on it — the in-process contender."""
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def test_the_windows_skip_guard_precedes_the_fcntl_import() -> None:
    """Out-of-family review round 4 [P2], accepted — a STRUCTURAL check, and
    labelled as one because a behavioural witness is NOT AVAILABLE here.

    The property: on Windows a bare module-level `import fcntl` would raise
    `ModuleNotFoundError` BEFORE pytest could evaluate any skip marker, so
    collecting the whole `harness-core` suite would FAIL — not skip — on a host
    OS `Target_Stack_Commitment_v1.md:42` (C-STK-10) commits to. The
    module-level `pytest.skip` above fixes it, and its ORDER relative to the
    import is the entire fix.

    **Why this is not an executing witness, stated rather than glossed.** A
    subprocess that fakes `sys.platform = "win32"` plus an absent `fcntl` was
    BUILT and DISCARDED at this arc: faking the platform makes the *stdlib*
    take its Windows branches too, and the run dies on `_winapi` long before
    reaching this module. Simulating Windows in-process is not simulating
    Windows. That is precisely the witnessability gate `B-45` is deferred on —
    so the honest posture is a presence check that is HONEST ABOUT BEING ONE,
    not a behavioural claim POSIX CI cannot support. A real `windows-latest`
    job (demand test `D-1`) would witness it for free.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    guard = source.index('if sys.platform == "win32":')
    fcntl_import = source.index("\nimport fcntl")
    assert guard < fcntl_import, (
        "the module-level Windows skip must come BEFORE `import fcntl`, or "
        "collection dies on Windows before the guard is reached"
    )
    assert "allow_module_level=True" in source[guard:fcntl_import], (
        "the guard must skip at MODULE level; a function-level skip runs too late"
    )


def test_the_error_is_reachable_from_the_package_root() -> None:
    """The ratified home (fork §12.4 item 2): ONE nominal type at `harness_core`,
    importable from the package root by all four carriers. A carrier defining its
    own would type-check fine and be a DIFFERENT class at every `except` arm."""
    import harness_core.cross_process_lock_deadline as deadline_module

    assert CrossProcessLockTimeoutError is deadline_module.CrossProcessLockTimeoutError
    assert "CrossProcessLockTimeoutError" in __import__("harness_core").__all__


def test_the_error_is_not_an_oserror_or_timeouterror() -> None:
    """Base-class choice is load-bearing, not cosmetic. Three of the nine sites
    sit inside `except OSError` arms that classify ENOTSUP and yield UNGUARDED;
    an OSError-derived timeout would be swallowed into that degradation path and
    the caller would silently proceed without the lock."""
    assert not issubclass(CrossProcessLockTimeoutError, OSError)
    assert not issubclass(CrossProcessLockTimeoutError, TimeoutError)
    assert issubclass(CrossProcessLockTimeoutError, Exception)


def test_default_budget_is_the_declared_conservative_value() -> None:
    """Pins the one value this arc CHOSE rather than inherited (the fork ratified
    that a deadline exists, not what it is). A silent shortening is a regression
    risk on a substrate hardened across four closed rows."""
    assert DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS == 300.0
    assert CrossProcessLockDeadline.starting_now().budget_seconds == 300.0
    assert CrossProcessLockDeadline.starting_now(0.5).budget_seconds == 0.5


def test_a_non_positive_budget_is_refused() -> None:
    """Detect-then-refuse: a zero/negative budget would make every contended
    acquisition fail without waiting at all — a silent no-lock posture."""
    for bad in (0.0, -1.0):
        with pytest.raises(ValueError, match="finite positive"):
            CrossProcessLockDeadline.starting_now(bad)


def test_the_dataclass_constructor_itself_refuses_a_non_expiring_deadline() -> None:
    """Out-of-family review round 2 [P2], accepted. The dataclass is EXPORTED and
    directly constructible, so validating only in `starting_now` left the
    illegal state one ordinary constructor call away: a `nan` expiry makes
    `remaining_seconds()` return `nan`, `remaining <= 0` is never true, and a
    contended acquisition polls FOREVER — the unbounded block this module
    removes, reachable through the public type.

    Mutation probe (run at this arc): deleting `__post_init__` lets every case
    below construct and this test fails."""
    for bad in (float("inf"), float("nan"), 0.0, -1.0):
        with pytest.raises(ValueError, match="finite positive"):
            CrossProcessLockDeadline(budget_seconds=bad)


def test_the_expiry_cannot_disagree_with_the_declared_budget() -> None:
    """Out-of-family review round 3 [P2], accepted. Validating the two fields
    INDEPENDENTLY was not enough: a caller could declare `budget_seconds=0.001`
    with an expiry an hour out, and every timeout message would then report a
    1 ms budget for an hour-long wait — a diagnostic that lies about the one
    thing this type exists to make legible.

    Closed by removing the SECOND AUTHORITY rather than policing a relationship:
    `expires_at` is DERIVED, so the fields cannot disagree by construction. The
    witness is that supplying it is a TypeError — not that a mismatch is
    rejected, which would still admit the two-authority shape.

    Mutation probe (run at this arc): restoring `expires_at` as an `init=True`
    field makes the constructor accept the mismatch and this test fails."""
    with pytest.raises(TypeError):
        CrossProcessLockDeadline(budget_seconds=0.001, expires_at=time.monotonic() + 3600)  # type: ignore[call-arg]
    derived = CrossProcessLockDeadline(budget_seconds=0.5)
    assert 0.0 < derived.remaining_seconds() <= 0.5, (
        "expiry is not derived from the declared budget"
    )


@requires_posix_flock
def test_a_late_wake_past_the_budget_does_not_acquire(tmp_path: Path) -> None:
    """Out-of-family review round 2 [P2], accepted. `time.sleep` is a FLOOR, not
    a promise — a loaded scheduler can wake the poller well past its remaining
    budget. Without an expiry check AFTER the sleep the loop probes first, so a
    holder releasing during the overshoot hands the lock to a caller whose
    deadline had already passed: a bound that holds "usually".

    The overshoot is simulated deterministically by patching `time.sleep` inside
    the module to release the holder and then sleep past the budget — waiting on
    a real scheduler stall would be a flake, not a witness.

    Round 6 [P2] sharpened WHERE the check has to live: gating the probe cannot
    close this, because the thread can be descheduled between the check and the
    probe. The check now sits on the SUCCESS path, so the probe here genuinely
    ACQUIRES and is then unlocked and refused — which is why the assertion below
    that the lock is free afterwards is load-bearing, not decorative.

    Mutation probe (run at this arc): removing the success-path expiry check
    makes the acquisition stand and this test fails."""
    import harness_core.cross_process_lock_deadline as module

    target = tmp_path / "latewake.lock"
    holder = _held_fd(target)
    waiter = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    real_sleep = time.sleep
    released = False

    def _overshooting_sleep(_seconds: float) -> None:
        nonlocal released
        if not released:
            released = True
            fcntl.flock(holder, fcntl.LOCK_UN)  # the holder lets go mid-sleep
        real_sleep(0.15)  # ... and we wake well past a 0.05s budget

    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(module.time, "sleep", _overshooting_sleep)
            with pytest.raises(CrossProcessLockTimeoutError):
                flock_until_deadline(
                    waiter,
                    fcntl.LOCK_EX,
                    deadline=CrossProcessLockDeadline.starting_now(0.05),
                    lock_target=str(target),
                )
        assert released, "the holder never released — the probe did not exercise the race"
        # And it really did not take the lock, even though it was free.
        third = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(third, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(third, fcntl.LOCK_UN)
        finally:
            os.close(third)
    finally:
        os.close(waiter)
        os.close(holder)


def test_a_non_finite_budget_is_refused() -> None:
    """Out-of-family review round 1 [P2], accepted. `inf` passes a bare `> 0`
    trivially and `nan` passes it because EVERY comparison with `nan` is False —
    and either makes `remaining_seconds()` never reach `<= 0`, so the poll loop
    spins forever and RECREATES the indefinite hang this module exists to
    remove. The check must be finiteness, not just sign.

    Mutation probe (run at this arc): reverting the guard to `budget <= 0.0`
    makes both cases construct successfully and this test fails."""
    for bad in (float("inf"), float("nan")):
        with pytest.raises(ValueError, match="finite positive"):
            CrossProcessLockDeadline.starting_now(bad)


def test_the_deadline_is_absolute_and_cannot_be_re_armed() -> None:
    """The END-TO-END contract. One entry surface blocks at up to THREE sites in
    sequence and retries the whole acquisition on an inode swap; a RELATIVE
    budget threaded down that path is indistinguishable from a fresh one at every
    hop, which is the "partial guarantee that reads as a total one" the fork's
    §5 Variant F was dominated on. Passing the same object twice must therefore
    spend, not reset."""
    deadline = CrossProcessLockDeadline.starting_now(0.2)
    first = deadline.remaining_seconds()
    time.sleep(0.1)
    second = deadline.remaining_seconds()
    assert second < first
    assert second <= 0.11
    time.sleep(0.15)
    assert deadline.remaining_seconds() <= 0.0


@requires_posix_flock
def test_uncontended_acquisition_succeeds_with_an_already_spent_budget(tmp_path: Path) -> None:
    """The bound is on WAITING, not on acquiring. An expired deadline must not
    refuse a lock nobody holds — otherwise every long-running caller would start
    failing acquisitions it would previously have taken instantly."""
    target = tmp_path / "uncontended.lock"
    fd = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        spent = CrossProcessLockDeadline.starting_now(0.01)
        time.sleep(0.05)
        assert spent.remaining_seconds() < 0
        flock_until_deadline(fd, fcntl.LOCK_EX, deadline=spent, lock_target=str(target))
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


@requires_posix_flock
def test_contended_acquisition_raises_the_typed_error_and_does_not_hold(tmp_path: Path) -> None:
    """The headline behaviour, plus the property a bare `pytest.raises` would
    miss: on timeout the lock is NOT held. If the failed attempt left the flock
    acquired, the caller's unwind would release a lock it never took — and the
    holder's own release would then be a double-unlock."""
    target = tmp_path / "contended.lock"
    holder = _held_fd(target)
    waiter = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        deadline = CrossProcessLockDeadline.starting_now(0.2)
        started = time.monotonic()
        with pytest.raises(CrossProcessLockTimeoutError, match="not acquired within its 0.2s"):
            flock_until_deadline(waiter, fcntl.LOCK_EX, deadline=deadline, lock_target=str(target))
        elapsed = time.monotonic() - started
        assert elapsed >= 0.2, "returned before spending its budget — it did not actually wait"
        assert elapsed < 5.0, "waited far past its budget"
        # It genuinely did not acquire: a THIRD fd can still be refused by the
        # holder, which is only true while the holder's LOCK_EX stands.
        third = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(third, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(third)
    finally:
        os.close(waiter)
        fcntl.flock(holder, fcntl.LOCK_UN)
        os.close(holder)


@requires_posix_flock
def test_the_error_names_the_lock_target_and_the_budget(tmp_path: Path) -> None:
    """The row's harm is "no error, no log and no timeout" — a bare
    `TimeoutError` would fix only the third. The diagnostic must say WHICH lock
    and for HOW LONG, or an operator is no better placed than before."""
    target = tmp_path / "named.lock"
    holder = _held_fd(target)
    waiter = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        with pytest.raises(CrossProcessLockTimeoutError) as caught:
            flock_until_deadline(
                waiter,
                fcntl.LOCK_EX,
                deadline=CrossProcessLockDeadline.starting_now(0.05),
                lock_target=str(target),
            )
        assert caught.value.lock_target == str(target)
        assert caught.value.budget_seconds == 0.05
        assert str(target) in str(caught.value)
        assert "NOT entered" in str(caught.value)
    finally:
        os.close(waiter)
        fcntl.flock(holder, fcntl.LOCK_UN)
        os.close(holder)


@requires_posix_flock
def test_contention_observed_withdraws_the_first_probe_exemption(tmp_path: Path) -> None:
    """Out-of-family review round 7 [P2], accepted.

    The three ABBA arms run their OWN non-blocking probe, see `BlockingIOError`,
    release the directory lock, and only THEN call this helper. By that point
    contention is an ESTABLISHED FACT and the caller has already waited — so
    exempting this helper's first probe would let a holder releasing during the
    handoff give the lock to a caller whose budget had already expired. The
    exemption exists for the case where nothing was ever contended, and that is
    not this case.

    Here the lock is FREE and the budget SPENT — the exact shape the exemption
    would wave through — and the call must refuse anyway.

    Mutation probe (run at this arc): defaulting `first_probe = True` regardless
    of `contention_observed` makes this acquire and the test fails."""
    target = tmp_path / "handoff-exempt.lock"
    fd = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        spent = CrossProcessLockDeadline.starting_now(0.01)
        time.sleep(0.05)
        assert spent.remaining_seconds() < 0
        with pytest.raises(CrossProcessLockTimeoutError):
            flock_until_deadline(
                fd,
                fcntl.LOCK_EX,
                deadline=spent,
                lock_target=str(target),
                contention_observed=True,
            )
        # It refused WITHOUT leaving the lock held.
        other = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(other, fcntl.LOCK_UN)
        finally:
            os.close(other)
        # A FRESH deadline over the same free lock still succeeds — the refusal
        # above is about the SPENT budget, not about the lock. Deliberately a
        # fresh one: re-using `spent` here would now ALSO refuse, because the
        # declared contention is recorded on the DEADLINE and persists to every
        # later site under it (that persistence is its own witness below).
        flock_until_deadline(
            fd,
            fcntl.LOCK_EX,
            deadline=CrossProcessLockDeadline.starting_now(1.0),
            lock_target=str(target),
        )
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


@requires_posix_flock
def test_the_exemption_is_spent_by_contention_anywhere_under_the_deadline(
    tmp_path: Path,
) -> None:
    """Out-of-family review round 10 [P2], accepted — the third and last
    instance of the exemption class (rounds 2 and 6 were the first two).

    `contention_observed` was a PER-CALL flag, so an entry surface that
    contended at site 1 — spending its whole budget there — could then take a
    FREE site 2 through *that* site's own first-probe exemption, after expiry.
    The exemption is a property of the ENTRY SURFACE ("nothing here ever
    waited"), not of one call, so the flag now travels ON the deadline.

    Here site 1 genuinely waits out its budget and site 2 is completely free —
    the exact shape the per-call flag waved through.

    Mutation probe (run at this arc): dropping `and not deadline.has_contended()`
    makes the second acquisition succeed and this test fails."""
    deadline = CrossProcessLockDeadline.starting_now(0.15)

    contended = tmp_path / "site1.lock"
    free = tmp_path / "site2.lock"
    holder = _held_fd(contended)
    waiter = os.open(contended, os.O_CREAT | os.O_RDWR, 0o600)
    second = os.open(free, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        # Site 1: contends and spends the budget.
        with pytest.raises(CrossProcessLockTimeoutError):
            flock_until_deadline(
                waiter, fcntl.LOCK_EX, deadline=deadline, lock_target=str(contended)
            )
        assert deadline.has_contended(), "site 1's wait was not recorded on the deadline"
        assert deadline.remaining_seconds() <= 0.0
        # Site 2: FREE, and under the same (now spent) deadline. It must refuse.
        with pytest.raises(CrossProcessLockTimeoutError):
            flock_until_deadline(second, fcntl.LOCK_EX, deadline=deadline, lock_target=str(free))
        # A FRESH deadline over the same free lock still succeeds — the refusal
        # above is about the spent budget, not about the lock.
        flock_until_deadline(
            second,
            fcntl.LOCK_EX,
            deadline=CrossProcessLockDeadline.starting_now(1.0),
            lock_target=str(free),
        )
        fcntl.flock(second, fcntl.LOCK_UN)
    finally:
        os.close(second)
        os.close(waiter)
        fcntl.flock(holder, fcntl.LOCK_UN)
        os.close(holder)


@requires_posix_flock
def test_observed_contention_persists_to_later_sites(tmp_path: Path) -> None:
    """Out-of-family review at the merge-gate fix round — the same class as the
    round-10 fix, ONE HOP OUT.

    An ABBA arm passes `contention_observed=True` because it already saw
    `BlockingIOError` and already waited. If the holder then releases before this
    helper's first probe, the probe SUCCEEDS — and if the flag only gated that
    one call, `has_contended()` stayed False and a LATER site under the same
    end-to-end deadline regained its own first-probe exemption, acquiring past
    expiry. The fact has to persist on the DEADLINE, because that is what spans
    the sites.

    Site 1 here is UNCONTENDED at probe time but declares prior contention; site
    2 is free and the budget is spent. Site 2 must still refuse.

    Mutation probe (run at this arc): gating on `contention_observed` alone
    (without `deadline.note_contention()`) makes site 2 acquire and this fails."""
    deadline = CrossProcessLockDeadline.starting_now(0.05)
    first = tmp_path / "abba-site1.lock"
    second = tmp_path / "abba-site2.lock"
    fd1 = os.open(first, os.O_CREAT | os.O_RDWR, 0o600)
    fd2 = os.open(second, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        # Site 1: free at probe time, but the caller declares it already waited.
        flock_until_deadline(
            fd1,
            fcntl.LOCK_EX,
            deadline=deadline,
            lock_target=str(first),
            contention_observed=True,
        )
        fcntl.flock(fd1, fcntl.LOCK_UN)
        assert deadline.has_contended(), (
            "the declared contention was not recorded on the deadline — a later "
            "site will regain the first-probe exemption"
        )
        time.sleep(0.1)  # spend the budget
        assert deadline.remaining_seconds() <= 0.0
        # Site 2: free, same deadline, budget gone. Must refuse.
        with pytest.raises(CrossProcessLockTimeoutError):
            flock_until_deadline(fd2, fcntl.LOCK_EX, deadline=deadline, lock_target=str(second))
    finally:
        os.close(fd1)
        os.close(fd2)


def test_contention_state_is_constant_size() -> None:
    """Out-of-family review, merge-gate fix round 2 — `note_contention()` is
    IDEMPOTENT.

    `has_contended()` needs exactly one bit, but the poll loop calls
    `note_contention()` on EVERY retry: at the 1–5 ms cadence against the 300 s
    default that is ~60,000 calls per waiter, multiplied by every concurrent
    waiter on the same wedged lock. Appending each one grew a list nobody reads
    for its length — avoidable memory growth on exactly the pathological path
    the deadline exists to survive.

    Mutation probe (run at this arc): dropping the `if not self._contention`
    guard makes the recorded state grow with the call count and this fails."""
    deadline = CrossProcessLockDeadline.starting_now(1.0)
    assert not deadline.has_contended()
    for _ in range(1000):
        deadline.note_contention()
    assert deadline.has_contended()
    assert len(deadline._contention) == 1, (  # pyright: ignore[reportPrivateUsage]
        f"contention state grew to {len(deadline._contention)} entries "  # pyright: ignore[reportPrivateUsage]
        f"— it must stay constant-size"
    )


@requires_posix_flock
def test_shared_waiters_are_bounded_too(tmp_path: Path) -> None:
    """LOCK_SH is bounded exactly as LOCK_EX is. A shared reader blocked by an
    exclusive writer waits just as indefinitely, and one of the nine sites
    (`cross_process_read_lock`) is shared — bounding only the exclusive sites
    would leave `harness-inspect` unbounded."""
    target = tmp_path / "shared.lock"
    holder = _held_fd(target)
    waiter = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        with pytest.raises(CrossProcessLockTimeoutError):
            flock_until_deadline(
                waiter,
                fcntl.LOCK_SH,
                deadline=CrossProcessLockDeadline.starting_now(0.05),
                lock_target=str(target),
            )
    finally:
        os.close(waiter)
        fcntl.flock(holder, fcntl.LOCK_UN)
        os.close(holder)


@requires_posix_flock
def test_eacces_is_treated_as_contention_not_as_a_hard_failure(tmp_path: Path) -> None:
    """Out-of-family review round 8 [P1], accepted.

    `fcntl.flock`'s own docstring says it is "emulated using fcntl() on some
    systems", and the `lockf` docs spell out that a non-blocking failure arrives
    as `EACCES` *or* `EAGAIN` with an explicit instruction to "check for either
    value". A catch keyed on `BlockingIOError` alone therefore turns every
    contended acquisition on an emulated platform into an immediate
    `PermissionError`: the deadline never fires and the typed timeout is
    unreachable — the mechanism silently absent exactly where it is needed.

    `EACCES` cannot be produced natively on this host (Linux/macOS `flock` is
    real and reports `EWOULDBLOCK`), so contention is INJECTED. That is honest:
    the platform is unavailable, the BEHAVIOUR under it is not.

    Mutation probe (run at this arc): narrowing the catch back to
    `BlockingIOError` makes this raise `PermissionError` and the test fails."""
    target = tmp_path / "eacces.lock"
    fd = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    real_flock = fcntl.flock
    calls = {"n": 0}

    def _emulated_flock(the_fd: int, operation: int) -> None:
        if operation & fcntl.LOCK_NB:
            calls["n"] += 1
            if calls["n"] <= 2:
                raise PermissionError(errno.EACCES, "Permission denied")
        real_flock(the_fd, operation)

    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(fcntl, "flock", _emulated_flock)
            flock_until_deadline(
                fd,
                fcntl.LOCK_EX,
                deadline=CrossProcessLockDeadline.starting_now(5.0),
                lock_target=str(target),
            )
        assert calls["n"] >= 3, "the EACCES probes were not retried"
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def test_enotsup_is_not_in_the_contention_set() -> None:
    """No-over-widening guard on `_CONTENTION_ERRNOS` (merge-gate lens 3, G5).

    Three acquisition sites classify `ENOTSUP` — macOS raises it for a FIFO —
    and deliberately yield UNGUARDED so the caller's own validated open owns the
    loud rejection. If `ENOTSUP` were ever added to the contention set, those
    degradation arms would become unreachable: the helper would retry a lock the
    filesystem can never grant and then report a TIMEOUT, converting a
    documented, deliberate yield-unguarded path into a spurious deadline
    failure. The `EACCES` widening made that a live risk, so the boundary is
    pinned rather than left to reviewer memory.

    Mutation probe (run at this arc): adding `errno.ENOTSUP` to
    `_CONTENTION_ERRNOS` makes this test fail."""
    from harness_core.cross_process_lock_deadline import _CONTENTION_ERRNOS

    assert errno.ENOTSUP not in _CONTENTION_ERRNOS, (
        "ENOTSUP must NOT be contention — the three ENOTSUP arms yield "
        "unguarded on purpose and would become unreachable"
    )
    assert errno.EBADF not in _CONTENTION_ERRNOS
    assert _CONTENTION_ERRNOS == frozenset({errno.EWOULDBLOCK, errno.EAGAIN, errno.EACCES})


@requires_posix_flock
def test_a_non_contention_error_propagates_unchanged(tmp_path: Path) -> None:
    """Only BlockingIOError means "contended". Everything else (EBADF here;
    ENOTSUP on an un-flockable object in production) must reach the acquisition
    sites' own classifiers unmodified — folding them into a timeout would make
    the FIFO/ENOTSUP yield-unguarded arms unreachable."""
    target = tmp_path / "badfd.lock"
    fd = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    os.close(fd)
    with pytest.raises(OSError) as caught:
        flock_until_deadline(
            fd,
            fcntl.LOCK_EX,
            deadline=CrossProcessLockDeadline.starting_now(5.0),
            lock_target=str(target),
        )
    assert not isinstance(caught.value, CrossProcessLockTimeoutError)


@requires_posix_flock
def test_it_acquires_as_soon_as_the_holder_releases(tmp_path: Path) -> None:
    """The complement of the timeout witness: within its budget, a waiter that
    outlives the holder DOES acquire. Without this, a mechanism that simply
    always raised would pass every test above."""
    import threading

    target = tmp_path / "handoff.lock"
    holder = _held_fd(target)
    waiter = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
    acquired = threading.Event()

    def _wait() -> None:
        flock_until_deadline(
            waiter,
            fcntl.LOCK_EX,
            deadline=CrossProcessLockDeadline.starting_now(10.0),
            lock_target=str(target),
        )
        acquired.set()

    thread = threading.Thread(target=_wait)
    thread.start()
    try:
        assert not acquired.wait(0.3), "acquired while the holder still held LOCK_EX"
        fcntl.flock(holder, fcntl.LOCK_UN)
        assert acquired.wait(5.0), "never acquired after the holder released"
    finally:
        thread.join(10)
        os.close(holder)
        os.close(waiter)

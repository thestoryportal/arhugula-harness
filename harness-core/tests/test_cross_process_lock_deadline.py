"""B-93 — the deadline primitive itself (`harness_core.cross_process_lock_deadline`).

Unit-level witnesses for the mechanism the nine acquisition sites share. The
per-SITE witnesses (a genuine second OS process holding each of the nine locks)
live beside their carriers at `harness-is/tests/test_b93_cross_process_lock_deadline.py`
and `harness-runtime/tests/test_b93_cross_process_lock_deadline.py`; this file
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

import fcntl
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

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32", reason="fcntl.flock is POSIX-only (the B-45 carve-out)"
)


def _held_fd(path: Path) -> int:
    """Open `path` and hold LOCK_EX on it — the in-process contender."""
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


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
        with pytest.raises(ValueError, match="must be positive"):
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
        spent = CrossProcessLockDeadline(budget_seconds=1.0, expires_at=time.monotonic() - 5.0)
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

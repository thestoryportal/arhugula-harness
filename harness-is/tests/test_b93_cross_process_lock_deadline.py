"""B-93 — per-site deadline witnesses for the SIX `harness-is` acquisition sites.

The ratified Reading B (fork §12.4 item 6) owes "≥1 process-based deadline
witness per site-class". This file carries one per SITE rather than per class,
because the six sites differ in reachability, not only in shape: the two legacy
sidecar helpers are reached only through an ABSENT-canonical branch, and the
three ABBA arms are reached only after a non-blocking probe FAILS. A witness
that never reaches its site would pass on absence.

**Why a genuine second OS PROCESS.** Every one of these locks has an in-process
face too — `_DirLock`'s reentrant `threading.RLock`, and the callers' own module
`_WRITE_LOCK`s. A thread-based contender contends on THAT face and proves
nothing about the `flock`, which is the only face a second `harness run` sees.
The existing suite states this at `test_cross_process_ledger_lock.py`. The
holder here is a bare `python -c` that flocks the same inode: it needs no
harness import, so it cannot deadlock on a forked lock (the hazard
`test_shadow_git_rollback.py` records) and it models exactly what the kernel
sees — an unrelated process holding the inode.

Each test also pins WHICH lock timed out via `CrossProcessLockTimeoutError.lock_target`.
Without that, all six tests would pass identically if a single early acquisition
were bounded and the other five were not — the "partial guarantee that reads as
a total one" the fork's §5 Variant F was dominated on.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from harness_core import CrossProcessLockTimeoutError
from harness_is.cross_process_ledger_lock import (
    SCOPE_LOCK_FILENAME,
    cross_process_read_lock,
    cross_process_replace_lock,
    cross_process_scope_lock,
    cross_process_write_lock,
)

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32",
    reason="the cross-process locks degrade to a no-op on Windows (the B-45 register row)",
)

_DEADLINE = 0.2
"""Per-witness budget. Long enough that the holder is genuinely waited on (the
elapsed-time assertion below would fail on an instant refusal), short enough to
keep the suite fast."""

_HOLDER = """
import fcntl, os, sys, time
target, ready, release, mode, hold = sys.argv[1:6]
fd = os.open(target, os.O_RDONLY) if mode == "dir" else os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX)
open(ready, "w").close()
limit = time.monotonic() + float(hold)
while not os.path.exists(release) and time.monotonic() < limit:
    time.sleep(0.005)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
"""


class _ForeignHolder:
    """A genuine second OS process holding LOCK_EX on one inode.

    `hold_seconds` caps the hold so a witness can arrange a lock that releases
    PART WAY through the caller's budget — the only shape that can distinguish
    an end-to-end deadline from a per-acquisition one.
    """

    def __init__(
        self, tmp_path: Path, target: Path, *, mode: str = "file", hold_seconds: float = 60.0
    ) -> None:
        self._ready = tmp_path / f"ready-{os.getpid()}-{id(self)}"
        self._release = tmp_path / f"release-{os.getpid()}-{id(self)}"
        self._proc = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _HOLDER,
                str(target),
                str(self._ready),
                str(self._release),
                mode,
                str(hold_seconds),
            ]
        )

    def __enter__(self) -> _ForeignHolder:
        limit = time.monotonic() + 30
        while not self._ready.exists() and time.monotonic() < limit:
            if self._proc.poll() is not None:  # pragma: no cover — holder crashed
                raise AssertionError(f"holder exited early: {self._proc.returncode}")
            time.sleep(0.01)
        assert self._ready.exists(), "holder never acquired the lock"
        return self

    def __exit__(self, *_exc: object) -> None:
        self._release.write_text("go")
        self._proc.wait(timeout=30)


def _assert_timed_out_on(target: Path, block: object) -> None:
    """Run `block` (a zero-arg callable), asserting it timed out on `target`."""
    started = time.monotonic()
    with pytest.raises(CrossProcessLockTimeoutError) as caught:
        block()  # type: ignore[operator]
    elapsed = time.monotonic() - started
    assert caught.value.lock_target == str(target), (
        f"timed out on {caught.value.lock_target}, not the expected {target} — "
        f"a DIFFERENT acquisition is bounded and this site may not be"
    )
    assert caught.value.budget_seconds == _DEADLINE
    assert elapsed >= _DEADLINE, "refused without waiting — it never contended"


def _seed(ledger: Path) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("seed\n")


# --- site 1 — `_DirLock.acquire`, via `cross_process_scope_lock` ------------


@requires_posix_flock
def test_site1_scope_lock_deadline_fires(tmp_path: Path) -> None:
    """The entry surface carrying the row's registered exposure:
    `write_record_guarded` holds THIS lock across a caller-supplied
    precondition, so an unbounded holder wedges every same-host memory writer."""
    root = tmp_path / "scope-root"
    root.mkdir()
    lock_file = root / SCOPE_LOCK_FILENAME
    lock_file.touch()
    with _ForeignHolder(tmp_path, lock_file):

        def _attempt() -> None:
            with cross_process_scope_lock(root, deadline_seconds=_DEADLINE):
                raise AssertionError("entered the scope section while a holder held it")

        _assert_timed_out_on(lock_file, _attempt)


@requires_posix_flock
def test_site1_scope_lock_still_acquires_uncontended(tmp_path: Path) -> None:
    """The non-contended path is UNCHANGED — with a budget so short a polling
    waiter could never win a contended race, an uncontended acquisition still
    succeeds instantly. Without this, a mechanism that always raised would pass
    the timeout witness above."""
    root = tmp_path / "scope-root"
    entered = False
    with cross_process_scope_lock(root, deadline_seconds=0.001):
        entered = True
    assert entered


# --- site 2 — `_acquire_legacy_sidecar_for_writer` -------------------------


@requires_posix_flock
def test_site2_legacy_sidecar_writer_deadline_fires(tmp_path: Path) -> None:
    """Reached only through the ABSENT-canonical branch of the write lock: the
    directory lock is taken, the canonical open raises FileNotFoundError, and
    the legacy sidecar is provisioned + locked for the rolling-upgrade window.
    The canonical file is deliberately NOT created here."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True)
    sidecar = ledger.with_name(ledger.name + ".lock")
    with _ForeignHolder(tmp_path, sidecar):

        def _attempt() -> None:
            with cross_process_write_lock(ledger, deadline_seconds=_DEADLINE):
                raise AssertionError("entered the absent-file section")

        _assert_timed_out_on(sidecar, _attempt)


# --- site 3 — `_acquire_legacy_sidecar_if_present` (the SHARED site) -------


@requires_posix_flock
def test_site3_legacy_sidecar_shared_deadline_fires(tmp_path: Path) -> None:
    """The one site of the nine that acquires SHARED. Reached through the read
    lock's absent-canonical branch, where the sidecar EXISTS on disk. A shared
    waiter is blocked by an exclusive holder just as indefinitely as an
    exclusive one, so bounding only the exclusive sites would leave this open."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True)
    sidecar = ledger.with_name(ledger.name + ".lock")
    sidecar.touch()
    with _ForeignHolder(tmp_path, sidecar):

        def _attempt() -> None:
            with cross_process_read_lock(ledger, deadline_seconds=_DEADLINE):
                raise AssertionError("entered the absent-file read section")

        _assert_timed_out_on(sidecar, _attempt)


# --- site 4 — `cross_process_write_lock`'s file lock (ABBA arm) ------------


@requires_posix_flock
def test_site4_write_lock_file_deadline_fires(tmp_path: Path) -> None:
    """The ABBA handoff arm: the non-blocking probe fails, the directory lock is
    RELEASED, and only then is the file lock waited on. The release-before-wait
    invariant is preserved — asserted separately below."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    _seed(ledger)
    with _ForeignHolder(tmp_path, ledger):

        def _attempt() -> None:
            with cross_process_write_lock(ledger, deadline_seconds=_DEADLINE):
                raise AssertionError("entered the write section")

        _assert_timed_out_on(ledger, _attempt)


@requires_posix_flock
def test_site4_abba_release_before_blocking_is_preserved(tmp_path: Path) -> None:
    """The ABBA-avoidance invariant the fork forbids breaking (§4): while this
    caller waits on the FILE lock, it must NOT be holding the parent directory —
    a sibling ledger in the same directory must stay writable throughout. This
    is the property a timeout witness alone cannot see."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    sibling = tmp_path / "state" / "sibling.jsonl"
    _seed(ledger)
    _seed(sibling)
    with _ForeignHolder(tmp_path, ledger):
        import threading

        waiting = threading.Event()
        sibling_entered = threading.Event()

        def _blocked_writer() -> None:
            waiting.set()
            try:
                with cross_process_write_lock(ledger, deadline_seconds=3.0):
                    pass  # pragma: no cover — the holder never releases in time
            except CrossProcessLockTimeoutError:
                pass

        thread = threading.Thread(target=_blocked_writer)
        thread.start()
        try:
            assert waiting.wait(5)
            time.sleep(0.3)  # let it reach the blocking arm
            # A DIFFERENT ledger in the SAME directory must still be writable:
            # only true if the waiter released the directory lock first.
            with cross_process_write_lock(sibling, deadline_seconds=2.0):
                sibling_entered.set()
            assert sibling_entered.is_set()
        finally:
            thread.join(20)


# --- site 5 — `cross_process_replace_lock`'s wait-out (ABBA arm) -----------


@requires_posix_flock
def test_site5_replace_lock_deadline_fires(tmp_path: Path) -> None:
    """The replace lock waits out an active file-lock holder before swapping the
    inode. Its wait sits inside a `while True` retry loop, so this also witnesses
    that the end-to-end deadline is not re-armed per turn."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    _seed(ledger)
    with _ForeignHolder(tmp_path, ledger):

        def _attempt() -> None:
            with cross_process_replace_lock(ledger, deadline_seconds=_DEADLINE):
                raise AssertionError("entered the replace section")

        _assert_timed_out_on(ledger, _attempt)


# --- site 6 — `cross_process_read_lock`'s SHARED file lock (ABBA arm) ------


@requires_posix_flock
def test_site6_read_lock_shared_deadline_fires(tmp_path: Path) -> None:
    """`harness-inspect` is an interactive read surface; an unbounded shared wait
    behind an exclusive writer hangs it with no diagnostic."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    _seed(ledger)
    with _ForeignHolder(tmp_path, ledger):

        def _attempt() -> None:
            with cross_process_read_lock(ledger, deadline_seconds=_DEADLINE):
                raise AssertionError("entered the read section")

        _assert_timed_out_on(ledger, _attempt)


@requires_posix_flock
def test_read_lock_still_acquires_uncontended(tmp_path: Path) -> None:
    """Non-contended read path unchanged — the shared lock is taken instantly
    when no exclusive holder exists."""
    ledger = tmp_path / "state" / "ledger.jsonl"
    _seed(ledger)
    with cross_process_read_lock(ledger, deadline_seconds=0.001):
        assert ledger.read_text() == "seed\n"


# --- the END-TO-END property, across two sites in ONE entry surface --------


@requires_posix_flock
def test_the_budget_is_spent_across_sites_not_reset_at_each(tmp_path: Path) -> None:
    """The end-to-end contract, witnessed by ELAPSED TIME across TWO waits.

    A witness that contends only ONE site cannot see this: one acquisition
    spends one budget under either design. So the shape here is deliberately
    two-stage — the DIRECTORY is held for 0.6 s and then released, while the
    legacy sidecar is held throughout and the canonical file is ABSENT. One
    `cross_process_write_lock` call therefore waits at site 1 (~0.6 s, then
    succeeds) and again at site 2 (until expiry).

    With ONE end-to-end budget of 1.0 s the call raises at ~1.0 s total.
    Re-minting per acquisition would give site 2 a FRESH 1.0 s and the call
    would raise at ~1.6 s. The 1.4 s assertion sits between the two.

    Mutation probe (run at this arc): re-minting the deadline at the
    `_acquire_legacy_sidecar_for_writer` call site makes this FAIL on elapsed
    time — the deadline still fires, so a witness that only asserted "it raises"
    would pass the mutation and prove nothing about the end-to-end claim.
    """
    budget = 1.0
    dir_hold = 0.6
    ledger = tmp_path / "state" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True)
    sidecar = ledger.with_name(ledger.name + ".lock")
    sidecar.touch()
    with _ForeignHolder(tmp_path, sidecar):
        with _ForeignHolder(tmp_path, ledger.parent, mode="dir", hold_seconds=dir_hold):
            started = time.monotonic()
            with pytest.raises(CrossProcessLockTimeoutError) as caught:
                with cross_process_write_lock(ledger, deadline_seconds=budget):
                    raise AssertionError("entered while the sidecar was held")
            elapsed = time.monotonic() - started
        # It reached the SECOND site — so two waits really happened.
        assert caught.value.lock_target == str(sidecar), (
            f"timed out at {caught.value.lock_target}, never reaching the second site"
        )
        assert elapsed >= dir_hold, "never waited out the directory holder"
        assert elapsed < budget + 0.4, (
            f"spent {elapsed:.3f}s against a {budget}s END-TO-END budget — the "
            f"deadline was re-minted at the second site rather than threaded"
        )

"""Cross-process advisory lock for ledger writers (B-40 + B-46, C-IS-09 §9.3 / C-MEM-08).

C-IS-07 §7.3 ("the C3-pole append-only write contract serializes writers") and
C-IS-09 §9.3 ("concurrent writes across sibling worktrees against the same
`.git` storage backend are serialized") already require this; §9.4 defers only
the *mechanism* to implementation discretion. This module supplies that
mechanism, mirroring the proven same-host `flock` pattern already shipped at
`harness_runtime.lifecycle.reconciler_pause_resume_substrate._workflow_lock`.

`fcntl.flock` is POSIX advisory + **same-host** — kernel-authoritative,
released on process death. It does NOT span hosts: true cross-host distributed
writers are explicitly out of design horizon per ADR-F2 §Rationale(c)(ii)
`[SPECULATIVE]`, and multi-writer scale beyond worktree-isolation is a
downstream-D-ADR-gated tier per C-IS-09 §9.4. This lock serves exactly the
in-scope requirement: multiple same-host processes (e.g. two concurrent
`harness run` invocations, or sibling worktree fan-out) writing the same
`.git`-backed canonical ledger.

C-STK-10 commits to macOS / Linux / Windows host-OS support "without per-OS
port forking"; the stdlib has no `fcntl` on Windows. Per the fan-out import
chain (`harness_is.__init__` eagerly imports `memory_operation_ledger`, which
imports this module), an unconditional top-level `import fcntl` would make
`import harness_is` itself fail on Windows. On `sys.platform == "win32"` the
context managers below therefore degrade to a no-op (yield without locking):
Windows sits at exact pre-B-40 parity. This is a registered gap, not a silent
one — the B-45 forward-register row.

**Lock target (B-46 redesign — this module's second landing).** The first
landing locked a lazily-created sibling `<ledger>.lock` file, which carried a
first-write TOCTOU: a reader racing the very first writer could pass the
"sidecar doesn't exist yet" check and read unguarded while that writer was
mid-append — the race window stayed ARMED for a ledger's entire pre-first-write
life. Per the B-46 register close-out, the lock target is now the CANONICAL
file itself (a separate fd opened purely for `flock` — POSIX `flock` is per
open-file-description, so a lock fd is independent of any I/O fd), with a
parent-DIRECTORY lock covering the one state the file lock cannot: the file
not existing yet.

- **Writers** acquire the parent-directory lock EXCLUSIVE first, then — if the
  canonical file exists — hand off to an EXCLUSIVE lock on the file and
  release the directory. If the file does NOT exist, the writer holds the
  directory lock for the whole critical section; the CALLER creates the file
  inside it (the lock itself NEVER creates the canonical file — file
  existence must keep meaning "a real append happened", which the audit
  writer's round-36 absence guard depends on).
- **Readers** take a SHARED lock on the canonical file when it exists. When it
  does not, they take a SHARED lock on the parent directory instead — which
  excludes exactly the absent-file-mode first writer — and re-check; a file
  that appeared in between is then read under its own SHARED lock. Readers
  never create files or directories and never `mkdir` (the `harness-inspect`
  read-only-CLI contract; Codex round 3 of the first landing).

The dir→file acquisition order is the SINGLE ordering everywhere (no cycle;
writers release the directory only after holding the file lock or finishing an
absent-file section). Residual, documented honestly: a reader whose ledger
PARENT DIRECTORY does not exist yields unguarded — closing that would require
the reader to create the directory, which the read-only contract forbids. For
every shipped ledger the parent is the state directory provisioned at
bootstrap, so the residual requires reading a ledger whose deployment was
never bootstrapped — a microseconds-wide race against `mkdir` itself, vs the
indefinitely-armed pre-B-46 window. Legacy `<ledger>.lock` sibling files from
the first landing are inert orphans (harmless; no reader or writer consults
them any longer).
"""

from __future__ import annotations

import os
import sys
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

_IS_WINDOWS = sys.platform == "win32"


class _DirLock:
    """Per-directory lock: one cross-process `flock` EX face + a per-thread
    REENTRANT in-process face.

    `flock` contends between separate fds even within one process, so a
    naive per-acquisition dir fd self-deadlocks the B-50
    `tenant_transaction` composition: the audit sidecar's absent-file
    section (dir EX held) performs the IS state-ledger append inside it,
    whose own write lock touches the SAME parent directory from the SAME
    thread. The `threading.RLock` face makes same-thread nesting legal
    (refcounted; the single flock fd is acquired at depth 0 and released at
    depth 0), while other threads and other processes still block.
    """

    __slots__ = ("_fd", "_path", "_refcount", "_rlock")

    def __init__(self, path: Path) -> None:
        self._path = path
        self._rlock = threading.RLock()
        self._refcount = 0
        self._fd = -1

    def acquire(self) -> None:
        import fcntl  # POSIX-only; callers gate win32.

        self._rlock.acquire()
        if self._refcount == 0:
            try:
                self._fd = os.open(self._path, os.O_RDONLY)
            except BaseException:
                # Codex round-1 P2: a failed open (dir removed, EMFILE,
                # transient permission error) must not leave the RLock
                # permanently held — later threads would block forever.
                self._rlock.release()
                raise
            try:
                fcntl.flock(self._fd, fcntl.LOCK_EX)
            except BaseException:
                os.close(self._fd)
                self._fd = -1
                self._rlock.release()
                raise
        self._refcount += 1

    def release(self) -> None:
        import fcntl

        self._refcount -= 1
        if self._refcount == 0:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = -1
        self._rlock.release()


_DIR_LOCKS: dict[str, _DirLock] = {}
_DIR_LOCKS_GUARD = threading.Lock()


def _dir_lock_for(parent: Path) -> _DirLock:
    key = str(parent.resolve())
    with _DIR_LOCKS_GUARD:
        lock = _DIR_LOCKS.get(key)
        if lock is None:
            lock = _DirLock(parent)
            _DIR_LOCKS[key] = lock
        return lock


@contextmanager
def cross_process_write_lock(canonical_path: Path) -> Generator[None, None, None]:
    """Hold an exclusive same-host lock across a read-prior -> append critical section.

    Callers still hold their own in-process `threading.Lock` around the same
    section (unchanged) — this lock adds the cross-process dimension the
    thread lock cannot provide. The lock NEVER creates the canonical file:
    when it does not exist yet, the parent-directory lock is held for the
    whole section and the caller's own append creates the file inside it
    (preserving "file existence == a real append happened" for the audit
    writer's absence guard).
    """
    if _IS_WINDOWS:
        yield
        return
    import fcntl  # POSIX-only; never reached on Windows.

    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        dir_lock = _dir_lock_for(canonical_path.parent)
        dir_lock.acquire()
        dir_held = True
        try:
            try:
                # O_NONBLOCK (codex round-3 P1): a planted FIFO must not
                # stall this open — a FIFO fd returns immediately and the
                # caller's own validated open rejects it downstream.
                file_fd = os.open(canonical_path, os.O_RDWR | getattr(os, "O_NONBLOCK", 0))
            except FileNotFoundError:
                # First write: the caller creates the file under the
                # directory lock (held for the whole section; per-thread
                # REENTRANT so a nested same-directory write inside the
                # section — the B-50 tenant_transaction composition —
                # cannot self-deadlock). Later writers re-check under
                # THEIR dir hold, see the file, and hand off below.
                yield
                return
            # Handoff: probe the file lock NON-BLOCKING under the dir
            # hold; on contention, RELEASE the dir first and only then
            # block on the file alone (codex round-2 P1 — blocking on a
            # file lock while holding the dir deadlocks against a holder
            # of that file lock that later wants this dir). The dir hold
            # spans only the probe, so sibling ledgers never serialize.
            try:
                try:
                    fcntl.flock(file_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    dir_lock.release()
                    dir_held = False
                    fcntl.flock(file_fd, fcntl.LOCK_EX)
            except BaseException:
                os.close(file_fd)
                raise
            finally:
                if dir_held:
                    dir_lock.release()
                    dir_held = False
            # Inode-stability verify (codex round-3 P1): flock rides the
            # INODE, and `cross_process_replace_lock` (rollback) swaps the
            # canonical inode — a lock riding a pre-replacement fd would
            # not serialize against post-replacement writers. If the path
            # no longer names our locked inode, retry from the top (each
            # retry requires an actual replacement event, so the loop
            # terminates in every real workload).
            try:
                path_ino = os.stat(canonical_path).st_ino
            except FileNotFoundError:
                path_ino = -1
            if path_ino != os.fstat(file_fd).st_ino:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                continue
            try:
                yield
            finally:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
            return
        finally:
            if dir_held:
                dir_lock.release()


@contextmanager
def cross_process_replace_lock(canonical_path: Path) -> Generator[None, None, None]:
    """Hold EXCLUSION for a section that REPLACES the canonical file's inode
    (shadow-git rollback's `git checkout` + `write_bytes`).

    Holds the parent-directory lock for the WHOLE section — the directory
    is the only inode-stable target across replacement — and additionally
    waits out any active file-lock holder first (non-blocking probe, then
    release-dir-and-block-and-retry per the round-2 ABBA rule). New
    writers/readers block at their transitional dir acquisition for the
    section's duration; stragglers that locked the pre-replacement inode
    are caught by the acquisition-side inode verify and retry.
    """
    if _IS_WINDOWS:
        yield
        return
    import fcntl  # POSIX-only; never reached on Windows.

    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    dir_lock = _dir_lock_for(canonical_path.parent)
    while True:
        dir_lock.acquire()
        try:
            file_fd = os.open(canonical_path, os.O_RDWR | getattr(os, "O_NONBLOCK", 0))
        except FileNotFoundError:
            break  # nothing to wait out; dir hold covers the section
        try:
            fcntl.flock(file_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # An active holder: release the dir, wait it out on the file
            # alone (ABBA rule), then retry the whole acquisition.
            dir_lock.release()
            fcntl.flock(file_fd, fcntl.LOCK_EX)
            fcntl.flock(file_fd, fcntl.LOCK_UN)
            os.close(file_fd)
            continue
        except BaseException:
            os.close(file_fd)
            dir_lock.release()
            raise
        # Hold BOTH the dir lock and the (old-inode) file lock across the
        # replacement section.
        try:
            try:
                yield
            finally:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
            return
        finally:
            dir_lock.release()
    try:
        yield
    finally:
        dir_lock.release()


@contextmanager
def cross_process_read_lock(canonical_path: Path) -> Generator[None, None, None]:
    """Hold a shared same-host lock across a read, excluding a concurrent writer.

    Side-effect free (the `harness-inspect` read-only contract): never
    creates files or directories, never `mkdir`s. Dir-first, symmetric
    with the writer (codex round-1 P1): a file-first fast path could open
    a file an absent-file-mode writer's caller had just created and take
    an uncontested SHARED lock mid-append. Only a ledger whose PARENT
    DIRECTORY does not exist yields unguarded (see module docstring).
    """
    if _IS_WINDOWS:
        yield
        return
    import fcntl  # POSIX-only; never reached on Windows.

    if not canonical_path.parent.exists():
        # No parent directory: nothing to read AND no bootstrapped
        # deployment to race — the documented residual window. (Readers
        # never mkdir; the harness-inspect read-only contract.)
        yield
        return
    while True:
        dir_lock = _dir_lock_for(canonical_path.parent)
        dir_lock.acquire()
        dir_held = True
        try:
            try:
                # O_NONBLOCK (codex round-3 P1): a planted FIFO must not
                # stall this open; the caller's validated open rejects it.
                file_fd = os.open(canonical_path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
            except FileNotFoundError:
                # Genuinely nothing to read; the dir hold excludes an
                # absent-file-mode first writer for the caller's section.
                # (Exclusive rather than shared — a deliberate
                # simplification: absent-file reads are the rare
                # pre-first-write window and read nothing.)
                yield
                return
            try:
                try:
                    fcntl.flock(file_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
                except BlockingIOError:
                    # Round-2 P1 ABBA rule: never block on a file lock
                    # while holding the dir.
                    dir_lock.release()
                    dir_held = False
                    fcntl.flock(file_fd, fcntl.LOCK_SH)
            except BaseException:
                os.close(file_fd)
                raise
            finally:
                if dir_held:
                    dir_lock.release()
                    dir_held = False
            # Inode-stability verify (round-3 P1) — mirror of the writer.
            try:
                path_ino = os.stat(canonical_path).st_ino
            except FileNotFoundError:
                path_ino = -1
            if path_ino != os.fstat(file_fd).st_ino:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                continue
            try:
                yield
            finally:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
            return
        finally:
            if dir_held:
                dir_lock.release()

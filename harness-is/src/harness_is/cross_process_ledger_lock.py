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
    dir_lock = _dir_lock_for(canonical_path.parent)
    dir_lock.acquire()
    dir_held = True
    try:
        try:
            file_fd = os.open(canonical_path, os.O_RDWR)
        except FileNotFoundError:
            # First write: the caller creates the file under the directory
            # lock (held for the whole section; per-thread REENTRANT so a
            # nested same-directory write inside the section — the B-50
            # tenant_transaction composition — cannot self-deadlock).
            # Later writers re-check under THEIR dir hold, see the file,
            # and hand off below.
            yield
            return
        # Handoff: acquire the file lock, then RELEASE the directory lock
        # before the caller's section — holding dir EX across the section
        # would falsely serialize different ledgers sharing one parent
        # directory (the audit sidecar and the state ledger share the
        # state dir). The dir→file order is preserved; the dir hold spans
        # only the acquisition.
        try:
            fcntl.flock(file_fd, fcntl.LOCK_EX)
        except BaseException:
            os.close(file_fd)
            raise
        finally:
            dir_lock.release()
            dir_held = False
        try:
            yield
        finally:
            fcntl.flock(file_fd, fcntl.LOCK_UN)
            os.close(file_fd)
    finally:
        if dir_held:
            dir_lock.release()


@contextmanager
def cross_process_read_lock(canonical_path: Path) -> Generator[None, None, None]:
    """Hold a shared same-host lock across a read, excluding a concurrent writer.

    Side-effect free (the `harness-inspect` read-only contract): never
    creates files or directories, never `mkdir`s. When the canonical file
    exists it is locked SHARED directly; when it does not, the parent
    directory is locked SHARED — excluding the absent-file-mode first
    writer — and the file is re-checked once under that lock. Only a ledger
    whose PARENT DIRECTORY does not exist yields unguarded (see module
    docstring).
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
    # Dir-first, symmetric with the writer (codex round-1 P1 on this
    # landing): a file-first fast path could open a file the CALLER of an
    # absent-file-mode writer had just created and take an uncontested
    # SHARED lock while that writer — holding only the directory lock —
    # was still mid-append. Acquiring the directory lock first blocks on
    # exactly that writer; the hold is transitional (released right after
    # the file handoff) so long reads never couple sibling ledgers.
    dir_lock = _dir_lock_for(canonical_path.parent)
    dir_lock.acquire()
    dir_held = True
    try:
        try:
            file_fd = os.open(canonical_path, os.O_RDONLY)
        except FileNotFoundError:
            # Genuinely nothing to read; the dir hold excludes an
            # absent-file-mode first writer for the caller's section.
            # (The dir lock is exclusive rather than shared — a deliberate
            # simplification: absent-file reads are the rare
            # pre-first-write window, read nothing, and the one lock kind
            # keeps the per-thread reentrancy face sound.)
            yield
            return
        try:
            fcntl.flock(file_fd, fcntl.LOCK_SH)
        except BaseException:
            os.close(file_fd)
            raise
        finally:
            dir_lock.release()
            dir_held = False
        try:
            yield
        finally:
            fcntl.flock(file_fd, fcntl.LOCK_UN)
            os.close(file_fd)
    finally:
        if dir_held:
            dir_lock.release()

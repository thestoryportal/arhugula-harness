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
indefinitely-armed pre-B-46 window. Legacy `<ledger>.lock` sibling files are NOT orphans during the
compatibility window: writers PROVISION + lock them (round-7 — an
exists-check missed a fresh pre-B-46 process creating one mid-window) and
readers lock them when present. The one transitional residual left open: a
NEW-version reader racing a FRESH old-version writer's very first sidecar
creation can take a torn read (loud parse error, never silent corruption —
the historical posture); full retirement of the legacy protocol rides the
B-45 successor arc.
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


def _legacy_lock_file_path(canonical_path: Path) -> Path:
    """The pre-B-46 sibling advisory-lock file (`<ledger>.lock`)."""
    return canonical_path.with_name(canonical_path.name + ".lock")


def _acquire_legacy_sidecar_for_writer(canonical_path: Path) -> int:
    """Writer-side legacy coordination (codex round-7 P1): writers PROVISION
    the legacy sidecar (`O_CREAT`, atomic existence) rather than
    exists-checking it — a fresh pre-B-46 process arriving mid-window could
    otherwise create + lock the sidecar our exists-check missed and append
    concurrently (forked chain). Writers may create files (they mutate the
    ledger anyway); the sidecar therefore stays provisioned for the
    compatibility window — its removal rides the B-45 successor arc that
    retires the legacy protocol entirely. Returns the locked fd."""
    import fcntl
    import stat as stat_module

    fd = os.open(
        _legacy_lock_file_path(canonical_path),
        os.O_CREAT | os.O_RDWR | getattr(os, "O_NONBLOCK", 0),
        0o600,
    )
    try:
        if not stat_module.S_ISREG(os.fstat(fd).st_mode):
            # Fail CLOSED (round-8 P2): on Linux an old B-40 writer can
            # flock a FIFO sidecar — treating it as absent would let old
            # and new writers append concurrently (forked chain). Loud
            # refusal (the enclosing handler closes the fd); the operator
            # removes the mangled sidecar.
            raise ValueError(
                f"legacy lock sidecar {_legacy_lock_file_path(canonical_path)} "
                f"is not a regular file — refusing to write without "
                f"mixed-version serialization (remove the mangled sidecar)"
            )
        fcntl.flock(fd, fcntl.LOCK_EX)
    except BaseException:
        os.close(fd)
        raise
    return fd


def _acquire_legacy_sidecar_if_present(canonical_path: Path, *, exclusive: bool) -> int:
    """Transitional mixed-version coordination (codex round-4 P1): a
    pre-B-46 process on a sibling worktree locks `<ledger>.lock`, which the
    canonical-file lock never touches — without this, old and new writers
    never contend and can fork the chain. When the legacy sidecar EXISTS on
    disk, acquire it too (same mode), ordered strictly AFTER the canonical
    file lock everywhere (old processes hold only the sidecar and none of
    our locks, so no cross-version cycle is possible). New deployments
    never create the sidecar, so this is a no-op for them; the legacy
    lazy-provisioning TOCTOU survives only for the mixed-version
    transition window it has always covered. Returns the locked fd, or -1
    when the sidecar does not exist."""
    import fcntl  # POSIX-only; callers gate win32.
    import stat as stat_module

    try:
        fd = os.open(
            _legacy_lock_file_path(canonical_path),
            os.O_RDONLY | getattr(os, "O_NONBLOCK", 0),
        )
    except FileNotFoundError:
        return -1
    try:
        if not stat_module.S_ISREG(os.fstat(fd).st_mode):
            # Fail CLOSED (round-8 P2, superseding the round-5 treat-as-
            # absent): on Linux an old writer CAN flock a FIFO sidecar, so
            # ignoring it loses mixed-version serialization. Loud refusal
            # (no hang — the open above is nonblocking; the enclosing
            # handler closes the fd).
            raise ValueError(
                f"legacy lock sidecar {_legacy_lock_file_path(canonical_path)} "
                f"is not a regular file — refusing to proceed without "
                f"mixed-version serialization (remove the mangled sidecar)"
            )
        fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
    except BaseException:
        os.close(fd)
        raise
    return fd


def _release_legacy_sidecar(fd: int) -> None:
    if fd < 0:
        return
    import fcntl

    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)


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
                # Rolling-upgrade coexistence (round-5 P1): a pre-B-46
                # writer creates + locks the legacy sidecar BEFORE
                # creating the canonical file — acquire the sidecar too
                # when present, and re-check the canonical afterwards (it
                # may have appeared while we waited on the old writer).
                legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path)
                try:
                    if canonical_path.exists():
                        continue
                    yield
                    return
                finally:
                    _release_legacy_sidecar(legacy_fd)
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
            except OSError as exc:
                import errno as errno_module

                if exc.errno == errno_module.ENOTSUP:
                    # Un-flockable object (see the reader) — the caller's
                    # validated open owns the loud rejection.
                    os.close(file_fd)
                    yield
                    return
                os.close(file_fd)
                raise
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
            # terminates in every real workload). Any verify error
            # releases the acquired lock (round-4 P2 — a raised stat must
            # not leave the fd locked until process exit).
            try:
                try:
                    path_ino = os.stat(canonical_path).st_ino
                except FileNotFoundError:
                    path_ino = -1
            except BaseException:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise
            if path_ino != os.fstat(file_fd).st_ino:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                continue
            try:
                legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path)
            except BaseException:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise
            try:
                yield
            finally:
                _release_legacy_sidecar(legacy_fd)
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
        except BaseException:
            # Round-4 P2: an unexpected open failure (unreadable target,
            # a directory at the path) must not leave the dir lock held
            # forever for every ledger in the parent.
            dir_lock.release()
            raise
        try:
            fcntl.flock(file_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # An active holder: release the dir, wait it out on the file
            # alone (ABBA rule), then retry the whole acquisition. The
            # descriptor is closed on EVERY exit (round-8 P2 — an
            # interrupted blocking flock must not leak one fd per
            # attempt).
            dir_lock.release()
            try:
                fcntl.flock(file_fd, fcntl.LOCK_EX)
                fcntl.flock(file_fd, fcntl.LOCK_UN)
            finally:
                os.close(file_fd)
            continue
        except BaseException:
            os.close(file_fd)
            dir_lock.release()
            raise
        # Hold the dir lock, the (old-inode) file lock, AND — during a
        # rolling upgrade — the legacy sidecar lock across the replacement
        # section (round-5 P1: a pre-B-46 writer holding only the sidecar
        # would otherwise append concurrently and have its rows
        # overwritten by the rewrite).
        try:
            try:
                legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path)
            except BaseException:
                # Round-6 P2: a legacy-acquisition failure must not leave
                # the canonical file lock held until process restart.
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise
            try:
                yield
            finally:
                _release_legacy_sidecar(legacy_fd)
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
            return
        finally:
            dir_lock.release()
    try:
        legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path)
        try:
            yield
        finally:
            _release_legacy_sidecar(legacy_fd)
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
                # pre-first-write window and read nothing.) Rolling
                # upgrade (round-5 P1): also wait out a legacy-sidecar
                # holder and re-check for the canonical it may have
                # created.
                legacy_fd = _acquire_legacy_sidecar_if_present(canonical_path, exclusive=False)
                try:
                    if canonical_path.exists():
                        continue
                    yield
                    return
                finally:
                    _release_legacy_sidecar(legacy_fd)
            try:
                try:
                    fcntl.flock(file_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
                except BlockingIOError:
                    # Round-2 P1 ABBA rule: never block on a file lock
                    # while holding the dir.
                    dir_lock.release()
                    dir_held = False
                    fcntl.flock(file_fd, fcntl.LOCK_SH)
            except OSError as exc:
                import errno as errno_module

                if exc.errno == errno_module.ENOTSUP:
                    # An un-flockable object (macOS raises ENOTSUP for a
                    # FIFO): the lock layer cannot serialize it and must
                    # not own the rejection either — yield unguarded and
                    # let the CALLER's validated open fail loudly with its
                    # documented not-a-regular-file error.
                    os.close(file_fd)
                    yield
                    return
                os.close(file_fd)
                raise
            except BaseException:
                os.close(file_fd)
                raise
            finally:
                if dir_held:
                    dir_lock.release()
                    dir_held = False
            # Inode-stability verify (round-3 P1) — mirror of the writer,
            # with the same leak-safe wrap (round-4 P2).
            try:
                try:
                    path_ino = os.stat(canonical_path).st_ino
                except FileNotFoundError:
                    path_ino = -1
            except BaseException:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise
            if path_ino != os.fstat(file_fd).st_ino:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                continue
            try:
                legacy_fd = _acquire_legacy_sidecar_if_present(canonical_path, exclusive=False)
            except BaseException:
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise
            try:
                yield
            finally:
                _release_legacy_sidecar(legacy_fd)
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
            return
        finally:
            if dir_held:
                dir_lock.release()

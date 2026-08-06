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

**Scope locks (U-MEM-27 Codex round-1 [P1]).** The three context managers above
serialize writers of ONE canonical file. A critical section whose read set is
discovered dynamically — a compare-and-commit that re-reads an unbounded,
caller-chosen set of source files and then writes a different one — cannot be
expressed that way: there is no single canonical file to key on, and locking the
discovered set member-by-member reintroduces a lock-ordering problem.
`cross_process_scope_lock` covers that case with one exclusive lock per
directory TREE, built on the same `_DirLock` (per-path `flock` EX + reentrant
in-process face) the file locks already use.

**Liveness deadline (B-93, ratified Reading B — hand-rolled).** Every blocking
acquisition below is bounded: a non-blocking probe plus caller-owned bounded
retry, raising `harness_core.CrossProcessLockTimeoutError` when the bound
expires. Each of the four entry surfaces mints ONE
`CrossProcessLockDeadline` and threads it through every acquisition beneath
it, so the bound is END-TO-END — an entry surface that blocks at the directory
lock, then the legacy sidecar, then the file lock spends ONE budget across all
three, and the inode-replacement retry loops cannot re-arm it. A per-site bound
would be a partial guarantee that reads as a total one. `deadline_seconds`
overrides the default per call. Windows behaviour is UNCHANGED — the carve-outs
below still `yield` before any acquisition is reached (`B-45`, deferred on
witnessability).
"""

from __future__ import annotations

import os
import sys
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from harness_core.cross_process_lock_deadline import (
    CrossProcessLockDeadline,
    CrossProcessLockTimeoutError,
    flock_until_deadline,
)

_IS_WINDOWS = sys.platform == "win32"


class _DirLock:
    """Per-PATH lock: one cross-process `flock` EX face + a per-thread
    REENTRANT in-process face.

    Named for its original and still primary target, a ledger's parent
    directory; `cross_process_scope_lock` reuses it unchanged against a
    provisioned lock FILE, which `flock` treats identically (any fd will do).

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

    def acquire(self, deadline: CrossProcessLockDeadline | None = None) -> None:
        """Acquire BOTH faces within `deadline` — the in-process one too.

        B-93 site 1 of 9. `None` mints a fresh default-budget deadline, so a
        caller outside the four entry surfaces (only the direct-construction
        tests) still gets a bound rather than the pre-B-93 indefinite block.

        **BOTH faces are bounded, and an earlier draft of this arc bounded only
        the flock** (out-of-family review round 2 [P1], accepted). That draft
        argued the `RLock` needed no bound because a same-process holder is
        either this very thread (reentrant, returns immediately) or a thread
        whose own flock acquisition is already bounded. **The second half is a
        non-sequitur:** bounding how long a holder WAITED says nothing about how
        long it HOLDS — and a long hold is the exact harm this row registers.
        `write_record_guarded` keeps this lock across a caller-supplied
        precondition, so an in-process sibling thread running a slow precondition
        wedged every waiter here, BEFORE the bounded `flock` was ever reached,
        with the victim-side bound advertised and not delivered.

        The `RLock` therefore takes the deadline's REMAINING time (never
        negative — `acquire` rejects that) and raises the same typed error on
        expiry. An UNCONTENDED or REENTRANT acquisition still succeeds with a
        zero remaining budget, matching `flock_until_deadline`'s own contract:
        the bound is on WAITING, not on acquiring.
        """
        resolved = deadline or CrossProcessLockDeadline.starting_now()
        # `threading.TIMEOUT_MAX` cap (out-of-family review round 5 [P3],
        # accepted): `RLock.acquire` raises `OverflowError` for a timeout above
        # it, so a FINITE, POSITIVE, validation-passing budget like `1e20` blew
        # up here BEFORE any lock was attempted — on every `harness-is` entry
        # surface. Capped at the CONSUMER rather than refused at the deadline,
        # because `TIMEOUT_MAX` is a limit of THIS lock primitive and
        # `harness-core`'s deadline type has no business knowing about
        # `threading`. The cap is semantically free: it is ~292 years, so a
        # capped wait that expires has outlived any budget a caller meant.
        rlock_timeout = min(max(resolved.remaining_seconds(), 0.0), threading.TIMEOUT_MAX)
        if not self._rlock.acquire(blocking=False):
            # Contended at the IN-PROCESS face. Recorded on the deadline before
            # waiting (round 10 [P2]) so a LATER, FREE acquisition under the same
            # entry surface cannot slip through its own first-probe exemption
            # after this wait has spent the budget.
            resolved.note_contention()
            if not self._rlock.acquire(timeout=rlock_timeout):
                raise CrossProcessLockTimeoutError(
                    lock_target=str(self._path),
                    budget_seconds=resolved.budget_seconds,
                )
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
                import fcntl  # POSIX-only; callers gate win32.

                flock_until_deadline(
                    self._fd,
                    fcntl.LOCK_EX,
                    # `resolved`, NOT a fresh mint (out-of-family review round 3
                    # [P3], accepted). Re-minting here gave the two faces
                    # SEPARATE budgets whenever `deadline` was None: an
                    # in-process holder could consume nearly the whole default
                    # and a cross-process holder the whole of another — twice
                    # the bound this method's own docstring promises. The
                    # end-to-end contract has to hold WITHIN a site, not only
                    # across sites.
                    deadline=resolved,
                    lock_target=str(self._path),
                )
            except BaseException:
                os.close(self._fd)
                self._fd = -1
                self._rlock.release()
                raise
        self._refcount += 1

    def release(self) -> None:
        import fcntl

        # Mirror of `acquire`'s discipline on the way out: a raising `flock`
        # (LOCK_UN on a vanished mount, EBADF) must not skip the `os.close` or,
        # worse, leave the RLock held forever - the shared in-process face would
        # be permanently wedged for every other thread on this path.
        try:
            self._refcount -= 1
            if self._refcount == 0:
                fd, self._fd = self._fd, -1
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                finally:
                    os.close(fd)
        finally:
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


SCOPE_LOCK_FILENAME = ".cross-process-scope.lock"
"""Provisioned lock target for `cross_process_scope_lock`, one per scope root.

A dedicated file rather than the scope directory itself: a directory inode is
already the `_DirLock` target of every canonical-file lock under it, so locking
it here would couple scope holders to unrelated ledger writers in the same
directory. It is a LOCK file, never a canonical one — it carries no bytes and
nothing reads it.
"""


@contextmanager
def cross_process_scope_lock(
    scope_root: Path, *, deadline_seconds: float | None = None
) -> Generator[None, None, None]:
    """Hold an exclusive same-host lock over a whole directory TREE.

    The coarse sibling of `cross_process_write_lock`, for a critical section
    whose file set is not known when the lock is taken: a compare-and-commit
    that re-reads a caller-chosen set of source files and then writes a
    different one. One lock per `scope_root` serializes every such section
    against every other, and against any writer in the tree that takes the same
    scope lock — which is the discipline the tree's writers must adopt for the
    guarantee to mean anything (a writer outside it is simply unserialized).

    REENTRANT per thread, so a guarded section may call through the tree's own
    write path (which re-takes this lock) without self-deadlock; other threads
    and other OS processes still block. Provisioning the lock file is
    `O_CREAT`-idempotent, so concurrent first callers converge on one inode.

    Same-host only, and a no-op on Windows — identical posture to this module's
    file locks (see the module docstring and the B-45 register row).

    **B-93 — bounded.** `deadline_seconds` bounds the acquisition; expiry raises
    `harness_core.CrossProcessLockTimeoutError` and the section is NOT entered.
    This is the entry surface carrying the exposure the row registers:
    `CanonicalMemoryStore.write_record_guarded` holds this lock across a
    caller-supplied precondition callable, so the next precondition author gets
    a bounded failure with a named lock target instead of a silent host-wide
    wedge.
    """
    if _IS_WINDOWS:
        yield
        return

    deadline = CrossProcessLockDeadline.starting_now(deadline_seconds)
    scope_root.mkdir(parents=True, exist_ok=True)
    lock_file = scope_root / SCOPE_LOCK_FILENAME
    open_flags = os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    os.close(os.open(lock_file, open_flags, 0o600))
    lock = _dir_lock_for(lock_file)
    lock.acquire(deadline)
    try:
        yield
    finally:
        lock.release()


def _legacy_lock_file_path(canonical_path: Path) -> Path:
    """The pre-B-46 sibling advisory-lock file (`<ledger>.lock`)."""
    return canonical_path.with_name(canonical_path.name + ".lock")


def _acquire_legacy_sidecar_for_writer(
    canonical_path: Path, *, deadline: CrossProcessLockDeadline
) -> int:
    """Writer-side legacy coordination (codex round-7 P1): writers PROVISION
    the legacy sidecar (`O_CREAT`, atomic existence) rather than
    exists-checking it — a fresh pre-B-46 process arriving mid-window could
    otherwise create + lock the sidecar our exists-check missed and append
    concurrently (forked chain). Writers may create files (they mutate the
    ledger anyway); the sidecar therefore stays provisioned for the
    compatibility window — its removal rides the B-45 successor arc that
    retires the legacy protocol entirely. Returns the locked fd.

    B-93 site 2 of 9. `deadline` is the CALLER's end-to-end budget, already
    partly spent on the directory (and possibly the canonical-file) lock — this
    acquisition gets what remains of it, never a fresh one."""
    import fcntl
    import stat as stat_module

    open_flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NONBLOCK", 0)
    if not _IS_WINDOWS:
        # O_NOFOLLOW (round-9 P2): a symlink sidecar — including a
        # dangling one O_CREAT would otherwise materialize as the
        # CANONICAL file — fails loud with ELOOP.
        open_flags |= os.O_NOFOLLOW
    fd = os.open(_legacy_lock_file_path(canonical_path), open_flags, 0o600)
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
        sidecar_stat = os.fstat(fd)
        try:
            canonical_stat = os.stat(canonical_path)
        except FileNotFoundError:
            canonical_stat = None
        if canonical_stat is not None and (
            sidecar_stat.st_dev == canonical_stat.st_dev
            and sidecar_stat.st_ino == canonical_stat.st_ino
        ):
            # Alias check (round-9 P2): a hard link to the canonical file
            # passes S_ISREG but self-deadlocks on the inode this process
            # already holds LOCK_EX on. Loud refusal, no hang.
            raise ValueError(
                f"legacy lock sidecar {_legacy_lock_file_path(canonical_path)} "
                f"aliases the canonical ledger — refusing (remove the "
                f"mangled sidecar)"
            )
        flock_until_deadline(
            fd,
            fcntl.LOCK_EX,
            deadline=deadline,
            lock_target=str(_legacy_lock_file_path(canonical_path)),
        )
    except BaseException:
        os.close(fd)
        raise
    return fd


def _acquire_legacy_sidecar_if_present(
    canonical_path: Path, *, exclusive: bool, deadline: CrossProcessLockDeadline
) -> int:
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
    when the sidecar does not exist.

    B-93 site 3 of 9 — the one bounded acquisition that can be SHARED
    (`exclusive=False`); `LOCK_SH` is deadline-bounded exactly as `LOCK_EX` is,
    since a shared waiter is blocked by an exclusive holder just as
    indefinitely. `deadline` is the caller's remaining end-to-end budget."""
    import fcntl  # POSIX-only; callers gate win32.
    import stat as stat_module

    open_flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
    if not _IS_WINDOWS:
        open_flags |= os.O_NOFOLLOW  # round-9 P2 — symlink sidecar fails loud
    try:
        fd = os.open(_legacy_lock_file_path(canonical_path), open_flags)
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
        sidecar_stat = os.fstat(fd)
        try:
            canonical_stat = os.stat(canonical_path)
        except FileNotFoundError:
            canonical_stat = None
        if canonical_stat is not None and (
            sidecar_stat.st_dev == canonical_stat.st_dev
            and sidecar_stat.st_ino == canonical_stat.st_ino
        ):
            # Alias check (round-9 P2) — see the writer helper.
            raise ValueError(
                f"legacy lock sidecar {_legacy_lock_file_path(canonical_path)} "
                f"aliases the canonical ledger — refusing (remove the "
                f"mangled sidecar)"
            )
        flock_until_deadline(
            fd,
            fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH,
            deadline=deadline,
            lock_target=str(_legacy_lock_file_path(canonical_path)),
        )
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
def cross_process_write_lock(
    canonical_path: Path, *, deadline_seconds: float | None = None
) -> Generator[None, None, None]:
    """Hold an exclusive same-host lock across a read-prior -> append critical section.

    Callers still hold their own in-process `threading.Lock` around the same
    section (unchanged) — this lock adds the cross-process dimension the
    thread lock cannot provide. The lock NEVER creates the canonical file:
    when it does not exist yet, the parent-directory lock is held for the
    whole section and the caller's own append creates the file inside it
    (preserving "file existence == a real append happened" for the audit
    writer's absence guard).

    **B-93 — bounded END-TO-END.** `deadline_seconds` is ONE budget spanning
    every acquisition this surface performs: the directory lock, the legacy
    sidecar, and the canonical-file lock (up to three in sequence), INCLUDING
    across the inode-replacement retry loop below — which is why the deadline is
    minted once, outside the loop, and never re-armed. Expiry raises
    `harness_core.CrossProcessLockTimeoutError`; the section is NOT entered and
    no append happens.
    """
    if _IS_WINDOWS:
        yield
        return
    import fcntl  # POSIX-only; never reached on Windows.

    deadline = CrossProcessLockDeadline.starting_now(deadline_seconds)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        dir_lock = _dir_lock_for(canonical_path.parent)
        dir_lock.acquire(deadline)
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
                legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path, deadline=deadline)
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
                    # B-93 site 4 of 9. The ABBA handoff is PRESERVED exactly:
                    # the dir lock is released FIRST, and only then is the file
                    # lock waited on — now bounded rather than indefinite.
                    flock_until_deadline(
                        file_fd,
                        fcntl.LOCK_EX,
                        deadline=deadline,
                        lock_target=str(canonical_path),
                        contention_observed=True,
                    )
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
            # B-93 (out-of-family review, merge-gate fix round 2): the manual
            # probe above can SUCCEED without ever calling
            # `flock_until_deadline`, so a caller that already waited at the
            # directory lock could enter here on a SPENT budget through a path
            # the helper never sees. Release and refuse — the same rule the
            # helper applies to its own late retries.
            if deadline.refuse_after_acquire():
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise CrossProcessLockTimeoutError(
                    lock_target=str(canonical_path),
                    budget_seconds=deadline.budget_seconds,
                )
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
                legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path, deadline=deadline)
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
def cross_process_replace_lock(
    canonical_path: Path, *, deadline_seconds: float | None = None
) -> Generator[None, None, None]:
    """Hold EXCLUSION for a section that REPLACES the canonical file's inode
    (shadow-git rollback's `git checkout` + `write_bytes`).

    Holds the parent-directory lock for the WHOLE section — the directory
    is the only inode-stable target across replacement — and additionally
    waits out any active file-lock holder first (non-blocking probe, then
    release-dir-and-block-and-retry per the round-2 ABBA rule). New
    writers/readers block at their transitional dir acquisition for the
    section's duration; stragglers that locked the pre-replacement inode
    are caught by the acquisition-side inode verify and retry.

    **B-93 — bounded END-TO-END.** One `deadline_seconds` budget spans the
    directory lock, the wait-out of an active file holder, and the legacy
    sidecar — across every turn of the wait-out retry loop, which is why the
    deadline is minted before it. Expiry raises
    `harness_core.CrossProcessLockTimeoutError` and no inode is replaced.
    """
    if _IS_WINDOWS:
        yield
        return
    import fcntl  # POSIX-only; never reached on Windows.

    deadline = CrossProcessLockDeadline.starting_now(deadline_seconds)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    dir_lock = _dir_lock_for(canonical_path.parent)
    while True:
        dir_lock.acquire(deadline)
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
                # B-93 site 5 of 9. ABBA PRESERVED — the dir lock is released
                # above, before this wait; the wait is now bounded, and the
                # bound spans every turn of the enclosing retry loop.
                flock_until_deadline(
                    file_fd,
                    fcntl.LOCK_EX,
                    deadline=deadline,
                    lock_target=str(canonical_path),
                    contention_observed=True,
                )
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
        # B-93 (merge-gate fix round 2): same post-acquire rule as the other two
        # arms — the non-blocking probe above can succeed on a spent budget when
        # this caller already waited at the directory lock.
        if deadline.refuse_after_acquire():
            fcntl.flock(file_fd, fcntl.LOCK_UN)
            os.close(file_fd)
            dir_lock.release()
            raise CrossProcessLockTimeoutError(
                lock_target=str(canonical_path),
                budget_seconds=deadline.budget_seconds,
            )
        try:
            try:
                legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path, deadline=deadline)
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
        legacy_fd = _acquire_legacy_sidecar_for_writer(canonical_path, deadline=deadline)
        try:
            yield
        finally:
            _release_legacy_sidecar(legacy_fd)
    finally:
        dir_lock.release()


@contextmanager
def cross_process_read_lock(
    canonical_path: Path, *, deadline_seconds: float | None = None
) -> Generator[None, None, None]:
    """Hold a shared same-host lock across a read, excluding a concurrent writer.

    Side-effect free (the `harness-inspect` read-only contract): never
    creates files or directories, never `mkdir`s. Dir-first, symmetric
    with the writer (codex round-1 P1): a file-first fast path could open
    a file an absent-file-mode writer's caller had just created and take
    an uncontested SHARED lock mid-append. Only a ledger whose PARENT
    DIRECTORY does not exist yields unguarded (see module docstring).

    **B-93 — bounded END-TO-END.** One `deadline_seconds` budget spans the
    directory lock, the shared file lock and the legacy sidecar, across the
    inode-replacement retry loop. Bounding the READ path matters as much as the
    write path: a shared waiter is blocked by an exclusive holder just as
    indefinitely, and `harness-inspect` is an interactive surface.
    """
    if _IS_WINDOWS:
        yield
        return
    import fcntl  # POSIX-only; never reached on Windows.

    deadline = CrossProcessLockDeadline.starting_now(deadline_seconds)
    if not canonical_path.parent.exists():
        # No parent directory: nothing to read AND no bootstrapped
        # deployment to race — the documented residual window. (Readers
        # never mkdir; the harness-inspect read-only contract.)
        yield
        return
    while True:
        dir_lock = _dir_lock_for(canonical_path.parent)
        dir_lock.acquire(deadline)
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
                legacy_fd = _acquire_legacy_sidecar_if_present(
                    canonical_path, exclusive=False, deadline=deadline
                )
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
                    # B-93 site 6 of 9 — the only SHARED site of the nine.
                    # ABBA PRESERVED: dir released above, then the bounded wait.
                    flock_until_deadline(
                        file_fd,
                        fcntl.LOCK_SH,
                        deadline=deadline,
                        lock_target=str(canonical_path),
                        contention_observed=True,
                    )
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
            # B-93 (out-of-family review, merge-gate fix round 2): the manual
            # probe above can SUCCEED without ever calling
            # `flock_until_deadline`, so a caller that already waited at the
            # directory lock could enter here on a SPENT budget through a path
            # the helper never sees. Release and refuse — the same rule the
            # helper applies to its own late retries.
            if deadline.refuse_after_acquire():
                fcntl.flock(file_fd, fcntl.LOCK_UN)
                os.close(file_fd)
                raise CrossProcessLockTimeoutError(
                    lock_target=str(canonical_path),
                    budget_seconds=deadline.budget_seconds,
                )
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
                legacy_fd = _acquire_legacy_sidecar_if_present(
                    canonical_path, exclusive=False, deadline=deadline
                )
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

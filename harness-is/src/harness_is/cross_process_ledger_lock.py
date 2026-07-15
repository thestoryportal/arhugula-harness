"""Cross-process advisory lock for ledger writers (B-40, C-IS-09 §9.3 / C-MEM-08).

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
Windows sits at exact pre-B-40 parity (the in-process `threading.Lock`
callers already hold around the same critical sections is unaffected and is
cross-platform; only the *cross-process* dimension this module adds is
unavailable). This is a registered gap, not a silent one — see the B-40
follow-on forward-register row for genuine cross-platform locking (also
covers the identical POSIX-only-`fcntl` gap already shipped at
`harness_runtime.lifecycle.reconciler_pause_resume_substrate`).
"""

from __future__ import annotations

import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from enum import Enum, auto
from pathlib import Path

_IS_WINDOWS = sys.platform == "win32"


class _LockKind(Enum):
    """Platform-neutral stand-in for `fcntl.LOCK_EX` / `fcntl.LOCK_SH` — the
    real POSIX constants are resolved locally inside `_flock`, which is never
    reached on Windows (see the module docstring)."""

    EXCLUSIVE = auto()
    SHARED = auto()


def _lock_file_path(canonical_path: Path) -> Path:
    """The sibling advisory-lock file for a canonical ledger path."""
    return canonical_path.with_name(canonical_path.name + ".lock")


@contextmanager
def _flock(canonical_path: Path, kind: _LockKind, open_flags: int) -> Generator[None, None, None]:
    if _IS_WINDOWS:
        # No same-host advisory-lock primitive wired for Windows yet (see the
        # module docstring) — degrade to a no-op rather than fail the import
        # or the call. Pre-B-40 parity: cross-process serialization is simply
        # unavailable on this platform, same as before this module existed.
        yield
        return
    import fcntl  # POSIX-only; module load never reaches here on Windows.

    mode = fcntl.LOCK_EX if kind is _LockKind.EXCLUSIVE else fcntl.LOCK_SH
    lock_path = _lock_file_path(canonical_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, open_flags, 0o600)
    try:
        fcntl.flock(fd, mode)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


@contextmanager
def cross_process_write_lock(canonical_path: Path) -> Generator[None, None, None]:
    """Hold an exclusive same-host lock across a read-prior -> append critical section.

    Callers still hold their own in-process `threading.Lock` around the same
    section (unchanged) — this lock adds the cross-process dimension the
    thread lock cannot provide.
    """
    with _flock(canonical_path, _LockKind.EXCLUSIVE, os.O_CREAT | os.O_RDWR):
        yield


@contextmanager
def cross_process_read_lock(canonical_path: Path) -> Generator[None, None, None]:
    """Hold a shared same-host lock across a read, excluding a concurrent writer.

    Blocks only while a writer holds `cross_process_write_lock` on the same
    path, closing the torn/partial-line read race against a concurrent append.

    Opens the lock sidecar read-only (`O_RDONLY`), and WITHOUT `O_CREAT` when
    the sidecar already exists: `flock`'s locking semantics are independent
    of the fd's read/write mode or creation flags (POSIX `flock`, unlike
    byte-range `fcntl` locks, doesn't check open-mode permissions), and a
    pure reader never writes to the lock file — a genuinely read-only open
    preserves callers' own write-nothing guarantees (e.g. `harness-inspect`'s
    read-only-CLI invariant, which a blanket `O_CREAT` would otherwise trip
    even when it creates nothing). `O_CREAT` is only used as a fallback for
    the rare first-ever read of a ledger no writer has touched yet.
    """
    lock_path = _lock_file_path(canonical_path)
    if lock_path.exists():
        with _flock(canonical_path, _LockKind.SHARED, os.O_RDONLY):
            yield
    else:
        with _flock(canonical_path, _LockKind.SHARED, os.O_CREAT | os.O_RDONLY):
            yield

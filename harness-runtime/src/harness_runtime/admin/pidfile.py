"""Pidfile IPC primitive — U-RT-48 (C-RT-13).

Per `Spec_Harness_Runtime_v1.md` v1.1 §13:

> Pidfile lifecycle. The harness writes its pidfile at stage 7
> INGRESS_ACCEPT and removes it at the end of `shutdown()`. Pidfile
> contents are the pid only. Stale pidfiles (process not running) surface
> as `harness-shutdown` typed error.

**Atomicity.** Writes go to `<path>.tmp` then `os.replace(tmp, path)` —
atomic on POSIX. A crashed mid-write leaves either no file or the
*previous* valid pidfile (if any), never a truncated number that
`harness-shutdown` would parse as a different PID.

**Default location.** `RuntimeConfig.repository_root / ".harness/runtime.pid"`.
Configurable via `RuntimeConfig.pidfile_path` (optional override per spec
§13 deferred-to-discretion).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness_runtime.types import RuntimeConfig

__all__ = [
    "DEFAULT_PIDFILE_BASENAME",
    "PidfileError",
    "claim_pidfile",
    "default_pidfile_path",
    "pid_is_alive",
    "read_pidfile",
    "release_pidfile",
    "remove_pidfile",
    "resolve_pidfile_path",
    "write_pidfile",
]


DEFAULT_PIDFILE_BASENAME = Path(".harness/runtime.pid")


class PidfileError(Exception):
    """`RT-FAIL-ADMIN-PIDFILE` — pidfile missing / unreadable / unparseable.

    Used by `harness-shutdown` to surface stale-pidfile and parse errors
    as a typed error class. Subclasses `Exception` (not `OSError`) so
    callers can distinguish "pidfile contract violation" from "OS-level
    error during the read."
    """


def default_pidfile_path(repository_root: Path) -> Path:
    """Default pidfile location for a given repository root."""
    return repository_root / DEFAULT_PIDFILE_BASENAME


def resolve_pidfile_path(config: RuntimeConfig) -> Path:
    """Resolve the pidfile path from a `RuntimeConfig`.

    Returns `config.pidfile_path` if set; otherwise the default
    (`repository_root / ".harness/runtime.pid"`).
    """
    if config.pidfile_path is not None:
        return config.pidfile_path
    return default_pidfile_path(config.repository_root)


def write_pidfile(path: Path, pid: int) -> None:
    """Atomically write `pid` to `path`.

    Per spec §13 "Pidfile contents are the pid only" — single line, no
    trailing whitespace beyond a single newline. Atomic via `tmp + replace`.

    Creates `path.parent` if missing (idempotent).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(f"{pid}\n")
    os.replace(tmp, path)


def pid_is_alive(pid: int) -> bool:
    """True iff `pid` is a live process this user may signal (`os.kill(pid, 0)`).

    `ProcessLookupError` is a dead or recycled pid; `PermissionError` is another user's
    process, which this harness never owns, so both read as not ours and not alive.
    """
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _recorded_pid(path: Path) -> int | None:
    """The pid a well-formed pidfile names, else None (missing or malformed)."""
    try:
        return read_pidfile(path)
    except PidfileError:
        return None


def claim_pidfile(path: Path, pid: int) -> bool:
    """Write `pid` unless the pidfile names another live process; True iff written.

    The pidfile names ONE live harness process under a repository root. A daemon and a
    one-shot run share the root, so a second process that overwrote the file would make
    `harness-shutdown` lose the first. A file naming a dead pid is stale and is claimed.

    [LAW:single-enforcer] Ownership is decided here and released in `release_pidfile`;
    callers never compare pids themselves.
    """
    recorded = _recorded_pid(path)
    if recorded is not None and recorded != pid and pid_is_alive(recorded):
        return False
    write_pidfile(path, pid)
    return True


def release_pidfile(path: Path, pid: int) -> bool:
    """Remove the pidfile iff it names `pid`; True iff removed or already absent.

    A process that did not win the claim leaves the owner's file in place.
    """
    recorded = _recorded_pid(path)
    if recorded is not None and recorded != pid:
        return False
    remove_pidfile(path)
    return True


def read_pidfile(path: Path) -> int:
    """Read and parse the pidfile.

    Raises
    ------
    PidfileError
        File missing, unreadable, or content not a valid integer.
    """
    try:
        text = path.read_text()
    except FileNotFoundError as exc:
        raise PidfileError(f"pidfile not found: {path}") from exc
    except OSError as exc:
        raise PidfileError(f"pidfile unreadable: {path}: {exc}") from exc

    stripped = text.strip()
    if not stripped:
        raise PidfileError(f"pidfile empty: {path}")
    try:
        return int(stripped)
    except ValueError as exc:
        raise PidfileError(f"pidfile content not an integer: {path}: {stripped!r}") from exc


def remove_pidfile(path: Path) -> None:
    """Best-effort pidfile removal.

    Per spec §13 lifecycle: "removes it at the end of `shutdown()`."
    Idempotent — `FileNotFoundError` is swallowed (second `shutdown()`
    call, or operator pre-cleanup).

    OS-level errors other than missing-file propagate so callers can
    record them in their failure report.
    """
    try:
        path.unlink()
    except FileNotFoundError:
        return

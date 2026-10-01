"""Landlock exec launcher for the Codex read boundary (Runtime v1.135 C-RT-05).

Run as ``<interpreter> -I -S <this file> <spec json> -- <target argv>``. In ONE thread and
before any other thread exists it closes every inherited descriptor, verifies the pinned
executable through an open descriptor, restricts itself with a deny-by-default Landlock
ruleset, sets no-new-privs and executes that same descriptor. Every failure prints one
``REFUSAL_MARKER`` line on stderr and exits ``REFUSAL_EXIT`` without running the target:
there is no unrestricted fallback.

The launcher is the single enforcer of what a grant may be. Each allowance is opened
once; that descriptor must still name the declared canonical path, and its inode must not
be (or contain) a protected root, nor be, contain or lie inside a sealed root. The rule is
then added to that same descriptor, so the object checked is the object granted.

Standard library only, so the launcher can run with ``-I -S`` and import nothing from the
harness; the runtime imports the same module for the pure `build_ruleset_spec`, so the
production runner and the source canaries share one ruleset definition.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import platform
import stat
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

__all__ = [
    "DEFAULT_DEVICES",
    "LAUNCHER_PATH",
    "MIN_ABI",
    "REFUSAL_EXIT",
    "REFUSAL_MARKER",
    "LauncherRefusalError",
    "RulesetSpec",
    "build_ruleset_spec",
    "handled_access_fs",
    "launcher_argv",
    "require_supported_abi",
]

LAUNCHER_PATH = Path(__file__).resolve()
REFUSAL_EXIT = 125
REFUSAL_MARKER = "arhugula-read-boundary-refused:"
MIN_ABI = 9
"""`LANDLOCK_ACCESS_FS_RESOLVE_UNIX` (pathname-socket lookups) arrived in ABI 9."""

DEFAULT_DEVICES = ("/dev/null", "/dev/urandom")

# landlock_create_ruleset / add_rule / restrict_self share these numbers on every
# architecture using the generic syscall table, which includes both supported ones.
_SUPPORTED_MACHINES = frozenset({"aarch64", "x86_64"})
_SYS_CREATE_RULESET, _SYS_ADD_RULE, _SYS_RESTRICT_SELF = 444, 445, 446
_SYS_CLOSE_RANGE = 436
_CLOSE_RANGE_MAX = 0xFFFFFFFF
_CREATE_RULESET_VERSION = 1
_RULE_PATH_BENEATH = 1
_PR_SET_NO_NEW_PRIVS = 38

# Filesystem access rights (linux/landlock.h).
_EXECUTE, _WRITE_FILE, _READ_FILE, _READ_DIR = 1 << 0, 1 << 1, 1 << 2, 1 << 3
_REMOVE_DIR, _REMOVE_FILE, _MAKE_DIR, _MAKE_REG = 1 << 4, 1 << 5, 1 << 7, 1 << 8
_REFER, _TRUNCATE, _IOCTL_DEV, _RESOLVE_UNIX = 1 << 13, 1 << 14, 1 << 15, 1 << 16
_SCOPE_ABSTRACT_UNIX_SOCKET, _SCOPE_SIGNAL = 1 << 0, 1 << 1

_RIGHTS_SINCE_ABI = (
    (1, (1 << 13) - 1),
    (2, _REFER),
    (3, _TRUNCATE),
    (5, _IOCTL_DEV),
    (9, _RESOLVE_UNIX),
)

_EXECUTABLE_RIGHTS = _EXECUTE | _READ_FILE
_READ_ONLY_FILE_RIGHTS = _READ_FILE
_READ_ONLY_DIR_RIGHTS = _READ_FILE | _READ_DIR
_DEVICE_RIGHTS = _READ_FILE | _WRITE_FILE
_READ_WRITE_DIR_RIGHTS = (
    _READ_FILE
    | _READ_DIR
    | _WRITE_FILE
    | _TRUNCATE
    | _MAKE_REG
    | _MAKE_DIR
    | _REMOVE_FILE
    | _REMOVE_DIR
    | _REFER
)

SYSTEM_PROTECTED_ROOTS = ("/usr", "/home", "/root", "/etc", "/run/user", "/var", "/tmp", "/sys")
"""No grant may be or contain these (nor, through them, ``/`` and ``/run``)."""
SYSTEM_SEALED_ROOTS = ("/proc",)
"""No grant may be, contain or lie inside these."""


class LauncherRefusalError(Exception):
    """The boundary cannot be established; the target must not run."""


def handled_access_fs(abi: int) -> int:
    """Every filesystem right this launcher knows that the ABI can handle (deny-by-default)."""
    mask = 0
    for since, rights in _RIGHTS_SINCE_ABI:
        if abi >= since:
            mask |= rights
    return mask


def require_supported_abi(query: Callable[[], int]) -> int:
    """Return the Landlock ABI, or refuse an unsupported architecture, kernel or ABI.

    ``query`` returns the ABI version, or ``-errno`` when the kernel refuses the query.
    """
    machine = platform.machine()
    if machine not in _SUPPORTED_MACHINES:
        raise LauncherRefusalError(f"Landlock syscalls unverified on architecture {machine!r}")
    abi = query()
    if abi < 0:
        raise LauncherRefusalError(f"Landlock unavailable: {errno.errorcode.get(-abi, str(-abi))}")
    if abi < MIN_ABI:
        raise LauncherRefusalError(f"Landlock ABI {abi} < required {MIN_ABI}")
    return abi


@dataclass(frozen=True, slots=True)
class RulesetSpec:
    """Exactly what the launched process may touch; everything else is denied."""

    executable: str
    executable_sha256: str
    read_write_dirs: tuple[str, ...]
    read_only_paths: tuple[str, ...]
    devices: tuple[str, ...] = DEFAULT_DEVICES
    executable_paths: tuple[str, ...] = ()
    """Extra FILES the target may execute (e.g. a dynamic ELF loader). Empty for the
    static Codex binary; never a directory."""
    protected_roots: tuple[str, ...] = ()
    """Operator roots no grant may be or contain (the operator HOME)."""
    sealed_roots: tuple[str, ...] = ()
    """Operator roots no grant may be, contain or lie inside (the interactive Codex home)."""

    def to_json(self) -> str:
        return json.dumps(
            {
                "executable": self.executable,
                "executable_sha256": self.executable_sha256,
                "read_write_dirs": list(self.read_write_dirs),
                "read_only_paths": list(self.read_only_paths),
                "devices": list(self.devices),
                "executable_paths": list(self.executable_paths),
                "protected_roots": list(self.protected_roots),
                "sealed_roots": list(self.sealed_roots),
            },
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, text: str) -> RulesetSpec:
        raw = json.loads(text)
        return cls(
            executable=raw["executable"],
            executable_sha256=raw["executable_sha256"],
            read_write_dirs=tuple(raw["read_write_dirs"]),
            read_only_paths=tuple(raw["read_only_paths"]),
            devices=tuple(raw["devices"]),
            executable_paths=tuple(raw["executable_paths"]),
            protected_roots=tuple(raw["protected_roots"]),
            sealed_roots=tuple(raw["sealed_roots"]),
        )


def build_ruleset_spec(
    *,
    executable: str,
    executable_sha256: str,
    read_write_dirs: Sequence[str],
    read_only_paths: Sequence[str],
    executable_paths: Sequence[str] = (),
    protected_roots: Sequence[str] = (),
    sealed_roots: Sequence[str] = (),
) -> RulesetSpec:
    """Parse and freeze one boundary's shape: absolute paths and a hex pin.

    What a grant may *be* is decided by the launcher on the descriptor it grants
    (`_grant_descriptor`), never here on strings that a symlink can redirect.
    """
    # [LAW:single-enforcer] grant safety lives only in the launcher, bound to the inode.
    paths = (executable, *read_write_dirs, *read_only_paths, *executable_paths)
    for path in (*paths, *protected_roots, *sealed_roots):
        if not os.path.isabs(path):
            raise ValueError(f"boundary path must be absolute: {path!r}")
    if len(executable_sha256) != 64 or set(executable_sha256) - set("0123456789abcdef"):
        raise ValueError("executable_sha256 must be 64 lowercase hex characters")
    return RulesetSpec(
        executable=executable,
        executable_sha256=executable_sha256,
        read_write_dirs=tuple(read_write_dirs),
        read_only_paths=tuple(read_only_paths),
        executable_paths=tuple(executable_paths),
        protected_roots=tuple(protected_roots),
        sealed_roots=tuple(sealed_roots),
    )


def launcher_argv(spec: RulesetSpec, target_argv: Sequence[str]) -> tuple[str, ...]:
    """The argv that runs ``target_argv`` (argv[0] included) under ``spec``."""
    interpreter = os.path.realpath(sys.executable)
    return (interpreter, "-I", "-S", str(LAUNCHER_PATH), spec.to_json(), "--", *target_argv)


# --- the launcher itself (runs only inside the disposable child) --------------------------


class _RulesetAttr(ctypes.Structure):
    _fields_ = (
        ("handled_access_fs", ctypes.c_uint64),
        ("handled_access_net", ctypes.c_uint64),
        ("scoped", ctypes.c_uint64),
    )


class _PathBeneathAttr(ctypes.Structure):
    _pack_ = 1
    _fields_ = (("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32))


def _libc() -> ctypes.CDLL:
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    return libc


def _query_abi() -> int:
    result = _libc().syscall(
        ctypes.c_long(_SYS_CREATE_RULESET),
        None,
        ctypes.c_size_t(0),
        ctypes.c_uint32(_CREATE_RULESET_VERSION),
    )
    return int(result) if result >= 0 else -ctypes.get_errno()


def _checked(result: int, what: str) -> int:
    if result < 0:
        code = ctypes.get_errno()
        raise LauncherRefusalError(f"{what} failed: {errno.errorcode.get(code, str(code))}")
    return result


def _close_inherited_descriptors(libc: ctypes.CDLL) -> None:
    # [LAW:verifiable-goals] every descriptor >= 3, whatever RLIMIT_NOFILE says now.
    _checked(
        libc.syscall(
            ctypes.c_long(_SYS_CLOSE_RANGE),
            ctypes.c_uint(3),
            ctypes.c_uint(_CLOSE_RANGE_MAX),
            ctypes.c_uint(0),
        ),
        "close_range",
    )


def _identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _root_identities(paths: Iterable[str | Path]) -> set[tuple[int, int]]:
    """Identities of the existing ``paths`` (an absent root exposes nothing)."""
    found: set[tuple[int, int]] = set()
    for path in paths:
        try:
            found.add(_identity(os.stat(path)))
        except FileNotFoundError:
            pass
    return found


def _lineage(path: str) -> set[tuple[int, int]]:
    """Identities of ``path`` and each of its existing ancestors."""
    resolved = Path(os.path.realpath(path))
    return _root_identities((resolved, *resolved.parents))


@dataclass(frozen=True, slots=True)
class _GrantPolicy:
    """Inode identities a grant must avoid, fixed once before any rule is added."""

    exposes: frozenset[tuple[int, int]]
    """Protected and sealed roots plus every ancestor: a grant here exposes a root."""
    sealed: frozenset[tuple[int, int]]
    """Sealed roots themselves: a grant whose lineage meets one lies inside it."""

    @classmethod
    def of(cls, spec: RulesetSpec) -> _GrantPolicy:
        roots = (*SYSTEM_PROTECTED_ROOTS, *spec.protected_roots, *SYSTEM_SEALED_ROOTS)
        sealed = (*SYSTEM_SEALED_ROOTS, *spec.sealed_roots)
        exposes: set[tuple[int, int]] = set()
        for root in (*roots, *spec.sealed_roots):
            exposes |= _lineage(root)
        return cls(frozenset(exposes), frozenset(_root_identities(sealed)))


def _grant_descriptor(path: str, flags: int, policy: _GrantPolicy) -> int:
    """Open ``path`` once and return that descriptor only if it is a safe grant."""
    try:
        fd = os.open(path, flags | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise LauncherRefusalError(
            f"allowed path unusable ({errno.errorcode.get(exc.errno or 0)}): {path}"
        ) from exc
    actual, info = os.readlink(f"/proc/self/fd/{fd}"), os.fstat(fd)
    if actual != path or stat.S_ISLNK(info.st_mode):  # O_PATH|O_NOFOLLOW opens a link itself
        raise LauncherRefusalError(f"allowed path is not canonical ({actual}): {path}")
    if _identity(info) in policy.exposes:
        raise LauncherRefusalError(f"allowance exposes a protected or sealed root: {path}")
    if _lineage(actual) & policy.sealed:
        raise LauncherRefusalError(f"allowance lies inside a sealed root: {path}")
    return fd


def _open_verified_executable(spec: RulesetSpec, policy: _GrantPolicy) -> int:
    try:
        fd = _grant_descriptor(spec.executable, os.O_RDONLY, policy)
    except LauncherRefusalError as refusal:
        raise LauncherRefusalError(f"executable {refusal}") from refusal
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        raise LauncherRefusalError("executable is not a regular file")
    digest, offset = hashlib.sha256(), 0
    while chunk := os.pread(fd, 1 << 20, offset):
        digest.update(chunk)
        offset += len(chunk)
    if digest.hexdigest() != spec.executable_sha256:
        raise LauncherRefusalError("executable sha256 does not match the pin")
    return fd


def _add_rule(libc: ctypes.CDLL, ruleset: int, fd: int, rights: int) -> None:
    attr = _PathBeneathAttr(allowed_access=rights, parent_fd=fd)
    _checked(
        libc.syscall(
            ctypes.c_long(_SYS_ADD_RULE),
            ctypes.c_int(ruleset),
            ctypes.c_int(_RULE_PATH_BENEATH),
            ctypes.byref(attr),
            ctypes.c_uint32(0),
        ),
        "landlock_add_rule",
    )


def _restrict(
    libc: ctypes.CDLL, spec: RulesetSpec, policy: _GrantPolicy, exe_fd: int, abi: int
) -> None:
    attr = _RulesetAttr(
        handled_access_fs=handled_access_fs(abi),
        handled_access_net=0,  # network is deliberately NOT handled (HTTPS stays reachable)
        scoped=_SCOPE_ABSTRACT_UNIX_SOCKET | _SCOPE_SIGNAL,
    )
    ruleset = _checked(
        libc.syscall(
            ctypes.c_long(_SYS_CREATE_RULESET),
            ctypes.byref(attr),
            ctypes.c_size_t(ctypes.sizeof(attr)),
            ctypes.c_uint32(0),
        ),
        "landlock_create_ruleset",
    )
    _add_rule(libc, ruleset, exe_fd, _EXECUTABLE_RIGHTS)
    for path in spec.read_write_dirs:
        fd = _grant_descriptor(path, os.O_PATH, policy)
        if not stat.S_ISDIR(os.fstat(fd).st_mode):
            raise LauncherRefusalError(f"read-write path is not a directory: {path}")
        _add_rule(libc, ruleset, fd, _READ_WRITE_DIR_RIGHTS)
    for path in spec.read_only_paths:
        fd = _grant_descriptor(path, os.O_PATH, policy)
        is_dir = stat.S_ISDIR(os.fstat(fd).st_mode)
        _add_rule(libc, ruleset, fd, _READ_ONLY_DIR_RIGHTS if is_dir else _READ_ONLY_FILE_RIGHTS)
    for path in spec.executable_paths:
        fd = _grant_descriptor(path, os.O_PATH, policy)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise LauncherRefusalError(f"executable allowance is not a regular file: {path}")
        _add_rule(libc, ruleset, fd, _EXECUTABLE_RIGHTS)
    for path in spec.devices:
        _add_rule(libc, ruleset, _grant_descriptor(path, os.O_PATH, policy), _DEVICE_RIGHTS)
    _checked(libc.prctl(_PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0), "prctl(PR_SET_NO_NEW_PRIVS)")
    _checked(
        libc.syscall(ctypes.c_long(_SYS_RESTRICT_SELF), ctypes.c_int(ruleset), ctypes.c_uint32(0)),
        "landlock_restrict_self",
    )


def _refuse(reason: str) -> NoReturn:
    os.write(2, f"{REFUSAL_MARKER} {reason}\n".encode())
    os._exit(REFUSAL_EXIT)


def main(argv: Sequence[str]) -> NoReturn:
    try:
        if len(argv) < 3 or argv[1] != "--":
            raise LauncherRefusalError("usage: <spec json> -- <target argv>")
        libc = _libc()
        _close_inherited_descriptors(libc)  # before any rule or executable descriptor exists
        spec = RulesetSpec.from_json(argv[0])
        abi = require_supported_abi(_query_abi)
        policy = _GrantPolicy.of(spec)
        exe_fd = _open_verified_executable(spec, policy)
        _restrict(libc, spec, policy, exe_fd, abi)
        os.execve(exe_fd, list(argv[2:]), dict(os.environ))  # fexecve: no check/exec gap
    except LauncherRefusalError as refusal:
        _refuse(str(refusal))
    except Exception as exc:  # [LAW:no-silent-failure] any other fault still refuses loudly
        _refuse(f"unexpected {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main(sys.argv[1:])

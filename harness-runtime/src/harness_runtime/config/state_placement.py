"""External persistent state-root verifier — the single placement checkpoint (S1).

A declared `StatePlacementConfig` names where persistent recovery state must live so a
checkout `git clean`/restore can never destroy or rewind it. This module is the ONE unit
that judges that declaration, and it hands back a stamp — `VerifiedStateRoot` — that later
consumers take in their signatures instead of re-checking ([LAW:parse-dont-validate],
[LAW:single-enforcer]). Two producers exist: `bootstrap_state_root` (may create the root
and its marker) and `probe_state_root` (read-only; never creates). `revalidate_state_root`
proves a root is still the one a stamp was issued for.

Every refusal is a typed `StateRootPlacementError` raised BEFORE any filesystem mutation,
so a refused placement leaves nothing behind ([LAW:no-silent-failure]).

S1 is code-only: nothing calls these functions from bootstrap, the factories, inspect or
the B-104 claim gateway yet, so this module by itself does not make any production path
external. `state_path` is the one pure derivation those later slices route through; with no
verified root it returns the exact legacy `<repo>/.harness/<name>` path.

Checks run in this order (first failing reason wins):
RELATIVE, SYMLINK_ROOT, NOT_A_DIRECTORY, INSIDE_CHECKOUT, CONTAINS_CHECKOUT,
INSIDE_FORBIDDEN, LEDGER_CELL_OUTSIDE, NON_DURABLE_FS / FS_UNDETERMINED,
PERMISSIONS / PARENT_MISSING / PARENT_UNSAFE, LEGACY_STATE_PRESENT (bootstrap only),
then identity (marker + inode/device).
"""

from __future__ import annotations

import os
import re
import secrets
import stat
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from harness_is.path_class_registry import PathClass

from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.types import PathBindingConfig, StatePlacementConfig

__all__ = [
    "MARKER_NAME",
    "StateKind",
    "StatePlacementRefusal",
    "StateRootPlacementError",
    "VerifiedStateRoot",
    "bootstrap_state_root",
    "filesystem_type_from_mountinfo",
    "linux_filesystem_type",
    "probe_state_root",
    "revalidate_state_root",
    "state_path",
]

MARKER_NAME = ".arhugula-state-root"
"""The identity marker written once (O_EXCL) at the root; its content is the root_id."""

_ROOT_ID_PATTERN = re.compile(r"[0-9a-f]{32}")
_VOLATILE_FILESYSTEMS = frozenset({"tmpfs", "ramfs"})


class StatePlacementRefusal(StrEnum):
    """Why a declared placement was refused (fail class `RT-FAIL-STATE-ROOT-PLACEMENT:<reason>`)."""

    RELATIVE = "relative"
    SYMLINK_ROOT = "symlink-root"
    NOT_A_DIRECTORY = "not-a-directory"
    INSIDE_CHECKOUT = "inside-checkout"
    CONTAINS_CHECKOUT = "contains-checkout"
    INSIDE_FORBIDDEN = "inside-forbidden"
    LEDGER_CELL_OUTSIDE = "ledger-cell-outside"
    NON_DURABLE_FS = "non-durable-fs"
    FS_UNDETERMINED = "fs-undetermined"
    PERMISSIONS = "permissions"
    PARENT_MISSING = "parent-missing"
    PARENT_UNSAFE = "parent-unsafe"
    LEGACY_STATE_PRESENT = "legacy-state-present"
    ROOT_MISSING = "root-missing"
    MARKER_MISSING = "marker-missing"
    MARKER_INVALID = "marker-invalid"
    IDENTITY_CHANGED = "identity-changed"


class StateRootPlacementError(Exception):
    """A typed placement refusal; `reason` is the discriminator callers switch on."""

    def __init__(self, reason: StatePlacementRefusal, detail: str) -> None:
        super().__init__(f"RT-FAIL-STATE-ROOT-PLACEMENT:{reason.value}: {detail}")
        self.reason = reason
        self.detail = detail


class StateKind(StrEnum):
    """Persistent recovery/memory stores placed directly under the state root.

    The value is the directory (or file) name under the root AND under the legacy
    `<repo>/.harness/`. The pause journal, pause-state audit and engine-output stores
    are deliberately not kinds: they live under STATE_LEDGER, which check
    LEDGER_CELL_OUTSIDE already pins inside the root.
    """

    EFFECT_FENCE = "effect-fence"
    ENGINE_RECOVERY_SEGMENTS = "engine-recovery-segments"
    ENGINE_RECOVERY_RECONCILER = "engine-recovery-reconciler"
    PROTECTED_RESULTS = "protected-results"
    MEMORIES = "memories"
    MEMORIES_DB = "memories.db"
    MEMORIES_ENCRYPTED = "memories-encrypted"
    MEMORY = "memory"


@dataclass(frozen=True, slots=True)
class VerifiedStateRoot:
    """The stamp `verify` hands out: a root that passed every placement check.

    Equality is the revalidation test: the same realpath, device, inode and marker
    content mean the same root; anything else is a different (or replaced) directory.
    """

    realpath: Path
    st_dev: int
    st_ino: int
    root_id: str


def state_path(kind: StateKind, root: VerifiedStateRoot | None, repository_root: Path) -> Path:
    """The one derivation of a persistent store path.

    [LAW:one-source-of-truth] Every consumer derives through here. With no verified
    root the result is the exact legacy `<repository_root>/.harness/<name>`.
    """
    base = repository_root / ".harness" if root is None else root.realpath
    return base / kind.value


# --- pure path judgment -----------------------------------------------------------------


def _require_plain_absolute(path: Path, what: str) -> None:
    if not path.is_absolute() or any(part == ".." or part.startswith("~") for part in path.parts):
        raise StateRootPlacementError(
            StatePlacementRefusal.RELATIVE,
            f"{what} {str(path)!r} must be an absolute path with no '~' or '..' component",
        )


def _nearest_existing(path: Path) -> Path:
    existing = path
    while not os.path.lexists(existing):
        existing = existing.parent
    return existing


def _prospective_realpath(path: Path) -> Path:
    """Realpath of the nearest existing ancestor plus the remaining literal components."""
    existing = _nearest_existing(path)
    tail = path.relative_to(existing)
    return Path(os.path.normpath(Path(os.path.realpath(existing)) / tail))


def _is_within(path: Path, ancestor: Path) -> bool:
    return path == ancestor or ancestor in path.parents


def filesystem_type_from_mountinfo(mountinfo: str, path: Path) -> str | None:
    """Filesystem type of the longest mount covering `path`, from `/proc/self/mountinfo` text.

    Pure so the parsing is testable without a real mount table. A later line wins over an
    earlier one for the same mount point (a stacked mount hides what is below it).
    """
    best: tuple[int, str] | None = None
    for line in mountinfo.splitlines():
        fields = line.split(" ")
        if "-" not in fields[6:]:
            continue
        sep = fields.index("-", 6)
        mount_point = Path(re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), fields[4]))
        if _is_within(path, mount_point) and (best is None or len(mount_point.parts) >= best[0]):
            best = (len(mount_point.parts), fields[sep + 1])
    return None if best is None else best[1]


def linux_filesystem_type(path: Path) -> str | None:
    """Real resolver: the filesystem type under `path`, or `None` when it cannot be read."""
    try:
        text = Path("/proc/self/mountinfo").read_text()
    except OSError:
        return None
    return filesystem_type_from_mountinfo(text, path)


# --- the verifier -----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Judged:
    """A root that passed every check that needs no mutation."""

    lexical: Path
    resolved: Path
    exists: bool


def _judge(
    placement: StatePlacementConfig,
    *,
    repository_root: Path,
    worktree_base: Path,
    path_bindings: PathBindingConfig,
    filesystem_type: Callable[[Path], str | None],
    creating: bool,
) -> _Judged:
    root = placement.state_root
    _require_plain_absolute(root, "state_root")
    for forbidden in placement.forbidden_roots:
        _require_plain_absolute(forbidden, "forbidden_roots entry")

    exists = os.path.lexists(root)
    if exists:
        mode = os.lstat(root).st_mode
        if stat.S_ISLNK(mode):
            raise StateRootPlacementError(
                StatePlacementRefusal.SYMLINK_ROOT, f"state_root {str(root)!r} is a symlink"
            )
        if not stat.S_ISDIR(mode):
            raise StateRootPlacementError(
                StatePlacementRefusal.NOT_A_DIRECTORY,
                f"state_root {str(root)!r} is not a directory",
            )
    resolved = _prospective_realpath(root)

    for ancestor in resolved.parents:
        if os.path.lexists(ancestor / ".git"):
            raise StateRootPlacementError(
                StatePlacementRefusal.INSIDE_CHECKOUT,
                f"state_root resolves to {str(resolved)!r}, "
                f"inside the checkout at {str(ancestor)!r}",
            )

    protected = [
        _prospective_realpath(repository_root),
        _prospective_realpath(worktree_base),
        *(_prospective_realpath(f) for f in placement.forbidden_roots),
    ]
    if os.path.lexists(resolved / ".git") or any(_is_within(t, resolved) for t in protected):
        raise StateRootPlacementError(
            StatePlacementRefusal.CONTAINS_CHECKOUT,
            f"state_root {str(resolved)!r} is or contains a checkout, "
            "worktree base or forbidden root",
        )
    for forbidden in protected[2:]:
        if _is_within(resolved, forbidden):
            raise StateRootPlacementError(
                StatePlacementRefusal.INSIDE_FORBIDDEN,
                f"state_root {str(resolved)!r} is inside the forbidden root {str(forbidden)!r}",
            )

    for entry in build_path_binding(path_bindings).entries:
        if entry.path_class is not PathClass.STATE_LEDGER:
            continue
        cell = Path(entry.path)
        if not cell.is_absolute() or not _is_within(_prospective_realpath(cell), resolved):
            raise StateRootPlacementError(
                StatePlacementRefusal.LEDGER_CELL_OUTSIDE,
                f"STATE_LEDGER cell {entry.workflow_class.value!r} path {entry.path!r} "
                f"is not inside the state root {str(resolved)!r}",
            )

    fs = filesystem_type(_nearest_existing(resolved))
    if fs is None:
        raise StateRootPlacementError(
            StatePlacementRefusal.FS_UNDETERMINED, "filesystem type of the state root is unknown"
        )
    if fs in _VOLATILE_FILESYSTEMS:
        raise StateRootPlacementError(
            StatePlacementRefusal.NON_DURABLE_FS, f"state root is on a volatile filesystem ({fs})"
        )

    if exists:
        st = os.stat(resolved)
        if st.st_uid != os.geteuid() or st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise StateRootPlacementError(
                StatePlacementRefusal.PERMISSIONS,
                "state root must be owned by the effective user and not group/other-writable",
            )
    elif creating:
        _require_safe_parent(resolved.parent)
    return _Judged(lexical=root, resolved=resolved, exists=exists)


def _require_safe_parent(parent: Path) -> None:
    try:
        st = os.stat(parent)
    except OSError as exc:
        raise StateRootPlacementError(
            StatePlacementRefusal.PARENT_MISSING,
            f"parent {str(parent)!r} of the state root must already exist ({exc.strerror})",
        ) from exc
    if not stat.S_ISDIR(st.st_mode):
        raise StateRootPlacementError(
            StatePlacementRefusal.PARENT_MISSING, f"parent {str(parent)!r} is not a directory"
        )
    others_can_write = st.st_mode & (stat.S_IWGRP | stat.S_IWOTH) and not st.st_mode & stat.S_ISVTX
    if st.st_uid not in {os.geteuid(), 0} or others_can_write:
        raise StateRootPlacementError(
            StatePlacementRefusal.PARENT_UNSAFE,
            f"parent {str(parent)!r} is owned by another user or writable by group/other",
        )


def _legacy_state_present(repository_root: Path) -> list[Path]:
    present: list[Path] = []
    for kind in StateKind:
        legacy = state_path(kind, None, repository_root)
        try:
            if legacy.is_dir():
                nonempty = any(legacy.iterdir())
            else:
                nonempty = legacy.exists() and legacy.stat().st_size > 0
        except OSError:
            nonempty = True  # unreadable legacy state is uncertain: refuse rather than guess
        if nonempty:
            present.append(legacy)
    return present


def _read_marker(root: Path) -> str | None:
    """The marker's root_id, `None` when absent; `MARKER_INVALID` when unusable."""
    marker = root / MARKER_NAME
    try:
        fd = os.open(marker, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise StateRootPlacementError(
            StatePlacementRefusal.MARKER_INVALID, f"marker unreadable: {exc.strerror}"
        ) from exc
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise StateRootPlacementError(
                StatePlacementRefusal.MARKER_INVALID, "marker is not a regular file"
            )
        text = os.read(fd, 64).decode("ascii", errors="replace")
    finally:
        os.close(fd)
    if not _ROOT_ID_PATTERN.fullmatch(text):
        raise StateRootPlacementError(
            StatePlacementRefusal.MARKER_INVALID, "marker content is not a root id"
        )
    return text


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_marker_exclusively(root: Path) -> None:
    root_id = secrets.token_hex(16)
    fd = os.open(root / MARKER_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, root_id.encode("ascii"))
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(root)


def _stamp(resolved: Path, root_id: str) -> VerifiedStateRoot:
    st = os.stat(resolved)
    return VerifiedStateRoot(realpath=resolved, st_dev=st.st_dev, st_ino=st.st_ino, root_id=root_id)


def probe_state_root(
    placement: StatePlacementConfig,
    *,
    repository_root: Path,
    worktree_base: Path,
    path_bindings: PathBindingConfig,
    filesystem_type: Callable[[Path], str | None] = linux_filesystem_type,
) -> VerifiedStateRoot:
    """Verify an EXISTING, marked root without creating or writing anything."""
    judged = _judge(
        placement,
        repository_root=repository_root,
        worktree_base=worktree_base,
        path_bindings=path_bindings,
        filesystem_type=filesystem_type,
        creating=False,
    )
    if not judged.exists:
        raise StateRootPlacementError(
            StatePlacementRefusal.ROOT_MISSING,
            f"state root {str(judged.lexical)!r} does not exist (probe never creates)",
        )
    root_id = _read_marker(judged.resolved)
    if root_id is None:
        raise StateRootPlacementError(
            StatePlacementRefusal.MARKER_MISSING, f"no {MARKER_NAME} marker in the state root"
        )
    return _stamp(judged.resolved, root_id)


def bootstrap_state_root(
    placement: StatePlacementConfig,
    *,
    repository_root: Path,
    worktree_base: Path,
    path_bindings: PathBindingConfig,
    filesystem_type: Callable[[Path], str | None] = linux_filesystem_type,
) -> VerifiedStateRoot:
    """Verify the placement and, only once every check passed, create root and marker.

    A missing root is created 0700 under an already-existing safe parent (never
    `parents=True`). An existing root keeps its marker; an existing EMPTY directory is
    adopted; an existing non-empty directory without a marker is refused
    (`MARKER_MISSING`) because adopting someone else's data as harness state is unsafe.
    A non-empty legacy repo-local store refuses (`LEGACY_STATE_PRESENT`): migration is an
    explicit operator step, never an automatic copy.
    """
    judged = _judge(
        placement,
        repository_root=repository_root,
        worktree_base=worktree_base,
        path_bindings=path_bindings,
        filesystem_type=filesystem_type,
        creating=True,
    )
    legacy = _legacy_state_present(repository_root)
    if legacy:
        raise StateRootPlacementError(
            StatePlacementRefusal.LEGACY_STATE_PRESENT,
            "non-empty repo-local state exists at "
            + ", ".join(str(p) for p in legacy)
            + "; stop the harness and migrate or archive it explicitly "
            "before placing state externally",
        )
    root_id = _read_marker(judged.resolved) if judged.exists else None
    if judged.exists and root_id is None and any(judged.resolved.iterdir()):
        raise StateRootPlacementError(
            StatePlacementRefusal.MARKER_MISSING,
            "existing non-empty state root has no marker and will not be adopted",
        )
    if not judged.exists:
        os.mkdir(judged.resolved, 0o700)
        _fsync_dir(judged.resolved.parent)
    if root_id is None:
        _write_marker_exclusively(judged.resolved)
        root_id = _read_marker(judged.resolved)
    assert root_id is not None  # just written: absence here is a broken filesystem, not input
    return _stamp(judged.resolved, root_id)


def revalidate_state_root(
    stamp: VerifiedStateRoot,
    placement: StatePlacementConfig,
    *,
    repository_root: Path,
    worktree_base: Path,
    path_bindings: PathBindingConfig,
    filesystem_type: Callable[[Path], str | None] = linux_filesystem_type,
) -> VerifiedStateRoot:
    """Probe the declared root again and require it to be exactly the stamped one."""
    current = probe_state_root(
        placement,
        repository_root=repository_root,
        worktree_base=worktree_base,
        path_bindings=path_bindings,
        filesystem_type=filesystem_type,
    )
    if current != stamp:
        raise StateRootPlacementError(
            StatePlacementRefusal.IDENTITY_CHANGED,
            f"state root is no longer the one stamped ({str(stamp.realpath)!r} -> "
            f"{str(current.realpath)!r}; device/inode/root_id compared)",
        )
    return current

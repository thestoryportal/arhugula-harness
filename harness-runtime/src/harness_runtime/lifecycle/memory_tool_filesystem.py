"""U-RT-77 — `LocalFilesystemMemoryToolBackend` filesystem implementation.

Implements runtime spec v1.17 §14.12.3 step 2a (`MemoryToolStorageBackend.FILESYSTEM`
→ filesystem-backed implementation) + §14.12.2 per-callback invocation discipline
(path validation at every callback; async-only Protocol surface; no retry inside
callback) + §14.12.5 invariants 3 (path discipline enforced at backend BEFORE I/O)
+ 6 (per-backend lifecycle owned by backend).

Per L9-octies cluster discipline (runtime plan v2.15 §1):
- L1 within-cluster (←U-RT-76).
- §14.D operator-ratified scope: filesystem-only backend at v2.14/v2.15 arc; other
  enum values (S3 / ENCRYPTED_FILESYSTEM / DATABASE / OPERATOR_DEFINED) deferred
  to operator-discretion follow-on retirement-batch arcs per §16 §6.C v2 C.vii.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from pathlib import Path, PurePosixPath

from harness_runtime.lifecycle.memory_tool_types import (
    MemoryCallbackIOError,
    MemoryPathViolationError,
)

__all__ = ["LocalFilesystemMemoryToolBackend"]


_MEMORIES_SCOPE = "/memories/"
"""The `/memories/` path-scope prefix per ADR-D3 v1.2 §1.1 #11 + runtime spec
§14.12.5 invariant 3."""


class LocalFilesystemMemoryToolBackend:
    """Filesystem-backed `MemoryToolStorageBackendProtocol` implementation.

    Roots `/memories/` callback paths at a deployment-surface-resolved
    filesystem path. Path discipline enforced BEFORE I/O per §14.12.5
    invariant 3 (NOT relying on filesystem permission errors). Concurrency
    via per-path `asyncio.Lock` per §14.12.2 invariant 3 (backend owns
    concurrency model).
    """

    def __init__(self, *, root: Path) -> None:
        """Instantiate backend rooted at `root` filesystem path.

        `root` is the directory under which `/memories/{relative}` callbacks
        resolve. Resolution to PathClass enum is deferred per
        §14.12.7 implementation discretion; this constructor accepts a
        `Path` directly per plan v2.15 U-RT-77 signature.
        """
        self._root = root.resolve()
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    # ------------------------------------------------------------------
    # Path discipline (per §14.12.5 invariant 3 — validate BEFORE I/O).
    # ------------------------------------------------------------------

    def _validate_path(self, path: str) -> Path:
        """Validate `path` is scoped to `/memories/` + map to filesystem path.

        Raises `MemoryPathViolationError` (→ RT-FAIL-MEMORY-PATH-VIOLATION
        permanent per §14.12.4) BEFORE any filesystem I/O on:
        - paths not prefixed with `/memories/`
        - paths containing `..` traversal segments
        - paths whose resolved location escapes `self._root`
        """
        if not path.startswith(_MEMORIES_SCOPE):
            raise MemoryPathViolationError(
                f"path {path!r} not prefixed with {_MEMORIES_SCOPE!r}"
            )

        relative = path[len(_MEMORIES_SCOPE):]
        if not relative:
            raise MemoryPathViolationError(
                f"path {path!r} resolves to /memories/ directory itself; expected file path"
            )
        if relative.startswith("/"):
            raise MemoryPathViolationError(
                f"path {path!r} double-slash after /memories/ scope"
            )

        # Reject `..` traversal segments BEFORE resolution attempt
        # (defense in depth — resolution check below also catches escapes).
        if ".." in PurePosixPath(relative).parts:
            raise MemoryPathViolationError(
                f"path {path!r} contains path-traversal segment '..'"
            )

        resolved = (self._root / relative).resolve()
        # Defense-in-depth: resolved path must lie inside self._root
        # (catches symlink-based escapes + normalization edge cases).
        try:
            resolved.relative_to(self._root)
        except ValueError as exc:
            raise MemoryPathViolationError(
                f"path {path!r} resolves outside /memories/ scope root {self._root!r}"
            ) from exc

        return resolved

    # ------------------------------------------------------------------
    # MemoryToolStorageBackendProtocol — 5 CRUD callbacks.
    # ------------------------------------------------------------------

    async def view(self, path: str) -> bytes:
        """Read content of `/memories/{path}` (Protocol method).

        Per §14.12.2 invariant 4: no retry inside callback; first-attempt
        I/O failure propagates as `MemoryCallbackIOError`.
        """
        target = self._validate_path(path)
        async with self._locks[path]:
            try:
                return await asyncio.to_thread(target.read_bytes)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"view({path!r}) failed: {exc}"
                ) from exc

    async def create(self, path: str, content: bytes) -> None:
        """Create `/memories/{path}` with `content`; overwrites if exists.

        Parents are created on demand (mkdir(parents=True, exist_ok=True))
        per filesystem-style interface ergonomic at /memories paths Claude
        controls.
        """
        target = self._validate_path(path)
        async with self._locks[path]:
            try:
                await asyncio.to_thread(target.parent.mkdir, parents=True, exist_ok=True)
                await asyncio.to_thread(target.write_bytes, content)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"create({path!r}) failed: {exc}"
                ) from exc

    async def delete(self, path: str) -> None:
        """Delete `/memories/{path}`; no-op if absent."""
        target = self._validate_path(path)
        async with self._locks[path]:
            try:
                await asyncio.to_thread(target.unlink, missing_ok=True)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"delete({path!r}) failed: {exc}"
                ) from exc

    async def str_replace(self, path: str, old: str, new: str) -> None:
        """Replace `old` with `new` in `/memories/{path}`.

        Raises `MemoryCallbackIOError` if `old` not found OR if file absent
        OR on read/write I/O failure.
        """
        target = self._validate_path(path)
        async with self._locks[path]:
            try:
                content = await asyncio.to_thread(target.read_text)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"str_replace({path!r}) read failed: {exc}"
                ) from exc

            if old not in content:
                raise MemoryCallbackIOError(
                    f"str_replace({path!r}): substring {old!r} not found"
                )

            replaced = content.replace(old, new)
            try:
                await asyncio.to_thread(target.write_text, replaced)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"str_replace({path!r}) write failed: {exc}"
                ) from exc

    async def insert(self, path: str, line: int, content: str) -> None:
        """Insert `content` at 1-indexed `line` in `/memories/{path}`.

        Per Anthropic Memory tool convention: lines are 1-indexed; `line=1`
        inserts at the top of the file. Raises `MemoryCallbackIOError` on
        out-of-range line OR I/O failure.
        """
        target = self._validate_path(path)
        async with self._locks[path]:
            try:
                existing = await asyncio.to_thread(target.read_text)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"insert({path!r}) read failed: {exc}"
                ) from exc

            lines = existing.splitlines(keepends=True)
            # 1-indexed; line=1 → insert before lines[0]; line=len(lines)+1 → append.
            if line < 1 or line > len(lines) + 1:
                raise MemoryCallbackIOError(
                    f"insert({path!r}, line={line}): out of range "
                    f"(1..{len(lines) + 1})"
                )

            lines.insert(line - 1, content)
            replaced = "".join(lines)

            try:
                await asyncio.to_thread(target.write_text, replaced)
            except OSError as exc:
                raise MemoryCallbackIOError(
                    f"insert({path!r}) write failed: {exc}"
                ) from exc

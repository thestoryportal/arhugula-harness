"""U-RT-77 — `LocalFilesystemMemoryToolBackend` tests.

ACs per runtime plan v2.15 §1 U-RT-77 (8 original ACs + NEW AC #9 per F1-02
absorption at v2.15: "no retry inside callback" invariant 4):

1. `LocalFilesystemMemoryToolBackend(root=tmp_path)` instantiates; satisfies
   `MemoryToolStorageBackendProtocol` via `@runtime_checkable` isinstance.
2. Round-trip: create → view → delete → subsequent view raises
   `MemoryCallbackIOError`.
3. `str_replace` after create → view returns replaced content.
4. `insert` after create with multi-line content → expected line contains
   inserted content.
5. Path-discipline: `../etc/passwd` raises `MemoryPathViolationError` BEFORE
   filesystem I/O.
6. Path-discipline: `/etc/passwd` (absolute outside scope) raises
   `MemoryPathViolationError`.
7. Concurrency: 100 concurrent calls (distinct paths) succeed; 100 concurrent
   `str_replace` on same path complete without race (per-path lock).
8. Importable; pyright strict mode passes.
9. **NEW at v2.15 per F1-02 absorption:** callbacks do NOT retry on
   `MemoryCallbackIOError`; transient I/O failure propagates immediately on
   first attempt (call-count == 1 on mock filesystem op; no asyncio.sleep
   inside backend method body).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
from harness_runtime.lifecycle.memory_tool_filesystem import (
    LocalFilesystemMemoryToolBackend,
)
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryCallbackIOError,
    MemoryPathViolationError,
    MemoryToolStorageBackendProtocol,
)

# AC #1 — instantiation + Protocol conformance.


def test_backend_instantiates_with_tmp_root(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    assert backend is not None


def test_backend_satisfies_protocol_via_isinstance(tmp_path: Path) -> None:
    """AC #1 — `isinstance(backend, MemoryToolStorageBackendProtocol)` passes."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    assert isinstance(backend, MemoryToolStorageBackendProtocol)


# AC #2 — round-trip create/view/delete.


@pytest.mark.asyncio
async def test_round_trip_create_view_delete(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"hello")
    assert await backend.view("/memories/foo.txt") == b"hello"
    await backend.delete("/memories/foo.txt")
    with pytest.raises(MemoryCallbackIOError):
        await backend.view("/memories/foo.txt")


@pytest.mark.asyncio
async def test_create_overwrites_existing(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"first")
    await backend.create("/memories/foo.txt", b"second")
    assert await backend.view("/memories/foo.txt") == b"second"


@pytest.mark.asyncio
async def test_delete_is_noop_on_absent_file(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    # Should not raise per Protocol "No-op if absent" docstring.
    await backend.delete("/memories/never_existed.txt")


@pytest.mark.asyncio
async def test_create_makes_parent_dirs(tmp_path: Path) -> None:
    """Nested paths: parents created on demand for filesystem-style ergonomics."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/nested/dir/file.txt", b"data")
    assert await backend.view("/memories/nested/dir/file.txt") == b"data"


# AC #3 — str_replace.


@pytest.mark.asyncio
async def test_str_replace_round_trip(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"hello world")
    await backend.str_replace("/memories/foo.txt", "world", "claude")
    assert await backend.view("/memories/foo.txt") == b"hello claude"


@pytest.mark.asyncio
async def test_str_replace_raises_on_missing_substring(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"hello")
    with pytest.raises(MemoryCallbackIOError, match="not found"):
        await backend.str_replace("/memories/foo.txt", "absent", "x")


# AC #4 — insert at 1-indexed line.


@pytest.mark.asyncio
async def test_insert_at_top(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"line A\nline B\n")
    await backend.insert("/memories/foo.txt", 1, "INSERTED\n")
    content = await backend.view("/memories/foo.txt")
    assert content == b"INSERTED\nline A\nline B\n"


@pytest.mark.asyncio
async def test_insert_in_middle(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"line A\nline B\nline C\n")
    await backend.insert("/memories/foo.txt", 2, "MIDDLE\n")
    content = await backend.view("/memories/foo.txt")
    assert content == b"line A\nMIDDLE\nline B\nline C\n"


@pytest.mark.asyncio
async def test_insert_at_append_position(tmp_path: Path) -> None:
    """`line == len(lines) + 1` appends at end."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"line A\nline B\n")
    await backend.insert("/memories/foo.txt", 3, "APPEND\n")
    content = await backend.view("/memories/foo.txt")
    assert content == b"line A\nline B\nAPPEND\n"


@pytest.mark.asyncio
async def test_insert_out_of_range_raises(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/foo.txt", b"only one line\n")
    with pytest.raises(MemoryCallbackIOError, match="out of range"):
        await backend.insert("/memories/foo.txt", 99, "x")
    with pytest.raises(MemoryCallbackIOError, match="out of range"):
        await backend.insert("/memories/foo.txt", 0, "x")


# AC #5 — path-discipline: traversal rejected BEFORE filesystem I/O.


@pytest.mark.asyncio
async def test_path_traversal_rejected_before_io(tmp_path: Path) -> None:
    """AC #5 — `../etc/passwd` raises MemoryPathViolationError BEFORE any
    filesystem I/O attempt (verified via mock-patched `Path.read_bytes`)."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    with patch.object(Path, "read_bytes") as mock_read:
        with pytest.raises(MemoryPathViolationError):
            await backend.view("/memories/../etc/passwd")
        mock_read.assert_not_called()


# AC #6 — path-discipline: absolute path outside scope.


@pytest.mark.asyncio
async def test_absolute_path_outside_scope_rejected(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    with pytest.raises(MemoryPathViolationError):
        await backend.view("/etc/passwd")


@pytest.mark.asyncio
async def test_path_without_memories_prefix_rejected(tmp_path: Path) -> None:
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    with pytest.raises(MemoryPathViolationError):
        await backend.view("foo.txt")
    with pytest.raises(MemoryPathViolationError):
        await backend.create("notes/x", b"")


@pytest.mark.asyncio
async def test_empty_relative_path_rejected(tmp_path: Path) -> None:
    """`/memories/` (no file) rejected — expected file path, not dir itself."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    with pytest.raises(MemoryPathViolationError, match="directory itself"):
        await backend.view("/memories/")


# AC #7 — concurrency.


@pytest.mark.asyncio
async def test_concurrent_distinct_paths_complete(tmp_path: Path) -> None:
    """100 concurrent create calls to distinct paths complete without error."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    tasks = [backend.create(f"/memories/file_{i}.txt", f"content_{i}".encode()) for i in range(100)]
    await asyncio.gather(*tasks)
    # Verify all readable
    for i in range(100):
        assert await backend.view(f"/memories/file_{i}.txt") == f"content_{i}".encode()


@pytest.mark.asyncio
async def test_concurrent_str_replace_same_path_serializes(tmp_path: Path) -> None:
    """100 concurrent str_replace on same path complete without race.

    Per-path asyncio.Lock serializes; final content is deterministic per
    serial semantics (each replace applied once; final state matches the
    last-acquired-lock semantics — content reaches a stable, well-defined
    end-state).
    """
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)
    await backend.create("/memories/shared.txt", b"original")

    # Each task does original → replaced_{i}; after 100 sequential applications
    # only one substitution sticks (depending on lock acquisition order). Test
    # asserts no race / corruption: final read produces SOME valid content.
    async def _replace(i: int) -> None:
        try:
            await backend.str_replace("/memories/shared.txt", "original", f"r{i}")
        except MemoryCallbackIOError:
            # After first successful replace, "original" is absent for others.
            pass

    await asyncio.gather(*[_replace(i) for i in range(100)])
    final = await backend.view("/memories/shared.txt")
    # Exactly one replace succeeded; content starts with "r" + a number.
    assert final.startswith(b"r")


# AC #8 — importable + pyright (importable verified by test-module loading).


def test_module_importable() -> None:
    from harness_runtime.lifecycle import memory_tool_filesystem

    assert memory_tool_filesystem.LocalFilesystemMemoryToolBackend is not None


# AC #9 (NEW at v2.15 per F1-02 absorption) — no retry inside callback.


@pytest.mark.asyncio
async def test_no_retry_on_io_failure_view(tmp_path: Path) -> None:
    """AC #9 — callbacks do NOT retry on transient I/O failure.

    Per §14.12.2 invariant 4: storage-backend I/O failures propagate
    immediately as MemoryCallbackIOError on first attempt. Mock filesystem
    op raises OSError; assert exactly 1 call (no retry loop)."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)

    call_count = 0

    def _failing_read(*args: object, **kwargs: object) -> bytes:
        nonlocal call_count
        call_count += 1
        raise OSError("transient I/O")

    with patch.object(Path, "read_bytes", side_effect=_failing_read):
        with pytest.raises(MemoryCallbackIOError):
            await backend.view("/memories/foo.txt")

    assert call_count == 1, (
        f"expected exactly 1 filesystem read attempt; got {call_count} "
        f"(retry inside callback violates §14.12.2 invariant 4)"
    )


@pytest.mark.asyncio
async def test_no_retry_on_io_failure_create(tmp_path: Path) -> None:
    """AC #9 (create variant) — no retry on write failure."""
    backend = LocalFilesystemMemoryToolBackend(root=tmp_path)

    call_count = 0

    def _failing_write(*args: object, **kwargs: object) -> None:
        nonlocal call_count
        call_count += 1
        raise OSError("disk full")

    with patch.object(Path, "write_bytes", side_effect=_failing_write):
        with pytest.raises(MemoryCallbackIOError):
            await backend.create("/memories/foo.txt", b"data")

    assert call_count == 1, f"expected exactly 1 filesystem write attempt; got {call_count}"


@pytest.mark.asyncio
async def test_no_asyncio_sleep_in_backend_body() -> None:
    """AC #9 (defense-in-depth) — backend module source contains no asyncio.sleep
    calls (no in-band retry-with-backoff pattern)."""
    import harness_runtime.lifecycle.memory_tool_filesystem as module_under_test

    source = Path(module_under_test.__file__).read_text()
    assert "asyncio.sleep" not in source, (
        "backend module source contains `asyncio.sleep` — possible "
        "in-band retry-with-backoff pattern violating §14.12.2 invariant 4"
    )

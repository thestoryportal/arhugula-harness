"""U-RT-78 — `MemoryToolRegistry` tests.

ACs per runtime plan v2.15 §1 U-RT-78 (preserved from v2.14):

1. `MemoryToolRegistry(backend=fake_backend,
   configured_backend=MemoryToolStorageBackend.FILESYSTEM)` instantiates;
   `.resolve_backend(DeploymentSurface.LOCAL_DEVELOPMENT) is fake_backend`;
   `.configured_backend == MemoryToolStorageBackend.FILESYSTEM`.
2. `resolve_backend` callable with any `DeploymentSurface` value and returns
   the same backend instance (bootstrap-time-frozen per invariant 1).
3. Importable; pyright strict mode passes.
"""

from __future__ import annotations

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_runtime.lifecycle.memory_tool_registry import MemoryToolRegistry
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryToolStorageBackend,
    MemoryToolStorageBackendProtocol,
)


class _FakeBackend:
    """Minimal Protocol-satisfying backend for registry tests."""

    async def view(self, path: str) -> bytes:
        return b""

    async def create(self, path: str, content: bytes) -> None:
        return None

    async def delete(self, path: str) -> None:
        return None

    async def str_replace(self, path: str, old: str, new: str) -> None:
        return None

    async def insert(self, path: str, line: int, content: str) -> None:
        return None


# AC #1 — instantiation + resolve_backend + configured_backend.


def test_registry_instantiates_and_stores_backend() -> None:
    fake = _FakeBackend()
    registry = MemoryToolRegistry(
        backend=fake,
        configured_backend=MemoryToolStorageBackend.FILESYSTEM,
    )
    assert registry.resolve_backend(DeploymentSurface.LOCAL_DEVELOPMENT) is fake
    assert registry.configured_backend == MemoryToolStorageBackend.FILESYSTEM


def test_registry_accepts_protocol_typed_backend() -> None:
    """The fake satisfies MemoryToolStorageBackendProtocol via @runtime_checkable."""
    fake = _FakeBackend()
    assert isinstance(fake, MemoryToolStorageBackendProtocol)
    # Registry accepts the Protocol-typed backend without runtime error.
    registry = MemoryToolRegistry(
        backend=fake,
        configured_backend=MemoryToolStorageBackend.FILESYSTEM,
    )
    assert registry.resolve_backend(DeploymentSurface.LOCAL_DEVELOPMENT) is fake


# AC #2 — resolve_backend bootstrap-time-frozen (returns same instance regardless
# of deployment_surface argument).


@pytest.mark.parametrize(
    "surface",
    [
        DeploymentSurface.LOCAL_DEVELOPMENT,
        DeploymentSurface.SELF_HOSTED_SERVER,
        DeploymentSurface.MANAGED_CLOUD,
    ],
)
def test_resolve_backend_returns_same_instance_for_any_surface(
    surface: DeploymentSurface,
) -> None:
    """AC #2 — resolve_backend returns the stored backend regardless of arg
    per §14.12.5 invariant 1 (bootstrap-time-frozen resolution)."""
    fake = _FakeBackend()
    registry = MemoryToolRegistry(
        backend=fake,
        configured_backend=MemoryToolStorageBackend.FILESYSTEM,
    )
    assert registry.resolve_backend(surface) is fake


def test_configured_backend_round_trips_each_enum_value() -> None:
    """Registry accepts any MemoryToolStorageBackend enum value at construction."""
    fake = _FakeBackend()
    for enum_value in MemoryToolStorageBackend:
        registry = MemoryToolRegistry(backend=fake, configured_backend=enum_value)
        assert registry.configured_backend == enum_value


# AC #3 — module importable (verified via test-file imports + this assertion).


def test_module_importable() -> None:
    from harness_runtime.lifecycle import memory_tool_registry

    assert memory_tool_registry.MemoryToolRegistry is not None

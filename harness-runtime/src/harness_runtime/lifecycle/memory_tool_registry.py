"""U-RT-78 — `MemoryToolRegistry` class.

Implements runtime spec v1.17 §14.12.1 (`MemoryToolRegistry` class declaration —
`resolve_backend(deployment_surface) → MemoryToolStorageBackendProtocol` +
`configured_backend` property returning `MemoryToolStorageBackend` enum value) +
§14.12.5 invariant 1 (storage-backend resolved exactly once per bootstrap; no
re-resolution at dispatch-time).

Per L9-octies cluster discipline (runtime plan v2.15 §1):
- L1 within-cluster (←U-RT-76); no edge to U-RT-77.
- Constructor receives pre-resolved backend implementation + enum-value
  identity from U-RT-80 factory; registry is a pure carrier (no resolution
  logic — that lives at the factory per §14.12.5 invariant 1).
- MVP: `resolve_backend(deployment_surface)` ignores its argument and returns
  the stored backend; future multi-surface support is implementation-arc
  discretion per §14.12.7 (the argument shape is retained for API-shape
  stability per §14.12.1 signature).
"""

from __future__ import annotations

from harness_core.deployment_surface import DeploymentSurface

from harness_runtime.lifecycle.memory_tool_types import (
    MemoryToolStorageBackend,
    MemoryToolStorageBackendProtocol,
)

__all__ = ["MemoryToolRegistry"]


class MemoryToolRegistry:
    """Registry binding `MemoryToolStorageBackendProtocol` implementations to
    deployment surfaces.

    Constructed at bootstrap stage 5 by `materialize_memory_tool_registry_stage`
    per §14.12.3 (factory landing owed at U-RT-80). At v2.15 MVP scope: stores
    a single pre-resolved backend implementation + the enum-value identity for
    span-attribute emission at C-RT-15 §14.5.1 callback-injection composer-step.
    """

    def __init__(
        self,
        *,
        backend: MemoryToolStorageBackendProtocol,
        configured_backend: MemoryToolStorageBackend,
    ) -> None:
        """Bind a pre-resolved storage-backend implementation to the registry.

        Per §14.12.5 invariant 1: storage-backend resolved exactly once per
        bootstrap; the registry stores the resolution outcome (the backend
        implementation + the enum identity). Re-resolution at dispatch-time
        is forbidden.
        """
        self._backend = backend
        self._configured_backend = configured_backend

    def resolve_backend(
        self,
        deployment_surface: DeploymentSurface,
    ) -> MemoryToolStorageBackendProtocol:
        """Return the stored storage-backend implementation.

        Per §14.12.5 invariant 1: resolution is bootstrap-time-frozen.
        The `deployment_surface` parameter is retained per §14.12.1 signature
        for API-shape stability; future multi-surface registry support is
        implementation-arc discretion per §14.12.7. MVP returns the stored
        backend regardless of `deployment_surface` value.
        """
        return self._backend

    @property
    def configured_backend(self) -> MemoryToolStorageBackend:
        """The `MemoryToolStorageBackend` enum value identifying the backend.

        Consumed at C-RT-15 §14.5.1 callback-injection composer-step for
        `memory.backend` span-attribute emission per AS spec v1.5 §14.7
        + §14.8 sampling-row at memory.operation spans.
        """
        return self._configured_backend

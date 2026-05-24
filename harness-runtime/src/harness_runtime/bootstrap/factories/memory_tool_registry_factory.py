"""U-RT-80 — Stage 5 factory `materialize_memory_tool_registry_stage(config, ctx)
→ MemoryToolRegistry`.

Per `Spec_Harness_Runtime_v1.md` v1.17 §14.12.3 stage-5 factory contract +
§14.12.5 invariant 2 (Protocol-conformance enforced at stage-5 binding via
`@runtime_checkable` introspection).

3-step composition body per spec §14.12.3 prose:

  1. Resolve the configured `MemoryToolStorageBackend` enum value per
     `config.memory_tool_backend_config` override (if present), else via the
     `harness_as.anthropic_graceful_degradation.memory_tool_storage_backend`
     resolver default for `config.deployment_surface` (picks the
     `FILESYSTEM` member if present in the returned frozenset — the only
     backend with an implementation landed at v2.15 per §14.D operator
     ratification).
  2. Construct the storage-backend implementation:
     - `FILESYSTEM` → `LocalFilesystemMemoryToolBackend` rooted at
       `config.repository_root / ".harness/memories"` (root path resolution
       per §14.12.7 implementation discretion; PathClass extension deferred).
     - Other enum values → raise `MemoryBackendResolutionError` naming the
       unimplemented backend and carrying the fork-doc §14.D pointer.
  3. Verify the constructed backend satisfies
     `MemoryToolStorageBackendProtocol` via `@runtime_checkable` isinstance
     introspection (§14.12.5 invariant 2). Defense-in-depth: also verify
     every method named on the Protocol resolves on the backend (catches
     non-callable shadowing that `@runtime_checkable` does not).
  4. Construct `MemoryToolRegistry(backend=..., configured_backend=...)`
     and bind to `ctx.memory_tool_registry`.

Stage-5 ordering per §14.12.3: arbitrary within stage 5 LOOP_INIT (no
ordering dependency on `materialize_runtime_tool_dispatcher_stage` — the
registry construction has no shared dependency with the tool dispatcher).
"""

from __future__ import annotations

from harness_as.anthropic_graceful_degradation import (
    MemoryToolStorageBackend,
    memory_tool_storage_backend,
)

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.memory_tool_filesystem import (
    LocalFilesystemMemoryToolBackend,
)
from harness_runtime.lifecycle.memory_tool_registry import MemoryToolRegistry
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryBackendResolutionError,
    MemoryToolStorageBackendProtocol,
)
from harness_runtime.types import RuntimeConfig

__all__ = [
    "MEMORY_TOOL_FILESYSTEM_ROOT_SUBPATH",
    "PROTOCOL_REQUIRED_METHODS",
    "materialize_memory_tool_registry_stage",
]


MEMORY_TOOL_FILESYSTEM_ROOT_SUBPATH = ".harness/memories"
"""Sub-path under `config.repository_root` for the FILESYSTEM backend root.

Per spec §14.12.7 implementation discretion + §14.12.3 step 2a suggestion of
`PathClass.MEMORY_TOOL_BACKEND_ROOT` (PathClass extension deferred). Mirrors
the `.harness/...` sibling sub-paths used by other runtime carriers
(`.harness/runtime.pid`, etc.)."""


PROTOCOL_REQUIRED_METHODS: tuple[str, ...] = (
    "view",
    "create",
    "delete",
    "str_replace",
    "insert",
)
"""The 5 CRUD callbacks per ADR-D3 v1.2 §1.1 #11 + runtime spec v1.17
§14.12.1 `MemoryToolStorageBackendProtocol`. Used for the defensive
post-isinstance method-presence sweep at step 3 below."""


async def materialize_memory_tool_registry_stage(
    config: RuntimeConfig,
    ctx: _MutableHarnessContext,
) -> MemoryToolRegistry:
    """Compose the Memory tool storage-backend registry and bind to ctx.

    Mutates `ctx` in-place: binds `ctx.memory_tool_registry` to the
    constructed registry. Returns the registry for the stage-5 callsite to
    inspect.

    Per spec v1.17 §14.12.3 + plan v2.15 §1 U-RT-80 ACs.
    """
    # --- Step 1: resolve enum value -----------------------------------------
    if config.memory_tool_backend_config is not None:
        configured = config.memory_tool_backend_config.backend
    else:
        admissible = memory_tool_storage_backend(config.deployment_surface)
        if MemoryToolStorageBackend.FILESYSTEM not in admissible:
            raise MemoryBackendResolutionError(
                f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: deployment surface "
                f"{config.deployment_surface.value!r} admits backends "
                f"{sorted(b.value for b in admissible)!r}; v2.15 implements only "
                f"{MemoryToolStorageBackend.FILESYSTEM.value!r} per fork-doc §14.D "
                f"(non-FILESYSTEM backends deferred to follow-on retirement-batch arc)"
            )
        configured = MemoryToolStorageBackend.FILESYSTEM

    # --- Step 2: construct backend implementation ---------------------------
    if configured is MemoryToolStorageBackend.FILESYSTEM:
        backend: MemoryToolStorageBackendProtocol = LocalFilesystemMemoryToolBackend(
            root=config.repository_root / MEMORY_TOOL_FILESYSTEM_ROOT_SUBPATH,
        )
    else:
        raise MemoryBackendResolutionError(
            f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: backend "
            f"{configured.value!r} has no implementation landed at v2.15 "
            f"(deferred to follow-on retirement-batch arc per fork-doc §14.D)"
        )

    # --- Step 3: Protocol-conformance enforcement per §14.12.5 invariant 2 --
    # Two-layer check: (a) attribute-present + callable sweep over the 5
    # CRUD methods catches both missing methods AND non-callable shadowing
    # (the latter is admitted by `@runtime_checkable` isinstance per PEP 544
    # caveat); (b) final `@runtime_checkable` isinstance as the canonical
    # Protocol assertion.
    missing = tuple(name for name in PROTOCOL_REQUIRED_METHODS if not hasattr(backend, name))
    if missing:
        raise MemoryBackendResolutionError(
            f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: constructed backend for "
            f"{configured.value!r} does not satisfy "
            f"MemoryToolStorageBackendProtocol "
            f"(missing methods: {missing!r})"
        )
    non_callable = tuple(
        name for name in PROTOCOL_REQUIRED_METHODS if not callable(getattr(backend, name))
    )
    if non_callable:
        raise MemoryBackendResolutionError(
            f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: backend for "
            f"{configured.value!r} has non-callable Protocol method(s): "
            f"{non_callable!r}"
        )
    # pyright sees `backend` as always `LocalFilesystemMemoryToolBackend`
    # at this branch (the only constructor reached), but the isinstance is
    # the spec §14.12.5 invariant 2 canonical Protocol assertion — kept
    # intentionally as defense-in-depth for tests that inject incomplete
    # backends via constructor monkey-patching (AC #7).
    if not isinstance(backend, MemoryToolStorageBackendProtocol):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise MemoryBackendResolutionError(
            f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: constructed backend for "
            f"{configured.value!r} does not satisfy "
            f"MemoryToolStorageBackendProtocol isinstance check"
        )

    # --- Step 4: construct registry + bind to ctx ---------------------------
    registry = MemoryToolRegistry(
        backend=backend,
        configured_backend=configured,
    )
    ctx.memory_tool_registry = registry
    return registry

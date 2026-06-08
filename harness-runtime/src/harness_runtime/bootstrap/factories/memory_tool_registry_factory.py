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

import importlib
from pathlib import Path
from typing import Any, cast

from harness_as.anthropic_graceful_degradation import (
    MemoryToolStorageBackend,
    memory_tool_storage_backend,
)

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.memory_tool_filesystem import (
    LocalFilesystemMemoryToolBackend,
)
from harness_runtime.lifecycle.memory_tool_registry import MemoryToolRegistry
from harness_runtime.lifecycle.memory_tool_s3 import S3ClientProtocol, S3MemoryToolBackend
from harness_runtime.lifecycle.memory_tool_sqlite import SqliteMemoryToolBackend
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryBackendResolutionError,
    MemoryToolBackendConfig,
    MemoryToolStorageBackendProtocol,
)
from harness_runtime.types import RuntimeConfig

__all__ = [
    "MEMORY_TOOL_DATABASE_SUBPATH",
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


MEMORY_TOOL_DATABASE_SUBPATH = ".harness/memories.db"
"""Default sub-path under `config.repository_root` for the DATABASE backend
SQLite file, used when `backend_params['connection_string']` is absent (R-830;
spec §14.12.3 DATABASE step). Sibling of the FILESYSTEM `.harness/memories`
root."""


def _resolve_database_connection_path(config: RuntimeConfig) -> Path:
    """Resolve the SQLite database path for the DATABASE backend.

    Per spec §14.12.3 DATABASE step, the connection is supplied via
    `backend_params['connection_string']`. When that key is absent (or
    `backend_params` is `None`), fall back to the workspace default
    `config.repository_root / MEMORY_TOOL_DATABASE_SUBPATH`.
    """
    backend_cfg = config.memory_tool_backend_config
    if backend_cfg is not None and backend_cfg.backend_params is not None:
        connection_string = backend_cfg.backend_params.get("connection_string")
        if connection_string:
            return Path(connection_string)
    return config.repository_root / MEMORY_TOOL_DATABASE_SUBPATH


def _require_backend_params(
    backend_cfg: MemoryToolBackendConfig | None,
    *,
    backend: MemoryToolStorageBackend,
) -> dict[str, str]:
    if backend_cfg is None or backend_cfg.backend_params is None:
        raise MemoryBackendResolutionError(
            f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: backend {backend.value!r} "
            f"requires memory_tool_backend_config.backend_params"
        )
    return dict(backend_cfg.backend_params)


def _create_s3_client_from_backend_params(params: dict[str, str]) -> S3ClientProtocol:
    """Lazily construct a boto3 S3 client from operator backend params.

    boto3 is intentionally optional: provider-free CI monkeypatches this
    function, while live MANAGED_CLOUD use requires the operator to install the
    dependency and provide ambient AWS credentials or equivalent boto3 config.
    """
    try:
        boto3 = importlib.import_module("boto3")
    except ImportError as exc:
        raise MemoryBackendResolutionError(
            "RT-FAIL-MEMORY-BACKEND-RESOLUTION: backend 's3' requires optional "
            "dependency boto3 for live client construction; provider-free tests "
            "may monkeypatch _create_s3_client_from_backend_params"
        ) from exc

    client_kwargs: dict[str, str] = {}
    for key in ("region_name", "endpoint_url", "profile_name"):
        value = params.get(key)
        if value:
            client_kwargs[key] = value

    boto3_module = cast(Any, boto3)
    if "profile_name" in client_kwargs:
        profile_name = client_kwargs.pop("profile_name")
        session = boto3_module.Session(profile_name=profile_name)
        return cast(S3ClientProtocol, session.client("s3", **client_kwargs))
    return cast(S3ClientProtocol, boto3_module.client("s3", **client_kwargs))


def _construct_s3_backend(config: RuntimeConfig) -> S3MemoryToolBackend:
    params = _require_backend_params(
        config.memory_tool_backend_config,
        backend=MemoryToolStorageBackend.S3,
    )
    bucket = params.get("bucket")
    if not bucket:
        raise MemoryBackendResolutionError(
            "RT-FAIL-MEMORY-BACKEND-RESOLUTION: backend 's3' requires backend_params['bucket']"
        )
    client = _create_s3_client_from_backend_params(params)
    return S3MemoryToolBackend(
        bucket=bucket,
        key_prefix=params.get("key_prefix", ""),
        client=client,
    )


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
    elif configured is MemoryToolStorageBackend.DATABASE:
        # R-830 SELF_HOSTED_SERVER DATABASE backend (local embedded SQLite).
        # NOT the remaining optional MANAGED_CLOUD managed-DB backend. S3 is
        # implemented separately below; ENCRYPTED_FILESYSTEM / OPERATOR_DEFINED
        # still raise, and the surface-default path still picks FILESYSTEM only
        # when admitted (DATABASE reaches here via explicit operator override).
        backend = SqliteMemoryToolBackend(db_path=_resolve_database_connection_path(config))
    elif configured is MemoryToolStorageBackend.S3:
        # R-830 MANAGED_CLOUD cloud-vault backend. Provider-free construction
        # reaches this path through a monkeypatched client factory; live use
        # requires boto3 + operator-provided credentials and bucket params.
        backend = _construct_s3_backend(config)
    else:
        raise MemoryBackendResolutionError(
            f"RT-FAIL-MEMORY-BACKEND-RESOLUTION: backend "
            f"{configured.value!r} has no implementation landed "
            f"(FILESYSTEM + DATABASE + S3 landed; ENCRYPTED_FILESYSTEM / "
            f"OPERATOR_DEFINED deferred to operator-discretion follow-on arcs "
            f"per spec §14.D + §16 §6.C v2 C.vii)"
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

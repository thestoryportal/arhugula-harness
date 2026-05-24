"""U-RT-80 — Stage 5 factory ``materialize_memory_tool_registry_stage`` tests.

ACs per ``Implementation_Plan_Harness_Runtime_v2_14.md`` §1 U-RT-80 (preserved
verbatim at v2.15). Spec contract: ``Spec_Harness_Runtime_v1.md`` v1.17
§14.12.3 stage-5 factory contract + §14.12.4 fail-class taxonomy + §14.12.5
invariant 2 Protocol-conformance enforcement.

Note on plan-prose typo: plan AC #1 names ``DeploymentSurface.LOCAL_DEV``;
the actual enum value is ``DeploymentSurface.LOCAL_DEVELOPMENT`` per
``harness_core/deployment_surface.py:33``. Tests use the correct identifier.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness_as.anthropic_graceful_degradation import MemoryToolStorageBackend
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern

from harness_runtime.bootstrap.factories.memory_tool_registry_factory import (
    MEMORY_TOOL_FILESYSTEM_ROOT_SUBPATH,
    materialize_memory_tool_registry_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.memory_tool_filesystem import (
    LocalFilesystemMemoryToolBackend,
)
from harness_runtime.lifecycle.memory_tool_registry import MemoryToolRegistry
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryBackendResolutionError,
    MemoryToolBackendConfig,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _config(
    *,
    memory_tool_backend_config: MemoryToolBackendConfig | None = None,
    deployment_surface: DeploymentSurface = DeploymentSurface.LOCAL_DEVELOPMENT,
    repository_root: Path | None = None,
) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=deployment_surface,
        repository_root=repository_root if repository_root is not None else Path("/tmp"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        memory_tool_backend_config=memory_tool_backend_config,
    )


# ---------------------------------------------------------------------------
# AC #1 — default path: backend_config=None at LOCAL_DEVELOPMENT → FILESYSTEM.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_default_resolver_picks_filesystem_at_local_development(
    tmp_path: Path,
) -> None:
    cfg = _config(repository_root=tmp_path)
    ctx = _MutableHarnessContext()

    registry = await materialize_memory_tool_registry_stage(cfg, ctx)

    assert isinstance(registry, MemoryToolRegistry)
    assert registry.configured_backend is MemoryToolStorageBackend.FILESYSTEM


# ---------------------------------------------------------------------------
# AC #2 — operator override: explicit FILESYSTEM honored.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_operator_override_filesystem_honored(tmp_path: Path) -> None:
    cfg = _config(
        memory_tool_backend_config=MemoryToolBackendConfig(
            backend=MemoryToolStorageBackend.FILESYSTEM,
        ),
        repository_root=tmp_path,
    )
    ctx = _MutableHarnessContext()

    registry = await materialize_memory_tool_registry_stage(cfg, ctx)

    assert registry.configured_backend is MemoryToolStorageBackend.FILESYSTEM


# ---------------------------------------------------------------------------
# AC #3 — operator override: S3 (and other non-FILESYSTEM) raise with
# RT-FAIL-MEMORY-BACKEND-RESOLUTION + fork-doc §14.D pointer.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "unimplemented_backend",
    [
        MemoryToolStorageBackend.S3,
        MemoryToolStorageBackend.DATABASE,
        MemoryToolStorageBackend.ENCRYPTED_FILESYSTEM,
        MemoryToolStorageBackend.OPERATOR_DEFINED,
    ],
)
async def test_unimplemented_backend_raises_with_fork_doc_pointer(
    unimplemented_backend: MemoryToolStorageBackend,
    tmp_path: Path,
) -> None:
    cfg = _config(
        memory_tool_backend_config=MemoryToolBackendConfig(backend=unimplemented_backend),
        repository_root=tmp_path,
    )
    ctx = _MutableHarnessContext()

    with pytest.raises(MemoryBackendResolutionError) as excinfo:
        await materialize_memory_tool_registry_stage(cfg, ctx)

    msg = str(excinfo.value)
    assert "RT-FAIL-MEMORY-BACKEND-RESOLUTION" in msg
    assert unimplemented_backend.value in msg
    # Fork-doc pointer per `[[halt-route-split-AC-pattern]]` carry-forward.
    assert "§14.D" in msg
    assert ctx.memory_tool_registry is None  # never bound on resolution failure


# ---------------------------------------------------------------------------
# AC #4 — stage-5 LOOP_INIT invocation: ctx.memory_tool_registry bound after
# stage 5 with non-None .backend (verified via the resolve_backend Protocol
# accessor + pre-bound builder state mirroring full-bootstrap invariants).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_factory_binds_registry_on_ctx_with_non_none_backend(
    tmp_path: Path,
) -> None:
    cfg = _config(repository_root=tmp_path)
    ctx = _MutableHarnessContext()

    await materialize_memory_tool_registry_stage(cfg, ctx)

    assert ctx.memory_tool_registry is not None
    backend = ctx.memory_tool_registry.resolve_backend(cfg.deployment_surface)
    assert backend is not None
    assert isinstance(backend, LocalFilesystemMemoryToolBackend)


# ---------------------------------------------------------------------------
# AC #5 — bootstrap-abort behavior: a raise from the factory propagates as
# fail-closed (no swallowing); ctx.memory_tool_registry remains None per AC #3.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_factory_failure_propagates_fail_closed(tmp_path: Path) -> None:
    cfg = _config(
        memory_tool_backend_config=MemoryToolBackendConfig(
            backend=MemoryToolStorageBackend.S3,
        ),
        repository_root=tmp_path,
    )
    ctx = _MutableHarnessContext()

    with pytest.raises(MemoryBackendResolutionError):
        await materialize_memory_tool_registry_stage(cfg, ctx)

    assert ctx.memory_tool_registry is None


# ---------------------------------------------------------------------------
# AC #6 — integration: registry.configured_backend == FILESYSTEM and
# resolve_backend(LOCAL_DEVELOPMENT) returns a LocalFilesystemMemoryToolBackend
# under the default-config path.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_default_path_yields_filesystem_backend(tmp_path: Path) -> None:
    cfg = _config(repository_root=tmp_path)
    ctx = _MutableHarnessContext()

    await materialize_memory_tool_registry_stage(cfg, ctx)

    assert ctx.memory_tool_registry.configured_backend is MemoryToolStorageBackend.FILESYSTEM
    backend = ctx.memory_tool_registry.resolve_backend(DeploymentSurface.LOCAL_DEVELOPMENT)
    assert isinstance(backend, LocalFilesystemMemoryToolBackend)


# ---------------------------------------------------------------------------
# AC #7 — Protocol-conformance enforcement: backend missing a method raises
# RT-FAIL-MEMORY-BACKEND-RESOLUTION naming the missing method(s).
# Verified via monkey-patching the FILESYSTEM constructor to return an
# incomplete object — exercises step 3 introspection.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_incomplete_protocol_backend_raises_with_missing_method_names(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class IncompleteBackend:
        async def view(self, path: str) -> bytes:  # noqa: ARG002
            return b""

        # create / delete / str_replace / insert intentionally missing.

    def _fake_ctor(*, root: Path) -> IncompleteBackend:  # noqa: ARG001
        return IncompleteBackend()

    monkeypatch.setattr(
        "harness_runtime.bootstrap.factories.memory_tool_registry_factory."
        "LocalFilesystemMemoryToolBackend",
        _fake_ctor,
    )

    cfg = _config(repository_root=tmp_path)
    ctx = _MutableHarnessContext()

    with pytest.raises(MemoryBackendResolutionError) as excinfo:
        await materialize_memory_tool_registry_stage(cfg, ctx)

    msg = str(excinfo.value)
    assert "RT-FAIL-MEMORY-BACKEND-RESOLUTION" in msg
    # Names at least one of the missing Protocol methods.
    assert any(name in msg for name in ("create", "delete", "str_replace", "insert"))


@pytest.mark.asyncio
async def test_non_callable_protocol_attribute_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Defense-in-depth: PEP 544 @runtime_checkable accepts non-callable
    attributes that shadow method names; the factory rejects them."""

    class NonCallableBackend:
        view = None  # non-callable shadow
        create = None
        delete = None
        str_replace = None
        insert = None

    def _fake_ctor(*, root: Path) -> NonCallableBackend:  # noqa: ARG001
        return NonCallableBackend()

    monkeypatch.setattr(
        "harness_runtime.bootstrap.factories.memory_tool_registry_factory."
        "LocalFilesystemMemoryToolBackend",
        _fake_ctor,
    )

    cfg = _config(repository_root=tmp_path)
    ctx = _MutableHarnessContext()

    with pytest.raises(MemoryBackendResolutionError) as excinfo:
        await materialize_memory_tool_registry_stage(cfg, ctx)

    assert "non-callable" in str(excinfo.value)


# ---------------------------------------------------------------------------
# AC #8 — importable + pyright strict pass. Importable verified by the
# imports at top of this module; pyright strict run separately at CI/local
# `pyright --project harness-runtime`.
# ---------------------------------------------------------------------------


def test_factory_symbol_importable() -> None:
    # Re-import via module-level attribute to assert public-API surface.
    from harness_runtime.bootstrap.factories import memory_tool_registry_factory

    assert callable(memory_tool_registry_factory.materialize_memory_tool_registry_stage)
    assert memory_tool_registry_factory.MEMORY_TOOL_FILESYSTEM_ROOT_SUBPATH == (
        ".harness/memories"
    )
    assert memory_tool_registry_factory.PROTOCOL_REQUIRED_METHODS == (
        "view",
        "create",
        "delete",
        "str_replace",
        "insert",
    )


# ---------------------------------------------------------------------------
# Additional: filesystem-root path is resolved per
# config.repository_root / ".harness/memories" — verifies step 2a sub-path.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_filesystem_backend_rooted_at_repository_subpath(tmp_path: Path) -> None:
    cfg = _config(repository_root=tmp_path)
    ctx = _MutableHarnessContext()

    await materialize_memory_tool_registry_stage(cfg, ctx)

    backend = ctx.memory_tool_registry.resolve_backend(cfg.deployment_surface)
    expected_root = (tmp_path / MEMORY_TOOL_FILESYSTEM_ROOT_SUBPATH).resolve()
    # LocalFilesystemMemoryToolBackend keeps the resolved root at `_root`.
    assert backend._root == expected_root  # type: ignore[attr-defined]

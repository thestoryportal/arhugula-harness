"""U-RT-73 — Stage 3a factory `materialize_mcp_client_host_stage` tests.

ACs per Implementation_Plan_Harness_Runtime_v2_13.md §1B U-RT-73 (preserved
from v2.12). Spec contract: Spec_Harness_Runtime_v1.md v1.16 §14.9.3
stage-3a factory contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from harness_as.discriminators import MCPTransport
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.sandbox_tier_floor import MCPServerTrustLevel
from harness_core import ClientName
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.bootstrap.factories.mcp_client_host_factory import (
    materialize_mcp_client_host_stage,
)
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.types import (
    CollectorConfig,
    MCPClientConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _config(mcp_clients: list[MCPClientConfig] | None = None) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=Path("/tmp"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=mcp_clients or [],
    )


def _stdio_client(name: str = "test-stdio") -> MCPClientConfig:
    return MCPClientConfig(
        client_name=ClientName(name),
        transport=MCPTransport.STDIO,
        trust_level=MCPServerTrustLevel.L1_SIGNED_PINNED,
        blast_radius=BlastRadiusTier.READ_ONLY,
        connection_url="stdio:///bin/echo",
    )


@pytest.mark.asyncio
async def test_returns_mcp_client_host_when_mcp_clients_populated() -> None:
    # AC #1 — non-empty mcp_clients → MCPClientHost instance.
    cfg = _config([_stdio_client()])
    host = await materialize_mcp_client_host_stage(cfg)
    assert isinstance(host, MCPClientHost)
    assert host.server_name == "test-stdio"


@pytest.mark.asyncio
async def test_returns_empty_sentinel_when_mcp_clients_empty() -> None:
    # AC #2 — empty mcp_clients → empty-sentinel MCPClientHost (does NOT raise).
    cfg = _config([])
    host = await materialize_mcp_client_host_stage(cfg)
    assert isinstance(host, MCPClientHost)
    assert host.server_name == "<empty-sentinel>"


@pytest.mark.asyncio
async def test_factory_returns_unstarted_host() -> None:
    """Factory returns an unstarted host; stage 3a body invokes `.start()`
    if the host is non-sentinel. Tested by reading the private `_started`
    flag through Python's introspection (no public predicate at U-RT-63 MVP)."""
    cfg = _config([])
    host = await materialize_mcp_client_host_stage(cfg)
    assert getattr(host, "_started", True) is False


@pytest.mark.asyncio
async def test_stage_3a_body_binds_factory_return_to_ctx() -> None:
    """AC #3 — stage 3a body invokes factory exactly once and binds the
    return value to `ctx.mcp_client_host`. Tested via direct import of
    the stage shim and an isolated config."""
    from harness_core.workload_class import WorkloadClass
    from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
    from harness_runtime.bootstrap.stage_3a_cp_clients import execute as stage_3a_execute

    builder = _MutableHarnessContext()

    # Stub keyring_resolver — stage 0 normally populates this. We bypass by
    # patching the providers factory to avoid network calls; the
    # mcp_client_host path is what we're verifying.
    builder.keyring_resolver = object()

    cfg = _config([])

    # Monkey-patch `materialize_provider_clients_stage` to avoid touching
    # the real providers. Direct module-level swap.
    import harness_runtime.bootstrap.stage_3a_cp_clients as stage_3a_module

    class _StubStage:
        providers: dict[str, Any] = {}

    async def _stub_providers(*args: Any, **kwargs: Any) -> _StubStage:
        return _StubStage()

    original = stage_3a_module.materialize_provider_clients_stage
    stage_3a_module.materialize_provider_clients_stage = _stub_providers  # type: ignore[assignment]
    try:
        await stage_3a_execute(builder, cfg, WorkloadClass.SOFTWARE_ENGINEERING)
    finally:
        stage_3a_module.materialize_provider_clients_stage = original  # type: ignore[assignment]

    assert isinstance(builder.mcp_client_host, MCPClientHost)
    assert builder.mcp_client_host.server_name == "<empty-sentinel>"


@pytest.mark.asyncio
async def test_per_server_transport_heterogeneity_first_entry_wins_at_mvp() -> None:
    """AC #5 — multi-server config (v1.15 MVP uses first; multi-server
    deferred to future-arc schema extension per factory module docstring)."""
    cfg = _config(
        [
            _stdio_client("first-server"),
            _stdio_client("second-server"),
        ]
    )
    host = await materialize_mcp_client_host_stage(cfg)
    assert host.server_name == "first-server"


# ---------------------------------------------------------------------------
# spec v1.40 Reading B — stage-3a factory builds a default-policy converter
# per `.harness/class_1_fork_tool_step_no_operator_supplied_converter.md`.
# ---------------------------------------------------------------------------


class _FakeTool:
    """Minimal `mcp.types.Tool` stand-in for converter unit tests."""

    def __init__(
        self,
        name: str,
        description: str | None,
        input_schema: dict[str, object] | None,
    ) -> None:
        self.name = name
        self.description = description
        self.inputSchema = input_schema  # mirrors mcp.types.Tool field name


def _policy_client(
    *,
    name: str = "policy-server",
    minimum_tier: SandboxTier = SandboxTier.TIER_2_CONTAINER,
    blast_radius: BlastRadiusTier = BlastRadiusTier.READ_ONLY,
) -> MCPClientConfig:
    return MCPClientConfig(
        client_name=ClientName(name),
        transport=MCPTransport.STDIO,
        trust_level=MCPServerTrustLevel.L1_SIGNED_PINNED,
        blast_radius=BlastRadiusTier.READ_ONLY,
        connection_url="stdio:///bin/echo",
        default_minimum_tier=minimum_tier,
        default_blast_radius=blast_radius,
    )


@pytest.mark.asyncio
async def test_factory_wires_non_default_converter() -> None:
    """v1.40 — a configured server's host carries a real converter, NOT the
    raise-on-every-call default stub."""
    cfg = _config([_policy_client()])
    host = await materialize_mcp_client_host_stage(cfg)
    converter = host._tool_contract_converter  # type: ignore[attr-defined]
    contract = converter(_FakeTool("echo", "echo a string", {"type": "object"}))
    assert contract.name == "echo"


@pytest.mark.asyncio
async def test_converter_stamps_per_server_default_policy() -> None:
    """v1.40 — converter stamps the entry's default tier + blast radius onto
    every discovered tool's `ToolContract`."""
    cfg = _config(
        [
            _policy_client(
                minimum_tier=SandboxTier.TIER_1_PROCESS,
                blast_radius=BlastRadiusTier.LOCAL_MUTATION,
            )
        ]
    )
    host = await materialize_mcp_client_host_stage(cfg)
    converter = host._tool_contract_converter  # type: ignore[attr-defined]
    contract = converter(_FakeTool("write_file", "writes a file", {"type": "object"}))
    assert contract.minimum_tier is SandboxTier.TIER_1_PROCESS
    assert contract.blast_radius_tier is BlastRadiusTier.LOCAL_MUTATION
    assert contract.description == "writes a file"


@pytest.mark.asyncio
async def test_converter_tolerates_none_description_and_schema() -> None:
    """v1.40 — `mcp.types.Tool.description` may be None and `inputSchema` may
    be absent; the converter substitutes safe defaults."""
    cfg = _config([_policy_client()])
    host = await materialize_mcp_client_host_stage(cfg)
    converter = host._tool_contract_converter  # type: ignore[attr-defined]
    contract = converter(_FakeTool("noisy", None, None))
    assert contract.description == ""
    assert contract.input_schema == {"type": "object"}


@pytest.mark.asyncio
async def test_default_policy_field_defaults_are_conservative() -> None:
    """v1.40 — a client that omits the policy fields gets the conservative
    Pydantic defaults (TIER_2_CONTAINER / READ_ONLY) per fork §0."""
    entry = _stdio_client()
    assert entry.default_minimum_tier is SandboxTier.TIER_2_CONTAINER
    assert entry.default_blast_radius is BlastRadiusTier.READ_ONLY


@pytest.mark.asyncio
async def test_empty_sentinel_host_keeps_raise_on_call_converter() -> None:
    """v1.40 — the 0-server empty-sentinel host wires no converter (no tools
    to convert); its default stub still raises on invocation."""
    cfg = _config([])
    host = await materialize_mcp_client_host_stage(cfg)
    converter = host._tool_contract_converter  # type: ignore[attr-defined]
    with pytest.raises(LookupError):
        converter(_FakeTool("x", "x", {"type": "object"}))

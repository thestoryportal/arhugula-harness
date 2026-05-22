"""U-RT-63 — `MCPClientHost` class skeleton + transport selector.

Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-63 ACs:
1. `__init__` accepts transport literal + raises `ValueError` on unknown
2. `MCPHostHealth` dataclass instantiable with all 6 fields per §14.9.1
3. `tool_registry` property raises `MCPHostNotStartedError` before `start()`
4. Importable; pyright strict
5. Coverage ≥ 90% on the skeleton
"""

from __future__ import annotations

import pytest

from harness_cp.cp_shared_types import MCPTrustTier

from harness_runtime.lifecycle.mcp_client_host import (
    MCPClientHost,
    MCPHostAlreadyStartedError,
    MCPHostHealth,
    MCPHostNotStartedError,
)


# ---------- AC #1 — transport literal validation ----------------------------


@pytest.mark.parametrize("transport", ["stdio", "streamable_http", "sse"])
def test_init_accepts_each_valid_transport(transport: str) -> None:
    host = MCPClientHost(
        transport=transport,  # type: ignore[arg-type]
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={},
    )
    assert host.transport == transport
    assert host.server_name == "srv-1"
    assert host.trust_tier is MCPTrustTier.LEVEL_2_SANDBOX_ALL
    assert host.started is False


def test_init_rejects_unknown_transport() -> None:
    with pytest.raises(ValueError, match="unknown MCP transport 'websocket'"):
        MCPClientHost(
            transport="websocket",  # type: ignore[arg-type]
            server_name="srv-1",
            trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
            transport_config={},
        )


def test_init_rejects_empty_string_transport() -> None:
    with pytest.raises(ValueError, match="unknown MCP transport ''"):
        MCPClientHost(
            transport="",  # type: ignore[arg-type]
            server_name="srv-1",
            trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
            transport_config={},
        )


# ---------- AC #2 — MCPHostHealth dataclass shape ---------------------------


def test_mcp_host_health_instantiates_with_six_fields() -> None:
    health = MCPHostHealth(
        alive=True,
        last_ping_ms=42,
        protocol_version="2025-06-18",
        transport="stdio",
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT,
    )
    assert health.alive is True
    assert health.last_ping_ms == 42
    assert health.protocol_version == "2025-06-18"
    assert health.transport == "stdio"
    assert health.server_name == "srv-1"
    assert health.trust_tier is MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT


def test_mcp_host_health_is_frozen() -> None:
    health = MCPHostHealth(
        alive=False,
        last_ping_ms=0,
        protocol_version="2025-06-18",
        transport="sse",
        server_name="srv-2",
        trust_tier=MCPTrustTier.LEVEL_1_SIGNED_PINNED,
    )
    with pytest.raises(Exception):
        health.alive = True  # type: ignore[misc]


# ---------- AC #3 — tool_registry raises pre-start --------------------------


def test_tool_registry_raises_pre_start() -> None:
    host = MCPClientHost(
        transport="stdio",
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={},
    )
    with pytest.raises(MCPHostNotStartedError, match="srv-1"):
        _ = host.tool_registry


# ---------- AC #4 — importability (covered by module-level imports) ---------


def test_module_exports_public_surface() -> None:
    from harness_runtime.lifecycle import mcp_client_host as mod

    assert "MCPClientHost" in mod.__all__
    assert "MCPHostHealth" in mod.__all__
    assert "MCPHostNotStartedError" in mod.__all__
    assert "MCPHostAlreadyStartedError" in mod.__all__
    assert "MCPTransport" in mod.__all__


# ---------- AC #5 — skeleton methods raise NotImplementedError --------------


@pytest.mark.asyncio
async def test_start_raises_not_implemented_pre_u_rt_64() -> None:
    host = MCPClientHost(
        transport="stdio",
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={},
    )
    with pytest.raises(NotImplementedError, match="U-RT-64"):
        await host.start()


@pytest.mark.asyncio
async def test_health_check_raises_not_implemented_pre_per_transport() -> None:
    host = MCPClientHost(
        transport="streamable_http",
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={},
    )
    with pytest.raises(NotImplementedError):
        await host.health_check()


@pytest.mark.asyncio
async def test_shutdown_raises_not_implemented_pre_per_transport() -> None:
    host = MCPClientHost(
        transport="sse",
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={},
    )
    with pytest.raises(NotImplementedError):
        await host.shutdown()


@pytest.mark.asyncio
async def test_call_tool_raises_not_implemented_pre_per_transport() -> None:
    host = MCPClientHost(
        transport="stdio",
        server_name="srv-1",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={},
    )
    with pytest.raises(NotImplementedError):
        await host.call_tool("some_tool", {}, "idempotency-1")


# ---------- AlreadyStartedError typed (used by U-RT-64) ---------------------


def test_already_started_error_is_runtime_error_subclass() -> None:
    assert issubclass(MCPHostAlreadyStartedError, RuntimeError)
    assert issubclass(MCPHostNotStartedError, RuntimeError)

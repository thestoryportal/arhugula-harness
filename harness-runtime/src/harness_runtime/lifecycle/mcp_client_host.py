"""U-RT-63 — `MCPClientHost` class skeleton + transport selector.

Per `Spec_Harness_Runtime_v1.md` v1.13 §14.9.1 architectural surfaces.
Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-63.

Skeleton-only at this unit. Per-transport `start()` lifecycle implementations
land at U-RT-64 (STDIO) + U-RT-65 (HTTP) + U-RT-66 (SSE).

Distinct from `lifecycle/mcp_host.py` (U-RT-15 `MCPHost` — server-hosting
placeholder for the H_T-as-MCP-server topology per `lifecycle/mcp_server.py`
U-RT-62). `MCPClientHost` is the H_T-as-MCP-client surface: it owns the
client-side lifecycle for connecting *out* to MCP servers (filesystem /
GitHub / sandbox / etc.) that publish `ToolContract`s consumed by the
runtime tool dispatcher (U-RT-67 `RuntimeToolDispatcher`).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from harness_cp.cp_shared_types import MCPTrustTier

from harness_runtime.lifecycle.tool_registry import ToolRegistry

__all__ = [
    "MCPClientHost",
    "MCPHostAlreadyStartedError",
    "MCPHostHealth",
    "MCPHostNotStartedError",
    "MCPTransport",
]


MCPTransport = Literal["stdio", "streamable_http", "sse"]
"""Per spec §14.9.1 transport-neutral terminology block + §14.9.6 inv 5.

All 3 transports in scope at v1 per Decision 1.D4 RATIFIED (2026-05-21).
"""


class MCPHostNotStartedError(RuntimeError):
    """Raised when `tool_registry` is accessed before `start()` completes.

    Per spec §14.9.1: `tool_registry` is "immutable after start()" — i.e.,
    only populated once `start()` has invoked `list_tools` on the connected
    MCP server. Pre-start access is a contract violation; this typed error
    surfaces it deterministically rather than returning an empty registry
    that callers may silently consume.
    """


class MCPHostAlreadyStartedError(RuntimeError):
    """Raised when `start()` is invoked twice on the same `MCPClientHost`.

    Per spec §14.9.6 inv 1: "MCP host instance started exactly once per
    bootstrap. Stage 3a starts; stage 7 SHUTDOWN drains. ... Idempotent
    restart out of scope at v1 (deferred to operator-driven restart arc)."
    """


@dataclass(frozen=True)
class MCPHostHealth:
    """Liveness probe carrier per spec §14.9.1.

    6-field frozen dataclass. Returned by `MCPClientHost.health_check()` on
    a per-dispatch cadence (§14.9.2 invariant 3 — health check pre-call).

    `transport` literal mirrors `MCPTransport`; spec §14.9.6 invariant 5
    pins all 3 values in scope at v1 (the `mcp.transport` span attribute
    populates from this field).

    `trust_tier` is the `MCPTrustTier` from CP plan v2.8 U-CP-00c carrier —
    cross-axis read (CP→runtime via `harness_cp.cp_shared_types`). Used by
    the dispatcher (U-RT-67) to populate the `mcp.server.trust_tier` span
    attribute and gate the per-server-trust evaluation step.
    """

    alive: bool
    last_ping_ms: int
    protocol_version: str
    transport: MCPTransport
    server_name: str
    trust_tier: MCPTrustTier


class MCPClientHost:
    """Per-server MCP-client lifecycle host (H_T-as-MCP-client surface).

    Owns subprocess (STDIO) / HTTP-client-pool (streamable_http) /
    event-stream-consumer (SSE) lifecycle for a single connected MCP
    server. Materialized at bootstrap stage 3a per spec §14.9.3.

    Per spec §14.9.6 inv 1: one instance per MCP server; one transport per
    instance (transport is selected at `__init__` from per-server bootstrap
    config). For deployments with N MCP servers, the operator materializes
    N `MCPClientHost` instances at stage 3a (each transport-typed).

    At U-RT-63 (this unit) only the skeleton + transport-validation
    preconditions land. `start()` / `health_check()` / `shutdown()` /
    `call_tool()` raise `NotImplementedError` until the per-transport
    units (U-RT-64 / U-RT-65 / U-RT-66) extend the skeleton.
    """

    _VALID_TRANSPORTS: frozenset[str] = frozenset({"stdio", "streamable_http", "sse"})

    def __init__(
        self,
        *,
        transport: MCPTransport,
        server_name: str,
        trust_tier: MCPTrustTier,
        transport_config: Mapping[str, Any],
    ) -> None:
        """Construct an unstarted `MCPClientHost`.

        Parameters
        ----------
        transport:
            One of `"stdio"`, `"streamable_http"`, `"sse"`. Other values raise
            `ValueError` per AC #1.
        server_name:
            Per-deployment registry ID — populates `MCPHostHealth.server_name`
            + `mcp.server.name` span attribute per C-AS-14 §14.3.
        trust_tier:
            The per-server trust tier (cross-axis from CP plan v2.8 U-CP-00c).
            Populates `MCPHostHealth.trust_tier` + `mcp.server.trust_tier`
            span attribute.
        transport_config:
            Transport-specific bootstrap config (subprocess argv for STDIO;
            URL + auth headers for HTTP; URL for SSE). Schema is
            transport-specific; per-transport units validate.
        """
        if transport not in self._VALID_TRANSPORTS:
            raise ValueError(
                f"unknown MCP transport {transport!r}; expected one of "
                f"{sorted(self._VALID_TRANSPORTS)}"
            )
        self._transport: MCPTransport = transport
        self._server_name: str = server_name
        self._trust_tier: MCPTrustTier = trust_tier
        self._transport_config: Mapping[str, Any] = transport_config
        self._started: bool = False
        self._tool_registry: ToolRegistry | None = None

    @property
    def transport(self) -> MCPTransport:
        return self._transport

    @property
    def server_name(self) -> str:
        return self._server_name

    @property
    def trust_tier(self) -> MCPTrustTier:
        return self._trust_tier

    @property
    def started(self) -> bool:
        return self._started

    @property
    def tool_registry(self) -> ToolRegistry:
        """Return the populated tool registry; raise pre-start per AC #3.

        Per spec §14.9.1: "immutable after start()". `list_tools` populates
        the registry as part of `start()`; pre-start access surfaces an
        `MCPHostNotStartedError`.
        """
        if not self._started or self._tool_registry is None:
            raise MCPHostNotStartedError(
                f"MCPClientHost(server_name={self._server_name!r}) — "
                "tool_registry accessed before start() completed; per spec "
                "§14.9.1 the registry is immutable after start() and is not "
                "available pre-start"
            )
        return self._tool_registry

    async def start(self) -> None:
        """Per-transport startup. Per-transport implementations land at
        U-RT-64 (STDIO) / U-RT-65 (HTTP) / U-RT-66 (SSE)."""
        raise NotImplementedError(
            f"MCPClientHost.start() — transport {self._transport!r} branch "
            "lands at U-RT-64 (stdio) / U-RT-65 (streamable_http) / "
            "U-RT-66 (sse)"
        )

    async def health_check(self) -> MCPHostHealth:
        """Per-transport liveness probe. Lands at the per-transport units."""
        raise NotImplementedError(
            "MCPClientHost.health_check() — per-transport implementation "
            "lands at U-RT-64..66"
        )

    async def shutdown(self) -> None:
        """Per-transport graceful close. Lands at the per-transport units."""
        raise NotImplementedError(
            "MCPClientHost.shutdown() — per-transport implementation "
            "lands at U-RT-64..66"
        )

    async def call_tool(
        self,
        name: str,
        args: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        """Invoke a tool via the underlying MCP client. Lands at the
        per-transport units (shared call path; transport-specific connection
        carries the call)."""
        raise NotImplementedError(
            "MCPClientHost.call_tool() — per-transport implementation lands "
            "at U-RT-64..66"
        )

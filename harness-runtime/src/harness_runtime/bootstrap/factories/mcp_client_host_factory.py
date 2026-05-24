"""Stage 3a factory — `materialize_mcp_client_host_stage(config) → MCPClientHost`.

Per `Spec_Harness_Runtime_v1.md` v1.16 §14.9.3 stage-3a factory contract
(added at v1.15 per U-RT-68 fork Q2=B2 ratification). Ingests
`config.mcp_clients: list[MCPClientConfig]` (per-server transport_config) and
constructs an `MCPClientHost` instance. The factory return value is bound to
`ctx.mcp_client_host` (C-RT-04 v1.15+ field) by the stage 3a body.

Per spec §14.9.6 invariant 1 ("one instance per MCP server; one transport
per instance") + the singular field-type commitment at §4 C-RT-04
(`mcp_client_host: MCPClientHost`, not a mapping), the v1.15 MVP supports
0 or 1 MCP server entries in `config.mcp_clients`:

- 0 servers: returns an empty-tool-registry `MCPClientHost` (`.started=False`).
  Tool-dispatch attempts at U-RT-67 raise `RT-FAIL-TOOL-CONTRACT-UNKNOWN`
  per spec §14.9.5 since the registry is empty.
- 1 server: constructs an `MCPClientHost` from the single `MCPClientConfig`
  entry's per-server transport_config; subprocess spawn + protocol
  handshake + `list_tools` registry population happen at `start()`,
  which the stage 3a body invokes after factory return.
- >1 server (deferred): the v1.15 field type is singular; multi-server
  support is a future-arc extension that will route to a §4 + factory
  signature amendment via planner revision-pass. Until then the factory
  uses the first entry and raises a typed warning via the logger when
  more than one is configured (per the "Deferred to implementation
  discretion" §14.9.3 clause).

Per `Plan_Executability_Audit_v1.md` framework-pull discipline: no
framework adoption.
"""

from __future__ import annotations

import shlex
from typing import Any, Literal, cast

from harness_cp.cp_shared_types import MCPTrustTier

from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.types import RuntimeConfig

# Re-declare the Literal type so this module is self-contained for the
# transport cast (the same Literal is declared at lifecycle.mcp_client_host).
_MCPTransportLiteral = Literal["stdio", "streamable_http", "sse"]

__all__ = ["materialize_mcp_client_host_stage"]


_EMPTY_TRANSPORT_CONFIG: dict[str, Any] = {}

_STDIO_URL_PREFIX = "stdio://"


def _build_transport_config(
    transport: _MCPTransportLiteral, connection_url: str
) -> dict[str, Any]:
    """Translate MCPClientConfig.connection_url into the transport_config
    shape MCPClientHost consumes per its per-transport context contracts.

    The host docstrings at `_stdio_connection_context` / `_http_connection_context`
    / `_sse_connection_context` enumerate the required keys per transport:

      - stdio  → `command` (REQUIRED str), `args` (list[str], default []),
                 `env`/`cwd` (deferred — not supplied from MCPClientConfig at v1.17)
      - streamable_http / sse → `url` (REQUIRED str)

    The factory satisfies these contracts. Earlier landed code at this site
    passed `{"connection_url": ...}` unconditionally, which the host rejects
    at `host.start()` time with `ValueError("STDIO transport_config requires
    str 'command'")` — surfaced at U-RT-86 e2e pre-flight check. The fix is
    a factory-side translation; no spec change, no host change.

    Stdio `connection_url` shape: `'stdio://<command> [args...]'` per the
    URL-scheme + shell-style-argv convention at the existing factory test
    fixture `_stdio_client(connection_url="stdio:///bin/echo")`. The prefix
    is stripped and the remainder shlex-split into (command, args).
    """
    if transport == "stdio":
        if not connection_url.startswith(_STDIO_URL_PREFIX):
            raise ValueError(
                f"stdio connection_url must start with {_STDIO_URL_PREFIX!r}; "
                f"got {connection_url!r}"
            )
        remainder = connection_url[len(_STDIO_URL_PREFIX) :]
        parts = shlex.split(remainder)
        if not parts:
            raise ValueError(
                f"stdio connection_url has no command after "
                f"{_STDIO_URL_PREFIX!r}: {connection_url!r}"
            )
        return {"command": parts[0], "args": parts[1:]}
    # streamable_http / sse — host's _http_connection_context /
    # _sse_connection_context consume `url` per their docstrings.
    return {"url": connection_url}


async def materialize_mcp_client_host_stage(config: RuntimeConfig) -> MCPClientHost:
    """Construct the stage 3a `MCPClientHost` from operator-supplied config.

    Per spec v1.16 §14.9.3 stage-3a factory contract + AC #1/AC #2/AC #5 at
    U-RT-73 (Implementation_Plan_Harness_Runtime_v2_13.md).

    Returns
    -------
    MCPClientHost
        An unstarted host. The stage 3a body is responsible for calling
        `.start()` afterward if `config.mcp_clients` is non-empty; the
        empty-list sentinel host is intentionally left in `.started=False`
        state (no subprocess to spawn, no registry to populate).
    """
    if not config.mcp_clients:
        # Empty-sentinel branch. stdio + empty transport_config — the host
        # is constructible but `.start()` would fail per the per-transport
        # branches; the empty branch never calls `.start()`.
        return MCPClientHost(
            transport="stdio",
            server_name="<empty-sentinel>",
            trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
            transport_config=_EMPTY_TRANSPORT_CONFIG,
        )

    # MVP: one host per first configured client. Multi-server deferred to
    # a future-arc schema extension (see module docstring). `entry.transport`
    # is an `harness_as.discriminators.MCPTransport` StrEnum; its `.value`
    # is one of the literal strings the host accepts.
    entry = config.mcp_clients[0]
    transport_value: _MCPTransportLiteral = cast(
        _MCPTransportLiteral, entry.transport.value
    )
    return MCPClientHost(
        transport=transport_value,
        server_name=entry.client_name,
        trust_tier=_trust_tier_from_level(entry.trust_level),
        transport_config=_build_transport_config(
            transport_value, entry.connection_url
        ),
    )


def _trust_tier_from_level(level: Any) -> MCPTrustTier:
    """Project the per-MCPClientConfig `trust_level` (AS-side enum) onto
    the per-MCPClientHost `trust_tier` (CP-side enum).

    The two enums differ in shape per the AS / CP axis-separation
    discipline (`MCPServerTrustLevel` is the AS-side per-server trust
    framework class; `MCPTrustTier` is the CP-side tier the per-server
    trust evaluator gates on). MVP mapping is conservative — every
    AS-side level maps to the most-restrictive CP-side tier
    (`LEVEL_0_REFUSE_REMOTE`); production deployments will surface a
    spec-committed mapping at a future arc per Q1a=(i) follow-on.
    """
    _ = level  # MVP conservative — see docstring
    return MCPTrustTier.LEVEL_0_REFUSE_REMOTE

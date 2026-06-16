"""Stage 3a factory — `materialize_mcp_client_host_stage(config) → MCPClientHost`.

Per `Spec_Harness_Runtime_v1.md` §14.9.3 stage-3a factory contract (added at
v1.15 per U-RT-68 fork Q2=B2 ratification; reshaped singular→mapping at v1.51
§14.9.10 D1 per the B2 multi-server reshape). Ingests
`config.mcp_clients: list[MCPClientConfig]` (per-server transport_config) and
constructs `MCPClientHost` instances. The factory return value — a
`dict[ServerName, MCPClientHost]` keyed on each host's `server_name` — is bound
to `ctx.mcp_client_hosts` (C-RT-04 v1.51+ field) by the stage 3a body.

The field is now a mapping (§4 C-RT-04 v1.51 / U-RT-125). The factory handles:

- 0 servers: returns a 1-entry dict holding an empty-tool-registry
  `MCPClientHost` (`.started=False`) under the `<empty-sentinel>` key.
  Tool-dispatch attempts at U-RT-67 raise `RT-FAIL-TOOL-CONTRACT-UNKNOWN`
  per spec §14.9.5 since the registry is empty.
- 1 server: returns a 1-entry dict whose `MCPClientHost` is constructed from
  the single `MCPClientConfig` entry's per-server transport_config; subprocess
  spawn + protocol handshake + `list_tools` registry population happen at
  `start()`, which the stage 3a body invokes per-host after factory return.

**B2-impl-2a scope (carrier reshape).** This factory returns the mapping SHAPE
but still materializes a SINGLE host from `config.mcp_clients[0]` — honestly
single-host (no reachable multi-host path until the ≥2-server e2e fixture
lands). The materialize-ALL loop (U-RT-126-full), the cross-host routing index
+ collision fail-class (U-RT-127), and the per-host sandbox (U-RT-130) are
B2-impl-2b. The §14.9.6 inv-1 per-host lifecycle reword lands with them.

Per `Plan_Executability_Audit_v1.md` framework-pull discipline: no
framework adoption.
"""

from __future__ import annotations

import shlex
from typing import Any, Final, Literal, cast

from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.sandbox_tier_floor import MCPServerTrustLevel
from harness_as.tool_contract import ToolContract
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.cp_shared_types import MCPTrustTier

from harness_runtime.config.sandbox_defaults import resolve_effective_sandbox_defaults
from harness_runtime.lifecycle.mcp_client_host import (
    MCPClientHost,
    MCPToolContractConverter,
)
from harness_runtime.types import MCPClientConfig, RuntimeConfig, ServerName

# Re-declare the Literal type so this module is self-contained for the
# transport cast (the same Literal is declared at lifecycle.mcp_client_host).
_MCPTransportLiteral = Literal["stdio", "streamable_http", "sse"]

__all__ = ["materialize_mcp_client_host_stage"]


_EMPTY_TRANSPORT_CONFIG: dict[str, Any] = {}

_STDIO_URL_PREFIX = "stdio://"


def _build_transport_config(transport: _MCPTransportLiteral, connection_url: str) -> dict[str, Any]:
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


def _build_default_policy_converter(
    entry: MCPClientConfig, deployment_surface: DeploymentSurface
) -> MCPToolContractConverter:
    """Build a Reading-B default-policy `MCPToolContractConverter` (spec v1.40
    §14.9.3).

    The converter stamps every tool discovered from this server with the
    operator-declared per-server defaults (`entry.default_minimum_tier` +
    `entry.default_blast_radius`), mapping an advertised MCP `Tool`
    (name / description / inputSchema) → AS `ToolContract`. This replaces the
    raise-on-every-call `_default_tool_contract_converter` that the host would
    otherwise use, making a TOOL_STEP dispatchable through the operator
    `api.run` path (closes `.harness/class_1_fork_tool_step_no_operator_supplied_converter.md`
    Reading B).

    The `tool` argument is an `mcp.types.Tool` (typed `Any` per the
    `MCPToolContractConverter = Callable[[Any], ToolContract]` alias);
    `description` may be `None` and `inputSchema` is a JSON-schema dict.
    """
    # Reconcile the per-server minimum_tier through the deployment-surface-aware
    # default policy (runtime spec v1.43 §14.9.9 + fork §7.1) so a bare config's
    # minimum_tier stays coherent with the stage-5 resolved sandbox_tier — the
    # §14.9.4 tier-floor never spuriously violates (three-field reconciliation).
    minimum_tier: SandboxTier = resolve_effective_sandbox_defaults(
        entry, deployment_surface
    ).minimum_tier
    blast_radius_tier: BlastRadiusTier = entry.default_blast_radius

    def convert(tool: Any) -> ToolContract:
        input_schema: dict[str, object] = tool.inputSchema or {"type": "object"}
        return ToolContract(
            name=tool.name,
            description=tool.description or "",
            input_schema=input_schema,
            output_schema={"type": "object"},
            minimum_tier=minimum_tier,
            blast_radius_tier=blast_radius_tier,
        )

    return convert


async def materialize_mcp_client_host_stage(
    config: RuntimeConfig,
) -> dict[ServerName, MCPClientHost]:
    """Construct the stage 3a `MCPClientHost` mapping from operator-supplied config.

    Per spec §14.9.3 stage-3a factory contract (v1.51 §14.9.10 D1 reshape) +
    AC #1/AC #2/AC #5 at U-RT-73/126.

    Returns
    -------
    dict[ServerName, MCPClientHost]
        A 1-entry mapping of unstarted host(s), keyed on `server_name`. The
        stage 3a body is responsible for calling `.start()` per-host afterward
        if `config.mcp_clients` is non-empty; the empty-list sentinel host is
        intentionally left in `.started=False` state (no subprocess to spawn,
        no registry to populate) under the `<empty-sentinel>` key.

    B2-impl-2a returns the mapping SHAPE while materializing a single host
    (`config.mcp_clients[0]`); the materialize-ALL loop is U-RT-126-full
    (B2-impl-2b).
    """
    if not config.mcp_clients:
        # Empty-sentinel branch. stdio + empty transport_config — the host
        # is constructible but `.start()` would fail per the per-transport
        # branches; the empty branch never calls `.start()`.
        sentinel = MCPClientHost(
            transport="stdio",
            server_name="<empty-sentinel>",
            trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
            transport_config=_EMPTY_TRANSPORT_CONFIG,
        )
        return {ServerName(sentinel.server_name): sentinel}

    # B2-impl-2a: one host from the first configured client, returned as a
    # 1-entry mapping keyed on its `server_name`. Multi-server materialization
    # (loop over all `config.mcp_clients`) is U-RT-126-full / B2-impl-2b (see
    # module docstring). `entry.transport` is an
    # `harness_as.discriminators.MCPTransport` StrEnum; its `.value` is one of
    # the literal strings the host accepts.
    entry = config.mcp_clients[0]
    transport_value: _MCPTransportLiteral = cast(_MCPTransportLiteral, entry.transport.value)
    host = MCPClientHost(
        transport=transport_value,
        server_name=entry.client_name,
        trust_tier=_trust_tier_from_level(entry.trust_level),
        transport_config=_build_transport_config(transport_value, entry.connection_url),
        tool_contract_converter=_build_default_policy_converter(entry, config.deployment_surface),
    )
    return {ServerName(host.server_name): host}


_TRUST_LEVEL_TO_TIER: Final[dict[MCPServerTrustLevel, MCPTrustTier]] = {
    MCPServerTrustLevel.L0_REFUSE_REMOTE: MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
    MCPServerTrustLevel.L1_SIGNED_PINNED: MCPTrustTier.LEVEL_1_SIGNED_PINNED,
    MCPServerTrustLevel.L2_SANDBOX_ALL: MCPTrustTier.LEVEL_2_SANDBOX_ALL,
    MCPServerTrustLevel.L3_ALLOW_WITH_AUDIT: MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT,
}
"""Identity-by-ordinal projection table (CP spec v1.34 §27.8 / U-RT-129).

The AS-side `MCPServerTrustLevel` and CP-side `MCPTrustTier` are the SAME
closed 4-value set — `MCPTrustTier` is a "byte-exact factor-out of the
AS-owned value set" (C-AS-10 §10.3 / CP §27.8), so identity (`L_k → LEVEL_k`)
is the unique faithful realization. Total over the closed enum.
"""


def _trust_tier_from_level(level: MCPServerTrustLevel) -> MCPTrustTier:
    """Project the per-`MCPClientConfig` `trust_level` (AS-side enum) onto
    the per-`MCPClientHost` `trust_tier` (CP-side enum), identity-by-ordinal.

    Per CP spec **v1.34 §27.8** (U-RT-129): the projection is a faithful
    `L_k → LEVEL_k` identity over the shared closed 4-value set (the prior
    constant-collapse stub returned `LEVEL_0_REFUSE_REMOTE` regardless,
    flattening every server's trust telemetry to the most-restrictive tier).

    **TELEMETRY-ONLY.** The result populates `MCPHostHealth.trust_tier` → the
    `mcp.server.trust_tier` span attribute (`mcp_client_namespace_emitter`).
    It does NOT feed the dispatch trust gate — that keys on `server_name` via
    the per-server `TrustPolicy`/`per_server_trust_evaluator.evaluate`, a path
    byte-unchanged by this projection. No transport-aware clamp here: transport
    severity is owned by the per-transport sandbox floor (a clamp would be a
    one-source-of-truth violation; the narrow `level`-only signature is the
    positive evidence transport belongs to the floor, not the projection).
    """
    return _TRUST_LEVEL_TO_TIER[level]

"""`harness_runtime.types` — runtime composition primitives + schemas.

Authority:
- `design-substrate/Spec_Harness_Runtime_v1.md` v1.1 §3 (C-RT-03 `RuntimeConfig`)
  and §4 (C-RT-04 `HarnessContext`).
- Class 2 Tension 2026-05-19: 13 axis-typed `HarnessContext` fields name types
  absent from the landed library
  (`.harness/class_2_tension_phase_2_session_5_harness_context_axis_type_mapping.md`).
  Per the operator-confirmed Class 2 resolution, those types are declared
  here as `typing.Protocol` stubs; L2-L6 units narrow or concretize via
  implementations in `harness_runtime.lifecycle.*` / `harness_runtime.wiring.*`.

Module scope at L0 (U-RT-02):
- `BootstrapStage` lands at U-RT-03 (separate L0 unit), not here.
- `_MutableHarnessContext` builder is implementation-discretion (spec §4) and
  is deferred to U-RT-43 (the bootstrap orchestrator).
- Field-level Pydantic validators on `RuntimeConfig` (path-existence checks,
  allowlist-key enforcement) land at U-RT-04 (config precedence resolver),
  per the spec's "Deferred to implementation discretion" clause.

What this module ships at L0:
- `RuntimeConfig` — frozen Pydantic v2 schema; round-trips with empty sub-configs.
- `HarnessContext` — frozen Pydantic v2 schema with `arbitrary_types_allowed=True`;
  every C-RT-04 field declared with its spec-typed surface.
- Sub-config placeholders (empty `BaseModel`s that L1 units enrich).
- 13 `Protocol` stubs for the Class 2 unresolved axis types.
- 5 `Protocol` stubs for the spec-acknowledged runtime-defined types.
- 1 `ProviderClient` `Protocol` (C-RT-05; concretized at U-RT-17/18/19/20).
- 1 local `ToolName` NewType. `SkillID` + `ClientName` were promoted to
  `harness_core.identity` at Session 5; `ToolName` stays local pending a
  cross-axis naming-convention pass (see CP precedent at
  `harness_cp.hitl_as_tool_call_rewriting:38` `type ToolName = str`).
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import NewType, Protocol, runtime_checkable

# ----------------------------------------------------------------------------
# Concrete axis-type imports (the 6 names that resolve at HEAD).
# ----------------------------------------------------------------------------
from harness_as.discriminators import MCPTransport
from harness_as.sandbox_tier import BlastRadiusTier
from harness_as.sandbox_tier_floor import MCPServerTrustLevel
from harness_as.tool_contract import SecretAllowlistEntry, ToolContract
from harness_core import ClientName, SkillID
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.cross_family_fallback_chain import FallbackChain
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.topology_pattern import TopologyPattern
from harness_is.path_resolver import PathResolver
from harness_is.workload_manifest_opt_in_schema import WorkloadManifestOptIns
from harness_is.worktree_isolation import WorktreeIsolationManager
from harness_od.local_first_otlp_collector import (
    BATCH_SPAN_PROCESSOR_BATCH_SIZE,
    BATCH_SPAN_PROCESSOR_WINDOW_SECONDS,
)
from harness_od.per_cell_collector_placement_matrix import CollectorPlacement
from harness_od.sampling_mode import SamplingMode
from pydantic import BaseModel, ConfigDict, Field, field_validator

__all__ = [
    "AuditLedgerWriter",
    "BootstrapStage",
    "ClientName",
    "CollectorConfig",
    "CollectorDaemonHandle",
    "ContentAddressedIndex",
    "CostAttributionChain",
    "EngineSelector",
    "HITLPlacementRegistry",
    "HandoffRegistry",
    "HarnessContext",
    "LedgerWriter",
    "LifecycleEventEmitter",
    "MCPClient",
    "MCPClientConfig",
    "MCPHost",
    "OTelConfig",
    "PathBindingConfig",
    "PerStepOverrideEvaluator",
    "ProviderClient",
    "ProviderSecretsConfig",
    "RetryBreakerRegistry",
    "RuntimeConfig",
    "SandboxDispatchTable",
    "SemanticCache",
    "ShadowGitSupervisor",
    "Skill",
    "SkillID",
    "StageLifecycleHook",
    "StageResult",
    "ToolName",
    "TopologyDispatcher",
]


# ----------------------------------------------------------------------------
# `BootstrapStage` - C-RT-01 v1.1 9-value enum, fixed order.
# Total enum cardinality = 9; file count = 9 (with stage_3a + stage_3b split).
# ----------------------------------------------------------------------------
class BootstrapStage(Enum):
    """The 9 bootstrap stages of the runtime, in fixed traversal order.

    Per `Spec_Harness_Runtime_v1.md` v1.1 §1 (C-RT-01) the order is normative:
    `list(BootstrapStage)` MUST equal `[PREAMBLE, IS, AS, CP_CLIENTS,
    CP_ROUTING, OD, LOOP_INIT, CXA_WIRING, INGRESS_ACCEPT]`. The two stage-3
    members (`CP_CLIENTS`, `CP_ROUTING`) correspond to file-naming convention
    `stage_3a_*.py` / `stage_3b_*.py`.

    Invariants (C-RT-01):
    - `len(BootstrapStage) == 9`.
    - No stage runs before its strict predecessor completes (orchestrator
      invariant; see C-RT-02).
    - The enum is immutable across v1; adding a stage is a v2.0 event.
    """

    PREAMBLE = 0
    IS = 1
    AS = 2
    CP_CLIENTS = 3  # stage 3a
    CP_ROUTING = 4  # stage 3b
    OD = 5
    LOOP_INIT = 6
    CXA_WIRING = 7
    INGRESS_ACCEPT = 8


# ----------------------------------------------------------------------------
# `StageResult` - return shape of a single stage's `execute()` call.
# Per C-RT-02 "implementation discretion": minimal shape at L0; per-stage
# extensions (e.g., per-stage post-condition attestations) land with the
# stage units (L1-L9).
# ----------------------------------------------------------------------------
class StageResult(BaseModel):
    """Result of a single bootstrap stage's `execute()` call (C-RT-02).

    On success, names the stage that produced the result. Failure modes
    raise typed exceptions per the runtime-local fail-class taxonomy
    (C-RT-14); stages do not return failure results - the orchestrator
    treats a returned `StageResult` as success and an exception as the
    `RT-FAIL-BOOTSTRAP` / `RT-FAIL-TRANSIENT` / `RT-FAIL-PARTIAL-ROLLBACK-
    REQUIRED` taxonomy entry.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    stage: BootstrapStage
    """The stage that produced this result."""


# ----------------------------------------------------------------------------
# `StageLifecycleHook` - per-stage entry + exit hook stub.
# Per C-RT-01 invariant "Each stage emits exactly one workflow_event_class
# lifecycle event on entry and exit". Concretized at U-RT-41 (lifecycle
# event emission); at L0 this is a structural Protocol stub.
# ----------------------------------------------------------------------------
@runtime_checkable
class StageLifecycleHook(Protocol):
    """Per-stage entry/exit hook (C-RT-01 lifecycle invariant; U-RT-41)."""


# ----------------------------------------------------------------------------
# Identity NewTypes — local-only.
#
# `SkillID` and `ClientName` are promoted to `harness_core.identity` and
# imported above. `ToolName` stays local: `harness_cp.hitl_as_tool_call_
# rewriting` already carries `type ToolName = str` with documented "future
# cross-axis decision" rationale; promoting here would force a concurrent CP
# refactor + a cross-axis naming-convention pass. Deferred to that pass.
# ----------------------------------------------------------------------------
ToolName = NewType("ToolName", str)


# ----------------------------------------------------------------------------
# Sub-config placeholders (Pydantic BaseModel stubs).
# L1 units (U-RT-04..U-RT-08) enrich these with concrete fields + validators.
# ----------------------------------------------------------------------------
class PathBindingConfig(BaseModel):
    """Path-binding input — U-RT-05 (L1).

    Holds the raw path-binding entry records the operator declares plus the
    workload-manifest opt-in declaration that gates shadow-Git checkpoint
    cadence and worktree-isolation concurrency. The runtime materializes a
    validated `harness_is.PathBinding` via `config.path_bindings.build_path_binding`
    at stage 1 IS bootstrap (U-RT-10).

    Per C-IS-08 §8.1 the opt-ins default to all-off; downstream stage 1 units
    fail-open on the (unset → off) interpretation rather than requiring an
    explicit declaration at every site.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw_entries: tuple[Mapping[str, object], ...] = ()
    """Raw `(path_class, workflow_class, deployment_surface, path)` records.

    Validated into `PathBindingEntry` instances by `load_path_binding` at
    `build_path_binding` time (U-RT-05).
    """

    opt_ins: WorkloadManifestOptIns = Field(default_factory=WorkloadManifestOptIns)
    """Workload-class opt-in declaration (shadow-Git + worktree).

    Defaults to all-off per C-IS-08 §8.1 / C-IS-09 §9.1.
    """


class ProviderSecretsConfig(BaseModel):
    """Provider-secret config — U-RT-06 (L1).

    Holds the OS-keyring service identifier + the operator-policy allowlist
    per C-AS-06 §6.2. Secret VALUES never live in this config; only ALLOWLIST
    KEYS. Per ADR-F5 v1.1 + `Target_Stack_Commitment_v1.md` §5.1 the runtime
    binds `python-keyring` as the keyring library (AS spec §5.4 defers this
    binding to implementation discretion).

    The driver is built at `config.provider_secrets.make_keyring_resolver`
    and invoked at tool-fetch time (post-L3); audit-event composition
    (SecretFetchEvent) is the CALLER's responsibility per U-AS-26 separation.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    keyring_service: str = "harness"
    """OS-keyring service-name identifier (python-keyring `service` arg)."""

    operator_allowlist: tuple[SecretAllowlistEntry, ...] = ()
    """Operator-policy allowlist (C-AS-06 §6.2 override set).

    `tuple[SecretAllowlistEntry, ...]` (Pydantic-friendly); converted to
    `frozenset` at resolver-construction time for `check_secret_allowlist`.
    Empty default means no operator-allowlisted secrets — every fetch is
    DENIED_NOT_IN_OPERATOR_POLICY_OVERRIDE until populated.
    """


class OTelConfig(BaseModel):
    """OTel runtime config — U-RT-07 (L1).

    Carries the OTLP endpoint, an optional sampling-mode override, and
    operator-supplied additional resource attributes. The sampler mode
    defaults to the per-deployment-surface mapping at C-OD-09 §9.1
    (`PER_DEPLOYMENT_SURFACE_SAMPLING` in `harness_od.sampling_mode`); a
    non-None override here wins (operator-tunable for self-hosted-server
    deployments running mixed regimes).

    Endpoint validation runs at construction time per the field validator
    (URL must include `://`); detailed schema validation (gRPC vs HTTP) is
    deferred to U-RT-27 (TracerProvider construction).

    Resource attributes for the 12 ADR-D6 v1.2 §1.2 namespaces are built at
    `config.otel_config.build_resource_attributes()` from `deployment_surface`
    + `additional_resource_attrs`; not stored on the config itself (derived).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    otlp_endpoint: str
    """OTLP exporter endpoint URL (e.g. `http://localhost:4318`)."""

    sampling_mode: SamplingMode | None = None
    """Optional override of the per-deployment-surface default (C-OD-09 §9.1)."""

    additional_resource_attrs: tuple[tuple[str, str], ...] = ()
    """Operator-supplied additional resource attrs; merged into the OTel
    resource at TracerProvider construction (U-RT-27)."""

    @field_validator("otlp_endpoint")
    @classmethod
    def _endpoint_has_scheme(cls, value: str) -> str:
        """Reject endpoints without a `://` scheme separator at construction time."""
        if "://" not in value:
            raise ValueError(
                f"otlp_endpoint must include a `://` scheme (got {value!r})",
            )
        return value


class CollectorConfig(BaseModel):
    """In-process collector daemon config — U-RT-08 (L1).

    Carries the placement selection (architectural class per C-OD-20 §20.1),
    ring-buffer size, sqlite rotation thresholds, and BatchSpanProcessor
    cadence inherited from C-OD-19 §19.1 defaults. The collector daemon
    supervisor at U-RT-29 (F-P2-5) consumes these settings.

    All numeric thresholds are validated as positive at construction time;
    defaults match the OD-spec-committed BSP constants
    (`BATCH_SPAN_PROCESSOR_WINDOW_SECONDS=5`, `BATCH_SPAN_PROCESSOR_BATCH_SIZE=512`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    placement: CollectorPlacement = CollectorPlacement.IN_PROCESS
    """Architectural collector placement (C-OD-20 §20.1). Defaults to
    `IN_PROCESS` per F-P2-5 (runtime owns the in-process collector daemon)."""

    ring_buffer_size: int = 4096
    """Span ring-buffer capacity for the collector daemon (bounded > 0)."""

    sqlite_rotation_max_rows: int = 100_000
    """Row-count rotation threshold for the collector sqlite store (> 0)."""

    sqlite_rotation_max_bytes: int = 100_000_000
    """Byte-size rotation threshold for the collector sqlite store (> 0)."""

    batch_window_seconds: int = BATCH_SPAN_PROCESSOR_WINDOW_SECONDS
    """BSP batching window in seconds (C-OD-19 §19.1 default = 5; > 0)."""

    batch_size: int = BATCH_SPAN_PROCESSOR_BATCH_SIZE
    """BSP batch size (C-OD-19 §19.1 default = 512; > 0)."""

    @field_validator(
        "ring_buffer_size",
        "sqlite_rotation_max_rows",
        "sqlite_rotation_max_bytes",
        "batch_window_seconds",
        "batch_size",
    )
    @classmethod
    def _positive(cls, value: int) -> int:
        """All collector thresholds must be strictly positive."""
        if value <= 0:
            raise ValueError(f"value must be > 0 (got {value})")
        return value


class MCPClientConfig(BaseModel):
    """MCP client connection config — U-RT-15 (L3).

    Carries the per-client transport + trust-level surface that
    `harness_as.mcp_transport_floor` validates at stage 2 AS bootstrap.
    Real connection URL + auth-secret reference are operator-supplied;
    the connection-URL schema (stdio: command line; remote: HTTP URL) is
    runtime implementation-discretion at L3.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    client_name: ClientName
    """Operator-supplied client identifier — key in `HarnessContext.mcp_clients`."""

    transport: MCPTransport
    """Transport class (C-AS-10 §10.1 — stdio / streamable_http / ssecached)."""

    trust_level: MCPServerTrustLevel
    """Trust-tier framework class (C-AS-10 §10.3) — gates remote registration."""

    blast_radius: BlastRadiusTier
    """Blast-radius capability of the tool surfaces this client proxies."""

    connection_url: str
    """Stdio command-line OR remote HTTP URL (per `transport`)."""


# ----------------------------------------------------------------------------
# Protocol stubs - spec-acknowledged runtime-defined types (C-RT-04).
# Empty bodies at L0; method shapes narrow as L2-L6 units consume them.
# ----------------------------------------------------------------------------
@runtime_checkable
class ShadowGitSupervisor(Protocol):
    """Runtime-defined per C-RT-04. Concretized at U-RT-11."""


@runtime_checkable
class LedgerWriter(Protocol):
    """Runtime-defined wrapper around IS state-ledger. Concretized at U-RT-12."""


@runtime_checkable
class AuditLedgerWriter(Protocol):
    """Runtime-defined wrapper around IS+OD audit-ledger. Concretized at U-RT-32."""


@runtime_checkable
class CollectorDaemonHandle(Protocol):
    """Runtime-defined supervisor handle (F-P2-5; C-RT-07). Concretized at U-RT-29."""


@runtime_checkable
class LifecycleEventEmitter(Protocol):
    """Runtime-defined `workflow_event_class` emitter. Concretized at U-RT-41."""


# ----------------------------------------------------------------------------
# Protocol stubs - Class 2 unresolved axis-typed names (Tension 2026-05-19).
# Mapping decision: runtime composes these from landed contracts/policies.
# L2-L6 units provide concrete implementations.
# ----------------------------------------------------------------------------
@runtime_checkable
class ContentAddressedIndex(Protocol):
    """Composed at U-RT-09 from landed IS index primitives."""


@runtime_checkable
class SemanticCache(Protocol):
    """Composed at U-RT-09 from landed IS cache primitives."""


@runtime_checkable
class Skill(Protocol):
    """Composed at U-RT-13 from landed AS skill-loading primitives."""


@runtime_checkable
class MCPHost(Protocol):
    """Composed at U-RT-15 wrapping `mcp` (FastMCP) host runtime."""


@runtime_checkable
class MCPClient(Protocol):
    """Composed at U-RT-15 wrapping `mcp` client runtime."""


@runtime_checkable
class SandboxDispatchTable(Protocol):
    """Composed at U-RT-16 from landed AS sandbox-tier primitives."""


@runtime_checkable
class EngineSelector(Protocol):
    """Composed at U-RT-22 from landed CP engine-class primitives."""


@runtime_checkable
class RetryBreakerRegistry(Protocol):
    """Composed at U-RT-24 from hand-rolled retry / breaker primitives.

    Per `Plan_Executability_Audit_v1.md` framework-pull discipline: NO
    `tenacity` / `pybreaker` / `circuitbreaker`.
    """


@runtime_checkable
class HITLPlacementRegistry(Protocol):
    """Composed at U-RT-25 from landed CP HITL-placement primitives."""


@runtime_checkable
class HandoffRegistry(Protocol):
    """Composed at U-RT-26 from landed CP sub-agent-handoff primitives."""


@runtime_checkable
class PerStepOverrideEvaluator(Protocol):
    """Composed at U-RT-39 from landed CP per-step-override primitives."""


@runtime_checkable
class TopologyDispatcher(Protocol):
    """Composed at U-RT-40 from landed CP topology-pattern primitives.

    Risk gate: Tension 002 (TopologyPattern enum) is re-verified at U-RT-40
    landing per the open-question carry-forward in `Spec_Harness_Runtime_v1.md`
    §16.
    """


@runtime_checkable
class CostAttributionChain(Protocol):
    """Composed at U-RT-31 from landed OD cost-attribution primitives."""


# ----------------------------------------------------------------------------
# Protocol — provider SDK structural shape (C-RT-05).
# Concrete adapters (Anthropic / OpenAI / Ollama) wrap each async SDK client
# behind this Protocol uniformly. Concretized at U-RT-17.
#
# Per spec §5 (C-RT-05 v1.1 lines 326-344): the Protocol is intentionally
# minimal — only the lifecycle obligation the runtime owns. The capability-
# aware abstraction layer (CP `provider_capabilities`) is what dispatches to
# provider-specific completion methods, not this Protocol (per advisor +
# spec docstring at line 335-339).
# ----------------------------------------------------------------------------
@runtime_checkable
class ProviderClient(Protocol):
    """Structural protocol every async provider adapter satisfies (C-RT-05 v1.1).

    Concrete adapters at `harness_runtime.lifecycle.providers`:
    `AnthropicAdapter` (U-RT-17), `OpenAIAdapter` (U-RT-18), `OllamaAdapter`
    (U-RT-19). Each adapter wraps its SDK's async client so the runtime can
    `aclose()` all three uniformly at C-RT-10 reverse-shutdown.
    """

    async def aclose(self) -> None:
        """Close the underlying SDK client + connections. Idempotent.

        Per C-RT-05 §5 + C-RT-10 reverse-shutdown: called at runtime shutdown
        for every entry in `HarnessContext.providers`. Adapters MUST tolerate
        repeated invocation without raising (idempotent post-condition).
        """
        ...


# ----------------------------------------------------------------------------
# `RuntimeConfig` — C-RT-03 v1.1 schema.
# ----------------------------------------------------------------------------
class RuntimeConfig(BaseModel):
    """Input configuration to the runtime; frozen post-construction.

    Field order and type discipline are normative per C-RT-03. Path-existence,
    keyring-allowlist, and precedence-resolution validators are deferred to
    U-RT-04 (config precedence resolver) per the spec's "Deferred to
    implementation discretion" clause.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    deployment_surface: DeploymentSurface
    """Local / hybrid / cloud — drives OTel resource attrs + collector placement."""

    repository_root: Path
    """Absolute path; must exist (validator at U-RT-04). Basis for `.harness/`."""

    path_bindings: PathBindingConfig
    """Inputs to `PathResolver(binding)`. Enriched at U-RT-05."""

    provider_secrets: ProviderSecretsConfig
    """Keyring allowlist *keys* only — no secret values. Enriched at U-RT-06."""

    otel: OTelConfig
    """OTLP endpoint, sampler mode, additional resource attrs. Enriched at U-RT-07."""

    collector: CollectorConfig
    """Ring buffer size, sqlite rotation thresholds, placement-matrix. U-RT-08."""

    default_topology: TopologyPattern
    """TopologyPattern dispatched when no per-workflow override is set."""

    mcp_clients: list[MCPClientConfig] = []
    """MCP client connection configs; empty list permitted."""

    ollama_host: str | None = None
    """Ollama daemon host URL (per spec §5 line 354 `AsyncClient(host=...)`).

    `None` → `ollama.AsyncClient()` falls back to its built-in default
    (`http://localhost:11434`). Top-level placement (vs. nested under
    `ProviderSecretsConfig`) per spec §5 deferred-discretion note line 373:
    Ollama is local-tier and credential-less, so this is a *behavior* knob,
    not a key-allowlist concern. U-RT-17 amendment per advisor.
    """

    ollama_optional: bool = False
    """If True, Ollama unreachability at stage 3a → `RT-FAIL-PROVIDER-DEGRADED`
    (typed warning; stage continues with 2-provider context). Default False:
    Ollama unreachability is a hard stage 3a failure per the multi-LLM
    commitment (ADR-F1 v1.2). U-RT-19 wires the degraded branch; field is
    declared here at U-RT-17 to keep schema additions in one commit."""

    tenant_id: str | None = None
    """Multi-tenant separation key per OD audit-ledger. `None` = single-tenant."""

    routing_manifest: RoutingManifest = Field(
        default_factory=lambda: RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(),
            retry_policies={},
        ),
    )
    """Operator-supplied routing manifest (CP v2.10 R-2 read / W-2 write schemas).

    Enriched at U-RT-21 (L5 stage 3b CP_ROUTING). Default is an empty manifest
    (`manifest_version=1`, no role bindings, no workload overrides, no fallback
    chains, no retry policies) — sufficient to drive the bootstrap path through
    stage 3b in test scenarios that don't exercise routing dispatch. Operators
    supply a populated manifest via kwarg at runtime construction; the manifest
    is persisted to `PathClass.ROUTING_MANIFEST` at stage 3b per C-CP-01 §1.3.
    """


# ----------------------------------------------------------------------------
# `HarnessContext` — C-RT-04 v1.1 schema.
# Frozen post-bootstrap. The `_MutableHarnessContext` builder used during the
# 9-stage bootstrap is implementation-discretion and lands at U-RT-43.
# ----------------------------------------------------------------------------
class HarnessContext(BaseModel):
    """Post-bootstrap handle through which `run()` reaches every wired component.

    Mutation during bootstrap goes through a separate `_MutableHarnessContext`
    builder (U-RT-43); at stage 7 INGRESS_ACCEPT the builder is materialized
    into this frozen final form. Every field is non-`None` at stage 7 EXCEPT
    `mcp_clients` (empty dict permitted) and `tenant_id`-derived audit-writer
    scoping.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    # Stage 0 PREAMBLE.
    config: RuntimeConfig
    drained_flag: asyncio.Event

    # Stage 1 IS.
    path_resolver: PathResolver
    worktree_manager: WorktreeIsolationManager
    shadow_git: ShadowGitSupervisor
    ledger_writer: LedgerWriter
    index: ContentAddressedIndex
    cache: SemanticCache

    # Stage 2 AS.
    skills: dict[SkillID, Skill]
    tool_contracts: dict[ToolName, ToolContract]
    mcp_host: MCPHost
    mcp_clients: dict[ClientName, MCPClient]
    sandbox_dispatch: SandboxDispatchTable

    # Stage 3a CP_CLIENTS.
    providers: dict[str, ProviderClient]

    # Stage 3b CP_ROUTING.
    routing_manifest: RoutingManifest
    engine_selector: EngineSelector
    fallback_chain: FallbackChain
    retry_breaker: RetryBreakerRegistry
    hitl_registry: HITLPlacementRegistry
    handoff_registry: HandoffRegistry

    # Stage 4 OD.
    # `tracer_provider` is informational per C-RT-04 — consumers call
    # `opentelemetry.trace.get_tracer_provider()` per ADR-F5. We type it
    # arbitrarily (Protocol-ish via arbitrary_types_allowed) to avoid pulling
    # the OTel SDK type into the schema at L0; U-RT-27 fills it.
    tracer_provider: object
    collector_daemon: CollectorDaemonHandle
    cost_chain: CostAttributionChain
    audit_writer: AuditLedgerWriter

    # Stage 5 LOOP_INIT.
    override_evaluator: PerStepOverrideEvaluator
    topology_dispatcher: TopologyDispatcher
    lifecycle_emitter: LifecycleEventEmitter

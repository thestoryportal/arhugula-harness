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
from enum import Enum
from pathlib import Path
from typing import NewType, Protocol, runtime_checkable

# ----------------------------------------------------------------------------
# Concrete axis-type imports (the 6 names that resolve at HEAD).
# ----------------------------------------------------------------------------
from harness_as.tool_contract import ToolContract
from harness_core import ClientName, SkillID
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.cross_family_fallback_chain import FallbackChain
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.topology_pattern import TopologyPattern
from harness_is.path_resolver import PathResolver
from harness_is.worktree_isolation import WorktreeIsolationManager
from pydantic import BaseModel, ConfigDict

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
    """L0 placeholder — U-RT-05 enriches with concrete `PathBinding` fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ProviderSecretsConfig(BaseModel):
    """L0 placeholder — U-RT-06 enriches with keyring allowlist fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class OTelConfig(BaseModel):
    """L0 placeholder — U-RT-07 enriches with OTLP endpoint + sampler fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class CollectorConfig(BaseModel):
    """L0 placeholder — U-RT-08 enriches with collector daemon fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class MCPClientConfig(BaseModel):
    """L0 placeholder — L3 AS bootstrap units enrich with MCP client fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


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
# Concrete async clients (anthropic / openai / ollama) duck-type to this.
# Method shape lands at U-RT-17/18/19/20 when the runtime first calls them.
# ----------------------------------------------------------------------------
@runtime_checkable
class ProviderClient(Protocol):
    """Structural protocol every async provider client satisfies (C-RT-05 v1.1).

    Concrete clients: `AsyncAnthropic`, `AsyncOpenAI`, `ollama.AsyncClient`.
    The method shape (e.g., `aclose()` per C-RT-10 reverse-shutdown contract,
    a capability-aware completion entry point per ADR-F1 v1.2) is filled in
    at U-RT-17..U-RT-20 when the runtime first calls each.
    """


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

    tenant_id: str | None = None
    """Multi-tenant separation key per OD audit-ledger. `None` = single-tenant."""


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

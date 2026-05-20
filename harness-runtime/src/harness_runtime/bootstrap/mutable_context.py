"""`_MutableHarnessContext` — per C-RT-04 §4 deferred-to-discretion builder.

The frozen `HarnessContext` (spec §4) is constructed at stage 7 INGRESS_ACCEPT
from this mutable builder. Every HarnessContext field has an `| None`-typed
counterpart here; `freeze()` validates non-None coverage and constructs the
frozen Pydantic model.

The builder additionally carries:
- `completed_stages`: the in-order list of stages that have committed, used by
  the orchestrator's reverse-order rollback.
- `emitted_bootstrap_events`: the post-emit log of `BootstrapStageCompleteEvent`
  records, populated as the orchestrator drains its event buffer through the
  emitter (introspectable in tests via the `frozen` context's emitter).
- `frozen`: the materialized `HarnessContext` after `freeze()` succeeds —
  stashed here so `stage_7_ingress.execute` can publish its result without
  changing the executor return type.
- `_cxa_stages`: per-stage 6 wiring composer results held for verification +
  freeze-time discard (the wiring side-effects are what matters; the stage
  records themselves do not live on the frozen context).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from harness_as.tool_contract import ToolContract
from harness_core import ClientName, SkillID
from harness_cp.cross_family_fallback_chain import FallbackChain
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_is.path_resolver import PathResolver
from harness_is.worktree_isolation import WorktreeIsolationManager
from pydantic import BaseModel, ConfigDict

from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.types import (
    AuditLedgerWriter,
    BootstrapStage,
    CollectorDaemonHandle,
    ContentAddressedIndex,
    CostAttributionChain,
    EngineSelector,
    HandoffRegistry,
    HarnessContext,
    HITLPlacementRegistry,
    LedgerReader,
    LedgerWriter,
    LifecycleEventEmitter,
    MCPClient,
    MCPHost,
    PerStepOverrideEvaluator,
    ProviderClient,
    RetryBreakerRegistry,
    RuntimeConfig,
    SandboxDispatchTable,
    SemanticCache,
    ShadowGitSupervisor,
    Skill,
    ToolName,
    TopologyDispatcher,
)

__all__ = [
    "BootstrapStageCompleteEvent",
    "IncompleteBootstrapError",
    "_MutableHarnessContext",
]


class IncompleteBootstrapError(Exception):
    """`freeze()` called with one or more required `HarnessContext` fields None.

    Raised by `_MutableHarnessContext.freeze()` at stage 7 INGRESS_ACCEPT when
    the builder is missing any non-optional field. Indicates an orchestrator
    or stage-implementation defect (every required field MUST be populated by
    its declared stage per C-RT-04).
    """

    def __init__(self, missing_fields: tuple[str, ...]) -> None:
        self.missing_fields = missing_fields
        super().__init__(
            f"_MutableHarnessContext.freeze() called with required fields None: "
            f"{', '.join(missing_fields)}"
        )


class BootstrapStageCompleteEvent(BaseModel):
    """Lifecycle event record — one emitted per bootstrap stage completion.

    Distinct from `WorkflowEventClass` (which is closed at cardinality 8 per
    `[[fork-drained-event-class]]` and addresses workflow lifecycle, not
    bootstrap). Surface bounded to `harness_runtime.bootstrap`; consumed by
    the orchestrator's buffer-and-flush logic + by tests asserting AC #3.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    stage: BootstrapStage


# Set of fields that MUST be populated by stage 7 freeze. Mirrors
# `HarnessContext`'s required-field set per C-RT-04 (the spec's only
# exemption is `mcp_clients` which may be an empty dict; we still require
# the dict object itself to be non-None).
_REQUIRED_FIELDS: tuple[str, ...] = (
    "config",
    "drained_flag",
    "path_resolver",
    "worktree_manager",
    "shadow_git",
    "ledger_writer",
    "ledger_reader",
    "index",
    "cache",
    "skills",
    "tool_contracts",
    "mcp_host",
    "mcp_clients",
    "sandbox_dispatch",
    "providers",
    "routing_manifest",
    "engine_selector",
    "fallback_chain",
    "retry_breaker",
    "hitl_registry",
    "handoff_registry",
    "tracer_provider",
    "collector_daemon",
    "cost_chain",
    "audit_writer",
    "override_evaluator",
    "topology_dispatcher",
    "lifecycle_emitter",
    "llm_dispatcher",
)


@dataclass(slots=True)
class _MutableHarnessContext:
    """Bootstrap-time mutable builder for `HarnessContext` (C-RT-04 discretion)."""

    # Stage 0 PREAMBLE.
    config: RuntimeConfig | None = None
    drained_flag: asyncio.Event | None = None
    actor: Any = None  # harness_is.Actor — runtime identity; threaded into stage 1
    keyring_resolver: Any = None  # KeyringSecretResolver — threaded into stage 3a

    # Stage 1 IS.
    path_resolver: PathResolver | None = None
    worktree_manager: WorktreeIsolationManager | None = None
    shadow_git: ShadowGitSupervisor | None = None
    ledger_writer: LedgerWriter | None = None
    ledger_reader: LedgerReader | None = None
    index: ContentAddressedIndex | None = None
    cache: SemanticCache | None = None

    # Stage 2 AS.
    skills: dict[SkillID, Skill] | None = None
    tool_contracts: dict[ToolName, ToolContract] | None = None
    mcp_host: MCPHost | None = None
    mcp_clients: dict[ClientName, MCPClient] | None = None
    sandbox_dispatch: SandboxDispatchTable | None = None

    # Stage 3a CP_CLIENTS.
    providers: dict[str, ProviderClient] | None = None

    # Stage 3b CP_ROUTING.
    routing_manifest: RoutingManifest | None = None
    engine_selector: EngineSelector | None = None
    fallback_chain: FallbackChain | None = None
    retry_breaker: RetryBreakerRegistry | None = None
    hitl_registry: HITLPlacementRegistry | None = None
    handoff_registry: HandoffRegistry | None = None

    # Stage 4 OD.
    tracer_provider: object | None = None
    collector_daemon: CollectorDaemonHandle | None = None
    cost_chain: CostAttributionChain | None = None
    audit_writer: AuditLedgerWriter | None = None

    # Stage 5 LOOP_INIT.
    override_evaluator: PerStepOverrideEvaluator | None = None
    topology_dispatcher: TopologyDispatcher | None = None
    lifecycle_emitter: LifecycleEventEmitter | None = None
    llm_dispatcher: RuntimeLLMDispatcher | None = None

    # Orchestrator bookkeeping — not part of HarnessContext.
    completed_stages: list[BootstrapStage] = field(default_factory=list)
    emitted_bootstrap_events: list[BootstrapStageCompleteEvent] = field(default_factory=list)
    cxa_stages: dict[str, Any] = field(default_factory=dict)
    frozen: HarnessContext | None = None

    def freeze(self) -> HarnessContext:
        """Materialize the frozen `HarnessContext`. Raises if any required field None."""
        missing = tuple(name for name in _REQUIRED_FIELDS if getattr(self, name) is None)
        if missing:
            raise IncompleteBootstrapError(missing)

        ctx = HarnessContext(
            config=self.config,
            drained_flag=self.drained_flag,
            path_resolver=self.path_resolver,
            worktree_manager=self.worktree_manager,
            shadow_git=self.shadow_git,
            ledger_writer=self.ledger_writer,
            ledger_reader=self.ledger_reader,
            index=self.index,
            cache=self.cache,
            skills=self.skills,
            tool_contracts=self.tool_contracts,
            mcp_host=self.mcp_host,
            mcp_clients=self.mcp_clients,
            sandbox_dispatch=self.sandbox_dispatch,
            providers=self.providers,
            routing_manifest=self.routing_manifest,
            engine_selector=self.engine_selector,
            fallback_chain=self.fallback_chain,
            retry_breaker=self.retry_breaker,
            hitl_registry=self.hitl_registry,
            handoff_registry=self.handoff_registry,
            tracer_provider=self.tracer_provider,
            collector_daemon=self.collector_daemon,
            cost_chain=self.cost_chain,
            audit_writer=self.audit_writer,
            override_evaluator=self.override_evaluator,
            topology_dispatcher=self.topology_dispatcher,
            lifecycle_emitter=self.lifecycle_emitter,
            llm_dispatcher=self.llm_dispatcher,
        )
        self.frozen = ctx
        return ctx

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

from harness_runtime.lifecycle.llm_dispatch import (
    RuntimeLLMDispatcher,  # noqa: F401  # pyright: ignore[reportUnusedImport] — schema legacy carrier
)
from harness_runtime.types import (
    AuditLedgerWriter,
    BootstrapStage,
    CollectorDaemonHandle,
    ContentAddressedIndex,
    CostAttributionChain,
    EngineSelector,
    HandoffRegistry,
    HarnessContext,
    HarnessMCPServer,
    HITLPlacementRegistry,
    LedgerReader,
    LedgerWriter,
    LifecycleEventEmitter,
    LLMDispatcher,
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
    "pause_requested_flag",
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
    "mcp_client_host",
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
    "sub_agent_dispatcher",
    "ask_user_question_surface",
    "step_dispatchers",
    "tool_dispatcher",
    "per_server_trust_evaluator",
    "mcp_namespace_emitter",
    "memory_tool_registry",
    "resume_context_holder",
)


def _bound[T](value: T | None) -> T:
    """Narrow a required mutable-builder field Optional → T for the frozen
    `HarnessContext` constructor in `freeze()`. The `_REQUIRED_FIELDS` guard
    has already raised `IncompleteBootstrapError` if any were None; this shim
    makes that bootstrap-complete invariant visible to the type checker."""
    assert value is not None
    return value


@dataclass(slots=True)
class _MutableHarnessContext:
    """Bootstrap-time mutable builder for `HarnessContext` (C-RT-04 discretion)."""

    # Stage 0 PREAMBLE.
    config: RuntimeConfig | None = None
    drained_flag: asyncio.Event | None = None
    pause_requested_flag: asyncio.Event | None = None
    """U-RT-87 — Caller-side pause-signaling primitive per runtime spec v1.21
    §4 + §14.14.3 sibling-pattern to `drained_flag`. Initialized at stage 0
    PREAMBLE alongside `drained_flag`. Required on the frozen HarnessContext
    per spec v1.21 §4 C-RT-04."""
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
    mcp_server: HarnessMCPServer | None = None
    """U-RT-62 — H_T-as-MCP-server hosting surface. Populated at stage 2 AS
    sibling to `mcp_host` (U-RT-15 H_T-as-MCP-client). Optional on the
    frozen `HarnessContext` (defaults to `None` per AC #1 transitional
    bootstrap-builder shape; not in `_REQUIRED_FIELDS`)."""
    sandbox_dispatch: SandboxDispatchTable | None = None

    # Stage 3a CP_CLIENTS.
    providers: dict[str, ProviderClient] | None = None
    mcp_client_host: Any = None
    """U-RT-72 — H_T-as-MCP-client host (concrete:
    `harness_runtime.lifecycle.mcp_client_host.MCPClientHost`). Populated
    at stage 3a by `materialize_mcp_client_host_stage` (U-RT-73). Required
    on the frozen HarnessContext per spec v1.16 §4 C-RT-04."""

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
    llm_dispatcher: LLMDispatcher | None = None
    """Top-level dispatcher seam — bound at stage 5 to either the bare
    ``RuntimeLLMDispatcher`` (U-RT-52, C-RT-15) or the
    ``RetryBreakerFallbackDispatcher`` wrapper (U-RT-58, C-RT-16). Both
    satisfy the ``LLMDispatcher`` Protocol; the field is typed against the
    Protocol so the C-RT-16 wrap is type-transparent."""

    sub_agent_dispatcher: Any = None
    """U-RT-59 (C-RT-17 §14.7) sub-agent dispatch composer + U-RT-60
    (C-RT-18 §14.8) HITL gate composer wrap layer; bound at stage 5
    LOOP_INIT alongside ``llm_dispatcher``. v1.11 (post-U-RT-60 wrap-
    asymmetry fork APPLIED): bound to ``RuntimeHITLGateComposer`` with
    ``applicable_placements={SUB_AGENT_BOUNDARY}`` wrapping the sync
    sub-agent dispatcher; the composer is async + the sync Protocol
    satisfaction at registry boundary is carried by ``SyncDispatcherFacade``
    (see ``step_dispatchers``). Typed ``Any`` (same pattern as
    ``llm_dispatcher``)."""

    ask_user_question_surface: Any = None
    """U-RT-60 (C-RT-18 §14.8.3 v1.11 binding pin) MCP-backed
    AskUserQuestion delivery surface; bound at stage 5 LOOP_INIT. Concretized
    by ``MCPBackedAskUserQuestionSurface``; satisfies the
    ``AskUserQuestionSurface`` Protocol consumed by both HITL composers
    (PRE_ACTION + SUB_AGENT_BOUNDARY rows of the §14.8.1 wrap-asymmetry
    table). Typed ``Any`` (same pattern as ``sub_agent_dispatcher``)."""

    step_dispatchers: Any = None
    """U-RT-59 (C-RT-17 §14.7.1 + §14.7.7) step-kind routing registry;
    bound at stage 5 LOOP_INIT after both dispatchers are constructed.
    Concretized by
    ``harness_runtime.lifecycle.step_dispatchers.StepKindDispatcherRegistry``.
    v1.6 MVP binds 1 entry (``SUB_AGENT_DISPATCH``); ``INFERENCE_STEP``
    binding deferred per Class 1 fork (U-RT-58 async wrapper / sync driver
    mismatch). Typed ``Any`` to avoid pulling the CP
    ``StepDispatcherRegistry`` Protocol into the schema layer."""

    tool_dispatcher: Any = None
    """U-RT-72/75 (C-RT-21 §14.11 retry-wrap around C-RT-19) TOOL_STEP
    dispatcher; bound at stage 5 LOOP_INIT by
    ``materialize_runtime_tool_dispatcher_stage`` (U-RT-75). The bare
    ``RuntimeToolDispatcher`` is private to the wrapper (constructor arg
    per spec §14.9.6 inv 6). Required on the frozen HarnessContext per
    spec v1.16 §4 C-RT-04."""

    per_server_trust_evaluator: Any = None
    """U-RT-72; U-CP-68 PerServerTrustEvaluator. Bound at stage 5 within
    ``materialize_runtime_tool_dispatcher_stage`` (U-RT-75) step 1 from
    ``config.trust_policy``. Required on the frozen HarnessContext per
    spec v1.16 §4 C-RT-04."""

    mcp_namespace_emitter: Any = None
    """U-RT-72; U-CP-69 MCPClientNamespaceEmitter. Bound at stage 5 within
    ``materialize_runtime_tool_dispatcher_stage`` (U-RT-75) step 2 from
    ``ctx.mcp_client_host.tool_registry``. Required on the frozen
    HarnessContext per spec v1.16 §4 C-RT-04."""

    memory_tool_registry: Any = None
    """U-RT-79 — Memory tool storage-backend registry (U-RT-78
    ``MemoryToolRegistry``). Bound at stage 5 LOOP_INIT by
    ``materialize_memory_tool_registry_stage`` (U-RT-80) per spec v1.17
    §14.12.3. Required on the frozen HarnessContext per spec v1.17 §4
    C-RT-04 (added at v1.17 per Class 1 fork H_T-CP-16+17 §16 ratified
    Memory-only arc absorption 2026-05-23). Typed ``Any`` per the
    Protocol-vs-concrete-narrowing pattern (mirrors ``tool_dispatcher``)."""

    pause_resume_protocol: Any = None
    """U-RT-87 — Pause/resume protocol (CP spec v1.13 §26
    ``PauseResumeProtocol`` class body). Bound at stage 5 LOOP_INIT by
    ``materialize_pause_resume_protocol_stage`` per runtime spec v1.21
    §14.14.3. Optional (``None`` = operator opt-out preserving the v1.20
    production-default state); NOT in ``_REQUIRED_FIELDS``. Typed ``Any``
    on the mutable builder per the same Protocol-vs-concrete-narrowing
    pattern as ``validator_framework`` + ``tool_dispatcher`` +
    ``memory_tool_registry``; the frozen ``HarnessContext.pause_resume_protocol``
    field carries the narrowed ``PauseResumeProtocol | None`` class surface."""

    webhook_delivery_composer: Any = None
    """U-RT-96 — Webhook delivery composer (runtime spec v1.26 §14.10.1
    ``WebhookDeliveryComposer`` class body landed at U-RT-69). Bound at
    stage 5 LOOP_INIT by ``materialize_webhook_delivery_composer_stage`` per
    runtime spec v1.26 §14.16.3. Optional (``None`` = operator opt-out
    preserving the pre-v1.26 production-default state); NOT in
    ``_REQUIRED_FIELDS``. Typed ``Any`` on the mutable builder per the
    same Protocol-vs-concrete-narrowing pattern as ``pause_resume_protocol``
    + ``validator_framework`` + ``tool_dispatcher`` + ``memory_tool_registry``;
    the frozen ``HarnessContext.webhook_delivery_composer`` field carries the
    narrowed ``WebhookDeliveryComposer | None`` class surface."""

    resume_context_holder: Any = None
    """U-RT-94 — Runtime-internal sidecar carrier for one-shot ResumeContext
    delivery across the pause-resume cycle (runtime spec v1.25 §14.8.8.9
    + §4 C-RT-04 NEW field row). Bound at stage 5 LOOP_INIT to an empty
    holder (``ResumeContextHolder()`` with ``_current_context = None``
    default). REQUIRED on the frozen ``HarnessContext`` (unconditionally
    bound regardless of operator-supply at RuntimeConfig — the holder is a
    runtime-loop carrier, not deployment-time configuration); listed in
    ``_REQUIRED_FIELDS``. Typed ``Any`` on the mutable builder per the same
    Protocol-vs-concrete-narrowing pattern as ``pause_resume_protocol`` +
    ``validator_framework``; the frozen ``HarnessContext.resume_context_holder``
    field carries the narrowed ``ResumeContextHolder`` class surface."""

    validator_framework: Any = None
    """U-RT-84 — Validator framework (CP spec v1.11 §25
    ``ConcreteValidatorFramework`` / ``ValidatorFramework`` Protocol). Bound at
    stage 4 OD by ``materialize_validator_framework_stage`` per runtime spec
    v1.18 §14.13.3. Optional (``None`` = operator opt-out preserving the v1.17
    production-default state); NOT in ``_REQUIRED_FIELDS``. Typed ``Any`` on
    the mutable builder per the same Protocol-vs-concrete-narrowing pattern
    as ``tool_dispatcher`` + ``memory_tool_registry``; the frozen
    ``HarnessContext.validator_framework`` field carries the narrowed
    ``ValidatorFramework | None`` Protocol surface."""

    skill_activation_emitter: Any = None
    """U-RT-100 — SkillActivationSpanEmitter (runtime spec v1.32 §14.17.1
    ``SkillActivationSpanEmitter`` class body). Bound at stage 5 LOOP_INIT by
    ``materialize_skill_activation_emitter_stage`` per runtime spec v1.32
    §14.17.3. Optional (``None`` = operator opt-out preserving the pre-v1.32
    production-default state); NOT in ``_REQUIRED_FIELDS``. Typed ``Any`` on
    the mutable builder per the same Protocol-vs-concrete-narrowing pattern
    as ``validator_framework`` + ``pause_resume_protocol`` +
    ``webhook_delivery_composer``; the frozen
    ``HarnessContext.skill_activation_emitter`` field carries the narrowed
    ``SkillActivationSpanEmitter | None`` class surface."""

    procedural_tier_snapshot_resolver: Any = None
    """R-003 — zero-arg procedural-tier resolver closure (IS spec v1.3
    §C-IS-05 §5.1). Bound at stage 6 CXA_WIRING to
    ``make_procedural_tier_snapshot_resolver(ctx)`` (the same closure that
    wires the §16.5 CP composers). Optional (``None`` = operator opt-out);
    NOT in ``_REQUIRED_FIELDS``. Typed ``Any`` per the same Protocol-vs-
    concrete-narrowing pattern as ``cp_is_wiring``; the frozen
    ``HarnessContext.procedural_tier_snapshot_resolver`` carries it for the CP
    driver's ``_append_step_ledger_entry`` per-step ledger write."""

    # Orchestrator bookkeeping — not part of HarnessContext. The declared
    # element types are explicit; pyright's `default_factory=list/dict`
    # inference reports the bare factory as `list[Unknown]`/`dict[Unknown]`,
    # so the strict reportUnknownVariableType is suppressed at these three.
    completed_stages: list[BootstrapStage] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    emitted_bootstrap_events: list[BootstrapStageCompleteEvent] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    cxa_stages: dict[str, Any] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    frozen: HarnessContext | None = None

    def freeze(self) -> HarnessContext:
        """Materialize the frozen `HarnessContext`. Raises if any required field None."""
        missing = tuple(name for name in _REQUIRED_FIELDS if getattr(self, name) is None)
        if missing:
            raise IncompleteBootstrapError(missing)

        ctx = HarnessContext(
            config=_bound(self.config),
            drained_flag=_bound(self.drained_flag),
            pause_requested_flag=_bound(self.pause_requested_flag),
            pause_resume_protocol=self.pause_resume_protocol,
            path_resolver=_bound(self.path_resolver),
            worktree_manager=_bound(self.worktree_manager),
            shadow_git=self.shadow_git,
            ledger_writer=_bound(self.ledger_writer),
            ledger_reader=self.ledger_reader,
            index=self.index,
            cache=self.cache,
            skills=_bound(self.skills),
            tool_contracts=_bound(self.tool_contracts),
            mcp_host=self.mcp_host,
            mcp_clients=_bound(self.mcp_clients),
            mcp_server=self.mcp_server,
            mcp_client_host=self.mcp_client_host,
            sandbox_dispatch=self.sandbox_dispatch,
            providers=_bound(self.providers),
            routing_manifest=_bound(self.routing_manifest),
            engine_selector=_bound(self.engine_selector),
            fallback_chain=_bound(self.fallback_chain),
            retry_breaker=_bound(self.retry_breaker),
            hitl_registry=_bound(self.hitl_registry),
            handoff_registry=_bound(self.handoff_registry),
            tracer_provider=self.tracer_provider,
            collector_daemon=self.collector_daemon,
            cost_chain=_bound(self.cost_chain),
            audit_writer=_bound(self.audit_writer),
            override_evaluator=_bound(self.override_evaluator),
            topology_dispatcher=_bound(self.topology_dispatcher),
            lifecycle_emitter=_bound(self.lifecycle_emitter),
            llm_dispatcher=_bound(self.llm_dispatcher),
            sub_agent_dispatcher=self.sub_agent_dispatcher,
            ask_user_question_surface=self.ask_user_question_surface,
            step_dispatchers=self.step_dispatchers,
            tool_dispatcher=self.tool_dispatcher,
            per_server_trust_evaluator=self.per_server_trust_evaluator,
            mcp_namespace_emitter=self.mcp_namespace_emitter,
            memory_tool_registry=self.memory_tool_registry,
            validator_framework=self.validator_framework,
            resume_context_holder=self.resume_context_holder,
            webhook_delivery_composer=self.webhook_delivery_composer,
            skill_activation_emitter=self.skill_activation_emitter,
            cp_is_wiring=(
                self.cxa_stages["cp_is_wiring"].wiring
                if "cp_is_wiring" in self.cxa_stages
                else None
            ),
            procedural_tier_snapshot_resolver=self.procedural_tier_snapshot_resolver,
        )
        self.frozen = ctx
        return ctx

"""Stage 5 LOOP_INIT — override evaluator, topology dispatcher, lifecycle
emitter, LLM dispatcher, sub-agent dispatcher, step-kind registry.

Per `Spec_Harness_Runtime_v1.md` v1.2 §2 stage 5 post-conditions +
§14.5 C-RT-15 (LLM-dispatch composer) + v1.6 §14.7 C-RT-17 (sub-agent
dispatch composer + step-kind routing registry per U-RT-59). On success:
``ctx.override_evaluator``, ``ctx.topology_dispatcher``,
``ctx.lifecycle_emitter``, ``ctx.llm_dispatcher``,
``ctx.sub_agent_dispatcher``, and ``ctx.step_dispatchers`` are all
non-None.

Composer order is free across the first three (no intra-stage
dependencies). The LLM dispatcher depends on ``ctx.providers``
(stage 3a) + ``ctx.tracer_provider`` (stage 4 OD); both are populated
before stage 5 begins per the bootstrap traversal order at C-RT-01.

On stage 5 success the orchestrator drains its buffered
`BootstrapStageCompleteEvent` records for stages 0..5 through the
freshly-materialized emitter.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from harness_core.workload_class import WorkloadClass
from harness_cp.workflow_driver_types import StepKind
from harness_od.audit_ledger_types import SignatureAlgorithm

from harness_cp.hitl_placement import HITLPlacementKind

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.child_workflow_runner import compose_child_workflow_runner
from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer
from harness_runtime.lifecycle.lifecycle_emitter import materialize_lifecycle_emitter_stage
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchBindError,
    materialize_llm_dispatcher_stage,
)
from harness_runtime.lifecycle.mcp_backed_ask_user_question_surface import (
    materialize_mcp_backed_ask_user_question_surface_stage,
)
from harness_runtime.lifecycle.override_evaluator import materialize_override_evaluator_stage
from harness_runtime.bootstrap.factories.runtime_tool_dispatcher_factory import (
    materialize_runtime_tool_dispatcher_stage,
)
from harness_runtime.lifecycle.retry_breaker_fallback import (
    materialize_retry_breaker_fallback_dispatcher_stage,
)
from harness_runtime.lifecycle.step_dispatchers import StepKindDispatcherRegistry
from harness_runtime.lifecycle.sub_agent_dispatch import RuntimeSubAgentDispatcher
from harness_runtime.lifecycle.sync_dispatcher_facade import (
    materialize_sync_dispatcher_facade,
)
from harness_runtime.lifecycle.topology_dispatcher import materialize_topology_dispatcher_stage
from harness_runtime.types import HarnessContext, RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 5 LOOP_INIT fields on `ctx`."""
    _ = workload_class

    override = materialize_override_evaluator_stage(config)
    ctx.override_evaluator = override.evaluator

    topology = materialize_topology_dispatcher_stage(config)
    ctx.topology_dispatcher = topology.dispatcher

    emitter = materialize_lifecycle_emitter_stage(config)
    ctx.lifecycle_emitter = emitter.emitter

    # LLM dispatcher (U-RT-52, C-RT-15) — depends on providers (stage 3a)
    # + tracer_provider (stage 4 OD). Both are populated by their declared
    # stages before stage 5 executes per C-RT-01 traversal order. The
    # factory raises ``LLMDispatchBindError`` if providers is empty —
    # surfaces as a stage-5 failure that the orchestrator's reverse-order
    # rollback handles.
    providers = ctx.providers
    if providers is None:
        raise LLMDispatchBindError(
            "ctx.providers is None at stage 5 — stage 3a CP_CLIENTS "
            "did not populate the providers map (bootstrap-orchestrator "
            "defect or stage-3a failure not surfaced before stage 5)"
        )
    tracer_provider = ctx.tracer_provider
    if tracer_provider is None:
        raise LLMDispatchBindError(
            "ctx.tracer_provider is None at stage 5 — stage 4 OD did "
            "not populate the tracer provider"
        )
    # `ctx.tracer_provider` is typed ``object`` per C-RT-04 (the spec
    # defers OTel-SDK type adoption); cast at this site to the
    # composer's structural shape.
    # U-OD-38: cost-attribution substrate is required at composer
    # construction per AC #1. Stage 4 OD populates ctx.cost_chain +
    # ctx.audit_writer; PRICE_TABLE_REF is sourced from RATE_TABLE_V1
    # default per §C-OD-28.3 (operator override via bootstrap config is a
    # future arc — ctx.rate_table extension on HarnessContext).
    from harness_od.rate_table_v1 import RATE_TABLE_V1
    if ctx.cost_chain is None or ctx.audit_writer is None:
        raise LLMDispatchBindError(
            "ctx.cost_chain / ctx.audit_writer is None at stage 5 — stage 4 "
            "OD did not populate the cost-attribution substrate required by "
            "U-OD-38 (C-OD-26.1 + C-OD-26.2 row 'llm_dispatch')."
        )
    bare_dispatcher = materialize_llm_dispatcher_stage(
        providers,
        cast(Any, tracer_provider),
        cost_chain=cast(Any, ctx.cost_chain),
        audit_writer=cast(Any, ctx.audit_writer),
        rate_table=RATE_TABLE_V1,
    )

    # U-RT-58 (C-RT-16 §14.6 D6): rebind ``ctx.llm_dispatcher`` from the
    # bare ``RuntimeLLMDispatcher`` to the ``RetryBreakerFallbackDispatcher``
    # wrapper. The driver call site at `workflow_driver.py:379` is unchanged
    # — the wrapper satisfies the same ``StepDispatcher`` Protocol. The bare
    # dispatcher becomes a private constructor arg of the wrapper.
    retry_breaker = ctx.retry_breaker
    if retry_breaker is None:
        raise LLMDispatchBindError(
            "ctx.retry_breaker is None at stage 5 — stage 3b CP_ROUTING "
            "did not populate the retry/breaker registry (U-RT-58 wrapper "
            "construction requires it per C-RT-16 §14.6 D6)"
        )
    fallback_chain = ctx.fallback_chain
    if fallback_chain is None:
        raise LLMDispatchBindError(
            "ctx.fallback_chain is None at stage 5 — stage 3b CP_ROUTING "
            "did not populate the fallback chain (U-RT-58 wrapper "
            "construction requires it per C-RT-16 §14.6 D6)"
        )
    # ---------------------------------------------------------------------
    # U-RT-60 (C-RT-18 §14.8) wrap-asymmetry fork APPLIED — row 1 chain:
    #   bare (async C-RT-15)
    #     → HITL gate composer (async; applicable_placements={PRE_ACTION})
    #     → RetryBreakerFallback (async C-RT-16; outer of HITL gate)
    #     → SyncDispatcherFacade (sync; registry binding)
    #
    # AskUserQuestionSurface is bound to the H_T-CP-20-substituted MCP-
    # backed surface (placeholder MCP callback at this arc; FastMCP host
    # wiring deferred per Phase 7d retirement batch 8 H_T-CP-20 RETIRE-READY).
    # Stage 4 OD's `audit_writer` + stage 1 IS's `ledger_writer` are
    # consumed by the HITL composer for the 4-substep audit-write at
    # spec §14.8.2 step 4h (same dep set as U-RT-59 sub-agent dispatch
    # per Q3 ratification — shared `cp_audit_to_od_audit` converter).
    if ctx.ledger_writer is None or ctx.audit_writer is None:
        raise LLMDispatchBindError(
            "ctx.ledger_writer / ctx.audit_writer is None at stage 5 — stage 1 "
            "IS / stage 4 OD must complete before stage 5 HITL gate composer "
            "construction per the runtime spec v1.11 §14.8.2 step 4h "
            "4-substep audit-write composition contract"
        )
    if ctx.mcp_host is None:
        raise LLMDispatchBindError(
            "ctx.mcp_host is None at stage 5 — stage 2 AS did not populate "
            "the MCP host (U-RT-60 AskUserQuestionSurface construction "
            "requires it per spec §14.8.3 v1.11 binding pin)"
        )
    # `ctx.mcp_host` is typed against the schema-level Protocol at
    # `harness_runtime.types.MCPHost`; the concrete dataclass at
    # `harness_runtime.lifecycle.mcp_host.MCPHost` is what stage 2 bound
    # (same C-RT-04 Protocol-vs-concrete pattern as `tracer_provider` +
    # `ledger_writer` / `audit_writer`).
    # U-RT-62 AC #4: stage 5 default binding rebinds the surface's
    # callback from `_PlaceholderMCPCallback` to `ServerCtxElicitCallback`
    # when `ctx.mcp_server` is materialized (post-stage-2 per U-RT-62
    # AC #2). The callback reads the in-flight `run_workflow` tool ctx
    # from `ctx.mcp_server._state['_current_tool_ctx']` + invokes
    # `await ctx.elicit(...)` outbound per spec v1.12 §14.8.3 topology
    # pin (Reading α CC-initiates). Test substrates that do not exercise
    # the MCP server path may leave `ctx.mcp_server = None` — the
    # surface then falls back to the placeholder for defensive failure.
    ask_surface = materialize_mcp_backed_ask_user_question_surface_stage(
        cast(Any, ctx.mcp_host),
        harness_mcp_server=ctx.mcp_server,
    )
    ctx.ask_user_question_surface = ask_surface

    hitl_inference = RuntimeHITLGateComposer(
        inner=bare_dispatcher,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(Any, ask_surface),
        ledger_writer=cast(Any, ctx.ledger_writer),
        audit_writer=cast(Any, ctx.audit_writer),
        tracer_provider=cast(Any, tracer_provider),
        audit_signing_key_id="harness-runtime-dev",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
    )
    ctx.llm_dispatcher = materialize_retry_breaker_fallback_dispatcher_stage(
        inner=cast(Any, hitl_inference),
        retry_breaker=retry_breaker,
        fallback_chain=fallback_chain,
        tracer_provider=cast(Any, tracer_provider),
    )

    # ---------------------------------------------------------------------
    # U-RT-59 (C-RT-17 §14.7): sub-agent dispatch composer + step-kind
    # routing registry. Per spec §14.7.7 "Integration with C-RT-04": two
    # new HarnessContext fields at v1.6 (`sub_agent_dispatcher`,
    # `step_dispatchers`); both bound here.
    #
    # v1.7 wiring lifts the v1.6 MVP INFERENCE_STEP carve-out per the Path B
    # resolution of the U-RT-59 async/sync StepDispatcher Class 1 fork
    # (`.harness/class_1_tension_u_rt_59_async_sync_step_dispatcher.md`):
    # `ctx.llm_dispatcher` (the U-RT-58 `RetryBreakerFallbackDispatcher`
    # wrapper) is async; the CP driver's `StepDispatcher` Protocol is sync;
    # the registry binds the wrapper through a `SyncDispatcherFacade` that
    # captures this loop and schedules coroutines back via
    # `asyncio.run_coroutine_threadsafe(...).result(timeout=...)` from the
    # worker thread that runs `execute_workflow` per api.py:399. Stage 5 runs
    # in an `async def` awaited from `await run_bootstrap(...)` at
    # api.py:349 — the running loop here IS the loop that hosts the
    # subsequent `asyncio.to_thread`, so `materialize_sync_dispatcher_facade`
    # captures the correct loop. Tool / HITL / validator step kinds remain
    # unbound per spec §14.7 (follow-on composer arcs).
    #
    # Child workflow runner closes over `ctx` (the _MutableHarnessContext);
    # at runtime invocation it reads `ctx.step_dispatchers` (set below) +
    # casts ctx to the CP driver's structural `DriverContext` Protocol.
    # The mutable ctx satisfies the Protocol structurally — same pattern
    # api.py uses on the frozen ctx.
    child_runner = compose_child_workflow_runner(cast(HarnessContext, ctx))

    # v1.7 §14.7.2 step 8 4-substep audit composition extends the
    # dispatcher's dependency set with the IS state-ledger writer (8b F2-
    # write), the OD audit writer (8d IS-anchored append), and signing
    # config + time source for the CP→OD converter at 8c. The audit-writer
    # availability check above (HITL composer construction) covers the
    # same dependency set.
    # Audit-signing config — operator surface deferred per spec §14.7
    # "Deferred to implementation discretion" + ADR-D5 v1.3 §1.4.1 (HSM /
    # KMS / keystore custody). v1.7 MVP binds a deployment-default value;
    # operator-tunable surface is a follow-on RuntimeConfig extension.
    bare_sub_agent_dispatcher = RuntimeSubAgentDispatcher(
        handoff_registry=ctx.handoff_registry,  # type: ignore[arg-type]  # narrowed at stage 3b
        topology_dispatcher=topology.dispatcher,
        tracer_provider=cast(Any, tracer_provider),
        child_workflow_runner=child_runner,
        # `ctx.ledger_writer` / `ctx.audit_writer` are typed as Protocols at
        # `harness_runtime.types` (C-RT-04 schema layer); the dispatcher
        # consumes the concrete dataclass types from `harness_runtime.lifecycle`.
        # The structural shape matches; cast bridges the Protocol → concrete
        # mismatch at the composition site per the C-RT-04 pattern reused at
        # tracer_provider above.
        ledger_writer=cast(Any, ctx.ledger_writer),
        audit_writer=cast(Any, ctx.audit_writer),
        audit_signing_key_id="harness-runtime-dev",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        time_source=lambda: datetime.now(UTC),
    )

    # U-RT-60 (C-RT-18 §14.8) wrap-asymmetry fork APPLIED — row 2 chain:
    #   bare sub-agent dispatcher (sync C-RT-17)
    #     → HITL gate composer (async; applicable_placements={SUB_AGENT_BOUNDARY})
    #     → SyncDispatcherFacade (sync; registry binding)
    #
    # Inner-call shape: HITL composer body invokes `self.inner.dispatch(...)`
    # via the duck-typed `_dispatch_inner` helper at `hitl_gate_composer.py`;
    # for sync C-RT-17 inner the call returns a Mapping directly (no await
    # needed), per fork §7.2 Q3 ratification.
    hitl_sub_agent = RuntimeHITLGateComposer(
        inner=bare_sub_agent_dispatcher,
        applicable_placements=frozenset({HITLPlacementKind.SUB_AGENT_BOUNDARY}),
        ask_user_question_surface=cast(Any, ask_surface),
        ledger_writer=cast(Any, ctx.ledger_writer),
        audit_writer=cast(Any, ctx.audit_writer),
        tracer_provider=cast(Any, tracer_provider),
        audit_signing_key_id="harness-runtime-dev",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
    )
    ctx.sub_agent_dispatcher = hitl_sub_agent

    # Registry binding: both rows wrap through `SyncDispatcherFacade` at the
    # top so the CP `StepDispatcher` Protocol (sync) is satisfied uniformly.
    # `materialize_sync_dispatcher_facade` captures the running event loop
    # (this stage executes on the outer api.py loop per loop-capture-timing
    # invariant). Result-timeout reuses `config.drain_timeout_seconds`;
    # tracked at Class 3 drift item 7 for the future
    # `step_dispatch_timeout_seconds` config split.
    inference_step_dispatcher = materialize_sync_dispatcher_facade(
        cast(Any, ctx.llm_dispatcher),
        result_timeout_seconds=config.drain_timeout_seconds,
    )
    sub_agent_step_dispatcher = materialize_sync_dispatcher_facade(
        cast(Any, hitl_sub_agent),
        result_timeout_seconds=config.drain_timeout_seconds,
    )

    # ---------------------------------------------------------------------
    # U-RT-68 (REWRITTEN at v2.12): stage-5 TOOL_STEP wire-up via the
    # U-RT-75 `materialize_runtime_tool_dispatcher_stage` factory. Per
    # spec v1.16 §14.9.3 stage-5 prose + §14.11 C-RT-21: the factory
    # composes the 5-step chain (PerServerTrustEvaluator → MCPClientNamespaceEmitter
    # → bare RuntimeToolDispatcher → RetryBreakerToolDispatcher wrap →
    # return wrapper). The bare dispatcher is private to the wrapper per
    # spec §14.9.6 inv 6; ctx.tool_dispatcher binds to the wrapper.
    #
    # Mirrors the existing `ctx.llm_dispatcher` wrap-binding pattern at
    # C-RT-16 §14.6 D6 above. Step-dispatcher registry below extends with
    # TOOL_STEP → tool_step_dispatcher facade.
    ctx.tool_dispatcher = await materialize_runtime_tool_dispatcher_stage(
        ctx, config
    )
    tool_step_dispatcher = materialize_sync_dispatcher_facade(
        ctx.tool_dispatcher,
        result_timeout_seconds=config.drain_timeout_seconds,
    )

    ctx.step_dispatchers = StepKindDispatcherRegistry(
        dispatchers={
            StepKind.INFERENCE_STEP: inference_step_dispatcher,
            StepKind.SUB_AGENT_DISPATCH: sub_agent_step_dispatcher,
            StepKind.TOOL_STEP: tool_step_dispatcher,
        },
    )

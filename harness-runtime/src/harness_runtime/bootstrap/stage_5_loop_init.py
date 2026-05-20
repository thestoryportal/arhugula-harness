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

from typing import Any, cast

from harness_core.workload_class import WorkloadClass
from harness_cp.workflow_driver_types import StepKind

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.child_workflow_runner import compose_child_workflow_runner
from harness_runtime.lifecycle.lifecycle_emitter import materialize_lifecycle_emitter_stage
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchBindError,
    materialize_llm_dispatcher_stage,
)
from harness_runtime.lifecycle.override_evaluator import materialize_override_evaluator_stage
from harness_runtime.lifecycle.retry_breaker_fallback import (
    materialize_retry_breaker_fallback_dispatcher_stage,
)
from harness_runtime.lifecycle.step_dispatchers import StepKindDispatcherRegistry
from harness_runtime.lifecycle.sub_agent_dispatch import RuntimeSubAgentDispatcher
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
    bare_dispatcher = materialize_llm_dispatcher_stage(
        providers, cast(Any, tracer_provider)
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
    ctx.llm_dispatcher = materialize_retry_breaker_fallback_dispatcher_stage(
        inner=bare_dispatcher,
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
    # v1.6 MVP binds only `SUB_AGENT_DISPATCH` in the registry per the
    # Class 1 fork on U-RT-58 wrapper async/sync mismatch (the async
    # `llm_dispatcher.dispatch` does not compose with the sync driver
    # call site as a registry binding). `INFERENCE_STEP` binding deferred
    # to follow-on arc. Tool / HITL / validator step kinds remain unbound
    # per spec §14.7 (follow-on composer arcs).
    #
    # Child workflow runner closes over `ctx` (the _MutableHarnessContext);
    # at runtime invocation it reads `ctx.step_dispatchers` (set below) +
    # casts ctx to the CP driver's structural `DriverContext` Protocol.
    # The mutable ctx satisfies the Protocol structurally — same pattern
    # api.py uses on the frozen ctx.
    child_runner = compose_child_workflow_runner(cast(HarnessContext, ctx))

    sub_agent_dispatcher = RuntimeSubAgentDispatcher(
        handoff_registry=ctx.handoff_registry,  # type: ignore[arg-type]  # narrowed at stage 3b
        topology_dispatcher=topology.dispatcher,
        tracer_provider=cast(Any, tracer_provider),
        child_workflow_runner=child_runner,
    )
    ctx.sub_agent_dispatcher = sub_agent_dispatcher

    ctx.step_dispatchers = StepKindDispatcherRegistry(
        dispatchers={StepKind.SUB_AGENT_DISPATCH: sub_agent_dispatcher},
    )

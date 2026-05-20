"""Stage 5 LOOP_INIT — override evaluator, topology dispatcher, lifecycle emitter.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 5 post-conditions:
`ctx.override_evaluator`, `ctx.topology_dispatcher`, `ctx.lifecycle_emitter`
all non-None.

Composer order is free (no intra-stage dependencies). On stage 5 success the
orchestrator drains its buffered `BootstrapStageCompleteEvent` records for
stages 0..5 through the freshly-materialized emitter.
"""

from __future__ import annotations

from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.lifecycle_emitter import materialize_lifecycle_emitter_stage
from harness_runtime.lifecycle.override_evaluator import materialize_override_evaluator_stage
from harness_runtime.lifecycle.topology_dispatcher import materialize_topology_dispatcher_stage
from harness_runtime.types import RuntimeConfig

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

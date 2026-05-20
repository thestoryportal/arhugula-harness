"""Stage 3b CP_ROUTING — routing manifest, engine selector, fallback, retry/breaker, HITL, handoff.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 3b post-conditions:
`ctx.routing_manifest`, `ctx.engine_selector`, `ctx.fallback_chain`,
`ctx.retry_breaker`, `ctx.hitl_registry`, `ctx.handoff_registry` all non-None.

Composer order within the stage is free (no intra-stage dependencies among
the 6 composers); the orchestrator calls them in alphabetical-by-field order
for determinism.
"""

from __future__ import annotations

from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.engine_selector import materialize_engine_selector
from harness_runtime.lifecycle.fallback_chain import materialize_fallback_chain_stage
from harness_runtime.lifecycle.handoff import materialize_handoff_stage
from harness_runtime.lifecycle.hitl_placement import materialize_hitl_placement_stage
from harness_runtime.lifecycle.retry_breaker import materialize_retry_breaker_stage
from harness_runtime.lifecycle.routing_manifest import materialize_routing_manifest_stage
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 3b CP_ROUTING fields on `ctx`."""
    assert ctx.path_resolver is not None, "stage 1 IS must precede stage 3b"

    # 1. Routing manifest (depends on path resolver for residence path).
    routing = materialize_routing_manifest_stage(
        config,
        ctx.path_resolver,
        workload_class,
    )
    ctx.routing_manifest = routing.manifest

    # 2. Engine selector.
    ctx.engine_selector = materialize_engine_selector(config)

    # 3. Cross-family fallback chain.
    fallback = materialize_fallback_chain_stage(config)
    ctx.fallback_chain = fallback.chain

    # 4. Retry/breaker registry.
    retry = materialize_retry_breaker_stage(config)
    ctx.retry_breaker = retry.registry

    # 5. HITL placement registry.
    hitl = materialize_hitl_placement_stage(config)
    ctx.hitl_registry = hitl.registry

    # 6. Sub-agent handoff registry.
    handoff = materialize_handoff_stage(config)
    ctx.handoff_registry = handoff.registry

"""Stage 4 OD — tracer + span_processor + collector + ring buffer + cost chain + audit writer.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 4 post-conditions:
`opentelemetry.trace.get_tracer_provider()` returns the runtime-registered
provider; `ctx.collector_daemon` is running (health-check ok); `ctx.cost_chain`,
`ctx.audit_writer` non-None.

Composer call order (intra-stage dependencies):
1. `materialize_tracer_provider_stage` — globally registers TracerProvider.
2. `materialize_span_processor_stage(config, provider)` — attaches BSP + exporter.
3. `materialize_collector_daemon_stage(config)` — supervisor (NOT started yet).
4. `await daemon.start()` — start the collector daemon explicitly (docstring
   at `lifecycle/collector_daemon.py` line ~60: "The bootstrap orchestrator
   (U-RT-43) calls `await stage.daemon.start()` at the stage 4 entry").
5. `materialize_ring_buffer_stage(config, daemon)` — depends on running daemon.
6. `materialize_cost_attribution_stage(config)`.
7. `materialize_audit_writer_stage(config, ledger_writer)` — depends on stage 1.

**Tracer rollback (Class 3 informational).** OTel has no `unset_tracer_provider`
API. On stage 4 failure, rollback leaves the global provider registered;
subsequent process invocations replace via `set_tracer_provider`. Deferred to
U-RT-44/45 shutdown work if a true unregister API is needed.
"""

from __future__ import annotations

from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.factories.validator_framework_factory import (
    materialize_validator_framework_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.audit_writer import materialize_audit_writer_stage
from harness_runtime.lifecycle.collector_daemon import materialize_collector_daemon_stage
from harness_runtime.lifecycle.cost_attribution import materialize_cost_attribution_stage
from harness_runtime.lifecycle.ring_buffer import materialize_ring_buffer_stage
from harness_runtime.lifecycle.span_processor import materialize_span_processor_stage
from harness_runtime.lifecycle.tracer_provider import materialize_tracer_provider_stage
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 4 OD fields on `ctx`."""
    _ = workload_class
    assert ctx.ledger_writer is not None, "stage 1 IS must precede stage 4 OD"

    # 1. Tracer provider — globally registered.
    tracer = materialize_tracer_provider_stage(config)
    ctx.tracer_provider = tracer.provider

    # 2. Span processor + exporter (attaches to the registered tracer provider).
    materialize_span_processor_stage(config, tracer.provider)
    # The span processor's lifetime is tied to the tracer provider; the stage
    # record is not held on HarnessContext (the BSP is reachable via the
    # tracer provider's processor list). The C-RT-10 shutdown will need to
    # retain a typed handle — addressed at U-RT-45.

    # 3. Collector daemon supervisor (constructed; NOT yet started).
    daemon_stage = materialize_collector_daemon_stage(config)

    # 4. Start the daemon. Failure here surfaces as a stage 4 failure and
    # triggers rollback of stages 0-3 + stage-4 partial-state cleanup.
    await daemon_stage.daemon.start()
    ctx.collector_daemon = daemon_stage.daemon

    # 5. Ring buffer (depends on running daemon).
    materialize_ring_buffer_stage(config, daemon_stage.daemon)
    # Like the span processor, the ring buffer's lifetime is tied to the
    # daemon supervisor; HarnessContext exposes the daemon, not the buffer.

    # 6. Cost attribution chain.
    cost = materialize_cost_attribution_stage(config)
    ctx.cost_chain = cost.chain

    # 7. Audit-ledger writer (depends on stage 1 ledger writer).
    audit = materialize_audit_writer_stage(config, ctx.ledger_writer)
    ctx.audit_writer = audit.writer

    # 8. Validator framework (U-RT-84) — final stage-4 binding per runtime
    # spec v1.18 §14.13.3. Operator-opt-in: `None` (default) preserves the
    # v1.17 production-default state; non-`None` constructs an empty-registry
    # ConcreteValidatorFramework per Reading A scope.
    ctx.validator_framework = await materialize_validator_framework_stage(config)

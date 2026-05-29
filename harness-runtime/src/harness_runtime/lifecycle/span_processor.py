"""BatchSpanProcessor + OTLPSpanExporter attach — stage 4 OD (U-RT-28).

Per `Spec_Harness_Runtime_v1.md` v1.1 §6 (C-RT-06 TracerProvider lifecycle —
F-P2-3 absorption) step 3 and the Phase 2 Session 3 Track A atomic
decomposition §L6 (U-RT-28). The runtime attaches a `BatchSpanProcessor`
backed by an `OTLPSpanExporter` to the U-RT-27 `TracerProvider`. This
completes the C-RT-06 construction sequence step 3 — step 4 (global
registration) is already done at U-RT-27.

**BSP cadence + batching constants.** Sourced from `RuntimeConfig.collector`
(U-RT-08), which defaults to the OD-spec-committed BSP constants per
C-OD-19 §19.1:

- `batch_window_seconds=5` → `schedule_delay_millis=5_000`.
- `batch_size=512` → `max_export_batch_size=512`.
- `max_queue_size` defaults to the OTel SDK default (2048); operator override
  via a future `CollectorConfig` extension when needed.

**OTLP exporter protocol.** Spec §6 "deferred to implementation discretion"
clause: "exporter protocol (suggest gRPC; HTTP/protobuf accepted via
config)". At HEAD this module binds `OTLPSpanExporter` from
`opentelemetry.exporter.otlp.proto.grpc.trace_exporter` — gRPC over the
endpoint in `config.otel.otlp_endpoint`. The exporter does NOT connect at
construction time (lazy connect on first export), so a missing collector
surfaces as a `RT-FAIL-TRANSIENT` at flush-time per C-RT-06 failure-mode
taxonomy rather than at bootstrap. A future unit may wire HTTP/protobuf or
expose an `OTLPExporterFactory` keyword for operator override.

**Reachability matrix.** AC #2 ("reachability matrix enforced") wires the
OD-canonical `assert_otlp_reachable_from_sandbox` decision into the
registry. The runtime itself does not have a single sandbox tier — the
sandbox-tier-vs-placement composition is per-dispatch (each sandbox-tier
dispatched call must reach the configured collector placement). The
registry exposes `assert_reachable(sandbox_tier)` so consumer-side dispatch
code (U-RT-15 sandbox table, future U-RT-40 topology dispatcher) can
enforce the §20.3 matrix at the dispatch site. The composer itself runs a
single check: the BOOTSTRAP runtime's own sandbox-tier (Tier-1 process) MUST
reach the configured `CollectorConfig.placement` — a violation at bootstrap
raises `SpanProcessorReachabilityError`. The runtime bootstraps inside the
host process (Tier-1) per F-P2-5; this floor is non-operator-tunable at
bootstrap.

Per-component landing posture:

- `SpanProcessorBindError` — bootstrap-time bind failure (RT-FAIL-BOOTSTRAP)
  for malformed exporter/processor construction.
- `SpanProcessorReachabilityError` — bootstrap-time reachability failure
  (RT-FAIL-BOOTSTRAP) when the bootstrap-tier (Tier-1 process) cannot reach
  the configured `CollectorPlacement` per the §20.3 matrix.
- `SpanProcessorStage` — frozen materialization stage carrying the
  attached processor + exporter handles + a `flush(timeout_millis)` method
  delegating to `processor.force_flush(timeout_millis)`.
- `materialize_span_processor_stage(config, provider, *, exporter=None)` —
  composer.

Scope discipline (U-RT-28 boundary held): NO collector daemon supervision
(U-RT-29), NO ring-buffer or sqlite rotation wiring (U-RT-30), NO
cost-attribution chain (U-RT-31), NO audit-ledger writer (U-RT-32). This
unit attaches the BSP + exporter only.
"""

from __future__ import annotations

from dataclasses import dataclass

from harness_as.sandbox_tier import SandboxTier
from harness_od.per_sandbox_tier_otlp_reachability import (
    ReachabilityViolation,
    assert_otlp_reachable_from_sandbox,
)
from harness_od.redaction_span_processor import RedactionSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter

from harness_runtime.types import RuntimeConfig

__all__ = [
    "SpanProcessorBindError",
    "SpanProcessorReachabilityError",
    "SpanProcessorStage",
    "materialize_span_processor_stage",
]


#: Bootstrap-time sandbox tier of the runtime process itself. The runtime
#: bootstraps in the host process at Tier-1 (no isolation around the runtime
#: itself); per-tool dispatches at U-RT-15 enforce their own tier reachability.
_BOOTSTRAP_SANDBOX_TIER: SandboxTier = SandboxTier.TIER_1_PROCESS


class SpanProcessorBindError(Exception):
    """Bootstrap-time BSP/exporter bind failure (RT-FAIL-BOOTSTRAP).

    Raised when the OTLP exporter or BatchSpanProcessor cannot be
    constructed at composer time. Surfaces at
    `materialize_span_processor_stage`, never at runtime."""


class SpanProcessorReachabilityError(Exception):
    """Bootstrap-time reachability failure (RT-FAIL-BOOTSTRAP).

    Raised when the bootstrap-tier (Tier-1 process per F-P2-5) cannot reach
    the configured `CollectorPlacement` per the C-OD-20 §20.3 matrix. Wraps
    the OD-canonical `ReachabilityViolation` to keep the runtime-side
    bootstrap-failure surface typed."""


@dataclass(frozen=True, slots=True)
class SpanProcessorStage:
    """Frozen result of stage 4 OD BSP + exporter materialization.

    The bootstrap orchestrator (U-RT-43) holds this stage for the lifetime
    of the runtime — the exporter and processor are referenced by the
    `TracerProvider` via `add_span_processor`, but the stage retains a
    typed handle so the shutdown path (C-RT-10) can call
    `processor.force_flush(...)` then `processor.shutdown()` in deterministic
    order.

    The runtime attaches TWO processors at this stage in registration order:
    (1) `RedactionSpanProcessor` (OD spec C-OD-12 §12.1 + C-OD-13 §13.2 —
    pre-collector redaction at SDK / wrapper boundary BEFORE the BSP buffer);
    (2) `BatchSpanProcessor(exporter)`. Consumers acquire tracers via
    `opentelemetry.trace.get_tracer(...)` and emit spans which flow through
    BOTH processors — redaction first (strips §12.1 default-off content
    attributes from the attribute bag), then BSP (enqueues the now-redacted
    span for export on cadence or on `flush()` call).
    """

    processor: BatchSpanProcessor
    exporter: SpanExporter
    redaction_processor: RedactionSpanProcessor

    def flush(self, timeout_millis: int = 30_000) -> bool:
        """Force-flush buffered spans through the exporter.

        Returns True iff the flush completed within `timeout_millis`. AC #1
        surface (spans flush on demand). Delegates to
        `BatchSpanProcessor.force_flush`.
        """
        return self.processor.force_flush(timeout_millis=timeout_millis)


def materialize_span_processor_stage(
    config: RuntimeConfig,
    provider: TracerProvider,
    *,
    exporter: SpanExporter | None = None,
) -> SpanProcessorStage:
    """Attach a `BatchSpanProcessor(OTLPSpanExporter(...))` to `provider`.

    Stage 4 composer (C-RT-06 step 3). Construction sequence:

    1. Bootstrap-tier reachability check: `assert_otlp_reachable_from_sandbox(
       TIER_1_PROCESS, config.collector.placement)`. A violation raises
       `SpanProcessorReachabilityError`.
    2. Construct the OTLP exporter from `config.otel.otlp_endpoint`
       (gRPC at HEAD). Tests pass an `exporter` keyword override (commonly
       `InMemorySpanExporter`) to avoid network construction.
    3. Construct `BatchSpanProcessor(exporter,
       max_export_batch_size=config.collector.batch_size,
       schedule_delay_millis=config.collector.batch_window_seconds * 1000)`.
    4. `provider.add_span_processor(bsp)` — the processor is now live on the
       provider's pipeline.

    Parameters
    ----------
    config :
        Frozen `RuntimeConfig`. Drives the endpoint + BSP cadence + placement.
    provider :
        The `TracerProvider` from U-RT-27 (production: registered globally;
        tests: optionally not).
    exporter :
        Optional `SpanExporter` override for tests. When None (production),
        constructs `OTLPSpanExporter(endpoint=config.otel.otlp_endpoint)`.

    Returns
    -------
    SpanProcessorStage
        Frozen handle carrying the attached processor + exporter.

    Raises
    ------
    SpanProcessorReachabilityError
        When the bootstrap tier (Tier-1 process) cannot reach
        `config.collector.placement` per C-OD-20 §20.3.
    SpanProcessorBindError
        Wrap-and-re-raise for exporter / BSP construction failures.
    """
    try:
        assert_otlp_reachable_from_sandbox(
            _BOOTSTRAP_SANDBOX_TIER, config.collector.placement
        )
    except ReachabilityViolation as exc:
        raise SpanProcessorReachabilityError(
            f"bootstrap-tier ({_BOOTSTRAP_SANDBOX_TIER.value}) cannot reach "
            f"configured CollectorPlacement ({config.collector.placement.value}) "
            f"per C-OD-20 §20.3: {exc}"
        ) from exc

    try:
        resolved_exporter: SpanExporter = exporter if exporter is not None else (
            OTLPSpanExporter(endpoint=config.otel.otlp_endpoint)
        )
        processor = BatchSpanProcessor(
            resolved_exporter,
            max_export_batch_size=config.collector.batch_size,
            schedule_delay_millis=config.collector.batch_window_seconds * 1000,
        )
        redaction_processor = RedactionSpanProcessor(
            persona_tier=config.persona_tier
        )
    except Exception as exc:
        raise SpanProcessorBindError(
            f"BatchSpanProcessor / OTLPSpanExporter construction failed: {exc}"
        ) from exc

    # Redaction MUST register BEFORE the BSP — the synchronous OTLP exporter
    # serializes the SpanData inside its on_end path, so any attribute the
    # BSP enqueues for export is what reaches the wire. Per OD spec C-OD-13
    # §13.2: pre-collector redaction at SDK / wrapper boundary BEFORE the
    # BatchSpanProcessor buffer.
    provider.add_span_processor(redaction_processor)
    provider.add_span_processor(processor)
    return SpanProcessorStage(
        processor=processor,
        exporter=resolved_exporter,
        redaction_processor=redaction_processor,
    )

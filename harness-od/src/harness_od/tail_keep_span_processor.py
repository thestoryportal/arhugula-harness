"""C-OD-09 §9.1 production-time tail-based-sampling + §10.2 tail-keep-on-classification.

H_T-OD-3 PARTIAL → RETIRE-READY substrate (gate (a)). Closes the
"tail-keep-on-classification at the OTLP collector boundary per §9.1"
deferral inherited from OD spec v1.2 §9.3 implementer-discretion clause.

**Algorithm shape (per §9.3 implementer-discretion choice).**

OTel-Python's SpanProcessor chain invokes EACH registered processor
independently at `on_end` — a processor cannot prevent a sibling processor
(e.g., the `BatchSpanProcessor` exporter) from receiving a span. To
implement tail-based KEEP-OR-DROP semantics over a span chain, this
processor takes the **wrap-BSP** approach: the downstream processor (the
BSP that holds the OTLP exporter) is NOT registered directly on the
`TracerProvider`; instead, this `TailKeepSpanProcessor` wraps it as
`downstream=`, intercepting all `on_end` calls and selectively forwarding
buffered spans on root-close based on §10.2 classification triggers.

**Engagement gate (per §9.1).** At local-development deployment surface,
§9.1 mandates **head-based sampling** — the sampler at span creation is
the binding decision; tail-keep semantics do NOT apply. At
self-hosted-server + managed-cloud surfaces, §9.1 mandates **tail-based
sampling with tail-keep-on-classification**. Engagement is therefore
gated at construction (`materialize_span_processor_stage` chooses to wrap
the BSP with this processor iff `deployment_surface !=
LOCAL_DEVELOPMENT`); when wrapped, this processor honors the
§10.2 triggers exhaustively.

**Per-trace buffering algorithm.**

1. `on_end(span)` — span ends; the processor:
   - If the span's name is in the always-sampled set per §9.2 (per
     `is_always_sampled`) → forward immediately to `downstream`. Always-
     sampled spans skip the buffer to keep memory bounded; their tree-
     siblings buffered separately get the keep-decision on root close.
   - Else → append the span to the per-trace buffer keyed by `trace_id`.
     Inspect `is_classification_trigger(span)` and OR-merge into the per-
     trace keep flag.
   - If the span is a **root close** (parent SpanContext is None) →
     materialize the keep decision for the trace: forward buffered spans
     to `downstream` iff the keep flag is True; otherwise drop them.
     Clear the buffer + keep flag entries for this trace_id.

2. `force_flush(timeout_millis)` — flush any still-buffered traces (treat
   them as keep-all to avoid silent loss on shutdown) + delegate to
   `downstream.force_flush()`. Returns the downstream flush result.

3. `shutdown()` — flush + delegate to `downstream.shutdown()`.

**Drop semantics (false-but-bounded).** Because trace-end (root close) is
detected by parent-context inspection at `on_end`, a trace that never
materializes a root-close span will accumulate in the buffer until
`force_flush` / `shutdown`. The bootstrap-orchestrator's drain path
(C-RT-10) calls `force_flush` before `shutdown`, so accumulated traces are
flushed before exporter teardown — the keep decision defaults to keep-all
at flush time to avoid silent loss. This is the **trust-sampler-on-base-
rate** posture: the upstream `HarnessCompositeSampler` (per H_T-OD-3
substrate batch-34) has already applied the §10.3 per-cell base-rate to
the head-based sampling decision; this processor only adds the §10.2
classification-trigger PRESERVATION layer atop that decision. Spans the
sampler dropped never enter `on_end`; this processor cannot resurrect
them. The keep semantics here apply to spans the sampler RECORDED — for
those, classification triggers ensure trace-tree preservation across the
batch-export boundary.

**Bounded-buffer carve-out (MVP scope-lock).** This MVP does NOT bound
buffer size by trace count or by per-trace span count. A pathological
producer that opens 10^6 traces without ever closing a root would
accumulate without bound. Future operator-tunable bounds at
`CollectorConfig` are a follow-on arc per §9.3 implementer-discretion.

**Spec authority.** OD spec v1.2 §C-OD-09 §9.1 (per-deployment-surface
sampling mode) + §9.2 (always-sampled exception set) + §9.3 (sampling-
discipline invariants + implementer-discretion clause on tail-based
algorithm) + §C-OD-10 §10.2 (3 classification triggers).

Authority anchors: `harness-od/src/harness_od/base_rate_set_and_envelope.py`
canonical `TAIL_KEEP_RULES` declaration site;
`harness-od/src/harness_od/tail_keep_classification.py` per-span trigger
predicate; `harness-od/src/harness_od/sampling_mode.py` always-sampled
set + `is_always_sampled` decomposed-prefix lookup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_classification import is_classification_trigger

if TYPE_CHECKING:
    pass

__all__ = [
    "TailKeepSpanProcessor",
]


class TailKeepSpanProcessor(SpanProcessor):
    """OTel SpanProcessor wrapping a downstream processor with tail-keep-on-classification.

    Per OD spec §C-OD-09 §9.1 (production-time tail-based-sampling) +
    §10.2 (3 classification triggers) + §9.3 (implementer-discretion
    algorithm). Buffers non-always-sampled spans per trace_id; on root-
    close, forwards the buffer to `downstream` iff any span in the trace
    carried a §10.2 classification trigger, else drops. Always-sampled
    spans (per §9.2) bypass the buffer and forward immediately.

    The downstream processor is typically a `BatchSpanProcessor(exporter)`;
    this processor is the registered processor on the `TracerProvider`.
    """

    def __init__(self, *, downstream: SpanProcessor) -> None:
        self._downstream: SpanProcessor = downstream
        # Per-trace_id buffer of non-always-sampled spans pending root-close
        # keep decision. Keyed by the int form of OTel trace_id.
        self._buffer: dict[int, list[ReadableSpan]] = {}
        # Per-trace_id keep flag — True iff any span in the trace carried a
        # §10.2 classification trigger. OR-merged at on_end.
        self._keep: dict[int, bool] = {}

    @property
    def downstream(self) -> SpanProcessor:
        """The wrapped downstream processor (test introspection)."""
        return self._downstream

    @property
    def buffered_trace_count(self) -> int:
        """Number of traces currently buffered (test introspection)."""
        return len(self._buffer)

    def on_start(
        self,
        span: Span,
        parent_context: Context | None = None,
    ) -> None:
        """Forward to downstream; no buffering at start (decisions are at end)."""
        self._downstream.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan) -> None:
        """Buffer non-always-sampled spans by trace_id; flush-or-drop on root close.

        Always-sampled spans (per §9.2) forward immediately to `downstream`.
        Non-always-sampled spans buffer pending root close; on root close,
        the trace's buffered spans flush to `downstream` iff any span in
        the trace carried a §10.2 classification trigger, else drop.
        """
        # §9.2 always-sampled set: forward immediately, do not buffer.
        # These spans (`audit.*`, `sandbox.violation`, `hitl.*`, etc.) ARE
        # always-sampled per spec and their tree-siblings are buffered
        # separately under the trace_id; the always-sampled span itself
        # never depends on tail-keep buffering.
        if is_always_sampled(span.name):
            self._downstream.on_end(span)
            # Still mark the trace keep-flag if the always-sampled span is
            # a classification trigger (sandbox.violation + breaker.tripped
            # are both in §9.2 AND in §10.2) so tree-siblings buffered
            # under the same trace get preserved at root close.
            ctx = span.get_span_context()
            assert ctx is not None  # a span reaching on_end always has a context
            if is_classification_trigger(span):
                self._keep[ctx.trace_id] = True
            return

        ctx = span.get_span_context()
        assert ctx is not None  # a span reaching on_end always has a context
        trace_id = ctx.trace_id

        self._buffer.setdefault(trace_id, []).append(span)
        if is_classification_trigger(span):
            self._keep[trace_id] = True

        # Root close detection: parent SpanContext is None means this span
        # has no parent in the recorded trace (it is the local-root). At
        # span-end, OTel `ReadableSpan.parent` is `None` for the root.
        if span.parent is None:
            self._materialize_trace_decision(trace_id)

    def _materialize_trace_decision(self, trace_id: int) -> None:
        """Flush or drop the buffered spans for `trace_id` per the keep flag."""
        buffered = self._buffer.pop(trace_id, [])
        keep = self._keep.pop(trace_id, False)
        if not keep:
            return
        for span in buffered:
            self._downstream.on_end(span)

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        """Flush any still-buffered traces (keep-all) + delegate to downstream.

        At force-flush, accumulated traces (those never having materialized
        a root-close span) are forwarded to `downstream` as keep-all to
        avoid silent loss on shutdown. Then delegates to
        `downstream.force_flush(timeout_millis)`.
        """
        # Drain the buffer — keep-all on shutdown to avoid silent loss.
        for trace_id in list(self._buffer.keys()):
            for span in self._buffer[trace_id]:
                self._downstream.on_end(span)
            self._buffer.pop(trace_id, None)
            self._keep.pop(trace_id, None)
        return self._downstream.force_flush(timeout_millis=timeout_millis)

    def shutdown(self) -> None:
        """Flush + delegate to downstream.shutdown()."""
        self.force_flush()
        self._downstream.shutdown()

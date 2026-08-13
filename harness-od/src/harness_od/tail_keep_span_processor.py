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

**Bounded-buffer bounds (OD spec v1.28 — §9.3 implementer-discretion).**
The v1.27 §2(a) carve-out (MVP did NOT bound buffer size) is CLOSED at OD
spec v1.28: the processor now accepts two optional operator-tunable
ceilings, supplied in production from `CollectorConfig`:

- ``max_buffered_traces`` — ceiling on the number of distinct traces
  buffered pending root-close. When a NEW trace that will REMAIN pending
  would exceed the ceiling, the **oldest buffered trace is evicted**
  (drop-oldest / insertion-order FIFO) and counted at
  ``dropped_trace_count``. This directly bounds the pathological case (a
  producer that opens 10^6 roots without closing them): the stale
  never-closing traces are the oldest, so they are shed first to make room.
  A new trace whose FIRST observed span is already its root-close
  materializes + frees its slot in the same ``on_end`` (no steady-state
  buffer pressure), so it does NOT trigger eviction.
- ``max_spans_per_trace`` — ceiling on the non-always-sampled spans
  buffered for a single trace. Overflow **non-root** spans are dropped and
  counted at ``dropped_span_count``; the root-close span ALWAYS processes
  (so the trace materializes and frees its slot rather than leaking).

Both default to ``None`` (unbounded — preserves the v1.27 MVP behavior for
direct construction; the production materializer always passes the
``CollectorConfig`` ceilings, so production is bounded by default).

**Eviction fidelity tradeoff (documented choice).** Drop-oldest may evict
a *keep-flagged* trace (one whose §10.2 classification trigger fired)
under buffer pressure. This is an accepted, bounded loss: the trigger span
itself is in the §9.2 always-sampled set and so was **forwarded
immediately** at ``on_end`` (it bypasses the buffer) — the failure
*signal* survives eviction; only the buffered tree-*context* (sibling
spans the sampler recorded) is shed. This is consistent with the
processor's "trust-sampler-on-base-rate, best-effort preservation"
posture. A keep-flag-preferential eviction (evict non-keep traces first)
is a documented future refinement; drop-oldest is chosen for O(1)
eviction and because the failure signal is already preserved. Alternative
considered: drop-NEW (reject the incoming trace) — rejected because it
lets stale never-closing traces hog the buffer indefinitely, the opposite
of the pathology the bound exists to contain.

**Event-shaped §9.2 members (OD spec v1.38 §9.2.1 — `B-133`).** Three §9.2
members are emitted as span **EVENTS** on a wrapper span rather than as
spans of their own: ``fallback.triggered`` and ``fallback.exhausted``
(``harness-runtime/.../lifecycle/retry_breaker_fallback.py``) and
``breaker.tripped`` (``harness_od.harness_breaker_schema``). Resolving the
§9.2 floor against ``span.name`` alone therefore never sees them, and the
carrier span — ``harness.runtime.retry_breaker_fallback``, which is in
neither §9.2 nor §10.2 — buffers and is DROPPED at root close, taking the
always-sampled event with it. That was confirmed empirically (not inferred)
by the `B-133` positive control before this arm was written: a real
exhausted dispatch through the real ``HarnessCompositeSampler`` + this
processor exported ZERO spans for all three members.

``_carries_always_sampled_event`` closes the TAIL half **for carriers the
head ADMITTED**: after the span-name check fails, the span's EVENT names are
resolved against the same ``is_always_sampled`` SSOT and a match forwards
immediately. Of the carriers that reach ``on_end`` this delivers 100% (the
`B-133` measurement: 420/420 and 837/837).

**What it does NOT do, stated because the coverage claim would be false.**
The HEAD half cannot be closed at this venue — a span's events do not exist
at span creation, so ``HarnessCompositeSampler.should_sample`` has nothing
to inspect — and it stays a **declared bound** (OD spec v1.38 §9.2.1 term
4). The bound is neither vacuous nor confined to the dev cell. Production
resolves the head sampler from the §10.3 envelope **unconditionally in both
§9.1 modes** (``tracer_provider.py`` binds
``build_default_sampler(base_rate=PER_CELL_BASE_RATE_ENVELOPE[cell]
.default_rate)`` and says in the same breath that *"the current default
sampler ignores the mode"*), so a ``TAIL_BASED_PROD`` cell at base-rate 0.1
drops ~90% of event carriers **before this processor exists to classify
them** — measured 10.4% reaching the tail at ``team-binding ×
self-hosted-server`` and 20.9% at ``multi-tenant-compliance ×
managed-cloud``, over 4,000 carriers each. The bound reaches **five of the
eight** ACTIVE cells (every cell whose head base-rate is < 1.0).

**The bound is SHAPE-specific, and that asymmetry is why `B-133` exists.**
At the SAME cell and base rate, a §9.2 member realized as a ROOT SPAN NAME
reaches the tail at 100% and exports at 100% (measured 4,000/4,000 for
``sandbox.violation`` at base-rate 0.1), because the head sampler resolves
``is_always_sampled`` against the span name. Name-shaped members are
delivered everywhere; event-shaped members are delivered at the cell's base
rate.

Making the head unconditionally admitting in ``TAIL_BASED_PROD`` mode (and
moving the §10.3 ratio into this processor) would close it — but that is an
architecture change spanning every class the tail preserves, including the
non-root §10.2 triggers measured at ~9% preservation at base-rate 0.1. It is
registered as **`B-137`** and is NOT undertaken here.

**Spec authority.** OD spec v1.2 §C-OD-09 §9.1 (per-deployment-surface
sampling mode) + §9.2 (always-sampled exception set) + §9.3 (sampling-
discipline invariants + implementer-discretion clause on tail-based
algorithm) + §C-OD-10 §10.2 (3 classification triggers) + OD spec v1.38
§9.2.1 (the event-aware tail arm + the declared head bound).

Authority anchors: `harness-od/src/harness_od/base_rate_set_and_envelope.py`
canonical `TAIL_KEEP_RULES` declaration site;
`harness-od/src/harness_od/tail_keep_classification.py` per-span trigger
predicate; `harness-od/src/harness_od/sampling_mode.py` always-sampled
set + `is_always_sampled` decomposed-prefix lookup.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_classification import (
    SUBAGENT_RESULT_STATUS_ATTR,
    SUBAGENT_RESULT_STATUS_FAILED_VALUE,
    SUBAGENT_SPAN_NAME,
    is_classification_trigger,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from opentelemetry.sdk.trace import Event

__all__ = [
    "TailKeepSpanProcessor",
]


def _carries_always_sampled_event(
    span: ReadableSpan, *, events: Sequence[Event] | None = None
) -> bool:
    """Return True iff any of `span`'s EVENT names is a §9.2 always-sampled member.

    The `B-133` event-aware companion to the `span.name` check. Resolves the
    SAME `is_always_sampled` SSOT the name arm uses, so the §9.2 roster has
    exactly one authority and a roster edit reaches both arms at once; event
    attributes are passed through so the §9.2 conditional-by-attribute rows
    keep their conservative-absent posture here too.

    **Reached when the NAME arm did not forward** — which is *usually* because
    the name is not a §9.2 member, but NOT always: a non-root SUCCEEDED
    `subagent.span` is deliberately held back from the name arm by the §9.2
    root-conditional gate, so this helper does run on a span whose own NAME is
    always-sampled. That is contracted rather than incidental — OD spec v1.38
    §9.2.1 term 1 states the event resolution is independent of the carrier's
    own §9.2 status, including its root-conditional membership, because an
    event's class is the event's and not the span's.

    **`events` — an OPTIONAL pre-read snapshot (register row `B-123`,
    out-of-family Codex [P2]).** `span.events` is a PROPERTY, not a field:
    OTel's `ReadableSpan.events` returns `tuple(event for event in
    self._events)` over a `BoundedList` whose `__iter__` takes a lock and
    copies the deque — one lock acquisition, one deque copy and one tuple
    build **per access**, even when the result is empty. `TailKeepSpanProcessor.
    on_end` calls this function AND (on some paths) `is_classification_trigger`
    against the SAME span in the SAME `on_end` invocation; without a shared
    snapshot each function would read the property independently, paying the
    cost TWICE per span for every ordinary (non-name-matched) span, including
    zero-event ones. `on_end` reads `span.events` exactly ONCE and passes the
    resulting tuple to both call sites via this parameter. `events=None` (the
    default) means "read it yourself" — every OTHER caller, and every
    pre-existing test, is unaffected; behaviour is byte-identical to a fresh
    `span.events` read. When a snapshot IS supplied, this function performs
    ZERO reads of the property.

    Once a snapshot is in hand (supplied or self-read), the emptiness guard is
    a plain truthiness test; when events are present the scan early-exits on
    the first match, and each step is one frozenset lookup plus a two-prefix
    `startswith` scan. The worst case is bounded by the OTel SDK's per-span
    event limit (default 128) — the same bound the SDK already accepts when it
    serializes those events for export.
    """
    resolved_events = span.events if events is None else events
    if not resolved_events:
        return False
    return any(is_always_sampled(event.name, event.attributes) for event in resolved_events)


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

    def __init__(
        self,
        *,
        downstream: SpanProcessor,
        max_buffered_traces: int | None = None,
        max_spans_per_trace: int | None = None,
    ) -> None:
        self._downstream: SpanProcessor = downstream
        # `B-163` — OTel calls `SpanProcessor.on_end` from whichever thread ends the span,
        # so every mutation of `_buffer` / `_keep` / the counters must be serialized. An
        # RLock (not a Lock) because `_evict_oldest_trace` is called from inside the
        # `_publish_keep_and_maybe_detach` / buffering critical sections, which already hold it.
        #
        # SCOPE DISCIPLINE: the lock guards the per-trace dict work ONLY. It is NEVER held
        # across `self._downstream.on_end(...)` — a slow exporter would otherwise serialize
        # every span in the process. `_publish_keep_and_maybe_detach` therefore detaches the
        # bucket under the lock and RETURNS it, so the caller forwards outside.
        self._state_lock = threading.RLock()
        # `B-164` — batches detached under `_state_lock` are forwarded OUTSIDE it (so a slow
        # exporter cannot serialize every span). That leaves a window where spans have left
        # `_buffer` but have not yet reached `downstream`, and a concurrent `force_flush()`
        # would see an empty buffer and return — defeating its own documented purpose,
        # "flush any still-buffered traces … to avoid silent loss on shutdown". These two
        # track batches in that window so `force_flush` can wait for them.
        # The condition shares `_state_lock`, so a batch is registered as in-flight in the
        # SAME critical section that detaches it. With two separate locks there was a gap:
        # `_publish_keep_and_maybe_detach` popped the batch, released, and only then did the
        # forwarder increment — a `force_flush` landing in between saw an empty buffer AND
        # zero in-flight, and returned while the spans were in the air (out-of-family Codex).
        self._inflight_batches = 0
        # `B-164` round 5 — a span whose `on_end` has STARTED but has not yet taken
        # `_state_lock` is work `force_flush` must also wait for: it can register a batch
        # AFTER the in-flight wait has already observed zero, landing during the downstream
        # flush. Counting entry/exit of `on_end` covers that window; the batch counter alone
        # cannot, because the batch does not exist yet.
        self._active_on_end = 0
        self._inflight_cv = threading.Condition(self._state_lock)
        # Per-trace_id buffer of non-always-sampled spans pending root-close
        # keep decision. Keyed by the int form of OTel trace_id. Python dict
        # insertion order makes `next(iter(...))` the oldest trace (FIFO
        # drop-oldest eviction under `max_buffered_traces` pressure).
        self._buffer: dict[int, list[ReadableSpan]] = {}
        # Per-trace_id keep flag — True iff any span in the trace carried a
        # §10.2 classification trigger. OR-merged at on_end.
        self._keep: dict[int, bool] = {}
        # OD spec v1.28 §9.3 operator-tunable bounded-buffer ceilings. None =
        # unbounded (v1.27 MVP behavior); the production materializer passes
        # the `CollectorConfig` ceilings so production is bounded by default.
        self._max_buffered_traces: int | None = max_buffered_traces
        self._max_spans_per_trace: int | None = max_spans_per_trace
        # Drop counters (observability + test introspection).
        self._dropped_trace_count: int = 0
        self._dropped_span_count: int = 0

    @property
    def downstream(self) -> SpanProcessor:
        """The wrapped downstream processor (test introspection)."""
        return self._downstream

    @property
    def buffered_trace_count(self) -> int:
        """Number of traces currently buffered (test introspection)."""
        return len(self._buffer)

    @property
    def dropped_trace_count(self) -> int:
        """Traces evicted (drop-oldest) under the `max_buffered_traces` ceiling."""
        return self._dropped_trace_count

    @property
    def dropped_span_count(self) -> int:
        """Non-root spans dropped under the `max_spans_per_trace` ceiling."""
        return self._dropped_span_count

    def on_start(
        self,
        span: Span,
        parent_context: Context | None = None,
    ) -> None:
        """Forward to downstream; no buffering at start (decisions are at end)."""
        self._downstream.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan) -> None:
        with self._inflight_cv:
            self._active_on_end += 1
        try:
            self._on_end_inner(span)
        finally:
            with self._inflight_cv:
                self._active_on_end -= 1
                self._inflight_cv.notify_all()

    def _on_end_inner(self, span: ReadableSpan) -> None:
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
        #
        # B-TAIL-CONDITIONAL-SAMPLING: pass `span.attributes` so the §9.2
        # ATTRIBUTE-CONDITIONAL rows (`files.operation` at non-mutation `kind`,
        # `memory.operation` at non-mutation `kind`, `validator.fail.*` at
        # `permanence=transient`) resolve to NOT-always-sampled at the TAIL and
        # buffer for the §10.2 tail-keep decision — rather than force-forwarding
        # unconditionally. This is the production enforcement point: producers set
        # `files.operation.kind` / `memory.operation.kind` / `validator.fail.permanence`
        # DURING the span, so at `on_end` (here) the discriminating attribute is
        # finalized, whereas at the head `should_sample` (span start) it is absent →
        # conservative-always-sample (the B7-landed head half). Conservative-absent is
        # preserved by construction: a missing attribute still returns always-sample,
        # so this only NARROWS behavior for present-and-non-mutation/transient spans
        # (never under-samples the §9.3 inviolable floor).
        #
        # B-TAIL also enforces the §9.2 `subagent.span (root)` ROOT-conditional row at
        # the tail: only the ROOT `subagent.span` is always-sampled; a non-root (nested)
        # `subagent.span` → §10.1 base-rate (buffer). The head enforces this structurally
        # via `ParentBased` (the inner sampler is consulted ONLY for root spans), but the
        # tail has no `ParentBased` wrapper, so it gates here with a parent-check (advisor:
        # a processor parent-check, NOT an SSOT `is_root` param — it is the one
        # root-conditional row, and root-ness is structural, not a name/attribute).
        #
        # EXCEPTION — a FAILED `subagent.span` is force-forwarded (eviction-safe) regardless
        # of depth (out-of-family Codex round 2): §14.3's tail-keep-on-failure decision is
        # determined by the span's OWN `result_status`, KNOWN at on_end, so it needs no
        # root-close buffering. Buffering it would expose the failure SIGNAL to §9.3
        # eviction/overflow — the `_evict_oldest_trace` fidelity tradeoff explicitly assumes
        # keep-TRIGGER spans are always-sampled/immediate (so eviction only sheds buffered
        # siblings, never the trigger itself); a buffered failure-trigger would be silently
        # lost under buffer pressure. So only a SUCCEEDED non-root `subagent.span` buffers.
        _failed_subagent = (
            span.name == SUBAGENT_SPAN_NAME
            and (span.attributes or {}).get(SUBAGENT_RESULT_STATUS_ATTR)
            == SUBAGENT_RESULT_STATUS_FAILED_VALUE
        )
        _buffer_nonroot_subagent = (
            span.name == SUBAGENT_SPAN_NAME and span.parent is not None and not _failed_subagent
        )
        if not _buffer_nonroot_subagent and is_always_sampled(span.name, span.attributes):
            # Mark the trace keep-flag if the always-sampled span is a classification
            # trigger (sandbox.violation + breaker.tripped are both in §9.2 AND in §10.2)
            # so tree-siblings buffered under the same trace get preserved at root close.
            #
            # `B-163` round 3: the state transition runs BEFORE `downstream.on_end(span)`,
            # not after. Forwarding does not depend on the keep flag, and a SLOW downstream
            # otherwise widens the publication window arbitrarily — long enough for a
            # concurrent root close to detach the trace with `keep=False`, dropping the
            # buffered siblings and leaving a stale `_keep` entry. Unlike the ordering
            # residual recorded on B-163, this window opens for a WELL-FORMED trace, so it
            # is closed here rather than documented.
            ctx = span.get_span_context()
            assert ctx is not None  # a span reaching on_end always has a context
            _trigger = is_classification_trigger(span)
            # `B-136` REPAIR — mirror OD spec v1.38 §9.2.1 term 5 (already normative for
            # the event arm below) onto this name arm. Before this, the arm returned
            # UNCONDITIONALLY, so an always-sampled ROOT forwarded itself and left its
            # buffered siblings pending until `force_flush`, holding a
            # `max_buffered_traces` slot for the process lifetime.
            #
            # That broke v1.28 §1.1's own containment model, which reasons that "a new
            # trace whose first observed span is already its root-close materializes +
            # frees its slot in the same `on_end` (no steady-state pressure), so it does
            # NOT evict" — an always-sampled-root trace root-closed but behaved like a
            # never-closing one for eviction purposes, displacing live traces.
            #
            # CONSEQUENCE, stated rather than buried: siblings of an always-sampled root
            # that carried no §10.2 trigger are now DROPPED at root close instead of
            # surviving to `force_flush` keep-all. That keep-all was never a guarantee —
            # measured, it degrades to eviction under buffer pressure (97 of 100 traces
            # shed at a cap of 3) — and dropping here is exactly what an ORDINARY root
            # already does. The forwarded always-sampled span itself is NOT in the buffer,
            # so the §9.2 floor and the §10.2 failure signal are both unaffected.
            _pending = self._publish_keep_and_maybe_detach(
                ctx.trace_id, is_trigger=_trigger, is_root_close=span.parent is None
            )
            # `_pending` is ALREADY registered in flight by the detach above, so the
            # forwarding of `span` must not be able to skip the release. If
            # `downstream.on_end(span)` raises, the count would otherwise stay positive
            # forever and every later `force_flush` would burn its whole budget.
            try:
                self._downstream.on_end(span)
            finally:
                self._forward_detached(_pending)
            return

        # `B-133` EVENT-AWARE ARM (OD spec v1.38 §9.2.1, U-OD-59). Three §9.2
        # members (`fallback.triggered` / `breaker.tripped` / `fallback.exhausted`)
        # ride as span EVENTS on a carrier span that is in neither §9.2 nor
        # §10.2, so the name check above cannot see them and the carrier is
        # dropped at root close with the always-sampled event inside it. Reached
        # only after the name check failed, so an always-sampled span never pays
        # for the scan.
        #
        # `B-123` single-read discipline (out-of-family Codex [P2]): `span.events`
        # is read ONCE here — for every span reaching this point, whether or not
        # it carries an always-sampled event — and the SAME snapshot is threaded
        # into `_carries_always_sampled_event` below AND into whichever
        # `is_classification_trigger` call site this span reaches (this arm's, or
        # the ordinary buffer path's further down). Before this read was shared,
        # a span falling through to the ordinary path paid the lock-acquire +
        # deque-copy TWICE per `on_end` call — once here, once inside
        # `is_classification_trigger`'s own self-read — for every ordinary span,
        # including zero-event ones.
        events = span.events
        if _carries_always_sampled_event(span, events=events):
            ctx = span.get_span_context()
            assert ctx is not None  # a span reaching on_end always has a context
            # Mirror of the name arm's trigger-flag step: an event-carrying span
            # that is ALSO a §10.2 classification trigger must still preserve its
            # buffered tree-siblings. `is_classification_trigger` now ALSO scans
            # `span.events` for the two §10.2 event-shaped trigger names (register
            # row `B-123`, OD spec v1.39 §9.2.1 term 3 — CLOSED), so an
            # event-carried `breaker.tripped` sets the flag here too, preserving
            # the trip's sibling tree at root close subject to the §9.2/§10.2
            # head-admission bound `B-137` measured (the arm delivers only for
            # carriers the head sampler admitted).
            _trigger = is_classification_trigger(span, events=events)
            # The name arm returns unconditionally, so an always-sampled ROOT
            # leaves its trace's buffered siblings pending until `force_flush`
            # (pre-existing; observed at the `B-133` probe and registered as
            # `B-136`). This arm must not extend that to the dispatch path,
            # where the carrier span IS routinely the root close: materialize
            # the trace decision so the siblings resolve and the trace frees its
            # `max_buffered_traces` slot. The forwarded span is NOT in the
            # buffer, so the decision below concerns only its siblings.
            # `B-163` round 3 — same reordering as the name arm: transition first, then
            # forward, so a slow downstream cannot widen the publication window.
            _pending = self._publish_keep_and_maybe_detach(
                ctx.trace_id, is_trigger=_trigger, is_root_close=span.parent is None
            )
            # `_pending` is ALREADY registered in flight by the detach above, so the
            # forwarding of `span` must not be able to skip the release. If
            # `downstream.on_end(span)` raises, the count would otherwise stay positive
            # forever and every later `force_flush` would burn its whole budget.
            try:
                self._downstream.on_end(span)
            finally:
                self._forward_detached(_pending)
            return

        ctx = span.get_span_context()
        assert ctx is not None  # a span reaching on_end always has a context
        trace_id = ctx.trace_id
        is_root_close = span.parent is None

        # OD spec v1.28 §9.3 max-buffered-traces ceiling: a NEW trace that will
        # REMAIN pending evicts the oldest buffered trace (drop-oldest FIFO).
        # Gate on `not is_root_close`: a root-close-first trace materializes +
        # frees its slot in this same on_end (no steady-state buffer pressure),
        # so it must NOT shed an existing pending trace's context.
        # `B-163` — the eviction test, the bucket insert and the append below are ONE
        # critical section. Splitting them is precisely the losing interleaving: a child
        # could `setdefault` an empty bucket here and append to it after a concurrent
        # root-close `pop` had already detached it, losing the span entirely.
        with self._state_lock:
            if (
                not is_root_close
                and trace_id not in self._buffer
                and self._max_buffered_traces is not None
                and len(self._buffer) >= self._max_buffered_traces
            ):
                self._evict_oldest_trace()

            bucket = self._buffer.setdefault(trace_id, [])
            # OD spec v1.28 §9.3 max-spans-per-trace ceiling: drop overflow
            # non-root spans (the root-close span always processes below so the
            # trace materializes and frees its slot rather than leaking).
            if (
                not is_root_close
                and self._max_spans_per_trace is not None
                and len(bucket) >= self._max_spans_per_trace
            ):
                self._dropped_span_count += 1
            else:
                bucket.append(span)

        _trigger = is_classification_trigger(span, events=events)

        # Root close detection: parent SpanContext is None means this span
        # has no parent in the recorded trace (it is the local-root). At
        # span-end, OTel `ReadableSpan.parent` is `None` for the root.
        self._forward_detached(
            self._publish_keep_and_maybe_detach(
                trace_id, is_trigger=_trigger, is_root_close=is_root_close
            )
        )

    def _forward_detached(self, spans: list[ReadableSpan]) -> None:
        """Forward a detached batch downstream, counted as in-flight (`B-164`).

        The batch has already left `_buffer`, so `force_flush` can no longer see it there.
        Registering it here — and only clearing in a `finally` — means a concurrent
        `force_flush` waits for delivery instead of returning while spans are in the air.
        `downstream.on_end` is still called with NO processor lock held.
        """
        if not spans:
            return
        try:
            for span in spans:
                self._downstream.on_end(span)
        finally:
            with self._inflight_cv:
                self._inflight_batches -= 1
                self._inflight_cv.notify_all()

    def _publish_keep_and_maybe_detach(
        self, trace_id: int, *, is_trigger: bool, is_root_close: bool
    ) -> list[ReadableSpan]:
        """Publish the keep flag and, at root close, detach the trace — ATOMICALLY.

        `B-163` round 2: guarding each mutation separately was not enough. With the keep
        write and the root materialization in DIFFERENT critical sections, a §10.2 child
        trigger could evaluate as a trigger, lose the lock to its root's `on_end` (which
        popped `_buffer`/`_keep` and dropped the siblings with `keep=False`), and only then
        write `_keep[trace_id] = True` — leaving a stale entry nothing would ever pop.
        Publishing and detaching in ONE critical section removes both the dropped-context
        window and the stale-keep leak.

        Returns the spans the caller must forward. Forwarding happens OUTSIDE the lock —
        holding it across `downstream.on_end` would serialize a slow exporter.
        """
        with self._state_lock:
            if is_trigger:
                self._keep[trace_id] = True
            if not is_root_close:
                return []
            buffered = self._buffer.pop(trace_id, [])
            keep = self._keep.pop(trace_id, False)
            released = buffered if keep else []
            if released:
                # Register the batch as in-flight WHILE still holding the lock that guards
                # `_buffer`, so no `force_flush` can observe "buffer empty AND nothing in
                # flight" for a batch that has been detached but not yet forwarded.
                self._inflight_batches += 1
        return released

    def _evict_oldest_trace(self) -> None:
        """Drop the oldest buffered trace (FIFO) under the max-traces ceiling.

        Python dict preserves insertion order, so `next(iter(self._buffer))`
        is the oldest-inserted trace_id. Its buffered spans are dropped
        (memory freed) and the trace is counted at `dropped_trace_count`. See
        the module docstring "Eviction fidelity tradeoff" for the rationale
        (drop-oldest may shed a keep-flagged trace's buffered context, but its
        always-sampled trigger span was already forwarded immediately).
        """
        oldest_trace_id = next(iter(self._buffer))
        self._buffer.pop(oldest_trace_id, None)
        self._keep.pop(oldest_trace_id, None)
        self._dropped_trace_count += 1

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        """Flush any still-buffered traces (keep-all) + delegate to downstream.

        At force-flush, accumulated traces (those never having materialized
        a root-close span) are forwarded to `downstream` as keep-all to
        avoid silent loss on shutdown. Then delegates to
        `downstream.force_flush(timeout_millis)`.
        """
        # Drain the buffer — keep-all on shutdown to avoid silent loss.
        #
        # `B-164` — this is a DRAIN-UNTIL-STABLE loop, not a single pass. Three distinct
        # windows made the single pass unsound, each found by out-of-family review:
        #   (i)   a batch detached but not yet forwarded (`_inflight_batches`),
        #   (ii)  an `on_end` that has started but not yet taken the lock (`_active_on_end`)
        #         — at that moment no batch exists to register, and
        #   (iii) such a call BUFFERING after the drain has already run, which leaves the
        #         span in `_buffer` with both counters back at zero.
        # Waiting on the counters alone fixes (i) and (ii) but not (iii); re-draining after
        # they settle, and repeating until a drain finds nothing new, covers all three.
        deadline = time.monotonic() + (timeout_millis / 1000.0)
        drained_in_time = True

        while True:
            with self._state_lock:
                drained = [span for spans in self._buffer.values() for span in spans]
                self._buffer.clear()
                self._keep.clear()
                if drained:
                    # Same registration rule as `_publish_keep_and_maybe_detach`: count the
                    # batch while still holding the lock, since `_forward_detached` only
                    # decrements.
                    self._inflight_batches += 1
            self._forward_detached(drained)

            # Let in-progress work settle: batches in the air, and `on_end` calls that have
            # entered but not yet reached the buffer. Bounded by the caller's own budget —
            # on expiry we still delegate, so a wedged exporter cannot make `force_flush`
            # hang forever, but we report failure rather than a false success.
            with self._inflight_cv:
                while self._inflight_batches > 0 or self._active_on_end > 0:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not self._inflight_cv.wait(timeout=remaining):
                        drained_in_time = self._inflight_batches == 0 and self._active_on_end == 0
                        break
                # Anything that arrived in `_buffer` while we waited needs another pass.
                more_pending = bool(self._buffer)

            if not more_pending or not drained_in_time or time.monotonic() >= deadline:
                if more_pending:
                    drained_in_time = False
                break

        remaining_millis = max(0.0, deadline - time.monotonic()) * 1000.0
        downstream_ok = self._downstream.force_flush(timeout_millis=int(remaining_millis))
        return downstream_ok and drained_in_time

    def shutdown(self) -> None:
        """Flush + delegate to downstream.shutdown()."""
        self.force_flush()
        self._downstream.shutdown()

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
   - If the span's trace has **already materialized** (a late arrival — see
     below) → forward it immediately and buffer nothing.

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

**Late arrivals — spans that end after their own root (`B-164(b)`).** Root
close is the materialization point: the keep decision is published, the
bucket and the keep flag are popped, and nothing will ever pop them again.
A span of that trace can still arrive afterwards, and production really does
produce them — ``harness_cp.workflow_driver._run_fanout_to_completion``
abandons its ``ThreadPoolExecutor`` with ``shutdown(wait=False)`` on the
§25.11 barrier deadline (or any branch failure), so an orphaned thread keeps
running with the root's context copied by ``asyncio.to_thread`` and closes
its child span after the root's ``with`` block has unwound. Witnessed by
execution at ``harness-runtime/tests/test_b164b_fanout_orphaned_child_span_repro.py``.

Buffering such a span was the defect: ``setdefault`` re-created a bucket that
no root close would ever detach, so the span was stranded until
``force_flush`` — and, being the OLDEST entry, it was the FIRST evicted under
the ``max_buffered_traces`` ceiling, i.e. a permanent loss rather than a
delay. It is now **forwarded immediately and never buffered**. Keep-all is
the posture this processor already takes everywhere a tail decision is
unavailable to it (``force_flush`` drains keep-all "to avoid silent loss");
a late arrival is exactly that case, one span at a time.

Recognising a late arrival needs a memory of which traces have materialized,
and that memory must be bounded — an unbounded set would be a worse leak than
the one being closed. The orphan can arrive in TWO orderings, and out-of-family
review produced a reproduction for each in turn, so the retention rule is the
composition of two:

1. **Live-pinned — the child was already OPEN when its root closed.** Spans are
   counted per trace at ``on_start`` and released at ``on_end``; while that
   count is non-zero the trace is retained unconditionally. Exact, with no
   window to age out of. The first revision instead used a fixed FIFO window of
   1,024 root closes, and review reproduced its boundary exactly: 1,023
   intervening roots forwarded the still-open child, 1,024 aged it out onto the
   buffer path where the ceiling evicted it — the repair reinstating its own
   defect.
2. **History-retained — the child had not STARTED yet when its root closed.**
   The abandoned worker holds a copied context, so it can open its span after
   the root has gone. At that instant the trace has no live spans at all, so
   rule 1 has nothing to pin and only a memory of the past decision can catch
   it. The second revision deleted the entry the moment liveness hit zero, and
   review reproduced that too (``buffered_trace_count == 1``, child never
   forwarded).

So the entry is kept while live AND for a bounded history afterwards
(``_LIVENESS_TRACKING_CEILING`` materializations), and FIFO eviction SKIPS
live-pinned entries so the bounded rule can never expire the exact one.

**The residual, stated exactly rather than optimistically** (the first revision
claimed "a delay, not a loss" and that was false): a child that has not yet
started when more than ``_LIVENESS_TRACKING_CEILING`` unrelated traces
materialize after its root is no longer recognised, and reverts to the pre-fix
behaviour — with ``max_buffered_traces`` set, which production always sets,
that is eviction and permanent loss, not a delay. This residual is inherent
rather than a missing case: distinguishing "a span of an old trace is about to
start" from "a new trace is starting" requires unbounded history.

**A late TRIGGER cannot rescue its trace, and that is a decided bound, not
an oversight.** If the late span is itself a §10.2 classification trigger,
the trace's keep decision was already taken WITHOUT it and its siblings are
already gone; retaining dropped spans on the chance a trigger arrives later
would reintroduce exactly the unbounded memory the drop exists to avoid. So
the trigger span itself is preserved (it is forwarded, immediately) and the
buffered tree-*context* is accepted as lost — the SAME tradeoff already
documented above for eviction, where "the failure *signal* survives …; only
the buffered tree-*context* … is shed". What is NOT accepted is the leak:
publishing ``_keep[trace_id]`` for an already-materialized trace left an
entry nothing would ever pop, and that write is now suppressed.

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

#: `B-164(b)` — how many materialized traces are remembered as HISTORY, for the ordering
#: liveness cannot cover: an orphaned worker holding a copied context that has not yet
#: opened its span when the root closes. At that instant the trace has no live spans, so
#: only a memory of the past decision can recognise the child when it finally arrives, and
#: a memory of the past is exactly the thing that has to be bounded.
#:
#: It is NOT the retention rule for a child that is ALREADY OPEN at root close — that one
#: is live-pinned and exempt from eviction here, so this ceiling can never age out the case
#: the first revision's fixed window got wrong. It also caps `_open_spans`, whose only
#: unbounded case is a span that starts and never ends ("still open" being
#: indistinguishable from "gone").
#:
#: **What is lost past it, stated exactly.** An aged-out trace reverts to the pre-fix
#: behaviour, and that is NOT merely a delay: with `max_buffered_traces` set — which
#: production always sets — the re-buffered span becomes the oldest bucket and is evicted
#: outright, and a late trigger recreates the stale `_keep` entry. 4096 is chosen to put
#: that far beyond the window it guards: an orphaned worker opens its span within one
#: branch dispatch of being abandoned, not after four thousand unrelated traces complete.
_LIVENESS_TRACKING_CEILING = 4096


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
        # `B-164` round 5 — a span whose `on_end` has STARTED but has not yet taken
        # `_state_lock` is work `force_flush` must also wait for: it can register a batch
        # AFTER the in-flight wait has already observed zero, landing during the downstream
        # flush. Counting entry/exit of `on_end` covers that window; the batch counter alone
        # cannot, because the batch does not exist yet.
        # `B-164` round 7 — the entry counter needs its OWN lock. If it were guarded by
        # `_state_lock` (which `_inflight_cv` shares), a callback reaching `on_end` while
        # `force_flush` holds that lock would block BEFORE being counted; the flusher could
        # release, immediately reacquire for its zero check, see nothing and return — after
        # which the queued callback buffers an already-ended span. This lock is only ever
        # held for two integer operations, so it is never contended for long.
        self._entry_lock = threading.Lock()
        # `B-164` round 8 — entrants carry a monotonic sequence number so a flush waits only
        # for callbacks that were ALREADY IN FLIGHT at its own cutoff. Waiting on a bare
        # count would also include callbacks that started after the flush began, so under
        # sustained tracing the count never reaches zero and `force_flush` burns its whole
        # budget and reports failure even though everything present at invocation drained.
        self._entry_seq = 0
        self._active_entries: set[int] = set()
        # Detached batches carry the generation of the `on_end` that produced them, so a
        # flush waits only for batches from entrants at or below its own cutoff. A bare
        # count would let post-cutoff traffic consume the budget — the same spurious-failure
        # shape the entrant cutoff fixed, one level down (`B-164` round 9).
        self._inflight_batch_seqs: list[int] = []
        # The generation of the `on_end` running on THIS thread, so the detach path can tag
        # its batch without threading the id through every call site. `force_flush`'s own
        # drained batch is tagged 0, which is at or below every cutoff and so is always
        # waited for by the flush that produced it.
        self._current_entry = threading.local()
        self._inflight_cv = threading.Condition(self._state_lock)
        # Per-trace_id buffer of non-always-sampled spans pending root-close
        # keep decision. Keyed by the int form of OTel trace_id. Python dict
        # insertion order makes `next(iter(...))` the oldest trace (FIFO
        # drop-oldest eviction under `max_buffered_traces` pressure).
        self._buffer: dict[int, list[ReadableSpan]] = {}
        # Per-trace_id keep flag — True iff any span in the trace carried a
        # §10.2 classification trigger. OR-merged at on_end.
        self._keep: dict[int, bool] = {}
        # `B-164(b)` — trace_ids whose keep decision has already been PUBLISHED at root
        # close. Used as an ordered set (dict insertion order = FIFO, same idiom as
        # `_buffer`). Read and written only under `_state_lock`, and — critically — tested
        # in the SAME critical section that would otherwise buffer the span, so a concurrent
        # root close cannot land between the test and the append.
        self._materialized: dict[int, None] = {}
        # `B-164(b)` round 2 (out-of-family Codex, P1) — per-trace count of spans that have
        # STARTED and not yet ended. An entry is retained in `_materialized` exactly while
        # this count is non-zero, because that is exactly the condition under which a late
        # arrival is still possible: a span the processor has not yet seen at `on_end` has
        # already been seen at `on_start`.
        #
        # The first attempt expired `_materialized` on a fixed FIFO window of unrelated
        # root closes instead. Codex reproduced the boundary that makes that unsound — with
        # the orphaned child still open, 1,023 intervening roots forwarded it but 1,024
        # pushed it back onto the buffer path, where the `max_buffered_traces` ceiling
        # evicted it outright and a late trigger recreated the `_keep` leak. Liveness is not
        # a bigger window; it is the exact condition, so there is no boundary to cross.
        self._open_spans: dict[int, int] = {}
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
        """Count the span as live, then forward downstream (no buffering at start).

        `B-164(b)` — the count is what lets `on_end` know whether a root-closed trace may
        still receive a late arrival. Tracking is done HERE, before forwarding, because
        this is the only point at which the processor learns a span exists before it ends;
        the whole defect was about a span the processor could not otherwise anticipate.
        """
        # `Span.get_span_context()` is non-optional (unlike `ReadableSpan`'s, which is why
        # `_release_open_span` still guards), so this needs no None check.
        with self._state_lock:
            self._retain_open_span(span.get_span_context().trace_id)
        self._downstream.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan) -> None:
        with self._entry_lock:
            self._entry_seq += 1
            entry_id = self._entry_seq
            self._active_entries.add(entry_id)
        self._current_entry.value = entry_id
        try:
            self._on_end_inner(span)
        finally:
            # `B-164(b)` — released AFTER `_on_end_inner`, never before: the late-arrival
            # test inside it reads `_materialized`, and this span is precisely one of the
            # live spans keeping that entry alive. Releasing first could discard the entry
            # a concurrent sibling is about to consult.
            self._release_open_span(span)
            with self._entry_lock:
                self._active_entries.discard(entry_id)
            # Wake any flusher parked on the batch condition; the entry count it also
            # consults is read under `_entry_lock`, never this one.
            with self._inflight_cv:
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
        #
        # `B-164(b)` — the late-arrival test lives INSIDE this critical section rather than
        # ahead of it. Ahead of it, a root close landing between the test and the append
        # would put the span back in the stranded state the test exists to prevent — the
        # same interleaving `B-163` closed for the eviction/insert pair one line down.
        with self._state_lock:
            late_arrival = trace_id in self._materialized
            if late_arrival:
                # The keep decision for this trace is already published and unrepeatable, so
                # this span can neither join it nor be released by a future one. Forward it
                # (keep-all — the posture used wherever a tail decision is unavailable)
                # instead of re-creating a bucket nothing will ever pop. Registered in
                # flight here, under the lock, for the same reason a detached batch is.
                self._register_inflight()
            else:
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

        if late_arrival:
            self._forward_detached([span])
            return

        _trigger = is_classification_trigger(span, events=events)

        # Root close detection: parent SpanContext is None means this span
        # has no parent in the recorded trace (it is the local-root). At
        # span-end, OTel `ReadableSpan.parent` is `None` for the root.
        self._forward_detached(
            self._publish_keep_and_maybe_detach(
                trace_id, is_trigger=_trigger, is_root_close=is_root_close
            )
        )

    def _batches_pending(self, cutoff: int) -> bool:
        """True while a detached batch produced at or before `cutoff` is still forwarding."""
        return any(seq <= cutoff for seq in self._inflight_batch_seqs)

    def _entry_cutoff(self) -> int:
        """Snapshot the entry sequence — a flush waits only for entrants at or below it."""
        with self._entry_lock:
            return self._entry_seq

    def _entrants_pending(self, cutoff: int) -> bool:
        """True while an `on_end` that entered at or before `cutoff` is still running.

        Read under `_entry_lock` — deliberately NOT `_state_lock`, so a callback queued on
        the state lock is already registered here before a flusher can observe zero. The
        cutoff is what keeps a flush from waiting on traffic that arrived after it began.
        """
        with self._entry_lock:
            return any(entry_id <= cutoff for entry_id in self._active_entries)

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
                seq = getattr(self._current_entry, "value", 0)
                if seq in self._inflight_batch_seqs:
                    self._inflight_batch_seqs.remove(seq)
                elif self._inflight_batch_seqs:  # pragma: no cover - defensive
                    self._inflight_batch_seqs.pop()
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
            # `B-164(b)` — do NOT publish a keep flag for a trace that has already
            # materialized. The decision was taken without this trigger and cannot be
            # retaken, so the entry would be one nothing ever pops. The trigger span itself
            # is still preserved — it is forwarded by the always-sampled arm, or by the
            # late-arrival path — so the §10.2 failure SIGNAL survives; only the buffered
            # tree-context is accepted as lost, the same tradeoff eviction already makes.
            if is_trigger and trace_id not in self._materialized:
                self._keep[trace_id] = True
            if not is_root_close:
                return []
            buffered = self._buffer.pop(trace_id, [])
            keep = self._keep.pop(trace_id, False)
            self._remember_materialized(trace_id)
            released = buffered if keep else []
            if released:
                # Register the batch as in-flight WHILE still holding the lock that guards
                # `_buffer`, so no `force_flush` can observe "buffer empty AND nothing in
                # flight" for a batch that has been detached but not yet forwarded. Tagged
                # with this thread's entrant generation so a flush can tell whether the
                # batch predates its cutoff.
                self._register_inflight()
        return released

    def _register_inflight(self) -> None:
        """Tag a batch about to be forwarded with this thread's entrant generation.

        MUST be called holding `_state_lock` — that is what makes the registration and the
        removal-from-`_buffer` (or, for a `B-164(b)` late arrival, the decision not to enter
        it at all) a single critical section, so no `force_flush` can observe "buffer empty
        AND nothing in flight" for a span that is on its way to `downstream`. Every
        registration is paired with exactly one `_forward_detached` call, which clears it.
        """
        self._inflight_batch_seqs.append(getattr(self._current_entry, "value", 0))

    def _remember_materialized(self, trace_id: int) -> None:
        """Record that `trace_id` has published its keep decision (`B-164(b)`).

        Called under `_state_lock` from the root-close materialization. The entry is
        retained by TWO composed rules, because neither alone covers both orderings a
        late arrival can take (out-of-family Codex, two successive P1 findings):

        - **while the trace has live spans** — the orphaned child was ALREADY OPEN when
          its root closed. Exact, unbounded in time, no window to age out of.
        - **for a bounded history afterwards** — the orphaned worker had the root's
          context copied but had NOT YET opened its span when the root closed, so there
          was no liveness to pin anything. Only a memory of the past decision can catch
          that one, and a memory of the past must be bounded.

        Eviction is FIFO but SKIPS live-pinned entries, so the bounded half can never
        expire the exact half. Entries older than the ceiling are almost never live, so
        the scan below breaks on its first candidate in practice.
        """
        self._materialized[trace_id] = None
        while len(self._materialized) > _LIVENESS_TRACKING_CEILING:
            for candidate in self._materialized:
                if candidate not in self._open_spans:
                    del self._materialized[candidate]
                    break
            else:
                # Every entry is live-pinned. Shed the oldest anyway rather than let the
                # dictionary grow without limit — boundedness is the harder guarantee.
                del self._materialized[next(iter(self._materialized))]

    def _retain_open_span(self, trace_id: int) -> None:
        """Count one more started-and-not-yet-ended span for `trace_id` (`B-164(b)`).

        Called under `_state_lock` from `on_start`. Bounded by the same abandoned-span
        backstop: shedding the oldest count only costs the trace its liveness-keyed
        retention, after which it falls back to the FIFO ceiling — it can never make a
        count go negative, because `_release_open_span` ignores an absent entry.
        """
        self._open_spans[trace_id] = self._open_spans.get(trace_id, 0) + 1
        while len(self._open_spans) > _LIVENESS_TRACKING_CEILING:
            del self._open_spans[next(iter(self._open_spans))]

    def _release_open_span(self, span: ReadableSpan) -> None:
        """Drop one live span for its trace (`B-164(b)`).

        At zero the trace stops being live-PINNED in `_materialized`, but its entry is NOT
        deleted — deleting it was the second `B-164(b)` P1: a worker holding a copied
        context can open its span AFTER the root closed, at which point the trace has no
        live spans at all and an eagerly-deleted entry would send that child straight back
        onto the stranding path. The entry now ages out of the bounded history instead.

        An absent count is ignored rather than treated as zero, so a span whose `on_start`
        this processor never saw (registered on the provider mid-flight, or shed by the
        backstop) can never drive the count negative.
        """
        ctx = span.get_span_context()
        if ctx is None:  # pragma: no cover - a span reaching on_end always has a context
            return
        with self._state_lock:
            remaining = self._open_spans.get(ctx.trace_id)
            if remaining is None:
                return
            if remaining > 1:
                self._open_spans[ctx.trace_id] = remaining - 1
                return
            del self._open_spans[ctx.trace_id]

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
        #   (i)   a batch detached but not yet forwarded (`_inflight_batch_seqs`),
        #   (ii)  an `on_end` that has started but not yet taken the lock (tracked by
        #         `_active_entries`)
        #         — at that moment no batch exists to register, and
        #   (iii) such a call BUFFERING after the drain has already run, which leaves the
        #         span in `_buffer` with both counters back at zero.
        # Waiting on the counters alone fixes (i) and (ii) but not (iii); re-draining after
        # they settle, and repeating until a drain finds nothing new, covers all three.
        deadline = time.monotonic() + (timeout_millis / 1000.0)
        drained_in_time = True
        # Everything that had entered `on_end` by now must be waited for; later arrivals
        # must not be, or sustained tracing would make every flush time out.
        entry_cutoff = self._entry_cutoff()

        while True:
            with self._state_lock:
                drained = [span for spans in self._buffer.values() for span in spans]
                self._buffer.clear()
                self._keep.clear()
                if drained:
                    # Same registration rule as `_publish_keep_and_maybe_detach`. Tagged 0 —
                    # at or below every cutoff — so the flush always waits for its own batch.
                    self._current_entry.value = 0
                    self._inflight_batch_seqs.append(0)
            self._forward_detached(drained)

            # Let in-progress work settle: batches in the air, and `on_end` calls that have
            # entered but not yet reached the buffer. Bounded by the caller's own budget —
            # on expiry we still delegate, so a wedged exporter cannot make `force_flush`
            # hang forever, but we report failure rather than a false success.
            with self._inflight_cv:
                while self._batches_pending(entry_cutoff) or self._entrants_pending(entry_cutoff):
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not self._inflight_cv.wait(timeout=remaining):
                        drained_in_time = not self._batches_pending(
                            entry_cutoff
                        ) and not self._entrants_pending(entry_cutoff)
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

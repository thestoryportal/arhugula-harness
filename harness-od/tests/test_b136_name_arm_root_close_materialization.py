"""B-136 — the §9.2 name arm now materializes the trace decision at root close.

**What B-136 was.** `TailKeepSpanProcessor.on_end`'s §9.2 **name-matching** arm forwarded the
span downstream, optionally set the §10.2 keep flag, and **returned unconditionally** —
before the `is_root_close → _materialize_trace_decision(trace_id)` step further down the
method. When the always-sampled span was itself the trace's root close, the trace's buffered
siblings were never resolved: they sat in `self._buffer` holding a `max_buffered_traces`
slot until `force_flush` drained them keep-all.

The `B-133` **event** arm deliberately does *not* share that shape — OD spec v1.38 §9.2.1
**term 5** makes root-close materialization normative for it, and its in-line comment names
`B-136` explicitly as the case it must not extend. This module repairs the asymmetry by
mirroring term 5 onto the name arm.

**Why it is a defect and not merely bookkeeping.** The row's own step (2) asked exactly
that, on the premise that *"`force_flush` drains keep-all, so nothing is lost."* Measured,
that premise holds **only below the buffer ceiling**: with `max_buffered_traces=3` over 100
always-sampled-root traces, **97 are evicted** and their children never export at all
(`test_the_keep_all_at_drain_benefit_was_never_a_guarantee`). More decisively, the shape
contradicts **v1.28 §1.1's own containment model**, which reasons that *"a new trace whose
first observed span is already its root-close materializes + frees its slot in the same
`on_end` (no steady-state pressure), so it does NOT evict"* — an always-sampled-root trace
root-closed yet behaved like a never-closing one for eviction purposes, displacing live
traces.

**The consequence, stated rather than buried** (the row's step (4) requires witnessing BOTH
directions). Siblings of an always-sampled root are now resolved at root close instead of
at drain. Where the root — or any span in the trace — is a §10.2 classification trigger,
they are **kept**, and now export *earlier*. Where nothing in the trace triggered, they are
**dropped**, which is a real reduction against the previous accidental keep-all — and is
exactly what an **ordinary** root already did. The always-sampled span itself is forwarded
before the buffer is consulted, so the §9.2 floor and the §10.2 failure signal are
untouched either way.
"""

from __future__ import annotations

from typing import Any

from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace import TracerProvider

#: Always-sampled AND a §10.2 classification trigger.
_TRIGGER_ROOT = "sandbox.violation"
#: Always-sampled but NOT a §10.2 trigger — the population that loses its siblings.
_QUIET_ROOT = "hitl.gate.evaluated"


class _Downstream:
    """Records what the processor forwards."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        return None

    def on_end(self, span: Any) -> None:
        self.seen.append(span.name)

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True


def _one_trace(
    root: str, *, child: str = "ordinary.child", **bounds: int
) -> tuple[TailKeepSpanProcessor, _Downstream]:
    """Emit one `root` trace with a single `child`, through the REAL processor."""
    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream, **bounds)
    provider = TracerProvider()  # always-on head: isolate the TAIL behaviour
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b136")
    with tracer.start_as_current_span(root):
        with tracer.start_as_current_span(child):
            pass
    return tail, downstream


def test_the_premise_both_roots_are_always_sampled() -> None:
    """Ground the two fixtures before drawing any conclusion from them."""
    assert is_always_sampled(_TRIGGER_ROOT) is True
    assert is_always_sampled(_QUIET_ROOT) is True
    assert is_always_sampled("ordinary.root") is False, (
        "`ordinary.root` entered the §9.2 set — the control below is no longer a control"
    )


def test_an_always_sampled_root_now_frees_its_buffer_slot() -> None:
    """**Direction 1 — the repair.** The slot is released at root close, not at drain.

    Before B-136 this returned `1` for both always-sampled roots and `0` only for the
    ordinary control. Reverting the two-line materialization in the name arm turns this RED.
    """
    for root in (_TRIGGER_ROOT, _QUIET_ROOT, "ordinary.root"):
        tail, _ = _one_trace(root)
        assert tail.buffered_trace_count == 0, (
            f"trace rooted at `{root}` still holds a buffer slot after root close "
            f"({tail.buffered_trace_count}) — B-136 has regressed, and v1.28 §1.1's "
            "containment model (root-closes free their slot) does not hold"
        )


def test_a_triggered_trace_keeps_its_siblings_and_now_exports_them_earlier() -> None:
    """**Direction 2a** — where a §10.2 trigger fired, nothing is lost; it arrives sooner.

    `sandbox.violation` is both a §9.2 member and a §10.2 trigger, so the root sets the keep
    flag itself. Materializing at root close therefore FLUSHES the buffered child — the same
    spans as before the repair, at root close rather than at `force_flush`.
    """
    tail, downstream = _one_trace(_TRIGGER_ROOT)
    assert downstream.seen == [_TRIGGER_ROOT, "ordinary.child"], (
        f"expected the trigger root and its kept child; got {downstream.seen}"
    )
    assert tail.buffered_trace_count == 0


def test_a_quiet_always_sampled_root_now_drops_its_siblings() -> None:
    """**Direction 2b — the cost, witnessed rather than buried.**

    `hitl.gate.evaluated` is always-sampled but is NOT a §10.2 trigger, so nothing sets the
    keep flag. Its buffered child is now dropped at root close, where previously it survived
    to `force_flush` keep-all. This is a real reduction in exported spans for a real
    population, and the row registered B-136 rather than folding it into `B-133` precisely
    because of it.

    The comparison that justifies it: an ORDINARY root already drops its child under exactly
    the same no-trigger condition. The repair removes an inconsistency, it does not invent a
    new drop rule.
    """
    tail, downstream = _one_trace(_QUIET_ROOT)
    assert downstream.seen == [_QUIET_ROOT], (
        f"expected ONLY the always-sampled root to be forwarded; got {downstream.seen}"
    )
    tail.force_flush()
    assert "ordinary.child" not in downstream.seen, (
        "the quiet root's child survived to force_flush — the repair did not take effect"
    )

    # The ordinary-root control drops identically, which is the consistency argument.
    control_tail, control_downstream = _one_trace("ordinary.root")
    control_tail.force_flush()
    assert control_downstream.seen == [], (
        f"the ordinary-root control changed behaviour; got {control_downstream.seen}"
    )


def test_the_always_sampled_span_itself_is_never_at_risk() -> None:
    """The §9.2 floor and the §10.2 signal are untouched by the repair.

    The arm forwards the span *before* the buffer is consulted, so whatever happens to its
    siblings, the always-sampled span itself always leaves. If this ever failed, the repair
    would have moved a floor member into the buffered population — a far worse defect than
    the one B-136 describes.
    """
    for root in (_TRIGGER_ROOT, _QUIET_ROOT):
        _, downstream = _one_trace(root)
        assert downstream.seen[0] == root, (
            f"`{root}` was not forwarded first; got {downstream.seen} — a §9.2 member may "
            "now be buffered rather than always-sampled"
        )


def test_the_keep_all_at_drain_benefit_was_never_a_guarantee() -> None:
    """**Why step (2) resolves to "defect"** — the pre-repair benefit failed under pressure.

    The row's step (2) asked whether this is a defect at all, since *"`force_flush` drains
    keep-all, so nothing is lost."* That holds only while the buffer stays below its ceiling.
    `CollectorConfig` ships finite bounds (4096 each) and the buffer evicts **drop-oldest**,
    so a population of never-resolving always-sampled-root traces sheds its own oldest
    members — they never reach `force_flush` at all.

    This drives the REAL processor at a small ceiling to make the shape visible. After the
    repair no trace lingers, so nothing is evicted and the counter stays at zero — which is
    itself the point: the repair removes the population that was being shed.
    """
    tail, downstream = _one_trace(_QUIET_ROOT, max_buffered_traces=3, max_spans_per_trace=4096)
    assert tail.dropped_trace_count == 0, (
        "a single trace evicted something — the ceiling arithmetic changed"
    )

    # Post-repair steady state: 100 always-sampled-root traces at a ceiling of 3 leave
    # nothing buffered and evict nothing, because each resolves at its own root close.
    downstream = _Downstream()
    tail = TailKeepSpanProcessor(
        downstream=downstream, max_buffered_traces=3, max_spans_per_trace=4096
    )
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b136.pressure")
    for _ in range(100):
        with tracer.start_as_current_span(_QUIET_ROOT):
            with tracer.start_as_current_span("ordinary.child"):
                pass

    assert tail.buffered_trace_count == 0, (
        f"{tail.buffered_trace_count} trace(s) still buffered after 100 root closes — the "
        "never-resolving population B-136 describes is back"
    )
    assert tail.dropped_trace_count == 0, (
        f"{tail.dropped_trace_count} trace(s) evicted under a ceiling of 3 — before the "
        "repair this population displaced live traces; it should now be empty"
    )

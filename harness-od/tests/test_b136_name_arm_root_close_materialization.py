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

import ast
import pathlib
import threading
import time
from typing import Any

from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider

#: Always-sampled AND a §10.2 classification trigger.
_TRIGGER_ROOT = "sandbox.violation"
#: Always-sampled but NOT a §10.2 trigger — the population that loses its siblings.
_QUIET_ROOT = "hitl.gate.evaluated"
#: Repo root, for the src/-scoped invariant below.
_REPO = pathlib.Path(__file__).resolve().parents[2]


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


# ---------------------------------------------------------------------------
# B-163 — the per-trace state transition is atomic
# ---------------------------------------------------------------------------


def test_b163_a_concurrent_child_and_root_close_cannot_lose_a_span() -> None:
    """**B-163** — drive the exact losing interleaving, deterministically.

    OTel calls `SpanProcessor.on_end` from whichever thread ends the span, so the buffer
    mutations must be serialized. The losing order out-of-family Codex named:

    1. a child `on_end` runs `self._buffer.setdefault(trace_id, [])`, creating an empty
       bucket, and is descheduled **before** `bucket.append(span)`;
    2. a root `on_end` on another thread runs `_materialize_trace_decision`, whose first act
       is `self._buffer.pop(trace_id, [])` — it pops the **empty** bucket and forwards
       nothing;
    3. the child resumes and appends to a now-detached list.

    The span then reaches **neither** `downstream` **nor** `_buffer`, so not even
    `force_flush` can recover it — and when the root is a §10.2 trigger, the lost span is
    exactly the context the keep flag was meant to preserve.

    This is a **coordinated** witness, not a stress loop: the child thread is blocked inside
    the processor at the precise point above via a `setdefault` hook, so the test is
    deterministic. Removing the `RLock` makes it fail every run rather than occasionally.
    """
    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b163")

    child_is_inside = threading.Event()
    root_may_proceed = threading.Event()

    class _HookedBuffer(dict[int, list[Any]]):
        """Pauses the child between `setdefault` and its `append`."""

        def setdefault(self, key: Any, default: Any = None) -> Any:  # type: ignore[override]
            bucket = super().setdefault(key, default)
            if threading.current_thread().name == "b163-child":
                child_is_inside.set()
                root_may_proceed.wait(timeout=5.0)
            return bucket

    tail._buffer = _HookedBuffer(tail._buffer)

    # Both spans must be in ONE trace: create the root first, then the child under the
    # root's context explicitly (OTel context does NOT propagate across threads), so the
    # child really is a non-root span of the same trace_id.
    root_span = tracer.start_span(_TRIGGER_ROOT)
    child_span = tracer.start_span(
        "ordinary.child", context=otel_trace.set_span_in_context(root_span)
    )
    assert child_span.get_span_context().trace_id == root_span.get_span_context().trace_id, (
        "the fixture failed to place both spans in one trace — the race cannot occur"
    )

    child_thread = threading.Thread(target=child_span.end, name="b163-child")
    child_thread.start()
    assert child_is_inside.wait(timeout=5.0), "the child never reached the buffer insert"

    # With the lock the root BLOCKS here until the child's critical section completes;
    # without it the root pops the empty bucket and the child's append is lost.
    root_thread = threading.Thread(target=root_span.end, name="b163-root")
    root_thread.start()
    root_may_proceed.set()
    child_thread.join(timeout=5.0)
    root_thread.join(timeout=5.0)
    assert not child_thread.is_alive() and not root_thread.is_alive(), "a thread hung"

    assert "ordinary.child" in downstream.seen, (
        f"the concurrently-ended child was LOST — it reached neither downstream nor the "
        f"buffer. downstream={downstream.seen}, still buffered="
        f"{sum(len(v) for v in tail._buffer.values())}. B-163's lock has regressed."
    )


def test_b163_the_publish_and_detach_transition_is_indivisible() -> None:
    """**B-163 round 2** — keep-publication and root materialization are ONE transition.

    Guarding each mutation separately was not enough (out-of-family Codex, round 4): with
    the keep write and the root materialization in *different* critical sections, a thread
    could observe a **torn** state — `_keep` written against a trace whose buffer another
    thread had already popped, leaving a stale entry nothing would pop. They are now a
    single critical section in `_publish_keep_and_maybe_detach`.

    **What this does and does not close, stated precisely.** Mutual exclusion fixes *torn
    state*. It cannot fix *ordering*: if a root's `on_end` runs to completion before a
    child's `on_end` begins, the trace materializes before that child is accounted for, and
    no lock discipline inside `on_end` can change that. That ordering requires a **root to
    end before its own child**, which violates the span-nesting contract OTel and this
    processor's entire root-close design assume. The residual is recorded on B-163 rather
    than papered over.

    This asserts the part that IS guaranteed: for a well-formed trace, a trigger published
    concurrently with sibling buffering always preserves the siblings, and no `_keep` entry
    survives materialization.
    """
    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b163.trigger")

    # A well-formed trace: quiet root, one ordinary sibling, one §10.2 trigger child — the
    # root ends LAST, as the nesting contract requires.
    root_span = tracer.start_span(_QUIET_ROOT)
    parent_ctx = otel_trace.set_span_in_context(root_span)

    barrier = threading.Barrier(2, timeout=5.0)

    def _end_sibling() -> None:
        span = tracer.start_span("ordinary.child", context=parent_ctx)
        barrier.wait()
        span.end()

    def _end_trigger() -> None:
        span = tracer.start_span(_TRIGGER_ROOT, context=parent_ctx)
        barrier.wait()
        span.end()

    threads = [
        threading.Thread(target=_end_sibling, name="b163-sibling"),
        threading.Thread(target=_end_trigger, name="b163-trigger"),
    ]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=5.0)
    assert all(not th.is_alive() for th in threads), "a thread hung"

    root_span.end()

    assert "ordinary.child" in downstream.seen, (
        f"the buffered sibling was dropped despite a §10.2 trigger in the same trace; "
        f"downstream={downstream.seen} — the publish/detach transition is not indivisible"
    )
    assert not tail._keep, (
        f"a `_keep` entry survived materialization: {dict(tail._keep)} — nothing will pop "
        "it, so the map grows without bound across traces"
    )
    assert tail.buffered_trace_count == 0, "the trace did not resolve at root close"


def test_b163_a_slow_downstream_cannot_widen_the_keep_publication_window() -> None:
    """**B-163 round 3** — the state transition runs BEFORE the downstream forward.

    Out-of-family Codex round 5: publishing the keep flag *after* `downstream.on_end(span)`
    let a **slow exporter** widen the publication window arbitrarily. A non-root
    always-sampled trigger would sit inside the exporter while its root acquired the lock,
    detached the trace with `keep=False`, dropped the buffered siblings, and left the
    trigger to write a stale `_keep` entry afterwards.

    Unlike the ordering residual recorded on B-163 — which needs a root to end *before* its
    own child, a malformed trace — this window opens for a **well-formed** trace and is
    entirely an artifact of where the forward sat. Forwarding never depended on the keep
    flag, so the transition simply moved ahead of it.

    Driven deterministically with the exact shape Codex named: a buffered ordinary child, a
    `sandbox.violation` trigger **blocked inside downstream**, and a quiet always-sampled
    root closing concurrently.
    """
    trigger_in_downstream = threading.Event()
    root_done = threading.Event()

    class _SlowDownstream(_Downstream):
        def on_end(self, span: Any) -> None:
            if span.name == _TRIGGER_ROOT and threading.current_thread().name == "b163-slow":
                trigger_in_downstream.set()
                root_done.wait(timeout=5.0)  # the exporter is "slow"
            super().on_end(span)

    downstream = _SlowDownstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b163.slow")

    root_span = tracer.start_span(_QUIET_ROOT)
    parent_ctx = otel_trace.set_span_in_context(root_span)
    with tracer.start_as_current_span("ordinary.child", context=parent_ctx):
        pass  # buffered sibling
    trigger_span = tracer.start_span(_TRIGGER_ROOT, context=parent_ctx)

    slow_thread = threading.Thread(target=trigger_span.end, name="b163-slow")
    slow_thread.start()
    assert trigger_in_downstream.wait(timeout=5.0), "the trigger never reached downstream"

    # The root closes while the trigger is still stuck in the exporter. Because the keep
    # was published BEFORE that forward, the root must observe it.
    root_span.end()
    root_done.set()
    slow_thread.join(timeout=5.0)
    assert not slow_thread.is_alive(), "the slow thread hung"

    assert "ordinary.child" in downstream.seen, (
        f"the buffered sibling was dropped while the trigger sat in a slow downstream; "
        f"downstream={downstream.seen} — the keep publication is still behind the forward"
    )
    assert not tail._keep, (
        f"a stale `_keep` entry leaked: {dict(tail._keep)} — the trigger published after "
        "its trace had already materialized"
    )


# ---------------------------------------------------------------------------
# B-164 — force_flush waits for in-flight detached batches
# ---------------------------------------------------------------------------


def test_b164_force_flush_waits_for_an_inflight_detached_batch() -> None:
    """**B-164 (a)** — `force_flush` must not return while spans are still in the air.

    Batches detached under `_state_lock` are forwarded **outside** it, deliberately: holding
    the lock across `downstream.on_end` would serialize a slow exporter behind every span.
    That leaves a window where spans have left `_buffer` but have not reached `downstream` —
    and a concurrent `force_flush()` would see an **empty buffer**, delegate, and return
    `True` while they were still being delivered. Shutdown then closes the exporter first.

    **Grounding for why this is a defect and not contemplated best-effort** (B-164's step
    (1)): the module's own contract says `force_flush` exists to *"flush any still-buffered
    traces (treat them as keep-all to avoid silent loss on shutdown)"*. Returning before
    delivery defeats exactly that stated purpose, so it is in scope rather than covered by
    the *"Drop semantics (false-but-bounded)"* posture — which is about traces that never
    root-close, not about spans already handed to the forwarder.

    Driven deterministically: a trigger root detaches a buffered sibling and blocks inside a
    slow downstream, while another thread calls `force_flush`.
    """
    sibling_in_downstream = threading.Event()
    release_downstream = threading.Event()
    order: list[str] = []

    class _SlowDownstream(_Downstream):
        delivered_before_flush_returned = False

        def on_end(self, span: Any) -> None:
            if span.name == "ordinary.child":
                sibling_in_downstream.set()
                release_downstream.wait(timeout=5.0)
            super().on_end(span)
            if span.name == "ordinary.child":
                # Set only if the processor's force_flush has NOT yet returned.
                type(self).delivered_before_flush_returned = "flush-returned" not in order

        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            return True

    downstream = _SlowDownstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164")

    # A trigger root with one buffered sibling: closing the root detaches the sibling and
    # forwards it — which is where the forwarder blocks.
    root_span = tracer.start_span(_TRIGGER_ROOT)
    with tracer.start_as_current_span(
        "ordinary.child", context=otel_trace.set_span_in_context(root_span)
    ):
        pass

    producer = threading.Thread(target=root_span.end, name="b164-producer")
    producer.start()
    assert sibling_in_downstream.wait(timeout=5.0), "the sibling never reached downstream"
    assert tail.buffered_trace_count == 0, (
        "the trace should already be detached — that is what makes the window observable"
    )

    # ORDER-based, not timing-based (out-of-family Codex): a `wait(0.5)` on the flusher can
    # pass simply because the scheduler never ran it. Nor is an event set just BEFORE the
    # call enough — the flusher can be descheduled there, the release fires first, and the
    # test passes with the wait deleted. Synchronize on a point reached INSIDE the wait by
    # hooking the condition, so the flusher is provably parked on the in-flight count before
    # anything is released. (An earlier attempt to apply this edit silently no-op'd and was
    # caught by out-of-family Codex re-reading the committed file.)
    in_the_wait = threading.Event()
    real_cv_wait = tail._inflight_cv.wait

    def _hooked_wait(timeout: float | None = None) -> bool:
        in_the_wait.set()
        return real_cv_wait(timeout)

    tail._inflight_cv.wait = _hooked_wait  # type: ignore[method-assign]

    def _flush() -> None:
        tail.force_flush(timeout_millis=5_000)
        order.append("flush-returned")

    flusher = threading.Thread(target=_flush, name="b164-flusher")
    flusher.start()
    assert in_the_wait.wait(timeout=5.0), (
        "force_flush never entered the in-flight wait — either the batch was not registered "
        "as in flight, or the wait itself is gone"
    )

    release_downstream.set()
    producer.join(timeout=5.0)
    flusher.join(timeout=5.0)
    assert not producer.is_alive() and not flusher.is_alive(), "a thread hung"

    assert "ordinary.child" in downstream.seen, "the detached sibling was never delivered"
    assert order == ["flush-returned"], f"unexpected event order: {order}"
    assert downstream.delivered_before_flush_returned, (
        "force_flush RETURNED before the in-flight detached batch reached downstream — "
        "shutdown could close the exporter first, which is the silent loss force_flush "
        "exists to prevent"
    )


def test_b164_force_flush_still_returns_when_a_wedged_exporter_exceeds_the_budget() -> None:
    """The wait is BOUNDED, and expiry is REPORTED — no hang, no false success.

    `force_flush` waits only within the caller's own `timeout_millis`; on expiry it stops
    waiting and delegates anyway. Without that bound, adding the B-164 wait would trade a
    silent-loss bug for a shutdown hang, which is strictly worse.

    It must also return **False** in that case (out-of-family Codex): returning True with
    batches still undelivered tells the runtime that shutdown may proceed when spans are
    demonstrably outstanding — a quieter version of the very bug this row is about.
    """
    wedged = threading.Event()

    producer_wedged = threading.Event()

    class _WedgedDownstream(_Downstream):
        def on_end(self, span: Any) -> None:
            if span.name == "ordinary.child":
                producer_wedged.set()
                wedged.wait(timeout=10.0)  # never released within the test's budget
            super().on_end(span)

        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            return True

    downstream = _WedgedDownstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.wedged")

    root_span = tracer.start_span(_TRIGGER_ROOT)
    with tracer.start_as_current_span(
        "ordinary.child", context=otel_trace.set_span_in_context(root_span)
    ):
        pass
    producer = threading.Thread(target=root_span.end, name="b164-wedged-producer", daemon=True)
    producer.start()
    # Entry EVENT, not a sleep (out-of-family Codex): on a loaded runner a 100 ms sleep can
    # elapse before the producer reaches the wedged exporter, in which case the main thread
    # would drain the child itself and block on the exporter's own 10 s wait.
    assert producer_wedged.wait(timeout=5.0), "the producer never reached the wedged exporter"

    started = time.monotonic()
    result = tail.force_flush(timeout_millis=300)
    elapsed = time.monotonic() - started
    assert result is False, (
        "force_flush reported SUCCESS while a batch was still undelivered — that tells the "
        "runtime shutdown may proceed when spans are demonstrably outstanding"
    )
    assert elapsed < 3.0, (
        f"force_flush waited {elapsed:.1f}s on a wedged exporter with a 300ms budget — the "
        "B-164 wait is not bounded and shutdown can hang"
    )
    wedged.set()
    producer.join(timeout=5.0)


def test_b164_a_batch_is_registered_in_flight_the_moment_it_is_detached() -> None:
    """**B-164 (a), the atomicity half** — registration happens WITH the detach, not after.

    A first version of this fix incremented the in-flight counter inside `_forward_detached`,
    i.e. *after* `_publish_keep_and_maybe_detach` had already popped the batch and released
    the lock. Out-of-family Codex found the gap: a `force_flush` landing in that window sees
    an **empty buffer AND zero in-flight**, delegates, and returns while the spans are in the
    air — reproducing the exact loss the fix intends to close.

    The earlier witness could not tell the two versions apart: it starts its flusher long
    before the window and so only proves that a *registered* batch is waited for. This one
    discriminates by construction — the producer is suspended at the entry to
    `_forward_detached`, which is precisely the moment *after* detachment and *before* any
    post-hoc increment would run. With registration done under the detaching lock the batch
    is already counted there; with the gap it is not.
    """
    at_forward_entry = threading.Event()
    release_producer = threading.Event()

    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    original_forward = tail._forward_detached

    def _hooked_forward(spans: Any) -> None:
        if spans and threading.current_thread().name == "b164-atomic-producer":
            at_forward_entry.set()
            release_producer.wait(timeout=5.0)
        original_forward(spans)

    tail._forward_detached = _hooked_forward  # type: ignore[method-assign]

    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.atomic")

    root_span = tracer.start_span(_TRIGGER_ROOT)
    with tracer.start_as_current_span(
        "ordinary.child", context=otel_trace.set_span_in_context(root_span)
    ):
        pass

    producer = threading.Thread(target=root_span.end, name="b164-atomic-producer")
    producer.start()
    assert at_forward_entry.wait(timeout=5.0), "the producer never reached the forward"

    # The batch is detached (buffer empty) but not yet forwarded. If registration were
    # post-hoc, in-flight would read 0 here and force_flush would return immediately.
    assert tail.buffered_trace_count == 0, "the batch should already be detached"
    assert len(tail._inflight_batch_seqs) == 1, (
        f"the detached batch is not registered in flight ({tail._inflight_batch_seqs}) — a "
        "concurrent force_flush would see an empty buffer and nothing pending, and return "
        "while these spans are still undelivered"
    )

    release_producer.set()
    producer.join(timeout=5.0)
    assert not producer.is_alive(), "the producer hung"
    assert "ordinary.child" in downstream.seen
    assert not tail._inflight_batch_seqs, "the in-flight registry did not settle back to empty"


def test_b164_a_raising_downstream_does_not_leak_the_in_flight_registration() -> None:
    """The registration is released even if forwarding the current span RAISES.

    `_publish_keep_and_maybe_detach` registers the detached batch while it still holds the
    lock, so the release must be unconditional. If `downstream.on_end(span)` — the
    always-sampled span itself, forwarded *before* the batch — raises and the release is
    skipped, the in-flight registry stays non-empty **forever**: every later `force_flush` then
    burns its entire timeout waiting for a batch that will never be delivered, and now also
    reports failure. A `finally` around the current-span forward covers it (out-of-family
    Codex).
    """

    class _RaisingDownstream(_Downstream):
        def on_end(self, span: Any) -> None:
            if span.name == _TRIGGER_ROOT:
                raise RuntimeError("exporter blew up")
            super().on_end(span)

    downstream = _RaisingDownstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.raise")

    root_span = tracer.start_span(_TRIGGER_ROOT)
    with tracer.start_as_current_span(
        "ordinary.child", context=otel_trace.set_span_in_context(root_span)
    ):
        pass

    # The SDK propagates processor exceptions rather than swallowing them (verified — an
    # earlier draft assumed otherwise and the RuntimeError escaped the test).
    raised = False
    try:
        root_span.end()
    except RuntimeError:
        raised = True
    assert raised, "the raising downstream did not propagate — the scenario is not exercised"

    assert not tail._inflight_batch_seqs, (
        f"the in-flight registration leaked ({tail._inflight_batch_seqs}) after the current-span "
        "forward raised — every later force_flush would burn its whole budget and report "
        "failure for a batch that will never arrive"
    )
    # And the siblings still went out, since their forwarding is in the `finally`.
    assert "ordinary.child" in downstream.seen

    started = time.monotonic()
    assert tail.force_flush(timeout_millis=500) is True
    assert time.monotonic() - started < 0.4, "force_flush waited on a leaked registration"


def test_b164_force_flush_waits_for_an_on_end_that_has_not_registered_yet() -> None:
    """**B-164 round 5** — work already inside `on_end` counts, not just registered batches.

    The in-flight *batch* counter cannot cover a span whose `on_end` has **started** but has
    not yet taken `_state_lock`: at that moment no batch exists to register. So a
    `force_flush` could observe zero, enter the downstream flush, and only then have the
    child buffer and its root detach a batch — registration landing after the only wait, and
    the flush returning `True` with a batch undelivered.

    `on_end` now counts its own entry and exit, so `force_flush` waits for work already in
    progress. Driven deterministically: the producer is suspended *inside* `on_end` before it
    reaches any buffering, then a flusher runs.
    """
    inside_on_end = threading.Event()
    release_producer = threading.Event()

    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    original_inner = tail._on_end_inner

    def _hooked_inner(span: Any) -> None:
        if threading.current_thread().name == "b164-entry-producer":
            inside_on_end.set()
            release_producer.wait(timeout=5.0)
        original_inner(span)

    tail._on_end_inner = _hooked_inner  # type: ignore[method-assign]

    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.entry")

    root_span = tracer.start_span(_TRIGGER_ROOT)
    child = tracer.start_span("ordinary.child", context=otel_trace.set_span_in_context(root_span))

    producer = threading.Thread(target=child.end, name="b164-entry-producer")
    producer.start()
    assert inside_on_end.wait(timeout=5.0), "the producer never entered on_end"

    # Nothing is buffered and no batch is in flight — only an on_end in progress.
    assert tail.buffered_trace_count == 0
    assert not tail._inflight_batch_seqs
    assert tail._entrants_pending(tail._entry_cutoff()), (
        "in-progress on_end work is not registered — force_flush would see nothing pending "
        "and return before this span is even buffered"
    )

    in_the_wait = threading.Event()
    real_cv_wait = tail._inflight_cv.wait

    def _hooked_wait(timeout: float | None = None) -> bool:
        in_the_wait.set()
        return real_cv_wait(timeout)

    tail._inflight_cv.wait = _hooked_wait  # type: ignore[method-assign]

    result: list[bool] = []
    flusher = threading.Thread(
        target=lambda: result.append(tail.force_flush(timeout_millis=5_000)),
        name="b164-entry-flusher",
    )
    flusher.start()
    assert in_the_wait.wait(timeout=5.0), (
        "force_flush did not wait for the in-progress on_end — it would return while a span "
        "that has entered the processor is still unaccounted for"
    )

    release_producer.set()
    producer.join(timeout=5.0)
    root_span.end()
    flusher.join(timeout=5.0)
    assert not producer.is_alive() and not flusher.is_alive(), "a thread hung"
    assert result == [True], f"force_flush reported {result}"
    assert not tail._active_entries, "the entrant registry did not settle back to empty"


def test_b164_force_flush_redrains_a_span_that_buffers_after_the_first_pass() -> None:
    """**B-164 round 6** — a single drain pass is unsound; `force_flush` drains until stable.

    The counters fix two windows but not this third one: a non-root span that entered
    `on_end` **before** the drain, and buffers **after** it. The drain has already run, then
    the span appends to `_buffer` and deregisters its entrant — so the wait loop exits
    with both counters at zero and `force_flush` returns `True` **with the span still
    buffered and never delivered**.

    `force_flush` now re-drains after the counters settle and repeats until a pass finds
    nothing new. Driven deterministically: the producer is suspended inside `on_end` (so the
    first drain sees an empty buffer) and released only once the flusher is parked in its
    wait.
    """
    inside_on_end = threading.Event()
    release_producer = threading.Event()

    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    original_inner = tail._on_end_inner

    def _hooked_inner(span: Any) -> None:
        if threading.current_thread().name == "b164-redrain-producer":
            inside_on_end.set()
            release_producer.wait(timeout=5.0)
        original_inner(span)

    tail._on_end_inner = _hooked_inner  # type: ignore[method-assign]

    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.redrain")

    root_span = tracer.start_span(_QUIET_ROOT)
    child = tracer.start_span("ordinary.child", context=otel_trace.set_span_in_context(root_span))

    producer = threading.Thread(target=child.end, name="b164-redrain-producer")
    producer.start()
    assert inside_on_end.wait(timeout=5.0), "the producer never entered on_end"
    assert tail.buffered_trace_count == 0, "nothing should be buffered yet — that is the point"

    in_the_wait = threading.Event()
    real_cv_wait = tail._inflight_cv.wait

    def _hooked_wait(timeout: float | None = None) -> bool:
        in_the_wait.set()
        return real_cv_wait(timeout)

    tail._inflight_cv.wait = _hooked_wait  # type: ignore[method-assign]

    result: list[bool] = []
    flusher = threading.Thread(
        target=lambda: result.append(tail.force_flush(timeout_millis=5_000)),
        name="b164-redrain-flusher",
    )
    flusher.start()
    assert in_the_wait.wait(timeout=5.0), "force_flush never parked — it drained and returned"

    # Now let the span buffer: this happens AFTER force_flush's first drain pass.
    release_producer.set()
    producer.join(timeout=5.0)
    flusher.join(timeout=5.0)
    assert not producer.is_alive() and not flusher.is_alive(), "a thread hung"

    assert "ordinary.child" in downstream.seen, (
        f"the span buffered after the first drain pass was never delivered; "
        f"downstream={downstream.seen}, still buffered={tail.buffered_trace_count} — "
        "force_flush must re-drain until a pass finds nothing new"
    )
    assert tail.buffered_trace_count == 0, "the buffer was not fully drained"
    assert result == [True], f"force_flush reported {result} despite draining everything"


def test_b164_a_callback_queued_on_the_state_lock_is_already_counted() -> None:
    """**B-164 round 7** — entrants are counted BEFORE they contend on `_state_lock`.

    The entry counter used to be guarded by `_state_lock` itself (via the shared condition).
    That reintroduced the same class of hole one level down: a callback reaching `on_end`
    while `force_flush` held the state lock would block **before** being counted, so the
    flusher could release, immediately reacquire for its zero check, observe nothing, and
    return — after which the queued callback buffered an already-ended span.

    The counter now has its own `_entry_lock`, held only for two integer operations. This
    asserts the ordering directly: with `_state_lock` held by the test, a span ending on
    another thread is **already counted** even though it cannot yet proceed.
    """
    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.queued")

    root_span = tracer.start_span(_QUIET_ROOT)
    child = tracer.start_span("ordinary.child", context=otel_trace.set_span_in_context(root_span))

    # Hold the state lock so the ending callback is stuck contending for it.
    with tail._state_lock:
        producer = threading.Thread(target=child.end, name="b164-queued-producer")
        producer.start()

        # Give the producer time to reach the contention point. The ASSERTION does not
        # depend on this window being long enough — if the producer has not entered yet the
        # counter reads 0 and the test fails loudly rather than passing vacuously.
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not tail._entrants_pending(tail._entry_cutoff()):
            time.sleep(0.01)

        assert tail._entrants_pending(tail._entry_cutoff()), (
            "a callback queued on `_state_lock` is NOT counted as an entrant — a flusher "
            "holding that lock could release, re-check, see zero and return, and this span "
            "would then be buffered after the flush completed"
        )
        # It genuinely cannot have proceeded: nothing is buffered while we hold the lock.
        assert tail.buffered_trace_count == 0

    producer.join(timeout=5.0)
    assert not producer.is_alive(), "the producer hung"
    assert not tail._entrants_pending(tail._entry_cutoff()), (
        "the entry counter did not settle back to zero"
    )


def test_b164_force_flush_does_not_wait_on_traffic_that_arrives_after_its_cutoff() -> None:
    """**B-164 round 8** — the flush waits for work at ITS cutoff, not for all later traffic.

    Waiting on a bare "any entrant active" predicate is over-conservative: under sustained
    tracing the count never reaches zero, so `force_flush` burns its whole budget and
    reports **failure** even though everything present at invocation was drained. That is a
    spurious shutdown error, not a loss.

    Entrants now carry a monotonic sequence number and the flush snapshots a cutoff, waiting
    only for entrants at or below it. This asserts the semantics directly: a span that
    enters `on_end` **after** the cutoff is taken is not something that cutoff waits for.
    """
    downstream = _Downstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.cutoff")

    inside = threading.Event()
    release = threading.Event()
    original_inner = tail._on_end_inner

    def _hooked_inner(span: Any) -> None:
        if threading.current_thread().name == "b164-late":
            inside.set()
            release.wait(timeout=5.0)
        original_inner(span)

    tail._on_end_inner = _hooked_inner  # type: ignore[method-assign]

    # Cutoff taken FIRST, while nothing is in flight.
    cutoff = tail._entry_cutoff()
    assert not tail._entrants_pending(cutoff), "nothing should be pending at the cutoff yet"

    # Now a LATE span enters on_end — after the cutoff.
    late_root = tracer.start_span(_QUIET_ROOT)
    late_thread = threading.Thread(target=late_root.end, name="b164-late")
    late_thread.start()
    assert inside.wait(timeout=5.0), "the late span never entered on_end"

    assert tail._entrants_pending(tail._entry_cutoff()), (
        "a currently-running on_end is not registered at all — the entrant registry is broken"
    )
    assert not tail._entrants_pending(cutoff), (
        "a span that entered AFTER the cutoff is being waited for by that cutoff — under "
        "sustained tracing force_flush would never settle and would report spurious failure"
    )

    release.set()
    late_thread.join(timeout=5.0)
    assert not late_thread.is_alive(), "the late thread hung"


def test_b164_a_post_cutoff_batch_does_not_consume_the_flush_budget() -> None:
    """**B-164 round 9** — batches carry generations too, exercised THROUGH `force_flush()`.

    Round 8 gave *entrants* a cutoff but left the batch count global, so a batch detached by
    a **post-cutoff** callback still made the flush wait — the same spurious `False` the
    cutoff exists to prevent, one level down. Batches now carry the generation of the
    `on_end` that produced them.

    **Getting the scenario right mattered.** A first draft started the late trace *before*
    calling `force_flush`, which makes it legitimately **pre**-cutoff work that the flush
    *should* wait for — the test failed for the right reason and the code was fine. To model
    post-cutoff traffic the batch must be produced **after** the cutoff is taken, so this
    hooks `_entry_cutoff` and starts the late producer from inside it.
    """
    release_late = threading.Event()
    late_started = threading.Event()

    class _LateBlockingDownstream(_Downstream):
        def on_end(self, span: Any) -> None:
            if span.name == "late.child" and threading.current_thread().name == "b164-late-batch":
                release_late.wait(timeout=5.0)
            super().on_end(span)

        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            return True

    downstream = _LateBlockingDownstream()
    tail = TailKeepSpanProcessor(downstream=downstream)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b164.late-batch")

    late_thread: list[threading.Thread] = []
    real_cutoff = tail._entry_cutoff

    def _hooked_cutoff() -> int:
        cutoff = real_cutoff()
        if not late_started.is_set():
            late_started.set()
            # Everything below is created AFTER the cutoff was taken.
            late_root = tracer.start_span(_TRIGGER_ROOT)
            with tracer.start_as_current_span(
                "late.child", context=otel_trace.set_span_in_context(late_root)
            ):
                pass
            th = threading.Thread(target=late_root.end, name="b164-late-batch")
            late_thread.append(th)
            th.start()
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline and not tail._inflight_batch_seqs:
                time.sleep(0.01)
        return cutoff

    tail._entry_cutoff = _hooked_cutoff  # type: ignore[method-assign]

    result = tail.force_flush(timeout_millis=400)

    assert tail._inflight_batch_seqs, (
        "the late batch was already delivered — the scenario did not reproduce"
    )
    # NOT a wall-clock assertion (out-of-family Codex): a loaded worker can deschedule this
    # process for longer than any threshold and fail a correct implementation. The two
    # assertions below distinguish the paths without timing — a flush that HAD waited on the
    # late batch would have exhausted its budget and returned False, since that batch is
    # still undelivered at this point (asserted directly above).
    assert result is True, (
        "force_flush reported failure because of a batch that is not its concern — it waited "
        "for a batch produced AFTER its cutoff and timed out, which is the spurious-failure "
        "shape the generation cutoff exists to prevent"
    )

    release_late.set()
    for th in late_thread:
        th.join(timeout=5.0)
        assert not th.is_alive(), "the late producer hung"


def test_b164b_the_only_manual_lifetime_span_is_uncalled() -> None:
    """**B-164(b) inventory invariant** — pins the manual-lifetime span set. Does NOT close the row.

    B-164(b) needs a **root to end before its own child**. Step (3) asked whether that is
    worth defending against.

    **Read this first: this test does NOT establish that B-164(b) is unreachable.** It was
    written to, and that closure was WITHDRAWN at review. The assertions below are true and
    worth keeping — they pin the manual-lifetime span inventory and reopen loudly if it
    changes — but the *closure* they were used to justify rested on an additional, unstated
    universal: *"the interleaving needs a span whose end() can be called out of order, or one
    handed to another thread; production has neither."* Production **has** the second, by
    deliberate design: `harness_cp.workflow_driver._run_fanout_to_completion` abandons its
    executor on any exception via `shutdown(wait=False)` ("the orphaned thread runs to
    completion in the background"), branch dispatch runs under `asyncio.to_thread` — which
    copies the `contextvars` context, so the OTel parent propagates into that thread and
    `llm_dispatch` opens a real child span there — and the §25.11 barrier deadline then
    unwinds the `workflow.envelope` root while that child is still open. So a root CAN end
    before its own child with zero manual `start_span` calls, and B-164(b) stays OPEN until
    someone either builds a repro through that path or argues positively that an orphaned
    child span cannot reach the processor after its root materializes.

    **A first version of this test asserted the wrong thing and passed vacuously.** It
    claimed production held *zero* manual-lifetime spans, but filtered on `ast.Assign` only —
    so it skipped `child: ChildSpanRef = tracer.start_span(...)`, an **annotated** assignment
    at `operator_burden_eval_primitives.py:252`. The invariant was already false when
    written, and out-of-family Codex caught it. The corrected basis is narrower and is
    asserted here in two parts:

    1. **Exactly one** `start_span` site exists in `src/` — every other span-opening site
       uses `with tracer.start_as_current_span(...)`, whose lexical nesting makes a
       parent-ends-first ordering impossible; and
    2. that one site, `emit_eval_as_child_span`, has **no caller anywhere in `src/`** — its
       own docstring says *"never invoked"*. It is the same landed-but-uncalled shape as
       `B-162`.

    So *this particular* route to the shape — a manual-lifetime span ended out of order — is
    closed off **because nothing calls the only code that could produce it**. That is a
    strictly weaker claim than the first draft made, and it is the true one. It is also not
    sufficient to close B-164(b), per the paragraph above: the fan-out orphaned-thread route
    reaches the same ordering without any manual-lifetime span at all. If either part below
    changes — a second manual-lifetime span appears, or something calls this one — a second
    independent route opens too, which is what the failure messages below say.
    """
    manual_sites: list[str] = []
    for path in _REPO.glob("harness-*/src/**/*.py"):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:  # pragma: no cover - a syntax error fails the suite anyway
            continue
        for node in ast.walk(tree):
            # Match at the CALL level: an `ast.Assign` filter misses annotated assignments,
            # walrus bindings and bare expressions. That mistake is what made the first
            # version of this test vacuous.
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "start_span"
            ):
                manual_sites.append(f"{path.relative_to(_REPO)}:{node.lineno}")

    assert manual_sites == ["harness-od/src/harness_od/operator_burden_eval_primitives.py:252"], (
        f"the manual-lifetime span inventory changed: {manual_sites}. A span whose `end()` "
        "can be called out of order — or which can be handed to another thread — makes "
        "B-164(b)'s root-ends-before-its-child interleaving REACHABLE, so that row must be "
        "re-adjudicated rather than left closed."
    )

    # ...and the one site that exists is dead code, which is what actually closes B-164(b).
    callers = [
        f"{path.relative_to(_REPO)}:{node.lineno}"
        for path in _REPO.glob("harness-*/src/**/*.py")
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id == "emit_eval_as_child_span")
            or (
                isinstance(node.func, ast.Attribute) and node.func.attr == "emit_eval_as_child_span"
            )
        )
    ]
    assert callers == [], (
        f"`emit_eval_as_child_span` now has caller(s) {callers} — the only manual-lifetime "
        "span in production has become live, so B-164(b) is REACHABLE and must be reopened."
    )

"""`B-164(b)` REPRO — the fan-out orphaned thread ends a child span AFTER its root.

**What this file settles.** `B-164(b)` says a child span that reaches
`TailKeepSpanProcessor.on_end` *after* its own root has already materialized the
trace is stranded (and, under buffer pressure, evicted). Two successive closures
claimed the ordering was UNREACHABLE in production. Both were wrong. The second
one — "the interleaving needs a span whose `end()` can be called out of order, or
one handed to another thread; production has neither" — is falsified here **by
execution, not by argument**: production hands spans to another thread by design.

**The production mechanism, driven directly.** These tests call the REAL
`harness_cp.workflow_driver._run_fanout_to_completion` (a private symbol imported
deliberately — the whole point is to exercise the shipped function, not a
re-implementation of it). On ANY exception — the §25.11 barrier deadline or an
ordinary branch failure — it abandons its `ThreadPoolExecutor` with
`shutdown(wait=False)`; its own docstring says *"the orphaned thread runs to
completion in the background"*. Branch dispatch runs under `asyncio.to_thread`,
which copies the `contextvars` context, so the OTel parent propagates across the
bridge and a real child span opens **on a thread the fan-out no longer waits
for**. The exception then unwinds the enclosing
`with tracer.start_as_current_span(...)` root **while that child is still open**.

**The abandon is load-bearing, and that is checked rather than assumed.** An
out-of-family reviewer built the counterfactual: replace the abandoning
`_run_fanout_to_completion` with joining semantics (`asyncio.run`, which joins its
default executor at shutdown) and keep everything else identical — the ordering
*disappears*, `['gen_ai.dispatch', 'ordinary.root']`, child before root. So the
ordering under test is produced by `shutdown(wait=False)`, not by the fixture.

**Precision about WHERE the span opens** (out-of-family lens, P2 — recorded on the
`B-164(b)` row). This file opens the child span *directly* in the abandoned worker,
which is the minimal faithful shape. For every currently-wired dispatcher the span
opens one hop further out: `SyncDispatcherFacade` — which opens no span itself —
bridges back to a captured, persistent outer loop via
`asyncio.run_coroutine_threadsafe`, so `RuntimeLLMDispatcher.dispatch`'s span runs
on the OUTER LOOP's thread, not on the `to_thread` worker that gets abandoned. The
reviewer verified independently, wiring a real `SyncDispatcherFacade`, that the same
root-before-child ordering reproduces through that path — so reachability is
unaffected. It does change the shape of a fix: the late-arrival window is gated by
the outer loop's coroutine lifetime, not literally by the abandoned executor. A
facade-level witness is the natural next strengthening of this file.

**Determinism.** Nothing here races on a sleep. The failing branch does not raise
until the wedged branch has signalled that its child span is OPEN, and the child
span does not close until the test releases it — which it does only after the
root's `with` block has already exited. The ordering under test is therefore
forced, not observed by luck.

**Status of each test — `B-164(b)` is now FIXED, and this file records what the
fix does and does not deliver.** The mechanism test still PASSES and still pins
production's ability to end a child after its root, which stays true whether or
not the processor handles it. The three `xfail(strict=True)` witnesses that
asserted the FIXED behaviour reddened as XPASS when the fix landed — the
intended signal — and are now plain passing assertions, except for the one half
of the last witness that is a DECIDED BOUND rather than a defect.

**What the fix does** (`tail_keep_span_processor.py`, "Late arrivals"): a span
whose trace has already published its keep decision at root close is recognised
against a bounded FIFO memory of recently materialized trace_ids and forwarded
IMMEDIATELY — never buffered. That kills both measured costs at once: with no
ceiling the span is no longer DELAYED to `force_flush`, and under buffer
pressure it is no longer the oldest bucket and so no longer DROPPED. It also
suppresses the `_keep` write for an already-materialized trace, closing the
stale-entry leak.

**What the fix deliberately does NOT do** (`test_b164b_bound_*`): a late span
that is itself the §10.2 trigger cannot rescue its trace. The keep decision was
taken without it and its siblings were already dropped; retaining dropped spans
against the chance of a later trigger would reintroduce the unbounded memory the
drop exists to avoid. The trigger span itself IS preserved — this is the same
tradeoff the processor already documents for eviction, where the failure signal
survives and only the buffered tree-context is shed.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from typing import Any

import pytest
from harness_cp.workflow_driver import _run_fanout_to_completion
from harness_od.tail_keep_span_processor import (
    _LIVENESS_TRACKING_CEILING,
    TailKeepSpanProcessor,
)
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.trace import set_span_in_context

#: A §10.2 classification trigger AND a §9.2 always-sampled span name.
_TRIGGER = "sandbox.violation"
#: Deliberately NOT always-sampled, so it takes the buffering path under test.
_ROOT = "ordinary.root"
_CHILD = "gen_ai.dispatch"
#: Every wait is bounded; a hang is a failure, never a hung suite.
_TIMEOUT = 10.0


class _Downstream:
    """Records what the tail processor actually forwards."""

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


class _EndOrder(SpanProcessor):
    """A second processor recording the TRUE `on_end` order, before any filtering.

    Registered alongside the tail processor rather than wrapping it, so observing
    the order cannot perturb the behaviour being observed.
    """

    def __init__(self) -> None:
        self.ended: list[tuple[str, bool, int]] = []

    def on_end(self, span: Any) -> None:
        ctx = span.get_span_context()
        self.ended.append((span.name, span.parent is None, ctx.trace_id))

    def names(self) -> list[str]:
        return [name for name, _root, _tid in self.ended]


class _Fixture:
    """A provider wired to the real tail processor plus an order recorder."""

    def __init__(self, **bounds: int | None) -> None:
        self.downstream = _Downstream()
        self.tail = TailKeepSpanProcessor(downstream=self.downstream, **bounds)  # type: ignore[arg-type]
        self.order = _EndOrder()
        provider = TracerProvider()
        provider.add_span_processor(self.order)
        provider.add_span_processor(self.tail)
        self.tracer = provider.get_tracer("b164b-repro")

    def orphan_a_child(
        self,
        child_name: str = _CHILD,
        *,
        root_name: str = _ROOT,
        while_child_open: Callable[[], None] | None = None,
    ) -> None:
        """Run the real fan-out so `child_name` ends AFTER `root_name` has closed.

        Returns once the orphaned thread has finished, so the caller observes the
        settled state rather than a moving one.

        `while_child_open` runs at the one moment that is hard to reach from outside: the
        root has closed and the orphaned child is still OPEN. That is the window in which
        unrelated traffic can age the orphan out of a size-bounded memory, so a caller
        that wants to test that window has to drive it from in here.
        """
        child_open = threading.Event()
        release_child = threading.Event()
        child_done = threading.Event()

        def _wedged_branch() -> None:
            # Runs in the executor thread that `_run_fanout_to_completion` abandons.
            # `asyncio.to_thread` copied the contextvars context, so the root below
            # is this span's live parent.
            with self.tracer.start_as_current_span(child_name):
                child_open.set()
                release_child.wait(timeout=_TIMEOUT)
            child_done.set()

        async def _fanout() -> None:
            async def wedged() -> None:
                await asyncio.to_thread(_wedged_branch)

            async def failing() -> None:
                # Wait for the CONDITION, not a duration: raise only once the child
                # span is genuinely open, so the orphaning is forced every run.
                while not child_open.is_set():
                    await asyncio.sleep(0.005)
                raise RuntimeError("branch failed — the §25.11-shaped exit")

            await asyncio.gather(wedged(), failing())

        with self.tracer.start_as_current_span(root_name):
            with pytest.raises(RuntimeError):
                _run_fanout_to_completion(_fanout(), max_workers=2)
        # The root span has ENDED here while the orphaned thread still holds its child.
        assert child_open.is_set(), (
            "the child span never opened — fixture is not exercising B-164(b)"
        )
        assert not child_done.is_set(), "the child closed before the root — ordering not achieved"

        if while_child_open is not None:
            while_child_open()

        release_child.set()
        assert child_done.wait(timeout=_TIMEOUT), "the orphaned thread never completed"

    def orphan_a_child_that_starts_late(
        self, child_name: str = _CHILD, *, root_name: str = _ROOT
    ) -> None:
        """Run the real fan-out so `child_name` STARTS after `root_name` has closed.

        The other ordering, and a strictly harder one. In `orphan_a_child` the child span
        is already open when the root closes, so the processor has seen its `on_start` and
        can pin the trace as live. Here the abandoned worker is running with the root's
        copied context but has NOT opened its span yet, so at root close the trace looks
        completely finished — nothing is live, and only a memory of the materialization can
        recognise the child when it finally arrives.

        This is not a contrived shape: the §25.11 barrier deadline fires on a clock, with
        no regard for whether a branch has reached its dispatch call yet.
        """
        worker_ready = threading.Event()
        start_child = threading.Event()
        child_done = threading.Event()

        def _wedged_branch() -> None:
            # Deliberately does NOT open the span yet — the context is copied and live,
            # but the span does not exist until the test says so.
            worker_ready.set()
            start_child.wait(timeout=_TIMEOUT)
            with self.tracer.start_as_current_span(child_name):
                pass
            child_done.set()

        async def _fanout() -> None:
            async def wedged() -> None:
                await asyncio.to_thread(_wedged_branch)

            async def failing() -> None:
                # Raise once the worker is RUNNING but before it opens anything.
                while not worker_ready.is_set():
                    await asyncio.sleep(0.005)
                raise RuntimeError("branch failed before the child span opened")

            await asyncio.gather(wedged(), failing())

        with self.tracer.start_as_current_span(root_name):
            with pytest.raises(RuntimeError):
                _run_fanout_to_completion(_fanout(), max_workers=2)
        assert worker_ready.is_set(), "the orphaned worker never ran — fixture mis-built"
        assert not child_done.is_set(), "the child ran to completion before the root closed"

        start_child.set()
        assert child_done.wait(timeout=_TIMEOUT), "the orphaned thread never completed"


def test_the_fanout_really_orphans_a_thread_that_outlives_the_root() -> None:
    """**Premise.** The mechanism exists: a child span ends after its own root.

    This is the fact both closure attempts denied. It is a property of shipped
    production code (`_run_fanout_to_completion` + `asyncio.to_thread`), so it
    stays true after any `B-164(b)` fix — this test pins the grounding, not the bug.
    """
    fx = _Fixture()
    fx.orphan_a_child()

    assert fx.order.names() == [_ROOT, _CHILD], (
        f"expected the root to end BEFORE its own child, got {fx.order.names()} — "
        "if this changed, the fan-out no longer orphans a span-holding thread and "
        "B-164(b)'s premise must be re-grounded"
    )
    (_root_name, root_is_root, root_tid), (_child_name, child_is_root, child_tid) = fx.order.ended
    assert root_is_root is True, "the root span is not parentless — fixture mis-built"
    assert child_is_root is False, (
        "the orphaned span has no parent, so it is its own trace and cannot strand a "
        "sibling — the contextvars propagation this repro depends on has changed"
    )
    assert child_tid == root_tid, (
        "the orphaned child landed in a DIFFERENT trace, so it cannot be stranded under "
        "the root's trace_id — B-164(b)'s mechanism would not apply"
    )


def test_the_orphaned_child_is_not_stranded_in_the_buffer_after_root_close() -> None:
    """**The repaired behaviour, at the exact site the defect lived.** No slot leaks.

    Before the fix the root had already popped `_buffer[trace_id]`, the late child hit
    `setdefault`, re-created the bucket, and — being a non-root close — detached nothing:
    the same never-freed-slot pathology `B-136` repaired for always-sampled roots. The
    late-arrival path forwards the child instead of buffering it, so no bucket is
    re-created and the trace holds no `max_buffered_traces` slot.

    Asserted on the buffer AND on downstream, because either alone is satisfiable the
    wrong way: an empty buffer with nothing forwarded would mean the span was dropped.
    """
    fx = _Fixture()
    fx.orphan_a_child()

    assert fx.tail.buffered_trace_count == 0, (
        f"the orphaned child re-created a bucket nothing will ever pop "
        f"({fx.tail.buffered_trace_count} trace(s) buffered) — B-164(b) has regressed"
    )
    assert _CHILD in fx.downstream.seen, (
        f"the orphaned child left the buffer without reaching downstream, i.e. it was "
        f"dropped rather than forwarded; got {fx.downstream.seen}"
    )


def test_b164b_the_orphaned_child_reaches_downstream_under_live_traffic() -> None:
    """**Repaired.** The dispatch span exports instead of missing its own trace.

    Before the fix it never reached downstream at all — and it is precisely the span
    an operator most wants when a branch wedged badly enough to trip the barrier.

    **Why it exports is worth stating precisely, because the obvious reading is
    wrong.** The `sandbox.violation` opened here is NOT a sibling of the orphan: it
    has no active parent, so it roots its OWN trace (verified — the two spans carry
    different trace_ids), and it therefore keep-flags nothing in the orphan's trace.
    The orphan's trace in fact materializes with `keep=False`. The child reaches
    downstream because the late-arrival path forwards it directly — keep-all, the
    posture used wherever a tail decision is unavailable — not because any keep flag
    rescued it. The unrelated trace is retained as live traffic around the orphan:
    it proves the late-arrival memory is keyed by trace_id and is not perturbed by
    other traces materializing before or between.
    """
    fx = _Fixture()
    with fx.tracer.start_as_current_span(_TRIGGER):
        pass
    fx.orphan_a_child()

    assert _CHILD in fx.downstream.seen, (
        f"the orphaned dispatch span never reached downstream; got {fx.downstream.seen}"
    )


def test_b164b_the_orphaned_child_survives_buffer_pressure() -> None:
    """**Repaired.** The orphan is no longer silently dropped under a ceiling.

    This is the half of `B-164(b)` that was a permanent LOSS rather than a delay.
    Measured before the fix: with no ceiling the span was merely DELAYED to
    `force_flush`; with a ceiling and live traffic the stranded bucket was the OLDEST
    entry, so it was the first evicted and `force_flush` never recovered it. Because
    the span is now forwarded at its own `on_end` it never occupies a bucket, so no
    amount of subsequent pressure can evict it.
    """
    fx = _Fixture(max_buffered_traces=1)
    fx.orphan_a_child()

    # Drive genuinely separate, well-formed traces past the ceiling.
    for i in range(3):
        with fx.tracer.start_as_current_span(f"pressure.root.{i}"):
            with fx.tracer.start_as_current_span(f"pressure.child.{i}"):
                pass

    fx.tail.force_flush(2000)
    assert _CHILD in fx.downstream.seen, (
        f"the orphaned span was evicted and is permanently lost "
        f"(dropped_trace_count={fx.tail.dropped_trace_count}); force_flush could not "
        f"recover it. downstream={fx.downstream.seen}"
    )


def test_b164b_the_orphan_survives_unrelated_traffic_while_it_is_still_open() -> None:
    """**The boundary that killed the first fix, now absent by construction.**

    The first revision remembered materialized traces in a fixed FIFO window of 1,024
    root closes. Out-of-family review reproduced the exact edge: with the orphaned child
    still open, 1,023 intervening roots forwarded it and 1,024 aged it out, dropping it
    back onto the buffer path where the `max_buffered_traces` ceiling evicted it — the
    original loss, restored by the repair's own bookkeeping.

    Retention is now keyed to LIVENESS rather than to a count of unrelated traces, so
    there is no window to exceed. The churn here deliberately runs past
    `_LIVENESS_TRACKING_CEILING` — the abandoned-span backstop — so that passing cannot
    be explained by the backstop merely being larger than the old window. It can only be
    explained by the orphan's trace being retained *because the orphan is still open*.

    `max_buffered_traces=1` is what makes a regression LOSS rather than delay: without a
    ceiling an aged-out orphan would merely wait for `force_flush` and the assertion would
    still pass, hiding the defect.
    """
    fx = _Fixture(max_buffered_traces=1)

    def churn_unrelated_traces() -> None:
        for i in range(_LIVENESS_TRACKING_CEILING + 64):
            with fx.tracer.start_as_current_span(f"unrelated.root.{i}"):
                pass

    fx.orphan_a_child(while_child_open=churn_unrelated_traces)

    assert _CHILD in fx.downstream.seen, (
        f"the orphan was aged out of the materialization memory by unrelated traffic and "
        f"then evicted from the buffer — the B-164(b) loss has returned "
        f"(dropped_trace_count={fx.tail.dropped_trace_count})"
    )
    assert fx.tail.buffered_trace_count == 0, (
        f"the orphan re-entered the buffer instead of being forwarded "
        f"({fx.tail.buffered_trace_count} trace(s) buffered)"
    )


def test_b164b_the_orphan_survives_when_it_starts_after_its_root_closed() -> None:
    """**The other ordering — the child had not STARTED when the root closed.**

    Liveness cannot help here: at root close the trace has no open spans at all, because
    the abandoned worker is holding a copied context and has not yet reached its
    `start_as_current_span`. A revision that forgot the trace as soon as liveness hit zero
    sent this child straight back onto the stranding path — reproduced by out-of-family
    review as `buffered_trace_count == 1` with the child never forwarded.

    `max_buffered_traces=1` again makes a regression a LOSS rather than a delay, so the
    assertion cannot be satisfied by a `force_flush` that has not happened.
    """
    fx = _Fixture(max_buffered_traces=1)
    fx.orphan_a_child_that_starts_late()

    assert fx.order.names() == [_ROOT, _CHILD], (
        f"the child did not end after the root — this fixture is not exercising the "
        f"starts-late ordering; got {fx.order.names()}"
    )
    _root_entry, (_child_name, child_is_root, child_tid) = fx.order.ended
    assert child_is_root is False and child_tid == _root_entry[2], (
        "the late-started child did not inherit the root's trace via the copied context, "
        "so it cannot be a late arrival at all — the premise has changed"
    )
    assert _CHILD in fx.downstream.seen, (
        f"a child that STARTED after root close was stranded and lost; "
        f"got {fx.downstream.seen} (dropped_trace_count={fx.tail.dropped_trace_count})"
    )
    assert fx.tail.buffered_trace_count == 0, (
        f"the late-started child re-created a bucket nothing will ever pop "
        f"({fx.tail.buffered_trace_count} trace(s) buffered)"
    )


def test_b164b_the_tracking_dictionaries_stay_bounded_under_completed_traffic() -> None:
    """**Neither tracking structure may become a leak of its own.**

    `_open_spans` must return to EMPTY — every trace here completes, so every `on_start`
    is matched by an `on_end`; a non-empty result means the pairing this design rests on
    is broken. `_materialized` is deliberately different: it retains history for the
    starts-late ordering above, so it is asserted BOUNDED by the ceiling rather than
    empty. Asserting it empty would be asserting the second P1 back into existence.
    """
    fx = _Fixture()
    for i in range(256):
        with fx.tracer.start_as_current_span(f"complete.root.{i}"):
            with fx.tracer.start_as_current_span(f"complete.child.{i}"):
                pass

    assert fx.tail._open_spans == {}, (
        f"completed traces were retained in the liveness counter "
        f"({len(fx.tail._open_spans)} entries) — on_start/on_end are not pairing"
    )
    assert len(fx.tail._materialized) <= _LIVENESS_TRACKING_CEILING, (
        f"the materialization history exceeded its ceiling "
        f"({len(fx.tail._materialized)} > {_LIVENESS_TRACKING_CEILING})"
    )


def test_b164b_keep_flags_stay_bounded_when_triggers_arrive_past_the_history() -> None:
    """**The residual must be a bounded LOSS, never an unbounded LEAK.**

    Aging out of the materialization history is an accepted fidelity loss. What is not
    acceptable is what out-of-family review found hiding behind it: past the history a
    late `sandbox.violation` looks like an ordinary pending trace, so it writes
    `_keep[trace_id]` that no root close will ever pop — and REPEATING that ordering grew
    `_keep` without limit. A component whose entire design is bounded memory cannot have
    an unbounded dictionary in it, so `_keep` carries its own ceiling.

    Driven with plain span contexts rather than the fan-out fixture: the ordering under
    test is "child ends after its root, past the history window", and reproducing that
    thousands of times through real abandoned threads would buy no extra fidelity for a
    great deal of wall-clock. The threaded fixture already establishes that production
    produces this ordering; this test is about what the processor does when it recurs.
    """
    fx = _Fixture()
    overshoot = _LIVENESS_TRACKING_CEILING + 64

    # Root-close each trace, keeping a context so a child can still be parented to it.
    aged_parents = []
    for i in range(overshoot):
        root = fx.tracer.start_span(f"aged.root.{i}")
        aged_parents.append(set_span_in_context(root))
        root.end()

    # Push every one of those traces out of the bounded history.
    for i in range(overshoot):
        fx.tracer.start_span(f"churn.root.{i}").end()

    # Now a late trigger on each aged-out trace — the leak ordering, repeated.
    for parent in aged_parents:
        fx.tracer.start_span(_TRIGGER, context=parent).end()

    assert len(fx.tail._keep) <= _LIVENESS_TRACKING_CEILING, (
        f"stale keep flags grew past the ceiling ({len(fx.tail._keep)} > "
        f"{_LIVENESS_TRACKING_CEILING}) — the bounded loss has become an unbounded leak"
    )
    assert len(fx.tail._materialized) <= _LIVENESS_TRACKING_CEILING, (
        f"the materialization history grew past its ceiling ({len(fx.tail._materialized)})"
    )
    assert fx.downstream.seen.count(_TRIGGER) == overshoot, (
        f"the §10.2 failure signal was lost while bounding the leak — every trigger span "
        f"must still be forwarded; got {fx.downstream.seen.count(_TRIGGER)} of {overshoot}"
    )


def test_b164b_bounding_keep_flags_never_discards_a_live_keep_decision() -> None:
    """**Bounding the leak must not silently drop VALID keep decisions.**

    The first attempt at the bound was a blind FIFO ceiling on `_keep`, and out-of-family
    review showed it discards legitimate state: with more than `_LIVENESS_TRACKING_CEILING`
    trigger-bearing traces genuinely pending root close, the oldest valid entry was
    evicted, its trace then materialized `keep=False`, and its root was dropped — silently,
    with `dropped_trace_count` still zero, so nothing in the metrics would show it.

    Every trace here is legitimately in flight (root still open, trigger already seen), so
    NOTHING is evictable and all of them must survive. `max_buffered_traces` is left
    unbounded on purpose: that isolates the failure to the keep-flag ceiling rather than
    to buffer pressure, which is exactly the case review raised.
    """
    fx = _Fixture()
    pending = _LIVENESS_TRACKING_CEILING + 64

    roots = []
    for i in range(pending):
        root = fx.tracer.start_span(f"pending.root.{i}")
        # An always-sampled §10.2 trigger inside the still-open root: it forwards
        # immediately and sets the trace's keep flag without ever entering the buffer.
        fx.tracer.start_span(_TRIGGER, context=set_span_in_context(root)).end()
        roots.append(root)

    for root in roots:
        root.end()

    forwarded_roots = {name for name in fx.downstream.seen if name.startswith("pending.root.")}
    assert len(forwarded_roots) == pending, (
        f"only {len(forwarded_roots)} of {pending} keep-flagged roots were forwarded — a "
        f"valid keep decision was discarded by the bound "
        f"(dropped_trace_count={fx.tail.dropped_trace_count}, which stays 0 precisely "
        f"because this loss does not go through buffer eviction)"
    )
    assert fx.tail._keep == {}, (
        f"keep flags survived their own root closes ({len(fx.tail._keep)} left) — every "
        f"one of these traces root-closed, so every flag should have been popped"
    )


def test_b164b_history_pressure_never_evicts_a_provably_live_trace() -> None:
    """**A ceiling may shed history; it may never shed a proven-live pin.**

    An earlier revision, when every `_materialized` entry was live-pinned, shed the oldest
    one anyway on the reasoning that boundedness was the harder guarantee. Out-of-family
    review pointed out what that costs: `_open_spans` PROVES that trace still has an open
    descendant, and deleting its entry puts that descendant back on the stranding path —
    the `B-164(b)` loss, restored by the bound meant to make the fix safe.

    Every trace here has root-closed with a child still open, so nothing is evictable and
    the ceiling must give way instead of the guarantee. Growth is safe in exactly this
    case, because each retained entry is backed by a live span and is therefore bounded by
    real concurrency rather than by traffic.
    """
    fx = _Fixture(max_buffered_traces=1)
    live = _LIVENESS_TRACKING_CEILING + 64

    children = []
    for i in range(live):
        root = fx.tracer.start_span(f"live.root.{i}")
        children.append(fx.tracer.start_span(f"{_CHILD}.{i}", context=set_span_in_context(root)))
        root.end()

    for child in children:
        child.end()

    forwarded = {name for name in fx.downstream.seen if name.startswith(_CHILD)}
    assert len(forwarded) == live, (
        f"only {len(forwarded)} of {live} live-pinned children were forwarded — a trace "
        f"proven live by _open_spans was evicted from the materialization memory and its "
        f"child stranded (dropped_trace_count={fx.tail.dropped_trace_count})"
    )


def test_b164b_a_failing_downstream_on_start_does_not_leak_liveness() -> None:
    """**A rolled-back span must not leave a permanent liveness pin.**

    `on_start` increments before forwarding, so if the downstream processor raises, the
    SDK propagates before `Tracer.start_span` returns and the span never exists — no
    `on_end` will ever come to undo the increment. Repeated failures would leak one entry
    per trace and could wrongly pin materialization state for traces that never ran.

    The exception must still reach the caller: swallowing it would hide a downstream fault
    behind a tracing component, so that is asserted too.
    """

    class _FailingOnStart(_Downstream):
        def on_start(self, span: Any, parent_context: Any = None) -> None:
            raise RuntimeError("downstream refused the span")

    fx = _Fixture()
    fx.tail._downstream = _FailingOnStart()  # type: ignore[assignment]

    for _ in range(64):
        with pytest.raises(RuntimeError, match="downstream refused the span"):
            fx.tracer.start_span("rejected.root")

    assert fx.tail._open_spans == {}, (
        f"spans that never came into existence left {len(fx.tail._open_spans)} liveness "
        f"entries behind — each one is permanent, since no on_end can ever release it"
    )


def test_b164b_a_late_trigger_leaks_no_keep_entry_and_is_itself_preserved() -> None:
    """**Repaired.** The late trigger neither leaks nor vanishes.

    Here the orphaned span IS the `sandbox.violation` trigger. It arrives after root
    close, so the trace has already materialized. Before the fix it wrote
    `_keep[trace_id] = True` — an entry no root close would ever pop, i.e. an
    unbounded per-trace leak driven by ordinary production behaviour. That write is
    now suppressed for an already-materialized trace.

    The trigger span itself still reaches downstream, which is the property that makes
    the accepted loss below tolerable: the §10.2 failure SIGNAL survives.
    """
    fx = _Fixture()
    fx.orphan_a_child(child_name=_TRIGGER)

    stale_keep = len(fx.tail._keep)
    assert stale_keep == 0, f"a stale _keep entry was left behind ({stale_keep})"
    assert fx.tail.buffered_trace_count == 0, (
        f"the late trigger left a buffered trace behind ({fx.tail.buffered_trace_count})"
    )
    assert _TRIGGER in fx.downstream.seen, (
        f"the late trigger span itself never reached downstream, so the §10.2 failure "
        f"signal was lost — this is the assumption the accepted bound below rests on; "
        f"got {fx.downstream.seen}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="B-164(b) DECIDED BOUND (not a defect): a trigger arriving after root close "
    "cannot retroactively rescue siblings that were already dropped. Retaining dropped "
    "spans against the chance of a later trigger would reintroduce the unbounded memory "
    "the drop exists to avoid. Strict, so the bound cannot be silently widened.",
)
def test_b164b_bound_a_late_trigger_cannot_rescue_its_already_dropped_root() -> None:
    """**The accepted loss, pinned so it stays a decision rather than a surprise.**

    The trace materialized with `keep=False` before the trigger existed, so the root
    was dropped at that moment. Nothing observed later can bring it back without the
    processor retaining spans it has decided to drop — which is the unbounded memory
    the `max_buffered_traces` ceiling exists to prevent, so the loss is accepted.

    This is the SAME tradeoff the processor already documents for eviction ("the
    failure *signal* survives eviction; only the buffered tree-*context* is shed"),
    and the signal's survival is asserted in the test above rather than assumed here.

    Kept as a strict xfail rather than deleted: if a later change ever does preserve
    the root, this reddens and forces the bound to be re-decided in the open instead
    of drifting.
    """
    fx = _Fixture()
    fx.orphan_a_child(child_name=_TRIGGER)

    assert _ROOT in fx.downstream.seen, (
        f"the root was dropped despite its trace later carrying a trigger; got {fx.downstream.seen}"
    )

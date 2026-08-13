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
which copies the `contextvars` context, so the OTel parent propagates into that
thread and a real child span opens there. The exception then unwinds the
enclosing `with tracer.start_as_current_span(...)` root **while that child is
still open**.

**Determinism.** Nothing here races on a sleep. The failing branch does not raise
until the wedged branch has signalled that its child span is OPEN, and the child
span does not close until the test releases it — which it does only after the
root's `with` block has already exited. The ordering under test is therefore
forced, not observed by luck.

**Status of each test.** The first two PASS today: they pin the mechanism and the
ordering, which are facts about production and stay true whether or not
`B-164(b)` is ever fixed. The remaining three are `xfail(strict=True)` — they
assert the behaviour a FIXED processor would have. When `B-164(b)` is fixed they
flip to XPASS and strict mode reddens the suite, which is the intended signal to
close the register row rather than let a stale repro rot.

Measured cost (see the individual tests): with no `max_buffered_traces` ceiling
the orphaned span is DELAYED to `force_flush` (i.e. missing from its trace at
root-close, when the trace is actually exported); under buffer pressure it is
DROPPED outright and `force_flush` never recovers it. If the orphan is itself the
§10.2 classification trigger, the trace's keep decision is taken WITHOUT it — the
root and its siblings drop — and a `_keep` entry is left that nothing will ever
pop.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any

import pytest
from harness_cp.workflow_driver import _run_fanout_to_completion
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

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

    def orphan_a_child(self, child_name: str = _CHILD, *, root_name: str = _ROOT) -> None:
        """Run the real fan-out so `child_name` ends AFTER `root_name` has closed.

        Returns once the orphaned thread has finished, so the caller observes the
        settled state rather than a moving one.
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

        release_child.set()
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


def test_the_orphaned_child_is_stranded_in_the_buffer_after_root_close() -> None:
    """**The defect, pinned as it behaves today.** The trace slot is never freed.

    The root already popped `_buffer[trace_id]`; the late child hits `setdefault`,
    re-creates the bucket, and — being a non-root close — detaches nothing. This is
    the same never-freed-slot pathology `B-136` repaired for always-sampled roots.
    """
    fx = _Fixture()
    fx.orphan_a_child()

    assert fx.tail.buffered_trace_count == 1, (
        "the orphaned child is no longer stranded — if B-164(b) has been fixed, delete "
        "this test and close the register row (the xfail witnesses below will already "
        "have reddened)"
    )
    assert _CHILD not in fx.downstream.seen, (
        "the orphaned child reached downstream after all — B-164(b) may be fixed"
    )


@pytest.mark.xfail(
    strict=True,
    reason="B-164(b) OPEN: a child arriving after root close is never detached, so it "
    "misses the root-close materialization that exports its trace.",
)
def test_b164b_desired_the_orphaned_child_reaches_downstream_with_its_trace() -> None:
    """**Desired behaviour.** The dispatch span should export with its trace.

    The trace is keep-flagged by a sibling `sandbox.violation`, so every buffered
    span in it SHOULD reach downstream at root close. The orphaned dispatch does
    not — and it is precisely the span an operator most wants when a branch wedged
    badly enough to trip the barrier.
    """
    fx = _Fixture()
    with fx.tracer.start_as_current_span(_TRIGGER):
        pass
    fx.orphan_a_child()

    assert _CHILD in fx.downstream.seen, (
        f"the orphaned dispatch span never reached downstream; got {fx.downstream.seen}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="B-164(b) OPEN: the stranded bucket is the OLDEST entry, so it is the first "
    "evicted under the max_buffered_traces ceiling — a permanent loss, not a delay.",
)
def test_b164b_desired_the_orphaned_child_survives_buffer_pressure() -> None:
    """**Desired behaviour.** The orphan should not be silently dropped.

    Measured: with no ceiling the span is merely DELAYED to `force_flush`; with a
    ceiling and live traffic it is DROPPED and `force_flush` never recovers it.
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


@pytest.mark.xfail(
    strict=True,
    reason="B-164(b) OPEN: a trigger arriving after root close writes _keep[trace_id] "
    "that nothing will ever pop, and the keep decision was already taken without it.",
)
def test_b164b_desired_a_late_trigger_still_preserves_its_trace() -> None:
    """**Desired behaviour.** A late trigger should not be decided against, then leak.

    Here the orphaned span IS the `sandbox.violation` trigger. Because it arrives
    after root close, the trace was already materialized with `keep=False` — so the
    root and its siblings were DROPPED — and the trigger then writes a `_keep` entry
    that no root close will ever pop.
    """
    fx = _Fixture()
    fx.orphan_a_child(child_name=_TRIGGER)

    stale_keep = len(fx.tail._keep)
    assert stale_keep == 0, f"a stale _keep entry was left behind ({stale_keep})"
    assert _ROOT in fx.downstream.seen, (
        f"the root was dropped despite its trace carrying a trigger; got {fx.downstream.seen}"
    )

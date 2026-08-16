"""B-123 — the `is_classification_trigger` §10.2 event-name arm.

Authority: `design-substrate/Spec_Operational_Discipline_v1_2.md` §C-OD-10
§10.2 (lines 582-584, cleared and PRESERVED VERBATIM through the current
head — the contract table already reads "Parent + sibling spans of any
`sandbox.violation` EVENT preserved" / "...`breaker.tripped` EVENT
preserved") + register row `B-123` (the widening this module witnesses is a
conformance repair to that already-cleared text, not a design extension).
`Spec_Operational_Discipline_v1_39.md` §1 lands in the SAME PR as this
module: it AMENDS §C-OD-09 §9.2.1 term 3 in full, retracting v1.38 term 3's
explicit decline to widen and requiring the predicate to resolve BOTH the
span-name and span-event shapes of the two §10.2 trigger names. `B-123`
CLOSES at this leg's implementation (this module + `tail_keep_classification
.py` + `tail_keep_span_processor.py`).

**Why a new file rather than extending `test_b133_event_aware_tail_floor.py`
or `test_tail_keep_span_processor.py`.** `B-133`'s module pins the
`TailKeepSpanProcessor.on_end` §9.2.1 arm (`_carries_always_sampled_event`,
a DIFFERENT function resolving span EVENT names against the §9.2 roster).
`B-123` widens a sibling function, `is_classification_trigger`
(`tail_keep_classification.py`), against the DISJOINT §10.2 roster
(`SECTION_10_2_EVENT_TRIGGER_NAMES`, exactly 2 names). The predicate-level
witnesses here (AC1/AC2/AC6/AC7/AC8) are genuinely new surface: no prior
test exercised `is_classification_trigger` against a span EVENT at all.
`test_tail_keep_span_processor.py`'s existing four `is_classification_trigger`
tests (`test_classification_trigger_predicate_matches_*`) stay untouched —
they are name/attribute-arm witnesses, unaffected by this widening. AC3 (the
`B-123` boundary that must now INVERT) is a sibling of an EXISTING witness
(`test_w7_...` in `test_b133_event_aware_tail_floor.py`) and is rewritten
in place there, not duplicated here.

**AC → witness map** (see the PD-8 probe table in this module's tail-comment
for the mutation → red-witness correspondence):

| AC | Witness |
|---|---|
| AC1 | `test_ac1_breaker_tripped_event_on_a_non_trigger_named_span_is_a_trigger` |
| AC2 | `test_ac2_sandbox_violation_event_on_a_non_trigger_named_span_is_a_trigger` |
| AC5 | `test_ac5_section_9_2_member_event_is_not_a_section_10_2_trigger` |
| AC6 | `test_ac6_zero_events_does_not_raise_and_preserves_pre_existing_verdict` |
| AC7 | `test_ac7_name_matching_span_never_touches_events_cheapest_first` |
| AC8 | `test_ac8_event_trigger_names_are_derived_not_re_literalled` |
| AC11 | `test_ac11_span_events_is_read_exactly_once_per_on_end` (+ `test_ac7_confirmed_by_counting_double_zero_events_touches`) |
| AC12 | `test_ac12_keep_flag_scans_the_whole_event_list_not_just_the_first` |

AC3/AC4/AC9/AC10 are proven elsewhere per the arc brief: AC3 at
`test_b133_event_aware_tail_floor.py` (the rewritten `test_w7_...`), AC4 at
`harness-runtime/tests/test_b133_event_aware_tail_floor_real_dispatch.py`
(real-dispatch, no `force_flush`), AC9 (the head-admission bound; do not
overclaim a full floor) stated in this module's + the real-dispatch
witness's docstrings rather than as a separate assertion, AC10 by running
the full suite.

**AC11 (out-of-family Codex [P2] fix-forward, adjudicated CORRECT).** The
event-aware arm at `TailKeepSpanProcessor.on_end` calls BOTH
`_carries_always_sampled_event` and `is_classification_trigger` against the
SAME span in the SAME `on_end` invocation; before this fix each function
independently read `span.events` (a locked, deque-copying OTel property),
doubling the cost for every ordinary span reaching the event checks,
including zero-event ones. Both functions now accept an OPTIONAL
keyword-only `events` snapshot (default `None` = self-read, byte-identical
to prior behaviour for every OTHER caller), and `on_end` reads
`span.events` exactly once and threads that snapshot into both calls.
AC11 proves the count structurally, via a COUNTING double (not a
"small enough" bound) at the `on_end` orchestration level — this is
OD-local (`TailKeepSpanProcessor` is `harness_od`-owned), so no
`harness_runtime` import is needed.

**AC12 (merge-gate BLOCK, test-witness lens, adjudicated CORRECT).** A
mutation reducing `is_classification_trigger`'s event-scan `any(...)` to a
FIRST-EVENT-ONLY check slipped through the ENTIRE changed test set
undetected: every single-function witness above (AC1/AC2/AC5/AC6/AC7/AC11)
uses a span with zero or exactly one event, where `any()` and "first event
only" are indistinguishable; the one multi-event witness that reaches this
line (`test_w15_...`, `member_index=2`, in `test_b133_event_aware_tail_floor
.py`) asserts only carrier export + `buffered_trace_count == 0`, both
driven by the SEPARATE `_carries_always_sampled_event` §9.2 arm (there is no
buffered sibling in that trace for the keep flag to gate); and AC4/AC4b's
real dispatch happens to put `breaker.tripped` FIRST in its event list
(`['breaker.tripped', 'breaker.tripped', 'fallback.exhausted', 'exception']`),
so a first-event-only reduction still finds it. AC12 closes the gap:
its assertion depends on the KEEP FLAG (a buffered SIBLING surviving root
close), not on carrier export — carrier export stays green under the
mutation regardless, since it is decided by the unmutated
`_carries_always_sampled_event`. Parametrized over member position (first /
middle / LAST), mirroring `W15`'s coverage for the sibling function; the
last-position case is the strongest discriminator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from harness_od.sampling_mode import ALWAYS_SAMPLED_EVENT_CLASSES
from harness_od.tail_keep_classification import (
    BREAKER_TRIPPED_SPAN_NAME,
    SANDBOX_VIOLATION_SPAN_NAME,
    SECTION_10_2_EVENT_TRIGGER_NAMES,
    is_classification_trigger,
)
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

#: The carrier span name the real `breaker.tripped` producer uses
#: (`harness_breaker_schema.py:282` calls `parent_span_ref.add_event(...)` on
#: a span named this — never a span literally named `breaker.tripped`).
CARRIER_SPAN_NAME = "harness.runtime.retry_breaker_fallback"


# ---------------------------------------------------------------------------
# AC1 / AC2 — the event-name arm fires on a non-trigger-named carrier.
# ---------------------------------------------------------------------------


def test_ac1_breaker_tripped_event_on_a_non_trigger_named_span_is_a_trigger() -> None:
    """AC1 — a span named `harness.runtime.retry_breaker_fallback` (NOT a §10.2
    trigger name) that carries a `breaker.tripped` EVENT is now a trigger.

    This is the exact production shape: `harness_breaker_schema.py:282` calls
    `parent_span_ref.add_event(name="breaker.tripped", ...)` on the dispatch
    wrapper span, never on a span named `breaker.tripped` itself. Before
    `B-123` this returned False (register row `B-123`'s grounded defect); the
    event-name arm closes it.
    """
    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)
    span = tracer.start_span(CARRIER_SPAN_NAME)
    span.add_event(BREAKER_TRIPPED_SPAN_NAME)
    span.end()
    assert is_classification_trigger(span)  # type: ignore[arg-type]


def test_ac2_sandbox_violation_event_on_a_non_trigger_named_span_is_a_trigger() -> None:
    """AC2 — the `sandbox.violation` sibling of AC1, over the event-name arm.

    **Grounded, not speculative: no production site currently emits
    `sandbox.violation` as an event.** An exhaustive `add_event(` sweep over
    all seven `harness-*/src` trees (register row `B-123` close-out, step 3,
    re-verified for this leg) returns exactly six sites —
    `harness_breaker_schema.py:282` (`breaker.tripped`),
    `alignment_floor_drift_detection.py:242`,
    `retry_breaker_fallback.py:749` (`fallback.triggered`),
    `retry_breaker_fallback.py:879` (`retry.skipped`),
    `retry_breaker_fallback.py:1151` (`fallback.exhausted`), and
    `retry_breaker_tool.py:314` (`tool_retry.exhausted`) — and NONE is named
    `sandbox.violation`. The real `sandbox.violation` producer emits a REAL
    SPAN (`runtime_tool_dispatcher.py:725`,
    `tracer.start_as_current_span("sandbox.violation")`), so this witness
    exists because the CONTRACT (§10.2, lines 582-584) names both triggers as
    event-preservable, not because a producer currently exercises this arm.
    """
    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)
    span = tracer.start_span("arbitrary.carrier")
    span.add_event(SANDBOX_VIOLATION_SPAN_NAME)
    span.end()
    assert is_classification_trigger(span)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC5 — the §10.2 set is NOT the §9.2 set.
# ---------------------------------------------------------------------------


def test_ac5_section_9_2_member_event_is_not_a_section_10_2_trigger() -> None:
    """AC5 — `fallback.exhausted` is a §9.2 always-sampled member (its OWN
    carrier forwards, via the pre-existing `B-133` §9.2.1 arm) but is NOT a
    §10.2 tail-keep trigger: it must NOT set the keep flag, so a buffered
    sibling in the same trace is DROPPED at root close.

    This discriminates `SECTION_10_2_EVENT_TRIGGER_NAMES` (2 names) from
    `ALWAYS_SAMPLED_EVENT_CLASSES` (20 names since OD spec v1.42 row 20, a strict
    superset containing both §10.2 names plus 18 more): a mutation that replaces the former with
    the latter in `is_classification_trigger` would make this event ALSO a
    §10.2 trigger, preserve `sibling.work`, and fail this test (PD-8 probe P2).
    """
    assert "fallback.exhausted" in ALWAYS_SAMPLED_EVENT_CLASSES
    assert "fallback.exhausted" not in SECTION_10_2_EVENT_TRIGGER_NAMES

    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("ac5")

    with tracer.start_as_current_span(CARRIER_SPAN_NAME) as root:
        with tracer.start_as_current_span("sibling.work"):
            pass
        root.add_event("fallback.exhausted")

    names = [s.name for s in exporter.get_finished_spans()]
    assert CARRIER_SPAN_NAME in names  # §9.2 floor delivered (pre-existing arm)
    assert "sibling.work" not in names  # §10.2 NOT triggered — sibling dropped
    assert tail.buffered_trace_count == 0  # the root closed; slot freed either way


# ---------------------------------------------------------------------------
# AC6 — tolerance: zero events never raises; pre-existing verdict unchanged.
# ---------------------------------------------------------------------------


def test_ac6_zero_events_does_not_raise_and_preserves_pre_existing_verdict() -> None:
    """AC6 — a span with zero events must not raise and must return the
    SAME (negative) verdict the predicate returned before the event arm
    existed, mirroring the pre-existing `attrs is None` tolerance.
    """
    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)
    span = tracer.start_span("arbitrary.work")
    span.set_attribute("foo", "bar")
    span.end()
    assert span.events == ()  # precondition: genuinely zero events
    assert not is_classification_trigger(span)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC7 — cheapest-first ordering, asserted structurally (not by timing).
# ---------------------------------------------------------------------------


class _EventAccessForbidden(RuntimeError):
    """Raised if `.events` is read — proves the name arm short-circuited."""


@dataclass
class _NameOnlyFakeSpan:
    """A minimal `ReadableSpan`-shaped double whose `.events` property raises.

    Standing in for a real span lets the test assert STRUCTURALLY that the
    name arm returns before the (expensive) event scan ever reads
    `span.events` — no timing measurement involved.
    """

    name: str
    attributes: dict[str, Any] | None = None

    @property
    def events(self) -> tuple[Any, ...]:
        raise _EventAccessForbidden(
            "is_classification_trigger read span.events despite a name-arm match — "
            "the cheapest-first ordering (name, then attribute, then event scan) is broken"
        )


def test_ac7_name_matching_span_never_touches_events_cheapest_first() -> None:
    """AC7 — a span NAMED `breaker.tripped` returns True via the name arm
    and never reaches the event scan, asserted structurally: `.events` on
    this double raises if accessed at all, so a passing call proves the
    short-circuit rather than merely being consistent with it.
    """
    fake = _NameOnlyFakeSpan(name=BREAKER_TRIPPED_SPAN_NAME)
    assert is_classification_trigger(fake)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC8 — the event-trigger set is DERIVED, not re-literalled.
# ---------------------------------------------------------------------------


def test_ac8_event_trigger_names_are_derived_not_re_literalled() -> None:
    """AC8 — `SECTION_10_2_EVENT_TRIGGER_NAMES` equals the set built FROM the
    two source name constants, so a future rename of either constant reaches
    the event arm by construction rather than drifting silently.

    Structural on purpose (per the arc brief): this only pins that the
    constant EQUALS the two source constants today; it does not (and cannot)
    prove the arm is used correctly — AC1/AC2/AC5 are the behavioural proof
    of that.
    """
    assert SECTION_10_2_EVENT_TRIGGER_NAMES == {
        SANDBOX_VIOLATION_SPAN_NAME,
        BREAKER_TRIPPED_SPAN_NAME,
    }


# ---------------------------------------------------------------------------
# AC11 — `span.events` is read EXACTLY ONCE per `on_end` (out-of-family Codex
# [P2] fix-forward, register row `B-123`). This is the OPPOSITE bound from
# AC7's raising double: not "never touched" but "touched exactly once" for a
# span that DOES reach the event checks — proven at the `TailKeepSpanProcessor
# .on_end` orchestration level with a COUNTING double, since the double-read
# defect was in HOW `on_end` composed `_carries_always_sampled_event` and
# `is_classification_trigger`, not in either function alone.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FakeEvent:
    """A minimal `Event`-shaped double: `.name` + `.attributes`, nothing more."""

    name: str
    attributes: dict[str, Any] | None = None


class _SpanContextDouble:
    """A minimal `SpanContext`-shaped double carrying only `.trace_id`."""

    def __init__(self, trace_id: int) -> None:
        self.trace_id = trace_id


class _EventAccessCountingSpan:
    """A `ReadableSpan`-shaped double whose `.events` PROPERTY increments a
    counter on every access, instead of raising (AC7's technique) — the
    counting sibling that proves the AC11 bound. Implements exactly the
    surface `TailKeepSpanProcessor.on_end` touches (`.name`, `.attributes`,
    `.parent`, `.events`, `.get_span_context()`) and nothing more; every span
    here is a trace root (`.parent = None`) so `on_end` runs to a root-close
    decision without needing a second span.
    """

    def __init__(
        self,
        name: str,
        *,
        events: tuple[_FakeEvent, ...] = (),
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.attributes = attributes
        self.parent = None
        self._events = events
        self.access_count = 0
        self._ctx = _SpanContextDouble(trace_id=0xAC11)

    @property
    def events(self) -> tuple[_FakeEvent, ...]:
        self.access_count += 1
        return self._events

    def get_span_context(self) -> _SpanContextDouble:
        return self._ctx


class _RecordingDownstream:
    """A minimal `SpanProcessor`-shaped downstream double. Deliberately does
    NOT inspect the forwarded span — the AC11 synthetic span doubles above
    implement only what `on_end` itself touches, and a real `SimpleSpanProcessor`
    / `InMemorySpanExporter` would additionally require a `.context` property
    + other `ReadableSpan` surface these doubles do not carry.
    """

    def __init__(self) -> None:
        self.on_end_calls: list[Any] = []

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        pass

    def on_end(self, span: Any) -> None:
        self.on_end_calls.append(span)

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True

    def shutdown(self) -> None:
        pass


@pytest.mark.parametrize(
    ("span_name", "events"),
    [
        ("ac11.ordinary.zero_events", ()),
        ("ac11.ordinary.nonmatching_event", (_FakeEvent("retry.skipped"),)),
        ("ac11.always_sampled_event_carrier", (_FakeEvent("breaker.tripped"),)),
    ],
    ids=["zero-events", "nonmatching-event-ordinary-path", "always-sampled-event-path"],
)
def test_ac11_span_events_is_read_exactly_once_per_on_end(
    span_name: str, events: tuple[_FakeEvent, ...]
) -> None:
    """AC11 — before this fix, a span reaching the event checks paid
    `span.events`'s lock-acquire + deque-copy cost TWICE per `on_end` call:
    once inside `_carries_always_sampled_event`, once inside
    `is_classification_trigger`'s own self-read — for EVERY ordinary span,
    including zero-event ones. This asserts the count is EXACTLY 1, not
    merely small: an assertion of `<= 2` would pass against the very code
    being fixed, so equality is required.

    Three cases, covering both branches `on_end` can take after the single
    read: the ordinary buffer path with zero events, the ordinary buffer
    path with a non-matching event (the scan must still run, just once),
    and the always-sampled-event path (`_carries_always_sampled_event`
    returns True, which ALSO calls `is_classification_trigger` — the exact
    double-call shape Codex flagged).
    """
    tail = TailKeepSpanProcessor(downstream=_RecordingDownstream())  # type: ignore[arg-type]
    span = _EventAccessCountingSpan(span_name, events=events)
    tail.on_end(span)  # type: ignore[arg-type]
    assert span.access_count == 1, (
        f"span.events was accessed {span.access_count} times in one on_end call — "
        "expected EXACTLY 1 per register row B-123's single-read discipline "
        "(out-of-family Codex [P2])"
    )


def test_ac7_confirmed_by_counting_double_zero_events_touches() -> None:
    """AC7 reconfirmation after the single-read refactor, stated as an
    explicit COUNT rather than a raise: a span NAMED `breaker.tripped` is
    ALSO a §9.2 always-sampled member by name, so `on_end`'s first branch
    forwards it and returns before `events = span.events` is ever reached —
    `.events` must be touched ZERO times, at the same `on_end` orchestration
    level AC11 tests, using the SAME counting technique.
    """
    tail = TailKeepSpanProcessor(downstream=_RecordingDownstream())  # type: ignore[arg-type]
    span = _EventAccessCountingSpan(BREAKER_TRIPPED_SPAN_NAME)
    tail.on_end(span)  # type: ignore[arg-type]
    assert span.access_count == 0, (
        f"span.events was accessed {span.access_count} times for a NAME-matching span — "
        "expected ZERO (the name arm must short-circuit before on_end ever reads events)"
    )


# ---------------------------------------------------------------------------
# AC12 — merge-gate BLOCK (test-witness lens): the event scan must examine
# the WHOLE event list, not just the first entry. Unlike AC1/AC2/AC5/AC6/AC7,
# this witness's PASS/FAIL depends on the KEEP FLAG (a buffered sibling
# surviving root close) — carrier export alone (what AC1/AC2/AC5 assert) is
# decided by the SEPARATE, unmutated `_carries_always_sampled_event`, which
# would stay green under a first-event-only reduction of THIS function's scan.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("event_names", "member_index"),
    [
        (("breaker.tripped", "exception"), 0),
        (("retry.skipped", "breaker.tripped", "exception"), 1),
        (("retry.skipped", "exception", "breaker.tripped"), 2),
    ],
    ids=["member-first", "member-middle", "member-last"],
)
def test_ac12_keep_flag_scans_the_whole_event_list_not_just_the_first(
    event_names: tuple[str, ...], member_index: int
) -> None:
    """AC12 — a mutation reducing the event-scan `any(...)` at
    `tail_keep_classification.py` to a FIRST-EVENT-ONLY check slipped through
    the entire pre-AC12 changed test set: every single-function witness
    (AC1/AC2/AC5/AC6/AC7/AC11) uses ≤ 1 event, where `any()` and
    "first event only" cannot be told apart; the one multi-event witness
    reaching this line (`test_w15_...`, `member_index=2`) asserts only carrier
    export + `buffered_trace_count == 0`, both driven by the DIFFERENT
    `_carries_always_sampled_event` §9.2 arm — there is no buffered sibling in
    that trace for the §10.2 keep flag to gate; and AC4/AC4b's real dispatch
    happens to put `breaker.tripped` first in its actual event list, so a
    first-event-only reduction still finds it there too.

    This witness is different: the carrier's NAME is not a §10.2 trigger, it
    carries MULTIPLE events with a non-member (`retry.skipped` — the real
    non-member the dispatcher emits when a candidate's breaker is pre-open,
    per `test_w15_...`/`test_w16_...`'s production grounding) at every
    position BEFORE the §10.2 member, and a plain sibling span closes BEFORE
    the carrier so it BUFFERS. The assertion is on the SIBLING's survival —
    gated by the keep flag `is_classification_trigger` sets — not on the
    carrier's own export (gated by the separate, unmutated
    `_carries_always_sampled_event`, since `breaker.tripped` is BOTH a §9.2
    member and a §10.2 trigger, so the carrier always also takes the
    event-aware arm regardless of this function's verdict).

    Parametrized over member position — first / middle / LAST — mirroring
    `test_w15_...`'s coverage for the sibling function; the last-position
    case is the strongest discriminator (a first-event-only scan cannot find
    a member it never examines).
    """
    # Precondition: every event BEFORE the member is genuinely a non-member,
    # so a passing case cannot be vacuous.
    for name in event_names[:member_index]:
        assert name not in SECTION_10_2_EVENT_TRIGGER_NAMES, f"{name!r} is itself a §10.2 trigger"
    assert event_names[member_index] == BREAKER_TRIPPED_SPAN_NAME

    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("ac12")

    with tracer.start_as_current_span(CARRIER_SPAN_NAME) as root:
        with tracer.start_as_current_span("ac12.sibling.work"):
            pass
        for name in event_names:
            root.add_event(name)

    names = [s.name for s in exporter.get_finished_spans()]
    assert CARRIER_SPAN_NAME in names  # the §9.2 floor — unaffected by this arc's mutation
    assert "ac12.sibling.work" in names, (
        f"the buffered sibling was dropped with the §10.2 member at index {member_index} of "
        f"{event_names!r} — is_classification_trigger's event scan did not find "
        "`breaker.tripped` unless it happened to be first (this is the exact first-event-only "
        "reduction the merge gate's test-witness lens flagged)"
    )
    assert tail.buffered_trace_count == 0


# ---------------------------------------------------------------------------
# PD-8 mutation probes (run manually per the arc brief; not test-encoded —
# see the report for the recorded red/green outcome per probe).
# ---------------------------------------------------------------------------
#
# P1 delete the event-scan arm from `is_classification_trigger`            -> AC1/AC2/AC5(discriminator half) RED
# P2 replace SECTION_10_2_EVENT_TRIGGER_NAMES with ALWAYS_SAMPLED_EVENT_CLASSES -> AC5 RED
# P3 move the event scan to the TOP of the predicate                       -> reported honestly per probe run
# P4 remove SANDBOX_VIOLATION_SPAN_NAME from the event set                 -> AC2 RED
# P6 hard-code SECTION_10_2_EVENT_TRIGGER_NAMES + rename one source constant -> AC8 RED
# P7 (merge-gate BLOCK) reduce the event-scan any(...) to first-event-only  -> AC12 RED (member-middle + member-last cases)

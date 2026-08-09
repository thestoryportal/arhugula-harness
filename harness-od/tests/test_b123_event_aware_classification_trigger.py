"""B-123 — the `is_classification_trigger` §10.2 event-name arm.

Authority: `design-substrate/Spec_Operational_Discipline_v1_2.md` §C-OD-10
§10.2 (lines 582-584, cleared and PRESERVED VERBATIM through the current
head — the contract table already reads "Parent + sibling spans of any
`sandbox.violation` EVENT preserved" / "...`breaker.tripped` EVENT
preserved") + register row `B-123` (the widening this module witnesses is a
conformance repair to that already-cleared text, not a design extension).
Spec delta owed forward at OD spec v1.39 §9.2.1 term 3 (currently v1.38
term 3 DECLINES to widen and names this row); that doc delta is out of
scope for this module.

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

AC3/AC4/AC9/AC10 are proven elsewhere per the arc brief: AC3 at
`test_b133_event_aware_tail_floor.py` (the rewritten `test_w7_...`), AC4 at
`harness-runtime/tests/test_b133_event_aware_tail_floor_real_dispatch.py`
(real-dispatch, no `force_flush`), AC9 (the head-admission bound; do not
overclaim a full floor) stated in this module's + the real-dispatch
witness's docstrings rather than as a separate assertion, AC10 by running
the full suite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
    `ALWAYS_SAMPLED_EVENT_CLASSES` (19 names, a strict superset containing
    both §10.2 names plus 17 more): a mutation that replaces the former with
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
# PD-8 mutation probes (run manually per the arc brief; not test-encoded —
# see the report for the recorded red/green outcome per probe).
# ---------------------------------------------------------------------------
#
# P1 delete the event-scan arm from `is_classification_trigger`            -> AC1/AC2/AC5(discriminator half) RED
# P2 replace SECTION_10_2_EVENT_TRIGGER_NAMES with ALWAYS_SAMPLED_EVENT_CLASSES -> AC5 RED
# P3 move the event scan to the TOP of the predicate                       -> reported honestly per probe run
# P4 remove SANDBOX_VIOLATION_SPAN_NAME from the event set                 -> AC2 RED
# P6 hard-code SECTION_10_2_EVENT_TRIGGER_NAMES + rename one source constant -> AC8 RED

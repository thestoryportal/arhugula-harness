"""Tests for U-OD-09 — `harness.breaker.*` 9-attribute canonical schema.

Test set per the U-OD-09 §3.3.1 (v2.8) `Tests:` field — covers acceptance
#1/#3-#10 against C-OD-07 §7.1 / §7.2 / §7.3. acc #2 is STRUCK (v2.8 D-3) —
no test; the `test_required_tier_*` / `test_conditional_tier_*` tests are
struck. v1.32 (B-19-BREAKER-AMBIENT-ATTRS) added `cause` + `cooldown_ms`
(7 -> 9 attributes); tests below updated + 2 new tests added for the pair.
"""

from __future__ import annotations

import pytest
from harness_od.harness_breaker_schema import (
    HARNESS_BREAKER_ATTRIBUTES,
    BreakerCause,
    BreakerEmissionError,
    BreakerScope,
    BreakerState,
    HarnessBreakerEvent,
    emit_breaker_trip_span_event,
)
from harness_od.otel_genai_base import EventEmission, SpanRef
from opentelemetry.sdk.trace import TracerProvider

_EXPECTED_ATTRIBUTES: tuple[str, ...] = (
    "harness.breaker.scope",
    "harness.breaker.from_state",
    "harness.breaker.to_state",
    "harness.breaker.trigger_count",
    "harness.breaker.permanent_fail_repeats",
    "harness.breaker.tool_id",
    "harness.breaker.model_version",
    "harness.breaker.cause",
    "harness.breaker.cooldown_ms",
)


def _span() -> SpanRef:
    """An OTel-SDK span handle — the U-OD-04 `SpanRef` carrier substrate."""
    return TracerProvider().get_tracer("u-od-09-test").start_span("parent")


def _full_event() -> HarnessBreakerEvent:
    """A `HarnessBreakerEvent` with all nine attributes populated."""
    return HarnessBreakerEvent(
        scope=BreakerScope.PER_MODEL,
        from_state=BreakerState.CLOSED,
        to_state=BreakerState.OPEN,
        trigger_count=5,
        permanent_fail_repeats=3,
        tool_id="tool::search",
        model_version="claude-opus-4-7",
        cause=BreakerCause.RATE_LIMIT,
        cooldown_ms=30000,
    )


# --- acc #1 ----------------------------------------------------------------
def test_harness_breaker_attributes_cardinality_nine() -> None:
    """`HARNESS_BREAKER_ATTRIBUTES` declares exactly 9 attribute names per §7.1."""
    assert len(HARNESS_BREAKER_ATTRIBUTES) == 9


def test_harness_breaker_attribute_names_byte_exact() -> None:
    """Attribute names are byte-exact against the §7.1 table (9 rows)."""
    assert HARNESS_BREAKER_ATTRIBUTES == _EXPECTED_ATTRIBUTES


def test_harness_breaker_attributes_typed_list_of_string() -> None:
    """`HARNESS_BREAKER_ATTRIBUTES` is a tuple of `str` (v2.8 D-3 re-typing)."""
    assert all(isinstance(name, str) for name in HARNESS_BREAKER_ATTRIBUTES)


# --- acc #3 ----------------------------------------------------------------
def test_breaker_scope_cardinality_two() -> None:
    """`BreakerScope` enumerates exactly 2 values per §7.1."""
    assert len(BreakerScope) == 2


def test_breaker_scope_names_per_model_per_provider() -> None:
    """`BreakerScope` values are `per_model` / `per_provider` per §7.1 verbatim."""
    assert {s.value for s in BreakerScope} == {"per_model", "per_provider"}


# --- v1.32 NEW: cause + cooldown_ms ------------------------------------------
def test_breaker_cause_cardinality_four() -> None:
    """`BreakerCause` enumerates exactly 4 values per §7.1 (v1.32 NEW)."""
    assert len(BreakerCause) == 4
    assert {c.value for c in BreakerCause} == {
        "rate_limit",
        "auth_failure",
        "5xx_streak",
        "capability_shortfall",
    }


def test_harness_breaker_event_cause_and_cooldown_ms_default_none() -> None:
    """`cause` / `cooldown_ms` default `None` — both optional (v1.32 NEW)."""
    event = HarnessBreakerEvent(
        scope=BreakerScope.PER_MODEL,
        from_state=BreakerState.CLOSED,
        to_state=BreakerState.OPEN,
        trigger_count=1,
    )
    assert event.cause is None
    assert event.cooldown_ms is None


def test_emit_breaker_trip_cause_and_cooldown_ms_populate_attribute_count() -> None:
    """Populated `cause` + `cooldown_ms` each count toward `attribute_count`."""
    cause_only = HarnessBreakerEvent(
        scope=BreakerScope.PER_MODEL,
        from_state=BreakerState.CLOSED,
        to_state=BreakerState.OPEN,
        trigger_count=1,
        cause=BreakerCause.AUTH_FAILURE,
    )
    emission = emit_breaker_trip_span_event(_span(), cause_only)
    assert emission.attribute_count == 5  # 4 non-optional + cause

    cooldown_only = HarnessBreakerEvent(
        scope=BreakerScope.PER_MODEL,
        from_state=BreakerState.CLOSED,
        to_state=BreakerState.OPEN,
        trigger_count=1,
        cooldown_ms=15000,
    )
    emission = emit_breaker_trip_span_event(_span(), cooldown_only)
    assert emission.attribute_count == 5  # 4 non-optional + cooldown_ms


# --- acc #4 ----------------------------------------------------------------
def test_breaker_state_cardinality_three() -> None:
    """`BreakerState` enumerates exactly 3 values per §7.1."""
    assert len(BreakerState) == 3
    assert {s.value for s in BreakerState} == {"closed", "open", "half_open"}


# --- acc #9 — emission accepts all-nine; rejects missing required ----------
def test_emit_breaker_trip_with_all_nine_attrs_accept() -> None:
    """`emit_breaker_trip_span_event` emits when all attributes populate."""
    emission = emit_breaker_trip_span_event(_span(), _full_event())
    assert isinstance(emission, EventEmission)
    assert emission.event_name == "breaker.tripped"
    assert emission.attribute_count == 9


def test_emit_breaker_trip_missing_required_attr_reject() -> None:
    """Emission raises `BreakerEmissionError` if a non-optional attr is missing.

    The four non-optional fields (`scope` / `from_state` / `to_state` /
    `trigger_count`) are required by Pydantic at construction; a model bypassing
    construction with one set to `None` is rejected by the emission guard.
    """
    for attribute_name in ("scope", "from_state", "to_state", "trigger_count"):
        bad = _full_event().model_copy(update={attribute_name: None})
        with pytest.raises(BreakerEmissionError):
            emit_breaker_trip_span_event(_span(), bad)


# --- acc #5 ----------------------------------------------------------------
def test_breaker_event_always_sampled_at_all_cells() -> None:
    """`breaker.tripped` emission is always-sampled per §7.2 (acc #5)."""
    emission = emit_breaker_trip_span_event(_span(), _full_event())
    assert emission.sampled is True


def test_breaker_attributes_cardinality_safe() -> None:
    """Breaker attributes are cardinality-safe per §7.2 (acc #5).

    Per-attribute cardinality is bounded by `BreakerScope` (2) x `BreakerState`
    (3) x bounded integers — no payload content. The optional event attributes
    are absorbed when `None`, so the emission attribute count is bounded by 7.
    """
    minimal = HarnessBreakerEvent(
        scope=BreakerScope.PER_PROVIDER,
        from_state=BreakerState.HALF_OPEN,
        to_state=BreakerState.OPEN,
        trigger_count=1,
    )
    emission = emit_breaker_trip_span_event(_span(), minimal)
    assert emission.attribute_count == 4


# --- acc #8 ----------------------------------------------------------------
def test_cross_axis_export_to_u_cp_54_section_24_1_c_declared() -> None:
    """Cross-axis export edge to U-CP-54 / C-CP-24 §24.1.C is declared (acc #8)."""
    from harness_od import harness_breaker_schema as mod

    assert mod.__doc__ is not None
    assert "U-CP-54" in mod.__doc__
    assert "C-CP-24 §24.1.C" in mod.__doc__


# --- acc #7 ----------------------------------------------------------------
def test_substrate_anchored_outside_cp_per_f_cp_01_stage_3b() -> None:
    """The schema is substrate-anchored at OD per F-CP-01 Stage 3b (acc #7)."""
    from harness_od import harness_breaker_schema as mod

    assert mod.__doc__ is not None
    assert "F-CP-01 Stage 3b" in mod.__doc__


# --- acc #10 ---------------------------------------------------------------
def test_span_ref_event_emission_resolve_to_u_od_04_carrier() -> None:
    """`parent_span_ref` / return resolve to the U-OD-04 OTel-handle family.

    v2.6 M-1 / acc #10 — no `Span*` type is materialized inside U-OD-09; the
    emission consumes `SpanRef` and returns `EventEmission`, both from
    `otel_genai_base` (U-OD-04).
    """
    span = _span()
    assert isinstance(span, SpanRef.__value__)
    emission = emit_breaker_trip_span_event(span, _full_event())
    assert isinstance(emission, EventEmission)
    assert emission.emitted_at_span is span

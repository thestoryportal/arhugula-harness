"""Tests for B-OD18-DRIFT-ALGORITHM — per-primitive drift computation +
re-baselining workflow + eval-kind SDK-boundary enforcement.

Acceptance per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §4
B-OD18-DRIFT-ALGORITHM: "Synthetic-window drift witness (floor breach ->
event with correct 4-attr set; no breach -> silence); re-baseline round-trip;
eval-kind guard fail-closed test."
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
from harness_od.alignment_floor_drift_algorithm import (
    NotSpanDerivableError,
    compute_current_value,
    rebaseline_threshold,
    run_drift_check,
)
from harness_od.alignment_floor_drift_detection import (
    DRIFT_DETECTED_ATTRIBUTE_NAMES,
    DRIFT_DETECTED_EVENT_NAME,
    AlignmentFloorPrimitive,
    AlignmentFloorThreshold,
    ObservationWindow,
    ObservationWindowKind,
)
from harness_od.eval_vs_runtime_gate import (
    EvalKindDiscriminator,
    EvalShapeViolation,
    EvalSpanRouting,
    validate_eval_span_routing,
)
from harness_od.operator_burden_eval_primitives import (
    OperatorBurdenEvalPrimitive,
    emit_eval_as_child_span,
)
from harness_od.otel_genai_base import SpanRef
from harness_od.sqlite_span_store import SpanInsertRow, initialize_span_store, insert_spans
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_NS_PER_S = 1_000_000_000


def _span(
    span_id: str, start_time_ns: int, attributes: dict[str, object] | None = None
) -> SpanInsertRow:
    return SpanInsertRow(
        span_id=span_id,
        trace_id=f"trace-{span_id}",
        parent_span_id=None,
        name="chat claude-sonnet-5",
        kind=0,
        start_time_ns=start_time_ns,
        end_time_ns=start_time_ns + 1,
        status_code=0,
        status_message=None,
        attributes_json=json.dumps(attributes or {}),
        events_json="[]",
        workflow_id=None,
        workflow_run_id=None,
        workflow_idempotency_key=None,
    )


@pytest.fixture()
def conn(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    c = initialize_span_store(tmp_path / "spans.db")
    yield c
    c.close()


def _parent_span() -> SpanRef:
    return TracerProvider().get_tracer("b-od18-test").start_span("parent")


def _time_window(seconds: float) -> ObservationWindow:
    return ObservationWindow(kind=ObservationWindowKind.TIME_WINDOW, time_window_seconds=seconds)


def _sample_window(count: int) -> ObservationWindow:
    return ObservationWindow(kind=ObservationWindowKind.SAMPLE_WINDOW, sample_window_count=count)


# ---------------------------------------------------------------------------
# compute_current_value — span-derivable vs judge-scored primitives.
# ---------------------------------------------------------------------------


def test_not_span_derivable_for_judge_kappa(conn: sqlite3.Connection) -> None:
    with pytest.raises(NotSpanDerivableError):
        compute_current_value(
            conn,
            AlignmentFloorPrimitive.JUDGE_HUMAN_COHENS_KAPPA,
            _sample_window(10),
            now_ns=0,
        )


def test_not_span_derivable_for_routing_accuracy_holdout(conn: sqlite3.Connection) -> None:
    with pytest.raises(NotSpanDerivableError):
        compute_current_value(
            conn,
            AlignmentFloorPrimitive.ROUTING_ACCURACY_HOLDOUT,
            _sample_window(10),
            now_ns=0,
        )


def test_not_span_derivable_for_sandbox_tier_routing_accuracy(conn: sqlite3.Connection) -> None:
    with pytest.raises(NotSpanDerivableError):
        compute_current_value(
            conn,
            AlignmentFloorPrimitive.SANDBOX_TIER_ROUTING_ACCURACY,
            _sample_window(10),
            now_ns=0,
        )


def test_cache_hit_rate_computed_from_spans(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span(
                "a",
                0,
                {
                    "anthropic.cache_read_input_tokens": 80,
                    "anthropic.cache_creation_input_tokens": 20,
                },
            )
        ],
    )
    value = compute_current_value(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        _time_window(3600),
        now_ns=1,
    )
    assert value == pytest.approx(0.8)


def test_cache_hit_rate_none_when_no_cache_data(conn: sqlite3.Connection) -> None:
    insert_spans(conn, [_span("a", 0, {})])
    value = compute_current_value(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        _time_window(3600),
        now_ns=1,
    )
    assert value is None


# ---------------------------------------------------------------------------
# Window scoping — TIME_WINDOW and SAMPLE_WINDOW exclude out-of-window spans.
# ---------------------------------------------------------------------------


def test_time_window_excludes_old_spans(conn: sqlite3.Connection) -> None:
    now_ns = 1000 * _NS_PER_S
    insert_spans(
        conn,
        [
            # Outside the 60s window (1000s ago): all-cache-read, would
            # dominate the ratio to 1.0 if wrongly included.
            _span(
                "old",
                0,
                {
                    "anthropic.cache_read_input_tokens": 1000,
                    "anthropic.cache_creation_input_tokens": 0,
                },
            ),
            # Inside the window (5s ago): 50/50 split.
            _span(
                "new",
                now_ns - 5 * _NS_PER_S,
                {
                    "anthropic.cache_read_input_tokens": 50,
                    "anthropic.cache_creation_input_tokens": 50,
                },
            ),
        ],
    )
    value = compute_current_value(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        _time_window(60),
        now_ns=now_ns,
    )
    assert value == pytest.approx(0.5)


def test_sample_window_keeps_only_most_recent_n(conn: sqlite3.Connection) -> None:
    rows = [
        _span(
            f"s{i}",
            i,
            {"anthropic.cache_read_input_tokens": 0, "anthropic.cache_creation_input_tokens": 10},
        )
        for i in range(5)
    ]
    # The most recent row is all cache-read; the other 4 are all cache-creation.
    rows[-1] = _span(
        "s4",
        4,
        {"anthropic.cache_read_input_tokens": 10, "anthropic.cache_creation_input_tokens": 0},
    )
    insert_spans(conn, rows)
    value = compute_current_value(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        _sample_window(1),
        now_ns=0,
    )
    assert value == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Synthetic-window drift witness — floor breach emits; no breach is silent.
# ---------------------------------------------------------------------------


def test_floor_breach_emits_drift_event_with_correct_attrs(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span(
                "a",
                0,
                {
                    "anthropic.cache_read_input_tokens": 10,
                    "anthropic.cache_creation_input_tokens": 90,
                },
            )
        ],
    )
    threshold = AlignmentFloorThreshold(
        primitive=AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        threshold_value=0.5,
        observation_window=_time_window(3600),
    )
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    parent = provider.get_tracer("b-od18-test").start_span("parent")

    emission = run_drift_check(
        conn, AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR, threshold, parent, now_ns=1
    )
    parent.end()

    assert emission is not None
    assert emission.event_name == DRIFT_DETECTED_EVENT_NAME
    assert emission.attribute_count == len(DRIFT_DETECTED_ATTRIBUTE_NAMES)
    assert emission.sampled is True


def test_no_breach_is_silent(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span(
                "a",
                0,
                {
                    "anthropic.cache_read_input_tokens": 90,
                    "anthropic.cache_creation_input_tokens": 10,
                },
            )
        ],
    )
    threshold = AlignmentFloorThreshold(
        primitive=AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        threshold_value=0.5,
        observation_window=_time_window(3600),
    )
    emission = run_drift_check(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        threshold,
        _parent_span(),
        now_ns=1,
    )
    assert emission is None


def test_no_data_in_window_is_silent(conn: sqlite3.Connection) -> None:
    threshold = AlignmentFloorThreshold(
        primitive=AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        threshold_value=0.9,
        observation_window=_time_window(3600),
    )
    emission = run_drift_check(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        threshold,
        _parent_span(),
        now_ns=1,
    )
    assert emission is None


def test_judge_scored_primitive_requires_supplied_value(conn: sqlite3.Connection) -> None:
    threshold = AlignmentFloorThreshold(
        primitive=AlignmentFloorPrimitive.JUDGE_HUMAN_COHENS_KAPPA,
        threshold_value=0.8,
        observation_window=_sample_window(10),
    )
    with pytest.raises(ValueError, match="judge_supplied_current_value"):
        run_drift_check(
            conn,
            AlignmentFloorPrimitive.JUDGE_HUMAN_COHENS_KAPPA,
            threshold,
            _parent_span(),
            now_ns=0,
        )


def test_judge_scored_primitive_breach_with_supplied_value(conn: sqlite3.Connection) -> None:
    threshold = AlignmentFloorThreshold(
        primitive=AlignmentFloorPrimitive.JUDGE_HUMAN_COHENS_KAPPA,
        threshold_value=0.8,
        observation_window=_sample_window(10),
    )
    emission = run_drift_check(
        conn,
        AlignmentFloorPrimitive.JUDGE_HUMAN_COHENS_KAPPA,
        threshold,
        _parent_span(),
        now_ns=0,
        judge_supplied_current_value=0.5,
    )
    assert emission is not None
    assert emission.event_name == DRIFT_DETECTED_EVENT_NAME


# ---------------------------------------------------------------------------
# Re-baseline round-trip.
# ---------------------------------------------------------------------------


def test_rebaseline_round_trip_resolves_drift(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span(
                "a",
                0,
                {
                    "anthropic.cache_read_input_tokens": 60,
                    "anthropic.cache_creation_input_tokens": 40,
                },
            )
        ],
    )
    window = _time_window(3600)
    # Original threshold (0.9) drifts against the observed 0.6 ratio.
    original = AlignmentFloorThreshold(
        primitive=AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        threshold_value=0.9,
        observation_window=window,
    )
    from harness_od.alignment_floor_drift_detection import detect_drift

    assert (
        detect_drift(AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR, 0.6, original)
        is not None
    )

    # Re-baseline to 0.5 (below the observed 0.6) — should resolve the drift.
    result = rebaseline_threshold(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        0.5,
        window,
        now_ns=1,
    )
    assert result.new_threshold.threshold_value == 0.5
    assert result.recomputed_current_value == pytest.approx(0.6)
    assert result.still_drifting is False


def test_rebaseline_can_still_drift(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span(
                "a",
                0,
                {
                    "anthropic.cache_read_input_tokens": 10,
                    "anthropic.cache_creation_input_tokens": 90,
                },
            )
        ],
    )
    window = _time_window(3600)
    result = rebaseline_threshold(
        conn,
        AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
        0.5,
        window,
        now_ns=1,
    )
    assert result.recomputed_current_value == pytest.approx(0.1)
    assert result.still_drifting is True


def test_rebaseline_judge_scored_primitive_with_supplied_value(conn: sqlite3.Connection) -> None:
    result = rebaseline_threshold(
        conn,
        AlignmentFloorPrimitive.ROUTING_ACCURACY_HOLDOUT,
        0.85,
        _sample_window(10),
        now_ns=0,
        judge_supplied_current_value=0.9,
    )
    assert result.recomputed_current_value == 0.9
    assert result.still_drifting is False


# ---------------------------------------------------------------------------
# Eval-kind SDK-boundary enforcement — reachable guard + fail-closed.
# ---------------------------------------------------------------------------


def test_emit_eval_as_child_span_sets_eval_kind_offline_judge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The one production-reachable call site now emits `gen_ai.eval.kind`,
    previously never set anywhere in the codebase.

    `emit_eval_as_child_span` resolves its tracer via
    `opentelemetry.trace.get_tracer_provider()` — the process-global OTel-SDK
    provider (C-OD-04 §4.4), set once at real runtime startup. Nothing in
    this test process sets it, so the un-patched global default hands back a
    no-op span with no recorded attributes; `monkeypatch` binds it to a real
    `TracerProvider` for the duration of this test only (auto-reverted after,
    no cross-test global-state leakage) so the returned child span is a real,
    inspectable SDK span."""
    import opentelemetry.trace as otel_trace_module

    monkeypatch.setattr(otel_trace_module, "get_tracer_provider", lambda: TracerProvider())

    parent = _parent_span()
    child = emit_eval_as_child_span(
        parent, OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT, 0.9
    )
    parent.end()

    assert child.attributes is not None
    assert child.attributes["gen_ai.eval.kind"] == "offline_judge"
    assert child.attributes["eval.primitive"] == "routing_accuracy_holdout"


def test_eval_kind_guard_fails_closed_on_offline_judge_via_inline_path() -> None:
    """The same guard `emit_eval_as_child_span` calls rejects an `offline_judge`
    routing that was NOT emitted as a child span (the "inline path" the
    C-OD-18 §18.3 acceptance criterion names) — proving the guard is
    load-bearing, not decorative, at the one production-reachable site."""
    with pytest.raises(EvalShapeViolation, match="separate child span"):
        validate_eval_span_routing(
            EvalKindDiscriminator.OFFLINE_JUDGE,
            _parent_span(),
            EvalSpanRouting(
                emitted_as_child_span=False,
                has_validator_fail_attributes=False,
                has_operator_burden_eval_reference=True,
            ),
        )

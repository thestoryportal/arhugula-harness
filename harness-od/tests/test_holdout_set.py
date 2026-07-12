"""Tests for B-OD17-EVAL-LOOP-TOOLING — holdout-set construction.

Acceptance per `.harness/r-fs-2-final-closure-implementation-plan-v1.md`
§3 B-OD17-EVAL-LOOP-TOOLING: "Holdout determinism witness; review round-trip
persists; zero model calls in the loop (control assert)." This file covers
the determinism witness + the sampler's own validation/edge behavior; the
round-trip + zero-model-calls assertions live in
`test_holdout_review_ledger.py` / `test_holdout_end_to_end_loop.py`.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
from harness_core import DeploymentSurface, PersonaTier
from harness_od.holdout_set import (
    HoldoutSet,
    NotHoldoutEvaluableError,
    WrongLoopBindingError,
    read_holdout_set,
    sample_holdout_traces,
    write_holdout_set,
)
from harness_od.observability_matrix import EXCLUDED_CELL, CellBindingViolation, CellID
from harness_od.operator_burden_eval_primitives import OperatorBurdenEvalPrimitive
from harness_od.sqlite_span_store import SpanInsertRow, initialize_span_store, insert_spans

_SOLO_LOCAL = CellID(
    persona_tier=PersonaTier.SOLO_DEVELOPER, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT
)
_TEAM_LOCAL = CellID(
    persona_tier=PersonaTier.TEAM_BINDING, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT
)


def _span(trace_id: str, span_id: str) -> SpanInsertRow:
    return SpanInsertRow(
        span_id=span_id,
        trace_id=trace_id,
        parent_span_id=None,
        name="meta-eval",
        kind=0,
        start_time_ns=0,
        end_time_ns=1,
        status_code=0,
        status_message=None,
        attributes_json="{}",
        events_json="[]",
        workflow_id=None,
        workflow_run_id=None,
        workflow_idempotency_key=None,
    )


@pytest.fixture()
def conn(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    c = initialize_span_store(tmp_path / "spans.db")
    # 10 distinct traces, 2 spans each.
    for i in range(10):
        trace_id = f"trace-{i:02d}"
        insert_spans(c, [_span(trace_id, f"{trace_id}-a"), _span(trace_id, f"{trace_id}-b")])
    yield c
    c.close()


# ---------------------------------------------------------------------------
# Determinism witness.
# ---------------------------------------------------------------------------


def test_same_seed_yields_identical_holdout_set(conn: sqlite3.Connection) -> None:
    kwargs = dict(
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.SANDBOX_TIER_ROUTING_ACCURACY,
        n=4,
        seed=42,
        sampled_at="2026-07-12T00:00:00Z",
    )
    first = sample_holdout_traces(conn, **kwargs)
    second = sample_holdout_traces(conn, **kwargs)
    assert first == second
    assert [t.trace_id for t in first.traces] == [t.trace_id for t in second.traces]


def test_different_seed_can_yield_different_selection(conn: sqlite3.Connection) -> None:
    a = sample_holdout_traces(
        conn,
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.SANDBOX_TIER_ROUTING_ACCURACY,
        n=4,
        seed=1,
        sampled_at="t",
    )
    b = sample_holdout_traces(
        conn,
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.SANDBOX_TIER_ROUTING_ACCURACY,
        n=4,
        seed=2,
        sampled_at="t",
    )
    assert {t.trace_id for t in a.traces} != {t.trace_id for t in b.traces}


def test_sample_size_and_span_counts(conn: sqlite3.Connection) -> None:
    holdout = sample_holdout_traces(
        conn,
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
        n=3,
        seed=7,
        sampled_at="t",
    )
    assert len(holdout.traces) == 3
    assert len(set(t.trace_id for t in holdout.traces)) == 3
    assert all(t.span_count == 2 for t in holdout.traces)


def test_n_larger_than_available_traces_returns_all(conn: sqlite3.Connection) -> None:
    holdout = sample_holdout_traces(
        conn,
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
        n=1000,
        seed=1,
        sampled_at="t",
    )
    assert len(holdout.traces) == 10


def test_empty_store_yields_empty_holdout(tmp_path: Path) -> None:
    conn = initialize_span_store(tmp_path / "empty.db")
    holdout = sample_holdout_traces(
        conn,
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
        n=5,
        seed=1,
        sampled_at="t",
    )
    conn.close()
    assert holdout.traces == ()


# ---------------------------------------------------------------------------
# Validation.
# ---------------------------------------------------------------------------


def test_non_holdout_evaluable_primitive_rejected(conn: sqlite3.Connection) -> None:
    with pytest.raises(NotHoldoutEvaluableError):
        sample_holdout_traces(
            conn,
            cell_id=_SOLO_LOCAL,
            primitive=OperatorBurdenEvalPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR,
            n=4,
            seed=1,
            sampled_at="t",
        )


def test_excluded_cell_rejected(conn: sqlite3.Connection) -> None:
    with pytest.raises(CellBindingViolation):
        sample_holdout_traces(
            conn,
            cell_id=EXCLUDED_CELL,
            primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
            n=4,
            seed=1,
            sampled_at="t",
        )


def test_non_ring_buffer_cell_rejected(conn: sqlite3.Connection) -> None:
    """Only solo-developer cells bind the Husain loop to the sqlite ring
    buffer (C-OD-17 §17.3 row 1); team-binding cells bind to a cell-committed
    backend this sampler never reads — a team `cell_id` must be rejected, not
    silently sampled from the ring buffer as if it were authoritative."""
    with pytest.raises(WrongLoopBindingError):
        sample_holdout_traces(
            conn,
            cell_id=_TEAM_LOCAL,
            primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
            n=4,
            seed=1,
            sampled_at="t",
        )


# ---------------------------------------------------------------------------
# Persistence round-trip.
# ---------------------------------------------------------------------------


def test_write_then_read_round_trips_byte_identical(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    holdout = sample_holdout_traces(
        conn,
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.SANDBOX_TIER_ROUTING_ACCURACY,
        n=3,
        seed=9,
        sampled_at="2026-07-12T00:00:00Z",
    )
    path = tmp_path / "holdout" / "sample.json"
    write_holdout_set(holdout, path)
    reloaded: HoldoutSet = read_holdout_set(path)
    assert reloaded == holdout

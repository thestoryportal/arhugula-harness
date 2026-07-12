"""Deterministic holdout-set construction — B-OD17-EVAL-LOOP-TOOLING.

Implements the holdout-set-construction half of C-OD-17 §17.3's deferred
"specific holdout-set construction protocol per primitive" — the two
holdout-evaluable primitives (`sandbox_tier_routing_accuracy`,
`routing_accuracy_holdout`, per `operator_burden_eval_primitives`) need a
sampled set of traces an operator can manually review; §17.3 names the
protocol as implementation discretion, not the primitive set or the
solo-developer TUI-ring-buffer binding, both of which are already declared
(`operator_burden_eval_primitives.py` / `operator_burden_eval_dashboard_binding.py`).

This module is the sampler half of the Husain manual-review -> categorize ->
automate -> align loop (`HusainLoopState.iteration_phase == "manual-review"`,
the opening phase `run_husain_loop_at_cell` returns): pull the distinct trace
ids present in the sqlite ring buffer, draw a deterministic sample of `n` of
them keyed by an explicit seed, and persist the sample as a versioned JSON
holdout file the review loop (`holdout_review_ledger.py`) walks.

Hard boundary (`[[eval-harness-refused-as-governance-gate]]`): this module
computes NO judge/alignment ratio and makes NO model calls — it only selects
and records which traces are in scope for the operator's manual review.

Scope notes:

- Solo-developer cells only. Per C-OD-17 §17.3 row 1, the sqlite-ring-buffer
  binding is `HusainLoopBinding.RING_BUFFER_OPERATOR_SELF_CURATION`, which
  only solo-developer cells carry; team-binding and multi-tenant-compliance
  cells bind to a cell-committed backend this module never reads.
  `sample_holdout_traces` enforces this via `run_husain_loop_at_cell` and
  raises `WrongLoopBindingError` for any other cell.
- Primitive-agnostic sampling in v1. `primitive` is validated as
  holdout-evaluable and carried on the persisted `HoldoutSet`, but does not
  influence *which* traces are drawn — both holdout-evaluable primitives get
  the identical sample for a given `(cell_id, seed)`. Per-primitive
  construction is deferred to implementation discretion per §17.3, same as
  the rest of this module's scope.
- The sqlite ring buffer this module reads (`sqlite_span_store_reader`) has
  no production writer as of this arc — see B-OD19-LOCAL-INSPECTION's
  reconciliation note. This tooling is verified against seeded test data; the
  composed chain (real spans -> holdout -> review -> assertion) is not yet
  live in production until a production span-emission path exists.
"""

from __future__ import annotations

import json
import random
import sqlite3
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from harness_od.observability_matrix import CellID
from harness_od.operator_burden_eval_dashboard_binding import (
    HusainLoopBinding,
    run_husain_loop_at_cell,
)
from harness_od.operator_burden_eval_primitives import (
    EVAL_PRIMITIVE_DECLARATIONS,
    OperatorBurdenEvalPrimitive,
)
from harness_od.sqlite_span_store_reader import read_all_spans

__all__ = [
    "HoldoutSet",
    "HoldoutTraceRef",
    "NotHoldoutEvaluableError",
    "WrongLoopBindingError",
    "read_holdout_set",
    "sample_holdout_traces",
    "write_holdout_set",
]


class NotHoldoutEvaluableError(Exception):
    """Raised when a holdout set is requested for a non-holdout-evaluable primitive.

    Only `sandbox_tier_routing_accuracy` and `routing_accuracy_holdout` are
    declared `holdout_evaluable=True` (C-OD-17 §17.1); the other three
    primitives are counter/ratio rollups with no meta-judge dimension.
    """


class WrongLoopBindingError(Exception):
    """Raised when a cell's Husain-loop binding isn't ring-buffer self-curation.

    Per C-OD-17 §17.3 row 1, only solo-developer cells bind the Husain loop to
    the sqlite ring buffer with operator self-curation
    (`HusainLoopBinding.RING_BUFFER_OPERATOR_SELF_CURATION`); team-binding and
    multi-tenant-compliance cells bind to a cell-committed backend instead.
    This sampler only ever reads the ring buffer, so it is scoped to
    solo-developer cells — a team/multi-tenant `cell_id` is a caller mistake,
    not a case this module silently handles.
    """


class HoldoutTraceRef(BaseModel):
    """One sampled trace in a holdout set. Frozen -> `Eq`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    trace_id: str
    #: number of spans belonging to this trace at sample time (informational —
    #: lets the review loop show the operator how much material there is
    #: without a second store read).
    span_count: int


class HoldoutSet(BaseModel):
    """A versioned, deterministically-sampled holdout set (C-OD-17 §17.3).

    Frozen -> `Eq`, JSON-round-trippable via `write_holdout_set` /
    `read_holdout_set`. `seed` + `sampled_at` are the version identity — two
    `HoldoutSet`s with the same seed sampled from the same store snapshot are
    byte-identical (the determinism witness the acceptance criterion names).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    cell_id: CellID
    primitive: OperatorBurdenEvalPrimitive
    seed: int
    #: operator-supplied version label (e.g. an ISO timestamp or a run id) —
    #: carried verbatim, not derived, so re-sampling with the same seed at a
    #: later time does not silently collide with an earlier holdout file.
    sampled_at: str
    traces: tuple[HoldoutTraceRef, ...]


def _reject_not_holdout_evaluable(primitive: OperatorBurdenEvalPrimitive) -> None:
    declaration = next(d for d in EVAL_PRIMITIVE_DECLARATIONS if d.primitive is primitive)
    if not declaration.holdout_evaluable:
        raise NotHoldoutEvaluableError(
            f"{primitive.value} is not holdout-evaluable per C-OD-17 §17.1 "
            "(holdout_evaluable=False) — only sandbox_tier_routing_accuracy "
            "and routing_accuracy_holdout take a holdout set"
        )


def sample_holdout_traces(
    conn: sqlite3.Connection,
    *,
    cell_id: CellID,
    primitive: OperatorBurdenEvalPrimitive,
    n: int,
    seed: int,
    sampled_at: str,
) -> HoldoutSet:
    """Draw a deterministic sample of up to `n` distinct traces from `conn`.

    Determinism: trace ids present in the store are sorted lexicographically
    (a stable, store-order-independent base ordering) before
    `random.Random(seed).sample(...)` draws from them — the same `seed` over
    the same store snapshot always yields the same trace-id selection, in the
    same order, regardless of the sqlite row-scan order. When fewer than `n`
    distinct traces exist, every trace is included (no error — a small ring
    buffer is an expected early-lifecycle state, not a caller mistake).

    Raises `CellBindingViolation` (via `run_husain_loop_at_cell`) if `cell_id`
    is the structurally-excluded cell, `WrongLoopBindingError` if `cell_id`'s
    Husain-loop binding isn't ring-buffer self-curation (only solo-developer
    cells bind there — this sampler only ever reads the ring buffer), and
    `NotHoldoutEvaluableError` if `primitive` is not holdout-evaluable — all
    three are validation, not sampling.
    """
    loop_state = run_husain_loop_at_cell(cell_id, primitive)
    if loop_state.loop_binding is not HusainLoopBinding.RING_BUFFER_OPERATOR_SELF_CURATION:
        raise WrongLoopBindingError(
            f"{cell_id} binds the Husain loop to {loop_state.loop_binding.value}, "
            "not RING_BUFFER_OPERATOR_SELF_CURATION — this sampler only reads "
            "the sqlite ring buffer and is scoped to solo-developer cells "
            "(C-OD-17 §17.3 row 1)"
        )
    _reject_not_holdout_evaluable(primitive)

    rows = read_all_spans(conn)
    span_counts: dict[str, int] = {}
    for row in rows:
        span_counts[row.trace_id] = span_counts.get(row.trace_id, 0) + 1

    ordered_trace_ids = sorted(span_counts)
    k = min(n, len(ordered_trace_ids))
    selected = random.Random(seed).sample(ordered_trace_ids, k=k) if k else []

    traces = tuple(
        HoldoutTraceRef(trace_id=trace_id, span_count=span_counts[trace_id])
        for trace_id in selected
    )
    return HoldoutSet(
        cell_id=cell_id,
        primitive=primitive,
        seed=seed,
        sampled_at=sampled_at,
        traces=traces,
    )


def write_holdout_set(holdout: HoldoutSet, path: Path) -> None:
    """Write `holdout` to `path` as indented, sorted-key JSON.

    Creates parent directories if absent (a holdout file is a fresh
    operator-initiated artifact, unlike the read-only ledger/store paths
    elsewhere in this package).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json.loads(holdout.model_dump_json()), indent=2, sort_keys=True) + "\n"
    )


def read_holdout_set(path: Path) -> HoldoutSet:
    """Read a `HoldoutSet` previously written by `write_holdout_set`."""
    return HoldoutSet.model_validate_json(path.read_text())

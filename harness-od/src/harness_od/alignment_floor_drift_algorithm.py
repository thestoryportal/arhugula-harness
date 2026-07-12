"""Per-primitive drift computation + re-baselining workflow — B-OD18-DRIFT-ALGORITHM.

Implements the C-OD-18 §18 "Deferred to implementation discretion" items left
open by U-OD-25 (`alignment_floor_drift_detection.py`): the drift-detection
*algorithm* per primitive (a real current-value source over the ring-buffer
observation window, feeding the existing `detect_drift`/`emit_drift_event`
pair) and the re-baselining cycle *workflow* (operator-facing recompute +
threshold-update path — the threshold *value* itself stays operator-supplied /
deployment-binding per §18.1; this module never invents one).

Scope discipline (grounded before build; per
`.harness/r-fs-2-final-closure-implementation-plan-v1.md` §4 B-OD18 entry).
§18.1's drift table names exactly the **4** `AlignmentFloorPrimitive` values
U-OD-25 already committed to — the arc register's "five C-OD-17 primitives"
phrasing is loose cross-reference prose (C-OD-17 §17.1 has 5 operator-burden
primitives; C-OD-18 §18.1's alignment-floor table has 4). The spec table wins
per the workspace authority chain (root `CLAUDE.md` §1.3): this module
targets the 4-primitive `AlignmentFloorPrimitive` set, not a 5th. Class-3
informational note, not a fork — no committed surface is contradicted.

Of those 4, only `CACHE_HIT_RATE_ALIGNMENT_FLOOR` has a deterministic,
judgment-free formula (C-OD-17 §17.1's cache-hit-ratio formula, computed off
`anthropic.cache_*` span attributes) — genuinely automatable from the ring
buffer. The other three (`JUDGE_HUMAN_COHENS_KAPPA`,
`ROUTING_ACCURACY_HOLDOUT`, `SANDBOX_TIER_ROUTING_ACCURACY`) require a
judge/human verdict to become a ratio at all; the B-OD17 review ledger
(`holdout_review_ledger.py`) stores only operator-authored free-text
categories with **no fixed taxonomy**, by explicit hard boundary
(`[[eval-harness-refused-as-governance-gate]]` — no automated inference/
scoring from that ledger, ever). Synthesizing an accuracy ratio from it here
would build exactly the judge that boundary forecloses. `compute_current_value`
therefore raises `NotSpanDerivableError` for those three; their current value
is always an operator/judge-supplied input — precisely the seam
`detect_drift(primitive, current_value, threshold)` (U-OD-25) already
provides. `run_drift_check` / `rebaseline_threshold` take
`judge_supplied_current_value` for that case.

Production-liveness note (same disposition as B-OD17/B-OD19): the sqlite ring
buffer this module reads (`sqlite_span_store_reader`) has no production
writer as of this arc — verified here against seeded test data only.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, cast

from pydantic import BaseModel, ConfigDict

from harness_od.alignment_floor_drift_detection import (
    AlignmentFloorPrimitive,
    AlignmentFloorThreshold,
    ObservationWindow,
    ObservationWindowKind,
    detect_drift,
    emit_drift_event,
)
from harness_od.otel_genai_base import EventEmission, SpanRef
from harness_od.sqlite_span_store import SpanInsertRow
from harness_od.sqlite_span_store_reader import read_all_spans

__all__ = [
    "NotSpanDerivableError",
    "RebaselineResult",
    "compute_current_value",
    "rebaseline_threshold",
    "run_drift_check",
]

_CACHE_READ_ATTR = "anthropic.cache_read_input_tokens"
_CACHE_CREATION_ATTR = "anthropic.cache_creation_input_tokens"

#: The one C-OD-18 §18.1 primitive with a deterministic, judgment-free
#: span-derived formula (see module docstring). The other 3 always require an
#: operator/judge-supplied current value.
_SPAN_DERIVABLE_PRIMITIVES = frozenset({AlignmentFloorPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR})


class NotSpanDerivableError(Exception):
    """Raised by `compute_current_value` for a judge/human-scored primitive.

    `primitive` has no deterministic span-derived formula — its current value
    can only come from an operator/judge verdict, never inferred from stored
    review data (`[[eval-harness-refused-as-governance-gate]]`). Callers must
    supply `judge_supplied_current_value` to `run_drift_check` /
    `rebaseline_threshold` instead.
    """


def _coerce_int(value: object) -> int:
    """Best-effort int coercion for a span attribute value; non-numeric /
    missing / `None` contributes zero rather than raising."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _parse_attrs(attributes_json: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(attributes_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return cast("dict[str, Any]", parsed)


def _spans_in_window(
    rows: list[SpanInsertRow], window: ObservationWindow, *, now_ns: int
) -> list[SpanInsertRow]:
    """Scope `rows` (ascending `start_time_ns`, the `sqlite_span_store_reader`
    ordering contract) to `window` (C-OD-18 §18.1/§18.2).

    `SAMPLE_WINDOW` keeps the most recent `sample_window_count` rows (a tail
    slice, since `rows` is pre-sorted ascending). `TIME_WINDOW` keeps rows
    with `start_time_ns >= now_ns - duration_ns`.
    """
    if window.kind is ObservationWindowKind.SAMPLE_WINDOW:
        assert window.sample_window_count is not None
        count = window.sample_window_count
        return rows[-count:] if count > 0 else []
    assert window.time_window_seconds is not None
    start_ns = now_ns - int(window.time_window_seconds * 1_000_000_000)
    return [r for r in rows if r.start_time_ns >= start_ns]


def _cache_hit_ratio(rows: list[SpanInsertRow]) -> float | None:
    """C-OD-17 §17.1 primitive-4 formula, scoped to `rows`:
    `cache_read / (cache_read + cache_creation)`.

    Malformed/absent attributes on a matching row contribute zero. Returns
    `None` when no row in `rows` carries either cache attribute — "no data in
    this window" is distinct from a fabricated `0.0`.
    """
    read_total = 0
    creation_total = 0
    any_cache_attrs = False
    for row in rows:
        attrs = _parse_attrs(row.attributes_json)
        if attrs is None:
            continue
        if _CACHE_READ_ATTR not in attrs and _CACHE_CREATION_ATTR not in attrs:
            continue
        any_cache_attrs = True
        read_total += _coerce_int(attrs.get(_CACHE_READ_ATTR))
        creation_total += _coerce_int(attrs.get(_CACHE_CREATION_ATTR))
    if not any_cache_attrs:
        return None
    denom = read_total + creation_total
    if denom == 0:
        return None
    return read_total / denom


def compute_current_value(
    conn: sqlite3.Connection,
    primitive: AlignmentFloorPrimitive,
    window: ObservationWindow,
    *,
    now_ns: int,
) -> float | None:
    """Compute `primitive`'s current value over `window` (C-OD-18 §18.1
    "drift-detection algorithm per primitive").

    Returns `None` when the window contains no relevant data — the caller
    should treat `None` as "skip this check" (no signal), never as drift.
    Raises `NotSpanDerivableError` for the 3 judge/human-scored primitives
    (see module docstring); those require `judge_supplied_current_value` at
    the `run_drift_check` / `rebaseline_threshold` call sites instead.
    """
    if primitive not in _SPAN_DERIVABLE_PRIMITIVES:
        raise NotSpanDerivableError(
            f"{primitive.value} has no deterministic span-derived formula "
            "(C-OD-18 §18.1) — its current value must come from an "
            "operator/judge verdict, not be inferred from stored review data "
            "(eval-harness-refused-as-governance-gate)"
        )
    scoped = _spans_in_window(read_all_spans(conn), window, now_ns=now_ns)
    return _cache_hit_ratio(scoped)


def run_drift_check(
    conn: sqlite3.Connection,
    primitive: AlignmentFloorPrimitive,
    threshold: AlignmentFloorThreshold,
    parent_span_ref: SpanRef,
    *,
    now_ns: int,
    judge_supplied_current_value: float | None = None,
) -> EventEmission | None:
    """Compute-then-emit drift check for one primitive (wires U-OD-25's
    `detect_drift` / `emit_drift_event` to a real current-value source — the
    §18.1 "algorithm" half deferred at U-OD-25).

    For `CACHE_HIT_RATE_ALIGNMENT_FLOOR`, computes the current value from
    `conn` over `threshold.observation_window`. For the other 3 primitives,
    uses `judge_supplied_current_value` — raises `ValueError` if absent.
    Returns `None` if there's nothing to check (no data in window, or no
    drift); returns the `EventEmission` if a drift event was emitted.
    """
    if primitive in _SPAN_DERIVABLE_PRIMITIVES:
        current_value = compute_current_value(
            conn, primitive, threshold.observation_window, now_ns=now_ns
        )
        if current_value is None:
            return None
    else:
        if judge_supplied_current_value is None:
            raise ValueError(
                f"{primitive.value} requires judge_supplied_current_value "
                "(C-OD-18 §18.1 — not span-derivable)"
            )
        current_value = judge_supplied_current_value
    attrs = detect_drift(primitive, current_value, threshold)
    if attrs is None:
        return None
    return emit_drift_event(parent_span_ref, attrs)


class RebaselineResult(BaseModel):
    """The result of a re-baselining round-trip (C-OD-18 §18.1 "re-baselining
    cycle workflow", deferred to implementation discretion at U-OD-25).
    Frozen -> `Eq`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    #: the updated threshold. `threshold_value` is always operator-supplied
    #: (config-driven; stays deployment-binding per §18.1) — this function
    #: performs no policy inference over what the value should be.
    new_threshold: AlignmentFloorThreshold
    #: the current value recomputed under `new_threshold.observation_window`;
    #: `None` if there's no data (span-derivable primitive) or no judge value
    #: was supplied (judge-scored primitive).
    recomputed_current_value: float | None
    #: `True` if `recomputed_current_value` still drifts below
    #: `new_threshold` — re-baselining to a value the current data still
    #: fails is a legitimate (if unusual) outcome, surfaced rather than
    #: silently accepted.
    still_drifting: bool


def rebaseline_threshold(
    conn: sqlite3.Connection,
    primitive: AlignmentFloorPrimitive,
    new_threshold_value: float,
    observation_window: ObservationWindow,
    *,
    now_ns: int,
    judge_supplied_current_value: float | None = None,
) -> RebaselineResult:
    """Operator-facing recompute + threshold-update path (C-OD-18 §18.1
    re-baselining cycle workflow).

    Constructs the new `AlignmentFloorThreshold` at the operator-supplied
    `new_threshold_value` and recomputes the current value under
    `observation_window`, so the operator sees immediately whether the
    re-baselined threshold still drifts before committing to it.
    """
    new_threshold = AlignmentFloorThreshold(
        primitive=primitive,
        threshold_value=new_threshold_value,
        observation_window=observation_window,
    )
    if primitive in _SPAN_DERIVABLE_PRIMITIVES:
        current_value = compute_current_value(conn, primitive, observation_window, now_ns=now_ns)
    else:
        current_value = judge_supplied_current_value
    still_drifting = (
        current_value is not None
        and detect_drift(primitive, current_value, new_threshold) is not None
    )
    return RebaselineResult(
        new_threshold=new_threshold,
        recomputed_current_value=current_value,
        still_drifting=still_drifting,
    )

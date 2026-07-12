"""Tests for B-OD17-EVAL-LOOP-TOOLING — review-loop persistence.

Acceptance: "review round-trip persists" (`.harness/r-fs-2-final-closure-
implementation-plan-v1.md` §3 B-OD17-EVAL-LOOP-TOOLING).
"""

from __future__ import annotations

from pathlib import Path

from harness_core import DeploymentSurface, PersonaTier
from harness_od.holdout_review_ledger import (
    ReviewEntry,
    append_review_entry,
    read_review_ledger,
    reviewed_trace_ids,
)
from harness_od.observability_matrix import CellID
from harness_od.operator_burden_eval_primitives import OperatorBurdenEvalPrimitive

_SOLO_LOCAL = CellID(
    persona_tier=PersonaTier.SOLO_DEVELOPER, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT
)


def _entry(trace_id: str, category: str = "expected") -> ReviewEntry:
    return ReviewEntry(
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
        trace_id=trace_id,
        category=category,
        notes=None,
        reviewed_at="2026-07-12T00:00:00Z",
    )


def test_read_missing_ledger_returns_empty(tmp_path: Path) -> None:
    assert read_review_ledger(tmp_path / "does-not-exist.jsonl") == []


def test_append_then_read_round_trips(tmp_path: Path) -> None:
    ledger_path = tmp_path / "review" / "ledger.jsonl"
    entry = _entry("trace-01", category="correct-routing")
    append_review_entry(ledger_path, entry)

    reloaded = read_review_ledger(ledger_path)
    assert reloaded == [entry]


def test_round_trip_persists_across_fresh_reads(tmp_path: Path) -> None:
    """The persisted-not-cached acceptance: two independent `read_review_ledger`
    calls against the same path (simulating a second process/session) both
    see the same durable content."""
    ledger_path = tmp_path / "ledger.jsonl"
    append_review_entry(ledger_path, _entry("trace-01"))

    first_read = read_review_ledger(ledger_path)
    second_read = read_review_ledger(ledger_path)
    assert first_read == second_read == [_entry("trace-01")]


def test_multiple_appends_preserve_order(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    entries = [_entry(f"trace-{i:02d}") for i in range(5)]
    for entry in entries:
        append_review_entry(ledger_path, entry)

    assert read_review_ledger(ledger_path) == entries


def test_reviewed_trace_ids_reflects_ledger_contents(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    append_review_entry(ledger_path, _entry("trace-01"))
    append_review_entry(ledger_path, _entry("trace-02"))

    assert reviewed_trace_ids(ledger_path) == {"trace-01", "trace-02"}
    assert reviewed_trace_ids(tmp_path / "missing.jsonl") == set()


def test_category_is_carried_verbatim_no_inference(tmp_path: Path) -> None:
    """The category persisted is exactly what was passed in — nothing in this
    module rewrites, normalizes, or scores it."""
    ledger_path = tmp_path / "ledger.jsonl"
    weird_category = "operator's raw judgement: 'looks fine, unsure why'"
    append_review_entry(ledger_path, _entry("trace-01", category=weird_category))

    [entry] = read_review_ledger(ledger_path)
    assert entry.category == weird_category

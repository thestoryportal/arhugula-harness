"""Tests for B-OD17-EVAL-LOOP-TOOLING — the "automate" assertion-stub scaffolder."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_core import DeploymentSurface, PersonaTier
from harness_od.holdout_assertion_scaffold import (
    scaffold_assertion_stub_source,
    scaffold_pending_stubs,
)
from harness_od.holdout_review_ledger import ReviewEntry, append_review_entry
from harness_od.observability_matrix import CellID
from harness_od.operator_burden_eval_primitives import OperatorBurdenEvalPrimitive

_SOLO_LOCAL = CellID(
    persona_tier=PersonaTier.SOLO_DEVELOPER, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT
)


def _entry(trace_id: str, category: str = "expected", notes: str | None = None) -> ReviewEntry:
    return ReviewEntry(
        cell_id=_SOLO_LOCAL,
        primitive=OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT,
        trace_id=trace_id,
        category=category,
        notes=notes,
        reviewed_at="2026-07-12T00:00:00Z",
    )


def test_stub_source_always_raises_not_implemented() -> None:
    """The generated stub never auto-passes — it is a scaffold, not a judge."""
    source = scaffold_assertion_stub_source(_entry("trace-01"))
    assert "raise NotImplementedError" in source
    assert "assert True" not in source


def test_stub_source_is_valid_python(tmp_path: Path) -> None:
    source = scaffold_assertion_stub_source(_entry("abc-123-def"))
    compile(source, "<stub>", "exec")  # raises SyntaxError on malformed source


def test_stub_source_carries_category_and_notes() -> None:
    source = scaffold_assertion_stub_source(
        _entry("trace-01", category="mis-routed", notes="tier too low")
    )
    assert "mis-routed" in source
    assert "tier too low" in source


def test_stub_function_name_handles_hex_and_special_chars() -> None:
    source = scaffold_assertion_stub_source(_entry("0xdead-beef!"))
    compile(source, "<stub>", "exec")


def test_scaffold_pending_stubs_writes_one_file_per_reviewed_trace(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    append_review_entry(ledger_path, _entry("trace-01"))
    append_review_entry(ledger_path, _entry("trace-02"))

    output_dir = tmp_path / "stubs"
    written = scaffold_pending_stubs(ledger_path, output_dir)

    assert len(written) == 2
    assert all(p.exists() for p in written)
    assert {p.name for p in written} == {
        "test_holdout_trace_01.py",
        "test_holdout_trace_02.py",
    }


def test_scaffold_pending_stubs_never_overwrites_existing_file(tmp_path: Path) -> None:
    """An operator's in-progress hand-authored assertion survives a re-run."""
    ledger_path = tmp_path / "ledger.jsonl"
    append_review_entry(ledger_path, _entry("trace-01"))
    output_dir = tmp_path / "stubs"

    first = scaffold_pending_stubs(ledger_path, output_dir)
    assert len(first) == 1
    hand_authored = "def test_holdout_trace_01():\n    assert 1 + 1 == 2\n"
    first[0].write_text(hand_authored)

    second = scaffold_pending_stubs(ledger_path, output_dir)
    assert second == []  # nothing re-written
    assert first[0].read_text() == hand_authored


def test_scaffold_pending_stubs_empty_ledger_writes_nothing(tmp_path: Path) -> None:
    output_dir = tmp_path / "stubs"
    written = scaffold_pending_stubs(tmp_path / "missing.jsonl", output_dir)
    assert written == []


def test_scaffold_pending_stubs_raises_on_trace_id_sanitization_collision(
    tmp_path: Path,
) -> None:
    """Regression guard — two distinct trace_ids that sanitize to the same
    stub path must raise, not silently drop the second one. Previously
    `path.exists()` treated the second entry as "already scaffolded" with
    zero signal that it was actually a different trace."""
    ledger_path = tmp_path / "ledger.jsonl"
    append_review_entry(ledger_path, _entry("abc-123"))
    append_review_entry(ledger_path, _entry("abc_123"))  # sanitizes identically
    output_dir = tmp_path / "stubs"

    with pytest.raises(ValueError, match="sanitization collision"):
        scaffold_pending_stubs(ledger_path, output_dir)

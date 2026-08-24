"""Witnesses for the lever cohort report (B-211/B-212 observability).

The load-bearing property is FAIL-CLOSED bucketing: an unmapped row must never
enter a median, an other-lever row must never contaminate either cohort, and a
malformed ledger line must abort loudly rather than shrink the data silently.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_lever_report as alr


def _write(ledger: Path, rows: list[dict]) -> Path:
    ledger.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return ledger


ROWS = [
    {
        "arc_id": "pr-1",
        "arc_type": "applying",
        "review_rounds": 10,
        "p1_rounds": [2],
        "arc_span_s": 7200.0,
        "levers_active": [],
    },
    {
        "arc_id": "pr-2",
        "arc_type": "applying",
        "review_rounds": 22,
        "p1_rounds": [1, 2, 3],
        "arc_span_s": 36000.0,
        "levers_active": [],
    },
    {
        "arc_id": "pr-3",
        "arc_type": "applying",
        "review_rounds": 2,
        "p1_rounds": [],
        "arc_span_s": 3600.0,
        "levers_active": ["B-211", "B-212"],
    },
    {
        "arc_id": "pr-4",
        "arc_type": "applying",
        "review_rounds": None,
        "p1_rounds": None,
        "arc_span_s": None,
        "levers_active": ["B-211", "B-212"],
    },
    {
        "arc_id": "pr-5",
        "arc_type": "applying",
        "review_rounds": 7,
        "p1_rounds": [],
        "arc_span_s": 7200.0,
        "levers_active": ["B-171"],
    },
]


def _summary(tmp_path: Path, rows: list[dict], **kw) -> dict:
    ledger = _write(tmp_path / "ledger.jsonl", rows)
    cohorts = alr.split_cohorts(
        alr.load_rows(ledger), kw.get("levers", ("B-211", "B-212")), kw.get("arc_type")
    )
    return alr.summarize(cohorts, kw.get("levers", ("B-211", "B-212")))


# mutation-probe(tools/arc_lever_report.py): treat review_rounds=None rows as measured
def test_unmapped_rows_are_excluded_from_medians_and_listed(tmp_path: Path) -> None:
    """B-170: an honest null is not a measurement; it must be visible, never averaged."""
    s = _summary(tmp_path, ROWS)
    assert s["excluded_unmapped"] == ["pr-4"]
    assert s["cohort_sizes"]["treated"] == 1, "the unmapped treated row must not count"
    assert s["treated_median_rounds"] == 2


# mutation-probe(tools/arc_lever_report.py): put other-lever rows in the baseline bucket
def test_other_lever_rows_contaminate_neither_cohort(tmp_path: Path) -> None:
    """A row treated by a DIFFERENT lever is neither baseline nor this treated set."""
    s = _summary(tmp_path, ROWS)
    assert s["excluded_other_levers"] == ["pr-5"]
    assert s["baseline_median"]["review_rounds"] == 16.0, "baseline is pr-1/pr-2 only"


# mutation-probe(tools/arc_lever_report.py): drop the delta computation
def test_delta_is_against_the_baseline_median(tmp_path: Path) -> None:
    s = _summary(tmp_path, ROWS)
    (treated,) = s["treated_arcs"]
    assert treated["delta_rounds_vs_baseline_median"] == -14.0


# mutation-probe(tools/arc_lever_report.py): report per_skill_separable as always True
def test_per_skill_separation_requires_divergent_lever_sets(tmp_path: Path) -> None:
    """Identical treated lever sets cannot attribute an effect to one skill."""
    s = _summary(tmp_path, ROWS)
    assert s["per_skill_separable"] is False
    diverged = [
        *ROWS,
        {
            "arc_id": "pr-6",
            "arc_type": "applying",
            "review_rounds": 3,
            "p1_rounds": [],
            "arc_span_s": 3600.0,
            "levers_active": ["B-211"],
        },
    ]
    assert _summary(tmp_path, diverged)["per_skill_separable"] is True


# mutation-probe(tools/arc_lever_report.py): skip malformed ledger lines instead of aborting
def test_a_malformed_ledger_line_aborts_loudly(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(ROWS[0]) + "\nnot json\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not JSON"):
        alr.load_rows(ledger)


def test_a_missing_ledger_aborts_loudly(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="not found"):
        alr.load_rows(tmp_path / "absent.jsonl")


# mutation-probe(tools/arc_lever_report.py): ignore the arc_type filter
def test_arc_type_filter_excludes_other_types(tmp_path: Path) -> None:
    mixed = [
        *ROWS,
        {
            "arc_id": "pr-7",
            "arc_type": "inventing",
            "review_rounds": 19,
            "p1_rounds": [1],
            "arc_span_s": 3600.0,
            "levers_active": [],
        },
    ]
    s = _summary(tmp_path, mixed, arc_type="applying")
    assert s["baseline_median"]["review_rounds"] == 16.0, "the inventing row must not shift it"


def test_cli_renders_and_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = _write(tmp_path / "ledger.jsonl", ROWS)
    assert alr.main(["--ledger", str(ledger)]) == 0
    out = capsys.readouterr().out
    assert "1 treated / 2 baseline" in out
    assert "NOT separable" in out
    assert "pr-4" in out, "the excluded unmapped arc must be visible in the human view"

"""Witnesses for the lever cohort report (B-211/B-212 observability).

The load-bearing property is FAIL-CLOSED bucketing: an unmapped or partial row
must never enter a median, an other-lever row must never contaminate either
cohort, arc types must never pool into one median, a null P1 count must never
read as zero, and a malformed ledger line must abort loudly rather than shrink
the data silently.
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


def _row(arc_id: str, rounds, levers: list[str], **kw) -> dict:
    return {
        "arc_id": arc_id,
        "arc_type": kw.get("arc_type", "applying"),
        "review_rounds": rounds,
        "p1_rounds": kw.get("p1", []),
        "arc_span_s": kw.get("span", 3600.0),
        "levers_active": levers,
        "round_completeness": kw.get("completeness", "complete"),
        "arc_type_declared_at": kw.get("declared_at", "open"),
    }


ROWS = [
    _row("pr-1", 10, [], p1=[2], span=7200.0),
    _row("pr-2", 22, [], p1=[1, 2, 3], span=36000.0),
    _row("pr-3", 2, ["B-211", "B-212"]),
    _row("pr-4", None, ["B-211", "B-212"], span=None),
    _row("pr-5", 7, ["B-171"], span=7200.0),
    _row("pr-6", 7, [], completeness="partial-suffix"),
]


def _summary(tmp_path: Path, rows: list[dict], levers=("B-211", "B-212")) -> dict:
    ledger = _write(tmp_path / "ledger.jsonl", rows)
    return alr.summarize(alr.split_cohorts(alr.load_rows(ledger), levers), levers)


# mutation-probe(tools/arc_lever_report.py): treat review_rounds=None rows as measured
def test_unmapped_rows_are_excluded_from_medians_and_listed(tmp_path: Path) -> None:
    """B-170: an honest null is not a measurement; it must be visible, never averaged."""
    s = _summary(tmp_path, ROWS)["arc_types"]["applying"]
    assert s["excluded_unmapped"] == ["pr-4"]
    assert s["cohort_sizes"]["treated"] == 1, "the unmapped treated row must not count"
    assert s["treated_median_rounds"] == 2


# mutation-probe(tools/arc_lever_report.py): let non-complete rounds into the medians
def test_partial_round_data_is_excluded_from_medians_and_listed(tmp_path: Path) -> None:
    """A partial suffix is a lower bound with an unknown P1 count — never a score."""
    s = _summary(tmp_path, ROWS)["arc_types"]["applying"]
    assert s["excluded_partial"] == ["pr-6"]
    assert s["baseline_median"]["review_rounds"] == 16.0, "pr-6 must not shift the median"


# mutation-probe(tools/arc_lever_report.py): put other-lever rows in the baseline bucket
def test_other_lever_rows_contaminate_neither_cohort(tmp_path: Path) -> None:
    """A row treated by a DIFFERENT lever is neither baseline nor this treated set."""
    s = _summary(tmp_path, ROWS)["arc_types"]["applying"]
    assert s["excluded_other_levers"] == ["pr-5"]
    assert s["baseline_median"]["review_rounds"] == 16.0, "baseline is pr-1/pr-2 only"


# mutation-probe(tools/arc_lever_report.py): drop the delta computation
def test_delta_is_against_the_baseline_median(tmp_path: Path) -> None:
    s = _summary(tmp_path, ROWS)["arc_types"]["applying"]
    (treated,) = s["treated_arcs"]
    assert treated["delta_rounds_vs_baseline_median"] == -14.0


# mutation-probe(tools/arc_lever_report.py): judge separability on whole lever lists
def test_per_skill_separation_ignores_non_target_levers(tmp_path: Path) -> None:
    """A stray extra lever on an identical target pattern is NOT separation."""
    contaminated = [*ROWS, _row("pr-7", 3, ["B-211", "B-212", "B-999"])]
    s = _summary(tmp_path, contaminated)["arc_types"]["applying"]
    assert s["per_skill_separable"] is False, "target patterns are identical"
    diverged = [*contaminated, _row("pr-8", 3, ["B-211"])]
    s2 = _summary(tmp_path, diverged)["arc_types"]["applying"]
    assert s2["per_skill_separable"] is True
    assert s2["separable_levers"] == ["B-211", "B-212"], (
        "{}<->{211} isolates B-211; {211}<->{211,212} isolates B-212"
    )


# mutation-probe(tools/arc_lever_report.py): group close-declared rows by bare arc_type
def test_close_declared_arc_types_group_as_contaminated(tmp_path: Path) -> None:
    """C-HE-26: a close-time label is outcome-contaminated — never beside open-declared."""
    rows = [
        _row("pr-a", 10, [], p1=[1]),
        _row("pr-b", 22, [], p1=[2], declared_at="close"),
    ]
    s = _summary(tmp_path, rows)
    assert set(s["arc_types"]) == {
        "applying",
        "applying (close-declared — outcome-contaminated, C-HE-26)",
    }
    assert s["arc_types"]["applying"]["baseline_median"]["review_rounds"] == 10


# mutation-probe(tools/arc_lever_report.py): judge the contrast on target-lever intersections
def test_a_non_target_lever_changing_simultaneously_confounds(tmp_path: Path) -> None:
    """{} vs {B-211,B-999}: B-999 changes with B-211 — no clean B-211 contrast."""
    rows = [_row("pr-a", 10, [], p1=[1]), _row("pr-b", 2, ["B-211", "B-999"])]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["separable_levers"] == [], "the non-target lever is a simultaneous change"


# mutation-probe(tools/arc_lever_report.py): report cohort size as the P1 sample size
def test_p1_medians_carry_their_own_sample_counts(tmp_path: Path) -> None:
    """A P1 median over fewer rows than the cohort must say so (n>=5 honesty)."""
    rows = [
        _row("pr-a", 10, [], p1=[1, 2]),
        _row("pr-b", 12, [], p1=None),
        _row("pr-c", 2, ["B-211", "B-212"], p1=[1]),
    ]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["baseline_median"]["measured_n"] == {
        "review_rounds": 2,
        "p1_rounds": 1,
        "arc_span_h": 2,
    }
    assert s["treated_p1_measured_n"] == 1
    assert s["p1_unmapped"] == ["pr-b"]


# mutation-probe(tools/arc_lever_report.py): mark separable on any pattern divergence
def test_separation_requires_a_single_lever_contrast(tmp_path: Path) -> None:
    """No baseline + patterns {211} vs {211,212}: only B-212 has a contrast."""
    rows = [
        _row("pr-a", 4, ["B-211"]),
        _row("pr-b", 5, ["B-211", "B-212"]),
    ]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["separable_levers"] == ["B-212"], "B-211 is present in every observation"
    # The discriminating half: a pattern pair differing in BOTH levers at once
    # ({} vs {211,212}) must separate neither — a >=1-sized diff is not a contrast.
    confounded = [_row("pr-c", 10, [], p1=[1]), _row("pr-d", 2, ["B-211", "B-212"])]
    s2 = _summary(tmp_path, confounded)["arc_types"]["applying"]
    assert s2["separable_levers"] == [], "the two levers are fully confounded"


# mutation-probe(tools/arc_lever_report.py): count a null p1_rounds as zero
def test_null_p1_is_unmapped_not_a_measured_zero(tmp_path: Path) -> None:
    """p1_rounds=null with complete rounds is unmapped provenance, never a score."""
    rows = [
        _row("pr-a", 10, [], p1=[1, 2]),
        _row("pr-b", 12, [], p1=None),
        _row("pr-c", 2, ["B-211", "B-212"], p1=None),
    ]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["baseline_median"]["p1_rounds"] == 2.0, "pr-b's null must not enter as 0"
    (treated,) = s["treated_arcs"]
    assert treated["p1_rounds"] is None
    assert s["treated_median_p1"] is None, "no measured treated P1 exists"


# mutation-probe(tools/arc_lever_report.py): drop the treated P1 median from the summary
def test_treated_p1_median_is_computed(tmp_path: Path) -> None:
    """B-211/B-212's register bar names round AND P1 cohort medians."""
    rows = [*ROWS, _row("pr-8", 4, ["B-211", "B-212"], p1=[1])]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["treated_median_p1"] == 0.5


# mutation-probe(tools/arc_lever_report.py): tell excluded-treated operators to declare levers
def test_no_evaluable_treated_arcs_is_not_a_declaration_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Rows that DID declare the levers but are unmapped must not be told to declare."""
    rows = [_row("pr-a", 10, [], p1=[1]), _row("pr-b", None, ["B-211", "B-212"], span=None)]
    ledger = _write(tmp_path / "ledger.jsonl", rows)
    assert alr.main(["--ledger", str(ledger)]) == 0
    out = capsys.readouterr().out
    assert "no evaluable treated arcs (1 treated row(s) excluded" in out
    assert "declare the lever ids" not in out


# mutation-probe(tools/arc_lever_report.py): pool arc types into one summary
def test_arc_types_are_reported_separately_never_pooled(tmp_path: Path) -> None:
    """Mixing inventing and applying compares arcs that were never comparable."""
    mixed = [*ROWS, _row("pr-9", 19, [], arc_type="inventing", p1=[1])]
    s = _summary(tmp_path, mixed)
    assert set(s["arc_types"]) == {"applying", "inventing"}
    assert s["arc_types"]["applying"]["baseline_median"]["review_rounds"] == 16.0
    assert s["arc_types"]["inventing"]["baseline_median"]["review_rounds"] == 19


# mutation-probe(tools/arc_lever_report.py): skip malformed ledger lines instead of aborting
def test_a_malformed_ledger_line_aborts_loudly(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(ROWS[0]) + "\nnot json\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not JSON"):
        alr.load_rows(ledger)


def test_a_missing_ledger_aborts_loudly(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="not found"):
        alr.load_rows(tmp_path / "absent.jsonl")


# mutation-probe(tools/arc_lever_report.py): ignore the --arc-type restriction in main
def test_cli_arc_type_flag_restricts_to_one_type(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mixed = [*ROWS, _row("pr-9", 19, [], arc_type="inventing", p1=[1])]
    ledger = _write(tmp_path / "ledger.jsonl", mixed)
    assert alr.main(["--ledger", str(ledger), "--arc-type", "applying", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert set(out["arc_types"]) == {"applying"}


def test_cli_renders_and_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = _write(tmp_path / "ledger.jsonl", ROWS)
    assert alr.main(["--ledger", str(ledger)]) == 0
    out = capsys.readouterr().out
    assert "[applying] 1 treated / 2 baseline" in out
    assert "NOT separable" in out
    assert "span_h>=" in out and "lower bound" in out, "span must read as a lower bound"
    assert "pr-4" in out, "the excluded unmapped arc must be visible in the human view"
    assert "pr-6" in out, "the excluded partial arc must be visible in the human view"

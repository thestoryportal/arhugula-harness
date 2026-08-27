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
    assert s["pattern_metrics"]["B-211+B-212"]["n"] == 1
    assert s["pattern_metrics"]["B-211+B-212"]["median_rounds"] == 2


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
        "cost_miet": 0,
    }
    assert s["pattern_metrics"]["B-211+B-212"]["p1_measured_n"] == 1
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
    assert s["pattern_metrics"]["B-211+B-212"]["median_p1"] is None, "no measured treated P1 exists"


# mutation-probe(tools/arc_lever_report.py): drop the treated P1 median from the summary
def test_treated_p1_median_is_computed(tmp_path: Path) -> None:
    """B-211/B-212's register bar names round AND P1 cohort medians."""
    rows = [*ROWS, _row("pr-8", 4, ["B-211", "B-212"], p1=[1])]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["pattern_metrics"]["B-211+B-212"]["median_p1"] == 0.5


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


# mutation-probe(tools/arc_lever_report.py): keep duplicate lever ids as distinct patterns
def test_duplicate_lever_declarations_normalize_to_one_pattern(tmp_path: Path) -> None:
    """[B-211] and [B-211,B-211] are one declaration; together they reach n=5."""
    rows = [_row(f"pr-a{i}", 3, ["B-211"]) for i in range(3)]
    rows += [_row(f"pr-b{i}", 3, ["B-211", "B-211"]) for i in range(2)]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["pattern_metrics"]["B-211"]["n"] == 5


# mutation-probe(tools/arc_lever_report.py): advertise separability from non-evaluable data
def test_separability_is_gated_on_group_evaluability(tmp_path: Path) -> None:
    """A clean {} vs {B-211} contrast in a close-declared group must not advertise."""
    rows = [
        _row("pr-a", 10, [], p1=[1], declared_at="close"),
        _row("pr-b", 2, ["B-211"], declared_at="close"),
    ]
    key = "applying (close-declared — outcome-contaminated, C-HE-26)"
    s = _summary(tmp_path, rows)["arc_types"][key]
    assert s["per_skill_separable"] is False
    assert s["separable_levers"] == []


# mutation-probe(tools/arc_lever_report.py): treat any open-declared label as evaluable
def test_unknown_arc_type_labels_are_non_evaluable(tmp_path: Path) -> None:
    """C-HE-26 admits inventing/applying only; five 'research' rows form no cohort."""
    rows = [_row(f"pr-{i}", 3, ["B-211", "B-212"], arc_type="research") for i in range(5)]
    s = _summary(tmp_path, rows)["arc_types"]["research"]
    assert s["evaluable_for_lever_decision"] is False


# mutation-probe(tools/arc_lever_report.py): read an explicit null completeness as complete
def test_explicit_null_completeness_fails_closed(tmp_path: Path) -> None:
    """Absent field = legacy complete; an explicit null is unknown and excludes."""
    rows = [
        {**_row("pr-a", 10, [], p1=[1]), "round_completeness": None},
        _row("pr-b", 14, [], p1=[2]),
    ]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["excluded_partial"] == ["pr-a"]
    assert s["baseline_median"]["review_rounds"] == 14


# mutation-probe(tools/arc_lever_report.py): mark unclassified groups evaluable
def test_untyped_groups_are_non_evaluable(tmp_path: Path) -> None:
    """C-HE-26 needs an open-time inventing/applying label; untyped rows have none."""
    rows = [{k: v for k, v in _row("pr-a", 10, ["B-211", "B-212"]).items() if k != "arc_type"}]
    rows[0]["arc_type"] = None
    s = _summary(tmp_path, rows)["arc_types"]["unclassified"]
    assert s["evaluable_for_lever_decision"] is False


# mutation-probe(tools/arc_lever_report.py): classify an absent round_completeness as partial
def test_legacy_rows_without_completeness_field_stay_evaluable(tmp_path: Path) -> None:
    """Absent field = the legacy complete shape; only explicit non-complete excludes."""
    legacy = {k: v for k, v in _row("pr-a", 10, [], p1=[1]).items() if k != "round_completeness"}
    s = _summary(tmp_path, [legacy, _row("pr-b", 14, [], p1=[2])])["arc_types"]["applying"]
    assert s["excluded_partial"] == []
    assert s["baseline_median"]["review_rounds"] == 12.0, "the legacy row must count"


# mutation-probe(tools/arc_lever_report.py): pool all treated lever sets into one median
def test_treated_sub_cohorts_split_by_exact_lever_set(tmp_path: Path) -> None:
    """5x B-211-only fast + 5x B-212-only slow must not pool into a meaningless median."""
    rows = [_row("pr-base", 10, [], p1=[1])]
    rows += [_row(f"pr-a{i}", 1, ["B-211"]) for i in range(5)]
    rows += [_row(f"pr-b{i}", 19, ["B-212"]) for i in range(5)]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["pattern_metrics"]["B-211"] == {
        "n": 5,
        "median_rounds": 1,
        "median_p1": 0,
        "p1_measured_n": 5,
    }
    assert s["pattern_metrics"]["B-212"]["median_rounds"] == 19
    assert "treated_median_rounds" not in s, "pooled treated aggregates evaluate neither lever"


# mutation-probe(tools/arc_lever_report.py): leave contaminated groups evaluable
def test_contaminated_groups_are_non_evaluable_for_the_lever_decision(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Five close-declared treated rows must NOT satisfy the n>=5 gate (C-HE-26)."""
    rows = [
        _row("pr-a", 22, [], p1=[1], declared_at="close"),
        _row("pr-b", 2, ["B-211", "B-212"], declared_at="close"),
        _row("pr-c", 9, [], p1=[2]),
    ]
    s = _summary(tmp_path, rows)
    contaminated = s["arc_types"]["applying (close-declared — outcome-contaminated, C-HE-26)"]
    assert contaminated["evaluable_for_lever_decision"] is False
    assert s["arc_types"]["applying"]["evaluable_for_lever_decision"] is True
    ledger = _write(tmp_path / "l2.jsonl", rows)
    assert alr.main(["--ledger", str(ledger)]) == 0
    assert "NON-EVALUABLE for the n>=5 lever decision" in capsys.readouterr().out


# mutation-probe(tools/arc_lever_report.py): collect contrast patterns from treated rows only
def test_a_matched_other_lever_contrast_isolates_the_target(tmp_path: Path) -> None:
    """{B-999} vs {B-211,B-999} differs only in B-211 — a valid matched contrast,
    even though the B-999-only row belongs to no cohort median."""
    rows = [_row("pr-a", 9, ["B-999"]), _row("pr-b", 3, ["B-211", "B-999"])]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["separable_levers"] == ["B-211"]
    assert s["excluded_other_levers"] == ["pr-a"], "the contrast row still joins no cohort"
    assert s["pattern_metrics"]["B-999"]["median_rounds"] == 9, (
        "a separability claim must ship its control pattern's metrics"
    )


# mutation-probe(tools/arc_lever_report.py): read a null/absent levers_active as []
def test_undeclared_levers_are_no_claim_not_a_baseline(tmp_path: Path) -> None:
    """[] is an explicit claim; an absent or null field is structurally incomplete."""
    absent = {k: v for k, v in _row("pr-a", 10, []).items() if k != "levers_active"}
    rows = [absent, {**_row("pr-b", 12, []), "levers_active": None}, _row("pr-c", 14, [])]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["excluded_undeclared"] == ["pr-a", "pr-b"]
    assert s["baseline_median"]["review_rounds"] == 14, "only the explicit [] is baseline"


# mutation-probe(tools/arc_lever_report.py): filter --arc-type by exact key equality
def test_cli_arc_type_flag_matches_contaminated_groups(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """On an all-close-declared ledger the recommended invocation must not go empty."""
    rows = [
        _row("pr-a", 22, [], p1=[1], declared_at="close"),
        _row("pr-b", 2, ["B-211", "B-212"], declared_at="close"),
    ]
    ledger = _write(tmp_path / "ledger.jsonl", rows)
    assert alr.main(["--ledger", str(ledger), "--arc-type", "applying", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert list(out["arc_types"]) == ["applying (close-declared — outcome-contaminated, C-HE-26)"]


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


# mutation-probe(tools/arc_lever_report.py): drop the cost_miet computation in _metrics
def test_cost_renders_per_arc_when_present_and_never_as_a_partial_sum(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """C-HE-25 X6e: a treated arc with cost fields shows cost=<n>M IET; a row whose
    MAIN cost is unmeasured stays unmeasured even when a subagent figure exists."""
    costed = _row("pr-c", 3, ["B-211", "B-212"])
    costed.update(cost_main_iet=2_000_000.0, cost_subagent_iet=500_000.0)
    partial = _row("pr-p", 4, ["B-211", "B-212"])
    partial.update(cost_subagent_iet=500_000.0)  # main null -> no partial sum
    base = _row("pr-b", 10, [])
    base.update(cost_main_iet=4_000_000.0)  # control-side cost (codex u-he-48 r1)
    s = _summary(tmp_path, [base, costed, partial])["arc_types"]["applying"]
    by_id = {m["arc_id"]: m for m in s["treated_arcs"]}
    assert by_id["pr-c"]["cost_miet"] == 2.5
    assert by_id["pr-p"]["cost_miet"] is None
    assert s["baseline_median"]["cost_miet"] == 4.0
    assert s["baseline_median"]["measured_n"]["cost_miet"] == 1
    ledger = _write(tmp_path / "ledger.jsonl", [base, costed, partial])
    assert alr.main(["--ledger", str(ledger)]) == 0
    out = capsys.readouterr().out
    assert "cost=2.5M IET" in out
    assert "cost=4.0M IET (n=1)" in out, "the baseline median must expose control-side cost"
    assert "cost=0.5M IET" not in out, "a main-null row must not render the subagent half"


# mutation-probe(tools/arc_lever_report.py): accept a row missing arc_id into the buckets
def test_a_row_missing_arc_id_aborts_loudly(tmp_path: Path) -> None:
    """codex r12: a syntactically-valid row missing arc_id must be refused at the
    LedgerRow boundary, never absorbed anonymously into a cohort median."""
    anonymous = {k: v for k, v in _row("pr-a", 3, []).items() if k != "arc_id"}
    ledger = _write(tmp_path / "ledger.jsonl", [anonymous])
    with pytest.raises(SystemExit, match=r"ledger\.jsonl:1 illegal row shape"):
        alr.load_rows(ledger)


# mutation-probe(tools/arc_lever_report.py): pass non-object JSON lines through as rows
def test_a_non_object_row_aborts_loudly(tmp_path: Path) -> None:
    """A JSON array/scalar line parses as JSON but is not an arc row; the boundary
    must refuse it there, not crash mid-bucketing."""
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(ROWS[0]) + "\n[1, 2]\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="illegal row shape"):
        alr.load_rows(ledger)


# mutation-probe(tools/arc_lever_report.py): consume non-arc record_kind rows as arcs
def test_a_non_arc_record_kind_aborts_loudly(tmp_path: Path) -> None:
    """Only record_kind 'arc' (or the absent legacy shape) is an arc row; any other
    kind entering a cohort would score a record that is not an arc."""
    ledger = _write(tmp_path / "ledger.jsonl", [{**_row("pr-a", 3, []), "record_kind": "finding"}])
    with pytest.raises(SystemExit, match="illegal row shape"):
        alr.load_rows(ledger)


# mutation-probe(tools/arc_lever_report.py): coerce a mistyped review_rounds to a cohort value
def test_a_mistyped_field_aborts_loudly(tmp_path: Path) -> None:
    ledger = _write(tmp_path / "ledger.jsonl", [{**_row("pr-a", 3, []), "review_rounds": "many"}])
    with pytest.raises(SystemExit, match="illegal row shape"):
        alr.load_rows(ledger)


# mutation-probe(tools/arc_lever_report.py): relax the boundary back to lax coercion
@pytest.mark.parametrize(
    "patch",
    [
        {"review_rounds": "3"},
        {"review_rounds": 3.0},
        {"review_rounds": -1},
        {"p1_rounds": ["1"]},
        {"arc_span_s": -5.0},
    ],
)
def test_coercible_and_negative_values_are_not_measurements(tmp_path: Path, patch: dict) -> None:
    """codex r13: a coerced "3"/3.0/["1"] would enter a median as a measurement the
    producer never took, and negative rounds/spans are no measurement at all."""
    ledger = _write(tmp_path / "ledger.jsonl", [{**_row("pr-a", 3, []), **patch}])
    with pytest.raises(SystemExit, match="illegal row shape"):
        alr.load_rows(ledger)


def test_an_integral_span_is_a_lossless_legacy_shape(tmp_path: Path) -> None:
    """Strict float admits int by design; a legacy integer span stays readable."""
    rows = alr.load_rows(
        _write(tmp_path / "l.jsonl", [{**_row("pr-a", 3, []), "arc_span_s": 3600}])
    )
    assert rows[0].arc_span_s == 3600.0


# mutation-probe(tools/arc_lever_report.py): drop the is-not-None span filters feeding median
def test_null_span_rows_stay_in_cohorts_but_out_of_span_medians(tmp_path: Path) -> None:
    """merge-gate witness lens r1 P1: ArcRow permits arc_span_s=None independently of
    review_rounds; such a row must enter its cohort (rounds ARE measured) while its
    null span stays out of the span median instead of crashing statistics.median."""
    rows = [
        _row("pr-a", 10, [], p1=[1], span=None),
        _row("pr-b", 14, [], p1=[2], span=7200.0),
        _row("pr-c", 2, ["B-211", "B-212"], span=None),
    ]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    assert s["cohort_sizes"]["baseline"] == 2, "a null span must not evict the row"
    assert s["baseline_median"]["arc_span_h"] == 2.0, "median over the one measured span"
    assert s["baseline_median"]["measured_n"]["arc_span_h"] == 1
    (treated,) = s["treated_arcs"]
    assert treated["arc_span_h"] is None, "null span renders as null, never a number"


# mutation-probe(tools/arc_lever_report.py): drop the None guard on the baseline delta
def test_treated_rows_with_zero_baseline_carry_a_null_delta(tmp_path: Path) -> None:
    """merge-gate witness lens r1 P2: a nascent cohort can have treated rows and no
    baseline; the delta must be an honest null, not a crash or a number."""
    s = _summary(tmp_path, [_row("pr-a", 3, ["B-211"])])["arc_types"]["applying"]
    assert s["baseline_median"]["review_rounds"] is None
    (treated,) = s["treated_arcs"]
    assert treated["delta_rounds_vs_baseline_median"] is None


# mutation-probe(tools/arc_lever_report.py): invert the target-membership filter in _metrics
def test_target_levers_declared_lists_targets_only(tmp_path: Path) -> None:
    """merge-gate witness lens r1 P2: the per-row target/non-target split is data
    a reader acts on; pin its membership logic."""
    rows = [_row("pr-base", 10, [], p1=[1]), _row("pr-a", 3, ["B-999", "B-211"])]
    s = _summary(tmp_path, rows)["arc_types"]["applying"]
    (treated,) = s["treated_arcs"]
    assert treated["target_levers_declared"] == ["B-211"]
    assert treated["levers"] == ["B-211", "B-999"]


# mutation-probe(tools/arc_lever_report.py): stop filtering empty tokens from --levers
def test_cli_levers_flag_parses_and_empty_rejects(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """merge-gate witness lens r1 P3: exercise --levers through argparse — custom
    ids with stray commas/space parse, and an all-empty value aborts loudly."""
    ledger = _write(tmp_path / "ledger.jsonl", [_row("pr-a", 3, ["B-999"])])
    assert alr.main(["--ledger", str(ledger), "--levers", " B-999,, ", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["target_levers"] == ["B-999"]
    assert out["arc_types"]["applying"]["cohort_sizes"]["treated"] == 1
    with pytest.raises(SystemExit, match="at least one lever id"):
        alr.main(["--ledger", str(ledger), "--levers", " , "])


# mutation-probe(tools/arc_lever_report.py): crash on blank lines / drop the no-treated message
def test_blank_ledger_lines_skip_and_zero_treated_renders_the_declare_hint(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """merge-gate witness lens r1 P3: a trailing/interior blank line is a legal
    ledger shape, and the zero-treated render branch has its own message."""
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(_row("pr-a", 3, [])) + "\n\n", encoding="utf-8")
    assert alr.main(["--ledger", str(ledger)]) == 0
    assert "no treated arcs — declare the lever ids" in capsys.readouterr().out


# mutation-probe(tools/arc_lever_report.py): re-derive the non-evaluable cause in render
def test_open_declared_unknown_type_carries_its_own_reason(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """codex r12: an open-declared 'research' group is neither close-declared nor
    untyped — the render must carry the split-time reason, not re-derive a wrong one."""
    rows = [_row("pr-a", 3, ["B-211"], arc_type="research")]
    s = _summary(tmp_path, rows)["arc_types"]["research"]
    assert "unknown open-declared arc type 'research'" in s["non_evaluable_reason"]
    ledger = _write(tmp_path / "l2.jsonl", rows)
    assert alr.main(["--ledger", str(ledger)]) == 0
    out = capsys.readouterr().out
    assert "unknown open-declared arc type 'research'" in out
    assert "close-declared or untyped" not in out


def test_evaluable_groups_carry_no_reason(tmp_path: Path) -> None:
    s = _summary(tmp_path, [_row("pr-a", 3, [])])["arc_types"]["applying"]
    assert s["evaluable_for_lever_decision"] is True
    assert s["non_evaluable_reason"] is None

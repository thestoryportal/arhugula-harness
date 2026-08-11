"""Tests for the substitution-ledger derivation (R-600-substitution-ledger-schema).

The CI tally-validation gate runs this module. It pins the live canonical ledger integers
+ structural invariants + the label≠count-membership rule, and proves the gate actually
catches the failure classes it exists for (silent disposition flip; impossible snapshot
pairs).
"""

from __future__ import annotations

import copy

import pytest
import substitution_ledger as sl


@pytest.fixture
def data() -> dict:
    return sl.load()


# ── The canonical pin (advisor's independent snapshot) ──────────────────────────────────
# If these literals legitimately change, a retirement-event transit happened: update the
# row's `disposition` + the `snapshot:` block in substitutions.yaml + these literals + file
# a retirement batch — all in the SAME commit (forward-only). Never edit just one.


def test_canonical_integers(data):
    d = sl.derive(data)
    assert d["retired"] == 54, "post-batch-56 CXA-1 back-flow RETIRED"
    assert d["pipeline_advanced"] == 54
    assert d["total_canonical"] == 54
    assert d["non_canonical"] == 1  # CP-24


def test_bucket_breakdown(data):
    d = sl.derive(data)
    # CXA-2 bounded-residual discharged at batch-57 (R-FS-1 E-impl-2): BOUNDED_RESIDUAL
    # 3→2, SUBSTANTIVE_RETIRED 43→44. Count-neutral — both buckets count as RETIRED.
    assert d["by_disposition"] == {
        "SUBSTANTIVE_RETIRED": 44,
        "AUTHORING_ONLY": 8,
        "BOUNDED_RESIDUAL": 2,
    }


# ── The two distinct per-axis breakdowns — do NOT cross them (advisor's trap) ───────────
# CP is 21 ROWS and now contributes 21 to RETIRED after batch-52. At Phase-8 declaration
# time, CP-17 was still SB-INDEF; historical prose stays historical, but the live ledger
# pin below is batch-52.


def test_axis_rowcount(data):
    d = sl.derive(data)
    assert d["axis_rowcount"] == {"IS": 9, "AS": 11, "CP": 21, "OD": 8, "CXA": 5}
    assert sum(d["axis_rowcount"].values()) == 54


def test_axis_retired_contribution(data):
    d = sl.derive(data)
    assert d["axis_retired"] == {"IS": 9, "AS": 11, "CP": 21, "OD": 8, "CXA": 5}
    assert sum(d["axis_retired"].values()) == 54


# ── label ≠ count-membership (the rule the R-700 close turned on) ───────────────────────


def test_retired_as_label_does_not_retally(data):
    bad = copy.deepcopy(data)
    for r in bad["substitutions"]:
        if r["id"] == "H_T-CXA-1":
            r["sign_off_label"] = "RETIRED-AS-SYNTHETIC-DEFERRED"
            r["disposition"] = "PARTIAL"
            break
    # The "RETIRED-AS-X" label must NOT make an otherwise PARTIAL row counted.
    assert "H_T-CXA-1" not in {
        s["id"] for s in sl.derive(bad)["sign_offs"] if s["counted_in_retired"]
    }


def test_bounded_residual_rows_are_counted(data):
    # The tell from the R-700 close: OD-6 carries a terminal BOUNDED_RESIDUAL disposition AND
    # is counted in RETIRED — proving bounded-residual rows are terminal count-members.
    # (CXA-2 was the other example until batch-57 discharged its residual →
    # SUBSTANTIVE_RETIRED; OD-6 remains the canonical bounded-residual exemplar.)
    rows = {r["id"]: r for r in data["substitutions"]}
    assert rows["H_T-OD-6"]["disposition"] == "BOUNDED_RESIDUAL"  # counted
    assert rows["H_T-OD-6"]["disposition"] in sl.RETIRED_DISPOSITIONS


def test_batch_52_backflow_rows_are_retired(data):
    rows = {r["id"]: r for r in data["substitutions"]}
    for row_id in ("H_T-AS-8e", "H_T-AS-8f", "H_T-CP-17"):
        assert rows[row_id]["disposition"] == "SUBSTANTIVE_RETIRED"
        assert rows[row_id]["batch"] == "batch-52"
    assert "SB_INDEFINITE" not in sl.derive(data)["by_disposition"]


def test_as_axis_claude_uses_live_batch_52_posture(data):
    rows = {r["id"]: r for r in data["substitutions"]}
    derived = sl.derive(data)
    text = (sl.DEFAULT_LEDGER.parents[1] / "harness-as" / "CLAUDE.md").read_text(encoding="utf-8")

    assert derived["axis_rowcount"]["AS"] == 11
    assert derived["axis_retired"]["AS"] == 11
    assert ".harness/substitutions.yaml" in text
    assert "tools/substitution_ledger.py" in text
    assert "2 / 11 STILL-BOUNDED-INDEFINITELY" not in text

    lines = text.splitlines()
    for row_id in ("H_T-AS-8e", "H_T-AS-8f"):
        assert rows[row_id]["disposition"] == "SUBSTANTIVE_RETIRED"
        assert rows[row_id]["batch"] == "batch-52"
        row_line = next(line for line in lines if line.startswith(f"| {row_id} "))
        assert "SUBSTANTIVE_RETIRED" in row_line
        assert "batch-52" in row_line
        assert "STILL-BOUNDED" not in row_line


def test_batch_53_backflow_rows_are_retired(data):
    rows = {r["id"]: r for r in data["substitutions"]}
    for row_id in ("H_T-OD-4", "H_T-CXA-4"):
        assert rows[row_id]["disposition"] == "SUBSTANTIVE_RETIRED"
        assert rows[row_id]["batch"] == "batch-53"
        assert "sign_off_label" not in rows[row_id]


def test_batch_54_backflow_rows_are_retired(data):
    rows = {r["id"]: r for r in data["substitutions"]}
    assert rows["H_T-CXA-3"]["disposition"] == "SUBSTANTIVE_RETIRED"
    assert rows["H_T-CXA-3"]["batch"] == "batch-54"
    assert "sign_off_label" not in rows["H_T-CXA-3"]


def test_batch_57_cxa_2_residual_discharged(data):
    # batch-55 closed CXA-2 as a COUNTED bounded-residual (engine recovery loop dormant);
    # batch-57 (R-FS-1 E-impl-2) discharged that residual — the WAL_SEGMENT recovery loop
    # is live in production — so the row upgrades BOUNDED_RESIDUAL→SUBSTANTIVE_RETIRED
    # (count-neutral: both count as RETIRED).
    rows = {r["id"]: r for r in data["substitutions"]}
    assert rows["H_T-CXA-2"]["disposition"] == "SUBSTANTIVE_RETIRED"
    assert rows["H_T-CXA-2"]["batch"] == "batch-57"
    assert "sign_off_label" not in rows["H_T-CXA-2"]


def test_batch_56_backflow_rows_are_retired(data):
    rows = {r["id"]: r for r in data["substitutions"]}
    assert rows["H_T-CXA-1"]["disposition"] == "SUBSTANTIVE_RETIRED"
    assert rows["H_T-CXA-1"]["batch"] == "batch-56"
    assert "sign_off_label" not in rows["H_T-CXA-1"]


# ── The live ledger validates clean ────────────────────────────────────────────────────


def test_live_ledger_passes_validation(data):
    assert sl.validate(data) == []


# ── Negative tests — prove the gate catches what it exists for ─────────────────────────


def test_silent_disposition_flip_is_caught(data):
    # CXA-1 SUBSTANTIVE_RETIRED → PARTIAL: RETIRED 54→53, pipeline-advanced unchanged at 54,
    # Axis row counts and bucket sum still pass — only the snapshot pin catches it.
    # pin catches it. This is the exact class the original 48/54 bug lived in.
    bad = copy.deepcopy(data)
    for r in bad["substitutions"]:
        if r["id"] == "H_T-CXA-1":
            r["disposition"] = "PARTIAL"
    violations = sl.validate(bad)
    assert any("snapshot" in v for v in violations), violations


def test_impossible_pipeline_pair_is_caught(data):
    # Force an impossible pair: alter the snapshot without changing the rows.
    bad = copy.deepcopy(data)
    bad["snapshot"]["retired"] = 50  # claim 50 while rows derive 54
    violations = sl.validate(bad)
    assert any("snapshot.retired" in v for v in violations), violations


def test_label_promoted_to_count_is_caught(data):
    # A future editor flips a labelled PARTIAL row to a counted bucket but keeps RETIRED-AS-X.
    bad = copy.deepcopy(data)
    for r in bad["substitutions"]:
        if r["id"] == "H_T-CXA-1":
            r["sign_off_label"] = "RETIRED-AS-SYNTHETIC-DEFERRED"
            r["disposition"] = "BOUNDED_RESIDUAL"  # now counted, label still RETIRED-AS-X
    violations = sl.validate(bad)
    assert any("must NOT drive the count" in v for v in violations), violations


def test_row_count_drift_is_caught(data):
    bad = copy.deepcopy(data)
    bad["substitutions"] = bad["substitutions"][:-1]  # drop a canonical row
    violations = sl.validate(bad)
    assert any("canonical row count" in v or "snapshot" in v for v in violations), violations


# ── R-CTX-1 / U-CTX-12: root CLAUDE.md §4.1 must not re-hardcode a LIVE tally ───────────
# §4.1 carried two tables that read as live counts but were the FROZEN design-phase
# `Phase_7_Meta_Architecture_v1.md` §5 declaration; its per-axis line said `AS=6` against a
# live ledger the batch-24 decomposition had already moved past. The repair labels both
# tables as design-phase history and routes the live tally to this tool. These pins keep
# that split intact — no literal is asserted, the live figure is derived here.


def _root_claude_md() -> str:
    return (sl.DEFAULT_LEDGER.parents[1] / "CLAUDE.md").read_text(encoding="utf-8")


def test_root_claude_section_4_1_routes_live_counts_to_the_derivation(data) -> None:
    text = _root_claude_md()
    section = text.split("### 4.1 ")[1].split("### 4.2 ")[0]
    assert "tools/substitution_ledger.py --summary" in section
    assert "FROZEN design-phase" in section
    # The design-phase figures are retained, but explicitly as history.
    assert "IS=9 / AS=6 / CP=21 / OD=8 / CXA=5" in section
    assert "The live per-axis split is different and is derived, not written here" in section


def test_root_claude_section_4_1_does_not_assert_the_live_per_axis_split(data) -> None:
    """The live split must never be pasted in — that is exactly how `AS=6` went stale."""
    section = _root_claude_md().split("### 4.1 ")[1].split("### 4.2 ")[0]
    derived = sl.derive(data)["axis_rowcount"]
    live_line = " / ".join(f"{axis}={derived[axis]}" for axis in ("IS", "AS", "CP", "OD", "CXA"))
    assert live_line not in section, (
        f"root CLAUDE.md §4.1 hardcodes the live per-axis split ({live_line}); "
        "§4.2 requires it be derived from tools/substitution_ledger.py instead"
    )


def test_artifact_pointer_index_carries_no_inline_substitution_cardinality() -> None:
    """`.harness/artifact-pointers/plans.md` §2.5 rows carried stale `(N entries)` counts."""
    path = sl.DEFAULT_LEDGER.parents[1] / ".harness" / "artifact-pointers" / "plans.md"
    text = path.read_text(encoding="utf-8")
    for axis in ("IS", "AS", "CP", "OD"):
        assert f"{axis} substitution surface (" not in text, (
            f"{path.name} re-introduced an inline {axis} substitution cardinality"
        )
    assert "tools/substitution_ledger.py --summary" in text

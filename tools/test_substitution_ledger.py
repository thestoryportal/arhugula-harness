"""Tests for the substitution-ledger derivation (R-600-substitution-ledger-schema).

The CI tally-validation gate runs this module. It pins the canonical Phase-8 graduation
integers + structural invariants + the label≠count-membership rule, and proves the gate
actually catches the failure classes it exists for (silent disposition flip; the 48-vs-49
impossibility).
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
    assert d["retired"] == 46, "Phase-8 graduation canonical RETIRED (accounting (i))"
    assert d["pipeline_advanced"] == 49
    assert d["total_canonical"] == 54
    assert d["non_canonical"] == 1  # CP-24


def test_bucket_breakdown(data):
    d = sl.derive(data)
    assert d["by_disposition"] == {
        "SUBSTANTIVE_RETIRED": 36,
        "AUTHORING_ONLY": 8,
        "BOUNDED_RESIDUAL": 2,
        "PARTIAL": 3,
        "STILL_BOUNDED": 2,
        "SB_INDEFINITE": 3,
    }


# ── The two distinct per-axis breakdowns — do NOT cross them (advisor's trap) ───────────
# CP is 21 ROWS but contributes 20 to RETIRED (CP-17 is the SB-INDEF). The graduation §3
# "CP 21" is the row-count, not the RETIRED contribution.


def test_axis_rowcount(data):
    d = sl.derive(data)
    assert d["axis_rowcount"] == {"IS": 9, "AS": 11, "CP": 21, "OD": 8, "CXA": 5}
    assert sum(d["axis_rowcount"].values()) == 54


def test_axis_retired_contribution(data):
    d = sl.derive(data)
    assert d["axis_retired"] == {"IS": 9, "AS": 9, "CP": 20, "OD": 7, "CXA": 1}
    assert sum(d["axis_retired"].values()) == 46


# ── label ≠ count-membership (the rule the R-700 close turned on) ───────────────────────


def test_od4_label_does_not_retally(data):
    rows = {r["id"]: r for r in data["substitutions"]}
    od4 = rows["H_T-OD-4"]
    assert od4["sign_off_label"] == "RETIRED-AS-CROSS-AXIS-DEFERRED"
    assert od4["disposition"] == "PARTIAL"
    # The "RETIRED-AS-X" label must NOT make OD-4 counted.
    assert "H_T-OD-4" not in {
        s["id"] for s in sl.derive(data)["sign_offs"] if s["counted_in_retired"]
    }


def test_od6_in_signoff_list_yet_counted(data):
    # The tell from the R-700 close: OD-6 carries a terminal disposition AND is counted in
    # the 46 — proving "appears with a sign-off" is orthogonal to "counted in RETIRED".
    rows = {r["id"]: r for r in data["substitutions"]}
    assert rows["H_T-OD-6"]["disposition"] == "BOUNDED_RESIDUAL"  # counted
    od4_counted = rows["H_T-OD-4"]["disposition"] in sl.RETIRED_DISPOSITIONS
    od6_counted = rows["H_T-OD-6"]["disposition"] in sl.RETIRED_DISPOSITIONS
    assert od6_counted and not od4_counted


# ── The live ledger validates clean ────────────────────────────────────────────────────


def test_live_ledger_passes_validation(data):
    assert sl.validate(data) == []


# ── Negative tests — prove the gate catches what it exists for ─────────────────────────


def test_silent_disposition_flip_is_caught(data):
    # OD-4 PARTIAL → SUBSTANTIVE_RETIRED: RETIRED 46→47, pipeline-advanced unchanged at 49,
    # OD still 8 rows, sum still 54 — every STRUCTURAL invariant passes. Only the snapshot
    # pin catches it. This is the exact class the original 48/54 bug lived in.
    bad = copy.deepcopy(data)
    for r in bad["substitutions"]:
        if r["id"] == "H_T-OD-4":
            r["disposition"] = "SUBSTANTIVE_RETIRED"
    violations = sl.validate(bad)
    assert any("snapshot" in v for v in violations), violations


def test_impossible_pipeline_pair_is_caught(data):
    # Force the 48-vs-49 impossibility: bump RETIRED without touching the snapshot/pipeline.
    bad = copy.deepcopy(data)
    bad["snapshot"]["retired"] = 47  # claim 47 while rows derive 46
    violations = sl.validate(bad)
    assert any("snapshot.retired" in v for v in violations), violations


def test_label_promoted_to_count_is_caught(data):
    # A future editor flips OD-4 to a counted bucket but keeps the RETIRED-AS-X label.
    bad = copy.deepcopy(data)
    for r in bad["substitutions"]:
        if r["id"] == "H_T-OD-4":
            r["disposition"] = "BOUNDED_RESIDUAL"  # now counted, label still RETIRED-AS-X
    violations = sl.validate(bad)
    assert any("must NOT drive the count" in v for v in violations), violations


def test_row_count_drift_is_caught(data):
    bad = copy.deepcopy(data)
    bad["substitutions"] = bad["substitutions"][:-1]  # drop a canonical row
    violations = sl.validate(bad)
    assert any("canonical row count" in v or "snapshot" in v for v in violations), violations

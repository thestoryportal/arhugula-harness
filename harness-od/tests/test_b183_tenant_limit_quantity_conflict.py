"""B-183: the per-tenant limit's QUANTITY is declared three ways. Pinned, not resolved.

`B-183` registered that `assert_per_tenant_cardinality_isolation` compares
`CardinalityCounters.observed_series` — a count of **distinct attribute-value series** —
against `tenant_rate_limit`, documented as **spans/sec**, while never reading
`observation_window`. Its close-out says the **quantity** must be settled before the unit.

Grounding the corpus settles what the conflict IS, and simultaneously shows it is **not
agent-decidable**. Three surfaces disagree:

1. **`C-OD-11 §11` frames the whole contract as CARDINALITY** — the section is *"Cardinality
   budget per cell + cardinality-safe-attribute discipline"*, its contract surface is
   *"Per-cell **cardinality** budget"*, and ADR-D6 v1.1 §1.3 is cited as the *"cardinality
   budget per cell"* paragraph. §11.2/§11.3 use cardinality in its ordinary sense: **distinct
   values**. `C-OD-21 §21.4`'s row is literally *"Per-tenant **cardinality** isolation"*.
2. **The OD plan's own field signature says SPANS/SEC** —
   `Implementation_Plan_Operational_Discipline_v2.md:978`,
   `// per-cell global rate limit (spans/sec)` — and two cleared spec deltas quantify it the
   same way: `Spec_Operational_Discipline_v1_37.md` (*"`tenant_rate_limit=1_000.0` spans/sec
   at the two multi-tenant cells"*) and `v1_38.md` (*"the C-OD-11 §11.1 1,000 spans/sec
   budget"*).
3. **The code compares SERIES.** `observed_series` counts distinct attribute-value series;
   `assert_per_tenant_cardinality_isolation` compares it directly to `tenant_rate_limit`.

**Spans and series are not interchangeable** — one series can carry any number of spans — so
at most one of these readings can be right, and the choice changes what a **compliance**
surface measures at the two multi-tenant cells (`C-OD-21` per-tenant isolation).

**Why this module pins rather than fixes.** An earlier pass of this arc read only `§11`'s
cardinality framing, concluded the *"spans/sec"* docstrings were a stray documentation
error, and was about to correct them. They are not stray: they are the **plan's own
signature** plus two **cleared spec deltas**. Changing which quantity the limit governs is a
design-substrate decision, not a docstring tidy — X-AL-3 forbids making it here. So the
conflict is pinned at its three sites, and `B-183` routes the decision rather than absorbing
it.

**What the tests below guarantee.** That all three declarations still say what this row
quotes. If any one moves — a spec delta re-quantifies the budget, the plan signature is
amended, or the comparison changes — the conflict has been resolved or has shifted, and
`B-183`'s routing must be re-derived instead of assumed.

**Not asserted:** which reading is correct, and whether `observation_window` should be read.
The time dimension is downstream of the quantity, and `§11.4` defers thresholds to
implementation discretion in any case.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.persona_tier import PersonaTier
from harness_od.multi_tenant_cross_cutting_enforcement import (
    CardinalityCounters,
    PerTenantCardinalityViolation,
    assert_per_tenant_cardinality_isolation,
)
from harness_od.observability_matrix import CellID
from harness_od.per_cell_cardinality_budget import PER_CELL_CARDINALITY_BUDGET

_SUBSTRATE = Path(__file__).resolve().parents[2] / "design-substrate"

_MTC_SELF = CellID(
    persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)


def _read(name: str) -> str:
    path = _SUBSTRATE / name
    if not path.exists():  # pragma: no cover - corpus moved
        pytest.skip(f"{name} is absent; re-ground B-183 before trusting this module")
    return path.read_text(encoding="utf-8")


# --- declaration 1: the contract frames it as CARDINALITY ---------------------


def test_c_od_11_frames_the_budget_as_cardinality() -> None:
    spec = _read("Spec_Operational_Discipline_v1_2.md")
    assert "## §11 C-OD-11 — Cardinality budget per cell" in spec, (
        "C-OD-11's cardinality framing moved — the first horn of B-183's quantity conflict "
        "is gone and the row must be re-derived"
    )
    assert "**Per-tenant cardinality isolation**" in spec, (
        "C-OD-21 §21.4's per-tenant CARDINALITY isolation row moved"
    )


# --- declaration 2: the plan signature and two spec deltas say SPANS/SEC ------


def test_the_plan_signature_declares_spans_per_second() -> None:
    """The declaration an earlier pass of this arc mistook for a stray docstring."""
    plan = _read("Implementation_Plan_Operational_Discipline_v2.md")
    assert "// per-cell global rate limit (spans/sec)" in plan, (
        "the OD plan's own field signature no longer says spans/sec — the second horn of "
        "B-183's conflict may be resolved; re-derive the row rather than assuming"
    )


def test_two_cleared_spec_deltas_quantify_the_tenant_budget_in_spans_per_second() -> None:
    v37 = _read("Spec_Operational_Discipline_v1_37.md")
    assert "tenant_rate_limit=1_000.0` spans/sec at the two multi-tenant cells" in v37, (
        "v1.37 no longer quantifies the per-tenant budget in spans/sec"
    )
    v38 = _read("Spec_Operational_Discipline_v1_38.md")
    assert "1,000 spans/sec budget" in v38, (
        "v1.38 no longer quantifies the C-OD-11 §11.1 budget in spans/sec"
    )


# --- declaration 3: the code compares SERIES ----------------------------------


def test_the_shipped_comparison_is_against_distinct_series() -> None:
    """`observed_series` is a count of distinct attribute-value series, not of spans.

    Driven through the real function so this is the shipped semantics, not a reading of it.
    """
    limit = PER_CELL_CARDINALITY_BUDGET[_MTC_SELF].tenant_rate_limit
    assert limit == 1000.0, f"the per-tenant limit moved to {limit}; B-183 quotes 1000.0"

    within = CardinalityCounters(tenant_id="t", observed_series=int(limit), observation_window="1s")
    assert assert_per_tenant_cardinality_isolation("t", _MTC_SELF, within) is None

    over = CardinalityCounters(
        tenant_id="t", observed_series=int(limit) + 1, observation_window="1s"
    )
    with pytest.raises(PerTenantCardinalityViolation):
        assert_per_tenant_cardinality_isolation("t", _MTC_SELF, over)


def test_the_observation_window_is_still_ignored_by_the_comparison() -> None:
    """The time dimension is dropped — but it is DOWNSTREAM of the quantity question.

    Two identical series counts over wildly different windows are treated identically. That
    is only a defect once the quantity is settled: under a standing-cardinality reading it
    may be correct, and under a spans/sec reading it is not. B-183 routes the quantity first.
    """
    limit = int(PER_CELL_CARDINALITY_BUDGET[_MTC_SELF].tenant_rate_limit or 0)
    for window in ("1s", "1m", "24h"):
        over = CardinalityCounters(
            tenant_id="t", observed_series=limit + 1, observation_window=window
        )
        with pytest.raises(PerTenantCardinalityViolation):
            assert_per_tenant_cardinality_isolation("t", _MTC_SELF, over)


def test_the_conflict_is_between_two_non_interchangeable_quantities() -> None:
    """The reason this is a decision and not a tidy-up.

    One series carries arbitrarily many spans, so `spans/sec` and `distinct series` cannot
    both describe the same threshold. Pinned as an explicit statement so no future reader
    treats the docstring and the comparison as trivially reconcilable.
    """
    budget = PER_CELL_CARDINALITY_BUDGET[_MTC_SELF]
    assert budget.tenant_rate_limit is not None
    counters = CardinalityCounters(tenant_id="t", observed_series=1, observation_window="1s")
    assert counters.observed_series == 1, (
        "one observed SERIES — which may carry any number of spans. The comparison treats "
        "this as one unit against a limit the plan signature calls spans/sec."
    )

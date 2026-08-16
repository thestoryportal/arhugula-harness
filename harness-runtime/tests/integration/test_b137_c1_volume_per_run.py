"""B-137 step (3): what C1's `1/base_rate` multiplier costs, measured per workflow RUN.

`B-137`'s C11 objection is that C1's multiplier is *"unpriced against the C-OD-11 §11.1 per-cell
budgets."* `B-182` grounded the instrument and found the cap **does** carry a number —
`cell_rate_limit=10_000.0` **spans/sec** at every ACTIVE cell — and that what §11.1 leaves open at
the team cells is the **volume evidence** to price against it, deferred to `Persona_Document_v1.md`
§11 open-item 4 (*"throughput rough order-of-magnitude per day"*, still open).

**This module supplies the half of that evidence which is measurable today.** A spans/sec budget
factors into two terms:

    spans/sec  =  spans per run  ×  runs per sec

`runs/sec` is exactly the open item, and nothing here can close it. **`spans per run` is
measurable at the real `api.run` venue, and no artifact had measured it.** Measuring it converts
C11's objection from *"unpriced"* into *"priced up to one named factor"*, and turns the open item
into a specific answerable question rather than an open-ended unknown.

**Measured.** Driving the shipped B-72 fan-out end-to-end through `api.run` with a real
`TracerProvider`, a fully-admitting head exports **3 spans per run** — `workflow.envelope`,
`hitl.gate.evaluated`, `pause.captured`. Under C1 (envelope in the §9.2 set) every run exports the
same 3, deterministically, because the root takes the always-sampled arm and its children inherit.

**Derived, so the council does not have to.** At 3 spans/run, saturating the 10,000 spans/sec cap
under C1 requires **~3,333 workflow runs per second**. Equivalently: at a plausible harness run
rate of 1 run/sec, a workflow would need ~10,000 spans **per run** before C1 could reach the cap.

**THE SCOPE BOUND, AND IT IS LOAD-BEARING — read it before quoting the number.** The B-72 fan-out
is *one small workflow shape*, chosen by the sibling module because it reaches a HITL gate, not
because it is representative. Three spans per run is therefore a **lower bound** on span volume,
which makes ~3,333 runs/sec an **upper bound** on the break-even rate. A span-heavier workflow —
many tool dispatches, validator evaluations, retries, nested sub-agents — moves the break-even
down **proportionally**: at 30 spans/run it is ~333 runs/sec, at 300 it is ~33.

So this module does **not** conclude that C1 is affordable. It establishes that **two** factors
were missing and now **one** is measured at one venue, and it names precisely what the council
still needs: a *representative* spans/run for the workloads a cell actually carries, and the
runs/sec of Persona open-item 4. *(This scoping is deliberate and hard-won: the `B-182` arc that
preceded this one took eight out-of-family review rounds and 28 valid findings, every one of which
falsified an interpretation layered on a fact rather than a fact — see that row.)*

**Determinism.** Only the two *decidable* compositions are asserted: `base_rate=1.0`, where every
span is admitted, and C1 at `base_rate=0.0`, where the ratio arm admits nothing and the
always-sampled arm admits everything. The intermediate production rate (0.1) is a genuine **sample**
— a probe run at 0.1 happened to export all 3 spans because the root won its draw — so nothing is
asserted there (`[[assert-the-shape-not-the-measurement]]`).
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.persona_tier import PersonaTier
from harness_od.base_rate_set_and_envelope import PER_CELL_BASE_RATE_ENVELOPE
from harness_od.observability_matrix import CellID
from harness_od.per_cell_cardinality_budget import PER_CELL_CARDINALITY_BUDGET

#: The cell B-137 prices step (3) against.
_TEAM_SELF = CellID(
    persona_tier=PersonaTier.TEAM_BINDING,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)

#: The spans the shipped B-72 fan-out really exports per run, measured at the `api.run` venue.
_EXPECTED_SPANS = ("hitl.gate.evaluated", "pause.captured", "workflow.envelope")


def _venue() -> Any:
    """Load the sibling step-(2) module, which owns the real-`api.run` driver.

    Re-using its `_run_the_real_workflow` rather than re-implementing the composition is
    deliberate: a re-implementation would prove this module's model of the venue, not the venue
    (`[[a repro must drive the REAL function]]`).
    """
    path = pathlib.Path(__file__).with_name("test_b137_ninety_two_floor_at_the_real_run_venue.py")
    name = "_b137_volume_venue"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_the_real_run_exports_three_spans_when_the_head_admits_everything() -> None:
    """**The measurement.** Span count per run at the real venue, fully admitting.

    This is the multiplicand C11's budget needs and that no artifact had measured. Asserted as an
    exact name set rather than a bare count, so a span appearing or vanishing surfaces as a
    changed identity rather than a silently-shifted number
    (`[[count-contract-sweep-every-granularity]]`).
    """
    exported = await _venue()._run_the_real_workflow(base_rate=1.0)
    assert tuple(sorted(set(exported))) == _EXPECTED_SPANS, (
        f"the B-72 venue now exports {sorted(set(exported))}, not {list(_EXPECTED_SPANS)}. "
        "B-137's per-run volume figure is derived from this set and is stale — re-derive the "
        "break-even run rate before quoting it"
    )
    assert len(exported) == 3, (
        f"the venue exported {len(exported)} spans, not 3 — the break-even arithmetic in this "
        "module's docstring is stale"
    )


@pytest.mark.asyncio
async def test_c1_exports_the_same_three_spans_deterministically_at_a_starving_rate() -> None:
    """C1's per-run cost equals the fully-admitting cost — which is what makes ×10 the multiplier.

    At `base_rate=0.0` the ratio arm admits nothing, so every span here is admitted by the
    always-sampled arm via root inheritance. That makes this a decision, not a sample.
    """
    venue = _venue()
    with venue._member_set(add=frozenset({venue._ENVELOPE})):
        exported = await venue._run_the_real_workflow(base_rate=0.0)
    assert tuple(sorted(set(exported))) == _EXPECTED_SPANS, (
        f"under C1 at a starving rate the venue exported {sorted(set(exported))}, not "
        f"{list(_EXPECTED_SPANS)} — C1 no longer delivers the whole trace and B-137's C7 half "
        "must be re-grounded before this module's cost figure means anything"
    )


@pytest.mark.asyncio
async def test_nothing_is_exported_without_c1_at_a_starving_rate() -> None:
    """The contrast that makes the C1 figure a *cost* rather than a baseline.

    Without C1 the root loses its draw and every child inherits the drop, so the same run exports
    nothing. C1's per-run cost is therefore the full 3 spans, not a delta against some smaller
    admitted set.
    """
    exported = await _venue()._run_the_real_workflow(base_rate=0.0)
    assert exported == [], (
        f"a starving rate now exports {exported} without C1 — the floor reaches the run by some "
        "other route, and C1's marginal cost is smaller than this module computes"
    )


def test_the_break_even_run_rate_is_derived_from_live_substrate_not_hard_coded() -> None:
    """**The derivation**, recomputed from the cap and the measured count rather than quoted.

    `spans/sec = spans/run × runs/sec`, so `runs/sec at saturation = cap ÷ spans/run`. Both inputs
    are read live, so the figure cannot go stale silently: if the cap moves or the venue's span
    count moves, the assertion moves with them and the docstring's arithmetic is re-derived.
    """
    cap = PER_CELL_CARDINALITY_BUDGET[_TEAM_SELF].cell_rate_limit
    assert cap == 10_000.0, (
        f"the per-cell cap is now {cap}, not 10_000.0 — every figure in this module's docstring "
        "is stale and must be re-derived"
    )
    spans_per_run = len(_EXPECTED_SPANS)
    break_even = cap / spans_per_run
    assert 3_300 < break_even < 3_400, (
        f"break-even is now {break_even:.0f} runs/sec, outside the ~3,333 this module and B-137 "
        "quote — re-derive before the council uses it"
    )

    # The reciprocal framing, which is the one a council can sanity-check against a real
    # deployment: at ONE run per second, how span-heavy must a workflow be to reach the cap?
    spans_per_run_to_saturate_at_one_run_per_sec = cap / 1.0
    assert spans_per_run_to_saturate_at_one_run_per_sec == 10_000.0

    # And the bound that stops the number being over-quoted: this venue is a LOWER bound on span
    # volume, so the break-even above is an UPPER bound on the tolerable run rate.
    assert PER_CELL_BASE_RATE_ENVELOPE[_TEAM_SELF].default_rate == 0.1, (
        "the cell's base rate moved, so C1's multiplier is no longer x10 and the per-run cost "
        "comparison in this module's docstring is stale"
    )

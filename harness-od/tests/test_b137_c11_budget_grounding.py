"""B-137 step (3), C11 half: what the §11.1 per-cell budget actually commits and enforces.

B-137's step (3) council is declared **dyadic C7 ⊥ C11** — an observability floor (C7) against
telemetry volume and *"the C-OD-11 §11.1 per-cell budgets those caps were sized against"* (C11).
`#1362` measured the C7 half. This module grounds the C11 half.

**A first draft of this module overclaimed in four places; out-of-family Codex round 1 raised
five [P2]s and all five were valid. The corrections are recorded here because the withdrawn
claims were the interesting ones, and a reader who only sees the survivors would re-derive them.**

1. **WITHDRAWN — the "dependency cycle".** The draft argued §11.1's team budget defers to an
   open item closable only from operational telemetry, that B-137 starves that telemetry, and
   therefore that the budget is *unpriceable*: *"you cannot measure throughput from a stream you
   are dropping 90% of."* **That is false, and the spec says so.** C-OD-16 §16.2 provides for
   exactly this: *"at sampled rates below 1.0, the dashboard cost rollup is scaled by
   `1/base_rate` for unbiased cost estimation."* A known-rate sample estimates an aggregate
   fine, and Persona open-item 4 asks for a *rough order-of-magnitude per day* — an aggregate.
   The cycle is refuted for the thing the open item actually asks for, and is withdrawn.
2. **CORRECTED — "both enforcement layers are out-of-process."** False. `COLLECTOR_BOUNDARY` is
   the **in-process** OTLP collector against the sqlite ring-buffer
   (`per_cell_cardinality_budget.py:69-70`), and **4 of the 8 ACTIVE cells** resolve to it. This
   correction *strengthens* the finding rather than dissolving it — see below.
3. **WITHDRAWN — "uniform ⇒ placeholder."** A per-cell cap may legitimately be identical across
   cells when it represents shared collector or backend capacity. Uniformity is reported; the
   inference to *placeholder* is not drawn.
4. **FIXED — the spec read was baseline-only.** The draft read `Spec_Operational_Discipline_v1_2.md`
   alone. OD is a **delta chain** (42 files, head v1.41) that preserves prior bodies verbatim, so a
   later delta could re-table §11.1 with a number and leave an anti-rot test green. Every spec
   assertion now scans the whole chain.

**What survives, and it is sharper than the draft.**

**Round 2 raised three more [P2]s, also all valid, and they hardened rather than reversed the
findings:** the (A) check tested *presence anywhere* rather than the **effective** declaration
(a later delta could add a number while the historical row survived — reproduced with a
synthetic v1.42); the in-process check asserted the collector-boundary set's *cardinality*
rather than its *identities* (swapping two cells kept the count at four while inverting which
cells are in-process); and this arc's own rewrite had **destroyed** a cite correction landed at
`#1362`, which is restored in the register. The first two are pinned in the tests below.

**(A) §11.1 commits NO number at the team-binding cells.** Its table gives solo cells a concrete
posture (*"default 1.0; rotation handles volume"*) and multi-tenant cells per-tenant isolation,
but the team-binding row — covering exactly the cell B-137 prices against — defers verbatim to
*"Persona §11.4 throughput rough order-of-magnitude open item; envelope refines downstream of
§11.4 closure."* Resolved at the **effective** declaration: of every chain file carrying a §11.1
team-binding row at all, the highest-versioned one carries the deferral.

**(B) The deferral target is still open** — `Persona_Document_v1.md` **§11 Open items, row 4**
(a table row, not a subsection; the draft's first pass searched for a `§11.4` heading, found
nothing, and nearly filed the cite as dangling). It is *closable* (per correction 1); it is not
*closed*. So the team-cell budget has no committed figure today, which is all C11's objection
needs to be about — and less than the draft claimed.

**(C) The in-process cap is declared and read by nothing, at the cells where it IS in-process.**
`per_cell_cardinality_budget.py:118` commits a flat `cell_rate_limit=10_000.0` spans/sec at every
ACTIVE cell, with **zero readers** anywhere in `harness-*/src` outside its own declaration. Its
sibling `tenant_rate_limit` **is** genuinely enforced — witnessed behaviourally below, not by
token scan. **The correction in (2) is what makes this load-bearing:** at the 4 cells resolving
to `COLLECTOR_BOUNDARY`, §11.1's enforcement point is the harness's *own* in-process collector,
so an absent reader there cannot be explained as "an out-of-process consumer handles it." At the
4 `BACKEND_INGESTION` cells that explanation does hold. The disposition therefore **splits by
enforcement layer**, and `B-182` carries it that way.

**What this module does NOT establish.** Nothing here says C1 is affordable, or unaffordable. A
real collector or backend would still see `1/base_rate` more spans under C1 and shed the excess;
OD spec v1.37 ruled (for `B-133`'s F-08 rider) that these caps enforce *"independently of any
sampling decision."* The affordability call is **unaffected and still owed**. What changes is
narrower: at the team cells C11's objection names, §11.1 carries no figure to price against, and
at half the cells the cap has no enforcement site at the layer §11.1 nominates.

**A question this raises, registered rather than asserted.** If the effective cap is a rate
limiter, raising head admission does not *breach* the budget — it **relocates the drop**, from a
ratio-based decision at the SDK to a rate-based one at the cap. A rate limiter carries no §9.2
membership knowledge, so the floor C1 exists to deliver could be shed one hop later. Not claimed
here; it is the shape of question that discriminates C1 from candidate A, and no artifact asks it.

**Grounding, not behaviour** — except where a behavioural witness is available, which after
correction (4) it is for the tenant limit. These are anti-rot pins on facts a council decision
will rest on; each assertion states what goes stale if it moves.
"""

from __future__ import annotations

import pathlib
import re

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.persona_tier import PersonaTier
from harness_od.base_rate_set_and_envelope import PER_CELL_BASE_RATE_ENVELOPE
from harness_od.multi_tenant_cross_cutting_enforcement import (
    CardinalityCounters,
    PerTenantCardinalityViolation,
    assert_per_tenant_cardinality_isolation,
)
from harness_od.observability_matrix import CellID
from harness_od.per_cell_cardinality_budget import PER_CELL_CARDINALITY_BUDGET

_REPO = pathlib.Path(__file__).resolve().parents[2]
_SUBSTRATE = _REPO / "design-substrate"
_PERSONA = _SUBSTRATE / "Persona_Document_v1.md"

#: The cell B-137 prices step (3) against.
_TEAM_SELF = CellID(
    persona_tier=PersonaTier.TEAM_BINDING,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)
#: A multi-tenant cell — the only class carrying an enforced per-tenant limit.
_MTC_SELF = CellID(
    persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)


def _od_spec_chain() -> list[pathlib.Path]:
    """Every file in the OD spec delta chain, not just the v1.2 baseline.

    Correction (4): OD is a delta chain whose head is v1.41 and whose deltas preserve prior
    bodies verbatim. Reading only the baseline lets a later delta re-table §11.1 with a number
    while every anti-rot assertion here stays green — which would defeat `B-182`'s own falsifier.
    """
    chain = sorted(_SUBSTRATE.glob("Spec_Operational_Discipline_v1*.md"))
    assert len(chain) >= 40, (
        f"only {len(chain)} OD spec files found — the chain glob is wrong, and a 'no delta "
        "states a number' result would be an artifact of not looking, not a fact"
    )
    return chain


def _chain_version(path: pathlib.Path) -> tuple[int, int]:
    """Order a chain file by its version, so "latest" means latest and not lexicographic.

    `..._v1_37.md` → `(1, 37)`. The unsuffixed baseline and its ` (1)` / ` (2)` copies carry no
    delta number and sort as `(1, 0)`.
    """
    m = re.search(r"_v(\d+)_(\d+)\.md$", path.name)
    return (int(m.group(1)), int(m.group(2))) if m else (1, 0)


def test_the_effective_team_binding_budget_is_still_the_deferral_not_a_number() -> None:
    """**(A)** The budget B-137 would be priced against is DEFERRED — at the EFFECTIVE head.

    **Out-of-family Codex round 2 [P2]:** a first version asserted only that the deferral row is
    *present somewhere* in the chain. A later delta could add a numeric team-binding budget while
    the historical v1.2 row survives verbatim — presence stays true, the test stays green, and
    `B-182`'s central claim silently becomes false. Codex reproduced this with a synthetic v1.42.

    So this resolves the **effective** declaration: of every chain file that carries a §11.1
    team-binding cardinality row at all, the highest-versioned one must carry the deferral.

    The solo row's concreteness is the contrast that makes the team row's silence a deliberate
    deferral rather than the table simply being non-numeric.
    """
    row_prefix = "| team-binding × * | Per-cell cardinality budget"
    deferral = (
        "| team-binding × * | Per-cell cardinality budget bounded per Persona §11.4 "
        "throughput rough order-of-magnitude open item; envelope refines downstream of "
        "§11.4 closure |"
    )
    carriers = [p for p in _od_spec_chain() if row_prefix in p.read_text()]
    assert carriers, (
        "no OD chain file carries a §11.1 team-binding cardinality row at all — the row was "
        "removed or reworded, and B-182's (A) must be re-grounded from scratch"
    )
    effective = max(carriers, key=_chain_version)
    assert deferral in effective.read_text(), (
        f"the EFFECTIVE §11.1 team-binding row now lives at {effective.name} and is not the "
        "deferral. A delta has superseded it — if it states a figure, C11's objection became "
        "priceable and B-137 step (3) must be re-argued against that number"
    )
    baseline = _SUBSTRATE / "Spec_Operational_Discipline_v1_2.md"
    assert "default 1.0; rotation handles volume" in baseline.read_text(), (
        "§11.1's solo row no longer commits a concrete posture — without that contrast the "
        "team row's deferral cannot be read as deliberate"
    )


def test_the_deferral_target_is_still_an_open_item() -> None:
    """**(B)** `Persona §11.4` is §11 *Open items*, row 4 — and it is still open.

    Deliberately NOT asserting the withdrawn "unpriceable" cycle (correction 1). The claim is
    only that no figure is committed today, which is what C11's objection rests on.
    """
    persona = _PERSONA.read_text()
    assert "## §11 Open items" in persona, (
        "Persona §11 is no longer an Open-items section — the `Persona §11.4` cite in "
        "C-OD-11 §11.1 resolves differently now and this module's reading is stale"
    )
    row4 = (
        "| 4 | Throughput rough order-of-magnitude per day | Dim 3 follow-up | "
        "Emerges from operational telemetry once harness is running |"
    )
    assert row4 in persona, (
        "Persona §11 open-item 4 is not the verbatim row this module quotes. If it CLOSED, the "
        "team-cell budget has a figure and B-137's C11 half becomes priceable — re-derive "
        "before deciding step (3)"
    )


def test_the_sampled_stream_is_estimable_by_contract_so_the_cycle_claim_stays_withdrawn() -> None:
    """**Correction 1, pinned so the withdrawn claim cannot quietly return.**

    C-OD-16 §16.2 scales sub-1.0 observations by `1/base_rate` for unbiased estimation. That is
    the contract term which refutes "a starved stream cannot yield a throughput figure", and it
    is why B-182 carries no circularity premise. Pinned because the cycle is a seductive
    argument that a future reader (or a future me) would otherwise re-invent.
    """
    baseline = (_SUBSTRATE / "Spec_Operational_Discipline_v1_2.md").read_text()
    scaling = (
        "at sampled rates below 1.0, the dashboard cost rollup is scaled by `1/base_rate` "
        "for unbiased cost estimation"
    )
    assert scaling in baseline, (
        "C-OD-16 §16.2's `1/base_rate` unbiased-estimation term is gone. It is the sole "
        "grounds on which this arc withdrew its dependency-cycle claim — if the term was "
        "removed, that withdrawal must be re-examined rather than assumed"
    )


def test_the_flat_cap_has_no_contract_provenance_only_a_citation_of_the_code() -> None:
    """**(C) provenance** — the number lives in code; the chain references it by citing code.

    Reported precisely rather than as "the spec never states it" (which was true only of the
    baseline read). Exactly one delta mentions the figure, and it does so by quoting the
    implementation carrier, which is a citation of code and not a contract declaration.
    """
    mentions = [p.name for p in _od_spec_chain() if "10_000" in p.read_text()]
    assert mentions == ["Spec_Operational_Discipline_v1_37.md"], (
        f"the OD chain's references to the flat cap changed to {mentions}; B-182 states that "
        "exactly one delta mentions it and does so by citing the code carrier — re-ground"
    )
    v137 = (_SUBSTRATE / "Spec_Operational_Discipline_v1_37.md").read_text()
    assert "per_cell_cardinality_budget.py" in v137, (
        "v1.37 now states the cap WITHOUT citing the implementation carrier — that would make "
        "it a contract declaration rather than a citation of code, giving C11's objection the "
        "provenance B-182 says it lacks"
    )


def test_the_cap_is_uniform_across_cells_whose_base_rates_are_not() -> None:
    """**(C) shape** — reported, with NO inference to "placeholder" (correction 3).

    A uniform cap may legitimately represent shared collector or backend capacity. The fact is
    recorded because a council reading "budgets those caps were sized against" should know the
    caps do not vary with the rates; what it means is left to the adjudication B-182 owes.
    """
    limits = {b.cell_rate_limit for b in PER_CELL_CARDINALITY_BUDGET.values()}
    assert limits == {10_000.0}, (
        f"cell_rate_limit is now {sorted(limits)} rather than a uniform 10_000.0 — B-137's C11 "
        "analysis quotes the uniform value and is stale"
    )
    rates = {PER_CELL_BASE_RATE_ENVELOPE[c].default_rate for c in PER_CELL_CARDINALITY_BUDGET}
    assert len(rates) > 1, (
        "every ACTIVE cell now shares one base rate, so 'uniform cap over non-uniform rates' "
        "is no longer a fact worth reporting to the council"
    )


def test_half_the_cells_enforce_in_process_yet_nothing_reads_the_cell_cap() -> None:
    """**The sharpened finding** — correction 2 turned into the result.

    At `COLLECTOR_BOUNDARY` cells §11.1's enforcement point is the harness's OWN in-process
    collector, so an absent reader there cannot be explained away as "an out-of-process consumer
    handles it." That explanation does hold at `BACKEND_INGESTION` cells. Hence B-182's
    disposition splits by enforcement layer instead of treating all 8 cells alike.

    **Out-of-family Codex round 2 [P2]:** a first version asserted only that the in-process set
    has FOUR members. Swapping one collector-boundary cell for one backend-ingestion cell keeps
    the count at four while changing *which* cells are in-process — and in particular whether
    B-137's own target cell (`team-binding × self-hosted-server`) is among them, which would
    invert this row's scoping. The exact identities are therefore asserted, not the cardinality.
    """
    in_process = {
        f"{c.persona_tier.value}×{c.deployment_surface.value}"
        for c, b in PER_CELL_CARDINALITY_BUDGET.items()
        if b.enforcement_layer == "COLLECTOR_BOUNDARY"
    }
    expected = {
        "solo-developer×local-development",
        "solo-developer×self-hosted-server",
        "solo-developer×managed-cloud",
        "multi-tenant-compliance×self-hosted-server",
    }
    assert in_process == expected, (
        f"the COLLECTOR_BOUNDARY cell set is now {sorted(in_process)}, not {sorted(expected)}. "
        "B-182 scopes its in-process half to exactly these cells and must be re-scoped — and if "
        "team-binding×self-hosted-server entered the set, B-137's own target cell became "
        "in-process and this row's whole disposition inverts"
    )
    assert PER_CELL_CARDINALITY_BUDGET[_TEAM_SELF].enforcement_layer == "BACKEND_INGESTION", (
        "B-137's target cell now enforces at COLLECTOR_BOUNDARY — the out-of-process "
        "explanation no longer covers it and B-182's (C) applies there directly"
    )

    src_files = [p for d in sorted(_REPO.glob("harness-*/src")) for p in d.rglob("*.py")]
    assert len(src_files) > 100, (
        f"only {len(src_files)} src files found — the scan root is wrong and a 'no reader' "
        "result would be an artifact of not looking (never report unlooked as empty)"
    )
    decl = _REPO / "harness-od" / "src" / "harness_od" / "per_cell_cardinality_budget.py"
    readers = sorted(
        str(p.relative_to(_REPO))
        for p in src_files
        if p != decl and re.search(r"\bcell_rate_limit\b", p.read_text())
    )
    assert readers == [], (
        f"`cell_rate_limit` acquired a reader at {readers} — the per-cell cap is now consulted "
        "in-process, which gives C11's objection a real instrument and closes B-182's (C)"
    )


def test_the_tenant_limit_is_enforced_behaviourally_not_merely_referenced() -> None:
    """**Correction 4 for the sibling half** — a behavioural witness, not a token scan.

    The draft established `tenant_rate_limit`'s enforcement by regex, which would stay green if
    the comparison and raise were deleted while a docstring mention survived. This drives the
    real function on both sides of the limit, so the asymmetry B-182 rests on ("the half C11
    names is unenforced while its sibling is not") is witnessed rather than asserted.
    """
    limit = PER_CELL_CARDINALITY_BUDGET[_MTC_SELF].tenant_rate_limit
    assert limit == 1000.0, (
        f"the multi-tenant per-tenant limit moved to {limit}; this witness pins 1000.0"
    )

    within = CardinalityCounters(
        tenant_id="t1", observed_series=int(limit), observation_window="1m"
    )
    assert assert_per_tenant_cardinality_isolation("t1", _MTC_SELF, within) is None, (
        "the tenant limit now rejects an observation AT the limit — boundary semantics changed"
    )

    over = CardinalityCounters(
        tenant_id="t1", observed_series=int(limit) + 1, observation_window="1m"
    )
    with pytest.raises(PerTenantCardinalityViolation):
        assert_per_tenant_cardinality_isolation("t1", _MTC_SELF, over)

    # The contrast that makes this an ASYMMETRY: no equivalent callable exists for the cell cap.
    # If one appears, the enforced/unenforced split B-182 rests on has closed.
    assert PER_CELL_CARDINALITY_BUDGET[_TEAM_SELF].tenant_rate_limit is None, (
        "the team cell acquired a per-tenant limit — the multi-tenant-only scoping of the "
        "enforced half no longer holds"
    )


def test_the_cell_this_is_all_priced_against_still_carries_its_rate() -> None:
    """Anti-rot pin on the one figure the C11 narrative quotes.

    The `×10` reading is correct only while this cell carries 0.1. The envelope's `max_rate` is
    pinned too: a x5 rise over the default is ALREADY operator-tunable under the cleared §10.3
    envelope, which is context the council should have before treating any increase as novel.
    """
    env = PER_CELL_BASE_RATE_ENVELOPE[_TEAM_SELF]
    assert env.default_rate == 0.1, (
        f"team×self-hosted default rate is now {env.default_rate}, so C1's in-envelope "
        f"multiplier reads ×{1 / env.default_rate:g}, not ×10 — re-price step (3)"
    )
    assert env.max_rate == 0.5, (
        f"team×self-hosted max_rate moved to {env.max_rate}; the council's sense of how much "
        "volume increase the cleared envelope already permits at this cell is stale"
    )

"""B-137 step (3), C11 half: what the §11.1 per-cell budget actually commits and consumes.

B-137's step (3) council is declared **dyadic C7 ⊥ C11** — an observability floor (C7) against
telemetry volume and *"the C-OD-11 §11.1 per-cell budgets those caps were sized against"* (C11).
`#1362` measured the C7 half. This module grounds the C11 half.

**Read this first: the arc that produced this module was wrong five times, and the shape of the
error is worth more than most of what survived.** Out-of-family Codex reviewed it across five
rounds and raised **19 valid findings**, including four [P1]s. Every one of them falsified an
*interpretation* this arc layered on top of its facts; **none falsified a fact.** The recurring
mistake was always the same: **inferring contract meaning from an implementation carrier instead
of reading the canonical matrix that already answered the question.** Concretely —

- Placement was "derived" by filtering the implementation's logical `COLLECTOR_BOUNDARY` mapping
  by persona name, twice (first "four cells in-process", then "three solo cells"). **C-OD-20
  §20.1 is a per-cell collector placement matrix and it existed the whole time.** Read against
  it, exactly ONE cell is unambiguously in-process.
- Provenance was "derived" from the number's absence in the v1.2 baseline. **`Spec_Operational_
  Discipline_v1_37.md` states the figure in canonical spec text** and uses it to declare a budget
  check passed; naming the carrier alongside does not make it non-contractual.
- An enforcement *asymmetry* was asserted between the two caps. **Neither cap is reached in
  production** — the tenant helper has no call site either.
- A *dependency cycle* was asserted, then "refuted" via C-OD-16 §16.2's `1/base_rate` rescaling,
  and the refutation was itself wrong (§16.2 is unbiased only for a uniformly sampled stream;
  this one is not). **Neither the cycle nor its refutation is established.**
- A *placeholder* inference was drawn from the cap's uniformity across cells. A uniform cap may
  simply represent shared capacity.

**So this module now asserts FACTS ONLY, and `B-182` records facts only.** The interpretation is
left to whoever dispositions it, with the canonical instruments named.

**The facts, each mutation-probed or anti-rot-guarded.**

1. `cell_rate_limit` (flat `10_000.0` at every ACTIVE cell) has **zero readers** anywhere in
   `harness-*/src` outside its own declaration.
2. `assert_per_tenant_cardinality_isolation` — the only implemented consumer of the sibling
   `tenant_rate_limit` — has **no call site in `harness-*/src`** either. It has real semantics
   (it raises), but nothing reaches it. **Neither cap is enforced on any production path.**
3. §11.1's **team-binding** row commits no figure; it defers to *"Persona §11.4 throughput rough
   order-of-magnitude open item."* Resolved at the **effective** declaration across the whole
   42-file OD delta chain, not the baseline alone.
4. That target is `Persona_Document_v1.md` **§11 Open items, row 4** (a table row, not a
   subsection) and is still **open**.
5. **C-OD-20 §20.1** is the canonical placement instrument; per it, only
   `solo-developer × local-development` is unambiguously in-process.

**What this module does NOT establish.** Whether C1 is affordable; whether the §11.1 caps are
correctly external; how many cells are in-process beyond fact 5; whether the throughput figure is
recoverable from a starved stream. The affordability call B-137's council owes is **untouched**.

**A LATENT defect surfaced in passing, registered as `B-183`** (latent, not live — no production
caller): `tenant_rate_limit` is documented in **spans**/sec while `observed_series` counts
**distinct series**, and `assert_per_tenant_cardinality_isolation` compares them directly while
never reading `observation_window`. Two mismatched quantities *and* a dropped time dimension; the
quantity must be settled before the unit. Not repaired here.
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
from harness_od.sampling_mode import is_always_sampled

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

    # Round 6 [P2]: selecting the effective carrier by `row_prefix` alone is a false-green
    # surface. A later delta could supersede the team budget with a differently-SHAPED row (per
    # deployment surface, different wording), which `row_prefix` would not match — so that file
    # is excluded from `carriers`, the historical v1.2 deferral stays "effective", and the test
    # passes while the claim is false. Guard by failing on ANY later §11.1 team-binding
    # amendment this matcher does not recognise, rather than silently ignoring it.
    newest_carrier = max(carriers, key=_chain_version)
    # A delta SUPERSEDES a contract section by re-tabling it — i.e. carrying a `## §11 ` heading
    # of its own. Merely mentioning "§11.1" or "team-binding" in passing is not a supersession
    # (many deltas do, in unrelated riders), so the guard keys on the re-tabling shape.
    unrecognised = sorted(
        f.name
        for f in _od_spec_chain()
        if _chain_version(f) > _chain_version(newest_carrier)
        and "## §11 " in f.read_text()
        and row_prefix not in f.read_text()
    )
    assert unrecognised == [], (
        f"later OD delta(s) {unrecognised} RE-TABLE §11 without a team-binding row this matcher "
        "recognises. A re-tabling is how a delta supersedes a contract section, so these may "
        "replace the deferral with a differently-shaped row — which would make B-182's (A) "
        "false while this test stayed green. Read them and either extend the matcher or "
        "re-ground the claim"
    )

    effective = newest_carrier
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


def test_neither_the_cycle_claim_nor_its_refutation_is_established() -> None:
    """**Correction 1, twice-corrected — the honest terminal state is NEITHER claim.**

    Round 1 caught the draft's *dependency cycle* (*"you cannot measure throughput from a stream
    you are dropping 90% of"*) and offered C-OD-16 §16.2's `1/base_rate` scaling as the refutation.
    A first fix adopted that and called the cycle *refuted*.

    **Round 2 [P2] then caught the refutation itself.** §16.2's flat `1/base_rate` scaling is
    unbiased only for a *uniformly* sampled stream, and this stream is not uniform:
    `HarnessCompositeSampler` admits §9.2 names at 1.0 while ordinary roots take `base_rate`, so
    a flat rescale **overcounts** the always-sampled classes. §16.2 therefore does not establish
    that Persona's throughput figure is recoverable from the admitted stream.

    So the terminal position is **symmetric and deliberately weak**: the cycle is *not*
    established, and neither is its refutation. What §16.2 does show is that the spec
    **contemplates** estimating from a sub-1.0 stream — enough to make the draft's confident
    "unpriceable" claim unsupported, and not enough to assert the opposite. `B-182` therefore
    rests on neither, and this test pins **both** the term's presence and the non-uniformity that
    stops it from carrying more weight than that.
    """
    baseline = (_SUBSTRATE / "Spec_Operational_Discipline_v1_2.md").read_text()
    scaling = (
        "at sampled rates below 1.0, the dashboard cost rollup is scaled by `1/base_rate` "
        "for unbiased cost estimation"
    )
    assert scaling in baseline, (
        "C-OD-16 §16.2's `1/base_rate` scaling term is gone. B-182 cites it as evidence the "
        "spec CONTEMPLATES estimating from a sampled stream — if the term was removed, the "
        "withdrawal of the cycle claim must be re-examined rather than assumed"
    )
    # The non-uniformity that stops §16.2 from carrying the refutation: the head admits §9.2
    # names unconditionally while ordinary roots take the ratio, so one flat rescale cannot be
    # unbiased across both populations. If this stops being true, §16.2 gets stronger and the
    # symmetric "neither claim established" position should be revisited.
    assert is_always_sampled("sandbox.violation") is True, (
        "a §9.2 member is no longer admitted unconditionally — the stream may have become "
        "uniformly sampled, which would let §16.2's flat 1/base_rate rescale actually carry "
        "the refutation this arc declined to assert"
    )
    assert PER_CELL_BASE_RATE_ENVELOPE[_TEAM_SELF].default_rate < 1.0, (
        "the team cell now admits at full rate, so there is no sub-1.0 stream to estimate "
        "from and this whole line of argument is moot"
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
    # Rounds 3 AND 5 [P1]: `COLLECTOR_BOUNDARY` is a LOGICAL enforcement layer, not a process
    # placement, and filtering it by persona name is NOT a way to derive placement. The canonical
    # instrument is C-OD-20 §20.1's per-cell collector placement matrix, asserted separately at
    # `test_the_canonical_placement_matrix_is_the_instrument_for_process_placement`. This arc
    # inferred placement from the implementation carrier for three rounds before reading it.
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


def test_neither_cap_is_reached_in_production_only_their_semantics_differ() -> None:
    """**The asymmetry this arc claimed is FALSE — out-of-family Codex round 4 [P1].**

    Three drafts of this module claimed *"the half C11's objection names is unenforced while its
    sibling IS enforced."* That is wrong. `assert_per_tenant_cardinality_isolation` has **no call
    site anywhere in `harness-*/src`** — only its own definition, its `__all__` entry, two
    docstring mentions, and tests. So **neither** cap is reached on any production path.

    What actually differs is weaker, and is all `B-182` may now claim: `tenant_rate_limit` has an
    implemented, tested comparison with defined semantics that *a caller could* reach, while
    `cell_rate_limit` has **no consumer at all**, not even an unreached one. That is a difference
    in how much of the mechanism exists, not a difference between enforced and unenforced.

    The behavioural half is retained because it still establishes the helper's semantics (it
    really raises), which is what makes `B-183`'s dimensional finding meaningful — but the label
    on `B-183` is correspondingly *a defect in an uncalled helper*, not a live production defect.
    """
    src_files = [p for d in sorted(_REPO.glob("harness-*/src")) for p in d.rglob("*.py")]
    assert len(src_files) > 100, (
        f"only {len(src_files)} src files found — the scan root is wrong and a 'no caller' "
        "result would be an artifact of not looking"
    )
    decl = _REPO / "harness-od" / "src" / "harness_od" / "multi_tenant_cross_cutting_enforcement.py"
    callers = sorted(
        str(f.relative_to(_REPO))
        for f in src_files
        if f != decl and "assert_per_tenant_cardinality_isolation" in f.read_text()
    )
    assert callers == [], (
        f"`assert_per_tenant_cardinality_isolation` acquired a production caller at {callers}. "
        "The tenant cap is now genuinely reached, which RESTORES the enforced-vs-unenforced "
        "asymmetry B-182 withdrew and upgrades B-183 to a live production defect — both rows "
        "must be re-stated"
    )
    limit = PER_CELL_CARDINALITY_BUDGET[_MTC_SELF].tenant_rate_limit
    assert limit == 1000.0, (
        f"the multi-tenant per-tenant limit moved to {limit}; this witness pins 1000.0"
    )

    within = CardinalityCounters(
        tenant_id="t1", observed_series=int(limit), observation_window="1s"
    )
    assert assert_per_tenant_cardinality_isolation("t1", _MTC_SELF, within) is None, (
        "the tenant limit now rejects an observation AT the limit — boundary semantics changed"
    )

    over = CardinalityCounters(
        tenant_id="t1", observed_series=int(limit) + 1, observation_window="1s"
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


def test_the_canonical_placement_matrix_is_the_instrument_for_process_placement() -> None:
    """**Round 5 [P1] — the instrument this arc should have used from the start.**

    Three rounds of this arc derived "which cells are in-process" by filtering the
    implementation's logical `COLLECTOR_BOUNDARY` mapping by persona name. That is not a
    derivation of placement, and it produced a wrong answer twice (first "four cells", then
    "three solo cells"). **C-OD-20 §20.1 is the canonical per-cell collector placement matrix and
    it existed the whole time.** Read against it, exactly ONE cell is unambiguously in-process:

    - `solo-developer × local-development` — *"In-process otelcol-contrib + BatchSpanProcessor"*
    - `solo-developer × self-hosted-server` — in-process only *"permitted as alt-route"*, with the
      cell-committed backend's collector **preferred**
    - `solo-developer × managed-cloud` — *"Vendor-pipeline"*, not in-process at all

    So `B-182` makes **no** claim about how many cells are in-process. It records the two
    no-consumer facts and points at this matrix as the instrument for anyone dispositioning them.
    """
    spec = (_SUBSTRATE / "Spec_Operational_Discipline_v1_2.md").read_text()
    assert "### §20.1 Per-cell collector placement matrix" in spec, (
        "C-OD-20 §20.1's placement matrix is gone — it is the canonical instrument B-182 points "
        "at for process placement, and without it that pointer is dangling"
    )
    unambiguous = (
        "| solo-developer × local-development | In-process otelcol-contrib + "
        "BatchSpanProcessor; sqlite ring-buffer; TUI trace browser |"
    )
    assert unambiguous in spec, (
        "the one unambiguously in-process cell row changed. B-182 states that exactly one cell "
        "is unambiguously in-process per §20.1 — re-ground that claim"
    )
    alt_route = "In-process collector permitted as alt-route"
    assert alt_route in spec, (
        "solo × self-hosted-server no longer describes in-process as a permitted ALT-ROUTE. If "
        "it became the default, the in-process cell count rises and B-182's pointer needs a note"
    )

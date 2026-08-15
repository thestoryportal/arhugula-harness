"""B-137 step (3), C11 half: what the §11.1 per-cell budget actually commits and enforces.

B-137's step (3) is a posture fork whose council is declared **dyadic C7 ⊥ C11** — a real
observability floor (C7) against telemetry volume and *"the C-OD-11 §11.1 per-cell budgets
those caps were sized against"* (C11). The C7 half was measured at `#1362`. **This module
grounds the C11 half, and what it finds reframes the objection rather than pricing it.**

C11's objection, as the register states it, is that C1's `1/base_rate` in-envelope multiplier
is *"unpriced against the C-OD-11 §11.1 per-cell budgets."* Pricing it requires that those
budgets (a) commit a number at the cells in question, (b) be closable, and (c) be enforced.
Grounded at HEAD, **all three are weaker than the objection assumes**:

**(1) §11.1 commits NO number at the team-binding cells.** Its three-row table gives
solo-developer cells a concrete posture (*"default 1.0; rotation handles volume"*) and
multi-tenant cells per-tenant isolation, but the team-binding row reads, verbatim: *"Per-cell
cardinality budget bounded per Persona §11.4 throughput rough order-of-magnitude open item;
envelope refines downstream of §11.4 closure."* The budget at exactly the cells B-137 prices
against (`team-binding × self-hosted-server`, base rate 0.1) is **deferred, not stated**.

**(2) The deferral target is an OPEN item whose closing path is circular with B-137.**
*"Persona §11.4"* is not a subsection — it is **§11 Open items, row 4** of
`Persona_Document_v1.md`: *"Throughput rough order-of-magnitude per day | Dim 3 follow-up |
**Emerges from operational telemetry once harness is running**."* So the budget that would
price the fix can only close from operational telemetry — and B-137 is precisely the finding
that this telemetry is starved at these cells. **You cannot measure throughput from a stream
you are dropping 90% of.** That is a dependency cycle, and naming it is this module's point:
C11's instrument is not merely unpriced, it is not currently *priceable* by the route its own
contract nominates.

**(3) The one number in code is implementation-chosen, and the per-CELL half is enforced
NOWHERE.** `per_cell_cardinality_budget.py` commits a flat `cell_rate_limit=10_000.0` spans/sec
at every ACTIVE cell — a figure §11.1 never states, uniform across cells whose base rates span
0.1 to 1.0. `tenant_rate_limit` **is** genuinely enforced (`multi_tenant_cross_cutting_enforcement.py`
raises when observed series exceed it), but `cell_rate_limit` has **zero readers** anywhere in
`harness-*/src` outside its own declaration. In-process, nothing can breach it because nothing
consults it.

**What this does NOT establish — the boundary this module will not cross.** OD spec v1.37
adjudicated an adjacent question for `B-133`'s F-08 rider and ruled that the §11.1 caps enforce
*"at the COLLECTOR_BOUNDARY / BACKEND_INGESTION layer independently of any sampling decision."*
That ruling is about an **out-of-process** enforcement point — a real OTel collector or backend
— which this repo does not contain and these tests therefore cannot witness. So: **nothing here
says C1 is affordable.** A real collector-boundary limiter would still see `1/base_rate` more
spans under C1 and shed the excess. What the tests below establish is narrower and precise —
that the in-repo instrument C11's objection names does not currently carry, close, or enforce
the number the objection would need. **The council still owes the affordability call; it now
owes it against an honestly-described instrument.**

**A consequence worth the council's attention, stated as a question rather than a finding.**
If the effective cap is an out-of-process rate limiter, then raising head admission does not
breach the budget — it **relocates the drop**, from a ratio-based decision at the SDK to a
rate-based one at the boundary. A boundary limiter has no §9.2 membership knowledge, so the
floor C1 exists to deliver could be shed one hop later. This module does **not** assert that
(the limiter is out of repo); it registers it, because it is the shape of question that decides
between C1 and candidate A and no artifact currently asks it.

**Grounding, not behaviour.** Every assertion reads substrate declared at HEAD. These are
anti-rot pins on the facts a council decision will rest on — if any of them moves, the C11
analysis above is stale and must be re-derived before the decision is made.
"""

from __future__ import annotations

import pathlib
import re

from harness_core.deployment_surface import DeploymentSurface
from harness_core.persona_tier import PersonaTier
from harness_od.base_rate_set_and_envelope import PER_CELL_BASE_RATE_ENVELOPE
from harness_od.observability_matrix import CellID
from harness_od.per_cell_cardinality_budget import PER_CELL_CARDINALITY_BUDGET

_REPO = pathlib.Path(__file__).resolve().parents[2]
_OD_SPEC_11 = _REPO / "design-substrate" / "Spec_Operational_Discipline_v1_2.md"
_PERSONA = _REPO / "design-substrate" / "Persona_Document_v1.md"

#: The cell B-137 prices step (3) against.
_TEAM_SELF = CellID(
    persona_tier=PersonaTier.TEAM_BINDING,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)


def test_section_11_1_commits_no_number_at_the_team_binding_cells() -> None:
    """**(1)** The budget B-137 would be priced against is DEFERRED, not stated.

    §11.1's table gives solo cells a concrete posture and multi-tenant cells per-tenant
    isolation. The team-binding row defers to an open item. That asymmetry is the finding.
    """
    spec = _OD_SPEC_11.read_text()
    assert "## §11 C-OD-11" in spec, (
        "C-OD-11's section heading moved in the v1.2 baseline — re-ground the delta chain "
        "before trusting this module (CLAUDE.md §2 delta-baseline §-cite convention)"
    )
    team_row = (
        "| team-binding × * | Per-cell cardinality budget bounded per Persona §11.4 "
        "throughput rough order-of-magnitude open item; envelope refines downstream of "
        "§11.4 closure |"
    )
    assert team_row in spec, (
        "§11.1's team-binding row is no longer the verbatim deferral this module quotes. If it "
        "now states a number, C11's objection became priceable and B-137 step (3) must be "
        "re-argued against the new figure"
    )
    # The contrast is load-bearing: the solo row DOES commit a posture, so the team row's
    # silence is a deliberate deferral rather than the table simply being non-numeric.
    assert "default 1.0; rotation handles volume" in spec, (
        "§11.1's solo row no longer commits a concrete posture — without that contrast the "
        "team row's deferral cannot be read as deliberate"
    )


def test_the_deferral_target_is_an_open_item_closed_only_by_the_starved_telemetry() -> None:
    """**(2) The dependency cycle** — the load-bearing result of this module.

    `Persona §11.4` is §11 *Open items*, row 4 — NOT a subsection. Its closing path is
    "Emerges from operational telemetry once harness is running", and B-137 is the finding
    that this telemetry is starved at these very cells. The budget cannot close by the route
    its own contract nominates while the defect it would price is open.

    (Recorded because a first pass of this grounding searched for a `§11.4` HEADING, found
    nothing, and nearly concluded the reference was dangling. It is a table row.)
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
        "Persona §11 open-item 4 is not the verbatim row this module quotes. If it CLOSED, "
        "the C11 half of B-137's council becomes priceable and the dependency cycle below "
        "dissolves — re-derive before deciding step (3)"
    )
    # The cycle, pinned structurally: the closing path names telemetry, and B-137's own cell
    # is one whose telemetry is rate-suppressed by the very default this arc is about.
    assert PER_CELL_BASE_RATE_ENVELOPE[_TEAM_SELF].default_rate < 1.0, (
        "the team×self-hosted cell now admits at full rate, so its telemetry is no longer "
        "suppressed and the dependency cycle this test names does not apply"
    )


def test_the_flat_ten_thousand_is_implementation_chosen_not_declared_by_11_1() -> None:
    """**(3a)** The one number in code has no §11.1 provenance, and does not vary by cell.

    A budget genuinely "sized against" a per-cell base rate would differ across cells whose
    rates differ by 10x. This one does not, which is what makes it a placeholder rather than
    a sizing.
    """
    limits = {c: b.cell_rate_limit for c, b in PER_CELL_CARDINALITY_BUDGET.items()}
    assert len(set(limits.values())) == 1, (
        f"cell_rate_limit now varies across cells ({sorted(set(limits.values()))}) — it may "
        "have become a real per-cell sizing, which would give C11's objection an instrument "
        "it lacks today; re-ground before deciding step (3)"
    )
    assert set(limits.values()) == {10_000.0}, (
        f"the flat cell_rate_limit moved to {set(limits.values())} — B-137's C11 analysis "
        "quotes 10_000.0 and is now stale"
    )
    rates = {PER_CELL_BASE_RATE_ENVELOPE[c].default_rate for c in PER_CELL_CARDINALITY_BUDGET}
    assert len(rates) > 1, (
        "every ACTIVE cell now shares one base rate, so a uniform budget would no longer be "
        "evidence of a placeholder — this test's inference is void"
    )
    spec = _OD_SPEC_11.read_text()
    assert "10_000" not in spec and "10,000" not in spec, (
        "§11.1's baseline now states a five-figure rate limit — the code's 10_000.0 may have "
        "acquired the contract provenance this test asserts it lacks"
    )


def test_the_per_cell_half_of_the_budget_has_no_consumer_while_the_per_tenant_half_does() -> None:
    """**(3b)** `cell_rate_limit` is declared-and-never-read; `tenant_rate_limit` is enforced.

    The asymmetry is the point: this is not "the budget is unimplemented," it is "the half
    C11's objection names is unimplemented while its sibling is not." In-process, nothing can
    breach `cell_rate_limit` because nothing consults it.

    Scanned over `harness-*/src` only — the enforcement OD spec v1.37 describes lives at an
    out-of-process collector/backend this repo does not contain, and this test makes no claim
    about that layer (see the module docstring's boundary note).
    """
    src_files = [p for d in sorted(_REPO.glob("harness-*/src")) for p in d.rglob("*.py")]
    assert len(src_files) > 100, (
        f"only {len(src_files)} src files found — the scan root is wrong and a 'no consumer' "
        "result would be an artifact of not looking (never report unlooked as empty)"
    )
    decl = _REPO / "harness-od" / "src" / "harness_od" / "per_cell_cardinality_budget.py"

    cell_readers = sorted(
        str(p.relative_to(_REPO))
        for p in src_files
        if p != decl and re.search(r"\bcell_rate_limit\b", p.read_text())
    )
    tenant_readers = sorted(
        str(p.relative_to(_REPO))
        for p in src_files
        if p != decl and re.search(r"\btenant_rate_limit\b", p.read_text())
    )

    assert cell_readers == [], (
        f"`cell_rate_limit` acquired a consumer at {cell_readers} — the per-cell cap is now "
        "enforced in-process, which gives C11's objection a real instrument and makes the "
        "'nothing consults it' half of B-137's C11 grounding stale"
    )
    assert tenant_readers == [
        "harness-od/src/harness_od/multi_tenant_cross_cutting_enforcement.py"
    ], (
        f"the `tenant_rate_limit` consumer set changed to {tenant_readers}; the enforced-vs-"
        "unenforced asymmetry this module rests on must be re-grounded"
    )


def test_the_cell_this_is_all_priced_against_still_carries_its_rate() -> None:
    """Anti-rot pin on the one figure the C11 narrative quotes.

    B-137 states C1's cost as `1/base_rate` at the team cells. The `×10` reading is only
    correct while this cell carries 0.1, and the envelope is substrate that can move.
    """
    env = PER_CELL_BASE_RATE_ENVELOPE[_TEAM_SELF]
    assert env.default_rate == 0.1, (
        f"team×self-hosted default rate is now {env.default_rate}, so C1's in-envelope "
        f"multiplier reads ×{1 / env.default_rate:g}, not ×10 — re-price step (3)"
    )
    # The envelope already authorises the operator to raise this cell to max_rate. That is
    # context the council should have: a x5 increase over the default is ALREADY sanctioned
    # by the cleared §10.3 envelope, without any B-137 decision at all.
    assert env.max_rate == 0.5, (
        f"team×self-hosted max_rate moved to {env.max_rate}; the council's sense of how much "
        "volume increase the cleared envelope already permits at this cell is stale"
    )

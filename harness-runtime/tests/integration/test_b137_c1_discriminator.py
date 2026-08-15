"""B-137 step-(3) discriminator: candidate C1 measured on A′'s own falsifying test.

`B-137`'s step (3) is a posture fork over a live option set — A (mode-conditional
`ALWAYS_ON` head, unmeasured), A′ (bare-composite head, measured), C1 (admit the root),
B (reporting only) and C (ratify a root-only floor). Two of those have been measured at
the real venue; **the two measurements were not run against the same question**, so the
option set cannot yet be compared on one axis.

**The asymmetry this module closes.** A′ was demoted to a *partial, name-only remedy* by
exactly one test — `test_candidate_a_prime_is_a_name_only_remedy` in the sibling step-(2)
module — which showed it rescues the **name-backed** starved population and not the
**event-carried** one (the `B-133` family, which B-137 explicitly includes). **That test
was never run against C1.** If C1 shared the hole, the option set would collapse toward
candidate A and its ×1/base_rate-on-everything cost; if it does not, C1 dominates A′ on
coverage. This module runs A′'s own falsifying test against C1, at the same composition,
and then prices the volume difference between C1 and candidate A.

**Results, measured here and stated so the council does not have to re-derive them.**

1. **C1 rescues BOTH starved populations inside the envelope; A′ rescues one.** Under C1
   the root takes the always-sampled arm, so `ParentBased` hands every child — name-backed
   member and ordinary event-carrier alike — an inherited `RECORD_AND_SAMPLE`. The head
   never needs to classify the child, which is precisely why the event-carried population
   survives here and dies under A′: A′ exposes the child's *name* to the sampler, and an
   event-carrier's name is ordinary.

2. **C1's coverage is bounded to in-envelope traces, and that bound is exactly the starved
   population B-137 names.** A carrier that is its own trace root still takes the base-rate
   draw under C1 (`test_c1_does_not_rescue_a_carrier_that_is_its_own_root`). The row's own
   scope statement — after it withdrew the *"all 19 members are children of the envelope"*
   overclaim — is that the starvation is *"scoped to the members emitted inside the
   envelope."* C1's coverage and that scope are the same set.

3. **C1's volume cost is strictly less than candidate A's, not equal to it.** Candidate A
   admits every span in the process at `TAIL_BASED_PROD`; C1 admits only traces rooted at
   `workflow.envelope`, leaving every other root on its base-rate draw. Inside the envelope
   the two are identical, so C1 buys A's floor coverage over the starved set **without** A's
   out-of-envelope volume. This is the finding that moves the fork.

**Determinism — and why there is no trial count here.** Every assertion runs at
`base_rate=0.0`, where the ratio arm admits nothing and the always-sampled arm admits
everything, so each assertion is a *decision* rather than a sample — the discipline the
sibling module established. Result 3 is therefore asserted as a **shape** (an
out-of-envelope root is admitted under A and not under C1) rather than as a measured
admission percentage: the `1/base_rate` multiplier follows arithmetically from *which*
roots are unconditionally admitted, so sampling it would add a flake surface without
adding evidence. The cell's rate is grounded separately, so the `×10` figure the register
quotes cannot go stale silently.

**Mutation-probed.** Neutering the C1 patch (`_c1_member_set` yielding the unmodified set)
reds three tests: the positive control, the discriminator, and the A-equivalence. Two
tests survive that mutation by construction and are **bounds, not mechanism checks** —
`test_c1_does_not_rescue_a_carrier_that_is_its_own_root` and
`test_c1_leaves_out_of_envelope_roots_on_their_base_rate_draw_where_a_does_not` both assert
a *negative* about C1, which neutering C1 cannot falsify. They are recorded as scope
statements, and no conclusion here rests on them alone.

**Why the private `_ALWAYS_SAMPLED_LITERALS` is patched.** `is_always_sampled` resolves
against literal/prefix structures derived once at import (`sampling_mode.py:160-172`), so
patching the public `ALWAYS_SAMPLED_EVENT_CLASSES` frozenset alone is a silent no-op. There
is no runtime mutation path to the set in `src/`; this is test mechanics, and
`test_the_c1_patch_actually_reaches_the_sampler` is the positive control that fails loudly
if it stops reaching it.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

import harness_od.sampling_mode as _sm
from harness_core.deployment_surface import DeploymentSurface
from harness_core.persona_tier import PersonaTier
from harness_od.base_rate_set_and_envelope import PER_CELL_BASE_RATE_ENVELOPE
from harness_od.composite_sampler import HarnessCompositeSampler, build_default_sampler
from harness_od.observability_matrix import CellID
from harness_od.sampling_mode import is_always_sampled
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

_ENVELOPE = "workflow.envelope"
#: A §9.2 member with a real span-open site inside the envelope — the name-backed
#: starved population (population (ii) of the row, restricted to members).
_MEMBER = "hitl.gate.evaluated"
#: A §9.2 member that rides as a span EVENT on an ordinary carrier — the event-carried
#: starved population (population (i), the `B-133` family).
_SANDBOX = "sandbox.violation"
#: An ordinary span whose NAME carries no floor. Under A′ its name is what the head sees.
_CARRIER = "ordinary.carrier"

#: The real production cell the row prices step (3) against.
_PROD_CELL = CellID(
    persona_tier=PersonaTier.TEAM_BINDING,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)


@contextmanager
def _c1_member_set() -> Generator[None]:
    """Candidate C1: `workflow.envelope` joins the §9.2 always-sampled set."""
    original = _sm._ALWAYS_SAMPLED_LITERALS
    _sm._ALWAYS_SAMPLED_LITERALS = frozenset(original | {_ENVELOPE})
    try:
        yield
    finally:
        _sm._ALWAYS_SAMPLED_LITERALS = original


def _exported(sampler: object, *, envelope_wrapped: bool) -> list[str]:
    """Emit the two starved populations under `sampler`; return exported span names.

    `envelope_wrapped` places BOTH the name-backed member and the event-carrier inside a
    `workflow.envelope` root — the shape the driver really produces
    (`workflow_driver.py:3305` opens the envelope, members are emitted under it). When
    False the carrier is its own trace root, which is the out-of-envelope shape C1 is NOT
    claimed to cover.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=sampler)  # type: ignore[arg-type]
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("b137.c1.discriminator")

    if envelope_wrapped:
        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_MEMBER):  # name-backed §9.2 member
                pass
            with tracer.start_as_current_span(_CARRIER) as carrier:
                carrier.add_event(_SANDBOX)  # §9.2 member riding as an EVENT
    else:
        with tracer.start_as_current_span(_MEMBER):
            pass
        with tracer.start_as_current_span(_CARRIER) as carrier:
            carrier.add_event(_SANDBOX)

    return sorted(s.name for s in exporter.get_finished_spans())


# ---------------------------------------------------------------------------
# Grounding — the premise this module's comparison rests on
# ---------------------------------------------------------------------------


def test_the_c1_patch_actually_reaches_the_sampler() -> None:
    """Positive control for the private-structure patch (see module docstring).

    Without this, every C1 result below could be a silent no-op reported as a finding.
    """
    assert is_always_sampled(_ENVELOPE) is False, (
        f"`{_ENVELOPE}` is in the §9.2 set at HEAD — C1 is no longer a counterfactual and "
        "B-137's step (3) must be re-grounded before this module is trusted"
    )
    with _c1_member_set():
        assert is_always_sampled(_ENVELOPE) is True, (
            "the C1 patch did not reach `is_always_sampled` — the literal/prefix "
            "structures at `sampling_mode.py:160-172` are derived at import, so the patch "
            "target has moved and every result in this module is a false negative"
        )
    assert is_always_sampled(_ENVELOPE) is False, "the C1 patch leaked out of its context"


def test_the_carrier_name_carries_no_floor_but_its_event_does() -> None:
    """The asymmetry that makes the event-carried population a distinct one.

    A′ repairs by exposing the child's NAME to the sampler. That only helps a member whose
    floor is keyed on the name it is emitted under — which the event-carrier's is not.
    """
    assert is_always_sampled(_SANDBOX) is True, (
        f"`{_SANDBOX}` left the §9.2 set — re-ground B-137 before trusting this module"
    )
    assert is_always_sampled(_CARRIER) is False, (
        f"`{_CARRIER}` entered the §9.2 set — it is meant to be an ordinary carrier, and "
        "the event-carried population cannot be measured with a carrier that has a floor"
    )


# ---------------------------------------------------------------------------
# The discriminator — A′'s own falsifying test, run against C1
# ---------------------------------------------------------------------------


def test_c1_rescues_the_event_carried_population_that_a_prime_cannot() -> None:
    """**The load-bearing result of this module.**

    `test_candidate_a_prime_is_a_name_only_remedy` (sibling module) demoted A′ to a partial
    remedy by showing it drops the event-carrier. Run at the same composition, C1 keeps it.

    The mechanism is why, not a coincidence: under C1 the ROOT takes the always-sampled arm,
    so `ParentBased` never consults any child's name — it hands down an inherited
    `RECORD_AND_SAMPLE`. A repair that works by *inheritance* is indifferent to how a member
    is realized (name or event); a repair that works by *name exposure* is not.
    """
    with _c1_member_set():
        exported = _exported(build_default_sampler(base_rate=0.0), envelope_wrapped=True)

    assert exported == sorted([_ENVELOPE, _MEMBER, _CARRIER]), (
        f"expected C1 to admit the whole in-envelope trace; got {exported}. If the "
        f"event-carrier `{_CARRIER}` is missing, C1 shares A′'s name-only hole and "
        "B-137 step (3)'s option set collapses toward candidate A — re-price before deciding"
    )


def test_a_prime_drops_the_same_event_carrier_at_the_same_composition() -> None:
    """The head-to-head control for the test above — same spans, same rate, A′ instead.

    Stated here rather than cross-referenced so the comparison is one file's result: the
    two candidates are measured on identical inputs, and the only variable is the head.
    """
    exported = _exported(HarnessCompositeSampler(base_rate=0.0), envelope_wrapped=True)

    assert exported == [_MEMBER], (
        f"expected A′ to rescue ONLY the name-backed member; got {exported}. If the "
        "event-carrier now survives A′, the sibling module's name-only finding has been "
        "overtaken and this module's whole comparison must be re-run"
    )


def test_c1_does_not_rescue_a_carrier_that_is_its_own_root() -> None:
    """The honest bound on result 1 — C1's coverage is in-envelope, not universal.

    A span emitted OUTSIDE any envelope is its own trace root, so `ParentBased` consults the
    composite sampler on its own name and it takes the base-rate draw. C1 does not reach it.

    This is not a defect in C1: the row's own scope statement, after it withdrew the *"all
    19 members are children of the envelope"* overclaim, is that the starvation is *"scoped
    to the members emitted inside the envelope."* C1's coverage and that scope coincide. The
    bound is recorded so step (3) is not chosen against a coverage claim C1 does not make.
    """
    with _c1_member_set():
        exported = _exported(build_default_sampler(base_rate=0.0), envelope_wrapped=False)

    assert exported == [_MEMBER], (
        f"expected C1 to rescue only the name-backed ROOT member out of the envelope; got "
        f"{exported}. If the out-of-envelope carrier survives, C1's coverage is wider than "
        "this module claims and its volume figure below is understated"
    )


# ---------------------------------------------------------------------------
# The volume differential — C1 vs candidate A, at a real production cell
# ---------------------------------------------------------------------------


def test_c1_and_candidate_a_deliver_the_same_floor_inside_the_envelope() -> None:
    """Coverage equivalence: over the starved set, C1 buys exactly what A buys.

    Candidate A is `ALWAYS_ON` at the head. If A and C1 export the same in-envelope spans,
    then A's extra cost buys nothing *over the population B-137 names* — which is what makes
    the volume differential below decisive rather than merely interesting.
    """
    with _c1_member_set():
        under_c1 = _exported(build_default_sampler(base_rate=0.0), envelope_wrapped=True)
    under_a = _exported(ALWAYS_ON, envelope_wrapped=True)

    assert under_c1 == under_a, (
        f"C1 exported {under_c1} but candidate A exported {under_a} for the same "
        "in-envelope trace. If A covers something C1 does not, A's extra volume is buying "
        "real coverage and step (3) cannot prefer C1 on cost alone"
    )


def test_c1_leaves_out_of_envelope_roots_on_their_base_rate_draw_where_a_does_not() -> None:
    """**Result 3 — the volume differential, asserted as a shape, not a measurement.**

    At `base_rate=0.0` an out-of-envelope ordinary root is a *decision*: candidate A admits
    it (`ALWAYS_ON` consults nothing), C1 does not (it is a root with no floor, so it takes
    the ratio arm). That single decision is the whole volume difference between the two
    candidates — C1's `1/base_rate` multiplier applies to envelope-rooted traces only, while
    A's applies to every span the process emits.
    """
    with _c1_member_set():
        c1_carrier_admitted = _CARRIER in _exported(
            build_default_sampler(base_rate=0.0), envelope_wrapped=False
        )
    a_carrier_admitted = _CARRIER in _exported(ALWAYS_ON, envelope_wrapped=False)

    assert a_carrier_admitted is True, (
        "candidate A did not admit an out-of-envelope ordinary root — A is defined as an "
        "unconditionally-admitting head, so this module has mis-modelled it"
    )
    assert c1_carrier_admitted is False, (
        "C1 admitted an out-of-envelope ordinary root, so its volume multiplier is NOT "
        "scoped to envelope-rooted traces and the cost advantage over candidate A that "
        "step (3) would rely on does not exist"
    )


def test_the_production_cell_this_is_priced_against_still_carries_its_rate() -> None:
    """Ground the magnitude claim's input rather than hard-coding `×10` in prose.

    The register states C1's cost as `1/base_rate` at the team cells. That figure is only
    meaningful while the cell really carries the rate it is quoted at, and the envelope is
    substrate that can move under this row.
    """
    rate = PER_CELL_BASE_RATE_ENVELOPE[_PROD_CELL].default_rate
    assert rate == 0.1, (
        f"`{_PROD_CELL}` now has base rate {rate}, not 0.1 — B-137's quoted ×10 in-envelope "
        f"multiplier is stale and reads ×{1 / rate:g}; re-price step (3) before deciding"
    )

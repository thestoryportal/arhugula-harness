"""B-137 step-(3) discriminator: candidate C1 measured on A′'s own falsifying test.

**AS-BUILT SINCE OD SPEC v1.42 — the polarity of this module is INVERTED, deliberately.**
When it was written, C1 was a *counterfactual*: `workflow.envelope` was absent from §9.2 and
a context manager patched it in. The operator ratified C1 at step (3) on 2026-08-16 and OD
spec v1.42 §0.2 landed `workflow.envelope` as §9.2 row 20, so the shipped set now carries it
and the patch has nothing to add. The measurements below are unchanged in substance — every
one still runs at the same composition and asserts the same outcome — but they now measure
**HEAD** rather than a hypothesis, and the counterfactual arm has flipped to `_without_c1`,
which REMOVES the envelope to reproduce the pre-v1.42 world. That inversion is what keeps
the module non-circular: an as-built assertion that never exercises the negative arm cannot
distinguish "C1 works" from "this test asserts nothing"
(`[[only-the-classifier-can-witness-the-classifier]]`).

`B-137`'s step (3) was a posture fork over a live option set — A (mode-conditional
`ALWAYS_ON` head with the §10.3 ratio moved into the tail consumer, unmeasured), A′
(bare-composite head, measured), C1 (admit the root), B (reporting only) and C (ratify a
root-only floor). Two of those had been measured at the real venue, but **never against the
same question**, so the option set could not be compared on one axis.

**The asymmetry this module closes.** A′ was demoted to a *partial, name-only remedy* by
exactly one test — `test_candidate_a_prime_is_a_name_only_remedy` in the sibling step-(2)
module — which showed it rescues the **name-backed** starved population and not the
**event-carried** one (the `B-133` family, which B-137 explicitly includes). **That test
was never run against C1.** This module runs it against C1 at the same composition, and
then prices what separates C1 from candidate A.

**Two measurement disciplines this module had to learn the hard way (out-of-family Codex
round 1, absorbed 2026-08-15).** A first draft got the right answer for the wrong reasons
and overstated one of its three results. Both corrections are structural, so they are
encoded as tests rather than prose:

1. **Head admission is not export.** The first draft composed only a `SimpleSpanProcessor`,
   which measures whether the head *admitted* a span — not whether the pipeline *exported*
   it. Every claim about what survives now runs through the real `TailKeepSpanProcessor`
   (`_exported`), and the head-only helper (`_head_admitted`) is kept for the claims that
   are genuinely about admission, named so it cannot be confused for the other.

2. **The event name chosen decides the answer.** The first draft carried the §9.2 member
   `sandbox.violation` as its event-carried case. That name is **also** a §10.2
   classification trigger (`SANDBOX_VIOLATION_SPAN_NAME`), so it rescues its own whole trace
   at the tail and makes every candidate look equivalent. The representative `B-133`
   event-carried names — `fallback.triggered` / `fallback.exhausted` — are §9.2 members and
   **not** §10.2 triggers. This module measures with `fallback.exhausted` and keeps the
   trigger case as an explicit contrast, because the contrast *is* the finding.

**Results, measured here and stated so the council does not have to re-derive them.**

1. **C1 rescues BOTH starved populations inside the envelope; A′ rescues one.** Verified
   end-to-end through the real tail with the representative event: C1 exports the
   event-carrier, A′ does not. Under C1 the root takes the always-sampled arm, so
   `ParentBased` hands every child an inherited `RECORD_AND_SAMPLE` and never consults a
   child's name — which is exactly why the event-carried population survives here and dies
   under A′, whose repair works by exposing the child's *name*, and an event-carrier's name
   is ordinary.

2. **C1's coverage is bounded to in-envelope traces, and that bound is exactly the starved
   population B-137 names.** A carrier that is its own trace root still takes the base-rate
   draw under C1. The row's own scope statement — after it withdrew the *"all 19 members are
   children of the envelope"* overclaim — is that the starvation is *"scoped to the members
   emitted inside the envelope."* C1's coverage and that scope coincide.

3. **C1 and candidate A are NOT export-equivalent inside the envelope — the first draft's
   claim that they were is WITHDRAWN.** With the representative event and the real tail, C1
   exports `workflow.envelope` and A's head half does not: under C1 the envelope is a §9.2
   member and takes the bypass arm, while under an unconditionally-admitting head it is an
   ordinary span buffered at the tail and dropped at root close, no §10.2 trigger being
   present. **And candidate A cannot be fully measured at all**, because its defining half —
   the §10.3 ratio moved *into* the tail consumer — does not exist in code; anything called
   "A" here is A's **head half against today's tail**, and is labelled so. What survives of
   the first draft's result 3 is only its **cost** half, which is a head-admission fact and
   is asserted as one: C1's `1/base_rate` multiplier is scoped to envelope-rooted traces,
   while an unconditional head admits every root the process opens.

**What this does NOT settle.** The ×10 in-envelope multiplier at the production cells is
real and **unpriced against the C-OD-11 §11.1 per-cell budgets** — that is C11's half of the
declared C7 ⊥ C11 tension, and no probe here touches it. The dyadic **C7 + C11** convening
remains owed, with an agenda **narrowed but not reduced to one question**: A′ is out as a
complete repair and C1's coverage is settled, but **A vs C1 is NOT resolved** — A's defining
tail half is unbuilt and therefore unmeasurable here — so A, C1, B and C all remain live.

**Determinism — and why there is no trial count here.** Every assertion runs at
`base_rate=0.0`, where the ratio arm admits nothing and the always-sampled arm admits
everything, so each assertion is a *decision* rather than a sample — the discipline the
sibling module established. The cost claim is asserted as a **shape** (an out-of-envelope
root is admitted under an unconditional head and not under C1) rather than as a sampled
admission percentage: the `1/base_rate` multiplier follows arithmetically from *which* roots
are unconditionally admitted, so sampling it would add a flake surface without adding
evidence. The cell's rate is grounded separately so the `×10` figure cannot go stale.

**Why the private `_ALWAYS_SAMPLED_LITERALS` is patched.** `is_always_sampled` resolves
against literal/prefix structures derived once at import (`sampling_mode.py:160-172`), so
patching the public `ALWAYS_SAMPLED_EVENT_CLASSES` frozenset alone is a silent no-op. There
is no runtime mutation path to the set in `src/`; this is test mechanics, and
`test_c1_is_as_built_and_the_counterfactual_arm_still_bites` is the positive control that
fails loudly if the patch target moves — now guarding the `_without_c1` direction.

**Mutation-probed on both load-bearing mechanisms.** *(1)* Reverting the v1.42 membership
(dropping `workflow.envelope` from `ALWAYS_SAMPLED_EVENT_CLASSES`) reds the positive
control, the discriminator, the non-equivalence result and the contrast witness. *(2)*
Reverting
`_B133_EVENT` to the flattering `sandbox.violation` reds three — the trigger-status
grounding, the non-equivalence result (A's head half suddenly exports the envelope), and the
contrast witness (the two event names stop disagreeing). Probe (2) is the one that matters
most: it makes the measurement error out-of-family Codex caught in this module's first draft
a permanent regression guard rather than a lesson in prose.
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
from harness_od.tail_keep_classification import SECTION_10_2_EVENT_TRIGGER_NAMES
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

_ENVELOPE = "workflow.envelope"
#: A §9.2 member with a real span-open site inside the envelope — the name-backed
#: starved population.
_MEMBER = "hitl.gate.evaluated"
#: An ordinary span whose NAME carries no floor. Under A′ its name is what the head sees.
_CARRIER = "ordinary.carrier"

#: The REPRESENTATIVE event-carried §9.2 member — a `B-133`-family name that is NOT a §10.2
#: classification trigger. This is the case the comparison must be run on; see the module
#: docstring's discipline 2.
_B133_EVENT = "fallback.exhausted"
#: The CONTRAST case — a §9.2 member that is ALSO a §10.2 trigger, so it rescues its own
#: trace at the tail regardless of the head. Measuring with this name is what made the first
#: draft's candidates look equivalent.
_TRIGGER_EVENT = "sandbox.violation"

#: The real production cell the row prices step (3) against.
_PROD_CELL = CellID(
    persona_tier=PersonaTier.TEAM_BINDING,
    deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
)


@contextmanager
def _without_c1() -> Generator[None]:
    """The PRE-v1.42 counterfactual: `workflow.envelope` leaves the §9.2 set.

    The inverse of this module's original patch. C1 is as-built, so the hypothesis that
    needs constructing is now the *old* world — and constructing it is what proves the
    as-built assertions are discriminating rather than vacuous.
    """
    original = _sm._ALWAYS_SAMPLED_LITERALS
    _sm._ALWAYS_SAMPLED_LITERALS = frozenset(original - {_ENVELOPE})
    try:
        yield
    finally:
        _sm._ALWAYS_SAMPLED_LITERALS = original


def _emit(provider: TracerProvider, *, envelope_wrapped: bool, event: str) -> None:
    """Emit the two starved populations under `provider`.

    `envelope_wrapped` places BOTH the name-backed member and the event-carrier inside a
    `workflow.envelope` root — the shape the driver really produces
    (`workflow_driver.py:3458` opens the envelope, members are emitted under it). When
    False the carrier is its own trace root, which is the out-of-envelope shape C1 is NOT
    claimed to cover.

    **Cite drift, grounded 2026-08-15.** B-137's register row cites this site as
    `workflow_driver.py:3305`; at HEAD `:3305` is skill-emitter code and the envelope really
    opens at `:3458` (`start_as_current_span("workflow.envelope")`, under the C-OD-25 §25.1
    comment block). The mechanism the row describes is unchanged — only the line moved.
    """
    tracer = provider.get_tracer("b137.c1.discriminator")
    if envelope_wrapped:
        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_MEMBER):
                pass
            with tracer.start_as_current_span(_CARRIER) as carrier:
                carrier.add_event(event)
    else:
        with tracer.start_as_current_span(_MEMBER):
            pass
        with tracer.start_as_current_span(_CARRIER) as carrier:
            carrier.add_event(event)


def _exported(
    sampler: object, *, envelope_wrapped: bool = True, event: str = _B133_EVENT
) -> list[str]:
    """END-TO-END EXPORT through the REAL `TailKeepSpanProcessor`.

    This is the helper every survival claim uses. A head-admitted span still has to survive
    the tail's buffer-and-forward-or-drop decision at root close, and for an ordinary
    carrier in a trace with no §10.2 trigger it does not.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=sampler)  # type: ignore[arg-type]
    provider.add_span_processor(TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter)))
    _emit(provider, envelope_wrapped=envelope_wrapped, event=event)
    provider.force_flush()
    return sorted(s.name for s in exporter.get_finished_spans())


def _head_admitted(
    sampler: object, *, envelope_wrapped: bool = True, event: str = _B133_EVENT
) -> list[str]:
    """HEAD ADMISSION only — no tail processor.

    Kept separate and named for it, because conflating this with `_exported` is exactly the
    error out-of-family Codex caught in this module's first draft. Use it only for claims
    that are genuinely about what the head admits.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=sampler)  # type: ignore[arg-type]
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    _emit(provider, envelope_wrapped=envelope_wrapped, event=event)
    return sorted(s.name for s in exporter.get_finished_spans())


# ---------------------------------------------------------------------------
# Grounding — the premises the comparison rests on
# ---------------------------------------------------------------------------


def test_c1_is_as_built_and_the_counterfactual_arm_still_bites() -> None:
    """Positive control, INVERTED for the as-built world (see module docstring).

    Two things, and the second is the one that carries weight. First, C1 really is shipped:
    `workflow.envelope` resolves as always-sampled through `is_always_sampled` at HEAD, not
    merely as a literal in the public frozenset. Second — and this is what keeps every
    as-built assertion below from being vacuous — the `_without_c1` arm still reaches the
    derived literal/prefix structures, so the pre-v1.42 comparison is a real counterfactual
    rather than a no-op that would let every test pass by construction.
    """
    assert is_always_sampled(_ENVELOPE) is True, (
        f"`{_ENVELOPE}` is NOT in the §9.2 set at HEAD — OD spec v1.42 row 20 has been "
        "reverted or the derived literal structures no longer see it; B-137's ratified "
        "step (3) is not in force and every result in this module is measuring the old world"
    )
    with _without_c1():
        assert is_always_sampled(_ENVELOPE) is False, (
            "the `_without_c1` patch did not reach `is_always_sampled` — the literal/prefix "
            "structures at `sampling_mode.py:160-172` are derived at import, so the patch "
            "target has moved and the counterfactual arm is a silent no-op"
        )
    assert is_always_sampled(_ENVELOPE) is True, "the counterfactual leaked out of its context"


def test_the_representative_event_is_a_member_but_not_a_ten_two_trigger() -> None:
    """**The distinction out-of-family Codex round 1 surfaced, pinned as a test.**

    The whole comparison turns on measuring with an event that does NOT rescue its own
    trace. `fallback.exhausted` is a §9.2 member and not a §10.2 trigger; `sandbox.violation`
    is both. Choosing the latter makes every candidate look equivalent at the tail — which is
    precisely how this module's first draft reached a conclusion it had to withdraw.
    """
    assert is_always_sampled(_B133_EVENT) is True, (
        f"`{_B133_EVENT}` left the §9.2 set — it is no longer an event-carried member and "
        "cannot represent the `B-133` population"
    )
    assert _B133_EVENT not in SECTION_10_2_EVENT_TRIGGER_NAMES, (
        f"`{_B133_EVENT}` became a §10.2 trigger — it would now rescue its own trace at the "
        "tail, and every candidate comparison in this module would be flattered by it"
    )
    assert _TRIGGER_EVENT in SECTION_10_2_EVENT_TRIGGER_NAMES, (
        f"`{_TRIGGER_EVENT}` left the §10.2 trigger set — the contrast case below no longer "
        "demonstrates why the event choice decides the answer"
    )
    assert is_always_sampled(_CARRIER) is False, (
        f"`{_CARRIER}` entered the §9.2 set — the event-carried population cannot be "
        "measured with a carrier that has a floor of its own"
    )


# ---------------------------------------------------------------------------
# Result 1 — the discriminator, end-to-end through the real tail
# ---------------------------------------------------------------------------


def test_c1_rescues_the_event_carried_population_that_a_prime_cannot() -> None:
    """**The load-bearing result of this module**, measured through the real tail.

    `test_candidate_a_prime_is_a_name_only_remedy` (sibling module) demoted A′ by showing it
    drops the event-carrier. Run at the same composition with the representative `B-133`
    event and the shipped `TailKeepSpanProcessor`, C1 keeps it.

    The mechanism is why, not a coincidence: under C1 the ROOT takes the always-sampled arm,
    so `ParentBased` never consults any child's name — it hands down an inherited
    `RECORD_AND_SAMPLE`. A repair that works by *inheritance* is indifferent to how a member
    is realized (name or event); a repair that works by *name exposure* is not.
    """
    under_c1 = _exported(build_default_sampler(base_rate=0.0))
    # A′ is an ALTERNATIVE to C1, not something co-resident with it: its whole mechanism is
    # exposing a child's NAME to the composite sampler, so with C1 also in force the envelope
    # would be rescued by its own §9.2 membership and A′ would be flattered by the very row
    # it is being compared against. Measure it in the world it was proposed for.
    with _without_c1():
        under_a_prime = _exported(HarnessCompositeSampler(base_rate=0.0))
        pre_v1_42 = _exported(build_default_sampler(base_rate=0.0))

    assert pre_v1_42 == [], (
        f"the pre-v1.42 world exported {pre_v1_42}, expected nothing: at base_rate=0.0 an "
        "ordinary envelope root took the ratio arm and its children inherited the drop. If "
        "this is non-empty the counterfactual is not reproducing the starvation B-137 "
        "measured, and the as-built result below is not attributable to C1"
    )
    assert under_c1 == sorted([_ENVELOPE, _MEMBER, _CARRIER]), (
        f"expected C1 to export the whole in-envelope trace; got {under_c1}. If the "
        f"event-carrier `{_CARRIER}` is missing, C1 shares A′'s name-only hole and B-137 "
        "step (3)'s option set collapses toward candidate A — re-price before deciding"
    )
    assert under_a_prime == [_MEMBER], (
        f"expected A′ to rescue ONLY the name-backed member; got {under_a_prime}. If the "
        "event-carrier now survives A′, the sibling module's name-only finding has been "
        "overtaken and this module's whole comparison must be re-run"
    )


# ---------------------------------------------------------------------------
# Result 2 — the honest coverage bound
# ---------------------------------------------------------------------------


def test_c1_does_not_rescue_a_carrier_that_is_its_own_root() -> None:
    """The honest bound on result 1 — C1's coverage is in-envelope, not universal.

    A span emitted OUTSIDE any envelope is its own trace root, so `ParentBased` consults the
    composite sampler on its own name and it takes the base-rate draw. C1 does not reach it.

    This is not a defect in C1: the row's own scope statement, after it withdrew the *"all 19
    members are children of the envelope"* overclaim, is that the starvation is *"scoped to
    the members emitted inside the envelope."* C1's coverage and that scope coincide. The
    bound is recorded so step (3) is not chosen against a coverage claim C1 does not make.
    """
    exported = _exported(build_default_sampler(base_rate=0.0), envelope_wrapped=False)

    assert exported == [_MEMBER], (
        f"expected C1 to rescue only the name-backed ROOT member out of the envelope; got "
        f"{exported}. If the out-of-envelope carrier survives, C1's coverage is wider than "
        "this module claims and its cost statement below is understated"
    )


# ---------------------------------------------------------------------------
# Result 3 — C1 vs candidate A: NOT equivalent, and A is not fully modellable
# ---------------------------------------------------------------------------


def test_c1_and_an_unconditional_head_are_not_export_equivalent() -> None:
    """**The first draft's equivalence claim, WITHDRAWN and replaced by the measurement.**

    The draft asserted C1 and candidate A export the identical in-envelope span set, and
    concluded A's extra volume "buys nothing." Measured properly — real tail, representative
    event — they differ: C1 exports `workflow.envelope`, an unconditional head does not.

    Under C1 the envelope is a §9.2 member and takes the tail's bypass arm. Under an
    unconditionally-admitting head it is an ordinary span, buffered at the tail and dropped
    at root close because the trace carries no §10.2 trigger.

    **Scope — what is being compared.** Candidate A is `ALWAYS_ON` at the head *with the
    §10.3 ratio moved into the tail consumer*. That tail half does not exist in code, so A
    cannot be measured; `ALWAYS_ON` here is **A's head half against today's tail**, and no
    conclusion about A's full cost or behaviour is drawn from it.
    """
    under_c1 = _exported(build_default_sampler(base_rate=0.0))
    # Candidate A is an ALTERNATIVE to C1 (see the A′ note in the discriminator above): with
    # C1 also in force the envelope takes its own §9.2 bypass arm under A's head too, and the
    # two candidates would appear equivalent for a reason that has nothing to do with A.
    with _without_c1():
        under_a_head = _exported(ALWAYS_ON)

    assert under_c1 == sorted([_ENVELOPE, _MEMBER, _CARRIER]), (
        f"C1 exported {under_c1}, not the whole trace — re-ground result 1 first"
    )
    assert under_a_head == sorted([_MEMBER, _CARRIER]), (
        f"A's head half exported {under_a_head}; expected the envelope to be dropped at "
        "root close. If it now survives, the two candidates ARE export-equivalent here and "
        "this module's result 3 must be re-stated in the register"
    )
    assert under_c1 != under_a_head, (
        "C1 and an unconditional head are export-equivalent inside the envelope — the "
        "withdrawn first-draft claim would be correct after all, and the register bullet "
        "recording its withdrawal must be corrected"
    )


def test_the_trigger_event_hides_the_difference_that_the_representative_event_shows() -> None:
    """**Codex round 1's finding, encoded as a regression witness.**

    Swap the representative event for `sandbox.violation` — a §10.2 trigger — and C1 and the
    unconditional head become export-equivalent, because the trigger rescues the whole trace
    at the tail regardless of what the head did. That equivalence is an artifact of the name,
    not a property of the candidates, and it is what the first draft measured.

    Pinned so no future revision silently reintroduces the flattering choice.
    """
    c1_trigger = _exported(build_default_sampler(base_rate=0.0), event=_TRIGGER_EVENT)
    with _without_c1():
        a_head_trigger = _exported(ALWAYS_ON, event=_TRIGGER_EVENT)

    assert c1_trigger == a_head_trigger == sorted([_ENVELOPE, _MEMBER, _CARRIER]), (
        f"with the §10.2 trigger event the candidates diverged (C1={c1_trigger}, "
        f"A-head={a_head_trigger}); the contrast this test exists to demonstrate no longer "
        "holds, so the module's discipline-2 rationale needs re-grounding"
    )

    c1_repr = _exported(build_default_sampler(base_rate=0.0))
    with _without_c1():
        a_head_repr = _exported(ALWAYS_ON)
    assert c1_repr != a_head_repr, (
        "the representative event no longer separates the candidates — if both event names "
        "now agree, the event choice is no longer decisive and result 3 must be re-derived"
    )


def test_c1_leaves_out_of_envelope_roots_on_their_base_rate_draw() -> None:
    """**The cost half of result 3 — a HEAD-ADMISSION claim, asserted as one.**

    At `base_rate=0.0` an out-of-envelope ordinary root is a *decision*: an unconditional
    head admits it, C1 does not (it is a root with no floor, so it takes the ratio arm). That
    single decision is the whole volume difference — C1's `1/base_rate` multiplier applies to
    envelope-rooted traces only, while an unconditional head admits every root the process
    opens.

    This uses `_head_admitted` deliberately: it is a claim about what the head lets in, which
    is where the volume cost is actually incurred.
    """
    c1_admits_carrier = _CARRIER in _head_admitted(
        build_default_sampler(base_rate=0.0), envelope_wrapped=False
    )
    unconditional_admits_carrier = _CARRIER in _head_admitted(ALWAYS_ON, envelope_wrapped=False)

    assert unconditional_admits_carrier is True, (
        "an unconditional head did not admit an out-of-envelope ordinary root — this module "
        "has mis-modelled candidate A's head half"
    )
    assert c1_admits_carrier is False, (
        "C1 admitted an out-of-envelope ordinary root, so its volume multiplier is NOT "
        "scoped to envelope-rooted traces and the cost advantage step (3) would rely on "
        "does not exist"
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

"""U-OD-59 — the `B-133` event-aware §9.2 floor arm at `TailKeepSpanProcessor.on_end`.

Authority: `Spec_Operational_Discipline_v1_38.md` §C-OD-09 §9.2.1 (the
event-aware tail arm + the declared HEAD bound) +
`Implementation_Plan_Operational_Discipline_v2_33.md` U-OD-59.

**What `B-133` found, empirically.** Both §9.2 consumers classified span
NAMES; three §9.2 members (`fallback.triggered` / `breaker.tripped` /
`fallback.exhausted`) are span EVENTS on a carrier span
(`harness.runtime.retry_breaker_fallback`) that is in NEITHER §9.2 nor
§10.2. The `B-133` positive control drove a REAL exhausted dispatch through
the REAL `HarnessCompositeSampler` + the REAL `TailKeepSpanProcessor` and
exported ZERO spans for all three members.

**Axis homing — this module is `harness_runtime`-FREE, by rule.** OD is the
consumer-most-downstream axis, so the `axis-isolation — harness-od` CI leg syncs
ONLY `harness-od` + its declared deps and runs this directory's tests there; a
`harness_runtime` import fails collection outright. The five witnesses that
drive a REAL `RetryBreakerFallbackDispatcher` (W1–W5) therefore live at
`harness-runtime/tests/test_b133_event_aware_tail_floor_real_dispatch.py` — genuinely
runtime-homed, since runtime is what consumes the tail processor in production.
**This module pins the processor's OWN contract with no runtime present**, using
spans built directly through a `TracerProvider`. W13/W14 stay here deliberately:
they compose only `build_default_sampler` + `TailKeepSpanProcessor` + the §10.3
envelope, all OD surfaces, so nothing about the production-cell bound needs
runtime to state it.

**Witness roster (this module).**

| ID | Witness |
|---|---|
| W6  | Trigger-flag mirror — an event-matching span that is ALSO a §10.2 trigger sets the per-trace keep flag, preserving buffered siblings |
| W7  | `breaker.tripped` carried as an EVENT DOES set the keep flag — `B-123` CLOSED, sibling preserved |
| W8  | Conservative-absent — a `files.operation` event with no `kind` forwards; with a non-mutation `kind` it does not |
| W9  | Non-matching spans still buffer; drop counters untouched |
| W10 | Root-close carrier materializes the trace decision (no buffer leak) and frees its `max_buffered_traces` slot |
| W11 | SSOT completeness — every literal member of `ALWAYS_SAMPLED_EVENT_CLASSES` forwards its carrier when carried as an EVENT |
| W12 | Name-arm precedence — an always-sampled NAME with zero events still forwards (the scan is never on that path) |
| W13 | HEAD starves the TAIL at the two sub-1.0 production `TAIL_BASED_PROD` cells — the declared bound, and every admitted carrier still exports |
| W14 | Shape asymmetry — a root-NAME-shaped §9.2 member is admitted at 100% at the SAME cell and rate |
| W15 | Scan position — the member survives at ANY index, incl. the real `retry.skipped`-first dispatch ordering |

**Roster homed at `harness-runtime/tests/test_b133_event_aware_tail_floor_real_dispatch.py`**: W1 counterfactual;
W2–W4 the three members surviving the tail; W5 the `base_rate=0.0` head bound.

**PD-8 mutation probes.** Every figure below was RE-MEASURED against the FINAL
roster; the scope for all of them is this module + the runtime-homed module +
`test_tail_keep_span_processor.py` (the sibling contract suite) = **70 cases**
baseline, so the numbers are comparable to each other and checkable.

| # | Mutation | Measured | Red witnesses |
|---|---|---|---|
| i   | Delete the event-aware arm from `on_end` | — | equivalent to (ii) by construction |
| ii  | `_carries_always_sampled_event` returns `False` (name-check-only) | **34 / 36** | W2, W3, W4, W6, W7, W8(×2), W10, W11(×19), W13(×2), W15(×4), W16 |
| iii | Move the event arm ABOVE the name arm | **0 / 70** | none — see below |
| iv  | Drop the root-close `_materialize_trace_decision` | **5 / 65** | W2, W4, W6, W7, W10 |
| v   | Drop `event.attributes` from the lookup | **1 / 69** | W8 (non-mutation case) |
| vi  | Head sampler made unconditionally admitting (a `B-137` candidate-A sketch) | **4 / 66** | W5, W13(×2), W14 — exactly the bound witnesses |
| vii | First-event-only scan (`is_always_sampled(events[0]…)`) | **5 / 65** | W15(×4), W16 |

**Probe (iii) is green, and the honest reading is narrower than "ordering is a
cost property".** No witness distinguishes the two orderings; the only
observable divergence (re-gate-measured) is on a name-always-sampled ROOT that
also carries an always-sampled event — e.g. a `sandbox.violation` root with a
`fallback.exhausted` event: name-first leaves its buffered sibling behind
(`buffered_trace_count == 1`, the `B-136` leak), event-first would materialize
it — so the divergence narrows `B-136`'s territory rather than this arm's.
(The non-root succeeded `subagent.span` case was measured NON-divergent: the
event arm forwards it under either ordering.) The ordering is therefore left
as name-first for cost, not asserted.

**Probe (vii) is the merge-gate finding, and it is why W15/W16 exist.** Lens-3
measured that a first-event-only scan passed the ENTIRE pre-existing suite (65
cases) while reinstating `B-133` on a PRODUCTION-REACHABLE ordering: when a
candidate's breaker is already open, `retry_breaker_fallback` emits the
non-member `retry.skipped` on the OUTER span and then `fallback.exhausted` on
that same span. Every prior witness happened to put a member FIRST.
"""

from __future__ import annotations

from typing import Any

import pytest
from harness_core import DeploymentSurface, PersonaTier
from harness_od.base_rate_set_and_envelope import PER_CELL_BASE_RATE_ENVELOPE
from harness_od.composite_sampler import build_default_sampler
from harness_od.observability_matrix import CellID
from harness_od.sampling_mode import (
    ALWAYS_SAMPLED_EVENT_CLASSES,
    FILES_OPERATION_KIND_ATTR,
    PER_DEPLOYMENT_SURFACE_SAMPLING,
    SamplingMode,
    is_always_sampled,
)
from harness_od.tail_keep_classification import (
    VALIDATOR_FAIL_PERMANENCE_ATTR,
    VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE,
)
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

CARRIER_SPAN_NAME = "harness.runtime.retry_breaker_fallback"

#: The three §9.2 members that ride as span EVENTS rather than as spans.
EVENT_SHAPED_MEMBERS = ("fallback.triggered", "breaker.tripped", "fallback.exhausted")


# ---------------------------------------------------------------------------
# W6 / W7 — the trigger-flag mirror, INCLUDING the `B-123` event-name arm
# (CLOSED — `is_classification_trigger` now scans `span.events`, so an
# event-carried `breaker.tripped` sets the keep flag too).
# ---------------------------------------------------------------------------


def test_w6_event_matching_span_that_is_also_a_trigger_sets_the_keep_flag() -> None:
    """Mirror of the name arm at `:259-269` — an event-carrying span that is ALSO
    a §10.2 classification trigger preserves its buffered tree-siblings.

    The assertion is on export ORDER, not membership, and that is deliberate:
    membership alone is satisfied WITHOUT the arm (the span's own attribute
    trigger sets the keep flag on the buffered path, so both spans forward at
    root close anyway) — PD-8 probe (ii) showed this witness passing under the
    name-check-only mutation before it was sharpened. Order is the discriminator
    the arm actually owns: the arm forwards the carrier IMMEDIATELY (root first,
    eviction-safe, bypassing the buffer); the buffered path materializes in
    insertion order, so the sibling would come first.
    """
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w6")

    with tracer.start_as_current_span(
        "ordinary.root",
        attributes={VALIDATOR_FAIL_PERMANENCE_ATTR: VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE},
    ) as root:
        with tracer.start_as_current_span("sibling.work"):
            pass
        root.add_event("fallback.exhausted")

    names = [s.name for s in exporter.get_finished_spans()]
    # The trigger-carrying root forwarded IMMEDIATELY via the event arm (first),
    # and its buffered sibling preserved by the keep flag (second). Without the
    # arm the order inverts — that inversion is what makes this load-bearing.
    assert names == ["ordinary.root", "sibling.work"]
    assert tail.buffered_trace_count == 0


def test_w7_event_carried_breaker_tripped_now_sets_the_keep_flag() -> None:
    """`B-123` boundary — CLOSED (was: "NOT widened at this leg").

    Rewritten in place per the arc brief: this test was deliberately written
    by the `B-133` leg to PIN the pre-`B-123` boundary so widening it later
    would be test-visible rather than silent — and it now proves the
    widening happened. `is_classification_trigger` (`tail_keep_classification.py`)
    now scans `span.events` for the two §10.2 event-shaped trigger names
    AFTER its name/attribute checks, so an event-carried `breaker.tripped`
    both forwards its OWN carrier (the pre-existing §9.2 floor) AND flags the
    trace, preserving the buffered sibling at root close — the §10.2 sibling
    preservation this row's `close_out` step (2) settled as a conformance
    repair to already-cleared contract text
    (`design-substrate/Spec_Operational_Discipline_v1_2.md` §10.2, lines
    582-584, which reads "Parent + sibling spans of any `breaker.tripped`
    EVENT preserved" — the contract already said event).

    **The bound this delivers, stated so it is not overclaimed (AC9).** This
    test runs at the module's plain `TracerProvider()` — an unconditional
    sampler, i.e. the head-ADMITTED case. Per `B-137`, production tail cells
    only admit event carriers to this processor at their §10.3 base rate
    (~10-20% measured), so the repair delivers the sibling tree only for
    carriers the head sampler let through, not a full floor.
    """
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w7")

    with tracer.start_as_current_span("ordinary.root") as root:
        with tracer.start_as_current_span("sibling.work"):
            pass
        root.add_event("breaker.tripped")

    # The trigger-carrying root forwarded IMMEDIATELY via the event arm
    # (first), and its buffered sibling preserved by the now-set keep flag
    # (second) — the same order W6 pins for the attribute-triggered case.
    names = [s.name for s in exporter.get_finished_spans()]
    assert names == ["ordinary.root", "sibling.work"]
    assert tail.buffered_trace_count == 0


# ---------------------------------------------------------------------------
# W8 — conservative-absent preserved through the event arm.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("event_attributes", "expected_forwarded"),
    [
        (None, True),  # conservative-absent: missing `kind` always-samples
        ({FILES_OPERATION_KIND_ATTR: "upload"}, True),  # mutation kind
        ({FILES_OPERATION_KIND_ATTR: "list"}, False),  # non-mutation -> base-rate
    ],
)
def test_w8_conditional_rows_resolve_conservatively_through_the_event_arm(
    event_attributes: dict[str, str] | None,
    expected_forwarded: bool,
) -> None:
    """The §9.2 conditional-by-attribute rows keep their posture at the event arm.

    Event attributes are passed through to `is_always_sampled`, so a missing
    discriminator still always-samples (never under-sample the §9.3 floor) and a
    present non-mutation discriminator falls to the §10.1 base-rate regime.
    """
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w8")

    with tracer.start_as_current_span("ordinary.root") as root:
        root.add_event("files.operation", attributes=event_attributes)

    forwarded = [s.name for s in exporter.get_finished_spans()] == ["ordinary.root"]
    assert forwarded is expected_forwarded


# ---------------------------------------------------------------------------
# W9 / W10 — buffering + bookkeeping.
# ---------------------------------------------------------------------------


def test_w9_non_matching_spans_still_buffer_and_counters_are_untouched() -> None:
    """The arm changes nothing for a span carrying no §9.2 event."""
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter), max_spans_per_trace=1)
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w9")

    with tracer.start_as_current_span("ordinary.root"):
        with tracer.start_as_current_span("child.a") as child:
            child.add_event("retry.skipped")
        with tracer.start_as_current_span("child.b"):
            pass

    assert exporter.get_finished_spans() == ()  # no §10.2 trigger -> dropped
    assert tail.buffered_trace_count == 0
    assert tail.dropped_span_count == 1  # the `max_spans_per_trace` overflow
    assert tail.dropped_trace_count == 0


def test_w10_root_close_carrier_materializes_the_trace_and_leaks_no_buffer() -> None:
    """An event-carrying ROOT close resolves its trace instead of leaking it.

    The name arm returns unconditionally, so an always-sampled ROOT leaves its
    siblings pending until `force_flush` (pre-existing; registered as `B-136`).
    This arm must NOT extend that to the dispatch path, where the carrier span
    IS routinely the root close.
    """
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w10")

    with tracer.start_as_current_span("ordinary.root") as root:
        with tracer.start_as_current_span("sibling.work"):
            pass
        root.add_event("fallback.exhausted")

    assert tail.buffered_trace_count == 0  # the slot is freed, not leaked
    assert [s.name for s in exporter.get_finished_spans()] == ["ordinary.root"]


# ---------------------------------------------------------------------------
# W11 / W12 — SSOT completeness + name-arm precedence.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("member", sorted(ALWAYS_SAMPLED_EVENT_CLASSES))
def test_w11_every_always_sampled_member_forwards_its_carrier_as_an_event(
    member: str,
) -> None:
    """SSOT — the arm resolves the WHOLE §9.2 roster, not a hand-listed three.

    Parametrized over `ALWAYS_SAMPLED_EVENT_CLASSES` itself, so a future roster
    row is covered the moment it lands (the parametrize-literal drift gap
    U-OD-58 closed at the name arm, closed here too). Wildcard rows are
    exercised at a concrete descendant name, exactly as the SDK boundary sees
    them.
    """
    concrete = member.replace(".*", ".concrete") if member.endswith(".*") else member
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w11")

    with tracer.start_as_current_span("ordinary.root") as root:
        root.add_event(concrete)

    assert [s.name for s in exporter.get_finished_spans()] == ["ordinary.root"]
    # The three event-shaped members are the ones `B-133` names; assert the
    # roster still contains all three so a removal is test-visible.
    assert set(EVENT_SHAPED_MEMBERS) <= ALWAYS_SAMPLED_EVENT_CLASSES


def _tail_admission_counts(
    *, base_rate: float, span_name: str, event_name: str | None, n: int
) -> tuple[int, int]:
    """Return (spans reaching the tail processor, spans exported downstream).

    The REAL production composition: `build_default_sampler(base_rate)` as the
    provider sampler + the REAL `TailKeepSpanProcessor`, subclassed only to
    count arrivals at its own `on_end` input.
    """
    exporter = InMemorySpanExporter()
    arrivals: list[str] = []

    class _CountingTail(TailKeepSpanProcessor):
        def on_end(self, span: Any) -> None:
            arrivals.append(span.name)
            super().on_end(span)

    tail = _CountingTail(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider(sampler=build_default_sampler(base_rate=base_rate))
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("admission")
    for _ in range(n):
        with tracer.start_as_current_span(span_name) as span:
            if event_name is not None:
                span.add_event(event_name)
    return len(arrivals), len(exporter.get_finished_spans())


@pytest.mark.parametrize(
    ("cell_persona", "cell_surface"),
    [
        (PersonaTier.TEAM_BINDING, DeploymentSurface.SELF_HOSTED_SERVER),
        (PersonaTier.MULTI_TENANT_COMPLIANCE, DeploymentSurface.MANAGED_CLOUD),
    ],
)
def test_w13_head_starves_the_tail_at_sub_one_tail_cells_declared_bound(
    cell_persona: PersonaTier,
    cell_surface: DeploymentSurface,
) -> None:
    """OD spec v1.38 §9.2.1 term 4 — the bound BITES AT PRODUCTION TAIL CELLS.

    Surfaced by out-of-family Codex round 1 against this arc's first commit,
    whose premise this witness CONFIRMS rather than declines. Production binds
    the §10.3 per-cell base rate at the HEAD in BOTH §9.1 modes
    (`tracer_provider.py`: "the current default sampler ignores the mode"), so a
    `TAIL_BASED_PROD` cell at base-rate 0.1 never gives this processor most of
    its event carriers to classify.

    **This witness asserts the BOUND, exactly as W5 does for the dev cell — it
    is not a repair and must not be read as one.** What it also asserts is that
    the arm is complete for what it CAN see: every carrier that reaches the tail
    is exported. The residual is admission, not classification. `B-137` owns the
    architecture-level question.
    """
    cell = CellID(persona_tier=cell_persona, deployment_surface=cell_surface)
    base_rate = PER_CELL_BASE_RATE_ENVELOPE[cell].default_rate
    # Grounded, not assumed: this really is a TAIL_BASED_PROD cell at a sub-1.0
    # head rate — if the envelope or the mode map moves, this witness goes red
    # rather than silently asserting nothing.
    assert PER_DEPLOYMENT_SURFACE_SAMPLING[cell_surface] is SamplingMode.TAIL_BASED_PROD
    assert base_rate < 1.0

    n = 2000
    reached, exported = _tail_admission_counts(
        base_rate=base_rate,
        span_name=CARRIER_SPAN_NAME,
        event_name="fallback.exhausted",
        n=n,
    )
    # THE BOUND: most carriers never reach the tail at all.
    assert reached < n, "head admitted everything — the §10.3 rate is not binding at the head"
    # Sanity that the rate is roughly the envelope's (wide band — this is a
    # ratio sampler over random trace ids, not a determinism claim).
    assert 0.5 * base_rate * n < reached < 1.5 * base_rate * n
    # THE ARM IS COMPLETE FOR WHAT IT SEES: every admitted carrier is exported.
    assert exported == reached


def test_w14_name_shaped_members_are_delivered_at_the_same_sub_one_cell() -> None:
    """The SHAPE asymmetry — the load-bearing half of term 4, and the reason
    `B-133` is about emission shape rather than about sampling rates.

    At the SAME cell and the SAME base rate at which event-shaped carriers are
    ~90% starved (W13), a §9.2 member realized as a ROOT SPAN NAME is admitted
    at 100% — the head sampler resolves `is_always_sampled` against the span
    name and returns RECORD_AND_SAMPLE. Without this pairing, W13 would read as
    "sampling drops things", which is not a finding; with it, W13 reads as "the
    floor's realization depends on the member's emission shape", which is.
    """
    cell = CellID(
        persona_tier=PersonaTier.TEAM_BINDING,
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
    )
    base_rate = PER_CELL_BASE_RATE_ENVELOPE[cell].default_rate
    assert base_rate < 1.0

    n = 1000
    name_reached, name_exported = _tail_admission_counts(
        base_rate=base_rate, span_name="sandbox.violation", event_name=None, n=n
    )
    event_reached, _ = _tail_admission_counts(
        base_rate=base_rate, span_name=CARRIER_SPAN_NAME, event_name="fallback.exhausted", n=n
    )

    # Name-shaped: fully delivered at head AND at tail.
    assert name_reached == n
    assert name_exported == n
    # Event-shaped: starved at head. The asymmetry is the finding.
    assert event_reached < name_reached


def test_w12_always_sampled_name_forwards_without_any_event_scan() -> None:
    """Name-arm precedence — an always-sampled NAME never depends on events.

    The event scan sits AFTER the name check, so the name arm's spans (which
    carry no events at all) forward on the name alone. Ordering is a COST
    property here, not a correctness one; this pins the cheap path.
    """
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w12")

    with tracer.start_as_current_span("sandbox.violation") as span:
        assert not span.events

    assert [s.name for s in exporter.get_finished_spans()] == ["sandbox.violation"]


# ---------------------------------------------------------------------------
# W15 — scan position: the member need not be the carrier's FIRST event.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("event_names", "member_index"),
    [
        (("retry.skipped", "fallback.exhausted"), 1),
        (("retry.skipped", "retry.skipped", "fallback.exhausted", "exception"), 2),
        (
            (
                "tool_retry.exhausted",
                "gen_ai.eval.alignment_floor.drift_detected",
                "breaker.tripped",
            ),
            2,
        ),
        (("exception", "fallback.triggered"), 1),
    ],
)
def test_w15_member_survives_at_any_scan_position(
    event_names: tuple[str, ...],
    member_index: int,
) -> None:
    """The arm must scan the WHOLE event list, not just the first entry.

    **Why this witness exists — it was measured, not imagined.** The merge gate's
    lens-3 reduced `_carries_always_sampled_event` to
    `is_always_sampled(events[0].name, events[0].attributes)` and the mutation
    passed the ENTIRE suite (65 cases) while reinstating `B-133`. Every other
    witness happens to put a §9.2 member FIRST, so nothing constrained the scan
    position. The ordering below is the real dispatcher's, not a contrived one:
    `retry_breaker_fallback` emits the non-member `retry.skipped` on the OUTER
    span when a candidate's breaker is already open, then `fallback.exhausted` on
    that SAME span at exhaustion. `harness-runtime`'s W16 drives that shape
    end-to-end; this one pins the processor's own contract over the ordering,
    with no runtime present, and generalizes it across the non-member vocabulary.
    """
    # Precondition — the leading events really are non-members, so the case
    # cannot pass by accident if the roster ever absorbs one of them.
    for name in event_names[:member_index]:
        assert not is_always_sampled(name), f"{name!r} is a §9.2 member — case is vacuous"
    assert is_always_sampled(event_names[member_index])

    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider()
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("w15")

    with tracer.start_as_current_span(CARRIER_SPAN_NAME) as span:
        for name in event_names:
            span.add_event(name)

    assert [s.name for s in exporter.get_finished_spans()] == [CARRIER_SPAN_NAME]
    assert tail.buffered_trace_count == 0

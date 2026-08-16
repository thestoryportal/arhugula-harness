"""B-137 step-(2) witness, executed at the REAL `api.run` venue.

`B-137`'s close-out prescribes: *"(1) RE-GROUND THE WIRING FIRST … (2) RE-MEASURE, do not
re-reason … (3) DECIDE THE POSTURE, and this is a genuine architectural fork rather than a
bug with a fix."* This module is step (2)'s result.

**The finding, at the venue.** Running the B-72 fan-out workflow end-to-end through
`api.run` with a real `TracerProvider` and the production sampler at a starving base rate,
**nothing is exported at all** — including `hitl.gate.evaluated`, which **is** a §9.2
always-sampled member whose floor is declared `head=1.0`. The reason is structural, not a
per-span bug: `workflow_driver.py:3305` opens **`workflow.envelope`** as the trace root,
`workflow.envelope` is **not** a §9.2 member, and `ParentBased(root=HarnessCompositeSampler)`
consults the composite sampler **only for roots**. The root loses its base-rate draw and
every child inherits the drop, its own name never consulted. **The §9.2 floor is
root-only**, so a member emitted inside the envelope does not receive it.

**Two prior overclaims by this arc, corrected here (out-of-family Codex, round 1).**

1. An earlier draft asserted *"all 19 §9.2 members, at their real emission sites, are
   children of the envelope."* **False.** Only **11 of the 19** have a span-open site in
   `src/` at all (the other 8 are event-carried names or unimplemented — population (i) of
   the row), and at least one span-backed member is a **root**: `skill.activation` is
   emitted from `workflow_driver.py:3206`, which precedes the envelope's open at `:3305`.
   The starvation is therefore **scoped to the members emitted inside the envelope**, not
   universal. `test_the_scope_is_inside_the_envelope_not_all_nineteen` pins both facts.
   **Qualified (round 14):** that root status holds for a **top-level** run only — under a
   nested, recursive `execute_workflow` the dispatcher invokes the child runner inside an
   active `subagent.span`, so the same pre-envelope emit is a child and is starved too.

2. An earlier draft called `emit_pause_captured_span` a *"real production emitter."* At
   the time it was a real function with **no caller anywhere in `src/`** — so
   `pause.captured` and `resume.attempted` were never emitted in production, and that draft
   drove a manufactured composition rather than a shipped path. That is why this module
   measures `hitl.gate.evaluated` through `api.run`. The uncalled-emitter fact was
   registered as **B-162** and has since been **CLOSED** by wiring the driver; the
   assertion is now inverted at `test_the_pause_span_emitters_are_now_wired_b162_closed`.

**And a third correction, from round 2 — the two uncalled spans are NOT symmetric.** A
first draft of B-162 gated both on B-137. Wrong for one of them: the driver runs
entry-point resume detection **before** the envelope opens (`workflow_driver.py:3213-3225`,
and it says so in-line), so a `resume.attempted` span at its prescribed call site would be
a **root** and **would** receive its §9.2 floor once added to the set, while
`pause.captured` would be an envelope child and would not.
`test_the_two_uncalled_spans_land_on_opposite_sides_of_the_envelope` pins the split.

**Determinism.** `base_rate=0.0` makes the ratio arm admit nothing and the always-sampled
arm admit everything, so each assertion is a decision rather than a sample. The mechanism
is rate-independent — `ParentBased` consults the inner sampler only for roots at any rate.

**Why the private `_ALWAYS_SAMPLED_LITERALS` is patched.** `is_always_sampled` resolves
against literal/prefix structures derived once at import (`sampling_mode.py:160-172`);
patching the public `ALWAYS_SAMPLED_EVENT_CLASSES` frozenset alone is a silent no-op, and a
first draft of this arc drew a false negative from exactly that. There is no runtime
mutation path to the set in `src/`, so the precompute is sound in production — this is test
mechanics only, and a positive control fails loudly if the patch stops reaching the sampler.
"""

from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager, nullcontext
from typing import Any

import harness_od.sampling_mode as _sm
import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.persona_tier import PersonaTier
from harness_od.base_rate_set_and_envelope import PER_CELL_BASE_RATE_ENVELOPE
from harness_od.composite_sampler import HarnessCompositeSampler, build_default_sampler
from harness_od.observability_matrix import CellID
from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_span_processor import (
    TailKeepSpanProcessor,
    is_classification_trigger,
)
from harness_runtime.lifecycle.tracer_provider import materialize_tracer_provider_stage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_ENVELOPE = "workflow.envelope"
#: A §9.2 member the B-72 fan-out workflow really emits, inside the envelope.
_MEMBER = "hitl.gate.evaluated"
#: A §9.2 member that is ALSO a §10.2 classification trigger — used for the
#: root-name-matched and event-carried populations.
_SANDBOX = "sandbox.violation"
_REPO = pathlib.Path(__file__).resolve().parents[3]

#: The §9.2 members that have a `start_as_current_span` site in `src/` — 11 of the 19.
#: The register cites this exact count to scope and price B-137's step (3), so the
#: identity set is pinned rather than its cardinality alone (out-of-family Codex round 2:
#: a "some but not all" check would let an emission site appear or vanish silently and
#: leave the authoritative result stale).
_SPAN_BACKED_MEMBERS = frozenset(
    {
        "files.operation",
        "hitl.gate.evaluated",
        "hitl.invocation.opened",
        "hitl.invocation.responded",
        "hitl.invocation.timed_out",
        "managed_agents.runtime",
        "mcp.tool.call",
        "memory.operation",
        "sandbox.violation",
        "skill.activation",
        "subagent.span",
        # §9.2 row 20, span-backed by construction — the envelope's own open at
        # `workflow_driver.py` is the site the whole row is about (OD spec v1.42, `B-137` C1).
        "workflow.envelope",
    }
)


def _b72() -> Any:
    """Load the B-72 fan-out harness by path (robust to package layout)."""
    path = pathlib.Path(__file__).with_name(
        "test_b72_fanout_sub_agent_dispatch_hitl_gate_resume.py"
    )
    name = "_b137_b72_harness"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def _member_set(
    *, add: frozenset[str] = frozenset(), remove: frozenset[str] = frozenset()
) -> Generator[None]:
    original = _sm._ALWAYS_SAMPLED_LITERALS
    _sm._ALWAYS_SAMPLED_LITERALS = frozenset(original | add) - remove
    try:
        yield
    finally:
        _sm._ALWAYS_SAMPLED_LITERALS = original


@contextmanager
def _pre_c1() -> Generator[None]:
    """Reconstruct the PRE-v1.42 world, in which `workflow.envelope` carried no floor.

    **Why this module needs it.** Everything below measures the STARVATION — the condition
    `B-137` was opened to establish. OD spec v1.42 §0.2 landed candidate C1
    (`workflow.envelope` as §9.2 row 20, operator-ratified 2026-08-16), which *removed* that
    condition, so at HEAD these measurements would silently measure the repaired world and
    report it as the finding. Rather than delete the evidence, each starvation measurement
    now runs explicitly in the pre-C1 world and the module becomes a two-sided record: the
    starvation was real (here), and C1 is what closed it
    (`test_admitting_the_root_delivers_the_floor_candidate_c1`, which runs at HEAD).

    Do NOT "simplify" this away by dropping the context manager — an unwrapped assertion
    here passes against the fix rather than against the defect, which is the same
    silent-inversion hazard `[[only-the-classifier-can-witness-the-classifier]]` names.
    """
    with _member_set(remove=frozenset({_ENVELOPE})):
        yield


def _production_provider(config: Any, *, base_rate: float) -> TracerProvider:
    """Compose the provider through the SHIPPED stage-4 composer.

    Out-of-family Codex round 4: constructing `TracerProvider(...)` directly bypasses
    `materialize_tracer_provider_stage`, so the result could not honestly be called a
    real-production composition. This routes through the real composer — resource
    attributes, mode resolution, provider construction — and uses only the `sampler`
    override the composer itself documents as being *"for tests that need a deterministic
    sampler"*. `test_the_sampler_override_is_faithful_to_the_shipped_binding` pins that the
    override matches what the composer resolves on its own.
    """
    stage = materialize_tracer_provider_stage(
        config,
        register_globally=False,  # the runtime forbids a second global registration
        sampler=build_default_sampler(base_rate=base_rate),
    )
    return stage.provider


async def _run_the_real_workflow(*, base_rate: float) -> list[str]:
    """Drive the shipped `api.run` path; return the span names that were EXPORTED."""
    harness = _b72()
    exporter = InMemorySpanExporter()
    with tempfile.TemporaryDirectory() as cfg_tmp:
        provider = _production_provider(harness._config(pathlib.Path(cfg_tmp)), base_rate=base_rate)
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    with pytest.MonkeyPatch.context() as mp:
        # The harness stubs OD stage 4 with a NoOp tracer; substitute the real provider so
        # the shipped emission sites are actually recorded.
        mp.setattr(
            harness._FakeTracerProvider,
            "get_tracer",
            lambda self, name, /: provider.get_tracer(name),
        )
        harness._install_fake_providers(mp, harness._SucceedingAnthropicClient())
        harness._install_fake_od_stage4(mp)
        harness._install_fake_webhook_composer_factory(mp, [])
        with tempfile.TemporaryDirectory() as tmp:
            result = await harness.api_run(
                harness._FanOutSubAgentDispatchWorkflow(),
                config=harness._config(pathlib.Path(tmp)),
            )
    assert result.status == "paused", f"the B-72 venue did not reach its gate: {result.status}"
    return sorted(s.name for s in exporter.get_finished_spans())


# ---------------------------------------------------------------------------
# Grounding
# ---------------------------------------------------------------------------


def test_the_member_carries_a_floor_and_the_root_does_not_pre_c1() -> None:
    """The asymmetry the whole finding rests on — stated for the PRE-C1 world.

    At HEAD the asymmetry is GONE, and that is the point: OD spec v1.42 gave the root a
    floor too. Both halves are asserted so the module records the transition rather than
    just one side of it.
    """
    assert is_always_sampled(_MEMBER) is True, (
        f"`{_MEMBER}` left the §9.2 set — re-ground B-137 before trusting this module"
    )
    with _pre_c1():
        assert is_always_sampled(_ENVELOPE) is False, (
            f"`{_ENVELOPE}` still carries a floor with the C1 membership patched OUT — the "
            "`_pre_c1` counterfactual is not reaching the derived literal structures, so "
            "every starvation measurement in this module is a silent no-op"
        )
    assert is_always_sampled(_ENVELOPE) is True, (
        f"`{_ENVELOPE}` is NOT in the §9.2 set at HEAD — OD spec v1.42 row 20 has been "
        "reverted, which would re-open the production half of B-137"
    )


def test_the_sampler_override_is_faithful_to_the_shipped_binding() -> None:
    """The bridge P1a's claim rests on — the override is not a different composition.

    Every measurement here routes through the real `materialize_tracer_provider_stage` but
    passes a deterministic `sampler`. That is only honest if the composer, left to itself,
    binds a sampler of the *same shape*. It does: `tracer_provider.py:228-236` resolves the
    per-cell rate from `PER_CELL_BASE_RATE_ENVELOPE` and calls the same
    `build_default_sampler`. Asserted by comparing the composer's own sampler description
    against a directly-built one at the cell's rate.

    Note the cell: the B-72 harness config is `solo-developer x local-development`, whose
    base rate is **1.0** — no starvation there. The starving cells are the production ones
    (0.1 at team-binding, 0.2 at multi-tenant), and `base_rate=0.0` stands in for them
    deterministically.
    """
    harness = _b72()
    with tempfile.TemporaryDirectory() as tmp:
        config = harness._config(pathlib.Path(tmp))

    composed = materialize_tracer_provider_stage(config, register_globally=False)
    cell = CellID(persona_tier=config.persona_tier, deployment_surface=config.deployment_surface)
    expected = build_default_sampler(base_rate=PER_CELL_BASE_RATE_ENVELOPE[cell].default_rate)

    assert composed.provider.sampler.get_description() == expected.get_description(), (
        "the shipped composer no longer binds `build_default_sampler` at the per-cell rate "
        "— the deterministic override used throughout this module would no longer be "
        "faithful to production, and B-137 must be re-measured"
    )

    overridden = _production_provider(config, base_rate=0.0)
    assert type(overridden.sampler) is type(composed.provider.sampler), (
        "the override produced a different sampler TYPE than the shipped binding"
    )


def test_a_production_cell_still_binds_the_unconditional_ratio_sampler() -> None:
    """**The tripwire for the fix B-137 is waiting on** (out-of-family Codex round 6).

    Every other measurement in this module supplies a deterministic `sampler` override, and
    the B-72 harness config is a `solo-developer x local-development` cell whose base rate
    is 1.0 with `sampling_mode=None`. A future mode-conditional sampler that repairs only
    `TAIL_BASED_PROD` — precisely B-137's candidate A — would therefore leave every one of
    those runs green, and this witness would not notice the row had been closed by other
    work.

    So compose a real PRODUCTION cell (`team-binding x self-hosted-server`, base rate 0.1)
    through the shipped stage with **no override at all**, and assert the composer still
    binds the plain per-cell `ParentBased(HarnessCompositeSampler)`. When a mode-conditional
    sampler lands, this reddens and forces the re-measurement step (2) requires.
    """
    harness = _b72()
    with tempfile.TemporaryDirectory() as tmp:
        base = harness._config(pathlib.Path(tmp))
    production = base.model_copy(
        update={
            "persona_tier": PersonaTier.TEAM_BINDING,
            "deployment_surface": DeploymentSurface.SELF_HOSTED_SERVER,
        }
    )

    cell = CellID(
        persona_tier=production.persona_tier,
        deployment_surface=production.deployment_surface,
    )
    assert PER_CELL_BASE_RATE_ENVELOPE[cell].default_rate == 0.1, (
        "the team-binding x self-hosted-server base rate moved — B-137's measured figures "
        "are quoted against 0.1 and must be re-derived"
    )

    composed = materialize_tracer_provider_stage(production, register_globally=False)
    assert composed.provider.sampler.get_description() == (
        build_default_sampler(base_rate=0.1).get_description()
    ), (
        "a production cell no longer binds the unconditional per-cell ratio sampler — a "
        "mode-conditional sampler may have landed, which would CLOSE B-137's head half; "
        "re-measure the row rather than trusting this module's other assertions"
    )


def test_all_three_populations_through_the_real_tail_processor() -> None:
    """**Step (2)'s probe, at the shape the row prescribes** (out-of-family Codex round 13).

    The row's step (2) names `build_default_sampler` **plus the real
    `TailKeepSpanProcessor`**, counting `on_end` arrivals across all three populations.
    `test_all_three_starved_populations_at_one_composition` covers head admission via
    `SimpleSpanProcessor`, and the `api.run` probe covers the tail for the non-root member
    only — so neither alone discharges step (2), and an earlier draft claimed completion
    while conceding the remaining tail arms were owed. That contradiction is removed here by
    running all three through the real processor.

    Result: the tail processor is **reached by nothing** for the two starved populations,
    because the head drops them before recording; only the root-name-matched span arrives.
    """
    arrivals: list[str] = []
    downstream = _Counting()

    class _SpyingTailKeep(TailKeepSpanProcessor):
        def on_end(self, span: Any) -> None:
            arrivals.append(span.name)
            super().on_end(span)

    with _pre_c1():
        provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
        provider.add_span_processor(
            _SpyingTailKeep(
                downstream=downstream, max_buffered_traces=4096, max_spans_per_trace=4096
            )
        )
        tracer = provider.get_tracer("b137.populations.tail")

        # (i) root-name-matched
        with tracer.start_as_current_span(_SANDBOX):
            pass
        # (ii) non-root member, and (ii-b) non-root TRIGGER
        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_MEMBER):
                pass
        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_SANDBOX):
                pass
        # (iii) event-carried
        with tracer.start_as_current_span("ordinary.carrier") as carrier:
            carrier.add_event(_SANDBOX)

    assert arrivals == [_SANDBOX], (
        f"`TailKeepSpanProcessor.on_end` arrivals were {arrivals}, expected only the "
        f"root-name-matched `{_SANDBOX}`. A starved population reaching the tail means the "
        "head now records-without-sampling and B-137's boundary has moved."
    )
    assert downstream.seen == [_SANDBOX], (
        f"downstream received {downstream.seen} — a consequence check on the same claim"
    )


def _finished_span(name: str) -> Any:
    """Record one span with an always-on provider and return the ReadableSpan."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    with provider.get_tracer("b137.probe").start_as_current_span(name):
        pass
    return exporter.get_finished_spans()[0]


def _trigger_probe() -> Any:
    return _finished_span(_SANDBOX)


def _member_probe() -> Any:
    return _finished_span(_MEMBER)


def test_all_three_starved_populations_at_one_composition() -> None:
    """**Step (2)'s three populations, executed** (out-of-family Codex round 6).

    The row's step (2) names three populations to re-measure: root-name-matched,
    event-carried, and non-root. The `api.run` venue above exercises only the non-root one
    (`hitl.gate.evaluated` under the envelope), so on its own it does not discharge step
    (2). This covers all three at one composition, deterministically at `base_rate=0.0` —
    which is the probe shape step (2) actually prescribes (*"four lines of composition"*);
    the `api.run` venue is this arc's addition on top, not a replacement.

    Measured equivalents at the production rate 0.1 (N=2000), recorded on the row:
    root-name-matched **100%**, non-root **9.3%**, event-carried **9.1%**, against a
    **10.8%** control.
    """
    exporter = InMemorySpanExporter()
    with _pre_c1():
        provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("b137.populations")

        # (i) root-name-matched — the ONE population that is not starved.
        with tracer.start_as_current_span(_SANDBOX):
            pass
        # (ii) non-root — a §9.2 member under an unlisted root. Two arms, because step (2)
        # names the "non-root TRIGGER" case specifically and `hitl.gate.evaluated` is NOT a
        # §10.2 classification trigger (out-of-family Codex round 8 — an earlier draft labelled
        # this arm as the trigger population when it was not one).
        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_MEMBER):  # member, NOT a trigger
                pass
        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_SANDBOX):  # member AND a §10.2 trigger
                pass
        # (iii) event-carried — a §9.2 name riding as an EVENT on an unlisted carrier span.
        with tracer.start_as_current_span("ordinary.carrier") as carrier:
            carrier.add_event(_SANDBOX)

    # The trigger arm's own premise, asserted rather than assumed.
    assert is_classification_trigger(_trigger_probe()), (
        f"`{_SANDBOX}` is no longer a §10.2 classification trigger — the non-root TRIGGER "
        "population below is not being exercised and step (2) is not discharged"
    )
    assert not is_classification_trigger(_member_probe()), (
        f"`{_MEMBER}` became a §10.2 trigger — the two non-root arms above are no longer "
        "distinct and this test must be re-derived"
    )

    exported = sorted(s.name for s in exporter.get_finished_spans())
    assert exported == [_SANDBOX], (
        f"expected ONLY the root-name-matched population to survive; got {exported}. "
        "If a starved population now survives, the head composition changed and B-137 must "
        "be re-measured; if the root-matched one stopped surviving, §9.2 itself changed."
    )


def test_control_the_membership_patch_reaches_the_sampler() -> None:
    """Positive control — without it every membership result here could pass wrongly.

    Re-based on the as-built world: C1 shipped, so the patch that has to be proven live is
    the REMOVING one (`_pre_c1`). Both directions are exercised, since the module now uses
    both — `_pre_c1` for every starvation measurement and the plain HEAD set for the C1
    arms.
    """
    assert is_always_sampled(_ENVELOPE) is True, (
        "`workflow.envelope` is not always-sampled at HEAD — OD spec v1.42 row 20 reverted"
    )
    with _pre_c1():
        assert is_always_sampled(_ENVELOPE) is False, (
            "removing from `_ALWAYS_SAMPLED_LITERALS` no longer reaches the sampler — every "
            "starvation measurement in this module is silently measuring the REPAIRED world"
        )
    assert is_always_sampled(_ENVELOPE) is True, "the patch did not restore"
    with _member_set(add=frozenset({"probe.only.name"})):
        assert is_always_sampled("probe.only.name") is True, (
            "adding to `_ALWAYS_SAMPLED_LITERALS` no longer reaches the sampler"
        )


# ---------------------------------------------------------------------------
# The venue
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_real_run_emits_the_member_as_a_child_of_the_envelope() -> None:
    """Establish the production SHAPE by execution, not by reading the driver.

    With an always-on provider the shipped `api.run` path records exactly the envelope and
    one §9.2 member nested under it. This is the composition the sampling result below is
    about; if it ever changes, every conclusion here must be re-measured.
    """
    harness = _b72()
    exporter = InMemorySpanExporter()
    provider = TracerProvider()  # ALWAYS_ON — capture the true shape
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            harness._FakeTracerProvider,
            "get_tracer",
            lambda self, name, /: provider.get_tracer(name),
        )
        harness._install_fake_providers(mp, harness._SucceedingAnthropicClient())
        harness._install_fake_od_stage4(mp)
        harness._install_fake_webhook_composer_factory(mp, [])
        with tempfile.TemporaryDirectory() as tmp:
            await harness.api_run(
                harness._FanOutSubAgentDispatchWorkflow(),
                config=harness._config(pathlib.Path(tmp)),
            )

    spans = {s.name: s for s in exporter.get_finished_spans()}
    assert _ENVELOPE in spans and _MEMBER in spans, (
        f"the real run did not emit both spans; got {sorted(spans)}"
    )
    assert spans[_ENVELOPE].parent is None, f"`{_ENVELOPE}` is no longer the trace root"
    member_parent = spans[_MEMBER].parent
    assert member_parent is not None, (
        f"`{_MEMBER}` became a ROOT — it would then receive the §9.2 floor directly and "
        "this half of B-137 would be closed for it"
    )
    assert member_parent.span_id == spans[_ENVELOPE].context.span_id, (
        f"`{_MEMBER}` is no longer nested under `{_ENVELOPE}`"
    )


@pytest.mark.asyncio
async def test_the_floor_does_not_survive_the_real_run_at_a_starving_base_rate() -> None:
    """**The finding.** A §9.2 member is dropped by the shipped path despite its floor.

    At `base_rate=0.0` the root loses unconditionally, and `hitl.gate.evaluated` — whose
    C-OD contract declares `head=1.0` — leaves the process not at all. Nothing about its
    own name is ever consulted.
    """
    with _pre_c1():
        exported = await _run_the_real_workflow(base_rate=0.0)
    assert exported == [], (
        f"spans survived a base_rate=0.0 run ({exported}) — the head composition changed "
        "and B-137 must be RE-MEASURED, which its close-out step (2) requires over "
        "re-arguing"
    )


@pytest.mark.asyncio
async def test_admitting_the_root_delivers_the_floor_candidate_c1() -> None:
    """**AS-BUILT since OD spec v1.42** — the repair, at the same venue as the finding.

    Formerly the counterfactual that priced step (3); C1 is now shipped, so this runs at
    HEAD with no patch and is the standing regression witness that the repair holds. Read
    against `test_the_floor_does_not_survive_the_real_run_at_a_starving_base_rate` directly
    above, which reconstructs the pre-C1 world: same run, same base rate, opposite outcome.
    That pairing is what shows the loss was the ROOT's decision and not an emission failure.

    **Scope — this arm uses `SimpleSpanProcessor`, so it prices the HEAD only.** What C1
    costs through the shipped tail chain is a separate question, measured by
    `test_candidate_c1_strands_ordinary_children_in_the_tail_buffer` below; an earlier
    draft of this arc called C1 "whole traces" on the strength of this test alone, which
    out-of-family Codex round 3 correctly rejected.
    """
    exported = await _run_the_real_workflow(base_rate=0.0)
    # `pause.captured` joined this set when B-162 wired the driver-side emission — the
    # B-72 venue really does pause, so the span is now live on this path.
    assert exported == sorted([_MEMBER, "pause.captured", _ENVELOPE]), (
        f"admitting the root did not deliver the floor to its children; got {exported}"
    )


# ---------------------------------------------------------------------------
# The tail half — the row's step (2) names `TailKeepSpanProcessor` explicitly
# ---------------------------------------------------------------------------


class _Counting:
    """Minimal downstream that records what the tail processor forwards."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        return None

    def on_end(self, span: Any) -> None:
        self.seen.append(span.name)

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True


def test_candidate_c1_resolves_every_trace_at_root_close() -> None:
    """**C1's tail behaviour, measured through the SHIPPED chain — post-B-136.**

    History, because the conclusion reversed. An earlier draft priced C1 as *"delivers the
    floor and keeps traces whole, one line"* from a `SimpleSpanProcessor` run; out-of-family
    Codex rejected that, and driving the real `TailKeepSpanProcessor` showed C1 **stranding**
    ordinary children — a trace held a buffer slot forever because the always-sampled root
    took the §9.2 name arm and returned before the root-close decision. That stranding was
    **`B-136`**, not C1: the name arm's unconditional return. With B-136 repaired, C1 leaves
    **nothing** buffered.

    What C1 costs now, exactly: every trace resolves at its own root close, so
    ordinary non-member children are **kept** when any §10.2 trigger fired in the trace and
    **dropped** when none did — which is what an ordinary trace already does. No stranding,
    no eviction, no never-resolving population. The remaining C1 cost is its `1/base_rate`
    admission multiplier, nothing more.
    """

    def trial(*, envelope_in_set: bool, with_trigger: bool) -> tuple[list[str], int]:
        downstream = _Counting()
        tail = TailKeepSpanProcessor(downstream=downstream)
        provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
        provider.add_span_processor(tail)
        tracer = provider.get_tracer("b137.c1")
        # AS-BUILT since v1.42: `envelope_in_set=True` is simply HEAD, and the arm that now
        # needs constructing is the pre-C1 one.
        with nullcontext() if envelope_in_set else _pre_c1():
            with tracer.start_as_current_span(_ENVELOPE):
                with tracer.start_as_current_span("validator.evaluate"):  # ORDINARY child
                    pass
                with tracer.start_as_current_span(_MEMBER):  # §9.2 member child
                    pass
                if with_trigger:
                    with tracer.start_as_current_span("sandbox.violation"):
                        pass
        return downstream.seen, sum(len(v) for v in tail._buffer.values())

    # Baseline: today the head drops everything, so nothing is forwarded OR buffered.
    forwarded, buffered = trial(envelope_in_set=False, with_trigger=False)
    assert forwarded == [] and buffered == 0, (
        f"the head no longer drops the whole trace (forwarded={forwarded}, "
        f"buffered={buffered}) — re-measure B-137"
    )

    # C1 POST-B-136: members forwarded and the buffer RESOLVES at root close.
    forwarded, buffered = trial(envelope_in_set=True, with_trigger=False)
    assert sorted(forwarded) == sorted([_MEMBER, _ENVELOPE]), (
        f"C1 no longer forwards the floor members; got {forwarded}"
    )
    assert buffered == 0, (
        f"C1 stranded {buffered} trace(s) again — B-136's root-close materialization has "
        "regressed, and step (3)'s C1 pricing reverts to data-loss-under-pressure"
    )

    # ...and a §10.2 trigger now RESCUES the ordinary child, because the always-sampled root
    # materializes the trace decision instead of returning early.
    forwarded, buffered = trial(envelope_in_set=True, with_trigger=True)
    assert "sandbox.violation" in forwarded, "the trigger itself should still forward"
    assert "validator.evaluate" in forwarded, (
        f"a §10.2 trigger did not preserve the ordinary child under C1; got {forwarded} — "
        "B-136's repair is what makes this work, so re-ground it before re-pricing C1"
    )
    assert buffered == 0, f"the trace did not resolve at root close; {buffered} buffered"


def test_candidate_c1_no_longer_evicts_under_production_bounds() -> None:
    """**C1 no longer evicts under production bounds — the cost was B-136's.**

    Production never builds an unbounded processor: `span_processor.py:373-374` always
    supplies `max_buffered_traces` / `max_spans_per_trace` from `CollectorConfig` (defaults
    **4096** each, `types.py:741,752`), and the buffer evicts **drop-oldest**.

    Before `B-136` this test read the opposite: C1 left every trace buffered, so under a
    small ceiling the population was shed — **97 of 100 evicted at a cap of 3**, which is
    why C1 was priced as *data loss, not delay*. B-136's root-close materialization removed
    the population entirely, so there is nothing left to evict. This asserts the zero, and
    its failure message says what a non-zero would mean: B-136 has regressed and C1's
    step-(3) pricing reverts.
    """
    downstream = _Counting()
    cap = 3
    tail = TailKeepSpanProcessor(
        downstream=downstream, max_buffered_traces=cap, max_spans_per_trace=4096
    )
    provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
    provider.add_span_processor(tail)
    tracer = provider.get_tracer("b137.c1.bounded")

    traces = 100
    with _member_set(add=frozenset({_ENVELOPE})):
        for _ in range(traces):
            with tracer.start_as_current_span(_ENVELOPE):
                with tracer.start_as_current_span("validator.evaluate"):
                    pass

    # POST-B-136 these are both ZERO: every trace resolves at its own root close, so no
    # population accumulates to be evicted. Before B-136 this read `cap` buffered and
    # `traces - cap` (97 of 100) evicted — the "data loss, not delay" cost C1 was priced
    # with. That cost belonged to B-136's early return, NOT to C1.
    assert tail.buffered_trace_count == 0, (
        f"{tail.buffered_trace_count} trace(s) buffered under C1 — B-136's root-close "
        "materialization has regressed and C1's eviction cost is back"
    )
    assert tail.dropped_trace_count == 0, (
        f"{tail.dropped_trace_count} trace(s) EVICTED under C1 — B-136 has regressed; C1's "
        "step-(3) pricing reverts to data loss under sustained load"
    )
    # The floor members still forwarded — the loss is confined to ordinary children.
    assert downstream.seen.count(_ENVELOPE) == traces, (
        "C1 stopped forwarding the always-sampled root; the whole counterfactual is stale"
    )
    assert "validator.evaluate" not in downstream.seen, (
        "an ordinary child reached the downstream — C1 would then not be losing them, and "
        "the eviction cost recorded on B-137 must be re-derived"
    )


@pytest.mark.asyncio
async def test_the_tail_processor_never_sees_what_the_head_dropped() -> None:
    """Executed rather than asserted — the row's step (2) names this processor.

    `TailKeepSpanProcessor` honours §9.2 too (always-sampled spans bypass its buffer), so
    one might expect it to rescue the floor. It cannot: a span the head drops is never
    recorded, so `on_end` never runs and no tail-side rule can act on it. This drives the
    REAL processor through the REAL run.

    **Observed at the right layer** (out-of-family Codex round 10). An earlier draft counted
    arrivals at the processor's DOWNSTREAM, which is the wrong observation layer for the
    claim: if the head ever moved from `DROP` to `RECORD_ONLY`, `TailKeepSpanProcessor.on_end`
    WOULD run but might buffer the span without forwarding it, leaving a downstream counter
    empty and this test green over exactly the boundary change it is meant to catch. It now
    spies on the tail processor's own `on_end`, which is what the register's claim is about.
    """
    harness = _b72()
    arrivals: list[str] = []
    forwarded: list[str] = []

    class _Counting:
        def on_start(self, span: Any, parent_context: Any = None) -> None:
            return None

        def on_end(self, span: Any) -> None:
            forwarded.append(span.name)

        def shutdown(self) -> None:
            return None

        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            return True

    class _SpyingTailKeep(TailKeepSpanProcessor):
        """The REAL processor, with its own `on_end` observed before delegating."""

        def on_end(self, span: Any) -> None:
            arrivals.append(span.name)
            super().on_end(span)

    with _pre_c1():
        provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
        provider.add_span_processor(_SpyingTailKeep(downstream=_Counting()))

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                harness._FakeTracerProvider,
                "get_tracer",
                lambda self, name, /: provider.get_tracer(name),
            )
            harness._install_fake_providers(mp, harness._SucceedingAnthropicClient())
            harness._install_fake_od_stage4(mp)
            harness._install_fake_webhook_composer_factory(mp, [])
            with tempfile.TemporaryDirectory() as tmp:
                await harness.api_run(
                    harness._FanOutSubAgentDispatchWorkflow(),
                    config=harness._config(pathlib.Path(tmp)),
                )

    assert arrivals == [], (
        f"`TailKeepSpanProcessor.on_end` was REACHED with {arrivals} from a head-dropped "
        "trace — if the head now records-without-sampling, B-137's starvation boundary has "
        "moved and the row must be re-measured"
    )
    # Downstream is necessarily empty too, but that is a consequence, not the claim.
    assert forwarded == [], f"spans reached the downstream processor: {forwarded}"

    # POSITIVE CONTROL — the spy must FIRE when the head admits, or "zero arrivals" above
    # is unfalsifiable and would stay green if the processor were never installed at all.
    arrivals.clear()
    forwarded.clear()
    admitting = TracerProvider(sampler=build_default_sampler(base_rate=1.0))
    admitting.add_span_processor(_SpyingTailKeep(downstream=_Counting()))
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            harness._FakeTracerProvider,
            "get_tracer",
            lambda self, name, /: admitting.get_tracer(name),
        )
        harness._install_fake_providers(mp, harness._SucceedingAnthropicClient())
        harness._install_fake_od_stage4(mp)
        harness._install_fake_webhook_composer_factory(mp, [])
        with tempfile.TemporaryDirectory() as tmp:
            await harness.api_run(
                harness._FanOutSubAgentDispatchWorkflow(),
                config=harness._config(pathlib.Path(tmp)),
            )
    assert _MEMBER in arrivals, (
        f"the tail-processor spy did not fire even at base_rate=1.0 (arrivals={arrivals}) — "
        "the zero-arrivals assertion above proves nothing"
    )


# ---------------------------------------------------------------------------
# Scope corrections — what this arc got wrong before out-of-family review
# ---------------------------------------------------------------------------


def _span_open_sites() -> tuple[dict[str, list[str]], list[str]]:
    """Inventory span-open call sites by AST, not by line regex.

    Out-of-family Codex round 5: a per-line regex counts occurrences inside comments and
    docstrings, misses multiline calls, and cannot see `start_span` or constant-named spans.
    Both errors were real here — `child_workflow_runner.py:16` was a docstring reference
    counted as a site, and `hitl.invocation.timed_out`'s `hitl_gate_composer.py:2101` call
    was missed for being multiline.

    Returns `(literal_sites, dynamic_sites)`. Module-level `Final[str]` constants are
    resolved, so a constant-named span is found; genuinely dynamic names (f-strings,
    parameters) cannot be resolved statically and are returned separately so the residual
    is stated rather than silently treated as absent.
    """
    literal: dict[str, list[str]] = {}
    dynamic: list[str] = []

    for path in _REPO.glob("harness-*/src/**/*.py"):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:  # pragma: no cover - a syntax error would fail the suite anyway
            continue
        rel = path.relative_to(_REPO)

        # Module-level string constants, so `start_as_current_span(SOME_SPAN_NAME)` resolves.
        constants: dict[str, str] = {}
        for node in tree.body:
            targets = (
                [node.target]
                if isinstance(node, ast.AnnAssign)
                else list(node.targets)
                if isinstance(node, ast.Assign)
                else []
            )
            value = getattr(node, "value", None)
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                for target in targets:
                    if isinstance(target, ast.Name):
                        constants[target.id] = value.value

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            name = (
                func.attr
                if isinstance(func, ast.Attribute)
                else func.id
                if isinstance(func, ast.Name)
                else None
            )
            if name not in {"start_as_current_span", "start_span"}:
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                literal.setdefault(arg.value, []).append(f"{rel}:{node.lineno}")
            elif isinstance(arg, ast.Name) and arg.id in constants:
                literal.setdefault(constants[arg.id], []).append(f"{rel}:{node.lineno}")
            else:
                dynamic.append(f"{rel}:{node.lineno}")

    return literal, dynamic


def test_the_scope_is_inside_the_envelope_not_all_nineteen() -> None:
    """**The correction.** The starvation is scoped, and an earlier draft overclaimed it.

    Two facts, both measured from `src/`: most §9.2 members have no span-open site at all
    (so they are not even candidates for root-vs-child starvation), and `skill.activation`
    — one that does — is emitted from a call site that PRECEDES the envelope's open, so it
    is a root and does receive its floor. Any repricing of step (3) must be against the
    members actually emitted inside the envelope.
    """
    sites, dynamic = _span_open_sites()
    members = set(_sm.ALWAYS_SAMPLED_EVENT_CLASSES)

    # State the residual rather than letting it read as 'absent': these span names are
    # built at runtime (f-strings / parameters) and cannot be inventoried statically, so
    # the 11-member result is '11 among statically-resolvable sites'.
    assert len(dynamic) == 4, (
        f"the dynamically-named span population changed ({len(dynamic)} sites: {dynamic}) "
        "— one of them may now emit a §9.2 member, which the static inventory below "
        "cannot see; re-derive B-137's scope by execution before trusting it"
    )
    # The four are an f-string (`router_resolution.py`, `f"chat {model}"`) and three
    # parameter/variable names (`memory_observability.py`, two in `llm_dispatch.py`). A
    # fifth site, `per_server_trust_evaluator.py:323`, is NOT in this residual: it names the
    # module constant `MCP_TRUST_EVALUATE_SPAN_NAME`, which the resolver above resolves to
    # `mcp.trust.evaluate` — B-160's conditional case, not a §9.2 member, so it does not
    # move the count of 11.

    span_backed = {
        m
        for m in members
        if (any(n.startswith(m[:-1]) for n in sites) if m.endswith("*") else m in sites)
    }
    # Pin the EXACT identity set, not merely "some but not all" (out-of-family Codex
    # round 2): the register cites this scope to price B-137's step (3) — 11-of-19 as the row
    # was written, 12-of-20 since OD spec v1.42 added the envelope itself — so an
    # emission site appearing or disappearing must redden this rather than pass silently.
    assert span_backed == _SPAN_BACKED_MEMBERS, (
        "the span-backed §9.2 population changed — B-137's scope and step-(3) pricing "
        "cite this exact set, so re-derive both before acting on the row. "
        f"added={sorted(span_backed - _SPAN_BACKED_MEMBERS)} "
        f"removed={sorted(_SPAN_BACKED_MEMBERS - span_backed)}"
    )
    assert len(span_backed) < len(members), (
        "every §9.2 member became span-backed — the withdrawn 'all 19 are children' "
        "overclaim would need re-deriving from scratch"
    )

    assert "skill.activation" in span_backed
    driver_path = _REPO / "harness-cp/src/harness_cp/workflow_driver.py"
    driver = driver_path.read_text().splitlines()
    envelope_line = next(
        i for i, line in enumerate(driver, 1) if f'start_as_current_span("{_ENVELOPE}")' in line
    )

    # Resolve the SKILL-ACTIVATION emitter exactly, by AST. A substring match on
    # `_emitter.emit(` selects `ctx.lifecycle_emitter.emit(` at :2647 first — that string
    # literally contains `_emitter.emit(` — so the assertion below would pass against a
    # different call and stay green if skill activation moved inside the envelope
    # (out-of-family Codex round 11; the same defect class as round 5's `attempt_resume`).
    tree = ast.parse(driver_path.read_text())
    emit_lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "emit"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "_emitter"
    ]
    assert emit_lines, (
        "no `_emitter.emit(...)` call found in the driver — the skill-activation emission "
        "may have been renamed or removed; re-ground B-137's root counterexample"
    )
    # `_emitter` is bound from `ctx.skill_activation_emitter`, asserted so the receiver name
    # cannot silently come to mean something else.
    assert any(
        "skill_activation_emitter" in line
        for line in driver
        if line.strip().startswith("_emitter =")
    ), "`_emitter` is no longer bound from `ctx.skill_activation_emitter`"
    emit_line = min(emit_lines)
    assert emit_line < envelope_line, (
        f"the skill-activation emit ({emit_line}) no longer precedes the envelope open "
        f"({envelope_line}) — the counterexample to the 'all members are children' "
        "overclaim is gone and the scope must be re-derived"
    )

    # QUALIFIED, exactly as `resume.attempted` is (out-of-family Codex round 14 — the same
    # defect class as round 7, which this arc fixed for resume and not here). Preceding the
    # envelope makes `skill.activation` a ROOT only for a TOP-LEVEL run. Under a nested,
    # recursive `execute_workflow` the dispatcher invokes the child runner inside an active
    # `subagent.span`, so the same pre-envelope emit is a CHILD and is starved like the
    # rest. The counterexample therefore SCOPES the starved population rather than
    # exempting `skill.activation` outright — pinned by the containment witness below,
    # which is the same structure the nested-resume case relies on.
    # The load-bearing structural fact behind that qualification: the emit lives inside
    # `execute_workflow`, which is precisely the function the child runner re-enters under
    # `subagent.span`. So the same line is a root on a top-level call and a child on a
    # nested one.
    tree_fns = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.lineno < emit_line <= (node.end_lineno or node.lineno)
    ]
    assert any(fn.name == "execute_workflow" for fn in tree_fns), (
        f"the skill-activation emit at :{emit_line} is no longer inside `execute_workflow` "
        f"(enclosing: {[fn.name for fn in tree_fns]}) — the top-level-vs-nested "
        "qualification on B-137's root counterexample must be re-derived"
    )


def _callers_of(helper: str) -> list[str]:
    """Call sites of `helper` across `src/`, by AST — alias- and multiline-safe.

    Out-of-family Codex round 8: a substring scan for `helper(` misses an aliased import
    (`from ... import emit_pause_captured_span as _emit`) and a call whose parenthesis sits
    on the next line, and it can invent a caller from prose. This resolves per-module import
    aliases and matches `ast.Call` nodes, so B-162's grounding cannot go stale silently.
    """
    hits: list[str] = []
    for path in _REPO.glob("harness-*/src/**/*.py"):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:  # pragma: no cover
            continue
        names = {helper}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == helper and alias.asname:
                        names.add(alias.asname)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == helper:
                continue  # the definition itself is not a call
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            called = (
                func.id
                if isinstance(func, ast.Name)
                else func.attr
                if isinstance(func, ast.Attribute)
                else None
            )
            if called in names:
                hits.append(f"{path.relative_to(_REPO)}:{node.lineno}")
    return sorted(hits)


def test_the_pause_span_emitters_are_now_wired_b162_closed() -> None:
    """**B-162 CLOSED** — the emitters that had no caller in `src/` are now invoked.

    When this arc first measured B-137 at the real venue, `emit_pause_captured_span` and
    `emit_resume_attempted_span` implemented `C-OD-30.3`'s two declared `head=1.0` spans and
    **nothing in `src/` called either**, so neither span was ever emitted in production —
    `U-CP-65`'s AC #1, #2 and #5 were unmet even though the helpers themselves were landed
    and unit-tested. That was registered as **B-162** and this test asserted the absence,
    with the message *"re-ground B-160's and B-162's dispositions"* so closing it could not
    happen silently.

    It has now been closed: `workflow_driver.py` calls `_emit_pause_captured` after every
    `protocol.capture_pause_snapshot(...)` (11 sites across the 6 topology executors) and
    `_emit_resume_attempted` after the entry-point `protocol.attempt_resume(...)`. The
    assertion is therefore INVERTED — it now guards against the wiring being lost again.
    """
    pause_callers = _callers_of("emit_pause_captured_span")
    resume_callers = _callers_of("emit_resume_attempted_span")

    assert pause_callers, (
        "`emit_pause_captured_span` has no caller in `src/` again — C-OD-30.3's "
        "`pause.captured` span is not emitted in production and B-162 has REGRESSED"
    )
    assert resume_callers, (
        "`emit_resume_attempted_span` has no caller in `src/` again — C-OD-30.3's "
        "`resume.attempted` span is not emitted in production and B-162 has REGRESSED"
    )
    # Both are called from the workflow driver, which is the venue U-CP-65 prescribes
    # ("workflow driver invokes capture_pause_snapshot, then this helper").
    for caller in pause_callers + resume_callers:
        assert "workflow_driver.py" in caller, (
            f"an emitter is invoked from {caller}, not the workflow driver — U-CP-65's "
            "caller-side convention names the driver as the emission venue"
        )


def _driver_call_lines(method: str, *, receiver: str) -> list[int]:
    """Line numbers of `<receiver>.<method>(...)` calls in the workflow driver, by AST."""
    tree = ast.parse((_REPO / "harness-cp/src/harness_cp/workflow_driver.py").read_text())
    found: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != method:
            continue
        base = func.value
        # `protocol.attempt_resume(...)` and `cast(X, protocol).capture_pause_snapshot(...)`
        owner = (
            base.id
            if isinstance(base, ast.Name)
            else base.args[1].id
            if isinstance(base, ast.Call)
            and len(base.args) > 1
            and isinstance(base.args[1], ast.Name)
            else None
        )
        if owner == receiver:
            found.append(node.lineno)
    return sorted(found)


def test_the_two_uncalled_spans_land_on_opposite_sides_of_the_envelope() -> None:
    """**The topology split** — B-162's two spans are not symmetric.

    A first draft of B-162 gated both spans on B-137, reasoning that wiring them would put
    both inside the envelope. That is right for `pause.captured` and **wrong for
    `resume.attempted`**: the driver runs entry-point resume detection BEFORE the envelope
    opens, and says so in-line — *"The resume detection runs BEFORE the workflow.envelope
    opens — a failed resume (corruption or diff-aborted) returns FAILED without opening a
    new envelope."* So a `resume.attempted` span at its prescribed call site would be a
    **root**, would consult the composite sampler directly, and **would** receive its §9.2
    floor once added to the set. `resume.attempted` is therefore the one name among B-160's
    four unconditional names for which membership alone is sufficient — after wiring.

    **Anchored on the exact production calls (out-of-family Codex round 5).** An earlier
    draft matched the first line containing `attempt_resume`, which selected
    `_engine_recovery_loop.attempt_resume` at `:2632` — a *different* call that merely
    happens to also precede the envelope, so the assertion passed for the wrong reason. It
    now resolves `protocol.attempt_resume` and `protocol.capture_pause_snapshot` by AST,
    which are the two calls B-162's close-out actually names.
    """
    driver = (_REPO / "harness-cp/src/harness_cp/workflow_driver.py").read_text()
    envelope_line = next(
        i
        for i, line in enumerate(driver.splitlines(), 1)
        if f'start_as_current_span("{_ENVELOPE}")' in line
    )

    resume_calls = _driver_call_lines("attempt_resume", receiver="protocol")
    assert len(resume_calls) == 1, (
        f"expected exactly one entry-point `protocol.attempt_resume` call, got {resume_calls} "
        "— B-162's prescribed instrumentation point is ambiguous and must be re-grounded"
    )
    assert resume_calls[0] < envelope_line, (
        f"the entry-point resume call ({resume_calls[0]}) no longer precedes the envelope "
        f"open ({envelope_line}) — `resume.attempted` would become an envelope CHILD and "
        "B-162's topology split must be re-derived"
    )
    # NOTE the scope this buys, and the scope it does NOT (out-of-family Codex round 7):
    # preceding the envelope makes `resume.attempted` a root only for a TOP-LEVEL resume.
    # A nested child resume runs under `subagent.span`, so it is a non-root child and stays
    # gated on B-137 — pinned by
    # `test_a_nested_child_resume_runs_under_subagent_span`.

    capture_calls = _driver_call_lines("capture_pause_snapshot", receiver="protocol")
    assert capture_calls, "no `protocol.capture_pause_snapshot` call found in the driver"
    assert min(capture_calls) > envelope_line, (
        f"a pause-capture call ({min(capture_calls)}) now precedes the envelope open "
        f"({envelope_line}) — `pause.captured` would become a ROOT and would no longer be "
        "gated on B-137"
    )

    prose = " ".join(driver.replace("#", " ").split())
    assert "The resume detection runs BEFORE the workflow.envelope opens" in prose, (
        "the driver's own ordering declaration changed — re-read it before trusting the "
        "root-vs-child split B-162 records"
    )


@pytest.mark.asyncio
async def test_candidate_a_prime_admits_the_member_but_orphans_it() -> None:
    """**A′'s durable witness** (out-of-family Codex round 5) — it was an unpinned claim.

    The register calls A′ *measured*, but no committed test constructed the bare
    `HarnessCompositeSampler`; the measurement lived only in a throwaway probe, so the
    orphaned-span claim could drift silently. This pins it at the same `api.run` venue.

    A′ = drop `ParentBased` so the composite sampler is consulted for **every** span. At
    `base_rate=0.0` it admits `hitl.gate.evaluated` (a §9.2 member, matched by name) and
    **still drops `workflow.envelope`** (not a member) — so the floor span survives with
    its parent discarded. That is the orphaning the register prices, and it is also why A′
    is cheaper than C1: only floor members are admitted, not whole traces.
    """
    harness = _b72()
    exporter = InMemorySpanExporter()
    # A′ is an ALTERNATIVE to C1, so it is measured in the pre-C1 world. Co-resident with
    # v1.42 row 20 the envelope would be admitted by its OWN membership — A′ would look like
    # it keeps traces whole, which is precisely the property it does not have.
    with _pre_c1():
        provider = TracerProvider(sampler=HarnessCompositeSampler(base_rate=0.0))
        provider.add_span_processor(SimpleSpanProcessor(exporter))

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                harness._FakeTracerProvider,
                "get_tracer",
                lambda self, name, /: provider.get_tracer(name),
            )
            harness._install_fake_providers(mp, harness._SucceedingAnthropicClient())
            harness._install_fake_od_stage4(mp)
            harness._install_fake_webhook_composer_factory(mp, [])
            with tempfile.TemporaryDirectory() as tmp:
                await harness.api_run(
                    harness._FanOutSubAgentDispatchWorkflow(),
                    config=harness._config(pathlib.Path(tmp)),
                )

    exported = {s.name: s for s in exporter.get_finished_spans()}
    assert _MEMBER in exported, (
        f"A′ did not admit the §9.2 member; exported {sorted(exported)} — the register's "
        "A′ pricing must be re-derived"
    )
    assert _ENVELOPE not in exported, (
        "A′ admitted the envelope too — the orphaning claim the register prices is gone"
    )
    assert exported[_MEMBER].parent is not None, "the member should still record a parent id"
    orphan_parent = exported[_MEMBER].parent.span_id
    assert orphan_parent not in {s.context.span_id for s in exported.values()}, (
        "the member's parent WAS exported, so it is not orphaned — A′'s trace-integrity "
        "cost, which step (3) weighs against C1, no longer holds"
    )


def test_a_nested_child_resume_runs_under_subagent_span() -> None:
    """**The scope limit on B-162's root claim** (out-of-family Codex round 7).

    A prior round concluded that `resume.attempted` would be a **root** because the
    entry-point `protocol.attempt_resume` call precedes the envelope's open. That reasoning
    generalized *local line ordering inside one function* into *trace-root status*, and it
    is only valid for a **top-level** resume.

    For a **nested child** resume it is false: `sub_agent_dispatch.py` opens
    `subagent.span` and invokes `child_workflow_runner(..., pause_snapshot_input=...)`
    **inside** that block, and the child runner forwards the snapshot to `execute_workflow`
    — so the child driver's entry-point resume detection runs while `subagent.span` is
    current. `resume.attempted` would then be a **non-root child**, `ParentBased` would
    never consult its membership, and it stays gated on **B-137** exactly like
    `pause.captured`.

    So B-162's *"membership alone is sufficient"* holds for top-level resumes ONLY. This
    asserts the containment structurally, so a refactor that moves the dispatch out of the
    span reddens rather than silently invalidating the scoping.

    **Scope — STRUCTURAL, not executed** (out-of-family Codex round 12). This proves lexical
    containment of the child dispatch inside the `subagent.span` block. It does NOT observe
    the child driver's resume detection at runtime, so it does not by itself prove the OTel
    context is still current there, nor that the forwarded snapshot is non-`None` on the
    path taken. The conclusion rests on containment plus ordinary OTel context-propagation
    semantics; **an executed nested-resume parentage witness is owed** and is recorded as
    such on B-160 and B-162 before either acts on the top-level-vs-nested split.
    """
    module = _REPO / "harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py"
    tree = ast.parse(module.read_text())

    subagent_with: ast.With | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            call = item.context_expr
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr == "start_as_current_span"
                and call.args
                and isinstance(call.args[0], ast.Constant)
                and call.args[0].value == "subagent.span"
            ):
                subagent_with = node
    assert subagent_with is not None, (
        "`sub_agent_dispatch.py` no longer opens a `subagent.span` `with` block — "
        "B-162's nested-resume scoping must be re-derived"
    )

    body_start = subagent_with.body[0].lineno
    body_end = subagent_with.end_lineno or body_start
    dispatch_calls = [
        node.lineno
        for node in ast.walk(subagent_with)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "child_workflow_runner"
        and any(kw.arg == "pause_snapshot_input" for kw in node.keywords)
    ]
    assert dispatch_calls, (
        "no `child_workflow_runner(..., pause_snapshot_input=...)` call was found inside "
        "the `subagent.span` block — if the nested resume moved out of the span, "
        "`resume.attempted` may now be a root there too and B-162 must be re-scoped"
    )
    assert all(body_start <= line <= body_end for line in dispatch_calls), (
        f"the nested-resume dispatch ({dispatch_calls}) is no longer lexically inside the "
        f"`subagent.span` block (lines {body_start}-{body_end}) — re-derive B-162's "
        "top-level-only scoping"
    )


def test_candidate_a_prime_is_a_name_only_remedy() -> None:
    """**A′ does not rescue the event-carried population** (out-of-family Codex round 15).

    B-137 names two starved populations, and A′ addresses only one of them. Removing
    `ParentBased` exposes every span's NAME to `HarnessCompositeSampler`, which repairs the
    non-root **name-backed** members. It does nothing for the **event-carried** members —
    the `B-133` family, which B-137 explicitly includes — because those ride as span EVENTS
    on an ordinary carrier, and at span creation the head still sees only the carrier's
    name and applies the base-rate draw.

    So A′ is a **partial, name-only** remedy. Listing it in the step-(3) option set without
    that qualification could lead the council to select an incomplete repair.
    """
    exporter = InMemorySpanExporter()
    # Pre-C1, for the same reason as the A′ orphaning witness above: A′ is an alternative to
    # C1, and with row 20 in force the envelope's own membership would mask A′'s real scope.
    with _pre_c1():
        provider = TracerProvider(sampler=HarnessCompositeSampler(base_rate=0.0))
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("b137.a_prime.scope")

        with tracer.start_as_current_span(_ENVELOPE):
            with tracer.start_as_current_span(_MEMBER):  # name-backed §9.2 member
                pass
        with tracer.start_as_current_span("ordinary.carrier") as carrier:
            carrier.add_event(_SANDBOX)  # §9.2 member riding as an EVENT

    exported = sorted(s.name for s in exporter.get_finished_spans())
    assert exported == [_MEMBER], (
        f"expected A′ to rescue ONLY the name-backed member; got {exported}. If the "
        "event-carried carrier now survives, A′ is no longer name-only and step (3)'s "
        "option set must be re-priced."
    )

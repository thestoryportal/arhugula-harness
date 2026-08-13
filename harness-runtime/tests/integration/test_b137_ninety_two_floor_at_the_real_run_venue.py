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

2. An earlier draft called `emit_pause_captured_span` a *"real production emitter."* It is
   a real function with **no caller anywhere in `src/`** — so `pause.captured` and
   `resume.attempted` are never emitted in production, and the earlier witness drove a
   manufactured composition rather than a shipped path. That is why this module measures
   `hitl.gate.evaluated` through `api.run` instead. The uncalled-emitter fact is registered
   as **B-162** and pinned by `test_the_pause_span_emitters_have_no_caller_in_src`.

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
from contextlib import contextmanager
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
def _member_set(*, add: frozenset[str] = frozenset()) -> Generator[None]:
    original = _sm._ALWAYS_SAMPLED_LITERALS
    _sm._ALWAYS_SAMPLED_LITERALS = frozenset(original | add)
    try:
        yield
    finally:
        _sm._ALWAYS_SAMPLED_LITERALS = original


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


def test_the_member_carries_a_floor_and_the_root_does_not() -> None:
    """The asymmetry the whole finding rests on."""
    assert is_always_sampled(_MEMBER) is True, (
        f"`{_MEMBER}` left the §9.2 set — re-ground B-137 before trusting this module"
    )
    assert is_always_sampled(_ENVELOPE) is False, (
        f"`{_ENVELOPE}` entered the §9.2 set — that would deliver the floor to every "
        "in-workflow member by inheritance and close the production half of B-137"
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
    """Positive control — without it every membership result here could pass wrongly."""
    assert is_always_sampled(_ENVELOPE) is False
    with _member_set(add=frozenset({_ENVELOPE})):
        assert is_always_sampled(_ENVELOPE) is True, (
            "patching `_ALWAYS_SAMPLED_LITERALS` no longer reaches the sampler"
        )
    assert is_always_sampled(_ENVELOPE) is False, "the patch did not restore"


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
    exported = await _run_the_real_workflow(base_rate=0.0)
    assert exported == [], (
        f"spans survived a base_rate=0.0 run ({exported}) — the head composition changed "
        "and B-137 must be RE-MEASURED, which its close-out step (2) requires over "
        "re-arguing"
    )


@pytest.mark.asyncio
async def test_admitting_the_root_delivers_the_floor_candidate_c1() -> None:
    """The counterfactual, at the same venue — and it prices step (3).

    Adding `workflow.envelope` itself to §9.2 makes the identical run export both spans.
    So the loss is the ROOT's decision, not an emission failure. Without this arm the
    finding above could be read as "the member is never emitted", which it is not.

    **Scope — this arm uses `SimpleSpanProcessor`, so it prices the HEAD only.** What C1
    costs through the shipped tail chain is a separate question, measured by
    `test_candidate_c1_strands_ordinary_children_in_the_tail_buffer` below; an earlier
    draft of this arc called C1 "whole traces" on the strength of this test alone, which
    out-of-family Codex round 3 correctly rejected.
    """
    with _member_set(add=frozenset({_ENVELOPE})):
        exported = await _run_the_real_workflow(base_rate=0.0)
    assert exported == [_MEMBER, _ENVELOPE], (
        f"admitting the root did not deliver the floor to its child; got {exported}"
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


def test_candidate_c1_strands_ordinary_children_in_the_tail_buffer() -> None:
    """**C1's unpriced cost, measured through the SHIPPED tail chain.**

    An earlier draft of this arc priced C1 as *"delivers the floor and keeps traces whole,
    one line"* on the strength of a `SimpleSpanProcessor` run. Out-of-family Codex round 3
    rejected that, correctly. Driving the REAL `TailKeepSpanProcessor`:

    * C1 **does** deliver every §9.2 member plus the envelope — those take the
      always-sampled arm (`tail_keep_span_processor.py:361`) and bypass the buffer;
    * it does **not** keep traces whole. An ordinary, non-member child stays **buffered**
      at root close — and stays buffered even when a §10.2 classification trigger fires,
      because making the ROOT always-sampled means the root itself takes the bypass arm and
      `return`s **before** the root-close flush-or-drop decision ever runs.

    So under C1 a trace **that contains at least one ordinary non-member child** becomes a
    never-resolving buffered trace, drained only by `force_flush` — the **B-136** pressure
    B-137's own close-out step (5) predicts, which C1 aggravates rather than avoids.

    **Scope, stated (out-of-family Codex round 4).** This is NOT "every workflow trace". The
    B-72 venue used elsewhere in this module emits only `workflow.envelope` +
    `hitl.gate.evaluated`, both of which bypass the buffer under C1 — its buffer stays at
    zero. The ordinary child below is manufactured. The driver does open ordinary spans in
    production (`validator.evaluate` at `workflow_driver.py:5600`, plus `tool.dispatch` /
    `sandbox.*` / `secret.fetch` in the tool dispatcher), so the population is non-empty,
    but **how often such a child occurs is unmeasured and is owed before step (3) picks
    C1**.
    """

    def trial(*, envelope_in_set: bool, with_trigger: bool) -> tuple[list[str], int]:
        downstream = _Counting()
        tail = TailKeepSpanProcessor(downstream=downstream)
        provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
        provider.add_span_processor(tail)
        tracer = provider.get_tracer("b137.c1")
        with _member_set(add=frozenset({_ENVELOPE}) if envelope_in_set else frozenset()):
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

    # C1: members forwarded, ordinary child STRANDED.
    forwarded, buffered = trial(envelope_in_set=True, with_trigger=False)
    assert sorted(forwarded) == sorted([_MEMBER, _ENVELOPE]), (
        f"C1 no longer forwards the floor members; got {forwarded}"
    )
    assert buffered == 1, (
        f"expected the ordinary child to remain buffered under C1, got {buffered} — if C1 "
        "now drains at root close, its B-136 cost is gone and step (3) must be re-priced"
    )

    # ...and a §10.2 trigger does NOT rescue it, because the always-sampled root returns
    # before the root-close flush-or-drop decision.
    forwarded, buffered = trial(envelope_in_set=True, with_trigger=True)
    assert "sandbox.violation" in forwarded, "the trigger itself should still forward"
    assert buffered == 1, (
        "a §10.2 classification trigger flushed the buffer under C1 — that would remove "
        "C1's never-resolving-trace cost, so step (3)'s pricing must be re-derived"
    )


@pytest.mark.asyncio
async def test_the_tail_processor_never_sees_what_the_head_dropped() -> None:
    """Executed rather than asserted — the row's step (2) names this processor.

    `TailKeepSpanProcessor` honours §9.2 too (always-sampled spans bypass its buffer), so
    one might expect it to rescue the floor. It cannot: a span the head drops is never
    recorded, so `on_end` never runs and no tail-side rule can act on it. This drives the
    REAL processor through the REAL run and counts its `on_end` arrivals.
    """
    harness = _b72()
    arrivals: list[str] = []

    class _Counting:
        def on_start(self, span: Any, parent_context: Any = None) -> None:
            return None

        def on_end(self, span: Any) -> None:
            arrivals.append(span.name)

        def shutdown(self) -> None:
            return None

        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            return True

    provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
    provider.add_span_processor(TailKeepSpanProcessor(downstream=_Counting()))

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
        f"the tail processor received {arrivals} from a head-dropped trace — if the head "
        "now records-without-sampling, B-137's starvation boundary has moved and the row "
        "must be re-measured"
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
    # round 2): the register cites 11-of-19 to scope and price B-137's step (3), so an
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
    driver = (_REPO / "harness-cp/src/harness_cp/workflow_driver.py").read_text().splitlines()
    emit_line = next(i for i, line in enumerate(driver, 1) if "_emitter.emit(" in line)
    envelope_line = next(
        i for i, line in enumerate(driver, 1) if f'start_as_current_span("{_ENVELOPE}")' in line
    )
    assert emit_line < envelope_line, (
        f"the skill-activation emit ({emit_line}) no longer precedes the envelope open "
        f"({envelope_line}) — the counterexample to the 'all members are children' "
        "overclaim is gone and the scope must be re-derived"
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


def test_the_pause_span_emitters_have_no_caller_in_src() -> None:
    """The second correction — and a finding in its own right (**B-162**).

    `emit_pause_captured_span` / `emit_resume_attempted_span` implement C-OD-30.3's two
    declared `head=1.0` spans, but nothing in `src/` calls them, so neither span is ever
    emitted in production. That is why an earlier draft's "real production emitter" claim
    was wrong, and it makes two of B-160's four unconditional names inert for a second,
    independent reason: adding a never-emitted name to the floor set changes nothing.
    """
    # Positive control: the scanner must actually FIND callers, or "no callers" below is
    # unfalsifiable. `capture_pause_snapshot` is the sibling the driver really does call.
    control = _callers_of("capture_pause_snapshot")
    assert control, (
        "the caller scanner found no callers of `capture_pause_snapshot`, which the driver "
        "demonstrably calls — the no-caller results below are unreliable"
    )

    for helper in ("emit_pause_captured_span", "emit_resume_attempted_span"):
        callers = _callers_of(helper)
        assert callers == [], (
            f"`{helper}` now has caller(s) {callers} — C-OD-30.3's span may be live in "
            "production; re-ground B-160's and B-162's dispositions, which assume it is not"
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

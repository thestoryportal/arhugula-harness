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
   `hitl.gate.evaluated` through `api.run` instead. The uncalled-emitter fact is itself
   registered (it makes two of B-160's four unconditional names doubly inert) and is
   pinned by `test_the_pause_span_emitters_have_no_caller_in_src`.

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

import importlib.util
import pathlib
import re
import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import harness_od.sampling_mode as _sm
import pytest
from harness_od.composite_sampler import build_default_sampler
from harness_od.sampling_mode import is_always_sampled
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_ENVELOPE = "workflow.envelope"
#: A §9.2 member the B-72 fan-out workflow really emits, inside the envelope.
_MEMBER = "hitl.gate.evaluated"
_REPO = pathlib.Path(__file__).resolve().parents[3]


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


async def _run_the_real_workflow(*, base_rate: float) -> list[str]:
    """Drive the shipped `api.run` path; return the span names that were EXPORTED."""
    harness = _b72()
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=build_default_sampler(base_rate=base_rate))
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
    So the loss is the ROOT's decision, not an emission failure, and **candidate C1
    demonstrably delivers the floor** — in one line, at the same `1/base_rate` volume cost
    as candidate A. Without this arm the finding above could be read as "the member is
    never emitted", which it is not.
    """
    with _member_set(add=frozenset({_ENVELOPE})):
        exported = await _run_the_real_workflow(base_rate=0.0)
    assert exported == [_MEMBER, _ENVELOPE], (
        f"admitting the root did not deliver the floor to its child; got {exported}"
    )


# ---------------------------------------------------------------------------
# The tail half — the row's step (2) names `TailKeepSpanProcessor` explicitly
# ---------------------------------------------------------------------------


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


def _span_open_sites() -> dict[str, list[str]]:
    pattern = re.compile(r'start_as_current_span\(\s*"([^"]+)"')
    sites: dict[str, list[str]] = {}
    for path in _REPO.glob("harness-*/src/**/*.py"):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for match in pattern.finditer(line):
                sites.setdefault(match.group(1), []).append(f"{path.relative_to(_REPO)}:{lineno}")
    return sites


def test_the_scope_is_inside_the_envelope_not_all_nineteen() -> None:
    """**The correction.** The starvation is scoped, and an earlier draft overclaimed it.

    Two facts, both measured from `src/`: most §9.2 members have no span-open site at all
    (so they are not even candidates for root-vs-child starvation), and `skill.activation`
    — one that does — is emitted from a call site that PRECEDES the envelope's open, so it
    is a root and does receive its floor. Any repricing of step (3) must be against the
    members actually emitted inside the envelope.
    """
    sites = _span_open_sites()
    members = set(_sm.ALWAYS_SAMPLED_EVENT_CLASSES)

    span_backed = {
        m
        for m in members
        if (any(n.startswith(m[:-1]) for n in sites) if m.endswith("*") else m in sites)
    }
    assert 0 < len(span_backed) < len(members), (
        f"expected SOME but not all §9.2 members to be span-backed; got "
        f"{len(span_backed)}/{len(members)} — the 'all 19 are children' overclaim would be "
        "live again if this ever became total"
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


def test_the_pause_span_emitters_have_no_caller_in_src() -> None:
    """The second correction — and a finding in its own right.

    `emit_pause_captured_span` / `emit_resume_attempted_span` implement C-OD-30.3's two
    declared `head=1.0` spans, but nothing in `src/` calls them, so neither span is ever
    emitted in production. This is why the earlier draft's "real production emitter" claim
    was wrong, and it makes two of B-160's four unconditional names doubly inert: adding a
    never-emitted name to the floor set changes nothing.
    """
    for helper in ("emit_pause_captured_span", "emit_resume_attempted_span"):
        callers = [
            f"{path.relative_to(_REPO)}:{lineno}"
            for path in _REPO.glob("harness-*/src/**/*.py")
            for lineno, line in enumerate(path.read_text().splitlines(), 1)
            if f"{helper}(" in line and not line.lstrip().startswith(("def ", "#", "*"))
        ]
        assert callers == [], (
            f"`{helper}` now has caller(s) {callers} — C-OD-30.3's span may be live in "
            "production; re-ground B-160's disposition, which assumes it is not"
        )

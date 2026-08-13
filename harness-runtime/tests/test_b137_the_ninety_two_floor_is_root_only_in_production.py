"""B-137 step-(2) witness — the §9.2 always-sampled floor is **root-only**, and every
class it governs is emitted as a **non-root** span in production.

`B-137`'s close-out prescribes three steps: *"(1) RE-GROUND THE WIRING FIRST … (2)
RE-MEASURE, do not re-reason … (3) DECIDE THE POSTURE, and this is a genuine
architectural fork rather than a bug with a fix."* This module is step (2)'s result,
pinned so step (3) is decided against an executed fact rather than an argument.

**What the row already carries.** B-137 names two starved populations, and population
**(ii)** is *"non-root spans of any class, because `ParentBased` consults the inner
sampler only for roots and children inherit an unsampled parent's decision."* That
mechanism is correct and is not what this module adds.

**What this module adds — the production shape of population (ii).** The row leaves
population (ii) reading as one starved population among two. It is not a population: it
is the whole in-workflow surface. `workflow_driver.py:3281-3305` opens `workflow.envelope`
as the outer span of every workflow and states in-line that *"Every downstream child span
(LLM dispatch / tool dispatch / HITL gate / validator / pause-resume / per-server-trust)
nests under this envelope."* And `workflow.envelope` is **not** a §9.2 member. So the root
whose draw decides every workflow trace is sampled at the per-cell base rate, and **all 19
§9.2 members, at their real emission sites, are children of it.** The floor fires only for
a span that happens to be a trace root — which, in a workflow, none of them are.

**Measured** (recorded on the B-137 register row; `base_rate=0.1`, the team-binding ×
self-hosted-server cell, N=2000): a §9.2 member admits at **100%** as a root and **9.3%**
as a child of `workflow.envelope` — i.e. at base rate, indistinguishable from the 10.8%
control on an ordinary unlisted root.

**The B-160 tie-in, and why it is a gate rather than a cross-reference.** `B-160` proposes
adding six declared-`head=1.0` names to the set. Driving the **real**
`emit_pause_captured_span` under a **real** `workflow.envelope`, that repair moves
admission from 9.9% to **10.3%** — it is inert in the production shape, while moving the
same emitter standalone from 9.2% to 100%. B-160 is therefore not merely *"dependent on"*
B-137; without B-137 its repair delivers nothing at all.

**Determinism.** The measurements above are statistical; the assertions below are not.
They run at `base_rate=0.0`, where the ratio arm never admits and the always-sampled arm
always does, so each test is a decision, not a sample. The mechanism is rate-independent
(`ParentBased` consults the inner sampler only for roots at any rate), and the two
`base_rate=0.0` control tests below prove both arms behave as claimed at that rate before
any conclusion is drawn from them.

**Why the private `_ALWAYS_SAMPLED_LITERALS` is patched, and why that is not itself a
finding.** `is_always_sampled` resolves against literal/prefix structures derived once at
import (`sampling_mode.py:160-172`); patching the public `ALWAYS_SAMPLED_EVENT_CLASSES`
tuple alone is a silent no-op, and a first draft of this module drew a false negative
from exactly that. There is **no runtime mutation path** to the set in `src/` (checked
repo-wide), so the precompute is sound in production — this is test mechanics only. A
positive control below fails loudly if the patch ever stops reaching the decision.

**Scope.** This pins the *sampler's* decision at span creation. It does not model the
`TailKeepSpanProcessor`, and it does not need to: a span the head drops is never recorded,
so `on_end` never runs and no tail rule — including that processor's own §9.2
bypass-the-buffer arm — can act on it. That is the same boundary B-137's row states.
"""

from __future__ import annotations

import pathlib
from collections.abc import Generator
from contextlib import contextmanager

import harness_cp.pause_resume_protocol as _prp
import harness_od.sampling_mode as _sm
import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_od.composite_sampler import build_default_sampler
from harness_od.sampling_mode import is_always_sampled
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

#: The outer span `workflow_driver.py:3305` opens for every workflow.
_ENVELOPE = "workflow.envelope"
#: A §9.2 member with a real emitter, from C-OD-30.3's contract.
_PAUSE = "pause.captured"
#: A §9.2 member with no B-160 involvement — used to show the asymmetry is the set's,
#: not an artifact of the names B-160 happens to name.
_SANDBOX = "sandbox.violation"

_SNAPSHOT = PauseSnapshot(
    workflow_id="wf-b137",
    run_id="run-b137",
    step_index=0,
    pause_reason=WorkflowPauseReason.HITL_PENDING,
    state_summary=StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    ),
    snapshot_hash="f" * 64,
    created_at=0,
    state_ledger_anchor="0" * 64,
)


@contextmanager
def _set_membership(
    *, add: frozenset[str] = frozenset(), drop: frozenset[str] = frozenset()
) -> Generator[None]:
    """Temporarily reshape the §9.2 literal set the sampler actually consults."""
    original = _sm._ALWAYS_SAMPLED_LITERALS
    _sm._ALWAYS_SAMPLED_LITERALS = frozenset((original | add) - drop)
    try:
        yield
    finally:
        _sm._ALWAYS_SAMPLED_LITERALS = original


def _admitted(*, base_rate: float, under_envelope: bool) -> int:
    """Drive the REAL `emit_pause_captured_span` and count exported `pause.captured`.

    `under_envelope=True` nests it exactly as `workflow_driver.py:3305` does.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=build_default_sampler(base_rate=base_rate))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("harness.cp.workflow_driver")

    for _ in range(20):
        if under_envelope:
            with tracer.start_as_current_span(_ENVELOPE):
                _prp.emit_pause_captured_span(_SNAPSHOT, tracer=tracer)
        else:
            _prp.emit_pause_captured_span(_SNAPSHOT, tracer=tracer)

    return sum(1 for s in exporter.get_finished_spans() if s.name == _PAUSE)


# ---------------------------------------------------------------------------
# Controls — establish that the instrument reads what it claims to read, before
# any conclusion is drawn from it.
# ---------------------------------------------------------------------------


def test_control_the_membership_patch_reaches_the_sampler() -> None:
    """Positive control. Removing a KNOWN member must change its decision.

    Without this, a patch that silently stopped reaching `is_always_sampled` would make
    every assertion below pass for the wrong reason — which is exactly how a first draft
    of this module produced a false negative.
    """
    assert is_always_sampled(_SANDBOX) is True
    with _set_membership(drop=frozenset({_SANDBOX})):
        assert is_always_sampled(_SANDBOX) is False, (
            "patching `_ALWAYS_SAMPLED_LITERALS` no longer reaches the sampler — every "
            "membership result in this module is unreliable until this is fixed"
        )
    assert is_always_sampled(_SANDBOX) is True, "the patch did not restore"


def test_control_at_base_rate_zero_the_two_arms_are_decisions_not_samples() -> None:
    """The determinism this module's assertions rest on, established rather than assumed.

    At `base_rate=0.0` the ratio arm admits nothing and the always-sampled arm admits
    everything, so each assertion below is a decision. If the ratio arm ever admitted at
    0.0, the drop-side assertions would be vacuous.
    """
    assert _admitted(base_rate=0.0, under_envelope=False) == 0, (
        "the ratio arm admitted at base_rate=0.0 — the drop-side assertions below would "
        "no longer be decisions"
    )
    with _set_membership(add=frozenset({_PAUSE})):
        assert _admitted(base_rate=0.0, under_envelope=False) == 20, (
            "the always-sampled arm did not admit at base_rate=0.0"
        )


# ---------------------------------------------------------------------------
# The grounding — the production nesting, read off the driver itself.
# ---------------------------------------------------------------------------


def test_the_contract_declares_every_in_workflow_span_a_child_of_the_envelope() -> None:
    """Ground the PRODUCTION SHAPE from the driver, not from this module's reasoning.

    Read the claim off `workflow_driver.py` verbatim so this witness fails loudly if the
    nesting is ever reworked, rather than silently continuing to assert a stale shape.
    """
    driver = pathlib.Path(
        pytest.importorskip("harness_cp.workflow_driver").__file__ or ""
    ).read_text()

    assert f'start_as_current_span("{_ENVELOPE}")' in driver, (
        f"the driver no longer opens `{_ENVELOPE}` — B-137's production-shape premise "
        "must be re-grounded"
    )

    # The declaration is a wrapped `#` comment, so match against a de-commented,
    # whitespace-collapsed form rather than the raw text — a re-wrap must not redden
    # this, but a rewording must.
    prose = " ".join(driver.replace("#", " ").split())
    assert "Every downstream child span" in prose and "nests under this envelope" in prose, (
        "the driver's own nesting declaration changed — re-read it before trusting the "
        "root-only conclusion below"
    )
    # The two families this witness and B-160 both turn on are named in it explicitly.
    for family in ("HITL gate", "pause-resume"):
        assert family in prose, (
            f"`{family}` is no longer declared to nest under the envelope — the "
            "production shape B-137/B-160 rest on must be re-grounded"
        )


def test_the_root_of_every_workflow_trace_is_not_a_floor_member() -> None:
    """**The fact that makes the floor inert.**

    If `workflow.envelope` were a §9.2 member, every workflow trace would be admitted
    whole and each child would inherit admission — the floor would be delivered by
    inheritance. It is not a member, so the trace's fate is a base-rate draw.
    """
    assert is_always_sampled(_ENVELOPE) is False, (
        "`workflow.envelope` entered the §9.2 set — that would deliver the floor to every "
        "in-workflow class by inheritance and CLOSE the production half of B-137; "
        "re-ground the row rather than leaving this assertion inverted"
    )


# ---------------------------------------------------------------------------
# The mechanism — the root's draw decides, the child's name does not.
# ---------------------------------------------------------------------------


def test_an_admitted_root_carries_an_unlisted_child_through() -> None:
    """Half one: inheritance IGNORES the child's name when the root is admitted.

    `pause.captured` is not in the set here and the rate is 0.0, yet every one is
    admitted — because `ParentBased` never consults the inner sampler for a child.
    """
    assert is_always_sampled(_PAUSE) is False, (
        "`pause.captured` entered the set — this test's premise (an UNLISTED child) is "
        "gone; see the B-160 test below"
    )
    with _set_membership(add=frozenset({_ENVELOPE})):
        admitted = _admitted(base_rate=0.0, under_envelope=True)
    assert admitted == 20, (
        f"an admitted root did not carry its unlisted child through ({admitted}/20) — "
        "the ParentBased inheritance B-137 population (ii) rests on is not live"
    )


def test_a_dropped_root_takes_a_listed_child_down_with_it() -> None:
    """**Half two — the finding.** The floor is defeated by the root, not by the set.

    `pause.captured` IS a floor member here, and the rate is 0.0, so a root-position span
    of that name would be admitted unconditionally (the control above shows exactly
    that). Under the envelope it is dropped anyway: the head never asks its name.
    """
    with _set_membership(add=frozenset({_PAUSE})):
        standalone = _admitted(base_rate=0.0, under_envelope=False)
        under_envelope = _admitted(base_rate=0.0, under_envelope=True)

    assert standalone == 20, "floor membership did not admit the span in root position"
    assert under_envelope == 0, (
        f"a §9.2 member under `{_ENVELOPE}` was admitted ({under_envelope}/20) despite the "
        "root being dropped — if this is now true the head composition changed and B-137 "
        "should be RE-MEASURED, which its close-out step (2) requires over re-arguing"
    )


def test_the_b160_repair_is_inert_in_the_production_shape() -> None:
    """**The B-160 gate, executed.**

    B-160 proposes adding six declared-`head=1.0` names to the set. This runs that repair
    against the REAL emitter in the REAL nesting. It buys the root case and nothing else,
    so B-160 cannot close on its own — a repair that changes no admitted span is not a
    repair. Measured at the production rate 0.1: 9.9% before, 10.3% after.
    """
    before = _admitted(base_rate=0.0, under_envelope=True)
    with _set_membership(add=frozenset({_PAUSE})):
        after = _admitted(base_rate=0.0, under_envelope=True)
        after_standalone = _admitted(base_rate=0.0, under_envelope=False)

    assert after_standalone == 20, "the repair did not take effect at all — check the patch"
    assert before == after == 0, (
        f"B-160's membership repair changed in-workflow admission ({before} -> {after}) — "
        "if so it is NO LONGER gated on B-137 and both rows must be re-grounded"
    )

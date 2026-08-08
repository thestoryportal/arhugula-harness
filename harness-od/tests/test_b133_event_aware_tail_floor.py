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
exported ZERO spans for all three members. This module is that control,
inverted: the pre-repair shape is asserted as a counterfactual (W1) and the
post-repair survival is asserted end-to-end through the real processor chain
(W2-W4).

**Witness roster.**

| ID | Witness |
|---|---|
| W1  | Counterfactual — the carrier span fails BOTH name-shaped predicates, and a carrier whose events are all non-members is still dropped |
| W2  | `fallback.exhausted` survives the tail via a REAL exhausted dispatch |
| W3  | `fallback.triggered` survives the tail via a REAL capability-shortfall dispatch |
| W4  | `breaker.tripped` survives the tail via a REAL charging-fault dispatch |
| W5  | HEAD-half DECLARED BOUND — the head sampler at `base_rate=0.0` still drops the event carrier, while a span NAMED `fallback.exhausted` survives |
| W6  | Trigger-flag mirror — an event-matching span that is ALSO a §10.2 trigger sets the per-trace keep flag, preserving buffered siblings |
| W7  | `breaker.tripped` carried as an EVENT does NOT set the keep flag (`B-123` scope, NOT widened here) |
| W8  | Conservative-absent — a `files.operation` event with no `kind` forwards; with a non-mutation `kind` it does not |
| W9  | Non-matching spans still buffer; drop counters untouched |
| W10 | Root-close carrier materializes the trace decision (no buffer leak) and frees its `max_buffered_traces` slot |
| W11 | SSOT completeness — every literal member of `ALWAYS_SAMPLED_EVENT_CLASSES` forwards its carrier when carried as an EVENT |
| W12 | Name-arm precedence — an always-sampled NAME with zero events still forwards (the scan is never on that path) |

**PD-8 mutation probes** (each run by reverting the named surface, confirming
the listed witnesses go RED, then restoring):

| # | Mutation | Expected red |
|---|---|---|
| i   | Delete the event-aware arm from `on_end` | W2, W3, W4, W6, W7, W8, W10, W11 |
| ii  | `_carries_always_sampled_event` returns `False` unconditionally (name-check-only) | W2, W3, W4, W6, W7, W8, W10, W11 |
| iii | Move the event arm ABOVE the name arm | W12 stays green (the name arm's own spans carry no events) — recorded as the ordering being a COST property, not a correctness one; W9 unaffected |
| iv  | Drop the `_materialize_trace_decision` call on the root-close path | W10 |
| v   | Drop `event.attributes` from the `is_always_sampled` call | W8's non-mutation half |
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface, PersonaTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
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
    is_classification_trigger,
)
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchPayloadShapeError,
    LLMDispatchProviderUnreachableError,
)
from harness_runtime.lifecycle.retry_breaker import (
    DEFAULT_COOLDOWN_SECONDS,
    DEFAULT_FAIL_THRESHOLD,
    DEFAULT_RETRY_POLICY,
    RuntimeRetryBreaker,
)
from harness_runtime.lifecycle.retry_breaker_fallback import (
    RESERVED_LLM_DISPATCH_KEY,
    RetryBreakerFallbackDispatcher,
    RetryBreakerFallbackExhaustedError,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

CARRIER_SPAN_NAME = "harness.runtime.retry_breaker_fallback"

#: The three §9.2 members that ride as span EVENTS rather than as spans.
EVENT_SHAPED_MEMBERS = ("fallback.triggered", "breaker.tripped", "fallback.exhausted")


# ---------------------------------------------------------------------------
# Real-dispatch fixtures (mirrors of the U-RT-58 suite's fakes).
# ---------------------------------------------------------------------------


@dataclass
class _MockInner:
    """Raises the supplied fault on every `dispatch` (drives to exhaustion)."""

    outcomes: list[Mapping[str, Any] | BaseException]
    calls: list[Any] = field(default_factory=list)
    _cursor: int = 0

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> Mapping[str, Any]:
        self.calls.append((binding, step))
        outcome = self.outcomes[min(self._cursor, len(self.outcomes) - 1)]
        self._cursor += 1
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _candidate(provider: str, model: str) -> ProviderCandidate:
    family_map = {
        "anthropic": ProviderFamily.ANTHROPIC,
        "openai": ProviderFamily.OPENAI,
    }
    return ProviderCandidate(provider=provider, model=model, family=family_map[provider])


def _binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider="anthropic", model="claude-test-1"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 100},
        },
    )


def _thinking_step() -> WorkflowStep:
    """An INFERENCE_STEP requiring the THINKING capability (C-CP-03 §3.3)."""
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "think hard"}],
            "tools": None,
            "params": {"thinking": {"type": "enabled", "budget_tokens": 4096}},
        },
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="test-step-key",
        tenant_id=None,
        step_index=0,
    )


def _registry(*, max_attempts: int = 2, fail_threshold: int = DEFAULT_FAIL_THRESHOLD):
    return RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=max_attempts, backoff="full_jitter", jitter="full_jitter"
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        fail_threshold=fail_threshold,
        cooldown_seconds=DEFAULT_COOLDOWN_SECONDS,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )


async def _noop_sleep(_seconds: float) -> None:
    return None


def _tail_provider(*, base_rate: float = 1.0) -> tuple[TracerProvider, InMemorySpanExporter, Any]:
    """The REAL production processor chain: composite sampler + tail-keep."""
    exporter = InMemorySpanExporter()
    tail = TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter))
    provider = TracerProvider(sampler=build_default_sampler(base_rate=base_rate))
    provider.add_span_processor(tail)
    return provider, exporter, tail


async def _dispatch_exhausted(
    provider: TracerProvider,
    *,
    fault: BaseException,
    step: WorkflowStep,
    fail_threshold: int = DEFAULT_FAIL_THRESHOLD,
) -> None:
    """Drive a REAL dispatch to fallback-chain exhaustion."""
    chain = FallbackChain(
        primary=_candidate("anthropic", "claude-test-1"),
        same_family=(_candidate("anthropic", "claude-test-2"),),
        cross_family=(),
        terminal=None,
    )
    wrapper = RetryBreakerFallbackDispatcher(
        inner=_MockInner(outcomes=[fault]),
        retry_breaker=_registry(max_attempts=2, fail_threshold=fail_threshold),
        fallback_chain=chain,
        tracer_provider=provider,
        sleep_fn=_noop_sleep,
    )
    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding(), step, step_context=_step_context())


async def _dispatch_capability_shortfall(provider: TracerProvider) -> None:
    """Drive a REAL capability-shortfall exhaustion (emits `fallback.triggered`)."""
    chain = FallbackChain(
        primary=_candidate("openai", "gpt-test-1"),
        same_family=(),
        cross_family=(_candidate("openai", "gpt-test-2"),),
        terminal=None,
    )
    wrapper = RetryBreakerFallbackDispatcher(
        inner=_MockInner(outcomes=[]),
        retry_breaker=_registry(max_attempts=1),
        fallback_chain=chain,
        tracer_provider=provider,
        sleep_fn=_noop_sleep,
    )
    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding(), _thinking_step(), step_context=_step_context())


def _exported_event_names(exporter: InMemorySpanExporter) -> set[str]:
    return {e.name for s in exporter.get_finished_spans() for e in s.events}


# ---------------------------------------------------------------------------
# W1 — the counterfactual (what the pre-repair shape asserted).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_w1_carrier_span_fails_both_name_shaped_predicates() -> None:
    """The `B-133` defect shape, asserted rather than described.

    The dispatch carrier span is in NEITHER §9.2 (by name) NOR §10.2 (by the
    trigger predicate) — so under a name-only classification the whole trace,
    always-sampled event included, is dropped at root close. This assertion is
    what makes the repair load-bearing: if either predicate ever became True by
    name, the event arm would be redundant and this witness would go red.
    """
    provider, exporter, _ = _tail_provider(base_rate=1.0)
    plain_exporter = InMemorySpanExporter()
    plain_provider = TracerProvider(sampler=build_default_sampler(base_rate=1.0))
    plain_provider.add_span_processor(SimpleSpanProcessor(plain_exporter))
    await _dispatch_exhausted(
        plain_provider, fault=LLMDispatchProviderUnreachableError("anthropic"), step=_step()
    )
    plain_provider.force_flush()
    carrier = next(s for s in plain_exporter.get_finished_spans() if s.name == CARRIER_SPAN_NAME)
    assert is_always_sampled(carrier.name, carrier.attributes) is False
    assert is_classification_trigger(carrier) is False
    assert "fallback.exhausted" in {e.name for e in carrier.events}

    # Live control: a carrier whose events are ALL non-members is still dropped.
    tracer = provider.get_tracer("w1")
    with tracer.start_as_current_span(CARRIER_SPAN_NAME) as span:
        span.add_event("retry.skipped")
        span.add_event("exception")
    assert exporter.get_finished_spans() == ()


# ---------------------------------------------------------------------------
# W2-W4 — post-repair survival, all three members, REAL processor chain.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_w2_fallback_exhausted_survives_the_tail() -> None:
    """A REAL exhausted dispatch's `fallback.exhausted` reaches the exporter."""
    provider, exporter, tail = _tail_provider(base_rate=1.0)
    await _dispatch_exhausted(
        provider, fault=LLMDispatchProviderUnreachableError("anthropic"), step=_step()
    )
    # No `force_flush` — survival must come from the arm, not the drain path.
    assert "fallback.exhausted" in _exported_event_names(exporter)
    assert tail.buffered_trace_count == 0


@pytest.mark.asyncio
async def test_w3_fallback_triggered_survives_the_tail() -> None:
    """A REAL capability-shortfall dispatch's `fallback.triggered` reaches the exporter."""
    provider, exporter, tail = _tail_provider(base_rate=1.0)
    await _dispatch_capability_shortfall(provider)
    assert "fallback.triggered" in _exported_event_names(exporter)
    assert tail.buffered_trace_count == 0


@pytest.mark.asyncio
async def test_w4_breaker_tripped_survives_the_tail() -> None:
    """A REAL charging-fault dispatch's `breaker.tripped` reaches the exporter.

    `LLMDispatchPayloadShapeError` is a CHARGING fault (it is not one of the
    §14.6.3 five waived types), so `record_failure` fires and the breaker trips
    at `fail_threshold=1`, emitting the event on the carrier span.
    """
    provider, exporter, tail = _tail_provider(base_rate=1.0)
    await _dispatch_exhausted(
        provider,
        fault=LLMDispatchPayloadShapeError("bad shape"),
        step=_step(),
        fail_threshold=1,
    )
    assert "breaker.tripped" in _exported_event_names(exporter)
    assert tail.buffered_trace_count == 0


# ---------------------------------------------------------------------------
# W5 — the HEAD-half DECLARED BOUND, pinned honestly.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_w5_head_sampler_still_drops_the_event_carrier_declared_bound() -> None:
    """OD spec v1.38 §9.2.1 term 4 — the HEAD half is NOT repaired by this arm.

    A span's events do not exist at span creation, so `should_sample` has
    nothing to inspect; at `base_rate < 1` the event carrier is dropped before
    any processor runs. Asserted, not glossed — and paired with the discriminator
    that a span NAMED `fallback.exhausted` DOES survive the same sampler, which
    is what makes "event-shaped, not name-shaped" the operative cause.

    This bound is NOT vacuous: `team-binding x local-development` is
    HEAD_BASED_DEV at a §10.3 default base-rate of 0.5 and engages no tail
    processor, so the three event-shaped members are still dropped there.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=build_default_sampler(base_rate=0.0))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    await _dispatch_exhausted(
        provider, fault=LLMDispatchProviderUnreachableError("anthropic"), step=_step()
    )
    provider.force_flush()
    assert exporter.get_finished_spans() == ()

    # Discriminator: the SAME sampler keeps a NAME-shaped member.
    tracer = provider.get_tracer("w5")
    with tracer.start_as_current_span("fallback.exhausted"):
        pass
    provider.force_flush()
    assert [s.name for s in exporter.get_finished_spans()] == ["fallback.exhausted"]


# ---------------------------------------------------------------------------
# W6 / W7 — the trigger-flag mirror, and its `B-123` boundary.
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


def test_w7_event_carried_breaker_tripped_does_not_set_the_keep_flag() -> None:
    """`B-123` boundary — NOT widened at this leg.

    `is_classification_trigger` matches `breaker.tripped` by span NAME only, so
    an event-carried trip forwards its OWN carrier (the §9.2 floor) but does NOT
    flag the trace for §10.2 sibling preservation. Register row `B-123` owns
    that half; this witness pins the boundary so widening it is a deliberate,
    test-visible act rather than a silent drift.
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

    names = [s.name for s in exporter.get_finished_spans()]
    assert "ordinary.root" in names  # §9.2 floor delivered
    assert "sibling.work" not in names  # §10.2 sibling preservation NOT delivered
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

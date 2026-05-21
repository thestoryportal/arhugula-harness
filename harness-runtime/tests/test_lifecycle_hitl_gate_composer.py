"""Tests for U-RT-60 — HITL gate composer (C-RT-18 §14.8 v1.11).

Acceptance-criterion coverage (per Phase-2 Session-3 Track-A v2.9 L9-quater).
v1.11 minimum-viable landing — covers load-bearing ACs:

  AC #1  — Protocol satisfaction
      → test_runtime_hitl_gate_composer_satisfies_step_dispatcher_protocol
  AC #2  — AskUserQuestionSurface Protocol shape
      → test_ask_user_question_surface_protocol_is_runtime_checkable
  AC #3  — placement-trigger filter + empty-skip
      → test_dispatch_with_empty_hitl_placements_delegates_to_inner
      → test_dispatch_with_non_matching_placements_delegates_to_inner
  AC #4  — VALIDATOR_ESCALATION foreclosure
      → test_dispatch_with_validator_escalation_placement_raises_foreclosed
  AC #7  — canonical hitl.gate.evaluated 3-attribute set
      → test_hitl_gate_evaluated_span_carries_canonical_3_attributes
      → test_hitl_gate_evaluated_attribute_names_match_carrier
  AC #8  — canonical 4-span shape (response received path)
      → test_dispatch_with_matching_placement_opens_3_canonical_spans
      → test_hitl_response_class_attribute_carries_operator_response
  AC #13 — hand-coded attribute strings NOT permitted (carrier import discipline)
      → test_no_hand_coded_attribute_names_outside_carrier

Deferred to follow-on commits (clearly bounded scope at v1.11 MVP landing):
  - AC #5  HandoffContext composition + matrix-cell resolution (binding-aware path)
  - AC #6  full palette emission verification (DEFAULT_FULL_PALETTE unconditionally)
  - AC #9  4-substep audit-write verification + CXA Pattern P1 23-seam assertion
  - AC #10 4-response processing (APPROVE/EDIT/REJECT/RESPOND branch coverage)
  - AC #11 multi-placement same-position 4-span emission count assertion
  - AC #12 retry-of-gate per-attempt re-eval (requires C-RT-16 retry-wrap integration)
  - AC #14 Phase 7d batch 8 retirement event (files at U-RT-60 landing)
  - Stage 5 wiring (`bootstrap/stage_5_loop_init.py` integration)
  - MCP-server-backed `AskUserQuestionSurface` binding
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import Any, cast

import pytest
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.workflow_driver import StepDispatcher
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepID,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_od.audit_ledger_types import SignatureAlgorithm
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
)
from harness_runtime.lifecycle.hitl_gate_composer import (
    DEFAULT_FULL_PALETTE,
    HITLPlacementForeclosedAtV19Error,
    RuntimeHITLGateComposer,
    compose_hitl_action_id,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-hitl-runtime")


class _MockAskUserQuestionSurface:
    """Queue-of-canned-results mock per spec v1.11 §14.8 deferred-list MUST-language.

    Satisfies the `AskUserQuestionSurface` Protocol; pops the next canned
    result on each `ask(...)` call. Empty queue raises `RuntimeError`.
    """

    def __init__(self, results: list[AskUserQuestionResult]) -> None:
        self._results = list(results)
        self.calls: list[tuple[str, list[HITLResponse], float | None]] = []

    async def ask(
        self,
        prompt: str,
        options: Sequence[HITLResponse],
        timeout: float | None,
    ) -> AskUserQuestionResult:
        self.calls.append((prompt, list(options), timeout))
        if not self._results:
            raise RuntimeError("MockAskUserQuestionSurface: queue empty")
        return self._results.pop(0)


class _MockInnerDispatcher:
    """Sync `StepDispatcher` Protocol satisfying inner; records invocations."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, WorkflowStep, StepExecutionContext]] = []

    def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        self.calls.append((binding, step, step_context))
        return {"inner_dispatched": True}


class _MockLedgerWriter:
    """Minimal sync stub matching the `append(payload, key)` shape."""

    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, payload: Any, key: Any) -> Any:
        self.appends.append((payload, key))
        return ("dummy-entry-hash", payload, key)


class _MockAuditWriter:
    """Minimal stub matching the `append(tenant_id, audit_entry)` shape."""

    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, *, tenant_id: Any, audit_entry: Any) -> Any:
        self.appends.append((tenant_id, audit_entry))
        return ("dummy-write-result", audit_entry)


def _make_step(
    *,
    step_id: str = "step-0",
    placements: tuple[HITLPlacement, ...] = (),
) -> WorkflowStep:
    """Compose a `WorkflowStep` with `hitl_placements` attached via dynamic attr.

    The CP `WorkflowStep` model is frozen + `extra="forbid"` per
    `workflow_driver_types.py:75`; it does NOT carry `hitl_placements` as a
    declared field. The composer reads `getattr(step, "hitl_placements", ())`
    per spec §14.8.2 step 1 (tolerant of absent-field). Tests pass placements
    via a small adapter wrapper.
    """
    step = WorkflowStep(
        step_id=StepID(step_id),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={},
    )
    # Tests need to attach `hitl_placements` for composer step-1 read. Since
    # WorkflowStep is frozen + extra=forbid, wrap in a small adapter object.
    class _StepWithPlacements:
        def __init__(self, inner: WorkflowStep, placements: tuple[HITLPlacement, ...]) -> None:
            self._inner = inner
            self.hitl_placements = placements

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    return cast(WorkflowStep, _StepWithPlacements(step, placements))


def _make_step_context() -> StepExecutionContext:
    from harness_as.sandbox_tier import SandboxTier
    from harness_core import ActionID
    from harness_cp.gate_level_rule import GateLevel
    from harness_is.state_ledger_entry_schema import Identifier

    return StepExecutionContext(
        parent_action_id=ActionID("workflow:test:step:0"),
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key=Identifier("test-idempotency-key"),
        tenant_id=None,
        step_index=0,
    )


@pytest.fixture
def tracer_provider() -> tuple[TracerProvider, InMemorySpanExporter]:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def _make_composer(
    *,
    inner: _MockInnerDispatcher,
    surface: _MockAskUserQuestionSurface,
    tracer_provider: TracerProvider,
    applicable_placements: frozenset[HITLPlacementKind] = frozenset(
        {HITLPlacementKind.PRE_ACTION}
    ),
    loop: asyncio.AbstractEventLoop | None = None,
) -> RuntimeHITLGateComposer:
    if loop is None:
        # For sync-tests that don't actually invoke the surface (e.g.,
        # placement filter / VALIDATOR foreclosure paths), a new-event-loop
        # is fine. For tests that invoke the surface, the caller passes
        # the active loop.
        loop = asyncio.new_event_loop()
    return RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=applicable_placements,
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, _MockLedgerWriter()),
        audit_writer=cast(Any, _MockAuditWriter()),
        tracer_provider=tracer_provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        loop=loop,
        result_timeout_seconds=5.0,
    )


# ---------------------------------------------------------------------------
# AC #1 — Protocol satisfaction
# ---------------------------------------------------------------------------


def test_runtime_hitl_gate_composer_satisfies_step_dispatcher_protocol(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #1: `isinstance(composer, StepDispatcher)` returns True."""
    provider, _ = tracer_provider
    composer = _make_composer(
        inner=_MockInnerDispatcher(),
        surface=_MockAskUserQuestionSurface([]),
        tracer_provider=provider,
    )
    assert isinstance(composer, StepDispatcher)


# ---------------------------------------------------------------------------
# AC #2 — AskUserQuestionSurface Protocol shape
# ---------------------------------------------------------------------------


def test_ask_user_question_surface_protocol_is_runtime_checkable() -> None:
    """AC #2: Protocol is `@runtime_checkable`; mock satisfies it."""
    surface = _MockAskUserQuestionSurface([])
    assert isinstance(surface, AskUserQuestionSurface)


# ---------------------------------------------------------------------------
# AC #3 — placement-trigger filter + empty-skip
# ---------------------------------------------------------------------------


def test_dispatch_with_empty_hitl_placements_delegates_to_inner(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #3: empty `step.hitl_placements` → composer delegates directly."""
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    composer = _make_composer(
        inner=inner,
        surface=_MockAskUserQuestionSurface([]),
        tracer_provider=provider,
    )
    step = _make_step(placements=())
    ctx = _make_step_context()

    result = composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    # No HITL spans emitted
    assert exporter.get_finished_spans() == ()


def test_dispatch_with_non_matching_placements_delegates_to_inner(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #3: placements present but none matching `applicable_placements` → delegate."""
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    # composer's applicable set is {PRE_ACTION}; step declares SUB_AGENT_BOUNDARY
    composer = _make_composer(
        inner=inner,
        surface=_MockAskUserQuestionSurface([]),
        tracer_provider=provider,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
    )
    placement = HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    result = composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    assert exporter.get_finished_spans() == ()


# ---------------------------------------------------------------------------
# AC #4 — VALIDATOR_ESCALATION foreclosure
# ---------------------------------------------------------------------------


def test_dispatch_with_validator_escalation_placement_raises_foreclosed(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #4: VALIDATOR_ESCALATION placement → raises HITLPlacementForeclosedAtV19Error."""
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    composer = _make_composer(
        inner=inner,
        surface=_MockAskUserQuestionSurface([]),
        tracer_provider=provider,
        applicable_placements=frozenset({HITLPlacementKind.VALIDATOR_ESCALATION}),
    )
    placement = HITLPlacement(position=HITLPlacementKind.VALIDATOR_ESCALATION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    with pytest.raises(HITLPlacementForeclosedAtV19Error, match="VALIDATOR_ESCALATION"):
        composer.dispatch(cast(Any, object()), step, step_context=ctx)

    # No inner delegation; no spans (foreclosure raises before span open)
    assert inner.calls == []
    assert exporter.get_finished_spans() == ()


# ---------------------------------------------------------------------------
# AC #7 + AC #8 — canonical 4-span shape (response received path)
# ---------------------------------------------------------------------------


def _drive_composer_on_event_loop(
    composer: RuntimeHITLGateComposer,
    step: WorkflowStep,
    ctx: StepExecutionContext,
) -> Mapping[str, Any]:
    """Drive composer.dispatch() from a thread while the captured loop runs.

    Mirrors the production pattern: composer.dispatch is sync; it bridges to
    the captured loop via run_coroutine_threadsafe. Tests must run the loop
    while dispatch executes off-thread.
    """
    result_holder: dict[str, Any] = {}

    def _worker() -> None:
        result_holder["value"] = composer.dispatch(
            cast(Any, object()), step, step_context=ctx
        )

    async def _run() -> Mapping[str, Any]:
        await asyncio.to_thread(_worker)
        return cast(Mapping[str, Any], result_holder["value"])

    loop = composer.loop
    return loop.run_until_complete(_run())


@pytest.mark.asyncio
async def test_dispatch_with_matching_placement_opens_3_canonical_spans(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #8: response received path opens canonical 3-span hierarchy.

    gate.evaluated → invocation.opened → invocation.responded
    """
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(
                response=HITLResponse.APPROVE,
                latency_ms=42.0,
            )
        ]
    )
    composer = _make_composer(
        inner=inner,
        surface=surface,
        tracer_provider=provider,
        loop=asyncio.get_event_loop(),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    result = await asyncio.to_thread(
        composer.dispatch, cast(Any, object()), step, step_context=ctx
    )

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    assert len(surface.calls) == 1

    span_names = [s.name for s in exporter.get_finished_spans()]
    # Canonical 4-span shape per ADR-D5 v1.3 §1.8 + CP carrier
    assert "hitl.gate.evaluated" in span_names
    assert "hitl.invocation.opened" in span_names
    assert "hitl.invocation.responded" in span_names
    # Timeout span NOT emitted on response-received path
    assert "hitl.invocation.timed_out" not in span_names


@pytest.mark.asyncio
async def test_hitl_gate_evaluated_span_carries_canonical_3_attributes(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #7: hitl.gate.evaluated carries canonical 3-attribute set per ADR-D5 §1.8."""
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(
                response=HITLResponse.APPROVE,
                latency_ms=15.0,
            )
        ]
    )
    composer = _make_composer(
        inner=inner,
        surface=surface,
        tracer_provider=provider,
        loop=asyncio.get_event_loop(),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await asyncio.to_thread(
        composer.dispatch, cast(Any, object()), step, step_context=ctx
    )

    gate_spans = [
        s for s in exporter.get_finished_spans() if s.name == "hitl.gate.evaluated"
    ]
    assert len(gate_spans) == 1
    gate_span = gate_spans[0]
    attrs = dict(gate_span.attributes) if gate_span.attributes else {}
    # Canonical 3 per ADR-D5 v1.3 §1.8 row 1 + CP carrier HITL_SPAN_NAMESPACE_SCHEMA[0]
    assert "hitl.gate.level" in attrs
    assert "hitl.gate.persona_tier" in attrs
    assert "hitl.gate.required" in attrs
    # The retired hand-coded v1.9/v1.10 names MUST NOT appear
    assert "hitl.gate.evaluated.placement" not in attrs
    assert "hitl.gate.evaluated.response_palette" not in attrs
    assert "hitl.gate.evaluated.outcome" not in attrs


@pytest.mark.asyncio
async def test_hitl_response_class_attribute_carries_operator_response(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #8: hitl.invocation.responded carries canonical hitl.response.class value."""
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(
                response=HITLResponse.APPROVE,
                latency_ms=33.0,
            )
        ]
    )
    composer = _make_composer(
        inner=inner,
        surface=surface,
        tracer_provider=provider,
        loop=asyncio.get_event_loop(),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await asyncio.to_thread(
        composer.dispatch, cast(Any, object()), step, step_context=ctx
    )

    resp_spans = [
        s for s in exporter.get_finished_spans() if s.name == "hitl.invocation.responded"
    ]
    assert len(resp_spans) == 1
    attrs = dict(resp_spans[0].attributes) if resp_spans[0].attributes else {}
    # Canonical 3 per ADR-D5 v1.3 §1.8 row 3 + CP carrier HITL_SPAN_NAMESPACE_SCHEMA[2]
    assert attrs.get("hitl.response.class") == HITLResponse.APPROVE.value
    assert attrs.get("hitl.response.latency_ms") == 33.0
    assert "hitl.response.summary_hash" in attrs
    # The retired v1.9/v1.10 names MUST NOT appear
    assert "hitl.invocation.responded.response_class" not in attrs
    assert "hitl.invocation.responded.response_latency_ms" not in attrs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_compose_hitl_action_id_shape() -> None:
    """`compose_hitl_action_id` produces `hitl:<parent>:<position>` shape."""
    from harness_core import ActionID

    action_id = compose_hitl_action_id(
        ActionID("workflow:test:step:0"), HITLPlacementKind.PRE_ACTION
    )
    assert str(action_id) == "hitl:workflow:test:step:0:pre-action"


def test_default_full_palette_is_4_responses() -> None:
    """`DEFAULT_FULL_PALETTE` carries the full 4-response palette per C-CP-16 §16.1."""
    assert len(DEFAULT_FULL_PALETTE) == 4
    assert HITLResponse.APPROVE in DEFAULT_FULL_PALETTE
    assert HITLResponse.EDIT in DEFAULT_FULL_PALETTE
    assert HITLResponse.REJECT in DEFAULT_FULL_PALETTE
    assert HITLResponse.RESPOND in DEFAULT_FULL_PALETTE

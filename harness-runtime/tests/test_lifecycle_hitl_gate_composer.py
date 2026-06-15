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

from collections.abc import Mapping, Sequence
from typing import Any, cast

import pytest
from harness_core import PersonaTier
from harness_core.identity import StepID
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_entry_schema import Identifier as _Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
)
from harness_runtime.lifecycle.hitl_gate_composer import (
    DEFAULT_FULL_PALETTE,
    RuntimeHITLGateComposer,
    compose_hitl_action_id,
)
from harness_runtime.lifecycle.sync_dispatcher_facade import AsyncStepDispatcher
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

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
        workflow_id="test",
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
    inner: Any,
    surface: _MockAskUserQuestionSurface,
    tracer_provider: TracerProvider,
    applicable_placements: frozenset[HITLPlacementKind] = frozenset({HITLPlacementKind.PRE_ACTION}),
    ledger_writer: Any | None = None,
    audit_writer: Any | None = None,
) -> RuntimeHITLGateComposer:
    """Build composer fixture per U-RT-60 wrap-asymmetry fork (c) ratification.

    Composer is async per spec §14.8.1 item 1; no `loop` /
    `result_timeout_seconds` ceremony needed (those fields are dropped at
    the fork APPLIED landing). The registry-boundary sync bridging lives at
    `SyncDispatcherFacade` (asserted at AC #13 stage-5 post-condition).
    """
    return RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=applicable_placements,
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(
            Any, ledger_writer if ledger_writer is not None else _MockLedgerWriter()
        ),
        audit_writer=cast(Any, audit_writer if audit_writer is not None else _MockAuditWriter()),
        tracer_provider=tracer_provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )


# ---------------------------------------------------------------------------
# AC #1 — Protocol satisfaction
# ---------------------------------------------------------------------------


def test_runtime_hitl_gate_composer_satisfies_async_step_dispatcher_protocol(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #1 (post-U-RT-60 wrap-asymmetry fork APPLIED): `isinstance(composer,
    AsyncStepDispatcher)` returns True.

    Per the fork RATIFIED Q1=(c) wrap chain, the composer is async per spec
    §14.8.1 item 1; the sync CP `StepDispatcher` Protocol satisfaction now
    belongs to `SyncDispatcherFacade(composer)` at the registry boundary
    (asserted at AC #13 stage-5 post-condition test).
    """
    provider, _ = tracer_provider
    composer = _make_composer(
        inner=_MockInnerDispatcher(),
        surface=_MockAskUserQuestionSurface([]),
        tracer_provider=provider,
    )
    assert isinstance(composer, AsyncStepDispatcher)


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


@pytest.mark.asyncio
async def test_dispatch_with_empty_hitl_placements_delegates_to_inner(
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

    result = await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    # No HITL spans emitted
    assert exporter.get_finished_spans() == ()


@pytest.mark.asyncio
async def test_dispatch_with_non_matching_placements_delegates_to_inner(
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

    result = await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    assert exporter.get_finished_spans() == ()


# ---------------------------------------------------------------------------
# AC #4 — VALIDATOR_ESCALATION support at Reading B v1.22
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_with_validator_escalation_placement_is_filtered_at_wrap_time(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Reading B v1.22 §14.8.2 step 3: VALIDATOR_ESCALATION placements are
    filtered out of wrap-time `matching` set; wrap-time composer body
    delegates to inner dispatcher without firing a gate. The mid-step re-entry
    path at §14.15 (workflow_driver post-dispatch hook) fires these placements.
    """
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

    # Should NOT raise; wrap-time composer filters VALIDATOR_ESCALATION out
    # and delegates to inner dispatcher per v1.22 amendment.
    result = await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    # No gate spans emitted at wrap-time path; mid-step re-entry at §14.15
    # is the firing site for VALIDATOR_ESCALATION.
    assert exporter.get_finished_spans() == ()


# ---------------------------------------------------------------------------
# AC #7 + AC #8 — canonical 4-span shape (response received path)
# ---------------------------------------------------------------------------


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
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    result = await composer.dispatch(cast(Any, object()), step, step_context=ctx)

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
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    gate_spans = [s for s in exporter.get_finished_spans() if s.name == "hitl.gate.evaluated"]
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
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    resp_spans = [s for s in exporter.get_finished_spans() if s.name == "hitl.invocation.responded"]
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


# ---------------------------------------------------------------------------
# AC #5 — binding-aware HandoffContext composition
# ---------------------------------------------------------------------------


def test_compose_hitl_handoff_context_inference_step_shape() -> None:
    """AC #5: `_compose_hitl_handoff_context` produces a 7-field HandoffContext.

    INFERENCE_STEP kind → `ProposedAction.action_kind = INFERENCE_STEP` per
    spec §14.8.2 step 4a. `audit_trail_link` sourced from `step_context`
    per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A.
    """
    from harness_cp.handoff_context import ActionKind, HandoffContext
    from harness_runtime.lifecycle import hitl_gate_composer as _hgc

    _compose_hitl_handoff_context = _hgc._compose_hitl_handoff_context  # pyright: ignore[reportPrivateUsage]

    step = WorkflowStep(
        step_id=StepID("step-hc-0"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"prompt": "go"},
    )
    ctx = _make_step_context()
    handoff = _compose_hitl_handoff_context(step_context=ctx, step=step)

    assert isinstance(handoff, HandoffContext)
    assert handoff.proposed_action.action_kind == ActionKind.INFERENCE_STEP
    assert handoff.proposed_action.payload == {"prompt": "go"}
    assert handoff.proposed_action.brief is None
    assert handoff.failed_attempts == ()
    assert handoff.alternatives_considered == ()
    # audit_trail_link cites parent action via step_context per spec §14.8.2 step 4a
    assert str(handoff.audit_trail_link.action_id) == str(ctx.parent_action_id)
    assert handoff.audit_trail_link.entry_hash == ctx.parent_entry_hash


@pytest.mark.asyncio
async def test_dispatch_composes_real_handoff_context_for_size_attribute(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #5: composer's `hitl.invocation.handoff_context_size_bytes` reflects
    a real serialized payload size (>0) instead of the v1.11 MVP placeholder 0.
    """
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=11.0)]
    )
    composer = _make_composer(
        inner=inner,
        surface=surface,
        tracer_provider=provider,
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    opened = [s for s in exporter.get_finished_spans() if s.name == "hitl.invocation.opened"]
    assert len(opened) == 1
    attrs = dict(opened[0].attributes) if opened[0].attributes else {}
    size = attrs.get("hitl.invocation.handoff_context_size_bytes")
    assert isinstance(size, int)
    # Real Pydantic model_dump_json byte length is non-trivial (>50 bytes for
    # a typical 7-field HandoffContext); strict >0 catches the previous v1.11
    # MVP placeholder=0 regression.
    assert size > 0


@pytest.mark.asyncio
async def test_dispatch_skips_gate_when_requires_hitl_is_false(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #5: `_hitl_required == False` → step 4j skip (no spans, delegate to inner).

    Per spec §14.8.2 step 4c bounded reading: when placement carries an
    explicit `requires_hitl=False` (future workflow-grammar shape), composer
    skips the gate; only `hitl.gate.evaluated` may fire (carries `.required=False`).
    """
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    composer = _make_composer(
        inner=inner,
        surface=_MockAskUserQuestionSurface([]),
        tracer_provider=provider,
    )

    # Build a placement with a dynamic `requires_hitl=False` attribute via
    # adapter (HITLPlacement is frozen + extra=forbid).
    class _PlacementWithRequiresHitl:
        def __init__(self, inner: HITLPlacement, requires_hitl: bool) -> None:
            self._inner = inner
            self.requires_hitl = requires_hitl

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    placement = cast(
        HITLPlacement,
        _PlacementWithRequiresHitl(
            HITLPlacement(position=HITLPlacementKind.PRE_ACTION),
            requires_hitl=False,
        ),
    )
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    result = await composer.dispatch(cast(Any, object()), step, step_context=ctx)
    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1

    span_names = [s.name for s in exporter.get_finished_spans()]
    # gate.evaluated fires (records the decision per U-CP-46 AC #10);
    # invocation.opened MUST NOT fire because the surface was never invoked.
    assert "hitl.gate.evaluated" in span_names
    assert "hitl.invocation.opened" not in span_names
    assert "hitl.invocation.responded" not in span_names
    # And the gate-evaluated span carries .required=False
    gate = [s for s in exporter.get_finished_spans() if s.name == "hitl.gate.evaluated"][0]
    attrs = dict(gate.attributes) if gate.attributes else {}
    assert attrs.get("hitl.gate.required") is False


# ---------------------------------------------------------------------------
# AC #6 — full palette emission verification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_surface_receives_full_4_response_palette(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #6: composer passes the full 4-response palette to surface.ask unconditionally."""
    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)]
    )
    composer = _make_composer(
        inner=inner,
        surface=surface,
        tracer_provider=provider,
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert len(surface.calls) == 1
    _, options, _ = surface.calls[0]
    assert set(options) == set(DEFAULT_FULL_PALETTE)
    assert len(options) == 4


# ---------------------------------------------------------------------------
# AC #9 — 4-substep audit-write E2E (8a → 8b → 8c → 8d)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_4_substep_audit_chain_writes_one_cp_one_od_entry_per_placement(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #9: one matching placement → ledger_writer.append called once (8b);
    audit_writer.append called once (8d) carrying the converted OD entry."""
    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=5.0)]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    # 8b: one F2 entry appended with action_id matching hitl:<parent>:<position>
    assert len(ledger.appends) == 1
    payload, _key = ledger.appends[0]
    assert str(payload.action_id).startswith("hitl:")
    assert "pre-action" in str(payload.action_id)
    # 8d: one OD audit entry persisted; it's the result of cp_audit_to_od_audit
    assert len(audit.appends) == 1
    tenant_id, od_entry = audit.appends[0]
    assert tenant_id == ctx.tenant_id
    # The OD AuditLedgerEntry's payload carries the CP-projected attrs
    from harness_od.audit_ledger_types import AuditLedgerEntry

    assert isinstance(od_entry, AuditLedgerEntry)
    # Substep 8c projected the CP entry's action_id under audit.cp.action_id
    cp_action_id_attr = od_entry.payload.audit_namespace_attrs.get("audit.cp.action_id")
    assert cp_action_id_attr is not None and cp_action_id_attr.startswith("hitl:")


@pytest.mark.asyncio
async def test_8b_hitl_f2_entry_populates_procedural_tier_snapshot_ref(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """R-003: the 8b-HITL F2 entry populates `procedural_tier_snapshot_ref` via
    the injected resolver closure (workflow-context emission per IS spec v1.3
    §C-IS-05 §5.1)."""
    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=5.0)]
    )
    ledger = _MockLedgerWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, _MockAuditWriter()),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    await composer.dispatch(cast(Any, object()), step, step_context=_make_step_context())
    assert len(ledger.appends) == 1
    payload, _key = ledger.appends[0]
    assert payload.procedural_tier_snapshot_ref == _Identifier("b" * 64)


@pytest.mark.asyncio
async def test_8b_hitl_resolver_raise_halts_before_ledger_write(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """R-003 HALT: a raising procedural-tier resolver fires before the 8b-HITL
    `ledger_writer.append`, so no F2 entry is written (invariant holds whether
    the composer re-raises or swallows the failure per its 8-substep path)."""
    provider, _ = tracer_provider
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=5.0)]
    )
    ledger = _MockLedgerWriter()

    def _boom() -> _Identifier:
        raise RuntimeError("resolver boom")

    composer = RuntimeHITLGateComposer(
        inner=_MockInnerDispatcher(),
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, _MockAuditWriter()),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=_boom,
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    try:
        await composer.dispatch(cast(Any, object()), step, step_context=_make_step_context())
    except Exception:
        pass  # raise-vs-swallow is path-dependent; the invariant below is what matters
    assert ledger.appends == [], "resolver raise must HALT before the 8b-HITL ledger write"


@pytest.mark.asyncio
async def test_cp_entry_timestamp_is_iso_8601_per_v1_28(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """CP spec v1.28 §16.5.6.X — `timestamp` is non-tier-conditional per
    C-CP-16 §16.2 + ADR-D5 §1.4. Pre-v1.28 `timestamp=""` placeholder closed
    at hitl_gate_composer.py:713 composer-site clock."""
    from datetime import datetime

    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=5.0)]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert len(audit.appends) == 1
    _tenant_id, od_entry = audit.appends[0]
    # cp_entry.timestamp projects to audit.cp.timestamp per
    # harness_cxa.cp_audit_conversion.cp_audit_to_od_audit
    timestamp = od_entry.payload.audit_namespace_attrs.get("audit.cp.timestamp")
    assert timestamp is not None and timestamp != ""
    parsed = datetime.fromisoformat(timestamp)
    assert parsed.tzinfo is not None, "timestamp MUST carry UTC tzinfo"


# ---------------------------------------------------------------------------
# AC #10 — 4-response branch coverage (APPROVE / EDIT / REJECT / RESPOND)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_response_delegates_to_inner(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #10 APPROVE: composer delegates to inner with step unchanged."""
    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0)]
    )
    composer = _make_composer(
        inner=inner,
        surface=surface,
        tracer_provider=provider,
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    result = await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1


@pytest.mark.asyncio
async def test_edit_response_records_edited_proposal_hash_in_audit(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #10 EDIT: composer records edited_proposal_hash at 8a-HITL; inner called."""
    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(
                response=HITLResponse.EDIT,
                latency_ms=12.0,
                edited_proposal="REPLACEMENT_PAYLOAD",
            )
        ]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    # Inner still called (EDIT proceeds to step 5)
    assert len(inner.calls) == 1
    # Audit entry carries audit.cp.edited_proposal_hash per converter
    _, od_entry = audit.appends[0]
    assert "audit.cp.edited_proposal_hash" in od_entry.payload.audit_namespace_attrs


@pytest.mark.asyncio
async def test_reject_response_raises_typed_error(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #10 REJECT: composer raises HITLGateRejectedError; rejection audit preserved."""
    from harness_runtime.lifecycle.hitl_gate_composer import HITLGateRejectedError

    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(
                response=HITLResponse.REJECT,
                latency_ms=8.0,
                rejection_reason="not approved",
            )
        ]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement,))
    ctx = _make_step_context()

    with pytest.raises(HITLGateRejectedError, match="rejected"):
        await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    # Inner NOT called on REJECT path
    assert inner.calls == []
    # Rejection audit entry was preserved (audit-suppression-on-REJECT discipline
    # preserves the audit fact — converter ran and audit.cp.rejection_reason_hash
    # is in the projected attrs).
    assert len(audit.appends) == 1
    _, od_entry = audit.appends[0]
    assert "audit.cp.rejection_reason_hash" in od_entry.payload.audit_namespace_attrs


@pytest.mark.asyncio
async def test_respond_response_does_not_inject_payload(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #10 RESPOND: composer records response_text_hash; step.step_payload untouched."""
    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(
                response=HITLResponse.RESPOND,
                latency_ms=4.0,
                response_text="continuing dialogue",
            )
        ]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    original_payload = {"prompt": "original"}
    inner_step = WorkflowStep(
        step_id=StepID("respond-step"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload=original_payload,
    )

    # Wrap with placements (same adapter pattern as _make_step)
    class _StepAdapter:
        def __init__(self, inner: WorkflowStep, placements: tuple[HITLPlacement, ...]) -> None:
            self._inner = inner
            self.hitl_placements = placements

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    step = cast(WorkflowStep, _StepAdapter(inner_step, (placement,)))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    # Inner WAS called (RESPOND proceeds to step 5 with step unchanged)
    assert len(inner.calls) == 1
    _, delivered_step, _ = inner.calls[0]
    # Step payload not mutated — inner sees original
    assert delivered_step.step_payload == original_payload
    # Audit carries response_text_hash
    _, od_entry = audit.appends[0]
    assert "audit.cp.response_text_hash" in od_entry.payload.audit_namespace_attrs


# ---------------------------------------------------------------------------
# AC #11 — multi-placement same-position 4-span emission count
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_two_pre_action_placements_emit_per_placement_canonical_4_spans(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #11: 2 PRE_ACTION placements on a single step → 2× each canonical span.

    Per spec v1.11 §14.8.5 hierarchy diagram + §14.8.6 Invariants ("exactly
    once per matching placement"): each matching placement gets exactly one
    `hitl.gate.evaluated` + one `hitl.invocation.opened` + one
    `hitl.invocation.responded`. Distinct action_ids per placement preserved.
    """
    provider, exporter = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0),
        ]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    # Two PRE_ACTION placements on a single step (NOTE 6-i exercise-able case)
    placement_a = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    placement_b = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    step = _make_step(placements=(placement_a, placement_b))
    ctx = _make_step_context()

    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    # Surface called twice (once per placement)
    assert len(surface.calls) == 2
    # 2× each canonical span
    span_names = [s.name for s in exporter.get_finished_spans()]
    assert span_names.count("hitl.gate.evaluated") == 2
    assert span_names.count("hitl.invocation.opened") == 2
    assert span_names.count("hitl.invocation.responded") == 2
    # 2× audit entries reach the writer
    assert len(audit.appends) == 2
    # Note: the v1.11 MVP action_id shape `hitl:<parent>:<position>` collides
    # across same-position placements; per spec §14.8.2 step 4 NOTE 6-i,
    # in-loop sub-shape is impl-discretion. This test asserts at-least the
    # 2-emission cardinality and surface invocation pattern.


# ---------------------------------------------------------------------------
# AC #12 — retry-of-gate: each C-RT-16 retry attempt re-evaluates the gate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_of_gate_re_evaluates_gate_per_attempt(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC #12: C-RT-16 retry of the HITL gate composer fires the gate on
    EVERY attempt — per spec §14.8.7 NOTE 6-iii ("operator re-asked on each
    retry attempt") + plan v2.9 U-RT-60 AC #12 literal Q2 reading.

    Wrap chain (post-U-RT-60 wrap-asymmetry fork APPLIED):

        bare async dispatcher (fails 2× then succeeds)
          → RuntimeHITLGateComposer (PRE_ACTION; async)
          → RetryBreakerFallbackDispatcher (C-RT-16; max_attempts=3)

    Each retry attempt at `retry_breaker_fallback.py:393` (
    `await self.inner.dispatch(rebound_binding, step, ...)`) re-enters the
    composer body step 1; the composer step 4f invokes the surface; the
    composer step 4h emits one CP→OD audit pair. **3 attempts → 3 surface
    invocations → 3 audit entries → 3× canonical 4-span hierarchy.**

    This test is the load-bearing AC for the fork (c) wrap chain Q1
    ratification — proves the spec-canonical wrap chain actually delivers
    the per-attempt re-evaluation semantic. Failure here means the wrap
    chain is structurally wrong; the test is the wrap-chain post-condition
    at the workflow-driver dispatch level.
    """
    # Use the C-RT-16 retry fixture pattern from
    # `test_lifecycle_retry_breaker_fallback.py` verbatim — do NOT
    # construct retry budget from scratch (advisor-flagged blind spot).
    from harness_core.identity import StepID as _StepID
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.cross_family_fallback_chain import (
        FallbackChain,
        ProviderCandidate,
        ProviderFamily,
    )
    from harness_cp.engine_class import EngineClass
    from harness_cp.per_step_override_evaluator import StepEffectiveBinding
    from harness_cp.routing_manifest_residence import RetryPolicy
    from harness_runtime.lifecycle.retry_breaker import (
        DEFAULT_RETRY_POLICY,
        RuntimeRetryBreaker,
    )
    from harness_runtime.lifecycle.retry_breaker_fallback import (
        RESERVED_LLM_DISPATCH_KEY,
        RetryBreakerFallbackDispatcher,
    )

    provider, exporter = tracer_provider

    # Bare async inner — fails 2× transient, succeeds on attempt 3.
    class _BareAsyncDispatcher:
        def __init__(self) -> None:
            self.attempt = 0
            self.outcomes: list[Mapping[str, Any] | BaseException] = [
                RuntimeError("transient attempt 0"),
                RuntimeError("transient attempt 1"),
                {"result": "success-on-attempt-3"},
            ]
            self.calls: list[Any] = []

        async def dispatch(
            self,
            binding: Any,
            step: WorkflowStep,
            *,
            step_context: StepExecutionContext,
        ) -> Mapping[str, Any]:
            self.calls.append((binding, step, step_context))
            outcome = self.outcomes[self.attempt]
            self.attempt += 1
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    bare = _BareAsyncDispatcher()
    surface = _MockAskUserQuestionSurface(
        [
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=3.0),
        ]
    )
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()

    # Row 1 of §14.8.1 wrap-asymmetry table: bare → HITL → C-RT-16.
    hitl = RuntimeHITLGateComposer(
        inner=bare,
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, audit),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )

    # C-RT-16 retry/fallback wrapper — replicate
    # `_retry_breaker_with_llm_policy(max_attempts=3)` + `_chain(_candidate)`
    # from the existing C-RT-16 fixture for parity (advisor-flagged).
    breaker = RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=3,
                backoff="full_jitter",
                jitter="full_jitter",
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )
    primary = ProviderCandidate(
        provider="anthropic",
        model="claude-test-1",
        family=ProviderFamily.ANTHROPIC,
    )
    chain = FallbackChain(primary=primary, same_family=(), cross_family=(), terminal=None)

    async def _noop_sleep(_seconds: float) -> None:
        return None

    wrapper = RetryBreakerFallbackDispatcher(
        inner=cast(Any, hitl),
        retry_breaker=breaker,
        fallback_chain=chain,
        tracer_provider=provider,
        sleep_fn=_noop_sleep,
    )

    # Standard binding + step + ctx for the C-RT-16 → HITL → bare chain.
    binding = StepEffectiveBinding(
        step_id="step-rt-60-ac-12",
        model_binding=ModelBinding(provider="anthropic", model="claude-test-1"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    placement = HITLPlacement(position=HITLPlacementKind.PRE_ACTION)
    inner_step = WorkflowStep(
        step_id=_StepID("step-rt-60-ac-12"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"messages": [{"role": "user", "content": "hi"}]},
    )

    class _StepWithPlacements:
        def __init__(self, inner: WorkflowStep, placements: tuple[HITLPlacement, ...]) -> None:
            self._inner = inner
            self.hitl_placements = placements

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    step = cast(WorkflowStep, _StepWithPlacements(inner_step, (placement,)))
    step_ctx = _make_step_context()

    # Dispatch the full wrap chain. C-RT-16 retries 3× through HITL
    # composer → bare; bare fails 2× then succeeds on attempt 3.
    result = await wrapper.dispatch(binding, step, step_context=step_ctx)
    assert result == {"result": "success-on-attempt-3"}

    # AC #12 load-bearing assertions: 3 surface invocations + 3 audit
    # entries + 3 invocations of `hitl.invocation.responded` span (one
    # per retry attempt). Each retry through the C-RT-16 wrapper re-
    # enters the HITL composer body step 1 of §14.8.2 → fires the gate.
    assert len(surface.calls) == 3, (
        f"AC #12: expected 3 surface invocations (one per retry attempt), got {len(surface.calls)}"
    )
    assert len(audit.appends) == 3, (
        f"AC #12: expected 3 audit entries (one per retry attempt), got {len(audit.appends)}"
    )
    assert bare.attempt == 3, (
        f"AC #12: expected 3 bare-inner invocations (one per retry attempt), got {bare.attempt}"
    )

    # Per spec §14.8.5 canonical 4-span shape per gate invocation: 3
    # attempts → 3× each gate/invocation span. Non-timeout response path
    # yields gate.evaluated + invocation.opened + invocation.responded
    # (timed_out NOT fired on response-received path).
    span_names = [s.name for s in exporter.get_finished_spans()]
    assert span_names.count("hitl.gate.evaluated") == 3
    assert span_names.count("hitl.invocation.opened") == 3
    assert span_names.count("hitl.invocation.responded") == 3
    assert "hitl.invocation.timed_out" not in span_names


# ---------------------------------------------------------------------------
# AC #13 — producer-side carrier import discipline (no hand-coded names)
# ---------------------------------------------------------------------------


def test_composer_source_imports_canonical_carrier_constants() -> None:
    """AC #13: composer module imports HITL_SPAN_NAMESPACE_SCHEMA + AUDIT_NAMESPACE_SCHEMA.

    Producer-side carrier-import discipline per spec §14.8.5 — the
    composer source MUST cite the canonical CP carrier; this guards against
    silent regression to hand-coded attribute names.
    """
    import inspect

    from harness_runtime.lifecycle import hitl_gate_composer

    source = inspect.getsource(hitl_gate_composer)
    assert "HITL_SPAN_NAMESPACE_SCHEMA" in source, (
        "composer source must import HITL_SPAN_NAMESPACE_SCHEMA per spec §14.8.5"
    )
    assert "AUDIT_NAMESPACE_SCHEMA" in source, (
        "composer source must import AUDIT_NAMESPACE_SCHEMA per spec §14.8.5"
    )
    # Retired v1.9/v1.10 hand-coded names MUST NOT appear in the source
    # (carrier-canonical attribute discipline per Q1+Q2 fork resolution).
    forbidden = (
        "hitl.gate.evaluated.placement",
        "hitl.gate.evaluated.response_palette",
        "hitl.gate.evaluated.outcome",
        "hitl.invocation.responded.response_class",
        "hitl.invocation.responded.response_latency_ms",
    )
    for name in forbidden:
        assert name not in source, (
            f"retired v1.9/v1.10 hand-coded attribute name {name!r} "
            f"must not appear in composer source (carrier-canonical "
            f"discipline per spec §14.8.5 v1.11)"
        )


# ---------------------------------------------------------------------------
# U-RT-116 (G1-skip; §3.8 / F-B3-1) — HITLAutoApprovePolicy in-`max()` floor
# override + the smart-HITL conditional skip + AC-1 audit-on-skip + AC-2
# EXTERNAL_* not-representable.
# ---------------------------------------------------------------------------


def _binding(persona_tier: PersonaTier, engine_class: Any = None) -> Any:
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.engine_class import EngineClass
    from harness_cp.per_step_override_evaluator import StepEffectiveBinding

    # `pure-pattern-no-engine` is non-excluded at SOLO but C-CP-07 §7.2 EXCLUDED at
    # team / multi; `save-point-checkpoint` is non-excluded at all three tiers
    # (used for the non-solo composer-level tests).
    return StepEffectiveBinding(
        step_id="step-b3",
        model_binding=ModelBinding(provider="anthropic", model="claude-test-1"),
        engine_class=(
            engine_class if engine_class is not None else EngineClass.PURE_PATTERN_NO_ENGINE
        ),
        override_applied=False,
        persona_tier=persona_tier,
    )


def _smart_composer(
    *,
    tracer_provider: TracerProvider,
    blast: Any,
    policy: Any,
    surface: _MockAskUserQuestionSurface | None = None,
    inner: _MockInnerDispatcher | None = None,
    ledger: _MockLedgerWriter | None = None,
    audit: _MockAuditWriter | None = None,
) -> RuntimeHITLGateComposer:
    """Build a composer with a bound `blast_radius_resolver` + `hitl_auto_approve_policy`.

    The resolver returns a fixed `blast` (decoupling the test from step-kind),
    matching the production stage-5 binding. The policy is the §3.8 sub-model.
    """
    return RuntimeHITLGateComposer(
        inner=cast(Any, inner if inner is not None else _MockInnerDispatcher()),
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(
            AskUserQuestionSurface,
            surface if surface is not None else _MockAskUserQuestionSurface([]),
        ),
        ledger_writer=cast(Any, ledger if ledger is not None else _MockLedgerWriter()),
        audit_writer=cast(Any, audit if audit is not None else _MockAuditWriter()),
        tracer_provider=tracer_provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
        blast_radius_resolver=lambda _step: blast,
        hitl_auto_approve_policy=policy,
    )


def _pre_action_step() -> WorkflowStep:
    return _make_step(placements=(HITLPlacement(position=HITLPlacementKind.PRE_ACTION),))


# --- _policy_floor_overrides pure-function (the in-`max()` named-cell logic) -


def test_policy_floor_overrides_solo_read_only_default_lowers_persona_only() -> None:
    from harness_as import BlastRadiusTier
    from harness_cp.gate_level_rule import GateLevel
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import _policy_floor_overrides

    persona_ovr, blast_ovr = _policy_floor_overrides(
        HITLAutoApprovePolicy(), PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.READ_ONLY
    )
    # Default: persona knob ON → AUTO; LOCAL_MUTATION knob OFF + READ_ONLY step
    # → no blast override (READ_ONLY blast floor is already AUTO).
    assert persona_ovr is GateLevel.AUTO
    assert blast_ovr is None


def test_policy_floor_overrides_solo_local_mutation_opt_in_lowers_blast() -> None:
    from harness_as import BlastRadiusTier
    from harness_cp.gate_level_rule import GateLevel
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import _policy_floor_overrides

    policy = HITLAutoApprovePolicy(solo_local_mutation_floor_auto=True)
    persona_ovr, blast_ovr = _policy_floor_overrides(
        policy, PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.LOCAL_MUTATION
    )
    assert persona_ovr is GateLevel.AUTO
    assert blast_ovr is GateLevel.AUTO


def test_policy_floor_overrides_external_reversible_blast_never_lowered() -> None:
    # AC-2: EXTERNAL_REVERSIBLE is NOT representable — even with BOTH knobs ON, the
    # blast override stays None for an EXTERNAL_REVERSIBLE step (the named cell is
    # LOCAL_MUTATION only). The hard-stop floor (ASK) is preserved structurally.
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import _policy_floor_overrides

    policy = HITLAutoApprovePolicy(
        solo_persona_floor_auto=True, solo_local_mutation_floor_auto=True
    )
    _persona_ovr, blast_ovr = _policy_floor_overrides(
        policy, PersonaTier.SOLO_DEVELOPER, BlastRadiusTier.EXTERNAL_REVERSIBLE
    )
    assert blast_ovr is None


@pytest.mark.parametrize("tier", [PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE])
def test_policy_floor_overrides_non_solo_no_override(tier: PersonaTier) -> None:
    # Solo-scoped: at team / multi the knobs do NOT apply (multi structurally
    # foreclosed, team a registered follow-on). Both overrides None.
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import _policy_floor_overrides

    persona_ovr, blast_ovr = _policy_floor_overrides(
        HITLAutoApprovePolicy(), tier, BlastRadiusTier.READ_ONLY
    )
    assert persona_ovr is None
    assert blast_ovr is None


# --- composer end-to-end: the conditional skip (§3.8 arithmetic table) -------


@pytest.mark.asyncio
async def test_solo_read_only_default_policy_skips_gate(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """§3.8 row 1: solo READ_ONLY + default policy → AUTO → skip (the headline)."""
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    inner = _MockInnerDispatcher()
    surface = _MockAskUserQuestionSurface([])  # empty: a prompt would raise
    composer = _smart_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.READ_ONLY,
        policy=HITLAutoApprovePolicy(),
        surface=surface,
        inner=inner,
    )
    result = await composer.dispatch(
        _binding(PersonaTier.SOLO_DEVELOPER), _pre_action_step(), step_context=_make_step_context()
    )
    # Gate skipped: inner dispatched, operator NEVER prompted.
    assert result == {"inner_dispatched": True}
    assert len(inner.calls) == 1
    assert surface.calls == [], "READ_ONLY solo skip MUST NOT prompt the operator"


@pytest.mark.asyncio
async def test_solo_local_mutation_default_policy_gates(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """§3.8 row 2: solo LOCAL_MUTATION + default (opt-in OFF) → ASK → gate."""
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)]
    )
    composer = _smart_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.LOCAL_MUTATION,
        policy=HITLAutoApprovePolicy(),  # opt-in OFF
        surface=surface,
    )
    await composer.dispatch(
        _binding(PersonaTier.SOLO_DEVELOPER), _pre_action_step(), step_context=_make_step_context()
    )
    assert len(surface.calls) == 1, "LOCAL_MUTATION with opt-in OFF MUST gate (prompt)"


@pytest.mark.asyncio
async def test_solo_local_mutation_opt_in_skips_gate(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """§3.8 row 2 (opt-in ON): solo LOCAL_MUTATION + knob2 ON → AUTO → skip."""
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    surface = _MockAskUserQuestionSurface([])
    composer = _smart_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.LOCAL_MUTATION,
        policy=HITLAutoApprovePolicy(solo_local_mutation_floor_auto=True),
        surface=surface,
    )
    await composer.dispatch(
        _binding(PersonaTier.SOLO_DEVELOPER), _pre_action_step(), step_context=_make_step_context()
    )
    assert surface.calls == [], "LOCAL_MUTATION opt-in ON MUST skip (no prompt)"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "blast_name",
    ["EXTERNAL_REVERSIBLE", "EXTERNAL_IRREVERSIBLE"],
)
async def test_solo_external_always_gates_even_with_both_knobs(
    blast_name: str,
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """§3.8 rows 3/4 (AC-2): solo EXTERNAL_* gates even with BOTH knobs ON — the
    hard-stop is structural (the policy cannot express an EXTERNAL_* override)."""
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)]
    )
    composer = _smart_composer(
        tracer_provider=provider,
        blast=getattr(BlastRadiusTier, blast_name),
        policy=HITLAutoApprovePolicy(
            solo_persona_floor_auto=True, solo_local_mutation_floor_auto=True
        ),
        surface=surface,
    )
    await composer.dispatch(
        _binding(PersonaTier.SOLO_DEVELOPER), _pre_action_step(), step_context=_make_step_context()
    )
    assert len(surface.calls) == 1, f"{blast_name} MUST gate (hard-stop) regardless of policy"


@pytest.mark.asyncio
@pytest.mark.parametrize("tier", [PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE])
async def test_non_solo_read_only_still_gates(
    tier: PersonaTier,
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Solo-scoped: at team / multi the policy does NOT apply — READ_ONLY still gates."""
    from harness_as import BlastRadiusTier
    from harness_cp.engine_class import EngineClass
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    surface = _MockAskUserQuestionSurface(
        [AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)]
    )
    composer = _smart_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.READ_ONLY,
        policy=HITLAutoApprovePolicy(),
        surface=surface,
    )
    # `save-point-checkpoint` is non-excluded at team / multi (pure-pattern is
    # C-CP-07 §7.2 excluded there — the matrix-cell exclusion is orthogonal).
    await composer.dispatch(
        _binding(tier, EngineClass.SAVE_POINT_CHECKPOINT),
        _pre_action_step(),
        step_context=_make_step_context(),
    )
    assert len(surface.calls) == 1, f"{tier.value} READ_ONLY MUST gate (policy is solo-scoped)"


# --- AC-1 (C10 audit-wiring guard) — non-vacuous §20.1 audit on the skip -----


@pytest.mark.asyncio
async def test_policy_skip_emits_non_vacuous_audit_by_execution(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC-1: each policy-caused skip emits a NON-VACUOUS §20.1 audit-ledger entry,
    verified BY EXECUTION (the actual skip path → capturing writers)."""
    from harness_as import BlastRadiusTier
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    ledger = _MockLedgerWriter()
    audit = _MockAuditWriter()
    composer = _smart_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.READ_ONLY,
        policy=HITLAutoApprovePolicy(),
        ledger=ledger,
        audit=audit,
    )
    await composer.dispatch(
        _binding(PersonaTier.SOLO_DEVELOPER), _pre_action_step(), step_context=_make_step_context()
    )
    # The full 4-substep audit-write ran on the skip path (NOT a no-op): one F2
    # (8b-HITL) ledger write + one OD (8d-HITL) audit append.
    assert len(ledger.appends) == 1, "policy skip MUST F2-write the auto-approval (8b-HITL)"
    assert len(audit.appends) == 1, "policy skip MUST emit the §20.1 audit entry (8d-HITL)"
    payload, _key = ledger.appends[0]
    assert str(payload.action_id).startswith("hitl:"), "auto-approve action_id carries hitl: prefix"


def test_auto_approve_audit_entry_is_non_vacuous_approve_not_timeout(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """AC-1 shape: the auto-approve audit entry is `response="approve"` + `gate_level=AUTO`
    — NOT the timeout partial `response=""` (which would be vacuous)."""
    from harness_as import BlastRadiusTier
    from harness_cp.gate_level_rule import GateLevel as CPGateLevel
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy

    provider, _ = tracer_provider
    composer = _smart_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.READ_ONLY,
        policy=HITLAutoApprovePolicy(),
    )
    cp_entry, _write = composer._compose_and_persist_audit(
        parent_action_id=cast(Any, "workflow:test:step:0"),
        placement=HITLPlacement(position=HITLPlacementKind.PRE_ACTION),
        cell=cast(Any, None),
        gate_result=None,
        step_context=_make_step_context(),
        raise_on_failure=True,
        auto_approved=True,
    )
    assert cp_entry.response == HITLResponse.APPROVE.value
    assert cp_entry.response != "", "auto-approve entry MUST NOT be the vacuous timeout shape"
    assert cp_entry.gate_level == CPGateLevel.AUTO


# ---------------------------------------------------------------------------
# U-RT-117 (G2; D-palette) — compute gate_level ONCE + thread the real value
# into the step-4d palette (replacing the hardcoded ASK + double-computation).
# ---------------------------------------------------------------------------


def test_compute_gate_decision_returns_none_for_partial_binding() -> None:
    """U-RT-117 fallback: no persona_tier / no blast → None (caller uses
    requires_hitl + DEFAULT_FULL_PALETTE per the Reading-B v1.22 tolerance)."""
    from types import SimpleNamespace

    from harness_runtime.lifecycle.hitl_gate_composer import _compute_gate_decision

    assert _compute_gate_decision(binding=SimpleNamespace(), resolved_blast_radius=None) is None


def test_effective_palette_ask_and_auto_are_full_palette() -> None:
    """U-RT-117 regression-safety: ASK/AUTO → full palette (== prior hardcoded-ASK
    behavior); only DENY narrows."""
    from harness_cp.gate_level_rule import GateLevel
    from harness_runtime.lifecycle.hitl_gate_composer import (
        DEFAULT_FULL_PALETTE,
        _effective_palette_for,
    )

    assert _effective_palette_for(GateLevel.ASK) == DEFAULT_FULL_PALETTE
    assert _effective_palette_for(GateLevel.AUTO) == DEFAULT_FULL_PALETTE


def test_compute_once_deny_tier_tool_threads_deny_row_narrowing() -> None:
    """U-RT-117 AC: a synthetic `per_tool_gate_level=DENY` reaches `gate_level=DENY`
    and the threaded palette is the §19.4 deny-row `{REJECT, RESPOND}` (the G2
    payoff — reachable via the per-tool axis; inert-but-harmless in production
    until the G2c producer / O-CP-3 lands)."""
    from types import SimpleNamespace

    from harness_as import BlastRadiusTier
    from harness_cp.gate_level_rule import GateLevel
    from harness_runtime.lifecycle.hitl_gate_composer import (
        _compute_gate_decision,
        _effective_palette_for,
    )

    binding = SimpleNamespace(
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        per_tool_gate_level=GateLevel.DENY,
    )
    decision = _compute_gate_decision(
        binding=binding, resolved_blast_radius=BlastRadiusTier.READ_ONLY
    )
    assert decision is not None
    assert decision.computed_gate_level is GateLevel.DENY
    palette = _effective_palette_for(decision.computed_gate_level)
    assert palette == frozenset({HITLResponse.REJECT, HITLResponse.RESPOND})


# ---------------------------------------------------------------------------
# U-RT-118 (G4a) + U-RT-119 (G4b / §14.8.9) — timeout-degradation dispatch-on-
# mode. The ask-surface always times out; the composer consults the per-persona-
# tier vocab-A mode (U-CP-92) and dispatches: fail-closed → REJECT;
# escalate-secondary-channel → webhook + pause (degrade to fail-closed when
# unbound); fail-open unreachable; persona_tier-None → residual hard-timeout.
# ---------------------------------------------------------------------------


class _TimeoutAskSurface:
    """`AskUserQuestionSurface` whose `ask(...)` always times out."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, list[HITLResponse], float | None]] = []

    async def ask(
        self,
        prompt: str,
        options: Sequence[HITLResponse],
        timeout: float | None,
    ) -> AskUserQuestionResult:
        from harness_runtime.lifecycle.ask_user_question_surface import (
            AskUserQuestionTimeoutError,
        )

        self.calls.append((prompt, list(options), timeout))
        raise AskUserQuestionTimeoutError("mock timeout")


class _MockWebhookComposer:
    """Minimal `WebhookDeliveryComposer` stub — records the brief-delivery call
    and returns a delivered `WebhookDeliveryResult`."""

    def __init__(self) -> None:
        self.delivered: list[tuple[Any, str]] = []

    async def deliver_webhook_for_brief(self, brief: Any, idempotency_key: str) -> Any:
        from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryResult

        self.delivered.append((brief, idempotency_key))
        return WebhookDeliveryResult(
            delivered=True,
            status_code=200,
            response_idempotency_key=idempotency_key,
            delivery_attempts=1,
            final_attempt_at=0,
        )


def _timeout_composer(
    *,
    tracer_provider: TracerProvider,
    blast: Any,
    policy: Any,
    webhook: Any = None,
    pause: Any = None,
) -> RuntimeHITLGateComposer:
    """Composer whose ask-surface always times out (U-RT-118/119 tests).

    Optionally binds the webhook + pause-resume joint surface (the
    escalate-secondary-channel disposition). `blast=LOCAL_MUTATION` makes the
    gate FIRE at every tier (blast ASK-floor dominates the `max()` regardless of
    the solo policy), so the ask is invoked and times out.
    """
    return RuntimeHITLGateComposer(
        inner=cast(Any, _MockInnerDispatcher()),
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(AskUserQuestionSurface, _TimeoutAskSurface()),
        ledger_writer=cast(Any, _MockLedgerWriter()),
        audit_writer=cast(Any, _MockAuditWriter()),
        tracer_provider=tracer_provider,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
        blast_radius_resolver=lambda _step: blast,
        hitl_auto_approve_policy=policy,
        webhook_delivery_composer=cast(Any, webhook),
        pause_resume_protocol=cast(Any, pause),
    )


def _timeout_degradation_span_mode(exporter: InMemorySpanExporter) -> str | None:
    """Extract `hitl.timeout.degradation_mode_applied` from the timed_out span."""
    for span in exporter.get_finished_spans():
        if span.name == "hitl.invocation.timed_out":
            attrs = span.attributes or {}
            value = attrs.get("hitl.timeout.degradation_mode_applied")
            return None if value is None else str(value)
    return None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tier", "engine", "expected_mode"),
    [
        (PersonaTier.SOLO_DEVELOPER, "SAVE_POINT_CHECKPOINT", "fail-closed"),
        (PersonaTier.TEAM_BINDING, "SAVE_POINT_CHECKPOINT", "escalate-secondary-channel"),
        (PersonaTier.MULTI_TENANT_COMPLIANCE, "SAVE_POINT_CHECKPOINT", "fail-closed"),
    ],
)
async def test_timeout_degradation_mode_applied_from_consult(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
    tier: PersonaTier,
    engine: str,
    expected_mode: str,
) -> None:
    """U-RT-118 (G4a) — the `hitl.timeout.degradation_mode_applied` span attribute
    carries the per-persona-tier `on_hitl_timeout` consult value (vocab-A;
    U-CP-92), NOT the literal `"default"`. solo/multi → fail-closed; team →
    escalate-secondary-channel. By execution (span inspection)."""
    from harness_as import BlastRadiusTier
    from harness_cp.engine_class import EngineClass
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import HITLGateRejectedError

    provider, exporter = tracer_provider
    composer = _timeout_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.LOCAL_MUTATION,
        policy=HITLAutoApprovePolicy(),
    )
    # No webhook bound → every tier's disposition resolves to REJECT here
    # (team's escalate-secondary-channel degrades to fail-closed when unbound);
    # the G4a span attribute still reflects the RESOLVED mode (set before the
    # dispatch), which is what this test asserts.
    with pytest.raises(HITLGateRejectedError):
        await composer.dispatch(
            _binding(tier, getattr(EngineClass, engine)),
            _pre_action_step(),
            step_context=_make_step_context(),
        )
    assert _timeout_degradation_span_mode(exporter) == expected_mode


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tier",
    [PersonaTier.SOLO_DEVELOPER, PersonaTier.MULTI_TENANT_COMPLIANCE],
)
async def test_timeout_fail_closed_routes_to_reject(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
    tier: PersonaTier,
) -> None:
    """U-RT-119 (G4b; AC-3) — a fail-closed timeout (solo + multi defaults)
    routes through the step-4i REJECT disposition (`HITLGateRejectedError` →
    RT-FAIL-HITL-GATE-REJECTED), NOT the v1.9 unconditional
    `HITLGateTimeoutError`. By execution."""
    from harness_as import BlastRadiusTier
    from harness_cp.engine_class import EngineClass
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import HITLGateRejectedError

    provider, _ = tracer_provider
    composer = _timeout_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.LOCAL_MUTATION,
        policy=HITLAutoApprovePolicy(),
    )
    # The `pytest.raises(HITLGateRejectedError)` IS the contrasting-baseline: if
    # the v1.9 unconditional `HITLGateTimeoutError` were still raised, this would
    # fail to match and the test would error.
    with pytest.raises(HITLGateRejectedError):
        await composer.dispatch(
            _binding(tier, EngineClass.SAVE_POINT_CHECKPOINT),
            _pre_action_step(),
            step_context=_make_step_context(),
        )


@pytest.mark.asyncio
async def test_timeout_escalate_secondary_channel_delivers_webhook_and_pauses(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """U-RT-119 (G4b; AC-3) — a team-binding timeout (escalate-secondary-channel)
    with the webhook + pause joint surface bound delivers the gate out-of-band
    (webhook) + sets the pause flag + raises `HITLPauseRequestedSignal` (the
    workflow pauses; the gate is NOT failed). team SAVE_POINT_CHECKPOINT is
    BOTH_BY_TIER (≠ DURABLE_ASYNC) so the 4-bis branch does not pre-empt and the
    ask fires + times out. By execution."""
    from harness_as import BlastRadiusTier
    from harness_cp.engine_class import EngineClass
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import HITLPauseRequestedSignal

    provider, _ = tracer_provider
    webhook = _MockWebhookComposer()
    composer = _timeout_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.LOCAL_MUTATION,
        policy=HITLAutoApprovePolicy(),
        webhook=webhook,
        pause=object(),  # any non-None — the helper only reads webhook + flag
    )
    with pytest.raises(HITLPauseRequestedSignal):
        await composer.dispatch(
            _binding(PersonaTier.TEAM_BINDING, EngineClass.SAVE_POINT_CHECKPOINT),
            _pre_action_step(),
            step_context=_make_step_context(),
        )
    assert webhook.delivered, "escalate-secondary-channel MUST deliver the webhook"
    assert composer.pause_requested_flag.is_set(), "the pause flag MUST be set"


@pytest.mark.asyncio
async def test_timeout_escalate_degrades_to_fail_closed_when_unbound(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """U-RT-119 (G4b; AC-3 safe fallback) — a team-binding timeout
    (escalate-secondary-channel) with the webhook/pause surfaces UNBOUND degrades
    to fail-closed (REJECT), never silently continuing. By execution."""
    from harness_as import BlastRadiusTier
    from harness_cp.engine_class import EngineClass
    from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
    from harness_runtime.lifecycle.hitl_gate_composer import HITLGateRejectedError

    provider, exporter = tracer_provider
    composer = _timeout_composer(
        tracer_provider=provider,
        blast=BlastRadiusTier.LOCAL_MUTATION,
        policy=HITLAutoApprovePolicy(),
        # no webhook / no pause → joint binding absent → degrade
    )
    with pytest.raises(HITLGateRejectedError):
        await composer.dispatch(
            _binding(PersonaTier.TEAM_BINDING, EngineClass.SAVE_POINT_CHECKPOINT),
            _pre_action_step(),
            step_context=_make_step_context(),
        )
    # The mode resolved (attribute) is still escalate-secondary-channel; the
    # disposition degraded to fail-closed (the safe fallback).
    assert _timeout_degradation_span_mode(exporter) == "escalate-secondary-channel"


@pytest.mark.asyncio
async def test_timeout_persona_tier_none_residual_hard_timeout(
    tracer_provider: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """U-RT-119 (regression-safe) — a partial binding with no persona_tier has no
    resolvable degradation policy → the residual hard-timeout
    `HITLGateTimeoutError` is preserved (the v1.9 disposition for the
    unresolvable case). By execution."""
    from harness_runtime.lifecycle.hitl_gate_composer import HITLGateTimeoutError

    provider, _ = tracer_provider
    # A bare-object binding (no persona_tier) → gate fires via placement
    # requires_hitl default True; persona_tier None → residual timeout.
    composer = _make_composer(
        inner=_MockInnerDispatcher(),
        surface=cast(_MockAskUserQuestionSurface, _TimeoutAskSurface()),
        tracer_provider=provider,
    )
    with pytest.raises(HITLGateTimeoutError):
        await composer.dispatch(
            cast(Any, object()),
            _pre_action_step(),
            step_context=_make_step_context(),
        )

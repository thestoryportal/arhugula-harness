"""Tests for U-OD-35 — workflow.envelope OTel tracer integration at driver entry.

Acceptance-criterion coverage (per Implementation_Plan_Operational_Discipline_v2_14.md):
  #1 workflow.envelope span opens at workflow_driver entry (post-drain-check)
      → test_envelope_opens_on_normal_execution
      → test_envelope_does_not_open_when_drained_at_entry
  #2 Single envelope per workflow (per §C-OD-25.4 invariant 1)
      → test_single_envelope_per_workflow
  #3 Closes on normal SUCCESS / FAILED / DRAINED + on exception via OTel exception-status
      → test_envelope_status_ok_on_success
      → test_envelope_status_error_on_failed
      → test_envelope_closes_on_drained_mid_execution
  #4 Head=1.0 always-sampled (per §C-OD-25.3) — verified at OD-axis sampler config;
     at driver level: envelope span is always created when entered.
      → covered by test_envelope_opens_on_normal_execution
  #5 Integration test: root span observable at OTel collector with
     parent_span_id=null + status=OK on SUCCESS / status=ERROR on FAILED;
     subsequent child spans nest under the envelope.
      → test_envelope_is_root_span
      → test_envelope_nests_child_spans

Spec authority: OD spec v1.8 §C-OD-25.1 + §25.2 + §25.3 + §25.4 + §25.5.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import StatusCode


# ---------------------------------------------------------------------------
# Fixtures — production TracerProvider + in-memory exporter for span assertions.
# ---------------------------------------------------------------------------


_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-envelope-driver")


@pytest.fixture
def exporter_and_provider() -> tuple[InMemorySpanExporter, TracerProvider]:
    """Per-test isolated TracerProvider + in-memory exporter.

    Per-test isolation: a fresh TracerProvider is created per test so spans
    from prior tests do not leak into this test's collector. The provider is
    NOT registered globally (register_globally=False semantics) — we pass it
    via the DriverContext directly.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter, provider


def _manifest(
    *,
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
    workflow_id: str = "wf-envelope",
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=engine_class,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step(idx: int) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"step-{idx}"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"index": idx},
    )


class _FakeLedger:
    actor: Actor

    def __init__(self) -> None:
        self.actor = _ACTOR
        self.appends: list[tuple[Any, Any]] = []

    def append(self, payload: Any, write_key: Any) -> Any:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return len(self.appends) == 0

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _FakeEmitter:
    def __init__(self) -> None:
        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: WorkflowEventClass) -> None:
        self.emits.append(event_class)


class _FakeLedgerReader:
    def read_by_idempotency_key(self, idempotency_key: Any, bounded_window: Any) -> Any:
        class _Result:
            entries: tuple[object, ...] = ()
            truncated = False
            next_position = None

        return _Result()


class _FakeCtx:
    def __init__(
        self,
        *,
        tracer_provider: TracerProvider,
        drained: bool = False,
    ) -> None:
        self.ledger_writer = _FakeLedger()
        self.ledger_reader = _FakeLedgerReader()
        self.lifecycle_emitter = _FakeEmitter()
        self.drained_flag = asyncio.Event()
        if drained:
            self.drained_flag.set()
        self.tracer_provider = tracer_provider


class _EchoDispatcher:
    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        return {"step_id": str(step.step_id), "echoed_payload": dict(step.step_payload)}


class _RaisingDispatcher:
    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        raise RuntimeError("dispatcher failure for envelope FAILED test")


class _SingleKindRegistry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind != StepKind.INFERENCE_STEP:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    return cast(StepDispatcherRegistry, _SingleKindRegistry(dispatcher))


# ---------------------------------------------------------------------------
# AC #1 — Envelope opens at driver entry (post-drain-check)
# ---------------------------------------------------------------------------


def test_envelope_opens_on_normal_execution(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider)
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
    )
    spans = exporter.get_finished_spans()
    envelopes = [s for s in spans if s.name == "workflow.envelope"]
    assert len(envelopes) == 1, f"expected 1 envelope, got {len(envelopes)}"


def test_envelope_does_not_open_when_drained_at_entry(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """C-OD-25 AC #1 — envelope opens POST-drain-check. Drain-at-entry returns
    DRAINED without ever opening the envelope (no observable workflow ran)."""
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider, drained=True)
    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
    )
    assert result.status is RunStatus.DRAINED
    spans = exporter.get_finished_spans()
    envelopes = [s for s in spans if s.name == "workflow.envelope"]
    assert envelopes == [], "envelope must not open on drain-at-entry"


# ---------------------------------------------------------------------------
# AC #2 — Single envelope per workflow
# ---------------------------------------------------------------------------


def test_single_envelope_per_workflow(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider)
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
    )
    spans = exporter.get_finished_spans()
    envelopes = [s for s in spans if s.name == "workflow.envelope"]
    assert len(envelopes) == 1


# ---------------------------------------------------------------------------
# AC #3 — Status on normal close (SUCCESS / FAILED / DRAINED)
# ---------------------------------------------------------------------------


def test_envelope_status_ok_on_success(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """SUCCESS close leaves status UNSET per OTel default (UNSET is OK-equivalent
    for downstream tooling; explicit OK marking is not required by §C-OD-25.4)."""
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider)
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
    )
    envelope = _single_envelope(exporter)
    assert envelope.status.status_code in {StatusCode.UNSET, StatusCode.OK}


def test_envelope_status_error_on_failed(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider)
    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _RaisingDispatcher())),
    )
    assert result.status is RunStatus.FAILED
    envelope = _single_envelope(exporter)
    assert envelope.status.status_code is StatusCode.ERROR
    # fail_class propagates into status description (load-bearing for triage).
    assert envelope.status.description is not None
    assert "step-failure" in envelope.status.description


def test_envelope_closes_on_drained_mid_execution(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """Drain set BEFORE entry returns DRAINED with no envelope (covered above).
    Drain set MID-execution: envelope opened, then per-step drain check returns
    DRAINED — envelope closes deterministically."""
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider)

    class _DrainMidDispatcher:
        def dispatch(
            self,
            binding: StepEffectiveBinding,
            step: WorkflowStep,
            *,
            step_context: Any = None,
        ) -> dict[str, Any]:
            ctx.drained_flag.set()
            return {"step_id": str(step.step_id), "echoed_payload": {}}

    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _DrainMidDispatcher())),
    )
    assert result.status is RunStatus.DRAINED
    envelope = _single_envelope(exporter)
    # DRAINED close leaves status UNSET (DRAINED is not a fail per §C-OD-25.5
    # default — workflow.fail_class null on DRAINED outcome).
    assert envelope.status.status_code in {StatusCode.UNSET, StatusCode.OK}


# ---------------------------------------------------------------------------
# AC #5 — Root span discipline + child-span nesting
# ---------------------------------------------------------------------------


def test_envelope_is_root_span(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    exporter, provider = exporter_and_provider
    ctx = _FakeCtx(tracer_provider=provider)
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
    )
    envelope = _single_envelope(exporter)
    assert envelope.parent is None, "workflow.envelope must be a root span"
    assert envelope.context.span_id != 0


def test_envelope_nests_child_spans(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """Verifies OTel parent-context propagation per §C-OD-25.4 invariant 3 —
    child spans opened inside execute_workflow must carry the envelope as
    their parent (no manual parent-id management; trust OTel context)."""
    exporter, provider = exporter_and_provider
    tracer = provider.get_tracer("test.envelope.child")

    class _ChildSpanDispatcher:
        def dispatch(
            self,
            binding: StepEffectiveBinding,
            step: WorkflowStep,
            *,
            step_context: Any = None,
        ) -> dict[str, Any]:
            with tracer.start_as_current_span("child.span"):
                pass
            return {"step_id": str(step.step_id), "echoed_payload": {}}

    ctx = _FakeCtx(tracer_provider=provider)
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, _ChildSpanDispatcher())),
    )
    spans = exporter.get_finished_spans()
    envelope = _single_envelope(exporter)
    children = [s for s in spans if s.name == "child.span"]
    assert len(children) == 1
    assert children[0].parent is not None
    assert children[0].parent.span_id == envelope.context.span_id


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _single_envelope(exporter: InMemorySpanExporter) -> ReadableSpan:
    spans = [s for s in exporter.get_finished_spans() if s.name == "workflow.envelope"]
    assert len(spans) == 1, f"expected 1 envelope, got {len(spans)}: {[s.name for s in exporter.get_finished_spans()]}"
    return spans[0]

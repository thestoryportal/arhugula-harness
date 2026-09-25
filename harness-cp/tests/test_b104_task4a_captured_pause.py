"""B-104 Task 4a: typed pause capture (`CapturedPause`) and true numeric descent depth.

Behavior under test: the CP protocol boundary returns either an ephemeral capture (no
journal ref) or a durable capture carrying the exact ref of the record it just wrote;
a paused `RunResult` carries that ref bound to its snapshot; and the driver threads an
explicit numeric descent depth (root 0, child 1, grandchild 2) into every capture.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest
from harness_core import JournalRecordRef, PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import (
    DurableCapturedPause,
    EphemeralCapturedPause,
    PauseSnapshot,
    WorkflowPauseReason,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunResult, RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from pydantic import ValidationError

_ANCHOR = "0" * 64
_WF = "wf-b104-4a"
_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_summary(), _ANCHOR),
    )


def _ref_for(snapshot: PauseSnapshot, *, record_count: int = 1) -> JournalRecordRef:
    return JournalRecordRef(
        tenant=None,
        workflow_id=snapshot.workflow_id,
        run_id=snapshot.run_id,
        record_count=record_count,
        latest_digest="a" * 64,
        snapshot_hash=snapshot.snapshot_hash,
    )


def _capture_ephemeral(depth: int = 0) -> EphemeralCapturedPause:
    captured = asyncio.run(
        _protocol().capture_pause_snapshot(
            _WF, "run-1", 0, WorkflowPauseReason.EXPLICIT_OPERATOR, descent_depth=depth
        )
    )
    assert isinstance(captured, EphemeralCapturedPause)
    return captured


# ---------------------------------------------------------------------------
# The typed capture result
# ---------------------------------------------------------------------------


def test_cp_protocol_capture_is_ephemeral_without_a_ref() -> None:
    captured = _capture_ephemeral()
    assert isinstance(captured.snapshot, PauseSnapshot)
    assert captured.record_ref is None


def test_durable_captured_pause_carries_its_ref() -> None:
    snapshot = _capture_ephemeral().snapshot
    ref = _ref_for(snapshot)
    durable = DurableCapturedPause(snapshot=snapshot, record_ref=ref)
    assert durable.record_ref == ref
    assert durable.snapshot is snapshot


@pytest.mark.parametrize(
    "tamper",
    [
        {"snapshot_hash": "b" * 64},
        {"run_id": "some-other-run"},
        {"workflow_id": "some-other-workflow"},
    ],
)
def test_durable_captured_pause_refuses_a_ref_for_a_different_snapshot(
    tamper: dict[str, str],
) -> None:
    snapshot = _capture_ephemeral().snapshot
    foreign = _ref_for(snapshot).model_copy(update=tamper)
    with pytest.raises(ValidationError):
        DurableCapturedPause(snapshot=snapshot, record_ref=foreign)


def test_capture_requires_an_explicit_depth() -> None:
    """A caller that forgets the depth must fail loudly, never record a root by accident."""
    with pytest.raises(TypeError):
        asyncio.run(
            _protocol().capture_pause_snapshot(  # type: ignore[call-arg]
                _WF, "run-1", 0, WorkflowPauseReason.EXPLICIT_OPERATOR
            )
        )


# ---------------------------------------------------------------------------
# RunResult binds the ref to its snapshot
# ---------------------------------------------------------------------------


def _paused_result(**overrides: Any) -> RunResult:
    snapshot = _capture_ephemeral().snapshot
    fields: dict[str, Any] = {
        "workflow_id": _WF,
        "run_id": "run-1",
        "status": RunStatus.PAUSED,
        "pause_snapshot": snapshot,
    }
    fields.update(overrides)
    return RunResult(**fields)


def test_paused_result_without_a_ref_is_the_ephemeral_shape() -> None:
    assert _paused_result().pause_record_ref is None


def test_paused_result_accepts_the_ref_of_its_own_snapshot() -> None:
    snapshot = _capture_ephemeral().snapshot
    ref = _ref_for(snapshot)
    result = _paused_result(pause_snapshot=snapshot, pause_record_ref=ref)
    assert result.pause_record_ref == ref


def test_paused_result_refuses_a_ref_whose_hash_differs_from_its_snapshot() -> None:
    snapshot = _capture_ephemeral().snapshot
    wrong = _ref_for(snapshot).model_copy(update={"snapshot_hash": "c" * 64})
    with pytest.raises(ValidationError):
        _paused_result(pause_snapshot=snapshot, pause_record_ref=wrong)


def test_result_refuses_a_ref_without_a_snapshot() -> None:
    ref = _ref_for(_capture_ephemeral().snapshot)
    with pytest.raises(ValidationError):
        RunResult(
            workflow_id=_WF,
            run_id="run-1",
            status=RunStatus.PAUSED,
            pause_snapshot=None,
            pause_record_ref=ref,
        )


# ---------------------------------------------------------------------------
# The driver threads explicit depth and the ref into a real paused run
# ---------------------------------------------------------------------------


class _RecordingProtocol(PauseResumeProtocol):
    """A durable-shaped protocol: records the depth it was given, returns a durable capture."""

    def __init__(self) -> None:
        super().__init__(
            state_ledger_writer=object(),
            state_ledger_reader=object(),
            pause_context_reader=lambda: (_summary(), _ANCHOR),
        )
        self.depths: list[int] = []
        self.refs: list[JournalRecordRef] = []

    async def capture_pause_snapshot(  # type: ignore[override]
        self, *args: Any, descent_depth: int, **kwargs: Any
    ) -> DurableCapturedPause:
        self.depths.append(descent_depth)
        captured = await super().capture_pause_snapshot(
            *args, descent_depth=descent_depth, **kwargs
        )
        ref = _ref_for(captured.snapshot, record_count=len(self.depths))
        self.refs.append(ref)
        return DurableCapturedPause(snapshot=captured.snapshot, record_ref=ref)


class _Ledger:
    def __init__(self) -> None:
        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-b104-4a")
        self.appends: list[Any] = []

    def append(self, payload: Any, write_key: Any) -> Any:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return not self.appends

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _Emitter:
    def emit(self, event_class: Any) -> None:
        return None


class _Ctx:
    def __init__(self, protocol: PauseResumeProtocol) -> None:
        import asyncio as _asyncio

        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _Ledger()
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = _asyncio.Event()
        self.pause_requested_flag = _asyncio.Event()
        self.pause_resume_protocol = protocol
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.inter_step_output_channel = None


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._dispatcher
        raise StepKindDispatcherNotBoundError(step_kind)


class _FailingDispatcher:
    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        if str(step.step_id) == "s1":
            raise RuntimeError("simulated stage failure")
        return {"stage": str(step.step_id)}


def _steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID(name),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"stage": name},
        )
        for name in ("s0", "s1")
    ]


def _handoff_manifest() -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=_WF,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,  # cascade_policy=pause
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.DECENTRALIZED_HANDOFF,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _run_paused(protocol: _RecordingProtocol, **kwargs: Any) -> RunResult:
    return execute_workflow(
        _handoff_manifest(),
        _steps(),
        run_id="run-1",
        ctx=cast(DriverContext, _Ctx(protocol)),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(cast(Any, _FailingDispatcher()))),
        **kwargs,
    )


@pytest.mark.parametrize("depth", [0, 1, 2])
def test_driver_captures_at_the_descent_depth_it_was_given(depth: int) -> None:
    """Root 0, child 1, grandchild 2: the capture site sees the true numeric depth."""
    protocol = _RecordingProtocol()
    result = _run_paused(protocol, descent_depth=depth)
    assert result.status is RunStatus.PAUSED
    assert protocol.depths == [depth]


def test_paused_run_result_carries_the_ref_from_the_same_capture() -> None:
    protocol = _RecordingProtocol()
    result = _run_paused(protocol, descent_depth=1)
    assert result.pause_snapshot is not None
    assert protocol.refs == [result.pause_record_ref]
    assert result.pause_record_ref is not None
    assert result.pause_record_ref.snapshot_hash == result.pause_snapshot.snapshot_hash

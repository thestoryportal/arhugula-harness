"""B-104 Task 5b-1: CP carries the Runtime's child-resume authority as opaque data.

Behavior under test: `execute_workflow_at_depth(child_resume_authority=...)` puts the SAME
authority object on every `StepExecutionContext` a dispatcher sees, in all six strategies
and on every branch copy; the authority never reaches a pause snapshot or any hash input;
and CP itself never calls it. Callers that pass none see `None` everywhere.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp import workflow_driver as _wd
from harness_cp.engine_class import EngineClass
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    ChildResumeAuthority,
    RunResult,
    RunStatus,
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

from .test_b104_task4a_captured_pause import (
    _BINDING,  # pyright: ignore[reportPrivateUsage]
    _CHAIN,  # pyright: ignore[reportPrivateUsage]
    _Ctx,  # pyright: ignore[reportPrivateUsage]
    _RecordingProtocol,  # pyright: ignore[reportPrivateUsage]
)


class _FakeAuthority:
    """Satisfies `ChildResumeAuthority`; any CP call to it is recorded and fails the test."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, Any]] = []

    def run_admitted[R](self, verified: Any, body: Callable[[], R]) -> R:
        self.calls.append((verified, body))
        raise AssertionError("CP must never invoke a child-resume authority")


class _Recorder:
    """A dispatcher recording every `step_context` it is handed (branches may be threaded)."""

    def __init__(self) -> None:
        self.contexts: list[StepExecutionContext] = []
        self._lock = threading.Lock()

    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        with self._lock:
            self.contexts.append(step_context)
        if str(step.step_id) == "evaluate":
            return {"accepted": True, "feedback": ""}
        return {"stage": str(step.step_id)}


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._dispatcher
        raise StepKindDispatcherNotBoundError(step_kind)


def _step(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"stage": name},
    )


def _manifest(pattern: TopologyPattern) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id="wf-b104-5b1",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=pattern,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


_STRATEGY_STEPS: dict[TopologyPattern, tuple[str, ...]] = {
    TopologyPattern.SINGLE_THREADED_LINEAR: ("s0", "s1"),
    TopologyPattern.PARALLELIZATION: ("b0", "b1", "b2"),
    TopologyPattern.EVALUATOR_OPTIMIZER: ("generate", "evaluate"),
    TopologyPattern.ORCHESTRATOR_WORKERS: ("orchestrator", "w0", "w1"),
    TopologyPattern.HIERARCHICAL_DELEGATION: ("orchestrator", "w0", "w1"),
    TopologyPattern.DECENTRALIZED_HANDOFF: ("h0", "h1"),
}


def _run(pattern: TopologyPattern, recorder: Any, *, depth: int = 1, **kwargs: Any) -> RunResult:
    return _wd.execute_workflow_at_depth(
        _manifest(pattern),
        [_step(name) for name in _STRATEGY_STEPS[pattern]],
        run_id="run-5b1",
        ctx=cast(DriverContext, _Ctx(_RecordingProtocol())),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(cast(Any, recorder))),
        descent_depth=depth,
        **kwargs,
    )


@pytest.mark.parametrize("pattern", list(TopologyPattern))
def test_every_strategy_hands_the_same_authority_object_to_every_step_and_branch(
    pattern: TopologyPattern,
) -> None:
    assert set(_STRATEGY_STEPS) == set(TopologyPattern)  # all six strategies are exercised
    authority = _FakeAuthority()
    recorder = _Recorder()

    result = _run(pattern, recorder, child_resume_authority=authority)

    assert result.status is RunStatus.SUCCESS
    assert len(recorder.contexts) >= len(_STRATEGY_STEPS[pattern])
    assert all(context.child_resume_authority is authority for context in recorder.contexts)
    assert authority.calls == []  # CP only carries it


@pytest.mark.parametrize("pattern", list(TopologyPattern))
def test_a_caller_without_an_authority_sees_none_on_every_context(
    pattern: TopologyPattern,
) -> None:
    recorder = _Recorder()

    result = _run(pattern, recorder)

    assert result.status is RunStatus.SUCCESS
    assert recorder.contexts
    assert all(context.child_resume_authority is None for context in recorder.contexts)


def test_the_authority_is_a_runtime_checkable_protocol_and_only_that() -> None:
    assert isinstance(_FakeAuthority(), ChildResumeAuthority)
    assert not isinstance(object(), ChildResumeAuthority)


def test_the_authority_is_absent_from_every_serialization_of_a_step_context() -> None:
    authority = _FakeAuthority()
    recorder = _Recorder()
    _run(TopologyPattern.SINGLE_THREADED_LINEAR, recorder, child_resume_authority=authority)

    context = recorder.contexts[0]
    assert context.child_resume_authority is authority
    assert "child_resume_authority" not in context.model_dump()
    assert "child_resume_authority" not in context.model_dump_json()
    assert "child_resume_authority" not in repr(context)


def test_a_paused_run_snapshot_and_its_hash_are_identical_with_and_without_an_authority() -> None:
    """A step failure under TEAM_BINDING pauses; the captured snapshot must not see the carrier."""

    class _Failing(_Recorder):
        def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
            if str(step.step_id) == "h1":
                raise RuntimeError("simulated stage failure")
            return super().dispatch(binding, step, step_context=step_context)

    def paused(**kwargs: Any) -> RunResult:
        result = _run(TopologyPattern.DECENTRALIZED_HANDOFF, _Failing(), **kwargs)
        assert result.status is RunStatus.PAUSED and result.pause_snapshot is not None
        return result

    authority = _FakeAuthority()
    with_authority = paused(child_resume_authority=authority)
    without = paused()

    assert with_authority.pause_snapshot is not None and without.pause_snapshot is not None
    assert with_authority.pause_snapshot.snapshot_hash == without.pause_snapshot.snapshot_hash
    assert "authority" not in with_authority.pause_snapshot.model_dump_json()
    assert authority.calls == []


def test_the_root_entry_forwards_the_same_authority_without_invoking_it() -> None:
    authority = _FakeAuthority()
    recorder = _Recorder()
    result = execute_workflow(
        _manifest(TopologyPattern.SINGLE_THREADED_LINEAR),
        [_step("s0")],
        run_id="run-5b1",
        ctx=cast(DriverContext, _Ctx(_RecordingProtocol())),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(cast(Any, recorder))),
        child_resume_authority=authority,
    )
    assert result.status is RunStatus.SUCCESS
    assert recorder.contexts and all(
        c.child_resume_authority is authority for c in recorder.contexts
    )
    assert authority.calls == []  # CP carries the authority; it never invokes it

    default_recorder = _Recorder()
    default_result = execute_workflow(
        _manifest(TopologyPattern.SINGLE_THREADED_LINEAR),
        [_step("s0")],
        run_id="run-5b1",
        ctx=cast(DriverContext, _Ctx(_RecordingProtocol())),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(cast(Any, default_recorder))),
    )
    assert default_result.status is RunStatus.SUCCESS
    assert default_recorder.contexts and all(
        c.child_resume_authority is None for c in default_recorder.contexts
    )

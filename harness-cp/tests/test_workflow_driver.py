"""Tests for U-CP-56 — workflow execution driver core.

Acceptance-criterion coverage (per Implementation_Plan_Control_Plane_v2_11.md):
  #1 type surface materialized
      → test_run_result_seven_fields
      → test_run_status_four_members
      → test_step_kind_five_members
      → test_workflow_step_three_fields
      → test_typed_errors_subclass_workflow_driver_error
  #2 topology + engine-class validation at entry
      → test_topology_pattern_not_yet_materialized_raised_at_non_single_threaded_linear
      → test_engine_class_not_yet_materialized_raised_at_out_of_scope_engine_class
      → test_validation_failure_emits_no_workflow_start
  #3 workflow.start emission
      → test_workflow_start_emitted_after_validation
  #4 step iteration loop
      → test_step_iteration_declaration_order
      → test_per_step_step_boundary_emitted
      → test_state_ledger_append_per_step
      → test_step_idempotency_key_deterministic
  #5 lifecycle event filter (single-threaded-linear)
      → test_lifecycle_events_in_happy_path
      → test_no_terminal_lifecycle_event_at_success
  #6 replay-resumption read at re-entry
      → test_workflow_resumption_emitted_on_save_point_checkpoint_reentry
      → test_no_resumption_emission_under_pure_pattern_no_engine
  #7 terminal SUCCESS return
      → test_terminal_success_return_shape
  #8 failure-mode taxonomy
      → test_step_failure_returns_failed_status
      → test_ledger_append_failure_returns_failed_status
  #9 determinism
      → test_driver_iteration_deterministic_given_inputs
"""

from __future__ import annotations

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
    execute_workflow,
)
from harness_cp.workflow_driver_errors import (
    EngineClassNotYetMaterializedError,
    TopologyPatternNotYetMaterializedError,
    WorkflowDriverError,
)
from harness_cp.workflow_driver_types import (
    RunResult,
    RunStatus,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass

# ---------------------------------------------------------------------------
# Fixtures + fakes
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-driver-runtime")


def _manifest(
    *,
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
    topology_pattern: TopologyPattern = TopologyPattern.SINGLE_THREADED_LINEAR,
    workflow_id: str = "wf-1",
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=engine_class,
        topology_pattern=topology_pattern,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step(idx: int, kind: StepKind = StepKind.INFERENCE_STEP) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"step-{idx}"),
        step_kind=kind,
        step_payload={"index": idx},
    )


class _FakeLedger:
    """In-memory `LedgerWriterLike` substrate for tests."""

    actor: Actor

    def __init__(self, *, fail: bool = False, prior_entries: int = 0) -> None:
        self.actor = _ACTOR
        self.appends: list[tuple[Any, Any]] = []
        self._fail = fail
        self._prior = prior_entries

    def append(self, payload: Any, write_key: Any) -> Any:
        if self._fail:
            raise RuntimeError("simulated ledger append failure")
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return self._prior == 0 and len(self.appends) == 0

    @property
    def entry_count(self) -> int:
        return self._prior + len(self.appends)


class _FakeEmitter:
    """In-memory `LifecycleEventEmitterLike` substrate for tests."""

    def __init__(self) -> None:
        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: WorkflowEventClass) -> None:
        self.emits.append(event_class)


class _FakeCtx:
    """Combined fake `DriverContext`."""

    def __init__(self, *, ledger: _FakeLedger, emitter: _FakeEmitter) -> None:
        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter


class _EchoDispatcher:
    """Step dispatcher that echoes the step payload back."""

    def __init__(self, *, fail_at_step: int | None = None) -> None:
        self.dispatched: list[tuple[StepEffectiveBinding, WorkflowStep]] = []
        self._fail_at = fail_at_step

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep
    ) -> dict[str, Any]:
        if self._fail_at is not None and len(self.dispatched) == self._fail_at:
            raise RuntimeError(f"simulated step failure at index {self._fail_at}")
        self.dispatched.append((binding, step))
        return {"step_id": str(step.step_id), "echoed_payload": dict(step.step_payload)}


def _ctx(*, prior_entries: int = 0) -> tuple[_FakeCtx, _FakeLedger, _FakeEmitter]:
    ledger = _FakeLedger(prior_entries=prior_entries)
    emitter = _FakeEmitter()
    return _FakeCtx(ledger=ledger, emitter=emitter), ledger, emitter


# ---------------------------------------------------------------------------
# AC #1 — Type surface materialized
# ---------------------------------------------------------------------------


def test_run_result_seven_fields() -> None:
    result = RunResult(
        workflow_id="wf",
        run_id="run-1",
        status=RunStatus.SUCCESS,
    )
    field_names = set(type(result).model_fields.keys())
    assert field_names == {
        "workflow_id",
        "run_id",
        "status",
        "terminal_step_index",
        "partial_state",
        "final_state",
        "fail_class",
    }


def test_run_status_four_members() -> None:
    members = {m.name for m in RunStatus}
    assert members == {"SUCCESS", "DRAINED", "FAILED", "PARTIAL"}


def test_step_kind_five_members() -> None:
    members = {m.value for m in StepKind}
    assert members == {
        "declarative-step",
        "inference-step",
        "tool-step",
        "HITL-step",
        "sub-agent-dispatch",
    }


def test_workflow_step_three_fields() -> None:
    step = _step(0)
    field_names = set(type(step).model_fields.keys())
    assert field_names == {"step_id", "step_kind", "step_payload"}


def test_typed_errors_subclass_workflow_driver_error() -> None:
    assert issubclass(TopologyPatternNotYetMaterializedError, WorkflowDriverError)
    assert issubclass(EngineClassNotYetMaterializedError, WorkflowDriverError)


# ---------------------------------------------------------------------------
# AC #2 — Topology + engine-class validation at entry
# ---------------------------------------------------------------------------


def test_topology_pattern_not_yet_materialized_raised_at_non_single_threaded_linear() -> None:
    manifest = _manifest(topology_pattern=TopologyPattern.ORCHESTRATOR_WORKERS)
    ctx, ledger, emitter = _ctx()
    with pytest.raises(TopologyPatternNotYetMaterializedError):
        execute_workflow(
            manifest_entry=manifest,
            steps=[_step(0)],
            run_id="run-1",
            ctx=cast(DriverContext, ctx),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
        )
    assert emitter.emits == []
    assert ledger.appends == []


def test_engine_class_not_yet_materialized_raised_at_out_of_scope_engine_class() -> None:
    manifest = _manifest(engine_class=EngineClass.EVENT_SOURCED_REPLAY)
    ctx, ledger, emitter = _ctx()
    with pytest.raises(EngineClassNotYetMaterializedError):
        execute_workflow(
            manifest_entry=manifest,
            steps=[_step(0)],
            run_id="run-1",
            ctx=cast(DriverContext, ctx),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
        )
    assert emitter.emits == []
    assert ledger.appends == []


def test_validation_failure_emits_no_workflow_start() -> None:
    manifest = _manifest(topology_pattern=TopologyPattern.PARALLELIZATION)
    ctx, _, emitter = _ctx()
    with pytest.raises(TopologyPatternNotYetMaterializedError):
        execute_workflow(
            manifest_entry=manifest,
            steps=[_step(0)],
            run_id="run-1",
            ctx=cast(DriverContext, ctx),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
        )
    assert WorkflowEventClass.WORKFLOW_START not in emitter.emits


# ---------------------------------------------------------------------------
# AC #3 — workflow.start emission post-validation
# ---------------------------------------------------------------------------


def test_workflow_start_emitted_after_validation() -> None:
    ctx, _, emitter = _ctx()
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    assert emitter.emits[0] is WorkflowEventClass.WORKFLOW_START


# ---------------------------------------------------------------------------
# AC #4 — Step iteration loop
# ---------------------------------------------------------------------------


def test_step_iteration_declaration_order() -> None:
    steps = [_step(i) for i in range(3)]
    ctx, _, _ = _ctx()
    dispatcher = _EchoDispatcher()
    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=steps,
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, dispatcher),
    )
    assert result.status is RunStatus.SUCCESS
    dispatched_step_ids = [str(s.step_id) for _, s in dispatcher.dispatched]
    assert dispatched_step_ids == ["step-0", "step-1", "step-2"]


def test_per_step_step_boundary_emitted() -> None:
    ctx, _, emitter = _ctx()
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    step_boundaries = [e for e in emitter.emits if e is WorkflowEventClass.STEP_BOUNDARY]
    assert len(step_boundaries) == 3


def test_state_ledger_append_per_step() -> None:
    ctx, ledger, _ = _ctx()
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    assert len(ledger.appends) == 3


def test_step_idempotency_key_deterministic() -> None:
    # Two runs with identical inputs produce identical per-step idempotency keys.
    keys_run_a: list[str] = []
    keys_run_b: list[str] = []
    for accumulator in (keys_run_a, keys_run_b):
        ctx, ledger, _ = _ctx()
        execute_workflow(
            manifest_entry=_manifest(),
            steps=[_step(0), _step(1)],
            run_id="run-deterministic",
            ctx=cast(DriverContext, ctx),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
        )
        for payload, _ in ledger.appends:
            accumulator.append(str(payload.idempotency_key))
    assert keys_run_a == keys_run_b
    assert len(set(keys_run_a)) == 2  # each step has a distinct key


# ---------------------------------------------------------------------------
# AC #5 — Lifecycle event filter (single-threaded-linear)
# ---------------------------------------------------------------------------


def test_lifecycle_events_in_happy_path() -> None:
    """Happy path emits exactly: workflow.start + N step.boundary."""
    ctx, _, emitter = _ctx()
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    expected = [
        WorkflowEventClass.WORKFLOW_START,
        WorkflowEventClass.STEP_BOUNDARY,
        WorkflowEventClass.STEP_BOUNDARY,
    ]
    assert emitter.emits == expected


def test_no_terminal_lifecycle_event_at_success() -> None:
    """No new event class at terminal exit (per §25.3.4 + §25.5 strict
    composition against §5.1 closed-at-8 taxonomy).
    """
    ctx, _, emitter = _ctx()
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    # Last emit is the per-step step.boundary; no terminal sentinel.
    assert emitter.emits[-1] is WorkflowEventClass.STEP_BOUNDARY


# ---------------------------------------------------------------------------
# AC #6 — Replay-resumption read at re-entry
# ---------------------------------------------------------------------------


def test_resumption_emit_shape_wired_for_save_point_checkpoint() -> None:
    """RESUMPTION emit *shape* is wired (not full AC #6 — see partial-land below).

    **PARTIAL-LAND scope.** This test verifies that a save-point-checkpoint
    binding entering a non-genesis ledger emits RESUMPTION in the lifecycle
    stream. It does NOT verify:
    - Prefix match against `run_idempotency_key` (AC #6 step 2 — STRUCK at
      partial land per `.harness/class_1_tension_u_cp_56_resumption_underspec.md`)
    - Step skip + resume-at-first-unmaterialized (AC #6 step 4 — STRUCK)
    - Selective RESUMPTION based on prior-run match (any prior entry triggers
      RESUMPTION at the weaker shipped behavior)

    The weaker behavior is intentional at U-CP-56 PARTIAL-LAND pending the
    Class 1 fork resolution (`WorkflowManifestEntry` extension with
    `entry_version` field + per-run prefix-match read primitive).
    """
    ctx, _, emitter = _ctx(prior_entries=3)  # non-genesis ledger
    execute_workflow(
        manifest_entry=_manifest(engine_class=EngineClass.SAVE_POINT_CHECKPOINT),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    assert WorkflowEventClass.RESUMPTION in emitter.emits
    # RESUMPTION precedes WORKFLOW_START in emission order.
    resumption_idx = emitter.emits.index(WorkflowEventClass.RESUMPTION)
    start_idx = emitter.emits.index(WorkflowEventClass.WORKFLOW_START)
    assert resumption_idx < start_idx


def test_no_resumption_emission_under_pure_pattern_no_engine() -> None:
    """Under pure-pattern-no-engine, no RESUMPTION is emitted at entry
    regardless of ledger state (state-ledger native dedup per §8.2 row 3
    handles dedup at per-step idempotency_key).
    """
    ctx, _, emitter = _ctx(prior_entries=5)  # non-genesis ledger
    execute_workflow(
        manifest_entry=_manifest(engine_class=EngineClass.PURE_PATTERN_NO_ENGINE),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    assert WorkflowEventClass.RESUMPTION not in emitter.emits


# ---------------------------------------------------------------------------
# AC #7 — Terminal SUCCESS return
# ---------------------------------------------------------------------------


def test_terminal_success_return_shape() -> None:
    ctx, _, _ = _ctx()
    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    assert result.status is RunStatus.SUCCESS
    assert result.terminal_step_index is None
    assert result.partial_state is None
    assert result.fail_class is None
    assert result.final_state is not None
    # final_state aggregates step outputs keyed by step_id.
    assert set(result.final_state.keys()) == {"step-0", "step-1"}


# ---------------------------------------------------------------------------
# AC #8 — Failure-mode taxonomy
# ---------------------------------------------------------------------------


def test_step_failure_returns_failed_status() -> None:
    ctx, _, _ = _ctx()
    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher(fail_at_step=1)),
    )
    assert result.status is RunStatus.FAILED
    assert result.terminal_step_index == 1
    assert result.partial_state is not None
    assert "step-0" in result.partial_state
    assert "step-1" not in result.partial_state  # failed step not in partial
    assert result.fail_class is not None
    assert result.fail_class.startswith("step-failure")


def test_ledger_append_failure_returns_failed_status() -> None:
    failing_ledger = _FakeLedger(fail=True)
    emitter = _FakeEmitter()
    ctx = _FakeCtx(ledger=failing_ledger, emitter=emitter)
    result = execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatcher=cast(StepDispatcher, _EchoDispatcher()),
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert result.fail_class.startswith("ledger-append-failed")


# ---------------------------------------------------------------------------
# AC #9 — Determinism
# ---------------------------------------------------------------------------


def test_driver_iteration_deterministic_given_inputs() -> None:
    """Two runs with identical inputs produce identical observable results:
    same emission sequence, same dispatched step order, same final_state keys.
    """
    runs: list[tuple[tuple[WorkflowEventClass, ...], tuple[str, ...], tuple[str, ...]]] = []
    for _ in range(2):
        ctx, _, emitter = _ctx()
        dispatcher = _EchoDispatcher()
        result = execute_workflow(
            manifest_entry=_manifest(),
            steps=[_step(0), _step(1)],
            run_id="run-deterministic",
            ctx=cast(DriverContext, ctx),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatcher=cast(StepDispatcher, dispatcher),
        )
        runs.append(
            (
                tuple(emitter.emits),
                tuple(str(s.step_id) for _, s in dispatcher.dispatched),
                tuple(sorted((result.final_state or {}).keys())),
            )
        )
    assert runs[0] == runs[1]

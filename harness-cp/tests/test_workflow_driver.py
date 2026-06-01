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
    _append_step_ledger_entry,
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
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

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


class _FakeLedgerReader:
    """In-memory `LedgerReaderLike` substrate for tests (v2.12).

    Holds a mapping `idempotency_key → entries_count` simulating ledger
    contents. `read_by_idempotency_key` returns a stub `ReadResult`-shaped
    object whose `entries` is a tuple of dummies sized to the count.
    """

    def __init__(self, materialized_keys: dict[str, int] | None = None) -> None:
        self._keys = materialized_keys or {}

    def read_by_idempotency_key(self, idempotency_key: Any, bounded_window: Any) -> Any:
        _ = bounded_window
        # The driver passes Identifier(hex_string); compare on str form.
        count = self._keys.get(str(idempotency_key), 0)

        class _Result:
            def __init__(self, n: int) -> None:
                self.entries = tuple(object() for _ in range(n))
                self.truncated = False
                self.next_position = None

        return _Result(count)


class _FakeCtx:
    """Combined fake `DriverContext`.

    `drained_flag` defaults to a fresh never-set `asyncio.Event` so U-CP-56
    happy-path tests don't trigger drain. U-CP-57 drain tests explicitly set
    the flag at the relevant boundary site.
    """

    def __init__(
        self,
        *,
        ledger: _FakeLedger,
        emitter: _FakeEmitter,
        drained_flag: asyncio.Event | None = None,
        ledger_reader: _FakeLedgerReader | None = None,
        tracer_provider: object | None = None,
        validator_framework: object | None = None,
        pause_resume_protocol: object | None = None,
        pause_requested_flag: asyncio.Event | None = None,
        tenant_id: str | None = None,
    ) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = drained_flag if drained_flag is not None else asyncio.Event()
        # U-RT-87 (v2.20) — pause_resume_protocol + pause_requested_flag fields
        # per runtime spec v1.21 §4 + §14.14.3 DriverContext Protocol extension.
        self.pause_resume_protocol = pause_resume_protocol
        self.pause_requested_flag = (
            pause_requested_flag if pause_requested_flag is not None else asyncio.Event()
        )
        self.ledger_reader = ledger_reader if ledger_reader is not None else _FakeLedgerReader()
        # U-OD-35 — DriverContext requires tracer_provider per C-OD-25 §25.2.
        # Default to NoOpTracerProvider so happy-path tests don't assert span
        # observables; envelope-specific tests live in test_workflow_driver_envelope.py.
        self.tracer_provider = (
            tracer_provider if tracer_provider is not None else NoOpTracerProvider()
        )
        # U-CP-61 — optional ValidatorFramework binding; default None (skip hook).
        self.validator_framework = validator_framework
        # tenant_id binding lift — DriverContext.tenant_id surfaced from
        # HarnessContext.tenant_id (which reads RuntimeConfig.tenant_id).
        # Default None preserves single-tenant behavior for happy-path tests.
        self.tenant_id = tenant_id


class _SingleKindRegistry:
    """Minimal test `StepDispatcherRegistry` impl — binds one (kind, dispatcher).

    Concrete impl for the v1.6 routing-layer refactor per C-RT-17 §14.7.7.
    The production `StepKindDispatcherRegistry` lives in `harness_runtime`;
    CP tests use this inline impl to avoid the CP→runtime dependency
    direction. Lookup of an unbound kind raises
    `StepKindDispatcherNotBoundError` (same shape as the production impl).
    """

    def __init__(self, kind: StepKind, dispatcher: StepDispatcher) -> None:
        self._kind = kind
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind != self._kind:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    """Compose a single-kind INFERENCE_STEP registry for legacy tests.

    Pre-U-RT-59 tests passed a single dispatcher; post-refactor the driver
    requires a `StepDispatcherRegistry`. This helper wraps a dispatcher
    in a minimal one-entry registry bound to INFERENCE_STEP (the default
    `_step(...)` fixture's step_kind).
    """
    return cast(StepDispatcherRegistry, _SingleKindRegistry(StepKind.INFERENCE_STEP, dispatcher))


class _EchoDispatcher:
    """Step dispatcher that echoes the step payload back."""

    def __init__(self, *, fail_at_step: int | None = None) -> None:
        self.dispatched: list[tuple[StepEffectiveBinding, WorkflowStep]] = []
        self._fail_at = fail_at_step

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        # `step_context` accepted at v1.6 Path A per amended StepDispatcher
        # Protocol (C-RT-17 resolution); echo dispatcher does not consume.
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


def test_run_result_eight_fields() -> None:
    """8-field RunResult per C-CP-25 §25.2 + v1.21 §14.14.5 invariant 4
    additive `pause_snapshot` field (U-RT-89)."""
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
        "pause_snapshot",
    }


def test_run_status_five_members() -> None:
    """5-member RunStatus per C-CP-25 §25.2 + v1.21 §14.14.5 invariant 4
    additive `PAUSED` value (U-RT-89)."""
    members = {m.name for m in RunStatus}
    assert members == {"SUCCESS", "DRAINED", "FAILED", "PARTIAL", "PAUSED"}


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
            step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
            step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
            step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
            step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
    )
    # Last emit is the per-step step.boundary; no terminal sentinel.
    assert emitter.emits[-1] is WorkflowEventClass.STEP_BOUNDARY


# ---------------------------------------------------------------------------
# AC #6 — Replay-resumption read at re-entry
# ---------------------------------------------------------------------------


def _expected_step_key(run_id: str, workflow_id: str, entry_version: int, step_index: int) -> str:
    """Compute the expected step idempotency_key per §25.6, for test setup."""
    import hashlib

    run_h = hashlib.sha256()
    run_h.update(run_id.encode("utf-8"))
    run_h.update(b"\x00")
    run_h.update(workflow_id.encode("utf-8"))
    run_h.update(b"\x00")
    run_h.update(str(entry_version).encode("utf-8"))
    run_key = run_h.hexdigest()

    step_h = hashlib.sha256()
    step_h.update(run_key.encode("utf-8"))
    step_h.update(b"\x00")
    step_h.update(str(step_index).encode("utf-8"))
    return step_h.hexdigest()


def test_workflow_resumption_emitted_on_save_point_checkpoint_reentry() -> None:
    """v2.12 (un-strike of AC #6) — RESUMPTION emit is *selective* per run.

    Materializes prior step entries matching `run-1`'s expected keys; driver
    detects them, advances resume_at over the contiguous prefix, and emits
    RESUMPTION.
    """
    manifest = _manifest(engine_class=EngineClass.SAVE_POINT_CHECKPOINT)
    # Materialize ledger entries for steps 0 and 1 of this run.
    materialized = {
        _expected_step_key("run-1", "wf-1", 1, 0): 1,
        _expected_step_key("run-1", "wf-1", 1, 1): 1,
    }
    ledger = _FakeLedger(prior_entries=2)
    emitter = _FakeEmitter()
    ctx = _FakeCtx(ledger=ledger, emitter=emitter, ledger_reader=_FakeLedgerReader(materialized))
    dispatcher = _EchoDispatcher()
    execute_workflow(
        manifest_entry=manifest,
        steps=[_step(0), _step(1), _step(2)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
    )
    # RESUMPTION emitted before WORKFLOW_START.
    assert WorkflowEventClass.RESUMPTION in emitter.emits
    resumption_idx = emitter.emits.index(WorkflowEventClass.RESUMPTION)
    start_idx = emitter.emits.index(WorkflowEventClass.WORKFLOW_START)
    assert resumption_idx < start_idx
    # Only step 2 dispatched (steps 0 + 1 already in ledger).
    assert len(dispatcher.dispatched) == 1
    assert str(dispatcher.dispatched[0][1].step_id) == "step-2"


def test_resumption_not_emitted_for_unrelated_prior_run() -> None:
    """v2.12 — prior ledger entries from a different run produce no RESUMPTION.

    Even with non-genesis ledger, if the expected step keys for THIS run
    return zero matches, the driver treats this as a genesis run for the
    purpose of resumption.
    """
    manifest = _manifest(engine_class=EngineClass.SAVE_POINT_CHECKPOINT)
    # Materialize ledger entries for an unrelated run (run-OTHER).
    materialized = {
        _expected_step_key("run-OTHER", "wf-1", 1, 0): 1,
        _expected_step_key("run-OTHER", "wf-1", 1, 1): 1,
    }
    ledger = _FakeLedger(prior_entries=2)
    emitter = _FakeEmitter()
    ctx = _FakeCtx(ledger=ledger, emitter=emitter, ledger_reader=_FakeLedgerReader(materialized))
    dispatcher = _EchoDispatcher()
    execute_workflow(
        manifest_entry=manifest,
        steps=[_step(0), _step(1)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
    )
    assert WorkflowEventClass.RESUMPTION not in emitter.emits
    # All steps dispatched; resume_at == 0.
    assert len(dispatcher.dispatched) == 2


def test_resumption_skips_already_replayed_steps() -> None:
    """v2.12 — driver resumes at first unmaterialized step; prior dispatched skip."""
    manifest = _manifest(engine_class=EngineClass.SAVE_POINT_CHECKPOINT)
    materialized = {
        _expected_step_key("run-1", "wf-1", 1, 0): 1,
        _expected_step_key("run-1", "wf-1", 1, 1): 1,
        _expected_step_key("run-1", "wf-1", 1, 2): 1,
    }
    ledger = _FakeLedger(prior_entries=3)
    emitter = _FakeEmitter()
    ctx = _FakeCtx(ledger=ledger, emitter=emitter, ledger_reader=_FakeLedgerReader(materialized))
    dispatcher = _EchoDispatcher()
    execute_workflow(
        manifest_entry=manifest,
        steps=[_step(0), _step(1), _step(2), _step(3), _step(4)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
    )
    # Only steps 3 + 4 dispatched.
    assert len(dispatcher.dispatched) == 2
    dispatched_ids = {str(d[1].step_id) for d in dispatcher.dispatched}
    assert dispatched_ids == {"step-3", "step-4"}


def test_resume_at_advances_over_contiguous_prefix_only() -> None:
    """v2.12 — gap behavior: contiguous prefix only, gap-fill out of scope."""
    manifest = _manifest(engine_class=EngineClass.SAVE_POINT_CHECKPOINT)
    # Materialize step 0 + step 2, gap at step 1.
    materialized = {
        _expected_step_key("run-1", "wf-1", 1, 0): 1,
        # step 1 intentionally missing
        _expected_step_key("run-1", "wf-1", 1, 2): 1,
    }
    ledger = _FakeLedger(prior_entries=2)
    emitter = _FakeEmitter()
    ctx = _FakeCtx(ledger=ledger, emitter=emitter, ledger_reader=_FakeLedgerReader(materialized))
    dispatcher = _EchoDispatcher()
    execute_workflow(
        manifest_entry=manifest,
        steps=[_step(0), _step(1), _step(2)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
    )
    # resume_at advances to 1 (only step 0 is contiguous-prefix-materialized);
    # step 1 + step 2 dispatch.
    assert len(dispatcher.dispatched) == 2
    dispatched_ids = [str(d[1].step_id) for d in dispatcher.dispatched]
    assert dispatched_ids == ["step-1", "step-2"]


def test_entry_version_changes_idempotency_key_basis() -> None:
    """v2.12 — bumping entry_version invalidates prior-run resumption substrate.

    Prior run was at entry_version=1; this run is at entry_version=2 — the
    computed expected step keys differ → zero matches → no RESUMPTION.
    """
    manifest_v2 = _manifest(engine_class=EngineClass.SAVE_POINT_CHECKPOINT)
    # Construct a manifest with entry_version=2 by re-building from defaults.
    manifest_v2 = WorkflowManifestEntry(
        workflow_id=manifest_v2.workflow_id,
        workload_class=manifest_v2.workload_class,
        persona_tier=manifest_v2.persona_tier,
        engine_class=manifest_v2.engine_class,
        topology_pattern=manifest_v2.topology_pattern,
        layer_budgets=manifest_v2.layer_budgets,
        fallback_chain=manifest_v2.fallback_chain,
        hitl_placements=manifest_v2.hitl_placements,
        per_step_overrides=manifest_v2.per_step_overrides,
        entry_version=2,
    )
    # Materialize prior-version (1) step keys.
    materialized = {
        _expected_step_key("run-1", "wf-1", 1, 0): 1,
    }
    ledger = _FakeLedger(prior_entries=1)
    emitter = _FakeEmitter()
    ctx = _FakeCtx(ledger=ledger, emitter=emitter, ledger_reader=_FakeLedgerReader(materialized))
    dispatcher = _EchoDispatcher()
    execute_workflow(
        manifest_entry=manifest_v2,
        steps=[_step(0)],
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
    )
    # v2-keyed expected key differs from v1-stored key → no match → no RESUMPTION.
    assert WorkflowEventClass.RESUMPTION not in emitter.emits
    assert len(dispatcher.dispatched) == 1


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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher(fail_at_step=1))),
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
        step_dispatchers=_registry(cast(StepDispatcher, _EchoDispatcher())),
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
            step_dispatchers=_registry(cast(StepDispatcher, dispatcher)),
        )
        runs.append(
            (
                tuple(emitter.emits),
                tuple(str(s.step_id) for _, s in dispatcher.dispatched),
                tuple(sorted((result.final_state or {}).keys())),
            )
        )
    assert runs[0] == runs[1]


# ---------------------------------------------------------------------------
# Tenant-id binding lift — driver reads ctx.tenant_id at StepExecutionContext
# composition site (replacing the v1.6 MVP hardcoded None). Per workflow_
# driver_types.py deferral comment: this is the v1.7+ extension that lifts
# the hardcode as a binding fix (per-deployment scoping via RuntimeConfig,
# not a per-workflow WorkflowManifestEntry schema extension like CP-19's
# default_gate_level at CP spec v1.20 §6.1.Y).
# ---------------------------------------------------------------------------


class _TenantIdProbeDispatcher:
    """Records `step_context.tenant_id` observed at each dispatch."""

    def __init__(self) -> None:
        self.observed: list[str | None] = []

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        self.observed.append(getattr(step_context, "tenant_id", "<missing>"))
        return {"step_id": str(step.step_id), "echoed_payload": dict(step.step_payload)}


def _run_and_capture_tenant_id(*, tenant_id: str | None) -> str | None:
    ctx, _, _ = _ctx()
    ctx.tenant_id = tenant_id  # override default None set at _FakeCtx.__init__
    probe = _TenantIdProbeDispatcher()
    execute_workflow(
        manifest_entry=_manifest(),
        steps=[_step(0)],
        run_id="run-tenant-test",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, probe)),
    )
    assert len(probe.observed) == 1
    return probe.observed[0]


def test_tenant_id_none_propagates_to_step_context() -> None:
    """Single-tenant (default): ctx.tenant_id=None → step_context.tenant_id=None."""
    assert _run_and_capture_tenant_id(tenant_id=None) is None


def test_tenant_id_non_none_propagates_to_step_context() -> None:
    """Multi-tenant: ctx.tenant_id='acme' → step_context.tenant_id='acme'."""
    assert _run_and_capture_tenant_id(tenant_id="acme") == "acme"


def test_tenant_id_empty_string_propagates_verbatim() -> None:
    """Empty-string tenant is NOT coerced at driver layer.

    Coercion (if any) is audit-writer's concern per `_tenant_tag` (which
    treats falsy as single-tenant sentinel). The driver propagates verbatim.
    """
    assert _run_and_capture_tenant_id(tenant_id="") == ""


def test_driver_context_protocol_declares_tenant_id() -> None:
    """DriverContext Protocol must declare tenant_id (structural typing check).

    HarnessContext satisfies the Protocol via a `@computed_field` property
    reading `self.config.tenant_id`; test fixtures (_FakeCtx) bind it as a
    plain instance attribute. Both shapes match structurally.
    """
    assert "tenant_id" in DriverContext.__annotations__, (
        "DriverContext.tenant_id must be declared so HarnessContext can "
        "structurally satisfy the protocol via the computed property."
    )


def test_driver_context_protocol_declares_procedural_tier_snapshot_resolver() -> None:
    """R-003 — DriverContext must declare the resolver field so HarnessContext
    structurally satisfies it (bound at bootstrap stage 6)."""
    assert "procedural_tier_snapshot_resolver" in DriverContext.__annotations__


class _LedgerOnlyCtx:
    """Minimal DriverContext shape for `_append_step_ledger_entry` (it reads
    only `ledger_writer` + `procedural_tier_snapshot_resolver`)."""

    def __init__(self, ledger: _FakeLedger, resolver: Any) -> None:
        self.ledger_writer = ledger
        self.procedural_tier_snapshot_resolver = resolver


def test_append_step_ledger_entry_populates_procedural_tier_snapshot_ref() -> None:
    """R-003 — the per-step state-ledger write (§25.3.3.7, workflow-context)
    populates the sidecar via the bound resolver per IS spec v1.3 §C-IS-05 §5.1."""
    ledger = _FakeLedger()
    ctx = _LedgerOnlyCtx(ledger, lambda: Identifier("b" * 64))
    _append_step_ledger_entry(
        ctx=cast(DriverContext, ctx),
        workflow_id="wf-1",
        step_index=0,
        step_idempotency_key="idem-0",
        step_output={"ok": True},
    )
    [(payload, _key)] = ledger.appends
    assert payload.procedural_tier_snapshot_ref == Identifier("b" * 64)


def test_append_step_ledger_entry_none_when_resolver_absent() -> None:
    """R-003 — when no resolver is bound (operator opt-out / test ctx), the
    sidecar stays None (the getattr-defensive opt-out path)."""
    ledger = _FakeLedger()
    ctx = _LedgerOnlyCtx(ledger, None)
    _append_step_ledger_entry(
        ctx=cast(DriverContext, ctx),
        workflow_id="wf-1",
        step_index=0,
        step_idempotency_key="idem-0",
        step_output={"ok": True},
    )
    [(payload, _key)] = ledger.appends
    assert payload.procedural_tier_snapshot_ref is None

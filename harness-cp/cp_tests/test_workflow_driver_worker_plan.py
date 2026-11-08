"""CP v1.130 §25.11.1 — lead-directed worker plan, driver-level witnesses.

Each test drives the public `execute_workflow` entry with recording dispatchers and names the
§2 witness it discharges and the mutant it kills. The pure parser legs (W1-W5 derivation, W10
manifest validation, the W6c snapshot leg) live in `test_worker_plan.py`; Runtime's reader legs
(RW1/RW2) live in `harness-runtime/tests/test_lifecycle_sub_agent_dispatch.py`.

Authority: `design-substrate/Spec_Control_Plane_v1_130.md` §25.11.1 + §2 witness table.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol_types import (
    FanOutBranchResumeState,
    FanOutResumeState,
    PauseSnapshot,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_brief import (
    ClearTaskBoundaries,
    OutputSchema,
    OutputSchemaKind,
    SubAgentBrief,
    compute_brief_summary_hash,
)
from harness_cp.topology_pattern import TopologyPattern, WorkerSelection
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
    execute_workflow_at_depth,
)
from harness_cp.workflow_driver_types import RunStatus, StepExecutionContext, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import FanoutTimeoutDisposition, WorkflowManifestEntry

from .test_workflow_driver_fanout_output_replay_full_chain import (
    _Ctx as _StoreCtx,
)
from .test_workflow_driver_fanout_output_replay_full_chain import (
    _InMemoryBranchStore,
    _pause_protocol,
)
from .test_workflow_driver_fanout_pause import (
    _CHAIN,
    _DEFAULT_BINDING,
    _captured_snapshot,
    _CtxP,
    _Emitter,
    _RecordingLedger,
    _synthesis_step,
)

LEAD = WorkerSelection.LEAD_PLAN
POOL = WorkerSelection.DECLARED_POOL
_SOLO = PersonaTier.SOLO_DEVELOPER  # cascade_policy = proceed
_TEAM = PersonaTier.TEAM_BINDING  # cascade_policy = pause
_WF = "wf-fp"  # `_captured_snapshot`'s workflow id


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _manifest(
    selection: WorkerSelection,
    *,
    tier: PersonaTier = _SOLO,
    engine: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
    topology: TopologyPattern = TopologyPattern.ORCHESTRATOR_WORKERS,
    workflow_id: str = _WF,
    timeout: FanoutTimeoutDisposition = FanoutTimeoutDisposition.FAIL_CLOSED,
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=tier,
        engine_class=engine,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
        fanout_timeout_disposition=timeout,
        worker_selection=selection,
    )


def _brief(objective: str) -> SubAgentBrief:
    unhashed = SubAgentBrief(
        objective=objective,
        output_format=OutputSchema(schema_kind=OutputSchemaKind.FREE_TEXT),
        guidance="g",
        task_boundaries=ClearTaskBoundaries(
            in_scope=("a",), out_of_scope=("b",), termination_criteria=("c",)
        ),
        summary_hash="",
    )
    return unhashed.model_copy(update={"summary_hash": compute_brief_summary_hash(unhashed)})


def _plan_brief(objective: str) -> dict[str, Any]:
    """A plan entry's `brief`: the four §13.2 fields, no `summary_hash` (§25.11.1.3(3))."""
    return _brief(objective).model_dump(mode="json", exclude={"summary_hash"})


def _orch(output: Mapping[str, Any]) -> WorkflowStep:
    """The orchestrator; the dispatcher returns `output` as its result."""
    return WorkflowStep(
        step_id=StepID("orch"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={"out": output}
    )


def _leaf(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name), step_kind=StepKind.DECLARATIVE_STEP, step_payload={"name": name}
    )


def _sub(name: str, declared_objective: str = "declared") -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={
            "child_workflow_id": f"wf-{name}",
            "brief": _brief(declared_objective).model_dump(mode="json"),
        },
    )


def _plan(*entries: str | tuple[str, str]) -> dict[str, Any]:
    """An orchestrator output carrying `worker_plan`; a tuple entry adds a lead brief."""
    return {
        "worker_plan": [
            {"worker": e} if isinstance(e, str) else {"worker": e[0], "brief": _plan_brief(e[1])}
            for e in entries
        ]
    }


class _PlanDispatcher:
    """Orchestrators return their `out` payload; workers echo `{"worker": id}` and record their
    `StepExecutionContext`. A worker in `fail` raises after every worker in `gate` completed
    (event sync, no sleeps). A `child_manifest` payload recurses one level (HIERARCHICAL)."""

    def __init__(
        self,
        *,
        fail: frozenset[str] = frozenset(),
        gate: frozenset[str] = frozenset(),
        ctx: DriverContext | None = None,
    ) -> None:
        self.calls: list[str] = []
        self.contexts: dict[str, StepExecutionContext] = {}
        self._fail = fail
        self._done = {name: threading.Event() for name in gate}
        self._lock = threading.Lock()
        self.ctx = ctx
        self.registry: StepDispatcherRegistry | None = None

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        with self._lock:
            self.calls.append(step_id)
            self.contexts[step_id] = step_context
        if "out" in step.step_payload:
            return dict(step.step_payload["out"])
        if "child_manifest" in step.step_payload:
            assert self.ctx is not None and self.registry is not None
            child = execute_workflow_at_depth(
                step.step_payload["child_manifest"],
                step.step_payload["child_steps"],
                run_id=f"child-{step_id}",
                ctx=self.ctx,
                default_model_binding=_DEFAULT_BINDING,
                step_dispatchers=self.registry,
                parent_gate_floor=step_context.parent_gate_level,
                descent_depth=1,
            )
            assert child.status is RunStatus.SUCCESS, child.fail_class
            return dict(child.final_state or {})
        if step_id in self._fail:
            for name, event in self._done.items():
                assert event.wait(timeout=10.0), f"{name} never completed"
            raise RuntimeError(f"simulated worker failure at {step_id}")
        if step_id in self._done:
            self._done[step_id].set()
        return {"worker": step_id}

    def worker_calls(self) -> list[str]:
        return [c for c in self.calls if c != "orch"]


class _Registry:
    def __init__(self, dispatcher: _PlanDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind in (StepKind.DECLARATIVE_STEP, StepKind.SUB_AGENT_DISPATCH):
            return cast(StepDispatcher, self._dispatcher)
        raise StepKindDispatcherNotBoundError(step_kind)


def _run(
    manifest: WorkflowManifestEntry,
    steps: list[WorkflowStep],
    dispatcher: _PlanDispatcher,
    ctx: Any,
    **kwargs: Any,
) -> Any:
    registry = cast(StepDispatcherRegistry, _Registry(dispatcher))
    dispatcher.registry = registry
    return execute_workflow(
        manifest,
        steps,
        run_id="run-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
        **kwargs,
    )


def _pause_ctx() -> Any:
    return _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())


def _store_ctx(store: _InMemoryBranchStore, ledger: Any = None) -> Any:
    return _StoreCtx(
        ledger=ledger if ledger is not None else _RecordingLedger(),
        store=store,
        pause_resume_protocol=_pause_protocol(),
    )


def _store_run(
    selection: WorkerSelection,
    steps: list[WorkflowStep],
    store: _InMemoryBranchStore,
    *,
    dispatcher: _PlanDispatcher | None = None,
    tier: PersonaTier = _SOLO,
    timeout: FanoutTimeoutDisposition = FanoutTimeoutDisposition.FAIL_CLOSED,
    ledger: Any = None,
) -> tuple[Any, _PlanDispatcher]:
    dispatcher = dispatcher if dispatcher is not None else _PlanDispatcher()
    manifest = _manifest(
        selection, tier=tier, engine=EngineClass.EVENT_SOURCED_REPLAY, timeout=timeout
    )
    return _run(manifest, steps, dispatcher, _store_ctx(store, ledger)), dispatcher


def _branch_entries(ledger: _RecordingLedger) -> list[Any]:
    return [payload for payload, _wk in ledger.appends if payload.branch_metadata is not None]


# ---------------------------------------------------------------------------
# W1 / W2 / W3 — fresh dispatch
# ---------------------------------------------------------------------------


def test_w1_declared_pool_ignores_a_worker_plan_key() -> None:
    """W1 — kills: reading `worker_plan` regardless of selection (a key-presence mode)."""
    steps = [_orch(_plan("c")), _leaf("a"), _leaf("b"), _leaf("c")]
    dispatcher = _PlanDispatcher()
    result = _run(_manifest(POOL), steps, dispatcher, _pause_ctx())

    assert result.status is RunStatus.SUCCESS
    assert sorted(dispatcher.worker_calls()) == ["a", "b", "c"]
    assert list(result.final_state["worker_outputs"]) == ["a", "b", "c"]
    assert {w: dispatcher.contexts[w].step_index for w in "abc"} == {"a": 1, "b": 2, "c": 3}
    assert all(dispatcher.contexts[w].lead_brief is None for w in "abc")


def test_w2_lead_plan_selects_orders_and_keeps_declared_step_index() -> None:
    """W2 — kills: `worker_steps = steps[1:]` retained; `step_index = branch_index + 1`."""
    store = _InMemoryBranchStore()
    ledger = _RecordingLedger()
    steps = [_orch(_plan("c", "a")), _leaf("a"), _leaf("b"), _leaf("c")]
    result, dispatcher = _store_run(LEAD, steps, store, tier=_TEAM, ledger=ledger)

    assert result.status is RunStatus.SUCCESS
    assert list(result.final_state["worker_outputs"]) == ["c", "a"]  # branch ordinals 0, 1
    assert "b" not in dispatcher.calls
    # c keeps declared index 3, a keeps 1 — the key per-step policy / skill activation read.
    assert dispatcher.contexts["c"].step_index == 3
    assert dispatcher.contexts["a"].step_index == 1
    assert dispatcher.contexts["c"].branch_index == 0
    assert dispatcher.contexts["a"].branch_index == 1
    key = store.sole_run_key()
    assert store.dispatched_branch_step_ids(key) == {0: "c", 1: "a"}  # no marker for b
    assert {e.branch_metadata.branch_index for e in _branch_entries(ledger)} == {0, 1}  # none for b


def test_w3_lead_brief_reaches_the_worker_context_with_computed_hash() -> None:
    """W3 (CP leg) — the planned brief is carried hash-inert on the worker's context with
    `summary_hash = compute_brief_summary_hash`; a supplied hash is refused. Kills: the parser
    trusting a supplied hash. Runtime's three readers are RW1/RW2."""
    steps = [_orch(_plan(("s", "lead objective"))), _sub("s")]
    dispatcher = _PlanDispatcher()
    result = _run(_manifest(LEAD), steps, dispatcher, _pause_ctx())

    assert result.status is RunStatus.SUCCESS
    lead_brief = dispatcher.contexts["s"].lead_brief
    assert lead_brief == _brief("lead objective")
    assert lead_brief.summary_hash == compute_brief_summary_hash(lead_brief)
    assert "lead_brief" not in dispatcher.contexts["s"].model_dump()

    forged = {"worker_plan": [{"worker": "s", "brief": {**_plan_brief("x"), "summary_hash": "f"}}]}
    refused = _run(_manifest(LEAD), [_orch(forged), _sub("s")], _PlanDispatcher(), _pause_ctx())
    assert refused.fail_class == "orchestrator-workers-plan-invalid: malformed-brief:s"


# ---------------------------------------------------------------------------
# W4 / W5 — invalid and empty plans
# ---------------------------------------------------------------------------

_POOL = [_leaf("a"), _leaf("b"), _leaf("c"), _sub("s")]


@pytest.mark.parametrize(
    ("output", "reason"),
    [
        ({}, "missing-worker-plan"),
        ({"worker_plan": "c"}, "not-a-sequence"),
        ({"worker_plan": ["c"]}, "not-a-sequence"),
        ({"worker_plan": [{"worker": "c", "extra": 1}]}, "malformed-assignment"),
        ({"worker_plan": [{"worker": 3}]}, "malformed-assignment"),
        (_plan("orch"), "unknown-worker:orch"),
        (_plan("synthesis"), "unknown-worker:synthesis"),
        (_plan("a", "a"), "duplicate-worker:a"),
        (_plan("s"), "missing-brief:s"),
        (_plan(("a", "x")), "brief-on-non-subagent:a"),
        ({"worker_plan": [{"worker": "s", "brief": {"objective": 1}}]}, "malformed-brief:s"),
    ],
)
def test_w4_invalid_plan_fails_before_any_worker_dispatch_or_marker(
    output: dict[str, Any], reason: str
) -> None:
    """W4 — kills: silently skipping an invalid entry; falling back to the declared pool. The
    carved synthesis step id is not a pool member."""
    store = _InMemoryBranchStore()
    ledger = _RecordingLedger()
    steps = [_orch(output), *_POOL, _synthesis_step()]
    result, dispatcher = _store_run(LEAD, steps, store, tier=_TEAM, ledger=ledger)

    assert result.status is RunStatus.FAILED
    assert result.fail_class == f"orchestrator-workers-plan-invalid: {reason}"
    assert dispatcher.calls == ["orch"]
    key = store.sole_run_key()
    assert store.orchestrator_present(key)  # the orchestrator's replay record is kept
    assert len(ledger.appends) == 1 and _branch_entries(ledger) == []  # its ledger entry is kept
    assert store.present_dispatched_indexes(key) == set()
    assert not store.fanout_cardinality_present(key)


def test_w5_empty_plan_succeeds_and_synthesis_refuses_zero_siblings() -> None:
    """W5 — kills: an empty plan treated as invalid, or as "all workers"."""
    dispatcher = _PlanDispatcher()
    output = _plan()
    result = _run(_manifest(LEAD), [_orch(output), _leaf("a")], dispatcher, _pause_ctx())
    assert result.status is RunStatus.SUCCESS
    assert result.final_state == {"orchestrator": output, "worker_outputs": {}}
    assert dispatcher.calls == ["orch"]

    with_synthesis = _run(
        _manifest(LEAD),
        [_orch(output), _leaf("a"), _synthesis_step()],
        _PlanDispatcher(),
        _pause_ctx(),
    )
    assert with_synthesis.status is RunStatus.FAILED
    assert (with_synthesis.fail_class or "").startswith("post-join-synthesis-no-siblings")


# ---------------------------------------------------------------------------
# W6 / W6b / W6c / W6d — pause resume and selection binding
# ---------------------------------------------------------------------------


def _lead_snapshot(
    output: Mapping[str, Any],
    branches: tuple[FanOutBranchResumeState, ...],
    worker_count: int,
    selection: WorkerSelection = LEAD,
) -> Any:
    return _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output=dict(output),
            orchestrator_step_id="orch",
            branches=branches,
            worker_count=worker_count,
            worker_selection=selection,
        )
    )


def _completed(index: int, step_id: str) -> FanOutBranchResumeState:
    return FanOutBranchResumeState(
        branch_index=index,
        step_id=step_id,
        terminal_status="completed",
        output={"worker": step_id},
    )


def test_w6_pause_captures_the_plan_and_resume_redispatches_only_planned_rest() -> None:
    """W6 — kills: resume deriving `worker_steps` from the declared pool."""
    output = _plan("c", "a")
    steps = [_orch(output), _leaf("a"), _leaf("b"), _leaf("c")]
    paused = _run(
        _manifest(LEAD, tier=_TEAM),
        steps,
        _PlanDispatcher(fail=frozenset({"a"}), gate=frozenset({"c"})),
        _pause_ctx(),
    )
    assert paused.status is RunStatus.PAUSED
    captured = paused.pause_snapshot.fan_out_resume
    assert captured.worker_count == 2 and captured.worker_selection is LEAD
    assert {b.branch_index: b.step_id for b in captured.branches} == {0: "c", 1: "a"}

    # a left re-dispatchable (cancelled before dispatch): only a re-runs, as declared index 1.
    resume = _PlanDispatcher()
    result = _run(
        _manifest(LEAD, tier=_TEAM),
        steps,
        resume,
        _pause_ctx(),
        pause_snapshot_input=_lead_snapshot(output, (_completed(0, "c"),), 2),
    )
    assert result.status is RunStatus.SUCCESS
    assert resume.calls == ["a"]
    assert resume.contexts["a"].step_index == 1
    assert list(result.final_state["worker_outputs"]) == ["c", "a"]

    # A resumed plan whose ordinals no longer match the recorded branches fails closed.
    reordered = _lead_snapshot(_plan("a", "c"), (_completed(0, "c"),), 2)
    mismatch = _run(
        _manifest(LEAD, tier=_TEAM),
        steps,
        _PlanDispatcher(),
        _pause_ctx(),
        pause_snapshot_input=reordered,
    )
    assert (mismatch.fail_class or "").startswith(
        "orchestrator-workers-resume-branch-identity-mismatch at 0"
    )


@pytest.mark.parametrize(("captured", "resumed"), [(LEAD, POOL), (POOL, LEAD)])
def test_w6b_pause_resume_under_a_changed_selection_fails_without_dispatch(
    captured: WorkerSelection, resumed: WorkerSelection
) -> None:
    """W6b (pause) — kills: selection not recorded (b re-dispatched with its declared brief
    beside a's lead-plan output)."""
    steps = [_orch(_plan("a", ("b", "lead b"))), _leaf("a"), _sub("b")]
    paused = _run(
        _manifest(captured, tier=_TEAM),
        steps,
        _PlanDispatcher(fail=frozenset({"b"}), gate=frozenset({"a"})),
        _pause_ctx(),
    )
    assert paused.status is RunStatus.PAUSED
    assert paused.pause_snapshot.fan_out_resume.worker_selection is captured

    resume = _PlanDispatcher()
    result = _run(
        _manifest(resumed, tier=_TEAM),
        steps,
        resume,
        _pause_ctx(),
        pause_snapshot_input=paused.pause_snapshot,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-selection-mismatch"
    assert resume.calls == []


@pytest.mark.parametrize(("recorded", "resumed"), [(LEAD, POOL), (POOL, LEAD)])
def test_w6b_crash_resume_under_a_changed_selection_fails_without_dispatch(
    recorded: WorkerSelection, resumed: WorkerSelection
) -> None:
    """W6b (crash) — the selection recorded with the store's orchestrator output binds."""
    store = _InMemoryBranchStore()
    steps = [_orch(_plan("a", ("b", "lead b"))), _leaf("a"), _sub("b")]
    _store_run(recorded, steps, store)
    store.forget_branch(store.sole_run_key(), 1)

    result, resume = _store_run(resumed, steps, store)
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-selection-mismatch"
    assert resume.calls == []


class _LegacyStore(_InMemoryBranchStore):
    """A pre-v1.130 store: `record_orchestrator` has no `worker_selection` parameter."""

    def record_orchestrator(  # type: ignore[override]
        self, run_key: str, step_id: str, output: dict[str, Any]
    ) -> None:
        super().record_orchestrator(run_key, step_id, output)


def test_w6c_absent_selection_resumes_as_declared_pool() -> None:
    """W6c — kills: absent selection read as `LEAD_PLAN`. A snapshot and a store record
    without `worker_selection` resume as `DECLARED_POOL` (and refuse `LEAD_PLAN`)."""
    output = _plan("c")
    steps = [_orch(output), _leaf("a"), _leaf("c")]
    captured = _lead_snapshot(output, (_completed(0, "a"),), 2, selection=POOL)
    assert "worker_selection" not in captured.fan_out_resume.model_dump()
    # Re-read from its persisted form, as a snapshot written before v1.130 would be.
    legacy_snapshot = PauseSnapshot.model_validate_json(captured.model_dump_json())

    resume = _PlanDispatcher()
    ok = _run(
        _manifest(POOL, tier=_TEAM),
        steps,
        resume,
        _pause_ctx(),
        pause_snapshot_input=legacy_snapshot,
    )
    assert ok.status is RunStatus.SUCCESS and resume.calls == ["c"]
    refused = _run(
        _manifest(LEAD, tier=_TEAM),
        steps,
        _PlanDispatcher(),
        _pause_ctx(),
        pause_snapshot_input=legacy_snapshot,
    )
    assert refused.fail_class == "orchestrator-workers-selection-mismatch"

    store = _LegacyStore()
    _store_run(POOL, steps, store)
    store.forget_branch(store.sole_run_key(), 1)
    crash_ok, crash_resume = _store_run(POOL, steps, store)
    assert crash_ok.status is RunStatus.SUCCESS and crash_resume.calls == ["c"]


def test_w6c_lead_plan_on_a_store_without_the_parameter_fails_before_the_orchestrator() -> None:
    """W6c — kills: a `LEAD_PLAN` record written without its selection."""
    store = _LegacyStore()
    result, dispatcher = _store_run(LEAD, [_orch(_plan("a")), _leaf("a")], store, tier=_TEAM)
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-plan-store-unsupported"
    assert dispatcher.calls == []
    assert store._orchestrator_dispatched == {} and store._orchestrators == {}


def test_w6d_resumed_lead_plan_keeps_the_recorded_brief_over_a_changed_declared_one() -> None:
    """W6d — kills: an optional lead brief falling back to the declared payload brief."""
    output = _plan(("a", "lead a"), ("b", "lead b"))
    changed = [_orch(output), _sub("a"), _sub("b", declared_objective="CHANGED")]

    pause_resume = _PlanDispatcher()
    paused = _run(
        _manifest(LEAD, tier=_TEAM),
        changed,
        pause_resume,
        _pause_ctx(),
        pause_snapshot_input=_lead_snapshot(output, (_completed(0, "a"),), 2),
    )
    assert paused.status is RunStatus.SUCCESS
    assert pause_resume.calls == ["b"]
    assert pause_resume.contexts["b"].lead_brief == _brief("lead b")

    store = _InMemoryBranchStore()
    _store_run(LEAD, [_orch(output), _sub("a"), _sub("b")], store)
    store.forget_branch(store.sole_run_key(), 1)
    crashed, crash_resume = _store_run(LEAD, changed, store)
    assert crashed.status is RunStatus.SUCCESS
    assert crash_resume.calls == ["b"]
    assert crash_resume.contexts["b"].lead_brief == _brief("lead b")


# ---------------------------------------------------------------------------
# W7a / W7b / W8 / W8b — crash resume
# ---------------------------------------------------------------------------

_CA = [_orch(_plan("c", "a")), _leaf("a"), _leaf("b"), _leaf("c")]


def test_w7a_crash_resume_sizes_the_worker_domain_from_the_plan() -> None:
    """W7a — kills: `_determine_fanout_resume` returning `worker_count = len(steps) - 1`;
    recovery contexts using `branch_index + 1`."""
    store = _InMemoryBranchStore()
    _store_run(LEAD, _CA, store)
    store.forget_branch(store.sole_run_key(), 1)  # a (ordinal 1) in flight at the crash

    result, resume = _store_run(LEAD, _CA, store)
    assert result.status is RunStatus.SUCCESS
    assert resume.calls == ["a"]
    assert resume.contexts["a"].step_index == 1
    assert list(result.final_state["worker_outputs"]) == ["c", "a"]


def _no_completed_branch(store: _InMemoryBranchStore) -> str:
    key = store.sole_run_key()
    store.forget_branch_undispatched(key, 0)
    store.forget_branch_undispatched(key, 1)
    return key


def test_w7b_stale_marker_beyond_the_plan_fails_closed_at_the_driver_gate() -> None:
    """W7b (cardinality/gate leg) — kills: the driver gate's ordinal bound sized from the pool.
    Ordinal 2 is inside the declared count (3) and outside the planned count (2)."""
    store = _InMemoryBranchStore()
    _store_run(LEAD, _CA, store, tier=_TEAM)
    key = _no_completed_branch(store)
    store.inject_stale_dispatch_marker(key, 2, "declarative-step")

    result, resume = _store_run(LEAD, _CA, store, tier=_TEAM)
    assert result.status is RunStatus.FAILED
    assert "fan-out-crash-resume" in (result.fail_class or "")
    assert resume.calls == []


def test_w7b_timed_out_marker_beyond_the_plan_is_refire_unsafe() -> None:
    """W7b (timeout leg) — kills: the `RE_DISPATCH` timeout `_branch_count` sized from the pool."""
    store = _InMemoryBranchStore()
    redispatch = FanoutTimeoutDisposition.RE_DISPATCH
    _store_run(LEAD, _CA, store, timeout=redispatch)
    key = _no_completed_branch(store)
    store.record_branch(key, 2, "b", "timed_out", None)
    store.inject_stale_dispatch_marker(key, 2, "declarative-step")

    result, resume = _store_run(LEAD, _CA, store, timeout=redispatch)
    assert result.status is RunStatus.FAILED
    assert (result.fail_class or "").startswith("fan-out-crash-resume-timeout-ambiguous")
    assert resume.calls == []


def test_w7b_changed_pool_size_still_fails_the_recorded_cardinality_check() -> None:
    """W7b (kept check) — kills: the recorded-cardinality check dropped or switched to plan
    length (the plan [c, a] still fits the grown pool)."""
    store = _InMemoryBranchStore()
    _store_run(LEAD, _CA, store)
    store.forget_branch(store.sole_run_key(), 1)

    result, resume = _store_run(LEAD, [*_CA, _leaf("d")], store)
    assert result.status is RunStatus.FAILED
    assert "cardinality mismatch" in (result.fail_class or "")
    assert resume.calls == []


def test_w8_worker_record_without_an_orchestrator_record_fails_closed() -> None:
    """W8 — kills: falling back to the declared pool when the orchestrator record is missing."""
    store = _InMemoryBranchStore()
    _store_run(LEAD, _CA, store)
    store._orchestrators.pop(store.sole_run_key())

    result, resume = _store_run(LEAD, _CA, store)
    assert result.status is RunStatus.FAILED
    assert (result.fail_class or "").startswith("fan-out-crash-resume-store-corrupt")
    assert resume.calls == []


@pytest.mark.parametrize("selection", [LEAD, POOL])
@pytest.mark.parametrize("tier", [_TEAM, _SOLO])
@pytest.mark.parametrize("marker", ["worker-dispatch", "cardinality"])
def test_w8b_orphaned_marker_without_any_orchestrator_artifact_fails_closed(
    selection: WorkerSelection, tier: PersonaTier, marker: str
) -> None:
    """W8b — kills: the no-branch arm returning `None` (a fresh re-dispatch) when only worker or
    cardinality markers are present. Under `PROCEED` workers write no dispatch markers, so any
    such marker is orphaned too."""
    store = _InMemoryBranchStore()
    _store_run(selection, _CA, store, tier=tier)
    key = store.sole_run_key()
    store.forget_orchestrator_undispatched(key)
    if marker == "worker-dispatch":
        store.inject_stale_dispatch_marker(key, 0, "declarative-step")
    else:
        store.record_fanout_cardinality(key, len(_CA))

    result, resume = _store_run(selection, _CA, store, tier=tier)
    assert result.status is RunStatus.FAILED
    assert (result.fail_class or "").startswith("fan-out-crash-resume-store-corrupt")
    assert resume.calls == []  # not even the orchestrator


# ---------------------------------------------------------------------------
# W9 — HIERARCHICAL_DELEGATION
# ---------------------------------------------------------------------------


def test_w9_each_level_applies_its_own_selection_and_the_cap_reads_the_pool() -> None:
    """W9 — kills: the cap computed on the plan; a child level using the parent's selection."""
    child_manifest = _manifest(
        LEAD, topology=TopologyPattern.HIERARCHICAL_DELEGATION, workflow_id="wf-child"
    )
    child_steps = [_orch(_plan("g2")), _leaf("g0"), _leaf("g1"), _leaf("g2")]
    parent_steps = [
        WorkflowStep(
            step_id=StepID("parent-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"out": {"role": "parent"}},
        ),
        WorkflowStep(
            step_id=StepID("sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_manifest": child_manifest, "child_steps": child_steps},
        ),
    ]
    ctx = _pause_ctx()
    dispatcher = _PlanDispatcher(ctx=ctx)
    parent = _manifest(POOL, topology=TopologyPattern.HIERARCHICAL_DELEGATION)
    result = _run(parent, parent_steps, dispatcher, ctx)
    assert result.status is RunStatus.SUCCESS
    assert result.final_state["worker_outputs"]["sub"]["worker_outputs"] == {"g2": {"worker": "g2"}}
    assert not {"g0", "g1"} & set(dispatcher.calls)

    capped = _PlanDispatcher()
    over_cap = _run(
        _manifest(LEAD, topology=TopologyPattern.HIERARCHICAL_DELEGATION),
        [_orch(_plan("w0", "w1")), *(_leaf(f"w{i}") for i in range(4))],
        capped,
        _pause_ctx(),
    )
    assert over_cap.status is RunStatus.FAILED
    assert "hierarchical-delegation-fanout-cap-exceeded" in (over_cap.fail_class or "")
    assert capped.calls == []

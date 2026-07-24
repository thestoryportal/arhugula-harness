"""B-39 impl leg Slice B, codex round-2 [P1] fix — CP spec v1.106 §1.2 property 4
(round-7 deterministic safety rule) + property 5 (gate-owning-vs-container split).

`hitl_response_for`'s uniform `hitl_response` fallback is safe only when exactly
ONE gate-owning branch is paused-and-unaddressed this resume cycle. With 2+
concurrently-paused gate-owning siblings, applying the uniform default to every
unaddressed one would misattribute a single operator answer (possibly a
branch-specific EDIT payload) to multiple distinct branches. This module tests:

  1. `_collect_gate_owning_run_ids` / `compute_hitl_uniform_fallback_eligible_
     run_id` (pure tree-walk over `PauseSnapshot`) in isolation.
  2. The linear reconstruction site's consumption of the computed eligibility
     (`workflow_driver.py`'s `hitl_delivery_cell` construction) — the actual
     defect codex round-2 found.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

from harness_core import PersonaTier, StepID, WorkloadClass
from harness_core.identity import EntryID
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import (
    PausedChildBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    _collect_gate_owning_run_ids,
    compute_hitl_uniform_fallback_eligible_run_id,
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-hitl-uniform-fallback-p4")
_ANCHOR = "0" * 64
_WF = "wf-hitl-p4"


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _snapshot(
    *,
    run_id: str,
    pause_reason: WorkflowPauseReason,
    step_index: int = 0,
    peer_fan_out_resume: PeerFanOutResumeState | None = None,
) -> PauseSnapshot:
    """A minimal `PauseSnapshot` for the PURE tree-walk tests — `snapshot_hash`
    is a placeholder (never validated by `_collect_gate_owning_run_ids` /
    `compute_hitl_uniform_fallback_eligible_run_id`, which read the object
    graph directly, not through `attempt_resume`'s hash-recompute gate)."""
    return PauseSnapshot(
        workflow_id=_WF,
        run_id=run_id,
        step_index=step_index,
        pause_reason=pause_reason,
        state_summary=_summary(),
        snapshot_hash="f" * 64,
        created_at=0,
        state_ledger_anchor=_ANCHOR,
        peer_fan_out_resume=peer_fan_out_resume,
    )


def _paused_child(
    *, branch_index: int, child_snapshot: PauseSnapshot
) -> PausedChildBranchResumeState:
    return PausedChildBranchResumeState(
        branch_index=branch_index,
        step_id=f"worker-{branch_index}",
        child_snapshot=child_snapshot,
    )


# ---------- pure tree-walk unit tests ----------------------------------------


def test_single_gate_owning_branch_is_eligible_for_uniform_fallback() -> None:
    """Byte-compat / pre-B-39 shape: a lone HITL_PENDING root has no siblings —
    it is trivially the sole member of the unaddressed gate-owning set."""
    root = _snapshot(run_id="run-solo", pause_reason=WorkflowPauseReason.HITL_PENDING)
    assert _collect_gate_owning_run_ids(root) == ["run-solo"]
    eligible = compute_hitl_uniform_fallback_eligible_run_id(root, ResumeContext())
    assert eligible == "run-solo"


def test_two_unaddressed_gate_owning_siblings_yield_no_eligible_run_id() -> None:
    """codex round-2 [P1] core case: 2 concurrently-paused gate-owning peer
    branches, neither addressed by `hitl_responses` — NEITHER may use the
    uniform fallback (property 4 safety: 2+ unaddressed → None)."""
    child_a = _snapshot(run_id="run-a", pause_reason=WorkflowPauseReason.HITL_PENDING)
    child_b = _snapshot(run_id="run-b", pause_reason=WorkflowPauseReason.HITL_PENDING)
    root = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(branch_index=0, child_snapshot=child_a),
                _paused_child(branch_index=1, child_snapshot=child_b),
            ),
        ),
    )
    assert set(_collect_gate_owning_run_ids(root)) == {"run-a", "run-b"}
    assert compute_hitl_uniform_fallback_eligible_run_id(root, ResumeContext()) is None
    # A resume_context that carries ONLY the uniform field (the pre-B-39-shaped,
    # naive-caller-common case codex flagged) is exactly this scenario.
    uniform_only = ResumeContext(
        hitl_response=HITLResult(
            response=HITLResponse.APPROVE,
            timestamp="2026-07-24T00:00:00Z",
            audit_ledger_entry_id=EntryID("e-uniform-only"),
            response_summary_hash="a" * 64,
        )
    )
    assert compute_hitl_uniform_fallback_eligible_run_id(root, uniform_only) is None


def test_map_addressing_one_of_two_leaves_the_other_as_sole_eligible() -> None:
    """When the operator's `hitl_responses` map addresses ALL BUT ONE
    gate-owning sibling, the remaining unaddressed one is safely the SOLE
    member — the uniform fallback may resolve it (property 4's own boundary:
    "ONLY when that branch is the SOLE member of the unaddressed set")."""
    child_a = _snapshot(run_id="run-a", pause_reason=WorkflowPauseReason.HITL_PENDING)
    child_b = _snapshot(run_id="run-b", pause_reason=WorkflowPauseReason.HITL_PENDING)
    root = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(branch_index=0, child_snapshot=child_a),
                _paused_child(branch_index=1, child_snapshot=child_b),
            ),
        ),
    )
    addressed = ResumeContext(
        hitl_responses={
            "run-a": HITLResult(
                response=HITLResponse.EDIT,
                timestamp="2026-07-24T00:00:00Z",
                audit_ledger_entry_id=EntryID("e-run-a"),
                response_summary_hash="b" * 64,
            )
        }
    )
    assert compute_hitl_uniform_fallback_eligible_run_id(root, addressed) == "run-b"


def test_container_branch_never_counted_as_gate_owning() -> None:
    """Property 5: a transitively-paused container/ancestor branch (paused only
    because an unresolved DESCENDANT exists below it) is NEVER itself
    gate-owning, regardless of nesting depth — only the deepest HITL_PENDING
    leaves are collected."""
    grandchild = _snapshot(run_id="run-grandchild", pause_reason=WorkflowPauseReason.HITL_PENDING)
    container_child = _snapshot(
        run_id="run-container-child",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            paused_child_branches=(_paused_child(branch_index=0, child_snapshot=grandchild),),
        ),
    )
    leaf_sibling = _snapshot(
        run_id="run-leaf-sibling", pause_reason=WorkflowPauseReason.HITL_PENDING
    )
    root = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(branch_index=0, child_snapshot=container_child),
                _paused_child(branch_index=1, child_snapshot=leaf_sibling),
            ),
        ),
    )
    # The container's own run_id is NEVER in the gate-owning set — only the
    # grandchild (the true gate-owning leaf) and the leaf sibling are.
    assert set(_collect_gate_owning_run_ids(root)) == {"run-grandchild", "run-leaf-sibling"}
    assert "run-container-child" not in _collect_gate_owning_run_ids(root)
    # 2 unaddressed gate-owning leaves → property 4 safety → no eligible run_id,
    # even though the container branch sits between them structurally.
    assert compute_hitl_uniform_fallback_eligible_run_id(root, ResumeContext()) is None


def test_none_root_or_none_resume_context_yields_no_eligible_run_id() -> None:
    assert compute_hitl_uniform_fallback_eligible_run_id(None, ResumeContext()) is None
    root = _snapshot(run_id="run-solo", pause_reason=WorkflowPauseReason.HITL_PENDING)
    assert compute_hitl_uniform_fallback_eligible_run_id(root, None) is None


# ---------- linear reconstruction site integration witnesses -----------------


def _manifest() -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=_WF,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": "do_effect", "tool_args": {"message": name}},
    )


class _RecordingLedger:
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


class _Emitter:
    def __init__(self) -> None:
        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: WorkflowEventClass) -> None:
        self.emits.append(event_class)


def _pause_context_reader() -> tuple[StateSummary, str]:
    return (_summary(), _ANCHOR)


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


class _Ctx:
    def __init__(self) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _RecordingLedger()
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = _protocol()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.inter_step_output_channel = None


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.TOOL_STEP:
            return self._dispatcher
        raise StepKindDispatcherNotBoundError(step_kind)


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    return cast(StepDispatcherRegistry, _Registry(dispatcher))


class HITLPauseRequestedSignal(BaseException):
    """Local re-declaration mirroring the production runtime composer's
    exception — the driver name-matches on `type(exc).__name__`
    (harness-cp cannot import harness-runtime per the workspace dependency
    graph), so this local class is sufficient to exercise the same path."""


class _HITLPauseDispatcher:
    """Signals a HITL pause at `raise_on` (mirrors the real HITL gate
    composer's durable-async branch: sets the shared `pause_requested_flag`,
    then raises the name-matched signal). Succeeds otherwise. Records
    `step_context.hitl_delivery_holder` on every dispatch."""

    def __init__(self, *, pause_requested_flag: asyncio.Event, raise_on: str) -> None:
        self._flag = pause_requested_flag
        self._raise_on = raise_on
        self.dispatched: list[str] = []
        self.seen_holders: list[tuple[str, Any]] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        self.seen_holders.append((step_id, getattr(step_context, "hitl_delivery_holder", None)))
        if step_id == self._raise_on:
            self._flag.set()
            raise HITLPauseRequestedSignal()
        return {"tool_id": "do_effect", "response": {"echoed": step_id}}


def _capture_hitl_pause(*, run_id: str) -> PauseSnapshot:
    ctx = _Ctx()
    dispatcher = _HITLPauseDispatcher(pause_requested_flag=ctx.pause_requested_flag, raise_on="s0")
    result = execute_workflow(
        _manifest(),
        [_step("s0"), _step("s1")],
        run_id=run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason is WorkflowPauseReason.HITL_PENDING
    return snap


def _resume(
    *,
    pause_snapshot_input: PauseSnapshot,
    resume_context: ResumeContext,
    hitl_uniform_fallback_eligible_run_id: str | None,
) -> _HITLPauseDispatcher:
    """Resume the captured pause; return the recording dispatcher for assertion."""
    ctx = _Ctx()
    dispatcher = _HITLPauseDispatcher(
        pause_requested_flag=ctx.pause_requested_flag, raise_on="__never__"
    )
    result = execute_workflow(
        _manifest(),
        [_step("s0"), _step("s1")],
        run_id=pause_snapshot_input.run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
        pause_snapshot_input=pause_snapshot_input,
        resume_context=resume_context,
        hitl_uniform_fallback_eligible_run_id=hitl_uniform_fallback_eligible_run_id,
    )
    assert result.status is RunStatus.SUCCESS
    return dispatcher


def test_two_unaddressed_gate_owning_children_both_repause_inert_not_misapplied() -> None:
    """codex round-2 [P1] mutation probe — the actual defect. Two independently
    paused HITL_PENDING children (simulating 2 concurrently-paused gate-owning
    peer branches under one resume() cycle) resume with a `resume_context`
    carrying ONLY the uniform `hitl_response` (no map — the naive, pre-B-39-
    shaped caller). `hitl_uniform_fallback_eligible_run_id=None` (what
    `compute_hitl_uniform_fallback_eligible_run_id` correctly returns for this
    2-member-unaddressed scenario, per the pure tests above) — NEITHER child's
    `hitl_delivery_holder` may be populated. Before the fix, EACH child's own
    `hitl_response_for(run_id)` call fell through to the SAME uniform value
    independently, misapplying one operator answer to both."""
    snap_a = _capture_hitl_pause(run_id="child-run-a")
    snap_b = _capture_hitl_pause(run_id="child-run-b")

    uniform_fallback = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-07-24T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-two-unaddressed"),
        response_summary_hash="c" * 64,
    )
    resume_ctx = ResumeContext(hitl_response=uniform_fallback)

    dispatcher_a = _resume(
        pause_snapshot_input=snap_a,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=None,
    )
    dispatcher_b = _resume(
        pause_snapshot_input=snap_b,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=None,
    )

    # The RESUMED step (s0, where the pause was captured) must NEVER receive a
    # delivery cell for either child — re-pause INERT is the safe outcome, not
    # an auto-applied cross-branch misattribution.
    holder_a = dict(dispatcher_a.seen_holders)["s0"]
    holder_b = dict(dispatcher_b.seen_holders)["s0"]
    assert holder_a is None
    assert holder_b is None


def test_sole_unaddressed_gate_owning_child_safely_receives_uniform_fallback() -> None:
    """Positive control: when `hitl_uniform_fallback_eligible_run_id` correctly
    names ONE child as the sole unaddressed member, THAT child receives the
    uniform response — property 4 does not foreclose the safe single-branch
    case (byte-compat with pre-B-39 behavior)."""
    snap_a = _capture_hitl_pause(run_id="child-run-solo")
    uniform_fallback = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-07-24T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-sole-unaddressed"),
        response_summary_hash="d" * 64,
    )
    resume_ctx = ResumeContext(hitl_response=uniform_fallback)

    dispatcher = _resume(
        pause_snapshot_input=snap_a,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=snap_a.run_id,
    )
    holder = dict(dispatcher.seen_holders)["s0"]
    assert holder is not None
    assert holder.consume_and_clear() == uniform_fallback


def test_map_hit_is_always_safe_regardless_of_uniform_fallback_eligibility() -> None:
    """A `hitl_responses` map HIT is addressed to THIS run_id specifically —
    always safe, independent of `hitl_uniform_fallback_eligible_run_id` (which
    only gates the UNIFORM fallback path). Even with eligibility explicitly
    `None` (as it correctly would be with an unaddressed sibling elsewhere),
    a map-addressed child still receives its OWN keyed response."""
    snap_a = _capture_hitl_pause(run_id="child-run-mapped")
    keyed_response = HITLResult(
        response=HITLResponse.EDIT,
        timestamp="2026-07-24T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-map-hit"),
        response_summary_hash="e" * 64,
    )
    uniform_fallback = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-07-24T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-map-hit-uniform"),
        response_summary_hash="f" * 64,
    )
    resume_ctx = ResumeContext(
        hitl_response=uniform_fallback,
        hitl_responses={snap_a.run_id: keyed_response},
    )

    dispatcher = _resume(
        pause_snapshot_input=snap_a,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=None,
    )
    holder = dict(dispatcher.seen_holders)["s0"]
    assert holder is not None
    assert holder.consume_and_clear() == keyed_response

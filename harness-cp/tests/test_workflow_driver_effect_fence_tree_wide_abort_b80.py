"""B-80 impl leg — CP spec v1.111 §2 property 8: the effect-fence-abort HITL-delivery
suppression guard MUST be computed against the TRUE ROOT of the resume tree, not
merely the current fan-out level's own locally-recovered branches.

The pre-existing `_any_fence_abort` guard (B-72 impl leg, round 4) is computed from
`_recovered_effect_fence_paused`, scoped to the CURRENT fan-out level only. When an
effect-fence ABORT targets a DIFFERENT, nested pause subtree (a deeper
`HIERARCHICAL_DELEGATION` level, or a sibling peer's recursively paused child), a
shallower level's own `_any_fence_abort` stays `False` and its pre-dispatch
gate-owning peer could still receive a delivery cell and dispatch before the
run-level abort is honored. `compute_effect_fence_tree_wide_abort_present` closes
this by computing a THIRD sibling signal ONCE at the true depth-0 root (mirroring
`compute_hitl_uniform_fallback_eligible_run_id` /
`compute_effect_fence_uniform_fallback_eligible_key`) and ORing it (never replacing)
into the level-local guard at both fan-out dispatch sites.

This module tests:

  1. `compute_effect_fence_tree_wide_abort_present` (pure tree-walk over
     `PauseSnapshot`, reusing `_collect_effect_fence_idempotency_keys` +
     `_resolve_effect_fence_gated`) in isolation, including the tree-wide reach
     into a NESTED `paused_child_branches` subtree a level-local computation
     could never see.
  2. The `_execute_parallelization` + `_execute_orchestrator_workers` OR-widening
     sites' actual suppression behavior, via `execute_workflow`'s
     `effect_fence_tree_wide_abort_present` parameter — a direct-kwarg witness
     mirroring how `test_workflow_driver_effect_fence_uniform_fallback_b70.py`
     exercises its own sibling parameter, since this level's own recovered set
     has NO effect-fence-paused branch of its own (so the level-local term is
     `False` on its own) yet suppression MUST still fire when the tree-wide
     signal is `True`.
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
    EffectFenceResolution,
    EffectFenceResumeState,
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
    _collect_effect_fence_idempotency_keys,
    compute_effect_fence_tree_wide_abort_present,
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-effect-fence-tree-wide-abort-b80")
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # -> cascade_policy = pause
_ANCHOR = "0" * 64


class HITLPauseRequestedSignal(BaseException):
    """Test-local stand-in for the runtime `hitl_gate_composer.HITLPauseRequestedSignal`
    — a `BaseException`, name-matched by the driver (harness-cp cannot import
    harness-runtime), mirroring `test_workflow_driver_parallelization_pause.py`'s own
    local declaration."""


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
    pause_reason: WorkflowPauseReason = WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
    step_index: int = 0,
    effect_fence_resume: EffectFenceResumeState | None = None,
    peer_fan_out_resume: PeerFanOutResumeState | None = None,
) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id="wf-b80",
        run_id=run_id,
        step_index=step_index,
        pause_reason=pause_reason,
        state_summary=_summary(),
        snapshot_hash="f" * 64,
        created_at=0,
        state_ledger_anchor=_ANCHOR,
        effect_fence_resume=effect_fence_resume,
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


def test_none_root_or_none_resume_context_yields_false() -> None:
    """Byte-compat with the crash-resume path (CP spec v1.111 §2.1(b)) — no
    `resume_context` exists, so the level-local `_any_fence_abort` term already
    evaluates `False`; this sibling MUST also evaluate `False`, never `True`."""
    assert compute_effect_fence_tree_wide_abort_present(None, ResumeContext()) is False
    root = _snapshot(
        run_id="run-solo", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-solo")
    )
    assert compute_effect_fence_tree_wide_abort_present(root, None) is False


def test_no_effect_fence_pause_anywhere_yields_false() -> None:
    root = _snapshot(
        run_id="run-none",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
    )
    assert _collect_effect_fence_idempotency_keys(root) == []
    assert compute_effect_fence_tree_wide_abort_present(root, ResumeContext()) is False


def test_sole_pause_resolving_non_abort_yields_false() -> None:
    root = _snapshot(
        run_id="run-solo", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-solo")
    )
    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    assert compute_effect_fence_tree_wide_abort_present(root, resume_ctx) is False


def test_sole_pause_resolving_abort_via_uniform_fallback_yields_true() -> None:
    root = _snapshot(
        run_id="run-solo", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-solo")
    )
    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.ABORT)
    assert compute_effect_fence_tree_wide_abort_present(root, resume_ctx) is True


def test_map_addressed_abort_yields_true_regardless_of_uniform_eligibility() -> None:
    """A map HIT is always safe (CP spec v1.107 §1.1) — even with 2 unaddressed
    siblings elsewhere (so `eligible_key` would be `None`), a location the
    operator's map explicitly resolves to ABORT still counts."""
    child_a = _snapshot(
        run_id="run-a", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-a")
    )
    child_b = _snapshot(
        run_id="run-b", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-b")
    )
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
    addressed = ResumeContext(effect_fence_resolutions={"key-a": EffectFenceResolution.ABORT})
    assert compute_effect_fence_tree_wide_abort_present(root, addressed) is True


def test_two_unaddressed_uniform_abort_yields_false_neither_may_use_fallback() -> None:
    """Safety mirror of `compute_effect_fence_uniform_fallback_eligible_key`'s own
    2+-unaddressed rule: with `eligible_key=None`, the uniform ABORT default may
    NOT resolve either location — so the tree-wide signal stays `False` even
    though the operator's uniform default IS `ABORT`."""
    child_a = _snapshot(
        run_id="run-a", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-a")
    )
    child_b = _snapshot(
        run_id="run-b", effect_fence_resume=EffectFenceResumeState(idempotency_key="key-b")
    )
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
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.ABORT)
    assert compute_effect_fence_tree_wide_abort_present(root, uniform_only) is False


def test_nested_paused_child_abort_is_reachable_tree_wide() -> None:
    """The core tree-wide-reach case: an ABORT resolves at a location nested TWO
    levels deep under `paused_child_branches` (a recursively-paused grandchild) —
    invisible to any level-local `_recovered_effect_fence_paused` computation at
    a shallower level, but reachable by the tree-wide walk from the true root."""
    grandchild = _snapshot(
        run_id="run-grandchild",
        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-deep"),
    )
    child = _snapshot(
        run_id="run-child",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            paused_child_branches=(_paused_child(branch_index=0, child_snapshot=grandchild),),
        ),
    )
    root = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            paused_child_branches=(_paused_child(branch_index=0, child_snapshot=child),),
        ),
    )
    assert _collect_effect_fence_idempotency_keys(root) == ["key-deep"]
    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.ABORT)
    assert compute_effect_fence_tree_wide_abort_present(root, resume_ctx) is True


# ---------- fan-out dispatch-site OR-widening integration witnesses ----------


def _pause_context_reader() -> tuple[StateSummary, str]:
    return (_summary(), _ANCHOR)


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
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


def _manifest(
    workflow_id: str, topology: TopologyPattern, persona_tier: PersonaTier = _PAUSE_TIER
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


class _SoloPreDispatchDispatcher:
    """Single SUB_AGENT_DISPATCH step that always raises the pre-dispatch HITL
    pause signal — no effect-fence peer at this level at all, so
    `_recovered_effect_fence_paused` is empty and the level-local
    `_any_fence_abort` term is `False` on its own construction."""

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        raise HITLPauseRequestedSignal()


class _ResumeAwareGateDispatcher:
    """Mirrors the real HITL gate composer's Step-0 short-circuit: consumes
    `step_context.hitl_delivery_holder` if present and non-`None` (dispatches as
    if approved); otherwise re-raises the pause signal."""

    def __init__(self) -> None:
        self.dispatched_without_cell: list[str] = []
        self.dispatched_with_cell: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        holder = getattr(step_context, "hitl_delivery_holder", None)
        resolved = holder.consume_and_clear() if holder is not None else None
        if resolved is not None:
            self.dispatched_with_cell.append(str(step.step_id))
            return {"role": "resumed-gate", "echoed": dict(step.step_payload)}
        self.dispatched_without_cell.append(str(step.step_id))
        raise HITLPauseRequestedSignal()


def _approve_response() -> HITLResult:
    return HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-07-27T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-b80"),
        response_summary_hash="b" * 64,
    )


def _capture_parallelization_pause() -> PauseSnapshot:
    ctx = cast(DriverContext, _Ctx())
    steps = [
        WorkflowStep(
            step_id=StepID("branch-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-b80"},
        ),
    ]
    result = execute_workflow(
        _manifest("wf-b80-par", TopologyPattern.PARALLELIZATION),
        steps,
        run_id="run-b80-par",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _SoloPreDispatchDispatcher()),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    pfr = snap.peer_fan_out_resume
    assert pfr is not None
    assert [b.branch_index for b in pfr.pre_dispatch_gate_owning_branches] == [0]
    return snap


def test_parallelization_suppresses_sole_gate_owner_when_tree_wide_abort_present() -> None:
    """The B-80 defect this arc closes, at `_execute_parallelization`. THIS
    level's own recovered set has NO effect-fence-paused branch (the level-local
    `_any_fence_abort` term is `False` on its own), yet the sole pre-dispatch
    gate-owning peer MUST NOT receive a delivery cell when
    `effect_fence_tree_wide_abort_present=True` — proving the OR-widening at the
    dispatch site, not merely at the pure `compute_*` function."""
    snap = _capture_parallelization_pause()
    dispatcher = _ResumeAwareGateDispatcher()
    resume_ctx = ResumeContext(hitl_response=_approve_response())
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_ctx)
    resumed = execute_workflow(
        _manifest("wf-b80-par", TopologyPattern.PARALLELIZATION),
        [
            WorkflowStep(
                step_id=StepID("branch-0-sub"),
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                step_payload={"child_workflow_id": "wf-child-b80"},
            ),
        ],
        run_id="run-b80-par",
        ctx=cast(DriverContext, _Ctx()),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
        effect_fence_tree_wide_abort_present=True,
    )
    assert dispatcher.dispatched_with_cell == [], (
        "the sole pre-dispatch gate-owning peer must NEVER receive a delivery "
        "cell while a TREE-WIDE effect-fence ABORT is in play, even though this "
        f"level's own local guard is False: {dispatcher.dispatched_with_cell!r}"
    )
    assert dispatcher.dispatched_without_cell == ["branch-0-sub"], (
        "the peer must still be RE-DISPATCHED (re-pausing INERT with no cell), "
        "not silently skipped — a vacuous pass would look identical to a real "
        "suppression"
    )
    assert resumed.status is RunStatus.PAUSED


def test_parallelization_delivers_sole_gate_owner_when_tree_wide_abort_absent() -> None:
    """Negative control: with `effect_fence_tree_wide_abort_present` at its
    `False` default (byte-compat), the sole pre-dispatch gate-owning peer
    receives its delivery cell exactly as before this arc — the OR-widening
    must never spuriously suppress when no tree-wide abort is present. Threads
    the SAME `hitl_uniform_fallback_eligible_run_id` the `_present` twin above
    uses, so this test genuinely exercises delivery reachability rather than
    passing vacuously because the branch was never eligible in the first
    place."""
    snap = _capture_parallelization_pause()
    dispatcher = _ResumeAwareGateDispatcher()
    resume_ctx = ResumeContext(hitl_response=_approve_response())
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_ctx)
    resumed = execute_workflow(
        _manifest("wf-b80-par", TopologyPattern.PARALLELIZATION),
        [
            WorkflowStep(
                step_id=StepID("branch-0-sub"),
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                step_payload={"child_workflow_id": "wf-child-b80"},
            ),
        ],
        run_id="run-b80-par",
        ctx=cast(DriverContext, _Ctx()),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
    )
    assert dispatcher.dispatched_with_cell == ["branch-0-sub"]
    assert dispatcher.dispatched_without_cell == []
    assert resumed.status is RunStatus.SUCCESS


def _capture_orchestrator_workers_pause() -> PauseSnapshot:
    ctx = cast(DriverContext, _Ctx())
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-b80-ow"},
        ),
    ]

    class _OrchestratorThenGateDispatcher:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            return cast(StepDispatcher, self)

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            if str(step.step_id) == "orchestrator":
                return {"role": "orchestrator", "echoed": dict(step.step_payload)}
            raise HITLPauseRequestedSignal()

    result = execute_workflow(
        _manifest("wf-b80-ow", TopologyPattern.ORCHESTRATOR_WORKERS),
        steps,
        run_id="run-b80-ow",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _OrchestratorThenGateDispatcher()),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    fr = snap.fan_out_resume
    assert fr is not None
    assert [b.branch_index for b in fr.pre_dispatch_gate_owning_branches] == [0]
    return snap


class _OrchestratorResumeAwareGateDispatcher:
    def __init__(self) -> None:
        self.dispatched_without_cell: list[str] = []
        self.dispatched_with_cell: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        if str(step.step_id) == "orchestrator":
            return {"role": "orchestrator", "echoed": dict(step.step_payload)}
        holder = getattr(step_context, "hitl_delivery_holder", None)
        resolved = holder.consume_and_clear() if holder is not None else None
        if resolved is not None:
            self.dispatched_with_cell.append(str(step.step_id))
            return {"role": "resumed-gate", "echoed": dict(step.step_payload)}
        self.dispatched_without_cell.append(str(step.step_id))
        raise HITLPauseRequestedSignal()


def _ow_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-b80-ow"},
        ),
    ]


def test_orchestrator_workers_suppresses_sole_gate_owner_when_tree_wide_abort_present() -> None:
    """Test-parity sibling of the PARALLELIZATION witness above, at
    `_execute_orchestrator_workers`'s own OR-widening site (grepped
    byte-identical to the PARALLELIZATION site before writing this test, per
    `[[codex-finding-scope-verify-sibling-pattern]]`)."""
    snap = _capture_orchestrator_workers_pause()
    dispatcher = _OrchestratorResumeAwareGateDispatcher()
    resume_ctx = ResumeContext(hitl_response=_approve_response())
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_ctx)
    resumed = execute_workflow(
        _manifest("wf-b80-ow", TopologyPattern.ORCHESTRATOR_WORKERS),
        _ow_steps(),
        run_id="run-b80-ow",
        ctx=cast(DriverContext, _Ctx()),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
        effect_fence_tree_wide_abort_present=True,
    )
    assert dispatcher.dispatched_with_cell == [], (
        "the sole pre-dispatch gate-owning worker must NEVER receive a delivery "
        "cell while a TREE-WIDE effect-fence ABORT is in play, even though this "
        f"level's own local guard is False: {dispatcher.dispatched_with_cell!r}"
    )
    assert dispatcher.dispatched_without_cell == ["worker-0-sub"]
    assert resumed.status is RunStatus.PAUSED


def test_orchestrator_workers_delivers_sole_gate_owner_when_tree_wide_abort_absent() -> None:
    """Negative control mirror of the PARALLELIZATION test above — threads the
    SAME `hitl_uniform_fallback_eligible_run_id` the `_present` twin uses."""
    snap = _capture_orchestrator_workers_pause()
    dispatcher = _OrchestratorResumeAwareGateDispatcher()
    resume_ctx = ResumeContext(hitl_response=_approve_response())
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_ctx)
    resumed = execute_workflow(
        _manifest("wf-b80-ow", TopologyPattern.ORCHESTRATOR_WORKERS),
        _ow_steps(),
        run_id="run-b80-ow",
        ctx=cast(DriverContext, _Ctx()),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
    )
    assert dispatcher.dispatched_with_cell == ["worker-0-sub"]
    assert dispatcher.dispatched_without_cell == []
    assert resumed.status is RunStatus.SUCCESS


def test_fresh_non_resuming_dispatch_ignores_default_tree_wide_abort_param() -> None:
    """A fresh (non-resume) dispatch never reaches the fan-out OR-site's
    consult path — byte-identical to pre-arc regardless of the new parameter's
    (default `False`) value."""
    ctx = cast(DriverContext, _Ctx())
    dispatcher = _SoloPreDispatchDispatcher()
    result = execute_workflow(
        _manifest("wf-b80-fresh", TopologyPattern.PARALLELIZATION),
        [
            WorkflowStep(
                step_id=StepID("branch-0-sub"),
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                step_payload={"child_workflow_id": "wf-child-b80"},
            ),
        ],
        run_id="run-b80-fresh",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )
    assert result.status is RunStatus.PAUSED
    assert result.pause_snapshot is not None

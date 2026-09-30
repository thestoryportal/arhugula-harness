"""B-79 impl leg slice 2 — CP spec v1.111 §1.2 property 7, §1.1(d): the three
single-owner sequential sites (LINEAR `resume_at`, `EVALUATOR_OPTIMIZER`,
`DECENTRALIZED_HANDOFF`) gain the SAME material-diff guard slice 1 built for the
fan-out closure's pre-dispatch gate-owning branch identity. `PauseSnapshot` gains
ONE new top-level field, `hitl_gate_config_hash` (default-`None`, byte-compat
scoped), reused across all three sites (unlike the fan-out branches, a sequential
resume has at most one currently-relevant step, so no per-branch carrier is
needed — see `PauseSnapshot.hitl_gate_config_hash`'s own docstring).

Placement (deliberately NOT mirroring slice 1's fan-out placement inside
`_resume_body_mismatch`): each site's check lives immediately before its
`hitl_delivery_cell` construction — the point where a stale delivery would
actually occur — not inside the unconditional `_resume_body_mismatch` closure.
A `_eo_resume`/`_handoff_resume`-bearing resume with NO delivery pending this
cycle (e.g. a nested child under a fan-out with 2+ unaddressed gate-owning
siblings) legitimately reaches those closures; rejecting it there would turn a
recoverable INERT re-pause into a terminal FAILED. `test_eo_*_no_delivery_pending_*`
/ `test_dh_*_no_delivery_pending_*` below are the witness for this — a design
correction caught before merge (an initial draft placed the EO/DH checks
inside `_resume_body_mismatch`, mirroring slice 1's placement uncritically;
`advisor()` confirmed the divergence + the over-rejection risk before this
landed). LINEAR has no such closure to begin with (it never had ANY material-
diff guard before this delta), so `test_linear_*_no_delivery_pending_*` proves
a narrower, less load-bearing property — only that the guard stays scoped
inside the `resume_context is not None` gate, not hoisted unconditionally
(merge-gate test-witness lens, PR #1133).

This module tests, per site (LINEAR / EVALUATOR_OPTIMIZER / DECENTRALIZED_HANDOFF):
  1. resume accepts an unchanged HITL gate configuration (real pause → resume
     round trip via `execute_workflow`, delivery actually happens → SUCCESS).
  2. resume rejects a changed HITL gate configuration (workflow edited between
     pause and resume) → FAILED, fail_class names the site + the changed hash.
  3. resume SKIPS the check for a legacy (captured-value-`None`) snapshot even
     when the live config has since changed — byte-compat, not an unconditional
     mismatch.
  4. a changed config with NO delivery pending this cycle (no `resume_context`)
     does NOT fail the run — the design-correction witness.
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
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind, HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol import PauseResumeProtocol, _compute_snapshot_hash
from harness_cp.pause_resume_protocol_types import PauseSnapshot, ResumeContext
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import CascadePolicy, TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b79-slice2")
_PAUSE_TIER = PersonaTier.TEAM_BINDING
_ANCHOR = "0" * 64

_PLACEMENT_A = HITLPlacement(
    position=HITLPlacementKind.PRE_ACTION,
    tool_filter=("read_file",),
    cascade_policy=CascadePolicy.PAUSE,
    timeout=5000,
)
_PLACEMENT_B = HITLPlacement(
    position=HITLPlacementKind.PRE_ACTION,
    tool_filter=("read_file",),
    cascade_policy=CascadePolicy.PAUSE,
    timeout=9999,  # ONLY the timeout differs from _PLACEMENT_A
)


def _hitl_result() -> HITLResult:
    return HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-07-27T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-b79-slice2"),
        response_summary_hash="a" * 64,
    )


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


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
        self.inter_step_output_channel = None


class HITLPauseRequestedSignal(BaseException):
    """Test-local stand-in for the runtime `hitl_gate_composer.HITLPauseRequestedSignal`
    — a `BaseException`, name-matched by the driver (harness-cp cannot import
    harness-runtime), mirroring every sibling pause test file's identically-named
    stand-in."""


def _manifest(
    *, topology: TopologyPattern, hitl_placements: tuple[HITLPlacement, ...], workflow_id: str
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PAUSE_TIER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=hitl_placements,
        per_step_overrides={},
    )


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    class _Registry:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            if step_kind is StepKind.DECLARATIVE_STEP:
                return dispatcher
            raise StepKindDispatcherNotBoundError(step_kind)

    return cast(StepDispatcherRegistry, _Registry())


def _legacy_snapshot(snap: PauseSnapshot) -> PauseSnapshot:
    """Simulate a snapshot captured by the PRECEDING deployment (before this
    field existed): `hitl_gate_config_hash=None`, `snapshot_hash` recomputed to
    match — a genuine legacy-shape witness, not a corruption probe. Mirrors
    slice 1's `test_peer_resume_skips_check_for_legacy_row_with_absent_hash`."""
    assert snap.hitl_gate_config_hash is not None
    legacy_hash = _compute_snapshot_hash(
        workflow_id=snap.workflow_id,
        run_id=snap.run_id,
        step_index=snap.step_index,
        state_summary=snap.state_summary,
        fan_out_resume=snap.fan_out_resume,
        peer_fan_out_resume=snap.peer_fan_out_resume,
        handoff_resume=snap.handoff_resume,
        evaluator_optimizer_resume=snap.evaluator_optimizer_resume,
        effect_fence_resume=snap.effect_fence_resume,
        orchestrator_effect_fence_resume=snap.orchestrator_effect_fence_resume,
        hitl_gate_config_hash=None,
    )
    return snap.model_copy(update={"hitl_gate_config_hash": None, "snapshot_hash": legacy_hash})


# =============================================================================
# LINEAR
# =============================================================================

_LINEAR_WF = "wf-b79-slice2-linear"


class _LinearDispatcher:
    def __init__(self, *, raise_on: str, pause_requested_flag: asyncio.Event) -> None:
        self._raise_on = raise_on
        self._flag = pause_requested_flag
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == self._raise_on:
            self._raise_on = "__never__"  # only raise once (the capture call)
            self._flag.set()
            raise HITLPauseRequestedSignal()
        self.dispatched.append(step_id)
        return {"echoed": step_id}


def _linear_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(step_id=StepID("s0"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}),
        WorkflowStep(step_id=StepID("s1"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}),
    ]


def _linear_capture(*, hitl_placements: tuple[HITLPlacement, ...]) -> PauseSnapshot:
    manifest = _manifest(
        topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        hitl_placements=hitl_placements,
        workflow_id=_LINEAR_WF,
    )
    ctx = _Ctx()
    result = execute_workflow(
        manifest,
        _linear_steps(),
        run_id="run-linear-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _LinearDispatcher(raise_on="s0", pause_requested_flag=ctx.pause_requested_flag)
        ),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason.value == "hitl_pending"
    assert snap.hitl_gate_config_hash is not None
    return snap


def _linear_resume(
    *,
    snap: PauseSnapshot,
    hitl_placements: tuple[HITLPlacement, ...],
    with_delivery: bool,
) -> Any:
    manifest = _manifest(
        topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        hitl_placements=hitl_placements,
        workflow_id=_LINEAR_WF,
    )
    ctx = _Ctx()
    return execute_workflow(
        manifest,
        _linear_steps(),
        run_id=snap.run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _LinearDispatcher(raise_on="__never__", pause_requested_flag=ctx.pause_requested_flag)
        ),
        pause_snapshot_input=snap,
        resume_context=ResumeContext(hitl_response=_hitl_result()) if with_delivery else None,
        hitl_uniform_fallback_eligible_run_id=snap.run_id if with_delivery else None,
    )


def test_linear_resume_accepts_unchanged_hitl_gate_config() -> None:
    snap = _linear_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _linear_resume(snap=snap, hitl_placements=(_PLACEMENT_A,), with_delivery=True)
    assert resumed.status is RunStatus.SUCCESS, resumed.fail_class


def test_linear_resume_rejects_hitl_gate_config_changed() -> None:
    """Mutation probe: flip `!=` to `==` (or delete the branch) at the LINEAR
    site's guard and this test fails (status flips to SUCCESS)."""
    snap = _linear_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _linear_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=True)
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "linear-resume-hitl-gate-config-changed" in resumed.fail_class


def test_linear_resume_rejects_hitl_gate_config_placement_removed() -> None:
    """codex out-of-family review [P2]: an altered-attribute test alone (timeout)
    does not prove the §1.1(b) REMOVAL-symmetry direction — a placement present
    at capture but ABSENT at resume must also reject."""
    snap = _linear_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _linear_resume(snap=snap, hitl_placements=(), with_delivery=True)
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "linear-resume-hitl-gate-config-changed" in resumed.fail_class


def test_linear_resume_skips_check_for_legacy_snapshot_with_absent_hash() -> None:
    """Mutation probe: treating `None` as a mismatch (rather than skipping) at
    the LINEAR site's guard flips this test's SUCCESS to FAILED."""
    snap = _legacy_snapshot(_linear_capture(hitl_placements=(_PLACEMENT_A,)))
    resumed = _linear_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=True)
    assert resumed.status is RunStatus.SUCCESS, (
        f"a legacy (hitl_gate_config_hash=None) snapshot must not be rejected on the "
        f"gate-config check alone; got status={resumed.status!r} "
        f"fail_class={resumed.fail_class!r}"
    )


def test_linear_resume_changed_config_with_no_delivery_pending_does_not_fail() -> None:
    """Design-correction witness: a changed config with NO delivery pending this
    cycle (no `resume_context`) must not fail the run — the check only applies
    at the point a delivery is actually about to happen."""
    snap = _linear_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _linear_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=False)
    assert resumed.status is RunStatus.SUCCESS, (
        f"no delivery pending this cycle must not be rejected on a changed gate "
        f"config; got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )


def test_linear_resume_shortened_body_fails_closed_not_indexerror() -> None:
    """out-of-family Codex [P2]: `api.resume`'s outer bounds check does not cover
    the internal `ChildWorkflowRunner` recursive-dispatch path — a workflow body
    SHORTENED between pause and resume (`resume_at >= len(steps)`) reached that
    way must return a fail-closed `RunResult`, not raise an uncaught
    `IndexError` from `steps[resume_at]` and abort the parent resume.
    Mutation probe: deleting the bounds-check block reproduces the IndexError
    (confirmed empirically against the pre-fix code — `execute_workflow` itself
    raises, so this test would ERROR rather than FAIL)."""
    snap = _linear_capture(hitl_placements=(_PLACEMENT_A,))
    manifest = _manifest(
        topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        hitl_placements=(_PLACEMENT_A,),
        workflow_id=_LINEAR_WF,
    )
    ctx = _Ctx()
    resumed = execute_workflow(
        manifest,
        [],  # SHORTENED body: resume_at (0) is now out of range for zero steps
        run_id=snap.run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _LinearDispatcher(raise_on="__never__", pause_requested_flag=ctx.pause_requested_flag)
        ),
        pause_snapshot_input=snap,
        resume_context=ResumeContext(hitl_response=_hitl_result()),
        hitl_uniform_fallback_eligible_run_id=snap.run_id,
    )
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "linear-resume-step-index-out-of-range" in resumed.fail_class


# =============================================================================
# EVALUATOR_OPTIMIZER
# =============================================================================

_EO_WF = "wf-b79-slice2-eo"
_GENERATE = "generate"
_EVALUATE = "evaluate"


class _EoDispatcher:
    def __init__(self, *, raise_on_first_call: bool, pause_requested_flag: asyncio.Event) -> None:
        self._raise_on_first_call = raise_on_first_call
        self._flag = pause_requested_flag
        self.calls = 0

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.calls += 1
        if self._raise_on_first_call and self.calls == 1:
            self._flag.set()
            raise HITLPauseRequestedSignal()
        if str(step.step_id) == _GENERATE:
            return {"draft": self.calls}
        return {"accepted": True, "feedback": "ok"}


def _eo_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID(_GENERATE), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
        WorkflowStep(
            step_id=StepID(_EVALUATE), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
    ]


def _eo_capture(*, hitl_placements: tuple[HITLPlacement, ...]) -> PauseSnapshot:
    manifest = _manifest(
        topology=TopologyPattern.EVALUATOR_OPTIMIZER,
        hitl_placements=hitl_placements,
        workflow_id=_EO_WF,
    )
    ctx = _Ctx()
    result = execute_workflow(
        manifest,
        _eo_steps(),
        run_id="run-eo-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _EoDispatcher(raise_on_first_call=True, pause_requested_flag=ctx.pause_requested_flag)
        ),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason.value == "hitl_pending"
    assert snap.hitl_gate_config_hash is not None
    return snap


def _eo_resume(
    *,
    snap: PauseSnapshot,
    hitl_placements: tuple[HITLPlacement, ...],
    with_delivery: bool,
) -> Any:
    manifest = _manifest(
        topology=TopologyPattern.EVALUATOR_OPTIMIZER,
        hitl_placements=hitl_placements,
        workflow_id=_EO_WF,
    )
    ctx = _Ctx()
    return execute_workflow(
        manifest,
        _eo_steps(),
        run_id=snap.run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _EoDispatcher(raise_on_first_call=False, pause_requested_flag=ctx.pause_requested_flag)
        ),
        pause_snapshot_input=snap,
        resume_context=ResumeContext(hitl_response=_hitl_result()) if with_delivery else None,
        hitl_uniform_fallback_eligible_run_id=snap.run_id if with_delivery else None,
    )


def test_eo_resume_accepts_unchanged_hitl_gate_config() -> None:
    snap = _eo_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _eo_resume(snap=snap, hitl_placements=(_PLACEMENT_A,), with_delivery=True)
    assert resumed.status is RunStatus.SUCCESS, resumed.fail_class


def test_eo_resume_rejects_hitl_gate_config_changed() -> None:
    snap = _eo_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _eo_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=True)
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "evaluator-optimizer-resume-hitl-gate-config-changed" in resumed.fail_class


def test_eo_resume_rejects_hitl_gate_config_placement_removed() -> None:
    """codex out-of-family review [P2]: an altered-attribute test alone (timeout)
    does not prove the §1.1(b) REMOVAL-symmetry direction."""
    snap = _eo_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _eo_resume(snap=snap, hitl_placements=(), with_delivery=True)
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "evaluator-optimizer-resume-hitl-gate-config-changed" in resumed.fail_class


def test_eo_resume_skips_check_for_legacy_snapshot_with_absent_hash() -> None:
    snap = _legacy_snapshot(_eo_capture(hitl_placements=(_PLACEMENT_A,)))
    resumed = _eo_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=True)
    assert resumed.status is RunStatus.SUCCESS, (
        f"a legacy (hitl_gate_config_hash=None) snapshot must not be rejected on the "
        f"gate-config check alone; got status={resumed.status!r} "
        f"fail_class={resumed.fail_class!r}"
    )


def test_eo_resume_changed_config_with_no_delivery_pending_does_not_fail() -> None:
    """Design-correction witness (EO): proves the check is NOT hooked into the
    unconditional `_resume_body_mismatch` closure — a nested child under a
    fan-out with unaddressed siblings would otherwise wrongly FAIL here instead
    of a recoverable INERT re-pause."""
    snap = _eo_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _eo_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=False)
    assert resumed.status is RunStatus.SUCCESS, (
        f"no delivery pending this cycle must not be rejected on a changed gate "
        f"config; got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )


# =============================================================================
# DECENTRALIZED_HANDOFF
# =============================================================================

_DH_WF = "wf-b79-slice2-dh"


class _DhDispatcher:
    def __init__(self, *, raise_on: str, pause_requested_flag: asyncio.Event) -> None:
        self._raise_on = raise_on
        self._flag = pause_requested_flag

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == self._raise_on:
            self._raise_on = "__never__"
            self._flag.set()
            raise HITLPauseRequestedSignal()
        return {"role": step_id}


def _dh_stages() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("stage0"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
        WorkflowStep(
            step_id=StepID("stage1"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
    ]


def _dh_capture(*, hitl_placements: tuple[HITLPlacement, ...]) -> PauseSnapshot:
    manifest = _manifest(
        topology=TopologyPattern.DECENTRALIZED_HANDOFF,
        hitl_placements=hitl_placements,
        workflow_id=_DH_WF,
    )
    ctx = _Ctx()
    result = execute_workflow(
        manifest,
        _dh_stages(),
        run_id="run-dh-1",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _DhDispatcher(raise_on="stage0", pause_requested_flag=ctx.pause_requested_flag)
        ),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason.value == "hitl_pending"
    assert snap.hitl_gate_config_hash is not None
    return snap


def _dh_resume(
    *,
    snap: PauseSnapshot,
    hitl_placements: tuple[HITLPlacement, ...],
    with_delivery: bool,
) -> Any:
    manifest = _manifest(
        topology=TopologyPattern.DECENTRALIZED_HANDOFF,
        hitl_placements=hitl_placements,
        workflow_id=_DH_WF,
    )
    ctx = _Ctx()
    return execute_workflow(
        manifest,
        _dh_stages(),
        run_id=snap.run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            _DhDispatcher(raise_on="__never__", pause_requested_flag=ctx.pause_requested_flag)
        ),
        pause_snapshot_input=snap,
        resume_context=ResumeContext(hitl_response=_hitl_result()) if with_delivery else None,
        hitl_uniform_fallback_eligible_run_id=snap.run_id if with_delivery else None,
    )


def test_dh_resume_accepts_unchanged_hitl_gate_config() -> None:
    snap = _dh_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _dh_resume(snap=snap, hitl_placements=(_PLACEMENT_A,), with_delivery=True)
    assert resumed.status is RunStatus.SUCCESS, resumed.fail_class


def test_dh_resume_rejects_hitl_gate_config_changed() -> None:
    snap = _dh_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _dh_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=True)
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "decentralized-handoff-resume-hitl-gate-config-changed" in resumed.fail_class


def test_dh_resume_rejects_hitl_gate_config_placement_removed() -> None:
    """codex out-of-family review [P2]: an altered-attribute test alone (timeout)
    does not prove the §1.1(b) REMOVAL-symmetry direction."""
    snap = _dh_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _dh_resume(snap=snap, hitl_placements=(), with_delivery=True)
    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class is not None
    assert "decentralized-handoff-resume-hitl-gate-config-changed" in resumed.fail_class


def test_dh_resume_skips_check_for_legacy_snapshot_with_absent_hash() -> None:
    snap = _legacy_snapshot(_dh_capture(hitl_placements=(_PLACEMENT_A,)))
    resumed = _dh_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=True)
    assert resumed.status is RunStatus.SUCCESS, (
        f"a legacy (hitl_gate_config_hash=None) snapshot must not be rejected on the "
        f"gate-config check alone; got status={resumed.status!r} "
        f"fail_class={resumed.fail_class!r}"
    )


def test_dh_resume_changed_config_with_no_delivery_pending_does_not_fail() -> None:
    snap = _dh_capture(hitl_placements=(_PLACEMENT_A,))
    resumed = _dh_resume(snap=snap, hitl_placements=(_PLACEMENT_B,), with_delivery=False)
    assert resumed.status is RunStatus.SUCCESS, (
        f"no delivery pending this cycle must not be rejected on a changed gate "
        f"config; got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )


# =============================================================================
# Byte-compat: a pre-existing (hitl_gate_config_hash-absent) snapshot's hash
# =============================================================================


def test_compute_snapshot_hash_unaffected_when_hitl_gate_config_hash_none() -> None:
    """A snapshot computed WITHOUT ever passing `hitl_gate_config_hash` (the
    pre-delta call shape) must hash byte-identically to one that explicitly
    passes `hitl_gate_config_hash=None` — proving the new param is additive-only
    per the "add to canonical dict ONLY when not None" discipline every sibling
    carrier already follows."""
    summary = _summary()
    without = _compute_snapshot_hash(
        workflow_id="wf", run_id="run", step_index=0, state_summary=summary
    )
    with_none = _compute_snapshot_hash(
        workflow_id="wf",
        run_id="run",
        step_index=0,
        state_summary=summary,
        hitl_gate_config_hash=None,
    )
    assert without == with_none
    with_value = _compute_snapshot_hash(
        workflow_id="wf",
        run_id="run",
        step_index=0,
        state_summary=summary,
        hitl_gate_config_hash="deadbeef",
    )
    assert with_value != without

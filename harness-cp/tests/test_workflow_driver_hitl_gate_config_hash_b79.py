"""B-79 impl leg slice 1 — CP spec v1.110 §1.2 property 7: a resumed pre-dispatch
gate-owning branch's APPLICABLE HITL gate configuration MUST be validated unchanged
between pause and resume at the fan-out closure's pre-dispatch-gate-owning delivery
site (`_execute_parallelization` + `_execute_orchestrator_workers`, the latter
covering `HIERARCHICAL_DELEGATION` via its recursive reuse per the B-72 precedent).

`PreDispatchGateOwningBranchResumeState` gains ONE new REQUIRED field,
`hitl_gate_config_hash` — a sha256 hex digest over the ADD-only-folded applicable
`HITLPlacement` tuple (`fold_step_hitl_placements(manifest_entry.hitl_placements,
binding.hitl_placement)`) plus the per-step `removed_placements` directive
(`binding.removed_placements`) — mirroring `step_id`/`step_kind`/`child_workflow_id`'s
own material-diff identity guard shape. Slice 2 (the LINEAR/EVALUATOR_OPTIMIZER/
DECENTRALIZED_HANDOFF net-new carrier) is a separate follow-on arc.

This module tests:

  1. `_hash_hitl_gate_config` (pure canonicalization) in isolation — the five
     discrimination witnesses §1.1(a) requires (position, tool_filter,
     cascade_policy, timeout, removed_placements each changed ALONE must
     discriminate), plus §1.1(b) symmetry (an ADDED placement rejects; a REMOVED
     placement rejects), plus determinism (identical inputs → identical hash;
     `removed_placements` frozenset-order-independence).
  2. `_execute_parallelization`'s actual resume-side rejection/acceptance, via
     `execute_workflow`'s real pause → resume round trip — mirroring
     `test_workflow_driver_parallelization_pause.py`'s own
     `test_peer_resume_rejects_pre_dispatch_gate_owning_kind_changed` shape.
  3. `_execute_orchestrator_workers`'s twin guard (proves the second wiring site,
     not just the pure function).
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

from harness_core import PersonaTier, StepID, WorkloadClass
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind, LoosenablePlacementKind
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import PauseSnapshot
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import CascadePolicy, TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    _hash_hitl_gate_config,
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import StepOverride, WorkflowManifestEntry
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b79-slice1")
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # → cascade_policy = pause
_ANCHOR = "0" * 64

_BASE_PLACEMENT = HITLPlacement(
    position=HITLPlacementKind.PRE_ACTION,
    tool_filter=("read_file", "write_file"),
    cascade_policy=CascadePolicy.PAUSE,
    timeout=5000,
)


class HITLPauseRequestedSignal(BaseException):
    """Test-local stand-in for the runtime `hitl_gate_composer.HITLPauseRequestedSignal`
    — a `BaseException`, name-matched by the driver (harness-cp cannot import
    harness-runtime), mirroring `test_workflow_driver_parallelization_pause.py`'s
    own stand-in of the same name."""


def _manifest(
    *,
    hitl_placements: tuple[HITLPlacement, ...] = (),
    per_step_overrides: dict[StepID, StepOverride] | None = None,
    workflow_id: str = "wf-b79",
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PAUSE_TIER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=hitl_placements,
        per_step_overrides=per_step_overrides or {},
    )


def _peer_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("branch-0"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 0},
        ),
        WorkflowStep(
            step_id=StepID("branch-1-inf"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"prompt": "hi"},
        ),
    ]


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
    return (
        StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        _ANCHOR,
    )


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


class _CtxP:
    def __init__(self, *, ledger: Any, emitter: _Emitter) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = _protocol()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


def _ctx() -> DriverContext:
    return cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))


class _DeclarativeDispatcher:
    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        return {"role": str(step.step_id), "echoed": dict(step.step_payload)}


class _PreDispatchGateOnceDispatcher:
    """Raises `HITLPauseRequestedSignal` on the FIRST `INFERENCE_STEP` dispatch
    only; every subsequent call (the resume re-dispatch) succeeds — the
    "unchanged resume succeeds" shape, mirroring
    `test_workflow_driver_parallelization_pause.py`'s
    `_PreDispatchGateOnInferenceStepDispatcher`."""

    def __init__(self) -> None:
        self._raised = False

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.INFERENCE_STEP:
            return cast(StepDispatcher, self)
        return cast(StepDispatcher, _DeclarativeDispatcher())

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        if not self._raised:
            self._raised = True
            raise HITLPauseRequestedSignal()
        return {"role": str(step.step_id), "echoed": dict(step.step_payload)}


class _PreDispatchGateAlwaysDispatcher:
    """Raises `HITLPauseRequestedSignal` on EVERY `INFERENCE_STEP` dispatch — for
    tests where the resume is expected to be rejected before ever reaching a
    second dispatch attempt."""

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.INFERENCE_STEP:
            return cast(StepDispatcher, self)
        return cast(StepDispatcher, _DeclarativeDispatcher())

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        raise HITLPauseRequestedSignal()


def _pause(manifest: WorkflowManifestEntry) -> PauseSnapshot:
    paused = execute_workflow(
        manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateAlwaysDispatcher()),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.peer_fan_out_resume is not None
    assert len(snap.peer_fan_out_resume.pre_dispatch_gate_owning_branches) == 1
    return snap


# --- 1. `_hash_hitl_gate_config` pure unit tests -----------------------------------


def test_hash_identical_inputs_yield_identical_hash() -> None:
    h1 = _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset())
    h2 = _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset())
    assert h1 == h2


def test_hash_position_alone_discriminates() -> None:
    altered = _BASE_PLACEMENT.model_copy(update={"position": HITLPlacementKind.SUB_AGENT_BOUNDARY})
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset()) != _hash_hitl_gate_config(
        (altered,), frozenset()
    )


def test_hash_tool_filter_alone_discriminates() -> None:
    altered = _BASE_PLACEMENT.model_copy(update={"tool_filter": ("read_file",)})
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset()) != _hash_hitl_gate_config(
        (altered,), frozenset()
    )


def test_hash_cascade_policy_alone_discriminates() -> None:
    altered = _BASE_PLACEMENT.model_copy(update={"cascade_policy": CascadePolicy.PROCEED})
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset()) != _hash_hitl_gate_config(
        (altered,), frozenset()
    )


def test_hash_timeout_alone_discriminates() -> None:
    """The critical "ALTERED, not just position-existence" witness — a scheme
    that only distinguishes placement-KIND presence would miss this."""
    altered = _BASE_PLACEMENT.model_copy(update={"timeout": 9000})
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset()) != _hash_hitl_gate_config(
        (altered,), frozenset()
    )


def test_hash_removed_placements_alone_discriminates() -> None:
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset()) != _hash_hitl_gate_config(
        (_BASE_PLACEMENT,), frozenset({LoosenablePlacementKind.SUB_AGENT_BOUNDARY})
    )


def test_hash_placement_added_discriminates() -> None:
    """§1.1(b) symmetry — an ADDED placement must reject, not only a removed one."""
    second = HITLPlacement(position=HITLPlacementKind.VALIDATOR_ESCALATION)
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), frozenset()) != _hash_hitl_gate_config(
        (_BASE_PLACEMENT, second), frozenset()
    )


def test_hash_placement_removed_discriminates() -> None:
    """§1.1(b) symmetry — a REMOVED placement must reject too."""
    second = HITLPlacement(position=HITLPlacementKind.VALIDATOR_ESCALATION)
    assert _hash_hitl_gate_config((_BASE_PLACEMENT, second), frozenset()) != _hash_hitl_gate_config(
        (_BASE_PLACEMENT,), frozenset()
    )


def test_hash_removed_placements_set_order_independent() -> None:
    """`removed_placements` is a `frozenset` — construction order must not affect
    the hash (the sorted-by-`.value` canonicalization)."""
    s1 = frozenset({LoosenablePlacementKind.SUB_AGENT_BOUNDARY})
    s2 = frozenset(list({LoosenablePlacementKind.SUB_AGENT_BOUNDARY}))
    assert _hash_hitl_gate_config((_BASE_PLACEMENT,), s1) == _hash_hitl_gate_config(
        (_BASE_PLACEMENT,), s2
    )


# --- 2. `_execute_parallelization` resume-side witnesses ---------------------------


def test_peer_resume_accepts_unchanged_hitl_gate_config() -> None:
    """The SAME dispatcher instance is used for both the pause call and the
    resume call — its `_raised` flag is what makes the SECOND (resume) dispatch
    of `branch-1-inf` succeed, mirroring
    `test_workflow_driver_parallelization_pause.py`'s
    `test_peer_resume_accepts_unchanged_pre_action_gated_inference_step` exactly
    (a FRESH dispatcher instance at resume would raise again on its own first
    call and produce a fresh — not rejected — re-pause, which is a different
    scenario from the one this test targets)."""
    manifest = _manifest(hitl_placements=(_BASE_PLACEMENT,))
    dispatcher = _PreDispatchGateOnceDispatcher()
    paused = execute_workflow(
        manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.peer_fan_out_resume is not None
    assert len(snap.peer_fan_out_resume.pre_dispatch_gate_owning_branches) == 1

    resumed = execute_workflow(
        manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.SUCCESS, (
        f"expected an UNCHANGED gate-config resume to succeed; got "
        f"status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )


def test_peer_resume_rejects_hitl_gate_config_timeout_altered() -> None:
    """The critical integration witness: a same-step_id, same-step_kind,
    same-child_workflow_id resume whose ONLY change is an attribute (`timeout`)
    on an EXISTING placement position must still fail closed."""
    manifest = _manifest(hitl_placements=(_BASE_PLACEMENT,))
    snap = _pause(manifest)

    altered_manifest = _manifest(
        hitl_placements=(_BASE_PLACEMENT.model_copy(update={"timeout": 9000}),)
    )
    resumed = execute_workflow(
        altered_manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateOnceDispatcher()),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "pre-dispatch-gate-owning-hitl-gate-config-changed" in (resumed.fail_class or "")


def test_peer_resume_rejects_hitl_gate_config_placement_removed() -> None:
    manifest = _manifest(hitl_placements=(_BASE_PLACEMENT,))
    snap = _pause(manifest)

    altered_manifest = _manifest(hitl_placements=())
    resumed = execute_workflow(
        altered_manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateOnceDispatcher()),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "pre-dispatch-gate-owning-hitl-gate-config-changed" in (resumed.fail_class or "")


def test_peer_resume_rejects_hitl_gate_config_removed_placements_added() -> None:
    """The per-step `removed_placements` directive (not the workflow-level
    `hitl_placements` tuple) changing alone must also reject."""
    manifest = _manifest(hitl_placements=(_BASE_PLACEMENT,))
    snap = _pause(manifest)

    altered_manifest = _manifest(
        hitl_placements=(_BASE_PLACEMENT,),
        per_step_overrides={
            StepID("branch-1-inf"): StepOverride(
                step_id=StepID("branch-1-inf"),
                removed_placements=frozenset({LoosenablePlacementKind.SUB_AGENT_BOUNDARY}),
            )
        },
    )
    resumed = execute_workflow(
        altered_manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateOnceDispatcher()),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "pre-dispatch-gate-owning-hitl-gate-config-changed" in (resumed.fail_class or "")


# --- 3. `_execute_orchestrator_workers` twin-guard witness --------------------------


def _ow_manifest(
    *, hitl_placements: tuple[HITLPlacement, ...] = (), workflow_id: str = "wf-b79-ow"
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PAUSE_TIER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.ORCHESTRATOR_WORKERS,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=hitl_placements,
        per_step_overrides={},
    )


def _ow_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-inf"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"prompt": "hi"},
        ),
    ]


def test_ow_resume_rejects_hitl_gate_config_changed() -> None:
    manifest = _ow_manifest(hitl_placements=(_BASE_PLACEMENT,))
    paused = execute_workflow(
        manifest,
        _ow_steps(),
        run_id="run-ow-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateAlwaysDispatcher()),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert len(snap.fan_out_resume.pre_dispatch_gate_owning_branches) == 1

    altered_manifest = _ow_manifest(
        hitl_placements=(_BASE_PLACEMENT.model_copy(update={"timeout": 1}),)
    )
    resumed = execute_workflow(
        altered_manifest,
        _ow_steps(),
        run_id="run-ow-1",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateOnceDispatcher()),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "pre-dispatch-gate-owning-hitl-gate-config-changed" in (resumed.fail_class or "")


def test_ow_resume_accepts_unchanged_hitl_gate_config() -> None:
    """Mirrors `test_peer_resume_accepts_unchanged_hitl_gate_config`'s shared-
    dispatcher-instance shape."""
    manifest = _ow_manifest(hitl_placements=(_BASE_PLACEMENT,))
    dispatcher = _PreDispatchGateOnceDispatcher()
    paused = execute_workflow(
        manifest,
        _ow_steps(),
        run_id="run-ow-2",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None

    resumed = execute_workflow(
        manifest,
        _ow_steps(),
        run_id="run-ow-2",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.SUCCESS, (
        f"expected an UNCHANGED gate-config resume to succeed; got "
        f"status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )

"""B-FANOUT-PAUSE (R-FS-1) — resumable `cascade_policy=pause` fan-out.

Materializes the cleared CP spec §25.15.1 `pause → PAUSED` row ("composes with
C-CP-26 PauseResumeProtocol + C-RT-35 `api.resume`") for the `ORCHESTRATOR_WORKERS`
fan-out, flipping the interim `class_3_fanout_pause_resume_not_yet_materialized`
deviation (FAILED + `not-yet-materialized`) to a genuine resumable PAUSED.

The honest bar (the interim foreclosed a FALSE-`PAUSED`): a PAUSED is returned
ONLY when a `pause_resume_protocol` is bound so a `FanOutResumeState`-bearing
`PauseSnapshot` can actually be captured, and `api.resume` (via the real
`execute_workflow(pause_snapshot_input=...)` entry-point resume detection — the
exact path the runtime `api.resume` drives) genuinely re-enters the strategy:
terminal branches are SKIPPED (§25.15.2 obligation 7, outputs recovered), the
not-yet-dispatched ones re-dispatched.

The completed-branch OUTPUT recovery is the materialization of the R-CC-1 design
§1.1 re-open trigger (the ledger carries causality + `terminal_status`, NOT the
dispatch output) — carried in the snapshot, COVERED by `snapshot_hash`.

Authority: `Spec_Control_Plane_v1_32.md` §25.15.1 + §25.15.2 obl. 7;
`pause_resume_protocol_types.py` C-CP-26 (FanOutResumeState / PauseSnapshot);
`.harness/class_3_fanout_pause_resume_not_yet_materialized.md` (closed by this arc).
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any, cast

import pytest
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
from harness_cp.pause_resume_protocol import PauseResumeProtocol, _compute_snapshot_hash
from harness_cp.pause_resume_protocol_types import (
    EffectFencePausedBranchResumeState,
    EffectFenceResolution,
    FanOutBranchResumeState,
    FanOutResumeState,
    OrchestratorEffectFencePausedResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_dispatch_capacity_authority import DefaultCapacityAuthority
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    compute_effect_fence_uniform_fallback_eligible_key,
    compute_hitl_uniform_fallback_eligible_run_id,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
    SubAgentChildPausedError,
    WorkflowStep,
)
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-fanout-pause")
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # → cascade_policy = pause
_ANCHOR = "0" * 64  # constant MVP pause-context anchor (no material diff on resume)


def _manifest(
    workflow_id: str = "wf-fp",
    _topology: TopologyPattern = TopologyPattern.ORCHESTRATOR_WORKERS,
    persona_tier: PersonaTier = _PAUSE_TIER,
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=_topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _steps(n_workers: int) -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        *(
            WorkflowStep(
                step_id=StepID(f"worker-{i}"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={"index": i},
            )
            for i in range(n_workers)
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
    """MVP constant-sentinel reader (mirrors the runtime factory): empty
    StateSummary + a constant anchor → resume detects no material diff → admits."""
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
    """Driver context WITH a bound `pause_resume_protocol` (the pause/resume
    opt-in) so the fan-out `pause` branch can capture a snapshot + return PAUSED,
    and `execute_workflow(pause_snapshot_input=...)` entry-point resume detection
    can validate + admit a resume."""

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


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is not StepKind.DECLARATIVE_STEP:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    return cast(StepDispatcherRegistry, _Registry(dispatcher))


class _CountingDispatcher:
    """Echoes `{step_id, payload}`; records every dispatched step_id (so a resume
    can assert which branches were re-dispatched vs terminal-skipped). A step_id
    in `fail_step_ids` raises (the cascade trigger)."""

    def __init__(self, *, fail_step_ids: set[str] | None = None) -> None:
        self._fail = fail_step_ids or set()
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id in self._fail:
            raise RuntimeError(f"simulated worker failure at {step_id}")
        return {"role": step_id, "echoed": dict(step.step_payload)}


class _GatedFailDispatcher:
    """Forces a DETERMINISTIC all-terminal pause: worker-0 completes cleanly and
    sets a gate; worker-1 waits on that gate THEN fails. So both branches reach a
    terminal disposition (worker-0 `completed`+output / worker-1 ran-and-errored
    `completed`/no-output) BEFORE the barrier resolves — no not-yet-dispatched
    (cancelled) branch, no timing race. The orchestrator returns immediately."""

    def __init__(self) -> None:
        self._gate = threading.Event()
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        if step_id == "worker-0":
            self._gate.set()
            return {"role": "worker-0", "echoed": dict(step.step_payload)}
        # worker-1: wait until worker-0 has completed, then fail (the trigger).
        assert self._gate.wait(timeout=10.0), "worker-0 never completed"
        raise RuntimeError("simulated worker-1 failure (after worker-0 completed)")


class _SynthDispatcher:
    """B-FANOUT-PAUSE-SYNTHESIS — handles the orchestrator + worker branches
    (`DECLARATIVE_STEP`) AND the terminal `POST_JOIN_SYNTHESIS` step (returning a
    DISTINCT `{synthesized, from}` marker so a test can prove the run's aggregate is the
    SYNTHESIZED output, NOT the deterministic orchestrator+workers fold). Records every
    dispatched step_id."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step.step_kind is StepKind.POST_JOIN_SYNTHESIS:
            siblings = tuple(
                sid for sid, _ in (getattr(step_context, "sibling_outputs", None) or ())
            )
            return {"synthesized": True, "from": siblings}
        return {"role": step_id, "echoed": dict(step.step_payload)}


class _SynthRegistry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind not in (StepKind.DECLARATIVE_STEP, StepKind.POST_JOIN_SYNTHESIS):
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _synthesis_step(step_id: str = "synthesis") -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(step_id),
        step_kind=StepKind.POST_JOIN_SYNTHESIS,
        step_payload={"messages": [], "params": {"max_tokens": 64}},
    )


def _run(
    *,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    ctx: DriverContext,
    pause_snapshot_input: PauseSnapshot | None = None,
    workflow_id: str = "wf-fp",
    topology: TopologyPattern = TopologyPattern.ORCHESTRATOR_WORKERS,
    persona_tier: PersonaTier = _PAUSE_TIER,
    resume_context: Any = None,
    effect_fence_uniform_fallback_eligible_key: str | None = None,
) -> Any:
    return execute_workflow(
        _manifest(workflow_id, topology, persona_tier),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
        pause_snapshot_input=pause_snapshot_input,
        resume_context=resume_context,
        effect_fence_uniform_fallback_eligible_key=effect_fence_uniform_fallback_eligible_key,
    )


# ---------------------------------------------------------------------------
# Capture — a real fan-out pause returns PAUSED + a fan-out-aware snapshot
# ---------------------------------------------------------------------------


def test_pause_with_protocol_returns_paused_with_fan_out_snapshot() -> None:
    """TEAM persona → pause, protocol bound: worker-1 fails (after worker-0
    completes) → the run PAUSES (not the interim FAILED) with a hash-valid
    `PauseSnapshot` carrying a `FanOutResumeState` (orchestrator output recovered;
    the terminal branches + worker-0's recovered output)."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=_GatedFailDispatcher(), ctx=ctx)

    assert result.status is RunStatus.PAUSED
    assert result.fail_class is None
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    fr = snap.fan_out_resume
    assert fr.worker_count == 2
    assert fr.orchestrator_output == {"role": "orchestrator"}
    # worker-0 completed cleanly → terminal + its output recovered into the snapshot.
    by_index = {b.branch_index: b for b in fr.branches}
    assert by_index[0].terminal_status == "completed"
    assert by_index[0].step_id == "worker-0"  # identity captured for resume validation
    assert by_index[0].output == {"role": "worker-0", "echoed": {"index": 0}}
    # worker-1 ran-and-errored → terminal `completed` (dispatch-boundary), no output.
    assert by_index[1].terminal_status == "completed"
    assert by_index[1].step_id == "worker-1"
    assert by_index[1].output is None
    # The snapshot is hash-valid (covers fan_out_resume).
    assert snap.snapshot_hash == _compute_snapshot_hash(
        workflow_id=snap.workflow_id,
        run_id=snap.run_id,
        step_index=snap.step_index,
        state_summary=snap.state_summary,
        fan_out_resume=fr,
    )


def test_pause_emits_resumption_not_workflow_start_on_resume() -> None:
    """The resume envelope emits RESUMPTION (the orchestrator + terminal workers
    already ran in the original envelope), not a second WORKFLOW_START."""
    emitter = _Emitter()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=emitter))
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator"},
            orchestrator_step_id="orchestrator",
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="worker-0",
                    terminal_status="completed",
                    output={"role": "worker-0"},
                ),
            ),
            worker_count=2,
        )
    )
    _run(
        steps=_steps(2),
        dispatcher=_CountingDispatcher(),
        ctx=ctx,
        pause_snapshot_input=snapshot,
    )
    assert WorkflowEventClass.RESUMPTION in emitter.emits
    assert WorkflowEventClass.WORKFLOW_START not in emitter.emits


# ---------------------------------------------------------------------------
# Resume — the real `execute_workflow(pause_snapshot_input=...)` witness
# ---------------------------------------------------------------------------


def _captured_snapshot(
    *, fan_out_resume: FanOutResumeState, workflow_id: str = "wf-fp"
) -> PauseSnapshot:
    """A hash-valid fan-out snapshot, captured through the real protocol (NOT a
    hand-mutated model) — the exact shape a prior `pause` halt would produce."""
    return asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id=workflow_id,
            run_id="run-1",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            fan_out_resume=fan_out_resume,
        )
    )


def test_resume_skips_terminal_recovers_outputs_and_redispatches_rest() -> None:
    """THE WITNESS — through the real `execute_workflow(pause_snapshot_input=...)`
    entry-point resume detection (the path `api.resume` drives):
      (1) the terminal branch (worker-0) is NOT re-dispatched (obligation 7),
      (2) the not-yet-dispatched branch (worker-1) IS re-dispatched,
      (3) the orchestrator is NOT re-dispatched (recovered),
      (4) the aggregate fuses the RECOVERED worker-0 output + the FRESH worker-1
          output + the recovered orchestrator output → SUCCESS."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator", "recovered": True},
            orchestrator_step_id="orchestrator",
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="worker-0",
                    terminal_status="completed",
                    output={"role": "worker-0", "recovered": True},
                ),
            ),  # worker-1 ABSENT → left re-dispatchable
            worker_count=2,
        )
    )
    dispatcher = _CountingDispatcher()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=dispatcher, ctx=ctx, pause_snapshot_input=snapshot)

    assert result.status is RunStatus.SUCCESS
    # (1)+(3): the terminal worker-0 + the orchestrator were NOT re-dispatched.
    assert "worker-0" not in dispatcher.dispatched
    assert "orchestrator" not in dispatcher.dispatched
    # (2): only the re-dispatchable worker-1 ran on resume.
    assert dispatcher.dispatched == ["worker-1"]
    # (4): the aggregate fuses recovered (orchestrator + worker-0) + fresh (worker-1).
    assert result.final_state is not None
    assert result.final_state["orchestrator"] == {"role": "orchestrator", "recovered": True}
    assert result.final_state["worker_outputs"]["worker-0"] == {
        "role": "worker-0",
        "recovered": True,
    }
    assert result.final_state["worker_outputs"]["worker-1"] == {
        "role": "worker-1",
        "echoed": {"index": 1},
    }


def test_resume_all_terminal_with_a_failed_branch_is_partial_not_silent_success() -> None:
    """Real pause → real resume round-trip (the GatedFail all-terminal pause):
    both workers terminal at pause (worker-0 completed, worker-1 FAILED) → resume
    re-dispatches NOTHING and surfaces **PARTIAL** (degraded), NOT a bare silent
    SUCCESS dropping the failure — the silent-degradation class this arc forecloses
    (advisor [P1]; mirrors the `proceed`-cascade `any_failed → PARTIAL`). worker-0's
    output is recovered; the failed worker-1 contributes nothing + is not re-fired
    (obligation 7 + at-most-once)."""
    pause_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = _run(steps=_steps(2), dispatcher=_GatedFailDispatcher(), ctx=pause_ctx)
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None

    resume_dispatcher = _CountingDispatcher()
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2),
        dispatcher=resume_dispatcher,
        ctx=resume_ctx,
        pause_snapshot_input=snapshot,
    )
    # A recovered branch FAILED → degraded → PARTIAL (not silent SUCCESS).
    assert result.status is RunStatus.PARTIAL
    # Both branches were terminal at pause → NOTHING re-dispatched on resume.
    assert resume_dispatcher.dispatched == []
    # The salvaged aggregate is on partial_state; worker-0 recovered, worker-1 gone.
    assert result.partial_state is not None
    assert "worker-0" in result.partial_state["worker_outputs"]
    assert "worker-1" not in result.partial_state["worker_outputs"]


# ---------------------------------------------------------------------------
# Negative controls + integrity + backward-compat
# ---------------------------------------------------------------------------


def test_snapshot_hash_covers_fan_out_resume_tamper_rejected() -> None:
    """Integrity: a snapshot whose recovered branch output is TAMPERED (without
    re-hashing) is REJECTED at resume → FAILED + CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION
    (no silent-tamper gap on the data the resumed aggregate trusts)."""
    good = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator"},
            orchestrator_step_id="orchestrator",
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="worker-0",
                    terminal_status="completed",
                    output={"amount": 100},
                ),
            ),
            worker_count=2,
        )
    )
    # Tamper the recovered output, keeping the STALE hash → corruption.
    tampered = good.model_copy(
        update={
            "fan_out_resume": good.fan_out_resume.model_copy(  # type: ignore[union-attr]
                update={
                    "branches": (
                        FanOutBranchResumeState(
                            branch_index=0,
                            step_id="worker-0",
                            terminal_status="completed",
                            output={"amount": 999999},
                        ),
                    )
                }
            )
        }
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=tampered
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION"


def test_negative_control_empty_branches_loses_recovery() -> None:
    """Persistence is load-bearing: a snapshot whose `branches` is EMPTY (no
    recovered worker-0 output) re-dispatches BOTH workers and the aggregate does
    NOT contain a recovered worker-0 — proving the recovered output in the
    snapshot is what populates the aggregate, not an incidental re-run."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator", "recovered": True},
            orchestrator_step_id="orchestrator",
            branches=(),  # nothing recovered → both workers re-dispatchable
            worker_count=2,
        )
    )
    dispatcher = _CountingDispatcher()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=dispatcher, ctx=ctx, pause_snapshot_input=snapshot)
    assert result.status is RunStatus.SUCCESS
    # BOTH workers re-dispatched (no terminal skip); worker-0's output is the FRESH
    # one (no "recovered" marker), proving the recovered-output path is the only
    # source of a recovered value (vs. this incidental re-run).
    assert set(dispatcher.dispatched) == {"worker-0", "worker-1"}
    assert result.final_state is not None
    assert result.final_state["worker_outputs"]["worker-0"] == {
        "role": "worker-0",
        "echoed": {"index": 0},
    }


def test_resume_worker_count_mismatch_fails_closed() -> None:
    """Material-diff guard: a snapshot captured with worker_count=3 but resumed
    against a 2-worker body fails CLOSED (the recovered ordinals no longer map to
    these steps — a changed body) rather than re-dispatching a mismatched set."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator"},
            orchestrator_step_id="orchestrator",
            branches=(),
            worker_count=3,
        )
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=snapshot
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "resume-worker-count-mismatch" in result.fail_class


def test_linear_snapshot_hash_byte_identical_backward_compat() -> None:
    """Backward-compat: a snapshot with NO `fan_out_resume` (every linear /
    single-step pause) hashes byte-identically to the pre-B-FANOUT-PAUSE formula
    (the key is added to the canonical dict ONLY when fan_out_resume is present)
    → existing durable snapshots still validate."""
    summary = _pause_context_reader()[0]
    with_field = _compute_snapshot_hash(
        workflow_id="wf", run_id="r", step_index=0, state_summary=summary, fan_out_resume=None
    )
    legacy_canonical_hash = _compute_snapshot_hash(
        workflow_id="wf", run_id="r", step_index=0, state_summary=summary
    )
    assert with_field == legacy_canonical_hash


def test_fan_out_snapshot_survives_json_roundtrip() -> None:
    """Durable-store fidelity: the fan-out snapshot round-trips through
    model_dump(mode="json") → model_validate (the JournalWorkflowPauseStore path)
    with `fan_out_resume` intact AND the hash still valid."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator"},
            orchestrator_step_id="orchestrator",
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="worker-0",
                    terminal_status="completed",
                    output={"k": "v"},
                ),
                FanOutBranchResumeState(
                    branch_index=1, step_id="worker-1", terminal_status="timed_out", output=None
                ),
            ),
            worker_count=3,
        )
    )
    restored = PauseSnapshot.model_validate(snapshot.model_dump(mode="json"))
    assert restored == snapshot
    assert restored.fan_out_resume is not None
    assert restored.snapshot_hash == _compute_snapshot_hash(
        workflow_id=restored.workflow_id,
        run_id=restored.run_id,
        step_index=restored.step_index,
        state_summary=restored.state_summary,
        fan_out_resume=restored.fan_out_resume,
    )


# ---------------------------------------------------------------------------
# Decorrelated-review hardening — re-pause union, hierarchical gate, identity
# ---------------------------------------------------------------------------


def test_resume_redispatch_failing_worker_re_pauses_with_unioned_branches() -> None:
    """A re-dispatched worker failing AGAIN under `pause` re-PAUSES with a snapshot
    whose `branches` UNION the prior-recovered + this-round-terminal sets (advisor
    [secondary] — the re-pause claim was untested). worker-0 recovered; worker-1
    fails on re-dispatch → the new snapshot carries BOTH (worker-0's recovered
    output carried forward + worker-1 newly terminal)."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator", "recovered": True},
            orchestrator_step_id="orchestrator",
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="worker-0",
                    terminal_status="completed",
                    output={"role": "worker-0", "recovered": True},
                ),
            ),  # worker-1 + worker-2 absent → re-dispatchable
            worker_count=3,
        )
    )
    dispatcher = _CountingDispatcher(fail_step_ids={"worker-1"})
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(3), dispatcher=dispatcher, ctx=ctx, pause_snapshot_input=snapshot)

    # A re-dispatched worker failed under pause (protocol bound) → re-PAUSED.
    assert result.status is RunStatus.PAUSED
    new_snap = result.pause_snapshot
    assert new_snap is not None and new_snap.fan_out_resume is not None
    by_index = {b.branch_index: b for b in new_snap.fan_out_resume.branches}
    # UNION: the prior-recovered worker-0 (carried forward, output preserved) +
    # the newly-terminal worker-1 (failed this round).
    assert 0 in by_index and 1 in by_index
    assert by_index[0].output == {"role": "worker-0", "recovered": True}
    assert by_index[1].output is None  # ran-and-errored → no output
    # worker-0 was NOT re-dispatched (terminal-skipped); worker-1 WAS (and failed).
    assert "worker-0" not in dispatcher.dispatched
    assert "worker-1" in dispatcher.dispatched


def test_hierarchical_delegation_pause_materializes_resumable_paused() -> None:
    """B-HIERARCHICAL-PAUSE (R-FS-1) — HIERARCHICAL_DELEGATION REUSES
    `_execute_orchestrator_workers` and now threads `pause_resumable=True` + the
    resume snapshot. A TEAM/pause level-local worker failure materializes a GENUINE
    resumable PAUSED (the interim `...-not-yet-materialized` FAILED is RETIRED) — the
    same `FanOutResumeState` mechanism ORCHESTRATOR_WORKERS uses, now wired for the
    recursion-heavy topology. A resume round-trip completes (worker-0's terminal is
    skipped, the re-dispatchable worker re-runs)."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2),
        dispatcher=_GatedFailDispatcher(),
        ctx=ctx,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
    )
    assert result.status is RunStatus.PAUSED
    assert result.fail_class is None
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert snap.fan_out_resume.worker_count == 2
    # No recursive child paused here (level-local worker pause) → empty.
    assert snap.fan_out_resume.paused_child_branches == ()
    # Hash-valid (covers fan_out_resume).
    assert snap.snapshot_hash == _compute_snapshot_hash(
        workflow_id=snap.workflow_id,
        run_id=snap.run_id,
        step_index=snap.step_index,
        state_summary=snap.state_summary,
        fan_out_resume=snap.fan_out_resume,
    )
    # Resume round-trip: HIERARCHICAL re-enters with the snapshot + a clean dispatcher.
    ctx2 = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = _run(
        steps=_steps(2),
        dispatcher=_CountingDispatcher(),
        ctx=ctx2,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
        pause_snapshot_input=snap,
    )
    assert resumed.status is not RunStatus.PAUSED
    assert resumed.status in (RunStatus.SUCCESS, RunStatus.PARTIAL)


def test_resume_body_identity_mismatch_fails_closed() -> None:
    """Codex [P1] — a valid (same worker_count) snapshot whose recovered branch
    `step_id` does NOT match the re-supplied body (a worker rename / reorder) fails
    CLOSED rather than silently attributing the recovered output to the wrong step.
    The hash is valid (captured for the renamed id), so this is caught by the
    in-strategy identity guard, not the snapshot_hash."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator"},
            orchestrator_step_id="orchestrator",
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="renamed-worker",  # the body has "worker-0" at index 0
                    terminal_status="completed",
                    output={"stale": True},
                ),
            ),
            worker_count=2,
        )
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=snapshot
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "branch-identity-mismatch" in result.fail_class


def test_pause_captures_in_flight_sibling_completed_output() -> None:
    """Codex [P1] — a sibling IN-FLIGHT when the barrier cancels it (because
    another worker failed) runs to completion under the shield; its successful
    OUTPUT must be captured into the snapshot (else resume skips it as terminal +
    drops the output). worker-0 is mid-dispatch (a brief sleep) when worker-1
    fails → worker-0 completes under the shield → its output is recovered."""
    import time

    class _InFlightCompletesDispatcher:
        def __init__(self) -> None:
            self._started = threading.Event()

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            sid = str(step.step_id)
            if sid == "orchestrator":
                return {"role": "orchestrator"}
            if sid == "worker-0":
                self._started.set()
                time.sleep(0.05)  # in-flight when worker-1 fails; completes under the shield
                return {"role": "worker-0", "in_flight_completed": True}
            assert self._started.wait(timeout=10.0), "worker-0 never started"
            raise RuntimeError("worker-1 fails while worker-0 is in-flight")

    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=_InFlightCompletesDispatcher(), ctx=ctx)

    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    by_index = {b.branch_index: b for b in snap.fan_out_resume.branches}
    # worker-0 was cancelled-but-completed → terminal `completed` WITH its output
    # captured (the fix); without it `output` would be None and resume would drop it.
    assert by_index[0].terminal_status == "completed"
    assert by_index[0].output == {"role": "worker-0", "in_flight_completed": True}


def test_resume_orchestrator_identity_mismatch_fails_closed() -> None:
    """Codex [P2] — the orchestrator's output is recovered + its dispatch skipped,
    so a snapshot whose `orchestrator_step_id` does NOT match the re-supplied
    `steps[0]` (a renamed/reordered orchestrator, same worker shape) fails CLOSED
    rather than applying stale orchestrator output to a different body."""
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator", "stale": True},
            orchestrator_step_id="renamed-orchestrator",  # body has "orchestrator"
            branches=(),
            worker_count=2,
        )
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=snapshot
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "orchestrator-identity-mismatch" in result.fail_class


# ---------------------------------------------------------------------------
# B-HIERARCHICAL-PAUSE (R-FS-1) — recursive child PAUSE: capture + resume re-entry.
#
# The discriminating full-chain witness (`[[full-chain-witness-not-half-proofs]]`):
# a grandchild step that COMPLETED before the child paused is NOT re-executed when
# the parent resumes — the child re-enters at ITS cursor (counter == 1), NOT a fresh
# re-dispatch (which would make counter == 2). The child is a REAL recursive
# `execute_workflow` fan-out; only the SUB_AGENT_DISPATCH dispatcher is a faithful
# double of `RuntimeSubAgentDispatcher` (raise SubAgentChildPausedError on a child
# PAUSED + forward `step_context.child_resume_snapshot` as the child's
# `pause_snapshot_input`) — that runtime seam is unit-proven in
# `harness-runtime/tests/test_lifecycle_sub_agent_dispatch.py`. The INFERENCE-child
# real-provider e2e is blocked by a pre-existing runtime sync/async deadlock
# (`.harness/runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md`), so
# this declarative-only witness is the non-deadlocking proof of the recursion.
# ---------------------------------------------------------------------------

# Mutable holder (a list, not an ALL_CAPS module constant — pyright would flag a
# reassigned ALL_CAPS name as reportConstantRedefinition; Codex [P1]).
_grandchild0_dispatches = [0]


class _GrandchildDispatcher:
    """Child fan-out grandchild dispatcher: grandchild-0 completes (incrementing a
    module counter + setting a gate); grandchild-1 waits then FAILS → the child fan-out
    PAUSES with grandchild-0 terminal+recovered. Deterministic (the _GatedFailDispatcher
    shape)."""

    def __init__(self) -> None:
        self._gate = threading.Event()

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        if sid == "child-orch":
            return {"role": "child-orch"}
        if sid == "grandchild-0":
            _grandchild0_dispatches[0] += 1
            self._gate.set()
            return {"role": "grandchild-0", "done": True}
        assert self._gate.wait(timeout=10.0), "grandchild-0 never completed"
        raise RuntimeError("grandchild-1 fails (after grandchild-0 completed) → child pauses")


def _child_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("child-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "child-orch"},
        ),
        WorkflowStep(
            step_id=StepID("grandchild-0"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 0},
        ),
        WorkflowStep(
            step_id=StepID("grandchild-1"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 1},
        ),
    ]


class _FaithfulSubAgentDispatcher:
    """A faithful double of `RuntimeSubAgentDispatcher` for the B-HIERARCHICAL-PAUSE
    seam: dispatches a REAL child `execute_workflow`, reading
    `step_context.child_resume_snapshot` to thread the child's resume snapshot (so a
    resumed child re-enters at its cursor), and RAISING `SubAgentChildPausedError`
    (carrying the child's PauseSnapshot) when the child returns PAUSED — exactly what
    the runtime dispatcher does at `sub_agent_dispatch.py`."""

    def __init__(self, *, child_dispatcher: _GrandchildDispatcher) -> None:
        self._child_dispatcher = child_dispatcher
        self.child_calls = 0
        self.received_resume: list[Any] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.child_calls += 1
        child_resume = getattr(step_context, "child_resume_snapshot", None)
        self.received_resume.append(child_resume)
        child_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
        child_result = execute_workflow(
            _manifest("wf-child", TopologyPattern.ORCHESTRATOR_WORKERS),
            _child_steps(),
            run_id="child-run",
            ctx=child_ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=_registry(self._child_dispatcher),
            pause_snapshot_input=child_resume,
        )
        if child_result.status is RunStatus.PAUSED:
            assert child_result.pause_snapshot is not None
            raise SubAgentChildPausedError(
                child_workflow_id="wf-child", child_snapshot=child_result.pause_snapshot
            )
        # SUCCESS / PARTIAL / DRAINED → success-equivalent (mirrors the dispatcher's
        # non-FAILED, non-PAUSED handling): return the child's state as the worker output.
        return dict(child_result.final_state or child_result.partial_state or {})


class _ParentRegistry:
    """Routes DECLARATIVE_STEP (the parent orchestrator) to a simple echo and
    SUB_AGENT_DISPATCH (the recursive worker) to the faithful sub-agent double."""

    def __init__(self, *, sub_agent: _FaithfulSubAgentDispatcher) -> None:
        self._sub_agent = sub_agent
        self._echo = _CountingDispatcher()

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agent)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)


def _parent_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("parent-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "parent-orch"},
        ),
        WorkflowStep(
            step_id=StepID("sub-worker"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child"},
        ),
    ]


def test_hierarchical_child_pause_resume_does_not_reexecute_grandchild() -> None:
    """THE discriminating witness — a grandchild completed INSIDE the child before the
    pause is NOT re-executed on resume (the child re-enters at its cursor, not fresh).

    First run: parent HIERARCHICAL → SUB_AGENT worker → REAL child fan-out; grandchild-0
    completes (counter → 1), grandchild-1 fails → child PAUSES → the worker raises
    SubAgentChildPausedError → the parent captures the child's snapshot into
    `paused_child_branches` + PAUSES. Resume: the parent re-dispatches the worker WITH
    the child snapshot → the child re-enters at its cursor → grandchild-0 is
    terminal-skipped (counter STAYS 1), proving non-re-execution. A broken re-entry
    (re-dispatch fresh) would make counter == 2."""
    _grandchild0_dispatches[0] = 0
    child_dispatcher = _GrandchildDispatcher()
    sub_agent = _FaithfulSubAgentDispatcher(child_dispatcher=child_dispatcher)
    parent_registry = cast(StepDispatcherRegistry, _ParentRegistry(sub_agent=sub_agent))

    # ---- First run: parent pauses on the recursive child PAUSE.
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION),
        _parent_steps(),
        run_id="parent-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=parent_registry,
    )
    assert paused.status is RunStatus.PAUSED, f"parent must pause; got {paused.status}"
    assert _grandchild0_dispatches[0] == 1, "grandchild-0 ran exactly once on the first pass"
    snap = paused.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    pcb = snap.fan_out_resume.paused_child_branches
    assert len(pcb) == 1, "the SUB_AGENT worker's child paused → exactly one paused-child branch"
    assert pcb[0].step_id == "sub-worker"
    # The captured child_snapshot is the child fan-out's own resumable snapshot.
    assert pcb[0].child_snapshot.fan_out_resume is not None
    # Hash covers the nested child cursor (a tampered child snapshot fails parent resume).
    assert snap.snapshot_hash == _compute_snapshot_hash(
        workflow_id=snap.workflow_id,
        run_id=snap.run_id,
        step_index=snap.step_index,
        state_summary=snap.state_summary,
        fan_out_resume=snap.fan_out_resume,
    )

    # ---- Resume: the child re-enters at its cursor — grandchild-0 is NOT re-executed.
    ctx2 = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION),
        _parent_steps(),
        run_id="parent-run",
        ctx=ctx2,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=parent_registry,
        pause_snapshot_input=snap,
    )
    assert resumed.status is not RunStatus.PAUSED
    # THE load-bearing assertion: the child re-entered at its cursor (terminal-skipped
    # grandchild-0), so it was NOT re-executed. Fresh re-dispatch would give 2.
    assert _grandchild0_dispatches[0] == 1, (
        f"grandchild-0 was RE-EXECUTED on resume (count={_grandchild0_dispatches[0]}) — the child "
        f"was re-dispatched FRESH instead of re-entering at its cursor (broken resume re-entry)"
    )
    # The worker WAS re-dispatched on resume (re-entry IS a dispatch, just at the cursor).
    assert sub_agent.child_calls == 2
    # Discriminating: the FIRST child dispatch got no resume snapshot (fresh); the SECOND
    # (resume) received the child's snapshot threaded via child_resume_snapshot — so the
    # non-re-execution is genuine re-entry, not a coincidental skip.
    assert sub_agent.received_resume[0] is None
    assert sub_agent.received_resume[1] is not None
    assert sub_agent.received_resume[1].fan_out_resume is not None


def test_hierarchical_resume_rejects_paused_child_workflow_id_swap() -> None:
    """B-31 — a same-step_id, same-step_kind edit that swaps the SUB_AGENT_DISPATCH
    worker's `child_workflow_id` must fail closed, symmetric with the PARALLELIZATION
    guard (`test_peer_resume_rejects_paused_child_workflow_id_swap`)."""
    _grandchild0_dispatches[0] = 0
    child_dispatcher = _GrandchildDispatcher()
    sub_agent = _FaithfulSubAgentDispatcher(child_dispatcher=child_dispatcher)
    parent_registry = cast(StepDispatcherRegistry, _ParentRegistry(sub_agent=sub_agent))

    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION),
        _parent_steps(),
        run_id="parent-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=parent_registry,
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    assert snap.fan_out_resume.paused_child_branches[0].child_workflow_id == "wf-child"

    # Resume with sub-worker's step_payload edited to target a DIFFERENT child workflow —
    # same step_id, same step_kind.
    changed_steps = [
        _parent_steps()[0],
        WorkflowStep(
            step_id=StepID("sub-worker"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-SWAPPED"},
        ),
    ]
    ctx2 = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION),
        changed_steps,
        run_id="parent-run",
        ctx=ctx2,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=parent_registry,
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "paused-child-workflow-id-changed" in (resumed.fail_class or "")


class _PausingChildDispatcher:
    """A child fan-out grandchild dispatcher whose grandchild-1 always fails → the child
    fan-out PAUSES (grandchild-0 completes terminal+output). Distinct gates per child so
    the parent's two SUB_AGENT workers pause in a controlled order."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        if sid == "child-orch" or sid == "grandchild-0":
            return {"role": sid}
        raise RuntimeError("grandchild-1 fails → child pauses")


class _OrderedPausingSubAgentDispatcher:
    """Two SUB_AGENT workers, each dispatching a REAL child fan-out that PAUSES. worker
    `sub-0` raises its SubAgentChildPausedError FIRST (sets a gate); `sub-1` waits the
    gate then raises — so worker-0's raise cancels worker-1 while worker-1's own child
    pause is draining in-flight, exercising the CANCELLATION path (Codex [P1]). Both
    paused children MUST survive into `paused_child_branches` (without the fix the
    cancelled worker-1 is recorded terminal `completed` + its snapshot DROPPED)."""

    def __init__(self) -> None:
        self._gate = threading.Event()

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        child_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
        child_result = execute_workflow(
            _manifest(f"wf-child-{sid}", TopologyPattern.ORCHESTRATOR_WORKERS),
            _child_steps(),
            run_id=f"child-run-{sid}",
            ctx=child_ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=_registry(_PausingChildDispatcher()),
        )
        assert child_result.status is RunStatus.PAUSED and child_result.pause_snapshot is not None
        if sid == "sub-0":
            self._gate.set()  # let worker-1 proceed AFTER worker-0 has its pause ready
        else:
            # worker-1: wait until worker-0 raised (→ cancels this branch) so this
            # branch's pause drains in-flight under the shield → CancelledError path.
            assert self._gate.wait(timeout=10.0)
        raise SubAgentChildPausedError(
            child_workflow_id=f"wf-child-{sid}", child_snapshot=child_result.pause_snapshot
        )


class _TwoSubAgentRegistry:
    def __init__(self, *, sub_agent: _OrderedPausingSubAgentDispatcher) -> None:
        self._sub_agent = sub_agent
        self._echo = _CountingDispatcher()

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agent)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)


def test_cancellation_race_captures_paused_child_among_failing_siblings() -> None:
    """B-HIERARCHICAL-PAUSE (Codex [P1]) — when one paused-child worker raises and the
    TaskGroup cancels a SIBLING whose own child also paused in-flight, the cancelled
    sibling's child PAUSE lands in `inflight.exception()` (the shielded drain suppresses
    it + re-raises CancelledError). Both paused children MUST survive into
    `paused_child_branches` — the cancelled one is NOT recorded as a terminal `completed`
    branch (which would drop its snapshot on resume)."""
    sub_agent = _OrderedPausingSubAgentDispatcher()
    registry = cast(StepDispatcherRegistry, _TwoSubAgentRegistry(sub_agent=sub_agent))
    parent_steps = [
        WorkflowStep(
            step_id=StepID("parent-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "parent-orch"},
        ),
        WorkflowStep(
            step_id=StepID("sub-0"), step_kind=StepKind.SUB_AGENT_DISPATCH, step_payload={}
        ),
        WorkflowStep(
            step_id=StepID("sub-1"), step_kind=StepKind.SUB_AGENT_DISPATCH, step_payload={}
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = execute_workflow(
        _manifest("wf-parent-2", TopologyPattern.HIERARCHICAL_DELEGATION),
        parent_steps,
        run_id="parent-run-2",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    pcb_indices = {p.branch_index for p in snap.fan_out_resume.paused_child_branches}
    terminal_indices = {b.branch_index for b in snap.fan_out_resume.branches}
    # BOTH paused children captured — neither lost to a terminal `completed` branch.
    assert pcb_indices == {0, 1}, (
        f"a paused child was DROPPED in the cancellation race: paused={pcb_indices}, "
        f"terminal={terminal_indices}"
    )
    assert terminal_indices.isdisjoint(pcb_indices)
    # B-32 contrasting baseline — both nested children paused for an ORDINARY
    # `cascade_policy=pause` branch failure (itself EXPLICIT_OPERATOR, not a HITL gate);
    # presence of paused children alone must NOT relabel the parent HITL_PENDING.
    assert snap.pause_reason is WorkflowPauseReason.EXPLICIT_OPERATOR


def _hitl_pending_child_pause_snapshot(workflow_id: str) -> PauseSnapshot:
    state_summary, anchor = _pause_context_reader()
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=f"{workflow_id}-run",
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=state_summary,
        snapshot_hash="a" * 64,
        created_at=1_700_000_000_000,
        state_ledger_anchor=anchor,
    )


class _SingleWorkerHITLPausingSubAgentDispatcher:
    """A single SUB_AGENT worker (no siblings, no TaskGroup race) whose recursive child's
    OWN pause_reason genuinely IS HITL_PENDING — isolates the ORCHESTRATOR_WORKERS/
    HIERARCHICAL_DELEGATION pause_reason-propagation behavior (B-32) from any
    cancellation-race timing, mirroring the PARALLELIZATION positive test in
    test_workflow_driver_parallelization_pause.py."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        raise SubAgentChildPausedError(
            child_workflow_id="wf-child-worker-0",
            child_snapshot=_hitl_pending_child_pause_snapshot("wf-child-worker-0"),
        )


class _SingleWorkerHITLRegistry:
    def __init__(self, *, sub_agent: _SingleWorkerHITLPausingSubAgentDispatcher) -> None:
        self._sub_agent = sub_agent
        self._orchestrator = _CountingDispatcher()

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agent)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._orchestrator)
        raise StepKindDispatcherNotBoundError(step_kind)


def test_orchestrator_worker_child_hitl_pending_pause_labels_parent_hitl_pending() -> None:
    """B-32 positive case (ORCHESTRATOR_WORKERS analogue of the PARALLELIZATION positive
    test) — a nested worker child whose OWN pause_reason genuinely IS HITL_PENDING labels
    the PARENT's pause HITL_PENDING too. A single-worker round (no siblings) isolates the
    pause_reason-propagation behavior from any TaskGroup cancellation-race timing.
    Mutation-probe: deleting or inverting the `_any_nested_hitl_pending` check at the
    ORCHESTRATOR_WORKERS/HIERARCHICAL_DELEGATION `_pause_reason` derivation site would
    leave this assertion failing (parent falls back to EXPLICIT_OPERATOR)."""
    registry = cast(
        StepDispatcherRegistry,
        _SingleWorkerHITLRegistry(sub_agent=_SingleWorkerHITLPausingSubAgentDispatcher()),
    )
    parent_steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0"), step_kind=StepKind.SUB_AGENT_DISPATCH, step_payload={}
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = execute_workflow(
        _manifest("wf-orch-hitl-positive"),
        parent_steps,
        run_id="run-orch-hitl-positive",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    pcb_indices = {p.branch_index for p in snap.fan_out_resume.paused_child_branches}
    assert pcb_indices == {0}, f"expected worker-0 captured as a paused child: {pcb_indices}"
    assert snap.pause_reason is WorkflowPauseReason.HITL_PENDING


# ---------------------------------------------------------------------------
# B-FANOUT-PAUSE-SYNTHESIS — synthesis-bearing ORCHESTRATOR_WORKERS pause-resume.
# (HIERARCHICAL_DELEGATION reuses `_execute_orchestrator_workers` + `FanOutResumeState`
# + the SAME `execute_workflow(pause_snapshot_input=...)` entry the child re-enters on,
# so these FanOut witnesses cover the HIERARCHICAL top-level + child-level paths too.)
# ---------------------------------------------------------------------------


def test_resume_with_matching_synthesis_fresh_dispatches_succeeds() -> None:
    """B-FANOUT-PAUSE-SYNTHESIS full-chain (ORCHESTRATOR_WORKERS) — a synthesis-bearing
    fan-out PAUSE is now RESUMABLE. The snapshot recovers the orchestrator output + carries
    the synthesis identity (`synthesis_step_id="synthesis"`); resume material-diffs it
    (match), re-dispatches the (absent) workers, then FRESH-dispatches the synthesis over
    the worker siblings post-barrier (it never ran on a pause → effect-free, first-and-only).
    Load-bearing: the aggregate is the SYNTHESIZED output (NOT the orchestrator+workers
    fold), the synthesis dispatched EXACTLY ONCE, and the orchestrator was NOT re-dispatched
    (recovered)."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator", "recovered": True},
            orchestrator_step_id="orchestrator",
            branches=(),  # both workers re-dispatchable
            worker_count=2,
            synthesis_step_id="synthesis",
        )
    )
    dispatcher = _SynthDispatcher()
    result = execute_workflow(
        _manifest(),
        [*_steps(2), _synthesis_step()],
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _SynthRegistry(dispatcher)),
        pause_snapshot_input=snapshot,
    )
    assert result.status is RunStatus.SUCCESS
    # SYNTHESIZED output, NOT the fold — `from` carries the branch-index-ordered WORKER
    # siblings (0, 1); the orchestrator (steps[0]) is NOT a sibling.
    assert result.final_state == {"synthesized": True, "from": (0, 1)}
    assert dispatcher.dispatched.count("synthesis") == 1
    # Workers re-dispatched; the orchestrator was recovered (NOT re-dispatched).
    assert {s for s in dispatcher.dispatched if s.startswith("worker")} == {
        "worker-0",
        "worker-1",
    }
    assert "orchestrator" not in dispatcher.dispatched


def test_resume_synthesis_added_fails_closed_fanout() -> None:
    """B-FANOUT-PAUSE-SYNTHESIS material-diff (ADDED, ORCHESTRATOR_WORKERS) — a snapshot
    captured WITHOUT a synthesis but resumed against a body that NOW carries one fails
    closed (the synthesis was added between pause and resume)."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    snapshot = _captured_snapshot(
        fan_out_resume=FanOutResumeState(
            orchestrator_output={"role": "orchestrator"},
            orchestrator_step_id="orchestrator",
            branches=(),
            worker_count=2,
        )
    )
    result = _run(
        steps=[*_steps(2), _synthesis_step()],
        dispatcher=_CountingDispatcher(),
        ctx=ctx,
        pause_snapshot_input=snapshot,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert result.fail_class.startswith("post-join-synthesis-resume-material-diff:")


def test_synthesis_absent_fanout_snapshot_byte_compat_hash() -> None:
    """B-FANOUT-PAUSE-SYNTHESIS byte-compat (FanOutResumeState) — a synthesis-ABSENT fan-out
    snapshot (`synthesis_step_id=None`, no `paused_child_branches`) hashes byte-identically
    to the pre-arc shape: `_compute_snapshot_hash` DROPS the `synthesis_step_id` key (next to
    the existing `paused_child_branches` drop) when None, so every old durable
    ORCHESTRATOR_WORKERS snapshot still validates."""
    import hashlib
    import json

    state_summary, _ = _pause_context_reader()
    fan = FanOutResumeState(
        orchestrator_output={"role": "orchestrator"},
        orchestrator_step_id="orchestrator",
        branches=(),
        worker_count=2,
    )  # synthesis_step_id + paused_child_branches both default-empty
    got = _compute_snapshot_hash(
        workflow_id="wf-fp",
        run_id="run-1",
        step_index=0,
        state_summary=state_summary,
        fan_out_resume=fan,
    )
    # The pre-arc canonical serialization — FanOut carrier with NEITHER `synthesis_step_id`
    # NOR `paused_child_branches` keys (both dropped when empty).
    canonical = {
        "workflow_id": "wf-fp",
        "run_id": "run-1",
        "step_index": 0,
        "state_summary": state_summary.model_dump(mode="json"),
        "fan_out_resume": {
            "orchestrator_output": {"role": "orchestrator"},
            "orchestrator_step_id": "orchestrator",
            "branches": [],
            "worker_count": 2,
        },
    }
    expected = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert got == expected


def test_paused_child_absent_workflow_id_byte_compat_hash() -> None:
    """B-31 byte-compat — a `paused_child_branches` entry captured BEFORE
    `child_workflow_id` existed (`child_workflow_id=None`, the field's default) hashes
    byte-identically to the pre-B-31 shape: `_strip_default_fanout_resume_fields` drops the
    `child_workflow_id` key (not just leaves it `null`) from that entry's `model_dump`, so
    every durable HIERARCHICAL/ORCHESTRATOR_WORKERS pause snapshot with a paused-child
    branch that predates this field still recomputes the SAME hash and validates on
    resume. Directly proves the drop-when-`None` claim at the entry level (distinct from
    the list-level `paused_child_branches` empty-drop `test_synthesis_absent_fanout_
    snapshot_byte_compat_hash` already covers) — a `paused_child_branches` list that is
    NON-empty but whose sole entry omits `child_workflow_id`."""
    import hashlib
    import json

    state_summary, _ = _pause_context_reader()
    child_state_summary, child_anchor = _pause_context_reader()
    child_snap = PauseSnapshot(
        workflow_id="wf-child",
        run_id="child-run",
        step_index=1,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=child_state_summary,
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor=child_anchor,
    )
    pcb = PausedChildBranchResumeState(
        branch_index=0,
        step_id="sub-worker",
        child_snapshot=child_snap,
    )  # child_workflow_id omitted -> defaults to None (the pre-B-31 shape)
    assert pcb.child_workflow_id is None
    fan = FanOutResumeState(
        orchestrator_output={"role": "orchestrator"},
        orchestrator_step_id="orchestrator",
        branches=(),
        worker_count=1,
        paused_child_branches=(pcb,),
    )
    got = _compute_snapshot_hash(
        workflow_id="wf-fp",
        run_id="run-1",
        step_index=0,
        state_summary=state_summary,
        fan_out_resume=fan,
    )
    # The pre-B-31 canonical serialization — the paused_child_branches entry has NO
    # `child_workflow_id` key at all (the field did not exist), not `child_workflow_id: null`.
    # The nested child_snapshot dict also has its (pre-existing, unrelated to B-31)
    # default-None `orchestrator_effect_fence_resume` key dropped by the SAME strip
    # function — mirror that here too, else this test's own hand-built "canonical" dict
    # would disagree with the real stripped shape for an unrelated reason.
    child_snap_dump = child_snap.model_dump(mode="json")
    child_snap_dump.pop("orchestrator_effect_fence_resume", None)
    canonical = {
        "workflow_id": "wf-fp",
        "run_id": "run-1",
        "step_index": 0,
        "state_summary": state_summary.model_dump(mode="json"),
        "fan_out_resume": {
            "orchestrator_output": {"role": "orchestrator"},
            "orchestrator_step_id": "orchestrator",
            "branches": [],
            "worker_count": 1,
            "paused_child_branches": [
                {
                    "branch_index": 0,
                    "step_id": "sub-worker",
                    "child_snapshot": child_snap_dump,
                }
            ],
        },
    }
    expected = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert got == expected, (
        "child_workflow_id=None must be DROPPED from the entry's model_dump, not "
        "serialized as `child_workflow_id: null` — else every pre-B-31 durable snapshot "
        "with a paused-child branch re-hashes differently and fails resume validation"
    )


# ---------------------------------------------------------------------------
# B-FANOUT-PAUSE-SYNTHESIS × HIERARCHICAL — a REAL nested round-trip (advisor Item 1).
# A synthesis-bearing CHILD fan-out snapshot embedded in a parent's paused_child_branches:
# proves (1) the nested child synthesis identity survives a REAL protocol capture, (2) the
# parent hash recomputes consistently over the nested carrier (the recursive `synthesis_step_id`
# strip — Codex #1 was exactly a nested-HIERARCHICAL hash bug), and (3) on parent resume the
# child re-enters `execute_workflow(pause_snapshot_input=...)`, MY entry guard material-diffs the
# child synthesis (matches), and the child reaches SUCCESS + FRESH-dispatches its synthesis once.
# ---------------------------------------------------------------------------


class _ChildSynthDispatcher:
    """Child fan-out dispatcher with a terminal synthesis: `child-orch` + workers echo;
    `child-synthesis` returns a DISTINCT marker + counts its dispatches (so the
    fresh-dispatched-exactly-once claim is checkable)."""

    def __init__(self) -> None:
        self.synth_dispatches = 0

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        if step.step_kind is StepKind.POST_JOIN_SYNTHESIS:
            self.synth_dispatches += 1
            sibs = tuple(i for i, _ in (getattr(step_context, "sibling_outputs", None) or ()))
            return {"child_synthesized": True, "from": sibs}
        return {"role": str(step.step_id)}


class _ChildSynthRegistry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind not in (StepKind.DECLARATIVE_STEP, StepKind.POST_JOIN_SYNTHESIS):
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _child_steps_with_synthesis() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("child-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "child-orch"},
        ),
        WorkflowStep(
            step_id=StepID("child-worker-0"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 0},
        ),
        WorkflowStep(
            step_id=StepID("child-worker-1"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 1},
        ),
        WorkflowStep(
            step_id=StepID("child-synthesis"),
            step_kind=StepKind.POST_JOIN_SYNTHESIS,
            step_payload={"messages": [], "params": {"max_tokens": 64}},
        ),
    ]


class _SynthChildSubAgentDispatcher:
    """Faithful sub-agent double that re-enters a SYNTHESIS-bearing child fan-out, threading
    `step_context.child_resume_snapshot` as the child's `pause_snapshot_input` (exactly the
    runtime `sub_agent_dispatch.py` seam) so the child re-enters at its cursor."""

    def __init__(self, *, child_dispatcher: _ChildSynthDispatcher) -> None:
        self._child_dispatcher = child_dispatcher
        self.received_resume: list[Any] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        child_resume = getattr(step_context, "child_resume_snapshot", None)
        self.received_resume.append(child_resume)
        child_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
        child_result = execute_workflow(
            _manifest("wf-child", TopologyPattern.ORCHESTRATOR_WORKERS),
            _child_steps_with_synthesis(),
            run_id="child-run",
            ctx=child_ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=cast(
                StepDispatcherRegistry, _ChildSynthRegistry(self._child_dispatcher)
            ),
            pause_snapshot_input=child_resume,
        )
        if child_result.status is RunStatus.PAUSED:
            assert child_result.pause_snapshot is not None
            raise SubAgentChildPausedError(
                child_workflow_id="wf-child", child_snapshot=child_result.pause_snapshot
            )
        return dict(child_result.final_state or child_result.partial_state or {})


class _SynthParentRegistry:
    def __init__(self, *, sub_agent: _SynthChildSubAgentDispatcher) -> None:
        self._sub_agent = sub_agent
        self._echo = _CountingDispatcher()

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agent)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)


def test_hierarchical_child_synthesis_real_nested_round_trip() -> None:
    """B-FANOUT-PAUSE-SYNTHESIS × HIERARCHICAL real nested round-trip (advisor Item 1)."""
    # A synthesis-bearing CHILD snapshot — captured through the REAL protocol (hash-valid).
    # `branches=()` → resume re-dispatches both child workers → SUCCESS → the synthesis fires
    # (a real failure-pause always leaves a terminal-errored branch → degraded → fold, so the
    # SUCCESS+synthesis path is the no-errored-branch shape, as for the top-level full-chain).
    child_snap = asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id="wf-child",
            run_id="child-run",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            fan_out_resume=FanOutResumeState(
                orchestrator_output={"role": "child-orch", "recovered": True},
                orchestrator_step_id="child-orch",
                branches=(),
                worker_count=2,
                synthesis_step_id="child-synthesis",
            ),
        )
    )
    # A parent snapshot embedding the child as a paused-child branch (the sub-worker, ordinal 0).
    parent_fan = FanOutResumeState(
        orchestrator_output={"role": "parent-orch", "recovered": True},
        orchestrator_step_id="parent-orch",
        branches=(),
        worker_count=1,
        paused_child_branches=(
            PausedChildBranchResumeState(
                branch_index=0, step_id="sub-worker", child_snapshot=child_snap
            ),
        ),
    )
    parent_snap = asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id="wf-parent",
            run_id="parent-run",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            fan_out_resume=parent_fan,
        )
    )
    # (1) REAL nested capture: the child's synthesis identity survives inside the parent snapshot.
    assert parent_snap.fan_out_resume is not None
    nested = parent_snap.fan_out_resume.paused_child_branches[0].child_snapshot
    assert nested.fan_out_resume is not None
    assert nested.fan_out_resume.synthesis_step_id == "child-synthesis"
    # (2) Parent hash byte-compat over the NESTED carrier: the recompute COVERS the nested
    # (non-None) synthesis identity AND strips the parent's own None — `snapshot_hash` (computed
    # at capture) recomputes identically. With a top-level-only drop this would have diverged
    # (Codex #1). The recursive strip leaves the nested `synthesis_step_id: null`-free.
    assert parent_snap.snapshot_hash == _compute_snapshot_hash(
        workflow_id=parent_snap.workflow_id,
        run_id=parent_snap.run_id,
        step_index=parent_snap.step_index,
        state_summary=parent_snap.state_summary,
        fan_out_resume=parent_snap.fan_out_resume,
    )
    # (3) REAL parent resume → the child re-enters `execute_workflow` at its cursor, MY entry
    # guard material-diffs the child synthesis (matches "child-synthesis"), the child reaches
    # SUCCESS and FRESH-dispatches its synthesis EXACTLY ONCE.
    child_dispatcher = _ChildSynthDispatcher()
    sub_agent = _SynthChildSubAgentDispatcher(child_dispatcher=child_dispatcher)
    parent_registry = cast(StepDispatcherRegistry, _SynthParentRegistry(sub_agent=sub_agent))
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION),
        _parent_steps(),
        run_id="parent-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=parent_registry,
        pause_snapshot_input=parent_snap,
    )
    assert resumed.status is RunStatus.SUCCESS, f"{resumed.status} / {resumed.fail_class}"
    # The child re-entered WITH its snapshot (genuine re-entry, not a fresh run).
    assert sub_agent.received_resume[-1] is not None
    assert sub_agent.received_resume[-1].fan_out_resume is not None
    assert sub_agent.received_resume[-1].fan_out_resume.synthesis_step_id == "child-synthesis"
    # The child synthesis FRESH-dispatched exactly once (effect-free, first-and-only).
    assert child_dispatcher.synth_dispatches == 1


# ---------------------------------------------------------------------------
# B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE — the ORCHESTRATOR_WORKERS analogue: a WORKER
# whose OWN dispatch raises the runtime effect fence composes that ambiguous-pause
# THROUGH the worker barrier to a genuine PAUSE carrying `effect_fence_paused_branches`,
# and resume re-enters the worker with the operator's key-bound resolution. The
# real-fence witness is the REAL `_execute_orchestrator_workers` TaskGroup+shield; the
# error is name-matched (harness-cp cannot import harness-runtime).
# ---------------------------------------------------------------------------


class EffectFenceAmbiguousUncommittedError(Exception):
    """Test-local stand-in for the runtime `effect_fence.EffectFenceAmbiguousUncommittedError`
    (C-RT-31 §14.22) — the driver name-matches `type(exc).__name__`, so a same-named local class
    with the `idempotency_key` attribute is the faithful CP-side witness."""

    def __init__(self, *, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__(f"ambiguous (key={idempotency_key!r})")


class _OrchestratorFenceAmbiguousDispatcher:
    """Deterministic: orchestrator returns immediately; worker-0 completes (sets a gate);
    worker-1 waits on the gate THEN raises the effect-fence ambiguous error — so worker-0 is
    terminal BEFORE worker-1's fence-pause halts the barrier. Records each dispatch's threaded
    `effect_fence_resolution` (the resume producer-half witness)."""

    def __init__(self, *, fence_key: str = "fence-key-worker-1") -> None:
        self._gate = threading.Event()
        self._fence_key = fence_key
        self.dispatched: list[str] = []
        self.seen_resolution: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        self.seen_resolution[step_id] = getattr(step_context, "effect_fence_resolution", None)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        if step_id == "worker-0":
            self._gate.set()
            return {"role": "worker-0", "echoed": dict(step.step_payload)}
        assert self._gate.wait(timeout=10.0), "worker-0 never completed"
        raise EffectFenceAmbiguousUncommittedError(idempotency_key=self._fence_key)


class _OrchestratorResumeRecordingDispatcher:
    """Resume-side recording dispatcher: orchestrator + worker-0 recovered (skipped); records the
    threaded `effect_fence_resolution` per dispatch then SUCCEEDS (no gate, no raise)."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []
        self.seen_resolution: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        self.seen_resolution[step_id] = getattr(step_context, "effect_fence_resolution", None)
        return {"role": step_id, "echoed": dict(step.step_payload)}


def test_orchestrator_worker_effect_fence_ambiguous_composes_through_barrier_to_pause() -> None:
    """REAL-FENCE WITNESS (PAUSE half, ORCHESTRATOR_WORKERS): a worker whose OWN dispatch raises
    the effect-fence ambiguous error composes through the REAL `_execute_orchestrator_workers`
    TaskGroup+shield to a genuine PAUSE carrying `effect_fence_paused_branches` (worker-1 + its
    held reserve key), DISJOINT from the terminal `branches` (worker-0 recovered) and the
    orchestrator (recovered)."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=_OrchestratorFenceAmbiguousDispatcher(), ctx=ctx)

    assert result.status is RunStatus.PAUSED
    assert result.fail_class is None
    snap = result.pause_snapshot
    assert snap is not None
    # Labeled EFFECT_FENCE_AMBIGUOUS so the operator surface knows to supply a resolution.
    assert snap.pause_reason is WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS
    fr = snap.fan_out_resume
    assert fr is not None
    assert fr.orchestrator_output == {"role": "orchestrator"}
    # worker-1 (branch ordinal 1) is the disjoint effect-fence-paused disposition.
    assert {b.branch_index for b in fr.branches} == {0}  # only worker-0 terminal
    efp = fr.effect_fence_paused_branches
    assert len(efp) == 1
    assert efp[0] == EffectFencePausedBranchResumeState(
        branch_index=1,
        step_id="worker-1",
        step_kind="declarative-step",
        idempotency_key="fence-key-worker-1",
    )
    restored = PauseSnapshot.model_validate(snap.model_dump(mode="json"))
    assert restored == snap


def test_orchestrator_worker_effect_fence_resume_threads_key_bound_resolution() -> None:
    """REAL-FENCE WITNESS (resume half, ORCHESTRATOR_WORKERS): resuming re-enters ONLY the
    fence-paused worker (orchestrator + worker-0 recovered-skipped), threading the operator's
    `EffectFenceResolution` key-bound to THAT worker's held reserve."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    efp = snap.fan_out_resume.effect_fence_paused_branches
    assert len(efp) == 1
    key = efp[0].idempotency_key

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    rec = _OrchestratorResumeRecordingDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — the uniform fallback now applies only
    # when this location is the SOLE unaddressed member; this snapshot has exactly
    # one fence-paused location, so its own key is trivially eligible.
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=key,
    )

    assert result.status is RunStatus.SUCCESS
    # orchestrator + worker-0 recovered-skipped; only worker-1 re-dispatched WITH the directive.
    assert "orchestrator" not in rec.dispatched
    assert "worker-0" not in rec.dispatched
    assert "worker-1" in rec.dispatched
    threaded = rec.seen_resolution["worker-1"]
    assert threaded is not None
    assert threaded.resolution is EffectFenceResolution.RE_FIRE
    assert threaded.idempotency_key == key
    # Non-consuming: re-reading resume_ctx.effect_fence_resolution still returns RE_FIRE.
    assert resume_ctx.effect_fence_resolution is EffectFenceResolution.RE_FIRE


class EffectFenceAbortedError(Exception):
    """Test-local stand-in for the runtime `effect_fence.EffectFenceAbortedError` (operator ABORT
    applied at the fence gate)."""


class _OrchestratorAbortOnResolutionDispatcher:
    """Resume-side: orchestrator + worker-0 recovered-skipped; the re-entered fence-paused worker
    RAISES `EffectFenceAbortedError` when its threaded directive is ABORT (the runtime applying the
    operator's choice) — witnessing ABORT → terminal FAILED, not a re-pause."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        directive = getattr(step_context, "effect_fence_resolution", None)
        if directive is not None and directive.resolution is EffectFenceResolution.ABORT:
            raise EffectFenceAbortedError(f"operator aborted {step_id}")
        return {"role": step_id, "echoed": dict(step.step_payload)}


def test_orchestrator_worker_effect_fence_resume_abort_is_terminal_failed() -> None:
    """Codex [P1] regression (ORCHESTRATOR_WORKERS): resuming an effect-fence-paused worker with
    ABORT yields a TERMINAL `RunStatus.FAILED`, NOT a re-pause — even on the cascade_policy=pause
    tier."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    key = snap.fan_out_resume.effect_fence_paused_branches[0].idempotency_key

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.ABORT)
    rec = _OrchestratorAbortOnResolutionDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — the uniform fallback now applies only
    # when this location is the SOLE unaddressed member; this snapshot has exactly
    # one fence-paused location, so its own key is trivially eligible.
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=key,
    )

    assert result.status is RunStatus.FAILED
    assert "orchestrator-workers-effect-fence-aborted" in (result.fail_class or "")
    assert result.pause_snapshot is None  # terminal — NOT a re-pause
    assert "worker-1" in rec.dispatched  # the aborted worker DID re-dispatch


def test_orchestrator_worker_effect_fence_resume_changed_kind_fails_closed() -> None:
    """Codex [P1] R2 regression (ORCHESTRATOR_WORKERS): an effect-fence-paused worker re-supplied
    at the SAME step_id but a CHANGED step_kind on resume FAILS CLOSED (the resolution would not
    reach the fence). The live-pause analogue of the crash-resume changed-kind guard."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None

    # Resume with worker-1 CHANGED from declarative-step → inference-step (same step_id).
    changed = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 0},
        ),
        WorkflowStep(
            step_id=StepID("worker-1"), step_kind=StepKind.INFERENCE_STEP, step_payload={"index": 1}
        ),
    ]
    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.SKIP_AS_FIRED)
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=changed,
        dispatcher=_OrchestratorResumeRecordingDispatcher(),
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED
    assert "effect-fence-paused-kind-changed" in (result.fail_class or "")


# ---------------------------------------------------------------------------
# B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-EFFECT-BEARING — the ORCHESTRATOR's OWN
# (steps[0]) dispatch raises the effect-fence ambiguous error → composed to a §26.2 pause
# (Part 2) carrying the new `orchestrator_effect_fence_resume` carrier; resume re-dispatches
# the orchestrator WITH the operator's key-bound EffectFenceResolution threaded onto its
# context (Part 3, the NEW resume→orchestrator application site). Real-fence witnesses through
# the REAL `_execute_orchestrator_workers` sequential orchestrator-dispatch path.
# ---------------------------------------------------------------------------


class _OrchestratorSelfFenceAmbiguousDispatcher:
    """The ORCHESTRATOR's OWN dispatch raises the effect-fence ambiguous error on its FIRST dispatch
    (no resolution threaded — the effect-bearing orchestrator maybe-ran). On RESUME a directive IS
    threaded, and this dispatcher APPLIES it (the runtime fence's role): ABORT → raise
    `EffectFenceAbortedError`; RE_FIRE (or any non-abort) → a fresh success. Records each dispatch's
    threaded `effect_fence_resolution` (the resume producer-half witness)."""

    def __init__(self, *, fence_key: str = "fence-key-orchestrator") -> None:
        self._fence_key = fence_key
        self.dispatched: list[str] = []
        self.seen_resolution: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        directive = getattr(step_context, "effect_fence_resolution", None)
        self.seen_resolution[step_id] = directive
        if step_id == "orchestrator":
            if directive is None:
                raise EffectFenceAmbiguousUncommittedError(idempotency_key=self._fence_key)
            if directive.resolution is EffectFenceResolution.ABORT:
                raise EffectFenceAbortedError(f"operator aborted {step_id}")
            return {"role": "orchestrator", "refired": True}
        return {"role": step_id, "echoed": dict(step.step_payload)}


def test_orchestrator_self_effect_fence_ambiguous_composes_to_pause() -> None:
    """REAL-FENCE WITNESS (PAUSE half): the ORCHESTRATOR's OWN dispatch raises the effect-fence
    ambiguous error → `_execute_orchestrator_workers` composes a §26.2 EFFECT_FENCE_AMBIGUOUS pause
    carrying the new `orchestrator_effect_fence_resume` (held key + orchestrator step_id/step_kind).
    NOTHING ran (no `fan_out_resume`); the snapshot is hash-valid + round-trips."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(), ctx=ctx)

    assert result.status is RunStatus.PAUSED
    assert result.fail_class is None
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason is WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS
    # The orchestrator paused BEFORE any worker / its own capture → no fan_out_resume.
    assert snap.fan_out_resume is None
    oefr = snap.orchestrator_effect_fence_resume
    assert oefr == OrchestratorEffectFencePausedResumeState(
        idempotency_key="fence-key-orchestrator",
        step_id="orchestrator",
        step_kind="declarative-step",
    )
    # Hash-valid (covers the new carrier) + byte round-trips.
    assert snap.snapshot_hash == _compute_snapshot_hash(
        workflow_id=snap.workflow_id,
        run_id=snap.run_id,
        step_index=snap.step_index,
        state_summary=snap.state_summary,
        orchestrator_effect_fence_resume=oefr,
    )
    restored = PauseSnapshot.model_validate(snap.model_dump(mode="json"))
    assert restored == snap


def test_orchestrator_self_effect_fence_resume_re_fire_recovers() -> None:
    """REAL-FENCE WITNESS (resume RE_FIRE): resuming an orchestrator effect-fence pause re-dispatches
    the orchestrator WITH the operator's RE_FIRE directive key-bound to its reserve, then the workers
    fan out fresh → SUCCESS. The directive is threaded onto the orchestrator's context (the NEW
    resume→orchestrator application site)."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.orchestrator_effect_fence_resume is not None
    key = snap.orchestrator_effect_fence_resume.idempotency_key

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    rec = _OrchestratorSelfFenceAmbiguousDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — the uniform fallback now applies only
    # when this location is the SOLE unaddressed member; this snapshot has exactly
    # one fence-paused location, so its own key is trivially eligible.
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=key,
    )

    assert result.status is RunStatus.SUCCESS
    # The orchestrator re-dispatched WITH the RE_FIRE directive key-bound to its reserve.
    assert "orchestrator" in rec.dispatched
    threaded = rec.seen_resolution["orchestrator"]
    assert threaded is not None
    assert threaded.resolution is EffectFenceResolution.RE_FIRE
    assert threaded.idempotency_key == key
    # Non-consuming: re-reading resume_ctx.effect_fence_resolution still returns RE_FIRE.
    assert resume_ctx.effect_fence_resolution is EffectFenceResolution.RE_FIRE


def test_orchestrator_self_effect_fence_resume_abort_is_terminal_failed() -> None:
    """REAL-FENCE WITNESS (resume ABORT): an ABORT directive threaded to the orchestrator re-dispatch
    raises `EffectFenceAbortedError` (the runtime applying the operator's choice) → the generic
    orchestrator-dispatch except returns terminal FAILED, NOT a re-pause."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.orchestrator_effect_fence_resume is not None
    key = snap.orchestrator_effect_fence_resume.idempotency_key

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.ABORT)
    rec = _OrchestratorSelfFenceAmbiguousDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — the uniform fallback now applies only
    # when this location is the SOLE unaddressed member; this snapshot has exactly
    # one fence-paused location, so its own key is trivially eligible.
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=key,
    )

    assert result.status is RunStatus.FAILED
    assert result.pause_snapshot is None  # terminal — NOT a re-pause
    assert "orchestrator" in rec.dispatched  # the orchestrator DID re-dispatch (then aborted)


def test_orchestrator_self_effect_fence_resume_skip_as_fired_rejected() -> None:
    """REAL-FENCE WITNESS (resume SKIP_AS_FIRED REJECTED): SKIP_AS_FIRED is rejected at the CP resume
    site for an orchestrator (its empty output would silently structure a degenerate fan-out
    aggregate — no-silent-failure). The orchestrator is NOT re-dispatched; the run FAILS loud."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.orchestrator_effect_fence_resume is not None
    key = snap.orchestrator_effect_fence_resume.idempotency_key

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.SKIP_AS_FIRED)
    rec = _OrchestratorSelfFenceAmbiguousDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — the uniform fallback now applies only
    # when this location is the SOLE unaddressed member; this snapshot has exactly
    # one fence-paused location, so its own key is trivially eligible.
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=key,
    )

    assert result.status is RunStatus.FAILED
    assert "skip-as-fired-unsupported" in (result.fail_class or "")
    assert rec.dispatched == []  # rejected BEFORE any dispatch — never re-dispatched


def test_orchestrator_self_effect_fence_resume_changed_orchestrator_fails_closed() -> None:
    """REAL-FENCE WITNESS (changed-orchestrator guard): an orchestrator re-supplied on resume with a
    CHANGED step_kind (same step_id) FAILS CLOSED — threading the resolution would reach the WRONG
    (or no) fence and silently abandon the original ambiguous effect."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.orchestrator_effect_fence_resume is not None

    # Resume with the orchestrator CHANGED declarative-step → inference-step (same step_id).
    changed = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 0},
        ),
        WorkflowStep(
            step_id=StepID("worker-1"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 1},
        ),
    ]
    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    rec = _OrchestratorSelfFenceAmbiguousDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=changed,
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED
    assert "changed-orchestrator" in (result.fail_class or "")
    assert rec.dispatched == []  # fail-closed BEFORE any re-dispatch


def test_orchestrator_self_effect_fence_no_protocol_fails_closed() -> None:
    """Part-2 gating: the orchestrator raises the fence error but NO PauseResumeProtocol is bound →
    the pause cannot be composed → fall through to terminal FAILED (the pre-arc fail-closed; resume
    would advertise a resumability `api.resume` cannot honor)."""
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    ctx_obj.pause_resume_protocol = None  # type: ignore[assignment]
    result = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, ctx_obj),
    )
    assert result.status is RunStatus.FAILED
    assert result.pause_snapshot is None


def test_orchestrator_self_effect_fence_resume_empty_body_fails_closed() -> None:
    """Empty-body guard (out-of-family Codex [P2], codex-vs-main): an orchestrator fence pause
    resumed with the body CHANGED to EMPTY (`steps=[]`) FAILS CLOSED — the empty-steps SUCCESS fast
    path must NOT silently abandon the unresolved ambiguous orchestrator effect + the operator's
    resolution (the changed-orchestrator guard reads `steps[0]`, which an empty body lacks)."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.orchestrator_effect_fence_resume is not None

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=[],  # body changed to empty between pause and resume
        dispatcher=_OrchestratorSelfFenceAmbiguousDispatcher(),
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )
    assert result.status is RunStatus.FAILED
    assert "changed-orchestrator" in (result.fail_class or "")
    assert result.pause_snapshot is None


class _OrchestratorSelfFenceSynthDispatcher:
    """Orchestrator raises the fence ambiguous error on its FIRST dispatch; on RESUME (a directive
    threaded) it re-fires; workers echo; the terminal POST_JOIN_SYNTHESIS composes. Witnesses an
    orchestrator fence pause in a SYNTHESIS-bearing workflow."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step.step_kind is StepKind.POST_JOIN_SYNTHESIS:
            return {"synthesized": True}
        if step_id == "orchestrator":
            directive = getattr(step_context, "effect_fence_resolution", None)
            if directive is None:
                raise EffectFenceAmbiguousUncommittedError(idempotency_key="fence-key-orchestrator")
            return {"role": "orchestrator", "refired": True}
        return {"role": step_id, "echoed": dict(step.step_payload)}


def test_orchestrator_self_effect_fence_resume_synthesis_bearing_recovers() -> None:
    """REAL-FENCE WITNESS (synthesis-bearing, out-of-family Codex [P2]): an orchestrator fence pause
    in an ORCHESTRATOR_WORKERS workflow that ALSO carries a terminal POST_JOIN_SYNTHESIS step
    RESUMES — the synthesis material-diff is SKIPPED (the orchestrator paused BEFORE everything, so
    nothing ran + no synthesis identity was captured; the orchestrator + workers + synthesis all
    re-dispatch fresh on RE_FIRE). Before the [P2] fix the absent captured synthesis identity falsely
    rejected the unchanged synthesis-bearing body as a 'removed' material diff."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest(),
        [*_steps(2), _synthesis_step()],
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(
            StepDispatcherRegistry, _SynthRegistry(_OrchestratorSelfFenceSynthDispatcher())
        ),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None and snap.orchestrator_effect_fence_resume is not None
    key = snap.orchestrator_effect_fence_resume.idempotency_key

    resume_ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    rec = _OrchestratorSelfFenceSynthDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — the uniform fallback now applies only
    # when this location is the SOLE unaddressed member; this snapshot has exactly
    # one fence-paused location, so its own key is trivially eligible.
    result = execute_workflow(
        _manifest(),
        [*_steps(2), _synthesis_step()],
        run_id="run-1",
        ctx=cast(DriverContext, ctx_obj),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _SynthRegistry(rec)),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=key,
    )
    assert result.status is RunStatus.SUCCESS  # NOT rejected by the synthesis material-diff
    # Everything re-dispatched fresh (orchestrator re-fired + workers + synthesis once).
    assert "orchestrator" in rec.dispatched
    assert rec.dispatched.count("synthesis") == 1


# ---------------------------------------------------------------------------
# B-FANOUT-EFFECT-FENCE-PER-BRANCH-RESOLUTION — two workers fence-pause in ONE barrier;
# resume resolves them DIFFERENTLY via the `effect_fence_resolutions` per-key map
# (idempotency_key -> EffectFenceResolution), the single field staying the uniform default.
# Real-fence witness: the REAL `_execute_orchestrator_workers` TaskGroup+shield.
# ---------------------------------------------------------------------------


class _OrchestratorTwoFenceDispatcher:
    """Orchestrator completes; BOTH workers raise the effect-fence ambiguous error with DISTINCT
    keys, synchronized on a barrier so both are in-flight BEFORE either raises → TWO
    `effect_fence_paused_branches` in one pause (the per-branch-distinct precondition)."""

    def __init__(self) -> None:
        self._barrier = threading.Barrier(2, timeout=10.0)
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        self._barrier.wait()
        raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-{step_id}")


class _OrchestratorPartialResumeDispatcher:
    """Resume-side (partial-map iterative witness): a worker WITH a threaded directive resolves
    (success); a worker WITHOUT one (unanswered → INERT) RE-RAISES the fence — modelling the
    runtime's INERT re-pause — so the unanswered worker re-pauses while the answered one resolves
    terminal."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []
        self.seen_resolution: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        directive = getattr(step_context, "effect_fence_resolution", None)
        self.seen_resolution[step_id] = directive
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        if directive is None:
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-{step_id}")
        return {"role": step_id, "echoed": dict(step.step_payload)}


def _orchestrator_two_fence_pause() -> PauseSnapshot:
    """Drive a real ORCHESTRATOR_WORKERS pause with BOTH workers effect-fence-paused; return the
    snapshot (the per-branch-distinct precondition)."""
    paused = _run(
        steps=_steps(2),
        dispatcher=_OrchestratorTwoFenceDispatcher(),
        ctx=cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    assert len(snap.fan_out_resume.effect_fence_paused_branches) == 2
    return snap


def test_orchestrator_per_branch_distinct_resolutions() -> None:
    """REAL-FENCE WITNESS (ORCHESTRATOR_WORKERS, per-branch-DISTINCT): two workers fence-pause in
    one barrier; resume resolves worker-0 SKIP_AS_FIRED + worker-1 RE_FIRE via the per-key
    `effect_fence_resolutions` map — each worker re-dispatched with ITS OWN key-bound resolution,
    the capability the single uniform field could not express."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.SKIP_AS_FIRED,
            key_by_index[1]: EffectFenceResolution.RE_FIRE,
        }
    )
    rec = _OrchestratorResumeRecordingDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.SUCCESS
    w0 = rec.seen_resolution["worker-0"]
    w1 = rec.seen_resolution["worker-1"]
    assert w0 is not None and w0.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert w0.idempotency_key == key_by_index[0]
    assert w1 is not None and w1.resolution is EffectFenceResolution.RE_FIRE
    assert w1.idempotency_key == key_by_index[1]


def test_orchestrator_per_branch_map_overrides_uniform_default() -> None:
    """The per-key map OVERRIDES the uniform `effect_fence_resolution` default per branch: worker-0
    (in the map) gets SKIP_AS_FIRED; worker-1 (absent from the map) falls back to the uniform
    RE_FIRE default — the `default + per-key override` composition."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={key_by_index[0]: EffectFenceResolution.SKIP_AS_FIRED},
        effect_fence_resolution=EffectFenceResolution.RE_FIRE,
    )
    rec = _OrchestratorResumeRecordingDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    # B-70 impl leg (CP spec v1.107 §1.1) — worker-0 is map-addressed (always safe);
    # worker-1 is the SOLE remaining unaddressed location this cycle, so the uniform
    # fallback is safe for it too. Computed via the real resolver, not hand-derived.
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=(
            compute_effect_fence_uniform_fallback_eligible_key(snap, resume_ctx)
        ),
    )

    assert result.status is RunStatus.SUCCESS
    assert rec.seen_resolution["worker-0"].resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert rec.seen_resolution["worker-1"].resolution is EffectFenceResolution.RE_FIRE  # fallback


def test_orchestrator_partial_map_unanswered_worker_re_pauses_iteratively() -> None:
    """Partial-map iterative composability: a map answering ONLY worker-0 (no uniform default) →
    worker-0 resolves terminal, worker-1 (unanswered → INERT) re-pauses carrying its residual. The
    NEW snapshot holds ONLY the still-unanswered worker-1, so a subsequent resume can answer it."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    # Answer ONLY worker-0; worker-1 left unanswered with NO uniform fallback.
    resume_ctx = ResumeContext(
        effect_fence_resolutions={key_by_index[0]: EffectFenceResolution.SKIP_AS_FIRED}
    )
    rec = _OrchestratorPartialResumeDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.PAUSED
    snap2 = result.pause_snapshot
    assert snap2 is not None and snap2.fan_out_resume is not None
    efp2 = snap2.fan_out_resume.effect_fence_paused_branches
    assert len(efp2) == 1
    assert efp2[0].branch_index == 1  # only worker-1 still paused
    assert efp2[0].idempotency_key == key_by_index[1]
    # worker-0 got its SKIP directive (answered); worker-1 got None (unanswered → re-paused).
    assert rec.seen_resolution["worker-0"].resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert rec.seen_resolution["worker-1"] is None


def test_orchestrator_no_map_two_unaddressed_workers_both_repause_inert() -> None:
    """B-70 impl leg (CP spec v1.107 §1.1) SUPERSEDES the pre-arc behavior this test
    used to pin: with NO map and BOTH workers fence-paused, the uniform `effect_fence_
    resolution` no longer applies unconditionally to every unaddressed location — that
    was exactly the cross-location misapplication risk the spec's safety rule exists to
    close (a single operator judgment silently applied to 2+ distinct held reserves).
    With 2 unaddressed locations this cycle, `effect_fence_uniform_fallback_eligible_key`
    is `None` (per the pure tests), so NEITHER worker receives a directive — both
    re-pause INERT, and the run stays PAUSED with both branches still unresolved."""
    snap = _orchestrator_two_fence_pause()
    resume_ctx = ResumeContext(
        effect_fence_resolution=EffectFenceResolution.RE_FIRE
    )  # single field only, no map
    eligible_key = compute_effect_fence_uniform_fallback_eligible_key(snap, resume_ctx)
    assert eligible_key is None  # 2 unaddressed locations -> no sole eligible member
    rec = _OrchestratorPartialResumeDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=eligible_key,
    )

    assert result.status is RunStatus.PAUSED
    assert rec.seen_resolution["worker-0"] is None
    assert rec.seen_resolution["worker-1"] is None
    snap2 = result.pause_snapshot
    assert snap2 is not None and snap2.fan_out_resume is not None
    # Both locations re-pause carrying their same original keys — neither was
    # misattributed the uniform RE_FIRE judgment intended for at most one of them.
    assert {b.idempotency_key for b in snap2.fan_out_resume.effect_fence_paused_branches} == {
        b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }


class _OrchestratorAmbiguousUnlessAbortLeakedDispatcher:
    """Resume-side witness for the no-map-two-unaddressed-ABORT case: RAISES
    `EffectFenceAbortedError` if a directive somehow reached this worker (proving
    the safety gate leaked — the failure mode this witness exists to catch), else
    RAISES the ambiguous fence error (proving NO directive reached it — the
    expected safe outcome, re-pause INERT, never a terminal FAILED)."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []
        self.seen_resolution: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        directive = getattr(step_context, "effect_fence_resolution", None)
        self.seen_resolution[step_id] = directive
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        if directive is not None:
            raise EffectFenceAbortedError(f"leaked directive at {step_id}: {directive}")
        raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-{step_id}")


def test_orchestrator_no_map_two_unaddressed_workers_abort_default_both_repause_inert() -> None:
    """advisor()-flagged gap: the uniform-ABORT + 2-unaddressed-locations path is a
    DISTINCT code path from the RE_FIRE case above — it exercises the interaction
    between the B-70 safety gate and the pre-existing run-level ABORT guard
    (`_any_fence_abort`). Pre-B-70, both workers would have resolved ABORT
    unconditionally -> `_any_fence_abort=True` -> terminal FAILED. Post-B-70, with 2
    unaddressed locations and no map, `effect_fence_uniform_fallback_eligible_key`
    is `None`, so NEITHER worker's gated resolution is ABORT (both are `None`) ->
    `_any_fence_abort=False` -> the run stays PAUSED, re-entering both locations
    INERT rather than misattributing a single ABORT judgment to both distinct held
    reserves and failing the whole run on an ambiguous operator input."""
    snap = _orchestrator_two_fence_pause()
    resume_ctx = ResumeContext(
        effect_fence_resolution=EffectFenceResolution.ABORT
    )  # single field only, no map
    eligible_key = compute_effect_fence_uniform_fallback_eligible_key(snap, resume_ctx)
    assert eligible_key is None  # 2 unaddressed locations -> no sole eligible member
    rec = _OrchestratorAmbiguousUnlessAbortLeakedDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=eligible_key,
    )

    assert result.status is RunStatus.PAUSED  # NOT FAILED — the pre-B-70 outcome
    assert rec.seen_resolution["worker-0"] is None
    assert rec.seen_resolution["worker-1"] is None
    snap2 = result.pause_snapshot
    assert snap2 is not None and snap2.fan_out_resume is not None
    assert {b.idempotency_key for b in snap2.fan_out_resume.effect_fence_paused_branches} == {
        b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }


class _OrchestratorAbortGuardDispatcher:
    """Resume-side abort-guard witness: an ABORT directive raises EffectFenceAbortedError; a
    RE_FIRE / SKIP directive FIRES (records the branch in `fired`); a None directive (a suppressed
    sibling) RE-RAISES the ambiguous fence (re-pause, no fire). Witnesses that under a mixed
    {ABORT, RE_FIRE} map the RE_FIRE sibling does NOT fire before the ABORT fails the run."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []
        self.fired: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        directive = getattr(step_context, "effect_fence_resolution", None)
        if directive is None:
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-{step_id}")
        if directive.resolution is EffectFenceResolution.ABORT:
            raise EffectFenceAbortedError(f"operator aborted {step_id}")
        self.fired.append(step_id)  # RE_FIRE / SKIP would fire the effect
        return {"role": step_id, "echoed": dict(step.step_payload)}


def test_orchestrator_mixed_abort_map_suppresses_sibling_refire() -> None:
    """Codex [P1] (ORCHESTRATOR_WORKERS): a mixed map {worker-0: ABORT, worker-1: RE_FIRE} must NOT
    fire the RE_FIRE sibling before the ABORT fails the run — ABORT stays run-level-terminal
    (v1.65 §1(b)). The RE_FIRE sibling's directive is SUPPRESSED (re-pauses INERT, no fire); the
    run FAILs. Per-branch-SCOPED abort (fire survivors anyway) is the registered follow-on."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT,
            key_by_index[1]: EffectFenceResolution.RE_FIRE,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED
    assert "orchestrator-workers-effect-fence-aborted" in (result.fail_class or "")
    assert result.pause_snapshot is None  # terminal — NOT a re-pause
    assert "worker-1" not in rec.fired  # the RE_FIRE sibling was SUPPRESSED — did NOT fire


# ---------------------------------------------------------------------------
# B-FANOUT-EFFECT-FENCE-PER-BRANCH-SCOPED-ABORT (ORCHESTRATOR_WORKERS) — the per-branch-SCOPED
# abort (`ABORT_BRANCH`): fail JUST one worker, let the vouched-for siblings FIRE, fold survivors
# per cascade_policy. The symmetric witness of the parallelization peer case (same shared sites).
# ---------------------------------------------------------------------------


def test_orchestrator_scoped_abort_fires_vouched_sibling() -> None:
    """CRUX contrasting baseline (ORCHESTRATOR_WORKERS; inverse of
    test_orchestrator_mixed_abort_map_suppresses_sibling_refire): a mixed map
    {worker-0: ABORT_BRANCH, worker-1: RE_FIRE} fails JUST worker-0 (never re-dispatched →
    at-most-once) and FIRES the vouched-for RE_FIRE sibling → the run folds the survivor → PARTIAL
    (NOT the run-level-ABORT FAILED)."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT_BRANCH,
            key_by_index[1]: EffectFenceResolution.RE_FIRE,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.PARTIAL  # survivor folded, NOT the run-level-ABORT FAILED
    # PARTIAL carries fail_class=None like every degraded PARTIAL (the aborted worker is a degraded
    # terminal non-contributor; run-result provenance is FAILED-only — see the all-abort test).
    assert result.fail_class is None
    assert "worker-1" in rec.fired  # the vouched-for RE_FIRE sibling FIRED (NOT suppressed)
    assert "worker-0" not in rec.dispatched  # the scoped-abort worker was NEVER re-dispatched


def test_orchestrator_all_scoped_abort_fails_not_vacuous_partial() -> None:
    """All-abort guard (advisor watchpoint #1; ORCHESTRATOR_WORKERS): when EVERY fence-paused worker
    is scoped-aborted, branch_plan is empty and NO worker survived → the run is FAILED, NOT the
    vacuous PARTIAL the empty-`branch_plan` short-circuit's `_degraded` would otherwise return."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT_BRANCH,
            key_by_index[1]: EffectFenceResolution.ABORT_BRANCH,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED  # NO survivor → FAILED, not a vacuous PARTIAL
    assert "orchestrator-workers-effect-fence-branch-aborted" in (result.fail_class or "")
    assert "worker-0" not in rec.dispatched  # neither scoped-abort worker was re-dispatched
    assert "worker-1" not in rec.dispatched


def test_orchestrator_scoped_abort_iterative_repause() -> None:
    """Iterative re-pause (advisor watchpoint #4; ORCHESTRATOR_WORKERS): a map answering ONLY
    worker-0 (ABORT_BRANCH) while worker-1 is left unresolved → worker-0 finalizes as a TERMINAL
    branch (next resume SKIPS it) and worker-1 re-pauses INERT (carried forward as still
    fence-paused)."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={key_by_index[0]: EffectFenceResolution.ABORT_BRANCH}
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.PAUSED
    snap2 = result.pause_snapshot
    assert snap2 is not None and snap2.fan_out_resume is not None
    # worker-0 (scoped-aborted) is now a TERMINAL branch — a later resume SKIPS it (never re-fires).
    assert 0 in {b.branch_index for b in snap2.fan_out_resume.branches}
    # worker-1 (unresolved) re-paused INERT — still fence-paused, carried forward.
    assert {b.branch_index for b in snap2.fan_out_resume.effect_fence_paused_branches} == {1}
    assert "worker-0" not in rec.dispatched  # the scoped-abort worker was NEVER re-dispatched


def test_orchestrator_mixed_run_abort_and_scoped_abort_deterministic() -> None:
    """advisor [P1] (precedence; ORCHESTRATOR_WORKERS): a mixed map {worker-0: ABORT, worker-1:
    ABORT_BRANCH} — run-level ABORT dominates (the run FAILs), but the scoped-abort worker-1 MUST be
    recorded DETERMINISTICALLY (excluded from re-dispatch), NOT nulled by the run-level-ABORT
    suppression and re-dispatched into the ABORT race. Witnesses the interception-BEFORE-suppression
    ordering: worker-1 is NEVER dispatched."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT,
            key_by_index[1]: EffectFenceResolution.ABORT_BRANCH,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED  # run-level ABORT dominates
    assert "orchestrator-workers-effect-fence-aborted" in (result.fail_class or "")
    assert "worker-0" in rec.dispatched  # the ABORT worker re-dispatched → raised → FAILED
    assert "worker-1" not in rec.dispatched  # the scoped-abort worker deterministically EXCLUDED


def test_orchestrator_scoped_abort_under_cascade_cancel_fails() -> None:
    """Codex [P1] (CASCADE_CANCEL tier; ORCHESTRATOR_WORKERS): a MIXED scoped-abort + surviving
    worker resumed under MULTI_TENANT_COMPLIANCE (CascadePolicy.CASCADE_CANCEL) must FAIL — NOT a
    SUCCESS with the surviving worker as final_state. The cascade-cancel block returns before the
    §25.15.1 degraded fold, so the scoped-abort guard must fire on this tier too."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT_BRANCH,
            key_by_index[1]: EffectFenceResolution.RE_FIRE,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,  # → CascadePolicy.CASCADE_CANCEL
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED  # NOT a SUCCESS hiding the scoped-abort
    assert "orchestrator-workers-effect-fence-branch-aborted" in (result.fail_class or "")


def test_orchestrator_scoped_abort_under_proceed_rejected_requires_strict_tier() -> None:
    """Codex [P2] (PROCEED tier; ORCHESTRATOR_WORKERS, MIXED): an effect-fence pause resumed under
    SOLO_DEVELOPER (CascadePolicy.PROCEED) with a surviving worker is rejected FAIL-CLOSED with
    `...-requires-strict-tier` (the existing guard, branch_plan non-empty) — scoped-abort recording
    SKIPPED (fail-closed precedes durable writes)."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT_BRANCH,
            key_by_index[1]: EffectFenceResolution.RE_FIRE,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        persona_tier=PersonaTier.SOLO_DEVELOPER,  # → CascadePolicy.PROCEED
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED
    assert "orchestrator-workers-effect-fence-resume-requires-strict-tier" in (
        result.fail_class or ""
    )
    assert "worker-0" not in rec.dispatched  # no dispatch (rejected before the barrier)


def test_orchestrator_all_scoped_abort_under_proceed_requires_strict_tier() -> None:
    """Codex [P2] (PROCEED tier; ORCHESTRATOR_WORKERS, ALL-abort): an all-scoped-abort PROCEED resume
    empties branch_plan → the `not branch_plan` short-circuit (which returns BEFORE the existing
    strict-tier guard). The early gate there must report `...-requires-strict-tier` (NOT the
    scoped-abort fail_class nor a SUCCESS), and NO scoped-abort durable write happened."""
    snap = _orchestrator_two_fence_pause()
    key_by_index = {
        b.branch_index: b.idempotency_key for b in snap.fan_out_resume.effect_fence_paused_branches
    }
    resume_ctx = ResumeContext(
        effect_fence_resolutions={
            key_by_index[0]: EffectFenceResolution.ABORT_BRANCH,
            key_by_index[1]: EffectFenceResolution.ABORT_BRANCH,
        }
    )
    rec = _OrchestratorAbortGuardDispatcher()
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    result = _run(
        steps=_steps(2),
        dispatcher=rec,
        ctx=cast(DriverContext, ctx_obj),
        pause_snapshot_input=snap,
        persona_tier=PersonaTier.SOLO_DEVELOPER,  # → CascadePolicy.PROCEED
        resume_context=resume_ctx,
    )

    assert result.status is RunStatus.FAILED
    assert "orchestrator-workers-effect-fence-resume-requires-strict-tier" in (
        result.fail_class or ""
    )


# ---------------------------------------------------------------------------
# B-39 interim constraint (CP spec v1.102 §3, fork §4 item 6, change-note item
# (e)) — a fan-out resuming a paused durable-HITL branch sequences ALL sibling
# dispatches (gated and ungated) around the resumed target: the resumed target
# dispatches FIRST, before ANY sibling.
# ---------------------------------------------------------------------------


def _resumed_target_snapshot(
    *, orchestrator_output: dict[str, Any], child_snapshot: PauseSnapshot
) -> PauseSnapshot:
    """A HAND-CONSTRUCTED parent-level PauseSnapshot (mirrors this file's own
    `_hitl_pending_child_pause_snapshot` convention, used elsewhere in this
    file to isolate ORCHESTRATOR_WORKERS/HIERARCHICAL_DELEGATION resume
    behavior from pause-CAPTURE race timing): `sub-worker` (branch 0) is a
    recovered paused-child (the resumed target); `sibling-worker` (branch 1)
    is ABSENT from both `branches` and `paused_child_branches` — genuinely
    not-yet-dispatched, re-dispatchable by omission (§25.15.2 obligation 7)."""
    state_summary, anchor = _pause_context_reader()
    fan_out_resume = FanOutResumeState(
        orchestrator_output=orchestrator_output,
        orchestrator_step_id="parent-orch",
        branches=(),
        worker_count=2,
        paused_child_branches=(
            PausedChildBranchResumeState(
                branch_index=0,
                step_id="sub-worker",
                child_workflow_id="wf-child",
                child_snapshot=child_snapshot,
            ),
        ),
    )
    return PauseSnapshot(
        workflow_id="wf-b39-order",
        run_id="wf-b39-order-run",
        step_index=0,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=state_summary,
        snapshot_hash=_compute_snapshot_hash(
            workflow_id="wf-b39-order",
            run_id="wf-b39-order-run",
            step_index=0,
            state_summary=state_summary,
            fan_out_resume=fan_out_resume,
        ),
        created_at=1_700_000_000_000,
        state_ledger_anchor=anchor,
        fan_out_resume=fan_out_resume,
    )


class _OrderRecordingSubWorker:
    """The resumed target's dispatcher: records "sub-worker-start", sleeps
    briefly (a REAL thread sleep — this runs off-loop via `asyncio.to_thread`
    so it does not block the event loop, but it DOES hold this dispatch open
    long enough that a concurrently-dispatched sibling would land its own
    entry strictly BETWEEN start and done if B-39 sequencing were broken),
    then records "sub-worker-done"."""

    def __init__(self, *, order: list[str], order_lock: threading.Lock) -> None:
        self._order = order
        self._lock = order_lock

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        with self._lock:
            self._order.append("sub-worker-start")
        time.sleep(0.1)
        with self._lock:
            self._order.append("sub-worker-done")
        return {"role": "sub-worker"}


class _OrderRecordingEcho:
    """`parent-orch` + `sibling-worker`: records its own step_id the instant
    it is dispatched."""

    def __init__(self, *, order: list[str], order_lock: threading.Lock) -> None:
        self._order = order
        self._lock = order_lock

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        with self._lock:
            self._order.append(str(step.step_id))
        return {"role": str(step.step_id)}


class _OrderRecordingRegistry:
    def __init__(self, *, order: list[str]) -> None:
        self._lock = threading.Lock()
        self._sub_worker = _OrderRecordingSubWorker(order=order, order_lock=self._lock)
        self._echo = _OrderRecordingEcho(order=order, order_lock=self._lock)

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_worker)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)


def _b39_parent_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("parent-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "parent-orch"},
        ),
        WorkflowStep(
            step_id=StepID("sub-worker"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child"},
        ),
        WorkflowStep(
            step_id=StepID("sibling-worker"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "sibling-worker"},
        ),
    ]


def test_b39_resumed_target_dispatches_before_any_sibling() -> None:
    """CP spec v1.102 §3 row 1 (fork §4 item 6, change-note item (e)): a fan-out
    resuming a paused durable-HITL branch (`sub-worker`, branch 0) sequences
    the FRESH, never-dispatched sibling (`sibling-worker`, branch 1) behind
    it — the resumed target dispatches FIRST, fully completes, and ONLY THEN
    does the sibling begin. `sub-worker` holds its dispatch open for 0.1s;
    `sibling-worker` is a near-instant echo — if it dispatched concurrently
    (the pre-B-39 baseline: ALL branches in `branch_plan` fan out together),
    its entry would land strictly BETWEEN "sub-worker-start" and
    "sub-worker-done". Mutation probe: reverting the B-39 phase-0 split
    (dispatching `_resumed_target_plan` + `_rest_plan` together via the
    ordinary concurrent barrier) reproduces exactly that interleaving and
    fails this assertion."""
    order: list[str] = []
    registry = cast(StepDispatcherRegistry, _OrderRecordingRegistry(order=order))
    child_snapshot = _hitl_pending_child_pause_snapshot("wf-child")
    snapshot = _resumed_target_snapshot(
        orchestrator_output={"role": "parent-orch"}, child_snapshot=child_snapshot
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))

    result = execute_workflow(
        _manifest("wf-b39-order", TopologyPattern.ORCHESTRATOR_WORKERS),
        _b39_parent_steps(),
        run_id="wf-b39-order-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
        pause_snapshot_input=snapshot,
    )

    assert result.status is RunStatus.SUCCESS, (
        f"expected a clean resume; got {result.status} fail_class={result.fail_class!r}"
    )
    assert order == ["sub-worker-start", "sub-worker-done", "sibling-worker"], (
        f"resumed-target-first sequencing violated — dispatch order was {order!r} "
        f"(sibling-worker must land strictly AFTER sub-worker-done)"
    )


class _FailingSubWorker:
    """The resumed target's dispatcher RAISES — simulating a Phase-0 failure
    that must not reach `sibling-worker`'s dispatch (still admitted, never
    started)."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        msg = "resumed-target dispatch failed"
        raise RuntimeError(msg)


class _FailingSubWorkerRegistry:
    def __init__(self) -> None:
        self._sub_worker = _FailingSubWorker()
        self._echo = _OrderRecordingEcho(order=[], order_lock=threading.Lock())

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_worker)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)


def test_b39_resumed_target_phase0_failure_releases_rest_plan_admissions() -> None:
    """B-48 lease-leak fix (out-of-family Codex [P1], directly implicating the
    B-39 Phase-0 sequencing added this arc): when the resumed target's Phase-0
    dispatch RAISES, `_rest_plan` (here: `sibling-worker`, branch 1) never
    reaches its own dispatch `finally` — its whole-fan-out-admitted lease
    would leak forever without the `except BaseException` release wrapped
    around the Phase-0 loop in `_cancel_fanout`.
    """
    authority = DefaultCapacityAuthority(frame_budget=4)
    registry = cast(StepDispatcherRegistry, _FailingSubWorkerRegistry())
    child_snapshot = _hitl_pending_child_pause_snapshot("wf-child")
    snapshot = _resumed_target_snapshot(
        orchestrator_output={"role": "parent-orch"}, child_snapshot=child_snapshot
    )
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    ctx_obj.capacity_authority = authority  # type: ignore[attr-defined]
    ctx = cast(DriverContext, ctx_obj)

    result = execute_workflow(
        _manifest("wf-b39-phase0-fail", TopologyPattern.ORCHESTRATOR_WORKERS),
        _b39_parent_steps(),
        run_id="wf-b39-phase0-fail-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
        pause_snapshot_input=snapshot,
    )

    assert result.status is not RunStatus.SUCCESS
    # Mutation probe: dropping the `except BaseException` release wrapper
    # around the Phase-0 loop leaves this short by 1 (`sibling-worker`'s
    # admitted-but-never-dispatched frame) — `available` would read 3, not 4.
    assert authority.available == 4


def test_b39_resumed_target_dispatches_before_any_sibling_under_proceed() -> None:
    """Round-5b codex [P1] #3 "sequence resumed targets on the PROCEED path":
    the SAME B-39 ordering guarantee as
    `test_b39_resumed_target_dispatches_before_any_sibling`, but under a
    PROCEED-resolved persona (`SOLO_DEVELOPER`) — the tier `_cancel_fanout`'s
    own Phase-0 does NOT cover. Before this fix, `_proceed_fanout` dispatched
    the FULL `branch_plan` (including the resumed target) concurrently via a
    single `asyncio.gather`, so `sibling-worker` would land strictly between
    "sub-worker-start" and "sub-worker-done" — exactly the interleaving this
    test's dispatcher pair is built to catch.

    Mutation probe: reverting `_proceed_fanout`'s gate-False branch to gather
    over `branch_plan` again (dropping the Phase-0 loop) reproduces that
    interleaving and fails the order assertion below."""
    order: list[str] = []
    registry = cast(StepDispatcherRegistry, _OrderRecordingRegistry(order=order))
    child_snapshot = _hitl_pending_child_pause_snapshot("wf-child")
    snapshot = _resumed_target_snapshot(
        orchestrator_output={"role": "parent-orch"}, child_snapshot=child_snapshot
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))

    result = execute_workflow(
        _manifest(
            "wf-b39-order-proceed",
            TopologyPattern.ORCHESTRATOR_WORKERS,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
        ),
        _b39_parent_steps(),
        run_id="wf-b39-order-proceed-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
        pause_snapshot_input=snapshot,
    )

    assert result.status is RunStatus.SUCCESS, (
        f"expected a clean resume; got {result.status} fail_class={result.fail_class!r}"
    )
    assert order == ["sub-worker-start", "sub-worker-done", "sibling-worker"], (
        f"resumed-target-first sequencing violated under PROCEED — dispatch order was "
        f"{order!r} (sibling-worker must land strictly AFTER sub-worker-done)"
    )


def test_b39_resumed_target_phase0_failure_under_proceed_does_not_abort_sibling() -> None:
    """PROCEED's defining difference from `_cancel_fanout`'s Phase-0 (which
    this fix could NOT simply copy verbatim): a resumed target's ORDINARY
    failure must not cancel/skip siblings — `sibling-worker` still dispatches
    and the run still degrades to PARTIAL (not FAILED), exactly as an
    ordinary mid-fan-out PROCEED branch failure already does. Only a genuine
    deadline strike may abort the rest under PROCEED.

    Mutation probe: re-raising the Phase-0 failure instead of capturing it as
    that branch's own result (i.e. letting `_FailingSubWorker`'s exception
    propagate straight out of the `for _target_plan in _resumed_target_plan`
    loop) would prevent `sibling-worker` from ever dispatching — this
    assertion catches that."""
    registry = cast(StepDispatcherRegistry, _FailingSubWorkerRegistry())
    child_snapshot = _hitl_pending_child_pause_snapshot("wf-child")
    snapshot = _resumed_target_snapshot(
        orchestrator_output={"role": "parent-orch"}, child_snapshot=child_snapshot
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))

    result = execute_workflow(
        _manifest(
            "wf-b39-phase0-fail-proceed",
            TopologyPattern.ORCHESTRATOR_WORKERS,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
        ),
        _b39_parent_steps(),
        run_id="wf-b39-phase0-fail-proceed-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
        pause_snapshot_input=snapshot,
    )

    assert result.status is RunStatus.PARTIAL, (
        f"a resumed-target failure must degrade to PARTIAL under proceed, not abort the "
        f"sibling; got {result.status} fail_class={result.fail_class!r}"
    )
    assert result.partial_state is not None
    # `sibling-worker` DID dispatch (its echoed output is present) — proof the
    # Phase-0 failure was captured as the resumed target's own result, not
    # re-raised to skip the rest.
    assert "sibling-worker" in str(result.partial_state)


def _two_resumed_targets_snapshot(*, orchestrator_output: dict[str, Any]) -> PauseSnapshot:
    """Two resumed durable-HITL targets (`sub-worker-a` branch 0, `sub-worker-b`
    branch 1) + one genuinely fresh sibling (`sibling-worker`, branch 2, absent
    from both `branches` and `paused_child_branches`)."""
    state_summary, anchor = _pause_context_reader()
    fan_out_resume = FanOutResumeState(
        orchestrator_output=orchestrator_output,
        orchestrator_step_id="parent-orch",
        branches=(),
        worker_count=3,
        paused_child_branches=(
            PausedChildBranchResumeState(
                branch_index=0,
                step_id="sub-worker-a",
                child_workflow_id="wf-child-a",
                child_snapshot=_hitl_pending_child_pause_snapshot("wf-child-a"),
            ),
            PausedChildBranchResumeState(
                branch_index=1,
                step_id="sub-worker-b",
                child_workflow_id="wf-child-b",
                child_snapshot=_hitl_pending_child_pause_snapshot("wf-child-b"),
            ),
        ),
    )
    return PauseSnapshot(
        workflow_id="wf-b39-two-resumed",
        run_id="wf-b39-two-resumed-run",
        step_index=0,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=state_summary,
        snapshot_hash=_compute_snapshot_hash(
            workflow_id="wf-b39-two-resumed",
            run_id="wf-b39-two-resumed-run",
            step_index=0,
            state_summary=state_summary,
            fan_out_resume=fan_out_resume,
        ),
        created_at=1_700_000_000_000,
        state_ledger_anchor=anchor,
        fan_out_resume=fan_out_resume,
    )


def _two_resumed_targets_parent_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("parent-orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "parent-orch"},
        ),
        WorkflowStep(
            step_id=StepID("sub-worker-a"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-a"},
        ),
        WorkflowStep(
            step_id=StepID("sub-worker-b"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-b"},
        ),
        WorkflowStep(
            step_id=StepID("sibling-worker"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "sibling-worker"},
        ),
    ]


class _FirstResumedTargetFailsRegistry:
    """`sub-worker-a` (the FIRST resumed target in Phase-0 iteration order)
    RAISES synchronously — the Phase-0 loop never reaches `sub-worker-b` (the
    SECOND resumed target) at all. `sub-worker-b` would also raise if it were
    ever dispatched (proving, if this test's mutation probe is right, that it
    genuinely never runs — not that it ran and happened to succeed)."""

    def __init__(self) -> None:
        self._echo = _OrderRecordingEcho(order=[], order_lock=threading.Lock())

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        msg = f"resumed-target dispatch failed at {step.step_id}"
        raise RuntimeError(msg)


def test_b39_phase0_strike_on_first_of_two_resumed_targets_releases_the_second() -> None:
    """Round-6 concurrency-lens BLOCK: the Phase-0 `except BaseException` release
    handler released only `_rest_plan`'s admissions, never any `_resumed_target_plan`
    entry left un-dispatched when the strike lands on a NON-LAST Phase-0 iteration.
    With 2 resumed targets (`sub-worker-a` branch 0, `sub-worker-b` branch 1) and
    `sub-worker-a` raising on Phase-0's FIRST iteration, `sub-worker-b` (Phase-0's
    SECOND, never-reached iteration) previously leaked its admitted frame(s)
    forever — on top of `sibling-worker`'s (`_rest_plan`) already-covered leak.

    Mutation probe: reverting to releasing only `_rest_plan` (dropping
    `_resumed_target_plan[_resumed_index + 1:]` from the release set) leaves
    `authority.available` short by `sub-worker-b`'s admitted frames after this
    run — this test's `available == frame_budget` assertion would then fail."""
    authority = DefaultCapacityAuthority(frame_budget=12)
    registry = cast(StepDispatcherRegistry, _FirstResumedTargetFailsRegistry())
    snapshot = _two_resumed_targets_snapshot(orchestrator_output={"role": "parent-orch"})
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    ctx_obj.capacity_authority = authority  # type: ignore[attr-defined]
    ctx = cast(DriverContext, ctx_obj)

    result = execute_workflow(
        _manifest("wf-b39-two-resumed-fail"),
        _two_resumed_targets_parent_steps(),
        run_id="wf-b39-two-resumed-fail-run",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
        pause_snapshot_input=snapshot,
    )

    assert result.status is not RunStatus.SUCCESS
    assert authority.available == 12, (
        f"expected full frame-budget recovery (12); got {authority.available} — "
        f"sub-worker-b's admission leaked"
    )


class _CancelledOnFirstResumedTargetRegistry:
    """`sub-worker-a` (the FIRST resumed target) raises `asyncio.CancelledError`
    synchronously — `_proceed_worker`'s Phase-0 loop has an INNER
    `except BaseException as _resumed_exc:` that captures an ORDINARY failure
    as that branch's own result (never aborting — `test_b39_resumed_target_
    phase0_failure_under_proceed_does_not_abort_sibling` above pins this), so
    only a `CancelledError` (the explicit `except asyncio.CancelledError:
    raise` ABOVE that inner catch-all) reaches the OUTER `except BaseException:`
    that this fix's release wrapper guards — the genuine "Phase-0 strike"
    shape under PROCEED."""

    def __init__(self) -> None:
        self._echo = _OrderRecordingEcho(order=[], order_lock=threading.Lock())

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self._echo)
        raise StepKindDispatcherNotBoundError(step_kind)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        raise asyncio.CancelledError(f"deadline strike at {step.step_id}")


def test_b39_phase0_strike_on_first_of_two_resumed_targets_releases_the_second_under_proceed() -> (
    None
):
    """Same fix as `test_b39_phase0_strike_on_first_of_two_resumed_targets_
    releases_the_second`, but for `_proceed_worker`'s own twin Phase-0 loop
    (round-6 concurrency-lens BLOCK named all 4 symmetric sites; this one and
    its `_proceed_fanout`/`_cancel_fanout` PARALLELIZATION siblings had zero
    witness before this test — test-witness lens round 7).

    Mutation probe: reverting `_proceed_worker`'s release set to
    `_rest_plan`-only (dropping `_resumed_target_plan[_resumed_index + 1:]`)
    leaves `authority.available` short by `sub-worker-b`'s admitted frames.

    A `CancelledError` is a `BaseException`, not an `Exception` — it
    propagates straight out of `execute_workflow` (no top-level `except
    Exception:` swallows it, by design: cancellation must always reach the
    caller), so this test catches it directly rather than reading a
    `RunResult.status`."""
    authority = DefaultCapacityAuthority(frame_budget=12)
    registry = cast(StepDispatcherRegistry, _CancelledOnFirstResumedTargetRegistry())
    snapshot = _two_resumed_targets_snapshot(orchestrator_output={"role": "parent-orch"})
    ctx_obj = _CtxP(ledger=_RecordingLedger(), emitter=_Emitter())
    ctx_obj.capacity_authority = authority  # type: ignore[attr-defined]
    ctx = cast(DriverContext, ctx_obj)

    with pytest.raises(asyncio.CancelledError):
        execute_workflow(
            _manifest(
                "wf-b39-two-resumed-fail-proceed",
                TopologyPattern.ORCHESTRATOR_WORKERS,
                persona_tier=PersonaTier.SOLO_DEVELOPER,
            ),
            _two_resumed_targets_parent_steps(),
            run_id="wf-b39-two-resumed-fail-proceed-run",
            ctx=ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=registry,
            pause_snapshot_input=snapshot,
        )

    assert authority.available == 12, (
        f"expected full frame-budget recovery (12); got {authority.available} — "
        f"sub-worker-b's admission leaked under the PROCEED-tier Phase-0 loop"
    )


# ---------------------------------------------------------------------------
# B-60 — Phase-0 resumed-target dispatch must RE-RAISE the fence signal.
# ---------------------------------------------------------------------------


def _b60_linear_child_snapshot() -> PauseSnapshot:
    """A hash-valid LINEAR child snapshot (the paused-child carrier input)."""
    return asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id="wf-child",
            run_id="child-run",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        )
    )


class _B60PausingThenTrippingSubAgent:
    """First run: BOTH sub-agent workers' children pause (SubAgentChildPausedError
    with a hash-valid child snapshot). Resume: the FIRST resumed target's
    re-dispatch raises `DispatchFenceTrippedSignal` (the real dispatcher's
    effect-entry refusal after an ancestor trip); the second must never be
    re-dispatched."""

    def __init__(self) -> None:
        self.first_run_calls: list[str] = []
        self.resume_calls: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

        step_id = str(step.step_id)
        child_resume = getattr(step_context, "child_resume_snapshot", None)
        if child_resume is None:
            self.first_run_calls.append(step_id)
            raise SubAgentChildPausedError(
                child_workflow_id=f"wf-child-{step_id}",
                child_snapshot=_b60_linear_child_snapshot(),
            )
        self.resume_calls.append(step_id)
        raise DispatchFenceTrippedSignal


class _B60Registry:
    def __init__(self, *, sub_agent: Any) -> None:
        self._sub_agent = sub_agent
        self.echo = _CountingDispatcher()

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agent)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return cast(StepDispatcher, self.echo)
        raise StepKindDispatcherNotBoundError(step_kind)


def _b60_sub_worker(index: int) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"sub-worker-{index}"),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={"child_workflow_id": f"wf-child-sub-worker-{index}"},
    )


def _b60_phase0_run(topology: TopologyPattern) -> None:
    from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

    sub_agent = _B60PausingThenTrippingSubAgent()
    registry = cast(StepDispatcherRegistry, _B60Registry(sub_agent=sub_agent))
    steps = (
        [_b60_sub_worker(1), _b60_sub_worker(2)]
        if topology is TopologyPattern.PARALLELIZATION
        else [
            WorkflowStep(
                step_id=StepID("parent-orch"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={"role": "parent-orch"},
            ),
            _b60_sub_worker(1),
            _b60_sub_worker(2),
        ]
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-b60", topology),
        steps,
        run_id="run-b60",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    resume_state = snap.fan_out_resume or snap.peer_fan_out_resume
    assert resume_state is not None
    assert len(resume_state.paused_child_branches) == 2

    ctx2 = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    with pytest.raises(DispatchFenceTrippedSignal):
        execute_workflow(
            _manifest("wf-b60", topology),
            steps,
            run_id="run-b60",
            ctx=ctx2,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=registry,
            pause_snapshot_input=snap,
        )
    # THE load-bearing assertion (codex round-2 on PR #1075, reproduced):
    # the signal was NOT captured as a branch result — the SECOND resumed
    # target was never re-dispatched.
    assert len(sub_agent.resume_calls) == 1


def test_b60_phase0_resumed_target_fence_signal_reraise_orchestrator() -> None:
    """Phase-0 (ORCHESTRATOR_WORKERS): a fence signal raised by the first
    resumed target's re-dispatch propagates — never captured as an ordinary
    branch result that lets the second target and fresh siblings proceed."""
    _b60_phase0_run(TopologyPattern.ORCHESTRATOR_WORKERS)


def test_b60_phase0_resumed_target_fence_signal_reraise_parallelization() -> None:
    """Phase-0 (PARALLELIZATION twin): the peer fan-out's own resumed-target
    loop has the identical capture shape — pinned separately so a
    single-arm regression cannot slip."""
    _b60_phase0_run(TopologyPattern.PARALLELIZATION)


def test_b60_phase0_resumed_target_fence_signal_reraise_proceed_tier() -> None:
    """Phase-0 under the PROCEED tier (SOLO): the sequential resumed-target
    loop's own `except _DispatchFenceTrippedSignal: raise` arm — the capture
    here is `results[ordinal] = exc`, not a TaskGroup, so this pins the
    loop-arm fix separately from the group unwrap."""
    from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

    sub_agent = _B60PausingThenTrippingSubAgent()
    registry = cast(StepDispatcherRegistry, _B60Registry(sub_agent=sub_agent))
    steps = [_b60_sub_worker(1), _b60_sub_worker(2)]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-b60-proceed", TopologyPattern.PARALLELIZATION),
        steps,
        run_id="run-b60p",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert paused.status is RunStatus.PAUSED

    ctx2 = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    with pytest.raises(DispatchFenceTrippedSignal):
        execute_workflow(
            _manifest(
                "wf-b60-proceed", TopologyPattern.PARALLELIZATION, PersonaTier.SOLO_DEVELOPER
            ),
            steps,
            run_id="run-b60p",
            ctx=ctx2,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=registry,
            pause_snapshot_input=paused.pause_snapshot,
        )
    assert len(sub_agent.resume_calls) == 1


def test_b60_fresh_branch_fence_signal_not_captured_by_rest_gather() -> None:
    """The rest-plan gather (`return_exceptions=True`) captures BaseExceptions
    as results — the post-gather scan must re-raise a captured fence signal
    instead of letting the fold convert it into a branch failure/PARTIAL.
    Fresh 2-branch PROCEED fan-out; branch 'b' raises the signal."""
    from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

    class _SignalRaisingDispatcher:
        def __init__(self) -> None:
            self.dispatched: list[str] = []

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            step_id = str(step.step_id)
            self.dispatched.append(step_id)
            if step_id == "b":
                raise DispatchFenceTrippedSignal
            return {"ok": step_id}

    dispatcher = _SignalRaisingDispatcher()

    class _Reg:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            return cast(StepDispatcher, dispatcher)

    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    with pytest.raises(DispatchFenceTrippedSignal):
        execute_workflow(
            _manifest("wf-b60-rest", TopologyPattern.PARALLELIZATION, PersonaTier.SOLO_DEVELOPER),
            [
                WorkflowStep(
                    step_id=StepID("a"),
                    step_kind=StepKind.DECLARATIVE_STEP,
                    step_payload={},
                ),
                WorkflowStep(
                    step_id=StepID("b"),
                    step_kind=StepKind.DECLARATIVE_STEP,
                    step_payload={},
                ),
            ],
            run_id="run-b60r",
            ctx=ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, _Reg()),
        )


def test_b60_trip_after_final_drain_stops_post_join_synthesis() -> None:
    """B-60 (codex round-3 on PR #1075, reproduced): a token tripping as the
    LAST branch entry drains must stop the terminal POST_JOIN_SYNTHESIS
    (an LLM dispatch + its disclosing append — both effects) from
    beginning. Deterministic: the ledger double trips on branch 1's
    terminal drain append (the final drained entry); the synthesis consult
    then refuses before the synthesis dispatcher is ever looked up."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )

    token = DispatchCancelToken()

    class _TrippingLedger(_RecordingLedger):
        def append(self, payload: Any, write_key: Any) -> Any:
            result = super().append(payload, write_key)
            bm = getattr(payload, "branch_metadata", None)
            if bm is not None and bm.branch_index == 1 and bm.terminal_status == "completed":
                token.trip()
            return result

    ledger = _TrippingLedger()
    dispatcher = _CountingDispatcher()

    class _Reg:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            if step_kind in (StepKind.DECLARATIVE_STEP, StepKind.POST_JOIN_SYNTHESIS):
                return cast(StepDispatcher, dispatcher)
            raise StepKindDispatcherNotBoundError(step_kind)

    ctx = cast(DriverContext, _CtxP(ledger=ledger, emitter=_Emitter()))
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            execute_workflow(
                _manifest(
                    "wf-b60-synth", TopologyPattern.PARALLELIZATION, PersonaTier.SOLO_DEVELOPER
                ),
                [
                    WorkflowStep(
                        step_id=StepID("a"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
                    ),
                    WorkflowStep(
                        step_id=StepID("b"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
                    ),
                    _synthesis_step(),
                ],
                run_id="run-b60s",
                ctx=ctx,
                default_model_binding=_DEFAULT_BINDING,
                step_dispatchers=cast(StepDispatcherRegistry, _Reg()),
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
    # Both branches ran; the synthesis never began (no synthesis dispatch,
    # no synthesis ledger entry).
    assert "synthesis" not in dispatcher.dispatched
    assert not any(
        getattr(p, "branch_metadata", None) is None and "synthesis" in str(p.action_id)
        for p, _k in ledger.appends
    )


def test_b60_group_wrapped_fence_signal_not_captured_by_rest_gather() -> None:
    """Codex round-5 on PR #1075: a branch whose internal TaskGroup wraps
    the fence signal delivers a `BaseExceptionGroup` RESULT to the rest
    gather — the scan must unwrap it, never fold it into PARTIAL."""
    from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

    class _GroupRaisingDispatcher:
        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            if str(step.step_id) == "b":
                raise BaseExceptionGroup("inner", [DispatchFenceTrippedSignal()])
            return {"ok": str(step.step_id)}

    class _Reg:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            return cast(StepDispatcher, _GroupRaisingDispatcher())

    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    with pytest.raises(DispatchFenceTrippedSignal):
        execute_workflow(
            _manifest("wf-b60-grp", TopologyPattern.PARALLELIZATION, PersonaTier.SOLO_DEVELOPER),
            [
                WorkflowStep(
                    step_id=StepID("a"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
                ),
                WorkflowStep(
                    step_id=StepID("b"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
                ),
            ],
            run_id="run-b60g",
            ctx=ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, _Reg()),
        )


def test_b60_phase0_group_wrapped_fence_signal_reraise_proceed_tier() -> None:
    """Codex round-6 on PR #1075: a resumed target whose nested TaskGroup
    wraps the fence signal delivers a `BaseExceptionGroup` to the Phase-0
    capture loop — the group arm must split-and-reraise, never store it as
    an ordinary branch result that lets the second target proceed."""
    from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

    class _GroupTrippingSubAgent(_B60PausingThenTrippingSubAgent):
        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            child_resume = getattr(step_context, "child_resume_snapshot", None)
            if child_resume is None:
                return super().dispatch(binding, step, step_context=step_context)
            self.resume_calls.append(str(step.step_id))
            raise BaseExceptionGroup("inner", [DispatchFenceTrippedSignal()])

    sub_agent = _GroupTrippingSubAgent()
    registry = cast(StepDispatcherRegistry, _B60Registry(sub_agent=sub_agent))
    steps = [_b60_sub_worker(1), _b60_sub_worker(2)]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-b60-p0g", TopologyPattern.PARALLELIZATION),
        steps,
        run_id="run-b60pg",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert paused.status is RunStatus.PAUSED

    ctx2 = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    with pytest.raises(DispatchFenceTrippedSignal):
        execute_workflow(
            _manifest("wf-b60-p0g", TopologyPattern.PARALLELIZATION, PersonaTier.SOLO_DEVELOPER),
            steps,
            run_id="run-b60pg",
            ctx=ctx2,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=registry,
            pause_snapshot_input=paused.pause_snapshot,
        )
    assert len(sub_agent.resume_calls) == 1


def test_b60_depth2_nested_group_fence_signal_unwrapped() -> None:
    """Merge-gate test-witness lens M3: the leaf-extraction WHILE loop in
    `_reraise_fence_signal_from_group` must survive depth-2 nesting (the
    round-5/6 production shape: branch TaskGroup inside a phase TaskGroup)
    — a single-level unwrap would re-raise a GROUP, not the signal."""
    from harness_cp.sub_agent_dispatch_cancellation import DispatchFenceTrippedSignal

    class _NestedGroupDispatcher:
        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            if str(step.step_id) == "b":
                raise BaseExceptionGroup(
                    "outer", [BaseExceptionGroup("inner", [DispatchFenceTrippedSignal()])]
                )
            return {"ok": str(step.step_id)}

    class _Reg:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            return cast(StepDispatcher, _NestedGroupDispatcher())

    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    with pytest.raises(DispatchFenceTrippedSignal):
        execute_workflow(
            _manifest("wf-b60-d2", TopologyPattern.PARALLELIZATION, PersonaTier.SOLO_DEVELOPER),
            [
                WorkflowStep(
                    step_id=StepID("a"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
                ),
                WorkflowStep(
                    step_id=StepID("b"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
                ),
            ],
            run_id="run-b60d2",
            ctx=ctx,
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, _Reg()),
        )


class HITLPauseRequestedSignal(BaseException):
    """Test-local stand-in for the runtime `hitl_gate_composer.HITLPauseRequestedSignal`
    — a `BaseException`, name-matched by the driver (harness-cp cannot import
    harness-runtime). Mirrors `test_workflow_driver_parallelization_pause.py`'s
    identically-named test-local class."""


class _WarmupCohortLeaderGateDispatcherOW:
    """merge-gate test-witness lens round 1 [BLOCK] — the ORCHESTRATOR_WORKERS
    mirror of `_execute_parallelization`'s round-6 `_pre_dispatch_gate_owning_
    carried_forward` fix (`workflow_driver.py`'s `FanOutResumeState` construction
    site) had zero test coverage. worker-0-sub and worker-1-sub form a size-2
    SUB_AGENT_DISPATCH `cohort_key` cohort, so worker-0-sub (the lower ordinal)
    is the §25.19 warm-up Phase-1 leader and worker-1-sub is deferred to Phase 2.
    The leader re-raises the pre-dispatch HITL signal (still unresolved) on
    every call, which fails Phase 1 — Phase 2 (the follower) is never even
    attempted this round."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "ow-warmup-cohort-k" if step.step_kind is StepKind.SUB_AGENT_DISPATCH else None

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        self.dispatched.append(step_id)
        raise HITLPauseRequestedSignal()


def test_ow_worker_resume_carries_forward_pre_dispatch_gate_owner_withheld_by_warmup() -> None:
    """merge-gate test-witness lens round 1 [BLOCK] — the ORCHESTRATOR_WORKERS
    analogue of `test_workflow_driver_parallelization_pause.py`'s
    `test_peer_resume_carries_forward_pre_dispatch_gate_owner_withheld_by_warmup`.
    A repeated resume starting with a recovered pre-dispatch gate-owning worker
    must not silently drop it when §25.19 warm-up scheduling withholds it this
    round (the leader re-pauses before its cohort follower is ever dispatched).
    Exercises `_execute_orchestrator_workers`'s own `FanOutResumeState`
    construction site (workflow_driver.py's `_pre_dispatch_gate_owning_carried_
    forward` union), which the PARALLELIZATION regression test does not reach —
    `HIERARCHICAL_DELEGATION` reuses this same function recursively."""
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-0"},
        ),
        WorkflowStep(
            step_id=StepID("worker-1-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-1"},
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-ow-pp"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateDispatcherOW()),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert [b.branch_index for b in snap.fan_out_resume.pre_dispatch_gate_owning_branches] == [
        0,
        1,
    ], "round 1 (no warm-up cohort) must record BOTH SUB_AGENT_DISPATCH workers"

    resume_dispatcher = _WarmupCohortLeaderGateDispatcherOW()
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-ow-pp"),
        steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=snap,
    )
    assert resume_dispatcher.dispatched == ["worker-0-sub"], (
        "worker-1-sub must be genuinely WITHHELD by the warm-up split this round "
        f"(never reach dispatch()) — got {resume_dispatcher.dispatched!r}"
    )
    assert resumed.status is RunStatus.PAUSED
    resumed_snap = resumed.pause_snapshot
    assert resumed_snap is not None
    resumed_fr = resumed_snap.fan_out_resume
    assert resumed_fr is not None
    assert sorted(b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches) == [
        0,
        1,
    ], (
        "worker-1-sub (withheld, neither re-fired nor resolved this round) must be "
        "CARRIED FORWARD from the recovered set, not silently dropped"
    )
    _carried = next(b for b in resumed_fr.pre_dispatch_gate_owning_branches if b.branch_index == 1)
    assert _carried.step_id == "worker-1-sub"
    assert _carried.step_kind == StepKind.SUB_AGENT_DISPATCH.value
    assert _carried.child_workflow_id == "wf-child-1"


class _PreDispatchGateDispatcherOW:
    """Round-1 dispatcher: orchestrator completes; both workers unconditionally
    raise the pre-dispatch HITL signal (no cohort key — no warm-up split, so
    BOTH get a live attempt this round, mirroring
    `test_workflow_driver_parallelization_pause.py`'s `_PreDispatchGateDispatcher`)."""

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        raise HITLPauseRequestedSignal()


class _RoundTwoResolveOneFireOtherDispatcherOW:
    """merge-gate test-witness lens round 2 [BLOCK] — the ORCHESTRATOR_WORKERS
    mirror of `_execute_parallelization`'s `HITLDeliveryCell` CONSTRUCTION site
    (workflow_driver.py ~12066-12076, the actual delivery/liveness half of the
    B-72 fix, not merely the carry-forward counting half) had zero test
    coverage anywhere in the repo — round 1's withheld-branch test only proved
    the COUNTING side survives a repeated resume, never that a delivered cell
    is actually consumed at this site. worker-0-sub consumes its delivered
    cell and completes; worker-1-sub — dispatched for the first time ever,
    since round 1's warm-up split withheld it — raises the pause signal
    unconditionally (a fresh, not-yet-recovered gate owner)."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "worker-0-sub":
            holder = getattr(step_context, "hitl_delivery_holder", None)
            resolved = holder.consume_and_clear() if holder is not None else None
            if resolved is not None:
                return {"role": "worker-0-sub", "resolved": True}
            raise HITLPauseRequestedSignal()
        raise HITLPauseRequestedSignal()


def test_ow_worker_resume_delivers_and_excludes_resolved_pre_dispatch_gate_owner() -> None:
    """merge-gate test-witness lens round 2 [BLOCK] — the ORCHESTRATOR_WORKERS
    analogue of `test_workflow_driver_parallelization_pause.py`'s
    `test_peer_resume_excludes_pre_dispatch_gate_owner_resolved_this_round`.
    Exercises the `HITLDeliveryCell` CONSTRUCTION site at `_execute_orchestrator_
    workers` (workflow_driver.py ~12066-12076) — the required-OUTCOME delivery
    half of CP spec v1.108 §1.1(c), not just the carry-forward counting half —
    AND proves the carry-forward union's exclusion conjuncts hold at the
    `FanOutResumeState` construction site too: worker-0 resolves this round
    (consumes its delivered cell, completes) and must be EXCLUDED from the new
    snapshot; worker-1 (fresh this round) must be present.

    Uses the SAME real §25.19 warm-up cohort split as the withheld-branch test
    (deterministic — no thread races) to get worker-1 genuinely untouched in
    round 1, so worker-0 is the resume-cycle-wide SOLE unaddressed member and
    actually receives a delivery cell in round 2."""
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-0"},
        ),
        WorkflowStep(
            step_id=StepID("worker-1-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-1"},
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    round1_dispatcher = _WarmupCohortLeaderGateDispatcherOW()
    paused = execute_workflow(
        _manifest("wf-ow-excl"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, round1_dispatcher),
    )
    assert round1_dispatcher.dispatched == ["worker-0-sub"], (
        "worker-1-sub must be genuinely WITHHELD by the warm-up split in round 1 "
        f"(never reach dispatch()) — got {round1_dispatcher.dispatched!r}"
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert [b.branch_index for b in snap.fan_out_resume.pre_dispatch_gate_owning_branches] == [0], (
        "round 1: worker-0-sub (the leader) is the SOLE recorded pre-dispatch gate owner"
    )

    resume_dispatcher = _RoundTwoResolveOneFireOtherDispatcherOW()
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resume_context = ResumeContext(
        hitl_response=HITLResult(
            response=HITLResponse.APPROVE,
            timestamp="2026-07-25T00:00:00Z",
            audit_ledger_entry_id=EntryID("e-b72-ow-exclusion"),
            response_summary_hash="d" * 64,
        )
    )
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_context)
    assert eligible_run_id is not None, (
        "worker-0-sub must be the resume-cycle-wide SOLE unaddressed gate-owning "
        "member so it actually receives a delivery cell this round"
    )
    resumed = execute_workflow(
        _manifest("wf-ow-excl"),
        steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_context,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
    )
    assert sorted(resume_dispatcher.dispatched) == ["worker-0-sub", "worker-1-sub"], (
        f"both workers must be re-dispatched this round — got {resume_dispatcher.dispatched!r}"
    )
    assert resumed.status is RunStatus.PAUSED, (
        f"expected worker-1-sub's fresh pre-dispatch pause to re-pause the run; "
        f"got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )
    resumed_snap = resumed.pause_snapshot
    assert resumed_snap is not None
    resumed_fr = resumed_snap.fan_out_resume
    assert resumed_fr is not None
    assert sorted(b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches) == [1], (
        "worker-0 RESOLVED this round (consumed its DELIVERED cell, completed) and "
        "must be EXCLUDED from the carried-forward set — only worker-1 (the fresh "
        f"this-round pause) should remain; got "
        f"{sorted(b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches)!r}"
    )


# ---------------------------------------------------------------------------
# B-81 close-out (1) — the OW mirror of PARALLELIZATION's own pre-dispatch
# gate-owning material-diff witnesses (test_workflow_driver_parallelization_
# pause.py's test_peer_resume_rejects_pre_dispatch_gate_owning_kind_changed /
# _workflow_id_swap / test_peer_resume_accepts_unchanged_pre_action_gated_
# inference_step), ported against _execute_orchestrator_workers's OWN
# `_resume_body_mismatch` closure (workflow_driver.py ~11605-11653) — this
# code path was symmetric with PARALLELIZATION's but had ZERO direct test
# coverage of its own before this arc (merge-gate test-witness lens round 2).
# ---------------------------------------------------------------------------


def test_ow_worker_resume_rejects_pre_dispatch_gate_owning_kind_changed() -> None:
    """B-81 (1) — a same-`step_id` edit that swaps a pre-dispatch gate-owning OW
    branch's `step_kind` must fail closed, mirroring PARALLELIZATION's own guard
    at its structurally-identical `_resume_body_mismatch` closure.

    Mutation-probe note: disabling the kind-changed guard does NOT flip
    `status` (a downstream workflow-id-unreadable guard still catches the
    malformed resume and returns FAILED) — this test's actual discriminating
    power is the `fail_class` substring assertion below, not the status
    assertion. Verified via mutation probe 2026-07-26."""
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-ow-kind"},
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-ow-kind"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateDispatcherOW()),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert len(snap.fan_out_resume.pre_dispatch_gate_owning_branches) == 1
    assert snap.fan_out_resume.pre_dispatch_gate_owning_branches[0].branch_index == 0

    # Resume with worker-0-sub's step_kind CHANGED to DECLARATIVE_STEP (same step_id).
    changed_steps = [
        steps[0],
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": 0},
        ),
    ]
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-ow-kind"),
        changed_steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(_CountingDispatcher()),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "pre-dispatch-gate-owning-kind-changed" in (resumed.fail_class or "")


def test_ow_worker_resume_rejects_pre_dispatch_gate_owning_workflow_id_swap() -> None:
    """B-81 (1) — a same-`step_id`, same-`step_kind` edit that swaps a pre-dispatch
    gate-owning OW `SUB_AGENT_DISPATCH` branch's target `child_workflow_id` must
    fail closed, mirroring PARALLELIZATION's own guard.

    Mutation-probe note: unlike the sibling kind-changed test above, disabling
    THIS guard flips `status` PAUSED -> FAILED directly (no downstream guard
    catches it) — `status` itself is load-bearing here, not just `fail_class`.
    Verified via mutation probe 2026-07-26."""
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-ow-swap"},
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-ow-swap"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _PreDispatchGateDispatcherOW()),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert (
        snap.fan_out_resume.pre_dispatch_gate_owning_branches[0].child_workflow_id
        == "wf-child-ow-swap"
    )

    # Resume with worker-0-sub's step_payload edited to target a DIFFERENT child
    # workflow — same step_id, same step_kind (so the identity/kind guards pass).
    changed_steps = [
        steps[0],
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-ow-SWAPPED"},
        ),
    ]
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-ow-swap"),
        changed_steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(_CountingDispatcher()),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.FAILED
    assert "pre-dispatch-gate-owning-workflow-id-changed" in (resumed.fail_class or "")


class _PreDispatchGateOnInferenceStepDispatcherOW:
    """OW mirror of `test_workflow_driver_parallelization_pause.py`'s
    `_PreDispatchGateOnInferenceStepDispatcher` — a `PRE_ACTION`-gated
    `INFERENCE_STEP` worker ALSO raises `HITLPauseRequestedSignal` pre-dispatch
    (not only `SUB_AGENT_DISPATCH`); an UNCHANGED resume of this exact shape
    must succeed, not be falsely rejected as a kind-changed material diff."""

    def __init__(self) -> None:
        self._raised = False
        self.dispatched: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "worker-0-inf" and not self._raised:
            self._raised = True
            raise HITLPauseRequestedSignal()
        return {"role": step_id, "echoed": dict(step.step_payload)}


def test_ow_worker_resume_accepts_unchanged_pre_action_gated_inference_step() -> None:
    """B-81 (1) — the OW mirror of PARALLELIZATION's own round-5 regression:
    `PRE_ACTION` can gate an `INFERENCE_STEP`/`TOOL_STEP` OW worker too, raising
    the SAME name-matched signal; an UNCHANGED resume of that worker must
    succeed, not be rejected as a false `pre-dispatch-gate-owning-kind-changed`.

    Mutation-probe note: hardcoding the kind comparison's RHS to the
    `SUB_AGENT_DISPATCH` literal (the exact round-5 regression shape, in place
    of comparing against the captured `pg.step_kind`) flips this test's
    outcome SUCCESS -> FAILED with `fail_class` reporting a spurious
    kind-changed diff for an actually-unchanged INFERENCE_STEP resume —
    confirming this test would catch the regression it was ported to guard
    against. Verified via mutation probe 2026-07-26."""
    steps = [
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
    dispatcher = _PreDispatchGateOnInferenceStepDispatcherOW()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    paused = execute_workflow(
        _manifest("wf-ow-inf"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    pre_dispatch = snap.fan_out_resume.pre_dispatch_gate_owning_branches
    assert len(pre_dispatch) == 1
    assert pre_dispatch[0].branch_index == 0
    assert pre_dispatch[0].step_kind == StepKind.INFERENCE_STEP.value
    assert pre_dispatch[0].child_workflow_id is None, (
        "an INFERENCE_STEP branch has no child_workflow_id to capture — must "
        "stay None, not spuriously read a payload key that doesn't exist"
    )

    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resumed = execute_workflow(
        _manifest("wf-ow-inf"),
        steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        pause_snapshot_input=snap,
    )
    assert resumed.status is RunStatus.SUCCESS, (
        f"expected an UNCHANGED PRE_ACTION-gated INFERENCE_STEP resume to succeed "
        f"(no material diff at all); got status={resumed.status!r} "
        f"fail_class={resumed.fail_class!r}"
    )


class _RoundTwoResolveOnePausedChildFireOtherDispatcherOW:
    """B-81 close-out (2) — the OW mirror of `test_workflow_driver_parallelization_
    pause.py`'s `_RoundTwoResolveOnePausedChildFireOtherDispatcher`: worker-0-sub
    consumes its delivered `HITLDeliveryCell` and acts as a faithful `RuntimeSubAgentDispatcher`
    double — dispatching a REAL nested child `execute_workflow` that itself PAUSES (the same
    `_GrandchildDispatcher` shape `_FaithfulSubAgentDispatcher` uses above) and re-raising
    `SubAgentChildPausedError`. worker-1-sub raises the pause signal synchronously and
    typically completes first, so this exercise most often lands in the in-flight-cancellation-
    race catch rather than the direct own-dispatch catch — both write
    `paused_child_dispositions[branch_index]` identically (merge-gate test-witness lens,
    PR #1119), so either path equally exercises the exclusion conjunct this test targets.
    worker-1-sub, dispatched for the first time (withheld by round 1's warm-up
    cohort), raises the pause signal unconditionally — a fresh gate owner."""

    def __init__(self, *, child_dispatcher: _GrandchildDispatcher) -> None:
        self._child_dispatcher = child_dispatcher
        self.dispatched: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        self.dispatched.append(step_id)
        if step_id == "worker-0-sub":
            holder = getattr(step_context, "hitl_delivery_holder", None)
            resolved = holder.consume_and_clear() if holder is not None else None
            assert resolved is not None, "worker-0-sub must receive its delivery cell this round"
            child_resume = getattr(step_context, "child_resume_snapshot", None)
            child_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
            child_result = execute_workflow(
                _manifest("wf-child-0", TopologyPattern.ORCHESTRATOR_WORKERS),
                _child_steps(),
                run_id="child-run-0",
                ctx=child_ctx,
                default_model_binding=_DEFAULT_BINDING,
                step_dispatchers=_registry(self._child_dispatcher),
                pause_snapshot_input=child_resume,
            )
            assert child_result.status is RunStatus.PAUSED, (
                "the nested child must itself pause (grandchild-1 fails under "
                f"cascade_policy=pause); got status={child_result.status!r}"
            )
            assert child_result.pause_snapshot is not None
            raise SubAgentChildPausedError(
                child_workflow_id="wf-child-0", child_snapshot=child_result.pause_snapshot
            )
        raise HITLPauseRequestedSignal()


def test_ow_worker_resume_excludes_pre_dispatch_gate_owner_paused_child_this_round() -> None:
    """B-81 close-out (2) — the OW mirror of `test_workflow_driver_parallelization_
    pause.py`'s `test_peer_resume_excludes_pre_dispatch_gate_owner_paused_child_
    this_round`: the round-6 carry-forward fix's `paused_child_dispositions`
    exclusion conjunct must actually discriminate at the `FanOutResumeState`
    construction site too — a recovered pre-dispatch gate-owning worker whose
    delivered cell leads to a REAL nested child pause (not a clean complete) must
    be excluded from `pre_dispatch_gate_owning_branches` and land in
    `paused_child_branches` instead.

    Mutation-probe note: deleting the `and _bi not in paused_child_dispositions`
    conjunct at the OW construction site should make worker-0 wrongly reappear in
    `pre_dispatch_gate_owning_branches` alongside worker-1."""
    _grandchild0_dispatches[0] = 0
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-0"},
        ),
        WorkflowStep(
            step_id=StepID("worker-1-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-1"},
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    round1_dispatcher = _WarmupCohortLeaderGateDispatcherOW()
    paused = execute_workflow(
        _manifest("wf-ow-paused-child"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, round1_dispatcher),
    )
    assert round1_dispatcher.dispatched == ["worker-0-sub"], (
        "worker-1-sub must be genuinely WITHHELD by the warm-up split in round 1 "
        f"(never reach dispatch()) — got {round1_dispatcher.dispatched!r}"
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert [b.branch_index for b in snap.fan_out_resume.pre_dispatch_gate_owning_branches] == [0]

    resume_dispatcher = _RoundTwoResolveOnePausedChildFireOtherDispatcherOW(
        child_dispatcher=_GrandchildDispatcher()
    )
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resume_context = ResumeContext(
        hitl_response=HITLResult(
            response=HITLResponse.APPROVE,
            timestamp="2026-07-26T00:00:00Z",
            audit_ledger_entry_id=EntryID("e-b81-ow-paused-child"),
            response_summary_hash="f" * 64,
        )
    )
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_context)
    assert eligible_run_id is not None
    resumed = execute_workflow(
        _manifest("wf-ow-paused-child"),
        steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_context,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
    )
    assert sorted(resume_dispatcher.dispatched) == ["worker-0-sub", "worker-1-sub"]
    assert resumed.status is RunStatus.PAUSED, (
        f"expected the run to re-pause (worker-1's fresh gate + worker-0's paused child); "
        f"got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )
    resumed_snap = resumed.pause_snapshot
    assert resumed_snap is not None
    resumed_fr = resumed_snap.fan_out_resume
    assert resumed_fr is not None
    assert [b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches] == [1], (
        "worker-0 PAUSED as a nested child this round and must be EXCLUDED from the "
        "carried-forward pre-dispatch gate-owning set — only worker-1 (the fresh "
        f"this-round pause) should remain; got "
        f"{[b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches]!r}"
    )
    assert [b.branch_index for b in resumed_fr.paused_child_branches] == [0], (
        "worker-0 must land in paused_child_branches instead of being silently dropped"
    )
    assert resumed_fr.paused_child_branches[0].child_workflow_id == "wf-child-0"


class _RoundTwoResolveOneFenceAmbiguousFireOtherDispatcherOW:
    """B-81 close-out (2) — the OW mirror of `test_workflow_driver_parallelization_
    pause.py`'s `_RoundTwoResolveOneFenceAmbiguousFireOtherDispatcher`: worker-0-sub
    consumes its delivered `HITLDeliveryCell` and its OWN dispatch raises the
    runtime effect fence's ambiguous-uncommitted error (name-matched;
    `EffectFenceAmbiguousUncommittedError` test-local stand-in defined above).
    worker-1-sub, dispatched for the first time, raises the pause signal
    unconditionally — a fresh gate owner."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        self.dispatched.append(step_id)
        if step_id == "worker-0-sub":
            holder = getattr(step_context, "hitl_delivery_holder", None)
            resolved = holder.consume_and_clear() if holder is not None else None
            assert resolved is not None, "worker-0-sub must receive its delivery cell this round"
            raise EffectFenceAmbiguousUncommittedError(idempotency_key="fence-key-b81-ow")
        raise HITLPauseRequestedSignal()


def test_ow_worker_resume_excludes_pre_dispatch_gate_owner_effect_fence_paused_this_round() -> None:
    """B-81 close-out (2) — the OW mirror of `test_workflow_driver_parallelization_
    pause.py`'s `test_peer_resume_excludes_pre_dispatch_gate_owner_effect_fence_
    paused_this_round`: the round-6 carry-forward fix's `effect_fence_paused_
    dispositions` exclusion conjunct must actually discriminate at the
    `FanOutResumeState` construction site too — a recovered pre-dispatch
    gate-owning worker whose delivered cell leads to an effect-fence-ambiguous
    dispatch (not a clean complete) must be excluded from `pre_dispatch_gate_
    owning_branches` and land in `effect_fence_paused_branches` instead.

    Mutation-probe note: deleting the `and _bi not in effect_fence_paused_
    dispositions` conjunct at the OW construction site should make worker-0
    wrongly reappear in `pre_dispatch_gate_owning_branches` alongside worker-1."""
    steps = [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        WorkflowStep(
            step_id=StepID("worker-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-0"},
        ),
        WorkflowStep(
            step_id=StepID("worker-1-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-1"},
        ),
    ]
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    round1_dispatcher = _WarmupCohortLeaderGateDispatcherOW()
    paused = execute_workflow(
        _manifest("wf-ow-fence"),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, round1_dispatcher),
    )
    assert round1_dispatcher.dispatched == ["worker-0-sub"], (
        "worker-1-sub must be genuinely WITHHELD by the warm-up split in round 1 "
        f"(never reach dispatch()) — got {round1_dispatcher.dispatched!r}"
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.fan_out_resume is not None
    assert [b.branch_index for b in snap.fan_out_resume.pre_dispatch_gate_owning_branches] == [0]

    resume_dispatcher = _RoundTwoResolveOneFenceAmbiguousFireOtherDispatcherOW()
    resume_ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    resume_context = ResumeContext(
        hitl_response=HITLResult(
            response=HITLResponse.APPROVE,
            timestamp="2026-07-26T00:00:00Z",
            audit_ledger_entry_id=EntryID("e-b81-ow-fence-ambiguous"),
            response_summary_hash="0" * 64,
        )
    )
    eligible_run_id = compute_hitl_uniform_fallback_eligible_run_id(snap, resume_context)
    assert eligible_run_id is not None
    resumed = execute_workflow(
        _manifest("wf-ow-fence"),
        steps,
        run_id="run-1",
        ctx=resume_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=snap,
        resume_context=resume_context,
        hitl_uniform_fallback_eligible_run_id=eligible_run_id,
    )
    assert sorted(resume_dispatcher.dispatched) == ["worker-0-sub", "worker-1-sub"]
    assert resumed.status is RunStatus.PAUSED, (
        f"expected the run to re-pause (worker-1's fresh gate + worker-0's fence-ambiguous "
        f"pause); got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )
    resumed_snap = resumed.pause_snapshot
    assert resumed_snap is not None
    resumed_fr = resumed_snap.fan_out_resume
    assert resumed_fr is not None
    assert [b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches] == [1], (
        "worker-0 fence-ambiguous-paused this round and must be EXCLUDED from the "
        "carried-forward pre-dispatch gate-owning set — only worker-1 (the fresh "
        f"this-round pause) should remain; got "
        f"{[b.branch_index for b in resumed_fr.pre_dispatch_gate_owning_branches]!r}"
    )
    assert [b.branch_index for b in resumed_fr.effect_fence_paused_branches] == [0], (
        "worker-0 must land in effect_fence_paused_branches instead of being silently dropped"
    )
    assert resumed_fr.effect_fence_paused_branches[0].idempotency_key == "fence-key-b81-ow"

"""B-FANOUT-PAUSE-PARALLELIZATION (R-FS-1) — resumable `cascade_policy=pause` for the
PARALLELIZATION (peer fan-out) topology.

Materializes the cleared CP spec §25.15.1 `pause → PAUSED` row ("composes with
C-CP-26 PauseResumeProtocol + C-RT-30 `api.resume`") for PARALLELIZATION, flipping
the interim `parallelization-pause-resume-not-yet-materialized` FAILED to a genuine
resumable PAUSED — the `_execute_orchestrator_workers` (U-CP-88 / B-FANOUT-PAUSE)
shape applied PARALLELIZATION-shaped: NO orchestrator `steps[0]`, every step is a
PEER branch (indexed over `steps`), so the resume state is `PeerFanOutResumeState`
(branches + branch_count), NOT the orchestrator-bearing `FanOutResumeState`.

The honest bar (no false-`PAUSED`): a PAUSED is returned ONLY when a
`pause_resume_protocol` is bound so a `PeerFanOutResumeState`-bearing `PauseSnapshot`
can actually be captured, and `api.resume` (via the real `execute_workflow(
pause_snapshot_input=...)` entry-point resume detection — the exact path the runtime
`api.resume` drives) genuinely re-enters the strategy: terminal branches are SKIPPED
(§25.15.2 obligation 7, outputs recovered), the not-yet-dispatched ones re-dispatched.

Prerequisite: B-PARALLELIZATION-CASCADE (closed) built the cascade_policy harvest
this resume builds on (PARALLELIZATION had NO cascade machinery before that arc).

Authority: `Spec_Control_Plane_v1_44.md` §1 (PeerFanOutResumeState) + §2 (§25.15.1
PARALLELIZATION materialization note); `pause_resume_protocol_types.py` C-CP-26.
"""

from __future__ import annotations

import asyncio
import threading
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
from harness_cp.pause_resume_protocol import PauseResumeProtocol, _compute_snapshot_hash
from harness_cp.pause_resume_protocol_types import (
    FanOutBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-par-pause")
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # → cascade_policy = pause
_ANCHOR = "0" * 64  # constant MVP pause-context anchor (no material diff on resume)


def _manifest(workflow_id: str = "wf-pp") -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PAUSE_TIER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _steps(n_branches: int) -> list[WorkflowStep]:
    """A PEER fan-out — every step IS a branch (NO orchestrator `steps[0]`)."""
    return [
        WorkflowStep(
            step_id=StepID(f"branch-{i}"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": i},
        )
        for i in range(n_branches)
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
    """MVP constant-sentinel reader: empty StateSummary + a constant anchor →
    resume detects no material diff → admits."""
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
    """Driver context WITH a bound `pause_resume_protocol` (the pause/resume opt-in)
    so the peer fan-out `pause` branch can capture a snapshot + return PAUSED, and
    `execute_workflow(pause_snapshot_input=...)` entry-point resume detection can
    validate + admit a resume. `procedural_tier_snapshot_resolver` absent → the
    R-003 sidecar stays None."""

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
    """Echoes `{role, echoed}`; records every dispatched step_id (so a resume can
    assert which branches were re-dispatched vs terminal-skipped). A step_id in
    `fail_step_ids` raises (the cascade trigger)."""

    def __init__(self, *, fail_step_ids: set[str] | None = None) -> None:
        self._fail = fail_step_ids or set()
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id in self._fail:
            raise RuntimeError(f"simulated branch failure at {step_id}")
        return {"role": step_id, "echoed": dict(step.step_payload)}


class _GatedFailDispatcher:
    """Forces a DETERMINISTIC all-terminal pause: branch-0 completes cleanly and
    sets a gate; branch-1 waits on that gate THEN fails. So both branches reach a
    terminal disposition (branch-0 `completed`+output / branch-1 ran-and-errored
    `completed`/no-output) BEFORE the barrier resolves — no not-yet-dispatched
    (cancelled) branch, no timing race."""

    def __init__(self) -> None:
        self._gate = threading.Event()
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "branch-0":
            self._gate.set()
            return {"role": "branch-0", "echoed": dict(step.step_payload)}
        # branch-1: wait until branch-0 has completed, then fail (the trigger).
        assert self._gate.wait(timeout=10.0), "branch-0 never completed"
        raise RuntimeError("simulated branch-1 failure (after branch-0 completed)")


def _run(
    *,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    ctx: DriverContext,
    pause_snapshot_input: PauseSnapshot | None = None,
    workflow_id: str = "wf-pp",
) -> Any:
    return execute_workflow(
        _manifest(workflow_id),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
        pause_snapshot_input=pause_snapshot_input,
    )


def _captured_snapshot(
    *, peer_fan_out_resume: PeerFanOutResumeState, workflow_id: str = "wf-pp"
) -> PauseSnapshot:
    """A hash-valid peer fan-out snapshot, captured through the real protocol (NOT a
    hand-mutated model) — the exact shape a prior `pause` halt would produce."""
    return asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id=workflow_id,
            run_id="run-1",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            peer_fan_out_resume=peer_fan_out_resume,
        )
    )


# ---------------------------------------------------------------------------
# Capture — a real peer fan-out pause returns PAUSED + a peer-aware snapshot
# ---------------------------------------------------------------------------


def test_pause_with_protocol_returns_paused_with_peer_snapshot() -> None:
    """TEAM persona → pause, protocol bound: branch-1 fails (after branch-0
    completes) → the run PAUSES (not the interim FAILED) with a hash-valid
    `PauseSnapshot` carrying a `PeerFanOutResumeState` (NO orchestrator; the
    terminal branches + branch-0's recovered output)."""
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=_GatedFailDispatcher(), ctx=ctx)

    assert result.status is RunStatus.PAUSED
    assert result.fail_class is None
    snap = result.pause_snapshot
    assert snap is not None
    # PARALLELIZATION sets `peer_fan_out_resume`, NEVER the orchestrator-bearing one.
    assert snap.fan_out_resume is None
    pr = snap.peer_fan_out_resume
    assert pr is not None
    assert pr.branch_count == 2
    by_index = {b.branch_index: b for b in pr.branches}
    # branch-0 completed cleanly → terminal + its output recovered into the snapshot.
    assert by_index[0].terminal_status == "completed"
    assert by_index[0].step_id == "branch-0"  # identity captured for resume validation
    assert by_index[0].output == {"role": "branch-0", "echoed": {"index": 0}}
    # branch-1 ran-and-errored → terminal `completed` (dispatch-boundary), no output.
    assert by_index[1].terminal_status == "completed"
    assert by_index[1].step_id == "branch-1"
    assert by_index[1].output is None
    # The snapshot is hash-valid (covers peer_fan_out_resume).
    assert snap.snapshot_hash == _compute_snapshot_hash(
        workflow_id=snap.workflow_id,
        run_id=snap.run_id,
        step_index=snap.step_index,
        state_summary=snap.state_summary,
        peer_fan_out_resume=pr,
    )


def test_pause_emits_resumption_not_workflow_start_on_resume() -> None:
    """The resume envelope emits RESUMPTION (the terminal branches already ran in
    the original envelope), not a second WORKFLOW_START."""
    emitter = _Emitter()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=emitter))
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    terminal_status="completed",
                    output={"role": "branch-0"},
                ),
            ),  # branch-1 absent → re-dispatchable
            branch_count=2,
        )
    )
    _run(steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=snapshot)
    assert WorkflowEventClass.RESUMPTION in emitter.emits
    assert WorkflowEventClass.WORKFLOW_START not in emitter.emits


# ---------------------------------------------------------------------------
# Resume — the real `execute_workflow(pause_snapshot_input=...)` witness
# ---------------------------------------------------------------------------


def test_resume_skips_terminal_recovers_outputs_and_redispatches_rest() -> None:
    """THE WITNESS — through the real `execute_workflow(pause_snapshot_input=...)`
    entry-point resume detection (the path `api.resume` drives):
      (1) the terminal branch (branch-0) is NOT re-dispatched (obligation 7),
      (2) the not-yet-dispatched branch (branch-1) IS re-dispatched,
      (3) the aggregate fuses the RECOVERED branch-0 output + the FRESH branch-1
          output → SUCCESS."""
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    terminal_status="completed",
                    output={"role": "branch-0", "recovered": True},
                ),
            ),  # branch-1 ABSENT → left re-dispatchable
            branch_count=2,
        )
    )
    dispatcher = _CountingDispatcher()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=dispatcher, ctx=ctx, pause_snapshot_input=snapshot)

    assert result.status is RunStatus.SUCCESS
    # (1): the terminal branch-0 was NOT re-dispatched.
    assert "branch-0" not in dispatcher.dispatched
    # (2): only the re-dispatchable branch-1 ran on resume.
    assert dispatcher.dispatched == ["branch-1"]
    # (3): the aggregate's branch_outputs fuse recovered (branch-0) + fresh (branch-1).
    assert result.final_state is not None
    assert result.final_state["branch_outputs"]["branch-0"] == {
        "role": "branch-0",
        "recovered": True,
    }
    assert result.final_state["branch_outputs"]["branch-1"] == {
        "role": "branch-1",
        "echoed": {"index": 1},
    }


def test_resume_all_terminal_with_a_failed_branch_is_partial_not_silent_success() -> None:
    """Real pause → real resume round-trip (the GatedFail all-terminal pause): both
    branches terminal at pause (branch-0 completed, branch-1 FAILED) → resume
    re-dispatches NOTHING and surfaces **PARTIAL** (degraded), NOT a bare silent
    SUCCESS dropping the failure — the silent-degradation class this arc forecloses.
    branch-0's output is recovered; the failed branch-1 contributes nothing + is not
    re-fired (obligation 7 + at-most-once)."""
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
    # The salvaged aggregate is on partial_state; branch-0 recovered, branch-1 gone.
    assert result.partial_state is not None
    assert "branch-0" in result.partial_state["branch_outputs"]
    assert "branch-1" not in result.partial_state["branch_outputs"]


# ---------------------------------------------------------------------------
# Negative controls + integrity + backward-compat
# ---------------------------------------------------------------------------


def test_snapshot_hash_covers_peer_fan_out_resume_tamper_rejected() -> None:
    """Integrity: a snapshot whose recovered branch output is TAMPERED (without
    re-hashing) is REJECTED at resume → FAILED + CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION
    (no silent-tamper gap on the data the resumed aggregate trusts)."""
    good = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    terminal_status="completed",
                    output={"amount": 100},
                ),
            ),
            branch_count=2,
        )
    )
    # Tamper the recovered output, keeping the STALE hash → corruption.
    tampered = good.model_copy(
        update={
            "peer_fan_out_resume": good.peer_fan_out_resume.model_copy(  # type: ignore[union-attr]
                update={
                    "branches": (
                        FanOutBranchResumeState(
                            branch_index=0,
                            step_id="branch-0",
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
    recovered branch-0 output) re-dispatches BOTH branches and branch-0's output is
    the FRESH one — proving the recovered output in the snapshot is what populates
    the aggregate, not an incidental re-run."""
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),  # nothing recovered → both branches re-dispatchable
            branch_count=2,
        )
    )
    dispatcher = _CountingDispatcher()
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=dispatcher, ctx=ctx, pause_snapshot_input=snapshot)
    assert result.status is RunStatus.SUCCESS
    # BOTH branches re-dispatched (no terminal skip); branch-0's output is the FRESH
    # echo (no "recovered" marker), proving the recovered-output path is the only
    # source of a recovered value (vs. this incidental re-run).
    assert set(dispatcher.dispatched) == {"branch-0", "branch-1"}
    assert result.final_state is not None
    assert result.final_state["branch_outputs"]["branch-0"] == {
        "role": "branch-0",
        "echoed": {"index": 0},
    }


def test_resume_branch_count_mismatch_fails_closed() -> None:
    """Material-diff guard: a snapshot captured with branch_count=3 but resumed
    against a 2-branch body fails CLOSED (the recovered ordinals no longer map to
    these steps — a changed body) rather than re-dispatching a mismatched set."""
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(branches=(), branch_count=3)
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=snapshot
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "branch-count-mismatch" in result.fail_class


def test_resume_branch_identity_mismatch_fails_closed() -> None:
    """A valid (same branch_count) snapshot whose recovered branch `step_id` does
    NOT match the re-supplied body (a branch rename / reorder) fails CLOSED rather
    than silently attributing the recovered output to the wrong step. The hash is
    valid (captured for the renamed id), so this is caught by the in-strategy
    identity guard, not the snapshot_hash."""
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="renamed-branch",  # the body has "branch-0" at index 0
                    terminal_status="completed",
                    output={"stale": True},
                ),
            ),
            branch_count=2,
        )
    )
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(
        steps=_steps(2), dispatcher=_CountingDispatcher(), ctx=ctx, pause_snapshot_input=snapshot
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "branch-identity-mismatch" in result.fail_class


def test_resume_redispatch_failing_branch_re_pauses_with_unioned_branches() -> None:
    """A re-dispatched branch failing AGAIN under `pause` re-PAUSES with a snapshot
    whose `branches` UNION the prior-recovered + this-round-terminal sets. branch-0
    recovered; branch-1 fails on re-dispatch → the new snapshot carries BOTH
    (branch-0's recovered output carried forward + branch-1 newly terminal)."""
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    terminal_status="completed",
                    output={"role": "branch-0", "recovered": True},
                ),
            ),  # branch-1 + branch-2 absent → re-dispatchable
            branch_count=3,
        )
    )
    dispatcher = _CountingDispatcher(fail_step_ids={"branch-1"})
    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(3), dispatcher=dispatcher, ctx=ctx, pause_snapshot_input=snapshot)

    # A re-dispatched branch failed under pause (protocol bound) → re-PAUSED.
    assert result.status is RunStatus.PAUSED
    new_snap = result.pause_snapshot
    assert new_snap is not None and new_snap.peer_fan_out_resume is not None
    by_index = {b.branch_index: b for b in new_snap.peer_fan_out_resume.branches}
    # UNION: the prior-recovered branch-0 (carried forward, output preserved) +
    # the newly-terminal branch-1 (failed this round).
    assert 0 in by_index and 1 in by_index
    assert by_index[0].output == {"role": "branch-0", "recovered": True}
    assert by_index[1].output is None  # ran-and-errored → no output
    # branch-0 was NOT re-dispatched (terminal-skipped); branch-1 WAS (and failed).
    assert "branch-0" not in dispatcher.dispatched
    assert "branch-1" in dispatcher.dispatched


def test_pause_captures_in_flight_sibling_completed_output() -> None:
    """A sibling IN-FLIGHT when the barrier cancels it (because another branch
    failed) runs to completion under the shield; its successful OUTPUT must be
    captured into the snapshot (else resume skips it as terminal + drops the
    output). branch-0 is mid-dispatch (a brief sleep) when branch-1 fails →
    branch-0 completes under the shield → its output is recovered."""
    import time

    class _InFlightCompletesDispatcher:
        def __init__(self) -> None:
            self._started = threading.Event()

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            sid = str(step.step_id)
            if sid == "branch-0":
                self._started.set()
                time.sleep(0.05)  # in-flight when branch-1 fails; completes under the shield
                return {"role": "branch-0", "in_flight_completed": True}
            assert self._started.wait(timeout=10.0), "branch-0 never started"
            raise RuntimeError("branch-1 fails while branch-0 is in-flight")

    ctx = cast(DriverContext, _CtxP(ledger=_RecordingLedger(), emitter=_Emitter()))
    result = _run(steps=_steps(2), dispatcher=_InFlightCompletesDispatcher(), ctx=ctx)

    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None and snap.peer_fan_out_resume is not None
    by_index = {b.branch_index: b for b in snap.peer_fan_out_resume.branches}
    # branch-0 was cancelled-but-completed → terminal `completed` WITH its output
    # captured; without it `output` would be None and resume would drop it.
    assert by_index[0].terminal_status == "completed"
    assert by_index[0].output == {"role": "branch-0", "in_flight_completed": True}


def test_peer_snapshot_hash_byte_identical_backward_compat() -> None:
    """Backward-compat: a snapshot with NO `peer_fan_out_resume` (and no
    `fan_out_resume`) hashes byte-identically to the pre-B-FANOUT-PAUSE formula
    (each key is added to the canonical dict ONLY when present) → existing durable
    snapshots still validate."""
    summary = _pause_context_reader()[0]
    with_field = _compute_snapshot_hash(
        workflow_id="wf",
        run_id="r",
        step_index=0,
        state_summary=summary,
        peer_fan_out_resume=None,
    )
    legacy_canonical_hash = _compute_snapshot_hash(
        workflow_id="wf", run_id="r", step_index=0, state_summary=summary
    )
    assert with_field == legacy_canonical_hash


def test_peer_snapshot_survives_json_roundtrip() -> None:
    """Durable-store fidelity: the peer fan-out snapshot round-trips through
    model_dump(mode="json") → model_validate (the JournalWorkflowPauseStore path)
    with `peer_fan_out_resume` intact AND the hash still valid."""
    snapshot = _captured_snapshot(
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    terminal_status="completed",
                    output={"k": "v"},
                ),
                FanOutBranchResumeState(
                    branch_index=1, step_id="branch-1", terminal_status="timed_out", output=None
                ),
            ),
            branch_count=3,
        )
    )
    restored = PauseSnapshot.model_validate(snapshot.model_dump(mode="json"))
    assert restored == snapshot
    assert restored.peer_fan_out_resume is not None
    assert restored.snapshot_hash == _compute_snapshot_hash(
        workflow_id=restored.workflow_id,
        run_id=restored.run_id,
        step_index=restored.step_index,
        state_summary=restored.state_summary,
        peer_fan_out_resume=restored.peer_fan_out_resume,
    )

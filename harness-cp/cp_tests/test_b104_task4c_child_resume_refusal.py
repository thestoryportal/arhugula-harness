"""B-104 Task 4c (CP side): the carried child capture reaches the resumed worker, and a
Runtime refusal of a durable paused child is terminal for the parent.

Behavior under test, in both fan-out families and on the typed-catch AND the in-flight
cancellation path: the resumed worker receives its own exact capture (ref included); when
the Runtime raises `ChildResumeRefusedError` the run is FAILED with a distinct reason and
produces no new pause snapshot, no capture and no fresh child dispatch; a snapshot listing
one journal record for two children is refused before anything is dispatched.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import PausedChildCapture, PauseSnapshot
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    ChildResumeRefusal,
    ChildResumeRefusedError,
    ResumeRefusal,
    RunResult,
    RunStatus,
    StepKind,
    SubAgentChildPausedError,
    WorkflowStep,
)

from .test_b104_task4b_child_ref_carry import (
    _same_id_sibling_captures,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_fanout_pause import (
    _CountingDispatcher as _OwEcho,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_fanout_pause import (
    _CtxP as _OwCtx,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_fanout_pause import (
    _Emitter as _OwEmitter,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_fanout_pause import (
    _manifest as _ow_manifest,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_fanout_pause import (
    _RecordingLedger as _OwLedger,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_parallelization_pause import (
    _CtxP as _PeerCtx,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_parallelization_pause import (
    _Emitter as _PeerEmitter,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_parallelization_pause import (
    _manifest as _peer_manifest,  # pyright: ignore[reportPrivateUsage]
)
from .test_workflow_driver_parallelization_pause import (
    _RecordingLedger as _PeerLedger,  # pyright: ignore[reportPrivateUsage]
)

_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_FAMILIES = ("fan_out", "peer")
# The stable prefix, then the refusal reason(s) the run ended on (Task 4c correction).
_REFUSED_FAIL_CLASS = {
    "fan_out": "orchestrator-workers-child-resume-refused (gateway-not-installed)",
    "peer": "parallelization-child-resume-refused (gateway-not-installed)",
}


def _sub_agent(name: str) -> WorkflowStep:
    # The resume guard requires the payload to still target the child workflow the snapshot
    # was captured against.
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={"child_workflow_id": "wf-child"},
    )


class _SubAgents:
    """Per worker: pause (a child pause), refuse (`ChildResumeRefusedError`) or complete.

    `w-1` waits for `w-0`, so that when both raise, w-0's raise cancels w-1 while w-1's own
    outcome is still in flight (the shielded-drain path).
    """

    def __init__(
        self, *, pause: frozenset[str] = frozenset(), refuse: frozenset[str] = frozenset()
    ) -> None:
        self._pause = pause
        self._refuse = refuse
        self._captures = _same_id_sibling_captures()
        self._gate = threading.Event()
        self.received: dict[str, PausedChildCapture | None] = {}

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        self.received[sid] = step_context.child_resume
        if sid == "w-0":
            self._gate.set()
        else:
            assert self._gate.wait(timeout=10.0)
        if sid in self._refuse:
            raise ChildResumeRefusedError(ChildResumeRefusal.GATEWAY_NOT_INSTALLED, sid)
        if sid in self._pause:
            raise SubAgentChildPausedError(capture=self._captures[sid])
        return {"completed": sid}


class _Registry:
    def __init__(self, sub_agents: _SubAgents, echo: StepDispatcher) -> None:
        self._sub_agents = sub_agents
        self._echo = echo

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agents)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._echo
        raise StepKindDispatcherNotBoundError(step_kind)


@dataclass
class _Run:
    result: RunResult
    captures: list[str]


def _steps(family: str, n_workers: int) -> list[WorkflowStep]:
    workers = [_sub_agent(f"w-{i}") for i in range(n_workers)]
    if family == "peer":
        return workers
    return [
        WorkflowStep(
            step_id=StepID("orch"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orch"},
        ),
        *workers,
    ]


def _execute(
    family: str,
    n_workers: int,
    sub_agents: _SubAgents,
    *,
    resume_from: PauseSnapshot | None = None,
    persona_tier: PersonaTier = PersonaTier.TEAM_BINDING,  # cascade_policy=pause
) -> _Run:
    registry = _Registry(sub_agents, cast(StepDispatcher, _OwEcho()))
    if family == "fan_out":
        manifest = _ow_manifest(
            "wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION, persona_tier=persona_tier
        )
        ctx: Any = _OwCtx(ledger=_OwLedger(), emitter=_OwEmitter())
    else:
        manifest = _peer_manifest("wf-parent", persona_tier=persona_tier)
        ctx = _PeerCtx(ledger=_PeerLedger(), emitter=_PeerEmitter())
    captures: list[str] = []
    protocol = ctx.pause_resume_protocol
    original = protocol.capture_pause_snapshot

    async def counting(*args: Any, **kwargs: Any) -> Any:
        captures.append("capture")
        return await original(*args, **kwargs)

    protocol.capture_pause_snapshot = counting
    result = execute_workflow(
        manifest,
        _steps(family, n_workers),
        run_id="run-parent",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, registry),
        pause_snapshot_input=resume_from,
    )
    return _Run(result, captures)


def _paused_snapshot(family: str, n_workers: int) -> PauseSnapshot:
    first = _execute(
        family, n_workers, _SubAgents(pause=frozenset(f"w-{i}" for i in range(n_workers)))
    )
    assert first.result.status is RunStatus.PAUSED and first.result.pause_snapshot is not None
    return first.result.pause_snapshot


def _carriers(family: str, snapshot: PauseSnapshot) -> Any:
    carrier = snapshot.fan_out_resume if family == "fan_out" else snapshot.peer_fan_out_resume
    assert carrier is not None
    return sorted(carrier.paused_child_branches, key=lambda c: c.branch_index)


# --- the worker receives its own exact capture -------------------------------------------


@pytest.mark.parametrize("family", _FAMILIES)
def test_each_resumed_worker_receives_its_own_exact_child_capture(family: str) -> None:
    snapshot = _paused_snapshot(family, 2)
    resumed = _SubAgents(refuse=frozenset({"w-1"}))  # w-0 completes, so w-1 is reached and refuses

    _execute(family, 2, resumed, resume_from=snapshot)

    carriers = _carriers(family, snapshot)
    assert set(resumed.received) == {"w-0", "w-1"}
    for index, name in enumerate(("w-0", "w-1")):
        capture = resumed.received[name]
        assert capture == carriers[index].as_capture()
        assert capture is not None and capture.child_record_ref == carriers[index].child_record_ref
    first, second = (resumed.received[n] for n in ("w-0", "w-1"))
    assert first is not None and second is not None
    assert first.child_record_ref != second.child_record_ref


# --- a refusal is terminal for the parent --------------------------------------------------


@pytest.mark.parametrize("family", _FAMILIES)
@pytest.mark.parametrize("n_workers", [1, 2])
def test_a_refused_child_fails_the_parent_terminally_without_pause_capture_or_redispatch(
    family: str, n_workers: int
) -> None:
    snapshot = _paused_snapshot(family, n_workers)
    resumed = _SubAgents(refuse=frozenset(f"w-{i}" for i in range(n_workers)))

    run = _execute(family, n_workers, resumed, resume_from=snapshot)

    assert run.result.status is RunStatus.FAILED
    assert run.result.fail_class == _REFUSED_FAIL_CLASS[family]
    assert run.result.pause_snapshot is None and run.result.pause_record_ref is None
    assert run.captures == []  # no new pause capture of any kind
    # Resumed children are dispatched one at a time: the first refusal stops the run, so a
    # second paused child is never dispatched (and nothing is dispatched fresh).
    assert set(resumed.received) == {"w-0"}


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_refusal_landing_on_the_in_flight_cancellation_path_still_fails_terminally(
    family: str,
) -> None:
    """w-0 pauses; w-1's refusal arrives only through the shielded in-flight drain. Without
    its own catch that refusal would be an ordinary branch failure and the run would PAUSE
    on w-0's child."""
    sub_agents = _SubAgents(pause=frozenset({"w-0"}), refuse=frozenset({"w-1"}))

    run = _execute(family, 2, sub_agents)

    assert run.result.status is RunStatus.FAILED
    assert run.result.fail_class == _REFUSED_FAIL_CLASS[family]
    assert run.result.pause_snapshot is None and run.result.pause_record_ref is None
    assert run.captures == []


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_refusal_under_the_proceed_tier_is_terminal_not_a_degraded_run(family: str) -> None:
    """`proceed` normally harvests survivors into PARTIAL/SUCCESS; a refused durable child
    must never be degraded away."""
    sub_agents = _SubAgents(refuse=frozenset({"w-0"}))

    run = _execute(family, 2, sub_agents, persona_tier=PersonaTier.SOLO_DEVELOPER)

    assert run.result.status is RunStatus.FAILED
    assert run.result.fail_class == _REFUSED_FAIL_CLASS[family]
    assert run.result.pause_snapshot is None and run.captures == []


class _DeadlineRefusalSubAgents(_SubAgents):
    """Make a refusal and an in-flight sibling coexist before the barrier expires."""

    def __init__(self, *, audit_signing_failed: bool) -> None:
        super().__init__()
        self.audit_signing_failed = audit_signing_failed
        self.sibling_entered = threading.Event()
        self.refusal_raised = threading.Event()
        self.release = threading.Event()

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        self.received[sid] = step_context.child_resume
        if sid == "w-1":
            self.sibling_entered.set()
            self.release.wait(timeout=5.0)  # cleanup backstop; the test releases in finally
            raise RuntimeError("sibling released without running a child")
        self.refusal_raised.set()
        raise ChildResumeRefusedError(
            ChildResumeRefusal.UNREADABLE_RECORD,
            sid,
            audit_signing_failed=self.audit_signing_failed,
        )


@pytest.mark.parametrize("family", _FAMILIES)
@pytest.mark.parametrize("audit_signing_failed", [False, True])
def test_proceed_deadline_preserves_a_recorded_child_refusal(
    family: str, audit_signing_failed: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The sibling is in flight before refusal; its deadline must not hide that refusal."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.5)
    sub_agents = _DeadlineRefusalSubAgents(audit_signing_failed=audit_signing_failed)
    try:
        run = _execute(family, 2, sub_agents, persona_tier=PersonaTier.SOLO_DEVELOPER)
    finally:
        sub_agents.release.set()

    assert sub_agents.sibling_entered.is_set() and sub_agents.refusal_raised.is_set()
    assert set(sub_agents.received) == {"w-0", "w-1"}
    assert run.result.status is RunStatus.FAILED
    expected = (
        f"{'orchestrator-workers' if family == 'fan_out' else 'parallelization'}"
        "-child-resume-refused (unreadable-record"
        f"{'; audit-signing-failed' if audit_signing_failed else ''})"
    )
    assert run.result.fail_class == expected
    assert run.result.final_state is None
    assert run.result.pause_snapshot is None and run.captures == []


# --- one journal record can never stand for two children ---------------------------------


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_snapshot_presenting_one_record_for_two_children_dispatches_nothing(
    family: str,
) -> None:
    snapshot = _paused_snapshot(family, 2)
    first, second = _carriers(family, snapshot)
    duplicated = second.model_copy(update={"child_record_ref": first.child_record_ref})
    carrier_key = "fan_out_resume" if family == "fan_out" else "peer_fan_out_resume"
    tampered_carrier = getattr(snapshot, carrier_key).model_copy(
        update={"paused_child_branches": (first, duplicated)}
    )
    # Re-hash so the ONLY defect is the duplicate ref (a hash mismatch would refuse first).
    tampered = snapshot.model_copy(
        update={
            carrier_key: tampered_carrier,
            "snapshot_hash": _compute_snapshot_hash(
                workflow_id=snapshot.workflow_id,
                run_id=snapshot.run_id,
                step_index=snapshot.step_index,
                state_summary=snapshot.state_summary,
                **{carrier_key: tampered_carrier},
            ),
        }
    )
    resumed = _SubAgents()

    run = _execute(family, 2, resumed, resume_from=tampered)

    assert run.result.status is RunStatus.FAILED
    assert resumed.received == {}  # refused before any worker was dispatched


class _PerWorkerRefusals(_SubAgents):
    """Every listed worker refuses with its own reasons and signing fact."""

    def __init__(self, refusals: dict[str, ChildResumeRefusedError]) -> None:
        super().__init__(refuse=frozenset(refusals))
        self._refusals = refusals

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        try:
            return super().dispatch(binding, step, step_context=step_context)
        except ChildResumeRefusedError:
            raise self._refusals[str(step.step_id)] from None


@pytest.mark.parametrize("family", _FAMILIES)
def test_two_recorded_disjoint_refusals_end_the_run_on_their_union(family: str) -> None:
    """CP plan v2.56 U-CP-106 criterion 3: both children refuse concurrently with disjoint
    reasons and differing signing facts; w-1's refusal is recorded through the in-flight drain
    before the barrier ends. The run carries the reason union and the signing OR, and its fail
    class renders that same value.

    Mutation probes: keeping only the first recorded refusal loses `hitl-gate-config-changed`
    and the signing fact; keeping only the last loses `claim-busy`. Both turn this red.
    """
    run = _execute(family, 2, _PerWorkerRefusals(_disjoint_refusals()))

    _assert_ended_on_the_disjoint_union(family, run)


def _disjoint_refusals() -> dict[str, ChildResumeRefusedError]:
    # Disjoint reasons and differing signing facts: a first-only selector loses
    # `hitl-gate-config-changed` and the signing fact; a last-only selector loses `claim-busy`.
    return {
        "w-0": ChildResumeRefusedError(ChildResumeRefusal.CLAIM_BUSY, "w-0"),
        "w-1": ChildResumeRefusedError(
            ChildResumeRefusal.HITL_GATE_CONFIG_CHANGED, "w-1", audit_signing_failed=True
        ),
    }


def _assert_ended_on_the_disjoint_union(family: str, run: _Run) -> None:
    prefix = _REFUSED_FAIL_CLASS[family].split(" (")[0]
    assert run.result.status is RunStatus.FAILED
    assert run.result.resume_refusal == ResumeRefusal(
        reasons=frozenset(
            {ChildResumeRefusal.CLAIM_BUSY, ChildResumeRefusal.HITL_GATE_CONFIG_CHANGED}
        ),
        audit_signing_failed=True,
    )
    assert run.result.fail_class == (
        f"{prefix} (claim-busy; hitl-gate-config-changed; audit-signing-failed)"
    )
    assert run.result.pause_snapshot is None and run.captures == []


class _OrderedRefusals(_PerWorkerRefusals):
    """Logs each dispatch's entry and exit, so a test can see whether two overlapped."""

    def __init__(self, refusals: dict[str, ChildResumeRefusedError]) -> None:
        super().__init__(refusals)
        self.order: list[str] = []

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        self.order.append(f"enter {sid}")
        try:
            return super().dispatch(binding, step, step_context=step_context)
        finally:
            self.order.append(f"exit {sid}")


@pytest.mark.parametrize("family", _FAMILIES)
def test_one_proceed_resume_ends_on_the_union_of_both_resumed_refusals(family: str) -> None:
    """One resume, under `proceed`, of a parent the CP itself paused on two children. Each
    resumed child gets its own exact capture, the two are dispatched one after the other
    (B-39), and both refusals are recorded before the barrier ends, so the run ends on their
    union rather than on the first refusal.

    `proceed` never captures a resumable child pause (B-21 fails that run instead), so the
    snapshot is captured under the `pause` tier and the one resume runs under `proceed`."""
    snapshot = _paused_snapshot(family, 2)
    resumed = _OrderedRefusals(_disjoint_refusals())

    run = _execute(
        family, 2, resumed, resume_from=snapshot, persona_tier=PersonaTier.SOLO_DEVELOPER
    )

    carriers = _carriers(family, snapshot)
    assert [resumed.received[n] for n in ("w-0", "w-1")] == [c.as_capture() for c in carriers]
    assert resumed.order == ["enter w-0", "exit w-0", "enter w-1", "exit w-1"]
    _assert_ended_on_the_disjoint_union(family, run)

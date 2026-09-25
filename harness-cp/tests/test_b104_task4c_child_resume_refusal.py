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

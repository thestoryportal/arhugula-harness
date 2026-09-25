"""B-104 Task 4b: the exact child journal ref is captured and carried, nothing more.

Behavior under test: a paused child's `JournalRecordRef` travels from the child-pause error
into the parent's paused-child carrier (both fan-out families, including the in-flight
cancellation path), is validated against the child snapshot and workflow identity, is
covered by the PARENT's snapshot hash, and is absent from the hash input when it is `None`
so legacy and ephemeral snapshots re-hash byte-identically. Resume-side use of the ref is
Task 4c and is not exercised here.
"""

from __future__ import annotations

import threading
from typing import Any, cast

import pytest
from harness_core import JournalRecordRef, StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import (
    FanOutResumeState,
    PausedChildBranchResumeState,
    PausedChildCapture,
    PauseSnapshot,
    PeerFanOutResumeState,
    WorkflowPauseReason,
)
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
    SubAgentChildPausedError,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Identifier
from pydantic import ValidationError

from .test_workflow_driver_fanout_pause import (
    _CountingDispatcher as _OwCountingDispatcher,  # pyright: ignore[reportPrivateUsage]
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
_SUMMARY = StateSummary(
    relevant_entries=(),
    summary_text="",
    summary_hash="0" * 64,
    idempotency_key=Identifier(""),
    external_references=(),
)

# Hashes of the two parent snapshots below (paused child `wf-c` that itself carries a paused
# grandchild `wf-g`, all refs absent), computed with the pre-Task-4b hash code at ed983b0.
# A legacy or ephemeral capture must keep producing exactly these.
_LEGACY_FAN_OUT_HASH = "846f4c15ca56f92f64832fd78fe55f51d4bff2ff195cf0395891490051794e25"
_LEGACY_PEER_HASH = "3733be59b59522bb00692a5d3b552b5d77578583ba063221995eb79a1de52f77"


def _snapshot(workflow_id: str, run_id: str, snap_hash: str, **carriers: Any) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=run_id,
        step_index=0,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=_SUMMARY,
        snapshot_hash=snap_hash,
        created_at=1_700_000_000_000,
        state_ledger_anchor="b" * 64,
        **carriers,
    )


def _ref(snapshot: PauseSnapshot, *, count: int, digest: str) -> JournalRecordRef:
    return JournalRecordRef(
        tenant=None,
        workflow_id=snapshot.workflow_id,
        run_id=snapshot.run_id,
        record_count=count,
        latest_digest=digest * 64,
        snapshot_hash=snapshot.snapshot_hash,
    )


def _carrier(
    snapshot: PauseSnapshot, workflow_id: str, ref: JournalRecordRef | None
) -> PausedChildBranchResumeState:
    return PausedChildBranchResumeState(
        branch_index=0,
        step_id="w0",
        child_workflow_id=workflow_id,
        child_snapshot=snapshot,
        child_record_ref=ref,
    )


def _nested_parent_hashes(
    *, g_ref: JournalRecordRef | None, c_ref: JournalRecordRef | None
) -> tuple[str, str]:
    """(fan-out family hash, peer family hash) of P holding C, which holds G."""
    g = _snapshot("wf-g", "run-g", "1" * 64)
    c = _snapshot(
        "wf-c",
        "run-c",
        "2" * 64,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            paused_child_branches=(_carrier(g, "wf-g", g_ref),),
        ),
    )
    common: dict[str, Any] = {
        "workflow_id": "wf-p",
        "run_id": "run-p",
        "step_index": 0,
        "state_summary": _SUMMARY,
    }
    fan_out = FanOutResumeState(
        orchestrator_output={"r": "o"},
        orchestrator_step_id="orch",
        branches=(),
        worker_count=1,
        paused_child_branches=(_carrier(c, "wf-c", c_ref),),
    )
    peer = PeerFanOutResumeState(
        branches=(), branch_count=1, paused_child_branches=(_carrier(c, "wf-c", c_ref),)
    )
    return (
        _compute_snapshot_hash(fan_out_resume=fan_out, **common),
        _compute_snapshot_hash(peer_fan_out_resume=peer, **common),
    )


def _g_ref() -> JournalRecordRef:
    return _ref(_snapshot("wf-g", "run-g", "1" * 64), count=3, digest="a")


def _c_ref() -> JournalRecordRef:
    return _ref(_snapshot("wf-c", "run-c", "2" * 64), count=5, digest="b")


# --- hash: absent ref is byte-identical, present ref is covered ---------------------------


def test_absent_refs_rehash_byte_identically_to_the_pre_task_4b_hash() -> None:
    assert _nested_parent_hashes(g_ref=None, c_ref=None) == (
        _LEGACY_FAN_OUT_HASH,
        _LEGACY_PEER_HASH,
    )


def test_either_ref_in_a_parent_child_grandchild_chain_changes_the_parents_hash() -> None:
    legacy = _nested_parent_hashes(g_ref=None, c_ref=None)
    with_g = _nested_parent_hashes(g_ref=_g_ref(), c_ref=None)
    with_c = _nested_parent_hashes(g_ref=None, c_ref=_c_ref())
    with_both = _nested_parent_hashes(g_ref=_g_ref(), c_ref=_c_ref())

    for family in (0, 1):
        hashes = {legacy[family], with_g[family], with_c[family], with_both[family]}
        assert len(hashes) == 4, "a ref is not covered by the parent hash"
    other_g = _ref(_snapshot("wf-g", "run-g", "1" * 64), count=4, digest="c")
    assert _nested_parent_hashes(g_ref=other_g, c_ref=_c_ref()) != with_both


# --- validators: a ref must name the snapshot and workflow it travels with ----------------


@pytest.mark.parametrize(
    "mismatch",
    [
        {"workflow_id": "wf-other"},
        {"run_id": "run-other"},
        {"snapshot_hash": "9" * 64},
    ],
    ids=["workflow", "run", "snapshot-hash"],
)
def test_a_ref_that_does_not_name_the_child_snapshot_is_refused_at_both_carriers(
    mismatch: dict[str, str],
) -> None:
    snap = _snapshot("wf-c", "run-c", "2" * 64)
    bad = _ref(snap, count=1, digest="a").model_copy(update=mismatch)

    with pytest.raises(ValidationError):
        PausedChildCapture(child_workflow_id="wf-c", child_snapshot=snap, child_record_ref=bad)
    with pytest.raises(ValidationError):
        _carrier(snap, "wf-c", bad)


def test_a_ref_for_a_different_child_workflow_than_the_one_dispatched_is_refused() -> None:
    snap = _snapshot("wf-c", "run-c", "2" * 64)
    good = _ref(snap, count=1, digest="a")

    with pytest.raises(ValidationError):
        PausedChildCapture(
            child_workflow_id="wf-dispatched-elsewhere",
            child_snapshot=snap,
            child_record_ref=good,
        )
    with pytest.raises(ValidationError):
        _carrier(snap, "wf-dispatched-elsewhere", good)


def test_an_ephemeral_child_capture_carries_no_ref_and_the_error_exposes_it() -> None:
    snap = _snapshot("wf-c", "run-c", "2" * 64)
    ephemeral = PausedChildCapture(
        child_workflow_id="wf-c", child_snapshot=snap, child_record_ref=None
    )
    durable_ref = _ref(snap, count=2, digest="d")
    durable = PausedChildCapture(
        child_workflow_id="wf-c", child_snapshot=snap, child_record_ref=durable_ref
    )

    assert SubAgentChildPausedError(capture=ephemeral).capture.child_record_ref is None
    assert SubAgentChildPausedError(capture=durable).capture.child_record_ref == durable_ref


# --- the driver keeps each sibling's own ref in both families, incl. cancellation ---------


def _same_id_sibling_captures() -> dict[str, PausedChildCapture]:
    """Two children of ONE workflow id whose records differ only by position and digest."""
    snap = _snapshot("wf-child", "run-child", "c" * 64)
    return {
        f"w-{i}": PausedChildCapture(
            child_workflow_id="wf-child",
            child_snapshot=snap,
            child_record_ref=_ref(snap, count=i + 1, digest=str(i + 1)),
        )
        for i in range(2)
    }


class _PausingSubAgents:
    """`w-0` raises first; `w-1` waits for that, so w-0's raise cancels w-1 in flight."""

    def __init__(self, captures: dict[str, PausedChildCapture]) -> None:
        self._captures = captures
        self._gate = threading.Event()

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        sid = str(step.step_id)
        if sid == "w-0":
            self._gate.set()
        else:
            assert self._gate.wait(timeout=10.0)
        raise SubAgentChildPausedError(capture=self._captures[sid])


class _Registry:
    def __init__(self, sub_agents: _PausingSubAgents, echo: StepDispatcher) -> None:
        self._sub_agents = sub_agents
        self._echo = echo

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return cast(StepDispatcher, self._sub_agents)
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._echo
        raise StepKindDispatcherNotBoundError(step_kind)


def _sub_agent_step(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name), step_kind=StepKind.SUB_AGENT_DISPATCH, step_payload={}
    )


def _paused_by_two_same_id_children(
    family: str,
) -> tuple[tuple[PausedChildBranchResumeState, ...], PauseSnapshot]:
    sub_agents = _PausingSubAgents(_same_id_sibling_captures())
    if family == "fan_out":
        registry = _Registry(sub_agents, cast(StepDispatcher, _OwCountingDispatcher()))
        result = execute_workflow(
            _ow_manifest("wf-parent", TopologyPattern.HIERARCHICAL_DELEGATION),
            [
                WorkflowStep(
                    step_id=StepID("orch"),
                    step_kind=StepKind.DECLARATIVE_STEP,
                    step_payload={"role": "orch"},
                ),
                _sub_agent_step("w-0"),
                _sub_agent_step("w-1"),
            ],
            run_id="run-parent",
            ctx=cast(DriverContext, _OwCtx(ledger=_OwLedger(), emitter=_OwEmitter())),
            default_model_binding=_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, registry),
        )
        assert result.pause_snapshot is not None and result.pause_snapshot.fan_out_resume
        carrier = result.pause_snapshot.fan_out_resume
    else:
        registry = _Registry(sub_agents, cast(StepDispatcher, _OwCountingDispatcher()))
        result = execute_workflow(
            _peer_manifest("wf-parent"),
            [_sub_agent_step("w-0"), _sub_agent_step("w-1")],
            run_id="run-parent",
            ctx=cast(DriverContext, _PeerCtx(ledger=_PeerLedger(), emitter=_PeerEmitter())),
            default_model_binding=_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, registry),
        )
        assert result.pause_snapshot is not None and result.pause_snapshot.peer_fan_out_resume
        carrier = result.pause_snapshot.peer_fan_out_resume
    assert result.status is RunStatus.PAUSED
    return carrier.paused_child_branches, result.pause_snapshot


@pytest.mark.parametrize("family", ["fan_out", "peer"])
def test_two_same_id_sibling_children_keep_their_own_refs_in_the_parent_carrier(
    family: str,
) -> None:
    """Worker 0 is captured by the typed handler; worker 1 by the in-flight cancellation
    path. Both must keep the ref of their own record, not a shared or dropped one."""
    expected = _same_id_sibling_captures()
    carriers, _ = _paused_by_two_same_id_children(family)

    by_index = {c.branch_index: c for c in carriers}
    assert set(by_index) == {0, 1}
    for index, name in ((0, "w-0"), (1, "w-1")):
        assert by_index[index].child_workflow_id == "wf-child"
        assert by_index[index].child_record_ref == expected[name].child_record_ref
    refs = [c.child_record_ref for c in carriers]
    assert refs[0] is not None and refs[1] is not None and refs[0] != refs[1]


@pytest.mark.parametrize("family", ["fan_out", "peer"])
def test_the_parent_snapshot_hash_covers_each_carried_child_ref(family: str) -> None:
    carriers, snapshot = _paused_by_two_same_id_children(family)
    common: dict[str, Any] = {
        "workflow_id": snapshot.workflow_id,
        "run_id": snapshot.run_id,
        "step_index": snapshot.step_index,
        "state_summary": snapshot.state_summary,
    }
    carrier_key = "fan_out_resume" if family == "fan_out" else "peer_fan_out_resume"
    parent_carrier = getattr(snapshot, carrier_key)

    def parent_hash(swapped: tuple[PausedChildBranchResumeState, ...]) -> str:
        return _compute_snapshot_hash(
            **common,
            **{carrier_key: parent_carrier.model_copy(update={"paused_child_branches": swapped})},
        )

    assert parent_hash(carriers) == snapshot.snapshot_hash
    first, second = carriers
    exchanged = (
        first.model_copy(update={"child_record_ref": second.child_record_ref}),
        second,
    )
    assert parent_hash(exchanged) != snapshot.snapshot_hash
    dropped = (first.model_copy(update={"child_record_ref": None}), second)
    assert parent_hash(dropped) != snapshot.snapshot_hash

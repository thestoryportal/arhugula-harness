"""B-104 Task 4b (Runtime side): the dispatcher raise site carries the exact child ref, and a
real durable journal run keeps each paused child's own ref in the parent carrier.

Capture/carry only: nothing here resumes a child or reads a ref back into a run (Task 4c).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import JournalRecordRef, PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import PausedChildCapture, PauseSnapshot
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow_at_depth,
)
from harness_cp.workflow_driver_types import (
    RunResult,
    RunStatus,
    StepKind,
    SubAgentChildPausedError,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_runtime.lifecycle.audit_signing_errors import PostEffectAuditSigningError
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from pydantic import ValidationError

from .test_b104_task4a_capture_depth import (
    _DriverCtx,  # pyright: ignore[reportPrivateUsage]
    _FailingSecondStage,  # pyright: ignore[reportPrivateUsage]
    _protocol,  # pyright: ignore[reportPrivateUsage]
    _store,  # pyright: ignore[reportPrivateUsage]
)
from .test_lifecycle_sub_agent_dispatch import (
    _binding,  # pyright: ignore[reportPrivateUsage]
    _child_snapshot,  # pyright: ignore[reportPrivateUsage]
    _dispatcher,  # pyright: ignore[reportPrivateUsage]
    _FamilyRaisingAuditWriter,  # pyright: ignore[reportPrivateUsage]
    _paused_result,  # pyright: ignore[reportPrivateUsage]
    _step,  # pyright: ignore[reportPrivateUsage]
    _step_context,  # pyright: ignore[reportPrivateUsage]
)

_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


# --- the dispatcher raise site ------------------------------------------------------------


def _durable_paused_result(snapshot: PauseSnapshot) -> RunResult:
    ref = JournalRecordRef(
        tenant=None,
        workflow_id=snapshot.workflow_id,
        run_id=snapshot.run_id,
        record_count=7,
        latest_digest="e" * 64,
        snapshot_hash=snapshot.snapshot_hash,
    )
    return _paused_result(snapshot).model_copy(update={"pause_record_ref": ref})


def test_the_child_pause_error_carries_the_exact_ref_of_the_paused_run_result(
    tmp_path: Path,
) -> None:
    paused = _durable_paused_result(_child_snapshot())
    dispatcher, _, _ = _dispatcher(tmp_path, child_result=paused)

    with pytest.raises(SubAgentChildPausedError) as raised:
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())

    assert raised.value.capture.child_record_ref == paused.pause_record_ref
    assert raised.value.capture.child_record_ref is not None
    assert raised.value.capture.child_snapshot is paused.pause_snapshot


def test_an_ephemeral_child_pause_carries_no_ref(tmp_path: Path) -> None:
    dispatcher, _, _ = _dispatcher(tmp_path, child_result=_paused_result(_child_snapshot()))

    with pytest.raises(SubAgentChildPausedError) as raised:
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())

    assert raised.value.capture.child_record_ref is None


def test_a_ref_for_another_workflow_than_the_dispatched_child_is_refused_loudly(
    tmp_path: Path,
) -> None:
    """The dispatcher never hands the parent a ref that names a different child workflow."""
    other = _child_snapshot().model_copy(update={"workflow_id": "some-other-wf"})
    dispatcher, _, _ = _dispatcher(tmp_path, child_result=_durable_paused_result(other))

    with pytest.raises(ValidationError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())


def test_a_signing_failure_after_a_durable_child_pause_keeps_the_ref_on_the_carrier(
    tmp_path: Path,
) -> None:
    """The branch fails closed, but the orphaned child record stays identifiable."""
    paused = _durable_paused_result(_child_snapshot())
    dispatcher, _, _ = _dispatcher(
        tmp_path,
        child_result=paused,
        audit_writer_override=cast(Any, _FamilyRaisingAuditWriter()),
    )
    dispatcher.audit_signing_fail_closed = True

    with pytest.raises(PostEffectAuditSigningError) as raised:
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())

    assert cast(RunResult, raised.value.result).pause_record_ref == paused.pause_record_ref


# --- a real durable journal: parent -> child -> grandchild --------------------------------


def _manifest(workflow_id: str, topology: TopologyPattern) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,  # cascade_policy=pause
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step_of(name: str, kind: StepKind) -> WorkflowStep:
    return WorkflowStep(step_id=StepID(name), step_kind=kind, step_payload={"stage": name})


class _Echo:
    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        return {"echo": str(step.step_id)}


class _Registry:
    def __init__(self, declarative: Any, sub_agent: Any = None) -> None:
        self._by_kind = {
            StepKind.DECLARATIVE_STEP: declarative,
            StepKind.SUB_AGENT_DISPATCH: sub_agent,
        }

    def lookup(self, step_kind: StepKind) -> Any:
        dispatcher = self._by_kind.get(step_kind)
        if dispatcher is None:
            raise StepKindDispatcherNotBoundError(step_kind)
        return dispatcher


class _Descend:
    """Runs one child a level down on the shared durable protocol, then raises the child-pause
    error the way `sub_agent_dispatch` does (the raise site itself is tested above)."""

    def __init__(self, protocol: Any, run_child: Any) -> None:
        self._protocol = protocol
        self._run_child = run_child

    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any) -> Any:
        result: RunResult = self._run_child(
            str(step.step_id), self._protocol, step_context.descent_depth + 1
        )
        assert result.status is RunStatus.PAUSED and result.pause_snapshot is not None
        raise SubAgentChildPausedError(
            capture=PausedChildCapture(
                child_workflow_id=result.workflow_id,
                child_snapshot=result.pause_snapshot,
                child_record_ref=result.pause_record_ref,
            )
        )


def _run(
    workflow_id: str,
    topology: TopologyPattern,
    steps: list[WorkflowStep],
    registry: _Registry,
    *,
    run_id: str,
    protocol: Any,
    depth: int,
) -> RunResult:
    return execute_workflow_at_depth(
        _manifest(workflow_id, topology),
        steps,
        run_id=run_id,
        ctx=cast(DriverContext, _DriverCtx(protocol)),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, registry),
        descent_depth=depth,
    )


def _grandchild(run_id: str, protocol: Any, depth: int) -> RunResult:
    return _run(
        "wf-g",
        TopologyPattern.DECENTRALIZED_HANDOFF,
        [_step_of("s0", StepKind.DECLARATIVE_STEP), _step_of("s1", StepKind.DECLARATIVE_STEP)],
        _Registry(_FailingSecondStage()),
        run_id=run_id,
        protocol=protocol,
        depth=depth,
    )


def _child_over_grandchild(run_id: str, protocol: Any, depth: int) -> RunResult:
    return _run(
        "wf-c",
        TopologyPattern.HIERARCHICAL_DELEGATION,
        [_step_of("orch", StepKind.DECLARATIVE_STEP), _step_of("g-0", StepKind.SUB_AGENT_DISPATCH)],
        _Registry(_Echo(), _Descend(protocol, lambda _sid, p, d: _grandchild("run-g", p, d))),
        run_id=run_id,
        protocol=protocol,
        depth=depth,
    )


def test_parent_child_grandchild_refs_name_their_own_records_at_the_true_depths(
    tmp_path: Path,
) -> None:
    store: JournalWorkflowPauseStore = _store(tmp_path)
    protocol = _protocol(store)
    parent = _run(
        "wf-p",
        TopologyPattern.HIERARCHICAL_DELEGATION,
        [_step_of("orch", StepKind.DECLARATIVE_STEP), _step_of("c-0", StepKind.SUB_AGENT_DISPATCH)],
        _Registry(
            _Echo(), _Descend(protocol, lambda _sid, p, d: _child_over_grandchild("run-c", p, d))
        ),
        run_id="run-p",
        protocol=protocol,
        depth=0,
    )

    assert parent.status is RunStatus.PAUSED
    assert parent.pause_snapshot is not None and parent.pause_snapshot.fan_out_resume is not None
    (c_carrier,) = parent.pause_snapshot.fan_out_resume.paused_child_branches
    c_ref = c_carrier.child_record_ref
    assert c_ref is not None
    (g_carrier,) = c_carrier.child_snapshot.fan_out_resume.paused_child_branches  # type: ignore[union-attr]
    g_ref = g_carrier.child_record_ref
    assert g_ref is not None

    for ref, carrier, depth in ((c_ref, c_carrier, 1), (g_ref, g_carrier, 2)):
        at_ref = store.read_exact(ref)
        assert at_ref is not None
        assert at_ref.depth == depth
        assert at_ref.snapshot == carrier.child_snapshot
    assert parent.pause_record_ref is not None
    root_at_ref = store.read_exact(parent.pause_record_ref)
    assert root_at_ref is not None and root_at_ref.depth == 0

    # Each ref is covered by the snapshot hash of the level that holds it: dropping either
    # ref makes that level's recomputed hash disagree with the stored one.
    def parent_hash(carrier: Any) -> str:
        assert parent.pause_snapshot is not None and parent.pause_snapshot.fan_out_resume
        return _compute_snapshot_hash(
            workflow_id=parent.pause_snapshot.workflow_id,
            run_id=parent.pause_snapshot.run_id,
            step_index=parent.pause_snapshot.step_index,
            state_summary=parent.pause_snapshot.state_summary,
            fan_out_resume=parent.pause_snapshot.fan_out_resume.model_copy(
                update={"paused_child_branches": (carrier,)}
            ),
        )

    assert parent_hash(c_carrier) == parent.pause_snapshot.snapshot_hash
    assert parent_hash(c_carrier.model_copy(update={"child_record_ref": None})) != (
        parent.pause_snapshot.snapshot_hash
    )
    inner = c_carrier.child_snapshot.model_copy(
        update={
            "fan_out_resume": c_carrier.child_snapshot.fan_out_resume.model_copy(  # type: ignore[union-attr]
                update={
                    "paused_child_branches": (
                        g_carrier.model_copy(update={"child_record_ref": None}),
                    )
                }
            )
        }
    )
    assert parent_hash(c_carrier.model_copy(update={"child_snapshot": inner})) != (
        parent.pause_snapshot.snapshot_hash
    )


def test_two_same_workflow_siblings_in_one_journal_carry_their_own_records(
    tmp_path: Path,
) -> None:
    """Both children append to ONE journal file (same workflow id); each carrier must name
    the record its own child wrote, at depth 1, never the latest."""
    store = _store(tmp_path)
    protocol = _protocol(store)
    parent = _run(
        "wf-p",
        TopologyPattern.HIERARCHICAL_DELEGATION,
        [
            _step_of("orch", StepKind.DECLARATIVE_STEP),
            _step_of("w-0", StepKind.SUB_AGENT_DISPATCH),
            _step_of("w-1", StepKind.SUB_AGENT_DISPATCH),
        ],
        _Registry(
            _Echo(),
            _Descend(protocol, lambda sid, p, d: _grandchild(f"run-{sid}", p, d)),
        ),
        run_id="run-p",
        protocol=protocol,
        depth=0,
    )

    assert parent.pause_snapshot is not None and parent.pause_snapshot.fan_out_resume is not None
    carriers = {
        c.branch_index: c for c in parent.pause_snapshot.fan_out_resume.paused_child_branches
    }
    assert set(carriers) == {0, 1}
    refs = [carriers[0].child_record_ref, carriers[1].child_record_ref]
    assert refs[0] is not None and refs[1] is not None and refs[0] != refs[1]
    assert {r.record_count for r in refs} == {1, 2}
    for index, ref in enumerate(refs):
        assert ref is not None
        at_ref = store.read_exact(ref)
        assert at_ref is not None
        assert at_ref.depth == 1
        assert at_ref.snapshot.run_id == f"run-w-{index}"

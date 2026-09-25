"""B-104 Task 4c (Runtime side): a durable paused child is verified against its exact journal
record and then refused at the required admission seam; nothing of it runs.

Real durable protocol and journal throughout. The parent/child/grandchild records come from
the same driver-to-journal run as the Task 4b witnesses. Provider-free, no live service.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from harness_core import StepID
from harness_cp.pause_resume_protocol_types import (
    PausedChildBranchResumeState,
    PausedChildCapture,
    WorkflowPauseReason,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcherRegistry,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    ChildResumeRefusal,
    ChildResumeRefusedError,
    RunResult,
    RunStatus,
    StepKind,
    WorkflowStep,
)
from harness_runtime.lifecycle import child_workflow_runner as cwr
from harness_runtime.lifecycle.durable_child_admission import (
    RefuseDurableChildAdmission,
    VerifiedChildRecord,
)
from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from pydantic import ValidationError

from .test_b104_task4a_capture_depth import (
    _DriverCtx,  # pyright: ignore[reportPrivateUsage]
    _protocol,  # pyright: ignore[reportPrivateUsage]
    _store,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_task4b_dispatch_and_journal_refs import (
    _BINDING,  # pyright: ignore[reportPrivateUsage]
    _child_over_grandchild,  # pyright: ignore[reportPrivateUsage]
    _Descend,  # pyright: ignore[reportPrivateUsage]
    _Echo,  # pyright: ignore[reportPrivateUsage]
    _grandchild,  # pyright: ignore[reportPrivateUsage]
    _manifest,  # pyright: ignore[reportPrivateUsage]
    _Registry,  # pyright: ignore[reportPrivateUsage]
    _run,  # pyright: ignore[reportPrivateUsage]
    _step_of,  # pyright: ignore[reportPrivateUsage]
)
from .test_lifecycle_sub_agent_dispatch import (
    _dispatcher,  # pyright: ignore[reportPrivateUsage]
    _payload,  # pyright: ignore[reportPrivateUsage]
)


class _RecordingAdmission:
    """A permissive test double that records what verification proved."""

    def __init__(self) -> None:
        self.admitted: list[VerifiedChildRecord] = []

    def run_admitted(self, verified: VerifiedChildRecord, body: Callable[[], Any]) -> Any:
        self.admitted.append(verified)
        return body()


class _ExecuteSpy:
    """Stands in for `execute_workflow_at_depth`: any call means a child was let run."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append({"run_id": args[2], **kwargs})
        return cast(Any, object())


def _runner_over(
    protocol: Any, admission: Any, monkeypatch: pytest.MonkeyPatch
) -> tuple[Any, _ExecuteSpy]:
    spy = _ExecuteSpy()
    monkeypatch.setattr(cwr, "execute_workflow_at_depth", spy)
    ctx = SimpleNamespace(pause_resume_protocol=protocol, step_dispatchers={})
    return cwr.compose_child_workflow_runner(cast(Any, ctx), durable_admission=admission), spy


def _resume(runner: Any, capture: PausedChildCapture, *, depth: int) -> Any:
    return runner(
        workflow_id=capture.child_workflow_id,
        manifest_entry=cast(Any, None),
        steps=(),
        handoff_context=cast(Any, None),
        descent=cast(Any, SimpleNamespace(child_gate_level=None)),
        default_model_binding=cast(Any, None),
        descent_depth=depth,
        child_resume=capture,
    )


def _journal_line_counts(root: Path) -> dict[str, int]:
    return {
        p.name: len(p.read_bytes().splitlines()) for p in sorted(root.rglob("*")) if p.is_file()
    }


class _Site:
    """A durable P -> C -> G pause whose carriers hold the real, exact journal refs."""

    def __init__(self, tmp_path: Path) -> None:
        self.root = tmp_path / "pj"
        self.store: JournalWorkflowPauseStore = _store(tmp_path)
        self.protocol: DurablePauseResumeProtocol = _protocol(self.store)
        self.parent: RunResult = _run(
            "wf-p",
            TopologyPattern.HIERARCHICAL_DELEGATION,
            [
                _step_of("orch", StepKind.DECLARATIVE_STEP),
                _step_of("c-0", StepKind.SUB_AGENT_DISPATCH),
            ],
            _Registry(
                _Echo(),
                _Descend(self.protocol, lambda _sid, p, d: _child_over_grandchild("run-c", p, d)),
            ),
            run_id="run-p",
            protocol=self.protocol,
            depth=0,
        )
        assert self.parent.pause_snapshot is not None
        assert self.parent.pause_snapshot.fan_out_resume is not None
        (self.c_carrier,) = self.parent.pause_snapshot.fan_out_resume.paused_child_branches
        assert self.c_carrier.child_snapshot.fan_out_resume is not None
        (self.g_carrier,) = self.c_carrier.child_snapshot.fan_out_resume.paused_child_branches

    @property
    def c(self) -> PausedChildCapture:
        return self.c_carrier.as_capture()

    @property
    def g(self) -> PausedChildCapture:
        return self.g_carrier.as_capture()


@pytest.fixture
def site(tmp_path: Path) -> _Site:
    return _Site(tmp_path)


# --- what admission is shown ---------------------------------------------------------------


def test_admission_sees_the_exact_verified_ref_and_depth_of_child_and_grandchild(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    admission = _RecordingAdmission()
    runner, spy = _runner_over(site.protocol, admission, monkeypatch)

    _resume(runner, site.c, depth=1)
    _resume(runner, site.g, depth=2)

    assert [(v.ref, v.depth) for v in admission.admitted] == [
        (site.c.child_record_ref, 1),
        (site.g.child_record_ref, 2),
    ]
    assert [v.snapshot for v in admission.admitted] == [
        site.c.child_snapshot,
        site.g.child_snapshot,
    ]
    assert len(spy.calls) == 2  # admitted children then reach the driver


def test_same_workflow_siblings_are_each_verified_against_their_own_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Record N must still verify after N+1 exists (journal-latest would refuse it)."""
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
        _Registry(_Echo(), _Descend(protocol, lambda sid, p, d: _grandchild(f"run-{sid}", p, d))),
        run_id="run-p",
        protocol=protocol,
        depth=0,
    )
    assert parent.pause_snapshot is not None and parent.pause_snapshot.fan_out_resume is not None
    carriers = sorted(
        parent.pause_snapshot.fan_out_resume.paused_child_branches, key=lambda c: c.branch_index
    )
    admission = _RecordingAdmission()
    runner, _ = _runner_over(protocol, admission, monkeypatch)

    for carrier in reversed(carriers):  # newest record first, then the older one
        _resume(runner, carrier.as_capture(), depth=1)

    refs = [v.ref for v in admission.admitted]
    assert refs == [carriers[1].child_record_ref, carriers[0].child_record_ref]
    assert {r.record_count for r in refs} == {1, 2}
    assert {r.workflow_id for r in refs} == {"wf-g"}


# --- refusals happen before admission and before any execution ---------------------------


def _mutated(capture: PausedChildCapture, **update: Any) -> PausedChildCapture:
    ref = capture.child_record_ref
    assert ref is not None
    return PausedChildCapture(
        child_workflow_id=capture.child_workflow_id,
        child_snapshot=capture.child_snapshot,
        child_record_ref=ref.model_copy(update=update),
    )


@pytest.mark.parametrize(
    ("case", "reason"),
    [
        ("missing-ref", ChildResumeRefusal.MISSING_REF),
        ("count-beyond-journal", ChildResumeRefusal.UNREADABLE_RECORD),
        ("wrong-digest", ChildResumeRefusal.UNREADABLE_RECORD),
        ("altered-snapshot", ChildResumeRefusal.SNAPSHOT_MISMATCH),
        ("wrong-depth", ChildResumeRefusal.DEPTH_MISMATCH),
    ],
)
def test_a_child_that_is_not_its_exact_journal_record_is_refused_before_admission(
    site: _Site, monkeypatch: pytest.MonkeyPatch, case: str, reason: ChildResumeRefusal
) -> None:
    capture, depth = site.c, 1
    if case == "missing-ref":
        capture = PausedChildCapture(
            child_workflow_id=capture.child_workflow_id,
            child_snapshot=capture.child_snapshot,
            child_record_ref=None,
        )
    elif case == "count-beyond-journal":
        capture = _mutated(capture, record_count=99)
    elif case == "wrong-digest":
        capture = _mutated(capture, latest_digest="0" * 64)
    elif case == "altered-snapshot":
        # Same workflow/run/hash (so the capture still forms) but not the journaled bytes.
        capture = PausedChildCapture(
            child_workflow_id=capture.child_workflow_id,
            child_snapshot=capture.child_snapshot.model_copy(update={"created_at": 1}),
            child_record_ref=capture.child_record_ref,
        )
    else:
        depth = 2  # the record was journaled at depth 1
    admission = _RecordingAdmission()
    runner, spy = _runner_over(site.protocol, admission, monkeypatch)
    before = _journal_line_counts(site.root)

    with pytest.raises(ChildResumeRefusedError) as raised:
        _resume(runner, capture, depth=depth)

    assert raised.value.reason is reason
    assert admission.admitted == [] and spy.calls == []
    assert _journal_line_counts(site.root) == before


def test_a_record_journaled_without_a_depth_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pre-Task-4a records have `depth=None`; a durable child never resumes from one."""
    store = _store(tmp_path)
    paused = _grandchild("run-legacy", _protocol(store), 1)
    assert paused.pause_snapshot is not None
    legacy_snapshot = paused.pause_snapshot.model_copy(update={"run_id": "run-legacy-no-depth"})
    legacy_ref = store.capture(legacy_snapshot, depth=None)
    at_ref = store.read_exact(legacy_ref)
    assert at_ref is not None and at_ref.depth is None
    capture = PausedChildCapture(
        child_workflow_id=legacy_ref.workflow_id,
        child_snapshot=legacy_snapshot,
        child_record_ref=legacy_ref,
    )
    admission = _RecordingAdmission()
    runner, spy = _runner_over(_protocol(store), admission, monkeypatch)

    with pytest.raises(ChildResumeRefusedError) as raised:
        _resume(runner, capture, depth=1)

    assert raised.value.reason is ChildResumeRefusal.DEPTH_MISMATCH
    assert admission.admitted == [] and spy.calls == []


def test_a_sibling_ref_cannot_be_swapped_onto_another_siblings_snapshot(site: _Site) -> None:
    """Refs bind their snapshot's workflow, run and hash, so a swap cannot even form."""
    other = site.g.child_record_ref
    assert other is not None
    with pytest.raises(ValidationError):
        PausedChildCapture(
            child_workflow_id=site.c.child_workflow_id,
            child_snapshot=site.c.child_snapshot,
            child_record_ref=other,
        )
    with pytest.raises(ValidationError):
        PausedChildBranchResumeState(
            branch_index=0,
            step_id="c-0",
            child_workflow_id=site.c.child_workflow_id,
            child_snapshot=site.c.child_snapshot,
            child_record_ref=other,
        )


# --- the production binding refuses; ephemeral is unchanged ------------------------------


def test_the_production_binding_refuses_a_fully_verified_child_and_runs_nothing(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner, spy = _runner_over(site.protocol, RefuseDurableChildAdmission(), monkeypatch)
    before = _journal_line_counts(site.root)

    with pytest.raises(ChildResumeRefusedError) as raised:
        _resume(runner, site.c, depth=1)

    assert raised.value.reason is ChildResumeRefusal.GATEWAY_NOT_INSTALLED
    assert spy.calls == []
    assert _journal_line_counts(site.root) == before


def test_an_ephemeral_protocol_resumes_exactly_as_before(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    admission = _RecordingAdmission()
    ephemeral = object()  # not a durable protocol: no journal record exists to verify
    runner, spy = _runner_over(ephemeral, admission, monkeypatch)
    bare = PausedChildCapture(
        child_workflow_id=site.c.child_workflow_id,
        child_snapshot=site.c.child_snapshot,
        child_record_ref=None,
    )

    _resume(runner, bare, depth=1)

    assert admission.admitted == []
    assert len(spy.calls) == 1
    assert spy.calls[0]["pause_snapshot_input"] is bare.child_snapshot
    assert spy.calls[0]["run_id"] == bare.child_snapshot.run_id


# --- real dispatcher + real child runner + durable protocol + journal --------------------


class _CountingBodies:
    """Every child-body dispatcher a non-refused resume would use; must stay at zero."""

    def __init__(self) -> None:
        self.invocations = 0

    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        self.invocations += 1
        return {}


def test_a_real_composed_resume_refuses_at_admission_and_the_parent_fails_terminally(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _store(tmp_path)
    protocol = _protocol(store)
    payload = _payload()
    step = WorkflowStep(
        step_id=StepID("c-0"),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload=payload.model_dump(),
    )
    steps = [_step_of("orch", StepKind.DECLARATIVE_STEP), step]

    def child_paused(_sid: str, p: Any, d: int) -> RunResult:
        result = _run(
            "child-wf",
            TopologyPattern.DECENTRALIZED_HANDOFF,
            [_step_of("s0", StepKind.DECLARATIVE_STEP), _step_of("s1", StepKind.DECLARATIVE_STEP)],
            _Registry(_FailingSecondStage()),
            run_id="run-child",
            protocol=p,
            depth=d,
        )
        return result

    first = _run(
        "wf-p",
        TopologyPattern.HIERARCHICAL_DELEGATION,
        steps,
        _Registry(_Echo(), _Descend(protocol, child_paused)),
        run_id="run-p",
        protocol=protocol,
        depth=0,
    )
    assert first.status is RunStatus.PAUSED and first.pause_snapshot is not None
    root = tmp_path / "pj"
    before = _journal_line_counts(root)

    # Resume through the REAL dispatcher and the REAL composed runner (production binding).
    bodies = _CountingBodies()
    spy = _ExecuteSpy()
    monkeypatch.setattr(cwr, "execute_workflow_at_depth", spy)
    dispatcher, _, _ = _dispatcher(tmp_path)
    dispatcher.child_workflow_runner = cwr.compose_child_workflow_runner(
        cast(Any, SimpleNamespace(pause_resume_protocol=protocol, step_dispatchers=bodies)),
        durable_admission=RefuseDurableChildAdmission(),
    )
    resumed = execute_workflow(
        _manifest("wf-p", TopologyPattern.HIERARCHICAL_DELEGATION),
        steps,
        run_id="run-p",
        ctx=cast(DriverContext, _DriverCtx(protocol)),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(_Echo(), dispatcher)),
        pause_snapshot_input=first.pause_snapshot,
    )

    assert resumed.status is RunStatus.FAILED
    assert resumed.fail_class == (
        "orchestrator-workers-child-resume-refused (gateway-not-installed)"
    )
    assert resumed.pause_snapshot is None and resumed.pause_record_ref is None
    assert bodies.invocations == 0 and spy.calls == []
    assert _journal_line_counts(root) == before


class _FailingSecondStage:
    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        if str(step.step_id) == "s1":
            raise RuntimeError("simulated stage failure")
        return {"stage": str(step.step_id)}


@pytest.mark.asyncio
async def test_the_real_stage_5_binding_refuses_a_durable_child_it_has_fully_verified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The runner stage 5 actually composes, on a real durable bootstrap, has no gateway
    yet: it verifies the carried record and then refuses, so nothing of the child runs."""
    from harness_runtime.bootstrap import run_bootstrap
    from harness_runtime.lifecycle.pause_resume_protocol_types import PauseResumeProtocolConfig
    from harness_runtime.lifecycle.sub_agent_dispatch import RuntimeSubAgentDispatcher

    from .test_bootstrap import (
        _WORKLOAD,  # pyright: ignore[reportPrivateUsage]
        _config,  # pyright: ignore[reportPrivateUsage]
        _patch_collector,  # pyright: ignore[reportPrivateUsage]
        _patch_providers,  # pyright: ignore[reportPrivateUsage]
    )

    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    config = _config(tmp_path).model_copy(
        update={"pause_resume_protocol_config": PauseResumeProtocolConfig(durable=True)}
    )
    ctx = await run_bootstrap(config, workload_class=_WORKLOAD)
    assert isinstance(ctx.pause_resume_protocol, DurablePauseResumeProtocol)
    assert isinstance(ctx.sub_agent_dispatcher.inner, RuntimeSubAgentDispatcher)  # type: ignore[union-attr]
    runner = ctx.sub_agent_dispatcher.inner.child_workflow_runner  # type: ignore[union-attr]
    captured = await ctx.pause_resume_protocol.capture_pause_snapshot(
        "child-wf", "run-c", 0, WorkflowPauseReason.EXPLICIT_OPERATOR, descent_depth=1
    )
    capture = PausedChildCapture(
        child_workflow_id="child-wf",
        child_snapshot=captured.snapshot,
        child_record_ref=captured.record_ref,
    )

    with pytest.raises(ChildResumeRefusedError) as raised:
        _resume(runner, capture, depth=1)

    assert raised.value.reason is ChildResumeRefusal.GATEWAY_NOT_INSTALLED

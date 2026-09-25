"""B-104 Task 4c correction: a child-resume refusal is terminal even when audit signing fails,
and a legacy workflow-id mismatch is a typed refusal, not a generic `ValueError`.

Real `RuntimeSubAgentDispatcher` + real composed child runner (production refusing admission)
+ real durable protocol and journal, driven through BOTH CP fan-out families under the pause
cascade. With `audit_signing_fail_closed=True` and a signing failure while the dispatcher
composes its best-effort audit, the raised object must still be a `ChildResumeRefusedError`
(so CP ends the run FAILED) AND a member of the signing family (U-RT-136), and must never be
the completed-effect `PostEffectAuditSigningError`.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from harness_core import StepID
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import PausedChildCapture, PauseSnapshot
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
from harness_runtime.lifecycle.audit_signing_errors import (
    AUDIT_SIGNING_HARD_FAILURES,
    PostEffectAuditSigningError,
)
from harness_runtime.lifecycle.durable_child_admission import RefuseDurableChildAdmission

from .test_b104_task4a_capture_depth import (
    _DriverCtx,  # pyright: ignore[reportPrivateUsage]
    _FailingSecondStage,  # pyright: ignore[reportPrivateUsage]
    _protocol,  # pyright: ignore[reportPrivateUsage]
    _store,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_task4b_dispatch_and_journal_refs import (
    _BINDING,  # pyright: ignore[reportPrivateUsage]
    _Descend,  # pyright: ignore[reportPrivateUsage]
    _Echo,  # pyright: ignore[reportPrivateUsage]
    _manifest,  # pyright: ignore[reportPrivateUsage]
    _Registry,  # pyright: ignore[reportPrivateUsage]
    _run,  # pyright: ignore[reportPrivateUsage]
    _step_of,  # pyright: ignore[reportPrivateUsage]
)
from .test_lifecycle_sub_agent_dispatch import (
    _binding,  # pyright: ignore[reportPrivateUsage]
    _dispatcher,  # pyright: ignore[reportPrivateUsage]
    _FamilyRaisingAuditWriter,  # pyright: ignore[reportPrivateUsage]
    _payload,  # pyright: ignore[reportPrivateUsage]
    _step,  # pyright: ignore[reportPrivateUsage]
    _step_context,  # pyright: ignore[reportPrivateUsage]
)

_FAMILIES = {
    "fan_out": (TopologyPattern.HIERARCHICAL_DELEGATION, "orchestrator-workers"),
    "peer": (TopologyPattern.PARALLELIZATION, "parallelization"),
}


class _CountingBodies:
    """Every child-body dispatcher a non-refused resume would use; must stay at zero."""

    def __init__(self) -> None:
        self.invocations = 0

    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        self.invocations += 1
        return {}


class _ExecuteSpy:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        return cast(Any, object())


def _journal_lines(tmp_path: Path) -> dict[str, int]:
    root = tmp_path / "pj"
    return {
        p.name: len(p.read_bytes().splitlines()) for p in sorted(root.rglob("*")) if p.is_file()
    }


class _Site:
    """A durable parent (in the given family) paused on one child of workflow `child-wf`."""

    def __init__(self, tmp_path: Path, family: str) -> None:
        self.tmp_path = tmp_path
        self.topology, self.prefix = _FAMILIES[family]
        self.protocol = _protocol(_store(tmp_path))
        payload = _payload()
        worker = WorkflowStep(
            step_id=StepID("c-0"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload=payload.model_dump(),
        )
        self.steps = (
            [worker] if family == "peer" else [_step_of("orch", StepKind.DECLARATIVE_STEP), worker]
        )

        def child_paused(_sid: str, p: Any, d: int) -> RunResult:
            return _run(
                "child-wf",
                TopologyPattern.DECENTRALIZED_HANDOFF,
                [
                    _step_of("s0", StepKind.DECLARATIVE_STEP),
                    _step_of("s1", StepKind.DECLARATIVE_STEP),
                ],
                _Registry(_FailingSecondStage()),
                run_id="run-child",
                protocol=p,
                depth=d,
            )

        first = _run(
            "wf-p",
            self.topology,
            self.steps,
            _Registry(_Echo(), _Descend(self.protocol, child_paused)),
            run_id="run-p",
            protocol=self.protocol,
            depth=0,
        )
        assert first.status is RunStatus.PAUSED and first.pause_snapshot is not None
        self.snapshot: PauseSnapshot = first.pause_snapshot

    def carrier(self) -> Any:
        parent = (
            self.snapshot.fan_out_resume
            if self.snapshot.fan_out_resume is not None
            else self.snapshot.peer_fan_out_resume
        )
        assert parent is not None
        (carrier,) = parent.paused_child_branches
        return carrier

    def resume(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        fail_closed: bool,
        signing_failure: bool,
        snapshot: PauseSnapshot | None = None,
    ) -> tuple[RunResult, _CountingBodies, _ExecuteSpy]:
        bodies, spy = _CountingBodies(), _ExecuteSpy()
        monkeypatch.setattr(cwr, "execute_workflow_at_depth", spy)
        dispatcher, _, _ = _dispatcher(
            self.tmp_path,
            audit_writer_override=cast(Any, _FamilyRaisingAuditWriter())
            if signing_failure
            else None,
        )
        dispatcher.audit_signing_fail_closed = fail_closed
        dispatcher.child_workflow_runner = cwr.compose_child_workflow_runner(
            cast(
                Any,
                SimpleNamespace(pause_resume_protocol=self.protocol, step_dispatchers=bodies),
            ),
            durable_admission=RefuseDurableChildAdmission(),
        )
        result = execute_workflow(
            _manifest("wf-p", self.topology),
            self.steps,
            run_id="run-p",
            ctx=cast(DriverContext, _DriverCtx(self.protocol)),
            default_model_binding=_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, _Registry(_Echo(), dispatcher)),
            pause_snapshot_input=snapshot if snapshot is not None else self.snapshot,
        )
        return result, bodies, spy


@pytest.fixture(params=sorted(_FAMILIES))
def site(request: pytest.FixtureRequest, tmp_path: Path) -> _Site:
    return _Site(tmp_path, request.param)


# --- a signing failure must not turn a refusal into a re-pause ---------------------------


def test_a_refusal_with_a_signing_failure_under_fail_closed_still_fails_the_parent_terminally(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = _journal_lines(site.tmp_path)

    result, bodies, spy = site.resume(monkeypatch, fail_closed=True, signing_failure=True)

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert result.fail_class.startswith(f"{site.prefix}-child-resume-refused")
    assert "gateway-not-installed" in result.fail_class
    assert "audit-signing-failed" in result.fail_class
    assert result.pause_snapshot is None and result.pause_record_ref is None
    assert _journal_lines(site.tmp_path) == before  # no capture, no new journal line
    assert bodies.invocations == 0 and spy.calls == 0


def test_the_raised_carrier_is_both_a_refusal_and_a_signing_failure_never_a_completed_effect(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    dispatcher, _, _ = _dispatcher(
        site.tmp_path, audit_writer_override=cast(Any, _FamilyRaisingAuditWriter())
    )
    dispatcher.audit_signing_fail_closed = True
    monkeypatch.setattr(cwr, "execute_workflow_at_depth", _ExecuteSpy())
    dispatcher.child_workflow_runner = cwr.compose_child_workflow_runner(
        cast(Any, SimpleNamespace(pause_resume_protocol=site.protocol, step_dispatchers={})),
        durable_admission=RefuseDurableChildAdmission(),
    )
    context = _step_context().model_copy(update={"child_resume": site.carrier().as_capture()})

    with pytest.raises(Exception) as raised:
        dispatcher.dispatch(_binding(), _step(), step_context=context)

    assert isinstance(raised.value, ChildResumeRefusedError)
    assert isinstance(raised.value, AUDIT_SIGNING_HARD_FAILURES)
    assert not isinstance(raised.value, PostEffectAuditSigningError)
    assert raised.value.reason is ChildResumeRefusal.GATEWAY_NOT_INSTALLED
    assert raised.value.audit_signing_failed is True
    assert raised.value.__cause__ is not None  # the signing failure stays attributable


# --- controls: the correction changes nothing where signing is not in play ----------------


@pytest.mark.parametrize(
    ("fail_closed", "signing_failure"),
    [(False, True), (True, False), (False, False)],
    ids=["sign-off-with-failing-writer", "fail-closed-healthy-writer", "sign-off-healthy-writer"],
)
def test_without_a_fail_closed_signing_failure_the_plain_refusal_is_raised_and_terminal(
    site: _Site, monkeypatch: pytest.MonkeyPatch, fail_closed: bool, signing_failure: bool
) -> None:
    result, bodies, spy = site.resume(
        monkeypatch, fail_closed=fail_closed, signing_failure=signing_failure
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert result.fail_class.startswith(f"{site.prefix}-child-resume-refused")
    assert "audit-signing-failed" not in result.fail_class
    assert result.pause_snapshot is None
    assert bodies.invocations == 0 and spy.calls == 0


# --- a legacy carrier whose child workflow differs is a typed, terminal refusal ------------


def test_a_legacy_carrier_for_a_different_child_workflow_fails_terminally(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No recorded `child_workflow_id` and no ref (a pre-4b carrier) skips CP's identity
    guard, so the runner is the only place that can notice the child changed."""
    carrier = site.carrier()
    legacy = carrier.model_copy(
        update={
            "child_workflow_id": None,
            "child_record_ref": None,
            "child_snapshot": carrier.child_snapshot.model_copy(update={"workflow_id": "other-wf"}),
        }
    )
    key = "fan_out_resume" if site.snapshot.fan_out_resume is not None else "peer_fan_out_resume"
    parent = getattr(site.snapshot, key).model_copy(update={"paused_child_branches": (legacy,)})
    tampered = site.snapshot.model_copy(
        update={
            key: parent,
            "snapshot_hash": _compute_snapshot_hash(
                workflow_id=site.snapshot.workflow_id,
                run_id=site.snapshot.run_id,
                step_index=site.snapshot.step_index,
                state_summary=site.snapshot.state_summary,
                **{key: parent},
            ),
        }
    )
    before = _journal_lines(site.tmp_path)

    result, bodies, spy = site.resume(
        monkeypatch, fail_closed=False, signing_failure=False, snapshot=tampered
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert result.fail_class.startswith(f"{site.prefix}-child-resume-refused")
    assert "workflow-mismatch" in result.fail_class
    assert result.pause_snapshot is None
    assert _journal_lines(site.tmp_path) == before
    assert bodies.invocations == 0 and spy.calls == 0


def test_the_runner_raises_a_typed_workflow_mismatch_before_verification(
    site: _Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = cwr.compose_child_workflow_runner(
        cast(Any, SimpleNamespace(pause_resume_protocol=site.protocol, step_dispatchers={})),
        durable_admission=RefuseDurableChildAdmission(),
    )
    capture: PausedChildCapture = site.carrier().as_capture()

    with pytest.raises(ChildResumeRefusedError) as raised:
        runner(
            workflow_id="a-different-child-wf",
            manifest_entry=cast(Any, None),
            steps=(),
            handoff_context=cast(Any, None),
            descent=cast(Any, None),
            default_model_binding=cast(Any, None),
            descent_depth=1,
            child_resume=capture,
        )

    assert raised.value.reason is ChildResumeRefusal.WORKFLOW_MISMATCH
    assert json.dumps(str(raised.value)).count(str(site.tmp_path)) == 0

"""B-314 fork §6 — an engine-native pause taken by `api.run` resumes through `api.resume`.

The pause is real: a WAL or reconciler workflow pauses before step 1 through the provider-free
bootstrap, the CP driver and the engine substrate, and the root body journals its locator. Resume
re-bootstraps over the same state root and the same F2 ledger. Both calls run in this process;
nothing here is a separate-process or installed-host witness.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from harness_core.identity import StepID
from harness_cp import workflow_driver
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol import CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION, ResumeOutcomeKind
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_is.state_ledger_write import read_ledger
from harness_runtime import bootstrap as bootstrap_module
from harness_runtime.api import resume, run
from harness_runtime.lifecycle.engine_recovery_loop import RuntimeEngineRecoveryLoop

from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
)
from .test_b104_root_resume_facade import (
    _WORKFLOW_ID,  # pyright: ignore[reportPrivateUsage]
    Harness,
    _assert_refused,  # pyright: ignore[reportPrivateUsage]
    _Dispatcher,  # pyright: ignore[reportPrivateUsage]
    _durable_filesystem,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _outcome,  # pyright: ignore[reportPrivateUsage]
    _Workflow,  # pyright: ignore[reportPrivateUsage]
)
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock"),
    pytest.mark.usefixtures("_patched_runtime"),
]

_ENGINES = pytest.mark.parametrize(
    ("engine_class", "literal"),
    [(EngineClass.WAL_SEGMENT, "WAL-segment"), (EngineClass.RECONCILER_LOOP, "reconciler-loop")],
)


class _Observed:
    """Every bootstrapped context, CP driver run_id and engine `attempt_resume` outcome, in order.

    `api.RunResult` carries no run_id, so run identity is read from the CP driver's own result."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.contexts: list[Any] = []
        self.run_ids: list[str] = []
        self.fail_classes: list[str | None] = []
        self.outcomes: list[ResumeOutcomeKind] = []
        bootstrap, attempt = (
            bootstrap_module.run_bootstrap,
            RuntimeEngineRecoveryLoop.attempt_resume,
        )
        execute = workflow_driver.execute_workflow

        def executed(*args: Any, **kwargs: Any) -> Any:
            result = execute(*args, **kwargs)
            self.run_ids.append(result.run_id)
            self.fail_classes.append(result.fail_class)
            return result

        async def bootstrapped(*args: Any, **kwargs: Any) -> Any:
            self.contexts.append(await bootstrap(*args, **kwargs))
            return self.contexts[-1]

        async def attempted(loop: RuntimeEngineRecoveryLoop, **kwargs: Any) -> Any:
            emission = await attempt(loop, **kwargs)
            self.outcomes.append(emission.resume_outcome.outcome_kind)
            return emission

        monkeypatch.setattr(bootstrap_module, "run_bootstrap", bootstrapped)
        monkeypatch.setattr(RuntimeEngineRecoveryLoop, "attempt_resume", attempted)
        monkeypatch.setattr(workflow_driver, "execute_workflow", executed)

    def resume_attempts(self) -> int:
        handle = self.contexts[-1].engine_recovery_loop.wiring.ledger_writer.handle
        return [e.action_id for e in read_ledger(handle)].count("cp.resume-attempted")

    def ledger_path(self) -> Path:
        return self.contexts[0].engine_recovery_loop.wiring.ledger_writer.handle.canonical_path


def _workflow(engine_class: EngineClass, dispatcher: _Dispatcher) -> _Workflow:
    workflow = _Workflow(dispatcher)
    workflow.manifest_entry = workflow.manifest_entry.model_copy(
        update={"engine_class": engine_class}
    )
    workflow.steps = tuple(
        WorkflowStep(
            step_id=StepID(f"step-{i}"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        )
        for i in range(2)
    )
    return workflow


async def _paused_at_step_1(h: Harness, seen: _Observed, engine_class: EngineClass) -> str:
    """Run until step 0 commits, then pause; return the run_id the pause belongs to."""
    dispatcher = _Dispatcher(lambda: seen.contexts[-1].pause_requested_flag.set())
    paused = await run(_workflow(engine_class, dispatcher), config=h.config)
    assert (paused.status, dispatcher.steps) == ("paused", ["step-0"]), paused
    return seen.run_ids[-1]


def _journaled_locators(h: Harness) -> Sequence[dict[str, Any]]:
    lines = (
        json.loads(line)
        for path in sorted(h.journal_dir.rglob("*"))
        if path.is_file()
        for line in path.read_text().splitlines()
        if line.strip()
    )
    return [line for line in lines if line.get("kind") == "engine-pause-locator"]


def _engine_records(h: Harness) -> list[Path]:
    return [p for p in h.site.base.rglob("*") if p.is_file() and "engine-recovery" in str(p)]


@pytest.fixture
def harness(world: Path) -> Harness:  # noqa: F811
    return Harness(world)


@pytest.fixture
def seen(monkeypatch: pytest.MonkeyPatch) -> _Observed:
    return _Observed(monkeypatch)


@pytest.mark.asyncio
@_ENGINES
async def test_an_engine_pause_resumes_once_under_its_run_id_without_redispatching_its_prefix(
    harness: Harness, seen: _Observed, engine_class: EngineClass, literal: str
) -> None:
    run_id = await _paused_at_step_1(harness, seen, engine_class)
    [locator] = _journaled_locators(harness)
    assert (locator["engine_class"], locator["step_index"]) == (literal, 1)
    assert EngineClass(locator["engine_class"]) is engine_class

    resumed = _Dispatcher()
    result = await resume(
        _workflow(engine_class, resumed), resume_handle=_WORKFLOW_ID, config=harness.config
    )

    assert (result.status, seen.run_ids, resumed.steps) == ("completed", [run_id] * 2, ["step-1"])
    assert locator["run_id"] == run_id
    assert seen.outcomes == [ResumeOutcomeKind.RESUME_CLEAN]
    assert seen.resume_attempts() == 1

    again = _Dispatcher()
    outcome = await _outcome(
        resume(_workflow(engine_class, again), resume_handle=_WORKFLOW_ID, config=harness.config)
    )
    assert again.steps == []
    _assert_refused(outcome, "claim-refused")


async def _admitted_failure(h: Harness, seen: _Observed, engine_class: EngineClass) -> None:
    """Resume an admitted record whose body must fail; check §4b's shared literals."""
    resumed = _Dispatcher()
    result = await resume(
        _workflow(engine_class, resumed), resume_handle=_WORKFLOW_ID, config=h.config
    )
    again = await _outcome(
        resume(_workflow(engine_class, _Dispatcher()), resume_handle=_WORKFLOW_ID, config=h.config)
    )
    assert (result.status, resumed.steps) == ("failed", [])
    _assert_refused(again, "claim-refused")


@pytest.mark.asyncio
@_ENGINES
async def test_a_corrupt_engine_record_fails_its_one_attempt_and_consumes_the_claim(
    harness: Harness, seen: _Observed, engine_class: EngineClass, literal: str
) -> None:
    _ = literal
    run_id = await _paused_at_step_1(harness, seen, engine_class)
    for record in _engine_records(harness):
        record.write_bytes(b"\x00not an engine record\n")

    await _admitted_failure(harness, seen, engine_class)

    assert (seen.run_ids, seen.fail_classes[-1]) == (
        [run_id] * 2,
        CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION,
    )
    assert seen.outcomes == [ResumeOutcomeKind.ABORT_SNAPSHOT_CORRUPTED]
    assert seen.resume_attempts() == 1


@pytest.mark.asyncio
@_ENGINES
async def test_a_lost_f2_prefix_fails_closed_before_any_attempt(
    harness: Harness, seen: _Observed, engine_class: EngineClass, literal: str
) -> None:
    _ = literal
    run_id = await _paused_at_step_1(harness, seen, engine_class)
    seen.ledger_path().write_bytes(b"")

    await _admitted_failure(harness, seen, engine_class)

    assert (seen.run_ids, seen.fail_classes[-1]) == (
        [run_id] * 2,
        "RT-FAIL-RESUME-ENGINE-PREFIX-SKEW",
    )
    assert seen.outcomes == []
    assert seen.resume_attempts() == 0


@pytest.mark.asyncio
async def test_a_later_engine_locator_outranks_an_earlier_snapshot(
    harness: Harness, seen: _Observed
) -> None:
    await harness.capture_root(run_id="run-snapshot")
    run_id = await _paused_at_step_1(harness, seen, EngineClass.WAL_SEGMENT)

    resumed = _Dispatcher()
    result = await resume(
        _workflow(EngineClass.WAL_SEGMENT, resumed),
        resume_handle=_WORKFLOW_ID,
        config=harness.config,
    )

    assert (result.status, seen.run_ids, resumed.steps) == ("completed", [run_id] * 2, ["step-1"])
    assert seen.outcomes == [ResumeOutcomeKind.RESUME_CLEAN]


@pytest.mark.asyncio
async def test_a_later_snapshot_outranks_an_earlier_engine_locator(
    harness: Harness, seen: _Observed
) -> None:
    await _paused_at_step_1(harness, seen, EngineClass.WAL_SEGMENT)
    await harness.capture_root(run_id="run-snapshot")

    resumed = _Dispatcher()
    result = await resume(
        _workflow(EngineClass.WAL_SEGMENT, resumed),
        resume_handle=_WORKFLOW_ID,
        config=harness.config,
    )
    again = await _outcome(
        resume(
            _workflow(EngineClass.WAL_SEGMENT, _Dispatcher()),
            resume_handle=_WORKFLOW_ID,
            config=harness.config,
        )
    )

    assert (result.status, seen.run_ids[-1]) == ("completed", "run-snapshot")
    assert seen.outcomes == []
    _assert_refused(again, "claim-refused")

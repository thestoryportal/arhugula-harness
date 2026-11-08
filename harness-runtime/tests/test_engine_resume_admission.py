"""B-314 fork §3-§4a, §6 — engine-pause locator admission refuses before anything runs.

Each case journals a locator through the real store and resumes through `api.resume`.
Every refusal also checks the §6 literals for an admission-stage (exit 6) refusal: the CP
driver is never entered (so no `attempt_resume` fire, no `cp.resume-attempted` entry and
no new `run_id`), no step is dispatched, and no journal or claim record is written.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from harness_cp import workflow_driver
from harness_cp.engine_class import EngineClass
from harness_runtime.api import resume
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    EnginePauseLocator,
    PauseJournalReadCause,
)
from harness_runtime.resume_refusal import (
    REFUSAL_ERRORS,
    HandleRefusal,
    RefusalKind,
    ResumeRefusal,
    project,
)

from .test_b104_root_resume_facade import (
    _WORKFLOW_ID,  # pyright: ignore[reportPrivateUsage]
    Harness,
    _Dispatcher,  # pyright: ignore[reportPrivateUsage]
    _durable_filesystem,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _Workflow,  # pyright: ignore[reportPrivateUsage]
)
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)


@pytest.fixture
def harness(world: Path) -> Harness:  # noqa: F811
    return Harness(world)


def _locator(engine_class: EngineClass, *, step_index: int = 0) -> dict[str, object]:
    return {
        "kind": "engine-pause-locator",
        **EnginePauseLocator(
            workflow_id=_WORKFLOW_ID,
            run_id="run-root",
            engine_class=engine_class,  # pyright: ignore[reportArgumentType]
            step_index=step_index,
        ).model_dump(mode="json"),
        "depth": 0,
    }


def _workflow(engine_class: EngineClass) -> _Workflow:
    workflow = _Workflow(_Dispatcher())
    workflow.manifest_entry = workflow.manifest_entry.model_copy(
        update={"engine_class": engine_class}
    )
    return workflow


def _journal(h: Harness, *records: dict[str, object]) -> None:
    h.site.stamp(h.config)
    for record in records:
        h.journal()._append(_WORKFLOW_ID, record)  # pyright: ignore[reportPrivateUsage]


def _superseded(h: Harness) -> None:
    _journal(h, _locator(EngineClass.WAL_SEGMENT))
    h.journal().supersede(_WORKFLOW_ID, "run-fresh")


_CASES: dict[str, tuple[Callable[[Harness], None], EngineClass, RefusalKind]] = {
    "engine record removed": (
        lambda h: _journal(h, _locator(EngineClass.WAL_SEGMENT)),
        EngineClass.WAL_SEGMENT,
        RefusalKind.ENGINE_PAUSE_RECORD_ABSENT,
    ),
    "engine class changed to non-engine": (
        lambda h: _journal(h, _locator(EngineClass.RECONCILER_LOOP)),
        EngineClass.PURE_PATTERN_NO_ENGINE,
        RefusalKind.ENGINE_CLASS_MISMATCH,
    ),
    "engine class changed between engines": (
        lambda h: _journal(h, _locator(EngineClass.WAL_SEGMENT)),
        EngineClass.RECONCILER_LOOP,
        RefusalKind.ENGINE_CLASS_MISMATCH,
    ),
    "child depth": (
        lambda h: _journal(h, {**_locator(EngineClass.WAL_SEGMENT), "depth": 1}),
        EngineClass.WAL_SEGMENT,
        RefusalKind.DEPTH,
    ),
    "step out of range": (
        lambda h: _journal(h, _locator(EngineClass.WAL_SEGMENT, step_index=5)),
        EngineClass.WAL_SEGMENT,
        RefusalKind.STEP_INDEX_OUT_OF_RANGE,
    ),
    "superseded": (_superseded, EngineClass.WAL_SEGMENT, RefusalKind.PAUSE_RECORD_SUPERSEDED),
}


async def _refused(
    h: Harness, monkeypatch: pytest.MonkeyPatch, workflow: _Workflow
) -> ResumeRefusal:
    """Resume, require a typed refusal, and check §6's admission-stage literals."""
    entered: list[str] = []

    def never(*_args: Any, **_kwargs: Any) -> Any:
        entered.append("execute_workflow")

    monkeypatch.setattr(workflow_driver, "execute_workflow", never)
    before = h.journal().read_latest_attributed(_WORKFLOW_ID)

    with pytest.raises(REFUSAL_ERRORS) as raised:
        await resume(workflow, resume_handle=_WORKFLOW_ID, config=h.config)

    after = h.journal().read_latest_attributed(_WORKFLOW_ID)
    assert entered == []
    assert workflow.step_dispatchers.lookup(None).steps == []
    assert (after.record_count, after.latest_record_digest) == (
        before.record_count,
        before.latest_record_digest,
    )
    assert h.claim_files() == []
    return project(raised.value)  # pyright: ignore[reportArgumentType]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", list(_CASES))
async def test_an_engine_locator_refusal_runs_nothing_and_writes_nothing(
    harness: Harness, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    arrange, workflow_engine, kind = _CASES[case]
    arrange(harness)

    refusal = await _refused(harness, monkeypatch, _workflow(workflow_engine))

    assert refusal.kind is kind


@pytest.mark.asyncio
async def test_a_corrupt_locator_line_is_the_existing_corrupt_handle_cause(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    _journal(harness, {**_locator(EngineClass.WAL_SEGMENT), "step_index": "two"})

    refusal = await _refused(harness, monkeypatch, _workflow(EngineClass.WAL_SEGMENT))

    assert isinstance(refusal, HandleRefusal)
    assert refusal.cause.value == PauseJournalReadCause.CORRUPT_LATEST.value


@pytest.mark.asyncio
async def test_a_locator_naming_another_workflow_is_the_mismatch_handle_cause(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    _journal(harness, {**_locator(EngineClass.WAL_SEGMENT), "workflow_id": "wf-other"})

    refusal = await _refused(harness, monkeypatch, _workflow(EngineClass.WAL_SEGMENT))

    assert isinstance(refusal, HandleRefusal)
    assert refusal.cause.value == PauseJournalReadCause.WORKFLOW_MISMATCH.value

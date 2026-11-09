"""B-314 fork §5 — the §14.14.9 pause-state accessor projects an engine-pause locator.

The latest journal record's kind decides the projection: a locator reads as the
`engine` pause layer with only its identity fields, a snapshot as the `workflow`
layer. The workflow-match guard, the staleness token and the required OD read event
behave as for a snapshot.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_cp.engine_class import EngineClass
from harness_cp.pause_state_projection import (
    AccessorDerivedResumeContext,
    EnginePausedState,
    PausedWorkflowState,
)
from harness_runtime.api import PausedWorkflowStateUnavailableError, read_paused_workflow_state
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    EnginePauseLocator,
    PauseJournalReadCause,
)
from harness_runtime.lifecycle.pause_state_staleness import mint_staleness_token

from .test_paused_workflow_state_accessor_b69 import (
    _WORKFLOW_ID,
    _capture,
    _config,
    _sink_rows,
    _store,
    _Workflow,
)

_ENGINE_CLASSES = (EngineClass.WAL_SEGMENT, EngineClass.RECONCILER_LOOP)


def _append_locator(tmp_path: Path, engine_class: EngineClass, *, step_index: int = 2) -> None:
    _store(tmp_path).capture_locator(
        EnginePauseLocator(
            workflow_id=_WORKFLOW_ID,
            run_id="run-engine",
            engine_class=engine_class,  # pyright: ignore[reportArgumentType]
            step_index=step_index,
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("engine_class", _ENGINE_CLASSES)
async def test_a_locator_projects_the_engine_layer_and_only_its_identity(
    tmp_path: Path, engine_class: EngineClass
) -> None:
    await _capture(tmp_path, run_id="run-earlier")
    _append_locator(tmp_path, engine_class)

    state = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path)
    )

    token = mint_staleness_token(_store(tmp_path).read_latest_attributed(_WORKFLOW_ID))
    assert token is not None
    assert state == EnginePausedState(
        workflow_id=_WORKFLOW_ID,
        run_id="run-engine",
        step_index=2,
        engine_class=engine_class,  # pyright: ignore[reportArgumentType]
        staleness_token=token,
    )
    # No store path, digest or locator hash is projected (fork §5).
    assert state.model_dump(mode="json") == {
        "pause_layer": "engine",
        "workflow_id": _WORKFLOW_ID,
        "run_id": "run-engine",
        "step_index": 2,
        "depth": 0,
        "engine_class": engine_class.value,
        "staleness_token": token,
    }


@pytest.mark.asyncio
async def test_a_snapshot_after_a_locator_projects_the_workflow_layer(tmp_path: Path) -> None:
    _append_locator(tmp_path, EngineClass.WAL_SEGMENT)
    await _capture(tmp_path, run_id="run-later")

    state = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path)
    )

    assert isinstance(state, PausedWorkflowState)
    assert state.pause_layer == "workflow"


@pytest.mark.asyncio
async def test_an_engine_read_emits_the_required_succeeded_event_with_no_locations(
    tmp_path: Path,
) -> None:
    _append_locator(tmp_path, EngineClass.RECONCILER_LOOP)

    state = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path)
    )

    (row,) = _sink_rows(tmp_path)
    assert row.succeeded is True
    assert row.staleness_token == state.staleness_token
    assert row.cause_attribution is None
    assert (
        row.hitl_addressable_count,
        row.effect_fence_addressable_count,
        row.uniform_fallback_only_count,
        row.transitively_paused_count,
    ) == (0, 0, 0, 0)


@pytest.mark.asyncio
async def test_a_locator_naming_another_workflow_is_workflow_mismatch(tmp_path: Path) -> None:
    _append_locator(tmp_path, EngineClass.WAL_SEGMENT)

    class _Other(_Workflow):
        workflow_id = "wf-other"

    with pytest.raises(PausedWorkflowStateUnavailableError) as raised:
        await read_paused_workflow_state(
            _Other(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path)
        )

    assert raised.value.cause is PauseJournalReadCause.WORKFLOW_MISMATCH
    (row,) = _sink_rows(tmp_path)
    assert row.succeeded is False
    assert row.staleness_token is None


@pytest.mark.asyncio
async def test_successive_engine_reads_mint_distinct_tokens_and_fence_a_resume_context(
    tmp_path: Path,
) -> None:
    _append_locator(tmp_path, EngineClass.WAL_SEGMENT, step_index=1)
    first = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path)
    )
    _append_locator(tmp_path, EngineClass.WAL_SEGMENT, step_index=1)
    second = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path)
    )

    assert first.staleness_token != second.staleness_token
    context = AccessorDerivedResumeContext.from_pause_state(second)
    assert context.staleness_token == second.staleness_token
    # The variant survives a round trip through the carrier's own validation.
    assert AccessorDerivedResumeContext.model_validate(context.model_dump()) == context

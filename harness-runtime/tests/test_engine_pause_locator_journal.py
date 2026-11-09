"""B-314 T05: the engine-pause locator record kind in the workflow-layer pause journal."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    EnginePauseLocator,
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
)
from pydantic import ValidationError

_WORKFLOW_ID = "wf-engine"


def _store(tmp_path: Path) -> JournalWorkflowPauseStore:
    return JournalWorkflowPauseStore(journal_dir=tmp_path, tenant_id=None)


def _locator(engine_class: EngineClass = EngineClass.WAL_SEGMENT) -> EnginePauseLocator:
    return EnginePauseLocator(
        workflow_id=_WORKFLOW_ID, run_id="run-original", engine_class=engine_class, step_index=1
    )


def _snapshot() -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=_WORKFLOW_ID,
        run_id="run-snapshot",
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
    )


def _journal_lines(store: JournalWorkflowPauseStore) -> list[dict[str, object]]:
    path = store._journal_file(_WORKFLOW_ID)
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _append_raw(store: JournalWorkflowPauseStore, record: dict[str, object]) -> None:
    store._append(_WORKFLOW_ID, record)


@pytest.mark.parametrize(
    ("engine_class", "literal"),
    [(EngineClass.WAL_SEGMENT, "WAL-segment"), (EngineClass.RECONCILER_LOOP, "reconciler-loop")],
)
def test_locator_round_trips_its_literal_engine_class(
    tmp_path: Path, engine_class: EngineClass, literal: str
) -> None:
    store = _store(tmp_path)
    ref = store.capture_locator(_locator(engine_class))

    (line,) = _journal_lines(store)
    assert line == {
        "kind": "engine-pause-locator",
        "workflow_id": _WORKFLOW_ID,
        "run_id": "run-original",
        "engine_class": literal,
        "step_index": 1,
        "depth": 0,
    }
    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.cause is None
    assert read.snapshot is None
    assert read.locator == _locator(engine_class)
    assert read.locator is not None and read.locator.engine_class is engine_class
    assert read.depth == 0
    assert (read.record_count, read.latest_record_digest) == (1, ref.latest_digest)
    assert ref.run_id == "run-original"
    assert ref.snapshot_hash == _locator(engine_class).locator_hash


def test_exact_locator_read_is_bound_to_its_ref(tmp_path: Path) -> None:
    store = _store(tmp_path)
    ref = store.capture_locator(_locator())

    at_ref = store.read_exact_locator(ref)
    assert at_ref is not None
    assert (at_ref.locator, at_ref.depth) == (_locator(), 0)
    # A locator is never returned as a snapshot, and a wrong hash fails closed.
    assert store.read_exact(ref) is None
    assert store.read_exact_locator(ref.model_copy(update={"snapshot_hash": "f" * 64})) is None


def test_snapshot_ref_is_never_read_as_a_locator(tmp_path: Path) -> None:
    store = _store(tmp_path)
    ref = store.capture(_snapshot(), depth=0)

    assert store.read_exact_locator(ref) is None
    assert store.read_exact(ref) is not None


def test_latest_record_alone_decides_the_kind(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.capture(_snapshot(), depth=0)
    store.capture_locator(_locator())
    later_locator = store.read_latest_attributed(_WORKFLOW_ID)
    assert (later_locator.snapshot, later_locator.locator) == (None, _locator())

    store.capture(_snapshot(), depth=0)
    later_snapshot = store.read_latest_attributed(_WORKFLOW_ID)
    assert (later_snapshot.snapshot, later_snapshot.locator) == (_snapshot(), None)


@pytest.mark.parametrize(
    "mutation",
    [
        {"engine_class": "pure-pattern-no-engine"},
        {"engine_class": "wal-segment"},
        {"step_index": -1},
        {"step_index": "1"},
        {"run_id": 7},
        {"depth": -1},
        {"extra": "field"},
    ],
)
def test_malformed_locator_line_is_corrupt_latest(
    tmp_path: Path, mutation: dict[str, object]
) -> None:
    store = _store(tmp_path)
    store.capture(_snapshot(), depth=0)
    _append_raw(
        store,
        {"kind": "engine-pause-locator", **_locator().model_dump(mode="json"), "depth": 0}
        | mutation,
    )

    read = store.read_latest_attributed(_WORKFLOW_ID)
    # Fail closed on the latest line: the earlier snapshot is never resumed instead.
    assert (read.snapshot, read.locator) == (None, None)
    assert read.cause is PauseJournalReadCause.CORRUPT_LATEST


def test_locator_naming_another_workflow_is_workflow_mismatch(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _append_raw(
        store,
        {
            "kind": "engine-pause-locator",
            **_locator().model_dump(mode="json"),
            "workflow_id": "wf-other",
            "depth": 0,
        },
    )

    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert (read.snapshot, read.locator) == (None, None)
    assert read.cause is PauseJournalReadCause.WORKFLOW_MISMATCH


def test_child_depth_locator_reads_with_its_recorded_depth(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _append_raw(
        store, {"kind": "engine-pause-locator", **_locator().model_dump(mode="json"), "depth": 1}
    )

    read = store.read_latest_attributed(_WORKFLOW_ID)
    # Root authority is decided by admission on depth; the read only reports it.
    assert (read.locator, read.depth, read.cause) == (_locator(), 1, None)


def test_snapshot_only_read_never_returns_a_locator(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.capture_locator(_locator())

    assert store.read_latest(_WORKFLOW_ID) is None


def test_locator_model_admits_only_engine_native_classes() -> None:
    with pytest.raises(ValidationError):
        EnginePauseLocator(
            workflow_id=_WORKFLOW_ID,
            run_id="run-original",
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,  # type: ignore[arg-type]
            step_index=0,
        )
    with pytest.raises(ValidationError):
        EnginePauseLocator(
            workflow_id=_WORKFLOW_ID,
            run_id="run-original",
            engine_class=EngineClass.WAL_SEGMENT,
            step_index=-1,
        )

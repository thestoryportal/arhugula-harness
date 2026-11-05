"""U-RT-160 portion 160a — the journal supersession record and its readers.

Runtime spec v1.137 Rules A1-A4: a supersession record is a second record kind in the same
per-(tenant, workflow_id) journal, appended through the one writer path; every reader treats it
as the latest durable fact, so a superseded pause is never resumed or projected again.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from harness_core import JournalRecordRef
from harness_od.pause_resume_namespace import PauseStateCauseAttribution, PauseStateEventKind
from harness_runtime import bootstrap as bootstrap_module
from harness_runtime.api import (
    PausedWorkflowStateUnavailableError,
    ResumePauseRecordSupersededError,
    read_paused_workflow_state,
    resume,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
)
from harness_runtime.lifecycle.pre_bootstrap_pause_state_sink import pause_state_sink_for

from .test_b104_root_resume_facade import _WORKFLOW_ID as _ROOT_WORKFLOW_ID
from .test_b104_root_resume_facade import (  # noqa: F401  (fixtures: harness, ext4 placement)
    Harness,
    _Dispatcher,
    _durable_filesystem,
    _outcome,
    harness,
)
from .test_b104_root_resume_facade import _Workflow as _RootWorkflow
from .test_paused_workflow_state_accessor_b69 import _WORKFLOW_ID as _ACCESSOR_WORKFLOW_ID
from .test_paused_workflow_state_accessor_b69 import _WORKLOAD, _capture, _config, _store
from .test_paused_workflow_state_accessor_b69 import _Workflow as _AccessorWorkflow
from .test_state_placement import world  # noqa: F401  (fixture used by `harness`)

_WORKFLOW_ID = "wf-rt-160a"


def _journal(tmp_path: Path) -> JournalWorkflowPauseStore:
    return JournalWorkflowPauseStore(journal_dir=tmp_path / "journal", tenant_id=None)


def _write_latest(store: JournalWorkflowPauseStore, record: dict[str, object]) -> None:
    """Append a raw line, standing in for a record no writer of this store produces."""
    path = store._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


async def _captured(tmp_path: Path) -> tuple[JournalWorkflowPauseStore, JournalRecordRef]:
    """A genuine journaled pause (the b69 capture path), plus its exact record identity."""
    snapshot = await _capture(tmp_path, run_id="run-paused")
    store = _store(tmp_path)
    ref = store.capture(snapshot, depth=0)
    return store, ref


# --- store: Rules A1-A3 -------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_supersession_record_is_the_latest_fact_and_changes_the_journal_identity(
    tmp_path: Path,
) -> None:
    store, _ = await _captured(tmp_path)
    before = store.read_latest_attributed(_ACCESSOR_WORKFLOW_ID)
    assert before.snapshot is not None

    store.supersede(_ACCESSOR_WORKFLOW_ID, "run-fresh")
    after = store.read_latest_attributed(_ACCESSOR_WORKFLOW_ID)

    assert after.snapshot is None
    assert after.cause is PauseJournalReadCause.SUPERSEDED
    assert (after.retryable, after.indeterminate) == (False, False)
    assert after.record_count == before.record_count + 1
    assert after.latest_record_digest != before.latest_record_digest
    assert store.read_latest(_ACCESSOR_WORKFLOW_ID) is None


@pytest.mark.asyncio
async def test_read_exact_refuses_a_supersession_position(tmp_path: Path) -> None:
    store, ref = await _captured(tmp_path)
    store.supersede(_ACCESSOR_WORKFLOW_ID, "run-fresh")
    path = store._journal_file(_ACCESSOR_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]
    lines = path.read_bytes().splitlines()
    at_supersession = ref.model_copy(
        update={
            "record_count": len(lines),
            "latest_digest": hashlib.sha256(lines[-1]).hexdigest(),
        }
    )

    assert store.read_exact(at_supersession) is None


def test_the_supersession_record_is_exactly_kind_workflow_id_run_id(tmp_path: Path) -> None:
    store = _journal(tmp_path)
    store.supersede(_WORKFLOW_ID, "run-fresh")
    path = store._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]

    assert [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] == [
        {"kind": "supersession", "workflow_id": _WORKFLOW_ID, "run_id": "run-fresh"}
    ]


@pytest.mark.asyncio
async def test_a_snapshot_line_without_kind_still_reads_as_a_snapshot(tmp_path: Path) -> None:
    store, ref = await _captured(tmp_path)
    path = store._journal_file(_ACCESSOR_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]

    assert all("kind" not in json.loads(line) for line in path.read_text().splitlines())
    read = store.read_latest_attributed(_ACCESSOR_WORKFLOW_ID)
    assert read.cause is None and read.snapshot is not None
    assert read.snapshot.run_id == ref.run_id


@pytest.mark.parametrize(
    "record",
    [
        {"kind": "resolution", "workflow_id": _WORKFLOW_ID, "run_id": "run-fresh"},
        {"kind": "supersession", "workflow_id": _WORKFLOW_ID},
        {"kind": "supersession", "workflow_id": _WORKFLOW_ID, "run_id": "r", "depth": 0},
        {"kind": "supersession", "workflow_id": _WORKFLOW_ID, "run_id": 7},
        {"kind": "supersession", "workflow_id": None, "run_id": "run-fresh"},
    ],
    ids=["unknown-kind", "missing-field", "extra-field", "non-string-run", "non-string-workflow"],
)
def test_any_other_kind_or_field_set_is_corrupt_latest(
    tmp_path: Path, record: dict[str, object]
) -> None:
    store = _journal(tmp_path)
    _write_latest(store, record)

    read = store.read_latest_attributed(_WORKFLOW_ID)

    assert (read.snapshot, read.cause) == (None, PauseJournalReadCause.CORRUPT_LATEST)


def test_a_supersession_record_for_another_workflow_is_a_workflow_mismatch(
    tmp_path: Path,
) -> None:
    store = _journal(tmp_path)
    _write_latest(store, {"kind": "supersession", "workflow_id": "wf-other", "run_id": "r"})

    read = store.read_latest_attributed(_WORKFLOW_ID)

    assert (read.snapshot, read.cause) == (None, PauseJournalReadCause.WORKFLOW_MISMATCH)


# --- resume(): its own pre-bootstrap refusal (Rule A3, §D.5) ------------------------------------


@pytest.mark.asyncio
async def test_resume_of_a_superseded_handle_refuses_before_bootstrap_and_claims_nothing(
    harness: Harness,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await harness.capture_root()
    harness.journal().supersede(_ROOT_WORKFLOW_ID, "run-fresh")
    bootstraps: list[object] = []

    async def no_bootstrap(*args: Any, **kwargs: Any) -> Any:
        bootstraps.append((args, kwargs))
        raise AssertionError("resume bootstrapped a superseded handle")

    monkeypatch.setattr(bootstrap_module, "run_bootstrap", no_bootstrap)
    dispatcher = _Dispatcher()

    outcome = await _outcome(
        resume(_RootWorkflow(dispatcher), resume_handle=_ROOT_WORKFLOW_ID, config=harness.config)
    )

    assert type(outcome) is ResumePauseRecordSupersededError, outcome
    assert "/" not in str(outcome)  # names no filesystem path
    assert dispatcher.steps == [] and bootstraps == []
    assert harness.claim_files() == []


# --- read_paused_workflow_state(): Rule A4 ------------------------------------------------------


_FRESH_PROCESS_READ = """
import sys
from pathlib import Path
from harness_runtime.lifecycle.pre_bootstrap_pause_state_sink import PreBootstrapPauseStateSink
for row in PreBootstrapPauseStateSink(sink_dir=Path(sys.argv[1])).read_all():
    print(row.model_dump_json())
"""


def _rows_read_in_a_fresh_process(sink_dir: Path) -> list[dict[str, Any]]:
    fresh = subprocess.run(
        [sys.executable, "-c", _FRESH_PROCESS_READ, str(sink_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    return [json.loads(line) for line in fresh.stdout.splitlines()]


@pytest.mark.asyncio
async def test_the_accessor_refuses_a_superseded_record_and_audits_the_failed_read(
    tmp_path: Path,
) -> None:
    store, _ = await _captured(tmp_path)
    store.supersede(_ACCESSOR_WORKFLOW_ID, "run-fresh")
    sink = pause_state_sink_for(_config(tmp_path), _WORKLOAD)
    rows_before = len(sink.read_all())

    with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
        await read_paused_workflow_state(
            _AccessorWorkflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_ACCESSOR_WORKFLOW_ID,
            config=_config(tmp_path),
        )

    assert excinfo.value.cause is PauseJournalReadCause.SUPERSEDED
    assert (excinfo.value.retryable, excinfo.value.indeterminate) == (False, False)
    rows = (await asyncio.to_thread(_rows_read_in_a_fresh_process, sink.path.parent))[rows_before:]
    assert rows == [
        {
            **rows[0],
            "event_kind": PauseStateEventKind.ACCESSOR_READ.value,
            "workflow_id": _ACCESSOR_WORKFLOW_ID,
            "succeeded": False,
            "staleness_token": None,
            "cause_attribution": PauseStateCauseAttribution.SUPERSEDED.value,
            "hitl_addressable_count": None,
            "effect_fence_addressable_count": None,
            "uniform_fallback_only_count": None,
            "transitively_paused_count": None,
        }
    ]


def test_the_runtime_and_od_cause_vocabularies_are_identical_at_six() -> None:
    runtime = [(member.name, member.value) for member in PauseJournalReadCause]
    od = [(member.name, member.value) for member in PauseStateCauseAttribution]

    assert runtime == od
    assert len(runtime) == 6

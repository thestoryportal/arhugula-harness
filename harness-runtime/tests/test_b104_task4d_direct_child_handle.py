"""B-104 Task 4d: a direct `resume(resume_handle=...)` never resumes a child journal record.

Real `JournalWorkflowPauseStore` records at ancestry depth 0/1/2, a legacy line with no depth,
malformed depths and same-workflow siblings. `run_bootstrap` is replaced by a sentinel so the
tests observe exactly how far `resume` got: a refused handle must stop BEFORE bootstrap (and
so before any claim, model/tool/body invocation or other side effect); a depth-0 root record
continues into the existing path (Task 5 still owns the claim/started barrier for that path).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from harness_cp.pause_resume_protocol_types import PauseSnapshot
from harness_runtime import api as api_module
from harness_runtime.api import read_paused_workflow_state, resume
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
)

from .test_pause_journal_surface_parity_b97a import (
    _WORKFLOW_ID,  # pyright: ignore[reportPrivateUsage]
    _config,  # pyright: ignore[reportPrivateUsage]
    _journal_dir,  # pyright: ignore[reportPrivateUsage]
    _snapshot,  # pyright: ignore[reportPrivateUsage]
    _Workflow,  # pyright: ignore[reportPrivateUsage]
)


class _BootstrapReached(Exception):
    """Raised by the bootstrap sentinel: `resume` got past every pre-bootstrap refusal."""


@dataclass
class _Outcome:
    kind: str  # "bootstrap" | "refused" | "other"
    error: BaseException | None = None


@pytest.fixture(autouse=True)
def _bootstrap_sentinel(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []

    async def _sentinel(*_a: Any, **_k: Any) -> Any:
        calls.append(1)
        raise _BootstrapReached

    monkeypatch.setattr("harness_runtime.bootstrap.run_bootstrap", _sentinel)
    return calls


def _store(tmp_path: Path) -> JournalWorkflowPauseStore:
    return JournalWorkflowPauseStore(journal_dir=_journal_dir(tmp_path), tenant_id=None)


def _journal_file(tmp_path: Path) -> Path:
    return _store(tmp_path)._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]


def _rewrite_latest_line(tmp_path: Path, edit: Any) -> None:
    """Edit ONLY the newest journal line's JSON record (simulating legacy/corrupt depth)."""
    path = _journal_file(tmp_path)
    *head, last = path.read_text().splitlines()
    record = json.loads(last)
    edit(record)
    path.write_text("\n".join([*head, json.dumps(record, sort_keys=True)]) + "\n")


async def _direct_handle_resume(tmp_path: Path) -> _Outcome:
    refused = getattr(api_module, "ResumeDirectChildHandleError", None)
    try:
        await resume(
            _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path, tenant_id=None)
        )
    except _BootstrapReached:
        return _Outcome("bootstrap")
    except Exception as exc:
        return _Outcome("refused" if refused and isinstance(exc, refused) else "other", exc)
    return _Outcome("other")


# --- the guard: depth is read from the same latest record ----------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("depth", [1, 2])
async def test_a_child_or_grandchild_record_is_refused_before_bootstrap(
    tmp_path: Path, _bootstrap_sentinel: list[int], depth: int
) -> None:
    _store(tmp_path).capture(_snapshot("run-child"), depth=depth)
    before = _journal_file(tmp_path).read_bytes()

    outcome = await _direct_handle_resume(tmp_path)

    assert outcome.kind == "refused", outcome
    assert _bootstrap_sentinel == []  # no bootstrap => no claim, model, tool or body effect
    assert getattr(outcome.error, "depth", "absent") == depth
    assert _journal_file(tmp_path).read_bytes() == before


@pytest.mark.asyncio
async def test_a_root_record_continues_into_the_existing_path(
    tmp_path: Path, _bootstrap_sentinel: list[int]
) -> None:
    """Pre-Task-5 contract: depth 0 is not refused here; Task 5 must still gate it."""
    _store(tmp_path).capture(_snapshot("run-root"), depth=0)

    outcome = await _direct_handle_resume(tmp_path)

    assert outcome.kind == "bootstrap", outcome
    assert _bootstrap_sentinel == [1]


@pytest.mark.asyncio
async def test_a_legacy_record_with_no_depth_is_refused_not_inferred_as_root(
    tmp_path: Path, _bootstrap_sentinel: list[int]
) -> None:
    _store(tmp_path).capture(_snapshot("run-legacy"), depth=None)

    outcome = await _direct_handle_resume(tmp_path)

    assert outcome.kind == "refused", outcome
    assert getattr(outcome.error, "depth", "absent") is None
    assert _bootstrap_sentinel == []


@pytest.mark.asyncio
async def test_a_line_with_the_depth_key_missing_entirely_is_refused(
    tmp_path: Path, _bootstrap_sentinel: list[int]
) -> None:
    _store(tmp_path).capture(_snapshot("run-old"), depth=0)
    _rewrite_latest_line(tmp_path, lambda record: record.pop("depth"))

    outcome = await _direct_handle_resume(tmp_path)

    assert outcome.kind == "refused", outcome
    assert _bootstrap_sentinel == []


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_depth", ["0", -1, 1.5, True, [0], {"d": 0}], ids=repr)
async def test_a_malformed_depth_is_refused(
    tmp_path: Path, _bootstrap_sentinel: list[int], bad_depth: object
) -> None:
    _store(tmp_path).capture(_snapshot("run-bad"), depth=0)
    _rewrite_latest_line(tmp_path, lambda record: record.__setitem__("depth", bad_depth))

    outcome = await _direct_handle_resume(tmp_path)

    assert outcome.kind == "refused", outcome
    assert _bootstrap_sentinel == []


@pytest.mark.asyncio
async def test_same_workflow_siblings_are_judged_by_the_latest_record_only(
    tmp_path: Path, _bootstrap_sentinel: list[int]
) -> None:
    """One journal file holds records of several runs of the same workflow id; the depth
    that decides admission is the depth of the very record the snapshot came from."""
    store = _store(tmp_path)
    store.capture(_snapshot("run-root"), depth=0)
    store.capture(_snapshot("run-child"), depth=1)  # latest is a child
    assert (await _direct_handle_resume(tmp_path)).kind == "refused"

    store.capture(_snapshot("run-root-2"), depth=0)  # latest is a root again
    assert (await _direct_handle_resume(tmp_path)).kind == "bootstrap"
    assert _bootstrap_sentinel == [1]


# --- what stays as it was ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_caller_supplied_snapshot_keeps_its_own_path(
    tmp_path: Path, _bootstrap_sentinel: list[int]
) -> None:
    _store(tmp_path).capture(_snapshot("run-child"), depth=2)
    snapshot: PauseSnapshot = _snapshot("run-supplied")

    with pytest.raises(_BootstrapReached):
        await resume(_Workflow(), pause_snapshot=snapshot, config=_config(tmp_path, tenant_id=None))

    assert _bootstrap_sentinel == [1]


@pytest.mark.asyncio
async def test_the_read_only_accessor_still_reports_a_child_record(tmp_path: Path) -> None:
    _store(tmp_path).capture(_snapshot("run-child"), depth=1)

    state = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path, tenant_id=None)
    )

    assert state.workflow_id == _WORKFLOW_ID


@pytest.mark.asyncio
async def test_the_refusal_names_no_filesystem_path(tmp_path: Path) -> None:
    _store(tmp_path).capture(_snapshot("run-child"), depth=1)

    outcome = await _direct_handle_resume(tmp_path)

    assert outcome.kind == "refused", outcome
    assert str(tmp_path) not in str(outcome.error)


# --- the depth rides the SAME read as the snapshot ----------------------------------------


def test_the_latest_read_carries_the_depth_of_its_own_line(tmp_path: Path) -> None:
    store = _store(tmp_path)
    for run, depth in (("run-0", 0), ("run-1", 1), ("run-2", 2)):
        store.capture(_snapshot(run), depth=depth)
        read = store.read_latest_attributed(_WORKFLOW_ID)
        assert read.snapshot is not None and read.snapshot.run_id == run
        assert getattr(read, "depth", "absent") == depth


@pytest.mark.parametrize("edit", ["missing", "x", -1, True, 1.5])
def test_an_unknown_depth_is_none_and_never_changes_the_read_attribution(
    tmp_path: Path, edit: object
) -> None:
    store = _store(tmp_path)
    store.capture(_snapshot("run-x"), depth=1)
    before = store.read_latest_attributed(_WORKFLOW_ID)
    _rewrite_latest_line(
        tmp_path,
        (lambda r: r.pop("depth")) if edit == "missing" else (lambda r: r.update(depth=edit)),
    )

    after = store.read_latest_attributed(_WORKFLOW_ID)

    assert getattr(after, "depth", "absent") is None
    assert after.snapshot == before.snapshot and after.cause is None
    assert (after.record_count, after.latest_record_digest) != (None, None)


def test_a_failed_read_carries_no_depth(tmp_path: Path) -> None:
    read = _store(tmp_path).read_latest_attributed(_WORKFLOW_ID)

    assert read.cause is PauseJournalReadCause.ABSENT
    assert getattr(read, "depth", "absent") is None

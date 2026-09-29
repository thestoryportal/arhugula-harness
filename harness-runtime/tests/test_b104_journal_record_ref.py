"""B-104 Task 3a: exact, shared pause-journal record identity."""

from __future__ import annotations

import hashlib
import inspect
import json
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest
from harness_core import JournalRecordRef
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.admin.pause_journal_enumeration import enumerate_pause_journals
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from pydantic import ValidationError


def _snapshot(run_id: str) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id="wf-identity",
        run_id=run_id,
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


def test_shared_ref_is_frozen_and_typed() -> None:
    ref = JournalRecordRef(
        tenant=None,
        workflow_id="wf-identity",
        run_id="run-1",
        record_count=1,
        latest_digest="a" * 64,
        snapshot_hash="0" * 64,
    )
    assert ref.__class__.__module__ == "harness_core.journal_record_ref"
    with pytest.raises(ValidationError):
        ref.record_count = 2
    with pytest.raises(ValidationError):
        JournalRecordRef(
            tenant=None,
            workflow_id="wf-identity",
            run_id="run-1",
            record_count=0,
            latest_digest="bad",
            snapshot_hash="0" * 64,
        )
    capture_depth = inspect.signature(JournalWorkflowPauseStore.capture).parameters["depth"]
    assert capture_depth.default is inspect.Parameter.empty
    assert capture_depth.kind is inspect.Parameter.KEYWORD_ONLY


def test_capture_returns_first_identity_before_sibling_append(tmp_path: Path) -> None:
    store = JournalWorkflowPauseStore(journal_dir=tmp_path, tenant_id=None)
    sibling = JournalWorkflowPauseStore(journal_dir=tmp_path, tenant_id=None)
    lock = store._cross_process_append_lock

    @contextmanager
    def append_sibling_after_unlock(path: Path) -> Generator[None, None, None]:
        with lock(path):
            yield
        sibling.capture(_snapshot("run-2"), depth=None)

    store._cross_process_append_lock = append_sibling_after_unlock  # type: ignore[method-assign]
    first = store.capture(_snapshot("run-1"), depth=None)
    assert first.run_id == "run-1"
    assert first.record_count == 1
    assert store.read_latest("wf-identity").run_id == "run-2"  # type: ignore[union-attr]


def test_raw_identity_agrees_with_inspect_on_odd_and_torn_bytes(tmp_path: Path) -> None:
    store = JournalWorkflowPauseStore(journal_dir=tmp_path, tenant_id=None)
    path = store._journal_file("wf-identity")
    path.write_bytes(b"odd\x0bline\n\xff\xfe torn")
    rows = enumerate_pause_journals(tmp_path, tenant_scope=None, scope_known=True)
    assert len(rows) == 1
    read = store.read_latest_attributed("wf-identity")
    assert read.record_count == rows[0].record_count
    assert read.latest_record_digest == rows[0].latest_record_digest


def test_legacy_unknown_depth_and_exact_position_survive_newer_append(tmp_path: Path) -> None:
    store = JournalWorkflowPauseStore(journal_dir=tmp_path, tenant_id=None)
    snapshot = _snapshot("run-legacy")
    raw = json.dumps(
        {"workflow_id": snapshot.workflow_id, "pause_snapshot": snapshot.model_dump(mode="json")},
        sort_keys=True,
    ).encode()
    path = store._journal_file(snapshot.workflow_id)
    path.write_bytes(raw + b"\n")
    ref = JournalRecordRef(
        tenant=None,
        workflow_id=snapshot.workflow_id,
        run_id=snapshot.run_id,
        record_count=1,
        latest_digest=hashlib.sha256(raw).hexdigest(),
        snapshot_hash=snapshot.snapshot_hash,
    )
    new_ref = store.capture(_snapshot("run-new"), depth=0)
    new_exact = store.read_exact(new_ref)
    assert new_exact is not None
    assert new_exact.depth == 0
    exact = store.read_exact(ref)
    assert exact is not None
    assert exact.snapshot.run_id == "run-legacy"
    assert exact.depth is None
    assert store.read_latest(snapshot.workflow_id).run_id == "run-new"  # type: ignore[union-attr]
    assert store.read_exact(ref.model_copy(update={"run_id": "wrong"})) is None
    assert store.read_exact(ref.model_copy(update={"latest_digest": "a" * 64})) is None
    assert store.read_exact(ref.model_copy(update={"snapshot_hash": "b" * 64})) is None

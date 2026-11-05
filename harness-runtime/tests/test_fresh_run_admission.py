"""U-RT-160a — a fresh root run supersedes the workflow's pause record at its admission point.

Runtime spec v1.137 Rules B1/B2 (C2 order, B6) and plan v2.68 U-RT-160 criterion 18 / witness
I.16. Every `run_workflow` invocation builds its own `FreshRunAdmission`, which takes the
(tenant, workflow_id) journal lock and, in that one locked step, appends a supersession record
when the journal exists and is non-empty, before the body's first step. Earlier and later are
journal positions under that lock, never start or wall-clock time.

The journal directory is still the capture derivation; the Rule B3/B7 root resolver is a later
slice, so I.16's root-resolution-failure caller (F1) is not witnessed here. Overlap is forced by
events and the real `flock`, never timed.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle import journal_workflow_pause_store as journal_module
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_LOCK_SUFFIX,
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
    cross_process_journal_lock,
    pause_journal_dir_for,
)
from harness_runtime.lifecycle.root_resume_admission import (
    FreshRunAdmission,
    FreshRunAdmissionError,
)
from mcp.types import CallToolResult, TextContent

from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
)
from .test_b104_root_resume_facade import (
    _WORKFLOW_ID,  # pyright: ignore[reportPrivateUsage]
    Harness,
    _Dispatcher,  # pyright: ignore[reportPrivateUsage]
    _durable_filesystem,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _Workflow,  # pyright: ignore[reportPrivateUsage]
)
from .test_daemon_mcp_resume import _daemon, _run_result  # pyright: ignore[reportPrivateUsage]
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="the journal lock is POSIX flock")

_W = "wf-fresh-admission"
_W2 = "wf-fresh-admission-2"


def _snapshot(workflow_id: str, run_id: str) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
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


def _ledger_dir(tmp_path: Path) -> Path:
    return tmp_path / "state-ledger"


def _store(tmp_path: Path) -> JournalWorkflowPauseStore:
    """The store over the journal directory a fresh run's admission derives (capture's)."""
    return JournalWorkflowPauseStore(
        journal_dir=pause_journal_dir_for(_ledger_dir(tmp_path)), tenant_id=None
    )


def _ctx(tmp_path: Path) -> Any:
    """The two facts the admission reads from a bootstrapped context: ledger dir and tenant."""
    state_jsonl = _ledger_dir(tmp_path) / "state.jsonl"
    return SimpleNamespace(
        ledger_writer=SimpleNamespace(handle=SimpleNamespace(canonical_path=state_jsonl)),
        config=SimpleNamespace(tenant_id=None),
    )


def _records(store: JournalWorkflowPauseStore, workflow_id: str) -> list[dict[str, Any]]:
    path = store._journal_file(workflow_id)  # pyright: ignore[reportPrivateUsage]
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _order(store: JournalWorkflowPauseStore, workflow_id: str) -> list[str]:
    """The journal order, one label per record: `snapshot:<run>` or `supersession:<run>`."""
    return [
        f"supersession:{record['run_id']}"
        if record.get("kind") == "supersession"
        else f"snapshot:{record['pause_snapshot']['run_id']}"
        for record in _records(store, workflow_id)
    ]


def _admit_in_another_process(tmp_path: Path, workflow_id: str, run_id: str) -> None:
    """Run one fresh run's real admission, with an empty body, in a separate OS process."""
    script = (
        "import sys\n"
        "from pathlib import Path\n"
        "from types import SimpleNamespace as N\n"
        "from harness_runtime.lifecycle.root_resume_admission import FreshRunAdmission\n"
        "ledger, workflow_id, run_id = sys.argv[1:4]\n"
        "ctx = N(ledger_writer=N(handle=N(canonical_path=Path(ledger) / 'state.jsonl')),\n"
        "        config=N(tenant_id=None))\n"
        "FreshRunAdmission(workflow_id=workflow_id, run_id=run_id).run(ctx, lambda _: None)\n"
    )
    subprocess.run(
        [sys.executable, "-c", script, str(_ledger_dir(tmp_path)), workflow_id, run_id],
        check=True,
        timeout=60,
    )


# --- Rule B2: what is written ---------------------------------------------------------------------


def test_a_fresh_run_with_no_journal_writes_no_line(tmp_path: Path) -> None:
    store = _store(tmp_path)
    journal = store._journal_file(_W)  # pyright: ignore[reportPrivateUsage]
    body: list[object] = []

    FreshRunAdmission(workflow_id=_W, run_id="run-fresh").run(_ctx(tmp_path), body.append)

    assert body == [None]
    assert not journal.exists()
    assert journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX).exists()


def test_a_fresh_run_over_an_empty_journal_writes_no_line(tmp_path: Path) -> None:
    store = _store(tmp_path)
    journal = store._journal_file(_W)  # pyright: ignore[reportPrivateUsage]
    journal.parent.mkdir(parents=True)
    journal.touch()

    FreshRunAdmission(workflow_id=_W, run_id="run-fresh").run(_ctx(tmp_path), lambda _: None)

    assert journal.read_bytes() == b""


def test_a_fresh_run_appends_its_own_run_id_before_its_body_runs(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.capture(_snapshot(_W, "run-paused"), depth=0)
    seen_by_body: list[list[str]] = []

    FreshRunAdmission(workflow_id=_W, run_id="run-fresh").run(
        _ctx(tmp_path), lambda _: seen_by_body.append(_order(store, _W))
    )

    assert seen_by_body == [["snapshot:run-paused", "supersession:run-fresh"]]
    assert store.read_latest_attributed(_W).cause is PauseJournalReadCause.SUPERSEDED


def test_a_failed_append_fails_the_run_before_its_body_and_records_its_own_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _store(tmp_path).capture(_snapshot(_W, "run-paused"), depth=0)

    def refuse(*args: Any, **kwargs: Any) -> Any:
        raise PermissionError(13, "denied")

    monkeypatch.setattr(JournalWorkflowPauseStore, "_append_locked", refuse)
    admission = FreshRunAdmission(workflow_id=_W, run_id="run-fresh")
    body: list[object] = []

    with pytest.raises(FreshRunAdmissionError) as raised:
        admission.run(_ctx(tmp_path), body.append)

    assert body == []
    assert raised.value is admission.failure
    assert isinstance(raised.value.__cause__, PermissionError)
    assert str(tmp_path) not in str(raised.value)


# --- I.16 / criterion 18: overlapping root runs are ordered by journal position (cross-process) --


def test_a_snapshot_captured_after_a_later_admission_stays_resumable(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.capture(_snapshot(_W, "run-old"), depth=0)

    def r1_body(_: object) -> None:
        # R2 is admitted (in another process) and completes inside R1's life; R1 then captures.
        _admit_in_another_process(tmp_path, _W, "run-r2")
        store.capture(_snapshot(_W, "run-r1"), depth=0)

    FreshRunAdmission(workflow_id=_W, run_id="run-r1").run(_ctx(tmp_path), r1_body)

    assert _order(store, _W) == [
        "snapshot:run-old",
        "supersession:run-r1",
        "supersession:run-r2",
        "snapshot:run-r1",
    ]
    latest = store.read_latest_attributed(_W)
    assert latest.snapshot is not None and latest.snapshot.run_id == "run-r1"


def test_a_snapshot_captured_before_a_later_admission_is_superseded(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.capture(_snapshot(_W, "run-old"), depth=0)

    FreshRunAdmission(workflow_id=_W, run_id="run-r1").run(
        _ctx(tmp_path), lambda _: store.capture(_snapshot(_W, "run-r1"), depth=0)
    )
    _admit_in_another_process(tmp_path, _W, "run-r2")

    assert _order(store, _W)[-2:] == ["snapshot:run-r1", "supersession:run-r2"]
    assert store.read_latest_attributed(_W).cause is PauseJournalReadCause.SUPERSEDED


# --- I.16 / criterion 18: lock scope — the existence check is made only under the lock ------------


@contextmanager
def _admission_waiting_on_the_held_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[threading.Event]:
    """Signal when a non-test thread starts waiting for a journal lock."""
    waiting = threading.Event()
    real = journal_module.flock_until_deadline
    test_thread = threading.current_thread()

    def observed(*args: Any, **kwargs: Any) -> Any:
        if threading.current_thread() is not test_thread:
            waiting.set()
        return real(*args, **kwargs)

    monkeypatch.setattr(journal_module, "flock_until_deadline", observed)
    yield waiting


def test_a_snapshot_written_while_an_admission_waits_on_the_lock_is_superseded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _store(tmp_path)
    journal = store._journal_file(_W)  # pyright: ignore[reportPrivateUsage]
    journal.parent.mkdir(parents=True)
    failures: list[BaseException] = []

    def admit() -> None:
        try:
            FreshRunAdmission(workflow_id=_W, run_id="run-fresh").run(
                _ctx(tmp_path), lambda _: None
            )
        except BaseException as exc:  # surfaced on the test thread below
            failures.append(exc)

    with _admission_waiting_on_the_held_lock(monkeypatch) as waiting:
        with cross_process_journal_lock(journal):
            admission = threading.Thread(target=admit)
            admission.start()
            assert waiting.wait(timeout=10), "the admission never reached the journal lock"
            # A capture's bytes, written by the lock holder: ordered before the admission's check.
            record = {
                "workflow_id": _W,
                "pause_snapshot": _snapshot(_W, "run-paused").model_dump(mode="json"),
                "depth": 0,
            }
            journal.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
        admission.join(timeout=30)

    assert not admission.is_alive() and failures == []
    assert _order(store, _W) == ["snapshot:run-paused", "supersession:run-fresh"]
    assert store.read_latest_attributed(_W).cause is PauseJournalReadCause.SUPERSEDED


# --- I.16 / criterion 18: per-invocation admission over concurrent daemon calls -------------------


def _error_text(reply: CallToolResult) -> str:
    assert reply.isError is True, reply
    match reply.content:
        case [TextContent(text=text)]:
            return text
        case _:
            raise AssertionError(f"not exactly one text error: {reply.content!r}")


@pytest.mark.asyncio
@pytest.mark.usefixtures("_patched_runtime")
async def test_concurrent_daemon_runs_each_keep_their_own_run_id_and_failure(
    world: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = Harness(world)
    await harness.capture_root()  # W's non-empty journal; read-only below, so F's append fails
    journal = harness.journal()
    journal.capture(_snapshot(_W2, "run-w2-paused"), depth=0)  # S's non-empty journal
    w_file = journal._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]
    w_bytes = w_file.read_bytes()
    w_file.chmod(0o444)
    with pytest.raises(PermissionError):  # the precondition: this host enforces the mode
        w_file.open("a").close()

    admissions: dict[str, FreshRunAdmission] = {}
    both_constructed = threading.Barrier(2, timeout=30)
    f_failed, s_projected = threading.Event(), threading.Event()
    real_run = FreshRunAdmission.run

    def forced(self: FreshRunAdmission, ctx: Any, body: Callable[[object], Any]) -> Any:
        admissions[self.workflow_id] = self
        both_constructed.wait()
        if self.workflow_id == _WORKFLOW_ID:  # F: fails first, projected only after S
            try:
                return real_run(self, ctx, body)
            finally:
                f_failed.set()
                assert s_projected.wait(timeout=30)
        assert f_failed.wait(timeout=30)  # S: admitted after F recorded its failure
        return real_run(self, ctx, body)

    monkeypatch.setattr(FreshRunAdmission, "run", forced)
    f_dispatcher, s_dispatcher = _Dispatcher(), _Dispatcher()

    async with _daemon(
        harness.config, _Workflow(f_dispatcher), _Workflow(s_dispatcher, _W2)
    ) as session:
        f_call = asyncio.create_task(
            session.call_tool("run_workflow", {"workflow_id": _WORKFLOW_ID})
        )
        s_reply = await session.call_tool("run_workflow", {"workflow_id": _W2})
        s_projected.set()
        f_reply = await f_call

    f, s = admissions[_WORKFLOW_ID], admissions[_W2]
    assert f is not s and f.run_id != s.run_id
    assert _run_result(s_reply)["status"] == "success"
    assert _run_result(s_reply)["run_id"] == s.run_id and s.failure is None
    assert _order(journal, _W2) == ["snapshot:run-w2-paused", f"supersession:{s.run_id}"]
    assert isinstance(f.failure, FreshRunAdmissionError)
    assert str(f.failure) in _error_text(f_reply)
    assert (f_dispatcher.steps, s_dispatcher.steps) == ([], ["step-0"])
    assert w_file.read_bytes() == w_bytes
    os.chmod(w_file, 0o644)

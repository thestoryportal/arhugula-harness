"""`B-97` half (b) — cross-process write serialization on the pause journal's `_append`.

The register's close_out (`.harness/forward-register.yaml`, `B-97`) names half (b) as
*"a genuine cross-process write serialization primitive on `_append` (O_EXCL, lockfile,
or advisory lock), which the current plain append open does not provide."* This module
witnesses that primitive. Half (a) — the tenant binding — is fork-shaped and NOT
touched here.

**What the lock actually buys, stated honestly** (an empirical probe run at this arc,
not an assumption). The shipped `_append` emits each record in exactly ONE `write()`
syscall — measured by rebuilding the `FileIO -> BufferedWriter -> TextIOWrapper` stack
`path.open("a", encoding="utf-8")` builds and counting raw writes: a 60 KB record, a
4 MB record, and the leading-newline self-heal path (whose 1-byte `"\\n"` is coalesced
into the same buffered flush rather than emitted separately) each produced a SINGLE
`write()`. Under `O_APPEND` on a local POSIX filesystem that write is atomic, so a
two-process data-tearing witness does NOT discriminate here: a 2x12 concurrent-append
run at 12 KB / 60 KB / 500 KB / 4 MB record sizes produced zero malformed records with
the lock REMOVED. Shipping a tearing assertion as *the* witness would therefore be a
false witness — it would pass either way.

What the lock genuinely delivers, and what the witnesses below assert instead:

1. **Mutual exclusion across OS processes** at all — asserted directly, by blocking a
   genuinely separate interpreter's `capture()` on a parent-held lock, and by pinning
   that both processes contend on the SAME lock-file inode (`st_dev`/`st_ino`), per
   `[[verification-shape-sharpened-grep-vs-e2e]]`'s lock-identity discipline. Racing
   wall-clock proves nothing; lock identity does.
2. **Independence from an unspecified platform guarantee.** `O_APPEND` write atomicity
   is not contractual: it does not hold on NFS/SMB (the resolved `STATE_LEDGER`
   directory is operator-configured and may be a network mount), and a short write
   re-introduces multi-syscall emission. The lock makes the guarantee the store's own.
3. **Soundness of the torn-append self-heal**, whose "read the last byte, then decide"
   reasoning is documented single-writer-only and was a live TOCTOU across processes.

**The lock is PER-WORKFLOW, not per-directory** — witnessed below, because the coarser
choice is the tempting one. The house `cross_process_scope_lock` (one lock per directory
TREE) was tried first and rejected on out-of-family review: it makes one workflow's
append wait behind another's, contradicting this store's own isolation property, and —
because reads are unlocked — it widens the window in which a read of the queued workflow
reports the `absent` cause that Runtime spec v1.107 §30 attributes as PERMANENT.

**The read path deliberately takes NO lock** — witnessed twice below (a callsite witness
and a genuine liveness witness), because that decision is exactly what keeps §30's
`empty-journal` INDETERMINATE clause correct as written, and therefore what makes this
arc owe zero spec text.

**Both directory fsyncs are unconditional**, and three witnesses below pin that. Every
flag-gated form (`dir_is_new`, `is_new_file`, or their disjunction) is unsound because
the flags are process-local while the crash they guard against is another process's —
see `_append`'s own docstring for the two interleavings that defeat them.
"""

from __future__ import annotations

import errno
import json
import subprocess
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle import journal_workflow_pause_store as store_module
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_LOCK_SUFFIX,
    JournalWorkflowPauseStore,
    pause_journal_filename,
)

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32",
    reason="`_cross_process_append_lock` deliberately no-ops on Windows (C-STK-10, no "
    "fcntl; the B-45 register row), so no lock file is created and the exclusion "
    "assertions do not hold there.",
)
"""Applied PER TEST, not module-wide.

A module-wide `pytestmark` also skipped the durability, self-heal, round-trip and
provisioning witnesses — none of which touch `fcntl` — leaving those properties with
ZERO Windows coverage for no reason, and leaving the `_IS_WINDOWS` branch itself
unexecuted on every platform. Only the tests that genuinely require POSIX `flock`
semantics carry this mark.
"""

_WORKFLOW_ID = "wf-b97-cross-process"
_READY_TIMEOUT = 30.0
"""A cold child interpreter's own import of `harness_runtime` costs seconds here."""

_BLOCKED_WINDOW = 0.5
"""Bounded wait AFTER the child signals it is AT the `flock` syscall (the B-73
handshake): before that signal, 'not done yet' would only prove the child had not
finished importing."""

#: Shared child-process preamble: build the SAME `PauseSnapshot` shape the store
#: journals, without importing this test module (a fresh interpreter cannot resolve
#: this monorepo's several same-named `tests` packages by module name).
_CHILD_PREAMBLE = f"""
import os, sys, time
from pathlib import Path
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore

def snapshot(run_id, payload_size=0):
    return PauseSnapshot(
        workflow_id={_WORKFLOW_ID!r},
        run_id=run_id,
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="x" * payload_size,
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
    )
"""

#: Wraps `fcntl.flock` itself so the readiness marker fires at the ACTUAL syscall,
#: not merely "shortly before the call that contends" — the B-73 round-3 finding: a
#: child descheduled between the marker and the syscall can otherwise let a missing
#: lock go undetected. Also records the locked fd's filesystem identity, which is
#: what the lock-identity witness compares.
_FLOCK_SIGNAL_WRAPPER = """
import fcntl as _fcntl
_real_flock = _fcntl.flock
def _signaling_flock(fd, op):
    st = os.fstat(fd)
    Path(identity_marker).write_text("%d:%d" % (st.st_dev, st.st_ino))
    Path(ready_marker).write_text("ready")
    return _real_flock(fd, op)
_fcntl.flock = _signaling_flock
"""

_CHILD_CAPTURE_SCRIPT = (
    _CHILD_PREAMBLE
    + """
journal_dir, done_marker, ready_marker, identity_marker = sys.argv[1:5]
"""
    + _FLOCK_SIGNAL_WRAPPER
    + """
JournalWorkflowPauseStore(journal_dir=Path(journal_dir), tenant_id=None).capture(snapshot("run-child"))
Path(done_marker).write_text("done")
"""
)

_CHILD_HOLD_LOCK_SCRIPT = (
    _CHILD_PREAMBLE
    + """
journal_dir, workflow_id, held_marker, release_marker = sys.argv[1:5]
store = JournalWorkflowPauseStore(journal_dir=Path(journal_dir), tenant_id=None)
Path(journal_dir).mkdir(parents=True, exist_ok=True)
with store._cross_process_append_lock(store._journal_file(workflow_id)):
    Path(held_marker).write_text("held")
    deadline = time.monotonic() + 60.0
    while not Path(release_marker).exists() and time.monotonic() < deadline:
        time.sleep(0.01)
"""
)

_CHILD_BULK_APPEND_SCRIPT = (
    _CHILD_PREAMBLE
    + """
journal_dir, tag, count, payload_size, go_marker, ready_marker = sys.argv[1:7]
store = JournalWorkflowPauseStore(journal_dir=Path(journal_dir), tenant_id=None)
Path(ready_marker).write_text("ready")
deadline = time.monotonic() + 60.0
while not Path(go_marker).exists():
    assert time.monotonic() < deadline, "start barrier never opened"
    time.sleep(0.005)
for i in range(int(count)):
    store.capture(snapshot("run-%s-%d" % (tag, i), payload_size=int(payload_size)))
"""
)


# --------------------------------------------------------------------------
# Substrate
# --------------------------------------------------------------------------


def _snapshot(run_id: str, *, payload_size: int = 0) -> PauseSnapshot:
    return _snapshot_for(_WORKFLOW_ID, run_id, payload_size=payload_size)


def _snapshot_for(workflow_id: str, run_id: str, *, payload_size: int = 0) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=run_id,
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="x" * payload_size,
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
    )


def _journal_file(journal_dir: Path, workflow_id: str = _WORKFLOW_ID) -> Path:
    # AMENDED at `B-97` half (a): the filename derives from the TENANT-COMPOSITE
    # key (Runtime spec v1.108 §14.14.8), not the bare `workflow_id`. Every store
    # in this module is constructed untenanted (`tenant_id=None`), so the
    # one-segment form is the one under test here — the tenanted forms are
    # witnessed at `test_pause_journal_tenant_keying_b97a.py`.
    return journal_dir / pause_journal_filename(None, workflow_id)


def _lock_file(journal_dir: Path, workflow_id: str = _WORKFLOW_ID) -> Path:
    journal = _journal_file(journal_dir, workflow_id)
    return journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX)


@contextmanager
def _hold_append_lock(journal_dir: Path, workflow_id: str = _WORKFLOW_ID) -> Generator[None]:
    """Hold the store's OWN per-workflow append lock, exactly as `_append` takes it."""
    journal_dir.mkdir(parents=True, exist_ok=True)
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    with store._cross_process_append_lock(  # pyright: ignore[reportPrivateUsage]
        _journal_file(journal_dir, workflow_id)
    ):
        yield


def _await_marker(marker: Path, *, what: str, timeout: float = _READY_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout
    while not marker.exists():
        assert time.monotonic() < deadline, f"{what} never appeared"
        time.sleep(0.02)


def _spawn(script: str, *args: object) -> subprocess.Popen[bytes]:
    """A GENUINE separate OS process: a fresh interpreter with no shared Python state,
    so no in-process lock could ever serialize it. (`subprocess` rather than
    `multiprocessing`: `fork` after a lock is held is the documented workspace deadlock
    hazard, and `spawn`'s pickle-by-module-name resolution is ambiguous across this
    monorepo's several same-named `tests` packages.)"""
    return subprocess.Popen([sys.executable, "-c", script, *(str(a) for a in args)])


@contextmanager
def _child(script: str, *args: object) -> Generator[subprocess.Popen[bytes]]:
    """`_spawn` plus reliable reaping on any exit, for the cases whose child does not
    need to outlive the block."""
    proc = _spawn(script, *args)
    try:
        yield proc
    finally:
        if proc.poll() is None:  # pragma: no cover - failure/cleanup path
            proc.kill()
        proc.wait(timeout=30.0)


# --------------------------------------------------------------------------
# W1 — mutual exclusion across OS processes
# --------------------------------------------------------------------------


@requires_posix_flock
def test_append_blocks_a_second_os_process_holding_the_journal_lock(tmp_path: Path) -> None:
    """THE primary witness: a genuinely separate OS process's `capture()` BLOCKS
    while this process holds the journal's cross-process lock.

    A GENUINE second interpreter is required, not a thread. `_cross_process_append_lock`
    opens a FRESH fd per call and `flock`s it, so its exclusion is kernel-side and
    per-open-file-description; a same-process thread pair would tell us nothing about
    the property under test, and any in-process serialization the caller happened to
    hold would mask a missing `flock` entirely.

    Mutation probe (run at this arc): deleting the
    `with self._cross_process_append_lock(path):` wrapper from `_append` makes the
    child's `capture()` complete immediately — `done_marker` exists inside the parent's
    hold and this test FAILS. Restored: green.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    done = tmp_path / "child_done"
    ready = tmp_path / "child_ready"
    identity = tmp_path / "child_identity"

    # Not the `_child` helper here: the child must OUTLIVE the parent's hold (it is
    # released by that hold, and its own success is half the assertion), so it is
    # reaped explicitly on the failure path only.
    with _hold_append_lock(journal_dir):
        child = _spawn(_CHILD_CAPTURE_SCRIPT, journal_dir, done, ready, identity)
        try:
            _await_marker(ready, what="the child's flock-attempt signal")
            # Timed from the moment the child is AT the syscall, not from spawn.
            time.sleep(_BLOCKED_WINDOW)
            assert not done.exists(), (
                "a separate OS process's capture() completed while this process held "
                "the journal's cross-process write lock — _append is unserialized"
            )
            assert child.poll() is None, "the child exited without ever contending"
        except BaseException:  # pragma: no cover - failure path
            child.kill()
            child.wait(timeout=30.0)
            raise

    assert child.wait(timeout=_READY_TIMEOUT) == 0
    assert done.exists()
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None and read.snapshot.run_id == "run-child"


@requires_posix_flock
def test_both_processes_contend_on_the_same_lock_file_identity(tmp_path: Path) -> None:
    """Lock-IDENTITY witness: the writer this process runs and the writer a separate
    OS process runs `flock` the SAME inode.

    The blocking witness above establishes that a second process WAITED; on its own
    that is a timing observation, and a cold child interpreter's own multi-second
    import cost is a known way for such an observation to pass for the wrong reason
    (the B-73 round-3 finding). This one converts it into an identity claim: the inode
    the child actually passed to `fcntl.flock` IS THIS WORKFLOW's own lock file. No
    accident of scheduling can satisfy that, and it pins the per-workflow KEYING (a
    directory-wide lock file would fail the path assertion outright).

    Mutation probe (run at this arc): mis-keying `_append`'s lock — e.g. back to a
    directory-wide `cross_process_scope_lock(journal_dir)` — fails THIS test because no
    `<journal>.lock` sibling is ever created; recorded honestly, it also fails the
    blocking witness above, since any mis-keying breaks both. The two are mutually
    reinforcing, not independent: this one supplies the identity the other cannot.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    done = tmp_path / "child_done"
    ready = tmp_path / "child_ready"
    child_identity = tmp_path / "child_identity"

    with _child(_CHILD_CAPTURE_SCRIPT, journal_dir, done, ready, child_identity) as child:
        _await_marker(ready, what="the child's flock-attempt signal")
        assert child.wait(timeout=_READY_TIMEOUT) == 0

    lock_file = _lock_file(journal_dir)
    assert lock_file.exists(), "this workflow's journal carries no cross-process lock file"
    parent_stat = lock_file.stat()
    assert child_identity.read_text() == f"{parent_stat.st_dev}:{parent_stat.st_ino}", (
        "the child locked a DIFFERENT inode than this workflow's own lock file — "
        "the two writers are not mutually excluded by anything"
    )


@requires_posix_flock  # its corroboration half spawns `_CHILD_CAPTURE_SCRIPT`, which
# imports `fcntl` unconditionally. The platform-independent half of this claim (the lock
# target IS this workflow's own journal) stays covered on Windows by
# `test_the_read_path_acquires_no_cross_process_lock`'s callsite assertion.
def test_two_workflows_lock_distinct_targets_and_do_not_block_each_other(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """out-of-family Codex [P2] on this arc — the reason the lock is PER-WORKFLOW.

    The first implementation used the house `cross_process_scope_lock` over the journal
    DIRECTORY. It serializes correctly, but it also makes workflow B's capture wait
    behind workflow A's — and the cost is externally visible, not merely a throughput
    one: because the read path is deliberately unlocked, B's journal stays absent for
    the whole wait, so a concurrent `read_latest_attributed(B)` reports the `absent`
    cause, which Runtime spec v1.107 §30 attributes as PERMANENT (`retryable=False`,
    `indeterminate=False`) — a decisive resume-handle failure for a capture that
    completes moments later. It also contradicts this store's own documented isolation
    property: per-workflow files exist so one workflow cannot block another.

    The load-bearing assertion is STRUCTURAL — two workflows lock two DISTINCT targets,
    each its own journal's `.lock` sibling — because that is the claim a directory-wide
    lock actually violates. The genuine-two-process half below corroborates that a
    second interpreter's capture of B runs to completion while this process holds A's
    lock; on its own it would be weaker, since it can only observe the lock the shipped
    code takes.

    Mutation probe (run at this arc): restoring `cross_process_scope_lock(journal_dir)`
    in `_append` fails the structural assertion outright (no per-workflow lock is taken
    at all), alongside three of this module's other witnesses. Recorded honestly: under
    that same mutation the two-process half below passes for an UNINTERESTING reason —
    the parent's hold uses the then-unreferenced per-workflow primitive, so there is
    nothing for the child to contend with. That is exactly why the structural assertion
    leads.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    other = "wf-b97-a-different-workflow"

    acquired: list[Path] = []
    real = JournalWorkflowPauseStore._cross_process_append_lock  # pyright: ignore[reportPrivateUsage]

    @contextmanager
    def _recording(
        self: JournalWorkflowPauseStore, journal_path: Path
    ) -> Generator[None, None, None]:
        acquired.append(journal_path)
        with real(self, journal_path):
            yield

    monkeypatch.setattr(JournalWorkflowPauseStore, "_cross_process_append_lock", _recording)
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("run-a"))
    store.capture(_snapshot_for(other, "run-b"))
    assert acquired == [_journal_file(journal_dir), _journal_file(journal_dir, other)], (
        "the two workflows did not lock distinct per-workflow targets — a shared lock "
        "makes one workflow's capture wait behind another's"
    )
    monkeypatch.undo()

    # Corroboration against a GENUINE second process.
    done = tmp_path / "child_done"
    ready = tmp_path / "child_ready"
    identity = tmp_path / "child_identity"
    with _hold_append_lock(journal_dir, other):
        with _child(_CHILD_CAPTURE_SCRIPT, journal_dir, done, ready, identity) as child:
            assert child.wait(timeout=_READY_TIMEOUT) == 0, (
                "a capture for one workflow blocked behind a lock held on ANOTHER "
                "workflow's journal — the lock is coarser than the store's isolation"
            )
        assert done.exists()


@requires_posix_flock
def test_two_os_processes_appending_large_records_leave_every_record_whole(
    tmp_path: Path,
) -> None:
    """End-to-end integrity under genuine concurrency: two separate OS processes
    interleaving multi-KiB appends leave a journal in which EVERY record parses whole
    and NONE is lost.

    Scope stated honestly: this is a REGRESSION guard, not the discriminator. Per the
    module docstring's syscall probe, today's `_append` emits one record per `write()`
    and `O_APPEND` makes that atomic on a local POSIX filesystem, so this assertion
    passes with the lock removed too. It earns its place by failing if a future change
    re-introduces multi-syscall record emission (an unbuffered handle, a separate
    prefix write outside the buffer) — the exact condition under which the lock stops
    being belt-and-braces and starts being load-bearing — and by proving the lock
    itself neither deadlocks nor drops records under real contention.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    per_process = 12
    payload = 60_000  # > the 8 KiB text-IO buffer, per the register's own framing
    go = tmp_path / "go"

    readies = [tmp_path / "ready-A", tmp_path / "ready-B"]
    with _child(
        _CHILD_BULK_APPEND_SCRIPT, journal_dir, "A", per_process, payload, go, readies[0]
    ) as a:
        with _child(
            _CHILD_BULK_APPEND_SCRIPT, journal_dir, "B", per_process, payload, go, readies[1]
        ) as b:
            for marker in readies:
                _await_marker(marker, what=f"{marker.name} (a bulk appender)")
            go.write_text("go")
            assert a.wait(timeout=180.0) == 0
            assert b.wait(timeout=180.0) == 0

    lines = [ln for ln in _journal_file(journal_dir).read_text("utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2 * per_process
    run_ids: set[str] = set()
    for line in lines:
        record = json.loads(line)  # a torn/interleaved line raises here
        assert record["workflow_id"] == _WORKFLOW_ID
        snapshot = record["pause_snapshot"]
        assert len(snapshot["state_summary"]["summary_text"]) == payload
        run_ids.add(str(snapshot["run_id"]))
    expected = {f"run-{tag}-{i}" for tag in ("A", "B") for i in range(per_process)}
    assert run_ids == expected, "a concurrent append was lost or duplicated"

    read = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed(_WORKFLOW_ID)
    assert read.record_count == 2 * per_process
    assert read.snapshot is not None


# --------------------------------------------------------------------------
# W2 — the read path takes NO lock (the zero-spec-text premise, pinned)
# --------------------------------------------------------------------------


def test_the_read_path_acquires_no_cross_process_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Callsite witness: `capture()` acquires exactly one lock, on THIS workflow's
    journal; `read_latest_attributed()` acquires NOTHING.

    This is deliberate, not an omission. Runtime spec v1.107 §30 calls `empty-journal`
    *"INDETERMINATE across processes"* because *"a concurrent `capture()` may complete
    immediately after this read"* — an after-the-read completion no write lock can
    exclude. Locking the read would buy no determinism while making the shipped
    `indeterminate=True` read as over-conservative rather than exact; leaving it
    unlocked is what keeps §30 correct AS WRITTEN, and therefore why serializing the
    write path owed zero spec text.

    Mutation probe (run at this arc): wrapping the body of `read_latest_attributed` in
    the same lock makes the read record an acquisition and this test FAILS on both
    assertions.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    acquired: list[Path] = []
    real = JournalWorkflowPauseStore._cross_process_append_lock  # pyright: ignore[reportPrivateUsage]

    @contextmanager
    def _recording(
        self: JournalWorkflowPauseStore, journal_path: Path
    ) -> Generator[None, None, None]:
        acquired.append(journal_path)
        with real(self, journal_path):
            yield

    monkeypatch.setattr(JournalWorkflowPauseStore, "_cross_process_append_lock", _recording)

    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("run-write"))
    assert acquired == [_journal_file(journal_dir)], (
        "the write path must lock THIS workflow's journal, exactly once"
    )

    acquired.clear()
    assert store.read_latest_attributed(_WORKFLOW_ID).snapshot is not None
    assert store.read_latest(_WORKFLOW_ID) is not None
    assert acquired == [], "the read path acquired the write lock — see this test's docstring"


@requires_posix_flock
def test_read_completes_while_a_separate_os_process_holds_the_journal_lock(
    tmp_path: Path,
) -> None:
    """The liveness half of the same decision, against a GENUINE second process.

    The callsite witness above could be satisfied by a lock taken through some other
    name; this one cannot. A separate interpreter holds THIS workflow's append lock open
    for the whole assertion, and the read still returns the journaled snapshot.

    Mutation probe (run at this arc): with the read wrapped in the same lock, this test
    hangs until the child's own 60s release deadline and then fails the bounded `assert`
    below.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("run-before-hold"))

    held = tmp_path / "child_held"
    release = tmp_path / "child_release"
    with _child(_CHILD_HOLD_LOCK_SCRIPT, journal_dir, _WORKFLOW_ID, held, release) as child:
        try:
            _await_marker(held, what="the child's lock-held signal")
            started = time.monotonic()
            read = store.read_latest_attributed(_WORKFLOW_ID)
            elapsed = time.monotonic() - started
            assert read.snapshot is not None and read.snapshot.run_id == "run-before-hold"
            assert elapsed < 5.0, (
                "the read blocked on the journal's write lock while another process "
                f"held it ({elapsed:.1f}s) — it must not take that lock"
            )
        finally:
            release.write_text("go")
        assert child.wait(timeout=_READY_TIMEOUT) == 0


# --------------------------------------------------------------------------
# W3 — single-writer behaviour is unchanged under the lock
# --------------------------------------------------------------------------


def test_torn_tail_self_heal_still_repairs_under_the_lock(tmp_path: Path) -> None:
    """The self-heal is now sound rather than merely single-writer-correct: it runs
    INSIDE the hold, so the last-byte probe and the append it authorizes can no longer
    be split by another process. Its shipped behaviour is unchanged — a crash-torn
    fragment becomes its own ignored, non-latest line and the new record is the clean
    latest one."""
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("run-first"))
    journal = _journal_file(journal_dir)
    with journal.open("a", encoding="utf-8") as handle:
        handle.write('{"workflow_id": "wf-b97-cros')  # a torn in-flight append

    store.capture(_snapshot("run-after-tear"))

    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None and read.snapshot.run_id == "run-after-tear"
    lines = [ln for ln in journal.read_text("utf-8").splitlines() if ln.strip()]
    assert len(lines) == 3, "the torn fragment must survive as its own non-latest line"
    assert lines[1].endswith("cros"), "the fragment was concatenated onto, not separated"


def _record_fsyncs(monkeypatch: pytest.MonkeyPatch, journal_dir: Path) -> list[tuple[Path, bool]]:
    """Record every `_fsync_dir` target AND whether this workflow's journal file
    existed at that instant — the ordering fact the by-construction claim rests on."""
    seen: list[tuple[Path, bool]] = []
    real = JournalWorkflowPauseStore._fsync_dir  # pyright: ignore[reportPrivateUsage]

    def _recording(directory: Path) -> None:
        seen.append((directory, _journal_file(journal_dir).exists()))
        real(directory)

    monkeypatch.setattr(JournalWorkflowPauseStore, "_fsync_dir", staticmethod(_recording))
    return seen


def test_parent_dirent_is_fsynced_before_any_journal_file_can_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The by-construction ordering claim, asserted directly.

    The parent (`STATE_LEDGER`) fsync must happen BEFORE any statement that could
    create a journal file — that ordering is the whole reason the unconditional form
    is sound where every flag-gated form is not.

    Mutation probes (run at this arc): DELETING the pre-lock
    `self._fsync_dir(journal_dir.parent)` fails this on a missing parent entry;
    MOVING it after the `with` block fails it on `journal_file_existed=True`.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    seen = _record_fsyncs(monkeypatch, journal_dir)

    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(
        _snapshot("run-first")
    )

    assert seen, "no directory fsync happened at all"
    first_target, journal_file_existed = seen[0]
    assert first_target == journal_dir.parent, (
        "the first directory fsync was not the STATE_LEDGER parent — the "
        "pause-journal dirent is not linked durably before a journal file appears"
    )
    assert not journal_file_existed, (
        "the parent was fsynced only AFTER a journal file already existed — a writer "
        "dying in that window leaves a file whose directory is not durably linked"
    )
    assert [target for target, _ in seen] == [journal_dir.parent, journal_dir]


@pytest.mark.parametrize(
    ("residue", "gated_form_it_defeats"),
    [
        ("directory-only", "if dir_is_new:"),
        ("directory-and-file", "if is_new_file or dir_is_new:"),
    ],
)
def test_parent_is_fsynced_even_when_a_dead_writer_left_state_behind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, residue: str, gated_form_it_defeats: str
) -> None:
    """Both crash residues a flag-gated parent fsync skips FOREVER.

    `dir_is_new` and `is_new_file` are PROCESS-LOCAL, but the crash they must survive
    is another process's. Two residues, each defeating one gated form:

    - `directory-only` — a writer `mkdir`ed and died. Every successor reads
      `dir_is_new=False`, so `if dir_is_new:` never fires again.
    - `directory-and-file` — a writer's `path.open("a")` created the journal file and
      it died before the fsync. Every successor reads BOTH flags False, so even
      `if is_new_file or dir_is_new:` never fires again. This is the interleaving that
      falsifies "a journal file exists ⇒ some earlier writer already fsynced".

    Mutation probes (run at this arc): gating the parent fsync on `dir_is_new` fails
    the second case; gating it on `is_new_file or dir_is_new` also fails the second
    case; deleting it fails both.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True)
    if residue == "directory-and-file":
        # The dead writer got as far as creating + writing its record.
        _journal_file(journal_dir).write_text(
            json.dumps({"workflow_id": _WORKFLOW_ID, "pause_snapshot": {}}) + "\n",
            encoding="utf-8",
        )

    seen = _record_fsyncs(monkeypatch, journal_dir)
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(
        _snapshot("run-after-residue")
    )

    assert journal_dir.parent in [target for target, _ in seen], (
        f"a capture over {residue} crash residue never made the pause-journal dirent "
        f"durable — the {gated_form_it_defeats} form skips it forever"
    )


def test_journal_dir_is_fsynced_on_every_append_not_only_the_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The identical defect one level down, closed rather than left as a known twin.

    A writer that creates the journal file, writes, and dies before
    `_fsync_dir(journal_dir)` leaves the file's dirent non-durable; under an
    `if is_new_file:` gate every successor reads `False` and never links it. This
    window is PRE-EXISTING (byte-identical to the pre-`B-97` code) — it is closed here
    because shipping a fix for the parent while knowingly leaving its exact twin one
    level down is the asymmetry, not the discipline.

    Mutation probes (run at this arc): re-gating on `if is_new_file:` fails the
    second-capture assertion; deleting the call fails the first.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    seen = _record_fsyncs(monkeypatch, journal_dir)
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)

    store.capture(_snapshot("run-first"))
    assert [target for target, _ in seen] == [journal_dir.parent, journal_dir]

    seen.clear()
    store.capture(_snapshot("run-second"))
    assert [target for target, _ in seen] == [journal_dir.parent, journal_dir], (
        "a repeat append skipped a directory fsync — a predecessor that died before "
        "linking the dirent would never be recovered from"
    )


@requires_posix_flock
@pytest.mark.parametrize("dangling", [False, True])
def test_a_symlink_planted_at_the_lock_path_fails_loud(tmp_path: Path, dangling: bool) -> None:
    """`O_NOFOLLOW` on the lock-file open, witnessed.

    Without it, a symlink planted at `<journal>.lock` silently redirects exclusion to
    an attacker-chosen inode: every writer would `flock` a file of someone else's
    choosing, so two writers could believe they hold the lock while serializing
    against nothing — and a DANGLING symlink is worse, because `O_CREAT` would
    materialize the lock file at the link's target instead. Both are refused loudly.

    Mutation probe (run at this arc): dropping `os.O_NOFOLLOW` from the flag set makes
    `capture()` succeed against both planted links and fails BOTH parameterizations of
    this test — and only this test, which is why it is owed.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    journal_dir.mkdir(parents=True)
    target = tmp_path / "attacker-chosen"
    if not dangling:
        target.write_bytes(b"")
    _lock_file(journal_dir).symlink_to(target)

    with pytest.raises(OSError) as excinfo:
        JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(
            _snapshot("run-symlink")
        )
    assert excinfo.value.errno in {errno.ELOOP, errno.EMLINK}, (
        f"expected a loud O_NOFOLLOW refusal, got errno={excinfo.value.errno}"
    )
    assert not target.exists() or not target.read_bytes(), (
        "the lock open followed the symlink and wrote through it"
    )


def test_windows_carve_out_round_trips_without_creating_a_lock_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `_IS_WINDOWS` branch, EXECUTED — on every platform.

    It was previously unreachable in CI: `fcntl` exists on the POSIX runners, so the
    branch never ran, and the module-wide skip meant Windows ran nothing at all. The
    branch is not decoration — it is the documented C-STK-10 / `B-45` posture, and a
    typo in it would have shipped invisibly.

    Asserts the two things the carve-out promises: the store still round-trips (Windows
    sits at exact pre-`B-97` parity, not at a broken capture), and NO lock file is
    created (there is nothing to lock with).

    Mutation probe (run at this arc): making the carve-out `raise` instead of yielding
    fails this test and no other.
    """
    monkeypatch.setattr(store_module, "_IS_WINDOWS", True)
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)

    store.capture(_snapshot("run-windows"))
    store.capture(_snapshot("run-windows-2"))

    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None and read.snapshot.run_id == "run-windows-2"
    assert read.record_count == 2
    assert not _lock_file(journal_dir).exists(), (
        "the Windows carve-out created a lock file it can never lock"
    )


@requires_posix_flock
def test_the_lock_file_is_not_mistaken_for_a_journal_record(tmp_path: Path) -> None:
    """The lock file is a `<journal>.lock` sibling in the same directory. Nothing globs
    that directory (reads open one sha256-named path directly), so its presence must
    leave every read outcome untouched — including the ABSENT cause for a workflow that
    has never been journaled, whose own lock file is never created either."""
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("run-only"))

    assert _lock_file(journal_dir).exists()
    assert not _lock_file(journal_dir).read_bytes(), "the lock file must carry no bytes"
    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None and read.record_count == 1
    other = store.read_latest_attributed("wf-never-journaled")
    assert other.snapshot is None and other.cause is store_module.PauseJournalReadCause.ABSENT
    assert not _lock_file(journal_dir, "wf-never-journaled").exists()


def test_journal_directory_is_still_provisioned_when_absent(tmp_path: Path) -> None:
    """Deep-provisioning is preserved: `_append` creates the whole `pause-journal`
    chain under a not-yet-existing `STATE_LEDGER` directory. The `mkdir` runs BEFORE
    the lock (the lock file lives inside the directory it guards), which is also why
    `dir_is_new` is sampled first."""
    journal_dir = tmp_path / "never" / "created" / "pause-journal"
    assert not journal_dir.parent.exists()
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(
        _snapshot("run-deep")
    )
    assert _journal_file(journal_dir).exists()


@pytest.mark.parametrize("payload_size", [0, 60_000])
def test_round_trip_under_the_lock_preserves_the_record(tmp_path: Path, payload_size: int) -> None:
    """Both sides of the 8 KiB text-IO buffer boundary round-trip byte-identically."""
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("run-round-trip", payload_size=payload_size))
    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None
    assert len(read.snapshot.state_summary.summary_text) == payload_size

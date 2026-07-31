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
"""

from __future__ import annotations

import hashlib
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
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="cross_process_scope_lock deliberately no-ops on Windows (C-STK-10, no fcntl; "
    "the B-45 register row) — the exclusion assertions below do not hold there.",
)

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
JournalWorkflowPauseStore(journal_dir=Path(journal_dir)).capture(snapshot("run-child"))
Path(done_marker).write_text("done")
"""
)

_CHILD_HOLD_LOCK_SCRIPT = (
    _CHILD_PREAMBLE
    + """
journal_dir, workflow_id, held_marker, release_marker = sys.argv[1:5]
store = JournalWorkflowPauseStore(journal_dir=Path(journal_dir))
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
store = JournalWorkflowPauseStore(journal_dir=Path(journal_dir))
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
    return journal_dir / f"{hashlib.sha256(workflow_id.encode()).hexdigest()}.jsonl"


def _lock_file(journal_dir: Path, workflow_id: str = _WORKFLOW_ID) -> Path:
    journal = _journal_file(journal_dir, workflow_id)
    return journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX)


@contextmanager
def _hold_append_lock(journal_dir: Path, workflow_id: str = _WORKFLOW_ID) -> Generator[None]:
    """Hold the store's OWN per-workflow append lock, exactly as `_append` takes it."""
    journal_dir.mkdir(parents=True, exist_ok=True)
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
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


def test_append_blocks_a_second_os_process_holding_the_journal_lock(tmp_path: Path) -> None:
    """THE primary witness: a genuinely separate OS process's `capture()` BLOCKS
    while this process holds the journal's cross-process lock.

    A thread-based witness would prove nothing — `cross_process_scope_lock`'s
    in-process face is a per-thread reentrant `RLock` over a shared `_DirLock`, so a
    second thread would contend on that alone. Only a second interpreter, with fresh
    locks and fresh fds, isolates the `flock`.

    Mutation probe (run at this arc): deleting the `with cross_process_scope_lock(...)`
    wrapper from `_append` makes the child's `capture()` complete immediately —
    `done_marker` exists inside the parent's hold and this test FAILS. Restored: green.
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
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None and read.snapshot.run_id == "run-child"


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
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
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

    read = JournalWorkflowPauseStore(journal_dir=journal_dir).read_latest_attributed(_WORKFLOW_ID)
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

    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
    store.capture(_snapshot("run-write"))
    assert acquired == [_journal_file(journal_dir)], (
        "the write path must lock THIS workflow's journal, exactly once"
    )

    acquired.clear()
    assert store.read_latest_attributed(_WORKFLOW_ID).snapshot is not None
    assert store.read_latest(_WORKFLOW_ID) is not None
    assert acquired == [], "the read path acquired the write lock — see this test's docstring"


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
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
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
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
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


def test_first_capture_still_fsyncs_both_the_journal_dir_and_its_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one durability property this arc could plausibly have regressed.

    `cross_process_scope_lock` PROVISIONS its scope root, so sampling `dir_is_new`
    after acquisition would always read `False` and silently drop the grandparent
    fsync that persists the `pause-journal` dirent into the `STATE_LEDGER` directory —
    the exact loss the shipped comment says would produce a spurious
    `RT-FAIL-RESUME-HANDLE-UNKNOWN`. `_append` therefore samples it BEFORE the lock.

    Mutation probe (run at this arc): moving the `dir_is_new = not journal_dir.exists()`
    line inside the `with cross_process_scope_lock(...)` block leaves every other test
    in this module green and makes THIS one fail — the parent is never fsynced.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    fsynced: list[Path] = []
    real = JournalWorkflowPauseStore._fsync_dir  # pyright: ignore[reportPrivateUsage]

    def _recording(directory: Path) -> None:
        fsynced.append(directory)
        real(directory)

    monkeypatch.setattr(JournalWorkflowPauseStore, "_fsync_dir", staticmethod(_recording))

    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
    store.capture(_snapshot("run-first"))
    assert fsynced == [journal_dir, journal_dir.parent]

    fsynced.clear()
    store.capture(_snapshot("run-second"))
    assert fsynced == [], "a repeat append into an existing journal owes no directory fsync"


def test_parent_is_fsynced_when_a_prior_process_left_the_directory_but_no_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """out-of-family Codex [P1] on this arc — the crash window `dir_is_new` alone
    leaves open, and the reason the parent fsync keys on `is_new_file`.

    A process that `mkdir`s the journal directory and then dies before writing leaves
    the dirent PRESENT but NOT DURABLE. Every later writer then samples
    `dir_is_new=False` and, keyed on that alone, skips the grandparent fsync FOREVER —
    so a capture returns successfully while the whole `pause-journal` directory is
    still losable to a host crash. The window pre-exists this arc (the old code had the
    same gap between its `mkdir` and its write); it just went unnoticed until an
    out-of-family reviewer looked at the provisioning order.

    Mutation probe (run at this arc): reverting the condition to `if dir_is_new:`
    alone leaves every other test in this module green — including the first-capture
    witness above, whose directory is created by `_append` itself — and makes THIS one
    fail with an empty parent fsync.
    """
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    # Exactly what the dead process left behind: the directory, no journal record,
    # no durable parent dirent.
    journal_dir.mkdir(parents=True)
    assert not _journal_file(journal_dir).exists()

    fsynced: list[Path] = []
    real = JournalWorkflowPauseStore._fsync_dir  # pyright: ignore[reportPrivateUsage]

    def _recording(directory: Path) -> None:
        fsynced.append(directory)
        real(directory)

    monkeypatch.setattr(JournalWorkflowPauseStore, "_fsync_dir", staticmethod(_recording))
    JournalWorkflowPauseStore(journal_dir=journal_dir).capture(_snapshot("run-after-orphan"))

    assert journal_dir.parent in fsynced, (
        "the first real capture after a lock-only directory creation never made the "
        "pause-journal dirent durable — an accepted pause is losable to a host crash"
    )


def test_the_lock_file_is_not_mistaken_for_a_journal_record(tmp_path: Path) -> None:
    """The lock file is a `<journal>.lock` sibling in the same directory. Nothing globs
    that directory (reads open one sha256-named path directly), so its presence must
    leave every read outcome untouched — including the ABSENT cause for a workflow that
    has never been journaled, whose own lock file is never created either."""
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
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
    JournalWorkflowPauseStore(journal_dir=journal_dir).capture(_snapshot("run-deep"))
    assert _journal_file(journal_dir).exists()


@pytest.mark.parametrize("payload_size", [0, 60_000])
def test_round_trip_under_the_lock_preserves_the_record(tmp_path: Path, payload_size: int) -> None:
    """Both sides of the 8 KiB text-IO buffer boundary round-trip byte-identically."""
    journal_dir = tmp_path / "state_ledger" / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir)
    store.capture(_snapshot("run-round-trip", payload_size=payload_size))
    read = store.read_latest_attributed(_WORKFLOW_ID)
    assert read.snapshot is not None
    assert len(read.snapshot.state_summary.summary_text) == payload_size

"""`B-46` — canonical-file cross-process lock witnesses.

The lock contends between separate fds even within one process (POSIX
`flock` is per open-file-description), so thread pairs with independent
lock acquisitions exercise the real cross-process semantics without
`fork()` (which composes badly with held locks — see the workspace
fork+lock memory). All blocking assertions are event-bounded, never bare
sleeps.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest
from harness_is.cross_process_ledger_lock import (
    cross_process_read_lock,
    cross_process_write_lock,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX flock semantics (B-45 posture)"
)

_WAIT = 5.0


def test_reader_blocks_during_first_ever_write(tmp_path: Path) -> None:
    """THE B-46 witness: a reader racing the very first write of a
    brand-new ledger (file absent, parent exists) must BLOCK on the
    absent-file-mode writer's directory hold — the pre-B-46 sidecar
    design yielded unguarded here for the ledger's whole pre-first-write
    life."""
    ledger = tmp_path / "ledger.jsonl"
    writer_in_section = threading.Event()
    release_writer = threading.Event()
    reader_entered = threading.Event()

    def _first_writer() -> None:
        with cross_process_write_lock(ledger):
            writer_in_section.set()
            release_writer.wait(_WAIT)
            ledger.write_text('{"row": 1}\n')

    def _reader() -> None:
        with cross_process_read_lock(ledger):
            reader_entered.set()

    w = threading.Thread(target=_first_writer)
    w.start()
    assert writer_in_section.wait(_WAIT)
    r = threading.Thread(target=_reader)
    r.start()
    # The reader must NOT enter while the first writer holds the section.
    assert not reader_entered.wait(0.5), "reader entered during the first write — B-46 race open"
    release_writer.set()
    w.join(_WAIT)
    r.join(_WAIT)
    assert reader_entered.is_set()
    assert ledger.read_text() == '{"row": 1}\n'


def test_reader_never_creates_anything(tmp_path: Path) -> None:
    """`harness-inspect` read-only contract: a read lock on a missing file
    (existing parent) and on a missing parent creates nothing."""
    ledger = tmp_path / "ledger.jsonl"
    with cross_process_read_lock(ledger):
        pass
    assert list(tmp_path.iterdir()) == []

    orphan = tmp_path / "never-bootstrapped" / "ledger.jsonl"
    with cross_process_read_lock(orphan):
        pass
    assert not orphan.parent.exists()


def test_lock_never_creates_canonical_file(tmp_path: Path) -> None:
    """The write lock itself must NOT create the canonical file — file
    existence must keep meaning "a real append happened" (the audit
    writer's round-36 absence guard keys on it)."""
    ledger = tmp_path / "ledger.jsonl"
    with cross_process_write_lock(ledger):
        assert not ledger.exists(), "the lock created the canonical file"
    assert not ledger.exists()


def test_writers_serialize_through_first_write(tmp_path: Path) -> None:
    """Two writers racing an absent ledger: the second blocks on the dir
    hold, then proceeds in file mode after the first creates the file."""
    ledger = tmp_path / "ledger.jsonl"
    w1_in = threading.Event()
    release_w1 = threading.Event()
    w2_done = threading.Event()

    def _w1() -> None:
        with cross_process_write_lock(ledger):
            w1_in.set()
            release_w1.wait(_WAIT)
            ledger.write_text("one\n")

    def _w2() -> None:
        with cross_process_write_lock(ledger):
            with ledger.open("a") as fh:
                fh.write("two\n")
        w2_done.set()

    t1 = threading.Thread(target=_w1)
    t2 = threading.Thread(target=_w2)
    t1.start()
    assert w1_in.wait(_WAIT)
    t2.start()
    assert not w2_done.wait(0.5), "second writer entered during the first write"
    release_w1.set()
    t1.join(_WAIT)
    t2.join(_WAIT)
    assert w2_done.is_set()
    assert ledger.read_text() == "one\ntwo\n"


def test_existing_file_read_write_exclusion(tmp_path: Path) -> None:
    """Regression witness for the pre-existing guarantee: with the file
    already on disk, a reader blocks while a writer holds the file lock."""
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("seed\n")
    writer_in = threading.Event()
    release_writer = threading.Event()
    reader_entered = threading.Event()

    def _writer() -> None:
        with cross_process_write_lock(ledger):
            writer_in.set()
            release_writer.wait(_WAIT)

    def _reader() -> None:
        with cross_process_read_lock(ledger):
            reader_entered.set()

    w = threading.Thread(target=_writer)
    w.start()
    assert writer_in.wait(_WAIT)
    r = threading.Thread(target=_reader)
    r.start()
    assert not reader_entered.wait(0.5), "reader entered while writer held the file lock"
    release_writer.set()
    w.join(_WAIT)
    r.join(_WAIT)
    assert reader_entered.is_set()


def test_different_ledgers_same_directory_do_not_serialize(tmp_path: Path) -> None:
    """The dir lock is a HANDOFF, not a section hold: a writer on ledger A
    (existing, file mode) must not block a writer on ledger B in the same
    directory — the audit sidecar and state ledger share a parent."""
    ledger_a = tmp_path / "a.jsonl"
    ledger_b = tmp_path / "b.jsonl"
    ledger_a.write_text("a\n")
    ledger_b.write_text("b\n")
    a_in = threading.Event()
    release_a = threading.Event()
    b_entered = threading.Event()

    def _writer_a() -> None:
        with cross_process_write_lock(ledger_a):
            a_in.set()
            release_a.wait(_WAIT)

    def _writer_b() -> None:
        with cross_process_write_lock(ledger_b):
            b_entered.set()

    ta = threading.Thread(target=_writer_a)
    ta.start()
    assert a_in.wait(_WAIT)
    tb = threading.Thread(target=_writer_b)
    tb.start()
    assert b_entered.wait(_WAIT), (
        "writer on a sibling ledger blocked — the dir lock is being held across the section"
    )
    release_a.set()
    ta.join(_WAIT)
    tb.join(_WAIT)


def test_nested_same_thread_same_directory_writes_do_not_deadlock(tmp_path: Path) -> None:
    """The B-50 `tenant_transaction` composition: an absent-file write
    section (dir lock held) performs ANOTHER write to a sibling ledger in
    the same directory from the SAME thread. A non-reentrant dir lock
    self-deadlocks here (flock contends between fds even in one process) —
    this witness hangs, and the suite timeout kills it, under that
    regression."""
    sidecar = tmp_path / "audit-entries.jsonl"
    state = tmp_path / "state.jsonl"
    state.write_text("genesis\n")
    done = threading.Event()

    def _nested() -> None:
        with cross_process_write_lock(sidecar):  # absent-file mode: dir held
            with cross_process_write_lock(state):  # same dir, same thread
                with state.open("a") as fh:
                    fh.write("nested\n")
            sidecar.write_text("first\n")
        done.set()

    t = threading.Thread(target=_nested)
    t.start()
    t.join(_WAIT)
    assert done.is_set(), "nested same-thread same-directory write deadlocked"
    assert state.read_text() == "genesis\nnested\n"
    assert sidecar.read_text() == "first\n"


def test_reader_blocks_after_midsection_file_creation(tmp_path: Path) -> None:
    """Codex round-1 P1 (B-46 landing) — the reader must be dir-first: a
    file-first fast path could open the file the absent-mode writer's
    CALLER just created and take an uncontested SHARED lock while that
    writer (holding only the directory lock) was still mid-append."""
    ledger = tmp_path / "ledger.jsonl"
    file_created = threading.Event()
    release_writer = threading.Event()
    reader_entered = threading.Event()

    def _first_writer() -> None:
        with cross_process_write_lock(ledger):
            ledger.write_text("partial")  # created MID-SECTION, append unfinished
            file_created.set()
            release_writer.wait(_WAIT)
            with ledger.open("a") as fh:
                fh.write(" complete\n")

    def _reader() -> None:
        with cross_process_read_lock(ledger):
            reader_entered.set()

    w = threading.Thread(target=_first_writer)
    w.start()
    assert file_created.wait(_WAIT)
    r = threading.Thread(target=_reader)
    r.start()
    assert not reader_entered.wait(0.5), (
        "reader entered mid-section after the caller created the file — file-first fast path"
    )
    release_writer.set()
    w.join(_WAIT)
    r.join(_WAIT)
    assert reader_entered.is_set()
    assert ledger.read_text() == "partial complete\n"


def test_lifecycle_probe_waits_for_first_writer(tmp_path: Path) -> None:
    """Codex round-1 P1 (B-46 landing) — `initialize_jsonl_event_ledger`'s
    missing-path touch + count must run under the write lock, not before
    it: an unlocked probe completed with entry_count=0 while a first
    writer held the directory lock mid-append."""
    from harness_core.deployment_surface import DeploymentSurface
    from harness_core.workload_class import WorkloadClass
    from harness_is.jsonl_event_ledger_lifecycle import (
        STATE_LEDGER_JSONL_FILENAME,
        initialize_jsonl_event_ledger,
    )
    from harness_is.path_class_registry import PathClass

    ledger = tmp_path / STATE_LEDGER_JSONL_FILENAME

    class _Resolver:
        def resolve_path(
            self, path_class: PathClass, wc: WorkloadClass, ds: DeploymentSurface
        ) -> Path:
            return tmp_path

    writer_in = threading.Event()
    release_writer = threading.Event()
    probe_done = threading.Event()
    counts: list[int] = []

    def _first_writer() -> None:
        with cross_process_write_lock(ledger):
            writer_in.set()
            release_writer.wait(_WAIT)
            ledger.write_text('{"row": 1}\n')

    def _probe() -> None:
        handle = initialize_jsonl_event_ledger(
            _Resolver(),  # type: ignore[arg-type] — structural stand-in
            workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
            deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        )
        counts.append(handle.entry_count)
        probe_done.set()

    w = threading.Thread(target=_first_writer)
    w.start()
    assert writer_in.wait(_WAIT)
    p = threading.Thread(target=_probe)
    p.start()
    assert not probe_done.wait(0.5), "probe completed while the first writer held the lock"
    release_writer.set()
    w.join(_WAIT)
    p.join(_WAIT)
    assert counts == [1], f"probe undercounted after waiting: {counts}"


def test_dir_lock_survives_failed_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex round-1 P2 (B-46 landing) — a failed dir open inside
    `_DirLock.acquire` must release the in-process RLock; a poisoned lock
    would block every later acquisition on that directory forever."""
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    real_open = os_module.open
    state = {"fail_next_dir_open": True}

    def _flaky_open(path: object, flags: int, *args: object) -> int:
        if state["fail_next_dir_open"] and str(path) == str(tmp_path):
            state["fail_next_dir_open"] = False
            raise PermissionError("transient")
        return real_open(path, flags, *args)  # type: ignore[arg-type]

    monkeypatch.setattr(os_module, "open", _flaky_open)
    with pytest.raises(PermissionError):
        with cross_process_write_lock(ledger):
            pass  # pragma: no cover — never entered

    done = threading.Event()

    def _retry() -> None:
        with cross_process_write_lock(ledger):
            done.set()

    t = threading.Thread(target=_retry)
    t.start()
    t.join(_WAIT)
    assert done.is_set(), "dir lock poisoned by the failed open"


def test_dir_lock_release_survives_a_raising_unlock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Gate-log LOW (post-#1159) — a raising `LOCK_UN` must not wedge the lock.

    `release` unlocked, closed the fd, and dropped the RLock in bare sequence,
    so an `OSError` out of `flock(fd, LOCK_UN)` (vanished mount, EBADF) skipped
    BOTH the `os.close` and the `self._rlock.release()`: the shared in-process
    face was then held forever and every later thread on that path blocked.
    The exception must still propagate — it is a real failure — but the lock
    must be left releasable, mirroring `acquire`'s already-hardened discipline.
    """
    import fcntl as fcntl_module

    from harness_is.cross_process_ledger_lock import _DirLock

    real_flock = fcntl_module.flock
    unlocks = 0

    def _flaky_flock(fd: int, operation: int) -> None:
        nonlocal unlocks
        if operation == fcntl_module.LOCK_UN:
            unlocks += 1
            if unlocks == 1:
                raise OSError(5, "Input/output error")
        real_flock(fd, operation)

    monkeypatch.setattr(fcntl_module, "flock", _flaky_flock)

    lock = _DirLock(tmp_path)
    lock.acquire()
    with pytest.raises(OSError):
        lock.release()

    done = threading.Event()

    def _retry() -> None:
        lock.acquire()
        try:
            done.set()
        finally:
            lock.release()

    # `daemon` so a regression fails this assertion rather than hanging the
    # interpreter at exit on a thread blocked forever inside `acquire`.
    t = threading.Thread(target=_retry, daemon=True)
    t.start()
    t.join(_WAIT)
    assert done.is_set(), "the in-process face stayed wedged after the raising unlock"
    assert lock._fd == -1, "the failed unlock left a stale fd behind"


def test_txn_with_reader_on_sibling_ledgers_does_not_deadlock(tmp_path: Path) -> None:
    """Codex round-2 P1 (B-46 landing) — the ABBA cycle: a transaction
    holds an existing sidecar's FILE lock and then writes the sibling
    state ledger (wants the dir); a concurrent sidecar reader holds the
    dir (transitional) waiting on that same file lock. Blocking on a file
    while holding the dir deadlocks both; the non-blocking probe +
    release-dir-then-block rule breaks the cycle. Under the regression
    this witness hangs (suite timeout kills it)."""
    sidecar = tmp_path / "audit-entries.jsonl"
    state = tmp_path / "state.jsonl"
    sidecar.write_text("seed\n")
    state.write_text("genesis\n")
    txn_holds_sidecar = threading.Event()
    reader_started = threading.Event()
    all_done = threading.Event()
    reader_done = threading.Event()

    def _txn() -> None:
        with cross_process_write_lock(sidecar):  # file EX on sidecar
            txn_holds_sidecar.set()
            reader_started.wait(_WAIT)
            # Give the reader time to take the dir and block on the sidecar.
            import time as time_module

            time_module.sleep(0.3)
            with cross_process_write_lock(state):  # wants the dir
                with state.open("a") as fh:
                    fh.write("txn\n")
        all_done.set()

    def _reader() -> None:
        reader_started.set()
        with cross_process_read_lock(sidecar):  # dir → blocks on file SH
            pass
        reader_done.set()

    t1 = threading.Thread(target=_txn)
    t2 = threading.Thread(target=_reader)
    t1.start()
    assert txn_holds_sidecar.wait(_WAIT)
    t2.start()
    t1.join(_WAIT * 2)
    t2.join(_WAIT)
    assert all_done.is_set(), "ABBA deadlock: txn blocked on the dir held by the reader"
    assert reader_done.is_set()
    assert state.read_text() == "genesis\ntxn\n"


def test_fifo_at_canonical_path_does_not_hang_read_lock(tmp_path: Path) -> None:
    """Codex round-3 P1 (B-46 landing) — a planted FIFO at the canonical
    path must not STALL the lock layer: with O_NONBLOCK the open returns
    immediately. The outcome is then platform-shaped and either is safe —
    macOS `flock` REJECTS a FIFO fd loudly (ENOTSUP), Linux permits it and
    the caller's validated open rejects the non-regular file downstream.
    The guarantee under test is completion-without-hang; the blocking-open
    regression hangs this witness."""
    import os as os_module

    fifo = tmp_path / "ledger.jsonl"
    os_module.mkfifo(fifo)
    completed = threading.Event()
    outcomes: list[str] = []

    def _read() -> None:
        try:
            with cross_process_read_lock(fifo):
                outcomes.append("entered")
        except OSError:
            outcomes.append("rejected")
        completed.set()

    t = threading.Thread(target=_read)
    t.start()
    t.join(_WAIT)
    assert completed.is_set(), "read lock hung on a planted FIFO"
    assert outcomes in (["entered"], ["rejected"])


def test_replace_section_excludes_writers_and_appends_survive(tmp_path: Path) -> None:
    """Codex round-3 P1 (B-46 landing) — the rollback composition: a
    section that REPLACES the ledger inode then rewrites content must
    exclude concurrent writers for its WHOLE duration; under a plain
    file lock (old inode) a concurrent append lands between the replace
    and the rewrite and is silently LOST."""
    import os as os_module

    from harness_is.cross_process_ledger_lock import cross_process_replace_lock

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("original\n")
    replaced = threading.Event()
    proceed_rewrite = threading.Event()
    writer_done = threading.Event()

    def _replacer() -> None:
        with cross_process_replace_lock(ledger):
            staging = tmp_path / "staging.tmp"
            staging.write_text("rolled-back\n")
            os_module.replace(staging, ledger)  # inode swap
            replaced.set()
            proceed_rewrite.wait(_WAIT)
            ledger.write_bytes(b"rolled-back\n")  # the rollback rewrite

    def _writer() -> None:
        with cross_process_write_lock(ledger):
            with ledger.open("a") as fh:
                fh.write("append\n")
        writer_done.set()

    r = threading.Thread(target=_replacer)
    r.start()
    assert replaced.wait(_WAIT)
    w = threading.Thread(target=_writer)
    w.start()
    # The writer must NOT complete while the replace section is active.
    assert not writer_done.wait(0.5), "writer entered during the replace section"
    proceed_rewrite.set()
    r.join(_WAIT)
    w.join(_WAIT)
    assert writer_done.is_set()
    assert ledger.read_text() == "rolled-back\nappend\n", (
        "the concurrent append was lost across the inode replacement"
    )


def test_acquisition_retries_across_inode_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex round-3 P1 (mechanism witness) — a lock acquired on an fd
    whose inode was swapped out between open and flock must be DISCARDED
    and retried: flock rides the inode, so a stale-inode lock would not
    serialize against post-replacement writers. The patched open swaps
    the file after the first call; the verify forces a second open."""
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("old\n")
    replacement_source = tmp_path / "next.tmp"
    replacement_source.write_text("new\n")
    real_open = os_module.open
    calls: list[str] = []

    def _swapping_open(path: object, flags: int, *args: object) -> int:
        fd = real_open(path, flags, *args)  # type: ignore[arg-type]
        if str(path) == str(ledger):
            calls.append("open")
            if len(calls) == 1:
                os_module.replace(replacement_source, ledger)  # inode swap
        return fd

    monkeypatch.setattr(os_module, "open", _swapping_open)
    with cross_process_write_lock(ledger):
        pass
    assert len(calls) == 2, f"expected a retry after the inode swap (2 opens), saw {len(calls)}"
    assert ledger.read_text() == "new\n"


def test_mixed_version_legacy_sidecar_coexistence(tmp_path: Path) -> None:
    """Codex round-4 P1 (B-46 landing) — a pre-B-46 process locks the
    sibling `<ledger>.lock` sidecar; when that sidecar EXISTS, the new
    lock must ALSO contend on it (transitional dual-locking) or old and
    new writers never contend and can fork the chain."""
    import fcntl
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("seed\n")
    legacy = tmp_path / "ledger.jsonl.lock"
    legacy.touch()  # a pre-B-46 process provisioned it

    old_holds = threading.Event()
    release_old = threading.Event()
    new_entered = threading.Event()

    def _old_process_writer() -> None:
        fd = os_module.open(legacy, os_module.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)  # the pre-B-46 protocol
            old_holds.set()
            release_old.wait(_WAIT)
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os_module.close(fd)

    def _new_writer() -> None:
        with cross_process_write_lock(ledger):
            new_entered.set()

    old = threading.Thread(target=_old_process_writer)
    old.start()
    assert old_holds.wait(_WAIT)
    new = threading.Thread(target=_new_writer)
    new.start()
    assert not new_entered.wait(0.5), (
        "new-version writer entered while a legacy-sidecar holder was active — chain fork risk"
    )
    release_old.set()
    old.join(_WAIT)
    new.join(_WAIT)
    assert new_entered.is_set()


def test_verify_error_does_not_leak_the_file_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex round-4 P2 (B-46 landing) — a raised stat during the inode
    verify must release the just-acquired file lock; a leaked lock blocks
    every later access to the ledger until process exit."""
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("seed\n")
    real_stat = os_module.stat
    state = {"raise_next": True}

    def _flaky_stat(path: object, **kw: object):  # type: ignore[no-untyped-def]
        if state["raise_next"] and str(path) == str(ledger):
            state["raise_next"] = False
            raise PermissionError("transient stat failure")
        return real_stat(path, **kw)  # type: ignore[arg-type]

    monkeypatch.setattr(os_module, "stat", _flaky_stat)
    with pytest.raises(PermissionError):
        with cross_process_write_lock(ledger):
            pass  # pragma: no cover — never entered

    done = threading.Event()

    def _retry() -> None:
        with cross_process_write_lock(ledger):
            done.set()

    t = threading.Thread(target=_retry)
    t.start()
    t.join(_WAIT)
    assert done.is_set(), "file lock leaked by the failed verify"


def test_absent_file_write_waits_for_legacy_holder(tmp_path: Path) -> None:
    """Codex round-5 P1 (B-46 landing) — rolling upgrade: a pre-B-46
    writer creates + locks the legacy sidecar BEFORE creating the
    canonical file. A new-version FIRST write reaching the absent-file
    branch must wait that holder out (and re-check the canonical it may
    have created) rather than fork the chain."""
    import fcntl
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    legacy = tmp_path / "ledger.jsonl.lock"
    legacy.touch()
    old_holds = threading.Event()
    release_old = threading.Event()
    new_entered = threading.Event()
    observed: list[str] = []

    def _old_writer() -> None:
        fd = os_module.open(legacy, os_module.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            old_holds.set()
            release_old.wait(_WAIT)
            ledger.write_text("old-row\n")  # the pre-B-46 first append
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os_module.close(fd)

    def _new_writer() -> None:
        with cross_process_write_lock(ledger):
            observed.append(ledger.read_text() if ledger.exists() else "<absent>")
            with ledger.open("a") as fh:
                fh.write("new-row\n")
        new_entered.set()

    old = threading.Thread(target=_old_writer)
    old.start()
    assert old_holds.wait(_WAIT)
    new = threading.Thread(target=_new_writer)
    new.start()
    assert not new_entered.wait(0.5), (
        "new writer entered the absent-file branch past a legacy holder"
    )
    release_old.set()
    old.join(_WAIT)
    new.join(_WAIT)
    assert new_entered.is_set()
    # The re-check saw the canonical the old writer created (no fork).
    assert observed == ["old-row\n"]
    assert ledger.read_text() == "old-row\nnew-row\n"


def test_fifo_legacy_sidecar_fails_loud_without_hanging(tmp_path: Path) -> None:
    """Codex rounds 5+8 (B-46 landing) — a FIFO planted at the legacy
    sidecar path must neither STALL the lock (nonblocking open) nor be
    silently ignored (on Linux an old writer CAN flock a FIFO, so
    treating it as absent loses mixed-version serialization): the write
    fails LOUD, promptly."""
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("seed\n")
    os_module.mkfifo(tmp_path / "ledger.jsonl.lock")
    done = threading.Event()
    outcomes: list[str] = []

    def _write() -> None:
        try:
            with cross_process_write_lock(ledger):
                outcomes.append("entered")
        except ValueError:
            outcomes.append("refused")
        done.set()

    t = threading.Thread(target=_write)
    t.start()
    t.join(_WAIT)
    assert done.is_set(), "write lock hung on a FIFO legacy sidecar"
    assert outcomes == ["refused"], f"mangled sidecar was not refused: {outcomes}"


def test_writer_provisions_legacy_sidecar_against_fresh_old_process(tmp_path: Path) -> None:
    """Codex round-7 P1 (B-46 landing) — a fresh pre-B-46 process arriving
    MID-WINDOW creates the legacy sidecar an exists-check missed. Writers
    now PROVISION + lock the sidecar, so the old process's create+lock
    blocks until the new writer's section ends (no concurrent append, no
    chain fork)."""
    import fcntl
    import os as os_module

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("seed\n")
    legacy = tmp_path / "ledger.jsonl.lock"
    assert not legacy.exists()

    new_in = threading.Event()
    release_new = threading.Event()
    old_entered = threading.Event()

    def _new_writer() -> None:
        with cross_process_write_lock(ledger):
            new_in.set()
            release_new.wait(_WAIT)

    def _fresh_old_process() -> None:
        # The pre-B-46 protocol: create the sidecar lazily, lock it EX.
        fd = os_module.open(legacy, os_module.O_CREAT | os_module.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            old_entered.set()
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os_module.close(fd)

    n = threading.Thread(target=_new_writer)
    n.start()
    assert new_in.wait(_WAIT)
    assert legacy.exists(), "the new writer did not provision the legacy sidecar"
    o = threading.Thread(target=_fresh_old_process)
    o.start()
    assert not old_entered.wait(0.5), (
        "a fresh old-version process entered concurrently — the provisioning race is open"
    )
    release_new.set()
    n.join(_WAIT)
    o.join(_WAIT)
    assert old_entered.is_set()


def test_aliased_legacy_sidecar_refused_without_hanging(tmp_path: Path) -> None:
    """Codex round-9 P2 (B-46 landing) — a sidecar aliasing the canonical
    ledger (hard link or symlink) passes S_ISREG but self-deadlocks on
    the inode this process already holds; both shapes must be refused
    LOUD and promptly (O_NOFOLLOW for the symlink; a dev/ino alias check
    for the hard link)."""
    import os as os_module

    def _attempt(target: Path, done: threading.Event, outcomes: list[str]) -> None:
        try:
            with cross_process_write_lock(target):
                outcomes.append("entered")
        except (ValueError, OSError):
            outcomes.append("refused")
        done.set()

    for alias_kind in ("hardlink", "symlink"):
        ledger = tmp_path / f"ledger-{alias_kind}.jsonl"
        ledger.write_text("seed\n")
        legacy = tmp_path / f"ledger-{alias_kind}.jsonl.lock"
        if alias_kind == "hardlink":
            os_module.link(ledger, legacy)
        else:
            os_module.symlink(ledger, legacy)
        done = threading.Event()
        outcomes: list[str] = []
        t = threading.Thread(target=_attempt, args=(ledger, done, outcomes))
        t.start()
        t.join(_WAIT)
        assert done.is_set(), f"write lock hung on a {alias_kind} legacy sidecar"
        assert outcomes == ["refused"], f"{alias_kind} alias not refused: {outcomes}"


def _mp_first_writer_worker(ledger: Path, in_section: object, release: object) -> None:
    """Module-level (picklable) worker: a genuine second OS process performing
    the FIRST write of an absent ledger. Forked BEFORE any lock is touched
    (fork-after-lock duplicates locked threading state into the child — the
    documented hazard in test_shadow_git_rollback)."""
    with cross_process_write_lock(ledger):
        in_section.set()  # type: ignore[attr-defined]
        release.wait(timeout=10)  # type: ignore[attr-defined]
        ledger.write_text("child\n")


def test_dir_flock_excludes_a_genuine_second_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Merge-gate round-1 test-witness lens (B-46) — the dir lock's
    CROSS-PROCESS flock face is the headline first-write guarantee, and
    every thread-based witness contends only on the in-process RLock face
    (the per-process `_DirLock` singleton). This witness forks a genuine
    second OS process (fresh RLock, fresh fds — only the flock can
    exclude it) holding the absent-file section; the parent's write must
    block, and the deterministic backstop pins the no-overwrite ordering.
    The transitional legacy-sidecar provisioning is inhibited BEFORE the
    fork (both processes inherit the patch), because it redundantly
    covers absent-file exclusion today — this witness pins the dir flock
    ALONE, the guard that becomes sole once B-45 retires the legacy
    protocol."""
    import multiprocessing

    from harness_is import cross_process_ledger_lock as lock_module

    monkeypatch.setattr(
        lock_module, "_acquire_legacy_sidecar_for_writer", lambda canonical_path: -1
    )
    ledger = tmp_path / "ledger.jsonl"
    ctx = multiprocessing.get_context("fork")
    in_section = ctx.Event()
    release = ctx.Event()
    proc = ctx.Process(target=_mp_first_writer_worker, args=(ledger, in_section, release))
    proc.start()
    try:
        assert in_section.wait(timeout=10)
        parent_entered = threading.Event()

        def _parent_write() -> None:
            with cross_process_write_lock(ledger):
                with ledger.open("a") as fh:
                    fh.write("parent\n")
            parent_entered.set()

        t = threading.Thread(target=_parent_write)
        t.start()
        assert not parent_entered.wait(0.5), (
            "parent entered while a second OS process held the absent-file dir flock"
        )
        release.set()
        t.join(_WAIT * 2)
        proc.join(10)
        assert parent_entered.is_set()
        assert ledger.read_text() == "child\nparent\n", (
            "append ordering broken — the dir flock did not exclude the second process"
        )
    finally:
        release.set()
        proc.join(5)
        if proc.is_alive():  # pragma: no cover — cleanup path
            proc.terminate()


def test_replace_lock_waits_out_an_active_file_holder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Merge-gate round-1 test-witness lens (B-46) — the replace lock's
    BlockingIOError wait-out branch: an ACTIVE file-lock holder must be
    waited out before the inode swap, or its in-flight append is
    clobbered by the checkout/restore-write (silent row loss). The
    transitional legacy provisioning is inhibited so the wait-out branch
    ALONE is pinned (it becomes sole once B-45 retires the legacy
    protocol)."""
    import os as os_module

    from harness_is import cross_process_ledger_lock as lock_module
    from harness_is.cross_process_ledger_lock import cross_process_replace_lock

    monkeypatch.setattr(
        lock_module, "_acquire_legacy_sidecar_for_writer", lambda canonical_path: -1
    )

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("seed\n")
    holder_in = threading.Event()
    release_holder = threading.Event()
    replacer_entered = threading.Event()

    def _holder() -> None:
        with cross_process_write_lock(ledger):
            holder_in.set()
            release_holder.wait(_WAIT)
            with ledger.open("a") as fh:
                fh.write("held\n")

    def _replacer() -> None:
        with cross_process_replace_lock(ledger):
            replacer_entered.set()
            staging = tmp_path / "staging.tmp"
            staging.write_text("rolled\n")
            os_module.replace(staging, ledger)
            ledger.write_bytes(b"rolled\n")

    h = threading.Thread(target=_holder)
    h.start()
    assert holder_in.wait(_WAIT)
    r = threading.Thread(target=_replacer)
    r.start()
    assert not replacer_entered.wait(0.5), (
        "replace section entered while an active writer held the file lock"
    )
    release_holder.set()
    h.join(_WAIT)
    r.join(_WAIT)
    assert replacer_entered.is_set()
    assert ledger.read_text() == "rolled\n", (
        "the active holder's append was clobbered mid-flight (wait-out missing)"
    )

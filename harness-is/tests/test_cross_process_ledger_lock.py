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

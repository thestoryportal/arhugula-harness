"""B-93 — the THREE `harness-runtime` acquisition sites, plus the §3(ii) import repair.

Companion to `harness-is/tests/test_b93_lock_deadline_is_sites.py` (sites
1-6). This file carries:

- sites 7/8/9 — `_workflow_lock`, `_cross_process_lock`, `cross_process_journal_lock`;
- **the `_workflow_lock` EXCLUSION witness the fork found MISSING at HEAD.**
  Out-of-family review round 9 on the filing established that the reconciler's
  only cross-process test — `test_cas_concurrent_resume_across_os_processes_exactly_one_wins`
  — proves the `os.link` CAS and SURVIVES removal of `_workflow_lock` entirely,
  so that carrier was UNWITNESSED. §12.4 item 6 makes closing that gap a
  condition of this leg. The witness runs the REAL `_workflow_lock` in a genuine
  second OS process and pins exclusion BY EXECUTION;
- the §3(ii) import repair — this module was the ONE lock carrier importing
  `fcntl` unconditionally at module scope, so `import harness_runtime...` died on
  Windows before any lock could degrade. Witnessed by importing it with `fcntl`
  made unavailable, which is what a Windows interpreter presents.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from harness_core import CrossProcessLockTimeoutError, WorkflowID
from harness_runtime.lifecycle import reconciler_pause_resume_substrate as reconciler_module
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_LOCK_SUFFIX,
    cross_process_journal_lock,
)
from harness_runtime.lifecycle.protected_result_store import (
    _CROSS_PROCESS_LOCK_FILENAME,  # type: ignore[attr-defined]
    ProtectedResultStore,
)
from harness_runtime.lifecycle.reconciler_pause_resume_substrate import (
    ReconcilerEnginePauseResumeSubstrate,
)

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32",
    reason="the cross-process locks degrade to a no-op on Windows (the B-45 register row)",
)

_DEADLINE = 0.2
_WORKFLOW = "wf-b93"

_FOREIGN_HOLDER = """
import fcntl, os, sys, time
target, ready, release = sys.argv[1:4]
fd = os.open(target, os.O_CREAT | os.O_RDWR, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX)
open(ready, "w").close()
limit = time.monotonic() + 60
while not os.path.exists(release) and time.monotonic() < limit:
    time.sleep(0.01)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
"""

_REAL_WORKFLOW_LOCK_HOLDER = """
import os, sys, time
from pathlib import Path
from harness_core import WorkflowID
from harness_runtime.lifecycle.reconciler_pause_resume_substrate import (
    ReconcilerEnginePauseResumeSubstrate,
)

journal_dir, workflow_id, ready, release = sys.argv[1:5]
substrate = ReconcilerEnginePauseResumeSubstrate(
    journal_dir=Path(journal_dir),
    state_summary_provider=lambda: None,
)
with substrate._workflow_lock(WorkflowID(workflow_id)):
    open(ready, "w").close()
    limit = time.monotonic() + 60
    while not os.path.exists(release) and time.monotonic() < limit:
        time.sleep(0.01)
"""


class _Holder:
    """A genuine second OS process holding one lock until released."""

    def __init__(self, tmp_path: Path, script: str, *args: str) -> None:
        self._ready = tmp_path / f"ready-{id(self)}"
        self._release = tmp_path / f"release-{id(self)}"
        self._proc = subprocess.Popen(
            [sys.executable, "-c", script, *args, str(self._ready), str(self._release)]
        )

    def __enter__(self) -> _Holder:
        limit = time.monotonic() + 60
        while not self._ready.exists() and time.monotonic() < limit:
            if self._proc.poll() is not None:  # pragma: no cover — holder crashed
                raise AssertionError(f"holder exited early with {self._proc.returncode}")
            time.sleep(0.01)
        assert self._ready.exists(), "holder never acquired the lock"
        return self

    def __exit__(self, *_exc: object) -> None:
        self._release.write_text("go")
        self._proc.wait(timeout=60)


def _substrate(journal_dir: Path) -> ReconcilerEnginePauseResumeSubstrate:
    return ReconcilerEnginePauseResumeSubstrate(
        journal_dir=journal_dir,
        state_summary_provider=lambda: None,  # type: ignore[arg-type,return-value]
    )


# --- site 7 — `_workflow_lock` --------------------------------------------


@requires_posix_flock
def test_site7_workflow_lock_deadline_fires(tmp_path: Path) -> None:
    """Bounded against a genuine second OS process running the REAL
    `_workflow_lock` — not a bare flock on the same path, so the witness also
    proves the two processes agree on which inode the lock lives at."""
    journal_dir = tmp_path / "reconcile"
    journal_dir.mkdir()
    substrate = _substrate(journal_dir)
    lock_file = substrate._lock_file(WorkflowID(_WORKFLOW))  # type: ignore[attr-defined]
    with _Holder(tmp_path, _REAL_WORKFLOW_LOCK_HOLDER, str(journal_dir), _WORKFLOW):
        started = time.monotonic()
        with pytest.raises(CrossProcessLockTimeoutError) as caught:
            with substrate._workflow_lock(  # type: ignore[attr-defined]
                WorkflowID(_WORKFLOW), deadline_seconds=_DEADLINE
            ):
                raise AssertionError("entered while a second OS process held the lock")
        assert caught.value.lock_target == str(lock_file)
        assert caught.value.budget_seconds == _DEADLINE
        assert time.monotonic() - started >= _DEADLINE


@requires_posix_flock
def test_site7_workflow_lock_excludes_a_genuine_second_os_process(tmp_path: Path) -> None:
    """THE GAP THE FORK NAMED (§12.4 item 6; out-of-family round 9 on the filing).

    `_workflow_lock` was UNWITNESSED at HEAD: the reconciler's only
    cross-process test proves the atomic `os.link` revision-claim, which
    guarantees exactly-one-winner INDEPENDENTLY of this flock — so that test
    passes with `_workflow_lock` deleted. This one cannot: it asserts, BY
    EXECUTION, that while a second OS process is inside the lock this process
    cannot enter, and that it enters promptly once the holder leaves.

    Deliberately NOT a deadline test — a generous budget is used so that a
    timeout would be a FAILURE. Exclusion and liveness are separate claims and
    a witness that conflated them would be satisfied by either.
    """
    journal_dir = tmp_path / "reconcile"
    journal_dir.mkdir()
    substrate = _substrate(journal_dir)
    entered = threading.Event()
    failed: list[BaseException] = []

    with _Holder(tmp_path, _REAL_WORKFLOW_LOCK_HOLDER, str(journal_dir), _WORKFLOW) as holder:

        def _contend() -> None:
            try:
                with substrate._workflow_lock(  # type: ignore[attr-defined]
                    WorkflowID(_WORKFLOW), deadline_seconds=30.0
                ):
                    entered.set()
            except BaseException as exc:  # pragma: no cover — surfaced below
                failed.append(exc)

        thread = threading.Thread(target=_contend)
        thread.start()
        try:
            assert not entered.wait(1.0), (
                "entered `_workflow_lock` while a genuine second OS process held it — "
                "the cross-process face excludes nothing"
            )
            assert not failed, f"contender failed before the holder released: {failed}"
            holder.__exit__()
            assert entered.wait(30.0), "never entered after the holder released"
            assert not failed
        finally:
            thread.join(60)
            holder._release.write_text("go")


@requires_posix_flock
def test_site7_workflow_lock_uncontended_is_unchanged(tmp_path: Path) -> None:
    """Non-contended path unchanged, and REENTRANT-free by construction: a
    budget too short to win any contended race still enters instantly."""
    journal_dir = tmp_path / "reconcile"
    journal_dir.mkdir()
    substrate = _substrate(journal_dir)
    with substrate._workflow_lock(WorkflowID(_WORKFLOW), deadline_seconds=0.001):  # type: ignore[attr-defined]
        assert substrate._lock_file(WorkflowID(_WORKFLOW)).exists()  # type: ignore[attr-defined]


# --- site 8 — `ProtectedResultStore._cross_process_lock` -------------------


@requires_posix_flock
def test_site8_protected_result_store_lock_deadline_fires(tmp_path: Path) -> None:
    """Serializes `_publish_atomic` and `gc_sweep`'s candidate selection across
    processes sharing a store root; an unbounded holder wedged both."""
    from cryptography.fernet import Fernet

    store_dir = tmp_path / "store"
    store_dir.mkdir()
    store = ProtectedResultStore(
        store_dir, codec=Fernet(Fernet.generate_key()), ttl_seconds=86400.0
    )
    lock_path = store_dir / _CROSS_PROCESS_LOCK_FILENAME
    with _Holder(tmp_path, _FOREIGN_HOLDER, str(lock_path)):
        started = time.monotonic()
        with pytest.raises(CrossProcessLockTimeoutError) as caught:
            with store._cross_process_lock(deadline_seconds=_DEADLINE):  # type: ignore[attr-defined]
                raise AssertionError("entered while a second OS process held the store lock")
        assert caught.value.lock_target == str(lock_path)
        assert time.monotonic() - started >= _DEADLINE


@requires_posix_flock
def test_site8_write_once_folds_the_timeout_instead_of_raising(tmp_path: Path) -> None:
    """Out-of-family review round 1 [P1], accepted — and it FALSIFIED a claim an
    earlier draft of `_cross_process_lock`'s docstring made.

    `write_once` is contracted to NEVER raise for an expected failure class: it
    is reached only while constructing a `PostEffectAuditSigningError` for an
    ALREADY-COMPLETED paid effect, so an escaping exception lets CP treat that
    effect as an ordinary resumable failure and REDISPATCH it. A raising `flock`
    arrived as an `OSError` and the existing arm folded it;
    `CrossProcessLockTimeoutError` deliberately does not derive from `OSError`,
    so before the fold it ESCAPED — a new failure path through the one method
    whose whole purpose is to have none.

    Mutation probe (run at this arc): removing the
    `except CrossProcessLockTimeoutError` arm makes this fail with the raw
    timeout propagating out of `write_once`.
    """
    from cryptography.fernet import Fernet

    store_dir = tmp_path / "store"
    store_dir.mkdir()
    store = ProtectedResultStore(
        store_dir, codec=Fernet(Fernet.generate_key()), ttl_seconds=86400.0
    )
    lock_path = store_dir / _CROSS_PROCESS_LOCK_FILENAME
    # Force every acquisition on this store to expire fast while a genuine
    # second OS process holds the lock.
    original = type(store)._cross_process_lock  # type: ignore[attr-defined]

    def _fast(self: ProtectedResultStore, *, deadline_seconds: float | None = None) -> object:
        return original(self, deadline_seconds=0.05)

    with _Holder(tmp_path, _FOREIGN_HOLDER, str(lock_path)):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(type(store), "_cross_process_lock", _fast)
            outcome = store.write_once(None, {"paid": "effect"})

    assert not isinstance(outcome, str), f"write_once returned a live ref: {outcome!r}"
    assert "lock timeout" in outcome.reason, outcome.reason


@requires_posix_flock
def test_site8_uncontended_is_unchanged(tmp_path: Path) -> None:
    """Non-contended publish/GC path unchanged."""
    from cryptography.fernet import Fernet

    store_dir = tmp_path / "store"
    store_dir.mkdir()
    store = ProtectedResultStore(
        store_dir, codec=Fernet(Fernet.generate_key()), ttl_seconds=86400.0
    )
    with store._cross_process_lock(deadline_seconds=0.001):  # type: ignore[attr-defined]
        assert (store_dir / _CROSS_PROCESS_LOCK_FILENAME).exists()


# --- site 9 — `cross_process_journal_lock` --------------------------------


@requires_posix_flock
def test_site9_journal_lock_deadline_fires(tmp_path: Path) -> None:
    """The `B-97` half-(b) per-workflow append lock, shared by the store and the
    (3b) adoption tool. Its own docstring records that the acquisition BLOCKS the
    calling thread; it is now finite."""
    journal = tmp_path / "journal" / "abc.jsonl"
    journal.parent.mkdir(parents=True)
    lock_path = journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX)
    with _Holder(tmp_path, _FOREIGN_HOLDER, str(lock_path)):
        started = time.monotonic()
        with pytest.raises(CrossProcessLockTimeoutError) as caught:
            with cross_process_journal_lock(journal, deadline_seconds=_DEADLINE):
                raise AssertionError("entered while a second OS process held the journal lock")
        assert caught.value.lock_target == str(lock_path)
        assert time.monotonic() - started >= _DEADLINE


@requires_posix_flock
def test_site9_uncontended_is_unchanged(tmp_path: Path) -> None:
    """Non-contended append path unchanged."""
    journal = tmp_path / "journal" / "abc.jsonl"
    journal.parent.mkdir(parents=True)
    with cross_process_journal_lock(journal, deadline_seconds=0.001):
        assert journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX).exists()


def test_journal_exclusion_degraded_predicate_is_untouched() -> None:
    """`B-45` is DEFERRED and this arc must not prejudge it. The predicate the
    (3b) adoption's refuse-by-default consult keys on still reports the PLATFORM
    carve-out — a deadline bounds how long exclusion is WAITED FOR, never whether
    it holds once acquired."""
    from harness_runtime.lifecycle.journal_workflow_pause_store import (
        journal_exclusion_is_degraded,
    )

    assert journal_exclusion_is_degraded() is (sys.platform == "win32")


# --- the §3(ii) import repair ---------------------------------------------


_IMPORT_UNDER_NO_FCNTL = """
import sys
sys.modules["fcntl"] = None  # what a Windows interpreter presents
import harness_runtime.lifecycle.reconciler_pause_resume_substrate as m
assert hasattr(m, "_IS_WINDOWS"), "the platform flag is missing"
print("imported")
"""


def test_the_reconciler_module_imports_without_fcntl() -> None:
    """§3(ii) — the repair, witnessed by EXECUTION rather than by grep.

    This module imported `fcntl` unconditionally at module scope and is imported
    at module scope by `bootstrap/factories/r_cxa_2_producer_loop_factory.py`, so
    on Windows that bootstrap path raised `ModuleNotFoundError: fcntl` at IMPORT
    time — a process that could not start, not a degraded lock. A `None` entry in
    `sys.modules` makes `import fcntl` fail exactly as it does on Windows.

    Mutation probe (run at this arc): restoring the module-scope `import fcntl`
    makes this fail with `ImportError: import of fcntl halted`.
    """
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_UNDER_NO_FCNTL],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        f"the reconciler module still needs fcntl at import time:\n{result.stderr}"
    )
    assert "imported" in result.stdout


def test_the_reconciler_module_does_not_bind_fcntl_at_module_scope() -> None:
    """The structural half of the repair, and the reason the runtime witness
    above is not sufficient on its own: a lazily re-added module-scope import
    inside a `try/except ImportError` would keep that test green while
    reintroducing the divergence from the three sibling carriers."""
    assert not hasattr(reconciler_module, "fcntl")
    assert reconciler_module._IS_WINDOWS is (sys.platform == "win32")


def test_the_windows_carve_out_yields_without_locking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The carve-out branch is EXERCISABLE, mirroring the sibling carriers'
    existing `_IS_WINDOWS`-monkeypatched witnesses. It must yield without
    creating a lock file — and must NOT be mistaken for a serialization claim:
    on Windows this excludes nothing, exactly as its three siblings do not
    (`B-45`, deferred on witnessability)."""
    journal_dir = tmp_path / "reconcile"
    journal_dir.mkdir()
    substrate = _substrate(journal_dir)
    monkeypatch.setattr(reconciler_module, "_IS_WINDOWS", True)
    with substrate._workflow_lock(WorkflowID(_WORKFLOW)):  # type: ignore[attr-defined]
        pass
    assert not any(p.suffix == ".lock" for p in journal_dir.iterdir()), (
        "the Windows carve-out created a lock file — it must yield before touching the fs"
    )
    assert os.listdir(journal_dir) == []

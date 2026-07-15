"""Tests for U-IS-15 — shadow-Git rollback primitive (C-IS-08 §8.3).

Test set per the U-IS-15 `Tests:` field — 7 tests covering acceptance #1-#6.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_is.chain_verification import VerificationStatus, verify_chain
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.shadow_git_checkpoint import (
    CheckpointTriggerContext,
    create_shadow_git_checkpoint,
)
from harness_is.shadow_git_rollback import RollbackStatus, rollback_to_checkpoint
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import EntryPayload, WriteKey, append_ledger_entry, read_ledger
from harness_is.workload_manifest_opt_in_schema import CheckpointCadence

_RUN = Identifier("wf-run-1")
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="agent-1")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@harness.local")
    _git(repo, "config", "user.name", "harness-test")
    (repo / "app.py").write_text("v1\n")
    (repo / "lib.py").write_text("lib-v1\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "base")
    return repo


def _ledger(repo: Path) -> JsonlLedgerHandle:
    """A ledger handle (untracked file inside the repo) with one prior entry."""
    handle = JsonlLedgerHandle(canonical_path=repo / "state.jsonl", exists=False, entry_count=0)
    append_ledger_entry(
        handle,
        EntryPayload(
            action_id=Identifier("act-pre"),
            idempotency_key=Identifier("idem-pre"),
            actor=_ACTOR,
            timestamp=datetime(2026, 5, 16, 1, tzinfo=UTC),
        ),
        WriteKey(
            thread_id=_RUN, step_id=Identifier("step-0"), idempotency_key=Identifier("idem-pre")
        ),
    )
    return handle


def _checkpoint(repo: Path) -> Identifier:
    result = create_shadow_git_checkpoint(
        repo,
        _RUN,
        CheckpointTriggerContext(
            cadence=CheckpointCadence.PER_EXPLICIT_MARKER, explicit_marker="m"
        ),
    )
    return result.checkpoint_id


def test_rollback_restores_filesystem(tmp_path: Path) -> None:
    """Acceptance #2/#3 — rollback restores tracked filesystem state."""
    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    (repo / "app.py").write_text("v2-broken\n")
    result = rollback_to_checkpoint(repo, _ledger(repo), checkpoint_id, _RUN)
    assert result.status is RollbackStatus.RESTORED
    assert (repo / "app.py").read_text() == "v1\n"


def test_rollback_does_not_restore_ledger(tmp_path: Path) -> None:
    """Acceptance #2 — the state-ledger is not rolled back."""
    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    handle = _ledger(repo)
    (repo / "app.py").write_text("v2\n")
    rollback_to_checkpoint(repo, handle, checkpoint_id, _RUN)
    # The pre-rollback entry survives (the ledger was not restored).
    action_ids = [e.action_id for e in read_ledger(handle)]
    assert "act-pre" in action_ids


def test_rollback_writes_rollback_event_to_ledger(tmp_path: Path) -> None:
    """Acceptance #4 — rollback appends an event carrying the checkpoint_id."""
    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    handle = _ledger(repo)
    rollback_to_checkpoint(repo, handle, checkpoint_id, _RUN)
    assert read_ledger(handle)[-1].action_id == f"rollback:{checkpoint_id}"


def test_rollback_atomic_full_or_none(tmp_path: Path) -> None:
    """Acceptance #1 — rollback restores every checkpointed file (full)."""
    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    (repo / "app.py").write_text("app-broken\n")
    (repo / "lib.py").write_text("lib-broken\n")
    rollback_to_checkpoint(repo, _ledger(repo), checkpoint_id, _RUN)
    assert (repo / "app.py").read_text() == "v1\n"
    assert (repo / "lib.py").read_text() == "lib-v1\n"


def test_rollback_checkpoint_not_found(tmp_path: Path) -> None:
    """Acceptance #5 — an unknown checkpoint ⇒ CHECKPOINT_NOT_FOUND, no change."""
    repo = _repo(tmp_path)
    handle = _ledger(repo)
    (repo / "app.py").write_text("v2\n")
    entries_before = len(read_ledger(handle))
    result = rollback_to_checkpoint(repo, handle, Identifier("no-such-ckpt"), _RUN)
    assert result.status is RollbackStatus.CHECKPOINT_NOT_FOUND
    assert result.rollback_entry_id is None
    assert (repo / "app.py").read_text() == "v2\n"  # filesystem unchanged
    assert len(read_ledger(handle)) == entries_before  # ledger unchanged


def test_rollback_filesystem_bounded(tmp_path: Path) -> None:
    """Acceptance #2 — rollback restores the FS but the ledger is preserved."""
    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    handle = _ledger(repo)
    (repo / "app.py").write_text("v2\n")
    rollback_to_checkpoint(repo, handle, checkpoint_id, _RUN)
    assert (repo / "app.py").read_text() == "v1\n"  # FS restored
    assert "act-pre" in [e.action_id for e in read_ledger(handle)]  # ledger kept


def test_rollback_does_not_modify_inference_state(tmp_path: Path) -> None:
    """Acceptance #3 — rollback is filesystem-bounded: it returns a
    RollbackResult and touches only tracked FS + the ledger event; there is no
    inference-state restoration (IS holds no inference state)."""
    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    result = rollback_to_checkpoint(repo, _ledger(repo), checkpoint_id, _RUN)
    assert result.status is RollbackStatus.RESTORED
    assert result.rollback_entry_id is not None


def test_rollback_holds_write_lock_across_ledger_preserve_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression — the ledger read-then-restore-write window (preserving the
    ledger's bytes across `git checkout`) must hold the same module-level
    write lock `append_ledger_entry` uses. Previously it read/wrote the
    ledger file directly with no lock — a concurrent append landing inside
    that window is silently overwritten and lost.

    Verified by asserting the lock is held (from another thread's view)
    exactly during the git-checkout call — the middle of the guarded window.
    """
    import threading

    from harness_is import shadow_git_rollback as sgr
    from harness_is.state_ledger_write import ledger_write_lock

    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    handle = _ledger(repo)

    observed_locked_from_other_thread: list[bool] = []
    real_git = sgr._git

    def _spy_git(repository_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if args and args[0] == "checkout":
            result_holder: list[bool] = []

            def _check() -> None:
                result_holder.append(ledger_write_lock().locked())

            probe = threading.Thread(target=_check)
            probe.start()
            probe.join()
            observed_locked_from_other_thread.extend(result_holder)
        return real_git(repository_root, *args)

    monkeypatch.setattr(sgr, "_git", _spy_git)  # type: ignore[attr-defined]

    result = rollback_to_checkpoint(repo, handle, checkpoint_id, _RUN)
    assert result.status is RollbackStatus.RESTORED
    assert observed_locked_from_other_thread == [True]


def _mp_append_worker_gated(canonical_path: Path, ready_event: object) -> None:
    """Module-level (picklable) worker — waits for a signal, then appends from
    a genuine OS process. Forked BEFORE any lock is acquired (see the caller's
    docstring for why fork timing matters here)."""
    from harness_is.state_ledger_write import append_ledger_entry as _append

    ready_event.wait(timeout=10)  # type: ignore[attr-defined]
    handle = JsonlLedgerHandle(canonical_path=canonical_path, exists=False, entry_count=0)
    _append(
        handle,
        EntryPayload(
            action_id=Identifier("act-concurrent"),
            idempotency_key=Identifier("idem-concurrent"),
            actor=_ACTOR,
            timestamp=datetime(2026, 5, 16, 2, tzinfo=UTC),
        ),
        WriteKey(
            thread_id=_RUN,
            step_id=Identifier("step-concurrent"),
            idempotency_key=Identifier("idem-concurrent"),
        ),
    )


@pytest.mark.skipif(sys.platform == "win32", reason="multiprocessing 'fork' context is POSIX-only")
def test_rollback_cross_process_lock_prevents_lost_concurrent_append(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-40 — a genuine OS process appending during the ledger-preserve-across-
    checkout window must NOT be silently lost by the restore-write. Without
    `cross_process_write_lock` (B-40's fix), the concurrent process's append
    can land between the pre-checkout read and the restore-write below it and
    get clobbered — the exact same-process-only gap the thread-based spy test
    above cannot detect (it only proves the in-process `threading.Lock` is
    held, not that a genuine second OS process is excluded).

    The child process is forked and started BEFORE `rollback_to_checkpoint`
    ever runs, then waits on an Event; the monkeypatched `_git` sets that
    event exactly during the checkout call, so the child's append attempt
    races against the ongoing preserve window. Fork timing matters: forking
    AFTER the parent has acquired `ledger_write_lock()` (a `threading.Lock`)
    would duplicate that lock's OS-level locked state into the child, which
    would then block forever (the only thread that could release it doesn't
    run in the child's address space) — a real hazard tried and confirmed
    here during development, not a hypothetical. Forking before any lock is
    touched sidesteps it; the child's own `_WRITE_LOCK` copy starts unlocked,
    and the cross-process `flock` genuinely serializes via a freshly-opened
    fd in the child, correctly modeling an independently-launched second
    `harness run` process.
    """
    import multiprocessing

    from harness_is import shadow_git_rollback as sgr

    repo = _repo(tmp_path)
    checkpoint_id = _checkpoint(repo)
    handle = _ledger(repo)
    ctx = multiprocessing.get_context("fork")
    ready_event = ctx.Event()
    proc = ctx.Process(target=_mp_append_worker_gated, args=(handle.canonical_path, ready_event))
    proc.start()

    real_git = sgr._git

    def _spy_git(repository_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if args and args[0] == "checkout":
            ready_event.set()  # type: ignore[attr-defined]
        return real_git(repository_root, *args)

    monkeypatch.setattr(sgr, "_git", _spy_git)  # type: ignore[attr-defined]

    result = rollback_to_checkpoint(repo, handle, checkpoint_id, _RUN)
    assert result.status is RollbackStatus.RESTORED

    proc.join(timeout=30)
    assert proc.exitcode == 0

    # Both the pre-existing entry and the concurrent process's entry survive
    # (not lost by the ledger-restore-write); `rollback_to_checkpoint` also
    # appends its own rollback-event entry after the preserve window.
    ledger = read_ledger(handle)
    action_ids = {entry.action_id for entry in ledger}
    assert {"act-pre", "act-concurrent"} <= action_ids
    assert len(ledger) == 3
    assert verify_chain(ledger).status is VerificationStatus.VALID

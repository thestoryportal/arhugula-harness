"""B-104 Task 6a: claim-scoped audited recovery of one exact resume claim.

Provider-free. Every case runs over a real verified external state root in a scratch
directory (the S3 placed-root fixture), a real claim store and the real durable IS audit
writer. Crash points are simulated by failing the sync at that boundary, which leaves the
same on-disk state a process death there would; the same request is then retried.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_core import JournalRecordRef
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import QuiescenceAttestation
from harness_is.state_ledger_write import RecoveryAuditDurabilityError, read_ledger
from harness_runtime.admin import pause_claim_recovery as recovery_module
from harness_runtime.admin.pause_claim_recovery import (
    ClaimAbandon,
    ClaimRelease,
    PauseClaimRecovery,
    RecoveryOutcome,
)
from harness_runtime.config.state_placement import MARKER_NAME, StateRootPlacementError
from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError, started_frame

from .test_b104_resume_claim_store import Placed, _capture
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)
from .test_state_placement_bootstrap import Site

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")

UID = 1000
REASON = "d" * 64
OTHER_REASON = "e" * 64


@pytest.fixture
def placed(world: Path) -> Placed:  # noqa: F811
    """A verified external state root with the pause journal directory under it."""
    site = Site(world / "site")
    config = site.config(placement=True)
    journal_dir = site.root / "state-ledger" / "pause-journal"
    stamp = site.stamp(config)
    journal_dir.mkdir(parents=True, mode=0o700)
    return Placed(site, config, stamp, journal_dir)


def _ledger(placed: Placed) -> JsonlLedgerHandle:
    return JsonlLedgerHandle(
        canonical_path=placed.site.root / "state-ledger" / "state.jsonl",
        exists=False,
        entry_count=0,
    )


def _recovery(placed: Placed) -> PauseClaimRecovery:
    return PauseClaimRecovery(placement=placed.placement(), tenant_id=None, ledger=_ledger(placed))


def _attestation() -> QuiescenceAttestation:
    return QuiescenceAttestation(
        operator_uid=UID,
        attested_at=datetime(2026, 9, 25, tzinfo=UTC),
        stopped_services_digest="a" * 64,
        no_workers_observed=True,
        restart_disabled=True,
    )


def _release(ref: JournalRecordRef, action_id: str = "rel-1", reason: str = REASON) -> ClaimRelease:
    return ClaimRelease(record_ref=ref, action_id=action_id, operator_uid=UID, reason_digest=reason)


def _abandon(ref: JournalRecordRef, action_id: str = "abn-1") -> ClaimAbandon:
    return ClaimAbandon(
        record_ref=ref,
        action_id=action_id,
        operator_uid=UID,
        reason_digest=REASON,
        quiescence_attestation=_attestation(),
    )


def _claimed(placed: Placed) -> JournalRecordRef:
    """A current record with a complete, unstarted claim whose holder has exited."""
    ref = _capture(placed.journal_dir)
    with placed.store().claim(ref):
        pass
    return ref


def _audits(placed: Placed) -> list[tuple[str, str, str]]:
    handle = _ledger(placed)
    if not handle.canonical_path.exists():
        return []
    return [
        (
            e.recovery_audit.phase,
            e.recovery_audit.action_id,
            getattr(e.recovery_audit, "transition_kind", "-"),
        )
        for e in read_ledger(handle)
        if e.recovery_audit is not None
    ]


def _tree(path: Path) -> list[tuple[str, int, int, bytes]]:
    return sorted(
        (
            str(p.relative_to(path)),
            p.lstat().st_ino,
            p.lstat().st_size,
            p.read_bytes() if p.is_file() else b"",
        )
        for p in path.rglob("*")
        if not p.name.endswith(".lock")
    )


def _archives(placed: Placed, ref: JournalRecordRef) -> list[Path]:
    paths = placed.store().paths_for(ref)
    return sorted(
        p for p in placed.journal_dir.iterdir() if p.name.startswith(paths.archive_prefix)
    )


def _tombstones(placed: Placed, ref: JournalRecordRef) -> list[Path]:
    paths = placed.store().paths_for(ref)
    return sorted(
        p for p in placed.journal_dir.iterdir() if p.name.startswith(paths.tombstone_prefix)
    )


def _fail_nth_dir_sync(monkeypatch: pytest.MonkeyPatch, n: int) -> None:
    """Make the coordinator's n-th directory fsync fail (a crash at that boundary)."""
    original: Callable[[Path], None] = recovery_module._fsync_dir
    calls = 0

    def failing(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == n:
            raise OSError("injected directory fsync failure")
        original(path)

    monkeypatch.setattr(recovery_module, "_fsync_dir", failing)


def _fail_nth_audit_sync(monkeypatch: pytest.MonkeyPatch, n: int) -> None:
    """Make the n-th durable audit append's file fsync fail (after its line is written)."""
    import harness_is.state_ledger_write as writer

    original = writer._fsync_recovery_target
    appends = 0

    def failing(fd: int) -> None:
        nonlocal appends
        import os
        import stat

        if stat.S_ISREG(os.fstat(fd).st_mode):
            appends += 1
            if appends == n:
                raise OSError("injected audit fsync failure")
        original(fd)

    monkeypatch.setattr(writer, "_fsync_recovery_target", failing)


# --- release of an unstarted claim, and the C1 crash matrix --------------------------------


def test_release_archives_the_claim_and_a_later_claim_c2_is_admitted(placed: Placed) -> None:
    ref = _claimed(placed)
    store = placed.store()
    paths = store.paths_for(ref)
    claim_ino = paths.claim.stat().st_ino

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.RELEASED
    assert not paths.claim.exists()
    [archive] = _archives(placed, ref)
    assert archive.stat().st_ino == claim_ino
    assert paths.lease.exists()
    assert _audits(placed) == [("intent", "rel-1", "-"), ("complete", "rel-1", "release_archive")]

    # C1's archive is history: a new claim C2 of the same record is admitted and can be
    # recovered under its own action, with the C1 archive still present.
    with store.claim(ref):
        pass
    c2 = _recovery(placed).recover(_abandon(ref, "abn-c2"))
    assert c2.outcome is RecoveryOutcome.ABANDONED
    assert _archives(placed, ref) == [archive]


def test_completed_action_retry_is_idempotent(placed: Placed) -> None:
    ref = _claimed(placed)
    assert _recovery(placed).recover(_release(ref)).outcome is RecoveryOutcome.RELEASED
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()
    assert _recovery(placed).recover(_release(ref)).outcome is RecoveryOutcome.RELEASED
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes


@pytest.mark.parametrize(
    ("fail", "left_behind"),
    [
        ("intent-sync", "intent written, live only"),
        ("link-sync", "live + archive"),
        ("unlink-sync", "archive only"),
        ("complete-sync", "complete written"),
    ],
)
def test_release_crash_at_every_sync_boundary_then_retry_releases(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, fail: str, left_behind: str
) -> None:
    ref = _claimed(placed)
    paths = placed.store().paths_for(ref)
    claim_ino = paths.claim.stat().st_ino
    with monkeypatch.context() as patch:
        if fail == "intent-sync":
            _fail_nth_audit_sync(patch, 1)
        elif fail == "link-sync":
            _fail_nth_dir_sync(patch, 1)
        elif fail == "unlink-sync":
            _fail_nth_dir_sync(patch, 2)
        else:
            _fail_nth_audit_sync(patch, 2)
        # A real durability failure surfaces; it is never reported as an outcome.
        with pytest.raises((OSError, RecoveryAuditDurabilityError)):
            _recovery(placed).recover(_release(ref))

    if left_behind == "live + archive":
        assert paths.claim.exists() and _archives(placed, ref)
    if left_behind == "archive only":
        assert not paths.claim.exists() and _archives(placed, ref)

    result = _recovery(placed).recover(_release(ref))
    assert result.outcome is RecoveryOutcome.RELEASED
    assert not paths.claim.exists()
    [archive] = _archives(placed, ref)
    assert archive.stat().st_ino == claim_ino
    assert _audits(placed) == [("intent", "rel-1", "-"), ("complete", "rel-1", "release_archive")]


# --- abandon: terminal tombstone -------------------------------------------------------------


def test_abandon_of_a_begun_claim_tombstones_the_record_and_bars_admission(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref) as held:
        started = started_frame(held)
    paths = store.paths_for(ref)
    with paths.claim.open("ab") as claim:
        claim.write(started)
    claim_bytes = paths.claim.read_bytes()

    result = _recovery(placed).recover(_abandon(ref))

    assert result.outcome is RecoveryOutcome.ABANDONED
    assert len(_tombstones(placed, ref)) == 1
    assert paths.claim.read_bytes() == claim_bytes  # original claim preserved
    assert paths.lease.exists()
    assert _audits(placed) == [("intent", "abn-1", "-"), ("complete", "abn-1", "claim_tombstone")]
    with pytest.raises(ClaimRefusedError):
        store.claim(ref)


def test_abandon_crash_after_tombstone_then_retry_completes(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _claimed(placed)
    with monkeypatch.context() as patch:
        _fail_nth_dir_sync(patch, 1)
        with pytest.raises(OSError):
            _recovery(placed).recover(_abandon(ref))
    assert len(_tombstones(placed, ref)) == 1
    assert _recovery(placed).recover(_abandon(ref)).outcome is RecoveryOutcome.ABANDONED
    assert len(_tombstones(placed, ref)) == 1
    assert _audits(placed) == [("intent", "abn-1", "-"), ("complete", "abn-1", "claim_tombstone")]


def test_release_of_a_begun_claim_is_held_without_audit(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref) as held:
        started = started_frame(held)
    with store.paths_for(ref).claim.open("ab") as claim:
        claim.write(started)
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


# --- contention, conflicts, integrity -------------------------------------------------------


def test_live_lease_holder_is_retryable_contention_with_no_intent(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    with placed.store().claim(ref):
        result = _recovery(placed).recover(_release(ref))
    assert result.outcome is RecoveryOutcome.RETRYABLE_CONTENTION
    assert _audits(placed) == []


def test_same_action_with_a_different_payload_is_an_integrity_fault(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _claimed(placed)
    with monkeypatch.context() as patch:
        _fail_nth_dir_sync(patch, 1)
        with pytest.raises(OSError):
            _recovery(placed).recover(_release(ref))
    before = _tree(placed.journal_dir)
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()

    result = _recovery(placed).recover(_release(ref, reason=OTHER_REASON))

    assert result.outcome is RecoveryOutcome.INTEGRITY_FAULT
    assert _tree(placed.journal_dir) == before
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes


def test_torn_ledger_refuses_before_any_transition(placed: Placed) -> None:
    ref = _claimed(placed)
    ledger = _ledger(placed).canonical_path
    ledger.write_bytes(b'{"action_id": "torn')
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.INTEGRITY_FAULT
    assert _tree(placed.journal_dir) == before
    assert ledger.read_bytes() == b'{"action_id": "torn'


def test_a_second_action_on_a_claim_with_a_pending_intent_is_held(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _claimed(placed)
    with monkeypatch.context() as patch:
        _fail_nth_dir_sync(patch, 1)
        with pytest.raises(OSError):
            _recovery(placed).recover(_abandon(ref))
    audits = _audits(placed)

    result = _recovery(placed).recover(_release(ref, action_id="rel-other"))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == audits


def test_terminal_tombstone_takes_precedence_over_a_new_release(placed: Placed) -> None:
    ref = _claimed(placed)
    assert _recovery(placed).recover(_abandon(ref)).outcome is RecoveryOutcome.ABANDONED
    audits = _audits(placed)

    result = _recovery(placed).recover(_release(ref, action_id="rel-after"))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == audits


def test_a_foreign_tombstone_holds_a_release_without_audit(placed: Placed) -> None:
    ref = _claimed(placed)
    paths = placed.store().paths_for(ref)
    (placed.journal_dir / (paths.tombstone_prefix + "record-scope")).write_bytes(b"terminal\n")

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []


# --- pending INTENT: lost evidence is a permanent hold, never COMPLETE/none ------------------


def _pending_release_intent(placed: Placed, monkeypatch: pytest.MonkeyPatch) -> JournalRecordRef:
    """A durable release INTENT with no transition (crash before the archive link)."""
    ref = _claimed(placed)
    original_link = recovery_module._link_archive

    def crash(*_args: object) -> None:
        raise OSError("injected crash before the archive link")

    monkeypatch.setattr(recovery_module, "_link_archive", crash)
    with pytest.raises(OSError):
        _recovery(placed).recover(_release(ref))
    monkeypatch.setattr(recovery_module, "_link_archive", original_link)
    assert _audits(placed) == [("intent", "rel-1", "-")]
    return ref


@pytest.mark.parametrize("damage", ["missing", "invalid", "replaced"])
def test_lost_lease_evidence_under_a_pending_intent_is_held_untouched(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    ref = _pending_release_intent(placed, monkeypatch)
    store = placed.store()
    lease = store.paths_for(ref).lease
    if damage == "missing":
        lease.unlink()
    elif damage == "invalid":
        lease.write_bytes(b"not a lease\n")
    else:
        # A valid, canonical lease of a different generation on a new inode.
        lease.unlink()
        lease.write_bytes(store._lease_bytes(ref, "9" * 32))
    before = _tree(placed.journal_dir)
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _tree(placed.journal_dir) == before
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes


def test_changed_claim_bytes_under_a_pending_intent_are_held(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _pending_release_intent(placed, monkeypatch)
    claim = placed.store().paths_for(ref).claim
    claim.write_bytes(claim.read_bytes() + b"x")
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes


def test_pending_intent_whose_precondition_failed_completes_none_then_abandon_may_follow(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _pending_release_intent(placed, monkeypatch)
    paths = placed.store().paths_for(ref)
    claim_bytes = paths.claim.read_bytes()
    _capture(placed.journal_dir)  # the record is no longer the current one: release is moot

    result = _recovery(placed).recover(_release(ref))

    assert result.outcome is RecoveryOutcome.COMPLETED_NONE
    assert paths.claim.read_bytes() == claim_bytes
    assert _archives(placed, ref) == []
    assert _audits(placed) == [("intent", "rel-1", "-"), ("complete", "rel-1", "none")]

    followed = _recovery(placed).recover(_abandon(ref, "abn-after-none"))
    assert followed.outcome is RecoveryOutcome.ABANDONED


# --- record-scoped states are not claim-scoped recovery --------------------------------------


@pytest.mark.parametrize("state", ["lease-missing", "no-token-claim", "claim-absent"])
def test_record_scoped_states_are_held_without_audit(placed: Placed, state: str) -> None:
    ref = _claimed(placed)
    paths = placed.store().paths_for(ref)
    if state == "lease-missing":
        paths.lease.unlink()
    elif state == "no-token-claim":
        paths.claim.write_bytes(b"partial")
    else:
        paths.claim.unlink()
    before = _tree(placed.journal_dir)

    for request in (_release(ref), _abandon(ref)):
        result = _recovery(placed).recover(request)
        assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


def test_a_replaced_state_root_refuses_as_a_placement_fault(placed: Placed) -> None:
    ref = _claimed(placed)
    (placed.site.root / MARKER_NAME).write_text("f" * 32)
    with pytest.raises(StateRootPlacementError):
        _recovery(placed).recover(_release(ref))
    assert _audits(placed) == []


def test_intent_and_complete_pin_the_exact_claim_and_lease_identity(placed: Placed) -> None:
    import hashlib
    import json

    ref = _claimed(placed)
    paths = placed.store().paths_for(ref)
    claim_bytes = paths.claim.read_bytes()
    claim_st = paths.claim.stat()
    lease_st = paths.lease.stat()
    lease_token = json.loads(paths.lease.read_bytes())["token"]

    assert _recovery(placed).recover(_release(ref)).outcome is RecoveryOutcome.RELEASED

    [intent, complete] = [
        e.recovery_audit for e in read_ledger(_ledger(placed)) if e.recovery_audit is not None
    ]
    assert intent.observation == complete.observation
    assert intent.subject_id == complete.subject_id
    observed = intent.observation
    assert observed.claim_bytes_digest == hashlib.sha256(claim_bytes).hexdigest()
    assert observed.canonical_claim_path == str(paths.claim)
    assert (observed.claim_st_dev, observed.claim_st_ino) == (claim_st.st_dev, claim_st.st_ino)
    assert observed.lease_generation == lease_token
    assert (observed.lease_st_dev, observed.lease_st_ino) == (lease_st.st_dev, lease_st.st_ino)
    assert intent.quiescence_attestation is None  # a release never carries one


def test_one_open_action_per_claim_even_with_evidence_intact(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _pending_release_intent(placed, monkeypatch)
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_abandon(ref, "abn-while-pending"))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == [("intent", "rel-1", "-")]
    assert _tree(placed.journal_dir) == before

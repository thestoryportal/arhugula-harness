"""B-104 Task 6b phase A: audited record-scoped terminal abandon.

Provider-free, over the same real placed state root, claim store and durable IS audit
writer as the Task 6a claim-scoped tests. Only the three representable record
observations are abandoned here: claim absent, claim present without a parseable token,
and claim unreadable. A claim WITH a parseable token is claim-scoped work, and a token
claim whose lease is missing or invalid stays held for a later phase.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest
from harness_core import JournalRecordRef
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import (
    Identifier,
    RecordCompleteAudit,
    RecordIntentAudit,
)
from harness_is.state_ledger_write import RecoveryAuditDurabilityError, read_ledger
from harness_runtime.admin import pause_claim_recovery as recovery_module
from harness_runtime.admin.pause_claim_recovery import (
    ClaimAbandon,
    ClaimRelease,
    RecordAbandon,
    RecoveryOutcome,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError, started_frame

from . import test_b104_pause_claim_recovery as claim_recovery_tests
from .test_b104_pause_claim_recovery import (
    OTHER_REASON,
    REASON,
    UID,
    _attestation,
    _audits,
    _fail_nth_audit_sync,
    _fail_nth_dir_sync,
    _failing_file_sync,
    _ledger,
    _record_syncs,
    _recovery,
    _tombstones,
    _tree,
)
from .test_b104_resume_claim_store import Placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

placed = claim_recovery_tests.placed  # the Task 6a placed-root fixture, shared unchanged

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")

STATES = ["claim_absent", "claim_no_token", "claim_unreadable"]


def _capture(root: Path, workflow_id: str = "wf-claim") -> JournalRecordRef:
    snapshot = PauseSnapshot(
        workflow_id=workflow_id,
        run_id="run-1",
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
    return JournalWorkflowPauseStore(journal_dir=root, tenant_id=None).capture(snapshot, depth=0)


def _record_abandon(
    ref: JournalRecordRef, action_id: str = "rec-1", reason: str = REASON
) -> RecordAbandon:
    return RecordAbandon(
        record_ref=ref,
        action_id=action_id,
        operator_uid=UID,
        reason_digest=reason,
        quiescence_attestation=_attestation(),
    )


def _in_state(placed: Placed, state: str) -> JournalRecordRef:
    """A record in one of the three record-scoped states, with no live holder."""
    ref = _capture(placed.journal_dir)
    if state == "claim_absent":
        return ref
    store = placed.store()
    with store.claim(ref):
        pass
    claim = store.paths_for(ref).claim
    if state == "claim_no_token":
        claim.write_bytes(b'{"version":1,"phase":"claimed","tok')  # a torn claimed frame
    else:
        claim.unlink()
        claim.symlink_to(store.paths_for(ref).lease)  # O_NOFOLLOW cannot read it
    return ref


def _record_entries(placed: Placed) -> list[RecordIntentAudit | RecordCompleteAudit]:
    return [
        e.recovery_audit
        for e in read_ledger(_ledger(placed))
        if isinstance(e.recovery_audit, RecordIntentAudit | RecordCompleteAudit)
    ]


def _files(path: Path) -> dict[str, tuple[int, bytes]]:
    """Claim/lease evidence by name: inode and bytes (a symlink by its target)."""
    out: dict[str, tuple[int, bytes]] = {}
    for p in path.iterdir():
        st = p.lstat()
        out[p.name] = (
            st.st_ino,
            os.readlink(p).encode() if p.is_symlink() else p.read_bytes() if p.is_file() else b"",
        )
    return out


def _pending_record_intent(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, state: str
) -> JournalRecordRef:
    """A durable record INTENT with no tombstone (crash before the tombstone is created)."""
    ref = _in_state(placed, state)

    def crash(*_args: object) -> None:
        raise OSError("injected crash before the tombstone")

    with monkeypatch.context() as patch:
        patch.setattr(recovery_module, "_write_new_file", crash)
        with pytest.raises(OSError):
            _recovery(placed).recover(_record_abandon(ref))
    assert _audits(placed) == [("intent", "rec-1", "-")]
    assert _tombstones(placed, ref) == []
    return ref


# --- the three observations are abandoned, audited and evidence-preserving -------------------


@pytest.mark.parametrize("state", STATES)
def test_record_abandon_tombstones_each_observation_and_preserves_evidence(
    placed: Placed, state: str
) -> None:
    ref = _in_state(placed, state)
    store = placed.store()
    paths = store.paths_for(ref)
    evidence_before = {
        k: v
        for k, v in _files(placed.journal_dir).items()
        if k in (paths.claim.name, paths.lease.name)
    }

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.ABANDONED
    assert len(_tombstones(placed, ref)) == 1
    after = _files(placed.journal_dir)
    assert {k: after[k] for k in evidence_before} == evidence_before  # claim/lease untouched
    assert _audits(placed) == [("intent", "rec-1", "-"), ("complete", "rec-1", "record_tombstone")]
    intent, complete = _record_entries(placed)
    assert intent.observation == complete.observation
    assert intent.observation.kind == state
    assert intent.quiescence_attestation == _attestation()
    with pytest.raises(ClaimRefusedError):
        store.claim(ref)


@pytest.mark.parametrize("state", STATES)
def test_the_intent_pins_the_exact_observed_path_parent_and_claim(
    placed: Placed, state: str
) -> None:
    ref = _in_state(placed, state)
    paths = placed.store().paths_for(ref)
    parent = placed.journal_dir.stat()

    assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED

    observed = _record_entries(placed)[0].observation
    assert observed.canonical_claim_path == str(paths.claim)
    assert (observed.parent_st_dev, observed.parent_st_ino) == (parent.st_dev, parent.st_ino)
    if state != "claim_absent":
        claim = paths.claim.lstat()
        assert (observed.claim_st_dev, observed.claim_st_ino) == (claim.st_dev, claim.st_ino)  # type: ignore[union-attr]
    if state == "claim_no_token":
        assert observed.raw_digest == hashlib.sha256(paths.claim.read_bytes()).hexdigest()  # type: ignore[union-attr]


def test_a_no_token_claim_with_a_missing_lease_is_abandoned(placed: Placed) -> None:
    ref = _in_state(placed, "claim_no_token")
    placed.store().paths_for(ref).lease.unlink()
    assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED


def test_the_tombstone_bars_the_exact_record_but_not_a_sibling_or_a_later_record(
    placed: Placed,
) -> None:
    ref = _capture(placed.journal_dir)
    sibling = _capture(placed.journal_dir, "wf-sibling")
    store = placed.store()

    assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED

    with pytest.raises(ClaimRefusedError):
        store.claim(ref)
    with store.claim(sibling):
        pass
    later = _capture(placed.journal_dir)
    with store.claim(later):
        pass


# --- C1 released, then later C2/no-token state -----------------------------------------------


@pytest.mark.parametrize("c2", ["claim_absent", "claim_no_token"])
def test_a_released_c1_archive_does_not_block_record_abandon_of_later_state(
    placed: Placed, c2: str
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref):
        pass
    c1 = _recovery(placed).recover(ClaimRelease(ref, "rel-c1", UID, REASON))
    assert c1.outcome is RecoveryOutcome.RELEASED
    paths = store.paths_for(ref)
    [archive] = [p for p in placed.journal_dir.iterdir() if p.name.startswith(paths.archive_prefix)]
    archived = archive.read_bytes()
    if c2 == "claim_no_token":
        with store.claim(ref):
            pass
        paths.claim.write_bytes(b"torn")

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.ABANDONED
    assert archive.read_bytes() == archived


@pytest.mark.parametrize("state", STATES)
def test_an_archive_without_a_completed_claim_release_holds(placed: Placed, state: str) -> None:
    ref = _in_state(placed, state)
    paths = placed.store().paths_for(ref)
    (placed.journal_dir / (paths.archive_prefix + "f" * 64)).write_bytes(b"orphan\n")
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


# --- attestation, record identity and scope boundaries ---------------------------------------


def test_a_missing_or_forged_attestation_is_refused_at_the_request_boundary(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    forged = [
        None,
        _attestation().model_dump(),  # an untyped look-alike
        _attestation().model_copy(update={"operator_uid": UID + 1}),  # another operator's
    ]
    for attestation in forged:
        with pytest.raises((TypeError, ValueError)):
            RecordAbandon(
                record_ref=ref,
                action_id="rec-forged",
                operator_uid=UID,
                reason_digest=REASON,
                quiescence_attestation=attestation,  # type: ignore[arg-type]
            )
    assert _tombstones(placed, ref) == []


@pytest.mark.parametrize(
    "mismatch", [{"snapshot_hash": "f" * 64}, {"run_id": "run-other"}, {"record_count": 2}]
)
def test_a_ref_that_does_not_match_the_journal_is_held(
    placed: Placed, mismatch: dict[str, object]
) -> None:
    ref = _capture(placed.journal_dir).model_copy(update=mismatch)
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


def test_abandoning_one_record_leaves_its_sibling_claim_untouched(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    sibling = _capture(placed.journal_dir, "wf-sibling")
    store = placed.store()
    with store.claim(sibling):
        pass
    sibling_claim = store.paths_for(sibling).claim.read_bytes()

    assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED

    assert store.paths_for(sibling).claim.read_bytes() == sibling_claim
    assert _tombstones(placed, sibling) == []
    assert _recovery(placed).recover(ClaimRelease(sibling, "rel-s", UID, REASON)).outcome is (
        RecoveryOutcome.RELEASED
    )


@pytest.mark.parametrize("phase", ["unstarted", "started"])
def test_a_claim_with_a_token_and_valid_lease_is_claim_scoped_not_record_scoped(
    placed: Placed, phase: str
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref) as held:
        started = started_frame(held)
    if phase == "started":
        with store.paths_for(ref).claim.open("ab") as claim:
            claim.write(started)
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert result.reason.startswith("claim-scope-required")
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


@pytest.mark.parametrize("damage", ["missing", "invalid"])
def test_a_token_claim_with_a_missing_or_invalid_lease_stays_held_for_phase_b(
    placed: Placed, damage: str
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref):
        pass
    lease = store.paths_for(ref).lease
    lease.unlink()
    if damage == "invalid":
        lease.write_bytes(b"not a lease\n")
    before = _tree(placed.journal_dir)

    for request in (
        _record_abandon(ref),
        ClaimAbandon(ref, "abn-1", UID, REASON, _attestation()),
    ):
        result = _recovery(placed).recover(request)
        assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


def test_a_live_lease_holder_is_retryable_contention_with_no_intent(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref):
        store.paths_for(ref).claim.write_bytes(b"torn while the worker runs")
        result = _recovery(placed).recover(_record_abandon(ref))
    assert result.outcome is RecoveryOutcome.RETRYABLE_CONTENTION
    assert _audits(placed) == []
    assert _tombstones(placed, ref) == []


@pytest.mark.skipif(not os.path.isdir("/proc/self/fd"), reason="fd cleanup is read from /proc")
@pytest.mark.parametrize("kind", ["empty", "garbage", "noncanonical"])
def test_a_live_holder_with_a_damaged_lease_and_no_token_claim_is_contention_not_a_tombstone(
    placed: Placed, kind: str
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    paths = store.paths_for(ref)
    with store.claim(ref):
        paths.claim.write_bytes(b'{"version":1,"phase":"claimed","tok')  # a torn, tokenless claim
        canonical = paths.lease.read_bytes()
        paths.lease.write_bytes(
            {"empty": b"", "garbage": b"not a lease\n", "noncanonical": canonical[:-1] + b"  \n"}[
                kind
            ]
        )
        before = _tree(placed.journal_dir)
        fds_before = len(os.listdir("/proc/self/fd"))

        result = _recovery(placed).recover(_record_abandon(ref))

        assert result.outcome is RecoveryOutcome.RETRYABLE_CONTENTION
        assert _audits(placed) == []  # zero INTENT / COMPLETE
        assert _tombstones(placed, ref) == []
        assert _tree(placed.journal_dir) == before
        assert len(os.listdir("/proc/self/fd")) == fds_before

    # The worker is gone: the same damaged lease is now free and invalid, and the record
    # transition proceeds under the existing record-scope rule.
    after = _recovery(placed).recover(_record_abandon(ref))

    assert after.outcome is RecoveryOutcome.ABANDONED
    assert len(_tombstones(placed, ref)) == 1
    assert _audits(placed) == [("intent", "rec-1", "-"), ("complete", "rec-1", "record_tombstone")]
    assert _record_entries(placed)[0].observation.kind == "claim_no_token"


def test_a_live_holder_with_a_damaged_lease_is_contention_for_a_claim_scoped_abandon(
    placed: Placed,
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref):
        store.paths_for(ref).lease.write_bytes(b"not a lease\n")
        before = _tree(placed.journal_dir)

        result = _recovery(placed).recover(ClaimAbandon(ref, "abn-1", UID, REASON, _attestation()))

        assert result.outcome is RecoveryOutcome.RETRYABLE_CONTENTION
        assert _audits(placed) == []
        assert _tree(placed.journal_dir) == before


# --- idempotency and conflicts ---------------------------------------------------------------


@pytest.mark.parametrize("state", STATES)
def test_a_duplicate_replay_converges_without_new_audit(placed: Placed, state: str) -> None:
    ref = _in_state(placed, state)
    assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()
    tree = _tree(placed.journal_dir)

    again = _recovery(placed).recover(_record_abandon(ref))

    assert again.outcome is RecoveryOutcome.ABANDONED
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes
    assert _tree(placed.journal_dir) == tree


@pytest.mark.parametrize("stage", ["pending", "complete"])
def test_the_same_action_with_a_changed_payload_is_an_integrity_fault(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    if stage == "pending":
        ref = _pending_record_intent(placed, monkeypatch, "claim_no_token")
    else:
        ref = _in_state(placed, "claim_no_token")
        assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()
    tree = _tree(placed.journal_dir)

    changed = _recovery(placed).recover(_record_abandon(ref, reason=OTHER_REASON))
    # The same action ID reused as a claim-scoped action is a changed payload too.
    rescoped = _recovery(placed).recover(ClaimAbandon(ref, "rec-1", UID, REASON, _attestation()))

    assert changed.outcome is RecoveryOutcome.INTEGRITY_FAULT
    assert rescoped.outcome is RecoveryOutcome.INTEGRITY_FAULT
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes
    assert _tree(placed.journal_dir) == tree


def test_a_torn_ledger_refuses_before_any_transition(placed: Placed) -> None:
    ref = _in_state(placed, "claim_no_token")
    ledger = _ledger(placed).canonical_path
    ledger.write_bytes(b'{"action_id": "torn')
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.INTEGRITY_FAULT
    assert _tree(placed.journal_dir) == before
    assert ledger.read_bytes() == b'{"action_id": "torn'


# --- retry after every durable transition boundary ------------------------------------------


@pytest.mark.parametrize(
    "fail",
    [
        "intent-sync",
        "tombstone-create",
        "tombstone-file-sync",
        "tombstone-dir-sync",
        "complete-sync",
    ],
)
@pytest.mark.parametrize("state", STATES)
def test_a_crash_at_every_durable_boundary_then_retry_abandons(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, state: str, fail: str
) -> None:
    ref = _in_state(placed, state)
    with monkeypatch.context() as patch:
        if fail == "intent-sync":
            _fail_nth_audit_sync(patch, 1)
        elif fail == "tombstone-create":

            def crash(*_args: object) -> None:
                raise OSError("injected crash before the tombstone")

            patch.setattr(recovery_module, "_write_new_file", crash)
        elif fail == "tombstone-file-sync":
            patch.setattr(recovery_module, "_fsync_file", _failing_file_sync)
        elif fail == "tombstone-dir-sync":
            _fail_nth_dir_sync(patch, 1)
        else:
            _fail_nth_audit_sync(patch, 2)
        with pytest.raises((OSError, RecoveryAuditDurabilityError)):
            _recovery(placed).recover(_record_abandon(ref))

    with monkeypatch.context() as patch:
        events = _record_syncs(patch)
        result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.ABANDONED
    assert len(_tombstones(placed, ref)) == 1
    assert _audits(placed) == [("intent", "rec-1", "-"), ("complete", "rec-1", "record_tombstone")]
    if fail != "complete-sync":
        # INTENT re-synced, then the tombstone file and its directory, then COMPLETE.
        assert events == ["ledger", "file", "dir", "ledger"]


def test_a_first_abandon_syncs_intent_tombstone_file_dir_then_complete(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _in_state(placed, "claim_absent")
    with monkeypatch.context() as patch:
        events = _record_syncs(patch)
        assert _recovery(placed).recover(_record_abandon(ref)).outcome is RecoveryOutcome.ABANDONED
    assert events == ["ledger", "file", "dir", "ledger"]


# --- tombstones: precedence, foreign bytes, appearance under a pending INTENT ----------------


def test_an_existing_tombstone_holds_a_new_record_abandon_without_audit(placed: Placed) -> None:
    ref = _in_state(placed, "claim_absent")
    paths = placed.store().paths_for(ref)
    (placed.journal_dir / (paths.tombstone_prefix + "foreign")).write_bytes(b"terminal\n")
    before = _tree(placed.journal_dir)

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == []
    assert _tree(placed.journal_dir) == before


def test_foreign_bytes_at_the_record_tombstone_are_an_integrity_fault(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _in_state(placed, "claim_no_token")
    with monkeypatch.context() as patch:
        patch.setattr(recovery_module, "_fsync_file", _failing_file_sync)
        with pytest.raises(OSError):
            _recovery(placed).recover(_record_abandon(ref))
    [tombstone] = _tombstones(placed, ref)
    tombstone.write_bytes(b"not ours\n")
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.INTEGRITY_FAULT
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes


def test_a_tombstone_appearing_under_a_pending_intent_is_held(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _pending_record_intent(placed, monkeypatch, "claim_absent")
    paths = placed.store().paths_for(ref)
    (placed.journal_dir / (paths.tombstone_prefix + "foreign")).write_bytes(b"terminal\n")
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes


# --- changed or lost evidence under a pending INTENT is a permanent hold ---------------------


def _replace_parent(placed: Placed) -> None:
    """Swap the journal directory for a copy: same names and bytes, different inode."""
    old = placed.journal_dir.with_name("pause-journal.old")
    placed.journal_dir.rename(old)
    placed.journal_dir.mkdir(mode=0o700)
    for p in old.iterdir():
        if p.is_symlink():
            (placed.journal_dir / p.name).symlink_to(os.readlink(p))
        elif p.is_file():
            (placed.journal_dir / p.name).write_bytes(p.read_bytes())


@pytest.mark.parametrize(
    ("state", "change"),
    [
        ("claim_absent", "claim-appears"),
        ("claim_absent", "parent-replaced"),
        ("claim_no_token", "bytes-changed"),
        ("claim_no_token", "inode-replaced"),
        ("claim_no_token", "claim-removed"),
        ("claim_no_token", "parent-replaced"),
        ("claim_unreadable", "inode-replaced"),
        ("claim_unreadable", "claim-removed"),
        ("claim_no_token", "journal-lost"),
    ],
)
def test_changed_or_lost_evidence_under_a_pending_intent_is_a_permanent_hold(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, state: str, change: str
) -> None:
    ref = _pending_record_intent(placed, monkeypatch, state)
    paths = placed.store().paths_for(ref)
    claim = paths.claim
    if change == "claim-appears":
        with placed.store().claim(ref):
            pass
    elif change == "bytes-changed":
        with claim.open("ab") as f:
            f.write(b"x")
    elif change == "inode-replaced":
        original = claim.lstat()
        target = os.readlink(claim) if claim.is_symlink() else None
        data = None if target else claim.read_bytes()
        replacement = claim.with_name(f"{claim.name}.replacement")
        if target:
            replacement.symlink_to(target)
        else:
            replacement.write_bytes(data or b"")
        os.replace(replacement, claim)
        current = claim.lstat()
        assert (current.st_dev, current.st_ino) != (original.st_dev, original.st_ino)
    elif change == "claim-removed":
        claim.unlink()
    elif change == "parent-replaced":
        _replace_parent(placed)
    else:
        paths.journal.write_bytes(b"")
    ledger_bytes = _ledger(placed).canonical_path.read_bytes()

    for _ in range(2):  # permanent: a second retry is held the same way
        result = _recovery(placed).recover(_record_abandon(ref))
        assert result.outcome is RecoveryOutcome.HELD
    assert _ledger(placed).canonical_path.read_bytes() == ledger_bytes
    assert _tombstones(placed, ref) == []


# --- one open action per record across scopes ------------------------------------------------


def test_a_pending_claim_action_holds_a_record_abandon(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref):
        pass
    with monkeypatch.context() as patch:
        _fail_nth_dir_sync(patch, 1)  # the claim-scoped tombstone's directory sync
        with pytest.raises(OSError):
            _recovery(placed).recover(ClaimAbandon(ref, "abn-1", UID, REASON, _attestation()))
    for tombstone in _tombstones(placed, ref):
        tombstone.unlink()  # leave only the pending claim INTENT
    store.paths_for(ref).claim.write_bytes(b"torn")
    audits = _audits(placed)

    result = _recovery(placed).recover(_record_abandon(ref))

    assert result.outcome is RecoveryOutcome.HELD
    assert _audits(placed) == audits


def test_a_pending_record_action_holds_claim_scoped_and_other_record_actions(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _pending_record_intent(placed, monkeypatch, "claim_absent")
    with placed.store().claim(ref):  # a claimant ignoring the operator's restart hold
        pass
    audits = _audits(placed)
    before = _tree(placed.journal_dir)

    for request in (
        ClaimAbandon(ref, "abn-c2", UID, REASON, _attestation()),
        ClaimRelease(ref, "rel-c2", UID, REASON),
        _record_abandon(ref, "rec-2"),
    ):
        assert _recovery(placed).recover(request).outcome is RecoveryOutcome.HELD
    assert _audits(placed) == audits
    assert _tree(placed.journal_dir) == before

"""B-104 Task 5a: the durable ``started`` transition and typed recency admission.

Claim-store seam only: nothing here resumes a body, wires `api.resume`, or recovers a claim.
Ordering is proven against the real code path (the actual `os.write` / `os.fsync` calls on
the claim descriptor), not just serialized bytes.
"""

from __future__ import annotations

import os
import sys
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from harness_core import JournalRecordRef
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import (
    FanOutResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    WorkflowPauseReason,
)
from harness_runtime.config.state_placement import StateRootPlacementError
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimBusyError,
    ClaimRefusedError,
    HeldClaim,
    LeaseBusy,
    ParentCarriedAdmission,
    ResumeClaimStore,
    RootLatestAdmission,
    StartedClaim,
    StartedOrUnknown,
    UnstartedProof,
    parse_claim,
    started_frame,
)

from .test_b104_resume_claim_store import (
    Placed,
    _capture,  # pyright: ignore[reportPrivateUsage]
    _swap_marker,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_store import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def _claim_bytes(store: ResumeClaimStore, ref: JournalRecordRef) -> bytes:
    return store.paths_for(ref).claim.read_bytes()


class _ForgedLease:
    """A stand-in for the lease capability: a bare descriptor a caller opened for itself."""

    def __init__(self, fd: int) -> None:
        self.fd = fd

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


def _forged_claim(held: HeldClaim, fd: int) -> HeldClaim:
    """What any caller can build from the public dataclass and the disk-readable token."""
    return HeldClaim(held.token, held.record_ref, _ForgedLease(fd))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]


def _held(placed: Placed) -> tuple[ResumeClaimStore, JournalRecordRef, HeldClaim]:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    return store, ref, store.claim(ref, RootLatestAdmission())


def _lease_is_held_elsewhere(store: ResumeClaimStore, ref: JournalRecordRef) -> bool:
    return isinstance(store.probe_lease(ref), LeaseBusy)


# --- the transition ------------------------------------------------------------------------


def test_mark_started_appends_the_exact_started_frame_and_keeps_the_lease(placed: Placed) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)

    started = store.mark_started(held)

    assert isinstance(started, StartedClaim)
    assert _claim_bytes(store, ref) == claimed + started_frame(held)
    state = parse_claim(_claim_bytes(store, ref), ref)
    assert isinstance(state, StartedOrUnknown) and state.phase == "started"
    assert state.token == held.token
    assert started.lease_fd == held.lease_fd >= 0 and started.token == held.token
    assert _lease_is_held_elsewhere(store, ref)  # ownership stayed with the caller
    started.close()
    assert held.lease_fd == -1  # one descriptor, closed once, seen through both views
    assert not _lease_is_held_elsewhere(store, ref)


def test_the_started_frame_is_written_then_fsynced_before_mark_started_returns(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Durable ordering in the real code: write(started) -> fsync(claim fd) -> return."""
    store, ref, held = _held(placed)
    claim_name = store.paths_for(ref).claim.name
    events: list[tuple[str, str]] = []
    real_write, real_fsync = os.write, os.fsync

    def name_of(fd: int) -> str:
        return os.path.basename(os.readlink(f"/proc/self/fd/{fd}"))

    def write(fd: int, data: Any) -> int:
        if name_of(fd) == claim_name:
            events.append(("write", bytes(data).decode()))
        return real_write(fd, data)

    def fsync(fd: int) -> None:
        if name_of(fd) == claim_name:
            events.append(("fsync", ""))
        real_fsync(fd)

    monkeypatch.setattr(os, "write", write)
    monkeypatch.setattr(os, "fsync", fsync)

    store.mark_started(held)
    events.append(("returned", ""))

    assert [kind for kind, _ in events] == ["write", "fsync", "returned"]
    assert events[0][1].encode() == started_frame(held)


def test_a_failed_fsync_never_returns_a_started_claim_and_never_reads_as_unstarted(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, ref, held = _held(placed)
    claim_name = store.paths_for(ref).claim.name
    real_fsync = os.fsync

    def failing_fsync(fd: int) -> None:
        if os.path.basename(os.readlink(f"/proc/self/fd/{fd}")) == claim_name:
            raise OSError("simulated fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", failing_fsync)
    with pytest.raises(ClaimRefusedError):
        store.mark_started(held)
    monkeypatch.undo()

    assert not isinstance(parse_claim(_claim_bytes(store, ref), ref), UnstartedProof)
    assert held.lease_fd >= 0 and _lease_is_held_elsewhere(store, ref)  # still the caller's
    with pytest.raises(ClaimRefusedError):  # and it can never be started a second time
        store.mark_started(held)


# --- refusals: never busy, never a closed or changed lease, lease stays owned --------------


def test_a_second_mark_started_refuses_and_changes_nothing(placed: Placed) -> None:
    store, ref, held = _held(placed)
    store.mark_started(held)
    after_first = _claim_bytes(store, ref)

    with pytest.raises(ClaimRefusedError) as raised:
        store.mark_started(held)

    assert not isinstance(raised.value, ClaimBusyError)
    assert _claim_bytes(store, ref) == after_first
    assert held.lease_fd >= 0


def test_a_closed_lease_refuses_before_anything_is_written(placed: Placed) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    held.close()

    with pytest.raises(ClaimRefusedError):
        store.mark_started(held)

    assert _claim_bytes(store, ref) == claimed


def test_a_lease_fd_that_is_not_the_canonical_lease_refuses(placed: Placed) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    decoy = placed.journal_dir / "decoy"
    decoy.write_bytes(b"x")
    forged = _forged_claim(held, os.open(decoy, os.O_RDONLY))
    try:
        with pytest.raises(ClaimRefusedError):
            store.mark_started(forged)
    finally:
        forged.close()

    assert _claim_bytes(store, ref) == claimed
    assert held.lease_fd >= 0


def test_a_wrong_token_for_the_live_lease_refuses(placed: Placed) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    forged = HeldClaim(uuid.uuid4().hex, held.record_ref, held.lease)

    with pytest.raises(ClaimRefusedError):
        store.mark_started(forged)

    assert _claim_bytes(store, ref) == claimed
    assert held.lease_fd >= 0  # the forged view shares the fd but did not close it


def test_a_valid_looking_lease_on_a_replaced_inode_refuses(placed: Placed) -> None:
    """The fd holds a canonical-looking frame, but the canonical path now names another inode."""
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    lease = store.paths_for(ref).lease
    body = lease.read_bytes()
    lease.rename(lease.with_name(lease.name + ".moved"))
    lease.write_bytes(body)

    with pytest.raises(ClaimRefusedError):
        store.mark_started(held)

    assert _claim_bytes(store, ref) == claimed
    assert held.lease_fd >= 0


@pytest.mark.parametrize(
    "tamper",
    ["truncated", "garbage-tail", "other-token", "already-started", "empty", "missing", "symlink"],
)
def test_a_claim_that_is_not_an_exact_unstarted_proof_refuses_without_writing(
    placed: Placed, tamper: str
) -> None:
    store, ref, held = _held(placed)
    claim_path = store.paths_for(ref).claim
    good = claim_path.read_bytes()
    decoy = placed.journal_dir / "decoy-claim"
    decoy.write_bytes(good)
    if tamper == "truncated":
        claim_path.write_bytes(good[:-5])
    elif tamper == "garbage-tail":
        claim_path.write_bytes(good + b"junk")
    elif tamper == "other-token":
        claim_path.write_bytes(good.replace(held.token.encode(), uuid.uuid4().hex.encode()))
    elif tamper == "already-started":
        claim_path.write_bytes(good + started_frame(held))
    elif tamper == "empty":
        claim_path.write_bytes(b"")
    elif tamper == "missing":
        claim_path.unlink()
    else:
        claim_path.unlink()
        claim_path.symlink_to(decoy)
    before = None if tamper == "missing" else claim_path.read_bytes()
    decoy_before = decoy.read_bytes()

    with pytest.raises(ClaimRefusedError) as raised:
        store.mark_started(held)

    assert not isinstance(raised.value, ClaimBusyError)
    assert decoy.read_bytes() == decoy_before  # a symlink target is never appended to
    if before is not None:
        assert claim_path.read_bytes() == before
    assert held.lease_fd >= 0


def test_a_tombstoned_record_refuses(placed: Placed) -> None:
    store, ref, held = _held(placed)
    paths = store.paths_for(ref)
    claimed = _claim_bytes(store, ref)
    (paths.journal.parent / (paths.tombstone_prefix + "0")).write_bytes(b"x")

    with pytest.raises(ClaimRefusedError):
        store.mark_started(held)

    assert _claim_bytes(store, ref) == claimed


# --- placement -----------------------------------------------------------------------------


def test_a_swapped_root_before_the_transition_is_a_placement_fault_and_writes_nothing(
    placed: Placed,
) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    _swap_marker(placed)

    with pytest.raises(StateRootPlacementError):
        store.mark_started(held)

    assert _claim_bytes(store, ref) == claimed
    assert held.lease_fd >= 0


def test_a_root_swapped_after_the_journal_lock_still_writes_nothing(placed: Placed) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    inner = store._placement  # pyright: ignore[reportPrivateUsage]

    class SwapOnSecondBarrier:
        calls = 0

        def revalidate(self) -> None:
            SwapOnSecondBarrier.calls += 1
            if SwapOnSecondBarrier.calls == 2:  # the barrier taken under the journal lock
                _swap_marker(placed)
            inner.revalidate()

    store._placement = SwapOnSecondBarrier()  # type: ignore[assignment]  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(StateRootPlacementError):
        store.mark_started(held)

    assert SwapOnSecondBarrier.calls == 2
    assert _claim_bytes(store, ref) == claimed


# --- typed recency admission ---------------------------------------------------------------


def _summary_snapshot(workflow_id: str, run_id: str, **carriers: Any) -> PauseSnapshot:  # pyright: ignore[reportUnusedFunction]
    from harness_cp.handoff_context import StateSummary
    from harness_is.state_ledger_entry_schema import Identifier

    summary = StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )
    base: dict[str, Any] = {
        "workflow_id": workflow_id,
        "run_id": run_id,
        "step_index": 0,
        "pause_reason": WorkflowPauseReason.HITL_PENDING,
        "state_summary": summary,
        "snapshot_hash": (run_id.encode().hex() * 64)[:64],
        "created_at": 0,
        "state_ledger_anchor": "0" * 64,
    }
    return PauseSnapshot(**base, **carriers)


class Family:
    """Parent P (depth 0) carrying two same-workflow children N and N+1 (depth 1)."""

    def __init__(self, root: Path) -> None:
        self.journal = JournalWorkflowPauseStore(journal_dir=root, tenant_id=None)
        self.child_snaps = [_summary_snapshot("wf-child", f"run-child-{i}") for i in (0, 1)]
        self.child_refs = [self.journal.capture(s, depth=1) for s in self.child_snaps]
        self.parent_snapshot = self.parent_with(self.child_refs)
        self.parent_ref = self.journal.capture(self.parent_snapshot, depth=0)

    def parent_with(
        self,
        refs: list[JournalRecordRef],
        *,
        rehash: bool = True,
        snaps: list[PauseSnapshot] | None = None,
    ) -> PauseSnapshot:
        carriers = tuple(
            PausedChildBranchResumeState(
                branch_index=i,
                step_id=f"w-{i}",
                child_workflow_id="wf-child",
                child_snapshot=(snaps or self.child_snaps)[i],
            )
            for i, _ref in enumerate(refs)
        )
        fan_out = FanOutResumeState(
            orchestrator_output={},
            orchestrator_step_id="orch",
            branches=(),
            worker_count=2,
            paused_child_branches=carriers,
        )
        snapshot = _summary_snapshot("wf-parent", "run-parent", fan_out_resume=fan_out)
        if not rehash:
            return snapshot
        return snapshot.model_copy(
            update={
                "snapshot_hash": _compute_snapshot_hash(
                    workflow_id=snapshot.workflow_id,
                    run_id=snapshot.run_id,
                    step_index=snapshot.step_index,
                    state_summary=snapshot.state_summary,
                    fan_out_resume=fan_out,
                )
            }
        )


@pytest.fixture
def family(placed: Placed) -> Family:
    return Family(placed.journal_dir)


def _started_parent(store: ResumeClaimStore, family: Family) -> StartedClaim:
    held = store.claim(family.parent_ref, RootLatestAdmission())
    return store.mark_started(held)


def test_root_latest_admission_is_the_default_and_refuses_a_positional_sibling(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    # child 0 is no longer the journal's latest record for wf-child once child 1 exists
    with pytest.raises(ClaimRefusedError):
        store.claim(family.child_refs[0], RootLatestAdmission())
    with pytest.raises(ClaimRefusedError):
        store.claim(family.child_refs[0])


def test_a_started_parent_admits_each_same_workflow_sibling_positionally(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    with _started_parent(store, family) as parent:
        admission = ParentCarriedAdmission(parent)
        with store.claim(family.child_refs[0], admission) as first:  # N, though N+1 is latest
            with store.claim(family.child_refs[1], admission) as second:
                assert first.record_ref != second.record_ref
                assert first.lease_fd != second.lease_fd


def _parent_carried_refusal(
    placed: Placed, family: Family, parent: StartedClaim, child: int = 0
) -> None:
    store = placed.store()
    ref = family.child_refs[child]
    with pytest.raises(ClaimRefusedError) as raised:
        store.claim(ref, ParentCarriedAdmission(parent))
    assert not isinstance(raised.value, ClaimBusyError)
    assert not store.paths_for(ref).claim.exists()  # no claim was created


def test_a_parent_that_is_only_claimed_not_started_is_refused(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    unstarted = store.claim(family.parent_ref, RootLatestAdmission())
    with unstarted:
        _parent_carried_refusal(placed, family, StartedClaim(unstarted))  # forged typestate


def test_a_closed_parent_is_refused(placed: Placed, family: Family) -> None:
    parent = _started_parent(placed.store(), family)
    parent.close()
    _parent_carried_refusal(placed, family, parent)


def test_a_parent_that_does_not_carry_the_child_is_refused(placed: Placed, family: Family) -> None:
    store = placed.store()
    other = family.journal.capture(_summary_snapshot("wf-child", "run-child-2"), depth=1)
    with _started_parent(store, family) as parent:
        with pytest.raises(ClaimRefusedError):
            store.claim(other, ParentCarriedAdmission(parent))


def test_a_child_carried_twice_is_refused(placed: Placed) -> None:
    family = Family(placed.journal_dir)
    same = family.child_snaps[0]
    duplicated = family.parent_with([family.child_refs[0]] * 2, snaps=[same, same])
    family.parent_ref = family.journal.capture(duplicated, depth=0)
    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent)


def test_a_parent_whose_carriers_are_not_hash_covered_is_refused(placed: Placed) -> None:
    family = Family(placed.journal_dir)
    tampered = family.parent_with(family.child_refs, rehash=False).model_copy(
        update={"snapshot_hash": "f" * 64}
    )
    family.parent_ref = family.journal.capture(tampered, depth=0)
    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent)


def test_a_child_that_is_not_one_level_below_its_parent_is_refused(placed: Placed) -> None:
    family = Family(placed.journal_dir)
    root_level = family.journal.capture(family.child_snaps[0], depth=0)
    family.child_refs[0] = root_level
    family.parent_ref = family.journal.capture(family.parent_with(family.child_refs), depth=0)
    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent)


# --- F2: the lease's exclusive lock must be held by THIS descriptor -----------------------


def _unlocked_fd_for(store: ResumeClaimStore, ref: JournalRecordRef) -> int:
    """A fresh read-only descriptor on the canonical lease inode: same bytes, no flock."""
    return os.open(store.paths_for(ref).lease, os.O_RDONLY)


def test_a_forged_claim_on_an_unlocked_fd_refuses_while_the_real_holder_is_live(
    placed: Placed,
) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    forged = _forged_claim(held, _unlocked_fd_for(store, ref))
    try:
        with pytest.raises(ClaimRefusedError) as raised:
            store.mark_started(forged)
        assert not isinstance(raised.value, ClaimBusyError)
    finally:
        forged.close()

    assert _claim_bytes(store, ref) == claimed  # nothing was appended
    assert _lease_is_held_elsewhere(store, ref)  # the real holder's lock is undisturbed
    store.mark_started(held)  # and the real holder still proceeds


def test_a_forged_claim_on_an_unlocked_fd_refuses_when_nobody_holds_the_lease(
    placed: Placed,
) -> None:
    """No live holder at all: the descriptor still proves nothing, and the refused attempt
    must not leave the lease locked behind it."""
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    forged = _forged_claim(held, _unlocked_fd_for(store, ref))
    held.close()
    try:
        with pytest.raises(ClaimRefusedError):
            store.mark_started(forged)
    finally:
        forged.close()

    assert _claim_bytes(store, ref) == claimed
    assert not _lease_is_held_elsewhere(store, ref)  # no lock was left behind


def test_a_forged_started_parent_on_an_unlocked_fd_admits_no_child(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    real_parent = _started_parent(store, family)  # the genuine holder stays live
    forged = StartedClaim(
        _forged_claim(real_parent.claim, _unlocked_fd_for(store, family.parent_ref))
    )
    try:
        _parent_carried_refusal(placed, family, forged)
    finally:
        forged.close()
        real_parent.close()


def test_the_real_holder_is_unaffected_by_the_lock_proof_repeated_probes(placed: Placed) -> None:
    store, ref, held = _held(placed)
    for _ in range(3):
        assert _lease_is_held_elsewhere(store, ref)
    started = store.mark_started(held)
    assert isinstance(started, StartedClaim) and _lease_is_held_elsewhere(store, ref)
    started.close()


# --- F2 release race: ownership is a store-issued capability, not a lock acquired on demand --


@contextmanager
def _release_holder_when_a_nonblocking_lock_is_first_refused(
    monkeypatch: pytest.MonkeyPatch, holder: HeldClaim
) -> Generator[None]:
    """The genuine holder closes at the exact point a fresh lock attempt is refused.

    This is the OS ordering behind the review finding: whatever the store does after its
    first refused lock attempt runs against a lease nobody holds any more.
    """
    import fcntl

    real_flock = fcntl.flock
    released: list[bool] = []

    def flock(fd: int, operation: int) -> None:
        try:
            real_flock(fd, operation)
        except OSError:
            if not released:
                released.append(True)
                holder.close()
            raise

    monkeypatch.setattr(fcntl, "flock", flock)
    yield


def test_a_forged_claim_is_refused_when_the_holder_releases_between_lock_attempts(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    forged = _forged_claim(held, _unlocked_fd_for(store, ref))
    try:
        with _release_holder_when_a_nonblocking_lock_is_first_refused(monkeypatch, held):
            with pytest.raises(ClaimRefusedError):
                store.mark_started(forged)
    finally:
        forged.close()

    assert _claim_bytes(store, ref) == claimed  # no started frame was appended


def test_a_forged_parent_admits_no_child_when_the_holder_releases_between_lock_attempts(
    placed: Placed, family: Family, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = placed.store()
    real_parent = _started_parent(store, family)
    forged = StartedClaim(
        _forged_claim(real_parent.claim, _unlocked_fd_for(store, family.parent_ref))
    )
    try:
        with _release_holder_when_a_nonblocking_lock_is_first_refused(
            monkeypatch, real_parent.claim
        ):
            _parent_carried_refusal(placed, family, forged)
    finally:
        forged.close()
        real_parent.close()


def test_lease_capabilities_are_issued_only_by_the_store() -> None:
    from harness_runtime.lifecycle.resume_claim_store import LeaseCapability

    with pytest.raises(TypeError):
        LeaseCapability(object(), 0)


def test_a_started_parent_from_one_store_instance_admits_a_child_in_another(
    placed: Placed, family: Family
) -> None:
    parent = _started_parent(placed.store(), family)
    with parent:
        with placed.store().claim(family.child_refs[0], ParentCarriedAdmission(parent)) as child:
            assert child.record_ref == family.child_refs[0]
            assert _lease_is_held_elsewhere(placed.store(), child.record_ref)


def test_closing_a_claim_invalidates_it_for_start_and_for_parent_admission(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    parent = _started_parent(store, family)
    parent.close()
    assert parent.lease_fd == -1 and not _lease_is_held_elsewhere(store, family.parent_ref)
    _parent_carried_refusal(placed, family, parent)

    _store, ref, held = _held(placed)
    held.close()
    with pytest.raises(ClaimRefusedError):
        store.mark_started(held)


def test_a_capability_whose_flock_was_released_behind_its_back_refuses(placed: Placed) -> None:
    import fcntl

    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    fcntl.flock(held.lease_fd, fcntl.LOCK_UN)  # the fd is open, the lock is gone

    with pytest.raises(ClaimRefusedError):
        store.mark_started(held)

    assert _claim_bytes(store, ref) == claimed
    held.close()


def test_a_capability_on_a_moved_lease_refuses_even_if_someone_holds_the_new_one(
    placed: Placed,
) -> None:
    import fcntl

    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    lease = store.paths_for(ref).lease
    data = lease.read_bytes()
    lease.rename(lease.with_name(lease.name + ".moved"))
    lease.write_bytes(data)  # a different inode with identical bytes, held by another party
    other = os.open(lease, os.O_RDONLY)
    try:
        fcntl.flock(other, fcntl.LOCK_EX)
        with pytest.raises(ClaimRefusedError):
            store.mark_started(held)
    finally:
        os.close(other)
        held.close()

    assert _claim_bytes(store, ref) == claimed

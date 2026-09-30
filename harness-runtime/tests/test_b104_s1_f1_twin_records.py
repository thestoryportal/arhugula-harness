"""B-104 S1 + F1 integration: the combined claimed-child admission over two real twin records.

Real placed claim store and real journal. Twins N and N+1 are byte-identical snapshots of one
child workflow journaled at different positions; the parent's hash-covered snapshot names
exactly one of them. The path under test is `ClaimedChildAdmission.run_admitted` (S1) over
`ParentCarriedAdmission` and the store's exact-ref check (F1), with a counting body as the child.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest
from harness_cp.pause_resume_protocol import verify_pause_snapshot_hash
from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError
from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.durable_child_admission import VerifiedChildRecord
from harness_runtime.lifecycle.resume_claim_store import StartedClaim

from .test_b104_f4_started_body_gateway import (
    _Body,  # pyright: ignore[reportPrivateUsage]
    _lease_is_free,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import (
    Family,
    _started_parent,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def _twin_family(placed: Any, *, names: int) -> tuple[Family, StartedClaim]:
    """Twins N (0) and N+1 (1); the started parent's journaled carrier names ONLY twin `names`."""
    family = Family(placed.journal_dir, identical_children=True)
    assert family.child_snaps[0] == family.child_snaps[1]
    assert family.child_refs[0] != family.child_refs[1]
    carried = family.parent_with([family.child_refs[names]], snaps=[family.child_snaps[names]])
    assert verify_pause_snapshot_hash(carried)  # CP's public verifier: the carrier is hash-covered
    family.parent_ref = family.journal.capture(carried, depth=0)
    return family, _started_parent(placed.store(), family)


def _verified(family: Family, index: int) -> VerifiedChildRecord:
    ref = family.child_refs[index]
    record = family.journal.read_exact(ref)
    assert record is not None
    return VerifiedChildRecord(ref=ref, snapshot=record.snapshot, depth=1)


def _journal_files(placed: Any) -> set[str]:
    return {p.name for p in placed.journal_dir.iterdir()}


def test_the_uncarried_twin_is_claim_refused_with_no_claim_frame_or_body(placed: Any) -> None:
    family, parent = _twin_family(placed, names=0)  # the parent carries N
    store = placed.store()
    wrong = _verified(family, 1)  # ... but N+1 is what gets presented
    body = _Body(store, wrong.ref)
    files_before = _journal_files(placed)

    with parent:
        with pytest.raises(ChildResumeRefusedError) as caught:
            ClaimedChildAdmission(store, parent).run_admitted(wrong, body)

        assert caught.value.reason is ChildResumeRefusal.CLAIM_REFUSED
        assert body.calls == 0  # no result of the wrong record exists
        assert not store.paths_for(wrong.ref).claim.exists()  # no claim, so no started frame
        assert not store.paths_for(wrong.ref).lease.exists()
        assert not store.paths_for(family.child_refs[0]).claim.exists()  # N was not touched either
        assert _journal_files(placed) == files_before  # nothing was written for either twin


def test_the_carried_twin_starts_and_calls_the_body_once_then_releases_its_lease(
    placed: Any,
) -> None:
    family, parent = _twin_family(placed, names=0)
    store = placed.store()
    exact = _verified(family, 0)
    body = _Body(store, exact.ref)

    with parent:
        assert ClaimedChildAdmission(store, parent).run_admitted(exact, body) == "ran"

    assert body.calls == 1
    assert body.claim_phase == "started"  # the fsynced frame was on disk at body entry
    assert body.lease_seen is not None and body.lease_seen.__name__ == "LeaseBusy"
    assert _lease_is_free(store, exact.ref)  # released at exit
    assert not store.paths_for(family.child_refs[1]).claim.exists()  # the other twin untouched


@pytest.mark.parametrize("names", [0, 1])
def test_only_the_named_twin_is_admitted_whichever_position_it_holds(
    placed: Any, names: int
) -> None:
    family, parent = _twin_family(placed, names=names)
    store = placed.store()
    named, other = _verified(family, names), _verified(family, 1 - names)
    named_body, other_body = _Body(store, named.ref), _Body(store, other.ref)

    with parent:
        with pytest.raises(ChildResumeRefusedError) as caught:
            ClaimedChildAdmission(store, parent).run_admitted(other, other_body)
        assert ClaimedChildAdmission(store, parent).run_admitted(named, named_body) == "ran"

    assert caught.value.reason is ChildResumeRefusal.CLAIM_REFUSED
    assert (named_body.calls, other_body.calls) == (1, 0)

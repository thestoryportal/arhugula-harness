"""B-104 Task 5a F1: a child is admitted only under the EXACT record ref its parent carries.

The authority is the parent's OWN journaled snapshot (its hash-covered `child_record_ref`),
never anything a caller presents. Two byte-identical records at different positions share
every snapshot field, so matching on snapshot equality alone would let one carrier admit
either; the exact ref is what tells them apart. Every refusal is a `ClaimRefusedError` raised
before the claim file is created, so no `claimed` and no `started` frame can follow.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import (
    FanOutResumeState,
    PausedChildBranchResumeState,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from harness_runtime.lifecycle.resume_claim_store import ParentCarriedAdmission

from .test_b104_resume_claim_started import (
    Family,
    _parent_carried_refusal,  # pyright: ignore[reportPrivateUsage]
    _started_parent,  # pyright: ignore[reportPrivateUsage]
    _summary_snapshot,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def _twin_parent(placed: Any, *, names: int) -> tuple[Family, Any]:
    """Twins N (0) and N+1 (1): the parent's snapshot carries ONLY twin `names`, by exact ref."""
    family = Family(placed.journal_dir, identical_children=True)
    assert family.child_snaps[0] == family.child_snaps[1]  # byte-identical content
    assert family.child_refs[0] != family.child_refs[1]  # at different positions
    carried = family.parent_with([family.child_refs[names]], snaps=[family.child_snaps[names]])
    family.parent_ref = family.journal.capture(carried, depth=0)
    return family, _started_parent(placed.store(), family)


@pytest.mark.parametrize("names", [0, 1])
def test_a_carrier_that_names_one_twin_refuses_the_other_and_admits_the_named_one(
    placed: Any, names: int
) -> None:
    family, parent = _twin_parent(placed, names=names)
    other = 1 - names
    with parent:
        _parent_carried_refusal(placed, family, parent, child=other)
        with placed.store().claim(
            family.child_refs[names], ParentCarriedAdmission(parent)
        ) as admitted:
            assert admitted.record_ref == family.child_refs[names]


def test_a_legacy_carrier_with_no_ref_never_admits_a_child(placed: Any) -> None:
    family = Family(placed.journal_dir)
    legacy = family.parent_with([family.child_refs[0]], carried=[None])  # snapshot matches
    family.parent_ref = family.journal.capture(legacy, depth=0)

    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent, child=0)


def test_a_carrier_that_names_the_same_exact_ref_twice_is_refused(placed: Any) -> None:
    family = Family(placed.journal_dir)
    same = family.child_refs[0]
    doubled = family.parent_with([same, same], snaps=[family.child_snaps[0]] * 2)
    family.parent_ref = family.journal.capture(doubled, depth=0)

    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent, child=0)


def test_a_matching_ref_with_a_snapshot_that_differs_in_an_uncovered_field_is_refused(
    placed: Any,
) -> None:
    family = Family(placed.journal_dir)
    # `created_at` is not part of the snapshot hash, so the carrier's ref still binds it and
    # the parent still re-hashes, yet it is not the snapshot the journal holds at that ref.
    drifted = family.child_snaps[0].model_copy(update={"created_at": 99})
    assert drifted.snapshot_hash == family.child_snaps[0].snapshot_hash
    parent_snapshot = family.parent_with([family.child_refs[0]], snaps=[drifted])
    family.parent_ref = family.journal.capture(parent_snapshot, depth=0)

    with _started_parent(placed.store(), family) as parent:
        _parent_carried_refusal(placed, family, parent, child=0)


def test_distinct_siblings_are_each_admitted_under_their_own_exact_ref(placed: Any) -> None:
    family = Family(placed.journal_dir)
    store = placed.store()
    with _started_parent(store, family) as parent:
        admission = ParentCarriedAdmission(parent)
        with store.claim(family.child_refs[0], admission) as first:
            with store.claim(family.child_refs[1], admission) as second:
                assert (first.record_ref, second.record_ref) == tuple(family.child_refs)


def _carrying(workflow: str, run: str, child_workflow: str, child_snapshot: Any, child_ref: Any):
    """A hash-covered snapshot whose fan-out carries one paused child by exact ref."""
    carrier = PausedChildBranchResumeState(
        branch_index=0,
        step_id="w-0",
        child_workflow_id=child_workflow,
        child_snapshot=child_snapshot,
        child_record_ref=child_ref,
    )
    fan_out = FanOutResumeState(
        orchestrator_output={},
        orchestrator_step_id="orch",
        branches=(),
        worker_count=1,
        paused_child_branches=(carrier,),
    )
    snapshot = _summary_snapshot(workflow, run, fan_out_resume=fan_out)
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


def test_a_depth_two_grandchild_is_admitted_through_the_started_root_zero_to_child_one_chain(
    placed: Any,
) -> None:
    journal = JournalWorkflowPauseStore(journal_dir=Path(placed.journal_dir), tenant_id=None)
    grand_snapshot = _summary_snapshot("wf-grand", "run-grand")
    grand_ref = journal.capture(grand_snapshot, depth=2)
    mid_snapshot = _carrying("wf-mid", "run-mid", "wf-grand", grand_snapshot, grand_ref)
    mid_ref = journal.capture(mid_snapshot, depth=1)
    root_snapshot = _carrying("wf-root", "run-root", "wf-mid", mid_snapshot, mid_ref)
    root_ref = journal.capture(root_snapshot, depth=0)
    store = placed.store()

    # Only the depth-0 root holds root authority; each lower level is admitted through the
    # STARTED parent that carries it by exact ref, and every lease stays live until the end.
    with store.mark_started(store.claim(root_ref)) as root:
        with store.mark_started(store.claim(mid_ref, ParentCarriedAdmission(root))) as mid:
            with store.claim(grand_ref, ParentCarriedAdmission(mid)) as grand:
                assert grand.record_ref == grand_ref

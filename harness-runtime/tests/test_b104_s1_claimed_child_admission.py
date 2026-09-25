"""B-104 S1: the unbound `ClaimedChildAdmission` maps the gateway's typed phases to refusals.

Real placed claim store, counting body. The mapping is by (phase, cause type), never by message
text; unexpected faults are not refusals; nothing in production imports the new binding.
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path
from typing import Any

import pytest
from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError
from harness_runtime.lifecycle import resume_claim_store as rcs
from harness_runtime.lifecycle.durable_child_admission import VerifiedChildRecord
from harness_runtime.lifecycle.resume_claim_store import (
    HeldClaim,
    HeldLease,
    ResumeClaimStore,
    RootLatestAdmission,
    StartedClaim,
)

from .test_b104_f4_started_body_gateway import (
    _Body,  # pyright: ignore[reportPrivateUsage]
    _lease_is_free,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import (
    Family,
    _started_parent,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import family as family  # fixture
from .test_b104_resume_claim_store import Placed
from .test_b104_resume_claim_store import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")

_SRC = Path(rcs.__file__).resolve().parents[1]


def _admission(store: ResumeClaimStore, parent: StartedClaim) -> Any:
    from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission

    return ClaimedChildAdmission(store, parent)


def _verified(family: Family, index: int = 0) -> VerifiedChildRecord:
    ref = family.child_refs[index]
    record = family.journal.read_exact(ref)
    assert record is not None
    return VerifiedChildRecord(ref=ref, snapshot=record.snapshot, depth=1)


def _refusal_reason(caught: pytest.ExceptionInfo[ChildResumeRefusedError]) -> ChildResumeRefusal:
    error = caught.value
    assert isinstance(error.__cause__, Exception)  # the gateway refusal is chained
    return error.reason


def test_a_started_parent_admits_the_child_body_and_returns_its_result(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    verified = _verified(family)
    body = _Body(store, verified.ref)
    with _started_parent(store, family) as parent:
        assert _admission(store, parent).run_admitted(verified, body) == "ran"

    assert body.calls == 1 and body.claim_phase == "started"


def test_a_stale_or_mismatched_child_ref_is_claim_refused(placed: Placed, family: Family) -> None:
    store = placed.store()
    good = _verified(family)
    wrong = VerifiedChildRecord(
        ref=good.ref.model_copy(update={"latest_digest": "0" * 64}),
        snapshot=good.snapshot,
        depth=1,
    )
    body = _Body(store, wrong.ref)
    with _started_parent(store, family) as parent:
        with pytest.raises(ChildResumeRefusedError) as caught:
            _admission(store, parent).run_admitted(wrong, body)

    assert _refusal_reason(caught) is ChildResumeRefusal.CLAIM_REFUSED
    assert body.calls == 0 and not store.paths_for(wrong.ref).claim.exists()


def test_an_unstarted_parent_is_claim_refused(placed: Placed, family: Family) -> None:
    store = placed.store()
    verified = _verified(family)
    body = _Body(store, verified.ref)
    unstarted = store.claim(family.parent_ref, RootLatestAdmission())
    with unstarted:
        with pytest.raises(ChildResumeRefusedError) as caught:
            _admission(store, StartedClaim(unstarted)).run_admitted(verified, body)

    assert _refusal_reason(caught) is ChildResumeRefusal.CLAIM_REFUSED and body.calls == 0


def test_a_busy_child_lease_is_claim_busy(placed: Placed, family: Family) -> None:
    store = placed.store()
    verified = _verified(family)
    body = _Body(store, verified.ref)
    with _started_parent(store, family) as parent:
        store.claim(verified.ref, rcs.ParentCarriedAdmission(parent)).close()
        store.paths_for(verified.ref).claim.unlink()  # a child lease with no claim, held below
        other = store.probe_lease(verified.ref)
        assert isinstance(other, HeldLease)
        try:
            with pytest.raises(ChildResumeRefusedError) as caught:
                _admission(store, parent).run_admitted(verified, body)
        finally:
            other.close()

    assert _refusal_reason(caught) is ChildResumeRefusal.CLAIM_BUSY and body.calls == 0


class _StartRefusingStore(ResumeClaimStore):
    def mark_started(self, held: HeldClaim, *, deadline_seconds: float | None = None):
        paths = self.paths_for(held.record_ref)
        (paths.journal.parent / (paths.tombstone_prefix + "0")).write_bytes(b"x")
        return super().mark_started(held, deadline_seconds=deadline_seconds)


class _FsyncFaultStore(ResumeClaimStore):
    def __init__(self, *args: Any, patch: pytest.MonkeyPatch, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._patch = patch

    def mark_started(self, held: HeldClaim, *, deadline_seconds: float | None = None):
        real = os.fsync

        def broken(fd: int) -> None:
            raise OSError("injected fsync fault")

        self._patch.setattr(os, "fsync", broken)
        try:
            return super().mark_started(held, deadline_seconds=deadline_seconds)
        finally:
            self._patch.setattr(os, "fsync", real)


@pytest.mark.parametrize("fault", ["tombstone", "fsync"])
def test_a_refused_durable_start_is_start_refused_with_the_lease_released(
    placed: Placed, family: Family, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    parent_store = placed.store()
    verified = _verified(family)
    store: ResumeClaimStore = (
        _StartRefusingStore(placement=placed.placement(), tenant_id=None)
        if fault == "tombstone"
        else _FsyncFaultStore(placement=placed.placement(), tenant_id=None, patch=monkeypatch)
    )
    body = _Body(store, verified.ref)
    with _started_parent(parent_store, family) as parent:
        with pytest.raises(ChildResumeRefusedError) as caught:
            _admission(store, parent).run_admitted(verified, body)

    assert _refusal_reason(caught) is ChildResumeRefusal.START_REFUSED
    assert body.calls == 0 and _lease_is_free(store, verified.ref)


def test_the_detail_is_the_stores_human_text_and_never_the_reason(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    verified = _verified(family)
    unstarted = store.claim(family.parent_ref, RootLatestAdmission())
    with unstarted:
        with pytest.raises(ChildResumeRefusedError) as caught:
            _admission(store, StartedClaim(unstarted)).run_admitted(verified, lambda: "x")

    assert caught.value.detail == str(caught.value.__cause__.__cause__)  # type: ignore[union-attr]
    assert "claim-refused" not in caught.value.detail


# --- faults that are not refusals propagate as themselves -----------------------------------------


def test_a_placement_fault_is_not_a_refusal(placed: Placed, family: Family) -> None:
    from harness_runtime.config.state_placement import StateRootPlacementError

    from .test_b104_resume_claim_store import (
        _swap_marker,  # pyright: ignore[reportPrivateUsage]
    )

    store = placed.store()
    verified = _verified(family)
    body = _Body(store, verified.ref)
    with _started_parent(store, family) as parent:
        _swap_marker(placed)
        with pytest.raises(StateRootPlacementError):
            _admission(store, parent).run_admitted(verified, body)

    assert body.calls == 0


def test_a_journal_lock_timeout_is_not_a_refusal(placed: Placed, family: Family) -> None:
    from harness_core.cross_process_lock_deadline import CrossProcessLockTimeoutError
    from harness_runtime.lifecycle.journal_workflow_pause_store import cross_process_journal_lock

    store = placed.store()
    verified = _verified(family)
    body = _Body(store, verified.ref)
    with _started_parent(store, family) as parent:
        from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission

        admission = ClaimedChildAdmission(store, parent, deadline_seconds=0.2)
        with cross_process_journal_lock(store.paths_for(verified.ref).journal):
            with pytest.raises(CrossProcessLockTimeoutError):
                admission.run_admitted(verified, body)

    assert body.calls == 0


def test_a_raw_oserror_creating_the_claim_is_not_a_refusal(
    placed: Placed, family: Family, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = placed.store()
    verified = _verified(family)
    body = _Body(store, verified.ref)
    real = rcs._write_all  # pyright: ignore[reportPrivateUsage]

    def failing(fd: int, data: bytes) -> None:
        if b'"claimed"' in data:
            raise OSError(28, "injected write fault")
        real(fd, data)

    with _started_parent(store, family) as parent:
        monkeypatch.setattr(rcs, "_write_all", failing)
        with pytest.raises(OSError, match="injected write fault") as caught:
            _admission(store, parent).run_admitted(verified, body)

    assert not isinstance(caught.value, ChildResumeRefusedError) and body.calls == 0


def test_a_gateway_refusal_raised_by_the_body_itself_is_not_remapped(
    placed: Placed, family: Family
) -> None:
    """A nested child's gateway refusal inside this child's body is the body's, not ours."""
    from harness_runtime.lifecycle.started_body_gateway import GatewayPhase, GatewayRefusal

    store = placed.store()
    verified = _verified(family)
    inner = GatewayRefusal(GatewayPhase.CLAIM, rcs.ClaimRefusedError("nested"))

    def body() -> str:
        raise inner

    with _started_parent(store, family) as parent:
        with pytest.raises(GatewayRefusal) as caught:
            _admission(store, parent).run_admitted(verified, body)

    assert caught.value is inner


def test_a_body_failure_propagates_and_the_claim_stays_started(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    verified = _verified(family)

    def body() -> str:
        raise RuntimeError("child failed")

    with _started_parent(store, family) as parent:
        with pytest.raises(RuntimeError, match="child failed"):
            _admission(store, parent).run_admitted(verified, body)

    assert _lease_is_free(store, verified.ref)


# --- nothing in production binds or imports the new binding ---------------------------------------


def test_stage_five_still_binds_the_refusing_admission_and_only_tests_touch_the_new_binding() -> (
    None
):
    stage5 = (_SRC / "bootstrap" / "stage_5_loop_init.py").read_text()

    assert "durable_admission=RefuseDurableChildAdmission()" in stage5
    assert "ClaimedChildAdmission" not in stage5
    for path in _SRC.rglob("*.py"):
        text = path.read_text()
        if path.name == "claimed_child_admission.py":
            continue
        imports = {
            (n.module or "") for n in ast.walk(ast.parse(text)) if isinstance(n, ast.ImportFrom)
        }
        assert not any("claimed_child_admission" in m for m in imports), path
        if path.name != "started_body_gateway.py":
            assert "ClaimedChildAdmission" not in text, path

"""B-104 Task 5b-1 correction: a gateway body holds a nonclosable started proof, never the claim.

Over the real placed claim store. The body of `run_started` must be unable to release the lease
it runs under; only the gateway's `finally` does. `ParentCarriedAdmission` still admits an exact
child through that proof, on the same parent lease.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimRefusedError,
    HeldLease,
    ParentCarriedAdmission,
    RootLatestAdmission,
)
from harness_runtime.lifecycle.started_body_gateway import run_started

from .test_b104_resume_claim_started import Family
from .test_b104_resume_claim_started import family as family  # fixture
from .test_b104_resume_claim_store import Placed
from .test_b104_resume_claim_store import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def _lease_is_free(store: Any, ref: Any) -> bool:
    probe = store.probe_lease(ref)
    if isinstance(probe, HeldLease):
        probe.close()
        return True
    return False


def _lease_busy(store: Any, ref: Any) -> bool:
    return not _lease_is_free(store, ref)


def test_a_body_holds_a_proof_it_cannot_close_and_the_lease_stays_busy_until_it_returns(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    ref = family.parent_ref
    seen: dict[str, Any] = {}

    def body(proof: Any) -> str:
        seen["type"] = type(proof)
        seen["public"] = sorted(n for n in dir(proof) if not n.startswith("_"))
        seen["closable"] = hasattr(proof, "close")
        seen["closed_in"] = proof.closed
        seen["busy_in"] = _lease_busy(store, ref)
        seen["proof"] = proof
        with pytest.raises(AttributeError):
            proof.close()
        seen["still_busy"] = _lease_busy(store, ref)  # the failed release attempt freed nothing
        return "ran"

    assert run_started(store, ref, RootLatestAdmission(), body) == "ran"

    assert seen["type"].__name__ == "StartedProof" and seen["closable"] is False
    assert seen["public"] == ["closed", "record_ref", "token"]  # no claim, lease or close route
    assert seen["closed_in"] is False and seen["busy_in"] and seen["still_busy"]
    assert seen["proof"].closed is True and _lease_is_free(store, ref)  # gateway alone released


def test_the_proof_admits_an_exact_child_on_the_same_parent_lease(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    child = family.child_refs[0]
    seen: dict[str, Any] = {}

    def body(proof: Any) -> str:
        with store.claim(child, ParentCarriedAdmission(proof)) as held:
            seen["child_busy"] = _lease_busy(store, child)
            seen["record"] = held.record_ref
        seen["parent_busy"] = _lease_busy(store, family.parent_ref)
        seen["proof"] = proof
        return "ran"

    run_started(store, family.parent_ref, RootLatestAdmission(), body)

    assert seen["record"] == child and seen["child_busy"] and seen["parent_busy"]
    assert _lease_is_free(store, family.parent_ref)
    # once the gateway released the parent, the retained proof admits nothing
    with pytest.raises(ClaimRefusedError):
        store.claim(family.child_refs[1], ParentCarriedAdmission(seen["proof"]))


def test_a_proof_cannot_be_minted_subclassed_copied_or_pickled(
    placed: Placed, family: Family
) -> None:
    import copy
    import pickle

    from harness_runtime.lifecycle.resume_claim_store import StartedProof

    store = placed.store()
    got: list[Any] = []
    run_started(store, family.parent_ref, RootLatestAdmission(), got.append)
    (proof,) = got

    with pytest.raises(TypeError):
        StartedProof(object(), None)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    with pytest.raises(TypeError):
        type("Sub", (StartedProof,), {})
    with pytest.raises(TypeError):
        copy.copy(proof)
    with pytest.raises(TypeError):
        pickle.dumps(proof)

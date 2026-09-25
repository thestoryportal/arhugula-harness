"""B-104 Task 5b-1 (Runtime half): a child's own authority is handed to its body, never the root's.

Real placed claim store and durable journal; the child body is a counting stand-in, so the ORDER
is proven on the real code path. Nothing here wires `api.resume` or stage 5: no production entry
can supply an authority yet, and these tests assert that too.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from harness_core import JournalRecordRef
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import (
    FanOutResumeState,
    PausedChildBranchResumeState,
    PausedChildCapture,
    PauseSnapshot,
)
from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError
from harness_runtime.lifecycle import child_workflow_runner as cwr
from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.durable_child_admission import (
    RefuseDurableChildAdmission,
    VerifiedChildRecord,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from harness_runtime.lifecycle.resume_claim_store import (
    HeldLease,
    LeaseBusy,
    ResumeClaimStore,
    RootLatestAdmission,
    StartedClaim,
    StartedOrUnknown,
    parse_claim,
)

from .test_b104_resume_claim_started import _summary_snapshot  # pyright: ignore[reportPrivateUsage]
from .test_b104_resume_claim_store import Placed
from .test_b104_resume_claim_store import placed as placed
from .test_b104_task4a_capture_depth import _protocol  # pyright: ignore[reportPrivateUsage]
from .test_lifecycle_sub_agent_dispatch import (
    _binding,  # pyright: ignore[reportPrivateUsage]
    _dispatcher,  # pyright: ignore[reportPrivateUsage]
    _payload,  # pyright: ignore[reportPrivateUsage]
    _step,  # pyright: ignore[reportPrivateUsage]
    _step_context,  # pyright: ignore[reportPrivateUsage]
)
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def _carrying(workflow_id: str, run_id: str, child_workflow_id: str, child: PauseSnapshot):
    carrier = PausedChildBranchResumeState(
        branch_index=0, step_id="w-0", child_workflow_id=child_workflow_id, child_snapshot=child
    )
    fan_out = FanOutResumeState(
        orchestrator_output={},
        orchestrator_step_id="orch",
        branches=(),
        worker_count=1,
        paused_child_branches=(carrier,),
    )
    snapshot = _summary_snapshot(workflow_id, run_id, fan_out_resume=fan_out)
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


class Chain:
    """Journaled P (depth 0) carrying C (depth 1) carrying G (depth 2), each exactly once."""

    def __init__(self, root: Path) -> None:
        self.journal = JournalWorkflowPauseStore(journal_dir=root, tenant_id=None)
        self.g_snap = _summary_snapshot("wf-g", "run-g")
        self.g_ref = self.journal.capture(self.g_snap, depth=2)
        self.c_snap = _carrying("wf-c", "run-c", "wf-g", self.g_snap)
        self.c_ref = self.journal.capture(self.c_snap, depth=1)
        self.p_snap = _carrying("wf-p", "run-p", "wf-c", self.c_snap)
        self.p_ref = self.journal.capture(self.p_snap, depth=0)

    def verified(self, ref: JournalRecordRef, snap: PauseSnapshot, depth: int):
        return VerifiedChildRecord(ref=ref, snapshot=snap, depth=depth)

    @property
    def c(self) -> VerifiedChildRecord:
        return self.verified(self.c_ref, self.c_snap, 1)

    @property
    def g(self) -> VerifiedChildRecord:
        return self.verified(self.g_ref, self.g_snap, 2)

    def capture(self, ref: JournalRecordRef, snap: PauseSnapshot) -> PausedChildCapture:
        return PausedChildCapture(
            child_workflow_id=ref.workflow_id, child_snapshot=snap, child_record_ref=ref
        )


@pytest.fixture
def chain(placed: Placed) -> Chain:
    return Chain(placed.journal_dir)


def _root_authority(
    store: ResumeClaimStore, chain: Chain
) -> tuple[ClaimedChildAdmission, StartedClaim]:
    started = store.mark_started(store.claim(chain.p_ref, RootLatestAdmission()))
    return ClaimedChildAdmission(store, started), started


def _lease_state(store: ResumeClaimStore, ref: JournalRecordRef) -> str:
    probe = store.probe_lease(ref)
    if isinstance(probe, HeldLease):
        probe.close()
        return "free"
    return "busy" if isinstance(probe, LeaseBusy) else "other"


# --- the body gets the child's own, fresh authority after a durable start -----------------------


def test_a_live_parent_and_a_durable_child_start_precede_one_body_that_gets_a_new_authority(
    placed: Placed, chain: Chain
) -> None:
    store = placed.store()
    root, _started = _root_authority(store, chain)
    seen: list[Any] = []

    def body(child: ClaimedChildAdmission) -> str:
        state = parse_claim(store.paths_for(chain.c_ref).claim.read_bytes(), chain.c_ref)
        seen.append(
            (
                child,
                isinstance(state, StartedOrUnknown) and state.phase,
                _lease_state(store, chain.c_ref),
            )
        )
        return "ran"

    assert root.run_with_child_authority(chain.c, body) == "ran"

    ((child, phase, lease),) = seen
    assert type(child) is ClaimedChildAdmission and child is not root
    assert phase == "started" and lease == "busy"  # fsynced start on disk, lease held in body
    assert _lease_state(store, chain.c_ref) == "free"  # released once the body returned


def test_the_child_lease_stays_held_until_its_worker_body_returns_even_after_a_caller_timeout(
    placed: Placed, chain: Chain
) -> None:
    store = placed.store()
    root, _started = _root_authority(store, chain)
    entered, release, done = threading.Event(), threading.Event(), threading.Event()

    def worker_body(_child: ClaimedChildAdmission) -> str:
        entered.set()
        release.wait()
        return "finished"

    def worker() -> None:
        root.run_with_child_authority(chain.c, worker_body)
        done.set()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    assert entered.wait(timeout=10)
    thread.join(timeout=0.05)  # the caller gives up waiting; the worker is still running
    assert not done.is_set() and _lease_state(store, chain.c_ref) == "busy"

    release.set()
    thread.join(timeout=10)
    assert done.is_set() and _lease_state(store, chain.c_ref) == "free"


def test_a_parent_closed_before_the_claim_refuses_and_never_runs_the_body(
    placed: Placed, chain: Chain
) -> None:
    store = placed.store()
    root, started = _root_authority(store, chain)
    started.close()
    calls: list[object] = []

    with pytest.raises(ChildResumeRefusedError) as caught:
        root.run_with_child_authority(chain.c, calls.append)

    assert caught.value.reason is ChildResumeRefusal.CLAIM_REFUSED and calls == []
    assert not store.paths_for(chain.c_ref).claim.exists()


def test_a_child_already_claimed_finishes_after_its_parent_closes(
    placed: Placed, chain: Chain
) -> None:
    store = placed.store()
    root, started = _root_authority(store, chain)
    inside: list[str] = []

    def body(_child: ClaimedChildAdmission) -> str:
        started.close()  # the parent's run returned while this child is still running
        inside.append(_lease_state(store, chain.c_ref))
        return "finished"

    assert root.run_with_child_authority(chain.c, body) == "finished"
    assert inside == ["busy"] and _lease_state(store, chain.c_ref) == "free"


def test_a_grandchild_is_admitted_through_its_childs_authority_never_the_roots(
    placed: Placed, chain: Chain
) -> None:
    store = placed.store()
    root, _started = _root_authority(store, chain)
    grand: list[str] = []

    def child_body(child: ClaimedChildAdmission) -> str:
        with pytest.raises(ChildResumeRefusedError) as caught:
            root.run_with_child_authority(chain.g, lambda _g: "no")  # the root does not carry G
        assert caught.value.reason is ChildResumeRefusal.CLAIM_REFUSED
        return child.run_with_child_authority(chain.g, lambda _g: grand.append("ran") or "g")

    assert root.run_with_child_authority(chain.c, child_body) == "g" and grand == ["ran"]


def test_an_authority_exposes_no_way_to_release_its_own_lease(placed: Placed, chain: Chain) -> None:
    store = placed.store()
    root, _started = _root_authority(store, chain)
    exposed: list[list[str]] = []

    root.run_with_child_authority(
        chain.c, lambda child: exposed.append([n for n in dir(child) if not n.startswith("_")])
    )

    assert exposed and all("close" not in name for name in exposed[0])


# --- the runner honors only the exact Runtime type ----------------------------------------------


class _ExecuteSpy:
    def __init__(self, inside: Any = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self.inside = inside

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self.inside is not None:
            self.inside(kwargs["child_resume_authority"])
        return cast(Any, object())


def _runner(placed: Placed, admission: Any, spy: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setattr(cwr, "execute_workflow_at_depth", spy)
    protocol = _protocol(JournalWorkflowPauseStore(journal_dir=placed.journal_dir, tenant_id=None))
    ctx = SimpleNamespace(pause_resume_protocol=protocol, step_dispatchers={})
    return cwr.compose_child_workflow_runner(cast(Any, ctx), durable_admission=admission)


def _resume(runner: Any, capture: PausedChildCapture, depth: int, authority: Any) -> Any:
    return runner(
        workflow_id=capture.child_workflow_id,
        manifest_entry=cast(Any, None),
        steps=(),
        handoff_context=cast(Any, None),
        descent=cast(Any, SimpleNamespace(child_gate_level=None)),
        default_model_binding=cast(Any, None),
        descent_depth=depth,
        child_resume=capture,
        child_resume_authority=authority,
    )


class _Fake:
    """Duck-types `run_admitted`, exactly what CP's Protocol demands; must never be trusted."""

    def __init__(self) -> None:
        self.calls = 0

    def run_admitted(self, verified: Any, body: Any) -> Any:
        self.calls += 1
        return body()


class _Subclass(ClaimedChildAdmission):
    pass


@pytest.mark.parametrize("kind", ["none", "fake", "subclass"])
def test_a_missing_wrong_or_fake_authority_keeps_the_refusing_binding_and_never_runs_the_body(
    placed: Placed, chain: Chain, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    store = placed.store()
    real, _started = _root_authority(store, chain)
    fake = _Fake()
    authority = {
        "none": None,
        "fake": fake,
        "subclass": _Subclass(store, _started),
    }[kind]
    del real
    spy = _ExecuteSpy()
    runner = _runner(placed, RefuseDurableChildAdmission(), spy, monkeypatch)

    with pytest.raises(ChildResumeRefusedError) as caught:
        _resume(runner, chain.capture(chain.c_ref, chain.c_snap), 1, authority)

    assert caught.value.reason is ChildResumeRefusal.GATEWAY_NOT_INSTALLED
    assert spy.calls == [] and fake.calls == 0
    assert not store.paths_for(chain.c_ref).claim.exists()


def test_the_child_runs_with_its_own_authority_and_the_grandchild_must_use_it(
    placed: Placed, chain: Chain, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = placed.store()
    root, _started = _root_authority(store, chain)
    forwarded: list[Any] = []
    grand: list[str] = []

    def inside(child_authority: Any) -> None:
        forwarded.append(child_authority)
        assert _lease_state(store, chain.c_ref) == "busy"
        with pytest.raises(ChildResumeRefusedError):
            root.run_with_child_authority(chain.g, lambda _g: grand.append("root"))
        child_authority.run_with_child_authority(chain.g, lambda _g: grand.append("child"))

    spy = _ExecuteSpy(inside)
    runner = _runner(placed, RefuseDurableChildAdmission(), spy, monkeypatch)

    _resume(runner, chain.capture(chain.c_ref, chain.c_snap), 1, root)

    (child_authority,) = forwarded
    assert type(child_authority) is ClaimedChildAdmission and child_authority is not root
    assert grand == ["child"] and _lease_state(store, chain.c_ref) == "free"


# --- dispatch threads the CP field beside `child_resume` ----------------------------------------


def test_dispatch_threads_the_step_contexts_authority_into_the_runner(tmp_path: Path) -> None:
    dispatcher, runner, _ = _dispatcher(tmp_path)
    authority = _Fake()
    context = _step_context().model_copy(update={"child_resume_authority": authority})

    dispatcher.dispatch(_binding(), _step(_payload()), step_context=context)
    dispatcher.dispatch(_binding(), _step(_payload()), step_context=_step_context())

    assert runner.calls[0]["child_resume_authority"] is authority
    assert runner.calls[1]["child_resume_authority"] is None


# --- no production entry can supply an authority ------------------------------------------------


def test_stage_five_and_the_root_entries_still_supply_no_authority() -> None:
    src = Path(cwr.__file__).resolve().parents[1]

    assert (
        "durable_admission=RefuseDurableChildAdmission()"
        in (src / "bootstrap" / "stage_5_loop_init.py").read_text()
    )
    for path in src.rglob("*.py"):
        if path.name in {"claimed_child_admission.py", "child_workflow_runner.py"}:
            continue
        assert "ClaimedChildAdmission" not in path.read_text(), path
        if path.name != "sub_agent_dispatch.py":
            assert "child_resume_authority" not in path.read_text(), path

"""B-104 Task 5a F4: the non-invoking started-body gateway and the `run_admitted` seam.

Nothing here resumes a real child or wires `api.resume`; the gateway is a unit no production
path calls. A counting body stands in for the child, over the real placed claim store, so the
ORDER is proven on the real code path: claim, fsync'd `started`, body, one release.
"""

from __future__ import annotations

import ast
import contextlib
import os
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from harness_core import JournalRecordRef
from harness_cp.workflow_driver_types import ChildResumeRefusal, ChildResumeRefusedError
from harness_runtime.lifecycle import child_workflow_runner as cwr
from harness_runtime.lifecycle import resume_claim_store as rcs
from harness_runtime.lifecycle.durable_child_admission import (
    RefuseDurableChildAdmission,
    VerifiedChildRecord,
)
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimBusyError,
    ClaimRefusedError,
    HeldClaim,
    HeldLease,
    LeaseBusy,
    ParentCarriedAdmission,
    ResumeClaimStore,
    RootLatestAdmission,
    StartedClaim,
    StartedOrUnknown,
    StartedProof,
    UnstartedProof,
    parse_claim,
)

from .test_b104_resume_claim_started import (
    Family,
    _started_parent,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import family as family  # fixture
from .test_b104_resume_claim_store import (
    _ABSENT,  # pyright: ignore[reportPrivateUsage]
    Placed,
    _capture,  # pyright: ignore[reportPrivateUsage]
    _capture_with_recorded_depth,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_store import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")

_SRC = Path(rcs.__file__).resolve().parents[1]  # harness_runtime package directory


def _gateway() -> Any:
    from harness_runtime.lifecycle import started_body_gateway

    return started_body_gateway


class _Body:
    """A body that records how often it ran and what the disk showed inside.

    It takes the started proof `run_started` hands its body, or nothing when a
    `run_admitted` seam calls it.
    """

    def __init__(self, store: ResumeClaimStore, ref: JournalRecordRef) -> None:
        self.store, self.ref = store, ref
        self.calls = 0
        self.claim_phase: str | None = None
        self.lease_seen: type | None = None

    def __call__(self, *_started: StartedProof) -> str:
        self.calls += 1
        state = parse_claim(self.store.paths_for(self.ref).claim.read_bytes(), self.ref)
        self.claim_phase = state.phase if isinstance(state, StartedOrUnknown) else None
        self.lease_seen = type(self.store.probe_lease(self.ref))
        return "ran"


@contextlib.contextmanager
def _gateway_refusal(phase: str, cause_type: type[Exception]) -> Generator[None]:
    """Expect the gateway's typed refusal: the phase and the original cause, by type."""
    with pytest.raises(_gateway().GatewayRefusal) as caught:
        yield
    refusal = caught.value
    assert refusal.phase is _gateway().GatewayPhase(phase)
    assert type(refusal.cause) is cause_type and refusal.__cause__ is refusal.cause
    assert str(refusal) == str(refusal.cause)  # the original text is retained for humans


def _lease_is_free(store: ResumeClaimStore, ref: JournalRecordRef) -> bool:
    probe = store.probe_lease(ref)
    if isinstance(probe, HeldLease):
        probe.close()
        return True
    return False


class _CloseCounter:
    """Counts every `HeldClaim.close` call so a single release is observable."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.count = 0
        real = HeldClaim.close

        def counting(held: HeldClaim) -> None:
            self.count += 1
            real(held)

        monkeypatch.setattr(HeldClaim, "close", counting)


# --- the gateway order -------------------------------------------------------------------------


def test_a_root_claim_runs_the_body_only_after_a_durable_started_and_holds_the_lease(
    placed: Placed,
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    body = _Body(store, ref)

    result = _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert result == "ran" and body.calls == 1
    assert body.claim_phase == "started"  # the fsync'd frame was on disk at body entry
    assert body.lease_seen is LeaseBusy  # the child's lease was held for the whole body
    assert _lease_is_free(store, ref)  # and released afterwards
    assert isinstance(parse_claim(store.paths_for(ref).claim.read_bytes(), ref), StartedOrUnknown)


def test_a_stale_or_unadmitted_ref_never_reaches_the_body(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    _capture(placed.journal_dir)  # a newer record makes `ref` stale for root-latest admission
    store = placed.store()
    body = _Body(store, ref)

    with _gateway_refusal("claim", ClaimRefusedError):
        _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert body.calls == 0 and not store.paths_for(ref).claim.exists()


@pytest.mark.parametrize("depth", [1, 2, None, _ABSENT, -1, True, "0"])
def test_a_non_root_or_unknown_depth_root_request_never_reaches_the_body(
    placed: Placed, depth: object
) -> None:
    ref = _capture_with_recorded_depth(placed.journal_dir, depth)
    store = placed.store()
    body = _Body(store, ref)

    for admission in (RootLatestAdmission(), rcs._ROOT_LATEST):  # pyright: ignore[reportPrivateUsage]
        with _gateway_refusal("claim", ClaimRefusedError):
            _gateway().run_started(store, ref, admission, body)

    paths = store.paths_for(ref)
    assert body.calls == 0 and not paths.claim.exists() and not paths.lease.exists()


def test_a_busy_lease_never_reaches_the_body(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    store.claim(ref).close()
    store.paths_for(ref).claim.unlink()  # a lease with no claim, held elsewhere below
    other = store.probe_lease(ref)
    assert isinstance(other, HeldLease)
    body = _Body(store, ref)
    try:
        with _gateway_refusal("claim", ClaimBusyError):
            _gateway().run_started(store, ref, RootLatestAdmission(), body)
    finally:
        other.close()

    assert body.calls == 0


class _StartRefusingStore(ResumeClaimStore):
    """Injects a tombstone between the gateway's claim and its start."""

    def mark_started(self, held: HeldClaim, *, deadline_seconds: float | None = None):
        paths = self.paths_for(held.record_ref)
        (paths.journal.parent / (paths.tombstone_prefix + "0")).write_bytes(b"x")
        return super().mark_started(held, deadline_seconds=deadline_seconds)


def test_a_refused_start_leaves_the_body_uncalled_and_the_lease_released(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = _StartRefusingStore(placement=placed.placement(), tenant_id=None)
    body = _Body(store, ref)

    with _gateway_refusal("start", ClaimRefusedError):
        _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert body.calls == 0
    assert isinstance(parse_claim(store.paths_for(ref).claim.read_bytes(), ref), UnstartedProof)
    assert _lease_is_free(store, ref)


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


def test_an_fsync_fault_during_started_never_reaches_the_body_and_releases_the_lease(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _capture(placed.journal_dir)
    store = _FsyncFaultStore(placement=placed.placement(), tenant_id=None, patch=monkeypatch)
    body = _Body(store, ref)

    with _gateway_refusal("start", ClaimRefusedError):
        _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert body.calls == 0
    state = parse_claim(store.paths_for(ref).claim.read_bytes(), ref)
    assert not isinstance(state, UnstartedProof)  # started-or-invalid: never non-execution
    assert _lease_is_free(store, ref)


@pytest.mark.parametrize("exit_kind", ["return", "exception", "base-exception"])
def test_the_lease_is_released_exactly_once_on_every_body_exit(
    placed: Placed, monkeypatch: pytest.MonkeyPatch, exit_kind: str
) -> None:
    class _Stop(BaseException):
        pass

    ref = _capture(placed.journal_dir)
    store = placed.store()
    closes = _CloseCounter(monkeypatch)

    def body(_started: StartedProof) -> str:
        if exit_kind == "exception":
            raise RuntimeError("body failed")
        if exit_kind == "base-exception":
            raise _Stop()
        return "ok"

    if exit_kind == "return":
        assert _gateway().run_started(store, ref, RootLatestAdmission(), body) == "ok"
    else:
        with pytest.raises(RuntimeError if exit_kind == "exception" else _Stop):
            _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert closes.count == 1
    assert _lease_is_free(store, ref)
    # a body that failed after `started` leaves the claim started: never re-runnable, never
    # an unstarted proof that ordinary release could clear
    assert isinstance(parse_claim(store.paths_for(ref).claim.read_bytes(), ref), StartedOrUnknown)


def test_the_gateway_never_accepts_a_started_claim_from_its_caller() -> None:
    import inspect

    parameters = inspect.signature(_gateway().run_started).parameters

    assert not any("started" in name or "held" in name for name in parameters)
    assert all(
        p.annotation is not StartedClaim and p.annotation is not HeldClaim
        for p in parameters.values()
    )


# --- a child claims through its live started parent ---------------------------------------------


def test_a_started_parent_admits_a_child_body(placed: Placed, family: Family) -> None:
    store = placed.store()
    ref = family.child_refs[0]
    body = _Body(store, ref)
    with _started_parent(store, family) as parent:
        result = _gateway().run_started(store, ref, ParentCarriedAdmission(parent), body)

    assert result == "ran" and body.calls == 1 and body.claim_phase == "started"


def test_an_unstarted_parent_never_reaches_a_child_body(placed: Placed, family: Family) -> None:
    store = placed.store()
    ref = family.child_refs[0]
    body = _Body(store, ref)
    unstarted = store.claim(family.parent_ref, RootLatestAdmission())
    with unstarted:
        with _gateway_refusal("claim", ClaimRefusedError):
            _gateway().run_started(
                store, ref, ParentCarriedAdmission(StartedClaim(unstarted)), body
            )  # forged typestate over a claim that is only claimed

    assert body.calls == 0 and not store.paths_for(ref).claim.exists()


def test_a_closed_parent_never_reaches_a_child_body(placed: Placed, family: Family) -> None:
    store = placed.store()
    ref = family.child_refs[0]
    body = _Body(store, ref)
    closed = _started_parent(store, family)
    closed.close()

    with _gateway_refusal("claim", ClaimRefusedError):
        _gateway().run_started(store, ref, ParentCarriedAdmission(closed), body)

    assert body.calls == 0 and not store.paths_for(ref).claim.exists()


# --- the admission seam and the runner ----------------------------------------------------------


def test_the_refusing_binding_never_calls_the_body() -> None:
    calls: list[int] = []
    verified = cast(
        VerifiedChildRecord, SimpleNamespace(ref=SimpleNamespace(workflow_id="w", record_count=1))
    )

    with pytest.raises(ChildResumeRefusedError) as caught:
        RefuseDurableChildAdmission().run_admitted(verified, lambda: calls.append(1))  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue,reportUnknownLambdaType]

    assert caught.value.reason is ChildResumeRefusal.GATEWAY_NOT_INSTALLED and calls == []


def test_stage_five_still_binds_the_always_refusing_admission_and_nothing_calls_the_gateway() -> (
    None
):
    stage5 = (_SRC / "bootstrap" / "stage_5_loop_init.py").read_text()

    assert "durable_admission=RefuseDurableChildAdmission()" in stage5
    for path in _SRC.rglob("*.py"):
        if path.name in {
            "started_body_gateway.py",
            "claimed_child_admission.py",
            "root_resume_admission.py",
        }:
            continue  # the gateway, its child consumer (S1 test) and the one root consumer
        tree = ast.parse(path.read_text())
        names = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | {
            a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
        }
        assert not any("started_body_gateway" in name for name in names), path
        assert "run_started" not in path.read_text() or path.name == "started_body_gateway.py"


class _BodyRunningAdmission:
    """A permissive double that lets the body run only when it chooses to."""

    def __init__(self, *, run_body: bool) -> None:
        self.run_body = run_body
        self.seen: list[VerifiedChildRecord] = []

    def run_admitted(self, verified: VerifiedChildRecord, body: Callable[[], Any]) -> Any:
        self.seen.append(verified)
        return body() if self.run_body else "not-run"


class _DriverSpy:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        return cast(Any, object())


def _ephemeral_runner(admission: Any, monkeypatch: pytest.MonkeyPatch) -> tuple[Any, _DriverSpy]:
    spy = _DriverSpy()
    monkeypatch.setattr(cwr, "execute_workflow_at_depth", spy)
    ctx = SimpleNamespace(pause_resume_protocol=None, step_dispatchers={})
    return cwr.compose_child_workflow_runner(cast(Any, ctx), durable_admission=admission), spy


def _dispatch(runner: Any) -> Any:
    return runner(
        workflow_id="wf-c",
        manifest_entry=cast(Any, None),
        steps=(),
        handoff_context=cast(Any, None),
        descent=cast(Any, SimpleNamespace(child_gate_level=None)),
        default_model_binding=cast(Any, None),
        descent_depth=1,
    )


def test_a_first_dispatch_bypasses_the_admission_and_runs_the_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admission = _BodyRunningAdmission(run_body=False)
    runner, spy = _ephemeral_runner(admission, monkeypatch)

    _dispatch(runner)

    assert spy.calls == 1 and admission.seen == []


def test_a_durable_resumed_child_runs_only_when_the_admission_runs_its_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from .test_b104_task4c_durable_child_admission import (
        _resume,  # pyright: ignore[reportPrivateUsage]
        _runner_over,  # pyright: ignore[reportPrivateUsage]
        _Site,  # pyright: ignore[reportPrivateUsage]
    )

    site = _Site(tmp_path)
    holds = _BodyRunningAdmission(run_body=False)
    runner, spy = _runner_over(site.protocol, holds, monkeypatch)

    assert _resume(runner, site.c, depth=1) == "not-run"
    assert spy.calls == [] and [(v.ref, v.depth) for v in holds.seen] == [
        (site.c.child_record_ref, 1)
    ]

    runs = _BodyRunningAdmission(run_body=True)
    runner, spy = _runner_over(site.protocol, runs, monkeypatch)
    _resume(runner, site.c, depth=1)
    assert len(spy.calls) == 1 and len(runs.seen) == 1


def test_the_refusing_binding_leaves_a_durable_resumed_child_unrun(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from .test_b104_task4c_durable_child_admission import (
        _resume,  # pyright: ignore[reportPrivateUsage]
        _runner_over,  # pyright: ignore[reportPrivateUsage]
        _Site,  # pyright: ignore[reportPrivateUsage]
    )

    site = _Site(tmp_path)
    runner, spy = _runner_over(site.protocol, RefuseDurableChildAdmission(), monkeypatch)

    with pytest.raises(ChildResumeRefusedError) as caught:
        _resume(runner, site.c, depth=1)

    assert caught.value.reason is ChildResumeRefusal.GATEWAY_NOT_INSTALLED and spy.calls == []


# --- S1: the phase is typed, and only the two expected refusals are wrapped ----------------------


def test_a_ref_naming_no_exact_journal_record_is_a_claim_phase_refusal(
    placed: Placed, family: Family
) -> None:
    store = placed.store()
    other_ref = family.child_refs[
        1
    ]  # only names the body's disk view; the request below is not exact
    body = _Body(store, other_ref)
    with _started_parent(store, family) as parent:
        wrong = family.child_refs[0].model_copy(update={"latest_digest": "0" * 64})
        with _gateway_refusal("claim", ClaimRefusedError):
            _gateway().run_started(store, wrong, ParentCarriedAdmission(parent), body)

    assert body.calls == 0


def test_a_placement_fault_propagates_unchanged(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StateRootPlacementError

    from .test_b104_resume_claim_store import (
        _swap_marker,  # pyright: ignore[reportPrivateUsage]
    )

    ref = _capture(placed.journal_dir)
    store = placed.store()
    body = _Body(store, ref)
    _swap_marker(placed)

    with pytest.raises(StateRootPlacementError):
        _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert body.calls == 0


def test_a_journal_lock_timeout_propagates_unchanged(placed: Placed) -> None:
    from harness_core.cross_process_lock_deadline import CrossProcessLockTimeoutError
    from harness_runtime.lifecycle.journal_workflow_pause_store import cross_process_journal_lock

    ref = _capture(placed.journal_dir)
    store = placed.store()
    body = _Body(store, ref)

    with cross_process_journal_lock(store.paths_for(ref).journal):
        with pytest.raises(CrossProcessLockTimeoutError):
            _gateway().run_started(store, ref, RootLatestAdmission(), body, deadline_seconds=0.2)

    assert body.calls == 0


def test_a_raw_oserror_while_creating_the_claim_propagates_unchanged(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    body = _Body(store, ref)
    real = rcs._write_all  # pyright: ignore[reportPrivateUsage]

    def failing(fd: int, data: bytes) -> None:
        if b'"claimed"' in data:
            raise OSError(28, "injected write fault")
        real(fd, data)

    monkeypatch.setattr(rcs, "_write_all", failing)

    with pytest.raises(OSError, match="injected write fault") as caught:
        _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert type(caught.value) is OSError and body.calls == 0


def test_a_start_phase_busy_error_is_not_a_gateway_refusal(placed: Placed) -> None:
    """Only the two expected refusals are wrapped: START wraps ClaimRefusedError alone."""
    ref = _capture(placed.journal_dir)

    class _BusyAtStart(ResumeClaimStore):
        def mark_started(self, held: HeldClaim, *, deadline_seconds: float | None = None):
            raise ClaimBusyError("unexpected")

    store = _BusyAtStart(placement=placed.placement(), tenant_id=None)
    body = _Body(store, ref)

    with pytest.raises(ClaimBusyError):
        _gateway().run_started(store, ref, RootLatestAdmission(), body)

    assert body.calls == 0 and _lease_is_free(store, ref)

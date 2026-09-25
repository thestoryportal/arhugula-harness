"""B-104: a durable root `resume(resume_handle=...)` claims its exact record before its body.

Provider-free: the real bootstrap (providers and OD stages faked), a verified external state
root, the real durable journal, claim store and CP driver. Step dispatchers are stubs that look
at the claim and lease at the moment a step runs, so the ORDER is observed on the real path.
The carried-child test replaces only CP's `execute_workflow` with a stub that exercises the
authority the facade hands it. Nothing here is an installed-host, multi-process or crash witness.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from collections.abc import Callable, Coroutine, Sequence
from pathlib import Path
from typing import Any

import pytest
from harness_core import JournalRecordRef
from harness_core.identity import StepID
from harness_core.persona_tier import PersonaTier
from harness_core.workload_class import WorkloadClass
from harness_cp import workflow_driver
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol_types import WorkflowPauseReason
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import RunResult as CpRunResult
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_runtime import api as api_module
from harness_runtime import bootstrap as bootstrap_module
from harness_runtime.api import ResumeDirectChildHandleError, resume
from harness_runtime.bootstrap import stage_1_is
from harness_runtime.config import state_placement as sp
from harness_runtime.config.state_placement import (
    StatePlacementRefusal,
    StateRootPlacementError,
    place_state_dir,
)
from harness_runtime.lifecycle import resume_claim_store as rcs
from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    pause_journal_dir_for,
)
from harness_runtime.lifecycle.pause_resume_protocol_types import PauseResumeProtocolConfig
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimRefusedError,
    HeldLease,
    InvalidClaim,
    LeaseBusy,
    LeaseMissing,
    ResumeClaimStore,
    StartedOrUnknown,
    UnstartedProof,
    parse_claim,
)
from harness_runtime.shutdown import shutdown
from harness_runtime.types import RuntimeConfig

from .integration.test_r_cc_1_api_resume import (
    _CHAIN,  # pyright: ignore[reportPrivateUsage]
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
)
from .test_b104_5b1_runtime_handoff import Chain
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)
from .test_state_placement_bootstrap import Site

pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock"),
    pytest.mark.usefixtures("_patched_runtime"),
]

_WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING
_WORKFLOW_ID = "wf-b104-root"


def _ext4(_path: Path) -> str | None:
    return "ext4"


@pytest.fixture(autouse=True)
def _durable_filesystem(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scratch dirs may be tmpfs; the verifier's real resolver is covered in test_state_placement."""
    monkeypatch.setattr(stage_1_is, "linux_filesystem_type", _ext4)
    monkeypatch.setattr(sp, "linux_filesystem_type", _ext4)


# --- a workflow whose one step reports what it sees ---------------------------------------------


class _Dispatcher:
    """A stub step dispatcher; `observe` runs at the instant the step is dispatched."""

    def __init__(self, observe: Callable[[], object] = lambda: None, *, fail: bool = False) -> None:
        self.steps: list[str] = []
        self._observe = observe
        self._fail = fail

    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        _ = binding, step_context
        self.steps.append(str(step.step_id))
        self._observe()
        if self._fail:
            raise RuntimeError("the resumed body failed")
        return {"step_id": str(step.step_id), "ok": True}


class _Registry:
    def __init__(self, dispatcher: _Dispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: Any) -> _Dispatcher:
        _ = step_kind
        return self._dispatcher


class _Workflow:
    workload_class = _WORKLOAD
    default_model_binding = ModelBinding(provider="anthropic", model="claude-haiku-4-5")

    def __init__(self, dispatcher: _Dispatcher, workflow_id: str = _WORKFLOW_ID) -> None:
        self.workflow_id = workflow_id
        self.step_dispatchers = _Registry(dispatcher)
        self.steps: Sequence[WorkflowStep] = (
            WorkflowStep(
                step_id=StepID("step-0"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
            ),
        )
        self.manifest_entry = WorkflowManifestEntry(
            workflow_id=workflow_id,
            workload_class=_WORKLOAD,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(),
            per_step_overrides={},
        )


# --- a placed site: the journal, claims and leases all live under the verified root -------------


class Harness:
    def __init__(
        self,
        scratch: Path,
        *,
        placement: bool = True,
        drain: float = 60.0,
        ledger: str = "state-ledger",
    ) -> None:
        self.site = Site(scratch / "site")
        self._placement = placement
        self._drain = drain
        self.config = self.config_with_ledger(self.site.root / ledger)
        self.journal_dir = pause_journal_dir_for(self.site.root / ledger)

    def config_with_ledger(self, ledger: Path) -> RuntimeConfig:
        """This site's config with its STATE_LEDGER cell bound to `ledger`."""
        return self.site.config(
            placement=self._placement,
            ledger=ledger,
            ollama_optional=True,
            pause_resume_protocol_config=PauseResumeProtocolConfig(durable=True),
            routing_manifest=RoutingManifest(
                manifest_version=1,
                per_role_bindings={},
                per_workload_overrides={},
                fallback_chains=(_CHAIN,),
                retry_policies={},
            ),
            drain_timeout_seconds=self._drain,
        )

    async def capture_root(self, run_id: str = "run-root") -> JournalRecordRef:
        """Pause through the real durable protocol of a bootstrapped harness (the capture side)."""
        ctx = await bootstrap_module.run_bootstrap(self.config, workload_class=_WORKLOAD)
        try:
            assert ctx.pause_resume_protocol is not None
            captured = await ctx.pause_resume_protocol.capture_pause_snapshot(
                workflow_id=_WORKFLOW_ID,
                run_id=run_id,
                step_index=0,
                pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
                descent_depth=0,
            )
        finally:
            await shutdown(ctx)
        ref = getattr(captured, "record_ref", None)
        assert isinstance(ref, JournalRecordRef)
        return ref

    def journal(self) -> JournalWorkflowPauseStore:
        return JournalWorkflowPauseStore(journal_dir=self.journal_dir, tenant_id=None)

    def store(self) -> ResumeClaimStore:
        placement = place_state_dir(
            self.journal_dir,
            self.config,
            self.site.stamp(self.config),
            what="test pause journal",
            filesystem_type=_ext4,
        )
        return ResumeClaimStore(placement=placement, tenant_id=None)

    def phase(self, ref: JournalRecordRef) -> str:
        claim = self.store().paths_for(ref).claim
        if not claim.exists():
            return "none"
        match parse_claim(claim.read_bytes(), ref):
            case UnstartedProof():
                return "claimed"
            case StartedOrUnknown(phase=phase):
                return phase
            case InvalidClaim():
                return "invalid"

    def lease(self, ref: JournalRecordRef) -> str:
        probe = self.store().probe_lease(ref)
        if isinstance(probe, HeldLease):
            probe.close()
            return "free"
        return {LeaseBusy: "busy", LeaseMissing: "missing"}.get(type(probe), "invalid")

    def claim_files(self) -> list[Path]:
        return sorted(
            p
            for p in self.site.base.rglob("*")
            if ".resume-claim-" in p.name or ".resume-lease-" in p.name
        )


@pytest.fixture
def harness(world: Path) -> Harness:  # noqa: F811
    return Harness(world)


async def _outcome(call: Coroutine[Any, Any, Any]) -> Any:
    """The call's result, or the exception it raised (so body-count assertions run first)."""
    try:
        return await call
    except Exception as exc:
        return exc


def _assert_refused(outcome: object, reason: str) -> None:
    refused = getattr(api_module, "ResumeClaimRefusedError", None)
    assert refused is not None and isinstance(outcome, refused), outcome
    assert getattr(outcome, "reason", None) == reason
    assert "/" not in str(outcome)  # names no filesystem path


# --- started before the body; the lease is held through it --------------------------------------


@pytest.mark.asyncio
async def test_the_started_frame_is_durable_before_the_first_step_and_the_lease_spans_the_body(
    harness: Harness,
) -> None:
    ref = await harness.capture_root()
    seen: list[tuple[str, str]] = []
    dispatcher = _Dispatcher(lambda: seen.append((harness.phase(ref), harness.lease(ref))))

    result = await resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)

    assert result.status == "completed", result
    assert seen == [("started", "busy")]
    assert (harness.phase(ref), harness.lease(ref)) == ("started", "free")


@pytest.mark.asyncio
async def test_the_claim_sits_in_the_directory_capture_wrote_and_resume_read(
    harness: Harness,
) -> None:
    ref = await harness.capture_root()
    journal_file = harness.store().paths_for(ref).journal

    await resume(_Workflow(_Dispatcher()), resume_handle=_WORKFLOW_ID, config=harness.config)

    claim, lease = harness.store().paths_for(ref).claim, harness.store().paths_for(ref).lease
    assert journal_file.exists() and journal_file.parent == harness.journal_dir
    assert harness.claim_files() == sorted([claim, lease])  # no second address anywhere


# --- at most once -------------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("first_body", ["completed", "raised"])
async def test_a_second_resume_of_the_same_record_is_refused_and_runs_nothing(
    harness: Harness, first_body: str
) -> None:
    ref = await harness.capture_root()
    first = _Dispatcher(fail=first_body == "raised")
    await _outcome(resume(_Workflow(first), resume_handle=_WORKFLOW_ID, config=harness.config))
    assert first.steps == ["step-0"]

    second = _Dispatcher()
    outcome = await _outcome(
        resume(_Workflow(second), resume_handle=_WORKFLOW_ID, config=harness.config)
    )

    assert second.steps == []
    _assert_refused(outcome, "claim-refused")
    assert (harness.phase(ref), harness.lease(ref)) == ("started", "free")


@pytest.mark.asyncio
async def test_a_record_superseded_between_the_read_and_the_claim_is_refused(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref_n = await harness.capture_root()
    real = bootstrap_module.run_bootstrap
    appended: list[JournalRecordRef] = []

    async def bootstrap_then_append(*args: Any, **kwargs: Any) -> Any:
        ctx = await real(*args, **kwargs)
        # After resume's pre-bootstrap read of N, before the worker claims: N+1 lands.
        latest = harness.journal().read_latest(_WORKFLOW_ID)
        assert latest is not None
        appended.append(harness.journal().capture(latest, depth=0))
        return ctx

    monkeypatch.setattr(bootstrap_module, "run_bootstrap", bootstrap_then_append)
    dispatcher = _Dispatcher()

    outcome = await _outcome(
        resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)
    )

    assert dispatcher.steps == [] and len(appended) == 1
    _assert_refused(outcome, "claim-refused")
    assert harness.phase(ref_n) == "none" and harness.phase(appended[0]) == "none"


@pytest.mark.asyncio
async def test_of_byte_identical_records_n_and_n_plus_1_only_the_latest_is_claimed(
    harness: Harness,
) -> None:
    ref_n = await harness.capture_root()
    latest = harness.journal().read_latest(_WORKFLOW_ID)
    assert latest is not None
    ref_n1 = harness.journal().capture(latest, depth=0)  # the same snapshot, one position later
    dispatcher = _Dispatcher()

    result = await resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)

    assert result.status == "completed" and dispatcher.steps == ["step-0"]
    assert (harness.phase(ref_n1), harness.phase(ref_n)) == ("started", "none")
    with pytest.raises(ClaimRefusedError):
        harness.store().claim(ref_n)  # N is positional now, never the current root


# --- refusals before the body ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_live_lease_holder_makes_the_resume_busy_and_runs_nothing(
    harness: Harness,
) -> None:
    ref = await harness.capture_root()
    store = harness.store()
    store.claim(ref).close()
    store.paths_for(ref).claim.unlink()  # leave a published lease, held by "another" below
    other = store.probe_lease(ref)
    assert isinstance(other, HeldLease)
    dispatcher = _Dispatcher()
    try:
        outcome = await _outcome(
            resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)
        )
    finally:
        other.close()

    assert dispatcher.steps == []
    _assert_refused(outcome, "claim-busy")
    assert harness.phase(ref) == "none"


def _fail_started_write(monkeypatch: pytest.MonkeyPatch) -> None:
    real = rcs._write_all  # pyright: ignore[reportPrivateUsage]

    def failing(fd: int, data: bytes) -> None:
        if b'"started"' in data:
            raise OSError(28, "injected started-write fault")
        real(fd, data)

    monkeypatch.setattr(rcs, "_write_all", failing)


def _fail_started_fsync(monkeypatch: pytest.MonkeyPatch) -> None:
    real = os.fsync

    def failing(fd: int) -> None:
        target = Path(os.readlink(f"/proc/self/fd/{fd}"))
        if ".resume-claim-" in target.name and b'"started"' in target.read_bytes():
            raise OSError(5, "injected started-fsync fault")
        real(fd)

    monkeypatch.setattr(os, "fsync", failing)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fault", "left"), [(_fail_started_write, "claimed"), (_fail_started_fsync, "started")]
)
async def test_a_start_that_is_not_durable_runs_nothing_and_the_record_stays_barred(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
    fault: Callable[[pytest.MonkeyPatch], None],
    left: str,
) -> None:
    if fault is _fail_started_fsync and not Path("/proc/self/fd").is_dir():
        pytest.skip("needs /proc to target the claim file's fsync")
    ref = await harness.capture_root()
    first = _Dispatcher()
    with monkeypatch.context() as patch:
        fault(patch)
        outcome = await _outcome(
            resume(_Workflow(first), resume_handle=_WORKFLOW_ID, config=harness.config)
        )

    assert first.steps == []
    _assert_refused(outcome, "start-refused")
    assert isinstance(getattr(outcome, "__cause__", None), Exception)
    assert (harness.phase(ref), harness.lease(ref)) == (left, "free")

    later = _Dispatcher()
    again = await _outcome(
        resume(_Workflow(later), resume_handle=_WORKFLOW_ID, config=harness.config)
    )
    assert later.steps == []
    _assert_refused(again, "claim-refused")


def _eventually(predicate: Callable[[], bool], *, within: float = 20.0) -> bool:
    """Wait for a state the worker owns (the lease release), bounded; not a settle delay."""
    deadline = time.monotonic() + within
    while not predicate():
        if time.monotonic() > deadline:
            return False
        time.sleep(0.01)
    return True


@pytest.mark.asyncio
async def test_after_a_drain_timeout_the_worker_keeps_the_lease_until_its_body_returns(
    world: Path,  # noqa: F811
) -> None:
    harness = Harness(world, drain=0.5)
    ref = await harness.capture_root()
    entered, release = threading.Event(), threading.Event()

    def block() -> None:
        entered.set()
        release.wait(timeout=30)

    try:
        result = await resume(
            _Workflow(_Dispatcher(block)), resume_handle=_WORKFLOW_ID, config=harness.config
        )

        assert result.status == "drained", result
        assert entered.wait(timeout=10)
        assert (harness.phase(ref), harness.lease(ref)) == ("started", "busy")
    finally:
        release.set()
    assert _eventually(lambda: harness.lease(ref) == "free")
    assert harness.phase(ref) == "started"


# --- the record is claimed only where it was read, and only if bootstrap captures there ---------


def _changing_bootstrap(
    monkeypatch: pytest.MonkeyPatch, change: Callable[[RuntimeConfig], RuntimeConfig]
) -> None:
    """Run `change` after resume's pre-bootstrap read and before the real bootstrap."""
    real = bootstrap_module.run_bootstrap

    async def bootstrap(config: RuntimeConfig, **kwargs: Any) -> Any:
        return await real(change(config), **kwargs)

    monkeypatch.setattr(bootstrap_module, "run_bootstrap", bootstrap)


def _retargeted_link(scratch: Path) -> tuple[Harness, Path]:
    """A site whose STATE_LEDGER binding is a symlink inside the root, now naming `a`."""
    harness = Harness(scratch, ledger="ledger-link")
    harness.site.stamp(harness.config)  # the placed root exists before the link is made
    (harness.site.root / "state-ledger-a").mkdir()
    link = harness.site.root / "ledger-link"
    link.symlink_to(harness.site.root / "state-ledger-a")
    return harness, link


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["rebound", "retargeted"])
async def test_a_capture_directory_changed_between_read_and_bootstrap_refuses_before_any_claim(
    world: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
    change: str,
) -> None:
    if change == "rebound":
        harness = Harness(world)
        await harness.capture_root()
        other = harness.site.root / "state-ledger-b"  # still inside the verified root
        _changing_bootstrap(monkeypatch, lambda _config: harness.config_with_ledger(other))
    else:
        harness, link = _retargeted_link(world)
        await harness.capture_root()

        def retarget(config: RuntimeConfig) -> RuntimeConfig:
            (harness.site.root / "state-ledger-b").mkdir()
            link.unlink()
            link.symlink_to(harness.site.root / "state-ledger-b")  # same binding, new target
            return config

        _changing_bootstrap(monkeypatch, retarget)
    dispatcher = _Dispatcher()

    outcome = await _outcome(
        resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)
    )

    assert dispatcher.steps == []
    _assert_refused(outcome, "placement")
    assert type(getattr(outcome, "__cause__", None)).__name__ == "JournalDirectoryMismatchError"
    assert harness.claim_files() == []  # no claim or lease in either directory


@pytest.mark.asyncio
@pytest.mark.parametrize("ledger", ["state-ledger", "ledger-link"])
async def test_a_capture_directory_unchanged_through_bootstrap_is_claimed_and_run(
    world: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
    ledger: str,
) -> None:
    harness = _retargeted_link(world)[0] if ledger == "ledger-link" else Harness(world)
    ref = await harness.capture_root()
    _changing_bootstrap(monkeypatch, lambda config: config)  # the same binding and target
    dispatcher = _Dispatcher()

    result = await resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)

    assert result.status == "completed", result
    assert dispatcher.steps == ["step-0"]
    assert (harness.phase(ref), harness.lease(ref)) == ("started", "free")


# --- the root authority reaches CP and admits carried children exactly -------------------------


@pytest.mark.asyncio
async def test_the_root_authority_admits_its_carried_child_and_the_child_admits_the_grandchild(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    harness.site.stamp(harness.config)  # the placed root exists before the journal is written
    chain = Chain(harness.journal_dir)
    seen: dict[str, Any] = {}

    def execute(manifest_entry: Any, steps: Any, run_id: str, ctx: Any, **kwargs: Any) -> Any:
        _ = steps, ctx
        authority = kwargs.get("child_resume_authority")
        seen["authority"] = authority
        seen["root"] = (harness.phase(chain.p_ref), harness.lease(chain.p_ref))

        def grand_body(_grand: ClaimedChildAdmission) -> None:
            seen["grand"] = (harness.phase(chain.g_ref), harness.lease(chain.g_ref))

        def child_body(child: ClaimedChildAdmission) -> None:
            seen["child"] = (harness.phase(chain.c_ref), harness.lease(chain.c_ref))
            child.run_with_child_authority(chain.g, grand_body)

        authority.run_with_child_authority(chain.c, child_body)
        return CpRunResult(
            workflow_id=manifest_entry.workflow_id,
            run_id=run_id,
            status=RunStatus.SUCCESS,
            terminal_step_index=0,
            partial_state=None,
            final_state={},
            fail_class=None,
        )

    monkeypatch.setattr(workflow_driver, "execute_workflow", execute)

    outcome = await _outcome(
        resume(_Workflow(_Dispatcher(), "wf-p"), resume_handle="wf-p", config=harness.config)
    )

    assert type(seen.get("authority")) is ClaimedChildAdmission, outcome
    assert seen["root"] == ("started", "busy")
    assert seen["child"] == ("started", "busy") and seen["grand"] == ("started", "busy")
    assert getattr(outcome, "status", None) == "completed", outcome
    for ref in (chain.p_ref, chain.c_ref, chain.g_ref):
        assert (harness.phase(ref), harness.lease(ref)) == ("started", "free")


# --- what stays as it was ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_direct_child_handle_is_still_refused_with_no_claim(harness: Harness) -> None:
    harness.site.stamp(harness.config)
    chain = Chain(harness.journal_dir)
    dispatcher = _Dispatcher()

    outcome = await _outcome(
        resume(_Workflow(dispatcher, "wf-c"), resume_handle="wf-c", config=harness.config)
    )

    assert isinstance(outcome, ResumeDirectChildHandleError) and outcome.depth == 1
    assert dispatcher.steps == [] and harness.claim_files() == []
    assert harness.phase(chain.c_ref) == "none"


@pytest.mark.asyncio
async def test_a_durable_handle_without_a_declared_placement_is_refused_before_the_body(
    world: Path,  # noqa: F811
) -> None:
    harness = Harness(world, placement=False)
    await harness.capture_root()
    dispatcher = _Dispatcher()

    outcome = await _outcome(
        resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)
    )

    assert dispatcher.steps == []
    _assert_refused(outcome, "placement")
    cause = getattr(outcome, "__cause__", None)
    assert isinstance(cause, StateRootPlacementError)
    assert cause.reason is StatePlacementRefusal.PLACEMENT_REQUIRED
    assert harness.claim_files() == []


@pytest.mark.asyncio
async def test_a_caller_supplied_snapshot_takes_no_claim_and_hands_cp_no_authority(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = await harness.capture_root()
    snapshot = harness.journal().read_latest(_WORKFLOW_ID)
    assert snapshot is not None
    dispatcher = _Dispatcher()

    for _ in range(2):  # not sticky: a caller-supplied snapshot is outside the claim contract
        result = await resume(_Workflow(dispatcher), pause_snapshot=snapshot, config=harness.config)
        assert result.status == "completed", result

    assert dispatcher.steps == ["step-0", "step-0"]
    assert harness.claim_files() == [] and harness.phase(ref) == "none"

    authorities: list[object] = []
    real = workflow_driver.execute_workflow

    def spy(*args: Any, **kwargs: Any) -> Any:
        authorities.append(kwargs.get("child_resume_authority"))
        return real(*args, **kwargs)

    monkeypatch.setattr(workflow_driver, "execute_workflow", spy)
    await resume(_Workflow(_Dispatcher()), pause_snapshot=snapshot, config=harness.config)
    assert authorities == [None]

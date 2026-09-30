"""Behavioral witnesses for the `proceed`-tier completed-vs-deadline outcome seam in
`_execute_parallelization` and `_execute_orchestrator_workers` (`workflow_driver.py`, both
copies: PARALLELIZATION's own strategy, and ORCHESTRATOR_WORKERS's, which HIERARCHICAL_DELEGATION
also runs through).

The production fix restructures a `try` / `except (BranchBarrierDeadlineExceededError,
TimeoutError)` into `try` / `except` / `else`, so `results` (previously possibly-unbound to
pyright, though never actually reachable unbound) is read only inside the `else` clause, which
Python's own control flow guarantees runs exactly when the `try` body completed without raising.
The refused-child check is factored into one local `_refused_result()` helper called from both
branches, so `_finish(...)`'s construction for a refusal is not duplicated.

None of these tests captures or resumes a pause snapshot: every worker here is a FRESH,
first-attempt dispatch. A refused worker under this shape is THEREFORE NOT the Q-L=A "resumed
paused child" the N1 Path P prerequisite pins cover — it is a pre-effect fresh refusal, which
`_synthesize_undispatched_terminals` records as `cancelled` (arm 6: no disposition of any kind is
recorded for it, so `_dispatched_boundary` is `False`). Only a worker whose OWN dispatch actually
ran to a captured pause (`paused_child_dispositions`) records `completed` (arm 4). This file
initially asserted `completed` for a fresh refusal too; that was wrong, confirmed by an actual
run (`cp-focused-verification-after19/results.json`: 6 of 16 cases failed on exactly this point,
across both families and every refusal-involving case) and corrected below.

Known, stated limitations (not claimed resolved):
- The deadline-racing-refusal test remains TIME-BOUNDED, not deterministic: this file owns no
  seam inside `workflow_driver.py` to observe the moment `child_resume_refused_dispositions` is
  actually written, so it cannot prove the refusal was recorded before the barrier deadline
  fired — only that the deadline value used is large (1.5s) relative to a synchronous, no-I/O
  raise. A worker-dispatched signal set before the raise (an earlier draft) proved nothing about
  this and has been removed rather than left as a misleading comment.
- Deadline cases remain scheduling-dependent: `_run_fanout_to_completion` abandons the
  executor with `shutdown(wait=False)` on a caught deadline, while the blocked worker's own
  wait is bounded at 3s. The tests assert outcomes, not elapsed-time guarantees.
"""

from __future__ import annotations

import asyncio
import threading

import pytest
from harness_core import PersonaTier, StepID, WorkflowEventClass, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import (
    PausedChildCapture,
    PauseSnapshot,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    LedgerReaderLike,
    LedgerWriterLike,
    LifecycleEventEmitterLike,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    ChildResumeRefusal,
    ChildResumeRefusedError,
    RunResult,
    RunStatus,
    StepExecutionContext,
    StepKind,
    SubAgentChildPausedError,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_read import BoundedWindow, ReadResult
from harness_is.state_ledger_write import EntryPayload, WriteKey

_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-project-typing-workflow-outcomes")

_FAMILY_SHAPE = {"PARALLELIZATION": "peer", "ORCHESTRATOR_WORKERS": "fan_out"}
_FAMILIES = tuple(_FAMILY_SHAPE)


class NullLedgerReader:
    """A real `LedgerReaderLike` (`workflow_driver.py:363-393`). This seam never exercises
    replay-resumption reads, but `DriverContext.ledger_reader` is non-Optional, so a real (if
    inert) implementer is required."""

    def read_by_idempotency_key(
        self, idempotency_key: Identifier, bounded_window: BoundedWindow
    ) -> ReadResult:
        del idempotency_key, bounded_window
        raise NotImplementedError("not exercised by this seam's tests")


class RecordingLedger:
    """A real `LedgerWriterLike` (`workflow_driver.py:338-359`)."""

    def __init__(self) -> None:
        self.actor: Actor = _ACTOR
        self.appends: list[tuple[EntryPayload, WriteKey]] = []

    def append(self, payload: EntryPayload, write_key: WriteKey) -> str:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return len(self.appends) == 0

    @property
    def entry_count(self) -> int:
        return len(self.appends)

    def terminals(self) -> dict[int, str]:
        """`{branch_index: terminal_status}` for every append carrying one."""
        out: dict[int, str] = {}
        for payload, _write_key in self.appends:
            metadata = getattr(payload, "branch_metadata", None)
            if metadata is not None and metadata.terminal_status is not None:
                out[metadata.branch_index] = metadata.terminal_status
        return out


class Emitter:
    """A real `LifecycleEventEmitterLike` (`workflow_driver.py:395-405`)."""

    def __init__(self) -> None:
        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: WorkflowEventClass) -> None:
        self.emits.append(event_class)


class Ctx:
    """A real `DriverContext` (`workflow_driver.py:536-657`). Every field is declared with the
    Protocol's own type (not merely inferred from the assigned value), so a mutable-attribute
    structural check accepts `Ctx` with no `cast(...)` at any call site. `pause_resume_protocol`
    is `None` throughout (an explicitly Optional field) — this file exercises fresh-dispatch
    refusal / deadline / ordinary-failure / paused-child / success outcomes only, never a
    captured resumable pause."""

    def __init__(self, *, ledger: RecordingLedger, emitter: Emitter) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer: LedgerWriterLike = ledger
        self.ledger_reader: LedgerReaderLike = NullLedgerReader()
        self.lifecycle_emitter: LifecycleEventEmitterLike = emitter
        self.drained_flag: asyncio.Event = asyncio.Event()
        self.tracer_provider: object = NoOpTracerProvider()
        self.validator_framework: object | None = None
        self.pause_resume_protocol: object | None = None
        self.pause_requested_flag: asyncio.Event = asyncio.Event()
        self.tenant_id: str | None = None
        self.skill_activation_emitter: object | None = None
        self.skills: object = None
        self.cp_is_wiring: object | None = None
        self.procedural_tier_snapshot_resolver: object | None = None
        self.inter_step_output_channel: object | None = None


class Echo:
    """A real `StepDispatcher` for the orchestrator's own DECLARATIVE_STEP."""

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> dict[str, object]:
        del binding, step_context
        return dict(step.step_payload)


def peer_manifest(workflow_id: str = "wf-parent") -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,  # PROCEED
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def ow_manifest(workflow_id: str = "wf-parent") -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,  # PROCEED
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.ORCHESTRATOR_WORKERS,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _manifest(family: str) -> WorkflowManifestEntry:
    return peer_manifest() if family == "PARALLELIZATION" else ow_manifest()


def _sub_agent_step(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={"child_workflow_id": "wf-child"},
    )


def _steps(family: str, n_workers: int) -> list[WorkflowStep]:
    workers = [_sub_agent_step(f"w-{i}") for i in range(n_workers)]
    if _FAMILY_SHAPE[family] == "peer":
        return workers
    orch = WorkflowStep(
        step_id=StepID("orch"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
    )
    return [orch, *workers]


def _child_pause_snapshot() -> PauseSnapshot:
    """A hash-valid child `PauseSnapshot` for `SubAgentChildPausedError.capture`, built through
    the real `PauseResumeProtocol.capture_pause_snapshot` seam."""

    def _reader() -> tuple[StateSummary, str]:
        return (
            StateSummary(
                relevant_entries=(),
                summary_text="",
                summary_hash="0" * 64,
                idempotency_key=Identifier(""),
                external_references=(),
            ),
            "0" * 64,
        )

    protocol = PauseResumeProtocol(
        state_ledger_writer=object(), state_ledger_reader=object(), pause_context_reader=_reader
    )
    return asyncio.run(
        protocol.capture_pause_snapshot(
            workflow_id="wf-child",
            run_id="child-run",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            descent_depth=0,
        )
    ).snapshot


class SubAgents:
    """A real `StepDispatcher`. Per worker: `refuse` (`ChildResumeRefusedError`), `fail`
    (ordinary `RuntimeError` — a branch failure, distinct from a refusal), `pause`
    (`SubAgentChildPausedError`), or `ok` (completes). A worker named in `block_until` waits on a
    shared `threading.Event` before acting, bounded to 3s (not the driver's own barrier
    deadline — this is a worst-case cleanup bound for the test's OWN thread, released once `_run`
    returns; see the module docstring's note on `_run_fanout_to_completion`'s abandon-on-deadline
    behavior). `received` is a plain list, so dispatch order/count is never hidden by
    set-deduplication at the assertion site."""

    def __init__(
        self,
        *,
        refuse: frozenset[str] = frozenset(),
        fail: frozenset[str] = frozenset(),
        pause: frozenset[str] = frozenset(),
        block_until: frozenset[str] = frozenset(),
    ) -> None:
        self._refuse = refuse
        self._fail = fail
        self._pause = pause
        self._block_until = block_until
        self._release = threading.Event()
        self.received: list[str] = []

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> dict[str, object]:
        del binding, step_context
        sid = str(step.step_id)
        self.received.append(sid)
        if sid in self._block_until:
            self._release.wait(timeout=3.0)
            raise RuntimeError("blocked worker released without an assigned outcome")
        if sid in self._refuse:
            raise ChildResumeRefusedError(ChildResumeRefusal.GATEWAY_NOT_INSTALLED, sid)
        if sid in self._fail:
            raise RuntimeError(f"ordinary failure: {sid}")
        if sid in self._pause:
            raise SubAgentChildPausedError(
                capture=PausedChildCapture(
                    child_workflow_id="wf-child",
                    child_snapshot=_child_pause_snapshot(),
                    child_record_ref=None,
                )
            )
        return {"completed": sid}

    def release_blocked(self) -> None:
        self._release.set()


class Registry:
    """A real `StepDispatcherRegistry`."""

    def __init__(self, sub_agents: SubAgents, echo: Echo) -> None:
        self._sub_agents = sub_agents
        self._echo = echo

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.SUB_AGENT_DISPATCH:
            return self._sub_agents
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._echo
        raise StepKindDispatcherNotBoundError(step_kind)


def _run(
    family: str, n_workers: int, sub_agents: SubAgents
) -> tuple[RunResult, RecordingLedger, Emitter]:
    ledger = RecordingLedger()
    emitter = Emitter()
    ctx: DriverContext = Ctx(ledger=ledger, emitter=emitter)
    registry: StepDispatcherRegistry = Registry(sub_agents, Echo())
    result = execute_workflow(
        _manifest(family),
        _steps(family, n_workers),
        run_id="run-parent",
        ctx=ctx,
        default_model_binding=_BINDING,
        step_dispatchers=registry,
    )
    return result, ledger, emitter


def _expected_salvaged_state(family: str, outputs: dict[str, dict[str, str]]) -> dict[str, object]:
    if family == "PARALLELIZATION":
        return {"branch_outputs": outputs, "aggregate": next(iter(outputs.values()))}
    assert family == "ORCHESTRATOR_WORKERS"
    return {"orchestrator": {}, "worker_outputs": outputs}


# --- 1. the completed arm (the `else` clause): success, `results` genuinely consumed ---------


@pytest.mark.parametrize("family", _FAMILIES)
def test_all_workers_succeed_is_success(family: str) -> None:
    """Every worker completes; no deadline, no refusal, no paused child. Asserts the EXACT
    merged family-specific `final_state` (both worker outputs preserved, keyed by step_id;
    PARALLELIZATION also has its voting aggregate), not just that it
    is non-`None` — a mutant that dropped a completed branch's output before the fold would pass
    a weaker assertion but fails this one."""
    sub_agents = SubAgents()
    result, ledger, _emitter = _run(family, 2, sub_agents)

    assert result.status is RunStatus.SUCCESS
    assert sorted(sub_agents.received) == ["w-0", "w-1"]
    assert result.final_state == _expected_salvaged_state(
        family, {"w-0": {"completed": "w-0"}, "w-1": {"completed": "w-1"}}
    )
    assert result.partial_state is None
    assert ledger.terminals() == {0: "completed", 1: "completed"}


@pytest.mark.parametrize("family", _FAMILIES)
def test_an_ordinary_branch_failure_with_no_refusal_or_deadline_is_partial(family: str) -> None:
    """One worker fails ordinarily (not a refusal); no deadline, no paused child. The failed
    branch contributes nothing to the aggregate (it never returned an output) — the survivor's
    output is salvaged whole into `partial_state`, asserted exactly, not merely `is not None`.

    The PARTIAL status assertion detects disabled failure classification. The exact
    `partial_state` assertion separately detects a completed-output-loss defect even when
    failure classification and the PARTIAL status remain correct."""
    sub_agents = SubAgents(fail=frozenset({"w-1"}))
    result, ledger, _emitter = _run(family, 2, sub_agents)

    assert result.status is RunStatus.PARTIAL
    assert sorted(sub_agents.received) == ["w-0", "w-1"]
    assert result.final_state is None
    assert result.partial_state == _expected_salvaged_state(family, {"w-0": {"completed": "w-0"}})
    # The failed branch still persists a `completed` terminal (obligation-3/4 dispatch-boundary
    # — it WAS dispatched, its step ran and errored, no silent gap).
    assert ledger.terminals() == {0: "completed", 1: "completed"}


# --- 2. refusal precedence over BOTH the deadline arm and the completed arm ------------------


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_refusal_with_no_deadline_is_failed_not_partial_or_success(family: str) -> None:
    """A refusal recorded, no deadline struck: `_refused_result()` fires from the `else` clause
    before `paused_child_dispositions` or `results` are ever consulted, with `salvage=False` (no
    survivor carried — a refusal is never salvaged, unlike an ordinary failure or a paused
    child). The refused worker is a FRESH dispatch here (no captured resume), so its terminal is
    `cancelled` (arm 6 — no disposition recorded for it at all), NOT the Path P resumed-and-
    refused `completed` the N1 prerequisite pins cover; confirmed by an actual run that this
    file's earlier `completed` expectation was wrong here."""
    sub_agents = SubAgents(refuse=frozenset({"w-0"}))
    result, ledger, _emitter = _run(family, 2, sub_agents)

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "child-resume-refused" in result.fail_class
    assert "gateway-not-installed" in result.fail_class
    assert result.partial_state is None
    assert sorted(sub_agents.received) == ["w-0", "w-1"]
    assert ledger.terminals() == {0: "cancelled", 1: "completed"}


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_refusal_racing_a_struck_deadline_is_failed_not_partial(
    family: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """w-0 refuses immediately (a synchronous dict raise, no I/O, no further `await`); w-1
    blocks past a shrunk barrier deadline. The deadline strikes (raised inside
    `_run_fanout_to_completion`, caught by `except`), but the ALREADY-recorded refusal must
    still win: `_refused_result()` is called from the `except` clause BEFORE the unconditional
    PARTIAL return — the exact interleaving the except-clause's own comments name.

    This remains TIME-BOUNDED, not proven deterministic (see the module docstring): this file
    cannot observe the moment `child_resume_refused_dispositions` is actually written without
    owning `workflow_driver.py`. The 1.5s deadline is a large margin over w-0's near-instant
    raise, not a synchronization guarantee.

    Mutation discriminator: removing the `_refused_result()` call from the `except` clause (or
    reordering the PARTIAL return before it) makes this test observe PARTIAL instead of FAILED."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 1.5)
    sub_agents = SubAgents(refuse=frozenset({"w-0"}), block_until=frozenset({"w-1"}))
    try:
        result, ledger, _emitter = _run(family, 2, sub_agents)
    finally:
        sub_agents.release_blocked()  # cleanup backstop; harmless if already unblocked

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "child-resume-refused" in result.fail_class
    assert "gateway-not-installed" in result.fail_class
    assert sorted(sub_agents.received) == ["w-0", "w-1"]
    assert ledger.terminals().get(0) == "cancelled"  # w-0's fresh refusal


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_struck_deadline_with_no_refusal_is_partial(
    family: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """w-0 completes; w-1 blocks past a shrunk barrier deadline, and no refusal was ever
    recorded. The `except` clause's `_refused_result()` call returns `None`, so control falls
    through to the unconditional `_finish(RunStatus.PARTIAL, ...)` — the deadline-alone control
    for the previous test, isolating "refusal present" as the only variable that changes the
    outcome. A mutant that ignores `child_resume_refused_dispositions` entirely inside the
    `except` clause makes BOTH this and the previous test observe PARTIAL, collapsing the
    precedence distinction this pair exists to prove."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 1.5)
    sub_agents = SubAgents(block_until=frozenset({"w-1"}))
    try:
        result, _ledger, _emitter = _run(family, 2, sub_agents)
    finally:
        sub_agents.release_blocked()

    assert result.status is RunStatus.PARTIAL
    assert result.fail_class is None


# --- 3. the paused-child arm (the `else` clause's second check), alone and in combination -----


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_paused_child_with_no_deadline_or_refusal_is_failed_not_resumable(family: str) -> None:
    """w-0's recursive child PAUSES (no refusal, no deadline): the `else` clause's
    `paused_child_dispositions` check fires. FAILED with the family's
    `-child-paused-not-resumable-under-proceed` fail_class, `salvage=True` — the survivor's
    output is salvaged into `partial_state`, asserted exactly (the paused worker contributes
    NOTHING to the aggregate: it never returned an output). The paused worker's own zero-
    footprint stash IS a "did dispatch" disposition (arm 4), so it gets `completed`, unlike a
    fresh refusal — this is the one disposition kind this file's ledger assertions do NOT need
    correcting for (only the refusal cases needed the `cancelled` fix)."""
    sub_agents = SubAgents(pause=frozenset({"w-0"}))
    result, ledger, _emitter = _run(family, 2, sub_agents)

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "child-paused-not-resumable-under-proceed" in result.fail_class
    assert result.final_state is None
    assert result.partial_state == _expected_salvaged_state(family, {"w-1": {"completed": "w-1"}})
    assert sorted(sub_agents.received) == ["w-0", "w-1"]
    assert ledger.terminals() == {0: "completed", 1: "completed"}


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_refusal_beats_a_paused_child_with_no_deadline(family: str) -> None:
    """w-0 refuses, w-1's child pauses; neither races a deadline. `_refused_result()` is checked
    BEFORE `paused_child_dispositions` inside the `else` clause, so refusal wins: FAILED with the
    refusal fail_class (never the paused-not-resumable one), `salvage=False` (no survivor
    carried — refusal, unlike a lone paused child, salvages nothing).

    Mutation discriminator: swapping the `else`-clause check order (paused-child before
    `_refused_result()`) makes this test observe the paused fail_class, `salvage=True`, and a
    non-`None` `partial_state` instead."""
    sub_agents = SubAgents(refuse=frozenset({"w-0"}), pause=frozenset({"w-1"}))
    result, ledger, _emitter = _run(family, 2, sub_agents)

    assert result.status is RunStatus.FAILED
    assert result.fail_class is not None
    assert "child-resume-refused" in result.fail_class
    assert "child-paused-not-resumable" not in result.fail_class
    assert result.partial_state is None
    assert sorted(sub_agents.received) == ["w-0", "w-1"]
    # w-0: fresh refusal -> cancelled (no disposition); w-1: paused, THIS round -> completed.
    assert ledger.terminals() == {0: "cancelled", 1: "completed"}


@pytest.mark.parametrize("family", _FAMILIES)
def test_a_struck_deadline_beats_a_stashed_paused_child(
    family: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """w-0's child pauses (stashed, no refusal); w-1 blocks past a shrunk deadline. This is the
    "paused-child stash-then-deadline race" the `except` clause's own comments name: the
    deadline strikes BEFORE the paused-child check (which lives only in the `else` clause) is
    ever reached, so the run degrades to PARTIAL — never the paused-not-resumable FAILED — and
    the stashed pause's own disposition is STILL recorded as a `completed` terminal (arm 4 fires
    regardless of which return path follows). w-1's own in-flight-abandoned disposition is not
    asserted here — its exact timing versus the deadline exit was not observed running."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 1.5)
    sub_agents = SubAgents(pause=frozenset({"w-0"}), block_until=frozenset({"w-1"}))
    try:
        result, ledger, _emitter = _run(family, 2, sub_agents)
    finally:
        sub_agents.release_blocked()

    assert result.status is RunStatus.PARTIAL
    assert result.fail_class is None
    assert ledger.terminals().get(0) == "completed"  # the stashed paused-child

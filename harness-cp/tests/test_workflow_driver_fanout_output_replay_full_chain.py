"""B-FANOUT-OUTPUT-REPLAY — full-chain crash→resume witness (by-execution).

R-FS-1 standalone arc (operator ratified A — non-attested branch-index-keyed sidecar).
Drives the REAL `execute_workflow` through a two-phase crash→resume cycle to witness
BOTH halves of the recovery mechanism THROUGH the real driver path (NOT the
`_determine_fanout_resume` isolation tests in the sibling file):

  - PRODUCER (net-add #1): a completed branch's output is captured to the store inside
    `_record_clean` during real fan-out execution (+ the ORCHESTRATOR_WORKERS `steps[0]`
    output via `record_orchestrator`);
  - CONSUMER (net-add #3): on a fresh re-entry with a populated store + a fresh empty
    ledger (the crash model — the durable store survives, the §25.12 D1.b BINARY ledger
    is lost), `_execute_workflow_body` reconstructs the synthetic resume state and the
    strategy REPLAYS the completed branches (the dispatch counter shows they fire ONCE
    across crash+resume) + re-dispatches only the incomplete ones; the aggregate is
    identical to the no-crash trajectory.

These FAIL if the producer is reverted — the store stays empty → every branch
re-dispatches → the fire-once / no-re-dispatch assertions trip
(`[[full-chain-witness-not-half-proofs]]`: an e2e that passes unchanged with the
producer reverted is bypassing it). The real on-disk store round-trip (record →
read-back across a fresh store instance = crash+restart) is separately witnessed at
`harness-runtime/tests/test_engine_output_store.py`; this file witnesses the DRIVER
integration with a faithful in-memory store that mirrors the EngineOutputStore fan-out
branch API exactly.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, cast

from harness_core import PersonaTier, StepID, WorkloadClass
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-fanout-replay")
# SOLO_DEVELOPER → cascade_policy=proceed (a branch failure harvests survivors → PARTIAL),
# so a Run-1 "crash" leaves the completed siblings captured in the durable store.
_PROCEED_TIER = PersonaTier.SOLO_DEVELOPER


# ---------------------------------------------------------------------------
# Faithful in-memory mirror of the EngineOutputStore fan-out branch API.
# Survives across the two execute_workflow phases (the durable store outliving
# the crash). The driver duck-types it via getattr (the cp_is_wiring idiom).
# ---------------------------------------------------------------------------
class _InMemoryBranchStore:
    def __init__(self) -> None:
        self._branches: dict[str, dict[int, tuple[str, dict[str, Any]]]] = {}
        self._orchestrators: dict[str, tuple[str, dict[str, Any]]] = {}
        # branch indexes marked present-but-unreadable (corruption / tamper) per run_key.
        self._corrupt: dict[str, set[int]] = {}

    # -- producer (net-add #1) -------------------------------------------------
    def record_branch(
        self, run_key: str, branch_index: int, step_id: str, output: dict[str, Any]
    ) -> None:
        self._branches.setdefault(run_key, {})[branch_index] = (str(step_id), dict(output))

    def record_orchestrator(self, run_key: str, step_id: str, output: dict[str, Any]) -> None:
        self._orchestrators[run_key] = (str(step_id), dict(output))

    # -- consumer (net-add #2/#3) ---------------------------------------------
    def read_branch_outputs(self, run_key: str) -> dict[int, tuple[str, dict[str, Any]]]:
        return dict(self._branches.get(run_key, {}))

    def present_branch_indexes(self, run_key: str) -> set[int]:
        return set(self._branches.get(run_key, {})) | self._corrupt.get(run_key, set())

    def read_orchestrator_output(self, run_key: str) -> tuple[str, dict[str, Any]] | None:
        return self._orchestrators.get(run_key)

    def orchestrator_present(self, run_key: str) -> bool:
        return run_key in self._orchestrators

    # -- test helper: mark a branch present-but-unreadable ---------------------
    def mark_corrupt(self, run_key: str, branch_index: int) -> None:
        self._corrupt.setdefault(run_key, set()).add(branch_index)

    # -- test helper: the single run_key recorded this run (the driver computes
    # `sha256(run_id, workflow_id, entry_version)` internally; inspecting by the
    # sole recorded key avoids re-deriving it and coupling the test to §25.6). --
    def sole_run_key(self) -> str:
        keys = set(self._branches) | set(self._orchestrators)
        assert len(keys) == 1, f"expected exactly one recorded run_key, got {keys}"
        return next(iter(keys))


def _manifest(
    *,
    workflow_id: str,
    topology: TopologyPattern,
    engine_class: EngineClass = EngineClass.EVENT_SOURCED_REPLAY,
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PROCEED_TIER,
        engine_class=engine_class,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step(name: str, index: int) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"index": index},
    )


class _RecordingLedger:
    actor: Actor

    def __init__(self) -> None:
        self.actor = _ACTOR
        self.appends: list[tuple[Any, Any]] = []

    def append(self, payload: Any, write_key: Any) -> Any:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return len(self.appends) == 0

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _Emitter:
    def __init__(self) -> None:
        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: WorkflowEventClass) -> None:
        self.emits.append(event_class)


class _Ctx:
    """Minimal duck-typed DriverContext with an `engine_output_store` bound (the
    fan-out crash-resume substrate). Mirrors the PARALLELIZATION e2e `_Ctx`."""

    def __init__(self, *, ledger: Any, store: Any) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_resume_protocol = None
        self.pause_requested_flag = asyncio.Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.engine_output_store = store


class _CountingDispatcher:
    """Echoes `{"branch": index}` per branch and RECORDS every step_id it dispatches
    (the fire-once witness). `fail_index` raises for one branch AFTER its siblings
    complete (sibling-event sync, no time.sleep) so the survivors are captured before
    the failure propagates — the deterministic mid-fan-out partial-completion crash."""

    def __init__(self, *, n: int, fail_index: int | None = None) -> None:
        self.dispatched: list[str] = []
        self._fail_index = fail_index
        self._sibling_events = (
            {i: threading.Event() for i in range(n) if i != fail_index}
            if fail_index is not None
            else {}
        )

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.dispatched.append(str(step.step_id))
        idx = int(step.step_payload["index"])
        if self._fail_index is not None and idx == self._fail_index:
            for sibling, event in self._sibling_events.items():
                assert event.wait(timeout=10.0), f"sibling {sibling} never completed"
            raise RuntimeError(f"simulated branch crash at index {idx}")
        if idx in self._sibling_events:
            self._sibling_events[idx].set()
        return {"branch": idx}


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is not StepKind.DECLARATIVE_STEP:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _run(
    *,
    workflow_id: str,
    topology: TopologyPattern,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    store: Any,
    engine_class: EngineClass = EngineClass.EVENT_SOURCED_REPLAY,
) -> Any:
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), store=store))
    return execute_workflow(
        _manifest(workflow_id=workflow_id, topology=topology, engine_class=engine_class),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(dispatcher)),
    )


# ---------------------------------------------------------------------------
# PARALLELIZATION — partial crash → resume: completed branches replay (fire once),
# only the incomplete branch re-dispatches; the aggregate matches a no-crash run.
# ---------------------------------------------------------------------------
def test_parallelization_crash_resume_replays_completed_redispatches_incomplete() -> None:
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # Run 1 (the crash): branch 1 crashes after 0 + 2 complete → 0, 2 captured to the
    # durable store; PARTIAL (cascade_policy=proceed). The ledger from this phase is
    # discarded (the crash loses the binary ledger).
    crash = _CountingDispatcher(n=3, fail_index=1)
    r1 = _run(
        workflow_id="wf-par-crash",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=crash,
        store=store,
    )
    assert r1.status is RunStatus.PARTIAL
    assert store.read_branch_outputs(store.sole_run_key()).keys() == {0, 2}

    # Run 2 (resume): a FRESH ctx + FRESH (empty) ledger sharing the SAME durable store.
    # 0 + 2 are recovered (NOT re-dispatched); only branch 1 re-dispatches.
    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-par-crash",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    # Fire-once: across crash+resume the completed branches dispatched exactly once
    # (in Run 1). On resume ONLY the incomplete branch re-fires.
    assert resume.dispatched == ["branch-1"]
    # The aggregate is identical to a clean no-crash run of the same workflow.
    baseline = _run(
        workflow_id="wf-par-baseline",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=_InMemoryBranchStore(),
    )
    assert r2.final_state is not None and baseline.final_state is not None
    assert r2.final_state["branch_outputs"] == baseline.final_state["branch_outputs"]
    assert r2.final_state["aggregate"] == baseline.final_state["aggregate"]


# ---------------------------------------------------------------------------
# ORCHESTRATOR_WORKERS — full crash → resume: the orchestrator (steps[0]) AND every
# worker recover from the store; NOTHING re-dispatches on resume. Witnesses the
# orchestrator-output capture/recovery (the wire-both-or-FAIL-closed trap).
# ---------------------------------------------------------------------------
def test_orchestrator_crash_resume_recovers_orchestrator_and_workers() -> None:
    store = _InMemoryBranchStore()
    # steps[0] = orchestrator, steps[1:] = workers.
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]

    run1 = _CountingDispatcher(n=2)  # workers indexed 0,1 over steps[1:]
    r1 = _run(
        workflow_id="wf-ow-crash",
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
        dispatcher=run1,
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    # The orchestrator output was captured (else _determine_fanout_resume fails closed).
    assert store.orchestrator_present(store.sole_run_key()) is True

    # Run 2 (resume): same store, fresh ledger. Orchestrator + both workers recovered →
    # the resume dispatcher fires for NOTHING.
    resume = _CountingDispatcher(n=2)
    r2 = _run(
        workflow_id="wf-ow-crash",
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []  # fire-once: everything recovered, no re-dispatch


# ---------------------------------------------------------------------------
# HIERARCHICAL_DELEGATION — top-level crash → resume threads through the per-level
# `_execute_orchestrator_workers` (the crash_fan_out_resume forward). Recursive child
# levels crash-resume against their OWN run-keyed store (each child re-enters
# execute_workflow with its own key); this witnesses the TOP level. (The cross-bootstrap
# mid-recursion re-dispatch reproducibility is the existing paused_child_branches
# territory, NOT this arc — a crash has no paused children, paused_child_branches=().)
# ---------------------------------------------------------------------------
def test_hierarchical_top_level_crash_resume_recovers_orchestrator_and_workers() -> None:
    store = _InMemoryBranchStore()
    steps = [_step("parent", 0), _step("child-0", 0), _step("child-1", 1)]  # ≤3 (cap 3)

    r1 = _run(
        workflow_id="wf-hd-crash",
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert store.orchestrator_present(store.sole_run_key()) is True

    resume = _CountingDispatcher(n=2)
    r2 = _run(
        workflow_id="wf-hd-crash",
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []  # fire-once: parent + children recovered, none re-fire


# ---------------------------------------------------------------------------
# Negative control — NO store bound → crash-resume is INERT → every branch
# re-dispatches → byte-identical to a clean run (the default path is untouched).
# ---------------------------------------------------------------------------
def test_no_store_restarts_fresh_byte_identical() -> None:
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    disp = _CountingDispatcher(n=3)
    r = _run(
        workflow_id="wf-no-store",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=disp,
        store=None,
    )
    assert r.status is RunStatus.SUCCESS
    assert sorted(disp.dispatched) == ["branch-0", "branch-1", "branch-2"]


# ---------------------------------------------------------------------------
# Fail-closed — a present-but-unreadable branch (corruption / tamper) on resume →
# FAILED RunResult (never a silent re-dispatch that would re-fire a landed effect).
# ---------------------------------------------------------------------------
def test_crash_resume_fails_closed_on_corrupt_store() -> None:
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # Run 1: branch 1 crashes → 0, 2 captured.
    _run(
        workflow_id="wf-par-corrupt",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
    )
    # Corrupt branch 1's journal (present but unreadable) BEFORE resume.
    store.mark_corrupt(store.sole_run_key(), 1)

    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-par-corrupt",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "fan-out-crash-resume-store-corrupt" in r2.fail_class
    assert resume.dispatched == []  # fail-closed: nothing re-dispatched on corruption


# ---------------------------------------------------------------------------
# Synthesis-bearing crash-resume — FAIL-CLOSED (PR1). A POST_JOIN_SYNTHESIS fan-out
# that crash-resumes sails PAST the §3/§4 pause-resume reject (resume_snapshot is None),
# recovers its branches, and would otherwise dispatch the synthesis FRESH (a
# non-reproducible W3-window output). It must stay fail-closed until the synthesis
# self-hash + captured-output replay lands (the registered follow-on slice). This keeps
# the half-capability from silently shipping (advisor: don't let "works fresh" win).
# ---------------------------------------------------------------------------
class _SynthesisDispatcher:
    def __init__(self) -> None:
        self.dispatched = 0

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.dispatched += 1
        return {"synthesis": "composed"}


class _BranchOrSynthesisRegistry:
    def __init__(self, branch: StepDispatcher, synthesis: StepDispatcher) -> None:
        self._branch = branch
        self._synthesis = synthesis

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._branch
        if step_kind is StepKind.POST_JOIN_SYNTHESIS:
            return self._synthesis
        raise StepKindDispatcherNotBoundError(step_kind)


def _synthesis_step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("synthesis"),
        step_kind=StepKind.POST_JOIN_SYNTHESIS,
        step_payload={"prompt": "compose the siblings"},
    )


def _run_synth(
    *, workflow_id: str, branch: StepDispatcher, synthesis: StepDispatcher, store: Any
) -> Any:
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), store=store))
    steps = [_step("branch-0", 0), _step("branch-1", 1), _synthesis_step()]
    return execute_workflow(
        _manifest(workflow_id=workflow_id, topology=TopologyPattern.PARALLELIZATION),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(
            StepDispatcherRegistry, _BranchOrSynthesisRegistry(branch, synthesis)
        ),
    )


def test_synthesis_bearing_crash_resume_fails_closed() -> None:
    store = _InMemoryBranchStore()

    # Run 1: a clean synthesis-bearing fan-out — 2 branches + the terminal synthesis all
    # dispatch (the branches captured to the store; synthesis dispatched fresh, SUCCESS).
    r1 = _run_synth(
        workflow_id="wf-synth-crash",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert store.read_branch_outputs(store.sole_run_key()).keys() == {0, 1}

    # Run 2 (crash-resume): the store has the completed branches, so net-add #3 builds a
    # crash resume state — and because a synthesis step is present, the run FAILS CLOSED
    # (the synthesis would otherwise re-dispatch fresh, non-reproducibly). The synthesis
    # dispatcher must fire ZERO times on resume.
    resume_branch = _CountingDispatcher(n=2)
    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-crash",
        branch=resume_branch,
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-on-resume-unsupported" in r2.fail_class
    assert resume_synth.dispatched == 0  # never re-dispatched the synthesis
    assert resume_branch.dispatched == []  # fail-closed before the strategy ran

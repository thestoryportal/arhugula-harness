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
        self._branches: dict[str, dict[int, tuple[str, str, dict[str, Any] | None]]] = {}
        self._orchestrators: dict[str, tuple[str, dict[str, Any]]] = {}
        # branch indexes marked present-but-unreadable (corruption / tamper) per run_key.
        self._corrupt: dict[str, set[int]] = {}
        self._cardinality: dict[str, int] = {}
        # PR2 — captured terminal POST_JOIN_SYNTHESIS records: {run_key: (step_id, output, self_hash)}.
        self._synthesis: dict[str, tuple[str, dict[str, Any], str]] = {}
        # run_keys whose synthesis file is present-but-unreadable (a corrupt capture).
        self._synthesis_corrupt: set[str] = set()

    def record_fanout_cardinality(self, run_key: str, branch_count: int) -> None:
        self._cardinality[run_key] = int(branch_count)

    def read_fanout_cardinality(self, run_key: str) -> int | None:
        return self._cardinality.get(run_key)

    # -- producer (net-add #1) -------------------------------------------------
    def record_branch(
        self,
        run_key: str,
        branch_index: int,
        step_id: str,
        terminal_status: str,
        output: dict[str, Any] | None,
    ) -> None:
        self._branches.setdefault(run_key, {})[branch_index] = (
            str(step_id),
            str(terminal_status),
            dict(output) if output is not None else None,
        )

    def record_orchestrator(self, run_key: str, step_id: str, output: dict[str, Any]) -> None:
        self._orchestrators[run_key] = (str(step_id), dict(output))

    # -- PR2 synthesis capture / replay ---------------------------------------
    def record_synthesis(
        self, run_key: str, step_id: str, output: dict[str, Any], self_hash: str
    ) -> None:
        self._synthesis[run_key] = (str(step_id), dict(output), str(self_hash))

    def read_synthesis(self, run_key: str) -> tuple[str, dict[str, Any], str] | None:
        if run_key in self._synthesis_corrupt:
            return None  # present-but-unreadable
        return self._synthesis.get(run_key)

    def synthesis_present(self, run_key: str) -> bool:
        return run_key in self._synthesis or run_key in self._synthesis_corrupt

    # -- test helper: tamper a captured synthesis output (self-hash will mismatch) --
    def tamper_synthesis(self, run_key: str, output: dict[str, Any]) -> None:
        step_id, _old, self_hash = self._synthesis[run_key]
        self._synthesis[run_key] = (step_id, dict(output), self_hash)

    # -- test helper: mark the synthesis file present-but-unreadable (corrupt capture) --
    def mark_synthesis_corrupt(self, run_key: str) -> None:
        self._synthesis.pop(run_key, None)
        self._synthesis_corrupt.add(run_key)

    # -- test helper: simulate a crash BEFORE the synthesis ran (branches captured, synthesis not) --
    def forget_synthesis(self, run_key: str) -> None:
        self._synthesis.pop(run_key, None)
        self._synthesis_corrupt.discard(run_key)

    # -- consumer (net-add #2/#3) ---------------------------------------------
    def read_branch_records(
        self, run_key: str
    ) -> dict[int, tuple[str, str, dict[str, Any] | None]]:
        return dict(self._branches.get(run_key, {}))

    def present_branch_indexes(self, run_key: str) -> set[int]:
        return set(self._branches.get(run_key, {})) | self._corrupt.get(run_key, set())

    def read_orchestrator_output(self, run_key: str) -> tuple[str, dict[str, Any]] | None:
        return self._orchestrators.get(run_key)

    def orchestrator_present(self, run_key: str) -> bool:
        return run_key in self._orchestrators

    # -- test helper: mark a branch present-but-unreadable (drop the readable record) --
    def mark_corrupt(self, run_key: str, branch_index: int) -> None:
        self._branches.get(run_key, {}).pop(branch_index, None)
        self._corrupt.setdefault(run_key, set()).add(branch_index)

    # -- test helper: simulate a branch IN-FLIGHT at the crash (absent from the store) --
    def forget_branch(self, run_key: str, branch_index: int) -> None:
        self._branches.get(run_key, {}).pop(branch_index, None)

    # -- test helper: the single run_key recorded this run (the driver computes
    # `sha256(run_id, workflow_id, entry_version)` internally; inspecting by the
    # sole recorded key avoids re-deriving it and coupling the test to §25.6). --
    def sole_run_key(self) -> str:
        keys = set(self._branches) | set(self._orchestrators) | set(self._synthesis)
        assert len(keys) == 1, f"expected exactly one recorded run_key, got {keys}"
        return next(iter(keys))


def _manifest(
    *,
    workflow_id: str,
    topology: TopologyPattern,
    engine_class: EngineClass = EngineClass.EVENT_SOURCED_REPLAY,
    persona_tier: PersonaTier = _PROCEED_TIER,
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
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
# PARALLELIZATION — crash → resume: completed branches replay (fire once); a branch
# IN-FLIGHT at the crash (absent from the store) re-dispatches; aggregate matches no-crash.
# ---------------------------------------------------------------------------
def test_parallelization_crash_resume_replays_completed_redispatches_absent() -> None:
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # Run 1: all 3 branches complete + captured. Then `forget` branch 1 — modelling a
    # branch that was still IN-FLIGHT when the host crashed (no terminal record landed),
    # leaving 0 + 2 durable and 1 absent (the only re-dispatchable disposition).
    _run(
        workflow_id="wf-par-crash",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
    )
    store.forget_branch(store.sole_run_key(), 1)
    assert store.read_branch_records(store.sole_run_key()).keys() == {0, 2}

    # Run 2 (resume): a FRESH ctx + FRESH (empty) ledger sharing the SAME durable store.
    # 0 + 2 are recovered (NOT re-dispatched); only the absent branch 1 re-dispatches.
    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-par-crash",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    # Fire-once: the completed branches dispatched exactly once (in Run 1). On resume ONLY
    # the absent (in-flight-at-crash) branch re-fires.
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
# PARALLELIZATION — a ran-and-errored branch (effect LANDED, no output) is recovered as
# TERMINAL on crash-resume: NOT re-dispatched (at-most-once), NOT folded (honest PARTIAL).
# ---------------------------------------------------------------------------
def test_parallelization_crash_resume_errored_branch_recovered_as_terminal() -> None:
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # Run 1: branch 1 ran-and-errored (effect may have landed) → captured `completed`/None;
    # 0 + 2 clean. The disposition store records ALL three terminal dispositions.
    _run(
        workflow_id="wf-par-errored",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
    )
    records = store.read_branch_records(store.sole_run_key())
    assert records.keys() == {0, 1, 2}
    assert records[1] == ("branch-1", "completed", None)  # errored: terminal, no output

    # Run 2 (resume): branch 1 is recovered AS TERMINAL — never re-dispatched (its effect
    # may have landed) and never folded (no output). The run stays DEGRADED → PARTIAL (the
    # resume must NOT upgrade the original failure to SUCCESS by omitting it — Codex [P2]).
    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-par-errored",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert resume.dispatched == []  # at-most-once: the errored branch is NOT re-fired
    assert r2.status is RunStatus.PARTIAL  # degraded: the recovered failure is preserved
    assert r2.partial_state is not None
    assert set(r2.partial_state["branch_outputs"]) == {"branch-0", "branch-2"}


def _completed_branch_indexes(ledger: _RecordingLedger) -> set[int]:
    """The branch_index of every `completed` terminal entry in the drained ledger."""
    out: set[int] = set()
    for payload, _wk in ledger.appends:
        bm = getattr(payload, "branch_metadata", None)
        if bm is not None and getattr(bm, "terminal_status", None) == "completed":
            out.add(bm.branch_index)
    return out


def test_parallelization_crash_resume_rematerializes_recovered_branch_ledger_entries() -> None:
    """The finding-1 assertion (out-of-family Codex [P1]) the aggregate/fire-once witnesses
    MISSED: a crash lost the recovered branches' buffered ledger entries (the binary ledger
    drained nothing), so the resumed run's ledger must RE-MATERIALIZE them — else the audit
    trail omits branch outputs that ARE in the aggregate (a fail-open audit gap). The resumed
    ledger carries a terminal entry for EVERY branch (recovered + re-dispatched), and
    `workflow.step_count` counts all of them."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # Run 1: all 3 complete + captured; `forget` branch 1 (in-flight at the crash, absent →
    # the only re-dispatchable disposition) so resume re-dispatches 1 + replays 0, 2.
    _run(
        workflow_id="wf-par-ledger",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
    )
    store.forget_branch(store.sole_run_key(), 1)

    # Run 2 (resume) with an explicit ledger to inspect.
    ledger = _RecordingLedger()
    ctx = cast(DriverContext, _Ctx(ledger=ledger, store=store))
    r2 = execute_workflow(
        _manifest(workflow_id="wf-par-ledger", topology=TopologyPattern.PARALLELIZATION),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(_CountingDispatcher(n=3))),
    )
    assert r2.status is RunStatus.SUCCESS
    # The resumed ledger has a `completed` terminal entry for EVERY branch — the recovered
    # 0, 2 RE-MATERIALIZED + the re-dispatched 1 (NOT just the re-dispatched one).
    assert _completed_branch_indexes(ledger) == {0, 1, 2}
    # Compare to a clean no-crash run: the resumed ledger's branch terminal set is identical.
    baseline_ledger = _RecordingLedger()
    baseline_ctx = cast(DriverContext, _Ctx(ledger=baseline_ledger, store=_InMemoryBranchStore()))
    execute_workflow(
        _manifest(workflow_id="wf-par-ledger-baseline", topology=TopologyPattern.PARALLELIZATION),
        steps,
        run_id="run-1",
        ctx=baseline_ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(_CountingDispatcher(n=3))),
    )
    assert _completed_branch_indexes(ledger) == _completed_branch_indexes(baseline_ledger)


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


def test_orchestrator_crash_resume_rematerializes_worker_ledger_entries() -> None:
    """Finding-1 (Codex [P1]) for ORCHESTRATOR_WORKERS: a crash lost the recovered workers'
    buffered ledger entries; the resumed ledger must RE-MATERIALIZE them (else the audit
    omits worker outputs that ARE in the aggregate). Full-recovery crash → every worker
    terminal entry is present in the resumed ledger though NONE re-dispatched."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]

    # Run 1: orchestrator + both workers complete + captured.
    _run(
        workflow_id="wf-ow-ledger",
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
    )

    # Run 2 (resume) with an explicit ledger to inspect.
    ledger = _RecordingLedger()
    ctx = cast(DriverContext, _Ctx(ledger=ledger, store=store))
    resume = _CountingDispatcher(n=2)
    r2 = execute_workflow(
        _manifest(workflow_id="wf-ow-ledger", topology=TopologyPattern.ORCHESTRATOR_WORKERS),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(resume)),
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []  # fire-once: nothing re-dispatched
    # Both worker branches (0, 1) have a `completed` terminal entry in the resumed ledger —
    # RE-MATERIALIZED, though neither re-dispatched.
    assert _completed_branch_indexes(ledger) == {0, 1}


def test_orchestrator_zero_workers_crash_resume_recovers_orchestrator_only() -> None:
    """A crash after the orchestrator captured but with EVERY worker still in-flight /
    absent (Codex [P1]): on resume the orchestrator is RECOVERED (NOT re-dispatched — no
    double-fire), and every worker re-dispatches fresh. Exercises the empty-`branches=()`
    resume state, a NEW shape pause never produced (advisor)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]

    # Run 1: orchestrator + both workers complete + captured. Then `forget` both workers —
    # modelling a crash where the orchestrator landed + was recorded but the workers were
    # still in-flight (no terminal record), leaving the store orchestrator-only.
    _run(
        workflow_id="wf-ow-orch-only",
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
    )
    store.forget_branch(store.sole_run_key(), 0)
    store.forget_branch(store.sole_run_key(), 1)
    assert store.orchestrator_present(store.sole_run_key()) is True
    assert store.read_branch_records(store.sole_run_key()) == {}  # zero workers captured

    # Run 2 (resume): the orchestrator is recovered (NOT re-dispatched); both workers
    # re-dispatch fresh (none were captured).
    resume = _CountingDispatcher(n=2)
    r2 = _run(
        workflow_id="wf-ow-orch-only",
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    # The orchestrator (`orch`) is NOT in the resume dispatch set — recovered, not re-fired.
    assert "orch" not in resume.dispatched
    assert sorted(resume.dispatched) == ["w-0", "w-1"]  # only the workers re-dispatch


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
# Synthesis-bearing crash-resume — PR2 REPLAY (CP spec v1.56 §1/§2). The PR1 fail-closed
# is now RELAXED: a POST_JOIN_SYNTHESIS fan-out that crash-resumes under PROCEED recovers
# its branches then, at the post-barrier synthesis, REPLAYS a captured output (the W3
# window — verified by the record-local self-hash + step_id material-diff, reproducible) or
# re-dispatches FRESH on the reproduced branches (a crash BEFORE the synthesis ran;
# effect-free, consistent over the same siblings). Three fail-closed gates protect the
# replay: present-but-unreadable, self-hash mismatch, and a changed synthesis body.
# ---------------------------------------------------------------------------
class _SynthesisDispatcher:
    def __init__(self, *, output: dict[str, Any] | None = None) -> None:
        self.dispatched = 0
        self._output = {"synthesis": "composed"} if output is None else output

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.dispatched += 1
        return dict(self._output)


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
    *,
    workflow_id: str,
    branch: StepDispatcher,
    synthesis: StepDispatcher,
    store: Any,
    topology: TopologyPattern = TopologyPattern.PARALLELIZATION,
    steps: list[WorkflowStep] | None = None,
) -> Any:
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), store=store))
    if steps is None:
        steps = [_step("branch-0", 0), _step("branch-1", 1), _synthesis_step()]
    return execute_workflow(
        _manifest(workflow_id=workflow_id, topology=topology),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(
            StepDispatcherRegistry, _BranchOrSynthesisRegistry(branch, synthesis)
        ),
    )


def test_synthesis_crash_resume_replays_captured_output() -> None:
    """Window (a) — the W3 crash window (crash AFTER the synthesis was captured). The branches
    recover from the store AND the captured synthesis output is REPLAYED (not re-dispatched):
    the resume synthesis dispatcher fires ZERO times and the aggregate is byte-identical to the
    no-crash trajectory. No provider needed — fully deterministic (advisor)."""
    store = _InMemoryBranchStore()

    # Run 1: a clean synthesis-bearing fan-out — branches + synthesis captured; SUCCESS.
    r1 = _run_synth(
        workflow_id="wf-synth-replay",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(output={"synthesis": "composed-original"}),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert r1.final_state == {"synthesis": "composed-original"}
    assert store.synthesis_present(store.sole_run_key())

    # Run 2 (crash-resume): branches recover; the captured synthesis REPLAYS. The resume
    # dispatcher would return a DIFFERENT output if (wrongly) called — so the aggregate
    # matching Run 1 proves replay, not re-dispatch.
    resume_synth = _SynthesisDispatcher(output={"synthesis": "WRONG-fresh-redispatch"})
    r2 = _run_synth(
        workflow_id="wf-synth-replay",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume_synth.dispatched == 0  # REPLAYED from the store, never re-dispatched
    assert r2.final_state == r1.final_state == {"synthesis": "composed-original"}


def test_synthesis_crash_resume_before_synthesis_redispatches_fresh() -> None:
    """Window (b) — a crash BEFORE the synthesis ran (branches captured, synthesis not). On
    resume the branches recover and the synthesis dispatches FRESH on the reproduced siblings
    (effect-free, first-and-only). Not byte-reproducible by construction — but consistent."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-pre",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    # Simulate the crash landing BEFORE the synthesis-capture point: drop the synthesis record.
    store.forget_synthesis(store.sole_run_key())
    assert not store.synthesis_present(store.sole_run_key())

    resume_synth = _SynthesisDispatcher(output={"synthesis": "fresh-on-reproduced"})
    r2 = _run_synth(
        workflow_id="wf-synth-pre",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume_synth.dispatched == 1  # re-dispatched fresh (no capture to replay)
    assert r2.final_state == {"synthesis": "fresh-on-reproduced"}


def test_synthesis_crash_resume_self_hash_mismatch_fails_closed() -> None:
    """Window (c) — a captured synthesis whose record is TAMPERED (the output no longer matches
    its record-local self-hash). Replay fails closed rather than serving a tampered aggregate;
    the synthesis is NEVER re-dispatched (no silent fresh fallback that would mask the tamper)."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-tamper",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    store.tamper_synthesis(store.sole_run_key(), {"synthesis": "TAMPERED"})

    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-tamper",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-self-hash-mismatch" in r2.fail_class
    assert resume_synth.dispatched == 0


def test_synthesis_crash_resume_corrupt_capture_fails_closed() -> None:
    """Window (c) — a captured synthesis file present-but-UNREADABLE (a corrupt capture).
    `synthesis_present` is True but `read_synthesis` yields None → fail closed, never a silent
    fresh re-dispatch."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-corrupt",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    store.mark_synthesis_corrupt(store.sole_run_key())

    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-corrupt",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-corrupt" in r2.fail_class
    assert resume_synth.dispatched == 0


def test_synthesis_crash_resume_branch_corrupt_fails_closed_not_masked() -> None:
    """Advisor window (c) — a captured synthesis (so all branches DID complete) but a branch
    is now present-but-unreadable on resume. PR1's branch-corruption guard fires BEFORE the
    synthesis: the run fails closed (`fan-out-crash-resume-store-corrupt`), the synthesis replay
    does NOT mask the branch corruption, and the synthesis is never reached."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-branch-corrupt",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert store.synthesis_present(store.sole_run_key())
    store.mark_corrupt(store.sole_run_key(), 1)  # branch 1 now present-but-unreadable

    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-branch-corrupt",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "fan-out-crash-resume-store-corrupt" in r2.fail_class
    assert resume_synth.dispatched == 0  # synthesis never reached — branch guard fired first


def test_synthesis_crash_resume_replays_with_orchestrator_recovery() -> None:
    """Window (a) for ORCHESTRATOR_WORKERS: the orchestrator output AND the workers recover
    from the store, and the captured synthesis REPLAYS on top — proving the synthesis rides the
    orchestrator-topology recovery. HIERARCHICAL_DELEGATION reuses `_execute_orchestrator_workers`
    at each level, so this also covers the per-level synthesis recovery (CP spec v1.56 §2)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1), _synthesis_step()]

    r1 = _run_synth(
        workflow_id="wf-ow-synth-replay",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(output={"synthesis": "ow-original"}),
        store=store,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
    )
    assert r1.status is RunStatus.SUCCESS
    assert r1.final_state == {"synthesis": "ow-original"}
    assert store.orchestrator_present(store.sole_run_key())
    assert store.synthesis_present(store.sole_run_key())

    resume_synth = _SynthesisDispatcher(output={"synthesis": "WRONG-fresh-redispatch"})
    r2 = _run_synth(
        workflow_id="wf-ow-synth-replay",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        steps=steps,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume_synth.dispatched == 0  # orchestrator + workers + synthesis all recovered
    assert r2.final_state == r1.final_state == {"synthesis": "ow-original"}


def test_crash_resume_empty_manifest_fails_closed_material_diff() -> None:
    """A changed body (out-of-family Codex [P2]): the store holds recovered branches but the
    RESUMED manifest carries NO branch steps. The strategy's empty-step fast path would
    return SUCCESS with an empty aggregate BEFORE the resume material-diff guard — silently
    dropping the recovered outputs. Reject fail-closed instead."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # Run 1: all 3 branches complete + captured.
    r1 = _run(
        workflow_id="wf-par-empty",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS

    # Run 2 (resume) with an EMPTY manifest sharing the SAME store → FAILED (material-diff),
    # NOT a silent empty-aggregate SUCCESS.
    resume = _CountingDispatcher(n=0)
    r2 = _run(
        workflow_id="wf-par-empty",
        topology=TopologyPattern.PARALLELIZATION,
        steps=[],
        dispatcher=resume,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    # An empty resumed manifest is BOTH a cardinality change (3 → 0) and an empty-branch
    # material-diff; either fail-closed reason is correct (the cardinality check fires first).
    assert (
        "cardinality mismatch" in r2.fail_class
        or "fan-out-crash-resume-material-diff" in r2.fail_class
    )
    assert resume.dispatched == []


# ---------------------------------------------------------------------------
# Cascade-policy scope (PR1, advisor): crash-resume recovery is correct ONLY for
# CascadePolicy.PROCEED. PAUSE + CASCADE_CANCEL carry committed on-failure semantics a
# cascade-policy-BLIND recovery cannot honor → FAIL CLOSED. Cascade-policy-aware crash-resume
# is the registered back-flow follow-on (.harness/class_1_fork_fanout_crash_resume_cascade_policy.md).
# ---------------------------------------------------------------------------
def _run_persona(
    *,
    workflow_id: str,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    store: Any,
    persona_tier: PersonaTier,
) -> Any:
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), store=store))
    return execute_workflow(
        _manifest(
            workflow_id=workflow_id,
            topology=TopologyPattern.PARALLELIZATION,
            persona_tier=persona_tier,
        ),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(dispatcher)),
    )


def test_crash_resume_cascade_cancel_fails_closed() -> None:
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    # Run 1 (MULTI_TENANT_COMPLIANCE = cascade-cancel): all complete + captured.
    _run_persona(
        workflow_id="wf-cc",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    # Run 2 (resume): the crash-resume gate sees CASCADE_CANCEL → FAILED (never recovers /
    # re-dispatches — a cascade-policy-blind recovery would corrupt the cancel semantic).
    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None and "cascade-policy-unsupported" in r2.fail_class
    assert resume.dispatched == []  # fail-closed before any recovery / re-dispatch

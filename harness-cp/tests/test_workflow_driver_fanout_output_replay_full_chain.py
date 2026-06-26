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
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import PauseSnapshot
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
from harness_cp.workflow_manifest_entry import (
    FanoutTimeoutDisposition,
    WorkflowManifestEntry,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

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
        # B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE / MAYBE-RAN-RESOLUTION — reserve-before-
        # dispatch markers: {run_key: {branch_index that BEGAN dispatch: dispatch-time step_kind
        # value | None}} + the per-run dispatch-instrumented stamp. The kind is recorded at
        # dispatch so the maybe-ran classifier keys on the ORIGINAL kind (changed-manifest guard);
        # None models a pre-arc v1.60/v1.61 marker (step_id only, no kind) → fail-closed.
        self._dispatched: dict[str, dict[int, str | None]] = {}
        self._instrumented: set[str] = set()
        # B-FANOUT-CRASH-RESUME-ORCHESTRATOR-DISPATCH / MAYBE-RAN-RESOLUTION — {run_key:
        # orchestrator dispatch-time step_kind value | None} for runs whose orchestrator BEGAN
        # dispatch (the orchestrator reserve-before-dispatch marker; a single marker per run).
        # Presence = key membership; the kind keys the maybe-ran re-fire-safety classifier
        # (None models a pre-v1.81 v1.79-era marker — step_id only, no kind → fail-closed).
        self._orchestrator_dispatched: dict[str, str | None] = {}

    def record_fanout_cardinality(self, run_key: str, branch_count: int) -> None:
        self._cardinality[run_key] = int(branch_count)

    def read_fanout_cardinality(self, run_key: str) -> int | None:
        return self._cardinality.get(run_key)

    def fanout_cardinality_present(self, run_key: str) -> bool:
        return run_key in self._cardinality

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

    # -- B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE / MAYBE-RAN-RESOLUTION: reserve-before-
    # dispatch ----
    def record_branch_dispatched(
        self, run_key: str, branch_index: int, step_id: str, step_kind: str
    ) -> None:
        self._dispatched.setdefault(run_key, {})[int(branch_index)] = str(step_kind)

    def present_dispatched_indexes(self, run_key: str) -> set[int]:
        return set(self._dispatched.get(run_key, {}))

    def dispatched_branch_kinds(self, run_key: str) -> dict[int, str | None]:
        return dict(self._dispatched.get(run_key, {}))

    # -- test helper: a v1.60/v1.61 pre-arc marker (step_id only, no recorded kind) → the
    # maybe-ran classifier cannot prove the original kind → fail-closed. --
    def forget_branch_dispatch_kind(self, run_key: str, branch_index: int) -> None:
        if branch_index in self._dispatched.get(run_key, {}):
            self._dispatched[run_key][branch_index] = None

    # -- test helper: a stale / corrupt OUT-OF-RANGE dispatch marker (a leftover
    # branch-N.dispatched from a larger prior fan-out) with a re-fire-safe recorded kind → the
    # store no longer matches the declared fan-out → fail-closed (not silently ignored). --
    def inject_stale_dispatch_marker(self, run_key: str, branch_index: int, kind: str) -> None:
        self._dispatched.setdefault(run_key, {})[int(branch_index)] = str(kind)

    def record_dispatch_instrumented(self, run_key: str) -> None:
        self._instrumented.add(run_key)

    def dispatch_instrumented(self, run_key: str) -> bool:
        return run_key in self._instrumented

    # -- B-FANOUT-CRASH-RESUME-ORCHESTRATOR-DISPATCH: orchestrator reserve-before-dispatch --
    def record_orchestrator_dispatched(self, run_key: str, step_id: str, step_kind: str) -> None:
        self._orchestrator_dispatched[run_key] = str(step_kind)

    def orchestrator_dispatched(self, run_key: str) -> bool:
        return run_key in self._orchestrator_dispatched

    def orchestrator_dispatched_kind(self, run_key: str) -> str | None:
        return self._orchestrator_dispatched.get(run_key)

    # -- test helper: a pre-v1.81 (v1.79-era) orchestrator marker (step_id only, no recorded
    # kind) → the maybe-ran classifier cannot prove re-fire-safety → fail-closed (the v1.79
    # behavior). Mirrors `forget_branch_dispatch_kind` for the orchestrator. --
    def forget_orchestrator_dispatch_kind(self, run_key: str) -> None:
        if run_key in self._orchestrator_dispatched:
            self._orchestrator_dispatched[run_key] = None

    # -- test helper: a branch that was NOT-YET-DISPATCHED at the crash (no marker, no
    # output) — provably-not-run, the case the strict tiers can now re-dispatch safely. --
    def forget_branch_undispatched(self, run_key: str, branch_index: int) -> None:
        self._branches.get(run_key, {}).pop(branch_index, None)
        self._dispatched.get(run_key, {}).pop(branch_index, None)

    # -- test helper: a crash in the ORCHESTRATOR fire→capture window. The orchestrator
    # dispatched (marker + instrumented stamp present, both written BEFORE the dispatch) but
    # its output was never captured. The orchestrator runs FIRST, so no worker dispatched yet
    # → the only durable trace is the orchestrator marker + stamp; drop everything else (the
    # orchestrator output, cardinality, all worker records + markers). Maybe-ran → fail closed. --
    def forget_orchestrator_maybe_ran(self, run_key: str) -> None:
        self._orchestrators.pop(run_key, None)
        self._cardinality.pop(run_key, None)
        self._branches.pop(run_key, None)
        self._dispatched.pop(run_key, None)
        # KEEP self._orchestrator_dispatched + self._instrumented (the reserve-before-dispatch
        # marker + the cross-version stamp — both fsynced strictly before the dispatch).

    # -- test helper: a crash BEFORE the orchestrator dispatched — no marker, no output, no
    # cardinality, no worker (provably-not-run → a fresh re-run is at-most-once-safe). --
    def forget_orchestrator_undispatched(self, run_key: str) -> None:
        self._orchestrators.pop(run_key, None)
        self._cardinality.pop(run_key, None)
        self._branches.pop(run_key, None)
        self._dispatched.pop(run_key, None)
        self._orchestrator_dispatched.pop(run_key, None)

    # -- test helper: a PRE-arc (un-instrumented) journal — cardinality + branch records but
    # NO dispatch stamp and NO markers (the cross-version hazard). Forces the conservative
    # fail-closed: "no marker" cannot be read as "not-run" on an un-stamped journal. --
    def simulate_pre_arc_journal(self, run_key: str) -> None:
        self._instrumented.discard(run_key)
        self._dispatched.pop(run_key, None)
        self._orchestrator_dispatched.pop(run_key, None)

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

    # -- test helper: degrade a branch to `completed`-NO-OUTPUT (ran-and-errored, effect landed) --
    def degrade_branch(self, run_key: str, branch_index: int) -> None:
        step_id, _status, _out = self._branches[run_key][branch_index]
        self._branches[run_key][branch_index] = (step_id, "completed", None)

    # -- test helper: a deadline-cut (`timed_out`) branch — the §25.15 barrier cut-off
    # captured the disposition with NO output (effect may or may not have landed). The
    # B-FANOUT-CRASH-RESUME-TIMEOUT-REPLAY disposition policy resolves it on resume. --
    def timeout_branch(self, run_key: str, branch_index: int) -> None:
        step_id, _status, _out = self._branches[run_key][branch_index]
        self._branches[run_key][branch_index] = (step_id, "timed_out", None)

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
    timeout_disposition: FanoutTimeoutDisposition = FanoutTimeoutDisposition.FAIL_CLOSED,
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
        fanout_timeout_disposition=timeout_disposition,
    )


def _step(name: str, index: int, kind: StepKind = StepKind.DECLARATIVE_STEP) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=kind,
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


_PAUSE_ANCHOR = "0" * 64  # constant MVP pause-context anchor (no material diff on resume)


def _pause_context_reader() -> tuple[StateSummary, str]:
    """MVP constant-sentinel reader (mirrors the parallelization-pause harness): empty
    StateSummary + a constant anchor → resume detects no material diff → admits."""
    return (
        StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        _PAUSE_ANCHOR,
    )


def _pause_protocol() -> PauseResumeProtocol:
    """A real PauseResumeProtocol so the COMPLETE-recovery PAUSE crash-resume can CAPTURE
    a reconstructed snapshot + return PAUSED (B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT)."""
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


class _Ctx:
    """Minimal duck-typed DriverContext with an `engine_output_store` bound (the
    fan-out crash-resume substrate). Mirrors the PARALLELIZATION e2e `_Ctx`.

    `pause_resume_protocol` defaults None (the fail-closed / continue paths need no
    protocol); bind one (B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT) so a COMPLETE-recovery
    degraded PAUSE crash-resume can re-establish the lost PAUSED state."""

    def __init__(self, *, ledger: Any, store: Any, pause_resume_protocol: Any = None) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_resume_protocol = pause_resume_protocol
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


class _LookupRaisesRegistry:
    """A registry whose `lookup` ALWAYS raises — simulates an unknown-`step_kind` dispatcher
    lookup failure BEFORE any effect can fire (the orchestrator marker must NOT be written)."""

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        raise StepKindDispatcherNotBoundError(step_kind)


class _AnyKindRegistry:
    """A registry serving the SAME dispatcher for ANY step kind — for the
    B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION multi-kind fan-out tests (re-fire-SAFE
    DECLARATIVE_STEP / INFERENCE_STEP + fence-recoverable TOOL_STEP / MANAGED_AGENTS
    branches recover; the still-unfenced SUB_AGENT_DISPATCH branches fail closed)."""

    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return self._dispatcher


def _run(
    *,
    workflow_id: str,
    topology: TopologyPattern,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    store: Any,
    engine_class: EngineClass = EngineClass.EVENT_SOURCED_REPLAY,
    timeout_disposition: FanoutTimeoutDisposition = FanoutTimeoutDisposition.FAIL_CLOSED,
    persona_tier: PersonaTier = _PROCEED_TIER,
) -> Any:
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), store=store))
    return execute_workflow(
        _manifest(
            workflow_id=workflow_id,
            topology=topology,
            engine_class=engine_class,
            timeout_disposition=timeout_disposition,
            persona_tier=persona_tier,
        ),
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


# ---------------------------------------------------------------------------
# B-FANOUT-CRASH-RESUME-TIMEOUT-REPLAY (R-FS-1, CP spec v1.63 §1) — by-execution witnesses
# through the REAL execute_workflow crash→resume cycle, for each disposition policy.
# ---------------------------------------------------------------------------
def test_timeout_disposition_fail_closed_default_fails_the_resume() -> None:
    """The DEFAULT `FAIL_CLOSED` (the v1.55 §1 behavior): a deadline-cut (`timed_out`)
    branch fails the crash-resume CLOSED — even under the PROCEED tier — never recovering
    or re-dispatching. This is the contrast baseline for RECOVER_AS_TERMINAL / RE_DISPATCH."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run(
        workflow_id="wf-timeout-fc",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
    )
    store.timeout_branch(store.sole_run_key(), 1)  # branch 1 deadline-cut on the crashed run

    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-timeout-fc",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
        timeout_disposition=FanoutTimeoutDisposition.FAIL_CLOSED,
    )
    assert r2.status is RunStatus.FAILED  # v1.55 §1 byte-identical
    assert resume.dispatched == []  # never re-dispatched


def test_timeout_disposition_recover_as_terminal_recovers_partial() -> None:
    """RECOVER_AS_TERMINAL under PROCEED: the deadline-cut branch is recovered as a degraded
    non-contributor (never re-dispatched, never folded) → the run RECOVERS as PARTIAL folding
    the survivors, instead of FAILING closed. Contrast with the FAIL_CLOSED baseline above —
    same store state, different disposition → FAILED vs PARTIAL."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run(
        workflow_id="wf-timeout-rat",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
    )
    store.timeout_branch(store.sole_run_key(), 1)

    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-timeout-rat",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    assert resume.dispatched == []  # at-most-once: the deadline-cut branch is NOT re-fired
    assert r2.status is RunStatus.PARTIAL  # recovered (degraded) instead of FAILED
    assert r2.partial_state is not None
    assert set(r2.partial_state["branch_outputs"]) == {"branch-0", "branch-2"}


def test_timeout_disposition_re_dispatch_re_fire_safe_branch_re_runs() -> None:
    """RE_DISPATCH + a re-fire-safe (DECLARATIVE_STEP, the default `_step` kind) deadline-cut
    branch → re-run fresh (the dispatch marker recorded the re-fire-safe kind). On resume the
    timed-out branch re-fires exactly once + the survivors replay → SUCCESS, aggregate matches
    a clean run. A re-fire-safe re-run has no external effect to double-fire.

    Run under a STRICT tier (MULTI_TENANT_COMPLIANCE → cascade-cancel): the dispatch-time-kind
    markers RE_DISPATCH's re-fire-safety gate keys on are written only on the strict tiers (the
    v1.62 marker substrate is strict-tier-only — under PROCEED, with no markers to prove
    re-fire-safety, RE_DISPATCH conservatively fails closed; PROCEED-tier timeout recovery uses
    RECOVER_AS_TERMINAL)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run(
        workflow_id="wf-timeout-rd",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    store.timeout_branch(store.sole_run_key(), 1)

    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-timeout-rd",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
        timeout_disposition=FanoutTimeoutDisposition.RE_DISPATCH,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.SUCCESS  # re-fire-safe re-run completes the fan-out
    assert resume.dispatched == [
        "branch-1"
    ]  # ONLY the timed-out branch re-fires (survivors replay)
    baseline = _run(
        workflow_id="wf-timeout-rd-baseline",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=_InMemoryBranchStore(),
    )
    assert r2.final_state is not None and baseline.final_state is not None
    assert r2.final_state["aggregate"] == baseline.final_state["aggregate"]


def test_timeout_disposition_re_dispatch_effect_bearing_branch_fails_closed() -> None:
    """RE_DISPATCH + an EFFECT-BEARING deadline-cut branch → FAIL CLOSED through the real run
    path: the dispatch marker records an effect-bearing kind, so re-dispatch is refused (its
    effect may have landed). At-most-once is the GATE, not operator-overridable.

    The classifier keys on the dispatch-time-kind MARKER (the changed-manifest at-most-once
    guard, §3) — so branch 1's marker is overridden to TOOL_STEP after a clean DECLARATIVE
    Run 1 (modelling a branch that DISPATCHED as an effect-bearing kind; effect-bearing fan-out
    branch capture itself is the separately-registered effect-bearing-maybe-ran arc's substrate,
    out of scope here). Strict tier → markers present → the fail-closed is for the EFFECT-BEARING
    reason, not absent markers."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run(
        workflow_id="wf-timeout-rd-eb",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    run_key = store.sole_run_key()
    # branch 1 dispatched as an effect-bearing TOOL_STEP (override the recorded marker kind)
    # then deadline-cut → timed_out.
    store.inject_stale_dispatch_marker(run_key, 1, StepKind.TOOL_STEP.value)
    store.timeout_branch(run_key, 1)

    resume = _CountingDispatcher(n=3)
    r2 = _run(
        workflow_id="wf-timeout-rd-eb",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=resume,
        store=store,
        timeout_disposition=FanoutTimeoutDisposition.RE_DISPATCH,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.FAILED  # effect-bearing deadline-cut cannot be re-dispatched
    assert resume.dispatched == []


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
    ledger: Any = None,
) -> Any:
    ctx = cast(DriverContext, _Ctx(ledger=ledger or _RecordingLedger(), store=store))
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
    """Window (b) — the synthesis sidecar absent (branches captured, synthesis not). On resume
    the branches recover and the synthesis dispatches FRESH on the reproduced siblings. This one
    state covers BOTH pre-capture sub-windows — "synthesis never ran" AND "synthesis ran but the
    capture was lost before fsync" (Codex round-4): the store cannot distinguish them, and both
    safely re-dispatch because the synthesis is ENFORCED effect-free + the lost aggregate was
    never committed (the ledger-append is after the capture). Not byte-reproducible by
    construction — but consistent and effect-safe (see the capture-site comment in the driver)."""
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


def test_synthesis_crash_resume_incomplete_branches_fails_closed() -> None:
    """Out-of-family Codex [P2] — a captured synthesis PROVES every branch completed. If on
    resume a branch journal is ABSENT (a partial-cleanup / sidecar inconsistency),
    `_determine_fanout_resume` would re-dispatch it (re-firing a landed effect) while the
    replay returns the STALE captured aggregate over the just-changed sibling. Fail closed
    BEFORE any re-dispatch: a captured synthesis admits only a pure zero-re-dispatch replay."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-incomplete",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert store.synthesis_present(store.sole_run_key())
    # Drop branch 1's journal — present synthesis but an absent branch (an inconsistent store).
    store.forget_branch(store.sole_run_key(), 1)

    resume_branch = _CountingDispatcher(n=2)
    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-incomplete",
        branch=resume_branch,
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-incomplete-branches" in r2.fail_class
    assert resume_branch.dispatched == []  # fail-closed BEFORE the absent branch re-dispatched
    assert resume_synth.dispatched == 0  # the stale synthesis was NOT replayed


def test_synthesis_crash_resume_all_branches_absent_fails_closed() -> None:
    """Out-of-family Codex [P2] round-2 (a) — if ALL branch journals are absent but the
    synthesis sidecar survived, `_determine_fanout_resume` returns None (no crash-resume state),
    so the run would otherwise proceed as FRESH and then replay the stale synthesis over the
    freshly re-dispatched branches. The synthesis-completeness guard fires INDEPENDENT of
    `_crash_fan_out_resume` → fail closed, no re-dispatch."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-all-absent",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    key = store.sole_run_key()
    assert store.synthesis_present(key)
    store.forget_branch(key, 0)
    store.forget_branch(key, 1)  # ALL branches absent; synthesis still present

    resume_branch = _CountingDispatcher(n=2)
    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-all-absent",
        branch=resume_branch,
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-incomplete-branches" in r2.fail_class
    assert resume_branch.dispatched == []  # never proceeded as a fresh run
    assert resume_synth.dispatched == 0


def test_synthesis_crash_resume_degraded_branch_fails_closed() -> None:
    """Out-of-family Codex [P2] round-2 (b) — a recovered branch `completed` with NO output (a
    ran-and-errored degraded branch) keeps the branch COUNT but is non-output-bearing. A
    captured synthesis proves a SUCCESSFUL (all-output-bearing) fan-out, so a degraded branch on
    resume is inconsistent → fail closed (the count-only check would have let it through)."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-degraded",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    key = store.sole_run_key()
    store.degrade_branch(key, 1)  # branch 1: completed, output=None (count still 2)

    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-degraded",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-incomplete-branches" in r2.fail_class
    assert resume_synth.dispatched == 0


def test_synthesis_crash_resume_body_drops_synthesis_fails_closed() -> None:
    """Out-of-family Codex [P2] round-3 — a captured synthesis but the resumed manifest DROPPED
    the terminal POST_JOIN_SYNTHESIS step. Without a guard the run returns the deterministic
    FOLD, silently DISCARDING the captured synthesized aggregate. Material-diff → fail closed
    (the symmetric of the step_id material-diff for a CHANGED synthesis body)."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-dropped",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert store.synthesis_present(store.sole_run_key())

    # Run 2 (resume) with the SAME branches but the synthesis step REMOVED from the manifest.
    r2 = _run_synth(
        workflow_id="wf-synth-dropped",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
        steps=[_step("branch-0", 0), _step("branch-1", 1)],  # no _synthesis_step()
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-material-diff" in r2.fail_class


class _SynthesisAppendRaiser(_RecordingLedger):
    """A ledger that raises on the SYNTHESIS terminal entry append (the post-join-synthesis
    write_key) — to witness that a replay-path ledger failure maps to a FAILED RunResult
    rather than escaping execute_workflow."""

    def append(self, payload: Any, write_key: Any) -> Any:
        if "post-join-synthesis" in str(getattr(write_key, "step_id", "")):
            raise RuntimeError("simulated synthesis ledger-append failure")
        return super().append(payload, write_key)


def test_synthesis_replay_ledger_append_failure_maps_to_failed() -> None:
    """Out-of-family Codex [P2] — on the captured-synthesis replay path, a failing
    `_append_synthesis_ledger_entry` (or STEP_BOUNDARY emit) must map to a FAILED RunResult
    (like the fresh-dispatch path), NOT escape execute_workflow as a raw exception."""
    store = _InMemoryBranchStore()

    r1 = _run_synth(
        workflow_id="wf-synth-append-fail",
        branch=_CountingDispatcher(n=2),
        synthesis=_SynthesisDispatcher(),
        store=store,
    )
    assert r1.status is RunStatus.SUCCESS
    assert store.synthesis_present(store.sole_run_key())

    # Run 2 (replay): the synthesis is replayed, but the ledger re-append raises → FAILED,
    # not an escaping exception.
    resume_synth = _SynthesisDispatcher()
    r2 = _run_synth(
        workflow_id="wf-synth-append-fail",
        branch=_CountingDispatcher(n=2),
        synthesis=resume_synth,
        store=store,
        ledger=_SynthesisAppendRaiser(),
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "post-join-synthesis-replay-failure" in r2.fail_class
    assert resume_synth.dispatched == 0  # replayed (not re-dispatched), then the append failed


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
# Cascade-policy-AWARE crash-resume (B-FANOUT-CRASH-RESUME-CASCADE-POLICY), the STRICT-TIER-
# conservative version (Codex [P1] + advisor reconcile). For the strict tiers (PAUSE / TEAM,
# CASCADE_CANCEL / MULTI_TENANT_COMPLIANCE) a crash-resume CONTINUES only when the recovery is
# COMPLETE (every branch recovered → nothing to re-dispatch) AND no branch errored — every other
# state fails closed: an errored branch → the policy's failure semantics (CASCADE_CANCEL →
# reproduce FAILED; PAUSE → fail-closed-ambiguous → the B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT
# sub-arc); an INCOMPLETE recovery → fail closed (an absent branch is indistinguishable from one
# that ran its effect but crashed before its capture — re-dispatching an effect-BEARING branch
# is unsafe for these tiers; broad incomplete recovery is the B-FANOUT-CRASH-RESUME-STRICT-TIER-
# INCOMPLETE follow-on, needing at-most-once branch dispatch). PROCEED is UNCHANGED (PR1).
# ---------------------------------------------------------------------------
def _run_persona(
    *,
    workflow_id: str,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    store: Any,
    persona_tier: PersonaTier,
    topology: TopologyPattern = TopologyPattern.PARALLELIZATION,
    registry: Any = None,
    pause_resume_protocol: Any = None,
    pause_snapshot_input: PauseSnapshot | None = None,
    timeout_disposition: FanoutTimeoutDisposition = FanoutTimeoutDisposition.FAIL_CLOSED,
) -> Any:
    ctx = cast(
        DriverContext,
        _Ctx(ledger=_RecordingLedger(), store=store, pause_resume_protocol=pause_resume_protocol),
    )
    return execute_workflow(
        _manifest(
            workflow_id=workflow_id,
            topology=topology,
            persona_tier=persona_tier,
            timeout_disposition=timeout_disposition,
        ),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(
            StepDispatcherRegistry, registry if registry is not None else _Registry(dispatcher)
        ),
        pause_snapshot_input=pause_snapshot_input,
    )


def test_crash_resume_cascade_cancel_complete_recovery_completes() -> None:
    """The ONE strict-tier continue path — a COMPLETE recovery (every branch recovered, none
    errored). The crash landed after all branches finished but before the run finalized; on
    resume there is NOTHING to re-dispatch, so the run finalizes from the recovered set →
    SUCCESS (advisor: run it, don't infer it — re-dispatch count must be zero)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-complete",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    # All 3 captured; no forget → a COMPLETE recovery.
    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-complete",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []  # complete recovery → re-dispatches NOTHING


def test_crash_resume_cascade_cancel_incomplete_refire_safe_recovers() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION — an INCOMPLETE recovery where the absent
    branch is MAYBE-RAN of a RE-FIRE-SAFE kind. `forget_branch` drops the OUTPUT record but
    KEEPS the reserve-before-dispatch marker — a branch that BEGAN dispatch but crashed before
    its capture. `present_dispatched_indexes − recovered = {1}` ≠ ∅, but the branch is a
    DECLARATIVE_STEP (no non-idempotent external effect) → SAFE to re-dispatch fresh: the run
    RECOVERS, re-dispatching ONLY the maybe-ran branch (the captured siblings replay, fire
    zero times). The #732 arc failed this closed (conservative — "branches are effect-bearing");
    this arc lifts it for re-fire-safe kinds. The effect-bearing-kind maybe-ran case still fails
    closed — see `..._unsafe_kind_fails_closed`."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-incomplete",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # output gone, marker KEPT → branch 1 is MAYBE-RAN
    assert 1 in store.present_dispatched_indexes(key)  # the maybe-ran discriminator

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-incomplete",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.SUCCESS
    # ONLY the maybe-ran branch re-dispatches (re-fire-safe); the captured siblings replay.
    assert resume.dispatched == ["branch-1"]


def test_crash_resume_incomplete_fence_recoverable_tool_step_recovers() -> None:
    """B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE (R-FS-1) — an INCOMPLETE recovery where the absent
    branch is MAYBE-RAN of a FENCE-RECOVERABLE TOOL_STEP (marker kept, output gone) AND the
    resumed manifest's branch at that ordinal is STILL a TOOL_STEP. The #732/#736 arcs failed a
    maybe-ran TOOL_STEP closed (conservative "effect-bearing"); this arc RECOVERS it —
    re-dispatching re-reaches the AUTO-ACTIVE runtime effect fence, which makes the re-fire
    at-most-once AT THE TOOL SINK (suppress-if-captured / ambiguous-PAUSE / fresh-fire-if-claim-
    absent — proven through the REAL fence by the runtime test_effect_fence.py + the real-fence
    PARALLELIZATION witness). The run RECOVERS, re-dispatching ONLY the maybe-ran branch. Contrast
    the changed-kind (`..._changed_manifest_kind...`) + unfenced-kind (`..._unsafe_kind...`)
    siblings, which still fail closed."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.TOOL_STEP) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-fence-recoverable",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(
        key, 1
    )  # output gone, marker KEPT → maybe-ran TOOL_STEP (fence-recoverable)
    assert store.dispatched_branch_kinds(key)[1] == StepKind.TOOL_STEP.value

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-fence-recoverable",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.SUCCESS
    # ONLY the maybe-ran branch re-dispatches (into the fence); the captured siblings replay.
    assert resume.dispatched == ["branch-1"]


def test_crash_resume_cardinality_only_fence_recoverable_tool_step_recovers() -> None:
    """B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE (R-FS-1, cardinality-only path) — every branch is a
    MAYBE-RAN FENCE-RECOVERABLE TOOL_STEP (resumed manifest STILL TOOL_STEP). The cardinality
    marker is present but nothing is readably recovered; all branches began dispatch (markers
    kept). Re-dispatching re-reaches the auto-active fence → at-most-once at the tool sink → the
    run RECOVERS as a fresh re-dispatch. Witnesses the cardinality-only call site of the
    fence-recovery narrowing (distinct from the incomplete-recovery site above)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.TOOL_STEP) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-card-fence-recoverable",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    for i in range(3):
        store.forget_branch(key, i)  # all maybe-ran TOOL_STEP (fence-recoverable)
    assert store.read_branch_records(key) == {}
    assert store.present_dispatched_indexes(key) == {0, 1, 2}

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-card-fence-recoverable",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.SUCCESS
    assert sorted(resume.dispatched) == ["branch-0", "branch-1", "branch-2"]


def test_crash_resume_incomplete_fence_recoverable_managed_agents_recovers() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-UNFENCED-EXTERNAL (R-FS-1) — the MANAGED_AGENTS analogue of
    the TOOL_STEP recovery above. An INCOMPLETE recovery where the absent branch is a MAYBE-RAN
    MANAGED_AGENTS (marker kept, output gone) AND the resumed manifest's branch at that ordinal is
    STILL MANAGED_AGENTS. Before this arc the vendor-session dispatch was UNFENCED → fail closed;
    now it is fenced at its OWN §14.22 sink → the CP driver RE-DISPATCHES it into the fence (the
    at-most-once suppress / ambiguous-PAUSE / fresh-fire split is proven through the REAL fence by
    the runtime test_managed_agents_dispatch_effect_fence.py). The run RECOVERS, re-dispatching
    ONLY the maybe-ran branch; the captured siblings replay."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.MANAGED_AGENTS) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-managed-recoverable",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # output gone, marker KEPT → maybe-ran MANAGED_AGENTS (recoverable)
    assert store.dispatched_branch_kinds(key)[1] == StepKind.MANAGED_AGENTS.value

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-managed-recoverable",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.SUCCESS
    # ONLY the maybe-ran branch re-dispatches (into its vendor-session fence); siblings replay.
    assert resume.dispatched == ["branch-1"]


def test_crash_resume_managed_agents_cross_kind_swap_fails_closed() -> None:
    """The same-kind guard for MANAGED_AGENTS at the full-chain level — a maybe-ran branch
    dispatched as MANAGED_AGENTS, re-supplied on resume as TOOL_STEP (a CROSS-KIND swap between
    two fence-recoverable kinds). Both are recoverable, but re-dispatch would reach a DIFFERENT
    fence sink (a different idempotency-key namespace) → the original vendor effect's ambiguity
    silently abandoned + a fresh tool effect fired → fail closed (the same-kind-equality conjunct
    in `_fence_unrecoverable_maybe_ran_indices`)."""
    store = _InMemoryBranchStore()
    steps_v1 = [_step(f"branch-{i}", i, kind=StepKind.MANAGED_AGENTS) for i in range(3)]
    _run_persona(
        workflow_id="wf-managed-cross-kind",
        steps=steps_v1,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # maybe-ran MANAGED_AGENTS
    assert store.dispatched_branch_kinds(key)[1] == StepKind.MANAGED_AGENTS.value

    resume = _CountingDispatcher(n=3)
    steps_v2 = [
        _step("branch-0", 0, kind=StepKind.MANAGED_AGENTS),
        _step("branch-1", 1, kind=StepKind.TOOL_STEP),  # CROSS-KIND swap from MANAGED_AGENTS
        _step("branch-2", 2, kind=StepKind.MANAGED_AGENTS),
    ]
    r2 = _run_persona(
        workflow_id="wf-managed-cross-kind",
        steps=steps_v2,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # cross-kind swap → fail closed, no re-dispatch


def test_crash_resume_cardinality_only_changed_kind_tool_to_declarative_fails_closed() -> None:
    """B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE (R-FS-1) — the changed-kind guard at the CARDINALITY-ONLY
    site (the incomplete-recovery site is covered by `..._changed_manifest_kind_fails_closed`). All
    branches dispatched as TOOL_STEP, all maybe-ran (cardinality-only). On resume branch 1 is
    re-supplied as a DECLARATIVE_STEP (changed kind, same ordinal + step_id). The marker says
    TOOL_STEP but the RESUMED branch is DECLARATIVE → re-dispatch would reach NO tool fence → the
    original tool effect's ambiguity would be silently abandoned → fail closed (NOT fence-recoverable
    despite the marker; the resumed-kind conjunct closes the changed-manifest hole at this site)."""
    store = _InMemoryBranchStore()
    steps_v1 = [_step(f"branch-{i}", i, kind=StepKind.TOOL_STEP) for i in range(3)]
    _run_persona(
        workflow_id="wf-card-changed-kind",
        steps=steps_v1,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    for i in range(3):
        store.forget_branch(key, i)  # all maybe-ran TOOL_STEP (cardinality-only)
    assert store.dispatched_branch_kinds(key)[1] == StepKind.TOOL_STEP.value

    resume = _CountingDispatcher(n=3)
    steps_v2 = [
        _step("branch-0", 0, kind=StepKind.TOOL_STEP),
        _step("branch-1", 1, kind=StepKind.DECLARATIVE_STEP),  # CHANGED from TOOL_STEP
        _step("branch-2", 2, kind=StepKind.TOOL_STEP),
    ]
    r2 = _run_persona(
        workflow_id="wf-card-changed-kind",
        steps=steps_v2,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # changed-kind branch → fail closed, no re-dispatch


def test_crash_resume_cascade_cancel_incomplete_unsafe_kind_fails_closed() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION — the maybe-ran branch is an UNFENCED
    effect-bearing kind (SUB_AGENT_DISPATCH — fenced only at its CHILD's tool sinks, the recursive-child
    residual; NOT the now-fence-recoverable TOOL_STEP / MANAGED_AGENTS), so neither the
    re-fire-safe relaxation NOR the B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE fence-recovery applies: its
    vendor-session effect MAY have fired with NO fence to make a re-dispatch at-most-once → FAIL
    CLOSED (the unfenced-external resolution is the registered B-FANOUT-CRASH-RESUME-MAYBE-RAN-
    SUBAGENT follow-on). The contrasting positive controls are the DECLARATIVE re-fire-safe
    sibling above + the fence-recoverable TOOL_STEP / MANAGED_AGENTS siblings below — same shape,
    only the kind differs."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.SUB_AGENT_DISPATCH) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-unsafe-kind",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(
        key, 1
    )  # output gone, marker KEPT → branch 1 MAYBE-RAN (SUB_AGENT_DISPATCH)
    assert 1 in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-unsafe-kind",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # fail closed — the unfenced branch is NOT re-dispatched


def test_crash_resume_cascade_cancel_incomplete_mixed_safe_unsafe_fails_closed() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION — a MIX of maybe-ran branches: one re-fire-safe
    (DECLARATIVE_STEP) + one still-unfenced effect-bearing (SUB_AGENT_DISPATCH — recursive-child residual, NOT the fence-recoverable
    TOOL_STEP). The presence of ANY genuinely-unrecoverable maybe-ran branch fails the WHOLE
    incomplete recovery closed (the safe subset is not partially recovered — that would still leave
    the unsafe branch unresolved)."""
    store = _InMemoryBranchStore()
    steps = [
        _step("branch-0", 0, kind=StepKind.DECLARATIVE_STEP),
        _step("branch-1", 1, kind=StepKind.DECLARATIVE_STEP),
        _step("branch-2", 2, kind=StepKind.SUB_AGENT_DISPATCH),
    ]
    _run_persona(
        workflow_id="wf-cc-mixed",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # maybe-ran DECLARATIVE (re-fire-safe)
    store.forget_branch(
        key, 2
    )  # maybe-ran SUB_AGENT_DISPATCH (unfenced → poisons the whole recovery)
    assert store.present_dispatched_indexes(key) - {0} == {1, 2}

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-mixed",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # fail closed — one unsafe maybe-ran poisons the set


def test_crash_resume_cascade_cancel_cardinality_only_refire_safe_recovers() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION (cardinality-only path) — every branch is
    MAYBE-RAN of a RE-FIRE-SAFE kind. The cardinality marker is present but NOTHING is readably
    recovered (`_determine_fanout_resume` → None); every branch BEGAN dispatch (markers KEPT) but
    none was captured. All maybe-ran branches are DECLARATIVE_STEP → re-fire-safe → the run
    RECOVERS as a fresh re-dispatch (every branch fires once). The effect-bearing-kind variant
    still fails closed — see the sibling cardinality-only unsafe test."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-cardinality-only",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    for i in range(3):
        store.forget_branch(key, i)  # output gone, markers KEPT → all branches MAYBE-RAN
    assert store.read_fanout_cardinality(key) == 3
    assert store.read_branch_records(key) == {}
    assert store.present_dispatched_indexes(key) == {0, 1, 2}  # all maybe-ran

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-cardinality-only",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.SUCCESS
    # Fresh re-dispatch of every branch (re-fire-safe); each fires exactly once.
    assert sorted(resume.dispatched) == ["branch-0", "branch-1", "branch-2"]


def test_crash_resume_cascade_cancel_cardinality_only_unsafe_kind_fails_closed() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION (cardinality-only path) — an UNFENCED
    effect-bearing (SUB_AGENT_DISPATCH — recursive-child residual, NOT the fence-recoverable TOOL_STEP / MANAGED_AGENTS) maybe-ran branch in a
    cardinality-only store still FAILS CLOSED (neither the re-fire-safe nor the fence-recovery
    relaxation applies). The contrasting positive controls are the re-fire-safe + fence-recoverable
    TOOL_STEP siblings above."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.SUB_AGENT_DISPATCH) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-cardinality-unsafe",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    for i in range(3):
        store.forget_branch(key, i)  # all maybe-ran, all SUB_AGENT_DISPATCH (unfenced)
    assert store.present_dispatched_indexes(key) == {0, 1, 2}

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-cardinality-unsafe",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # fail closed on the cardinality-only effect-bearing store


def test_crash_resume_maybe_ran_changed_manifest_kind_fails_closed() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION — the changed-manifest at-most-once guard
    (out-of-family Codex [P1]). A branch dispatched as an EFFECT-BEARING kind (TOOL_STEP) that
    crashed before terminal capture is RE-SUPPLIED at the SAME ordinal as a RE-FIRE-SAFE kind
    (DECLARATIVE_STEP) on a same-cardinality resume (same workflow_id → same run_key → the Run-1
    markers are found). The classifier keys on the marker's RECORDED dispatch-time kind
    (TOOL_STEP), NOT the resumed manifest's kind → fail closed (the original tool effect may have
    fired; re-dispatch would double-fire). Were it to key on the resumed DECLARATIVE kind, it
    would wrongly recover → SUCCESS. Asserting FAILED proves the marker-keying."""
    store = _InMemoryBranchStore()
    # Run 1: all TOOL_STEP; branch 1 crashes maybe-ran (marker [TOOL_STEP] kept, output gone).
    steps_v1 = [_step(f"branch-{i}", i, kind=StepKind.TOOL_STEP) for i in range(3)]
    _run_persona(
        workflow_id="wf-changed-manifest",
        steps=steps_v1,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # maybe-ran: marker (TOOL_STEP) kept, output gone
    assert store.dispatched_branch_kinds(key)[1] == StepKind.TOOL_STEP.value

    # Run 2 (resume): branch 1 re-supplied as a RE-FIRE-SAFE DECLARATIVE_STEP (changed kind, same
    # ordinal + step_id). The marker still says TOOL_STEP → fail closed.
    resume = _CountingDispatcher(n=3)
    steps_v2 = [
        _step("branch-0", 0, kind=StepKind.TOOL_STEP),
        _step("branch-1", 1, kind=StepKind.DECLARATIVE_STEP),  # CHANGED from TOOL_STEP
        _step("branch-2", 2, kind=StepKind.TOOL_STEP),
    ]
    r2 = _run_persona(
        workflow_id="wf-changed-manifest",
        steps=steps_v2,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # keyed on the DISPATCH-TIME TOOL_STEP marker → fail closed


def test_crash_resume_maybe_ran_pre_arc_marker_no_kind_fails_closed() -> None:
    """A v1.60/v1.61 dispatch marker (step_id only, NO recorded kind — or a torn write) cannot
    prove the original kind → the maybe-ran classifier treats it as UNSAFE → fail closed
    (defensive; the recorded dispatch-time kind is the at-most-once authority, and an un-kinded
    marker is not trustworthy). Even though the branch is a DECLARATIVE_STEP in the manifest."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]  # DECLARATIVE (re-fire-safe normally)
    _run_persona(
        workflow_id="wf-prearc-marker",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # maybe-ran
    store.forget_branch_dispatch_kind(key, 1)  # simulate a pre-arc / torn marker: kind → None
    assert store.dispatched_branch_kinds(key)[1] is None

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-prearc-marker",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.FAILED  # un-kinded marker → cannot prove re-fire-safe → closed
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []


def test_crash_resume_maybe_ran_out_of_range_marker_fails_closed() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION — an out-of-range / stale dispatch marker (a
    corrupt `branch-99.dispatched` left from a larger prior fan-out) recording a re-fire-safe
    kind must NOT be ignored: the store no longer matches the declared fan-out → fail closed
    (out-of-family Codex [P2]). Branch 1 is a legitimate re-fire-safe maybe-ran; branch 99 is out
    of range → the whole incomplete recovery fails closed."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]  # DECLARATIVE (re-fire-safe)
    _run_persona(
        workflow_id="wf-stale-marker",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # legitimate re-fire-safe maybe-ran
    store.inject_stale_dispatch_marker(key, 99, "declarative-step")  # out-of-range, safe kind
    assert 99 in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-stale-marker",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.FAILED  # out-of-range marker → store mismatch → fail closed
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []


def test_crash_resume_cardinality_only_orchestrator_out_of_range_marker_fails_closed() -> None:
    """B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION — the cardinality-only out-of-range bound uses
    the WORKER count, not the recorded `len(steps)` cardinality (which for ORCHESTRATOR_WORKERS
    INCLUDES the orchestrator `steps[0]`). A stale `branch-{worker_count}.dispatched` marker (a
    worker ordinal one past the last real worker) with a re-fire-safe kind must fail closed, not
    re-run fresh (out-of-family Codex [P2] — `_cardinality` over-counts by one for orchestrated)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w0", 0), _step("w1", 1)]  # 1 orchestrator + 2 workers
    _run_persona(
        workflow_id="wf-orch-stale-card",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_undispatched(key)  # nothing readably recovered (orchestrator-None)
    store.record_fanout_cardinality(key, len(steps))  # recorded = 3 (INCLUDES the orchestrator)
    store.record_dispatch_instrumented(key)
    # worker ordinal 2 is OUT OF RANGE (only 2 workers: ordinals 0, 1) — `_cardinality`=3 would
    # wrongly accept it (2 < 3); the worker-count bound (3 − 1 = 2) rejects it (2 ≥ 2).
    store.inject_stale_dispatch_marker(key, 2, "declarative-step")
    assert store.present_dispatched_indexes(key) == {2}

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-orch-stale-card",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.FAILED  # worker-count bound → branch-2 out of range → closed
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []


def test_crash_resume_cascade_cancel_errored_branch_reproduces_failed() -> None:
    """An errored branch under CASCADE_CANCEL (the cascade trigger fired before the crash) →
    reproduce FAILED on resume, NEVER re-dispatching (the not-yet-dispatched siblings stay
    cancelled — re-dispatching would run effects the compliance tier deliberately stopped)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-fail",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),  # branch 1 errors → trigger
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    # branch 1 is captured `completed`-no-output (the trigger). Forget branch 2 to model a
    # genuinely-cancelled (not-yet-dispatched, absent) sibling: it must NOT be re-dispatched.
    store.forget_branch(store.sole_run_key(), 2)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-fail",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None and "fan-out-crash-resume-cascade-cancel" in r2.fail_class
    assert resume.dispatched == []  # FAILED reproduced; NO branch (incl. the absent one) re-run


def test_crash_resume_pause_complete_recovery_completes() -> None:
    """The complete-recovery continue path also holds under PAUSE (TEAM_BINDING): all branches
    recovered, none errored → finalize from the recovered set → SUCCESS, re-dispatch nothing."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-complete",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-complete",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []


def test_crash_resume_pause_incomplete_fails_closed() -> None:
    """An INCOMPLETE recovery with a MAYBE-RAN still-unfenced effect-bearing branch (SUB_AGENT_DISPATCH —
    NOT the fence-recoverable TOOL_STEP) under PAUSE (TEAM_BINDING) also fails closed —
    `forget_branch` keeps the dispatch marker, so branch 0 is maybe-ran (dispatched, no capture)
    and its vendor-session effect MAY have fired with no fence → not re-dispatchable on the team
    tier either. Both relaxations (re-fire-safe + fence-recovery) are tier-agnostic (see the
    recovery siblings)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.SUB_AGENT_DISPATCH) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-incomplete",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch(key, 0)  # output gone, marker KEPT → maybe-ran (SUB_AGENT_DISPATCH)
    assert 0 in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-incomplete",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []


def test_crash_resume_pause_incomplete_refire_safe_recovers() -> None:
    """The re-fire-safe maybe-ran relaxation is TIER-AGNOSTIC — a maybe-ran DECLARATIVE_STEP
    branch under PAUSE (TEAM_BINDING) recovers exactly as under CASCADE_CANCEL (the classifier
    keys on `cascade_policy is not PROCEED`, not on the specific strict tier)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-refire-safe",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    key = store.sole_run_key()
    store.forget_branch(key, 0)  # maybe-ran DECLARATIVE (re-fire-safe)
    assert 0 in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-refire-safe",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["branch-0"]  # only the maybe-ran branch re-dispatches


def test_crash_resume_pause_incomplete_errored_fails_closed_ambiguous() -> None:
    """B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT (CP spec v1.68 §2) — the INCOMPLETE case STAYS
    fail-closed (`pause-trigger-ambiguous`). An errored branch fired the pause AND a sibling is
    ABSENT (here forgotten → maybe-ran): the crash-interrupted store does NOT hold every
    finished-in-flight branch, so a reconstruct cannot honor §25.15.1 'finish in-flight, then
    pause'. No re-dispatch. (Only the COMPLETE-recovery window reconstructs — see below.)"""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-fail",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    key = store.sole_run_key()
    store.forget_branch(key, 2)  # a clean sibling's OUTPUT gone → INCOMPLETE recovery (absent #2)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-fail",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    assert r2.status is RunStatus.FAILED
    assert (
        r2.fail_class is not None
        and "fan-out-crash-resume-pause-trigger-ambiguous" in r2.fail_class
    )
    assert resume.dispatched == []


def test_crash_resume_pause_complete_reconstructs_paused() -> None:
    """B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT (CP spec v1.68 §1) — a COMPLETE-recovery degraded
    PAUSE crash-resume RE-ESTABLISHES the lost PAUSED state (Reading A). All 3 branches captured
    (branch-1 errored), the snapshot-write-window crash → reconstruct → PAUSED with a re-captured
    PeerFanOutResumeState snapshot; re-dispatch NOTHING."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-recon",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )  # COMPLETE recovery (all 3 captured, branch-1 errored) — no forget.

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-recon",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    assert r2.status is RunStatus.PAUSED
    assert resume.dispatched == []  # complete recovery → re-establish only, re-dispatch nothing
    assert r2.pause_snapshot is not None
    pr = r2.pause_snapshot.peer_fan_out_resume
    assert pr is not None
    # The errored trigger (branch-1) is represented IDENTICALLY to a live pause: terminal_status
    # "completed", output None; the clean siblings carry their captured output.
    by_index = {b.branch_index: b for b in pr.branches}
    assert set(by_index) == {0, 1, 2}
    assert all(b.terminal_status == "completed" for b in pr.branches)
    assert by_index[1].output is None
    assert by_index[0].output == {"branch": 0}
    assert by_index[2].output == {"branch": 2}


def test_crash_resume_pause_reconstruct_byte_matches_live_pause_then_resume_equal() -> None:
    """The result-fidelity witness (`[[full-chain-witness-not-half-proofs]]`, the #746 lesson):
    a COMPLETE-recovery crash-resume reconstruct produces a snapshot whose resume-carrier
    `branches` BYTE-EQUAL a real (non-crashed) pause snapshot's, and resuming the reconstruct
    yields the SAME PARTIAL state as resuming the real pause. No faked dispatcher, no proxy."""
    steps = [_step(f"branch-{i}", i) for i in range(3)]

    # run1 IS the live pause (branch-1 fails under PAUSE → PAUSED) AND populates the store; its
    # snapshot is the non-crashed baseline. run2 IGNORES it (resume_snapshot is None) and
    # reconstructs from the store → the crash model (the durable snapshot was lost).
    store = _InMemoryBranchStore()
    live = _run_persona(
        workflow_id="wf-pause-fid",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    assert live.status is RunStatus.PAUSED and live.pause_snapshot is not None
    recon = _run_persona(
        workflow_id="wf-pause-fid",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    assert recon.status is RunStatus.PAUSED and recon.pause_snapshot is not None

    # The load-bearing surface a consumer reads — the resume carrier's branches — byte-match.
    assert (
        recon.pause_snapshot.peer_fan_out_resume.branches  # type: ignore[union-attr]
        == live.pause_snapshot.peer_fan_out_resume.branches  # type: ignore[union-attr]
    )

    # Resuming EITHER snapshot yields the identical PARTIAL result (final-state fidelity).
    live_resume = _run_persona(
        workflow_id="wf-pause-fid",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=_InMemoryBranchStore(),
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
        pause_snapshot_input=live.pause_snapshot,
    )
    recon_resume = _run_persona(
        workflow_id="wf-pause-fid",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=_InMemoryBranchStore(),
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
        pause_snapshot_input=recon.pause_snapshot,
    )
    assert live_resume.status is RunStatus.PARTIAL
    assert recon_resume.status is live_resume.status
    assert recon_resume.partial_state == live_resume.partial_state


def test_crash_resume_pause_reconstruct_protocol_not_bound_fails_honestly() -> None:
    """Detect-then-refuse: a COMPLETE-recovery degraded PAUSE crash-resume with NO bound
    pause_resume_protocol cannot capture a snapshot → fail HONESTLY (never a false-resumable
    PAUSED), not silently reconstruct or finalize."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-nobind",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    r2 = _run_persona(
        workflow_id="wf-pause-nobind",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,  # NO protocol bound
    )
    assert r2.status is RunStatus.FAILED
    assert r2.fail_class is not None
    assert "pause-resume-protocol-not-bound" in r2.fail_class


def test_crash_resume_pause_complete_non_degraded_succeeds() -> None:
    """No pause was triggered (no branch errored) → a COMPLETE non-degraded PAUSE crash-resume
    finalizes SUCCESS, NOT a spurious re-established pause. The reconstruct fires ONLY on a
    degraded recovered set (a genuine pause trigger)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-clean",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-clean",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []


def test_crash_resume_pause_orchestrator_complete_reconstructs_paused() -> None:
    """The ORCHESTRATOR_WORKERS analogue — a complete recovery short-circuits at the `not
    branch_plan` block, where the re-establish builds a FanOutResumeState-bearing snapshot →
    PAUSED (covers HIERARCHICAL_DELEGATION too, which delegates to this strategy)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-ow-pause-recon",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2, fail_index=1),  # worker w-1 errors → pause trigger
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        pause_resume_protocol=_pause_protocol(),
    )
    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-pause-recon",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        pause_resume_protocol=_pause_protocol(),
    )
    assert r2.status is RunStatus.PAUSED
    assert resume.dispatched == []  # complete recovery → re-dispatch nothing
    assert r2.pause_snapshot is not None
    fr = r2.pause_snapshot.fan_out_resume
    assert fr is not None  # orchestrator-bearing carrier (NOT peer)
    assert {b.branch_index for b in fr.branches} == {0, 1}


def test_crash_resume_pause_reconstruct_idempotent_recrash() -> None:
    """The reconstruct is idempotent — a re-crash before the operator resumes re-reconstructs
    the SAME snapshot (the reconstruct does not auto-persist; same store + same inputs → byte-
    equal carrier), so no double-fire / divergence on repeated recovery."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-idem",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    r_a = _run_persona(
        workflow_id="wf-pause-idem",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    r_b = _run_persona(
        workflow_id="wf-pause-idem",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
    )
    assert r_a.status is RunStatus.PAUSED and r_b.status is RunStatus.PAUSED
    assert (
        r_a.pause_snapshot.peer_fan_out_resume.branches  # type: ignore[union-attr]
        == r_b.pause_snapshot.peer_fan_out_resume.branches  # type: ignore[union-attr]
    )


def test_crash_resume_pause_recovered_timeout_is_partial_not_paused() -> None:
    """Out-of-family Codex [P2] regression guard — a RECOVER_AS_TERMINAL `timed_out` branch is a
    degraded NON-contributor, NOT a pause trigger (a live timeout is `deadline_struck`→FAILED,
    never a pause). A COMPLETE crash-resume whose ONLY degraded branch is a recovered timeout
    (no genuine `completed`+no-output FAILURE) finalizes PARTIAL, NOT a spurious re-established
    PAUSED — even with a bound protocol. The re-establish keys on the failure disposition, not
    `output is None`."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-timeout",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),  # all branches CLEAN — no genuine failure
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    key = store.sole_run_key()
    store.timeout_branch(key, 1)  # branch 1 → (step_id, "timed_out", None): a recovered timeout

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-timeout",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    assert r2.status is RunStatus.PARTIAL  # recovered-timeout degraded → PARTIAL, NOT PAUSED
    assert r2.pause_snapshot is None
    assert resume.dispatched == []


def test_crash_resume_pause_timeout_plus_safe_absent_recovers_not_ambiguous() -> None:
    """Out-of-family Codex [P2] (round 2) — an INCOMPLETE PAUSE crash-resume whose degraded set is
    a recovered timeout PLUS a re-fire-safe absent ordinal (NO genuine `completed`+no-output
    FAILURE) must NOT fail closed `pause-trigger-ambiguous` (no branch failure lost a pause). The
    block-level PAUSE leg keys on the genuine-failure trigger, NOT `output is None` — so it falls
    through to the incomplete-recovery classifier, which re-dispatches the safe branch + finalizes
    PARTIAL (the timeout is the degraded non-contributor)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]  # DECLARATIVE_STEP = re-fire-safe
    _run_persona(
        workflow_id="wf-pause-timeout-safe",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),  # all clean — no genuine failure
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    key = store.sole_run_key()
    store.timeout_branch(key, 1)  # branch 1 → recovered timeout (degraded non-contributor)
    store.forget_branch(key, 2)  # branch 2 → maybe-ran, re-fire-safe DECLARATIVE (marker kept)
    assert 2 in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-timeout-safe",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    assert r2.status is RunStatus.PARTIAL  # recovers (NOT pause-trigger-ambiguous)
    assert r2.fail_class is None
    assert resume.dispatched == ["branch-2"]  # only the safe absent ordinal re-dispatches


def test_crash_resume_pause_genuine_failure_plus_timeout_reestablishes_paused() -> None:
    """The mixed case (advisor) — a COMPLETE recovery with BOTH a genuine `completed`+no-output
    FAILURE (the pause trigger) AND a recovered `timed_out` branch. The genuine failure triggers
    the re-establish → PAUSED; the recovered timeout flows into the snapshot as a degraded terminal
    (`terminal_status == "timed_out"`). NOTE this is the RECOVER_AS_TERMINAL-faithful PAUSED
    disposition, NOT a byte-match of a live pause — a live run with a deadline-cut branch hits
    `deadline_struck`→FAILED before the pause path, so no live pause snapshot ever holds a
    `timed_out` branch. At-most-once holds (nothing re-dispatched; resume skips both terminals)."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-mixed",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3, fail_index=1),  # branch 1 GENUINELY errors
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    key = store.sole_run_key()
    store.timeout_branch(key, 2)  # branch 2 → recovered timeout (a degraded sibling of the failure)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-mixed",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        pause_resume_protocol=_pause_protocol(),
        timeout_disposition=FanoutTimeoutDisposition.RECOVER_AS_TERMINAL,
    )
    assert r2.status is RunStatus.PAUSED  # the genuine failure triggers the re-establish
    assert resume.dispatched == []  # complete recovery → re-dispatch nothing
    pr = r2.pause_snapshot.peer_fan_out_resume  # type: ignore[union-attr]
    by_index = {b.branch_index: b for b in pr.branches}  # type: ignore[union-attr]
    assert by_index[1].terminal_status == "completed" and by_index[1].output is None  # the failure
    assert by_index[2].terminal_status == "timed_out"  # the recovered timeout, faithfully carried


def test_crash_resume_cascade_cancel_orchestrator_workers_errored() -> None:
    """Advisor — VERIFY the orchestrator leg, don't assume symmetry. The cascade trigger under
    ORCHESTRATOR_WORKERS is always a WORKER failure (an orchestrator failure returns FAILED
    directly before any worker — `workflow_driver.py:6548` 'cascade_policy governs WORKER
    failure'). So detection over `.branches` (the workers) covers it: an errored worker under
    CASCADE_CANCEL → FAILED on resume, no re-dispatch (orchestrator recovered, not the trigger)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-ow-cc-fail",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2, fail_index=1),  # worker w-1 errors → trigger
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert store.orchestrator_present(store.sole_run_key())

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-cc-fail",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-cancel" in (r2.fail_class or "")
    assert resume.dispatched == []  # FAILED reproduced; orchestrator + workers never re-run


def test_crash_resume_cascade_cancel_orchestrator_workers_complete_completes() -> None:
    """ORCHESTRATOR_WORKERS complete recovery under CASCADE_CANCEL — the orchestrator + ALL
    workers recovered (none absent, none errored) → finalize from the recovered set → SUCCESS,
    re-dispatch nothing (the strict-tier continue path, orchestrator topology)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-ow-cc-complete",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-cc-complete",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == []  # orchestrator + all workers recovered → nothing re-dispatched


# ===========================================================================
# B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE (R-FS-1) — the lifted capability:
# the strict tiers (PAUSE / CASCADE_CANCEL) now RECOVER an incomplete crash by
# re-dispatching ONLY the PROVABLY-not-run branches (reserve-before-dispatch markers),
# instead of failing closed. A maybe-ran branch (marker, no capture) or a pre-arc
# un-stamped journal still fails closed (the cross-version guard).
# ===========================================================================
def test_crash_resume_cascade_cancel_provably_not_run_recovers() -> None:
    """The core lift. A NOT-YET-DISPATCHED branch (no dispatch marker, no capture) is PROVABLY
    not-run, so a CASCADE_CANCEL crash-resume re-dispatches ONLY it (first-and-only) + recovers
    the captured siblings → SUCCESS. The no-double-fire witness: `resume.dispatched == ["branch-1"]`
    proves the recovered branches fire exactly once (in Run 1), not again on resume."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-not-run",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    # Branch 1 was NOT-YET-DISPATCHED at the crash: drop BOTH its output and its marker.
    store.forget_branch_undispatched(key, 1)
    assert store.read_branch_records(key).keys() == {0, 2}
    assert 1 not in store.present_dispatched_indexes(key)  # provably not-run

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-not-run",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["branch-1"]  # ONLY the provably-not-run branch re-fires
    # The recovered aggregate matches a clean no-crash run.
    baseline = _run_persona(
        workflow_id="wf-cc-baseline",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=_InMemoryBranchStore(),
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.final_state is not None and baseline.final_state is not None
    assert r2.final_state["branch_outputs"] == baseline.final_state["branch_outputs"]


def test_crash_resume_pause_provably_not_run_recovers() -> None:
    """The lift holds under PAUSE (TEAM_BINDING) too: a not-yet-dispatched branch re-dispatches,
    the captured siblings recover → SUCCESS, re-dispatching only the provably-not-run branch."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-pause-not-run",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    key = store.sole_run_key()
    store.forget_branch_undispatched(key, 2)
    assert 2 not in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-pause-not-run",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["branch-2"]


def test_crash_resume_orchestrator_workers_provably_not_run_recovers() -> None:
    """The lift under ORCHESTRATOR_WORKERS: a not-yet-dispatched WORKER re-dispatches while the
    orchestrator + the captured worker recover. The orchestrator is NOT re-dispatched (recovered
    from its own record); only the provably-not-run worker re-fires."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-ow-not-run",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_branch_undispatched(key, 1)  # worker w-1 not-yet-dispatched
    assert store.orchestrator_present(key)
    assert 1 not in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-not-run",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["w-1"]  # orchestrator + w-0 recovered; only w-1 re-fires


def test_crash_resume_hierarchical_top_level_provably_not_run_recovers() -> None:
    """The lift under HIERARCHICAL_DELEGATION (top level — reuses `_execute_orchestrator_workers`,
    so it threads the strict-tier reserve-before-dispatch path). Witnesses the clearance-marker
    claim of hierarchical coverage (`[[full-chain-witness-not-half-proofs]]`). Cross-LEVEL keying
    is safe by construction: `run_idempotency_key = sha256(run_id, workflow_id)` and each child
    level re-enters with a DISTINCT child workflow_id → a distinct store dir → no branch_index
    collision across levels (the markers key identically to `record_branch`)."""
    store = _InMemoryBranchStore()
    steps = [_step("parent", 0), _step("child-0", 0), _step("child-1", 1)]  # ≤3 (cap 3)
    _run_persona(
        workflow_id="wf-hd-not-run",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
    )
    key = store.sole_run_key()
    store.forget_branch_undispatched(key, 1)  # child-1 not-yet-dispatched (provably not-run)
    assert store.orchestrator_present(key)
    assert 1 not in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-hd-not-run",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
    )
    assert r2.status is RunStatus.SUCCESS
    assert "parent" not in resume.dispatched  # the orchestrator is recovered, not re-fired
    assert resume.dispatched == ["child-1"]  # only the provably-not-run child re-dispatches


def test_crash_resume_cardinality_only_no_dispatch_recovers_fresh() -> None:
    """The cardinality-only lift: a crash AFTER the cardinality marker but BEFORE any branch
    BEGAN dispatch (instrumented stamp present, ZERO dispatch markers) is provably a no-branch-
    started state → the run re-dispatches every branch fresh (first-and-only) → SUCCESS, rather
    than failing closed. (Contrast the maybe-ran cardinality-only test, which keeps the markers.)"""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-card-fresh",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    for i in range(3):
        store.forget_branch_undispatched(key, i)  # no output AND no marker for any branch
    assert store.read_fanout_cardinality(key) == 3
    assert store.present_dispatched_indexes(key) == set()
    assert store.dispatch_instrumented(key)  # the run WAS instrumented

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-card-fresh",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.SUCCESS
    assert sorted(resume.dispatched) == [
        "branch-0",
        "branch-1",
        "branch-2",
    ]  # all re-dispatch fresh


def test_crash_resume_incomplete_pre_arc_journal_fails_closed() -> None:
    """THE CROSS-VERSION GUARD (advisor BLOCKING). A crash journal written by PRE-arc code has NO
    dispatch markers for ANY branch — including a maybe-ran one. Classifying its absent branches
    'provably not-run' would re-dispatch + double-fire. The instrumented STAMP is the guard: an
    un-stamped journal retains the conservative fail-closed even though no markers exist."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-pre-arc",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    key = store.sole_run_key()
    store.forget_branch(key, 1)  # branch 1 absent (output)
    store.simulate_pre_arc_journal(key)  # clear the stamp AND all markers (a pre-arc journal)
    assert not store.dispatch_instrumented(key)
    assert store.present_dispatched_indexes(key) == set()  # no markers at all

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-pre-arc",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # un-stamped journal → fail closed, no re-dispatch


def test_crash_resume_mixed_not_run_and_maybe_ran_fails_closed() -> None:
    """A maybe-ran UNFENCED effect-bearing branch poisons the recovery even when another absent
    branch is provably not-run. Branch 1 is not-yet-dispatched (safe) but branch 2 is maybe-ran
    SUB_AGENT_DISPATCH (NOT the fence-recoverable TOOL_STEP / MANAGED_AGENTS — marker kept, output gone, child effect
    MAY have fired with no fence). `present_dispatched − recovered = {2}` ≠ ∅ AND branch 2 is
    genuinely-unrecoverable → fail closed — the at-most-once guarantee admits re-dispatch of a
    maybe-ran branch only when it is provably not-run, a re-fire-safe kind, OR a fence-recoverable
    TOOL_STEP."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i, kind=StepKind.SUB_AGENT_DISPATCH) for i in range(3)]
    _run_persona(
        workflow_id="wf-cc-mixed-notrun",
        steps=steps,
        dispatcher=_CountingDispatcher(n=3),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(_CountingDispatcher(n=3)),
    )
    key = store.sole_run_key()
    store.forget_branch_undispatched(key, 1)  # provably not-run
    store.forget_branch(
        key, 2
    )  # maybe-ran SUB_AGENT_DISPATCH (marker kept) — genuinely-unrecoverable
    assert 1 not in store.present_dispatched_indexes(key)
    assert 2 in store.present_dispatched_indexes(key)

    resume = _CountingDispatcher(n=3)
    r2 = _run_persona(
        workflow_id="wf-cc-mixed-notrun",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-cascade-policy-incomplete-recovery" in (r2.fail_class or "")
    assert resume.dispatched == []  # any re-fire-unsafe maybe-ran branch → fail closed


# ===========================================================================
# B-FANOUT-CRASH-RESUME-ORCHESTRATOR-DISPATCH (R-FS-1) — the orchestrator `steps[0]`'s
# OWN dispatch-before-capture window. The orchestrator runs FIRST (sequentially); a crash
# after it fires its effect but before `record_orchestrator` would, PRE-arc, re-dispatch
# `steps[0]` fresh → a double-fire on the strict tiers. The reserve-before-DISPATCH marker
# (the sequential analogue of the per-worker reserve) makes that window provably-not-run
# (no marker → fresh) or maybe-ran (marker, no capture → fail closed).
# ===========================================================================
def test_crash_resume_orchestrator_maybe_ran_re_fire_safe_recovers_cascade_cancel() -> None:
    """B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-RESOLUTION (CP spec v1.64 §1) — the re-fire-safe
    relaxation. The orchestrator dispatched (marker + instrumented stamp) but its output was never
    captured (the crash fell in its fire→capture window). Its DISPATCH-TIME kind is DECLARATIVE_STEP
    (re-fire-safe — no external effect), so re-dispatching `steps[0]` fresh cannot double-fire →
    the CASCADE_CANCEL (MULTI_TENANT_COMPLIANCE) crash-resume RECOVERS, re-dispatching the
    orchestrator + both workers first-and-only (was: failed closed unconditionally pre-v1.64)."""
    store = _InMemoryBranchStore()
    steps = [
        _step("orch", 0),
        _step("w-0", 0),
        _step("w-1", 1),
    ]  # _step ⇒ DECLARATIVE (re-fire-safe)
    _run_persona(
        workflow_id="wf-ow-orch-maybe-ran",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_maybe_ran(key)  # marker kept (kind=DECLARATIVE), the rest gone
    assert store.orchestrator_dispatched(key)  # the orchestrator BEGAN dispatch
    assert not store.orchestrator_present(key)  # but its output was never captured
    assert store.dispatch_instrumented(key)  # the run WAS instrumented
    assert store.orchestrator_dispatched_kind(key) == StepKind.DECLARATIVE_STEP.value

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-orch-maybe-ran",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["orch", "w-0", "w-1"]  # re-fire-safe → all re-dispatch fresh


def test_crash_resume_orchestrator_maybe_ran_re_fire_safe_recovers_pause() -> None:
    """The re-fire-safe orchestrator-maybe-ran recovery holds under PAUSE (TEAM_BINDING) too — a
    re-fire-safe (no-external-effect) orchestrator re-runs fresh regardless of the strict tier."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-ow-orch-maybe-ran-pause",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_maybe_ran(key)

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-orch-maybe-ran-pause",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.TEAM_BINDING,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["orch", "w-0", "w-1"]


def test_crash_resume_orchestrator_maybe_ran_effect_bearing_fails_closed() -> None:
    """An EFFECT-BEARING orchestrator (TOOL_STEP) maybe-ran STAYS fail-closed — its effect may have
    landed; re-dispatching `steps[0]` would double-fire. The effect-bearing-orchestrator resolution
    is the registered follow-on B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-EFFECT-BEARING. The
    DISPATCH-TIME kind in the marker (TOOL_STEP) — not the resumed manifest — governs."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0, StepKind.TOOL_STEP), _step("w-0", 0), _step("w-1", 1)]
    registry = _AnyKindRegistry(_CountingDispatcher(n=2))  # serves the TOOL_STEP orchestrator
    _run_persona(
        workflow_id="wf-ow-orch-effect-bearing",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        registry=registry,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_maybe_ran(key)
    assert store.orchestrator_dispatched_kind(key) == StepKind.TOOL_STEP.value

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-orch-effect-bearing",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
        registry=_AnyKindRegistry(resume),
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-orchestrator-maybe-ran" in (r2.fail_class or "")
    assert resume.dispatched == []  # NOT re-dispatched (no double-fire of an effect-bearing orch)


def test_crash_resume_orchestrator_maybe_ran_pre_v1_81_marker_fails_closed() -> None:
    """A pre-v1.81 (v1.79-era) orchestrator marker recorded only `step_id`, no dispatch-time kind.
    `orchestrator_dispatched_kind` → None → the classifier cannot prove re-fire-safety → fail
    closed (the v1.79 behavior preserved; presence ≠ validity, never a wrongful re-dispatch — the
    cross-version at-most-once guard `[[durable-recovery-presence-validity-scope]]`)."""
    store = _InMemoryBranchStore()
    steps = [
        _step("orch", 0),
        _step("w-0", 0),
        _step("w-1", 1),
    ]  # re-fire-safe kind in the manifest
    _run_persona(
        workflow_id="wf-ow-orch-pre-v181",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_maybe_ran(key)
    store.forget_orchestrator_dispatch_kind(key)  # model a pre-v1.81 marker (step_id only, no kind)
    assert store.orchestrator_dispatched(key)  # presence intact
    assert store.orchestrator_dispatched_kind(key) is None  # but the kind is unknown

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-orch-pre-v181",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.FAILED
    assert "fan-out-crash-resume-orchestrator-maybe-ran" in (r2.fail_class or "")
    assert resume.dispatched == []


def test_crash_resume_orchestrator_provably_not_run_recovers_fresh() -> None:
    """A crash BEFORE the orchestrator dispatched (no marker, no output, no cardinality) is
    PROVABLY not-run → the run re-dispatches everything fresh (first-and-only), re-firing the
    orchestrator + both workers, rather than failing closed (the marker is absent, so there is
    no double-fire risk)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-ow-orch-not-run",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_undispatched(key)  # no marker, no output → provably not-run
    assert not store.orchestrator_dispatched(key)

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-ow-orch-not-run",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["orch", "w-0", "w-1"]  # all re-dispatch fresh (incl. orchestrator)


def test_crash_resume_hierarchical_orchestrator_maybe_ran_re_fire_safe_recovers() -> None:
    """The re-fire-safe orchestrator-maybe-ran recovery threads through HIERARCHICAL_DELEGATION too
    (the top level reuses `_execute_orchestrator_workers`, so it threads the orchestrator
    reserve-before-dispatch + maybe-ran-classification path). Witnesses the hierarchical coverage
    claim (`[[full-chain-witness-not-half-proofs]]`) — the marker keys by the run's own key, so the
    DECLARATIVE (re-fire-safe) parent maybe-ran recovers fresh here too (was: failed closed)."""
    store = _InMemoryBranchStore()
    steps = [_step("parent", 0), _step("child-0", 0), _step("child-1", 1)]
    _run_persona(
        workflow_id="wf-hd-orch-maybe-ran",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_maybe_ran(key)
    assert store.orchestrator_dispatched(key) and not store.orchestrator_present(key)
    assert store.orchestrator_dispatched_kind(key) == StepKind.DECLARATIVE_STEP.value

    resume = _CountingDispatcher(n=2)
    r2 = _run_persona(
        workflow_id="wf-hd-orch-maybe-ran",
        steps=steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
    )
    assert r2.status is RunStatus.SUCCESS
    assert resume.dispatched == ["parent", "child-0", "child-1"]  # re-fire-safe → re-dispatch fresh


def test_crash_resume_parallelization_orchestrator_marker_topology_mismatch_fails_closed() -> None:
    """Changed-topology guard widened to the orchestrator MARKER. A run crashes mid-orchestrator
    (marker present, output absent) under ORCHESTRATOR_WORKERS, then resumes under a PARALLELIZATION
    manifest (same run key). The peer fan-out never writes an orchestrator marker, so its presence
    proves a topology change → fail closed rather than dropping the maybe-ran orchestrator effect."""
    store = _InMemoryBranchStore()
    ow_steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    _run_persona(
        workflow_id="wf-topo-mismatch",
        steps=ow_steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    key = store.sole_run_key()
    store.forget_orchestrator_maybe_ran(key)  # only the orchestrator marker survives
    assert store.orchestrator_dispatched(key) and not store.orchestrator_present(key)

    resume = _CountingDispatcher(n=2)
    peer_steps = [_step("p-0", 0), _step("p-1", 1)]
    r2 = _run_persona(
        workflow_id="wf-topo-mismatch",
        steps=peer_steps,
        dispatcher=resume,
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        topology=TopologyPattern.PARALLELIZATION,
    )
    assert r2.status is RunStatus.FAILED
    assert "topology mismatch" in (r2.fail_class or "")
    assert resume.dispatched == []


def test_crash_resume_proceed_orchestrator_writes_no_marker() -> None:
    """PROCEED is byte-unchanged: an ORCHESTRATOR_WORKERS run under SOLO_DEVELOPER (PROCEED) writes
    NO orchestrator reserve-before-dispatch marker (and no instrumented stamp). The PROCEED-tier
    orchestrator pre-capture double-fire window is the registered follow-on residual, not closed
    here — #724's effect-free-synthesis justification does not transfer to the orchestrator, so it
    is named in `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-RESOLUTION`, not silently absorbed."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    r = _run_persona(
        workflow_id="wf-ow-proceed-no-marker",
        steps=steps,
        dispatcher=_CountingDispatcher(n=2),
        store=store,
        persona_tier=_PROCEED_TIER,
        topology=TopologyPattern.ORCHESTRATOR_WORKERS,
    )
    assert r.status is RunStatus.SUCCESS
    key = store.sole_run_key()
    assert not store.orchestrator_dispatched(key)  # PROCEED writes no orchestrator marker
    assert not store.dispatch_instrumented(key)  # nor the instrumented stamp
    assert store.orchestrator_present(key)  # the reserve-before-COMMIT capture is unchanged


def test_crash_resume_orchestrator_lookup_failure_writes_no_marker() -> None:
    """A dispatcher LOOKUP failure raises BEFORE any orchestrator effect can fire, so it must
    leave NO orchestrator dispatched marker — else a false marker would poison a later same-
    run-key recovery into a spurious fail-closed (out-of-family Codex [P2]). The marker is
    written STRICTLY BETWEEN the (pure) lookup and the dispatch, so a lookup failure → FAILED
    with a clean store (no marker, no stamp)."""
    store = _InMemoryBranchStore()
    steps = [_step("orch", 0), _step("w-0", 0), _step("w-1", 1)]
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), store=store))
    r = execute_workflow(
        _manifest(
            workflow_id="wf-ow-lookup-fail",
            topology=TopologyPattern.ORCHESTRATOR_WORKERS,
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,  # strict tier (would write a marker)
        ),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _LookupRaisesRegistry()),
    )
    assert r.status is RunStatus.FAILED  # the orchestrator dispatch could not be resolved
    # The store holds NO orchestrator marker — the lookup failed before the marker write, so a
    # later recovery for this run_key is NOT poisoned into a false maybe-ran fail-closed.
    assert store._orchestrator_dispatched == {}  # no false marker anywhere
    assert store._instrumented == set()  # nor the stamp (it is written with the marker)


class _FullChainEffectFenceError(Exception):
    """Test-local stand-in for the runtime `effect_fence.EffectFenceAmbiguousUncommittedError`
    (name-matched by the driver; harness-cp cannot import harness-runtime)."""

    def __init__(self, *, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__("ambiguous")


class _CascadeCancelFenceDispatcher:
    """branch-0 completes (sets a gate); branch-1 waits then raises the fence-ambiguous error.
    Under cascade-cancel, branch-1's fence-pause halts the fan-out → FAILED; the driver must record
    branch-1's `completed`/no-output terminal to the durable STORE (not just the buffered ledger)."""

    def __init__(self) -> None:
        self._gate = threading.Event()
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if int(step.step_payload["index"]) == 0:
            self._gate.set()
            return {"branch": 0}
        assert self._gate.wait(timeout=10.0), "branch-0 never completed"
        raise _FullChainEffectFenceError(idempotency_key="fence-key")


def test_cascade_cancel_fence_paused_branch_terminal_captured_to_store() -> None:
    """Codex [P2] R1 regression: under CASCADE_CANCEL a fence-paused branch's `completed`/no-output
    terminal is captured to the durable STORE (not just the buffered ledger), so a crash mid-
    cascade-cancel reproduces the FAILED on resume instead of mis-classifying the branch as
    maybe-ran (dispatch marker present, no terminal) + re-dispatching it. Without the store capture
    branch-1 would carry ONLY its dispatch marker."""
    store = _InMemoryBranchStore()
    steps = [_step(f"branch-{i}", i) for i in range(2)]  # DECLARATIVE; the catch is name-matched
    r = _run(
        workflow_id="wf-cc-fence-store",
        topology=TopologyPattern.PARALLELIZATION,
        steps=steps,
        dispatcher=_CascadeCancelFenceDispatcher(),
        store=store,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,  # → cascade-cancel
    )
    assert r.status is RunStatus.FAILED
    assert "parallelization-cascade-cancel" in (r.fail_class or "")
    records = store.read_branch_records(store.sole_run_key())
    # The fence-paused branch-1 is recorded `completed`/no-output in the STORE (the Codex fix) — a
    # terminal record, so a crash-resume recovers it as terminal, NEVER re-dispatches it maybe-ran.
    assert 1 in records
    assert records[1][1] == "completed"  # terminal_status
    assert records[1][2] is None  # output (no output — the effect's ambiguity lives at the fence)

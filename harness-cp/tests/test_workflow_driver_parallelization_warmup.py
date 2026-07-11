"""B-18-3C-PREWARM — concurrent-prompt-cache warm-up for PARALLELIZATION strategy.

Tests the ADR-D4 §1.8 serialized branch[0] warm-up path added to `_execute_parallelization`
in `workflow_driver.py`.  The first section targets the PROCEED cascade-policy path
(PersonaTier.SOLO_DEVELOPER → CascadePolicy.PROCEED → warm-up gate evaluated).

Acceptance-criterion coverage (`.harness/u1-3c-prewarm-design-decision-record.md` §6+§11.5):

  Ordering witness — branch[0] serialized before siblings start:
    → test_warmup_serializes_branch0_before_siblings

  M1 (H1 fix) — branch[0] failure still dispatches siblings + PARTIAL:
    → test_warmup_branch0_failure_siblings_dispatched_and_partial

  M5 (H3 fix) — singleton branch_plan skips serialization:
    → test_warmup_singleton_branch_plan_no_serialization

  M6 — DECLARATIVE_STEP blocks predicate → all-concurrent (reverse-completion witness):
    → test_warmup_predicate_declarative_step_all_concurrent

  M8 — non-uniform thinking blocks predicate → all-concurrent (reverse-completion witness):
    → test_warmup_predicate_nonuniform_thinking_all_concurrent

  Gate-off regression — concurrent_cache_warmup=False → no serialization even with
  uniform INFERENCE_STEP:
    → test_warmup_gate_off_all_concurrent

B-18-3C-PREWARM-CASCADE section (`.harness/b18-3c-prewarm-cascade-ddr.md` §6 witnesses;
CP spec v1.90 §25.17 addendum) — the warm-up extended to the strict tiers
(CASCADE_CANCEL = MULTI_TENANT_COMPLIANCE / PAUSE = TEAM_BINDING via `_cancel_fanout`):

  W1 ordering witness (both strict tiers):
    → test_cascade_warmup_serializes_branch0_before_siblings
  W2 CASCADE_CANCEL branch[0]-fail — siblings withheld (no dispatch marker) + `cancelled`:
    → test_cascade_cancel_warmup_branch0_failure_siblings_withheld_cancelled_failed
  W3 PAUSE branch[0]-fail — snapshot carries only branch[0]; resume re-dispatches rest:
    → test_pause_warmup_branch0_failure_pauses_then_resume_redispatches_siblings
  W4 gate=False baseline unchanged (non-CohortKeyCapable → all-concurrent; both tiers):
    → test_cascade_cancel_warmup_gate_false_all_concurrent_baseline
  W4b partial-recovery resume warms the REMAINING cohort (new "branch[0]"; Fable-5 C4):
    → test_pause_warmup_partial_recovery_resume_new_branch0_serialized
  W5 PROCEED unmodified — the pre-existing section above stays green post-lift.
  W6 crash-window re-entry re-pauses (DDR §3b) — NEVER a silent PARTIAL:
    → test_pause_warmup_crash_window_reentry_repauses_never_silent_partial
  W7 R3 guard — a bare branch[0] TimeoutError is a branch FAILURE, never the deadline:
    → test_pause_warmup_branch0_bare_timeout_error_is_branch_failure_not_deadline
    → test_cascade_cancel_warmup_branch0_bare_timeout_error_fails_as_cascade

B-18-3C-PREWARM-TIMEOUT-LEDGER section (M2, DDR §11.5; CP spec v1.91 §25.17
addendum) — obligation-4 `cancelled` terminals synthesized at every TERMINAL
fan-out exit for branches withheld past the boundary (never-dispatched → zero
footprint would be indistinguishable from lost entries):

  ML1 PROCEED Phase-1 deadline strike → PARTIAL; withheld siblings `cancelled`
  (terminal-only, ledger-only):
    → test_proceed_warmup_phase1_deadline_strike_records_cancelled_for_withheld
  ML2 PAUSE Phase-1 deadline strike → FAILED barrier-deadline; siblings
  `cancelled` in ledger + dispatch-marker ABSENCE in store:
    → test_pause_warmup_phase1_deadline_strike_failed_with_cancelled_terminals
  ML3 CASCADE_CANCEL Phase-1 deadline strike → FAILED cascade-cancel; the
  pre-existing obl-4 scan (now the shared helper) covers the deadline path:
    → test_cascade_cancel_warmup_phase1_deadline_strike_cancelled_via_scan
  ML4 PAUSE branch[0]-failure + protocol NOT bound → terminal FAILED
  protocol-not-bound runs the scan (C2 — no snapshot, omission ≠ re-dispatchable):
    → test_pause_warmup_branch0_failure_protocol_not_bound_records_cancelled
  ML5 negative control — branch-failure → PAUSED does NOT run the scan
  (snapshot omission IS the re-dispatchable contract):
    → test_pause_warmup_branch0_failure_paused_siblings_zero_ledger_footprint
  ML6 baseline no-op — gate=False all-concurrent deadline strike: every branch
  in-flight-cut records `timed_out`; the absence-keyed scan synthesizes nothing:
    → test_baseline_all_concurrent_deadline_strike_no_cancelled_synthesis

Authority: `.harness/u1-3c-prewarm-design-decision-record.md` +
`.harness/b18-3c-prewarm-cascade-ddr.md` (Fable-5 review-cleared);
ADR-D4 v1.1 §1.8; `Spec_Control_Plane_v1_86.md` §25.15; CP spec v1.90 §25.17;
CP spec v1.91 (M2 terminal-exit synthesis).
"""

from __future__ import annotations

import asyncio
import os
import threading
import time
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
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
    FanOutBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Identifier

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _manifest(
    *,
    concurrent_cache_warmup: bool = True,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    workflow_id: str = "wf-warmup",
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
) -> WorkflowManifestEntry:
    """PARALLELIZATION manifest.  Default: SOLO_DEVELOPER → PROCEED + warmup=True.
    The CASCADE witnesses pass TEAM_BINDING (→ pause) / MULTI_TENANT_COMPLIANCE
    (→ cascade-cancel) and, for the store-bound crash-window tests, a
    `_FANOUT_REPLAY_ENGINE_CLASSES` member (EVENT_SOURCED_REPLAY)."""
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=engine_class,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
        concurrent_cache_warmup=concurrent_cache_warmup,
    )


def _inference_step(index: int, *, thinking: bool | None = None) -> WorkflowStep:
    """One branch step of kind INFERENCE_STEP — satisfies the same-prefix predicate
    when `thinking` is uniform across all branches (default None → no params key)."""
    payload: dict[str, Any] = {"index": index}
    if thinking is not None:
        payload["params"] = {"thinking": thinking}
    return WorkflowStep(
        step_id=StepID(f"inf-{index}"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload=payload,
    )


def _declarative_step(index: int) -> WorkflowStep:
    """DECLARATIVE_STEP — predicate returns False immediately (not INFERENCE_STEP)."""
    return WorkflowStep(
        step_id=StepID(f"dec-{index}"),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"index": index},
    )


class _RecordingLedger:
    """In-memory ledger sink that records drained appends."""

    def __init__(self) -> None:
        from harness_is.state_ledger_entry_schema import Actor, ActorClass

        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-warmup")
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
        from harness_core.workflow_event_class import WorkflowEventClass

        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: Any) -> None:
        self.emits.append(event_class)


class _Ctx:
    """Minimal fake DriverContext for PARALLELIZATION e2e.

    `pause_resume_protocol` (the pause/resume opt-in) and `engine_output_store`
    (the fan-out crash-resume substrate) default None/absent — the CASCADE
    witnesses bind them where the strict-tier path needs a snapshot / marker."""

    def __init__(
        self,
        *,
        ledger: Any,
        emitter: _Emitter,
        pause_resume_protocol: Any = None,
        engine_output_store: Any = None,
    ) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = __import__("asyncio").Event()
        self.pause_resume_protocol = pause_resume_protocol
        self.pause_requested_flag = __import__("asyncio").Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.engine_output_store = engine_output_store


class _InferenceRegistry:
    """Registry that routes INFERENCE_STEP (and optionally DECLARATIVE_STEP)
    to a single dispatcher — used to test mixed-kind predicate failure."""

    def __init__(self, dispatcher: StepDispatcher, *, also_declarative: bool = False) -> None:
        self._dispatcher = dispatcher
        self._also_declarative = also_declarative

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.INFERENCE_STEP:
            return self._dispatcher
        if self._also_declarative and step_kind is StepKind.DECLARATIVE_STEP:
            return self._dispatcher
        raise StepKindDispatcherNotBoundError(step_kind)


def _registry(
    dispatcher: StepDispatcher, *, also_declarative: bool = False
) -> StepDispatcherRegistry:
    return cast(
        StepDispatcherRegistry, _InferenceRegistry(dispatcher, also_declarative=also_declarative)
    )


def _run(
    *,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    ledger: Any | None = None,
    concurrent_cache_warmup: bool = True,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    also_declarative: bool = False,
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
    store: Any = None,
    with_pause_protocol: bool = False,
    pause_snapshot_input: PauseSnapshot | None = None,
    workflow_id: str = "wf-warmup",
) -> Any:
    if ledger is None:
        ledger = _RecordingLedger()
    emitter = _Emitter()
    ctx = cast(
        DriverContext,
        _Ctx(
            ledger=ledger,
            emitter=emitter,
            pause_resume_protocol=_protocol() if with_pause_protocol else None,
            engine_output_store=store,
        ),
    )
    return execute_workflow(
        _manifest(
            concurrent_cache_warmup=concurrent_cache_warmup,
            persona_tier=persona_tier,
            workflow_id=workflow_id,
            engine_class=engine_class,
        ),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher, also_declarative=also_declarative),
        pause_snapshot_input=pause_snapshot_input,
    )


# ---------------------------------------------------------------------------
# Dispatchers
# ---------------------------------------------------------------------------


class _WarmupOrderingWitness:
    """Records whether branch[0] was done before each sibling entered dispatch.

    Thread-safe.  branch[0] sleeps briefly to give siblings a window to start
    if dispatched concurrently (all-concurrent path).  Each sibling checks the
    `branch0_done` event at entry — with warmup, it must already be set.
    """

    def __init__(self) -> None:
        self.branch0_done = threading.Event()
        self._lock = threading.Lock()
        self.sibling_b0_done_on_entry: dict[int, bool] = {}

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = step.step_payload["index"]
        if idx == 0:
            time.sleep(0.02)
            self.branch0_done.set()
        else:
            with self._lock:
                self.sibling_b0_done_on_entry[idx] = self.branch0_done.is_set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"

    def assert_serialized(self, *, n: int) -> None:
        assert self.branch0_done.is_set(), "branch[0] never dispatched"
        for i in range(1, n):
            assert self.sibling_b0_done_on_entry.get(i) is True, (
                f"branch[{i}] started before branch[0] completed"
                f" (branch0_done_on_entry={self.sibling_b0_done_on_entry})"
            )


class _SimpleDispatcher:
    """Returns `{"branch": idx}` without error."""

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        return {"branch": step.step_payload["index"]}


class _FailBranch0Dispatcher:
    """Raises RuntimeError for branch[0]; succeeds for all others."""

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = step.step_payload["index"]
        if idx == 0:
            raise RuntimeError("simulated branch-0 failure (H1 regression)")
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


class _ReverseCompletionDispatcher:
    """Forces reverse-index completion order: branch i waits for branch i+1 to
    complete first.  On the all-concurrent path this succeeds (all threads run
    concurrently and the chain resolves).  On the serialized warmup path, branch[0]
    waits for branch[1] which hasn't started yet → DEADLOCK.  Use this dispatcher
    only in tests where the predicate is expected to be False (all-concurrent)."""

    def __init__(self, *, n: int) -> None:
        self._events = {i: threading.Event() for i in range(n)}
        self._n = n

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = step.step_payload["index"]
        higher = idx + 1
        if higher < self._n:
            assert self._events[higher].wait(timeout=10.0), (
                f"reverse-completion: branch[{higher}] never completed"
            )
        self._events[idx].set()
        return {"branch": idx}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_warmup_serializes_branch0_before_siblings() -> None:
    """Ordering witness: with concurrent_cache_warmup=True and a uniform
    INFERENCE_STEP cohort, branch[0] must complete before any sibling starts
    (the serialized cache-write phase)."""
    n = 4
    witness = _WarmupOrderingWitness()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=witness,
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.SUCCESS
    witness.assert_serialized(n=n)


def test_warmup_branch0_failure_siblings_dispatched_and_partial() -> None:
    """H1 regression: a branch[0] exception is captured (not bare-awaited), so
    branches[1..N-1] still dispatch and buffered ledger entries drain → PARTIAL."""
    n = 3
    ledger = _RecordingLedger()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=_FailBranch0Dispatcher(),
        ledger=ledger,
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.PARTIAL
    # All 3 branches contributed ledger entries (step + terminal per branch).
    branch_indices_seen = {payload.branch_metadata.branch_index for payload, _wk in ledger.appends}
    assert branch_indices_seen == {0, 1, 2}, f"missing branches in ledger: {branch_indices_seen}"


def test_warmup_singleton_branch_plan_no_serialization() -> None:
    """H3 regression: len(branch_plan) < 2 → _same_prefix_cohort() returns False
    → _warmup_gate=False even with concurrent_cache_warmup=True.  Singleton branch
    must succeed on the all-concurrent path."""
    result = _run(
        steps=[_inference_step(0)],
        dispatcher=_SimpleDispatcher(),
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.SUCCESS


def test_warmup_predicate_declarative_step_all_concurrent() -> None:
    """M6: DECLARATIVE_STEP uses a non-CohortKeyCapable dispatcher (mirrors
    production: sub-agent / tool / HITL dispatchers are not CohortKeyCapable) →
    _same_prefix_cohort() returns False → _warmup_gate=False → all-concurrent.
    Verified via ReverseCompletionDispatcher (would deadlock on the serialized path)."""
    n = 3
    reverse = _ReverseCompletionDispatcher(n=n)
    result = _run(
        steps=[_declarative_step(i) for i in range(n)],
        dispatcher=reverse,
        concurrent_cache_warmup=True,
        also_declarative=True,
    )
    assert result.status is RunStatus.SUCCESS


def test_warmup_predicate_nonuniform_thinking_all_concurrent() -> None:
    """M8 (non-CohortKeyCapable path): a non-CohortKeyCapable INFERENCE_STEP
    dispatcher → _same_prefix_cohort() returns False → _warmup_gate=False →
    all-concurrent.  Verified via ReverseCompletionDispatcher.

    The cohort-key encoding of thinking-uniformity (CohortKeyCapable path where
    non-uniform thinking yields different keys) is tested via RK-5 in test_cohort_key_rtllm.py."""
    n = 3
    # branch[0] has thinking=True; others have thinking=None → non-uniform.
    steps = [_inference_step(0, thinking=True)] + [_inference_step(i) for i in range(1, n)]
    reverse = _ReverseCompletionDispatcher(n=n)
    result = _run(
        steps=steps,
        dispatcher=reverse,
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.SUCCESS


def test_warmup_gate_off_all_concurrent() -> None:
    """Regression: concurrent_cache_warmup=False → _warmup_gate=False even with a
    uniform INFERENCE_STEP cohort that would otherwise satisfy the predicate.
    ReverseCompletionDispatcher confirms all-concurrent execution (no deadlock)."""
    n = 3
    reverse = _ReverseCompletionDispatcher(n=n)
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=reverse,
        concurrent_cache_warmup=False,
    )
    assert result.status is RunStatus.SUCCESS


# ---------------------------------------------------------------------------
# B-18-3C-PREWARM-CASCADE — warm-up on the strict tiers (CASCADE_CANCEL / PAUSE)
# via `_cancel_fanout`.  Witnesses W1-W6 per `.harness/b18-3c-prewarm-cascade-ddr.md`
# §6; CP spec v1.90 §25.17 addendum.
# ---------------------------------------------------------------------------


def _pause_context_reader() -> tuple[StateSummary, str]:
    """MVP constant-sentinel reader (mirrors the parallelization-pause harness):
    empty StateSummary + a constant anchor → resume detects no material diff →
    admits."""
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


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


def _captured_peer_snapshot(
    *, peer: PeerFanOutResumeState, workflow_id: str = "wf-warmup"
) -> PauseSnapshot:
    """A hash-valid peer fan-out snapshot captured through the real protocol (NOT a
    hand-mutated model) — the exact shape a prior `pause` halt would produce."""
    return asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id=workflow_id,
            run_id="run-1",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            peer_fan_out_resume=peer,
        )
    )


class _MiniFanoutStore:
    """Minimal in-memory EngineOutputStore fake covering the PARALLELIZATION
    produce + strict-tier crash-resume consume surface (the subset of the
    full-chain `_InMemoryBranchStore` these witnesses touch)."""

    def __init__(self) -> None:
        self._branches: dict[str, dict[int, tuple[str, str, dict[str, Any] | None]]] = {}
        self._cardinality: dict[str, int] = {}
        self._instrumented: set[str] = set()
        self._dispatched: dict[str, dict[int, str | None]] = {}
        self._dispatched_step_id: dict[str, dict[int, str | None]] = {}

    # -- producer surface --
    def record_fanout_cardinality(self, run_key: str, branch_count: int) -> None:
        self._cardinality[run_key] = int(branch_count)

    def record_dispatch_instrumented(self, run_key: str) -> None:
        self._instrumented.add(run_key)

    def record_branch(
        self,
        run_key: str,
        branch_index: int,
        step_id: str,
        terminal_status: str,
        output: dict[str, Any] | None,
    ) -> None:
        self._branches.setdefault(run_key, {})[int(branch_index)] = (
            str(step_id),
            str(terminal_status),
            dict(output) if output is not None else None,
        )

    def record_branch_dispatched(
        self,
        run_key: str,
        branch_index: int,
        step_id: str,
        step_kind: str,
        child_recoverable: bool | None = None,
        child_engine_class: str | None = None,
    ) -> None:
        _ = (child_recoverable, child_engine_class)
        self._dispatched.setdefault(run_key, {})[int(branch_index)] = str(step_kind)
        self._dispatched_step_id.setdefault(run_key, {})[int(branch_index)] = str(step_id)

    def record_synthesis(
        self, run_key: str, step_id: str, output: dict[str, Any], self_hash: str
    ) -> None:
        _ = (run_key, step_id, output, self_hash)

    # -- consumer surface (crash-resume classification) --
    def read_fanout_cardinality(self, run_key: str) -> int | None:
        return self._cardinality.get(run_key)

    def fanout_cardinality_present(self, run_key: str) -> bool:
        return run_key in self._cardinality

    def dispatch_instrumented(self, run_key: str) -> bool:
        return run_key in self._instrumented

    def read_branch_records(
        self, run_key: str
    ) -> dict[int, tuple[str, str, dict[str, Any] | None]]:
        return dict(self._branches.get(run_key, {}))

    def present_branch_indexes(self, run_key: str) -> set[int]:
        return set(self._branches.get(run_key, {}))

    def present_dispatched_indexes(self, run_key: str) -> set[int]:
        return set(self._dispatched.get(run_key, {}))

    def dispatched_branch_kinds(self, run_key: str) -> dict[int, str | None]:
        return dict(self._dispatched.get(run_key, {}))

    def dispatched_branch_step_ids(self, run_key: str) -> dict[int, str | None]:
        return dict(self._dispatched_step_id.get(run_key, {}))

    def subagent_child_recoverable_indexes(self, run_key: str) -> set[int]:
        _ = run_key
        return set()

    def dispatched_branch_child_engine_classes(self, run_key: str) -> dict[int, str | None]:
        _ = run_key
        return {}

    def synthesis_present(self, run_key: str) -> bool:
        _ = run_key
        return False

    def read_synthesis(self, run_key: str) -> tuple[str, dict[str, Any], str] | None:
        _ = run_key
        return None

    def orchestrator_present(self, run_key: str) -> bool:
        _ = run_key
        return False

    def read_orchestrator_output(self, run_key: str) -> tuple[str, dict[str, Any]] | None:
        _ = run_key
        return None

    def orchestrator_dispatched(self, run_key: str) -> bool:
        _ = run_key
        return False

    def orchestrator_dispatched_kind(self, run_key: str) -> str | None:
        _ = run_key
        return None

    def orchestrator_dispatched_step_id(self, run_key: str) -> str | None:
        _ = run_key
        return None

    def orchestrator_dispatched_proceed_unstamped(self, run_key: str) -> bool:
        _ = run_key
        return False

    def orchestrator_subagent_child_recoverable(self, run_key: str) -> bool:
        _ = run_key
        return False

    def orchestrator_dispatched_child_engine_class(self, run_key: str) -> str | None:
        _ = run_key
        return None

    def sole_run_key(self) -> str:
        keys = set(self._branches) | set(self._cardinality) | set(self._dispatched)
        assert len(keys) == 1, f"expected exactly one recorded run_key, got {keys}"
        return next(iter(keys))


class _RecordingCohortDispatcher:
    """CohortKeyCapable dispatcher that records dispatched branch indices; indices
    in `fail` raise (the Phase-1 / cascade trigger)."""

    def __init__(self, *, fail: set[int] | None = None) -> None:
        self._fail = fail or set()
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx in self._fail:
            raise RuntimeError(f"simulated branch-{idx} failure (cascade trigger)")
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


class _OrderingWitnessFrom:
    """Ordering witness for a partially-recovered cohort: `first_index` is the
    expected NEW "branch[0]" (the first LIVE ordinal after recovery, Fable-5 C4).
    Records whether it completed before each later live sibling entered dispatch."""

    def __init__(self, *, first_index: int) -> None:
        self._first = first_index
        self.first_done = threading.Event()
        self._lock = threading.Lock()
        self.dispatched: list[int] = []
        self.sibling_first_done_on_entry: dict[int, bool] = {}

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx == self._first:
            time.sleep(0.02)
            self.first_done.set()
        else:
            with self._lock:
                self.sibling_first_done_on_entry[idx] = self.first_done.is_set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


@pytest.mark.parametrize(
    "persona_tier",
    [PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE],
    ids=["pause-tier", "cascade-cancel-tier"],
)
def test_cascade_warmup_serializes_branch0_before_siblings(persona_tier: PersonaTier) -> None:
    """W1 ordering witness: with warmup on and a uniform cohort, the strict-tier
    `_cancel_fanout` serializes branch[0] (Phase 1, cache-write) before any
    sibling starts (Phase 2). Clean run stays SUCCESS on both strict tiers."""
    n = 4
    witness = _WarmupOrderingWitness()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=witness,
        concurrent_cache_warmup=True,
        persona_tier=persona_tier,
    )
    assert result.status is RunStatus.SUCCESS
    witness.assert_serialized(n=n)


def test_cascade_cancel_warmup_branch0_failure_siblings_withheld_cancelled_failed() -> None:
    """W2: CASCADE_CANCEL + warmup, branch[0] fails in Phase 1 → branches[1..N-1]
    are WITHHELD (never dispatched: no dispatch marker in the durable store — the
    DDR §2 effect-set-subset invariant, asserted per Fable-5 M1 as marker ABSENCE,
    not just `cancelled` records), the post-barrier scan records their `cancelled`
    terminals, and the run FAILs per §25.15.1."""
    n = 3
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    dispatcher = _RecordingCohortDispatcher(fail={0})
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=dispatcher,
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-cascade-cancel"
    # Only branch[0] ever dispatched (siblings withheld by the Phase-1 failure).
    assert dispatcher.dispatched == [0]
    # M1: dispatch-marker ABSENCE for the withheld siblings (not merely `cancelled`).
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0}
    # The not-yet-dispatched scan recorded `cancelled` terminals for the siblings.
    cancelled = {
        payload.branch_metadata.branch_index
        for payload, _wk in ledger.appends
        if payload.branch_metadata is not None
        and payload.branch_metadata.terminal_status == "cancelled"
    }
    assert cancelled == {1, 2}


def test_pause_warmup_branch0_failure_pauses_then_resume_redispatches_siblings() -> None:
    """W3: PAUSE + warmup, branch[0] fails in Phase 1 → PAUSED with a snapshot
    carrying ONLY branch[0] (terminal `completed`, no output); the withheld
    siblings are left re-dispatchable by omission. `api.resume` (snapshot input)
    re-dispatches exactly the siblings, skips terminal branch[0] → PARTIAL
    (branch[0] is a degraded non-contributor)."""
    n = 3
    dispatcher = _RecordingCohortDispatcher(fail={0})
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
    )
    assert result.status is RunStatus.PAUSED
    assert dispatcher.dispatched == [0]
    snapshot = result.pause_snapshot
    assert snapshot is not None
    peer = snapshot.peer_fan_out_resume
    assert peer is not None
    assert [(b.branch_index, b.terminal_status, b.output) for b in peer.branches] == [
        (0, "completed", None)
    ]
    assert peer.branch_count == n

    # Resume: siblings re-dispatch (warmed among themselves); branch[0] never re-fires.
    resume_dispatcher = _RecordingCohortDispatcher()
    resumed = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=resume_dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    assert resumed.status is RunStatus.PARTIAL
    assert sorted(resume_dispatcher.dispatched) == [1, 2]


@pytest.mark.parametrize(
    "persona_tier",
    [PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE],
    ids=["pause-tier", "cascade-cancel-tier"],
)
def test_cascade_cancel_warmup_gate_false_all_concurrent_baseline(
    persona_tier: PersonaTier,
) -> None:
    """W4: gate=False baseline — a non-CohortKeyCapable dispatcher keeps
    `_warmup_gate` False on BOTH strict tiers, routing to the pre-arc
    `cascade_cancel_barrier` all-concurrent path (ReverseCompletionDispatcher
    would deadlock on any serialized path)."""
    n = 3
    reverse = _ReverseCompletionDispatcher(n=n)
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=reverse,
        concurrent_cache_warmup=True,
        persona_tier=persona_tier,
    )
    assert result.status is RunStatus.SUCCESS


class _TimeoutErrorBranch0Dispatcher:
    """CohortKeyCapable dispatcher whose branch[0] raises a BARE TimeoutError —
    a branch FAILURE that must NOT be misclassified as the barrier deadline
    (Fable-5 R3; the Phase-1 `except asyncio.CancelledError: raise`-only guard)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx == 0:
            raise TimeoutError("simulated branch-0 TimeoutError (a branch failure, NOT deadline)")
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


def test_pause_warmup_branch0_bare_timeout_error_is_branch_failure_not_deadline() -> None:
    """W7 (Fable-5 diff-review concern 3): a bare `TimeoutError` raised BY
    branch[0] in Phase 1 is a branch FAILURE — it must classify as
    `branch_failed` (PAUSE tier → PAUSED with a branch[0]-only snapshot), NEVER
    as the barrier deadline (which would be FAILED
    `parallelization-barrier-deadline`, no snapshot). Pins the R3-corrected
    Phase-1 guard (`except asyncio.CancelledError: raise` ONLY) against a
    regression re-widening it to `except (asyncio.CancelledError, TimeoutError)`."""
    n = 3
    dispatcher = _TimeoutErrorBranch0Dispatcher()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
    )
    assert result.status is RunStatus.PAUSED, (
        "R3 regression: branch[0]'s bare TimeoutError was misclassified as the "
        f"barrier deadline (status={result.status}, fail_class={result.fail_class!r})"
    )
    assert dispatcher.dispatched == [0]
    snapshot = result.pause_snapshot
    assert snapshot is not None
    peer = snapshot.peer_fan_out_resume
    assert peer is not None
    assert [(b.branch_index, b.terminal_status, b.output) for b in peer.branches] == [
        (0, "completed", None)
    ]


def test_cascade_cancel_warmup_branch0_bare_timeout_error_fails_as_cascade() -> None:
    """W7 (CASCADE_CANCEL leg): the same bare branch[0] `TimeoutError` under the
    cascade-cancel tier maps to FAILED `parallelization-cascade-cancel` (the
    branch-failure fail_class) — NOT `parallelization-barrier-deadline`."""
    n = 3
    dispatcher = _TimeoutErrorBranch0Dispatcher()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-cascade-cancel"
    assert dispatcher.dispatched == [0]


def test_pause_warmup_partial_recovery_resume_new_branch0_serialized() -> None:
    """W4b (Fable-5 C4): a partial-recovery resume with 2+ remaining branches
    applies the warm-up to the RESUMED fan-out with a NEW "branch[0]" — the first
    remaining ordinal. Snapshot carries branches 0+1 terminal-with-outputs; the
    live plan is {2, 3}; branch[2] (Phase 1) completes before branch[3] enters."""
    n = 4
    snapshot = _captured_peer_snapshot(
        peer=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="inf-0",
                    terminal_status="completed",
                    output={"branch": 0},
                ),
                FanOutBranchResumeState(
                    branch_index=1,
                    step_id="inf-1",
                    terminal_status="completed",
                    output={"branch": 1},
                ),
            ),
            branch_count=n,
        )
    )
    witness = _OrderingWitnessFrom(first_index=2)
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=witness,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [2, 3]
    assert witness.sibling_first_done_on_entry.get(3) is True, (
        "branch[3] started before the resumed cohort's new branch[0] (=2) completed"
        f" (entries={witness.sibling_first_done_on_entry})"
    )


def test_pause_warmup_crash_window_reentry_repauses_never_silent_partial() -> None:
    """W6 (the decisive DDR §3b witness): PAUSE + warmup, branch[0] fails in
    Phase 1 and the host "crashes" before the operator consumes the PAUSED
    snapshot (modeled by re-entering WITHOUT `pause_snapshot_input`, sharing the
    durable store). The re-entry must re-establish PAUSED — never fall through to
    a silent PARTIAL that swallows branch[0]'s failure, and never re-dispatch the
    withheld siblings (their re-dispatch is `api.resume`'s operator-gated
    decision).

    Empirical grounding (2026-07-11 pre-build probe, this arc): the DDR §3b /
    Fable-5 R2 "critical gap" is REFUTED on HEAD — the entry-time crash-resume
    gate (B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT, CP spec v1.68 §1 + v1.70 §1)
    classifies the withheld siblings provably-not-run (instrumented + no dispatch
    marker) → `_crash_pause_reconstruct_no_dispatch` → empty branch_plan →
    `_crash_pause_reestablish` re-pauses. The DDR's Option A pre-barrier
    `branch_failed` synthesis is therefore NOT built (it would be dead code);
    this witness pins the covered behavior against regression (CP spec v1.90
    §25.17). The CASCADE_CANCEL analogue FAILs at the same entry gate
    (`fan-out-crash-resume-cascade-cancel`) — pinned by the pre-existing
    committed witness
    `test_crash_resume_cascade_cancel_errored_branch_reproduces_failed`
    (test_workflow_driver_fanout_output_replay_full_chain.py)."""
    n = 3
    store = _MiniFanoutStore()
    crash_dispatcher = _RecordingCohortDispatcher(fail={0})
    first = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=crash_dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    # Run 1 (the "crashed" invocation): live warmup pause — branch[0] terminal
    # `completed`/no-output captured durably; siblings withheld (marker ABSENT).
    assert first.status is RunStatus.PAUSED
    assert crash_dispatcher.dispatched == [0]
    run_key = store.sole_run_key()
    assert store.present_dispatched_indexes(run_key) == {0}
    assert store.read_branch_records(run_key)[0][1:] == ("completed", None)

    # Run 2 (crash re-entry: snapshot LOST — no pause_snapshot_input): re-pauses.
    reentry_dispatcher = _RecordingCohortDispatcher()
    second = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=reentry_dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    assert second.status is RunStatus.PAUSED, (
        "DDR §3b regression: the crash-window re-entry must re-establish PAUSED, "
        f"never a silent {second.status} (fail_class={second.fail_class!r})"
    )
    assert reentry_dispatcher.dispatched == []
    resnap = second.pause_snapshot
    assert resnap is not None
    repeer = resnap.peer_fan_out_resume
    assert repeer is not None
    assert [(b.branch_index, b.terminal_status, b.output) for b in repeer.branches] == [
        (0, "completed", None)
    ]


# ---------------------------------------------------------------------------
# E2E skeleton — B-18-3C-PREWARM-DEFAULT-ON
# ---------------------------------------------------------------------------


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — live Anthropic prefix-cache hit test skipped",
)
def test_warmup_default_on_live_cache_hit() -> None:  # pragma: no cover
    """B-18-3C-PREWARM-DEFAULT-ON live acceptance skeleton (CP spec v1.89 §25.17).

    Verifies that a WorkflowManifestEntry constructed WITHOUT explicit
    `concurrent_cache_warmup` gets the new default of True. The structural run
    below uses _ReverseCompletionDispatcher (non-CohortKeyCapable) → _same_prefix_cohort()
    returns False → _warmup_gate=False → all-concurrent baseline (the safety
    property: default-True + non-cohort dispatcher = byte-identical to old default-False).

    The ordering-witness tests above cover the serialized branch[0] path with
    a CohortKeyCapable dispatcher. This skeleton documents where the Anthropic
    live-cache-hit test belongs once a cache-instrumented dispatcher is built.

    TODO (follow-on): add a cache-instrumented live dispatcher that asserts
    siblings receive anthropic cache_read_input_tokens > 0 (cache hit on siblings).
    """
    # Verify the WME default flows correctly without any explicit setting.
    entry = WorkflowManifestEntry(
        workflow_id="wf-default-on-live",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
        # concurrent_cache_warmup intentionally omitted → must be True by default
    )
    assert entry.concurrent_cache_warmup is True, (
        "B-18-3C-PREWARM-DEFAULT-ON: WME default must be True per ADR-D4 §1.8(f)"
    )

    # Structural run with non-CohortKeyCapable dispatcher → gate stays False → baseline SUCCESS.
    n = 3
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=_ReverseCompletionDispatcher(n=n),
        concurrent_cache_warmup=entry.concurrent_cache_warmup,
    )
    assert result.status is RunStatus.SUCCESS


# ---------------------------------------------------------------------------
# B-18-3C-PREWARM-TIMEOUT-LEDGER (M2) — terminal-exit audit completeness
# ---------------------------------------------------------------------------


class _WedgeBranch0CohortDispatcher:
    """CohortKeyCapable dispatcher whose `wedge_index` branch (default the
    original branch[0]) blocks past the (monkeypatched) barrier deadline — the
    Phase-1 deadline-strike trigger (a resume's NEW "branch[0]" is the first
    remaining ordinal, so the C3 witness wedges index 1). Records dispatched
    indices so the withheld-siblings claim is asserted at the dispatch level too.
    Self-releases at `self_release_seconds` as a CI backstop; the test also sets
    `release` in a `finally` so the abandoned worker thread exits promptly
    (mirrors `_BlockingDispatcher` in test_workflow_driver_parallelization.py)."""

    def __init__(
        self,
        *,
        release: threading.Event,
        self_release_seconds: float,
        wedge_index: int = 0,
    ) -> None:
        self._release = release
        self._self_release_seconds = self_release_seconds
        self._wedge_index = wedge_index
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx == self._wedge_index:
            self._release.wait(timeout=self._self_release_seconds)
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


class _BlockingAllDispatcher:
    """NON-CohortKeyCapable (no `cohort_key`) dispatcher that wedges EVERY branch —
    the gate=False all-concurrent deadline-strike baseline (every branch in-flight
    when the cut lands)."""

    def __init__(self, *, release: threading.Event, self_release_seconds: float) -> None:
        self._release = release
        self._self_release_seconds = self_release_seconds
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        self._release.wait(timeout=self._self_release_seconds)
        return {"branch": idx}


def _branch_terminals(ledger: _RecordingLedger) -> dict[int, str]:
    """branch_index -> drained terminal_status."""
    return {
        payload.branch_metadata.branch_index: payload.branch_metadata.terminal_status
        for payload, _wk in ledger.appends
        if getattr(payload, "branch_metadata", None) is not None
        and payload.branch_metadata.terminal_status is not None
    }


def _branch_step_indexes(ledger: _RecordingLedger) -> set[int]:
    """Branch indices that drained a STEP entry (`terminal_status is None`) — a
    step entry claims the dispatch was scheduled, so a synthesized (never-
    dispatched) branch must NOT appear here."""
    return {
        payload.branch_metadata.branch_index
        for payload, _wk in ledger.appends
        if getattr(payload, "branch_metadata", None) is not None
        and payload.branch_metadata.terminal_status is None
    }


def test_proceed_warmup_phase1_deadline_strike_records_cancelled_for_withheld(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ML1 (M2, PROCEED): warm-up ON, branch[0] wedged past the barrier deadline
    in Phase 1 → PARTIAL; the never-released siblings drain obligation-4
    `cancelled` terminals (terminal-ONLY — a step entry would claim a dispatch
    that never fired; `timed_out` would claim an ambiguous in-flight effect);
    branch[0] records its own step + `timed_out`. The synthesis is LEDGER-only:
    the withheld siblings never reach the durable store (PROCEED writes no
    dispatch markers on any path — the load-bearing marker-absence assert is the
    strict-tier witness ML2)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 3
    release = threading.Event()
    dispatcher = _WedgeBranch0CohortDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    started = time.monotonic()
    try:
        result = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(StepDispatcher, dispatcher),
            ledger=ledger,
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
        )
    finally:
        release.set()
    elapsed = time.monotonic() - started
    assert result.status is RunStatus.PARTIAL
    # Phase 1 consumed the whole budget: the siblings were never released.
    assert dispatcher.dispatched == [0]
    assert _branch_terminals(ledger) == {0: "timed_out", 1: "cancelled", 2: "cancelled"}
    assert _branch_step_indexes(ledger) == {0}
    # LEDGER-only synthesis: branch[0]'s own in-flight `timed_out` capture is the
    # store's only record; the withheld siblings have none.
    assert store.present_branch_indexes(store.sole_run_key()) == {0}
    # Returned at ~the 0.2s deadline, not the 2.0s wedge (bounded-barrier guard).
    assert elapsed < 1.5


def test_pause_warmup_phase1_deadline_strike_failed_with_cancelled_terminals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ML2 (M2, PAUSE): the deadline-strike exit is terminal FAILED
    (`parallelization-barrier-deadline` — no clean pause boundary, nothing
    resumes it), so the scan RUNS: withheld siblings drain `cancelled` ledger
    terminals while their reserve-before-dispatch markers stay ABSENT in the
    store (marker-absence = provably-never-dispatched, CP spec v1.90 §25.17
    item 4 — the effect-set invariant is untouched by the synthesis)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 3
    release = threading.Event()
    dispatcher = _WedgeBranch0CohortDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    started = time.monotonic()
    try:
        result = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(StepDispatcher, dispatcher),
            ledger=ledger,
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
        )
    finally:
        release.set()
    elapsed = time.monotonic() - started
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-barrier-deadline"
    assert dispatcher.dispatched == [0]
    assert _branch_terminals(ledger) == {0: "timed_out", 1: "cancelled", 2: "cancelled"}
    assert _branch_step_indexes(ledger) == {0}
    # Strict tier: branch[0] wrote its dispatch marker + in-flight `timed_out`
    # capture; the withheld siblings wrote NEITHER (ledger-only synthesis).
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0}
    assert store.present_branch_indexes(store.sole_run_key()) == {0}
    assert elapsed < 1.5


def test_cascade_cancel_warmup_phase1_deadline_strike_cancelled_via_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ML3 (M2, CASCADE_CANCEL): the pre-existing obligation-4 scan (now the
    shared `_synthesize_undispatched_terminals`) already ran unconditionally on
    this tier BEFORE the deadline_struck check — regression pin that the helper
    refactor preserves it on the deadline path (FAILED
    `parallelization-cascade-cancel`)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 3
    release = threading.Event()
    dispatcher = _WedgeBranch0CohortDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    started = time.monotonic()
    try:
        result = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(StepDispatcher, dispatcher),
            ledger=ledger,
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
        )
    finally:
        release.set()
    elapsed = time.monotonic() - started
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-cascade-cancel"
    assert dispatcher.dispatched == [0]
    assert _branch_terminals(ledger) == {0: "timed_out", 1: "cancelled", 2: "cancelled"}
    assert _branch_step_indexes(ledger) == {0}
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0}
    assert elapsed < 1.5


def test_pause_warmup_branch0_failure_protocol_not_bound_records_cancelled() -> None:
    """ML4 (M2/C2, PAUSE): branch[0] FAILS in Phase 1 with NO pause/resume
    protocol bound → the detect-then-refuse terminal FAILED
    (`parallelization-pause-resume-protocol-not-bound`). No snapshot exists, so
    re-dispatchable-by-omission does not apply — the scan runs and the withheld
    siblings drain `cancelled` terminals (branch[0] itself is ran-and-errored →
    step + `completed` dispatch-boundary terminal)."""
    n = 3
    dispatcher = _RecordingCohortDispatcher(fail={0})
    ledger = _RecordingLedger()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=False,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-pause-resume-protocol-not-bound"
    assert dispatcher.dispatched == [0]
    assert _branch_terminals(ledger) == {0: "completed", 1: "cancelled", 2: "cancelled"}
    assert _branch_step_indexes(ledger) == {0}


def test_pause_warmup_branch0_failure_paused_siblings_zero_ledger_footprint() -> None:
    """ML5 (M2 negative control): the branch-failure → PAUSED boundary is
    RESUMABLE — snapshot OMISSION is the re-dispatchable contract (§25.15.1,
    CP spec v1.44 §1 as re-scoped at v1.91) — so the scan does NOT run there:
    the withheld siblings leave ZERO ledger footprint on the paused attempt
    (their record is written by the resumed attempt that actually runs them)."""
    n = 3
    dispatcher = _RecordingCohortDispatcher(fail={0})
    ledger = _RecordingLedger()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
    )
    assert result.status is RunStatus.PAUSED
    assert dispatcher.dispatched == [0]
    assert _branch_terminals(ledger) == {0: "completed"}
    assert _branch_step_indexes(ledger) == {0}


def test_baseline_all_concurrent_deadline_strike_no_cancelled_synthesis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ML6 (M2 baseline no-op): gate=False (non-CohortKeyCapable dispatcher) →
    all-concurrent; every branch is IN-FLIGHT when the deadline cuts, so every
    branch records its own step + `timed_out` at its CancelledError handler and
    the absence-keyed scan synthesizes NOTHING (no `cancelled` anywhere) — the
    pre-M2 baseline ledger shape is byte-preserved."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 3
    release = threading.Event()
    dispatcher = _BlockingAllDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    started = time.monotonic()
    try:
        result = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(StepDispatcher, dispatcher),
            ledger=ledger,
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
        )
    finally:
        release.set()
    elapsed = time.monotonic() - started
    assert result.status is RunStatus.PARTIAL
    assert sorted(dispatcher.dispatched) == [0, 1, 2]
    assert _branch_terminals(ledger) == {0: "timed_out", 1: "timed_out", 2: "timed_out"}
    assert _branch_step_indexes(ledger) == {0, 1, 2}
    assert elapsed < 1.5


def test_stale_snapshot_double_resume_synthesized_cancelled_key_collides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ML7 (M2/C3 residual pin): synthesized ledger terminals are PER-ATTEMPT
    audit records, not resume authority. A resume attempt that deadline-strikes
    in Phase 1 drains a synthesized `cancelled` terminal for the withheld
    sibling; a second resume from the SAME (stale) snapshot still re-dispatches
    that sibling — re-dispatch keys on snapshot OMISSION, never on a ledger
    terminal read — and the sibling's REAL terminal composes the IDENTICAL
    idempotency key (deterministic over run-key × step_index × terminal-path),
    so at a real shared IS ledger the second append IDEMPOTENT-NOOPs and the
    first attempt's `cancelled` stands in the audit trail. Result fidelity is
    unaffected: the second resume itself is PARTIAL with the sibling's output
    folded (the C3 residual recorded at CP spec v1.91)."""
    from harness_cp import workflow_driver as wd

    n = 3
    # Run A: branch[0] fails under warm-up → PAUSED; snapshot omits siblings 1, 2.
    result_a = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, _RecordingCohortDispatcher(fail={0})),
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
    )
    assert result_a.status is RunStatus.PAUSED
    snapshot = result_a.pause_snapshot
    assert snapshot is not None

    # Resume attempt 1: the remaining cohort's NEW branch[0] (ordinal 1) wedges
    # past the deadline in Phase 1 → FAILED barrier-deadline; ordinal 2 is
    # withheld and drains a synthesized `cancelled` terminal.
    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    release = threading.Event()
    ledger_1 = _RecordingLedger()
    try:
        attempt_1 = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(
                StepDispatcher,
                _WedgeBranch0CohortDispatcher(
                    release=release, self_release_seconds=2.0, wedge_index=1
                ),
            ),
            ledger=ledger_1,
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.TEAM_BINDING,
            with_pause_protocol=True,
            pause_snapshot_input=snapshot,
        )
    finally:
        release.set()
    assert attempt_1.status is RunStatus.FAILED
    assert attempt_1.fail_class == "parallelization-barrier-deadline"
    assert _branch_terminals(ledger_1)[2] == "cancelled"
    # Restore the production deadline for attempt 2 (no wedge remains).
    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 300.0)

    # Resume attempt 2 from the SAME stale snapshot: both siblings re-dispatch
    # (omission-keyed) and complete → PARTIAL (branch[0] is the degraded
    # non-contributor from run A).
    resume_dispatcher = _RecordingCohortDispatcher()
    ledger_2 = _RecordingLedger()
    attempt_2 = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, resume_dispatcher),
        ledger=ledger_2,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    assert attempt_2.status is RunStatus.PARTIAL
    assert sorted(resume_dispatcher.dispatched) == [1, 2]
    assert _branch_terminals(ledger_2)[2] == "completed"

    def _terminal_key(ledger: _RecordingLedger, branch_index: int) -> str:
        keys = {
            str(payload.idempotency_key)
            for payload, _wk in ledger.appends
            if getattr(payload, "branch_metadata", None) is not None
            and payload.branch_metadata.branch_index == branch_index
            and payload.branch_metadata.terminal_status is not None
        }
        assert len(keys) == 1, f"expected one terminal for branch {branch_index}, got {keys}"
        return next(iter(keys))

    # The collision: the synthesized `cancelled` (attempt 1) and the real
    # `completed` (attempt 2) compose the SAME idempotency key — at one shared
    # real ledger the second is an IDEMPOTENT_NOOP and `cancelled` stands.
    assert _terminal_key(ledger_1, 2) == _terminal_key(ledger_2, 2)

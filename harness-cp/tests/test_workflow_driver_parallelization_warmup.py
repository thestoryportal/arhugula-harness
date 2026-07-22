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

B-18-FENCE-LEDGER-FIDELITY section (CP spec v1.92;
`.harness/b18-fence-ledger-fidelity-design-decision-record.md` §6+§7) — the
obligation-4 scan's fence-family arms (aborted / fence-paused-union / cancelled)
plus the fifth scan call site at the fence-ABORT terminal exit:

  FL1 (+ FL2 recovered-withheld peer + FL7 arm ordering) — ABORT exit under
  warm-up on a resume round: aborted branch `completed` terminal-ONLY / no
  capture; withheld recovered peer `completed` / no capture; steps_executed = 0:
    → test_fence_ledger_abort_exit_aborted_and_recovered_completed_no_capture
  FL3 PAUSE deadline-strike on a resume round: withheld recovered fence peer
  `completed` (NOT `cancelled`), no capture; plain withheld sibling `cancelled`:
    → test_fence_ledger_pause_deadline_recovered_peer_completed_not_cancelled
  FL3b same union arm at the CASCADE_CANCEL post-barrier exit
  (persona-tier-change resume reach):
    → test_fence_ledger_cascade_cancel_exit_recovered_peer_completed_no_capture
  FL4 this-round INERT re-paused peer at the ABORT exit — inherited v1.91 arm
  (`completed` + store capture, the deliberate crash-visible addition):
    → test_fence_ledger_abort_exit_this_round_inert_repause_capture_present
  FL5 negative control — first-round deadline strike, no fence history → no
  `completed` synthesis anywhere:
    → test_fence_ledger_first_round_deadline_no_completed_synthesis
  FL6 negative control — ABORT_BRANCH ordinal at a scanned terminal exit records
  exactly ONE ledger terminal (the scoped-abort block's; no scan double-record):
    → test_fence_ledger_scoped_abort_single_terminal_no_scan_double_record
  FL8 containment — PAUSED boundary stays scan-free; a no-resolution recovered
  peer reappears in the new snapshot via the THIS-round dict, never a stale carry:
    → test_fence_ledger_paused_boundary_scan_free_peer_reappears_this_round

Authority: `.harness/u1-3c-prewarm-design-decision-record.md` +
`.harness/b18-3c-prewarm-cascade-ddr.md` (Fable-5 review-cleared);
ADR-D4 v1.1 §1.8; `Spec_Control_Plane_v1_86.md` §25.15; CP spec v1.90 §25.17;
CP spec v1.91 (M2 terminal-exit synthesis); CP spec v1.92 +
`.harness/b18-fence-ledger-fidelity-design-decision-record.md`
(B-18-FENCE-LEDGER-FIDELITY fence-family arms).
"""

from __future__ import annotations

import asyncio
import os
import threading
import time
from typing import Any, cast

import pytest
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
from harness_cp.pause_resume_protocol_types import (
    EffectFencePausedBranchResumeState,
    EffectFenceResolution,
    FanOutBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_dispatch_capacity_authority import DefaultCapacityAuthority
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
        resume_context_holder: Any = None,
        capacity_authority: Any = None,
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
        # B-18-FENCE-LEDGER-FIDELITY — the driver reads this via
        # `getattr(ctx, "resume_context_holder", None)`; None ≡ absent.
        self.resume_context_holder = resume_context_holder
        # B-48/U-CP-101 — injectable so a test can pin an explicit frame
        # budget for precise admission assertions. `None` → the strategy
        # falls back to the module-level default authority.
        self.capacity_authority = capacity_authority


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
    resume_context_holder: Any = None,
    emitter: _Emitter | None = None,
    capacity_authority: Any = None,
) -> Any:
    if ledger is None:
        ledger = _RecordingLedger()
    if emitter is None:
        emitter = _Emitter()
    ctx = cast(
        DriverContext,
        _Ctx(
            ledger=ledger,
            emitter=emitter,
            pause_resume_protocol=_protocol() if with_pause_protocol else None,
            engine_output_store=store,
            resume_context_holder=resume_context_holder,
            capacity_authority=capacity_authority,
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


class _CohortKeyRaisingDispatcher:
    """CohortKeyCapable dispatcher whose `cohort_key()` raises unconditionally
    — codex round-9 [P2] "whole-fan-out admission leaks on pre-dispatch setup
    failure": `_warmup_phase_split()`'s per-branch `dispatcher.cohort_key(...)`
    oracle call is one of the genuinely-reachable raise sites inside the
    pre-dispatch setup window B-48's admission is now deferred past."""

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        return {"branch": step.step_payload["index"]}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        raise RuntimeError("simulated cohort_key() oracle failure")


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
    """H3 regression: len(branch_plan) < 2 → the cohort partition short-circuits (no
    multi-member cohort) → _warmup_gate=False even with concurrent_cache_warmup=True.  Singleton branch
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
    no cohort forms → _warmup_gate=False → all-concurrent.
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
    dispatcher → no cohort forms → _warmup_gate=False →
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


def test_cascade_cancel_warmup_branch0_failure_releases_withheld_phase2_admissions() -> None:
    """B-48 (codex round-4 [P1] "release withheld warm-up admissions after
    Phase 1 fails"): `_admit_fanout_branch_plan` reserves frames for the
    WHOLE `branch_plan` (branches 0, 1, 2) upfront, but a Phase-1 failure
    (branch[0]) withholds Phase 2 (branches 1, 2) entirely — their
    `_cancel_branch` coroutines are never even CREATED (W2 above: no dispatch
    marker for them), so nothing else ever calls `release_unless_job_bound()`
    for their admissions. Without the fix, this permanently reduces the
    shared frame budget by the withheld branches' frame count on every
    Phase-1 failure."""
    n = 3
    authority = DefaultCapacityAuthority(frame_budget=4)
    dispatcher = _RecordingCohortDispatcher(fail={0})
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=dispatcher,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=_MiniFanoutStore(),
        capacity_authority=authority,
    )
    assert result.status is RunStatus.FAILED
    assert dispatcher.dispatched == [0]
    # All 3 branches' frames are back — including the 2 WITHHELD ones that
    # never reached `_cancel_branch` at all.
    assert authority.available == authority.frame_budget


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
    below uses _ReverseCompletionDispatcher (non-CohortKeyCapable) → the cohort partition
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


def test_proceed_warmup_phase1_deadline_strike_releases_withheld_phase2_admissions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-48 (codex round-4 [P1] "release admissions withheld by warm-up
    timeouts"): PROCEED-tier twin of
    `test_cascade_cancel_warmup_branch0_failure_releases_withheld_phase2_admissions`.
    Unlike the strict tier's TaskGroup (already fixed), `_proceed_fanout`'s
    Phase-1 gather is a SEPARATE, sequential `await` from Phase 2's — the
    outer `asyncio.timeout(deadline)` firing while Phase-1's gather is still
    running cancels it BEFORE Phase 2's own gather statement is ever reached,
    so `_warmup_phase2`'s upfront-reserved admissions never get a
    `_proceed_branch` call to release them (mutation probe: dropping the
    try/except around Phase-1's gather leaves `authority.available` short by
    the withheld branches' frames, permanently reducing the shared budget)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 3
    authority = DefaultCapacityAuthority(frame_budget=4)
    release = threading.Event()
    dispatcher = _WedgeBranch0CohortDispatcher(release=release, self_release_seconds=2.0)
    store = _MiniFanoutStore()
    try:
        result = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(StepDispatcher, dispatcher),
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
            capacity_authority=authority,
        )
    finally:
        release.set()
    assert result.status is RunStatus.PARTIAL
    assert dispatcher.dispatched == [0]
    # The 2 WITHHELD siblings' frames must be back by the time `_run` returns
    # (released synchronously inside `_proceed_fanout`'s except-block, before
    # `_run_fanout_to_completion` returns) — deterministic, race-free. Whether
    # branch[0]'s OWN frame has ALSO come back depends on how fast its wedged
    # worker thread unblocks after `release.set()` in `finally` above (a
    # separate, racy background completion), so this asserts the FIX's lower
    # bound rather than pinning an exact count: broken (leaked withheld
    # siblings) can only ever reach frame_budget - 2 (the pre-existing spare
    # + branch[0]'s eventual own release); fixed reaches frame_budget - 1
    # immediately and frame_budget once branch[0] also completes.
    assert authority.available >= authority.frame_budget - 1


def test_warmup_phase_split_cohort_key_failure_never_admits() -> None:
    """Codex round-9 [P2] "whole-fan-out admission leaks on pre-dispatch setup
    failure" — B-48's WHOLE-fan-out admission call is now DEFERRED to
    immediately before the `cascade_policy` split, i.e. AFTER `_warmup_phase_
    split()` runs (the split's own `dispatcher.cohort_key(...)` oracle call is
    unguarded and was one of the genuinely-reachable pre-dispatch raise sites
    inside the ~600-line setup window admission used to run BEFORE). A raise
    here must leave the capacity authority completely untouched — there was
    never anything to admit yet, let alone release.

    Mutation probe: moving `_admit_fanout_branch_plan` back to its pre-fix
    position (immediately after `branch_dispatchers` is resolved, BEFORE the
    warm-up split runs) would admit the fan-out's frames before this raise —
    `authority.available` would then read short of the full `frame_budget`
    (a genuine leak, since nothing downstream of the crash releases it),
    failing the assertion below.
    """
    authority = DefaultCapacityAuthority(frame_budget=4)
    with pytest.raises(RuntimeError, match="simulated cohort_key"):
        _run(
            steps=[_inference_step(0), _inference_step(1)],
            dispatcher=cast(StepDispatcher, _CohortKeyRaisingDispatcher()),
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
            capacity_authority=authority,
        )
    assert authority.available == authority.frame_budget == 4, (
        f"expected the frame budget completely untouched ({authority.available} "
        f"available of {authority.frame_budget}) — admission ran before the "
        f"warm-up cohort-key split failed"
    )


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
    original_deadline = wd._DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS
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
    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", original_deadline)

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


# ---------------------------------------------------------------------------
# B-18-FENCE-LEDGER-FIDELITY — fence-family arms of the obligation-4 scan +
# the fifth scan call site at the fence-ABORT terminal exit. Witnesses FL1-FL8
# per `.harness/b18-fence-ledger-fidelity-design-decision-record.md` §7
# (FL2 + FL7 folded into FL1 per the DDR's own folding notes); CP spec v1.92.
#
# The fence errors are NAME-MATCHED test-local stand-ins (harness-cp cannot
# import harness-runtime — the same pattern as
# test_workflow_driver_parallelization_pause.py); the hybrid dispatchers below
# are additionally CohortKeyCapable so the warm-up gate holds over INFERENCE
# branch plans (including the RESUME round's plan).
# ---------------------------------------------------------------------------


class EffectFenceAmbiguousUncommittedError(Exception):
    """Test-local stand-in for the runtime `effect_fence.EffectFenceAmbiguousUncommittedError`
    (C-RT-31 §14.22). The driver name-matches `type(exc).__name__`, so a same-named local
    class with the `idempotency_key` attribute is the faithful CP-side witness."""

    def __init__(self, *, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__(f"ambiguous (key={idempotency_key!r})")


class EffectFenceAbortedError(Exception):
    """Test-local stand-in for the runtime `effect_fence.EffectFenceAbortedError` — raised
    when the operator resolved an effect-fence pause with ABORT and the fence applies it."""


class _HolderWithResolutions:
    """Stand-in `ResumeContextHolder` — `peek()` returns a ResumeContext carrying a per-key
    `effect_fence_resolutions` map (NON-consuming, the production peek contract; the local
    twin of the pause-file fixture)."""

    def __init__(self, resolutions: dict[str, EffectFenceResolution]) -> None:
        self._rc = ResumeContext(effect_fence_resolutions=resolutions)
        self.peeked = 0

    def peek(self) -> ResumeContext:
        self.peeked += 1
        return self._rc


class _Branch0CleanSiblingsFenceCohortDispatcher:
    """Round-1 hybrid (CohortKeyCapable + fence-raising): branch[0] completes cleanly
    (the warm-up's serialized Phase 1); every sibling synchronizes on a barrier THEN
    raises the fence-ambiguous error with a per-branch key — so ALL siblings land in
    `effect_fence_paused_dispositions` deterministically (each is dispatched before any
    raise; whichever raise propagates first, the other lands via its own catch or the
    shielded in-flight `inflight.exception()` catch — both record the paused disposition)."""

    def __init__(self, *, sibling_parties: int) -> None:
        self._barrier = threading.Barrier(sibling_parties, timeout=10.0)
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
            return {"branch": 0}
        self._barrier.wait()
        raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-attempt1-{idx}")

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


class _FenceDirectiveReactorCohortDispatcher:
    """Resume-side hybrid (CohortKeyCapable): reacts to the threaded per-branch
    `EffectFenceResolutionDirective` the way the runtime fence would — indices in `fail`
    raise a PLAIN RuntimeError (an ordinary branch failure, checked FIRST); an ABORT
    directive raises the test-local `EffectFenceAbortedError`; a None directive (no/
    suppressed resolution) INERT re-pauses by re-raising the fence-ambiguous error with a
    THIS-ROUND key `{inert_key_prefix}{idx}` (so a re-pause snapshot's this-round-vs-stale
    provenance is checkable); SKIP_AS_FIRED / RE_FIRE fires (returns success). An optional
    `sync_barrier` makes N branches dispatch before any raises (deterministic composition)."""

    def __init__(
        self,
        *,
        fail: set[int] | None = None,
        sync_barrier: threading.Barrier | None = None,
        inert_key_prefix: str = "fence-key-inert-",
    ) -> None:
        self._fail = fail or set()
        self._barrier = sync_barrier
        self._inert_key_prefix = inert_key_prefix
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
        if self._barrier is not None:
            self._barrier.wait()
        if idx in self._fail:
            raise RuntimeError(f"simulated plain branch-{idx} failure")
        directive = getattr(step_context, "effect_fence_resolution", None)
        if directive is None:
            raise EffectFenceAmbiguousUncommittedError(
                idempotency_key=f"{self._inert_key_prefix}{idx}"
            )
        if directive.resolution is EffectFenceResolution.ABORT:
            raise EffectFenceAbortedError(f"operator aborted branch-{idx}")
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "test-cohort-uniform"


def _branch_terminal_statuses(ledger: _RecordingLedger, branch_index: int) -> list[str]:
    """EVERY drained terminal entry for one ordinal (order-preserving) — pins
    exactly-one-terminal claims (`== ["completed"]`), which `_branch_terminals`'
    dict shape (last-wins) cannot."""
    return [
        payload.branch_metadata.terminal_status
        for payload, _wk in ledger.appends
        if getattr(payload, "branch_metadata", None) is not None
        and payload.branch_metadata.branch_index == branch_index
        and payload.branch_metadata.terminal_status is not None
    ]


def _fence_pause_round1(store: _MiniFanoutStore) -> tuple[PauseSnapshot, dict[int, str]]:
    """Shared round 1 for FL1/FL4/FL6: TEAM_BINDING (PAUSE) + warm-up ON + protocol
    bound + durable store: branch[0] completes in Phase 1; branches 1..2 fence-pause
    in Phase 2 (barrier-synced). Returns the fence-pause snapshot + the per-branch
    reserve keys, after pinning the attempt-1 store state (markers for every
    dispatched branch; terminal capture ONLY for branch[0])."""
    n = 3
    dispatcher = _Branch0CleanSiblingsFenceCohortDispatcher(sibling_parties=2)
    paused = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, dispatcher),
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None
    peer = snapshot.peer_fan_out_resume
    assert peer is not None
    assert [(b.branch_index, b.terminal_status, b.output) for b in peer.branches] == [
        (0, "completed", {"branch": 0})
    ]
    key_by_index = {b.branch_index: b.idempotency_key for b in peer.effect_fence_paused_branches}
    assert key_by_index == {1: "fence-key-attempt1-1", 2: "fence-key-attempt1-2"}
    run_key = store.sole_run_key()
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2}
    assert store.present_branch_indexes(run_key) == {0}
    return snapshot, key_by_index


def test_fence_ledger_abort_exit_aborted_and_recovered_completed_no_capture() -> None:
    """FL1 (+ FL2 + FL7): the fence-ABORT terminal exit now runs the obligation-4
    scan (the fifth call site) BEFORE the unchanged `parallelization-effect-fence-
    aborted` FAILED return. Resume a 2-peer fence pause with {branch-1: ABORT} under
    warm-up: Phase 1 serializes ordinal 1 (the ABORT peer) whose re-dispatch raises
    the abort, collapsing Phase 1 — ordinal 2 (its directive suppressed by the
    run-level ABORT guard) is WITHHELD this round.

      Aborted branch-1 → ledger `completed` terminal-ONLY (no step entry) + NO store
      capture — and branch-1 is in BOTH `effect_fence_aborted_dispositions` AND
      `_recovered_effect_fence_paused`, so this also pins FL7 arm ORDERING (the
      aborted arm fires first; never the fence-arm capture).
      Withheld recovered peer branch-2 → ledger `completed` (the union arm; FL2) with
      NO store capture (attempt-1 store state byte-unchanged: marker-only).
      steps_executed = 0 — the terminal-only synthesis never inflates the
      step-count drain predicate (one STEP_BOUNDARY per branch that ran a step)."""
    n = 3
    store = _MiniFanoutStore()
    snapshot, key_by_index = _fence_pause_round1(store)
    run_key = store.sole_run_key()

    holder = _HolderWithResolutions({key_by_index[1]: EffectFenceResolution.ABORT})
    resume_dispatcher = _FenceDirectiveReactorCohortDispatcher()
    ledger = _RecordingLedger()
    emitter = _Emitter()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, resume_dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
        resume_context_holder=holder,
        emitter=emitter,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-effect-fence-aborted"
    assert result.pause_snapshot is None  # terminal — NOT a re-pause
    # Phase 1 = ordinal 1 (the ABORT peer); its abort collapsed Phase 1, so ordinal 2
    # was withheld — never dispatched this round.
    assert resume_dispatcher.dispatched == [1]
    # Ledger: aborted arm (branch-1) + recovered union arm (branch-2), both `completed`,
    # both terminal-ONLY — exactly one terminal each, zero step entries this round.
    assert _branch_terminals(ledger) == {1: "completed", 2: "completed"}
    assert _branch_terminal_statuses(ledger, 1) == ["completed"]
    assert _branch_terminal_statuses(ledger, 2) == ["completed"]
    assert _branch_step_indexes(ledger) == set()
    # Store: byte-unchanged from attempt-1 terminals — NO capture for branch-1 (FL7:
    # the aborted arm, never the fence-arm capture) NOR branch-2 (FL2: capture-less
    # recovered arm); dispatch markers stay the attempt-1 set (branch-1 re-marked).
    assert store.present_branch_indexes(run_key) == {0}
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2}
    assert store.read_branch_records(run_key)[0][1:] == ("completed", {"branch": 0})
    # steps_executed == branches that ran a step this round == 0 (DDR review finding 4):
    # the driver emits one STEP_BOUNDARY per branch that buffered a STEP entry.
    assert emitter.emits.count(WorkflowEventClass.STEP_BOUNDARY) == 0


def test_fence_ledger_pause_deadline_recovered_peer_completed_not_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FL3: ML2's shape (PAUSE tier, Phase-1 deadline strike) on a RESUME round seeded
    from a fence-pause snapshot — the withheld RECOVERED fence peer (no resolution
    supplied; holder absent) synthesizes `completed` via the union arm, NOT the false
    `cancelled` (whose obligation-4 meaning — "no effectful dispatch" — would
    contradict the peer's attempt-1 reserve); the plain withheld sibling still
    synthesizes `cancelled`; NO new store capture for the recovered peer."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 4
    # Hash-valid captured snapshot: branch 0 terminal `completed`; branch 2 a RECOVERED
    # fence peer (attempt-1 reserve key); branches 1 + 3 omitted → re-dispatchable.
    snapshot = _captured_peer_snapshot(
        peer=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="inf-0",
                    terminal_status="completed",
                    output={"branch": 0},
                ),
            ),
            branch_count=n,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=2,
                    step_id="inf-2",
                    step_kind="inference-step",
                    idempotency_key="fence-key-attempt1-2",
                ),
            ),
        )
    )
    release = threading.Event()
    # The resume plan is [1, 2, 3]; its NEW "branch[0]" is ordinal 1 — wedge it past
    # the deadline so ordinals 2 (recovered fence peer) + 3 (plain) are withheld.
    dispatcher = _WedgeBranch0CohortDispatcher(
        release=release, self_release_seconds=2.0, wedge_index=1
    )
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
            with_pause_protocol=True,
            pause_snapshot_input=snapshot,
        )
    finally:
        release.set()
    elapsed = time.monotonic() - started
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-barrier-deadline"
    assert dispatcher.dispatched == [1]
    # Recovered fence peer 2 → `completed` (NOT `cancelled`); plain sibling 3 →
    # `cancelled`; the wedged ordinal 1 records its own in-flight `timed_out`.
    assert _branch_terminals(ledger) == {1: "timed_out", 2: "completed", 3: "cancelled"}
    assert _branch_terminal_statuses(ledger, 2) == ["completed"]
    assert _branch_step_indexes(ledger) == {1}
    # Store: the ONLY write this round is the wedged ordinal's own marker + `timed_out`
    # capture — no new capture for the recovered peer (capture-less union arm).
    run_key = store.sole_run_key()
    assert store.present_branch_indexes(run_key) == {1}
    assert store.present_dispatched_indexes(run_key) == {1}
    assert elapsed < 1.5


def test_fence_ledger_cascade_cancel_exit_recovered_peer_completed_no_capture() -> None:
    """FL3b: the same union-arm output at the CASCADE_CANCEL post-barrier scan site —
    reached via the committed persona-tier-change resume path (capture on TEAM_BINDING
    → PAUSE; resume under MULTI_TENANT_COMPLIANCE → CASCADE_CANCEL, which has no
    strict-tier fence-resume rejection, only PROCEED does). A Phase-1 PLAIN branch
    failure withholds the recovered fence peer + the plain sibling; the run fails with
    the cascade fail_class this path actually produces
    (`parallelization-cascade-cancel` — the branch-failure route, asserted exactly)."""
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
            ),
            branch_count=n,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=2,
                    step_id="inf-2",
                    step_kind="inference-step",
                    idempotency_key="fence-key-attempt1-2",
                ),
            ),
        )
    )
    # Resume plan [1, 2, 3]; warm-up Phase 1 = ordinal 1 fails PLAIN → ordinals 2
    # (recovered fence peer, no resolution) + 3 (plain) withheld.
    dispatcher = _RecordingCohortDispatcher(fail={1})
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-cascade-cancel"
    assert dispatcher.dispatched == [1]
    # Union arm at the :8004-family exit: recovered peer 2 → `completed`; plain
    # withheld 3 → `cancelled`; ordinal 1 ran-and-errored → its own step + `completed`.
    assert _branch_terminals(ledger) == {1: "completed", 2: "completed", 3: "cancelled"}
    assert _branch_terminal_statuses(ledger, 2) == ["completed"]
    assert _branch_step_indexes(ledger) == {1}
    # No capture for the recovered peer — the only store terminal this round is the
    # ran-and-errored ordinal 1's own `completed`/no-output capture.
    run_key = store.sole_run_key()
    assert store.present_branch_indexes(run_key) == {1}
    assert store.read_branch_records(run_key)[1][1:] == ("completed", None)
    assert store.present_dispatched_indexes(run_key) == {1}


def test_fence_ledger_abort_exit_this_round_inert_repause_capture_present() -> None:
    """FL4: a THIS-round INERT re-paused peer at the fence-ABORT exit keeps the
    inherited v1.91 fence-arm treatment — ledger `completed` AND the store capture
    (`completed`/no-output) — the deliberate crash-visible addition named at DDR §6 Q2
    / review finding 1 (v1.65 §1(c) reproduce-the-terminal trade at the new exit).
    Warm-up OFF so BOTH peers re-dispatch concurrently (barrier-synced): branch-1's
    ABORT directive aborts; branch-2's SKIP_AS_FIRED is suppressed by the run-level
    ABORT guard → it re-dispatches and INERT re-pauses into the this-round dict."""
    n = 3
    store = _MiniFanoutStore()
    snapshot, key_by_index = _fence_pause_round1(store)
    run_key = store.sole_run_key()

    holder = _HolderWithResolutions(
        {
            key_by_index[1]: EffectFenceResolution.ABORT,
            key_by_index[2]: EffectFenceResolution.SKIP_AS_FIRED,
        }
    )
    resume_dispatcher = _FenceDirectiveReactorCohortDispatcher(
        sync_barrier=threading.Barrier(2, timeout=10.0)
    )
    ledger = _RecordingLedger()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, resume_dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=False,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
        resume_context_holder=holder,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-effect-fence-aborted"
    assert result.pause_snapshot is None
    # BOTH peers re-dispatched this round (all-concurrent, barrier-synced).
    assert sorted(resume_dispatcher.dispatched) == [1, 2]
    # Aborted branch-1 → terminal-only `completed`; INERT re-paused branch-2 → the
    # inherited fence arm: `completed` in the ledger AND the store capture.
    assert _branch_terminals(ledger) == {1: "completed", 2: "completed"}
    assert _branch_terminal_statuses(ledger, 1) == ["completed"]
    assert _branch_terminal_statuses(ledger, 2) == ["completed"]
    assert _branch_step_indexes(ledger) == set()
    # Store: branch-2's fence-arm capture IS present (`completed`/no-output — the
    # crash-visible addition this witness pins); branch-1 has NO capture.
    assert store.present_branch_indexes(run_key) == {0, 2}
    assert store.read_branch_records(run_key)[2][1:] == ("completed", None)
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2}


def test_fence_ledger_first_round_deadline_no_completed_synthesis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FL5 (negative control): a FIRST-round (non-resume) warm-up Phase-1 deadline
    strike has no fence history — the recovered dict is empty — so the scan
    synthesizes ONLY `cancelled` for the withheld siblings and NO `completed`
    appears anywhere (the ML1/ML2 baseline byte-preserved under the union arm)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    n = 3
    release = threading.Event()
    dispatcher = _WedgeBranch0CohortDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    try:
        result = _run(
            steps=[_inference_step(i) for i in range(n)],
            dispatcher=cast(StepDispatcher, dispatcher),
            ledger=ledger,
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.TEAM_BINDING,
        )
    finally:
        release.set()
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-barrier-deadline"
    assert dispatcher.dispatched == [0]
    assert _branch_terminals(ledger) == {0: "timed_out", 1: "cancelled", 2: "cancelled"}
    # The explicit FL5 pin: NO `completed` synthesis with an empty recovered dict.
    assert "completed" not in set(_branch_terminals(ledger).values())
    assert _branch_step_indexes(ledger) == {0}


def test_fence_ledger_scoped_abort_single_terminal_no_scan_double_record() -> None:
    """FL6 (negative control): an ABORT_BRANCH ordinal at a SCANNED terminal exit
    records exactly ONE ledger terminal — the scoped-abort block's `completed` — the
    scan never double-records it (a scoped-abort ordinal is excluded from
    `branch_plan`, which is all the scan iterates). Resumed under
    MULTI_TENANT_COMPLIANCE so the CASCADE_CANCEL post-barrier exit (which always
    scans) is the terminal exit; the vouched-for RE_FIRE sibling fires cleanly and
    the run fails with the scoped-abort fail_class."""
    n = 3
    store = _MiniFanoutStore()
    snapshot, key_by_index = _fence_pause_round1(store)
    run_key = store.sole_run_key()

    holder = _HolderWithResolutions(
        {
            key_by_index[1]: EffectFenceResolution.ABORT_BRANCH,
            key_by_index[2]: EffectFenceResolution.RE_FIRE,
        }
    )
    resume_dispatcher = _FenceDirectiveReactorCohortDispatcher()
    ledger = _RecordingLedger()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, resume_dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
        resume_context_holder=holder,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-effect-fence-branch-aborted"
    # The scoped-abort ordinal was NEVER re-dispatched; only the RE_FIRE sibling ran.
    assert resume_dispatcher.dispatched == [2]
    # Exactly ONE ledger terminal for the scoped-abort ordinal (the recording block's
    # `completed`) — the scan did not synthesize a second one.
    assert _branch_terminal_statuses(ledger, 1) == ["completed"]
    assert _branch_terminals(ledger) == {1: "completed", 2: "completed"}
    assert _branch_step_indexes(ledger) == {2}
    # Store: the distinguishing value lives in the runtime store (`scoped_aborted`,
    # the F1 split), NOT a second ledger terminal; the RE_FIRE sibling captured its
    # clean `completed` with output.
    assert store.read_branch_records(run_key)[1][1:] == ("scoped_aborted", None)
    assert store.read_branch_records(run_key)[2][1:] == ("completed", {"branch": 2})
    assert store.present_branch_indexes(run_key) == {0, 1, 2}


def test_fence_ledger_paused_boundary_scan_free_peer_reappears_this_round() -> None:
    """FL8 (containment): the branch-failure → PAUSED boundary stays SCAN-FREE. On a
    resume round where the recovered fence peer gets NO resolution (holder absent)
    and a PLAIN sibling failure triggers the PAUSE path (protocol bound), the run
    re-PAUSES with ZERO synthesized terminals for the recovered peer, and the NEW
    snapshot's `effect_fence_paused_branches` carries the peer via the THIS-round
    paused dict — proven by the re-raise key (`fence-key-round2-1` ≠ the attempt-1
    key), distinguishing a genuine re-dispatch-re-pause from a stale carry."""
    n = 3
    snapshot = _captured_peer_snapshot(
        peer=PeerFanOutResumeState(
            branches=(
                FanOutBranchResumeState(
                    branch_index=0,
                    step_id="inf-0",
                    terminal_status="completed",
                    output={"branch": 0},
                ),
            ),
            branch_count=n,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=1,
                    step_id="inf-1",
                    step_kind="inference-step",
                    idempotency_key="fence-key-attempt1-1",
                ),
            ),
        )
    )
    # Warm-up OFF + barrier(2): the recovered peer (1, directive None → INERT
    # re-pause with a round-2 key) and the plain sibling (2, RuntimeError) BOTH
    # dispatch before either raises.
    resume_dispatcher = _FenceDirectiveReactorCohortDispatcher(
        fail={2},
        sync_barrier=threading.Barrier(2, timeout=10.0),
        inert_key_prefix="fence-key-round2-",
    )
    ledger = _RecordingLedger()
    result = _run(
        steps=[_inference_step(i) for i in range(n)],
        dispatcher=cast(StepDispatcher, resume_dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=False,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )

    assert result.status is RunStatus.PAUSED
    assert result.fail_class is None
    assert sorted(resume_dispatcher.dispatched) == [1, 2]
    # ZERO synthesized terminals for the recovered peer this round (scan-free
    # boundary); the plain failed sibling records its own step + `completed`.
    assert _branch_terminal_statuses(ledger, 1) == []
    assert _branch_terminals(ledger) == {2: "completed"}
    assert _branch_step_indexes(ledger) == {2}
    # The NEW snapshot: terminal branches union {recovered 0, this-round 2}; the
    # unresolved peer reappears ONLY via the this-round dict — the round-2 key.
    snap2 = result.pause_snapshot
    assert snap2 is not None
    assert snap2.pause_reason is WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS
    peer2 = snap2.peer_fan_out_resume
    assert peer2 is not None
    assert [(b.branch_index, b.terminal_status, b.output) for b in peer2.branches] == [
        (0, "completed", {"branch": 0}),
        (2, "completed", None),
    ]
    assert [
        (e.branch_index, e.step_id, e.step_kind, e.idempotency_key)
        for e in peer2.effect_fence_paused_branches
    ] == [(1, "inf-1", "inference-step", "fence-key-round2-1")]


# ---------------------------------------------------------------------------
# B-18-EPOCH-PARTITION — heterogeneous cohort partition (CP spec v1.95 §25.19;
# `.harness/b18-epoch-partition-design-decision-record.md` §5 witnesses EP1-EP9).
# The binary all-same-key predicate is superseded: branches group by
# (step_kind, cohort_key); Phase 1 = one LEADER per multi-member cohort + every
# non-beneficiary (None-key / non-capable / singleton) branch; Phase 2 = the
# followers. EP4 (all-distinct keys → all singleton → gate False → baseline) is
# the reshaped CK-3′ in test_cohort_key_capable.py.
# ---------------------------------------------------------------------------


def _cohort_step(index: int, cohort: str | None) -> WorkflowStep:
    """INFERENCE_STEP whose cohort membership rides the payload; `cohort=None`
    yields a None cohort_key (a non-beneficiary branch) under the fixtures below."""
    return WorkflowStep(
        step_id=StepID(f"inf-{index}"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"index": index, "cohort": cohort},
    )


class _PartitionOrderingWitness:
    """CohortKeyCapable dispatcher for the partition ordering witnesses.

    Leaders (the caller names them — the first ordinal of each multi-member
    cohort) sleep briefly then set THEIR cohort's event; every other branch
    records at entry whether its own cohort's leader event was already set
    (followers must see True under the partition; on the pre-partition
    all-concurrent path they enter while the leader still sleeps → False).
    `slow_leaders` extends a leader's sleep so cross-cohort Phase-1 barrier
    ordering is observable (EP6)."""

    def __init__(self, *, leaders: set[int], slow_leaders: set[int] | None = None) -> None:
        self._leaders = leaders
        self._slow_leaders = slow_leaders or set()
        self._events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self.dispatched: list[int] = []
        self.follower_leader_done_on_entry: dict[int, bool] = {}
        self.all_leaders_done_on_entry: dict[int, bool] = {}

    def _event(self, cohort: str) -> threading.Event:
        with self._lock:
            return self._events.setdefault(cohort, threading.Event())

    def _all_leader_events_set(self) -> bool:
        with self._lock:
            events = list(self._events.values())
        return bool(events) and all(event.is_set() for event in events)

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        cohort = step.step_payload["cohort"]
        with self._lock:
            self.dispatched.append(idx)
        if idx in self._leaders:
            time.sleep(0.1 if idx in self._slow_leaders else 0.02)
            self._event(str(cohort)).set()
        else:
            self.all_leaders_done_on_entry[idx] = self._all_leader_events_set()
            if cohort is not None:
                self.follower_leader_done_on_entry[idx] = self._event(str(cohort)).is_set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


def test_partition_proceed_two_cohorts_leaders_serialize_before_followers() -> None:
    """EP1 (PROCEED): cohorts A={0,1} / B={2,3} → Phase 1 = leaders {0,2}
    concurrent, Phase 2 = followers {1,3}. Each follower must see ITS cohort
    leader completed at entry (per-cohort cache-write-before-cache-hit). Fails
    on the pre-partition binary gate (non-uniform keys → all-concurrent →
    followers enter while the leaders still sleep)."""
    witness = _PartitionOrderingWitness(leaders={0, 2})
    result = _run(
        steps=[
            _cohort_step(0, "A"),
            _cohort_step(1, "A"),
            _cohort_step(2, "B"),
            _cohort_step(3, "B"),
        ],
        dispatcher=cast(StepDispatcher, witness),
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [0, 1, 2, 3]
    assert witness.follower_leader_done_on_entry.get(1) is True, (
        f"follower 1 started before cohort-A leader completed ({witness.follower_leader_done_on_entry})"
    )
    assert witness.follower_leader_done_on_entry.get(3) is True, (
        f"follower 3 started before cohort-B leader completed ({witness.follower_leader_done_on_entry})"
    )


@pytest.mark.parametrize(
    "persona_tier",
    [PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE],
    ids=["pause-tier", "cascade-cancel-tier"],
)
def test_partition_strict_tiers_two_cohorts_leaders_serialize_before_followers(
    persona_tier: PersonaTier,
) -> None:
    """EP2 (strict tiers): the same two-cohort partition ordering through
    `_cancel_fanout`'s Phase-1 TaskGroup on BOTH strict tiers."""
    witness = _PartitionOrderingWitness(leaders={0, 2})
    result = _run(
        steps=[
            _cohort_step(0, "A"),
            _cohort_step(1, "A"),
            _cohort_step(2, "B"),
            _cohort_step(3, "B"),
        ],
        dispatcher=cast(StepDispatcher, witness),
        concurrent_cache_warmup=True,
        persona_tier=persona_tier,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [0, 1, 2, 3]
    assert witness.follower_leader_done_on_entry.get(1) is True
    assert witness.follower_leader_done_on_entry.get(3) is True


class _LeaderWaitsForNoneBranchDispatcher:
    """EP3 fixture: the cohort-A leader (index 0) BLOCKS until the None-key
    branch (index 2) completes. Passing therefore PROVES the None-key branch
    dispatched in Phase 1 alongside the leader (D2 non-beneficiary placement) —
    if it were withheld to Phase 2 the leader would wait out the 10 s guard and
    fail. Green on the pre-partition baseline too (all-concurrent): a
    deadlock-detector control, not a fails-on-main witness."""

    def __init__(self) -> None:
        self.none_branch_done = threading.Event()
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
            assert self.none_branch_done.wait(timeout=10.0), (
                "None-key branch never dispatched while the leader ran Phase 1 — "
                "non-beneficiary was withheld (D2 violation)"
            )
        if idx == 2:
            self.none_branch_done.set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


def test_partition_none_key_branch_dispatches_in_phase1() -> None:
    """EP3 (control): a None-key (non-beneficiary) branch keeps its baseline
    immediate dispatch — Phase 1 alongside the leaders, never delayed behind
    another cohort's cache-write (D2)."""
    dispatcher = _LeaderWaitsForNoneBranchDispatcher()
    result = _run(
        steps=[_cohort_step(0, "A"), _cohort_step(1, "A"), _cohort_step(2, None)],
        dispatcher=cast(StepDispatcher, dispatcher),
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(dispatcher.dispatched) == [0, 1, 2]


class _PartitionFailLeaderDispatcher:
    """CohortKeyCapable dispatcher over payload cohorts; indices in `fail` raise
    immediately; indices in `slow` sleep first (in-flight at a sibling failure →
    shielded completion)."""

    def __init__(self, *, fail: set[int], slow: set[int] | None = None) -> None:
        self._fail = fail
        self._slow = slow or set()
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
        if idx in self._slow:
            time.sleep(0.05)
        if idx in self._fail:
            raise RuntimeError(f"simulated leader-{idx} failure")
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


def test_partition_cascade_cancel_leader_failure_withholds_all_followers() -> None:
    """EP5 (strict tier): cohorts A={0,1} / B={2,3}; leader 0 fails fast in the
    Phase-1 TaskGroup while leader 2 is in-flight (slow → shielded completion).
    Followers {1,3} of BOTH cohorts are withheld: dispatch-marker ABSENCE (the
    v1.90 item-4 effect-set subset invariant under the partition) + obligation-4
    `cancelled` synthesis; the run FAILs cascade-cancel. Fails on the
    pre-partition gate (all four would dispatch concurrently)."""
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    dispatcher = _PartitionFailLeaderDispatcher(fail={0}, slow={2})
    result = _run(
        steps=[
            _cohort_step(0, "A"),
            _cohort_step(1, "A"),
            _cohort_step(2, "B"),
            _cohort_step(3, "B"),
        ],
        dispatcher=cast(StepDispatcher, dispatcher),
        ledger=ledger,
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "parallelization-cascade-cancel"
    # Phase 1 only: the failing leader + the in-flight leader; followers withheld.
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0, 2}
    # Leader 0 ran-and-errored → `completed`; leader 2 shielded to completion →
    # `completed`; withheld followers → scan `cancelled` (ledger-only).
    assert _branch_terminals(ledger) == {
        0: "completed",
        1: "cancelled",
        2: "completed",
        3: "cancelled",
    }
    assert _branch_step_indexes(ledger) == {0, 2}


def test_partition_proceed_leader_failure_still_releases_all_followers() -> None:
    """EP6 (PROCEED, H1 generalized): leader 0 (cohort A) fails fast; leader 2
    (cohort B) is SLOW (0.1 s). Phase 2 releases only after the WHOLE Phase-1
    gather returns, so every follower — including the failed cohort's — sees ALL
    leader events set at entry, and the failed leader still yields PARTIAL with
    everyone dispatched. Fails on the pre-partition gate (followers enter
    immediately → slow leader B not done)."""
    witness = _EP6FailLeaderOrderingWitness(fail={0}, leaders={0, 2}, slow_leaders={2})
    result = _run(
        steps=[
            _cohort_step(0, "A"),
            _cohort_step(1, "A"),
            _cohort_step(2, "B"),
            _cohort_step(3, "B"),
        ],
        dispatcher=cast(StepDispatcher, witness),
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.PARTIAL
    assert sorted(witness.dispatched) == [0, 1, 2, 3]
    # The Phase-1 barrier: both followers entered only after slow leader B set
    # its event (leader A failed — its event never sets; the assertion is on B).
    assert witness.leader_b_done_on_entry.get(1) is True
    assert witness.leader_b_done_on_entry.get(3) is True


class _EP6FailLeaderOrderingWitness:
    """EP6 fixture: leader 0 raises immediately (its cohort event never sets);
    leader 2 sleeps 0.1 s then sets cohort-B's event; followers record whether
    cohort-B's leader event was set at entry (the Phase-1 barrier witness that
    survives a failed leader)."""

    def __init__(self, *, fail: set[int], leaders: set[int], slow_leaders: set[int]) -> None:
        self._fail = fail
        self._leaders = leaders
        self._slow_leaders = slow_leaders
        self.leader_b_event = threading.Event()
        self._lock = threading.Lock()
        self.dispatched: list[int] = []
        self.leader_b_done_on_entry: dict[int, bool] = {}

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
            raise RuntimeError(f"simulated leader-{idx} failure")
        if idx in self._leaders:
            time.sleep(0.1 if idx in self._slow_leaders else 0.02)
            self.leader_b_event.set()
        else:
            self.leader_b_done_on_entry[idx] = self.leader_b_event.is_set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


class _WedgeLeaderPartitionDispatcher:
    """EP7 fixture: cohort-keyed variant of `_WedgeBranch0CohortDispatcher` —
    the wedged leader blocks past the (monkeypatched) deadline while the other
    cohort's leader completes clean."""

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
        if idx == 0:
            self._release.wait(timeout=self._self_release_seconds)
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


def test_partition_pause_deadline_strike_in_phase1_scan_covers_all_followers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EP7 (ML-family generalized): heterogeneous Phase 1 — leader 0 (cohort A)
    wedges past the deadline, leader 2 (cohort B) completes clean. The strike
    lands the PAUSE-tier terminal FAILED barrier-deadline exit; the obligation-4
    scan records `cancelled` for the withheld followers of BOTH cohorts,
    marker-absent; the cut leader records `timed_out`, the clean leader
    `completed`."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    release = threading.Event()
    dispatcher = _WedgeLeaderPartitionDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    store = _MiniFanoutStore()
    started = time.monotonic()
    try:
        result = _run(
            steps=[
                _cohort_step(0, "A"),
                _cohort_step(1, "A"),
                _cohort_step(2, "B"),
                _cohort_step(3, "B"),
            ],
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
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert _branch_terminals(ledger) == {
        0: "timed_out",
        1: "cancelled",
        2: "completed",
        3: "cancelled",
    }
    assert _branch_step_indexes(ledger) == {0, 2}
    # Markers: both Phase-1 leaders wrote theirs; the withheld followers wrote
    # NEITHER marker nor store record (ledger-only synthesis).
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0, 2}
    assert elapsed < 1.5


def test_partition_partial_recovery_resume_repartitions_remainder() -> None:
    """EP8: a partial-recovery resume re-partitions the LIVE remainder. Snapshot
    carries terminals for ordinals 0 (cohort A) and 3 (cohort B); the live plan
    {1,2,4} re-groups as A={1,2} (NEW leader 1) + singleton B={4} → Phase 1 =
    {1,4}, Phase 2 = {2}: follower 2 must see the new cohort-A leader completed
    at entry. Fails on the pre-partition gate (non-uniform remainder →
    all-concurrent)."""
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
                    branch_index=3,
                    step_id="inf-3",
                    terminal_status="completed",
                    output={"branch": 3},
                ),
            ),
            branch_count=5,
        )
    )
    witness = _PartitionOrderingWitness(leaders={1})
    result = _run(
        steps=[
            _cohort_step(0, "A"),
            _cohort_step(1, "A"),
            _cohort_step(2, "A"),
            _cohort_step(3, "B"),
            _cohort_step(4, "B"),
        ],
        dispatcher=cast(StepDispatcher, witness),
        concurrent_cache_warmup=True,
        persona_tier=PersonaTier.TEAM_BINDING,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [1, 2, 4]
    assert witness.follower_leader_done_on_entry.get(2) is True, (
        "follower 2 started before the resumed cohort's NEW leader (=1) completed"
    )


class _SpontaneousCancelLeaderDispatcher:
    """EP9 fixture: the cohort-A leader raises SPONTANEOUS CancelledError from
    its own dispatch (the sub-agent naked-escape / watchdog-cut vehicle); the
    cohort-B leader is slow (in-flight while the group settles)."""

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
            raise asyncio.CancelledError()
        if idx == 2:
            time.sleep(0.05)
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


def test_partition_phase1_spontaneous_cancel_resurfaces_and_withholds_followers() -> None:
    """EP9 (the review-B2 pin): a Phase-1 leader raising SPONTANEOUS
    CancelledError is SWALLOWED by the TaskGroup (CPython: the group exits clean
    with task.cancelled()=True) — the mandatory post-group `task.result()`
    collection (§25.19 normative) resurfaces it, so the cancellation propagates
    (honored, exactly the pre-arc solo re-raise) and the followers are NEVER
    dispatched: marker ABSENCE for {1,3}, no Phase-2 release after the cut (the
    v1.90 item-4 effect-set subset invariant). A naive TaskGroup Phase 1 without
    the collection dispatches the followers AFTER the cut — this witness fails
    against that regression, and against the pre-partition gate (heterogeneous →
    all four dispatch)."""
    store = _MiniFanoutStore()
    dispatcher = _SpontaneousCancelLeaderDispatcher()
    with pytest.raises(asyncio.CancelledError):
        _run(
            steps=[
                _cohort_step(0, "A"),
                _cohort_step(1, "A"),
                _cohort_step(2, "B"),
                _cohort_step(3, "B"),
            ],
            dispatcher=cast(StepDispatcher, dispatcher),
            concurrent_cache_warmup=True,
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
        )
    # Phase 1 only ever dispatched; the swallowed cancel resurfaced BEFORE any
    # Phase-2 release (the in-flight cohort-B leader ran shielded to completion).
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0, 2}


class _MutualLeaderEntryWitness:
    """EP10 fixture: each leader waits for the OTHER leader's ENTRY before
    returning (mutual entry-wait). Passing therefore PROVES the two cohort
    leaders ran CONCURRENTLY in Phase 1 — a (hypothetical) leader-serializing
    Phase 1 would wedge each wait out to its 10 s guard and fail the run."""

    def __init__(self) -> None:
        self.entered: dict[int, threading.Event] = {0: threading.Event(), 2: threading.Event()}
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
        if idx in self.entered:
            self.entered[idx].set()
            other = 2 if idx == 0 else 0
            assert self.entered[other].wait(timeout=10.0), (
                f"leader {other} never entered while leader {idx} ran — "
                "Phase-1 leaders were serialized (cross-cohort concurrency violated)"
            )
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


def test_partition_proceed_leaders_run_concurrently_in_phase1() -> None:
    """EP10 (post-build review cosmetic 2): different cohorts' LEADERS dispatch
    CONCURRENTLY with each other in Phase 1 on PROCEED — the partition
    serializes leader→followers WITHIN a cohort, never leader→leader ACROSS
    cohorts (different prefixes share no cache line). Deadlock-detector control
    (green on the all-concurrent baseline too; fails against a hypothetical
    leader-serializing Phase 1)."""
    witness = _MutualLeaderEntryWitness()
    result = _run(
        steps=[
            _cohort_step(0, "A"),
            _cohort_step(1, "A"),
            _cohort_step(2, "B"),
            _cohort_step(3, "B"),
        ],
        dispatcher=cast(StepDispatcher, witness),
        concurrent_cache_warmup=True,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [0, 1, 2, 3]


# ---------------------------------------------------------------------------
# B-60 — cancellation fence at nonlinear-topology entry + phase boundaries.
# ---------------------------------------------------------------------------


class _TrippingCohortDispatcher(_RecordingCohortDispatcher):
    """Records dispatches; TRIPS the supplied token at the END of the given
    branch's dispatch (the branch itself completes cleanly — the ONLY thing
    that may stop later phases is the B-60 boundary consult)."""

    def __init__(self, token: Any, *, trip_on: int) -> None:
        super().__init__()
        self._token = token
        self._trip_on = trip_on

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        result = super().dispatch(binding, step, step_context=step_context)
        if int(step.step_payload["index"]) == self._trip_on:
            self._token.trip()
        return result


def test_b60_pre_tripped_fence_refuses_nonlinear_strategy_entry() -> None:
    """B-60 entry witness (+ the fence-signal TRANSIT witness through the
    real `execute_workflow` boundary): an ambient token already tripped when
    a PARALLELIZATION run reaches the strategy dispatch refuses BEFORE any
    branch is scheduled — zero dispatches, zero ledger appends, and the
    BaseException signal surfaces at the `execute_workflow` caller (no
    except-arm or task-group machinery absorbs it)."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )

    ledger = _RecordingLedger()
    dispatcher = _RecordingCohortDispatcher()
    token = DispatchCancelToken()
    token.trip()
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            _run(
                steps=[_inference_step(i) for i in range(3)],
                dispatcher=dispatcher,
                ledger=ledger,
                concurrent_cache_warmup=False,
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
    assert dispatcher.dispatched == []
    assert ledger.appends == []


def test_b60_phase1_trip_stops_phase2_scheduling_proceed_tier() -> None:
    """B-60 phase-boundary witness (PROCEED tier): a token tripping DURING
    Phase 1 (branch[0] completes, tripping at its end) stops Phase 2 from
    ever SCHEDULING — the siblings are never dispatched, the signal
    surfaces at the caller, and the withheld Phase-2 admissions are
    released (no permanent frame-budget reduction)."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )

    authority = DefaultCapacityAuthority(frame_budget=4)
    token = DispatchCancelToken()
    dispatcher = _TrippingCohortDispatcher(token, trip_on=0)
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            _run(
                steps=[_inference_step(i) for i in range(3)],
                dispatcher=dispatcher,
                concurrent_cache_warmup=True,
                capacity_authority=authority,
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
    # Phase 1 dispatched exactly branch[0]; Phase 2 never scheduled.
    assert dispatcher.dispatched == [0]
    # The withheld Phase-2 admissions were released on the boundary raise.
    assert authority.available == authority.frame_budget


def test_b60_phase1_trip_stops_phase2_scheduling_cascade_tier() -> None:
    """B-60 phase-boundary witness (strict/cascade tier — the TaskGroup
    warm-up path): same interleaving under MULTI_TENANT_COMPLIANCE; the
    boundary consult between the Phase-1 and Phase-2 TaskGroups refuses
    Phase 2 and releases its admissions."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )

    authority = DefaultCapacityAuthority(frame_budget=4)
    token = DispatchCancelToken()
    dispatcher = _TrippingCohortDispatcher(token, trip_on=0)
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            _run(
                steps=[_inference_step(i) for i in range(3)],
                dispatcher=dispatcher,
                concurrent_cache_warmup=True,
                persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
                engine_class=EngineClass.EVENT_SOURCED_REPLAY,
                store=_MiniFanoutStore(),
                capacity_authority=authority,
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
    assert dispatcher.dispatched == [0]
    assert authority.available == authority.frame_budget


def test_b60_intra_phase_trip_stops_sibling_marker_and_dispatch() -> None:
    """B-60 (codex round-3 on PR #1075, reproduced): INTRA-phase — a token
    tripping while an earlier sibling writes its dispatch marker must stop
    the LATER sibling's marker + dispatch from beginning (the per-branch
    consult inside the marker try). Deterministic: the store's marker write
    for branch 0 trips; branch 1's consult then refuses."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )

    token = DispatchCancelToken()

    class _TrippingMarkerStore(_MiniFanoutStore):
        def record_branch_dispatched(self, run_key: str, branch_index: int, *a: Any, **k: Any):
            result = super().record_branch_dispatched(run_key, branch_index, *a, **k)
            if branch_index == 0:
                token.trip()
            return result

    store = _TrippingMarkerStore()
    dispatcher = _RecordingCohortDispatcher()
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            _run(
                steps=[_inference_step(i) for i in range(2)],
                dispatcher=dispatcher,
                concurrent_cache_warmup=False,
                persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
                engine_class=EngineClass.EVENT_SOURCED_REPLAY,
                store=store,
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
    # Branch 0's marker landed (the trip rode it); its OWN dispatch was
    # refused by the POST-marker consult (codex round-8), and branch 1's
    # marker AND dispatch never began.
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0}
    assert dispatcher.dispatched == []


def test_b60_all_rejected_with_trip_terminates_at_fence_not_paused() -> None:
    """B-60 all-rejected+tripped terminal witness: every branch capacity-
    rejected AND the token tripped during reservation -> the run terminates
    at the fence with NO branch-failure/cancelled terminals folded. HONESTY
    NOTE (merge-gate round 1): this pins the OUTCOME jointly with the B-61
    drain fence, not the round-10 consult ORDER in isolation — empirically
    no single-site discriminator for the order exists (with a pause
    protocol bound, admission-rejection pauses PRE-branch for fix and
    mutation alike; without one, the drain fence backstops). The order is
    strictly-earlier, comment-documented at both sites, and registered as
    a forward residual."""
    from harness_core import SubAgentDispatchCapacityError
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )

    token = DispatchCancelToken()

    class _AllRejectingTrippingAuthority:
        """Duck-typed authority (DefaultCapacityAuthority is @final):
        rejects EVERY branch and trips the token during reservation."""

        frame_budget = 1
        available = 1

        def reserve_fanout(
            self,
            branch_requirements: tuple[int, ...],
            *,
            step_ids: tuple[str, ...],
            descent_chain: tuple[str, ...],
        ):
            token.trip()  # the trip lands during reservation
            return tuple(
                SubAgentDispatchCapacityError(
                    requested_frames=req,
                    available_capacity=0,
                    step_id=sid,
                    descent_chain=descent_chain,
                )
                for req, sid in zip(branch_requirements, step_ids, strict=True)
            )

    authority = _AllRejectingTrippingAuthority()
    dispatcher = _RecordingCohortDispatcher()
    ledger = _RecordingLedger()
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            _run(
                steps=[_inference_step(i) for i in range(2)],
                dispatcher=dispatcher,
                ledger=ledger,
                concurrent_cache_warmup=False,
                persona_tier=PersonaTier.TEAM_BINDING,  # pause tier
                capacity_authority=authority,
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
    # Fold-side discriminators: nothing dispatched, and NO branch-failure /
    # cancelled terminal was folded for the rejected branches (the run
    # terminated at the fence, not at the cascade fold).
    assert dispatcher.dispatched == []
    assert not any(
        p.branch_metadata is not None and p.branch_metadata.terminal_status is not None
        for p, _k in ledger.appends
    )

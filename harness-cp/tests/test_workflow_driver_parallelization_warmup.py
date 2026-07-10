"""B-18-3C-PREWARM — concurrent-prompt-cache warm-up for PARALLELIZATION strategy.

Tests the ADR-D4 §1.8 serialized branch[0] warm-up path added to `_execute_parallelization`
in `workflow_driver.py`.  All tests target the PROCEED cascade-policy path
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

Authority: `.harness/u1-3c-prewarm-design-decision-record.md` (Fable-5 review-cleared);
ADR-D4 v1.1 §1.8; `Spec_Control_Plane_v1_86.md` §25.15.
"""

from __future__ import annotations

import threading
import time
from typing import Any, cast

from harness_core import PersonaTier, StepID, WorkloadClass
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
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

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
) -> WorkflowManifestEntry:
    """PARALLELIZATION manifest.  Default: SOLO_DEVELOPER → PROCEED + warmup=True."""
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
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
    """Minimal fake DriverContext for PARALLELIZATION e2e."""

    def __init__(self, *, ledger: Any, emitter: _Emitter) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = __import__("asyncio").Event()
        self.pause_resume_protocol = None
        self.pause_requested_flag = __import__("asyncio").Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


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
) -> Any:
    if ledger is None:
        ledger = _RecordingLedger()
    emitter = _Emitter()
    ctx = cast(DriverContext, _Ctx(ledger=ledger, emitter=emitter))
    return execute_workflow(
        _manifest(concurrent_cache_warmup=concurrent_cache_warmup, persona_tier=persona_tier),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher, also_declarative=also_declarative),
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
    """M6: DECLARATIVE_STEP fails the uniform-INFERENCE_STEP predicate check →
    _warmup_gate=False → all-concurrent.  Verified via ReverseCompletionDispatcher
    (would deadlock on the serialized path)."""
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
    """M8: non-uniform extended-thinking across branches fails the predicate →
    _warmup_gate=False → all-concurrent.  Verified via ReverseCompletionDispatcher."""
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

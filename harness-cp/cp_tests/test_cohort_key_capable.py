"""B-18-3C-PREWARM-COHORTKEY — CP driver integration: the warm-up cohort gate.

Tests that the dispatcher-oracle predicate correctly gates the concurrent-cache-warmup
serialization path for `_execute_parallelization`.  These tests use the full
`execute_workflow` path (same infrastructure as `test_workflow_driver_parallelization_warmup.py`)
but focus on the COHORTKEY-specific branches:

  CK-1  Uniform non-None cohort keys → warmup fires (serialized branch[0] first).
  CK-2  CohortKeyCapable dispatcher returns None → warmup blocked (all-concurrent).
  CK-3′ ALL-DISTINCT cohort keys (every cohort singleton) → warmup blocked
        (all-concurrent).  Reshaped at B-18-EPOCH-PARTITION (CP spec v1.95 §25.19).

Authority: `.harness/class_2_fork_b18_cohortkey_fork_a_vs_b.md`;
`Spec_Control_Plane_v1_88.md` §25.15–§25.16; DDR §11.5.
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
# Shared fixtures (mirror warmup test module)
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


def _manifest(*, concurrent_cache_warmup: bool = True) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id="wf-cohortkey",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
        concurrent_cache_warmup=concurrent_cache_warmup,
    )


def _step(index: int, *, thinking: bool | None = None) -> WorkflowStep:
    payload: dict[str, Any] = {"index": index}
    if thinking is not None:
        payload["params"] = {"thinking": thinking}
    return WorkflowStep(
        step_id=StepID(f"inf-{index}"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload=payload,
    )


class _RecordingLedger:
    def __init__(self) -> None:
        from harness_is.state_ledger_entry_schema import Actor, ActorClass

        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-cohortkey")
        self.appends: list[Any] = []

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
    def emit(self, event_class: Any) -> None:
        pass


class _Ctx:
    def __init__(self, *, ledger: Any) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = __import__("asyncio").Event()
        self.pause_resume_protocol = None
        self.pause_requested_flag = __import__("asyncio").Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


class _InferenceRegistry:
    def __init__(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> Any:
        if step_kind is StepKind.INFERENCE_STEP:
            return self._dispatcher
        raise StepKindDispatcherNotBoundError(step_kind)


def _run(*, steps: list[WorkflowStep], dispatcher: Any) -> Any:
    ledger = _RecordingLedger()
    ctx = cast(DriverContext, _Ctx(ledger=ledger))
    registry = cast(StepDispatcherRegistry, _InferenceRegistry(dispatcher))
    return execute_workflow(
        _manifest(concurrent_cache_warmup=True),
        steps,
        run_id="run-cohortkey",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )


# ---------------------------------------------------------------------------
# CohortKeyCapable dispatcher stubs
# ---------------------------------------------------------------------------


class _UniformCohortDispatcher:
    """CohortKeyCapable — always returns the same key → warmup fires.

    CK-1: branch[0] sleeps briefly then sets the event; siblings check
    that the event is already set when they start (proves serialization).
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
        return "uniform-cohort"


class _NullCohortDispatcher:
    """CohortKeyCapable — returns None → warmup blocked.  CK-2.

    Uses ReverseCompletion ordering (block i waits for i+1 to complete first).
    Deadlocks on the serialized path; safe on all-concurrent.
    """

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
            assert self._events[higher].wait(timeout=10.0)
        self._events[idx].set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return None


class _NonUniformCohortDispatcher:
    """CohortKeyCapable — ALL-DISTINCT keys per branch → warmup blocked.  CK-3′.

    Same reverse-completion ordering as above to detect serialization via deadlock.
    Every branch gets its own key → every cohort is a singleton → no multi-member
    cohort → the B-18-EPOCH-PARTITION gate stays False (CP spec v1.95 §25.19).

    (CK-3's pre-partition premise — branch 0 "key-A", others "key-B", asserting
    non-uniform → all-concurrent — was SUPERSEDED by B-18-EPOCH-PARTITION: a
    multi-member cohort now warms even beside a differing branch. That behavior
    is pinned by the EP witnesses in test_workflow_driver_parallelization_warmup.py;
    this reshaped fixture pins the SURVIVING half of the old contract.)
    """

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
            assert self._events[higher].wait(timeout=10.0)
        self._events[idx].set()
        return {"branch": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        idx = step.step_payload.get("index", 0)
        return f"key-{idx}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_uniform_cohort_key_triggers_warmup() -> None:
    """CK-1: CohortKeyCapable dispatcher returning the same non-None key for all
    branches → one N-member cohort → gate True → warmup serialization fires."""
    n = 4
    witness = _UniformCohortDispatcher()
    result = _run(
        steps=[_step(i) for i in range(n)],
        dispatcher=witness,
    )
    assert result.status is RunStatus.SUCCESS
    assert witness.branch0_done.is_set(), "branch[0] never dispatched"
    for i in range(1, n):
        assert witness.sibling_b0_done_on_entry.get(i) is True, (
            f"branch[{i}] started before branch[0] completed"
        )


def test_none_cohort_key_no_warmup() -> None:
    """CK-2: CohortKeyCapable dispatcher that returns None → no cohort forms →
    gate False → no serialization → all-concurrent (reverse-completion proves this)."""
    n = 3
    dispatcher = _NullCohortDispatcher(n=n)
    result = _run(
        steps=[_step(i) for i in range(n)],
        dispatcher=dispatcher,
    )
    assert result.status is RunStatus.SUCCESS


def test_nonuniform_cohort_keys_no_warmup() -> None:
    """CK-3′ (reshaped at B-18-EPOCH-PARTITION, CP spec v1.95 §25.19): ALL-DISTINCT
    cohort keys → every cohort a singleton → no multi-member cohort → gate False →
    no serialization → all-concurrent. (The pre-partition CK-3 premise — any
    non-uniformity blocks warmup — is superseded; see the EP witnesses.)"""
    n = 3
    dispatcher = _NonUniformCohortDispatcher(n=n)
    result = _run(
        steps=[_step(i) for i in range(n)],
        dispatcher=dispatcher,
    )
    assert result.status is RunStatus.SUCCESS

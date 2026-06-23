"""Full-chain witness — driver → real registry → REAL PostJoinSynthesisStepDispatcher
→ final_state (R-FS-1 arc B-POSTJOIN-LLM-SYNTHESIS; CP spec v1.54 + runtime §14.24).

The genuine end-to-end seam the CP-side witnesses (mock dispatcher) + the runtime
unit witnesses (dispatcher called directly) + the bootstrap-binding tests each
leave half-proven (`[[full-chain-witness-not-half-proofs]]`): here `execute_workflow`
(the CP driver) carves the terminal synthesis step, runs the fan-out, looks the
synthesis dispatcher up in a registry, and invokes the **REAL**
`PostJoinSynthesisStepDispatcher` — whose output must reach `final_state` AND
whose inner must have seen the branch-index-ordered composed siblings. Deterministic
(the inner is a recording stub; no provider) — lives in harness-runtime because it
imports BOTH `execute_workflow` (harness-cp) AND the runtime dispatcher.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
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
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.post_join_synthesis_dispatch import (
    POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX,
    PostJoinSynthesisStepDispatcher,
)

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-postjoin-full-chain")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
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
        self.emits: list[Any] = []

    def emit(self, event_class: Any) -> None:
        self.emits.append(event_class)


class _Ctx:
    def __init__(self, *, ledger: Any, emitter: _Emitter) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = asyncio.Event()
        self.pause_resume_protocol = None
        self.pause_requested_flag = asyncio.Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


class _WorkerEcho:
    """The DECLARATIVE_STEP (worker) dispatcher — echoes a per-branch output."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        return {"worker": str(step.step_id), "echoed": dict(step.step_payload)}


class _RecordingInner:
    """The inner LLM dispatcher the REAL synthesis dispatcher wraps — records the
    composed step it is handed (so the test can prove the siblings were composed
    through the real dispatcher) + returns a fixed synthesized aggregate."""

    def __init__(self) -> None:
        self.composed_messages: Any = None

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> Mapping[str, Any]:
        self.composed_messages = list(step.step_payload["messages"])
        return {"synthesis": "full-chain-composed"}


class _Registry:
    def __init__(self, *, worker: StepDispatcher, synthesis: StepDispatcher) -> None:
        self._worker = worker
        self._synthesis = synthesis

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.DECLARATIVE_STEP:
            return self._worker
        if step_kind is StepKind.POST_JOIN_SYNTHESIS:
            return self._synthesis
        raise StepKindDispatcherNotBoundError(step_kind)


def _manifest() -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id="wf-postjoin-full-chain",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _worker(index: int) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"worker-{index}"),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"index": index},
    )


def _synthesis_step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("synthesis"),
        step_kind=StepKind.POST_JOIN_SYNTHESIS,
        step_payload={"messages": [{"role": "system", "content": "synthesize"}]},
    )


def test_post_join_synthesis_full_chain_driver_to_final_state() -> None:
    """`execute_workflow` (CP driver) carves the terminal synthesis, runs the
    fan-out, looks up POST_JOIN_SYNTHESIS in the registry, and invokes the REAL
    PostJoinSynthesisStepDispatcher — its output reaches `final_state`, and its
    inner saw the branch-index-ordered composed siblings. The whole seam, no proxy
    on the dispatcher (the inner LLM call is a recording stub for determinism)."""
    inner = _RecordingInner()
    real_synthesis_dispatcher = PostJoinSynthesisStepDispatcher(inner=cast(StepDispatcher, inner))
    registry = cast(
        StepDispatcherRegistry,
        _Registry(worker=_WorkerEcho(), synthesis=real_synthesis_dispatcher),
    )
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))

    result = execute_workflow(
        _manifest(),
        [_worker(0), _worker(1), _synthesis_step()],
        run_id="run-1",
        ctx=ctx,
        default_model_binding=ModelBinding(provider="anthropic", model="claude-haiku-4-5"),
        step_dispatchers=registry,
    )

    # The REAL synthesis dispatcher's output reached final_state THROUGH the driver.
    assert result.status is RunStatus.SUCCESS
    assert result.final_state == {"synthesis": "full-chain-composed"}
    # The REAL dispatcher composed the 2 branch-index-ordered siblings into the LLM
    # input (the inner saw them) — proving the carve→dispatch→compose chain end-to-end.
    sibling_msg = inner.composed_messages[-1]["content"]
    assert sibling_msg.startswith(POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX)
    assert '"branch_index": 0' in sibling_msg
    assert '"branch_index": 1' in sibling_msg
    assert "worker-0" in sibling_msg and "worker-1" in sibling_msg

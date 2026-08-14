"""`B-165` — the PRODUCTION-FEED link, driven through the real `execute_workflow`.

The runtime-side witness
(`harness-runtime/tests/test_b165_same_position_placement_identity_witness.py`) shows
what the HITL gate composer DOES with two same-position placements: it gates both and
composes ONE identity for both. That is only half a claim. The other half — does
production ever HAND the composer that shape? — cannot be settled there, and two
rounds of out-of-family review said so, correctly: that module manufactures the
per-step context itself, so it would stay green even if `workflow_driver` stopped
carrying `hitl_placements` or `pre_dispatch_escalation_basis` altogether.

This module closes exactly that gap and nothing else. It declares a REAL
`WorkflowManifestEntry` carrying two `PRE_ACTION` placements, runs the REAL
`execute_workflow` on a `PARALLELIZATION` topology, and captures the
`StepExecutionContext` production actually hands each branch's step dispatcher.

The assertion is on what arrives at the dispatcher:

* both same-position placements are present on `step_context.hitl_placements` — the
  production producer surface, not a test proxy; and
* `pre_dispatch_escalation_basis` is non-`None` on the same context.

Both fields are set by ONE `model_copy` update at the fan-out branch-composition site
(`workflow_driver.py:8589-8606`), which is why they arrive together and why removing
either one reds this test. That co-arrival is the whole production-feed claim: the
`B-71` token is derived from the basis, so a context carrying the basis AND a
duplicated placement pair is precisely the colliding input the runtime witness then
acts on.

**Scope, stated so it cannot be over-read.** This proves production COMPOSES and
DELIVERS the colliding shape when a manifest declares duplicate placements. It does
NOT claim any shipped workflow declares them today — no in-tree manifest does. `B-165`
is a reachable-by-construction bound, not an observed production incident, and the
Class 1 fork filing says so in the same words.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

from harness_core import PersonaTier, WorkloadClass
from harness_core.identity import StepID
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    execute_workflow,
)
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b165-production-feed")
_GATE = HITLPlacementKind.PRE_ACTION


def _manifest(placements: tuple[HITLPlacement, ...]) -> Any:
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

    return WorkflowManifestEntry(
        workflow_id="wf-b165-feed",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=placements,
        per_step_overrides={},
    )


def _peer_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("branch-0"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"prompt": "a"},
        ),
        WorkflowStep(
            step_id=StepID("branch-1"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"prompt": "b"},
        ),
    ]


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


def _pause_context_reader() -> tuple[StateSummary, str]:
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


class _CtxP:
    def __init__(self) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _RecordingLedger()
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = PauseResumeProtocol(
            state_ledger_writer=object(),
            state_ledger_reader=object(),
            pause_context_reader=_pause_context_reader,
        )
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


class _CapturingDispatcher:
    """Records the `step_context` production hands each branch, then succeeds.

    Succeeding (rather than raising a pause signal) keeps this test about the
    CARRIER — what production delivers — and leaves what the gate then does with it
    to the runtime-side witness. The two halves are deliberately not merged.
    """

    def __init__(self) -> None:
        self.contexts: list[Any] = []

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        self.contexts.append(step_context)
        return {"role": str(step.step_id)}


# mutation-probe: delete BOTH placement carriers in
# `workflow_driver._execute_parallelization` — `hitl_placements=manifest_entry.hitl_placements`
# on the `fanout_parent` construction (~line 8411) AND the
# `"hitl_placements": fold_step_hitl_placements(...)` entry in the branch-child
# `model_copy` (~line 8593). BOTH are required to red this test.
#
# The conjunction is not padding, and it took two failed probes to find: production
# delivers the declared tuple to every branch by TWO REDUNDANT routes — the parent seeds
# it and the child re-folds it from `manifest_entry` — so dropping either ALONE leaves
# the other delivering it and the mutation SURVIVES. An annotation naming just one line
# reads as rigorous and proves nothing. Recorded here because the redundancy is a fact
# about the driver worth knowing, not merely a fact about this test.
def test_production_delivers_both_same_position_placements_to_the_branch_context() -> None:
    """The production-feed half of `B-165`, through the REAL `execute_workflow`."""
    dispatcher = _CapturingDispatcher()
    manifest = _manifest((HITLPlacement(position=_GATE), HITLPlacement(position=_GATE)))

    execute_workflow(
        manifest,
        _peer_steps(),
        run_id="run-b165-feed",
        ctx=cast(DriverContext, _CtxP()),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )

    assert dispatcher.contexts, "the driver dispatched no branch at all"
    branch_contexts = [c for c in dispatcher.contexts if c is not None]
    assert branch_contexts, "no branch received a step_context"

    for ctx in branch_contexts:
        placements = tuple(getattr(ctx, "hitl_placements", ()))
        assert len(placements) == 2, (
            f"production must deliver BOTH declared placements; got {len(placements)}"
        )
        assert [p.position for p in placements] == [_GATE, _GATE]


# mutation-probe: delete `"pre_dispatch_escalation_basis": _branch_pre_dispatch_identity`
# from the SAME fan-out branch-child `model_copy` update (the ~line-8602 entry), so the
# B-71 basis never reaches the per-step context and no token can be minted.
def test_production_delivers_the_b71_basis_on_the_same_branch_context() -> None:
    """The basis and the placements arrive TOGETHER — one `model_copy`, one context.

    This is what makes the collision reachable rather than hypothetical: the same
    object that carries a duplicated placement pair also carries the material the
    `B-71` token is derived from, so both placements resolve the SAME token.
    """
    dispatcher = _CapturingDispatcher()
    manifest = _manifest((HITLPlacement(position=_GATE), HITLPlacement(position=_GATE)))

    execute_workflow(
        manifest,
        _peer_steps(),
        run_id="run-b165-feed",
        ctx=cast(DriverContext, _CtxP()),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )

    branch_contexts = [c for c in dispatcher.contexts if c is not None]
    assert branch_contexts, "no branch received a step_context"

    carrying_both = [
        c
        for c in branch_contexts
        if getattr(c, "pre_dispatch_escalation_basis", None) is not None
        and len(tuple(getattr(c, "hitl_placements", ()))) == 2
    ]
    assert carrying_both, (
        "no branch context carried BOTH the B-71 basis and the duplicated placement "
        "pair — without that co-arrival the collision would not be reachable"
    )

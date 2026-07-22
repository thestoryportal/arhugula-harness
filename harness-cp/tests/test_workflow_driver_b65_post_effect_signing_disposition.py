"""B-65 (CP spec v1.103 §25.15; RATIFIED fork
`.harness/class_2_fork_b65_post_effect_signing_carrier_cascade_disposition.md` §3/§4
option A) — a branch failing with the Runtime-owned post-effect audit-signing carrier
(`PostEffectAuditSigningError`: the paid effect COMPLETED; only the post-effect audit
signing failed) is TERMINAL-with-result under EVERY `cascade_policy`, across every
topology that dispatches effect-bearing steps into a `pause`/PARTIAL/FAILED conversion.

Witnesses per the fork §2: (a) no resumable PAUSED snapshot is minted for the carrier
branch; (b) the surfaced failure carries the `result_ref`; (c) no re-dispatch path can
re-fire the effect. Name-matched (`type(exc).__name__ == "PostEffectAuditSigningError"`)
because `harness-cp` cannot import the runtime carrier type — every dispatcher double
below raises a LOCAL exception class of that exact name, never the real runtime type.
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b65")
_PROCEED_TIER = PersonaTier.SOLO_DEVELOPER  # -> cascade_policy = proceed
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # -> cascade_policy = pause
_CASCADE_CANCEL_TIER = PersonaTier.MULTI_TENANT_COMPLIANCE  # -> cascade_policy = cascade-cancel
_ANCHOR = "0" * 64


class PostEffectAuditSigningError(Exception):
    """LOCAL test double of the runtime carrier — matched by NAME only (the fence
    reads `type(exc).__name__`), never imported from harness-runtime."""

    def __init__(self, message: str, *, result_ref: object) -> None:
        super().__init__(message)
        self.result_ref = result_ref


def _manifest(
    *,
    topology: TopologyPattern,
    persona_tier: PersonaTier,
    workflow_id: str = "wf-b65",
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _peer_steps(n: int) -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID(f"branch-{i}"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": i},
        )
        for i in range(n)
    ]


def _orchestrator_worker_steps(n_workers: int) -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("orchestrator"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
        *(
            WorkflowStep(
                step_id=StepID(f"worker-{i}"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={"index": i},
            )
            for i in range(n_workers)
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
        _ANCHOR,
    )


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


class _Ctx:
    """Driver context WITH a bound `pause_resume_protocol` (so the strict tiers can
    actually capture a snapshot, distinguishing 'the fence correctly never mints one
    for the carrier branch' from 'no protocol was bound anyway')."""

    def __init__(self, *, ledger: Any, emitter: _Emitter) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = _protocol()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is not StepKind.DECLARATIVE_STEP:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    return cast(StepDispatcherRegistry, _Registry(dispatcher))


class _GatedCarrierDispatcher:
    """branch/worker-0 completes cleanly and sets a gate; branch/worker-1 waits on
    that gate then raises the B-65 carrier — a deterministic all-terminal cascade
    (no not-yet-dispatched race), mirroring `_GatedFailDispatcher` in the sibling
    pause test file. Records every dispatched step_id (the re-dispatch witness)."""

    def __init__(self, *, victim: str, result_ref: object) -> None:
        self._gate = threading.Event()
        self._victim = victim
        self._result_ref = result_ref
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id != self._victim:
            self._gate.set()
            return {"role": step_id, "echoed": dict(step.step_payload)}
        assert self._gate.wait(timeout=10.0), "the sibling never completed"
        raise PostEffectAuditSigningError(
            f"post-effect signing failed at {step_id}", result_ref=self._result_ref
        )


def _run(
    *,
    manifest: WorkflowManifestEntry,
    steps: list[WorkflowStep],
    dispatcher: StepDispatcher,
    ctx: DriverContext,
    pause_snapshot_input: Any = None,
) -> Any:
    return execute_workflow(
        manifest,
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
        pause_snapshot_input=pause_snapshot_input,
    )


# ---------------------------------------------------------------------------
# PARALLELIZATION
# ---------------------------------------------------------------------------


def test_parallelization_proceed_folds_result_ref_never_votes() -> None:
    """PROCEED: branch-0 succeeds, branch-1 raises the carrier. The run is PARTIAL;
    `partial_state["post_effect_signing_failures"]` carries `result_ref` VERBATIM
    (a str here — the live-ref case); the carrier's step_id is absent from
    `branch_outputs`/`aggregate` (never enters the voting fold).

    Mutation probe: routing the carrier's output into `collected` instead of the
    separate channel would make `aggregate["aggregate"]` equal `{"result_ref": ...}`
    (a 1-vote tie with branch-0's real output) HALF the time depending on dict
    ordering/hash — this test pins the CORRECT, deterministic shape instead."""
    manifest = _manifest(topology=TopologyPattern.PARALLELIZATION, persona_tier=_PROCEED_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _GatedCarrierDispatcher(victim="branch-1", result_ref="ref-abc123")
    result = _run(manifest=manifest, steps=_peer_steps(2), dispatcher=dispatcher, ctx=ctx)

    assert result.status is RunStatus.PARTIAL
    assert result.pause_snapshot is None
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"branch-1": {"result_ref": "ref-abc123"}}
    assert "branch-1" not in partial["branch_outputs"]
    assert partial["aggregate"] == {"role": "branch-0", "echoed": {"index": 0}}


def test_parallelization_pause_never_mints_resumable_and_never_redispatches() -> None:
    """PAUSE: branch-0 succeeds, branch-1 raises the carrier. The run PAUSES (the
    surviving branch-0 genuinely paused, per CP spec: 'run-level status follows the
    policy for the REMAINING branches') but branch-1's carrier disposition NEVER
    re-fires on `api.resume` — witness (a)+(c). The resumed run's report still
    carries branch-1's `result_ref` — witness (b).

    Mutation probe: if the fence routed the carrier into `paused_child_branches`
    (or omitted `terminal_dispositions`) instead of the terminal-with-result path,
    `api.resume` would re-dispatch branch-1 a SECOND time — this test's dispatch-
    count assertion catches that at-most-once violation directly."""
    manifest = _manifest(topology=TopologyPattern.PARALLELIZATION, persona_tier=_PAUSE_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _GatedCarrierDispatcher(victim="branch-1", result_ref="ref-xyz789")
    result = _run(manifest=manifest, steps=_peer_steps(2), dispatcher=dispatcher, ctx=ctx)

    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    pr = snap.peer_fan_out_resume
    assert pr is not None
    by_index = {b.branch_index: b for b in pr.branches}
    # branch-1 (the carrier) is recorded terminal — never re-dispatchable.
    assert by_index[1].terminal_status == "completed"
    assert by_index[1].step_id == "branch-1"
    # witness (b): the run's OWN report (partial_state) carries the result_ref.
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"branch-1": {"result_ref": "ref-xyz789"}}

    # witness (a)+(c): resume never re-dispatches branch-1 — dispatched exactly once.
    resume_ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    resume_dispatcher = _GatedCarrierDispatcher(victim="branch-1", result_ref="ref-xyz789")
    _run(
        manifest=manifest,
        steps=_peer_steps(2),
        dispatcher=resume_dispatcher,
        ctx=resume_ctx,
        pause_snapshot_input=snap,
    )
    assert "branch-1" not in resume_dispatcher.dispatched


def test_parallelization_cascade_cancel_terminal_with_result() -> None:
    """CASCADE_CANCEL: branch-0 succeeds (shielded to completion), branch-1 raises
    the carrier — the run FAILS (cascade-cancel semantics), carrying branch-1's
    `result_ref` in the report rather than the plain no-aggregate FAILED shape."""
    manifest = _manifest(
        topology=TopologyPattern.PARALLELIZATION, persona_tier=_CASCADE_CANCEL_TIER
    )
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _GatedCarrierDispatcher(victim="branch-1", result_ref="ref-cc-1")
    result = _run(manifest=manifest, steps=_peer_steps(2), dispatcher=dispatcher, ctx=ctx)

    assert result.status is RunStatus.FAILED
    assert result.pause_snapshot is None
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"branch-1": {"result_ref": "ref-cc-1"}}


def test_parallelization_unresolvable_ref_discriminator_survives() -> None:
    """A store-unresolvable declaration (a dict-shaped `result_ref`, mirroring the
    Runtime `UnresolvableResultRef` union member) is carried as a structured dict —
    never collapsed into a bare string (CP spec v1.103 §25.15 row 6: 'never a lossy
    stringification')."""
    manifest = _manifest(topology=TopologyPattern.PARALLELIZATION, persona_tier=_PROCEED_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    unresolvable = {"result_ref": {"unresolvable_reason": "no protected result store configured"}}

    class _UnresolvableCarrierDispatcher:
        def __init__(self) -> None:
            self._gate = threading.Event()

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            step_id = str(step.step_id)
            if step_id == "branch-0":
                self._gate.set()
                return {"role": step_id}
            assert self._gate.wait(timeout=10.0)
            exc = PostEffectAuditSigningError(
                "signing failed, store also unresolvable", result_ref=None
            )
            # Simulate the ALREADY-encoded discriminated-dict shape a real
            # `UnresolvableResultRef` would produce through `_post_effect_signing_
            # result_ref_output` — attach it directly as the exception's `result_ref`
            # so the fence's `getattr(exc, "result_ref", None)` sees a non-str object.
            exc.result_ref = _UnresolvableRef("no protected result store configured")
            raise exc

    result = _run(
        manifest=manifest,
        steps=_peer_steps(2),
        dispatcher=cast(StepDispatcher, _UnresolvableCarrierDispatcher()),
        ctx=ctx,
    )
    assert result.status is RunStatus.PARTIAL
    assert result.partial_state["post_effect_signing_failures"] == {"branch-1": unresolvable}


class _UnresolvableRef:
    """Mirrors the shape of Runtime's `UnresolvableResultRef` (a `reason: str`
    attribute) WITHOUT importing it — `_post_effect_signing_result_ref_output` reads
    it via `getattr`, never `isinstance`, so any object with `.reason` round-trips."""

    def __init__(self, reason: str) -> None:
        self.reason = reason


# ---------------------------------------------------------------------------
# ORCHESTRATOR_WORKERS (also covers HIERARCHICAL_DELEGATION — a thin wrapper
# per `_execute_hierarchical_delegation`'s docstring: "reuses ORCHESTRATOR_WORKERS
# at each level, NOT a parallel re-implementation")
# ---------------------------------------------------------------------------


def test_orchestrator_workers_proceed_folds_result_ref_never_votes() -> None:
    """PROCEED: the orchestrator + worker-0 succeed, worker-1 raises the carrier.
    PARTIAL; the ref lands in `partial_state["post_effect_signing_failures"]`,
    never in `worker_outputs` (never enters the plain-merge fold)."""
    manifest = _manifest(topology=TopologyPattern.ORCHESTRATOR_WORKERS, persona_tier=_PROCEED_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _GatedCarrierDispatcher(victim="worker-1", result_ref="ow-ref-1")
    result = _run(
        manifest=manifest, steps=_orchestrator_worker_steps(2), dispatcher=dispatcher, ctx=ctx
    )

    assert result.status is RunStatus.PARTIAL
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"worker-1": {"result_ref": "ow-ref-1"}}
    assert "worker-1" not in partial["worker_outputs"]


def test_orchestrator_workers_pause_never_mints_resumable_and_never_redispatches() -> None:
    """PAUSE: worker-1 raises the carrier — never re-dispatched on `api.resume`
    (witness a+c); the run's report still carries its `result_ref` (witness b)."""
    manifest = _manifest(topology=TopologyPattern.ORCHESTRATOR_WORKERS, persona_tier=_PAUSE_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _GatedCarrierDispatcher(victim="worker-1", result_ref="ow-ref-2")
    result = _run(
        manifest=manifest, steps=_orchestrator_worker_steps(2), dispatcher=dispatcher, ctx=ctx
    )

    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    fr = snap.fan_out_resume
    assert fr is not None
    by_index = {b.branch_index: b for b in fr.branches}
    assert by_index[1].terminal_status == "completed"
    assert by_index[1].step_id == "worker-1"
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"worker-1": {"result_ref": "ow-ref-2"}}

    resume_ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    resume_dispatcher = _GatedCarrierDispatcher(victim="worker-1", result_ref="ow-ref-2")
    _run(
        manifest=manifest,
        steps=_orchestrator_worker_steps(2),
        dispatcher=resume_dispatcher,
        ctx=resume_ctx,
        pause_snapshot_input=snap,
    )
    assert "worker-1" not in resume_dispatcher.dispatched


def test_orchestrator_workers_cascade_cancel_terminal_with_result() -> None:
    """CASCADE_CANCEL: worker-1 raises the carrier — the run FAILS, carrying its
    `result_ref` (the fork's rider names cascade-cancel explicitly)."""
    manifest = _manifest(
        topology=TopologyPattern.ORCHESTRATOR_WORKERS, persona_tier=_CASCADE_CANCEL_TIER
    )
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _GatedCarrierDispatcher(victim="worker-1", result_ref="ow-ref-3")
    result = _run(
        manifest=manifest, steps=_orchestrator_worker_steps(2), dispatcher=dispatcher, ctx=ctx
    )

    assert result.status is RunStatus.FAILED
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"worker-1": {"result_ref": "ow-ref-3"}}


# ---------------------------------------------------------------------------
# EVALUATOR_OPTIMIZER — sequential generate/evaluate loop (no fan-out)
# ---------------------------------------------------------------------------


class _EOCarrierDispatcher:
    """Generate succeeds; evaluate raises the carrier on the FIRST iteration."""

    def __init__(self, *, result_ref: object) -> None:
        self._result_ref = result_ref
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "generate":
            return {"draft": "v1"}
        raise PostEffectAuditSigningError(
            "post-effect signing failed at evaluate", result_ref=self._result_ref
        )


def _eo_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("generate"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
        WorkflowStep(
            step_id=StepID("evaluate"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
    ]


def test_evaluator_optimizer_pause_never_pauses_always_terminal_with_result() -> None:
    """EO's cascade_policy=pause row EXTENDS to the sequential generate/evaluate
    loop — but the carrier must NEVER take that resumable branch (a resume would
    re-dispatch `evaluate`, re-firing the completed effect). FAILED, carrying
    `result_ref` in `partial_state` — unlike EO's ordinary pause-protocol-not-bound
    FAILED, which attests no aggregate at all.

    Mutation probe: deleting the `type(exc).__name__ == "PostEffectAuditSigningError"`
    guard would route this into the ordinary `cascade_policy is CascadePolicy.PAUSE`
    branch, returning `RunStatus.PAUSED` with a resumable snapshot instead — this
    test's `status is RunStatus.FAILED` assertion catches that directly."""
    manifest = _manifest(topology=TopologyPattern.EVALUATOR_OPTIMIZER, persona_tier=_PAUSE_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _EOCarrierDispatcher(result_ref="eo-ref-1")
    result = _run(manifest=manifest, steps=_eo_steps(), dispatcher=dispatcher, ctx=ctx)

    assert result.status is RunStatus.FAILED
    assert result.pause_snapshot is None
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"evaluate": {"result_ref": "eo-ref-1"}}


# ---------------------------------------------------------------------------
# DECENTRALIZED_HANDOFF — single-owner sequential stage chain
# ---------------------------------------------------------------------------


class _HandoffCarrierDispatcher:
    """stage-0 succeeds; stage-1 raises the carrier."""

    def __init__(self, *, result_ref: object) -> None:
        self._result_ref = result_ref
        self.dispatched: list[str] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        if step_id == "stage-0":
            return {"role": "stage-0"}
        raise PostEffectAuditSigningError(
            f"post-effect signing failed at {step_id}", result_ref=self._result_ref
        )


def _handoff_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("stage-0"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
        WorkflowStep(
            step_id=StepID("stage-1"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
        ),
    ]


def test_decentralized_handoff_pause_never_pauses_always_terminal_with_result() -> None:
    """DECENTRALIZED_HANDOFF's cascade_policy=pause row EXTENDS to the single-owner
    sequential chain — the carrier must NEVER take that resumable branch. FAILED,
    carrying `result_ref` in the salvaged aggregate (alongside the completed
    stage-0 prefix), never a resumable `HandoffResumeState`-bearing PAUSED."""
    manifest = _manifest(topology=TopologyPattern.DECENTRALIZED_HANDOFF, persona_tier=_PAUSE_TIER)
    ctx = cast(DriverContext, _Ctx(ledger=_RecordingLedger(), emitter=_Emitter()))
    dispatcher = _HandoffCarrierDispatcher(result_ref="dh-ref-1")
    result = _run(manifest=manifest, steps=_handoff_steps(), dispatcher=dispatcher, ctx=ctx)

    assert result.status is RunStatus.FAILED
    assert result.pause_snapshot is None
    partial = result.partial_state
    assert partial is not None
    assert partial["post_effect_signing_failures"] == {"stage-1": {"result_ref": "dh-ref-1"}}
    # the completed stage-0 prefix is still salvaged alongside the carrier's ref.
    assert partial["stages"] == {"stage-0": {"role": "stage-0"}}

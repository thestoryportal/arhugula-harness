"""B-70 impl leg — CP spec v1.107 §1.1 multi-branch effect-fence-resolution
fallback-safety invariant (the effect-fence analogue of `hitl_response_for`'s
uniform-fallback-safety rule, CP spec v1.106 §1.2 property 4).

`_resolve_effect_fence_gated`'s uniform `effect_fence_resolution` fallback is safe
only when exactly ONE effect-fence-pause location is paused-and-unaddressed this
resume cycle (across all THREE carriers: LINEAR `effect_fence_resume`, the
ORCHESTRATOR's own `orchestrator_effect_fence_resume`, and fan-out `effect_fence_
paused_branches` entries). With 2+ concurrently-paused unaddressed locations,
applying the uniform default to every one of them would misattribute a single
operator judgment (SKIP_AS_FIRED / RE_FIRE / ABORT / ABORT_BRANCH) to multiple
distinct held reserves. This module tests:

  1. `_collect_effect_fence_idempotency_keys` / `compute_effect_fence_uniform_
     fallback_eligible_key` (pure tree-walk over `PauseSnapshot`, across all three
     carriers) in isolation.
  2. `_resolve_effect_fence_gated` (the per-key gated resolver) in isolation.
  3. The LINEAR reconstruction site's actual consumption of the computed
     eligibility (`workflow_driver.py`'s `effect_fence_directive` construction,
     round-3-corrected to be map-addressable) via real pause/resume cycles.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import (
    EffectFenceResolution,
    EffectFenceResumeState,
    OrchestratorEffectFencePausedResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    _collect_effect_fence_idempotency_keys,
    _resolve_effect_fence_gated,
    compute_effect_fence_uniform_fallback_eligible_key,
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
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-effect-fence-uniform-fallback-b70")
_ANCHOR = "0" * 64
_WF = "wf-ef-p1"


class EffectFenceAmbiguousUncommittedError(Exception):
    """Local stand-in for the runtime exception the fence raises (name-matched by
    the driver — harness-cp cannot import harness-runtime). Mirrors
    `test_workflow_driver_effect_fence_pause.py`'s own local declaration."""

    def __init__(self, message: str = "", *, idempotency_key: str = "") -> None:
        self.idempotency_key = idempotency_key
        super().__init__(message or "effect-fence: ambiguous (no captured output)")


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _snapshot(
    *,
    run_id: str,
    pause_reason: WorkflowPauseReason = WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
    step_index: int = 0,
    effect_fence_resume: EffectFenceResumeState | None = None,
    orchestrator_effect_fence_resume: OrchestratorEffectFencePausedResumeState | None = None,
    peer_fan_out_resume: PeerFanOutResumeState | None = None,
) -> PauseSnapshot:
    """A minimal `PauseSnapshot` for the PURE tree-walk tests — `snapshot_hash` is a
    placeholder (never validated by `_collect_effect_fence_idempotency_keys` /
    `compute_effect_fence_uniform_fallback_eligible_key`, which read the object
    graph directly, not through `attempt_resume`'s hash-recompute gate)."""
    return PauseSnapshot(
        workflow_id=_WF,
        run_id=run_id,
        step_index=step_index,
        pause_reason=pause_reason,
        state_summary=_summary(),
        snapshot_hash="f" * 64,
        created_at=0,
        state_ledger_anchor=_ANCHOR,
        effect_fence_resume=effect_fence_resume,
        orchestrator_effect_fence_resume=orchestrator_effect_fence_resume,
        peer_fan_out_resume=peer_fan_out_resume,
    )


def _paused_child(
    *, branch_index: int, child_snapshot: PauseSnapshot
) -> PausedChildBranchResumeState:
    return PausedChildBranchResumeState(
        branch_index=branch_index,
        step_id=f"worker-{branch_index}",
        child_snapshot=child_snapshot,
    )


# ---------- pure tree-walk unit tests ----------------------------------------


def test_single_linear_pause_is_sole_eligible_key() -> None:
    """Byte-compat / simplest shape: a lone LINEAR effect-fence pause has no
    siblings — it is trivially the sole member of the unaddressed set."""
    root = _snapshot(
        run_id="run-solo",
        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-solo"),
    )
    assert _collect_effect_fence_idempotency_keys(root) == ["key-solo"]
    eligible = compute_effect_fence_uniform_fallback_eligible_key(root, ResumeContext())
    assert eligible == "key-solo"


def test_orchestrator_own_dispatch_carrier_is_collected() -> None:
    """The 6th top-level `orchestrator_effect_fence_resume` carrier (the
    FIRST-step analogue of the LINEAR carrier) is collected too — round-1
    correction's own fix, verified here."""
    root = _snapshot(
        run_id="run-orch",
        orchestrator_effect_fence_resume=OrchestratorEffectFencePausedResumeState(
            idempotency_key="key-orch", step_id="s0", step_kind="tool-step"
        ),
    )
    assert _collect_effect_fence_idempotency_keys(root) == ["key-orch"]
    eligible = compute_effect_fence_uniform_fallback_eligible_key(root, ResumeContext())
    assert eligible == "key-orch"


def test_two_unaddressed_locations_yield_no_eligible_key() -> None:
    """Core safety case: 2 concurrently-paused effect-fence locations (a LINEAR
    pause nested under one peer branch + an orchestrator pause nested under a
    sibling peer branch), neither addressed by `effect_fence_resolutions` —
    NEITHER may use the uniform fallback (safety: 2+ unaddressed -> None)."""
    child_a = _snapshot(
        run_id="run-a",
        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-a"),
    )
    child_b = _snapshot(
        run_id="run-b",
        orchestrator_effect_fence_resume=OrchestratorEffectFencePausedResumeState(
            idempotency_key="key-b", step_id="s0", step_kind="tool-step"
        ),
    )
    root = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(branch_index=0, child_snapshot=child_a),
                _paused_child(branch_index=1, child_snapshot=child_b),
            ),
        ),
    )
    assert set(_collect_effect_fence_idempotency_keys(root)) == {"key-a", "key-b"}
    assert compute_effect_fence_uniform_fallback_eligible_key(root, ResumeContext()) is None
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    assert compute_effect_fence_uniform_fallback_eligible_key(root, uniform_only) is None


def test_map_addressing_one_of_two_leaves_the_other_as_sole_eligible() -> None:
    """When the operator's `effect_fence_resolutions` map addresses ALL BUT ONE
    unaddressed location, the remaining one is safely the SOLE member — the
    uniform fallback may resolve it."""
    child_a = _snapshot(
        run_id="run-a",
        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-a"),
    )
    child_b = _snapshot(
        run_id="run-b",
        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-b"),
    )
    root = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(branch_index=0, child_snapshot=child_a),
                _paused_child(branch_index=1, child_snapshot=child_b),
            ),
        ),
    )
    addressed = ResumeContext(effect_fence_resolutions={"key-a": EffectFenceResolution.ABORT})
    assert compute_effect_fence_uniform_fallback_eligible_key(root, addressed) == "key-b"


def test_none_root_or_none_resume_context_yields_no_eligible_key() -> None:
    assert compute_effect_fence_uniform_fallback_eligible_key(None, ResumeContext()) is None
    root = _snapshot(
        run_id="run-solo",
        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-solo"),
    )
    assert compute_effect_fence_uniform_fallback_eligible_key(root, None) is None


# ---------- `_resolve_effect_fence_gated` unit tests --------------------------


def test_gated_resolve_none_resume_context_yields_none() -> None:
    assert _resolve_effect_fence_gated(None, "key-a", "key-a") is None


def test_gated_resolve_map_hit_always_wins_regardless_of_eligibility() -> None:
    """A map HIT is addressed to THIS key specifically — always safe, independent
    of `eligible_key` (which only gates the UNIFORM fallback path). Even with
    `eligible_key=None` (correctly reflecting an unaddressed sibling elsewhere),
    a map-addressed key still resolves to its OWN mapped value."""
    ctx = ResumeContext(
        effect_fence_resolution=EffectFenceResolution.ABORT,
        effect_fence_resolutions={"key-a": EffectFenceResolution.SKIP_AS_FIRED},
    )
    assert _resolve_effect_fence_gated(ctx, "key-a", None) is EffectFenceResolution.SKIP_AS_FIRED


def test_gated_resolve_uniform_fallback_only_when_sole_eligible() -> None:
    ctx = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    assert _resolve_effect_fence_gated(ctx, "key-a", "key-a") is EffectFenceResolution.RE_FIRE
    # Not the eligible key -> None (re-pause INERT), never the uniform default.
    assert _resolve_effect_fence_gated(ctx, "key-a", "key-b") is None
    assert _resolve_effect_fence_gated(ctx, "key-a", None) is None


# ---------- LINEAR reconstruction site integration witnesses -----------------


def _manifest() -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=_WF,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": "do_effect", "tool_args": {"message": name}},
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


def _pause_context_reader() -> tuple[StateSummary, str]:
    return (_summary(), _ANCHOR)


def _protocol() -> Any:
    from harness_cp.pause_resume_protocol import PauseResumeProtocol

    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


class _Ctx:
    def __init__(self) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _RecordingLedger()
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = _protocol()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.inter_step_output_channel = None


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is StepKind.TOOL_STEP:
            return self._dispatcher
        raise StepKindDispatcherNotBoundError(step_kind)


def _registry(dispatcher: StepDispatcher) -> StepDispatcherRegistry:
    return cast(StepDispatcherRegistry, _Registry(dispatcher))


class _FenceAmbiguousDispatcher:
    """Raises the (name-matched) effect-fence ambiguous error at `raise_on`;
    succeeds otherwise. Records `step_context.effect_fence_resolution` seen at
    every dispatch (the producer-half witness)."""

    def __init__(self, *, raise_on: str) -> None:
        self._raise_on = raise_on
        self.dispatched: list[str] = []
        self.seen_directives: list[tuple[str, Any]] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.dispatched.append(step_id)
        self.seen_directives.append(
            (step_id, getattr(step_context, "effect_fence_resolution", None))
        )
        if step_id == self._raise_on:
            raise EffectFenceAmbiguousUncommittedError(
                "effect-fence: reserved + no captured output (ambiguous)",
                idempotency_key=f"fence-key-{step_id}",
            )
        return {"tool_id": "do_effect", "response": {"echoed": step_id}}


def _capture_fence_pause(*, run_id: str) -> PauseSnapshot:
    ctx = _Ctx()
    dispatcher = _FenceAmbiguousDispatcher(raise_on="s0")
    result = execute_workflow(
        _manifest(),
        [_step("s0"), _step("s1")],
        run_id=run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason is WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS
    return snap


def _resume(
    *,
    pause_snapshot_input: PauseSnapshot,
    resume_context: ResumeContext,
    effect_fence_uniform_fallback_eligible_key: str | None,
) -> _FenceAmbiguousDispatcher:
    """Resume the captured pause with a dispatcher that never re-raises (models a
    resolved/cleared reserve); return the recording dispatcher for assertion."""
    ctx = _Ctx()
    dispatcher = _FenceAmbiguousDispatcher(raise_on="__never__")
    result = execute_workflow(
        _manifest(),
        [_step("s0"), _step("s1")],
        run_id=pause_snapshot_input.run_id,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
        pause_snapshot_input=pause_snapshot_input,
        resume_context=resume_context,
        effect_fence_uniform_fallback_eligible_key=effect_fence_uniform_fallback_eligible_key,
    )
    assert result.status is RunStatus.SUCCESS
    return dispatcher


def test_two_unaddressed_linear_pauses_both_repause_inert_not_misapplied() -> None:
    """The B-70 defect this arc closes. Two independently-paused LINEAR effect-fence
    locations (simulating 2 concurrently-paused unaddressed locations in one resume()
    tree) resume with a `resume_context` carrying ONLY the uniform `effect_fence_
    resolution` (no map — the naive, pre-B-70-shaped caller).
    `effect_fence_uniform_fallback_eligible_key=None` (what `compute_effect_fence_
    uniform_fallback_eligible_key` correctly returns for this 2-member-unaddressed
    scenario, per the pure tests above) — NEITHER location's resumed step may
    receive a directive. Before this fix, the LINEAR site read `resume_context.
    effect_fence_resolution` directly and unconditionally, misapplying one operator
    judgment to both — exactly the round-2 defect out-of-family review found."""
    snap_a = _capture_fence_pause(run_id="run-fence-a")
    snap_b = _capture_fence_pause(run_id="run-fence-b")

    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)

    dispatcher_a = _resume(
        pause_snapshot_input=snap_a,
        resume_context=uniform_only,
        effect_fence_uniform_fallback_eligible_key=None,
    )
    dispatcher_b = _resume(
        pause_snapshot_input=snap_b,
        resume_context=uniform_only,
        effect_fence_uniform_fallback_eligible_key=None,
    )

    # The RESUMED step (s0, where the pause was captured) must NEVER receive a
    # directive for either location — re-pause INERT is the safe outcome (here
    # witnessed as "no directive threaded", since this dispatcher never re-raises).
    directive_a = dict(dispatcher_a.seen_directives)["s0"]
    directive_b = dict(dispatcher_b.seen_directives)["s0"]
    assert directive_a is None
    assert directive_b is None


def test_sole_unaddressed_linear_pause_safely_receives_uniform_fallback() -> None:
    """Positive control: when `effect_fence_uniform_fallback_eligible_key` correctly
    names ONE location's key as the sole unaddressed member, THAT location receives
    the uniform resolution key-bound to its own reserve."""
    snap = _capture_fence_pause(run_id="run-fence-solo")
    assert snap.effect_fence_resume is not None
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)

    dispatcher = _resume(
        pause_snapshot_input=snap,
        resume_context=uniform_only,
        effect_fence_uniform_fallback_eligible_key=snap.effect_fence_resume.idempotency_key,
    )
    directive = dict(dispatcher.seen_directives)["s0"]
    assert directive is not None
    assert directive.resolution is EffectFenceResolution.RE_FIRE
    assert directive.idempotency_key == snap.effect_fence_resume.idempotency_key


def test_map_hit_is_always_safe_regardless_of_uniform_fallback_eligibility() -> None:
    """An `effect_fence_resolutions` map HIT is addressed to THIS key specifically —
    always safe, independent of `effect_fence_uniform_fallback_eligible_key` (which
    only gates the UNIFORM fallback path). Even with eligibility explicitly `None`
    (as it correctly would be with an unaddressed sibling elsewhere), a map-addressed
    location still receives its own keyed resolution. This is also the round-3
    map-addressability witness: the LINEAR site now genuinely consults the map for
    its OWN key instead of reading the uniform field directly."""
    snap = _capture_fence_pause(run_id="run-fence-mapped")
    assert snap.effect_fence_resume is not None
    key = snap.effect_fence_resume.idempotency_key
    resume_ctx = ResumeContext(
        effect_fence_resolution=EffectFenceResolution.ABORT,
        effect_fence_resolutions={key: EffectFenceResolution.SKIP_AS_FIRED},
    )

    dispatcher = _resume(
        pause_snapshot_input=snap,
        resume_context=resume_ctx,
        effect_fence_uniform_fallback_eligible_key=None,
    )
    directive = dict(dispatcher.seen_directives)["s0"]
    assert directive is not None
    assert directive.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert directive.idempotency_key == key


def test_fresh_non_resuming_dispatch_never_receives_effect_fence_directive() -> None:
    """A fresh (non-resume) dispatch has no `resume_snapshot.effect_fence_resume` —
    the directive-construction gate never fires, byte-identical to pre-arc."""
    ctx = _Ctx()
    dispatcher = _FenceAmbiguousDispatcher(raise_on="__never__")
    result = execute_workflow(
        _manifest(),
        [_step("s0"), _step("s1")],
        run_id="run-fresh",
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(dispatcher),
        resume_context=ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE),
        effect_fence_uniform_fallback_eligible_key="some-unrelated-key",
    )
    assert result.status is RunStatus.SUCCESS
    assert all(directive is None for _step_id, directive in dispatcher.seen_directives)

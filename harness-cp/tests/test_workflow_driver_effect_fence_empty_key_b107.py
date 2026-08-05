"""B-107 impl leg — CP spec v1.115 §1.1-§1.5 / CP plan v2.49 §1.1 AC #A12.

The ratified "Reading A-hybrid" empty-effect-fence-key closure. Three contract terms,
each witnessed here:

  §1.1 SCALAR membership — the uniform-fallback unaddressed/eligible set contains only
       locations whose captured `idempotency_key` is NON-EMPTY, so
       `compute_effect_fence_uniform_fallback_eligible_key` can never nominate `""`.
  §1.2 MAP domain — on ORDINARY construction every `ResumeContext.
       effect_fence_resolutions` key MUST be non-empty, and the field MUST be a
       validated immutable COPY of the supplied mapping.
  §1.3 RESOLVER boundary — at EVERY consult an empty `idempotency_key` is unresolvable
       and yields no directive BEFORE either the map-hit check or the uniform-eligibility
       comparison, which also makes validation-bypassed content (§1.5) inert.

Module layout mirrors AC #A12's five clauses:

  1. The EIGHT-CELL GRID — map + scalar channels at LINEAR, PARALLELIZATION branch,
     ORCHESTRATOR_WORKERS worker, and ORCHESTRATOR-own carrier.
  2. SCALAR removal witnesses (§1.1) — the filtered candidate computation, the ratified
     b80 flip's own precondition, and the direct caller-supplied
     `effect_fence_uniform_fallback_eligible_key=""` no-directive case.
  3. PD-8 map probes (§1.2) — validation / copying / immutability / valid-map
     serialization compatibility, each discriminated by a DISTINCT probe.
  4. `model_construct` forged-context inertness (§1.5).
  5. The programmatic resolver-reader inventory (clause 5).

**Witness-strength honesty (plan v2.49 §1.1 clause 1).** The two ORCHESTRATOR-own cells
are CONSTRUCTED-SNAPSHOT tests, not e2e: the shipped orchestrator consult is
truthiness-gated on the captured key (`workflow_driver.py`'s `if (_orch_fence_resume.
idempotency_key and _ef_resume_ctx is not None)`), so those cells CANNOT discriminate the
§1.3 resolver guard and are NOT counted as §1.3 closure evidence. §1.3 discrimination
binds at the LINEAR reconstruction site and at the two level-local `_any_fence_abort`
branch scans, whose consults are ungated — those are the cells that carry clause 5's
"fails if the guard is removed" claim.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import textwrap
import threading
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp import workflow_driver as _workflow_driver_module
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
from pydantic import ValidationError

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-effect-fence-empty-key-b107")
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # -> cascade_policy = pause
_ANCHOR = "0" * 64


class EffectFenceAmbiguousUncommittedError(Exception):
    """Test-local stand-in for the runtime fence error (name-matched by the driver —
    `harness-cp` cannot import `harness-runtime`). Mirrors the identical local
    declaration in `test_workflow_driver_effect_fence_uniform_fallback_b70.py`."""

    def __init__(self, message: str = "", *, idempotency_key: str = "") -> None:
        self.idempotency_key = idempotency_key
        super().__init__(message or "effect-fence: ambiguous (no captured output)")


# ---------------------------------------------------------------------------
# Shared harness (pause/resume-capable driver context + registries)
# ---------------------------------------------------------------------------


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _pause_context_reader() -> tuple[StateSummary, str]:
    return (_summary(), _ANCHOR)


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
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


def _ctx() -> DriverContext:
    return cast(DriverContext, _Ctx())


class _KindRegistry:
    def __init__(self, dispatcher: StepDispatcher, kind: StepKind) -> None:
        self._dispatcher = dispatcher
        self._kind = kind

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is not self._kind:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


def _registry(dispatcher: StepDispatcher, kind: StepKind) -> StepDispatcherRegistry:
    return cast(StepDispatcherRegistry, _KindRegistry(dispatcher, kind))


def _manifest(workflow_id: str, topology: TopologyPattern) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PAUSE_TIER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _snapshot(
    *,
    run_id: str,
    pause_reason: WorkflowPauseReason = WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
    effect_fence_resume: EffectFenceResumeState | None = None,
    orchestrator_effect_fence_resume: OrchestratorEffectFencePausedResumeState | None = None,
    peer_fan_out_resume: PeerFanOutResumeState | None = None,
) -> PauseSnapshot:
    """A minimal `PauseSnapshot` for the CONSTRUCTED-SNAPSHOT cells — `snapshot_hash` is a
    placeholder (the pure classification functions read the object graph directly, never
    through `attempt_resume`'s hash-recompute gate). Mirrors the identical helper in
    `test_workflow_driver_effect_fence_uniform_fallback_b70.py`."""
    return PauseSnapshot(
        workflow_id="wf-b107",
        run_id=run_id,
        step_index=0,
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


# ---------------------------------------------------------------------------
# LINEAR carrier harness (real pause/resume through `execute_workflow`)
# ---------------------------------------------------------------------------


def _linear_step(name: str) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(name),
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": "do_effect", "tool_args": {"message": name}},
    )


class _LinearFenceDispatcher:
    """Raises the (name-matched) fence error at `raise_on` with the supplied key;
    succeeds otherwise. Records the `effect_fence_resolution` directive seen at every
    dispatch (the producer-half witness)."""

    def __init__(self, *, raise_on: str, fence_key: str) -> None:
        self._raise_on = raise_on
        self._fence_key = fence_key
        self.seen_directives: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        self.seen_directives[step_id] = getattr(step_context, "effect_fence_resolution", None)
        if step_id == self._raise_on:
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=self._fence_key)
        return {"tool_id": "do_effect", "response": {"echoed": step_id}}


def _capture_linear_fence_pause(*, run_id: str, fence_key: str) -> PauseSnapshot:
    result = execute_workflow(
        _manifest("wf-b107-linear", TopologyPattern.SINGLE_THREADED_LINEAR),
        [_linear_step("s0"), _linear_step("s1")],
        run_id=run_id,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            cast(StepDispatcher, _LinearFenceDispatcher(raise_on="s0", fence_key=fence_key)),
            StepKind.TOOL_STEP,
        ),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None
    assert snap.pause_reason is WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS
    assert snap.effect_fence_resume is not None
    assert snap.effect_fence_resume.idempotency_key == fence_key
    return snap


def _resume_linear(
    *,
    snap: PauseSnapshot,
    resume_context: ResumeContext,
    eligible_key: str | None,
) -> _LinearFenceDispatcher:
    """Resume the captured LINEAR pause with a dispatcher that never re-raises (models a
    resolved/cleared reserve); return the recording dispatcher for assertion."""
    dispatcher = _LinearFenceDispatcher(raise_on="__never__", fence_key="__unused__")
    result = execute_workflow(
        _manifest("wf-b107-linear", TopologyPattern.SINGLE_THREADED_LINEAR),
        [_linear_step("s0"), _linear_step("s1")],
        run_id=snap.run_id,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher), StepKind.TOOL_STEP),
        pause_snapshot_input=snap,
        resume_context=resume_context,
        effect_fence_uniform_fallback_eligible_key=eligible_key,
    )
    assert result.status is RunStatus.SUCCESS
    return dispatcher


# ---------------------------------------------------------------------------
# Fan-out carrier harness (PARALLELIZATION peers + ORCHESTRATOR_WORKERS workers)
# ---------------------------------------------------------------------------


def _peer_steps(n: int) -> list[WorkflowStep]:
    """A PEER fan-out — every step IS a branch (NO orchestrator `steps[0]`)."""
    return [
        WorkflowStep(
            step_id=StepID(f"branch-{i}"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"index": i},
        )
        for i in range(n)
    ]


def _worker_steps(n: int) -> list[WorkflowStep]:
    """An ORCHESTRATOR_WORKERS fan-out — `steps[0]` is the orchestrator."""
    return [
        WorkflowStep(
            step_id=StepID("orchestrator"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"role": "orchestrator"},
        ),
        *(
            WorkflowStep(
                step_id=StepID(f"worker-{i}"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={"index": i},
            )
            for i in range(n)
        ),
    ]


class _TwoBranchFenceDispatcher:
    """Both fan-out branches raise the fence error, synchronized on a barrier so BOTH are
    in-flight before either raises -> TWO `effect_fence_paused_branches` in one pause.
    `keys_by_step_id` decides which branch carries the EMPTY key, so the same harness
    produces BOTH carrier orders (the carrier tuple is `sorted()` by `branch_index`)."""

    def __init__(self, *, keys_by_step_id: dict[str, str], barrier_parties: int) -> None:
        self._keys = keys_by_step_id
        self._barrier = threading.Barrier(barrier_parties, timeout=10.0)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        self._barrier.wait()
        raise EffectFenceAmbiguousUncommittedError(idempotency_key=self._keys[step_id])


class _DirectiveRecordingDispatcher:
    """Resume-side witness: records the directive each branch received; RE-RAISES the fence
    error when NO directive reached the branch (modelling the runtime's INERT re-pause), so
    "no directive" is observable as a real re-pause rather than a vacuous success."""

    def __init__(self, *, keys_by_step_id: dict[str, str]) -> None:
        self._keys = keys_by_step_id
        self.seen_directives: dict[str, Any] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        step_id = str(step.step_id)
        if step_id == "orchestrator":
            return {"role": "orchestrator"}
        directive = getattr(step_context, "effect_fence_resolution", None)
        self.seen_directives[step_id] = directive
        if directive is None:
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=self._keys[step_id])
        return {"role": step_id, "echoed": dict(step.step_payload)}


_EMPTY = ""
_KEYED = "fence-key-real"


def _fanout_keys(*, empty_at: int, prefix: str) -> dict[str, str]:
    """Key assignment for a 2-branch fan-out: branch `empty_at` gets the EMPTY captured key
    and its sibling gets `_KEYED`. Driving BOTH values of `empty_at` exercises BOTH carrier
    orders (empty-before-keyed and keyed-before-empty)."""
    return {f"{prefix}-{i}": (_EMPTY if i == empty_at else _KEYED) for i in range(2)}


def _capture_peer_fence_pause(*, empty_at: int) -> PauseSnapshot:
    result = execute_workflow(
        _manifest("wf-b107-par", TopologyPattern.PARALLELIZATION),
        _peer_steps(2),
        run_id="run-b107-par",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            cast(
                StepDispatcher,
                _TwoBranchFenceDispatcher(
                    keys_by_step_id=_fanout_keys(empty_at=empty_at, prefix="branch"),
                    barrier_parties=2,
                ),
            ),
            StepKind.DECLARATIVE_STEP,
        ),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None and snap.peer_fan_out_resume is not None
    carrier = snap.peer_fan_out_resume.effect_fence_paused_branches
    assert [b.idempotency_key for b in carrier] == [
        _EMPTY if i == empty_at else _KEYED for i in range(2)
    ], f"carrier order not as intended: {[b.idempotency_key for b in carrier]!r}"
    return snap


_DERIVE_ELIGIBLE_KEY = "<derive-from-the-real-computation>"
"""Sentinel for the resume helpers' `eligible_key` argument: derive it through the real
`compute_effect_fence_uniform_fallback_eligible_key`. Passing an explicit value instead
lets a test BYPASS §1.1 and hand the driver a caller-supplied key directly, which is how
the §1.3 resolver boundary is exercised independently of the §1.1 membership rule."""


def _resume_peer(
    *,
    snap: PauseSnapshot,
    resume_context: ResumeContext,
    empty_at: int,
    eligible_key: str | None = _DERIVE_ELIGIBLE_KEY,
) -> tuple[Any, _DirectiveRecordingDispatcher]:
    dispatcher = _DirectiveRecordingDispatcher(
        keys_by_step_id=_fanout_keys(empty_at=empty_at, prefix="branch")
    )
    result = execute_workflow(
        _manifest("wf-b107-par", TopologyPattern.PARALLELIZATION),
        _peer_steps(2),
        run_id="run-b107-par",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher), StepKind.DECLARATIVE_STEP),
        pause_snapshot_input=snap,
        resume_context=resume_context,
        effect_fence_uniform_fallback_eligible_key=(
            compute_effect_fence_uniform_fallback_eligible_key(snap, resume_context)
            if eligible_key == _DERIVE_ELIGIBLE_KEY
            else eligible_key
        ),
    )
    return result, dispatcher


def _capture_worker_fence_pause(*, empty_at: int) -> PauseSnapshot:
    result = execute_workflow(
        _manifest("wf-b107-ow", TopologyPattern.ORCHESTRATOR_WORKERS),
        _worker_steps(2),
        run_id="run-b107-ow",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(
            cast(
                StepDispatcher,
                _TwoBranchFenceDispatcher(
                    keys_by_step_id=_fanout_keys(empty_at=empty_at, prefix="worker"),
                    barrier_parties=2,
                ),
            ),
            StepKind.DECLARATIVE_STEP,
        ),
    )
    assert result.status is RunStatus.PAUSED
    snap = result.pause_snapshot
    assert snap is not None and snap.fan_out_resume is not None
    carrier = snap.fan_out_resume.effect_fence_paused_branches
    assert [b.idempotency_key for b in carrier] == [
        _EMPTY if i == empty_at else _KEYED for i in range(2)
    ], f"carrier order not as intended: {[b.idempotency_key for b in carrier]!r}"
    return snap


def _resume_worker(
    *,
    snap: PauseSnapshot,
    resume_context: ResumeContext,
    empty_at: int,
    eligible_key: str | None = _DERIVE_ELIGIBLE_KEY,
) -> tuple[Any, _DirectiveRecordingDispatcher]:
    dispatcher = _DirectiveRecordingDispatcher(
        keys_by_step_id=_fanout_keys(empty_at=empty_at, prefix="worker")
    )
    result = execute_workflow(
        _manifest("wf-b107-ow", TopologyPattern.ORCHESTRATOR_WORKERS),
        _worker_steps(2),
        run_id="run-b107-ow",
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=_registry(cast(StepDispatcher, dispatcher), StepKind.DECLARATIVE_STEP),
        pause_snapshot_input=snap,
        resume_context=resume_context,
        effect_fence_uniform_fallback_eligible_key=(
            compute_effect_fence_uniform_fallback_eligible_key(snap, resume_context)
            if eligible_key == _DERIVE_ELIGIBLE_KEY
            else eligible_key
        ),
    )
    return result, dispatcher


# ===========================================================================
# CLAUSE 1 — the EIGHT-CELL grid
# ===========================================================================

# --- cells 1 + 2: LINEAR carrier -------------------------------------------


def test_cell1_linear_scalar_channel_empty_key_receives_no_directive() -> None:
    """GRID CELL 1 (LINEAR x SCALAR). A LINEAR effect-fence pause whose captured key is
    EMPTY, resumed with the operator's UNIFORM `effect_fence_resolution` only.

    e2e through the REAL `execute_workflow` LINEAR reconstruction site — the ungated
    consult §1.3 discrimination binds at. The resumed step must receive NO directive:
    §1.1 keeps `""` out of the eligible set, and §1.3 refuses it at the resolver even if
    an eligible key somehow named it (witnessed independently at clause 2). Before B-107
    this location WAS the sole "unaddressed" member and DID receive a key-bound directive
    carrying `idempotency_key=""` — a directive addressed to no held reserve at all."""
    snap = _capture_linear_fence_pause(run_id="run-b107-lin-scalar", fence_key=_EMPTY)
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    eligible = compute_effect_fence_uniform_fallback_eligible_key(snap, uniform_only)
    assert eligible is None, "§1.1 — an empty captured key is never uniform-fallback eligible"
    dispatcher = _resume_linear(snap=snap, resume_context=uniform_only, eligible_key=eligible)
    assert dispatcher.seen_directives["s0"] is None


def test_cell2_linear_map_channel_empty_key_receives_no_directive_keyed_control_does() -> None:
    """GRID CELL 2 (LINEAR x MAP). The same LINEAR carrier resolved through the per-key
    `effect_fence_resolutions` MAP channel.

    Two halves in one cell because a LINEAR pause has exactly one location and therefore no
    in-tree sibling: (a) an EMPTY-key LINEAR pause resumed with a map (plus a uniform
    default) receives NO directive; (b) the KEYED positive control — the identical map
    shape DOES deliver to a non-empty captured key, so half (a) is not passing merely
    because the map channel is inert here."""
    mapped = ResumeContext(
        effect_fence_resolutions={_KEYED: EffectFenceResolution.SKIP_AS_FIRED},
        effect_fence_resolution=EffectFenceResolution.RE_FIRE,
    )

    empty_snap = _capture_linear_fence_pause(run_id="run-b107-lin-map-e", fence_key=_EMPTY)
    empty_dispatcher = _resume_linear(
        snap=empty_snap,
        resume_context=mapped,
        eligible_key=compute_effect_fence_uniform_fallback_eligible_key(empty_snap, mapped),
    )
    assert empty_dispatcher.seen_directives["s0"] is None

    keyed_snap = _capture_linear_fence_pause(run_id="run-b107-lin-map-k", fence_key=_KEYED)
    keyed_dispatcher = _resume_linear(
        snap=keyed_snap,
        resume_context=mapped,
        eligible_key=compute_effect_fence_uniform_fallback_eligible_key(keyed_snap, mapped),
    )
    keyed_directive = keyed_dispatcher.seen_directives["s0"]
    assert keyed_directive is not None
    assert keyed_directive.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert keyed_directive.idempotency_key == _KEYED


# --- cells 3 + 4: PARALLELIZATION branch carrier ----------------------------


@pytest.mark.parametrize("empty_at", [0, 1])
def test_cell3_parallelization_scalar_channel_empty_key_never_suppresses_keyed_sibling(
    empty_at: int,
) -> None:
    """GRID CELL 3 (PARALLELIZATION branch x SCALAR), in BOTH carrier orders.

    Two peer branches fence-pause in one barrier: one with an EMPTY captured key, one with
    a real key. The operator supplies only the UNIFORM `effect_fence_resolution`.

    The keyed sibling MUST resolve, and the empty-key peer MUST receive nothing. Both
    halves are load-bearing and both were WRONG before B-107: the empty-key peer inflated
    the unaddressed count to 2, so `eligible_key` was `None` and the keyed sibling — the
    only location an operator could ever address — was denied the uniform fallback and
    re-paused INERT. The empty-key peer's own suppression is over-determined here (the
    per-branch consult truthiness-gates the key), so the load-bearing half of this cell is
    the SIBLING's survival."""
    snap = _capture_peer_fence_pause(empty_at=empty_at)
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    assert compute_effect_fence_uniform_fallback_eligible_key(snap, uniform_only) == _KEYED
    result, dispatcher = _resume_peer(snap=snap, resume_context=uniform_only, empty_at=empty_at)

    keyed_step = f"branch-{1 - empty_at}"
    empty_step = f"branch-{empty_at}"
    keyed_directive = dispatcher.seen_directives[keyed_step]
    assert keyed_directive is not None, "the keyed sibling must NOT be suppressed"
    assert keyed_directive.resolution is EffectFenceResolution.RE_FIRE
    assert keyed_directive.idempotency_key == _KEYED
    assert dispatcher.seen_directives[empty_step] is None
    # The empty-key peer re-paused INERT, so the run is still PAUSED and carries ONLY it.
    assert result.status is RunStatus.PAUSED
    snap2 = result.pause_snapshot
    assert snap2 is not None and snap2.peer_fan_out_resume is not None
    assert [b.idempotency_key for b in snap2.peer_fan_out_resume.effect_fence_paused_branches] == [
        _EMPTY
    ]


@pytest.mark.parametrize("empty_at", [0, 1])
def test_cell4_parallelization_map_channel_empty_key_never_suppresses_keyed_sibling(
    empty_at: int,
) -> None:
    """GRID CELL 4 (PARALLELIZATION branch x MAP), in BOTH carrier orders.

    The same two-peer pause, resolved through the per-key MAP channel. A map hit is
    unconditionally safe (CP spec v1.107 §1.1) and must remain so with an empty-key peer
    alongside: the keyed sibling gets its OWN mapped resolution and the empty-key peer
    still gets nothing — the map cannot be addressed to `""` at all (§1.2, witnessed at
    clause 3), so there is no map entry for it to hit."""
    snap = _capture_peer_fence_pause(empty_at=empty_at)
    mapped = ResumeContext(effect_fence_resolutions={_KEYED: EffectFenceResolution.SKIP_AS_FIRED})
    result, dispatcher = _resume_peer(snap=snap, resume_context=mapped, empty_at=empty_at)

    keyed_directive = dispatcher.seen_directives[f"branch-{1 - empty_at}"]
    assert keyed_directive is not None
    assert keyed_directive.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert keyed_directive.idempotency_key == _KEYED
    assert dispatcher.seen_directives[f"branch-{empty_at}"] is None
    assert result.status is RunStatus.PAUSED


# --- cells 5 + 6: ORCHESTRATOR_WORKERS worker carrier -----------------------


@pytest.mark.parametrize("empty_at", [0, 1])
def test_cell5_orchestrator_workers_scalar_channel_empty_key_never_suppresses_keyed_sibling(
    empty_at: int,
) -> None:
    """GRID CELL 5 (ORCHESTRATOR_WORKERS worker x SCALAR), in BOTH carrier orders.

    The `_execute_orchestrator_workers` sibling of cell 3 — the two strategies share the
    exact same `_resolve_effect_fence_gated` helper AND the same ungated level-local
    `_any_fence_abort` scan, so the property is asserted at BOTH rather than assumed to
    transfer (`[[codex-finding-scope-verify-sibling-pattern]]`)."""
    snap = _capture_worker_fence_pause(empty_at=empty_at)
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    assert compute_effect_fence_uniform_fallback_eligible_key(snap, uniform_only) == _KEYED
    result, dispatcher = _resume_worker(snap=snap, resume_context=uniform_only, empty_at=empty_at)

    keyed_directive = dispatcher.seen_directives[f"worker-{1 - empty_at}"]
    assert keyed_directive is not None, "the keyed sibling must NOT be suppressed"
    assert keyed_directive.resolution is EffectFenceResolution.RE_FIRE
    assert keyed_directive.idempotency_key == _KEYED
    assert dispatcher.seen_directives[f"worker-{empty_at}"] is None
    assert result.status is RunStatus.PAUSED
    snap2 = result.pause_snapshot
    assert snap2 is not None and snap2.fan_out_resume is not None
    assert [b.idempotency_key for b in snap2.fan_out_resume.effect_fence_paused_branches] == [
        _EMPTY
    ]


@pytest.mark.parametrize("empty_at", [0, 1])
def test_cell6_orchestrator_workers_map_channel_empty_key_never_suppresses_keyed_sibling(
    empty_at: int,
) -> None:
    """GRID CELL 6 (ORCHESTRATOR_WORKERS worker x MAP), in BOTH carrier orders — the
    `_execute_orchestrator_workers` sibling of cell 4."""
    snap = _capture_worker_fence_pause(empty_at=empty_at)
    mapped = ResumeContext(effect_fence_resolutions={_KEYED: EffectFenceResolution.SKIP_AS_FIRED})
    result, dispatcher = _resume_worker(snap=snap, resume_context=mapped, empty_at=empty_at)

    keyed_directive = dispatcher.seen_directives[f"worker-{1 - empty_at}"]
    assert keyed_directive is not None
    assert keyed_directive.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert keyed_directive.idempotency_key == _KEYED
    assert dispatcher.seen_directives[f"worker-{empty_at}"] is None
    assert result.status is RunStatus.PAUSED


# --- cells 7 + 8: ORCHESTRATOR-own carrier (CONSTRUCTED SNAPSHOTS ONLY) ------


def _orchestrator_own_root(*, orchestrator_key: str, sibling_key: str) -> PauseSnapshot:
    """A root whose ORCHESTRATOR-OWN dispatch fence-paused, with one nested keyed sibling
    location under a paused child. Constructed, never captured: the orchestrator-own carrier
    guards on a truthy key at its own CAPTURE site (`workflow_driver.py`), so an empty-key
    orchestrator-own shape is UNREACHABLE in production and rests on type totality (CP spec
    v1.113's own falsified-premise finding)."""
    sibling = _snapshot(
        run_id="run-b107-orch-sibling",
        effect_fence_resume=EffectFenceResumeState(idempotency_key=sibling_key),
    )
    return _snapshot(
        run_id="run-b107-orch-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        orchestrator_effect_fence_resume=OrchestratorEffectFencePausedResumeState(
            idempotency_key=orchestrator_key, step_id="s0", step_kind="tool-step"
        ),
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            paused_child_branches=(_paused_child(branch_index=0, child_snapshot=sibling),),
        ),
    )


def test_cell7_orchestrator_own_scalar_channel_classification_excludes_empty_key() -> None:
    """GRID CELL 7 (ORCHESTRATOR-own x SCALAR) — CONSTRUCTED-SNAPSHOT, classification only.

    **NOT §1.3 closure evidence** (plan v2.49 §1.1 clause 1): the shipped orchestrator-own
    consult is truthiness-gated on the captured key, so this cell cannot discriminate the
    resolver guard. What it DOES witness is the §1.1 classification at the orchestrator-own
    carrier: the empty orchestrator-own key is excluded from the unaddressed set (the
    walk still ENUMERATES it, §1.4), the nested keyed sibling becomes the sole eligible
    member, and the uniform default therefore reaches the sibling and not the orchestrator."""
    root = _orchestrator_own_root(orchestrator_key=_EMPTY, sibling_key="key-sibling")
    assert _collect_effect_fence_idempotency_keys(root) == [_EMPTY, "key-sibling"], (
        "§1.4 — the walk still PUBLISHES the position-only orchestrator-own entry"
    )
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    eligible = compute_effect_fence_uniform_fallback_eligible_key(root, uniform_only)
    assert eligible == "key-sibling"
    assert _resolve_effect_fence_gated(uniform_only, _EMPTY, eligible) is None
    assert (
        _resolve_effect_fence_gated(uniform_only, "key-sibling", eligible)
        is EffectFenceResolution.RE_FIRE
    )


def test_cell8_orchestrator_own_map_channel_classification_excludes_empty_key() -> None:
    """GRID CELL 8 (ORCHESTRATOR-own x MAP) — CONSTRUCTED-SNAPSHOT, classification only;
    **NOT §1.3 closure evidence**, for the same truthiness-gating reason as cell 7.

    With the nested keyed sibling MAP-addressed, nothing non-empty is left unaddressed, so
    there is no eligible key at all — yet the map hit still resolves the sibling (map hits
    are unconditionally safe) while the orchestrator's own empty key resolves to nothing."""
    root = _orchestrator_own_root(orchestrator_key=_EMPTY, sibling_key="key-sibling")
    mapped = ResumeContext(effect_fence_resolutions={"key-sibling": EffectFenceResolution.ABORT})
    eligible = compute_effect_fence_uniform_fallback_eligible_key(root, mapped)
    assert eligible is None
    assert _resolve_effect_fence_gated(mapped, _EMPTY, eligible) is None
    assert (
        _resolve_effect_fence_gated(mapped, "key-sibling", eligible) is EffectFenceResolution.ABORT
    )


# ===========================================================================
# CLAUSE 2 — SCALAR membership removal (§1.1) + the direct caller-supplied key
# ===========================================================================


def test_uniform_fallback_candidate_computation_excludes_empty_captured_keys() -> None:
    """§1.1 — the authoritative unaddressed/eligible set holds only NON-EMPTY captured keys.

    Three shapes at once: a SOLE empty-key location yields NO eligible key (it can never
    nominate `""`); an empty-key location BESIDE a keyed one leaves the keyed one as the
    SOLE member (the membership change the ratified b80 flip rests on); and two keyed
    locations still yield `None` (the pre-existing 2+-unaddressed safety rule is
    untouched)."""
    sole_empty = _snapshot(
        run_id="run-sole-empty",
        effect_fence_resume=EffectFenceResumeState(idempotency_key=_EMPTY),
    )
    assert _collect_effect_fence_idempotency_keys(sole_empty) == [_EMPTY]
    assert compute_effect_fence_uniform_fallback_eligible_key(sole_empty, ResumeContext()) is None

    empty_plus_keyed = _snapshot(
        run_id="run-mixed",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(
                    branch_index=0,
                    child_snapshot=_snapshot(
                        run_id="run-empty",
                        effect_fence_resume=EffectFenceResumeState(idempotency_key=_EMPTY),
                    ),
                ),
                _paused_child(
                    branch_index=1,
                    child_snapshot=_snapshot(
                        run_id="run-keyed",
                        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-b"),
                    ),
                ),
            ),
        ),
    )
    assert (
        compute_effect_fence_uniform_fallback_eligible_key(empty_plus_keyed, ResumeContext())
        == "key-b"
    )

    two_keyed = _snapshot(
        run_id="run-two-keyed",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                _paused_child(
                    branch_index=0,
                    child_snapshot=_snapshot(
                        run_id="run-a",
                        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-a"),
                    ),
                ),
                _paused_child(
                    branch_index=1,
                    child_snapshot=_snapshot(
                        run_id="run-b",
                        effect_fence_resume=EffectFenceResumeState(idempotency_key="key-b"),
                    ),
                ),
            ),
        ),
    )
    assert compute_effect_fence_uniform_fallback_eligible_key(two_keyed, ResumeContext()) is None


def test_caller_supplied_empty_eligible_key_produces_no_directive_at_the_linear_site() -> None:
    """§1.3 — `effect_fence_uniform_fallback_eligible_key` is an INPUT, never a second
    classification authority.

    This is the load-bearing §1.3 witness: it BYPASSES §1.1 entirely by handing the LINEAR
    reconstruction site a caller-supplied `""` eligible key directly (exactly what the
    pre-B-107 `compute_*` would have derived), and the resumed step STILL receives no
    directive. Without the resolver's own empty-key guard this resume would thread a
    directive key-bound to `""` — an address no held reserve can ever match."""
    snap = _capture_linear_fence_pause(run_id="run-b107-lin-direct", fence_key=_EMPTY)
    uniform_only = ResumeContext(effect_fence_resolution=EffectFenceResolution.RE_FIRE)
    dispatcher = _resume_linear(snap=snap, resume_context=uniform_only, eligible_key=_EMPTY)
    assert dispatcher.seen_directives["s0"] is None


@pytest.mark.parametrize("empty_at", [0, 1])
@pytest.mark.parametrize("topology", ["parallelization", "orchestrator_workers"])
def test_caller_supplied_empty_eligible_key_cannot_abort_a_keyed_sibling_at_the_branch_scan(
    topology: str, empty_at: int
) -> None:
    """§1.3 at the UNGATED level-local `_any_fence_abort` branch scan — with ORDINARY
    (validated) construction only, so it is independent of the forged-context clause.

    Setup: an empty-key branch beside a MAP-addressed keyed sibling (`SKIP_AS_FIRED`), a
    uniform `ABORT` default, and a caller-supplied `effect_fence_uniform_fallback_eligible_
    key=""` handed straight to the driver (bypassing §1.1, exactly the value the pre-B-107
    computation would have derived for this shape).

    Without the resolver's empty-key guard the scan resolves the empty branch to the uniform
    `ABORT`, which flips the RUN-LEVEL abort suppression on and NULLS the keyed sibling's
    `SKIP_AS_FIRED` directive — a location that addresses no reserve at all vetoing one the
    operator explicitly answered. With the guard, the scan sees no ABORT and the sibling
    fires. Both fan-out strategies are asserted (they carry separate copies of the scan) in
    both carrier orders."""
    resume_context = ResumeContext(
        effect_fence_resolutions={_KEYED: EffectFenceResolution.SKIP_AS_FIRED},
        effect_fence_resolution=EffectFenceResolution.ABORT,
    )
    if topology == "parallelization":
        snap = _capture_peer_fence_pause(empty_at=empty_at)
        result, dispatcher = _resume_peer(
            snap=snap, resume_context=resume_context, empty_at=empty_at, eligible_key=_EMPTY
        )
        prefix = "branch"
    else:
        snap = _capture_worker_fence_pause(empty_at=empty_at)
        result, dispatcher = _resume_worker(
            snap=snap, resume_context=resume_context, empty_at=empty_at, eligible_key=_EMPTY
        )
        prefix = "worker"

    keyed_directive = dispatcher.seen_directives[f"{prefix}-{1 - empty_at}"]
    assert keyed_directive is not None, (
        "the empty-key location must not activate the run-level ABORT guard and veto the "
        "map-addressed sibling the operator answered"
    )
    assert keyed_directive.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert keyed_directive.idempotency_key == _KEYED
    assert dispatcher.seen_directives[f"{prefix}-{empty_at}"] is None
    assert result.status is RunStatus.PAUSED


def test_the_pure_lookup_method_is_deliberately_outside_the_ss1_3_resolver_boundary() -> None:
    """§1.3 SCOPE PIN — the guard lives at the gated RESOLVER, not at the pure lookup.

    Records a DECLINED out-of-family Codex round-2 [P2] finding rather than absorbing it
    silently. The observation is factually correct — `ResumeContext(effect_fence_resolution=
    ABORT).effect_fence_resolution_for("")` does return `ABORT` — but extending the empty-key
    rule to that method is outside the ratified contract, for three grounded reasons:

    1. Fork §11 item 5 names the site: *"Every `_resolve_effect_fence_gated` consult treats
       `idempotency_key == ""` as unresolvable before map-hit and eligibility branches."*
    2. §1.3's own wording describes that function's structure — "yields no DIRECTIVE" and
       "before either a map-hit check or UNIFORM-ELIGIBILITY comparison". The pure lookup
       builds no directive and has no eligibility comparison; only the gated resolver has both.
    3. Spec v1.115 §0.1/§3 enumerate exactly THREE contract amendment sites. Narrowing a
       public method published at v1.66 would be a FOURTH, and §0.3 enumerates the authorized
       compatibility costs without it — an X-AL-3 silent design extension at impl time.

    Safety is not left to that reading: the method has exactly ONE non-test caller anywhere
    in production source (`_resolve_effect_fence_gated`, which now guards ahead of it), so no
    production path can reach the unguarded answer. This test pins BOTH halves — the
    deliberate behaviour and the single-caller premise it rests on — so a future arc that adds
    a second caller, or that ratifies the narrowing, breaks here instead of drifting silently.

    The inventory scans EVERY workspace package's `src/`, not just `workflow_driver.py`: a
    caller landing in some other production module would otherwise slip past the premise this
    decision rests on (out-of-family Codex round 3 [P3])."""
    plain = ResumeContext(effect_fence_resolution=EffectFenceResolution.ABORT)
    assert plain.effect_fence_resolution_for(_EMPTY) is EffectFenceResolution.ABORT

    repo_root = Path(__file__).resolve().parents[2]
    src_roots = sorted(repo_root.glob("harness-*/src"))
    assert len(src_roots) >= 6, f"unexpected workspace layout: {src_roots!r}"
    callers: dict[str, int] = {}
    for src_root in src_roots:
        for path in src_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            count = sum(
                1
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "effect_fence_resolution_for"
            )
            if count:
                callers[str(path.relative_to(repo_root))] = count

    assert callers == {"harness-cp/src/harness_cp/workflow_driver.py": 1}, (
        "the pure lookup's safety rests on having exactly ONE production caller, the guarded "
        f"`_resolve_effect_fence_gated`; found {callers!r} — re-decide the §1.3 boundary "
        "before adding another"
    )
    # And that one caller is genuinely the guarded resolver — counted over the resolver's own
    # AST, so its prose (which names the method) cannot inflate the count.
    assert _resolve_effect_fence_gated(plain, _EMPTY, _EMPTY) is None
    resolver_tree = ast.parse(textwrap.dedent(inspect.getsource(_resolve_effect_fence_gated)))
    assert (
        sum(
            1
            for node in ast.walk(resolver_tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "effect_fence_resolution_for"
        )
        == 1
    )


def test_resolver_refuses_empty_key_before_map_hit_and_before_eligibility() -> None:
    """§1.3 ORDERING — the refusal precedes BOTH downstream branches.

    Constructed to make each ordering claim falsifiable in isolation: the context carries a
    forged `""` map entry AND `""` is passed as the eligible key AND a uniform default is
    set, so a guard placed after the map-hit check, after the eligibility comparison, or
    after the uniform fallback would each return a resolution here. Only a guard ahead of
    all three returns `None`. The keyed control proves the resolver is otherwise live."""
    forged = ResumeContext.model_construct(
        effect_fence_resolution=EffectFenceResolution.ABORT,
        effect_fence_resolutions={
            _EMPTY: EffectFenceResolution.RE_FIRE,
            _KEYED: (EffectFenceResolution.SKIP_AS_FIRED),
        },
        hitl_response=None,
        hitl_responses=None,
    )
    assert _resolve_effect_fence_gated(forged, _EMPTY, _EMPTY) is None
    assert _resolve_effect_fence_gated(forged, _EMPTY, None) is None
    assert _resolve_effect_fence_gated(forged, _EMPTY, _KEYED) is None
    assert _resolve_effect_fence_gated(forged, _KEYED, None) is EffectFenceResolution.SKIP_AS_FIRED


# ===========================================================================
# CLAUSE 3 — PD-8 map probes (§1.2), each discriminated by a DISTINCT probe
# ===========================================================================


def test_pd8_probe_a_construction_with_an_empty_key_is_refused() -> None:
    """PD-8 probe (a) — VALIDATION. Fails if and only if the empty-key check is removed.

    Covers the base `ResumeContext` AND, by inheritance, the `AccessorDerivedResumeContext`
    subclass through BOTH of its construction entry points (`cls(...)` directly and the
    `from_pause_state` classmethod), per §1.2's "applies by inheritance" clause."""
    from harness_cp.pause_state_projection import AccessorDerivedResumeContext, PausedWorkflowState

    with pytest.raises(ValidationError):
        ResumeContext(effect_fence_resolutions={_EMPTY: EffectFenceResolution.ABORT})
    # A mixed map is refused too — one bad key poisons the whole domain, never a silent drop.
    with pytest.raises(ValidationError):
        ResumeContext(
            effect_fence_resolutions={
                _KEYED: EffectFenceResolution.RE_FIRE,
                _EMPTY: EffectFenceResolution.ABORT,
            }
        )

    pause_state = PausedWorkflowState(
        workflow_id="wf-b107",
        created_at=0,
        staleness_token="token-b107",
        locations=(),
    )
    with pytest.raises(ValidationError):
        AccessorDerivedResumeContext(
            pause_state=pause_state,
            effect_fence_resolutions={_EMPTY: EffectFenceResolution.ABORT},
        )
    with pytest.raises(ValidationError):
        AccessorDerivedResumeContext.from_pause_state(
            pause_state,
            effect_fence_resolutions={_EMPTY: EffectFenceResolution.ABORT},
        )


def test_pd8_probe_b_item_assignment_through_the_stored_mapping_is_refused() -> None:
    """PD-8 probe (b) — IMMUTABILITY. Fails if and only if the stored value stops being an
    immutable mapping (e.g. the validator returns a plain `dict` copy).

    `frozen=True` on the model is NOT sufficient and is deliberately not relied on: it
    forbids rebinding the FIELD, not mutating the nested container. The named
    `context.effect_fence_resolutions[""] = ...` shape the fork found ACCEPTED at HEAD is
    the first assertion; a non-empty key is asserted too so this probe fails on ANY loss of
    immutability rather than only on the empty-key path (which probe (a) already owns)."""
    context = ResumeContext(effect_fence_resolutions={_KEYED: EffectFenceResolution.RE_FIRE})
    stored = context.effect_fence_resolutions
    assert stored is not None
    with pytest.raises(TypeError):
        stored[_EMPTY] = EffectFenceResolution.ABORT  # type: ignore[index]
    with pytest.raises(TypeError):
        stored["another-key"] = EffectFenceResolution.ABORT  # type: ignore[index]
    # Every OTHER mutation route is refused too — a `dict` subclass would otherwise leave
    # `update` / `|=` / `pop` / `setdefault` / `clear` wide open. `|=` in particular mutates
    # IN PLACE before any frozen-field re-assignment could raise.
    for mutate in (
        lambda: stored.update({"u": EffectFenceResolution.ABORT}),  # type: ignore[union-attr]
        lambda: stored.__ior__({"i": EffectFenceResolution.ABORT}),  # type: ignore[attr-defined]
        lambda: stored.pop(_KEYED),  # type: ignore[union-attr]
        lambda: stored.popitem(),  # type: ignore[union-attr]
        lambda: stored.setdefault("s", EffectFenceResolution.ABORT),  # type: ignore[union-attr]
        lambda: stored.clear(),  # type: ignore[union-attr]
        lambda: stored.__delitem__(_KEYED),  # type: ignore[attr-defined]
    ):
        with pytest.raises(TypeError):
            mutate()
    # out-of-family Codex round 2 [P2], reproduced before fixing: `dict.__init__` on a LIVE
    # instance UPDATES it in place (it does not clear first), so leaving it inherited left
    # `ctx.effect_fence_resolutions.__init__({...})` as a mutation route the disabled
    # item/update methods did not cover — it really did inject a key and change a later
    # `effect_fence_resolution_for` answer. Unlike `dict.__setitem__(obj, ...)` this names no
    # base class, so it is a route the type EXPOSES in the §1.2 sense.
    with pytest.raises(TypeError):
        stored.__init__({"reinit": EffectFenceResolution.ABORT})  # type: ignore[misc]
    # The SEAL itself must not be reopenable by ordinary attribute assignment, or
    # `stored._sealed = False; stored.__init__({...})` walks straight back in (Codex round 3
    # [P2], reproduced before fixing). `__slots__` + a refusing `__setattr__` closes it; the
    # residual `object.__setattr__` route explicitly names a base class, the same boundary
    # §1.5 already draws for `model_construct`.
    with pytest.raises(TypeError):
        stored._sealed = False  # type: ignore[attr-defined, union-attr]
    with pytest.raises(TypeError):
        del stored._sealed  # type: ignore[attr-defined, union-attr]
    assert not hasattr(stored, "__dict__"), "a `__dict__` would reintroduce the writable seal"
    assert dict(stored) == {_KEYED: EffectFenceResolution.RE_FIRE}
    assert context.effect_fence_resolution_for("reinit") is None
    assert context.effect_fence_resolution_for(_EMPTY) is None


def test_pd8_probe_c_mutating_the_callers_original_mapping_cannot_change_the_stored_one() -> None:
    """PD-8 probe (c) — COPYING. Fails if and only if the `dict(supplied)` copy is removed.

    A proxy or view over a CALLER-RETAINED mapping does not satisfy §1.2: the caller would
    still hold a live mutation route into the model's state, including a route that injects
    the very empty key probe (a) refuses. This probe survives the loss of immutability (a
    plain-dict copy still isolates) and the loss of validation, so it fails independently of
    probes (a) and (b).

    **Two halves, because the model-level half is over-determined and saying otherwise would
    be a false witness.** Verified at this leg: pydantic's `dict[...]` validation already
    materializes a fresh mapping before the field validator runs, so the model-level half
    (below) passes even with the explicit copy removed — it witnesses the OBSERVABLE
    contract, not the mechanism. The DISCRIMINATING half exercises
    `_validate_effect_fence_resolution_map` directly with a caller-retained mapping, which is
    exactly the shape §1.2 forbids and exactly what an annotation change (a
    `BeforeValidator`, a passthrough type) would start handing it.

    **Honest limit on independence.** Because the immutable carrier's own constructor is
    what copies, "copying" and "immutability" are one mechanism, not two: the mutation that
    breaks this probe (returning the supplied mapping unchanged) also breaks probe (b). That
    is a property of the chosen carrier — a live view over caller state is structurally
    unrepresentable — not a gap in the probe. Probes (a) and (d)/(d2) remain independently
    discriminated."""
    from harness_cp.pause_resume_protocol_types import _validate_effect_fence_resolution_map

    # Half 1 (DISCRIMINATING) — the copy stated where the contract states it.
    retained: dict[str, EffectFenceResolution] = {_KEYED: EffectFenceResolution.RE_FIRE}
    validated = _validate_effect_fence_resolution_map(retained)
    retained[_EMPTY] = EffectFenceResolution.ABORT
    retained[_KEYED] = EffectFenceResolution.SKIP_AS_FIRED
    assert dict(validated) == {_KEYED: EffectFenceResolution.RE_FIRE}, (
        "the validated mapping must be a COPY, never a view over the supplied one"
    )

    # Half 2 (observable contract, over-determined) — end-to-end through the model.
    caller_map = {_KEYED: EffectFenceResolution.RE_FIRE}
    context = ResumeContext(effect_fence_resolutions=caller_map)

    caller_map[_EMPTY] = EffectFenceResolution.ABORT
    caller_map[_KEYED] = EffectFenceResolution.SKIP_AS_FIRED
    caller_map["late-key"] = EffectFenceResolution.ABORT

    stored = context.effect_fence_resolutions
    assert stored is not None
    assert dict(stored) == {_KEYED: EffectFenceResolution.RE_FIRE}
    assert context.effect_fence_resolution_for(_KEYED) is EffectFenceResolution.RE_FIRE
    assert context.effect_fence_resolution_for("late-key") is None
    assert context.effect_fence_resolution_for(_EMPTY) is None


def test_pd8_probe_d_a_valid_pre_amendment_map_keeps_its_bytes_and_its_meaning() -> None:
    """PD-8 probe (d) — VALID-MAP SERIALIZATION COMPATIBILITY (§0.3). Fails if and only if
    the stored value stops being a `dict` pydantic-core can serialize natively.

    Asserts byte-identical serialized logical content in BOTH dump modes against literals,
    a clean re-validation round trip, and unchanged resolution meaning — the whole point of
    §0.3's "existing valid maps retain their bytes and resolution meaning". A first draft of
    this amendment stored a `MappingProxyType`, which has no pydantic-core serializer: every
    dump emitted the raw proxy with a serializer warning and `model_dump_json` raised. This
    probe is what pins that shape out."""
    context = ResumeContext(
        effect_fence_resolutions={
            "k0": EffectFenceResolution.SKIP_AS_FIRED,
            "k1": EffectFenceResolution.RE_FIRE,
        },
        effect_fence_resolution=EffectFenceResolution.ABORT,
    )

    dumped = context.model_dump()
    assert isinstance(dumped["effect_fence_resolutions"], dict)
    assert dumped["effect_fence_resolutions"] == {
        "k0": EffectFenceResolution.SKIP_AS_FIRED,
        "k1": EffectFenceResolution.RE_FIRE,
    }
    assert context.model_dump(mode="json")["effect_fence_resolutions"] == {
        "k0": "skip_as_fired",
        "k1": "re_fire",
    }
    assert '"effect_fence_resolutions":{"k0":"skip_as_fired","k1":"re_fire"}' in (
        context.model_dump_json()
    )

    restored = ResumeContext.model_validate(context.model_dump(mode="json"))
    assert restored == context
    assert restored.effect_fence_resolution_for("k0") is EffectFenceResolution.SKIP_AS_FIRED
    assert restored.effect_fence_resolution_for("k1") is EffectFenceResolution.RE_FIRE
    assert restored.effect_fence_resolution_for("absent") is EffectFenceResolution.ABORT

    # `None` (the default) is untouched by the amendment — the v1.65 byte-identical shape.
    assert ResumeContext().model_dump()["effect_fence_resolutions"] is None
    assert '"effect_fence_resolutions":null' in ResumeContext().model_dump_json()


def test_pd8_probe_d2_a_valid_map_still_deep_copies_and_pickles() -> None:
    """PD-8 probe (d2) — CLONE + TRANSPORT COMPATIBILITY (§0.3), the sibling of probe (d).

    Out-of-family Codex [P2], caught before merge: the first draft of this amendment stored
    a `MappingProxyType`, which made `copy.deepcopy(context)`, `context.model_copy(deep=True)`
    and `pickle` of ANY context carrying a VALID map raise `TypeError: cannot pickle
    'mappingproxy' object`. §0.3 authorizes exactly three compatibility costs — a supplied
    `""`, a post-construction mutation, and a retained-alias mutation — and breaking clone /
    transport of an ordinary valid map is none of them.

    Fails if and only if `_ImmutableEffectFenceResolutions.__reduce__` is removed or the
    carrier is swapped back to a non-picklable proxy. Each clone must ALSO stay immutable,
    so the fix cannot be "make it copyable by making it a plain dict"."""
    import copy
    import pickle

    context = ResumeContext(
        effect_fence_resolutions={"k0": EffectFenceResolution.SKIP_AS_FIRED},
        effect_fence_resolution=EffectFenceResolution.ABORT,
    )
    clones = {
        "deepcopy": copy.deepcopy(context),
        "model_copy_deep": context.model_copy(deep=True),
        "model_copy_shallow": context.model_copy(),
        "pickle": pickle.loads(pickle.dumps(context)),
    }
    for label, clone in clones.items():
        assert clone == context, label
        stored = clone.effect_fence_resolutions
        assert stored is not None, label
        assert dict(stored) == {"k0": EffectFenceResolution.SKIP_AS_FIRED}, label
        assert clone.effect_fence_resolution_for("k0") is EffectFenceResolution.SKIP_AS_FIRED
        with pytest.raises(TypeError):
            stored["injected"] = EffectFenceResolution.ABORT  # type: ignore[index]


# ===========================================================================
# CLAUSE 4 — `model_construct` forged-context inertness (§1.5)
# ===========================================================================


@pytest.mark.parametrize("empty_at", [0, 1])
def test_forged_model_construct_empty_map_key_is_inert_and_keyed_sibling_survives(
    empty_at: int,
) -> None:
    """§1.5 — a validation-BYPASSED `ResumeContext` is outside B-107's closure criterion but
    MUST be inert under §1.3: no directive threaded for the empty-key location, and a keyed
    sibling's directive survives. No diagnostic is required for the forged object.

    e2e at the PARALLELIZATION fan-out (both carrier orders), which exercises the ungated
    level-local `_any_fence_abort` scan as well as the per-branch consult. That scan is what
    makes this a real defence-in-depth witness rather than a restatement of the truthiness
    gate: without the resolver guard the forged `{"": ABORT}` entry would resolve to ABORT
    inside the scan, flip the run-level ABORT suppression on, and NULL the keyed sibling's
    `SKIP_AS_FIRED` directive — the empty key silently overriding a location it never
    addressed."""
    snap = _capture_peer_fence_pause(empty_at=empty_at)
    forged = ResumeContext.model_construct(
        effect_fence_resolution=None,
        effect_fence_resolutions={
            _EMPTY: EffectFenceResolution.ABORT,
            _KEYED: EffectFenceResolution.SKIP_AS_FIRED,
        },
        hitl_response=None,
        hitl_responses=None,
    )
    assert forged.effect_fence_resolutions is not None
    assert _EMPTY in forged.effect_fence_resolutions, "the forged object really does carry it"

    result, dispatcher = _resume_peer(snap=snap, resume_context=forged, empty_at=empty_at)
    keyed_directive = dispatcher.seen_directives[f"branch-{1 - empty_at}"]
    assert keyed_directive is not None, "the forged empty key must not suppress the sibling"
    assert keyed_directive.resolution is EffectFenceResolution.SKIP_AS_FIRED
    assert keyed_directive.idempotency_key == _KEYED
    assert dispatcher.seen_directives[f"branch-{empty_at}"] is None
    assert result.status is RunStatus.PAUSED


# ===========================================================================
# CLAUSE 5 — programmatic resolver-reader inventory
# ===========================================================================

_EXPECTED_RESOLVER_CALL_SITES: dict[str, int] = {
    # enclosing function -> number of `_resolve_effect_fence_gated(...)` calls
    "compute_effect_fence_tree_wide_abort_present": 1,  # pre-filters empties itself
    "_execute_workflow_body": 1,  # LINEAR reconstruction site — UNGATED
    "_execute_parallelization": 2,  # level-local abort scan (UNGATED) + per-branch (gated)
    "_execute_orchestrator_workers": 3,  # abort scan (UNGATED) + orch-own + per-worker (gated)
}
"""The plan v2.49 clause-5 binding rule's reader inventory AT THIS REVISION: seven resolver
call sites. Re-derived programmatically below rather than asserted from a stale count, so a
new consult site fails this test until it is classified and witnessed."""

_TERMINAL_KEY_MATCH_CONSUMERS: tuple[str, ...] = (
    "harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py",
    "harness-runtime/src/harness_runtime/lifecycle/managed_agents_dispatch.py",
)
"""The two NON-TEST terminal consumers of a threaded directive: each compares
`step_context.effect_fence_resolution.idempotency_key` against its OWN composed key. Both
compose a SHA-256 hex digest, so neither can ever match `""` — they are inventoried (this is
a `harness-cp` unit, so they are read as files, never imported) but need no change."""


def _resolver_call_sites_by_enclosing_function() -> dict[str, int]:
    tree = ast.parse(inspect.getsource(_workflow_driver_module))
    counts: dict[str, int] = {}
    stack: list[str] = []

    class _Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            func = node.func
            if isinstance(func, ast.Name) and func.id == "_resolve_effect_fence_gated":
                owner = stack[-1] if stack else "<module>"
                counts[owner] = counts.get(owner, 0) + 1
            self.generic_visit(node)

    _Visitor().visit(tree)
    return counts


def test_every_resolver_call_site_is_inventoried_at_seven() -> None:
    """Clause 5 — re-derive the reader set PROGRAMMATICALLY, not from recall.

    Seven `_resolve_effect_fence_gated` call sites at this revision. A new consult site added
    by a later arc breaks this test on purpose: B-107's binding rule is stated over EVERY
    reader, so an un-inventoried reader is an un-witnessed one. The guard now lives INSIDE
    the resolver, so a new site inherits the property — but the classification (gated vs
    ungated, and therefore which cell witnesses it) still has to be made deliberately."""
    derived = _resolver_call_sites_by_enclosing_function()
    assert derived == _EXPECTED_RESOLVER_CALL_SITES
    assert sum(derived.values()) == 7


def test_the_two_terminal_key_match_consumers_are_inventoried_and_unchanged() -> None:
    """Clause 5 — the two non-test terminal consumers of a threaded directive.

    Read as FILES: this is a `harness-cp` unit and `harness-runtime` depends on `harness-cp`,
    so importing them would invert the workspace dependency graph. Each compares the
    directive's `idempotency_key` against a key it composes itself as a SHA-256 hex digest,
    which is never empty — so no runtime-side change is owed by B-107, and this test pins
    that reasoning against a future consumer that keys differently."""
    repo_root = Path(__file__).resolve().parents[2]
    for relative in _TERMINAL_KEY_MATCH_CONSUMERS:
        source = (repo_root / relative).read_text(encoding="utf-8")
        assert "effect_fence_resolution.idempotency_key == idempotency_key" in source, (
            f"{relative} no longer key-matches the threaded directive as inventoried"
        )

    scanned = sorted(
        path
        for path in (repo_root / "harness-runtime" / "src").rglob("*.py")
        if "effect_fence_resolution.idempotency_key" in path.read_text(encoding="utf-8")
    )
    assert [str(path.relative_to(repo_root)) for path in scanned] == sorted(
        _TERMINAL_KEY_MATCH_CONSUMERS
    )

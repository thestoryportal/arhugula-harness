"""B-18-FENCE-LEDGER-FIDELITY-OW — the §25.15.2 obligation-4 scan extended to the
ORCHESTRATOR_WORKERS engine (CP spec v1.93; DDR at
`.harness/b18-fence-ledger-fidelity-ow-design-decision-record.md` §6+§7).

The engine's inline CASCADE_CANCEL-only loop is factored into an O-W-local
`_synthesize_undispatched_terminals()` with six arms (aborted-first → fence
this-round + capture → fence recovered capture-less → paused-child this-round
capture-less → paused-child recovered capture-less → else `cancelled`), called at
seven terminal exits — the counts as of this arc's authoring (CP spec v1.93);
the v1.94 reconstruct-residual arc later added the reconstruct arms + the
EIGHTH call site. At this arc's authoring O-W had NO warm-up serialization
lever (B-18-PREWARM-OW / CP spec v1.96 later added the §25.19 partition — its
withheld-follower witnesses live at
`test_workflow_driver_orchestrator_workers_warmup.py`; these gate-False
witnesses keep the poisoned-ordinal mechanism), and a sibling's
raise never deterministically cancels later tasks pre-body (the TaskGroup abort
runs via a done-callback queued AFTER their first steps — verified empirically),
so the deterministic zero-footprint ordinal is the POISONED ordinal itself: a
registry whose lookup raises synchronously fails that worker before its marker +
dispatch (the pre-arc CC-scan tests' mechanism). The union-arm witnesses poison
the RECOVERED peers' own kind — "a recovered peer whose re-dispatch fails at
lookup" — which lands in the same absence-keyed arms the race-only
sibling-withheld shape reaches in production.

  OW1 (FL1+FL4+FL7 analogues) — fence-ABORT exit on a resume round: aborted
  ordinal (∈ aborted ∩ recovered by construction) `completed` terminal-ONLY /
  NO capture (arm order); suppressed INERT re-paused peer `completed` + store
  capture (named crash-visible addition #1):
    → test_ow_fence_abort_exit_aborted_no_capture_inert_peer_captured
  OW4 (FL3b + third-class union) — CASCADE_CANCEL exit on a persona-tier-change
  resume round: two recovered fence peers + one recovered paused-child peer
  whose re-dispatches all fail at LOOKUP (zero footprint) — all three record
  `completed` capture-less (never `cancelled`); store + markers
  byte-unchanged; the recovered-terminal worker records nothing:
    → test_ow_cascade_cancel_union_arm_recovered_fence_and_child_completed
  OW5 — PROCEED paused-child FAILED exit (O-W-specific; no parallelization
  analogue): the stashed child itself records `completed` terminal-ONLY,
  capture-less:
    → test_ow_proceed_child_paused_failed_exit_records_completed
  OW6a — PAUSE protocol-not-bound exit, same union construction as OW4:
    → test_ow_protocol_not_bound_union_arm_completed_no_snapshot
  OW6b — PAUSE protocol-not-bound exit, this-round fence peer: `completed` +
  store capture (named crash-visible addition #2):
    → test_ow_protocol_not_bound_this_round_fence_peer_captured
  OW8a — containment: fresh CASCADE_CANCEL baseline byte-preserved (both
  workers lookup-poisoned → both `cancelled`, exactly the pre-arc inline
  outputs):
    → test_ow_baseline_cascade_cancel_cancelled_only_byte_preserved
  OW8b — containment: worker-failure → PAUSED boundary stays SCAN-FREE on a
  resume round (lookup-failed recovered peers re-dispatchable by snapshot
  omission; zero synthesized terminals):
    → test_ow_paused_boundary_scan_free_recovered_peers_omitted
  OW9 — PAUSE not-yet-materialized exit (defence-in-depth; direct engine call,
  no live caller passes pause_resumable=False): fence stash captured + poisoned
  sibling `cancelled`:
    → test_ow_not_yet_materialized_direct_call_scan_runs
  OW10 (review finding 1) — PROCEED deadline exit with a stashed paused-child
  (stash-then-deadline interleaving exits through the merged E3 handler BEFORE
  the paused-child check): child records `completed` terminal-ONLY; the
  in-flight-cut sibling keeps its own `timed_out`:
    → test_ow_proceed_deadline_stashed_child_completed_not_cancelled

Authority: CP spec v1.92 item 7 (registration) + v1.93 (this arc);
`Spec_Control_Plane_v1_91.md` items 2–5 (M2 scan discipline);
`.harness/b18-fence-ledger-fidelity-ow-design-decision-record.md`
(pre-build Fable-5 adversarial design review: VERDICT AMEND, 0 blocking,
all findings folded).
"""

from __future__ import annotations

import asyncio
import threading
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
    EffectFenceResolution,
    PauseSnapshot,
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
    _execute_orchestrator_workers,
    execute_workflow,
    resume_should_redispatch,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
    SubAgentChildPausedError,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Identifier

# ---------------------------------------------------------------------------
# Shared fixtures (local twins of the warmup-file harness, O-W-shaped)
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
    persona_tier: PersonaTier,
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
    workflow_id: str = "wf-ow-fl",
) -> WorkflowManifestEntry:
    """ORCHESTRATOR_WORKERS manifest. SOLO_DEVELOPER → PROCEED / TEAM_BINDING →
    PAUSE / MULTI_TENANT_COMPLIANCE → CASCADE_CANCEL; the store-bound capture
    witnesses pass EVENT_SOURCED_REPLAY."""
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=engine_class,
        topology_pattern=TopologyPattern.ORCHESTRATOR_WORKERS,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _orch_step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("orchestrator"),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"role": "orchestrator"},
    )


def _worker(index: int, *, kind: StepKind = StepKind.INFERENCE_STEP) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"worker-{index}"),
        step_kind=kind,
        step_payload={"index": index},
    )


class _RecordingLedger:
    """In-memory ledger sink that records drained appends."""

    def __init__(self) -> None:
        from harness_is.state_ledger_entry_schema import Actor, ActorClass

        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-ow-fl")
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
    """Minimal fake DriverContext for ORCHESTRATOR_WORKERS e2e (the warmup-file
    twin; `pause_resume_protocol` / `engine_output_store` bound only where the
    witness needs a snapshot / durable marker-capture assertions)."""

    def __init__(
        self,
        *,
        ledger: Any,
        emitter: _Emitter,
        pause_resume_protocol: Any = None,
        engine_output_store: Any = None,
        resume_context_holder: Any = None,
    ) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = emitter
        self.drained_flag = asyncio.Event()
        self.pause_resume_protocol = pause_resume_protocol
        self.pause_requested_flag = asyncio.Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.engine_output_store = engine_output_store
        self.resume_context_holder = resume_context_holder


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


def _protocol() -> PauseResumeProtocol:
    return PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=_pause_context_reader,
    )


class _MiniOWStore:
    """Minimal in-memory EngineOutputStore fake covering the ORCHESTRATOR_WORKERS
    produce surface these witnesses touch (the warmup-file `_MiniFanoutStore`
    plus the orchestrator reserve/capture producer methods the O-W engine calls
    on a fresh strict-tier run)."""

    def __init__(self) -> None:
        self._branches: dict[str, dict[int, tuple[str, str, dict[str, Any] | None]]] = {}
        self._cardinality: dict[str, int] = {}
        self._instrumented: set[str] = set()
        self._dispatched: dict[str, dict[int, str | None]] = {}
        self._dispatched_step_id: dict[str, dict[int, str | None]] = {}
        self._orchestrator: dict[str, tuple[str, dict[str, Any]]] = {}
        self._orch_marker: dict[str, tuple[str, str]] = {}

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

    def record_orchestrator_dispatched(
        self, run_key: str, step_id: str, step_kind: str, **_kwargs: Any
    ) -> None:
        self._orch_marker[run_key] = (str(step_id), str(step_kind))

    def record_orchestrator(self, run_key: str, step_id: str, output: dict[str, Any]) -> None:
        self._orchestrator[run_key] = (str(step_id), dict(output))

    def record_synthesis(
        self, run_key: str, step_id: str, output: dict[str, Any], self_hash: str
    ) -> None:
        _ = (run_key, step_id, output, self_hash)

    # -- consumer surface (crash-resume classification; inert for these
    # operator-resume witnesses but kept honest where cheap) --
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
        return run_key in self._orchestrator

    def read_orchestrator_output(self, run_key: str) -> tuple[str, dict[str, Any]] | None:
        return self._orchestrator.get(run_key)

    def orchestrator_dispatched(self, run_key: str) -> bool:
        return run_key in self._orch_marker

    def orchestrator_dispatched_kind(self, run_key: str) -> str | None:
        marker = self._orch_marker.get(run_key)
        return marker[1] if marker is not None else None

    def orchestrator_dispatched_step_id(self, run_key: str) -> str | None:
        marker = self._orch_marker.get(run_key)
        return marker[0] if marker is not None else None

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


# ---------------------------------------------------------------------------
# Errors (test-local name-matched stand-ins), holders, registries, dispatchers
# ---------------------------------------------------------------------------


class EffectFenceAmbiguousUncommittedError(Exception):
    """Test-local stand-in for the runtime fence's ambiguous error (C-RT-31
    §14.22) — the driver name-matches `type(exc).__name__`."""

    def __init__(self, *, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__(f"ambiguous (key={idempotency_key!r})")


class EffectFenceAbortedError(Exception):
    """Test-local stand-in for the runtime fence's operator-ABORT error."""


class _HolderWithResolutions:
    """Stand-in ResumeContextHolder — `peek()` returns a ResumeContext carrying a
    per-key `effect_fence_resolutions` map (non-consuming peek contract)."""

    def __init__(self, resolutions: dict[str, EffectFenceResolution]) -> None:
        self._rc = ResumeContext(effect_fence_resolutions=resolutions)
        self.peeked = 0

    def peek(self) -> ResumeContext:
        self.peeked += 1
        return self._rc


class _KindMap:
    """Registry mapping step kinds to dispatchers; kinds in `poison` (or unmapped)
    raise `StepKindDispatcherNotBoundError` SYNCHRONOUSLY at lookup — the worker
    body's FIRST line, so the poisoned ordinal itself deterministically fails
    before its dispatch marker + dispatch fire (zero footprint, no marker)."""

    def __init__(
        self,
        mapping: dict[StepKind, Any],
        *,
        poison: frozenset[StepKind] = frozenset(),
    ) -> None:
        self._mapping = mapping
        self._poison = poison

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind in self._poison or step_kind not in self._mapping:
            raise StepKindDispatcherNotBoundError(step_kind)
        return cast(StepDispatcher, self._mapping[step_kind])


class _Echo:
    """Clean dispatcher (the orchestrator + `ok` workers)."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        return dict(step.step_payload)


class _ScriptedWorker:
    """Round-1 per-ordinal behavior: `ok` returns; `fence` raises the ambiguous
    error with key `fence-key-attempt1-{i}`; `child` raises
    `SubAgentChildPausedError` carrying `child_snapshot`; `fail` raises a plain
    RuntimeError; `block` waits `block_seconds` (self-releasing). Ordinals in
    `barrier_indexes` synchronize on one barrier BEFORE acting, so every stash
    raise happens with the others' dispatches in flight (deterministic
    composition through the TaskGroup shield)."""

    def __init__(
        self,
        script: dict[int, str],
        *,
        barrier_indexes: frozenset[int] = frozenset(),
        child_snapshot: PauseSnapshot | None = None,
        block_seconds: float = 1.2,
    ) -> None:
        self._script = script
        self._barrier = (
            threading.Barrier(len(barrier_indexes), timeout=10.0) if barrier_indexes else None
        )
        self._barrier_indexes = barrier_indexes
        self._child_snapshot = child_snapshot
        self._block_seconds = block_seconds
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if self._barrier is not None and idx in self._barrier_indexes:
            self._barrier.wait()
        action = self._script[idx]
        if action == "fence":
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-attempt1-{idx}")
        if action == "child":
            assert self._child_snapshot is not None
            raise SubAgentChildPausedError(
                child_workflow_id="wf-child", child_snapshot=self._child_snapshot
            )
        if action == "fail":
            raise RuntimeError(f"simulated plain worker-{idx} failure")
        if action == "block":
            threading.Event().wait(self._block_seconds)  # self-releasing — no leaked thread
        return {"index": idx}


class _DirectiveReactor:
    """Resume-side: reacts to the threaded per-worker `EffectFenceResolutionDirective`
    the way the runtime fence would — ABORT raises the test-local abort error; a
    None/suppressed directive INERT re-pauses (re-raises the ambiguous error with a
    THIS-round key); otherwise fires. `barrier_indexes` as in `_ScriptedWorker`."""

    def __init__(self, *, barrier_indexes: frozenset[int] = frozenset()) -> None:
        self._barrier = (
            threading.Barrier(len(barrier_indexes), timeout=10.0) if barrier_indexes else None
        )
        self._barrier_indexes = barrier_indexes
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if self._barrier is not None and idx in self._barrier_indexes:
            self._barrier.wait()
        directive = getattr(step_context, "effect_fence_resolution", None)
        if directive is None:
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-inert-{idx}")
        if directive.resolution is EffectFenceResolution.ABORT:
            raise EffectFenceAbortedError(f"operator aborted worker-{idx}")
        return {"index": idx}


class _NeverDispatch:
    """Poison-withheld ordinals must never reach dispatch."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        raise AssertionError(f"worker {step.step_id} dispatched — expected withheld")


# ---------------------------------------------------------------------------
# Ledger helpers + the shared runner
# ---------------------------------------------------------------------------


def _branch_terminals(ledger: _RecordingLedger) -> dict[int, str]:
    out: dict[int, str] = {}
    for payload, _wk in ledger.appends:
        meta = getattr(payload, "branch_metadata", None)
        if meta is not None and meta.terminal_status is not None:
            out[meta.branch_index] = meta.terminal_status
    return out


def _branch_terminal_statuses(ledger: _RecordingLedger, branch_index: int) -> list[str]:
    return [
        payload.branch_metadata.terminal_status
        for payload, _wk in ledger.appends
        if getattr(payload, "branch_metadata", None) is not None
        and payload.branch_metadata.branch_index == branch_index
        and payload.branch_metadata.terminal_status is not None
    ]


def _branch_step_indexes(ledger: _RecordingLedger) -> set[int]:
    return {
        payload.branch_metadata.branch_index
        for payload, _wk in ledger.appends
        if getattr(payload, "branch_metadata", None) is not None
        and payload.branch_metadata.terminal_status is None
    }


def _run(
    *,
    steps: list[WorkflowStep],
    registry: _KindMap,
    persona_tier: PersonaTier,
    ledger: _RecordingLedger | None = None,
    emitter: _Emitter | None = None,
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
    store: Any = None,
    with_pause_protocol: bool = False,
    pause_snapshot_input: PauseSnapshot | None = None,
    resume_context_holder: Any = None,
    workflow_id: str = "wf-ow-fl",
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
        ),
    )
    return execute_workflow(
        _manifest(persona_tier=persona_tier, engine_class=engine_class, workflow_id=workflow_id),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, registry),
        pause_snapshot_input=pause_snapshot_input,
    )


def _child_pause_snapshot() -> PauseSnapshot:
    """A hash-valid linear child PauseSnapshot (captured through the real
    protocol) for `SubAgentChildPausedError` stashes."""
    return asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id="wf-child",
            run_id="child-run",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        )
    )


# ---------------------------------------------------------------------------
# Round-1 builders (fence / mixed pause rounds)
# ---------------------------------------------------------------------------


def _fence_pause_round1(store: _MiniOWStore) -> tuple[PauseSnapshot, dict[int, str]]:
    """OW1/OW8b round 1: TEAM_BINDING (PAUSE) + protocol + durable store.
    Workers: w0 completes; w1 + w2 fence-stash (barrier parties=2) → PAUSED with
    branches={0}, fence={1, 2}. Returns (snapshot, reserve keys)."""
    dispatcher = _ScriptedWorker(
        {0: "ok", 1: "fence", 2: "fence"}, barrier_indexes=frozenset({1, 2})
    )
    registry = _KindMap({StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: dispatcher})
    paused = _run(
        steps=[_orch_step(), _worker(0), _worker(1), _worker(2)],
        registry=registry,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None
    fr = snapshot.fan_out_resume
    assert fr is not None
    assert [(b.branch_index, b.terminal_status) for b in fr.branches] == [(0, "completed")]
    key_by_index = {b.branch_index: b.idempotency_key for b in fr.effect_fence_paused_branches}
    assert key_by_index == {1: "fence-key-attempt1-1", 2: "fence-key-attempt1-2"}
    run_key = store.sole_run_key()
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2}
    assert store.present_branch_indexes(run_key) == {0}
    return snapshot, key_by_index


def _mixed_pause_round1(store: _MiniOWStore) -> PauseSnapshot:
    """OW4/OW6a round 1: TEAM_BINDING (PAUSE) + protocol + durable store.
    Workers w0 + w1 fence-stash and w2 child-stashes (barrier parties=3), all
    THREE on the TOOL_STEP kind (so the resume round can fail all three
    re-dispatches synchronously at lookup by poisoning that one kind); w3
    (INFERENCE) completes → PAUSED with branches={3}, fence={0, 1},
    paused-child={2}."""
    dispatcher = _ScriptedWorker(
        {0: "fence", 1: "fence", 2: "child", 3: "ok"},
        barrier_indexes=frozenset({0, 1, 2}),
        child_snapshot=_child_pause_snapshot(),
    )
    registry = _KindMap(
        {
            StepKind.DECLARATIVE_STEP: _Echo(),
            StepKind.INFERENCE_STEP: dispatcher,
            StepKind.TOOL_STEP: dispatcher,
        }
    )
    paused = _run(
        steps=[
            _orch_step(),
            _worker(0, kind=StepKind.TOOL_STEP),
            _worker(1, kind=StepKind.TOOL_STEP),
            _worker(2, kind=StepKind.TOOL_STEP),
            _worker(3),
        ],
        registry=registry,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None
    fr = snapshot.fan_out_resume
    assert fr is not None
    assert [(b.branch_index, b.terminal_status) for b in fr.branches] == [(3, "completed")]
    assert {b.branch_index for b in fr.effect_fence_paused_branches} == {0, 1}
    assert [b.branch_index for b in fr.paused_child_branches] == [2]
    run_key = store.sole_run_key()
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2, 3}
    assert store.present_branch_indexes(run_key) == {3}
    return snapshot


# ---------------------------------------------------------------------------
# OW1 — fence-ABORT exit (E1): aborted arm + this-round INERT capture arm
# ---------------------------------------------------------------------------


def test_ow_fence_abort_exit_aborted_no_capture_inert_peer_captured() -> None:
    """OW1 (FL1+FL4+FL7 analogues): resume a 2-peer O-W fence pause with
    {worker-1: ABORT}. The 9916 run-level guard suppresses worker-2's non-ABORT
    directive → its re-dispatch INERT re-raises (this-round fence stash); both
    dispatch (barrier), worker-1 raises the abort → the fence-ABORT terminal
    exit now runs the obligation-4 scan BEFORE the unchanged FAILED return.

      worker-1 (∈ aborted ∩ recovered — the directive is BUILT from the
      recovered dict) → ledger `completed` terminal-ONLY, no step entry, NO
      store capture (the aborted arm wins the arm order — never the fence-arm
      capture).
      worker-2 (this-round INERT re-pause) → ledger `completed` + store capture
      (named crash-visible addition #1 — the v1.65 §1(c) trade).
      steps_executed = 0 this round (terminal-only synthesis never inflates the
      STEP_BOUNDARY drain)."""
    store = _MiniOWStore()
    snapshot, key_by_index = _fence_pause_round1(store)
    run_key = store.sole_run_key()

    holder = _HolderWithResolutions({key_by_index[1]: EffectFenceResolution.ABORT})
    reactor = _DirectiveReactor(barrier_indexes=frozenset({1, 2}))
    registry = _KindMap({StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: reactor})
    ledger = _RecordingLedger()
    emitter = _Emitter()
    result = _run(
        steps=[_orch_step(), _worker(0), _worker(1), _worker(2)],
        registry=registry,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
        resume_context_holder=holder,
        ledger=ledger,
        emitter=emitter,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-effect-fence-aborted"
    assert result.pause_snapshot is None  # terminal — NOT a re-pause
    assert sorted(reactor.dispatched) == [1, 2]  # worker-0 recovered-skipped
    # Ledger: aborted arm (worker-1) + this-round INERT arm (worker-2), both
    # `completed`, both terminal-ONLY — exactly one terminal each, zero step
    # entries this round.
    assert _branch_terminals(ledger) == {1: "completed", 2: "completed"}
    assert _branch_terminal_statuses(ledger, 1) == ["completed"]
    assert _branch_terminal_statuses(ledger, 2) == ["completed"]
    assert _branch_step_indexes(ledger) == set()
    # Store: NO capture for aborted worker-1 (arm order); worker-2's capture IS
    # present (the named addition) — attempt-1's worker-0 record intact.
    assert store.present_branch_indexes(run_key) == {0, 2}
    assert store.read_branch_records(run_key)[2][1:] == ("completed", None)
    assert store.read_branch_records(run_key)[0][1] == "completed"
    # No worker ran a step this round → no worker STEP_BOUNDARY (orchestrator
    # not re-dispatched on resume).
    assert emitter.emits.count(WorkflowEventClass.STEP_BOUNDARY) == 0
    for status in _branch_terminals(ledger).values():
        assert resume_should_redispatch(status) is False


# ---------------------------------------------------------------------------
# OW4 — CASCADE_CANCEL exit (E2): the recovered union arm (fence + third class)
# ---------------------------------------------------------------------------


def test_ow_cascade_cancel_union_arm_recovered_fence_and_child_completed() -> None:
    """OW4 (FL3b + the third-class union): resume the mixed pause under
    MULTI_TENANT_COMPLIANCE (CASCADE_CANCEL — the persona-tier-change reach)
    with the TOOL_STEP kind POISONED: all three recovered peers' re-dispatches
    fail synchronously at lookup — each is a zero-footprint re-dispatchable
    ordinal at the terminal exit (the deterministic composition; the
    sibling-withheld variant is the same union arm reached by a race).

      worker-0 (recovered fence, lookup-failed)  → `completed` capture-less;
      worker-1 (recovered fence, lookup-failed)  → `completed` capture-less;
      worker-2 (recovered paused-child, lookup-failed) → `completed`
      capture-less (the NEW third-class half of the union arm — `cancelled`
      would contradict its attempt-1 dispatch marker);
      worker-3 (recovered terminal) is not re-dispatched and records nothing.
      Store + dispatch markers byte-unchanged from round 1."""
    store = _MiniOWStore()
    snapshot = _mixed_pause_round1(store)
    run_key = store.sole_run_key()

    registry = _KindMap(
        {StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: _NeverDispatch()},
        poison=frozenset({StepKind.TOOL_STEP}),
    )
    ledger = _RecordingLedger()
    result = _run(
        steps=[
            _orch_step(),
            _worker(0, kind=StepKind.TOOL_STEP),
            _worker(1, kind=StepKind.TOOL_STEP),
            _worker(2, kind=StepKind.TOOL_STEP),
            _worker(3),
        ],
        registry=registry,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
        ledger=ledger,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-cascade-cancel"
    # Union arms: all three re-dispatchable recovered peers → `completed`
    # (never `cancelled`), terminal-ONLY; recovered-terminal worker-3 absent.
    assert _branch_terminals(ledger) == {0: "completed", 1: "completed", 2: "completed"}
    for index in (0, 1, 2):
        assert _branch_terminal_statuses(ledger, index) == ["completed"]
    assert _branch_step_indexes(ledger) == set()
    # Store byte-unchanged: capture-less arms everywhere (worker-3's attempt-1
    # record only), markers still the attempt-1 set (lookup precedes the
    # re-mark, so not even worker-0 re-marked).
    assert store.present_branch_indexes(run_key) == {3}
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2, 3}


# ---------------------------------------------------------------------------
# OW5 — PROCEED paused-child FAILED exit (E4)
# ---------------------------------------------------------------------------


def test_ow_proceed_child_paused_failed_exit_records_completed() -> None:
    """OW5: under PROCEED (SOLO_DEVELOPER) a worker whose recursive child PAUSED
    drives the run to the honest FAILED
    `orchestrator-workers-child-paused-not-resumable-under-proceed` exit — which
    now runs the scan: the stashed child itself (zero footprint pre-arc) records
    `completed` terminal-ONLY (dispatch-boundary; its child paused mid-flight),
    capture-less."""
    store = _MiniOWStore()
    dispatcher = _ScriptedWorker({0: "ok", 1: "child"}, child_snapshot=_child_pause_snapshot())
    registry = _KindMap({StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: dispatcher})
    ledger = _RecordingLedger()
    emitter = _Emitter()
    result = _run(
        steps=[_orch_step(), _worker(0), _worker(1)],
        registry=registry,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        ledger=ledger,
        emitter=emitter,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-child-paused-not-resumable-under-proceed"
    # worker-0 ran a step + clean terminal; worker-1 (stashed child) synthesized
    # `completed` terminal-ONLY.
    assert _branch_terminals(ledger) == {0: "completed", 1: "completed"}
    assert _branch_step_indexes(ledger) == {0}
    assert _branch_terminal_statuses(ledger, 1) == ["completed"]
    # Capture-less arm: only clean worker-0 captured.
    run_key = store.sole_run_key()
    assert store.present_branch_indexes(run_key) == {0}
    # Orchestrator + worker-0 ran steps → exactly two STEP_BOUNDARYs.
    assert emitter.emits.count(WorkflowEventClass.STEP_BOUNDARY) == 2


# ---------------------------------------------------------------------------
# OW6a / OW6b — PAUSE protocol-not-bound exit (E7)
# ---------------------------------------------------------------------------


def test_ow_protocol_not_bound_union_arm_completed_no_snapshot() -> None:
    """OW6a: the union arms at the protocol-not-bound exit, driven by a DIRECT
    engine call — `execute_workflow` IGNORES `pause_snapshot_input` when no
    protocol is bound (workflow_driver.py:2541), so recovered peers at this exit
    are direct-call-reachable only (the same honest labeling as OW9; the fresh-
    run classes at this exit are OW6b's). All three recovered peers' poisoned
    re-dispatches → FAILED `protocol-not-bound`, three union-arm `completed`
    terminals (pre-arc: zero footprint), store byte-unchanged."""
    store = _MiniOWStore()
    snapshot = _mixed_pause_round1(store)
    run_key = store.sole_run_key()

    registry = _KindMap(
        {StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: _NeverDispatch()},
        poison=frozenset({StepKind.TOOL_STEP}),
    )
    ledger = _RecordingLedger()
    emitter = _Emitter()
    ctx = cast(
        DriverContext,
        _Ctx(ledger=ledger, emitter=emitter, engine_output_store=store),
    )
    result, _steps_executed = _execute_orchestrator_workers(
        manifest_entry=_manifest(
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        ),
        steps=[
            _orch_step(),
            _worker(0, kind=StepKind.TOOL_STEP),
            _worker(1, kind=StepKind.TOOL_STEP),
            _worker(2, kind=StepKind.TOOL_STEP),
            _worker(3),
        ],
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, registry),
        run_idempotency_key=run_key,
        resume_snapshot=snapshot,
        pause_resumable=True,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-pause-resume-protocol-not-bound"
    assert result.pause_snapshot is None
    assert _branch_terminals(ledger) == {0: "completed", 1: "completed", 2: "completed"}
    for index in (0, 1, 2):
        assert _branch_terminal_statuses(ledger, index) == ["completed"]
    assert _branch_step_indexes(ledger) == set()
    assert store.present_branch_indexes(run_key) == {3}


def test_ow_protocol_not_bound_this_round_fence_peer_captured() -> None:
    """OW6b: a FRESH PAUSE-tier round with no protocol bound: worker-0
    fence-stashes while worker-1 plain-fails (barrier — both dispatch) → FAILED
    `protocol-not-bound`; the scan records worker-0 `completed` + the durable
    store capture (named crash-visible addition #2 — without a snapshot the
    omission defense does not apply); worker-1 keeps its own step + `completed`
    from the plain-failure handler (the scan skips disposition-bearing
    writers)."""
    store = _MiniOWStore()
    dispatcher = _ScriptedWorker({0: "fence", 1: "fail"}, barrier_indexes=frozenset({0, 1}))
    registry = _KindMap({StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: dispatcher})
    ledger = _RecordingLedger()
    result = _run(
        steps=[_orch_step(), _worker(0), _worker(1)],
        registry=registry,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=False,
        ledger=ledger,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-pause-resume-protocol-not-bound"
    assert _branch_terminals(ledger) == {0: "completed", 1: "completed"}
    # worker-0 terminal-ONLY (fence stash recorded no step); worker-1 ran a step.
    assert _branch_step_indexes(ledger) == {1}
    assert _branch_terminal_statuses(ledger, 0) == ["completed"]
    # The capture arm fired for the this-round fence peer (worker-0) — worker-1's
    # capture is its own plain-failure handler's (both `completed`, no output).
    run_key = store.sole_run_key()
    assert store.present_branch_indexes(run_key) == {0, 1}
    assert store.read_branch_records(run_key)[0][1:] == ("completed", None)


# ---------------------------------------------------------------------------
# OW8a / OW8b — containment: baseline byte-preserved + PAUSED boundary scan-free
# ---------------------------------------------------------------------------


def test_ow_baseline_cascade_cancel_cancelled_only_byte_preserved() -> None:
    """OW8a: fresh CASCADE_CANCEL round with no fence/child history — both
    workers fail synchronously at lookup (the pre-arc deterministic
    all-cancelled-only cell); the factored scan reduces to the pre-arc inline
    outputs byte-exactly: both ordinals `cancelled`, terminal-only,
    resume-ineligible; only the orchestrator emits a STEP_BOUNDARY."""
    registry = _KindMap(
        {StepKind.DECLARATIVE_STEP: _Echo()},
        poison=frozenset({StepKind.TOOL_STEP}),
    )
    ledger = _RecordingLedger()
    emitter = _Emitter()
    result = _run(
        steps=[
            _orch_step(),
            _worker(0, kind=StepKind.TOOL_STEP),
            _worker(1, kind=StepKind.TOOL_STEP),
        ],
        registry=registry,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        ledger=ledger,
        emitter=emitter,
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-cascade-cancel"
    assert _branch_terminals(ledger) == {0: "cancelled", 1: "cancelled"}
    for index in (0, 1):
        assert _branch_terminal_statuses(ledger, index) == ["cancelled"]
    assert _branch_step_indexes(ledger) == set()
    assert emitter.emits.count(WorkflowEventClass.STEP_BOUNDARY) == 1
    for status in _branch_terminals(ledger).values():
        assert resume_should_redispatch(status) is False


def test_ow_paused_boundary_scan_free_recovered_peers_omitted() -> None:
    """OW8b (FL8/ML5 analogue): a resume round under the PAUSE tier (protocol
    BOUND) where both recovered fence peers' re-dispatches fail synchronously
    at lookup → PAUSED. The worker-failure → PAUSED boundary stays SCAN-FREE:
    zero branch entries this round; the new snapshot's fence set is composed
    from THIS-round dispositions only (empty), so both peers stay
    re-dispatchable by snapshot omission (the pre-existing contract)."""
    store = _MiniOWStore()
    snapshot, _keys = _fence_pause_round1(store)

    # Round 2: INFERENCE poisoned — both recovered peers' lookups raise
    # synchronously (zero footprint, no re-mark); protocol bound.
    registry = _KindMap(
        {StepKind.DECLARATIVE_STEP: _Echo()},
        poison=frozenset({StepKind.INFERENCE_STEP}),
    )
    ledger = _RecordingLedger()
    result = _run(
        steps=[_orch_step(), _worker(0), _worker(1), _worker(2)],
        registry=registry,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
        ledger=ledger,
    )

    assert result.status is RunStatus.PAUSED
    new_snapshot = result.pause_snapshot
    assert new_snapshot is not None
    fr = new_snapshot.fan_out_resume
    assert fr is not None
    # Scan-free boundary: NO synthesized terminals, NO step entries this round.
    assert _branch_terminals(ledger) == {}
    assert _branch_step_indexes(ledger) == set()
    # The re-pause snapshot carries the recovered terminal (worker-0) only;
    # workers 1 + 2 are re-dispatchable by omission (fence set composed from
    # this-round dispositions only — both empty this round).
    assert [(b.branch_index, b.terminal_status) for b in fr.branches] == [(0, "completed")]
    assert fr.effect_fence_paused_branches == ()
    assert fr.paused_child_branches == ()


# ---------------------------------------------------------------------------
# OW9 — PAUSE not-yet-materialized exit (E6; direct engine call)
# ---------------------------------------------------------------------------


def test_ow_not_yet_materialized_direct_call_scan_runs() -> None:
    """OW9: `pause_resumable=False` is reachable only by a direct engine call
    (both live callers pass True — defence-in-depth, honestly labeled). A worker
    fence-stashes in flight while its poisoned sibling fails synchronously at
    lookup (zero footprint): FAILED `not-yet-materialized`, and the scan runs —
    the fence stash records `completed` + capture (the finding-4 arm pin at this
    exit), the poisoned worker records `cancelled`."""
    store = _MiniOWStore()
    dispatcher = _ScriptedWorker({0: "fence"})
    registry = _KindMap(
        {StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: dispatcher},
        poison=frozenset({StepKind.TOOL_STEP}),
    )
    ledger = _RecordingLedger()
    emitter = _Emitter()
    ctx = cast(
        DriverContext,
        _Ctx(ledger=ledger, emitter=emitter, engine_output_store=store),
    )
    result, steps_executed = _execute_orchestrator_workers(
        manifest_entry=_manifest(
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        ),
        steps=[_orch_step(), _worker(0), _worker(1, kind=StepKind.TOOL_STEP)],
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, registry),
        run_idempotency_key="ow9-direct",
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-pause-resume-not-yet-materialized"
    # worker-0's in-flight fence raise landed via the shield → this-round fence
    # stash → `completed` + capture; poisoned worker-1 → `cancelled` ledger-only.
    assert _branch_terminals(ledger) == {0: "completed", 1: "cancelled"}
    assert _branch_terminal_statuses(ledger, 0) == ["completed"]
    assert _branch_terminal_statuses(ledger, 1) == ["cancelled"]
    assert _branch_step_indexes(ledger) == set()
    assert store.present_branch_indexes("ow9-direct") == {0}
    assert store.read_branch_records("ow9-direct")[0][1:] == ("completed", None)
    # Only the orchestrator ran a step.
    assert steps_executed == 1


# ---------------------------------------------------------------------------
# OW10 — PROCEED deadline exit (E3) with a stashed paused-child
# ---------------------------------------------------------------------------


def test_ow_proceed_deadline_stashed_child_completed_not_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OW10 (review finding 1): under PROCEED a stash-then-deadline interleaving
    exits through the merged deadline handler BEFORE the paused-child check —
    run PARTIAL unchanged (the pre-existing composition, named at v1.93); the
    stashed child records `completed` terminal-ONLY capture-less (never
    `cancelled` — its child paused mid-flight), while the in-flight-cut sibling
    keeps its own step + `timed_out` from its CancelledError handler."""
    import harness_cp.workflow_driver as workflow_driver_module

    monkeypatch.setattr(workflow_driver_module, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.3)
    store = _MiniOWStore()
    dispatcher = _ScriptedWorker(
        {0: "child", 1: "block"},
        child_snapshot=_child_pause_snapshot(),
        block_seconds=1.2,
    )
    registry = _KindMap({StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: dispatcher})
    ledger = _RecordingLedger()
    result = _run(
        steps=[_orch_step(), _worker(0), _worker(1)],
        registry=registry,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        ledger=ledger,
    )

    assert result.status is RunStatus.PARTIAL
    assert result.fail_class is None
    # worker-0 (stashed child) → synthesized `completed`, terminal-ONLY, no
    # capture; worker-1 (deadline-cut in flight) → its own step + `timed_out`.
    assert _branch_terminals(ledger) == {0: "completed", 1: "timed_out"}
    assert _branch_terminal_statuses(ledger, 0) == ["completed"]
    assert _branch_step_indexes(ledger) == {1}
    run_key = store.sole_run_key()
    assert 0 not in store.present_branch_indexes(run_key)

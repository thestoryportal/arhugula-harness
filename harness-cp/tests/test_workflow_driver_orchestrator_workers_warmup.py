"""B-18-PREWARM-OW — the ADR-D4 §1.8 concurrent-prompt-cache warm-up + the CP
spec v1.95 §25.19 heterogeneous cohort partition, extended to the
ORCHESTRATOR_WORKERS worker fan-out (CP spec v1.96; DDR at
`.harness/b18-prewarm-ow-design-decision-record.md`).

Workers are grouped by their dispatcher-attested `(step_kind, cohort_key)` over
the LIVE worker `branch_plan`; Phase 1 dispatches one LEADER per multi-member
cohort plus every non-beneficiary worker (None-key / non-capable / singleton
cohort), Phase 2 releases the followers. PROCEED = two sequential gathers under
the one deadline; strict tiers = inline two-phase (one deadline + one watchdog,
Phase-1 TaskGroup + the NORMATIVE post-group `task.result()` resurface, Phase-2
TaskGroup). The orchestrator is NOT a cohort member; the obligation-4 scan
family (all eight O-W exits) is untouched.

  OWP1  — PROCEED two-cohort: each cohort's leader completes before ITS
          followers start (fails on main: all-concurrent):
    → test_ow_partition_proceed_two_cohorts_leaders_serialize_before_followers
  OWP2  — the same ordering through `_cancel_fanout` on BOTH strict tiers:
    → test_ow_partition_strict_tiers_two_cohorts_leaders_serialize_before_followers
  OWP3  — non-beneficiary (None-key) worker keeps baseline IMMEDIATE dispatch
          (Phase 1 alongside the leaders; deadlock-detector control):
    → test_ow_partition_none_key_worker_dispatches_in_phase1
  OWP4  — all-distinct keys → every cohort singleton → gate False →
          all-concurrent (barrier control, green on main too):
    → test_ow_partition_all_distinct_keys_all_concurrent
  OWP5  — CASCADE_CANCEL leader failure: followers of ALL cohorts withheld —
          dispatch-marker ABSENCE + obligation-4 `cancelled` (fails on main):
    → test_ow_partition_cascade_cancel_leader_failure_withholds_all_followers
  OWP6  — PROCEED leader failure: Phase 2 STILL dispatches (H1 lineage), and
          followers start only after Phase 1 settled (fails on main):
    → test_ow_partition_proceed_leader_failure_still_releases_all_followers
  OWP7  — PAUSE-tier deadline wedge in a heterogeneous Phase 1: withheld
          followers `cancelled` via the deadline-exit scan, marker-absent; cut
          leader `timed_out`; clean leader `completed` (fails on main):
    → test_ow_partition_pause_deadline_strike_in_phase1_scan_covers_all_followers
  OWP8  — PAUSE partial-recovery resume re-partitions the LIVE remainder (a
          NEW leader per remaining cohort; organic two-round witness — round 1
          withholds via a Phase-1 leader failure; fails on main because round 1
          leaves nothing re-dispatchable there):
    → test_ow_partition_partial_recovery_resume_repartitions_remainder
  OWP9  — a Phase-1 leader raising SPONTANEOUS CancelledError is resurfaced by
          the NORMATIVE post-group `task.result()` collection: followers NEVER
          dispatch (marker ABSENCE; fails against a naive-TaskGroup impl AND
          against main's all-concurrent dispatch):
    → test_ow_partition_phase1_spontaneous_cancel_resurfaces_and_withholds_followers
  OWP10 — cross-cohort leader∥leader Phase-1 concurrency on PROCEED (mutual
          entry-wait control):
    → test_ow_partition_proceed_leaders_run_concurrently_in_phase1
  OWP11 — strict PAUSE: a Phase-1 worker's recursive child PAUSES → followers
          OMITTED from the snapshot (re-dispatchable by omission; the PAUSED
          boundary stays scan-free) + the paused child captured as the third
          disposition (fails on main: followers appear terminal):
    → test_ow_partition_pause_child_pause_in_phase1_omits_followers
  OWP12 — fence-family × partition (pre-build review C4): a RECOVERED fence
          peer withheld as a Phase-2 FOLLOWER on a CASCADE_CANCEL resume round
          records the union-arm `completed` CAPTURE-LESS at the terminal exit
          (never `cancelled`, never a store capture; fails on main where the
          peer re-dispatches and the this-round arm captures instead):
    → test_ow_partition_recovered_fence_peer_withheld_as_follower_completed_captureless

Structural-reachability note (DDR §5): at HEAD only INFERENCE_STEP dispatchers
are `CohortKeyCapable` in production, so fence-family (TOOL_STEP) and
paused-child ordinals are Phase-1 non-beneficiaries there; OWP11/OWP12 use a
capable stub to pin the composition contract against the day a second capable
kind lands.

Authority: ADR-D4 §1.8 ("all cells where fan-out cap > 1") + CP spec v1.95
§25.19 (the partition contract) + CP spec v1.96 (this arc) +
`.harness/b18-prewarm-ow-design-decision-record.md` (pre-build Fable-5
adversarial design review: AMEND-THEN-BUILD, 0 blocking, all findings folded).
"""

from __future__ import annotations

import asyncio
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
    PauseSnapshot,
    WorkflowPauseReason,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_dispatch_capacity_authority import DefaultCapacityAuthority
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
    SubAgentChildPausedError,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Identifier

# ---------------------------------------------------------------------------
# Shared fixtures (local twins of the O-W fence-ledger harness, cohort-shaped)
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
    concurrent_cache_warmup: bool = True,
    workflow_id: str = "wf-ow-warmup",
) -> WorkflowManifestEntry:
    """ORCHESTRATOR_WORKERS manifest. SOLO_DEVELOPER → PROCEED / TEAM_BINDING →
    PAUSE / MULTI_TENANT_COMPLIANCE → CASCADE_CANCEL; store-bound witnesses pass
    EVENT_SOURCED_REPLAY."""
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
        concurrent_cache_warmup=concurrent_cache_warmup,
    )


def _orch_step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("orchestrator"),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"role": "orchestrator"},
    )


def _worker(index: int, cohort: str | None, **extra: Any) -> WorkflowStep:
    """INFERENCE_STEP worker whose cohort membership rides the payload;
    `cohort=None` yields a None cohort_key (a non-beneficiary) under the capable
    fixtures below. `extra` carries additional payload fields (e.g. the OWP12
    round-2 `cohort2` re-keying)."""
    return WorkflowStep(
        step_id=StepID(f"worker-{index}"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"index": index, "cohort": cohort, **extra},
    )


class _RecordingLedger:
    """In-memory ledger sink that records drained appends."""

    def __init__(self) -> None:
        from harness_is.state_ledger_entry_schema import Actor, ActorClass

        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-ow-warmup")
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
    """Minimal fake DriverContext (the fence-ledger-file twin)."""

    def __init__(
        self,
        *,
        ledger: Any,
        emitter: _Emitter,
        pause_resume_protocol: Any = None,
        engine_output_store: Any = None,
        capacity_authority: Any = None,
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
        self.resume_context_holder = None
        # B-48/U-CP-101 — injectable so a test can pin an explicit frame
        # budget for precise admission assertions.
        self.capacity_authority = capacity_authority


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
    """Minimal in-memory EngineOutputStore fake covering the O-W produce +
    crash-consume surface these witnesses touch (the fence-ledger-file twin;
    marker/capture assertions are the load-bearing reads)."""

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

    # -- consumer surface --
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


class EffectFenceAmbiguousUncommittedError(Exception):
    """Test-local stand-in for the runtime fence's ambiguous error (C-RT-31
    §14.22) — the driver name-matches `type(exc).__name__`."""

    def __init__(self, *, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__(f"ambiguous (key={idempotency_key!r})")


class _KindMap:
    """Registry mapping step kinds to dispatchers; unmapped kinds raise
    `StepKindDispatcherNotBoundError` synchronously at lookup."""

    def __init__(self, mapping: dict[StepKind, Any]) -> None:
        self._mapping = mapping

    def lookup(self, step_kind: StepKind) -> Any:
        try:
            return self._mapping[step_kind]
        except KeyError as exc:
            raise StepKindDispatcherNotBoundError(str(step_kind)) from exc


class _Echo:
    """Clean dispatcher (the orchestrator)."""

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        return dict(step.step_payload)


# ---------------------------------------------------------------------------
# Cohort-keyed dispatchers
# ---------------------------------------------------------------------------


class _PartitionOrderingWitness:
    """Cohort-keyed dispatcher: each LEADER sleeps briefly then marks its cohort
    done; every NON-leader records at ENTRY which cohorts were already done (the
    §25.19 cache-write-before-cache-hit ordering witness). Leaders in `fail`
    raise instead of completing (their cohort event stays unset)."""

    def __init__(self, *, leaders: set[int], fail: set[int] | None = None) -> None:
        self._leaders = leaders
        self._fail = fail or set()
        self._lock = threading.Lock()
        self._cohort_done: dict[str, threading.Event] = {}
        self.dispatched: list[int] = []
        self.cohorts_done_on_entry: dict[int, frozenset[str]] = {}

    def _event(self, cohort: str) -> threading.Event:
        with self._lock:
            return self._cohort_done.setdefault(cohort, threading.Event())

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        cohort = str(step.step_payload["cohort"])
        event = self._event(cohort)
        with self._lock:
            self.dispatched.append(idx)
            self.cohorts_done_on_entry[idx] = frozenset(
                name for name, ev in self._cohort_done.items() if ev.is_set()
            )
        if idx in self._leaders:
            time.sleep(0.15)
            if idx in self._fail:
                raise RuntimeError(f"simulated leader-{idx} failure")
            event.set()
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


class _CohortScriptedWorker:
    """Cohort-keyed scripted dispatcher: per-ordinal behavior — `ok` returns;
    `fail` raises RuntimeError; `fence` raises the ambiguous fence error with
    key `fence-key-attempt1-{i}`; `child` raises `SubAgentChildPausedError`
    carrying `child_snapshot`. Ordinals in `barrier_indexes` synchronize on one
    barrier BEFORE acting (deterministic Phase-1 composition). An ordinal
    ABSENT from the script must never dispatch (withheld-expectation assert).
    `cohort_field` selects the payload field the cohort key derives from (the
    OWP12 round-2 re-keying)."""

    def __init__(
        self,
        script: dict[int, str],
        *,
        barrier_indexes: frozenset[int] = frozenset(),
        child_snapshot: PauseSnapshot | None = None,
        cohort_field: str = "cohort",
    ) -> None:
        self._script = script
        self._barrier = (
            threading.Barrier(len(barrier_indexes), timeout=10.0) if barrier_indexes else None
        )
        self._barrier_indexes = barrier_indexes
        self._child_snapshot = child_snapshot
        self._cohort_field = cohort_field
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        assert idx in self._script, f"worker {idx} dispatched — expected withheld"
        if self._barrier is not None and idx in self._barrier_indexes:
            self._barrier.wait()
        action = self._script[idx]
        if action == "fail":
            raise RuntimeError(f"simulated worker-{idx} failure")
        if action == "fence":
            raise EffectFenceAmbiguousUncommittedError(idempotency_key=f"fence-key-attempt1-{idx}")
        if action == "child":
            assert self._child_snapshot is not None
            raise SubAgentChildPausedError(
                child_workflow_id="wf-child", child_snapshot=self._child_snapshot
            )
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get(self._cohort_field)
        return f"cohort-{cohort}" if cohort is not None else None


class _LeaderWaitsForNoneWorkerDispatcher:
    """OWP3 fixture: the cohort-A leader (index 0) BLOCKS until the None-key
    worker (index 2) completes — passing PROVES the None-key worker dispatched
    in Phase 1 alongside the leader (non-beneficiary placement); if it were
    withheld to Phase 2 the leader would wait out the 10 s guard and fail."""

    def __init__(self) -> None:
        self.none_worker_done = threading.Event()
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx == 0:
            assert self.none_worker_done.wait(timeout=10.0), (
                "None-key worker never dispatched while the leader ran Phase 1 — "
                "non-beneficiary was withheld (D4 violation)"
            )
        if idx == 2:
            self.none_worker_done.set()
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


class _AllConcurrentBarrierDispatcher:
    """OWP4 fixture: all three workers synchronize on one barrier — passing
    PROVES they were all in flight simultaneously (gate False). A partition
    that wrongly grouped any of them would wedge the barrier out to its 10 s
    timeout and fail the run."""

    def __init__(self, parties: int) -> None:
        self._barrier = threading.Barrier(parties, timeout=10.0)
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        self._barrier.wait()
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


class _WedgeLeaderDispatcher:
    """OWP7 fixture: the cohort-A leader blocks past the (monkeypatched)
    deadline while the cohort-B leader completes clean."""

    def __init__(self, *, release: threading.Event, self_release_seconds: float) -> None:
        self._release = release
        self._self_release_seconds = self_release_seconds
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx == 0:
            self._release.wait(timeout=self._self_release_seconds)
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


class _SpontaneousCancelLeaderDispatcher:
    """OWP9 fixture: the cohort-A leader raises SPONTANEOUS CancelledError from
    its own dispatch (the sub-agent naked-escape / watchdog-cut vehicle); the
    cohort-B leader is slow (in-flight while the group settles)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        idx = int(step.step_payload["index"])
        with self._lock:
            self.dispatched.append(idx)
        if idx == 0:
            raise asyncio.CancelledError()
        if idx == 2:
            time.sleep(0.05)
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


class _MutualLeaderEntryWitness:
    """OWP10 fixture: each leader waits for the OTHER leader's ENTRY before
    returning — passing PROVES the two cohort leaders ran CONCURRENTLY in
    Phase 1 (the partition serializes leader→followers WITHIN a cohort, never
    leader→leader ACROSS cohorts)."""

    def __init__(self) -> None:
        self.entered: dict[int, threading.Event] = {0: threading.Event(), 2: threading.Event()}
        self._lock = threading.Lock()
        self.dispatched: list[int] = []

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
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
        return {"index": idx}

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        cohort = step.step_payload.get("cohort")
        return f"cohort-{cohort}" if cohort is not None else None


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
    concurrent_cache_warmup: bool = True,
    store: Any = None,
    with_pause_protocol: bool = False,
    pause_snapshot_input: PauseSnapshot | None = None,
    workflow_id: str = "wf-ow-warmup",
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
            capacity_authority=capacity_authority,
        ),
    )
    return execute_workflow(
        _manifest(
            persona_tier=persona_tier,
            engine_class=engine_class,
            concurrent_cache_warmup=concurrent_cache_warmup,
            workflow_id=workflow_id,
        ),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, registry),
        pause_snapshot_input=pause_snapshot_input,
    )


def _registry(dispatcher: Any) -> _KindMap:
    """Orchestrator (DECLARATIVE) echoes; workers (INFERENCE) hit `dispatcher`."""
    return _KindMap({StepKind.DECLARATIVE_STEP: _Echo(), StepKind.INFERENCE_STEP: dispatcher})


def _child_pause_snapshot() -> PauseSnapshot:
    """A hash-valid linear child PauseSnapshot for SubAgentChildPausedError."""
    return asyncio.run(
        _protocol().capture_pause_snapshot(
            workflow_id="wf-child",
            run_id="child-run",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        )
    )


# ---------------------------------------------------------------------------
# OWP1 / OWP2 — per-cohort serialization (PROCEED + both strict tiers)
# ---------------------------------------------------------------------------


def test_ow_partition_proceed_two_cohorts_leaders_serialize_before_followers() -> None:
    """OWP1 (PROCEED): cohorts A={0,1} / B={2,3} → Phase 1 = leaders {0,2},
    Phase 2 = followers {1,3}. Each follower must see ITS cohort leader
    completed at entry. Fails on main (no O-W warm-up → all-concurrent →
    followers enter while the leaders still sleep)."""
    witness = _PartitionOrderingWitness(leaders={0, 2})
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(witness),
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [0, 1, 2, 3]
    assert "A" in witness.cohorts_done_on_entry[1], (
        f"follower 1 started before cohort-A leader completed ({witness.cohorts_done_on_entry})"
    )
    assert "B" in witness.cohorts_done_on_entry[3], (
        f"follower 3 started before cohort-B leader completed ({witness.cohorts_done_on_entry})"
    )


@pytest.mark.parametrize(
    "persona_tier",
    [PersonaTier.TEAM_BINDING, PersonaTier.MULTI_TENANT_COMPLIANCE],
    ids=["pause-tier", "cascade-cancel-tier"],
)
def test_ow_partition_strict_tiers_two_cohorts_leaders_serialize_before_followers(
    persona_tier: PersonaTier,
) -> None:
    """OWP2 (strict tiers): the same two-cohort ordering through the inline
    two-phase `_cancel_fanout` on BOTH strict tiers."""
    witness = _PartitionOrderingWitness(leaders={0, 2})
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(witness),
        persona_tier=persona_tier,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [0, 1, 2, 3]
    assert "A" in witness.cohorts_done_on_entry[1]
    assert "B" in witness.cohorts_done_on_entry[3]


def _unbound_kind_worker(index: int) -> WorkflowStep:
    """A worker step whose `step_kind` (`TOOL_STEP`) is deliberately absent
    from `_registry()`'s `_KindMap` — `step_dispatchers.lookup(...)` raises
    `StepKindDispatcherNotBoundError` synchronously for it."""
    return WorkflowStep(
        step_id=StepID(f"worker-{index}"),
        step_kind=StepKind.TOOL_STEP,
        step_payload={"index": index},
    )


def test_proceed_worker_dispatcher_lookup_failure_releases_admission() -> None:
    """Codex round-8 [P2] "release admissions when worker lookup fails" —
    `_proceed_worker`'s `step_dispatchers.lookup(step.step_kind)` is the
    only statement before `_dispatch_releasing_admission` is ever scheduled;
    an unbound `StepKind` raising there must not strand this worker's
    already-reserved frame.

    Mutation probe: removing the `try/except BaseException: ... release_
    unless_job_bound(); raise` guard around the lookup in `_proceed_worker`
    leaks the worker's admitted frame — `authority.available` stays short of
    the full `frame_budget` post-run.
    """
    authority = DefaultCapacityAuthority(frame_budget=4)
    result = _run(
        steps=[_orch_step(), _unbound_kind_worker(0)],
        registry=_registry(_Echo()),
        persona_tier=PersonaTier.SOLO_DEVELOPER,  # PROCEED tier
        capacity_authority=authority,
        workflow_id="wf-ow-proceed-lookup-failure",
    )
    assert result.status is not RunStatus.SUCCESS
    assert authority.available == 4, (
        f"expected full frame-budget recovery (4); got {authority.available} — "
        f"the worker's admission leaked on dispatcher-lookup failure"
    )


def test_cascade_cancel_worker_dispatcher_lookup_failure_releases_admission() -> None:
    """Codex round-8 [P2] sibling witness for `_cancel_worker` (CASCADE_
    CANCEL tier) — same rationale as the PROCEED-tier witness above."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    result = _run(
        steps=[_orch_step(), _unbound_kind_worker(0)],
        registry=_registry(_Echo()),
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,  # CASCADE_CANCEL tier
        capacity_authority=authority,
        workflow_id="wf-ow-cascade-cancel-lookup-failure",
    )
    assert result.status is not RunStatus.SUCCESS
    assert authority.available == 4, (
        f"expected full frame-budget recovery (4); got {authority.available} — "
        f"the worker's admission leaked on dispatcher-lookup failure"
    )


def test_cascade_cancel_worker_marker_write_failure_releases_admission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-7 [P1] "release admission when dispatch marker creation
    fails" — the ORCHESTRATOR_WORKERS twin of `_cancel_branch`'s fix
    (`_cancel_worker`, byte-identical rationale + guard): `_mark_branch_
    dispatched` is the only statement before `inflight` is created, so a
    raise there must release `_admission` explicitly (`_dispatch_releasing_
    admission` never gets scheduled otherwise, and this coroutine's own
    `finally` deliberately does not release it either).

    Mutation probe: removing the `try/except BaseException: ... release_
    unless_job_bound(); raise` guard around `_mark_branch_dispatched` in
    `_cancel_worker` restores the leak — `authority.available` stays short
    of the full `frame_budget` post-run.
    """
    import harness_cp.workflow_driver as workflow_driver_module

    def _raising_marker(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("simulated marker-store write failure")

    monkeypatch.setattr(workflow_driver_module, "_mark_branch_dispatched", _raising_marker)

    authority = DefaultCapacityAuthority(frame_budget=4)
    result = _run(
        steps=[_orch_step(), _worker(0, None), _worker(1, None)],
        registry=_registry(_Echo()),
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,  # CASCADE_CANCEL tier
        capacity_authority=authority,
        workflow_id="wf-ow-marker-failure",
    )
    assert result.status is not RunStatus.SUCCESS
    assert authority.available == 4, (
        f"expected full frame-budget recovery (4); got {authority.available} — "
        f"a worker's admission leaked on marker-write failure"
    )


# ---------------------------------------------------------------------------
# OWP3 / OWP4 — non-beneficiary placement + gate-False controls
# ---------------------------------------------------------------------------


def test_ow_partition_none_key_worker_dispatches_in_phase1() -> None:
    """OWP3 (control): a None-key (non-beneficiary) worker keeps its baseline
    immediate dispatch — Phase 1 alongside the leaders, never delayed behind
    other cohorts' cache-writes. Deadlock-detector: green on main too."""
    dispatcher = _LeaderWaitsForNoneWorkerDispatcher()
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, None)],
        registry=_registry(dispatcher),
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(dispatcher.dispatched) == [0, 1, 2]


def test_ow_partition_all_distinct_keys_all_concurrent() -> None:
    """OWP4 (control): all-distinct cohort keys → every cohort singleton →
    phase2 empty → gate False → the all-concurrent baseline (the barrier
    passes only if all three workers are in flight simultaneously)."""
    dispatcher = _AllConcurrentBarrierDispatcher(parties=3)
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "B"), _worker(2, "C")],
        registry=_registry(dispatcher),
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(dispatcher.dispatched) == [0, 1, 2]


# ---------------------------------------------------------------------------
# OWP5 / OWP6 — leader failure per tier
# ---------------------------------------------------------------------------


def test_ow_partition_cascade_cancel_leader_failure_withholds_all_followers() -> None:
    """OWP5 (CASCADE_CANCEL): leader 0 (cohort A) fails in Phase 1 while leader
    2 (cohort B) is in flight → the followers of ALL cohorts are WITHHELD:
    dispatch-marker ABSENCE for {1,3} + the obligation-4 scan records their
    `cancelled` terminal at the cascade-cancel exit. Fails on main (all four
    dispatch; markers present)."""
    store = _MiniOWStore()
    ledger = _RecordingLedger()
    dispatcher = _CohortScriptedWorker({0: "fail", 2: "ok"}, barrier_indexes=frozenset({0, 2}))
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(dispatcher),
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        ledger=ledger,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-cascade-cancel"
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert _branch_terminals(ledger) == {
        0: "completed",
        1: "cancelled",
        2: "completed",
        3: "cancelled",
    }
    assert _branch_step_indexes(ledger) == {0, 2}
    run_key = store.sole_run_key()
    # Markers: Phase-1 members only; withheld followers wrote NEITHER marker
    # nor store record (ledger-only synthesis).
    assert store.present_dispatched_indexes(run_key) == {0, 2}
    assert store.present_branch_indexes(run_key) == {0, 2}


def test_ow_partition_cascade_cancel_leader_failure_releases_withheld_follower_admissions() -> None:
    """B-48 (codex round-4 [P1]; the `_execute_orchestrator_workers` twin of
    `_execute_parallelization`'s "release withheld warm-up admissions after
    Phase 1 fails"): `_admit_fanout_branch_plan` reserves frames for all 4
    workers upfront, but leader 0's Phase-1 failure withholds followers {1,
    3} entirely (never dispatched, per the sibling test above) — their
    `_cancel_worker` coroutines are never created, so nothing else releases
    their admissions without the fix."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    dispatcher = _CohortScriptedWorker({0: "fail", 2: "ok"}, barrier_indexes=frozenset({0, 2}))
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(dispatcher),
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=_MiniOWStore(),
        capacity_authority=authority,
    )
    assert result.status is RunStatus.FAILED
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert authority.available == authority.frame_budget


def test_ow_partition_proceed_deadline_strike_releases_withheld_follower_admissions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-48 (codex round-4 [P1] "release admissions withheld by warm-up
    timeouts"): PROCEED-tier + deadline twin of
    `test_ow_partition_cascade_cancel_leader_failure_releases_withheld_follower_admissions`
    (OWP5's admission half) and the PARALLELIZATION deadline-strike sibling.
    Both leaders wedge past the deadline (neither self-releases before the
    barrier strikes), so the snapshot taken IMMEDIATELY on `_run` returning —
    before this test's own `finally` unblocks them — is race-free: no leader
    could possibly have released yet. Mutation probe: dropping the try/except
    around Phase-1's gather leaves the withheld followers' 2 frames stuck
    forever (the snapshot would show frame_budget - 4, not frame_budget - 2)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)

    class _WedgeBothLeadersDispatcher:
        def __init__(self, *, release: threading.Event) -> None:
            self._release = release
            self._lock = threading.Lock()
            self.dispatched: list[int] = []

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            idx = int(step.step_payload["index"])
            with self._lock:
                self.dispatched.append(idx)
            if idx in (0, 2):
                self._release.wait(timeout=5.0)
            return {"index": idx}

        def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
            cohort = step.step_payload.get("cohort")
            return f"cohort-{cohort}" if cohort is not None else None

    authority = DefaultCapacityAuthority(frame_budget=4)
    release = threading.Event()
    dispatcher = _WedgeBothLeadersDispatcher(release=release)
    available_on_return: int | None = None
    try:
        result = _run(
            steps=[
                _orch_step(),
                _worker(0, "A"),
                _worker(1, "A"),
                _worker(2, "B"),
                _worker(3, "B"),
            ],
            registry=_registry(dispatcher),
            persona_tier=PersonaTier.SOLO_DEVELOPER,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=_MiniOWStore(),
            capacity_authority=authority,
        )
        # Race-free: captured before `finally` unblocks either wedged leader —
        # neither leader's frame could possibly have released yet, so any
        # frames back at this exact point came ONLY from the followers.
        available_on_return = authority.available
    finally:
        release.set()
    assert result.status is RunStatus.PARTIAL
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert available_on_return == authority.frame_budget - 2


def test_ow_partition_proceed_leader_failure_still_releases_all_followers() -> None:
    """OWP6 (PROCEED, H1 lineage): leader 0 (cohort A) FAILS in Phase 1 —
    Phase 2 still dispatches (including the failed cohort's follower) → PARTIAL;
    the ordering half pins the global Phase-1 barrier: every follower's entry
    sees cohort-B done (leader 2 completed before ANY follower started). Fails
    on main (followers enter while leader 2 still sleeps)."""
    witness = _PartitionOrderingWitness(leaders={0, 2}, fail={0})
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(witness),
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    assert result.status is RunStatus.PARTIAL
    assert sorted(witness.dispatched) == [0, 1, 2, 3]
    assert "B" in witness.cohorts_done_on_entry[1], (
        "follower 1 started before Phase 1 settled (global Phase-1 barrier violated)"
    )
    assert "B" in witness.cohorts_done_on_entry[3]


# ---------------------------------------------------------------------------
# OWP7 — PAUSE-tier deadline wedge in Phase 1
# ---------------------------------------------------------------------------


def test_ow_partition_pause_deadline_strike_in_phase1_scan_covers_all_followers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OWP7 (ML-family generalized): heterogeneous Phase 1 — leader 0 (cohort A)
    wedges past the deadline, leader 2 (cohort B) completes clean. The strike
    lands the PAUSE-tier terminal FAILED barrier-deadline exit; the obligation-4
    scan records `cancelled` for the withheld followers of BOTH cohorts,
    marker-absent; the cut leader records `timed_out`, the clean leader
    `completed`. Fails on main (all four dispatch)."""
    from harness_cp import workflow_driver as wd

    monkeypatch.setattr(wd, "_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS", 0.2)
    release = threading.Event()
    dispatcher = _WedgeLeaderDispatcher(release=release, self_release_seconds=2.0)
    ledger = _RecordingLedger()
    store = _MiniOWStore()
    started = time.monotonic()
    try:
        result = _run(
            steps=[
                _orch_step(),
                _worker(0, "A"),
                _worker(1, "A"),
                _worker(2, "B"),
                _worker(3, "B"),
            ],
            registry=_registry(dispatcher),
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
            ledger=ledger,
        )
    finally:
        release.set()
    elapsed = time.monotonic() - started
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-barrier-deadline"
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert _branch_terminals(ledger) == {
        0: "timed_out",
        1: "cancelled",
        2: "completed",
        3: "cancelled",
    }
    assert _branch_step_indexes(ledger) == {0, 2}
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0, 2}
    assert elapsed < 1.5


# ---------------------------------------------------------------------------
# OWP8 — partial-recovery resume re-partitions the LIVE remainder
# ---------------------------------------------------------------------------


def test_ow_partition_partial_recovery_resume_repartitions_remainder() -> None:
    """OWP8: an organic two-round witness. Round 1 (PAUSE tier): cohorts
    A={0,1,2} (leader 0) / B={3,4} (leader 3); leader 3 FAILS in Phase 1 →
    followers {1,2,4} withheld → OMITTED from the snapshot (re-dispatchable);
    terminals recovered for {0,3}. Round 2 re-partitions the LIVE remainder
    {1,2,4}: cohort A={1,2} elects the NEW leader 1, B={4} is a singleton
    non-beneficiary → follower 2 must see cohort-A done at entry. Fails on
    main (round 1 dispatches everything → nothing re-dispatchable → round 2
    never dispatches worker 2)."""
    store = _MiniOWStore()
    round1 = _CohortScriptedWorker({0: "ok", 3: "fail"}, barrier_indexes=frozenset({0, 3}))
    paused = _run(
        steps=[
            _orch_step(),
            _worker(0, "A"),
            _worker(1, "A"),
            _worker(2, "A"),
            _worker(3, "B"),
            _worker(4, "B"),
        ],
        registry=_registry(round1),
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None
    fan_out = snapshot.fan_out_resume
    assert fan_out is not None
    assert {b.branch_index for b in fan_out.branches} == {0, 3}
    assert sorted(round1.dispatched) == [0, 3]

    round2 = _PartitionOrderingWitness(leaders={1})
    result = _run(
        steps=[
            _orch_step(),
            _worker(0, "A"),
            _worker(1, "A"),
            _worker(2, "A"),
            _worker(3, "B"),
            _worker(4, "B"),
        ],
        registry=_registry(round2),
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    # Recovered ran-and-errored worker 3 (terminal, no output) keeps the resumed
    # run DEGRADED → PARTIAL.
    assert result.status is RunStatus.PARTIAL
    assert sorted(round2.dispatched) == [1, 2, 4]
    assert "A" in round2.cohorts_done_on_entry[2], (
        "round-2 follower 2 started before the NEW cohort-A leader (1) completed — "
        f"the live remainder was not re-partitioned ({round2.cohorts_done_on_entry})"
    )


# ---------------------------------------------------------------------------
# OWP9 — the NORMATIVE Phase-1 task.result() resurface
# ---------------------------------------------------------------------------


def test_ow_partition_phase1_spontaneous_cancel_resurfaces_and_withholds_followers() -> None:
    """OWP9 (the §25.19 item-4 pin): a Phase-1 leader raising SPONTANEOUS
    CancelledError is SWALLOWED by the TaskGroup (CPython: the group exits clean
    with task.cancelled()=True) — the mandatory post-group `task.result()`
    collection resurfaces it, so the cancellation propagates and the followers
    are NEVER dispatched: marker ABSENCE for {1,3}, no Phase-2 release after
    the cut. A naive TaskGroup Phase 1 without the collection dispatches the
    followers AFTER the cut — this witness fails against that regression, and
    against main (all four dispatch)."""
    store = _MiniOWStore()
    dispatcher = _SpontaneousCancelLeaderDispatcher()
    with pytest.raises(asyncio.CancelledError):
        _run(
            steps=[
                _orch_step(),
                _worker(0, "A"),
                _worker(1, "A"),
                _worker(2, "B"),
                _worker(3, "B"),
            ],
            registry=_registry(dispatcher),
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            engine_class=EngineClass.EVENT_SOURCED_REPLAY,
            store=store,
        )
    # Phase 1 only ever dispatched; the swallowed cancel resurfaced BEFORE any
    # Phase-2 release (the in-flight cohort-B leader ran shielded to completion).
    assert sorted(dispatcher.dispatched) == [0, 2]
    assert store.present_dispatched_indexes(store.sole_run_key()) == {0, 2}


# ---------------------------------------------------------------------------
# OWP10 — cross-cohort leader concurrency (control)
# ---------------------------------------------------------------------------


def test_ow_partition_proceed_leaders_run_concurrently_in_phase1() -> None:
    """OWP10 (control): different cohorts' LEADERS dispatch CONCURRENTLY with
    each other in Phase 1 — the partition serializes leader→followers WITHIN a
    cohort, never leader→leader ACROSS cohorts. Green on main too."""
    witness = _MutualLeaderEntryWitness()
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(witness),
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    assert result.status is RunStatus.SUCCESS
    assert sorted(witness.dispatched) == [0, 1, 2, 3]


# ---------------------------------------------------------------------------
# OWP11 — partition × paused-child (third disposition)
# ---------------------------------------------------------------------------


def test_ow_partition_pause_child_pause_in_phase1_omits_followers() -> None:
    """OWP11 (strict PAUSE): leader 0's recursive child PAUSES in Phase 1 while
    leader 2 is in flight → the fan-out halts at the pause boundary: the paused
    child is captured as the THIRD disposition (paused_child_branches), leader
    2's terminal is recovered, and the withheld followers {1,3} are OMITTED
    from the snapshot — re-dispatchable by omission, ZERO synthesized terminals
    (the PAUSED boundary stays scan-free). Fails on main (followers dispatch →
    appear terminal in the snapshot)."""
    store = _MiniOWStore()
    ledger = _RecordingLedger()
    dispatcher = _CohortScriptedWorker(
        {0: "child", 2: "ok"},
        barrier_indexes=frozenset({0, 2}),
        child_snapshot=_child_pause_snapshot(),
    )
    result = _run(
        steps=[_orch_step(), _worker(0, "A"), _worker(1, "A"), _worker(2, "B"), _worker(3, "B")],
        registry=_registry(dispatcher),
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        ledger=ledger,
        with_pause_protocol=True,
    )
    assert result.status is RunStatus.PAUSED
    snapshot = result.pause_snapshot
    assert snapshot is not None
    fan_out = snapshot.fan_out_resume
    assert fan_out is not None
    assert [(b.branch_index, b.terminal_status) for b in fan_out.branches] == [(2, "completed")]
    assert [b.branch_index for b in fan_out.paused_child_branches] == [0]
    assert fan_out.effect_fence_paused_branches == ()
    assert sorted(dispatcher.dispatched) == [0, 2]
    # Scan-free PAUSED boundary: NO synthesized terminals for the withheld
    # followers (snapshot omission IS the re-dispatchable contract).
    assert _branch_terminals(ledger) == {2: "completed"}
    run_key = store.sole_run_key()
    assert store.present_dispatched_indexes(run_key) == {0, 2}
    assert store.present_branch_indexes(run_key) == {2}


# ---------------------------------------------------------------------------
# OWP12 — partition × recovered fence peer (union arm, capture-less)
# ---------------------------------------------------------------------------


def test_ow_partition_recovered_fence_peer_withheld_as_follower_completed_captureless() -> None:
    """OWP12 (pre-build review C4): a RECOVERED effect-fence peer withheld as a
    Phase-2 FOLLOWER on a CASCADE_CANCEL resume round records the union-arm
    `completed` CAPTURE-LESS at the terminal exit — obligation-4 forecloses
    `cancelled` (its attempt-1 dispatch fired and holds the reserve), and a
    store capture would flip its crash classification.

    Round 1 (PAUSE tier, cohort field `cohort`): X={0,1,2} (leader 0 FAILS) /
    Y={3} (singleton non-beneficiary → Phase 1, FENCE-stashes). Phase-1 failure
    withholds followers {1,2}; snapshot: branches={0}, fence=[3], omitted
    {1,2}. Round 2 (MTC → CASCADE_CANCEL, the persona-tier-change reach; fresh
    dispatcher keys on `cohort2`): live plan {1,2,3} re-groups as Z={1,3}
    (leader 1 FAILS) / W={2} → the fence peer 3 is Z's FOLLOWER → withheld →
    the scan's recovered-fence arm fires: ledger `completed` terminal-ONLY, NO
    re-mark, NO capture. Fails on main (nothing is withheld in either round:
    the peer re-dispatches and the this-round fence arm captures instead)."""
    store = _MiniOWStore()
    round1 = _CohortScriptedWorker({0: "fail", 3: "fence"}, barrier_indexes=frozenset({0, 3}))
    paused = _run(
        steps=[
            _orch_step(),
            _worker(0, "X", cohort2="Z"),
            _worker(1, "X", cohort2="Z"),
            _worker(2, "X", cohort2="W"),
            _worker(3, "Y", cohort2="Z"),
        ],
        registry=_registry(round1),
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        with_pause_protocol=True,
    )
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None
    fan_out = snapshot.fan_out_resume
    assert fan_out is not None
    assert {b.branch_index for b in fan_out.branches} == {0}
    assert {b.branch_index for b in fan_out.effect_fence_paused_branches} == {3}
    assert sorted(round1.dispatched) == [0, 3]
    run_key = store.sole_run_key()
    assert store.present_dispatched_indexes(run_key) == {0, 3}
    assert store.present_branch_indexes(run_key) == {0}

    ledger2 = _RecordingLedger()
    round2 = _CohortScriptedWorker(
        {1: "fail", 2: "ok"},
        barrier_indexes=frozenset({1, 2}),
        cohort_field="cohort2",
    )
    result = _run(
        steps=[
            _orch_step(),
            _worker(0, "X", cohort2="Z"),
            _worker(1, "X", cohort2="Z"),
            _worker(2, "X", cohort2="W"),
            _worker(3, "Y", cohort2="Z"),
        ],
        registry=_registry(round2),
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        store=store,
        ledger=ledger2,
        with_pause_protocol=True,
        pause_snapshot_input=snapshot,
    )
    assert result.status is RunStatus.FAILED
    assert result.fail_class == "orchestrator-workers-cascade-cancel"
    # Round 2 dispatched Phase 1 only — the recovered fence peer was withheld.
    assert sorted(round2.dispatched) == [1, 2]
    # The union arm: `completed` terminal-ONLY for the withheld peer (never
    # `cancelled`, no step entry).
    assert _branch_terminal_statuses(ledger2, 3) == ["completed"]
    assert _branch_step_indexes(ledger2) == {1, 2}
    # CAPTURE-LESS: the store's capture set gains {1, 2} this round — never 3
    # (a capture would flip its fence-recoverable crash classification); its
    # attempt-1 dispatch marker stands un-re-marked.
    assert store.present_branch_indexes(run_key) == {0, 1, 2}
    assert store.present_dispatched_indexes(run_key) == {0, 1, 2, 3}

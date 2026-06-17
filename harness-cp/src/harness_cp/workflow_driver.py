"""Workflow execution driver — U-CP-56.

Implements C-CP-25 §25.1 (scope) + §25.2 (signatures) + §25.3 (iteration
discipline, happy-path) + §25.5 (lifecycle event emission boundaries —
SINGLE_THREADED_LINEAR filter over §5.1 closed-at-8 taxonomy) + §25.6
(replay-resumption composition with §8.2 idempotency-key join) + §25.7
(failure modes 1-4).

Drain composition (§25.4 + failure mode 5) is U-CP-57.

**Architectural shape (substrate composition).** The driver does not import
`harness-runtime` (which would invert the CP→runtime dependency direction).
Instead it consumes substrate via two locally-declared Protocols:

- `LedgerWriterLike` — write-side substrate (C-IS-07 §7.1 idempotent append
  composition with C-IS-05 entry shape). Concretized by runtime's
  `LedgerWriter` (`harness_runtime.lifecycle.state_ledger.LedgerWriter`)
  which structurally satisfies the protocol.
- `LifecycleEventEmitterLike` — lifecycle-event emission surface (§5.1 8-class
  taxonomy via `harness_core.WorkflowEventClass`). Concretized by runtime's
  `RuntimeLifecycleEventEmitter`.

Step dispatch is delegated through a `StepDispatcher` Protocol — the driver
itself is opaque to step body kind (LLM call / tool call / sub-routine);
binding lookup + provider/model dispatch is the dispatcher's responsibility.
Per C-CP-25 §25.3.3.4: "Step body is opaque to the driver; the router owns
provider / model / engine dispatch."

Authority:
- `Spec_Control_Plane_v1_4.md` §25
- `Implementation_Plan_Control_Plane_v2_11.md` U-CP-56
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
from collections.abc import Awaitable, Coroutine, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Protocol, cast, runtime_checkable

from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import ActionID
from harness_core.workflow_event_class import WorkflowEventClass
from harness_is.state_ledger_entry_schema import Actor
from opentelemetry.trace import Status, StatusCode, TracerProvider

if TYPE_CHECKING:
    from harness_is.state_ledger_entry_schema import Identifier

    from harness_cp.validator_framework import SyncValidatorFrameworkFacade
    from harness_cp.validator_framework_types import ValidatorEvaluation

from harness_cp.cp_shared_types import ActorIdentity, AgentRole, ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.handoff_context import (
    ActionKind,
    HandoffContext,
    LedgerEntryRef,
    ProposedAction,
    RetryHistory,
    StateSummary,
)
from harness_cp.pause_resume_protocol import (
    CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION,
    CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED,
    PauseReason,
    PauseResumeProtocol,
    PauseResumeProtocolEventKind,
    ResumeOutcomeKind,
)
from harness_cp.pause_resume_protocol_types import (
    MaterialDiffPolicy,
    PauseSnapshot,
    WorkflowPauseReason,
)
from harness_cp.per_role_catalog import derive_agent_role
from harness_cp.per_step_override_evaluator import StepEffectiveBinding, resolve_step_binding
from harness_cp.topology_pattern import CascadePolicy, TopologyPattern
from harness_cp.workflow_driver_errors import (
    BranchBarrierDeadlineExceededError,
    EngineClassNotYetMaterializedError,
    TopologyPatternNotYetMaterializedError,
)
from harness_cp.workflow_driver_types import (
    RunResult,
    RunStatus,
    StepExecutionContext,
    StepKind,
    WorkflowStep,
    compose_branch_child_context,
    compose_branch_metadata,
    compose_branch_path,
    compose_branch_step_action_id,
    compose_branch_terminal_action_id,
    compose_branch_terminal_path,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_cp.workload_engine_class_matrix import d4_tunable, lookup_cell

# ---------------------------------------------------------------------------
# v1.4 in-scope sets (per C-CP-25 §25.1 + Implementation Plan §0.2)
# ---------------------------------------------------------------------------


class _DriverStrategyStatus(Enum):
    """Materialization status of a topology's driver strategy (C-CP-25 §25.10).

    The §25.10 driver-strategy dispatch table replaces the §25.1
    `_IN_SCOPE_TOPOLOGY` materialization gate. It enumerates ALL SIX
    `TopologyPattern` values; a pattern lands by flipping its table entry, so
    the dispatch site never needs re-plumbing. At B1-impl-2 only
    `SINGLE_THREADED_LINEAR` is materialized (`LINEAR_INLINE` — the existing
    §25.3 iteration loop); the remaining non-linear patterns are
    `NOT_YET_MATERIALIZED` and raise `TopologyPatternNotYetMaterializedError`
    until each strategy unit (U-CP-86..U-CP-90) lands. `PARALLELIZATION`
    (the fan-out-barrier-aggregate strategy) landed first at U-CP-86;
    `EVALUATOR_OPTIMIZER` (the sequential generate→evaluate→regenerate loop)
    landed second at U-CP-87; `ORCHESTRATOR_WORKERS` (orchestrator-dispatch-
    collect fan-out) landed third at U-CP-88; `HIERARCHICAL_DELEGATION`
    (recursive bounded-fan-out — cap-3 per parent reusing `ORCHESTRATOR_WORKERS`
    at each level) landed fourth at U-CP-89; `DECENTRALIZED_HANDOFF` (single-owner
    sequential handoff via `HandoffContext`) landed fifth (last) at U-CP-90. **All
    six `TopologyPattern` values are now materialized** — no member is
    `NOT_YET_MATERIALIZED` (the status is retained as the dispatch-table sentinel
    type for any future pattern).

    **`DriverStrategy` shape (O-CP-1(d) resolution, decided at U-CP-86 — the
    first strategy unit).** The dispatch is a flat enum-keyed branch in
    `_execute_workflow_body`, NOT a callable/class registry. The enum value
    discriminates which materialized strategy runs; the body routes
    `LINEAR_INLINE` → the existing §25.3 inline loop and each non-linear value
    → its dedicated `_execute_<strategy>(...)` function returning
    `(RunResult, steps_executed)`. A heavier callable/class `DriverStrategy`
    abstraction is intentionally NOT introduced (simplicity-first — five
    strategies routed by a closed enum need no indirection layer; the dispatch
    table already enumerates the closed-at-6 `TopologyPattern`).
    """

    LINEAR_INLINE = "linear-inline"
    PARALLELIZATION = "parallelization"
    EVALUATOR_OPTIMIZER = "evaluator-optimizer"
    ORCHESTRATOR_WORKERS = "orchestrator-workers"
    HIERARCHICAL_DELEGATION = "hierarchical-delegation"
    DECENTRALIZED_HANDOFF = "decentralized-handoff"
    NOT_YET_MATERIALIZED = "not-yet-materialized"


# § 25.10.1 — driver-strategy dispatch table (lifts the §25.1
# `_IN_SCOPE_TOPOLOGY` gate). Keyed on the C-CP-10 §10.1 `TopologyPattern`
# enum; enumerates all six members (the closed-at-6 enum — an exhaustiveness
# test asserts no member is missing, so resolution never falls through to a
# KeyError).
_DRIVER_STRATEGY_DISPATCH: Mapping[TopologyPattern, _DriverStrategyStatus] = {
    TopologyPattern.SINGLE_THREADED_LINEAR: _DriverStrategyStatus.LINEAR_INLINE,
    TopologyPattern.PARALLELIZATION: _DriverStrategyStatus.PARALLELIZATION,
    TopologyPattern.ORCHESTRATOR_WORKERS: _DriverStrategyStatus.ORCHESTRATOR_WORKERS,
    TopologyPattern.HIERARCHICAL_DELEGATION: _DriverStrategyStatus.HIERARCHICAL_DELEGATION,
    TopologyPattern.DECENTRALIZED_HANDOFF: _DriverStrategyStatus.DECENTRALIZED_HANDOFF,
    TopologyPattern.EVALUATOR_OPTIMIZER: _DriverStrategyStatus.EVALUATOR_OPTIMIZER,
}


def resolve_driver_strategy(topology_pattern: TopologyPattern) -> _DriverStrategyStatus:
    """Resolve a topology pattern to its driver strategy (C-CP-25 §25.10).

    Replaces the §25.3.1 `_IN_SCOPE_TOPOLOGY` materialization gate. A pattern
    whose strategy has not yet landed (the four non-linear patterns still
    `NOT_YET_MATERIALIZED` after U-CP-86 lands `PARALLELIZATION`) raises
    `TopologyPatternNotYetMaterializedError`. Admissibility
    (C-CP-10 §10.3 / C-CP-11 §11.1) is unchanged — it is rejected at
    workflow-binding time; §25.10 lifts only the *materialization* gate, not
    admissibility (Invariant 2). The typed error is preserved for any future
    non-enumerated topology.
    """
    status = _DRIVER_STRATEGY_DISPATCH[topology_pattern]
    if status is _DriverStrategyStatus.NOT_YET_MATERIALIZED:
        raise TopologyPatternNotYetMaterializedError(topology_pattern)
    return status


_IN_SCOPE_ENGINE_CLASSES: frozenset[EngineClass] = frozenset(
    {
        EngineClass.PURE_PATTERN_NO_ENGINE,
        EngineClass.SAVE_POINT_CHECKPOINT,
        # U-CP-93 (R-FS-1 E-impl-1) — EVENT_SOURCED_REPLAY materialized as
        # resumption-routing impl against cleared C-CP-07/08, following the
        # U-CP-56 SAVE_POINT_CHECKPOINT precedent (added to _IN_SCOPE as impl,
        # "no spec bump"). See the `:1445`-region dispatch branch below.
        # Resumption (resume_at/RESUMPTION) is computed only on the
        # SINGLE_THREADED_LINEAR path; the 5 non-linear strategies are
        # resume-blind for EVERY in-scope engine class (incl. save-point) — they
        # return before the resume-path block. So EVENT_SOURCED_REPLAY + a
        # non-linear topology inherits the same resume-blind behavior save-point
        # already has; non-linear/fan-out resume is the registered B-FANOUT-PAUSE
        # arc (`.harness/beyond-mvp-capability-boundary-ledger.md`), not this unit.
        EngineClass.EVENT_SOURCED_REPLAY,
        # U-CP-94 (R-FS-1 E-impl-2) — WAL_SEGMENT materialized as segment-replay
        # resumption impl against cleared C-CP-07/08, following the U-CP-56 /
        # U-CP-93 precedent. The `:1469`-region dispatch branch computes resume_at
        # via the F2 per-segment prefix join (`_determine_segment_replay_resume_at`,
        # C-CP-08 §8.2 row 5) — a CP→IS read, no CP→runtime import. The durable
        # WAL segment-log substrate (U-RT-121) + the engine-layer recovery-loop
        # firing (U-CP-95 capture_pause/attempt_resume → C-CP-49/50, R-CXA-2
        # go-live) are the genuine distinguishing capability over save-point.
        # Resume-blind on the 5 non-linear strategies, exactly as save-point /
        # EVENT_SOURCED_REPLAY (B-FANOUT-PAUSE arc, not this unit).
        EngineClass.WAL_SEGMENT,
        # U-CP-96 (R-FS-1 E-impl-3a) — RECONCILER_LOOP materialized as
        # level-triggered read/diff/converge resumption (C-CP-08 §8.1
        # `reconciler_converge`) impl against cleared C-CP-07/08 + the v1_33 §7.4
        # substrate-deferral (hand-rolled etcd-style per I-6), following the
        # U-CP-93/94 precedent (added to _IN_SCOPE as impl, "no spec bump"). The
        # `reconciler-converge` dispatch branch (below, after EVENT_SOURCED_REPLAY)
        # computes resume_at via the F2 prefix join
        # (`_determine_reconciler_converge_resume_at`, a CP→IS read; the engine-owned
        # CRD_RECONCILER_LEDGER substrate is U-RT-123, not read here — no CP→runtime
        # import). This is the CP/IS-only resumption-semantics half; the engine-layer
        # recovery-loop firing (U-CP-97) + the durable etcd-style substrate (U-RT-123)
        # + activation (U-RT-124) are E-impl-3b. **RECONCILER_LOOP is the LAST engine
        # class — with it in _IN_SCOPE, _IN_SCOPE == the full closed EngineClass set
        # and the EngineClassNotYetMaterializedError gate (the `not in
        # _IN_SCOPE_ENGINE_CLASSES` raise above) becomes preserved-but-unreachable
        # (the E sub-program closes at the gate level).**
        # Resume-blind on the 5 non-linear strategies, exactly as save-point /
        # EVENT_SOURCED_REPLAY / WAL_SEGMENT (B-FANOUT-PAUSE arc, not this unit).
        EngineClass.RECONCILER_LOOP,
    }
)


# U-CP-95 (R-FS-1 E-impl-2) — engine-layer resume-abort → fail-class mapping.
# The C-CP-22 §22.1 `ResumeOutcomeKind` ABORT_* members that must FAIL the run
# CLOSED on engine-layer recovery, each mapped to its semantically-matching
# existing CP fail-class marker (no new fail-class invented — X-AL-3-clean;
# reuses the C-CP-26 §26.5 constants). The two RESUME_* members are absent by
# construction: a present pause whose resume succeeds proceeds normally. A
# corrupt snapshot → ABORT_SNAPSHOT_CORRUPTED; a revalidation failure →
# ABORT_REVALIDATION_FAILED (unreachable under the default WAL substrate wiring,
# which injects an empty diff-provider + always-succeeds revalidation, but
# handled for correctness if a deployment binds a real diff-provider).
_ENGINE_RESUME_ABORT_FAIL_CLASS: dict[ResumeOutcomeKind, str] = {
    ResumeOutcomeKind.ABORT_SNAPSHOT_CORRUPTED: CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION,
    ResumeOutcomeKind.ABORT_REVALIDATION_FAILED: CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED,
}


# ---------------------------------------------------------------------------
# Substrate Protocols (avoid harness-runtime backward dep)
# ---------------------------------------------------------------------------


@runtime_checkable
class LedgerWriterLike(Protocol):
    """Write-side state-ledger substrate (C-IS-07 §7.1 idempotent append).

    Structurally satisfied by
    `harness_runtime.lifecycle.state_ledger.LedgerWriter`.
    """

    actor: Actor

    def append(self, payload: Any, write_key: Any) -> Any:
        """Append a hash-chain-preserving entry (delegates to IS U-IS-11)."""
        ...

    @property
    def is_genesis(self) -> bool:
        """`True` when no entries exist yet."""
        ...

    @property
    def entry_count(self) -> int:
        """Current ledger entry count (snapshot at construction)."""
        ...


@runtime_checkable
class LedgerReaderLike(Protocol):
    """Read-side state-ledger substrate (C-IS-07 §7.4 implementation-discretion
    primitive; `read_by_idempotency_key(key)` enumerated as authorized).

    Introduced at CP plan v2.12 to materialize U-CP-56 AC #6 (full
    selective replay-resumption per `[[fork-u-cp-56-resumption-underspec]]`
    Path A-modified resolution). Mirrors the LedgerWriterLike read/write
    separation pattern; concretized by a runtime adapter wrapping
    `harness_is.state_ledger_read.LedgerNavigationPrimitive` over a
    `harness_is.state_ledger_write.read_ledger` snapshot.

    Method shape mirrors the IS NavigationPrimitive contract verbatim.
    """

    def read_by_idempotency_key(
        self,
        idempotency_key: Any,
        bounded_window: Any,
    ) -> Any:
        """Read entries by `idempotency_key`.

        The `Any` typing on `idempotency_key`, `bounded_window`, and the
        return shape avoids a CP→IS Protocol-level type dependency. Runtime
        concretization uses `harness_is.types.Identifier` (idempotency_key),
        `harness_is.state_ledger_read.BoundedWindow` (bounded_window),
        `harness_is.state_ledger_read.ReadResult` (return) — callers narrow
        at concrete sites if they need the typed shape.
        """
        ...


@runtime_checkable
class LifecycleEventEmitterLike(Protocol):
    """Lifecycle-event emission surface (§5.1 8-class taxonomy via
    `harness_core.WorkflowEventClass`).

    Structurally satisfied by
    `harness_runtime.lifecycle.lifecycle_emitter.RuntimeLifecycleEventEmitter`.
    """

    def emit(self, event_class: WorkflowEventClass) -> None:
        """Emit one lifecycle event of the given canonical class."""
        ...


@runtime_checkable
class StepDispatcher(Protocol):
    """Step body dispatch surface (per C-CP-25 §25.3.3.4 + U-CP-01 router seam).

    The driver delegates step body invocation through this Protocol. Concrete
    implementations live above the driver (typically in the runtime composition
    layer, which knows about the cap-aware router U-CP-01, the sandbox
    dispatch, the HITL gate, etc.).

    **v1.6 Path A amendment.** `step_context: StepExecutionContext` is a
    keyword-only parameter carrying per-step parent context composed by the
    driver from run-level state. Required for sub-agent dispatch composer
    (C-RT-17) per C-CP-12 §12.2 gate-level composition + C-CP-13 §13.5
    audit-trail-link composition. Existing dispatchers (C-RT-15 inner LLM
    dispatch, C-RT-16 retry/breaker/fallback wrapper) accept the parameter
    but do not consume it at v1.6; the parameter is reserved for v1.7+
    surfaces that may bind step context to the LLM inference span attributes or
    similar. See:
    `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md`
    for the resolution rationale.
    """

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Invoke the step body under the effective binding; return step output.

        Step output is a mapping; the driver accumulates these into the
        terminal `partial_state` / `final_state` of the returned `RunResult`.

        `step_context` carries per-step parent context composed by the driver
        per `StepExecutionContext` per-field semantics (8 fields; 4 composed
        deterministically + 4 MVP-default-bounded). Dispatchers may ignore
        the parameter at v1.6 if they do not need parent context (the C-RT-15
        LLM dispatcher does); dispatchers that need parent context (the
        C-RT-17 sub-agent dispatcher) consume it.
        """
        ...


class StepKindDispatcherNotBoundError(Exception):
    """No dispatcher bound for a `StepKind` at registry lookup (U-RT-59 §14.7).

    Raised by a `StepDispatcherRegistry.lookup(step_kind)` implementation when
    `step_kind` is not bound. The driver's try/except per C-CP-25 §25.3.3.4
    maps this to a `step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND: ...`
    per `Spec_Harness_Runtime_v1.md` v1.6 §14.7 failure-mode taxonomy.

    Declared CP-side (vs runtime-side) so the driver's typed `try/except` can
    catch a CP-owned error without inverting the CP→runtime dependency
    direction. Runtime's `StepKindDispatcherRegistry.lookup` raises this same
    type (imports from here).
    """

    def __init__(self, step_kind: StepKind) -> None:
        super().__init__(f"no StepDispatcher bound for step_kind {step_kind.value!r}")
        self.step_kind = step_kind


@runtime_checkable
class StepDispatcherRegistry(Protocol):
    """Routing-layer surface — frozen `{StepKind → StepDispatcher}` mapping.

    Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.1 + §14.7.7 (C-RT-17). The
    driver invokes `step_dispatchers.lookup(step.kind)` at every per-step
    dispatch site; the returned `StepDispatcher` then dispatches the step
    body via its sync `dispatch(binding, step, *, step_context)` method.

    Structurally satisfied by
    `harness_runtime.lifecycle.step_dispatchers.StepKindDispatcherRegistry`
    (the production composition; bound at bootstrap stage 5 to
    `HarnessContext.step_dispatchers`). The CP driver does not import the
    runtime composition (which would invert the CP→runtime dependency
    direction); it consumes via this Protocol.

    **v1.6 amendment.** Replaces the v1.5 single `step_dispatcher:
    StepDispatcher` parameter at `execute_workflow`. Per spec §14.7.7
    "Driver routing-layer refactor": "Parameter changes from `step_dispatcher:
    StepDispatcher` to `step_dispatchers: StepKindDispatcherRegistry`."
    """

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        """Return the bound dispatcher for `step_kind`.

        Raises
        ------
        StepKindDispatcherNotBoundError
            `step_kind` is not bound in this registry; driver maps to
            `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND`.
        """
        ...


@runtime_checkable
class DriverContext(Protocol):
    """Minimal substrate the driver consumes (subset of HarnessContext).

    Structurally satisfied by
    `harness_runtime.types.HarnessContext`. The CP driver does not import
    `HarnessContext` (which would invert the CP→runtime dependency direction);
    it consumes the substrate via this Protocol.

    `drained_flag` is consumed at U-CP-57 drain composition at the 3 driver
    boundary sites per `Spec_Control_Plane_v1_4.md` §25.4. U-CP-56 happy-path
    iteration never sets this flag itself (per U-CP-57 AC #6 — "Driver never
    calls `ctx.drained_flag.set()` itself"; flag ownership at U-RT-44 signal
    handler per `Spec_Harness_Runtime_v1.md` §11 C-RT-11).
    """

    ledger_writer: LedgerWriterLike
    ledger_reader: LedgerReaderLike
    lifecycle_emitter: LifecycleEventEmitterLike
    drained_flag: asyncio.Event
    # OTel `TracerProvider` substrate per C-OD-25 §25.2 (OD spec v1.8).
    # Driver opens the `workflow.envelope` outer span via
    # `tracer_provider.get_tracer("harness.cp.workflow_driver")`. Typed as
    # `object` to avoid pulling the OTel SDK into the CP protocol surface
    # (HarnessContext exposes the materialized provider with the same
    # `object`-typed field per harness-runtime/types.py).
    tracer_provider: object

    # OPTIONAL ValidatorFramework — operator-opt-in per C-CP-25 §25.3 +
    # Decision 2.D3 (Phase A.2 RATIFIED). When None, the U-CP-61 post-dispatch
    # validation hook is skipped (driver-level opt-out). When bound, the
    # operator-populated validator_registry must cover every step.step_id
    # (Decision 2.D3 in-band opt-out is via no-op validator at registry, not
    # at framework binding). Typed as `object | None` so the CP Protocol does
    # not import the sync facade type — concrete binding at runtime stage 5
    # uses `harness_cp.validator_framework.SyncValidatorFrameworkFacade`
    # (structural match via the `.evaluate(...)` sync method per
    # `SyncValidatorFrameworkLike` Protocol).
    validator_framework: object | None

    # OPTIONAL PauseResumeProtocol — U-RT-87 (v2.20) operator-opt-in per
    # runtime spec v1.21 §14.14.3 workflow_driver per-step pre-entry
    # pause-trigger detection point. When None (default), the per-step
    # pre-entry pause-trigger detection branch sibling to
    # `drained_flag.is_set()` evaluates False (driver-level opt-out;
    # production-default state preserved per spec §14.14.5 invariant 2).
    # When bound, the driver invokes `protocol.capture_pause_snapshot(...)`
    # on `pause_requested_flag.is_set()` + returns `RunStatus.PAUSED`.
    # Typed as `object | None` to avoid pulling
    # `harness_cp.pause_resume_protocol.PauseResumeProtocol` into the
    # Protocol surface (HarnessContext exposes the typed narrowed field
    # per runtime spec v1.21 §4).
    pause_resume_protocol: object | None

    # U-RT-87 (v2.20) caller-side pause-signaling primitive sibling-pattern
    # to `drained_flag` per runtime spec v1.21 §14.14.3. Set by external
    # caller to request driver pause at next per-step pre-entry; polled by
    # the driver as a sibling check to `drained_flag.is_set()`.
    pause_requested_flag: asyncio.Event

    # Multi-tenant scoping key sourced from `RuntimeConfig.tenant_id`. None =
    # single-tenant (the v1.6 MVP default; preserved unchanged at audit-writer
    # via the `_SINGLE_TENANT_TAG` sentinel). Non-None values flow through the
    # 4-substep audit composition (sub_agent_dispatch.py / hitl_gate_composer.py
    # / llm_dispatch.py / audit_writer.py) via `StepExecutionContext.tenant_id`
    # propagation. HarnessContext exposes this as a computed property reading
    # `self.config.tenant_id` so DriverContext is structurally satisfied
    # without duplicating storage. Per workflow_driver_types.py:189-192
    # deferral comment, this is the v1.7+ extension that lifts the v1.6 MVP
    # hardcode at the workflow_driver composition site (binding fix; not a
    # WorkflowManifestEntry schema extension).
    tenant_id: str | None

    # U-RT-101 (C-RT-27 §14.17.2 hook-1 per-workflow-init) — Skill activation
    # emitter + loaded skills. Both default-None-safe at the binding-site
    # arm; structurally satisfied by HarnessContext.skill_activation_emitter
    # + ctx.skills per runtime spec v1.32 §4. Typed as `object | None` to
    # avoid pulling harness_runtime.lifecycle.skill_activation into the CP
    # Protocol surface. When None, the per-workflow-init hook silent-skips
    # per §14.17.5 invariant 3 (operator opt-out path preserved).
    skill_activation_emitter: object | None
    skills: object

    # U-RT-111 (v2.36) — `RuntimeCpIsWiring` carrier per runtime plan v2.36 §1.2
    # ACs #3 + #11. Operator-opt-in MVP; default `None` preserves pre-v2.36
    # production behavior (workflow_driver pause/resume sites silent-skip
    # emission). Typed `object | None` to avoid pulling
    # `harness_runtime.lifecycle.cp_is_wiring.RuntimeCpIsWiring` into the CP
    # Protocol surface (workspace dep-graph discipline — harness-cp does NOT
    # depend on harness-runtime per `harness-cp/pyproject.toml`). When bound,
    # the 3 pause/resume firing sites at workflow_driver.py:546 + :756 + :881
    # invoke `ctx.cp_is_wiring.emit_pause_resume_state_ledger_entry(...)` via
    # `_run_protocol_method_sync(...)` per the same sync-bridging discipline as
    # `protocol.attempt_resume(...)` + `protocol.capture_pause_snapshot(...)`.
    cp_is_wiring: object | None

    # R-003 producer-site lift — zero-arg resolver returning the
    # `procedural_tier_snapshot_ref` Identifier D-derivative sidecar per IS
    # spec v1.3 §C-IS-05 §5.1. Consumed at `_append_step_ledger_entry`
    # (§25.3.3.7 per-step state-ledger write — a workflow-context emission).
    # Typed `object | None` to avoid pulling
    # `harness_runtime.lifecycle.procedural_tier_snapshot` into the CP Protocol
    # surface (workspace dep-graph discipline — harness-cp does NOT depend on
    # harness-runtime). When bound (production, via the frozen `HarnessContext`
    # field set at bootstrap stage 6), `_append_step_ledger_entry` invokes it
    # and populates the sidecar; when `None` (operator opt-out / outside-
    # workflow / test ctx), the sidecar stays `None`.
    procedural_tier_snapshot_resolver: object | None


# ---------------------------------------------------------------------------
# Driver core
# ---------------------------------------------------------------------------


def _compute_run_idempotency_key(
    run_id: str,
    workflow_id: str,
    *,
    extras: Sequence[str] = (),
) -> str:
    """Compose the run-scope idempotency key per C-CP-25 §25.6.

    `run_idempotency_key = sha256(run_id, workflow_id, *extras)`. The manifest
    entry does not carry an `entry_version` field at v1.4 — the extras
    parameter is the extension hook for a future workflow-versioning field.
    """
    h = hashlib.sha256()
    h.update(run_id.encode("utf-8"))
    h.update(b"\x00")
    h.update(workflow_id.encode("utf-8"))
    for extra in extras:
        h.update(b"\x00")
        h.update(extra.encode("utf-8"))
    return h.hexdigest()


def _compute_step_idempotency_key(
    run_idempotency_key: str,
    step_index: int,
    branch_path: str | None = None,
) -> str:
    """Per-step `idempotency_key = sha256(run_idempotency_key, step_index[, branch_path])`
    per C-CP-25 §25.3.3.7 + §25.6 + §25.16 (branch-scoped extension).

    `branch_path` (U-CP-83 / §25.16) enters the composition under fan-out so N
    parallel branches at the *same declared `step_index`* do not collapse to one
    ledger entry under the IS writer's `idempotency_key`-only dedup
    (C-IS-07 §7.5). It derives from the branch identity via
    `workflow_driver_types.compose_branch_path`. The `SINGLE_THREADED_LINEAR`
    path passes `branch_path=None` and composes the existing
    `sha256(run_idempotency_key, step_index)` key **byte-identically**
    (regression-safe — no extra separator is hashed when `branch_path is None`).
    This is a CP-side driver write-key composition change only — no six-field /
    hash-chain / ADR change (§25.16).
    """
    h = hashlib.sha256()
    h.update(run_idempotency_key.encode("utf-8"))
    h.update(b"\x00")
    h.update(str(step_index).encode("utf-8"))
    if branch_path is not None:
        h.update(b"\x00")
        h.update(branch_path.encode("utf-8"))
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Branch buffered/deferred-append substrate (C-CP-25 §25.11/§25.12 — U-CP-82)
# ---------------------------------------------------------------------------
#
# The shared substrate every non-linear topology strategy (U-CP-86..U-CP-90)
# reuses: the buffered-append discipline (D1.b), the deterministic
# branch-index-ordered drain (D1), and the bounded barrier (§25.11). Strategies
# differ in *control flow over steps*; they all defer the ledger *write* through
# this substrate. The `SINGLE_THREADED_LINEAR` strategy is unaffected — it keeps
# the inline per-step append of `_execute_workflow_body` verbatim (§25.12).


class BufferingLedgerWriter:
    """A `LedgerWriterLike` that BUFFERS appends instead of writing through.

    C-CP-25 §25.12 D1.b (the load-bearing buffered/deferred-append mechanism): a
    branch executes its step bodies + emits telemetry but **buffers its pending
    ledger entries** here; the orchestrator **drains the buffers through the
    single real `LedgerWriterLike` in branch-index order at the barrier**
    (`drain_branch_buffers`). Only the ledger WRITE is deferred — step dispatch
    and telemetry still fire inline (so the pre-dispatch gate is never deferred,
    §25.15.2 obligation 2). The inline per-step append of `_execute_workflow_body`
    (which persists in *completion* order under `gather`/`TaskGroup`) is the
    foreclosed anti-pattern for the non-linear strategies.

    Structurally satisfies the same `LedgerWriterLike` Protocol the driver
    consumes, so a branch's `ctx.ledger_writer` is swapped to this instance with
    no change to the per-step entry-*payload* shape. The swap is **necessary but
    not sufficient**: a strategy (U-CP-86+) executing branch steps must ALSO
    compose branch-unique `action_id`s via `compose_branch_step_action_id` and
    branch-scoped idempotency keys via `compose_branch_path` (§25.16) — reusing
    the linear `_append_step_ledger_entry`'s flat `workflow:{wf}:step:{N}`
    `action_id` inside a branch would collide across siblings (the U-CP-81
    forward obligation). `branch_index` is carried so `drain_branch_buffers` can
    order the drain deterministically by branch_index (NOT completion order —
    the §25.12 determinism boundary).
    """

    def __init__(self, *, actor: Actor, branch_index: int) -> None:
        self.actor = actor
        self.branch_index = branch_index
        self._buffer: list[tuple[Any, Any]] = []

    def append(self, payload: Any, write_key: Any) -> None:
        """Buffer the `(payload, write_key)` instead of writing through (§25.12 D1.b)."""
        self._buffer.append((payload, write_key))

    @property
    def is_genesis(self) -> bool:
        """Protocol-completeness only — NOT consulted on the branch-append path.

        A branch only appends; chain position / genesis detection is the single
        real writer's concern (a branch never reads `prior_event_hash`). Reports
        the buffer's own emptiness so the field is well-defined if read.
        """
        return len(self._buffer) == 0

    @property
    def entry_count(self) -> int:
        """Count of buffered (not-yet-drained) entries."""
        return len(self._buffer)

    @property
    def buffered_entries(self) -> list[tuple[Any, Any]]:
        """The ordered pending-entry list (step order within this branch)."""
        return list(self._buffer)


def drain_branch_buffers(
    real_writer: LedgerWriterLike,
    branch_buffers: Iterable[BufferingLedgerWriter],
) -> int:
    """Drain buffered branch entries through the single real writer in
    **branch-index order** at the barrier (C-CP-25 §25.12 D1 / D1.b).

    Realizes ADR-F2 v1.2 §Consequences's single-threaded-write boundary: branch
    *execution* is concurrent, but the resulting ledger *appends* are serialized
    through the one real `LedgerWriterLike` in deterministic branch-index order.
    The hash chain stays **single-parent linear** — no second `prior_event_hash`,
    no DAG entry; this helper only feeds the real writer's existing serialized
    append deterministically.

    `branch_buffers` MAY be collected in branch completion order (whichever
    branch's barrier task finished first); the drain **sorts by `branch_index`**
    so the persisted order is a pure function of `branch_index`, independent of
    which branch's model call returned first (the §25.12 determinism boundary;
    "lowest branch-index on tie"). Within a branch, entries drain in their
    buffered step order. Returns the count of entries drained.

    **Drain-time timestamp — the IS-monotonicity realization of the module's own
    "timestamp records the ledger-*append* event" semantic.** Every buffered
    payload is re-stamped to a single drain-moment timestamp at this — its actual
    append — point, NOT the buffer-time value the strategy supplied. A fan-out is
    one barrier-drain persist event, so one drain = one timestamp. This keeps the
    shared ZERO-tolerance IS ledger (`_CLOCK_SKEW_TOLERANCE = timedelta(0)`)
    strictly non-decreasing for **CAUSALLY-ORDERED** drains: the within-level
    scrambled-completion drain (buffer-time wall-clocks can invert branch-index
    order, but the single barrier drain runs on one thread, so `now()` here is
    `>=` whatever preceded the fan-out), AND the single-path cross-level recursion
    inversion (one `SUB_AGENT_DISPATCH` child drains its entries DURING the
    parent's barrier — causally *before* this post-barrier parent drain — so the
    child's `now()` `<=` the parent's). The buffer-time `timestamp=` the append
    helpers carry is a placeholder this drain overrides; the zero-tolerance writer
    remains the live safety net for the DIRECT (linear / runtime) append paths.

    **NOT covered (a known gap; the runtime concurrency fork).** `drain_timestamp`
    is captured here, OUTSIDE the IS writer's serialization point (the module-level
    `_WRITE_LOCK` inside `append_ledger_entry`). So this is monotonic-by-
    construction ONLY for causally-ordered drains, NOT for **concurrent** appends
    to the shared writer that this drain cannot order: (a) two `SUB_AGENT_DISPATCH`
    SIBLING children draining on separate fan-out threads (each captures its own
    `now()` outside `_WRITE_LOCK`; the lock can serialize their physical appends in
    the opposite order → `NonMonotonicTimestampError`), and (b) a runtime audit /
    cost write interleaving between this drain's capture and its appends. Both are
    unreachable today — the runtime sync/async-bridge deadlock blocks concurrent
    sub-agent recursion end-to-end — and were equally broken under the prior
    fan-out-start-timestamp policy (NOT a regression). The clean fix is
    timestamp-authority INSIDE `_WRITE_LOCK` (an IS write-path change, contract-
    touching) and belongs to the same arc as the deadlock; see
    `.harness/runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md`
    §8 + `test_concurrent_sibling_drains_invert_timestamp` (xfail, strict). The
    §25.12 determinism boundary is untouched regardless (it constrains append
    *order* — still a pure function of branch_index — never timestamp *values*;
    the chain is not byte-stable across replay).
    """
    drain_timestamp = datetime.now(UTC)
    drained = 0
    for buffer in sorted(branch_buffers, key=lambda b: b.branch_index):
        for payload, write_key in buffer.buffered_entries:
            real_writer.append(payload.model_copy(update={"timestamp": drain_timestamp}), write_key)
            drained += 1
    return drained


async def bounded_barrier[T](
    branch_tasks: Iterable[Awaitable[T]],
    *,
    deadline_seconds: float,
) -> list[T]:
    """Await all branch tasks at a barrier, bounded by a wall-clock deadline.

    C-CP-25 §25.11 (bounded barriers): every barrier (`TaskGroup` / `gather`
    join over branches) is wrapped in a wall-clock deadline so a stuck branch
    cannot strand its parent indefinitely. On deadline-exceeded, raises
    `BranchBarrierDeadlineExceededError`.

    **Leak-freedom (a property of the bound, not of cascade-policy).** No branch
    task ever outlives the barrier: on ANY non-clean exit — deadline-exceeded OR
    a branch raising before the deadline — the still-pending sibling tasks are
    cancelled and awaited before control returns, so no orphaned branch keeps
    dispatching effects in the background (the foreclosed `gather`-leaks-orphans
    anti-pattern, §25.15.2 obligation 8). This bounds the primitive's own tasks;
    it does NOT decide the run-level cascade-policy *reaction* (`FAILED` /
    `PARTIAL` / `PAUSED`) — a branch exception is re-raised UNCHANGED for the
    strategy / U-CP-85 to map (§25.15).

    `gather` (not `TaskGroup`) is used deliberately: it is policy-neutral
    (re-raises the original branch exception verbatim), and §25.11 permits it
    "where no cascade-cancel semantic is needed" — U-CP-82's scope. The
    cascade_policy-AWARE structured-cancellation form (TaskGroup, which bakes in
    cancel-siblings-on-failure and would foreclose the `proceed` policy that
    lets siblings run to completion) lands at U-CP-85 (§25.15.2 obligation 8).

    Results are returned in the input (branch) order of `branch_tasks`; the
    deterministic *persisted* order is enforced separately at
    `drain_branch_buffers`.
    """
    tasks = [asyncio.ensure_future(task) for task in branch_tasks]
    timeout_cm = asyncio.timeout(deadline_seconds)
    try:
        async with timeout_cm:
            return await asyncio.gather(*tasks)
    except TimeoutError as exc:
        # Disambiguate the BARRIER deadline from a branch-LOCAL TimeoutError
        # (e.g. a provider client timeout raised INSIDE a branch). Only the
        # former — for which the timeout context actually expired — is the
        # barrier deadline; a branch's own TimeoutError is re-raised UNCHANGED
        # per the policy-neutral contract above (`gather` propagates it verbatim).
        if timeout_cm.expired():
            raise BranchBarrierDeadlineExceededError(deadline_seconds) from exc
        raise
    finally:
        # Leak-freedom: cancel + await any branch task still pending after a
        # non-clean exit (deadline OR a sibling raising) so none outlives the
        # barrier. On the clean path every task is already done → no-op.
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# ---------------------------------------------------------------------------
# U-CP-85 — `cascade_policy` consumption + cascade-cancel reach (C-CP-25 §25.15)
# ---------------------------------------------------------------------------
#
# `CascadePolicy` (`pause` / `proceed` / `cascade-cancel`, C-CP-10 §10.2) is
# declared-but-unconsumed at HEAD; under fan-out it becomes load-bearing. This
# block consumes it per the §25.15.2 eight cascade-cancel obligations (the
# council-resolved Fork A — `.harness/council/r-fs-1-b1-cascade-cancel/`):
#
#   - `cascade_policy_run_status`     — the §25.15.1 on-branch-failure run-level
#                                       status mapping (obl. 6).
#   - `resume_should_redispatch`      — resume-idempotency-terminality (obl. 7).
#   - `cascade_cancel_barrier`        — `asyncio.TaskGroup` structured
#                                       cancellation of not-yet-dispatched
#                                       siblings (obl. 1 + 8); the cascade-cancel
#                                       counterpart to the policy-neutral
#                                       `bounded_barrier`.
#   - `dispatch_branch_step_shielded` — an in-flight effectful dispatch runs to
#                                       completion / deadline-timeout under a
#                                       cascade-cancel (obl. 1 + 3 + 4).
#
# Obligations 2 (no-gate-bypass-by-buffering) and 5 (high-blast-radius
# pre-dispatch gating via the committed C-AS-02 → C-CP-19 → C-CP-16 chain) are
# discharged by a branch dispatching its pre-dispatch gate BEFORE the shielded
# effectful dispatch — the gate is a not-yet-dispatched boundary where a
# cascade-cancel is clean. This block provides the cancellation machinery; the
# concrete branch control flow (gate → shielded dispatch → classify → record) is
# the consuming strategy's (U-CP-88, the first cascade-policy consumer). The
# machinery is unit-proven here against SYNTHETIC branch coroutines; the
# real-strategy + `RunResult.status` e2e lands at U-CP-88.


#: The C-CP-25 §25.15.1 run-level `RunStatus` a fan-out reaches when ≥1 branch
#: FAILS under the given policy (obl. 6). Existing `RunStatus` members only — no
#: new value. `PARTIAL` belongs to `proceed`, NEVER `cascade-cancel`
#: (advisor-caught at the council). The §25.15.1 "`degraded=true`" is SRE
#: graceful-degradation PROSE, not a contracted field — `RunStatus.PARTIAL` is
#: the sole degradation signal (the 8-field `RunResult` carries no `degraded`).
_CASCADE_POLICY_RUN_STATUS: dict[CascadePolicy, RunStatus] = {
    CascadePolicy.CASCADE_CANCEL: RunStatus.FAILED,
    CascadePolicy.PROCEED: RunStatus.PARTIAL,
    CascadePolicy.PAUSE: RunStatus.PAUSED,
}


def cascade_policy_run_status(policy: CascadePolicy) -> RunStatus:
    """Map a `cascade_policy` to its run-level `RunStatus` on a branch failure
    (C-CP-25 §25.15.1 table + §25.15.2 obligation 6).

    The **on-branch-failure** reaction mapping — the run-level status a fan-out
    reaches when ≥1 branch fails under the given policy:

    - ``CASCADE_CANCEL`` → ``RunStatus.FAILED``: the fan-out fails;
      not-yet-dispatched siblings were cancelled (`cascade_cancel_barrier`),
      in-flight steps ran to completion / deadline-timeout.
    - ``PROCEED`` → ``RunStatus.PARTIAL``: siblings ran to completion; the
      aggregator (the strategy's deterministic fold, U-CP-86) sees a partial
      result set carried in the existing ``RunResult.partial_state``. **No
      ``degraded`` boolean is minted** — ``RunStatus.PARTIAL`` is the sole
      degradation signal (the §25.15.1 "``degraded=true``" is SRE prose, not a
      contracted ``RunResult`` field).
    - ``PAUSE`` → ``RunStatus.PAUSED``: the fan-out halts at the HITL/pause
      boundary; composes with the existing PauseResumeProtocol + ``api.resume``
      (C-RT-30) — this mapping does NOT re-build pause-snapshot capture.

    A clean fan-out (no branch failure) is the strategy's normal ``SUCCESS`` path
    and does not consult this function.
    """
    return _CASCADE_POLICY_RUN_STATUS[policy]


def resume_should_redispatch(
    terminal_status: Literal["cancelled", "completed", "timed_out"] | None,
) -> bool:
    """Decide whether `api.resume` may re-dispatch a branch given its persisted
    `branch_metadata.terminal_status` (C-CP-25 §25.15.2 obligation 7 —
    resume-idempotency-terminality).

    A branch that reached ANY dispatch-boundary terminal disposition
    (``cancelled`` / ``completed`` / ``timed_out``) MUST NOT be re-dispatched on
    resume — its terminal entry is persisted (U-CP-84), so re-running it would
    double-dispatch its effects. Only a branch with **no** persisted terminal
    entry (``None`` — it never reached a dispatch boundary, e.g. a fan-out
    interrupted before this branch ran) is re-dispatch-eligible.

    ``api.resume`` (C-RT-30) reads each branch's persisted ``terminal_status``
    via the branch-scoped idempotency key (U-CP-83) and consults this predicate
    before re-dispatching: ``True`` ⟹ eligible; ``False`` ⟹ already-terminal,
    skip.
    """
    return terminal_status is None


#: The barrier↔shield coordination channel for the deadline cut-off (obl. 1).
#: Each enclosing `cascade_cancel_barrier` contributes ITS OWN registry set to a
#: **CHAIN** (outermost-first); a branch's in-flight effectful dispatch
#: (`dispatch_branch_step_shielded`) registers itself in **EVERY** set in the
#: chain, so the deadline watchdog of ANY enclosing barrier can cancel it DIRECTLY
#: — `asyncio.shield` protects an in-flight dispatch from the branch's own
#: cancellation (a sibling failure → the effect runs to completion, obl. 1) but
#: NOT from a direct cancel, so a watchdog's direct `inflight.cancel()` is exactly
#: the "...or barrier-deadline timeout" cut-off. **The chain (not a single set) is
#: load-bearing for NESTED fan-out (e.g. HIERARCHICAL_DELEGATION, U-CP-89): a
#: nested barrier's in-flight dispatch must remain visible to the OUTER deadline
#: watchdog, or the outer deadline would only cancel the outer branch task while
#: the shielded inner dispatch outlives it — the outer deadline would stop being a
#: hard cap.** A nested barrier `.set`s `(*parent_chain, my_set)`; the tightest
#: enclosing deadline that fires first cuts the dispatch. A ContextVar (not an
#: argument) so a deeply-nested branch dispatch reaches the chain without threading
#: it through the strategy's control flow; `None` when the helper is used outside
#: any `cascade_cancel_barrier` (then there is no deadline cut-off — only the
#: shield-drive).
_BRANCH_INFLIGHT_DISPATCHES: ContextVar[tuple[set[asyncio.Future[Any]], ...] | None] = ContextVar(
    "branch_inflight_dispatches", default=None
)


async def cascade_cancel_barrier[T](
    branch_coros: Iterable[Coroutine[Any, Any, T]],
    *,
    deadline_seconds: float,
) -> list[T]:
    """Await all branches under `asyncio.TaskGroup` structured cancellation,
    bounded by a wall-clock deadline (C-CP-25 §25.15.2 obligations 1 + 8 — the
    `cascade-cancel` counterpart to the policy-NEUTRAL `bounded_barrier`).

    The `cascade-cancel` policy form: on the FIRST branch raising, the
    ``TaskGroup`` deterministically cancels every not-yet-finished sibling
    (obligation 8: structured cancellation, no orphan leak — the foreclosed
    ``gather``-leaks-orphans anti-pattern). A sibling whose effectful step is in
    flight runs that step to completion (`dispatch_branch_step_shielded`,
    obligation 1) before the cancellation lands at its next dispatch boundary; a
    sibling at a not-yet-dispatched boundary unwinds cleanly. This barrier is
    used ONLY by `cascade-cancel` (the policy that needs
    cancel-siblings-on-first-failure).

    **`proceed` and `pause` use a DIFFERENT barrier — NOT this one and NOT
    `bounded_barrier` as-is.** `bounded_barrier` (gather, policy-NEUTRAL)
    re-raises a branch exception UNCHANGED and is the bounded-wait used where no
    cascade-cancel semantic is needed — but on a branch failure its ``finally``
    CANCELS the still-pending siblings, so it does NOT implement `proceed`
    either. `proceed` requires siblings to **run to completion** (a
    ``return_exceptions``-collecting barrier → a partial result set →
    `RunStatus.PARTIAL`); `pause` halts the fan-out at the HITL/pause boundary →
    `RunStatus.PAUSED`. Those two FLOWS — and the real high-blast-radius
    pre-dispatch gate (obligation 5: C-AS-02 → C-CP-19 → C-CP-16) — are owed at
    the consuming strategy (U-CP-88), composing with the pure
    `cascade_policy_run_status` mapping. U-CP-85 supplies the cascade-cancel
    barrier + that mapping; it does NOT itself wire the `proceed`/`pause` flows
    or the real gate.

    **The wall-clock deadline is a HARD cap on a stuck branch (§25.11).** Two
    composed mechanisms enforce it so it bounds a branch stuck ANYWHERE:

    - A **deadline watchdog** fires at ``deadline_seconds`` and cancels every
      registered in-flight effectful dispatch (`_BRANCH_INFLIGHT_DISPATCHES`)
      DIRECTLY — ``asyncio.shield`` keeps an in-flight dispatch alive against the
      branch's own cancellation (obligation 1 "...runs to its own completion"),
      so without this direct cut-off a stuck in-flight step would defeat the
      deadline ("...OR barrier-deadline timeout"). A branch whose in-flight step
      is cut this way records ``timed_out``.
    - ``asyncio.timeout(deadline_seconds)`` around the ``TaskGroup`` cancels the
      branch TASKS, bounding a branch stuck at a not-yet-dispatched boundary
      (e.g. a blocking HITL gate) that has no in-flight dispatch for the watchdog
      to cut. Such a branch records ``cancelled`` (no effect dispatched).

    On a branch failure the ``TaskGroup`` raises a ``BaseExceptionGroup``; it
    propagates UNCHANGED for the calling strategy (U-CP-88) to map to
    ``cascade_policy_run_status(CASCADE_CANCEL) == RunStatus.FAILED`` (obligation
    6). On the wall-clock deadline (no branch failure), raises
    ``BranchBarrierDeadlineExceededError`` (§25.11 parity with `bounded_barrier`).
    Results are returned in the input (branch) order of ``branch_coros``; the
    deterministic PERSISTED order is enforced separately at `drain_branch_buffers`
    (the §25.12 boundary).

    `branch_coros` are coroutines (the ``TaskGroup`` owns task creation — unlike
    `bounded_barrier`, which accepts already-scheduled awaitables); each is
    created exactly once, so a non-clean exit cannot leave an un-awaited coroutine.
    """
    inflight_dispatches: set[asyncio.Future[Any]] = set()
    # Compose with any enclosing barrier's chain (nested fan-out): this barrier's
    # set is appended so an inner dispatch registers in BOTH this set and every
    # ancestor set — the outer deadline watchdog stays a hard cap over inner work.
    parent_chain = _BRANCH_INFLIGHT_DISPATCHES.get() or ()
    registry_token = _BRANCH_INFLIGHT_DISPATCHES.set((*parent_chain, inflight_dispatches))

    async def _deadline_cutoff() -> None:
        # At the deadline, cancel each in-flight effectful dispatch DIRECTLY.
        # This — NOT timer ordering — is what makes the deadline a hard cap:
        # `asyncio.shield` keeps an in-flight dispatch alive against the BRANCH's
        # own cancellation (obl. 1 "...runs to its own completion") but NOT
        # against a direct `inflight.cancel()`, so cancelling `inflight` here
        # unblocks the branch's shielded drive REGARDLESS of whether this watchdog
        # or the `asyncio.timeout` below fires first (both orderings converge —
        # empirically verified). Do not "optimize away" this watchdog believing
        # the `asyncio.timeout` alone bounds the in-flight drive — it does not.
        # The `asyncio.timeout` below then unwinds any gate-stuck (no-in-flight)
        # branch the watchdog has nothing to cut.
        await asyncio.sleep(deadline_seconds)
        for inflight in list(inflight_dispatches):
            if not inflight.done():
                inflight.cancel()

    cutoff_task = asyncio.ensure_future(_deadline_cutoff())
    tasks: list[asyncio.Task[T]] = []
    try:
        async with asyncio.timeout(deadline_seconds):
            async with asyncio.TaskGroup() as task_group:
                tasks = [task_group.create_task(coro) for coro in branch_coros]
        return [task.result() for task in tasks]
    except TimeoutError as exc:
        # The barrier deadline fired with no branch failure: `asyncio.timeout`
        # cancelled the TaskGroup body and converted the resulting CancelledError
        # to TimeoutError. (A branch failure instead surfaces as a
        # BaseExceptionGroup, which is NOT a TimeoutError → it propagates
        # unchanged for the strategy to map to FAILED.)
        raise BranchBarrierDeadlineExceededError(deadline_seconds) from exc
    finally:
        # Reap the watchdog (a no-op if it already fired) so it never outlives
        # the barrier, then restore the registry ContextVar.
        cutoff_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cutoff_task
        _BRANCH_INFLIGHT_DISPATCHES.reset(registry_token)


async def dispatch_branch_step_shielded[T](inflight: asyncio.Future[T]) -> T:
    """Await an in-flight effectful step dispatch with `asyncio.shield` so a
    cascade-cancel of this branch does NOT abandon the in-flight effect
    (C-CP-25 §25.15.2 obligation 1).

    The caller schedules the dispatch (``inflight = asyncio.ensure_future(...)``)
    and passes the resulting future so it can classify the branch's terminal
    disposition afterwards (obligation 4). The dispatch is registered in the
    `cascade_cancel_barrier` deadline-cut-off channel (`_BRANCH_INFLIGHT_DISPATCHES`)
    for its lifetime, so the barrier's watchdog can cut it off at the deadline.
    Behavior:

    - **Clean path** (no cancellation): returns the dispatch result.
    - **Cancelled while in flight** (a sibling's cascade-cancel cancels THIS
      branch): the shielded ``inflight`` is driven to completion so the effect
      lands (obligations 1 + 3), then ``CancelledError`` is **re-raised** so the
      cancellation is honored (swallowing it would desync the ``TaskGroup`` and
      keep this branch running work that should stop). The caller classifies
      ``completed`` (the in-flight step ran) and records its step + terminal entry.
    - **The in-flight dispatch ERRORS during the drive** (the model/tool call
      raised, not a cancellation): the dispatch RAN, so its error does NOT
      override the cancellation — it is swallowed here and ``CancelledError`` is
      re-raised; the branch's terminal disposition is ``completed`` (a
      ran-and-errored branch is ``completed``, dispatch-boundary not step-outcome,
      per `append_branch_terminal_ledger_entry`'s closed-set contract; the step's
      failure lives at the step's own entry per obligation 3). Letting the error
      escape would spuriously mark a cancelled branch FAILED and drop its terminal
      record (the silent-audit-gap obligations 3/4 foreclose).
    - **Barrier deadline cuts off the in-flight dispatch** (a watchdog of THIS or
      any enclosing barrier cancels ``inflight`` DIRECTLY): ``asyncio.shield``
      surfaces ``inflight``'s cancellation; ``inflight`` is done+cancelled → the
      caller classifies ``timed_out`` (obligation 1 "...or barrier-deadline
      timeout"). The dispatch registers in EVERY enclosing barrier's registry
      (the `_BRANCH_INFLIGHT_DISPATCHES` chain), so an OUTER deadline is a hard
      cap over inner in-flight work (nested fan-out, U-CP-89).

    A cascade-cancel landing at a not-yet-dispatched boundary (the pre-dispatch
    gate, BEFORE this helper is called) never reaches here — the branch's gate
    ``await`` raises ``CancelledError`` cleanly → ``cancelled`` (obligation 4).

    The caller's classify-then-record-then-reraise idiom (the shape U-CP-88
    follows; `cascade_cancel_barrier` cancels a stuck branch's task at the
    deadline, so a branch reaching this ``except`` was itself cancelled → always
    re-raise to honor it)::

        inflight = asyncio.ensure_future(dispatcher.dispatch(step))
        try:
            await dispatch_branch_step_shielded(inflight)
        except asyncio.CancelledError:
            # The step was DISPATCHED → record its step entry (obligation 3:
            # every dispatched effectful step gets its own step ledger entry,
            # REGARDLESS of terminal disposition — the effect may have landed) on
            # BOTH terminal paths. `completed` = the in-flight step ran to
            # completion; `timed_out` = the barrier deadline cut it off (it ran
            # but did not return). A `cancelled` branch (not-yet-dispatched, no
            # effect) records NO step entry — it is handled at the gate boundary,
            # not here.
            record_step(local)  # obligation 3 — keyed by step index, not result
            terminal = "timed_out" if (inflight.cancelled() or not inflight.done()) else "completed"
            record_terminal(terminal)  # U-CP-84 fresh terminal entry
            raise  # honor the cancellation (the barrier cancelled this branch)
        record_step(local)  # clean: record + continue
    """
    # Register in EVERY enclosing barrier's registry (the chain) so an OUTER
    # deadline watchdog stays a hard cap over this (possibly nested) dispatch.
    chain = _BRANCH_INFLIGHT_DISPATCHES.get()
    if chain:
        for registry in chain:
            registry.add(inflight)
    try:
        return await asyncio.shield(inflight)
    except asyncio.CancelledError:
        if not inflight.done():
            try:
                # Drive the shielded in-flight dispatch to completion (obl. 1) so
                # the landed effect is recordable — do NOT abandon it mid-send.
                # (A deadline watchdog cancels `inflight` DIRECTLY, which surfaces
                # above as `inflight` already done+cancelled, so this drive is
                # bounded by the tightest enclosing deadline, never unbounded.)
                await asyncio.shield(inflight)
            except asyncio.CancelledError:
                # A SECOND cancellation while draining → cut it off (no leak).
                inflight.cancel()
            except Exception:
                # The dispatch ERRORED during the drive. The step RAN (errored)
                # → its disposition is `completed`
                # (dispatch-boundary, not step-outcome); honor the cancellation by
                # re-raising below. Swallowing the dispatch error here (not letting
                # it escape) is what keeps a cancelled-and-errored branch from
                # being spuriously marked FAILED with no terminal record (F2-01).
                pass
        raise
    finally:
        if chain:
            for registry in chain:
                registry.discard(inflight)


def resolve_parent_gate_level(manifest_entry: WorkflowManifestEntry) -> GateLevel:
    """Resolve `step_context.parent_gate_level` from manifest per CP spec v1.20 §6.1.Y.

    Reading A composition: operator-supplied `default_gate_level` flows through
    unchanged; `None` falls back to the v1.6 MVP hardcoded `GateLevel.AUTO`.
    This is the single source of truth for the workflow_driver:738 composition
    site — exposed as a module-level helper so H_T-CP-19 Layer 3 e2e tests
    can exercise the chain without re-implementing the conditional.
    """
    if manifest_entry.default_gate_level is not None:
        return manifest_entry.default_gate_level
    return GateLevel.AUTO


def _run_protocol_method_sync[TProtocolResult](
    coro: Coroutine[Any, Any, TProtocolResult],
) -> TProtocolResult:
    """Run a PauseResumeProtocol async-method coroutine to completion from sync
    driver context.

    The PauseResumeProtocol class declares its methods `async def` per CP spec
    v1.13 §26.1 but the body of `capture_pause_snapshot` + `attempt_resume`
    contains no actual `await` expressions at the v1.21 narrow-scope MVP
    (state-summary serialization + hash composition + reader invocation are
    all synchronous primitives). The workflow_driver runs in a worker thread
    spawned by `asyncio.to_thread` from `harness_runtime.api.run` — no current
    event loop is bound on the worker thread. `asyncio.run` constructs a new
    loop for this single coroutine.

    Per spec v1.21 §14.14.7 deferred-discretion: the sync-bridging mechanism
    is impl-discretion. The MVP uses `asyncio.run`; future arcs may substitute
    a `SyncDispatcherFacade`-style captured-loop bridge if the protocol body
    ever introduces real async I/O (e.g., async snapshot persistence).
    """
    return asyncio.run(coro)


def execute_workflow(
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    *,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    pause_snapshot_input: PauseSnapshot | None = None,
) -> RunResult:
    """Execute the workflow per C-CP-25 §25.3 happy-path discipline.

    Drain semantics are NOT applied at U-CP-56 — drain composition is U-CP-57.
    A `ctx.drained_flag.is_set()` value is not consulted here. To exercise the
    happy-path discipline under U-CP-56 alone, supply a context whose
    `drained_flag` is never set OR omit drain-aware composition by calling
    this function directly.

    Parameters
    ----------
    manifest_entry
        The workflow's manifest entry per §6.1; carries `engine_class`,
        `topology_pattern`, per-step overrides, fallback chain, etc.
    steps
        The step sequence in declaration order (in-session amendment §E to
        spec v1.4 — step sequence is decoupled from manifest_entry).
    run_id
        Harness-unique run identifier; root `idempotency_key` derives from
        this.
    ctx
        Driver context (ledger writer + lifecycle event emitter substrate).
        Structurally satisfied by `HarnessContext` at runtime composition.
    default_model_binding
        Default `(provider, model)` binding for steps without per-step
        override; per C-CP-06 §6.2's caller-supplied default discipline.
    step_dispatchers
        Frozen `{StepKind → StepDispatcher}` routing registry. v1.6
        amendment per C-RT-17 §14.7.7 — replaces the v1.5 single
        `step_dispatcher: StepDispatcher` parameter. Driver routes via
        `step_dispatchers.lookup(step.kind).dispatch(...)` (§25.3.3.4
        opaque-step-body discipline preserved — driver routes on the
        declared enum field, not on opaque payload content).

    Returns
    -------
    RunResult
        Terminal status + accumulated state. `status==SUCCESS` on happy-path
        completion; `status==FAILED` on step body or ledger append failure.

    Raises
    ------
    TopologyPatternNotYetMaterializedError
        `manifest_entry.topology_pattern` is outside the v1.4 in-scope set.
    EngineClassNotYetMaterializedError
        `manifest_entry.engine_class` is outside the v1.4 in-scope set.
    """
    # § 25.4 row "Driver entry" — drain check at entry (U-CP-57 AC #1).
    # If drained at entry, return DRAINED before any state mutation (no
    # workflow.start emit; no ledger append; no validation). Per spec §25.4
    # row 1 + plan v2.11 U-CP-57 AC #1: drain check precedes topology +
    # engine-class validation. Per C-OD-25 §25.1 AC #1 (U-OD-35): the
    # workflow.envelope span opens AFTER this check — drain-at-entry returns
    # before any envelope opens (no observable workflow execution occurred).
    if ctx.drained_flag.is_set():
        return RunResult(
            workflow_id=manifest_entry.workflow_id,
            run_id=run_id,
            status=RunStatus.DRAINED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=None,
        )

    # U-RT-101 (C-RT-27 §14.17.2 hook-1 per-workflow-init activation hook).
    # Pre-condition: emitter bound + hook bound + skills available. When any
    # is missing/None, silent-skip per §14.17.5 invariant 3 (operator opt-out
    # path preserves pre-v1.32 production behavior). Emit one
    # `skill.activation` span per skill returned by the operator-supplied
    # `SkillActivationHook.select_for_workflow_init(...)` policy, with
    # `activation_mode = FRONTMATTER_ONLY` per Q2=(d) hybrid hook-to-enum
    # mapping. Fires AFTER drain check + BEFORE resume detection / first
    # step dispatch per §14.17.2 hook-1 step 4 ordering.
    _emitter = getattr(ctx, "skill_activation_emitter", None)
    _skills = getattr(ctx, "skills", None)
    if _emitter is not None and _skills is not None:
        _hook = getattr(_emitter, "hook", None)
        if _hook is not None:
            # String literal per AS spec v1.7 §14.4 + runtime spec v1.32
            # §14.17.1 enum. Passed as str (NOT importing SkillActivationMode)
            # to preserve workspace dep-graph discipline — harness-cp does
            # NOT depend on harness-runtime per harness-cp/pyproject.toml;
            # the StrEnum value space is the contract surface across
            # workspace package boundaries.
            for _skill_id in _hook.select_for_workflow_init(
                loaded_skills=_skills.keys(),
                workflow_id=manifest_entry.workflow_id,
            ):
                if _skill_id in _skills:
                    _emitter.emit(
                        skill_id=_skill_id,
                        mode="frontmatter_only",
                        workflow_id=manifest_entry.workflow_id,
                        skill=_skills[_skill_id],
                    )

    # U-RT-89 (C-RT-24 §14.14.3) — entry-point resume detection.
    # When the caller supplies a pause_snapshot_input + the operator has bound
    # PauseResumeProtocol at ctx, invoke `attempt_resume(...)` to validate the
    # snapshot's integrity + check for material diff. The MVP fires the
    # STRICT MaterialDiffPolicy default per spec v1.21 change-note adjacent
    # defect (iii); operator-supplied per-resume policy selection is impl-
    # discretion at follow-on composer arc per spec §14.14.7.
    #
    # The resume detection runs BEFORE the workflow.envelope opens — a failed
    # resume (corruption or diff-aborted) returns FAILED without opening a
    # new envelope. A clean resume sets resume_at_step_index that overrides
    # the prefix-replay path at the body per spec §14.14.5 invariant 5
    # mutual-exclusivity (the two paths are non-overlapping).
    resume_at_step_index: int | None = None
    if pause_snapshot_input is not None and ctx.pause_resume_protocol is not None:
        protocol = cast(PauseResumeProtocol, ctx.pause_resume_protocol)
        resume_result = _run_protocol_method_sync(
            protocol.attempt_resume(
                pause_snapshot_input,
                material_diff_policy=MaterialDiffPolicy.STRICT,
            )
        )
        # U-RT-111 v2.38 AC #3 — RESUME_ATTEMPTED CP→IS state-ledger emission.
        # Defensive operator-opt-in: when cp_is_wiring is None, silent-skip.
        # Per-composer kwarg derivation per plan v2.38 §1.2 AC #3.
        _cp_is_wiring = getattr(ctx, "cp_is_wiring", None)
        if _cp_is_wiring is not None:
            _run_protocol_method_sync(
                _cp_is_wiring.emit_pause_resume_state_ledger_entry(
                    workflow_id=manifest_entry.workflow_id,
                    step_id=str(pause_snapshot_input.step_index),
                    protocol_event_kind=(PauseResumeProtocolEventKind.RESUME_ATTEMPTED),
                    event_sequence_id=(pause_snapshot_input.step_index << 2) | 0,
                    protocol_state_snapshot=resume_result.model_dump(mode="json"),
                    # Reading A apply (PR #83 sibling-extension): pass
                    # ActorIdentity str-newtype matching composer signature
                    # `actor: ActorIdentity`. See
                    # `.harness/class_2_fork_u_cp_74_actor_field_malformation.md`.
                    actor=ActorIdentity(ctx.ledger_writer.actor.actor_id),
                )
            )
        if not resume_result.resumed:
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.FAILED,
                terminal_step_index=pause_snapshot_input.step_index,
                partial_state=None,
                final_state=None,
                fail_class=resume_result.fail_class,
            )
        resume_at_step_index = pause_snapshot_input.step_index

    # § C-OD-25 §25.1 — Open the workflow.envelope outer OTel span via
    # ctx.tracer_provider.get_tracer(...).start_as_current_span(...). Every
    # downstream child span (LLM dispatch / tool dispatch / HITL gate /
    # validator / pause-resume / per-server-trust) nests under this envelope
    # via OTel parent-context propagation per §25.4 invariant 3 (U-OD-37 AC #3).
    #
    # Envelope close discipline (U-OD-37 AC #1 + AC #4):
    # - Normal SUCCESS / DRAINED returns leave status UNSET (§25.5 default
    #   — DRAINED is not a fail).
    # - FAILED returns set StatusCode.ERROR with fail_class as description.
    # - Unhandled exceptions inside the body trigger OTel's default discipline
    #   (record_exception=True + set_status_on_exception=True defaults on
    #   start_as_current_span) — exception event recorded with
    #   "exception.type" + status set to ERROR. No explicit try/except wrap
    #   needed; verified at test_envelope_records_exception_on_validation_failure.
    # - Span.end_time_ns reflects actual workflow termination time (context
    #   manager closes on body return; verified at
    #   test_envelope_end_time_reflects_workflow_termination).
    #
    # Resumption (U-OD-37 AC #2): each call to execute_workflow opens a FRESH
    # envelope per §25.4 invariant 1. The prior envelope was closed at
    # pause-snapshot capture per C-CP-26 §26. State-ledger anchoring across
    # envelopes via workflow.run_id + workflow.idempotency_key attributes.
    tracer = cast(TracerProvider, ctx.tracer_provider).get_tracer("harness.cp.workflow_driver")
    with tracer.start_as_current_span("workflow.envelope") as span:
        # C-OD-25 §25.1 — populate the 8 envelope-open attributes from
        # manifest_entry + run identity (workflow.id / run_id / idempotency_key
        # / entry_version / topology_pattern / engine_class / workload_class /
        # persona_tier). Enum values serialize via .value (AC #4 — string
        # form). idempotency_key matches the run-scope key computed inside
        # the body per §25.6 (kept consistent via _compute_run_idempotency_key).
        run_idempotency_key = _compute_run_idempotency_key(
            run_id,
            manifest_entry.workflow_id,
            extras=(str(manifest_entry.entry_version),),
        )
        span.set_attribute("workflow.id", manifest_entry.workflow_id)
        span.set_attribute("workflow.run_id", run_id)
        span.set_attribute("workflow.idempotency_key", run_idempotency_key)
        span.set_attribute("workflow.entry_version", int(manifest_entry.entry_version))
        span.set_attribute("workflow.topology_pattern", manifest_entry.topology_pattern.value)
        span.set_attribute("workflow.engine_class", manifest_entry.engine_class.value)
        span.set_attribute("workflow.workload_class", manifest_entry.workload_class.value)
        span.set_attribute("workflow.persona_tier", manifest_entry.persona_tier.value)

        result, steps_executed = _execute_workflow_body(
            manifest_entry=manifest_entry,
            steps=steps,
            run_id=run_id,
            ctx=ctx,
            default_model_binding=default_model_binding,
            step_dispatchers=step_dispatchers,
            span=span,
            run_idempotency_key=run_idempotency_key,
            resume_at_step_index_override=resume_at_step_index,
        )

        # C-OD-25 §25.1 close-time attributes (4 of 12). Outcome enum serializes
        # via .value. fail_class null on DRAINED per §25.5 default (omit
        # attribute rather than set null). terminal_step_index null on SUCCESS
        # (omit). step_count = steps_executed (single-attribute terminal-only
        # per §25.5 default).
        span.set_attribute("workflow.outcome", result.status.value)
        if result.status is RunStatus.FAILED and result.fail_class is not None:
            span.set_attribute("workflow.fail_class", result.fail_class)
        if result.terminal_step_index is not None:
            span.set_attribute("workflow.terminal_step_index", int(result.terminal_step_index))
        span.set_attribute("workflow.step_count", int(steps_executed))

        # C-OD-25 §25.4 invariant 2 — deterministic close. Set span status
        # from RunResult.status. FAILED → StatusCode.ERROR with fail_class
        # description; SUCCESS / DRAINED leave default UNSET.
        if result.status is RunStatus.FAILED:
            span.set_status(Status(StatusCode.ERROR, result.fail_class or "FAILED"))
        return result


def _execute_workflow_body(
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    *,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    span: Any,
    run_idempotency_key: str,
    resume_at_step_index_override: int | None = None,
) -> tuple[RunResult, int]:
    """Execute the workflow body within the workflow.envelope OTel span.

    Per C-OD-25 §25.1–§25.5 (OD spec v1.8): this helper executes inside the
    envelope opened by execute_workflow above. Returns the RunResult plus the
    count of steps fully executed (body + step.boundary emit + ledger append
    all succeeded) — consumed by the wrapper to populate the
    workflow.step_count close-time attribute (§25.5 default — single-attribute
    terminal-only).

    The run_idempotency_key parameter is computed by the wrapper (per §25.6
    + §25.1 workflow.idempotency_key attribute) and threaded through to keep
    the run-scope key identical between envelope-attribute set and the
    resumption N-lookup.
    """
    # § 25.10 — driver-strategy dispatch (replaces the §25.3.1
    # `_IN_SCOPE_TOPOLOGY` materialization gate). `SINGLE_THREADED_LINEAR`
    # resolves to the existing §25.3 inline loop below; the five non-linear
    # patterns raise `TopologyPatternNotYetMaterializedError` until their
    # strategy units (U-CP-86..U-CP-90) land. Resolution stays at this site so
    # the drain-at-entry check (§25.4, above) still precedes topology
    # validation (U-CP-57 AC #1 / C-OD-25 §25.1 ordering). The engine-class
    # gate is unchanged.
    strategy = resolve_driver_strategy(manifest_entry.topology_pattern)
    if manifest_entry.engine_class not in _IN_SCOPE_ENGINE_CLASSES:
        raise EngineClassNotYetMaterializedError(manifest_entry.engine_class)

    # § 25.10/25.11 — non-linear strategy dispatch (U-CP-86+). A materialized
    # non-linear pattern routes to its dedicated `_execute_<strategy>` and
    # returns here; the `SINGLE_THREADED_LINEAR` inline loop below stays
    # BYTE-UNCHANGED (§25.10 Invariant 1 — regression-safety). The linear-only
    # paths the early return skips (prefix-replay/resume detection, mid-loop
    # drain checks, pause-trigger detection, the per-step validator hook)
    # compose at later strategy units (U-CP-85 cascade_policy / U-CP-88
    # ORCHESTRATOR_WORKERS). `PARALLELIZATION` (U-CP-86) is the happy-path
    # fan-out + deterministic aggregation; `EVALUATOR_OPTIMIZER` (U-CP-87) is
    # the sequential generate→evaluate→regenerate loop. `ORCHESTRATOR_WORKERS`
    # (U-CP-88) dispatches a dynamic worker fan-out under one orchestrator;
    # `HIERARCHICAL_DELEGATION` (U-CP-89) is recursive `ORCHESTRATOR_WORKERS` (one
    # re-entrant level per `SUB_AGENT_DISPATCH` worker, fan-out cap 3 per parent).
    # `DECENTRALIZED_HANDOFF` (U-CP-90) is the single-owner sequential handoff (each
    # per-role stage chains ownership to the next via a `HandoffContext` record; no
    # fan-out, no `SUB_AGENT_DISPATCH`). ALL SIX patterns are now materialized.
    # Cross-level / scrambled-completion timestamp
    # monotonicity on the shared zero-tolerance IS ledger is realized at the drain
    # (`drain_branch_buffers` re-stamps every entry to its append moment); no
    # strategy coordinates a shared timestamp, and a `SUB_AGENT_DISPATCH` child
    # reuses the same recursion seam transparently.
    if strategy is _DriverStrategyStatus.PARALLELIZATION:
        return _execute_parallelization(
            manifest_entry=manifest_entry,
            steps=steps,
            run_id=run_id,
            ctx=ctx,
            default_model_binding=default_model_binding,
            step_dispatchers=step_dispatchers,
            run_idempotency_key=run_idempotency_key,
        )
    if strategy is _DriverStrategyStatus.EVALUATOR_OPTIMIZER:
        return _execute_evaluator_optimizer(
            manifest_entry=manifest_entry,
            steps=steps,
            run_id=run_id,
            ctx=ctx,
            default_model_binding=default_model_binding,
            step_dispatchers=step_dispatchers,
            run_idempotency_key=run_idempotency_key,
        )
    if strategy is _DriverStrategyStatus.ORCHESTRATOR_WORKERS:
        return _execute_orchestrator_workers(
            manifest_entry=manifest_entry,
            steps=steps,
            run_id=run_id,
            ctx=ctx,
            default_model_binding=default_model_binding,
            step_dispatchers=step_dispatchers,
            run_idempotency_key=run_idempotency_key,
        )
    if strategy is _DriverStrategyStatus.HIERARCHICAL_DELEGATION:
        return _execute_hierarchical_delegation(
            manifest_entry=manifest_entry,
            steps=steps,
            run_id=run_id,
            ctx=ctx,
            default_model_binding=default_model_binding,
            step_dispatchers=step_dispatchers,
            run_idempotency_key=run_idempotency_key,
        )
    if strategy is _DriverStrategyStatus.DECENTRALIZED_HANDOFF:
        return _execute_decentralized_handoff(
            manifest_entry=manifest_entry,
            steps=steps,
            run_id=run_id,
            ctx=ctx,
            default_model_binding=default_model_binding,
            step_dispatchers=step_dispatchers,
            run_idempotency_key=run_idempotency_key,
        )

    # Selective per-run replay-resumption via N-lookup over the existing
    # IS `read_by_idempotency_key` primitive (CP plan v2.12 §0.1 +
    # §2.9 U-CP-56 AC #6 re-author; operator-ratified Path A-modified —
    # no new IS prefix-match primitive). For each step index, compute the
    # expected per-step idempotency_key and look it up; advance `resume_at`
    # over the contiguous prefix of materialized steps.
    #
    # U-RT-89 (C-RT-24 §14.14.5 invariant 5): explicit-pause resume override.
    # When the entry-point caller supplied `pause_snapshot_input` + the
    # `attempt_resume(...)` returned `resumed=True`, the resume_at_step_index
    # override REPLACES the prefix-replay path. The two paths are mutually
    # exclusive per spec — explicit-pause resumption handles workflow-layer
    # PauseResumeProtocol resume; prefix-replay handles save-point-checkpoint
    # crash-recovery resumption.
    resume_at = 0
    if resume_at_step_index_override is not None:
        resume_at = resume_at_step_index_override
        if resume_at > 0:
            ctx.lifecycle_emitter.emit(WorkflowEventClass.RESUMPTION)
    elif manifest_entry.engine_class is EngineClass.SAVE_POINT_CHECKPOINT:
        resume_at = _determine_resume_at(
            ctx=ctx,
            run_idempotency_key=run_idempotency_key,
            step_count=len(steps),
            workload_class=manifest_entry.workload_class,
        )
        if resume_at > 0:
            ctx.lifecycle_emitter.emit(WorkflowEventClass.RESUMPTION)
    elif manifest_entry.engine_class is EngineClass.EVENT_SOURCED_REPLAY:
        # U-CP-93 (R-FS-1 E-impl-1) — EVENT_SOURCED_REPLAY resumption-routing.
        # Replay from event history = advance resume_at over the contiguous
        # materialized prefix (C-CP-08 §8.1 `engine_replay`: "no re-execution
        # of activities" — the prefix is not re-dispatched). Under the §8.2
        # row 1 reading the event history joins the F2 state-ledger on
        # `idempotency_key`, so resume_at is computed by the same F2-prefix
        # mechanism as save-point (`_determine_event_replay_resume_at`
        # delegates). The §8.1 *cached-output replay* refinement (replay prior
        # outputs into downstream-visible state) is degenerate at HEAD — the F2
        # ledger carries no activity output and the driver threads no
        # inter-step data flow (B-INTERSTEP) — so it is a registered build arc,
        # not this unit's burden. See `.harness/r-fs-1-e-impl-1-finding.md`.
        resume_at = _determine_event_replay_resume_at(
            ctx=ctx,
            run_idempotency_key=run_idempotency_key,
            step_count=len(steps),
            workload_class=manifest_entry.workload_class,
        )
        if resume_at > 0:
            ctx.lifecycle_emitter.emit(WorkflowEventClass.RESUMPTION)
    elif manifest_entry.engine_class is EngineClass.RECONCILER_LOOP:
        # U-CP-96 (R-FS-1 E-impl-3a) — RECONCILER_LOOP convergence resumption.
        # "Re-derive state from declarative CRDs; reconciler-loop converges through
        # compare-and-swap" (C-CP-08 §8.1 `reconciler_converge`): advance resume_at
        # over the contiguous materialized prefix so already-converged steps are not
        # re-dispatched. Under §8.2 row 4 the reconciler reads the F2 state-ledger
        # (joined on `idempotency_key`) to detect prior actions, so the CP-level
        # resume_at is the same F2-prefix computation save-point / event-replay /
        # segment-replay use (`_determine_reconciler_converge_resume_at` delegates) —
        # a CP→IS read, never a read of the engine-owned CRD_RECONCILER_LEDGER /
        # U-RT-123 substrate (no `harness_cp` → `harness_runtime` import; avoids a
        # CP↔RT cycle). reconciler-loop is an ENGINE-OWNS-SUBSTRATE class
        # (`f2_substrate_join_discipline.py:9-12`, grouped with event-sourced-replay),
        # so the AUTHORITATIVE durable reconciler state lives in U-RT-123 (E-impl-3b)
        # and this CP/IS resume_at is DELIBERATELY degenerate vs save-point (the same
        # accepted bar U-CP-93/94 take). The genuine distinguishing RECONCILER_LOOP
        # capabilities — the hand-rolled etcd-style CAS-lease substrate (U-RT-123) +
        # the engine-layer recovery-loop firing (U-CP-97, appended below) — give this
        # DURABLE_ASYNC class the EVENT_SOURCED_REPLAY resume_at shape PLUS the
        # WAL_SEGMENT-style engine-layer firing; the resume_at here is the (A)
        # resumption-semantics half, the (B) recovery-loop firing follows.
        resume_at = _determine_reconciler_converge_resume_at(
            ctx=ctx,
            run_idempotency_key=run_idempotency_key,
            step_count=len(steps),
            workload_class=manifest_entry.workload_class,
        )
        # U-CP-97 (R-FS-1 E-impl-3c) — RECONCILER_LOOP engine-layer recovery-loop
        # RESUME firing. The engine-native reconverge analogue of the workflow-layer
        # resume, mirroring the U-CP-95 WAL_SEGMENT RESUME firing (below) — duck-typed
        # `ctx.engine_recovery_loop` (no `harness_cp` → `harness_runtime` import), gated
        # by this RECONCILER_LOOP branch so the WAL firing + every non-reconciler path
        # stays behavior-unchanged. Fires `attempt_resume` → `cp.resume-attempted`
        # (C-CP-50) against the U-RT-123 reconciler substrate (U-RT-124 binds it
        # engine-class-aware so the reconverge reads the reconciler store, never the WAL
        # segment-log).
        #
        # GATED on (a) the PRESENCE of a pause record (presence, NOT validity — a
        # present-but-corrupt record still FIRES → ABORT_* → fail closed below; an
        # ordinary step-prefix recovery with no engine pause does not fire; `run_id`
        # run-scopes the record, identical key composition to the capture branch; the
        # WAL precedent's Codex [P1]/[P2] discipline) AND (b) `resume_at < len(steps)` —
        # the run is NOT already complete. (b) is the one RECONCILER-SPECIFIC divergence
        # from the WAL branch and is load-bearing: the reconciler substrate's CAS lease
        # makes a SECOND `attempt_resume` of an already-claimed revision ABORT (the
        # genuine new lease-coordination capability; U-RT-123). So once a run has fully
        # completed (every step committed → `resume_at == len(steps)`), an at-least-once
        # re-drive of the SAME run_id has NOTHING to reconverge, and firing would
        # claim-again → ABORT → spuriously FAIL a finished run. Skipping the fire when
        # complete lets the empty step loop return idempotent SUCCESS — satisfying
        # C-CP-07 §7.4 floor (ii) "idempotency-keyed exactly-once via the F2 ledger". The
        # WAL branch (below) carries NO such guard: its re-resumable substrate returns
        # RESUME_CLEAN (not ABORT) on a completed-run re-drive, so it does NOT fail-close
        # — the fail-closed regression this guard fixes is reconciler-only (a milder
        # PRE-EXISTING WAL exactly-once duplicate-emit on the same path is out of scope
        # here and tracked at `.harness/r-fs-1-e-impl-3c-f1-01-wal-exactly-once.md`). (b)
        # is an UPPER bound ONLY — a step-0 engine pause (resume_at == 0) still fires
        # (Codex [P2.b]); it is the incomplete-vs-complete discriminator, NOT a
        # `resume_at > 0` gate.
        _engine_recovery_loop = getattr(ctx, "engine_recovery_loop", None)
        _resume_engine_pause = (
            _engine_recovery_loop is not None
            and resume_at < len(steps)
            and _engine_recovery_loop.has_pause_record(
                engine_class=manifest_entry.engine_class,
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
            )
        )
        if resume_at > 0 or _resume_engine_pause:
            ctx.lifecycle_emitter.emit(WorkflowEventClass.RESUMPTION)
        if _resume_engine_pause and _engine_recovery_loop is not None:
            _engine_resume = _run_protocol_method_sync(
                _engine_recovery_loop.attempt_resume(
                    engine_class=manifest_entry.engine_class,
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    step_id=str(resume_at),
                    resume_event_id=f"resume:{run_id}:{resume_at}",
                    resume_attempt_count=1,
                    resume_at=datetime.now(UTC).isoformat(),
                )
            )
            # FAIL CLOSED on an aborting reconverge outcome (C-CP-22 §22.1 ABORT_*),
            # mirroring the WAL RESUME firing: a present pause whose reconverge aborts
            # must HALT the run — never proceed past unrecoverable engine state. The
            # `cp.resume-attempted` entry the fire emitted is the durable audit record.
            _abort_fail_class = _ENGINE_RESUME_ABORT_FAIL_CLASS.get(
                _engine_resume.resume_outcome.outcome_kind
            )
            if _abort_fail_class is not None:
                return RunResult(
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    terminal_step_index=None,
                    partial_state=None,
                    final_state=None,
                    fail_class=_abort_fail_class,
                ), 0
    elif manifest_entry.engine_class is EngineClass.WAL_SEGMENT:
        # U-CP-94 (R-FS-1 E-impl-2) — WAL_SEGMENT segment-replay resumption.
        # "Replay from WAL segments; per-segment dedup" (C-CP-08 §8.1
        # `segment_replay`): advance resume_at over the contiguous materialized
        # segment prefix. Under §8.2 row 5 the per-segment ledger entries join
        # the F2 state-ledger on `idempotency_key`, so the segment prefix is the
        # same F2-prefix computation save-point / event-replay use
        # (`_determine_segment_replay_resume_at` delegates) — a CP→IS read, never
        # a read of the U-RT-121 runtime segment-log substrate (no CP→runtime
        # import; resolves the only reading that avoids a CP↔RT cycle, U-CP-94
        # AC). As with EVENT_SOURCED_REPLAY this resume_at semantic is degenerate
        # vs save-point at the CP/IS level (same accepted bar); the genuine
        # distinguishing WAL_SEGMENT capability is the durable segment-log
        # substrate (U-RT-121) + the engine-layer recovery-loop firing below
        # (U-CP-95) — NOT cached-output replay (B-ENGINE-OUTPUT-REPLAY arc).
        resume_at = _determine_segment_replay_resume_at(
            ctx=ctx,
            run_idempotency_key=run_idempotency_key,
            step_count=len(steps),
            workload_class=manifest_entry.workload_class,
        )
        # U-CP-95 (R-FS-1 E-impl-2) — engine-layer recovery-loop RESUME firing.
        # Fire `ctx.engine_recovery_loop.attempt_resume` → `cp.resume-attempted`
        # (C-CP-50) through the CP→IS wiring (R-CXA-2 engine-layer seam),
        # consumed duck-typed (`Any` on the runtime ctx, exactly as `cp_is_wiring`
        # / `pause_resume_protocol`) — no `harness_cp` → `harness_runtime` import.
        #
        # GATED on the PRESENCE of a pause record (`has_pause_record`, a pure
        # non-emitting substrate read) — presence, NOT validity, and NOT
        # `resume_at`:
        #   - resume_at > 0 alone is the ORDINARY step-prefix crash recovery, which
        #     can occur with NO engine pause captured — firing there would emit a
        #     spurious `cp.resume-attempted = ABORT_SNAPSHOT_CORRUPTED` for a clean
        #     recovery, polluting the ledger (Codex [P2.a]); and
        #   - a WAL_SEGMENT engine pause can be captured BEFORE step 0 (resume_at
        #     == 0 yet a real pause record exists) — gating the firing on
        #     resume_at > 0 would silently never resume it (Codex [P2.b]); and
        #   - a present-but-CORRUPT record must still FIRE the resume (which then
        #     classifies it ABORT_* and the driver fails closed below) — the prior
        #     `has_captured_pause` conflated presence with validity, so a corrupt
        #     snapshot was misread as "absent" and silently skipped, losing the
        #     abort record AND resuming past unrecoverable state (Codex [P1-r3-a]).
        # So the presence check is the sole gate. NB: the engine `resume_at` arg is
        # the ResumeAttempt ISO-8601 timestamp — NOT the int step-index (distinct).
        # `run_id` run-scopes the engine pause record (matching the F2 prefix's
        # run_idempotency_key scope) so a fresh run of the same workflow_id never
        # picks up an earlier run's lingering record (Codex [P2]). The capture
        # branch below passes the SAME run_id — identical key composition.
        _engine_recovery_loop = getattr(ctx, "engine_recovery_loop", None)
        _resume_engine_pause = _engine_recovery_loop is not None and (
            _engine_recovery_loop.has_pause_record(
                engine_class=manifest_entry.engine_class,
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
            )
        )
        # RESUMPTION fires when resuming a committed step prefix OR a present
        # engine pause (a step-0 engine pause is a resumption even at resume_at==0).
        if resume_at > 0 or _resume_engine_pause:
            ctx.lifecycle_emitter.emit(WorkflowEventClass.RESUMPTION)
        if _resume_engine_pause and _engine_recovery_loop is not None:
            _engine_resume = _run_protocol_method_sync(
                _engine_recovery_loop.attempt_resume(
                    engine_class=manifest_entry.engine_class,
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    step_id=str(resume_at),
                    resume_event_id=f"resume:{run_id}:{resume_at}",
                    resume_attempt_count=1,
                    resume_at=datetime.now(UTC).isoformat(),
                )
            )
            # FAIL CLOSED on an aborting resume outcome (C-CP-22 §22.1
            # ABORT_SNAPSHOT_CORRUPTED / ABORT_REVALIDATION_FAILED). A present
            # pause whose resume aborts must HALT the run — never proceed past
            # unrecoverable engine state (Codex [P1-r3-b]). Mirrors the
            # workflow-layer precedent (`if not resume_result.resumed: return
            # FAILED` at the C-CP-26 resume branch above). Plain FAILED with the
            # matching CP fail-class marker; operator escalation is a future arc,
            # not silently absorbed here. The `cp.resume-attempted` entry the fire
            # above emitted is the durable audit record of the abort.
            _abort_fail_class = _ENGINE_RESUME_ABORT_FAIL_CLASS.get(
                _engine_resume.resume_outcome.outcome_kind
            )
            if _abort_fail_class is not None:
                return RunResult(
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    terminal_step_index=None,
                    partial_state=None,
                    final_state=None,
                    fail_class=_abort_fail_class,
                ), 0
    # Under pure-pattern-no-engine: no resumption-specific emission per CP spec
    # §25.5 v1.4 scope carve-out (`workflow.resumption` CONDITIONAL row: "At v1.4
    # scope: emit on re-entry if manifest_entry.engine_class ==
    # save-point-checkpoint"). §8.1 declares the 5-class ResumptionKind enum +
    # universal observable behavior at §8.3 — those are the full contract space;
    # §25.5 carves out the v1.4 implementation scope. §8.2 row 3 governs
    # state-ledger native dedup for the pure-pattern engine class (orthogonal
    # to emission scope; row 3 is JOIN discipline, not emission discipline).

    # § 25.3.2 — Emit workflow.start.
    ctx.lifecycle_emitter.emit(WorkflowEventClass.WORKFLOW_START)

    # § 25.3.3 — Iterate steps in declaration order (SINGLE_THREADED_LINEAR
    # has no parallel/fan-out branching). Begin at `resume_at` to skip
    # already-materialized steps from a prior crashed/drained run.
    # `steps_executed` tracks completed-this-envelope step count for the
    # workflow.step_count close-time attribute per C-OD-25 §25.1 (U-OD-36).
    # Fresh-envelope-on-resumption (§25.4 invariant 1 + §25.5 default) means
    # prior re-materialized steps were observed under the prior envelope;
    # this counter reflects only this envelope's executions.
    accumulated: dict[str, Any] = {}
    steps_executed = 0
    for step_index, step in enumerate(steps[resume_at:], start=resume_at):
        # § 25.4 row "Per-step pre-entry" — drain check before entering next
        # step (U-CP-57 AC #2; Path B operator-ratified — no `step.boundary`
        # emit at this site to preserve §5.2 step.kind 5-value enum). On
        # drain: return DRAINED with terminal_step_index = step_index - 1
        # (the prior step is the last fully-completed one).
        if ctx.drained_flag.is_set():
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.DRAINED,
                terminal_step_index=step_index - 1 if step_index > 0 else None,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=None,
            ), steps_executed

        # U-CP-95 (R-FS-1 E-impl-2) — WAL_SEGMENT engine-layer recovery-loop
        # PAUSE firing. The engine-native pause analogue of the workflow-layer
        # `ctx.pause_resume_protocol` fire below (a SEPARATE architectural
        # surface — C-CP-22 engine-layer vs C-CP-26 workflow-layer). Gated on
        # `engine_class == WAL_SEGMENT` + a bound (duck-typed) recovery loop +
        # the pause flag; checked BEFORE the workflow-layer branch so a
        # WAL_SEGMENT engine pause takes precedence and every non-WAL_SEGMENT
        # path stays BYTE-UNCHANGED (CP §25.10 Invariant 1). Fires
        # `capture_pause` → `cp.pause-captured` (C-CP-49) through the CP→IS
        # wiring, activating the R-CXA-2 engine-layer seam in production (the
        # first production caller of `RuntimeEngineRecoveryLoop` —
        # `[[built-but-vacuous-reground-ledger-asis]]`). Consumed duck-typed
        # (`Any` on the runtime ctx, no `harness_cp` → `harness_runtime` import).
        # The engine layer's durable state lives in the U-RT-121 segment log, so
        # the RunResult carries no workflow-layer PauseSnapshot (default None).
        _engine_recovery_loop = getattr(ctx, "engine_recovery_loop", None)
        if (
            manifest_entry.engine_class is EngineClass.WAL_SEGMENT
            and _engine_recovery_loop is not None
            and ctx.pause_requested_flag.is_set()
        ):
            _run_protocol_method_sync(
                _engine_recovery_loop.capture_pause(
                    engine_class=manifest_entry.engine_class,
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    step_id=str(step_index),
                    pause_reason=PauseReason.ENGINE_NATIVE_PAUSE,
                )
            )
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.PAUSED,
                terminal_step_index=step_index - 1 if step_index > 0 else None,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=None,
            ), steps_executed

        # U-CP-97 (R-FS-1 E-impl-3c) — RECONCILER_LOOP engine-layer recovery-loop
        # PAUSE firing. Sibling to the WAL_SEGMENT PAUSE firing above, gated on
        # `engine_class == RECONCILER_LOOP` (mutually exclusive with the WAL gate —
        # a workflow has exactly one engine class), reusing the already-fetched
        # duck-typed `_engine_recovery_loop`. Fires `capture_pause` →
        # `cp.pause-captured` (C-CP-49) against the U-RT-123 reconciler substrate
        # (U-RT-124 binds it engine-class-aware so the convergence state lands in the
        # reconciler store, never the WAL segment-log — the no-cross-contamination
        # invariant). The reconciler's durable state lives in the U-RT-123 store, so
        # the RunResult carries no workflow-layer PauseSnapshot (default None).
        if (
            manifest_entry.engine_class is EngineClass.RECONCILER_LOOP
            and _engine_recovery_loop is not None
            and ctx.pause_requested_flag.is_set()
        ):
            _run_protocol_method_sync(
                _engine_recovery_loop.capture_pause(
                    engine_class=manifest_entry.engine_class,
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    step_id=str(step_index),
                    pause_reason=PauseReason.ENGINE_NATIVE_PAUSE,
                )
            )
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.PAUSED,
                terminal_step_index=step_index - 1 if step_index > 0 else None,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=None,
            ), steps_executed

        # U-RT-89 (C-RT-24 §14.14.3) — per-step pre-entry pause-trigger
        # detection. Sibling check to `ctx.drained_flag.is_set()` above.
        # When the operator has bound PauseResumeProtocol + the caller has
        # signaled pause via `ctx.pause_requested_flag.set()`, capture a
        # PauseSnapshot via the protocol + return RunStatus.PAUSED with the
        # snapshot populated for caller-side resume invocation. MVP fires
        # WorkflowPauseReason.EXPLICIT_OPERATOR as the default reason per
        # spec v1.21 change-note adjacent defect (ii); finer-grained reason
        # selection is impl-discretion at follow-on composer arc per spec
        # §14.14.7.
        if ctx.pause_resume_protocol is not None and ctx.pause_requested_flag.is_set():
            protocol = cast(PauseResumeProtocol, ctx.pause_resume_protocol)
            pause_snapshot = _run_protocol_method_sync(
                protocol.capture_pause_snapshot(
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    step_index=step_index,
                    pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
                )
            )
            # U-RT-111 v2.38 AC #3 — PAUSE_CAPTURED drain-flag CP→IS emission.
            # event_kind_index=1 reserves the low bit for drain-flag path.
            _cp_is_wiring = getattr(ctx, "cp_is_wiring", None)
            if _cp_is_wiring is not None:
                _run_protocol_method_sync(
                    _cp_is_wiring.emit_pause_resume_state_ledger_entry(
                        workflow_id=manifest_entry.workflow_id,
                        step_id=str(step_index),
                        protocol_event_kind=(PauseResumeProtocolEventKind.PAUSE_CAPTURED),
                        event_sequence_id=(step_index << 2) | 1,
                        protocol_state_snapshot=pause_snapshot.model_dump(mode="json"),
                        # Reading A apply (PR #83 sibling-extension): see fork
                        # doc U-CP-74 actor field malformation.
                        actor=ActorIdentity(ctx.ledger_writer.actor.actor_id),
                    )
                )
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.PAUSED,
                terminal_step_index=step_index - 1 if step_index > 0 else None,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=None,
                pause_snapshot=pause_snapshot,
            ), steps_executed

        # § 25.3.3.2 — Resolve binding via U-CP-14.
        # `persona_tier` sourced from manifest_entry per CP spec v1.17 §6.5.3
        # (canonical upstream — §6.1 WorkflowManifestEntry.persona_tier).
        binding = resolve_step_binding(
            manifest_entry,
            str(step.step_id),
            default_model_binding=default_model_binding,
            persona_tier=manifest_entry.persona_tier,
        )

        # U-CP-74 §16.5 (S) sibling-variant CP→IS state-ledger emission.
        # Per CP spec v1.27 §16.5.6 dual-emission discipline: emit only when
        # the per-step override was applied (binding.override_applied=True);
        # absent-override steps inherit manifest defaults and have no
        # override-specific state-ledger entry to emit. Defensive
        # operator-opt-in: when cp_is_wiring is None, silent-skip.
        # post_override_step_config is the StepEffectiveBinding canonical
        # JSON projection per spec §16.5.5 outcome-bytes semantic.
        if binding.override_applied:
            _cp_is_wiring = getattr(ctx, "cp_is_wiring", None)
            if _cp_is_wiring is not None:
                # Reading A apply (PR #83): pass ActorIdentity str-newtype to
                # match composer signature `actor: ActorIdentity` at
                # `per_step_override_evaluator.py:286`. Pre-Reading-A passed
                # `ctx.ledger_writer.actor` (an `Actor` Pydantic model);
                # composer's `str(actor)` produced the Pydantic field-repr
                # instead of the clean identity string. See
                # `.harness/class_2_fork_u_cp_74_actor_field_malformation.md`.
                _run_protocol_method_sync(
                    _cp_is_wiring.emit_override_state_ledger_entry(
                        workflow_id=manifest_entry.workflow_id,
                        step_id=str(step.step_id),
                        post_override_step_config=binding.model_dump(mode="json"),
                        actor=ActorIdentity(ctx.ledger_writer.actor.actor_id),
                    )
                )

        # § 25.3.3.3 — Acquire lease (per §5.3 lease.mechanism substrate;
        # per-engine-class binding under-specified at CP spec v1.4 §B
        # carry-forward — resolved at implementation per c1-orchestration-
        # control SKILL substrate). At v1.4 minimum-viable scope, lease
        # emission is deferred to a follow-up unit when the first
        # lease-requiring engine-class materializes. For pure-pattern-no-
        # engine: no lease per §8.2 row 3 "F2 state-ledger native"
        # substrate reading. For save-point-checkpoint: lease emission
        # deferred (substrate-anchored to c1-orchestration-control SKILL).
        # No lease.acquired emit at v1.4 minimum-viable scope.

        # § 25.3.3.4 — Dispatch step body through injected dispatcher.
        # v1.6 Path A — compose StepExecutionContext from driver-tracked
        # state per the 8-field schema at workflow_driver_types.py. See
        # the type's docstring for per-field semantics + MVP-default
        # rationale. Resolves the C-RT-17 Class 1 fork on StepDispatcher
        # parent-context gap (Path A ratified 2026-05-20).
        step_idempotency_key_pre = _compute_step_idempotency_key(run_idempotency_key, step_index)
        # MVP defaults per C-CP-12 §12.4 + Spec_Control_Plane_v1_6.md §25.2.1:
        # parent_gate_level: sourced from manifest_entry.default_gate_level
        # per CP spec v1.20 §6.1.Y Reading A absorption (X-AL-3 silent-
        # absorption gap closed at v1.20 per
        # `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md`).
        # None → GateLevel.AUTO preserves the v1.6 MVP hardcoded default
        # at construction sites that do not surface the field; operator-
        # supplied (not None) values flow through unchanged.
        # parent_sandbox_tier = TIER_1_PROCESS; parent_entry_hash = ""
        # (child shares parent ledger writer per C-RT-17 §14.7.4); tenant_id
        # sourced from `ctx.tenant_id` (HarnessContext exposes the
        # `RuntimeConfig.tenant_id` value per the v1.7+ deferral comment
        # at workflow_driver_types.py:189-192). None preserves single-tenant
        # default; operator-supplied values flow through the 4-substep audit
        # composition unchanged.
        step_context = StepExecutionContext(
            workflow_id=manifest_entry.workflow_id,
            parent_action_id=(f"workflow:{manifest_entry.workflow_id}:step:{step_index}"),
            parent_gate_level=resolve_parent_gate_level(manifest_entry),
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=ctx.ledger_writer.actor,
            parent_entry_hash="",
            parent_idempotency_key=step_idempotency_key_pre,
            tenant_id=ctx.tenant_id,
            step_index=step_index,
        )
        # v1.6 routing-layer refactor per C-RT-17 §14.7.7: dispatch via
        # registry.lookup(step.kind).dispatch(...) instead of single
        # bound dispatcher. StepKindDispatcherNotBoundError maps to
        # RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND per §14.7 failure-mode
        # taxonomy (documented expected behavior at v1.6 for unbound
        # step_kinds: DECLARATIVE_STEP, TOOL_STEP, HITL_STEP, INFERENCE_STEP
        # — the last is a Class 1 carry-forward per the U-RT-59 landing
        # arc; sub-agent dispatch composer arc bound SUB_AGENT_DISPATCH
        # only at v1.6 MVP).
        try:
            step_output = step_dispatchers.lookup(step.step_kind).dispatch(
                binding, step, step_context=step_context
            )
        except StepKindDispatcherNotBoundError as exc:
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.FAILED,
                terminal_step_index=step_index,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=(f"step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND: {exc}"),
            ), steps_executed
        except BaseException as exc:
            # U-RT-95 (runtime spec v1.24 §14.8.8.4) — driver-side handler for
            # the HITLPauseRequestedSignal typed control-flow exception raised
            # by the HITL gate composer's durable-async branch (§14.8.8.1
            # step 6). The signal inherits BaseException (not Exception) so
            # `except Exception` below does NOT consume it; explicit
            # BaseException catch + class-name match honors the layering
            # discipline (harness-cp cannot import from harness-runtime per
            # the workspace dependency graph). On catch: capture the pause
            # snapshot via ctx.pause_resume_protocol (guaranteed non-None by
            # the §14.8.8.1 step 0 OR-form precondition that gated the
            # signal raise) + return RunStatus.PAUSED with
            # terminal_step_index = step_index - 1 (paused at step N's HITL
            # gate; completed through step N-1).
            if type(exc).__name__ == "HITLPauseRequestedSignal":
                if ctx.pause_resume_protocol is not None and ctx.pause_requested_flag.is_set():
                    protocol = cast(PauseResumeProtocol, ctx.pause_resume_protocol)
                    pause_snapshot = _run_protocol_method_sync(
                        protocol.capture_pause_snapshot(
                            workflow_id=manifest_entry.workflow_id,
                            run_id=run_id,
                            step_index=step_index,
                            pause_reason=WorkflowPauseReason.HITL_PENDING,
                        )
                    )
                    # U-RT-111 v2.38 AC #3 — PAUSE_CAPTURED HITL-signal CP→IS
                    # emission. event_kind_index=2 disambiguates HITL-signal
                    # path from drain-flag path (=1) at same step_index.
                    _cp_is_wiring = getattr(ctx, "cp_is_wiring", None)
                    if _cp_is_wiring is not None:
                        _run_protocol_method_sync(
                            _cp_is_wiring.emit_pause_resume_state_ledger_entry(
                                workflow_id=manifest_entry.workflow_id,
                                step_id=str(step_index),
                                protocol_event_kind=(PauseResumeProtocolEventKind.PAUSE_CAPTURED),
                                event_sequence_id=(step_index << 2) | 2,
                                protocol_state_snapshot=(pause_snapshot.model_dump(mode="json")),
                                # Reading A apply (PR #83 sibling-extension):
                                # see fork doc U-CP-74 actor malformation.
                                actor=ActorIdentity(ctx.ledger_writer.actor.actor_id),
                            )
                        )
                    return RunResult(
                        workflow_id=manifest_entry.workflow_id,
                        run_id=run_id,
                        status=RunStatus.PAUSED,
                        terminal_step_index=(step_index - 1 if step_index > 0 else None),
                        partial_state=dict(accumulated),
                        final_state=None,
                        fail_class=None,
                        pause_snapshot=pause_snapshot,
                    ), steps_executed
                # Defensive — signal fired but pause_resume_protocol absent.
                # Per §14.8.8.1 step 0 OR-form precondition this is
                # unreachable; surface as FAILED for visibility.
            if not isinstance(exc, Exception):
                # Unknown BaseException (KeyboardInterrupt, SystemExit, etc.) —
                # re-raise per Python convention; do not consume.
                raise
            # Spec v1.31 §11 — per-step worker-thread blocking bound exceeded
            # at SyncDispatcherFacade.dispatch's
            # future.result(timeout=config.step_dispatch_timeout_seconds).
            # Discriminated from generic Exception so the fail-class string
            # canonicalizes to RT-FAIL-STEP-DISPATCH-TIMEOUT. Name-match per
            # the HITLPauseRequestedSignal pattern above (harness-cp cannot
            # import from harness-runtime per workspace dependency graph).
            if type(exc).__name__ == "StepDispatchTimeoutError":
                return RunResult(
                    workflow_id=manifest_entry.workflow_id,
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    terminal_step_index=step_index,
                    partial_state=dict(accumulated),
                    final_state=None,
                    fail_class=(f"step-failure: RT-FAIL-STEP-DISPATCH-TIMEOUT: {exc}"),
                ), steps_executed
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.FAILED,
                terminal_step_index=step_index,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=f"step-failure: {type(exc).__name__}: {exc}",
            ), steps_executed

        # § 25.3.3.5 — Emit step.boundary.
        ctx.lifecycle_emitter.emit(WorkflowEventClass.STEP_BOUNDARY)

        # § 25.3.3.6 — Release lease (deferred per §25.3.3.3 above).

        # § 25.3.5 (NEW at v1.10) — U-CP-61 post-dispatch validation hook.
        # Per C-CP-25 §25.3 "post-dispatch, pre-ledger-append validation
        # hook". Operator-opt-in: skip when ctx.validator_framework is None
        # (driver-level opt-out). When bound, the framework returns a
        # ValidatorEvaluation; the next_action drives the branch:
        #   PROCEED   → fall through to ledger append (normal flow)
        #   RETRY     → caller's retry wrapper (C-RT-16) handles; pass through
        #               here (the framework body has no retry-state visibility;
        #               the U-CP-60 convert_revalidate_to_permanent_fail() is
        #               invoked externally on budget exhaustion). v1.10 MVP:
        #               proceeds-with-validator.revalidation event emit.
        #   ESCALATE_HITL → emit validator.escalation event; proceeds-with-
        #               escalation-marker. Actual HITL gate dispatch (per spec
        #               §25.7 invariant 4) is a future arc; v1.10 MVP emits the
        #               span linking-to subsequent hitl.gate.evaluated per
        #               §C-OD-29.1 row 10 + F2-02 absorption.
        #   ABORT     → return RunResult(FAILED) with CP-FAIL-VALIDATOR-PERMANENT
        if ctx.validator_framework is not None:
            tracer = cast(TracerProvider, ctx.tracer_provider).get_tracer(
                "harness.cp.workflow_driver"
            )
            with tracer.start_as_current_span("validator.evaluate") as evaluate_span:
                try:
                    evaluation: ValidatorEvaluation = cast(
                        "SyncValidatorFrameworkFacade", ctx.validator_framework
                    ).evaluate(
                        step,
                        step_output,
                        step_context=step_context,
                    )
                except Exception as exc:
                    evaluate_span.record_exception(exc)
                    return RunResult(
                        workflow_id=manifest_entry.workflow_id,
                        run_id=run_id,
                        status=RunStatus.FAILED,
                        terminal_step_index=step_index,
                        partial_state=dict(accumulated),
                        final_state=None,
                        fail_class=(f"validator-framework-failure: {type(exc).__name__}: {exc}"),
                    ), steps_executed

                # §C-OD-29.1 outer envelope (3 attrs).
                for attr_name, attr_value in evaluation.span_attributes.items():
                    evaluate_span.set_attribute(attr_name, attr_value)

                # AC #4 — populate validator.escalation.parent_hitl_span_id
                # when outcome=ESCALATE (links to subsequent hitl.gate.evaluated
                # span per F2-02 absorption). v1.10 MVP: use current span_id
                # as the parent-link marker; future HITL gate composer reads
                # this attribute to anchor its parent context.
                if evaluation.result.outcome.value == "escalate":
                    parent_hitl_span_id = format(evaluate_span.get_span_context().span_id, "016x")
                    evaluate_span.set_attribute(
                        "validator.escalation.parent_hitl_span_id",
                        parent_hitl_span_id,
                    )
                    if evaluation.result.fail_class is not None:
                        evaluate_span.set_attribute(
                            "validator.escalation.fail_class",
                            evaluation.result.fail_class.value,
                        )

                # AC #5 branch on next_action.
                if evaluation.next_action.value == "abort":
                    return RunResult(
                        workflow_id=manifest_entry.workflow_id,
                        run_id=run_id,
                        status=RunStatus.FAILED,
                        terminal_step_index=step_index,
                        partial_state=dict(accumulated),
                        final_state=None,
                        fail_class=(
                            f"CP-FAIL-VALIDATOR-PERMANENT: "
                            f"validator returned PERMANENT_FAIL at step_id="
                            f"{step.step_id!r}"
                        ),
                    ), steps_executed

                # Reading B v1.22 §14.15 — ESCALATE_HITL mid-step re-entry.
                # Per C-CP-28 §25.4 invariant 4: "ESCALATE always emits HITL
                # gate. Escalation cannot be silently dropped." Fires the
                # ValidatorEscalationGateComposer mid-step pre-ledger-append
                # per C-CP-28 §25.3 + §25.4 invariant 2. Operator-opt-in:
                # only when both validator_framework AND ask_user_question_
                # surface are bound at ctx (production paths supply both;
                # test paths may set ask_user_question_surface = None and
                # the escalation outcome will fail-closed).
                if evaluation.next_action.value == "escalate_hitl":
                    ask_user_question_surface = getattr(ctx, "ask_user_question_surface", None)
                    escalation_brief = evaluation.result.escalation_brief
                    if ask_user_question_surface is not None and escalation_brief is not None:
                        # Lazy import to avoid cycle (runtime → cp → runtime).
                        # GateLevel is module-level imported at line 51;
                        # do NOT lazy-import here (would shadow + break
                        # line 735's GateLevel.AUTO reference).
                        from harness_runtime.lifecycle.validator_escalation_composer import (
                            ValidatorEscalationGateAuditComposeError,
                            ValidatorEscalationGateRejectedError,
                            ValidatorEscalationGateTimeoutError,
                            compose_validator_escalation_gate,
                        )

                        from harness_cp.validator_fail_transient_staircase import (
                            CrossTrustBoundaryState,
                        )

                        try:
                            # Async composer bridged to sync driver context
                            # per `_run_protocol_method_sync` pattern (analog
                            # of PauseResumeProtocol bridging at U-CP-62).
                            hitl_response = _run_protocol_method_sync(
                                compose_validator_escalation_gate(
                                    ask_user_question_surface=ask_user_question_surface,
                                    brief=escalation_brief,
                                    step_action_id=str(step_context.parent_action_id),
                                    # v1.22 MVP sentinels per spec §14.15.8
                                    # deferred-discretion; full cross-trust-
                                    # state derivation gated on follow-on arc
                                    # per scoping doc adjacent observation (c).
                                    cross_trust_state=CrossTrustBoundaryState.NONE,
                                    gate_level=GateLevel.ASK,
                                    tracer_provider=ctx.tracer_provider,
                                )
                            )
                        except ValidatorEscalationGateRejectedError as exc:
                            return RunResult(
                                workflow_id=manifest_entry.workflow_id,
                                run_id=run_id,
                                status=RunStatus.FAILED,
                                terminal_step_index=step_index,
                                partial_state=dict(accumulated),
                                final_state=None,
                                fail_class=(
                                    f"RT-FAIL-HITL-GATE-REJECTED: "
                                    f"validator-escalation rejected at "
                                    f"step_id={step.step_id!r}: {exc}"
                                ),
                            ), steps_executed
                        except ValidatorEscalationGateTimeoutError as exc:
                            return RunResult(
                                workflow_id=manifest_entry.workflow_id,
                                run_id=run_id,
                                status=RunStatus.FAILED,
                                terminal_step_index=step_index,
                                partial_state=dict(accumulated),
                                final_state=None,
                                fail_class=(
                                    f"RT-FAIL-HITL-GATE-TIMEOUT: "
                                    f"validator-escalation timed out at "
                                    f"step_id={step.step_id!r}: {exc}"
                                ),
                            ), steps_executed
                        except ValidatorEscalationGateAuditComposeError as exc:
                            return RunResult(
                                workflow_id=manifest_entry.workflow_id,
                                run_id=run_id,
                                status=RunStatus.FAILED,
                                terminal_step_index=step_index,
                                partial_state=dict(accumulated),
                                final_state=None,
                                fail_class=(
                                    f"RT-FAIL-VALIDATOR-ESCALATION-GATE-COMPOSE: "
                                    f"audit-compose failed at step_id="
                                    f"{step.step_id!r}: {exc}"
                                ),
                            ), steps_executed

                        # APPROVE / EDIT / RESPOND — proceed to ledger append.
                        # Per spec §14.15.8 deferred-discretion: EDIT semantics
                        # (whether to mutate step_output) is implementer-
                        # discretion at v1.22 MVP — proceed-with-original-
                        # outcome is the safe default; future arc may apply
                        # operator edits to step_output. RESPOND: operator
                        # response recorded in audit (deferred to follow-on
                        # CP composer arc per scoping doc adjacent obs (d));
                        # workflow proceeds with original validator outcome.
                        _ = hitl_response

        # § 25.3.3.7 — State-ledger append via U-IS-11 composition.
        # Reuse pre-dispatch step_idempotency_key composed at the
        # StepExecutionContext site above (identical per-step value).
        step_idempotency_key = step_idempotency_key_pre
        try:
            _append_step_ledger_entry(
                ctx=ctx,
                workflow_id=manifest_entry.workflow_id,
                step_index=step_index,
                step_idempotency_key=step_idempotency_key,
                step_output=step_output,
            )
        except Exception as exc:
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.FAILED,
                terminal_step_index=step_index,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=f"ledger-append-failed: {type(exc).__name__}: {exc}",
            ), steps_executed

        # Accumulate step output under its step id for terminal state.
        accumulated[str(step.step_id)] = dict(step_output)
        # Step is fully complete (body + step.boundary + ledger append all
        # succeeded). Increment the workflow.step_count carrier per §C-OD-25
        # (U-OD-36).
        steps_executed += 1

        # § 25.4 row "Per-step post-exit" — drain check after step body
        # completes + step.boundary emitted + ledger append persisted
        # (U-CP-57 AC #3). On drain: return DRAINED with terminal_step_index
        # = this step (it counted; its ledger entry has persisted per
        # U-IS-11 append discipline).
        if ctx.drained_flag.is_set():
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.DRAINED,
                terminal_step_index=step_index,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=None,
            ), steps_executed

    # § 25.3.4 + § 25.3.5 — Terminal SUCCESS return. No new event class at
    # terminal exit; the absence of a further step.boundary plus the
    # RunResult.status=SUCCESS return is the terminal observable.
    return RunResult(
        workflow_id=manifest_entry.workflow_id,
        run_id=run_id,
        status=RunStatus.SUCCESS,
        terminal_step_index=None,
        partial_state=None,
        final_state=dict(accumulated),
        fail_class=None,
    ), steps_executed


def _determine_resume_at(
    *,
    ctx: DriverContext,
    run_idempotency_key: str,
    step_count: int,
    workload_class: Any,
) -> int:
    """Determine the resume-at index for selective replay-resumption (§25.6).

    Per CP plan v2.12 §2.9 U-CP-56 AC #6: under save-point-checkpoint binding,
    for each step index `i ∈ [0, step_count)`, compute the expected per-step
    idempotency_key and query the IS state-ledger via
    `ctx.ledger_reader.read_by_idempotency_key`. Advance over the contiguous
    prefix of materialized steps; stop at the first step whose expected key
    returns zero entries.

    Returns the index of the first step that needs to execute (i.e., the
    count of already-materialized contiguous-prefix steps). Returns 0 for a
    genesis run (no prior entries match this run's expected keys).

    Conservative semantic — gap behavior: if the ledger contains a gap
    (e.g., step 0 + step 2 entries exist but step 1 missing), the
    `resume_at` advances only over the contiguous prefix (returns 1 in
    that case). Gap-fill resumption is out of scope at v2.12.
    """
    # Lazy import to keep the module's import surface narrow and to avoid
    # pulling IS-read at module load. The `BoundedWindow` shape is the
    # IS-side bounding contract per C-IS-07 §7.2.
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_is.state_ledger_read import BoundedWindow

    # The bounding window's `max_entries` must be ≥ 1 (positive). Use the
    # ledger's current entry_count as an upper bound, falling back to a
    # nonzero value for a genesis ledger (returns no entries — correct).
    window_size = max(1, ctx.ledger_writer.entry_count)
    window = BoundedWindow(max_entries=window_size, workload_class=workload_class)

    for i in range(step_count):
        expected_step_key = _compute_step_idempotency_key(run_idempotency_key, i)
        result = ctx.ledger_reader.read_by_idempotency_key(
            Identifier(expected_step_key),
            window,
        )
        if not result.entries:
            return i
    return step_count


def _determine_event_replay_resume_at(
    *,
    ctx: DriverContext,
    run_idempotency_key: str,
    step_count: int,
    workload_class: Any,
) -> int:
    """Determine resume-at for EVENT_SOURCED_REPLAY (C-CP-08 §8.1 `engine_replay`).

    Named seam for engine-event-history replay resumption (U-CP-93). At HEAD it
    delegates to `_determine_resume_at`: under C-CP-08 §8.2 row 1 the engine
    event history joins the F2 state-ledger on `idempotency_key`, so the
    resume-at index — the count of contiguous already-materialized steps — is
    the identical F2-prefix computation save-point uses. EVENT_SOURCED_REPLAY's
    §8.1 distinction ("no re-execution of activities") manifests in the driver
    as the materialized prefix not being re-dispatched (the loop begins at
    `resume_at`), exactly as for save-point.

    The §8.1 *cached-output replay* refinement — replaying prior activity
    outputs into downstream-visible state so post-resume steps observe them
    deterministically — is **degenerate at HEAD and out of this unit's scope**:
    the F2 `EntryPayload` carries no activity output (only `response_hash`), and
    the driver threads no inter-step data flow (B-INTERSTEP). It is a registered
    build arc, not a silent defer. See `.harness/r-fs-1-e-impl-1-finding.md`.
    This helper is the extension point where that refinement lands once the
    output-carrying event-history substrate + inter-step data flow exist.
    """
    return _determine_resume_at(
        ctx=ctx,
        run_idempotency_key=run_idempotency_key,
        step_count=step_count,
        workload_class=workload_class,
    )


def _determine_segment_replay_resume_at(
    *,
    ctx: DriverContext,
    run_idempotency_key: str,
    step_count: int,
    workload_class: Any,
) -> int:
    """Determine resume-at for WAL_SEGMENT (C-CP-08 §8.1 `segment_replay`).

    Named seam for WAL-segment replay resumption (U-CP-94). At HEAD it delegates
    to `_determine_resume_at`: under C-CP-08 §8.2 row 5 the per-segment ledger
    entries join the F2 state-ledger on `idempotency_key`, so the resume-at index
    — the count of the contiguous already-materialized segment prefix — is the
    identical F2-prefix computation save-point / event-replay use. WAL_SEGMENT's
    §8.1 distinction ("replay from WAL segments; per-segment dedup") manifests in
    the driver as the materialized segment prefix not being re-dispatched (the
    loop begins at `resume_at`), and the F2 idempotency-key join is the
    per-segment dedup (a re-materialized segment's key already resolves to an
    entry → it is not re-applied).

    This is the CP→IS reading the U-CP-94 AC names as the only one that avoids a
    CP↔RT cycle (the CP driver cannot import `harness_runtime`, so it cannot read
    the U-RT-121 segment-log substrate directly). The durable segment-log
    substrate (U-RT-121) is what `ctx.engine_recovery_loop` fires against for the
    engine-layer pause/resume entries (U-CP-95) — it is NOT the `resume_at`
    source. As with EVENT_SOURCED_REPLAY (`.harness/r-fs-1-e-impl-1-finding.md`)
    this CP/IS-level resume_at is degenerate vs save-point; the genuine
    distinguishing WAL_SEGMENT capability is the durable substrate + recovery
    loop firing, not a richer prefix computation here.
    """
    return _determine_resume_at(
        ctx=ctx,
        run_idempotency_key=run_idempotency_key,
        step_count=step_count,
        workload_class=workload_class,
    )


def _determine_reconciler_converge_resume_at(
    *,
    ctx: DriverContext,
    run_idempotency_key: str,
    step_count: int,
    workload_class: Any,
) -> int:
    """Determine resume-at for RECONCILER_LOOP (C-CP-08 §8.1 `reconciler_converge`).

    Named seam for reconciler-loop convergence resumption (U-CP-96). At HEAD it
    delegates to `_determine_resume_at`: under C-CP-08 §8.2 row 4 the reconciler
    reads the F2 state-ledger (joined on `idempotency_key`) to detect prior
    actions, so the resume-at index — the count of the contiguous already-converged
    prefix — is the identical F2-prefix computation save-point / event-replay /
    segment-replay use. RECONCILER_LOOP's §8.1 distinction ("re-derive state from
    declarative CRDs; reconciler-loop converges through compare-and-swap")
    manifests in the driver as the materialized prefix not being re-dispatched
    (the loop begins at `resume_at`), and the F2 idempotency-key join is the
    convergence dedup (an already-converged step's key resolves to an entry → it
    is not re-applied).

    reconciler-loop is an ENGINE-OWNS-SUBSTRATE class
    (`f2_substrate_join_discipline.py:9-12`, grouped with event-sourced-replay; F2
    join `CRD_RECONCILER_LEDGER`): the AUTHORITATIVE durable reconciler state lives
    in the engine-owned, hand-rolled etcd-style store (U-RT-123, E-impl-3b), NOT
    this CP→IS F2-overlay read. The CP driver cannot import `harness_runtime`, so
    it cannot read that store directly — the only reading that avoids a CP↔RT cycle
    (U-CP-96 AC). As with EVENT_SOURCED_REPLAY (`.harness/r-fs-1-e-impl-1-finding.md`)
    and WAL_SEGMENT (`.harness/r-fs-1-e-impl-2-finding.md`) this CP/IS-level resume_at is
    DELIBERATELY degenerate vs save-point — a sharper engine-owns-vs-overlay split
    than WAL had, which makes the "if a genuinely engine-owned resume_at is needed
    it folds into the runtime layer (U-RT-124), never a new CP→RT edge" contingency
    MORE warranted for reconciler, not less (mirrors the U-CP-94 hedge, a fortiori).
    The genuine distinguishing RECONCILER_LOOP capabilities are the durable
    CAS-lease substrate (U-RT-123) + the engine-layer recovery-loop firing
    (U-CP-97), not a richer prefix computation here.
    """
    return _determine_resume_at(
        ctx=ctx,
        run_idempotency_key=run_idempotency_key,
        step_count=step_count,
        workload_class=workload_class,
    )


def _append_step_ledger_entry(
    *,
    ctx: DriverContext,
    workflow_id: str,
    step_index: int,
    step_idempotency_key: str,
    step_output: Mapping[str, Any],
) -> None:
    """Compose + append the per-step state-ledger entry per § 25.3.3.7.

    Uses the IS-exported `EntryPayload` + `WriteKey` shapes (C-IS-07 §7.1).
    Imported lazily to avoid pulling IS-write at module load.
    """
    # Lazy-import to keep the module's import surface narrow.
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_is.state_ledger_write import EntryPayload, WriteKey

    action_id = ActionID(f"workflow:{workflow_id}:step:{step_index}")
    # R-003 producer-site lift — populate the `procedural_tier_snapshot_ref`
    # D-derivative sidecar (IS spec v1.3 §C-IS-05 §5.1) for this workflow-
    # context per-step emission. The resolver arrives via the DriverContext
    # Protocol (never an import); `getattr` defensive-reads it the same way the
    # `cp_is_wiring` firing sites do (operator-opt-out / test ctx → `None`).
    _resolver = getattr(ctx, "procedural_tier_snapshot_resolver", None)
    _procedural_tier_snapshot_ref = _resolver() if _resolver is not None else None
    # `Identifier` is the IS-typed string newtype for state-ledger string ids;
    # we pass through the action_id verbatim plus the idempotency hex.
    payload = EntryPayload(
        action_id=Identifier(str(action_id)),
        idempotency_key=Identifier(step_idempotency_key),
        actor=ctx.ledger_writer.actor,
        timestamp=datetime.now(UTC),
        procedural_tier_snapshot_ref=_procedural_tier_snapshot_ref,
    )
    write_key = WriteKey(
        thread_id=Identifier(workflow_id),
        step_id=Identifier(str(step_index)),
        idempotency_key=Identifier(step_idempotency_key),
    )
    ctx.ledger_writer.append(payload, write_key)
    # Discard return value — driver does not branch on append vs idempotent-noop;
    # both outcomes leave the ledger correctly composed per C-IS-07 §7.1.


# ---------------------------------------------------------------------------
# Branch ledger write-cadence (C-CP-25 §25.13 + IS §5.4 + runtime §2.2(c) — U-CP-84)
# ---------------------------------------------------------------------------
#
# The producer-cadence by which the CP WorkflowDriver populates the IS
# `branch_metadata` sidecar under a non-linear topology strategy (U-CP-86+). Two
# helpers, both buffering into the branch's own `BufferingLedgerWriter` (U-CP-82)
# so the single barrier drain (`drain_branch_buffers`) serializes them in
# branch-index order with the existing single-writer discipline — NO change to
# `drain_branch_buffers`, NO second `prior_event_hash` (D1). The linear
# `_append_step_ledger_entry` is unaffected (its `branch_metadata` stays the
# carrier default `None`).
#
# Timestamp discipline (the determinism-boundary ⟂ IS-monotonicity interaction).
# The IS writer enforces a ZERO-tolerance non-decreasing-timestamp invariant
# (`state_ledger_write.append_ledger_entry`, `_CLOCK_SKEW_TOLERANCE = timedelta(0)`),
# while the drain persists in branch-index order independent of which branch's
# model call returned first (§25.12). Wall-clock stamps captured at branch
# *execution* time would therefore trip `NonMonotonicTimestampError` once a
# lower-branch-index entry happens to be stamped later than a higher one — and,
# under recursion, a `SUB_AGENT_DISPATCH` child sharing the writer drains its
# entries DURING the parent's barrier (before the parent's LATE post-barrier
# drain), a cross-level inversion the within-level shared-timestamp policy can't
# reach. This is NOT a spec contradiction (§25.12 constrains append *order*, not
# timestamp *values*; the canonical reading — consistent with the linear path —
# is that the timestamp records the ledger-*append* event, and a fan-out is one
# barrier-drain persist event). The realization: `drain_branch_buffers` re-stamps
# every entry to a single drain-moment timestamp at its actual append point, so
# physical-append-order == timestamp-order for **causally-ordered** drains —
# every level reached through the single-threaded recursion seam, plus the
# interleaved DIRECT linear-inline writer, are serialized in causal order and stay
# non-decreasing. This is NOT "by construction" for **concurrent** appends the
# drain cannot order: `drain_timestamp` is captured OUTSIDE the IS writer's
# `_WRITE_LOCK`, so two sibling `SUB_AGENT_DISPATCH` children draining on separate
# fan-out threads (or a runtime audit / cost write interleaving the lock between
# this capture and its appends) can still invert → `NonMonotonicTimestampError`.
# That is a known gap — unreachable today behind the runtime sync/async-bridge
# deadlock, and equally broken under the prior fan-out-start-timestamp policy (NOT
# a regression); the clean fix is timestamp-authority INSIDE `_WRITE_LOCK` (an IS
# write-path change, contract-touching) belonging to the same arc as the deadlock.
# See `.harness/runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md`
# §8 + `drain_branch_buffers` + `test_concurrent_sibling_drains_invert_timestamp`
# (xfail, strict). The `timestamp=` these helpers
# carry is a buffer-time placeholder the drain overrides (it never reaches the
# ledger; see `drain_branch_buffers`). The R-003
# active-workflow-context invariant (IS §5.1
# `procedural_tier_snapshot_ref` populated at every producer site) is honored via
# a caller-supplied injection param (defaulting `None`) on both helpers — the
# strategy (U-CP-86), which holds the `DriverContext` resolver the linear
# `_append_step_ledger_entry` reads, resolves + passes it, keeping these helpers
# pure (no `DriverContext` coupling) and the public API forward-complete.


def append_branch_step_ledger_entry(
    *,
    branch_writer: BufferingLedgerWriter,
    branch_context: StepExecutionContext,
    run_idempotency_key: str,
    local_step_index: int,
    timestamp: datetime,
    procedural_tier_snapshot_ref: Identifier | None = None,
) -> None:
    """Buffer a branch's per-step ledger entry carrying causality-only
    `branch_metadata` (`terminal_status=None`) — C-CP-25 §25.13 / runtime §2.2(c).

    Composes the branch-unique `action_id` (`compose_branch_step_action_id`) + the
    branch-scoped idempotency key (`compose_branch_path` → `_compute_step_idempotency_key`,
    U-CP-83) + the `branch_metadata` causality carrier (`compose_branch_metadata`,
    `terminal_status=None`) and buffers it through the branch's
    `BufferingLedgerWriter` (the write is deferred to the barrier drain; dispatch
    + telemetry already fired inline, so the pre-dispatch gate is never deferred,
    §25.15.2 obl. 2). `branch_context` must be a branch child context (the
    composers raise on a linear context). `timestamp` is a buffer-time
    placeholder the barrier drain overrides (`drain_branch_buffers` re-stamps to
    the append moment); see the module-level timestamp discipline.

    `procedural_tier_snapshot_ref` is the **caller-supplied** R-003 sidecar (IS
    spec v1.3 §5.1): a branch step entry is written inside an active-workflow
    context, so the strategy (U-CP-86) — which holds the `DriverContext` resolver
    the linear `_append_step_ledger_entry` reads — resolves and passes it here to
    honor the active-workflow-context population invariant. Defaulting `None` keeps
    this helper pure (no `DriverContext` coupling) and matches the §5.1
    omit-when-`None` canonicalization for the resolver-less paths (tests, an
    operator with no resolver bound).
    """
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_is.state_ledger_write import EntryPayload, WriteKey

    branch_metadata = compose_branch_metadata(branch_context, terminal_status=None)
    action_id = compose_branch_step_action_id(branch_context, local_step_index)
    idempotency_key = _compute_step_idempotency_key(
        run_idempotency_key,
        local_step_index,
        compose_branch_path(branch_context),
    )
    payload = EntryPayload(
        action_id=Identifier(action_id),
        idempotency_key=Identifier(idempotency_key),
        actor=branch_writer.actor,
        timestamp=timestamp,
        procedural_tier_snapshot_ref=procedural_tier_snapshot_ref,
        branch_metadata=branch_metadata,
    )
    write_key = WriteKey(
        thread_id=Identifier(branch_context.workflow_id),
        step_id=Identifier(f"{branch_metadata.branch_index}:{local_step_index}"),
        idempotency_key=Identifier(idempotency_key),
    )
    branch_writer.append(payload, write_key)


def append_branch_terminal_ledger_entry(
    *,
    branch_writer: BufferingLedgerWriter,
    branch_context: StepExecutionContext,
    run_idempotency_key: str,
    terminal_status: Literal["cancelled", "completed", "timed_out"],
    timestamp: datetime,
    procedural_tier_snapshot_ref: Identifier | None = None,
) -> None:
    """Buffer a branch's **fresh terminal entry** carrying the dispatch-boundary
    disposition — C-CP-25 §25.13 / IS §5.4 append-only invariant / runtime §2.2(c).

    A branch's terminal disposition is recorded at a fresh terminal entry (its own
    `compose_branch_terminal_action_id` marker + the distinct
    `compose_branch_terminal_path` idempotency key, so the IS dedup never drops it)
    — **never** by mutating an already-buffered step entry. Buffered as the
    branch's last entry, so the existing `drain_branch_buffers` appends it after
    the branch's step entries in branch-index order; the §6.3 chain re-verifies
    because every entry (including this one) is a fresh append.

    `terminal_status` is the caller-decided disposition (U-CP-85's cascade logic);
    U-CP-84 persists the value it is handed. The carrier's closed set forecloses
    `failed` — a ran-and-errored branch is `completed` (dispatch-boundary, not
    step-outcome). `procedural_tier_snapshot_ref` is the caller-supplied R-003
    sidecar — see `append_branch_step_ledger_entry` (the terminal entry is written
    at the barrier drain, still inside the active-workflow context). `branch_context`
    must be a branch child context.
    """
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_is.state_ledger_write import EntryPayload, WriteKey

    branch_metadata = compose_branch_metadata(branch_context, terminal_status=terminal_status)
    action_id = compose_branch_terminal_action_id(branch_context)
    idempotency_key = _compute_step_idempotency_key(
        run_idempotency_key,
        branch_context.step_index,
        compose_branch_terminal_path(branch_context),
    )
    payload = EntryPayload(
        action_id=Identifier(action_id),
        idempotency_key=Identifier(idempotency_key),
        actor=branch_writer.actor,
        timestamp=timestamp,
        procedural_tier_snapshot_ref=procedural_tier_snapshot_ref,
        branch_metadata=branch_metadata,
    )
    write_key = WriteKey(
        thread_id=Identifier(branch_context.workflow_id),
        step_id=Identifier(f"{branch_metadata.branch_index}:terminal"),
        idempotency_key=Identifier(idempotency_key),
    )
    branch_writer.append(payload, write_key)


# ---------------------------------------------------------------------------
# U-CP-86 — PARALLELIZATION driver strategy (C-CP-25 §25.11)
# ---------------------------------------------------------------------------
#
# The FIRST non-linear topology strategy — fan-out-barrier-aggregate. Per
# §25.11 "strategies differ only in *control flow over steps*", the SAME
# `steps` sequence the `SINGLE_THREADED_LINEAR` loop runs sequentially is here
# run CONCURRENTLY: each declared `WorkflowStep` is one branch (branch_index =
# its ordinal) over its varied `step_payload` (§25.11 PARALLELIZATION row + the
# B1 design "variation is in *inputs*, not agent specialization"). This reuses
# the existing `execute_workflow(manifest, steps, ...)` input with ZERO schema
# extension (a branch-spec payload schema would be an X-AL-3 spec extension).
#
# Composes the U-CP-80..84 substrate:
#   - branch child contexts            (compose_branch_child_context, U-CP-81)
#   - the buffered/deferred-append path (BufferingLedgerWriter + the
#     branch-index-ordered drain, U-CP-82) — NEVER the linear inline append
#   - branch_metadata causality + a `completed` terminal entry per branch
#     (append_branch_step/terminal_ledger_entry, U-CP-84)
#   - the policy-NEUTRAL bounded barrier (bounded_barrier, U-CP-82).
#
# U-CP-86 does NOT depend on U-CP-85 (cascade), so it uses NO cascade-cancel:
# the barrier is `bounded_barrier` (policy-neutral, leak-free); a branch failure
# maps to `RunStatus.FAILED`. The richer `cascade_policy` proceed/pause/
# cascade-cancel differentiation (→ PARTIAL/PAUSED/FAILED) is U-CP-85's machinery,
# first consumed by U-CP-88 (ORCHESTRATOR_WORKERS).
#
# Determinism (§25.12): both the persisted append order AND the aggregate are
# pure functions of the ORDERED (branch-index) result set — never completion
# order. `drain_branch_buffers` sorts by branch_index; `_aggregate_parallelization`
# votes with a lowest-branch-index tiebreak.

_DEFAULT_PARALLELIZATION_AGENT_ROLE = AgentRole("parallelization-worker")
"""The single per-worker role for PARALLELIZATION branches (C-CP-25 §25.11).

PARALLELIZATION varies *inputs*, NOT agent specialization — one role for all
branches (the B1 design "non-degenerate with one role"). The runtime role-read
(U-RT-114) therefore routes every branch to the same model. Per-role worker
specialization is the ORCHESTRATOR_WORKERS family (U-CP-88+)."""

_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS = 300.0
"""Wall-clock deadline on the fan-out barrier (C-CP-25 §25.11 bounded barriers;
O-CP-1(c) impl-discretion). Bounds the PARENT's return: a branch stuck past this
cap does not strand the workflow — the barrier raises and the run returns
`RunStatus.FAILED` (the fan-out is driven so a wedged SYNC branch thread cannot
re-defeat the cap at executor shutdown; see `_run_fanout_to_completion`). The
HARD in-flight EFFECT cut-off (cancelling a running dispatch) is §25.15 cascade
scope (U-CP-85), deliberately excluded from U-CP-86 per its dependency set.
Generous default sized for INFERENCE_STEP branches; a manifest-surfaced
per-workflow deadline is a forward field (not surfaced at v1.32)."""

_HIERARCHICAL_DELEGATION_FANOUT_CAP = 3
"""Fan-out cap per parent for `HIERARCHICAL_DELEGATION` (C-CP-25 §25.11 row —
"recursive bounded-fan-out … fan-out cap 3 per parent (C-CP-10 §10.3)";
`topology_pattern.py:76` "scope-bounded recursion; fan-out cap 3 per parent").

Spec-PINNED at 3 for HIERARCHICAL_DELEGATION (distinct from the §25.18
impl-discretion that governs OTHER patterns' per-cell caps). Counts a level's
DIRECT children = the worker steps `steps[1:]` under the level's orchestrator
(`steps[0]`). A level whose worker count exceeds the cap is rejected
`detect-then-refuse` (`RunStatus.FAILED`), NEVER silently truncated. The cap
auto-applies at EVERY recursion level whose child manifest declares
`HIERARCHICAL_DELEGATION` (a child declaring `ORCHESTRATOR_WORKERS` re-enters
the uncapped strategy — by design: the cap is a property of this topology)."""


def _parallelization_fanout_action_id(workflow_id: str) -> str:
    """The shared fan-out parent `action_id` every branch descends from.

    All PARALLELIZATION branches fan out from the workflow root, so they share
    one fan-out point. `(parent_action_id, branch_index)` is the branch
    causality key (IS spec v1.8 §5.4); a single fan-out `action_id` + the
    per-branch index yields a globally-unique key per branch (no `branch_path`
    at the causality key — Route Y).
    """
    return f"workflow:{workflow_id}:fanout"


def _aggregate_parallelization(
    branch_outputs: list[tuple[int, str, Mapping[str, Any]]],
) -> dict[str, Any]:
    """Fold the branch outputs into one result — voting, deterministic tiebreak
    = lowest branch-index (C-CP-25 §25.11 aggregator + §25.12 determinism).

    `branch_outputs` is `[(branch_index, step_id, output), ...]`. The fold is a
    PURE function of the ORDERED (branch-index) set — never completion order
    (the §25.12 determinism boundary; "first to finish wins" is forbidden):

    - **`branch_outputs`** (all preserved, no discard): every branch's output
      keyed by its `step_id` — parity with the linear path, which keys every
      step output by `step_id` (a single-winner fold that *dropped* the other
      N-1 branch results would silently lose them).
    - **`aggregate`** (the single synthesized result): a voting fold — branches
      "vote" with their canonical-JSON-serialized output; the winner is the
      most-voted output; ties break to the LOWEST branch-index. With
      all-distinct outputs every vote is 1 → tie → branch 0 wins (the
      deterministic floor; pinned by an explicit all-distinct test as
      *intended*, not accidental).
    """
    sorted_outputs = sorted(branch_outputs, key=lambda t: t[0])
    # Tally votes by canonical-JSON of each output, inserting in branch-index
    # order so a count tie resolves to the FIRST-inserted (lowest branch-index)
    # key — `max` is stable on first-seen among equal keys, and dicts preserve
    # insertion order.
    vote_counts: dict[str, int] = {}
    representative: dict[str, Mapping[str, Any]] = {}
    for _branch_index, _step_id, output in sorted_outputs:
        canon = json.dumps(output, sort_keys=True, default=str)
        if canon not in vote_counts:
            vote_counts[canon] = 0
            representative[canon] = output
        vote_counts[canon] += 1
    winning_canon = max(vote_counts, key=lambda k: vote_counts[k])
    return {
        "branch_outputs": {step_id: dict(output) for _bi, step_id, output in sorted_outputs},
        "aggregate": dict(representative[winning_canon]),
    }


def _writer_ran_a_step(writer: BufferingLedgerWriter) -> bool:
    """True iff the branch buffered ≥1 **STEP** entry (an `EntryPayload` whose
    `branch_metadata.terminal_status is None`) — i.e. its dispatch actually ran.

    A branch with ONLY a terminal entry (e.g. a CASCADE_CANCEL `cancelled`
    disposition written by the post-barrier empty-buffer scan for a
    not-yet-dispatched worker) did NOT run a step; counting it as a ran-step
    would inflate `workflow.step_count` + emit a spurious `STEP_BOUNDARY`
    ([P2-b]). The step/terminal discriminator is the same
    `branch_metadata.terminal_status` `resume_should_redispatch` reads (§25.15.2
    obl. 7). Defensive `getattr` for any future non-branch payload (none today —
    both branch append helpers set `branch_metadata`)."""
    return any(
        getattr(getattr(payload, "branch_metadata", None), "terminal_status", None) is None
        for payload, _write_key in writer.buffered_entries
    )


def _drain_and_emit_step_boundaries(
    ctx: DriverContext,
    branch_writers: Sequence[BufferingLedgerWriter],
) -> int:
    """Drain all branch buffers (branch-index order) through the single real
    writer, then emit one `STEP_BOUNDARY` per branch that ran a step.

    Single-threaded at the drain BY CONSTRUCTION: all emitter access (this
    drain + the one `WORKFLOW_START`) runs on the driver thread, after the
    barrier (`asyncio.run` over the fan-out has returned) — never concurrently.
    `STEP_BOUNDARY` is therefore NEVER emitted from the `to_thread` branch
    workers (which would also race the non-thread-safe emitter). The per-step
    boundary→append ordering of the linear path
    (§25.3.3.5 then §25.3.3.7) does not apply to a fan-out — the barrier-drain
    is one persist event; emitting the boundaries after the drain is the
    single-threaded analogue (impl-discretion, §25.18).

    Returns the count of branches that ran a step (the `workflow.step_count`
    carrier, C-OD-25) — counted by branches that buffered ≥1 **STEP** entry
    (`branch_metadata.terminal_status is None`), NOT by `entry_count > 0`. A
    fully-run branch buffered a step entry + a terminal entry (so its
    `entry_count` is 2; counted once); a branch whose dispatch raised before
    buffering contributed nothing (`entry_count` 0; not counted). The
    [P2-a/P2-b] distinction: a CASCADE_CANCEL worker cancelled BEFORE dispatch
    buffers ONLY a terminal `cancelled` entry (`entry_count` 1, NO step entry) —
    it did NOT run a step, so it must NOT inflate `workflow.step_count` or emit a
    `STEP_BOUNDARY`. (`entry_count > 0` would mis-count it; the non-cascade
    strategies — PARALLELIZATION / EVALUATOR_OPTIMIZER — never buffer a
    terminal-only branch, so the predicate is a no-op for them.)
    """
    ran = sum(1 for writer in branch_writers if _writer_ran_a_step(writer))
    drain_branch_buffers(ctx.ledger_writer, branch_writers)
    for _ in range(ran):
        ctx.lifecycle_emitter.emit(WorkflowEventClass.STEP_BOUNDARY)
    return ran


def _run_fanout_to_completion[T](fanout: Coroutine[Any, Any, T], *, max_workers: int) -> T:
    """Drive the async fan-out from the sync driver thread — WITHOUT `asyncio.run`.

    `asyncio.run` JOINS its default `ThreadPoolExecutor` at shutdown
    (`loop.shutdown_default_executor()` waits for every worker). A branch's SYNC
    dispatch runs off-loop via `asyncio.to_thread`, and CPython cannot kill a
    running thread — so a genuinely-wedged branch would block the parent's return
    at executor shutdown EVEN AFTER `bounded_barrier` raised the §25.11 wall-clock
    deadline, re-defeating the cap (the parent hangs instead of returning
    `parallelization-barrier-deadline-exceeded`).

    This drives the fan-out on a dedicated loop + a dedicated executor (sized to
    the fan-out so all branches run concurrently). On a CLEAN return every branch
    thread is idle/done → `shutdown(wait=True)` reclaims them (no thread leak). On
    ANY exception — the barrier deadline OR a branch failure — the executor is
    abandoned (`shutdown(wait=False)`) so a wedged branch thread NEVER blocks the
    parent's return; the orphaned thread runs to completion in the background.

    Honest residual (a CPython limit the spec routes to §25.15, NOT a U-CP-86
    defect): the orphaned thread is unkillable, so the HARD in-flight EFFECT
    cut-off (cancelling a running dispatch, classifying it `timed_out`) is §25.15
    cascade scope — U-CP-85's `cascade_cancel_barrier` `_deadline_cutoff`
    watchdog — deliberately excluded from U-CP-86 per its dependency set. In
    practice provider SDK per-call timeouts bound a real dispatch well under the
    fan-out backstop.
    """
    loop = asyncio.new_event_loop()
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="cp-fanout")
    loop.set_default_executor(executor)
    try:
        result = loop.run_until_complete(fanout)
    except BaseException:
        # Abandon (never join) on BOTH exit reasons — the barrier deadline AND an
        # ordinary branch failure — because either can leave a wedged sibling
        # thread, and joining one would re-defeat U-CP-86's OWN §25.11 obligation
        # ("a stuck branch cannot strand its parent indefinitely"): a branch that
        # fails fast (e.g. t=1s) has already exited `bounded_barrier`'s
        # `asyncio.timeout` window, so a `wait=True` join of a wedged sibling
        # would block PAST the deadline, forever. Parent-bounding is the
        # obligation U-CP-86 owns — honored by always returning. The orphaned
        # sibling's effect DISPOSITION (cancel / record / discriminate
        # terminal_status) is the §25.15.1 cascade_policy semantic — U-CP-85's
        # `cascade_cancel_barrier` + the proceed/pause/cascade-cancel table —
        # deliberately EXCLUDED from U-CP-86 by its dependency set. No
        # silent-uncompensated-effect results: PARALLELIZATION is §10.3-admissible
        # only for RESEARCH / CONTENT_CREATION (non-effectful breadth-search / A-B
        # cells; `topology_pattern.py:73-86`, and not a §11.1 primary), and an
        # effectful step gates BEFORE dispatch inside the dispatcher
        # (C-AS-02 → C-CP-19 → C-CP-16; only the ledger WRITE is buffered, never
        # the gate), so an orphaned sibling either never dispatched (no effect) or
        # already passed its operator gate.
        executor.shutdown(wait=False)
        raise
    else:
        # Clean fan-out: every branch thread is idle/done → reclaim them.
        executor.shutdown(wait=True)
        return result
    finally:
        loop.close()


def _execute_parallelization(
    *,
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    run_idempotency_key: str,
) -> tuple[RunResult, int]:
    """Execute the `PARALLELIZATION` fan-out-barrier-aggregate strategy (U-CP-86).

    Each declared `WorkflowStep` is fanned out as one branch (branch_index = its
    ordinal); all branches run concurrently; the barrier holds until every
    branch finishes; the structured outputs fold into one deterministic result.
    Returns `(RunResult, steps_executed)` for the `_execute_workflow_body`
    caller (matching the linear path's tuple).

    Bypassed linear-only paths (documented scoped-not-forgotten): prefix-replay
    / explicit-pause resume detection, mid-loop drain checks, per-step
    pause-trigger detection, and the per-step validator hook are NOT composed
    here — they compose at later strategy units (U-CP-85 cascade_policy /
    U-CP-88 ORCHESTRATOR_WORKERS). U-CP-86 is the happy-path fan-out + the
    deterministic aggregation.
    """
    workflow_id = manifest_entry.workflow_id

    # Empty step sequence → trivially SUCCESS with an empty aggregate (no
    # fan-out; mirrors the linear path's empty-loop SUCCESS).
    if not steps:
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.SUCCESS,
            terminal_step_index=None,
            partial_state=None,
            final_state={"branch_outputs": {}, "aggregate": {}},
            fail_class=None,
        ), 0

    # One fan-out parent context (the fan-out point); each branch descends a
    # child via compose_branch_child_context (U-CP-81). The MVP-default seed
    # fields mirror the linear per-step composition site.
    fanout_parent = StepExecutionContext(
        workflow_id=workflow_id,
        parent_action_id=_parallelization_fanout_action_id(workflow_id),
        parent_gate_level=resolve_parent_gate_level(manifest_entry),
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=ctx.ledger_writer.actor,
        parent_entry_hash="",
        parent_idempotency_key=_compute_step_idempotency_key(run_idempotency_key, 0),
        tenant_id=ctx.tenant_id,
        step_index=0,
    )

    # R-003 active-workflow-context sidecar (resolved once per fan-out; the same
    # resolver the linear `_append_step_ledger_entry` reads). None when no
    # resolver is bound (operator opt-out / test ctx).
    _resolver = getattr(ctx, "procedural_tier_snapshot_resolver", None)
    snapshot_ref = _resolver() if _resolver is not None else None

    # Buffer-time placeholder timestamp for every branch entry; the authoritative
    # append timestamp is assigned at the drain (`drain_branch_buffers` re-stamps
    # to one drain-moment value — the IS-monotonicity realization, see the module
    # timestamp-discipline note above `append_branch_step_ledger_entry`).
    fanout_timestamp = datetime.now(UTC)

    # Per-branch plan: (branch_index, step, child context, buffering writer,
    # resolved binding). The fan-out cardinality cap (C-CP-10 §10.3 cells) is an
    # ADMISSIBILITY property rejected at workflow-binding (§25.10 Invariant 2) —
    # NOT re-truncated here (silently dropping declared steps beyond a cap would
    # be silent branch loss); the strategy fans out every declared branch.
    branch_plan: list[
        tuple[int, WorkflowStep, StepExecutionContext, BufferingLedgerWriter, StepEffectiveBinding]
    ] = []
    for branch_index, step in enumerate(steps):
        child = compose_branch_child_context(
            fanout_parent,
            branch_index=branch_index,
            agent_role=_DEFAULT_PARALLELIZATION_AGENT_ROLE,
        )
        writer = BufferingLedgerWriter(actor=ctx.ledger_writer.actor, branch_index=branch_index)
        binding = resolve_step_binding(
            manifest_entry,
            str(step.step_id),
            default_model_binding=default_model_binding,
            persona_tier=manifest_entry.persona_tier,
        )
        branch_plan.append((branch_index, step, child, writer, binding))
    branch_writers = [plan[3] for plan in branch_plan]

    # § 25.3.2 — Emit workflow.start (the fan-out begins). Single-threaded on the
    # driver thread, BEFORE the concurrent branches spawn.
    ctx.lifecycle_emitter.emit(WorkflowEventClass.WORKFLOW_START)

    async def _run_branch(
        branch_index: int,
        step: WorkflowStep,
        child: StepExecutionContext,
        writer: BufferingLedgerWriter,
        binding: StepEffectiveBinding,
    ) -> tuple[int, str, Mapping[str, Any]]:
        # Concurrency: the existing SYNC dispatcher is run off-loop in a thread
        # so N branches genuinely run concurrently (the dispatch IS the blocking
        # model/tool call). The pre-dispatch gate is NOT deferred — dispatch
        # fires inline in the branch; only the ledger WRITE is buffered
        # (§25.15.2 obl. 2). No `asyncio.shield` here: U-CP-86 has no
        # cascade-cancel (U-CP-85 non-dep), so an in-flight effect never needs
        # the shield-and-drive of `dispatch_branch_step_shielded` (U-CP-88).
        dispatcher = step_dispatchers.lookup(step.step_kind)
        step_output: Mapping[str, Any] = await asyncio.to_thread(
            dispatcher.dispatch, binding, step, step_context=child
        )
        # Buffer the branch's per-step entry (causality-only branch_metadata) +
        # a fresh `completed` terminal entry (dispatch-boundary disposition — a
        # ran branch is `completed`). Both buffer through the branch's OWN
        # writer on the loop thread (after the awaited dispatch returns); the
        # single barrier drain serializes them in branch-index order (U-CP-82/84).
        append_branch_step_ledger_entry(
            branch_writer=writer,
            branch_context=child,
            run_idempotency_key=run_idempotency_key,
            local_step_index=0,
            timestamp=fanout_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        append_branch_terminal_ledger_entry(
            branch_writer=writer,
            branch_context=child,
            run_idempotency_key=run_idempotency_key,
            terminal_status="completed",
            timestamp=fanout_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        return (branch_index, str(step.step_id), step_output)

    async def _fanout() -> list[tuple[int, str, Mapping[str, Any]]]:
        return await bounded_barrier(
            [_run_branch(*plan) for plan in branch_plan],
            deadline_seconds=_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS,
        )

    # Sync bridge — drive the fan-out on a dedicated loop (NOT `asyncio.run`,
    # which would join the executor at shutdown and let a wedged SYNC branch
    # re-defeat the §25.11 deadline; see `_run_fanout_to_completion`). The
    # executor is sized to the fan-out so every branch runs concurrently.
    try:
        branch_results = _run_fanout_to_completion(_fanout(), max_workers=max(1, len(branch_plan)))
    except BranchBarrierDeadlineExceededError as exc:
        # A stuck branch hit the wall-clock deadline. Drain whatever the
        # completed branches buffered (no silent failure) then FAILED. The
        # bounded_barrier `finally` already cancelled + awaited pending tasks
        # (leak-free). The discriminating `timed_out` per-branch terminal_status
        # is U-CP-85's cascade machinery (non-dep) — at U-CP-86 a fan-out
        # deadline is a barrier-level FAILED.
        steps_executed = _drain_and_emit_step_boundaries(ctx, branch_writers)
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.FAILED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=f"parallelization-barrier-deadline-exceeded: {exc}",
        ), steps_executed
    except Exception as exc:
        # A branch raised. U-CP-86 has no cascade_policy differentiation
        # (U-CP-85 non-dep) → FAILED. Drain whatever each branch buffered so
        # the completed branches' entries persist (no silent failure — the
        # audit-honoring at U-CP-86's scope). The richer harvest-partial-results
        # `proceed`→PARTIAL flow + the discriminating cancelled/timed_out
        # terminal_status are U-CP-85.
        steps_executed = _drain_and_emit_step_boundaries(ctx, branch_writers)
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.FAILED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=f"parallelization-branch-failure: {type(exc).__name__}: {exc}",
        ), steps_executed

    # Clean barrier — drain (branch-index order) + emit STEP_BOUNDARYs, then
    # fold the structured outputs into one deterministic result.
    steps_executed = _drain_and_emit_step_boundaries(ctx, branch_writers)
    final_state = _aggregate_parallelization(branch_results)
    return RunResult(
        workflow_id=workflow_id,
        run_id=run_id,
        status=RunStatus.SUCCESS,
        terminal_step_index=None,
        partial_state=None,
        final_state=final_state,
        fail_class=None,
    ), steps_executed


# ---------------------------------------------------------------------------
# U-CP-87 — EVALUATOR_OPTIMIZER driver strategy (C-CP-25 §25.11)
# ---------------------------------------------------------------------------
#
# The SECOND non-linear topology strategy — a sequential generate→evaluate→
# (accept | regenerate) loop, bounded by a max-iteration cap (§25.11
# EVALUATOR_OPTIMIZER row: "Loop: generate-step → evaluate-step → (accept |
# regenerate-with-feedback), bounded by a max-iteration cap. Sequential;
# terminal on evaluator accept or cap.").
#
# Per the §25.11 common substrate, `steps` is the loop body: `steps[0]` is the
# GENERATE step (the optimizer) and `steps[1]` is the EVALUATE step (the
# evaluator); the two are distinguished by their per-step prompt (R-PM-1 §29,
# already landed) — non-hollow at B1 WITHOUT the B4 per-role binding catalog,
# because generate ≠ evaluate by `step_id` (and hence by selected prompt). The
# CP-unit proof is distinct-step dispatch (a different `step_id` resolves a
# different binding); live R-PM-1 §29 prompt selection is composed at runtime
# stage-0, not in the CP driver (presence-vs-correctness honesty).
#
# Deps are [U-CP-80 (dispatch), U-CP-82 (buffered-append substrate)] — NOT
# U-CP-81 (no branch child-contexts; sequential single-owner, NO fan-out) and
# NOT U-CP-85 (no cascade_policy). So:
#   - NO branch_metadata: entries carry the carrier default (`None`) — the AC's
#     "Sequential; no fan-out branch_metadata required". (Hence a dedicated
#     `_append_buffered_sequential_entry`, NOT the U-CP-84 branch helpers, which
#     always compose branch_metadata + require a branch child-context.)
#   - The buffered/deferred-append path (§25.11/§25.12) is STILL used (the
#     common-substrate mandate for all 5 non-linear strategies + the plan AC):
#     one `BufferingLedgerWriter`; the orchestrator drains it through the single
#     real writer at the end. Sequential execution is already naturally ordered,
#     so the drain is order-preserving by construction (the determinism subtlety
#     is the fan-out concern, not this one).
#
# Idempotency (the load-bearing decision). The loop re-dispatches the SAME two
# declared steps each iteration, so TWO distinct indices are kept apart:
#   - the MONOTONIC `entry_index` (0,1,2,3,… across the whole loop) scopes the
#     unique ledger action_id + idempotency key. Re-using the declared step
#     ordinal (0/1) as the ledger key would collide iteration-2's generate with
#     iteration-1's on the IS writer's `idempotency_key`-only dedup (C-IS-07
#     §7.5) → a silently-dropped entry. The monotonic key makes every dispatched
#     step persist a distinct entry (the live e2e asserts the full
#     `iterations × 2` persisted count + chain VALID).
#   - the DECLARED step ordinal (0=generate, 1=evaluate) is what
#     `StepExecutionContext.step_index` carries (Codex [P2]): downstream
#     dispatchers read that field for per-step policy / override selection +
#     audit context, so it MUST keep matching the declared step across iterations
#     rather than drifting to the ledger row number. The ledger `action_id`s
#     (incl. `parent_action_id`) keep the unique `entry_index`.
#
# Scope (scoped-not-forgotten): the linear-only prefix-replay / explicit-pause
# resume detection, mid-loop drain checks, per-step pause-trigger detection, and
# the per-step validator hook are NOT composed here (their units are not EO
# deps) — they compose at later strategy units. "regenerate-with-feedback": the
# loop re-dispatching the generate step IS the regenerate. Inter-step DATA flow
# (the generate draft → the evaluator's input; the evaluator's feedback → the
# next generate's input) is NOT threaded at the driver level — exactly as the
# `SINGLE_THREADED_LINEAR` path does not thread its `accumulated` step outputs
# into subsequent `dispatch(...)` calls (the dispatcher signature carries only
# `binding, step, step_context`, never prior outputs; the driver never
# introspects or mutates the frozen `step_payload`, §25.3.3.4). Inter-step data
# flow is therefore a runtime/dispatcher concern (a shared run context the
# dispatcher reads, or B4 per-step prompt composition), the SAME for every
# topology — not a B1 EO driver concern. EO at the driver level is the loop
# CONTROL FLOW (generate→evaluate→accept/regenerate, bounded cap, accept-signal
# read from the evaluator's structured output).

_EVALUATOR_OPTIMIZER_ACCEPT_KEY = "accepted"
"""The reserved key the EVALUATE step's output sets truthy to signal acceptance
(C-CP-25 §25.11 EVALUATOR_OPTIMIZER terminal-on-accept; §25.18 impl-discretion).

The evaluator/optimizer roles are distinguished by per-step prompt (R-PM-1 §29);
the accept SIGNAL the driver reads from the evaluator's structured output is this
boolean key. A missing/false key ⟹ regenerate (continue the loop). The signal
SHAPE is impl-discretion (§25.18 — the contract specifies observable behavior,
not the signal encoding); no other accept/terminal convention exists in step
outputs (grep-clean at authoring)."""

_DEFAULT_EVALUATOR_OPTIMIZER_MAX_ITERATIONS = 3
"""The max-iteration cap on the generate→evaluate loop (C-CP-25 §25.11 "bounded
by a max-iteration cap"; §25.18 impl-discretion). The loop terminates on the
first evaluator-accept OR when this many iterations have run without accept (a
best-effort SUCCESS, `accepted=False`; §25.17 lists no cap-failure mode — cap is
a normal bounded termination, NOT a failure). A manifest-surfaced per-workflow
cap is a forward field (not surfaced at v1.32)."""


def _evaluator_optimizer_accepted(evaluation: Mapping[str, Any]) -> bool:
    """`True` when the evaluator's output signals acceptance (terminal-on-accept).

    Reads the `_EVALUATOR_OPTIMIZER_ACCEPT_KEY` reserved key (truthy ⟹ accept;
    absent/false ⟹ regenerate). Pure; no side effects.
    """
    return bool(evaluation.get(_EVALUATOR_OPTIMIZER_ACCEPT_KEY, False))


def _append_buffered_sequential_entry(
    *,
    writer: BufferingLedgerWriter,
    workflow_id: str,
    entry_index: int,
    idempotency_key: str,
    timestamp: datetime,
    procedural_tier_snapshot_ref: Identifier | None = None,
) -> None:
    """Buffer a sequential strategy's per-step ledger entry — NO branch_metadata
    (C-CP-25 §25.11/§25.12 buffered path; the EVALUATOR_OPTIMIZER sequential
    analogue of the U-CP-84 branch helpers).

    Composes the flat `workflow:{wf}:step:{entry_index}` action_id (the
    caller-supplied `idempotency_key` is the matching
    `_compute_step_idempotency_key(run_idempotency_key, entry_index)` value,
    reused from the `StepExecutionContext` composition to avoid recomputing it)
    and buffers it through the strategy's single `BufferingLedgerWriter` (the
    write is deferred to the drain; dispatch + telemetry already fired inline, so
    the pre-dispatch gate is never deferred — §25.15.2 obl. 2). The
    `branch_metadata` carrier stays the default `None` — this strategy is
    sequential single-owner with NO fan-out causality (the AC's "no fan-out
    branch_metadata required"); it is therefore a dedicated helper, NOT the
    U-CP-84 branch-cadence helpers (which always compose branch_metadata).

    `entry_index` is MONOTONIC across the whole loop (NOT the declared step
    ordinal) so iteration-N's re-dispatch of the same declared step never collides
    with iteration-(N-1)'s on the IS writer's idempotency_key-only dedup (C-IS-07
    §7.5). The linear `_append_step_ledger_entry` is left byte-unchanged (§25.10
    Invariant 1).
    """
    from harness_is.state_ledger_entry_schema import Identifier as _Identifier
    from harness_is.state_ledger_write import EntryPayload, WriteKey

    action_id = ActionID(f"workflow:{workflow_id}:step:{entry_index}")
    payload = EntryPayload(
        action_id=_Identifier(str(action_id)),
        idempotency_key=_Identifier(idempotency_key),
        actor=writer.actor,
        timestamp=timestamp,
        procedural_tier_snapshot_ref=procedural_tier_snapshot_ref,
    )
    write_key = WriteKey(
        thread_id=_Identifier(workflow_id),
        step_id=_Identifier(str(entry_index)),
        idempotency_key=_Identifier(idempotency_key),
    )
    writer.append(payload, write_key)


def _execute_evaluator_optimizer(
    *,
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    run_idempotency_key: str,
) -> tuple[RunResult, int]:
    """Execute the `EVALUATOR_OPTIMIZER` generate→evaluate→regenerate loop (U-CP-87).

    `steps[0]` is the GENERATE step, `steps[1]` is the EVALUATE step. The loop
    dispatches generate then evaluate, terminating on the first evaluator-accept
    (`_evaluator_optimizer_accepted`) or when
    `_DEFAULT_EVALUATOR_OPTIMIZER_MAX_ITERATIONS` iterations have run. Each
    dispatched step buffers a plain (no-branch_metadata) ledger entry keyed by a
    MONOTONIC `entry_index`; the buffer drains through the single real writer at
    the end (§25.11/§25.12 buffered path). Returns `(RunResult, steps_executed)`
    for the `_execute_workflow_body` caller (matching the linear path's tuple).

    Terminal: evaluator-accept OR cap → SUCCESS (`final_state.accepted`
    discriminates accept-terminal from cap-terminal; §25.17 lists no cap-failure
    mode); a step dispatch raising → FAILED (the prior buffered entries STILL
    drain — no silent loss). Sequential single-owner; NO fan-out, NO
    cascade_policy (U-CP-85 non-dep), NO branch_metadata (AC).
    """
    workflow_id = manifest_entry.workflow_id

    # Empty step sequence → trivially SUCCESS (mirrors the linear empty-loop + the
    # PARALLELIZATION empty-steps SUCCESS).
    if not steps:
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.SUCCESS,
            terminal_step_index=None,
            partial_state=None,
            final_state={"accepted": False, "iterations": 0, "output": {}, "evaluation": {}},
            fail_class=None,
        ), 0

    # EVALUATOR_OPTIMIZER is exactly generate→evaluate (§25.11) — 2 declared
    # steps. A non-empty manifest declaring any other count is malformed for this
    # pattern (a multi-step generate phase would be a spec extension, not a driver
    # generalization — X-AL-3). FAILED with a clear fail_class (no silent reshape).
    if len(steps) != 2:
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.FAILED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=(
                "evaluator-optimizer-malformed: expected exactly 2 steps "
                f"(generate, evaluate); got {len(steps)}"
            ),
        ), 0

    generate_step, evaluate_step = steps[0], steps[1]

    # R-003 active-workflow-context sidecar (resolved once; the same resolver the
    # linear `_append_step_ledger_entry` reads). None when no resolver is bound.
    _resolver = getattr(ctx, "procedural_tier_snapshot_resolver", None)
    snapshot_ref = _resolver() if _resolver is not None else None

    # Buffer-time placeholder timestamp for every buffered entry; the
    # authoritative append timestamp is assigned at the drain
    # (`drain_branch_buffers` re-stamps to one drain-moment value — the
    # IS-monotonicity realization, see the module timestamp-discipline note).
    loop_timestamp = datetime.now(UTC)

    writer = BufferingLedgerWriter(actor=ctx.ledger_writer.actor, branch_index=0)

    # § 25.3.2 — Emit workflow.start (single-threaded on the driver thread).
    ctx.lifecycle_emitter.emit(WorkflowEventClass.WORKFLOW_START)

    def _dispatch_and_buffer(
        step: WorkflowStep, *, declared_step_index: int, entry_index: int
    ) -> Mapping[str, Any]:
        # Dispatch one declared step on the driver thread (sequential — no
        # to_thread / barrier), buffer its plain ledger entry under the monotonic
        # entry_index, and emit one STEP_BOUNDARY. The pre-dispatch gate fires
        # inline inside the dispatcher; only the ledger WRITE is buffered
        # (§25.15.2 obl. 2). A dispatch exception propagates to the caller's
        # FAILED handler (the entry is NOT buffered + no boundary emitted for the
        # failed step, so entry_index stays the completed-step count).
        #
        # TWO distinct indices (Codex [P2]). `declared_step_index` is the step's
        # DECLARED ordinal (0=generate, 1=evaluate) — it is what
        # `StepExecutionContext.step_index` carries, because downstream dispatchers
        # read that field for per-step policy / override selection + audit context
        # (it must keep matching the declared step across loop iterations, NOT
        # drift to the ledger row number). `entry_index` is the MONOTONIC ledger
        # row index (0,1,2,3,…) — it scopes the unique ledger action_id +
        # idempotency key so re-dispatching the same declared step across
        # iterations never collapses on the IS writer's idempotency_key-only dedup
        # (C-IS-07 §7.5). The two coincide only on iteration 0.
        binding = resolve_step_binding(
            manifest_entry,
            str(step.step_id),
            default_model_binding=default_model_binding,
            persona_tier=manifest_entry.persona_tier,
        )
        entry_idempotency_key = _compute_step_idempotency_key(run_idempotency_key, entry_index)
        step_context = StepExecutionContext(
            workflow_id=workflow_id,
            parent_action_id=f"workflow:{workflow_id}:step:{entry_index}",
            parent_gate_level=resolve_parent_gate_level(manifest_entry),
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=ctx.ledger_writer.actor,
            parent_entry_hash="",
            parent_idempotency_key=entry_idempotency_key,
            tenant_id=ctx.tenant_id,
            step_index=declared_step_index,
        )
        step_output = step_dispatchers.lookup(step.step_kind).dispatch(
            binding, step, step_context=step_context
        )
        _append_buffered_sequential_entry(
            writer=writer,
            workflow_id=workflow_id,
            entry_index=entry_index,
            idempotency_key=entry_idempotency_key,
            timestamp=loop_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        ctx.lifecycle_emitter.emit(WorkflowEventClass.STEP_BOUNDARY)
        return step_output

    entry_index = 0
    accepted = False
    iterations = 0
    last_generate_output: Mapping[str, Any] = {}
    last_evaluation: Mapping[str, Any] = {}
    try:
        for _iteration in range(_DEFAULT_EVALUATOR_OPTIMIZER_MAX_ITERATIONS):
            iterations += 1
            last_generate_output = _dispatch_and_buffer(
                generate_step, declared_step_index=0, entry_index=entry_index
            )
            entry_index += 1
            last_evaluation = _dispatch_and_buffer(
                evaluate_step, declared_step_index=1, entry_index=entry_index
            )
            entry_index += 1
            if _evaluator_optimizer_accepted(last_evaluation):
                accepted = True
                break
    except Exception as exc:
        # A generate/evaluate dispatch raised. EVALUATOR_OPTIMIZER has no
        # cascade_policy differentiation (U-CP-85 non-dep) → FAILED. Drain
        # whatever was buffered so the completed steps' entries persist (no
        # silent failure — audit-honoring at this scope).
        drain_branch_buffers(ctx.ledger_writer, [writer])
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.FAILED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=f"evaluator-optimizer-step-failure: {type(exc).__name__}: {exc}",
        ), entry_index

    # Clean termination (accept or cap) — drain the buffer through the single real
    # writer in execution order, then return SUCCESS. `accepted` discriminates
    # accept-terminal from cap-terminal (§25.17 lists no cap-failure mode).
    drain_branch_buffers(ctx.ledger_writer, [writer])
    return RunResult(
        workflow_id=workflow_id,
        run_id=run_id,
        status=RunStatus.SUCCESS,
        terminal_step_index=None,
        partial_state=None,
        final_state={
            "accepted": accepted,
            "iterations": iterations,
            "output": dict(last_generate_output),
            "evaluation": dict(last_evaluation),
        },
        fail_class=None,
    ), entry_index


# ---------------------------------------------------------------------------
# U-CP-88 — ORCHESTRATOR_WORKERS driver strategy (C-CP-25 §25.11/§25.14/§25.15)
# ---------------------------------------------------------------------------
#
# The THIRD non-linear topology strategy — orchestrator-dispatch-collect fan-out
# with per-role workers (§25.11 ORCHESTRATOR_WORKERS row: "An orchestrator step
# computes a dynamic worker set, dispatches workers concurrently (per-role
# specialization via §25.14), collects. Barrier at collection; orchestrator
# composes the final result."). It is the FIRST `cascade_policy` consumer (the
# U-CP-85 machinery) AND the FIRST role-seam consumer (the U-CP-81 `agent_role`
# field + the runtime read U-RT-114).
#
# Structure (the B1 design §6 reading — `.harness/r-fs-1-b1-topology-...md`):
#   - `steps[0]` is the ORCHESTRATOR step. It is dispatched FIRST, sequentially
#     on the driver thread; its `action_id` (`workflow:{wf}:step:0`) is the
#     fan-out parent every worker branch descends from ("worker steps serialize
#     under the orchestrator's parent_action_id" — design §6). At B1 the
#     orchestrator's OUTPUT does NOT drive worker selection — there is NO
#     inter-step DATA flow (B-INTERSTEP), exactly as the linear path /
#     EVALUATOR_OPTIMIZER never thread a step's output into the next step's
#     input. The "dynamic worker set" is the declared `steps[1:]` (structural,
#     not data-driven); richer orchestrator-output-driven worker spawning is the
#     same runtime/dispatcher concern deferred at B-INTERSTEP for every topology.
#   - `steps[1:]` are the WORKERS, fanned out CONCURRENTLY, each under a per-role
#     child `StepExecutionContext` (U-CP-81 `agent_role`). The role is derived
#     from the worker's `step_id` (`AgentRole(str(step.step_id))`) — distinct per
#     worker, so with a `RoutingManifest.per_role_bindings` catalog the runtime
#     read (U-RT-114) routes each worker to its role's model (non-hollow by
#     per-role model specialization). The per-role binding CATALOG + per-step
#     override surface remains R-FS-1 child-arc B4; B1 pins the seam MECHANISM.
#   - The barrier COLLECTS; the orchestrator "composes the final result" = a
#     deterministic fold over the orchestrator output + the branch-index-ordered
#     worker outputs (§25.12 determinism — a pure function of the ORDERED set,
#     never completion order). NO second "compose" dispatch (that would need the
#     deferred inter-step data).
#
# Composes the U-CP-80..85 substrate: the dispatch table (U-CP-80); branch child
# contexts (U-CP-81); the buffered/deferred-append path + branch-index drain
# (U-CP-82); the branch_metadata causality + fresh terminal entry (U-CP-84); and
# — the new consumer — the `cascade_policy` machinery (U-CP-85): the per-policy
# run-status mapping (`cascade_policy_run_status`), the cascade-cancel
# TaskGroup barrier (`cascade_cancel_barrier`), and the in-flight-effect shield
# (`dispatch_branch_step_shielded`).
#
# `cascade_policy` (resolved from the manifest's (workload_class, engine_class,
# persona_tier) via the §11.4 D4 multiplicative tunable — NOT a manifest field)
# governs the on-WORKER-FAILURE reaction at the barrier (§25.15.1):
#   - `proceed`        → siblings RUN TO COMPLETION; the aggregator sees a
#                        partial result set → `RunStatus.PARTIAL` (degraded). A
#                        `return_exceptions`-collecting barrier (NOT
#                        `bounded_barrier`, whose finally cancels pending
#                        siblings on a failure).
#   - `cascade-cancel` → `cascade_cancel_barrier` (TaskGroup structured
#                        cancellation) cancels not-yet-dispatched siblings;
#                        in-flight effects run to completion (shielded);
#                        → `RunStatus.FAILED`.
#   - `pause`          → resumable FAN-OUT pause is NOT YET MATERIALIZED at B1
#                        (see the pause branch below): a `RunStatus.PAUSED` would
#                        advertise a resumability the position-only C-CP-26
#                        `PauseSnapshot` + the resume-blind strategy cannot honor
#                        (§25.15.2 obl. 7 resume reconstructs N-branch state from
#                        the LEDGER, and completed-branch OUTPUTS are not persisted
#                        for the aggregate merge). A worker failure under `pause`
#                        therefore fails HONESTLY → `RunStatus.FAILED` +
#                        `not-yet-materialized` fail_class (no false-`PAUSED`); the
#                        resumable-fan-out-pause build is a focused follow-on arc.
#
# The eight §25.15.2 cascade-cancel obligations are discharged: (1) dispatch-
# boundary-bounded + (8) structured cancellation by `cascade_cancel_barrier`;
# (2) no-gate-bypass + (5) high-blast-radius pre-dispatch gating by the gate
# living INSIDE `dispatcher.dispatch` (the buffered path defers only the ledger
# WRITE, never the gate — the SAME committed C-AS-02→C-CP-19→C-CP-16 gate the
# linear path uses; cascade-cancel COMPOSES it, never re-invents — §25.15.2 obl.
# 5 + §25.18 (d) "no dry_run/preview primitive"); (3) audit-completeness — every
# dispatched (in-flight) worker records its OWN step ledger entry regardless of
# terminal disposition; (4) discriminating `terminal_status` — `cancelled` =
# not-yet-dispatched (empty buffer, no effect), `completed` = the in-flight step
# ran (ran-and-errored is still `completed` — dispatch-boundary, not step-
# outcome), `timed_out` = the barrier deadline cut an in-flight step; (6) the
# run-level status mapping (`cascade_policy_run_status`); (7) resume-idempotency-
# terminality via the branch-scoped idempotency keys (U-CP-83) + the persisted
# discriminating `terminal_status` (`resume_should_redispatch`).
#
# Scope (scoped-not-forgotten): the linear-only prefix-replay / explicit-pause
# resume detection, mid-loop drain checks, and the per-step validator hook are
# NOT composed here (their units are not U-CP-88 deps). HIERARCHICAL_DELEGATION
# (U-CP-89) reuses THIS strategy recursively; DECENTRALIZED_HANDOFF (U-CP-90) is
# the single-owner sequential sibling.


def _aggregate_orchestrator_workers(
    orchestrator_output: Mapping[str, Any],
    collected: Mapping[int, tuple[str, Mapping[str, Any]]],
) -> dict[str, Any]:
    """Compose the ORCHESTRATOR_WORKERS final result — the orchestrator output +
    the branch-index-ordered worker outputs (C-CP-25 §25.11 "orchestrator
    composes the final result" + §25.12 determinism).

    The fold is a PURE function of the ORDERED (branch-index) collected set —
    never completion order ("first to finish wins" is forbidden, §25.12). At B1
    there is NO second "compose" dispatch (that would need the deferred
    inter-step DATA flow, B-INTERSTEP); the orchestrator's composition is this
    deterministic fold:

    - **`orchestrator`** — the orchestrator step's output (the fan-out parent).
    - **`worker_outputs`** — every COMPLETED worker's output keyed by its
      `step_id`, in branch-index order (cancelled / timed-out / stuck workers
      contribute nothing — their disposition lives in the persisted ledger
      `terminal_status`, not the in-memory aggregate).
    """
    sorted_items = sorted(collected.items(), key=lambda kv: kv[0])
    return {
        "orchestrator": dict(orchestrator_output),
        "worker_outputs": {step_id: dict(output) for _bi, (step_id, output) in sorted_items},
    }


def _execute_orchestrator_workers(
    *,
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    run_idempotency_key: str,
) -> tuple[RunResult, int]:
    """Execute the `ORCHESTRATOR_WORKERS` orchestrator-dispatch-collect strategy (U-CP-88).

    `steps[0]` is the orchestrator (dispatched first, sequentially; its
    `action_id` parents the worker fan-out); `steps[1:]` are workers fanned out
    concurrently under per-role child contexts. The barrier collects per the
    resolved `cascade_policy` (proceed → PARTIAL / cascade-cancel → FAILED /
    pause → PAUSED on a worker failure; SUCCESS when every worker completes);
    the orchestrator composes a deterministic fold. Returns
    `(RunResult, steps_executed)` for the `_execute_workflow_body` caller
    (matching the linear path's tuple). See the module block above for the full
    §25.11/§25.14/§25.15 obligation discharge.
    """
    workflow_id = manifest_entry.workflow_id

    # Empty step sequence → trivially SUCCESS (mirrors the linear empty-loop +
    # the PARALLELIZATION / EVALUATOR_OPTIMIZER empty-steps SUCCESS).
    if not steps:
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.SUCCESS,
            terminal_step_index=None,
            partial_state=None,
            final_state={"orchestrator": {}, "worker_outputs": {}},
            fail_class=None,
        ), 0

    orchestrator_step = steps[0]
    worker_steps = list(steps[1:])

    # The on-worker-failure cascade reaction (§25.15.1) — resolved from the
    # manifest's (workload_class, engine_class, persona_tier) via the §11.4 D4
    # multiplicative tunable (`cascade_policy` is NOT a WorkflowManifestEntry
    # field; it is the D4-layer tunable default — SOLO→proceed / TEAM→pause /
    # MTC→cascade-cancel).
    cascade_policy = d4_tunable(
        lookup_cell(manifest_entry.workload_class, manifest_entry.engine_class),
        manifest_entry.persona_tier,
    ).cascade_policy

    # R-003 active-workflow-context sidecar (resolved once; the same resolver the
    # linear `_append_step_ledger_entry` reads). None when no resolver is bound.
    _resolver = getattr(ctx, "procedural_tier_snapshot_resolver", None)
    snapshot_ref = _resolver() if _resolver is not None else None

    # Buffer-time placeholder timestamp for every entry (orchestrator + workers);
    # the authoritative append timestamp is assigned at the drain
    # (`drain_branch_buffers` re-stamps to one drain-moment value — the
    # IS-monotonicity realization, see the module timestamp-discipline note above
    # `append_branch_step_ledger_entry`).
    fanout_timestamp = datetime.now(UTC)

    # § 25.3.2 — Emit workflow.start (single-threaded on the driver thread, BEFORE
    # any dispatch).
    ctx.lifecycle_emitter.emit(WorkflowEventClass.WORKFLOW_START)

    # --- 1) the orchestrator step (sequential; its action_id parents the fan-out) ---
    # `workflow:{wf}:step:0` is the orchestrator's action_id AND the fan-out
    # parent every worker descends from (compose_branch_child_context carries it
    # verbatim). A plain sequential entry (NO branch_metadata — the orchestrator
    # is the parent, not itself a branch).
    orchestrator_action_id = f"workflow:{workflow_id}:step:0"
    orchestrator_idempotency_key = _compute_step_idempotency_key(run_idempotency_key, 0)
    orchestrator_writer = BufferingLedgerWriter(actor=ctx.ledger_writer.actor, branch_index=0)
    orchestrator_context = StepExecutionContext(
        workflow_id=workflow_id,
        parent_action_id=orchestrator_action_id,
        parent_gate_level=resolve_parent_gate_level(manifest_entry),
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=ctx.ledger_writer.actor,
        parent_entry_hash="",
        parent_idempotency_key=orchestrator_idempotency_key,
        tenant_id=ctx.tenant_id,
        step_index=0,
    )
    try:
        orchestrator_binding = resolve_step_binding(
            manifest_entry,
            str(orchestrator_step.step_id),
            default_model_binding=default_model_binding,
            persona_tier=manifest_entry.persona_tier,
        )
        orchestrator_output: Mapping[str, Any] = step_dispatchers.lookup(
            orchestrator_step.step_kind
        ).dispatch(orchestrator_binding, orchestrator_step, step_context=orchestrator_context)
    except Exception as exc:
        # The orchestrator failed before any worker fan-out → FAILED (nothing
        # buffered yet; no silent loss). cascade_policy governs WORKER failure,
        # not the orchestrator's own dispatch.
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.FAILED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=f"orchestrator-workers-orchestrator-failure: {type(exc).__name__}: {exc}",
        ), 0
    _append_buffered_sequential_entry(
        writer=orchestrator_writer,
        workflow_id=workflow_id,
        entry_index=0,
        idempotency_key=orchestrator_idempotency_key,
        timestamp=fanout_timestamp,
        procedural_tier_snapshot_ref=snapshot_ref,
    )

    # --- 2) the worker fan-out plan (per-role child contexts under the orchestrator) ---
    fanout_parent = orchestrator_context.model_copy(
        update={"parent_idempotency_key": orchestrator_idempotency_key}
    )
    branch_plan: list[
        tuple[int, WorkflowStep, StepExecutionContext, BufferingLedgerWriter, StepEffectiveBinding]
    ] = []
    for branch_index, step in enumerate(worker_steps):
        # Per-worker role (B1: step_id-derived — distinct per worker, bindable via
        # RoutingManifest.per_role_bindings; the binding catalog is B4). The
        # derivation is the single shared B1↔B4 contract (B4 Slice 2) an operator
        # keys their catalog on — see `derive_agent_role` (per_role_catalog.py).
        role = derive_agent_role(step.step_id)
        # The worker's DECLARED step ordinal is its position in the original
        # `steps` (orchestrator=0, workers=1,2,…), i.e. `branch_index + 1`.
        # `compose_branch_child_context` inherits `step_index` from the fan-out
        # parent (the orchestrator, step 0), so set it to the declared ordinal
        # here — downstream consumers key per-step policy / audit / the runtime
        # skill-activation hook on `step_context.step_index`, so every worker must
        # carry its own ordinal (the declared-ordinal discipline U-CP-87 set), not
        # all report as step 0. (Branch identity stays `(parent_action_id,
        # branch_index)`; the ledger keys stay branch-scoped — this only fixes the
        # transient driver-side `step_index` the dispatcher reads.)
        child = compose_branch_child_context(
            fanout_parent, branch_index=branch_index, agent_role=role
        ).model_copy(update={"step_index": branch_index + 1})
        writer = BufferingLedgerWriter(actor=ctx.ledger_writer.actor, branch_index=branch_index)
        binding = resolve_step_binding(
            manifest_entry,
            str(step.step_id),
            default_model_binding=default_model_binding,
            persona_tier=manifest_entry.persona_tier,
        )
        branch_plan.append((branch_index, step, child, writer, binding))
    branch_writers = [plan[3] for plan in branch_plan]

    # Worker outputs collected as each branch CLEANLY completes (branch-index
    # keyed). Populated on the fan-out loop thread after the awaited dispatch
    # returns; read on the driver thread AFTER the barrier (single-threaded) for
    # the deterministic fold.
    collected: dict[int, tuple[str, Mapping[str, Any]]] = {}

    def _record_clean(
        branch_index: int,
        step: WorkflowStep,
        child: StepExecutionContext,
        writer: BufferingLedgerWriter,
        output: Mapping[str, Any],
    ) -> None:
        # A cleanly-completed worker: its per-step entry (causality-only
        # branch_metadata) + a fresh `completed` terminal entry (U-CP-84) +
        # collect the output for the aggregate.
        append_branch_step_ledger_entry(
            branch_writer=writer,
            branch_context=child,
            run_idempotency_key=run_idempotency_key,
            local_step_index=0,
            timestamp=fanout_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        append_branch_terminal_ledger_entry(
            branch_writer=writer,
            branch_context=child,
            run_idempotency_key=run_idempotency_key,
            terminal_status="completed",
            timestamp=fanout_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        collected[branch_index] = (str(step.step_id), output)

    # Orchestrator-only (no workers) → SUCCESS with an empty worker set.
    if not worker_steps:
        drain_branch_buffers(ctx.ledger_writer, [orchestrator_writer])
        ctx.lifecycle_emitter.emit(WorkflowEventClass.STEP_BOUNDARY)
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.SUCCESS,
            terminal_step_index=None,
            partial_state=None,
            final_state=_aggregate_orchestrator_workers(orchestrator_output, {}),
            fail_class=None,
        ), 1

    def _finish(
        status: RunStatus, *, fail_class: str | None, salvage: bool
    ) -> tuple[RunResult, int]:
        # Drain the orchestrator entry FIRST (the fan-out parent persists before
        # its workers), then the worker buffers (branch-index order), emitting one
        # STEP_BOUNDARY per persisted-step writer. steps_executed = orchestrator +
        # workers that ran a step.
        drain_branch_buffers(ctx.ledger_writer, [orchestrator_writer])
        ctx.lifecycle_emitter.emit(WorkflowEventClass.STEP_BOUNDARY)
        steps_executed = 1 + _drain_and_emit_step_boundaries(ctx, branch_writers)
        aggregate = _aggregate_orchestrator_workers(orchestrator_output, collected)
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=status,
            terminal_step_index=None,
            partial_state=aggregate if salvage else None,
            final_state=aggregate if status is RunStatus.SUCCESS else None,
            fail_class=fail_class,
        ), steps_executed

    deadline = _DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS

    # === proceed: siblings run to completion → SUCCESS | PARTIAL (degraded) ===
    if cascade_policy is CascadePolicy.PROCEED:

        async def _proceed_worker(
            branch_index: int,
            step: WorkflowStep,
            child: StepExecutionContext,
            writer: BufferingLedgerWriter,
            binding: StepEffectiveBinding,
        ) -> None:
            dispatcher = step_dispatchers.lookup(step.step_kind)
            try:
                output = await asyncio.to_thread(
                    dispatcher.dispatch, binding, step, step_context=child
                )
            except asyncio.CancelledError:
                # The §25.11 wall-clock deadline (`_proceed_fanout`'s
                # `asyncio.timeout`) cancelled this in-flight worker. Its dispatch
                # was scheduled (the effect may have landed on the abandoned
                # thread) → record the step entry (obl. 3 — no silent obl-3 gap) +
                # a `timed_out` terminal, then re-raise to honor the cancellation.
                # WITHOUT this branch a deadline-cancelled worker would buffer
                # nothing and its dispatched effect would be an unrecorded silent
                # gap (decorrelated-review [P2]).
                append_branch_step_ledger_entry(
                    branch_writer=writer,
                    branch_context=child,
                    run_idempotency_key=run_idempotency_key,
                    local_step_index=0,
                    timestamp=fanout_timestamp,
                    procedural_tier_snapshot_ref=snapshot_ref,
                )
                append_branch_terminal_ledger_entry(
                    branch_writer=writer,
                    branch_context=child,
                    run_idempotency_key=run_idempotency_key,
                    terminal_status="timed_out",
                    timestamp=fanout_timestamp,
                    procedural_tier_snapshot_ref=snapshot_ref,
                )
                raise
            except Exception:
                # Ran-and-errored → record the step entry (obl. 3) + a `completed`
                # terminal (dispatch-boundary, not step-outcome; the failure lives
                # at the step entry). Contributes nothing to the aggregate; re-raise
                # so the return_exceptions gather marks this branch failed (→ the
                # partial result set → PARTIAL). proceed does NOT cancel siblings.
                append_branch_step_ledger_entry(
                    branch_writer=writer,
                    branch_context=child,
                    run_idempotency_key=run_idempotency_key,
                    local_step_index=0,
                    timestamp=fanout_timestamp,
                    procedural_tier_snapshot_ref=snapshot_ref,
                )
                append_branch_terminal_ledger_entry(
                    branch_writer=writer,
                    branch_context=child,
                    run_idempotency_key=run_idempotency_key,
                    terminal_status="completed",
                    timestamp=fanout_timestamp,
                    procedural_tier_snapshot_ref=snapshot_ref,
                )
                raise
            _record_clean(branch_index, step, child, writer, output)

        async def _proceed_fanout() -> list[Any]:
            # `return_exceptions=True`: a failing worker does NOT cancel siblings
            # (the proceed semantic). Bounded by the §25.11 wall-clock deadline.
            async with asyncio.timeout(deadline):
                return await asyncio.gather(
                    *(_proceed_worker(*plan) for plan in branch_plan),
                    return_exceptions=True,
                )

        try:
            results = _run_fanout_to_completion(
                _proceed_fanout(), max_workers=max(1, len(branch_plan))
            )
        except BranchBarrierDeadlineExceededError:
            # A stuck worker hit the deadline; the completed workers buffered their
            # entries → PARTIAL (degraded). (proceed does not cancel; the stuck
            # worker is abandoned per `_run_fanout_to_completion`.)
            return _finish(RunStatus.PARTIAL, fail_class=None, salvage=True)
        except TimeoutError:
            return _finish(RunStatus.PARTIAL, fail_class=None, salvage=True)
        any_failed = any(isinstance(r, BaseException) for r in results)
        if any_failed:
            return _finish(RunStatus.PARTIAL, fail_class=None, salvage=True)
        return _finish(RunStatus.SUCCESS, fail_class=None, salvage=False)

    # === cascade-cancel | pause: cancel-on-failure (TaskGroup structured cancel) ===
    # Both halt the fan-out on the first worker failure with in-flight effects run
    # to completion (shielded). They differ only in the run-level outcome on a
    # worker failure: cascade-cancel → FAILED (+ the empty-buffer not-yet-dispatched
    # scan records `cancelled`); pause → FAILED + `not-yet-materialized` fail_class
    # (resumable fan-out pause is a follow-on arc; see the pause branch below — a
    # false-`PAUSED` is foreclosed). The CLEAN (no-failure) path is SUCCESS for both.
    async def _cancel_worker(
        branch_index: int,
        step: WorkflowStep,
        child: StepExecutionContext,
        writer: BufferingLedgerWriter,
        binding: StepEffectiveBinding,
    ) -> None:
        dispatcher = step_dispatchers.lookup(step.step_kind)
        # Schedule the (sync) dispatch off-loop; `dispatch_branch_step_shielded`
        # keeps it alive against THIS branch's cancellation so an in-flight effect
        # runs to its own completion (obl. 1), and registers it for the barrier's
        # deadline watchdog (the hard "...or barrier-deadline timeout" cut-off).
        inflight: asyncio.Future[Mapping[str, Any]] = asyncio.ensure_future(
            asyncio.to_thread(dispatcher.dispatch, binding, step, step_context=child)
        )
        try:
            output = await dispatch_branch_step_shielded(inflight)
        except asyncio.CancelledError:
            # In-flight at cancel-time: the effect ran (shielded to completion) or
            # the deadline cut it. Record the step entry (obl. 3) + the
            # discriminating terminal (obl. 4): `completed` = ran (ran-and-errored
            # is still completed — dispatch-boundary), `timed_out` = the deadline
            # cut the in-flight step. A not-yet-dispatched worker NEVER reaches here
            # (it has no inflight) — its `cancelled`/re-dispatchable disposition is
            # handled post-barrier by the empty-buffer scan.
            append_branch_step_ledger_entry(
                branch_writer=writer,
                branch_context=child,
                run_idempotency_key=run_idempotency_key,
                local_step_index=0,
                timestamp=fanout_timestamp,
                procedural_tier_snapshot_ref=snapshot_ref,
            )
            terminal: Literal["completed", "timed_out"] = (
                "timed_out" if (inflight.cancelled() or not inflight.done()) else "completed"
            )
            append_branch_terminal_ledger_entry(
                branch_writer=writer,
                branch_context=child,
                run_idempotency_key=run_idempotency_key,
                terminal_status=terminal,
                timestamp=fanout_timestamp,
                procedural_tier_snapshot_ref=snapshot_ref,
            )
            raise  # honor the cancellation (the barrier cancelled this branch)
        except Exception:
            # THIS worker's own dispatch ERRORED — the failure that triggers the
            # cascade. The effect ran-and-errored → record the step entry (obl. 3 —
            # every dispatched effectful step gets its own entry REGARDLESS of
            # disposition; the step failure lives at this entry) + a `completed`
            # terminal (dispatch-boundary, not step-outcome — the carrier forecloses
            # `failed`). Re-raise so the TaskGroup cascade-cancels the siblings.
            append_branch_step_ledger_entry(
                branch_writer=writer,
                branch_context=child,
                run_idempotency_key=run_idempotency_key,
                local_step_index=0,
                timestamp=fanout_timestamp,
                procedural_tier_snapshot_ref=snapshot_ref,
            )
            append_branch_terminal_ledger_entry(
                branch_writer=writer,
                branch_context=child,
                run_idempotency_key=run_idempotency_key,
                terminal_status="completed",
                timestamp=fanout_timestamp,
                procedural_tier_snapshot_ref=snapshot_ref,
            )
            raise
        _record_clean(branch_index, step, child, writer, output)

    async def _cancel_fanout() -> list[None]:
        return await cascade_cancel_barrier(
            (_cancel_worker(*plan) for plan in branch_plan), deadline_seconds=deadline
        )

    worker_failed = False
    deadline_struck = False
    try:
        _run_fanout_to_completion(_cancel_fanout(), max_workers=max(1, len(branch_plan)))
    except BranchBarrierDeadlineExceededError:
        # The wall-clock deadline fired with no worker raising (a stuck fan-out) —
        # the §25.11 hard cap. A bare strand is FAILED (parity with PARALLELIZATION);
        # the in-flight workers recorded `timed_out` in their except blocks.
        deadline_struck = True
    except BaseExceptionGroup:
        # A worker raised → the TaskGroup cancelled not-yet-finished siblings.
        # In-flight siblings ran to completion (shielded) + recorded their terminal;
        # the failing worker's exception group is consumed here (the durable record
        # is the drained ledger). cascade_policy maps the run-level status.
        worker_failed = True

    if cascade_policy is CascadePolicy.CASCADE_CANCEL:
        # obl. 4: a not-yet-dispatched worker (empty buffer — its task was cancelled
        # before scheduling its dispatch) records a `cancelled` terminal so
        # `resume_should_redispatch` is False (no double-dispatch on resume).
        for _bi, _step, child, writer, _binding in branch_plan:
            if writer.entry_count == 0:
                append_branch_terminal_ledger_entry(
                    branch_writer=writer,
                    branch_context=child,
                    run_idempotency_key=run_idempotency_key,
                    terminal_status="cancelled",
                    timestamp=fanout_timestamp,
                    procedural_tier_snapshot_ref=snapshot_ref,
                )
        if worker_failed or deadline_struck:
            return _finish(
                RunStatus.FAILED,
                fail_class="orchestrator-workers-cascade-cancel",
                salvage=False,
            )
        return _finish(RunStatus.SUCCESS, fail_class=None, salvage=False)

    # pause: resumable FAN-OUT pause is NOT YET MATERIALIZED at B1. Returning a
    # `RunStatus.PAUSED` here would advertise a resumability the harness cannot
    # honor: the linear pause path captures a position-only C-CP-26 `PauseSnapshot`
    # (single `step_index`) for `api.resume` (C-RT-30), but a fan-out's resume must
    # (per §25.15.2 obl. 7) reconstruct N-branch state from the LEDGER — skip each
    # branch whose persisted `terminal_status` is set, re-dispatch the rest — AND
    # recover the COMPLETED branches' OUTPUTS for the aggregate (which the ledger
    # entries do not carry). That resume-re-entry path (the strategy is
    # resume-blind by design — §25.3 prefix-replay is bypassed above) + the
    # completed-branch output persistence is a focused follow-on R-FS-1 arc, NOT a
    # silent defer. A false-`PAUSED` is the silent-degradation failure mode
    # (decorrelated-review [P1]/F1-01 — two reviewers converged). So a worker
    # failure under `pause` policy fails HONESTLY → `RunStatus.FAILED` with an
    # explicit `not-yet-materialized` fail_class; the completed/in-flight workers'
    # ledger entries + the salvaged partial result set STILL persist (no silent
    # loss). The CLEAN (no-failure) path is unaffected → SUCCESS.
    if deadline_struck:
        return _finish(
            RunStatus.FAILED, fail_class="orchestrator-workers-barrier-deadline", salvage=False
        )
    if worker_failed:
        return _finish(
            RunStatus.FAILED,
            fail_class="orchestrator-workers-pause-resume-not-yet-materialized",
            salvage=True,
        )
    return _finish(RunStatus.SUCCESS, fail_class=None, salvage=False)


def _execute_hierarchical_delegation(
    *,
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    run_idempotency_key: str,
) -> tuple[RunResult, int]:
    """Execute the `HIERARCHICAL_DELEGATION` recursive bounded-fan-out strategy (U-CP-89).

    HIERARCHICAL_DELEGATION is **recursive `ORCHESTRATOR_WORKERS` with depth**
    (C-CP-25 §25.11 row): at each level `steps[0]` is the orchestrator/parent and
    `steps[1:]` are its direct children (workers); a worker of kind
    `SUB_AGENT_DISPATCH` recurses — its dispatcher re-enters `execute_workflow`
    with the child's own manifest + step sequence (the existing C-RT-17 §14.7.4
    `ChildWorkflowRunner` seam), and when that child manifest declares
    `HIERARCHICAL_DELEGATION` the recursion re-enters HERE, so the cap-3 +
    gate-level descent + bottom-up barrier composition hold at EVERY level.

    This strategy adds exactly two things over `ORCHESTRATOR_WORKERS` (U-CP-88),
    which it **REUSES at each level (NOT a parallel re-implementation — the AC):**

    1. **Materialization** — a manifest may declare `HIERARCHICAL_DELEGATION`, so
       a recursive child re-enters this strategy (vs the uncapped
       `ORCHESTRATOR_WORKERS`).
    2. **The fan-out cap 3 per parent** (`_HIERARCHICAL_DELEGATION_FANOUT_CAP`;
       C-CP-10 §10.3 / §25.11 "recursive *bounded*-fan-out"): a level with more
       than 3 direct children is rejected `detect-then-refuse` (`RunStatus.FAILED`,
       no `workflow.start` emit / no ledger append — parity with the
       topology/engine-class entry gate), NEVER silently truncated.

    Everything else is the `ORCHESTRATOR_WORKERS` strategy verbatim: the
    orchestrator parents the fan-out (`steps[0].action_id`); workers fan out
    concurrently under per-role child contexts whose gate-level descends per
    C-CP-12 §12.2 (`compose_branch_child_context`, monotonic — equality default);
    each parent barriers on its children and composes the deterministic
    branch-index fold (bottom-up); `cascade_policy` governs the on-failure
    reaction (§25.15). The nested barrier deadline composes — `cascade_cancel_barrier`
    extends (not replaces) the `_BRANCH_INFLIGHT_DISPATCHES` chain, so an OUTER
    level's deadline stays a hard cap over an inner-level in-flight dispatch.
    Returns `(RunResult, steps_executed)` for the `_execute_workflow_body` caller.

    **Gate-level descent across the recursion boundary (honest scope).** The
    sub-agent gate-level descent (C-CP-12 §12.2) is COMPUTED + RECORDED at the
    `SUB_AGENT_DISPATCH` dispatch boundary (the runtime
    `RuntimeHandoffRegistry.dispatch` → `dispatch_sub_agent`), but the child's
    EXECUTED gate-level re-seeds from its own manifest — the harness-computed
    descent is recorded-not-applied at the child run (pre-existing v1.6 MVP
    child-context sharing, `child_workflow_runner.py` module docstring). Strict
    cross-level *executed* descent is a v1.7+/B4-adjacent arc
    (`.harness/class_3_hierarchical_delegation_descent_recorded_not_applied.md`);
    §12.2 itself is monotonic-≤ with equality as the valid default, so the
    within-level worker descent (`compose_branch_child_context`) + the recorded
    boundary descent satisfy the monotonic invariant.
    """
    workflow_id = manifest_entry.workflow_id

    # Fan-out cap 3 per parent (C-CP-10 §10.3 / §25.11 "recursive bounded-fan-out").
    # steps[0] = this level's orchestrator (parent); steps[1:] = its direct children.
    # detect-then-refuse: a level exceeding the cap FAILS loud with no side effects
    # (no workflow.start emit, no ledger append) — never a silent truncation. The cap
    # re-checks at every recursion level whose child manifest declares
    # HIERARCHICAL_DELEGATION (the recursion re-enters this function).
    worker_count = max(0, len(steps) - 1)
    if worker_count > _HIERARCHICAL_DELEGATION_FANOUT_CAP:
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.FAILED,
            terminal_step_index=None,
            partial_state=None,
            final_state=None,
            fail_class=(
                f"hierarchical-delegation-fanout-cap-exceeded: {worker_count} children "
                f"> cap {_HIERARCHICAL_DELEGATION_FANOUT_CAP} (C-CP-10 §10.3)"
            ),
        ), 0

    # Reuse ORCHESTRATOR_WORKERS at this level (U-CP-88; the AC: "reuses
    # ORCHESTRATOR_WORKERS at each level — NOT a parallel re-implementation").
    # Recursion-with-depth emerges through SUB_AGENT_DISPATCH workers re-entering
    # the driver per the child manifest's topology.
    return _execute_orchestrator_workers(
        manifest_entry=manifest_entry,
        steps=steps,
        run_id=run_id,
        ctx=ctx,
        default_model_binding=default_model_binding,
        step_dispatchers=step_dispatchers,
        run_idempotency_key=run_idempotency_key,
    )


def _compose_handoff_to_next(
    *,
    completed_action_id: str,
    completed_context: StepExecutionContext,
    next_step: WorkflowStep,
    next_role: AgentRole,
    actor_identity: ActorIdentity,
) -> HandoffContext:
    """Compose the C-CP-13 `HandoffContext` recording the ownership transfer from a
    just-completed stage to the next stage-expert (C-CP-25 §25.11 DECENTRALIZED_HANDOFF).

    A RECORD, not a dispatch (the next stage runs through the ordinary
    `StepDispatcher`, never `SUB_AGENT_DISPATCH`). The MVP composition mirrors the
    runtime `sub_agent_dispatch` precedent exactly: `audit_trail_link` /
    `state_summary.relevant_entries` anchor the handing-off stage's ledger entry
    (`entry_hash` = the stage context's `parent_entry_hash` — `""` on the buffered
    path, the same value the existing composer passes); `summary_hash = sha256(b"")`
    (the v1.6 MVP default); the deliberation fields (`failed_attempts` /
    `alternatives_considered` / `retry_history` / `external_references`) are empty.
    `proposed_action` names the next stage-expert — `SUB_AGENT_DISPATCH` is the
    C-CP-17 §17.1 sub-agent-boundary placement a handoff *is* — and its payload
    carries only the next stage's *identity* (step_id + role): control-flow
    metadata, NOT the prior stage's output (the harness threads NO inter-step data
    for any topology, B-INTERSTEP)."""
    from harness_is.state_ledger_entry_schema import Identifier as _Identifier

    entry_ref = LedgerEntryRef(
        action_id=ActionID(completed_action_id),
        entry_hash=completed_context.parent_entry_hash,
        actor=actor_identity,
    )
    return HandoffContext(
        proposed_action=ProposedAction(
            action_kind=ActionKind.SUB_AGENT_DISPATCH,
            payload={"next_stage": str(next_step.step_id), "next_role": str(next_role)},
            brief=None,
        ),
        agent_confidence=None,
        failed_attempts=(),
        alternatives_considered=(),
        state_summary=StateSummary(
            relevant_entries=(entry_ref,),
            summary_text="",
            summary_hash=hashlib.sha256(b"").hexdigest(),
            idempotency_key=_Identifier(completed_context.parent_idempotency_key),
            external_references=(),
        ),
        audit_trail_link=entry_ref,
        retry_history=RetryHistory(attempts=(), retry_count=0),
    )


def _handoff_record(handoff: HandoffContext) -> dict[str, Any]:
    """Serialize a `HandoffContext` into the deterministic `final_state` surface —
    the observable ownership-transfer chain the AC asserts ("hands ownership
    stage-to-stage via HandoffContext")."""
    return {
        "from_action_id": str(handoff.audit_trail_link.action_id),
        "to_stage": handoff.proposed_action.payload["next_stage"],
        "to_role": handoff.proposed_action.payload["next_role"],
        "action_kind": handoff.proposed_action.action_kind.value,
    }


def _execute_decentralized_handoff(
    *,
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
    run_idempotency_key: str,
) -> tuple[RunResult, int]:
    """Execute the `DECENTRALIZED_HANDOFF` single-owner sequential handoff strategy (U-CP-90).

    Each declared step is a stage-expert that OWNS the workflow in turn, then hands
    ownership to the next via a `HandoffContext` (C-CP-13). Single-owner-at-a-time:
    stages run strictly sequentially on the driver thread (NO fan-out, NO
    `TaskGroup` — there is never more than one owner). Two consequences fall out of
    "sequential": there are no concurrent drains (it sidesteps the arc-15 F1-01
    sibling-drain timestamp gap), and each stage dispatches through the ordinary
    `StepDispatcher` (NEVER `SUB_AGENT_DISPATCH`), so a real multi-stage e2e
    genuinely SUCCEEDS — no sync/async-bridge recursion (the `HandoffContext` is a
    RECORD, not a dispatch).

    Non-hollow by ledger construction (the persisted distinction):
    - vs `EVALUATOR_OPTIMIZER` (no `branch_metadata` at all) — every stage persists
      `branch_metadata` (it is a per-role branch entry).
    - vs `ORCHESTRATOR_WORKERS` (a STAR — every worker's
      `branch_metadata.parent_action_id` is the ONE orchestrator) — here it CHAINS:
      stage *i*'s `branch_metadata.parent_action_id` is stage *(i-1)*'s `action_id`
      (the durable "who handed to whom" record); `branch_index` stays 0 (single
      owner — no siblings; the ordering rides the chain, not the fan-out ordinal).
      Stage 0 anchors at the workflow origin `workflow:{wf}:step:0`.
    Each stage is a per-role expert (`AgentRole(str(step.step_id))` → distinct binding
    via U-RT-114; the per-role catalog is B4); ownership transfers via a composed
    `HandoffContext` surfaced in `final_state["handoffs"]`.

    Terminal when no further handoff — structural: the declared step list IS the
    handoff sequence, terminal = after the last stage (no continue-signal read from
    step output, B-INTERSTEP). On a stage failure the chain stops (`cascade_policy`
    is degenerate for single-owner — no concurrent in-flight sibling to cancel):
    `cascade-cancel` → FAILED, `proceed` → PARTIAL (completed stages salvaged),
    `pause` → FAILED + pause-resume-not-yet-materialized (the resumable handoff-pause
    is a forward BUILD, B-FANOUT-PAUSE, parallel to ORCHESTRATOR_WORKERS). Returns
    `(RunResult, steps_executed)` for the `_execute_workflow_body` caller.
    """
    workflow_id = manifest_entry.workflow_id

    # Empty step sequence → trivially SUCCESS (mirrors the other strategies).
    if not steps:
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=RunStatus.SUCCESS,
            terminal_step_index=None,
            partial_state=None,
            final_state={"stages": {}, "handoffs": []},
            fail_class=None,
        ), 0

    # The on-stage-failure cascade reaction (§25.15.1) — resolved from the manifest's
    # (workload_class, engine_class, persona_tier) via the §11.4 D4 tunable, the same
    # source ORCHESTRATOR_WORKERS reads (SOLO→proceed / TEAM→pause / MTC→cascade-cancel;
    # the §25.11 DECENTRALIZED_HANDOFF row notes cascade-cancel is the typical
    # single-owner case).
    cascade_policy = d4_tunable(
        lookup_cell(manifest_entry.workload_class, manifest_entry.engine_class),
        manifest_entry.persona_tier,
    ).cascade_policy

    _resolver = getattr(ctx, "procedural_tier_snapshot_resolver", None)
    snapshot_ref = _resolver() if _resolver is not None else None

    # Buffer-time placeholder; the drain re-stamps to one drain-moment value. The
    # sequential chain is causally ordered, so this is monotonic by construction (no
    # concurrent drain — the F1-01 gap is structurally unreachable here).
    handoff_timestamp = datetime.now(UTC)
    actor_identity = ActorIdentity(ctx.ledger_writer.actor.actor_id)

    # § 25.3.2 — workflow.start (single-threaded on the driver thread).
    ctx.lifecycle_emitter.emit(WorkflowEventClass.WORKFLOW_START)

    stage_writers: list[BufferingLedgerWriter] = []
    stage_outputs: dict[str, Mapping[str, Any]] = {}
    handoffs: list[HandoffContext] = []
    # Stage 0 anchors at the workflow origin; each later stage chains off its
    # predecessor's action_id (the persisted handoff chain — the non-hollow signal).
    prev_action_id = f"workflow:{workflow_id}:step:0"

    def _finish(
        status: RunStatus, *, fail_class: str | None, salvage: bool
    ) -> tuple[RunResult, int]:
        # Drain the COMPLETED-stage writers in stage order (writer.branch_index =
        # stage ordinal) + emit one STEP_BOUNDARY per stage that ran.
        steps_executed = _drain_and_emit_step_boundaries(ctx, stage_writers)
        aggregate = {
            "stages": {sid: dict(out) for sid, out in stage_outputs.items()},
            "handoffs": [_handoff_record(h) for h in handoffs],
        }
        return RunResult(
            workflow_id=workflow_id,
            run_id=run_id,
            status=status,
            terminal_step_index=None,
            partial_state=aggregate if salvage else None,
            final_state=aggregate if status is RunStatus.SUCCESS else None,
            fail_class=fail_class,
        ), steps_executed

    for stage_index, step in enumerate(steps):
        role = derive_agent_role(step.step_id)
        # The spawning context the next stage descends from: its parent_action_id is
        # the prior stage's action_id (the chain; the workflow origin anchors stage 0).
        spawning = StepExecutionContext(
            workflow_id=workflow_id,
            parent_action_id=prev_action_id,
            parent_gate_level=resolve_parent_gate_level(manifest_entry),
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=ctx.ledger_writer.actor,
            parent_entry_hash="",
            parent_idempotency_key=_compute_step_idempotency_key(run_idempotency_key, stage_index),
            tenant_id=ctx.tenant_id,
            step_index=stage_index,
        )
        # Single owner → branch_index 0 (no siblings; causality rides the chained
        # parent_action_id, NOT the fan-out ordinal). step_index = the declared stage
        # ordinal (the dispatcher reads it for per-step policy / audit / skill hook).
        stage_ctx = compose_branch_child_context(
            spawning, branch_index=0, agent_role=role
        ).model_copy(update={"step_index": stage_index})
        this_action_id = compose_branch_step_action_id(stage_ctx, 0)
        # writer.branch_index = the stage ordinal — the DRAIN-order key (distinct
        # from the entry's branch_metadata.branch_index=0; different layers). One
        # writer per stage → one STEP_BOUNDARY per stage via _drain_and_emit_*.
        writer = BufferingLedgerWriter(actor=ctx.ledger_writer.actor, branch_index=stage_index)
        try:
            binding = resolve_step_binding(
                manifest_entry,
                str(step.step_id),
                default_model_binding=default_model_binding,
                persona_tier=manifest_entry.persona_tier,
            )
            output = step_dispatchers.lookup(step.step_kind).dispatch(
                binding, step, step_context=stage_ctx
            )
        except Exception as exc:
            # A stage owner failed → the chain stops (single-owner: no in-flight
            # sibling to cancel; the failed stage buffered nothing). cascade_policy
            # governs the disposition over the COMPLETED-stage prefix.
            if cascade_policy is CascadePolicy.PROCEED:
                return _finish(
                    RunStatus.PARTIAL,
                    fail_class=(
                        f"decentralized-handoff-stage-failure: {type(exc).__name__}: {exc}"
                    ),
                    salvage=True,
                )
            if cascade_policy is CascadePolicy.PAUSE:
                return _finish(
                    RunStatus.FAILED,
                    fail_class=(
                        "decentralized-handoff-pause-resume-not-yet-materialized: "
                        f"stage {stage_index} failed under cascade_policy=pause; the "
                        "resumable single-owner handoff-pause is a forward BUILD "
                        f"(B-FANOUT-PAUSE), not yet materialized — underlying: "
                        f"{type(exc).__name__}: {exc}"
                    ),
                    salvage=False,
                )
            return _finish(
                RunStatus.FAILED,
                fail_class=f"decentralized-handoff-stage-failure: {type(exc).__name__}: {exc}",
                salvage=False,
            )
        # Persist the stage as a per-role branch entry whose branch_metadata chains
        # off the prior stage (causality) + a fresh `completed` terminal entry (U-CP-84).
        append_branch_step_ledger_entry(
            branch_writer=writer,
            branch_context=stage_ctx,
            run_idempotency_key=run_idempotency_key,
            local_step_index=0,
            timestamp=handoff_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        append_branch_terminal_ledger_entry(
            branch_writer=writer,
            branch_context=stage_ctx,
            run_idempotency_key=run_idempotency_key,
            terminal_status="completed",
            timestamp=handoff_timestamp,
            procedural_tier_snapshot_ref=snapshot_ref,
        )
        stage_writers.append(writer)
        stage_outputs[str(step.step_id)] = output
        # Compose the ownership transfer to the next stage-expert (a RECORD; surfaced
        # in final_state). Terminal stage → no further handoff (structural).
        if stage_index < len(steps) - 1:
            next_step = steps[stage_index + 1]
            handoffs.append(
                _compose_handoff_to_next(
                    completed_action_id=this_action_id,
                    completed_context=stage_ctx,
                    next_step=next_step,
                    next_role=derive_agent_role(next_step.step_id),
                    actor_identity=actor_identity,
                )
            )
        prev_action_id = this_action_id

    # Terminal: the last stage completed, no further handoff → SUCCESS.
    return _finish(RunStatus.SUCCESS, fail_class=None, salvage=False)


__all__ = [
    "BufferingLedgerWriter",
    "DriverContext",
    "LedgerWriterLike",
    "LifecycleEventEmitterLike",
    "StepDispatcher",
    "append_branch_step_ledger_entry",
    "append_branch_terminal_ledger_entry",
    "bounded_barrier",
    "cascade_cancel_barrier",
    "cascade_policy_run_status",
    "dispatch_branch_step_shielded",
    "drain_branch_buffers",
    "execute_workflow",
    "resume_should_redispatch",
]

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
import hashlib
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable

from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import ActionID
from harness_core.workflow_event_class import WorkflowEventClass
from harness_is.state_ledger_entry_schema import Actor

from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding, resolve_step_binding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_errors import (
    EngineClassNotYetMaterializedError,
    TopologyPatternNotYetMaterializedError,
)
from harness_cp.workflow_driver_types import (
    RunResult,
    RunStatus,
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

# ---------------------------------------------------------------------------
# v1.4 in-scope sets (per C-CP-25 §25.1 + Implementation Plan §0.2)
# ---------------------------------------------------------------------------

_IN_SCOPE_TOPOLOGY: frozenset[TopologyPattern] = frozenset(
    {TopologyPattern.SINGLE_THREADED_LINEAR}
)

_IN_SCOPE_ENGINE_CLASSES: frozenset[EngineClass] = frozenset(
    {EngineClass.PURE_PATTERN_NO_ENGINE, EngineClass.SAVE_POINT_CHECKPOINT}
)


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
    surfaces that may bind step context to llm.inference span attributes or
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
        super().__init__(
            f"no StepDispatcher bound for step_kind {step_kind.value!r}"
        )
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


def _compute_step_idempotency_key(run_idempotency_key: str, step_index: int) -> str:
    """Per-step `idempotency_key = sha256(run_idempotency_key, step.index)`
    per C-CP-25 §25.3.3.7 + §25.6.
    """
    h = hashlib.sha256()
    h.update(run_idempotency_key.encode("utf-8"))
    h.update(b"\x00")
    h.update(str(step_index).encode("utf-8"))
    return h.hexdigest()


def execute_workflow(
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: DriverContext,
    *,
    default_model_binding: ModelBinding,
    step_dispatchers: StepDispatcherRegistry,
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
    # engine-class validation.
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

    # § 25.3.1 — Validate topology + engine class.
    if manifest_entry.topology_pattern not in _IN_SCOPE_TOPOLOGY:
        raise TopologyPatternNotYetMaterializedError(manifest_entry.topology_pattern)
    if manifest_entry.engine_class not in _IN_SCOPE_ENGINE_CLASSES:
        raise EngineClassNotYetMaterializedError(manifest_entry.engine_class)

    # § 25.6 — Replay-resumption check at re-entry.
    # `run_idempotency_key = sha256(run_id, workflow_id, entry_version)`
    # per CP spec v1.4 §25.6 line 270. `entry_version` was added to
    # `WorkflowManifestEntry` at U-CP-13 carrier-growth (CP plan v2.12),
    # resolving `[[fork-u-cp-56-resumption-underspec]]`.
    run_idempotency_key = _compute_run_idempotency_key(
        run_id,
        manifest_entry.workflow_id,
        extras=(str(manifest_entry.entry_version),),
    )

    # Selective per-run replay-resumption via N-lookup over the existing
    # IS `read_by_idempotency_key` primitive (CP plan v2.12 §0.1 +
    # §2.9 U-CP-56 AC #6 re-author; operator-ratified Path A-modified —
    # no new IS prefix-match primitive). For each step index, compute the
    # expected per-step idempotency_key and look it up; advance `resume_at`
    # over the contiguous prefix of materialized steps.
    resume_at = 0
    if manifest_entry.engine_class is EngineClass.SAVE_POINT_CHECKPOINT:
        resume_at = _determine_resume_at(
            ctx=ctx,
            run_idempotency_key=run_idempotency_key,
            step_count=len(steps),
            workload_class=manifest_entry.workload_class,
        )
        if resume_at > 0:
            ctx.lifecycle_emitter.emit(WorkflowEventClass.RESUMPTION)
    # Under pure-pattern-no-engine: no resumption-specific emission
    # (state-ledger native dedup per §8.2 row 3 handles per-step dedup).

    # § 25.3.2 — Emit workflow.start.
    ctx.lifecycle_emitter.emit(WorkflowEventClass.WORKFLOW_START)

    # § 25.3.3 — Iterate steps in declaration order (SINGLE_THREADED_LINEAR
    # has no parallel/fan-out branching). Begin at `resume_at` to skip
    # already-materialized steps from a prior crashed/drained run.
    accumulated: dict[str, Any] = {}
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
            )

        # § 25.3.3.2 — Resolve binding via U-CP-14.
        binding = resolve_step_binding(
            manifest_entry,
            str(step.step_id),
            default_model_binding=default_model_binding,
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
        step_idempotency_key_pre = _compute_step_idempotency_key(
            run_idempotency_key, step_index
        )
        # MVP defaults per C-CP-12 §12.4 + Spec_Control_Plane_v1_6.md §25.2.1:
        # parent_gate_level = AUTO; parent_sandbox_tier = TIER_1_PROCESS;
        # parent_entry_hash = "" (child shares parent ledger writer per
        # C-RT-17 §14.7.4); tenant_id = None (multi-tenancy not at v1.6 stack).
        step_context = StepExecutionContext(
            parent_action_id=(
                f"workflow:{manifest_entry.workflow_id}:step:{step_index}"
            ),
            parent_gate_level=GateLevel.AUTO,
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=ctx.ledger_writer.actor,
            parent_entry_hash="",
            parent_idempotency_key=step_idempotency_key_pre,
            tenant_id=None,
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
                fail_class=(
                    f"step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND: "
                    f"{exc}"
                ),
            )
        except Exception as exc:
            return RunResult(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                status=RunStatus.FAILED,
                terminal_step_index=step_index,
                partial_state=dict(accumulated),
                final_state=None,
                fail_class=f"step-failure: {type(exc).__name__}: {exc}",
            )

        # § 25.3.3.5 — Emit step.boundary.
        ctx.lifecycle_emitter.emit(WorkflowEventClass.STEP_BOUNDARY)

        # § 25.3.3.6 — Release lease (deferred per §25.3.3.3 above).

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
            )

        # Accumulate step output under its step id for terminal state.
        accumulated[str(step.step_id)] = dict(step_output)

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
            )

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
    )


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
    # `Identifier` is the IS-typed string newtype for state-ledger string ids;
    # we pass through the action_id verbatim plus the idempotency hex.
    payload = EntryPayload(
        action_id=Identifier(str(action_id)),
        idempotency_key=Identifier(step_idempotency_key),
        actor=ctx.ledger_writer.actor,
        timestamp=datetime.now(UTC),
    )
    write_key = WriteKey(
        thread_id=Identifier(workflow_id),
        step_id=Identifier(str(step_index)),
        idempotency_key=Identifier(step_idempotency_key),
    )
    ctx.ledger_writer.append(payload, write_key)
    # Discard return value — driver does not branch on append vs idempotent-noop;
    # both outcomes leave the ledger correctly composed per C-IS-07 §7.1.


__all__ = [
    "DriverContext",
    "LedgerWriterLike",
    "LifecycleEventEmitterLike",
    "StepDispatcher",
    "execute_workflow",
]

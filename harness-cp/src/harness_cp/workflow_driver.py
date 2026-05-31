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
from collections.abc import Coroutine
from typing import Any, Protocol, TypeVar, cast, runtime_checkable

from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import ActionID
from harness_core.workflow_event_class import WorkflowEventClass
from harness_is.state_ledger_entry_schema import Actor
from opentelemetry.trace import Status, StatusCode

from harness_cp.cp_shared_types import ActorIdentity, ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding, resolve_step_binding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_errors import (
    EngineClassNotYetMaterializedError,
    TopologyPatternNotYetMaterializedError,
)
from harness_cp.pause_resume_protocol import (
    PauseResumeProtocol,
    PauseResumeProtocolEventKind,
)
from harness_cp.pause_resume_protocol_types import (
    MaterialDiffPolicy,
    PauseSnapshot,
    WorkflowPauseReason,
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


_TProtocolResult = TypeVar("_TProtocolResult")


def _run_protocol_method_sync(
    coro: Coroutine[Any, Any, _TProtocolResult],
) -> _TProtocolResult:
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
                    protocol_event_kind=(
                        PauseResumeProtocolEventKind.RESUME_ATTEMPTED
                    ),
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
    tracer = ctx.tracer_provider.get_tracer(  # type: ignore[attr-defined]
        "harness.cp.workflow_driver"
    )
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
            span.set_status(
                Status(StatusCode.ERROR, result.fail_class or "FAILED")
            )
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
    # § 25.3.1 — Validate topology + engine class.
    if manifest_entry.topology_pattern not in _IN_SCOPE_TOPOLOGY:
        raise TopologyPatternNotYetMaterializedError(manifest_entry.topology_pattern)
    if manifest_entry.engine_class not in _IN_SCOPE_ENGINE_CLASSES:
        raise EngineClassNotYetMaterializedError(manifest_entry.engine_class)

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
                        protocol_event_kind=(
                            PauseResumeProtocolEventKind.PAUSE_CAPTURED
                        ),
                        event_sequence_id=(step_index << 2) | 1,
                        protocol_state_snapshot=pause_snapshot.model_dump(
                            mode="json"
                        ),
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
        step_idempotency_key_pre = _compute_step_idempotency_key(
            run_idempotency_key, step_index
        )
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
            parent_action_id=(
                f"workflow:{manifest_entry.workflow_id}:step:{step_index}"
            ),
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
                fail_class=(
                    f"step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND: "
                    f"{exc}"
                ),
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
                if (
                    ctx.pause_resume_protocol is not None
                    and ctx.pause_requested_flag.is_set()
                ):
                    protocol = cast(
                        PauseResumeProtocol, ctx.pause_resume_protocol
                    )
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
                                protocol_event_kind=(
                                    PauseResumeProtocolEventKind.PAUSE_CAPTURED
                                ),
                                event_sequence_id=(step_index << 2) | 2,
                                protocol_state_snapshot=(
                                    pause_snapshot.model_dump(mode="json")
                                ),
                                # Reading A apply (PR #83 sibling-extension):
                                # see fork doc U-CP-74 actor malformation.
                                actor=ActorIdentity(
                                    ctx.ledger_writer.actor.actor_id
                                ),
                            )
                        )
                    return RunResult(
                        workflow_id=manifest_entry.workflow_id,
                        run_id=run_id,
                        status=RunStatus.PAUSED,
                        terminal_step_index=(
                            step_index - 1 if step_index > 0 else None
                        ),
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
                    fail_class=(
                        f"step-failure: RT-FAIL-STEP-DISPATCH-TIMEOUT: {exc}"
                    ),
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
            tracer = ctx.tracer_provider.get_tracer("harness.cp.workflow_driver")  # type: ignore[attr-defined]
            with tracer.start_as_current_span("validator.evaluate") as evaluate_span:
                try:
                    evaluation = ctx.validator_framework.evaluate(  # type: ignore[attr-defined]
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
                        fail_class=(
                            f"validator-framework-failure: "
                            f"{type(exc).__name__}: {exc}"
                        ),
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
                    parent_hitl_span_id = format(
                        evaluate_span.get_span_context().span_id, "016x"
                    )
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
                    ask_user_question_surface = getattr(
                        ctx, "ask_user_question_surface", None
                    )
                    escalation_brief = evaluation.result.escalation_brief
                    if (
                        ask_user_question_surface is not None
                        and escalation_brief is not None
                    ):
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
                        _ = hitl_response  # noqa — outcome consumed by audit

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

"""Sub-agent dispatch composer — stage 5 LOOP_INIT (U-RT-59 ACs #2-#9).

Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17 (sub-agent dispatch
composer; Path A resolution of the StepDispatcher Protocol parent-context
gap). Concretes the `StepDispatcher` Protocol for `StepKind.SUB_AGENT_DISPATCH`
steps; composer body per §14.7.2 ten-step discipline, narrowed at v1.6 MVP per
operator-ratified fork resolutions documented below.

**Operator-ratified fork resolutions absorbed at landing.**

1. **Sync end-to-end (Class 3 spec-prose drift, ratified 2026-05-20).** Spec
   §14.7.1 declares async `dispatch`; §14.7.4 declares async
   `ChildWorkflowRunner.__call__`; §14.7.2 step 6 says `await self.child_workflow_runner(...)`.
   Stage 1 plumbing at `harness-cp/src/harness_cp/workflow_driver.py:175`
   froze the `StepDispatcher` Protocol as sync; `execute_workflow` is sync.
   Operator ratified land-sync per the de-facto Stage 1 contract.

2. **Class 1 — CP→OD audit-write gap (filed at landing).** Spec §14.7.2
   step 8 calls `ctx.audit_writer.append(tenant_id, audit_entry)` with
   `audit_entry: CPAuditLedgerEntry`. The real `audit_writer.append`
   signature takes OD-shaped `AuditLedgerEntry` (different schema); no
   CP→OD audit-shape converter exists. Joins the
   `[[fork-cp-is-wiring-gaps]]` Phase-6 CP-composer-authoring residual.
   Halt-route-split per `[[halt-route-split-AC-pattern]]`: AC #9 write
   half STRUCK; compose half landed (dispatch-fact `CPAuditLedgerEntry`
   produced for retirement-criterion-B evidence; end-to-end write owed
   to follow-on arc).

3. **Class 1 — async/sync dispatcher defect (filed at landing).**
   `ctx.llm_dispatcher` (U-RT-58 `RetryBreakerFallbackDispatcher` wrapper)
   is `async def dispatch`; the sync driver returns a coroutine if bound
   as `INFERENCE_STEP → ctx.llm_dispatcher`. U-RT-58 wired the wrapper at
   stage 5 without integration-driving through the sync driver — sleeping
   defect surfaced at U-RT-59. Plan AC #11 INFERENCE_STEP binding clause
   STRUCK at v1.6 MVP; registry binds only `SUB_AGENT_DISPATCH`. Resolution
   (sync facade vs async driver vs Protocol revision) owed to follow-on
   arc.

4. **Class 3 prose drift (rolled into landing).** `ctx.audit_writer`
   (not `ctx.audit_ledger_writer`); `harness_cp.topology_subagent_namespace`
   (not `harness_cp.handoff_context`); `ProposedAction` real shape is
   `action_kind / payload / brief` (not `text`); `ChildWorkflowRunner`
   carries additive `default_model_binding` kwarg.

**Composer body shape (v1.6 MVP, post-fork-absorption).**

1. Pydantic-validate `step.step_payload → SubAgentDispatchPayload` (AC #3)
2. Compose `HandoffContext` from `step_context` + payload (AC #4)
3. Compute `SubAgentGateLevelDescent` via `ctx.handoff_registry.dispatch` (AC #5a)
4. Verify topology admissibility via `ctx.topology_dispatcher` + `is_admissible` (AC #5b)
5. Open `subagent.span` + set canonical `subagent.*` + narrow `topology.*` attributes (AC #6)
6. Invoke child runner sync (AC #7)
7. Map child `RunResult.status` → `subagent.result_status` (AC #8)
8. Compose `CPAuditLedgerEntry` via `compose_dispatch_audit` (AC #9 partial — compose only)
9. Return step output (child `final_state` or `partial_state`)
10. Typed error propagation: typed error subclasses bubble; outer driver's
    try/except per C-CP-25 §25.3.3.4 maps to fail class

**Failure-mode taxonomy (per spec §14.7).** Three typed errors are raised
from this module + propagated through the sync driver:

- `SubAgentDispatchPayloadShapeError` → `RT-FAIL-PAYLOAD-SHAPE`
- `SubAgentDispatchTopologyInadmissibleError` → `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE`
- `SubAgentChildFailedError` → `RT-FAIL-SUB-AGENT-CHILD-FAILED`
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from harness_core.identity import ActionID
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.handoff_context import (
    ActionKind,
    HandoffContext,
    LedgerEntryRef,
    ProposedAction,
    RetryHistory,
    StateSummary,
)
from harness_cp.sub_agent_brief import SubAgentBrief
from harness_cp.topology_subagent_namespace import (
    SUBAGENT_NAMESPACE_SCHEMA,
    TOPOLOGY_NAMESPACE_SCHEMA,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepExecutionContext,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Identifier
from pydantic import BaseModel, ConfigDict, ValidationError

from harness_runtime.lifecycle.child_workflow_runner import ChildWorkflowRunner
from harness_runtime.lifecycle.handoff import RuntimeHandoffRegistry
from harness_runtime.lifecycle.topology_dispatcher import RuntimeTopologyDispatcher

__all__ = [
    "RuntimeSubAgentDispatcher",
    "SubAgentChildFailedError",
    "SubAgentDispatchPayload",
    "SubAgentDispatchPayloadShapeError",
    "SubAgentDispatchTopologyInadmissibleError",
    "compose_child_action_id",
]


# ---------------------------------------------------------------------------
# Payload schema (AC #3)
# ---------------------------------------------------------------------------


class SubAgentDispatchPayload(BaseModel):
    """Typed shape of a `SUB_AGENT_DISPATCH` step's `step_payload` (§14.7.2 step 1).

    `step.step_payload` is opaque to the driver per C-CP-25 §25.3.3.4 but
    typed at the dispatcher: v1.6 pins the convention that
    `SUB_AGENT_DISPATCH` payloads carry the child workflow's manifest + step
    sequence + lead-agent-authored brief. The composer pydantic-validates
    `step.step_payload → SubAgentDispatchPayload`; mis-shaped payloads
    surface as `SubAgentDispatchPayloadShapeError` mapping to
    `RT-FAIL-PAYLOAD-SHAPE` (existing fail class from §14.5).
    """

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    child_workflow_id: str
    """The child sub-workflow's workflow_id (per C-CP-06 §6.1)."""

    child_manifest_entry: WorkflowManifestEntry
    """The child's manifest entry — engine_class, topology_pattern,
    workload_class, persona_tier, per-step overrides, fallback chain."""

    child_steps: Sequence[WorkflowStep]
    """The child's declarative step sequence (in declaration order)."""

    brief: SubAgentBrief
    """Lead-agent-authored sub-agent brief (C-CP-13 §13.2 4-field +
    summary_hash). Drives HandoffContext composition + gate-level descent +
    audit-entry response_hash."""


# ---------------------------------------------------------------------------
# Typed errors (per spec §14.7 failure-mode taxonomy)
# ---------------------------------------------------------------------------


class SubAgentDispatchPayloadShapeError(Exception):
    """`step.step_payload` does not conform to `SubAgentDispatchPayload`.

    Driver's try/except per C-CP-25 §25.3.3.4 maps to `RT-FAIL-PAYLOAD-SHAPE`
    (existing fail class from spec §14.5).
    """


class SubAgentDispatchTopologyInadmissibleError(Exception):
    """Child manifest's topology + workload pair fails C-CP-10 §10.3 admissibility.

    Raised before `subagent.span` opens; no partial spans emitted. Driver's
    try/except per C-CP-25 §25.3.3.4 maps to
    `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE`.
    """


class SubAgentChildFailedError(Exception):
    """Child sub-workflow's terminal `RunResult.status == FAILED`.

    Raised after the composer's child-runner invocation per §14.7.2 step 6.
    Composer sets `subagent.result_status = "failed"` on the `subagent.span`
    before re-raising; the outer driver's try/except per C-CP-25 §25.3.3.4
    maps to `RT-FAIL-SUB-AGENT-CHILD-FAILED`.
    """


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def compose_child_action_id(parent_action_id: str, child_workflow_id: str) -> ActionID:
    """Compose the child sub-workflow's action_id (§14.7.4 deferred-to-discretion).

    Suggested shape per spec §14.7 "Deferred to implementation discretion":
    `f"{parent_action_id}::child::{child_workflow_id}"` for traceability. The
    `::child::` infix is a stable visual anchor in operator-facing ledger
    inspection without invoking a hash (which would lose the parent linkage).
    """
    return ActionID(f"{parent_action_id}::child::{child_workflow_id}")


def _empty_summary_hash() -> str:
    """`sha256(b"")` hex-64 — the v1.6 MVP `StateSummary.summary_hash` default.

    Per spec §14.7.3 v1.6 MVP composition: `state_summary.summary_hash =
    sha256(b"")`. Deferred to v1.7+ when actual summarization invocation
    lands (C-CP-21 §21.4)."""
    return hashlib.sha256(b"").hexdigest()


def _compose_handoff_context(
    *,
    step_context: StepExecutionContext,
    payload: SubAgentDispatchPayload,
) -> HandoffContext:
    """Build the v1.6 MVP `HandoffContext` per spec §14.7.3 (AC #4).

    Bounded-reduction composition per §14.7.3 table:

    - `proposed_action` — `ProposedAction(action_kind=SUB_AGENT_DISPATCH,
      payload={"objective": brief.objective}, brief=payload.brief)` per
      real `ProposedAction` shape (spec prose `ProposedAction(text=...)`
      was incorrect; rolled into the Class 3 spec-prose-drift note).
    - `agent_confidence` — `None` at v1.6 MVP.
    - `failed_attempts` — empty tuple.
    - `alternatives_considered` — empty tuple.
    - `state_summary` — `StateSummary(relevant_entries=(parent_entry_ref,),
      summary_text="", summary_hash=sha256(b""),
      idempotency_key=step_context.parent_idempotency_key,
      external_references=())`.
    - `audit_trail_link` — `LedgerEntryRef(action_id=step_context.parent_action_id,
      entry_hash=step_context.parent_entry_hash, actor=step_context.parent_actor.actor_id)`
      per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A.
    - `retry_history` — empty `RetryHistory` (cardinality 0, count 0).
    """
    parent_action_id = cast(ActionID, step_context.parent_action_id)
    # `step_context.parent_actor` is the IS-exported `Actor` (BaseModel with
    # `actor_class` + `actor_id`); `LedgerEntryRef.actor` is the CP-owned
    # `ActorIdentity` (NewType[str]). Project Actor → ActorIdentity via the
    # canonical `actor_id` string per the CP-vs-IS actor-identity carrier-map
    # convention at `harness_cp.cp_shared_types` §53.
    actor_identity = ActorIdentity(step_context.parent_actor.actor_id)
    parent_entry_ref = LedgerEntryRef(
        action_id=parent_action_id,
        entry_hash=step_context.parent_entry_hash,
        actor=actor_identity,
    )
    return HandoffContext(
        proposed_action=ProposedAction(
            action_kind=ActionKind.SUB_AGENT_DISPATCH,
            payload={"objective": payload.brief.objective},
            brief=payload.brief,
        ),
        agent_confidence=None,
        failed_attempts=(),
        alternatives_considered=(),
        state_summary=StateSummary(
            relevant_entries=(parent_entry_ref,),
            summary_text="",
            summary_hash=_empty_summary_hash(),
            idempotency_key=Identifier(step_context.parent_idempotency_key),
            external_references=(),
        ),
        audit_trail_link=parent_entry_ref,
        retry_history=RetryHistory(
            attempts=(),
            retry_count=0,
            last_retry_cause=None,
        ),
    )


# ---------------------------------------------------------------------------
# Composer (AC #2 — Protocol satisfaction)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class RuntimeSubAgentDispatcher:
    """Sub-agent dispatch composer (U-RT-59; satisfies `StepDispatcher` Protocol).

    Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17. Sync `dispatch`
    method satisfying the sync `StepDispatcher` Protocol declared at
    `harness-cp/src/harness_cp/workflow_driver.py:175` (`@runtime_checkable`).
    Constructed at bootstrap stage 5 (LOOP_INIT) per spec §14.7.7
    "Integration with C-RT-04"; bound to `HarnessContext.sub_agent_dispatcher`.

    Composition arguments per §14.7.1:

    - `handoff_registry` (U-RT-26) — composes `HandoffContext` + computes
      `SubAgentGateLevelDescent` + composes `CPAuditLedgerEntry`.
    - `topology_dispatcher` (U-RT-40) — dispatches `TopologyPattern` per
      child manifest + verifies admissibility.
    - `tracer_provider` (C-RT-06) — opens the `subagent.span`.
    - `child_workflow_runner` (this arc, U-RT-59 AC #7) — invokes the
      child sub-workflow in-process per §14.7.4 recursive primitive.
    """

    handoff_registry: RuntimeHandoffRegistry
    topology_dispatcher: RuntimeTopologyDispatcher
    tracer_provider: Any
    """Typed `Any` per the C-RT-04 pattern (avoids pulling OTel SDK type
    into the schema layer); matches `RuntimeLLMDispatcher` /
    `RetryBreakerFallbackDispatcher` discipline."""

    child_workflow_runner: ChildWorkflowRunner

    # Module-bound canonical attribute name constants (per spec §14.7.5
    # "Producer-side attribute carrier reference" — imported from the
    # canonical carrier; not hand-coded as strings). Frozen at construction
    # so a typo in the spec carrier surfaces at dataclass instantiation,
    # not at first dispatch.
    _subagent_attr_names: tuple[str, ...] = field(init=False)
    _topology_attr_names: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_subagent_attr_names",
            tuple(s.attribute_name for s in SUBAGENT_NAMESPACE_SCHEMA),
        )
        object.__setattr__(
            self,
            "_topology_attr_names",
            tuple(s.attribute_name for s in TOPOLOGY_NAMESPACE_SCHEMA),
        )

    def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Sync dispatch composer body (§14.7.2; v1.6 MVP per fork resolutions).

        `binding` is typed `Any` here for the same C-RT-04 reason: the
        Protocol declares `StepEffectiveBinding`; the runtime objects
        satisfy the structural shape. Pyright cannot infer Protocol
        satisfaction at this site, so the type relaxation moves to the
        composer. The composer reads `binding.model_binding` as the
        child's `default_model_binding` per spec §14.7.4 +
        `ChildWorkflowRunner` additive Protocol shape.

        Raises
        ------
        SubAgentDispatchPayloadShapeError
            `step.step_payload` failed Pydantic validation against
            `SubAgentDispatchPayload`.
        SubAgentDispatchTopologyInadmissibleError
            Child manifest's `(topology, workload_class)` pair fails
            C-CP-10 §10.3 admissibility.
        SubAgentChildFailedError
            Child sub-workflow's terminal `RunResult.status == FAILED`.
        """
        # --- Step 1: validate payload shape (AC #3) ------------------------
        try:
            payload = SubAgentDispatchPayload.model_validate(dict(step.step_payload))
        except ValidationError as exc:
            raise SubAgentDispatchPayloadShapeError(
                f"SUB_AGENT_DISPATCH step {str(step.step_id)!r} step_payload "
                f"failed SubAgentDispatchPayload validation: {exc}"
            ) from exc

        # --- Step 2: compose HandoffContext (AC #4) ------------------------
        handoff_context = _compose_handoff_context(
            step_context=step_context, payload=payload
        )

        # --- Step 3: compute gate-level descent (AC #5a) -------------------
        parent_action_id = cast(ActionID, step_context.parent_action_id)
        descent = self.handoff_registry.dispatch(
            parent_action_id=parent_action_id,
            parent_gate_level=step_context.parent_gate_level,
            parent_sandbox_tier=step_context.parent_sandbox_tier,
            sub_agent_brief=payload.brief,
            operator_override=None,
        )

        # --- Step 4: verify topology admissibility (AC #5b) ----------------
        topology = self.topology_dispatcher.dispatch(payload.child_manifest_entry)
        admissible = self.topology_dispatcher.is_admissible(
            topology, payload.child_manifest_entry.workload_class
        )
        if not admissible:
            raise SubAgentDispatchTopologyInadmissibleError(
                f"child manifest topology {topology.value!r} is not admissible "
                f"for workload_class "
                f"{payload.child_manifest_entry.workload_class.value!r} per "
                f"C-CP-10 §10.3"
            )

        # --- Step 5: open subagent.span + set attributes (AC #6) -----------
        tracer = self.tracer_provider.get_tracer(
            "harness.runtime.sub_agent_dispatch"
        )
        with tracer.start_as_current_span("subagent.span") as span:
            span_context = span.get_span_context()
            span_id_hex = f"{span_context.span_id:016x}"
            parent_span_context = (
                span.parent if hasattr(span, "parent") and span.parent else None
            )
            parent_span_id_hex = (
                f"{parent_span_context.span_id:016x}"
                if parent_span_context is not None
                else "0" * 16
            )

            # Open-time `subagent.*` attributes (3 of 7 set now; 4 close-time)
            span.set_attribute("subagent.span.id", span_id_hex)
            span.set_attribute("subagent.parent_span_id", parent_span_id_hex)
            # Open-time `topology.*` attributes (2 narrow-subset attributes;
            # fan-out-specific 8 attributes NOT set per §14.7.2 step 5).
            span.set_attribute("topology.pattern", topology.value)
            span.set_attribute(
                "topology.workload_class",
                payload.child_manifest_entry.workload_class.value,
            )

            # --- Step 6: invoke child runner (AC #7) -----------------------
            try:
                child_result = self.child_workflow_runner(
                    workflow_id=payload.child_workflow_id,
                    manifest_entry=payload.child_manifest_entry,
                    steps=payload.child_steps,
                    handoff_context=handoff_context,
                    descent=descent,
                    default_model_binding=binding.model_binding,
                )
            except Exception:
                # Typed errors from child execution: annotate span +
                # propagate. Spec §14.7.2 step 10.
                span.set_attribute("subagent.result_status", "failed")
                span.set_attribute("subagent.request_blocked_by_budget", False)
                span.set_attribute("subagent.tokens_in", 0)
                span.set_attribute("subagent.tokens_out", 0)
                span.set_attribute("subagent.cached_tokens_in", 0)
                # Compose audit entry even on child runner unhandled exception
                # (dispatch-fact persists; child failure-fact lives at span).
                _ = self.handoff_registry.compose_dispatch_audit(
                    parent_action_id=parent_action_id,
                    descent=descent,
                    brief_hash=self.handoff_registry.dispatch_response_hash(
                        payload.brief
                    ),
                )
                raise

            # --- Step 7: map child result → span (AC #8) -------------------
            if child_result.status == RunStatus.SUCCESS:
                span.set_attribute("subagent.result_status", "completed")
                span.set_attribute("subagent.request_blocked_by_budget", False)
                step_output: Mapping[str, Any] = dict(child_result.final_state or {})
            elif child_result.status == RunStatus.DRAINED:
                # Drain is operator-initiated (not failure) per §14.7.2 step 7
                span.set_attribute("subagent.result_status", "completed")
                span.set_attribute("subagent.request_blocked_by_budget", False)
                step_output = dict(child_result.partial_state or {})
            elif child_result.status == RunStatus.FAILED:
                span.set_attribute("subagent.result_status", "failed")
                span.set_attribute("subagent.request_blocked_by_budget", False)
                # Token counters set to 0 at v1.6 MVP (child does not surface
                # cost rollup through RunResult per C-CP-25 §25.2; deferred
                # to v1.7+ extension).
                span.set_attribute("subagent.tokens_in", 0)
                span.set_attribute("subagent.tokens_out", 0)
                span.set_attribute("subagent.cached_tokens_in", 0)
                # --- Step 8 partial: compose audit entry (AC #9 partial) ---
                # CP→OD audit-write composition Class 1 deferred; compose
                # the dispatch-fact entry for retirement criterion B evidence;
                # do NOT call ctx.audit_writer.append(...) per fork resolution.
                _ = self.handoff_registry.compose_dispatch_audit(
                    parent_action_id=parent_action_id,
                    descent=descent,
                    brief_hash=self.handoff_registry.dispatch_response_hash(
                        payload.brief
                    ),
                )
                raise SubAgentChildFailedError(
                    f"child sub-workflow {payload.child_workflow_id!r} "
                    f"terminated with RunStatus.FAILED; fail_class="
                    f"{child_result.fail_class!r}"
                )
            else:
                # PARTIAL — reserved per C-CP-25 §25.2. v1.6 MVP treats as
                # success-equivalent (per spec §14.7.2 step 7 enumeration:
                # only SUCCESS / DRAINED / FAILED named).
                span.set_attribute("subagent.result_status", "completed")
                span.set_attribute("subagent.request_blocked_by_budget", False)
                step_output = dict(child_result.partial_state or {})

            # Close-time `subagent.*` token attributes (4 attrs; 0 at v1.6
            # MVP — child cost rollup not surfaced through RunResult per
            # C-CP-25 §25.2 v1.6 shape).
            span.set_attribute("subagent.tokens_in", 0)
            span.set_attribute("subagent.tokens_out", 0)
            span.set_attribute("subagent.cached_tokens_in", 0)

            # --- Step 8: compose audit entry (AC #9 partial) ---------------
            # CP→OD audit-write composition Class 1 deferred per landing fork
            # resolution. Compose the dispatch-fact CPAuditLedgerEntry for
            # retirement criterion B evidence (H_T-CP-13). End-to-end write
            # via ctx.audit_writer.append(...) is owed to follow-on arc
            # (joins fork-cp-is-wiring-gaps Phase 6 CP-composer authoring).
            _ = self.handoff_registry.compose_dispatch_audit(
                parent_action_id=parent_action_id,
                descent=descent,
                brief_hash=self.handoff_registry.dispatch_response_hash(
                    payload.brief
                ),
            )

            # --- Step 9: return step output --------------------------------
            return step_output



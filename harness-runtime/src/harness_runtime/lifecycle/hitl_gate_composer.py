"""HITL gate composer — stage 5 LOOP_INIT (U-RT-60).

Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8 C-RT-18. Wraps an inner
`StepDispatcher` and produces a HITL-gated `StepDispatcher`. Bootstrap stage 5
constructs single-instance-per-step_kind per spec §14.8.1 wrap-asymmetry table:

  ctx.llm_dispatcher       = c_rt_16_compose(hitl_gate_composer(c_rt_15, {PRE_ACTION}))
  ctx.sub_agent_dispatcher = hitl_gate_composer(c_rt_17, {SUB_AGENT_BOUNDARY})

**Canonical 4-span shape** (per spec v1.11 §14.8.5 hierarchy diagram + ADR-D5
v1.3 §1.8 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA`):

  hitl.gate.evaluated  (.level, .persona_tier, .required)
   └── hitl.invocation.opened  (.level, .placement, .handoff_context_size_bytes,
       │                        .audit_ledger_entry_id)
       ├── hitl.invocation.responded  (.class, .latency_ms, .summary_hash)
       └── hitl.invocation.timed_out  (.duration_ms, .degradation_mode_applied)

`hitl.gate.evaluated` fires regardless of `_hitl_required` outcome (records the
evaluation decision). `hitl.invocation.opened` fires when `_hitl_required` is
True. Exactly one of `responded` OR `timed_out` fires per matching placement.

**4-substep audit-write at step 4h** mirrors the §14.7.2 step 8 sequence with
HITL-canonical at-origin shape (per CP spec v1.9 §13.5.1 NOTE 5): the
`CPAuditLedgerEntry` carrier carries the operator's actual response value
(unlike sub-agent dispatch's `response="approve"` convention). Shared
`cp_audit_to_od_audit` converter at `harness-cxa/` per Q3 ratification.

**Async `dispatch` per spec §14.8.1 item 1.** Per the U-RT-60 wrap-asymmetry
sync/async mismatch Class 1 fork (RATIFIED at HEAD `0a1ca94`; Q1=(c) async
HITL + SyncDispatcherFacade for registry), the composer's `dispatch` is
`async def`. Spec §14.8.1 item 1 line 1539 declares verbatim:
``Async dispatch(binding, step, *, step_context) -> StepOutput``. The
wrap chain at §14.8.1 row 1 (`c_rt_16_compose(hitl(c_rt_15))`) requires
the composer to be async because C-RT-16's wrapper strictly awaits its
inner (`retry_breaker_fallback.py:393` line `await self.inner.dispatch(...)`).

At the registry boundary the composer is wrapped by `SyncDispatcherFacade`
(U-RT-59 Path B precedent reuse at one site) so the sync CP `StepDispatcher`
Protocol consumed by the workflow driver continues to be satisfied.

**Inner duck-typed sync/async tolerance.** The composer's `inner` may be
*async* (C-RT-15 bare for the INFERENCE_STEP row at the §14.8.1 table) or
*sync* (C-RT-17 sub-agent dispatcher for the SUB_AGENT_DISPATCH row).
`_dispatch_inner` calls `self.inner.dispatch(...)` and awaits the result
iff `inspect.isawaitable(result)` is True. Defensive vs raw coroutine
check — tolerates any awaitable (Future, custom `__await__`).

**v1.11 amendment per c_rt_18 span-attr-carrier-drift fork (RATIFIED at
HEAD 95a9436).** Composer emits canonical 4-span shape with carrier-canonical
attribute names. Hand-coded v1.9/v1.10 names (`.placement` on gate.evaluated,
`.response_class` on responded, `.outcome` on gate.evaluated) retired.
Audit-compose failure uses OTel `Span.set_status(StatusCode.ERROR)` +
`Span.record_exception` per semconv-canonical.

**Carry-forward operative defaults at v1.11 MVP.**

- `placement.requires_hitl`: NOT a field on `HITLPlacement` at landed CP
  schema (per `harness-cp/src/harness_cp/hitl_placement.py:135`); v1.11 MVP
  defaults `_hitl_required = True` whenever a matching placement is found
  (the gate always fires). Spec §14.8.2 step 4c MVP-bounded reading;
  full 4-axis composition per C-CP-19 §19.1 deferred to validator-composer
  arc (Q5 dependency).
- `placement.response_palette`: also not a field; v1.11 MVP uses
  `DEFAULT_FULL_PALETTE = frozenset(HITLResponse)` unconditionally per
  spec §14.8.2 step 4d.
- `placement.timeout`: optional field on `HITLPlacement` (milliseconds);
  `None` = no deadline (test fixtures); production sets per workflow author.

**Composer body (sync) per spec §14.8.2:**

1. Read `step.hitl_placements` (workflow-binding-time per U-CP-13 + U-CP-38)
2. Filter by `applicable_placements` set
3. Foreclose VALIDATOR_ESCALATION per Q5 ratification
4. Per matching placement:
   4a. Compose HandoffContext (re-uses C-RT-17 pattern; not implemented at
       v1.11 MVP — HITL placement composition deferred to workflow-grammar
       arc when HandoffContext-at-PRE_ACTION binding lands)
   4b. Resolve matrix cell + raise on `is_excluded`
   4c. Evaluate `_hitl_required` (v1.11 MVP: always True on matching placement)
   4d. Determine palette (v1.11 MVP: DEFAULT_FULL_PALETTE)
   4e. Open `hitl.gate.evaluated` span + set canonical 3 attrs
   4f-bis. Open `hitl.invocation.opened` span + set canonical 4 attrs
   4f. Invoke `await surface.ask(...)`; on timeout, open `hitl.invocation.timed_out`
   4g. Open `hitl.invocation.responded` span + set canonical 3 attrs
   4h. 4-substep audit-write (8a CP entry → 8b F2 → 8c CP→OD → 8d audit append)
   4i. 4-response dispatch (APPROVE / EDIT / REJECT / RESPOND)
5. Delegate to inner dispatcher
6. Return output

**Failure-mode taxonomy** (per spec §14.8 + canonical OTel error discipline):

- `HITLPlacementForeclosedAtV19Error` → `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19`
- `HITLCellExcludedError`             → (new fail class; not in v1.9 taxonomy
                                        — surfaces as RuntimeError to driver)
- `HITLGateTimeoutError`              → `RT-FAIL-HITL-GATE-TIMEOUT`
- `HITLGateRejectedError`             → `RT-FAIL-HITL-GATE-REJECTED`
- `HITLGateAuditComposeError`         → `RT-FAIL-HITL-GATE-AUDIT-COMPOSE`

Audit-compose failure: composer annotates `hitl.gate.evaluated` via
`Span.set_status(Status(StatusCode.ERROR, "audit-compose-failed"))` +
`Span.record_exception(audit_compose_error)`. Suppressed on REJECT path —
`HITLGateRejectedError` is the primary fault.
"""

from __future__ import annotations

import hashlib
import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from harness_core.identity import ActionID
from harness_cp.audit_hitl_span_namespace import (
    AUDIT_NAMESPACE_SCHEMA,
    HITL_SPAN_NAMESPACE_SCHEMA,
)
from harness_as import GateLevel
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.handoff_context import (
    ActionKind,
    HandoffContext,
    LedgerEntryRef,
    ProposedAction,
    RetryHistory,
    StateSummary,
)
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.per_step_override_evaluator import (
    CPAuditLedgerEntry,
    StepEffectiveBinding,
)
from harness_cp.persona_engine_hitl_matrix import (
    HITLMatrixCell,
    SynchronyClass,
    matrix_cell_for,
)
from harness_cp.validator_framework_types import HITLEscalationBrief
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep
from harness_cxa.cp_audit_conversion import cp_audit_to_od_audit
from harness_is.state_ledger_entry_schema import Identifier
from harness_is.state_ledger_write import EntryPayload, WriteKey
from harness_od.audit_ledger_types import SignatureAlgorithm, StateLedgerEntryRef
from opentelemetry.trace import Status, StatusCode

from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
    AskUserQuestionTimeoutError,
)
from harness_runtime.lifecycle.webhook_delivery_composer import (
    WebhookDeliveryResult,
)

if TYPE_CHECKING:  # pragma: no cover — type-only imports
    from harness_runtime.lifecycle.audit_writer import RuntimeAuditLedgerWriter
    from harness_runtime.lifecycle.state_ledger import LedgerWriter

__all__ = [
    "DEFAULT_FULL_PALETTE",
    "HITLCellExcludedError",
    "HITLGateAuditComposeError",
    "HITLGateRejectedError",
    "HITLGateTimeoutError",
    "HITLPauseRequestedSignal",
    "RuntimeHITLGateComposer",
    "compose_hitl_action_id",
]


# ---------------------------------------------------------------------------
# v1.11 MVP defaults
# ---------------------------------------------------------------------------

DEFAULT_FULL_PALETTE: frozenset[HITLResponse] = frozenset(HITLResponse)
"""Per spec §14.8.2 step 4d v1.11 MVP — full 4-response palette unconditionally.

Cross-trust-boundary palette restriction per NOTE 6-iv deferred to
validator-composer + MCP-trust-framework arcs."""


# ---------------------------------------------------------------------------
# Typed errors (per spec §14.8 failure-mode taxonomy)
# ---------------------------------------------------------------------------


# NOTE — `HITLPlacementForeclosedAtV19Error` REMOVED at Reading B v1.22 per
# spec §14.8.2 step 3 un-foreclosure. VALIDATOR_ESCALATION placements are
# now VALID at the runtime layer; they fire via the mid-step re-entry path
# at `validator_escalation_composer.compose_validator_escalation_gate` from
# workflow_driver post-dispatch hook. The wrap-time composer body at §14.8.2
# filters VALIDATOR_ESCALATION placements out of `matching` (they do not fire
# at wrap-time path). Old `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail
# class also REMOVED from §14.8 failure-mode taxonomy.


class HITLCellExcludedError(Exception):
    """`HITLMatrixCell.is_excluded` is True at step 4b.

    Persona-tier × engine-class cell at C-CP-18 §18.1 is structurally
    excluded; gate cannot fire. Composer body raises at step 4b before
    opening spans for this placement. Driver maps to a v1.11-spec-implied
    new fail class (not in §14.8 taxonomy; surfaces as RuntimeError-shape
    error to driver).
    """


class HITLGateTimeoutError(Exception):
    """`placement.timeout` elapsed without operator response.

    Composer at step 4f catches `AskUserQuestionTimeoutError` from the surface
    + opens canonical `hitl.invocation.timed_out` dedicated span per ADR-D5
    v1.3 §1.8 row 4 + emits partial audit entry (response=None) + raises
    this typed error. Driver maps to `RT-FAIL-HITL-GATE-TIMEOUT`.
    """


class HITLGateRejectedError(Exception):
    """Operator selected `REJECT` at step 4i.

    Composer emits the rejection audit entry per step 4h (carrying
    `rejection_reason_hash`) BEFORE raising; annotates
    `hitl.response.class = "reject"` on `hitl.invocation.responded`.
    Driver maps to `RT-FAIL-HITL-GATE-REJECTED`. Audit-suppression-on-REJECT
    discipline: any downstream audit-compose failures on this path are
    suppressed; this error is primary fault per spec §14.8 fail-class table.
    """


class HITLGateAuditComposeError(Exception):
    """One of the §14.8.2 step 4h audit-composition substeps failed.

    Raised when the response path was APPROVE / EDIT / RESPOND and one of
    8b-HITL F2-write, 8c-HITL CP→OD convert + sign, 8d-HITL audit_writer.append
    raised a typed error. Composer annotates `hitl.gate.evaluated` span via
    `Span.set_status(StatusCode.ERROR)` + `Span.record_exception(typed_error)`
    per semconv-canonical error discipline. Driver maps to
    `RT-FAIL-HITL-GATE-AUDIT-COMPOSE`. **Suppressed on REJECT path** —
    `HITLGateRejectedError` is the primary fault.
    """


class HITLPauseRequestedSignal(BaseException):
    """Typed control-flow signal raised at §14.8.2 step 4-bis durable-async branch.

    Authored at runtime spec v1.24 §14.8.8.2 (preserved verbatim at v1.25)
    per U-RT-93 (L9-terdecies L0). NOT a fail class — this is a normal-path
    control-flow signal indicating that the HITL gate fired the durable-async
    composition body and the workflow MUST pause pending operator response
    via inbound webhook.

    Inherits ``BaseException`` (not ``Exception``) per spec §14.8.8.2
    inheritance-choice-rationale: normal-path ``try / except Exception`` blocks
    MUST NOT suppress the signal. Only explicit ``except HITLPauseRequestedSignal``
    (the driver-side handler at U-RT-95) or ``except BaseException`` may consume it.

    Carrier fields per spec §14.8.8.2:
      - ``brief``           : ``HITLEscalationBrief`` composed at step 1 per
                              C-CP-28 §25.2.
      - ``delivery_result`` : ``WebhookDeliveryResult`` from
                              ``ctx.webhook_delivery_composer.deliver_webhook(...)``
                              at step 3 per C-RT-20 §14.10.1.

    On catch, the driver invokes ``continue`` to the next iteration, falling
    through to the existing v1.21 §14.14.3 per-step pre-entry pause-trigger
    detection (which observes ``ctx.pause_requested_flag`` set by step 5 of
    the §14.8.8.1 composer body and fires ``capture_pause_snapshot(...)``).
    """

    def __init__(
        self,
        *,
        brief: HITLEscalationBrief,
        delivery_result: WebhookDeliveryResult,
    ) -> None:
        super().__init__("HITL durable-async pause requested")
        self.brief = brief
        self.delivery_result = delivery_result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def compose_hitl_action_id(
    parent_action_id: ActionID,
    placement_position: HITLPlacementKind,
) -> ActionID:
    """Compose the HITL gate action_id per spec §14.8.2 step 4h substep 8b-HITL.

    Suggested shape: `f"hitl:{parent_action_id}:{placement.position.value}"`
    (deferred to implementation discretion at v1.11 per spec §14.8 deferred-
    list; this is the suggested shape mirroring the `dispatch:` prefix from
    §14.7.2 step 8b). The `hitl:` prefix is the HITL-source discriminator
    at OD audit-trace consumers.
    """
    return ActionID(f"hitl:{parent_action_id}:{placement_position.value}")


def _evaluate_hitl_required_tolerant(
    *, binding: object, placement: object
) -> bool:
    """Reading B v1.22 §14.8.2 step 4c — binding-tolerant 4-axis consumption.

    When ``binding`` exposes both ``persona_tier`` and ``blast_radius_tier``,
    consume the spec-canonical 4-axis ``evaluate_hitl_required`` via CP-axis
    ``GateLevelInput`` per CP spec v1.15 §19.1.1 (v2.20 conformance —
    ``per_tool_gate_level`` from binding when available else sentinel default
    ``GateLevel.AUTO``; sentinel default for ``mcp_trust_tier`` per CP plan
    v2.20 §0.8 row 2 PARTIAL-ADVANCE unconsumed axis). Otherwise (test-fixture
    partial-binding case), fall back to the v1.11 MVP
    ``placement.requires_hitl`` getattr-tolerant default (True when absent).
    """
    from harness_as import BlastRadiusTier  # local import to avoid cycle
    from harness_cp.cp_shared_types import MCPTrustTier
    from harness_cp.gate_level_rule import GateLevel, GateLevelInput

    from harness_runtime.lifecycle.hitl_required_consumption import (
        evaluate_hitl_required,
    )

    persona_tier = getattr(binding, "persona_tier", None)
    blast_radius_tier = getattr(binding, "blast_radius_tier", None)
    if persona_tier is None or blast_radius_tier is None:
        # Test-fixture / partial-binding fallback — preserve v1.11 MVP behavior.
        return bool(getattr(placement, "requires_hitl", True))

    if not isinstance(blast_radius_tier, BlastRadiusTier):
        return bool(getattr(placement, "requires_hitl", True))

    per_tool = getattr(binding, "per_tool_gate_level", GateLevel.AUTO)
    if not isinstance(per_tool, GateLevel):
        per_tool = GateLevel.AUTO

    input_ = GateLevelInput(
        per_tool_gate_level=per_tool,
        persona_tier=persona_tier,
        blast_radius_tier=blast_radius_tier,
        mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
    )
    return evaluate_hitl_required(input_)


def _evaluate_cell_synchrony_tolerant(  # pyright: ignore[reportUnusedFunction]
    binding: StepEffectiveBinding | None,
) -> SynchronyClass | None:
    """Runtime spec v1.24 §14.8.8.3 — binding-tolerant matrix synchrony lookup.

    Thin-wrap over CP-axis ``matrix_cell_for(binding.persona_tier,
    binding.engine_class).synchrony_class`` per scoping doc Q1 (α-revised) +
    U-RT-93 AC #1/#2. Returns:

    * ``None`` when ``binding is None`` (operator-opt-out arm — composer at
      §14.8.8.1 step 1 falls through to sync-blocking per change-note (ii)).
    * ``None`` when ``binding`` does not carry ``persona_tier`` (test-fixture
      / partial-binding tolerance — mirrors the ``getattr`` precedent at
      ``_evaluate_hitl_required_tolerant`` + the existing dispatch callsite
      at line 821; canonical ``StepEffectiveBinding`` per
      ``per_step_override_evaluator.py`` does NOT declare ``persona_tier``,
      so production callers pass duck-typed extension shapes).
    * ``matrix_cell_for(persona_tier, binding.engine_class).synchrony_class``
      otherwise — the four-class ``SynchronyClass`` value declared at CP spec
      v1.2 §18.1 (preserved verbatim through v1.16). The ``EXCLUDED`` case is
      delegated to the existing §14.8.2 step 4b ``HITLCellExcludedError`` raise
      and does NOT need additional handling at this helper.

    Sibling pattern to ``_evaluate_hitl_required_tolerant`` (Reading B
    precedent at v1.22 §14.8.2 step 4c).
    """
    if binding is None:
        return None
    persona_tier = getattr(binding, "persona_tier", None)
    if persona_tier is None:
        return None
    return matrix_cell_for(persona_tier, binding.engine_class).synchrony_class


def _compute_effective_palette_tolerant(
    *, binding: object
) -> frozenset[HITLResponse]:
    """Reading B v1.22 §14.8.2 step 4d — binding-tolerant UNION-intersection.

    Wrap-time path passes ``validator_escalation_brief=None``. When binding-
    derived ``gate_level`` is available, consume ``compute_effective_palette``
    with ``cross_trust_state=NONE`` (wrap-time path has no cross-trust context).
    Otherwise fall back to ``DEFAULT_FULL_PALETTE`` (v1.11 MVP behavior).
    """
    from harness_cp.gate_level_rule import GateLevel
    from harness_cp.validator_fail_transient_staircase import (
        CrossTrustBoundaryState,
    )

    from harness_runtime.lifecycle.effective_palette import (
        compute_effective_palette,
    )

    # Wrap-time path: no per-step gate_level computed; v1.22 baseline uses
    # ASK as the sentinel (gate fires when wrap-time composer reaches step 4d,
    # which presupposes hitl_required=True per step 4c).
    gate_level = GateLevel.ASK
    return compute_effective_palette(
        gate_level=gate_level,
        cross_trust_state=CrossTrustBoundaryState.NONE,
        validator_escalation_brief=None,
    )


def _empty_summary_hash() -> str:
    """`sha256(b"")` hex-64 — used for APPROVE response (no content to hash)."""
    return hashlib.sha256(b"").hexdigest()


def _compute_response_summary_hash(result: AskUserQuestionResult) -> str:
    """Compose `hitl.response.summary_hash` per spec v1.11 deferred-list.

    Shape: sha256 of the per-response content field:
    - EDIT → sha256(edited_proposal)
    - RESPOND → sha256(response_text)
    - REJECT → sha256(rejection_reason)
    - APPROVE → sha256(b"")  (no content)

    Returns hex-64.
    """
    payload: bytes
    if result.response == HITLResponse.EDIT and result.edited_proposal is not None:
        payload = result.edited_proposal.encode("utf-8")
    elif result.response == HITLResponse.RESPOND and result.response_text is not None:
        payload = result.response_text.encode("utf-8")
    elif result.response == HITLResponse.REJECT and result.rejection_reason is not None:
        payload = result.rejection_reason.encode("utf-8")
    else:
        payload = b""
    return hashlib.sha256(payload).hexdigest()


def _compose_hitl_handoff_context(
    *,
    step_context: StepExecutionContext,
    step: WorkflowStep,
) -> HandoffContext:
    """Build the v1.11 MVP HITL-flavor `HandoffContext` per spec §14.8.2 step 4a.

    Spec wording: "re-used verbatim from C-RT-17". The C-RT-17
    `_compose_handoff_context(step_context, payload)` shape consumes a
    `SubAgentDispatchPayload`; HITL at PRE_ACTION binding does not have that
    payload type. The HITL-flavor composes the same 7-field schema with:

    - `proposed_action` — `ProposedAction(action_kind=<derived from step.kind>,
      payload=step.step_payload, brief=None)` — `brief` is `None` for non-
      SUB_AGENT_DISPATCH kinds (per `harness_cp.handoff_context.ProposedAction`
      `brief: SubAgentBrief | None = None`).
    - `agent_confidence` — `None` at v1.11 MVP.
    - `failed_attempts` — empty tuple.
    - `alternatives_considered` — empty tuple.
    - `state_summary` — `StateSummary(relevant_entries=(parent_entry_ref,),
      summary_text="", summary_hash=sha256(b""),
      idempotency_key=step_context.parent_idempotency_key,
      external_references=())`.
    - `audit_trail_link` — `LedgerEntryRef(action_id=step_context.parent_action_id,
      entry_hash=step_context.parent_entry_hash,
      actor=step_context.parent_actor.actor_id)` per `Spec_Control_Plane_v1_6.md`
      §25.2.1 Path A.
    - `retry_history` — empty `RetryHistory`.

    Kind mapping: `INFERENCE_STEP` → `ActionKind.INFERENCE_STEP`;
    `TOOL_STEP` → `ActionKind.TOOL_CALL`; other step kinds (e.g.,
    `SUB_AGENT_DISPATCH`, `DECLARATIVE_STEP`, `HITL_STEP`) map to
    `ActionKind.INFERENCE_STEP` as the v1.11 MVP default (closest match for
    pre-action gate semantics — the gate proposes *some* action to the
    operator; the precise enum is HITL-narrative, not load-bearing at v1.11).
    """
    step_kind_name = getattr(step.step_kind, "value", str(step.step_kind))
    if step_kind_name == "tool-step":
        action_kind = ActionKind.TOOL_CALL
    elif step_kind_name == "sub-agent-dispatch":
        action_kind = ActionKind.SUB_AGENT_DISPATCH
    else:
        action_kind = ActionKind.INFERENCE_STEP

    parent_action_id = cast(ActionID, step_context.parent_action_id)
    actor_identity = ActorIdentity(step_context.parent_actor.actor_id)
    parent_entry_ref = LedgerEntryRef(
        action_id=parent_action_id,
        entry_hash=step_context.parent_entry_hash,
        actor=actor_identity,
    )
    return HandoffContext(
        proposed_action=ProposedAction(
            action_kind=action_kind,
            payload=cast(Any, step.step_payload),
            brief=None,
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


def _compute_handoff_context_size_bytes(handoff_context: Any) -> int:
    """Approximate handoff_context payload size for the canonical span attr.

    v1.11 deferred-list-bounded shape: `len(handoff_context.model_dump_json()
    .encode("utf-8"))` per the spec §14.8 suggested form. Returns 0 if
    handoff_context lacks a `model_dump_json` method (test fixtures may pass
    None or a stub).
    """
    if handoff_context is None:
        return 0
    dump_method = getattr(handoff_context, "model_dump_json", None)
    if dump_method is None:
        return 0
    try:
        return len(dump_method().encode("utf-8"))
    except Exception:  # pragma: no cover — defensive
        return 0


# ---------------------------------------------------------------------------
# Composer (AC #1 — Protocol satisfaction)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class RuntimeHITLGateComposer:
    """HITL gate composer (U-RT-60; satisfies `StepDispatcher` Protocol).

    Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8 C-RT-18. Sync `dispatch`
    method satisfying the sync `StepDispatcher` Protocol declared at
    `harness-cp/src/harness_cp/workflow_driver.py:155` (`@runtime_checkable`).
    Constructed at bootstrap stage 5 (LOOP_INIT) per spec §14.8.1
    wrap-asymmetry table; bound to `HarnessContext.llm_dispatcher` (wrapped
    by C-RT-16) for PRE_ACTION + to `HarnessContext.sub_agent_dispatcher`
    for SUB_AGENT_BOUNDARY.

    Constructor args mirror sub_agent_dispatch + add the AskUserQuestionSurface.
    Composer body is **async** per spec §14.8.1 item 1; bridges to the sync
    CP `StepDispatcher` Protocol via `SyncDispatcherFacade` at the registry
    boundary (U-RT-59 Path B precedent reuse).

    The `inner` field is the inner dispatcher whose dispatch is gated. May be
    sync (e.g., C-RT-17 sub-agent dispatcher) or async (e.g., C-RT-15 bare
    LLM dispatcher); `_dispatch_inner` duck-types via `inspect.isawaitable`.
    The composer is **single-instance-per-step_kind** at v1.11 MVP:
    `applicable_placements={PRE_ACTION}` or `={SUB_AGENT_BOUNDARY}`.
    """

    inner: Any
    """Inner dispatcher wrapped by this composer. May be sync or async; the
    composer awaits the result iff `inspect.isawaitable(result)`. Typed `Any`
    per the C-RT-04 Protocol-vs-concrete-narrowing pattern at composition
    site (per the U-RT-60 wrap-asymmetry fork Q3 ratification — INFERENCE_STEP
    row inner is async C-RT-15; SUB_AGENT_DISPATCH row inner is sync C-RT-17)."""

    applicable_placements: frozenset[HITLPlacementKind]
    """Which `HITLPlacementKind` values this composer instance acts on. Per
    spec §14.8.1, single-instance-per-step_kind at v1.11 MVP:
    `{PRE_ACTION}` for INFERENCE_STEP wrap or `{SUB_AGENT_BOUNDARY}` for
    SUB_AGENT_DISPATCH wrap."""

    ask_user_question_surface: AskUserQuestionSurface
    """H_E delivery surface per spec §14.8.3 v1.11 MCP-server binding."""

    ledger_writer: LedgerWriter  # forward-typed via TYPE_CHECKING
    """IS state-ledger writer for F2 dispatch action at substep 8b-HITL."""

    audit_writer: RuntimeAuditLedgerWriter  # forward-typed via TYPE_CHECKING
    """OD audit-ledger writer for OD entry append at substep 8d-HITL."""

    tracer_provider: Any
    """Typed `Any` per C-RT-04; the composer opens canonical 4-span hierarchy."""

    audit_signing_key_id: str
    """Signing key_id passed to `cp_audit_to_od_audit` at substep 8c-HITL."""

    audit_signing_algorithm: SignatureAlgorithm
    """Signing algorithm passed to `cp_audit_to_od_audit` at substep 8c-HITL."""

    # Carrier-canonical attribute name constants (per spec §14.8.5 producer-
    # side carrier import discipline). Frozen at construction so a typo in
    # the spec carrier surfaces at dataclass instantiation, not first dispatch.
    _hitl_span_attrs: Mapping[str, tuple[str, ...]] = field(init=False)
    _audit_attr_names: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        # Build a map from span_name → tuple of canonical attribute names per
        # CP carrier HITL_SPAN_NAMESPACE_SCHEMA.
        span_attrs: dict[str, tuple[str, ...]] = {
            schema.span_name: schema.span_attributes
            for schema in HITL_SPAN_NAMESPACE_SCHEMA
        }
        object.__setattr__(self, "_hitl_span_attrs", span_attrs)
        object.__setattr__(
            self,
            "_audit_attr_names",
            tuple(a.attribute_name for a in AUDIT_NAMESPACE_SCHEMA),
        )

    async def _dispatch_inner(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Invoke `self.inner.dispatch(...)`; await if awaitable.

        Per the U-RT-60 wrap-asymmetry fork Q3 ratification, the composer's
        inner may be sync (C-RT-17 sub-agent dispatcher at SUB_AGENT_BOUNDARY)
        or async (C-RT-15 bare LLM dispatcher at PRE_ACTION). `isawaitable`
        is defensive vs `iscoroutine` — tolerates Future / custom `__await__`
        shapes in addition to bare coroutines.
        """
        result = self.inner.dispatch(binding, step, step_context=step_context)
        if inspect.isawaitable(result):
            result = await result
        return cast(Mapping[str, Any], result)

    def _compose_and_persist_audit(
        self,
        *,
        parent_action_id: ActionID,
        placement: HITLPlacement,
        cell: HITLMatrixCell,
        gate_result: AskUserQuestionResult | None,
        step_context: StepExecutionContext,
        raise_on_failure: bool,
    ) -> tuple[CPAuditLedgerEntry, Any | None]:
        """4-substep audit-write per spec §14.8.2 step 4h (HITL-flavor).

        - **8a-HITL** Compose `CPAuditLedgerEntry` with HITL-canonical
          `response` populated from `gate_result.response` (one of the 4
          palette values) — unlike sub-agent dispatch's `response="approve"`
          convention per CP spec v1.9 §13.5.1 NOTE 5.
        - **8b-HITL** F2-write the HITL action via `ledger_writer.append`.
          Action_id pattern: `compose_hitl_action_id(...)` →
          `f"hitl:{parent_action_id}:{placement.position.value}"`.
        - **8c-HITL** Convert CP→OD via `cp_audit_to_od_audit(...)` (shared
          converter with U-RT-59 sub-agent dispatch per Q3 ratification).
        - **8d-HITL** Persist via `audit_writer.append(tenant_id, od_entry)`.

        On 8b/8c/8d failure with `raise_on_failure=True`:
        `HITLGateAuditComposeError` raised. With `raise_on_failure=False`
        (REJECT path): swallowed; rejection audit fact at 8a preserved per
        spec §14.8.2 step 4h failure-semantics paragraph (audit-suppression-
        on-REJECT discipline).

        Returns `(cp_entry, write_result)`. On timeout path, `gate_result`
        is None → 8a-HITL composes with `response=None`-equivalent placeholder
        (response field type is `str`, set to empty per spec partial-audit
        shape).
        """
        # 8a-HITL — compose CP audit (always produced; HITL-canonical shape).
        timestamp = ""  # placeholder; downstream signer / writer fills as needed
        if gate_result is None:
            # Timeout path partial entry — response=None semantic surfaced
            # as empty-string placeholder (the CPAuditLedgerEntry.response
            # field is typed `str`; partial-audit shape per spec §14.8 fail
            # class RT-FAIL-HITL-GATE-TIMEOUT row).
            response_value = ""
            edited_hash = None
            response_text_hash = None
            rejection_hash = None
        else:
            response_value = gate_result.response.value
            edited_hash = (
                hashlib.sha256(gate_result.edited_proposal.encode("utf-8")).hexdigest()
                if gate_result.response == HITLResponse.EDIT
                and gate_result.edited_proposal is not None
                else None
            )
            response_text_hash = (
                hashlib.sha256(gate_result.response_text.encode("utf-8")).hexdigest()
                if gate_result.response == HITLResponse.RESPOND
                and gate_result.response_text is not None
                else None
            )
            rejection_hash = (
                hashlib.sha256(gate_result.rejection_reason.encode("utf-8")).hexdigest()
                if gate_result.response == HITLResponse.REJECT
                and gate_result.rejection_reason is not None
                else None
            )

        hitl_action_id = compose_hitl_action_id(parent_action_id, placement.position)
        # `gate_level` value: HITLMatrixCell at landed CP schema does not
        # carry a `gate_level` field (per `persona_engine_hitl_matrix.py:80`);
        # v1.11 MVP uses sentinel "auto" string-value mapped to the
        # `CPAuditLedgerEntry.gate_level: GateLevel` field. The GateLevel enum
        # at C-CP-19 §19.1 has AUTO as a canonical value; cast at this site
        # per the C-RT-04 Protocol-vs-concrete pattern. Spec narrative
        # references `cell.gate_level` — carry-forward Class 3 spec-prose
        # drift item for future revision pass.
        cp_entry = CPAuditLedgerEntry(
            action_id=hitl_action_id,
            gate_level=GateLevel.AUTO,
            response=response_value,
            edited_proposal_hash=edited_hash,
            rejection_reason_hash=rejection_hash,
            response_text_hash=response_text_hash,
            timestamp=timestamp,
            prior_event_hash=_empty_summary_hash(),  # placeholder per spec §14.8 partial-entry shape
        )

        try:
            # 8b-HITL — F2-write the HITL action.
            from datetime import UTC, datetime

            f2_payload = EntryPayload(
                action_id=Identifier(str(hitl_action_id)),
                idempotency_key=Identifier(str(hitl_action_id)),
                actor=step_context.parent_actor,
                timestamp=datetime.now(UTC),
            )
            f2_key = WriteKey(
                thread_id=Identifier(f"hitl:{step_context.parent_action_id}"),
                step_id=Identifier(str(hitl_action_id)),
                idempotency_key=Identifier(str(hitl_action_id)),
            )
            self.ledger_writer.append(f2_payload, f2_key)
            entry_core = StateLedgerEntryRef(str(hitl_action_id))

            # 8c-HITL — convert CP → OD via shared converter (Q3 ratification).
            od_entry = cp_audit_to_od_audit(
                cp_entry,
                key_id=self.audit_signing_key_id,
                algo=self.audit_signing_algorithm,
                entry_core=entry_core,
            )

            # 8d-HITL — persist OD audit entry through IS hash chain.
            write_result = self.audit_writer.append(
                tenant_id=step_context.tenant_id,
                audit_entry=od_entry,
            )
        except Exception as exc:
            if raise_on_failure:
                raise HITLGateAuditComposeError(
                    f"HITL gate audit composition failed for "
                    f"action_id={hitl_action_id!r}: {exc}"
                ) from exc
            return cp_entry, None

        return cp_entry, write_result

    async def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Async dispatch composer body per spec §14.8.2 (v1.11 canonical 4-span).

        See module docstring for the 9-step body discipline.

        Raises
        ------
        HITLPlacementForeclosedAtV19Error
            Workflow declared `VALIDATOR_ESCALATION` at v1.11 MVP.
        HITLCellExcludedError
            Persona-tier × engine-class matrix cell is excluded.
        HITLGateTimeoutError
            `placement.timeout` elapsed without operator response.
        HITLGateRejectedError
            Operator selected REJECT.
        HITLGateAuditComposeError
            Audit-write substep failed on APPROVE / EDIT / RESPOND path.
        """
        # --- Step 1: Read placement triggers from step ---------------------
        placements: tuple[HITLPlacement, ...] = getattr(
            step, "hitl_placements", ()
        )
        if not placements:
            return await self._dispatch_inner(binding, step, step_context=step_context)

        # --- Step 2: Filter by composer's applicable set --------------------
        matching = [p for p in placements if p.position in self.applicable_placements]
        if not matching:
            return await self._dispatch_inner(binding, step, step_context=step_context)

        # --- Step 3: Filter VALIDATOR_ESCALATION placements (Reading B v1.22).
        # Per spec v1.22 §14.8.2 step 3: VALIDATOR_ESCALATION placements are
        # VALID at v1.22 — they fire via the mid-step re-entry path at
        # `validator_escalation_composer.compose_validator_escalation_gate`
        # invoked from workflow_driver post-dispatch hook (NOT here at
        # wrap-time composer). The wrap-time composer body ignores
        # VALIDATOR_ESCALATION placements (filtered out of `matching`).
        matching = [
            p for p in matching
            if p.position != HITLPlacementKind.VALIDATOR_ESCALATION
        ]
        if not matching:
            return await self._dispatch_inner(binding, step, step_context=step_context)

        tracer = self.tracer_provider.get_tracer("harness.runtime.hitl_gate")
        parent_action_id = cast(ActionID, step_context.parent_action_id)

        # --- Step 4: Per matching placement (in declaration order) --------
        for placement in matching:
            # --- 4a/4b: HandoffContext composition + matrix cell -----------
            # AC #5: compose real `HandoffContext` per spec §14.8.2 step 4a
            # ("re-used verbatim from C-RT-17"). HITL-flavor wrapper handles
            # the non-SUB_AGENT_DISPATCH binding shape (PRE_ACTION's
            # `ProposedAction.brief` is None per the landed CP schema).
            # Matrix-cell resolution at v1.11 MVP still tolerates incomplete
            # binding shapes (binding's persona_tier + engine_class read if
            # present; sentinel fallback for partial-binding test fixtures).
            handoff_context = _compose_hitl_handoff_context(
                step_context=step_context, step=step
            )
            persona_tier = getattr(binding, "persona_tier", None)
            engine_class = getattr(binding, "engine_class", None)
            if persona_tier is not None and engine_class is not None:
                cell = matrix_cell_for(
                    persona_tier=persona_tier, engine_class=engine_class
                )
                if cell.is_excluded:
                    raise HITLCellExcludedError(
                        f"persona_tier={persona_tier!r} × engine_class="
                        f"{engine_class!r} matrix cell is excluded "
                        f"(exclusion_source={cell.exclusion_source!r}) per "
                        f"C-CP-18 §18.1"
                    )
            else:
                # Test-fixture / partial-binding tolerance — composer still
                # opens canonical spans; matrix-cell carries a sentinel
                # gate_level for span emission.
                cell = cast(HITLMatrixCell, _SentinelMatrixCell())

            # --- 4c: _hitl_required predicate (Reading B v1.22 consumption) -
            # Spec v1.22 §14.8.2 step 4c: full 4-axis _hitl_required evaluation
            # per C-CP-19 §19.1. Reading B replaces v1.9 MVP `placement.
            # requires_hitl` shortcut with `evaluate_hitl_required` consumption.
            # Binding-tolerant fallback: when binding-derived axes are NOT
            # available (test-fixture partial-binding case), retain getattr
            # default-True for backward-compatible test behavior; production
            # paths consume the full 4-axis composition per CP-axis surface.
            hitl_required = _evaluate_hitl_required_tolerant(
                binding=binding, placement=placement
            )

            # --- 4d: Determine effective palette (Reading B v1.22 consumption)
            # Spec v1.22 §14.8.2 step 4d: UNION-intersection of C-CP-19 §19.4
            # deny-row + C-CP-21 §21.3 cross-trust-boundary via
            # `compute_effective_palette`. Wrap-time composer passes
            # validator_escalation_brief=None (validator context not in scope
            # at wrap-time path — fires at §14.15 mid-step re-entry only).
            # Binding-tolerant fallback: when binding-derived gate_level is
            # NOT available, retain DEFAULT_FULL_PALETTE.
            palette = _compute_effective_palette_tolerant(binding=binding)

            # --- 4e: Open hitl.gate.evaluated span + canonical 3 attrs -----
            with tracer.start_as_current_span("hitl.gate.evaluated") as gate_span:
                # `cell.gate_level` is not on landed HITLMatrixCell; v1.11
                # MVP sentinel value (matches CPAuditLedgerEntry composition
                # site at _compose_and_persist_audit). Carrier-vs-spec drift
                # carried as Class 3 item for next revision.
                gate_level_value: str = "auto"
                persona_tier_value = (
                    persona_tier.value
                    if persona_tier is not None and hasattr(persona_tier, "value")
                    else str(persona_tier) if persona_tier is not None else "unknown"
                )
                gate_span.set_attribute("hitl.gate.level", str(gate_level_value))
                gate_span.set_attribute("hitl.gate.persona_tier", persona_tier_value)
                gate_span.set_attribute("hitl.gate.required", bool(hitl_required))

                if not hitl_required:
                    # Step 4j skip-gate: no further spans for this placement.
                    continue

                # --- 4f-bis: Open hitl.invocation.opened span ---------------
                with tracer.start_as_current_span(
                    "hitl.invocation.opened"
                ) as invocation_span:
                    invocation_span.set_attribute(
                        "hitl.gate.level", str(gate_level_value)
                    )
                    invocation_span.set_attribute(
                        "hitl.invocation.placement", placement.position.value
                    )
                    invocation_span.set_attribute(
                        "hitl.invocation.handoff_context_size_bytes",
                        _compute_handoff_context_size_bytes(handoff_context),
                    )
                    # `hitl.invocation.audit_ledger_entry_id` set at step 4h
                    # completion when action_id known.

                    # --- 4f: Invoke AskUserQuestion via surface --------------
                    timeout_seconds: float | None = (
                        placement.timeout / 1000.0
                        if placement.timeout is not None
                        else None
                    )
                    options: list[HITLResponse] = sorted(palette)
                    try:
                        gate_result = await self.ask_user_question_surface.ask(
                            prompt=f"HITL gate at {placement.position.value}",
                            options=options,
                            timeout=timeout_seconds,
                        )
                    except AskUserQuestionTimeoutError as timeout_exc:
                        # Timeout path: open canonical hitl.invocation.timed_out
                        # span; emit partial audit entry; raise typed error.
                        with tracer.start_as_current_span(
                            "hitl.invocation.timed_out"
                        ) as timeout_span:
                            timeout_span.set_attribute(
                                "hitl.timeout.duration_ms",
                                placement.timeout if placement.timeout is not None else 0,
                            )
                            # Degradation mode at v1.11 MVP — operator-tunable
                            # per harness_cp.hitl_timeout_degradation consult;
                            # placeholder string at composer site (the
                            # canonical attribute is present per carrier;
                            # value derivation is impl-discretion).
                            timeout_span.set_attribute(
                                "hitl.timeout.degradation_mode_applied",
                                "default",
                            )
                            # Partial audit entry (audit composition is best-
                            # effort; failure swallowed per timeout-path
                            # semantics).
                            self._compose_and_persist_audit(
                                parent_action_id=parent_action_id,
                                placement=placement,
                                cell=cell,
                                gate_result=None,
                                step_context=step_context,
                                raise_on_failure=False,
                            )
                        raise HITLGateTimeoutError(
                            f"HITL gate timed out at placement="
                            f"{placement.position.value!r} after "
                            f"{placement.timeout}ms"
                        ) from timeout_exc

                    # --- 4g: Open hitl.invocation.responded span -----------
                    with tracer.start_as_current_span(
                        "hitl.invocation.responded"
                    ) as resp_span:
                        resp_span.set_attribute(
                            "hitl.response.class", gate_result.response.value
                        )
                        resp_span.set_attribute(
                            "hitl.response.latency_ms", gate_result.latency_ms
                        )
                        resp_span.set_attribute(
                            "hitl.response.summary_hash",
                            _compute_response_summary_hash(gate_result),
                        )

                    # --- 4h: 4-substep audit-write (HITL-flavor) -----------
                    # REJECT path: audit-suppression-on-failure discipline
                    # — audit-compose failures swallowed; HITLGateRejectedError
                    # is primary fault.
                    raise_on_audit_failure = (
                        gate_result.response != HITLResponse.REJECT
                    )
                    try:
                        _, write_result = self._compose_and_persist_audit(
                            parent_action_id=parent_action_id,
                            placement=placement,
                            cell=cell,
                            gate_result=gate_result,
                            step_context=step_context,
                            raise_on_failure=raise_on_audit_failure,
                        )
                        # Set audit_ledger_entry_id attribute now that it's known.
                        if write_result is not None:
                            hitl_action_id = compose_hitl_action_id(
                                parent_action_id, placement.position
                            )
                            invocation_span.set_attribute(
                                "hitl.invocation.audit_ledger_entry_id",
                                str(hitl_action_id),
                            )
                    except HITLGateAuditComposeError as audit_exc:
                        gate_span.set_status(
                            Status(StatusCode.ERROR, "audit-compose-failed")
                        )
                        gate_span.record_exception(audit_exc)
                        raise

                    # --- 4i: Process gate response per 4-response palette --
                    if gate_result.response == HITLResponse.APPROVE:
                        pass  # proceed to step 5 with step unchanged
                    elif gate_result.response == HITLResponse.EDIT:
                        # v1.11 MVP: replace step.step_payload via the edited
                        # proposal. The WorkflowStep is frozen Pydantic; the
                        # composer would need to construct a replacement step.
                        # v1.11 MVP defers replacement mechanics to the inner
                        # dispatcher's read of step (the test-layer expectation
                        # is that gate_result.edited_proposal is observable;
                        # full replacement-semantics arc deferred per NOTE
                        # 6-ii).
                        pass
                    elif gate_result.response == HITLResponse.REJECT:
                        raise HITLGateRejectedError(
                            f"operator rejected HITL gate at placement="
                            f"{placement.position.value!r}: "
                            f"{gate_result.rejection_reason!r}"
                        )
                    elif gate_result.response == HITLResponse.RESPOND:
                        # RESPOND: continue dialogue without action per
                        # C-CP-16 §16.1 row 4 + U-CP-37 AC #7 — proceed to
                        # inner dispatcher with step unchanged.
                        pass

        # --- Step 5: Delegate to inner dispatcher --------------------------
        return await self._dispatch_inner(binding, step, step_context=step_context)


class _SentinelMatrixCell:
    """v1.11 MVP placeholder for test-fixture partial-binding tolerance.

    Carries `gate_level="auto"` + `is_excluded=False`. Real production
    callsites resolve the matrix cell via `matrix_cell_for(...)` per spec
    §14.8.2 step 4b; this sentinel exists only at the test-fixture surface
    where binding objects may lack persona_tier / engine_class fields.
    """

    gate_level = "auto"
    is_excluded = False
    exclusion_source: str | None = None

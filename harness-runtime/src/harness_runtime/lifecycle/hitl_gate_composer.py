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
   4c. Compute `gate_level()` ONCE (U-RT-115/116/117): resolve the per-step
       blast radius (G1-blast), apply the §3.8 operator-policy in-`max()` floor
       overrides (G1-skip, solo-scoped), then derive `_hitl_required` (§19.4).
       A policy-caused skip emits a non-vacuous §20.1 auto-approve audit (AC-1).
   4d. Determine palette from the SAME `gate_level` (G2): ASK/AUTO → full
       palette; DENY → §19.4 deny-row narrowing (inert until G2c/O-CP-3).
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

import asyncio
import hashlib
import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from harness_as import BlastRadiusTier, GateLevel
from harness_core import PersonaTier
from harness_core.identity import ActionID
from harness_cp.audit_hitl_span_namespace import (
    AUDIT_NAMESPACE_SCHEMA,
    HITL_SPAN_NAMESPACE_SCHEMA,
)
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.gate_level_rule import GateLevel as CPGateLevel
from harness_cp.gate_level_rule import GateLevelComputation
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
from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
from harness_runtime.lifecycle.resume_context_holder import ResumeContextHolder
from harness_runtime.lifecycle.webhook_delivery_composer import (
    WebhookDeliveryComposer,
    WebhookDeliveryExhaustedError,
    WebhookDeliveryResult,
)

if TYPE_CHECKING:  # pragma: no cover — type-only imports
    from harness_cp.pause_resume_protocol import PauseResumeProtocol

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


def _policy_floor_overrides(
    policy: HITLAutoApprovePolicy,
    persona_tier: object,
    resolved_blast_radius: BlastRadiusTier | None,
) -> tuple[CPGateLevel | None, CPGateLevel | None]:
    """U-RT-116 (G1-skip; §3.8) — compute the in-`max()` floor overrides.

    Returns `(persona_floor_override, blast_floor_override)` — the two §19.1 floor
    cells the operator's `HITLAutoApprovePolicy` lowers to `AUTO` at step-4c
    (Reading C, in-`max()`). Both `None` ⇒ no override (the canonical table floor).

    **Solo-scoped (C10 safety is structural).** The knobs apply ONLY at
    `SOLO_DEVELOPER`: multi-tenant-compliance is structurally foreclosed (no
    override attempt to refuse) and team-binding is a registered follow-on
    (F-B3-1 §6). At non-solo tiers both overrides are `None`.

    **Named-cell foreclosure (AC-2).** The LOCAL_MUTATION knob lowers the blast
    floor ONLY when the step's resolved `blast_radius_tier == LOCAL_MUTATION` —
    NEVER for EXTERNAL_REVERSIBLE / EXTERNAL_IRREVERSIBLE (their blast floor stays
    `ASK` → hard-stop; the asymmetry is resolved structurally, not widened). The
    persona override is unconditional-on-blast (solo + knob): that is safe because
    the blast floor independently holds the EXTERNAL_* hard-stop in `max()` (a
    READ_ONLY step's blast floor is already `AUTO`, so lowering only the persona
    cell yields `max()=AUTO`; an EXTERNAL_* step's blast floor stays `ASK`, so the
    `max()` stays `ASK` regardless of the persona override).
    """
    if persona_tier is not PersonaTier.SOLO_DEVELOPER:
        return None, None
    persona_override = CPGateLevel.AUTO if policy.solo_persona_floor_auto else None
    blast_override = (
        CPGateLevel.AUTO
        if (
            policy.solo_local_mutation_floor_auto
            and resolved_blast_radius is BlastRadiusTier.LOCAL_MUTATION
        )
        else None
    )
    return persona_override, blast_override


def _compute_gate_decision(
    *,
    binding: object,
    resolved_blast_radius: BlastRadiusTier | None = None,
    persona_floor_override: CPGateLevel | None = None,
    blast_floor_override: CPGateLevel | None = None,
) -> GateLevelComputation | None:
    """U-RT-117 (G2; D-palette) — compute the `GateLevelComputation` ONCE at step-4c.

    The single `gate_level()` result is threaded to BOTH the `hitl_required` bool
    (§19.4) AND the step-4d `compute_effective_palette` (§14.8.2 step-4d) —
    replacing the prior double-computation (the bool computed `gate_level` then
    DISCARDED it; the palette re-hardcoded `ASK`). Reading B v1.22 §14.8.2 step-4c
    4-axis consumption per CP spec v1.15 §19.1.1 (`per_tool_gate_level` from binding
    else sentinel `AUTO`; sentinel `mcp_trust_tier` per CP plan v2.20 §0.8 row 2
    PARTIAL-ADVANCE unconsumed axis).

    Returns `None` for the **test-fixture / partial-binding** case (`persona_tier`
    or `blast_radius_tier` unavailable) — the caller then falls back to
    `placement.requires_hitl` (bool) + `DEFAULT_FULL_PALETTE` (palette) per the
    Reading-B v1.22 tolerance (preserved).

    U-RT-115 (G1-blast): `resolved_blast_radius` is the per-step blast radius
    resolved by the composer's `blast_radius_resolver` (design §3.2) — the REAL
    producer for the §19.1 `blast_radius_floor` axis, preferred over
    `getattr(binding, "blast_radius_tier")` (which is `None` in production — no
    per-step carrier). U-RT-116 (G1-skip; §3.8): the `*_floor_override` args are the
    operator-policy in-`max()` floor overrides (Reading C) — default `None` → the
    canonical §19.1 table floor (`per_tool` / `mcp_trust` never override-able).
    """
    from harness_cp.cp_shared_types import MCPTrustTier
    from harness_cp.gate_level_rule import GateLevel, GateLevelInput, gate_level

    persona_tier = getattr(binding, "persona_tier", None)
    blast_radius_tier: BlastRadiusTier | None = (
        resolved_blast_radius
        if resolved_blast_radius is not None
        else getattr(binding, "blast_radius_tier", None)
    )
    if persona_tier is None or not isinstance(blast_radius_tier, BlastRadiusTier):
        # Test-fixture / partial-binding fallback — caller uses requires_hitl +
        # DEFAULT_FULL_PALETTE (preserve v1.11 MVP behavior).
        return None

    per_tool = getattr(binding, "per_tool_gate_level", GateLevel.AUTO)
    if not isinstance(per_tool, GateLevel):
        per_tool = GateLevel.AUTO

    return gate_level(
        GateLevelInput(
            per_tool_gate_level=per_tool,
            persona_tier=persona_tier,
            blast_radius_tier=blast_radius_tier,
            mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
            persona_floor_override=persona_floor_override,
            blast_floor_override=blast_floor_override,
        )
    )


def _evaluate_cell_synchrony(
    binding: StepEffectiveBinding | None,
) -> SynchronyClass | None:
    """Runtime spec v1.24 §14.8.8.3 — matrix synchrony lookup.

    Thin-wrap over CP-axis ``matrix_cell_for(binding.persona_tier,
    binding.engine_class).synchrony_class`` per scoping doc Q1 (α-revised) +
    U-RT-93 AC #1/#2. Returns:

    * ``None`` when ``binding is None`` (operator-opt-out arm — composer at
      §14.8.8.1 step 1 falls through to sync-blocking per change-note (ii)).
    * ``matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class``
      otherwise — the four-class ``SynchronyClass`` value declared at CP spec
      v1.2 §18.1. The ``EXCLUDED`` case is delegated to the existing §14.8.2
      step 4b ``HITLCellExcludedError`` raise and does NOT need additional
      handling at this helper.

    Post-CP-v1.17 §6.5 — ``StepEffectiveBinding.persona_tier`` is now a
    required field on the canonical model (no getattr-tolerance needed; the
    pre-v1.17 fallback path returning ``None`` for bare bindings is retired
    per runtime plan v2.25 §7.1 ACs #5/#6/#7 absorption).
    """
    if binding is None:
        return None
    return matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class


# Alias preserved for downstream callers during the v2.25 transition; the
# `_tolerant` suffix is no longer accurate post-CP-v1.17 (persona_tier is
# required on StepEffectiveBinding). Direct callers should prefer the
# unsuffixed name. Removable at a follow-on cleanup arc.
_evaluate_cell_synchrony_tolerant = _evaluate_cell_synchrony


def _effective_palette_for(gate_level: CPGateLevel) -> frozenset[HITLResponse]:
    """U-RT-117 (G2; D-palette) §14.8.2 step 4d — palette from the REAL `gate_level`.

    Threads the step-4c `computed_gate_level` (NOT the prior hardcoded `ASK`
    sentinel) into `compute_effective_palette` with `cross_trust_state=NONE`
    (wrap-time path has no cross-trust context — §14.15 mid-step re-entry only)
    and `validator_escalation_brief=None`. For `ASK`/`AUTO` this is the full
    palette (unchanged wrap-time behavior); for `DENY` it is the §19.4 deny-row
    narrowing `{REJECT, RESPOND}` — behaviorally inert-but-harmless in production
    until the `per_tool_gate_level` producer (G2c / O-CP-3) lands, since
    `gate_level` never reaches `DENY` in production at HEAD.
    """
    from harness_cp.validator_fail_transient_staircase import (
        CrossTrustBoundaryState,
    )

    from harness_runtime.lifecycle.effective_palette import (
        compute_effective_palette,
    )

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

    procedural_tier_snapshot_resolver: Callable[[], Identifier]
    """R-003 producer-site lift — resolves the `procedural_tier_snapshot_ref`
    D-derivative sidecar for the F2 HITL action entry at 8b-HITL. Invoked
    zero-arg at the `EntryPayload(...)` construction. This is a workflow-context
    emission per IS spec v1.3 §C-IS-05 §5.1, so the sidecar MUST be populated (a
    `None` value would be a producer-site bug). Resolver closure built at
    bootstrap stage 5 via `make_procedural_tier_snapshot_resolver(ctx)`; mirrors
    the `RuntimeCpIsWiring.procedural_tier_snapshot_resolver` pattern for the 6
    §16.5 CP composers (`cp_is_wiring.py`). Required (no default) — placed
    before the v2.25 optional fields to satisfy dataclass field ordering."""

    # --- v2.25 §7.2 AC #12: 4 new fields for durable-async cell HITL ---------
    #
    # Per runtime plan v2.25 §7.2 AC #12 (Reading A path 1 absorption of fork
    # `class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md`).
    # All four fields default to None / fresh-instance so existing test
    # fixtures (constructed without these args) keep working unchanged; the
    # §14.8.8.1 step 0 OR-form precondition AND-arm at the composer body
    # treats `None` values as operator opt-out (sync-blocking fall-through).
    # Bootstrap stage-5 LOOP_INIT populates with real instances via the
    # binding chain landed at L9-quaterdecies (U-RT-96/97/98) +
    # L9-undecies (U-RT-87/88/89).
    pause_resume_protocol: PauseResumeProtocol | None = None
    """CP-canonical PauseResumeProtocol (C-CP-26 §26) bound at stage-5
    LOOP_INIT by `materialize_pause_resume_protocol_stage` per C-RT-24
    §14.14.3. `None` (default) → operator opt-out → §14.8.8.1 step 0 OR-form
    precondition AND-arm at `ctx.pause_resume_protocol is None` evaluates
    True → fall through to step 4f (sync-blocking)."""

    pause_requested_flag: asyncio.Event = field(default_factory=asyncio.Event)
    """Caller-signal flag set by composer body §14.8.8.1 step 5 to indicate
    a pause is pending; observed by workflow_driver per-step pre-entry
    pause-trigger detection branch per C-RT-24 §14.14.3."""

    webhook_delivery_composer: WebhookDeliveryComposer | None = None
    """C-RT-20 §14.10.1 WebhookDeliveryComposer bound at stage-5 LOOP_INIT by
    `materialize_webhook_delivery_composer_stage` per C-RT-26 §14.16.3.
    `None` (default) → operator opt-out → §14.8.8.1 step 0 OR-form
    precondition AND-arm at `ctx.webhook_delivery_composer is None` evaluates
    True → fall through to step 4f (sync-blocking). Non-`None` → durable-
    async branch at step 3 invokes `deliver_webhook(brief, idempotency_key)`."""

    resume_context_holder: ResumeContextHolder = field(
        default_factory=lambda: ResumeContextHolder()
    )
    """Runtime-internal sidecar carrier for one-shot ResumeContext delivery
    per v1.25 §14.8.8.9. Bound at stage-5 LOOP_INIT to an empty holder.
    Consumed at §14.8.8.5 resume-side gate-evaluation via
    `consume_and_clear()` atomic one-shot read-and-clear."""

    blast_radius_resolver: Callable[[WorkflowStep], BlastRadiusTier] | None = None
    """U-RT-115 (G1-blast) — per-step blast-radius resolver closure.

    Bound at bootstrap stage-5 LOOP_INIT via `make_step_blast_radius_resolver(ctx)`
    (the `procedural_tier_snapshot_resolver` closure precedent). At step-4c the
    composer invokes it to compute a REAL `blast_radius_tier` for the §19.1
    `gate_level()` `max()` (design §3.2 per-step-kind table) — instead of the
    `getattr(binding, "blast_radius_tier", None) → None` fall-back. `None`
    (default) → test-fixture / direct-construction path: fall back to the
    binding getattr per the Reading-B v1.22 tolerance (preserved)."""

    hitl_auto_approve_policy: HITLAutoApprovePolicy = field(
        default_factory=lambda: HITLAutoApprovePolicy()
    )
    """U-RT-116 (G1-skip; §3.8 / F-B3-1) — the operator's CP §19.5 floor-override
    policy, read from `config.hitl_auto_approve_policy` at stage-5 construction and
    held as composer instance state (no C-RT-04 `HarnessContext` field — the
    composer does not read `ctx.<field>` at dispatch, per F-B3-1 §3.1). At step-4c,
    when `binding.persona_tier == SOLO_DEVELOPER`, the matching §19.1 floor cell is
    lowered to `AUTO` per the policy BEFORE `gate_level()` composes the `max()`
    (Reading C, in-`max()`). Default `HITLAutoApprovePolicy()` = READ_ONLY auto-ON
    / LOCAL_MUTATION opt-in / EXTERNAL_* hard-stop at solo-developer."""

    # Carrier-canonical attribute name constants (per spec §14.8.5 producer-
    # side carrier import discipline). Frozen at construction so a typo in
    # the spec carrier surfaces at dataclass instantiation, not first dispatch.
    _hitl_span_attrs: Mapping[str, tuple[str, ...]] = field(init=False)
    _audit_attr_names: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        # Build a map from span_name → tuple of canonical attribute names per
        # CP carrier HITL_SPAN_NAMESPACE_SCHEMA.
        span_attrs: dict[str, tuple[str, ...]] = {
            schema.span_name: schema.span_attributes for schema in HITL_SPAN_NAMESPACE_SCHEMA
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
        auto_approved: bool = False,
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
        # Composer-site clock per CP spec v1.28 §16.5.6.X universal timestamp
        # fix (was `""` placeholder pre-v1.28). ISO-8601 per C-CP-16 §16.2
        # `timestamp: str` field docstring.
        timestamp = datetime.now(UTC).isoformat()
        if auto_approved:
            # U-RT-116 (AC-1): policy-caused auto-approval skip. NON-VACUOUS
            # entry — `response="approve"` (the canonical C-CP-16 §16.1 APPROVE
            # value, consistent with sub-agent dispatch's `response="approve"`
            # convention) + `gate_level=AUTO` records that no human was needed.
            # Explicitly NOT the timeout `response=""` partial shape (which would
            # read as a vacuous/null entry, failing AC-1's spirit).
            response_value = HITLResponse.APPROVE.value
            edited_hash = None
            response_text_hash = None
            rejection_hash = None
        elif gate_result is None:
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
            # placeholder per spec §14.8 partial-entry shape
            prior_event_hash=_empty_summary_hash(),
        )

        try:
            # 8b-HITL — F2-write the HITL action.
            f2_payload = EntryPayload(
                action_id=Identifier(str(hitl_action_id)),
                idempotency_key=Identifier(str(hitl_action_id)),
                actor=step_context.parent_actor,
                timestamp=datetime.now(UTC),
                procedural_tier_snapshot_ref=(self.procedural_tier_snapshot_resolver()),
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
                    f"HITL gate audit composition failed for action_id={hitl_action_id!r}: {exc}"
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
        # --- Step 0: Resume-side one-shot consume per §14.8.8.5 -----------
        # Runtime spec v1.25 §14.8.8.9.3 + v1.24 §14.8.8.5: when the workflow
        # resumes from a durable-async pause cycle, the driver-side resume
        # entry-point populated `ctx.resume_context_holder` via
        # `holder.set(resume_context)`. The composer at the resumed-step
        # gate-evaluation reads `consume_and_clear()` (atomic one-shot
        # read-and-clear enforcing §14.8.8.7 invariant 3). When the holder
        # carries a hitl_response, the operator has already responded — the
        # gate is logically resolved; skip the gate composition body and
        # proceed to the inner dispatcher per the auto-approve semantic of
        # the resumed gate (MVP integration shape per v2.24 AC #7; the
        # detailed audit-write integration of the resumed response into the
        # 4h substep flow is implementer-discretion deferred to a follow-on
        # arc per FM-2).
        resume_state = self.resume_context_holder.consume_and_clear()
        if resume_state is not None and resume_state.hitl_response is not None:
            return await self._dispatch_inner(binding, step, step_context=step_context)

        # --- Step 1: Read placement triggers from step ---------------------
        placements: tuple[HITLPlacement, ...] = getattr(step, "hitl_placements", ())
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
        matching = [p for p in matching if p.position != HITLPlacementKind.VALIDATOR_ESCALATION]
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
            handoff_context = _compose_hitl_handoff_context(step_context=step_context, step=step)
            persona_tier = getattr(binding, "persona_tier", None)
            engine_class = getattr(binding, "engine_class", None)
            if persona_tier is not None and engine_class is not None:
                cell = matrix_cell_for(persona_tier=persona_tier, engine_class=engine_class)
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

            # --- 4c: compute the gate-level ONCE (U-RT-117 G2; D-palette) ---
            # Spec v1.22 §14.8.2 step 4c: full 4-axis evaluation per C-CP-19 §19.1.
            # U-RT-115 (G1-blast): resolve the per-step blast radius (design §3.2)
            # via the stage-5-bound resolver; None for direct-construction /
            # test-fixture composers (the decision helper then falls back to the
            # binding getattr).
            resolved_blast_radius = (
                self.blast_radius_resolver(step) if self.blast_radius_resolver is not None else None
            )
            # U-RT-116 (G1-skip; §3.8): apply the operator-policy in-`max()` floor
            # overrides (Reading C) — solo-scoped, named-cell. `policy_applied`
            # records whether a floor was actually lowered (drives the AC-1
            # audit on the policy-caused skip path below).
            persona_floor_override, blast_floor_override = _policy_floor_overrides(
                self.hitl_auto_approve_policy, persona_tier, resolved_blast_radius
            )
            policy_applied = persona_floor_override is not None or blast_floor_override is not None
            # U-RT-117 (G2; D-palette): compute the GateLevelComputation ONCE and
            # thread `computed_gate_level` to BOTH the hitl_required bool (§19.4)
            # AND the step-4d palette (replacing the prior hardcoded ASK + the
            # redundant double-computation). `None` → test-fixture partial-binding
            # fallback: requires_hitl (bool) + DEFAULT_FULL_PALETTE (palette).
            gate_decision = _compute_gate_decision(
                binding=binding,
                resolved_blast_radius=resolved_blast_radius,
                persona_floor_override=persona_floor_override,
                blast_floor_override=blast_floor_override,
            )
            if gate_decision is not None:
                hitl_required = gate_decision.computed_gate_level in (
                    CPGateLevel.ASK,
                    CPGateLevel.DENY,
                )
            else:
                hitl_required = bool(getattr(placement, "requires_hitl", True))

            # --- 4d: effective palette from the SAME gate_level (U-RT-117 G2) ---
            # Spec v1.22 §14.8.2 step 4d. For ASK/AUTO → full palette (unchanged);
            # for DENY → §19.4 deny-row narrowing (inert-but-harmless until G2c).
            # Test-fixture partial-binding fallback → DEFAULT_FULL_PALETTE.
            palette = (
                _effective_palette_for(gate_decision.computed_gate_level)
                if gate_decision is not None
                else DEFAULT_FULL_PALETTE
            )

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
                    else str(persona_tier)
                    if persona_tier is not None
                    else "unknown"
                )
                gate_span.set_attribute("hitl.gate.level", str(gate_level_value))
                gate_span.set_attribute("hitl.gate.persona_tier", persona_tier_value)
                gate_span.set_attribute("hitl.gate.required", bool(hitl_required))

                if not hitl_required:
                    # U-RT-116 (AC-1 C10 audit-wiring guard): when the operator
                    # policy lowered a floor and that caused the gate to skip,
                    # CP §19.5 line 1698 mandates *"each override emits audit-
                    # ledger entry per C-CP-20 §20.1."* Emit a NON-VACUOUS §20.1
                    # entry recording the auto-approval (response="approve",
                    # gate_level=AUTO) BEFORE the skip — NOT the timeout partial
                    # shape (response=""). The skip MUST NOT go live un-audited;
                    # `raise_on_failure=True` mirrors the gate-fired APPROVE
                    # discipline (a non-REJECT audit failure is a fault).
                    # `gate_decision is not None` ensures the skip was genuinely
                    # policy-caused (a real `gate_level()` AUTO) — not the
                    # test-fixture `requires_hitl=False` fallback (which would
                    # mis-attribute an auto-approve audit; benign over-audit
                    # foreclosed per adversarial F2-01 / advisor pre-done #3).
                    if gate_decision is not None and policy_applied:
                        self._compose_and_persist_audit(
                            parent_action_id=parent_action_id,
                            placement=placement,
                            cell=cell,
                            gate_result=None,
                            step_context=step_context,
                            raise_on_failure=True,
                            auto_approved=True,
                        )
                    # Step 4j skip-gate: no further spans for this placement.
                    continue

                # --- 4-bis: Durable-async cell branch (v1.24 §14.8.8.1) -----
                # Per runtime spec v1.26 §14.8.8.1 step 0 OR-form precondition
                # (canonical-reading amendment) + §14.8.2 step 4-bis insertion:
                # if joint binding (pause_resume_protocol + webhook_delivery_composer)
                # is satisfied AND the matrix cell synchrony is DURABLE_ASYNC,
                # fire the §14.8.8.1 6-step durable-async composer body.
                # Otherwise (any precondition False OR SYNC_BLOCKING), fall
                # through to the existing step 4f sync-blocking path.
                #
                # Composer-body binding-tolerant access: `binding: Any` per the
                # CP StepDispatcher Protocol; test fixtures pass bare `object()`
                # without persona_tier/engine_class. Production callers post-
                # CP-v1.17 land canonical StepEffectiveBinding. The defensive
                # getattr at lines 871-872 above resolved persona_tier+engine_class
                # for the EXCLUDED check; here we reuse `cell.synchrony_class`
                # (resolved at lines 873-875 to a real cell OR sentinel).
                _synchrony_attr = getattr(cell, "synchrony_class", None)
                joint_binding_present = (
                    self.pause_resume_protocol is not None
                    and self.webhook_delivery_composer is not None
                )
                if joint_binding_present and _synchrony_attr is SynchronyClass.DURABLE_ASYNC:
                    # §14.8.8.1 step 1: compose HITLEscalationBrief.
                    # fail_class=None per CP spec v1.18 §25.2.X Optional
                    # widening + fail_detail_hash=None per CP spec v1.19
                    # §25.2.Y Optional widening (pause-trigger construction
                    # site is not a validator failure — no validator outcome
                    # at this site).
                    durable_brief = HITLEscalationBrief(
                        parent_step_id=str(step.step_id),
                        parent_action_id=str(parent_action_id),
                        fail_class=None,
                        fail_detail_hash=None,
                        escalation_reason="durable_async_cell_synchrony",
                        proposed_response_palette=frozenset(sorted(palette)),
                    )
                    # §14.8.8.1 step 2: compose idempotency_key per
                    # `compose_hitl_action_id` shape (mirrors §14.7.2 step 8b
                    # convention; hitl: prefix is the source discriminator).
                    idempotency_key = str(
                        compose_hitl_action_id(parent_action_id, placement.position)
                    )
                    # §14.8.8.1 step 3 + step 4: deliver_webhook_for_brief; on
                    # exhausted the typed exception propagates (driver-side
                    # handler OR caller-side handler decides). Uses the
                    # spec-canonical brief surface per runtime spec v1.34
                    # §14.10.1 Reading (H) absorption + fork doc §0.1 at
                    # `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md`
                    # (operator-ratified 2026-05-28). The brief surface
                    # projects to WebhookPayload via webhook_brief_adapter +
                    # invokes the underlying raw 3-arg deliver_webhook.
                    # Local capture — `joint_binding_present` (line 968) already
                    # verified non-None, but pyright cannot narrow an instance
                    # attribute across the captured bool + await boundary.
                    composer = self.webhook_delivery_composer
                    assert composer is not None
                    try:
                        delivery_result = await composer.deliver_webhook_for_brief(
                            durable_brief, idempotency_key
                        )
                    except WebhookDeliveryExhaustedError:
                        # Step 4: webhook delivery exhausted. NO flag-set;
                        # NO signal raise. Per spec §14.8.8.1 step 4 the
                        # composer surfaces the failure as a fault — re-raise
                        # for the driver-side error path.
                        raise
                    # §14.8.8.1 step 5: set pause_requested_flag (caller-signal
                    # observed by workflow_driver per-step pre-entry detection
                    # per C-RT-24 §14.14.3).
                    self.pause_requested_flag.set()
                    # §14.8.8.1 step 6: raise HITLPauseRequestedSignal (typed
                    # control-flow exception per §14.8.8.2 — BaseException
                    # subclass; only explicit catch consumes it).
                    raise HITLPauseRequestedSignal(
                        brief=durable_brief,
                        delivery_result=delivery_result,
                    )
                # End of step 4-bis. Fall through to step 4f sync-blocking.

                # --- 4f-bis: Open hitl.invocation.opened span ---------------
                with tracer.start_as_current_span("hitl.invocation.opened") as invocation_span:
                    invocation_span.set_attribute("hitl.gate.level", str(gate_level_value))
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
                        placement.timeout / 1000.0 if placement.timeout is not None else None
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
                    with tracer.start_as_current_span("hitl.invocation.responded") as resp_span:
                        resp_span.set_attribute("hitl.response.class", gate_result.response.value)
                        resp_span.set_attribute("hitl.response.latency_ms", gate_result.latency_ms)
                        resp_span.set_attribute(
                            "hitl.response.summary_hash",
                            _compute_response_summary_hash(gate_result),
                        )

                    # --- 4h: 4-substep audit-write (HITL-flavor) -----------
                    # REJECT path: audit-suppression-on-failure discipline
                    # — audit-compose failures swallowed; HITLGateRejectedError
                    # is primary fault.
                    raise_on_audit_failure = gate_result.response != HITLResponse.REJECT
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
                        gate_span.set_status(Status(StatusCode.ERROR, "audit-compose-failed"))
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

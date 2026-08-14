"""Adapter projecting `HITLEscalationBrief` → `WebhookPayload`.

Resolves the runtime spec v1.34 §14.10.1 + §14.8.8.1 step 3 carrier-consumer
signature divergence per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md`
Reading (H) operator-ratified 2026-05-28.

Background: the spec contract at §14.10.1 + §14.8.8.1 step 3 declares the
canonical 2-arg `deliver_webhook(brief, idempotency_key)` surface against
`HITLEscalationBrief` (CP-axis); production carrier at
`webhook_delivery_composer.py:166-171` declares a 3-arg surface against
`WebhookConfig` + `WebhookPayload`. The two abstractions are not signature-
compatible — Reading (H) ratifies BOTH surfaces side-by-side and introduces
this projector as the boundary adapter.

Public API:
    `project_brief_to_payload(brief, idempotency_key) -> WebhookPayload`

The projection is a faithful field-mapping (no field invented):
- `approval_id` ← `brief.parent_action_id` (semantic match per
  C-CP-21 §21.8 "approval-id" surface; the parent action ID names the
  workflow step seeking approval).
- `idempotency_key` ← per-call `idempotency_key` param (canonical pass-through;
  the brief itself does not carry an idempotency_key field, by design — it
  is composed by the caller per `compose_hitl_action_id(parent_action_id,
  placement_position)` shape at `hitl_gate_composer.py:994-996`).
- `gate_evaluation_ref` ← `brief.parent_action_id` (the ledger join key per
  C-CP-21 §21.8; the gate's parent action ID is also its evaluation reference
  — the action ID composes from the same ledger-entry hash chain).
- `payload_body` ← serialized brief fields (`escalation_reason`, `fail_class`,
  `fail_detail_hash`, `proposed_response_palette`, `parent_step_id`) — opaque
  per §21.8 deferred clause; provides the operator-facing context for the
  HITL approval decision.

Ratified 2026-05-28 per fork doc §0.1 Reading (H) + §0.2 recommendation.
"""

from __future__ import annotations

from typing import Any

from harness_core import EntryID
from harness_cp.hitl_timeout_degradation import WebhookPayload
from harness_cp.pause_state_projection import PauseLocationVariant
from harness_cp.validator_framework_types import HITLEscalationBrief
from harness_is.state_ledger_entry_schema import Identifier


def project_brief_to_payload(
    brief: HITLEscalationBrief,
    idempotency_key: str,
    *,
    branch_context: str | None = None,
    resolvability: PauseLocationVariant | None = None,
    resolvability_note: str | None = None,
) -> WebhookPayload:
    """Project a `HITLEscalationBrief` to a `WebhookPayload` for outbound HTTP
    delivery via `WebhookDeliveryComposer.deliver_webhook(...)` (the raw 3-arg
    surface).

    Per fork doc §0.1 Reading (H): this adapter mediates between the
    spec-canonical brief surface (CP-axis validator-escalation context) and
    the production-canonical webhook payload surface (CP-axis HTTP-wire
    format).

    Parameters
    ----------
    brief
        The HITL escalation brief from validator framework escalation
        (CP spec v1.18 §25.2 `HITLEscalationBrief`).
    idempotency_key
        The per-call idempotency key composed by the caller per
        `compose_hitl_action_id(parent_action_id, placement_position)` shape.
    branch_context
        U-RT-155 / `B-71` (CP spec v1.119 §0.6) — the escalating branch's ordinal
        **as display-only PROSE**, under an explicit no-format commitment. This is
        §0.5's ONE scoped carve-out to the leak bar and it is exactly as narrow as
        the council scoped it: the ordinal MUST NOT appear as a typed or parseable
        field, on any other key, or on any exported span attribute. Not precedent
        for structured ordinal export.
    resolvability
        The resolution **CHANNEL**, typed as the CLOSED `PauseLocationVariant`
        vocabulary (`Spec_Control_Plane_v1_112.md` §2.1) the pause view already
        assigns — so the webhook and the pause view can never become two
        authorities over one concept. **Never the outcome**: resolvability is
        time-VARYING (a branch not resolvable while two gate-owners are unaddressed
        becomes resolvable the moment its peer is answered), and a value minted at
        escalation time cannot track that. A static `held-for-sole-resolution` stamp
        would tell the operator not to reply to the one request whose reply resolves
        the run — self-fulfillingly, since obeying it withholds that very action.
    resolvability_note
        Prose stating the sole-member RULE and routing the operator. **Promises no
        live status**: the pause view's projection is a function of the snapshot
        alone and the durable-pause read is ratified as NOT a liveness claim, so the
        note names the rule and the view, never a verdict.

    Returns
    -------
    WebhookPayload
        The projected payload with `approval_id` / `idempotency_key` /
        `gate_evaluation_ref` / `payload_body` fields populated per the
        field-mapping enumerated at the module docstring.
    """
    payload_body: dict[str, Any] = {
        "escalation_reason": brief.escalation_reason,
        "parent_step_id": brief.parent_step_id,
        "fail_class": brief.fail_class.value if brief.fail_class is not None else None,
        "fail_detail_hash": brief.fail_detail_hash,
        "proposed_response_palette": sorted(
            response.value for response in brief.proposed_response_palette
        ),
    }
    # U-RT-155 / `B-71` (Runtime spec v1.121 site 3; CP spec v1.119 §0.6) — the FOUR
    # additive keys. This adapter is an explicit field-by-field mapper, so a field
    # present on the brief and absent HERE silently never reaches the wire; that gap
    # is precisely what out-of-family review found in the spec leg's first draft.
    #
    # Each is emitted only when its source value is present, so the linear/validator
    # population's body is byte-identical to pre-arc (§0.12) — an unset Optional adds
    # no key, which is exactly the property this mapper shape already guarantees.
    #
    # `escalation_instance_id` is the **BARE** token, not the composed key, and that
    # distinction is the whole correlation loop: the `Idempotency-Key` carries
    # `hitl:{parent_action_id}:{position}:{token}` while the pause-view projection
    # carries the bare token, and §0.4(1) permits EQUALITY AND NOTHING ELSE — no
    # consumer may parse, split or derive. Without this key the two surfaces carry
    # values that are related but NOT COMPARABLE.
    if brief.escalation_instance_id is not None:
        payload_body["escalation_instance_id"] = brief.escalation_instance_id
    if branch_context is not None:
        payload_body["branch_context"] = branch_context
    if resolvability is not None:
        # Serialize the ENUM's value, never a caller-supplied string. Typing this
        # parameter `str` made an invalid wire state representable and admitted a
        # SECOND classification authority beside the pause view — the exact thing
        # §0.6's "no new vocabulary is minted" clause forecloses (out-of-family
        # review round 2, [P2]).
        payload_body["resolvability"] = resolvability.value
    if resolvability_note is not None:
        payload_body["resolvability_note"] = resolvability_note
    return WebhookPayload(
        approval_id=brief.parent_action_id,
        idempotency_key=Identifier(idempotency_key),
        gate_evaluation_ref=EntryID(brief.parent_action_id),
        payload_body=payload_body,
    )

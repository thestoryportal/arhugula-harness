"""HITL timeout-degradation + webhook delivery semantics — U-CP-52.

Implements C-CP-21 §21.6 (HITL timeout-degradation) + C-CP-18 §18.5 / C-CP-21
§21.8 (webhook delivery semantics).

Declares the `TimeoutDegradationKind` enum, the `TimeoutDegradationPolicy`
record + `TIMEOUT_DEGRADATION_TABLE`, the `WebhookConfig` / `WebhookPayload`
records (faithful factor-outs per Implementation Plan v2.9 §0.3), the
`WebhookDeliveryEvent` record + `WebhookDeliveryOutcome` enum, and the two
functions `on_hitl_timeout` / `deliver_webhook`.

`HITLInvocation` is consumed cross-cluster from U-CP-17 via the pre-existing
`[U-CP-17]` edge. `WebhookConfig` / `WebhookPayload` are the v2.9 §0.3 faithful
factor-outs of the C-CP-21 §21.8 idempotency-keyed webhook signal-delivery
contract; `payload_body` is opaque (`Mapping[str, Any]`) per the §21.8 deferred
clause. Webhook retry mechanics are delegated to the harness retry primitive
(hand-rolled — NO tenacity/pybreaker per CLAUDE.md §3.2).

Authority: Implementation_Plan_Control_Plane_v2_9.md §2A U-CP-52 (REVISED v2.9
— `WebhookConfig` / `WebhookPayload` specified); Spec_Control_Plane_v1_2.md §21
C-CP-21 §21.6/§21.8 + §18 C-CP-18 §18.5; ADR-D5 v1.3.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from harness_core import EntryID, PersonaTier
from harness_is.state_ledger_entry_schema import Identifier
from pydantic import BaseModel, ConfigDict

from harness_cp.workload_binding_engine_class_selection import HITLInvocation

#: `Duration` — millisecond integer (C-CP-21 §21.3 vocabulary).
type Duration = int


class TimeoutDegradationKind(StrEnum):
    """The 3 HITL timeout-degradation kinds (C-CP-21 §21.6)."""

    CONTINUE_AS_REJECT = "continue-as-reject"
    """Treat the timeout as a REJECT response."""

    ESCALATE_TO_REVIEW_BOARD = "escalate-to-review-board"
    """Raise the gate level; a second invocation."""

    ABORT_WORKFLOW = "abort-workflow"
    """Terminal — no further attempts."""


class TimeoutDegradationPolicy(BaseModel):
    """One per-persona-tier timeout-degradation policy (C-CP-21 §21.6)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    persona_tier: PersonaTier
    default_kind: TimeoutDegradationKind
    override_permitted: bool
    audit_required: bool
    """Always true."""


TIMEOUT_DEGRADATION_TABLE: tuple[TimeoutDegradationPolicy, ...] = (
    TimeoutDegradationPolicy(
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        default_kind=TimeoutDegradationKind.CONTINUE_AS_REJECT,
        override_permitted=True,
        audit_required=True,
    ),
    TimeoutDegradationPolicy(
        persona_tier=PersonaTier.TEAM_BINDING,
        default_kind=TimeoutDegradationKind.ESCALATE_TO_REVIEW_BOARD,
        override_permitted=True,
        audit_required=True,
    ),
    TimeoutDegradationPolicy(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        default_kind=TimeoutDegradationKind.ABORT_WORKFLOW,
        override_permitted=False,
        audit_required=True,
    ),
)
"""The 3 per-persona-tier timeout-degradation policies, C-CP-21 §21.6 verbatim.
SOLO_DEVELOPER -> CONTINUE_AS_REJECT (override permitted); TEAM_BINDING ->
ESCALATE_TO_REVIEW_BOARD (override permitted); MULTI_TENANT_COMPLIANCE ->
ABORT_WORKFLOW (override prohibited — terminal)."""


class WebhookConfig(BaseModel):
    """A per-webhook delivery descriptor (C-CP-18 §18.5 / C-CP-21 §21.8).

    Faithful factor-out per plan v2.9 §0.3 — the webhook-ingress contract for
    durable-async cells. No field invented.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    webhook_id: str
    endpoint_url: str
    timeout: Duration
    """Per the C-CP-17 §17.1.1 `hitl_gate` timeout."""

    degradation_mode: str
    """∈ {fail-closed, escalate-secondary-channel} per the C-CP-21 §21.8
    timeout-degradation table."""


class WebhookPayload(BaseModel):
    """An inbound webhook-signal record (C-CP-21 §21.8).

    Faithful factor-out per plan v2.9 §0.3 — keyed by the §21.8
    `(approval_id, idempotency_key)` pair; `payload_body` is opaque per the
    §21.8 deferred clause. No field invented.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_id: str
    idempotency_key: Identifier
    """§21.8 idempotency-keyed signal delivery."""

    gate_evaluation_ref: EntryID
    """Ledger join key."""

    payload_body: Mapping[str, Any]
    """Opaque — §21.8 defers idempotency-key extraction from inbound payload."""


class WebhookDeliveryOutcome(StrEnum):
    """The outcome of a webhook delivery attempt (C-CP-21 §21.8)."""

    DELIVERED = "delivered"
    RETRY_PENDING = "retry-pending"
    EXHAUSTED_AFTER_RETRIES = "exhausted-after-retries"


class WebhookDeliveryEvent(BaseModel):
    """A webhook-delivery event record (C-CP-21 §21.8)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    webhook_id: str
    workflow_id: str
    gate_evaluation_ref: EntryID
    payload_hash: str
    """`sha256(canonicalize(payload))`."""

    delivery_attempts: int
    delivery_outcome: WebhookDeliveryOutcome


def on_hitl_timeout(
    invocation: HITLInvocation, persona_tier: PersonaTier
) -> TimeoutDegradationKind:
    """Resolve the timeout-degradation kind for a timed-out HITL invocation.

    Per C-CP-21 §21.6: the degradation kind is the `TIMEOUT_DEGRADATION_TABLE`
    `default_kind` for `persona_tier`. The timeout emits an audit entry per the
    U-CP-46 `audit.*` attributes (the F2 entry written via U-IS-07 + U-IS-11);
    `on_hitl_timeout` consumes a `HITLInvocation` (U-CP-17, cross-cluster
    `[U-CP-17]`). The concrete audit-emission composes against the IS substrate
    at integration time.
    """
    _ = invocation
    policy = next(p for p in TIMEOUT_DEGRADATION_TABLE if p.persona_tier is persona_tier)
    return policy.default_kind


def deliver_webhook(webhook: WebhookConfig, payload: WebhookPayload) -> WebhookDeliveryEvent:
    """Deliver a webhook signal (C-CP-18 §18.5 / C-CP-21 §21.8).

    Webhook delivery is **idempotent** — duplicate delivery on retry does not
    produce duplicate workflow side effects (receiver-side dedup by the
    `gate_evaluation_ref` join). Retry mechanics delegate to the harness retry
    primitive (hand-rolled per CLAUDE.md §3.2). This is the delivery-semantics
    surface; the concrete HTTP delivery + retry loop composes at integration
    time. `payload_hash = sha256(canonicalize(payload))` per the §21.8
    signature discipline.
    """
    _ = (webhook, payload)
    raise NotImplementedError(
        "deliver_webhook composes the HTTP delivery + hand-rolled retry loop; "
        "the CP plan U-CP-52 unit declares the webhook delivery-semantics "
        "surface (C-CP-18 §18.5 / C-CP-21 §21.8)."
    )

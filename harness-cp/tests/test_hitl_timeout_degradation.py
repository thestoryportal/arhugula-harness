"""Tests for U-CP-52 — HITL timeout-degradation + webhook delivery (C-CP-21).

Lands the v2.9-revised body. Acceptance-criterion coverage:
  #1 TimeoutDegradationKind 3    -> test_timeout_degradation_three_kinds
  #2 degradation table 3 entries -> test_timeout_degradation_table_three_entries
  #3 on_hitl_timeout per tier    -> test_on_hitl_timeout_per_persona_tier
  #6 delivery outcome 3 values   -> test_webhook_delivery_outcome_three
  #8 WebhookConfig 4 fields      -> test_webhook_config_four_fields_cp_21_8
  #8 WebhookPayload 4 fields     -> test_webhook_payload_four_fields_cp_21_8
                                    test_webhook_payload_body_opaque_no_invented_fields
  #4 retry delegated             -> test_deliver_webhook_surface
"""

from __future__ import annotations

import pytest
from harness_core import EntryID, PersonaTier
from harness_is.state_ledger_entry_schema import Identifier

from harness_cp.handoff_context import (
    ActionKind,
    HandoffContext,
    LedgerEntryRef,
    ProposedAction,
    RetryHistory,
    StateSummary,
)
from harness_cp.cp_shared_types import ActorIdentity
from harness_core import ActionID
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.hitl_timeout_degradation import (
    TIMEOUT_DEGRADATION_TABLE,
    TimeoutDegradationKind,
    WebhookConfig,
    WebhookDeliveryOutcome,
    WebhookPayload,
    deliver_webhook,
    on_hitl_timeout,
)
from harness_cp.workload_binding_engine_class_selection import HITLInvocation


def _invocation() -> HITLInvocation:
    ctx = HandoffContext(
        proposed_action=ProposedAction(
            action_kind=ActionKind.INFERENCE_STEP, payload={}, brief=None
        ),
        agent_confidence=None,
        failed_attempts=(),
        alternatives_considered=(),
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="s",
            summary_hash="0" * 64,
            idempotency_key=Identifier("k"),
            external_references=(),
        ),
        audit_trail_link=LedgerEntryRef(
            action_id=ActionID("a0"), entry_hash="0" * 64, actor=ActorIdentity("op")
        ),
        retry_history=RetryHistory(attempts=(), retry_count=0),
    )
    return HITLInvocation(
        invocation_id="inv-0",
        placement="pre-action",
        handoff_context=ctx,
        response_palette=frozenset(HITLResponse),
        timeout=None,
        cascade_policy="pause",
        opened_at="2026-05-16T00:00:00Z",
    )


def test_timeout_degradation_three_kinds() -> None:
    """#1 — TimeoutDegradationKind declares exactly three values per §21.6."""
    assert len(TimeoutDegradationKind) == 3


def test_timeout_degradation_table_three_entries() -> None:
    """#2 — TIMEOUT_DEGRADATION_TABLE declares the 3 §21.6 per-tier rows."""
    assert len(TIMEOUT_DEGRADATION_TABLE) == 3
    by_tier = {p.persona_tier: p for p in TIMEOUT_DEGRADATION_TABLE}
    assert (
        by_tier[PersonaTier.SOLO_DEVELOPER].default_kind
        is TimeoutDegradationKind.CONTINUE_AS_REJECT
    )
    assert by_tier[PersonaTier.SOLO_DEVELOPER].override_permitted is True
    assert (
        by_tier[PersonaTier.TEAM_BINDING].default_kind
        is TimeoutDegradationKind.ESCALATE_TO_REVIEW_BOARD
    )
    mtc = by_tier[PersonaTier.MULTI_TENANT_COMPLIANCE]
    assert mtc.default_kind is TimeoutDegradationKind.ABORT_WORKFLOW
    assert mtc.override_permitted is False
    assert all(p.audit_required for p in TIMEOUT_DEGRADATION_TABLE)


def test_on_hitl_timeout_per_persona_tier() -> None:
    """#3 — on_hitl_timeout returns the per-tier degradation kind."""
    inv = _invocation()
    assert (
        on_hitl_timeout(inv, PersonaTier.SOLO_DEVELOPER)
        is TimeoutDegradationKind.CONTINUE_AS_REJECT
    )
    assert (
        on_hitl_timeout(inv, PersonaTier.MULTI_TENANT_COMPLIANCE)
        is TimeoutDegradationKind.ABORT_WORKFLOW
    )


def test_webhook_delivery_outcome_three() -> None:
    """#6 — WebhookDeliveryOutcome declares exactly three values."""
    assert len(WebhookDeliveryOutcome) == 3
    assert {o.value for o in WebhookDeliveryOutcome} == {
        "delivered",
        "retry-pending",
        "exhausted-after-retries",
    }


def test_webhook_config_four_fields_cp_21_8() -> None:
    """#8 — WebhookConfig declares exactly four fields."""
    assert set(WebhookConfig.model_fields) == {
        "webhook_id",
        "endpoint_url",
        "timeout",
        "degradation_mode",
    }


def test_webhook_payload_four_fields_cp_21_8() -> None:
    """#8 — WebhookPayload declares exactly four fields."""
    assert set(WebhookPayload.model_fields) == {
        "approval_id",
        "idempotency_key",
        "gate_evaluation_ref",
        "payload_body",
    }


def test_webhook_payload_body_opaque_no_invented_fields() -> None:
    """#8 — WebhookPayload.payload_body is opaque (any mapping shape)."""
    payload = WebhookPayload(
        approval_id="ap-0",
        idempotency_key=Identifier("k0"),
        gate_evaluation_ref=EntryID("e0"),
        payload_body={"arbitrary": "shape", "n": 1},
    )
    assert payload.payload_body["n"] == 1
    empty = WebhookPayload(
        approval_id="ap-1",
        idempotency_key=Identifier("k1"),
        gate_evaluation_ref=EntryID("e1"),
        payload_body={},
    )
    assert empty.payload_body == {}


def test_deliver_webhook_surface() -> None:
    """#4 — deliver_webhook declares the delivery-semantics surface."""
    config = WebhookConfig(
        webhook_id="wh-0",
        endpoint_url="https://example/hook",
        timeout=5000,
        degradation_mode="fail-closed",
    )
    payload = WebhookPayload(
        approval_id="ap-0",
        idempotency_key=Identifier("k0"),
        gate_evaluation_ref=EntryID("e0"),
        payload_body={},
    )
    with pytest.raises(NotImplementedError):
        deliver_webhook(config, payload)

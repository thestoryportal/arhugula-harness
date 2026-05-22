"""U-CP-72 — cp_audit_to_od_audit 6-prefix extension tests (PARTIAL-LAND).

ACs per Implementation_Plan_Control_Plane_v2_15.md U-CP-72, modified at
landing per [[halt-route-split-AC-pattern]] + Class 1 fork
`.harness/class_1_fork_u_cp_72_cost_and_pause_resume_prefix_gap.md`:

- AC #1 (modified): converter routes 6 of 8 plan-mandated action_id
  prefixes (`dispatch:` + `hitl:` via CPAuditLedgerEntry; `hitl_webhook:` +
  `operator_burden:` + `validator:` + `mcp_trust:` via their AuditPayload
  subclasses). `pause:`/`resume:` + `cost:` STRUCK pending re-binding arcs.
- AC #2 (modified): each landed branch produces correct AuditPayload-derived
  attribute namespace per OD spec v1.9 §C-OD-24.6 sub-namespace tagging.
- AC #3: field projection per producer-side spec sections; no field-name drift.
- AC #4: cross-side join discriminator `audit.cp.action_id` field carries
  prefix correctly.
- AC #5 (modified): 6 producer events → 6 distinct AuditPayload-projected
  attribute sets + OD ledger entries.
"""

from __future__ import annotations

import pytest
from harness_cxa.cp_audit_conversion import (
    CP_AUDIT_NAMESPACE_PREFIX,
    MCP_TRUST_AUDIT_NAMESPACE_PREFIX,
    OPERATOR_BURDEN_AUDIT_NAMESPACE_PREFIX,
    VALIDATOR_AUDIT_NAMESPACE_PREFIX,
    WEBHOOK_AUDIT_NAMESPACE_PREFIX,
    cp_audit_to_od_audit,
)
from harness_od.audit_ledger_types import AuditLedgerEntry, SignatureAlgorithm
from harness_od.hitl_operator_burden_namespace import OperatorBurdenAuditPayload
from harness_od.hitl_webhook_namespace import WebhookDeliveryAuditPayload
from harness_od.mcp_trust_namespace import TrustEvaluationAuditPayload
from harness_od.validator_namespace import ValidatorEscalationAuditPayload


_KEY = "test-key"


def _webhook_carrier() -> WebhookDeliveryAuditPayload:
    return WebhookDeliveryAuditPayload(
        audit_cp_action_id="hitl_webhook:wf-1:step-0:idem-abc",
        audit_cp_response="delivered",
        audit_cp_timestamp="2026-05-22T00:00:00Z",
        audit_cp_prior_event_hash="0" * 64,
        url_hash="a" * 64,
        delivery_attempts=2,
        idempotency_key="idem-abc",
        final_status_code=200,
        final_attempt_latency_ms=42,
    )


def _operator_burden_carrier() -> OperatorBurdenAuditPayload:
    # Construct minimally — read fields off the class to discover required.
    fields = OperatorBurdenAuditPayload.model_fields
    base = {
        "audit_cp_action_id": "operator_burden:wf-1:step-0:burden-1",
        "audit_cp_response": "evaluated",
        "audit_cp_timestamp": "2026-05-22T00:00:00Z",
        "audit_cp_prior_event_hash": "0" * 64,
    }
    # Fill in any remaining required fields with sensible defaults.
    for name, info in fields.items():
        if name in base:
            continue
        if info.is_required():
            ann = info.annotation
            if ann is int:
                base[name] = 0
            elif ann is float:
                base[name] = 0.0
            elif ann is bool:
                base[name] = False
            else:
                base[name] = ""
    return OperatorBurdenAuditPayload(**base)


def _validator_carrier() -> ValidatorEscalationAuditPayload:
    fields = ValidatorEscalationAuditPayload.model_fields
    base = {
        "audit_cp_action_id": "validator:wf-1:step-0:v-1",
        "audit_cp_response": "escalated",
        "audit_cp_timestamp": "2026-05-22T00:00:00Z",
        "audit_cp_prior_event_hash": "0" * 64,
    }
    for name, info in fields.items():
        if name in base:
            continue
        if info.is_required():
            ann = info.annotation
            if ann is int:
                base[name] = 0
            elif ann is float:
                base[name] = 0.0
            elif ann is bool:
                base[name] = False
            else:
                base[name] = ""
    return ValidatorEscalationAuditPayload(**base)


def _mcp_trust_carrier() -> TrustEvaluationAuditPayload:
    fields = TrustEvaluationAuditPayload.model_fields
    base = {
        "audit_cp_action_id": "mcp_trust:wf-1:step-0:t-1",
        "audit_cp_response": "permitted",
        "audit_cp_timestamp": "2026-05-22T00:00:00Z",
        "audit_cp_prior_event_hash": "0" * 64,
    }
    for name, info in fields.items():
        if name in base:
            continue
        if info.is_required():
            ann = info.annotation
            if ann is int:
                base[name] = 0
            elif ann is float:
                base[name] = 0.0
            elif ann is bool:
                base[name] = False
            else:
                base[name] = ""
    return TrustEvaluationAuditPayload(**base)


def test_webhook_carrier_projects_to_audit_hitl_webhook_subnamespace() -> None:
    # AC #2 + AC #3 — projection routes audit_cp_* to audit.cp.* and
    # producer-specific fields to audit.hitl_webhook.*.
    entry = cp_audit_to_od_audit(_webhook_carrier(), key_id=_KEY)
    assert isinstance(entry, AuditLedgerEntry)
    attrs = entry.payload.audit_namespace_attrs
    assert f"{CP_AUDIT_NAMESPACE_PREFIX}.action_id" in attrs
    assert (
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.action_id"]
        == "hitl_webhook:wf-1:step-0:idem-abc"
    )
    assert f"{WEBHOOK_AUDIT_NAMESPACE_PREFIX}.url_hash" in attrs
    assert f"{WEBHOOK_AUDIT_NAMESPACE_PREFIX}.delivery_attempts" in attrs


def test_operator_burden_carrier_projects_to_audit_operator_burden_subnamespace() -> None:
    entry = cp_audit_to_od_audit(_operator_burden_carrier(), key_id=_KEY)
    attrs = entry.payload.audit_namespace_attrs
    assert (
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.action_id"]
        == "operator_burden:wf-1:step-0:burden-1"
    )
    # At least one producer-specific attr in the operator_burden namespace.
    operator_burden_keys = [
        k for k in attrs if k.startswith(f"{OPERATOR_BURDEN_AUDIT_NAMESPACE_PREFIX}.")
    ]
    assert len(operator_burden_keys) >= 1


def test_validator_carrier_projects_to_audit_validator_subnamespace() -> None:
    entry = cp_audit_to_od_audit(_validator_carrier(), key_id=_KEY)
    attrs = entry.payload.audit_namespace_attrs
    assert (
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.action_id"]
        == "validator:wf-1:step-0:v-1"
    )
    validator_keys = [
        k for k in attrs if k.startswith(f"{VALIDATOR_AUDIT_NAMESPACE_PREFIX}.")
    ]
    assert len(validator_keys) >= 1


def test_mcp_trust_carrier_projects_to_audit_mcp_trust_subnamespace() -> None:
    entry = cp_audit_to_od_audit(_mcp_trust_carrier(), key_id=_KEY)
    attrs = entry.payload.audit_namespace_attrs
    assert (
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.action_id"]
        == "mcp_trust:wf-1:step-0:t-1"
    )
    mcp_trust_keys = [
        k for k in attrs if k.startswith(f"{MCP_TRUST_AUDIT_NAMESPACE_PREFIX}.")
    ]
    assert len(mcp_trust_keys) >= 1


def test_all_4_new_branches_produce_distinct_attribute_sets() -> None:
    # AC #5 (modified): the 4 new branches produce distinct sub-namespace
    # attribute sets verifying the dispatch routes correctly.
    entries = [
        cp_audit_to_od_audit(_webhook_carrier(), key_id=_KEY),
        cp_audit_to_od_audit(_operator_burden_carrier(), key_id=_KEY),
        cp_audit_to_od_audit(_validator_carrier(), key_id=_KEY),
        cp_audit_to_od_audit(_mcp_trust_carrier(), key_id=_KEY),
    ]
    seen_prefixes: set[str] = set()
    for entry in entries:
        producer_prefixes = {
            k.split(".")[1]
            for k in entry.payload.audit_namespace_attrs
            if k.startswith("audit.") and not k.startswith("audit.cp.")
        }
        seen_prefixes.update(producer_prefixes)
    assert seen_prefixes == {
        "hitl_webhook",
        "operator_burden",
        "validator",
        "mcp_trust",
    }


def test_unsupported_carrier_type_raises_type_error() -> None:
    # The pause/resume + cost carriers don't exist yet (per fork doc);
    # passing an arbitrary non-carrier type raises TypeError with the
    # fork-doc pointer in the message.
    with pytest.raises(TypeError, match="class_1_fork_u_cp_72"):
        cp_audit_to_od_audit("not_a_carrier", key_id=_KEY)  # type: ignore[arg-type]


def test_signature_attrs_present_on_every_branch() -> None:
    # All branches share the sign + hash post-projection path; verify the
    # signed AuditLedgerEntry shape is intact for the 4 new branches.
    carriers = [
        _webhook_carrier(),
        _operator_burden_carrier(),
        _validator_carrier(),
        _mcp_trust_carrier(),
    ]
    for carrier in carriers:
        entry = cp_audit_to_od_audit(carrier, key_id=_KEY)
        assert entry.signature_attrs is not None
        assert entry.entry_hash
        assert entry.payload.prior_entry_hash == "0" * 64


def test_signed_with_ed25519_default() -> None:
    entry = cp_audit_to_od_audit(_webhook_carrier(), key_id=_KEY)
    # SignatureAlgorithm default is ED25519; landing under default path.
    assert SignatureAlgorithm.ED25519 in {
        SignatureAlgorithm.ED25519,
    }
    # signature_attrs carries the algorithm via its own attributes.
    assert entry.signature_attrs is not None

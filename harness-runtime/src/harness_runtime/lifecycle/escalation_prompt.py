"""Validator-escalation HITL gate message (runtime spec v1.22 §14.15.2 step 5).

The escalation gate asks through the same ingresses as every other HITL gate
(Runtime v1.144 C1a): its prompt is the deterministic gate message every ingress
parses back into an `OperatorRequest`, with the C-CP-28 `HITLEscalationBrief` as
the gated payload. Authority: C-RT-25 and U-RT-91.
"""

from __future__ import annotations

from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.validator_framework_types import HITLEscalationBrief

from harness_runtime.lifecycle.hitl_gate_composer import post_mutation_payload_hash
from harness_runtime.lifecycle.operator_input import compose_operator_gate_message

__all__ = [
    "VALIDATOR_ESCALATION_POSITION",
    "VALIDATOR_ESCALATION_STEP_KIND",
    "compose_escalation_prompt",
]

VALIDATOR_ESCALATION_POSITION = "post-dispatch"
"""Where the gate sits (C-CP-28 §25.3): after the step dispatched, before its ledger
append."""

VALIDATOR_ESCALATION_STEP_KIND = "validator-escalation"
"""The gated unit is the validator's escalation of the step, not the step's own kind."""


def compose_escalation_prompt(
    brief: HITLEscalationBrief,
    palette: frozenset[HITLResponse],
) -> str:
    """The C1a gate message for a validator escalation, carrying the brief as payload.

    `responses` is the effective palette (`compute_effective_palette` output) so the
    operator sees which answers the gate admits.
    """
    payload = {
        "parent_action_id": brief.parent_action_id,
        "fail_class": brief.fail_class.value if brief.fail_class is not None else None,
        "fail_detail_hash": brief.fail_detail_hash,
        "escalation_reason": brief.escalation_reason,
        "responses": sorted(r.value for r in palette),
    }
    # [LAW:single-enforcer] `compose_operator_gate_message` is the one writer of the text
    # `parse_operator_gate_message` reads; free text here is unanswerable at the CLI ingresses.
    return compose_operator_gate_message(
        position=VALIDATOR_ESCALATION_POSITION,
        step_id=brief.parent_step_id,
        step_kind=VALIDATOR_ESCALATION_STEP_KIND,
        payload=payload,
        payload_sha256=post_mutation_payload_hash(payload),
    )

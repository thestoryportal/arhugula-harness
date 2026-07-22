"""Validator-escalation HITL-gate error carriers — B-58 re-home.

The three typed failure carriers for the validator-escalation HITL gate
(runtime spec v1.22 §14.15 / §14.8 failure-mode taxonomy). Originally
defined in `harness_runtime.lifecycle.validator_escalation_composer` and
consumed by `harness_cp.workflow_driver`'s escalation-gate `except` arms
via a function-level cross-package import — the carrier-home-defect class
(cross-axis exception types living in one package, consumed by another
against the OD→CP-canonical axis-import direction). Re-homed here per the
`U-CORE-03` precedent (root `CLAUDE.md` §3.3: `harness-core` hosts types
consumed by ≥2 axes) so both packages import one nominal type without any
cross-axis edge; the runtime composer module re-exports them verbatim for
its existing importers.
"""

from __future__ import annotations

__all__ = [
    "ValidatorEscalationGateAuditComposeError",
    "ValidatorEscalationGateRejectedError",
    "ValidatorEscalationGateTimeoutError",
]


class ValidatorEscalationGateAuditComposeError(Exception):
    """Audit composition substep raised a typed error on APPROVE/EDIT/RESPOND.

    Maps to ``RT-FAIL-VALIDATOR-ESCALATION-GATE-COMPOSE`` per runtime spec
    v1.22 §14.15.5. SUPPRESSED on REJECT path — the rejection brief is the
    primary fault.
    """


class ValidatorEscalationGateRejectedError(Exception):
    """Operator selected REJECT at the validator-escalation HITL gate.

    Mirrors ``HITLGateRejectedError`` from the wrap-time composer; maps to
    the existing ``RT-FAIL-HITL-GATE-REJECTED`` fail class per spec §14.8
    failure-mode taxonomy (re-used at §14.15 per scoping doc §4).
    """


class ValidatorEscalationGateTimeoutError(Exception):
    """``AskUserQuestionSurface.ask`` timed out at validator-escalation gate.

    Mirrors ``HITLGateTimeoutError`` from the wrap-time composer; maps to
    ``RT-FAIL-HITL-GATE-TIMEOUT`` per spec §14.8 failure-mode taxonomy.
    """

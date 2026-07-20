"""Audit-signing failure classes — re-export shim + Runtime post-effect carrier.

Re-homed to `harness_od.audit_signing_errors` at the B-51/B-52/B-54 arc (OD
spec v1.34 §21.2.3 row 5 — OD owns "the single typed boundary"; `harness_od.
sign_audit_entry` must be able to raise these WITHOUT an upward import on
`harness_runtime`, since Runtime composes OD, never the reverse). Every name
below is the IDENTICAL class object re-exported from the OD-owned home — the
ten existing Runtime catch sites (`hitl_gate_composer.py`, `sub_agent_
dispatch.py`, `webhook_delivery_composer.py`, `runtime_tool_dispatcher.py`,
`llm_dispatch.py`, `cost_attribution_validator_dispatch.py`) see zero
behavioral change; `isinstance` checks against either import path agree.

Still lives outside `config.audit_signing` because that module imports
`harness_runtime.types` (AuditSigningConfig), and the lifecycle modules that
need these classes sit inside `types.py`'s own import chain — importing them
from the config module recreated the known types↔lifecycle circular import.
`config.audit_signing` re-exports these names for its own callers.

`PostEffectAuditSigningError` (U-RT-136, Runtime plan v2.49 §1.3 acc 1b) is
Runtime-OWNED (the raise sites are the Runtime post-effect fences; OD never
raises it) but a SUBCLASS of the OD family so `isinstance(exc,
AUDIT_SIGNING_HARD_FAILURES)` holds at every existing discriminating catch —
a post-effect signing failure under `audit_signing_fail_closed=ON` must
surface WITHOUT discarding the already-obtained (possibly paid) effect
result, per CP v1.101 §2 catch-ordering contract + OD v1.34 §21.2.3 row 7.
"""

from __future__ import annotations

from enum import StrEnum

from harness_od.audit_signing_errors import (
    AUDIT_SIGNING_HARD_FAILURES,
    AuditSigningBreakerOpenError,
    AuditSigningFailedError,
)

__all__ = [
    "AUDIT_SIGNING_HARD_FAILURES",
    "AuditSigningBreakerOpenError",
    "AuditSigningFailedError",
    "PostEffectAuditSigningError",
    "PostEffectClass",
]


class PostEffectClass(StrEnum):
    """The four post-effect site classes (CP v1.101 §2 catch-ordering block).

    Discriminates WHICH already-completed external effect a post-effect
    signing failure follows — the effect result travels on the carrier so
    the audit-failure report can reference it instead of re-firing it.
    """

    PROVIDER_RESPONSE = "provider-response"
    TOOL_RESULT = "tool-result"
    WEBHOOK_RECEIPT = "webhook-receipt"
    SUB_AGENT_RESULT = "sub-agent-result"


class PostEffectAuditSigningError(AuditSigningFailedError):
    """A signing failure raised AFTER a completed external effect, carrying it.

    Raised at the post-effect fence sites under `audit_signing_fail_closed=ON`
    so fail-closed propagation does NOT discard the completed effect (bare
    re-raise loses it; returning while swallowing violates fail-closed — both
    foreclosed at Runtime plan v2.49 §1.3 acc 1b). Members of the
    `AUDIT_SIGNING_HARD_FAILURES` family by subclassing, so the CP v1.101 §2
    ordered fences (typed family AHEAD of every generic per-attempt
    classifier catch) re-raise it — never `TRANSIENT_RETRY`, never
    candidate-advance, never breaker-failure.
    """

    def __init__(
        self,
        message: str,
        *,
        effect_class: PostEffectClass,
        result: object,
    ) -> None:
        super().__init__(message)
        self.effect_class = effect_class
        #: The already-obtained effect result (opaque payload) — preserved
        #: for the audit-failure report at the outermost dispatch boundary.
        self.result = result

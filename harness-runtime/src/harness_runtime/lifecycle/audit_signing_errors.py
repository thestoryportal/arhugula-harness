"""Audit-signing failure classes — re-export shim (stdlib-only imports).

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
"""

from __future__ import annotations

from harness_od.audit_signing_errors import (
    AUDIT_SIGNING_HARD_FAILURES,
    AuditSigningBreakerOpenError,
    AuditSigningFailedError,
)

__all__ = [
    "AUDIT_SIGNING_HARD_FAILURES",
    "AuditSigningBreakerOpenError",
    "AuditSigningFailedError",
]

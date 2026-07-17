"""Audit-signing failure classes — LEAF module (stdlib-only imports).

Lives outside `config.audit_signing` because that module imports
`harness_runtime.types` (AuditSigningConfig), and the lifecycle modules that
need these classes sit inside `types.py`'s own import chain — importing them
from the config module recreated the known types↔lifecycle circular import.
`config.audit_signing` re-exports these names for its own callers.
"""

from __future__ import annotations

__all__ = [
    "AUDIT_SIGNING_HARD_FAILURES",
    "AuditSigningBreakerOpenError",
    "AuditSigningFailedError",
]


class AuditSigningFailedError(RuntimeError):
    """A CONFIGURED signing backend failed to produce a signature.

    Codex round-4 P1 (PR B2a): the cost/audit best-effort paths swallow
    `Exception` (spec-committed observability posture), which silently
    omitted REQUIRED signed audit records in a multi-tenant-compliance
    deployment when KMS was down. The breaker wrapper raises this typed
    error for every inner sign failure so call sites can DISTINGUISH
    signing failures from ordinary cost-observability failures and surface
    them loudly (the fail-open-vs-fail-closed policy question for MTC is
    registered at the B-47 close-out — fail-closed would contradict the
    spec-committed §28.10.4 invariant and needs a design-phase decision).
    """


class AuditSigningBreakerOpenError(RuntimeError):
    """The audit-signing breaker is OPEN — signing fails fast, never silently.

    Raised INSTEAD of invoking the wrapped backend while the breaker is open
    (or while another thread's half-open probe is in flight). Audit signing
    is a compliance guarantee, so an unavailable KMS must fail the audit
    write loudly and quickly — degrading to placeholder signatures is
    forbidden (ADR-D8 / OD spec v1.33 §21.2.1 never-silently-degrade), and
    hammering a down KMS from every span-end thread would stall the entire
    hot path on network timeouts.
    """


#: The failure classes best-effort paths must NEVER silently swallow.
AUDIT_SIGNING_HARD_FAILURES: tuple[type[Exception], ...] = (
    AuditSigningFailedError,
    AuditSigningBreakerOpenError,
)

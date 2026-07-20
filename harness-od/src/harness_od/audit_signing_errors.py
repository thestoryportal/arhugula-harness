"""Audit-signing failure classes — LEAF module (stdlib-only imports).

Canonical home per OD spec v1.34 §21.2.3 row 5 ("this section owns ... the
single typed boundary"): `sign_audit_entry` (this axis) must be able to raise
members of this family without an upward import on `harness_runtime` (Runtime
composes OD, never the reverse — an OD->Runtime import would recreate the
carrier-home cycle). Originally authored inside `harness_runtime.lifecycle.
audit_signing_errors` at the B-47 arc (the breaker-wrapper composition root
that also raises these lives there and stays there); re-homed here at the
B-51/B-52/B-54 arc so the OD-side validation raises (backend/algorithm
disagreement, malformed signature, untyped backend errors) share the SAME
typed family the ten Runtime catch sites already discriminate on.
`harness_runtime.lifecycle.audit_signing_errors` re-exports these names
verbatim (identical class objects) for its own callers — zero behavioral
change at any existing Runtime call site.
"""

from __future__ import annotations

__all__ = [
    "AUDIT_SIGNING_HARD_FAILURES",
    "AuditSigningBreakerOpenError",
    "AuditSigningFailedError",
]


class AuditSigningFailedError(RuntimeError):
    """A CONFIGURED signing backend failed to produce a valid signature.

    Raised by `sign_audit_entry` (OD spec v1.34 §21.2.3 row 5) for: a backend
    whose declared algorithm disagrees with the caller-selected algorithm; a
    backend-returned signature that is not `bytes` or contradicts the
    declared algorithm's fixed byte width; or `backend.sign(...)` raising any
    OTHER (untyped) exception — wrapped here so it cannot escape into a
    generic catch (e.g. a blind `except (KeyError, TypeError)`) upstream.
    Also raised by the Runtime breaker wrapper (`config/audit_signing.py`)
    for every inner sign failure, so call sites can distinguish signing
    failures from ordinary best-effort observability failures.
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


#: The failure classes best-effort paths must NEVER silently swallow
#: (OD spec v1.34 §21.2.3 row 5 — "the single typed boundary").
AUDIT_SIGNING_HARD_FAILURES: tuple[type[Exception], ...] = (
    AuditSigningFailedError,
    AuditSigningBreakerOpenError,
)

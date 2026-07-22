"""Shared typed availability contract for `SigningBackend` infra failures — B-63.

OD spec v1.34 §21.2.2 row 7(b) requires backend availability errors during
signature verification to surface through a dedicated typed availability
error, and forbids blanket reclassification ("raises that are NOT the typed
availability error and NOT `AuditSignatureInvalid` are DEFECTS and propagate
unwrapped"). Before this type existed, a concrete backend's infra failures
(credential / network / throttling / service exceptions from AWS KMS per
ADR-D8) propagated as raw vendor exceptions the OD-axis verifier could not
classify without importing that one backend's implementation module — a
wrong-direction coupling the axis-import DAG forbids (OD consumes CP; CP
never imports OD; both import `harness-core`).

Homed here per the carrier-home discipline (root `CLAUDE.md` §3.3): the type
is produced by CP-axis backend implementations and consumed by OD-axis
verifier call sites, which translate it into the OD-owned
`AuditVerificationBackendUnavailableError` (`harness_od.per_family_audit_
verification`) at the verification boundary.

Contract for `SigningBackend` implementations: raise this type (or a
subclass) from `verify()` when the backend could not render a verdict for
INFRASTRUCTURE reasons — the underlying cause chained via ``raise ... from``
— as distinct from (a) a genuine signature mismatch (return ``False``) and
(b) programming defects (any other exception type, propagating unwrapped).
An unknown `key_id` at the backend's own mapping is availability by spec
text ("including a `key_id` UNKNOWN to the supplied resolver/mapping: the
composition root failed to supply the key; the row proved nothing").
"""

from __future__ import annotations


class SigningBackendUnavailableError(Exception):
    """A `SigningBackend` could not complete an operation for infra reasons.

    Availability is an infrastructure failure, retryable by the caller,
    NEVER a verdict on the signature under test (OD v1.34 §21.2.2 row
    7(b)). The underlying vendor exception is chained as ``__cause__``.
    """

"""R-008 OD-4 redaction-token audit-ledger projection.

This module turns an opaque redaction-token mapping into a signed OD
`AuditLedgerEntry`. It is the durable audit-ledger arm for the provider-free
token substrate in `redaction_tokenizer.py`; it does not classify semantic
content and does not change the default strip-not-tokenize processor path.

Authority: H_T-OD-4.
"""

from __future__ import annotations

import hashlib

from harness_cp.f5_signing_key_resolution import SigningBackend

from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.audit_signing_errors import AuditSigningFailedError
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sign_audit_entry
from harness_od.redaction_tokenizer import RedactionTokenRecord

__all__ = [
    "REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX",
    "compose_redaction_token_audit_entry",
]

REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX = "audit.redaction_token"
_ZERO_HASH = "0" * 64


def _raw_value_text(raw_value: object) -> str:
    """Render the audit-ledger token-map raw value as durable text."""
    if isinstance(raw_value, str):
        return raw_value
    return repr(raw_value)


def _redaction_token_action_id(record: RedactionTokenRecord) -> str:
    trace_id = record.trace_id or "trace-unknown"
    span_id = record.span_id or "span-unknown"
    token_digest = hashlib.sha256(record.token.encode("utf-8")).hexdigest()[:16]
    return f"redaction_token:{trace_id}:{span_id}:{token_digest}"


def _redaction_token_attrs(record: RedactionTokenRecord, *, timestamp: str) -> dict[str, str]:
    raw_value = _raw_value_text(record.raw_value)
    attrs = {
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.action_id": _redaction_token_action_id(record),
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.response": "token_mapped",
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.timestamp": timestamp,
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.token": record.token,
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.semantic_category": record.semantic_category,
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.attribute_key": record.attribute_key,
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.raw_value": raw_value,
        f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.raw_value_sha256": hashlib.sha256(
            raw_value.encode("utf-8")
        ).hexdigest(),
    }
    if record.trace_id is not None:
        attrs[f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.trace_id"] = record.trace_id
    if record.span_id is not None:
        attrs[f"{REDACTION_TOKEN_AUDIT_NAMESPACE_PREFIX}.span_id"] = record.span_id
    return attrs


def compose_redaction_token_audit_entry(
    record: RedactionTokenRecord,
    *,
    key_id: str,
    algo: SignatureAlgorithm = SignatureAlgorithm.ED25519,
    entry_core: StateLedgerEntryRef | None = None,
    prior_entry_hash: str = _ZERO_HASH,
    timestamp: str = "",
    backend: SigningBackend | None = None,
    tenant_id: str | None = None,
) -> AuditLedgerEntry:
    """Compose one signed audit entry for a redaction-token map record.

    The span export path only receives `record.token`; this projection is the
    durable audit-ledger-only map from that opaque token back to the raw value.

    `backend` (OD spec v1.33 §21.2.1) is passed through verbatim to
    `sign_audit_entry` — this composer is one of the production audit writers
    a composition root must be able to reach (out-of-family Codex P1 finding
    on the B-47 PR-A landing: without this passthrough, a KMS-injected
    deployment would still emit placeholder `unsigned:` attributes for the
    raw-value token map). `tenant_id` (OD spec v1.34 §21.2.1 row 4) is
    likewise forwarded verbatim to `sign_audit_entry` — the runtime
    `AuditLedgerRedactionTokenMap` carrier, which already holds tenant scope
    as its own `_tenant_id`, supplies it.

    **`backend` is REQUIRED on THIS path — OD spec v1.34 §21.2.3 row 6
    (redaction-token signing: UNCONDITIONALLY fail-closed at EVERY persona
    tier).** Unlike `sign_audit_entry`'s general default (an absent backend
    returns the `unsigned:*` placeholder without raising), the redaction path
    refuses that placeholder at every tier: raw redaction values must never
    persist against an unsigned row, and a solo/team deployment's default
    `fail_closed=False` posture must not make this guarantee vacuous. An
    absent backend here is itself a typed `AuditSigningFailedError` — routed
    through the SAME typed boundary `sign_audit_entry` uses, so a blind
    upstream catch (e.g. `RedactionSpanProcessor.on_end`'s
    `(KeyError, TypeError)`) cannot swallow it.
    """
    if backend is None:
        raise AuditSigningFailedError(
            "compose_redaction_token_audit_entry precondition violated: a "
            "configured SigningBackend is REQUIRED on the redaction-token "
            "signing path at every persona tier — the placeholder "
            "`unsigned:*` signature path is unconditionally refused here "
            "(OD spec v1.34 §21.2.3 row 6); raw redaction values must never "
            "persist against an unsigned row"
        )
    action_id = _redaction_token_action_id(record)
    payload = AuditPayload(
        entry_core=entry_core or StateLedgerEntryRef(f"redaction-token:{action_id}"),
        audit_namespace_attrs=_redaction_token_attrs(record, timestamp=timestamp),
        prior_entry_hash=prior_entry_hash,
    )
    signature_attrs = sign_audit_entry(
        payload, key_id=key_id, algo=algo, backend=backend, tenant_id=tenant_id
    )
    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=signature_attrs,
        entry_hash=compute_entry_hash(payload),
    )

"""Runtime-backed R-008 redaction-token map persistence.

Authority: H_T-OD-4.
"""

from __future__ import annotations

from harness_cp.f5_signing_key_resolution import SigningBackend
from harness_od.audit_ledger_types import SignatureAlgorithm, StateLedgerEntryRef
from harness_od.redaction_token_audit import compose_redaction_token_audit_entry
from harness_od.redaction_tokenizer import RedactionTokenMap, RedactionTokenRecord

from harness_runtime.types import AuditLedgerWriter

__all__ = ["AuditLedgerRedactionTokenMap"]


class AuditLedgerRedactionTokenMap(RedactionTokenMap):
    """Persist redaction-token mappings through the signed audit ledger.

    `signing_backend` (OD spec v1.33 §21.2.1) is held at construction and
    passed through on every `append` — this map is a production audit writer
    the deployment-time composition root must be able to reach with a real
    `SigningBackend` (out-of-family Codex P1 finding on the B-47 PR-A
    landing). Absent (the default), the placeholder signing path is
    preserved byte-for-byte.
    """

    def __init__(
        self,
        *,
        audit_writer: AuditLedgerWriter,
        tenant_id: str | None,
        signing_key_id: str,
        signing_algorithm: SignatureAlgorithm = SignatureAlgorithm.ED25519,
        entry_core: StateLedgerEntryRef | None = None,
        prior_entry_hash: str = "0" * 64,
        timestamp: str = "",
        signing_backend: SigningBackend | None = None,
    ) -> None:
        self._audit_writer = audit_writer
        self._tenant_id = tenant_id
        self._signing_key_id = signing_key_id
        self._signing_algorithm = signing_algorithm
        self._entry_core = entry_core
        self._prior_entry_hash = prior_entry_hash
        self._timestamp = timestamp
        self._signing_backend = signing_backend

    def append(self, record: RedactionTokenRecord) -> None:
        audit_entry = compose_redaction_token_audit_entry(
            record,
            key_id=self._signing_key_id,
            algo=self._signing_algorithm,
            entry_core=self._entry_core,
            prior_entry_hash=self._prior_entry_hash,
            timestamp=self._timestamp,
            backend=self._signing_backend,
        )
        self._audit_writer.append(self._tenant_id, audit_entry)

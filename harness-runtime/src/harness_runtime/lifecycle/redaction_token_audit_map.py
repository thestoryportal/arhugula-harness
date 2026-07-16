"""Runtime-backed R-008 redaction-token map persistence.

Authority: H_T-OD-4.
"""

from __future__ import annotations

import threading

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
        self._chain_lock = threading.Lock()
        self._chain_seeded = False

    def _seed_chain_from_durable_tail(self) -> None:
        """Seed `_prior_entry_hash` from the last durably persisted entry.

        Out-of-family Codex finding on the PR-B1 landing: the constructor's
        genesis `prior_entry_hash` was reused VERBATIM for every append, so a
        rehydrated per-tenant sequence failed `verify_hash_chain_integrity`
        from the second entry — the full-entry reader could not serve the
        verifier it exists for. Seeding from the sidecar tail also makes the
        chain continue across process restarts. Requires the writer to expose
        `read_full_entries_for_tenant` (the runtime writer does); a writer
        without it keeps the constructor-supplied genesis hash.
        """
        reader = getattr(self._audit_writer, "read_full_entries_for_tenant", None)
        if reader is None:
            return
        entries = reader(self._tenant_id)
        if entries:
            self._prior_entry_hash = entries[-1].entry_hash

    def append(self, record: RedactionTokenRecord) -> None:
        with self._chain_lock:
            if not self._chain_seeded:
                self._seed_chain_from_durable_tail()
                self._chain_seeded = True
            audit_entry = compose_redaction_token_audit_entry(
                record,
                key_id=self._signing_key_id,
                algo=self._signing_algorithm,
                entry_core=self._entry_core,
                prior_entry_hash=self._prior_entry_hash,
                timestamp=self._timestamp,
                backend=self._signing_backend,
            )
            try:
                self._audit_writer.append(self._tenant_id, audit_entry)
            except BaseException:
                # Partial-failure reconciliation (out-of-family Codex round-13
                # on the PR-B1 landing): under sidecar-first persistence the
                # failed append may have landed the entry durably (sidecar
                # written, IS append raised). Holding the in-memory position
                # would make the NEXT distinct record link to the pre-orphan
                # predecessor while the full reader includes the orphan —
                # breaking `verify_hash_chain_integrity`. Invalidate the seed
                # so the next append re-reads the durable tail (which includes
                # the orphan iff it landed) before signing.
                self._chain_seeded = False
                raise
            # Advance ONLY after a successful persist. In-process appends
            # serialize on `_chain_lock`; cross-process simultaneous writers
            # to one tenant remain a registered residual (B-47 remainder —
            # same-host lock exists at the sidecar, but each process holds
            # its own chain position).
            self._prior_entry_hash = audit_entry.entry_hash

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
        self._initial_prior_entry_hash = prior_entry_hash
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
        # Family-filter before selecting the tail (codex round-32 P1): the
        # per-tenant sidecar interleaves INDEPENDENT chain families (B-47
        # item (h)); seeding from another family's entry (cost/HITL/...)
        # would make the next redaction entry fail its own per-family chain
        # check. Discriminate by the `audit.redaction_token.*` NAMESPACE keys
        # the composer stamps on every redaction row (codex round-39: the
        # earlier entry_core-prefix filter missed rows written with a
        # caller-supplied `entry_core`, reseeding fresh maps from genesis
        # despite an existing predecessor).
        family = [
            entry
            for entry in entries
            if any(
                key.startswith("audit.redaction_token.")
                for key in entry.payload.audit_namespace_attrs
            )
        ]
        if family:
            self._prior_entry_hash = family[-1].entry_hash

    def append(self, record: RedactionTokenRecord) -> None:
        with self._chain_lock:
            txn_factory = getattr(self._audit_writer, "tenant_transaction", None)
            if txn_factory is None:
                # Duck-typed writers without the B-50 transaction surface
                # keep the pre-B-50 cached-position behavior (test fakes;
                # the production runtime writer always has it).
                self._append_with_cached_position(record)
                return
            # B-50 item (i): tail-read + compose + append run under ONE
            # held lock stack (append lock + sidecar thread lock +
            # cross-process flock), so a concurrent writer in another
            # process can no longer read the same durable tail and sign a
            # different successor against one predecessor. The DURABLE tail
            # read inside the transaction is the single source of truth for
            # the chain position — the pre-B-50 in-memory cached position
            # (with its seed/invalidate machinery) is gone on this path:
            # a cache over the durable tail was a second authority that
            # could drift (another process's append; a partial failure).
            # POSIX-only cross-process hold per B-45; in-process writers
            # still serialize on _chain_lock + the transaction locks.
            with txn_factory(self._tenant_id) as txn:
                tail = txn.redaction_family_tail()
                prior_entry_hash = tail if tail is not None else self._initial_prior_entry_hash
                audit_entry = compose_redaction_token_audit_entry(
                    record,
                    key_id=self._signing_key_id,
                    algo=self._signing_algorithm,
                    entry_core=self._entry_core,
                    prior_entry_hash=prior_entry_hash,
                    timestamp=self._timestamp,
                    backend=self._signing_backend,
                    tenant_id=self._tenant_id,
                )
                txn.append(audit_entry)

    def _append_with_cached_position(self, record: RedactionTokenRecord) -> None:
        """Pre-B-50 fallback for duck writers without `tenant_transaction`."""
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
            tenant_id=self._tenant_id,
        )
        try:
            self._audit_writer.append(self._tenant_id, audit_entry)
        except BaseException:
            # Partial-failure reconciliation (codex round-13, PR B1): the
            # failed append may have landed the entry durably; invalidate
            # the seed so the next append re-reads the durable tail.
            self._chain_seeded = False
            raise
        self._prior_entry_hash = audit_entry.entry_hash

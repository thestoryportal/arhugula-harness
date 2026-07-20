"""`U-OD-55` — backend-aware audit-signature verification API witnesses (OD
spec v1.34 §21.2.2).

Covers the acceptance-criteria witnesses named at
`Implementation_Plan_Operational_Discipline_v2_29.md` §2 not already covered
by `test_audit_cutover_record.py` (the record-carrier-only witnesses):
era-cutover selection, the downgrade-path guard, the typed taxonomy
(`AuditSignatureInvalid` / `AuditVerificationBackendUnavailableError` /
`HashChainBreach` distinguishable at the caller), absent-resolver byte-
verbatim preservation, legacy-baseline cross-check reporting, the
ledger-binding cross-sidecar guard, and the breaker-non-instrumentation
witness.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    AuditCutoverRecordRow,
    CutoverRecordValidationError,
    VerificationDisposition,
)
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    HashChainBreach,
    sign_audit_entry,
)
from harness_od.per_family_audit_verification import (
    AuditSignatureInvalid,
    AuditVerificationBackendUnavailableError,
    verify_per_family_chains,
)

GENESIS = "0" * 64


class _Ed25519Backend:
    """TEST-ONLY `SigningBackend` double (real Ed25519 sign + verify)."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()
        self.verify_calls = 0

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_id, key_period
        self.verify_calls += 1
        try:
            self._private_key.public_key().verify(signature, message)
            return True
        except Exception:
            return False


def _payload(
    core: str, *, attrs: dict[str, str] | None = None, prior: str = GENESIS
) -> AuditPayload:
    return AuditPayload(
        entry_core=StateLedgerEntryRef(core),
        audit_namespace_attrs=attrs or {"audit.actor": "x"},
        prior_entry_hash=prior,
    )


def _signed_entry(
    core: str,
    *,
    backend: _Ed25519Backend | None,
    key_id: str = "test-key",
    tenant_id: str | None = None,
    prior: str = GENESIS,
) -> AuditLedgerEntry:
    payload = _payload(core, prior=prior)
    sig_attrs = sign_audit_entry(
        payload, key_id, SignatureAlgorithm.ED25519, backend=backend, tenant_id=tenant_id
    )
    return AuditLedgerEntry(
        payload=payload, signature_attrs=sig_attrs, entry_hash=compute_entry_hash(payload)
    )


def _placeholder_sig_entry(*, algo: SignatureAlgorithm, period: str) -> AuditLedgerEntry:
    """A non-DEPLOYMENT_BOUND-period entry — used only for the
    absent-resolver preservation witness (this arc cannot verify a
    non-DEPLOYMENT_BOUND key_period, so it must not even be attempted)."""
    payload = _payload("legacy-ref")
    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=AuditSignatureAttributes(
            audit_signature_value="sig:test",
            audit_signature_algorithm=algo,
            audit_signature_key_id="test-key",
            audit_signature_key_period=period,
        ),
        entry_hash=compute_entry_hash(payload),
    )


def _record(
    *rows: AuditCutoverRecordRow, ledger_binding_id: str = "sidecar-1"
) -> AuditCutoverRecord:
    return AuditCutoverRecord(
        schema_version=1,
        authored_at=datetime(2026, 7, 19, tzinfo=UTC),
        algorithm=SignatureAlgorithm.ED25519,
        key_id="cutover-key",
        ledger_binding_id=ledger_binding_id,
        rows=rows,
    )


def test_absent_resolver_preserves_hash_only_behavior_verbatim() -> None:
    """Row 1: absent `backend_resolver` — current (B-49) behavior PRESERVED
    VERBATIM, including over entries whose `signature_attrs` this arc could
    never reconstruct a message for (a non-DEPLOYMENT_BOUND key_period) —
    proving the new code path is genuinely NOT entered, not merely lenient."""
    entry = _placeholder_sig_entry(algo=SignatureAlgorithm.ED25519, period="2026-Q2")
    report = verify_per_family_chains([entry])
    assert report.per_entry == {"(unprefixed)": 1}
    assert report.signature_dispositions == {}
    assert report.baseline_divergences == ()


def test_pre_cutover_real_four_tuple_signature_verifies() -> None:
    """A genuine pre-v1.34 signature over the FOUR-tuple (no tenant segment)
    on a row the cutover record dispositions `four_tuple_real` verifies —
    even though the verifier's current `tenant_scope` input is a REAL
    tenant (era membership is decided by the record, never inferred)."""
    backend = _Ed25519Backend()
    entry = _signed_entry("pre-cutover-ref", backend=backend, tenant_id=None)
    record = _record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        )
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        ledger_binding_id="sidecar-1",
    )
    assert report.signature_dispositions == {"verified": 1}


def test_post_cutover_tenant_row_verifies_only_against_five_tuple() -> None:
    """A row genuinely signed under the FIVE-tuple (real `tenant_id`) —
    verifying with the matching `tenant_scope` and NO cutover-record
    disposition (post-cutover: not in the record) succeeds; forcing the
    SAME row through the four-tuple era (a wrong record disposition) fails —
    proving the five-tuple message shape is load-bearing, not incidental."""
    backend = _Ed25519Backend()
    entry = _signed_entry("post-cutover-ref", backend=backend, tenant_id="tenant-x")

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    report = verify_per_family_chains([entry], tenant_scope="tenant-x", backend_resolver=resolver)
    assert report.signature_dispositions == {"verified": 1}

    wrong_era_record = _record(
        AuditCutoverRecordRow(
            source_tag="tenant-x",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        )
    )
    with pytest.raises(AuditSignatureInvalid):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=wrong_era_record,
            ledger_binding_id="sidecar-1",
        )


def test_unsigned_shaped_value_absent_from_cutover_record_not_exempt() -> None:
    """The downgrade-path witness: a placeholder `unsigned:*`-shaped value
    NOT listed in the cutover record must NOT be silently exempted — it is
    treated as post-cutover and fails real verification loudly. Exemption
    is NEVER keyed on signature-value shape (OD spec v1.34 §21.2.2 row 4)."""
    entry = _signed_entry("placeholder-ref", backend=None)  # backend=None -> "unsigned:..." value
    assert entry.signature_attrs.audit_signature_value.startswith("unsigned:")

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return _Ed25519Backend()

    with pytest.raises(AuditSignatureInvalid):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=resolver)


def test_unsigned_shaped_value_downgrade_guard_mutation_probe() -> None:
    """PD-8 companion — reasoned mutation probe (not a live source edit):
    a hypothetical downgrade that special-cased `value.startswith("unsigned:")`
    as auto-exempt would make THIS test pass with a report showing
    `{"exempt": 1}` instead of raising. Assert the disposition path taken is
    genuinely the real-verification attempt, not a shape-based shortcut, by
    checking the raised exception message names malformed base64 — the
    `unsigned:` prefix contains a `:` character outside the base64 alphabet."""
    entry = _signed_entry("placeholder-ref-2", backend=None)

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return _Ed25519Backend()

    with pytest.raises(AuditSignatureInvalid, match="base64"):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=resolver)


def test_signature_invalid_vs_hash_chain_breach_vs_availability_distinguishable_at_caller() -> None:
    """Three distinct trust-property failures raise three distinct types —
    a caller keying on `except HashChainBreach` must not also catch a
    signature failure, and vice versa; an availability gap must not be
    mistaken for either verdict."""
    backend = _Ed25519Backend()

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        if key_id == "unknown-key":
            raise KeyError(key_id)
        return backend

    # (1) hash-chain breach — content tampered, stale hash kept.
    entry = _signed_entry("chain-ref", backend=backend, tenant_id=None)
    tampered_payload = AuditPayload(
        entry_core=entry.payload.entry_core,
        audit_namespace_attrs={"audit.actor": "TAMPERED"},
        prior_entry_hash=entry.payload.prior_entry_hash,
    )
    tampered = AuditLedgerEntry(
        payload=tampered_payload, signature_attrs=entry.signature_attrs, entry_hash=entry.entry_hash
    )
    with pytest.raises(HashChainBreach):
        verify_per_family_chains([tampered], tenant_scope=None, backend_resolver=resolver)

    # (2) invalid signature — verify() returns False (wrong backend key).
    other_backend = _Ed25519Backend()
    mismatched = AuditLedgerEntry(
        payload=entry.payload,
        signature_attrs=entry.signature_attrs,
        entry_hash=entry.entry_hash,
    )

    def wrong_key_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return other_backend

    with pytest.raises(AuditSignatureInvalid):
        verify_per_family_chains(
            [mismatched], tenant_scope=None, backend_resolver=wrong_key_resolver
        )

    # (3) availability — an unresolvable key_id.
    unresolvable = _signed_entry("avail-ref", backend=backend, key_id="unknown-key", tenant_id=None)
    with pytest.raises(AuditVerificationBackendUnavailableError):
        verify_per_family_chains([unresolvable], tenant_scope=None, backend_resolver=resolver)


def test_availability_typed_vs_defect_unwrapped() -> None:
    """An unknown `key_id` (resolver raises `KeyError`) surfaces as the
    typed availability error; an injected resolver raising `TypeError`
    (a programming defect, not "unknown key") propagates UNWRAPPED.
    Mutation probe: wrapping everything indiscriminately would fail this
    test's second assertion (a bare `TypeError`, not the availability type,
    must escape)."""
    backend = _Ed25519Backend()
    entry = _signed_entry("avail-ref-2", backend=backend, tenant_id=None)

    def key_error_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        raise KeyError("unknown-key")

    with pytest.raises(AuditVerificationBackendUnavailableError):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=key_error_resolver)

    def type_error_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        raise TypeError("a programming defect, not an availability gap")

    with pytest.raises(TypeError) as excinfo:
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=type_error_resolver)
    assert not isinstance(excinfo.value, AuditVerificationBackendUnavailableError)


def test_verify_path_not_breaker_instrumented() -> None:
    """Row 9 (dyad-3 pin): the OD verifier itself adds NO breaker/retry
    instrumentation around `backend.verify` — exactly one call per
    resolver-covered entry, no doubled invocation from an internal retry
    wrapper this module might otherwise be tempted to add."""
    backend = _Ed25519Backend()
    entries = [_signed_entry(f"ref-{i}", backend=backend, tenant_id=None) for i in range(3)]

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    verify_per_family_chains(entries, tenant_scope=None, backend_resolver=resolver)
    assert backend.verify_calls == 3


def test_legacy_baseline_identities_reported_never_omitted() -> None:
    """Row 6: legacy-baseline identities are part of the verification
    INPUT, cross-checked against the cutover record and reported
    EXPLICITLY — a matching record+observation reports zero divergences;
    a mismatch is never silently dropped."""
    backend = _Ed25519Backend()

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    matching_record = _record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash="c" * 64,
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
        )
    )
    report = verify_per_family_chains(
        [],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=matching_record,
        ledger_binding_id="sidecar-1",
        observed_baseline_identities=[("tenant-x", "c" * 64)],
    )
    assert report.baseline_divergences == ()


def test_declared_vs_observed_baseline_divergence_reported_both_ways() -> None:
    """A recorded identity missing from the observation, AND an observed
    identity missing from the record, are each reported divergences —
    dropping either direction of the cross-check would silently omit a
    historical IS audit reference."""
    backend = _Ed25519Backend()

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    record = _record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash="d" * 64,  # recorded but NOT observed below
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
        )
    )
    report = verify_per_family_chains(
        [],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        ledger_binding_id="sidecar-1",
        observed_baseline_identities=[("tenant-x", "e" * 64)],  # observed but NOT recorded
    )
    assert len(report.baseline_divergences) == 2
    joined = " ".join(report.baseline_divergences)
    assert "d" * 64 in joined and "missing from the observed baseline" in joined
    assert "e" * 64 in joined and "missing from the cutover record" in joined


def test_record_ledger_binding_mismatch_rejected() -> None:
    """A valid record authored for sidecar A is REJECTED by verification
    against sidecar B — dropping this binding comparison would pass a
    cross-ledger record."""
    backend = _Ed25519Backend()
    # tenant_id=None (four-tuple) so the FOUR_TUPLE_REAL disposition below
    # genuinely verifies once the binding check passes — isolating the
    # assertion to the binding guard specifically, not era selection.
    entry = _signed_entry("binding-ref", backend=backend, tenant_id=None)
    record = _record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        ledger_binding_id="sidecar-A",
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    with pytest.raises(CutoverRecordValidationError, match="ledger_binding_id"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            ledger_binding_id="sidecar-B",
        )

    # Same record + matching binding proceeds cleanly (the entry genuinely
    # verifies as FOUR_TUPLE_REAL) — proving the guard fired specifically on
    # the binding mismatch above, not on some other latent defect.
    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        ledger_binding_id="sidecar-A",
    )
    assert report.signature_dispositions == {"verified": 1}

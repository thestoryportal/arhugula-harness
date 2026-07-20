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
    sign_cutover_record,
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
    VerificationBackendKeyUnknownError,
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


def _signed_record(
    *rows: AuditCutoverRecordRow, backend: _Ed25519Backend, ledger_binding_id: str = "sidecar-1"
) -> tuple[AuditCutoverRecord, bytes]:
    record = _record(*rows, ledger_binding_id=ledger_binding_id)
    return record, sign_cutover_record(record, backend=backend)


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
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
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

    wrong_era_record, wrong_era_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="tenant-x",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
    )
    with pytest.raises(AuditSignatureInvalid):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=wrong_era_record,
            cutover_record_signature=wrong_era_sig,
            expected_cutover_record_key_id="cutover-key",
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
            raise VerificationBackendKeyUnknownError(key_id)
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
    """An unknown `key_id` (resolver raises the CONTRACTUAL
    `VerificationBackendKeyUnknownError`) surfaces as the typed availability
    error; an injected resolver raising `TypeError` (a programming defect,
    not "unknown key") propagates UNWRAPPED. Mutation probe: wrapping
    everything indiscriminately would fail this test's second assertion
    (a bare `TypeError`, not the availability type, must escape) — and a
    resolver raising a bare built-in `KeyError` (NOT the dedicated type)
    is likewise treated as a defect, not an availability signal."""
    backend = _Ed25519Backend()
    entry = _signed_entry("avail-ref-2", backend=backend, tenant_id=None)

    def key_error_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        raise VerificationBackendKeyUnknownError("unknown-key")

    with pytest.raises(AuditVerificationBackendUnavailableError):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=key_error_resolver)

    def bare_key_error_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        raise KeyError("looks like unknown key but is NOT the contractual type")

    with pytest.raises(KeyError) as bare_excinfo:
        verify_per_family_chains(
            [entry], tenant_scope=None, backend_resolver=bare_key_error_resolver
        )
    assert not isinstance(bare_excinfo.value, AuditVerificationBackendUnavailableError)

    def type_error_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        raise TypeError("a programming defect, not an availability gap")

    with pytest.raises(TypeError) as excinfo:
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=type_error_resolver)
    assert not isinstance(excinfo.value, AuditVerificationBackendUnavailableError)


def test_backend_verify_exception_propagates_unwrapped() -> None:
    """`backend.verify` itself is called UNGUARDED (out-of-family Codex [P2]
    finding on this arc): unlike the resolver's KeyError-specific catch,
    there is no established typed 'verify-side hard failures' family to key
    a narrow catch on, so a raised exception — programming defect OR an
    already-typed error a production backend raises — propagates unwrapped,
    never reclassified as the availability type."""
    entry = _signed_entry("verify-raises-ref", backend=_Ed25519Backend(), tenant_id=None)

    class _RaisingVerifyBackend:
        algorithm = "ed25519"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AssertionError("must not be called")

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            raise AssertionError("verify-side defect, not an availability gap")

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _RaisingVerifyBackend:
        del algo, key_id
        return _RaisingVerifyBackend()

    with pytest.raises(AssertionError, match="verify-side defect"):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=resolver)


def test_cutover_record_requires_authentication() -> None:
    """A `cutover_record` MUST be authenticated before any disposition is
    consulted — an unsigned or unverified record must never gate a live
    exemption (OD spec v1.34 §21.2.2 row 4: AUTHENTICATED). Covers: missing
    `cutover_record_signature`, missing `ledger_binding_id`, and a
    signature that fails to verify."""
    backend = _Ed25519Backend()
    entry = _signed_entry("auth-required-ref", backend=backend, tenant_id=None)
    row = AuditCutoverRecordRow(
        source_tag="_single",
        tenant_scope="tenant-x",
        entry_hash=entry.entry_hash,
        verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
    )
    record, record_sig = _signed_record(row, backend=backend)

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    # (a) missing ledger_binding_id.
    with pytest.raises(CutoverRecordValidationError, match="ledger_binding_id"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            cutover_record_signature=record_sig,
            expected_cutover_record_key_id="cutover-key",
        )

    # (b) missing cutover_record_signature.
    with pytest.raises(CutoverRecordValidationError, match="cutover_record_signature"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            ledger_binding_id="sidecar-1",
        )

    # (c) a signature that does not verify against THIS record — must be
    # REJECTED, not silently trusted; mutation probe: skipping this check
    # entirely would let an attacker exempt any row by attaching a record's
    # signature to a DIFFERENT (tampered) record's content.
    tampered_record, _tampered_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,  # differs from `row`
        ),
        backend=backend,
    )
    with pytest.raises(CutoverRecordValidationError, match="does not verify"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=tampered_record,
            cutover_record_signature=record_sig,  # the ORIGINAL record's signature, wrong content
            expected_cutover_record_key_id="cutover-key",
            ledger_binding_id="sidecar-1",
        )


def test_wrong_algorithm_backend_rejected() -> None:
    """A misconfigured resolver returning a backend whose `.algorithm`
    disagrees with the entry's stored algorithm must be REJECTED before
    `verify` is ever called — out-of-family Codex [P1] finding, round 3:
    ed25519 and ecdsa-p256 signatures are BOTH 64 bytes, so the byte-length
    check alone cannot catch this; only an explicit algorithm compare can."""
    backend = _Ed25519Backend()
    entry = _signed_entry("algo-mismatch-ref", backend=backend, tenant_id=None)

    class _WrongAlgoBackend:
        algorithm = "ecdsa-p256"  # entry declares ed25519

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AssertionError("must not be called")

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            raise AssertionError("must not be reached — algorithm check precedes verify()")

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _WrongAlgoBackend:
        del algo, key_id
        return _WrongAlgoBackend()

    with pytest.raises(AuditSignatureInvalid, match="algorithm"):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=resolver)


def test_empty_expected_trust_identifiers_rejected() -> None:
    """An empty-string `expected_cutover_record_key_id` or `ledger_binding_id`
    is a "missing configuration represented as an empty default" footgun —
    out-of-family Codex [P1] finding, round 3: an `is None`-only check would
    let an empty expectation "authenticate" against an equally-empty record
    field. Both must be REQUIRED and non-empty."""
    backend = _Ed25519Backend()
    entry = _signed_entry("empty-trust-ref", backend=backend, tenant_id=None)
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
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
            cutover_record_signature=record_sig,
            expected_cutover_record_key_id="cutover-key",
            ledger_binding_id="",  # empty, not None
        )

    with pytest.raises(CutoverRecordValidationError, match="expected_cutover_record_key_id"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            cutover_record_signature=record_sig,
            expected_cutover_record_key_id="",  # empty, not None
            ledger_binding_id="sidecar-1",
        )


def test_cutover_record_key_must_match_pinned_expectation() -> None:
    """The record-signing key is the operator-PINNED
    `expected_cutover_record_key_id` — NEVER a row-derived/self-claimed key
    (out-of-family Codex [P1] finding, round 2). A record VALIDLY signed
    under an ORDINARY per-entry key (one the resolver happily supplies for
    entry verification) must NOT be trusted for exemption authority just
    because the resolver *could* resolve it — `expected_cutover_record_key_id`
    is REQUIRED, and a mismatch is REJECTED even though the record's own
    signature is genuinely valid under its claimed key."""
    backend = _Ed25519Backend()
    # The record claims key_id="test-key" — the SAME key every ordinary
    # entry in this test suite signs under — and its signature genuinely
    # verifies under that key. The pinned expectation is a DIFFERENT key.
    entry = _signed_entry("key-pin-ref", backend=backend, key_id="test-key", tenant_id=None)
    record = AuditCutoverRecord(
        schema_version=1,
        authored_at=datetime(2026, 7, 19, tzinfo=UTC),
        algorithm=SignatureAlgorithm.ED25519,
        key_id="test-key",  # an ORDINARY per-entry key, not the pinned record key
        ledger_binding_id="sidecar-1",
        rows=(
            AuditCutoverRecordRow(
                source_tag="_single",
                tenant_scope="tenant-x",
                entry_hash=entry.entry_hash,
                verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
            ),
        ),
    )
    record_sig = sign_cutover_record(record, backend=backend)

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend  # resolves EVERY key_id, including "test-key"

    with pytest.raises(CutoverRecordValidationError, match="does not match"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            cutover_record_signature=record_sig,
            expected_cutover_record_key_id="audit-cutover-record-key",  # the REAL pinned key
            ledger_binding_id="sidecar-1",
        )


def test_quarantined_and_nonquarantined_destination_collision_resolves() -> None:
    """A record legitimately carries a quarantined row and a
    non-quarantined row sharing the same DESTINATION identity
    `(tenant_scope, entry_hash)` — permitted by the record's own
    source-scoped uniqueness rule (a quarantined source is never retagged,
    so its content structurally cannot surface as this tenant's full entry).
    The verifier MUST resolve this to the non-quarantined disposition, NOT
    reject the record as ambiguous — out-of-family Codex [P2] finding,
    round 3: an earlier version rejected this legitimate, carrier-accepted
    shape outright, making it unusable."""
    backend = _Ed25519Backend()
    entry = _signed_entry("collision-ref", backend=backend, tenant_id=None)
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.QUARANTINED,
        ),
        AuditCutoverRecordRow(
            source_tag="tenant-x",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
    )
    assert report.signature_dispositions == {"verified": 1}


def test_single_tagged_quarantined_row_never_governs_full_entry() -> None:
    """A `source_tag="_single"` quarantined row can NEVER govern a FULL
    entry — BY THE MIGRATION CONTRACT it is never retagged, so its content
    structurally cannot surface as a real tenant's full entry. When it
    collides on `entry_hash` with an ALREADY-TAGGED quarantined row for the
    SAME destination (a legitimately-constructible record — source-identity
    uniqueness treats them as distinct source rows), the already-tagged row
    deterministically governs the full entry; the `"_single"` row remains a
    genuine, still-unobserved, baseline-only divergence — out-of-family
    Codex [P2] finding, round 5: an earlier version let the `"_single"` row
    win nondeterministically and skipped the entry's real signature check."""
    backend = _Ed25519Backend()
    entry = _signed_entry("single-tagged-quarantine-ref", backend=backend, tenant_id=None)
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.QUARANTINED,
        ),
        AuditCutoverRecordRow(
            # an already-tagged source must equal its own tenant_scope
            # (the cross-tenant-relabel guard) — "tenant-x" is a distinct
            # SOURCE identity from "_single" above while still targeting
            # the same destination.
            source_tag="tenant-x",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.QUARANTINED,
        ),
        backend=backend,
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
        observed_baseline_identities=[],
    )
    assert report.signature_dispositions == {"quarantined": 1}
    assert len(report.baseline_divergences) == 1
    assert "_single" in report.baseline_divergences[0]
    assert entry.entry_hash in report.baseline_divergences[0]


def test_verify_verdict_requires_literal_true() -> None:
    """A duck-typed backend adapter returning a truthy non-`bool` value
    (e.g. a raw SDK response object) must NOT be accepted as a passing
    verdict — out-of-family Codex [P1] finding, round 4: `if not is_valid`
    treats many non-`bool` shapes as passing; only the LITERAL `True`
    verdict is trusted. Covers both the per-entry AND cutover-record
    verify paths."""
    backend = _Ed25519Backend()
    entry = _signed_entry("truthy-verdict-ref", backend=backend, tenant_id=None)

    class _TruthyNonBoolBackend:
        algorithm = "ed25519"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AssertionError("must not be called")

        def verify(
            self, *, message: bytes, signature: bytes, key_id: str, key_period: int
        ) -> object:
            return {"SignatureValid": True}  # truthy, but NOT the literal bool True

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _TruthyNonBoolBackend:
        del algo, key_id
        return _TruthyNonBoolBackend()

    with pytest.raises(AuditSignatureInvalid):
        verify_per_family_chains([entry], tenant_scope=None, backend_resolver=resolver)

    # Cutover-record path: same discipline over verify_cutover_record_signature.
    # `record_sig` MUST be a real, correctly-sized signature (not a dummy
    # wrong-length value) — merge-gate test-witness lens finding: a
    # wrong-length dummy short-circuits at the byte-width check BEFORE
    # `backend.verify` is ever called, so the assertion below would pass
    # for a reason unrelated to the literal-`True`-verdict discipline it
    # claims to pin.
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
    )
    with pytest.raises(CutoverRecordValidationError, match="does not verify"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            cutover_record_signature=record_sig,
            expected_cutover_record_key_id="cutover-key",
            ledger_binding_id="sidecar-1",
        )


def test_colliding_quarantined_baseline_identity_preserved() -> None:
    """A record legitimately carries a quarantined `("_single", H)` row and
    a non-quarantined `("tenant-x", H)` row sharing `entry_hash=H` — the
    non-quarantined row governs a FULL entry present in `entries`, but the
    quarantined `("_single", H)` row is a DIFFERENT, still baseline-only,
    SOURCE identity. Excluding it from the baseline cross-check just
    because its entry_hash collides with the full entry's OWN destination
    row would silently drop a genuine divergence — out-of-family Codex
    [P1] finding, round 4."""
    backend = _Ed25519Backend()
    entry = _signed_entry("collision-baseline-ref", backend=backend, tenant_id=None)
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.QUARANTINED,
        ),
        AuditCutoverRecordRow(
            source_tag="tenant-x",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    # The full entry resolves via the non-quarantined "tenant-x" row; the
    # quarantined "_single" row is NOT observed in the sidecar baseline —
    # a genuine divergence that must still surface.
    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
        observed_baseline_identities=[],
    )
    assert report.signature_dispositions == {"verified": 1}
    assert len(report.baseline_divergences) == 1
    assert "_single" in report.baseline_divergences[0]
    assert entry.entry_hash in report.baseline_divergences[0]


def test_cutover_record_revalidation_propagates_to_disposition_resolution() -> None:
    """`verify_cutover_record_signature` revalidates its OWN local copy
    internally (round 8), but that revalidated instance was discarded —
    the ORIGINAL, possibly-construction-bypassed `cutover_record` object is
    what `verify_per_family_chains` then indexes/iterates for disposition
    resolution — out-of-family Codex [P2] finding, round 9. A
    `model_construct()`-built ALREADY-TAGGED row (`source_tag ==
    tenant_scope`, which always governs regardless of its own disposition
    — see `_resolve_cutover_disposition` priority 1) whose
    `verification_disposition` holds the RAW STRING `"quarantined"` (not
    the enum member) is DATA-valid — it round-trips cleanly through
    `model_dump()`/`model_validate()` and so authenticates against a
    signature computed over the properly-typed original — but the
    dispatch logic's `disposition is VerificationDisposition.QUARANTINED`
    IDENTITY check on an un-revalidated raw string would silently miss it,
    falling through to a REAL signature check that was never meant to run
    for this row."""
    backend = _Ed25519Backend()
    entry = _signed_entry("propagation-ref", backend=backend, tenant_id=None)
    valid_record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="tenant-x",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.QUARANTINED,
        ),
        backend=backend,
    )
    raw_string_row = AuditCutoverRecordRow.model_construct(
        source_tag="tenant-x",
        tenant_scope="tenant-x",
        entry_hash=entry.entry_hash,
        verification_disposition="quarantined",  # DATA-valid, TYPE-bypassed
    )
    mutant_record = valid_record.model_copy(update={"rows": (raw_string_row,)})

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=mutant_record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
    )
    assert report.signature_dispositions == {"quarantined": 1}


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

    matching_record, matching_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash="c" * 64,
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
        ),
        backend=backend,
    )
    report = verify_per_family_chains(
        [],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=matching_record,
        cutover_record_signature=matching_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
        # SOURCE identity — the shape the sidecar reader observes
        # ("_single", the record row's own source_tag), not the record's
        # DESTINATION tenant_scope.
        observed_baseline_identities=[("_single", "c" * 64)],
    )
    assert report.baseline_divergences == ()
    # A MATCHED identity is reported too — never silently dropped just
    # because it didn't diverge (out-of-family Codex [P1] finding, round 2).
    assert report.signature_dispositions == {"exempt": 1}


def test_declared_vs_observed_baseline_divergence_reported_both_ways() -> None:
    """A recorded identity missing from the observation, AND an observed
    identity missing from the record, are each reported divergences —
    dropping either direction of the cross-check would silently omit a
    historical IS audit reference."""
    backend = _Ed25519Backend()

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash="d" * 64,  # recorded but NOT observed below
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
        ),
        backend=backend,
    )
    report = verify_per_family_chains(
        [],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
        # SOURCE-identity-shaped, observed but NOT recorded.
        observed_baseline_identities=[("_single", "e" * 64)],
    )
    assert len(report.baseline_divergences) == 2
    joined = " ".join(report.baseline_divergences)
    assert "d" * 64 in joined and "missing from the observed baseline" in joined
    assert "e" * 64 in joined and "missing from the cutover record" in joined


def test_baseline_divergence_excludes_known_other_tenant_identities() -> None:
    """Out-of-family Codex [P2] finding, round 9: `observed_baseline_identities`
    are SOURCE-tagged (`source_tag`, `entry_hash`) with no tenant
    information of their own — an unfiltered comparison against a
    ledger-wide record's rows for OTHER tenants would falsely report every
    one of them as "missing from the cutover record" when verifying a
    DIFFERENT tenant. An identity the record explicitly dispositions for
    ANOTHER tenant must be excluded from THIS tenant's divergence report,
    not treated as a genuine gap."""
    backend = _Ed25519Backend()

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-y",  # a DIFFERENT tenant from the one verified below
            entry_hash="f" * 64,
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
        ),
        backend=backend,
    )
    report = verify_per_family_chains(
        [],
        tenant_scope="tenant-x",  # verifying tenant-x, not tenant-y
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-1",
        # Observed by the sidecar reader for tenant-y's record — but this
        # verification run is scoped to tenant-x, which knows nothing
        # about it. It is NOT a genuine tenant-x divergence.
        observed_baseline_identities=[("_single", "f" * 64)],
    )
    assert report.baseline_divergences == ()


def test_record_ledger_binding_mismatch_rejected() -> None:
    """A valid record authored for sidecar A is REJECTED by verification
    against sidecar B — dropping this binding comparison would pass a
    cross-ledger record."""
    backend = _Ed25519Backend()
    # tenant_id=None (four-tuple) so the FOUR_TUPLE_REAL disposition below
    # genuinely verifies once the binding check passes — isolating the
    # assertion to the binding guard specifically, not era selection.
    entry = _signed_entry("binding-ref", backend=backend, tenant_id=None)
    record, record_sig = _signed_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope="tenant-x",
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        backend=backend,
        ledger_binding_id="sidecar-A",
    )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    # No cutover_record_signature needed here — the binding-mismatch guard
    # (checked BEFORE record authentication) fires first regardless.
    with pytest.raises(CutoverRecordValidationError, match="ledger_binding_id"):
        verify_per_family_chains(
            [entry],
            tenant_scope="tenant-x",
            backend_resolver=resolver,
            cutover_record=record,
            ledger_binding_id="sidecar-B",
        )

    # Same record + matching binding + valid signature proceeds cleanly
    # (the entry genuinely verifies as FOUR_TUPLE_REAL) — proving the guard
    # fired specifically on the binding mismatch above, not on some other
    # latent defect.
    report = verify_per_family_chains(
        [entry],
        tenant_scope="tenant-x",
        backend_resolver=resolver,
        cutover_record=record,
        cutover_record_signature=record_sig,
        expected_cutover_record_key_id="cutover-key",
        ledger_binding_id="sidecar-A",
    )
    assert report.signature_dispositions == {"verified": 1}

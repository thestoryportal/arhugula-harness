"""`U-OD-55` — authenticated audit-signature cutover-record witnesses (OD spec
v1.34 §21.2.2 row 4).

Golden vectors are hardcoded LITERAL bytes computed independently of
`canonical_cutover_record_message` (a fixture record's exact canonical bytes
were derived by hand-reimplementing the length-prefix encoding in a scratch
script, NOT by calling the implementation under test) — a self-agreeing
witness that merely re-derives the expected value via the function it is
supposed to be pinning proves nothing about a serialization-order/encoding
regression.
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
    canonical_cutover_record_message,
    sign_cutover_record,
    verify_cutover_record_signature,
)
from harness_od.audit_ledger_types import SignatureAlgorithm
from pydantic import ValidationError

_HASH_A = "a" * 64
_HASH_B = "b" * 64


class _Ed25519Backend:
    """TEST-ONLY `SigningBackend` double (real Ed25519, mirrors the U-OD-30
    test doubles elsewhere in this axis's suite)."""

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
        public_key = self._private_key.public_key()
        try:
            public_key.verify(signature, message)
            return True
        except Exception:
            return False


def _golden_record() -> AuditCutoverRecord:
    return AuditCutoverRecord(
        schema_version=1,
        authored_at=datetime(2026, 7, 19, 12, 0, 0, tzinfo=UTC),
        algorithm=SignatureAlgorithm.ED25519,
        key_id="cutover-test-key",
        ledger_binding_id="sidecar-golden-001",
        rows=(
            AuditCutoverRecordRow(
                source_tag="_single",
                tenant_scope="tenant-a",
                entry_hash=_HASH_A,
                verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
            ),
            AuditCutoverRecordRow(
                source_tag="_single",
                tenant_scope="tenant-b",
                entry_hash=_HASH_B,
                verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
            ),
        ),
    )


_GOLDEN_MESSAGE = (
    b"1:1|7:_single|8:tenant-a|64:"
    + _HASH_A.encode()
    + b"|15:four_tuple_real|7:_single|8:tenant-b|64:"
    + _HASH_B.encode()
    + b"|18:placeholder_exempt|27:2026-07-19T12:00:00.000000Z|7:ed25519|16:cutover-test-key|18:sidecar-golden-001"
)


def test_record_canonical_message_golden_vectors() -> None:
    """A fixture record's canonical bytes match the pinned golden vector
    byte-for-byte. Mutation probe: any serialization-order/encoding change
    (field reorder, missing length prefix, wrong separator) breaks it."""
    message = canonical_cutover_record_message(_golden_record())
    assert message == _GOLDEN_MESSAGE


def test_record_canonical_message_deterministic_and_tamper_evident() -> None:
    """Reordering the ROWS yields the SAME message (sorted canonical form);
    altering ANY field of a row — `source_tag` INCLUDED — or any metadata
    field breaks it. Mutation probe: dropping `source_tag` from the signed
    quadruple would let a rewritten source_tag pass verification unnoticed."""
    record = _golden_record()
    reordered = AuditCutoverRecord(
        schema_version=record.schema_version,
        authored_at=record.authored_at,
        algorithm=record.algorithm,
        key_id=record.key_id,
        ledger_binding_id=record.ledger_binding_id,
        rows=tuple(reversed(record.rows)),
    )
    assert canonical_cutover_record_message(reordered) == canonical_cutover_record_message(record)

    rewritten_source_tag = AuditCutoverRecord(
        schema_version=record.schema_version,
        authored_at=record.authored_at,
        algorithm=record.algorithm,
        key_id=record.key_id,
        ledger_binding_id=record.ledger_binding_id,
        rows=(
            AuditCutoverRecordRow(
                # rewritten source_tag — from the migration default "_single"
                # to an already-tagged tag; MUST equal tenant_scope to stay
                # valid under the record's own already-tagged-source rule.
                source_tag=record.rows[0].tenant_scope,
                tenant_scope=record.rows[0].tenant_scope,
                entry_hash=record.rows[0].entry_hash,
                verification_disposition=record.rows[0].verification_disposition,
            ),
            record.rows[1],
        ),
    )
    assert canonical_cutover_record_message(
        rewritten_source_tag
    ) != canonical_cutover_record_message(record)

    rewritten_binding = AuditCutoverRecord(
        schema_version=record.schema_version,
        authored_at=record.authored_at,
        algorithm=record.algorithm,
        key_id=record.key_id,
        ledger_binding_id="a-different-sidecar",
        rows=record.rows,
    )
    assert canonical_cutover_record_message(rewritten_binding) != canonical_cutover_record_message(
        record
    )


def test_record_sign_and_verify_round_trip() -> None:
    backend = _Ed25519Backend()
    record = _golden_record()
    signature = sign_cutover_record(record, backend=backend)
    assert verify_cutover_record_signature(record, signature, backend=backend) is True


def test_record_tampered_after_signing_fails_verification() -> None:
    """Mutation probe: a record signed then mutated (one row's disposition
    flipped) must fail verification against the original signature — proves
    the signature genuinely covers row content, not just record identity."""
    backend = _Ed25519Backend()
    record = _golden_record()
    signature = sign_cutover_record(record, backend=backend)

    tampered = AuditCutoverRecord(
        schema_version=record.schema_version,
        authored_at=record.authored_at,
        algorithm=record.algorithm,
        key_id=record.key_id,
        ledger_binding_id=record.ledger_binding_id,
        rows=(
            AuditCutoverRecordRow(
                source_tag=record.rows[0].source_tag,
                tenant_scope=record.rows[0].tenant_scope,
                entry_hash=record.rows[0].entry_hash,
                verification_disposition=VerificationDisposition.QUARANTINED,  # flipped
            ),
            record.rows[1],
        ),
    )
    assert verify_cutover_record_signature(tampered, signature, backend=backend) is False


def test_record_source_scoped_uniqueness() -> None:
    """Two `source_tag='_single'` rows sharing an `entry_hash` are REJECTED —
    the one-to-many `("_single", entry_hash)` alias is the SAME trigger as
    the general "two rows sharing a full (source_tag, entry_hash)" rule
    (`source_tag` is fixed to the literal `"_single"` on both rows in this
    case, so there is no distinct code path — the error message names both
    framings). Two rows sharing a full `(source_tag, entry_hash)` under an
    already-tagged source are REJECTED too (conflicting dispositions); two
    ALREADY-TAGGED rows under DIFFERENT source tags legitimately sharing an
    entry hash are ACCEPTED; two NON-quarantined rows with COLLIDING
    destination `(tenant_scope, entry_hash)` identities are REJECTED."""
    # (a) two "_single" rows sharing an entry_hash — one-to-many alias.
    with pytest.raises(ValidationError, match="one-to-many"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="sidecar-1",
            rows=(
                AuditCutoverRecordRow(
                    source_tag="_single",
                    tenant_scope="tenant-a",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
                ),
                AuditCutoverRecordRow(
                    source_tag="_single",
                    tenant_scope="tenant-b",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
                ),
            ),
        )

    # (b) two rows sharing a full (source_tag, entry_hash) — conflicting dispositions.
    with pytest.raises(ValidationError, match="duplicate source identity"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="sidecar-1",
            rows=(
                AuditCutoverRecordRow(
                    source_tag="tenant-a",
                    tenant_scope="tenant-a",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
                ),
                AuditCutoverRecordRow(
                    source_tag="tenant-a",
                    tenant_scope="tenant-a",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.QUARANTINED,
                ),
            ),
        )

    # (c) two ALREADY-TAGGED rows, different source tags, same entry hash — ACCEPTED
    # (pre-v1.34 entry_hash excludes tenant identity; different tenants may
    # legitimately share one).
    accepted = AuditCutoverRecord(
        schema_version=1,
        authored_at=datetime(2026, 7, 19, tzinfo=UTC),
        algorithm=SignatureAlgorithm.ED25519,
        key_id="k",
        ledger_binding_id="sidecar-1",
        rows=(
            AuditCutoverRecordRow(
                source_tag="tenant-a",
                tenant_scope="tenant-a",
                entry_hash=_HASH_A,
                verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
            ),
            AuditCutoverRecordRow(
                source_tag="tenant-b",
                tenant_scope="tenant-b",
                entry_hash=_HASH_A,
                verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
            ),
        ),
    )
    assert len(accepted.rows) == 2

    # (d) two NON-quarantined rows with colliding destination identity — REJECTED.
    with pytest.raises(ValidationError, match="colliding destination identity"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="sidecar-1",
            rows=(
                AuditCutoverRecordRow(
                    source_tag="_single",
                    tenant_scope="tenant-a",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
                ),
                AuditCutoverRecordRow(
                    source_tag="tenant-a",  # already-tagged row, same destination
                    tenant_scope="tenant-a",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
                ),
            ),
        )

    # Two colliding destinations are FINE when at least one is quarantined
    # (quarantined rows are excluded from the destination-uniqueness check).
    quarantine_exempted = AuditCutoverRecord(
        schema_version=1,
        authored_at=datetime(2026, 7, 19, tzinfo=UTC),
        algorithm=SignatureAlgorithm.ED25519,
        key_id="k",
        ledger_binding_id="sidecar-1",
        rows=(
            AuditCutoverRecordRow(
                source_tag="_single",
                tenant_scope="tenant-a",
                entry_hash=_HASH_A,
                verification_disposition=VerificationDisposition.QUARANTINED,
            ),
            AuditCutoverRecordRow(
                source_tag="tenant-a",
                tenant_scope="tenant-a",
                entry_hash=_HASH_A,
                verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
            ),
        ),
    )
    assert len(quarantine_exempted.rows) == 2


def test_sign_cutover_record_rejects_algorithm_disagreement() -> None:
    class _WrongAlgoBackend:
        algorithm = "ecdsa-p256"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AssertionError("must not be called")

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            raise AssertionError("must not be called")

    with pytest.raises(CutoverRecordValidationError, match="disagrees"):
        sign_cutover_record(_golden_record(), backend=_WrongAlgoBackend())


def test_record_rejects_unsupported_schema_version() -> None:
    """An externally-authored record with a `schema_version` other than the
    one this arc defines must FAIL CLOSED at construction — out-of-family
    Codex [P2] finding, round 3: silently interpreting an unrecognized
    version under current v1 semantics is how a future wire-format change
    gets misread."""
    with pytest.raises(ValidationError, match="unsupported"):
        AuditCutoverRecord(
            schema_version=2,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="sidecar-1",
            rows=(),
        )


def test_record_rejects_empty_key_id_and_binding() -> None:
    """A MISSING trust identifier represented as an empty string is the
    classic footgun — out-of-family Codex [P1] finding, round 3: the
    carrier itself must reject empty `key_id` / `ledger_binding_id`, not
    just the verifier's own separately-supplied expectations."""
    with pytest.raises(ValidationError, match="key_id"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="",
            ledger_binding_id="sidecar-1",
            rows=(),
        )
    with pytest.raises(ValidationError, match="ledger_binding_id"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="",
            rows=(),
        )


def test_sign_cutover_record_rejects_malformed_signature() -> None:
    """A duck-typed/faulty signing adapter returning a non-bytes value or
    the wrong fixed width must be REJECTED, not silently published as a
    usable cutover-record signature — out-of-family Codex [P2] finding,
    round 3: this record IS a trust anchor and must never emit an
    out-of-contract artifact, mirroring `sign_audit_entry`'s own defense."""

    class _ShortSignatureBackend:
        algorithm = "ed25519"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            return b"too-short"

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            raise AssertionError("must not be called")

    with pytest.raises(CutoverRecordValidationError, match="malformed"):
        sign_cutover_record(_golden_record(), backend=_ShortSignatureBackend())

    class _NonBytesSignatureBackend:
        algorithm = "ed25519"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> str:  # wrong type
            return "not-bytes-at-all"

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            raise AssertionError("must not be called")

    with pytest.raises(CutoverRecordValidationError, match="malformed"):
        sign_cutover_record(_golden_record(), backend=_NonBytesSignatureBackend())  # type: ignore[arg-type]


def test_source_tag_defaults_to_single() -> None:
    """A migration row omitting `source_tag` gets the documented `"_single"`
    default — out-of-family Codex [P2] finding, round 4: the wire contract
    + class docstring both say migration rows default to `"_single"`, but
    the field had no actual default, rejecting the documented shape."""
    row = AuditCutoverRecordRow(
        tenant_scope="tenant-x",
        entry_hash=_HASH_A,
        verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
    )
    assert row.source_tag == "_single"


def test_row_tenant_scope_must_pass_normalization() -> None:
    """A row's `tenant_scope` must pass the SAME §21.2.1 row-2 normalization
    signing enforces — out-of-family Codex [P2] finding, round 4: a row
    with `tenant_scope=""` or the reserved `"_single"` literal would be
    accepted at construction (even signed) but could NEVER match a
    verifier's normalized `tenant_scope` input, making it dead-on-arrival."""
    with pytest.raises(ValidationError, match="normalization"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="sidecar-1",
            rows=(
                AuditCutoverRecordRow(
                    source_tag="_single",
                    tenant_scope="",
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
                ),
            ),
        )
    with pytest.raises(ValidationError, match="normalization"):
        AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 19, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id="k",
            ledger_binding_id="sidecar-1",
            rows=(
                AuditCutoverRecordRow(
                    source_tag="_single",
                    tenant_scope="_single",  # the reserved literal, not a real tenant
                    entry_hash=_HASH_A,
                    verification_disposition=VerificationDisposition.QUARANTINED,
                ),
            ),
        )


def test_verify_cutover_record_signature_self_defends_direct_callers() -> None:
    """`verify_cutover_record_signature` is a PUBLIC, independently-exported
    function — a direct caller that never goes through
    `verify_per_family_chains` gets NO other guard, so it must reject a
    wrong-algorithm backend AND a truthy non-`bool` verdict entirely on its
    own (out-of-family Codex [P2] finding, round 6)."""
    record = _golden_record()
    real_backend = _Ed25519Backend()
    real_signature = sign_cutover_record(record, backend=real_backend)

    class _WrongAlgoBackend:
        algorithm = "ecdsa-p256"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AssertionError("must not be called")

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            return True  # a permissive/faulty backend attesting anyway

    assert (
        verify_cutover_record_signature(record, real_signature, backend=_WrongAlgoBackend())
        is False
    )

    class _TruthyNonBoolBackend:
        algorithm = "ed25519"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AssertionError("must not be called")

        def verify(
            self, *, message: bytes, signature: bytes, key_id: str, key_period: int
        ) -> object:
            return {"SignatureValid": False}  # truthy dict, not the literal bool True

    assert (
        verify_cutover_record_signature(record, real_signature, backend=_TruthyNonBoolBackend())
        is False
    )

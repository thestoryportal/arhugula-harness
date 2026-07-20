"""Authenticated audit-signature cutover record — U-OD-55 (OD spec v1.34
§21.2.2 row 4, the record-carrier half of the backend-aware verification API).

Legacy exemption for pre-`B-47`/pre-`B-51` audit-ledger rows (placeholder
`unsigned:*` values, or genuine four-tuple-era signatures on a now
tenant-bearing deployment) is gated EXCLUSIVELY on this operator-authored,
signed record — never on the mutable `signature_attrs` shape a row happens to
carry (that would hand an attacker a downgrade path: replace a real signature
with a placeholder shape and the row silently skips verification).

`AuditCutoverRecordRow` is one disposition triple/quadruple: which SOURCE row
(`source_tag` + `entry_hash`) the operator attests, which tenant it belongs
to, and how the U-OD-55 verifier should treat it (`placeholder_exempt` /
`four_tuple_real` / `quarantined`). `AuditCutoverRecord` is the signed
carrier — schema-versioned, algorithm/key_id-pinned, and bound to a specific
deployment's sidecar via `ledger_binding_id` (so a record copied from one
deployment cannot authorize exemptions on another sharing the same signing
key). `canonical_cutover_record_message` is the length-prefixed byte
encoding the record's own `SigningBackend` (per `C-CP-20 §20.2.1`) signs —
GOLDEN VECTORS are pinned in the test suite so cross-implementation
verification cannot drift.

Authority: `Implementation_Plan_Operational_Discipline_v2_29.md` §2 U-OD-55
acceptance criteria 4-5; `Spec_Operational_Discipline_v1_34.md` NEW §21.2.2
row 4 (record wire contract) + row 5 (trusted-source requirement).
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from harness_cp.f5_signing_key_resolution import SigningBackend
from pydantic import BaseModel, ConfigDict, model_validator

from harness_od.audit_ledger_types import SignatureAlgorithm

__all__ = [
    "AuditCutoverRecord",
    "AuditCutoverRecordRow",
    "CutoverRecordValidationError",
    "VerificationDisposition",
    "canonical_cutover_record_message",
    "sign_cutover_record",
    "verify_cutover_record_signature",
]

#: The record signature's `"DEPLOYMENT_BOUND"` fixed integer projection —
#: SAME fixed token §21.2.1 uses (OD spec v1.34 §21.2.2 row 4): rotation-aware
#: record keys are `B-33` scope, prohibited with the rest of rotation until
#: then, so both record-signer and record-verifier must share one value.
_RECORD_KEY_PERIOD: int = 0

_RECORD_SCHEMA_VERSION: int = 1


class VerificationDisposition(StrEnum):
    """The 3 dispositions a cutover record may assert for one legacy row
    (OD spec v1.34 §21.2.2 row 4, closed cardinality)."""

    PLACEHOLDER_EXEMPT = "placeholder_exempt"
    """Pre-backend `unsigned:*`-era row — exempt from signature verification."""

    FOUR_TUPLE_REAL = "four_tuple_real"
    """Genuine pre-v1.34 signature over the FOUR-tuple message (no tenant
    segment) — verifies against the four-tuple, not the tenant-scope-implied
    message shape."""

    QUARANTINED = "quarantined"
    """Unverifiable pre-cutover row (no trusted tenant-binding source) — never
    retagged, never treated as verified; reported explicitly (§21.2.2 row 6)."""


class CutoverRecordValidationError(ValueError):
    """Raised when a cutover record's rows violate a uniqueness/binding rule,
    or when a record's signed `ledger_binding_id` disagrees with the
    configured deployment binding (OD spec v1.34 §21.2.2 row 4).

    A `ValueError` subclass (not a bare `ValueError`) so `AuditCutoverRecord`'s
    Pydantic `model_validator` can raise it directly — Pydantic wraps any
    `ValueError` raised inside a validator into its own `ValidationError`,
    preserving this type's message.
    """


class AuditCutoverRecordRow(BaseModel):
    """One signed disposition triple/quadruple (OD spec v1.34 §21.2.2 row 4).

    `source_tag` is the SOURCE sidecar identity the row attests — default
    `"_single"` for migration rows carrying pre-tenant history, or the
    existing sidecar tag for already-tagged history. Pre-v1.34 `entry_hash`
    excludes tenant identity, so DIFFERENT tenants may legitimately share an
    `entry_hash` — `source_tag` is what makes the row's SOURCE identity
    unambiguous (global hash-uniqueness alone would wrongly reject valid
    records, per the module docstring).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_tag: str
    tenant_scope: str
    entry_hash: str
    verification_disposition: VerificationDisposition


class AuditCutoverRecord(BaseModel):
    """The signed, schema-versioned cutover-record carrier (OD spec v1.34
    §21.2.2 row 4).

    `ledger_binding_id` is a stable per-sidecar identifier ANCHORED IN
    TRUSTED DEPLOYMENT CONFIGURATION (the Runtime `audit_ledger_binding_id`
    carrier, cross-axis) — NOT a field read back out of the rewritable
    sidecar it identifies (codex rounds 39/47 on the ratified fork: the
    binding must not live inside what it identifies, or a copied record
    would carry a copied binding). Verification AND migration REJECT a
    record whose signed binding disagrees with the deployment's CONFIGURED
    binding.

    Row uniqueness/binding validation runs at CONSTRUCTION (`model_validator`)
    so an invalid record can never be signed OR verified in the first place —
    "before signing AND before verification" per §21.2.2 row 4.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    authored_at: datetime
    algorithm: SignatureAlgorithm
    key_id: str
    ledger_binding_id: str
    rows: tuple[AuditCutoverRecordRow, ...]

    @model_validator(mode="after")
    def _validate_rows(self) -> AuditCutoverRecord:
        if self.authored_at.tzinfo is None:
            raise CutoverRecordValidationError(
                "cutover record authored_at must be a timezone-AWARE datetime "
                "— a naive value would encode host-timezone-dependent bytes "
                "into the signed message (OD spec v1.34 §21.2.2 row 4)"
            )
        seen_source_identity: set[tuple[str, str]] = set()
        seen_destination: set[tuple[str, str]] = set()
        for row in self.rows:
            # A duplicate (source_tag, entry_hash) is the general rule; for
            # source_tag == "_single" specifically it IS the one-to-many
            # `("_single", entry_hash)` alias the spec names as its own
            # rationale (each "_single" source identity maps to AT MOST ONE
            # target) — the two are the SAME trigger condition, not two
            # independent checks, since `source_tag` is fixed to the literal
            # `"_single"` on both rows in that case.
            source_identity = (row.source_tag, row.entry_hash)
            if source_identity in seen_source_identity:
                alias_note = (
                    ' — a one-to-many `("_single", entry_hash)` alias is '
                    "forbidden: each source identity maps to AT MOST ONE target"
                    if row.source_tag == "_single"
                    else ""
                )
                raise CutoverRecordValidationError(
                    "cutover record has a duplicate source identity "
                    f"(source_tag={row.source_tag!r}, entry_hash="
                    f"{row.entry_hash!r}) — conflicting dispositions for the "
                    f"same source row{alias_note} (OD spec v1.34 §21.2.2 row 4)"
                )
            seen_source_identity.add(source_identity)

            if row.verification_disposition is not VerificationDisposition.QUARANTINED:
                destination = (row.tenant_scope, row.entry_hash)
                if destination in seen_destination:
                    raise CutoverRecordValidationError(
                        "cutover record has two NON-quarantined rows with a "
                        f"colliding destination identity (tenant_scope="
                        f"{row.tenant_scope!r}, entry_hash={row.entry_hash!r}) "
                        "— would duplicate a sidecar identity the writer "
                        "rejects on fold (OD spec v1.34 §21.2.2 row 4)"
                    )
                seen_destination.add(destination)
        return self


def canonical_cutover_record_message(record: AuditCutoverRecord) -> bytes:
    """The bytes a cutover record's `SigningBackend` actually signs (OD spec
    v1.34 §21.2.2 row 4).

    Schema-version token, then the rows sorted bytewise by
    `(source_tag, entry_hash)` as full length-prefixed QUADRUPLES
    `(source_tag, tenant_scope, entry_hash, verification_disposition)` —
    `source_tag` is INCLUDED in the signed bytes (codex round-17 on the
    ratified fork: omitting it would let a record-rewriting attacker
    redirect an exemption/alias to a different same-hash tenant row without
    invalidating the signature) — then the metadata fields in fixed order:
    `authored_at` as RFC 3339 UTC with a literal `Z` suffix, then
    `algorithm`, then `key_id`, then `ledger_binding_id`. Every field is
    UTF-8 length-prefixed (`len:content`) exactly as
    `canonical_od_signing_message` prefixes the §21.2.1 signing segments —
    the same injectivity discipline: no ambiguous field-boundary shift.

    Reordering the ROWS yields the SAME message (sorted canonical form) —
    but changing ANY field of ANY row, `source_tag` included, or any
    metadata field, changes the message and therefore breaks the signature.

    `authored_at` is formatted at MICROSECOND precision (never truncated) —
    two records `authored_at` a few hundred milliseconds apart must not
    collapse to byte-identical messages (out-of-family Codex finding on
    this arc's own PR: second-precision formatting made sub-second-apart
    `authored_at` values indistinguishable). `AuditCutoverRecord`'s own
    validator REQUIRES a timezone-aware `authored_at`, so `.astimezone(UTC)`
    here is a genuine zone conversion, never a host-timezone-dependent
    interpretation of a naive value. Each field is prefixed by its UTF-8
    BYTE length, not its Python character count (out-of-family Codex
    finding: a non-ASCII field's character count understates its encoded
    byte length, breaking cross-implementation parsing) — computed by
    encoding first, then prefixing the encoded length.
    """
    sorted_rows = sorted(
        record.rows, key=lambda row: (row.source_tag.encode(), row.entry_hash.encode())
    )
    parts: list[str] = [str(record.schema_version)]
    for row in sorted_rows:
        parts.extend(
            (row.source_tag, row.tenant_scope, row.entry_hash, row.verification_disposition.value)
        )
    parts.extend(
        (
            record.authored_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
            record.algorithm.value,
            record.key_id,
            record.ledger_binding_id,
        )
    )
    encoded_parts = (part.encode("utf-8") for part in parts)
    return b"|".join(f"{len(encoded)}:".encode() + encoded for encoded in encoded_parts)


def sign_cutover_record(record: AuditCutoverRecord, *, backend: SigningBackend) -> bytes:
    """Sign `record` via `backend` — the same `C-CP-20 §20.2.1` `SigningBackend`
    protocol §21.2.1 signing uses, over `canonical_cutover_record_message`,
    at the fixed `"DEPLOYMENT_BOUND"` key-period projection.

    Raises `CutoverRecordValidationError` when `backend.algorithm` disagrees
    with `record.algorithm` — mirrors `sign_audit_entry`'s algorithm-
    disagreement guard: a backend must not attest a record under an
    algorithm other than the one the record declares.
    """
    if backend.algorithm != record.algorithm.value:
        raise CutoverRecordValidationError(
            f"backend.algorithm={backend.algorithm!r} disagrees with the "
            f"record's declared algorithm={record.algorithm.value!r} (OD "
            "spec v1.34 §21.2.2 row 4)"
        )
    message = canonical_cutover_record_message(record)
    return backend.sign(message=message, key_id=record.key_id, key_period=_RECORD_KEY_PERIOD)


def verify_cutover_record_signature(
    record: AuditCutoverRecord, signature: bytes, *, backend: SigningBackend
) -> bool:
    """Verify `signature` over `record` via `backend` — the read-side mirror
    of `sign_cutover_record`. Returns the backend's raw boolean verdict; the
    U-OD-55 caller (`verify_per_family_chains`) is responsible for raising
    the typed taxonomy over a `False` result or a backend error.
    """
    message = canonical_cutover_record_message(record)
    return backend.verify(
        message=message, signature=signature, key_id=record.key_id, key_period=_RECORD_KEY_PERIOD
    )

"""OD-local audit-ledger composition types — U-OD-00.

Implements C-OD-14 §14.5 (audit-ledger schema + 8-field SHA-256 composition);
ADR-D5 v1.3 §1.4 / §1.4.1 (audit-ledger cryptographic shape — the `audit.*` /
`audit.signature.*` namespaces); C-OD-21 §21.2 (the 3-value
`audit.signature.algorithm` set).

U-OD-00 is the single OD audit-ledger-type carrier — an L1 anchor (it consumes
`CellID` from U-OD-01; `Depends on: [U-OD-01]`). The records here are consumed
at U-OD-30's `sign_audit_entry` / `verify_hash_chain_integrity` signature
positions via the `[U-OD-00]` edge.

`AuditPayload` / `AuditLedger` / `AuditLedgerEntry` / `AuditSignatureAttributes`
/ `SignatureAlgorithm` are **OD-axis-local** — they reside in the OD package,
NOT in `harness-core` and NOT imported from the IS axis. The OD audit ledger
*composes against* the IS-exported `StateLedgerEntry` shape (C-IS-10 §10.1); the
IS composition surface here is the `StateLedgerEntryRef` opaque marker, resolved
at U-OD-30's cross-axis IS edge — not an IS-exported `AuditLedger` type.

Authority: Implementation_Plan_Operational_Discipline_v2_7.md §3.0 U-OD-00
(v2.7 carrier-defect micro-revision — `.harness/class_1_tension_u_od_00_carrier_defects.md`);
Spec_Operational_Discipline_v1_2.md C-OD-14 §14.5 + C-OD-21 §21.2 (preserved
verbatim into v1.3); ADR-D5 v1.3 §1.4 / §1.4.1.
"""

from __future__ import annotations

from enum import StrEnum
from typing import NewType

from pydantic import BaseModel, ConfigDict

from harness_od.observability_matrix import CellID

__all__ = [
    "AuditLedger",
    "AuditLedgerEntry",
    "AuditPayload",
    "AuditSignatureAttributes",
    "SignatureAlgorithm",
    "StateLedgerEntryRef",
]

StateLedgerEntryRef = NewType("StateLedgerEntryRef", str)
"""Opaque reference to the IS-exported F2 state-ledger entry shape.

A marker `str`-newtype: U-OD-00 names the composition position but does not
import the IS `StateLedgerEntry` type. The concrete IS type resolves at
U-OD-30's cross-axis IS edge (C-IS-10 §10.1).
"""


class SignatureAlgorithm(StrEnum):
    """The 3 admissible audit-signature algorithms (C-OD-21 §21.2, verbatim).

    `audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}` — Ed25519
    default; operator-tunable `audit_signature_algorithm` axis per §21.2 /
    ADR-D5 v1.3 §1.4.1. Closed at cardinality 3. Moved to U-OD-00 from U-OD-30
    at OD plan v2.7 (D-1 — dependency-cycle resolution).
    """

    ED25519 = "ed25519"
    ECDSA_P256 = "ecdsa-p256"
    RSA_PSS_2048 = "rsa-pss-2048"


class AuditPayload(BaseModel):
    """The signable core of one audit-ledger entry (C-OD-14 §14.5).

    Composes against the IS-exported `StateLedgerEntry` shape and adds the
    `audit.*` namespace per ADR-D5 v1.3 §1.4. The pre-signature content over
    which U-OD-30's `sign_audit_entry` computes the signature.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_core: StateLedgerEntryRef
    """F2 6-field entry shape, IS-exported (C-IS-10 §10.1) — opaque marker."""

    audit_namespace_attrs: dict[str, str]
    """`audit.*` namespace attributes per C-OD-14 §14.5."""

    prior_entry_hash: str
    """SHA-256 hash-chain link per the C-IS-13 §13.5 discipline."""


class AuditSignatureAttributes(BaseModel):
    """The 4-attribute `audit.signature.*` set (ADR-D5 v1.3 §1.4.1 / §21.2).

    Declared at U-OD-00 (moved from U-OD-30 per Q-R5-3 — single audit-type
    carrier). Exactly the four `audit.signature.*` namespace attributes; no
    field beyond what §21.2 / ADR-D5 §1.4.1 commit (OD plan v2.7 D-3).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    audit_signature_value: str
    """`audit.signature.value`."""

    audit_signature_algorithm: SignatureAlgorithm
    """`audit.signature.algorithm`."""

    audit_signature_key_id: str
    """`audit.signature.key_id`."""

    audit_signature_key_period: str
    """`audit.signature.key_period`."""


class AuditLedgerEntry(BaseModel):
    """One signed, hash-chained audit-ledger entry (C-OD-14 §14.5)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    payload: AuditPayload
    signature_attrs: AuditSignatureAttributes
    entry_hash: str
    """SHA-256 over `payload` per the C-OD-14 §14.5 field-ordering."""


class AuditLedger(BaseModel):
    """An ordered, hash-chained sequence of signed audit entries (C-OD-14 §14.5).

    Well-formedness invariant: `entries[i].payload.prior_entry_hash ==
    entries[i-1].entry_hash` for all `i > 0`. U-OD-00 declares the shape and
    documents the invariant; verification is U-OD-30's
    `verify_hash_chain_integrity` — the carrier does not enforce it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entries: tuple[AuditLedgerEntry, ...]
    cell_id: CellID
    """U-OD-01 cell key — multi-tenant cells only (cell-7, cell-8)."""

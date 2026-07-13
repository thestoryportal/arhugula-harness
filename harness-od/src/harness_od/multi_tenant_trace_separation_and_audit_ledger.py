"""Per-tenant trace separation + cryptographic audit ledger composition — U-OD-30.

Implements C-OD-21 §21.1 (per-tenant trace separation — tenant.id attribute +
per-tenant OTLP routing or per-tenant backend partition), §21.2 (cryptographic
audit ledger composition — the 4 `audit.signature.*` attributes + 3 admissible
signature algorithms per ADR-D5 v1.3 §1.4.1), §21.3 (multi-tenant cell
composition — cells 7, 8 only); OD spec v1.31 C-OD-24 §24.7 (the
`audit.rotation_correlation_id` two-row dual-signature rotation pattern).

`TenantSeparationStrategy` enumerates the 2 per-tenant separation strategies.
`PerTenantSeparation` carries, for one multi-tenant cell, the cell's separation
strategy + the `tenant.id` resource-attribute commitment.
`PER_TENANT_SEPARATION_BINDINGS` declares one binding per multi-tenant cell —
exactly 2 entries (cell-7, cell-8). `sign_audit_entry` produces the 4-attribute
`AuditSignatureAttributes` set over an `AuditPayload`;
`verify_hash_chain_integrity` walks an `AuditLedger`'s hash chain;
`assert_tenant_id_on_every_span_at_multi_tenant_cells` enforces the §21.1
per-span tenant.id invariant at cells 7/8. `sign_rotation_pair` produces the
`audit.rotation_correlation_id`-joined sibling pair for a `secret_rotation_event`
where the rotating secret IS the audit-signing key (ADR-D5 §1.4 "Key-period
model for rotation"); `verify_rotation_pairs` walks a ledger's rotation-tagged
entries per the ADR's external-auditor verification semantics (OD spec v1.31
§24.7 steps 1-4).

Carrier resolution. `AuditPayload` / `AuditLedger` / `AuditSignatureAttributes` /
`SignatureAlgorithm` resolve to the U-OD-00 carrier (`audit_ledger_types`) via
the within-axis `[U-OD-00]` edge — `SignatureAlgorithm` was moved to U-OD-00 at
OD plan v2.7 (D-1, dependency-cycle resolution). `SpanRef` resolves to the
U-OD-04 OTel-handle alias family (`otel_genai_base`) via the `[U-OD-04]` edge.
`CellID` resolves to U-OD-01 (`observability_matrix`).

Cross-axis composition (resolves at sub-phase 7c — NOT imported here). The
audit-ledger composition has three cross-axis IS/CP edges per OD plan v2.1
§3.7.4 "Cross-axis dependency resolution": IS C-IS-10 §10.5 (Tier-5 audit
ledger durability), IS C-IS-10 §10.3 (hash-chain integrity primitive), CP
C-CP-20 §20.4 (audit namespace 7-attribute schema). These resolve to the
IS-exported `StateLedgerEntry` shape + hash-chain discipline (NOT to an
`AuditLedger` type — `AuditLedger` is OD-axis-local) and the CP-emitted audit
namespace; per U-OD-34 / CXA v2.1 the edge wiring lands at 7c. `verify_hash_
chain_integrity` here is the OD-side hash-chain walk over OD-local `AuditLedger`
entries; it composes with the IS C-IS-10 §10.3 primitive at 7c.

Authority: Implementation_Plan_Operational_Discipline_v2_7.md §3.7.4 U-OD-30
(v2.7 SignatureAlgorithm-note delta — `SignatureAlgorithm` declared at U-OD-00,
imported here via `[U-OD-00]`); v2.6 §3.7.4 (M-1 type re-point — `SpanRef` to
U-OD-04, `AuditPayload`/`AuditLedger` to U-OD-00, `AuditSignatureAttributes`
moved to U-OD-00 per Q-R5-3); v2.5 §3.7.4 (`SignatureAlgorithm` 3-value
conformance); v2.1 §3.7.4 (base unit body);
Spec_Operational_Discipline_v1_2.md §21 C-OD-21 §21.1 / §21.2 / §21.3
(preserved verbatim into v1.4 per v1.4 §0); ADR-D5 v1.3 §1.4 / §1.4.1.

Depends on: [U-OD-01, U-OD-02, U-OD-28, U-OD-04, U-OD-00] (within-axis) +
[U-IS-NN (C-IS-10 §10.5), U-IS-NN (C-IS-10 §10.3), U-CP-NN (C-CP-20 §20.4)]
(cross-axis — resolve at 7c).
"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Literal

from harness_core import DeploymentSurface, PersonaTier
from pydantic import BaseModel, ConfigDict

from harness_od.audit_ledger_types import (
    AuditLedger,
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.observability_matrix import CellID
from harness_od.otel_genai_base import SpanRef

__all__ = [
    "AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER",
    "PER_TENANT_SEPARATION_BINDINGS",
    "ROTATION_CORRELATION_ID_ATTR",
    "HashChainBreach",
    "PerTenantSeparation",
    "RotationPairIntegrityBreach",
    "TenantIdMissingViolation",
    "TenantSeparationStrategy",
    "sign_audit_entry",
    "sign_rotation_pair",
    "verify_hash_chain_integrity",
    "verify_rotation_pairs",
]


# --- §0.8 inline error arms ------------------------------------------------


class HashChainBreach(Exception):  # noqa: N818 — name is the U-OD-30 plan signature verbatim
    """Raised when an `AuditLedger`'s hash chain is broken (C-OD-21 §21.2).

    The `Result<(), HashChainBreach>` error arm of `verify_hash_chain_integrity`
    — a ledger is well-formed iff each entry's `prior_entry_hash` links to the
    predecessor's `entry_hash`. Stack is Pydantic v2 + stdlib, no `Result`
    framework pull (CLAUDE.md §3.2 / I-6).
    """


class RotationPairIntegrityBreach(Exception):  # noqa: N818 — mirrors HashChainBreach naming
    """Raised when an `audit.rotation_correlation_id` sibling pair is malformed.

    The `Result<(), RotationPairIntegrityBreach>` error arm of
    `verify_rotation_pairs` (OD spec v1.31 C-OD-24 §24.7) — a rotation-tagged
    entry set is well-formed iff every distinct `audit.rotation_correlation_id`
    value is carried by exactly two entries, each entry's stored `entry_hash`
    matches its recomputed hash, the pair's `key_period` values are
    consecutive integers with the earlier entry signed by the outgoing key,
    the key ids differ, and chain-hash continuity holds across the pair.
    """


class TenantIdMissingViolation(Exception):  # noqa: N818 — U-OD-30 plan signature verbatim
    """Raised when a span at a multi-tenant cell lacks the tenant.id attribute.

    The `Result<(), TenantIdMissingViolation>` error arm of
    `assert_tenant_id_on_every_span_at_multi_tenant_cells` — C-OD-21 §21.1
    commits a `tenant.id` resource attribute on every span at cells 7/8.
    """


# --- §21.1 per-tenant trace separation -------------------------------------


class TenantSeparationStrategy(StrEnum):
    """The 2 per-tenant trace-separation strategies (C-OD-21 §21.1, verbatim).

    Exactly 2 values per §21.1 — the self-hosted multi-tenant variant routes
    per tenant at the OTLP collector; the managed-cloud variant partitions per
    tenant at backend ingestion.
    """

    PER_TENANT_OTLP_COLLECTOR_ROUTING = "PER_TENANT_OTLP_COLLECTOR_ROUTING"
    """cells 7, 8 self-hosted variant — per-tenant OTLP collector routing."""

    PER_TENANT_BACKEND_PARTITION = "PER_TENANT_BACKEND_PARTITION"
    """cells 7, 8 managed-cloud variant — per-tenant backend partition."""


class PerTenantSeparation(BaseModel):
    """Per-tenant trace separation committed for one multi-tenant cell (§21.1).

    `cell_id` is one of {cell-7, cell-8}. `tenant_id_attribute` is the
    `"tenant.id"` resource-attribute name byte-exact per §21.1.
    `cross_tenant_aggregation_forbidden` is `True` per §21.1 — composes with
    U-OD-31 enforcement.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    cell_id: CellID
    strategy: TenantSeparationStrategy
    tenant_id_attribute: Literal["tenant.id"]
    cross_tenant_aggregation_forbidden: bool


def _cell(pt: PersonaTier, ds: DeploymentSurface) -> CellID:
    """Construct a `CellID` — local helper mirroring `per_cell_backend_class`."""
    return CellID(persona_tier=pt, deployment_surface=ds)


#: cell-7 — multi-tenant-compliance x self-hosted-server.
_CELL_7 = _cell(PersonaTier.MULTI_TENANT_COMPLIANCE, DeploymentSurface.SELF_HOSTED_SERVER)
#: cell-8 — multi-tenant-compliance x managed-cloud.
_CELL_8 = _cell(PersonaTier.MULTI_TENANT_COMPLIANCE, DeploymentSurface.MANAGED_CLOUD)

#: Per-tenant separation bindings — exactly 2 entries, cells 7 and 8 only
#: (C-OD-21 §21.3 multi-tenant cell composition). cell-7 routes per-tenant at
#: the OTLP collector (self-hosted variant); cell-8 partitions per-tenant at
#: backend ingestion (managed-cloud variant).
PER_TENANT_SEPARATION_BINDINGS: dict[CellID, PerTenantSeparation] = {
    _CELL_7: PerTenantSeparation(
        cell_id=_CELL_7,
        strategy=TenantSeparationStrategy.PER_TENANT_OTLP_COLLECTOR_ROUTING,
        tenant_id_attribute="tenant.id",
        cross_tenant_aggregation_forbidden=True,
    ),
    _CELL_8: PerTenantSeparation(
        cell_id=_CELL_8,
        strategy=TenantSeparationStrategy.PER_TENANT_BACKEND_PARTITION,
        tenant_id_attribute="tenant.id",
        cross_tenant_aggregation_forbidden=True,
    ),
}

#: The set of multi-tenant cells — the domain of `PER_TENANT_SEPARATION_BINDINGS`.
_MULTI_TENANT_CELLS: frozenset[CellID] = frozenset({_CELL_7, _CELL_8})


# --- §21.2 cryptographic audit ledger composition --------------------------

#: §21.2 + C-IS-10 §10.5 — audit-signature attestation is required at the
#: Tier-5 per-tenant audit ledger.
AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER: bool = True


def sign_audit_entry(
    payload: AuditPayload,
    key_id: str,
    algo: SignatureAlgorithm,
) -> AuditSignatureAttributes:
    """Sign an audit-ledger entry payload (C-OD-21 §21.2).

    Produces an `AuditSignatureAttributes` (the 4-attribute `audit.signature.*`
    set) over `payload` with the operator-selected `algo`. Raises `ValueError`
    at function precondition when `key_id` is missing (empty) — §21.2 requires
    a key identifier for the signing operation.

    The concrete cryptographic signing operation (key custody — HSM / cloud KMS
    / OS keychain) is deferred per ADR-D5 v1.3 §1.4.1 + §21.2 "Deferred to
    implementation discretion"; this library surface produces the typed
    `audit.signature.*` attribute record. The signature value is computed by the
    deployment-bound signing backend; here it is the deterministic placeholder
    a Phase-2 composition root replaces with the live signing call.
    """
    if not key_id:
        raise ValueError(
            "sign_audit_entry precondition violated: key_id is required "
            "(C-OD-21 §21.2 — audit.signature.key_id)"
        )
    # The live signing backend (HSM / KMS / keystore) is wired at a Phase-2
    # composition root; the library surface produces the typed attribute set.
    return AuditSignatureAttributes(
        audit_signature_value=f"unsigned:{key_id}:{payload.prior_entry_hash}",
        audit_signature_algorithm=algo,
        audit_signature_key_id=key_id,
        audit_signature_key_period="DEPLOYMENT_BOUND",
    )


def verify_hash_chain_integrity(ledger: AuditLedger) -> None:
    """Verify an audit ledger's hash-chain integrity (C-OD-21 §21.2).

    Returns `None` (the `Ok(())` arm) when the ledger is well-formed — every
    entry's stored `entry_hash` matches a fresh `compute_entry_hash` recompute
    over its own `payload` (content integrity), and each entry's
    `payload.prior_entry_hash` links to the predecessor's `entry_hash` for all
    `i > 0` (chain linkage). Raises `HashChainBreach` (the `Err` arm) at the
    first violation, content check before linkage check. Composes with the IS
    C-IS-10 §10.3 hash-chain integrity primitive (cross-axis IS edge — resolves
    at 7c).

    Content-integrity check mirrors `verify_rotation_pairs` (§24.7) below: a
    payload mutated in place (bad migration, bug, compromised writer) with its
    `entry_hash` left untouched is caught here — linkage alone cannot detect
    this, since a tampered entry's own stored hash never participates in the
    predecessor-link comparison.
    """
    entries = ledger.entries
    for i, entry in enumerate(entries):
        recomputed = compute_entry_hash(entry.payload)
        if recomputed != entry.entry_hash:
            raise HashChainBreach(
                f"audit-ledger entry {i} content integrity violated: stored "
                f"entry_hash={entry.entry_hash!r} does not match recomputed "
                f"hash={recomputed!r} over the entry's payload — payload "
                "tampered without recomputing entry_hash (C-OD-21 §21.2)"
            )
    for i in range(1, len(entries)):
        prior_hash = entries[i].payload.prior_entry_hash
        predecessor_hash = entries[i - 1].entry_hash
        if prior_hash != predecessor_hash:
            raise HashChainBreach(
                f"audit-ledger hash chain broken at entry {i}: "
                f"prior_entry_hash={prior_hash!r} != predecessor entry_hash="
                f"{predecessor_hash!r} (C-OD-21 §21.2 / C-IS-10 §10.3)"
            )
    return None


# --- C-OD-24 §24.7 rotation-pair dual-signature pattern (OD spec v1.31) ----

ROTATION_CORRELATION_ID_ATTR = "audit.rotation_correlation_id"
"""The §24.7 namespace-attribute name carried inside `audit_namespace_attrs`."""


def sign_rotation_pair(
    *,
    outgoing_entry_core: StateLedgerEntryRef,
    outgoing_prior_entry_hash: str,
    incoming_entry_core: StateLedgerEntryRef,
    outgoing_key_id: str,
    outgoing_key_period: int,
    incoming_key_id: str,
    incoming_key_period: int,
    algo: SignatureAlgorithm,
    outgoing_audit_namespace_attrs: dict[str, str] | None = None,
    incoming_audit_namespace_attrs: dict[str, str] | None = None,
) -> tuple[AuditLedgerEntry, AuditLedgerEntry]:
    """Produce the co-signed rotation-pair sibling entries (C-OD-24 §24.7).

    Materializes ADR-D5 §1.4's `secret_rotation_event` two-row pattern for the
    case where the rotating secret IS the audit-signing key: sibling-1 is
    signed under the outgoing key at `outgoing_key_period`; sibling-2 is
    signed under the incoming key at `incoming_key_period` and chains onto
    sibling-1 (`incoming.payload.prior_entry_hash == outgoing.entry_hash`).
    Both entries carry a freshly-generated, shared `audit.rotation_correlation_id`
    inside `audit_namespace_attrs`.

    Raises `ValueError` when `incoming_key_period != outgoing_key_period + 1`
    (periods must be consecutive) or `outgoing_key_id == incoming_key_id` (a
    rotation changes the key identity, not just the period counter).
    """
    if incoming_key_period != outgoing_key_period + 1:
        raise ValueError(
            "sign_rotation_pair precondition violated: incoming_key_period "
            f"({incoming_key_period}) must equal outgoing_key_period "
            f"({outgoing_key_period}) + 1 (C-OD-24 §24.7)"
        )
    if outgoing_key_id == incoming_key_id:
        raise ValueError(
            "sign_rotation_pair precondition violated: outgoing_key_id and "
            "incoming_key_id must differ (C-OD-24 §24.7)"
        )

    correlation_id = str(uuid.uuid4())

    outgoing_attrs = dict(outgoing_audit_namespace_attrs or {})
    outgoing_attrs[ROTATION_CORRELATION_ID_ATTR] = correlation_id
    outgoing_payload = AuditPayload(
        entry_core=outgoing_entry_core,
        audit_namespace_attrs=outgoing_attrs,
        prior_entry_hash=outgoing_prior_entry_hash,
    )
    outgoing_entry_hash = compute_entry_hash(outgoing_payload)
    outgoing_sig = sign_audit_entry(outgoing_payload, outgoing_key_id, algo).model_copy(
        update={"audit_signature_key_period": str(outgoing_key_period)}
    )
    outgoing_entry = AuditLedgerEntry(
        payload=outgoing_payload, signature_attrs=outgoing_sig, entry_hash=outgoing_entry_hash
    )

    incoming_attrs = dict(incoming_audit_namespace_attrs or {})
    incoming_attrs[ROTATION_CORRELATION_ID_ATTR] = correlation_id
    incoming_payload = AuditPayload(
        entry_core=incoming_entry_core,
        audit_namespace_attrs=incoming_attrs,
        prior_entry_hash=outgoing_entry_hash,
    )
    incoming_entry_hash = compute_entry_hash(incoming_payload)
    incoming_sig = sign_audit_entry(incoming_payload, incoming_key_id, algo).model_copy(
        update={"audit_signature_key_period": str(incoming_key_period)}
    )
    incoming_entry = AuditLedgerEntry(
        payload=incoming_payload, signature_attrs=incoming_sig, entry_hash=incoming_entry_hash
    )

    return outgoing_entry, incoming_entry


def verify_rotation_pairs(ledger: AuditLedger) -> None:
    """Verify every `audit.rotation_correlation_id` sibling pair (C-OD-24 §24.7).

    Returns `None` (the `Ok(())` arm) when every distinct rotation-correlation
    value tags exactly two entries whose recomputed `entry_hash` matches the
    stored value, whose key periods are consecutive integers, whose key ids
    differ, and whose chain-hash continuity holds across the pair (the
    later-period sibling's `prior_entry_hash` extends the earlier-period
    sibling's `entry_hash`). Raises `RotationPairIntegrityBreach` (the `Err`
    arm) on the first violation. Entries with no `audit.rotation_correlation_id`
    attribute are ignored — non-rotation entries are unaffected, per the ADR's
    verification semantics.

    Per the ADR's "Standard chain-verification walks entries in `entry_hash`
    chain order, recomputing hashes..." — each tagged entry's stored
    `entry_hash` is recomputed from its stored `payload` via `compute_entry_hash`
    before any cross-entry check runs, so a payload mutated in place (e.g. a
    tampered `audit.*` attribute) with a stale `entry_hash` left behind is
    caught here, not just at the cross-entry `prior_entry_hash` linkage.
    """
    by_correlation: dict[str, list[AuditLedgerEntry]] = {}
    for entry in ledger.entries:
        correlation_id = entry.payload.audit_namespace_attrs.get(ROTATION_CORRELATION_ID_ATTR)
        if not correlation_id:
            continue
        try:
            uuid.UUID(correlation_id)
        except ValueError as exc:
            raise RotationPairIntegrityBreach(
                f"audit.rotation_correlation_id={correlation_id!r} is not a "
                "canonical UUID string (C-OD-24 §24.7 declares this attribute "
                "as a UUID string or absent)"
            ) from exc
        by_correlation.setdefault(correlation_id, []).append(entry)

    for correlation_id, tagged in by_correlation.items():
        if len(tagged) != 2:
            raise RotationPairIntegrityBreach(
                f"audit.rotation_correlation_id={correlation_id!r} tagged "
                f"{len(tagged)} entries; the two-row rotation pattern requires "
                "exactly 2 (C-OD-24 §24.7)"
            )
        for entry in tagged:
            recomputed = compute_entry_hash(entry.payload)
            if recomputed != entry.entry_hash:
                raise RotationPairIntegrityBreach(
                    f"audit.rotation_correlation_id={correlation_id!r}: stored "
                    f"entry_hash={entry.entry_hash!r} does not match recomputed "
                    f"hash={recomputed!r} over the entry's payload — payload "
                    "tampered without recomputing entry_hash (C-OD-24 §24.7)"
                )
        entry_a, entry_b = tagged
        try:
            period_a = int(entry_a.signature_attrs.audit_signature_key_period)
            period_b = int(entry_b.signature_attrs.audit_signature_key_period)
        except ValueError as exc:
            raise RotationPairIntegrityBreach(
                f"audit.rotation_correlation_id={correlation_id!r}: key_period "
                "must be integer-valued for rotation-tagged entries (C-OD-24 §24.7)"
            ) from exc
        sibling_1, sibling_2 = (entry_a, entry_b) if period_a < period_b else (entry_b, entry_a)
        period_1, period_2 = sorted((period_a, period_b))
        if period_2 != period_1 + 1:
            raise RotationPairIntegrityBreach(
                f"audit.rotation_correlation_id={correlation_id!r}: key periods "
                f"{period_1} and {period_2} are not consecutive (C-OD-24 §24.7)"
            )
        if (
            sibling_1.signature_attrs.audit_signature_key_id
            == sibling_2.signature_attrs.audit_signature_key_id
        ):
            raise RotationPairIntegrityBreach(
                f"audit.rotation_correlation_id={correlation_id!r}: outgoing and "
                "incoming key_id must differ (C-OD-24 §24.7)"
            )
        if sibling_2.payload.prior_entry_hash != sibling_1.entry_hash:
            raise RotationPairIntegrityBreach(
                f"audit.rotation_correlation_id={correlation_id!r}: chain-hash "
                "continuity broken across the rotation boundary — "
                f"sibling_2.payload.prior_entry_hash={sibling_2.payload.prior_entry_hash!r} "
                f"!= sibling_1.entry_hash={sibling_1.entry_hash!r} (C-OD-24 §24.7)"
            )
    return None


def assert_tenant_id_on_every_span_at_multi_tenant_cells(
    span: SpanRef,
    cell_id: CellID,
) -> None:
    """Assert a span carries the tenant.id attribute at multi-tenant cells (§21.1).

    Returns `None` (the `Ok(())` arm) when `cell_id` is not a multi-tenant cell
    (the invariant applies only at cells 7/8), or when the span carries a
    non-empty `tenant.id` attribute. Raises `TenantIdMissingViolation` (the
    `Err` arm) when a span at cell-7 or cell-8 lacks the `tenant.id` attribute.

    `span` is an OTel-SDK span handle (`SpanRef`, U-OD-04 carrier). The
    attribute inspection reads the OTel span's attribute map; with no live span
    bound the function is exercised against an attribute snapshot in tests. The
    live span-attribute read is wired at a Phase-2 composition root.
    """
    if cell_id not in _MULTI_TENANT_CELLS:
        return None
    attributes = getattr(span, "attributes", None)
    tenant_id = None if attributes is None else attributes.get("tenant.id")
    if not tenant_id:
        raise TenantIdMissingViolation(
            f"span at multi-tenant cell {cell_id.persona_tier} x "
            f"{cell_id.deployment_surface} lacks the 'tenant.id' attribute "
            f"(C-OD-21 §21.1 — per-tenant trace separation)"
        )
    return None

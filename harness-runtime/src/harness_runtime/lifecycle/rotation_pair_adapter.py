"""U-RT-147 — composition-root adapter: the real OD §24.8 accessor behind the
CP-owned `RotationPairEvidenceProvider` Protocol (Runtime spec v1.105 §13.6;
CP spec v1.105 §2).

`harness-cp` cannot import `harness-od` (the OD→CP canonical direction plus
the `SigningBackend` import cycle), so `verify_rotation_6_steps`'s
`PROBE_VERIFY_AT_READ` step takes its OD-anchored evidence lookup as an
injected `RotationPairEvidenceProvider`. THIS module is the composition
root's side of that seam — `harness-runtime` imports both packages, wraps
`harness_od.multi_tenant_trace_separation_and_audit_ledger.
find_rotation_pair_evidence` (OD spec v1.35 §24.8) in the CP result
boundary, and maps the field-for-field-identical OD DTO to the CP-owned
`RotationPairEvidence` type.

**Adapter + factory ONLY — NO production call site (out-of-family review
[P2], mirrors U-RT-138's own scope narrowing).** Unlike U-RT-138 (which
injects `AuditWalkVerifier` into a REAL existing `harness-inspect`
invocation), `verify_rotation_6_steps` has ZERO production callers today
(CP plan v2.41 U-CP-45 criterion #6's explicit scope fence) — there is no
live call site to inject this adapter into without either constructing it
dead or adding the very production caller this arc and its siblings
explicitly defer. This module provides ONLY the adapter class + a
composition-root FACTORY function — available for a FUTURE caller, not
invoked by anything this leg adds.

The taxonomy mapping:

- OD `RotationPairIntegrityBreach`         → CP `RotationPairIntegrityBreach`
  (re-raised, message-preserving — a genuine tamper signal, never folded
  into a "false" evidence result).
- An OD-side ledger-load/lookup infrastructure failure (NOT a tamper
  signal) → CP `RotationPairEvidenceUnavailableError` (availability is
  never a verdict).
- ANY OTHER raise propagates UNWRAPPED as a defect, never misclassified as
  rerunnable infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass

from harness_cp.rotation_pair_verification import (
    KeyIdentityResolver,
    RotationPairEvidenceProvider,
)
from harness_cp.rotation_pair_verification import (
    RotationPairEvidence as CpRotationPairEvidence,
)
from harness_cp.rotation_pair_verification import (
    RotationPairIntegrityBreach as CpRotationPairIntegrityBreach,
)
from harness_od.audit_ledger_types import AuditLedger
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    RotationPairIntegrityBreach as OdRotationPairIntegrityBreach,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    find_rotation_pair_evidence,
)

from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    canonical_kms_key_identity,
)

__all__ = ["OdRotationPairEvidenceAdapter", "build_rotation_pair_evidence_provider"]


@dataclass(frozen=True, slots=True)
class OdRotationPairEvidenceAdapter:
    """`RotationPairEvidenceProvider` Protocol conformer over the real OD
    §24.8 accessor.

    The audit ledger to query is captured at construction (the composition
    root resolves it from wherever it wires the audit-ledger read for this
    scope); `evidence_for` supplies only the correlation id per invocation.
    """

    ledger: AuditLedger

    def evidence_for(self, correlation_id: str) -> CpRotationPairEvidence:
        try:
            od_evidence = find_rotation_pair_evidence(self.ledger, correlation_id)
        except OdRotationPairIntegrityBreach as exc:
            raise CpRotationPairIntegrityBreach(str(exc)) from exc
        # Any other raise (TypeError/KeyError/programming error) propagates
        # unwrapped as a defect — the CP result-boundary contract. There is
        # no separate OD-side "infrastructure unavailable" exception class
        # for this accessor today (unlike the audit-walk's backend
        # resolver) — `RotationPairEvidenceUnavailableError` is reserved
        # here for a future OD-side availability signal + the correlation-id
        # echo-check mismatch this adapter's caller (`verify_rotation_6_steps`)
        # performs on the returned DTO.
        return CpRotationPairEvidence(
            correlation_id=od_evidence.correlation_id,
            pair_present=od_evidence.pair_present,
            outgoing_key_period=od_evidence.outgoing_key_period,
            incoming_key_period=od_evidence.incoming_key_period,
            outgoing_key_id=od_evidence.outgoing_key_id,
            incoming_key_id=od_evidence.incoming_key_id,
            signatures_verified=od_evidence.signatures_verified,
        )


def build_rotation_pair_evidence_provider(ledger: AuditLedger) -> RotationPairEvidenceProvider:
    """Composition-root factory — constructs the adapter over a supplied OD
    audit ledger. Available for a FUTURE caller; not invoked by anything in
    this leg (no production call site exists for `verify_rotation_6_steps`
    yet, per the fork's own scope fence)."""
    return OdRotationPairEvidenceAdapter(ledger=ledger)


def build_key_identity_resolver_from_mapping(mapping: dict[str, str]) -> KeyIdentityResolver:
    """Composition-root factory — a minimal `KeyIdentityResolver` over an
    explicit `key_id -> physical identity` mapping (e.g. the operator-
    configured signing-key identity mapping, Runtime spec v1.105 §13.6 row
    1; `AwsKmsSigningBackend.key_arns` is the reference shape, ADR-D8).
    This factory does NOT fabricate a resolver where none exists — the
    composition root must supply a real mapping; an empty mapping
    constructs a resolver that raises `KeyError` for any lookup, which
    propagates unwrapped (never silently treated as a match).

    Mapping VALUES are canonicalized via `canonical_kms_key_identity`
    (out-of-family review round-1 [P1] correction) — without this, two
    logical `key_id`s mapped to different SPELLINGS of the same physical
    KMS key (a full ARN vs. the bare key ID/UUID) would compare as
    DIFFERENT identities, letting the physical-key-distinctness check
    (CP spec v1.105 §2 row 5) falsely accept a rotation that never
    actually changed the physical signing key."""
    return _MappingKeyIdentityResolver(mapping=mapping)


@dataclass(frozen=True, slots=True)
class _MappingKeyIdentityResolver:
    """`KeyIdentityResolver` Protocol conformer over an explicit mapping.

    `physical_identity_for` returns the CANONICALIZED form (via
    `canonical_kms_key_identity`), not the raw mapped string, so two
    entries mapped to different spellings of the same physical key
    (an ARN vs. its bare key-ID tail) compare equal."""

    mapping: dict[str, str]

    def physical_identity_for(self, key_id: str) -> str:
        return canonical_kms_key_identity(self.mapping[key_id])

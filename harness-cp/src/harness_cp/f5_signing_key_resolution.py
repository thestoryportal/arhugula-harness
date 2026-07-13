"""F5 signing-key resolution for `MULTI_TENANT_COMPLIANCE` — U-CP-44.

Implements C-CP-20 §20.3.1 (the multi-tenant-compliance audit-signing-key
resolution + lifecycle). Declares the `SigningKeyScope` / `SigningKeyHandle`
records, the `SecretScopeKind` / `KeyRotationState` / `SigningKeyResolutionError`
enums, the `SigningKeyResult` discriminated result, and the `resolve_signing_key`
/ `sign_audit_entry` / `verify_audit_entry_signature` functions.

Signing keys are **MULTI_TENANT_COMPLIANCE-exclusive** per C-CP-20 §20.3.1 —
`resolve_signing_key` returns the `SCOPE_UNAUTHORIZED` error for any lower
persona tier. Secret retrieval delegates to the U-AS-20 `fetch_secret` surface;
this unit does NOT implement secret-retrieval mechanics (AS owns).

The audit-entry types are the CP-spec-owned `CPAuditLedgerEntry` /
`CPSignedAuditLedgerEntry` (U-CP-14) — the v2.1 U-CP-44 body's
`AuditLedgerEntry` / `SignedAuditLedgerEntry` names are reconciled to the
CP-distinct names per the Implementation Plan v2.9 §0.5.1 name-collision
resolution (binding for all forward CP units; U-CP-44 consumes the renamed
types — no import of, no reconciliation with, the OD-local `AuditLedgerEntry`).

The concrete signature algorithm (Ed25519 vs ECDSA-P256 vs other) is deferred to
implementation discretion per spec §20.3.1; `sign_audit_entry` records the
algorithm token on the produced `CPSignedAuditLedgerEntry`.

**Real signing is not yet reachable from CP — fails loud, does not fake
success.** `SigningKeyHandle.key_secret_ref` is a U-AS-20 `SecretRef` — per AS
spec C-AS-05 §5.4 this is an *opaque* handle with "no value-accessor API";
resolving it to literal key bytes is a tier-specific mechanism that lives
downstream of `fetch_secret` (env-var read / in-sandbox HTTP bootstrap), not
reachable from the CP axis. But C-CP-20 §20.3.1's `verify_chain` pseudocode
requires a REAL check — "verify audit.signature.value against the key valid
at entry.audit.signature.key_period" — this is not deferred-to-discretion the
way the concrete signature *algorithm* choice is (§20.4's "Deferred to
implementation discretion" list names only the algorithm/library binding, not
whether verification is real). Unlike the OD-local sibling
`harness_od.multi_tenant_trace_separation_and_audit_ledger.sign_audit_entry`
(C-OD-21 §21.2 — which never exposes a function claiming to verify a
signature at all, only hash-chain content-integrity), this module's
`verify_audit_entry_signature` return type explicitly promises a
`VERIFIED`/`SIGNATURE_MISMATCH` security verdict. Returning `VERIFIED` from an
unkeyed hash match anyone with ledger-write access could forge is a false
attestation — worse than the pre-fix key-id-only check because it looks like
real verification landed. So both `sign_audit_entry` and
`verify_audit_entry_signature` raise `AuditSigningBackendUnavailableError`
instead: MULTI_TENANT_COMPLIANCE audit-signature tamper-evidence is presently
**unavailable**, not faked, pending a key-material-resolution seam from a
deployment-bound signing backend (HSM / KMS / vault) into this unit — the same
"live signing backend ... wired at a deployment-time composition root" shape
ADR-D5 v1.3 §1.4.1 already ratifies for OD. There are zero production callers
of either function today (confirmed by repo-wide grep — only the
`SigningKeyHandle` *type* is consumed, at `five_axis_composition.py`), so this
is a latent gap, not a live regression; operator-ratified 2026-07-13.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2 U-CP-44 (preserved
verbatim into v2.3/v2.4 — symbolic enum reference only; v2.9 §0.5.1
audit-entry name reconciliation); Spec_Control_Plane_v1_2.md §20 C-CP-20
§20.3, §20.3.1, §20.4 (preserved verbatim into v1.3); ADR-D5 v1.3 §1.4 /
§1.4.1; CLAUDE.md §3.2 (hand-rolled crypto composition — NO framework; the
composition/wiring here is hand-rolled, not a from-scratch crypto primitive —
this module never implements its own asymmetric-cipher math).
"""

from __future__ import annotations

from enum import StrEnum

from harness_as import SandboxTier, SecretRef, SecretScope, fetch_secret
from harness_core import PersonaTier
from pydantic import BaseModel, ConfigDict

from harness_cp.per_step_override_evaluator import (
    CPAuditLedgerEntry,
    CPSignedAuditLedgerEntry,
)


class SecretScopeKind(StrEnum):
    """The scope-kind of a signing-key secret (C-CP-20 §20.3.1).

    Closed at cardinality 3 — the v2.1 U-CP-44 body's decided inline-comment
    enumeration `{WORKFLOW_BOUND, TENANT_BOUND, FLEET_BOUND}`.
    """

    WORKFLOW_BOUND = "workflow_bound"
    TENANT_BOUND = "tenant_bound"
    FLEET_BOUND = "fleet_bound"


class KeyRotationState(StrEnum):
    """The rotation state of a signing key (C-CP-20 §20.3).

    Closed at cardinality 3. `ROTATING` is the two-row rotation-pattern
    transitional state (the `secret_rotation_event` entry is counter-signed
    under outgoing + incoming keys per §20.3).
    """

    ACTIVE = "active"
    ROTATING = "rotating"
    RETIRED = "retired"


class SigningKeyResolutionError(StrEnum):
    """A signing-key resolution failure cause (C-CP-20 §20.3.1)."""

    SECRET_FETCH_FAIL = "secret_fetch_fail"
    SCOPE_UNAUTHORIZED = "scope_unauthorized"
    KEY_RETIRED = "key_retired"


class AuditSigningBackendUnavailableError(NotImplementedError):
    """Raised by `sign_audit_entry` / `verify_audit_entry_signature`.

    Real cryptographic signing/verification against actual key material is not
    reachable from the CP axis today — see module docstring. Raised instead of
    fabricating a `VERIFIED` result, per the operator-ratified disposition
    (2026-07-13): MULTI_TENANT_COMPLIANCE audit-signature tamper-evidence is
    presently unavailable, not faked.
    """


class SigningKeyScope(BaseModel):
    """The scope a signing key is bound to (C-CP-20 §20.3.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope_kind: SecretScopeKind
    scope_identifier: str


class SigningKeyHandle(BaseModel):
    """A resolved signing-key handle (C-CP-20 §20.3.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    key_id: str
    key_secret_ref: SecretRef
    """The U-AS-20 `SecretRef` for the key material."""

    rotation_state: KeyRotationState
    acquired_at: str
    """ISO-8601 timestamp."""


class SigningKeyResult(BaseModel):
    """A `resolve_signing_key` result — `Result<SigningKeyHandle, error>`.

    Exactly one of `handle` / `error` is populated.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    handle: SigningKeyHandle | None = None
    error: SigningKeyResolutionError | None = None


class VerificationResult(StrEnum):
    """The outcome of an audit-entry signature verification (C-CP-20 §20.3.1)."""

    VERIFIED = "verified"
    SIGNATURE_MISMATCH = "signature_mismatch"


def resolve_signing_key(scope: SigningKeyScope, persona_tier: PersonaTier) -> SigningKeyResult:
    """Resolve the F5 audit-signing key for `scope` — C-CP-20 §20.3.1.

    Signing keys are MULTI_TENANT_COMPLIANCE-exclusive: any lower persona tier
    yields `Err(SCOPE_UNAUTHORIZED)`. Secret retrieval delegates to the U-AS-20
    `fetch_secret(name, scope, tier)` surface — this unit does NOT implement
    secret-retrieval mechanics. The resolved key is `ACTIVE`; rotation-state
    transitions are owned by U-CP-45's rotation pattern.
    """
    if persona_tier is not PersonaTier.MULTI_TENANT_COMPLIANCE:
        return SigningKeyResult(error=SigningKeyResolutionError.SCOPE_UNAUTHORIZED)
    secret_ref = fetch_secret(
        name=f"audit-signing-key:{scope.scope_identifier}",
        scope=SecretScope(name=scope.scope_identifier),
        tier=SandboxTier.TIER_4_FULL_VM,
    )
    return SigningKeyResult(
        handle=SigningKeyHandle(
            key_id=f"{scope.scope_kind.value}:{scope.scope_identifier}",
            key_secret_ref=secret_ref,
            rotation_state=KeyRotationState.ACTIVE,
            acquired_at="",
        )
    )


def sign_audit_entry(
    entry: CPAuditLedgerEntry,
    key: SigningKeyHandle,
    *,
    key_period: int,
) -> CPSignedAuditLedgerEntry:
    """Sign a CP audit-ledger entry under `key` (C-CP-20 §20.3.1 + §20.4).

    Raises `AuditSigningBackendUnavailableError` — real cryptographic signing
    against `key`'s actual key material is not reachable from the CP axis
    today (see module docstring); this function does not fabricate a signed
    entry. Still validates the `RETIRED`-key precondition first (a real
    signing-backend seam would need to honor it too): the signing key must be
    `ACTIVE` or `ROTATING`.
    """
    if key.rotation_state is KeyRotationState.RETIRED:
        raise ValueError("cannot sign under a RETIRED signing key (C-CP-20 §20.3)")
    raise AuditSigningBackendUnavailableError(
        "real audit-entry signing requires a key-material-resolution seam not "
        "yet wired from a deployment-bound signing backend into harness-cp "
        "(C-CP-20 §20.3.1; SecretRef is opaque per AS spec C-AS-05 §5.4)"
    )


def verify_audit_entry_signature(
    signed: CPSignedAuditLedgerEntry, key: SigningKeyHandle
) -> VerificationResult:
    """Verify a signed audit-entry's signature at read-time (C-CP-20 §20.3.1).

    Raises `AuditSigningBackendUnavailableError` — real cryptographic
    signature verification against `key`'s actual key material is not
    reachable from the CP axis today (see module docstring); this function
    does not fabricate a `VERIFIED` result.
    """
    del signed, key
    raise AuditSigningBackendUnavailableError(
        "real audit-entry signature verification requires a key-material-"
        "resolution seam not yet wired from a deployment-bound signing "
        "backend into harness-cp (C-CP-20 §20.3.1; SecretRef is opaque per "
        "AS spec C-AS-05 §5.4)"
    )

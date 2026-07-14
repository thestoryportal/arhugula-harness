"""Tests for U-CP-44 — F5 signing-key resolution (C-CP-20 §20.3.1).

Acceptance-criterion coverage:
  #1 SCOPE_UNAUTHORIZED below MTC -> test_resolve_signing_key_scope_unauthorized_below_multi_tenant
  #2 delegates to U-AS-20         -> test_resolve_delegates_to_u_as_20
  #3 rotation_state 3 values      -> test_signing_key_rotation_state_three_values

Without `backend`, `sign_audit_entry` / `verify_audit_entry_signature` raise
`AuditSigningBackendUnavailableError` — real cryptographic signing/verification
against actual key material is not reachable from the CP axis today (opaque
`SecretRef`, no value-accessor API per AS spec C-AS-05 §5.4). Operator-ratified
2026-07-13 (fail loud rather than return a false `VERIFIED` for an unkeyed
hash match — see module docstring); zero production callers exist.

With `backend` (C-CP-20 §20.2.1, spec v1.98 — the `B-22` seam), both functions
perform genuine signing/verification. `_InMemoryEd25519Backend` below is a
TEST-ONLY double proving the seam round-trips real cryptography — it makes no
claim about a production backend residence (the concrete prod-tech backend for
`multi-tenant-compliance` remains deferred per ADR-F5 §Deferred D-ADRs; see
`Spec_Control_Plane_v1_98.md`).
"""

from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from harness_as import GateLevel, SecretRef
from harness_core import PersonaTier
from harness_cp.f5_signing_key_resolution import (
    AuditSigningBackendUnavailableError,
    KeyRotationState,
    SecretScopeKind,
    SigningKeyHandle,
    SigningKeyResolutionError,
    SigningKeyScope,
    VerificationResult,
    resolve_signing_key,
    sign_audit_entry,
    verify_audit_entry_signature,
)
from harness_cp.per_step_override_evaluator import (
    CPAuditLedgerEntry,
    CPSignedAuditLedgerEntry,
)


class _InMemoryEd25519Backend:
    """TEST-ONLY `SigningBackend` double — one in-memory Ed25519 keypair.

    Proves the C-CP-20 §20.2.1 seam round-trips real cryptography without any
    claim about a production backend residence — the concrete prod-tech
    backend for `multi-tenant-compliance` remains deferred (see module docstring).
    """

    algorithm = "ed25519"

    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()

    def sign(self, *, message: bytes, key_id: str) -> bytes:
        del key_id
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str) -> bool:
        del key_id
        try:
            self._public_key.verify(signature, message)
        except InvalidSignature:
            return False
        return True


_SCOPE = SigningKeyScope(scope_kind=SecretScopeKind.TENANT_BOUND, scope_identifier="tenant-7")
_ENTRY = CPAuditLedgerEntry(
    action_id="wf||s1",  # type: ignore[arg-type]
    gate_level=GateLevel.AUTO,
    response="approve",
    timestamp="2026-05-16T00:00:00Z",
    prior_event_hash="a" * 64,
)


def test_resolve_signing_key_scope_unauthorized_below_multi_tenant() -> None:
    for tier in (PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING):
        result = resolve_signing_key(_SCOPE, tier)
        assert result.handle is None
        assert result.error is SigningKeyResolutionError.SCOPE_UNAUTHORIZED


def test_resolve_delegates_to_u_as_20() -> None:
    result = resolve_signing_key(_SCOPE, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert result.error is None
    assert result.handle is not None
    # The key material is carried as a U-AS-20 SecretRef — secret-retrieval
    # mechanics are delegated to harness-as (this unit does not implement them).
    assert isinstance(result.handle.key_secret_ref, SecretRef)


def test_signing_key_rotation_state_three_values() -> None:
    assert len(list(KeyRotationState)) == 3
    assert {s.value for s in KeyRotationState} == {"active", "rotating", "retired"}


def test_sign_rejects_retired_key() -> None:
    """The RETIRED-key precondition is validated before the backend-unavailable
    raise — it's a real, independent C-CP-20 §20.3 requirement a future
    signing-backend seam would still need to honor."""
    retired = SigningKeyHandle(
        key_id="k0",
        key_secret_ref=SecretRef.model_construct(),
        rotation_state=KeyRotationState.RETIRED,
        acquired_at="",
    )
    with pytest.raises(ValueError, match="RETIRED"):
        sign_audit_entry(_ENTRY, retired, key_period=1)


def test_sign_raises_backend_unavailable_for_active_key() -> None:
    """Regression — `sign_audit_entry` must not fabricate a signed entry.

    Previously it returned `audit_signature_value=b""` with
    `audit_signature_sha256` copied from the unrelated `prior_event_hash`
    field — a silent no-op indistinguishable from a real signature.
    """
    result = resolve_signing_key(_SCOPE, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert result.handle is not None
    with pytest.raises(AuditSigningBackendUnavailableError):
        sign_audit_entry(_ENTRY, result.handle, key_period=1)


def test_verify_raises_backend_unavailable() -> None:
    """Regression — `verify_audit_entry_signature` must not return a fake
    `VERIFIED`. Previously it only compared `audit_signature_key_id`, so any
    tampered entry with a matching key_id verified successfully."""
    result = resolve_signing_key(_SCOPE, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert result.handle is not None
    forged = CPSignedAuditLedgerEntry(
        entry=_ENTRY,
        audit_signature_sha256="0" * 64,
        audit_signature_value=b"",
        audit_signature_algorithm="ed25519",
        audit_signature_key_id=result.handle.key_id,
        audit_signature_key_period=1,
    )
    with pytest.raises(AuditSigningBackendUnavailableError):
        verify_audit_entry_signature(forged, result.handle)


def test_sign_and_verify_round_trip_with_real_backend() -> None:
    """C-CP-20 §20.2.1 seam — a real injected backend signs and verifies."""
    result = resolve_signing_key(_SCOPE, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert result.handle is not None
    backend = _InMemoryEd25519Backend()

    signed = sign_audit_entry(_ENTRY, result.handle, key_period=1, backend=backend)

    assert signed.audit_signature_algorithm == "ed25519"
    assert signed.audit_signature_key_id == result.handle.key_id
    assert signed.audit_signature_key_period == 1
    assert signed.audit_signature_value != b""

    assert (
        verify_audit_entry_signature(signed, result.handle, backend=backend)
        is VerificationResult.VERIFIED
    )


def test_verify_rejects_tampered_entry_content() -> None:
    """A tampered `entry` fails the content-integrity hash recompute check
    (§20.3.1 step 2) before the backend is ever consulted."""
    result = resolve_signing_key(_SCOPE, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert result.handle is not None
    backend = _InMemoryEd25519Backend()
    signed = sign_audit_entry(_ENTRY, result.handle, key_period=1, backend=backend)

    tampered_entry = _ENTRY.model_copy(update={"response": "reject"})
    tampered = signed.model_copy(update={"entry": tampered_entry})

    assert (
        verify_audit_entry_signature(tampered, result.handle, backend=backend)
        is VerificationResult.SIGNATURE_MISMATCH
    )


def test_verify_rejects_wrong_backend_key() -> None:
    """A signature produced under one backend's key does not verify under a
    different backend's key — mutation-probe for the seam's real-crypto claim."""
    result = resolve_signing_key(_SCOPE, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert result.handle is not None
    signing_backend = _InMemoryEd25519Backend()
    other_backend = _InMemoryEd25519Backend()
    signed = sign_audit_entry(_ENTRY, result.handle, key_period=1, backend=signing_backend)

    assert (
        verify_audit_entry_signature(signed, result.handle, backend=other_backend)
        is VerificationResult.SIGNATURE_MISMATCH
    )


def test_sign_with_backend_still_rejects_retired_key() -> None:
    """The RETIRED-key precondition holds even when a real backend is present."""
    retired = SigningKeyHandle(
        key_id="k0",
        key_secret_ref=SecretRef.model_construct(),
        rotation_state=KeyRotationState.RETIRED,
        acquired_at="",
    )
    with pytest.raises(ValueError, match="RETIRED"):
        sign_audit_entry(_ENTRY, retired, key_period=1, backend=_InMemoryEd25519Backend())

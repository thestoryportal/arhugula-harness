"""`U-RT-138` — the composition-root adapter: real U-OD-55 verifier through
the §20.3.1 CP blocking walk (Runtime plan v2.49 §1.5 CP-WALK ADAPTER
criterion; pairs with the CP v2.38 §3 witness of the same name).

The CP-side witnesses (`harness-cp/tests/test_u_cp_44_45_42_audit_walk.py`)
drive the walk with a FAKE verifier; these are the integration halves: the
REAL `verify_per_family_chains` behind `OdVerifierWalkAdapter` behind
`run_blocking_audit_walk`.
"""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harness_cp.audit_walk_verification import (
    WalkInvalidDiscriminator,
    WalkResultKind,
    run_blocking_audit_walk,
)
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sign_audit_entry
from harness_od.per_family_audit_verification import VerificationBackendKeyUnknownError
from harness_runtime.lifecycle.audit_walk_adapter import OdVerifierWalkAdapter

_GENESIS = "0" * 64


class _Ed25519Backend:
    """TEST-ONLY `SigningBackend` double (real Ed25519 sign + verify)."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_id, key_period
        try:
            self._private_key.public_key().verify(signature, message)
            return True
        except Exception:
            return False


def _signed_entry(
    core: str, *, backend: _Ed25519Backend, key_id: str = "test-key"
) -> AuditLedgerEntry:
    payload = AuditPayload(
        entry_core=StateLedgerEntryRef(core),
        audit_namespace_attrs={"audit.actor": "x"},
        prior_entry_hash=_GENESIS,
    )
    sig_attrs = sign_audit_entry(payload, key_id, SignatureAlgorithm.ED25519, backend=backend)
    return AuditLedgerEntry(
        payload=payload, signature_attrs=sig_attrs, entry_hash=compute_entry_hash(payload)
    )


def _adapter(backend: _Ed25519Backend) -> OdVerifierWalkAdapter:
    def resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        del algo, key_id
        return backend

    return OdVerifierWalkAdapter(backend_resolver=resolver)


def test_rt138_adapter_real_od_verifier_through_walk() -> None:
    """Integration (CP plan v2.38 §3 / Runtime plan v2.49 §1.5): the real
    U-OD-55 verifier through the adapter through the §20.3.1 walk —

    - valid entries PASS the walk (dispositions surfaced);
    - an invalid signature FAILS the walk with the `SIGNATURE_INVALID`
      discriminator (never INCOMPLETE, never a hash-only pass);
    - the OD typed availability error (unknown key_id from the resolver)
      surfaces as CP availability — INCOMPLETE + rerunnable, NOT a verdict;
    - a defect raise from the resolver propagates unwrapped.

    Mutation probes: dropping the adapter's `AuditSignatureInvalid` arm
    turns the invalid case into an unwrapped OD raise (walk never returns)
    → FAILS; wrapping defect raises into availability turns the TypeError
    case into INCOMPLETE → FAILS."""
    backend = _Ed25519Backend()

    # Valid entries → PASSED through the real verifier.
    good = [_signed_entry("ref-1", backend=backend)]
    result = run_blocking_audit_walk(good, verifier=_adapter(backend))
    assert result.kind is WalkResultKind.PASSED
    assert result.signature_dispositions == {"verified": 1}

    # Tampered signature → FAILED with the signature discriminator.
    entry = _signed_entry("ref-2", backend=backend)
    tampered = AuditLedgerEntry(
        payload=entry.payload,
        signature_attrs=entry.signature_attrs.model_copy(
            update={"audit_signature_value": "QUJD" * 21 + "QQ=="}  # wrong 64-byte sig
        ),
        entry_hash=entry.entry_hash,
    )
    failed = run_blocking_audit_walk([tampered], verifier=_adapter(backend))
    assert failed.kind is WalkResultKind.FAILED
    assert failed.failure_discriminator is WalkInvalidDiscriminator.SIGNATURE_INVALID

    # Unknown key_id (typed availability) → INCOMPLETE + rerunnable.
    def unknown_key_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        raise VerificationBackendKeyUnknownError(f"no backend for ({algo}, {key_id})")

    unavailable = run_blocking_audit_walk(
        good, verifier=OdVerifierWalkAdapter(backend_resolver=unknown_key_resolver)
    )
    assert unavailable.kind is WalkResultKind.INCOMPLETE_UNVERIFIED
    assert unavailable.rerunnable is True
    assert unavailable.failure_discriminator is None

    # Defect raise propagates unwrapped — never rerunnable infrastructure.
    def defect_resolver(algo: SignatureAlgorithm, key_id: str) -> _Ed25519Backend:
        raise TypeError("programming error (test)")

    with pytest.raises(TypeError, match="programming error"):
        run_blocking_audit_walk(
            good, verifier=OdVerifierWalkAdapter(backend_resolver=defect_resolver)
        )


def test_hash_chain_breach_fails_walk_with_discriminator() -> None:
    """Codex round-45 (CP plan v2.38 §3): content/linkage tampering is an
    audit-FAIL routed through the walk with the `HASH_CHAIN_BREACH`
    discriminator — never an internal error, never conflated with the
    signature discriminator.

    Mutation probe: dropping the adapter's `HashChainBreach` arm turns this
    into an unwrapped OD raise (walk never returns) → FAILS."""
    backend = _Ed25519Backend()
    entry = _signed_entry("ref-3", backend=backend)
    content_tampered = AuditLedgerEntry(
        payload=entry.payload.model_copy(
            update={"audit_namespace_attrs": {"audit.actor": "TAMPERED"}}
        ),
        signature_attrs=entry.signature_attrs,
        entry_hash=entry.entry_hash,  # stale hash over the original payload
    )
    result = run_blocking_audit_walk([content_tampered], verifier=_adapter(backend))
    assert result.kind is WalkResultKind.FAILED
    assert result.failure_discriminator is WalkInvalidDiscriminator.HASH_CHAIN_BREACH

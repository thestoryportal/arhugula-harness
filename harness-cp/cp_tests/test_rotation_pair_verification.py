"""C-CP-20 §20.3.2 — `RotationPairEvidence` construction-time coherence +
the `RotationPairEvidenceProvider`/`KeyIdentityResolver` injection Protocols.

The real evidence lookup + physical-key attestation are exercised end-to-end
via `verify_rotation_6_steps` (`test_five_axis_composition.py`); this file
covers the DTO's own invariant and Protocol conformance in isolation.
"""

from __future__ import annotations

import pytest
from harness_cp.rotation_pair_verification import (
    KeyIdentityResolver,
    RotationBoundaryPhysicalKeyCollisionError,
    RotationPairEvidence,
    RotationPairEvidenceProvider,
    RotationPairEvidenceUnavailableError,
    RotationPairIntegrityBreach,
)


def test_rotation_pair_evidence_absent_all_none_constructs() -> None:
    """A well-formed `pair_present=False` evidence object constructs cleanly."""
    evidence = RotationPairEvidence(correlation_id="c1", pair_present=False)
    assert evidence.pair_present is False
    assert evidence.signatures_verified is False


def test_rotation_pair_evidence_present_all_populated_constructs() -> None:
    """A well-formed `pair_present=True` evidence object constructs cleanly."""
    evidence = RotationPairEvidence(
        correlation_id="c1",
        pair_present=True,
        outgoing_key_period=3,
        incoming_key_period=4,
        outgoing_key_id="a",
        incoming_key_id="b",
    )
    assert evidence.pair_present is True


def test_rotation_pair_evidence_rejects_pair_present_true_with_missing_period_field() -> None:
    """Out-of-family review round-4 [P1] correction — illegal states
    unrepresentable: `pair_present=True` with ANY period/id field missing
    must fail construction, not silently pass through to a consumer.
    Mutation probe: removing the validator lets this construct successfully."""
    with pytest.raises(ValueError, match="requires all four"):
        RotationPairEvidence(
            correlation_id="c1",
            pair_present=True,
            outgoing_key_period=3,
            incoming_key_period=None,
            outgoing_key_id="a",
            incoming_key_id="b",
        )


def test_rotation_pair_evidence_rejects_pair_present_false_with_populated_period_field() -> None:
    """The symmetric case — `pair_present=False` must not carry populated
    period/id fields either. Mutation probe: removing the validator lets
    this construct successfully."""
    with pytest.raises(ValueError, match="requires all four"):
        RotationPairEvidence(
            correlation_id="c1",
            pair_present=False,
            outgoing_key_period=3,
        )


def test_rotation_pair_evidence_provider_protocol_runtime_checkable() -> None:
    """A conforming object satisfies `isinstance(..., RotationPairEvidenceProvider)`."""

    class _Provider:
        def evidence_for(self, correlation_id: str) -> RotationPairEvidence:
            return RotationPairEvidence(correlation_id=correlation_id, pair_present=False)

    assert isinstance(_Provider(), RotationPairEvidenceProvider)


def test_key_identity_resolver_protocol_runtime_checkable() -> None:
    """A conforming object satisfies `isinstance(..., KeyIdentityResolver)`."""

    class _Resolver:
        def physical_identity_for(self, key_id: str) -> str:
            return f"physical-{key_id}"

    assert isinstance(_Resolver(), KeyIdentityResolver)


def test_exception_types_are_distinct() -> None:
    """The three CP-owned exception types are DISTINCT — a tamper signal,
    an availability signal, and a physical-key collision are never
    conflated (mutation probe: aliasing any two of these to the same type
    would let a `except RotationPairIntegrityBreach` clause silently
    swallow an unrelated availability/collision failure)."""
    assert RotationPairIntegrityBreach is not RotationPairEvidenceUnavailableError
    assert RotationPairIntegrityBreach is not RotationBoundaryPhysicalKeyCollisionError
    assert RotationPairEvidenceUnavailableError is not RotationBoundaryPhysicalKeyCollisionError

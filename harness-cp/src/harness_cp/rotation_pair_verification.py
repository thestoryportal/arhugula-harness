"""C-CP-20 §20.3.2 rotation-pair-evidence injection seam + physical-key-
distinctness boundary attestation (U-CP-44/U-CP-45 v2.41 amendment; CP spec
v1.105 §2).

`verify_rotation_6_steps`'s `WRITE_DUAL_VERIFY_ENTRY`/`PROBE_VERIFY_AT_READ`
steps (`five_axis_composition.py`) need OD-anchored rotation-pair evidence
for a correlation id derived from an IS-owned window check. `harness-cp`
MUST NOT import `harness-od` (the OD→CP canonical direction per CXA §2.3.3;
`harness-od` already imports `harness-cp` for `SigningBackend`) — mirrors the
`audit_walk_verification.AuditWalkVerifier` precedent (a DIFFERENT injected
verifier for a DIFFERENT query shape: per-correlation-id evidence lookup,
not a whole-ledger audit walk). The composition root in `harness-runtime`
(which imports both packages) supplies the adapter over OD's
`find_rotation_pair_evidence` (OD spec v1.35 §24.8).

**Result boundary.** `RotationPairEvidence` (CP-owned mirror DTO, same field
shape as OD's) is returned/raised through CP-owned types only:
`RotationPairIntegrityBreach` (a genuine OD-detected structural tamper
signal — re-raised, never folded into a "false" evidence result);
`RotationPairEvidenceUnavailableError` (infrastructure availability OR an
evidence correlation-id mismatch — never a verdict). Any other raise from
the injected provider is a defect and propagates unwrapped.

**`signatures_verified` — necessary but not sufficient (CP spec v1.105 §2
row 4b).** `pair_present=True` certifies STRUCTURAL OD-anchored pair
evidence only — it does NOT certify per-entry cryptographic signature
verification against either sibling's historical key-period (no rotation-
period-aware verifier exists yet). `PROBE_VERIFY_AT_READ` gates on BOTH
`pair_present` AND `signatures_verified`, so no shipped provider in this
delta can reach a genuine pass (registered residual, not a bug).

**Physical-key-distinctness boundary attestation (§20.3.2 row 5) — REQUIRED,
not skippable.** A `KeyIdentityResolver` confirms an evidence-confirmed
pair's `outgoing_key_id`/`incoming_key_id` resolve to genuinely DIFFERENT
physical key material, not merely different string labels aliasing the SAME
underlying key. Absence of a resolver is NOT a silent skip — it yields the
same explicit-incomplete disposition as an absent `evidence_provider`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, model_validator

__all__ = [
    "KeyIdentityResolver",
    "RotationBoundaryPhysicalKeyCollisionError",
    "RotationPairEvidence",
    "RotationPairEvidenceProvider",
    "RotationPairEvidenceUnavailableError",
    "RotationPairIntegrityBreach",
]


class RotationPairIntegrityBreach(Exception):  # noqa: N818 — mirrors OD's own naming
    """A genuine OD-detected rotation-pair structural/cryptographic tamper
    signal, re-raised through the CP result boundary (message-preserving).

    NEVER folded into a `RotationPairEvidence` field — tamper detection is
    always fail-loud, mirroring OD's own fail-loud posture for this exact
    failure class (OD spec v1.35 §24.8 row 5).
    """


class RotationPairEvidenceUnavailableError(Exception):
    """Verification INFRASTRUCTURE was unavailable, OR the evidence provider
    returned evidence for a DIFFERENT correlation id than requested — never
    a verdict.

    The adapter wraps an OD-side ledger-load/lookup infrastructure failure
    (not a tamper signal, not pair-absence) in this type. It is ALSO raised
    when `RotationPairEvidence.correlation_id` does not equal the requested
    id (out-of-family review round-2 [P2] correction — a provider returning
    evidence for an unrelated id, whether from a bug or an adversarial
    injection, is a defect, not a pass). A re-run after availability is
    restored (or after the provider bug is fixed) may complete the step.
    """


class RotationBoundaryPhysicalKeyCollisionError(Exception):
    """A rotation pair's two key ids resolve to the SAME physical key
    material — the "rotation" never actually changed the physical signing
    key (CP spec v1.105 §2 row 5).

    DISTINCT from `RotationPairIntegrityBreach`: the OD-side pair may be
    perfectly well-formed (consecutive periods, differing key_id LABELS,
    valid chain continuity) while still failing this CP-owned boundary
    attestation.
    """


class RotationPairEvidence(BaseModel):
    """CP-owned mirror DTO — structurally mirrors OD spec v1.35 §24.8's
    `RotationPairEvidence` (same field set), but is its own CP-owned
    Pydantic type: `harness-cp` never imports the OD type, per the same
    no-cross-import discipline `WalkVerificationOutcome` already
    established for the audit walk.

    `pair_present=True` certifies STRUCTURAL pair validity only — it does
    NOT certify per-entry cryptographic signature verification against
    either sibling's historical key-period; `signatures_verified` is the
    machine-checkable field carrying that distinction (OD spec v1.35 §24.8
    row 8a) — necessary but not sufficient for `PROBE_VERIFY_AT_READ`'s
    genuine pass.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    correlation_id: str
    pair_present: bool
    outgoing_key_period: int | None = None
    incoming_key_period: int | None = None
    outgoing_key_id: str | None = None
    incoming_key_id: str | None = None
    signatures_verified: bool = False

    @model_validator(mode="after")
    def _pair_present_implies_populated_fields(self) -> RotationPairEvidence:
        """Construction-time coherence guard (out-of-family review round-4
        [P1] correction — illegal states unrepresentable). A buggy or
        adversarial `RotationPairEvidenceProvider` cannot construct
        `pair_present=True` with a missing period/id field, nor
        `pair_present=False` with a populated one."""
        populated = (
            self.outgoing_key_period,
            self.incoming_key_period,
            self.outgoing_key_id,
            self.incoming_key_id,
        )
        if self.pair_present and any(field is None for field in populated):
            raise ValueError(
                "RotationPairEvidence(pair_present=True) requires all four "
                "period/id fields to be populated — a provider returned "
                "pair_present=True with a missing field"
            )
        if not self.pair_present and any(field is not None for field in populated):
            raise ValueError(
                "RotationPairEvidence(pair_present=False) requires all four "
                "period/id fields to be None — a provider returned "
                "pair_present=False with a populated field"
            )
        return self


@runtime_checkable
class RotationPairEvidenceProvider(Protocol):
    """The injected per-correlation-id evidence-lookup seam (CP spec v1.105
    §2). Mirrors the `AuditWalkVerifier` mediation shape for a DIFFERENT
    query shape (a single correlation id, not a batch walk).

    Raises `RotationPairIntegrityBreach` for a genuine tamper signal,
    `RotationPairEvidenceUnavailableError` for infrastructure availability;
    any other raise is a defect and propagates unwrapped.
    """

    def evidence_for(self, correlation_id: str) -> RotationPairEvidence: ...


@runtime_checkable
class KeyIdentityResolver(Protocol):
    """Resolves a `key_id` label to its underlying PHYSICAL key identity
    (e.g. `AwsKmsSigningBackend.key_arns`, ADR-D8) — the physical-key-
    distinctness boundary attestation's REQUIRED input (CP spec v1.105 §2
    row 5). Absence is NOT a silent skip: `PROBE_VERIFY_AT_READ` reports
    the same explicit-incomplete disposition as an absent
    `evidence_provider` when this resolver is absent.
    """

    def physical_identity_for(self, key_id: str) -> str: ...

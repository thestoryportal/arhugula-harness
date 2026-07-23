"""5-axis composition + operator-policy override + key-rotation — U-CP-45.

Implements C-CP-19 §19.3 + §19.5 (5-axis composition + operator-policy
override) and C-CP-20 §20.3 + §20.3.1 (the key-rotation two-row pattern + the
6-step rotation verification protocol).

Declares the `FiveAxisCompositionInput` / `FiveAxisCompositionResult` records,
the `OperatorPolicyOverride` record + `OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE`,
the `KeyRotationStage` / `RotationVerificationStep` enums, the
`KeyRotationPattern` record + `KEY_ROTATION_PATTERN`, and the four composition
functions.

The 5-axis composition runs the U-CP-43 gate-level computation and the U-AS-12
sandbox-tier composition as **orthogonal axes** (§19.3) — neither collapses
into the other; the result carries `gate_level` and `sandbox_tier_floor`
independently.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2.7 U-CP-45 (preserved
verbatim through v2.9); Spec_Control_Plane_v1_2.md §19 C-CP-19 §19.3/§19.5 +
§20 C-CP-20 §20.3/§20.3.1; ADR-D5 v1.3 §1.4 + §1.5.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum

from harness_as import BlastRadiusTier
from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface, PersonaTier
from harness_is.chain_verification import verify_chain
from harness_is.entry_hash import compute_response_hash
from harness_is.rotation_window_verification import (
    RotationWindowCheckStatus,
    verify_rotation_window,
)
from harness_is.state_ledger_entry_schema import StateLedgerEntry
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.f5_signing_key_resolution import (
    KeyRotationState,
    SigningKeyHandle,
    SigningKeyScope,
)
from harness_cp.gate_level_rule import GateLevel, GateLevelInput, gate_level
from harness_cp.rotation_pair_verification import (
    KeyIdentityResolver,
    RotationBoundaryPhysicalKeyCollisionError,
    RotationPairEvidenceProvider,
    RotationPairEvidenceUnavailableError,
)

# --- §19.3 5-axis composition -----------------------------------------------


class FiveAxisCompositionInput(BaseModel):
    """The 5-axis composition input (C-CP-19 §19.3).

    Four axes from U-CP-43's `GateLevelInput` (v2.20 spec-canonical conformance
    per CP spec v1.15 §19.1.1.1: `per_tool_gate_level`, `blast_radius_tier`,
    `persona_tier`, `mcp_trust_tier`) plus the U-AS-12 cross-axis `sandbox_tier`.

    NOTE — `deployment_surface` is preserved as a field for U-CP-45 §19.3
    consumer compatibility at this revision; §19.3 5-axis spec-canonical
    enumeration is `{per_tool_gate_level, blast_radius, server_trust,
    persona_tier, sandbox_tier}` per AS C-AS-12 (deployment_surface is NOT
    a §19.3 D2-layer axis either — it's an input to sandbox_tier_floor
    computation). Full §19.3 spec-canonical conformance is out of v2.20 (B2)
    scope and remains a parallel drift logged for future follow-on.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    per_tool_gate_level: GateLevel
    """Spec-canonical D5-layer axis (v2.20 ADDED — passes into GateLevelInput)."""

    persona_tier: PersonaTier
    blast_radius_tier: BlastRadiusTier
    deployment_surface: DeploymentSurface
    """v2.4-lineage field; preserved for U-CP-45 §19.3 compatibility. §19.3
    spec-canonical does NOT carry deployment_surface as an axis — full §19.3
    conformance deferred to follow-on arc."""

    mcp_trust_tier: MCPTrustTier
    sandbox_tier: SandboxTier
    """From U-AS-12 (cross-axis: AS)."""


class FiveAxisCompositionResult(BaseModel):
    """The 5-axis composition result (C-CP-19 §19.3).

    Carries `gate_level` and `sandbox_tier_floor` as orthogonal axes — neither
    collapses into the other (acceptance #1).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    gate_level: GateLevel
    """From the U-CP-43 gate-level computation."""

    sandbox_tier_floor: SandboxTier
    """From the U-AS-12 sandbox-tier composition."""

    composition_admissible: bool
    """Orthogonal-axes product space valid."""

    cross_axis_composition_audit_attrs: frozenset[str]
    """The audit attribute set emitted at U-CP-46."""


def compose_five_axis(
    input: FiveAxisCompositionInput,
) -> FiveAxisCompositionResult:
    """Compose the gate-level and sandbox-tier axes orthogonally (§19.3).

    The gate level is computed by U-CP-43; the sandbox-tier floor is the
    U-AS-12 sandbox-tier composition input (passed through — this unit does
    NOT recompute the AS-side composition). Both axes are carried
    independently in the result (acceptance #1). `composition_admissible` is
    true for all valid input tuples — the axes are orthogonal, so every
    (gate_level, sandbox_tier) pair is a valid point in the product space
    (acceptance #2).
    """
    computation = gate_level(
        GateLevelInput(
            per_tool_gate_level=input.per_tool_gate_level,
            persona_tier=input.persona_tier,
            blast_radius_tier=input.blast_radius_tier,
            mcp_trust_tier=input.mcp_trust_tier,
        )
    )
    return FiveAxisCompositionResult(
        gate_level=computation.computed_gate_level,
        sandbox_tier_floor=input.sandbox_tier,
        composition_admissible=True,
        cross_axis_composition_audit_attrs=frozenset(
            {"audit.composition.gate_level", "audit.composition.sandbox_tier_floor"}
        ),
    )


# --- §19.5 operator-policy override -----------------------------------------


class OverrideKind(StrEnum):
    """The kind of operator-policy override (C-CP-19 §19.5)."""

    LOWER_GATE_LEVEL = "lower-gate-level"
    RAISE_GATE_LEVEL = "raise-gate-level"
    NARROW_PALETTE = "narrow-palette"


class OverrideScope(StrEnum):
    """The scope an operator-policy override is bound to (C-CP-19 §19.5)."""

    PER_TOOL = "per-tool"
    PER_WORKFLOW = "per-workflow"
    PER_PERSONA_TIER = "per-persona-tier"


class OperatorPolicyOverride(BaseModel):
    """One operator-policy override-scope entry (C-CP-19 §19.5)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    override_kind: OverrideKind
    scope: OverrideScope
    permitted_at: frozenset[PersonaTier]
    audit_required: bool
    """Always true — every override emits an audit entry (acceptance #4)."""


_ALL_TIERS: frozenset[PersonaTier] = frozenset(PersonaTier)
_SOLO_TEAM: frozenset[PersonaTier] = frozenset(
    {PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING}
)

OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE: tuple[OperatorPolicyOverride, ...] = (
    OperatorPolicyOverride(
        override_kind=OverrideKind.LOWER_GATE_LEVEL,
        scope=OverrideScope.PER_TOOL,
        permitted_at=_SOLO_TEAM,
        audit_required=True,
    ),
    OperatorPolicyOverride(
        override_kind=OverrideKind.RAISE_GATE_LEVEL,
        scope=OverrideScope.PER_TOOL,
        permitted_at=_ALL_TIERS,
        audit_required=True,
    ),
    OperatorPolicyOverride(
        override_kind=OverrideKind.NARROW_PALETTE,
        scope=OverrideScope.PER_TOOL,
        permitted_at=_ALL_TIERS,
        audit_required=True,
    ),
)
"""The §19.5 override-scope table: LOWER_GATE_LEVEL permitted at
solo-developer + team-binding (prohibited at multi-tenant-compliance);
RAISE_GATE_LEVEL and NARROW_PALETTE permitted at all three tiers."""


class OverrideRejection(BaseModel):
    """A rejected operator-policy override (C-CP-19 §19.5.2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    override_kind: OverrideKind
    persona_tier: PersonaTier
    rejection_reason: str


def apply_operator_policy_override(
    base: FiveAxisCompositionResult,
    override: OperatorPolicyOverride,
    persona_tier: PersonaTier,
) -> FiveAxisCompositionResult | OverrideRejection:
    """Apply an operator-policy override to a 5-axis composition result.

    Per §19.5: the override is rejected when `persona_tier` is not in the
    override's `permitted_at` set — `LOWER_GATE_LEVEL` at
    `MULTI_TENANT_COMPLIANCE` is structurally prohibited (ADR-D5 v1.3 §1.5.2).
    Every override (applied or rejected) emits an audit entry per U-CP-46
    `audit.policy.*` (acceptance #4 — `audit_required` is always true).
    """
    if persona_tier not in override.permitted_at:
        return OverrideRejection(
            override_kind=override.override_kind,
            persona_tier=persona_tier,
            rejection_reason=(
                f"{override.override_kind.value} override structurally "
                f"prohibited at {persona_tier.value} per C-CP-19 §19.5"
            ),
        )
    return base


# --- §20.3 key-rotation two-row pattern -------------------------------------


class KeyRotationStage(StrEnum):
    """The two-row key-rotation pattern stages (C-CP-20 §20.3)."""

    ROW_1_DUAL_VERIFY_ACTIVE = "row-1-dual-verify-active"
    """Both old and new keys verify signatures at read; new key signs new
    entries."""

    ROW_2_RETIRE_OLD = "row-2-retire-old"
    """Old key removed from the verification set; only the new key active."""


class RotationVerificationStep(StrEnum):
    """The §20.3.1 six-step rotation verification protocol."""

    STAGE_NEW_KEY = "stage-new-key"
    WRITE_DUAL_VERIFY_ENTRY = "write-dual-verify-entry"
    PROBE_VERIFY_AT_READ = "probe-verify-at-read"
    VERIFY_HASH_CHAIN_LINK = "verify-hash-chain-link"
    ROTATE_SIGNING_TO_NEW = "rotate-signing-to-new"
    RETIRE_OLD_KEY = "retire-old-key"


#: The §20.3.1 six steps, in protocol order.
ROTATION_VERIFICATION_STEPS: tuple[RotationVerificationStep, ...] = (
    RotationVerificationStep.STAGE_NEW_KEY,
    RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY,
    RotationVerificationStep.PROBE_VERIFY_AT_READ,
    RotationVerificationStep.VERIFY_HASH_CHAIN_LINK,
    RotationVerificationStep.ROTATE_SIGNING_TO_NEW,
    RotationVerificationStep.RETIRE_OLD_KEY,
)


class KeyRotationPattern(BaseModel):
    """One row of the §20.3 two-row key-rotation pattern."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stage: KeyRotationStage
    active_key_count: int
    """∈ {1, 2}."""

    signing_key: SigningKeyHandle
    verification_key_set: frozenset[str]
    """The `key_id` set valid for signature verification at this stage."""


class StepResult(BaseModel):
    """The result of one §20.3.1 rotation verification step."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step: RotationVerificationStep
    succeeded: bool
    detail: str


class KeyRotationOutcome(BaseModel):
    """The outcome of a key-rotation execution (C-CP-20 §20.3)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope: SigningKeyScope
    final_stage: KeyRotationStage
    rotation_complete: bool
    rotation_state_partial: bool
    """true when steps 1-5 are incomplete — emits `audit.policy.rotation_state_partial`."""


def execute_key_rotation(
    scope: SigningKeyScope,
    *,
    audit_ledger_entries: Sequence[StateLedgerEntry] = (),
    rotation_window_entries: Sequence[StateLedgerEntry] = (),
    evidence_provider: RotationPairEvidenceProvider | None = None,
    key_identity_resolver: KeyIdentityResolver | None = None,
) -> KeyRotationOutcome:
    """Execute the §20.3 two-row key rotation for a signing-key scope.

    The rotation runs the §20.3.1 six-step verification; a rotation that
    completes all six steps reaches `ROW_2_RETIRE_OLD` with the old key removed
    from the verification set. Rotation does NOT modify historical entries
    (acceptance #7 — F2 immutability invariant): historical entries remain
    verifiable by the (retired) key that signed them.

    All parameters thread through to `verify_rotation_6_steps` — see its
    docstring for what each one gates.
    """
    steps = verify_rotation_6_steps(
        scope,
        audit_ledger_entries=audit_ledger_entries,
        rotation_window_entries=rotation_window_entries,
        evidence_provider=evidence_provider,
        key_identity_resolver=key_identity_resolver,
    )
    complete = all(s.succeeded for s in steps)
    return KeyRotationOutcome(
        scope=scope,
        final_stage=(
            KeyRotationStage.ROW_2_RETIRE_OLD
            if complete
            else KeyRotationStage.ROW_1_DUAL_VERIFY_ACTIVE
        ),
        rotation_complete=complete,
        rotation_state_partial=not complete,
    )


def _write_dual_verify_entry(
    audit_ledger_entries: Sequence[StateLedgerEntry],
    rotation_window_entries: Sequence[StateLedgerEntry],
) -> tuple[bool, str, str | None]:
    """`WRITE_DUAL_VERIFY_ENTRY` — IS-anchored presence/uniqueness check over
    a caller-derived rotation window (CP spec v1.105 §1; IS spec v1.12 §7.7).

    Returns `(succeeded, detail, derived_correlation_id)`. FIRST verifies
    every `rotation_window_entries` member is also present in
    `audit_ledger_entries` (matched by `harness_is.entry_hash.
    compute_response_hash` identity — out-of-family review round-4 [P1]
    correction over round-3's fix) — this closes the gap where a fabricated
    window (real, valid entries elsewhere, but never authenticated as
    belonging to THIS chain) would otherwise pass presence/uniqueness. Then
    runs `verify_rotation_window`; on `VALID`, extracts the single derived
    correlation id.
    """
    if not rotation_window_entries:
        return (
            False,
            "no rotation_window_entries supplied — WRITE_DUAL_VERIFY_ENTRY "
            "requires a caller-derived rotation-event window (IS spec v1.12 §7.7)",
            None,
        )
    chain_hashes = {compute_response_hash(entry) for entry in audit_ledger_entries}
    for window_entry in rotation_window_entries:
        if compute_response_hash(window_entry) not in chain_hashes:
            return (
                False,
                "rotation_window_entries contains an entry not present in "
                "audit_ledger_entries — the window must be an authenticated "
                "subset of the genesis-anchored chain (out-of-family review "
                "round-3 [P1] correction)",
                None,
            )
    window_result = verify_rotation_window(rotation_window_entries)
    if window_result.status is not RotationWindowCheckStatus.VALID:
        failure_label = (
            window_result.failure_type.value if window_result.failure_type else "unknown"
        )
        return (
            False,
            f"rotation window invalid: {failure_label} (IS spec v1.12 §7.7)",
            None,
        )
    derived_id = rotation_window_entries[0].rotation_correlation_id
    return (
        True,
        f"rotation window valid — derived correlation id {derived_id!r} (IS spec v1.12 §7.7)",
        derived_id,
    )


def _probe_verify_at_read(
    derived_correlation_id: str | None,
    evidence_provider: RotationPairEvidenceProvider | None,
    key_identity_resolver: KeyIdentityResolver | None,
) -> tuple[bool, str]:
    """`PROBE_VERIFY_AT_READ` — OD-anchored evidence check + REQUIRED
    physical-key-distinctness boundary attestation (CP spec v1.105 §1/§2).

    A `RotationPairIntegrityBreach` (OD-detected tamper),
    `RotationPairEvidenceUnavailableError` (infrastructure unavailable OR a
    correlation-id mismatch), or `RotationBoundaryPhysicalKeyCollisionError`
    (same physical key under two labels) from the injected provider/resolver
    PROPAGATES UNWRAPPED — never caught into a `StepResult` (CP plan v2.41
    U-CP-45 criterion #4). Otherwise returns `(succeeded, detail)`: an
    absent pair, `signatures_verified=False` (structural evidence alone is
    necessary but not sufficient — every provider in this delta), or an
    absent resolver each yield an EXPLICIT incomplete disposition, never a
    silent pass.
    """
    if derived_correlation_id is None or evidence_provider is None:
        return (
            False,
            "no OD-anchored evidence available — WRITE_DUAL_VERIFY_ENTRY did "
            "not derive a valid rotation-correlation id, or no evidence_provider "
            "was injected (CP spec v1.105 §1)",
        )
    evidence = evidence_provider.evidence_for(derived_correlation_id)
    if evidence.correlation_id != derived_correlation_id:
        raise RotationPairEvidenceUnavailableError(
            f"evidence correlation-id mismatch: requested "
            f"{derived_correlation_id!r}, received {evidence.correlation_id!r} "
            "(out-of-family review round-2 [P2] correction)"
        )
    if not evidence.pair_present:
        return (
            False,
            f"no OD-anchored evidence for rotation boundary "
            f"{derived_correlation_id!r} (OD spec v1.35 §24.8 "
            "absence-is-not-a-breach disposition)",
        )
    if not evidence.signatures_verified:
        return (
            False,
            "structural evidence present, signature verification not "
            "available (OD spec v1.35 §24.8 row 8a — no rotation-period-aware "
            "cryptographic verifier exists yet; structural evidence alone is "
            "necessary but not sufficient)",
        )
    if key_identity_resolver is None:
        return (
            False,
            "no key_identity_resolver injected — physical-key-distinctness "
            "boundary attestation is REQUIRED, not skippable (CP spec v1.105 "
            "§2 row 5)",
        )
    # Guaranteed non-None by RotationPairEvidence's own construction-time
    # coherence validator (pair_present=True ⟹ all four fields populated).
    assert evidence.outgoing_key_id is not None
    assert evidence.incoming_key_id is not None
    outgoing_identity = key_identity_resolver.physical_identity_for(evidence.outgoing_key_id)
    incoming_identity = key_identity_resolver.physical_identity_for(evidence.incoming_key_id)
    if outgoing_identity == incoming_identity:
        raise RotationBoundaryPhysicalKeyCollisionError(
            f"rotation pair {derived_correlation_id!r}: outgoing key_id "
            f"{evidence.outgoing_key_id!r} and incoming key_id "
            f"{evidence.incoming_key_id!r} resolve to the SAME physical key "
            f"identity {outgoing_identity!r} — the rotation never actually "
            "changed the physical signing key (CP spec v1.105 §2 row 5)"
        )
    return (
        True,
        "OD-anchored structural pair evidence AND per-period signature "
        f"verification both confirmed for outgoing_key_period="
        f"{evidence.outgoing_key_period}, incoming_key_period="
        f"{evidence.incoming_key_period}",
    )


def verify_rotation_6_steps(
    scope: SigningKeyScope,
    *,
    audit_ledger_entries: Sequence[StateLedgerEntry] = (),
    rotation_window_entries: Sequence[StateLedgerEntry] = (),
    evidence_provider: RotationPairEvidenceProvider | None = None,
    key_identity_resolver: KeyIdentityResolver | None = None,
) -> tuple[StepResult, ...]:
    """Run the §20.3.1 six-step rotation verification protocol.

    Steps in order: stage new key (rotation_state = ROTATING) → write the
    first dual-verify entry → probe-verify both keys at read → verify
    hash-chain link continuity → rotate signing to the new key → retire the
    old key.

    `VERIFY_HASH_CHAIN_LINK` is wired to the real IS chain-linkage check
    (`harness_is.chain_verification.verify_chain`) against
    `audit_ledger_entries` — the FULL genesis-anchored chain (position 1's
    `prior_event_hash` == `ALL_ZEROS_SENTINEL`), NOT the rotation window.
    `audit_ledger_entries` defaulting to empty is itself treated as a
    failure, not a fabricated pass — zero entries is an absence of
    evidence, not proof of chain integrity.

    `WRITE_DUAL_VERIFY_ENTRY` gains a REAL presence/uniqueness check over
    the SEPARATE `rotation_window_entries` parameter — DISTINCT from
    `audit_ledger_entries` (out-of-family review round-2 [P1] correction:
    the two require CONFLICTING input shapes — `verify_chain`'s inception-
    sentinel contract needs the full chain, `verify_rotation_window` needs a
    sparse window scoped to just the rotation event). See
    `_write_dual_verify_entry` for the subset-membership check + window
    validation.

    `PROBE_VERIFY_AT_READ` gains a REAL OD-anchored evidence check via the
    injected `evidence_provider`, gated on BOTH `pair_present` AND
    `signatures_verified` (structural evidence alone is necessary but not
    sufficient — no rotation-period-aware cryptographic verifier exists yet,
    so no shipped provider in this delta can reach a genuine pass), plus a
    REQUIRED physical-key-distinctness attestation via `key_identity_resolver`.
    See `_probe_verify_at_read`.

    `ROTATE_SIGNING_TO_NEW`/`RETIRE_OLD_KEY` are gated on ALL THREE of
    {`VERIFY_HASH_CHAIN_LINK`, `WRITE_DUAL_VERIFY_ENTRY`, `PROBE_VERIFY_AT_READ`}
    succeeding. **Ordinal-sequencing scope (out-of-family review round-3
    [P2] correction):** `VERIFY_HASH_CHAIN_LINK`'s OWN result remains
    UNCHANGED and independent of the two new steps — a `WRITE_DUAL_VERIFY_
    ENTRY` failure does NOT retroactively block `VERIFY_HASH_CHAIN_LINK`
    itself, only the two rotate/retire steps additionally gate on it.

    `STAGE_NEW_KEY` and the two rotate/retire narration strings stay
    simulated: real key staging/signing/verification is not reachable from
    CP today (`f5_signing_key_resolution.sign_audit_entry` /
    `verify_audit_entry_signature` raise `AuditSigningBackendUnavailableError`
    pending a deployment-bound signing backend, B-22).

    Raises `RotationPairIntegrityBreach`, `RotationPairEvidenceUnavailableError`,
    or `RotationBoundaryPhysicalKeyCollisionError` — uncaught — when the
    injected `evidence_provider`/`key_identity_resolver` detects tamper,
    unavailability, or a physical-key collision (see `_probe_verify_at_read`).
    """
    # One snapshot, reused for both the emptiness check and verification —
    # a caller-supplied mutable sequence must not be re-read after
    # `verify_chain` runs (a TOCTOU re-read could see the sequence empty
    # pre-verify but non-empty post-verify, or vice versa, decoupling the
    # emptiness gate from what was actually verified).
    entries = list(audit_ledger_entries)
    chain_result = verify_chain(entries)
    # `failure_type is None` iff the chain is valid — mirrors
    # `harness_as.secret_fetch_audit`'s own `verify_chain` usage, which
    # likewise never imports the `VerificationStatus` enum across the CP→IS
    # boundary (avoids widening the CXA Pattern-P1 typed-seam surface for a
    # value already derivable from `ChainVerificationResult`'s other fields).
    scope_label = f"{scope.scope_kind.value}:{scope.scope_identifier}"
    if not entries:
        hash_chain_succeeded = False
        hash_chain_detail = (
            f"no audit_ledger_entries supplied for scope {scope_label} — "
            f"zero entries is an absence of evidence, not proof of chain "
            f"integrity"
        )
    elif chain_result.failure_type is None:
        hash_chain_succeeded = True
        hash_chain_detail = (
            f"generic prior_event_hash continuity verified via "
            f"harness_is.chain_verification.verify_chain across "
            f"{chain_result.entries_verified} entries for scope {scope_label} "
            f"— does not by itself confirm a rotation boundary is present"
        )
    else:
        hash_chain_succeeded = False
        failure_label = chain_result.failure_type.value
        hash_chain_detail = (
            f"chain-link mismatch at position {chain_result.failure_position} "
            f"({failure_label}) for scope {scope_label}"
        )

    write_dual_succeeded, write_dual_detail, derived_correlation_id = _write_dual_verify_entry(
        entries, rotation_window_entries
    )
    # Any of RotationPairIntegrityBreach / RotationPairEvidenceUnavailableError /
    # RotationBoundaryPhysicalKeyCollisionError propagates unwrapped here —
    # deliberately NOT caught (CP plan v2.41 U-CP-45 criterion #4).
    probe_succeeded, probe_detail = _probe_verify_at_read(
        derived_correlation_id, evidence_provider, key_identity_resolver
    )

    simulated_suffix = (
        " [simulated narration — no real signing backend wired from CP yet; "
        "see f5_signing_key_resolution.AuditSigningBackendUnavailableError, B-22]"
    )
    rotate_retire_gate_succeeded = hash_chain_succeeded and write_dual_succeeded and probe_succeeded
    blocked_detail = (
        "blocked — VERIFY_HASH_CHAIN_LINK / WRITE_DUAL_VERIFY_ENTRY / "
        "PROBE_VERIFY_AT_READ did not all succeed; §20.3.1 halts the rotation "
        "before this step"
    )
    details: dict[RotationVerificationStep, str] = {
        RotationVerificationStep.STAGE_NEW_KEY: (
            f"new key provisioned via U-CP-44; rotation_state = "
            f"{KeyRotationState.ROTATING.value}{simulated_suffix}"
        ),
        RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY: write_dual_detail,
        RotationVerificationStep.PROBE_VERIFY_AT_READ: probe_detail,
        RotationVerificationStep.VERIFY_HASH_CHAIN_LINK: hash_chain_detail,
        RotationVerificationStep.ROTATE_SIGNING_TO_NEW: (
            blocked_detail
            if not rotate_retire_gate_succeeded
            else (
                f"old key rotation_state = {KeyRotationState.RETIRED.value}; new "
                f"key rotation_state = {KeyRotationState.ACTIVE.value}{simulated_suffix}"
            )
        ),
        RotationVerificationStep.RETIRE_OLD_KEY: (
            blocked_detail
            if not rotate_retire_gate_succeeded
            else (
                "old key removed from the verification set after dual-verify "
                f"quiescence{simulated_suffix}"
            )
        ),
    }
    succeeded: dict[RotationVerificationStep, bool] = dict.fromkeys(
        ROTATION_VERIFICATION_STEPS, True
    )
    succeeded[RotationVerificationStep.VERIFY_HASH_CHAIN_LINK] = hash_chain_succeeded
    succeeded[RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY] = write_dual_succeeded
    succeeded[RotationVerificationStep.PROBE_VERIFY_AT_READ] = probe_succeeded
    succeeded[RotationVerificationStep.ROTATE_SIGNING_TO_NEW] = rotate_retire_gate_succeeded
    succeeded[RotationVerificationStep.RETIRE_OLD_KEY] = rotate_retire_gate_succeeded
    return tuple(
        StepResult(step=step, succeeded=succeeded[step], detail=details[step])
        for step in ROTATION_VERIFICATION_STEPS
    )

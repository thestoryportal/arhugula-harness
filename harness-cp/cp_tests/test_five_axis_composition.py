"""Tests for U-CP-45 — 5-axis composition + override + key rotation (C-CP-19/20).

Acceptance-criterion coverage:
  #1 5-axis orthogonality        -> test_five_axis_orthogonality
  #1 gate + sandbox independent  -> test_gate_level_and_sandbox_tier_independent
  #2 composition_admissible      -> test_composition_admissible_for_valid_inputs
  #3 override scope table        -> test_override_scope_table_match_spec
  #3 lower-gate prohibited @ MTC -> test_lower_gate_prohibited_at_multi_tenant
  #3 raise-gate @ all tiers      -> test_raise_gate_permitted_at_all_tiers
  #3 narrow-palette @ all tiers  -> test_narrow_palette_permitted_at_all_tiers
  #4 override emits audit        -> test_override_emits_audit_regardless_of_tier
  #5 key rotation 2 stages       -> test_key_rotation_two_stages
  #6 rotation 6 steps in order   -> test_rotation_six_steps_in_order
  #8 partial rotation audited    -> test_partial_rotation_state_audited
  B-26 real IS hash-chain wire   -> test_hash_chain_step_valid_multi_entry_ledger
  B-26 real IS hash-chain wire   -> test_hash_chain_step_broken_chain_fails_rotation
  B-26 no-evidence != success    -> test_empty_ledger_does_not_fake_success
"""

from __future__ import annotations

from datetime import UTC, datetime

from harness_as import BlastRadiusTier
from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface, PersonaTier
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.f5_signing_key_resolution import SecretScopeKind, SigningKeyScope
from harness_cp.five_axis_composition import (
    OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE,
    ROTATION_VERIFICATION_STEPS,
    FiveAxisCompositionInput,
    KeyRotationStage,
    OperatorPolicyOverride,
    OverrideKind,
    OverrideRejection,
    OverrideScope,
    RotationVerificationStep,
    apply_operator_policy_override,
    compose_five_axis,
    execute_key_rotation,
    verify_rotation_6_steps,
)
from harness_cp.gate_level_rule import GateLevel
from harness_cp.rotation_pair_verification import (
    RotationBoundaryPhysicalKeyCollisionError,
    RotationPairEvidence,
    RotationPairEvidenceUnavailableError,
    RotationPairIntegrityBreach,
)
from harness_is.chain_verification import FailureType
from harness_is.entry_hash import compute_response_hash
from harness_is.state_ledger_entry_schema import (
    ALL_ZEROS_SENTINEL,
    Actor,
    ActorClass,
    Identifier,
    StateLedgerEntry,
)


def _input() -> FiveAxisCompositionInput:
    return FiveAxisCompositionInput(
        per_tool_gate_level=GateLevel.AUTO,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        blast_radius_tier=BlastRadiusTier.EXTERNAL_REVERSIBLE,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        mcp_trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        sandbox_tier=SandboxTier.TIER_3_MICROVM,
    )


def _scope() -> SigningKeyScope:
    return SigningKeyScope(scope_kind=SecretScopeKind.TENANT_BOUND, scope_identifier="solo")


def _by_kind(kind: OverrideKind) -> OperatorPolicyOverride:
    return next(o for o in OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE if o.override_kind is kind)


def test_five_axis_orthogonality() -> None:
    """#1 — compose_five_axis carries gate-level and sandbox-tier separately."""
    result = compose_five_axis(_input())
    assert result.gate_level is not None
    assert result.sandbox_tier_floor is SandboxTier.TIER_3_MICROVM


def test_gate_level_and_sandbox_tier_independent() -> None:
    """#1 — gate-level and sandbox-tier are orthogonal: sandbox passes through."""
    for tier in SandboxTier:
        inp = _input().model_copy(update={"sandbox_tier": tier})
        assert compose_five_axis(inp).sandbox_tier_floor is tier


def test_composition_admissible_for_valid_inputs() -> None:
    """#2 — composition_admissible is true for valid input tuples."""
    assert compose_five_axis(_input()).composition_admissible is True


def test_override_scope_table_match_spec() -> None:
    """#3 — OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE has the 3 §19.5 entries."""
    assert len(OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE) == 3
    assert {o.override_kind for o in OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE} == set(OverrideKind)
    for o in OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE:
        assert o.audit_required is True
        assert isinstance(o.scope, OverrideScope)


def test_lower_gate_prohibited_at_multi_tenant() -> None:
    """#3 — LOWER_GATE_LEVEL is prohibited at MULTI_TENANT_COMPLIANCE."""
    lower = _by_kind(OverrideKind.LOWER_GATE_LEVEL)
    assert PersonaTier.MULTI_TENANT_COMPLIANCE not in lower.permitted_at
    assert PersonaTier.SOLO_DEVELOPER in lower.permitted_at
    assert PersonaTier.TEAM_BINDING in lower.permitted_at
    base = compose_five_axis(_input())
    rejection = apply_operator_policy_override(base, lower, PersonaTier.MULTI_TENANT_COMPLIANCE)
    assert isinstance(rejection, OverrideRejection)


def test_raise_gate_permitted_at_all_tiers() -> None:
    """#3 — RAISE_GATE_LEVEL is permitted at all three persona tiers."""
    assert _by_kind(OverrideKind.RAISE_GATE_LEVEL).permitted_at == frozenset(PersonaTier)


def test_narrow_palette_permitted_at_all_tiers() -> None:
    """#3 — NARROW_PALETTE is permitted at all three persona tiers."""
    assert _by_kind(OverrideKind.NARROW_PALETTE).permitted_at == frozenset(PersonaTier)


def test_override_emits_audit_regardless_of_tier() -> None:
    """#4 — every override entry has audit_required = true."""
    assert all(o.audit_required for o in OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE)
    # A permitted override applies (returns the base result).
    base = compose_five_axis(_input())
    applied = apply_operator_policy_override(
        base, _by_kind(OverrideKind.RAISE_GATE_LEVEL), PersonaTier.SOLO_DEVELOPER
    )
    assert not isinstance(applied, OverrideRejection)


def test_key_rotation_two_stages() -> None:
    """#5 — KeyRotationStage declares the two §20.3 rows."""
    assert len(KeyRotationStage) == 2
    assert {s.value for s in KeyRotationStage} == {
        "row-1-dual-verify-active",
        "row-2-retire-old",
    }


def test_rotation_six_steps_in_order() -> None:
    """#6 — verify_rotation_6_steps runs the §20.3.1 six steps in order.

    Backed by a real (non-empty) chain-verifiable ledger — an empty ledger
    no longer counts as a passing hash-chain step (B-26 round-3 fix; see
    `test_empty_ledger_does_not_fake_success`). Without a rotation window /
    evidence provider, WRITE_DUAL_VERIFY_ENTRY and PROBE_VERIFY_AT_READ are
    NOW real (B-33) and report explicit incomplete — see
    `test_full_rotation_pass_with_genuine_evidence_and_distinct_keys` for the
    all-succeeded happy path.
    """
    results = verify_rotation_6_steps(_scope(), audit_ledger_entries=_valid_ledger(1))
    assert len(results) == 6
    assert tuple(r.step for r in results) == ROTATION_VERIFICATION_STEPS
    assert ROTATION_VERIFICATION_STEPS[0] is RotationVerificationStep.STAGE_NEW_KEY
    assert ROTATION_VERIFICATION_STEPS[-1] is RotationVerificationStep.RETIRE_OLD_KEY
    by_step = {r.step: r for r in results}
    assert by_step[RotationVerificationStep.STAGE_NEW_KEY].succeeded is True
    assert by_step[RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY].succeeded is False
    assert by_step[RotationVerificationStep.PROBE_VERIFY_AT_READ].succeeded is False


def test_full_rotation_pass_with_genuine_evidence_and_distinct_keys() -> None:
    """B-33 — the ALL-succeeded happy path: a valid window + a stub provider
    forcing `signatures_verified=True` + a resolver confirming distinct
    physical keys drives every step to succeed (out-of-family review
    round-3 [P1] reachability witness — no shipped provider can produce
    `signatures_verified=True` today, so this uses a test-local stub to
    prove the gate composition is real)."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(evidence=_genuine_pass_evidence())
    resolver = _FakeKeyIdentityResolver({"key-out": "physical-a", "key-in": "physical-b"})
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=provider,
        key_identity_resolver=resolver,
    )
    assert all(r.succeeded for r in results)
    assert provider.calls == [_ROTATION_CORRELATION_ID]


def test_partial_rotation_state_audited() -> None:
    """#8 — a rotation missing window/evidence stays partial (ROW_1); with
    full genuine fixtures it reaches ROW_2 and `rotation_state_partial=False`.
    """
    outcome = execute_key_rotation(_scope(), audit_ledger_entries=_valid_ledger(1))
    assert outcome.rotation_complete is False
    assert outcome.final_stage is KeyRotationStage.ROW_1_DUAL_VERIFY_ACTIVE
    assert outcome.rotation_state_partial is True

    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(evidence=_genuine_pass_evidence())
    resolver = _FakeKeyIdentityResolver({"key-out": "physical-a", "key-in": "physical-b"})
    complete_outcome = execute_key_rotation(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=provider,
        key_identity_resolver=resolver,
    )
    assert complete_outcome.rotation_complete is True
    assert complete_outcome.final_stage is KeyRotationStage.ROW_2_RETIRE_OLD
    assert complete_outcome.rotation_state_partial is False


def test_empty_ledger_does_not_fake_success() -> None:
    """B-26 round-3 (Codex out-of-family) — the no-args default no longer
    fakes a completed rotation from zero evidence.

    Discriminating witness: reverting to `chain_result.failure_type is None`
    alone (dropping the `not audit_ledger_entries` guard) would make this
    test fail, since `verify_chain([])` is trivially `VALID`.
    """
    results = verify_rotation_6_steps(_scope())
    hash_chain_result = next(
        r for r in results if r.step is RotationVerificationStep.VERIFY_HASH_CHAIN_LINK
    )
    assert hash_chain_result.succeeded is False
    assert "no audit_ledger_entries" in hash_chain_result.detail

    outcome = execute_key_rotation(_scope())
    assert outcome.rotation_complete is False
    assert outcome.final_stage is KeyRotationStage.ROW_1_DUAL_VERIFY_ACTIVE


def _ledger_entry(
    action_id: str, prior_event_hash: bytes, *, rotation_correlation_id: str | None = None
) -> StateLedgerEntry:
    """Build a self-consistent entry — mirrors `test_chain_verification._entry`."""
    draft = StateLedgerEntry(
        action_id=Identifier(action_id),
        idempotency_key=Identifier(f"idem-{action_id}"),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-1"),
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=datetime(2026, 7, 13, tzinfo=UTC),
        prior_event_hash=prior_event_hash,
        rotation_correlation_id=rotation_correlation_id,
    )
    return draft.model_copy(update={"response_hash": compute_response_hash(draft)})


def _valid_ledger(n: int) -> list[StateLedgerEntry]:
    chain: list[StateLedgerEntry] = []
    prior = ALL_ZEROS_SENTINEL
    for i in range(n):
        entry = _ledger_entry(f"rotate-act-{i}", prior)
        chain.append(entry)
        prior = compute_response_hash(entry)
    return chain


_ROTATION_CORRELATION_ID = "1c1b0b3e-3e3e-4e3e-8e3e-3e3e3e3e3e3e"


def _valid_ledger_with_rotation_window(
    n: int,
) -> tuple[list[StateLedgerEntry], list[StateLedgerEntry]]:
    """A genesis-anchored chain of `n` entries where the LAST TWO carry a
    shared `rotation_correlation_id` — returns `(full_chain, window)`."""
    chain: list[StateLedgerEntry] = []
    prior = ALL_ZEROS_SENTINEL
    for i in range(n):
        tagged = i >= n - 2
        entry = _ledger_entry(
            f"rotate-act-{i}",
            prior,
            rotation_correlation_id=_ROTATION_CORRELATION_ID if tagged else None,
        )
        chain.append(entry)
        prior = compute_response_hash(entry)
    return chain, chain[-2:]


class _FakeEvidenceProvider:
    """Test-local `RotationPairEvidenceProvider` returning a canned evidence
    object (or raising)."""

    def __init__(
        self,
        evidence: RotationPairEvidence | None = None,
        raise_exc: BaseException | None = None,
    ) -> None:
        self.evidence = evidence
        self.raise_exc = raise_exc
        self.calls: list[str] = []

    def evidence_for(self, correlation_id: str) -> RotationPairEvidence:
        self.calls.append(correlation_id)
        if self.raise_exc is not None:
            raise self.raise_exc
        assert self.evidence is not None
        return self.evidence


class _FakeKeyIdentityResolver:
    """Test-local `KeyIdentityResolver` over an explicit label->identity map."""

    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def physical_identity_for(self, key_id: str) -> str:
        return self.mapping[key_id]


def _genuine_pass_evidence() -> RotationPairEvidence:
    """A stub evidence object with `signatures_verified=True` — proves the
    gate composition is reachable in principle, even though no shipped
    provider in this delta can produce it (OD spec v1.35 §24.8 row 8a)."""
    return RotationPairEvidence(
        correlation_id=_ROTATION_CORRELATION_ID,
        pair_present=True,
        outgoing_key_period=3,
        incoming_key_period=4,
        outgoing_key_id="key-out",
        incoming_key_id="key-in",
        signatures_verified=True,
    )


def test_hash_chain_step_valid_multi_entry_ledger() -> None:
    """B-26 — VERIFY_HASH_CHAIN_LINK calls the real IS `verify_chain`, not a stub."""
    ledger = _valid_ledger(4)
    results = verify_rotation_6_steps(_scope(), audit_ledger_entries=ledger)
    by_step = {r.step: r for r in results}
    hash_chain_result = by_step[RotationVerificationStep.VERIFY_HASH_CHAIN_LINK]
    assert hash_chain_result.succeeded is True
    assert "verify_chain" in hash_chain_result.detail
    assert "4 entries" in hash_chain_result.detail
    # STAGE_NEW_KEY stays simulated True; WRITE_DUAL_VERIFY_ENTRY and
    # PROBE_VERIFY_AT_READ are NOW real (B-33) and report explicit
    # incomplete without a window/evidence provider — independent of
    # VERIFY_HASH_CHAIN_LINK's own (here-passing) result.
    assert by_step[RotationVerificationStep.STAGE_NEW_KEY].succeeded is True
    assert by_step[RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY].succeeded is False
    assert by_step[RotationVerificationStep.PROBE_VERIFY_AT_READ].succeeded is False
    # ROTATE/RETIRE are still blocked — gated on ALL THREE of {hash-chain,
    # write-dual, probe} succeeding, and the latter two are absent here.
    assert by_step[RotationVerificationStep.ROTATE_SIGNING_TO_NEW].succeeded is False
    assert by_step[RotationVerificationStep.RETIRE_OLD_KEY].succeeded is False


def test_hash_chain_step_broken_chain_fails_rotation() -> None:
    """B-26 — a genuinely broken chain fails the step for real (not hardcoded True).

    Discriminating witness: reverting the wiring back to `succeeded=True`
    hardcoded would make this test fail.
    """
    ledger = _valid_ledger(4)
    tampered = list(ledger)
    tampered[2] = _ledger_entry("rotate-act-2", b"\x09" * 32)  # break the link into position 3

    results = verify_rotation_6_steps(_scope(), audit_ledger_entries=tampered)
    by_step = {r.step: r for r in results}
    hash_chain_result = by_step[RotationVerificationStep.VERIFY_HASH_CHAIN_LINK]
    assert hash_chain_result.succeeded is False
    assert "position 3" in hash_chain_result.detail
    assert FailureType.CHAIN_LINK_MISMATCH.value in hash_chain_result.detail

    # STAGE_NEW_KEY still narrates simulated success. WRITE_DUAL_VERIFY_ENTRY
    # / PROBE_VERIFY_AT_READ are real (B-33) and fail here for their OWN
    # reason (no window/evidence supplied) — NOT because VERIFY_HASH_CHAIN_
    # LINK failed (out-of-family review round-3 [P2]: VERIFY_HASH_CHAIN_LINK
    # stays UNCHANGED/independent, an ordinal-sequencing scope narrowing).
    assert by_step[RotationVerificationStep.STAGE_NEW_KEY].succeeded is True
    assert by_step[RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY].succeeded is False
    assert by_step[RotationVerificationStep.PROBE_VERIFY_AT_READ].succeeded is False
    for step in (
        RotationVerificationStep.ROTATE_SIGNING_TO_NEW,
        RotationVerificationStep.RETIRE_OLD_KEY,
    ):
        assert by_step[step].succeeded is False
        assert "blocked" in by_step[step].detail

    outcome = execute_key_rotation(_scope(), audit_ledger_entries=tampered)
    assert outcome.rotation_complete is False
    assert outcome.final_stage is KeyRotationStage.ROW_1_DUAL_VERIFY_ACTIVE
    assert outcome.rotation_state_partial is True


# --- B-33 leg (iii) — verify_rotation_6_steps real extension ---------------


def test_write_dual_verify_entry_rejects_window_entry_absent_from_audit_ledger_entries() -> None:
    """Out-of-family review round-3 [P1] correction — a fabricated window
    entry (same rotation_correlation_id tag, never actually written to the
    authenticated chain) must NOT pass presence/uniqueness. Mutation probe:
    skipping the subset-membership check lets this fabricated window pass.
    """
    chain, _real_window = _valid_ledger_with_rotation_window(4)
    fabricated_entry = _ledger_entry(
        "fabricated-not-in-chain",
        ALL_ZEROS_SENTINEL,
        rotation_correlation_id=_ROTATION_CORRELATION_ID,
    )
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=[fabricated_entry, chain[-1]],
    )
    by_step = {r.step: r for r in results}
    write_dual = by_step[RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY]
    assert write_dual.succeeded is False
    assert "not present in audit_ledger_entries" in write_dual.detail


def test_write_dual_verify_entry_valid_window_extracts_the_single_correlation_id() -> None:
    """The extracted id used downstream equals the window's own value —
    mutation probe: a caller-supplied id parameter doesn't exist to diverge
    from it (out-of-family review round-1 [P1])."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(evidence=_genuine_pass_evidence())
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=provider,
    )
    by_step = {r.step: r for r in results}
    assert by_step[RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY].succeeded is True
    assert provider.calls == [_ROTATION_CORRELATION_ID]


def test_probe_verify_at_read_pair_absent_reports_explicit_incomplete() -> None:
    """OD spec v1.35 §24.8 absence-is-not-a-breach — an absent pair FAILS
    the step with an EXPLICIT detail, distinct from a tamper raise."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(
        evidence=RotationPairEvidence(correlation_id=_ROTATION_CORRELATION_ID, pair_present=False)
    )
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=provider,
    )
    probe = next(r for r in results if r.step is RotationVerificationStep.PROBE_VERIFY_AT_READ)
    assert probe.succeeded is False
    assert "no OD-anchored evidence" in probe.detail


def test_probe_verify_at_read_structural_only_reports_explicit_incomplete_not_success() -> None:
    """Out-of-family review round-2 [P1] correction — `pair_present=True`
    with `signatures_verified=False` (every shipped provider in this delta)
    is an EXPLICIT incomplete disposition, NOT a pass. Mutation probe:
    treating `pair_present=True` alone as sufficient passes this incorrectly."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(
        evidence=RotationPairEvidence(
            correlation_id=_ROTATION_CORRELATION_ID,
            pair_present=True,
            outgoing_key_period=3,
            incoming_key_period=4,
            outgoing_key_id="key-out",
            incoming_key_id="key-in",
            signatures_verified=False,
        )
    )
    resolver = _FakeKeyIdentityResolver({"key-out": "physical-a", "key-in": "physical-b"})
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=provider,
        key_identity_resolver=resolver,
    )
    probe = next(r for r in results if r.step is RotationVerificationStep.PROBE_VERIFY_AT_READ)
    assert probe.succeeded is False
    assert "signature verification not available" in probe.detail


def test_probe_verify_at_read_evidence_correlation_id_mismatch_raises_unavailable_error() -> None:
    """Out-of-family review round-2 [P2] correction — a provider returning
    evidence for a DIFFERENT id than requested is a defect, never silently
    accepted. Mutation probe: skipping the echo-check assertion lets a
    mismatched-id evidence object silently pass through."""
    chain, window = _valid_ledger_with_rotation_window(4)
    mismatched = RotationPairEvidence(correlation_id="not-the-requested-id", pair_present=False)
    provider = _FakeEvidenceProvider(evidence=mismatched)
    try:
        verify_rotation_6_steps(
            _scope(),
            audit_ledger_entries=chain,
            rotation_window_entries=window,
            evidence_provider=provider,
        )
        raised = False
    except RotationPairEvidenceUnavailableError as exc:
        raised = True
        assert "correlation-id mismatch" in str(exc)
    assert raised


def test_probe_verify_at_read_integrity_breach_propagates_uncaught() -> None:
    """A `RotationPairIntegrityBreach` from the injected provider (OD-
    detected tamper) PROPAGATES as a raised exception out of
    `verify_rotation_6_steps` — NEVER caught and folded into a
    `StepResult(succeeded=False)` (CP plan v2.41 U-CP-45 criterion #4).
    Mutation probe: wrapping the provider call in a try/except that returns
    a failed StepResult instead of re-raising makes this test fail."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(raise_exc=RotationPairIntegrityBreach("tampered pair"))
    try:
        verify_rotation_6_steps(
            _scope(),
            audit_ledger_entries=chain,
            rotation_window_entries=window,
            evidence_provider=provider,
        )
        raised = False
    except RotationPairIntegrityBreach:
        raised = True
    assert raised


def test_probe_verify_at_read_unavailable_error_propagates_uncaught() -> None:
    """A `RotationPairEvidenceUnavailableError` from the injected provider
    (infrastructure availability) ALSO propagates unwrapped — never a
    verdict folded into a StepResult."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(raise_exc=RotationPairEvidenceUnavailableError("backend down"))
    try:
        verify_rotation_6_steps(
            _scope(),
            audit_ledger_entries=chain,
            rotation_window_entries=window,
            evidence_provider=provider,
        )
        raised = False
    except RotationPairEvidenceUnavailableError:
        raised = True
    assert raised


def test_probe_verify_at_read_key_identity_resolver_absent_reports_explicit_incomplete() -> None:
    """CP spec v1.105 §2 row 5 — `key_identity_resolver` absence is NOT a
    silent skip: it yields the SAME explicit-incomplete disposition as an
    absent `evidence_provider`, even when the OD evidence is otherwise a
    genuine structural + signature pass."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(evidence=_genuine_pass_evidence())
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=provider,
        key_identity_resolver=None,
    )
    probe = next(r for r in results if r.step is RotationVerificationStep.PROBE_VERIFY_AT_READ)
    assert probe.succeeded is False
    assert "key_identity_resolver" in probe.detail


def test_probe_verify_at_read_physical_key_collision_raises_uncaught() -> None:
    """CP spec v1.105 §2 row 5 — two `key_id` LABELS resolving to the SAME
    physical identity raises `RotationBoundaryPhysicalKeyCollisionError`,
    DISTINCT from `RotationPairIntegrityBreach` (the OD-side pair may be
    perfectly well-formed while the physical keys are the same underlying
    material under two labels). Mutation probe: comparing key_id STRINGS
    instead of resolved physical identities would pass this pair (the
    labels DO differ) and miss the collision."""
    chain, window = _valid_ledger_with_rotation_window(4)
    provider = _FakeEvidenceProvider(evidence=_genuine_pass_evidence())
    resolver = _FakeKeyIdentityResolver(
        {"key-out": "SAME-PHYSICAL-KEY", "key-in": "SAME-PHYSICAL-KEY"}
    )
    try:
        verify_rotation_6_steps(
            _scope(),
            audit_ledger_entries=chain,
            rotation_window_entries=window,
            evidence_provider=provider,
            key_identity_resolver=resolver,
        )
        raised = False
    except RotationBoundaryPhysicalKeyCollisionError:
        raised = True
    assert raised

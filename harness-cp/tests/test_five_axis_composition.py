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
    `test_empty_ledger_does_not_fake_success`).
    """
    results = verify_rotation_6_steps(_scope(), audit_ledger_entries=_valid_ledger(1))
    assert len(results) == 6
    assert tuple(r.step for r in results) == ROTATION_VERIFICATION_STEPS
    assert ROTATION_VERIFICATION_STEPS[0] is RotationVerificationStep.STAGE_NEW_KEY
    assert ROTATION_VERIFICATION_STEPS[-1] is RotationVerificationStep.RETIRE_OLD_KEY
    assert all(r.succeeded for r in results)


def test_partial_rotation_state_audited() -> None:
    """#8 — a completed rotation reaches ROW_2; rotation_state_partial false.

    Backed by a real (non-empty) chain-verifiable ledger — see
    `test_rotation_six_steps_in_order`.
    """
    outcome = execute_key_rotation(_scope(), audit_ledger_entries=_valid_ledger(1))
    assert outcome.rotation_complete is True
    assert outcome.final_stage is KeyRotationStage.ROW_2_RETIRE_OLD
    assert outcome.rotation_state_partial is False


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


def _ledger_entry(action_id: str, prior_event_hash: bytes) -> StateLedgerEntry:
    """Build a self-consistent entry — mirrors `test_chain_verification._entry`."""
    draft = StateLedgerEntry(
        action_id=Identifier(action_id),
        idempotency_key=Identifier(f"idem-{action_id}"),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-1"),
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=datetime(2026, 7, 13, tzinfo=UTC),
        prior_event_hash=prior_event_hash,
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


def test_hash_chain_step_valid_multi_entry_ledger() -> None:
    """B-26 — VERIFY_HASH_CHAIN_LINK calls the real IS `verify_chain`, not a stub."""
    ledger = _valid_ledger(4)
    results = verify_rotation_6_steps(_scope(), audit_ledger_entries=ledger)
    hash_chain_result = next(
        r for r in results if r.step is RotationVerificationStep.VERIFY_HASH_CHAIN_LINK
    )
    assert hash_chain_result.succeeded is True
    assert "verify_chain" in hash_chain_result.detail
    assert "4 entries" in hash_chain_result.detail
    # Every other step still narrates the (still-simulated) signing side.
    assert all(
        r.succeeded
        for r in results
        if r.step is not RotationVerificationStep.VERIFY_HASH_CHAIN_LINK
    )


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

    # Steps preceding the failed gate in §20.3.1 protocol order still report
    # their (simulated) narration; steps AFTER it are blocked, not
    # independently claiming success (Codex out-of-family P2).
    for step in (
        RotationVerificationStep.STAGE_NEW_KEY,
        RotationVerificationStep.WRITE_DUAL_VERIFY_ENTRY,
        RotationVerificationStep.PROBE_VERIFY_AT_READ,
    ):
        assert by_step[step].succeeded is True
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

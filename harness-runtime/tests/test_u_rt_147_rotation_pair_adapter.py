"""`U-RT-147` — the composition-root adapter: real OD §24.8 accessor through
the CP-owned `RotationPairEvidenceProvider` Protocol through
`verify_rotation_6_steps` (Runtime spec v1.105 §13.6 / CP spec v1.105 §2).

The CP-side witnesses (`harness-cp/tests/test_five_axis_composition.py`)
drive the gate with FAKE providers; these are the integration halves: the
REAL `find_rotation_pair_evidence` behind `OdRotationPairEvidenceAdapter`
behind `verify_rotation_6_steps`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from harness_core import DeploymentSurface, PersonaTier
from harness_cp.f5_signing_key_resolution import SecretScopeKind, SigningKeyScope
from harness_cp.five_axis_composition import (
    RotationVerificationStep,
    verify_rotation_6_steps,
)
from harness_cp.rotation_pair_verification import RotationPairIntegrityBreach
from harness_is.entry_hash import compute_response_hash
from harness_is.state_ledger_entry_schema import (
    ALL_ZEROS_SENTINEL,
    Actor,
    ActorClass,
    Identifier,
    StateLedgerEntry,
)
from harness_od.audit_ledger_types import AuditLedger, SignatureAlgorithm, StateLedgerEntryRef
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    RotationPairEvidence as OdRotationPairEvidence,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    sign_rotation_pair,
)
from harness_od.observability_matrix import CellID
from harness_runtime.lifecycle.rotation_pair_adapter import (
    OdRotationPairEvidenceAdapter,
    build_key_identity_resolver_from_mapping,
    build_rotation_pair_evidence_provider,
)


def _cell() -> CellID:
    return CellID(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
    )


def _scope() -> SigningKeyScope:
    return SigningKeyScope(scope_kind=SecretScopeKind.TENANT_BOUND, scope_identifier="rt147")


def _is_entry(
    action_id: str, prior_event_hash: bytes, *, rotation_correlation_id: str | None
) -> StateLedgerEntry:
    draft = StateLedgerEntry(
        action_id=Identifier(action_id),
        idempotency_key=Identifier(f"idem-{action_id}"),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-1"),
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=datetime(2026, 7, 23, tzinfo=UTC),
        prior_event_hash=prior_event_hash,
        rotation_correlation_id=rotation_correlation_id,
    )
    return draft.model_copy(update={"response_hash": compute_response_hash(draft)})


def _od_ledger_with_real_pair() -> tuple[AuditLedger, str]:
    """Build a REAL, genuinely-signed OD rotation pair via `sign_rotation_pair`
    (the actual write path this leg's read-side accessor consumes) — returns
    the ledger + the correlation id `sign_rotation_pair` generated."""
    outgoing, incoming = sign_rotation_pair(
        outgoing_entry_core=StateLedgerEntryRef("rt147-outgoing"),
        outgoing_prior_entry_hash="genesis",
        incoming_entry_core=StateLedgerEntryRef("rt147-incoming"),
        outgoing_key_id="rt147-key-out",
        outgoing_key_period=1,
        incoming_key_id="rt147-key-in",
        incoming_key_period=2,
        algo=SignatureAlgorithm.ED25519,
    )
    correlation_id = outgoing.payload.audit_namespace_attrs["audit.rotation_correlation_id"]
    ledger = AuditLedger(entries=(outgoing, incoming), cell_id=_cell())
    return ledger, correlation_id


def _is_chain_with_window(
    correlation_id: str,
) -> tuple[list[StateLedgerEntry], list[StateLedgerEntry]]:
    chain: list[StateLedgerEntry] = []
    prior = ALL_ZEROS_SENTINEL
    for i in range(4):
        tagged = i >= 2
        entry = _is_entry(
            f"rt147-is-act-{i}",
            prior,
            rotation_correlation_id=correlation_id if tagged else None,
        )
        chain.append(entry)
        prior = compute_response_hash(entry)
    return chain, chain[-2:]


def test_rt147_adapter_real_od_find_rotation_pair_evidence_absent_path() -> None:
    """Integration — a REAL OD ledger with NO matching correlation id drives
    `PROBE_VERIFY_AT_READ` to the explicit-incomplete disposition through
    the FULL real chain (OD `find_rotation_pair_evidence` → adapter → CP
    `verify_rotation_6_steps`), never a silent pass."""
    _real_ledger, real_correlation_id = _od_ledger_with_real_pair()
    empty_ledger = AuditLedger(entries=(), cell_id=_cell())
    adapter = build_rotation_pair_evidence_provider(empty_ledger)
    chain, window = _is_chain_with_window(real_correlation_id)
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=adapter,
    )
    probe = next(r for r in results if r.step is RotationVerificationStep.PROBE_VERIFY_AT_READ)
    assert probe.succeeded is False
    assert "no OD-anchored evidence" in probe.detail


def test_rt147_adapter_real_od_find_rotation_pair_evidence_tampered_path() -> None:
    """Integration — a REAL, tampered OD pair drives a `RotationPairIntegrityBreach`
    raise through the adapter unchanged — mutation probe: reverting the
    adapter's exception re-raise to a swallow-and-return-false makes the
    tampered-pair case silently report `succeeded=False` instead of
    raising, failing this test."""
    ledger, correlation_id = _od_ledger_with_real_pair()
    tampered_incoming = ledger.entries[1].model_copy(
        update={
            "signature_attrs": ledger.entries[1].signature_attrs.model_copy(
                update={"audit_signature_key_period": "99"}
            )
        }
    )
    tampered_ledger = AuditLedger(entries=(ledger.entries[0], tampered_incoming), cell_id=_cell())
    adapter = build_rotation_pair_evidence_provider(tampered_ledger)
    chain, window = _is_chain_with_window(correlation_id)
    with pytest.raises(RotationPairIntegrityBreach):
        verify_rotation_6_steps(
            _scope(),
            audit_ledger_entries=chain,
            rotation_window_entries=window,
            evidence_provider=adapter,
        )


def test_rt147_adapter_real_od_find_rotation_pair_evidence_valid_pair_reports_incomplete() -> None:
    """Integration — a genuinely VALID OD pair through the REAL accessor
    still reports the explicit-incomplete disposition (never `succeeded=
    True`), because `find_rotation_pair_evidence` always returns
    `signatures_verified=False` in this delta (OD spec v1.35 §24.8 row 8a —
    no rotation-period-aware cryptographic verifier exists yet). Mutation
    probe: hardcoding the adapter's mapped `signatures_verified` to `True`
    for a valid pair passes this test incorrectly and must be rejected."""
    ledger, correlation_id = _od_ledger_with_real_pair()
    adapter = build_rotation_pair_evidence_provider(ledger)
    resolver = build_key_identity_resolver_from_mapping(
        {"rt147-key-out": "physical-a", "rt147-key-in": "physical-b"}
    )
    chain, window = _is_chain_with_window(correlation_id)
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=adapter,
        key_identity_resolver=resolver,
    )
    probe = next(r for r in results if r.step is RotationVerificationStep.PROBE_VERIFY_AT_READ)
    assert probe.succeeded is False
    assert "signature verification not available" in probe.detail


def test_rt147_adapter_maps_signatures_verified_field_verbatim_never_hardcoded() -> None:
    """The adapter maps `signatures_verified` verbatim from OD's evidence —
    it never hardcodes a constant regardless of what OD returns.

    Out-of-family review round-1 [P2] correction: the real OD accessor
    always returns `False` in this delta, so a version of this test that
    only drove the real accessor would still pass even if the adapter
    hardcoded `signatures_verified=True` — every OTHER RT-147 test would
    also still pass, since none of them can observe a `True` from OD
    today. This test therefore monkeypatches OD's own accessor to return
    `True` for one call and `False` for another, and asserts the adapter's
    mapped output tracks each value exactly — proving the mapping is
    genuinely verbatim, not a hardcoded constant of either polarity."""
    ledger, correlation_id = _od_ledger_with_real_pair()
    adapter = OdRotationPairEvidenceAdapter(ledger=ledger)

    real_evidence = adapter.evidence_for(correlation_id)
    assert real_evidence.signatures_verified is False
    assert real_evidence.pair_present is True

    stub_true = OdRotationPairEvidence(
        correlation_id=correlation_id,
        pair_present=True,
        outgoing_key_period=1,
        incoming_key_period=2,
        outgoing_key_id="stub-out",
        incoming_key_id="stub-in",
        signatures_verified=True,
    )
    with patch(
        "harness_runtime.lifecycle.rotation_pair_adapter.find_rotation_pair_evidence",
        return_value=stub_true,
    ):
        mapped = adapter.evidence_for(correlation_id)
    assert mapped.signatures_verified is True
    assert mapped.pair_present is True


def test_rt147_and_rt138_factories_independent() -> None:
    """Constructing this unit's adapter via its factory does not require
    the audit-walk verifier's inputs, and vice versa — the two injected
    verifiers are wired independently."""
    ledger = AuditLedger(entries=(), cell_id=_cell())
    provider = build_rotation_pair_evidence_provider(ledger)
    assert provider is not None


def test_rt147_evidence_provider_factory_never_needs_or_raises_for_a_resolver() -> None:
    """`build_rotation_pair_evidence_provider` (the evidence-provider
    factory) NEVER RAISES, and its construction does not depend on a
    `key_identity_resolver` at all — the two injected seams are
    independently constructed (out-of-family review round-4 [P2] wording
    correction: "required" describes the DOWNSTREAM CP-side gate posture,
    not a precondition on this factory). Running the full gate with
    `key_identity_resolver=None` against a REAL OD pair reports the
    explicit-incomplete disposition — here it is the earlier
    `signatures_verified` gate (every real OD pair has `signatures_verified
    =False` today), since that check runs BEFORE the resolver is even
    consulted; the resolver-absence-specific disposition (reached only past
    a `signatures_verified=True` pair) is covered CP-side with a stub
    (`test_probe_verify_at_read_key_identity_resolver_absent_reports_explicit_incomplete`)."""
    ledger, correlation_id = _od_ledger_with_real_pair()
    adapter = build_rotation_pair_evidence_provider(ledger)
    assert adapter is not None
    chain, window = _is_chain_with_window(correlation_id)
    results = verify_rotation_6_steps(
        _scope(),
        audit_ledger_entries=chain,
        rotation_window_entries=window,
        evidence_provider=adapter,
        key_identity_resolver=None,
    )
    probe = next(r for r in results if r.step is RotationVerificationStep.PROBE_VERIFY_AT_READ)
    assert probe.succeeded is False
    assert "signature verification not available" in probe.detail


def test_rt147_key_identity_resolver_factory_raises_on_unknown_key() -> None:
    """`build_key_identity_resolver_from_mapping` does NOT fabricate a
    resolver where none exists — an unmapped `key_id` raises `KeyError`,
    propagating unwrapped rather than silently treated as a match."""
    resolver = build_key_identity_resolver_from_mapping({})
    with pytest.raises(KeyError):
        resolver.physical_identity_for("unknown-key")


def test_rt147_key_identity_resolver_factory_takes_defensive_copy_of_mapping() -> None:
    """Merge-gate concurrency lens finding — the factory copies the
    supplied mapping rather than aliasing it; mutating the caller's dict
    AFTER construction must not change what an already-built resolver
    reports (a resolver built once at composition-root startup and reused
    across concurrent calls must not observe a caller-side in-place
    mutation). Mutation probe: aliasing the raw dict (dropping the
    `dict(mapping)` copy) makes this test fail."""
    live_mapping = {"key-a": "physical-a"}
    resolver = build_key_identity_resolver_from_mapping(live_mapping)
    live_mapping["key-a"] = "physical-a-mutated"
    assert resolver.physical_identity_for("key-a") == "physical-a"

"""Tests for U-OD-30 — per-tenant trace separation + cryptographic audit ledger.

Every materializable U-OD-30 acceptance criterion maps to >=1 test below. ACs
#11 (always-sampled audit ledger — composes with U-OD-11) and #12 (cross-axis
IS/CP edges) resolve at sub-phase 7c and are documented in the module docstring
rather than tested here — they are not within-axis materializable surfaces.
Authority: Implementation_Plan_Operational_Discipline_v2_7.md §3.7.4 (delta
chain over v2.6/v2.5/v2.1 §3.7.4); Spec_Operational_Discipline_v1_2.md §21.
"""

from __future__ import annotations

from typing import Any

import pytest
from harness_core import DeploymentSurface, PersonaTier
from harness_od.audit_ledger_types import (
    AuditLedger,
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.audit_signing_errors import (
    AuditSigningBreakerOpenError,
    AuditSigningFailedError,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER,
    PER_TENANT_SEPARATION_BINDINGS,
    ROTATION_CORRELATION_ID_ATTR,
    HashChainBreach,
    PerTenantSeparation,
    RotationPairIntegrityBreach,
    TenantIdMissingViolation,
    TenantSeparationStrategy,
    assert_tenant_id_on_every_span_at_multi_tenant_cells,
    sidecar_tag,
    sign_audit_entry,
    sign_rotation_pair,
    signing_token,
    verify_hash_chain_integrity,
    verify_rotation_pairs,
)
from harness_od.observability_matrix import CellID


def _cell(pt: PersonaTier, ds: DeploymentSurface) -> CellID:
    return CellID(persona_tier=pt, deployment_surface=ds)


_CELL_1 = _cell(PersonaTier.SOLO_DEVELOPER, DeploymentSurface.LOCAL_DEVELOPMENT)
_CELL_7 = _cell(PersonaTier.MULTI_TENANT_COMPLIANCE, DeploymentSurface.SELF_HOSTED_SERVER)
_CELL_8 = _cell(PersonaTier.MULTI_TENANT_COMPLIANCE, DeploymentSurface.MANAGED_CLOUD)


class _FakeSpan:
    """A minimal OTel-span stand-in carrying an attribute map.

    `SpanRef` is a type-alias of the OTel-SDK span handle; the live span is
    wired at a Phase-2 composition root. This stand-in exercises the
    attribute-read path of `assert_tenant_id_on_every_span_at_multi_tenant_cells`.
    """

    def __init__(self, attributes: dict[str, Any]) -> None:
        self.attributes = attributes


def _payload(prior_hash: str) -> AuditPayload:
    return AuditPayload(
        entry_core=StateLedgerEntryRef("entry-core-ref"),
        audit_namespace_attrs={"audit.actor": "operator"},
        prior_entry_hash=prior_hash,
    )


def _entry(prior_hash: str) -> AuditLedgerEntry:
    """Build an entry with a genuinely self-consistent `entry_hash`.

    `entry_hash` is always `compute_entry_hash(payload)` — a hand-picked
    stand-in value would make every `verify_hash_chain_integrity` content
    check fail regardless of the linkage scenario under test.
    """
    payload = _payload(prior_hash)
    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=AuditSignatureAttributes(
            audit_signature_value="sig",
            audit_signature_algorithm=SignatureAlgorithm.ED25519,
            audit_signature_key_id="key-1",
            audit_signature_key_period="2026-Q2",
        ),
        entry_hash=compute_entry_hash(payload),
    )


# --- acc #1 — TenantSeparationStrategy 2 values ----------------------------


def test_tenant_separation_strategy_cardinality_two() -> None:
    """acc #1 — `TenantSeparationStrategy` enumerates exactly 2 values."""
    assert len(list(TenantSeparationStrategy)) == 2


# --- acc #2 — PER_TENANT_SEPARATION_BINDINGS only at cells 7/8 -------------


def test_per_tenant_separation_only_at_multi_tenant_cells() -> None:
    """acc #2 — exactly 2 entries, cell-7 and cell-8 only."""
    assert len(PER_TENANT_SEPARATION_BINDINGS) == 2
    assert set(PER_TENANT_SEPARATION_BINDINGS) == {_CELL_7, _CELL_8}


# --- acc #3 — per-cell strategy --------------------------------------------


def test_cell_7_self_hosted_strategy() -> None:
    """acc #3 — cell-7 -> PER_TENANT_OTLP_COLLECTOR_ROUTING (self-hosted)."""
    assert (
        PER_TENANT_SEPARATION_BINDINGS[_CELL_7].strategy
        == TenantSeparationStrategy.PER_TENANT_OTLP_COLLECTOR_ROUTING
    )


def test_cell_8_managed_cloud_strategy() -> None:
    """acc #3 — cell-8 -> PER_TENANT_BACKEND_PARTITION (managed-cloud)."""
    assert (
        PER_TENANT_SEPARATION_BINDINGS[_CELL_8].strategy
        == TenantSeparationStrategy.PER_TENANT_BACKEND_PARTITION
    )


# --- acc #4 — tenant_id_attribute byte-exact -------------------------------


def test_tenant_id_attribute_byte_exact() -> None:
    """acc #4 — tenant_id_attribute == 'tenant.id' at every binding."""
    for binding in PER_TENANT_SEPARATION_BINDINGS.values():
        assert binding.tenant_id_attribute == "tenant.id"


# --- acc #5 — cross_tenant_aggregation_forbidden ---------------------------


def test_cross_tenant_aggregation_forbidden() -> None:
    """acc #5 — cross_tenant_aggregation_forbidden == True at every binding."""
    for binding in PER_TENANT_SEPARATION_BINDINGS.values():
        assert binding.cross_tenant_aggregation_forbidden is True


# --- acc #6 — SignatureAlgorithm 3 values (U-OD-00 carrier) ----------------


def test_signature_algorithm_cardinality_three() -> None:
    """acc #6 — `SignatureAlgorithm` enumerates exactly 3 values (U-OD-00)."""
    assert len(list(SignatureAlgorithm)) == 3


def test_signature_algorithm_names_byte_exact() -> None:
    """acc #6 — the 3 values are byte-exact with §21.2 / ADR-D5 §1.4.1."""
    assert {a.value for a in SignatureAlgorithm} == {
        "ed25519",
        "ecdsa-p256",
        "rsa-pss-2048",
    }


# --- acc #7 — AuditSignatureAttributes 4 attributes (U-OD-00 carrier) ------


def test_audit_signature_attributes_cardinality_four() -> None:
    """acc #7 — `AuditSignatureAttributes` declares exactly 4 attributes."""
    assert set(AuditSignatureAttributes.model_fields) == {
        "audit_signature_value",
        "audit_signature_algorithm",
        "audit_signature_key_id",
        "audit_signature_key_period",
    }


# --- acc #8 — sign_audit_entry ---------------------------------------------


def test_sign_audit_entry_complete() -> None:
    """acc #8 — sign_audit_entry produces all 4 fields per algo selection."""
    sig = sign_audit_entry(_payload("h0"), "key-1", SignatureAlgorithm.ED25519)
    assert isinstance(sig, AuditSignatureAttributes)
    assert sig.audit_signature_algorithm == SignatureAlgorithm.ED25519
    assert sig.audit_signature_key_id == "key-1"
    assert sig.audit_signature_value
    assert sig.audit_signature_key_period


def test_sign_audit_entry_missing_key_id_reject() -> None:
    """acc #8 — missing key_id rejected at function precondition."""
    with pytest.raises(ValueError, match="key_id is required"):
        sign_audit_entry(_payload("h0"), "", SignatureAlgorithm.ED25519)


# --- acc #9 — verify_hash_chain_integrity ----------------------------------


def test_verify_hash_chain_intact_accept() -> None:
    """acc #9 — verify_hash_chain_integrity returns None for an intact chain."""
    entry_1 = _entry("genesis")
    entry_2 = _entry(entry_1.entry_hash)
    entry_3 = _entry(entry_2.entry_hash)
    ledger = AuditLedger(entries=(entry_1, entry_2, entry_3), cell_id=_CELL_7)
    assert verify_hash_chain_integrity(ledger) is None


def test_verify_hash_chain_broken_reject() -> None:
    """acc #9 — Err(HashChainBreach) when a hash-chain link is broken."""
    entry_1 = _entry("genesis")
    entry_2 = _entry("WRONG")  # does not chain onto entry_1.entry_hash
    ledger = AuditLedger(entries=(entry_1, entry_2), cell_id=_CELL_7)
    with pytest.raises(HashChainBreach, match="hash chain broken"):
        verify_hash_chain_integrity(ledger)


def test_verify_hash_chain_content_tamper_reject() -> None:
    """acc #9 — Err(HashChainBreach) when an entry's payload is mutated in
    place without recomputing its stored `entry_hash` — content-integrity
    check must fire even when every `prior_entry_hash` link still lines up."""
    entry_1 = _entry("genesis")
    entry_2 = _entry(entry_1.entry_hash)
    tampered_payload = entry_2.payload.model_copy(
        update={"audit_namespace_attrs": {"audit.actor": "attacker"}}
    )
    tampered_entry_2 = entry_2.model_copy(update={"payload": tampered_payload})
    ledger = AuditLedger(entries=(entry_1, tampered_entry_2), cell_id=_CELL_7)
    with pytest.raises(HashChainBreach, match="content integrity violated"):
        verify_hash_chain_integrity(ledger)


def test_verify_hash_chain_single_entry_accept() -> None:
    """acc #9 — a single-entry ledger is trivially well-formed."""
    ledger = AuditLedger(entries=(_entry("genesis"),), cell_id=_CELL_8)
    assert verify_hash_chain_integrity(ledger) is None


# --- acc #10 — assert_tenant_id_on_every_span_at_multi_tenant_cells --------


def test_assert_tenant_id_present_accept() -> None:
    """acc #10 — a span carrying tenant.id at cell-7 passes."""
    span = _FakeSpan({"tenant.id": "tenant-a"})
    assert (
        assert_tenant_id_on_every_span_at_multi_tenant_cells(span, _CELL_7)  # type: ignore[arg-type]
        is None
    )


def test_assert_tenant_id_missing_reject_at_cell_7() -> None:
    """acc #10 — Err(TenantIdMissingViolation) at cell-7 without tenant.id."""
    span = _FakeSpan({})
    with pytest.raises(TenantIdMissingViolation):
        assert_tenant_id_on_every_span_at_multi_tenant_cells(span, _CELL_7)  # type: ignore[arg-type]


def test_assert_tenant_id_missing_reject_at_cell_8() -> None:
    """acc #10 — Err(TenantIdMissingViolation) at cell-8 without tenant.id."""
    span = _FakeSpan({})
    with pytest.raises(TenantIdMissingViolation):
        assert_tenant_id_on_every_span_at_multi_tenant_cells(span, _CELL_8)  # type: ignore[arg-type]


def test_assert_tenant_id_not_required_at_non_multi_tenant_cell() -> None:
    """acc #10 — the tenant.id invariant applies only at cells 7/8."""
    span = _FakeSpan({})
    assert (
        assert_tenant_id_on_every_span_at_multi_tenant_cells(span, _CELL_1)  # type: ignore[arg-type]
        is None
    )


# --- §21.2 Tier-5 audit-signature requirement ------------------------------


def test_audit_signature_required_at_tier_5_ledger() -> None:
    """§21.2 + C-IS-10 §10.5 — audit-signature attestation required at Tier-5."""
    assert AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER is True


# --- acc #13 — algorithm selection deferred --------------------------------


def test_specific_algorithm_selection_deferred() -> None:
    """acc #13 — operators select within the 3-algorithm admissible set.

    `sign_audit_entry` accepts any of the 3 admissible algorithms — the
    specific selection is a deployment-binding-time operator choice per §21.2.
    """
    for algo in SignatureAlgorithm:
        sig = sign_audit_entry(_payload("h0"), "key-1", algo)
        assert sig.audit_signature_algorithm == algo


def test_per_tenant_separation_is_frozen() -> None:
    """PerTenantSeparation is a frozen, extra-forbidding record."""
    binding = PER_TENANT_SEPARATION_BINDINGS[_CELL_7]
    assert isinstance(binding, PerTenantSeparation)
    with pytest.raises(Exception):
        binding.cross_tenant_aggregation_forbidden = False  # type: ignore[misc]


# --- OD spec v1.31 C-OD-24 §24.7 — rotation-pair dual-signature pattern ----


def _rotation_pair(
    *,
    outgoing_key_id: str = "key-outgoing",
    outgoing_key_period: int = 3,
    incoming_key_id: str = "key-incoming",
    incoming_key_period: int = 4,
) -> tuple[AuditLedgerEntry, AuditLedgerEntry]:
    return sign_rotation_pair(
        outgoing_entry_core=StateLedgerEntryRef("rotation-outgoing"),
        outgoing_prior_entry_hash="genesis",
        incoming_entry_core=StateLedgerEntryRef("rotation-incoming"),
        outgoing_key_id=outgoing_key_id,
        outgoing_key_period=outgoing_key_period,
        incoming_key_id=incoming_key_id,
        incoming_key_period=incoming_key_period,
        algo=SignatureAlgorithm.ED25519,
    )


def test_sign_rotation_pair_shares_correlation_id() -> None:
    """§24.7 — both siblings carry the same `audit.rotation_correlation_id`."""
    outgoing, incoming = _rotation_pair()
    outgoing_id = outgoing.payload.audit_namespace_attrs[ROTATION_CORRELATION_ID_ATTR]
    incoming_id = incoming.payload.audit_namespace_attrs[ROTATION_CORRELATION_ID_ATTR]
    assert outgoing_id == incoming_id
    assert outgoing_id  # non-empty


def test_sign_rotation_pair_chains_onto_outgoing() -> None:
    """§24.7 — incoming.payload.prior_entry_hash == outgoing.entry_hash."""
    outgoing, incoming = _rotation_pair()
    assert incoming.payload.prior_entry_hash == outgoing.entry_hash


def test_sign_rotation_pair_key_periods_consecutive() -> None:
    """§24.7 — sibling-1 (outgoing) at period N, sibling-2 (incoming) at N+1."""
    outgoing, incoming = _rotation_pair(outgoing_key_period=5, incoming_key_period=6)
    assert outgoing.signature_attrs.audit_signature_key_period == "5"
    assert incoming.signature_attrs.audit_signature_key_period == "6"


def test_sign_rotation_pair_rejects_non_consecutive_periods() -> None:
    """§24.7 precondition — incoming_key_period must equal outgoing + 1."""
    with pytest.raises(ValueError, match="incoming_key_period"):
        sign_rotation_pair(
            outgoing_entry_core=StateLedgerEntryRef("a"),
            outgoing_prior_entry_hash="genesis",
            incoming_entry_core=StateLedgerEntryRef("b"),
            outgoing_key_id="k1",
            outgoing_key_period=3,
            incoming_key_id="k2",
            incoming_key_period=5,
            algo=SignatureAlgorithm.ED25519,
        )


def test_sign_rotation_pair_rejects_same_key_id() -> None:
    """§24.7 precondition — outgoing and incoming key_id must differ."""
    with pytest.raises(ValueError, match="key_id"):
        sign_rotation_pair(
            outgoing_entry_core=StateLedgerEntryRef("a"),
            outgoing_prior_entry_hash="genesis",
            incoming_entry_core=StateLedgerEntryRef("b"),
            outgoing_key_id="same-key",
            outgoing_key_period=3,
            incoming_key_id="same-key",
            incoming_key_period=4,
            algo=SignatureAlgorithm.ED25519,
        )


def test_verify_rotation_pairs_round_trip_accept() -> None:
    """§24.7 acceptance — rotate -> verify passes (round-trip witness)."""
    outgoing, incoming = _rotation_pair()
    ledger = AuditLedger(entries=(outgoing, incoming), cell_id=_CELL_7)
    assert verify_rotation_pairs(ledger) is None
    # Composes with the standing hash-chain walk — the pair is also a valid
    # 2-entry chain.
    assert verify_hash_chain_integrity(ledger) is None


def test_verify_rotation_pairs_non_rotation_entries_unaffected() -> None:
    """§24.7 acceptance — a ledger with no rotation-tagged entries is a no-op
    control (untagged entries carry no `audit.rotation_correlation_id`)."""
    entry_1 = _entry("genesis")
    entry_2 = _entry(entry_1.entry_hash)
    ledger = AuditLedger(entries=(entry_1, entry_2), cell_id=_CELL_7)
    assert ROTATION_CORRELATION_ID_ATTR not in ledger.entries[0].payload.audit_namespace_attrs
    assert verify_rotation_pairs(ledger) is None


def test_verify_rotation_pairs_tamper_outgoing_signature_key_id_fails() -> None:
    """§24.7 acceptance — tampering sibling-1 (outgoing key_id) fails verify."""
    outgoing, incoming = _rotation_pair()
    tampered_outgoing = outgoing.model_copy(
        update={
            "signature_attrs": outgoing.signature_attrs.model_copy(
                update={"audit_signature_key_id": incoming.signature_attrs.audit_signature_key_id}
            )
        }
    )
    ledger = AuditLedger(entries=(tampered_outgoing, incoming), cell_id=_CELL_7)
    with pytest.raises(RotationPairIntegrityBreach, match="key_id must differ"):
        verify_rotation_pairs(ledger)


def test_verify_rotation_pairs_tamper_payload_stale_hash_fails() -> None:
    """§24.7 acceptance — mutating a sibling's payload in place while leaving
    `entry_hash` stale is caught by hash recomputation, not just by the
    cross-entry `prior_entry_hash` comparison (a payload-content tamper that
    a naive stored-field-only check would miss)."""
    outgoing, incoming = _rotation_pair()
    tampered_payload = incoming.payload.model_copy(update={"prior_entry_hash": "WRONG"})
    tampered_incoming = incoming.model_copy(update={"payload": tampered_payload})
    ledger = AuditLedger(entries=(outgoing, tampered_incoming), cell_id=_CELL_7)
    with pytest.raises(RotationPairIntegrityBreach, match="does not match recomputed"):
        verify_rotation_pairs(ledger)
    # The standing hash-chain walk independently catches the same tamper.
    with pytest.raises(HashChainBreach):
        verify_hash_chain_integrity(ledger)


def test_verify_rotation_pairs_broken_chain_link_fails() -> None:
    """§24.7 acceptance — a self-consistent sibling-2 (its own `entry_hash`
    matches its own payload) whose `prior_entry_hash` does not extend
    sibling-1's `entry_hash` fails chain-hash continuity specifically —
    isolated from the hash-recomputation check above."""
    outgoing, incoming = _rotation_pair()
    broken_payload = incoming.payload.model_copy(update={"prior_entry_hash": "WRONG"})
    broken_incoming = incoming.model_copy(
        update={"payload": broken_payload, "entry_hash": compute_entry_hash(broken_payload)}
    )
    ledger = AuditLedger(entries=(outgoing, broken_incoming), cell_id=_CELL_7)
    with pytest.raises(RotationPairIntegrityBreach, match="chain-hash"):
        verify_rotation_pairs(ledger)


def test_verify_rotation_pairs_missing_sibling_fails() -> None:
    """§24.7 acceptance — a lone rotation-tagged entry (missing sibling) fails."""
    outgoing, _incoming = _rotation_pair()
    ledger = AuditLedger(entries=(outgoing,), cell_id=_CELL_7)
    with pytest.raises(RotationPairIntegrityBreach, match="requires exactly 2"):
        verify_rotation_pairs(ledger)


def test_verify_rotation_pairs_non_consecutive_periods_fails() -> None:
    """§24.7 acceptance — tampering a key_period to break consecutiveness fails."""
    outgoing, incoming = _rotation_pair()
    tampered_sig = incoming.signature_attrs.model_copy(update={"audit_signature_key_period": "9"})
    tampered_incoming = incoming.model_copy(update={"signature_attrs": tampered_sig})
    ledger = AuditLedger(entries=(outgoing, tampered_incoming), cell_id=_CELL_7)
    with pytest.raises(RotationPairIntegrityBreach, match="not consecutive"):
        verify_rotation_pairs(ledger)


def test_verify_rotation_pairs_solo_tier_no_op() -> None:
    """§24.7 — solo-tier entries never carry the attribute; verify is a no-op
    over an empty ledger (structural no-op, not merely a NULL column)."""
    ledger = AuditLedger(entries=(), cell_id=_CELL_7)
    assert verify_rotation_pairs(ledger) is None


def test_verify_rotation_pairs_rejects_malformed_correlation_id() -> None:
    """§24.7 acceptance — a present-but-non-UUID `audit.rotation_correlation_id`
    is rejected outright, not silently grouped as a valid pairing key (Codex
    out-of-family review finding — a non-empty non-UUID value must not bypass
    the exactly-two sibling discipline by accident of string equality)."""
    outgoing, incoming = _rotation_pair()
    malformed_payload = outgoing.payload.model_copy(
        update={
            "audit_namespace_attrs": {
                **outgoing.payload.audit_namespace_attrs,
                ROTATION_CORRELATION_ID_ATTR: "not-a-uuid",
            }
        }
    )
    malformed_outgoing = outgoing.model_copy(
        update={"payload": malformed_payload, "entry_hash": compute_entry_hash(malformed_payload)}
    )
    ledger = AuditLedger(entries=(malformed_outgoing, incoming), cell_id=_CELL_7)
    with pytest.raises(RotationPairIntegrityBreach, match="not a canonical UUID"):
        verify_rotation_pairs(ledger)


# --- OD spec v1.33 §21.2.1 — SigningBackend composition-root injection seam --


def test_sign_without_backend_placeholder_preserved_byte_identical() -> None:
    """§21.2.1 item 2 — the absent-backend path is PRESERVED VERBATIM: every
    attribute (including the exact placeholder value shape and the
    'DEPLOYMENT_BOUND' token) is byte-identical to the pre-seam behavior, so
    every existing caller sees zero regression."""
    payload = _payload("h0")
    sig = sign_audit_entry(payload, "key-1", SignatureAlgorithm.ED25519)
    assert sig == AuditSignatureAttributes(
        audit_signature_value="unsigned:key-1:h0",
        audit_signature_algorithm=SignatureAlgorithm.ED25519,
        audit_signature_key_id="key-1",
        audit_signature_key_period="DEPLOYMENT_BOUND",
    )


class _InMemoryEd25519Backend:
    """TEST-ONLY C-CP-20 §20.2.1 `SigningBackend` double — one in-memory
    Ed25519 keypair (real cryptography, no claim about production residence).
    Records the `key_period` values it was called with so the seam's
    'DEPLOYMENT_BOUND' → 0 integer projection is directly observable."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        self._private_key = Ed25519PrivateKey.generate()
        self.public_key = self._private_key.public_key()
        self.seen_key_periods: list[int] = []

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id
        self.seen_key_periods.append(key_period)
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        from cryptography.exceptions import InvalidSignature

        del key_id, key_period
        try:
            self.public_key.verify(signature, message)
        except InvalidSignature:
            return False
        return True


def test_sign_with_backend_real_signature_verifies_over_canonical_message() -> None:
    """§21.2.1 item 3/4 — with a real backend the produced value is standard
    base64 of a genuine signature over the canonical message binding
    (entry-content-hash, key_id, algo, key-period token); verified directly
    against the backend's public key, and the 3 metadata attrs are unchanged
    in shape ('DEPLOYMENT_BOUND' token preserved)."""
    import base64

    from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
        canonical_od_signing_message,
    )

    payload = _payload("h0")
    backend = _InMemoryEd25519Backend()
    sig = sign_audit_entry(payload, "key-1", SignatureAlgorithm.ED25519, backend=backend)

    assert not sig.audit_signature_value.startswith("unsigned:")
    raw = base64.b64decode(sig.audit_signature_value, validate=True)
    assert len(raw) == 64
    assert sig.audit_signature_algorithm == SignatureAlgorithm.ED25519
    assert sig.audit_signature_key_id == "key-1"
    assert sig.audit_signature_key_period == "DEPLOYMENT_BOUND"

    expected_message = canonical_od_signing_message(
        compute_entry_hash(payload),
        key_id="key-1",
        algo_value="ed25519",
        key_period_token="DEPLOYMENT_BOUND",
    )
    backend.public_key.verify(raw, expected_message)  # raises on mismatch


def test_sign_with_backend_message_binds_key_id_metadata() -> None:
    """§21.2.1 item 3 — the signature does NOT verify over a message
    reconstructed with a different key_id: metadata is bound into the signed
    bytes (the C-CP-20 §20.3.1 relabeling defense), not merely carried
    alongside them."""
    import base64

    import pytest as _pytest
    from cryptography.exceptions import InvalidSignature
    from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
        canonical_od_signing_message,
    )

    payload = _payload("h0")
    backend = _InMemoryEd25519Backend()
    sig = sign_audit_entry(payload, "key-1", SignatureAlgorithm.ED25519, backend=backend)
    raw = base64.b64decode(sig.audit_signature_value, validate=True)

    relabeled_message = canonical_od_signing_message(
        compute_entry_hash(payload),
        key_id="some-other-key",
        algo_value="ed25519",
        key_period_token="DEPLOYMENT_BOUND",
    )
    with _pytest.raises(InvalidSignature):
        backend.public_key.verify(raw, relabeled_message)


def test_sign_with_backend_passes_deployment_bound_period_zero() -> None:
    """§21.2.1 item 3 — the backend receives key_period=0, the fixed integer
    projection of the 'DEPLOYMENT_BOUND' token (rotation-aware selection is
    B-33's scope, not this seam's)."""
    backend = _InMemoryEd25519Backend()
    sign_audit_entry(_payload("h0"), "key-1", SignatureAlgorithm.ED25519, backend=backend)
    assert backend.seen_key_periods == [0]


def test_sign_with_backend_rejects_algorithm_disagreement() -> None:
    """§21.2.1 item 4 — a backend whose declared algorithm disagrees with the
    caller-selected algo must not attest: a mislabeled algorithm never lands
    on the attribute set. §21.2.3 row 5 — routes through the typed
    `AuditSigningFailedError` boundary, not a bare `ValueError`."""
    backend = _InMemoryEd25519Backend()
    with pytest.raises(AuditSigningFailedError, match="disagrees"):
        sign_audit_entry(_payload("h0"), "key-1", SignatureAlgorithm.ECDSA_P256, backend=backend)


def test_sign_with_backend_rejects_wrong_length_signature() -> None:
    """§21.2.1 item 4 — a backend returning a signature whose byte-length
    contradicts the declared algorithm's fixed width (C-CP-20 §20.4: ed25519
    is exactly 64 bytes) fails loud rather than landing a malformed
    attribute set. §21.2.3 row 5 — typed `AuditSigningFailedError`."""

    class _PaddingBackend(_InMemoryEd25519Backend):
        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            return super().sign(message=message, key_id=key_id, key_period=key_period) + b"\x00"

    with pytest.raises(AuditSigningFailedError, match="len=65"):
        sign_audit_entry(
            _payload("h0"), "key-1", SignatureAlgorithm.ED25519, backend=_PaddingBackend()
        )


def test_sign_with_backend_still_requires_key_id() -> None:
    """The §21.2 key_id precondition fires before any backend interaction —
    identical behavior on both seam paths; the recording backend proves it
    was never consulted (merge-gate test-witness lens note)."""
    backend = _InMemoryEd25519Backend()
    with pytest.raises(ValueError, match="key_id is required"):
        sign_audit_entry(_payload("h0"), "", SignatureAlgorithm.ED25519, backend=backend)
    assert backend.seen_key_periods == []


def test_canonical_message_exact_bytes_pin_all_four_bindings_and_injectivity() -> None:
    """§21.2.1 item 3 — merge-gate test-witness lens BLOCK fix: the earlier
    round-trip witness reconstructed the expected message with the SAME
    `canonical_od_signing_message` helper the implementation calls, so it
    could not catch a mutated helper (dropped entry-hash/algo/period binding,
    or a de-injectivized join). This witness constructs the committed message
    LITERALLY — `{len}:{part}` segments joined by `|` over the exact
    four-tuple — and verifies the real signature against those bytes, then
    proves each remaining binding by literal relabeled-message probes."""
    import base64

    import pytest as _pytest
    from cryptography.exceptions import InvalidSignature

    payload = _payload("h0")
    backend = _InMemoryEd25519Backend()
    sig = sign_audit_entry(payload, "key-1", SignatureAlgorithm.ED25519, backend=backend)
    raw = base64.b64decode(sig.audit_signature_value, validate=True)

    entry_hash = compute_entry_hash(payload)
    assert len(entry_hash) == 64  # sha256 hex

    def literal_message(h: str, key_id: str, algo: str, period: str) -> bytes:
        return "|".join(f"{len(part)}:{part}" for part in (h, key_id, algo, period)).encode()

    expected = literal_message(entry_hash, "key-1", "ed25519", "DEPLOYMENT_BOUND")
    assert expected == (f"64:{entry_hash}|5:key-1|7:ed25519|16:DEPLOYMENT_BOUND".encode())
    backend.public_key.verify(raw, expected)  # raises on mismatch

    # Payload/content binding — a different entry hash must not verify.
    with _pytest.raises(InvalidSignature):
        backend.public_key.verify(
            raw, literal_message("f" * 64, "key-1", "ed25519", "DEPLOYMENT_BOUND")
        )
    # Algorithm binding.
    with _pytest.raises(InvalidSignature):
        backend.public_key.verify(
            raw, literal_message(entry_hash, "key-1", "ecdsa-p256", "DEPLOYMENT_BOUND")
        )
    # Key-period binding.
    with _pytest.raises(InvalidSignature):
        backend.public_key.verify(raw, literal_message(entry_hash, "key-1", "ed25519", "0"))
    # Injectivity — the same fields under a plain (non-length-prefixed) join
    # must not verify: the length prefixes are part of the signed encoding.
    plain_join = "|".join((entry_hash, "key-1", "ed25519", "DEPLOYMENT_BOUND")).encode()
    with _pytest.raises(InvalidSignature):
        backend.public_key.verify(raw, plain_join)


# --- U-OD-30 amendment (OD spec v1.34 §21.2.1/§21.2.3) — tenant-bearing
# signing, the tenant-tag normalizer, and the typed AuditSigningFailedError
# boundary ----------------------------------------------------------------


def test_tenant_tag_normalizer_none_passthrough() -> None:
    """§21.2.1 row 2 — `signing_token(None)` drops the segment (`None`);
    `sidecar_tag(None)` preserves the writer's pre-amendment `"_single"`
    byte-shape."""
    assert signing_token(None) is None
    assert sidecar_tag(None) == "_single"


def test_tenant_tag_normalizer_same_token_for_real_tenant() -> None:
    """§21.2.1 row 2 — for a real (non-`None`) tenant, `signing_token` and
    `sidecar_tag` return the IDENTICAL token: the signed segment and the
    sidecar join key are the SAME token by construction."""
    assert signing_token("acme-corp") == sidecar_tag("acme-corp") == "acme-corp"


def test_tenant_tag_normalization_refuses_empty_and_single_literal() -> None:
    """§21.2.1 row 2 — the shared rule-set REFUSES the empty string (use
    `None` for untenanted) and the reserved `"_single"` sidecar literal, at
    BOTH projections (one authority, not two independently-drifting checks).
    Mutation probe: removing either refusal branch lets that value through
    both `signing_token` and `sidecar_tag` unrejected."""
    for bad in ("", "_single"):
        with pytest.raises(ValueError, match="tenant_id"):
            signing_token(bad)
        with pytest.raises(ValueError, match="tenant_id"):
            sidecar_tag(bad)


def test_tenant_absent_message_and_attrs_byte_identical_to_v1_33_path() -> None:
    """Witness (b) — with `tenant_id` absent, the canonical message and the
    resulting `AuditSignatureAttributes` are byte-identical to the
    pre-amendment (v1.33) path for every existing caller: calling with an
    explicit `tenant_id=None` produces the EXACT same signature bytes as
    calling without the keyword at all."""
    import base64

    payload = _payload("h0")
    backend = _InMemoryEd25519Backend()
    sig_no_kwarg = sign_audit_entry(payload, "key-1", SignatureAlgorithm.ED25519, backend=backend)

    entry_hash = compute_entry_hash(payload)

    def literal_message(*parts: str) -> bytes:
        return "|".join(f"{len(part)}:{part}" for part in parts).encode()

    expected_four_tuple = literal_message(entry_hash, "key-1", "ed25519", "DEPLOYMENT_BOUND")
    backend.public_key.verify(
        base64.b64decode(sig_no_kwarg.audit_signature_value, validate=True), expected_four_tuple
    )

    sig_explicit_none = sign_audit_entry(
        _payload("h0"), "key-1", SignatureAlgorithm.ED25519, backend=backend, tenant_id=None
    )
    # Ed25519 (RFC 8032) is DETERMINISTIC for a fixed key + message — the
    # same backend signing the byte-identical four-tuple message must
    # produce the byte-identical signature, which is the load-bearing proof
    # that tenant_id=None composes the EXACT same message as omitting the
    # keyword entirely (a de-normalization bug that dropped a stray byte
    # would flip this to a different, still-valid signature).
    assert sig_explicit_none.audit_signature_value == sig_no_kwarg.audit_signature_value
    assert sig_explicit_none == sig_no_kwarg


def test_five_segment_message_tenant_tag_swap_breaks_verification() -> None:
    """Witness (a) — a tenant-tag swap on a signed entry breaks verification:
    the message is injective across all five segments, so a five-tuple
    signed under `tenant_id="tenant-a"` does not verify against the literal
    five-tuple message for `"tenant-b"`. Mutation probe: dropping the tenant
    segment from the canonical message would make this pass wrongly (the
    swapped message would collapse to the same four-tuple prefix either way)
    — this witness pins the FULL five-part literal bytes, not a helper
    round-trip."""
    import base64

    from cryptography.exceptions import InvalidSignature

    payload = _payload("h0")
    backend = _InMemoryEd25519Backend()
    sig = sign_audit_entry(
        payload, "key-1", SignatureAlgorithm.ED25519, backend=backend, tenant_id="tenant-a"
    )
    raw = base64.b64decode(sig.audit_signature_value, validate=True)
    entry_hash = compute_entry_hash(payload)

    def literal_message(*parts: str) -> bytes:
        return "|".join(f"{len(part)}:{part}" for part in parts).encode()

    correct = literal_message(entry_hash, "key-1", "ed25519", "DEPLOYMENT_BOUND", "tenant-a")
    backend.public_key.verify(raw, correct)  # raises on mismatch — sanity pin

    swapped = literal_message(entry_hash, "key-1", "ed25519", "DEPLOYMENT_BOUND", "tenant-b")
    with pytest.raises(InvalidSignature):
        backend.public_key.verify(raw, swapped)


def test_five_tuple_message_distinct_from_four_tuple_injective() -> None:
    """§21.2.1 row 1 — a tenant-bearing (five-segment) signature does NOT
    verify against the tenant-absent (four-tuple) message: the length-prefix
    encoding keeps the four-tuple/five-tuple pair injective, so a verifier
    that forgets to include the tenant segment cannot be fooled into
    accepting a tenant-bound signature as tenant-absent (or vice versa)."""
    import base64

    from cryptography.exceptions import InvalidSignature

    payload = _payload("h0")
    backend = _InMemoryEd25519Backend()
    sig = sign_audit_entry(
        payload, "key-1", SignatureAlgorithm.ED25519, backend=backend, tenant_id="tenant-a"
    )
    raw = base64.b64decode(sig.audit_signature_value, validate=True)
    entry_hash = compute_entry_hash(payload)

    def literal_message(*parts: str) -> bytes:
        return "|".join(f"{len(part)}:{part}" for part in parts).encode()

    four_tuple = literal_message(entry_hash, "key-1", "ed25519", "DEPLOYMENT_BOUND")
    with pytest.raises(InvalidSignature):
        backend.public_key.verify(raw, four_tuple)


def test_sign_audit_entry_rejects_empty_tenant_and_reserved_literal() -> None:
    """§21.2.1 row 2 — `sign_audit_entry` applies the shared normalizer to
    its `tenant_id` BEFORE composing the message; the empty string and the
    reserved `"_single"` literal are refused at the signing entry point
    too, not only at the bare normalizer functions."""
    for bad in ("", "_single"):
        with pytest.raises(ValueError, match="tenant_id"):
            sign_audit_entry(_payload("h0"), "key-1", SignatureAlgorithm.ED25519, tenant_id=bad)


def test_sign_audit_entry_preserves_typed_breaker_open_error_unwrapped() -> None:
    """Out-of-family Codex P2 (PR #1061 round 2) — a production
    `BreakerGuardedSigningBackend` raises the ALREADY-typed
    `AuditSigningBreakerOpenError` when the breaker is open; that must
    propagate UNCHANGED (not double-wrapped into `AuditSigningFailedError`)
    — it is a distinct, caller-retryable AVAILABILITY signal, not a signing
    failure, and callers key on the exact type to distinguish them.
    Mutation probe: removing the `except AUDIT_SIGNING_HARD_FAILURES: raise`
    re-raise arm lets the generic `except Exception` wrap it instead."""

    class _BreakerOpenBackend(_InMemoryEd25519Backend):
        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            raise AuditSigningBreakerOpenError("breaker is open")

    with pytest.raises(AuditSigningBreakerOpenError, match="breaker is open"):
        sign_audit_entry(
            _payload("h0"), "key-1", SignatureAlgorithm.ED25519, backend=_BreakerOpenBackend()
        )


def test_sign_audit_entry_rejects_untyped_backend_error_wraps_typed() -> None:
    """§21.2.3 row 5 — `backend.sign` raising an UNTYPED exception (a bug in
    a third-party backend, not one of this module's own validations) is
    wrapped into the typed `AuditSigningFailedError`, never left to escape
    raw. Mutation probe: removing the wrapping try/except would let the
    injected `RuntimeError("boom")` propagate unwrapped and this assertion
    would see the wrong exception TYPE."""

    class _ExplodingBackend(_InMemoryEd25519Backend):
        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            del message, key_id, key_period
            raise RuntimeError("boom")

    with pytest.raises(AuditSigningFailedError, match="boom"):
        sign_audit_entry(
            _payload("h0"), "key-1", SignatureAlgorithm.ED25519, backend=_ExplodingBackend()
        )


def test_sign_audit_entry_rejects_non_bytes_signature() -> None:
    """§21.2.1 row 4 / §21.2.3 row 5 — a backend returning a non-`bytes`
    value (e.g. accidentally returning `str`) is rejected as malformed
    through the typed boundary, not left to raise an untyped `TypeError`
    out of `base64.b64encode` for a blind upstream catch to swallow."""

    class _StringBackend(_InMemoryEd25519Backend):
        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            del message, key_id, key_period
            return "not-bytes"  # type: ignore[return-value]

    with pytest.raises(AuditSigningFailedError, match="type=str"):
        sign_audit_entry(
            _payload("h0"), "key-1", SignatureAlgorithm.ED25519, backend=_StringBackend()
        )


def test_sign_rotation_pair_has_no_production_caller() -> None:
    """§21.2.1 row 7 (acc #21) — `sign_rotation_pair` is PROHIBITED at
    MULTI_TENANT_COMPLIANCE until `B-33`; the function takes no tier input
    and has ZERO production callers on `main`, so the enforceable slice at
    THIS arc is a static caller-regression guard: no production source file
    under harness-runtime/harness-cp/harness-cxa/harness-od calls
    `sign_rotation_pair(` anywhere — including an intra-module call inside
    the defining module itself. Only the `def sign_rotation_pair(` site and
    test files are excluded. Mutation probe: adding ANY production caller
    (including one inside this very module) fails this test."""
    import re
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    packages = ["harness-runtime", "harness-cp", "harness-cxa", "harness-od"]
    call_pattern = re.compile(r"\bsign_rotation_pair\s*\(")
    def_pattern = re.compile(r"^def sign_rotation_pair\(", re.MULTILINE)
    offenders: list[str] = []
    for package in packages:
        src_root = repo_root / package / "src"
        if not src_root.is_dir():
            continue
        for path in src_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for match in call_pattern.finditer(text):
                line_start = text.rfind("\n", 0, match.start()) + 1
                line = text[line_start : text.find("\n", match.start())]
                if def_pattern.match(line):
                    continue  # the def site itself
                offenders.append(f"{path.relative_to(repo_root)}:{line.strip()}")
    assert offenders == [], f"sign_rotation_pair has production callers: {offenders}"

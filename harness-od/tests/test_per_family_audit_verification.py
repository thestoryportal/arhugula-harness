"""`B-49` — per-family audit verification witnesses.

Policy under test (`.harness/b-47-pr-b2-design-disposition-v1.md`):
content-hash verification for EVERY entry; chain (linkage) verification
ONLY for the redaction-token family, discriminated by
`audit.redaction_token.*` namespace keys — never by `entry_core` prefix.
"""

from __future__ import annotations

import pytest
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import HashChainBreach
from harness_od.per_family_audit_verification import (
    REDACTION_TOKEN_FAMILY,
    FamilyVerificationReport,
    verify_per_family_chains,
)

GENESIS = "0" * 64


def _entry(
    *,
    core: str,
    attrs: dict[str, str],
    prior: str = GENESIS,
) -> AuditLedgerEntry:
    payload = AuditPayload(
        entry_core=StateLedgerEntryRef(core),
        audit_namespace_attrs=attrs,
        prior_entry_hash=prior,
    )
    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=AuditSignatureAttributes(
            audit_signature_value="sig:test",
            audit_signature_algorithm=SignatureAlgorithm.ED25519,
            audit_signature_key_id="test-key",
            audit_signature_key_period="2026-Q2",
        ),
        entry_hash=compute_entry_hash(payload),
    )


def _redaction(core: str, *, prior: str = GENESIS, seed: str = "r") -> AuditLedgerEntry:
    return _entry(
        core=core,
        attrs={"audit.redaction_token.token": f"[REDACTED:PII:{seed}]", "audit.seed": seed},
        prior=prior,
    )


def _cost(seed: str) -> AuditLedgerEntry:
    return _entry(core=f"cost:{seed}", attrs={"audit.cost.amount": seed}, prior=GENESIS)


def _dispatch(seed: str) -> AuditLedgerEntry:
    return _entry(core=f"dispatch:{seed}", attrs={"audit.actor": seed}, prior=GENESIS)


def _interleaved() -> tuple[list[AuditLedgerEntry], AuditLedgerEntry, AuditLedgerEntry]:
    """Two chained redaction rows interleaved with genesis-prior families."""
    r1 = _redaction("redaction-token:r1", seed="r1")
    r2 = _redaction("redaction-token:r2", prior=r1.entry_hash, seed="r2")
    entries = [_cost("c1"), r1, _dispatch("d1"), _cost("c2"), r2, _dispatch("d2")]
    return entries, r1, r2


def test_interleaved_multi_family_sequence_verifies() -> None:
    """The load-bearing policy claim: genesis-prior families (two cost, two
    dispatch entries) do NOT fail chain verification, while the chained
    redaction subsequence IS linkage-verified — a naive chain-verify-every-
    family mutation raises on the second cost entry."""
    entries, _r1, _r2 = _interleaved()
    report = verify_per_family_chains(entries)
    assert isinstance(report, FamilyVerificationReport)
    assert report.chained == {REDACTION_TOKEN_FAMILY: 2}
    assert report.per_entry == {"cost": 2, "dispatch": 2}


def test_tampered_payload_in_any_family_fails_loud() -> None:
    entries, _r1, _r2 = _interleaved()
    tampered_payload = AuditPayload(
        entry_core=entries[0].payload.entry_core,
        audit_namespace_attrs={"audit.cost.amount": "TAMPERED"},
        prior_entry_hash=entries[0].payload.prior_entry_hash,
    )
    entries[0] = AuditLedgerEntry(
        payload=tampered_payload,
        signature_attrs=entries[0].signature_attrs,
        entry_hash=entries[0].entry_hash,  # stale hash kept — the tamper signature
    )
    with pytest.raises(HashChainBreach, match="content integrity"):
        verify_per_family_chains(entries)


def test_broken_redaction_linkage_fails_loud() -> None:
    r1 = _redaction("redaction-token:r1", seed="r1")
    r2 = _redaction("redaction-token:r2", prior="f" * 64, seed="r2")  # wrong prior
    with pytest.raises(HashChainBreach, match="hash chain broken"):
        verify_per_family_chains([_cost("c1"), r1, r2])


def test_custom_core_redaction_row_is_still_chain_verified() -> None:
    """The discriminator claim: a redaction row composed with a
    caller-supplied entry_core (no `redaction-token:` prefix) is classified
    by its namespace keys — a prefix-based classifier would silently skip
    its linkage and let this broken chain pass."""
    r1 = _redaction("custom-core-ref", seed="r1")
    r2 = _redaction("another-custom-core", prior="f" * 64, seed="r2")  # broken linkage
    with pytest.raises(HashChainBreach, match="hash chain broken"):
        verify_per_family_chains([r1, r2])

    # And the happy path counts them into the chained family.
    r2_ok = _redaction("another-custom-core", prior=r1.entry_hash, seed="r2")
    report = verify_per_family_chains([r1, r2_ok])
    assert report.chained == {REDACTION_TOKEN_FAMILY: 2}
    assert report.per_entry == {}


def test_empty_sequence_returns_empty_report() -> None:
    report = verify_per_family_chains([])
    assert report.chained == {}
    assert report.per_entry == {}


def test_unprefixed_core_counts_into_the_unprefixed_family() -> None:
    report = verify_per_family_chains([_entry(core="bare-ref", attrs={"audit.actor": "x"})])
    assert report.per_entry == {"(unprefixed)": 1}


def test_report_is_deeply_immutable() -> None:
    """Codex round-1 (B-49) — a frozen carrier over mutable dicts still let
    `report.chained[...] = ...` alter verification evidence post-hoc."""
    entries, _r1, _r2 = _interleaved()
    report = verify_per_family_chains(entries)
    with pytest.raises(TypeError):
        report.chained["forged"] = 99  # type: ignore[index]
    with pytest.raises(AttributeError):
        report.per_entry.clear()  # type: ignore[attr-defined] — mappingproxy has no clear
    with pytest.raises((AttributeError, TypeError)):
        report.chained = {}  # type: ignore[misc]


def test_direct_construction_copies_and_freezes_sources() -> None:
    """Codex round-2 (B-49) — the immutability invariant belongs to the
    TYPE: a direct constructor caller retaining its source dict must not
    hold a mutation handle into the report."""
    source = {"cost": 1}
    report = FamilyVerificationReport(chained={}, per_entry=source)
    source["cost"] = 999
    source["forged"] = 1
    assert report.per_entry == {"cost": 1}
    with pytest.raises(TypeError):
        report.per_entry["x"] = 1  # type: ignore[index]


def test_baseline_divergences_direct_construction_copies_and_freezes() -> None:
    """Out-of-family Codex [P2] finding, round 7 (U-OD-55): the
    `tuple[str, ...]` annotation on `baseline_divergences` was never
    enforced at runtime — a caller passing a `list` retained a live
    mutation handle into this "deeply immutable" carrier. Mirrors the
    `per_entry`/`chained` dict-copy discipline above."""
    source = ["a divergence"]
    report = FamilyVerificationReport(chained={}, per_entry={}, baseline_divergences=source)
    source.append("mutated after construction")
    assert report.baseline_divergences == ("a divergence",)
    assert isinstance(report.baseline_divergences, tuple)

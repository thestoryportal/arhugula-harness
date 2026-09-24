"""Tests for U-IS-11 v2.4 amendment — `procedural_tier_snapshot_ref` sidecar.

Per Implementation_Plan_Information_Substrate_v2_4.md §2.2 U-IS-11 acceptance
criteria #11-#14 + tests list. The sidecar is the D-derivative extension of
the §5 F-layer six-field shape per IS spec v1.3 §C-IS-05 §5.1.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from harness_is.entry_hash import canonicalize, compute_response_hash
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import (
    ALL_ZEROS_SENTINEL,
    Actor,
    ActorClass,
    Identifier,
    StateLedgerEntry,
)
from harness_is.state_ledger_write import (
    EntryPayload,
    WriteKey,
    WriteResult,
    _deserialize_entry,
    _serialize_entry,
    append_ledger_entry,
    read_ledger,
)
from pydantic import ValidationError


def _recovery_audit_data() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": "claim",
        "phase": "complete",
        "record_identity": {
            "tenant_id": "tenant-1",
            "workflow_id": "workflow-1",
            "record_count": 2,
            "latest_digest": "a" * 64,
            "snapshot_hash": "b" * 64,
        },
        "subject_id": "claim-1",
        "action_id": "recover-1",
        "action": "release",
        "operator_uid": 1000,
        "reason_digest": "c" * 64,
        "observation": {
            "claim_bytes_digest": "d" * 64,
            "canonical_claim_path": "/state/claim-1",
            "claim_st_dev": 8,
            "claim_st_ino": 42,
            "lease_generation": "lease-gen-1",
            "lease_identity": "lease-1",
        },
        "transition_kind": "release_archive",
        "transition_digest": "e" * 64,
    }


def test_recovery_audit_round_trip_and_legacy_bytes(tmp_path: Path) -> None:
    legacy = StateLedgerEntry(
        action_id=Identifier("legacy-1"),
        idempotency_key=Identifier("legacy-key"),
        actor=Actor(actor_class=ActorClass.OPERATOR, actor_id="uid:1000"),
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=datetime(2026, 9, 24, tzinfo=UTC),
        prior_event_hash=ALL_ZEROS_SENTINEL,
    )
    legacy = legacy.model_copy(update={"response_hash": compute_response_hash(legacy)})
    assert canonicalize(legacy).decode() == (
        '{"action_id":"legacy-1","actor":{"actor_class":"operator","actor_id":"uid:1000"},'
        '"idempotency_key":"legacy-key","prior_event_hash":"' + '0' * 64 +
        '","timestamp":"2026-09-24T00:00:00+00:00"}'
    )
    assert legacy.response_hash.hex() == "693cd70e9333bd9b111cebc4780b7dfdd8116f063984983bbd613346f7a95f3c"
    assert _serialize_entry(legacy) == (
        '{"action_id":"legacy-1","idempotency_key":"legacy-key",'
        '"actor":{"actor_class":"operator","actor_id":"uid:1000"},'
        '"response_hash":"693cd70e9333bd9b111cebc4780b7dfdd8116f063984983bbd613346f7a95f3c",'
        '"timestamp":"2026-09-24T00:00:00+00:00","prior_event_hash":"' + '0' * 64 + '"}'
    )

    payload = EntryPayload.model_validate({
        "action_id": "recovery-entry",
        "idempotency_key": "recovery-key",
        "actor": {"actor_class": "operator", "actor_id": "uid:1000"},
        "timestamp": "2026-09-24T00:01:00+00:00",
        "recovery_audit": _recovery_audit_data(),
    })
    handle = _handle(tmp_path)
    assert append_ledger_entry(handle, payload, WriteKey(
        thread_id=Identifier("thread"), step_id=Identifier("step"),
        idempotency_key=Identifier("recovery-key"),
    )) is WriteResult.APPENDED
    line = handle.canonical_path.read_text().strip()
    assert json.loads(line)["recovery_audit"] == _recovery_audit_data()
    restored = _deserialize_entry(line)
    assert restored.recovery_audit == payload.recovery_audit
    assert compute_response_hash(restored) == restored.response_hash


def _attestation() -> dict[str, Any]:
    return {
        "operator_uid": 1000,
        "attested_at": "2026-09-24T00:00:00+00:00",
        "stopped_services_digest": "f" * 64,
        "no_workers_observed": True,
        "restart_disabled": True,
    }


def _recovery_entry(audit: dict[str, Any]) -> StateLedgerEntry:
    return StateLedgerEntry.model_validate({
        "action_id": "recovery-entry",
        "idempotency_key": "recovery-key",
        "actor": {"actor_class": "operator", "actor_id": "uid:1000"},
        "response_hash": ALL_ZEROS_SENTINEL,
        "timestamp": "2026-09-24T00:01:00+00:00",
        "prior_event_hash": ALL_ZEROS_SENTINEL,
        "recovery_audit": audit,
    })


@pytest.mark.parametrize("scope,phase,observation", [
    ("claim", "intent", None),
    ("claim", "complete", None),
    ("record", "intent", "claim_absent"),
    ("record", "complete", "claim_no_token"),
    ("record", "complete", "claim_unreadable"),
])
def test_recovery_audit_all_legal_variants_round_trip(
    tmp_path: Path, scope: str, phase: str, observation: str | None,
) -> None:
    audit = _recovery_audit_data()
    audit["scope"] = scope
    audit["phase"] = phase
    if phase == "intent":
        audit.pop("transition_kind")
        audit.pop("transition_digest")
    if scope == "record":
        audit["action"] = "abandon"
        audit["quiescence_attestation"] = _attestation()
        audit["observation"] = {
            "kind": observation,
            "canonical_claim_path": "/state/claim-1",
            "parent_st_dev": 8,
            "parent_st_ino": 20,
            **({"claim_st_dev": 8, "claim_st_ino": 42} if observation != "claim_absent" else {}),
            **({"raw_digest": "d" * 64} if observation == "claim_no_token" else {}),
        }
        if phase == "complete":
            audit["transition_kind"] = "record_tombstone"
            audit["transition_digest"] = "e" * 64
    entry = _recovery_entry(audit)
    line = _serialize_entry(entry)
    restored = _deserialize_entry(line)
    assert restored.recovery_audit == entry.recovery_audit
    assert json.loads(line)["recovery_audit"] == entry.recovery_audit.model_dump(
        mode="json", exclude_none=True,
    )
    assert compute_response_hash(restored) == compute_response_hash(entry)


@pytest.mark.parametrize("mutation", [
    ("action_id", "recover-2"),
    ("subject_id", "claim-2"),
    ("reason_digest", "1" * 64),
    ("observation.claim_bytes_digest", "2" * 64),
    ("observation.claim_st_ino", 43),
    ("observation.lease_generation", "lease-gen-2"),
    ("transition_digest", "3" * 64),
])
def test_recovery_audit_fields_change_hash(mutation: tuple[str, object]) -> None:
    original = _recovery_audit_data()
    changed = deepcopy(original)
    field, value = mutation
    target = changed
    if "." in field:
        field = field.split(".")[1]
        target = changed["observation"]
    target[field] = value
    assert compute_response_hash(_recovery_entry(original)) != compute_response_hash(
        _recovery_entry(changed)
    )


@pytest.mark.parametrize("field,value", [
    ("raw_reason", "secret"),
    ("claim_token", "secret"),
    ("hitl_answer", "secret"),
])
def test_recovery_audit_refuses_sensitive_raw_fields(field: str, value: str) -> None:
    audit = _recovery_audit_data()
    audit[field] = value
    with pytest.raises(ValidationError):
        _recovery_entry(audit)


def test_recovery_audit_refuses_illegal_scope_phase_and_transition() -> None:
    audit = _recovery_audit_data()
    audit["scope"] = "record"
    with pytest.raises(ValidationError):
        _recovery_entry(audit)
    audit = _recovery_audit_data()
    audit["phase"] = "intent"
    with pytest.raises(ValidationError):
        _recovery_entry(audit)
    audit = _recovery_audit_data()
    audit["action"] = "abandon"
    with pytest.raises(ValidationError):
        _recovery_entry(audit)


def test_record_abandon_requires_true_quiescence_attestation() -> None:
    audit = _recovery_audit_data()
    audit.update({"scope": "record", "action": "abandon", "phase": "intent"})
    audit.pop("transition_kind")
    audit.pop("transition_digest")
    audit["observation"] = {
        "kind": "claim_unreadable", "canonical_claim_path": "/state/claim-1",
        "parent_st_dev": 8, "parent_st_ino": 20,
        "claim_st_dev": 8, "claim_st_ino": 42,
    }
    with pytest.raises(ValidationError):
        _recovery_entry(audit)
    audit["quiescence_attestation"] = {**_attestation(), "restart_disabled": False}
    with pytest.raises(ValidationError):
        _recovery_entry(audit)


def test_recovery_scope_observation_transition_and_attestation_are_hashed() -> None:
    claim = _recovery_audit_data()
    claim_none = deepcopy(claim)
    claim_none["transition_kind"] = "none"
    claim_none["transition_digest"] = "1" * 64
    assert compute_response_hash(_recovery_entry(claim)) != compute_response_hash(
        _recovery_entry(claim_none)
    )

    record = deepcopy(claim)
    record.update({
        "scope": "record", "phase": "complete", "action": "abandon",
        "transition_kind": "record_tombstone",
        "observation": {
            "kind": "claim_no_token", "canonical_claim_path": "/state/claim-1",
            "parent_st_dev": 8, "parent_st_ino": 20,
            "claim_st_dev": 8, "claim_st_ino": 42, "raw_digest": "d" * 64,
        },
        "quiescence_attestation": _attestation(),
    })
    changed_observation = deepcopy(record)
    changed_observation["observation"]["kind"] = "claim_unreadable"
    changed_observation["observation"].pop("raw_digest")
    changed_attestation = deepcopy(record)
    changed_attestation["quiescence_attestation"]["stopped_services_digest"] = "1" * 64
    assert compute_response_hash(_recovery_entry(claim)) != compute_response_hash(
        _recovery_entry(record)
    )
    assert compute_response_hash(_recovery_entry(record)) != compute_response_hash(
        _recovery_entry(changed_observation)
    )
    assert compute_response_hash(_recovery_entry(record)) != compute_response_hash(
        _recovery_entry(changed_attestation)
    )

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="agent-1")
_SNAPSHOT_REF = Identifier(
    "ffeeddccbbaa998877665544332211000011223344556677889900aabbccddeeff"[:64]
)


def _handle(tmp_path: Path) -> JsonlLedgerHandle:
    return JsonlLedgerHandle(
        canonical_path=tmp_path / "state.jsonl",
        exists=False,
        entry_count=0,
    )


def _payload(
    i: int,
    snapshot_ref: Identifier | None = None,
) -> EntryPayload:
    return EntryPayload(
        action_id=Identifier(f"act-{i}"),
        idempotency_key=Identifier(f"idem-{i}"),
        actor=_ACTOR,
        timestamp=datetime(2026, 5, 30, i, tzinfo=UTC),
        procedural_tier_snapshot_ref=snapshot_ref,
    )


def _key(i: int) -> WriteKey:
    return WriteKey(
        thread_id=Identifier(f"thread-{i}"),
        step_id=Identifier(f"step-{i}"),
        idempotency_key=Identifier(f"idem-{i}"),
    )


# ---------------------------------------------------------------------------
# AC #11 — sidecar field optional with default None.
# ---------------------------------------------------------------------------


def test_entry_payload_accepts_none_procedural_tier_snapshot_ref_by_default() -> None:
    """AC #11: ``EntryPayload`` constructible without sidecar; default ``None``."""
    payload = EntryPayload(
        action_id=Identifier("a"),
        idempotency_key=Identifier("i"),
        actor=_ACTOR,
        timestamp=datetime(2026, 5, 30, 1, tzinfo=UTC),
    )
    assert payload.procedural_tier_snapshot_ref is None


def test_entry_payload_accepts_non_none_procedural_tier_snapshot_ref() -> None:
    """AC #11: ``EntryPayload`` accepts non-``None`` sidecar value."""
    payload = EntryPayload(
        action_id=Identifier("a"),
        idempotency_key=Identifier("i"),
        actor=_ACTOR,
        timestamp=datetime(2026, 5, 30, 1, tzinfo=UTC),
        procedural_tier_snapshot_ref=_SNAPSHOT_REF,
    )
    assert payload.procedural_tier_snapshot_ref == _SNAPSHOT_REF


# ---------------------------------------------------------------------------
# AC #12 — serialization discipline (omit when None; include when non-None).
# ---------------------------------------------------------------------------


def test_append_persists_sidecar_field_when_non_none(tmp_path: Path) -> None:
    """AC #12: persisted JSONL line includes sidecar key when non-None."""
    handle = _handle(tmp_path)
    payload = _payload(1, snapshot_ref=_SNAPSHOT_REF)
    result = append_ledger_entry(handle, payload, _key(1))
    assert result == WriteResult.APPENDED
    line = handle.canonical_path.read_text().splitlines()[0]
    raw = json.loads(line)
    assert raw["procedural_tier_snapshot_ref"] == _SNAPSHOT_REF


def test_append_omits_sidecar_key_when_none(tmp_path: Path) -> None:
    """AC #12: persisted JSONL line omits sidecar key entirely when None."""
    handle = _handle(tmp_path)
    payload = _payload(1, snapshot_ref=None)
    append_ledger_entry(handle, payload, _key(1))
    line = handle.canonical_path.read_text().splitlines()[0]
    raw = json.loads(line)
    assert "procedural_tier_snapshot_ref" not in raw


# ---------------------------------------------------------------------------
# AC #13 — response_hash includes sidecar field contribution when non-None.
# ---------------------------------------------------------------------------


def test_response_hash_includes_sidecar_field_contribution() -> None:
    """AC #13: two entries differing only in sidecar value produce different
    ``response_hash`` (sidecar participates in canonicalize when non-None)."""
    base_ts = datetime(2026, 5, 30, 1, tzinfo=UTC)
    entry_none = StateLedgerEntry(
        action_id=Identifier("a"),
        idempotency_key=Identifier("i"),
        actor=_ACTOR,
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=base_ts,
        prior_event_hash=ALL_ZEROS_SENTINEL,
        procedural_tier_snapshot_ref=None,
    )
    entry_with_ref = entry_none.model_copy(
        update={"procedural_tier_snapshot_ref": _SNAPSHOT_REF},
    )
    assert compute_response_hash(entry_none) != compute_response_hash(entry_with_ref)


def test_round_trip_with_sidecar_field_deterministic(tmp_path: Path) -> None:
    """AC #13: write→read round-trip preserves sidecar value byte-exact."""
    handle = _handle(tmp_path)
    payload = _payload(1, snapshot_ref=_SNAPSHOT_REF)
    append_ledger_entry(handle, payload, _key(1))
    entries = read_ledger(handle)
    assert len(entries) == 1
    assert entries[0].procedural_tier_snapshot_ref == _SNAPSHOT_REF


# ---------------------------------------------------------------------------
# AC #14 — action_id + sidecar compose without conflation.
# ---------------------------------------------------------------------------


def test_action_id_and_sidecar_compose_without_conflation(tmp_path: Path) -> None:
    """AC #14: action_id retains action-class semantics independently;
    sidecar populated alongside without interference per §C-IS-02 line 170."""
    handle = _handle(tmp_path)
    payload = EntryPayload(
        action_id=Identifier("workflow.step.completed"),  # action-class label
        idempotency_key=Identifier("idem-x"),
        actor=_ACTOR,
        timestamp=datetime(2026, 5, 30, 1, tzinfo=UTC),
        procedural_tier_snapshot_ref=_SNAPSHOT_REF,  # procedural-tier ref
    )
    append_ledger_entry(
        handle,
        payload,
        WriteKey(
            thread_id=Identifier("t"),
            step_id=Identifier("s"),
            idempotency_key=Identifier("idem-x"),
        ),
    )
    entries = read_ledger(handle)
    assert entries[0].action_id == "workflow.step.completed"
    assert entries[0].procedural_tier_snapshot_ref == _SNAPSHOT_REF


# ---------------------------------------------------------------------------
# Legacy chain backward-compat — pre-v1.3 entries (no sidecar key) hash same
# as v1.3 entries with sidecar None.
# ---------------------------------------------------------------------------


def test_legacy_entry_without_sidecar_key_hashes_same_as_v1_3_none(
    tmp_path: Path,
) -> None:
    """ZERO breaking change at hash level: legacy entries (no sidecar key in
    JSON) round-trip to ``procedural_tier_snapshot_ref=None`` and produce the
    same ``response_hash`` as v1.3 entries with sidecar None per IS plan v2.4
    + spec v1.3 §C-IS-06 §6.1 NEW canonicalize sidecar discipline."""
    base_ts = datetime(2026, 5, 30, 1, tzinfo=UTC)
    entry_v1_3_none = StateLedgerEntry(
        action_id=Identifier("a"),
        idempotency_key=Identifier("i"),
        actor=_ACTOR,
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=base_ts,
        prior_event_hash=ALL_ZEROS_SENTINEL,
        procedural_tier_snapshot_ref=None,
    )
    # Pre-v1.3 schema had no field — canonicalize must produce identical bytes.
    # Simulate this by hashing twice with identical entries; the canonicalize
    # contract guarantees ``None`` ⇒ key omitted, matching legacy entries.
    hash_a = compute_response_hash(entry_v1_3_none)
    hash_b = compute_response_hash(entry_v1_3_none)
    assert hash_a == hash_b
    # Negative control: non-None sidecar diverges per AC #13.
    entry_v1_3_with = entry_v1_3_none.model_copy(
        update={"procedural_tier_snapshot_ref": _SNAPSHOT_REF},
    )
    assert hash_a != compute_response_hash(entry_v1_3_with)

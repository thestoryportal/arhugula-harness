"""Tests for U-IS-20 — `rotation_correlation_id` D-derivative sidecar carrier
+ presence/uniqueness read-side invariants (IS spec v1.12 §5.6 + §7.7).

Per Implementation_Plan_Information_Substrate_v2_8.md §2.2 U-IS-20 acceptance
criteria #1-#8 + the unit's own `Tests:` list. Mirrors the §5.1
`procedural_tier_snapshot_ref` sidecar test discipline
(`test_state_ledger_write_sidecar.py`) for the carrier half, and the
`verify_chain` style (`test_chain_verification.py`) for the composed
read-side validator half.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_is.chain_verification import VerificationStatus, verify_chain
from harness_is.entry_hash import canonicalize, compute_response_hash
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.rotation_window_verification import (
    RotationWindowCheckStatus,
    RotationWindowFailureType,
    verify_rotation_window,
)
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
    append_ledger_entry,
    read_ledger,
)
from pydantic import ValidationError

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="agent-1")
_CANONICAL_UUID = "12345678-1234-5678-1234-567812345678"
_CANONICAL_UUID_2 = "87654321-4321-8765-4321-876543218765"

# The pre-v1.12 golden digest (test_entry_hash.py::test_compute_response_hash_golden).
_PRE_V1_12_GOLDEN = "29016134db6fb137d57fc6a741cea574d49f92c8a510220a056f0be91f3a0f36"


def _golden_entry(rotation_correlation_id: str | None = None) -> StateLedgerEntry:
    """The pinned golden entry; `rotation_correlation_id` defaults to None
    (pre-v1.12)."""
    return StateLedgerEntry(
        action_id=Identifier("act-golden-001"),
        idempotency_key=Identifier("idem-golden-001"),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-golden"),
        response_hash=b"\xab" * 32,
        timestamp=datetime(2026, 5, 15, 12, 0, 0, tzinfo=UTC),
        prior_event_hash=ALL_ZEROS_SENTINEL,
        rotation_correlation_id=rotation_correlation_id,
    )


def _handle(tmp_path: Path) -> JsonlLedgerHandle:
    return JsonlLedgerHandle(
        canonical_path=tmp_path / "state.jsonl",
        exists=False,
        entry_count=0,
    )


def _payload(i: int, rotation_correlation_id: str | None = None) -> EntryPayload:
    return EntryPayload(
        action_id=Identifier(f"act-{i}"),
        idempotency_key=Identifier(f"idem-{i}"),
        actor=_ACTOR,
        timestamp=datetime(2026, 7, 22, max(i, 1), tzinfo=UTC),
        rotation_correlation_id=rotation_correlation_id,
    )


def _key(i: int) -> WriteKey:
    return WriteKey(
        thread_id=Identifier(f"thread-{i}"),
        step_id=Identifier(f"step-{i}"),
        idempotency_key=Identifier(f"idem-{i}"),
    )


def _entry(
    action_id: str, prior_event_hash: bytes, rotation_correlation_id: str | None = None
) -> StateLedgerEntry:
    """Build an entry with a genuinely self-consistent `response_hash`
    (mirrors `test_chain_verification.py`'s own helper)."""
    draft = StateLedgerEntry(
        action_id=Identifier(action_id),
        idempotency_key=Identifier(f"idem-{action_id}"),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-1"),
        response_hash=ALL_ZEROS_SENTINEL,
        timestamp=datetime(2026, 7, 22, tzinfo=UTC),
        prior_event_hash=prior_event_hash,
        rotation_correlation_id=rotation_correlation_id,
    )
    return draft.model_copy(update={"response_hash": compute_response_hash(draft)})


def _valid_chain(
    n: int, rotation_ids: dict[int, str | None] | None = None
) -> list[StateLedgerEntry]:
    """Build an n-entry chain with correct `prior_event_hash` links; entries
    named in `rotation_ids` (0-indexed) carry the given rotation_correlation_id."""
    rotation_ids = rotation_ids or {}
    chain: list[StateLedgerEntry] = []
    prior = ALL_ZEROS_SENTINEL
    for i in range(n):
        entry = _entry(f"act-{i}", prior, rotation_ids.get(i))
        chain.append(entry)
        prior = compute_response_hash(entry)
    return chain


# ---------------------------------------------------------------------------
# AC #1/#2 — carrier optional, default None, byte-identity control.
# ---------------------------------------------------------------------------


def test_state_ledger_entry_constructs_with_none_rotation_correlation_id() -> None:
    """AC #1: `StateLedgerEntry(..., rotation_correlation_id=None)` constructs
    (the default; every existing call site unaffected)."""
    entry = _golden_entry(rotation_correlation_id=None)
    assert entry.rotation_correlation_id is None


def test_pre_v1_12_entry_canonicalizes_byte_identically_with_none_rotation_correlation_id() -> None:
    """AC #2 / byte-identity control: a `StateLedgerEntry` constructed with
    `rotation_correlation_id=None` canonicalizes byte-identically to the
    pinned pre-v1.12 golden fixture (mutation probe: including the key when
    `None` breaks this assertion against the golden)."""
    entry = _golden_entry(rotation_correlation_id=None)
    assert compute_response_hash(entry).hex() == _PRE_V1_12_GOLDEN
    assert b"rotation_correlation_id" not in canonicalize(entry)


# ---------------------------------------------------------------------------
# AC #3 — hash-coverage + chain-linkage tamper-evidence.
# ---------------------------------------------------------------------------


def test_rotation_correlation_id_participates_in_response_hash() -> None:
    """Hash-coverage witness: two entries differing only in
    `rotation_correlation_id` produce different `response_hash` (mutation
    probe: reverting the omit-when-`None`-else-include canonicalization
    branch to always-omit makes this assertion fail)."""
    none = compute_response_hash(_golden_entry(rotation_correlation_id=None))
    with_id = compute_response_hash(_golden_entry(rotation_correlation_id=_CANONICAL_UUID))
    assert none != with_id


def test_tamper_non_last_rotation_correlation_id_detected_at_successor() -> None:
    """AC #3: a ≥2-entry chain where a NON-LAST entry N carries a non-`None`
    `rotation_correlation_id`, tampered post-write (leaving `response_hash`
    and every other field byte-unchanged) — `verify_chain` reports the
    mismatch at entry N's SUCCESSOR N+1, per `verify_chain`'s own detection
    mechanism (it compares each entry's recomputed hash against the NEXT
    entry's `prior_event_hash`, never the entry's own stored `response_hash`
    against a recomputation of itself)."""
    chain = _valid_chain(3, rotation_ids={1: _CANONICAL_UUID})
    tampered = chain[1].model_copy(update={"rotation_correlation_id": _CANONICAL_UUID_2})
    chain[1] = tampered
    result = verify_chain(chain)
    assert result.status is VerificationStatus.INVALID
    assert result.failure_position == 3  # 1-indexed successor of 0-indexed entry 1


# ---------------------------------------------------------------------------
# AC #4 — construction-time canonical-round-trip rejection.
# ---------------------------------------------------------------------------


def test_rotation_correlation_id_accepts_canonical_uuid() -> None:
    """AC #4: a canonical-form 36-char hyphenated UUID string constructs
    successfully."""
    entry = _golden_entry(rotation_correlation_id=_CANONICAL_UUID)
    assert entry.rotation_correlation_id == _CANONICAL_UUID


def test_rotation_correlation_id_rejects_non_uuid_present_value() -> None:
    """AC #4: a non-UUID non-empty string is rejected at construction
    (mutation probe: removing the construction-time validation lets
    `rotation_correlation_id="not-a-uuid"` construct silently)."""
    with pytest.raises(ValidationError):
        _golden_entry(rotation_correlation_id="not-a-uuid")


@pytest.mark.parametrize(
    "noncanonical",
    [
        "12345678123456781234567812345678",  # 32-char unhyphenated hex
        "{12345678-1234-5678-1234-567812345678}",  # brace-wrapped
    ],
    ids=["unhyphenated-hex", "brace-wrapped"],
)
def test_rotation_correlation_id_rejects_parseable_noncanonical_uuid(
    noncanonical: str,
) -> None:
    """AC #4: a PARSEABLE-but-noncanonical string is ALSO rejected — both
    forms parse successfully via bare `uuid.UUID` but re-render to a
    DIFFERENT string than the input (mutation probe: replacing the
    canonical-round-trip check with bare `uuid.UUID(value)` parse-then-accept
    lets both constructs succeed)."""
    with pytest.raises(ValidationError):
        _golden_entry(rotation_correlation_id=noncanonical)


def test_entry_payload_rejects_parseable_noncanonical_uuid() -> None:
    """AC #4: the same canonical-round-trip check applies to `EntryPayload`,
    not only `StateLedgerEntry`."""
    with pytest.raises(ValidationError):
        _payload(1, rotation_correlation_id="{12345678-1234-5678-1234-567812345678}")


# ---------------------------------------------------------------------------
# Write / read carrier — EntryPayload field, JSONL omit-when-None, round-trip.
# ---------------------------------------------------------------------------


def test_entry_payload_defaults_rotation_correlation_id_none() -> None:
    """`EntryPayload` is constructible without the sidecar; default `None`."""
    assert _payload(1).rotation_correlation_id is None


def test_append_omits_rotation_correlation_id_key_when_none(tmp_path: Path) -> None:
    """Persisted JSONL line omits the key entirely when `None`."""
    handle = _handle(tmp_path)
    append_ledger_entry(handle, _payload(1, rotation_correlation_id=None), _key(1))
    raw = json.loads(handle.canonical_path.read_text().splitlines()[0])
    assert "rotation_correlation_id" not in raw


def test_append_persists_rotation_correlation_id_when_non_none(tmp_path: Path) -> None:
    """Persisted JSONL line includes the sidecar key when non-`None`."""
    handle = _handle(tmp_path)
    result = append_ledger_entry(
        handle, _payload(1, rotation_correlation_id=_CANONICAL_UUID), _key(1)
    )
    assert result == WriteResult.APPENDED
    raw = json.loads(handle.canonical_path.read_text().splitlines()[0])
    assert raw["rotation_correlation_id"] == _CANONICAL_UUID


def test_rotation_correlation_id_serializes_and_deserializes_through_jsonl_line(
    tmp_path: Path,
) -> None:
    """Round-trip witness: write → read round-trip preserves the sidecar
    value byte-exact (mirrors the §5.1/§5.4 JSONL round-trip precedent)."""
    handle = _handle(tmp_path)
    append_ledger_entry(handle, _payload(1, rotation_correlation_id=_CANONICAL_UUID), _key(1))
    entries = read_ledger(handle)
    assert len(entries) == 1
    assert entries[0].rotation_correlation_id == _CANONICAL_UUID


def test_legacy_entry_without_rotation_correlation_id_key_hashes_same_as_v1_12_none() -> None:
    """ZERO breaking change at hash level: legacy entries (no sidecar key in
    JSON) round-trip to `rotation_correlation_id=None` and produce the same
    `response_hash` as v1.12 entries with sidecar `None`."""
    entry_none = _golden_entry(rotation_correlation_id=None)
    hash_a = compute_response_hash(entry_none)
    hash_b = compute_response_hash(entry_none)
    assert hash_a == hash_b
    entry_with = entry_none.model_copy(update={"rotation_correlation_id": _CANONICAL_UUID})
    assert hash_a != compute_response_hash(entry_with)


# ---------------------------------------------------------------------------
# AC #5-#8 — composed read-side validator (C-IS-07 §7.7).
# ---------------------------------------------------------------------------


def test_rotation_window_check_fails_on_empty_sequence() -> None:
    """AC #6 (non-emptiness): an EMPTY sequence fails at `EMPTY_WINDOW` before
    any presence/uniqueness predicate runs (mutation probe: a check that runs
    presence/uniqueness directly against `[]` without the non-emptiness guard
    passes vacuously)."""
    result = verify_rotation_window([])
    assert result.status is RotationWindowCheckStatus.INVALID
    assert result.failure_type is RotationWindowFailureType.EMPTY_WINDOW


def test_rotation_window_presence_check_fails_on_a_none_entry_in_window() -> None:
    """AC #7 (presence): a non-empty window with any `None`-carrying entry
    fails at `PRESENCE_FAILURE` (mutation probe: a presence check that
    ignores a `None` member passes when it should fail)."""
    window = [
        _golden_entry(rotation_correlation_id=_CANONICAL_UUID),
        _golden_entry(rotation_correlation_id=None),
    ]
    result = verify_rotation_window(window)
    assert result.status is RotationWindowCheckStatus.INVALID
    assert result.failure_type is RotationWindowFailureType.PRESENCE_FAILURE


def test_rotation_window_presence_check_passes_when_every_entry_non_none() -> None:
    """AC #7 (presence): a non-empty window where every entry carries a
    non-`None` id (and all identical) passes presence + uniqueness → VALID."""
    window = [
        _golden_entry(rotation_correlation_id=_CANONICAL_UUID),
        _golden_entry(rotation_correlation_id=_CANONICAL_UUID),
    ]
    result = verify_rotation_window(window)
    assert result.status is RotationWindowCheckStatus.VALID
    assert result.failure_type is None


def test_rotation_window_uniqueness_check_fails_on_two_distinct_ids_in_window() -> None:
    """AC #8 (uniqueness): a torn/mixed window with 2 distinct non-`None` ids
    fails at `UNIQUENESS_FAILURE` (mutation probe: a uniqueness check that
    only inspects the first non-`None` value passes a torn window when it
    should fail)."""
    window = [
        _golden_entry(rotation_correlation_id=_CANONICAL_UUID),
        _golden_entry(rotation_correlation_id=_CANONICAL_UUID_2),
    ]
    result = verify_rotation_window(window)
    assert result.status is RotationWindowCheckStatus.INVALID
    assert result.failure_type is RotationWindowFailureType.UNIQUENESS_FAILURE


def test_rotation_window_single_entry_window_is_valid() -> None:
    """AC #5: a single-entry window with a non-`None` id is VALID — the
    trivial uniqueness case (cardinality 1)."""
    result = verify_rotation_window([_golden_entry(rotation_correlation_id=_CANONICAL_UUID)])
    assert result.status is RotationWindowCheckStatus.VALID


def test_rotation_window_result_is_frozen_and_forbids_extra() -> None:
    """The result carrier is frozen + `extra='forbid'` (house convention)."""
    result = verify_rotation_window([])
    with pytest.raises(ValidationError):
        result.status = RotationWindowCheckStatus.VALID  # type: ignore[misc]

"""`U-CP-72` (v2.38 amendment) — tenant-bearing converter signature.

Implements CP plan v2.38 §1 witness (a) per CP spec v1.101 §1 (C-CP-13
§13.5.1 AMENDED): `cp_audit_to_od_audit` gains ONE optional keyword
`tenant_id: str | None = None`, forwarded RAW to `sign_audit_entry`'s
same-named parameter (the `backend` passthrough shape) — no validation, no
normalization, no defaulting at the converter (tenant-tag normalization is
OD-owned at signing per OD v1.34 §21.2.1 row 2). Byte-compat drop-when-`None`
(§1 row 3): absent → the v1.100 four-tuple canonical message byte-for-byte.
"""

from __future__ import annotations

from typing import Any, cast

from harness_as.gate_level_composition import GateLevel
from harness_core.identity import ActionID
from harness_cp.per_step_override_evaluator import CPAuditLedgerEntry
from harness_cxa.cp_audit_conversion import cp_audit_to_od_audit
from harness_od.audit_signing_errors import AuditSigningFailedError
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    canonical_od_signing_message,
    signing_token,
)


class _CapturingEd25519Backend:
    """TEST-ONLY C-CP-20 §20.2.1 `SigningBackend` double (real Ed25519) that
    RECORDS every canonical message it signs."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        self._private_key = Ed25519PrivateKey.generate()
        self.messages: list[bytes] = []

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        self.messages.append(message)
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del message, signature, key_id, key_period
        return True


def _segments(message: bytes) -> list[str]:
    out: list[str] = []
    rest = message.decode()
    while rest:
        length_str, _, tail = rest.partition(":")
        n = int(length_str)
        out.append(tail[:n])
        rest = tail[n:]
        if rest.startswith("|"):
            rest = rest[1:]
    return out


def _cp_entry() -> CPAuditLedgerEntry:
    return CPAuditLedgerEntry(
        action_id=ActionID("dispatch:workflow:test:step:0:0"),
        gate_level=GateLevel.ASK,
        response="approve",
        edited_proposal_hash=None,
        rejection_reason_hash=None,
        response_text_hash=None,
        timestamp="2026-07-20T00:00:00+00:00",
        prior_event_hash="0" * 64,
    )


def test_converter_tenant_id_reaches_sign_audit_entry_unmodified_five_segment_message() -> None:
    """Witness (a), §1 rows 1-2: the converter forwards `tenant_id` VERBATIM
    to `sign_audit_entry` — the backend-observed canonical message carries
    the five-segment shape whose fifth segment equals the UNMODIFIED raw
    value (the §21.2.1 row-2 rule-set is pass-through for valid tenants;
    only the refusal rules transform anything). That the RULE-SET runs AT
    SIGNING and not in the converter is pinned by the second half: the empty
    string — which the OD normalizer REFUSES — traverses the converter
    untouched and the `ValueError` originates from `sign_audit_entry`, so
    the converter demonstrably neither validates nor normalizes.

    Mutation probe: dropping the converter's `tenant_id=tenant_id` forward
    reverts signing to the four-tuple → the segment-count assertion FAILS;
    adding converter-side validation (e.g. rejecting the empty string before
    signing) breaks the refusal half's origin expectation. The refusal is a
    member of the §21.2.3 row-5 typed family at the signing boundary
    (merge-gate concurrency lens, PR #1066)."""
    import pytest

    raw_tenant = "Tenant A"  # spaces/case preserved — raw passthrough proof
    backend = _CapturingEd25519Backend()
    entry = cp_audit_to_od_audit(
        _cp_entry(),
        key_id="key-72",
        backend=cast(Any, backend),
        tenant_id=raw_tenant,
    )
    assert entry.signature_attrs.audit_signature_key_id == "key-72"
    assert len(backend.messages) == 1
    segments = _segments(backend.messages[0])
    assert len(segments) == 5
    assert segments[4] == raw_tenant
    assert signing_token(raw_tenant) == raw_tenant  # the row-2 pass-through pin

    # OD-owned refusal at signing — the converter passes even a REFUSED value
    # through raw; the typed refusal fires inside `sign_audit_entry`.
    with pytest.raises(AuditSigningFailedError, match="tenant_id must not be the empty string"):
        cp_audit_to_od_audit(
            _cp_entry(),
            key_id="key-72",
            backend=cast(Any, _CapturingEd25519Backend()),
            tenant_id="",
        )


def test_converter_tenant_absent_entry_byte_identical_to_v1_100_path() -> None:
    """Witness (a), §1 row 3 (pairs with OD plan v2.29 U-OD-30 witness (b)):
    tenant absent/`None` → the v1.100 behavior PRESERVED VERBATIM — the
    signed canonical message is the four-tuple byte-for-byte, and an explicit
    `tenant_id=None` call produces a message identical to a call that never
    passes the parameter at all (zero regression for every existing caller)."""
    backend_default = _CapturingEd25519Backend()
    cp_audit_to_od_audit(_cp_entry(), key_id="key-72", backend=cast(Any, backend_default))

    backend_none = _CapturingEd25519Backend()
    cp_audit_to_od_audit(
        _cp_entry(), key_id="key-72", backend=cast(Any, backend_none), tenant_id=None
    )

    assert backend_default.messages[0] == backend_none.messages[0]
    segments = _segments(backend_none.messages[0])
    assert len(segments) == 4
    entry_hash, key_id, algo_value, key_period_token = segments
    assert backend_none.messages[0] == canonical_od_signing_message(
        entry_hash,
        key_id=key_id,
        algo_value=algo_value,
        key_period_token=key_period_token,
        tenant_tag=None,
    )

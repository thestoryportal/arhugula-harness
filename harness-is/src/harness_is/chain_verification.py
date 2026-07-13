"""Chain verification + tamper-evidence procedure — U-IS-10.

Implements C-IS-06 §6.4 (chain verification on demand) + §6.5 (tamper-evidence
contract). Declares `verify_chain` — the read-only procedure that re-derives
each entry's hash and checks the `prior_event_hash` links end-to-end.

Per §6.4 the verification checks only the chain links: entry N+1's
`prior_event_hash` must equal `compute_response_hash(entry N)`, and entry 1's
`prior_event_hash` must be `ALL_ZEROS_SENTINEL`. Any tamper (§6.5) surfaces as
a verification failure at the affected 1-indexed position.

**Deliberately no per-entry `response_hash` self-check.** §6.4's four-step
algorithm never reads an entry's own stored `response_hash` field — it
recomputes hashes fresh for the linkage comparison. This is load-bearing, not
an oversight: `response_hash` is a producer-populated field whose formula is
axis-specific (C-IS-06 §6.2's generic recipe for most producers, but C-AS-08
§8.2 legitimately overrides it to the `outputs_hash` structure-not-content
fingerprint for secret-fetch entries). A universal
`entry.response_hash == compute_response_hash(entry)` check would reject
every spec-compliant secret-fetch entry as tampered. Chain-linkage tamper-
evidence (this function's actual contract) does not depend on
`response_hash` at all: `canonicalize` excludes it, so it is never part of
what a neighbor's link check verifies either.

Authority: Implementation_Plan_Information_Substrate_v2_3.md §2.1 U-IS-10
(preserved verbatim from v2.1 §2); Spec_Information_Substrate_v1.md C-IS-06
§6.4 / §6.5; ADR-F2 v1.2 §Rationale (a.1).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from harness_is.entry_hash import compute_response_hash
from harness_is.state_ledger_entry_schema import ALL_ZEROS_SENTINEL, StateLedgerEntry


class VerificationStatus(StrEnum):
    """Overall outcome of a chain verification (C-IS-06 §6.4)."""

    VALID = "valid"
    INVALID = "invalid"


class FailureType(StrEnum):
    """The class of a chain verification failure (C-IS-06 §6.4 / §6.5)."""

    INCEPTION_SENTINEL_MISMATCH = "inception_sentinel_mismatch"
    CHAIN_LINK_MISMATCH = "chain_link_mismatch"


class ChainVerificationResult(BaseModel):
    """The result of a `verify_chain` inspection (C-IS-06 §6.4)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: VerificationStatus
    failure_position: int | None
    failure_type: FailureType | None
    entries_verified: int


def verify_chain(ledger: list[StateLedgerEntry]) -> ChainVerificationResult:
    """Verify a state-ledger hash chain (C-IS-06 §6.4 / §6.5).

    Read-only — the `ledger` list and its entries are never modified. Positions
    are 1-indexed. An empty ledger is `VALID`. Entry 1's `prior_event_hash`
    must be `ALL_ZEROS_SENTINEL` (else `INCEPTION_SENTINEL_MISMATCH` at
    position 1); each subsequent entry's `prior_event_hash` must equal
    `compute_response_hash` of its predecessor (else `CHAIN_LINK_MISMATCH` at
    that entry's position). `entries_verified` counts entries cleared before
    any failure.
    """
    if not ledger:
        return ChainVerificationResult(
            status=VerificationStatus.VALID,
            failure_position=None,
            failure_type=None,
            entries_verified=0,
        )
    if ledger[0].prior_event_hash != ALL_ZEROS_SENTINEL:
        return ChainVerificationResult(
            status=VerificationStatus.INVALID,
            failure_position=1,
            failure_type=FailureType.INCEPTION_SENTINEL_MISMATCH,
            entries_verified=0,
        )
    for i in range(1, len(ledger)):
        if ledger[i].prior_event_hash != compute_response_hash(ledger[i - 1]):
            return ChainVerificationResult(
                status=VerificationStatus.INVALID,
                failure_position=i + 1,
                failure_type=FailureType.CHAIN_LINK_MISMATCH,
                entries_verified=i,
            )
    return ChainVerificationResult(
        status=VerificationStatus.VALID,
        failure_position=None,
        failure_type=None,
        entries_verified=len(ledger),
    )

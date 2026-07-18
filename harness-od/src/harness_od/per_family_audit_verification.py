"""Per-family audit verification — `B-49` (split from the B-47 close-out).

A tenant's persisted audit entries interleave INDEPENDENT producer families,
and most families do not chain at all: cost projection, HITL gate audits, and
sub-agent dispatch deliberately emit constant non-chained `prior_entry_hash`
values on every entry (zero-hash genesis for cost/dispatch; `sha256(b"")` for
HITL — constant either way, never a predecessor link), so running `verify_hash_chain_integrity` over a raw
per-tenant sequence — or even over a naive per-prefix partition — reports
false tampering on the second untouched entry.

Producer-aware policy (per `.harness/b-47-pr-b2-design-disposition-v1.md`,
codex rounds 3/5/7/9 of that leg):

- **Every entry, every family**: per-entry CONTENT-HASH verification
  (`compute_entry_hash(payload) == entry_hash`) — a payload mutated in place
  with its stored hash left untouched is caught regardless of family.
- **Chain verification ONLY for the redaction-token family** — the one
  producer with real chain-position wiring today
  (`AuditLedgerRedactionTokenMap` seeds `prior_entry_hash` from its durable
  tail). The family is discriminated by the `audit.redaction_token.*`
  NAMESPACE KEYS the composer stamps on every redaction row — NOT by
  `entry_core` prefix, which misses rows composed with a caller-supplied
  `entry_core` (the map's own `_seed_chain_from_durable_tail` documents this;
  PR B1 codex round-39).
- **Backend signature verification is OUT of scope** — `B-54`
  (§21.2.1 leaves verification out of scope; adding a backend-aware
  verification API is spec surface).

Raises `HashChainBreach` (the existing U-OD-30 error arm) on the first
violation; returns a frozen per-family report on success.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import HashChainBreach

__all__ = [
    "REDACTION_TOKEN_FAMILY",
    "REDACTION_TOKEN_NAMESPACE_PREFIX",
    "FamilyVerificationReport",
    "verify_per_family_chains",
]

REDACTION_TOKEN_NAMESPACE_PREFIX = "audit.redaction_token."
"""Namespace-key prefix the redaction-token composer stamps on every row —
the family discriminator (caller-supplied `entry_core` rows carry no
reliable `entry_core` prefix)."""

REDACTION_TOKEN_FAMILY = "redaction-token"
"""Report key for the one chain-verified family."""


@dataclass(frozen=True, slots=True)
class FamilyVerificationReport:
    """Deeply immutable result of a successful `verify_per_family_chains` run.

    `chained` maps each CHAIN-VERIFIED family to its entry count;
    `per_entry` maps each content-hash-only family (keyed by `entry_core`
    prefix, or `"(unprefixed)"`) to its entry count. Counts exist so a
    caller can assert coverage — a verifier that silently classified every
    row into an empty family would otherwise look identical to success.
    The mappings are `MappingProxyType` views (codex round-1 on the B-49
    landing): a frozen carrier over MUTABLE dicts would still allow
    `report.chained[...] = ...` to alter verification evidence after the
    fact.
    """

    chained: Mapping[str, int]
    per_entry: Mapping[str, int]

    def __post_init__(self) -> None:
        # The invariant belongs to the TYPE (codex round-2 on the B-49
        # landing): a direct constructor caller passing a mutable dict must
        # not retain a mutation handle into the report — copy then wrap.
        object.__setattr__(self, "chained", MappingProxyType(dict(self.chained)))
        object.__setattr__(self, "per_entry", MappingProxyType(dict(self.per_entry)))


def _is_redaction_row(entry: AuditLedgerEntry) -> bool:
    return any(
        key.startswith(REDACTION_TOKEN_NAMESPACE_PREFIX)
        for key in entry.payload.audit_namespace_attrs
    )


def _per_entry_family_key(entry: AuditLedgerEntry) -> str:
    core = str(entry.payload.entry_core)
    prefix, sep, _rest = core.partition(":")
    return prefix if sep else "(unprefixed)"


def verify_per_family_chains(entries: Sequence[AuditLedgerEntry]) -> FamilyVerificationReport:
    """Producer-aware verification over an interleaved audit-entry sequence.

    See the module docstring for the policy. Content check runs FIRST over
    every entry (mirroring `verify_hash_chain_integrity`'s
    content-before-linkage order), then linkage over the redaction-token
    subsequence only.
    """
    for i, entry in enumerate(entries):
        recomputed = compute_entry_hash(entry.payload)
        if recomputed != entry.entry_hash:
            raise HashChainBreach(
                f"audit entry {i} content integrity violated: stored "
                f"entry_hash={entry.entry_hash!r} does not match recomputed "
                f"hash={recomputed!r} over the entry's payload — payload "
                f"tampered without recomputing entry_hash (C-OD-21 §21.2)"
            )

    chained: dict[str, int] = {}
    per_entry: dict[str, int] = {}
    redaction_rows: list[AuditLedgerEntry] = []
    for entry in entries:
        if _is_redaction_row(entry):
            redaction_rows.append(entry)
        else:
            key = _per_entry_family_key(entry)
            per_entry[key] = per_entry.get(key, 0) + 1

    if redaction_rows:
        # Content was already verified above; the LINKAGE check is what the
        # redaction family's real chain-position wiring makes meaningful.
        # Inlined (mirroring verify_hash_chain_integrity's linkage loop)
        # rather than wrapped in AuditLedger, whose carrier requires a
        # CellID this pure verification surface has no business inventing.
        for i in range(1, len(redaction_rows)):
            prior_hash = redaction_rows[i].payload.prior_entry_hash
            predecessor_hash = redaction_rows[i - 1].entry_hash
            if prior_hash != predecessor_hash:
                raise HashChainBreach(
                    f"redaction-token family hash chain broken at family "
                    f"index {i}: prior_entry_hash={prior_hash!r} != "
                    f"predecessor entry_hash={predecessor_hash!r} "
                    f"(C-OD-21 §21.2 / B-49 per-family policy)"
                )
        chained[REDACTION_TOKEN_FAMILY] = len(redaction_rows)

    return FamilyVerificationReport(chained=chained, per_entry=per_entry)

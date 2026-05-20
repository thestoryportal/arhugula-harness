"""U-RT-12 — state-ledger writer init + chain reattach.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 (C-RT-02 stage 1 IS post-conditions:
`ctx.ledger_writer` non-None; ledger chain reattached and verified) and Phase 2
Session 3 plan v2.1 §2 L2:

- Opens `.harness/state.jsonl` via `harness_is.initialize_jsonl_event_ledger`
  (fresh-creates an empty ledger when absent; line-counts an existing file).
- On reattach (existing entries), invokes `harness_is.verify_chain`; a
  `VerificationStatus.INVALID` result raises `TamperedChainError`.
- Wraps `harness_is.append_ledger_entry` behind a `LedgerWriter` handle bound
  to a fixed `Actor` (the runtime's identity for this process).

The "genesis entry" semantics per the plan AC are an EMERGENT property of the
hash-chain construction (C-IS-06 §6): the first entry written has
`prior_event_hash = ALL_ZEROS_SENTINEL`, which `verify_chain` checks at the
inception position. No genesis ENTRY is materialized at fresh-create — the
ledger is empty and chain-VALID per `verify_chain` on an empty list.

Risk-flag absorption (plan §2 U-RT-12):
- "reattach semantics across crashed prior run may surface IS spec gap" —
  `initialize_jsonl_event_ledger` resolves to an existing file via line count;
  `read_ledger` parses every non-empty line into a `StateLedgerEntry`;
  malformed lines surface as `ValidationError` (from Pydantic) at reattach
  time. No partial-write recovery — a crashed prior run mid-write surfaces as
  a JSON-malformed final line and reattach fails. Recovery semantics deferred
  to a future IS spec amendment if surfaced by real workloads.
"""

from __future__ import annotations

from dataclasses import dataclass

from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_is.chain_verification import ChainVerificationResult, VerificationStatus, verify_chain
from harness_is.jsonl_event_ledger_lifecycle import (
    JsonlLedgerHandle,
    initialize_jsonl_event_ledger,
)
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import Actor
from harness_is.state_ledger_write import (
    EntryPayload,
    WriteKey,
    WriteResult,
    append_ledger_entry,
    read_ledger,
)

__all__ = [
    "LedgerWriter",
    "TamperedChainError",
    "materialize_state_ledger",
]


class TamperedChainError(Exception):
    """Raised when reattach detects a `verify_chain` failure (C-IS-06 §6.4)."""

    def __init__(self, result: ChainVerificationResult) -> None:
        super().__init__(
            f"chain verification failed at position {result.failure_position}: "
            f"{result.failure_type.value if result.failure_type else 'unknown'}"
        )
        self.result = result


@dataclass(frozen=True)
class LedgerWriter:
    """Runtime wrapper around IS state-ledger primitives (C-RT-04 `ledger_writer`).

    Bound to a fixed `Actor` at construction (the runtime's identity). The
    append surface enforces C-IS-07 §7.1 idempotency-key discipline via
    `harness_is.append_ledger_entry`.
    """

    handle: JsonlLedgerHandle
    actor: Actor

    def append(self, payload: EntryPayload, write_key: WriteKey) -> WriteResult:
        """Append a hash-chain-preserving entry; pass-through to IS U-IS-11."""
        return append_ledger_entry(self.handle, payload, write_key)

    @property
    def entry_count(self) -> int:
        """Current ledger entry count (snapshot at handle construction)."""
        return self.handle.entry_count

    @property
    def is_genesis(self) -> bool:
        """`True` when no entries exist yet (next append produces the chain head)."""
        return self.handle.entry_count == 0


def materialize_state_ledger(
    resolver: PathResolver,
    *,
    workflow_class: WorkloadClass,
    deployment_surface: DeploymentSurface,
    actor: Actor,
) -> LedgerWriter:
    """Init the state ledger handle; reattach with chain verification.

    Steps:
    1. Resolve canonical path via `initialize_jsonl_event_ledger` (creates
       empty file if absent).
    2. If existing entries, `read_ledger` + `verify_chain`. A
       `VerificationStatus.INVALID` result raises `TamperedChainError`.
    3. Wrap the handle + actor in a frozen `LedgerWriter`.

    Raises
    ------
    TamperedChainError
        Existing ledger chain fails `verify_chain` (chain-link mismatch or
        inception sentinel mismatch per C-IS-06 §6.4).
    pydantic.ValidationError
        Malformed JSON / entry shape detected at `read_ledger`. Crashed-
        mid-write recovery is not implemented at U-RT-12; surface at landing
        if a real workload needs it.
    """
    handle = initialize_jsonl_event_ledger(resolver, workflow_class, deployment_surface)
    if handle.entry_count > 0:
        entries = read_ledger(handle)
        result = verify_chain(entries)
        if result.status is VerificationStatus.INVALID:
            raise TamperedChainError(result)
    return LedgerWriter(handle=handle, actor=actor)

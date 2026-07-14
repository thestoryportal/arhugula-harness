"""Shared F2-write helper for the 4 cost-attribution composers.

Per B-23 (`.harness/post-phase-8-forward-register.md`): the 4 production
cost-attribution composers (`cost_attribution_tool_dispatch.py`,
`cost_attribution_llm_dispatch.py`, `cost_attribution_webhook_dispatch.py`,
`cost_attribution_validator_dispatch.py`) called `cp_audit_to_od_audit(...)`
with no `entry_core`, so `harness_cxa.cp_audit_conversion._entry_core_or_default`
synthesized an opaque `cp-audit:<action_id>` marker instead of a real IS
state-ledger anchor — unlike `sub_agent_dispatch.py`'s 8a/8b/8c pattern
(compose → F2-write via `ledger_writer.append` → convert with the real
action_id as `entry_core`).

This helper performs the same F2 write for a cost-attribution event and
returns the resulting `StateLedgerEntryRef`, or `None` when no
`ledger_writer` is bound (preserves pre-existing unit-test ergonomics —
those callers keep the fabricated-marker fallback at the converter).

`procedural_tier_snapshot_ref` is populated whenever a resolver is bound:
per IS spec v1.3 §C-IS-05 §5.1, an active-workflow-context F2 write MUST
carry the sidecar (H_T-IS-2 "all producer sites handled" retirement
invariant) — these composers fire inside an active workflow step (they
hold workflow_id/parent_action_id), so they are producer sites, not one
of the 3 documented `None`-canonical outside-workflow-context exceptions.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import EntryPayload, WriteKey
from harness_od.audit_ledger_types import StateLedgerEntryRef

__all__ = ["compose_cost_f2_entry_core"]

#: The F2 entry's recorded actor for every cost-attribution write. Cost
#: attribution is an autonomous harness bookkeeping action following the
#: parent dispatch, not itself an operator or sub-agent action — `AGENT`
#: is the closest of the 3 `ActorClass` values (C-IS-05 §5).
_COST_ATTRIBUTION_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="harness-cost-attribution")


def compose_cost_f2_entry_core(
    *,
    ledger_writer: Any | None,
    procedural_tier_snapshot_resolver: Callable[[], Identifier] | None,
    workflow_id: str,
    parent_action_id: str,
    dispatch_disambiguator: str,
    time_source: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> StateLedgerEntryRef | None:
    """F2-write one cost-attribution dispatch fact; return its `entry_core`.

    `dispatch_disambiguator` MUST be unique per billable event sharing the
    same `(workflow_id, parent_action_id)` — e.g. a real per-attempt OTel
    span_id for tool/LLM/webhook dispatch (a fresh span opens per retry
    attempt), or the validator framework's monotonic `burden_count` for
    validator dispatch (whose `span_id` is a *synthesized*, not real,
    `f"validator-evaluate-{workflow_id}-{step_id}"` string that repeats
    identically across a REVALIDATE retry loop on the same step). Without
    a unique disambiguator, a second billable event on the same step
    computes the same `idempotency_key` and `append_ledger_entry` returns
    `IDEMPOTENT_NOOP` — the second cost event's audit entry would then
    reference the FIRST event's F2 anchor, not its own.

    Returns `None` when `ledger_writer` is `None` — the converter's
    `_entry_core_or_default` then falls back to its pre-existing
    `cp-audit:<action_id>` fabricated marker (unit-test ergonomics;
    production bootstrap always binds `ledger_writer`).
    """
    if ledger_writer is None:
        return None

    action_id = Identifier(f"cost:{workflow_id}:{parent_action_id}:{dispatch_disambiguator}")
    procedural_tier_snapshot_ref = (
        procedural_tier_snapshot_resolver()
        if procedural_tier_snapshot_resolver is not None
        else None
    )
    payload = EntryPayload(
        action_id=action_id,
        idempotency_key=action_id,
        actor=_COST_ATTRIBUTION_ACTOR,
        timestamp=time_source(),
        procedural_tier_snapshot_ref=procedural_tier_snapshot_ref,
    )
    write_key = WriteKey(
        thread_id=Identifier(f"cost:{workflow_id}"),
        step_id=action_id,
        idempotency_key=action_id,
    )
    ledger_writer.append(payload, write_key)
    return StateLedgerEntryRef(str(action_id))

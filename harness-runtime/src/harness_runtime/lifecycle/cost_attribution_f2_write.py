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


def _length_prefixed(segment: str) -> str:
    """Encode `segment` so a colon-join of these outputs is injective.

    Round 4/5 (out-of-family Codex) fixed the tenant segment's aliasing one
    case at a time (truthiness, then `_single`, then `""`). advisor()
    flagged that the SAME defect class was still open on every other raw
    colon-joined segment: `parent_action_id` is literally
    `f"workflow:{workflow_id}:step:{n}"` (contains colons), so a bare
    `f"...:{workflow_id}:{parent_action_id}:..."` join is not injective —
    e.g. `workflow_id="a", parent_action_id="b:c"` and
    `workflow_id="a:b", parent_action_id="c"` concatenate identically.
    Length-prefixing every segment (not just tenant) closes the whole class
    in one place: each segment is self-delimiting (read digits up to the
    first `:`, then exactly that many bytes), so the full join has exactly
    one parse, which makes two distinct segment tuples always produce
    distinct joins.
    """
    return f"{len(segment)}:{segment}"


def compose_cost_f2_entry_core(
    *,
    ledger_writer: Any | None,
    procedural_tier_snapshot_resolver: Callable[[], Identifier] | None,
    workflow_id: str,
    parent_action_id: str,
    parent_idempotency_key: str,
    dispatch_disambiguator: str,
    tenant_id: str | None = None,
    time_source: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> StateLedgerEntryRef | None:
    """F2-write one cost-attribution dispatch fact; return its `entry_core`.

    `parent_idempotency_key` (out-of-family Codex [P1], round 3) makes the
    F2 identity RUN-scoped: `workflow_id` is the operator-authored
    `WorkflowManifestEntry.workflow_id` — a stable per-DEFINITION identifier
    reused across every invocation of "that workflow" (per CP spec's own
    `run_idempotency_key = sha256(run_id, workflow_id, entry_version)`
    composition, `workflow_id` and the per-run `run_id` are DISTINCT
    components) — NOT unique per execution. For validator dispatch
    specifically, `dispatch_disambiguator` is a small deterministic space
    (`burden_count`-derived), so re-running the SAME workflow definition a
    second time with an identical validator outcome sequence would compute
    an IDENTICAL F2 key without a run-scoped component, silently pointing
    the second run's audit entry at the first run's F2 anchor.
    `parent_idempotency_key` is already run-scoped (CP composes step-level
    idempotency keys from the run's own idempotency key) and already a
    parameter every one of the 4 composers receives, so it is folded in
    uniformly here (tool/LLM/webhook's real per-attempt `span_id` already
    made this specific failure mode astronomically unlikely for them, but
    the fix costs nothing extra and removes the probabilistic argument).

    `dispatch_disambiguator` MUST additionally be unique per billable event
    sharing the same `(workflow_id, parent_action_id, parent_idempotency_key)`
    WITHIN one run — e.g. a real per-attempt OTel span_id for tool/LLM/
    webhook dispatch (a fresh span opens per retry attempt), or the
    validator framework's monotonic `burden_count` for validator dispatch
    (whose `span_id` is a *synthesized*, not real,
    `f"validator-evaluate-{workflow_id}-{step_id}"` string that repeats
    identically across a REVALIDATE retry loop on the same step). Without
    a unique disambiguator, a second billable event on the same step
    computes the same `idempotency_key` and `append_ledger_entry` returns
    `IDEMPOTENT_NOOP` — the second cost event's audit entry would then
    reference the FIRST event's F2 anchor, not its own.

    `tenant_id` is folded into the F2 identity (mirroring
    `RuntimeAuditLedgerWriter._tenant_tag`'s `audit:` action_id convention)
    because the underlying `LedgerWriter` is SHARED across tenants
    (out-of-family Codex [P1], round 3): two tenants dispatching workflows
    that happen to share the rest of the key would otherwise collide, and
    the second tenant's audit entry would silently reference the first
    tenant's F2 anchor.

    Returns `None` when `ledger_writer` is `None` — the converter's
    `_entry_core_or_default` then falls back to its pre-existing
    `cp-audit:<action_id>` fabricated marker (unit-test ergonomics;
    production bootstrap always binds `ledger_writer`).
    """
    if ledger_writer is None:
        return None

    # Every segment is length-prefixed (see `_length_prefixed`), including a
    # dedicated tenant PRESENCE flag ("1"/"0") ahead of the tenant value —
    # `tenant_id=None` and `tenant_id=""` both carry the empty-string value
    # segment, but only the former gets presence flag "0", so they cannot
    # alias each other (closes round 4/5's tenant-aliasing findings without
    # a bespoke sentinel constant).
    tenant_present = "1" if tenant_id is not None else "0"
    tenant_value = tenant_id if tenant_id is not None else ""
    segments = (
        tenant_present,
        tenant_value,
        workflow_id,
        parent_action_id,
        parent_idempotency_key,
        dispatch_disambiguator,
    )
    encoded = ":".join(_length_prefixed(segment) for segment in segments)
    action_id = Identifier(f"cost:{encoded}")
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

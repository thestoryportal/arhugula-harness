"""CP-to-OD response audit for model-emitted HITL tool calls.

The model tool loop is a separate PRE_ACTION gate site from the workflow-step
composer. It uses the same C-CP-16 carrier, F2 anchor, CP-to-OD converter and
stage-4 OD writer, and completes all four steps before the tool may dispatch.
"""

from __future__ import annotations

import contextlib
import hashlib
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from harness_as import GateLevel as ASGateLevel
from harness_core.identity import ActionID
from harness_cp.f5_signing_key_resolution import SigningBackend
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_placement import HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.per_step_override_evaluator import CPAuditLedgerEntry
from harness_cp.sub_agent_dispatch_cancellation import DISPATCH_CANCEL_TOKEN_VAR
from harness_cxa.cp_audit_conversion import cp_audit_to_od_audit
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import WRITER_OWNED_TIMESTAMP, EntryPayload, WriteKey
from harness_od.audit_ledger_types import SignatureAlgorithm, StateLedgerEntryRef

from harness_runtime.lifecycle.audit_offload import run_audit_off_loop
from harness_runtime.lifecycle.audit_writer import RuntimeAuditLedgerWriter
from harness_runtime.lifecycle.hitl_gate_composer import (
    compose_hitl_action_id,
    post_mutation_payload_hash,
)
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLGateDecision,
    HITLToolLoopContext,
    ModelToolCall,
)
from harness_runtime.lifecycle.state_ledger import LedgerWriter


@dataclass(frozen=True, slots=True)
class RuntimeHITLToolResponseAuditor:
    """Persist the actual operator response before model-tool dispatch."""

    ledger_writer: LedgerWriter
    audit_writer: RuntimeAuditLedgerWriter
    procedural_tier_snapshot_resolver: Callable[[], Identifier]
    tenant_id: str | None
    signing_backend: SigningBackend | None
    audit_signing_key_id: str = "harness-runtime-dev"
    audit_signing_algorithm: SignatureAlgorithm = SignatureAlgorithm.ED25519

    async def record(
        self,
        *,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        level: GateLevel,
        decision: HITLGateDecision,
    ) -> None:
        # Same cancellation/effect fence used by the workflow-step HITL audit
        # offload. No approved tool effect starts until this awaited write ends.
        token = DISPATCH_CANCEL_TOKEN_VAR.get()
        guard: contextlib.AbstractContextManager[None] = (
            token.effect_entry() if token is not None else contextlib.nullcontext()
        )
        with guard:
            await run_audit_off_loop(self._record_sync, call, context, level, decision)

    def _record_sync(
        self,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        level: GateLevel,
        decision: HITLGateDecision,
    ) -> None:
        # An operator response is an event, even if the model repeats its tool
        # call ID. The fresh token keeps successive prompts distinct while the
        # call identity remains legible in the canonical HITL action prefix.
        parent_action_id = ActionID(
            f"model-tool:{context.workflow_id}:{context.step_id}:{call.tool_call_id}"
        )
        action_id = compose_hitl_action_id(
            parent_action_id, HITLPlacementKind.PRE_ACTION, uuid.uuid4().hex
        )
        response = decision.response
        dispatched_arguments = (
            decision.edited_arguments if decision.edited_arguments is not None else call.arguments
        )
        composed_at = datetime.now(UTC)
        cp_entry = CPAuditLedgerEntry(
            action_id=action_id,
            gate_level=ASGateLevel(level.value),
            response=response.value,
            edited_proposal_hash=(
                post_mutation_payload_hash(dispatched_arguments)
                if response is HITLResponse.EDIT
                else None
            ),
            rejection_reason_hash=(
                hashlib.sha256(decision.rejection_reason.encode("utf-8")).hexdigest()
                if response is HITLResponse.REJECT and decision.rejection_reason is not None
                else None
            ),
            response_text_hash=(
                hashlib.sha256((decision.response_text or "").encode("utf-8")).hexdigest()
                if response is HITLResponse.RESPOND
                else None
            ),
            timestamp=composed_at.isoformat(),
            prior_event_hash=hashlib.sha256(b"").hexdigest(),
        )
        actor = Actor(actor_class=ActorClass.AGENT, actor_id=str(context.actor))
        self.ledger_writer.append(
            EntryPayload(
                action_id=Identifier(str(action_id)),
                idempotency_key=Identifier(str(action_id)),
                actor=actor,
                # C-IS-07 §7.6.1 / IS plan v2.10 row 15: this F2 anchor's
                # timestamp means when appended, so elect writer-owned sampling
                # inside the ledger lock. The CP audit timestamp above is the
                # separate audit-composition sample, not the F2 append instant.
                timestamp=WRITER_OWNED_TIMESTAMP,
                procedural_tier_snapshot_ref=self.procedural_tier_snapshot_resolver(),
            ),
            WriteKey(
                thread_id=Identifier(f"hitl:{parent_action_id}"),
                step_id=Identifier(str(action_id)),
                idempotency_key=Identifier(str(action_id)),
            ),
        )
        od_entry = cp_audit_to_od_audit(
            cp_entry,
            key_id=self.audit_signing_key_id,
            algo=self.audit_signing_algorithm,
            entry_core=StateLedgerEntryRef(str(action_id)),
            backend=self.signing_backend,
            tenant_id=self.tenant_id,
        )
        self.audit_writer.append(tenant_id=self.tenant_id, audit_entry=od_entry)

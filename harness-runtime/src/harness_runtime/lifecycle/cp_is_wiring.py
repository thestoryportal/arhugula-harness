"""CP → IS cross-axis wiring — stage 6 (U-RT-35, L7 §12.3, PARTIAL-LAND).

Per `Spec_Harness_Runtime_v1.md` v1.1 §12.3 (C-RT-12 CP → IS — 17 edges
across 9 CP source units): the runtime hands `ctx.ledger_writer.append`
to each CP source unit's emission site via callback registration. Source
units per spec: U-CP-12, U-CP-14, U-CP-27, U-CP-30, U-CP-34, U-CP-37,
U-CP-49, U-CP-50, U-CP-52. Spec authorizes split per the wording:
"Plan v2 U-RT-35 (split-allowed per the plan if signature divergence
surfaces at any source unit)."

**PARTIAL-LAND posture (1 of 17 edges).** Risk-gate at U-RT-35 landing
surfaced two materializability gaps + the spec's authorization to split.
This unit lands the **1 of 9 source units** that is fully materialized;
the other 8 source units (carrying the remaining 16 edges) are routed to
the Class 1 record at
`.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md`.

- U-CP-34 (`sibling_ledger_entry_composition`) — LANDED. Composer +
  IS append wrapper materialized; wired here.
- U-CP-14 (`per_step_override_evaluator`) — DEFERRED. Composer returns
  `CPAuditLedgerEntry` (placeholder timestamp / no `idempotency_key` /
  no `actor` on output); bridging at runtime would be X-AL-3 silent
  design extension.
- U-CP-12, 27, 30, 37, 49, 50, 52 — DEFERRED. No ledger-emission
  composer module at HEAD.

**Materialized seam (U-CP-34 → U-IS-11).** `sibling_ledger_entry_composition`
exports `construct_sibling_ledger_entry` (returns `EntryPayload` per
C-IS-07 §7.1 — IS computes `response_hash` + `prior_event_hash`
internally) plus `append_sibling_ledger_entry` (already wraps
`harness_is.state_ledger_write.append_ledger_entry`). The runtime
callback `emit_sibling_ledger_entry` composes via the CP surface, builds
the `WriteKey` from the structural identity fields (parent_action_id,
sibling_thread_id, step_index, tool, canonical_args), and delegates to
`ctx.ledger_writer.append`. Per-edge contract per spec §12.3 satisfied
for this one edge; the post-wiring invariant (chain_verification passes
post-emission) is verified in tests.

**Spec callable-signature drift (Class 3 weight).** Spec §12.3 declares
the wiring contract callable as `Callable[[StateLedgerEntry], EntryHash]`,
but the IS API contract is `append_ledger_entry(payload, write_key) ->
WriteResult` — caller supplies `EntryPayload` (not the fully-composed
6-field `StateLedgerEntry`) and IS computes the hash-chain fields per
C-IS-07 §7.1 acceptance #8. `EntryHash` is not a declared IS type. Same
shape as the U-RT-34 Class 3 prose drift; folded into the Class 1 record
above (Gap class C) rather than filing a separate Class 3.

**Module convention.** One module per unit.
`materialize_cp_is_wiring_stage` composer returns a frozen
`CpIsWiringStage` dataclass with `slots=True`. Typed
`CpIsWiringBindError` for bootstrap-time failures. Mirrors the L6 / L7
stage shape established at U-RT-27..34.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.hitl_as_tool_call_rewriting import (
    RewrittenToolCall,
    emit_hitl_tool_call_rewriting_state_ledger_entry,
)
from harness_cp.pause_resume_protocol import (
    PauseResumeProtocolEventKind,
    ResumeOutcome,
    emit_pause_captured_state_ledger_entry,
    emit_pause_resume_state_ledger_entry,
    emit_resume_attempted_state_ledger_entry,
)
from harness_cp.pause_resume_protocol_types import PauseSnapshot
from harness_cp.per_step_override_evaluator import emit_override_state_ledger_entry
from harness_cp.sibling_ledger_entry_composition import (
    construct_sibling_ledger_entry,
)
from harness_cp.workload_binding_engine_class_selection import (
    WorkloadBindingSelectionResult,
    emit_workload_class_selection_state_ledger_entry,
)
from harness_is.state_ledger_entry_schema import Identifier
from harness_is.state_ledger_write import (
    EntryPayload,
    WriteKey,
    WriteResult,
)

from harness_runtime.lifecycle.state_ledger import LedgerWriter
from harness_runtime.types import RuntimeConfig


class CpIsWiringBindError(Exception):
    """Raised when CP → IS wiring stage materialization fails."""


@dataclass(frozen=True, slots=True)
class RuntimeCpIsWiring:
    """Runtime CP → IS callback-registration surface (C-RT-12 §12.3, PARTIAL).

    Wraps the IS `LedgerWriter` (U-RT-12). Exposes one method per
    materialized CP source unit; at HEAD only the U-CP-34 sibling-ledger
    seam is materialized (1 of 9 source units; 1 of 17 edges per spec
    §12.3). The remaining 16 edges are tracked at the Class 1 record
    `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md`.
    """

    ledger_writer: LedgerWriter
    """IS state-ledger writer (U-RT-12) — durable substrate for CP emissions."""

    def emit_sibling_ledger_entry(
        self,
        *,
        parent_action_id: str,
        sibling_thread_id: str,
        step_index: int,
        tool: str,
        canonical_args: str,
        sibling_agent_identity: ActorIdentity,
        timestamp: datetime,
    ) -> WriteResult:
        """Compose + persist one per-sibling ledger entry via the IS chain.

        Wires the U-CP-34 → U-IS-11 seam (the 1 of 17 §12.3 edges that is
        materialized at HEAD). Returns the IS `WriteResult` — `APPENDED`
        on a fresh sibling, `IDEMPOTENT_NOOP` on a replay with the same
        `(parent_action_id, sibling_thread_id, step_index, tool,
        canonical_args)` 5-tuple per C-CP-15.1 + C-IS-07 §7.1.
        """
        payload = construct_sibling_ledger_entry(
            parent_action_id=parent_action_id,
            sibling_thread_id=sibling_thread_id,
            step_index=step_index,
            tool=tool,
            canonical_args=canonical_args,
            sibling_agent_identity=sibling_agent_identity,
            timestamp=timestamp,
        )
        write_key = WriteKey(
            thread_id=Identifier(sibling_thread_id),
            step_id=Identifier(str(step_index)),
            idempotency_key=payload.idempotency_key,
        )
        return self.ledger_writer.append(payload, write_key)

    # ------------------------------------------------------------------
    # U-RT-110 — 6 NEW §16.5 composer bindings (runtime plan v2.33).
    #
    # Each method exposes the per-composer kw-only inputs at the runtime
    # surface, constructs an async `_adapter` closure capturing
    # `(workflow_id, step_id)` for the WriteKey, and awaits the CP-axis
    # composer with `ledger_writer=_adapter`. The composer produces
    # `EntryPayload`, awaits the adapter (which sync-delegates to
    # `LedgerWriter.append`), and returns the IS `WriteResult`.
    #
    # Per CP spec v1.26 §16.5.8: the runtime wiring discipline binds the
    # ledger_writer Callable here; the inner LedgerWriter.append is sync
    # per state_ledger.py:83. The adapter MUST be `async def` to satisfy
    # the composers' `Callable[[EntryPayload], Awaitable[WriteResult]]`
    # parameter type at pyright strict.
    # ------------------------------------------------------------------

    async def emit_override_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        override_id: str,
        policy_id: str,
        post_override_step_config: Mapping[str, Any],
        actor: ActorIdentity,
    ) -> WriteResult:
        """Wire U-CP-74 emit_override_state_ledger_entry → ledger_writer.append.

        CP spec v1.26 §16.5 row U-CP-14. action_id `cp.per-step-override-application`.
        """

        async def _adapter(payload: EntryPayload) -> WriteResult:
            write_key = WriteKey(
                thread_id=Identifier(workflow_id),
                step_id=Identifier(step_id),
                idempotency_key=payload.idempotency_key,
            )
            return self.ledger_writer.append(payload, write_key)

        return await emit_override_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            override_id=override_id,
            policy_id=policy_id,
            post_override_step_config=post_override_step_config,
            actor=actor,
            ledger_writer=_adapter,
        )

    async def emit_workload_class_selection_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        selection_result: WorkloadBindingSelectionResult,
        actor: ActorIdentity,
    ) -> WriteResult:
        """Wire U-CP-75 emit_workload_class_selection_state_ledger_entry.

        CP spec v1.26 §16.5 row U-CP-27. action_id `cp.workload-binding-class-selection`.
        """

        async def _adapter(payload: EntryPayload) -> WriteResult:
            write_key = WriteKey(
                thread_id=Identifier(workflow_id),
                step_id=Identifier(step_id),
                idempotency_key=payload.idempotency_key,
            )
            return self.ledger_writer.append(payload, write_key)

        return await emit_workload_class_selection_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            selection_result=selection_result,
            actor=actor,
            ledger_writer=_adapter,
        )

    async def emit_pause_resume_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        protocol_event_kind: PauseResumeProtocolEventKind,
        event_sequence_id: int,
        protocol_state_snapshot: Mapping[str, Any],
        actor: ActorIdentity,
    ) -> WriteResult:
        """Wire U-CP-76 emit_pause_resume_state_ledger_entry (workflow-layer).

        CP spec v1.26 §16.5 row U-CP-30. action_id `cp.pause-resume-protocol`.
        """

        async def _adapter(payload: EntryPayload) -> WriteResult:
            write_key = WriteKey(
                thread_id=Identifier(workflow_id),
                step_id=Identifier(step_id),
                idempotency_key=payload.idempotency_key,
            )
            return self.ledger_writer.append(payload, write_key)

        return await emit_pause_resume_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            protocol_event_kind=protocol_event_kind,
            event_sequence_id=event_sequence_id,
            protocol_state_snapshot=protocol_state_snapshot,
            actor=actor,
            ledger_writer=_adapter,
        )

    async def emit_hitl_tool_call_rewriting_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        tool_call_id: str,
        semantic_variant_binding_id: str,
        rewritten_tool_call: RewrittenToolCall,
        actor: ActorIdentity,
    ) -> WriteResult:
        """Wire U-CP-77 emit_hitl_tool_call_rewriting_state_ledger_entry.

        CP spec v1.26 §16.5 row U-CP-37. action_id `cp.hitl-tool-call-rewriting`.
        """

        async def _adapter(payload: EntryPayload) -> WriteResult:
            write_key = WriteKey(
                thread_id=Identifier(workflow_id),
                step_id=Identifier(step_id),
                idempotency_key=payload.idempotency_key,
            )
            return self.ledger_writer.append(payload, write_key)

        return await emit_hitl_tool_call_rewriting_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            tool_call_id=tool_call_id,
            semantic_variant_binding_id=semantic_variant_binding_id,
            rewritten_tool_call=rewritten_tool_call,
            actor=actor,
            ledger_writer=_adapter,
        )

    async def emit_pause_captured_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        pause_event_id: str,
        pause_snapshot: PauseSnapshot,
        actor: ActorIdentity,
    ) -> WriteResult:
        """Wire U-CP-78 emit_pause_captured_state_ledger_entry (engine-layer).

        CP spec v1.26 §16.5 row U-CP-49. action_id `cp.pause-captured`.
        """

        async def _adapter(payload: EntryPayload) -> WriteResult:
            write_key = WriteKey(
                thread_id=Identifier(workflow_id),
                step_id=Identifier(step_id),
                idempotency_key=payload.idempotency_key,
            )
            return self.ledger_writer.append(payload, write_key)

        return await emit_pause_captured_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            pause_event_id=pause_event_id,
            pause_snapshot=pause_snapshot,
            actor=actor,
            ledger_writer=_adapter,
        )

    async def emit_resume_attempted_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        resume_event_id: str,
        resume_attempt_count: int,
        resume_outcome: ResumeOutcome,
        actor: ActorIdentity,
    ) -> WriteResult:
        """Wire U-CP-79 emit_resume_attempted_state_ledger_entry (engine-layer).

        CP spec v1.26 §16.5 row U-CP-50. action_id `cp.resume-attempted`.
        """

        async def _adapter(payload: EntryPayload) -> WriteResult:
            write_key = WriteKey(
                thread_id=Identifier(workflow_id),
                step_id=Identifier(step_id),
                idempotency_key=payload.idempotency_key,
            )
            return self.ledger_writer.append(payload, write_key)

        return await emit_resume_attempted_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            resume_event_id=resume_event_id,
            resume_attempt_count=resume_attempt_count,
            resume_outcome=resume_outcome,
            actor=actor,
            ledger_writer=_adapter,
        )


@dataclass(frozen=True, slots=True)
class CpIsWiringStage:
    """Frozen result of stage 6 CP → IS wiring materialization (PARTIAL).

    The bootstrap orchestrator (U-RT-43) binds `wiring` to the composition
    root so CP emission sites can route via the runtime callback. Mirrors
    the L6 / L7 stage shape.
    """

    wiring: RuntimeCpIsWiring


def materialize_cp_is_wiring_stage(
    config: RuntimeConfig,
    ledger_writer: LedgerWriter,
) -> CpIsWiringStage:
    """Build the stage 6 CP → IS wiring registry (PARTIAL-LAND).

    Constructed against the pre-existing IS `LedgerWriter` from stage 1
    (U-RT-12); no new IS handle is created. CP sibling-ledger entries
    share the IS hash chain per the cross-axis edge §12.3 commitment.

    `config` is read for API consistency with the L6 / L7 composers; no
    field is consumed at HEAD.
    """
    _ = config
    return CpIsWiringStage(
        wiring=RuntimeCpIsWiring(ledger_writer=ledger_writer),
    )

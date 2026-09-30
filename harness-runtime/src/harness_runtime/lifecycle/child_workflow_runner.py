"""In-process recursive child sub-workflow invocation primitive (U-RT-59 AC #7).

Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.4 (C-RT-17 contract). The
"child workflow runner" callable is injected at `RuntimeSubAgentDispatcher`
construction; the composer invokes it at §14.7.2 step 6 to re-enter
`execute_workflow_at_depth()` for the child sub-workflow body.

**v1.6 MVP composition (§14.7.4).**

- The child shares the parent's `HarnessContext` for substrate access (state
  ledger, tracer provider, audit ledger writer, retry/breaker registry,
  providers, sandbox tier dispatcher). Full child-context isolation is a
  v1.7+ scope question (CP-AL-1-adjacent boundary).
- The child's spans nest inside the current `subagent.span` via OTel context
  propagation (the runner is invoked from within the composer's
  `start_as_current_span("subagent.span")` block, so the child's
  `workflow.start` becomes a span-context child of `subagent.span`).
- The child's audit-ledger entries write to the same ledger via the same
  `ctx.audit_writer` (no separate ledger primitive at v1.6).
- The child's `RunResult` is returned verbatim to the composer.

**Sync surface (operator-ratified 2026-05-20).** Spec §14.7.4 declares the
`ChildWorkflowRunner` Protocol with `async def __call__`; operator ratified
sync end-to-end per the Stage 1 Protocol freeze at `workflow_driver.py:175`
(`StepDispatcher.dispatch` is sync; `execute_workflow_at_depth` is sync). Rolled into
the U-RT-59 Class 3 spec-prose-drift note at landing. Recursive sync re-entry
is sufficient at v1.6 MVP because the spec-pinned scope is "single-sub-agent
within linear parent" — no fan-out concurrency at the composer level.

**`default_model_binding` additive extension.** Spec §14.7.4 lists 5 kwargs
on the runner Protocol (`workflow_id`, `manifest_entry`, `steps`,
`handoff_context`, `descent`). `execute_workflow_at_depth` requires a
`default_model_binding` for the child's per-step binding resolution per
C-CP-06 §6.2; the composer forwards its parent `binding.model_binding`
(per C-CP-13 §13.3 brief-authoring inheritance MVP reading). Additive vs
spec; rolled into the same Class 3 note.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any, Protocol, cast, runtime_checkable

from harness_cp.cp_shared_types import ModelBinding
from harness_cp.handoff_context import HandoffContext
from harness_cp.hitl_placement import HITLPlacement
from harness_cp.pause_resume_protocol_types import PausedChildCapture, ResumeContext
from harness_cp.sub_agent_gate_level_descent import SubAgentGateLevelDescent
from harness_cp.workflow_driver import DriverContext as _CpDriverContext
from harness_cp.workflow_driver import execute_workflow_at_depth
from harness_cp.workflow_driver_types import (
    ChildResumeAuthority,
    ChildResumeRefusal,
    ChildResumeRefusedError,
    RunResult,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.durable_child_admission import (
    DurableChildAdmission,
    verify_durable_child_resume,
)
from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol
from harness_runtime.types import HarnessContext

__all__ = [
    "ChildWorkflowRunner",
    "compose_child_workflow_runner",
]


@runtime_checkable
class ChildWorkflowRunner(Protocol):
    """In-process recursive sub-workflow invocation surface (§14.7.4).

    Constructed at bootstrap stage 5 via `compose_child_workflow_runner(ctx)`;
    injected into `RuntimeSubAgentDispatcher.__init__`. The composer invokes
    it at §14.7.2 step 6 to run the child sub-workflow.

    Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.4 with two sync-vs-spec
    adjustments documented in the module docstring: (1) sync `__call__`
    instead of `async def __call__`; (2) additive `default_model_binding`
    kwarg.
    """

    def __call__(
        self,
        *,
        workflow_id: str,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: HandoffContext,
        descent: SubAgentGateLevelDescent,
        default_model_binding: ModelBinding,
        descent_depth: int,
        inherited_hitl_placements: tuple[HITLPlacement, ...] = (),
        child_resume: PausedChildCapture | None = None,
        child_run_id_seed: str | None = None,
        resume_context: ResumeContext | None = None,
        hitl_uniform_fallback_eligible_run_id: str | None = None,
        effect_fence_uniform_fallback_eligible_key: str | None = None,
        effect_fence_tree_wide_abort_present: bool = False,
        child_resume_authority: ChildResumeAuthority | None = None,
    ) -> RunResult:
        """Run the child sub-workflow and return its terminal `RunResult`.

        B-104 Task 4a: `descent_depth` (required, never defaulted) is the CHILD's own depth
        — its parent's depth + 1 — so the recursive `execute_workflow_at_depth` records a true
        ancestry (child 1, grandchild 2) with each pause it captures.

        B-HIERARCHICAL-PAUSE (R-FS-1): `child_resume` (additive, default
        `None`) — when the parent fan-out is RESUMING a previously-paused child, its
        capture (the child's own `PauseSnapshot` plus, under a durable protocol, the exact
        journal ref of its record) is threaded here so the child re-enters at its
        cursor (`execute_workflow_at_depth(pause_snapshot_input=...)`) rather than re-running
        from scratch. `None` on a first (non-resume) child dispatch → byte-identical
        to the pre-arc behavior.

        B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT (R-FS-1): `child_run_id_seed`
        (additive, default `None`) — a DETERMINISTIC first-dispatch child run_id
        (vs the legacy fresh `uuid`). The composer derives it from the spawning
        SUB_AGENT_DISPATCH worker's stable, recoverable per-branch idempotency key
        (`step_context.parent_idempotency_key`) + `child_workflow_id`, so it
        RE-DERIVES IDENTICALLY when the parent fan-out re-dispatches a maybe-ran
        SUB_AGENT_DISPATCH worker on crash-resume. That makes the child's durable
        store + effect-fence reserves RECOVERABLE under a stable key — a plain
        re-dispatch (no `pause_snapshot_input`) re-enters the child, whose OWN
        crash-resume auto-resumes from the shared durable store (at-most-once is
        compositional: it bottoms out at the child's recursively-classified steps).
        The composer passes it ONLY when the child is recoverable
        (`subagent_child_recoverable` — `{ESR,WAL}` ∧ LINEAR ∧ leaf); a
        non-recoverable child gets `None` → legacy fresh-`uuid` (no auto-resume,
        pre-existing behavior — no suffix-only-reconstruction corruption). Ignored
        on a resume (`pause_snapshot_input` non-None reuses the snapshot's run_id).

        B-39 impl leg Slice B (CP spec v1.106 §1): `resume_context` (additive,
        default `None`) — the operator's full resume payload, forwarded verbatim
        into the recursive `execute_workflow_at_depth(resume_context=...)` call so the
        child's OWN reconstruction can resolve its own effect-fence directive +
        per-branch HITL delivery cell (replacing the retired ctx-level, run-tree-
        wide-shared `ResumeContextHolder` singleton). `None` on a first (non-resume)
        child dispatch → byte-identical to pre-arc.

        B-39 impl leg Slice B, codex round-2 [P1] fix (CP spec v1.106 §1.2
        property 4): `hitl_uniform_fallback_eligible_run_id` (additive, default
        `None`) — the SOLE gate-owning branch's `run_id` (if any) the uniform
        `hitl_response` fallback may resolve this resume cycle, computed ONCE at
        the true depth-0 root (`mcp_server.py`, BEFORE any recursion narrows the
        snapshot to a subtree) and forwarded verbatim, exactly like
        `resume_context`, NEVER recomputed at this recursion level (a child's own
        `pause_snapshot_input` cannot see sibling branches paused elsewhere in the
        tree). `None` on a first (non-resume) child dispatch → byte-identical to
        pre-arc.

        B-70 impl leg (CP spec v1.107 §1.1): `effect_fence_uniform_fallback_
        eligible_key` (additive, default `None`) — the effect-fence analogue of
        `hitl_uniform_fallback_eligible_run_id` immediately above: the SOLE
        unaddressed effect-fence-pause location's `idempotency_key` (if any) the
        uniform `effect_fence_resolution` fallback may resolve this resume cycle,
        computed ONCE at the true depth-0 root and forwarded verbatim, NEVER
        recomputed at this recursion level. `None` on a first (non-resume) child
        dispatch → byte-identical to pre-arc.

        B-80 impl leg (CP spec v1.111 §2 property 8): `effect_fence_tree_wide_
        abort_present` (additive, default `False`) — the THIRD sibling of
        `hitl_uniform_fallback_eligible_run_id` / `effect_fence_uniform_fallback_
        eligible_key` immediately above: whether ANY location in the FULL resume
        tree resolves to an effect-fence `ABORT` this resume cycle, computed ONCE
        at the true depth-0 root and forwarded verbatim, NEVER recomputed at this
        recursion level. `False` on a first (non-resume) child dispatch →
        byte-identical to pre-arc. This is the SAME CP→Runtime→CP crossing its two
        siblings already use — no NEW seam is introduced.

        B-104 Task 5b-1: `child_resume_authority` (additive, default `None`) — the
        Runtime's permission to run a durable paused child, read off the CP step context beside
        `child_resume`. It is used only when it is exactly a `ClaimedChildAdmission`; anything
        else keeps the injected `durable_admission` binding.
        """
        ...


def compose_child_workflow_runner(
    ctx: HarnessContext, *, durable_admission: DurableChildAdmission
) -> ChildWorkflowRunner:
    """Build a `ChildWorkflowRunner` closing over the parent `HarnessContext`.

    Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.4 "Composer module residence":
    bootstrap stage 5 calls this factory + injects the result into
    `RuntimeSubAgentDispatcher` construction.

    The returned callable re-enters `execute_workflow_at_depth()` (the same C-CP-25
    §25.3 driver loop the top-level workflow uses per C-RT-08). Child shares
    parent `HarnessContext` per v1.6 MVP — substrate access (state ledger,
    audit writer, tracer provider, retry/breaker registry, providers,
    sandbox tier dispatcher) flows through `ctx` unchanged.

    The child's `step_dispatchers` is the parent's `ctx.step_dispatchers`
    registry — recursive `SUB_AGENT_DISPATCH` steps in the child route
    through the same composer (unbounded stack depth at v1.6 MVP; bounded
    by the operator-authored workflow shape).

    Parameters
    ----------
    ctx
        The parent `HarnessContext`. The runner closes over this context;
        `ctx.step_dispatchers` must be populated (which it is post stage 5
        per the bootstrap orchestrator's stage ordering).
    durable_admission
        B-104 Task 4c — REQUIRED, no default. Under a durable pause protocol a resumed
        paused child is verified against its exact journal record and then passed to this
        step before any of its steps run; the step either admits it or raises
        `ChildResumeRefusedError`. Every caller must state its binding: stage 5 binds the
        always-refusing `RefuseDurableChildAdmission` until Task 5's claim/started gateway.
        Not consulted for a first dispatch or an ephemeral protocol.
    """

    def _runner(
        *,
        workflow_id: str,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: HandoffContext,
        descent: SubAgentGateLevelDescent,
        default_model_binding: ModelBinding,
        descent_depth: int,
        inherited_hitl_placements: tuple[HITLPlacement, ...] = (),
        child_resume: PausedChildCapture | None = None,
        child_run_id_seed: str | None = None,
        resume_context: ResumeContext | None = None,
        hitl_uniform_fallback_eligible_run_id: str | None = None,
        effect_fence_uniform_fallback_eligible_key: str | None = None,
        effect_fence_tree_wide_abort_present: bool = False,
        child_resume_authority: ChildResumeAuthority | None = None,
    ) -> RunResult:
        # B-HIERARCHICAL-PAUSE — on a RESUME (pause_snapshot_input non-None), FAIL CLOSED
        # if the snapshot's workflow_id does not match the child being invoked (Codex
        # [P2], mirroring the root `api.resume` workflow-id guard): if the parent is
        # edited between pause + resume so the same SUB_AGENT_DISPATCH step_id points to
        # a DIFFERENT child workflow, the parent resume guard still passes, and applying
        # the old child's cursor/run_id to the new child would silently corrupt lineage.
        pause_snapshot_input = child_resume.child_snapshot if child_resume is not None else None
        if pause_snapshot_input is not None and pause_snapshot_input.workflow_id != workflow_id:
            # A typed refusal, not a generic ValueError: a legacy carrier with no recorded
            # child_workflow_id skips CP's identity guard, and a generic failure here would
            # let the pause cascade drop the child's cursor and dispatch it fresh.
            raise ChildResumeRefusedError(
                ChildResumeRefusal.WORKFLOW_MISMATCH,
                "child resume workflow-id mismatch: snapshot.workflow_id="
                f"{pause_snapshot_input.workflow_id!r}, resume child workflow_id="
                f"{workflow_id!r} (the paused child's snapshot cannot resume a different "
                "child workflow)",
            )

        def _execute(own_authority: ClaimedChildAdmission | None) -> RunResult:
            # Reuse the paused child's ORIGINAL run_id (not a fresh uuid) so the resumed
            # child's run/step idempotency keys + ledger/audit lineage stay coherent with
            # the original run — the same discipline the root resume path follows
            # (it threads `snapshot.run_id`). A fresh id on resume would re-key the child's
            # per-step idempotency + sever its run lineage (Codex [P2]).
            #
            # B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT (R-FS-1) — on a FIRST dispatch
            # (no `pause_snapshot_input`), prefer the composer-supplied DETERMINISTIC
            # `child_run_id_seed` over a fresh `uuid`. The seed is derived from the
            # spawning worker's stable, recoverable per-branch idempotency key, so a
            # parent-crash re-dispatch of a maybe-ran SUB_AGENT_DISPATCH worker
            # RE-DERIVES the SAME child run_id → the child's durable store + effect-fence
            # reserves are recoverable → the child's own crash-resume auto-resumes
            # (at-most-once compositional). The composer passes a seed ONLY for a
            # recoverable child (`{ESR,WAL}` ∧ LINEAR ∧ leaf); a non-recoverable child
            # gets `None` → legacy fresh-`uuid` (byte-identical to pre-arc; no auto-resume
            # so no suffix-only-reconstruction corruption).
            child_run_id = (
                pause_snapshot_input.run_id
                if pause_snapshot_input is not None
                else child_run_id_seed
                if child_run_id_seed is not None
                else uuid.uuid4().hex
            )
            # The CP driver consumes `ctx` via its structural `DriverContext`
            # Protocol (subset of HarnessContext). Cast for the type layer; the
            # runtime objects satisfy both Protocols — same pattern as
            # `harness_runtime.api.run` per the existing api.py:386 invocation.
            #
            # B-HIERARCHICAL-PAUSE — forward the child's resume snapshot (None on a
            # first dispatch) so a resumed child re-enters at its own cursor.
            #
            # B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT (R-FS-1) — opt the child run into
            # final_state reconstruction: on a durable-engine-class (EVENT_SOURCED_REPLAY /
            # WAL_SEGMENT) child resume over a committed prefix, the CP driver returns a
            # suffix-only `final_state` (the loop starts at `resume_at` with `accumulated`
            # empty); the parent fold (`sub_agent_dispatch` SUCCESS → `step_output =
            # child_result.final_state`; the B-HIERARCHICAL-PAUSE re-enter fold) would
            # otherwise consume that truncated state and silently corrupt the parent
            # aggregate. The opt-in seeds the committed prefix from the durable output store
            # so the child's `final_state` reconstructs the COMPLETE terminal state. ALL FOUR
            # durable resumable engine classes reconstruct (the EngineOutputStore is
            # class-agnostic: ESR/WAL #766, SAVE_POINT_CHECKPOINT v1.79 #779, RECONCILER_LOOP
            # v1.80 #781); only PURE_PATTERN_NO_ENGINE (non-durable) degrades to suffix-only.
            # A first (non-resume) dispatch is unaffected.
            # Top-level runs (`harness_runtime.api.run`) do NOT pass this → their accepted
            # suffix-only resume semantic is untouched (the fork-bearing top-level
            # reconstruction is a separate registered arc).
            return execute_workflow_at_depth(
                manifest_entry,
                steps,
                child_run_id,
                cast(_CpDriverContext, ctx),
                default_model_binding=default_model_binding,
                step_dispatchers=cast(Any, ctx.step_dispatchers),
                inherited_hitl_placements=inherited_hitl_placements,
                pause_snapshot_input=pause_snapshot_input,
                resume_context=resume_context,
                hitl_uniform_fallback_eligible_run_id=hitl_uniform_fallback_eligible_run_id,
                effect_fence_uniform_fallback_eligible_key=effect_fence_uniform_fallback_eligible_key,
                effect_fence_tree_wide_abort_present=effect_fence_tree_wide_abort_present,
                reconstruct_final_state=True,
                # U-1 slice 3a (B-18) — mark the child run as a DESCENDED sub-agent so
                # every child `StepExecutionContext` reports `sub_agent_descent` (derived
                # from `descent_depth > 0`); a child INFERENCE step then emits the downgraded
                # (external-irreversible-REMOVE'd) frozen_tool_superset per ADR-D4 §1.5,
                # closing the F1 latent C10 condition-2 gap. B-104 Task 4a: the depth is the
                # dispatcher-supplied parent depth + 1, so a grandchild re-enters here at 2.
                descent_depth=descent_depth,
                # [LAW:single-enforcer] CP clamps the child manifest to this recorded descent.
                parent_gate_floor=descent.child_gate_level,
                # B-104 Task 5b-1 — the child's OWN authority (never this dispatch's), so its
                # grandchildren claim through the child's started claim, not the root's.
                child_resume_authority=own_authority,
            )

        # B-104 Task 4c — under a DURABLE protocol a resumed paused child must be the exact
        # journal record its parent carried (verified by position and digest, full snapshot
        # equality and depth), and must then pass the required admission step, BEFORE
        # anything of it executes. Both refuse with `ChildResumeRefusedError`. An ephemeral
        # protocol has no journal record and keeps its existing behavior.
        # [LAW:single-enforcer] This is the only path from a resume capture to
        # `execute_workflow_at_depth`.
        if child_resume is not None and isinstance(
            ctx.pause_resume_protocol, DurablePauseResumeProtocol
        ):
            # [LAW:no-ambient-temporal-coupling] The admission decides WHEN the body runs; a
            # gateway may put a claim and a durable `started` frame before it.
            verified = verify_durable_child_resume(
                ctx.pause_resume_protocol, child_resume, descent_depth=descent_depth
            )
            # [LAW:single-enforcer] Only the exact Runtime type is honored; a fake or absent
            # authority keeps the injected binding (stage 5's always-refusing one).
            if type(child_resume_authority) is ClaimedChildAdmission:
                return child_resume_authority.run_with_child_authority(verified, _execute)
            return durable_admission.run_admitted(verified, lambda: _execute(None))
        return _execute(None)

    return _runner

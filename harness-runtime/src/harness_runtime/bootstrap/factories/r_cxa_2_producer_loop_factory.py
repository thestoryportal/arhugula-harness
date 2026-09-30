"""Stage-5 factory for R-CXA-2 CP->IS producer loops.

Materializes the model-driven HITL tool-loop primitive and the engine recovery
loop primitive against the CP->IS wiring that stage 3b has already bound.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, NoReturn, cast

from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_cp.cp_shared_types import ActorIdentity, MCPTrustTier, ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel, GateLevelInput, gate_level, max_gate_level
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.config.state_placement import StateKind, resolve_state_path
from harness_runtime.lifecycle.cp_is_wiring import RuntimeCpIsWiring
from harness_runtime.lifecycle.engine_recovery_loop import RuntimeEngineRecoveryLoop
from harness_runtime.lifecycle.hitl_placement import RuntimeHITLPlacementRegistry
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLGateDecision,
    HITLToolCallAssessment,
    HITLToolLoopContext,
    ModelToolCall,
    RuntimeHITLToolLoop,
    model_tool_call_step,
)
from harness_runtime.lifecycle.hitl_tool_response_audit import RuntimeHITLToolResponseAuditor
from harness_runtime.lifecycle.reconciler_pause_resume_substrate import (
    ReconcilerEnginePauseResumeSubstrate,
)
from harness_runtime.lifecycle.step_blast_radius import resolve_step_blast_radius
from harness_runtime.lifecycle.step_mcp_trust_tier import resolve_tool_owner
from harness_runtime.lifecycle.tool_search import (
    SEARCH_TOOLS_TOOL_NAME,
    compute_deferred_tool_index,
    dispatch_search_tools,
)
from harness_runtime.lifecycle.wal_segment_pause_resume_substrate import (
    WALSegmentEnginePauseResumeSubstrate,
)
from harness_runtime.types import RuntimeConfig, ToolName

__all__ = [
    "IN_PROCESS_TOOL_OWNER",
    "R_CXA_2_MODEL_TOOL_LOOP_PARENT_GATE_LEVEL",
    "UNREGISTERED_TOOL_OWNER",
    "RCXA2ProducerLoopMaterializeError",
    "RCXA2ProducerLoopStage",
    "materialize_r_cxa_2_producer_loop_stage",
]


R_CXA_2_MODEL_TOOL_LOOP_PARENT_GATE_LEVEL = GateLevel.AUTO
"""Synthetic TOOL_STEP parent gate used by the model-tool-call adapter.

The HITL decision has already fired in ``RuntimeHITLToolLoop`` before this
adapter dispatches an approved call. The wrapped C-RT-19 dispatcher does not
consume this field at HEAD; keeping it at AUTO avoids double-counting a gate
level at the synthetic tool-step bridge.
"""


class RCXA2ProducerLoopMaterializeError(Exception):
    """Stage-5 materialization failed for the R-CXA-2 producer loop bindings."""


@dataclass(frozen=True, slots=True)
class RCXA2ProducerLoopStage:
    """Frozen stage-5 result carrying the two R-CXA-2 runtime producers."""

    hitl_tool_loop: RuntimeHITLToolLoop
    engine_recovery_loop: RuntimeEngineRecoveryLoop


_HOST_LESS_SEARCH_TOOLS_TRUST = MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT
"""`search_tools` is answered in process with no owning MCP host, so it takes the same
host-less no-floor default the composer's host-less gate sites use (U-RT-131)."""

IN_PROCESS_TOOL_OWNER = "<in-process>"
"""Owner of `search_tools`: answered in this process, never by an MCP host."""

UNREGISTERED_TOOL_OWNER = "<unregistered>"
"""Owner of a tool no configured host registers: it computes DENY and cannot dispatch.
Angle brackets keep both labels out of the configured server-name space."""


@dataclass(frozen=True, slots=True)
class _HostTrustGateLevelEvaluator:
    """Assess a model-emitted tool call from its owning host's REAL trust and blast.

    One `resolve_tool_owner` lookup (the scan behind the tool-step composer's trust tier,
    keyed like the dispatcher's routing index) gives both the trust and the owner name, so
    the host that is scored is the host that is named and dispatched to; the model-supplied
    `server` label is never consulted. Blast comes from `resolve_step_blast_radius` over the
    shared synthetic `TOOL_STEP`. A tool no configured host registers, or whose host
    declares no trust, has no trust to stand on and computes DENY (fail closed; an
    unregistered tool could not dispatch anyway). A lookup that raises propagates: the loop
    turns it into a typed no-prompt refusal.
    """

    lookup_ctx: Any
    """Bootstrap context read for `mcp_client_hosts` when each call is evaluated."""

    def __call__(self, call: ModelToolCall, context: HITLToolLoopContext) -> HITLToolCallAssessment:
        if call.tool == SEARCH_TOOLS_TOOL_NAME:
            owner = IN_PROCESS_TOOL_OWNER
            trust: MCPTrustTier | None = _HOST_LESS_SEARCH_TOOLS_TRUST
            blast = BlastRadiusTier.READ_ONLY  # a pure in-process index read, no effect
        else:
            resolved = resolve_tool_owner(call.tool, self.lookup_ctx)
            if resolved is None:
                return HITLToolCallAssessment(GateLevel.DENY, UNREGISTERED_TOOL_OWNER)
            owner, trust = resolved.server_name, resolved.trust_tier
            if trust is None:
                return HITLToolCallAssessment(GateLevel.DENY, owner)
            blast = resolve_step_blast_radius(model_tool_call_step(call, context), self.lookup_ctx)
        computed = gate_level(
            GateLevelInput(
                per_tool_gate_level=GateLevel.AUTO,
                persona_tier=context.persona_tier,
                blast_radius_tier=blast,
                mcp_trust_tier=trust,
            )
        ).computed_gate_level
        # [LAW:single-enforcer] The descended-step parent floor folds in here, once.
        return HITLToolCallAssessment(max_gate_level(computed, context.inherited_gate_floor), owner)


@dataclass(frozen=True, slots=True)
class _AskUserQuestionGateAdapter:
    """Adapt the stage-5 ask-user surface to the model tool-loop gate protocol."""

    ask_user_question_surface: Any
    timeout_seconds: float | None = None

    async def decide(
        self,
        *,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        palette: frozenset[HITLResponse],
    ) -> HITLGateDecision:
        _ = context
        result = await self.ask_user_question_surface.ask(
            prompt=f"HITL tool call {call.tool} on {call.server}",
            options=tuple(sorted(palette)),
            timeout=self.timeout_seconds,
        )
        edited_arguments = None
        if result.response is HITLResponse.EDIT and isinstance(result.edited_proposal, str):
            try:
                edited_arguments = _parse_edited_arguments(result.edited_proposal)
            except ValueError:
                # The loop admits EDIT only with a decoded argument object. Preserve
                # a malformed reply for its typed refusal; never dispatch originals.
                pass
        return HITLGateDecision(
            response=result.response,
            edited_arguments=edited_arguments,
            response_text=result.response_text,
            rejection_reason=result.rejection_reason,
        )


@dataclass(frozen=True, slots=True)
class _RuntimeToolDispatcherModelCallAdapter:
    """Project approved model tool calls onto the existing C-RT-19 dispatcher.

    ``deferred_tool_index`` — B-TOOL-SEARCH-RUNTIME (AS spec v1.13 §13.7): the
    schemas of MCP tools omitted from the eager ``tools[]`` union at this
    run's ``compute_frozen_tool_superset(..., defer_names=...)`` call (stage
    5, ``stage_5_loop_init.py``). A model call to ``search_tools`` is
    intercepted HERE — before it ever reaches ``self.tool_dispatcher`` — and
    answered directly from this index, since ``search_tools`` is an
    in-process pure computation with no owning MCP host/server and thus no
    real trust/sandbox/cost semantics for the wrapped C-RT-19 dispatcher to
    evaluate. Default ``{}`` (empty) is byte-behavior-identical to pre-v1.13:
    no operator-facing policy for populating ``defer_names`` exists yet (AS
    spec §13.7 explicitly leaves that to implementation discretion), so this
    stays empty in production until such a policy is built — MUST be kept in
    sync with whatever ``defer_names``/``remove_tiers`` a future policy
    threads into the paired ``compute_frozen_tool_superset`` call(s).
    """

    tool_dispatcher: Any
    tenant_id: str | None
    deferred_tool_index: Mapping[str, Mapping[str, Any]] = field(
        default_factory=lambda: cast("dict[str, Mapping[str, Any]]", {})
    )

    async def dispatch(
        self,
        call: ModelToolCall,
        context: HITLToolLoopContext,
    ) -> Mapping[str, Any]:
        if call.tool == SEARCH_TOOLS_TOOL_NAME:
            return self._dispatch_search_tools(call)
        step = model_tool_call_step(call, context)
        synthetic_step_id = str(step.step_id)
        binding = StepEffectiveBinding(
            step_id=synthetic_step_id,
            model_binding=ModelBinding(provider=call.provider, model=call.model),
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            override_applied=False,
            persona_tier=context.persona_tier,
        )
        step_context = StepExecutionContext(
            workflow_id=context.workflow_id,
            parent_action_id=f"workflow:{context.workflow_id}:step:{context.step_id}",
            parent_gate_level=R_CXA_2_MODEL_TOOL_LOOP_PARENT_GATE_LEVEL,
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=Actor(
                actor_class=ActorClass.AGENT,
                actor_id=str(context.actor),
            ),
            parent_entry_hash="",
            parent_idempotency_key=(
                f"model-tool:{context.workflow_id}:{context.step_id}:{call.tool_call_id}"
            ),
            tenant_id=self.tenant_id,
            step_index=0,
        )
        return await self.tool_dispatcher.dispatch(
            binding,
            step,
            step_context=step_context,
        )

    def _dispatch_search_tools(self, call: ModelToolCall) -> Mapping[str, Any]:
        """Answer a ``search_tools`` model call directly from ``deferred_tool_index``.

        Bypasses ``self.tool_dispatcher`` entirely (§13.7 point 3 — an
        in-process pure computation, never an MCP-hosted effect). Response
        shape mirrors the wrapped dispatcher's ``Mapping[str, Any]`` contract
        (``tool_id`` / ``response`` / ``idempotency_key`` /
        ``trust_decision_reason`` / ``sandbox_tier``) so the unchanged
        downstream ``tool_result``-block construction (which JSON-serializes
        the whole mapping) keeps working without special-casing there.
        """
        query = call.arguments.get("query", "")
        matches = dispatch_search_tools(str(query), self.deferred_tool_index)
        return {
            "tool_id": call.tool,
            "response": {"matches": [dict(m) for m in matches]},
            "idempotency_key": f"search-tools:{call.tool_call_id}",
            "trust_decision_reason": "synthetic-in-process-no-trust-gate",
            "sandbox_tier": SandboxTier.TIER_1_PROCESS.value,
        }


def materialize_r_cxa_2_producer_loop_stage(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    *,
    defer_names: frozenset[ToolName] = frozenset(),
) -> RCXA2ProducerLoopStage:
    """Bind R-CXA-2 producer loops at stage 5 LOOP_INIT.

    ``defer_names`` — B-TOOL-SEARCH-RUNTIME (AS spec v1.13 §13.7): MUST match
    the ``defer_names`` the caller passes to the paired top-level
    ``compute_frozen_tool_superset(ctx.mcp_client_hosts, ..., defer_names=...)``
    call in ``stage_5_loop_init.py`` (this factory runs BEFORE that call at
    stage 5, so it independently recomputes the deferred index from the SAME
    ``ctx.mcp_client_hosts`` rather than accepting a pre-built mapping that
    could silently drift out of sync). Default ``frozenset()`` → empty index
    → byte-identical to pre-v1.13 (no operator-facing policy for populating
    ``defer_names`` exists yet; AS spec §13.7 explicitly leaves that to
    implementation discretion).
    """
    if "cp_is_wiring" not in ctx.cxa_stages:
        raise RCXA2ProducerLoopMaterializeError(
            "ctx.cxa_stages['cp_is_wiring'] missing at stage 5; stage 3b "
            "must materialize CP->IS wiring before R-CXA-2 producer loops"
        )
    if ctx.hitl_registry is None:
        raise RCXA2ProducerLoopMaterializeError(
            "ctx.hitl_registry is None at stage 5; stage 3b must populate HITL placement"
        )
    if ctx.ask_user_question_surface is None:
        raise RCXA2ProducerLoopMaterializeError(
            "ctx.ask_user_question_surface is None at stage 5; HITL gate adapter "
            "requires the stage-5 ask-user surface"
        )
    if ctx.tool_dispatcher is None:
        raise RCXA2ProducerLoopMaterializeError(
            "ctx.tool_dispatcher is None at stage 5; model tool calls dispatch "
            "through the existing C-RT-19 tool dispatcher"
        )

    if ctx.audit_writer is None:
        raise RCXA2ProducerLoopMaterializeError(
            "ctx.audit_writer is None at stage 5; stage 4 OD must bind the audit writer"
        )

    wiring = cast(RuntimeCpIsWiring, ctx.cxa_stages["cp_is_wiring"].wiring)
    placement_registry = cast(RuntimeHITLPlacementRegistry, ctx.hitl_registry)
    actor = _actor_identity_from_context(ctx)

    hitl_tool_loop = RuntimeHITLToolLoop(
        wiring=wiring,
        placement_registry=placement_registry,
        assess=_HostTrustGateLevelEvaluator(ctx),
        gate=_AskUserQuestionGateAdapter(ctx.ask_user_question_surface),
        response_auditor=RuntimeHITLToolResponseAuditor(
            ledger_writer=wiring.ledger_writer,
            audit_writer=cast(Any, ctx.audit_writer),
            procedural_tier_snapshot_resolver=wiring.procedural_tier_snapshot_resolver,
            tenant_id=config.tenant_id,
            signing_backend=ctx.audit_signing_backend,
        ),
        dispatcher=_RuntimeToolDispatcherModelCallAdapter(
            tool_dispatcher=ctx.tool_dispatcher,
            tenant_id=config.tenant_id,
            deferred_tool_index=compute_deferred_tool_index(ctx.mcp_client_hosts, defer_names),
        ),
    )
    # U-RT-124 (R-FS-1 E-impl-3c) — R-CXA-2 engine-layer activation, engine-class-aware.
    # The engine recovery loop binds ONE durable substrate per engine class that
    # fires it (O-RT-4): WAL_SEGMENT → the U-RT-121 WAL segment-log substrate
    # (U-RT-122, E-impl-2); RECONCILER_LOOP → the U-RT-123 etcd-style reconciler
    # substrate (E-impl-3b). Each firing call passes the workflow's `engine_class`
    # (the U-CP-95 WAL + U-CP-97 reconciler driver branches are already gated on
    # it), so `ctx.engine_recovery_loop.capture_pause`/`.attempt_resume` persist
    # `cp.pause-captured` / `cp.resume-attempted` against the engine class's OWN
    # crash-survivable store — bringing the R-CXA-2 CP→IS engine-layer seam LIVE in
    # production for BOTH durable engine classes. The per-engine-class map is the
    # single source of routing truth: DISTINCT journal directories mean a reconciler
    # pause can never land in the WAL segment-log, nor a WAL pause in the reconciler
    # store (the U-RT-124 no-cross-contamination AC, enforced by construction). Each
    # store lives under the operator's repository_root (no new RuntimeConfig field;
    # §7.4 substrate-location impl-discretion) and is created lazily on first capture.
    # Non-firing engine classes (the 3 non-DURABLE_ASYNC classes) never invoke the
    # loop (the driver gates on engine_class), so no files are written for them.
    engine_recovery_loop = RuntimeEngineRecoveryLoop(
        wiring=wiring,
        substrate_by_engine_class={
            EngineClass.WAL_SEGMENT: WALSegmentEnginePauseResumeSubstrate(
                journal_dir=resolve_state_path(
                    StateKind.ENGINE_RECOVERY_SEGMENTS, config, ctx.verified_state_root
                ),
                state_summary_provider=_default_engine_state_summary,
            ),
            EngineClass.RECONCILER_LOOP: ReconcilerEnginePauseResumeSubstrate(
                journal_dir=resolve_state_path(
                    StateKind.ENGINE_RECOVERY_RECONCILER, config, ctx.verified_state_root
                ),
                state_summary_provider=_default_engine_state_summary,
            ),
        },
        actor=actor,
    )
    ctx.hitl_tool_loop = hitl_tool_loop
    ctx.engine_recovery_loop = engine_recovery_loop
    return RCXA2ProducerLoopStage(
        hitl_tool_loop=hitl_tool_loop,
        engine_recovery_loop=engine_recovery_loop,
    )


def _actor_identity_from_context(ctx: _MutableHarnessContext) -> ActorIdentity:
    actor = getattr(ctx.ledger_writer, "actor", None)
    actor_id = getattr(actor, "actor_id", "harness-runtime")
    return ActorIdentity(str(actor_id))


def _default_engine_state_summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier("r-cxa-2-engine-state"),
        external_references=(),
    )


def _reject_nonfinite_edit_constant(constant: str) -> NoReturn:
    raise ValueError(f"non-finite JSON constant {constant!r} in HITL EDIT response")


def _parse_edited_arguments(edited_proposal: str) -> Mapping[str, Any]:
    parsed = json.loads(edited_proposal, parse_constant=_reject_nonfinite_edit_constant)
    if not isinstance(parsed, dict):
        raise ValueError("HITL EDIT response must be a JSON object of tool arguments")
    return cast(Mapping[str, Any], parsed)

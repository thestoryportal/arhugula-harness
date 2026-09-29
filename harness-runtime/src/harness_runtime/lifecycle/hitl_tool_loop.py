"""Runtime model-driven HITL tool-loop producer for R-CXA-2.

Authority: C-CP-17 HITL placement / tool-call rewriting and U-CP-77
`cp.hitl-tool-call-rewriting`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any, Protocol, cast

from harness_core import PersonaTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.gate_level_rule import GateLevel
from harness_cp.handoff_context import ActionKind, ProposedAction
from harness_cp.hitl_as_tool_call_rewriting import RewrittenToolCall
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.persona_engine_hitl_matrix import SynchronyClass
from harness_cp.validator_fail_transient_staircase import CrossTrustBoundaryState
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_is.state_ledger_write import WriteResult

from harness_runtime.lifecycle.cp_is_wiring import RuntimeCpIsWiring
from harness_runtime.lifecycle.effective_palette import compute_effective_palette
from harness_runtime.lifecycle.hitl_placement import RuntimeHITLPlacementRegistry


@dataclass(frozen=True, slots=True)
class ModelToolCall:
    """Provider-neutral model-emitted tool call."""

    tool_call_id: str
    tool: str
    server: str
    arguments: Mapping[str, Any]
    provider: str
    model: str


@dataclass(frozen=True, slots=True)
class HITLToolLoopContext:
    """Stable workflow and HITL placement context for one model tool turn."""

    workflow_id: str
    step_id: str
    persona_tier: PersonaTier
    cell_synchrony_class: SynchronyClass
    cross_trust_boundary_state: CrossTrustBoundaryState
    actor: ActorIdentity
    inherited_gate_floor: GateLevel
    """The parent's C-CP-12 gate floor for a descended (child) step, else `AUTO`. The
    caller states it explicitly so a forgotten floor is a type error, not a silent root."""


def model_tool_call_step(call: ModelToolCall, context: HITLToolLoopContext) -> WorkflowStep:
    """The synthetic `TOOL_STEP` for a model tool call.

    [LAW:single-enforcer] The one place tool identity is projected onto a step: the gate
    evaluator (trust and blast lookups) and the dispatcher both take this, so they cannot
    disagree about which tool a call names.
    """
    return WorkflowStep(
        step_id=StepID(f"{context.step_id}:tool:{call.tool_call_id}"),
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": call.tool, "tool_args": dict(call.arguments)},
    )


@dataclass(frozen=True, slots=True)
class HITLGateDecision:
    """Gate outcome consumed by the tool loop before dispatch."""

    response: HITLResponse
    edited_arguments: Mapping[str, Any] | None = None
    response_text: str | None = None
    rejection_reason: str | None = None


class HITLToolRefusalReason(StrEnum):
    """Why a model tool call was refused without dispatch under policy."""

    POLICY_DENY = "policy-deny"
    """The computed gate level is DENY (C-CP-19 §19.4): the operator was asked with only
    REJECT/RESPOND and no response dispatches."""
    RESPONSE_OUTSIDE_PALETTE = "response-outside-palette"
    """The adapter answered with a response the offered palette does not allow."""
    MALFORMED_GATE_REPLY = "malformed-gate-reply"
    """The adapter returned something that is not a `HITLGateDecision`."""
    EVALUATOR_FAILED = "evaluator-failed"
    """The gate level could not be computed: refused without prompting."""
    MALFORMED_GATE_LEVEL = "malformed-gate-level"
    """The evaluator returned something that is not a `HITLToolCallAssessment` with a real
    `GateLevel` and a named owner: refused without prompting."""


@dataclass(frozen=True, slots=True)
class HITLToolRefusal:
    """A typed refusal the model receives as an `is_error` tool result."""

    reason: HITLToolRefusalReason
    response_text: str | None = None
    """The operator's RESPOND text, preserved for the model when they gave one."""


@dataclass(frozen=True, slots=True)
class HITLToolLoopCallResult:
    """Per-tool-call loop result."""

    tool_call_id: str
    rewritten_tool_call: RewrittenToolCall | None
    """`None` only when the gate level could not be computed (no rewrite ran)."""
    rewrite_write_result: WriteResult | None
    gate_response: HITLResponse | None
    dispatched: bool
    dispatch_result: Mapping[str, Any] | None
    refusal: HITLToolRefusal | None = None


class HITLToolResponseAuditor(Protocol):
    """Persist one admitted operator reply before its disposition or tool effect."""

    async def record(
        self,
        *,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        level: GateLevel,
        decision: HITLGateDecision,
    ) -> None: ...


class HITLToolDispatcher(Protocol):
    """Dispatch surface for an approved model tool call."""

    async def dispatch(
        self,
        call: ModelToolCall,
        context: HITLToolLoopContext,
    ) -> Mapping[str, Any]: ...


class HITLGateAdapter(Protocol):
    """Gate surface opened after a rewrite and before tool dispatch."""

    async def decide(
        self,
        *,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        palette: frozenset[HITLResponse],
    ) -> HITLGateDecision: ...


@dataclass(frozen=True, slots=True)
class HITLToolCallAssessment:
    """The evaluator's verdict on one model tool call, from one owner lookup."""

    level: GateLevel
    owner: str
    """The host the call dispatches to, as resolved from the registry that also gave
    `level` — never the model-supplied `ModelToolCall.server` label. The operator is asked,
    and the rewrite is recorded, under this name."""


type HITLToolCallEvaluator = Callable[[ModelToolCall, HITLToolLoopContext], HITLToolCallAssessment]


@dataclass(frozen=True, slots=True)
class RuntimeHITLToolLoop:
    """Iterate model-emitted tool calls through gate evaluation, HITL and dispatch.

    One typed assessment per call (from `assess`) decides everything: its `GateLevel` sets
    whether the operator is asked, which responses they may give, and whether dispatch can
    happen; its owner replaces the model-supplied host label for the rewrite record, the
    prompt and dispatch. Under DENY nothing dispatches, whatever the adapter answers.
    """

    wiring: RuntimeCpIsWiring
    placement_registry: RuntimeHITLPlacementRegistry
    assess: HITLToolCallEvaluator
    gate: HITLGateAdapter
    dispatcher: HITLToolDispatcher
    response_auditor: HITLToolResponseAuditor

    async def run_tool_calls(
        self,
        calls: Sequence[ModelToolCall],
        context: HITLToolLoopContext,
    ) -> tuple[HITLToolLoopCallResult, ...]:
        """Process one journaled model turn's tool calls in provider order."""
        results: list[HITLToolLoopCallResult] = []
        for call in calls:
            results.append(await self._run_call(call, context))
        return tuple(results)

    async def _run_call(
        self, call: ModelToolCall, context: HITLToolLoopContext
    ) -> HITLToolLoopCallResult:
        try:
            raw = cast(object, self.assess(call, context))
        except Exception:
            # [LAW:no-silent-failure] An uncomputable level is a typed refusal the model
            # sees: no prompt (nothing to ask under) and no dispatch.
            return _refused(call, None, None, None, HITLToolRefusalReason.EVALUATOR_FAILED)
        assessment = _parse_assessment(raw)
        if isinstance(assessment, HITLToolRefusalReason):
            return _refused(call, None, None, None, assessment)
        level = assessment.level
        # Everything downstream (rewrite record, prompt, dispatch) sees the assessed owner.
        call = replace(call, server=assessment.owner)
        palette = compute_effective_palette(level, context.cross_trust_boundary_state, None)
        rewritten = self.placement_registry.rewrite_tool_call(
            tool=call.tool,
            server=call.server,
            persona_tier=context.persona_tier,
            proposed_action=_proposed_action_from_tool_call(call),
            cell_synchrony_class=context.cell_synchrony_class,
            cross_trust_boundary_state=context.cross_trust_boundary_state,
            hitl_required=level is not GateLevel.AUTO,
        )
        if not rewritten.hitl_required:
            return await self._dispatch(call, context, rewritten, None, None)
        variant = rewritten.variant
        if variant is None:
            raise RuntimeError("HITL-required rewrite must include a semantic variant")
        # The ledger records the palette the operator is actually offered.
        rewritten = rewritten.model_copy(update={"response_palette": palette})
        write_result = await self.wiring.emit_hitl_tool_call_rewriting_state_ledger_entry(
            workflow_id=context.workflow_id,
            step_id=context.step_id,
            tool_call_id=call.tool_call_id,
            semantic_variant_binding_id=variant.value,
            rewritten_tool_call=rewritten,
            actor=context.actor,
        )
        reply = cast(object, await self.gate.decide(call=call, context=context, palette=palette))
        decision, admitted_reply = _admit(level, palette, reply)
        # A DENY reply is still an operator response even though it cannot dispatch.
        # Admission is the single authority for the audit boundary: malformed,
        # out-of-palette and contentless EDIT replies are never recorded as valid.
        if admitted_reply is not None:
            await self.response_auditor.record(
                call=call, context=context, level=level, decision=admitted_reply
            )
        if isinstance(decision, HITLToolRefusal):
            response = reply.response if isinstance(reply, HITLGateDecision) else None
            return _refused(call, rewritten, write_result, response, decision)
        if decision.response is HITLResponse.REJECT:
            return HITLToolLoopCallResult(
                tool_call_id=call.tool_call_id,
                rewritten_tool_call=rewritten,
                rewrite_write_result=write_result,
                gate_response=decision.response,
                dispatched=False,
                dispatch_result=None,
            )
        if decision.response is HITLResponse.RESPOND:
            return HITLToolLoopCallResult(
                tool_call_id=call.tool_call_id,
                rewritten_tool_call=rewritten,
                rewrite_write_result=write_result,
                gate_response=decision.response,
                dispatched=False,
                dispatch_result={"response_text": decision.response_text or ""},
            )
        dispatch_call = call
        if decision.response is HITLResponse.EDIT:
            dispatch_call = ModelToolCall(
                tool_call_id=call.tool_call_id,
                tool=call.tool,
                server=call.server,
                arguments=decision.edited_arguments
                if decision.edited_arguments is not None
                else call.arguments,
                provider=call.provider,
                model=call.model,
            )
        return await self._dispatch(
            dispatch_call, context, rewritten, write_result, decision.response
        )

    async def _dispatch(
        self,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        rewritten: RewrittenToolCall,
        write_result: WriteResult | None,
        gate_response: HITLResponse | None,
    ) -> HITLToolLoopCallResult:
        dispatch_result = await self.dispatcher.dispatch(call, context)
        return HITLToolLoopCallResult(
            tool_call_id=call.tool_call_id,
            rewritten_tool_call=rewritten,
            rewrite_write_result=write_result,
            gate_response=gate_response,
            dispatched=True,
            dispatch_result=dispatch_result,
        )


def _parse_assessment(raw: object) -> HITLToolCallAssessment | HITLToolRefusalReason:
    """Parse the evaluator's runtime value; its declared return type is not trusted.

    [LAW:parse-dont-validate] The one place an evaluator value is judged: only an
    assessment with a real `GateLevel` and a non-empty owner name leaves as one. `None`, a
    bare level, a string, an int or a foreign enum would otherwise open the gate as if it
    were a non-DENY level.
    """
    if not isinstance(raw, HITLToolCallAssessment):
        return HITLToolRefusalReason.MALFORMED_GATE_LEVEL
    level, owner = cast(object, raw.level), cast(object, raw.owner)
    if not isinstance(level, GateLevel) or not isinstance(owner, str) or not owner:
        return HITLToolRefusalReason.MALFORMED_GATE_LEVEL
    return raw


def _admit(
    level: GateLevel,
    palette: frozenset[HITLResponse],
    reply: object,
) -> tuple[HITLGateDecision | HITLToolRefusal, HITLGateDecision | None]:
    """Parse an adapter reply into an admitted decision, or the refusal it earns.

    [LAW:parse-dont-validate] The one place a reply is judged against the level and palette;
    what leaves is either a `HITLGateDecision` the palette allows or a typed refusal. The
    adapter's declared return type is not trusted: a reply that is not a decision, or answers
    outside the offered palette, refuses; and under DENY every in-palette reply (REJECT or
    RESPOND) still refuses, carrying RESPOND text.
    """
    if not isinstance(reply, HITLGateDecision):
        return HITLToolRefusal(HITLToolRefusalReason.MALFORMED_GATE_REPLY), None
    response = cast(object, reply.response)
    if not isinstance(response, HITLResponse):
        return HITLToolRefusal(HITLToolRefusalReason.MALFORMED_GATE_REPLY), None
    if response not in palette:
        return HITLToolRefusal(HITLToolRefusalReason.RESPONSE_OUTSIDE_PALETTE), None
    if response is HITLResponse.EDIT and reply.edited_arguments is None:
        return HITLToolRefusal(HITLToolRefusalReason.MALFORMED_GATE_REPLY), None
    if level is GateLevel.DENY:
        text = reply.response_text if response is HITLResponse.RESPOND else None
        return HITLToolRefusal(HITLToolRefusalReason.POLICY_DENY, response_text=text), reply
    return reply, reply


def _refused(
    call: ModelToolCall,
    rewritten: RewrittenToolCall | None,
    write_result: WriteResult | None,
    response: HITLResponse | None,
    refusal: HITLToolRefusal | HITLToolRefusalReason,
) -> HITLToolLoopCallResult:
    typed = refusal if isinstance(refusal, HITLToolRefusal) else HITLToolRefusal(refusal)
    return HITLToolLoopCallResult(
        tool_call_id=call.tool_call_id,
        rewritten_tool_call=rewritten,
        rewrite_write_result=write_result,
        gate_response=response,
        dispatched=False,
        dispatch_result=None,
        refusal=typed,
    )


def _proposed_action_from_tool_call(call: ModelToolCall) -> ProposedAction:
    return ProposedAction(
        action_kind=ActionKind.TOOL_CALL,
        payload={
            "tool_name": call.tool,
            "tool_args": dict(call.arguments),
            "server": call.server,
            "tool_call_id": call.tool_call_id,
            "provider": call.provider,
            "model": call.model,
        },
        brief=None,
    )

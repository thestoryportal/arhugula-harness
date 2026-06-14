"""LLM-dispatch composer — stage 5 LOOP_INIT (U-RT-52, opens L9).

Per `Spec_Harness_Runtime_v1.md` v1.2 §C-RT-15 (LLM-dispatch composer).
Satisfies the `harness_cp.workflow_driver.StepDispatcher` Protocol
(declared at `harness-cp/src/harness_cp/workflow_driver.py:151`,
`runtime_checkable`). Per-step async composer that:

  1. Resolves the per-provider adapter from `ctx.providers` via
     ``binding.model_binding.provider`` (CP `ModelBinding.provider: str`
     per C-CP-01 §1.4).
  2. Opens a GenAI-semconv 1.41.0 span via
     ``ctx.tracer_provider.get_tracer("harness.runtime.llm_dispatch")``.
  3. Dispatches to the provider's SDK message-construction method
     (anthropic / openai / ollama) using the unpacked payload.
  4. Populates GenAI semconv attributes per OD C-OD-04..08 + (for the
     anthropic provider) ``anthropic.*`` cache attributes per AS spec
     C-AS-14 §14.2.
  5. Returns ``Mapping[str, Any]`` per `StepDispatcher` Protocol contract.

**Payload-shape convention (Class 3 fork resolution 2026-05-20,
`.harness/fork_u_rt_52_step_payload_shape.md`).** ``step.step_payload``
is consumed as a `harness_cp.cp_shared_types.ProviderAgnosticPayload`
mapping (``messages`` / ``tools`` / ``params``) per ADR-F1 v1.2 +
C-CP-01 §1.1 the provider-neutral 3-tuple. Spec §14.5 was silent on
``step_payload`` shape at v1.2; this module pins the convention at
v1.3 (`Spec_Harness_Runtime_v1.md` §14.5 amendment 2026-05-20).

**Q2a scope discipline (per `.harness/fork_llm_dispatch_composer_scope.md`
operator ratification 2026-05-20).** Composer is the smallest-scope
surface: per-step dispatch only. Fallback / retry / breaker wrappers
are explicitly out of scope — provider-side exceptions propagate
unmodified to `workflow_driver.py:380-389` `try/except`. CP-3 (retry.*)
+ CP-4 (fallback chain) retirements deferred to follow-on units.

**Q3a in-arc GenAI semconv binding.** Composer attaches the GenAI
1.41.0 attribute set per OTel semconv. Enables H_T-OD-2 PARTIAL →
RETIRE-READY upgrade in the same arc (OTel SDK substrate operative +
GenAI binding present + spans flow).

**OTel context-manager note.** Spec §14.5 invariants phrase ``async
with tracer.start_as_current_span(...)``; OpenTelemetry's tracer
context manager is synchronous (returns a regular ``ContextManager``,
not an ``AsyncContextManager``). Inside this async function we use
plain ``with`` per OTel API contract; spec phrasing is imprecise but
the semantic — exactly one span per call, lifecycle bound by the
``with`` block — is preserved.

**Module convention.** One module per unit. Bound at bootstrap stage 5
alongside override evaluator / topology dispatcher / lifecycle emitter.
Typed `LLMDispatchBindError` for bootstrap-time failures. Mirrors the
L5..L8 stage shape established at U-RT-21..U-RT-41.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast, runtime_checkable

from harness_core import PersonaTier, WorkloadClass
from harness_cp.cp_shared_types import (
    ActorIdentity,
    AgentRole,
    ProviderAgnosticPayload,
    RoutingDecisionTrace,
    TraceContext,
)
from harness_cp.layer_budget import DEFAULT_LAYER_BUDGETS
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.persona_engine_hitl_matrix import SynchronyClass
from harness_cp.routing_core_surface import (
    InferenceRequest,
    ProviderDispatchResult,
    infer,
)
from harness_cp.routing_layer import RoutingLayer
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.validator_fail_transient_staircase import CrossTrustBoundaryState
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep
from harness_od.otel_genai_base import HIERARCHY_CORRELATION_KEY, GenAiOperation

from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLToolLoopContext,
    ModelToolCall,
    RuntimeHITLToolLoop,
)
from harness_runtime.lifecycle.memory_tool_dispatch import (
    derive_context_editing_active,
    execute_with_memory_callbacks,
    step_has_memory_tool,
)


class LLMDispatchBindError(Exception):
    """Raised when LLM-dispatch composer stage materialization fails."""


class LLMDispatchProviderUnreachableError(Exception):
    """Raised when ``binding.model_binding.provider`` resolves to a
    provider absent from ``ctx.providers`` (e.g., Ollama-degraded path
    skipped registration).

    Maps to ``RT-FAIL-PROVIDER-UNREACHABLE`` per
    `Spec_Harness_Runtime_v1.md` v1.2 §C-RT-14 failure-mode taxonomy.
    Carries the offending provider name for operator-facing attribution.
    """

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name
        super().__init__(
            f"RT-FAIL-PROVIDER-UNREACHABLE: provider {provider_name!r} not in ctx.providers"
        )


class LLMDispatchPayloadShapeError(Exception):
    """Raised when ``step.step_payload`` cannot be coerced to the
    provider-neutral ``ProviderAgnosticPayload`` shape.

    Per the Class 3 fork resolution (2026-05-20), ``step.step_payload``
    is the `ProviderAgnosticPayload(messages, tools, params)` 3-tuple
    per C-CP-01 §1.1. Mis-shaped payloads (e.g., missing ``messages``)
    surface as this typed error rather than a generic ``KeyError`` /
    ``ValidationError`` so the driver's ``except`` boundary can
    attribute the failure to the dispatch site.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(f"RT-FAIL-PAYLOAD-SHAPE: {reason}")


class PromptInjectionConflictError(Exception):
    """Raised when a configured active prompt collides with a payload-carried
    system source at translate-time (R-PM-1 cascade PR #1).

    The active prompt (``HarnessContext.prompt_manifest.active_prompt_version
    .content``, bound on the dispatcher as ``active_system_prompt``) is the
    harness-owned base system prompt. If an active prompt is configured AND the
    payload already carries a competing system source — an Anthropic
    ``params["system"]`` (the opaque escape hatch) or an OpenAI/Ollama leading
    ``{"role":"system"}`` message — the two-source ambiguity is **fail-loud /
    detect-then-refuse**, never silently merged or dropped (consistent with the
    arc-#1 ``RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE`` posture).

    Maps to ``RT-FAIL-PROMPT-INJECTION-CONFLICT`` per
    `Spec_Harness_Runtime_v1.md` §C-RT-15 (v1.44 amendment). Step-level (per
    dispatch), like ``RT-FAIL-PROVIDER-UNREACHABLE``: propagates through the
    driver ``except`` boundary at `workflow_driver.py` as a step-failure; does
    NOT abort bootstrap.

    Known operational consequence: for OpenAI/Ollama a leading
    ``{"role":"system"}`` message is the idiomatic way a workflow step supplies
    its own system prompt, so configuring an active prompt will hard-error any
    workflow that already carries its own system message — this is the intended
    v1 contract (surface the collision, do not silently pick). The escape valve
    is a future explicit merge/replace policy (runtime spec §14.5 OQ-5).
    """

    def __init__(self, provider: str, source: str) -> None:
        self.provider = provider
        self.source = source
        super().__init__(
            "RT-FAIL-PROMPT-INJECTION-CONFLICT: active prompt configured but "
            f"{provider!r} payload already carries a system source ({source}); "
            "fail-loud rather than silently merge/replace"
        )


@runtime_checkable
class _ProvidersLike(Protocol):
    """Minimal ``ctx.providers`` substrate the composer consumes.

    Structurally satisfied by `harness_runtime.lifecycle.providers.
    ProviderClientsStage.providers` (a ``dict[str, ProviderClient]``
    mapping per C-RT-05). Position-only ``key`` parameters match
    `dict.__getitem__` / `dict.__contains__` shape so Protocol
    conformance carries through to the concrete dict at the stage-5
    factory call site.
    """

    def __contains__(self, key: object, /) -> bool: ...
    def __getitem__(self, key: str, /) -> Any: ...
    def __len__(self) -> int: ...


@runtime_checkable
class _TracerProviderLike(Protocol):
    """Minimal ``ctx.tracer_provider`` substrate the composer consumes.

    Structurally satisfied by `opentelemetry.sdk.trace.TracerProvider`
    materialized at C-RT-06 stage 4 OD.
    """

    def get_tracer(self, instrumenting_module_name: str, /) -> Any: ...


def _coerce_payload(payload: Mapping[str, Any]) -> ProviderAgnosticPayload:
    """Coerce ``step.step_payload`` to `ProviderAgnosticPayload`.

    Pydantic v2 ``model_validate`` accepts a mapping in the canonical
    shape. Mis-shaped mappings raise `LLMDispatchPayloadShapeError`
    wrapping the underlying `ValidationError` so the driver's
    ``except`` block sees a typed failure attributable to the dispatch
    site.
    """
    if isinstance(payload, ProviderAgnosticPayload):
        return payload
    try:
        return ProviderAgnosticPayload.model_validate(payload)
    except Exception as exc:
        raise LLMDispatchPayloadShapeError(
            f"step.step_payload not coercible to ProviderAgnosticPayload: {exc}"
        ) from exc


def _set_if_present(span: Any, key: str, value: Any) -> None:
    """Set a span attribute only when the value is not ``None``.

    OTel allows ``None`` as a value but the GenAI semconv discourages
    emitting attributes whose value is unknown. This helper keeps the
    per-provider attribute extraction code uncluttered.
    """
    if value is not None:
        span.set_attribute(key, value)


def _extract_anthropic_cache_request_attrs(
    payload: ProviderAgnosticPayload,
) -> tuple[str | None, int | None]:
    """Extract ``anthropic.cache_breakpoint_id`` + ``anthropic.cache_ttl_seconds``
    from the request payload's ``cache_control`` directives, if present.

    Per Anthropic prompt-caching docs, ``cache_control`` lives on
    individual content blocks within ``messages`` (and optionally on
    ``system`` / ``tools``). The breakpoint_id is the ordinal of the
    first cache_control-bearing block (≤4 per Anthropic limit); the
    ttl is the ``cache_control.ttl`` field translated to seconds
    (``"5m"`` → 300; ``"1h"`` → 3600). Returns ``(None, None)`` when
    no cache_control directive is present.

    The extraction is best-effort: payloads that don't follow the
    cache-control convention return ``(None, None)`` rather than
    raising. Per C-AS-14 §14.2 these attributes have low cardinality
    (≤4 breakpoints; binary ttl).
    """
    for index, message in enumerate(payload.messages):
        content = cast(Any, message.get("content"))
        if not isinstance(content, list):
            continue
        blocks = cast(list[Any], content)
        for block in blocks:
            if not isinstance(block, Mapping):
                continue
            block_mapping = cast(Mapping[str, Any], block)
            cache_control = cast(Any, block_mapping.get("cache_control"))
            if not isinstance(cache_control, Mapping):
                continue
            cc_mapping = cast(Mapping[str, Any], cache_control)
            ttl_label = cast(Any, cc_mapping.get("ttl"))
            ttl_seconds: int | None
            if ttl_label == "1h":
                ttl_seconds = 3600
            elif ttl_label == "5m":
                ttl_seconds = 300
            elif ttl_label is None:
                ttl_seconds = 300  # Anthropic default
            else:
                ttl_seconds = None
            return (f"msg-{index}", ttl_seconds)
    return (None, None)


# R-300 MVP routing-envelope placeholders. The DECLARATIVE-echo layer decision
# (see `RuntimeLLMDispatcher.dispatch`) echoes the resolved `binding.model_binding`
# and ignores the InferenceRequest discriminators, so these are carried-but-not-
# selection-driving at MVP. `AgentRole` is an open-string newtype and no per-step
# role is threaded through the execution path at v1.6 (WorkflowStep carries only
# step_id/step_kind/step_payload) and no conventional default-role key exists in
# `RoutingManifest.per_role_bindings`; they become load-bearing at
# R-300-second-provider when `route()` performs real per-discriminator selection.
_MVP_DEFAULT_AGENT_ROLE = AgentRole("default")
_MVP_DEFAULT_WORKLOAD_CLASS = WorkloadClass.SOFTWARE_ENGINEERING
_MVP_PLACEHOLDER_TRACE_CONTEXT = TraceContext(
    trace_id="0" * 32, span_id="0" * 16, trace_flags=0, trace_state=None
)
# Used when `self.routing_manifest` is unset (unit-test ergonomics). The echo
# decision ignores the manifest, so an empty manifest is behavior-neutral.
_EMPTY_ROUTING_MANIFEST = RoutingManifest(
    manifest_version=1,
    per_role_bindings={},
    per_workload_overrides={},
    fallback_chains=(),
    retry_policies={},
)


@dataclass(frozen=True, slots=True)
class RuntimeLLMDispatcher:
    """Per-step LLM-dispatch composer satisfying `harness_cp.workflow_driver.
    StepDispatcher` Protocol (C-RT-15 + C-CP-25 §25.3.3.4).

    Constructed at bootstrap stage 5 (LOOP_INIT) with frozen references
    to the provider clients map + tracer-provider materialized at
    earlier stages. The composer is stateless across calls — each
    `dispatch` invocation is driven entirely by its arguments + the
    frozen provider/tracer substrate.

    U-OD-38 extension (2026-05-21): cost-attribution substrate added per
    C-OD-26.1 + C-OD-26.2. Post-provider-call, every dispatch invokes
    `attribute_llm_dispatch_cost(...)` to compute + persist the per-attempt
    cost-record + audit-ledger entry. Substrate (cost_chain / audit_writer /
    rate_table) is REQUIRED — cost-attribution is not optional per AC #1.

    Attributes
    ----------
    providers :
        Frozen reference to the ``ctx.providers`` map (provider_name →
        ProviderClient adapter) materialized at stage 3a per C-RT-05.
    tracer_provider :
        Frozen reference to the ``ctx.tracer_provider`` materialized at
        stage 4 OD per C-RT-06.
    cost_chain :
        Cost-attribution chain (`ctx.cost_chain`) materialized at stage 4 OD
        per C-RT-31. Consumed at every dispatch for the §C-OD-26.1
        per-attempt cost computation. U-OD-38 — required.
    audit_writer :
        Audit-ledger writer (`ctx.audit_writer`) materialized at stage 4 OD
        per C-RT-32. Receives the cost-attribution audit entry per
        §C-OD-26.3. U-OD-38 — required.
    rate_table :
        Resolved PRICE_TABLE_REF (`ctx.rate_table`) per §C-OD-28.2 —
        immutable for the workflow's lifetime. Resolves to ProviderRates per
        (provider, model) for compute_per_attempt_cost. U-OD-38 — required.
    """

    providers: _ProvidersLike
    tracer_provider: _TracerProviderLike
    # U-OD-38 cost-attribution substrate. Required at production
    # construction (enforced at bootstrap stage 5); defaulted to None to
    # preserve construction ergonomics for unit-tests that only exercise
    # the LLM-dispatch surface and don't need cost-attribution. When any
    # is None, _attribute_cost_best_effort early-returns (no-op).
    cost_chain: Any = None
    audit_writer: Any = None
    rate_table: Any = None
    # U-RT-81 (C-RT-15 §14.5.1) — Memory tool storage-backend registry +
    # deployment_surface for `resolve_backend` call. When `step.step_payload.
    # tools` contains the Anthropic Memory tool definition + both fields are
    # bound, the dispatcher routes the anthropic branch through the harness-
    # authored inner loop at `memory_tool_dispatch.execute_with_memory_callbacks`
    # per spec v1.17 §14.5.1 mechanism β. Both defaulted to None for unit-test
    # ergonomics; production stage-5 binding sets both per `materialize_
    # llm_dispatcher_stage` kwargs.
    memory_tool_registry: Any = None
    deployment_surface: Any = None
    # R-CXA-2 — provider-turn model-emitted tool calls can run through the
    # bound RuntimeHITLToolLoop before Anthropic continuation. None preserves
    # the historical one-shot provider dispatch path for unit tests and
    # bootstrap states where the R-CXA-2 producer loop is unavailable.
    hitl_tool_loop: RuntimeHITLToolLoop | None = None
    # OD spec v1.20 §C-OD-04 §4.3 `server.address` / `server.port` resolution
    # for the ollama provider (operator-configurable endpoint). Threaded from
    # `RuntimeConfig.ollama_host` at stage 5 per `[[fork-od-spec-declared-but-
    # not-emitted-attributes]]` Path A. Defaults to None: when unset, ollama
    # spans emit neither `server.address` nor `server.port` per OTel
    # Conditionally Required "If `server.address` is set" gating.
    ollama_host: str | None = None
    # U-RT-101 (C-RT-27 §14.17.2 hook-2 per-LLM-dispatch) — Skill activation
    # emitter + loaded skills carrier. Both default None for unit-test
    # ergonomics; production stage-5 binding sets both when the operator opts
    # in via `RuntimeConfig.skill_activation_hook_config`. When either is None
    # OR the emitter's bound hook is None, the per-LLM-dispatch activation
    # hook silent-skips per §14.17.5 invariant 3.
    skill_activation_emitter: Any = None
    skills: Any = None
    # R-300 — layered routing-selection substrate. Threaded at bootstrap stage 5
    # from `ctx.routing_manifest` (stage 3b) + the run `workload_class` +
    # `config.persona_tier`. All default None for unit-test ergonomics; the
    # DECLARATIVE-echo path tolerates a None manifest (the echo decision ignores
    # it; `_EMPTY_ROUTING_MANIFEST` substitutes) and resolves the envelope
    # discriminators to MVP placeholders when unset.
    routing_manifest: RoutingManifest | None = None
    workload_class: WorkloadClass | None = None
    persona_tier: PersonaTier | None = None
    # R-PM-1 cascade PR #1 — the active prompt's resolved system-prompt content
    # (`ctx.prompt_manifest.active_prompt_version.content or None`), bound at
    # bootstrap stage 5. None / "" → no injection (byte-identical to pre-R-PM-1
    # dispatch; the local-first default). Per-provider injection happens at the
    # translate fns (`system=` kwarg for anthropic; leading `role:"system"`
    # message for openai/ollama); `ProviderAgnosticPayload` stays frozen.
    active_system_prompt: str | None = None

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Invoke the step body under the effective binding; return step output.

        ``step_context`` parameter accepted at v1.6 Path A per amended
        ``StepDispatcher`` Protocol (C-RT-17 resolution). C-RT-15 does NOT
        consume ``step_context`` at v1.6; reserved for v1.7+ surfaces that
        may bind parent context to the LLM inference span attributes per
        future C-RT-NN amendments.

        Per C-RT-15 §Specification content steps 1-5. Provider-specific
        dispatch branches are exhaustive over the three providers
        constructed at C-RT-05 stage 3a (anthropic / openai / ollama).

        R-300 (2026-06-01): provider/model SELECTION now flows through the
        layered routing strategy via `infer`
        (`harness_cp.routing_core_surface`) rather than reading
        `binding.model_binding` directly. `infer` composes `route` (U-CP-05)
        with `_invoke_provider` (this dispatcher's provider-SDK boundary) as
        its injected dispatch callable. At MVP the DECLARATIVE layer echoes the
        resolved `binding.model_binding` (== the manifest role binding with
        per-step overrides applied), so selection is behavior-preserving; the
        new behavior is the `routing.*` span attribution (C-CP-01 §1.4) on the
        `llm.inference` span. `infer` runs inside each RetryBreakerFallback
        attempt; at the echo it is idempotent and cross-family fallback remains
        the wrapper's responsibility (R-300-second-provider).

        Raises
        ------
        LLMDispatchProviderUnreachableError
            ``binding.model_binding.provider`` not in ``self.providers``.
            Maps to ``RT-FAIL-PROVIDER-UNREACHABLE`` per C-RT-14.
        LLMDispatchPayloadShapeError
            ``step.step_payload`` not coercible to `ProviderAgnosticPayload`.
        Exception
            Any provider-side SDK exception propagates unmodified per
            Q2a scope discipline. The CP driver's ``except`` boundary
            at `workflow_driver.py:380-389` fails the step with
            ``step-failure: {type}: {exc}``.
        """
        # --- C-RT-27 §14.17.2 hook-2 (per-LLM-dispatch activation hook) ---
        # Pre-condition: emitter bound + hook bound + skills available. When
        # any is missing/None, silent-skip per §14.17.5 invariant 3 (operator
        # opt-out path preserves pre-v1.32 production behavior). Emit one
        # `skill.activation` span per skill returned by the operator-supplied
        # `SkillActivationHook.select_for_llm_dispatch(...)` policy, with
        # `activation_mode = TOOL_SEARCH` per Q2=(d) hybrid hook-to-enum
        # mapping. Fires BEFORE provider resolution + LLM call per §14.17.2
        # hook-2 step 4 ordering.
        if (
            self.skill_activation_emitter is not None
            and self.skill_activation_emitter.hook is not None
            and self.skills is not None
        ):
            from harness_runtime.lifecycle.skill_activation import SkillActivationMode

            selected_ids = list(
                self.skill_activation_emitter.hook.select_for_llm_dispatch(
                    loaded_skills=self.skills.keys(),
                    workflow_id=step_context.workflow_id,
                    step_index=step_context.step_index,
                )
            )
            for skill_id in selected_ids:
                if skill_id in self.skills:
                    self.skill_activation_emitter.emit(
                        skill_id=skill_id,
                        mode=SkillActivationMode.TOOL_SEARCH,
                        workflow_id=step_context.workflow_id,
                        skill=self.skills[skill_id],
                    )

        payload = _coerce_payload(step.step_payload)

        # --- U-RT-114 (C-RT-15 §14.5.3): branch AgentRole carry ----------
        # The branch role (the CP-composed child StepExecutionContext, CP plan
        # v2.32 U-CP-81) is carried for the `InferenceRequest` envelope's
        # `agent_role` attribution below. Per-role MODEL selection is resolved
        # ONE LAYER OUT, at the C-RT-16 `RetryBreakerFallbackDispatcher` (the
        # dispatch-composition surface that owns candidate selection): the
        # per-role model is that wrapper's PRIMARY fallback candidate, so per-role
        # specialization composes with fallback — ONE source of truth for model
        # selection (the wrapper's chain). Here the inner faithfully dispatches
        # `binding.model_binding` (the wrapper's rebound candidate). §14.5.3
        # mechanism + all 3 invariants preserved; indexing the per-role model at
        # the inner too would create TWO authorities (wrapper candidate vs inner
        # override) and silently defeat fallback for role-routed branches (the
        # C-RT-16 composition gap). MODEL BINDING ONLY — the per-role PROMPT is
        # resolved once at stage 0 with the default role (deferred to B4, §14.5.3).
        _role = step_context.agent_role or _MVP_DEFAULT_AGENT_ROLE
        _effective_model_binding = binding.model_binding

        # --- R-300: layered routing-selection via infer() ----------------
        # The DECLARATIVE layer decision echoes the effective binding (the per-role
        # model binding, U-RT-114, else the CP-resolved manifest role binding with
        # per-step overrides applied) — selection is behavior-preserving at MVP.
        # `route()`'s `manifest` arg + the envelope discriminators are carried but
        # not selection-driving until R-300-second-provider.
        def _declarative_echo(
            _payload: ProviderAgnosticPayload, _manifest: RoutingManifest
        ) -> str | None:
            return f"{_effective_model_binding.provider}:{_effective_model_binding.model}"

        # `infer()` requires an InferenceRequest envelope. Its discriminator
        # fields are carried for the C-CP-01 §1.1 API surface but DISCARDED at
        # this boundary: the live routing decision is surfaced as `routing.*`
        # span attrs inside `_invoke_provider`, and the step output is the raw
        # provider Mapping returned below — NOT the InferenceResponse (which is
        # likewise discarded). They become load-bearing at R-300-second-provider.
        envelope = InferenceRequest(
            agent_role=_role,
            workload_class=self.workload_class or _MVP_DEFAULT_WORKLOAD_CLASS,
            persona_tier=self.persona_tier or PersonaTier.SOLO_DEVELOPER,
            context_tokens=len(payload.messages),
            request_payload=payload,
            trace_context=_MVP_PLACEHOLDER_TRACE_CONTEXT,
        )

        # The raw provider response Mapping (the step output) is surfaced out of
        # the `infer()` composition via this holder — `infer()` returns an
        # InferenceResponse, but the step-output contract is the raw Mapping.
        raw_response: dict[str, Mapping[str, Any]] = {}

        async def _provider_dispatch(
            provider: str,
            model: str,
            inner_payload: ProviderAgnosticPayload,
            routing_trace: RoutingDecisionTrace,
        ) -> ProviderDispatchResult:
            response = await self._invoke_provider(
                provider,
                model,
                inner_payload,
                step_context,
                step_id=str(step.step_id),
                routing_trace=routing_trace,
            )
            raw_response["value"] = response
            # ProviderDispatchResult is structurally required by `infer()` but
            # DISCARDED at this boundary: the raw `response` Mapping is the step
            # output, and gen_ai.usage.* + cost-attribution are already emitted +
            # persisted inside `_invoke_provider`. Minimal placeholder.
            return ProviderDispatchResult(
                response_payload=ProviderAgnosticPayload(messages=(), tools=None, params={}),
                tokens_in=0,
                tokens_out=0,
                cached_tokens_in=0,
            )

        await infer(
            envelope,
            dispatch=_provider_dispatch,
            manifest=self.routing_manifest or _EMPTY_ROUTING_MANIFEST,
            layer_decisions={RoutingLayer.DECLARATIVE: _declarative_echo},
            budgets=DEFAULT_LAYER_BUDGETS,
        )
        return raw_response["value"]

    async def _invoke_provider(
        self,
        provider_name: str,
        model: str,
        payload: ProviderAgnosticPayload,
        step_context: StepExecutionContext,
        *,
        step_id: str,
        routing_trace: RoutingDecisionTrace,
    ) -> Mapping[str, Any]:
        """Provider-SDK dispatch boundary — the injected dispatch callable for
        `infer()` (R-300). Opens the `llm.inference` span (gen_ai.* + routing.*
        attribution), dispatches to the routed provider, runs cost-attribution,
        and returns the raw provider response Mapping (the step output).

        ``provider_name`` + ``model`` are the routing-selected candidate (per
        `route()` per U-CP-05); ``routing_trace`` carries the routing decision
        for `routing.*` span attribution per C-CP-01 §1.4.

        Raises
        ------
        LLMDispatchProviderUnreachableError
            ``provider_name`` not in ``self.providers``.
            Maps to ``RT-FAIL-PROVIDER-UNREACHABLE`` per C-RT-14.
        """
        # --- Step 1: provider resolution --------------------------------
        if provider_name not in self.providers:
            raise LLMDispatchProviderUnreachableError(provider_name)

        adapter = self.providers[provider_name]

        # --- Step 2: open GenAI-semconv span ----------------------------
        # Span name per OD spec v1.12 §C-OD-04 §4.1 (2-token space-separated):
        # `{gen_ai.operation.name} {gen_ai.request.model}`. Byte-exact to OTel
        # GenAI semantic conventions 1.41.0 archived text per
        # `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.2 (R1).
        # Required (Stable) attribute set per §4.3: `gen_ai.operation.name` +
        # `gen_ai.provider.name` + `gen_ai.request.model` — all 3 emitted at
        # step 2 below per fork §"Adjacent observations" (f) RESOLVED arc.
        # Finding (g) RESOLVED at `_PROVIDER_OPERATIONS` binding above —
        # the operation-token in the span name + the `gen_ai.operation.name`
        # attribute value both source from `GenAiOperation.CHAT.value`
        # ("chat") per §4.2 enum.
        tracer = self.tracer_provider.get_tracer("harness.runtime.llm_dispatch")
        operation = _PROVIDER_OPERATIONS.get(provider_name)
        if operation is None:
            # Defensive — every key in self.providers is one of the
            # three constructed at stage 3a per C-RT-05. Surfacing any
            # other key as UNREACHABLE preserves the C-RT-14 taxonomy.
            raise LLMDispatchProviderUnreachableError(provider_name)
        span_name = f"{operation.value} {model}"

        # OTel tracer CM is synchronous (returns ``ContextManager``, not
        # ``AsyncContextManager``); spec §14.5 phrasing is imprecise.
        with tracer.start_as_current_span(span_name) as span:
            # §4.3 Required (Stable) tier — all 2 attributes always emitted
            # (per v1.19 §1.1 redistribution: `gen_ai.operation.name` +
            # `gen_ai.provider.name`).
            span.set_attribute("gen_ai.operation.name", operation.value)
            span.set_attribute("gen_ai.provider.name", provider_name)
            # §4.3 Conditionally Required tier — harness emits the model
            # unconditionally (always known at dispatch) + the conversation
            # id from `step_context.workflow_id` (always known per CP spec
            # v1.12 §25.2.1 9th-field). `server.port` emission below is
            # gated on `server.address` per the OTel canonical condition.
            # Closes `[[fork-od-spec-declared-but-not-emitted-attributes]]`
            # finding (g) Path A 2026-05-27.
            span.set_attribute("gen_ai.request.model", model)
            span.set_attribute(HIERARCHY_CORRELATION_KEY, step_context.workflow_id)
            # §4.3 `server.address` Recommended (Development) + `server.port`
            # Conditionally Required ("If `server.address` is set"). Hosted
            # providers resolve from static maps; ollama resolves from the
            # dispatcher-bound `ollama_host` (None → no emission per OTel
            # Conditionally Required gating). Closes Path A finding (f).
            if provider_name == "ollama":
                server_address, server_port = _parse_ollama_host(self.ollama_host)
            else:
                server_address = _PROVIDER_SERVER_ADDRESS.get(provider_name)
                server_port = _PROVIDER_SERVER_PORT.get(provider_name)
            if server_address is not None:
                span.set_attribute("server.address", server_address)
                if server_port is not None:
                    span.set_attribute("server.port", server_port)

            # --- routing.* attribution (C-CP-01 §1.4; R-300) ------------
            # The layered routing decision (`route()` per U-CP-05, composed by
            # `infer()`) attaches to the `llm.inference` span per §1.4. The full
            # §1.4 set is emitted so routing visibility is complete on the span
            # (the canonical routing-visibility surface) — `infer()`'s
            # InferenceResponse is discarded at the dispatch boundary, so the
            # span is where routing visibility lives. `routing.binding_rationale`
            # is the §1.4 optional token; at the MVP DECLARATIVE echo it records
            # the layer + selected candidate.
            span.set_attribute("routing.provider", provider_name)
            span.set_attribute("routing.model", model)
            span.set_attribute("routing.layer", routing_trace.layer)
            span.set_attribute(
                "routing.binding_rationale",
                f"{routing_trace.layer}:{routing_trace.candidate}",
            )

            # --- Step 3: per-provider dispatch --------------------------
            cache_attrs: _AnthropicCacheAttrs | None
            request_attrs: _AnthropicRequestAttrs | None
            if provider_name == "anthropic":
                # U-RT-81 (C-RT-15 §14.5.1) — Memory tool callback-injection
                # composer-step. If `step.step_payload.tools` contains the
                # Anthropic Memory tool definition AND the registry + surface
                # are bound, route through the harness-authored inner loop
                # (mechanism β). Otherwise the existing §14.5 step 4 path
                # preserves verbatim. The branch detection is intentionally
                # cheap (single `step_has_memory_tool` predicate over the
                # `payload.tools` sequence) so non-memory dispatches see
                # zero overhead.
                if (
                    self.memory_tool_registry is not None
                    and self.deployment_surface is not None
                    and step_has_memory_tool(payload.tools)
                ):
                    (
                        response,
                        usage_attrs,
                        cache_attrs,
                        request_attrs,
                    ) = await _dispatch_anthropic_with_memory(
                        adapter,
                        model,
                        payload,
                        registry=self.memory_tool_registry,
                        deployment_surface=self.deployment_surface,
                        tracer=tracer,
                        system=self.active_system_prompt,
                    )
                elif (
                    self.hitl_tool_loop is not None
                    and payload.tools is not None
                    and not step_has_memory_tool(payload.tools)
                ):
                    (
                        response,
                        usage_attrs,
                        cache_attrs,
                        request_attrs,
                    ) = await _dispatch_anthropic_with_hitl_tool_loop(
                        adapter,
                        model,
                        payload,
                        hitl_tool_loop=self.hitl_tool_loop,
                        step_context=step_context,
                        step_id=step_id,
                        persona_tier=self.persona_tier or PersonaTier.SOLO_DEVELOPER,
                        system=self.active_system_prompt,
                    )
                else:
                    (
                        response,
                        usage_attrs,
                        cache_attrs,
                        request_attrs,
                    ) = await _dispatch_anthropic(
                        adapter, model, payload, system=self.active_system_prompt
                    )
            elif provider_name == "openai":
                response, usage_attrs = await _dispatch_openai(
                    adapter, model, payload, system=self.active_system_prompt
                )
                cache_attrs = None
                request_attrs = None
            else:  # provider_name == "ollama" (only remaining branch)
                response, usage_attrs = await _dispatch_ollama(
                    adapter, model, payload, system=self.active_system_prompt
                )
                cache_attrs = None
                request_attrs = None

            # --- Step 4: populate response-side attributes --------------
            _set_if_present(span, "gen_ai.usage.input_tokens", usage_attrs.input_tokens)
            _set_if_present(span, "gen_ai.usage.output_tokens", usage_attrs.output_tokens)
            _set_if_present(span, "gen_ai.response.id", usage_attrs.response_id)

            # anthropic.* per C-AS-14 §14.2 — emitted ONLY when
            # provider == "anthropic" per AS-AL-3 cross-axis scope.
            if cache_attrs is not None:
                _set_if_present(
                    span,
                    "anthropic.cache_creation_input_tokens",
                    cache_attrs.cache_creation_input_tokens,
                )
                _set_if_present(
                    span,
                    "anthropic.cache_read_input_tokens",
                    cache_attrs.cache_read_input_tokens,
                )
                _set_if_present(
                    span,
                    "anthropic.cache_breakpoint_id",
                    cache_attrs.cache_breakpoint_id,
                )
                _set_if_present(
                    span,
                    "anthropic.cache_ttl_seconds",
                    cache_attrs.cache_ttl_seconds,
                )
            # anthropic.* rows 5-10 per C-AS-14 §14.2 — request-side +
            # model-derived attrs. `tokenizer_version` always emits;
            # the optional 5 emit only when present per spec optional
            # discipline (`_set_if_present` short-circuits on None).
            if request_attrs is not None:
                _set_if_present(span, "anthropic.thinking_mode", request_attrs.thinking_mode)
                _set_if_present(
                    span,
                    "anthropic.thinking_budget_tokens",
                    request_attrs.thinking_budget_tokens,
                )
                _set_if_present(
                    span,
                    "anthropic.thinking_effort",
                    request_attrs.thinking_effort,
                )
                _set_if_present(span, "anthropic.batch_id", request_attrs.batch_id)
                span.set_attribute("anthropic.tokenizer_version", request_attrs.tokenizer_version)
                _set_if_present(span, "anthropic.inference_geo", request_attrs.inference_geo)

            # --- Step 4.5: cost-attribution (U-OD-38) -------------------
            # Per §C-OD-26.1 + §C-OD-26.2 row "llm_dispatch": every LLM
            # dispatch invokes the 5-substep cost-attribution chain post-
            # provider-call. Persists the cost-record + audit-ledger entry
            # + emits cost.attributed_decimal OTel attribute via U-OD-49
            # string-form preserving Decimal precision at the OTel boundary.
            # Wrapped in best-effort try/except: cost-attribution failure
            # MUST NOT fail the dispatch (cost is observability not contract).
            _attribute_cost_best_effort(
                span=span,
                cost_chain=self.cost_chain,
                audit_writer=self.audit_writer,
                rate_table=self.rate_table,
                provider_name=provider_name,
                model=model,
                parent_idempotency_key=step_context.parent_idempotency_key,
                workflow_id=step_context.workflow_id,
                parent_action_id=step_context.parent_action_id,
                input_tokens=usage_attrs.input_tokens,
                output_tokens=usage_attrs.output_tokens,
                cache_creation=(
                    cache_attrs.cache_creation_input_tokens if cache_attrs is not None else None
                ),
                cache_read=(
                    cache_attrs.cache_read_input_tokens if cache_attrs is not None else None
                ),
                tenant_id=step_context.tenant_id,
            )

            # --- Step 5: return step output mapping ---------------------
            return response


# ---------------------------------------------------------------------------
# Per-provider dispatch helpers.
# ---------------------------------------------------------------------------


#: Per-provider §4.2 operation enum value used for both the span name
#: operation-token (per OD spec v1.12 §C-OD-04 §4.1) and the
#: `gen_ai.operation.name` Required (Stable) attribute (§4.3). All 3
#: providers dispatch chat-style completions:
#:   - `anthropic` → `client.messages.create` (Anthropic Messages API)
#:   - `openai`    → `client.chat.completions.create`
#:   - `ollama`    → `client.chat`
#: All 3 map to `GenAiOperation.CHAT` per OTel GenAI semconv 1.41.0 §4.2.
#: Finding (g) RESOLVED at this binding (was: API method names not in §4.2
#: enum — `messages.create` / `chat.completions` / `chat`).
_PROVIDER_OPERATIONS: dict[str, GenAiOperation] = {
    "anthropic": GenAiOperation.CHAT,
    "openai": GenAiOperation.CHAT,
    "ollama": GenAiOperation.CHAT,
}


#: Per-hosted-provider `server.address` per OD spec v1.20 §C-OD-04 §4.3
#: Recommended (Development) tier. Hosted providers (anthropic / openai) have
#: stable canonical endpoints. Ollama is operator-configurable and is resolved
#: from `RuntimeLLMDispatcher.ollama_host` per the OTel Conditionally Required
#: "If `server.address` is set" rule (no emission when the value is unknown).
_PROVIDER_SERVER_ADDRESS: dict[str, str] = {
    "anthropic": "api.anthropic.com",
    "openai": "api.openai.com",
}

#: Per-hosted-provider `server.port` per OD spec v1.20 §C-OD-04 §4.3
#: Conditionally Required tier. Both hosted providers are HTTPS-only.
_PROVIDER_SERVER_PORT: dict[str, int] = {
    "anthropic": 443,
    "openai": 443,
}


def _parse_ollama_host(host: str | None) -> tuple[str | None, int | None]:
    """Parse `RuntimeConfig.ollama_host` into `(address, port)`.

    Accepts a full URL (e.g., ``http://localhost:11434``) per spec §5 line
    354 `AsyncClient(host=...)` convention. Returns ``(None, None)`` when
    the input is ``None``, satisfying the OTel Conditionally Required "If
    `server.address` is set" gating — when the harness does not know the
    user's configured ollama endpoint, the harness emits neither attribute
    (per advisor 2026-05-27 correction to fork doc §3 Path A static-map
    framing; static `localhost` would be a factual lie in telemetry when
    the operator binds a remote daemon).

    When the input is set but port is omitted, defaults to the ollama SDK
    default port 11434 (matching `AsyncOllamaClient` fallback at
    `lifecycle/providers.py:504-505`).
    """
    if host is None:
        return (None, None)
    # Strip scheme.
    remainder = host
    for scheme in ("http://", "https://"):
        if remainder.startswith(scheme):
            remainder = remainder[len(scheme) :]
            break
    # Strip path.
    if "/" in remainder:
        remainder = remainder.split("/", 1)[0]
    # Split host:port.
    if ":" in remainder:
        address, _, port_str = remainder.partition(":")
        try:
            port = int(port_str)
        except ValueError:
            return (address or None, 11434)
        return (address or None, port)
    return (remainder or None, 11434)


@dataclass(frozen=True, slots=True)
class _UsageAttrs:
    """Provider-neutral usage-attribute carrier."""

    input_tokens: int | None
    output_tokens: int | None
    response_id: str | None


@dataclass(frozen=True, slots=True)
class _AnthropicCacheAttrs:
    """Anthropic-specific cache-attribute carrier (per C-AS-14 §14.2)."""

    cache_creation_input_tokens: int | None
    cache_read_input_tokens: int | None
    cache_breakpoint_id: str | None
    cache_ttl_seconds: int | None


@dataclass(frozen=True, slots=True)
class _AnthropicRequestAttrs:
    """Anthropic request-side + model-derived attribute carrier per C-AS-14
    §14.2 rows 5-10 (the 6 non-cache attrs on the `llm.inference` span).

    Sources per Anthropic Python SDK `MessageCreateParams` shape:
    - `thinking_mode` / `thinking_budget_tokens` — `payload.params["thinking"]`
    - `thinking_effort` — beta `payload.params["output_config"]["effort"]`
    - `inference_geo` — `payload.params["inference_geo"]`
    - `batch_id` — operator-supplied marker at `payload.params["batch_id"]`
      (not in synchronous messages.create; out-of-band Batch API submission marker)
    - `tokenizer_version` — model-derived: `"v2"` for Opus 4.7+; else `"v1"` per
      spec §14.2 row "v1 (default); v2 (Opus 4.7)". Always emitted.
    """

    thinking_mode: str | None
    thinking_budget_tokens: int | None
    thinking_effort: str | None
    batch_id: str | None
    tokenizer_version: str  # always emitted; bounded enum {"v1", "v2"}
    inference_geo: str | None


def _derive_tokenizer_version(model: str) -> str:
    """Per spec §14.2 row 9 — strict reading: `v2` for Opus 4.7+; else `v1`.

    Future model families MAY warrant additional `v*` values; that surface
    extension routes through design-phase back-flow per X-AL-3.
    """
    return "v2" if model.startswith("claude-opus-4-7") else "v1"


def _extract_anthropic_request_attrs(
    payload: ProviderAgnosticPayload, model: str
) -> _AnthropicRequestAttrs:
    """Extract the 6 non-cache anthropic.* attrs from request payload + model.

    Per C-AS-14 §14.2 rows 5-10. Best-effort: payloads that don't follow the
    expected shape return `None` per-field rather than raising. Total over
    `_AnthropicRequestAttrs` field domain.
    """
    params = payload.params
    thinking_cfg = params.get("thinking")
    thinking_mode: str | None = None
    thinking_budget: int | None = None
    if isinstance(thinking_cfg, Mapping):
        cfg = cast(Mapping[str, Any], thinking_cfg)
        type_raw = cfg.get("type")
        budget_raw = cfg.get("budget_tokens")
        if isinstance(type_raw, str):
            thinking_mode = type_raw
        if isinstance(budget_raw, int) and not isinstance(budget_raw, bool):
            thinking_budget = budget_raw

    output_cfg = params.get("output_config")
    thinking_effort: str | None = None
    if isinstance(output_cfg, Mapping):
        cfg = cast(Mapping[str, Any], output_cfg)
        effort_raw = cfg.get("effort")
        if isinstance(effort_raw, str):
            thinking_effort = effort_raw

    batch_id_raw = params.get("batch_id")
    batch_id = batch_id_raw if isinstance(batch_id_raw, str) else None

    inference_geo_raw = params.get("inference_geo")
    inference_geo = inference_geo_raw if isinstance(inference_geo_raw, str) else None

    return _AnthropicRequestAttrs(
        thinking_mode=thinking_mode,
        thinking_budget_tokens=thinking_budget,
        thinking_effort=thinking_effort,
        batch_id=batch_id,
        tokenizer_version=_derive_tokenizer_version(model),
        inference_geo=inference_geo,
    )


def _payload_to_anthropic_kwargs(
    payload: ProviderAgnosticPayload, system: str | None = None
) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``messages.create`` kwargs.

    Anthropic's ``messages.create`` requires ``max_tokens``; the
    provider-neutral payload carries it in ``params``. Tools are passed
    through when present; ``params`` keys merge into the call kwargs.

    R-PM-1 PR #1 — when ``system`` (the active prompt content) is supplied,
    inject it as Anthropic's **top-level ``system=`` kwarg** (the base-system-
    prompt route per the `claude-api` reference; a ``role:"system"`` message
    entry is NOT honored as a base prompt by Anthropic). ``ProviderAgnosticPayload``
    stays frozen — the system content rides the dispatcher, never the payload —
    so cost-attribution + ``_extract_anthropic_request_attrs`` are untouched
    (ADR-F1-faithful: per-provider feature use at the call site, no provider-
    specific field lifted into the neutral record). Fail-loud if ``params``
    already carries a competing ``system`` (the opaque escape hatch).
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    if system:
        if "system" in kwargs:
            raise PromptInjectionConflictError("anthropic", 'params["system"]')
        kwargs["system"] = system
    return kwargs


def _inject_leading_system_message(
    kwargs: dict[str, Any], system: str | None, provider: str
) -> None:
    """Prepend a ``{"role":"system"}`` entry to the OpenAI/Ollama messages
    (the base-system-prompt route for these providers) when ``system`` is
    supplied — R-PM-1 PR #1. Operates on the **post-`params`-merge** ``kwargs``
    so the injection cannot be clobbered by, and any competing system source
    cannot be hidden in, a ``params["messages"]`` escape-hatch override (Codex
    review). Fail-loud (`detect-then-refuse`) if the effective messages already
    lead with a ``role:"system"`` entry (the idiomatic per-step system prompt).
    """
    if not system:
        return
    messages: list[Mapping[str, Any]] = list(kwargs.get("messages", ()))
    if messages and messages[0].get("role") == "system":
        raise PromptInjectionConflictError(provider, 'messages[0] role:"system"')
    kwargs["messages"] = [{"role": "system", "content": system}, *messages]


def _payload_to_openai_kwargs(
    payload: ProviderAgnosticPayload, system: str | None = None
) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``chat.completions.create`` kwargs.

    R-PM-1 PR #1 — ``system`` (active prompt content) injects as a leading
    ``{"role":"system","content":...}`` message (the OpenAI base-prompt route),
    **after** the ``params`` merge so a ``params["messages"]`` override cannot
    silently drop it.
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    _inject_leading_system_message(kwargs, system, "openai")
    return kwargs


def _payload_to_ollama_kwargs(
    payload: ProviderAgnosticPayload, system: str | None = None
) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``ollama.chat`` kwargs.

    R-PM-1 PR #1 — ``system`` (active prompt content) injects as a leading
    ``{"role":"system","content":...}`` message (the Ollama base-prompt route),
    **after** the ``params`` merge so a ``params["messages"]`` override cannot
    silently drop it.
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    _inject_leading_system_message(kwargs, system, "ollama")
    return kwargs


_ANTHROPIC_HITL_MAX_TOOL_TURNS = 16


def _anthropic_attr(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        return cast(Mapping[str, Any], value).get(name)
    return getattr(value, name, None)


def _anthropic_content_blocks(response: Any) -> tuple[Any, ...]:
    content = _anthropic_attr(response, "content")
    if isinstance(content, Sequence) and not isinstance(content, (str, bytes, bytearray)):
        return tuple(cast(Sequence[Any], content))
    return ()


def _anthropic_stop_reason(response: Any) -> str | None:
    value = _anthropic_attr(response, "stop_reason")
    return value if isinstance(value, str) else None


def _anthropic_block_mapping(block: Any) -> Mapping[str, Any]:
    if isinstance(block, Mapping):
        return dict(cast(Mapping[str, Any], block))
    dump = getattr(block, "model_dump", None)
    if callable(dump):
        dumped = dump()
        if isinstance(dumped, Mapping):
            return dict(cast(Mapping[str, Any], dumped))
    projected: dict[str, Any] = {}
    for name in ("type", "id", "name", "input", "text"):
        value = getattr(block, name, None)
        if value is not None:
            projected[name] = value
    return projected


def _anthropic_tool_use_blocks(response: Any) -> tuple[Any, ...]:
    if _anthropic_stop_reason(response) != "tool_use":
        return ()
    return tuple(
        block
        for block in _anthropic_content_blocks(response)
        if _anthropic_attr(block, "type") == "tool_use"
    )


def _anthropic_tool_server_for_name(
    payload: ProviderAgnosticPayload,
    tool_name: str,
) -> str:
    for tool in payload.tools or ():
        tool_mapping = _anthropic_block_mapping(tool)
        if tool_mapping.get("name") != tool_name:
            continue
        for key in ("server", "mcp_server", "server_name", "mcp_server_name"):
            value = tool_mapping.get(key)
            if isinstance(value, str) and value:
                return value
    return "anthropic"


def _model_tool_call_from_anthropic_block(
    block: Any,
    *,
    payload: ProviderAgnosticPayload,
    provider: str,
    model: str,
) -> ModelToolCall:
    tool_call_id = _anthropic_attr(block, "id")
    tool_name = _anthropic_attr(block, "name")
    arguments = _anthropic_attr(block, "input")
    if not isinstance(tool_call_id, str) or not isinstance(tool_name, str):
        raise LLMDispatchPayloadShapeError(
            "Anthropic tool_use block missing string id/name for R-CXA-2 HITL loop"
        )
    if not isinstance(arguments, Mapping):
        arguments = {}
    return ModelToolCall(
        tool_call_id=tool_call_id,
        tool=tool_name,
        server=_anthropic_tool_server_for_name(payload, tool_name),
        arguments=cast(Mapping[str, Any], arguments),
        provider=provider,
        model=model,
    )


def _hitl_loop_context_from_step(
    step_context: StepExecutionContext,
    *,
    step_id: str,
    persona_tier: PersonaTier,
) -> HITLToolLoopContext:
    actor_id = getattr(step_context.parent_actor, "actor_id", "harness-runtime")
    return HITLToolLoopContext(
        workflow_id=step_context.workflow_id,
        step_id=step_id,
        persona_tier=persona_tier,
        cell_synchrony_class=SynchronyClass.SYNC_BLOCKING,
        cross_trust_boundary_state=CrossTrustBoundaryState.NONE,
        actor=ActorIdentity(str(actor_id)),
    )


def _anthropic_tool_result_content(result: Any) -> str:
    if result is None:
        return "HITL tool loop did not return a result for this tool call."
    dispatch_result = getattr(result, "dispatch_result", None)
    if not isinstance(dispatch_result, Mapping):
        return "HITL rejected or skipped this tool call."
    dispatch_mapping = cast(Mapping[str, Any], dispatch_result)
    response_text = dispatch_mapping.get("response_text")
    if isinstance(response_text, str):
        return response_text
    return json.dumps(dict(dispatch_mapping), sort_keys=True, default=str)


def _anthropic_tool_result_block(tool_use_block: Any, result: Any) -> dict[str, Any]:
    tool_call_id = _anthropic_attr(tool_use_block, "id")
    if not isinstance(tool_call_id, str):
        raise LLMDispatchPayloadShapeError(
            "Anthropic tool_use block missing string id for tool_result continuation"
        )
    block: dict[str, Any] = {
        "type": "tool_result",
        "tool_use_id": tool_call_id,
        "content": _anthropic_tool_result_content(result),
    }
    if result is None or getattr(result, "dispatch_result", None) is None:
        block["is_error"] = True
    return block


def _anthropic_response_bundle(
    response: Any,
    payload: ProviderAgnosticPayload,
    model: str,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs, _AnthropicRequestAttrs]:
    usage = getattr(response, "usage", None)
    usage_attrs = _UsageAttrs(
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
        response_id=getattr(response, "id", None),
    )
    cache_breakpoint_id, cache_ttl_seconds = _extract_anthropic_cache_request_attrs(payload)
    cache_attrs = _AnthropicCacheAttrs(
        cache_creation_input_tokens=getattr(usage, "cache_creation_input_tokens", None),
        cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", None),
        cache_breakpoint_id=cache_breakpoint_id,
        cache_ttl_seconds=cache_ttl_seconds,
    )
    request_attrs = _extract_anthropic_request_attrs(payload, model)
    return (_response_to_mapping(response), usage_attrs, cache_attrs, request_attrs)


async def _dispatch_anthropic_with_hitl_tool_loop(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    hitl_tool_loop: RuntimeHITLToolLoop,
    step_context: StepExecutionContext,
    step_id: str,
    persona_tier: PersonaTier,
    system: str | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs, _AnthropicRequestAttrs]:
    """Anthropic provider branch with generic R-CXA-2 HITL tool continuation.

    Non-memory Anthropic ``tool_use`` blocks are adapted into provider-neutral
    ``ModelToolCall`` values, processed by the bound ``RuntimeHITLToolLoop``,
    and then returned to Anthropic as ``tool_result`` blocks for continuation.

    R-PM-1 PR #1 — ``system`` (active prompt content) injects as the Anthropic
    ``system=`` top-level kwarg; it persists across continuation turns (the
    mutable ``messages`` list is rebuilt per turn, but ``system`` is a separate
    kwarg).
    """
    kwargs = _payload_to_anthropic_kwargs(payload, system)
    messages = list(payload.messages)
    kwargs["messages"] = messages
    context = _hitl_loop_context_from_step(
        step_context,
        step_id=step_id,
        persona_tier=persona_tier,
    )

    for _turn_index in range(_ANTHROPIC_HITL_MAX_TOOL_TURNS):
        response = await adapter.client.messages.create(model=model, **kwargs)
        tool_use_blocks = _anthropic_tool_use_blocks(response)
        if not tool_use_blocks:
            return _anthropic_response_bundle(response, payload, model)

        calls = tuple(
            _model_tool_call_from_anthropic_block(
                block,
                payload=payload,
                provider="anthropic",
                model=model,
            )
            for block in tool_use_blocks
        )
        results = await hitl_tool_loop.run_tool_calls(calls, context)
        result_by_id = {result.tool_call_id: result for result in results}

        messages.append(
            {
                "role": "assistant",
                "content": [
                    dict(_anthropic_block_mapping(block))
                    for block in _anthropic_content_blocks(response)
                ],
            }
        )
        messages.append(
            {
                "role": "user",
                "content": [
                    _anthropic_tool_result_block(
                        block,
                        result_by_id.get(cast(str, _anthropic_attr(block, "id"))),
                    )
                    for block in tool_use_blocks
                ],
            }
        )

    raise RuntimeError(
        "Anthropic R-CXA-2 HITL tool loop exceeded "
        f"{_ANTHROPIC_HITL_MAX_TOOL_TURNS} continuation turns"
    )


async def _dispatch_anthropic_with_memory(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    registry: Any,
    deployment_surface: Any,
    tracer: Any,
    system: str | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs, _AnthropicRequestAttrs]:
    """Anthropic provider branch with Memory tool inner loop (U-RT-81).

    Per spec v1.17 §14.5.1 mechanism β + AS spec v1.5 §14.7 memory.*
    namespace emission. Resolves the storage backend via the registry,
    derives `memory.context_editing_active`, then defers to
    `execute_with_memory_callbacks` for the inner tool-use loop.

    `MemoryPathViolationError` / `MemoryCallbackIOError` propagate
    VERBATIM through this helper to the C-RT-15 dispatcher boundary →
    driver `try/except` at `workflow_driver.py:618-635` per spec §14.5.1
    step 5.
    """
    backend = registry.resolve_backend(deployment_surface)
    configured_backend = registry.configured_backend
    context_editing_active = derive_context_editing_active(payload.params)
    kwargs = _payload_to_anthropic_kwargs(payload, system)

    response = await execute_with_memory_callbacks(
        adapter=adapter,
        model=model,
        messages_create_kwargs=kwargs,
        backend=backend,
        backend_enum=configured_backend,
        tracer=tracer,
        context_editing_active=context_editing_active,
    )

    return _anthropic_response_bundle(response, payload, model)


async def _dispatch_anthropic(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs, _AnthropicRequestAttrs]:
    """Anthropic provider branch — ``client.messages.create(...)``."""
    kwargs = _payload_to_anthropic_kwargs(payload, system)
    response = await adapter.client.messages.create(model=model, **kwargs)

    return _anthropic_response_bundle(response, payload, model)


async def _dispatch_openai(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """OpenAI provider branch — ``client.chat.completions.create(...)``."""
    kwargs = _payload_to_openai_kwargs(payload, system)
    response = await adapter.client.chat.completions.create(model=model, **kwargs)

    usage = getattr(response, "usage", None)
    usage_attrs = _UsageAttrs(
        input_tokens=getattr(usage, "prompt_tokens", None),
        output_tokens=getattr(usage, "completion_tokens", None),
        response_id=getattr(response, "id", None),
    )
    return (_response_to_mapping(response), usage_attrs)


async def _dispatch_ollama(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """Ollama provider branch — ``client.chat(...)``.

    Ollama's ``ChatResponse`` exposes ``prompt_eval_count`` / ``eval_count``
    instead of a nested ``usage`` object; no ``response_id``.
    """
    kwargs = _payload_to_ollama_kwargs(payload, system)
    response = await adapter.client.chat(model=model, **kwargs)

    usage_attrs = _UsageAttrs(
        input_tokens=getattr(response, "prompt_eval_count", None),
        output_tokens=getattr(response, "eval_count", None),
        response_id=None,
    )
    return (_response_to_mapping(response), usage_attrs)


def _response_to_mapping(response: Any) -> Mapping[str, Any]:
    """Coerce a provider response to ``Mapping[str, Any]``.

    All three provider SDKs return pydantic v2 models from their
    chat/messages methods, so ``model_dump()`` is uniformly available.
    Falls back to passing through Mapping instances for hand-rolled
    test stubs.
    """
    dump = getattr(response, "model_dump", None)
    if callable(dump):
        result = cast(Any, dump())
        if isinstance(result, Mapping):
            return cast(Mapping[str, Any], result)
    if isinstance(response, Mapping):
        return cast(Mapping[str, Any], response)
    raise LLMDispatchPayloadShapeError(
        f"provider response not coercible to Mapping[str, Any]: {type(response)!r}"
    )


def _attribute_cost_best_effort(
    *,
    span: Any,
    cost_chain: Any,
    audit_writer: Any,
    rate_table: Any,
    provider_name: str,
    model: str,
    parent_idempotency_key: str,
    workflow_id: str,
    parent_action_id: str,
    input_tokens: int | None,
    output_tokens: int | None,
    cache_creation: int | None,
    cache_read: int | None,
    tenant_id: str | None,
) -> None:
    """Best-effort cost-attribution invocation per §C-OD-26.1 (U-OD-38).

    Calls `attribute_llm_dispatch_cost`. On success, emits the
    cost.attributed_decimal OTel attribute on the current dispatch span via
    U-OD-49 string-form. On failure (rate-table missing OR upstream cost
    chain failure), swallows the exception — cost-attribution is observability,
    not contract, and MUST NOT fail the dispatch (AC #1: invoked on every
    dispatch, success + failure paths). Future hardening: per-provider
    "raise" config flag per §C-OD-28.2 fail-closed default; not at v1 MVP
    scope for the dispatch-side wrapper.
    """
    # Defer imports to module-load time at call-site to keep llm_dispatch.py's
    # cold import surface narrow (cost-attribution path pulls OD + CXA types
    # transitively).
    from decimal import Decimal

    from harness_od.cost_record_otel_serializer import (
        COST_ATTRIBUTED_DECIMAL_ATTR,
        serialize_decimal_for_otel,
    )

    from harness_runtime.lifecycle.cost_attribution_llm_dispatch import (
        attribute_llm_dispatch_cost,
    )

    if cost_chain is None or audit_writer is None or rate_table is None:
        # Cost-attribution substrate not bound — unit-test path (production
        # bootstrap stage 5 enforces all 3 substrates are present).
        return
    if input_tokens is None or output_tokens is None:
        # No usage attrs from provider — cost is undefined. Skip silently.
        return

    span_context = span.get_span_context()
    span_id_hex = format(span_context.span_id, "016x")

    try:
        attached = attribute_llm_dispatch_cost(
            rate_table=rate_table,
            cost_chain=cost_chain,
            audit_writer=audit_writer,
            provider_name=provider_name,
            model=model,
            span_id=span_id_hex,
            parent_idempotency_key=parent_idempotency_key,
            workflow_id=workflow_id,
            parent_action_id=parent_action_id,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            cache_creation=int(cache_creation) if cache_creation is not None else 0,
            cache_read=int(cache_read) if cache_read is not None else 0,
            tenant_id=tenant_id,
        )
    except Exception:
        # Cost-attribution is observability, not contract. Swallow.
        return

    # Emit cost.attributed_decimal OTel attribute via U-OD-49 string-form
    # preserving the float→Decimal serialization at the OTel boundary.
    span.set_attribute(
        COST_ATTRIBUTED_DECIMAL_ATTR,
        serialize_decimal_for_otel(Decimal(str(attached.total_cost))),
    )


def materialize_llm_dispatcher_stage(
    providers: _ProvidersLike,
    tracer_provider: _TracerProviderLike,
    *,
    cost_chain: Any = None,
    audit_writer: Any = None,
    rate_table: Any = None,
    memory_tool_registry: Any = None,
    deployment_surface: Any = None,
    hitl_tool_loop: RuntimeHITLToolLoop | None = None,
    ollama_host: str | None = None,
    skill_activation_emitter: Any = None,
    skills: Any = None,
    routing_manifest: RoutingManifest | None = None,
    workload_class: WorkloadClass | None = None,
    persona_tier: PersonaTier | None = None,
    active_system_prompt: str | None = None,
) -> RuntimeLLMDispatcher:
    """Stage 5 LOOP_INIT composer factory for the LLM dispatcher (U-RT-52).

    U-OD-38 extension: cost-attribution substrate (cost_chain + audit_writer +
    rate_table) is required at composer construction. The stage caller
    (bootstrap stage 5) sources from `ctx.cost_chain` (stage 4 OD) +
    `ctx.audit_writer` (stage 4 OD) + `ctx.rate_table` (stage 4 OD or
    bootstrap config).

    Raises
    ------
    LLMDispatchBindError
        If the providers map is empty (no providers registered at
        stage 3a — would indicate either Ollama-degraded + non-optional
        anthropic/openai failure path OR a bootstrap-orchestrator bug).
    """
    if len(providers) == 0:
        raise LLMDispatchBindError(
            "No providers registered at stage 3a — cannot bind LLM dispatcher at stage 5"
        )

    return RuntimeLLMDispatcher(
        providers=providers,
        tracer_provider=tracer_provider,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        rate_table=rate_table,
        memory_tool_registry=memory_tool_registry,
        deployment_surface=deployment_surface,
        hitl_tool_loop=hitl_tool_loop,
        ollama_host=ollama_host,
        skill_activation_emitter=skill_activation_emitter,
        skills=skills,
        routing_manifest=routing_manifest,
        workload_class=workload_class,
        persona_tier=persona_tier,
        active_system_prompt=active_system_prompt,
    )


__all__ = [
    "LLMDispatchBindError",
    "LLMDispatchPayloadShapeError",
    "LLMDispatchProviderUnreachableError",
    "PromptInjectionConflictError",
    "RuntimeLLMDispatcher",
    "materialize_llm_dispatcher_stage",
]

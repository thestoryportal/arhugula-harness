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

import asyncio
import hashlib
import json
import logging
import re
from collections.abc import Mapping, Sequence
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Final, Protocol, cast, runtime_checkable

from harness_as.memory_tool_contracts import MEMORY_TOOL_CONTRACTS, MemoryToolName
from harness_core import PersonaTier, WorkloadClass
from harness_cp.cp_shared_types import (
    ActorIdentity,
    AgentRole,
    ModelBinding,
    ProviderAgnosticPayload,
    RoutingDecisionTrace,
    TraceContext,
)
from harness_cp.engine_class import EngineClass
from harness_cp.layer_budget import DEFAULT_LAYER_BUDGETS, LayerBudget
from harness_cp.layered_routing_strategy import LayerDecisionFn
from harness_cp.memory_access_mode import MemoryAccessMode
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.persona_engine_hitl_matrix import SynchronyClass
from harness_cp.routing_core_surface import (
    InferenceRequest,
    ProviderDispatchResult,
    RouterResolutionFn,
    infer,
    resolve_routing_trace,
)
from harness_cp.routing_layer import RoutingLayer
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.validator_fail_transient_staircase import CrossTrustBoundaryState
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.memory_observability import (
    MemoryTelemetryOperationName,
    memory_telemetry_span,
)
from harness_is.memory_operation_ledger import MemoryOperationKind
from harness_od.otel_genai_base import HIERARCHY_CORRELATION_KEY, GenAiOperation

from harness_runtime.lifecycle.audit_offload import (
    resolve_result_ref_off_loop,
    run_audit_off_loop,
)
from harness_runtime.lifecycle.audit_signing_errors import (
    AUDIT_SIGNING_HARD_FAILURES,
    PostEffectAuditSigningError,
    PostEffectClass,
)
from harness_runtime.lifecycle.cacheable_epoch import DEFAULT_CACHE_TTL, CacheTTL
from harness_runtime.lifecycle.cost_record_sink import SupportsCostRecordAppend
from harness_runtime.lifecycle.cross_family_cost_tag import provider_family_for_scope_check
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
from harness_runtime.memory_context import (
    RenderedMemoryPromptPacket,
    RuntimeMemoryContext,
    append_rendered_memory_packet,
    compose_system_prompt_with_memory_packet,
    render_packet_for_degraded_dispatch,
)
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionInputError,
    MemoryToolExecutionRequest,
)


@dataclass(frozen=True, slots=True)
class RoutedPrimaryResolution:
    """The B-L2-FALLBACK-COMPOSITION routed-primary resolution (§14.6.1).

    `resolve_routed_binding` returns this when the layered routing
    (DECLARATIVE-decline → EMBEDDING → L3) picks a model: the routed
    ``model_binding`` the C-RT-16 wrapper seeds as its chain PRIMARY, PLUS the
    ``routing_trace`` (the real EMBEDDING/L3 layer + candidate) and
    ``binding_rationale`` that B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION threads to the
    inner `gen_ai` span for the routed-primary dispatch (§14.6.1 scope-boundary
    closure). The wrapper reads ``model_binding`` for chain composition; the
    trace + rationale ride `ROUTED_PRIMARY_SPAN_TRACE` to the span emitter.
    """

    model_binding: ModelBinding
    routing_trace: RoutingDecisionTrace
    binding_rationale: str | None


# B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION (§14.6.1 scope-boundary closure). Under
# `routing_activation` the C-RT-16 wrapper resolves the layered-routing decision
# ONCE (route-once-then-fallback) and reverts the inner C-RT-15 dispatcher to a
# FAITHFUL DECLARATIVE echo — so the inner's `gen_ai` span would carry the echo
# `routing.layer`, not the real EMBEDDING/L3 layer the wrapper used. The wrapper
# publishes the real `(routing_trace, binding_rationale)` here for the
# routed-PRIMARY dispatch ONLY (cleared for fallback candidates, which ARE
# faithful); `_invoke_provider` reads it for `routing.layer`/`binding_rationale`.
# A ContextVar (not an instance attribute) because the C-RT-15 dispatcher is
# shared across concurrent fan-out branches — the per-task isolation mirrors the
# B-INTERSTEP-PERRUN-ISOLATION (v1.64) precedent. Default/absent (routing off,
# non-routed, or any direct non-wrapper dispatch) → the local echo trace, so the
# pre-arc span attribution is byte-identical.
ROUTED_PRIMARY_SPAN_TRACE: ContextVar[tuple[RoutingDecisionTrace, str | None] | None] = ContextVar(
    "_routed_primary_span_trace", default=None
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
class _ExternalCLIProviderLike(Protocol):
    """Provider shape for text-only local CLI adapters."""

    async def dispatch_text(self, *, model: str, prompt: str) -> Any: ...


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


_UPSTREAM_CONTEXT_PREFIX = "Upstream step output:\n"
"""Label prefixing the B-INTERSTEP upstream-output context message (runtime spec
§14.21 C-RT-34). Lets a model (and a test) distinguish the injected prior-step
output from the step's own messages."""


def _inject_upstream_context_message(
    kwargs: dict[str, Any], upstream: Mapping[str, Any] | None
) -> None:
    """Insert the immediately-prior step's output as an upstream-context ``user``
    message into the FINAL provider ``kwargs["messages"]``, AFTER any leading
    ``role:"system"`` message.

    B-INTERSTEP (runtime spec §14.21 C-RT-34). Operating on the final kwargs (NOT
    ``payload.messages``) is load-bearing, and mirrors the R-PM-1 system-prompt
    post-`params` injection: it runs AFTER ``kwargs.update(payload.params)`` so a
    ``params["messages"]`` escape-hatch override cannot silently drop it, and AFTER
    ``_inject_leading_system_message`` so the upstream ``user`` message does not
    push a conflicting payload-leading ``system`` message off index 0 and mask the
    competing-system-source conflict check (Codex review). The dispatcher does NOT
    introspect the step body — it carries the driver-recorded output opaquely
    (`workflow_driver` §25.3.3.4 preserved); ``default=str`` keeps a non-JSON-native
    value serializable + ``sort_keys`` keeps the injected content deterministic.
    ``None`` (opt-out / empty channel) → no-op (byte-identical to pre-v1.59).
    """
    if upstream is None:
        return
    messages: list[Mapping[str, Any]] = list(kwargs.get("messages", ()))
    context_message: dict[str, Any] = {
        "role": "user",
        "content": _UPSTREAM_CONTEXT_PREFIX
        + json.dumps(dict(upstream), sort_keys=True, default=str),
    }
    insert_at = 1 if messages and messages[0].get("role") == "system" else 0
    kwargs["messages"] = [*messages[:insert_at], context_message, *messages[insert_at:]]


def _set_if_present(span: Any, key: str, value: Any) -> None:
    """Set a span attribute only when the value is not ``None``.

    OTel allows ``None`` as a value but the GenAI semconv discourages
    emitting attributes whose value is unknown. This helper keeps the
    per-provider attribute extraction code uncluttered.
    """
    if value is not None:
        span.set_attribute(key, value)


def _cache_control_ttl_seconds(cache_control: Mapping[str, Any]) -> int | None:
    """Translate an Anthropic ``cache_control.ttl`` label to seconds.

    ``"5m"`` → 300; ``"1h"`` → 3600; absent ttl → 300 (Anthropic's
    default when a ``cache_control`` directive is present without an
    explicit ttl); unrecognized label → ``None``.
    """
    ttl_label = cast(Any, cache_control.get("ttl"))
    if ttl_label == "1h":
        return 3600
    if ttl_label == "5m":
        return 300
    if ttl_label is None:
        return 300  # Anthropic default
    return None


def _first_cache_control_in_blocks(blocks: object) -> Mapping[str, Any] | None:
    """Return the first block-level ``cache_control`` mapping in a content-block
    list (a ``tools`` list, the structured ``system`` content-block array, or a
    message's ``content`` list), else ``None``.

    Non-list shapes (e.g. a plain-string ``system``) return ``None`` — they
    carry no block-level ``cache_control`` directive.
    """
    if not isinstance(blocks, list):
        return None
    for block in cast(list[Any], blocks):
        if not isinstance(block, Mapping):
            continue
        cache_control = cast(Any, cast(Mapping[str, Any], block).get("cache_control"))
        if isinstance(cache_control, Mapping):
            return cast(Mapping[str, Any], cache_control)
    return None


def _extract_anthropic_cache_request_attrs(
    request_kwargs: Mapping[str, Any],
) -> tuple[str | None, int | None]:
    """Extract ``anthropic.cache_breakpoint_id`` + ``anthropic.cache_ttl_seconds``
    from the TRANSLATED wire kwargs' ``cache_control`` directives, if present.

    Anthropic honors ``cache_control`` on ``tools`` blocks, the structured
    ``system`` content-block array, and ``messages`` content blocks, cached in
    that prefix order (``tools → system → messages``). The U-1 (B-18) cache
    breakpoint lands on the tools block (slice 1 / 3a) or the system block
    (slice 2), and is placed at TRANSLATE time on the wire kwargs — never on the
    frozen ``ProviderAgnosticPayload``. Scanning the wire kwargs (rather than
    ``payload.messages``, the pre-B-18 source) is therefore the single source of
    truth for what was actually sent, and records the tools/system breakpoint the
    messages-only scan missed (closes B-18-CACHE-TTL-OBSERVABILITY uniformly for
    slices 1/2/3a/3b).

    Returns the breakpoint position id (``"tools"`` / ``"system"`` /
    ``"msg-{index}"``) + the ttl in seconds for the FIRST cache_control-bearing
    position in prefix order, or ``(None, None)`` when no directive is present.
    Per C-AS-14 §14.2 these attributes are low-cardinality (≤4 breakpoints;
    binary ttl). Best-effort: shapes that don't follow the convention return
    ``(None, None)`` rather than raising.
    """
    tools_cc = _first_cache_control_in_blocks(request_kwargs.get("tools"))
    if tools_cc is not None:
        return ("tools", _cache_control_ttl_seconds(tools_cc))
    system_cc = _first_cache_control_in_blocks(request_kwargs.get("system"))
    if system_cc is not None:
        return ("system", _cache_control_ttl_seconds(system_cc))
    messages = request_kwargs.get("messages")
    if isinstance(messages, list):
        for index, message in enumerate(cast(list[Any], messages)):
            if not isinstance(message, Mapping):
                continue
            message_cc = _first_cache_control_in_blocks(
                cast(Mapping[str, Any], message).get("content")
            )
            if message_cc is not None:
                return (f"msg-{index}", _cache_control_ttl_seconds(message_cc))
    return (None, None)


# Routing-envelope defaults. The DECLARATIVE-echo layer decision (see
# `RuntimeLLMDispatcher.dispatch`) echoes the resolved `binding.model_binding` and
# ignores the InferenceRequest discriminators, so those envelope fields are
# carried-but-not-selection-driving on the echo path.
#
# CORRECTED 2026-07-27 — this comment previously added "no per-step role is
# threaded through the execution path at v1.6 (WorkflowStep carries only
# step_id/step_kind/step_payload) ... they become load-bearing at
# R-300-second-provider". FALSE at HEAD, and that arc itself RESOLVED 2026-06-03.
# A per-step role IS threaded (`StepExecutionContext.agent_role`) and IS indexed:
# per-role MODEL at `retry_breaker_fallback._effective_chain`'s per-role branch
# (unconditional) and per-role PROMPT at `dispatch`'s `per_role_system_prompts`
# lookup (R-FS-1 arc B4 / U-RT-114, runtime spec §14.5.3). This constant is the
# DEFAULT-role fall-through key, which both indexers deliberately exclude to keep
# the unbound/linear path byte-identical — not a stand-in for a missing dimension.
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


def _declarative_decline(
    _payload: ProviderAgnosticPayload, _manifest: RoutingManifest
) -> str | None:
    """A DECLARATIVE layer-decision that always DECLINES (returns ``None``).

    Used by `RuntimeLLMDispatcher.resolve_routed_binding`
    (B-L2-FALLBACK-COMPOSITION) AFTER its deterministic-binding check has
    established the request has NO deterministic binding — so DECLARATIVE must
    fall through to the EMBEDDING classifier (then the L3 router) per C-CP-02
    §2.2. A typed module-level function (not a lambda) keeps it pyright-clean
    against the ``LayerDecisionFn`` signature."""
    return None


class PrewarmOutcome(StrEnum):
    """Result of `RuntimeLLMDispatcher.prewarm()` (B-18-KEEPALIVE; ADR-D3 §1.5:189).

    Used by the keep-alive self-disable counter and test assertions.
    """

    WARMED = "warmed"
    """One `max_tokens=1` Anthropic call fired; cache breakpoint established."""
    SKIPPED_NOT_ELIGIBLE = "skipped_not_eligible"
    """No cacheable prefix or no resolved Anthropic model — no paid call made."""
    SKIPPED_NO_ANTHROPIC = "skipped_no_anthropic"
    """Anthropic adapter absent from `providers` — no paid call made."""
    SKIPPED_POLICY_FAIL_CLOSED = "skipped_policy_fail_closed"
    """U-RT-135 (Runtime spec v1.101 surface C; OD v1.34 §21.2.3 row 8):
    `audit_signing_fail_closed` resolved ON at MULTI_TENANT_COMPLIANCE —
    prewarm is a latency optimization whose swallow-all posture is a
    fail-open bypass at the compliance tier, so no paid call is made. A
    POLICY skip, not a `FAILED` outcome: it MUST NOT count toward the
    keepalive `consec_fail` self-disable accounting."""
    FAILED = "failed"
    """Provider call raised; exception swallowed (best-effort); no retry."""


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
    # B-23 — IS state-ledger writer (U-RT-12) + R-003 resolver, threaded to
    # `_attribute_cost_best_effort` so the per-dispatch cost-attribution audit
    # entry's `entry_core` is a real F2 anchor instead of a fabricated
    # `cp-audit:<action_id>` marker. None preserves unit-test ergonomics.
    ledger_writer: Any = None
    procedural_tier_snapshot_resolver: Any = None
    # B-47 PR B2a — OD spec v1.33 §21.2.1 signing-backend seam, threaded from
    # `ctx.audit_signing_backend` by `materialize_llm_dispatcher_stage`. None
    # (unit-test ergonomics) preserves the placeholder signing path.
    signing_backend: Any = None
    # R-FS-1 arc CA — run-scoped cost-record sink (the SAME list as
    # `ctx.cost_record_accumulator`, threaded by `materialize_llm_dispatcher_stage`
    # from the mutable bootstrap ctx). `_attribute_cost_best_effort` appends each
    # dispatch's returned `SpanCostRecord` so `_build_run_result` can roll up
    # `RunResult.cost_attribution` (runtime spec v1.53 §9 C-RT-09). None at unit-test
    # construction → the wrapper skips the append (no-op).
    cost_record_sink: SupportsCostRecordAppend | None = None
    # B-INTERSTEP (runtime spec §14.21 C-RT-34) — run-scoped inter-step output
    # channel (the SAME `InterStepOutputChannel` instance the CP driver records
    # into, threaded by `materialize_llm_dispatcher_stage` from the mutable
    # bootstrap ctx). When bound + non-empty, `dispatch` injects the
    # immediately-prior step's output (`most_recent_output()`) into the dispatched
    # payload as a prepended upstream-context message. None (opt-out / unit-test
    # construction) → no injection (byte-identical to pre-v1.59). Typed `Any` so
    # the dataclass field carries no import dependency on the concrete holder.
    inter_step_channel: Any = None
    # B-LAYER-BUDGET-OVERRIDE (CP spec v1.43 §2.5.3 / §3.1) — the per-layer
    # time budgets threaded to `infer()`. The L3 router timeout honors the §3.1
    # per-workload-class / per-persona-tier override carried on these budgets
    # (resolved against the request's `workload_class` + `persona_tier`). This
    # is the DORMANT threading seam: production stage-5 leaves it at the
    # `DEFAULT_LAYER_BUDGETS` default (no override surface is wired today, and
    # production never reaches L3 — `router=None` + DECLARATIVE always resolves),
    # so the override path is capability-built + production-dormant behind the
    # (UNOWNED) routing-activation gate. A test / future operator-config binding
    # supplies an override-bearing tuple. Default is the module-global immutable
    # tuple → byte-identical to the prior hardcoded `infer(budgets=...)`.
    budgets: tuple[LayerBudget, ...] = DEFAULT_LAYER_BUDGETS
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
    # U-1 (B-18) — the deterministic frozen tool superset for the Anthropic
    # prompt-cache `cache_control` breakpoint (ADR-D3 §1.5 slice 1). Bound at
    # stage-5 (top-level dispatch only, single-privilege-tier per the C10
    # blast-radius verdict) to the union of every `ctx.mcp_client_hosts[*].
    # tool_registry` contract projected to Anthropic `{name, description,
    # input_schema}`, deterministically ordered (+ memory tool when applicable).
    # None → byte-identical legacy path (`payload.tools` on the wire; no
    # breakpoint). The Anthropic translate seam replaces `payload.tools` with
    # this superset and marks its last block when the ≥4096-tok non-vacuity
    # gate clears + extended-thinking is off. Sub-agent / downgraded dispatchers
    # inherit None (fail-safe) → they fall back to `payload.tools`.
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None
    # U-1 slice 3a (B-18) — the DESCENDED sub-agent (child) frozen tool superset:
    # the ADR-D4 §1.5 default-downgrade REMOVE half applied to the SAME
    # `ctx.mcp_client_hosts` union (external-irreversible tools omitted; the
    # `compute_frozen_tool_superset(..., remove_tiers={EXTERNAL_IRREVERSIBLE})`
    # result, bound alongside `frozen_tool_superset` at stage 5). `dispatch()`
    # selects THIS superset when `step_context.sub_agent_descent` is True (a
    # child-workflow inference step), closing the F1 latent C10 condition-2 gap
    # (a sub-agent inference must NOT emit the parent's external-irreversible
    # tools into its inference context). `None` when the child union is empty
    # (no non-removed MCP tools + no memory) → fall back to `payload.tools`.
    # At MVP both supersets are `None` (no MCP tools) → byte-identical.
    child_frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None
    # U-1 slice 3b (B-18) — the Anthropic prompt-cache ttl for this run (ADR-D3
    # §1.5 line 188 `ttl: 5min default; 1hr at Persona §6 cost-ceiling cells`).
    # A run-scoped constant selected at stage 5 from the run's `workload_class` +
    # `RuntimeConfig.prompt_cache_long_ttl_workloads` (see `cacheable_epoch.
    # select_cache_ttl`); consumed at the translate seam where the `cache_control`
    # breakpoint is placed (tools OR system block). `"5m"` (the default) is
    # byte-identical to pre-slice-3b. Orthogonal to WHICH block is marked (slice
    # 1/2) and to the superset CONTENT (slice 3a) — it only sets the ttl value.
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL
    # U-MEM-15 — prompt-extension memory fallback context. When C-MEM-13 selects
    # `PROMPT_EXTENSION_PACKET`, the dispatcher renders the C-MEM-12 packet as
    # read-only system content and composes it into the existing provider prompt
    # seam. Other access modes leave the prompt byte-identical.
    memory_context: RuntimeMemoryContext | None = None
    # U-MEM-16 — provider-neutral standard memory tool executor. When C-MEM-13
    # selects STANDARD_MEMORY_TOOLS for a non-native provider, OpenAI tool-call
    # continuation dispatches memory.* calls through this executor under policy.
    # None preserves the pre-U-MEM-16 one-shot OpenAI path.
    standard_memory_tool_executor: Any = None
    # Automatic local memory substrate. When bound, each dispatch composes a
    # fresh memory context from the current model binding and step context.
    memory_runtime: Any = None
    fallback_chain: Any = None
    # R-FS-1 arc B4 (§14.5.3) — per-role PROMPT map: branch `AgentRole` → its
    # resolved system-prompt content, pre-resolved at bootstrap stage 0 (where the
    # fail-loud store-membership + binding-tier governance checks fire — before
    # this dispatcher is constructed) and bound here. The DEFAULT role is
    # deliberately EXCLUDED (it IS `active_system_prompt`), so an empty/no-per-role
    # catalog leaves this `{}` and every dispatch falls through to
    # `active_system_prompt` (byte-identical to pre-B4). Indexed per-call at
    # `dispatch()` via the branch role (NOT stashed on self — the dispatcher is
    # shared across concurrent fan-out branches).
    per_role_system_prompts: Mapping[AgentRole, str] = field(
        default_factory=lambda: dict[AgentRole, str](),
    )
    # R-FS-1 arc B4 Slice 3 (CP spec v1.37 §6.1) — per-step PROMPT override
    # support. The IS `PromptManifest.versions` content-addressed store projected
    # to `{version_sha: content}`, built at bootstrap stage 5 from
    # `ctx.prompt_manifest.versions`. A per-step binding's `prompt_version_sha`
    # (`StepEffectiveBinding`, set by CP `resolve_step_binding`) is resolved
    # against this map at dispatch with precedence **per-step > per-role >
    # run-level default**; fail-loud (`RT-FAIL-PROMPT-SELECTION-UNAUTHORED`) if
    # the sha is not an authored store member. Empty (`{}`) when no store /
    # no per-step overrides — every dispatch falls through unchanged (pre-Slice-3
    # behavior verbatim). Keyed by content-addressed sha (not stashed per-call;
    # the per-step value flows via the binding param, not on self).
    prompt_versions_by_sha: Mapping[str, str] = field(
        default_factory=lambda: dict[str, str](),
    )
    # Binding-tier prompt governance parity (OD spec C-OD-34): a per-step prompt
    # activated at a binding tier (team-binding / multi-tenant) must be
    # operator-approved, else fail-loud (`RT-FAIL-PROMPT-VERSION-UNAPPROVED`) —
    # closing the gap where a per-step override could otherwise bypass the
    # approval the per-role/default paths enforce at bootstrap. Threaded from
    # `RuntimeConfig.approved_prompt_version_shas` at stage 5; the gate is inert
    # at the solo-developer tier (no approval required) per `resolve_prompt_governance`.
    approved_prompt_version_shas: frozenset[str] = frozenset()
    # C-CP-02 §2.5 (R-impl-1) / U-RT-133 — the injected Layer-3
    # router-resolution callable.
    # Production binds None: the Layer-3 surface stays inert (DECLARATIVE
    # resolves all production traffic; no router is injected until R-impl-2
    # binds a real router model). A test fixture injects a mock RouterResolutionFn
    # (+ `layer_decisions_override` below to force the L3 sentinel) to exercise
    # the spec-§2.5.5 runtime fall-through->router e2e.
    router: RouterResolutionFn | None = None
    # Test-only seam (C-CP-02 §2.5.5 runtime e2e): override the layer-decision
    # map threaded into `infer`. None -> the production
    # `{RoutingLayer.DECLARATIVE: _declarative_echo}` (byte-identical). A test
    # injects e.g. `{RoutingLayer.DECLARATIVE: lambda *_: None}` to force the
    # `route()` L3 sentinel so the injected `router` is reached. NOT a production
    # override; production never sets it (the factory leaves it None).
    layer_decisions_override: Mapping[RoutingLayer, LayerDecisionFn] | None = None
    # C-CP-02 §2.1/§2.4 (R-FS-1 L2 — Option B) — the injected Layer-2 EMBEDDING
    # decision fn (a sync k-NN embedding classifier; built by
    # `embedding_resolution.make_embedding_classifier` over an injected light
    # in-process `EmbeddingFn` + a trained corpus). When set, it is bound at the
    # EMBEDDING layer of the production `layer_decisions` map below. Production
    # leaves it None: like the Layer-3 `router`, the Layer-2 surface stays
    # production-inert until R-300-second-provider makes DECLARATIVE conditional
    # (DECLARATIVE always echoes today, so `route()` short-circuits before
    # EMBEDDING). A test reaches it via `layer_decisions_override` (binding the
    # classifier at EMBEDDING + omitting DECLARATIVE).
    embedding_classifier: LayerDecisionFn | None = None
    # B-L2-EMBEDDING-ACTIVATION (C-CP-02 §2.2 — the routing-activation gate) — when
    # True, the DECLARATIVE layer is §2.2-FAITHFUL: it resolves the effective binding
    # ONLY when the routing manifest binds the request's tuple (`agent_role ∈
    # per_role_bindings` OR `workload_class ∈ per_workload_overrides`); otherwise it
    # DECLINES (returns None) so `route()` falls through to the EMBEDDING classifier
    # (then LLM_AS_ROUTER) — the cheapest-deterministic-first §2.2 contract. False
    # (default) → the #213 MVP behavior-preserving echo (DECLARATIVE always resolves)
    # → byte-identical, ZERO blast radius. Threaded from `RuntimeConfig.routing_
    # activation` at stage 5. HIGHEST-blast-radius opt-in (changes which model serves
    # a workload); flag-on assumes a bound `embedding_classifier` as the fall-through
    # target — the production factory (`materialize_llm_dispatcher_stage`) builds one
    # (or fail-louds on a missing `[embedding]` extra), so production is safe; a
    # DIRECT construction with flag-on but no classifier would let a manifest-miss
    # fall through EMBEDDING (empty) → L3 (`router=None`) → a dispatch raise.
    routing_activation: bool = False
    # B-18-KEEPALIVE — Anthropic model string for prewarm/keep-alive pings.
    # Threaded at stage 5 from `RuntimeConfig.prompt_cache_prewarm_model`; also
    # derived from `routing_manifest.per_workload_overrides` as the first-priority
    # resolution source in `prewarm()`. File/CLI-only on RuntimeConfig (not env-
    # keyed — does not gate correctness, only which model is warmed).
    prewarm_model: str | None = None
    # U-RT-135 (Runtime spec v1.101 surface C) — the MTC fail-closed policy
    # disable, bound at stage 5 from `mtc_audit_prewarm_disabled(config)`
    # (persona_tier == MULTI_TENANT_COMPLIANCE AND the resolved
    # `audit_signing_fail_closed` is ON). When True, `prewarm()` returns the
    # POLICY skip before any eligibility gate — no paid call, ever. Default
    # False preserves the v1.99 posture byte-for-byte everywhere else.
    prewarm_policy_fail_closed: bool = False
    # U-RT-136 (Runtime spec v1.101 surface D) — the RESOLVED OD v1.34
    # §21.2.3 `audit_signing_fail_closed` policy, bound at stage 5 from
    # `resolve_audit_signing_fail_closed(config)`. ON → a post-provider-call
    # signing failure raises the result-preserving carrier instead of
    # proceeding with the signed record omitted. Default False byte-preserves
    # the loudly-surfaced (ERROR-logged) proceed behavior at both catch
    # sites. NOT consulted at `prewarm()`'s cost-attribution call — the
    # lower-tier prewarm disposition is held at B-55 (fork gate item 8
    # decided MTC-scoped only; MTC+ON never reaches prewarm per U-RT-135).
    audit_signing_fail_closed: bool = False
    # B-65-A (Runtime spec v1.103 §14.8.11; RATIFIED B-65 Class 2 fork §3b) —
    # the protected post-effect result store, threaded from `ctx.
    # protected_result_store` at stage 5. `None` preserves unit-test
    # ergonomics (the raise-site helper `resolve_result_ref` degrades to an
    # `UnresolvableResultRef` naming the missing store, never a second
    # unrelated error) — production wiring always injects a real instance.
    protected_result_store: Any = None

    async def prewarm(self) -> PrewarmOutcome:
        """Boot-time prompt-cache pre-warm (B-18-KEEPALIVE; ADR-D3 §1.5:189).

        Fires one `max_tokens=1` Anthropic call through `_dispatch_anthropic` so
        the cache breakpoints a real dispatch places are established at process
        boot. Best-effort: any exception is caught + logged; returns
        `PrewarmOutcome.FAILED`, never raises.

        Called at bootstrap stage 5 (both one-shot `harness run` + daemon) and
        repeatedly by the daemon keep-alive loop. MUST NOT be routed through the
        `RetryBreakerFallbackDispatcher` or `RuntimeHITLGateComposer` wrappers
        (boot hangs on AskUserQuestion + breaker trips are not appropriate here).
        """
        # 0. U-RT-135 policy gate — FIRST, before any eligibility check:
        # under fail-closed at MTC, prewarm's swallow-all posture is a
        # fail-open bypass (OD v1.34 §21.2.3 row 8), so no ping is fired.
        if self.prewarm_policy_fail_closed:
            return PrewarmOutcome.SKIPPED_POLICY_FAIL_CLOSED

        # 1. Anthropic-only gate.
        if "anthropic" not in self.providers:
            return PrewarmOutcome.SKIPPED_NO_ANTHROPIC

        # 2. Eligibility gate — skip when no breakpoint would be placed.
        # Mirrors `_payload_to_anthropic_kwargs` placement logic so
        # eligible ⟺ breakpoint-will-place ⟺ ping warms something.
        if self.frozen_tool_superset is None:
            return PrewarmOutcome.SKIPPED_NOT_ELIGIBLE
        _system = self.active_system_prompt
        _eligible = (
            _combined_prefix_clears_non_vacuity_floor(self.frozen_tool_superset, _system)
            if _system
            else _superset_clears_non_vacuity_floor(self.frozen_tool_superset)
        )
        if not _eligible:
            return PrewarmOutcome.SKIPPED_NOT_ELIGIBLE

        # 3. Model resolution:
        #   (1) routing_manifest per_workload_overrides → Anthropic model_binding_override;
        #   (2) prewarm_model config field;
        #   (3) SKIPPED_NOT_ELIGIBLE (cannot warm without a model).
        _model: str | None = None
        if self.routing_manifest is not None and self.workload_class is not None:
            _wc_override = self.routing_manifest.per_workload_overrides.get(self.workload_class)
            if (
                _wc_override is not None
                and _wc_override.model_binding_override is not None
                and _wc_override.model_binding_override.provider == "anthropic"
            ):
                _model = _wc_override.model_binding_override.model
        if _model is None:
            _model = self.prewarm_model
        if _model is None:
            return PrewarmOutcome.SKIPPED_NOT_ELIGIBLE

        # 4. Minimal ping payload.
        # ADR-D3 §1.5:189 says max_tokens=0 but Anthropic requires ≥1; use 1.
        _ping = ProviderAgnosticPayload(
            messages=({"role": "user", "content": "cache prewarm"},),
            tools=None,
            params={"max_tokens": 1},
        )
        _adapter = self.providers["anthropic"]
        _tracer = self.tracer_provider.get_tracer("harness.runtime.llm_dispatch")
        _span_name = f"{GenAiOperation.CHAT.value} {_model}"
        try:
            with _tracer.start_as_current_span(_span_name) as _span:
                _span.set_attribute("gen_ai.operation.name", GenAiOperation.CHAT.value)
                _span.set_attribute("gen_ai.provider.name", "anthropic")
                _span.set_attribute("gen_ai.request.model", _model)
                _span.set_attribute("anthropic.prewarm", True)
                _srv_addr = _PROVIDER_SERVER_ADDRESS.get("anthropic")
                _srv_port = _PROVIDER_SERVER_PORT.get("anthropic")
                if _srv_addr is not None:
                    _span.set_attribute("server.address", _srv_addr)
                    if _srv_port is not None:
                        _span.set_attribute("server.port", _srv_port)

                _resp, _usage, _cache, _req = await _dispatch_anthropic(
                    _adapter,
                    _model,
                    _ping,
                    system=_system,
                    upstream=None,
                    frozen_tool_superset=self.frozen_tool_superset,
                    cache_ttl=self.cache_ttl,
                )

                _set_if_present(_span, "gen_ai.usage.input_tokens", _usage.input_tokens)
                _set_if_present(_span, "gen_ai.usage.output_tokens", _usage.output_tokens)
                _set_if_present(
                    _span,
                    "anthropic.cache_creation_input_tokens",
                    _cache.cache_creation_input_tokens,
                )
                _set_if_present(
                    _span, "anthropic.cache_read_input_tokens", _cache.cache_read_input_tokens
                )
                _set_if_present(_span, "anthropic.cache_breakpoint_id", _cache.cache_breakpoint_id)
                _set_if_present(_span, "anthropic.cache_ttl_seconds", _cache.cache_ttl_seconds)

                # Honest cost attribution — synthetic step context so the spend
                # appears in the audit ledger under workflow_id="__prewarm__"
                # rather than being silently attributed to the last real workflow.
                await _attribute_cost_off_loop_best_effort(
                    span=_span,
                    cost_chain=self.cost_chain,
                    audit_writer=self.audit_writer,
                    rate_table=self.rate_table,
                    cost_record_sink=self.cost_record_sink,
                    # B-23 — the prewarm ping fires outside any active workflow
                    # step (synthetic __prewarm__ ids), so it stays in the
                    # documented outside-workflow-context class: F2-write the
                    # dispatch fact (ledger_writer) but omit the sidecar
                    # (procedural_tier_snapshot_resolver=None) per IS §5.1.
                    ledger_writer=self.ledger_writer,
                    procedural_tier_snapshot_resolver=None,
                    signing_backend=self.signing_backend,
                    provider_name="anthropic",
                    model=_model,
                    parent_idempotency_key="__prewarm__",
                    workflow_id="__prewarm__",
                    parent_action_id="__prewarm__",
                    input_tokens=_usage.input_tokens,
                    output_tokens=_usage.output_tokens,
                    cache_creation=_cache.cache_creation_input_tokens,
                    cache_read=_cache.cache_read_input_tokens,
                    tenant_id=None,
                )
        except Exception:
            import logging

            logging.getLogger("harness.runtime.prewarm").warning(
                "prewarm failed (best-effort; will not propagate)", exc_info=True
            )
            return PrewarmOutcome.FAILED

        return PrewarmOutcome.WARMED

    def _resolve_per_step_system_prompt(self, prompt_version_sha: str) -> str:
        """Resolve a per-step ``prompt_version_sha`` → injected content (B4 Slice 3).

        The per-step override (CP ``StepOverride.prompt_version_sha``, applied by
        ``resolve_step_binding``) names a content-addressed member of the IS
        ``PromptManifest.versions`` store. This resolves it to content via the
        stage-5 ``prompt_versions_by_sha`` map, running the SAME fail-loud guards
        the per-role bootstrap path runs — but at this per-dispatch site (the
        per-step binding is only known here, not at bootstrap):

        * unauthored sha → :class:`PromptSelectionUnauthoredError`
          (``RT-FAIL-PROMPT-SELECTION-UNAUTHORED``) — a selected version must be
          an authored store member;
        * binding-tier governance parity → :class:`PromptVersionUnapprovedError`
          (``RT-FAIL-PROMPT-VERSION-UNAPPROVED``) — at a tier requiring approval
          (OD C-OD-34), the version's sha must be a member of
          ``approved_prompt_version_shas``.

        Governance keys on the **deployment** persona tier (``self.persona_tier``,
        threaded from ``config.persona_tier`` at stage 5) — NOT the per-workflow
        ``binding.persona_tier`` — exactly as the default/per-role approval gate
        does at bootstrap. Keying on the per-workflow tier would let a workflow
        whose manifest declares ``SOLO_DEVELOPER`` bypass the approval a
        binding-tier *deployment* requires (Codex P1). ``self.persona_tier`` is
        ``None`` only in the unit-test-ergonomics path (production stage 5 always
        binds ``config.persona_tier``); a ``None`` deployment tier is treated as
        no-governance-context (inert), never a binding tier.

        Both surface as a STEP failure here (per-dispatch — propagates to the CP
        driver try/except), unlike the per-role path's BootstrapFailure. Reuses the
        canonical fail-class exceptions so the audit fail-class catalog stays
        single-sourced. Lazy imports mirror the existing ``SkillActivationMode``
        lazy-import pattern in ``dispatch`` (keeps the module-load edge minimal).
        """
        from harness_od.prompt_governance_gradient import resolve_prompt_governance

        from harness_runtime.lifecycle.prompt_selection import (
            PromptSelectionUnauthoredError,
            PromptVersionUnapprovedError,
        )

        content = self.prompt_versions_by_sha.get(prompt_version_sha)
        if content is None:
            raise PromptSelectionUnauthoredError(prompt_version_sha)
        deployment_tier = self.persona_tier
        if (
            deployment_tier is not None
            and resolve_prompt_governance(deployment_tier).approval_required
            and prompt_version_sha not in self.approved_prompt_version_shas
        ):
            raise PromptVersionUnapprovedError(
                persona_tier=deployment_tier, version_sha=prompt_version_sha
            )
        return content

    async def resolve_routed_binding(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> RoutedPrimaryResolution | None:
        """Resolve the layered-routing PRIMARY candidate ONCE for the C-RT-16
        wrapper (B-L2-FALLBACK-COMPOSITION, `Spec_Harness_Runtime_v1.md` §14.6).

        The SELECTION half of `dispatch` — runs the layered routing strategy
        (DECLARATIVE-decline → EMBEDDING classifier → L3 router per C-CP-02 §2.2)
        and returns a ``RoutedPrimaryResolution`` (the routed ``ModelBinding`` +
        the resolving ``RoutingDecisionTrace`` + binding rationale) WITHOUT
        dispatching — the trace rides to the inner span per
        B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION (§14.6.1). The C-RT-16
        ``RetryBreakerFallbackDispatcher`` calls this ONCE per step (via a direct
        handle the stage-5 factory hands it — NOT through its HITL/inner chain)
        and SEEDS the routed model as its PRIMARY fallback candidate, so the
        layered routing decision composes with the fallback chain. The inner
        ``dispatch`` stays FAITHFUL — it dispatches the wrapper's rebound
        candidate exactly once per attempt (§14.6). This is the U-RT-114 §14.5.3
        pattern applied to layered routing: model-candidate selection lives at
        the wrapper as the chain PRIMARY, never re-run per fallback attempt (the
        §14.5.3 "no two-authority-at-dispatch" invariant the inner-routing
        re-evaluation otherwise breaks).

        Returns ``None`` — "no routing augmentation; the wrapper's existing
        per-role / stage chain governs" — when:

        - ``routing_activation`` is off (the default → byte-identical to the
          pre-B-L2 always-echo dispatch); OR
        - the request has a DETERMINISTIC binding (a per-step override
          ``override_applied``, a per-role ``per_role_bindings`` entry, or a
          MODEL-BEARING per-workload override). DECLARATIVE would RESOLVE (echo
          ``binding.model_binding``), which IS the wrapper's existing chain
          primary — so no augmentation is needed, and a per-role binding's own
          U-RT-114 primary augmentation takes PRECEDENCE (routing fills only the
          no-deterministic-binding gap — the mutual-exclusivity §2.2's
          ``_has_deterministic_binding`` check encodes); OR
        - no EMBEDDING classifier AND no L3 router is configured (nothing to
          route to → faithful; defensively, the factory builds the default
          EMBEDDING classifier when ``routing_activation`` is on).

        Raises
        ------
        RoutingCandidateUnresolvedError
            DECLARATIVE declined and EMBEDDING + L3 produced no well-formed
            candidate (§2.5.2/§2.5.3). The wrapper's ``dispatch`` surfaces it as
            a step failure, exactly as the inner dispatch surfaces it on the
            non-routing path.
        """
        if not self.routing_activation:
            return None
        _role = step_context.agent_role or _MVP_DEFAULT_AGENT_ROLE
        manifest = self.routing_manifest or _EMPTY_ROUTING_MANIFEST
        _workload = self.workload_class or _MVP_DEFAULT_WORKLOAD_CLASS
        _workload_override = manifest.per_workload_overrides.get(_workload)
        # B-MODEL-RESOLUTION-CONSOLIDATION §14.6.2 — the decline predicate MUST
        # mirror the wrapper's `_effective_chain` deterministic branches EXACTLY
        # (per-step MODEL / per-workload MODEL / per-role). It is an order-
        # independent disjunction, so the per-workload/per-role precedence swap does
        # not affect it. The decline may be more LENIENT than the authority (a wasted
        # routing call `_effective_chain` ignores) but NEVER stricter: a stricter
        # decline returns None while the authority also skips the source ⟹ the model
        # silently drops to default. Each conjunct pairs with a branch:
        #   - `model_binding_override is not None`  ⟷ per-step branch
        #     (was `binding.override_applied` — over-declined on a NON-model
        #     per-step override [hitl/engine-only], suppressing routing spuriously)
        #   - the per-workload conjunct ⟷ per-workload branch (same
        #     `self.workload_class or _MVP_DEFAULT_WORKLOAD_CLASS`)
        #   - `_role != _MVP_DEFAULT_AGENT_ROLE and _role in per_role_bindings`
        #     ⟷ per-role branch (the default-role exclusion mirrors the authority)
        _has_deterministic_binding = (
            binding.model_binding_override is not None
            or (
                _workload_override is not None
                and _workload_override.model_binding_override is not None
            )
            or (_role != _MVP_DEFAULT_AGENT_ROLE and _role in manifest.per_role_bindings)
        )
        if _has_deterministic_binding:
            # A higher-than-routed MODEL source governs (per-step / per-workload /
            # per-role) — the wrapper's `_effective_chain` owns the PRIMARY for it;
            # routing declines so it fills only the no-override gap.
            return None
        if self.embedding_classifier is None and self.router is None:
            # Nothing to route to (no L2 classifier + no L3 router) → faithful.
            # Defensive: `materialize_llm_dispatcher_stage` builds the default
            # EMBEDDING classifier when `routing_activation` is on.
            return None
        payload = _coerce_payload(step.step_payload)
        envelope = InferenceRequest(
            agent_role=_role,
            workload_class=_workload,
            persona_tier=self.persona_tier or PersonaTier.SOLO_DEVELOPER,
            context_tokens=len(payload.messages),
            request_payload=payload,
            trace_context=_MVP_PLACEHOLDER_TRACE_CONTEXT,
        )
        # Past the deterministic check → DECLARATIVE DECLINES so `route()` falls
        # through to the injected EMBEDDING classifier (then the L3 router). ONE
        # source of truth for the routing layers — the same EMBEDDING/L3 surface
        # the inner held, now consulted ONCE here for the wrapper's primary.
        routing_layer_decisions: dict[RoutingLayer, LayerDecisionFn] = {
            RoutingLayer.DECLARATIVE: _declarative_decline
        }
        if self.embedding_classifier is not None:
            routing_layer_decisions[RoutingLayer.EMBEDDING] = self.embedding_classifier
        trace, _binding_rationale = await resolve_routing_trace(
            envelope,
            manifest=manifest,
            layer_decisions=routing_layer_decisions,
            budgets=self.budgets,
            router=self.router,
        )
        provider, _sep, model = trace.candidate.partition(":")
        return RoutedPrimaryResolution(
            model_binding=ModelBinding(provider=provider, model=model),
            routing_trace=trace,
            binding_rationale=_binding_rationale,
        )

    def cohort_key(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
    ) -> str | None:
        """Return a stable cache-cohort key, or None if this dispatch is not cache-stable.

        B-18-3C-PREWARM-COHORTKEY: satisfies `CohortKeyCapable` Protocol.

        Returns None when:
        - `memory_runtime` is bound (per-dispatch memory packet injection makes the
          cache prefix unstable across dispatches), or
        - `frozen_tool_superset` is None (no deterministic tools block → no stable
          `cache_control` marker to warm).

        When cache-stable, returns a sha256 hex string encoding the attributes that
        determine the Anthropic prompt-cache prefix:
        provider, model, agent_role, prompt_version_sha, extended-thinking flag,
        cache_ttl, and "fts_bound" sentinel (frozen_tool_superset is not None).
        """
        if self.memory_runtime is not None:
            return None
        if self.frozen_tool_superset is None:
            return None
        raw_params = step.step_payload.get("params")
        thinking = (
            cast("dict[str, Any]", raw_params).get("thinking")
            if isinstance(raw_params, dict)
            else None
        )
        parts = [
            str(binding.model_binding.provider).encode(),
            str(binding.model_binding.model).encode(),
            str(binding.agent_role).encode(),
            str(binding.prompt_version_sha).encode(),
            str(thinking).encode(),
            str(self.cache_ttl).encode(),
            b"fts_bound",
        ]
        return hashlib.sha256(b"\x00".join(parts)).hexdigest()[:16]

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

        # --- B-POSTJOIN effect-free boundary guard (out-of-family Codex round 8 [P1]) ---
        # The LOAD-BEARING enforcement of the synthesis effect-free invariant (CP spec
        # v1.54 §3). This is the single convergence point for ALL payload sources: the
        # original compose, the `params` route, AND a post-HITL-EDIT replacement — the
        # `RuntimeHITLGateComposer` wraps this dispatcher, so a PRE_ACTION EDIT that
        # re-introduces tools lands in `step.step_payload` BEFORE this `_coerce_payload`.
        # The compose-time guard ran upstream and CANNOT see the edited payload; this
        # boundary is the real floor (`[[enforce-floor-no-bypass-seam]]`). A
        # POST_JOIN_SYNTHESIS step is read-only / effect-free — reject any tool binding
        # before the provider call (the synthesis except in `_maybe_post_join_synthesis`
        # maps this to a FAILED RunResult). Scoped to the SAFETY half only: an EDIT that
        # drops the sibling context is operator intent shown at the gate (CP spec v1.54 §3),
        # not a silent break.
        if step.step_kind is StepKind.POST_JOIN_SYNTHESIS:
            from harness_runtime.lifecycle.post_join_synthesis_dispatch import (
                post_join_tool_binding_violations,
            )

            _synth_violations = post_join_tool_binding_violations(payload.tools, payload.params)
            if _synth_violations:
                raise LLMDispatchPayloadShapeError(
                    "post-join-synthesis step is read-only / effect-free but the dispatched "
                    f"payload binds tools ({', '.join(_synth_violations)}); rejected at the LLM "
                    "dispatch boundary (this catches a post-HITL-EDIT re-introduction the "
                    "compose-time guard cannot see). CP spec v1.54 §3."
                )

        # --- B-INTERSTEP (runtime spec §14.21 C-RT-34): upstream-output read ---
        # The immediately-prior step's output (the opt-in inter-step channel's
        # most-recent record). It is injected into the FINAL provider kwargs at the
        # translator layer (`_inject_upstream_context_message`), NOT into
        # `payload.messages` here, so (1) a `params["messages"]` escape-hatch
        # override cannot silently drop it and (2) it runs AFTER the system-prompt
        # injection so it cannot mask the competing-system-source conflict check
        # (Codex review; mirrors the R-PM-1 post-`params` system-prompt injection).
        # None (opt-out) / empty channel → no injection (byte-identical to pre-v1.59).
        _upstream_output: Mapping[str, Any] | None = (
            self.inter_step_channel.most_recent_output()
            if self.inter_step_channel is not None
            else None
        )

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
        # C-RT-16 composition gap). MODEL BINDING ONLY — the per-role PROMPT is a
        # separate surface, resolved by the B4 dispatch-read immediately below.
        _role = step_context.agent_role or _MVP_DEFAULT_AGENT_ROLE
        _effective_model_binding = binding.model_binding

        # --- B4 (C-RT-15 §14.5.3): per-role PROMPT dispatch-read --------------
        # Index the branch role into the pre-resolved per-role system-prompt map
        # (built at bootstrap stage 0). EXPLICIT membership check (not `or`): a
        # bound role uses its resolved content even when "" (→ no injection per
        # §14.5.2), keeping "bound-but-empty" distinct from "unbound". An unbound
        # role — including the default/linear path, never in the map — falls
        # through to the stage-0 default-role `active_system_prompt` (the
        # §14.5.3 suggested fall-through-to-default lookup-miss policy). Per-call
        # LOCAL (never on self): the dispatcher is shared across concurrent
        # fan-out branches, so a per-role value MUST flow as a dispatch parameter.
        # --- B4 Slice 3 (CP spec v1.37 §6.1): per-step PROMPT override ---------
        # A per-step `prompt_version_sha` on the resolved binding (CP
        # `resolve_step_binding` applied a `StepOverride.prompt_version_sha`)
        # overrides BOTH the per-role and run-level-default prompts for THIS step.
        # Precedence: per-step > per-role > run-level default. The per-step sha is
        # resolved to content + governed HERE (the per-dispatch site) — not at
        # bootstrap like per-role — because the per-step binding is only known at
        # dispatch (it is a per-workflow `WorkflowManifestEntry.per_step_overrides`
        # entry, resolved CP-driver-side, not run-level config). Fail-loud on an
        # unauthored sha / unapproved binding-tier version surfaces as a STEP
        # failure (propagates to the driver try/except, like
        # RT-FAIL-PROMPT-INJECTION-CONFLICT), not a BootstrapFailure.
        if binding.prompt_version_sha is not None:
            _effective_system_prompt = self._resolve_per_step_system_prompt(
                binding.prompt_version_sha
            )
        elif _role in self.per_role_system_prompts:
            _effective_system_prompt = self.per_role_system_prompts[_role]
        else:
            _effective_system_prompt = self.active_system_prompt
        _memory_context = self.memory_context
        _standard_memory_tool_executor = self.standard_memory_tool_executor
        if self.memory_runtime is not None:
            if self.fallback_chain is None:
                raise LLMDispatchBindError(
                    "automatic memory runtime requires a fallback_chain binding"
                )
            _memory_context = self.memory_runtime.compose_for_dispatch(
                binding=binding,
                fallback_chain=self.fallback_chain,
                step=step,
                step_context=step_context,
            )
            if _standard_memory_tool_executor is None:
                _standard_memory_tool_executor = getattr(
                    self.memory_runtime,
                    "standard_memory_tool_executor",
                    None,
                )
        _effective_system_prompt = compose_system_prompt_with_memory_packet(
            _effective_system_prompt,
            _memory_context,
        )

        # --- R-300 / B-L2-FALLBACK-COMPOSITION: faithful dispatch-read ----------
        # The DECLARATIVE layer decision ECHOES the effective binding
        # (`binding.model_binding` — the C-RT-16 wrapper's rebound candidate: the
        # stage-chain primary, the U-RT-114 per-role model, or the routing_activation
        # routed primary). The inner C-RT-15 dispatch is FAITHFUL — it dispatches
        # whatever the wrapper rebinds, exactly once per attempt (§14.6 "the wrapper
        # invokes the inner dispatcher exactly once per attempt with a rebound
        # binding"). Layered-routing ACTIVATION (routing_activation → DECLARATIVE-
        # decline → EMBEDDING/L3 picking a DIFFERENT model) is NOT performed here: at
        # the inner it re-runs per fallback attempt and silently defeats the wrapper's
        # candidate chain (the §14.5.3 "no two-authority-at-dispatch" anti-pattern).
        # The routing decision is made ONCE, ONE LAYER OUT, at the C-RT-16 wrapper via
        # `resolve_routed_binding` (below), which seeds the routed model as the
        # wrapper's PRIMARY fallback candidate — so layered routing composes with the
        # fallback chain (B-L2-FALLBACK-COMPOSITION, runtime §14.6). `route()`'s
        # `manifest` arg + the envelope discriminators are carried for `routing.*`
        # span attribution.
        def _declarative_echo(
            _payload: ProviderAgnosticPayload, _manifest: RoutingManifest
        ) -> str | None:
            return f"{_effective_model_binding.provider}:{_effective_model_binding.model}"

        # `infer()` requires an InferenceRequest envelope. Its discriminator
        # fields are carried for the C-CP-01 §1.1 API surface but DISCARDED at
        # this boundary: the live routing decision is surfaced as `routing.*`
        # span attrs inside `_invoke_provider`, and the step output is the raw
        # provider Mapping returned below — NOT the InferenceResponse (which is
        # likewise discarded).
        #
        # CORRECTED 2026-07-27 — this previously closed "They become load-bearing
        # at R-300-second-provider"; that arc RESOLVED 2026-06-03 and per-role
        # selection did NOT land here. It landed on the two paths that bypass this
        # envelope entirely: per-role MODEL at
        # `retry_breaker_fallback._effective_chain`'s per-role branch and per-role
        # PROMPT at the `per_role_system_prompts` lookup above (both keying on
        # `step_context.agent_role`; R-FS-1 arc B4 / U-RT-114). The envelope's own
        # discriminators stay carried-but-discarded on the echo path — the live
        # per-discriminator `route()` selection is the `routing_activation`
        # opt-in path (`resolve_routed_binding`), not this construction.
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
            *,
            binding_rationale: str | None = None,
        ) -> ProviderDispatchResult:
            # C-CP-02 §2.5.4 — `binding_rationale` is the optional carrier
            # `infer()` threads ONLY on the Layer-3 router path (None on the
            # non-router path, so the span emitter keeps deriving
            # `f"{layer}:{candidate}"`). Matches the §2.5.4 Protocol-ized
            # `ProviderDispatchFn` seam (the defaulted kwarg keeps this closure
            # assignable + every non-router call byte-identical).
            response = await self._invoke_provider(
                provider,
                model,
                inner_payload,
                step_context,
                step_id=str(step.step_id),
                routing_trace=routing_trace,
                binding_rationale=binding_rationale,
                effective_system_prompt=_effective_system_prompt,
                upstream_output=_upstream_output,
                memory_context=_memory_context,
                standard_memory_tool_executor=_standard_memory_tool_executor,
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

        # C-CP-02 §2.1 production layer-decision map for the FAITHFUL inner
        # dispatch: DECLARATIVE-echo only. The DECLARATIVE echo always resolves
        # `binding.model_binding` (the wrapper's rebound candidate), so `route()`
        # short-circuits at DECLARATIVE and the inner faithfully dispatches it
        # (§14.6). Layered-routing ACTIVATION (the EMBEDDING classifier + the L3
        # router) is consulted ONCE at the C-RT-16 wrapper via
        # `resolve_routed_binding`, NOT here — so routing composes with fallback
        # instead of re-routing per attempt (B-L2-FALLBACK-COMPOSITION, §14.6).
        production_layer_decisions: dict[RoutingLayer, LayerDecisionFn] = {
            RoutingLayer.DECLARATIVE: _declarative_echo
        }

        await infer(
            envelope,
            dispatch=_provider_dispatch,
            manifest=self.routing_manifest or _EMPTY_ROUTING_MANIFEST,
            # `layer_decisions_override` is the test-only seam (C-CP-02 §2.5.5):
            # None -> the production map (DECLARATIVE-echo [+ EMBEDDING when a
            # classifier is injected]). A test injects a sentinel-forcing map to
            # reach the injected `router`, or an EMBEDDING-only map to reach L2.
            layer_decisions=(
                self.layer_decisions_override
                if self.layer_decisions_override is not None
                else production_layer_decisions
            ),
            # B-LAYER-BUDGET-OVERRIDE — the threaded budgets (DORMANT seam:
            # `DEFAULT_LAYER_BUDGETS` at production stage-5; an override-bearing
            # tuple resolves the §3.1 L3 per-persona/per-workload override).
            budgets=self.budgets,
            # C-CP-02 §2.5 — production binds None (Layer-3 inert); a test
            # fixture injects a mock RouterResolutionFn.
            router=self.router,
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
        binding_rationale: str | None = None,
        effective_system_prompt: str | None = None,
        upstream_output: Mapping[str, Any] | None = None,
        memory_context: RuntimeMemoryContext | None = None,
        standard_memory_tool_executor: Any = None,
    ) -> Mapping[str, Any]:
        """Provider-SDK dispatch boundary — the injected dispatch callable for
        `infer()` (R-300). Opens the `llm.inference` span (gen_ai.* + routing.*
        attribution), dispatches to the routed provider, runs cost-attribution,
        and returns the raw provider response Mapping (the step output).

        ``provider_name`` + ``model`` are the routing-selected candidate (per
        `route()` per U-CP-05); ``routing_trace`` carries the routing decision
        for `routing.*` span attribution per C-CP-01 §1.4.

        ``effective_system_prompt`` is the per-call system prompt the §14.5.2
        translate seam injects — the per-role prompt for a role-bound fan-out
        branch (B4 §14.5.3), else `self.active_system_prompt` (the stage-0
        default-role prompt). Passed as a parameter (not read from `self`)
        because the dispatcher is shared across concurrent branches.

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
        if operation is None and isinstance(adapter, _ExternalCLIProviderLike):
            operation = GenAiOperation.CHAT
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
            # is the §1.4 optional token. C-CP-02 §2.5.4: when `infer()` resolves
            # via a Layer-3 router it threads the router's free-text rationale
            # through the dispatch seam (`binding_rationale`); the emitter uses
            # it WHEN PRESENT. On every other path `binding_rationale is None`
            # and the emitter keeps deriving the layer+candidate token
            # (byte-identical to pre-§2.5 — the non-router path is unchanged).
            # B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION (§14.6.1 scope-boundary
            # closure): when the C-RT-16 wrapper resolved a routed PRIMARY it
            # publishes the REAL `(routing_trace, binding_rationale)` for THIS
            # dispatch — use it so `routing.layer` reports the EMBEDDING/L3 layer
            # that PICKED the model, not the inner's faithful DECLARATIVE echo.
            # Absent (routing off / a fallback candidate / any direct non-wrapper
            # dispatch) → the local echo trace (pre-arc behavior, byte-identical).
            # `routing.provider`/`routing.model` always reflect the actually
            # dispatched candidate (correct on every path), so only the layer +
            # rationale are sourced from the published trace.
            _routed_span = ROUTED_PRIMARY_SPAN_TRACE.get()
            _eff_trace = _routed_span[0] if _routed_span is not None else routing_trace
            _eff_rationale = _routed_span[1] if _routed_span is not None else binding_rationale
            span.set_attribute("routing.provider", provider_name)
            span.set_attribute("routing.model", model)
            span.set_attribute("routing.layer", _eff_trace.layer)
            span.set_attribute(
                "routing.binding_rationale",
                _eff_rationale
                if _eff_rationale is not None
                else f"{_eff_trace.layer}:{_eff_trace.candidate}",
            )

            # --- Step 2b (B-83): dispatch-time memory serve-check --------
            # `select_memory_access_mode` chose the access mode from DECLARED
            # capabilities, one layer out; the arm about to run is resolved
            # HERE. When STANDARD_MEMORY_TOOLS was selected but this dispatch
            # will not inject the C-MEM-14 tools — the anthropic arm (which
            # branches only on `step_has_memory_tool`/`hitl_tool_loop`, never
            # on access mode), the text-only external-CLI arm, an
            # openai/ollama dispatch with no bound executor, or a context whose
            # provider/family scope does not match this dispatch —
            # repair to the C-MEM-13 packet instead of silently serving zero
            # memory. `compose_system_prompt_with_memory_packet` already ran at
            # `dispatch()` and returned the prompt UNCHANGED (its gate is
            # `PROMPT_EXTENSION_PACKET`), so this adds the packet text that
            # earlier call declined to add.
            #
            # A scope-MISMATCHED context is the case that is NOT repaired — its
            # packet was retrieved under another provider/family scope, so it is
            # reported and withheld (`rendered is None`). See
            # `_degraded_serve_disposition`.
            #
            # B-83 [P1-d]: the packet travels as `memory_packet` rather than
            # being appended to `effective_system_prompt` here. Each translator
            # folds it into ITS OWN single effective system source — Anthropic's
            # `params["system"]`-or-kwarg, OpenAI/Ollama's leading
            # `role:"system"` message post-`params`-merge, the external CLI's
            # system section. Appending here instead produced a SECOND system
            # source and hard-failed `PromptInjectionConflictError` for any
            # payload that carries its own system prompt.
            degraded_sink = _DegradedMemoryServeSink(
                value=_degraded_serve_for_unservable_arm(
                    provider_name,
                    memory_context=memory_context,
                    standard_memory_tool_executor=standard_memory_tool_executor,
                )
            )
            repair_packet = (
                degraded_sink.value.rendered if degraded_sink.value is not None else None
            )
            # B-85 — a SECOND, structurally independent sink. Only a
            # standard-tools loop writes it, and only the degraded paths write
            # `degraded_sink`, so the two decisions never collide (see
            # `_UnservedMemoryToolCallsSink`).
            unserved_sink = _UnservedMemoryToolCallsSink()

            # --- Step 3: per-provider dispatch --------------------------
            cache_attrs: _AnthropicCacheAttrs | None
            request_attrs: _AnthropicRequestAttrs | None
            external_cli_attrs: _ExternalCLIAttrs | None = None
            # U-1 slice 3a (B-18) — select the DESCENDED superset for a sub-agent
            # (child-workflow) inference. The CP driver marks every child
            # `StepExecutionContext` with `sub_agent_descent=True` (ADR-D4 §1.5
            # descent); a descended dispatch emits the child superset (external-
            # irreversible tools REMOVE'd) instead of the parent's full superset —
            # closing the F1 latent C10 condition-2 gap. Top-level dispatch
            # (`sub_agent_descent=False`) is byte-identical to pre-slice-3a.
            if step_context.sub_agent_descent and self.frozen_tool_superset is not None:
                # A descended child in a run that HAS MCP tools: its wire tools ARE
                # the downgraded superset, and it MUST NOT fall back to
                # `payload.tools` (which could re-expose a removed external-
                # irreversible tool the child step declares). When the downgraded
                # union is empty (the parent registry held ONLY external-irreversible
                # tools → all REMOVE'd → `child_frozen_tool_superset is None`), emit an
                # EMPTY superset `()` so the translate sends `tools: []` (no visible
                # tools) rather than the step's declared tools (out-of-family Codex
                # [P2] — the two `None` meanings disambiguated by the parent superset).
                _effective_frozen_tool_superset = self.child_frozen_tool_superset or ()
            else:
                # Top-level dispatch, OR a descended child in an MVP run with NO MCP
                # tools at all (`frozen_tool_superset is None` → child superset also
                # None → the legacy `payload.tools` path; nothing to downgrade).
                _effective_frozen_tool_superset = self.frozen_tool_superset
            dispatch_outcome = _DISPATCH_OUTCOME_PROVIDER_ERROR
            dispatch_error_type: str | None = None
            try:
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
                            system=effective_system_prompt,
                            upstream=upstream_output,
                            frozen_tool_superset=_effective_frozen_tool_superset,
                            cache_ttl=self.cache_ttl,
                            memory_packet=repair_packet,
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
                            system=effective_system_prompt,
                            upstream=upstream_output,
                            frozen_tool_superset=_effective_frozen_tool_superset,
                            cache_ttl=self.cache_ttl,
                            memory_packet=repair_packet,
                        )
                    else:
                        (
                            response,
                            usage_attrs,
                            cache_attrs,
                            request_attrs,
                        ) = await _dispatch_anthropic(
                            adapter,
                            model,
                            payload,
                            system=effective_system_prompt,
                            upstream=upstream_output,
                            frozen_tool_superset=_effective_frozen_tool_superset,
                            cache_ttl=self.cache_ttl,
                            memory_packet=repair_packet,
                        )
                elif provider_name == "openai":
                    # B-83 — the arm guard and the serve-check read the SAME
                    # authority (`_standard_memory_tools_context`), so "the tools
                    # were injected" and "the serve-check passed" cannot disagree.
                    openai_tools_context = _standard_memory_tools_context(
                        provider_name,
                        memory_context=memory_context,
                        standard_memory_tool_executor=standard_memory_tool_executor,
                    )
                    if openai_tools_context is not None:
                        response, usage_attrs = await _dispatch_openai_with_standard_memory_tools(
                            adapter,
                            model,
                            payload,
                            memory_context=openai_tools_context,
                            standard_memory_tool_executor=standard_memory_tool_executor,
                            step_context=step_context,
                            step_id=step_id,
                            unserved_sink=unserved_sink,
                            system=effective_system_prompt,
                            upstream=upstream_output,
                        )
                    else:
                        response, usage_attrs = await _dispatch_openai(
                            adapter,
                            model,
                            payload,
                            system=effective_system_prompt,
                            upstream=upstream_output,
                            memory_packet=repair_packet,
                        )
                    cache_attrs = None
                    request_attrs = None
                elif provider_name == "ollama":
                    ollama_tools_context = _standard_memory_tools_context(
                        provider_name,
                        memory_context=memory_context,
                        standard_memory_tool_executor=standard_memory_tool_executor,
                    )
                    if ollama_tools_context is not None:
                        # B-83 (c) — the ollama arm can discover mid-dispatch that
                        # the daemon refuses tools for this model; it then repairs
                        # to the packet itself and publishes the decision into the
                        # SINK before its retry, so the `finally` emitter covers
                        # it even when that retry raises.
                        (
                            response,
                            usage_attrs,
                        ) = await _dispatch_ollama_with_standard_memory_tools(
                            adapter,
                            model,
                            payload,
                            memory_context=ollama_tools_context,
                            standard_memory_tool_executor=standard_memory_tool_executor,
                            step_context=step_context,
                            step_id=step_id,
                            degraded_sink=degraded_sink,
                            unserved_sink=unserved_sink,
                            system=effective_system_prompt,
                            upstream=upstream_output,
                        )
                    else:
                        response, usage_attrs = await _dispatch_ollama(
                            adapter,
                            model,
                            payload,
                            system=effective_system_prompt,
                            upstream=upstream_output,
                            memory_packet=repair_packet,
                        )
                    cache_attrs = None
                    request_attrs = None
                elif isinstance(adapter, _ExternalCLIProviderLike):
                    response, usage_attrs, external_cli_attrs = await _dispatch_external_cli(
                        adapter,
                        provider_name,
                        model,
                        payload,
                        system=effective_system_prompt,
                        upstream=upstream_output,
                        memory_packet=repair_packet,
                    )
                    cache_attrs = None
                    request_attrs = None
                else:
                    raise LLMDispatchProviderUnreachableError(provider_name)
            except asyncio.CancelledError:
                # Cancellation is not a provider fault; label it honestly. It
                # still passes through `finally`, so the span is still emitted.
                dispatch_outcome = _DISPATCH_OUTCOME_CANCELLED
                raise
            except BaseException as exc:
                dispatch_error_type = type(exc).__name__
                raise
            else:
                dispatch_outcome = _DISPATCH_OUTCOME_COMPLETED
            finally:
                # B-83 [P2-d] — ONE degraded-serve emission site, in `finally`,
                # for every reachability (unservable arm / scope-mismatched
                # context / daemon-refused ollama tools). Emitting AFTER the
                # dispatch instead lost the only B-83-specific signal whenever
                # the provider call raised — even though by then the packet had
                # already been sent (the disclosure happened) or already been
                # withheld (the denial happened). The sink is read rather than a
                # local, so a degradation decided INSIDE a failing arm call is
                # reported too.
                if degraded_sink.value is not None:
                    _emit_degraded_memory_serve_span(
                        self.tracer_provider,
                        degraded_sink.value,
                        provider=provider_name,
                        model=model,
                        outcome=dispatch_outcome,
                        error_type=dispatch_error_type,
                    )
                # B-85 — an INDEPENDENT emission, not an `elif`. The two sinks
                # report different facts about different dispatches and are
                # never both populated (see `_UnservedMemoryToolCallsSink`);
                # chaining them would make that structural invariant load-
                # bearing for correctness instead of merely true.
                if unserved_sink.value is not None:
                    _emit_unserved_memory_tool_calls_span(
                        self.tracer_provider,
                        unserved_sink.value,
                        provider=provider_name,
                        model=model,
                        outcome=dispatch_outcome,
                        error_type=dispatch_error_type,
                    )

            if memory_context is not None and self.memory_runtime is not None:
                capture_turn_completion = getattr(
                    self.memory_runtime,
                    "capture_turn_completion",
                    None,
                )
                if callable(capture_turn_completion):
                    capture_turn_completion(
                        memory_context=memory_context,
                        payload=payload,
                        step_context=step_context,
                        step_id=step_id,
                        provider=provider_name,
                        model=model,
                        response=response,
                        input_tokens=usage_attrs.input_tokens,
                        output_tokens=usage_attrs.output_tokens,
                    )

            # --- Step 4: populate response-side attributes --------------
            _set_if_present(span, "gen_ai.usage.input_tokens", usage_attrs.input_tokens)
            _set_if_present(span, "gen_ai.usage.output_tokens", usage_attrs.output_tokens)
            _set_if_present(span, "gen_ai.response.id", usage_attrs.response_id)
            if external_cli_attrs is not None:
                span.set_attribute("external_cli.exit_code", external_cli_attrs.exit_code)
                span.set_attribute("external_cli.provider.kind", external_cli_attrs.kind)

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
            # U-RT-136 post-effect fence site (provider-response class): a
            # signing failure escaping under `audit_signing_fail_closed=ON`
            # re-raises as the result-preserving carrier — the provider
            # response is a completed PAID effect; a bare raise would
            # discard it (CP v1.101 §2 catch-ordering contract).
            try:
                await _attribute_cost_off_loop_best_effort(
                    span=span,
                    cost_chain=self.cost_chain,
                    audit_writer=self.audit_writer,
                    rate_table=self.rate_table,
                    cost_record_sink=self.cost_record_sink,
                    ledger_writer=self.ledger_writer,
                    procedural_tier_snapshot_resolver=self.procedural_tier_snapshot_resolver,
                    signing_backend=self.signing_backend,
                    audit_signing_fail_closed=self.audit_signing_fail_closed,
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
                    run_engine_class=step_context.run_engine_class,
                )
            except AUDIT_SIGNING_HARD_FAILURES as exc:
                # codex [P1] on the B-65-A CP-side arc round 4 — `resolve_
                # result_ref` is synchronous I/O (pickle+encrypt+fsync, plus
                # an opportunistic decrypt-sweep of the whole store);
                # `asyncio.to_thread` would queue it onto the LOOP'S DEFAULT
                # executor, which `execute_workflow`'s own sync drivers can
                # exhaust while blocked awaiting a loop coroutine — the same
                # deadlock class `run_audit_off_loop`'s dedicated pool exists
                # to avoid (see `audit_offload.py` module docstring).
                _result_ref = await resolve_result_ref_off_loop(
                    self.protected_result_store,
                    step_context.tenant_id,
                    response,
                )
                raise PostEffectAuditSigningError(
                    f"audit signing failed after a completed provider response "
                    f"(provider={provider_name!r}, model={model!r}): {exc}",
                    effect_class=PostEffectClass.PROVIDER_RESPONSE,
                    result=response,
                    result_ref=_result_ref,
                ) from exc

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


@dataclass(frozen=True, slots=True)
class _ExternalCLIAttrs:
    exit_code: int
    kind: str


#: B-83 degraded-serve reasons. Span-attribute VALUES, deliberately not enum
#: members — `MemoryTelemetryOperationName` / `MemoryTelemetryFailureClass` /
#: `MemoryOperationKind` are CLOSED per C-MEM-19, and extending one would be an
#: X-AL-3 design extension.
#:
#: `arm_unservable` — the arm reached will not inject the C-MEM-14 tools, but
#: the context was composed FOR THIS provider, so its packet is
#: provider-matched by construction and can be served as prompt text
#: (C-MEM-13, `Spec_Memory_Substrate_v1.md:460`). REPAIRED.
_DEGRADED_REASON_ARM_UNSERVABLE: Final[str] = "arm_unservable"
#: `provider_scope_mismatch` — the context was composed for a DIFFERENT
#: provider than the one being dispatched. REPORT-ONLY: see
#: `_degraded_serve_for_unservable_arm` for why the packet must NOT be served.
_DEGRADED_REASON_PROVIDER_SCOPE_MISMATCH: Final[str] = "provider_scope_mismatch"
#: `provider_family_scope_mismatch` — provider IDENTITY matches, but the packet
#: was RETRIEVED under a different provider-FAMILY scope than the family this
#: dispatch belongs to. REPORT-ONLY. See `_packet_scope_matches_dispatch_family`.
_DEGRADED_REASON_PROVIDER_FAMILY_SCOPE_MISMATCH: Final[str] = "provider_family_scope_mismatch"
#: Packet-mode denials do NOT get a constant here. Scope is fine, but C-MEM-13
#: would not have selected `PROMPT_EXTENSION_PACKET` for this request, and the
#: reason is carried verbatim from the counterfactual selector on
#: `RuntimeMemoryContext.prompt_packet_fallback_denial` — its own
#: `MemoryAccessModeDenialReason` value (`token_budget_empty` /
#: `no_supported_mode`), or the `not_derived` sentinel. [P2-e]: a single
#: `packet_policy_denied` constant collapsed all of those into one label and
#: reported a budget denial as an operator policy decision, which is a false
#: accusation about a configuration the operator did not make.


@dataclass(frozen=True, slots=True)
class _DegradedMemoryServe:
    """B-83 — a dispatch that could NOT serve its selected access mode.

    Carries the mode that was SELECTED, WHY the dispatch could not serve it,
    and the packet served in its place — or `None` when the degradation is
    REPORT-ONLY and nothing was served. One carrier for both dispositions, so
    the single telemetry emitter (`_emit_degraded_memory_serve_span`) reports
    the same attribute shape for every reachability.

    Constructed at exactly two sites: the arm-selection serve-check (an arm
    that will not inject the tools, or a provider-mismatched context) and the
    ollama tools-unsupported fallback (an arm that tried and was refused by
    the daemon).
    """

    selected_access_mode: MemoryAccessMode
    reason: str
    #: None ⇒ report-only: nothing was served to the model.
    rendered: RenderedMemoryPromptPacket | None


@dataclass(slots=True)
class _DegradedMemoryServeSink:
    """Mutable single-slot carrier for a degradation decided mid-dispatch.

    B-83 [P2-d]. The ollama tools-unsupported fallback decides its degradation
    INSIDE the arm call, and the arm site must still be able to report it when
    that call RAISES. A return-tuple element cannot do that — it only travels on
    success — so the decision is PUBLISHED into this sink the moment it is made,
    before the retry that may fail. The arm site's ``finally`` reads the sink,
    so a decision that was reached is always reported, whether or not the
    provider call that followed it completed.

    One instance per dispatch, created at the arm-selection site: never shared
    across concurrent branches.
    """

    value: _DegradedMemoryServe | None = None


#: Terminal disposition of the provider call a degraded serve rode on. Span
#: attribute VALUES, not enum members (the C-MEM-19 enums are closed).
_DISPATCH_OUTCOME_COMPLETED: Final[str] = "completed"
_DISPATCH_OUTCOME_PROVIDER_ERROR: Final[str] = "provider_error"
_DISPATCH_OUTCOME_CANCELLED: Final[str] = "cancelled"


#: The provider arms that own a standard-memory-tools sibling dispatch fn.
_STANDARD_MEMORY_TOOL_ARMS: Final[frozenset[str]] = frozenset({"openai", "ollama"})


def _standard_memory_tools_context(
    provider_name: str,
    *,
    memory_context: RuntimeMemoryContext | None,
    standard_memory_tool_executor: Any,
) -> RuntimeMemoryContext | None:
    """The context THIS dispatch will serve the C-MEM-14 tools with, else None.

    The single authority for the question "does the arm about to run serve
    `STANDARD_MEMORY_TOOLS`?" — read by the two arm guards that take the
    standard-tools path AND by the B-83 serve-check, so the check and the
    branch can never disagree.

    The provider-identity conjunct closes B-83 reachability (b): a STATICALLY
    injected `RuntimeLLMDispatcher.memory_context` is composed ONCE, and
    `RetryBreakerFallbackDispatcher` rebinds the provider per attempt
    (`retry_breaker_fallback.py:185-192`), so the context on the wire can have
    been composed for a DIFFERENT provider than the one being dispatched.
    `MemoryAccessModeSelection.selected_provider` is
    `request.model_binding.provider` verbatim
    (`harness-cp/src/harness_cp/memory_access_mode.py:372`), the same string
    that reaches `provider_name` here, so the comparison is exact. The
    `memory_runtime`-bound path recomposes per attempt
    (`automatic_memory.compose_for_dispatch`) and therefore always matches —
    this conjunct is inert there.
    """

    if memory_context is None:
        return None
    if memory_context.access_mode is not MemoryAccessMode.STANDARD_MEMORY_TOOLS:
        return None
    if standard_memory_tool_executor is None:
        return None
    if memory_context.selection.selected_provider != provider_name:
        return None
    if provider_name not in _STANDARD_MEMORY_TOOL_ARMS:
        return None
    return memory_context


def _packet_scope_matches_dispatch_family(
    memory_context: RuntimeMemoryContext,
    provider_name: str,
) -> bool:
    """True iff the packet's RETRIEVAL scope belongs to this dispatch's family.

    B-83 [P1-c]. Provider IDENTITY is not sufficient. On the `memory_runtime`
    path a cross-family fallback RECOMPOSES the context for the current
    candidate — so `selection.selected_provider` equals the dispatched provider
    and the identity conjunct passes — but
    `automatic_memory.compose_for_dispatch` builds
    `record_scope.provider_family` from `fallback_chain.primary.family`
    (`automatic_memory.py:191-199`), i.e. the PRIMARY's family, not the
    candidate's. `MemoryRetriever` filters records on exactly that field
    (`memory_retrieval.py:371-384` `_scope_mismatch`), so the assembled packet
    holds PRIMARY-family records. Rendering it for a different-family candidate
    is the same disclosure leak the identity conjunct was meant to stop, one
    layer down. (`selection.selected_family` is derived from the same primary,
    so it agrees with the scope and cannot serve as the discriminator either.)

    `provider_family_for_scope_check` is the fail-closed sibling of the
    workspace's provider→family authority (`cross_family_cost_tag.py`, whose
    cost-attribution entry point the C-RT-16 wrapper still uses); one shared
    map, so a second mapping here would be the mirror-copy drift class. B-86
    item (3): the cost entry point falls back to `LOCAL_OPEN_WEIGHT` for an
    UNREGISTERED provider key, which made such a key compare EQUAL to an
    ollama-scoped packet and get it REPAIRED — conservative for attribution, a
    live disclosure leak for THIS scope-boundary use. The sibling returns
    `None` instead and this function fails closed on it. (B-86's own KEYING
    question — whether provider-family is the right scope discriminator at all
    — remains open; only the unregistered-key sentinel is settled here.)

    An absent scope, an absent `provider_family`, or an unregistered provider
    key is treated as NOT matching: `_scope_mismatch` treats a `None` request
    family as "no constraint", so the packet may hold records of ANY family and
    nothing here can prove otherwise. Unverifiable is not the same as safe.
    """

    scope = memory_context.record_scope
    if scope is None or scope.provider_family is None:
        return False
    dispatch_family = provider_family_for_scope_check(provider_name)
    if dispatch_family is None:
        return False
    return scope.provider_family == dispatch_family.value


def _degraded_serve_disposition(
    provider_name: str,
    memory_context: RuntimeMemoryContext,
) -> _DegradedMemoryServe:
    """Given that this dispatch CANNOT serve the selected mode, decide how.

    The single authority for repair-vs-report, shared by the arm-selection
    serve-check and the ollama tools-unsupported fallback, so the two sites can
    never disagree about whether a packet is safe to render.

    Repair requires THREE conjuncts, covering the two questions a degraded
    serve raises — *may these records go to this destination* (scope) and *is
    this delivery mode authorized at all* (policy):

    1. provider IDENTITY — the context was composed for this provider;
    2. provider FAMILY — the packet was RETRIEVED under this dispatch's family
       scope (`_packet_scope_matches_dispatch_family`);
    3. prompt-packet AUTHORIZATION — C-MEM-13 would itself have selected
       `PROMPT_EXTENSION_PACKET` for the same request
       (`prompt_packet_fallback_denial is None`, settled at composition where
       the policy + budget inputs are in scope; when it is NOT None its value
       is the selector's own denial reason, reported verbatim so telemetry
       names the gate that actually closed). Rendering the packet IS the
       prompt-packet mode, so the standard-tools selection that actually won
       does not authorize it; a policy allowing `standard_tool_access` while
       `injection_access` denies prompt packets is a legal, expressible
       configuration, and the packet mode additionally requires a non-empty
       token budget that the tools mode does not.

    Any conjunct failing is report-only: the degradation becomes visible in
    telemetry, and nothing is disclosed out of scope or through a mode the
    operator disabled.
    """

    if memory_context.selection.selected_provider != provider_name:
        return _DegradedMemoryServe(
            selected_access_mode=memory_context.access_mode,
            reason=_DEGRADED_REASON_PROVIDER_SCOPE_MISMATCH,
            rendered=None,
        )
    if not _packet_scope_matches_dispatch_family(memory_context, provider_name):
        return _DegradedMemoryServe(
            selected_access_mode=memory_context.access_mode,
            reason=_DEGRADED_REASON_PROVIDER_FAMILY_SCOPE_MISMATCH,
            rendered=None,
        )
    packet_denial = memory_context.prompt_packet_fallback_denial
    if packet_denial is not None:
        return _DegradedMemoryServe(
            selected_access_mode=memory_context.access_mode,
            reason=packet_denial,
            rendered=None,
        )
    return _DegradedMemoryServe(
        selected_access_mode=memory_context.access_mode,
        reason=_DEGRADED_REASON_ARM_UNSERVABLE,
        rendered=render_packet_for_degraded_dispatch(memory_context),
    )


def _degraded_serve_for_unservable_arm(
    provider_name: str,
    *,
    memory_context: RuntimeMemoryContext | None,
    standard_memory_tool_executor: Any,
) -> _DegradedMemoryServe | None:
    """B-83 — the dispatch-time serve-check at the arm-selection site.

    `select_memory_access_mode` picks a mode from DECLARED capabilities; the
    arm reached may not serve it. When `STANDARD_MEMORY_TOOLS` was selected and
    this dispatch will not inject the tools, the model would otherwise receive
    ZERO memory while a fully-retrieved, policy-checked packet sits unused on
    the context. C-MEM-14 (`Spec_Memory_Substrate_v1.md:489`) states the
    exposure as a present-tense obligation, and C-MEM-13 (`:460`) authorizes
    the prompt-extension packet for providers without usable tool support — so
    the repair is to serve the packet as read-only prompt text.

    TWO DISPOSITIONS, and the discriminator is provider identity:

    * `arm_unservable` → REPAIR. The context was composed for THIS provider,
      so the packet already cleared retrieval + policy for exactly this
      provider and provider-family scope. Serving it as prompt text discloses
      nothing the selection did not already clear.

    * `provider_scope_mismatch` / `provider_family_scope_mismatch` →
      REPORT-ONLY, no packet, no memory. Retrieval and injection enforce
      PROVIDER-FAMILY scope before ranking (memory threat model,
      `Spec_Memory_Substrate_v1.md:481`), and the packet was assembled under
      the composing binding's `MemoryScope.provider_family`. Forwarding its
      TEXT across that boundary is a DISCLOSURE leak, which no amount of
      read-only framing fixes. Recomposition cannot rescue either case —
      the statically-injected path is definitionally `memory_runtime`-UNBOUND,
      and the bound path DOES recompose yet still carries the PRIMARY's family
      scope — and fail-closed would convert a silent degradation into a run
      failure. So the honest and only safe action is to REPORT: the degradation
      becomes visible in telemetry, and no cross-scope record is disclosed.
      `_degraded_serve_disposition` owns the two-conjunct split.

    Returns None (zero behavior change) on every servable dispatch and on every
    non-`STANDARD_MEMORY_TOOLS` context.
    """

    if memory_context is None:
        return None
    if memory_context.access_mode is not MemoryAccessMode.STANDARD_MEMORY_TOOLS:
        return None
    if (
        _standard_memory_tools_context(
            provider_name,
            memory_context=memory_context,
            standard_memory_tool_executor=standard_memory_tool_executor,
        )
        is not None
    ):
        return None
    return _degraded_serve_disposition(provider_name, memory_context)


def _emit_degraded_memory_serve_span(
    tracer_provider: Any,
    degraded: _DegradedMemoryServe,
    *,
    provider: str,
    model: str,
    outcome: str = _DISPATCH_OUTCOME_COMPLETED,
    error_type: str | None = None,
) -> None:
    """Emit the ONE `memory.operation` span for a B-83 degraded serve.

    Every attribute reports what ACTUALLY happened, so the two dispositions are
    distinguishable without reading the reason string:

    * REPAIRED (`degraded.rendered` present) — `INJECTION` /
      `access_mode=prompt_extension_packet` / the served packet's hash and
      record count. A successful injection through a different seam, not a
      failure, so no `failure_class` is set.
    * REPORT-ONLY (`degraded.rendered is None`) — `DENIAL` /
      `access_mode=no_memory_access` / `record_count=0` / NO `packet_hash`
      (nothing was served, so claiming a served packet hash would be a lie).
      Mirrors `RuntimeMemoryContextComposer.compose_run_start`'s own
      DENIAL+INJECT shape for the no-memory outcome. `failure_class` is
      deliberately UNSET: no member of the closed `MemoryTelemetryFailureClass`
      describes a provider-scope mismatch, and reusing `POLICY_DENIAL` would
      assert a policy decision no resolver made.

    `memory.degraded_serve` + `.reason` + `.selected_access_mode` carry the
    B-83-specific detail. All of it lands on the memory tracer's own span,
    never on the `gen_ai` span (C-OD-04 §4.3 namespace discipline).

    Uses only existing closed-enum members (`MemoryTelemetryOperationName.
    INJECTION` / `.DENIAL`, `MemoryOperationKind.INJECT`) — adding a member to
    any of the three closed memory enums would be an X-AL-3 design extension,
    which is why the reason is a span-attribute VALUE.
    """

    served = degraded.rendered
    with memory_telemetry_span(
        tracer_provider,
        tracer_name="harness.runtime.llm_dispatch",
        operation_name=(
            MemoryTelemetryOperationName.INJECTION
            if served is not None
            else MemoryTelemetryOperationName.DENIAL
        ),
        operation_kind=MemoryOperationKind.INJECT.value,
        access_mode=(
            MemoryAccessMode.PROMPT_EXTENSION_PACKET.value
            if served is not None
            else MemoryAccessMode.NO_MEMORY_ACCESS.value
        ),
        provider=provider,
        model=model,
        packet_hash=served.packet_hash if served is not None else None,
        record_count=len(served.selected_refs) if served is not None else 0,
    ) as span:
        if span is not None:
            span.set_attribute("memory.degraded_serve", True)
            span.set_attribute("memory.degraded_serve.reason", degraded.reason)
            span.set_attribute(
                "memory.degraded_serve.selected_access_mode",
                degraded.selected_access_mode.value,
            )
            # B-83 [P2-d] — how the provider call this degradation rode on
            # ENDED. A repair that was sent and then timed out still disclosed;
            # a report-only denial still withheld. Both must stay visible, so
            # the span is emitted from a `finally` and says which happened.
            # The enclosing `gen_ai` span records the exception itself (OTel
            # `start_as_current_span` defaults `record_exception=True` /
            # `set_status_on_exception=True`, which this module relies on
            # everywhere rather than calling them explicitly); no exception is
            # raised INSIDE this short span, so the class is carried as an
            # attribute instead.
            span.set_attribute("memory.degraded_serve.dispatch_outcome", outcome)
            if error_type is not None:
                span.set_attribute("memory.degraded_serve.provider_error_type", error_type)


#: B-85 unserved-reason. A span-attribute VALUE for the same reason the B-83
#: reasons are (the C-MEM-19 enums are CLOSED; see the note at
#: `_DEGRADED_REASON_ARM_UNSERVABLE`). `mixed_batch_caller_owned` — the model
#: emitted a memory-tool call and a caller-tool call in ONE batch, and batch
#: atomicity hands the whole response back unprocessed, so the memory call was
#: not answered by THIS dispatch.
_UNSERVED_REASON_MIXED_BATCH_CALLER_OWNED: Final[str] = "mixed_batch_caller_owned"


@dataclass(frozen=True, slots=True)
class _UnservedMemoryToolCalls:
    """B-85 — memory-tool calls a standard-tools loop returned WITHOUT serving.

    Deliberately NOT `_DegradedMemoryServe`. The two decisions are structurally
    non-colliding and describe opposite facts: a degraded serve means the arm
    could not serve the SELECTED MODE at all, while this means the mode WAS
    served (by iteration `k` the loop has already answered `k` rounds of memory
    calls) and exactly one batch went unanswered. Sharing the B-83 carrier
    would force one single-slot decision to stand for both.
    """

    #: How many memory-named calls in the returned batch went unanswered.
    #: Always ≥ 1 — a batch with none is the caller's alone and is not
    #: reported (nothing memory-related happened to it).
    count: int
    reason: str


@dataclass(slots=True)
class _UnservedMemoryToolCallsSink:
    """Mutable single-slot carrier for a B-85 unserved-batch decision.

    Written INSIDE the standard-tools loop functions (neither of which receives
    a tracer) and read by the arm site's `finally`, which owns every memory
    telemetry emission for the dispatch. Single-slot is sufficient: the mixed
    exit RETURNS immediately, so a dispatch populates it at most once, and the
    openai / ollama arms are mutually exclusive `elif` branches so the two
    write sites can never both run. The ollama R5 tools-unsupported fallback
    returns at `iteration == 0` BEFORE any `tool_calls` inspection, so it can
    never co-occur with a write here either — and because this sink is separate
    from `_DegradedMemoryServeSink`, neither decision can overwrite the other.

    One instance per dispatch, created at the arm-selection site; never shared
    across concurrent branches.
    """

    value: _UnservedMemoryToolCalls | None = None


def _emit_unserved_memory_tool_calls_span(
    tracer_provider: Any,
    unserved: _UnservedMemoryToolCalls,
    *,
    provider: str,
    model: str,
    outcome: str = _DISPATCH_OUTCOME_COMPLETED,
    error_type: str | None = None,
) -> None:
    """Emit the ONE `memory.operation` span for a B-85 unserved tool-call batch.

    B-85 posture (3): the mixed-batch exits KEEP their return-whole semantics
    byte-identical — the response is already composed, batch atomicity forbids
    half-committing memory writes from it, and the packet cannot retroactively
    answer a tool call — so the only defect left to close is that NOTHING
    recorded the memory call going unserved. This span records it, truthfully.

    Every attribute reports what ACTUALLY happened, which is why this is NOT
    `_emit_degraded_memory_serve_span`:

    * `standard_tool_call`, not `DENIAL` — no resolver denied anything. The
      caller may re-dispatch, the model may then emit the memory call alone,
      and it will be served. This is "not served at THIS dispatch", not a
      denial, and for the same reason NO `failure_class` is set (none of the
      six closed classes describes it, and `POLICY_DENIAL` would assert a
      policy decision that was never made).
    * `standard_memory_tools`, not `no_memory_access` — the selected mode WAS
      served by this arm. At iteration k>0 the loop has already executed k
      rounds of memory calls; reporting no-memory-access would be false.
    * `record_count=0` and NO `packet_hash` — nothing was served IN RESPONSE to
      these calls, and no packet was rendered at all. Claiming a hash for a
      packet that never went anywhere is the B-87 defect class.

    The B-85-specific detail rides attribute VALUES in a distinct
    `memory.unserved_tool_call.*` namespace, per the B-83 precedent documented
    at the `_DEGRADED_REASON_*` constants: the three memory enums are CLOSED
    per C-MEM-19 and extending one would be an X-AL-3 design extension. All of
    it lands on the memory tracer's own span, never on the `gen_ai` span
    (C-OD-04 §4.3 namespace discipline).

    Emitted from the same `finally` as the B-83 span, so the report survives a
    provider call that raises AFTER the batch was returned; `dispatch_outcome`
    says which happened. Because model-emitted batches are nondeterministic the
    span may fire 0..N times across retry attempts of one logical call — the
    same property the B-83 span has, and deliberately not deduped.
    """

    with memory_telemetry_span(
        tracer_provider,
        tracer_name="harness.runtime.llm_dispatch",
        operation_name=MemoryTelemetryOperationName.STANDARD_TOOL_CALL,
        operation_kind=MemoryOperationKind.STANDARD_TOOL_CALL.value,
        access_mode=MemoryAccessMode.STANDARD_MEMORY_TOOLS.value,
        provider=provider,
        model=model,
        packet_hash=None,
        record_count=0,
    ) as span:
        if span is not None:
            span.set_attribute("memory.unserved_tool_call.count", unserved.count)
            span.set_attribute("memory.unserved_tool_call.reason", unserved.reason)
            span.set_attribute("memory.unserved_tool_call.dispatch_outcome", outcome)
            if error_type is not None:
                span.set_attribute("memory.unserved_tool_call.provider_error_type", error_type)


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


# U-1 (B-18) — Anthropic prompt-cache breakpoint marker (ADR-D3 §1.5 slice 1).
# Slice 1/2 used a fixed `ttl: "5m"`; slice 3b makes the ttl a run-scoped value
# selected from the workload class (`cacheable_epoch.select_cache_ttl`, ADR-D3
# §1.5 line 188 `5min default; 1hr at Persona §6 cost-ceiling cells`). The marker
# is otherwise unchanged (`type: ephemeral`). `"5m"` reproduces the pre-slice-3b
# directive byte-for-byte.
def _anthropic_cache_control(ttl: CacheTTL) -> dict[str, str]:
    """Return the Anthropic ephemeral `cache_control` directive for a ttl tier."""
    return {"type": "ephemeral", "ttl": ttl}


# Anthropic's minimum cacheable-prefix floor is 1024 tokens for smaller models
# and 2048/4096 for larger; slice 1 uses the max-model 4096-tok floor (the
# non-vacuity gate — below it a marker caches nothing = built-but-vacuous).
_ANTHROPIC_MIN_CACHEABLE_TOKENS: Final[int] = 4096
# Documented ~4-chars-per-token heuristic for the non-vacuity size estimate
# (approximation only; the authoritative check is the live cache-hit e2e).
_TOKENS_PER_CHAR_DIVISOR: Final[int] = 4


def _superset_clears_non_vacuity_floor(superset: tuple[Mapping[str, Any], ...]) -> bool:
    """Return True iff the serialized superset clears the ≥4096-tok floor.

    Approximates tokens as ``len(json.dumps(superset)) / 4`` (the documented
    per-char heuristic). Below the floor the ``cache_control`` marker would
    cache nothing (built-but-vacuous) → skip the marker, just send the tools.
    """
    serialized = json.dumps(list(superset), sort_keys=True, separators=(",", ":"))
    return len(serialized) / _TOKENS_PER_CHAR_DIVISOR >= _ANTHROPIC_MIN_CACHEABLE_TOKENS


def _anthropic_tools_with_cache_breakpoint(
    superset: tuple[Mapping[str, Any], ...],
    *,
    extended_thinking: bool,
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL,
) -> list[Mapping[str, Any]]:
    """Return the wire ``tools`` list for the frozen superset, with the
    ``cache_control`` breakpoint on a COPY of the last block when the gates pass.

    Gates (both must pass to emit the marker):
      - extended-thinking mode OFF (§1.5 extended-thinking-invalidates clause —
        handled at the epoch layer; below the epoch primitive slice 1 just skips
        the marker and sends the stable superset unmarked);
      - the superset clears the ≥4096-tok non-vacuity floor.

    Below either gate the superset is sent WITHOUT the marker (still a stable
    prefix; just no caching this dispatch). The frozen tuple's dicts are NEVER
    mutated in place — the marker is attached to a shallow copy of the last dict.
    """
    tools = list(superset)
    if extended_thinking or not _superset_clears_non_vacuity_floor(superset):
        return tools
    # Place the breakpoint on the LAST block that carries an ``input_schema`` — a
    # regular client-side tool. Anthropic *server-side* tool blocks (e.g. the
    # `memory_20250818` tool: ``type`` + ``name`` only, no ``input_schema``) are
    # appended after the client tools; whether a server-tool block accepts
    # ``cache_control`` is unverified, so the marker NEVER lands on one (else a
    # silent cache miss — the failure no-silent-failure forbids). A memory-only
    # superset (no client tool) is sub-floor and already returns unmarked above,
    # so the no-client-tool branch here is a defensive belt-and-suspenders.
    marker_idx = next(
        (i for i in range(len(tools) - 1, -1, -1) if "input_schema" in tools[i]),
        None,
    )
    if marker_idx is None:
        return tools
    tools[marker_idx] = {**tools[marker_idx], "cache_control": _anthropic_cache_control(cache_ttl)}
    return tools


# U-1 (B-18) slice 2 (ADR-D3 §1.5 full parent breakpoint) — move the SINGLE
# `cache_control` breakpoint from the tools block (slice 1) to the LAST system
# block when a system prompt is present. Anthropic caches in
# `tools → system → messages` order and one breakpoint caches everything from
# the start UP TO AND INCLUDING its block, so a marker on the system block
# caches the full `[tools + system]` parent position (§1.5) with exactly ONE
# breakpoint (never exceeds Anthropic's ≤4-breakpoint limit). Requires the
# structured/multi-block `system` content-block array (runtime-spec OQ-1 form),
# emitted at translate-time only — `ProviderAgnosticPayload` stays frozen.
def _combined_prefix_clears_non_vacuity_floor(
    superset: tuple[Mapping[str, Any], ...], system: str
) -> bool:
    """Return True iff the COMBINED tools-superset + system prefix clears the floor.

    The system-block breakpoint caches `[tools + system]`, so the non-vacuity
    estimate is the serialized superset length PLUS the system-prompt length
    (same ~4-chars-per-token heuristic + ≥4096-tok floor as
    ``_superset_clears_non_vacuity_floor`` — no second heuristic forked). Since
    the combined length is ≥ the superset-only length, this is monotone: a
    combined-below-floor prefix implies a superset-only-below-floor prefix, so
    the tools-marking path also stays unmarked (no double-marking, no orphan
    marker).
    """
    serialized = json.dumps(list(superset), sort_keys=True, separators=(",", ":"))
    combined_chars = len(serialized) + len(system)
    return combined_chars / _TOKENS_PER_CHAR_DIVISOR >= _ANTHROPIC_MIN_CACHEABLE_TOKENS


def _anthropic_system_cache_block(
    system: str, cache_ttl: CacheTTL = DEFAULT_CACHE_TTL
) -> list[Mapping[str, Any]]:
    """Return the single-element Anthropic ``system`` content-block array with the
    ``cache_control`` breakpoint on its (only, last) text block.

    This is the OQ-1 structured/multi-block ``system`` form: instead of the plain
    ``system=<string>``, emit ``system=[{"type": "text", "text": <system>,
    "cache_control": {"type": "ephemeral", "ttl": <cache_ttl>}}]`` so the
    breakpoint caches ``[tools + system]``. Only ever produced on the marker path;
    the plain string is preserved on every below-floor / no-superset /
    extended-thinking path (byte-identical to slice 1 / pre-slice-2). ``cache_ttl``
    defaults to ``"5m"`` (byte-identical to pre-slice-3b).
    """
    return [
        {
            "type": "text",
            "text": system,
            "cache_control": _anthropic_cache_control(cache_ttl),
        }
    ]


def _payload_to_anthropic_kwargs(
    payload: ProviderAgnosticPayload,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None,
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL,
    memory_packet: RenderedMemoryPromptPacket | None = None,
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

    U-1 (B-18) — when ``frozen_tool_superset`` is bound, it REPLACES
    ``payload.tools`` on the wire (the deterministic, cache-stable prefix) and a
    SINGLE ``cache_control`` breakpoint is placed at the end of the composed
    cacheable prefix, subject to the extended-thinking + non-vacuity gates.
    ``ProviderAgnosticPayload`` stays frozen — the superset rides the dispatcher,
    never the payload (ADR-F1-faithful: the Anthropic-specific structure lives
    ONLY here at translate-time). ``None`` → byte-identical legacy path
    (``payload.tools``).

    U-1 slice 2 (ADR-D3 §1.5 full parent breakpoint) — WHEN a system prompt is
    present (and the superset is bound + gates pass), the single breakpoint moves
    from the tools block to the LAST **system** block: ``tools[]`` = the frozen
    superset WITHOUT a marker (still the stable prefix) and ``system`` is emitted
    as the OQ-1 content-block array ``[{"type": "text", "text": <system>,
    "cache_control": {...}}]``, which caches ``[tools + system]`` with exactly ONE
    breakpoint. When NO system prompt is present (or the combined prefix is below
    floor, or extended-thinking is on) the slice-1 behavior is preserved verbatim
    (marker on the last client tool block when it clears floor; plain string
    ``system`` otherwise). The system marker is gated on ``frozen_tool_superset
    is not None`` — the frozen superset is the only STABLE tools prefix, so a
    system breakpoint over an unstable per-step ``payload.tools`` would write a
    cache every step that is never read (a silent cost regression). OpenAI/Ollama
    translators are untouched (they keep the ``role:"system"`` message form).
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    # U-1 — `thinking_mode` is not in scope here (extracted at
    # `_extract_anthropic_request_attrs`), so re-derive extended-thinking from
    # `params["thinking"]["type"]` for the breakpoint gates.
    thinking_cfg = payload.params.get("thinking")
    extended_thinking = (
        isinstance(thinking_cfg, Mapping)
        and cast(Mapping[str, Any], thinking_cfg).get("type") == "enabled"
    )
    # --- B-83 [P1-d]: fold the degraded-serve packet into the SINGLE source ---
    # Anthropic's single system source is `params["system"]` when present, else
    # the `system` kwarg. The packet is additive read-only context, NOT a
    # competing base prompt, so it must merge into whichever source exists
    # rather than become a second one — otherwise the repair hard-fails every
    # dispatch whose payload carries `params["system"]`. Folded BEFORE the
    # `place_on_system` decision so the cache block covers the merged text.
    # A genuine TWO-BASE collision (dispatch `system` AND `params["system"]`)
    # is left alone and still raises below, verbatim.
    #
    # B-83 [P2-c]: "is there an existing source?" is keyed on PRESENCE
    # (`"system" in payload.params`), because that is exactly what the conflict
    # check below keys on (`"system" in kwargs`). Keying on truthiness instead
    # let two VALID shapes slip past — the SDK's content-block ARRAY (the same
    # `[{"type": "text", ...}]` form `_anthropic_system_cache_block` itself
    # emits) and the empty string — into the `system`-variable branch, where the
    # unrecognized-but-present `params["system"]` then collided and turned a
    # working dispatch into `PromptInjectionConflictError`. The fold predicate
    # and the conflict predicate MUST agree on what "present" means.
    # `_content_with_appended_packet` covers every value shape and its sequence
    # branch appends a `{"type": "text", ...}` block — a valid Anthropic
    # `TextBlockParam` (`cache_control` is optional) — so no divergent
    # serialization is introduced here.
    params_system_present = "system" in payload.params
    folded_params_system: str | list[Any] | None = None
    if memory_packet is not None and not (system and params_system_present):
        if params_system_present:
            folded_params_system = _content_with_appended_packet(
                payload.params.get("system"), memory_packet
            )
        else:
            system = append_rendered_memory_packet(system, memory_packet)
    # U-1 slice 2 — decide ONCE where the single breakpoint lands, so the tools
    # branch and the system branch never each mark independently (double-marking).
    # The system position is used iff a system prompt is present AND the stable
    # frozen superset is bound AND extended-thinking is off AND the COMBINED
    # `[tools + system]` prefix clears the non-vacuity floor.
    place_on_system = (
        bool(system)
        and frozen_tool_superset is not None
        and not extended_thinking
        and _combined_prefix_clears_non_vacuity_floor(frozen_tool_superset, system)
    )
    if frozen_tool_superset is not None:
        # The frozen superset REPLACES `payload.tools` (visibility-only per the
        # C10 verdict; execution stays registry-gated). When the breakpoint is on
        # the system block the superset is sent UNMARKED (still the stable prefix);
        # otherwise the slice-1 tools-marking path applies (the extended-thinking +
        # superset-only floor gates live inside the helper).
        if place_on_system:
            kwargs["tools"] = list(frozen_tool_superset)
        else:
            kwargs["tools"] = _anthropic_tools_with_cache_breakpoint(
                frozen_tool_superset, extended_thinking=extended_thinking, cache_ttl=cache_ttl
            )
    elif payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    if folded_params_system is not None:
        # The payload-owned system source, with the packet merged in — a string
        # when it arrived as one, a block array (originals preserved, one text
        # block appended) when it arrived as one. Never wrapped in the OQ-1
        # cache block: a `params["system"]` was never breakpointed before B-83
        # either, so its caching posture is unchanged.
        kwargs["system"] = folded_params_system
    if system:
        if "system" in kwargs:
            raise PromptInjectionConflictError("anthropic", 'params["system"]')
        # slice 2 — the OQ-1 content-block array WITH the breakpoint when this is
        # the marker position; else the plain string (byte-identical to slice 1).
        kwargs["system"] = (
            _anthropic_system_cache_block(system, cache_ttl) if place_on_system else system
        )
    # B-INTERSTEP — Anthropic carries `system` as a top-level kwarg (not a message),
    # so the upstream context goes at messages index 0 (post-`params`-merge).
    _inject_upstream_context_message(kwargs, upstream)
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
    payload: ProviderAgnosticPayload,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``chat.completions.create`` kwargs.

    R-PM-1 PR #1 — ``system`` (active prompt content) injects as a leading
    ``{"role":"system","content":...}`` message (the OpenAI base-prompt route),
    **after** the ``params`` merge so a ``params["messages"]`` override cannot
    silently drop it. B-INTERSTEP — the upstream-context ``user`` message injects
    AFTER the system injection (so it lands after any leading system message and
    does not mask its conflict check).
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    _inject_leading_system_message(kwargs, system, "openai")
    _inject_upstream_context_message(kwargs, upstream)
    return kwargs


def _payload_to_ollama_kwargs(
    payload: ProviderAgnosticPayload,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``ollama.chat`` kwargs.

    R-PM-1 PR #1 — ``system`` (active prompt content) injects as a leading
    ``{"role":"system","content":...}`` message (the Ollama base-prompt route),
    **after** the ``params`` merge so a ``params["messages"]`` override cannot
    silently drop it. B-INTERSTEP — the upstream-context ``user`` message injects
    AFTER the system injection (so it lands after any leading system message and
    does not mask its conflict check).
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    _inject_leading_system_message(kwargs, system, "ollama")
    _inject_upstream_context_message(kwargs, upstream)
    return kwargs


def _payload_to_external_cli_prompt(
    payload: ProviderAgnosticPayload,
    *,
    provider: str,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    memory_packet: RenderedMemoryPromptPacket | None = None,
) -> str:
    """Translate provider-neutral messages to one text prompt for local CLIs.

    R-CLI-1 v1 is text-only. Non-empty tools are rejected before the subprocess
    boundary so a local CLI cannot execute or negotiate tools accidentally.

    ``memory_packet`` (B-83 [P1-d]) folds a degraded-serve packet into the ONE
    effective system source — the payload's leading ``role:"system"`` message
    when it has one, else the ``system`` argument — so the repair can never
    become a second source and trip the conflict check below.
    """
    if payload.tools:
        raise LLMDispatchPayloadShapeError(
            f"external CLI provider {provider!r} is text-only; tools are not supported"
        )

    messages = list(payload.messages)
    leading_system = messages[0] if (messages and messages[0].get("role") == "system") else None
    if memory_packet is not None and not (system and leading_system is not None):
        if leading_system is not None:
            # B-83 [P2-b] — serialize the existing content EXACTLY as the render
            # loop below would (`_external_cli_message_content`, the shared
            # authority), then append. Passing None for a non-string content
            # would REPLACE the step's own system instructions with the packet
            # alone — and since the external-CLI arm is text-only it ALWAYS
            # degrades `standard_memory_tools`, making that the common path here,
            # not an edge case.
            messages[0] = {
                **leading_system,
                "content": append_rendered_memory_packet(
                    _external_cli_message_content(leading_system.get("content", "")),
                    memory_packet,
                ),
            }
        else:
            system = append_rendered_memory_packet(system, memory_packet)
    if system and messages and messages[0].get("role") == "system":
        raise PromptInjectionConflictError(provider, 'messages[0] role:"system"')

    parts: list[str] = []
    if system:
        parts.append(f"system:\n{system}")
    if upstream is not None:
        rendered_upstream = json.dumps(dict(upstream), sort_keys=True, default=str)
        parts.append(f"user:\n{_UPSTREAM_CONTEXT_PREFIX}{rendered_upstream}")
    for message in messages:
        role = message.get("role", "user")
        if not isinstance(role, str) or not role:
            role = "user"
        parts.append(f"{role}:\n{_external_cli_message_content(message.get('content', ''))}")
    return "\n\n".join(parts)


def _external_cli_message_content(content: object) -> str:
    """Render one message ``content`` to the external-CLI prompt's text form.

    The single authority for that serialization, read by the render loop above
    AND by the B-83 [P2-b] packet fold, so a repaired dispatch can never
    represent the same content differently from an unrepaired one.
    """

    if isinstance(content, str):
        return content
    return json.dumps(content, sort_keys=True, default=str)


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
    request_kwargs: Mapping[str, Any],
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs, _AnthropicRequestAttrs]:
    usage = getattr(response, "usage", None)
    usage_attrs = _UsageAttrs(
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
        response_id=getattr(response, "id", None),
    )
    # B-18-CACHE-TTL-OBSERVABILITY — scan the TRANSLATED wire kwargs (tools /
    # system / messages), NOT `payload.messages`: the U-1 cache breakpoint is
    # placed on the tools/system block at translate-time, so the pre-B-18
    # messages-only scan never observed it.
    cache_breakpoint_id, cache_ttl_seconds = _extract_anthropic_cache_request_attrs(request_kwargs)
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
    upstream: Mapping[str, Any] | None = None,
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None,
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL,
    memory_packet: RenderedMemoryPromptPacket | None = None,
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
    kwargs = _payload_to_anthropic_kwargs(
        payload, system, upstream, frozen_tool_superset, cache_ttl, memory_packet
    )
    # Seed the per-turn mutable loop list from the TRANSLATED `kwargs["messages"]`
    # (NOT `payload.messages`) so it carries the `params["messages"]` merge result
    # AND the B-INTERSTEP upstream-context injection — otherwise the tool-loop's
    # model calls silently lose the inter-step context while the non-HITL Anthropic
    # path keeps it (Codex review). The loop then appends tool_result turns to it.
    messages = list(kwargs["messages"])
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
            return _anthropic_response_bundle(response, payload, model, kwargs)

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
    upstream: Mapping[str, Any] | None = None,
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None,
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL,
    memory_packet: RenderedMemoryPromptPacket | None = None,
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
    kwargs = _payload_to_anthropic_kwargs(
        payload, system, upstream, frozen_tool_superset, cache_ttl, memory_packet
    )

    response = await execute_with_memory_callbacks(
        adapter=adapter,
        model=model,
        messages_create_kwargs=kwargs,
        backend=backend,
        backend_enum=configured_backend,
        tracer=tracer,
        context_editing_active=context_editing_active,
    )

    return _anthropic_response_bundle(response, payload, model, kwargs)


async def _dispatch_anthropic(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None,
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL,
    memory_packet: RenderedMemoryPromptPacket | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs, _AnthropicRequestAttrs]:
    """Anthropic provider branch — ``client.messages.create(...)``.

    ``memory_packet`` (B-83 [P1-d]) is the degraded-serve repair packet, folded
    into the SINGLE effective system source by the translator. ``None`` — every
    caller but a repaired dispatch — is byte-identical to pre-B-83.
    """
    kwargs = _payload_to_anthropic_kwargs(
        payload, system, upstream, frozen_tool_superset, cache_ttl, memory_packet
    )
    response = await adapter.client.messages.create(model=model, **kwargs)

    return _anthropic_response_bundle(response, payload, model, kwargs)


async def _dispatch_openai(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    memory_packet: RenderedMemoryPromptPacket | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """OpenAI provider branch — ``client.chat.completions.create(...)``.

    ``memory_packet`` (B-83 [P1-d]) is the degraded-serve repair packet, folded
    into the SINGLE effective system source by the translator. ``None`` — every
    caller but a repaired dispatch — is byte-identical to pre-B-83.
    """
    kwargs = _payload_to_openai_kwargs(payload, system, upstream)
    if memory_packet is not None:
        _fold_memory_packet_into_system(kwargs, memory_packet)
    response = await adapter.client.chat.completions.create(model=model, **kwargs)
    return _openai_response_bundle(response)


@dataclass(frozen=True, slots=True)
class _PreparedMemoryToolCall:
    """One memory tool call fully resolved + validated, NOT yet executed.

    Batch preparation is what makes the memory tool loops safe against a
    partially-committed batch: every call in a response is resolved and
    validated BEFORE any of them runs, so a malformed *later* call cannot abort
    the dispatch after an *earlier* (possibly write-like) call already committed
    durable memory state. That matters because the abort can be retryable —
    ``_classify_provider_exception`` (`retry_breaker_fallback.py`) maps every
    exception other than ``LLMDispatchProviderUnreachableError`` /
    ``LLMDispatchPayloadShapeError`` / ``MemoryToolExecutionInputError``
    (fail-fast since B-84) / 401-403 to ``TRANSIENT_RETRY``, so
    ``RetryBreakerFallbackDispatcher`` re-runs the whole dispatch from the top
    and the already-committed call executes a second time.

    ``tool_call_id`` is OpenAI-only: ollama's typed client exposes no tool-call
    id at all (`ollama/_types.py:304-355`), so its result turn correlates by
    name instead.
    """

    tool_name: MemoryToolName
    request: MemoryToolExecutionRequest
    tool_call_id: str | None = None


#: The dotted C-MEM-14 provider-neutral identities, as a membership set.
_MEMORY_TOOL_NAMES: Final[frozenset[str]] = frozenset(tool.value for tool in MemoryToolName)


def _all_calls_are_memory_tools(
    names: Sequence[str | None],
    memory_names: frozenset[str],
) -> bool:
    """True only when EVERY call in the batch names a memory tool we advertised.

    A batch containing any other call — a legitimate caller-advertised tool that
    survived the dedup filter, a malformed tool_call shape, or a hallucinated
    name — belongs to the CALLER. The bare dispatch paths (`_dispatch_openai` /
    `_dispatch_ollama`) return every tool_call to the caller untouched, whatever
    it names; auto-injecting memory tools must not turn that into a raise, or
    enabling automatic memory would break ordinary tool workflows.
    """
    return all(name is not None and name in memory_names for name in names)


def _record_unserved_memory_tool_calls(
    sink: _UnservedMemoryToolCallsSink,
    names: Sequence[str | None],
    memory_names: frozenset[str],
) -> None:
    """B-85 — report the memory calls a caller-owned batch left unanswered.

    Takes the SAME `(names, memory_names)` inputs `_all_calls_are_memory_tools`
    just rejected the batch on, so the count can never be computed against a
    different membership rule than the guard used.

    Writes NOTHING when the batch names no memory tool at all: a purely
    caller-owned batch is the ordinary tool workflow the memory tools were
    injected alongside, nothing memory-related went unserved in it, and a span
    claiming otherwise would be false. Both provider loops route here so the
    two exits cannot drift apart.
    """

    count = sum(1 for name in names if name is not None and name in memory_names)
    if count == 0:
        return
    sink.value = _UnservedMemoryToolCalls(
        count=count,
        reason=_UNSERVED_REASON_MIXED_BATCH_CALLER_OWNED,
    )


def _add_optional_tokens(running: int | None, turn: int | None) -> int | None:
    """Sum two optional token counts, treating ``None`` as ABSENT — not zero.

    A turn the provider reported nothing for must neither invent a ``0`` total
    nor erase counts already accumulated.
    """
    if running is None:
        return turn
    if turn is None:
        return running
    return running + turn


def _accumulated_usage(running: _UsageAttrs, turn: _UsageAttrs) -> _UsageAttrs:
    """Fold one continuation turn's usage into a memory tool loop's totals.

    Every provider call in the loop consumes tokens, so bundling only the FINAL
    response's usage silently dropped every continuation turn from turn capture,
    ``gen_ai.usage.*`` and cost attribution. ``response_id`` is NOT accumulated —
    it identifies ONE provider response, so the bundle keeps the final turn's
    (unchanged semantics; ollama has none either way).
    """
    return _UsageAttrs(
        input_tokens=_add_optional_tokens(running.input_tokens, turn.input_tokens),
        output_tokens=_add_optional_tokens(running.output_tokens, turn.output_tokens),
        response_id=turn.response_id,
    )


#: A loop's usage accumulator before any provider call — all-absent, not zero.
_NO_USAGE: Final[_UsageAttrs] = _UsageAttrs(
    input_tokens=None,
    output_tokens=None,
    response_id=None,
)


def _memory_tool_loop_exhausted(provider_label: str, max_iterations: int) -> RuntimeError:
    """The C-MEM-14 continuation-loop bound error, shared by both provider loops.

    Deliberately the SAME generic ``RuntimeError`` both loops have always
    raised — introducing a distinct type here would change how
    ``_classify_provider_exception`` routes loop exhaustion (today:
    ``TRANSIENT_RETRY``), which is a separate decision from the
    execute-before-raise defect this shape exists to close.
    """
    return RuntimeError(
        f"{provider_label} standard memory tool loop exceeded {max_iterations} continuation turns"
    )


async def _dispatch_openai_with_standard_memory_tools(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    memory_context: RuntimeMemoryContext,
    standard_memory_tool_executor: Any,
    step_context: StepExecutionContext,
    step_id: str,
    unserved_sink: _UnservedMemoryToolCallsSink,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    max_iterations: int = 16,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """OpenAI provider branch with C-MEM-14 standard memory tool continuation.

    ``unserved_sink`` receives the B-85 report when a MIXED batch is handed
    back whole. This function has no tracer; the caller's ``finally`` owns the
    emission, as it does for the B-83 sink.
    """
    kwargs = _payload_to_openai_kwargs(payload, system, upstream)
    kwargs["tools"] = _openai_tools_with_standard_memory(kwargs.get("tools"), memory_context)
    messages = list(kwargs["messages"])
    kwargs["messages"] = messages

    usage = _NO_USAGE
    for iteration in range(max_iterations):
        response = await adapter.client.chat.completions.create(model=model, **kwargs)
        # Every call in the loop consumes tokens — fold each turn in before
        # any exit, so a continuation turn is never dropped from usage.
        usage = _accumulated_usage(usage, _openai_usage_attrs(response))
        response_mapping = _response_to_mapping(response)
        tool_calls = _openai_tool_calls(response_mapping)
        if not tool_calls:
            return (response_mapping, usage)
        if not _all_calls_are_memory_tools(
            [_function_tool_name(call) for call in tool_calls],
            _OPENAI_MEMORY_TOOL_CALL_NAMES,
        ):
            # The batch is the CALLER's — hand the whole response back
            # unprocessed (bare-path parity) and execute NOTHING from it, so a
            # mixed batch cannot half-commit memory before control returns.
            # B-85 posture (3): the memory call inside a MIXED batch therefore
            # goes unserved AND un-ledgered. Still not repairable at this site —
            # the response is already composed and the packet cannot
            # retroactively answer a tool call — so the return semantics are
            # kept byte-identical and the fact is REPORTED instead.
            _record_unserved_memory_tool_calls(
                unserved_sink,
                [_function_tool_name(call) for call in tool_calls],
                _OPENAI_MEMORY_TOOL_CALL_NAMES,
            )
            return (response_mapping, usage)
        # Validate the batch BEFORE the bound check: a malformed memory call is
        # a fail-fast payload-shape error, and letting the generic (retryable)
        # exhaustion error mask it on the terminal turn would replay up to
        # `max_iterations` provider calls for a request that can never succeed.
        prepared = _openai_prepared_memory_tool_calls(
            tool_calls,
            memory_context=memory_context,
            step_context=step_context,
            step_id=step_id,
            model=model,
        )
        if iteration + 1 >= max_iterations:
            # The batch is valid but no iteration budget remains to send its
            # results back, so the dispatch fails whatever it returns. Raise
            # BEFORE executing — otherwise a terminal `memory.write_note` /
            # `memory.propose_promotion` / `memory.request_redaction` commits
            # for a dispatch that reports failure, and the failure is retryable
            # (see `_PreparedMemoryToolCall`), so the sequence can repeat.
            raise _memory_tool_loop_exhausted("OpenAI", max_iterations)

        messages.append(_openai_assistant_message(response_mapping))
        messages.extend(
            _openai_memory_tool_result_messages(
                prepared,
                standard_memory_tool_executor=standard_memory_tool_executor,
            )
        )

    raise _memory_tool_loop_exhausted("OpenAI", max_iterations)


def _openai_usage_attrs(response: Any) -> _UsageAttrs:
    usage = getattr(response, "usage", None)
    return _UsageAttrs(
        input_tokens=getattr(usage, "prompt_tokens", None),
        output_tokens=getattr(usage, "completion_tokens", None),
        response_id=getattr(response, "id", None),
    )


def _openai_response_bundle(response: Any) -> tuple[Mapping[str, Any], _UsageAttrs]:
    return (_response_to_mapping(response), _openai_usage_attrs(response))


def _openai_assistant_message(response: Mapping[str, Any]) -> dict[str, Any]:
    message = _openai_first_message(response)
    return dict(message)


def _openai_tool_calls(response: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    message = _openai_first_message(response)
    tool_calls = message.get("tool_calls")
    if tool_calls is None:
        return ()
    if isinstance(tool_calls, str | bytes) or not isinstance(tool_calls, Sequence):
        raise LLMDispatchPayloadShapeError("OpenAI tool_calls must be a sequence")
    calls: list[Mapping[str, Any]] = []
    for item in cast(Sequence[object], tool_calls):
        if not isinstance(item, Mapping):
            raise LLMDispatchPayloadShapeError("OpenAI tool_call entries must be mappings")
        calls.append(cast(Mapping[str, Any], item))
    return tuple(calls)


def _openai_first_message(response: Mapping[str, Any]) -> Mapping[str, Any]:
    choices = response.get("choices")
    if isinstance(choices, str | bytes) or not isinstance(choices, Sequence) or not choices:
        raise LLMDispatchPayloadShapeError("OpenAI response choices missing")
    first = cast(Sequence[object], choices)[0]
    if not isinstance(first, Mapping):
        raise LLMDispatchPayloadShapeError("OpenAI response choice must be a mapping")
    first_mapping = cast(Mapping[str, object], first)
    message = first_mapping.get("message")
    if not isinstance(message, Mapping):
        raise LLMDispatchPayloadShapeError("OpenAI response choice.message missing")
    return cast(Mapping[str, Any], message)


def _openai_prepared_memory_tool_calls(
    calls: Sequence[Mapping[str, Any]],
    *,
    memory_context: RuntimeMemoryContext,
    step_context: StepExecutionContext,
    step_id: str,
    model: str,
) -> tuple[_PreparedMemoryToolCall, ...]:
    """Resolve + validate the COMPLETE batch before any of it executes.

    Every failure mode of a single call — missing id, unknown tool name,
    malformed arguments, a `scope_ref` that does not match the context — is
    raised here, where nothing has run yet. See `_PreparedMemoryToolCall`.
    """
    prepared: list[_PreparedMemoryToolCall] = []
    for call in calls:
        tool_call_id = call.get("id")
        if not isinstance(tool_call_id, str) or not tool_call_id:
            raise LLMDispatchPayloadShapeError("OpenAI memory tool_call missing string id")
        tool_name, arguments = _openai_memory_tool_name_and_arguments(call)
        prepared.append(
            _PreparedMemoryToolCall(
                tool_name=tool_name,
                request=MemoryToolExecutionRequest(
                    tool_name=tool_name,
                    arguments=arguments,
                    context=_standard_memory_tool_context(
                        arguments,
                        tool_name=tool_name,
                        memory_context=memory_context,
                        step_context=step_context,
                        step_id=step_id,
                        provider="openai",
                        model=model,
                    ),
                ),
                tool_call_id=tool_call_id,
            )
        )
    return tuple(prepared)


def _openai_memory_tool_result_messages(
    prepared: Sequence[_PreparedMemoryToolCall],
    *,
    standard_memory_tool_executor: Any,
) -> list[dict[str, Any]]:
    """Execute an ALREADY-VALIDATED batch in order and build its result turns."""
    messages: list[dict[str, Any]] = []
    for call in prepared:
        result = standard_memory_tool_executor.execute(call.request)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.tool_call_id,
                # Same wire boundary as the tools[] array — the tool-result turn
                # echoes the function name the provider called, so it carries the
                # wire name.
                "name": _OPENAI_MEMORY_TOOL_WIRE_NAMES[call.tool_name],
                "content": json.dumps(result, sort_keys=True, separators=(",", ":"), default=str),
            }
        )
    return messages


def _openai_memory_tool_name_and_arguments(
    call: Mapping[str, Any],
) -> tuple[MemoryToolName, dict[str, object]]:
    function = call.get("function")
    if not isinstance(function, Mapping):
        raise LLMDispatchPayloadShapeError("OpenAI memory tool_call.function missing")
    function_mapping = cast(Mapping[str, object], function)
    name = function_mapping.get("name")
    if not isinstance(name, str) or not name:
        raise LLMDispatchPayloadShapeError("OpenAI memory tool_call.function.name missing")
    # The model can only call a name we advertised, i.e. a wire name; the dotted
    # provider-neutral identity is still accepted as a tolerant second reading so
    # the resolve path stays byte-compatible with pre-wire-name callers.
    tool_name = _OPENAI_MEMORY_TOOL_FROM_WIRE.get(name)
    if tool_name is None:
        try:
            tool_name = MemoryToolName(name)
        except ValueError as exc:
            raise LLMDispatchPayloadShapeError(
                f"OpenAI standard memory loop received non-memory tool {name!r}"
            ) from exc
    raw_arguments = function_mapping.get("arguments")
    if isinstance(raw_arguments, str):
        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError as exc:
            raise LLMDispatchPayloadShapeError(
                f"OpenAI memory tool {name!r} arguments are not valid JSON"
            ) from exc
        if not isinstance(parsed, Mapping):
            raise LLMDispatchPayloadShapeError(
                f"OpenAI memory tool {name!r} arguments must decode to an object"
            )
        return (tool_name, dict(cast(Mapping[str, object], parsed)))
    if isinstance(raw_arguments, Mapping):
        return (tool_name, dict(cast(Mapping[str, object], raw_arguments)))
    raise LLMDispatchPayloadShapeError(f"OpenAI memory tool {name!r} arguments missing")


def _memory_tools_declaring(field: str) -> frozenset[MemoryToolName]:
    """Which C-MEM-14 tools declare ``field`` in their own input schema.

    Same authority ``_bind_schema_fixed_value`` uses when it binds a fixed enum
    value (presence in the contract's ``properties``), and the same partition
    the executor itself enforces: ``StandardMemoryToolExecutor._require_scope_ref``
    is reached ONLY from ``_search`` and ``_write_note``
    (`memory_tool_executor.py:195` / `:262`) — exactly the two contracts that
    declare ``scope_ref``.
    """
    return frozenset(
        entry.tool
        for entry in MEMORY_TOOL_CONTRACTS
        if isinstance(properties := entry.contract.input_schema.get("properties"), Mapping)
        and field in properties
    )


#: `memory.read` / `memory.propose_promotion` / `memory.request_redaction` declare
#: NO `scope_ref` and set `additionalProperties: false`
#: (`harness-as/src/harness_as/memory_tool_contracts.py`), so a schema-conformant
#: model CANNOT send one. Requiring it in the arguments for every tool — as this
#: dispatch-side check originally did — made three of the five ADVERTISED tools
#: permanently unreachable: they failed here before ever reaching the executor.
#: The authoritative `scope_ref` was never the argument anyway; it is
#: `RuntimeMemoryContext.scope_ref`, and the argument is only a cross-check,
#: which is exactly why it can be scoped to the tools that carry one.
_MEMORY_TOOLS_DECLARING_SCOPE_REF: Final[frozenset[MemoryToolName]] = _memory_tools_declaring(
    "scope_ref"
)


def _standard_memory_tool_context(
    arguments: Mapping[str, object],
    *,
    tool_name: MemoryToolName,
    memory_context: RuntimeMemoryContext,
    step_context: StepExecutionContext,
    step_id: str,
    provider: str,
    model: str,
) -> MemoryToolExecutionContext:
    if memory_context.record_scope is None:
        raise MemoryToolExecutionInputError(
            "standard memory tool dispatch requires RuntimeMemoryContext.record_scope"
        )
    if memory_context.scope_ref is None:
        raise MemoryToolExecutionInputError(
            "standard memory tool dispatch requires RuntimeMemoryContext.scope_ref"
        )
    if tool_name in _MEMORY_TOOLS_DECLARING_SCOPE_REF:
        scope_ref = arguments.get("scope_ref")
        if not isinstance(scope_ref, str) or not scope_ref:
            raise MemoryToolExecutionInputError("standard memory tool call requires scope_ref")
        if scope_ref != memory_context.scope_ref:
            raise MemoryToolExecutionInputError(
                "standard memory tool scope_ref does not match context"
            )
    token_budget = memory_context.packet.token_budget if memory_context.packet is not None else 0
    return MemoryToolExecutionContext(
        run_id=memory_context.run_id,
        workflow_id=step_context.workflow_id,
        workload_class=None,
        step_id=step_id,
        provider=provider,
        model=model,
        cli_profile=memory_context.selection.cli_profile_ref,
        scope=memory_context.record_scope,
        scope_ref=memory_context.scope_ref,
        policy_ref=memory_context.policy_ref,
        token_budget=token_budget,
        timestamp=datetime.now(UTC),
        actor=step_context.parent_actor,
    )


# --- OpenAI memory-tool wire names ------------------------------------------
# OpenAI's Chat Completions API constrains ``tools[].function.name`` to
# ``^[a-zA-Z0-9_-]{1,64}$``; a dot is rejected with an HTTP 400 before the model
# is ever reached. The C-MEM-14 tool identities (`Spec_Memory_Substrate_v1.md`
# §485-497) are PROVIDER-NEUTRAL and dotted (``memory.search`` ...), so the
# dot -> underscore encoding is owned by this OpenAI adapter boundary and NOT by
# the `MemoryToolName` enum (renaming the enum would leak a provider constraint
# into the provider-neutral contract).
#
# The map is an EXPLICIT table rather than a computed transform: a computed
# ``value.replace(".", "_")`` is not provably injective against future enum
# members, whereas an explicit table plus the import-time guard below fails loud
# the moment a new `MemoryToolName` lands without a wire name, two wire names
# collide, or a wire name violates the provider's name grammar.
_OPENAI_MEMORY_TOOL_WIRE_NAMES: Final[dict[MemoryToolName, str]] = {
    MemoryToolName.SEARCH: "memory_search",
    MemoryToolName.READ: "memory_read",
    MemoryToolName.WRITE_NOTE: "memory_write_note",
    MemoryToolName.PROPOSE_PROMOTION: "memory_propose_promotion",
    MemoryToolName.REQUEST_REDACTION: "memory_request_redaction",
}

_OPENAI_TOOL_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def _invert_openai_memory_tool_wire_names() -> dict[str, MemoryToolName]:
    """Invert the wire-name table, failing loud at import on an unusable table."""
    missing = [tool for tool in MemoryToolName if tool not in _OPENAI_MEMORY_TOOL_WIRE_NAMES]
    if missing:
        raise LLMDispatchBindError(
            f"OpenAI memory tool wire name missing for {[tool.value for tool in missing]!r}"
        )
    inverted: dict[str, MemoryToolName] = {}
    for tool, wire in _OPENAI_MEMORY_TOOL_WIRE_NAMES.items():
        if _OPENAI_TOOL_NAME_PATTERN.match(wire) is None:
            raise LLMDispatchBindError(
                f"OpenAI memory tool wire name {wire!r} for {tool.value!r} violates "
                r"^[a-zA-Z0-9_-]{1,64}$"
            )
        if wire in inverted:
            raise LLMDispatchBindError(f"OpenAI memory tool wire name {wire!r} is not unique")
        inverted[wire] = tool
    return inverted


_OPENAI_MEMORY_TOOL_FROM_WIRE: Final[dict[str, MemoryToolName]] = (
    _invert_openai_memory_tool_wire_names()
)

#: Every spelling an OpenAI tool_call can carry and still be OURS — the wire
#: names we actually advertise, plus the dotted identities the inbound resolver
#: tolerates for byte-compat. Anything outside this set is the caller's.
_OPENAI_MEMORY_TOOL_CALL_NAMES: Final[frozenset[str]] = _MEMORY_TOOL_NAMES | frozenset(
    _OPENAI_MEMORY_TOOL_FROM_WIRE
)


def _openai_tools_with_standard_memory(
    existing_tools: object,
    memory_context: RuntimeMemoryContext,
) -> list[dict[str, Any]]:
    # Drop a caller-supplied tool that names one of the injected memory tools
    # under EITHER spelling: the wire name (which would be a genuine duplicate
    # ``function.name`` in the emitted array) or the provider-neutral dotted
    # identity (which names the same tool AND would itself trip OpenAI's
    # name grammar if forwarded).
    memory_tool_names = {entry.tool.value for entry in MEMORY_TOOL_CONTRACTS} | set(
        _OPENAI_MEMORY_TOOL_FROM_WIRE
    )
    preserved: list[dict[str, Any]] = []
    if isinstance(existing_tools, Sequence) and not isinstance(existing_tools, str | bytes):
        for tool in cast(Sequence[object], existing_tools):
            if not isinstance(tool, Mapping):
                continue
            tool_mapping = dict(cast(Mapping[str, Any], tool))
            if _function_tool_name(tool_mapping) in memory_tool_names:
                continue
            preserved.append(tool_mapping)
    return [*preserved, *_openai_standard_memory_tools(memory_context)]


def _openai_standard_memory_tools(memory_context: RuntimeMemoryContext) -> list[dict[str, Any]]:
    if memory_context.scope_ref is None:
        raise MemoryToolExecutionInputError(
            "standard memory tool schema injection requires RuntimeMemoryContext.scope_ref"
        )
    tools: list[dict[str, Any]] = []
    for entry in MEMORY_TOOL_CONTRACTS:
        parameters: dict[str, object] = deepcopy(entry.contract.input_schema)
        properties = parameters.get("properties")
        if not isinstance(properties, dict):
            raise MemoryToolExecutionInputError("memory tool input schema properties missing")
        schema_properties = cast("dict[str, object]", properties)
        _bind_schema_fixed_value(schema_properties, "scope_ref", memory_context.scope_ref)
        _bind_schema_fixed_value(schema_properties, "policy_ref", memory_context.policy_ref)
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": _OPENAI_MEMORY_TOOL_WIRE_NAMES[entry.tool],
                    "description": entry.contract.description,
                    "parameters": parameters,
                },
            }
        )
    return tools


def _bind_schema_fixed_value(properties: dict[str, object], name: str, value: str) -> None:
    if name in properties:
        properties[name] = {"type": "string", "enum": [value]}


def _function_tool_name(tool: Mapping[str, Any]) -> str | None:
    """Read ``function.name`` off the shared ``{"type":"function",...}`` shape.

    OpenAI and Ollama advertise function tools — and echo function CALLS back —
    under the identical envelope, so this reader is provider-neutral and serves
    both the outbound ``tools[]`` array and the inbound ``tool_calls[]`` list.
    """
    function = tool.get("function")
    if not isinstance(function, Mapping):
        return None
    function_mapping = cast("Mapping[str, object]", function)
    name = function_mapping.get("name")
    return name if isinstance(name, str) else None


def _fold_memory_packet_into_system(
    kwargs: dict[str, Any],
    rendered: RenderedMemoryPromptPacket,
) -> None:
    """Merge a packet into the ONE effective system source, post-params-merge.

    B-83 [P1-b]. The naive repair — handing the packet to
    `_payload_to_ollama_kwargs` as its ``system`` argument — creates a SECOND
    system source whenever the payload already leads with a
    ``{"role":"system"}`` message, and `_inject_leading_system_message` then
    raises `PromptInjectionConflictError` by design. That would break a
    previously-working tool-free dispatch for every step that supplies its own
    system prompt (the idiomatic OpenAI/Ollama shape).

    So the packet is folded into whatever system text the dispatch ALREADY
    resolved — appended through `append_rendered_memory_packet`, the same seam
    the selected-mode path uses, so separator and ordering semantics cannot
    drift. Exactly one leading system message either way.

    Operates on the FINISHED kwargs (post-`params` merge) for the same reason
    `_inject_leading_system_message` does: a ``params["messages"]`` override can
    replace the message list wholesale, so a payload-level merge could miss the
    real leading system message and reintroduce the two-source collision.
    """

    messages: list[Mapping[str, Any]] = list(kwargs.get("messages", ()))
    if messages and messages[0].get("role") == "system":
        head = messages[0]
        kwargs["messages"] = [
            {**head, "content": _content_with_appended_packet(head.get("content"), rendered)},
            *messages[1:],
        ]
        return
    kwargs["messages"] = [{"role": "system", "content": rendered.content}, *messages]


def _content_with_appended_packet(
    content: object,
    rendered: RenderedMemoryPromptPacket,
) -> str | list[Any]:
    """Append a packet to a message ``content``, PRESERVING its representation.

    B-83 [P2-a]. OpenAI accepts a system message's ``content`` as either a
    plain string or a content-part ARRAY. Coercing the array through ``str()``
    before appending would put a Python repr on the wire — the structure is
    silently destroyed and the parts stop being parts. So each shape is folded
    in its own terms:

    * ``str`` / ``None`` — string append through the shared seam.
    * a parts SEQUENCE — the packet becomes one ADDITIONAL
      ``{"type": "text", "text": ...}`` part (the same part shape this module
      already emits at the Anthropic system block and the external-CLI
      response), with every original part preserved in order.
    * anything else — JSON-serialized first (``sort_keys`` + ``default=str``,
      matching `_inject_upstream_context_message` and the external-CLI
      renderer), then string-appended. Lossy-free and never a raise: an
      unexpected shape is not this repair's problem to adjudicate.

    Ollama shares this helper but can only ever take the string branch:
    `ollama._types.Message.content` is `Optional[str]` (`ollama/_types.py:312`),
    so a parts array could not reach the daemon through the typed client.
    """

    if content is None or isinstance(content, str):
        return append_rendered_memory_packet(content, rendered)
    if isinstance(content, Sequence) and not isinstance(content, str | bytes):
        parts = list(cast(Sequence[Any], content))
        return [*parts, {"type": "text", "text": rendered.content}]
    return append_rendered_memory_packet(json.dumps(content, sort_keys=True, default=str), rendered)


async def _dispatch_ollama(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    memory_packet: RenderedMemoryPromptPacket | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """Ollama provider branch — ``client.chat(...)``.

    Ollama's ``ChatResponse`` exposes ``prompt_eval_count`` / ``eval_count``
    instead of a nested ``usage`` object; no ``response_id``.

    ``memory_packet`` (B-83) folds a rendered C-MEM-12 packet into the single
    effective system source AFTER the normal translate, so it can never collide
    with a payload-carried system message. `None` — every caller but the
    tools-unsupported fallback — is byte-identical to pre-B-83.
    """
    kwargs = _payload_to_ollama_kwargs(payload, system, upstream)
    if memory_packet is not None:
        _fold_memory_packet_into_system(kwargs, memory_packet)
    response = await adapter.client.chat(model=model, **kwargs)
    return _ollama_response_bundle(response)


async def _dispatch_ollama_with_standard_memory_tools(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    memory_context: RuntimeMemoryContext,
    standard_memory_tool_executor: Any,
    step_context: StepExecutionContext,
    step_id: str,
    degraded_sink: _DegradedMemoryServeSink,
    unserved_sink: _UnservedMemoryToolCallsSink,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    max_iterations: int = 16,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """Ollama provider branch with C-MEM-14 standard memory tool continuation.

    B-82 — `select_memory_access_mode` selects `STANDARD_MEMORY_TOOLS` for
    ollama, so the bare branch silently degraded the selected mode to zero
    memory access. Unlike the OpenAI arm there is NO wire-name encoding here:
    ollama's ``/api/chat`` accepts the dotted C-MEM-14 provider-neutral
    identities (``memory.search`` ...) verbatim and echoes them back in
    ``message.tool_calls[].function.name``.

    ``degraded_sink`` receives the B-83 degraded-serve report — written ONLY on
    the tools-unsupported fallback below, and written BEFORE the retry it
    describes, so the report survives a retry that raises ([P2-d]). The caller
    owns the telemetry emission so every B-83 reachability reports through one
    emitter.

    ``unserved_sink`` receives the B-85 report when a MIXED batch is handed
    back whole — a strictly later point in the loop than the R5 fallback above
    it, which returns at ``iteration == 0`` before any ``tool_calls`` exist, so
    the two sinks can never both be written on one dispatch.
    """
    kwargs = _payload_to_ollama_kwargs(payload, system, upstream)
    kwargs["tools"] = _ollama_tools_with_standard_memory(kwargs.get("tools"), memory_context)
    messages = list(kwargs["messages"])
    kwargs["messages"] = messages

    usage = _NO_USAGE
    for iteration in range(max_iterations):
        try:
            response = await adapter.client.chat(model=model, **kwargs)
        except Exception as exc:
            if iteration != 0 or not _is_ollama_tools_unsupported_error(exc):
                raise
            # This model carries no tool template, so the memory tools we
            # auto-injected turned a previously-working TEXT dispatch into a
            # 400. The daemon, not a capability table, is the authority on
            # which models take tools — so the retry drops the tools.
            #
            # BEHAVIOR CHANGE at B-83 (deliberate; this fallback previously
            # BYTE-RESTORED the pre-B-82 bare dispatch): re-dispatching bare
            # left the model with ZERO memory on a plain default-reflection
            # path, with no trace of the degradation — B-83's shape on the
            # commonest configuration. The retry now carries the C-MEM-12
            # packet as read-only prompt text (C-MEM-13,
            # `Spec_Memory_Substrate_v1.md:460`) and reports the repair back
            # for telemetry. The TOOLS are still dropped, so the daemon
            # rejection is still resolved; only the prompt differs from
            # pre-B-82.
            #
            # FIRST call only: a mid-loop rejection would mean the model changed
            # identity between continuation turns, which is not a case to paper
            # over, so it stays fail-loud.
            # The SAME repair-vs-report authority the arm-selection
            # serve-check uses. Provider IDENTITY always matches here (this
            # function is only reached through `_standard_memory_tools_context`)
            # but the FAMILY conjunct is live: on the `memory_runtime` path a
            # cross-family fallback recomposes for the current candidate while
            # the packet keeps the chain PRIMARY's family scope (B-83 [P1-c]),
            # so a primary-family packet must NOT be rendered here.
            # "ollama" is this arm's provider key by construction — the same
            # literal `_ollama_prepared_memory_tool_calls` already passes.
            degraded = _degraded_serve_disposition("ollama", memory_context)
            # PUBLISH BEFORE the retry ([P2-d]). By this point the disposition
            # is settled — a repair authorizes disclosure, a report-only
            # withholds — and the retry itself can raise. Publishing first means
            # the caller's `finally` reports what was decided either way.
            degraded_sink.value = degraded
            # `system=system` reproduces the pre-B-83 retry EXACTLY (including
            # its pre-existing conflict semantics); the packet — when the
            # disposition allows one at all — is then folded into whichever
            # single system source that produced, so the retry never carries two.
            bare_response, bare_usage = await _dispatch_ollama(
                adapter,
                model,
                payload,
                system=system,
                upstream=upstream,
                memory_packet=degraded.rendered,
            )
            return (bare_response, bare_usage)
        # See the OpenAI arm — every turn's usage is folded in before exit.
        usage = _accumulated_usage(usage, _ollama_usage_attrs(response))
        response_mapping = _response_to_mapping(response)
        tool_calls = _ollama_tool_calls(response_mapping)
        if not tool_calls:
            return (response_mapping, usage)
        if not _all_calls_are_memory_tools(
            [_function_tool_name(call) for call in tool_calls],
            _MEMORY_TOOL_NAMES,
        ):
            # Caller-owned batch — see the OpenAI arm's matching comment.
            # B-85 posture (3): the memory call inside a MIXED batch goes
            # unserved and un-ledgered here; still unrepairable at this site
            # (the response is handed back whole for batch atomicity), so the
            # return is byte-identical and the fact is REPORTED instead.
            _record_unserved_memory_tool_calls(
                unserved_sink,
                [_function_tool_name(call) for call in tool_calls],
                _MEMORY_TOOL_NAMES,
            )
            return (response_mapping, usage)
        # Validate first, then check the bound, then execute — see the OpenAI
        # arm's matching comments; the ordering rationale is identical.
        prepared = _ollama_prepared_memory_tool_calls(
            tool_calls,
            memory_context=memory_context,
            step_context=step_context,
            step_id=step_id,
            model=model,
        )
        if iteration + 1 >= max_iterations:
            raise _memory_tool_loop_exhausted("Ollama", max_iterations)

        messages.append(dict(_ollama_message(response_mapping)))
        messages.extend(
            _ollama_memory_tool_result_messages(
                prepared,
                standard_memory_tool_executor=standard_memory_tool_executor,
            )
        )

    raise _memory_tool_loop_exhausted("Ollama", max_iterations)


#: Substring of the ollama daemon's rejection when a model has no tool template.
_OLLAMA_TOOLS_UNSUPPORTED_MARKER: Final[str] = "does not support tools"


def _is_ollama_tools_unsupported_error(exc: BaseException) -> bool:
    """True for the daemon's ``<model> does not support tools`` rejection.

    **Brittleness tradeoff, deliberate.** This matches a SUBSTRING of an upstream
    error string because the daemon offers no machine-readable discriminator:
    ``ollama.ResponseError`` carries only ``.error`` (str) and ``.status_code``
    (`ollama/_types.py:632-651`), and the same type is raised for unrelated
    failures. Probed live against ollama 0.6.2 + a local daemon:

    - tools unsupported -> ``.error = 'registry.ollama.ai/library/llava-llama3:
      latest does not support tools'``, ``.status_code = 400``
    - model not found   -> ``.error = "model 'x' not found"``, ``.status_code = 404``

    If upstream rewords the message this predicate simply stops matching and the
    error propagates — it fails CLOSED (a loud dispatch failure), never silently
    swallowing a different fault. The robust alternative, a per-model capability
    table, is a design question this arc deliberately does not open:
    `reflect_provider_capabilities` reports ``supports_tools=True`` for every
    ollama model string (`harness-cp/src/harness_cp/provider_capabilities.py:127`),
    which is the pre-existing gap this narrow fallback works around.

    Duck-typed on the class NAME rather than importing `ollama`, so this module
    stays free of provider-SDK imports like every other dispatch branch. Paired
    with the ``.error`` substring, a false positive is not reachable in practice.
    """
    if type(exc).__name__ != "ResponseError":
        return False
    error = getattr(exc, "error", None)
    return isinstance(error, str) and _OLLAMA_TOOLS_UNSUPPORTED_MARKER in error


def _ollama_usage_attrs(response: Any) -> _UsageAttrs:
    return _UsageAttrs(
        input_tokens=getattr(response, "prompt_eval_count", None),
        output_tokens=getattr(response, "eval_count", None),
        response_id=None,
    )


def _ollama_response_bundle(response: Any) -> tuple[Mapping[str, Any], _UsageAttrs]:
    return (_response_to_mapping(response), _ollama_usage_attrs(response))


def _ollama_message(response: Mapping[str, Any]) -> Mapping[str, Any]:
    """Read the assistant turn off an ollama ``ChatResponse`` dump.

    Ollama has NO ``choices[]`` envelope — ``ChatResponse.message`` is
    top-level (`ollama/_types.py:418`).
    """
    message = response.get("message")
    if not isinstance(message, Mapping):
        raise LLMDispatchPayloadShapeError("Ollama response message missing")
    return cast(Mapping[str, Any], message)


def _ollama_tool_calls(response: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    message = _ollama_message(response)
    tool_calls = message.get("tool_calls")
    if tool_calls is None:
        return ()
    if isinstance(tool_calls, str | bytes) or not isinstance(tool_calls, Sequence):
        raise LLMDispatchPayloadShapeError("Ollama tool_calls must be a sequence")
    calls: list[Mapping[str, Any]] = []
    for item in cast(Sequence[object], tool_calls):
        if not isinstance(item, Mapping):
            raise LLMDispatchPayloadShapeError("Ollama tool_call entries must be mappings")
        calls.append(cast(Mapping[str, Any], item))
    return tuple(calls)


def _ollama_prepared_memory_tool_calls(
    calls: Sequence[Mapping[str, Any]],
    *,
    memory_context: RuntimeMemoryContext,
    step_context: StepExecutionContext,
    step_id: str,
    model: str,
) -> tuple[_PreparedMemoryToolCall, ...]:
    """Resolve + validate the COMPLETE batch before any of it executes.

    Mirrors `_openai_prepared_memory_tool_calls` exactly, minus the tool-call-id
    check ollama has no field for. See `_PreparedMemoryToolCall`.
    """
    prepared: list[_PreparedMemoryToolCall] = []
    for call in calls:
        tool_name, arguments = _ollama_memory_tool_name_and_arguments(call)
        prepared.append(
            _PreparedMemoryToolCall(
                tool_name=tool_name,
                request=MemoryToolExecutionRequest(
                    tool_name=tool_name,
                    arguments=arguments,
                    context=_standard_memory_tool_context(
                        arguments,
                        tool_name=tool_name,
                        memory_context=memory_context,
                        step_context=step_context,
                        step_id=step_id,
                        provider="ollama",
                        model=model,
                    ),
                ),
            )
        )
    return tuple(prepared)


def _ollama_memory_tool_result_messages(
    prepared: Sequence[_PreparedMemoryToolCall],
    *,
    standard_memory_tool_executor: Any,
) -> list[dict[str, Any]]:
    """Execute an ALREADY-VALIDATED batch in order and build its result turns.

    Ollama's `Message` carries NO `tool_call_id` — the typed client drops the
    daemon's tool-call id entirely, so no correlation id is reachable. The
    tool-result turn correlates by NAME via `Message.tool_name`
    (`ollama/_types.py:330`); an extra `tool_call_id` key would be silently
    dropped by the pydantic model, so it is deliberately not emitted.
    """
    messages: list[dict[str, Any]] = []
    for call in prepared:
        result = standard_memory_tool_executor.execute(call.request)
        messages.append(
            {
                "role": "tool",
                "tool_name": call.tool_name.value,
                "content": json.dumps(result, sort_keys=True, separators=(",", ":"), default=str),
            }
        )
    return messages


def _ollama_memory_tool_name_and_arguments(
    call: Mapping[str, Any],
) -> tuple[MemoryToolName, dict[str, object]]:
    function = call.get("function")
    if not isinstance(function, Mapping):
        raise LLMDispatchPayloadShapeError("Ollama memory tool_call.function missing")
    function_mapping = cast(Mapping[str, object], function)
    name = function_mapping.get("name")
    if not isinstance(name, str) or not name:
        raise LLMDispatchPayloadShapeError("Ollama memory tool_call.function.name missing")
    try:
        tool_name = MemoryToolName(name)
    except ValueError as exc:
        raise LLMDispatchPayloadShapeError(
            f"Ollama standard memory loop received non-memory tool {name!r}"
        ) from exc
    raw_arguments = function_mapping.get("arguments")
    # `Message.ToolCall.Function.arguments` is typed `Mapping[str, Any]`
    # (`ollama/_types.py:346`) — already decoded, so the happy path does NOT
    # json.loads. A JSON string is still accepted defensively for client
    # versions / hand-rolled stubs that hand back the OpenAI-shaped encoding.
    if isinstance(raw_arguments, Mapping):
        return (tool_name, dict(cast(Mapping[str, object], raw_arguments)))
    if isinstance(raw_arguments, str):
        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError as exc:
            raise LLMDispatchPayloadShapeError(
                f"Ollama memory tool {name!r} arguments are not valid JSON"
            ) from exc
        if not isinstance(parsed, Mapping):
            raise LLMDispatchPayloadShapeError(
                f"Ollama memory tool {name!r} arguments must decode to an object"
            )
        return (tool_name, dict(cast(Mapping[str, object], parsed)))
    raise LLMDispatchPayloadShapeError(f"Ollama memory tool {name!r} arguments missing")


def _ollama_tools_with_standard_memory(
    existing_tools: object,
    memory_context: RuntimeMemoryContext,
) -> list[dict[str, Any]]:
    # Drop a caller-supplied tool that names one of the injected memory tools.
    # The collision set is the DOTTED provider-neutral identities only — unlike
    # OpenAI, ollama needs no second wire spelling, so there is no second name
    # to collide on.
    memory_tool_names = {entry.tool.value for entry in MEMORY_TOOL_CONTRACTS}
    preserved: list[dict[str, Any]] = []
    if isinstance(existing_tools, Sequence) and not isinstance(existing_tools, str | bytes):
        for tool in cast(Sequence[object], existing_tools):
            if not isinstance(tool, Mapping):
                continue
            tool_mapping = dict(cast(Mapping[str, Any], tool))
            if _function_tool_name(tool_mapping) in memory_tool_names:
                continue
            preserved.append(tool_mapping)
    return [*preserved, *_ollama_standard_memory_tools(memory_context)]


def _ollama_standard_memory_tools(memory_context: RuntimeMemoryContext) -> list[dict[str, Any]]:
    if memory_context.scope_ref is None:
        raise MemoryToolExecutionInputError(
            "standard memory tool schema injection requires RuntimeMemoryContext.scope_ref"
        )
    tools: list[dict[str, Any]] = []
    for entry in MEMORY_TOOL_CONTRACTS:
        # deepcopy BEFORE mutating — `entry.contract.input_schema` is the shared
        # module-level contract object; binding the fixed values in place would
        # leak this dispatch's scope_ref/policy_ref into every concurrent one.
        parameters: dict[str, object] = deepcopy(entry.contract.input_schema)
        properties = parameters.get("properties")
        if not isinstance(properties, dict):
            raise MemoryToolExecutionInputError("memory tool input schema properties missing")
        schema_properties = cast("dict[str, object]", properties)
        _bind_schema_fixed_value(schema_properties, "scope_ref", memory_context.scope_ref)
        _bind_schema_fixed_value(schema_properties, "policy_ref", memory_context.policy_ref)
        tools.append(
            {
                "type": "function",
                "function": {
                    # DOTTED provider-neutral identity — no wire-name map on this
                    # path (see `_dispatch_ollama_with_standard_memory_tools`).
                    "name": entry.tool.value,
                    "description": entry.contract.description,
                    "parameters": parameters,
                },
            }
        )
    return tools


async def _dispatch_external_cli(
    adapter: _ExternalCLIProviderLike,
    provider: str,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    system: str | None = None,
    upstream: Mapping[str, Any] | None = None,
    memory_packet: RenderedMemoryPromptPacket | None = None,
) -> tuple[Mapping[str, Any], _UsageAttrs, _ExternalCLIAttrs]:
    """External CLI provider branch — one text prompt, one text response.

    ``memory_packet`` (B-83 [P1-d]) is the degraded-serve repair packet, folded
    into the SINGLE effective system source by the translator. ``None`` — every
    caller but a repaired dispatch — is byte-identical to pre-B-83.
    """
    prompt = _payload_to_external_cli_prompt(
        payload,
        provider=provider,
        system=system,
        upstream=upstream,
        memory_packet=memory_packet,
    )
    result = await adapter.dispatch_text(model=model, prompt=prompt)
    text = getattr(result, "text", None)
    if not isinstance(text, str):
        raise LLMDispatchPayloadShapeError("external CLI provider result missing string text field")
    exit_code = getattr(result, "exit_code", 0)
    if not isinstance(exit_code, int):
        exit_code = 0
    kind = getattr(adapter, "kind", "external-cli")
    if not isinstance(kind, str):
        kind = "external-cli"
    response: Mapping[str, Any] = {
        "provider": provider,
        "model": model,
        "content": [{"type": "text", "text": text}],
    }
    return (
        response,
        _UsageAttrs(input_tokens=None, output_tokens=None, response_id=None),
        _ExternalCLIAttrs(exit_code=exit_code, kind=kind),
    )


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


async def _attribute_cost_off_loop_best_effort(**kwargs: Any) -> None:
    """Best-effort boundary AROUND the offload (codex round-17 P1): queue
    saturation raises at submit — BEFORE fn runs — so the fn-internal
    swallows never see it and an otherwise-successful dispatch failed.
    Contained here: logged loudly, dispatch preserved."""
    try:
        await run_audit_off_loop(_attribute_cost_best_effort, **kwargs)
    except AUDIT_SIGNING_HARD_FAILURES:
        logging.getLogger("harness.runtime.audit_signing").error(
            "audit offload refused the job — signed cost-audit record "
            "OMITTED for llm_dispatch (offload boundary)",
            exc_info=True,
        )
        # U-RT-136 (OD v1.34 §21.2.3 rows 1/5): under fail-closed the typed
        # family RAISES; the loudly-surfaced proceed above is the OFF arm.
        if kwargs.get("audit_signing_fail_closed"):
            raise


def _attribute_cost_best_effort(
    *,
    span: Any,
    cost_chain: Any,
    audit_writer: Any,
    rate_table: Any,
    cost_record_sink: SupportsCostRecordAppend | None = None,
    ledger_writer: Any = None,
    procedural_tier_snapshot_resolver: Any = None,
    signing_backend: Any = None,
    audit_signing_fail_closed: bool = False,
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
    run_engine_class: EngineClass | None = None,
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
    from harness_runtime.lifecycle.cross_family_cost_tag import (
        cross_family_tag_for_provider,
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
            ledger_writer=ledger_writer,
            procedural_tier_snapshot_resolver=procedural_tier_snapshot_resolver,
            signing_backend=signing_backend,
            # R-FS-1 B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION — populate the
            # §15.3 cross-family family tag from the dispatched provider so the
            # PER_PROVIDER_DISCRIMINATOR rollup is non-vacuous in production.
            # An LLM dispatch always has a provider ⟹ always a family tag.
            provider_discriminator=cross_family_tag_for_provider(provider_name),
            run_engine_class=run_engine_class,
        )
    except AUDIT_SIGNING_HARD_FAILURES:
        # Codex round-4 P1 (PR B2a): a CONFIGURED signing backend's failure
        # must never be silently swallowed with ordinary cost-observability
        # failures — the signed audit record is a compliance artifact.
        # Surfaced loudly; dispatch preserved under flag OFF. U-RT-136
        # (OD v1.34 §21.2.3 rows 1/5): under fail-closed the typed family
        # RAISES instead (the B-47-registered policy question, now decided).
        logging.getLogger("harness.runtime.audit_signing").error(
            "audit signing failed — signed cost-audit record OMITTED for llm_dispatch",
            exc_info=True,
        )
        if audit_signing_fail_closed:
            raise
        return
    except Exception:
        # Cost-attribution is observability, not contract. Swallow.
        return

    # Emit cost.attributed_decimal OTel attribute via U-OD-49 string-form
    # preserving the float→Decimal serialization at the OTel boundary.
    span.set_attribute(
        COST_ATTRIBUTED_DECIMAL_ATTR,
        serialize_decimal_for_otel(Decimal(str(attached.total_cost))),
    )

    # R-FS-1 arc CA — record the per-dispatch SpanCostRecord into the run-scoped
    # accumulator so `_build_run_result` can roll up `RunResult.cost_attribution`
    # (runtime spec v1.53 §9 C-RT-09). `list.append` is atomic under the GIL.
    if cost_record_sink is not None:
        cost_record_sink.append(attached)


def materialize_llm_dispatcher_stage(
    providers: _ProvidersLike,
    tracer_provider: _TracerProviderLike,
    *,
    cost_chain: Any = None,
    audit_writer: Any = None,
    rate_table: Any = None,
    cost_record_sink: SupportsCostRecordAppend | None = None,
    ledger_writer: Any = None,
    procedural_tier_snapshot_resolver: Any = None,
    signing_backend: Any = None,
    inter_step_channel: Any = None,
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
    frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None,
    child_frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None,
    cache_ttl: CacheTTL = DEFAULT_CACHE_TTL,
    memory_context: RuntimeMemoryContext | None = None,
    standard_memory_tool_executor: Any = None,
    memory_runtime: Any = None,
    fallback_chain: Any = None,
    per_role_system_prompts: Mapping[AgentRole, str] | None = None,
    prompt_versions_by_sha: Mapping[str, str] | None = None,
    approved_prompt_version_shas: frozenset[str] = frozenset(),
    routing_activation: bool = False,
    embedding_classifier: LayerDecisionFn | None = None,
    prewarm_model: str | None = None,
    prewarm_policy_fail_closed: bool = False,
    audit_signing_fail_closed: bool = False,
    protected_result_store: Any = None,
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

    # B-L2-FALLBACK-COMPOSITION (runtime §14.6) — routing_activation NOW composes
    # with the C-RT-16 fallback chain: the routing decision is made ONCE at the
    # C-RT-16 wrapper (via `RuntimeLLMDispatcher.resolve_routed_binding`, which the
    # stage-5 factory hands the wrapper as a direct handle) and SEEDS the routed
    # model as the wrapper's PRIMARY fallback candidate; the inner `dispatch` stays
    # FAITHFUL. The prior B-L2-EMBEDDING-ACTIVATION detect-then-refuse guard
    # (routing_activation + non-empty fallback_chains → LLMDispatchBindError) is
    # RETIRED — the silent-fallback-defeat it prevented is now architecturally
    # closed (the U-RT-114 §14.5.3 "wrapper owns model-candidate selection",
    # route-once-then-fallback-the-chain pattern applied to layered routing).

    # B-L2-EMBEDDING-ACTIVATION (C-CP-02 §2.2): when routing_activation is on and no
    # classifier is injected, build the default L2 EMBEDDING classifier (the light
    # in-process fastembed realization over the default per-workload corpus) so the
    # §2.2-conditional DECLARATIVE decline has a real fall-through target. Local
    # imports keep the module-load light + touch fastembed ONLY when flag-on;
    # `make_fastembed_embedding` fail-louds with the install hint when the optional
    # `[embedding]` extra is absent (the dep stays optional — promoting it to a
    # required dependency is the deferred deployment step). Default-off ⇒ this block
    # is skipped, fastembed is never imported, byte-identical.
    if routing_activation and embedding_classifier is None:
        from harness_cp.embedding_routing import make_embedding_classifier

        from harness_runtime.lifecycle.embedding_resolution import (
            default_routing_corpus,
            make_fastembed_embedding,
        )

        embedding_classifier = make_embedding_classifier(
            embed=make_fastembed_embedding(),
            corpus=default_routing_corpus(),
        )

    return RuntimeLLMDispatcher(
        providers=providers,
        tracer_provider=tracer_provider,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        rate_table=rate_table,
        cost_record_sink=cost_record_sink,
        ledger_writer=ledger_writer,
        procedural_tier_snapshot_resolver=procedural_tier_snapshot_resolver,
        signing_backend=signing_backend,
        inter_step_channel=inter_step_channel,
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
        frozen_tool_superset=frozen_tool_superset,
        child_frozen_tool_superset=child_frozen_tool_superset,
        cache_ttl=cache_ttl,
        memory_context=memory_context,
        standard_memory_tool_executor=standard_memory_tool_executor,
        memory_runtime=memory_runtime,
        fallback_chain=fallback_chain,
        per_role_system_prompts=per_role_system_prompts or {},
        prompt_versions_by_sha=prompt_versions_by_sha or {},
        approved_prompt_version_shas=approved_prompt_version_shas,
        routing_activation=routing_activation,
        embedding_classifier=embedding_classifier,
        prewarm_model=prewarm_model,
        # U-RT-135 — the MTC fail-closed prewarm disable (stage 5 passes
        # `mtc_audit_prewarm_disabled(config)`).
        prewarm_policy_fail_closed=prewarm_policy_fail_closed,
        # U-RT-136 — the resolved OD v1.34 §21.2.3 policy (stage 5 passes
        # `resolve_audit_signing_fail_closed(config)`).
        audit_signing_fail_closed=audit_signing_fail_closed,
        # B-65-A — `ctx.protected_result_store` (stage 4 OD).
        protected_result_store=protected_result_store,
    )


__all__ = [
    "LLMDispatchBindError",
    "LLMDispatchPayloadShapeError",
    "LLMDispatchProviderUnreachableError",
    "PrewarmOutcome",
    "PromptInjectionConflictError",
    "RuntimeLLMDispatcher",
    "materialize_llm_dispatcher_stage",
]

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

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, cast, runtime_checkable

from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep

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
            f"RT-FAIL-PROVIDER-UNREACHABLE: provider "
            f"{provider_name!r} not in ctx.providers"
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
        may bind parent context to ``llm.inference`` span attributes per
        future C-RT-NN amendments.

        Per C-RT-15 §Specification content steps 1-5. Provider-specific
        dispatch branches are exhaustive over the three providers
        constructed at C-RT-05 stage 3a (anthropic / openai / ollama).

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
        # --- Step 1: provider resolution --------------------------------
        provider_name = binding.model_binding.provider
        if provider_name not in self.providers:
            raise LLMDispatchProviderUnreachableError(provider_name)

        adapter = self.providers[provider_name]
        payload = _coerce_payload(step.step_payload)
        model = binding.model_binding.model

        # --- Step 2: open GenAI-semconv span ----------------------------
        # Span name per OTel GenAI semconv guidance:
        # `gen_ai.{system}.{operation}`.
        tracer = self.tracer_provider.get_tracer("harness.runtime.llm_dispatch")
        operation = _PROVIDER_OPERATIONS.get(provider_name)
        if operation is None:
            # Defensive — every key in self.providers is one of the
            # three constructed at stage 3a per C-RT-05. Surfacing any
            # other key as UNREACHABLE preserves the C-RT-14 taxonomy.
            raise LLMDispatchProviderUnreachableError(provider_name)
        span_name = f"gen_ai.{provider_name}.{operation}"

        # OTel tracer CM is synchronous (returns ``ContextManager``, not
        # ``AsyncContextManager``); spec §14.5 phrasing is imprecise.
        with tracer.start_as_current_span(span_name) as span:
            # Required GenAI semconv 1.41.0 attributes (request side).
            span.set_attribute("gen_ai.system", provider_name)
            span.set_attribute("gen_ai.request.model", model)

            # --- Step 3: per-provider dispatch --------------------------
            cache_attrs: _AnthropicCacheAttrs | None
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
                    response, usage_attrs, cache_attrs = await _dispatch_anthropic_with_memory(
                        adapter,
                        model,
                        payload,
                        registry=self.memory_tool_registry,
                        deployment_surface=self.deployment_surface,
                        tracer=tracer,
                    )
                else:
                    response, usage_attrs, cache_attrs = await _dispatch_anthropic(
                        adapter, model, payload
                    )
            elif provider_name == "openai":
                response, usage_attrs = await _dispatch_openai(
                    adapter, model, payload
                )
                cache_attrs = None
            else:  # provider_name == "ollama" (only remaining branch)
                response, usage_attrs = await _dispatch_ollama(
                    adapter, model, payload
                )
                cache_attrs = None

            # --- Step 4: populate response-side attributes --------------
            _set_if_present(
                span, "gen_ai.usage.input_tokens", usage_attrs.input_tokens
            )
            _set_if_present(
                span, "gen_ai.usage.output_tokens", usage_attrs.output_tokens
            )
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
                    cache_attrs.cache_creation_input_tokens
                    if cache_attrs is not None
                    else None
                ),
                cache_read=(
                    cache_attrs.cache_read_input_tokens
                    if cache_attrs is not None
                    else None
                ),
                tenant_id=step_context.tenant_id,
            )

            # --- Step 5: return step output mapping ---------------------
            return response


# ---------------------------------------------------------------------------
# Per-provider dispatch helpers.
# ---------------------------------------------------------------------------


_PROVIDER_OPERATIONS: dict[str, str] = {
    "anthropic": "messages.create",
    "openai": "chat.completions",
    "ollama": "chat",
}


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


def _payload_to_anthropic_kwargs(payload: ProviderAgnosticPayload) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``messages.create`` kwargs.

    Anthropic's ``messages.create`` requires ``max_tokens``; the
    provider-neutral payload carries it in ``params``. Tools are passed
    through when present; ``params`` keys merge into the call kwargs.
    """
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    return kwargs


def _payload_to_openai_kwargs(payload: ProviderAgnosticPayload) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``chat.completions.create`` kwargs."""
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    return kwargs


def _payload_to_ollama_kwargs(payload: ProviderAgnosticPayload) -> dict[str, Any]:
    """Translate `ProviderAgnosticPayload` → ``ollama.chat`` kwargs."""
    kwargs: dict[str, Any] = {"messages": list(payload.messages)}
    if payload.tools is not None:
        kwargs["tools"] = list(payload.tools)
    kwargs.update(payload.params)
    return kwargs


async def _dispatch_anthropic_with_memory(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
    *,
    registry: Any,
    deployment_surface: Any,
    tracer: Any,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs]:
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
    kwargs = _payload_to_anthropic_kwargs(payload)

    response = await execute_with_memory_callbacks(
        adapter=adapter,
        model=model,
        messages_create_kwargs=kwargs,
        backend=backend,
        backend_enum=configured_backend,
        tracer=tracer,
        context_editing_active=context_editing_active,
    )

    usage = getattr(response, "usage", None)
    usage_attrs = _UsageAttrs(
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
        response_id=getattr(response, "id", None),
    )
    cache_breakpoint_id, cache_ttl_seconds = (
        _extract_anthropic_cache_request_attrs(payload)
    )
    cache_attrs = _AnthropicCacheAttrs(
        cache_creation_input_tokens=getattr(
            usage, "cache_creation_input_tokens", None
        ),
        cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", None),
        cache_breakpoint_id=cache_breakpoint_id,
        cache_ttl_seconds=cache_ttl_seconds,
    )
    return (_response_to_mapping(response), usage_attrs, cache_attrs)


async def _dispatch_anthropic(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
) -> tuple[Mapping[str, Any], _UsageAttrs, _AnthropicCacheAttrs]:
    """Anthropic provider branch — ``client.messages.create(...)``."""
    kwargs = _payload_to_anthropic_kwargs(payload)
    response = await adapter.client.messages.create(model=model, **kwargs)

    usage = getattr(response, "usage", None)
    usage_attrs = _UsageAttrs(
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
        response_id=getattr(response, "id", None),
    )
    cache_breakpoint_id, cache_ttl_seconds = (
        _extract_anthropic_cache_request_attrs(payload)
    )
    cache_attrs = _AnthropicCacheAttrs(
        cache_creation_input_tokens=getattr(
            usage, "cache_creation_input_tokens", None
        ),
        cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", None),
        cache_breakpoint_id=cache_breakpoint_id,
        cache_ttl_seconds=cache_ttl_seconds,
    )

    return (_response_to_mapping(response), usage_attrs, cache_attrs)


async def _dispatch_openai(
    adapter: Any,
    model: str,
    payload: ProviderAgnosticPayload,
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """OpenAI provider branch — ``client.chat.completions.create(...)``."""
    kwargs = _payload_to_openai_kwargs(payload)
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
) -> tuple[Mapping[str, Any], _UsageAttrs]:
    """Ollama provider branch — ``client.chat(...)``.

    Ollama's ``ChatResponse`` exposes ``prompt_eval_count`` / ``eval_count``
    instead of a nested ``usage`` object; no ``response_id``.
    """
    kwargs = _payload_to_ollama_kwargs(payload)
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
            "No providers registered at stage 3a — cannot bind "
            "LLM dispatcher at stage 5"
        )

    return RuntimeLLMDispatcher(
        providers=providers,
        tracer_provider=tracer_provider,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        rate_table=rate_table,
        memory_tool_registry=memory_tool_registry,
        deployment_surface=deployment_surface,
    )


__all__ = [
    "LLMDispatchBindError",
    "LLMDispatchPayloadShapeError",
    "LLMDispatchProviderUnreachableError",
    "RuntimeLLMDispatcher",
    "materialize_llm_dispatcher_stage",
]

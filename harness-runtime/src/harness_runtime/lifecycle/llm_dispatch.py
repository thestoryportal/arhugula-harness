"""LLM-dispatch composer — stage 5 LOOP_INIT (U-RT-52, opens L9).

Per `Spec_Harness_Runtime_v1.md` v1.2 §C-RT-15 (LLM-dispatch composer).
Satisfies the `harness_cp.workflow_driver.StepDispatcher` Protocol
(declared at `harness_cp/src/harness_cp/workflow_driver.py:151`,
`runtime_checkable`). Per-step async composer that:

  1. Resolves `ProviderClient` from `ctx.provider_capabilities` via
     `binding.provider_name`.
  2. Starts a GenAI-semconv 1.41.0 span via
     `ctx.tracer_provider.get_tracer("harness.runtime.llm_dispatch")`.
  3. Dispatches to the provider's underlying SDK method per the
     capability-aware abstraction at CP C-CP-01 §1.
  4. Populates GenAI semconv attributes per OD C-OD-04..08 + (for the
     anthropic provider) `anthropic.cache_*` attributes per AS
     C-AS-14 §14.2.
  5. Returns `Mapping[str, Any]` per `StepDispatcher` Protocol contract.

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

**Module convention.** One module per unit. Bound at bootstrap stage 5
alongside override evaluator / topology dispatcher / lifecycle emitter.
Typed `LLMDispatchBindError` for bootstrap-time failures. Mirrors the
L5..L8 stage shape established at U-RT-21..U-RT-41.

**SKELETON STATUS (U-RT-52 partial-land).** This module is the typed
surface only — per-provider dispatch branches raise
`NotImplementedError` pending follow-on landing (estimated 4-6 hours
focused work: provider SDK invocations + GenAI span attribute
emission + per-provider mock tests + bootstrap stage 5 wiring +
retirement-event filing for batch 2). Acceptance criteria #2-#7 per
plan §atomic-units U-RT-52 require the dispatch + telemetry + tests
to land before U-RT-52 closes. AC #1 (Protocol satisfaction) +
AC #8 retirement-event prerequisite framing land at this skeleton.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import WorkflowStep


class LLMDispatchBindError(Exception):
    """Raised when LLM-dispatch composer stage materialization fails."""


class LLMDispatchProviderUnreachableError(Exception):
    """Raised when `binding.provider_name` resolves to a provider absent
    from `ctx.providers` (e.g., Ollama-degraded path skipped registration).

    Maps to `RT-FAIL-PROVIDER-UNREACHABLE` per `Spec_Harness_Runtime_v1.md`
    v1.2 §C-RT-14 failure-mode taxonomy. Carries the offending
    provider name for operator-facing attribution.
    """

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name
        super().__init__(
            f"RT-FAIL-PROVIDER-UNREACHABLE: provider "
            f"{provider_name!r} not in ctx.providers"
        )


@runtime_checkable
class _ProvidersLike(Protocol):
    """Minimal `ctx.providers` substrate the composer consumes.

    Structurally satisfied by `harness_runtime.lifecycle.providers.
    ProviderClientsStage.providers` (a `dict[str, ProviderClient]`
    mapping per C-RT-05). The Protocol decoupling avoids a
    forward-import cycle with the providers stage module.
    """

    def __contains__(self, key: object) -> bool: ...
    def __getitem__(self, key: str) -> Any: ...
    def __len__(self) -> int: ...


@runtime_checkable
class _TracerProviderLike(Protocol):
    """Minimal `ctx.tracer_provider` substrate the composer consumes.

    Structurally satisfied by `opentelemetry.sdk.trace.TracerProvider`
    materialized at C-RT-06 stage 4 OD.
    """

    def get_tracer(self, instrumenting_module_name: str) -> Any: ...


@dataclass(frozen=True, slots=True)
class RuntimeLLMDispatcher:
    """Per-step LLM-dispatch composer satisfying `harness_cp.workflow_driver.
    StepDispatcher` Protocol (C-RT-15 + C-CP-25 §25.3.3.4).

    Constructed at bootstrap stage 5 (LOOP_INIT) with frozen references
    to the provider clients map + tracer-provider materialized at
    earlier stages. The composer is stateless across calls — each
    `dispatch` invocation is driven entirely by its arguments + the
    frozen provider/tracer substrate.

    Attributes
    ----------
    providers :
        Frozen reference to the `ctx.providers` map (provider_name →
        ProviderClient) materialized at stage 3a per C-RT-05.
    tracer_provider :
        Frozen reference to the `ctx.tracer_provider` materialized at
        stage 4 OD per C-RT-06.
    """

    providers: _ProvidersLike
    tracer_provider: _TracerProviderLike

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
    ) -> Mapping[str, Any]:
        """Invoke the step body under the effective binding; return step output.

        Per C-RT-15 §Specification content steps 1-5:

          1. Resolve `ProviderClient` from `self.providers` via
             `binding.provider_name`; raise
             `LLMDispatchProviderUnreachableError` if absent.
          2. Start a GenAI-semconv 1.41.0 span via the runtime's
             TracerProvider.
          3. Dispatch to the provider's underlying SDK method
             (provider-specific branch).
          4. Populate GenAI semconv attributes + `anthropic.*` if
             anthropic provider.
          5. Return step output mapping.

        **SKELETON.** Implementation deferred to U-RT-52 close (per-
        provider SDK invocations + GenAI span attribute emission +
        tests). Raises `NotImplementedError` until landing.
        """
        # Step 1 — Resolve provider per C-RT-15 §Specification step 1
        # + Invariant 4 (`RT-FAIL-PROVIDER-UNREACHABLE` on absent provider).
        # `StepEffectiveBinding` carries provider identity via
        # `binding.model_binding.provider` per CP `ModelBinding` schema
        # (C-CP-01 §1.4 routing-binding vocabulary).
        provider_name = binding.model_binding.provider
        if provider_name not in self.providers:
            raise LLMDispatchProviderUnreachableError(provider_name)

        # Steps 2-5 — Span + dispatch + attributes + return. Skeleton.
        # Implementation lands at U-RT-52 close per plan AC #2-#7.
        raise NotImplementedError(
            "RuntimeLLMDispatcher.dispatch SKELETON — U-RT-52 partial-land. "
            "Per-provider SDK dispatch + GenAI semconv span emission + "
            "anthropic.* attribute set lands at U-RT-52 close. See "
            "Spec_Harness_Runtime_v1.md v1.2 §C-RT-15 Specification content."
        )


def materialize_llm_dispatcher_stage(
    providers: _ProvidersLike,
    tracer_provider: _TracerProviderLike,
) -> RuntimeLLMDispatcher:
    """Stage 5 LOOP_INIT composer factory for the LLM dispatcher (U-RT-52).

    Constructs a frozen `RuntimeLLMDispatcher` bound to the stage-3a
    provider clients map + the stage-4 tracer provider. Bootstrap stage 5
    invokes this factory alongside `materialize_override_evaluator_stage`,
    `materialize_topology_dispatcher_stage`, and
    `materialize_lifecycle_emitter_stage` per C-RT-02 stage 5 invariants;
    result attached to `ctx.llm_dispatcher` per C-RT-15 §Integration with
    C-RT-04.

    Parameters
    ----------
    providers :
        `ctx.providers` map from `materialize_provider_clients_stage`
        (C-RT-05 stage 3a).
    tracer_provider :
        `ctx.tracer_provider` from `materialize_tracer_provider_stage`
        (C-RT-06 stage 4 OD).

    Returns
    -------
    RuntimeLLMDispatcher
        Frozen composer instance satisfying the
        `harness_cp.workflow_driver.StepDispatcher` Protocol.

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
    )


__all__ = [
    "LLMDispatchBindError",
    "LLMDispatchProviderUnreachableError",
    "RuntimeLLMDispatcher",
    "materialize_llm_dispatcher_stage",
]

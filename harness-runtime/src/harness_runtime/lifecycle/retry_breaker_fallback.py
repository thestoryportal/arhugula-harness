"""Retry / breaker / fallback composer wrapping C-RT-15 — stage 5 LOOP_INIT
(U-RT-58, opens L9-bis).

Per `Spec_Harness_Runtime_v1.md` v1.4 §14.6 C-RT-16 (retry/breaker/fallback
composer). Wraps the bare C-RT-15 ``RuntimeLLMDispatcher`` with the per-step
candidate-iteration loop + per-candidate retry loop + breaker pre-check;
satisfies the same ``harness_cp.workflow_driver.StepDispatcher`` Protocol that
the inner dispatcher satisfies — from the CP driver's perspective the wrapper
IS the dispatcher.

Per-step invocation discipline (the body of
``RetryBreakerFallbackDispatcher.dispatch(binding, step)``):

  1. Look up ``RetryPolicy`` from the registry under the reserved
     ``"llm_dispatch"`` key — operator may not declare a tool by that name
     (enforced at manifest-validation time via ``ReservedToolNameError`` at
     `harness_cp.routing_manifest_residence.validate_routing_manifest`).
  2. Iterate the fallback chain candidates: first ``chain.primary``, then
     advance via ``advance_or_raise`` on per-candidate exhaustion. Cross-
     family transitions surface the C-CP-04 §4.3 attribution flags.
  3. Per candidate: breaker pre-check via ``breaker.should_attempt()``; on
     OPEN-and-cooldown-unexpired emit a ``retry.skipped`` event on the outer
     span and advance to the next candidate.
  4. Per-attempt loop (bounded by ``RetryPolicy.max_attempts``): start an
     inner ``harness.runtime.retry_attempt`` span carrying the
     C-CP-03 §3.5 ``retry.*`` 6-attribute namespace; dispatch via
     ``self.inner.dispatch(rebound_binding, step)``. On success the breaker
     records success and the result returns; on fail-fast (provider-
     unreachable / payload-shape) the breaker records failure and the
     candidate is abandoned; on transient SDK failure the staircase advances
     and either retries (sleeps full-jitter backoff) or escalates.
  5. On ``FallbackChainExhaustedError`` emit ``fallback.exhausted`` on the
     outer span and raise ``RetryBreakerFallbackExhaustedError`` (maps to the
     ``RT-FAIL-FALLBACK-EXHAUSTED`` fail class added at v1.4).

Three nesting levels per composer invocation (canonical OTel retry-wrapper
pattern): outer ``harness.runtime.retry_breaker_fallback`` → per-attempt
``harness.runtime.retry_attempt`` → inner ``gen_ai.{provider}.{operation}``
(from C-RT-15). Head sampler picks outer; tail sampler picks per-attempt;
inner GenAI is always-sampled per OTel GenAI semconv.

**Q2=c Registry key extension.** The reserved ``"llm_dispatch"`` policy key
is injected into the registry's internal ``retry_policies`` map by
``materialize_retry_breaker_stage`` post-validation, NOT carried in the
operator-supplied ``RoutingManifest.retry_policies``. The validator rejects
operator-supplied ``"llm_dispatch"`` keys. See ``RESERVED_LLM_DISPATCH_KEY``
+ ``DEFAULT_LLM_DISPATCH_RETRY_POLICY`` below.

**OTel context-manager note.** The OTel tracer ``start_as_current_span``
context manager is synchronous; spec §14.6 phrasing matches §14.5's pattern.
Inside this async function we use plain ``with`` per OTel API contract.

**Framework-pull discipline.** Hand-rolled per CLAUDE.md §3.2 — NO tenacity /
pybreaker / circuitbreaker. Breaker state machine lives at U-RT-24
``BreakerStateMachine``; backoff via ``compute_full_jitter_delay_seconds``;
candidate iteration via ``advance_or_raise``. The composer is thin
composition over these primitives.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.validator_fail_taxonomy import ValidatorFailClass
from harness_cp.validator_fail_transient_staircase import StaircaseStage
from harness_cp.workflow_driver_types import WorkflowStep
from harness_od.harness_breaker_schema import BreakerScope

from harness_runtime.lifecycle.fallback_chain import (
    FallbackChainExhaustedError,
    advance_or_raise,
)
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchPayloadShapeError,
    LLMDispatchProviderUnreachableError,
)
from harness_runtime.lifecycle.retry_breaker import BreakerStateMachine
from harness_runtime.types import LLMDispatcher, RetryBreakerRegistry

__all__ = [
    "DEFAULT_LLM_DISPATCH_RETRY_POLICY",
    "RESERVED_LLM_DISPATCH_KEY",
    "RetryBreakerFallbackDispatcher",
    "RetryBreakerFallbackExhaustedError",
    "materialize_retry_breaker_fallback_dispatcher_stage",
]


RESERVED_LLM_DISPATCH_KEY = "llm_dispatch"
"""Reserved registry key for the LLM-dispatch retry policy (Q2=c clause).

The runtime composer reserves this key for LLM-dispatch retry policy lookup;
tools may not declare a tool named ``"llm_dispatch"`` (enforced at manifest-
validation time via a typed ``ReservedToolNameError`` at
`harness_cp.routing_manifest_residence.validate_routing_manifest`). The
default policy below is injected into the registry's internal mapping by
``materialize_retry_breaker_stage`` when no operator override is supplied
through a future-arc mechanism (per-runtime override is not exposed at MVP
per spec §14.6 "Deferred to implementation discretion")."""


DEFAULT_LLM_DISPATCH_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    backoff="full_jitter",
    jitter="full_jitter",
)
"""Default ``RetryPolicy`` for the reserved ``"llm_dispatch"`` registry key.

Per spec §14.6: ``RetryPolicy(max_attempts=3, backoff="full_jitter",
base_delay_seconds=0.2, delay_cap_seconds=10.0)``. The registry carries
``base_delay_seconds`` / ``delay_cap_seconds`` as registry-level defaults
(not per-policy fields per `RetryPolicy` schema), so those are inherited
from the ``RuntimeRetryBreaker`` instance bound at stage 3b."""


class RetryBreakerFallbackExhaustedError(Exception):
    """Raised when the fallback chain exhausts after per-candidate retry
    exhaustion (every candidate either fails-fast or hits ``max_attempts``).

    Maps to ``RT-FAIL-FALLBACK-EXHAUSTED`` per `Spec_Harness_Runtime_v1.md`
    v1.4 §C-RT-14 failure-mode taxonomy (new row at v1.4). The driver
    ``try/except`` at ``workflow_driver.py:380-389`` catches and maps to
    ``step-failure: RT-FAIL-FALLBACK-EXHAUSTED: ...`` per C-CP-25 §25.3.3.4.

    Carries the last failed candidate for operator-facing attribution.
    """

    def __init__(self, failed: ProviderCandidate) -> None:
        self.failed = failed
        super().__init__(
            f"RT-FAIL-FALLBACK-EXHAUSTED: fallback chain exhausted after "
            f"candidate {failed.provider}:{failed.model} (chain traversal complete)"
        )


def _rebind_to_candidate(
    binding: StepEffectiveBinding, candidate: ProviderCandidate
) -> StepEffectiveBinding:
    """Construct a new ``StepEffectiveBinding`` with ``model_binding`` overridden
    to the current fallback candidate. Other fields carry forward unchanged."""
    return binding.model_copy(
        update={
            "model_binding": ModelBinding(
                provider=candidate.provider, model=candidate.model
            )
        }
    )


def _classify_provider_exception(exc: BaseException) -> ValidatorFailClass | None:
    """Map a provider-side exception to a ``ValidatorFailClass`` for the
    staircase, or ``None`` for fail-fast / propagate.

    Per spec §14.6 D2: AUTH / payload-shape / shutdown are fail-fast;
    network / rate-limit / 5xx are transient (run the staircase).

    MVP discrimination (conservative — extends naturally to provider-specific
    exception classes at a follow-on arc):

    - ``LLMDispatchProviderUnreachableError`` → ``None`` (fail-fast, abandons
      this candidate; the outer loop advances).
    - ``LLMDispatchPayloadShapeError`` → ``None`` (fail-fast, abandons this
      candidate; the outer loop advances).
    - ``asyncio.CancelledError`` → re-raise (shutdown / cancellation must
      propagate; this is handled by the caller, not classified here).
    - All other ``Exception`` subclasses → ``TRANSIENT_RETRY`` (treat as
      network / rate-limit / 5xx until proven otherwise).
    """
    if isinstance(exc, (LLMDispatchProviderUnreachableError, LLMDispatchPayloadShapeError)):
        return None
    return ValidatorFailClass.TRANSIENT_RETRY


@dataclass(slots=True)
class RetryBreakerFallbackDispatcher:
    """Per-step retry / breaker / fallback composer (C-RT-16).

    Wraps the bare C-RT-15 ``RuntimeLLMDispatcher`` (or any ``LLMDispatcher``
    Protocol-satisfying inner) with the candidate-iteration + retry-loop +
    breaker-coordination orchestration. Satisfies the
    ``harness_cp.workflow_driver.StepDispatcher`` Protocol via the same
    ``runtime_checkable`` introspection that the inner dispatcher satisfies.

    Attributes
    ----------
    inner :
        The inner ``LLMDispatcher`` (typically ``RuntimeLLMDispatcher``).
        Invoked exactly once per per-attempt iteration with a rebound
        ``StepEffectiveBinding`` whose ``model_binding`` is the current
        candidate's ``(provider, model)``.
    retry_breaker :
        The U-RT-24 registry. Used for policy lookup (``get_policy``),
        per-candidate breaker access (``get_breaker``), staircase
        advancement (``advance_staircase``), and ``harness.breaker.*``
        transition emission (``emit_breaker_transition_event``).
    fallback_chain :
        The stage 3b-bound ``FallbackChain``. The composer iterates its
        candidates in the §4.2 traversal order
        (primary → same-family → cross-family → terminal).
    tracer_provider :
        The stage 4 ``TracerProvider`` for outer + inner span emission.
        Typed ``Any`` for the same C-RT-04 reason ``RuntimeLLMDispatcher``
        uses (avoids pulling the OTel SDK type into the schema at L0).
    sleep_fn :
        Awaitable sleep function for full-jitter backoff between retry
        attempts. Defaults to ``asyncio.sleep``; tests inject a recording
        no-op to keep async tests fast and deterministic.
    """

    inner: LLMDispatcher
    retry_breaker: RetryBreakerRegistry
    fallback_chain: FallbackChain
    tracer_provider: Any
    sleep_fn: Callable[[float], Awaitable[None]] = field(
        default_factory=lambda: asyncio.sleep
    )

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
    ) -> Mapping[str, Any]:
        """Invoke the step body under the effective binding with retry /
        breaker / fallback orchestration; return step output.

        Raises
        ------
        RetryBreakerFallbackExhaustedError
            The fallback chain exhausted after per-candidate retry
            exhaustion. Maps to ``RT-FAIL-FALLBACK-EXHAUSTED``.
        asyncio.CancelledError
            Re-raised verbatim (shutdown / cancellation propagates).
        """
        policy = self.retry_breaker.get_policy(RESERVED_LLM_DISPATCH_KEY)
        tracer = self.tracer_provider.get_tracer(
            "harness.runtime.retry_breaker_fallback"
        )

        with tracer.start_as_current_span(
            "harness.runtime.retry_breaker_fallback"
        ) as outer_span:
            candidate: ProviderCandidate = self.fallback_chain.primary
            last_failure_class: str | None = None
            chain_length = _chain_length(self.fallback_chain)
            outer_span.set_attribute("fallback.chain_length", chain_length)

            while True:
                # --- Step 3: breaker pre-check ----------------------------
                breaker_identifier = f"{candidate.provider}:{candidate.model}"
                breaker_obj = self.retry_breaker.get_breaker(
                    BreakerScope.PER_MODEL, breaker_identifier
                )
                # Protocol returns ``object`` to avoid a `types`↔`lifecycle`
                # import cycle; the concrete type is the L8 `BreakerStateMachine`.
                # Narrow via isinstance per the Protocol docstring's guidance.
                assert isinstance(breaker_obj, BreakerStateMachine), (
                    f"retry_breaker.get_breaker returned non-BreakerStateMachine "
                    f"object: {type(breaker_obj).__name__}"
                )
                breaker = breaker_obj
                if not breaker.should_attempt():
                    outer_span.add_event(
                        "retry.skipped",
                        attributes={
                            "retry.skipped.reason": "breaker-open",
                            "retry.skipped.candidate": breaker_identifier,
                        },
                    )
                    last_failure_class = "breaker-open"
                    candidate = self._advance_or_exhaust(
                        candidate, outer_span, last_failure_class, chain_length
                    )
                    continue

                # --- Step 4: per-attempt loop -----------------------------
                attempt_terminal = await self._run_per_candidate_attempts(
                    binding=binding,
                    step=step,
                    candidate=candidate,
                    policy=policy,
                    breaker=breaker,
                    tracer=tracer,
                    outer_span=outer_span,
                )

                if attempt_terminal.result is not None:
                    # Success.
                    return attempt_terminal.result

                # Candidate abandoned; advance to next.
                last_failure_class = attempt_terminal.last_failure_class
                candidate = self._advance_or_exhaust(
                    candidate, outer_span, last_failure_class, chain_length
                )

    def _advance_or_exhaust(
        self,
        failed: ProviderCandidate,
        outer_span: Any,
        last_failure_class: str | None,
        chain_length: int,
    ) -> ProviderCandidate:
        """Advance to the next candidate or raise on exhaustion (Step 5).

        Emits ``fallback.exhausted`` on the outer span before raising the
        typed ``RetryBreakerFallbackExhaustedError``.
        """
        try:
            next_candidate, _result = advance_or_raise(self.fallback_chain, failed)
        except FallbackChainExhaustedError as exc:
            outer_span.add_event(
                "fallback.exhausted",
                attributes={
                    "fallback.chain_length": chain_length,
                    "fallback.last_failure_class": last_failure_class or "unknown",
                    "fallback.exhaustion_cause": "per-candidate-retry-exhaustion",
                },
            )
            raise RetryBreakerFallbackExhaustedError(failed) from exc
        return next_candidate

    async def _run_per_candidate_attempts(
        self,
        *,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        candidate: ProviderCandidate,
        policy: RetryPolicy,
        breaker: Any,
        tracer: Any,
        outer_span: Any,
    ) -> _PerCandidateTerminal:
        """Run the per-attempt loop for a single candidate (Step 4).

        Returns a ``_PerCandidateTerminal`` carrying either the successful
        result (return path) or the last-failure attribution (abandon path).

        The C-CP-21 §21.2 staircase is consulted as a **cause-class classifier**,
        not a per-attempt counter: `advance_staircase` is stage-keyed lookup
        and `attempt` is bookkeeping per the function's own docstring. The
        wrapper passes ``STAGE_1_REFLEXION`` as `current` on every call;
        transient classes (`TRANSIENT_RETRY` / `REFLEXION_RECOVERABLE`) route
        to ``STAGE_2_RETRY_WITH_BACKOFF`` (retry); skip-classes
        (`PERMANENT_FAIL_EXIT` / `TERMINAL_FAIL_EXIT` / `HITL_RECOVERABLE`)
        route directly to ``STAGE_5_HITL_ESCALATION`` (escalate). The
        per-attempt loop is capped by ``RetryPolicy.max_attempts``; both the
        staircase-escalate branch and the max-attempts-exhaustion branch are
        reachable under this reading.
        """
        _ = outer_span  # outer-span event emission is handled at advance site
        rebound = _rebind_to_candidate(binding, candidate)
        last_failure_class: str | None = None

        for attempt in range(policy.max_attempts):
            with tracer.start_as_current_span(
                "harness.runtime.retry_attempt"
            ) as inner_span:
                inner_span.set_attribute("retry.attempt", attempt)
                inner_span.set_attribute("retry.attempt_count", policy.max_attempts)
                inner_span.set_attribute("retry.policy_id", RESERVED_LLM_DISPATCH_KEY)

                try:
                    result = await self.inner.dispatch(rebound, step)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    cause = _classify_provider_exception(exc)
                    if cause is None:
                        # Fail-fast: AUTH / payload-shape.
                        inner_span.set_attribute("retry.terminal", "fail-fast")
                        inner_span.set_attribute(
                            "retry.cause_class", type(exc).__name__
                        )
                        inner_span.set_attribute("retry.backoff_ms", 0)
                        transition = breaker.record_failure()
                        if transition is not None:
                            self._emit_breaker_transition(transition, outer_span)
                        last_failure_class = type(exc).__name__
                        return _PerCandidateTerminal(
                            result=None, last_failure_class=last_failure_class
                        )

                    # Transient: classify via staircase. STAGE_1 is passed as
                    # `current` every time — the staircase is a cause-class
                    # classifier, not stateful across attempts (per the spec
                    # narrative + `advance_staircase` docstring).
                    staircase_transition = self.retry_breaker.advance_staircase(
                        StaircaseStage.STAGE_1_REFLEXION, cause, attempt
                    )
                    next_stage = staircase_transition.to_stage
                    is_last_attempt = attempt == policy.max_attempts - 1
                    if (
                        next_stage is StaircaseStage.STAGE_2_RETRY_WITH_BACKOFF
                        and not is_last_attempt
                    ):
                        backoff_seconds = self.retry_breaker.compute_delay_seconds(
                            attempt
                        )
                        inner_span.set_attribute("retry.terminal", "retry")
                        inner_span.set_attribute(
                            "retry.cause_class", cause.value
                        )
                        inner_span.set_attribute(
                            "retry.backoff_ms", int(backoff_seconds * 1000)
                        )
                        last_failure_class = cause.value
                        # Sleep outside the span CM is fine; OTel ends the span
                        # at the with-exit. We sleep after recording the
                        # attempt terminal so the inner span carries the
                        # actually-elapsed backoff hint.
                    elif (
                        next_stage is StaircaseStage.STAGE_2_RETRY_WITH_BACKOFF
                        and is_last_attempt
                    ):
                        # Staircase would retry, but max_attempts exhausted.
                        inner_span.set_attribute("retry.terminal", "max-attempts")
                        inner_span.set_attribute(
                            "retry.cause_class", cause.value
                        )
                        inner_span.set_attribute("retry.backoff_ms", 0)
                        transition = breaker.record_failure()
                        if transition is not None:
                            self._emit_breaker_transition(transition, outer_span)
                        last_failure_class = "max-attempts"
                        return _PerCandidateTerminal(
                            result=None, last_failure_class=last_failure_class
                        )
                    else:
                        # Escalation: cross-family-fallback / local-terminal /
                        # HITL-escalation — abandon this candidate.
                        inner_span.set_attribute("retry.terminal", "escalate")
                        inner_span.set_attribute(
                            "retry.cause_class", cause.value
                        )
                        inner_span.set_attribute("retry.backoff_ms", 0)
                        transition = breaker.record_failure()
                        if transition is not None:
                            self._emit_breaker_transition(transition, outer_span)
                        last_failure_class = cause.value
                        return _PerCandidateTerminal(
                            result=None, last_failure_class=last_failure_class
                        )
                else:
                    # Success.
                    inner_span.set_attribute("retry.terminal", "success")
                    inner_span.set_attribute("retry.backoff_ms", 0)
                    transition = breaker.record_success()
                    if transition is not None:
                        self._emit_breaker_transition(transition, outer_span)
                    return _PerCandidateTerminal(
                        result=result, last_failure_class=None
                    )

            # Sleep between retries (outside the inner span CM).
            await self.sleep_fn(self.retry_breaker.compute_delay_seconds(attempt))

        # Unreachable: the last attempt's `is_last_attempt` branch above
        # always returns. Kept as a defensive fallback if the iteration
        # invariant ever drifts.
        return _PerCandidateTerminal(
            result=None,
            last_failure_class=last_failure_class or "max-attempts",
        )

    def _emit_breaker_transition(self, transition: Any, parent_span: Any) -> None:
        """Delegate breaker-transition span emission to the registry per
        spec §14.6 D5. Wrapper code is thin against breaker concerns."""
        self.retry_breaker.emit_breaker_transition_event(
            transition,
            parent_span,
        )


@dataclass(frozen=True, slots=True)
class _PerCandidateTerminal:
    """Per-candidate attempt-loop terminal carrier.

    ``result`` non-None iff a successful dispatch occurred (return path).
    Otherwise ``last_failure_class`` carries the last attribution token for
    the outer ``fallback.exhausted`` event.
    """

    result: Mapping[str, Any] | None
    last_failure_class: str | None


def _chain_length(chain: FallbackChain) -> int:
    """Total candidate count across the §4.1 four-field structure."""
    return (
        1
        + len(chain.same_family)
        + len(chain.cross_family)
        + (1 if chain.terminal is not None else 0)
    )


def materialize_retry_breaker_fallback_dispatcher_stage(
    *,
    inner: LLMDispatcher,
    retry_breaker: RetryBreakerRegistry,
    fallback_chain: FallbackChain,
    tracer_provider: Any,
    sleep_fn: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> RetryBreakerFallbackDispatcher:
    """Stage 5 LOOP_INIT factory for the retry/breaker/fallback wrapper
    (U-RT-58, C-RT-16).

    Constructs the wrapper around the inner C-RT-15 dispatcher. Bootstrap
    stage 5 invokes this AFTER the bare ``RuntimeLLMDispatcher`` is built
    (per the existing ``materialize_llm_dispatcher_stage`` site) and
    rebinds ``ctx.llm_dispatcher`` to the wrapper.

    The wrapper consumes ``ctx.retry_breaker`` (U-RT-24) +
    ``ctx.fallback_chain`` (stage 3b) + ``ctx.tracer_provider`` (C-RT-06)
    + the inner dispatcher (private). ``StepDispatcher`` Protocol shape
    preserved per spec §14.6.
    """
    return RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=retry_breaker,
        fallback_chain=fallback_chain,
        tracer_provider=tracer_provider,
        sleep_fn=sleep_fn,
    )

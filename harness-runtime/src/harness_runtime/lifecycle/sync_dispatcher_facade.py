"""Sync-facing facade over an async ``StepDispatcher`` (U-RT-59 Path B).

Per ``.harness/class_1_tension_u_rt_59_async_sync_step_dispatcher.md``.
This module was **discovery-status** at landing (the facade implemented and
unit-tested for cross-loop survival semantics, ahead of production wiring);
it is now WIRED into ``harness_runtime.bootstrap.stage_5_loop_init`` (binding
``INFERENCE_STEP → SyncDispatcherFacade(ctx.llm_dispatcher)`` and siblings at
stage 5, per the Path B wiring landing referenced below).

Why the facade exists
---------------------

The CP driver (``harness_cp.workflow_driver.execute_workflow``) is **sync**;
``harness_runtime.api.run`` invokes it via ``asyncio.to_thread`` so the asyncio
loop remains responsive to signal handlers + drain timeout per
``Spec_Harness_Runtime_v1.md`` §11.

The runtime's production LLM dispatchers
(``RuntimeLLMDispatcher`` per C-RT-15, ``RetryBreakerFallbackDispatcher``
per C-RT-16) are **async**: their provider clients (``AsyncAnthropic``,
``AsyncOpenAI``, ``AsyncOllamaClient``) are httpx-backed and **loop-bound**
once their connection pool is opened (stage 3a ping qualifies as open). The
driver's ``StepDispatcher`` Protocol at ``harness_cp/workflow_driver.py:175``
declares a **sync** ``def dispatch(...) -> Mapping[str, Any]``; binding an
async wrapper to it without an adapter ships a coroutine where the driver
expects a mapping (``TypeError: 'coroutine' object is not iterable`` at the
next line, or silent coroutine drop without ``await``).

Path B resolution: a sync facade that captures the outer loop at construction
time and bridges back to it via ``asyncio.run_coroutine_threadsafe`` when
called from the worker thread.

Cross-loop survival (discovery rationale)
-----------------------------------------

The literal fork-text Path B reading was ``asyncio.run(wrapper.dispatch(...))``
inside the ``to_thread`` worker. That is dead on arrival once provider clients
have made any request on the outer loop: ``asyncio.run`` creates a NEW event
loop, and the clients' httpx pools / transport state are bound to the OLD
loop. Reusing them on the new loop raises ``RuntimeError: ... attached to a
different loop`` (or transport-already-closed errors depending on which
loop-bound primitive is hit first).

The viable variant is to schedule the coroutine *back* to the outer loop via
``asyncio.run_coroutine_threadsafe``. The outer loop is alive (it is awaiting
``asyncio.wait_for(asyncio.to_thread(execute_workflow, ...))``); the worker
thread blocks on ``future.result(timeout=...)``. Provider clients stay bound
to the loop where they were constructed.

Two constraints surfaced at design (advisor cross-check, 2026-05-20):

1. **Loop-capture timing.** The captured loop must be the loop that hosts
   the eventual ``to_thread``. Stage 5 bootstrap runs in
   ``async def execute(...)`` invoked from ``await run_bootstrap(...)`` at
   ``harness_runtime/api.py:349`` — the running loop at facade construction
   IS the loop that subsequently awaits the ``to_thread`` at api.py:399.
   ``materialize_sync_dispatcher_facade`` enforces this by calling
   ``asyncio.get_running_loop()`` (raises ``RuntimeError`` if invoked from
   sync code or a worker thread).

2. **Cancellation interaction.** Outer ``wait_for(drain_timeout)`` cancels
   the ``to_thread`` future but cannot cancel the thread. Without a bound
   on ``future.result(...)``, a hung inner coroutine + a drained outer loop
   would leak the worker thread for the lifetime of the interpreter. The
   facade applies ``future.result(timeout=result_timeout_seconds)``. The
   bound is constructor-supplied so the caller can align it with the
   drain-timeout / step-timeout budget. On expiry, ``TimeoutError`` is
   re-raised verbatim; the driver maps to its existing typed fail-mode
   taxonomy per C-CP-25 §25.3.3.4 (no new fail class added at the facade
   layer — the facade is a transport adapter, not a policy surface).

Discovery test coverage
-----------------------

See ``harness-runtime/tests/test_lifecycle_sync_dispatcher_facade.py``:

- **D1** ``asyncio.run`` inside ``to_thread`` on a loop-bound httpx client
  raises (evidence the naive reading is non-viable).
- **D2** ``run_coroutine_threadsafe`` to captured outer loop succeeds with
  the same loop-bound httpx client (evidence Path B variant works).
- **D3** Facade satisfies the sync ``StepDispatcher`` Protocol contract
  with realistic argument shapes.
- **D4** ``result_timeout_seconds`` bound fires when the inner coroutine
  exceeds the budget.
- **D5** Inner exceptions propagate verbatim through ``future.result()``.
- **D6** ``materialize_sync_dispatcher_facade`` raises ``RuntimeError``
  when called outside an async context.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep

__all__ = [
    "AsyncStepDispatcher",
    "StepDispatchTimeoutError",
    "SyncDispatcherFacade",
    "materialize_sync_dispatcher_facade",
]

#: Bounded post-cancel grace for the dispatch task's completion ack (codex
#: rounds 3-5) — covers CancelledError delivery + run_audit_off_loop's
#: join-on-cancel of one KMS sign + local file writes.
_AUDIT_DRAIN_GRACE_SECONDS = 10.0


class StepDispatchTimeoutError(Exception):
    """Typed per-step worker-thread blocking timeout.

    Raised by ``SyncDispatcherFacade.dispatch`` when the underlying
    ``future.result(timeout=self.result_timeout_seconds)`` exceeds the
    bound. Discriminated from generic ``TimeoutError`` so the CP workflow
    driver can map to ``RT-FAIL-STEP-DISPATCH-TIMEOUT`` per
    ``Spec_Harness_Runtime_v1.md`` v1.31 §11 failure-mode taxonomy.

    Cross-axis layering discipline: harness-cp cannot import this class
    (harness-runtime → harness-cp would invert the workspace dependency
    graph). The driver matches by ``type(exc).__name__ ==
    "StepDispatchTimeoutError"`` per the existing HITLPauseRequestedSignal
    name-match pattern at ``workflow_driver.py:830``.
    """


@runtime_checkable
class AsyncStepDispatcher(Protocol):
    """Async sibling of ``harness_cp.workflow_driver.StepDispatcher``.

    Concrete async dispatchers (``RetryBreakerFallbackDispatcher`` per
    C-RT-16, ``RuntimeLLMDispatcher`` per C-RT-15) satisfy this Protocol
    structurally. The facade wraps any conformer into the sync
    ``StepDispatcher`` Protocol consumed by the CP driver, bridging the
    async/sync seam at U-RT-59 §14.7.7 wiring.

    Declared ``@runtime_checkable`` for parity with the CP-side Protocol;
    ``isinstance`` checks here remain attribute-presence only and do NOT
    verify async-ness (which is the root sleeping-defect class that
    surfaced the fork in the first place). Callers should rely on static
    type-checking, not runtime isinstance, for shape conformance.
    """

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class SyncDispatcherFacade:
    """Sync ``StepDispatcher`` Protocol facade over an ``AsyncStepDispatcher``.

    Construction MUST occur on the event loop that will host the eventual
    ``asyncio.to_thread(execute_workflow, ...)`` invocation. Use
    ``materialize_sync_dispatcher_facade`` rather than constructing directly
    so the loop is captured uniformly.

    Fields
    ------
    inner :
        The async dispatcher to wrap. The facade does not own it; lifetime
        is the caller's responsibility (stage 5 bootstrap binds it via
        ``ctx.llm_dispatcher``).
    loop :
        The captured outer event loop. The facade's ``dispatch`` schedules
        coroutines onto this loop from worker threads. Reused across all
        ``dispatch`` calls for the lifetime of the bootstrap context.
    result_timeout_seconds :
        Upper bound on the worker-thread blocking wait per ``dispatch``
        invocation. On expiry, ``concurrent.futures.TimeoutError`` is raised
        (Python ≥ 3.11: aliased to ``builtins.TimeoutError``). Caller
        chooses the bound; aligning with drain-timeout budget per
        ``Spec_Harness_Runtime_v1.md`` §11 is the natural choice.
    """

    inner: AsyncStepDispatcher
    loop: asyncio.AbstractEventLoop
    result_timeout_seconds: float

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Sync ``StepDispatcher.dispatch``; bridges to captured async loop.

        Invoked from the CP driver's worker thread (per
        ``asyncio.to_thread(execute_workflow, ...)`` at
        ``harness_runtime/api.py:399``). Schedules
        ``self.inner.dispatch(...)`` onto ``self.loop`` via
        ``asyncio.run_coroutine_threadsafe`` and blocks the worker thread on
        ``future.result(timeout=self.result_timeout_seconds)``.

        Exception propagation: ``future.result()`` re-raises any exception
        raised by the inner coroutine verbatim (no wrapping). The driver's
        existing typed try/except per C-CP-25 §25.3.3.4 maps to fail-mode
        taxonomy as before.
        """
        # Per-dispatch completion acknowledgement (codex round-5 P1): set in
        # the task's `finally`, i.e. AFTER CancelledError has propagated
        # through the inner dispatch — including run_audit_off_loop's
        # join-on-cancel — so waiting on it below proves THIS dispatch's
        # audit work is complete-or-cancelled-before-start. A bare
        # `future.cancel()` snapshot could observe an audit job that had
        # not been SUBMITTED yet (task busy in sync work on the loop) and
        # miss its later write entirely.
        completion_ack = threading.Event()
        # B-48 (U-RT-142): re-bind the fan-out branch's capacity lease across
        # the loop bridge. The CP fan-out sets BRANCH_CAPACITY_LEASE_VAR
        # before `asyncio.to_thread(dispatcher.dispatch, ...)` (context copies
        # into THIS worker thread), but `run_coroutine_threadsafe` creates the
        # loop-side task in the LOOP's context — without the re-bind the
        # offload venue would double-charge an inner-dispatch frame the
        # fan-out's atomic allocation already holds (occupied+N+S model).
        from harness_cp.sub_agent_dispatch_capacity_authority import (
            BRANCH_CAPACITY_LEASE_VAR,
        )

        branch_lease = BRANCH_CAPACITY_LEASE_VAR.get()
        # B-48 (U-RT-143; §14.8.10.3): a fresh per-dispatch cancel token,
        # LINKED to any ambient ancestor token — this thread is a worker of an
        # enclosing offloaded job during recursive descent, so its context
        # carries the ancestor's token and tripping the ancestor fences this
        # whole chain (the token cascade). The token is re-bound into the
        # loop-side task (same bridge problem as the branch lease) so the
        # offload venue, the child driver's step boundaries, the retry loop's
        # effect entries, and the post-child audit persists all read it.
        from harness_cp.sub_agent_dispatch_cancellation import (
            DISPATCH_CANCEL_TOKEN_VAR,
            DispatchCancelToken,
            FenceAckOutcome,
        )

        cancel_token = DispatchCancelToken(parent=DISPATCH_CANCEL_TOKEN_VAR.get())
        coro = _ack_on_completion(
            _rebind_dispatch_context(
                self.inner.dispatch(binding, step, step_context=step_context),
                branch_lease,
                cancel_token,
            ),
            completion_ack,
            cancel_token,
        )
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=self.result_timeout_seconds)
        except TimeoutError as exc:
            # `future.result(timeout=...)` only stops *waiting* — the inner
            # coroutine (and its cost/audit-ledger write) keeps running
            # detached on `self.loop` unless explicitly cancelled. Without
            # this, a retry of the same run can execute concurrently with
            # the orphaned original dispatch: two live LLM calls / two audit
            # writes for the same logical step. `run_coroutine_threadsafe`'s
            # future chains cancellation back to the scheduled Task via
            # `call_soon_threadsafe`, so `.cancel()` is safe to call here
            # from this (worker) thread.
            future.cancel()
            # B-48 (U-RT-143; §14.8.10.3 part 2/3): trip the JOB-WIDE effect
            # fence — no further F2/audit writes begin anywhere in the job
            # (post-child persists included; cascades through descent) —
            # then run the bounded join to the fence acknowledgement.
            cancel_token.trip()
            # Codex rounds 3-5 (B-47 PR B2a): wait for the dispatch task to
            # ACKNOWLEDGE cancellation before surfacing — the ack fires only
            # after run_audit_off_loop's join-on-cancel, so no audit write
            # for this step lands after the raise. B-48 extends the join to
            # the WORKER job's fence ack (an offloaded worker outlives the
            # cancelled task); the two waits share ONE grace deadline. The
            # disposition rides attributes, NOT a subclass: harness-cp's
            # driver classifies by `type(exc).__name__ ==
            # "StepDispatchTimeoutError"` (it cannot import runtime types),
            # so a subclass would silently fall out of the
            # RT-FAIL-STEP-DISPATCH-TIMEOUT taxonomy (codex round-5 P2).
            join_deadline = time.monotonic() + _AUDIT_DRAIN_GRACE_SECONDS
            acked = completion_ack.wait(timeout=_AUDIT_DRAIN_GRACE_SECONDS)
            remaining_grace = max(0.0, join_deadline - time.monotonic())
            fence_outcome = cancel_token.wait_ack(grace_seconds=remaining_grace)
            drain_incomplete = not acked or fence_outcome is FenceAckOutcome.UNACKED_DRAINING
            timeout_error = StepDispatchTimeoutError(
                f"step dispatch exceeded {self.result_timeout_seconds}s bound"
                + (
                    ""
                    if not drain_incomplete
                    else (
                        f" AND the dispatch did not acknowledge the tripped "
                        f"effect fence within the {_AUDIT_DRAIN_GRACE_SECONDS}s "
                        f"grace (disposition: {fence_outcome.value}) — the "
                        f"worker is draining under the fence; effects are "
                        f"AMBIGUOUS and this step is PERMANENTLY TERMINAL; "
                        f"do not retry — workflow re-run after drain is an "
                        f"operator action"
                    )
                )
                + (
                    f" (disposition: {fence_outcome.value} — an effect-bearing "
                    f"operation was in flight at fence trip; effects AMBIGUOUS, "
                    f"step PERMANENTLY TERMINAL, worker finished — no drain in "
                    f"progress)"
                    if fence_outcome is FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS
                    else ""
                )
            )
            timeout_error.audit_drain_incomplete = drain_incomplete  # type: ignore[attr-defined]
            timeout_error.fence_ack_outcome = fence_outcome.value  # type: ignore[attr-defined]
            raise timeout_error from exc

    def cohort_key(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
    ) -> str | None:
        """Delegate to inner if it is CohortKeyCapable; else return None.

        B-18-3C-PREWARM-COHORTKEY delegation stub. The facade sits at the top
        of the production dispatcher chain (registry boundary). Delegating
        ensures `isinstance(facade, CohortKeyCapable)` is True and the call
        reaches the logic-bearing `RuntimeLLMDispatcher.cohort_key()`.
        """
        from harness_cp.workflow_driver import CohortKeyCapable

        if isinstance(self.inner, CohortKeyCapable):
            return self.inner.cohort_key(binding, step)
        return None


async def _ack_on_completion(coro: Any, ack: threading.Event, cancel_token: Any) -> Any:
    """Await `coro`; ack in the finally — the per-dispatch completion
    acknowledgement the facade's timeout path waits on (codex round-5 P1).

    B-48 (U-RT-143): also acks the dispatch's cancel token FROM THE TASK —
    honored only when ack ownership was not deferred to a worker job (the
    offload venue defers it, since a cancelled task's finally fires while
    the worker may still be running)."""
    try:
        return await coro
    finally:
        ack.set()
        cancel_token.ack_from_task()


async def _rebind_dispatch_context(coro: Any, lease: Any, cancel_token: Any) -> Any:
    """Re-bind the branch lease + cancel token inside the loop-side task.

    B-48 (U-RT-142/143): ContextVars set in the branch worker thread do not
    survive `run_coroutine_threadsafe` (the task is created in the loop's
    context), so the facade captures them worker-side and re-sets them here —
    inside the running task, where nested awaits (the composer's offload
    venue, the retry loop's effect entries) can read them.
    """
    from harness_cp.sub_agent_dispatch_cancellation import DISPATCH_CANCEL_TOKEN_VAR
    from harness_cp.sub_agent_dispatch_capacity_authority import (
        BRANCH_CAPACITY_LEASE_VAR,
    )

    token_reset = DISPATCH_CANCEL_TOKEN_VAR.set(cancel_token)
    lease_reset = BRANCH_CAPACITY_LEASE_VAR.set(lease) if lease is not None else None
    try:
        return await coro
    finally:
        if lease_reset is not None:
            BRANCH_CAPACITY_LEASE_VAR.reset(lease_reset)
        DISPATCH_CANCEL_TOKEN_VAR.reset(token_reset)


def materialize_sync_dispatcher_facade(
    inner: AsyncStepDispatcher,
    *,
    result_timeout_seconds: float,
) -> SyncDispatcherFacade:
    """Construct ``SyncDispatcherFacade`` capturing the running event loop.

    MUST be invoked from a coroutine running on the event loop that hosts
    the subsequent worker-thread ``dispatch(...)`` invocations. Stage 5
    bootstrap satisfies this (``async def execute(...)`` awaited from
    ``await run_bootstrap(...)`` at ``harness_runtime/api.py:349``).

    Raises
    ------
    RuntimeError
        If called from sync code or a non-loop-owning thread —
        ``asyncio.get_running_loop()`` propagates verbatim.
    """
    loop = asyncio.get_running_loop()
    return SyncDispatcherFacade(
        inner=inner,
        loop=loop,
        result_timeout_seconds=result_timeout_seconds,
    )

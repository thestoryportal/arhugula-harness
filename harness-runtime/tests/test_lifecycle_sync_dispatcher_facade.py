"""Discovery tests for U-RT-59 Path B — ``SyncDispatcherFacade``.

Per ``.harness/class_1_tension_u_rt_59_async_sync_step_dispatcher.md``. These
tests are **discovery-status**: they validate that ``Path B`` (sync facade
over async dispatcher via ``asyncio.run_coroutine_threadsafe`` to the
captured outer loop) survives the loop-binding pathology that disqualifies
the literal fork-text reading (``asyncio.run`` inside a worker thread on a
loop-bound httpx client).

Test taxonomy (mapped to module docstring D1-D6):

  D1 — Naive ``asyncio.run`` inside ``to_thread`` raises when the inner
       coroutine touches a loop-bound asyncio primitive (here: an
       ``asyncio.Future`` created on the outer loop). Negative control;
       evidence the literal fork-text Path B reading is non-viable for
       production dispatchers whose provider clients use loop-bound
       anyio primitives (httpx ``ConnectionPool``'s ``anyio.Semaphore``,
       ``AsyncOpenAI`` retry primitives, etc.). NOTE: ``httpx.MockTransport``
       does NOT exhibit this pathology because it dispatches synchronously
       without touching the loop-bound transport state — that is why a
       MockTransport-based negative control would silently pass and miss
       the production failure mode.
  D2 — ``asyncio.run_coroutine_threadsafe`` to captured outer loop succeeds
       with a real ``httpx.AsyncClient`` (positive evidence Path B variant
       works on httpx loop-binding semantics).
  D3 — Facade satisfies the sync ``StepDispatcher`` Protocol contract with
       realistic ``StepEffectiveBinding`` / ``WorkflowStep`` /
       ``StepExecutionContext`` argument shapes.
  D4 — ``result_timeout_seconds`` bound fires when inner exceeds budget.
  D5 — Inner exceptions propagate verbatim through ``future.result()``.
  D6 — ``materialize_sync_dispatcher_facade`` raises ``RuntimeError`` when
       called outside an async context.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx
import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver import StepDispatcher
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.sync_dispatcher_facade import (
    AsyncStepDispatcher,
    materialize_sync_dispatcher_facade,
)

# ---------------------------------------------------------------------------
# Fixture builders — mirror test_lifecycle_retry_breaker_fallback conventions
# ---------------------------------------------------------------------------


def _binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider="anthropic", model="claude-test"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
    )


def _step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"messages": [{"role": "user", "content": "hi"}]},
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="test-step-key",
        tenant_id=None,
        step_index=0,
    )


# ---------------------------------------------------------------------------
# Concrete async dispatchers used in D3-D5
# ---------------------------------------------------------------------------


@dataclass
class _RecordingAsyncDispatcher:
    """Async dispatcher that returns a fixed mapping and records invocations."""

    output: Mapping[str, Any]
    invocations: list[tuple[StepEffectiveBinding, WorkflowStep, StepExecutionContext]]

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        self.invocations.append((binding, step, step_context))
        return self.output


@dataclass
class _SlowAsyncDispatcher:
    """Async dispatcher that sleeps for ``delay_seconds`` before returning."""

    delay_seconds: float

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        await asyncio.sleep(self.delay_seconds)
        return {}


class _DispatchBoomError(Exception):
    """Inner exception raised by ``_RaisingAsyncDispatcher``."""


@dataclass
class _RaisingAsyncDispatcher:
    """Async dispatcher that raises a typed exception verbatim."""

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        raise _DispatchBoomError("inner dispatcher failed")


# ---------------------------------------------------------------------------
# D1 — Naive `asyncio.run` inside `to_thread` fails on loop-bound primitive
# ---------------------------------------------------------------------------


def _httpx_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"ok": True})


@pytest.mark.asyncio
async def test_d1_naive_asyncio_run_inside_to_thread_fails_on_loop_bound_primitive() -> None:
    """D1 — naive ``asyncio.run`` raises when inner touches loop-bound state.

    Direct demonstration of the cross-loop pathology that disqualifies the
    literal fork-text Path B reading. Create an ``asyncio.Future`` on the
    outer loop; from a worker thread, ``asyncio.run`` a coroutine that awaits
    that future. The new loop created by ``asyncio.run`` cannot drive a
    future bound to a different loop — Python raises
    ``RuntimeError: ... attached to a different loop``.

    This is the same pathology production async provider clients exhibit:
    ``httpx.AsyncHTTPTransport`` opens an anyio-backed ``ConnectionPool``
    whose ``Semaphore`` is loop-bound on first use (stage 3a ping qualifies).
    A subsequent ``asyncio.run(client.request(...))`` from a worker thread
    creates a new loop, the request reaches the loop-bound semaphore, and
    the await raises the same ``RuntimeError``.

    ``httpx.MockTransport`` (used at D2) does NOT exhibit this pathology
    because it dispatches synchronously via the handler callable, never
    acquiring loop-bound transport state — which is why a MockTransport
    negative control would silently pass and miss the production failure
    mode. We use the asyncio.Future contraption instead to assert the
    pathology directly.
    """
    outer_loop_future: asyncio.Future[int] = asyncio.get_running_loop().create_future()
    # Leave the future PENDING — a pre-resolved future short-circuits the
    # loop-affinity check at await time, masking the cross-loop pathology.

    async def _inner_await_outer_future() -> int:
        # `wait_for` bounds the wait so the worker thread cannot hang if the
        # cross-loop check is unexpectedly bypassed; in practice the
        # RuntimeError fires before the wait expires.
        return await asyncio.wait_for(outer_loop_future, timeout=1.0)

    def _worker_naive() -> int:
        # `asyncio.run` creates a new loop in this worker thread.
        # The pending future is bound to the outer loop.
        return asyncio.run(_inner_await_outer_future())

    with pytest.raises(RuntimeError, match="attached to a different loop"):
        await asyncio.to_thread(_worker_naive)


async def _inner_get(client: httpx.AsyncClient) -> httpx.Response:
    return await client.get("/probe")


# ---------------------------------------------------------------------------
# D2 — `run_coroutine_threadsafe` to captured outer loop succeeds
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_d2_run_coroutine_threadsafe_to_outer_loop_succeeds() -> None:
    """D2 — Path B variant works on real httpx loop-binding semantics.

    Same loop-bound client as D1. From the worker thread, schedule the
    request back onto the outer loop via ``asyncio.run_coroutine_threadsafe``
    and block on ``future.result()``. The transport stays bound to the loop
    where it was opened; the request succeeds.
    """
    transport = httpx.MockTransport(_httpx_handler)
    client = httpx.AsyncClient(transport=transport, base_url="http://test")
    try:
        # Open the pool on the outer loop.
        await client.get("/ping")

        outer_loop = asyncio.get_running_loop()

        def _worker_scheduled() -> int:
            future = asyncio.run_coroutine_threadsafe(_inner_get(client), outer_loop)
            return future.result(timeout=5.0).status_code

        status = await asyncio.to_thread(_worker_scheduled)
        assert status == 200
    finally:
        await client.aclose()


# ---------------------------------------------------------------------------
# D3 — Facade satisfies sync StepDispatcher Protocol with realistic args
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_d3_facade_satisfies_step_dispatcher_protocol() -> None:
    """D3 — facade behaves as a sync ``StepDispatcher`` from a worker thread."""
    expected_output = {"result": "ok", "attempt": 1}
    inner = _RecordingAsyncDispatcher(output=expected_output, invocations=[])
    facade = materialize_sync_dispatcher_facade(inner, result_timeout_seconds=5.0)

    assert isinstance(facade, StepDispatcher)  # structural sync Protocol satisfied
    assert isinstance(inner, AsyncStepDispatcher)  # structural async Protocol satisfied

    binding = _binding()
    step = _step()
    step_context = _step_context()

    def _worker() -> Mapping[str, Any]:
        return facade.dispatch(binding, step, step_context=step_context)

    output = await asyncio.to_thread(_worker)
    assert dict(output) == expected_output
    assert len(inner.invocations) == 1
    recorded_binding, recorded_step, recorded_ctx = inner.invocations[0]
    assert recorded_binding == binding
    assert recorded_step == step
    assert recorded_ctx == step_context


# ---------------------------------------------------------------------------
# D4 — Result timeout bound fires
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_d4_result_timeout_fires() -> None:
    """D4 — ``result_timeout_seconds`` raises when inner exceeds budget."""
    inner = _SlowAsyncDispatcher(delay_seconds=2.0)
    facade = materialize_sync_dispatcher_facade(inner, result_timeout_seconds=0.1)

    def _worker() -> Mapping[str, Any]:
        return facade.dispatch(_binding(), _step(), step_context=_step_context())

    with pytest.raises(TimeoutError):
        await asyncio.to_thread(_worker)


# ---------------------------------------------------------------------------
# D5 — Inner exception propagation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_d5_inner_exception_propagates_verbatim() -> None:
    """D5 — inner exceptions propagate through ``future.result()`` verbatim."""
    facade = materialize_sync_dispatcher_facade(
        _RaisingAsyncDispatcher(), result_timeout_seconds=5.0
    )

    def _worker() -> Mapping[str, Any]:
        return facade.dispatch(_binding(), _step(), step_context=_step_context())

    with pytest.raises(_DispatchBoomError, match="inner dispatcher failed"):
        await asyncio.to_thread(_worker)


# ---------------------------------------------------------------------------
# D6 — Construction outside async context raises
# ---------------------------------------------------------------------------


def test_d6_materialize_outside_async_context_raises() -> None:
    """D6 — ``materialize_sync_dispatcher_facade`` enforces loop-capture timing."""
    with pytest.raises(RuntimeError):
        materialize_sync_dispatcher_facade(
            _RecordingAsyncDispatcher(output={}, invocations=[]),
            result_timeout_seconds=5.0,
        )

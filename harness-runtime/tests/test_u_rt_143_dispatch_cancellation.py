"""U-RT-143 — three-part dispatch-time cancellation policy witnesses (B-48).

Tests per Implementation_Plan_Harness_Runtime_v2_50.md §1.4 (PD-8
mutation-probed): the token cascade fencing a whole descent chain; the
job-wide effect fence suppressing the post-child audit persists; the
two-outcome fence-ack classification (acked-clean / acked-inflight-ambiguous
/ unacked-draining) on the surfaced `StepDispatchTimeoutError`; the
effect-entry token consult stopping a new retry attempt within a step; the
terminal never-retried disposition; and the U-RT-141 lease rider — a
draining worker retains its frame lease until its job terminates.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Mapping
from typing import Any, cast

import pytest
from harness_cp.sub_agent_dispatch_cancellation import (
    DISPATCH_CANCEL_TOKEN_VAR,
    DispatchCancelToken,
    DispatchFenceTrippedSignal,
    FenceAckOutcome,
)
from harness_runtime.lifecycle.hitl_gate_composer import (
    InnerDispatchMode,
)
from harness_runtime.lifecycle.sub_agent_dispatch_executor import (
    SubAgentDispatchExecutor,
)
from harness_runtime.lifecycle.sync_dispatcher_facade import (
    StepDispatchTimeoutError,
    materialize_sync_dispatcher_facade,
)

# ---------------------------------------------------------------------------
# Local fixtures (self-contained — test modules are not importable packages)
# ---------------------------------------------------------------------------


def _make_step(step_id: str = "step-0") -> Any:
    from harness_core import StepID
    from harness_cp.workflow_driver_types import StepKind, WorkflowStep

    return WorkflowStep(
        step_id=StepID(step_id), step_kind=StepKind.SUB_AGENT_DISPATCH, step_payload={}
    )


def _make_step_context() -> Any:
    from harness_as.sandbox_tier import SandboxTier
    from harness_core import ActionID
    from harness_cp.gate_level_rule import GateLevel
    from harness_cp.workflow_driver_types import StepExecutionContext
    from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

    return StepExecutionContext(
        workflow_id="test",
        parent_action_id=ActionID("workflow:test:step:0"),
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id=Identifier("test-agent")),
        parent_entry_hash="",
        parent_idempotency_key=Identifier("test-idempotency-key"),
        tenant_id=None,
        step_index=0,
        hitl_placements=(),
    )


def _make_composer(
    *,
    inner: Any,
    mode: InnerDispatchMode = InnerDispatchMode.DIRECT_AWAIT,
    executor: SubAgentDispatchExecutor | None = None,
) -> Any:
    from harness_cp.hitl_placement import HITLPlacementKind
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_od.audit_ledger_types import SignatureAlgorithm
    from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer
    from opentelemetry.sdk.trace import TracerProvider

    return RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.SUB_AGENT_BOUNDARY}),
        ask_user_question_surface=cast(Any, object()),
        ledger_writer=cast(Any, object()),
        audit_writer=cast(Any, object()),
        tracer_provider=TracerProvider(),
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        inner_dispatch_mode=mode,
        dispatch_executor=executor,
    )


# ---------------------------------------------------------------------------
# Token carrier semantics
# ---------------------------------------------------------------------------


def test_token_cascade_trips_children_and_late_links() -> None:
    parent = DispatchCancelToken()
    child = DispatchCancelToken(parent=parent)
    grandchild = DispatchCancelToken(parent=child)
    parent.trip()
    assert child.tripped and grandchild.tripped
    # A descendant linked AFTER the trip is fenced immediately (a nested
    # dispatch starting during the drain window cannot escape the fence).
    late = DispatchCancelToken(parent=parent)
    assert late.tripped


def test_effect_entry_tracks_inflight_at_trip_and_blocks_new_effects() -> None:
    token = DispatchCancelToken()
    with token.effect_entry():
        token.trip()  # effect in flight at trip
    token.ack()
    assert token.wait_ack(grace_seconds=0.1) is FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS
    # After the trip, no NEW effect begins.
    with pytest.raises(DispatchFenceTrippedSignal):
        with token.effect_entry():
            pytest.fail("a new effect began after the fence tripped")


def test_clean_trip_between_operations_acks_clean() -> None:
    token = DispatchCancelToken()
    with token.effect_entry():
        pass  # operation completed before the trip
    token.trip()
    token.ack()
    assert token.wait_ack(grace_seconds=0.1) is FenceAckOutcome.ACKED_CLEAN


def test_unacked_grace_expiry_is_worker_draining_under_fence() -> None:
    token = DispatchCancelToken()
    token.trip()
    outcome = token.wait_ack(grace_seconds=0.05)
    assert outcome is FenceAckOutcome.UNACKED_DRAINING
    assert outcome.value == "worker_draining_under_fence"


# ---------------------------------------------------------------------------
# Facade-surfaced fence-ack outcomes (§14.8.10.3 rounds 10/11/12/40)
# ---------------------------------------------------------------------------


class _SlowSyncInner:
    """Sync inner sleeping WITHOUT holding an effect entry (between-ops shape)."""

    def __init__(self, delay: float) -> None:
        self._delay = delay
        self.calls = 0

    def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
        _ = (binding, step, step_context)
        self.calls += 1
        time.sleep(self._delay)
        return {"done": True}


class _InflightEffectSyncInner:
    """Sync inner holding an effect entry across the timeout window."""

    def __init__(self, delay: float) -> None:
        self._delay = delay

    def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
        _ = (binding, step, step_context)
        token = DISPATCH_CANCEL_TOKEN_VAR.get()
        assert token is not None
        with token.effect_entry():
            time.sleep(self._delay)  # an effect-bearing op in flight at trip
        return {"done": True}


async def _dispatch_via_facade(inner: Any, *, timeout_seconds: float) -> Mapping[str, Any]:
    executor = SubAgentDispatchExecutor(frame_budget=8)
    composer = _make_composer(inner=inner, mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor)
    facade = materialize_sync_dispatcher_facade(
        cast(Any, composer), result_timeout_seconds=timeout_seconds
    )
    return await asyncio.to_thread(
        facade.dispatch, object(), _make_step(), step_context=_make_step_context()
    )


@pytest.mark.asyncio
async def test_ack_clean_trip_surfaces_unqualified_timeout() -> None:
    """Fence trips between operations; the worker finishes inside the grace
    → NO drain disposition (effects genuinely unambiguous)."""
    with pytest.raises(StepDispatchTimeoutError) as excinfo:
        await _dispatch_via_facade(_SlowSyncInner(0.5), timeout_seconds=0.05)
    err = excinfo.value
    assert err.fence_ack_outcome == FenceAckOutcome.ACKED_CLEAN.value  # type: ignore[attr-defined]
    assert err.audit_drain_incomplete is False  # type: ignore[attr-defined]
    assert "worker_draining_under_fence" not in str(err)


@pytest.mark.asyncio
async def test_ack_after_inflight_effect_is_ambiguous_terminal() -> None:
    """An effect-bearing call in flight at trip, acked within grace → the
    DISTINCT acked-ambiguity disposition (mutation probe: keying on
    ack-presence alone passes the in-flight case as safe and fails)."""
    with pytest.raises(StepDispatchTimeoutError) as excinfo:
        await _dispatch_via_facade(_InflightEffectSyncInner(0.5), timeout_seconds=0.05)
    err = excinfo.value
    assert err.fence_ack_outcome == FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS.value  # type: ignore[attr-defined]
    assert "fence_acked_effect_ambiguous" in str(err)
    # No false active-drain report (codex round-40).
    assert "worker_draining_under_fence" not in str(err)


@pytest.mark.asyncio
async def test_grace_expiry_surfaces_worker_draining_under_fence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Worker still inside its blocking call at grace expiry → the
    `worker_draining_under_fence` AMBIGUOUS/TERMINAL disposition."""
    import harness_runtime.lifecycle.sync_dispatcher_facade as facade_mod

    monkeypatch.setattr(facade_mod, "_AUDIT_DRAIN_GRACE_SECONDS", 0.2)
    with pytest.raises(StepDispatchTimeoutError) as excinfo:
        await _dispatch_via_facade(_SlowSyncInner(2.0), timeout_seconds=0.05)
    err = excinfo.value
    assert err.fence_ack_outcome == FenceAckOutcome.UNACKED_DRAINING.value  # type: ignore[attr-defined]
    assert err.audit_drain_incomplete is True  # type: ignore[attr-defined]
    assert "worker_draining_under_fence" in str(err)
    assert "do not retry" in str(err)


@pytest.mark.asyncio
async def test_drained_under_fence_step_is_terminal_never_automatically_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The disposition is TERMINAL: the inner was invoked exactly once — no
    automatic re-dispatch path fires (the §14.8.1 SUB_AGENT_DISPATCH row
    carries no retry layer; mutation probe: routing the error through a
    retryable fail-class re-runs the step and fails the call-count pin)."""
    import harness_runtime.lifecycle.sync_dispatcher_facade as facade_mod

    monkeypatch.setattr(facade_mod, "_AUDIT_DRAIN_GRACE_SECONDS", 0.2)
    inner = _SlowSyncInner(1.0)
    with pytest.raises(StepDispatchTimeoutError):
        await _dispatch_via_facade(inner, timeout_seconds=0.05)
    await asyncio.sleep(1.2)  # let the abandoned worker drain fully
    assert inner.calls == 1


# ---------------------------------------------------------------------------
# Descent-chain cascade through REAL nested facades (§14.8.10.3)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parent_child_grandchild_cancellation_chain_fences_whole_descent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tripping the parent dispatch's fence reaches the GRANDCHILD's job:
    the ancestor token cascades through the per-job tokens the nested
    facades link (a timed-out child blocked inside a nested dispatch cannot
    reach its own next token check while the grandchild runs separately)."""
    import harness_runtime.lifecycle.sync_dispatcher_facade as facade_mod

    monkeypatch.setattr(facade_mod, "_AUDIT_DRAIN_GRACE_SECONDS", 0.3)
    executor = SubAgentDispatchExecutor(frame_budget=8)
    grandchild_fenced = threading.Event()

    class _Grandchild:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            _ = (binding, step, step_context)
            token = DISPATCH_CANCEL_TOKEN_VAR.get()
            assert token is not None
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                if token.tripped:
                    grandchild_fenced.set()
                    raise DispatchFenceTrippedSignal
                time.sleep(0.01)
            return {"level": "grandchild"}

    grandchild_composer = _make_composer(
        inner=_Grandchild(), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    grandchild_facade = materialize_sync_dispatcher_facade(
        cast(Any, grandchild_composer), result_timeout_seconds=10.0
    )

    class _Child:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            return grandchild_facade.dispatch(
                binding, _make_step("step-grandchild"), step_context=step_context
            )

    child_composer = _make_composer(
        inner=_Child(), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    child_facade = materialize_sync_dispatcher_facade(
        cast(Any, child_composer), result_timeout_seconds=0.2
    )

    # The PARENT's per-step bound expires while the grandchild still runs —
    # the parent-side trip must fence the whole descent.
    with pytest.raises(StepDispatchTimeoutError):
        await asyncio.to_thread(
            child_facade.dispatch,
            object(),
            _make_step("step-child"),
            step_context=_make_step_context(),
        )
    assert grandchild_fenced.wait(timeout=2.0)


# ---------------------------------------------------------------------------
# Post-child audit persists under the fence (§14.8.10.3 part 2)
# ---------------------------------------------------------------------------


def test_no_new_child_effects_after_failure_surfaces_including_post_child_audit_sites() -> None:
    """A tripped job fence suppresses `_compose_and_persist_audit` — ALL four
    post-child call sites route through it, so the single entry consult
    covers SUCCESS/DRAINED + exception/FAILED/PAUSED (mutation probe:
    unfencing the method makes this call touch the sentinel args and error
    instead of returning the suppressed (None, None))."""
    from harness_runtime.lifecycle.sub_agent_dispatch import RuntimeSubAgentDispatcher

    token = DispatchCancelToken()
    token.trip()
    var_token = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        result = RuntimeSubAgentDispatcher._compose_and_persist_audit(
            cast(RuntimeSubAgentDispatcher, object()),  # self untouched under the fence
            parent_action_id=cast(Any, "parent-action"),
            descent=object(),
            payload=cast(Any, object()),
            step_context=cast(Any, object()),
            raise_on_failure=True,
        )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(var_token)
    assert result == (None, None)


# ---------------------------------------------------------------------------
# Effect-entry retry consult (codex round-37) — U-RT-141 lease rider
# ---------------------------------------------------------------------------


def test_tripped_token_stops_new_retry_attempt_within_step() -> None:
    """The per-attempt retry loop consults the token before any new
    provider attempt (mutation probe: step-boundary-only checking lets
    another paid attempt begin and fails). Witnessed at the consult
    contract: a tripped ambient token raises BEFORE the attempt body."""
    token = DispatchCancelToken()
    token.trip()
    var_token = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            ambient = DISPATCH_CANCEL_TOKEN_VAR.get()
            assert ambient is not None
            ambient.check()  # the exact consult the retry loop performs
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(var_token)
    # Source pin (the consult sits inside the per-attempt loop, before the
    # attempt span/body — not only at step boundaries).
    from pathlib import Path

    import harness_runtime.lifecycle.retry_breaker_fallback as rbf

    source = Path(cast(str, rbf.__file__)).read_text()
    loop_idx = source.index("for attempt in range(policy.max_attempts):")
    span_idx = source.index('"harness.runtime.retry_attempt"')
    check_idx = source.index("_cancel_token.check()")
    assert loop_idx < check_idx < span_idx


@pytest.mark.asyncio
async def test_draining_worker_retains_lease_until_fence_ack(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """U-RT-141 lease rider: a cap-full budget with one draining worker
    rejects a new admission until the drain completes, then admits
    (mutation probe: releasing on parent return passes an over-cap dispatch
    during drain and fails)."""
    import harness_runtime.lifecycle.sync_dispatcher_facade as facade_mod

    monkeypatch.setattr(facade_mod, "_AUDIT_DRAIN_GRACE_SECONDS", 0.1)
    executor = SubAgentDispatchExecutor(frame_budget=1)
    composer = _make_composer(
        inner=_SlowSyncInner(1.0), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    facade = materialize_sync_dispatcher_facade(cast(Any, composer), result_timeout_seconds=0.05)
    with pytest.raises(StepDispatchTimeoutError):
        await asyncio.to_thread(
            facade.dispatch, object(), _make_step(), step_context=_make_step_context()
        )
    # Parent has returned (timeout surfaced) but the worker still drains —
    # the frames stay LEASED: a new admission must fail.
    from harness_core import SubAgentDispatchCapacityError

    with pytest.raises(SubAgentDispatchCapacityError):
        executor.reserve(1, step_id="s-new", descent_chain=("s-new",))
    # After the worker terminates, the lease releases exactly-once.
    deadline = time.monotonic() + 3.0
    while executor.available_frames < 1 and time.monotonic() < deadline:
        await asyncio.sleep(0.02)
    assert executor.available_frames == 1
    executor.reserve(1, step_id="s-new", descent_chain=("s-new",)).release()

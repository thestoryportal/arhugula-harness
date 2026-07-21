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


def test_descendant_inflight_at_trip_bubbles_to_parent_ack() -> None:
    """B-48 correctness fix (out-of-family Codex [P1]) — a descendant's own
    effect-in-flight-at-trip must make the PARENT's ack ambiguous too, not
    only the descendant's. The parent itself has ZERO effects in flight; only
    the CHILD does. Cascading `parent.trip()` while the child holds an open
    `effect_entry()` must still resolve the PARENT's `wait_ack()` as
    ACKED_EFFECT_AMBIGUOUS — a grandchild's effect landing after its own trip
    is exactly as ambiguous to the operator as the parent's own effect would
    be.

    Mutation probe: reverting `trip()` to discard its children's return value
    (the pre-fix shape) leaves `parent._inflight_at_trip` at its own
    (`False`) reading — this test's assertion would then see ACKED_CLEAN.
    """
    parent = DispatchCancelToken()
    child = DispatchCancelToken(parent=parent)
    guard = child.effect_entry()
    guard.__enter__()  # child effect in flight; parent has NO effect in flight
    parent.trip()  # cascades to the child; child's own in-flight flag is True
    guard.__exit__(None, None, None)
    parent.ack()
    assert parent.wait_ack(grace_seconds=0.1) is FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS
    # The child's own ack independently reflects the same ambiguity.
    child.ack()
    assert child.wait_ack(grace_seconds=0.1) is FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS


def test_late_linked_child_inflight_at_trip_bubbles_to_already_tripped_parent() -> None:
    """The `_link_child` late-join cascade path (a token linked to an
    ALREADY-tripped ancestor) must ALSO bubble an in-flight-at-trip flag up
    — not only the main `trip()` cascade path. Exercises `_link_child`
    directly (deliberately, as a private-but-load-bearing correctness
    surface): a child with an open effect, linked into an already-tripped
    parent that itself has zero effects in flight.
    """
    parent = DispatchCancelToken()
    parent.trip()  # parent tripped with NO effects anywhere; starts clean
    child = DispatchCancelToken()
    with child.effect_entry():
        # Mutation probe: reverting `_link_child` to discard `child.trip()`'s
        # return value leaves `parent._inflight_at_trip` at its pre-existing
        # (`False`) reading regardless of what the newly-linked child reports.
        parent._link_child(child)  # exercising the internal cascade path directly
    parent.ack()
    assert parent.wait_ack(grace_seconds=0.1) is FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS


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
    """The per-attempt retry loop guards the REAL provider attempt with
    `effect_entry()` (B-48 fix, out-of-family Codex [P1]: a bare pre-attempt
    `check()` only proves the token wasn't tripped at that instant — it never
    marks the attempt in-flight, so a trip landing WHILE the paid call is
    genuinely running would leave the job's `wait_ack()` falsely reporting
    ACKED_CLEAN). Witnessed at the consult contract: a tripped ambient
    token's `effect_entry()` raises BEFORE the attempt body, same as
    `check()` did, but ALSO would have marked the attempt in-flight had it
    not been tripped already."""
    token = DispatchCancelToken()
    token.trip()
    var_token = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            ambient = DISPATCH_CANCEL_TOKEN_VAR.get()
            assert ambient is not None
            with ambient.effect_entry():  # the exact guard the retry loop uses
                pytest.fail("a new attempt began after the fence tripped")
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(var_token)
    # Source pin (the guard wraps the REAL provider call inside the
    # per-attempt loop, before the attempt span/body — not only at step
    # boundaries, and not a bare non-effect-tracking `check()`).
    from pathlib import Path

    import harness_runtime.lifecycle.retry_breaker_fallback as rbf

    source = Path(cast(str, rbf.__file__)).read_text()
    loop_idx = source.index("for attempt in range(policy.max_attempts):")
    span_idx = source.index('"harness.runtime.retry_attempt"')
    guard_idx = source.index("_cancel_token.effect_entry()")
    dispatch_idx = source.index("with _effect_guard:")
    assert loop_idx < guard_idx < span_idx < dispatch_idx


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


# ---------------------------------------------------------------------------
# BRANCH_CAPACITY_LEASE_VAR isolation at the offload boundary (round-6 codex
# [P1] #1) — exercised through the REAL `hitl_gate_composer.py` offload path
# (not the free-function-in-isolation shape the round-5b registry test used;
# closes the test-witness lens gap on that test).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_nested_sub_agent_dispatch_inside_offload_self_reserves_not_ancestor_lease() -> None:
    """A fan-out branch's own admitted `CapacityLease` (bound into
    `BRANCH_CAPACITY_LEASE_VAR` the way `_proceed_branch`/`_cancel_branch`
    do before dispatching) must NOT be visible to a NESTED SUB_AGENT_DISPATCH
    running inside that branch's already-offloaded job — `copy_context()`
    would otherwise carry it forward, and the nested dispatch would
    `bind_release_to_job()` the SAME lease a second time, releasing the
    ANCESTOR's frames when the nested (not the ancestor) job completes,
    while the ancestor job is still running — exceeding the shared
    occupied+N+S frame budget (Runtime spec v1.102 §14.8.10.1).

    Chained real facades (mirrors
    `test_parent_child_grandchild_cancellation_chain_fences_whole_descent`):
    the ancestor's inner calls the nested facade directly, both facades
    constructed up-front on this test's own event loop so the blocking
    inner call from a worker thread is safe.

    Also asserts, at this SAME real call site, that `_BRANCH_INFLIGHT_DISPATCHES`
    reads `None` (not a sentinel bound in this test's own ambient context)
    and `INTER_STEP_CHANNEL_VAR` reads a fresh channel (not the sentinel) —
    closing the test-witness lens's gap on the round-5b registry test, which
    only proved the free function's mechanism in isolation, never that it is
    wired into the real `hitl_gate_composer.py` offload call site.

    Mutation probe: deleting `BRANCH_CAPACITY_LEASE_VAR.set(None)` from
    `hitl_gate_composer.py`'s `_run_with_child_channel` makes
    `nested_lease_seen` capture the ancestor's own `CapacityLease` object
    instead of `None`, and `frames_during_nested` capture `2` instead of
    `1` (the nested dispatch never self-reserves — it silently reuses the
    ancestor's already-admitted frames instead)."""
    executor = SubAgentDispatchExecutor(frame_budget=4)

    from harness_runtime.lifecycle.inter_step_output_channel import (
        INTER_STEP_CHANNEL_VAR,
        InterStepOutputChannel,
    )

    frames_during_nested: list[int] = []

    class _NestedLeafInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            frames_during_nested.append(executor.available_frames)
            return {"level": "nested-leaf"}

    nested_composer = _make_composer(
        inner=_NestedLeafInner(), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    nested_facade = materialize_sync_dispatcher_facade(
        cast(Any, nested_composer), result_timeout_seconds=5.0
    )

    nested_lease_seen: list[Any] = []
    nested_inflight_registry_seen: list[Any] = []
    nested_inter_step_channel_seen: list[Any] = []

    class _NestedDispatchInner:
        """The ancestor job's own inner — performs a NESTED
        SUB_AGENT_DISPATCH from inside the ancestor's offloaded worker
        thread, the exact recursive shape codex's finding describes."""

        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            from harness_cp.sub_agent_dispatch_capacity_authority import (
                BRANCH_CAPACITY_LEASE_VAR,
            )
            from harness_cp.workflow_driver import _BRANCH_INFLIGHT_DISPATCHES

            nested_lease_seen.append(BRANCH_CAPACITY_LEASE_VAR.get())
            nested_inflight_registry_seen.append(_BRANCH_INFLIGHT_DISPATCHES.get())
            nested_inter_step_channel_seen.append(INTER_STEP_CHANNEL_VAR.get())
            return nested_facade.dispatch(
                binding, _make_step("step-nested"), step_context=step_context
            )

    ancestor_composer = _make_composer(
        inner=_NestedDispatchInner(), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    ancestor_facade = materialize_sync_dispatcher_facade(
        cast(Any, ancestor_composer), result_timeout_seconds=5.0
    )

    from harness_cp.sub_agent_dispatch_capacity_authority import BRANCH_CAPACITY_LEASE_VAR
    from harness_cp.workflow_driver import _BRANCH_INFLIGHT_DISPATCHES

    # Mirrors the fan-out's own atomic per-branch admission (2 frames, the
    # sync SUB_AGENT_DISPATCH branch charge per §14.8.10.1) before the CP
    # driver dispatches this branch — plus sentinels for the other two
    # contextvars this offload boundary must isolate.
    ancestor_lease = executor.reserve(
        2, step_id="ancestor-branch", descent_chain=("ancestor-branch",)
    )
    sentinel_registry_chain = (frozenset(),)
    sentinel_channel = InterStepOutputChannel()
    lease_token = BRANCH_CAPACITY_LEASE_VAR.set(ancestor_lease)
    registry_token = _BRANCH_INFLIGHT_DISPATCHES.set(sentinel_registry_chain)
    channel_token = INTER_STEP_CHANNEL_VAR.set(sentinel_channel)
    try:
        result = await asyncio.to_thread(
            ancestor_facade.dispatch,
            object(),
            _make_step("step-ancestor"),
            step_context=_make_step_context(),
        )
    finally:
        BRANCH_CAPACITY_LEASE_VAR.reset(lease_token)
        _BRANCH_INFLIGHT_DISPATCHES.reset(registry_token)
        INTER_STEP_CHANNEL_VAR.reset(channel_token)

    assert result == {"level": "nested-leaf"}
    assert nested_lease_seen == [None], (
        f"nested dispatch saw {nested_lease_seen[0]!r} instead of None — the "
        f"ancestor's lease leaked into the copied context instead of being "
        f"reset at the offload boundary"
    )
    assert nested_inflight_registry_seen == [None], (
        f"nested dispatch saw {nested_inflight_registry_seen[0]!r} instead "
        f"of None — the ancestor's own offload boundary did not reset "
        f"_BRANCH_INFLIGHT_DISPATCHES at the real hitl_gate_composer.py "
        f"call site"
    )
    assert nested_inter_step_channel_seen[0] is not sentinel_channel, (
        "nested dispatch saw the test's sentinel INTER_STEP_CHANNEL_VAR "
        "instead of a fresh per-job channel — the ancestor's own offload "
        "boundary did not rebind INTER_STEP_CHANNEL_VAR at the real "
        "hitl_gate_composer.py call site"
    )
    assert frames_during_nested == [1], (
        f"expected the nested dispatch to self-reserve its own frame "
        f"(available=1 while it runs: budget 4 - ancestor's 2 - nested's "
        f"own 1), got {frames_during_nested} — it likely reused the "
        f"ancestor's lease instead of reserving independently"
    )
    # Both jobs release exactly-once on their own completion (no leak,
    # regardless of which lease each bound to — this alone would NOT catch
    # the bug above, hence the two load-bearing assertions before it).
    deadline = time.monotonic() + 3.0
    while executor.available_frames < 4 and time.monotonic() < deadline:
        await asyncio.sleep(0.02)
    assert executor.available_frames == 4


# ---------------------------------------------------------------------------
# B-62 — per-effect fence granularity at the step-8 write phase (8b/8c/8d).
# ---------------------------------------------------------------------------


def test_b62_trip_during_8b_stops_8c_signing_and_8d_audit_append() -> None:
    """B-62: 8b (F2 append), 8c (signing — effect-bearing KMS call at MTC),
    and 8d (audit append) each enter their OWN `effect_entry()`. A trip
    landing WHILE 8b executes previously rode the single pre-trip guard
    into 8c + 8d; now 8c's fresh consult refuses before signing begins.
    The raised `DispatchFenceTrippedSignal` is a BaseException — neither
    `except AUDIT_SIGNING_HARD_FAILURES` nor `except Exception` in the
    method can absorb it."""
    from types import SimpleNamespace
    from typing import Any, cast

    import harness_runtime.lifecycle.sub_agent_dispatch as dispatch_mod
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_od.audit_ledger_types import SignatureAlgorithm
    from harness_runtime.lifecycle.sub_agent_dispatch import RuntimeSubAgentDispatcher

    token = DispatchCancelToken()
    converter_calls: list[object] = []
    audit_appends: list[object] = []

    class _TrippingLedgerWriter:
        def __init__(self) -> None:
            self.appends: list[Any] = []

        def append(self, payload: Any, key: Any) -> Any:
            self.appends.append((payload, key))
            token.trip()  # the trip lands while 8b executes
            return ("entry-hash", payload, key)

    def _recording_converter(*args: Any, **kwargs: Any) -> Any:
        converter_calls.append((args, kwargs))
        return SimpleNamespace()

    class _RecordingAuditWriter:
        def append(self, *, tenant_id: Any, audit_entry: Any) -> Any:
            audit_appends.append((tenant_id, audit_entry))
            return ("write-result", audit_entry)

    dispatcher = RuntimeSubAgentDispatcher.__new__(RuntimeSubAgentDispatcher)
    dispatcher.handoff_registry = cast(
        Any,
        SimpleNamespace(
            dispatch_response_hash=lambda _b: "0" * 64,
            compose_dispatch_audit=lambda **_k: SimpleNamespace(),
        ),
    )
    ledger = _TrippingLedgerWriter()
    dispatcher.ledger_writer = cast(Any, ledger)
    dispatcher.audit_writer = cast(Any, _RecordingAuditWriter())
    dispatcher.procedural_tier_snapshot_resolver = lambda: Identifier("b" * 64)
    dispatcher.audit_signing_key_id = "harness-runtime-test"
    dispatcher.audit_signing_algorithm = SignatureAlgorithm.ED25519
    dispatcher.signing_backend = None
    dispatcher.audit_signing_fail_closed = False

    payload = SimpleNamespace(brief=object(), child_workflow_id="child-wf")
    original_converter = dispatch_mod.cp_audit_to_od_audit
    dispatch_mod.cp_audit_to_od_audit = _recording_converter
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            dispatcher._compose_and_persist_audit(
                parent_action_id=cast(Any, "workflow:test-b62:step:0"),
                descent=SimpleNamespace(),
                payload=cast(Any, payload),
                step_context=_make_step_context(),
                raise_on_failure=True,
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)
        dispatch_mod.cp_audit_to_od_audit = original_converter

    # 8b's append executed (the trip raced it); 8c signing and 8d audit
    # append never BEGAN — the load-bearing per-effect refusal.
    assert len(ledger.appends) == 1
    assert converter_calls == []
    assert audit_appends == []
    # The raced 8b write reads AMBIGUOUS at the ack, never a false clean.
    token.ack()
    assert token.wait_ack(grace_seconds=0.1) is FenceAckOutcome.ACKED_EFFECT_AMBIGUOUS

"""U-RT-144 — pause/resume + selective execution-context riders (B-48).

Tests per Implementation_Plan_Harness_Runtime_v2_50.md §1.5 (PD-8
mutation-probed), Runtime-half witnesses: the REAL `SubAgentChildPausedError`
+ pause snapshot crossing the executor future INTACT (item 4); worker-set
pause flags visible to the resume path (item 4); parent-child span
continuity through the offload's context carry (item 5; mutation probe:
dropping the copy breaks parentage); per-child inter-step channel binding —
no cross-sibling output bleed (item 5; mutation probe: sharing the parent
channel fails). The parent-barrier/nested cascade-deadline witnesses ride
the CP fan-out gating suite (the CP halves at plan v2.39 U-CP-85/86); the
B-39 sequencing witness is CP-owned.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Mapping
from typing import Any, cast

import pytest
from harness_cp.workflow_driver_types import SubAgentChildPausedError
from harness_runtime.lifecycle.hitl_gate_composer import InnerDispatchMode
from harness_runtime.lifecycle.inter_step_output_channel import (
    INTER_STEP_CHANNEL_VAR,
    InterStepOutputChannel,
)
from harness_runtime.lifecycle.sub_agent_dispatch_executor import (
    SubAgentDispatchExecutor,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)


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
    *, inner: Any, executor: SubAgentDispatchExecutor, tracer_provider: Any = None
) -> Any:
    from harness_cp.hitl_placement import HITLPlacementKind
    from harness_is.state_ledger_entry_schema import Identifier
    from harness_od.audit_ledger_types import SignatureAlgorithm
    from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer

    return RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({HITLPlacementKind.SUB_AGENT_BOUNDARY}),
        ask_user_question_surface=cast(Any, object()),
        ledger_writer=cast(Any, object()),
        audit_writer=cast(Any, object()),
        tracer_provider=tracer_provider or TracerProvider(),
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        inner_dispatch_mode=InnerDispatchMode.OFFLOAD_SYNC,
        dispatch_executor=executor,
    )


@pytest.mark.asyncio
async def test_real_sub_agent_child_paused_error_and_snapshot_cross_executor_future_intact() -> (
    None
):
    """Item 4 — the REAL carrier: `SubAgentChildPausedError` + the child's
    pause SNAPSHOT cross the executor future INTACT (mutation probe:
    dropping the snapshot across the future boundary fails). A synthetic
    signal or worker-set flag would exercise a path production never takes."""
    from harness_cp.pause_resume_protocol_types import (
        PauseSnapshot,
        StateSummary,
        WorkflowPauseReason,
    )
    from harness_is.state_ledger_entry_schema import Identifier

    executor = SubAgentDispatchExecutor(frame_budget=4)
    snapshot = PauseSnapshot(
        workflow_id="wf-child-7",
        run_id="run-child-7",
        step_index=2,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="child paused at nested durable-HITL gate",
            summary_hash="0" * 64,
            idempotency_key=Identifier("k-child-7"),
            external_references=(),
        ),
        snapshot_hash="a" * 64,
        created_at=1_700_000_000_000,
        state_ledger_anchor="b" * 64,
    )

    class _PausingInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            _ = (binding, step, step_context)
            raise SubAgentChildPausedError(child_workflow_id="wf-child-7", child_snapshot=snapshot)

    composer = _make_composer(inner=_PausingInner(), executor=executor)
    with pytest.raises(SubAgentChildPausedError) as excinfo:
        await composer._dispatch_inner(object(), _make_step(), step_context=_make_step_context())
    crossed = excinfo.value
    # The REAL carrier's fields cross INTACT — same snapshot object identity
    # is not required, but full equality (incl. the 8-field envelope) is.
    assert crossed.child_workflow_id == "wf-child-7"
    assert crossed.child_snapshot == snapshot


@pytest.mark.asyncio
async def test_worker_set_pause_flag_visible_to_resume_path() -> None:
    """Item 4 — durable-async pause flags set FROM the worker thread are
    visible to the loop-side resume path (no thread-local state)."""
    executor = SubAgentDispatchExecutor(frame_budget=4)
    loop = asyncio.get_running_loop()
    pause_flag = asyncio.Event()

    class _FlagSettingInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            _ = (binding, step, step_context)
            # The worker cannot call asyncio.Event.set() directly (not
            # thread-safe) — the §14.8.8.1 surface routes through the loop.
            loop.call_soon_threadsafe(pause_flag.set)
            return {"paused_signalled": True}

    composer = _make_composer(inner=_FlagSettingInner(), executor=executor)
    await composer._dispatch_inner(object(), _make_step(), step_context=_make_step_context())
    await asyncio.wait_for(pause_flag.wait(), timeout=2.0)
    assert pause_flag.is_set()


@pytest.mark.asyncio
async def test_ack_fires_when_job_cancelled_before_worker_starts() -> None:
    """B-48 (codex round-4 [P2] "acknowledge executor jobs canceled before
    starting"): ack ownership is deferred to the job (`defer_ack_to_job()`),
    but if the returned future is cancelled BEFORE the worker ever calls
    `set_running_or_notify_cancel()` successfully, `_job` never runs — its
    own `finally: cancel_token.ack()` never fires. Without the done-callback
    fix, `wait_ack()` would wait out the full grace period and misreport
    `worker_draining_under_fence` even though nothing was ever active."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        FenceAckOutcome,
    )

    class _NeverCalledInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            raise AssertionError("dispatch must never run — future was pre-cancelled")

    class _PreCancelledFutureExecutor:
        """Delegates admission to a real executor; `submit()` returns an
        ALREADY-CANCELLED future so `set_running_or_notify_cancel()` is
        guaranteed to see it cancelled — deterministic, no timing race."""

        def __init__(self, real: SubAgentDispatchExecutor) -> None:
            self._real = real

        def reserve(self, *args: Any, **kwargs: Any) -> Any:
            return self._real.reserve(*args, **kwargs)

        def submit(self, fn: Any) -> Any:
            from concurrent.futures import Future

            future: Future[Any] = Future()
            future.cancel()
            assert future.cancelled()
            return future

    real_executor = SubAgentDispatchExecutor(frame_budget=4)
    fake_executor = _PreCancelledFutureExecutor(real_executor)
    composer = _make_composer(inner=_NeverCalledInner(), executor=cast(Any, fake_executor))

    token = DispatchCancelToken()
    reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(asyncio.CancelledError):
            await composer._dispatch_inner(
                object(), _make_step(), step_context=_make_step_context()
            )
    finally:
        DISPATCH_CANCEL_TOKEN_VAR.reset(reset)

    # A short grace suffices — the ack must already have fired via the
    # done-callback, not the (never-run) `_job`'s own finally.
    outcome = token.wait_ack(grace_seconds=0.2)
    assert outcome is not FenceAckOutcome.UNACKED_DRAINING


@pytest.mark.asyncio
async def test_submit_failure_releases_own_lease_not_leaked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-48 (codex round-4 [P2] "roll back submission when worker creation
    fails"): if `executor.submit()` itself raises (e.g. the OS refuses a
    new thread), the offload venue's own single-frame reservation (no
    ambient `BRANCH_CAPACITY_LEASE_VAR` — a standalone SUB_AGENT_DISPATCH,
    not a fan-out branch) must still be released — `add_done_callback`
    never attaches since `submit()` never returned a future."""

    class _NeverCalledInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            raise AssertionError("dispatch must never run — submit() failed first")

    executor = SubAgentDispatchExecutor(frame_budget=4)

    def _submit_raises(fn: Any) -> Any:
        raise RuntimeError("can't start new thread (simulated OS refusal)")

    monkeypatch.setattr(executor, "submit", _submit_raises)
    composer = _make_composer(inner=_NeverCalledInner(), executor=executor)
    with pytest.raises(RuntimeError, match="can't start new thread"):
        await composer._dispatch_inner(object(), _make_step(), step_context=_make_step_context())
    assert executor.available_frames == executor.frame_budget


@pytest.mark.asyncio
async def test_parent_child_span_id_continuity_through_offload() -> None:
    """Item 5 — the offload carries `contextvars.copy_context()` for trace
    continuity: a span started inside the worker parents to the loop-side
    span (mutation probe: dropping the context copy orphans the child)."""
    from opentelemetry import trace as otel_trace

    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("u-rt-144")
    executor = SubAgentDispatchExecutor(frame_budget=4)

    class _SpanningInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            _ = (binding, step, step_context)
            with tracer.start_as_current_span("child-span"):
                return {"ok": True}

    composer = _make_composer(inner=_SpanningInner(), executor=executor, tracer_provider=provider)
    with tracer.start_as_current_span("parent-span") as parent_span:
        await composer._dispatch_inner(object(), _make_step(), step_context=_make_step_context())
        parent_span_id = parent_span.get_span_context().span_id
        _ = otel_trace  # namespace kept for clarity
    spans = {s.name: s for s in exporter.get_finished_spans()}
    child = spans["child-span"]
    assert child.parent is not None
    assert child.parent.span_id == parent_span_id


@pytest.mark.asyncio
async def test_sibling_children_channel_isolation_no_cross_child_output() -> None:
    """Item 5 — PER-CHILD inter-step channel: two concurrent sibling children
    each see a FRESH channel; one sibling's step output never enters the
    other's `most_recent_output()`, and the parent channel stays unpolluted
    (mutation probe: sharing the copied parent channel fails)."""
    executor = SubAgentDispatchExecutor(frame_budget=8)
    parent_channel = InterStepOutputChannel()
    reset_token = INTER_STEP_CHANNEL_VAR.set(parent_channel)
    barrier = threading.Barrier(2)
    observed: dict[str, Mapping[str, Any] | None] = {}
    observed_lock = threading.Lock()

    class _ChannelUsingInner:
        def __init__(self, tag: str) -> None:
            self._tag = tag

        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            _ = (binding, step, step_context)
            channel = INTER_STEP_CHANNEL_VAR.get()
            assert channel is not None
            channel.record(f"step-{self._tag}", {"from": self._tag})
            barrier.wait(timeout=5)  # both siblings mid-flight together
            with observed_lock:
                observed[self._tag] = channel.most_recent_output()
            return {"tag": self._tag}

    try:
        composer_a = _make_composer(inner=_ChannelUsingInner("a"), executor=executor)
        composer_b = _make_composer(inner=_ChannelUsingInner("b"), executor=executor)
        step_context = _make_step_context()
        await asyncio.gather(
            composer_a._dispatch_inner(object(), _make_step("step-a"), step_context=step_context),
            composer_b._dispatch_inner(object(), _make_step("step-b"), step_context=step_context),
        )
    finally:
        INTER_STEP_CHANNEL_VAR.reset(reset_token)
    assert observed["a"] == {"from": "a"}  # never sibling b's output
    assert observed["b"] == {"from": "b"}
    assert parent_channel.most_recent_output() is None  # parent unpolluted


@pytest.mark.asyncio
async def test_bind_release_to_job_already_released_aborts_before_submit() -> None:
    """Concurrency-lens finding (round 3): `SyncDispatcherFacade.dispatch()`'s
    own `result_timeout_seconds` bound can release this branch's lease (the
    CP branch's `finally` calling `release_unless_job_bound()`) BEFORE this
    cooperatively-cancelled loop-side task reaches `bind_release_to_job()` —
    a bare `future.cancel()` only requests cancellation at the next await
    point, so the offload-setup code between awaits can still run after the
    facade already gave up. Mutation probe: reverting `bind_release_to_job`
    to the bare `self._job_bound = True` write (dropping the `_released`
    check) would let this scenario silently proceed to `executor.submit()`,
    running new work against a lease the CP side already returned to the
    budget — undercounting the shared frame budget for the job's whole
    lifetime. This test asserts `executor.submit()` is never reached and the
    standard fence signal is raised instead."""
    from harness_cp.sub_agent_dispatch_cancellation import (
        DISPATCH_CANCEL_TOKEN_VAR,
        DispatchCancelToken,
        DispatchFenceTrippedSignal,
    )
    from harness_cp.sub_agent_dispatch_capacity_authority import (
        BRANCH_CAPACITY_LEASE_VAR,
        DefaultCapacityAuthority,
    )

    class _NeverCalledInner:
        def dispatch(self, binding: Any, step: Any, *, step_context: Any) -> Mapping[str, Any]:
            raise AssertionError("dispatch must never run — lease already released")

    class _SubmitTrackingExecutor:
        """Delegates admission to a real executor; `submit()` fails the test
        outright — the fix must abort BEFORE reaching submit at all."""

        def __init__(self, real: SubAgentDispatchExecutor) -> None:
            self._real = real

        def reserve(self, *args: Any, **kwargs: Any) -> Any:
            return self._real.reserve(*args, **kwargs)

        def submit(self, fn: Any) -> Any:
            raise AssertionError("submit must never be called — the bind reported release")

    real_executor = SubAgentDispatchExecutor(frame_budget=4)
    fake_executor = _SubmitTrackingExecutor(real_executor)
    composer = _make_composer(inner=_NeverCalledInner(), executor=cast(Any, fake_executor))

    authority = DefaultCapacityAuthority(frame_budget=4)
    branch_lease = authority.reserve(1, step_id="branch-0", descent_chain=("branch-0",))
    # Simulate the facade's own timeout path: the CP branch already gave up
    # and released the lease via `release_unless_job_bound()` before this
    # loop-side task reached the offload-setup code.
    assert branch_lease.release_unless_job_bound() is True

    token = DispatchCancelToken()
    token.trip()  # the facade's timeout handler always trips before releasing
    lease_reset = BRANCH_CAPACITY_LEASE_VAR.set(branch_lease)
    token_reset = DISPATCH_CANCEL_TOKEN_VAR.set(token)
    try:
        with pytest.raises(DispatchFenceTrippedSignal):
            await composer._dispatch_inner(
                object(), _make_step(), step_context=_make_step_context()
            )
    finally:
        BRANCH_CAPACITY_LEASE_VAR.reset(lease_reset)
        DISPATCH_CANCEL_TOKEN_VAR.reset(token_reset)

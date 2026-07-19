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

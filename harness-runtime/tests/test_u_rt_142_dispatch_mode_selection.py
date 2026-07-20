"""U-RT-142 — construction-time dispatch-mode selection witnesses (B-48).

Tests per Implementation_Plan_Harness_Runtime_v2_50.md §1.3 (PD-8
mutation-probed): the three §14.8.10.2 stage-5 rows select their venue at
CONSTRUCTION (sync inner submitted to the executor worker; async inners keep
the direct await path — mutation probe: reverting to post-call discovery
runs the sync inner ON the loop and fails the venue assertion); filing §4
item 8-bis — a pending loop timer demonstrably advances during a slow
offloaded dispatch (with the DIRECT_AWAIT control showing the pre-B-48
defect shape); filing §4 item 3 — the parent→child→grandchild chain bridges
from worker threads with the parent awaiting off-loop, each descent level a
separate executor job under the ONE shared budget.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Mapping
from typing import Any, cast

import pytest
from harness_cp.hitl_placement import HITLPlacementKind
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import (
    Actor,
    ActorClass,
    Identifier,
)
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.lifecycle.hitl_gate_composer import (
    InnerDispatchMode,
    RuntimeHITLGateComposer,
)
from harness_runtime.lifecycle.sub_agent_dispatch_executor import (
    DISPATCH_WORKER_THREAD_NAME_PREFIX,
    SubAgentDispatchExecutor,
)
from harness_runtime.lifecycle.sync_dispatcher_facade import (
    materialize_sync_dispatcher_facade,
)
from opentelemetry.sdk.trace import TracerProvider

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id=Identifier("test-agent"))


def _make_step(step_id: str = "step-0") -> WorkflowStep:
    from harness_core import StepID

    return WorkflowStep(
        step_id=StepID(step_id), step_kind=StepKind.SUB_AGENT_DISPATCH, step_payload={}
    )


def _make_step_context() -> StepExecutionContext:
    from harness_as.sandbox_tier import SandboxTier
    from harness_core import ActionID
    from harness_cp.gate_level_rule import GateLevel

    return StepExecutionContext(
        workflow_id="test",
        parent_action_id=ActionID("workflow:test:step:0"),
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key=Identifier("test-idempotency-key"),
        tenant_id=None,
        step_index=0,
        hitl_placements=(),
    )


class _ThreadRecordingSyncInner:
    """Sync C-RT-17-shaped inner recording its executing thread's name."""

    def __init__(self, *, delay_seconds: float = 0.0) -> None:
        self.thread_names: list[str] = []
        self._delay = delay_seconds

    def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        _ = (binding, step, step_context)
        self.thread_names.append(threading.current_thread().name)
        if self._delay:
            time.sleep(self._delay)
        return {"venue": threading.current_thread().name}


class _ThreadRecordingAsyncInner:
    """Async C-RT-15-shaped inner recording its executing thread's name."""

    def __init__(self) -> None:
        self.thread_names: list[str] = []

    async def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        _ = (binding, step, step_context)
        self.thread_names.append(threading.current_thread().name)
        return {"venue": threading.current_thread().name}


def _make_composer(
    *,
    inner: Any,
    mode: InnerDispatchMode = InnerDispatchMode.DIRECT_AWAIT,
    executor: SubAgentDispatchExecutor | None = None,
    placement: HITLPlacementKind = HITLPlacementKind.SUB_AGENT_BOUNDARY,
) -> RuntimeHITLGateComposer:
    return RuntimeHITLGateComposer(
        inner=inner,
        applicable_placements=frozenset({placement}),
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


@pytest.mark.asyncio
async def test_all_three_stage5_constructions_select_mode_at_construction() -> None:
    """§14.8.10.2 rows: sync inner SUBMITTED to a worker; async inners stay
    on the loop. Mutation probe: post-call discovery runs the sync inner on
    the loop thread and the worker-name assertion fails."""
    executor = SubAgentDispatchExecutor(frame_budget=8)
    loop_thread = threading.current_thread().name

    # Row 2 — hitl_sub_agent shape: sync inner, OFFLOAD_SYNC.
    sync_inner = _ThreadRecordingSyncInner()
    offloaded = _make_composer(
        inner=sync_inner, mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    result = await offloaded._dispatch_inner(
        object(), _make_step(), step_context=_make_step_context()
    )
    assert str(result["venue"]).startswith(DISPATCH_WORKER_THREAD_NAME_PREFIX)
    assert sync_inner.thread_names[0] != loop_thread

    # Rows 1/3 — hitl_inference / hitl_tool shape: async inner, DIRECT_AWAIT.
    for _row in ("hitl_inference", "hitl_tool"):
        async_inner = _ThreadRecordingAsyncInner()
        direct = _make_composer(
            inner=async_inner,
            mode=InnerDispatchMode.DIRECT_AWAIT,
            placement=HITLPlacementKind.PRE_ACTION,
        )
        result = await direct._dispatch_inner(
            object(), _make_step(), step_context=_make_step_context()
        )
        assert result["venue"] == loop_thread  # never a worker thread


def test_stage5_source_binds_offload_mode_to_sub_agent_construction_only() -> None:
    """Construction-site pin: stage 5 passes OFFLOAD_SYNC exactly once (the
    hitl_sub_agent construction) — the two async composers keep the
    DIRECT_AWAIT default. Complements the behavior witness above; the full
    production-path proof is the promoted ollama anchor (filing §4 item 8)."""
    from pathlib import Path

    import harness_runtime.bootstrap.stage_5_loop_init as stage5

    source = Path(cast(str, stage5.__file__)).read_text()
    assert source.count("inner_dispatch_mode=InnerDispatchMode.OFFLOAD_SYNC") == 1


@pytest.mark.asyncio
async def test_unrelated_workflow_and_loop_timer_advance_during_slow_offloaded_dispatch() -> None:
    """Filing §4 item 8-bis — the PRIMARY defect's own proof: a pending loop
    timer fires WHILE a slow sync dispatch runs offloaded. Mutation probe
    (control): the same slow sync inner under DIRECT_AWAIT blocks the loop
    and the timer cannot fire during the dispatch."""
    executor = SubAgentDispatchExecutor(frame_budget=8)
    timer_fired_during_dispatch = asyncio.Event()

    async def unrelated_timer() -> None:
        await asyncio.sleep(0.05)
        timer_fired_during_dispatch.set()

    # Offloaded venue: the timer advances during the 0.4s dispatch.
    slow_inner = _ThreadRecordingSyncInner(delay_seconds=0.4)
    offloaded = _make_composer(
        inner=slow_inner, mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    timer_task = asyncio.get_running_loop().create_task(unrelated_timer())
    await offloaded._dispatch_inner(object(), _make_step(), step_context=_make_step_context())
    assert timer_fired_during_dispatch.is_set()  # fired DURING the dispatch
    await timer_task

    # Control (the pre-B-48 defect shape): DIRECT_AWAIT of the sync inner
    # blocks the loop — the timer cannot fire until the dispatch returns.
    control_fired = asyncio.Event()

    async def control_timer() -> None:
        await asyncio.sleep(0.05)
        control_fired.set()

    direct = _make_composer(
        inner=_ThreadRecordingSyncInner(delay_seconds=0.4),
        mode=InnerDispatchMode.DIRECT_AWAIT,
    )
    control_task = asyncio.get_running_loop().create_task(control_timer())
    await direct._dispatch_inner(object(), _make_step(), step_context=_make_step_context())
    assert not control_fired.is_set()  # loop was blocked for the full dispatch
    await control_task


@pytest.mark.asyncio
async def test_parent_child_grandchild_chain_bridges_from_worker_threads_parent_off_loop() -> None:
    """Filing §4 item 3 — the full descent chain works: each level's sync
    inner bridges back to the main loop through the facade
    (`run_coroutine_threadsafe` from a WORKER thread) and each descent level
    runs as a SEPARATE executor job under the shared budget."""
    executor = SubAgentDispatchExecutor(frame_budget=8)
    level_threads: dict[str, str] = {}

    class _Leaf:
        def dispatch(
            self, binding: Any, step: WorkflowStep, *, step_context: Any
        ) -> Mapping[str, Any]:
            _ = (binding, step, step_context)
            level_threads["grandchild"] = threading.current_thread().name
            return {"level": "grandchild"}

    grandchild_composer = _make_composer(
        inner=_Leaf(), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    grandchild_facade = materialize_sync_dispatcher_facade(
        cast(Any, grandchild_composer), result_timeout_seconds=10.0
    )

    class _Mid:
        def dispatch(
            self, binding: Any, step: WorkflowStep, *, step_context: Any
        ) -> Mapping[str, Any]:
            level_threads["child"] = threading.current_thread().name
            # The sync child dispatches its OWN sub-agent through the facade —
            # a worker-thread loop-bridge, exactly the production descent shape.
            return grandchild_facade.dispatch(
                binding, _make_step("step-grandchild"), step_context=step_context
            )

    child_composer = _make_composer(
        inner=_Mid(), mode=InnerDispatchMode.OFFLOAD_SYNC, executor=executor
    )
    child_facade = materialize_sync_dispatcher_facade(
        cast(Any, child_composer), result_timeout_seconds=10.0
    )

    # Parent awaits OFF-LOOP: dispatch through the top facade from a plain
    # thread (the CP driver's asyncio.to_thread shape).
    result = await asyncio.to_thread(
        child_facade.dispatch,
        object(),
        _make_step("step-child"),
        step_context=_make_step_context(),
    )
    assert result == {"level": "grandchild"}
    assert level_threads["child"].startswith(DISPATCH_WORKER_THREAD_NAME_PREFIX)
    assert level_threads["grandchild"].startswith(DISPATCH_WORKER_THREAD_NAME_PREFIX)
    assert level_threads["child"] != level_threads["grandchild"]  # separate jobs

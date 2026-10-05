"""Terminal gate faults keep pre-effect identity and post-effect replay safety.

The real CP driver, sync facade, retry wrapper, dispatcher and tool loop run.
Only the provider and operator boundary are scripted; installed HITL is separate.
Excluding post-effect HITL from the fence or wrapping before effects breaks these
identity and CP fail-class witnesses.
"""

from __future__ import annotations

import asyncio
from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import ProviderCandidate
from harness_cp.gate_level_rule import GateLevel
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus
from harness_runtime.lifecycle.hitl_gate_composer import HITLGateTimeoutError
from harness_runtime.lifecycle.hitl_tool_loop import HITLToolCallAssessment
from harness_runtime.lifecycle.post_tool_effect import PostToolEffectError
from harness_runtime.lifecycle.state_ledger import materialize_state_ledger_reader
from harness_runtime.lifecycle.sync_dispatcher_facade import materialize_sync_dispatcher_facade
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from .integration.test_b165_driver_through_composer_round_trip import _Ctx, _manifest, _Registry
from .test_post_tool_effect_cell10 import _transitions
from .test_post_tool_effect_replay import _first_tool_turn, _provider_case, _Tools


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
@pytest.mark.parametrize("after_effect", [False, True], ids=["pre-effect", "post-effect"])
@pytest.mark.parametrize("provider", ["anthropic", "ollama"])
async def test_terminal_hitl_identity_and_cp_fail_class_depend_on_prior_effect(
    tmp_path: Path, provider: str, after_effect: bool, half_open: bool
) -> None:
    fault = HITLGateTimeoutError("scripted operator timeout")
    tools = _Tools()
    script = [_first_tool_turn(provider) for _ in range(1 + int(after_effect))]
    attempts, wrapper, breaker, step = _provider_case(tmp_path, provider, script, tools)
    original_loop = attempts.inner.hitl_tool_loop
    assert original_loop is not None
    assessments: list[str] = []

    def assess(call: Any, context: Any) -> HITLToolCallAssessment:
        assessments.append(call.tool)
        level = GateLevel.AUTO if after_effect and len(assessments) == 1 else GateLevel.ASK
        return HITLToolCallAssessment(level, "mcp-main")

    class OperatorTimeout:
        calls = 0

        async def decide(self, **kwargs: Any) -> Any:
            self.calls += 1
            raise fault

    operator = OperatorTimeout()
    attempts.inner = replace(
        attempts.inner, hitl_tool_loop=replace(original_loop, assess=assess, gate=operator)
    )
    primary = wrapper.fallback_chain.primary
    wrapper.fallback_chain = wrapper.fallback_chain.model_copy(
        update={
            "same_family": (
                ProviderCandidate(provider=provider, model="backup", family=primary.family),
            ),
        }
    )
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    before_count = breaker.fail_count
    exporter = InMemorySpanExporter()
    wrapper.tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    observed: list[Exception] = []

    class ObserveFailure:
        async def dispatch(self, *args: Any, **kwargs: Any) -> Any:
            try:
                return await wrapper.dispatch(*args, **kwargs)
            except Exception as exc:
                observed.append(exc)
                raise

    # [LAW:behavior-not-structure] CP composes the context and records the actual
    # exception delivered through the production sync bridge.
    facade = materialize_sync_dispatcher_facade(ObserveFailure(), result_timeout_seconds=30.0)
    manifest = _manifest().model_copy(
        update={
            "fallback_chain": wrapper.fallback_chain,
            "hitl_placements": (),
            "topology_pattern": TopologyPattern.SINGLE_THREADED_LINEAR,
        }
    )
    ctx = _Ctx()
    ctx.ledger_writer = original_loop.wiring.ledger_writer
    ctx.ledger_reader = materialize_state_ledger_reader(ctx.ledger_writer)
    result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=manifest,
            steps=[step],
            run_id="terminal-hitl-cp",
            ctx=ctx,
            default_model_binding=ModelBinding(provider=provider, model="m"),
            step_dispatchers=_Registry(facade),
        )
    )

    assert result.status is RunStatus.FAILED
    assert len(observed) == 1
    raised = observed[0]
    if after_effect:
        assert isinstance(raised, PostToolEffectError)
        assert raised.fault is raised.__cause__ is fault
        assert raised.origin.value == "non-provider"
        assert "PostToolEffectError" in result.fail_class
        assert "RT-FAIL-HITL-GATE-TIMEOUT" not in result.fail_class
    else:
        assert raised is fault
        assert "RT-FAIL-HITL-GATE-TIMEOUT" in result.fail_class
    assert (len(tools.calls), len(attempts.calls), operator.calls) == (int(after_effect), 1, 1)
    assert attempts.calls[0].model_binding.model == "m"
    assert breaker.fail_count == before_count
    if half_open:
        assert breaker.state.value == "open"
        assert breaker.opened_at is not None and breaker.opened_at > 0.0
        assert _transitions(exporter) == [("open", "half_open", 0), ("half_open", "open", 0)]
    else:
        assert breaker.state.value == "closed"

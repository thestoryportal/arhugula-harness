"""B-EFFECT-FENCE (runtime spec §14.22 C-RT-31) — at-most-once execution tests.

Proves the durable effect fence is NON-VACUOUS (the live trap this workspace
keeps re-hitting — a wired-but-production-dead surface, cf. B-TOOL-GATE #653):

  * `RuntimeEffectFence` mechanics — first claim wins, any re-claim loses, and the
    claim is DURABLE across a fresh instance (a restarted process — the genuine
    crash-then-resume witness).
  * The real `RuntimeToolDispatcher` sink fail-closes a re-dispatch of the same
    effect, firing the underlying tool body EXACTLY ONCE across two dispatches
    with the same per-(run, step, tool) idempotency key (the key the driver
    recomputes byte-identically on a resume re-dispatch of an uncommitted step).
  * The NEGATIVE CONTROL: without the fence, the same two dispatches double-fire
    the tool — the window `_determine_resume_at` cannot close on its own (the
    prefix-skip protects only COMMITTED steps; the effect fires at
    `workflow_driver.py:2031`, the per-step ledger commit lands at `:2336`, so a
    crash in between re-dispatches the effected-but-uncommitted step).
  * The fresh-dispatcher-over-the-same-fence-dir test is the genuine no-proxy
    crash-then-resume proof: a SECOND dispatcher instance (a restarted process)
    re-dispatching the same effect fail-closes against the on-disk claim.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_core import PersonaTier
from harness_cp.cp_shared_types import MCPTrustTier, ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.mcp_client_namespace_emitter import (
    MCPClientNamespaceEmitter,
    MCPServerInfo,
)
from harness_cp.per_server_trust_evaluator import PerServerTrustEvaluator
from harness_cp.per_server_trust_types import TierDerivationRule, TrustPolicy
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.effect_fence import (
    EffectFenceReservedUncommittedError,
    RuntimeEffectFence,
)
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    RuntimeToolDispatcher,
    SandboxDispatchDecision,
)
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session

# ---------- fence-unit tests -----------------------------------------------


def test_try_reserve_first_wins_second_loses(tmp_path: Path) -> None:
    fence = RuntimeEffectFence(fence_dir=tmp_path / "fence")
    assert fence.try_reserve("effect-key-1") is True  # fresh → won → fire
    assert fence.try_reserve("effect-key-1") is False  # re-claim → lost → fail-close


def test_try_reserve_distinct_keys_independent(tmp_path: Path) -> None:
    """Run-scoping (finding O-E3b-1): a different run derives a different
    idempotency key → a disjoint claim namespace, so a fresh run of the same
    workflow is never falsely fenced by a prior run's claims."""
    fence = RuntimeEffectFence(fence_dir=tmp_path / "fence")
    assert fence.try_reserve("run-A:step-0:tool") is True
    assert fence.try_reserve("run-B:step-0:tool") is True  # distinct key → won
    assert fence.try_reserve("run-A:step-0:tool") is False  # the run-A claim persists


def test_fresh_fence_instance_sees_prior_claim(tmp_path: Path) -> None:
    """Crash-survival: the claim is on disk, so a NEW fence instance over the same
    directory (a restarted process) loses the re-claim — the durability the
    at-most-once guarantee rests on."""
    fence_dir = tmp_path / "fence"
    assert RuntimeEffectFence(fence_dir=fence_dir).try_reserve("k") is True
    # Simulate a process restart: a brand-new instance over the same directory.
    assert RuntimeEffectFence(fence_dir=fence_dir).try_reserve("k") is False


# ---------- real-dispatcher sink fixtures ----------------------------------


def _counting_server(fired: list[str]) -> FastMCP:
    server = FastMCP(name="dispatcher-test-srv")

    @server.tool(description="non-idempotent side effect")
    def do_effect(message: str) -> str:
        fired.append(message)  # the genuine effect — counts every real fire
        return f"did: {message}"

    return server


def _session_factory(server: FastMCP):
    @asynccontextmanager
    async def factory():
        async with create_connected_server_and_client_session(
            server, raise_exceptions=True
        ) as session:
            yield session

    return factory


def _tool_converter(tool):
    return ToolContract(
        name=tool.name,
        description=tool.description or "",
        input_schema=tool.inputSchema or {"type": "object"},
        output_schema={"type": "object"},
        minimum_tier=SandboxTier.TIER_1_PROCESS,
        blast_radius_tier=BlastRadiusTier.READ_ONLY,
    )


async def _build_started_counting_host(fired: list[str]) -> MCPClientHost:
    host = MCPClientHost(
        transport="stdio",
        server_name="dispatcher-test-srv",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={"command": "unused"},
        tool_contract_converter=_tool_converter,
        session_context_factory=_session_factory(_counting_server(fired)),
        auth_present=False,
    )
    await host.start()
    return host


def _emitter() -> MCPClientNamespaceEmitter:
    def lookup(_server_name: str) -> MCPServerInfo:
        return MCPServerInfo(
            transport="stdio",
            protocol_version="2025-06-18",
            auth_present=False,
            trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        )

    return MCPClientNamespaceEmitter(info_lookup=lookup)


def _sandbox_resolver(_contract, _step):
    return SandboxDispatchDecision(
        tier=SandboxTier.TIER_1_PROCESS,
        tech="host",
        provider="host",
        assigned_tier_reason="test",
        cost_tier_overhead_ms=1,
    )


def _trust_policy() -> TrustPolicy:
    return TrustPolicy(
        default_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        require_audit_below_tier=MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT,
        allow_list=frozenset({"dispatcher-test-srv"}),
        deny_list=frozenset(),
        per_server_overrides={},
        tier_derivation=TierDerivationRule.CONSERVATIVE,
    )


def _dispatcher(host: MCPClientHost, fence: RuntimeEffectFence | None) -> RuntimeToolDispatcher:
    return RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_emitter(),
        trust_policy=_trust_policy(),
        sandbox_decision_resolver=_sandbox_resolver,
        effect_fence=fence,
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="wf-1",
        parent_action_id="workflow:wf-1:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.OPERATOR, actor_id="harness-runtime"),
        parent_entry_hash="",
        # The run-scoped per-step key the driver computes at `:1985`
        # (`_compute_step_idempotency_key(run_idempotency_key, step_index)`),
        # byte-identical across a fresh run and its resume re-dispatch.
        parent_idempotency_key="run-1:step-0",
        tenant_id=None,
        step_index=0,
    )


def _binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-1",
        model_binding=ModelBinding(provider="anthropic", model="claude-opus-4-7"),
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step() -> WorkflowStep:
    return WorkflowStep(
        step_id="step-1",
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": "do_effect", "tool_args": {"message": "fire"}},
    )


# ---------- real-dispatcher sink tests -------------------------------------


@pytest.mark.asyncio
async def test_dispatcher_fences_redispatch_at_most_once(tmp_path: Path) -> None:
    """With the fence, a re-dispatch of the same effect fail-closes — the tool
    body fires EXACTLY ONCE across two dispatches with the same idempotency key."""
    fired: list[str] = []
    fence = RuntimeEffectFence(fence_dir=tmp_path / "fence")
    host = await _build_started_counting_host(fired)
    dispatcher = _dispatcher(host, fence)
    try:
        result = await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
        assert result["tool_id"] == "do_effect"  # first dispatch fired
        # The resume re-dispatch (same key) — the effect MAY already have fired,
        # so the fence fail-closes rather than risk a double-execution.
        with pytest.raises(EffectFenceReservedUncommittedError):
            await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    finally:
        await host.shutdown()
    assert fired == ["fire"]  # at-most-once — the second dispatch never fired


@pytest.mark.asyncio
async def test_dispatcher_without_fence_double_fires(tmp_path: Path) -> None:
    """NEGATIVE CONTROL: without the fence the same two dispatches BOTH fire — the
    crash-between-effect-and-commit window is real and unguarded. Proves the fence
    is load-bearing (this test fails-to-double-fire only because no fence is bound)."""
    fired: list[str] = []
    host = await _build_started_counting_host(fired)
    dispatcher = _dispatcher(host, fence=None)
    try:
        await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
        await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    finally:
        await host.shutdown()
    assert fired == ["fire", "fire"]  # DOUBLE-FIRE — the gap the fence closes


@pytest.mark.asyncio
async def test_dispatcher_fence_survives_process_restart(tmp_path: Path) -> None:
    """No-proxy crash-then-resume: a SECOND dispatcher instance (a restarted
    process) over the SAME on-disk fence directory re-dispatching the same effect
    fail-closes against the durable claim — the effect fires once across the crash."""
    fence_dir = tmp_path / "fence"
    fired: list[str] = []

    host1 = await _build_started_counting_host(fired)
    dispatcher1 = _dispatcher(host1, RuntimeEffectFence(fence_dir=fence_dir))
    try:
        await dispatcher1.dispatch(_binding(), _step(), step_context=_step_context())
    finally:
        await host1.shutdown()

    # Restart: a brand-new dispatcher + fence instance over the same directory.
    host2 = await _build_started_counting_host(fired)
    dispatcher2 = _dispatcher(host2, RuntimeEffectFence(fence_dir=fence_dir))
    try:
        with pytest.raises(EffectFenceReservedUncommittedError):
            await dispatcher2.dispatch(_binding(), _step(), step_context=_step_context())
    finally:
        await host2.shutdown()

    assert fired == ["fire"]  # at-most-once across the process restart

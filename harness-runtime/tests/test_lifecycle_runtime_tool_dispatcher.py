"""U-RT-67 — `RuntimeToolDispatcher.dispatch()` body + sandbox span emission.

Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-67 (5 ACs):
1. Dispatch resolves ToolContract; raises RT-FAIL-TOOL-CONTRACT-UNKNOWN on miss
2. Per-server-trust evaluation invoked; raises RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION on deny
3. sandbox.* 7-attribute namespace emitted on sandbox.enter per C-AS-15 §15
4. mcp.* 7-attribute namespace emitted on mcp.tool.call per C-AS-14 §14.3
5. Schema validation both directions; raises RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION on breach
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from harness_core import PersonaTier
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.mcp_client_namespace_emitter import (
    MCPClientNamespaceEmitter,
    MCPServerInfo,
)
from harness_cp.per_server_trust_evaluator import PerServerTrustEvaluator
from harness_cp.per_server_trust_types import (
    TierDerivationRule,
    TrustPolicy,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_is.state_ledger_entry_schema import Actor, ActorClass

from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    MCPHostUnreachableError,
    RuntimeToolDispatcher,
    SandboxDispatchDecision,
    SandboxTierFloorViolationError,
    ToolContractUnknownError,
    ToolInvocationProtocolError,
    ToolInvocationSchemaViolationError,
    ToolInvocationTimeoutError,
    ToolInvocationTrustViolationError,
)


# ---------- fixtures + helpers ---------------------------------------------


def _build_fastmcp_server(register_echo: bool = True) -> FastMCP:
    server = FastMCP(name="dispatcher-test-srv")
    if register_echo:

        @server.tool(description="echo")
        def echo(message: str) -> str:
            return f"echoed: {message}"

    return server


def _build_session_factory(server: FastMCP):
    @asynccontextmanager
    async def factory():
        async with create_connected_server_and_client_session(
            server, raise_exceptions=True
        ) as session:
            yield session

    return factory


def _make_tool_converter():
    def convert(tool):
        return ToolContract(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object"},
            output_schema={"type": "object"},  # empty → no validation
            minimum_tier=SandboxTier.TIER_1_PROCESS,
            blast_radius_tier=BlastRadiusTier.READ_ONLY,
        )

    return convert


async def _build_started_host(register_echo: bool = True) -> MCPClientHost:
    server = _build_fastmcp_server(register_echo=register_echo)
    host = MCPClientHost(
        transport="stdio",
        server_name="dispatcher-test-srv",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={"command": "unused"},
        tool_contract_converter=_make_tool_converter(),
        session_context_factory=_build_session_factory(server),
        auth_present=False,
    )
    await host.start()
    return host


def _make_step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="wf-1",
        parent_action_id="workflow:wf-1:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.OPERATOR, actor_id="harness-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="run-idem-key-abc",
        tenant_id=None,
        step_index=0,
    )


def _make_step(tool_id: str, tool_args: dict | None = None) -> WorkflowStep:
    return WorkflowStep(
        step_id="step-1",
        step_kind=StepKind.TOOL_STEP,
        step_payload={"tool_id": tool_id, "tool_args": tool_args or {}},
    )


def _make_binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-1",
        model_binding=ModelBinding(provider="anthropic", model="claude-opus-4-7"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _make_trust_policy(*, deny: list[str] | None = None) -> TrustPolicy:
    return TrustPolicy(
        default_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        require_audit_below_tier=MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT,
        # Explicitly allow the test server so unknown-server-tier-floor
        # doesn't fire under CONSERVATIVE; deny_list still takes precedence
        # per spec §27.6 inv 3.
        allow_list=frozenset({"dispatcher-test-srv"}),
        deny_list=frozenset(deny or []),
        per_server_overrides={},
        tier_derivation=TierDerivationRule.CONSERVATIVE,
    )


def _make_emitter() -> MCPClientNamespaceEmitter:
    def lookup(_server_name: str) -> MCPServerInfo:
        return MCPServerInfo(
            transport="stdio",
            protocol_version="2025-06-18",
            auth_present=False,
            trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        )

    return MCPClientNamespaceEmitter(info_lookup=lookup)


def _good_sandbox_resolver(_contract, _step):
    return SandboxDispatchDecision(
        tier=SandboxTier.TIER_2_CONTAINER,
        tech="linux-namespaces",
        provider="container-d",
        assigned_tier_reason="default-from-test",
        cost_tier_overhead_ms=120,
    )


def _low_tier_sandbox_resolver(_contract, _step):
    """Resolves below the contract's TIER_1 floor — never used unless
    contract is TIER_2+."""
    return SandboxDispatchDecision(
        tier=SandboxTier.TIER_1_PROCESS,
        tech="host",
        provider="host",
        assigned_tier_reason="tier-1-pinned",
        cost_tier_overhead_ms=10,
    )


# ---------- AC #1 — tool-contract resolution + unknown failure -------------


@pytest.mark.asyncio
async def test_dispatch_unknown_tool_id_raises_contract_unknown() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
    )
    try:
        with pytest.raises(ToolContractUnknownError, match="not-registered"):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("not-registered"),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()


@pytest.mark.asyncio
async def test_dispatch_missing_tool_id_in_payload_raises() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
    )
    try:
        step = WorkflowStep(
            step_id="step-x",
            step_kind=StepKind.TOOL_STEP,
            step_payload={},  # no tool_id
        )
        with pytest.raises(ToolContractUnknownError, match="missing or non-str"):
            await dispatcher.dispatch(_make_binding(), step, step_context=_make_step_context())
    finally:
        await host.shutdown()


# ---------- AC #2 — trust violation ----------------------------------------


@pytest.mark.asyncio
async def test_dispatch_trust_violation_raises() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(deny=["dispatcher-test-srv"]),
        sandbox_decision_resolver=_good_sandbox_resolver,
    )
    try:
        with pytest.raises(ToolInvocationTrustViolationError, match="explicit_deny|EXPLICIT_DENY"):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "hi"}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()


# ---------- AC #3+4 — sandbox.* + mcp.* span emission ----------------------


@pytest.mark.asyncio
async def test_dispatch_emits_sandbox_and_mcp_spans() -> None:
    host = await _build_started_host()
    # Wire up an in-memory OTel exporter.
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        tracer_provider=provider,
    )
    try:
        result = await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "spans!"}),
            step_context=_make_step_context(),
        )
        assert result["tool_id"] == "echo"
        spans = exporter.get_finished_spans()
        names = {span.name for span in spans}
        assert "tool.dispatch" in names
        assert "sandbox.enter" in names
        assert "mcp.tool.call" in names
        assert "sandbox.exit" in names

        # sandbox.enter span carries the 7-attribute set (minus
        # sandbox.tier_escalation event which is conditional).
        sandbox_enter = next(s for s in spans if s.name == "sandbox.enter")
        attrs = dict(sandbox_enter.attributes or {})
        assert attrs["sandbox.tier"] == "tier-2-container"
        assert attrs["sandbox.tech"] == "linux-namespaces"
        assert attrs["sandbox.provider"] == "container-d"
        assert attrs["sandbox.policy.assigned_tier_reason"] == "default-from-test"
        assert attrs["sandbox.cost.tier_overhead_ms"] == 120
        assert "sandbox.fail.class" in attrs

        # mcp.tool.call span carries the 7-attribute mcp.* namespace.
        mcp_call = next(s for s in spans if s.name == "mcp.tool.call")
        mcp_attrs = dict(mcp_call.attributes or {})
        assert mcp_attrs["mcp.server.name"] == "dispatcher-test-srv"
        assert mcp_attrs["mcp.server.trust_tier"] == "level-2-sandbox-all"
        assert mcp_attrs["mcp.protocol_version"] == "2025-06-18"
        assert mcp_attrs["mcp.transport"] == "stdio"
        assert mcp_attrs["mcp.auth_present"] is False
        assert mcp_attrs["mcp.primitive.kind"] == "tool"
        assert isinstance(mcp_attrs["mcp.primitive.signature.sha256"], str)
        assert len(mcp_attrs["mcp.primitive.signature.sha256"]) == 64
    finally:
        await host.shutdown()


# ---------- AC #5 — schema violation ---------------------------------------


@pytest.mark.asyncio
async def test_dispatch_schema_violation_raises() -> None:
    """Output schema validation fires on mismatch."""
    server = _build_fastmcp_server()

    def strict_converter(tool):
        return ToolContract(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object"},
            # Strict output schema — require a "must_be_present" field.
            output_schema={
                "type": "object",
                "required": ["must_be_present"],
                "properties": {"must_be_present": {"type": "string"}},
            },
            minimum_tier=SandboxTier.TIER_1_PROCESS,
            blast_radius_tier=BlastRadiusTier.READ_ONLY,
        )

    host = MCPClientHost(
        transport="stdio",
        server_name="dispatcher-test-srv",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={"command": "unused"},
        tool_contract_converter=strict_converter,
        session_context_factory=_build_session_factory(server),
    )
    await host.start()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
    )
    try:
        with pytest.raises(ToolInvocationSchemaViolationError, match="output_schema validation"):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "x"}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()


# ---------- tier-floor violation -------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_tier_floor_violation_raises() -> None:
    """When the resolved tier is below contract.minimum_tier, raise."""
    server = _build_fastmcp_server()

    def high_floor_converter(tool):
        return ToolContract(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object"},
            output_schema={},
            minimum_tier=SandboxTier.TIER_3_MICROVM,  # high floor
            blast_radius_tier=BlastRadiusTier.EXTERNAL_REVERSIBLE,
        )

    host = MCPClientHost(
        transport="stdio",
        server_name="dispatcher-test-srv",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={"command": "unused"},
        tool_contract_converter=high_floor_converter,
        session_context_factory=_build_session_factory(server),
    )
    await host.start()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_low_tier_sandbox_resolver,  # tier 1 < tier 3
    )
    try:
        with pytest.raises(
            SandboxTierFloorViolationError,
            match="tier_3_microvm|tier-3-microvm",
        ):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "x"}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()


# ---------- happy path: end-to-end --------------------------------------


@pytest.mark.asyncio
async def test_dispatch_happy_path_returns_step_output() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
    )
    try:
        result = await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "hello"}),
            step_context=_make_step_context(),
        )
        assert result["tool_id"] == "echo"
        assert result["sandbox_tier"] == "tier-2-container"
        # TrustDecisionReason values are snake_case; both default + explicit
        # allow are permitted outcomes.
        assert result["trust_decision_reason"] in {
            "default_allow",
            "explicit_allow",
        }
        # Idempotency key is deterministic over (parent_key, step_id, tool_id).
        assert isinstance(result["idempotency_key"], str)
        assert len(result["idempotency_key"]) == 64  # sha256 hex
    finally:
        await host.shutdown()


# ---------- default sandbox resolver loud-on-misconfig ---------------------


@pytest.mark.asyncio
async def test_default_sandbox_resolver_raises() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        # NOT passing sandbox_decision_resolver — should hit default.
    )
    try:
        with pytest.raises(LookupError, match="default SandboxDecisionResolver"):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "x"}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()


# ---------- AS spec v1.6 §15.9 dual-attribute emission discipline ---------


def _otel_setup() -> tuple[InMemorySpanExporter, TracerProvider]:
    """Standalone in-memory OTel exporter + provider for dispatcher tests."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter, provider


async def _dispatch_with_failing_call_tool(
    exc: Exception,
) -> tuple[InMemorySpanExporter, Exception]:
    """Build a real fastmcp-backed dispatcher, then patch host.call_tool to
    raise `exc` post-MCP-span-open. Returns the OTel exporter + the
    raised exception for caller assertions."""
    host = await _build_started_host()

    async def _failing_call_tool(*_args, **_kwargs):
        raise exc

    # Patch the bound method on this host instance.
    host.call_tool = _failing_call_tool  # type: ignore[method-assign]

    exporter, provider = _otel_setup()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        tracer_provider=provider,
    )
    raised: Exception | None = None
    try:
        try:
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "x"}),
                step_context=_make_step_context(),
            )
        except Exception as e:
            raised = e
    finally:
        await host.shutdown()
    assert raised is not None
    return exporter, raised


def _violation_attrs(exporter: InMemorySpanExporter) -> dict[str, object]:
    spans = exporter.get_finished_spans()
    violation = next((s for s in spans if s.name == "sandbox.violation"), None)
    assert violation is not None, (
        f"expected sandbox.violation span, got names={[s.name for s in spans]}"
    )
    return dict(violation.attributes or {})


@pytest.mark.asyncio
async def test_dispatch_transport_failure_emits_sandbox_violation_dual_attrs() -> None:
    """§15.9 row 2 — MCPHostUnreachableError → mcp.fail.class=transport;
    projected sandbox.fail.class=exit_nonzero per §15.10 row 1."""
    exporter, raised = await _dispatch_with_failing_call_tool(
        MCPHostUnreachableError("host unreachable")
    )
    assert isinstance(raised, MCPHostUnreachableError)
    attrs = _violation_attrs(exporter)
    assert attrs["mcp.fail.class"] == "transport"
    assert attrs["sandbox.fail.class"] == "exit_nonzero"
    # AS spec v1.6 §15.6 row 1: sandbox.violation carries parent idempotency_key
    idem = attrs.get("idempotency_key")
    assert isinstance(idem, str) and len(idem) == 64  # sha256 hex


@pytest.mark.asyncio
async def test_dispatch_protocol_error_emits_sandbox_violation_dual_attrs() -> None:
    """ToolInvocationProtocolError → mcp.fail.class=protocol_error;
    projected sandbox.fail.class=exit_nonzero per §15.10 row 2."""
    exporter, raised = await _dispatch_with_failing_call_tool(
        ToolInvocationProtocolError("malformed")
    )
    assert isinstance(raised, ToolInvocationProtocolError)
    attrs = _violation_attrs(exporter)
    assert attrs["mcp.fail.class"] == "protocol_error"
    assert attrs["sandbox.fail.class"] == "exit_nonzero"
    idem = attrs.get("idempotency_key")
    assert isinstance(idem, str) and len(idem) == 64


@pytest.mark.asyncio
async def test_dispatch_timeout_emits_sandbox_violation_dual_attrs() -> None:
    """§15.9 row 4 — ToolInvocationTimeoutError → mcp.fail.class=timeout;
    projected sandbox.fail.class=timeout per §15.10 row 4 (value-name parity)."""
    exporter, raised = await _dispatch_with_failing_call_tool(
        ToolInvocationTimeoutError("call timed out")
    )
    assert isinstance(raised, ToolInvocationTimeoutError)
    attrs = _violation_attrs(exporter)
    assert attrs["mcp.fail.class"] == "timeout"
    assert attrs["sandbox.fail.class"] == "timeout"
    idem = attrs.get("idempotency_key")
    assert isinstance(idem, str) and len(idem) == 64


@pytest.mark.asyncio
async def test_dispatch_schema_violation_emits_sandbox_violation_dual_attrs() -> None:
    """§15.9 row 3 — jsonschema.ValidationError → mcp.fail.class=schema_violation;
    projected sandbox.fail.class=policy_override per §15.10 row 3 (HIGH stretch).

    Uses a real fastmcp server with strict output schema that the echo
    response will fail (the dispatcher catches `jsonschema.ValidationError`
    inside its own `_validate_response_schema` step).
    """
    server = _build_fastmcp_server()

    def strict_converter(tool):
        return ToolContract(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object"},
            output_schema={
                "type": "object",
                "required": ["must_be_present"],
                "properties": {"must_be_present": {"type": "string"}},
            },
            minimum_tier=SandboxTier.TIER_1_PROCESS,
            blast_radius_tier=BlastRadiusTier.READ_ONLY,
        )

    host = MCPClientHost(
        transport="stdio",
        server_name="dispatcher-test-srv",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={"command": "unused"},
        tool_contract_converter=strict_converter,
        session_context_factory=_build_session_factory(server),
    )
    await host.start()
    exporter, provider = _otel_setup()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        tracer_provider=provider,
    )
    try:
        with pytest.raises(ToolInvocationSchemaViolationError):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "x"}),
                step_context=_make_step_context(),
            )
        attrs = _violation_attrs(exporter)
        assert attrs["mcp.fail.class"] == "schema_violation"
        assert attrs["sandbox.fail.class"] == "policy_override"
        idem = attrs.get("idempotency_key")
        assert isinstance(idem, str) and len(idem) == 64
    finally:
        await host.shutdown()


@pytest.mark.asyncio
async def test_dispatch_happy_path_emits_no_sandbox_violation() -> None:
    """Success path: sandbox.exit emits without a preceding sandbox.violation.

    Regression guard — the violation span only opens on the exception path
    per §15.9 emission discipline.
    """
    host = await _build_started_host()
    exporter, provider = _otel_setup()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        tracer_provider=provider,
    )
    try:
        await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "ok"}),
            step_context=_make_step_context(),
        )
        names = {s.name for s in exporter.get_finished_spans()}
        assert "sandbox.violation" not in names
        assert "sandbox.exit" in names
    finally:
        await host.shutdown()


@pytest.mark.asyncio
async def test_dispatch_sandbox_violation_idempotency_key_matches_parent_dispatch() -> None:
    """AS spec v1.6 §15.6 row 1 idempotency-key join — H_T-AS-5 retirement gate.

    The `sandbox.violation` event's `idempotency_key` MUST equal the value
    passed to the parent `mcp.tool.call` (`host.call_tool(..., key)`), so
    that cross-axis cost-attribution (D6) and engine event history (D1)
    can correlate the violation back to its parent dispatch.
    """
    host = await _build_started_host()
    captured: list[str] = []

    async def _capturing_failing_call_tool(_tool_id, _tool_args, key):
        captured.append(key)
        raise MCPHostUnreachableError("host unreachable")

    host.call_tool = _capturing_failing_call_tool  # type: ignore[method-assign]
    exporter, provider = _otel_setup()
    dispatcher = RuntimeToolDispatcher(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        tracer_provider=provider,
    )
    try:
        with pytest.raises(MCPHostUnreachableError):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "x"}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()
    assert len(captured) == 1
    attrs = _violation_attrs(exporter)
    assert attrs["idempotency_key"] == captured[0]

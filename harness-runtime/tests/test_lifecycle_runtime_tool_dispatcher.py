"""U-RT-67 — `RuntimeToolDispatcher.dispatch()` body + sandbox span emission.

Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-67 (5 ACs):
1. Dispatch resolves ToolContract; raises RT-FAIL-TOOL-CONTRACT-UNKNOWN on miss
2. Per-server-trust evaluation invoked; raises RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION on deny
3. sandbox.* 7-attribute namespace emitted on sandbox.enter per C-AS-15 §15
4. mcp.* 7-attribute namespace emitted on mcp.tool.call per C-AS-14 §14.3
5. Schema validation both directions; raises RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION on breach
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.secret_fail_class import SecretFailClass
from harness_as.secret_fetch import SecretRef, SecretScope
from harness_as.secret_fetch_audit import SecretFetchEvent, compose_secret_fetch_audit_entry
from harness_as.tool_contract import SecretAllowlistEntry, ToolContract
from harness_core import PersonaTier
from harness_cp.cp_shared_types import MCPTrustTier, ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
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
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_write import WriteResult
from harness_runtime.config.provider_secrets import SecretResolutionError
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    MCPHostUnreachableError,
    RuntimeToolDispatcher,
    SandboxDispatchDecision,
    SandboxTierFloorViolationError,
    ToolContractUnknownError,
    ToolExecutionDriver,
    ToolInvocationProtocolError,
    ToolInvocationSchemaViolationError,
    ToolInvocationTimeoutError,
    ToolInvocationTrustViolationError,
)
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
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


def _make_secret_tool_converter(*required_secrets: SecretAllowlistEntry):
    def convert(tool):
        return ToolContract(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object"},
            output_schema={"type": "object"},
            minimum_tier=SandboxTier.TIER_1_PROCESS,
            blast_radius_tier=BlastRadiusTier.READ_ONLY,
            required_secrets=required_secrets,
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


async def _build_started_secret_host(*required_secrets: SecretAllowlistEntry) -> MCPClientHost:
    server = _build_fastmcp_server(register_echo=True)
    host = MCPClientHost(
        transport="stdio",
        server_name="dispatcher-test-srv",
        trust_tier=MCPTrustTier.LEVEL_2_SANDBOX_ALL,
        transport_config={"command": "unused"},
        tool_contract_converter=_make_secret_tool_converter(*required_secrets),
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


class _InjectedExecutionDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[SandboxDispatchDecision, str, dict, str]] = []

    async def call_tool(
        self,
        *,
        mcp_client_host: MCPClientHost,
        sandbox_decision: SandboxDispatchDecision,
        tool_id: str,
        tool_args: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self.calls.append((sandbox_decision, tool_id, dict(tool_args), idempotency_key))
        return {
            "content": [{"type": "text", "text": f"driver:{tool_args['message']}"}],
            "isError": False,
            "structuredContent": {"provider": sandbox_decision.provider},
        }


@dataclass(frozen=True)
class _ResolvedSecretForAudit:
    ref: SecretRef
    secret_last_rotated_at: str
    backend: str = "test-secret-backend"
    cache_tier_overhead_ms: int = 7
    policy_access_decision_reason: str = "permitted"


class _MetadataSecretResolver:
    def __init__(self, *results: _ResolvedSecretForAudit) -> None:
        self._results = {result.ref.name: result for result in results}
        self.calls: list[tuple[str, SecretScope, SandboxTier, ToolContract | None]] = []

    def resolve_with_audit_metadata(
        self,
        name: str,
        scope: SecretScope,
        tier: SandboxTier,
        *,
        tool: ToolContract | None = None,
    ) -> _ResolvedSecretForAudit:
        self.calls.append((name, scope, tier, tool))
        return self._results[name]


class _FailingSecretResolver:
    def resolve_with_audit_metadata(
        self,
        name: str,
        scope: SecretScope,
        tier: SandboxTier,
        *,
        tool: ToolContract | None = None,
    ) -> _ResolvedSecretForAudit:
        _ = scope, tier, tool
        raise SecretResolutionError(SecretFailClass.SECRET_UNAVAILABLE, name)


class _CapturingSecretAuditEmitter:
    def __init__(self) -> None:
        self.events: list[SecretFetchEvent] = []

    def emit(self, event: SecretFetchEvent) -> WriteResult:
        self.events.append(event)
        return WriteResult.APPENDED


class _DedupSecretAuditEmitter:
    def __init__(self) -> None:
        self.events: list[SecretFetchEvent] = []
        self._seen_idempotency_keys: set[str] = set()

    def emit(self, event: SecretFetchEvent) -> WriteResult:
        entry = compose_secret_fetch_audit_entry(event, None)
        if entry.idempotency_key in self._seen_idempotency_keys:
            return WriteResult.IDEMPOTENT_NOOP
        self._seen_idempotency_keys.add(entry.idempotency_key)
        self.events.append(event)
        return WriteResult.APPENDED


# ---------- R-CXA-1 — workflow-time secret-fetch AS→IS producer ------------


@pytest.mark.asyncio
async def test_secret_fetch_producer_fires_at_workflow_step() -> None:
    """R-CXA-1: required_secrets resolve at TOOL_STEP time and emit AS→IS audit."""
    scope = SecretScope(name="prod")
    required = SecretAllowlistEntry(name="api-token", scope=scope)
    ref = SecretRef(name="api-token", scope=scope, tier=SandboxTier.TIER_2_CONTAINER)
    resolver = _MetadataSecretResolver(
        _ResolvedSecretForAudit(
            ref=ref,
            secret_last_rotated_at="2026-06-08T00:00:00+00:00",
        )
    )
    audit = _CapturingSecretAuditEmitter()
    host = await _build_started_secret_host(required)
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        provider_secret_resolver=resolver,
        secret_fetch_audit_emitter=audit.emit,
    )

    try:
        result = await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "secret"}),
            step_context=_make_step_context(),
        )
    finally:
        await host.shutdown()

    assert result["tool_id"] == "echo"
    assert len(resolver.calls) == 1
    name, resolved_scope, resolved_tier, tool = resolver.calls[0]
    assert name == "api-token"
    assert resolved_scope == scope
    assert resolved_tier is SandboxTier.TIER_2_CONTAINER
    assert tool is not None
    assert tool.required_secrets == (required,)

    assert len(audit.events) == 1
    event = audit.events[0]
    assert event.thread_id == "wf-1"
    assert event.step_id == "step-1"
    assert event.actor == _make_step_context().parent_actor
    assert event.secret_name == "api-token"
    assert event.secret_scope == scope
    assert event.secret_last_rotated_at == "2026-06-08T00:00:00+00:00"


@pytest.mark.asyncio
async def test_secret_fetch_event_fields_non_hollow() -> None:
    """R-CXA-1: rotation metadata changes the structure-not-content fingerprint."""
    scope = SecretScope(name="prod")
    required = SecretAllowlistEntry(name="api-token", scope=scope)
    audit = _CapturingSecretAuditEmitter()
    resolver = _MetadataSecretResolver(
        _ResolvedSecretForAudit(
            ref=SecretRef(
                name="api-token",
                scope=scope,
                tier=SandboxTier.TIER_2_CONTAINER,
            ),
            secret_last_rotated_at="2026-06-08T00:00:00+00:00",
        )
    )
    host = await _build_started_secret_host(required)
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        provider_secret_resolver=resolver,
        secret_fetch_audit_emitter=audit.emit,
    )

    try:
        await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "first"}),
            step_context=_make_step_context(),
        )
    finally:
        await host.shutdown()

    event = audit.events[0]
    assert event.secret_scope.name == "prod"
    assert event.secret_last_rotated_at != ""
    same_secret_rotated = event.model_copy(
        update={"secret_last_rotated_at": "2026-06-09T00:00:00+00:00"}
    )
    first_entry = compose_secret_fetch_audit_entry(event, None)
    second_entry = compose_secret_fetch_audit_entry(same_secret_rotated, None)
    assert first_entry.response_hash != second_entry.response_hash


@pytest.mark.asyncio
async def test_secret_fetch_replay_idempotent_noop() -> None:
    """R-CXA-1: replay of the same workflow-step secret fetch does not duplicate."""
    scope = SecretScope(name="prod")
    required = SecretAllowlistEntry(name="api-token", scope=scope)
    resolver = _MetadataSecretResolver(
        _ResolvedSecretForAudit(
            ref=SecretRef(
                name="api-token",
                scope=scope,
                tier=SandboxTier.TIER_2_CONTAINER,
            ),
            secret_last_rotated_at="2026-06-08T00:00:00+00:00",
        )
    )
    audit = _DedupSecretAuditEmitter()
    host = await _build_started_secret_host(required)
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        provider_secret_resolver=resolver,
        secret_fetch_audit_emitter=audit.emit,
    )

    try:
        for message in ("first", "replay"):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": message}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()

    assert len(resolver.calls) == 2
    assert len(audit.events) == 1


@pytest.mark.asyncio
async def test_secret_fetch_span_co_emitted() -> None:
    """R-CXA-1: successful fetch emits the structure-only secret.fetch span."""
    scope = SecretScope(name="prod")
    required = SecretAllowlistEntry(name="api-token", scope=scope)
    resolver = _MetadataSecretResolver(
        _ResolvedSecretForAudit(
            ref=SecretRef(
                name="api-token",
                scope=scope,
                tier=SandboxTier.TIER_2_CONTAINER,
            ),
            secret_last_rotated_at="2026-06-08T00:00:00+00:00",
            backend="gcp-secret-manager",
            cache_tier_overhead_ms=11,
            policy_access_decision_reason="permitted",
        )
    )
    audit = _CapturingSecretAuditEmitter()
    exporter, provider = _otel_setup()
    host = await _build_started_secret_host(required)
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        provider_secret_resolver=resolver,
        secret_fetch_audit_emitter=audit.emit,
        tracer_provider=provider,
    )

    try:
        await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "span"}),
            step_context=_make_step_context(),
        )
    finally:
        await host.shutdown()

    secret_span = next(s for s in exporter.get_finished_spans() if s.name == "secret.fetch")
    attrs = dict(secret_span.attributes or {})
    assert attrs["secret.name"] == "api-token"
    assert attrs["secret.scope"] == "prod"
    assert attrs["secret.backend"] == "gcp-secret-manager"
    assert attrs["secret.cache.tier_overhead_ms"] == 11
    assert attrs["secret.policy.access_decision_reason"] == "permitted"
    assert "secret.fail.class" not in attrs
    assert not any("sk-" in str(value) for value in attrs.values())


@pytest.mark.asyncio
async def test_failed_fetch_emits_fail_class() -> None:
    """R-CXA-1: failed fetch emits secret.fail.class on secret.fetch span."""
    scope = SecretScope(name="prod")
    required = SecretAllowlistEntry(name="api-token", scope=scope)
    exporter, provider = _otel_setup()
    host = await _build_started_secret_host(required)
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        provider_secret_resolver=_FailingSecretResolver(),
        secret_fetch_audit_emitter=_CapturingSecretAuditEmitter().emit,
        tracer_provider=provider,
    )

    try:
        with pytest.raises(SecretResolutionError):
            await dispatcher.dispatch(
                _make_binding(),
                _make_step("echo", {"message": "fail"}),
                step_context=_make_step_context(),
            )
    finally:
        await host.shutdown()

    secret_span = next(s for s in exporter.get_finished_spans() if s.name == "secret.fetch")
    attrs = dict(secret_span.attributes or {})
    assert attrs["secret.name"] == "api-token"
    assert attrs["secret.scope"] == "prod"
    assert attrs["secret.fail.class"] == "secret_unavailable"
    assert not any("sk-" in str(value) for value in attrs.values())


# ---------- AC #1 — tool-contract resolution + unknown failure -------------


@pytest.mark.asyncio
async def test_dispatch_unknown_tool_id_raises_contract_unknown() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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


@pytest.mark.asyncio
async def test_dispatch_uses_injected_tool_execution_driver() -> None:
    """R-410 seam: after sandbox decision resolution, execution is delegated
    to the configured driver instead of being hard-wired to MCPClientHost."""
    host = await _build_started_host()
    driver: ToolExecutionDriver = _InjectedExecutionDriver()
    dispatcher = RuntimeToolDispatcher.for_single_host(
        mcp_client_host=host,
        per_server_trust_evaluator=PerServerTrustEvaluator(),
        mcp_namespace_emitter=_make_emitter(),
        trust_policy=_make_trust_policy(),
        sandbox_decision_resolver=_good_sandbox_resolver,
        tool_execution_driver=driver,
    )
    try:
        result = await dispatcher.dispatch(
            _make_binding(),
            _make_step("echo", {"message": "via-driver"}),
            step_context=_make_step_context(),
        )
        response = result["response"]
        assert response["content"][0]["text"] == "driver:via-driver"

        assert isinstance(driver, _InjectedExecutionDriver)
        assert len(driver.calls) == 1
        sandbox_decision, tool_id, tool_args, idempotency_key = driver.calls[0]
        assert sandbox_decision.tier is SandboxTier.TIER_2_CONTAINER
        assert sandbox_decision.provider == "container-d"
        assert tool_id == "echo"
        assert tool_args == {"message": "via-driver"}
        assert isinstance(idempotency_key, str)
        assert len(idempotency_key) == 64
    finally:
        await host.shutdown()


# ---------- default sandbox resolver loud-on-misconfig ---------------------


@pytest.mark.asyncio
async def test_default_sandbox_resolver_raises() -> None:
    host = await _build_started_host()
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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
    dispatcher = RuntimeToolDispatcher.for_single_host(
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

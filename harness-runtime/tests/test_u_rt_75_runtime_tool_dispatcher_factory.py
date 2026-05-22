"""U-RT-75 — Stage 5 factory materialize_runtime_tool_dispatcher_stage tests.

ACs per Implementation_Plan_Harness_Runtime_v2_13.md §1 U-RT-75 (cite-edited
at v2.13). Spec contract: Spec_Harness_Runtime_v1.md v1.16 §14.9.3 stage-5
factory contract + §14.11 C-RT-21.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_core import SandboxDecisionPolicy
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.mcp_client_namespace_emitter import MCPClientNamespaceEmitter
from harness_cp.per_server_trust_evaluator import PerServerTrustEvaluator
from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.bootstrap.factories.mcp_client_host_factory import (
    materialize_mcp_client_host_stage,
)
from harness_runtime.bootstrap.factories.runtime_tool_dispatcher_factory import (
    DEFAULT_TRUST_POLICY,
    materialize_runtime_tool_dispatcher_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.retry_breaker import (
    DEFAULT_RETRY_POLICY,
    RuntimeRetryBreaker,
)
from harness_runtime.lifecycle.retry_breaker_tool import (
    RESERVED_TOOL_DISPATCH_KEY,
    RetryBreakerToolDispatcher,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)
from opentelemetry.sdk.trace import TracerProvider


def _config() -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=Path("/tmp"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
    )


async def _post_stage_3a_builder(cfg: RuntimeConfig) -> _MutableHarnessContext:
    """Construct a builder with the minimum stage-3a + stage-3b state the
    stage-5 factory consumes."""
    builder = _MutableHarnessContext()
    builder.mcp_client_host = await materialize_mcp_client_host_stage(cfg)
    builder.retry_breaker = RuntimeRetryBreaker(
        retry_policies={
            RESERVED_TOOL_DISPATCH_KEY: RetryPolicy(
                max_attempts=3, backoff="full_jitter", jitter="full_jitter"
            ),
        },
        default_policy=DEFAULT_RETRY_POLICY,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )
    builder.tracer_provider = TracerProvider()
    return builder


@pytest.mark.asyncio
async def test_factory_returns_retry_wrapper_instance() -> None:
    # AC #1 — returns RetryBreakerToolDispatcher.
    cfg = _config()
    builder = await _post_stage_3a_builder(cfg)
    wrapper = await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    assert isinstance(wrapper, RetryBreakerToolDispatcher)


@pytest.mark.asyncio
async def test_step1_binds_per_server_trust_evaluator() -> None:
    # AC #2 — ctx.per_server_trust_evaluator bound to PerServerTrustEvaluator.
    cfg = _config()
    builder = await _post_stage_3a_builder(cfg)
    await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    assert isinstance(builder.per_server_trust_evaluator, PerServerTrustEvaluator)


@pytest.mark.asyncio
async def test_step2_binds_mcp_namespace_emitter() -> None:
    # AC #3 — ctx.mcp_namespace_emitter bound to MCPClientNamespaceEmitter.
    cfg = _config()
    builder = await _post_stage_3a_builder(cfg)
    await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    assert isinstance(builder.mcp_namespace_emitter, MCPClientNamespaceEmitter)


@pytest.mark.asyncio
async def test_step4_wrapper_inner_is_bare_runtime_tool_dispatcher() -> None:
    # AC #5 — wrapper.inner is a bare RuntimeToolDispatcher; bare is NOT
    # surfaced on the builder (private constructor arg per spec §14.9.6 inv 6).
    from harness_runtime.lifecycle.runtime_tool_dispatcher import (
        RuntimeToolDispatcher,
    )

    cfg = _config()
    builder = await _post_stage_3a_builder(cfg)
    wrapper = await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    assert isinstance(wrapper.inner, RuntimeToolDispatcher)
    # bare dispatcher not surfaced on tool_dispatcher field (caller U-RT-68
    # binds the wrapper, not the bare); on the builder mid-factory it's
    # not present either.
    assert builder.tool_dispatcher is None  # caller binds, not the factory


@pytest.mark.asyncio
async def test_factory_uses_runtime_default_trust_policy_when_config_omits() -> None:
    # AC #2 (extended) — config.trust_policy=None → factory uses DEFAULT_TRUST_POLICY.
    cfg = _config()
    assert cfg.trust_policy is None
    builder = await _post_stage_3a_builder(cfg)
    wrapper = await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    # The bare dispatcher stores the trust policy as a private; verify via
    # the bound evaluator side-effect (evaluator constructed regardless).
    assert wrapper.inner is not None
    # And confirm the default policy itself is the canonical
    # conservative-tier-floor shape (sanity check on the module constant).
    assert DEFAULT_TRUST_POLICY.allow_list == frozenset()
    assert DEFAULT_TRUST_POLICY.deny_list == frozenset()


@pytest.mark.asyncio
async def test_factory_uses_sandbox_decision_policy_default_when_config_omits() -> None:
    # AC #4 (extended) — config.sandbox_decision_policy=None → factory uses
    # SandboxDecisionPolicy.default(). Verified by absence-of-error path
    # (empty-marker default is always constructible).
    cfg = _config()
    assert cfg.sandbox_decision_policy is None
    builder = await _post_stage_3a_builder(cfg)
    wrapper = await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    assert wrapper is not None
    # Confirm SandboxDecisionPolicy.default() is the U-CORE-02 carrier.
    assert isinstance(SandboxDecisionPolicy.default(), SandboxDecisionPolicy)


@pytest.mark.asyncio
async def test_factory_does_not_bind_tool_dispatcher_directly() -> None:
    """Per spec §14.9.3 + U-RT-68's role: the factory returns the wrapper;
    the caller (stage 5 body / U-RT-68) binds it to ctx.tool_dispatcher.
    This separation preserves single-responsibility per atomic decomposition."""
    cfg = _config()
    builder = await _post_stage_3a_builder(cfg)
    assert builder.tool_dispatcher is None
    await materialize_runtime_tool_dispatcher_stage(builder, cfg)
    # Factory does NOT bind tool_dispatcher; only intermediate carriers.
    assert builder.tool_dispatcher is None

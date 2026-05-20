"""U-RT-02 — `RuntimeConfig` + `HarnessContext` schema tests.

ACs per Phase 2 Session 3 plan v2.1 §2 L0:
- pyright-strict clean (verified out-of-band via `uv run pyright harness-runtime/`).
- `RuntimeConfig` round-trips.
- `HarnessContext` is frozen.
"""

from __future__ import annotations

from pathlib import Path

from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.types import (
    CollectorConfig,
    HarnessContext,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _make_runtime_config() -> RuntimeConfig:
    """Build a minimal `RuntimeConfig` with stub sub-configs.

    Sub-config validators (path existence, keyring allowlist) land at U-RT-04+
    per spec C-RT-03 'Deferred to implementation discretion' clause; at L0 the
    sub-configs are empty placeholders.
    """
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=Path("/tmp"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def test_runtime_config_round_trips() -> None:
    """`RuntimeConfig` survives `model_dump()` → `model_validate()` byte-equal."""
    original = _make_runtime_config()
    dumped = original.model_dump()
    rebuilt = RuntimeConfig.model_validate(dumped)
    assert rebuilt == original
    assert rebuilt.model_dump() == dumped


def test_runtime_config_is_frozen() -> None:
    """`RuntimeConfig` instances reject post-construction mutation per C-RT-03."""
    cfg = _make_runtime_config()
    # Pydantic v2 frozen models raise `ValidationError` on attribute set.
    try:
        cfg.tenant_id = "should-fail"  # type: ignore[misc]
    except Exception:
        pass
    else:
        raise AssertionError("RuntimeConfig accepted mutation; frozen invariant violated")


def test_runtime_config_rejects_unknown_keys() -> None:
    """`extra='forbid'` invariant per C-RT-03."""
    base = _make_runtime_config().model_dump()
    base["unknown_field"] = "should-fail"
    try:
        RuntimeConfig.model_validate(base)
    except Exception:
        pass
    else:
        raise AssertionError("RuntimeConfig accepted unknown field; extra='forbid' violated")


def test_runtime_config_mcp_clients_defaults_empty() -> None:
    """`mcp_clients` defaults to `[]` per C-RT-03 row 7."""
    cfg = _make_runtime_config()
    assert cfg.mcp_clients == []


def test_runtime_config_tenant_id_defaults_none() -> None:
    """`tenant_id` defaults to `None` per C-RT-03 row 9 (single-tenant mode)."""
    cfg = _make_runtime_config()
    assert cfg.tenant_id is None


def test_harness_context_is_frozen() -> None:
    """`HarnessContext.model_config['frozen']` is `True` per C-RT-04."""
    assert HarnessContext.model_config.get("frozen") is True


def test_harness_context_allows_arbitrary_types() -> None:
    """`HarnessContext` supports `arbitrary_types_allowed=True` per C-RT-04.

    Required so Protocol stubs + non-Pydantic axis types (PathResolver,
    WorktreeIsolationManager) compose into the frozen schema without coercion.
    """
    assert HarnessContext.model_config.get("arbitrary_types_allowed") is True


def test_harness_context_declares_all_c_rt_04_fields() -> None:
    """Every field enumerated at Spec_Harness_Runtime_v1.md v1.1 §4 is declared.

    Source: the C-RT-04 §4 table (`config`, stage 1 IS bundle, stage 2 AS
    bundle, stage 3a/3b CP bundles, stage 4 OD bundle, stage 5 LOOP_INIT
    bundle, `drained_flag`).
    """
    expected = {
        # Stage 0.
        "config",
        "drained_flag",
        # Stage 1 IS.
        "path_resolver",
        "worktree_manager",
        "shadow_git",
        "ledger_writer",
        "ledger_reader",  # v2.12 — read-view counterpart of ledger_writer
        "index",
        "cache",
        # Stage 2 AS.
        "skills",
        "tool_contracts",
        "mcp_host",
        "mcp_clients",
        "sandbox_dispatch",
        # Stage 3a CP_CLIENTS.
        "providers",
        # Stage 3b CP_ROUTING.
        "routing_manifest",
        "engine_selector",
        "fallback_chain",
        "retry_breaker",
        "hitl_registry",
        "handoff_registry",
        # Stage 4 OD.
        "tracer_provider",
        "collector_daemon",
        "cost_chain",
        "audit_writer",
        # Stage 5 LOOP_INIT.
        "override_evaluator",
        "topology_dispatcher",
        "lifecycle_emitter",
        "llm_dispatcher",  # U-RT-52 — C-RT-15 LLM-dispatch composer
        "sub_agent_dispatcher",  # U-RT-59 — C-RT-17 §14.7 sub-agent dispatch composer
        "step_dispatchers",  # U-RT-59 — C-RT-17 §14.7.1 + §14.7.7 step-kind routing registry
    }
    actual = set(HarnessContext.model_fields.keys())
    assert actual == expected, f"missing: {expected - actual}; extra: {actual - expected}"

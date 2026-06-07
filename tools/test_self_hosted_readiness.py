from __future__ import annotations

from pathlib import Path

from harness_as.secret_fetch import SecretScope
from harness_as.tool_contract import SecretAllowlistEntry
from harness_core import DeploymentSurface, PersonaTier
from harness_cp.topology_pattern import TopologyPattern
from harness_od.per_cell_collector_placement_matrix import CollectorPlacement
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

from tools.self_hosted_readiness import evaluate_config


def _allowlist_entry() -> SecretAllowlistEntry:
    return SecretAllowlistEntry(
        name="anthropic_key",
        scope=SecretScope(name="default"),
    )


def _config(
    tmp_path: Path,
    *,
    deployment_surface: DeploymentSurface = DeploymentSurface.SELF_HOSTED_SERVER,
    placement: CollectorPlacement = CollectorPlacement.SELF_HOSTED_BACKEND_COLLECTOR,
    provider_secrets: ProviderSecretsConfig | None = None,
) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=deployment_surface,
        repository_root=tmp_path,
        provider_secrets=provider_secrets
        or ProviderSecretsConfig(operator_allowlist=(_allowlist_entry(),)),
        otel=OTelConfig(otlp_endpoint="http://collector.internal:4317"),
        collector=CollectorConfig(placement=placement),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _checks_by_name(config: RuntimeConfig) -> dict[str, bool]:
    report = evaluate_config(config)
    return {check.name: check.ok for check in report.checks}


def test_self_hosted_config_surfaces_missing_tier_secret_backend(tmp_path: Path) -> None:
    """A plausible R-420 config passes static gates but still blocks on R-440."""
    report = evaluate_config(_config(tmp_path))

    assert report.ready is False
    checks = {check.name: check for check in report.checks}
    assert checks["deployment-surface"].ok is True
    assert checks["collector-placement"].ok is True
    assert checks["otlp-endpoint"].ok is True
    assert checks["provider-secret-allowlist"].ok is True
    assert checks["tier-secrets-backend"].ok is False
    assert "no tier-level backend selector" in checks["tier-secrets-backend"].detail


def test_local_development_surface_fails_r420_gate(tmp_path: Path) -> None:
    checks = _checks_by_name(
        _config(tmp_path, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT)
    )

    assert checks["deployment-surface"] is False


def test_in_process_collector_fails_real_self_hosted_collector_gate(tmp_path: Path) -> None:
    checks = _checks_by_name(_config(tmp_path, placement=CollectorPlacement.IN_PROCESS))

    assert checks["collector-placement"] is False


def test_empty_provider_secret_allowlist_fails_r440_precondition(tmp_path: Path) -> None:
    checks = _checks_by_name(
        _config(
            tmp_path,
            provider_secrets=ProviderSecretsConfig(operator_allowlist=()),
        )
    )

    assert checks["provider-secret-allowlist"] is False


def test_team_self_hosted_sidecar_collector_is_accepted(tmp_path: Path) -> None:
    config = _config(tmp_path, placement=CollectorPlacement.SIDECAR)
    config = config.model_copy(update={"persona_tier": PersonaTier.TEAM_BINDING})

    checks = _checks_by_name(config)

    assert checks["collector-placement"] is True

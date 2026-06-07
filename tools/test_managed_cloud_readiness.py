from __future__ import annotations

from pathlib import Path

from harness_core import DeploymentSurface, PersonaTier
from harness_cp.topology_pattern import TopologyPattern
from harness_od.per_cell_collector_placement_matrix import CollectorPlacement
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    ProviderSecretBackend,
    ProviderSecretsConfig,
    RuntimeConfig,
)

from tools.managed_cloud_readiness import (
    e2b_secret_allowlist_entry,
    evaluate_config,
    load_report,
)


def _config(
    tmp_path: Path,
    *,
    deployment_surface: DeploymentSurface = DeploymentSurface.MANAGED_CLOUD,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    placement: CollectorPlacement = CollectorPlacement.VENDOR_PIPELINE,
    otlp_endpoint: str = "https://collector.vendor.example/v1/traces",
    provider_secrets: ProviderSecretsConfig | None = None,
) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=deployment_surface,
        persona_tier=persona_tier,
        repository_root=tmp_path,
        provider_secrets=provider_secrets
        or ProviderSecretsConfig(operator_allowlist=(e2b_secret_allowlist_entry(),)),
        otel=OTelConfig(otlp_endpoint=otlp_endpoint),
        collector=CollectorConfig(placement=placement),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _checks_by_name(config: RuntimeConfig, *, hosted_sandbox_provider: str | None = None):
    report = evaluate_config(config, hosted_sandbox_provider=hosted_sandbox_provider)
    return {check.name: check for check in report.checks}


def test_managed_cloud_static_readiness_blocks_on_local_secret_backend(
    tmp_path: Path,
) -> None:
    report = evaluate_config(_config(tmp_path), hosted_sandbox_provider="e2b")

    checks = {check.name: check for check in report.checks}
    assert report.ready is False
    assert checks["deployment-surface"].ok is True
    assert checks["collector-placement"].ok is True
    assert checks["managed-otlp-endpoint"].ok is True
    assert checks["provider-secret-allowlist"].ok is True
    assert checks["hosted-sandbox-provider"].ok is True
    assert checks["cloud-secret-backend"].ok is False
    assert "local-keyring-env-fallback" in checks["cloud-secret-backend"].detail


def test_managed_cloud_static_readiness_passes_with_gcp_backend(tmp_path: Path) -> None:
    report = evaluate_config(
        _config(
            tmp_path,
            provider_secrets=ProviderSecretsConfig(
                backend=ProviderSecretBackend.GCP_SECRET_MANAGER,
                gcp_project_id="harness-test-project",
                operator_allowlist=(e2b_secret_allowlist_entry(),),
            ),
        ),
        hosted_sandbox_provider="e2b",
    )

    assert report.ready is True
    assert {check.name for check in report.checks if not check.ok} == set()


def test_local_development_surface_fails_r421_gate(tmp_path: Path) -> None:
    checks = _checks_by_name(
        _config(tmp_path, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT),
        hosted_sandbox_provider="e2b",
    )

    assert checks["deployment-surface"].ok is False


def test_loopback_otlp_endpoint_fails_managed_cloud_gate(tmp_path: Path) -> None:
    checks = _checks_by_name(
        _config(tmp_path, otlp_endpoint="http://127.0.0.1:4317"),
        hosted_sandbox_provider="e2b",
    )

    assert checks["managed-otlp-endpoint"].ok is False


def test_managed_cloud_collector_placement_uses_per_cell_matrix(tmp_path: Path) -> None:
    solo_checks = _checks_by_name(
        _config(tmp_path, persona_tier=PersonaTier.SOLO_DEVELOPER),
        hosted_sandbox_provider="e2b",
    )
    mtc_checks = _checks_by_name(
        _config(
            tmp_path,
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            placement=CollectorPlacement.VENDOR_MANAGED_COLLECTOR,
        ),
        hosted_sandbox_provider="e2b",
    )
    wrong_checks = _checks_by_name(
        _config(
            tmp_path,
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            placement=CollectorPlacement.VENDOR_PIPELINE,
        ),
        hosted_sandbox_provider="e2b",
    )

    assert solo_checks["collector-placement"].ok is True
    assert mtc_checks["collector-placement"].ok is True
    assert wrong_checks["collector-placement"].ok is False


def test_e2b_candidate_requires_named_allowlist_entry(tmp_path: Path) -> None:
    checks = _checks_by_name(
        _config(tmp_path, provider_secrets=ProviderSecretsConfig(operator_allowlist=())),
        hosted_sandbox_provider="e2b",
    )

    assert checks["provider-secret-allowlist"].ok is False
    assert checks["hosted-sandbox-provider"].ok is False
    assert "e2b-secret" in checks["hosted-sandbox-provider"].detail


def test_managed_cloud_readiness_loads_config_file(tmp_path: Path) -> None:
    config_file = tmp_path / "harness.managed-cloud.toml"
    config_file.write_text(
        f"""
[runtime]
deployment_surface = "managed-cloud"
repository_root = "{tmp_path}"
default_topology = "single-threaded-linear"

[runtime.otel]
otlp_endpoint = "https://collector.vendor.example/v1/traces"

[runtime.collector]
placement = "VENDOR_PIPELINE"

[runtime.provider_secrets]
backend = "gcp-secret-manager"
gcp_project_id = "harness-test-project"
keyring_service = "harness"

[[runtime.provider_secrets.operator_allowlist]]
name = "e2b-secret"
scope = {{ name = "r421-managed-cloud" }}
""".strip(),
        encoding="utf-8",
    )

    report = load_report(config_file, hosted_sandbox_provider="e2b")

    assert report.ready is True
    assert {check.name for check in report.checks if not check.ok} == set()

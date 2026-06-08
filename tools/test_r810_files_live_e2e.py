from __future__ import annotations

from pathlib import Path

import pytest
from harness_as.sandbox_tier import SandboxTier
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

from tools.r810_files_live_e2e import (
    R810LiveE2EError,
    _assert_managed_cloud_config,
    _response_text,
    _span_has_files_attrs,
    _wait_for_files_trace,
)


def _config(
    tmp_path: Path,
    *,
    deployment_surface: DeploymentSurface = DeploymentSurface.MANAGED_CLOUD,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    bootstrap_sandbox_tier: SandboxTier = SandboxTier.TIER_4_FULL_VM,
    otlp_endpoint: str = "https://collector.example.run.app",
) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=deployment_surface,
        persona_tier=persona_tier,
        repository_root=tmp_path,
        provider_secrets=ProviderSecretsConfig(
            backend=ProviderSecretBackend.GCP_SECRET_MANAGER,
            gcp_project_id="project-ba535aa4-f08d-46b2-ba6",
        ),
        otel=OTelConfig(otlp_endpoint=otlp_endpoint),
        collector=CollectorConfig(
            placement=CollectorPlacement.VENDOR_PIPELINE,
            bootstrap_sandbox_tier=bootstrap_sandbox_tier,
        ),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def test_assert_managed_cloud_config_accepts_r421_collector_shape(tmp_path: Path) -> None:
    _assert_managed_cloud_config(_config(tmp_path))


def test_assert_managed_cloud_config_rejects_non_managed_or_loopback(tmp_path: Path) -> None:
    for config in (
        _config(tmp_path, deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER),
        _config(tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE),
        _config(tmp_path, otlp_endpoint="http://127.0.0.1:4317"),
        _config(tmp_path, bootstrap_sandbox_tier=SandboxTier.TIER_1_PROCESS),
    ):
        with pytest.raises(R810LiveE2EError):
            _assert_managed_cloud_config(config)


def test_response_text_supports_sdk_objects_and_mappings() -> None:
    class Block:
        text = "ok"

    class Response:
        def __init__(self) -> None:
            self.content = [Block(), {"text": "-dict"}]

    assert _response_text(Response()) == "ok-dict"


def test_span_has_files_attrs_accepts_cloud_trace_labels() -> None:
    assert _span_has_files_attrs(
        {
            "spans": [
                {
                    "name": "files.operation",
                    "labels": {
                        "files.operation.kind": "reference",
                        "files.file_id": "file_live",
                    },
                }
            ]
        }
    )


def test_wait_for_files_trace_requires_span_and_attrs(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "spans": [
            {
                "name": "files.operation",
                "labels": {"files.file_id": "file_live"},
            }
        ]
    }
    monkeypatch.setattr(
        "tools.r810_files_live_e2e._cloud_trace_payload",
        lambda **_kwargs: payload,
    )

    result = _wait_for_files_trace(
        project_id="project-ba535aa4-f08d-46b2-ba6",
        trace_id="trace",
        timeout_seconds=1.0,
        query_interval_seconds=0.01,
    )

    assert result.observed is True
    assert result.files_attrs_observed is True
    assert "files.operation" in result.span_names

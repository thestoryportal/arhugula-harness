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

from tools.r820_managed_agents_live_e2e import (
    R820LiveE2EError,
    _assert_managed_cloud_config,
    _cleanup_disposable_resources,
    _event_type,
    _span_has_managed_attrs,
    _wait_for_managed_agents_trace,
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


class _FakeSessions:
    def __init__(self) -> None:
        self.deleted: list[str] = []
        self.archived: list[str] = []

    def delete(self, session_id: str, **_kwargs: object) -> None:
        self.deleted.append(session_id)

    def archive(self, session_id: str, **_kwargs: object) -> None:
        self.archived.append(session_id)


class _FakeAgents:
    def __init__(self) -> None:
        self.archived: list[str] = []

    def archive(self, agent_id: str, **_kwargs: object) -> None:
        self.archived.append(agent_id)


class _FakeEnvironments:
    def __init__(self) -> None:
        self.deleted: list[str] = []
        self.archived: list[str] = []

    def delete(self, environment_id: str, **_kwargs: object) -> None:
        self.deleted.append(environment_id)

    def archive(self, environment_id: str, **_kwargs: object) -> None:
        self.archived.append(environment_id)


class _FakeBeta:
    def __init__(self) -> None:
        self.sessions = _FakeSessions()
        self.agents = _FakeAgents()
        self.environments = _FakeEnvironments()


class _FakeClient:
    def __init__(self) -> None:
        self.beta = _FakeBeta()


def test_assert_managed_cloud_config_accepts_r421_managed_collector_shape(
    tmp_path: Path,
) -> None:
    _assert_managed_cloud_config(_config(tmp_path))


def test_assert_managed_cloud_config_rejects_non_managed_or_loopback(tmp_path: Path) -> None:
    for config in (
        _config(tmp_path, deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER),
        _config(tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE),
        _config(tmp_path, otlp_endpoint="http://127.0.0.1:4317"),
        _config(tmp_path, bootstrap_sandbox_tier=SandboxTier.TIER_1_PROCESS),
    ):
        with pytest.raises(R820LiveE2EError):
            _assert_managed_cloud_config(config)


def test_event_type_supports_mapping_and_sdk_objects() -> None:
    class EventObject:
        type = "session.status_idle"

    assert _event_type({"type": "agent.message"}) == "agent.message"
    assert _event_type(EventObject()) == "session.status_idle"


def test_span_has_managed_attrs_accepts_cloud_trace_labels() -> None:
    assert _span_has_managed_attrs(
        {
            "spans": [
                {
                    "name": "managed_agents.runtime",
                    "labels": {
                        "managed_agents.session_id": "session_live",
                        "managed_agents.runtime_ms": "1000",
                    },
                }
            ]
        }
    )


def test_wait_for_managed_agents_trace_requires_span_and_attrs(monkeypatch) -> None:
    payload = {
        "spans": [
            {
                "name": "managed_agents.runtime",
                "labels": {"managed_agents.session_id": "session_live"},
            }
        ]
    }
    monkeypatch.setattr(
        "tools.r820_managed_agents_live_e2e._cloud_trace_payload",
        lambda **_kwargs: payload,
    )

    result = _wait_for_managed_agents_trace(
        project_id="project-ba535aa4-f08d-46b2-ba6",
        trace_id="trace",
        timeout_seconds=1.0,
        query_interval_seconds=0.01,
    )

    assert result.observed is True
    assert result.managed_attrs_observed is True
    assert "managed_agents.runtime" in result.span_names


def test_cleanup_disposable_resources_deletes_and_archives_created_ids() -> None:
    client = _FakeClient()

    _cleanup_disposable_resources(
        client,
        session_id="session_live",
        agent_id="agent_live",
        environment_id="environment_live",
    )

    assert client.beta.sessions.deleted == ["session_live"]
    assert client.beta.sessions.archived == []
    assert client.beta.agents.archived == ["agent_live"]
    assert client.beta.environments.deleted == ["environment_live"]
    assert client.beta.environments.archived == []

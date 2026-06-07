from __future__ import annotations

import os
from pathlib import Path

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

from tools.managed_cloud_readiness import e2b_secret_allowlist_entry
from tools.r421_managed_cloud_live_e2e import (
    R421LiveE2EError,
    _assert_deterministic_managed_cell,
    _assert_runtime_bootstrap_can_reach_collector,
    _cloud_run_grpc_credentials,
    _fetch_cloud_run_id_token,
    _probe_endpoint,
    _run_hosted_e2b_probe,
    _trace_id_hex,
    _trace_span_names,
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
            operator_allowlist=(e2b_secret_allowlist_entry(),),
        ),
        otel=OTelConfig(otlp_endpoint=otlp_endpoint),
        collector=CollectorConfig(
            placement=CollectorPlacement.VENDOR_PIPELINE,
            bootstrap_sandbox_tier=bootstrap_sandbox_tier,
        ),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def test_trace_id_hex_is_cloud_trace_width() -> None:
    assert _trace_id_hex(0xABC) == "00000000000000000000000000000abc"


def test_probe_endpoint_requires_cloud_run_style_grpc_url() -> None:
    _probe_endpoint("https://collector.example.run.app")

    for endpoint in (
        "http://collector.example.run.app",
        "https://collector.example.run.app/v1/traces",
        "https://",
    ):
        try:
            _probe_endpoint(endpoint)
        except R421LiveE2EError:
            pass
        else:  # pragma: no cover
            raise AssertionError(f"expected {endpoint!r} to fail")


def test_deterministic_config_requires_solo_managed_cloud(tmp_path: Path) -> None:
    _assert_deterministic_managed_cell(_config(tmp_path))

    for config in (
        _config(tmp_path, deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER),
        _config(tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE),
    ):
        try:
            _assert_deterministic_managed_cell(config)
        except R421LiveE2EError:
            pass
        else:  # pragma: no cover
            raise AssertionError("expected non-deterministic/non-managed config to fail")


def test_runtime_bootstrap_reachability_allows_managed_vendor_pipeline_with_full_vm_tier(
    tmp_path: Path,
) -> None:
    _assert_runtime_bootstrap_can_reach_collector(_config(tmp_path))


def test_runtime_bootstrap_reachability_fails_before_live_sandbox_for_tier1_vendor_pipeline(
    tmp_path: Path,
) -> None:
    try:
        _assert_runtime_bootstrap_can_reach_collector(
            _config(tmp_path, bootstrap_sandbox_tier=SandboxTier.TIER_1_PROCESS)
        )
    except R421LiveE2EError as exc:
        assert "failed before E2B sandbox creation" in str(exc)
        assert "VENDOR_PIPELINE" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected R-421 vendor pipeline bootstrap reachability to fail")


def test_trace_span_names_extracts_cloud_trace_v1_shape() -> None:
    payload = {
        "traceId": "abc",
        "spans": [
            {"name": "r421.managed_cloud.root"},
            {"name": "sandbox.violation"},
        ],
    }

    assert _trace_span_names(payload) == frozenset({"r421.managed_cloud.root", "sandbox.violation"})


def test_run_hosted_e2b_probe_restores_environment(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text("[runtime]\n", encoding="utf-8")
    monkeypatch.setenv("E2B_API_KEY", "previous")
    calls: list[str] = []

    monkeypatch.setattr(
        "tools.r421_managed_cloud_live_e2e.resolve_e2b_secret_from_config",
        lambda _config_file, *, secret_name: f"value-for-{secret_name}",
    )
    monkeypatch.setattr("tools.r421_managed_cloud_live_e2e._load_sandbox_class", lambda: object)

    def fake_run_probe(**_kwargs: object) -> str:
        calls.append(os.environ["E2B_API_KEY"])
        return "r421-e2b-ok"

    monkeypatch.setattr("tools.r421_managed_cloud_live_e2e.run_probe", fake_run_probe)

    _run_hosted_e2b_probe(
        config_file=config_file,
        secret_name="e2b-secret",
        sandbox_timeout_seconds=60,
        command_timeout_seconds=15,
    )

    assert calls == ["value-for-e2b-secret"]
    assert os.environ["E2B_API_KEY"] == "previous"


def test_fetch_cloud_run_id_token_uses_gcloud_without_printing_token(monkeypatch) -> None:
    calls: list[list[str]] = []

    class _Result:
        stdout = "header.payload.signature\n"

    def fake_run(command, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(command)
        assert kwargs["capture_output"] is True
        return _Result()

    monkeypatch.setattr("tools.r421_managed_cloud_live_e2e.subprocess.run", fake_run)

    assert (
        _fetch_cloud_run_id_token(
            audience="https://collector.example.run.app",
            gcloud_bin="/path/to/gcloud",
            impersonate_service_account="collector@example.iam.gserviceaccount.com",
        )
        == "header.payload.signature"
    )
    assert calls == [
        [
            "/path/to/gcloud",
            "auth",
            "print-identity-token",
            "--audiences=https://collector.example.run.app",
            "--impersonate-service-account=collector@example.iam.gserviceaccount.com",
        ]
    ]


def test_cloud_run_grpc_credentials_attach_authorization_metadata(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "tools.r421_managed_cloud_live_e2e.grpc.ssl_channel_credentials",
        lambda: "ssl-creds",
    )

    def fake_metadata_call_credentials(callback):  # type: ignore[no-untyped-def]
        captured["callback"] = callback
        return "call-creds"

    monkeypatch.setattr(
        "tools.r421_managed_cloud_live_e2e.grpc.metadata_call_credentials",
        fake_metadata_call_credentials,
    )
    monkeypatch.setattr(
        "tools.r421_managed_cloud_live_e2e.grpc.composite_channel_credentials",
        lambda *creds: ("composite", creds),
    )

    credentials = _cloud_run_grpc_credentials("redacted-token")

    assert credentials == ("composite", ("ssl-creds", "call-creds"))
    callback = captured["callback"]
    observed: list[object] = []
    callback(None, lambda metadata, error: observed.append((metadata, error)))
    assert observed == [((("authorization", "Bearer redacted-token"),), None)]

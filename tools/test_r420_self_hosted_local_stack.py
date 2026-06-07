from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STACK_DIR = ROOT / "deploy" / "self-hosted-local"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    assert isinstance(loaded, dict)
    return loaded


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        loaded = tomllib.load(handle)
    assert isinstance(loaded, dict)
    return loaded


def test_r420_compose_declares_local_collector_tempo_grafana_stack() -> None:
    compose = _load_yaml(STACK_DIR / "compose.yaml")

    services = compose["services"]
    assert {"otel-collector", "tempo", "grafana"} <= set(services)

    collector = services["otel-collector"]
    assert collector["image"].startswith(
        "${R420_OTEL_COLLECTOR_IMAGE:-otel/opentelemetry-collector-contrib:"
    )
    assert "4317:4317" in collector["ports"]
    assert "4318:4318" in collector["ports"]
    assert collector["depends_on"] == {"tempo": {"condition": "service_started"}}
    assert "./otel-collector.yaml:/etc/otelcol-contrib/config.yaml:ro" in collector["volumes"]

    tempo = services["tempo"]
    assert tempo["image"].startswith("${R420_TEMPO_IMAGE:-grafana/tempo:")
    assert "3200:3200" in tempo["ports"]

    grafana = services["grafana"]
    assert grafana["image"].startswith("${R420_GRAFANA_IMAGE:-grafana/grafana:")
    assert "3000:3000" in grafana["ports"]
    assert grafana["depends_on"] == {"tempo": {"condition": "service_started"}}


def test_r420_collector_receives_otlp_and_exports_traces_to_tempo() -> None:
    collector = _load_yaml(STACK_DIR / "otel-collector.yaml")

    protocols = collector["receivers"]["otlp"]["protocols"]
    assert protocols["grpc"]["endpoint"] == "0.0.0.0:4317"
    assert protocols["http"]["endpoint"] == "0.0.0.0:4318"

    assert "batch" in collector["processors"]
    tempo_exporter = collector["exporters"]["otlp/tempo"]
    assert tempo_exporter["endpoint"] == "tempo:4317"
    assert tempo_exporter["tls"] == {"insecure": True}

    traces = collector["service"]["pipelines"]["traces"]
    assert traces["receivers"] == ["otlp"]
    assert traces["processors"] == ["batch"]
    assert traces["exporters"] == ["otlp/tempo"]


def test_r420_tempo_binds_otlp_receivers_for_container_network() -> None:
    tempo = _load_yaml(STACK_DIR / "tempo.yaml")

    assert tempo["auth_enabled"] is False
    protocols = tempo["distributor"]["receivers"]["otlp"]["protocols"]
    assert protocols["grpc"]["endpoint"] == "0.0.0.0:4317"
    assert protocols["http"]["endpoint"] == "0.0.0.0:4318"
    assert tempo["storage"]["trace"]["backend"] == "local"


def test_r420_grafana_datasource_points_at_tempo_service() -> None:
    datasource = _load_yaml(STACK_DIR / "grafana" / "provisioning" / "datasources" / "tempo.yaml")

    tempo_sources = [entry for entry in datasource["datasources"] if entry["type"] == "tempo"]
    assert len(tempo_sources) == 1
    assert tempo_sources[0]["name"] == "Tempo"
    assert tempo_sources[0]["url"] == "http://tempo:3200"
    assert tempo_sources[0]["isDefault"] is True


def test_r420_harness_template_matches_static_self_hosted_readiness_gate() -> None:
    config = _load_toml(STACK_DIR / "harness.selfhosted.local.example.toml")
    runtime = config["runtime"]

    assert runtime["deployment_surface"] == "self-hosted-server"
    assert runtime["otel"]["otlp_endpoint"] == "http://127.0.0.1:4317"
    assert runtime["collector"]["placement"] == "SELF_HOSTED_BACKEND_COLLECTOR"
    assert runtime["provider_secrets"]["backend"] == "self-hosted-keyring"
    assert runtime["provider_secrets"]["keyring_service"] == "harness"
    assert runtime["provider_secrets"]["operator_allowlist"] == [
        {"name": "anthropic_key", "scope": {"name": "default"}}
    ]

    path_bindings = runtime["path_bindings"]["raw_entries"]
    assert len(path_bindings) == 4
    assert {entry["deployment_surface"] for entry in path_bindings} == {"self-hosted-server"}

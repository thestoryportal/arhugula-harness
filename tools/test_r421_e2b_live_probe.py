from __future__ import annotations

import importlib
from typing import ClassVar

from tools.r421_e2b_live_probe import (
    LiveProbeError,
    _load_sandbox_class,
    main,
    resolve_e2b_secret_from_config,
    run_probe,
)


class _Result:
    stdout = "r421-e2b-ok"


class _Commands:
    calls: ClassVar[list[tuple[str, int]]] = []

    def run(self, command: str, *, timeout: int) -> _Result:
        self.calls.append((command, timeout))
        return _Result()


class _Sandbox:
    create_kwargs: ClassVar[dict[str, object]] = {}

    def __init__(self) -> None:
        self.commands = _Commands()

    @classmethod
    def create(cls, **kwargs: object) -> _Sandbox:
        cls.create_kwargs = kwargs
        return cls()

    def __enter__(self) -> _Sandbox:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None


def test_run_probe_disables_internet_and_tags_roadmap_item() -> None:
    stdout = run_probe(
        sandbox_cls=_Sandbox,
        command="printf r421-e2b-ok",
        sandbox_timeout_seconds=60,
        command_timeout_seconds=15,
    )

    assert stdout == "r421-e2b-ok"
    assert _Sandbox.create_kwargs == {
        "timeout": 60,
        "allow_internet_access": False,
        "metadata": {"roadmap_item": "R-421-managed-cloud-deployment-e2e"},
    }


def test_load_sandbox_class_fails_when_sdk_missing(monkeypatch) -> None:
    def missing(_name: str):
        raise ImportError("missing")

    monkeypatch.setattr(importlib, "import_module", missing)

    try:
        _load_sandbox_class()
    except LiveProbeError as exc:
        assert "Python module 'e2b' is not importable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected LiveProbeError")


def test_resolve_e2b_secret_from_config_uses_provider_backend(
    tmp_path,
    monkeypatch,
) -> None:
    config_file = tmp_path / "harness.managed-cloud.toml"
    config_file.write_text(
        """
[runtime]
deployment_surface = "managed-cloud"
repository_root = "/tmp"
default_topology = "single-threaded-linear"

[runtime.provider_secrets]
backend = "gcp-secret-manager"
gcp_project_id = "project-ba535aa4-f08d-46b2-ba6"

[[runtime.provider_secrets.operator_allowlist]]
name = "e2b-secret"
scope = { name = "r421-managed-cloud" }

[runtime.otel]
otlp_endpoint = "https://collector.example/v1/traces"

[runtime.collector]
placement = "VENDOR_PIPELINE"
""",
        encoding="utf-8",
    )
    calls: list[str] = []

    class _Resolver:
        def resolve_bootstrap_value(self, name: str) -> str:
            calls.append(name)
            return "e2b-secret-from-backend"

    monkeypatch.setattr(
        "tools.r421_e2b_live_probe.make_provider_secret_resolver",
        lambda _provider_secrets: _Resolver(),
    )

    assert (
        resolve_e2b_secret_from_config(config_file, secret_name="e2b-secret")
        == "e2b-secret-from-backend"
    )
    assert calls == ["e2b-secret"]


def test_main_resolve_only_sources_key_from_config_without_sandbox(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    config_file = tmp_path / "harness.managed-cloud.toml"
    config_file.write_text(
        """
[runtime]
deployment_surface = "managed-cloud"
repository_root = "/tmp"
default_topology = "single-threaded-linear"

[runtime.provider_secrets]
backend = "gcp-secret-manager"
gcp_project_id = "project-ba535aa4-f08d-46b2-ba6"

[runtime.otel]
otlp_endpoint = "https://collector.example/v1/traces"

[runtime.collector]
placement = "VENDOR_PIPELINE"
""",
        encoding="utf-8",
    )
    monkeypatch.delenv("E2B_API_KEY", raising=False)
    monkeypatch.setattr(
        "tools.r421_e2b_live_probe.resolve_e2b_secret_from_config",
        lambda _config_file, *, secret_name: f"value-for-{secret_name}",
    )

    assert main(["--config", str(config_file), "--resolve-only"]) == 0

    output = capsys.readouterr().out
    assert "resolved e2b-secret from configured provider-secret backend (redacted)" in output
    assert "resolve-only completed: no hosted E2B sandbox was created" in output
    assert "value-for-e2b-secret" not in output

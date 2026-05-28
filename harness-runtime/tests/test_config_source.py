"""Tests for U-RT-103 — 3-source RuntimeConfig loader (spec v1.35 §3.7).

Maps to acceptance criteria 1-9 at runtime plan v2.31 §1.3.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern

from harness_runtime.config_source import (
    RUNTIME_CONFIG_LOAD_FAIL_CLASS,
    RuntimeConfigLoadError,
    RuntimeConfigSource,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _minimum_required_overrides() -> dict[str, Any]:
    """Minimum kwargs to construct a valid RuntimeConfig.

    Sub-configs are empty placeholders; mirrors the U-RT-04 test fixture.
    """
    return {
        "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
        "repository_root": Path("/tmp"),
        "path_bindings": PathBindingConfig(),
        "provider_secrets": ProviderSecretsConfig(),
        "otel": OTelConfig(otlp_endpoint="http://localhost:4318"),
        "collector": CollectorConfig(),
        "default_topology": TopologyPattern.SINGLE_THREADED_LINEAR,
    }


@pytest.fixture(autouse=True)
def _clear_harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip every ``HARNESS_*`` var so a leaked dev-shell value can't pollute."""
    for key in list(os.environ):
        if key.startswith("HARNESS_"):
            monkeypatch.delenv(key, raising=False)


# AC #1 — no env / no file / no CLI overrides composes to Pydantic defaults.
# RuntimeConfig has required fields with no class-level defaults; we supply
# the minimum required set via cli_overrides and verify defaults flow through
# for the remaining fields. Equivalent to `RuntimeConfig(**minimum)`.
def test_default_load_returns_runtime_config_pydantic_defaults() -> None:
    overrides = _minimum_required_overrides()
    cfg = RuntimeConfigSource.load(cli_overrides=overrides)
    direct = RuntimeConfig(**overrides)
    assert cfg == direct
    # Spot-check: an unset optional field inherits its declared default.
    assert cfg.tenant_id is None
    assert cfg.drain_timeout_seconds == 60.0
    assert cfg.step_dispatch_timeout_seconds == 30.0


# AC #2 — HARNESS_TENANT_ID → config.tenant_id.
def test_env_var_supplies_tenant_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARNESS_TENANT_ID", "acme")
    cfg = RuntimeConfigSource.load(cli_overrides=_minimum_required_overrides())
    assert cfg.tenant_id == "acme"


# AC #3 — config-file [runtime] table supplies tenant_id.
def test_config_file_runtime_table_supplies_tenant_id(tmp_path: Path) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text('[runtime]\ntenant_id = "acme"\n', encoding="utf-8")
    cfg = RuntimeConfigSource.load(
        config_file=config_file,
        cli_overrides=_minimum_required_overrides(),
    )
    assert cfg.tenant_id == "acme"


# AC #4 — CLI overrides supply tenant_id.
def test_cli_overrides_supply_tenant_id() -> None:
    overrides = _minimum_required_overrides() | {"tenant_id": "acme"}
    cfg = RuntimeConfigSource.load(cli_overrides=overrides)
    assert cfg.tenant_id == "acme"


# AC #5 — precedence: env=X + file=Y + CLI=Z → CLI wins.
def test_cli_overrides_win_over_file_and_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HARNESS_TENANT_ID", "env-tenant")
    config_file = tmp_path / "harness.toml"
    config_file.write_text('[runtime]\ntenant_id = "file-tenant"\n', encoding="utf-8")
    overrides = _minimum_required_overrides() | {"tenant_id": "cli-tenant"}
    cfg = RuntimeConfigSource.load(config_file=config_file, cli_overrides=overrides)
    assert cfg.tenant_id == "cli-tenant"


# AC #6 — precedence: env=X + file=Y (no CLI override of that field) → file wins.
def test_config_file_wins_over_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HARNESS_TENANT_ID", "env-tenant")
    config_file = tmp_path / "harness.toml"
    config_file.write_text('[runtime]\ntenant_id = "file-tenant"\n', encoding="utf-8")
    cfg = RuntimeConfigSource.load(
        config_file=config_file,
        cli_overrides=_minimum_required_overrides(),
    )
    assert cfg.tenant_id == "file-tenant"


# AC #7 — plaintext API key at config file → RT-FAIL-CLI-CONFIG-LOAD typed exc.
def test_plaintext_api_key_in_config_raises_secrets_excluded_error(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        '[runtime]\nanthropic_api_key = "sk-fake-leaked-token"\n',
        encoding="utf-8",
    )
    with pytest.raises(RuntimeConfigLoadError) as excinfo:
        RuntimeConfigSource.load(
            config_file=config_file,
            cli_overrides=_minimum_required_overrides(),
        )
    err = excinfo.value
    assert err.FAIL_CLASS == RUNTIME_CONFIG_LOAD_FAIL_CLASS == "RT-FAIL-CLI-CONFIG-LOAD"
    assert "ADR-F5" in str(err)
    assert "keyring" in str(err).lower()
    assert "anthropic_api_key" in str(err)


# AC #8 — TOML parse error → RT-FAIL-CLI-CONFIG-LOAD with file path.
def test_toml_parse_error_raises_config_load_error(tmp_path: Path) -> None:
    config_file = tmp_path / "broken.toml"
    config_file.write_text("[runtime\nthis is not valid TOML", encoding="utf-8")
    with pytest.raises(RuntimeConfigLoadError) as excinfo:
        RuntimeConfigSource.load(
            config_file=config_file,
            cli_overrides=_minimum_required_overrides(),
        )
    err = excinfo.value
    assert err.FAIL_CLASS == "RT-FAIL-CLI-CONFIG-LOAD"
    assert "TOML parse error" in str(err)
    assert str(config_file) in str(err)


# AC #9 — type mismatch (TOML integer for str field) → RT-FAIL-CLI-CONFIG-LOAD.
def test_type_mismatch_raises_config_load_error_with_pydantic_validation(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text("[runtime]\ntenant_id = 42\n", encoding="utf-8")
    with pytest.raises(RuntimeConfigLoadError) as excinfo:
        RuntimeConfigSource.load(
            config_file=config_file,
            cli_overrides=_minimum_required_overrides(),
        )
    err = excinfo.value
    assert err.FAIL_CLASS == "RT-FAIL-CLI-CONFIG-LOAD"
    assert "Pydantic validation failed" in str(err)


# Coverage extension: secrets-exclusion catches nested keys too (Q-L=b walks
# the full TOML document, not just the top-level table).
def test_nested_secret_key_in_config_raises_secrets_excluded_error(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        "[provider.anthropic]\nsecret_token = \"sk-fake\"\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeConfigLoadError) as excinfo:
        RuntimeConfigSource.load(
            config_file=config_file,
            cli_overrides=_minimum_required_overrides(),
        )
    assert "secret_token" in str(excinfo.value)

"""`materialize_protected_result_store_stage` — B-65-A stage-4 factory tests.

Implements `Spec_Harness_Runtime_v1.md` v1.103 §14.8.11 construction (RATIFIED
B-65 Class 2 fork §3b).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.bootstrap.factories.protected_result_store_factory import (
    materialize_protected_result_store_stage,
)
from harness_runtime.lifecycle.protected_result_store import ProtectedResultStore
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
    )


def test_unset_key_env_var_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HARNESS_PROTECTED_RESULT_STORE_KEY", raising=False)
    assert materialize_protected_result_store_stage(_config(tmp_path)) is None


def test_malformed_key_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation probe: propagating the malformed-key exception instead of
    degrading to None fails this witness (the caller — validate_mtc_audit_
    signing_config — is the fail-loud site, not this factory)."""
    monkeypatch.setenv("HARNESS_PROTECTED_RESULT_STORE_KEY", "not-a-valid-fernet-key")
    assert materialize_protected_result_store_stage(_config(tmp_path)) is None


def test_valid_key_constructs_a_working_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HARNESS_PROTECTED_RESULT_STORE_KEY", Fernet.generate_key().decode("ascii"))
    store = materialize_protected_result_store_stage(_config(tmp_path))
    assert isinstance(store, ProtectedResultStore)
    ref = store.write_once("tenant-a", "round-trip payload")
    assert isinstance(ref, str)
    assert store.read("tenant-a", ref) == "round-trip payload"


def test_custom_key_env_var_name_honored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`RuntimeConfig.protected_result_store_key_env_var` names WHICH env var
    to read — mutation probe: hardcoding the default name instead of reading
    the config field fails this witness."""
    monkeypatch.delenv("HARNESS_PROTECTED_RESULT_STORE_KEY", raising=False)
    monkeypatch.setenv("CUSTOM_STORE_KEY_VAR", Fernet.generate_key().decode("ascii"))
    config = _config(tmp_path).model_copy(
        update={"protected_result_store_key_env_var": "CUSTOM_STORE_KEY_VAR"}
    )
    store = materialize_protected_result_store_stage(config)
    assert isinstance(store, ProtectedResultStore)


@pytest.mark.parametrize("bad_ttl", [0.0, -1.0])
def test_nonpositive_ttl_rejected_at_construction(tmp_path: Path, bad_ttl: float) -> None:
    """codex [P2] on the B-65-A CP-side arc: a zero/negative TTL is rejected at
    `RuntimeConfig` CONSTRUCTION (the `Field(gt=0.0)` constraint) — without it,
    the first successful write would immediately collect its own newly-created
    entry during the opportunistic sweep, returning a live-looking `str` ref
    whose subsequent read 404s. `model_copy(update=...)` deliberately bypasses
    pydantic validation (verified empirically, unrelated to this fix), so this
    witness constructs a FRESH config directly — the real deployment-config-
    loading shape, not the `model_copy` test-convenience shape used elsewhere
    in this file."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        RuntimeConfig(
            deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
            repository_root=tmp_path,
            path_bindings=PathBindingConfig(),
            provider_secrets=ProviderSecretsConfig(),
            otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
            collector=CollectorConfig(),
            default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
            mcp_clients=[],
            protected_result_store_ttl_seconds=bad_ttl,
        )


def test_ttl_env_only_override_honored_through_both_loaders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """codex round-4 [P2]: the TTL gates a compliance property (retention
    window for tenant-scoped protected payloads at the MTC tier) and must
    be registered in BOTH `config/loader.py::_ENV_SCALAR_FIELDS` and
    `config_source.py::_RuntimeEnvSettings`
    ([[runtimeconfig-scalar-needs-both-env-loaders]]). Mutation probe:
    removing EITHER loader registration fails one half."""
    from harness_core.deployment_surface import DeploymentSurface as _DS
    from harness_cp.topology_pattern import TopologyPattern as _TP
    from harness_runtime.config.loader import materialize_runtime_config

    def _kwargs() -> dict[str, object]:
        return {
            "deployment_surface": _DS.LOCAL_DEVELOPMENT,
            "repository_root": tmp_path,
            "path_bindings": PathBindingConfig(),
            "provider_secrets": ProviderSecretsConfig(),
            "otel": OTelConfig(otlp_endpoint="http://localhost:4317"),
            "collector": CollectorConfig(),
            "default_topology": _TP.SINGLE_THREADED_LINEAR,
            "mcp_clients": [],
        }

    # Half 1 — config/loader.py::_ENV_SCALAR_FIELDS path (explicit env map).
    config = materialize_runtime_config(
        env={"HARNESS_PROTECTED_RESULT_STORE_TTL_SECONDS": "123.5"}, **_kwargs()
    )
    assert config.protected_result_store_ttl_seconds == 123.5

    # Half 2 — config_source.py::_RuntimeEnvSettings path (process env).
    monkeypatch.setenv("HARNESS_PROTECTED_RESULT_STORE_TTL_SECONDS", "456.5")
    from harness_runtime.config_source import RuntimeConfigSource

    config2 = RuntimeConfigSource.load(
        cli_overrides={k: str(v) if isinstance(v, Path) else v for k, v in _kwargs().items()}
    )
    assert config2.protected_result_store_ttl_seconds == 456.5


def test_ttl_threaded_from_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation probe: hardcoding a fixed TTL instead of reading
    `config.protected_result_store_ttl_seconds` fails this witness."""
    monkeypatch.setenv("HARNESS_PROTECTED_RESULT_STORE_KEY", Fernet.generate_key().decode("ascii"))
    config = _config(tmp_path).model_copy(update={"protected_result_store_ttl_seconds": 1.0})
    store = materialize_protected_result_store_stage(config)
    assert isinstance(store, ProtectedResultStore)
    store.write_once("tenant-a", "expires fast")
    expired = store.gc_sweep(now=time.time() + 10.0)
    assert len(expired) == 1

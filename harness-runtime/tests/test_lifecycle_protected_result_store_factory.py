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

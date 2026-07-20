"""U-RT-140 — `sub_agent_dispatch_max_workers` C-RT-03 field tests (B-48).

Tests per Implementation_Plan_Harness_Runtime_v2_50.md §1.1 (PD-8
mutation-probed): dual env-loader registration (mutation probe: removing
EITHER loader registration fails), ≥1 validation at config load, and the
typed capacity error naming the overflowing step + descent chain (the
error carrier itself is U-CORE-03; the taxonomy-row mapping witness here
pins the Runtime-side surface).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from harness_core import DeploymentSurface, SubAgentDispatchCapacityError
from harness_runtime.config.loader import materialize_runtime_config
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
    TopologyPattern,
)
from pydantic import ValidationError


def _required_kwargs() -> dict[str, Any]:
    return {
        "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
        "repository_root": Path("/tmp"),
        "path_bindings": PathBindingConfig(),
        "provider_secrets": ProviderSecretsConfig(),
        "otel": OTelConfig(otlp_endpoint="http://localhost:4318"),
        "collector": CollectorConfig(),
        "default_topology": TopologyPattern.SINGLE_THREADED_LINEAR,
    }


def test_cap_field_default_256() -> None:
    config = materialize_runtime_config(env={}, **_required_kwargs())
    assert config.sub_agent_dispatch_max_workers == 256


def test_cap_field_env_only_override_honored_through_both_loaders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mutation probe: removing EITHER loader registration fails one half."""
    # Half 1 — config/loader.py::_ENV_SCALAR_FIELDS path (explicit env map).
    config = materialize_runtime_config(
        env={"HARNESS_SUB_AGENT_DISPATCH_MAX_WORKERS": "32"}, **_required_kwargs()
    )
    assert config.sub_agent_dispatch_max_workers == 32
    # Half 2 — config_source.py::_RuntimeEnvSettings path (process env).
    monkeypatch.setenv("HARNESS_SUB_AGENT_DISPATCH_MAX_WORKERS", "48")
    from harness_runtime.config_source import RuntimeConfigSource

    config2 = RuntimeConfigSource.load(
        cli_overrides={
            k: str(v) if isinstance(v, Path) else v for k, v in _required_kwargs().items()
        }
    )
    assert config2.sub_agent_dispatch_max_workers == 48


def test_cap_field_validated_ge_one_at_config_load() -> None:
    """0 and negative are typed config-validation rejections."""
    for bad in (0, -1):
        with pytest.raises(ValidationError):
            RuntimeConfig(sub_agent_dispatch_max_workers=bad, **_required_kwargs())
    with pytest.raises(ValidationError):
        materialize_runtime_config(
            env={"HARNESS_SUB_AGENT_DISPATCH_MAX_WORKERS": "0"}, **_required_kwargs()
        )


def test_cap_field_unset_changes_no_existing_config_surface() -> None:
    """Contract-minor byte-compat: default construction untouched."""
    base = materialize_runtime_config(env={}, **_required_kwargs())
    assert base.sub_agent_dispatch_max_workers == 256
    # The field is optional-with-default: constructing without it succeeds and
    # no other field's default shifts.
    assert base.step_dispatch_timeout_seconds == 30.0


def test_capacity_error_names_overflowing_step_and_descent_chain() -> None:
    """The §14.8.10.5 row's C1 contract on the Runtime-consumed carrier."""
    err = SubAgentDispatchCapacityError(
        requested_frames=2,
        available_capacity=0,
        step_id="step-dispatch-7",
        descent_chain=("wf-root", "step-dispatch-7"),
    )
    assert "step-dispatch-7" in str(err)
    assert "wf-root -> step-dispatch-7" in str(err)

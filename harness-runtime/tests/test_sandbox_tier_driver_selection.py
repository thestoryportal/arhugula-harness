"""Sandbox tier→driver selection contract — runtime spec v1.43 §14.9.9.

Covers the R-CC-1 arc #1 fix (`.harness/class_1_fork_sandbox_tier_driver_selection_silent_in_process.md`,
Reading A+): the resolved sandbox tier now selects the matching execution driver
(FR-1), or fails loud (FR-2) — it is NEVER silently executed in-process under a
`> TIER_1_PROCESS` claim. Two layers tested here without a live substrate:

- the deployment-surface-aware default policy + three-field coherence
  (`resolve_effective_sandbox_defaults`);
- the tier→driver selection registry + the fail-loud branches
  (`_select_tool_execution_driver`) — the discriminating-power / contrasting-baseline
  test (same no-driver input; TIER_1 → in-process driver, TIER_2 → RAISE).
"""

from __future__ import annotations

import pytest
from harness_as.discriminators import MCPTransport
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.sandbox_tier_floor import MCPServerTrustLevel
from harness_core import ClientName
from harness_core.deployment_surface import DeploymentSurface
from harness_runtime.bootstrap.factories.runtime_tool_dispatcher_factory import (
    _select_tool_execution_driver,
)
from harness_runtime.config.sandbox_defaults import resolve_effective_sandbox_defaults
from harness_runtime.lifecycle.docker_tool_execution_driver import (
    DockerToolRunnerExecutionDriver,
    GVisorRunscToolRunnerExecutionDriver,
)
from harness_runtime.lifecycle.e2b_tool_execution_driver import (
    E2BManagedFullVMToolRunnerExecutionDriver,
)
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    MCPHostToolExecutionDriver,
    SandboxDriverUnavailableError,
)
from harness_runtime.types import MCPClientConfig, SandboxDriverConfig


def _client(**overrides: object) -> MCPClientConfig:
    base: dict[str, object] = dict(
        client_name=ClientName("echo-server"),
        transport=MCPTransport.STDIO,
        trust_level=MCPServerTrustLevel.L1_SIGNED_PINNED,
        blast_radius=BlastRadiusTier.READ_ONLY,
        connection_url="stdio:///bin/echo",
    )
    base.update(overrides)
    return MCPClientConfig(**base)  # type: ignore[arg-type]


_DRIVER_CFG = SandboxDriverConfig(command=("python", "runner.py"), image="echo:latest")


# ---------------------------------------------------------------------------
# resolve_effective_sandbox_defaults — surface-aware default policy (Reading A+).
# ---------------------------------------------------------------------------


def test_bare_local_development_resolves_honest_tier_1() -> None:
    """A bare local-development config → honest TIER_1_PROCESS, coherent
    minimum_tier + sandbox_tier (no spurious floor violation), in-process out-of-box."""
    eff = resolve_effective_sandbox_defaults(_client(), DeploymentSurface.LOCAL_DEVELOPMENT)
    assert eff.sandbox_tier is SandboxTier.TIER_1_PROCESS
    assert eff.minimum_tier is SandboxTier.TIER_1_PROCESS
    assert eff.sandbox_tech == "host-process"
    assert eff.sandbox_provider == "host"


@pytest.mark.parametrize(
    "surface",
    [DeploymentSurface.SELF_HOSTED_SERVER, DeploymentSurface.MANAGED_CLOUD],
)
def test_bare_production_surfaces_resolve_fail_safe_high(surface: DeploymentSurface) -> None:
    """Bare self-hosted / managed-cloud configs → fail-safe-high TIER_2_CONTAINER
    (which FR-2(i) refuses to run unless a driver is configured)."""
    eff = resolve_effective_sandbox_defaults(_client(), surface)
    assert eff.sandbox_tier is SandboxTier.TIER_2_CONTAINER
    assert eff.minimum_tier is SandboxTier.TIER_2_CONTAINER
    assert eff.sandbox_tech == "container"


def test_explicit_operator_values_override_surface_policy() -> None:
    """An explicit per-server tier/tech/provider overrides the surface-aware default."""
    eff = resolve_effective_sandbox_defaults(
        _client(
            default_sandbox_tier=SandboxTier.TIER_3_MICROVM,
            default_minimum_tier=SandboxTier.TIER_3_MICROVM,
            default_sandbox_tech="gvisor",
            default_sandbox_provider="runsc",
        ),
        DeploymentSurface.LOCAL_DEVELOPMENT,  # would default TIER_1 — overridden
    )
    assert eff.sandbox_tier is SandboxTier.TIER_3_MICROVM
    assert eff.minimum_tier is SandboxTier.TIER_3_MICROVM
    assert eff.sandbox_tech == "gvisor"


# ---------------------------------------------------------------------------
# _select_tool_execution_driver — tier→driver registry (FR-1) + fail-loud (FR-2).
# ---------------------------------------------------------------------------


def test_tier_1_selects_in_process_host_driver_without_config() -> None:
    """TIER_1_PROCESS needs no driver config — the in-process host driver."""
    driver = _select_tool_execution_driver(tier=SandboxTier.TIER_1_PROCESS, driver_config=None)
    assert isinstance(driver, MCPHostToolExecutionDriver)


def test_tier_2_selects_docker_driver_when_configured() -> None:
    driver = _select_tool_execution_driver(
        tier=SandboxTier.TIER_2_CONTAINER, driver_config=_DRIVER_CFG
    )
    assert isinstance(driver, DockerToolRunnerExecutionDriver)
    # Delivered-tier == resolved-tier invariant (the driver self-guards on it).
    assert driver.required_tier is SandboxTier.TIER_2_CONTAINER


def test_tier_3_selects_gvisor_driver_when_configured() -> None:
    driver = _select_tool_execution_driver(
        tier=SandboxTier.TIER_3_MICROVM, driver_config=_DRIVER_CFG
    )
    assert isinstance(driver, GVisorRunscToolRunnerExecutionDriver)
    assert driver.required_tier is SandboxTier.TIER_3_MICROVM
    assert driver.runtime == "runsc"


def test_tier_4_selects_e2b_driver_when_configured() -> None:
    driver = _select_tool_execution_driver(
        tier=SandboxTier.TIER_4_FULL_VM,
        driver_config=SandboxDriverConfig(command=("python", "runner.py")),
    )
    assert isinstance(driver, E2BManagedFullVMToolRunnerExecutionDriver)
    assert driver.required_tier is SandboxTier.TIER_4_FULL_VM


# --- FR-2(i) fail-loud — the contrasting-baseline / discriminating-power test ---


def test_tier_2_without_any_driver_config_fails_loud_not_in_process() -> None:
    """THE security fix: a TIER_2_CONTAINER claim with no driver configured RAISES
    `RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE` — it does NOT silently fall through to the
    in-process driver (the pre-v1.43 defect). Discriminating power: same no-driver
    input as the TIER_1 case above, opposite outcome."""
    with pytest.raises(SandboxDriverUnavailableError):
        _select_tool_execution_driver(tier=SandboxTier.TIER_2_CONTAINER, driver_config=None)


@pytest.mark.parametrize(
    "tier",
    [SandboxTier.TIER_2_CONTAINER, SandboxTier.TIER_3_MICROVM],
)
def test_container_tiers_without_image_fail_loud(tier: SandboxTier) -> None:
    """A container/microVM tier with a driver config missing `image` fails loud —
    a partially-configured driver is non-delivery, not a silent downgrade."""
    cfg = SandboxDriverConfig(command=("python", "runner.py"))  # no image
    with pytest.raises(SandboxDriverUnavailableError):
        _select_tool_execution_driver(tier=tier, driver_config=cfg)

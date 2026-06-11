"""Deployment-surface-aware per-server sandbox default policy (Reading A+).

Per runtime spec v1.43 §14.9.9 + fork
`.harness/class_1_fork_sandbox_tier_driver_selection_silent_in_process.md` §7.1.
When a per-server `MCPClientConfig` leaves a sandbox default field unset
(`None`), the effective default is keyed on `RuntimeConfig.deployment_surface`:

- `local-development` → honest `TIER_1_PROCESS` in-process (no lie, runs out-of-box;
  the in-process host driver needs no substrate).
- `self-hosted-server` / `managed-cloud` → fail-safe-high `TIER_2_CONTAINER` (which
  FR-2(i) fail-loud at the stage-5 factory refuses to run unless a `sandbox_driver`
  is configured).

This is a *floor-safe* default per the floor-verification at fork §7: the ADR-D2
§1.1 / C-AS-09 §9.1 cells are raise-only floors, so a surface-keyed default only
ever sits at or above the matrix floor, and the §14.9.4 tier-floor check is the
safety net against silent under-sandboxing.

The single source of truth for BOTH the stage-3a converter (`minimum_tier`) and the
stage-5 resolver/driver-selection (`sandbox_tier`/`tech`/`provider`) — so the three
`default_*` fields stay coherent and a bare config never spuriously trips the
floor check (the three-field-incoherence catch recorded at fork §7.1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from harness_as.sandbox_tier import SandboxTier
from harness_core.deployment_surface import DeploymentSurface

if TYPE_CHECKING:
    from harness_runtime.types import MCPClientConfig

__all__ = [
    "EffectiveSandboxDefaults",
    "resolve_effective_sandbox_defaults",
    "surface_default_sandbox_tier",
]


# Per-tier (tech, provider) labels emitted on the `sandbox.enter` span when the
# operator leaves them unset. Impl-discretion (§14.9.9 Deferred — "the registry
# names families, not classes"). NOTE (adversarial-review F1-02): these are
# placeholder labels that do NOT yet match the ADR-D2 §1.7 canonical `sandbox.*`
# namespace (where `sandbox.tech` = the tier-mechanism class e.g. `microvm`, and
# `sandbox.provider` = the provider+tech tuple e.g. `e2b_firecracker`). Aligning
# them is deferred to the future observability-hygiene arc alongside the §1.7
# provider-class reconciliation; the operator may override per-server today.
_TIER_TECH_PROVIDER: dict[SandboxTier, tuple[str, str]] = {
    SandboxTier.TIER_1_PROCESS: ("host-process", "host"),
    SandboxTier.TIER_2_CONTAINER: ("container", "docker"),
    SandboxTier.TIER_3_MICROVM: ("gvisor", "runsc"),
    SandboxTier.TIER_4_FULL_VM: ("firecracker", "e2b"),
}


@dataclass(frozen=True)
class EffectiveSandboxDefaults:
    """The reconciled per-server sandbox defaults after applying the
    deployment-surface-aware policy to any `None` `MCPClientConfig` fields."""

    minimum_tier: SandboxTier
    sandbox_tier: SandboxTier
    sandbox_tech: str
    sandbox_provider: str


def surface_default_sandbox_tier(deployment_surface: DeploymentSurface) -> SandboxTier:
    """The Reading-A+ default sandbox tier for a deployment surface (used when the
    operator leaves the per-server tier unset)."""
    if deployment_surface is DeploymentSurface.LOCAL_DEVELOPMENT:
        # Honest in-process default — the in-process host driver needs no substrate,
        # so a bare local-dev config runs out-of-box, truthfully labeled TIER_1.
        return SandboxTier.TIER_1_PROCESS
    # self-hosted-server / managed-cloud: fail-safe-high. FR-2(i) refuses to run
    # unless a sandbox_driver is configured — production never runs silently
    # unsandboxed.
    return SandboxTier.TIER_2_CONTAINER


def resolve_effective_sandbox_defaults(
    entry: MCPClientConfig, deployment_surface: DeploymentSurface
) -> EffectiveSandboxDefaults:
    """Resolve the per-server sandbox defaults, applying the surface-aware policy to
    any unset (`None`) field and keeping the three tier-bearing fields coherent.

    Explicit operator values always override the policy. When `default_minimum_tier`
    / `default_sandbox_tier` are both `None`, they resolve to the SAME surface-derived
    tier — so the §14.9.4 tier-floor check (`resolved.tier >= contract.minimum_tier`)
    never spuriously violates on a bare config.
    """
    surface_tier = surface_default_sandbox_tier(deployment_surface)

    sandbox_tier = (
        entry.default_sandbox_tier if entry.default_sandbox_tier is not None else surface_tier
    )
    minimum_tier = (
        entry.default_minimum_tier if entry.default_minimum_tier is not None else surface_tier
    )

    default_tech, default_provider = _TIER_TECH_PROVIDER[sandbox_tier]
    sandbox_tech = (
        entry.default_sandbox_tech if entry.default_sandbox_tech is not None else default_tech
    )
    sandbox_provider = (
        entry.default_sandbox_provider
        if entry.default_sandbox_provider is not None
        else default_provider
    )

    return EffectiveSandboxDefaults(
        minimum_tier=minimum_tier,
        sandbox_tier=sandbox_tier,
        sandbox_tech=sandbox_tech,
        sandbox_provider=sandbox_provider,
    )

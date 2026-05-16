"""harness-as — Action Surface (AS) axis.

Public API re-exports. Authority: harness-as/CLAUDE.md; AS plan v1.
"""

from harness_as.blast_radius_floor import blast_radius_floor
from harness_as.discriminators import DeploymentSurface, MCPTransport, PersonaTier
from harness_as.forced_tier_resolution import (
    ForcedTierCause,
    ForcedTierResult,
    ToolContext,
    forced_tier,
)
from harness_as.operator_policy_override_scope import (
    OverrideScopeResult,
    override_scope,
)
from harness_as.sandbox_fail_class import (
    C5FailClass,
    C9RetryPosture,
    SandboxFailClass,
    SandboxFailClassMetadata,
    fail_class_metadata,
    permanent_fail_skips_staircase,
)
from harness_as.sandbox_provider_class import (
    ClassCardinality,
    ProviderClassMetadata,
    SandboxProviderClass,
    provider_class_metadata,
)
from harness_as.sandbox_tier import (
    BlastRadiusTier,
    MechanismClass,
    SandboxTier,
    SandboxTierMetadata,
    is_tier_at_or_above,
    tier_metadata,
)
from harness_as.secret_fetch import (
    TIER_RESOLUTION_TABLE,
    SecretRef,
    SecretResolutionMechanism,
    SecretScope,
    TierResolutionMechanism,
    TPerm2Pole,
    fetch_secret,
    tier_resolution_mechanism,
)

__all__ = [
    "TIER_RESOLUTION_TABLE",
    "BlastRadiusTier",
    "C5FailClass",
    "C9RetryPosture",
    "ClassCardinality",
    "DeploymentSurface",
    "ForcedTierCause",
    "ForcedTierResult",
    "MCPTransport",
    "MechanismClass",
    "OverrideScopeResult",
    "PersonaTier",
    "ProviderClassMetadata",
    "SandboxFailClass",
    "SandboxFailClassMetadata",
    "SandboxProviderClass",
    "SandboxTier",
    "SandboxTierMetadata",
    "SecretRef",
    "SecretResolutionMechanism",
    "SecretScope",
    "TPerm2Pole",
    "TierResolutionMechanism",
    "ToolContext",
    "blast_radius_floor",
    "fail_class_metadata",
    "fetch_secret",
    "forced_tier",
    "is_tier_at_or_above",
    "override_scope",
    "permanent_fail_skips_staircase",
    "provider_class_metadata",
    "tier_metadata",
    "tier_resolution_mechanism",
]

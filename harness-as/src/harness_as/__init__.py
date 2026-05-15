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

__all__ = [
    "BlastRadiusTier",
    "C5FailClass",
    "C9RetryPosture",
    "ClassCardinality",
    "DeploymentSurface",
    "ForcedTierCause",
    "ForcedTierResult",
    "MCPTransport",
    "MechanismClass",
    "PersonaTier",
    "ProviderClassMetadata",
    "SandboxFailClass",
    "SandboxFailClassMetadata",
    "SandboxProviderClass",
    "SandboxTier",
    "SandboxTierMetadata",
    "ToolContext",
    "blast_radius_floor",
    "fail_class_metadata",
    "forced_tier",
    "is_tier_at_or_above",
    "permanent_fail_skips_staircase",
    "provider_class_metadata",
    "tier_metadata",
]

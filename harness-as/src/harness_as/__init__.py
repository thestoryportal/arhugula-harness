"""harness-as — Action Surface (AS) axis.

Public API re-exports. Authority: harness-as/CLAUDE.md; AS plan v1.
"""

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
    "DeploymentSurface",
    "ForcedTierCause",
    "ForcedTierResult",
    "MCPTransport",
    "MechanismClass",
    "PersonaTier",
    "SandboxFailClass",
    "SandboxFailClassMetadata",
    "SandboxTier",
    "SandboxTierMetadata",
    "ToolContext",
    "fail_class_metadata",
    "forced_tier",
    "is_tier_at_or_above",
    "permanent_fail_skips_staircase",
    "tier_metadata",
]

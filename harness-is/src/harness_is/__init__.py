"""harness-is — Information Substrate (IS) axis.

Public API re-exports. Authority: harness-is/CLAUDE.md; IS plan v2.2.
"""

from harness_is.artifact_tier_registry import (
    ARTIFACT_TIER_REGISTRY,
    ArtifactTier,
    ArtifactTierMetadata,
    SubstrateResidence,
    SurvivalScope,
)
from harness_is.path_binding import (
    DeploymentSurface,
    PathBinding,
    PathBindingDuplicateError,
    PathBindingEntry,
    WorkflowClass,
    load_path_binding,
)
from harness_is.path_class_registry import (
    PATH_CLASS_REGISTRY,
    PathClass,
    PathClassMetadata,
    ResidenceContract,
    StabilityInvariant,
    VisibilitySurface,
)
from harness_is.path_resolver import PathBindingMissingError, PathResolver

__all__ = [
    "ARTIFACT_TIER_REGISTRY",
    "PATH_CLASS_REGISTRY",
    "ArtifactTier",
    "ArtifactTierMetadata",
    "DeploymentSurface",
    "PathBinding",
    "PathBindingDuplicateError",
    "PathBindingEntry",
    "PathBindingMissingError",
    "PathClass",
    "PathClassMetadata",
    "PathResolver",
    "ResidenceContract",
    "StabilityInvariant",
    "SubstrateResidence",
    "SurvivalScope",
    "VisibilitySurface",
    "WorkflowClass",
    "load_path_binding",
]

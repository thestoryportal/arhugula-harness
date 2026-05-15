"""harness-is — Information Substrate (IS) axis.

Public API re-exports. Authority: harness-is/CLAUDE.md; IS plan v2.2.
"""

from harness_is.path_class_registry import (
    PATH_CLASS_REGISTRY,
    PathClass,
    PathClassMetadata,
    ResidenceContract,
    StabilityInvariant,
    VisibilitySurface,
)

__all__ = [
    "PATH_CLASS_REGISTRY",
    "PathClass",
    "PathClassMetadata",
    "ResidenceContract",
    "StabilityInvariant",
    "VisibilitySurface",
]

"""Path-binding configuration + loader — U-IS-02 (`path-binding-loader`).

Implements C-IS-01 §1 (canonical filesystem path contract). Supplies the
implementation-time path-binding configuration consumed by the path
resolver: canonical path strings per `(path_class, workflow_class,
deployment_surface)` cell.

Authority: Implementation_Plan_Information_Substrate_v2_1.md §2 U-IS-02
(preserved verbatim at v2.2); Spec_Information_Substrate_v1.md §1 C-IS-01
("Deferred to implementation discretion: specific canonical path strings
per workflow class per deployment-surface cell").

Resolution of a U-IS-02 under-specification: the U-IS-02 signature names
`WorkflowClass` and `DeploymentSurface` types without defining them. The
U-IS-02 `Inputs` field describes them as a "workflow class identifier" and
"deployment surface identifier" — keys into this configuration, not the
CP-axis workflow-class taxonomy (H_T-CP-11, owned by CP). They are modelled
here as opaque string identifiers; IS does not own the taxonomy, so U-IS-02
declares no cross-axis dependency (X-AL-3 — no silent design extension).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import NewType

from pydantic import BaseModel, ConfigDict

from harness_is.path_class_registry import PathClass

WorkflowClass = NewType("WorkflowClass", str)
"""Opaque workflow-class identifier — a path-binding lookup key."""

DeploymentSurface = NewType("DeploymentSurface", str)
"""Opaque deployment-surface identifier — a path-binding lookup key."""


class PathBindingEntry(BaseModel):
    """One canonical-path binding for a `(class, workflow, surface)` cell."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path_class: PathClass
    workflow_class: WorkflowClass
    deployment_surface: DeploymentSurface
    path: str
    """Canonical path string for this cell (implementation-time discretion)."""


class PathBindingDuplicateError(ValueError):
    """Raised when the binding config declares a triple more than once."""


class PathBinding(BaseModel):
    """Validated path-binding configuration — the resolver's only path source."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entries: tuple[PathBindingEntry, ...]


def load_path_binding(raw_entries: Iterable[Mapping[str, object]]) -> PathBinding:
    """Build a validated `PathBinding` from raw configuration records.

    Each raw record is validated into a `PathBindingEntry`. Duplicate
    `(path_class, workflow_class, deployment_surface)` triples are rejected
    — a single triple must bind to exactly one path for the resolver's
    stability invariant (U-IS-02 acceptance #1/#2) to hold.
    """
    entries = tuple(PathBindingEntry.model_validate(record) for record in raw_entries)
    seen: set[tuple[PathClass, str, str]] = set()
    for entry in entries:
        triple = (entry.path_class, entry.workflow_class, entry.deployment_surface)
        if triple in seen:
            raise PathBindingDuplicateError(f"duplicate path binding for triple {triple!r}")
        seen.add(triple)
    return PathBinding(entries=entries)

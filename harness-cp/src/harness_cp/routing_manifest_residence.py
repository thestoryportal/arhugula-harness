"""Routing manifest residence + schema + `RetryPolicy` record — U-CP-04.

Implements C-CP-01 §1.3 (the routing-manifest schema + canonical residence)
and — per the Implementation Plan v2.9 factor-out delta — C-CP-03 §3.5 (the
`RetryPolicy` record, a faithful factor-out of the `retry.*` namespace
`retry.policy` full-jitter-default vocabulary).

PARTIAL-LAND (v2.9 §0.5). `RetryPolicy`, `manifest_version`,
`fallback_chains`, and `retry_policies` materialize. The two `RoutingManifest`
`Map` fields `per_role_bindings` / `per_workload_overrides` have value-types
(`RoleRoutingBinding` / `WorkloadRoutingOverride`) that are NOT T2-covered and
genuinely uncommitted (C-CP-06 §6.1 does not decompose them; C-CP-01 §1.3
gives prose grain only). They are a forward Class 1 carry per
`.harness/class_1_tension_role_routing_binding_underspec.md` — landed here with
their value-type as a deferred opaque placeholder. No `RoleRoutingBinding` /
`WorkloadRoutingOverride` field set is invented.

`ToolName` (the `retry_policies` map key) is the AS-owned tool-name concept;
no `ToolName` NewType is landed in `harness_as` — the spec treats tool names as
plain strings (`ToolContract.name: str`), so the key type is `str` (a faithful
materialization; a future AS `ToolName` NewType is a `str` alias). See the
Class 3 note at `.harness/phase-7-progress.md`.

Authority: Implementation_Plan_Control_Plane_v2_9.md §2A U-CP-04 (revised body
— `RetryPolicy` factor-out; partial-land); Spec_Control_Plane_v1_3.md §1
C-CP-01 §1.3; §3 C-CP-03 §3 + §3.5 `retry.*` namespace; CLAUDE.md §3.2
(hand-rolled retry — NO tenacity/pybreaker).
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from harness_core import DeploymentSurface, WorkloadClass
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import AgentRole
from harness_cp.cross_family_fallback_chain import FallbackChain

# --- Class 1 carry — opaque placeholders ------------------------------------
# `RoleRoutingBinding` / `WorkloadRoutingOverride` field sets are genuinely
# uncommitted (v2.9 §0.5; `.harness/class_1_tension_role_routing_binding_
# underspec.md`). They are NOT T2 factor-out candidates. The two `Map` fields
# land with their value-type as a deferred opaque placeholder — inventing a
# field set would be an X-AL-3 design extension. Resolution awaits the Class 1
# record's operator decision.
type RoleRoutingBinding = Mapping[str, Any]
type WorkloadRoutingOverride = Mapping[str, Any]


class RetryPolicy(BaseModel):
    """A retry policy — faithful factor-out of C-CP-03 §3.5 `retry.policy`.

    The `retry.*` namespace `retry.policy` attribute commits a "full-jitter
    default per Cluster 4 §2.2.7 [HIGH]". Hand-rolled retry per CLAUDE.md §3.2
    — NO tenacity/pybreaker. Exactly three fields; no field invented beyond the
    §3.5 retry-policy vocabulary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_attempts: int
    """Retry-attempt cap per C-CP-03 §3 chain-advancement."""

    backoff: str
    """Backoff-strategy token; "full-jitter" default per C-CP-03 §3.5."""

    jitter: str
    """Jitter-mode token; composes with `backoff`."""


class RoutingManifest(BaseModel):
    """The routing manifest — canonical role x workload model-binding source.

    Exactly five top-level fields per C-CP-01 §1.3 + cross-references to
    C-CP-03 §3.5 + C-CP-04 §4.1. `per_role_bindings` / `per_workload_overrides`
    value-types are a Class 1 carry (opaque placeholders — see module
    docstring)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest_version: int
    per_role_bindings: Mapping[AgentRole, RoleRoutingBinding]
    """Class 1 carry — value-type is an opaque placeholder (v2.9 §0.5)."""

    per_workload_overrides: Mapping[WorkloadClass, WorkloadRoutingOverride]
    """Class 1 carry — value-type is an opaque placeholder (v2.9 §0.5)."""

    fallback_chains: tuple[FallbackChain, ...]
    """Populated per C-CP-04 (U-CP-09 `FallbackChain`)."""

    retry_policies: Mapping[str, RetryPolicy]
    """Per-tool retry policies, keyed by tool name; populated per C-CP-03 §3.5."""


class RoutingManifestValidationError(BaseModel):
    """A routing-manifest validation failure."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    reason: str


def validate_routing_manifest(
    manifest: RoutingManifest,
) -> RoutingManifestValidationError | None:
    """Validate a routing manifest; return `None` if valid, else the error.

    Structural validation: `manifest_version` must be positive. Per-role
    model-presence checks against the U-AS-29 model-binding catalog are a
    cross-axis runtime check (acceptance #3, runtime-deferred). Deterministic."""
    if manifest.manifest_version < 1:
        return RoutingManifestValidationError(
            reason="manifest_version must be a positive integer"
        )
    return None


def resolve_manifest_residence_path(
    resolver: PathResolver,
    workload_class: WorkloadClass,
    deployment_surface: DeploymentSurface,
) -> Path:
    """Resolve the canonical routing-manifest residence path.

    Delegates to the U-IS-02 `PathResolver` against the U-IS-01 `PathClass`;
    per-deployment-surface residence is the resolver's `deployment_surface`
    dimension (acceptance #2). The manifest resides under the `PROMPTS`
    path-class (operator-authored configuration)."""
    return resolver.resolve_path(
        PathClass.PROMPTS, workload_class, deployment_surface
    )


def load_routing_manifest(raw: Mapping[str, Any]) -> RoutingManifest:
    """Load a routing manifest from a parsed configuration mapping.

    The concrete on-disk format (JSON vs YAML vs TOML) is deferred to
    implementation discretion per C-CP-01 §1.3; this function consumes the
    already-parsed mapping and validates it against the `RoutingManifest`
    schema."""
    return RoutingManifest.model_validate(raw)

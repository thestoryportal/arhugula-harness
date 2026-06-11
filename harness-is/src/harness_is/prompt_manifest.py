"""Prompts-management carrier — `PromptManifest` + `PromptVersion`.

Implements the runtime-binding substrate for the **third procedural-tier
content-hash component** named — and deferred — at
``Spec_Information_Substrate_v1.md`` §C-IS-05 §5.2 ("Prompts component
deferred at v1.3"). The v1.5 amendment (post-MVP closure R-CL-P4; fork
``.harness/class_1_fork_prompts_management_surface_active_prompt_version.md``,
operator-ratified 2026-06-11) authors this carrier and widens the resolver
recipe from two components to three.

Design — mirror the `RoutingManifest` precedent exactly. The §5.2 v1.3
Deferral footer named three preconditions for the future component:

  1. runtime spec authors ``active_prompt_version: PromptVersion`` at
     ``HarnessContext``;
  2. a ``PromptManifest`` carrier lands homing prompt-version metadata;
  3. the prompts-management surface authors operational read-access to the
     active prompt version at write-time.

All three are bound by a single ``HarnessContext.prompt_manifest:
PromptManifest`` field (the carrier lives on the context; the resolver reads
the carrier-homed ``active_prompt_version`` at write-time) — the exact shape
of ``HarnessContext.routing_manifest`` + ``routing_manifest_sha``. This unifies
the two named preconditions into the routing-precedent shape rather than two
parallel context fields:

  * ``PromptVersion`` authored + active-version read-access ............ (1)
  * ``PromptManifest`` carrier landed ................................. (2)
  * resolver reads ``ctx.prompt_manifest.active_prompt_version`` ...... (3)

Both models are frozen + ``extra="forbid"``, mirroring ``RoutingManifest``.
The carrier is empty-defaultable at ``HarnessContext`` (``version_sha=""`` →
no active prompt) so operators that do not version prompts carry zero config
burden — the routing-manifest ``default_factory`` precedent. The fuller
prompts-management surface (multi-prompt versioning + selection UX) is a
separate forward arc per fork DP-4; this unit closes only the §5.2 hash-
component deferral.

Authority: ``Spec_Information_Substrate_v1.md`` v1.5 §C-IS-05 §5.2 (NEW
3-component recipe + preconditions (1)-(3)); ``Spec_Harness_Runtime_v1.md``
§14.18 (``active_prompt_version`` runtime binding); ADR-F2 §Consequences (c)
(D-derivative entry-shape extension authorization, inherited via §5.1 sidecar).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

__all__ = [
    "PromptManifest",
    "PromptVersion",
]


class PromptVersion(BaseModel):
    """The active prompt version identity — the §5.2 third hash-component input.

    Mirrors the per-Skill ``version_sha`` shape that feeds ``active_skills_versions``:
    a single content digest naming the active prompt version in scope at an
    entry's write-time. ``version_sha=""`` is the empty-carrier sentinel (no
    active prompt; the default-constructed manifest), contributing a stable
    empty value to the recipe.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    version_sha: str
    """Content digest of the active prompt version; ``""`` = no active prompt."""


class PromptManifest(BaseModel):
    """Prompts-management carrier — homes prompt-version metadata (§5.2 precondition 2).

    Mirrors ``RoutingManifest`` (frozen + ``extra="forbid"``; a ``manifest_version``
    plus content). Lives on ``HarnessContext`` as the operator-supplied,
    empty-defaultable substrate; the resolver reads ``active_prompt_version``
    from it at write-time for the procedural-tier content hash.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest_version: int
    """Manifest schema version (mirrors ``RoutingManifest.manifest_version``)."""

    active_prompt_version: PromptVersion
    """The active prompt version read by ``resolve_procedural_tier_snapshot`` at
    write-time (§5.2 recipe component ``active_prompt_version``)."""

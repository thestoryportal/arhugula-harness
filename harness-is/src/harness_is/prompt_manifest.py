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

R-PM-1 cascade PR #1 (IS spec v1.6 §C-IS-05 §5.2 provenance-tightening): the
minimal inline ``PromptVersion.content`` carrier + the ``version_sha ==
prompt_version_sha(content)`` derive-invariant. The §5.2 recipe *shape* is
unchanged (still 3-component, still reads ``active_prompt_version.version_sha``);
only ``version_sha``'s *provenance* tightens to a content-derived digest so
runtime injection (runtime spec v1.44) and the procedural-tier hash cannot
disagree about what content is active.
"""

from __future__ import annotations

import hashlib
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, model_validator

__all__ = [
    "PromptManifest",
    "PromptVersion",
    "prompt_version_sha",
]


def prompt_version_sha(content: str) -> str:
    """Content-addressed digest of a prompt version — the single source of the sha.

    R-PM-1 cascade PR #1 (runtime injection). The active prompt's
    ``version_sha`` MUST be derived from its ``content`` so the C-IS-05 §5.2
    procedural-tier content hash cannot report "unchanged" while injected
    content changes (a silent provenance/replay-integrity gap). Empty content
    maps to the empty-carrier sentinel ``""`` (no active prompt → no injection
    → a stable empty value in the §5.2 recipe — the #496 behavior preserved
    verbatim). Non-empty content maps to its hex SHA-256 digest.
    """
    if not content:
        return ""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class PromptVersion(BaseModel):
    """The active prompt version — identity (``version_sha``) + inline ``content``.

    Mirrors the per-Skill ``version_sha`` shape that feeds ``active_skills_versions``:
    a single content digest naming the active prompt version in scope at an
    entry's write-time. ``version_sha=""`` is the empty-carrier sentinel (no
    active prompt; the default-constructed manifest), contributing a stable
    empty value to the recipe.

    R-PM-1 cascade PR #1 adds the minimal inline ``content`` carrier so a single
    operator-supplied active prompt injects + proves e2e within PR #1 (the
    self-contained content source; PR #2 generalizes this to the multi-version
    ``PROMPTS``-path-class store). The ``content`` ↔ ``version_sha`` derive-
    invariant (``version_sha == prompt_version_sha(content)``) is enforced at
    construction (detect-then-refuse): the sha is not an independent operator-set
    field. Use :meth:`from_content` for ergonomic authoring.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    version_sha: str = ""
    """Content digest of the active prompt version; ``""`` = no active prompt.

    Derived from ``content`` — operators supply ``content`` (e.g. declaratively
    via TOML/JSON ``RuntimeConfig.prompt_manifest``) and the sha is filled in
    (the sha is not an independent operator-set field). An *explicitly-supplied*
    non-empty ``version_sha`` MUST equal ``prompt_version_sha(content)``
    (detect-then-refuse at construction)."""

    content: str = ""
    """Inline system-prompt content (R-PM-1 PR #1 minimal carrier). ``""`` = no
    active prompt (the empty-carrier sentinel; forward-compatible with the
    #496 identity-only construction ``PromptVersion(version_sha="")``)."""

    @model_validator(mode="before")
    @classmethod
    def _derive_sha_when_absent(cls, data: Any) -> Any:
        """Fill ``version_sha`` from ``content`` when it is absent/empty — the
        operator-supplied declarative path (`PromptVersion(content="...")` /
        TOML/JSON), where the operator naturally supplies content but not a
        precomputed digest. An *explicit* non-empty ``version_sha`` is left
        untouched so the after-validator can detect-then-refuse a mismatch.
        """
        if not isinstance(data, dict):
            return data
        raw: dict[str, Any] = dict(cast("dict[str, Any]", data))
        if not raw.get("version_sha"):
            raw["version_sha"] = prompt_version_sha(str(raw.get("content") or ""))
        return raw

    @model_validator(mode="after")
    def _enforce_content_sha_invariant(self) -> PromptVersion:
        """Detect-then-refuse a mismatched explicit ``version_sha``.

        Construction-time only — Pydantic does not re-run ``mode="after"`` on
        ``model_copy(update=...)``, so a caller that ``model_copy``s a
        ``PromptVersion`` to mutate ``content`` would bypass the invariant. No
        current caller does this (the carrier is frozen + empty-defaultable, and
        configs copy the *config*, not the carrier); the PR #2 versioning store
        is where any mutation path would be introduced and must re-derive.
        """
        expected = prompt_version_sha(self.content)
        if self.version_sha != expected:
            raise ValueError(
                "PromptVersion.version_sha must equal prompt_version_sha(content) "
                f"(got version_sha={self.version_sha!r}, "
                f"expected {expected!r} for the supplied content)"
            )
        return self

    @classmethod
    def from_content(cls, content: str) -> PromptVersion:
        """Construct from content alone, deriving ``version_sha`` (authoring helper)."""
        return cls(version_sha=prompt_version_sha(content), content=content)


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

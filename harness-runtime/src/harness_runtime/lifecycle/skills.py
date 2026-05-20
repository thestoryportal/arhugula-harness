"""U-RT-13 — Skills filesystem load.

Per `Spec_Harness_Runtime_v1.md` v1.1 §4 (C-RT-04 `skills` field:
`dict[SkillID, Skill]`) and Phase 2 Session 3 plan v2.1 §2 L3 U-RT-13.

Class 2 Protocol-stub concretization: the L0 Tension record authorized
the runtime to define `Skill` since AS shipped skill-validation primitives
(`validate_skill_attributes_carry_both_version_fields`) but no data class.

Manifest schema is runtime implementation-discretion per the same pattern
AS C-AS-05 §5.4 sets (keyring-library binding "deferred to implementation
discretion"). The minimal `SkillManifest` is:

    {
        "skill_id": "my-skill",
        "name": "human label",
        "description": "what it does",
        "version": "1.0",
    }

Stored on disk as `<skill_id>.skill.json` under `PATH_CLASS_REGISTRY[SKILLS]`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from harness_core import SkillID
from pydantic import BaseModel, ConfigDict

__all__ = [
    "DuplicateSkillError",
    "Skill",
    "SkillManifest",
    "load_skills_from_dir",
]


class SkillManifest(BaseModel):
    """Runtime-defined skill manifest schema (U-RT-13 implementation discretion)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    skill_id: SkillID
    name: str
    description: str
    version: str


@dataclass(frozen=True)
class Skill:
    """A loaded skill — manifest + the filesystem path it loaded from."""

    manifest: SkillManifest
    source_path: Path


class DuplicateSkillError(ValueError):
    """Raised when two manifest files declare the same `skill_id`."""

    def __init__(self, skill_id: SkillID, paths: tuple[Path, Path]) -> None:
        super().__init__(
            f"duplicate skill_id {skill_id!r}: {paths[0]} and {paths[1]}",
        )
        self.skill_id = skill_id
        self.paths = paths


def load_skills_from_dir(skills_dir: Path) -> dict[SkillID, Skill]:
    """Load all `*.skill.json` manifests under `skills_dir`.

    Per AC: 'all skills under PathClass.SKILLS loaded; duplicate IDs rejected;
    manifest schema enforced.'

    Parameters
    ----------
    skills_dir :
        Resolved PathClass.SKILLS directory from U-RT-10.

    Returns
    -------
    dict[SkillID, Skill]
        Indexed by skill_id; iteration order is filesystem-glob order.

    Raises
    ------
    DuplicateSkillError
        Two manifests declare the same `skill_id`.
    pydantic.ValidationError
        A manifest file fails schema validation (`extra='forbid'`, missing
        required field, wrong type).
    """
    skills: dict[SkillID, Skill] = {}
    path_index: dict[SkillID, Path] = {}

    for manifest_path in sorted(_walk_manifests(skills_dir)):
        raw = manifest_path.read_text(encoding="utf-8")
        manifest = SkillManifest.model_validate_json(raw)
        prior = path_index.get(manifest.skill_id)
        if prior is not None:
            raise DuplicateSkillError(manifest.skill_id, (prior, manifest_path))
        path_index[manifest.skill_id] = manifest_path
        skills[manifest.skill_id] = Skill(manifest=manifest, source_path=manifest_path)

    return skills


def _walk_manifests(skills_dir: Path) -> Iterable[Path]:
    """Yield `*.skill.json` files under `skills_dir` (non-recursive)."""
    if not skills_dir.exists():
        return
    yield from skills_dir.glob("*.skill.json")

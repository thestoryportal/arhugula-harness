"""U-RT-13 — Skills filesystem load (extended at v1.32 / U-RT-99 plan v2.28;
skill content at v1.139 §14.17.8.1).

Per ``Spec_Harness_Runtime_v1.md`` v1.32 §4 (C-RT-04 ``skills`` field:
``dict[SkillID, Skill]``) + §14.17.5 invariant 7 (``version_sha`` +
``body_tokens`` computed at load).

v1.139 binds each manifest ``<stem>.skill.json`` to its content file
``<stem>.SKILL.md``: the loaded ``Skill`` carries the content, and
``version_sha`` / ``body_tokens`` derive from the content bytes, not from the
manifest.

The original ``SkillManifest`` at v1.1 carried 4 fields (``skill_id`` / ``name``
/ ``description`` / ``version``). v1.32 extends with 2 derived fields:

* ``version_sha`` — git blob hash of the content file (byte-exact identical to
  ``git hash-object <stem>.SKILL.md``) per AS spec v1.7 §14.4 + §14.17.7.
* ``body_tokens`` — ``len(content) // 4`` per the §14.17.7 default heuristic.

Stored on disk as ``<stem>.skill.json`` + ``<stem>.SKILL.md`` under
``PATH_CLASS_REGISTRY[SKILLS]``. The manifest JSON MAY pin ``version_sha``
(it must then equal the content digest); a supplied ``body_tokens`` is
ignored and recomputed.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from harness_as import SkillFrontmatterRejectionReason, validate_skill_frontmatter
from harness_core import SkillID
from pydantic import BaseModel, ConfigDict

__all__ = [
    "DuplicateSkillError",
    "Skill",
    "SkillContentInvalidError",
    "SkillContentInvalidReason",
    "SkillFrontmatterRejectedError",
    "SkillManifest",
    "compute_git_blob_sha",
    "load_skills_from_dir",
]


class SkillManifest(BaseModel):
    """Runtime-defined skill manifest schema.

    Extended at v1.32 with ``version_sha`` + ``body_tokens`` fields per
    runtime spec §14.17.5 invariant 7 — both computed at load when not
    supplied in the manifest JSON.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    skill_id: SkillID
    name: str
    description: str
    version: str
    # Derived at load from the content bytes (v1.139 §14.17.8.1 items 3-4).
    version_sha: str
    body_tokens: int


class _ManifestFile(BaseModel):
    """The on-disk manifest JSON, before content binding.

    ``version_sha`` is an optional pin that must equal the content digest;
    ``body_tokens`` is accepted for compatibility and always recomputed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    skill_id: SkillID
    name: str
    description: str
    version: str
    version_sha: str | None = None
    body_tokens: int | None = None


@dataclass(frozen=True)
class Skill:
    """A loaded skill — manifest, its content and the manifest path it loaded from.

    ``content`` is the complete text of ``<stem>.SKILL.md`` read once at load;
    ``manifest.version_sha`` is the git blob SHA of exactly those bytes.
    """

    manifest: SkillManifest
    source_path: Path
    content: str


class SkillContentInvalidReason(StrEnum):
    """Closed reasons for ``RT-FAIL-SKILL-CONTENT-INVALID`` (v1.139 §14.17.8.3)."""

    CONTENT_MISSING = "content-missing"
    CONTENT_UNREADABLE = "content-unreadable"
    CONTENT_NOT_UTF8 = "content-not-utf8"
    CONTENT_EMPTY = "content-empty"
    VERSION_SHA_MISMATCH = "version-sha-mismatch"


class SkillContentInvalidError(ValueError):
    """A skill's content file cannot be delivered; bootstrap stage 2 aborts.

    Maps to ``RT-FAIL-SKILL-CONTENT-INVALID`` (v1.139 §14.17.8.3).
    """

    rt_fail_class = "RT-FAIL-SKILL-CONTENT-INVALID"

    def __init__(
        self,
        skill_id: SkillID,
        content_path: Path,
        reason: SkillContentInvalidReason,
    ) -> None:
        super().__init__(
            f"skill {skill_id!r} content {content_path} rejected: {reason.value}",
        )
        self.skill_id = skill_id
        self.content_path = content_path
        self.reason = reason


class DuplicateSkillError(ValueError):
    """Raised when two manifest files declare the same `skill_id`."""

    def __init__(self, skill_id: SkillID, paths: tuple[Path, Path]) -> None:
        super().__init__(
            f"duplicate skill_id {skill_id!r}: {paths[0]} and {paths[1]}",
        )
        self.skill_id = skill_id
        self.paths = paths


class SkillFrontmatterRejectedError(ValueError):
    """Raised when a manifest violates a committed SKILL.md frontmatter
    constraint (B-SKILL-FRONTMATTER-VALIDATOR; ADR-D3 §Rationale + §1.8.1:331).
    """

    def __init__(
        self,
        skill_id: SkillID,
        path: Path,
        reason: SkillFrontmatterRejectionReason,
    ) -> None:
        super().__init__(
            f"skill {skill_id!r} at {path} rejected: {reason.value}",
        )
        self.skill_id = skill_id
        self.path = path
        self.reason = reason


def compute_git_blob_sha(content: bytes) -> str:
    """Compute the git blob SHA-1 hash for ``content``.

    Byte-exact identical to ``git hash-object <file>`` output. Per spec
    §14.17.7 deferred-discretion default mechanism (canonical git-blob
    byte sequence: ``b"blob " + len + b"\\0" + content`` SHA-1'd).
    """
    header = f"blob {len(content)}".encode("ascii") + b"\0"
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


_MANIFEST_SUFFIX = ".skill.json"
_CONTENT_SUFFIX = ".SKILL.md"


def load_skills_from_dir(skills_dir: Path) -> dict[SkillID, Skill]:
    """Load all ``*.skill.json`` manifests and their content under ``skills_dir``.

    Each manifest binds to the sibling ``<stem>.SKILL.md`` content file
    (v1.139 §14.17.8.1). ``version_sha`` is the content's git blob SHA and
    ``body_tokens`` is ``len(content) // 4``.

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
        Two manifests declare the same ``skill_id``.
    SkillContentInvalidError
        A content file is missing, unreadable, not UTF-8, blank, or its
        digest differs from a manifest-pinned ``version_sha``.
    SkillFrontmatterRejectedError
        A manifest violates a committed SKILL.md frontmatter constraint
        (name/description length, missing version/version_sha).
    pydantic.ValidationError
        A manifest file fails schema validation.
    """
    skills: dict[SkillID, Skill] = {}
    path_index: dict[SkillID, Path] = {}

    for manifest_path in sorted(_walk_manifests(skills_dir)):
        manifest_file = _ManifestFile.model_validate(json.loads(manifest_path.read_bytes()))
        content_path = manifest_path.with_name(
            manifest_path.name.removesuffix(_MANIFEST_SUFFIX) + _CONTENT_SUFFIX
        )
        content_bytes, content = _read_content(manifest_file.skill_id, content_path)
        version_sha = compute_git_blob_sha(content_bytes)
        # [LAW:one-source-of-truth] the digest of the delivered bytes is the version;
        # a manifest value is only a pin that must agree with it.
        if manifest_file.version_sha not in (None, version_sha):
            raise SkillContentInvalidError(
                manifest_file.skill_id,
                content_path,
                SkillContentInvalidReason.VERSION_SHA_MISMATCH,
            )
        manifest = SkillManifest(
            skill_id=manifest_file.skill_id,
            name=manifest_file.name,
            description=manifest_file.description,
            version=manifest_file.version,
            version_sha=version_sha,
            body_tokens=len(content) // 4,
        )
        validation = validate_skill_frontmatter(
            name=manifest.name,
            description=manifest.description,
            version=manifest.version,
            version_sha=manifest.version_sha,
        )
        if validation.outcome is not SkillFrontmatterRejectionReason.VALID:
            raise SkillFrontmatterRejectedError(
                manifest.skill_id,
                manifest_path,
                validation.outcome,
            )
        prior = path_index.get(manifest.skill_id)
        if prior is not None:
            raise DuplicateSkillError(manifest.skill_id, (prior, manifest_path))
        path_index[manifest.skill_id] = manifest_path
        skills[manifest.skill_id] = Skill(
            manifest=manifest,
            source_path=manifest_path,
            content=content,
        )

    return skills


def _read_content(skill_id: SkillID, content_path: Path) -> tuple[bytes, str]:
    """Read ``content_path`` as deliverable skill content: its bytes and UTF-8 text.

    [LAW:parse-dont-validate] the one crossing from the filesystem; every
    failure leaves as a ``SkillContentInvalidError`` with a closed reason.
    """
    try:
        content_bytes = content_path.read_bytes()
    except FileNotFoundError as exc:
        raise SkillContentInvalidError(
            skill_id, content_path, SkillContentInvalidReason.CONTENT_MISSING
        ) from exc
    except OSError as exc:
        raise SkillContentInvalidError(
            skill_id, content_path, SkillContentInvalidReason.CONTENT_UNREADABLE
        ) from exc
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SkillContentInvalidError(
            skill_id, content_path, SkillContentInvalidReason.CONTENT_NOT_UTF8
        ) from exc
    if not content.strip():
        raise SkillContentInvalidError(
            skill_id, content_path, SkillContentInvalidReason.CONTENT_EMPTY
        )
    return content_bytes, content


def _walk_manifests(skills_dir: Path) -> Iterable[Path]:
    """Yield `*.skill.json` files under `skills_dir` (non-recursive)."""
    if not skills_dir.exists():
        return
    yield from skills_dir.glob("*.skill.json")

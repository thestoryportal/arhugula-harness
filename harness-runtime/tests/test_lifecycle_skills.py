"""U-RT-13 — `load_skills_from_dir` tests.

ACs per Phase 2 Session 3 plan v2.1 §2 L3:
- All skills under PathClass.SKILLS loaded.
- Duplicate IDs rejected.
- Manifest schema enforced.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from harness_as.skill_frontmatter_validator import (
    SKILL_DESCRIPTION_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    SkillFrontmatterRejectionReason,
)
from harness_core import SkillID
from harness_runtime.lifecycle.skills import (
    DuplicateSkillError,
    Skill,
    SkillFrontmatterRejectedError,
    SkillManifest,
    load_skills_from_dir,
)
from pydantic import ValidationError


def _write_manifest(skills_dir: Path, skill_id: str, **overrides: object) -> Path:
    """Write a valid skill manifest to disk; return the file path."""
    skills_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "skill_id": skill_id,
        "name": f"Skill {skill_id}",
        "description": "test",
        "version": "1.0",
        **overrides,
    }
    path = skills_dir / f"{skill_id}.skill.json"
    path.write_text(json.dumps(manifest))
    return path


def test_empty_dir_returns_empty_dict(tmp_path: Path) -> None:
    """An empty PathClass.SKILLS dir → empty skills dict."""
    (tmp_path / "skills").mkdir()
    assert load_skills_from_dir(tmp_path / "skills") == {}


def test_absent_dir_returns_empty_dict(tmp_path: Path) -> None:
    """A missing PathClass.SKILLS dir → empty skills dict (no crash)."""
    assert load_skills_from_dir(tmp_path / "skills") == {}


def test_single_skill_loaded(tmp_path: Path) -> None:
    """One manifest file → one Skill entry indexed by skill_id."""
    _write_manifest(tmp_path / "skills", "my-skill")
    skills = load_skills_from_dir(tmp_path / "skills")
    assert len(skills) == 1
    skill = skills[SkillID("my-skill")]
    assert isinstance(skill, Skill)
    assert skill.manifest.skill_id == "my-skill"
    assert skill.manifest.name == "Skill my-skill"
    assert skill.manifest.version == "1.0"


def test_multiple_skills_loaded(tmp_path: Path) -> None:
    """Multiple manifests → multiple Skill entries (plan AC: all loaded)."""
    for skill_id in ["alpha", "beta", "gamma"]:
        _write_manifest(tmp_path / "skills", skill_id)
    skills = load_skills_from_dir(tmp_path / "skills")
    assert set(skills.keys()) == {SkillID("alpha"), SkillID("beta"), SkillID("gamma")}


def test_duplicate_skill_id_rejected(tmp_path: Path) -> None:
    """Two manifests with the same skill_id → `DuplicateSkillError`."""
    # Two files, both declaring skill_id='same' but with different filenames.
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "first.skill.json").write_text(
        json.dumps(
            {
                "skill_id": "same",
                "name": "First",
                "description": "x",
                "version": "1.0",
            },
        ),
    )
    (skills_dir / "second.skill.json").write_text(
        json.dumps(
            {
                "skill_id": "same",
                "name": "Second",
                "description": "y",
                "version": "1.0",
            },
        ),
    )
    with pytest.raises(DuplicateSkillError) as exc_info:
        load_skills_from_dir(skills_dir)
    assert exc_info.value.skill_id == SkillID("same")


def test_manifest_missing_field_rejected(tmp_path: Path) -> None:
    """Manifest missing a required field → `ValidationError`."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "broken.skill.json").write_text(
        json.dumps({"skill_id": "broken", "name": "x"}),  # no description / version
    )
    with pytest.raises(ValidationError):
        load_skills_from_dir(skills_dir)


def test_manifest_extra_field_rejected(tmp_path: Path) -> None:
    """`extra='forbid'` — unknown manifest fields raise `ValidationError`."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "extra.skill.json").write_text(
        json.dumps(
            {
                "skill_id": "extra",
                "name": "x",
                "description": "y",
                "version": "1.0",
                "unknown_field": "boom",
            },
        ),
    )
    with pytest.raises(ValidationError):
        load_skills_from_dir(skills_dir)


def test_non_skill_files_ignored(tmp_path: Path) -> None:
    """Files not matching `*.skill.json` are ignored."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_manifest(skills_dir, "real")
    (skills_dir / "README.md").write_text("not a skill")
    (skills_dir / "config.json").write_text('{"not": "a skill"}')
    skills = load_skills_from_dir(skills_dir)
    assert set(skills.keys()) == {SkillID("real")}


def test_skill_carries_source_path(tmp_path: Path) -> None:
    """`Skill.source_path` records the file the manifest came from."""
    manifest_path = _write_manifest(tmp_path / "skills", "traced")
    skills = load_skills_from_dir(tmp_path / "skills")
    assert skills[SkillID("traced")].source_path == manifest_path


def test_skill_is_frozen(tmp_path: Path) -> None:
    """`Skill` is a frozen dataclass."""
    _write_manifest(tmp_path / "skills", "frozen-test")
    skill = load_skills_from_dir(tmp_path / "skills")[SkillID("frozen-test")]
    with pytest.raises((AttributeError, Exception)):
        skill.source_path = Path("/")  # type: ignore[misc]


def test_skill_manifest_is_frozen() -> None:
    """`SkillManifest` is a frozen Pydantic model."""
    assert SkillManifest.model_config.get("frozen") is True


def test_load_rejects_name_too_long(tmp_path: Path) -> None:
    """B-SKILL-FRONTMATTER-VALIDATOR — wired at the real load path, not tests-only.

    A manifest with `name` over the committed 64-char ceiling (ADR-D3
    §Rationale) is rejected at `load_skills_from_dir`, not silently loaded.
    """
    _write_manifest(tmp_path / "skills", "too-long-name", name="x" * (SKILL_NAME_MAX_LENGTH + 1))
    with pytest.raises(SkillFrontmatterRejectedError) as exc_info:
        load_skills_from_dir(tmp_path / "skills")
    assert exc_info.value.reason is SkillFrontmatterRejectionReason.NAME_TOO_LONG


def test_load_rejects_empty_description(tmp_path: Path) -> None:
    """`description` empty (ADR-D3 §Rationale: non-empty) is rejected at load."""
    _write_manifest(tmp_path / "skills", "empty-desc", description="")
    with pytest.raises(SkillFrontmatterRejectedError) as exc_info:
        load_skills_from_dir(tmp_path / "skills")
    assert exc_info.value.reason is SkillFrontmatterRejectionReason.DESCRIPTION_EMPTY


def test_load_rejects_description_too_long(tmp_path: Path) -> None:
    """`description` over the committed 1024-char ceiling is rejected at load."""
    _write_manifest(
        tmp_path / "skills",
        "long-desc",
        description="x" * (SKILL_DESCRIPTION_MAX_LENGTH + 1),
    )
    with pytest.raises(SkillFrontmatterRejectedError) as exc_info:
        load_skills_from_dir(tmp_path / "skills")
    assert exc_info.value.reason is SkillFrontmatterRejectionReason.DESCRIPTION_TOO_LONG


def test_load_rejects_empty_version(tmp_path: Path) -> None:
    """`version` empty → MISSING_VERSION (ADR-D3 §1.8.1:331 — both required)."""
    _write_manifest(tmp_path / "skills", "empty-version", version="")
    with pytest.raises(SkillFrontmatterRejectedError) as exc_info:
        load_skills_from_dir(tmp_path / "skills")
    assert exc_info.value.reason is SkillFrontmatterRejectionReason.MISSING_VERSION


def test_load_rejects_empty_version_sha(tmp_path: Path) -> None:
    """`version_sha` empty → MISSING_VERSION_SHA (operator-supplied override to empty)."""
    _write_manifest(tmp_path / "skills", "empty-sha", version_sha="")
    with pytest.raises(SkillFrontmatterRejectedError) as exc_info:
        load_skills_from_dir(tmp_path / "skills")
    assert exc_info.value.reason is SkillFrontmatterRejectionReason.MISSING_VERSION_SHA


def test_load_accepts_valid_frontmatter(tmp_path: Path) -> None:
    """Accepted-fixture control — a manifest within every constraint still loads."""
    _write_manifest(tmp_path / "skills", "within-bounds")
    skills = load_skills_from_dir(tmp_path / "skills")
    assert SkillID("within-bounds") in skills

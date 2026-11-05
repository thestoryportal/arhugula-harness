"""U-RT-13 — `load_skills_from_dir` tests.

ACs per Phase 2 Session 3 plan v2.1 §2 L3:
- All skills under PathClass.SKILLS loaded.
- Duplicate IDs rejected.
- Manifest schema enforced.

Runtime v1.139 §14.17.8.5 W1 (content load + digest) and W2 (one typed load
failure per closed reason).
"""

from __future__ import annotations

import json
import os
import subprocess
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
    SkillContentInvalidError,
    SkillContentInvalidReason,
    SkillFrontmatterRejectedError,
    SkillManifest,
    load_skills_from_dir,
)
from pydantic import ValidationError


def _write_manifest(
    skills_dir: Path,
    skill_id: str,
    *,
    content: str | None = "# Skill body\n\nDo the thing.\n",
    **overrides: object,
) -> Path:
    """Write a valid skill manifest and its `<stem>.SKILL.md` content; return the manifest path.

    `content=None` writes the manifest alone.
    """
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
    if content is not None:
        (skills_dir / f"{skill_id}.SKILL.md").write_text(content, encoding="utf-8")
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
    (skills_dir / "first.SKILL.md").write_text("first body")
    (skills_dir / "second.SKILL.md").write_text("second body")
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


def test_load_rejects_empty_version_sha_pin(tmp_path: Path) -> None:
    """An operator-pinned empty `version_sha` disagrees with the content digest (v1.139)."""
    _write_manifest(tmp_path / "skills", "empty-sha", version_sha="")
    with pytest.raises(SkillContentInvalidError) as exc_info:
        load_skills_from_dir(tmp_path / "skills")
    assert exc_info.value.reason is SkillContentInvalidReason.VERSION_SHA_MISMATCH


def test_load_accepts_valid_frontmatter(tmp_path: Path) -> None:
    """Accepted-fixture control — a manifest within every constraint still loads."""
    _write_manifest(tmp_path / "skills", "within-bounds")
    skills = load_skills_from_dir(tmp_path / "skills")
    assert SkillID("within-bounds") in skills


# --- Runtime v1.139 §14.17.8.5 W1: content load + digest -------------------


def _git_hash_object(path: Path) -> str:
    return subprocess.run(
        ["git", "hash-object", str(path)], check=True, capture_output=True, text=True
    ).stdout.strip()


def test_w1_content_loads_with_digest_of_content_file(tmp_path: Path) -> None:
    """`content` is the SKILL.md text; `version_sha` is `git hash-object` of it, not the manifest."""
    content = "# Review\n\nCheck every seam. \u2014 ünïcode survives.\n"
    manifest_path = _write_manifest(tmp_path / "skills", "w1", content=content)
    content_path = tmp_path / "skills" / "w1.SKILL.md"

    skill = load_skills_from_dir(tmp_path / "skills")[SkillID("w1")]

    assert skill.content == content
    assert skill.manifest.version_sha == _git_hash_object(content_path)
    assert skill.manifest.version_sha != _git_hash_object(manifest_path)
    assert skill.manifest.body_tokens == len(content) // 4


def test_w1_matching_pin_loads_and_supplied_body_tokens_is_recomputed(tmp_path: Path) -> None:
    """A pin equal to the digest loads; a supplied `body_tokens` never survives."""
    content = "pinned body " * 10
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "pinned.SKILL.md").write_text(content)
    pin = _git_hash_object(skills_dir / "pinned.SKILL.md")
    _write_manifest(skills_dir, "pinned", content=content, version_sha=pin, body_tokens=999_999)

    skill = load_skills_from_dir(skills_dir)[SkillID("pinned")]

    assert skill.manifest.version_sha == pin
    assert skill.manifest.body_tokens == len(content) // 4


def test_w1_content_binds_by_manifest_stem_not_skill_id(tmp_path: Path) -> None:
    """The content file is `<stem>.SKILL.md` beside `<stem>.skill.json`, whatever the id."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "file-stem.skill.json").write_text(
        json.dumps({"skill_id": "other-id", "name": "n", "description": "d", "version": "1"})
    )
    (skills_dir / "file-stem.SKILL.md").write_text("stem-bound body")

    assert load_skills_from_dir(skills_dir)[SkillID("other-id")].content == "stem-bound body"


# --- Runtime v1.139 §14.17.8.5 W2: one typed failure per closed reason ------


def _assert_content_invalid(skills_dir: Path, reason: SkillContentInvalidReason) -> None:
    with pytest.raises(SkillContentInvalidError) as exc_info:
        load_skills_from_dir(skills_dir)
    err = exc_info.value
    assert err.reason is reason
    assert err.skill_id == SkillID("bad")
    assert err.content_path == skills_dir / "bad.SKILL.md"
    assert "'bad'" in str(err) and str(err.content_path) in str(err)
    assert err.rt_fail_class == "RT-FAIL-SKILL-CONTENT-INVALID"


def test_w2_missing_content(tmp_path: Path) -> None:
    _write_manifest(tmp_path / "skills", "bad", content=None)
    _assert_content_invalid(tmp_path / "skills", SkillContentInvalidReason.CONTENT_MISSING)


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads mode-000 files")
def test_w2_unreadable_content(tmp_path: Path) -> None:
    _write_manifest(tmp_path / "skills", "bad")
    content_path = tmp_path / "skills" / "bad.SKILL.md"
    content_path.chmod(0)
    try:
        _assert_content_invalid(tmp_path / "skills", SkillContentInvalidReason.CONTENT_UNREADABLE)
    finally:
        content_path.chmod(0o600)


def test_w2_invalid_utf8_content(tmp_path: Path) -> None:
    _write_manifest(tmp_path / "skills", "bad")
    (tmp_path / "skills" / "bad.SKILL.md").write_bytes(b"ok \xff\xfe not utf-8")
    _assert_content_invalid(tmp_path / "skills", SkillContentInvalidReason.CONTENT_NOT_UTF8)


def test_w2_whitespace_only_content(tmp_path: Path) -> None:
    _write_manifest(tmp_path / "skills", "bad", content=" \n\t\n ")
    _assert_content_invalid(tmp_path / "skills", SkillContentInvalidReason.CONTENT_EMPTY)


def test_w2_pinned_version_sha_mismatch(tmp_path: Path) -> None:
    _write_manifest(tmp_path / "skills", "bad", version_sha="0" * 40)
    _assert_content_invalid(tmp_path / "skills", SkillContentInvalidReason.VERSION_SHA_MISMATCH)

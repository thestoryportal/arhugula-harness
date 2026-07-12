"""Tests for B-SKILL-FRONTMATTER-VALIDATOR — SKILL.md frontmatter constraint
enforcement (ADR-D3 §Rationale + §1.8.1:331)."""

from __future__ import annotations

from harness_as.skill_frontmatter_validator import (
    SKILL_DESCRIPTION_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    SkillFrontmatterRejectionReason,
    validate_skill_frontmatter,
)


def _valid(**overrides: str) -> dict[str, str]:
    fields: dict[str, str] = {
        "name": "my-skill",
        "description": "a skill",
        "version": "1.0",
        "version_sha": "abc123",
    }
    fields.update(overrides)
    return fields


def test_valid_frontmatter_accepted() -> None:
    """The accepted-fixture control: every constraint satisfied → VALID."""
    result = validate_skill_frontmatter(**_valid())
    assert result.outcome is SkillFrontmatterRejectionReason.VALID


def test_name_at_max_length_accepted() -> None:
    """Boundary — name exactly at the 64-char ceiling is accepted."""
    result = validate_skill_frontmatter(**_valid(name="x" * SKILL_NAME_MAX_LENGTH))
    assert result.outcome is SkillFrontmatterRejectionReason.VALID


def test_name_too_long_rejected() -> None:
    """name > 64 chars → NAME_TOO_LONG (ADR-D3 §Rationale)."""
    result = validate_skill_frontmatter(**_valid(name="x" * (SKILL_NAME_MAX_LENGTH + 1)))
    assert result.outcome is SkillFrontmatterRejectionReason.NAME_TOO_LONG


def test_description_empty_rejected() -> None:
    """Empty description → DESCRIPTION_EMPTY (ADR-D3 §Rationale: non-empty)."""
    result = validate_skill_frontmatter(**_valid(description=""))
    assert result.outcome is SkillFrontmatterRejectionReason.DESCRIPTION_EMPTY


def test_description_at_max_length_accepted() -> None:
    """Boundary — description exactly at the 1024-char ceiling is accepted."""
    result = validate_skill_frontmatter(**_valid(description="x" * SKILL_DESCRIPTION_MAX_LENGTH))
    assert result.outcome is SkillFrontmatterRejectionReason.VALID


def test_description_too_long_rejected() -> None:
    """description > 1024 chars → DESCRIPTION_TOO_LONG."""
    result = validate_skill_frontmatter(
        **_valid(description="x" * (SKILL_DESCRIPTION_MAX_LENGTH + 1)),
    )
    assert result.outcome is SkillFrontmatterRejectionReason.DESCRIPTION_TOO_LONG


def test_missing_version_rejected() -> None:
    """Empty version → MISSING_VERSION (ADR-D3 §1.8.1:331 — both required)."""
    result = validate_skill_frontmatter(**_valid(version=""))
    assert result.outcome is SkillFrontmatterRejectionReason.MISSING_VERSION


def test_missing_version_sha_rejected() -> None:
    """Empty version_sha → MISSING_VERSION_SHA (ADR-D3 §1.8.1:331 — both required)."""
    result = validate_skill_frontmatter(**_valid(version_sha=""))
    assert result.outcome is SkillFrontmatterRejectionReason.MISSING_VERSION_SHA


def test_name_checked_before_description() -> None:
    """Precedence — a name violation is reported even when description also violates."""
    result = validate_skill_frontmatter(
        **_valid(name="x" * (SKILL_NAME_MAX_LENGTH + 1), description=""),
    )
    assert result.outcome is SkillFrontmatterRejectionReason.NAME_TOO_LONG

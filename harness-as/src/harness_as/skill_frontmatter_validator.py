"""SKILL.md frontmatter constraint enforcement — B-SKILL-FRONTMATTER-VALIDATOR.

Enforces the substrate-committed SKILL.md frontmatter constraints at the
skills filesystem-load seam: `name` <= 64 chars and non-empty `description`
<= 1024 chars per the Anthropic SKILL.md schema (ADR-D3 §Rationale, [HIGH]
cite: platform.claude.com/docs/en/agents-and-tools/agent-skills/overview);
`frontmatter.version` and `version_sha` both non-empty per ADR-D3 §1.8.1:331
(the `skill.version_sha` / `skill.frontmatter.version` semantic distinction —
both required, neither substitutes for the other).

Pure validation function mirroring `validate_tool_contract_at_registration`
(`tool_contract.py`) — a typed rejection-reason enum, checked in a fixed
precedence order, fail-closed on the first violation found.

Scope note: only the two substrate-committed constraints above are enforced.
The external agentskills.io extras (lowercase-alphanumeric names, reserved
words) are NOT committed in-substrate — enforcing them would be silent
design extension (X-AL-3) and is out of scope here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

#: SKILL.md frontmatter `name` field max length (ADR-D3 §Rationale, [HIGH]).
SKILL_NAME_MAX_LENGTH = 64

#: SKILL.md frontmatter `description` field max length (ADR-D3 §Rationale, [HIGH]).
SKILL_DESCRIPTION_MAX_LENGTH = 1024


class SkillFrontmatterRejectionReason(StrEnum):
    """Typed rejection reason for a SKILL.md frontmatter constraint violation."""

    VALID = "VALID"
    NAME_TOO_LONG = "NAME_TOO_LONG"
    DESCRIPTION_EMPTY = "DESCRIPTION_EMPTY"
    DESCRIPTION_TOO_LONG = "DESCRIPTION_TOO_LONG"
    MISSING_VERSION = "MISSING_VERSION"
    MISSING_VERSION_SHA = "MISSING_VERSION_SHA"


class SkillFrontmatterValidationResult(BaseModel):
    """Outcome of SKILL.md frontmatter constraint validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: SkillFrontmatterRejectionReason


def validate_skill_frontmatter(
    *,
    name: str,
    description: str,
    version: str,
    version_sha: str,
) -> SkillFrontmatterValidationResult:
    """Validate a SKILL.md frontmatter against the substrate-committed constraints.

    Checked in order: `name` length, `description` non-empty, `description`
    length, `version` non-empty, `version_sha` non-empty. The first violation
    found is returned (fail-closed) — a caller enforcing this at a load seam
    should reject the skill entirely rather than proceed with a partially
    valid frontmatter.
    """
    if len(name) > SKILL_NAME_MAX_LENGTH:
        return SkillFrontmatterValidationResult(
            outcome=SkillFrontmatterRejectionReason.NAME_TOO_LONG,
        )
    if not description.strip():
        return SkillFrontmatterValidationResult(
            outcome=SkillFrontmatterRejectionReason.DESCRIPTION_EMPTY,
        )
    if len(description) > SKILL_DESCRIPTION_MAX_LENGTH:
        return SkillFrontmatterValidationResult(
            outcome=SkillFrontmatterRejectionReason.DESCRIPTION_TOO_LONG,
        )
    if not version.strip():
        return SkillFrontmatterValidationResult(
            outcome=SkillFrontmatterRejectionReason.MISSING_VERSION,
        )
    if not version_sha.strip():
        return SkillFrontmatterValidationResult(
            outcome=SkillFrontmatterRejectionReason.MISSING_VERSION_SHA,
        )
    return SkillFrontmatterValidationResult(outcome=SkillFrontmatterRejectionReason.VALID)

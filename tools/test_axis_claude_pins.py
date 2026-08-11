"""CI pins for the R-CTX-1 Arc 6 axis-file slimming (U-CTX-19 / U-CTX-20).

Two families of pin:

  1. Pointer<->archive closure — parametrized over all four slimmed axes
     (IS/AS/CP/OD), per U-CTX-19's own requirement ("CI pins for ALL slimmed
     axes", `.harness/r-ctx-1-implementation-plan-v1.md:69`). Each axis's
     `harness-{axis}/CLAUDE.md` §1.2 spec+plan rows must point at
     `.harness/artifact-pointers/{axis}.md` §1.2 axis archive, and that
     archive file must actually carry the relocated content for the EXACT
     artifact names the CLAUDE.md row currently cites (derived from the
     CLAUDE.md text itself, not hardcoded, so this stays valid across future
     head-version bumps). This is the safety net for the U-CTX-20 slimming
     pass. Each axis's `harness-{axis}/AGENTS.md` Codex projection must also
     mirror the same relocation route (U-CTX-20's AGENTS.md co-update
     requirement, `.harness/r-ctx-1-implementation-plan-v1.md:70`).

  2. The `harness-as/CLAUDE.md` §4.1 byte-critical rows — AS-only, since AS is
     the one axis whose §4.1 carries a live-ledger-derived substitution table
     (mirrors the pin shape of `test_substitution_ledger.py:99`,
     `test_as_axis_claude_uses_live_batch_52_posture`). §4.1 is explicitly OUT
     of the U-CTX-20 slimming's scope and must survive it byte-verbatim.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]

_AXES = ("is", "as", "cp", "od")

_ROW_RE = re.compile(r"^\| `([^`]+)` \|")


def _claude_text(axis: str) -> str:
    return (_REPO_ROOT / f"harness-{axis}" / "CLAUDE.md").read_text(encoding="utf-8")


def _agents_text(axis: str) -> str:
    return (_REPO_ROOT / f"harness-{axis}" / "AGENTS.md").read_text(encoding="utf-8")


def _archive_text(axis: str) -> str:
    return (_REPO_ROOT / ".harness" / "artifact-pointers" / f"{axis}.md").read_text(
        encoding="utf-8"
    )


def _spec_and_plan_artifacts(claude_text: str) -> tuple[str, str]:
    """Pull the exact spec/plan artifact filenames straight off the §1.2 rows —
    no hardcoded version number, so this derives fresh at every head bump."""
    lines = claude_text.splitlines()
    spec_line = next(line for line in lines if line.startswith("| `Spec_"))
    plan_line = next(line for line in lines if line.startswith("| `Implementation_Plan_"))
    spec_match = _ROW_RE.match(spec_line)
    plan_match = _ROW_RE.match(plan_line)
    assert spec_match and plan_match
    return spec_match.group(1), plan_match.group(1)


@pytest.mark.parametrize("axis", _AXES)
def test_axis_claude_section_1_2_points_at_the_archive(axis: str) -> None:
    text = _claude_text(axis)
    pointer = f".harness/artifact-pointers/{axis}.md"
    # Both the spec row AND the plan row must carry the pointer — U-CTX-20's
    # AC that the relocation is byte-preserving in BOTH directions.
    assert text.count(pointer) >= 2, (
        f"harness-{axis}/CLAUDE.md §1.2 must point both its spec row and its "
        f"plan row at {pointer} (U-CTX-20 archive-pointer closure)"
    )
    assert "§1.2 axis archive" in text


@pytest.mark.parametrize("axis", _AXES)
def test_axis_archive_carries_the_relocated_section(axis: str) -> None:
    claude_text = _claude_text(axis)
    archive_text = _archive_text(axis)
    spec_artifact, plan_artifact = _spec_and_plan_artifacts(claude_text)

    assert "## §1.2 axis CLAUDE.md archive" in archive_text
    assert f"### `{spec_artifact}` (spec) — original §1.2 Version cell" in archive_text, (
        f"{axis}.md archive is missing the relocated spec cell for {spec_artifact} — "
        "the CLAUDE.md row names it as head but the archive doesn't carry it"
    )
    assert f"### `{plan_artifact}` (plan) — original §1.2 Version cell" in archive_text, (
        f"{axis}.md archive is missing the relocated plan cell for {plan_artifact} — "
        "the CLAUDE.md row names it as head but the archive doesn't carry it"
    )


@pytest.mark.parametrize("axis", _AXES)
def test_axis_agents_md_mirrors_the_archive_route(axis: str) -> None:
    text = _agents_text(axis)
    assert f".harness/artifact-pointers/{axis}.md" in text, (
        f"harness-{axis}/AGENTS.md does not mirror the §1.2 archive relocation "
        f"route its harness-{axis}/CLAUDE.md sibling points to (U-CTX-20 AGENTS.md co-update)"
    )


def test_harness_as_claude_section_4_1_ledger_pointer_strings_present() -> None:
    text = _claude_text("as")
    assert ".harness/substitutions.yaml" in text
    assert "tools/substitution_ledger.py" in text


def test_harness_as_claude_h_t_as_8e_row_pinned() -> None:
    text = _claude_text("as")
    lines = text.splitlines()
    row_line = next(line for line in lines if line.startswith("| H_T-AS-8e "))
    assert "SUBSTANTIVE_RETIRED" in row_line
    assert "batch-52" in row_line
    assert "STILL-BOUNDED" not in row_line

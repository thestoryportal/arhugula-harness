"""CI pin for the byte-critical `harness-as/CLAUDE.md` §4.1 rows (R-CTX-1 Arc 6 / U-CTX-19).

The Arc 6 axis-file arc (U-CTX-20) slims each axis `CLAUDE.md`'s §1.2 (spec + plan
lineage) to a heads-row + archive pointer. §4.1 (the substitution-status table) is
explicitly OUT of that slimming's scope — it must survive byte-verbatim. This module
is the safety net that proves it: it pins the exact strings and row shape U-CTX-20's
own AC depends on, mirroring the shape of the pre-existing
`test_substitution_ledger.py:99` (`test_as_axis_claude_uses_live_batch_52_posture`),
but as a standalone file-content check with no ledger-fixture dependency — so it
protects the CLAUDE.md content on its own, independent of `.harness/substitutions.yaml`
derivation, and stays meaningful even if the ledger module or its fixtures change.
"""

from __future__ import annotations

from pathlib import Path

_HARNESS_AS_CLAUDE = Path(__file__).resolve().parents[1] / "harness-as" / "CLAUDE.md"


def _text() -> str:
    return _HARNESS_AS_CLAUDE.read_text(encoding="utf-8")


def test_harness_as_claude_section_4_1_ledger_pointer_strings_present():
    text = _text()
    assert ".harness/substitutions.yaml" in text
    assert "tools/substitution_ledger.py" in text


def test_harness_as_claude_h_t_as_8e_row_pinned():
    text = _text()
    lines = text.splitlines()
    row_line = next(line for line in lines if line.startswith("| H_T-AS-8e "))
    assert "SUBSTANTIVE_RETIRED" in row_line
    assert "batch-52" in row_line
    assert "STILL-BOUNDED" not in row_line

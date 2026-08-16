"""Tests for `tools/ac_claim_precision.py` — B-167 step 3's OBSTACLE CENSUS.

**No precision verdict is asserted here, because none is supported.** Three attempts
produced 68%, 40% and 62%, each after out-of-family review found a different methodological
flaw, and the third round showed the classification behind the last figure was itself
unsupported (delta and reference forms were being counted as total-count claims). Two
obstacles — revision collapse and count semantics — remain UNSOLVED, so the ratio does not
model the gate.

What the real-corpus tests pin is that each named obstacle is **real in this corpus**. That
is what survived, and it is what the next attempt has to solve. The mechanics tests below
still pin the matcher's behaviour, which is sound as far as it goes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ac_claim_precision as acp

ROOT = acp.ROOT


def _corpus(tmp_path: Path, plan: str, other: str = "") -> Path:
    (tmp_path / "design-substrate").mkdir()
    (tmp_path / ".harness").mkdir()
    (tmp_path / "design-substrate" / "Implementation_Plan_X_v2_1.md").write_text(
        plan, encoding="utf-8"
    )
    if other:
        (tmp_path / ".harness" / "notes.md").write_text(other, encoding="utf-8")
    return tmp_path


_BLOCK = "### U-XX-01 — a unit\n\n**Acceptance criteria:**\n\n1. one\n2. two\n3. three\n"


# --- the measurement mechanics ------------------------------------------------


def test_a_matching_claim_counts_as_agreement(tmp_path: Path) -> None:
    root = _corpus(tmp_path, _BLOCK, "U-XX-01 carries 3 acceptance criteria.\n")
    p = acp.measure(root)
    assert (p.associable_claims, p.agree, p.disagree) == (1, 1, 0)


def test_a_mismatching_claim_counts_as_a_firing(tmp_path: Path) -> None:
    root = _corpus(tmp_path, _BLOCK, "U-XX-01 carries 9 acceptance criteria.\n")
    p = acp.measure(root)
    assert (p.associable_claims, p.agree, p.disagree) == (1, 0, 1)


def test_identifier_digits_are_not_read_as_a_claimed_count(tmp_path: Path) -> None:
    """Obstacle 1. `U-CP-56 acceptance criteria` is not a claim of fifty-six.

    Fixing this moved the reported figure 68% → 40%. Condemning a design on a strawman
    implementation is its own failure mode, so the exclusion is pinned.
    """
    root = _corpus(tmp_path, _BLOCK, "U-XX-01 acceptance criteria are listed above.\n")
    assert acp.measure(root).associable_claims == 0


def test_a_claim_with_no_unit_on_the_line_is_not_associable(tmp_path: Path) -> None:
    root = _corpus(tmp_path, _BLOCK, "The unit has 3 acceptance criteria.\n")
    assert acp.measure(root).associable_claims == 0


def test_a_claim_about_a_unit_with_no_derivable_count_is_skipped(tmp_path: Path) -> None:
    """No ground truth means nothing to compare — silence, not a guess."""
    plan = "### U-YY-02 — amended\n\n**Acceptance criteria (v2.1 additions):**\n\n0. zero\n"
    root = _corpus(tmp_path, plan, "U-YY-02 carries 4 acceptance criteria.\n")
    assert acp.measure(root).associable_claims == 0


def test_word_numbers_are_understood(tmp_path: Path) -> None:
    root = _corpus(tmp_path, _BLOCK, "U-XX-01 carries three acceptance criteria.\n")
    p = acp.measure(root)
    assert (p.associable_claims, p.agree) == (1, 1)


def test_a_multi_number_line_is_classified_as_such(tmp_path: Path) -> None:
    """The live-versus-declared shape, which the matcher classifies separately.

    NOTE this classifier is exactly what review round 2 showed to be too crude on the real
    corpus: it cannot distinguish this genuine case from `+1 AC` or `AC #1`. It is retained
    to locate the shape, not to support a ratio.
    """
    root = _corpus(
        tmp_path, _BLOCK, "| U-XX-01 body | 7 acceptance criteria (12 declared, 5 STRUCK) |\n"
    )
    p = acp.measure(root)
    assert p.disagree == 1
    assert p.disagree_on_multi_number_lines == 1


def test_fire_rate_is_zero_when_there_is_nothing_to_compare(tmp_path: Path) -> None:
    root = _corpus(tmp_path, _BLOCK)
    assert acp.measure(root).fire_rate == 0.0


# --- the obstacles, on the real corpus ----------------------------------------
#
# These do NOT assert a precision figure. Three attempts produced 68%, 40% and 62%, and
# review showed the classification behind the last was unsupported, so the rate is withdrawn
# (see the module docstring). What is pinned is that each named obstacle is REAL in this
# corpus — because the obstacle census is what survived, and it is what the next attempt
# must solve.


def test_revision_collapse_is_real_obstacle_four() -> None:
    """A unit-id key collapses delta revisions, so a STALE claim can score as agreement."""
    truth = acp.derived_counts()
    collapsed = {u: c for u, c in truth.items() if len(c) > 1}
    assert collapsed, (
        "no unit derives multiple counts any more — obstacle 4 (revision collapse) may be "
        "gone, which would materially change what a sound step-3 measurement costs"
    )


def test_delta_and_reference_forms_are_real_obstacle_five() -> None:
    """`+1 AC`, `STRUCK 4 ACs`, `AC #1` are not total-count claims."""
    import re

    forms = re.compile(r"\+\d+ ACs?\b|STRUCK \d+ ACs?\b|\bACs? #\d+")
    hits = 0
    for folder in ("design-substrate", ".harness"):
        for path in (ROOT / folder).rglob("*.md"):
            hits += len(forms.findall(path.read_text(encoding="utf-8", errors="ignore")))
    assert hits > 0, (
        "no delta or reference count forms found — obstacle 5 may be gone, in which case a "
        "claim matcher no longer needs to validate count semantics"
    )


def test_the_recount_itself_is_still_exact_where_it_applies() -> None:
    """Steps 1-2 are unaffected by step 3's withdrawal. The recount still works."""
    truth = acp.derived_counts()
    assert len(truth) >= 100, f"only {len(truth)} units carry a derived count — re-ground B-167"


def test_the_measurement_makes_no_precision_claim() -> None:
    """A guard on this arc's own honesty.

    The module must not re-acquire a verdict while obstacles 4 and 5 are unsolved. If a
    future edit deletes this disclaimer, that edit owes the sound measurement first.
    """
    text = (ROOT / "tools" / "ac_claim_precision.py").read_text(encoding="utf-8")
    assert "NOT a precision figure" in text or "NOT A PRECISION FIGURE" in text
    assert "UNSOLVED" in text

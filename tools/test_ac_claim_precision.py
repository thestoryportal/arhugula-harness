"""Tests for `tools/ac_claim_precision.py` — B-167 step 3's measurement.

The verdict this module supports is *"a claim-versus-recount gate is not viable"*, so the
assertions pin the **shape** that makes it non-viable, not the exact percentage. A test
asserting `fire_rate == 0.40` would redden on any corpus growth and teach nothing; a test
asserting *"firing is common AND dominated by legitimate multi-number prose"* stays true
for the reason the verdict is true, and reddens only if that reason stops holding.
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
    """The trap that made a first pass report 68% instead of 40%.

    `U-CP-56 acceptance criteria` is not a claim of fifty-six. Condemning a design on a
    strawman implementation is its own failure mode, so this is pinned.
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
    """The shape that makes the gate non-viable: a live count and a declared count
    stated together, both correct."""
    root = _corpus(
        tmp_path, _BLOCK, "| U-XX-01 body | 7 acceptance criteria (12 declared, 5 STRUCK) |\n"
    )
    p = acp.measure(root)
    assert p.disagree == 1
    assert p.disagree_on_multi_number_lines == 1


def test_fire_rate_is_zero_when_there_is_nothing_to_compare(tmp_path: Path) -> None:
    root = _corpus(tmp_path, _BLOCK)
    assert acp.measure(root).fire_rate == 0.0


# --- the verdict, on the real corpus ------------------------------------------


def test_the_real_corpus_still_makes_the_gate_non_viable() -> None:
    """B-167 step 3's actual result, asserted as a SHAPE.

    Two conditions carry the verdict, and both must hold for it to stand:
      * firing is common — well above a rate anyone would tolerate in a pre-push gate; and
      * the firings are dominated by legitimate multi-number prose, which no better matcher
        resolves because the ambiguity is in the artifact.

    If either stops holding, the disposition is re-openable and this test says so by going
    red — which is the point of pinning the reason rather than the number.
    """
    p = acp.measure()
    assert p.associable_claims >= 20, (
        f"only {p.associable_claims} associable claims — too few to support a precision "
        "verdict either way; re-derive B-167 step 3 before trusting its disposition"
    )
    assert p.fire_rate > 0.25, (
        f"fire rate fell to {p.fire_rate:.0%}. A claim-versus-recount gate may now be "
        "viable — B-167 step 3's refutation was measured at 40% and must be re-derived"
    )
    assert p.disagree_on_multi_number_lines / p.disagree > 0.5, (
        "multi-number prose no longer dominates the firings, so the 'ambiguity is in the "
        "artifact' argument no longer carries the verdict — re-derive B-167 step 3"
    )


def test_the_recount_itself_is_still_exact_where_it_applies() -> None:
    """The verdict refutes the GATE, not the recount. Steps 1-2 must still hold."""
    truth = acp.derived_counts()
    assert len(truth) >= 100, f"only {len(truth)} units carry a derived count — re-ground B-167"

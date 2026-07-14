from __future__ import annotations

import hashlib
from typing import Any

from tools import qa_evidence_matrix

# B-35 (.harness/post-phase-8-forward-register.md) - a pre-existing gap, not
# introduced this session: as of 2026-07-14 a known set of contracts (11
# memory-substrate + 1 IS contract) have no test file citing their contract
# id anywhere in the repo. Deliberately NOT spelled out by literal id in this
# file's own text -- this scanner counts any test_*.py file that merely
# CONTAINS a contract-id-shaped substring as "proof" for that id, so writing
# the literal ids here would make this file falsely count as their evidence
# (out-of-family Codex round 2 caught exactly this self-citation bug in an
# earlier draft that spelled one id out in an xfail reason string).
#
# A bare COUNT assertion (round-2 fix) has its own gap (out-of-family Codex
# round 3): if one known-missing contract gains a citation in the same
# change that a different, previously-covered contract loses its citation,
# the count is unchanged and the regression passes silently. Pin a SHA-256
# fingerprint of the sorted missing-id list instead of the count -- any
# substitution changes the digest even when the count doesn't, and the
# digest itself never spells out a contract id in this file's text.
_B35_KNOWN_MISSING_TEST_EVIDENCE_COUNT = 12
_B35_KNOWN_MISSING_TEST_EVIDENCE_FINGERPRINT = (
    "4f5c5c86af83254e16aa5558d85d31754275f3051cc6b0fe7e65c0957712f0e5"
)
_B35_KNOWN_CXA_MISSING_ENDPOINT_COUNT = 0


def _missing_test_evidence_fingerprint(matrix: dict[str, Any]) -> str:
    missing_ids: list[str] = sorted(
        row["contract_id"] for row in matrix["contracts"] if not row["test_files"]
    )
    return hashlib.sha256(",".join(missing_ids).encode("utf-8")).hexdigest()


def test_q3_evidence_matrix_known_gaps_are_tracked_not_growing() -> None:
    """B-28 finding #17/#18 follow-up (out-of-family Codex rounds 2 + 3) -
    the original test asserted `== []` against live data that currently has
    known gaps (see B-35). A blanket xfail on that whole assertion would
    mask a genuinely NEW regression behind the same expected-failure
    outcome; a bare count assertion would miss a same-count substitution
    (one gap closes while a different, previously-clean contract loses its
    citation). Assert a fingerprint of the exact missing-id set instead:
    this fails loudly on ANY change to *which* contracts are missing, not
    just how many, without ever spelling out a contract id in this file."""
    matrix = qa_evidence_matrix.derive_matrix()
    stats = qa_evidence_matrix.summary(matrix)

    assert stats["contracts_total"] > 0
    assert stats["contracts_missing_test_evidence"] == _B35_KNOWN_MISSING_TEST_EVIDENCE_COUNT, (
        "the R-CL-Q3 evidence-matrix gap count changed -- if it DECREASED, "
        "update _B35_KNOWN_MISSING_TEST_EVIDENCE_COUNT + the fingerprint down "
        "(real progress on B-35); if it INCREASED, a previously-covered "
        "contract just lost its test-file citation -- investigate before "
        "touching this constant."
    )
    fingerprint = _missing_test_evidence_fingerprint(matrix)
    assert fingerprint == _B35_KNOWN_MISSING_TEST_EVIDENCE_FINGERPRINT, (
        "the R-CL-Q3 missing-test-evidence CONTRACT SET changed even though "
        "the count may be unchanged -- a substitution (one contract gained "
        "evidence while a different one lost it) can hide behind a stable "
        "count; print sorted(row['contract_id'] for row in "
        "qa_evidence_matrix.derive_matrix()['contracts'] if not "
        "row['test_files']) to see the current set before updating this "
        "fingerprint."
    )
    assert stats["cxa_seams_missing_endpoint"] == _B35_KNOWN_CXA_MISSING_ENDPOINT_COUNT


def test_q3_evidence_report_renders_contract_rows() -> None:
    matrix = qa_evidence_matrix.derive_matrix()
    report = qa_evidence_matrix.render_markdown(matrix)

    assert "# R-CL-Q3 QA Evidence Matrix" in report
    assert "| Contracts with test proof |" in report
    assert "## Contract Evidence" in report

    # B-28 finding #18 (test-quality preflight 2026-07-12) - the prior body's
    # write-then-read-back assertion only proved the filesystem round-trips a
    # string, adding no coverage of `render_markdown` beyond the substring
    # checks above; assert real completeness instead - every contract row in
    # the matrix actually appears as a rendered table row.
    for row in matrix["contracts"]:
        assert f"| {row['contract_id']} |" in report


def test_violations_reports_missing_test_evidence_and_cxa_endpoint() -> None:
    """B-28 finding #17 (test-quality preflight 2026-07-12) - `violations()`
    was only ever called against the live, already-clean matrix; construct a
    synthetic matrix with a known contract-missing-test-evidence row and a
    known CXA-seam-missing-endpoint row and assert both are reported."""
    synthetic_matrix = {
        "contracts": [
            {
                "contract_id": "C-XX-99",
                "declaration_files": ["design-substrate/Fake.md"],
                "source_files": ["harness_fake/module.py"],
                "test_files": [],
            },
            {
                "contract_id": "C-XX-01",
                "declaration_files": ["design-substrate/Fake.md"],
                "source_files": ["harness_fake/module.py"],
                "test_files": ["harness-fake/tests/test_module.py"],
            },
        ],
        "cxa": {
            "total": 1,
            "wired": 0,
            "missing": [{"edge_label": "FAKE-AXIS -> OTHER-AXIS"}],
        },
    }

    reported = qa_evidence_matrix.violations(synthetic_matrix)

    assert "C-XX-99 has no test proof" in reported
    assert not any("C-XX-01" in item for item in reported)
    assert "FAKE-AXIS -> OTHER-AXIS has a missing CXA endpoint" in reported
    assert len(reported) == 2

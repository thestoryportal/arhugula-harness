from __future__ import annotations

from tools import qa_evidence_matrix

# B-35 (.harness/post-phase-8-forward-register.md) - a pre-existing gap, not
# introduced this session: as of 2026-07-14 a known set of contracts (11
# memory-substrate + 1 IS contract) have no test file citing their contract
# id anywhere in the repo. Deliberately NOT spelled out by literal id in this
# file's own text -- this scanner counts any test_*.py file that merely
# CONTAINS a contract-id-shaped substring as "proof" for that id, so writing
# the literal ids here would make this file falsely count as their evidence
# (out-of-family Codex round 2 caught exactly this self-citation bug in an
# earlier draft that spelled one id out in an xfail reason string). Pin the
# exact COUNT instead of xfail-ing the whole assertion, so a genuinely NEW
# gap (count increases) still fails loudly instead of being silently
# absorbed by a blanket expected-failure.
_B35_KNOWN_MISSING_TEST_EVIDENCE_COUNT = 12
_B35_KNOWN_CXA_MISSING_ENDPOINT_COUNT = 0


def test_q3_evidence_matrix_known_gaps_are_tracked_not_growing() -> None:
    """B-28 finding #17/#18 follow-up (out-of-family Codex round 2) - the
    original test asserted `== []` against live data that currently has
    known gaps (see B-35). A blanket xfail on that whole assertion would
    mask a genuinely NEW regression (a different, previously-clean contract
    losing its test citation) behind the same expected-failure outcome.
    Assert the exact known count instead: this fails loudly if the gap count
    ever changes in either direction, forcing a human to look at *which*
    contract changed before adjusting the constant."""
    matrix = qa_evidence_matrix.derive_matrix()
    stats = qa_evidence_matrix.summary(matrix)

    assert stats["contracts_total"] > 0
    assert stats["contracts_missing_test_evidence"] == _B35_KNOWN_MISSING_TEST_EVIDENCE_COUNT, (
        "the R-CL-Q3 evidence-matrix gap count changed -- if it DECREASED, "
        "update _B35_KNOWN_MISSING_TEST_EVIDENCE_COUNT down (real progress on "
        "B-35); if it INCREASED, a previously-covered contract just lost its "
        "test-file citation -- investigate before touching this constant."
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

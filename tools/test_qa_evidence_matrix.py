from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qa_evidence_matrix

_B35_KNOWN_CXA_MISSING_ENDPOINT_COUNT = 0


def test_q3_evidence_matrix_known_gaps_are_tracked_not_growing() -> None:
    """B-35 (.harness/forward-register.yaml, CLOSED) - a prior draft of this
    test pinned a known-nonzero gap (12 contracts, mostly memory-substrate,
    with no test file citing their contract id anywhere in the repo) via a
    SHA-256 fingerprint of the sorted missing-id list, since a bare count
    assertion would miss a same-count substitution (out-of-family Codex
    rounds 2 + 3). B-35 is now closed -- 1 phantom id (C-IS-14, a documented
    non-contract per `overlay.DOCUMENTED_NON_CONTRACTS`) was excluded from
    the keyspace, 10 ids gained a one-line contract-id citation on an
    already-passing test, and the last (C-MEM-01, an architectural contract
    with no dedicated source module) gained two new tests
    (harness-runtime/tests/test_memory_plane_boundary.py). Assert the direct,
    honest invariant now that the gap is empty: any FUTURE contract losing
    its citation fails this immediately, without carrying forward dead
    gap-tracking machinery."""
    matrix = qa_evidence_matrix.derive_matrix()
    stats = qa_evidence_matrix.summary(matrix)

    assert stats["contracts_total"] > 0
    missing_ids = sorted(row["contract_id"] for row in matrix["contracts"] if not row["test_files"])
    assert missing_ids == [], (
        f"contract(s) {missing_ids} lack test-file citation -- either add a "
        "one-line contract-id citation to an existing test, write a new "
        "test, or (if genuinely phantom) add to "
        "overlay.DOCUMENTED_NON_CONTRACTS with a canonical-spec citation"
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
